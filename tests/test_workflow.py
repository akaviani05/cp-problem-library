"""Behavior checks use fake Polygon transport; no credentials or live mutations."""
import copy
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import zipfile

from cpplib.catalog import refresh_catalog, START, END
from cpplib.cli import main
from cpplib.model import Problem
from cpplib.polygon import Polygon, signed_parameters
from cpplib.runner import execute
from cpplib import sync
from cpplib.util import Error, read_json, write_json
from cpplib.verify import Judge, VERIFICATION_VERSION, verified

REPO = Path(__file__).resolve().parents[1]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(REPO / "include", self.root / "include")
        shutil.copytree(REPO / "problems/a-plus-b", self.root / "problems/a-plus-b",
                        ignore=shutil.ignore_patterns("build", "artifacts", "polygon-state.json"))
        self.problem = Problem(self.root, "a-plus-b")

    def evidence(self):
        self.problem.build.mkdir(parents=True, exist_ok=True)
        directory = self.problem.build / "tests"
        directory.mkdir(exist_ok=True)
        data = {"in": b"1 2\n", "ans": b"3\n"}
        for suffix, content in data.items():
            (directory / f"01.{suffix}").write_bytes(content)
        report = {"passed": True, "verificationVersion": VERIFICATION_VERSION,
                  "fingerprint": self.problem.fingerprint(), "testCount": 1,
                  "inputSha256": {"1": hashlib.sha256(data["in"]).hexdigest()},
                  "answerSha256": {"1": hashlib.sha256(data["ans"]).hexdigest()}}
        write_json(self.problem.build / "verification.json", report)
        return report


class LocalContracts(Fixture):
    def test_multiline_signing_uses_decoded_values_before_urlencoding(self):
        params = {"file": "line 1\n&+={}\n", "verify": True}
        signed = signed_parameters("problem.saveFile", params, "test-key", "test-secret", 123, "abcdef")
        expected = "abcdef/problem.saveFile?apiKey=test-key&file=line 1\n&+={}\n&time=123&verify=true#test-secret"
        self.assertEqual(signed["apiSig"], "abcdef" + hashlib.sha512(expected.encode()).hexdigest())

    def test_recipe_rejects_gaps_duplicates_and_shell(self):
        script = self.problem.file("tests/doall.txt")
        for source in ("gen random 1 > 5\n", "gen random 1 > 1\n", "gen x ; gen y > 4\n"):
            script.write_text(source)
            with self.subTest(source=source), self.assertRaises(Error):
                self.problem.recipe()

    def test_draft_and_unfinished_statement_are_rejected(self):
        self.problem.config["draft"] = True
        with self.assertRaisesRegex(Error, "draft"):
            self.problem.validate()
        self.problem.config["draft"] = False
        self.problem.file("statements/english/legend.tex").write_text("CPPL_TEMPLATE_UNFINISHED")
        with self.assertRaisesRegex(Error, "Complete statement"):
            self.problem.validate()

    def test_source_edit_invalidates_verification(self):
        self.evidence()
        verified(self.problem)
        source = self.problem.file("solutions/main.cpp")
        source.write_text(source.read_text() + "\n// relevant edit\n")
        with self.assertRaisesRegex(Error, "stale"):
            verified(self.problem)

    def test_generated_answer_edit_invalidates_verification(self):
        self.evidence()
        (self.problem.build / "tests/01.ans").write_bytes(b"4\n")
        with self.assertRaisesRegex(Error, "changed"):
            verified(self.problem)

    def test_old_verification_contract_is_stale(self):
        report = self.evidence()
        report.pop("verificationVersion")
        write_json(self.problem.build / "verification.json", report)
        with self.assertRaisesRegex(Error, "stale"):
            verified(self.problem)

    def test_catalog_preserves_authored_text(self):
        prefix = "# User introduction\nDo not change this.\n"
        suffix = "\nUser footer\n"
        (self.root / "README.md").write_text(prefix + START + "\nold\n" + END + suffix)
        refresh_catalog(self.root)
        result = (self.root / "README.md").read_text()
        self.assertTrue(result.startswith(prefix + START))
        self.assertTrue(result.endswith(END + suffix))
        self.assertIn("2026-09-30", result)

    def test_checker_crash_is_not_a_wrong_solution_witness(self):
        script = self.problem.build / "bad-checker"
        script.parent.mkdir(parents=True)
        script.write_text("#!/bin/sh\nexit 3\n")
        script.chmod(0o755)
        programs = {self.problem.config["assets"]["validator"]: script,
                    self.problem.config["assets"]["checker"]: script}
        with self.assertRaisesRegex(Error, "Checker failed"):
            Judge(self.problem, programs).check(b"1 2\n", b"3\n", b"4\n")


class ProcessLimits(unittest.TestCase):
    def test_peak_rss_excludes_large_parent_fork_memory(self):
        if not shutil.which("time"):
            self.skipTest("GNU time not installed")
        parent_allocation = bytearray(64 * 1024 * 1024)
        result = execute(["/bin/true"])
        self.assertEqual(len(parent_allocation), 64 * 1024 * 1024)
        self.assertIsNotNone(result.max_rss_kib)
        self.assertLess(result.max_rss_kib, 20 * 1024)
    def test_time_limit_and_process_group(self):
        result = execute([sys.executable, "-c", "import time; time.sleep(5)"], timeout=.06)
        self.assertEqual(result.termination, "TIME_LIMIT")
        self.assertLess(result.wall_seconds, 1)

    def test_output_limit_including_python_efbig(self):
        result = execute([sys.executable, "-c", "import os; os.write(1, b'x'*3000000); os.write(1,b'x')"], output_mib=1)
        self.assertEqual(result.termination, "OUTPUT_LIMIT")
        self.assertLessEqual(len(result.stdout), 1024 * 1024)

    def test_memory_limit(self):
        result = execute([sys.executable, "-c", "x = bytearray(100*1024*1024)"], memory_mib=32)
        self.assertEqual(result.termination, "MEMORY_LIMIT")
        self.assertGreater(result.max_rss_kib, 0)

    def test_credentials_not_in_authored_program_environment(self):
        with patch.dict("os.environ", {"POLYGON_API_KEY": "fake", "POLYGON_API_SECRET": "fake", "CPPL_CONFIG": "fake"}):
            result = execute([sys.executable, "-c", "import os; print(any(k in os.environ for k in ('POLYGON_API_KEY','POLYGON_API_SECRET','CPPL_CONFIG')))" ])
        self.assertEqual(result.stdout, b"False\n")


class TransportFailures(unittest.TestCase):
    def test_network_failure_is_not_retried_and_does_not_echo_request(self):
        api = Polygon({"api_key": "fake-key", "api_secret": "fake-secret"})
        with patch.object(api.opener, "open", side_effect=urllib.error.URLError("fake-key fake-secret signed request")) as request:
            with self.assertRaisesRegex(Error, "retry the CLI command") as failure:
                api.call("problem.create", {"name": "example"})
        self.assertEqual(request.call_count, 1)
        self.assertNotIn("fake-key", str(failure.exception))
        self.assertNotIn("fake-secret", str(failure.exception))


class PlainChecker(unittest.TestCase):
    def test_real_template_handles_whitespace_punctuation_and_unicode(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            binary = work / "checker"
            result = execute(["g++", "-std=c++17", "-O2", "-I", REPO / "include",
                              REPO / "templates/plain/checkers/checker.cpp", "-o", binary],
                             timeout=90, memory_mib=0)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            answer = "-5 {} café\n"
            (work / "input").write_text("0\n")
            (work / "answer").write_text(answer)
            for output, expected in (("\n -5\t{} café \n", 0), ("-5 {} wrong\n", 1),
                                     ("-5 {}\n", 1), (answer + "extra\n", 2), ("", 1)):
                with self.subTest(output=output):
                    (work / "output").write_text(output)
                    run = execute([binary, work / "input", work / "output", work / "answer"])
                    self.assertEqual(run.returncode, expected, run.stderr.decode())

    def test_api_error_redacts_credentials(self):
        api = Polygon({"api_key": "fake-key", "api_secret": "fake-secret"})
        error = urllib.error.HTTPError("https://polygon.codeforces.com", 400, "bad", {},
                                      io.BytesIO(b'{"comment":"bad fake-key fake-secret"}'))
        with patch.object(api.opener, "open", side_effect=error):
            with self.assertRaises(Error) as failure:
                api.call("problem.info", {"problemId": 1})
        self.assertNotIn("fake-key", str(failure.exception))
        self.assertNotIn("fake-secret", str(failure.exception))


def empty_snapshot():
    return {"info": {}, "tags": [], "statements": {}, "files": {}, "solutions": {},
            "validator": None, "checker": None, "script": "", "manualTests": {},
            "validatorTests": {}, "checkerTests": {}}


class FakePolygon:
    def __init__(self, problem):
        self.name = problem.config["name"]
        self.owner = "test-owner"
        self.exists = False
        self.modified = False
        self.revision = 1
        self.remote = empty_snapshot()
        self.changes, _ = sync.operations(problem, self.remote)
        self.calls = []
        self.fail_after = None
        self.packages = []
        self.payload = None

    def call(self, method, parameters=None, raw=False):
        self.calls.append(method)
        if method == "problems.list":
            return ([{"id": 1, "name": self.name, "owner": self.owner, "accessType": "OWNER",
                      "modified": self.modified, "revision": self.revision}] if self.exists else [])
        if method == "problem.create":
            self.exists = True
            if self.fail_after == method:
                self.fail_after = None
                raise Error("simulated lost creation response")
            return {"id": 1, "owner": self.owner}
        if method == "problem.package":
            return self.payload
        raise AssertionError(method)

    def problem(self, state, method, **params):
        self.calls.append(method)
        if method == "problem.accesses":
            return [{"login": "codeforces", "accessType": "READ"}]
        if method == "problem.commitChanges":
            self.revision += int(self.modified)
            self.modified = False
            return {"conflictOccurred": False}
        if method == "problem.packages":
            return self.packages
        if method == "problem.buildPackage":
            self.packages.append({"id": 3, "revision": self.revision, "type": "linux", "state": "READY"})
            return None
        if method == "problem.cautions":
            return {key: [] for key in ("common", "statement", "structure", "issues", "packageReadinessIssues", "latestPackageWarnings")}
        for candidate, expected, path, value in self.changes:
            if candidate == method and params == expected:
                sync.put_path(self.remote, path, value)
                self.modified = True
                if self.fail_after == method:
                    self.fail_after = None
                    raise Error("simulated lost asset response")
                return None
        raise AssertionError((method, params))


class RemoteContracts(Fixture):
    def setUp(self):
        super().setUp()
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        self.evidence()
        self.api = FakePolygon(self.problem)
        self.addCleanup(patch.stopall)
        patch("cpplib.sync.snapshot", side_effect=lambda api, state: copy.deepcopy(api.remote)).start()

    def test_lost_creation_response_is_reconciled_without_duplicate(self):
        self.api.fail_after = "problem.create"
        with self.assertRaisesRegex(Error, "lost creation"):
            sync.upload(self.problem, self.api, {})
        self.assertNotIn("id", read_json(self.problem.state_path))
        state = sync.upload(self.problem, self.api, {})
        self.assertEqual(state["id"], 1)
        self.assertEqual(self.api.calls.count("problem.create"), 1)
        self.assertTrue(state["importAccess"]["verified"])

    def test_explicit_attach_resolves_idless_creation_intent(self):
        self.api.exists = True
        write_json(self.problem.state_path, {"name": self.api.name, "stage": "creating"})
        with patch("cpplib.cli.Polygon", return_value=self.api):
            self.assertEqual(main(["--root", str(self.root), "attach", "a-plus-b", "--id", "1"]), 0)
        self.assertEqual(read_json(self.problem.state_path)["id"], 1)
        self.assertNotIn("problem.create", self.api.calls)

    def test_lost_asset_response_resumes_and_skips_applied_asset(self):
        self.api.fail_after = "problem.saveFile"
        with self.assertRaisesRegex(Error, "lost asset"):
            sync.upload(self.problem, self.api, {})
        state = sync.upload(self.problem, self.api, {})
        self.assertEqual(state["stage"], "committed")
        self.assertEqual(self.api.calls.count("problem.create"), 1)
        self.assertEqual(self.api.calls.count("problem.saveFile"), len(self.problem.config["files"]))

    def test_pending_upload_stops_for_conflicting_remote_edit(self):
        self.api.fail_after = "problem.saveFile"
        with self.assertRaises(Error):
            sync.upload(self.problem, self.api, {})
        self.api.remote["info"]["timeLimit"] = 777
        with self.assertRaisesRegex(Error, "conflict"):
            sync.upload(self.problem, self.api, {})

    def test_commented_recipe_uploads_commands_and_resumes(self):
        script = self.problem.file(self.problem.config["testsets"]["tests"]["script"])
        commands = [line for line in script.read_text().splitlines()
                    if line.strip() and not line.lstrip().startswith("#")]
        original = "# local documentation\n\n" + "\n".join(reversed(commands)) + "\n  # final comment\n"
        script.write_text(original)
        self.evidence()
        self.api.changes, _ = sync.operations(self.problem, self.api.remote)
        save = next(params for method, params, _, _ in self.api.changes if method == "problem.saveScript")
        lines = save["source"].splitlines()
        self.assertTrue(lines)
        self.assertTrue(all(line.strip() and not line.lstrip().startswith("#") for line in lines))
        self.assertTrue(all(line.split()[-2] == ">" and line.split()[-1].isdigit() for line in lines))
        indices = [int(line.split()[-1]) for line in lines]
        self.assertEqual(indices, sorted(indices))
        self.api.fail_after = "problem.saveScript"
        with self.assertRaisesRegex(Error, "lost asset"):
            sync.upload(self.problem, self.api, {})
        state = sync.upload(self.problem, self.api, {})
        self.assertEqual(state["stage"], "committed")
        self.assertEqual(self.api.calls.count("problem.saveScript"), 1)
        self.assertEqual(script.read_text(), original)

    def test_readback_mismatch_reports_asset_path_without_content(self):
        original = self.api.problem

        def mutate(state, method, **params):
            result = original(state, method, **params)
            if method == "problem.saveScript":
                self.api.remote["script"] = "private remote edit"
            return result

        self.api.problem = mutate
        with self.assertRaisesRegex(Error, "readback differs at script") as caught:
            sync.upload(self.problem, self.api, {})
        self.assertNotIn("private remote edit", str(caught.exception))
        self.assertNotIn("problem.commitChanges", self.api.calls)
        with self.assertRaisesRegex(Error, "pending upload at script"):
            sync.upload(self.problem, self.api, {})

    def test_statement_punctuation_matches_polygon_readback(self):
        fragment = self.problem.file("statements/english/output.tex")
        original = fragment.read_text() + '\nPrint \u201cAlice\u201d \u2014 the winner.\n'
        fragment.write_text(original)
        self.evidence()
        self.api.changes, _ = sync.operations(self.problem, self.api.remote)
        save = next(params for method, params, _, _ in self.api.changes if method == "problem.saveStatement")
        self.assertIn('Print "Alice" --- the winner.\n', save["output"])
        self.api.fail_after = "problem.saveStatement"
        with self.assertRaisesRegex(Error, "lost asset"):
            sync.upload(self.problem, self.api, {})
        state = sync.upload(self.problem, self.api, {})
        self.assertEqual(state["stage"], "committed")
        self.assertEqual(self.api.calls.count("problem.saveStatement"), 1)
        self.assertEqual(fragment.read_text(), original)

    def test_local_only_fixture_edit_can_resume_same_remote_payload(self):
        self.api.fail_after = "problem.saveFile"
        with self.assertRaises(Error):
            sync.upload(self.problem, self.api, {})
        fixtures = self.problem.file(self.problem.config["selfTests"]["validator"])
        cases = read_json(fixtures)
        cases.append({"name": "empty local", "input": "", "verdict": "INVALID", "polygon": False})
        write_json(fixtures, cases)
        self.evidence()
        state = sync.upload(self.problem, self.api, {})
        self.assertEqual(state["stage"], "committed")

    def test_changed_remote_payload_cannot_resume_old_intent(self):
        self.api.fail_after = "problem.saveFile"
        with self.assertRaises(Error):
            sync.upload(self.problem, self.api, {})
        source = self.problem.file("solutions/main.cpp")
        source.write_text(source.read_text() + "\n// new payload\n")
        self.evidence()
        with self.assertRaisesRegex(Error, "remote payload"):
            sync.upload(self.problem, self.api, {})

    def test_modified_working_copy_is_preserved(self):
        state = sync.upload(self.problem, self.api, {})
        self.api.modified = True
        with self.assertRaisesRegex(Error, "user changes"):
            sync.upload(self.problem, self.api, {})
        self.assertEqual(read_json(self.problem.state_path)["revision"], state["revision"])

    def test_standard_only_package_does_not_suppress_full_build(self):
        state = sync.upload(self.problem, self.api, {})
        self.api.packages = [{"id": 2, "revision": state["revision"], "type": "standard", "state": "READY"}]
        sync.build_and_wait(self.problem, self.api, {"build_timeout_seconds": 1, "poll_seconds": 1}, state)
        self.assertEqual(self.api.calls.count("problem.buildPackage"), 1)

    def test_zip_revision_and_every_test_byte_checked(self):
        state = sync.upload(self.problem, self.api, {})
        self.api.packages = [{"id": 2, "revision": state["revision"], "type": "linux", "state": "READY"}]
        def package(revision, answer):
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w") as archive:
                archive.writestr("problem.xml", f'<problem revision="{revision}"><judging><testset name="tests"><input-path-pattern>tests/%02d</input-path-pattern><answer-path-pattern>tests/%02d.a</answer-path-pattern><tests><test/></tests></testset></judging></problem>')
                archive.writestr("tests/01", b"1 2\r\n")
                archive.writestr("tests/01.a", answer)
            return output.getvalue()
        self.api.payload = package(state["revision"] + 1, b"3\n")
        with self.assertRaisesRegex(Error, "revision differs"):
            sync.export_package(self.problem, self.api, state)
        self.api.payload = package(state["revision"], b"4\n")
        with self.assertRaisesRegex(Error, "differs from verified"):
            sync.export_package(self.problem, self.api, state)
        self.api.payload = package(state["revision"], b"3\r\n")
        sync.export_package(self.problem, self.api, state)
        self.assertEqual(state["packageId"], 2)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""A+B experiment runner. The general, installable CLI is a later phase."""

import argparse
import base64
import getpass
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROBLEM = ROOT / "problems" / "a-plus-b"
API = "https://polygon.codeforces.com/api/"
STATE = PROBLEM / "polygon-state.json"
CHECKER_CODES = {"OK": 0, "WRONG_ANSWER": 1, "PRESENTATION_ERROR": 2}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_problem():
    return tomllib.loads((PROBLEM / "problem.toml").read_text(encoding="utf-8"))


def remote_cases(config, asset):
    return [case for case in read_json(PROBLEM / config["selfTests"][asset]) if case.get("polygon", True)]


def run(command, *, data=None, timeout=5):
    return subprocess.run(
        [str(item) for item in command], input=data, capture_output=True,
        timeout=timeout, check=False,
    )


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verification():
    """Verify this pilot, including a Python big-integer oracle for every test."""
    config = load_problem()
    build = PROBLEM / "build"
    binaries = build / "bin"
    tests_dir = build / "tests"
    binaries.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    source_files = [file for file in config["files"] if file["type"] == "source"]
    for source in source_files + config["solutions"]:
        result = run([
            "g++", "-std=c++17", "-O2", "-Wall", "-Wextra",
            "-I", ROOT / "include", PROBLEM / source["path"],
            "-o", binaries / Path(source["name"]).stem,
        ], timeout=90)
        require(result.returncode == 0,
                f"Compilation failed: {source['name']}\n{result.stderr.decode(errors='replace')}")
    print(f"Compiled {len(source_files) + len(config['solutions'])} C++ programs.", flush=True)

    validator = binaries / Path(config["assets"]["validator"]).stem
    checker = binaries / Path(config["assets"]["checker"]).stem
    validator_cases = read_json(PROBLEM / config["selfTests"]["validator"])
    for case in validator_cases:
        result = run([validator], data=case["input"].encode())
        require(result.returncode in (0, 3),
                f"Validator crashed in self-test: {case['name']}")
        require((result.returncode == 0) == (case["verdict"] == "VALID"),
                f"Validator self-test failed: {case['name']}")

    def check(input_path, answer_path, output):
        output_path = build / "candidate.out"
        output_path.write_bytes(output)
        return run([checker, input_path, output_path, answer_path])

    checker_cases = read_json(PROBLEM / config["selfTests"]["checker"])
    for case in checker_cases:
        input_path = build / "checker.in"
        answer_path = build / "checker.ans"
        input_path.write_text(case["input"], encoding="utf-8")
        answer_path.write_text(case["answer"], encoding="utf-8")
        result = check(input_path, answer_path, case["output"].encode())
        require(result.returncode == CHECKER_CODES[case["verdict"]],
                f"Checker self-test failed: {case['name']}\n{result.stderr.decode(errors='replace')}")

    inputs = {}
    for manual in config["testsets"]["tests"]["manualTests"]:
        inputs[manual["index"]] = (PROBLEM / manual["input"]).read_bytes()
    script = PROBLEM / config["testsets"]["tests"]["script"]
    for line in script.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        tokens = shlex.split(line)
        require(len(tokens) >= 4 and tokens[-2] == ">",
                "Pilot supports only 'generator arguments > index' script lines.")
        index = int(tokens[-1])
        require(index not in inputs, f"Duplicate test index: {index}")
        command = [binaries / tokens[0], *tokens[1:-2]]
        first, second = run(command), run(command)
        require(first.returncode == second.returncode == 0,
                f"Generator failed: {line}\n{first.stderr.decode(errors='replace')}")
        require(first.stdout == second.stdout, f"Nondeterministic generator: {line}")
        inputs[index] = first.stdout
    require(sorted(inputs) == list(range(1, len(inputs) + 1)), "Tests must be contiguous.")
    require(len(set(inputs.values())) == len(inputs), "Duplicate test inputs.")
    solutions = config["solutions"]
    require(sum(solution["tag"] == "MA" for solution in solutions) == 1,
            "Exactly one main solution is required.")
    killed = {solution["name"]: [] for solution in solutions if solution["tag"] == "WA"}
    hashes = {}
    for index, data in sorted(inputs.items()):
        input_path = tests_dir / f"{index:02d}.in"
        answer_path = tests_dir / f"{index:02d}.ans"
        input_path.write_bytes(data)
        valid = run([validator], data=data)
        require(valid.returncode == 0,
                f"Invalid test {index}: {valid.stderr.decode(errors='replace')}")
        a, b = map(int, data.split())
        oracle = f"{a + b}\n".encode()
        answer_path.write_bytes(oracle)
        hashes[str(index)] = hashlib.sha256(data).hexdigest()
        for solution in solutions:
            result = run([binaries / Path(solution["name"]).stem], data=data)
            require(result.returncode == 0, f"Solution crashed: {solution['name']} on test {index}")
            verdict = check(input_path, answer_path, result.stdout).returncode
            if solution["tag"] in ("MA", "OK"):
                require(verdict == 0, f"{solution['name']} failed test {index} (checker {verdict}).")
                require(result.stdout.split() == oracle.split(),
                        f"{solution['name']} disagrees with the Python oracle on test {index}.")
            elif solution["tag"] == "WA":
                require(verdict in (0, 1), f"Unexpected verdict {verdict} for {solution['name']}.")
                if verdict == 1:
                    killed[solution["name"]].append(index)
            else:
                raise RuntimeError(f"Unsupported pilot solution tag: {solution['tag']}")
    for manual in config["testsets"]["tests"]["manualTests"]:
        require((PROBLEM / manual["output"]).read_bytes() ==
                (tests_dir / f"{manual['index']:02d}.ans").read_bytes(),
                f"Sample answer mismatch at test {manual['index']}.")
    require(all(killed.values()), "At least one deliberately wrong solution survived all tests.")
    report = {
        "passed": True, "testCount": len(inputs), "validatorSelfTests": len(validator_cases),
        "checkerSelfTests": len(checker_cases), "acceptedSolutions":
        [solution["name"] for solution in solutions if solution["tag"] in ("MA", "OK")],
        "wrongSolutionsRejectedOn": killed, "inputSha256": hashes,
    }
    write_json(build / "verification.json", report)
    print(f"PASS: {len(inputs)} unique tests, {len(validator_cases)} validator self-tests, "
          f"{len(checker_cases)} checker self-tests; both wrong solutions rejected.", flush=True)
    return report


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


class Polygon:
    def __init__(self):
        self.key = os.environ.get("POLYGON_API_KEY") or getpass.getpass("Polygon API key: ")
        self.secret = os.environ.get("POLYGON_API_SECRET") or getpass.getpass("Polygon API secret: ")
        require(bool(self.key and self.secret), "Both Polygon credentials are required.")
        self.opener = urllib.request.build_opener(NoRedirect())

    def call(self, method, parameters=None, *, raw=False):
        # Sign decoded values before URL encoding. Never print the signed request.
        params = {key: str(value).lower() if isinstance(value, bool) else str(value)
                  for key, value in (parameters or {}).items()}
        params.update(apiKey=self.key, time=str(int(time.time())))
        canonical = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
        nonce = secrets.token_hex(3)
        signature = f"{nonce}/{method}?{canonical}#{self.secret}"
        params["apiSig"] = nonce + hashlib.sha512(signature.encode()).hexdigest()
        request = urllib.request.Request(
            API + method, data=urllib.parse.urlencode(params).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                     "User-Agent": "cp-problem-library-pilot/0.1"},
        )
        try:
            with self.opener.open(request, timeout=270 if method == "problem.renderStatements" else 60) as response:
                payload = response.read()
        except urllib.error.HTTPError as error:
            payload = error.read()
            try:
                message = json.loads(payload).get("comment", f"HTTP {error.code}")
            except (ValueError, AttributeError):
                message = f"HTTP {error.code} (non-JSON response)"
            raise RuntimeError(f"{method}: {self.redact(message)}") from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError(f"{method}: network error; inspect remote state before retrying mutations.") from None
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            require(raw, f"{method}: unexpected non-JSON response")
            return payload
        if isinstance(result, dict) and result.get("status") == "FAILED":
            raise RuntimeError(f"{method}: {self.redact(result.get('comment', 'failed'))}")
        if raw:
            return payload
        require(isinstance(result, dict) and result.get("status") == "OK", f"{method}: malformed response")
        return result.get("result")

    def redact(self, message):
        return str(message).replace(self.key, "[API KEY]").replace(self.secret, "[API SECRET]")


def problem_call(api, state, method, **parameters):
    return api.call(method, {"problemId": state["id"], **parameters})


def prepare_import(api, state):
    """Grant Codeforces the read access needed to import this Polygon problem."""
    remote = api.call("problems.list", {"id": state["id"]})
    require(len(remote) == 1 and remote[0]["name"] == state["name"]
            and remote[0]["owner"] == state["owner"], "Remote identity mismatch.")
    accesses = problem_call(api, state, "problem.accesses")
    current = next((entry["accessType"] for entry in accesses if entry["login"] == "codeforces"), None)
    if current not in ("READ", "WRITE", "OWNER"):
        problem_call(api, state, "problem.setAccess", login="codeforces", accessType="READ")
    accesses = problem_call(api, state, "problem.accesses")
    current = next((entry["accessType"] for entry in accesses if entry["login"] == "codeforces"), None)
    require(current in ("READ", "WRITE", "OWNER"), "Codeforces import access was not granted.")
    state["importAccess"] = {"login": "codeforces", "accessType": current, "verified": True}
    write_json(STATE, state)
    write_json(PROBLEM / "build" / "polygon-accesses.json", accesses)
    print(f"Verified Codeforces import access: codeforces has {current} on problem {state['id']}.", flush=True)


def upload(api):
    config = load_problem()
    if STATE.exists():
        raise RuntimeError("This pilot already has a remote ID. Use status/build; updates belong to the next CLI phase.")
    existing = api.call("problems.list", {"name": config["name"]})
    require(not any(problem["name"] == config["name"] and problem["accessType"] == "OWNER"
                    for problem in existing),
            "A problem with this name already exists. Reconcile it before creating another.")
    remote = api.call("problem.create", {"name": config["name"]})
    state = {"id": remote["id"], "owner": remote["owner"], "name": remote["name"],
             "url": f"https://polygon.codeforces.com/problem?problemId={remote['id']}",
             "stage": "created"}
    write_json(STATE, state)
    print(f"Created Polygon problem {state['id']}: {state['url']}", flush=True)
    populate(api, state, config)
    prepare_import(api, state)


def populate(api, state, config):
    problem_call(api, state, "problem.updateInfo", **config["info"])
    if "tags" in config:
        problem_call(api, state, "problem.saveTags", tags=",".join(config["tags"]))
    for language, statement in config["statements"].items():
        parameters = {key: (PROBLEM / value).read_text(encoding="utf-8")
                      if key in ("legend", "input", "output", "notes", "tutorial", "scoring", "interaction")
                      else value for key, value in statement.items()}
        problem_call(api, state, "problem.saveStatement", lang=language, **parameters)
    for file in config["files"]:
        parameters = {key: value for key, value in file.items() if key != "path"}
        parameters["file"] = (PROBLEM / file["path"]).read_text(encoding="utf-8")
        problem_call(api, state, "problem.saveFile", **parameters)
    for solution in config["solutions"]:
        parameters = {key: value for key, value in solution.items() if key != "path"}
        parameters["file"] = (PROBLEM / solution["path"]).read_text(encoding="utf-8")
        problem_call(api, state, "problem.saveSolution", **parameters)
    problem_call(api, state, "problem.setValidator", validator=config["assets"]["validator"])
    problem_call(api, state, "problem.setChecker", checker=config["assets"]["checker"])
    for testset, settings in config["testsets"].items():
        for manual in settings["manualTests"]:
            data = (PROBLEM / manual["input"]).read_text(encoding="utf-8")
            problem_call(api, state, "problem.saveTest", testset=testset, testIndex=manual["index"],
                         testInput=data, testDescription=manual["description"],
                         testUseInStatements=manual["useInStatements"],
                         verifyInputOutputForStatements=True)
        problem_call(api, state, "problem.saveScript", testset=testset,
                     source=(PROBLEM / settings["script"]).read_text(encoding="utf-8"))
    for index, case in enumerate(remote_cases(config, "validator"), 1):
        problem_call(api, state, "problem.saveValidatorTest", testIndex=index,
                     testInput=case["input"], testVerdict=case["verdict"])
    for index, case in enumerate(remote_cases(config, "checker"), 1):
        problem_call(api, state, "problem.saveCheckerTest", testIndex=index,
                     testInput=case["input"], testAnswer=case["answer"],
                     testOutput=case["output"], testVerdict=case["verdict"])
    result = problem_call(api, state, "problem.commitChanges", minorChanges=True,
                          message="A+B pilot: verified solutions, generators, validator, checker and tests")
    require(not result or not result.get("conflictOccurred"), "Polygon commit reported a conflict.")
    state["stage"] = "committed"
    write_json(STATE, state)
    print("Uploaded and committed all problem assets.", flush=True)


def build(api, state):
    require(state["stage"] in ("committed", "building", "ready"), "Finish the upload before building.")
    if state["stage"] == "committed":
        remote = api.call("problems.list", {"id": state["id"]})
        require(len(remote) == 1 and not remote[0]["modified"], "Commit the working copy before building.")
        state["revision"] = remote[0]["revision"]
        problem_call(api, state, "problem.buildPackage", full=True, verify=True)
        state["stage"] = "building"
        write_json(STATE, state)
        print("Started a full package build with Polygon verification.", flush=True)
    else:
        print("A package was already requested; use status to inspect it.", flush=True)


def status(api, state):
    packages = problem_call(api, state, "problem.packages")
    cautions = problem_call(api, state, "problem.cautions")
    report = {"problem": {key: state[key] for key in ("id", "owner", "name", "url")},
              "packages": packages, "cautions": cautions}
    write_json(PROBLEM / "build" / "polygon-status.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return packages


def audit(api, state):
    """Compare uploaded text and metadata to the manifest before trusting export."""
    config = load_problem()

    def normalized(value):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return value.replace("\r\n", "\n")

    def raw(method, **parameters):
        return api.call(method, {"problemId": state["id"], **parameters}, raw=True)

    require(problem_call(api, state, "problem.info") == config["info"], "Remote problem info differs.")
    statements = problem_call(api, state, "problem.statements")
    for language, statement in config["statements"].items():
        for key, value in statement.items():
            expected = (PROBLEM / value).read_text(encoding="utf-8") if key in (
                "legend", "input", "output", "notes", "tutorial", "scoring", "interaction") else value
            require(normalized(statements[language][key]) == normalized(expected),
                    f"Remote statement {language}.{key} differs.")
    for file in config["files"]:
        content = raw("problem.viewFile", type=file["type"], name=file["name"])
        require(normalized(content) == normalized((PROBLEM / file["path"]).read_text(encoding="utf-8")),
                f"Remote file differs: {file['name']}")
    remote_solutions = {solution["name"]: solution for solution in problem_call(api, state, "problem.solutions")}
    for solution in config["solutions"]:
        require(remote_solutions[solution["name"]]["tag"] == solution["tag"], "Remote solution tag differs.")
        require(remote_solutions[solution["name"]]["sourceType"] == solution["sourceType"],
                "Remote solution language differs.")
        content = raw("problem.viewSolution", name=solution["name"])
        require(normalized(content) == normalized((PROBLEM / solution["path"]).read_text(encoding="utf-8")),
                f"Remote solution differs: {solution['name']}")
    for asset in ("validator", "checker"):
        require(problem_call(api, state, f"problem.{asset}") == config["assets"][asset],
                f"Remote {asset} differs.")
    for testset, settings in config["testsets"].items():
        remote_script = normalized(raw("problem.script", testset=testset))
        local_script = (PROBLEM / settings["script"]).read_text(encoding="utf-8")
        require([shlex.split(line) for line in remote_script.splitlines() if line.strip()] ==
                [shlex.split(line) for line in local_script.splitlines() if line.strip()], "Remote script differs.")
        remote_tests = {test["index"]: test for test in problem_call(api, state, "problem.tests", testset=testset)}
        require(len(remote_tests) == read_json(PROBLEM / "build" / "verification.json")["testCount"],
                "Remote test count differs.")
        for manual in settings["manualTests"]:
            test = remote_tests[manual["index"]]
            input_data = base64.b64decode(test["inputBase64"]) if "inputBase64" in test else test["input"]
            require(normalized(input_data) == normalized((PROBLEM / manual["input"]).read_bytes()),
                    f"Remote manual input {manual['index']} differs.")
            require(test["useInStatements"] == manual["useInStatements"], "Remote sample flag differs.")
    fixture_runs = {}
    for asset in ("validator", "checker"):
        local_cases = remote_cases(config, asset)
        actual_cases = problem_call(api, state, f"problem.{asset}Tests")
        fixture_runs[asset] = [{key: case[key] for key in (
            "index", "expectedVerdict", "runVerdict", "runComment") if key in case}
            for case in actual_cases]
        require(len(actual_cases) == len(local_cases), f"Remote {asset} fixture count differs.")
        for expected, actual in zip(local_cases, sorted(actual_cases, key=lambda case: case["index"])):
            require(expected["verdict"] == actual["expectedVerdict"], "Remote fixture verdict differs.")
            require(actual.get("runVerdict") == expected["verdict"],
                    f"Remote {asset} fixture {actual['index']} has not passed its expected verdict.")
            for field in ("input", "answer", "output"):
                if field in expected:
                    require(normalized(expected[field]) == normalized(actual[field]), "Remote fixture data differs.")
    require(sorted(problem_call(api, state, "problem.viewTags")) == sorted(config["tags"]), "Remote tags differ.")
    write_json(PROBLEM / "build" / "polygon-audit.json", {
        "passed": True, "problemId": state["id"], "fixtureRuns": fixture_runs,
    })
    print("PASS: remote statements, files, solutions, tags, tests, scripts, and fixtures match local assets.", flush=True)


def download(api, state):
    packages = problem_call(api, state, "problem.packages")
    remote = api.call("problems.list", {"id": state["id"]})
    require(len(remote) == 1 and not remote[0]["modified"], "Remote working copy has uncommitted changes.")
    revision = remote[0]["revision"]
    ready = [package for package in packages if package["state"] == "READY" and package["revision"] == revision]
    require(bool(ready), "Polygon has no READY package yet; run status again later.")
    package = max(ready, key=lambda item: (item["revision"], item["id"]))
    payload = api.call("problem.package", {"problemId": state["id"], "packageId": package["id"],
                                            "type": "linux"}, raw=True)
    require(zipfile.is_zipfile(io.BytesIO(payload)), "Polygon did not return a ZIP package.")
    directory = PROBLEM / "artifacts"
    directory.mkdir(exist_ok=True)
    destination = directory / f"{state['name']}-r{package['revision']}-linux.zip"
    destination.write_bytes(payload)
    # Inspect without extracting untrusted archive paths.
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        xml_names = [name for name in archive.namelist() if name == "problem.xml" or name.endswith("/problem.xml")]
        require(len(xml_names) == 1, "Expected one Polygon problem.xml in the archive.")
        xml_data = archive.read(xml_names[0])
        (directory / "problem.xml").write_bytes(xml_data)
        root = ET.fromstring(xml_data)
        testset = root.find("./judging/testset[@name='tests']")
        require(testset is not None, "Package is missing the tests testset.")
        tests = testset.find("tests")
        require(tests is not None, "Package is missing test metadata.")
        count = len(tests)
        require(count == read_json(PROBLEM / "build" / "verification.json")["testCount"],
                "Polygon package test count disagrees with local verification.")
        input_pattern = testset.findtext("input-path-pattern")
        answer_pattern = testset.findtext("answer-path-pattern")
        require(input_pattern and answer_pattern, "Package has no test path patterns.")
        prefix = xml_names[0][:-len("problem.xml")]
        for index in range(1, count + 1):
            for pattern, suffix in ((input_pattern, "in"), (answer_pattern, "ans")):
                actual = archive.read(prefix + (pattern % index)).replace(b"\r\n", b"\n")
                expected = (PROBLEM / "build" / "tests" / f"{index:02d}.{suffix}").read_bytes()
                require(actual == expected, f"Package test {index} {suffix} disagrees with local data.")
    state.update(stage="ready", packageId=package["id"], revision=package["revision"],
                 packageUrl=root.get("url"),
                 packagePath=str(destination.relative_to(PROBLEM)), packageSha256=hashlib.sha256(payload).hexdigest())
    write_json(STATE, state)
    print(f"Downloaded and compared all {count} inputs and answers: {destination}", flush=True)


def render(api, state):
    result = problem_call(api, state, "problem.renderStatements", includeContent=True)
    directory = PROBLEM / "artifacts"
    directory.mkdir(exist_ok=True)
    for category in ("statements", "tutorials"):
        for statement in result.get(category, []):
            for format_name in ("html", "pdf"):
                rendered = statement[format_name]
                require(rendered["status"] == "OK", f"{category} {format_name} rendering failed.")
                content = base64.b64decode(rendered["contentBase64"])
                require(hashlib.sha256(content).hexdigest() == rendered["sha256"], "Render hash mismatch.")
                filename = f"{category}-{statement['language']}.{format_name}"
                (directory / filename).write_bytes(content)
    print("Downloaded successful Polygon statement and tutorial renders.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "upload", "build", "status", "audit", "download", "render", "prepare-import"))
    args = parser.parse_args()
    if args.command in ("verify", "upload"):
        verification()
    if args.command == "verify":
        return
    api = Polygon()
    if args.command == "upload":
        upload(api)
        return
    require(STATE.exists(), "Upload the pilot first.")
    state = read_json(STATE)
    {"build": build, "status": status, "audit": audit, "download": download,
     "render": render, "prepare-import": prepare_import}[args.command](api, state)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)

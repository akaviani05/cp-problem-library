import argparse
import json
import platform
import shutil
import sys

from . import __version__
from .catalog import new_problem, refresh_catalog
from .config import init_config, load_config
from .model import Problem
from .polygon import Polygon
from . import sync
from .util import Error, problem_lock, read_json, repository, require, write_json
from .verify import generate, stress, verified, verify


def parser():
    result = argparse.ArgumentParser(prog="cppl", description="Author, verify, and publish competitive programming problems to Polygon.")
    result.add_argument("--root", type=str, help="Repository root; defaults to the current checkout")
    result.add_argument("--version", action="version", version=__version__)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check setup without showing credentials")
    config = commands.add_parser("config", help="Manage ignored local credentials")
    config.add_argument("action", choices=["init", "check"])
    config.add_argument("--contest", type=int, default=0)
    config.add_argument("--owner", default="")
    config.add_argument("--force", action="store_true")
    new = commands.add_parser("new", help="Create an unfinished problem from a template")
    new.add_argument("slug")
    new.add_argument("--title", required=True)
    new.add_argument("--description", required=True)
    new.add_argument("--tags", required=True, help="Comma-separated tags")
    new.add_argument("--template", default="plain")
    commands.add_parser("catalog", help="Refresh the generated README problem table")
    for name, help_text in [
        ("lint", "Validate manifest and required assets"), ("generate", "Compile, generate and validate deterministic inputs"),
        ("verify", "Verify solutions, fixtures, samples, and independent stress tests"),
        ("stress", "Run only the independent small-case oracle comparison"),
        ("plan", "Print a verified upload plan without network access"),
        ("upload", "Reconcile, upload, read back, commit and grant Codeforces access"),
        ("build", "Build a full verified package and wait for completion"),
        ("export", "Download the current Linux package and compare every input/answer"),
        ("publish", "Verify, upload, build, export, render and refresh README"),
        ("status", "Show Polygon package state and cautions"), ("render", "Download statement/tutorial HTML and PDF"),
        ("prepare-import", "Ensure codeforces has READ access"),
        ("inspect", "Show compact local verification and performance evidence"),
        ("attach", "Attach a known existing Polygon ID without overwriting it"),
    ]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("slug")
        if name in ("status", "inspect"):
            command.add_argument("--json", action="store_true")
        if name == "attach":
            command.add_argument("--id", required=True, type=int)
    return result


def inspect(problem):
    result = {"slug": problem.slug, "draft": problem.config.get("draft", False), "verified": False}
    report_path = problem.build / "verification.json"
    if report_path.exists():
        report = read_json(report_path)
        try:
            verified(problem)
            result["verified"] = True
        except Error as error:
            result["verificationIssue"] = str(error)
        result.update(
                      tests=report["testCount"], stressCases=report.get("stressCases", 0),
                      validatorFixtures=report.get("validatorSelfTests"), checkerFixtures=report.get("checkerSelfTests"),
                      verificationSeconds=report.get("wallSeconds"), wrongSolutionsRejectedOn=report.get("wrongSolutionsRejectedOn", {}))
        result["solutions"] = {name: {"maxWallSeconds": max(run["wallSeconds"] for run in runs),
                                       "maxCpuSeconds": max(run["cpuSeconds"] for run in runs),
                                       "maxRssKiB": max((run["maxRssKiB"] for run in runs if run["maxRssKiB"] is not None), default=None)}
                                 for name, runs in report.get("solutions", {}).items() if runs}
    if problem.state_path.exists():
        state = read_json(problem.state_path)
        result["polygon"] = {key: state[key] for key in ("id", "url", "revision", "stage", "packageId", "importAccess") if key in state}
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        from pathlib import Path
        root = Path(args.root).resolve() if args.root else repository()
        config = load_config(root)
        if args.command == "doctor" or (args.command == "config" and args.action == "check"):
            print(json.dumps({"version": __version__, "python": platform.python_version(), "platform": sys.platform,
                              "g++": bool(shutil.which("g++")), "credentialsConfigured": bool(config["api_key"] and config["api_secret"]),
                              "gnuTime": bool(shutil.which("time")),
                              "problemPrefix": config["problem_prefix"], "contestId": config["contest_id"],
                              "contestLinking": "optional/manual; prefix is the grouping mechanism"}, indent=2))
            return 0
        if args.command == "config":
            init_config(root, args.contest, args.owner, args.force)
            return 0
        if args.command == "new":
            new_problem(root, args.slug, args.title, args.description, args.tags, args.template)
            return 0
        if args.command == "catalog":
            refresh_catalog(root)
            return 0
        problem = Problem(root, args.slug)
        with problem_lock(problem):
            if args.command == "lint":
                print(json.dumps(problem.validate(), indent=2))
            elif args.command == "generate":
                generate(problem)
            elif args.command == "verify":
                verify(problem)
            elif args.command == "stress":
                stress(problem)
            elif args.command == "plan":
                print(json.dumps(sync.plan(problem), indent=2))
            elif args.command == "inspect":
                print(json.dumps(inspect(problem), indent=2))
            else:
                if args.command == "publish":
                    try:
                        verified(problem)
                        print("Reusing current verification evidence.", flush=True)
                    except Error:
                        verify(problem)
                api = Polygon(config)
                if args.command == "attach":
                    require(not problem.state_path.exists() or "id" not in read_json(problem.state_path),
                            "Already attached; reconcile the recorded identity explicitly.")
                    remote = api.call("problems.list", {"id": args.id})
                    require(len(remote) == 1 and remote[0]["name"] == problem.config["name"], "ID does not match manifest name.")
                    state = {"id": remote[0]["id"], "name": remote[0]["name"], "owner": remote[0]["owner"],
                             "url": f"https://polygon.codeforces.com/problem?problemId={args.id}", "stage": "attached",
                             "revision": remote[0]["revision"]}
                    write_json(problem.state_path, state)
                    print(f"Attached {args.id}; no remote assets were modified.")
                elif args.command in ("upload", "publish"):
                    state = sync.upload(problem, api, config)
                    if args.command == "publish":
                        sync.build_and_wait(problem, api, config, state)
                        sync.export_package(problem, api, state)
                        sync.render(problem, api, state)
                    refresh_catalog(root)
                elif args.command == "build":
                    sync.build_and_wait(problem, api, config)
                elif args.command == "export":
                    sync.export_package(problem, api)
                elif args.command == "render":
                    sync.render(problem, api)
                elif args.command == "prepare-import":
                    state = sync.state_for(problem)
                    sync.identity(api, state)
                    sync.prepare_import(problem, api, state)
                    print("Codeforces import access verified.")
                elif args.command == "status":
                    result = sync.status(problem, api)
                    if args.json:
                        print(json.dumps(result, indent=2))
                    else:
                        ready = [p for p in result["packages"] if p["revision"] == result["revision"]]
                        print(f"Polygon {result['problemId']}, revision {result['revision']}: "
                              f"{', '.join(sorted({p['state'] for p in ready})) or 'no package'}")
                        for category in ("common", "statement", "structure", "issues"):
                            for caution in result["cautions"][category]:
                                print(f"{caution['severity']}: {caution['message']}")
                print(f"Polygon API calls: {api.calls}.", flush=True)
        return 0
    except (Error, OSError, KeyError, TypeError, ValueError) as error:
        message = str(error)
        if "config" in locals():
            for key in ("api_key", "api_secret"):
                if config.get(key):
                    message = message.replace(config[key], "[REDACTED]")
        print(f"ERROR: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

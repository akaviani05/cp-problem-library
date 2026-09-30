import base64
import copy
import hashlib
import io
from pathlib import Path
import time
import zipfile
import xml.etree.ElementTree as ET

from .model import TEXT_FIELDS
from .util import Error, digest, normalize, read_json, require, utc_now, write_json
from .verify import verified


def state_for(problem):
    require(problem.state_path.is_file(), "Upload the problem first.")
    return read_json(problem.state_path)


def identity(api, state):
    matches = api.call("problems.list", {"id": state["id"]})
    require(len(matches) == 1 and matches[0]["name"] == state["name"]
            and matches[0]["owner"] == state["owner"], "Remote identity mismatch; check polygon-state.json.")
    return matches[0]


def snapshot(api, state):
    result = {"info": api.problem(state, "problem.info"),
              "tags": sorted(api.problem(state, "problem.viewTags")), "statements": {}, "files": {}, "solutions": {},
              "validator": api.problem(state, "problem.validator"), "checker": api.problem(state, "problem.checker"),
              "manualTests": {}, "validatorTests": {}, "checkerTests": {}}
    statements = api.problem(state, "problem.statements")
    for language, statement in statements.items():
        result["statements"][language] = {key: normalize(statement.get(key, ""))
                                           for key in TEXT_FIELDS | {"name", "encoding"}}
    inventory = api.problem(state, "problem.files")
    for kind, field in (("resource", "resourceFiles"), ("source", "sourceFiles"), ("aux", "auxFiles")):
        for file in inventory[field]:
            content = api.call("problem.viewFile", {"problemId": state["id"], "type": kind, "name": file["name"]}, raw=True)
            entry = {"content": normalize(content)}
            if kind == "source":
                entry["sourceType"] = file["sourceType"]
            result["files"][f"{kind}:{file['name']}"] = entry
    for solution in api.problem(state, "problem.solutions"):
        content = api.call("problem.viewSolution", {"problemId": state["id"], "name": solution["name"]}, raw=True)
        result["solutions"][solution["name"]] = {"content": normalize(content), "tag": solution["tag"],
                                                    "sourceType": solution["sourceType"]}
    result["script"] = normalize(api.call("problem.script", {"problemId": state["id"], "testset": "tests"}, raw=True)).strip()
    for test in api.problem(state, "problem.tests", testset="tests"):
        if test["manual"]:
            data = base64.b64decode(test["inputBase64"]) if "inputBase64" in test else test.get("input", "")
            result["manualTests"][str(test["index"])] = {
                "input": normalize(data), "description": test.get("description", ""),
                "sample": test["useInStatements"], "inputForStatements": normalize(test.get("inputForStatement", "")),
                "outputForStatements": normalize(test.get("outputForStatement", "")),
                "verifyInputOutputForStatements": test.get("verifyInputOutputForStatements", True),
                "group": test.get("group", ""), "points": test.get("points"),
            }
    for role in ("validator", "checker"):
        for case in api.problem(state, f"problem.{role}Tests"):
            entry = {"input": normalize(case["input"]), "verdict": case["expectedVerdict"]}
            if role == "checker":
                entry.update(answer=normalize(case["answer"]), output=normalize(case["output"]))
            else:
                entry.update(testset=case.get("testset", ""), group=case.get("group", ""))
            result[role + "Tests"][str(case["index"])] = entry
    return result


def get_path(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def put_path(value, path, item):
    for key in path[:-1]:
        value = value.setdefault(key, {})
    value[path[-1]] = item


def compatible(current, before, desired):
    """Each observed leaf must equal either the recorded baseline or our intended write."""
    if all(isinstance(item, dict) for item in (current, before, desired)):
        return all(compatible(current.get(key), before.get(key), desired.get(key))
                   for key in current.keys() | before.keys() | desired.keys())
    return current == before or current == desired


def operations(problem, baseline):
    c = problem.config
    desired = copy.deepcopy(baseline)
    changes = []

    def add(method, path, value, **parameters):
        put_path(desired, path, value)
        changes.append((method, parameters, path, value))

    add("problem.updateInfo", ["info"], {**baseline["info"], **c["info"]}, **c["info"])
    add("problem.saveTags", ["tags"], sorted(c["tags"]), tags=",".join(c["tags"]))
    for language, statement in c["statements"].items():
        params = {key: problem.text(value) if key in TEXT_FIELDS else value for key, value in statement.items()}
        value = {key: normalize(params.get(key, "")) for key in TEXT_FIELDS | {"name", "encoding"}}
        add("problem.saveStatement", ["statements", language], value, lang=language, **params)
    for file in c["files"]:
        params = {key: value for key, value in file.items() if key != "path"}
        content = problem.text(file["path"])
        value = {"content": normalize(content)}
        if file["type"] == "source":
            value["sourceType"] = file["sourceType"]
        add("problem.saveFile", ["files", f"{file['type']}:{file['name']}"], value, file=content, **params)
    for solution in c["solutions"]:
        params = {key: value for key, value in solution.items() if key != "path"}
        content = problem.text(solution["path"])
        value = {"content": normalize(content), "tag": solution["tag"], "sourceType": solution["sourceType"]}
        add("problem.saveSolution", ["solutions", solution["name"]], value, file=content, **params)
    for role in ("validator", "checker"):
        add(f"problem.set{role.capitalize()}", [role], c["assets"][role], **{role: c["assets"][role]})
    for manual in c["testsets"]["tests"].get("manualTests", []):
        data = problem.text(manual["input"])
        value = {"input": normalize(data), "description": manual.get("description", ""),
                 "sample": manual.get("useInStatements", False), "inputForStatements": "", "outputForStatements": "",
                 "verifyInputOutputForStatements": True, "group": "", "points": None}
        add("problem.saveTest", ["manualTests", str(manual["index"])], value, testset="tests", testIndex=manual["index"],
            testInput=data, testDescription=value["description"], testUseInStatements=value["sample"],
            testInputForStatements="", testOutputForStatements="", verifyInputOutputForStatements=True)
    script = problem.text(c["testsets"]["tests"]["script"])
    add("problem.saveScript", ["script"], normalize(script).strip(), testset="tests", source=script)
    for role in ("validator", "checker"):
        cases = problem.fixtures(role, remote=True)
        require(len(cases) >= len(baseline[role + "Tests"]),
                f"Removing remote {role} fixtures is unsupported; retain them or use a new problem.")
        for index, case in enumerate(cases, 1):
            value = {"input": normalize(case["input"]), "verdict": case["verdict"]}
            params = {"testIndex": index, "testInput": case["input"], "testVerdict": case["verdict"]}
            if role == "checker":
                value.update(answer=normalize(case["answer"]), output=normalize(case["output"]))
                params.update(testAnswer=case["answer"], testOutput=case["output"])
            else:
                value.update(testset="", group="")
            add(f"problem.save{role.capitalize()}Test", [role + "Tests", str(index)], value, **params)
    expected_sources = {f"{item['type']}:{item['name']}" for item in c["files"]}
    require(all(key in expected_sources or key.startswith("resource:") for key in baseline["files"]),
            "Removing remote source/aux files is unsupported; retain them in the manifest.")
    require(set(baseline["solutions"]) <= {entry["name"] for entry in c["solutions"]},
            "Removing remote solutions is unsupported; retain them in the manifest.")
    require(set(baseline["manualTests"]) <= {str(entry["index"]) for entry in c["testsets"]["tests"].get("manualTests", [])},
            "Removing manual tests requires an explicit reviewed deletion; keep them in the manifest.")
    return changes, desired


def prepare_import(problem, api, state):
    accesses = api.problem(state, "problem.accesses")
    current = next((item["accessType"] for item in accesses if item["login"] == "codeforces"), None)
    if current not in ("READ", "WRITE", "OWNER"):
        api.problem(state, "problem.setAccess", login="codeforces", accessType="READ")
    accesses = api.problem(state, "problem.accesses")
    current = next((item["accessType"] for item in accesses if item["login"] == "codeforces"), None)
    require(current in ("READ", "WRITE", "OWNER"), "Codeforces import access was not granted.")
    state["importAccess"] = {"login": "codeforces", "accessType": current, "verified": True}
    write_json(problem.state_path, state)
    write_json(problem.build / "polygon-accesses.json", accesses)


def upload(problem, api, config):
    report = verified(problem)
    if problem.state_path.exists():
        state = read_json(problem.state_path)
    else:
        state = {"name": problem.config["name"], "stage": "creating", "startedAt": utc_now()}
        matches = api.call("problems.list", {"name": state["name"]})
        require(not any(item["name"] == state["name"] and item["accessType"] == "OWNER" for item in matches),
                "An owned problem with this name already exists. Attach its ID explicitly; do not duplicate it.")
        write_json(problem.state_path, state)
        remote = api.call("problem.create", {"name": state["name"]})
        state.update(id=remote["id"], owner=remote["owner"], stage="created")
        state["url"] = f"https://polygon.codeforces.com/problem?problemId={state['id']}"
        write_json(problem.state_path, state)
        print(f"Created Polygon {state['id']}: {state['url']}", flush=True)
    if "id" not in state:
        matches = [item for item in api.call("problems.list", {"name": state["name"]})
                   if item["name"] == state["name"] and item["accessType"] == "OWNER"]
        require(len(matches) == 1, "Creation outcome is uncertain; inspect Polygon and attach the correct ID.")
        remote = matches[0]
        state.update(id=remote["id"], owner=remote["owner"], stage="created",
                     url=f"https://polygon.codeforces.com/problem?problemId={remote['id']}")
        write_json(problem.state_path, state)
    remote = identity(api, state)
    require(state["name"] == problem.config["name"], "Remote names cannot be changed implicitly.")
    current = snapshot(api, state)
    if state.get("stage") == "uploading":
        baseline = state["uploadBaseline"]
        changes, desired = operations(problem, baseline)
        require(state.get("intentFingerprint") == report["fingerprint"]
                or state.get("uploadDesiredFingerprint") == digest(desired),
                "Finish the pending upload before changing its remote payload.")
        require(compatible(current, baseline, desired), "Remote changes conflict with the pending upload; inspect them before proceeding.")
    else:
        require(not remote["modified"], "Remote working copy contains user changes; commit or reconcile them before upload.")
        if state.get("remoteBaseline"):
            require(current == state["remoteBaseline"], "Remote assets changed since the last sync; inspect before overwriting.")
        baseline = current
        changes, desired = operations(problem, baseline)
        state.update(stage="uploading", intentFingerprint=report["fingerprint"], uploadBaseline=baseline,
                     uploadDesiredFingerprint=digest(desired))
        write_json(problem.state_path, state)
    count = 0
    for method, params, path, value in changes:
        if get_path(current, path) == value:
            continue
        api.problem(state, method, **params)
        put_path(current, path, value)
        count += 1
        print(f"Uploaded {'/'.join(path)}.", flush=True)
    observed = snapshot(api, state)
    require(observed == desired, "Remote readback differs; upload remains resumable, inspect the mismatch.")
    result = api.problem(state, "problem.commitChanges", minorChanges=True, message=f"cppl: verified {problem.slug}")
    require(not result or not result.get("conflictOccurred"), "Commit reported a conflict.")
    remote = identity(api, state)
    require(not remote["modified"], "Remote working copy was changed during commit.")
    state.update(stage="committed", revision=remote["revision"], remoteBaseline=observed,
                 sourceFingerprint=report["fingerprint"])
    state.pop("uploadBaseline", None)
    state.pop("intentFingerprint", None)
    state.pop("uploadDesiredFingerprint", None)
    write_json(problem.state_path, state)
    prepare_import(problem, api, state)
    print(f"Committed revision {state['revision']}; {count} changed assets; codeforces import access verified.", flush=True)
    return state


def status(problem, api, state=None):
    state = state or state_for(problem)
    remote = identity(api, state)
    packages = api.problem(state, "problem.packages")
    cautions = api.problem(state, "problem.cautions")
    result = {"problemId": state["id"], "url": state["url"], "revision": remote["revision"],
              "modified": remote["modified"], "packages": packages, "cautions": cautions}
    write_json(problem.build / "polygon-status.json", result)
    return result


def build_and_wait(problem, api, config, state=None):
    state = state or state_for(problem)
    remote = identity(api, state)
    require(not remote["modified"] and remote["revision"] == state["revision"], "Remote revision changed; reconcile it before building.")
    packages = api.problem(state, "problem.packages")
    target = [entry for entry in packages if entry["revision"] == state["revision"]]
    if not any(entry["state"] in ("PENDING", "RUNNING")
               or (entry["state"] == "READY" and entry["type"] == "linux") for entry in target):
        require(state.get("stage") != "building", "Previous build failed or is uncertain; inspect status before retrying.")
        state["stage"] = "building"
        write_json(problem.state_path, state)
        api.problem(state, "problem.buildPackage", full=True, verify=True)
        print(f"Requested full verified package for revision {state['revision']}.", flush=True)
    deadline = time.monotonic() + config["build_timeout_seconds"]
    previous = None
    while True:
        packages = api.problem(state, "problem.packages")
        target = [entry for entry in packages if entry["revision"] == state["revision"]]
        ready = [entry for entry in target if entry["state"] == "READY" and entry["type"] == "linux"]
        if ready:
            package = max(ready, key=lambda item: item["id"])
            state.update(stage="ready", packageId=package["id"])
            write_json(problem.state_path, state)
            break
        require(not any(entry["state"] == "FAILED" for entry in target), "Polygon package failed; inspect cppl status and build logs.")
        summary = sorted({entry["state"] for entry in target})
        if summary != previous:
            print(f"Polygon package: {', '.join(summary) or 'waiting for queue'}.", flush=True)
            previous = summary
        require(time.monotonic() < deadline, "Package is still building; rerun build to wait without duplicating it.")
        time.sleep(config["poll_seconds"])
    result = status(problem, api, state)
    require(not result["cautions"]["packageReadinessIssues"] and not result["cautions"]["latestPackageWarnings"],
            "Package has readiness issues or verification warnings; inspect status.")
    for category in ("common", "statement", "structure", "issues"):
        require(not any(item["severity"] == "HARD" for item in result["cautions"][category]), "Polygon reported a hard caution.")
    print(f"READY package {state['packageId']} at revision {state['revision']}.", flush=True)
    return state


def export_package(problem, api, state=None):
    report = verified(problem)
    state = state or state_for(problem)
    remote = identity(api, state)
    require(not remote["modified"] and remote["revision"] == state["revision"], "Remote revision changed; sync again before export.")
    require(state.get("sourceFingerprint") == report["fingerprint"], "Remote package does not correspond to the verified sources.")
    packages = api.problem(state, "problem.packages")
    ready = [entry for entry in packages if entry["revision"] == state["revision"]
             and entry["state"] == "READY" and entry["type"] == "linux"]
    require(ready, "No READY Linux package for this revision; run build first.")
    package = max(ready, key=lambda item: item["id"])
    payload = api.call("problem.package", {"problemId": state["id"], "packageId": package["id"], "type": "linux"}, raw=True)
    require(zipfile.is_zipfile(io.BytesIO(payload)), "Polygon did not return a ZIP package.")
    problem.artifacts.mkdir(parents=True, exist_ok=True)
    destination = problem.artifacts / f"{state['name']}-r{state['revision']}-linux.zip"
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        require(all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names), "Unsafe package archive paths.")
        descriptors = [name for name in names if name == "problem.xml" or name.endswith("/problem.xml")]
        require(len(descriptors) == 1, "Expected one problem.xml.")
        xml = archive.read(descriptors[0])
        descriptor = ET.fromstring(xml)
        require(int(descriptor.get("revision")) == state["revision"], "Package revision differs.")
        testset = descriptor.find("./judging/testset[@name='tests']")
        require(testset is not None and len(testset.find("tests")) == report["testCount"], "Package test count differs.")
        prefix = descriptors[0][:-len("problem.xml")]
        for index in range(1, report["testCount"] + 1):
            for tag, suffix in (("input-path-pattern", "in"), ("answer-path-pattern", "ans")):
                actual = normalize(archive.read(prefix + (testset.findtext(tag) % index)))
                expected = normalize((problem.build / "tests" / f"{index:02d}.{suffix}").read_bytes())
                require(actual == expected, f"Package test {index}.{suffix} differs from verified data.")
        (problem.artifacts / "problem.xml").write_bytes(xml)
    destination.write_bytes(payload)
    state.update(stage="ready", packageId=package["id"], packageUrl=descriptor.get("url"),
                 packagePath=str(destination.relative_to(problem.path)), packageSha256=hashlib.sha256(payload).hexdigest())
    write_json(problem.state_path, state)
    print(f"Exported and compared every input/answer: {destination}", flush=True)
    return destination


def render(problem, api, state=None):
    state = state or state_for(problem)
    result = api.problem(state, "problem.renderStatements", includeContent=True)
    problem.artifacts.mkdir(parents=True, exist_ok=True)
    for category in ("statements", "tutorials"):
        for statement in result.get(category, []):
            for kind in ("html", "pdf"):
                item = statement[kind]
                require(item["status"] == "OK", f"{category}/{statement['language']}.{kind} render failed.")
                content = base64.b64decode(item["contentBase64"])
                require(hashlib.sha256(content).hexdigest() == item["sha256"], "Statement render hash differs.")
                (problem.artifacts / f"{category}-{statement['language']}.{kind}").write_bytes(content)
    print("Statement and tutorial HTML/PDF renders saved.", flush=True)


def plan(problem):
    report = verified(problem)
    return {"problem": problem.slug, "name": problem.config["name"], "fingerprint": report["fingerprint"],
            "tests": report["testCount"], "files": [item["name"] for item in problem.config["files"]],
            "solutions": [{"name": item["name"], "tag": item["tag"]} for item in problem.config["solutions"]],
            "codeforcesAccess": "READ", "package": "full, verify=true, linux export", "contestLinking": "not required"}

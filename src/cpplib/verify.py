import hashlib
import json
from pathlib import Path
import sys
import time

from .runner import compile_problem, execute
from .util import Error, read_json, require, utc_now, write_json

CHECKER_CODES = {"OK": 0, "WRONG_ANSWER": 1, "PRESENTATION_ERROR": 2}
VERIFICATION_VERSION = 2
ALLOWED = {"MA": {"OK"}, "OK": {"OK"}, "WA": {"OK", "WRONG_ANSWER"},
           "PE": {"OK", "PRESENTATION_ERROR"}, "RE": {"OK", "RUNTIME_ERROR"},
           "TL": {"OK", "TIME_LIMIT"}, "ML": {"OK", "MEMORY_LIMIT"},
           "RJ": {"OK", "WRONG_ANSWER", "PRESENTATION_ERROR", "RUNTIME_ERROR", "TIME_LIMIT", "MEMORY_LIMIT", "OUTPUT_LIMIT"},
           "TO": {"OK", "TIME_LIMIT"}, "TM": {"OK", "TIME_LIMIT", "MEMORY_LIMIT"}}


def success(execution, what):
    require(execution.returncode == 0 and execution.termination is None,
            f"{what} failed: {execution.termination or execution.returncode}: "
            f"{execution.stderr.decode(errors='replace')[-1500:]}")


class Judge:
    def __init__(self, problem, programs):
        self.problem = problem
        self.programs = programs
        self.validator = programs[problem.config["assets"]["validator"]]
        self.checker = programs[problem.config["assets"]["checker"]]
        self.work = problem.build / "judge"
        self.work.mkdir(parents=True, exist_ok=True)

    def validate(self, data, label):
        result = execute([self.validator], data, cwd=self.problem.path, timeout=5)
        success(result, f"Validator on {label}")

    def check(self, data, answer, output):
        for name, content in (("input", data), ("answer", answer), ("output", output)):
            (self.work / name).write_bytes(content)
        result = execute([self.checker, self.work / "input", self.work / "output", self.work / "answer"],
                         cwd=self.problem.path, timeout=5)
        require(not result.termination and result.returncode in (0, 1, 2),
                f"Checker failed: {result.stderr.decode(errors='replace')[-1500:]}")
        return {0: "OK", 1: "WRONG_ANSWER", 2: "PRESENTATION_ERROR"}[result.returncode]

    def solution(self, entry, data):
        info = self.problem.config["info"]
        result = execute([self.programs[entry["name"]]], data, cwd=self.problem.path,
                         timeout=info["timeLimit"] / 1000 + 0.05, memory_mib=info["memoryLimit"])
        verdict = result.termination or ("RUNTIME_ERROR" if result.returncode else None)
        return result, verdict

    def oracle(self, data):
        path = self.problem.file(self.problem.config["verification"]["oracle"])
        result = execute([sys.executable, path], data, cwd=self.problem.path, timeout=10, memory_mib=512)
        success(result, "Independent oracle")
        return result.stdout


def self_tests(problem, judge):
    for case in problem.fixtures("validator"):
        result = execute([judge.validator], case["input"].encode(), cwd=problem.path, timeout=5)
        require(not result.termination and result.returncode in (0, 3), f"Validator crashed in {case['name']}.")
        actual = "VALID" if result.returncode == 0 else "INVALID"
        require(actual == case["verdict"], f"Validator self-test failed: {case['name']} ({actual}).")
    for case in problem.fixtures("checker"):
        verdict = judge.check(case["input"].encode(), case["answer"].encode(), case["output"].encode())
        require(verdict == case["verdict"], f"Checker self-test failed: {case['name']} ({verdict}).")


def generate_inputs(problem, programs, judge):
    manual, commands = problem.recipe()
    inputs = {case["index"]: problem.file(case["input"]).read_bytes() for case in manual}
    for index, tokens in commands:
        command = [programs[tokens[0]], *tokens[1:]]
        first = execute(command, cwd=problem.path, timeout=10, memory_mib=512)
        second = execute(command, cwd=problem.path, timeout=10, memory_mib=512)
        success(first, f"Generator for test {index}")
        success(second, f"Repeated generator for test {index}")
        require(first.stdout == second.stdout, f"Generator is nondeterministic on test {index}.")
        inputs[index] = first.stdout
    if not problem.config["info"].get("skipDuplicatedTestsValidation", False):
        require(len(set(inputs.values())) == len(inputs), "Duplicate test inputs.")
    directory = problem.build / "tests"
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for index, data in sorted(inputs.items()):
        judge.validate(data, f"test {index}")
        (directory / f"{index:02d}.in").write_bytes(data)
        hashes[str(index)] = hashlib.sha256(data).hexdigest()
    return inputs, hashes


def generate(problem):
    problem.validate()
    programs, compiler = compile_problem(problem)
    judge = Judge(problem, programs)
    self_tests(problem, judge)
    inputs, hashes = generate_inputs(problem, programs, judge)
    report = {"fingerprint": problem.fingerprint(), "testCount": len(inputs), "inputSha256": hashes, "compiler": compiler}
    write_json(problem.build / "generation.json", report)
    print(f"Generated and validated {len(inputs)} unique inputs.", flush=True)
    return report


def stress(problem, programs=None, judge=None):
    problem.validate()
    if programs is None:
        programs, _ = compile_problem(problem)
    judge = judge or Judge(problem, programs)
    generator = problem.file(problem.config["verification"]["stressGenerator"])
    result = execute([sys.executable, generator], cwd=problem.path, timeout=30, memory_mib=512)
    success(result, "Stress generator")
    try:
        cases = json.loads(result.stdout)
    except ValueError:
        raise Error("Stress generator must print a JSON array of input strings.") from None
    require(isinstance(cases, list) and cases and all(isinstance(case, str) for case in cases),
            "Stress generator must produce a nonempty JSON array of inputs.")
    require(len(cases) <= 10000, "Keep stress runs at or below 10000 cases.")
    accepted = [entry for entry in problem.config["solutions"] if entry["tag"] in ("MA", "OK")]
    started = time.monotonic()
    for index, text in enumerate(cases, 1):
        data = text.encode()
        try:
            judge.validate(data, f"stress case {index}")
            oracle = judge.oracle(data)
            for entry in accepted:
                output, failure = judge.solution(entry, data)
                require(failure is None, f"{entry['name']} failed stress case {index}: {failure}.")
                require(judge.check(data, oracle, output.stdout) == "OK",
                        f"{entry['name']} disagrees with oracle on stress case {index}.")
        except Error:
            witness = problem.build / "failure-stress.in"
            witness.write_bytes(data)
            print(f"Failure witness: {witness}", flush=True)
            raise
    report = {"passed": True, "fingerprint": problem.fingerprint(), "cases": len(cases),
              "wallSeconds": round(time.monotonic() - started, 3), "completedAt": utc_now()}
    write_json(problem.build / "stress.json", report)
    print(f"Stress passed: {len(cases)} cases against the independent oracle.", flush=True)
    return report


def verify(problem):
    started = time.monotonic()
    problem.validate()
    fingerprint = problem.fingerprint()
    programs, compiler = compile_problem(problem)
    judge = Judge(problem, programs)
    self_tests(problem, judge)
    inputs, hashes = generate_inputs(problem, programs, judge)
    entries = problem.config["solutions"]
    main = next(entry for entry in entries if entry["tag"] == "MA")
    runs = {entry["name"]: [] for entry in entries if entry["tag"] != "NR"}
    witnesses = {entry["name"]: [] for entry in entries if entry["tag"] not in ("MA", "OK", "NR", "TO")}
    answer_hashes = {}
    for index, data in sorted(inputs.items()):
        oracle = judge.oracle(data)
        answer, failure = judge.solution(main, data)
        require(failure is None and judge.check(data, oracle, answer.stdout) == "OK", f"Main solution failed test {index}.")
        (problem.build / "tests" / f"{index:02d}.ans").write_bytes(answer.stdout)
        answer_hashes[str(index)] = hashlib.sha256(answer.stdout).hexdigest()
        for entry in entries:
            if entry["tag"] == "NR":
                continue
            result, failure = (answer, None) if entry["tag"] == "MA" else judge.solution(entry, data)
            verdict = failure or judge.check(data, answer.stdout, result.stdout)
            require(verdict in ALLOWED[entry["tag"]],
                    f"{entry['name']} tagged {entry['tag']} returned {verdict} on test {index}.")
            if entry["tag"] in ("MA", "OK"):
                require(judge.check(data, oracle, result.stdout) == "OK", f"{entry['name']} disagrees with oracle.")
            if entry["name"] in witnesses and verdict != "OK":
                witnesses[entry["name"]].append(index)
            runs[entry["name"]].append({"test": index, "verdict": verdict, **result.metrics()})
    for name, indices in witnesses.items():
        require(indices, f"Rejected solution {name} survived every test.")
    for manual in problem.config["testsets"]["tests"].get("manualTests", []):
        expected = problem.file(manual["output"]).read_bytes()
        actual = (problem.build / "tests" / f"{manual['index']:02d}.ans").read_bytes()
        require(judge.check(inputs[manual["index"]], expected, actual) == "OK", f"Sample {manual['index']} answer differs.")
    stress_report = stress(problem, programs, judge)
    require(problem.fingerprint() == fingerprint, "Source changed during verification; run verify again.")
    report = {"passed": True, "verificationVersion": VERIFICATION_VERSION,
              "fingerprint": fingerprint, "testCount": len(inputs), "compiler": compiler,
              "rssMeasurement": "GNU time child peak RSS; null when unavailable or killed before measurement",
              "completedAt": utc_now(), "wallSeconds": round(time.monotonic() - started, 3),
              "validatorSelfTests": len(problem.fixtures("validator")), "checkerSelfTests": len(problem.fixtures("checker")),
              "stressCases": stress_report["cases"], "inputSha256": hashes, "answerSha256": answer_hashes,
              "wrongSolutionsRejectedOn": witnesses, "solutions": runs}
    write_json(problem.build / "verification.json", report)
    print(f"PASS {problem.slug}: {len(inputs)} tests, {stress_report['cases']} stress cases, all solution tags verified "
          f"in {report['wallSeconds']}s.", flush=True)
    return report


def verified(problem):
    problem.validate()
    path = problem.build / "verification.json"
    require(path.is_file(), "Run verify before upload.")
    report = read_json(path)
    require(report.get("passed") and report.get("verificationVersion") == VERIFICATION_VERSION
            and report.get("fingerprint") == problem.fingerprint(),
            "Verification is missing or stale. Run verify again.")
    for kind, suffix in (("inputSha256", "in"), ("answerSha256", "ans")):
        for index, expected in report[kind].items():
            path = problem.build / "tests" / f"{int(index):02d}.{suffix}"
            require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                    f"Generated test {index}.{suffix} changed; run verify again.")
    return report

import hashlib
import re
import shlex
from pathlib import Path
import tomllib

from .util import Error, digest, read_json, require

TAGS = {"MA", "OK", "WA", "PE", "RE", "TL", "ML", "RJ", "NR", "TO", "TM"}
TEXT_FIELDS = {"legend", "input", "output", "notes", "tutorial", "scoring", "interaction"}
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


class Problem:
    def __init__(self, root, slug):
        self.root = Path(root).resolve()
        self.path = (self.root / "problems" / slug).resolve()
        require(self.path.parent == self.root / "problems", "Use a problem slug, not an external path.")
        self.slug = self.path.name
        self.build = self.path / "build"
        self.artifacts = self.path / "artifacts"
        self.state_path = self.path / "polygon-state.json"
        try:
            self.config = tomllib.loads((self.path / "problem.toml").read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise Error(f"Cannot load {self.slug}/problem.toml: {error}") from None

    def file(self, name):
        path = (self.path / name).resolve()
        require(path.is_relative_to(self.root), f"Asset path escapes the repository: {name}")
        require(path.is_file(), f"Missing asset: {self.slug}/{name}")
        return path

    def text(self, name):
        try:
            return self.file(name).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise Error(f"Text asset is not UTF-8: {name}") from None

    def fixtures(self, asset, remote=False):
        cases = read_json(self.file(self.config["selfTests"][asset]))
        require(isinstance(cases, list) and cases, f"Write nonempty {asset} self-test fixtures.")
        return [case for case in cases if not remote or case.get("polygon", True)]

    def recipe(self):
        settings = self.config["testsets"]["tests"]
        sources = {Path(file["name"]).stem for file in self.config["files"] if file["type"] == "source"}
        manual = settings.get("manualTests", [])
        indices = [case["index"] for case in manual]
        commands = []
        for number, line in enumerate(self.text(settings["script"]).splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            tokens = shlex.split(line)
            require(len(tokens) >= 4 and tokens[-2] == ">" and tokens[-1].isdigit(),
                    f"doall.txt:{number}: supported syntax is 'generator arguments > numeric-index'.")
            require(tokens[0] in sources, f"doall.txt:{number}: unknown generator {tokens[0]}.")
            require(not any(token in (";", "|", "&&", "||", "<", ">") for token in tokens[:-2]),
                    "Shell syntax is not supported in test recipes.")
            index = int(tokens[-1])
            indices.append(index)
            commands.append((index, tokens[:-2]))
        require(indices and all(isinstance(index, int) and index > 0 for index in indices), "Invalid test indices.")
        require(len(set(indices)) == len(indices), "Duplicate test indices.")
        require(sorted(indices) == list(range(1, len(indices) + 1)), "Test indices must be contiguous, starting at 1.")
        return manual, commands

    def validate(self):
        c = self.config
        require(c.get("schemaVersion") == 1, "Unsupported schemaVersion.")
        require(not c.get("draft", False), "Scaffold is a draft. Complete its files, then set draft = false.")
        require(SAFE_NAME.fullmatch(c.get("name", "")), "Invalid remote problem name.")
        require(c.get("description") and c.get("created"), "Add description and ISO creation date to problem.toml.")
        import datetime
        try:
            datetime.date.fromisoformat(str(c["created"]))
        except ValueError:
            raise Error("created must use YYYY-MM-DD.") from None
        require(c.get("tags") and all(isinstance(tag, str) for tag in c["tags"]), "Declare problem tags.")
        info = c.get("info", {})
        require(info.get("interactive") is False, "Only standard batch problems are currently supported.")
        require(info.get("inputFile") == "stdin" and info.get("outputFile") == "stdout", "Use stdin/stdout.")
        require(250 <= info.get("timeLimit", 0) <= 15000 and info["timeLimit"] % 50 == 0, "Invalid Polygon time limit.")
        require(4 <= info.get("memoryLimit", 0) <= 1024, "Invalid Polygon memory limit.")
        require(set(c.get("testsets", {})) == {"tests"}, "Only the default 'tests' testset is supported.")
        all_names = []
        for file in c.get("files", []):
            require(file["type"] in ("resource", "source", "aux"), "Unknown file type.")
            require(SAFE_NAME.fullmatch(file["name"]), "Unsafe remote asset filename.")
            self.file(file["path"])
            if file["type"] == "source":
                require(file.get("sourceType") == "cpp.g++17", "Executable assets currently require cpp.g++17.")
            all_names.append(file["name"].casefold())
        solutions = c.get("solutions", [])
        require(sum(solution["tag"] == "MA" for solution in solutions) == 1, "Declare exactly one MA solution.")
        require(any(solution["tag"] == "OK" for solution in solutions), "Declare an independent OK solution.")
        require(any(solution["tag"] in ("WA", "PE", "RE", "TL", "ML", "RJ") for solution in solutions),
                "Declare at least one intentionally rejected solution.")
        for solution in solutions:
            require(solution["tag"] in TAGS, f"Unsupported solution tag: {solution['tag']}")
            require(solution.get("sourceType") == "cpp.g++17", "Uploaded solutions currently require cpp.g++17.")
            self.file(solution["path"])
            all_names.append(solution["name"].casefold())
        require(len(all_names) == len(set(all_names)), "Remote filenames collide.")
        stems = [Path(item["name"]).stem for item in c["files"] if item["type"] == "source"]
        stems += [Path(item["name"]).stem for item in solutions]
        require(len(stems) == len(set(stems)), "Executable names collide after removing extensions.")
        for role in ("validator", "checker"):
            require(any(file["type"] == "source" and file["name"] == c["assets"][role] for file in c["files"]),
                    f"Unknown {role} source.")
            cases = self.fixtures(role)
            required = {"VALID", "INVALID"} if role == "validator" else {"OK", "WRONG_ANSWER"}
            require(required <= {case["verdict"] for case in cases}, f"{role} fixtures need positive and negative cases.")
            for case in cases:
                require(isinstance(case.get("input"), str), "Fixture input must be a string.")
                if role == "checker":
                    require(isinstance(case.get("answer"), str) and isinstance(case.get("output"), str),
                            "Checker fixture answer/output must be strings.")
                if case.get("polygon", True):
                    fields = ("input",) if role == "validator" else ("input", "answer", "output")
                    require(all(case[field] for field in fields),
                            "Empty Polygon fixture fields are unsupported; mark the case polygon=false and retain it locally.")
        require(c.get("statements"), "Write a statement.")
        for language, statement in c["statements"].items():
            require(language and statement.get("name"), "Statement language/title are required.")
            for key in ("legend", "input", "output", "tutorial"):
                require(self.text(statement[key]).strip(), f"Write statement field {language}.{key}.")
            for key in TEXT_FIELDS & statement.keys():
                self.file(statement[key])
                require("CPPL_TEMPLATE_UNFINISHED" not in self.text(statement[key]),
                        f"Complete statement field {language}.{key}.")
        manual, commands = self.recipe()
        require(any(case.get("useInStatements") for case in manual), "Provide at least one statement sample.")
        for case in manual:
            self.file(case["input"])
            self.file(case["output"])
        verification = c.get("verification", {})
        for field in ("oracle", "stressGenerator"):
            require(field in verification, f"Declare verification.{field}.")
            require(self.file(verification[field]).suffix == ".py", f"{field} currently requires a Python script.")
        require(self.text("review.md").strip(), "Write review.md with the contract, proof, independent oracle and coverage.")
        require("CPPL_TEMPLATE_UNFINISHED" not in self.text("review.md"), "Complete review.md.")
        return {"slug": self.slug, "testCount": len(manual) + len(commands), "files": len(c["files"]),
                "solutions": len(solutions)}

    def fingerprint(self):
        paths = {self.path / "problem.toml"}
        c = self.config
        paths.update(self.file(item["path"]) for item in c["files"] + c["solutions"])
        paths.update(self.file(value) for statement in c["statements"].values()
                     for key, value in statement.items() if key in TEXT_FIELDS)
        paths.add(self.file(c["testsets"]["tests"]["script"]))
        for manual in c["testsets"]["tests"].get("manualTests", []):
            paths.update((self.file(manual["input"]), self.file(manual["output"])))
        paths.update(self.file(value) for value in c["selfTests"].values())
        paths.update(self.file(c["verification"][key]) for key in ("oracle", "stressGenerator"))
        return digest({str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in sorted(paths)})

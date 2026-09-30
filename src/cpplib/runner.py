"""Process limits and per-process measurements; this is not an OS security sandbox."""

import dataclasses
import hashlib
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

from .util import Error, digest, read_json, require, write_json


@dataclasses.dataclass
class Execution:
    stdout: bytes
    stderr: bytes
    returncode: int
    wall_seconds: float
    cpu_seconds: float | None
    max_rss_kib: int | None
    termination: str | None

    def metrics(self):
        return {"wallSeconds": round(self.wall_seconds, 6), "cpuSeconds": self.cpu_seconds,
                "maxRssKiB": self.max_rss_kib, "returncode": self.returncode,
                "termination": self.termination}


def execute(command, data=b"", *, cwd=None, timeout=5, memory_mib=256, output_mib=16):
    import resource
    cap = output_mib * 1024 * 1024
    environment = {key: value for key, value in os.environ.items()
                   if key not in ("POLYGON_API_KEY", "POLYGON_API_SECRET", "CPPL_CONFIG")}

    def limits():
        os.setsid()
        if memory_mib:
            memory = memory_mib * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (cap, cap))
        seconds = max(1, math.ceil(timeout))
        resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds + 1))

    start = time.monotonic()
    with tempfile.TemporaryFile() as input_file, tempfile.TemporaryFile() as output_file, tempfile.TemporaryFile() as error_file, \
            tempfile.NamedTemporaryFile() as rss_file:
        input_file.write(data)
        input_file.seek(0)
        # wait4's ru_maxrss retains the Python parent's pre-exec fork footprint.
        # GNU time measures its own child, after the small native launcher exec.
        timer = shutil.which("time")
        launched = ([timer, "-q", "-o", rss_file.name, "-f", "%M", "--"] if timer else []) + list(command)
        try:
            process = subprocess.Popen([str(item) for item in launched], stdin=input_file,
                                       stdout=output_file, stderr=error_file, cwd=cwd,
                                       env=environment, preexec_fn=limits)
        except OSError as error:
            raise Error(f"Cannot start {command[0]}: {error}") from None
        termination = None
        while True:
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start > timeout:
                termination = "TIME_LIMIT"
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, status, usage = os.wait4(process.pid, 0)
                break
            time.sleep(0.002)
        process.returncode = os.waitstatus_to_exitcode(status)
        elapsed = time.monotonic() - start
        output_file.seek(0)
        error_file.seek(0)
        stdout = output_file.read(cap + 1)
        stderr = error_file.read(cap + 1)
        if process.returncode in (-signal.SIGXCPU, 128 + signal.SIGXCPU):
            termination = "TIME_LIMIT"
        elif process.returncode in (-signal.SIGXFSZ, 128 + signal.SIGXFSZ) or len(stdout) > cap or len(stderr) > cap \
                or (process.returncode and (len(stdout) >= cap or len(stderr) >= cap)):
            termination = "OUTPUT_LIMIT"
        measured = Path(rss_file.name).read_text().strip()
        rss = int(measured) if measured.isdigit() else None
        if not termination and process.returncode and memory_mib and (b"bad_alloc" in stderr or b"MemoryError" in stderr
              or b"Cannot allocate memory" in stderr or (rss is not None and rss >= memory_mib * 1024 * 0.98)):
            termination = "MEMORY_LIMIT"
        return Execution(stdout[:cap], stderr[:cap], process.returncode, elapsed,
                         round(usage.ru_utime + usage.ru_stime, 6), rss, termination)


def compile_problem(problem):
    require(shutil.which("g++"), "Install g++ with C++17 support.")
    version = subprocess.run(["g++", "--version"], capture_output=True, check=True).stdout.decode().splitlines()[0]
    directory = problem.build / "bin"
    includes = problem.build / "include"
    directory.mkdir(parents=True, exist_ok=True)
    includes.mkdir(parents=True, exist_ok=True)
    resources = {}
    for item in problem.config["files"]:
        if item["type"] == "resource":
            data = problem.file(item["path"]).read_bytes()
            (includes / item["name"]).write_bytes(data)
            resources[item["name"]] = hashlib.sha256(data).hexdigest()
    programs = {}
    compiled = 0
    entries = [item for item in problem.config["files"] if item["type"] == "source"] + problem.config["solutions"]
    for item in entries:
        source = problem.file(item["path"])
        target = directory / Path(item["name"]).stem
        cache = target.with_suffix(".json")
        fingerprint = digest({"source": source.read_text(), "resources": resources, "compiler": version,
                              "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra"]})
        if not (target.exists() and cache.exists() and read_json(cache).get("fingerprint") == fingerprint):
            result = execute(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-I", includes,
                              source, "-o", target], cwd=problem.path, timeout=90, memory_mib=0)
            (directory / (item["name"] + ".log")).write_bytes(result.stderr)
            require(result.returncode == 0 and not result.termination,
                    f"Compilation failed for {item['name']}: {result.stderr.decode(errors='replace')[-2000:]}")
            write_json(cache, {"fingerprint": fingerprint, "compiler": version})
            compiled += 1
        programs[item["name"]] = target
        programs[target.name] = target
    print(f"Compiled {compiled} programs; reused {len(entries) - compiled}; {version}.", flush=True)
    return programs, version

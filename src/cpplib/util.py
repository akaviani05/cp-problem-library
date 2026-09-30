import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path


class Error(Exception):
    """A concise, user-facing failure."""


def require(condition, message):
    if not condition:
        raise Error(message)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Error(f"Cannot read JSON: {path}: {error}") from None


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def today():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()


def repository(start=None):
    start = Path(start or os.getcwd()).resolve()
    for path in (start, *start.parents):
        if (path / "pyproject.toml").is_file() and (path / "templates" / "plain").is_dir():
            return path
    raise Error("Run cppl inside a clone of cp-problem-library (or pass --root).")


def normalize(value):
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return value.replace("\r\n", "\n")


@contextlib.contextmanager
def problem_lock(problem):
    path = problem.build / ".lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        try:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Error(f"Another command is working on {problem.slug}.") from None
        except ImportError:
            raise Error("Process locking currently requires Linux or macOS.") from None
        yield

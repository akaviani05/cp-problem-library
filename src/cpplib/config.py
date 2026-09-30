import getpass
import json
import os
from pathlib import Path
import tomllib

from .util import Error, require


def load_config(root):
    path = Path(os.environ.get("CPPL_CONFIG", root / "config.toml"))
    data = {}
    if path.exists():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            raise Error("Cannot parse local config.toml; never paste its credential values into logs.") from None
    section = data.get("polygon", {})
    section["api_key"] = os.environ.get("POLYGON_API_KEY", section.get("api_key", ""))
    section["api_secret"] = os.environ.get("POLYGON_API_SECRET", section.get("api_secret", ""))
    section.setdefault("contest_id", 0)
    section.setdefault("owner", "")
    section.setdefault("problem_prefix", "cp-library-")
    section.setdefault("poll_seconds", 10)
    section.setdefault("build_timeout_seconds", 600)
    require(isinstance(section["contest_id"], int) and section["contest_id"] >= 0,
            "polygon.contest_id must be a nonnegative integer.")
    require(1 <= section["poll_seconds"] <= 60, "polygon.poll_seconds must be between 1 and 60.")
    return section


def init_config(root, contest_id=0, owner="", force=False):
    path = root / "config.toml"
    require(force or not path.exists(), "config.toml already exists; edit it locally or use --force.")
    key = os.environ.get("POLYGON_API_KEY") or getpass.getpass("Polygon API key (stored only in ignored config.toml): ")
    secret = os.environ.get("POLYGON_API_SECRET") or getpass.getpass("Polygon API secret: ")
    require(key and secret, "Both credentials are required.")
    text = "# Local credentials. Ignored by Git; do not paste this file into chat.\n[polygon]\n"
    text += f"api_key = {json.dumps(key)}\napi_secret = {json.dumps(secret)}\n"
    text += f"owner = {json.dumps(owner)}\ncontest_id = {contest_id}\n"
    text += 'problem_prefix = "cp-library-"\n'
    text += 'poll_seconds = 10\nbuild_timeout_seconds = 600\n'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(text)
    path.chmod(0o600)
    print(f"Saved private config.toml; target contest {contest_id or 'not configured'}.")

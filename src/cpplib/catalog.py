import json
import re
from pathlib import Path
import shutil
import tomllib

from .config import load_config
from .util import require, today

START = "<!-- cppl:problems:start -->"
END = "<!-- cppl:problems:end -->"


def refresh_catalog(root):
    rows = []
    for directory in sorted((root / "problems").iterdir()):
        manifest = directory / "problem.toml"
        if not manifest.is_file():
            continue
        config = tomllib.loads(manifest.read_text(encoding="utf-8"))
        if config.get("draft", False):
            continue
        clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
        title = config.get("statements", {}).get("english", {}).get("name", directory.name)
        problem = f"[{clean(title)}](problems/{directory.name}/problem.toml)"
        state = directory / "polygon-state.json"
        if state.is_file():
            remote = json.loads(state.read_text(encoding="utf-8"))
            if remote.get("id"):
                problem += f" · [Polygon](https://polygon.codeforces.com/problem?problemId={remote['id']})"
        rows.append(f"| {problem} | {clean(config.get('description', ''))} | "
                    f"{clean(', '.join(config.get('tags', [])))} | {clean(config.get('created', ''))} |")
    table = "| Problem | Short description | Tags | Created |\n| --- | --- | --- | --- |\n" + "\n".join(rows)
    readme = root / "README.md"
    content = readme.read_text(encoding="utf-8")
    require(content.count(START) == content.count(END) == 1, "README needs exactly one cppl problem-table marker pair.")
    content = content[:content.index(START) + len(START)] + "\n" + table + "\n" + content[content.index(END):]
    readme.write_text(content, encoding="utf-8")
    print(f"Updated README problem table: {len(rows)} completed problems.", flush=True)


def new_problem(root, slug, title, description, tags, template="plain"):
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), "Use a lowercase hyphenated slug.")
    require(template == "plain", "Only the plain template is installed.")
    destination = root / "problems" / slug
    require(not destination.exists(), f"Problem {slug} already exists.")
    prefix = load_config(root)["problem_prefix"]
    require(re.fullmatch(r"[a-z0-9-]*", prefix), "problem_prefix must contain lowercase letters, digits, and hyphens.")
    shutil.copytree(root / "templates" / template, destination)
    replacements = {'"__NAME__"': json.dumps(prefix + slug), '"__TITLE__"': json.dumps(title),
                    '"__DESCRIPTION__"': json.dumps(description), '"__DATE__"': json.dumps(today()),
                    '["__TAGS__"]': json.dumps([tag.strip() for tag in tags.split(",") if tag.strip()])}
    manifest = destination / "problem.toml"
    text = manifest.read_text(encoding="utf-8")
    for token, value in replacements.items():
        text = text.replace(token, value)
    manifest.write_text(text, encoding="utf-8")
    print(f"Created {destination}; edit draft assets using docs/agents/problem.md.", flush=True)

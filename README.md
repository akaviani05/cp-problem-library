# CP problem library

Turn an informal competitive programming idea into a tested Codeforces Polygon
problem. Open this folder in Codex and describe the problem, or use the `cppl`
CLI directly. Each problem keeps its statement, generators, validator, checker,
solutions, and test recipes together under `problems/<slug>/`.

The CLI verifies everything locally, uploads through Polygon's official API,
builds a full verified package, and downloads the official Linux ZIP with every
test input and answer checked against the local data. It also grants the
`codeforces` user READ access for Codeforces import.

## Set up

You need Python 3.11+, `g++` with C++17 support, and Linux (or WSL).
There are no third-party Python runtime dependencies.

```bash
git clone https://github.com/akaviani05/cp-problem-library.git
cd cp-problem-library
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/cppl doctor
```

Configure Polygon once using hidden prompts:

```bash
.venv/bin/cppl config init --owner YOUR_POLYGON_LOGIN
```

This creates a Git-ignored `config.toml` with private file permissions. See
[config.example.toml](config.example.toml) for the available options. You can
also supply `POLYGON_API_KEY` and `POLYGON_API_SECRET` through the environment.
Offline creation and verification work without credentials.

New Polygon names start with `cp-library-`. Change `polygon.problem_prefix` in
your local config to use another prefix. `contest_id` is optional: the documented
API does not provide contest insertion, so add problems to a contest manually
if needed. Prefix grouping and publication work independently of a contest.

## Ask Codex to create a problem

Open this repository in Codex and say, for example:

> Create a Polygon-ready problem: given an unweighted tree and vertices s and t,
> find their distance. Use one query and at most 200,000 vertices.

[AGENTS.md](AGENTS.md) routes the agent into a focused authoring workflow. It
chooses or clarifies the contract, writes independent references, exercises
adversarial cases, verifies the problem, publishes it, checks the official
package, and updates the table below. Ask for an **offline draft** if you want
local files and verification only.

Agents improving the CLI or templates use a separate project-development guide.
The problem guide contains the file list and testlib snippets, so authoring
agents do not need to read the tool implementation or other problems.

## Use the CLI yourself

```bash
.venv/bin/cppl new my-problem --title 'My Problem' \
  --description 'A short description' --tags 'implementation'
# Complete the files in problems/my-problem and set draft = false.
.venv/bin/cppl verify my-problem
.venv/bin/cppl inspect my-problem
.venv/bin/cppl plan my-problem
.venv/bin/cppl publish my-problem
.venv/bin/cppl status my-problem
```

The [plain template](templates/plain) includes a seeded generator scaffold,
strict validator scaffold, a working whitespace-ignoring token checker, accepted
and rejected solution slots, statement fragments, sample folders, and fixture
formats. It stays a draft until you complete the problem-specific parts.

`verify` checks validator/checker fixtures, generator determinism, all generated
inputs, samples, accepted solutions against an independent oracle, intentionally
wrong solutions, and small-case stress tests. It records time, memory, and hashes
under the ignored `build/` folder. Authored programs are executable code; the
process limits are not a security sandbox.

`publish` reuses current verification, reads uploaded assets back, commits,
waits for a full verified package, checks package revision and cautions, exports
the ZIP, and saves statement/tutorial renders under `artifacts/`. If interrupted,
rerun it: the stored remote identity and upload baseline support recovery while
protecting conflicting remote changes. Exported ZIPs and local credentials are
not committed to Git.

For separate stages, use `generate`, `stress`, `upload`, `build`, `export`,
`render`, or `prepare-import`. See [CLI and schema details](docs/cli.md),
[architecture](docs/architecture.md), and [agent evaluation](docs/agent-benchmarks.md).
The [A+B pilot record](docs/pilot.md) documents the original API experiment.

## Created problems

This table is maintained from problem metadata by `cppl catalog`.

<!-- cppl:problems:start -->
| Problem | Short description | Tags | Created |
| --- | --- | --- | --- |
| [A Minus B](problems/a-minus-b/problem.toml) · [Polygon](https://polygon.codeforces.com/problem?problemId=592590) | Compute the difference of two signed integers. | implementation, math | 2026-09-30 |
| [A + B](problems/a-plus-b/problem.toml) · [Polygon](https://polygon.codeforces.com/problem?problemId=592542) | Add two signed integers, with 64-bit boundary tests. | implementation, math | 2026-09-30 |
| [Tree Distance](problems/tree-distance/problem.toml) · [Polygon](https://polygon.codeforces.com/problem?problemId=592594) | Find the number of edges on the unique path between two vertices of an unweighted tree. | trees, dfs and similar, shortest paths | 2026-09-30 |
<!-- cppl:problems:end -->

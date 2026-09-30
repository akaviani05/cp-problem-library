# Project development: focused onboarding

Read this guide and run `rtk proxy .venv/bin/cppl doctor`. Read only the module
and tests relevant to the requested change. Use `docs/cli.md` for command/schema
contracts; use historical `docs/pilot.md` only for a specific Polygon behavior.

| Change | Start here |
| --- | --- |
| Command behavior/setup | `src/cpplib/cli.py`, `pyproject.toml` |
| Manifest/schema/new templates | `src/cpplib/model.py`, `src/cpplib/catalog.py`, `templates/plain/problem.toml` |
| Local judging/performance | `src/cpplib/runner.py`, `src/cpplib/verify.py` |
| Credentials/config | `src/cpplib/config.py`, `config.example.toml`; never read real config |
| Signed API transport | `src/cpplib/polygon.py`; consult only the relevant official API section |
| Upload/recovery/export | `src/cpplib/sync.py`, targeted recovery/export tests |
| Agent onboarding | `AGENTS.md`, the specific mode guide |
| README table | `src/cpplib/catalog.py`, generated marker block at the end of README |

Commands use stdlib Python 3.11+ and the installed C++17 compiler. The process
runner targets POSIX systems; Windows users should use WSL. Keep offline checks
network-free. Do not add a Python dependency for a small stdlib operation.

Run `rtk proxy .venv/bin/python -m unittest discover -s tests -v` for tool
behavior changes. Choose meaningful tests for the changed contract: source
freshness, signed multiline values, memory/time/output handling, unexpected
checker exits, interrupted writes, creation recovery, working-copy conflicts,
package revision/content matching, and README preservation. Do not write tests
that merely restate implementation for low-impact wording edits.

Use `cppl verify a-plus-b` as an end-to-end offline check only when changing
execution, generation, model, or verification behavior. Compile caching should
avoid unrelated recompiles. Use mocked transport for mutation failure tests;
live publication belongs to an explicitly requested live experiment, not a
unit test. The user has authorized live A−B and tree-distance experiments in
this task, including upload and Codeforces READ access.

Never put credentials or signed requests in fixtures, exceptions, or logs.
`config.toml` and per-problem build/artifact/state files must remain ignored.
Do not silently retry creation, overwrite a modified remote working copy,
remove remote assets, or grant unrelated access. Preserve user changes in the
shared checkout. A compiler timeout/limit is not a security sandbox.

When adding a feature, update the focused CLI/schema documentation and relevant
mode guide. Keep root AGENTS.md a small dispatcher; do not stuff implementation
or historical API documentation into every problem agent's context. Keep the
README user-friendly and its final problem-table markers intact. Record changed
behavior, verification, and any material limitation in the final response.

# Entry point for agents

This workspace has two modes. Select the mode from the user's request before
reading implementation files.

- **Create or edit a CP problem:** read **only** `docs/agents/problem.md` next.
  Work in `problems/<slug>/`; use the CLI, not private Polygon API scripts.
- **Improve the project, CLI, templates, or harness:** read
  **only** `docs/agents/project.md` next, then the modules relevant to the change.
- If a request contains both, finish the tool change and its checks before
  using the updated problem workflow. Preserve already authorized scope.

Use `rtk proxy <command>` for agent shell commands when RTK is installed. In
this user's environment, all shell commands must have the RTK prefix. Use `rg`
for focused discovery. Batch independent reads, but keep edits and dependent
commands sequential.

## Context budget

Do not read all problems, the vendored `include/testlib.h`, historical pilot
logs, downloaded packages, or `docs/architecture.md` to onboard. The mode guide
contains the precise files, commands, and API snippets needed. Read further
only to resolve a concrete failure, and use a targeted line or symbol search.

Never read, print, copy into a prompt, or commit `config.toml`, `.env`, or
`.polygon/` session data. Use `cppl doctor` to check credentials without viewing
them. Credentials are read by the CLI. Do not pass them to subagents.

## Shared invariants

- `include/testlib.h` is pinned and unmodified. Extend `testlib_ext.h` only in
  project mode, with a concrete need and suitable validation.
- Offline commands must not need credentials or network. Uploads require fresh
  verification and must preserve conflicting remote user changes.
- `codeforces` must have READ access (retain stronger existing access) so ready
  packages can be imported. `publish` handles this and verifies it.
- Problem names use the configurable `polygon.problem_prefix`; default
  `cp-library-`. Contest linking is optional and currently manual.
- Update the generated problem table at the end of README using `cppl catalog`.
  Never replace manually written README content to add a row.
- Do not invent successful checks, remote IDs, benchmark numbers, or token
  counts. Report measured evidence and distinguish estimates.

Keep commentary concise and give a meaningful update at least once a minute.
Complete the authorized workflow, then report links, verification, and any
remaining material limitation. Do not stop at a plan or unfinished scaffold.

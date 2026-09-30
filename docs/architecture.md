# Problem architecture, version 1

Status: implemented version 1, validated against live Polygon packages.

## Compatibility boundary

Polygon's HTTP API operates on individual assets and working copies. It does
not prescribe a Git folder layout or offer a documented method to ingest an
arbitrary source ZIP. Our authoring layout therefore describes those assets
explicitly and maps them to API calls. A distributable Polygon package is a
separate artifact: Polygon generates its `problem.xml`, tests, answers,
statements, and supporting files. For the pilot we download and inspect that
official package instead of inventing an XML schema.

The source of truth is the version-controlled authoring folder. Generated
inputs, answers, binaries, verification logs, rendered statements, and downloaded
packages are derived artifacts. They must be reproducible and are ignored by Git.

## Repository layout

```text
README.md
AGENTS.md                       Mode dispatcher with focused onboarding
docs/
include/
  testlib.h                     Unmodified, pinned upstream dependency
  testlib_ext.h                 Small project helpers, includes testlib.h
third_party/testlib/
  LICENSE
  provenance.json               Exact upstream commit and header digest
templates/plain/                Batch scaffold with whitespace token checker
src/cpplib/                     Installable CLI and verification/API implementation
tests/                          Offline behavioral tests with fake API transport
config.example.toml             Public config schema; real config.toml is ignored
tools/pilot.py                  First-milestone experiment only
problems/<slug>/
  problem.toml                  Asset inventory, limits, tags, testset definitions
  statements/<language>/
    legend.tex
    input.tex
    output.tex
    notes.tex
    tutorial.tex
  generators/*.cpp
  validators/*.cpp
  checkers/*.cpp
  solutions/*
  resources/*                   Optional additional compilation resources
  tests/
    doall.txt                   Polygon generation script
    manual/*.in                 Hand-authored inputs, including examples
    manual/*.ans                Expected example outputs
    validator/cases.json        Valid and invalid input fixtures
    checker/cases.json          Input, answer, output, expected verdict fixtures
  build/                        Ignored local compilation and verification
  artifacts/                    Ignored official packages and renders
  polygon-state.json            Ignored account-specific remote identity/state
```

An authoring filename can differ from its remote name. Every uploaded asset has
an explicit `name` in the manifest because Polygon's remote source namespace is
flat. Reject collisions before upload, including resource filenames. Shared
headers are referenced from `include/`; stage them into the remote problem as
resource files so includes do not rely on this repository's directory structure.

Statement `.tex` files are Polygon text fragments, not standalone LaTeX documents.
Example input/output comes from sample tests; do not maintain a second independent
sample definition inside the legend. Language keys follow Polygon naming, e.g.
`english`, rather than assuming an ISO language code.

## Manifest and API mapping

`problem.toml` is our versioned authoring manifest. Its `schemaVersion` is local,
not an API parameter. Names in `info`, statement fields, file `type`/`name`/
`sourceType`, and solution `tag` match the API. Local `path` values and
statement-fragment paths are resolved before sending content.

| Authoring data | API operation |
| --- | --- |
| `name` | `problem.create` |
| `tags` | `problem.saveTags` |
| `info` | `problem.updateInfo` |
| `statements.<language>` | `problem.saveStatement` |
| `files` | `problem.saveFile` |
| `solutions` | `problem.saveSolution` |
| `assets.validator`, `assets.checker` | `problem.setValidator`, `problem.setChecker` |
| `testsets.<name>.manualTests` | `problem.saveTest` |
| `testsets.<name>.script` | `problem.saveScript` |
| `selfTests.validator`, `selfTests.checker` | Validator/checker self-test save methods |
| Verified revision | `problem.commitChanges`, `problem.buildPackage` |
| Official export | `problem.packages`, `problem.package` |

Solution tags are stored verbatim, with exactly one `MA` main solution. The CLI
enforces permitted per-test verdicts and rejection witnesses; the supported
tags and contracts are listed in `docs/cli.md`.

The generator script is the single test recipe. Manually stored tests occupy
explicit indices; generated tests occupy the remaining indices. The CLI
supports single-generator lines with explicit numeric destinations and rejects
unsupported grammar. It never evaluates a script as arbitrary shell text.

## Verification contract

1. Validate the manifest, source inventory, statement constraints, sample
   definitions, remote names, test indices, and supported problem type.
2. Compile all executable assets with pinned language settings. Materialize the
   declared resource dependencies without depending on the current directory.
3. Run validator fixtures and checker fixtures. Invalid-input rejection and
   incorrect-output rejection are prerequisites for trusting later results.
4. Generate deterministic inputs, retain the exact command/seed for each input,
   reject duplicate inputs unless explicitly permitted, and validate every input.
5. Generate answers with the main solution and compare accepted solutions through
   the actual checker. Use an independent oracle and stress or exhaustive tests
   wherever feasible; agreement alone does not establish correctness.
6. Run additional solutions, enforce their declared tags, and require evidence
   that each intentionally wrong solution is detected. Record failure witnesses.
7. Record content hashes, compiler/runtime versions, limits, commands, seeds,
   verdicts, and coverage rationale. An upload is allowed only against the same
   verified contents; source edits invalidate that evidence.

The CLI runs these checks, including independent Python oracles, compilation
caching, per-process CPU/wall/RSS measurements, memory/output limits, and
process-group timeouts. It targets Linux/WSL. This is a trusted-author workflow,
not an OS security sandbox. Uploaded author programs are executable code.

## Upload and export contract

Build a reviewable upload plan from verified data. Store the remote problem ID
immediately after creation. Do not silently select a same-named problem owned
by another user. Do not duplicate creation after a timeout: reconcile remote
state first. Updating an existing problem requires a diff against its working
copy; never discard, overwrite, or delete remote user changes implicitly.

Upload headers, sources, statements, solutions, manual tests, scripts, and
checker/validator tests. Read them back, commit the intended working copy, and
request a full verified package. Check package revision/state and cautions.
Download the Linux package containing generated tests and compare its exact
inputs and answers against the verified local data. A successful upload alone
does not mean the problem is package-ready.

For the Codeforces import workflow, add the user `codeforces` to the problem's
access list with `READ` access and verify the entry using `problem.accesses`.
Use `problem.setAccess` only when access is missing; retain stronger existing
access. This is a required import-preparation step authorized by the user, and
applies to future created problems too. It takes effect immediately outside
the working copy and does not require a commit or a package rebuild.

API calls use signed POST bodies over fixed HTTPS without redirects. Credentials
come from the environment or ignored private config, outside manifests and Git. Logs exclude secrets,
signed requests, and raw exception URLs. Automatic mutation retries are unsafe
unless the operation is proven idempotent or its result has been reconciled.
Keep arbitrary access changes and contest publication outside ordinary asset
sync; the specifically authorized `codeforces` import access is part of upload.

## Agent workflow and extension boundary

The stdlib package `cpplib` exposes `cppl` through `pyproject.toml` and a `.venv`
workflow. Offline commands need no credentials or network. Behavioral tests
cover signing, fixtures, stale verification, process limits, partial writes,
creation recovery, conflicts, package matching, and catalog preservation.

`AGENTS.md` routes authors to `docs/agents/problem.md` and project contributors
to `docs/agents/project.md`. The author guide supplies the precise file list,
minimal testlib API, and proof/coverage/oracle review stages. New authors do not
need this architecture document, the tool implementation, or existing problems
to onboard. Problem agents use `cppl catalog` to update only the README table.

Polygon names use `polygon.problem_prefix`, default `cp-library-`. The optional
contest ID is retained as a local preference; the documented API lacks contest
insertion, so contest linking is manual and never blocks publication.

Interactive, output-only, and scored/grouped problems need separate templates
and execution contracts; the first CLI should clearly identify which are
supported. Do not claim support based only on an available API field.

## References

- [Official Polygon API](https://codeforces.github.io/polygon-misc/API), checked 2026-09-30.
- [Official testlib repository](https://github.com/MikeMirzayanov/testlib), vendored revision in `third_party/testlib/provenance.json`.
- [Codeforces import instructions](https://codeforces.com/blog/entry/10099), requiring read access for the `codeforces` user.

API behavior observed during the pilot takes precedence over untested assumptions
and is recorded separately in `docs/pilot.md`.

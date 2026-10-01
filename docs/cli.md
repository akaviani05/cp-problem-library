# CLI and schema reference

## Setup

Use Python 3.11+ on Linux/WSL with `g++` available:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/cppl doctor
```

Alternatively, `uv venv .venv` followed by
`uv pip install --python .venv/bin/python -e .` installs the same package.
Agent shell commands in this workspace use `rtk proxy` before these commands.
Ordinary users do not need RTK.

`cppl config init --owner LOGIN [--contest ID]` prompts secretly and saves
ignored `config.toml` with mode 0600. The example config documents options.
`CPPL_CONFIG` selects another private config; environment credentials override
file credentials. `doctor` / `config check` show only whether credentials exist.
`problem_prefix` applies to newly scaffolded names. Contest insertion is optional
and manual; the official API only documents contest listing.

## Commands

All problem commands take the folder slug. Run from anywhere inside the checkout
or specify `cppl --root /path/to/repository ...`.

| Command | Behavior |
| --- | --- |
| `new SLUG --title TITLE --description TEXT --tags CSV` | Copy the plain draft template; refuse an existing directory |
| `lint SLUG` | Check supported schema and required assets; no compilation/network |
| `generate SLUG` | Compile, check fixtures, generate twice, validate; save inputs |
| `verify SLUG` | Generate, compare oracle/accepted solutions, check tags/samples, stress; save evidence |
| `stress SLUG` | Run only the configured small-case oracle comparison |
| `inspect SLUG` | Compact verification, per-solution maximum metrics, and remote identity |
| `plan SLUG` | Require current verification and print local upload summary |
| `upload SLUG` | Reconcile, upload changed assets, read back, commit, verify Codeforces READ access |
| `build SLUG` | Request/wait for a full verified package for the recorded revision |
| `export SLUG` | Download READY Linux ZIP; check XML revision and every input/answer |
| `render SLUG` | Save official statement/tutorial HTML and PDF |
| `publish SLUG` | Verify if needed, upload, build, export, render, catalog |
| `status SLUG [--json]` | Current remote revision, packages, and cautions |
| `prepare-import SLUG` | Grant/verify `codeforces` READ; preserve stronger access |
| `attach SLUG --id ID` | Record a known matching remote identity without changing assets |
| `catalog` | Replace only the marked README problem table |

## Manifest version 1

`templates/plain/problem.toml` is the schema example. Currently supported:
standard batch stdin/stdout problems, C++17 programs, the default `tests` testset,
and literal seeded generator invocations with explicit contiguous test indices.
Interactive, output-only, scoring groups, and additional language runtimes need
separate execution contracts before support is added.

- Root fields: `schemaVersion = 1`, `draft`, Polygon `name`, catalog `description`,
  ISO `created`, `tags`.
- `info`: API-compatible millisecond `timeLimit`, MiB `memoryLimit`,
  `interactive = false`, `inputFile = "stdin"`, `outputFile = "stdout"`.
- `statements.<language>`: title `name`, `encoding`, fragment paths for `legend`,
  `input`, `output`, `notes`, `tutorial`; optional `scoring`, `interaction`.
- `files`: explicit remote `name`, local `path`, `type` (`resource`, `source`,
  `aux`), and source `sourceType = "cpp.g++17"`.
- `solutions`: remote `name`, local `path`, `sourceType`, Polygon `tag`.
  Exactly one `MA`, at least one `OK`, and at least one rejected solution.
- `assets`: remote checker/validator filenames.
- `testsets.tests`: script path and
  `manualTests` with index, input/output paths, description, useInStatements.
- `selfTests`: validator/checker JSON paths.
- `verification`: local Python `oracle` and `stressGenerator` paths.

Test recipe lines are `gen literal-arguments seed > numeric-index`; manual tests
occupy their declared indices. Blank lines and full-line `#` comments are allowed
locally and omitted from the Polygon script; commands are uploaded in test-index
order to match Polygon's readback. No shell execution, loops, `$` destinations, or
automatic numbering. Validator fixtures use VALID/INVALID; checker fixtures use
OK/WRONG_ANSWER/PRESENTATION_ERROR with input, answer, output. Empty API fields
must be marked `"polygon": false` and remain checked locally.

The whitespace checker compares exact tokens; different numeric spellings and
alternative answers require a different checker. `MA`/`OK` must always accept;
WA/PE/RE/TL/ML require a matching failure witness and may accept other tests;
RJ allows any rejection, TO may pass or time out, TM may pass or hit time/memory,
NR compiles but is not judged. See the verifier for any new tag behavior.

Statement uploads match Polygon's punctuation normalization: curly double quotes
become straight quotes, and an em dash becomes TeX `---`. Local source fragments
are preserved. Readback and conflict errors identify differing asset paths
without logging their contents.

## Evidence and recovery

`build/verification.json` records compiler, content fingerprint, test hashes,
fixture counts, stress count, per-run CPU/wall time and peak RSS, and rejecting
test indices. Relevant source/test edits or changed generated bytes invalidate
upload evidence. Limits use Linux resource limits and process-group wall-time
termination; they are not an untrusted-code sandbox.
Peak RSS uses GNU `time` to measure the executed child, excluding inherited
Python-runner memory. RSS is null when GNU time is absent or a wall-time kill
prevents collection. Evidence version 2 invalidates older measurement reports.

`polygon-state.json` stores identity, baseline, intent, revision, and package
state; it contains no API credentials. Keep it when rerunning a failed upload.
Creation is not blindly retried: the recorded intent can reconcile a unique
owned matching problem. Existing owned names need an explicit `attach`.
`attach` can also resolve a recorded creation intent that has no ID. If an
uncertain creation produced no problem, confirm that in Polygon before removing
only the ID-less intent file and starting creation again.
Partial uploads accept only baseline or intended values; third-party conflicting
changes stop the sync. A modified working copy outside a pending upload is never
overwritten. Removing remote sources/solutions/tests is deliberately refused.
Verified local-only edits can resume an upload if its stored remote-payload hash
is unchanged; edits to the pending remote payload still require reconciliation.

`build` resumes a pending build. A failed/uncertain build requires inspection
before requesting another; its working-copy state is not discarded. The exported
ZIP is Polygon's official artifact, with CRLF normalized only for comparisons.
`publish` checks hard cautions, readiness issues, and verification warnings.
Soft cautions remain visible in `status` and need author review.

Official mapping and references are in `docs/architecture.md`; the original
live observations are in `docs/pilot.md`.

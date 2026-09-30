# A+B Polygon pilot

Date: 2026-09-30. Status: complete, ready for user review.

Scope: complete the first milestone and wait for review before developing the
installable CLI or final agent harness.

The authoring problem is `problems/a-plus-b/`. Each operand is in
`[-10^18, 10^18]`; the sum fits a signed 64-bit integer. The suite contains three
statement samples plus boundary, zero, cancellation, small, and seeded random
tests. Accepted programs use direct addition and offset arithmetic. Incorrect
programs truncate to 32 bits or discard the sign. The independent local oracle
uses Python arbitrary-precision integers.

## Remote result

- Polygon problem ID: **592542**.
- Owner: `AlirezaKaviani`.
- Internal name: `cp-library-a-plus-b`; English title: `A + B`.
- [Open the problem in Polygon](https://polygon.codeforces.com/problem?problemId=592542).
- [Canonical package URL from Polygon's problem.xml](https://polygon.codeforces.com/p5C1J5A/AlirezaKaviani/cp-library-a-plus-b).
- Committed revision: **3**.
- Package ID: **1492984**; standard, Linux, and Windows variants are **READY**.
- Polygon's package comment: `Package created in 11474 ms with verification`.
- Final cautions: no common, statement, structure, or issue cautions; no package
  readiness issues and no latest-package warnings.
- Import access: `codeforces` has **READ** access, confirmed with
  `problem.accesses` on 2026-09-30. This is the permission required by
  [Codeforces' import instructions](https://codeforces.com/blog/entry/10099).

This is a problem in the user's Polygon account. The user-requested import
access was granted; no contest publication was performed. Credentials were supplied through hidden
interactive prompts and were not stored in project files.

## Verification evidence

| Check | Result |
| --- | --- |
| C++ compilation | Seven programs compiled locally; Polygon package build passed |
| Input suite | 34 unique tests, including three samples |
| Generator reproducibility | Every generation command produced identical bytes on two local runs |
| Input validation | Every generated and manual input accepted |
| Validator fixtures | All 18 passed locally and on Polygon |
| Checker fixtures | All 12 passed locally; all 11 supported fixtures passed on Polygon |
| Accepted solutions | Main and reference passed every test, also compared with Python big integers |
| Overflow bug | `wrong-overflow.cpp` rejected on 21 tests |
| Sign bug | `wrong-absolute.cpp` rejected on 14 tests |
| Remote asset audit | Statements, sources, headers, solutions, tags, manual tests, scripts, and fixtures matched local data |
| Official Linux package | All 34 test inputs and answers matched local data after CRLF/LF normalization |
| Statement/tutorial rendering | Both HTML and PDF renders succeeded; both one-page PDFs visually inspected |

The empty-output checker fixture is local-only. Polygon's save endpoint rejected
an empty `testOutput` with `testOutput: Field should not be empty`. Its JSON
fixture explicitly sets `polygon: false`; it still runs in every local check.
This exclusion does not affect contestant tests or the uploaded checker.

Local evidence lives in ignored `problems/a-plus-b/build/verification.json`,
`polygon-audit.json`, and `polygon-status.json`. The account-specific remote
state is in ignored `polygon-state.json`.
Import-access readback is in ignored `build/polygon-accesses.json`; this access
change did not alter revision 3 or require rebuilding its package.

The final downloaded artifacts are:

- `problems/a-plus-b/artifacts/cp-library-a-plus-b-r3-linux.zip`.
- `problems/a-plus-b/artifacts/problem.xml`.
- `problems/a-plus-b/artifacts/statements-english.pdf` and `.html`.
- `problems/a-plus-b/artifacts/tutorials-english.pdf` and `.html`.

## Observed API and package behavior

1. Signed URL-encoded POSTs work for multiline statements, scripts, and source
   files, including the full testlib header. Signature construction uses decoded
   parameter values before URL encoding. Keys and request signatures must stay
   out of logs.
2. `cpp.g++17` works for generator, validator, checker, and solution uploads.
   The two local shared headers must also be uploaded as resource files. The
   package contains them under `files/` alongside the executable sources.
3. The remote namespace is flat. Local paths are an authoring convenience;
   remote names and types are explicitly declared in `problem.toml`.
4. Manual tests plus the generation script produced the expected 34-test
   inventory. `tests` is the testset used by this standard batch pilot. Statement
   samples are manual tests marked for inclusion, with answers derived by Polygon
   from the main solution.
5. Explicit display-input overrides caused an unsafe-statement-input caution
   because of formatting differences. Clearing the overrides removed the
   caution. The uploader now omits them for newly created samples.
6. Validator/checker fixtures are normalized to CRLF remotely. Missing terminal
   newlines remain meaningful. Fixture readback and package comparison normalize
   line endings, while local generation still checks exact bytes.
7. `commitChanges` creates the revision used by the package builder. A full build
   with verification passed the declared solution tags and stress checks.
   A single package ID appears in the package listing for three format variants;
   choose a format explicitly when downloading.
8. The Linux export contains actual generated data. Its input pattern is
   `tests/%02d`, its answer pattern is `tests/%02d.a`, the time limit is 1000 ms,
   and the memory limit is 268435456 bytes. Authoring uses `stdin`/`stdout`; the
   exported XML represents standard streams as empty judging file attributes.
9. The package maps API solution tags to XML tags: `MA` becomes `main`, `OK`
   becomes `accepted`, and `WA` becomes `wrong-answer`. The actual descriptor is
   the reference for future export work; do not assume API and XML names match.
10. Polygon's cautions recommended grouped numeric literals in the validator and
    named range reads in the checker. Both were applied. A large sample crowded
    the PDF table, so it was shortened to `10^12 + 10^12`; the `10^18 + 10^18`
    boundary remains in hidden test 24.
11. Importing into Codeforces requires giving the `codeforces` user READ access.
    `problem.setAccess` applies this outside the working copy; `problem.accesses`
    confirms it. The pilot's `upload` now ensures this permission, and
    `prepare-import` applies it separately to existing problems without
    downgrading stronger access.

## Checkpoint

The pilot established the folder/API contract. The general installable CLI,
remote reconciliation, plain template, and two-mode agent harness now implement
the next milestone; see `docs/cli.md` and `docs/agent-benchmarks.md`.
`tools/pilot.py` remains a historical runner specific to this experiment. Use
`cppl` for new authoring and updates.

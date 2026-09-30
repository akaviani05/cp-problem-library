# Problem authoring: focused onboarding

Read this guide, then run `rtk proxy .venv/bin/cppl doctor`. If `.venv` is absent,
use the setup commands in `docs/cli.md` (setup section only). Do not read the
tool implementation or another problem unless a concrete failure requires it.

## 1. Fix the contract

Translate the informal task into one unambiguous batch problem: input grammar,
every constraint, output, algorithm, numeric types, time/memory limits, and
examples. For an ordinary under-specified task, choose reasonable constraints
and state the assumptions in `review.md`. Ask only when ambiguity changes the
mathematical task or a required user preference cannot be inferred. Continue
independent work while waiting. Do not add multiple queries, weights, scoring,
or interaction unless the user asked for them.

## 2. Scaffold without copying another problem

```bash
rtk proxy .venv/bin/cppl new <slug> --title 'Title' --description 'One sentence' --tags 'tag1,tag2'
```

Read the new `problem.toml`, `review.md`, and the specific stubs you will replace.
The plain checker and its fixtures are already usable for a unique sequence of
tokens. It ignores whitespace but does not allow different numeric spellings,
floating tolerance, or alternative correct outputs; replace it and its fixtures
if the problem needs a semantic checker.

Write exactly these problem files (add manifest entries for additional assets):

| Files | Required content |
| --- | --- |
| `problem.toml` | Metadata, limits, asset paths, solution tags, explicit manual-test indices; set `draft = false` after completing stubs |
| `statements/english/{legend,input,output,notes,tutorial}.tex` | Polygon fragments, precise constraints, sample explanations, algorithm/proof/complexity; no standalone document wrapper |
| `generators/gen.cpp` | Testlib-seeded generator modes; one valid input per invocation |
| `validators/validator.cpp` | Strict syntax plus every structural constraint, ending with EOF |
| `solutions/main.cpp`, `reference.cpp` | Two accepted implementations with meaningful independence |
| `solutions/wrong.cpp` (more if useful) | Plausible wrong approach with a documented rejecting case; use correct Polygon tags |
| `solutions/oracle.py` | Independent stdin→stdout reference; exact arithmetic or a simpler algorithm that can handle packaged tests |
| `tests/manual/NN.in`, `NN.ans` | Small readable statement examples with independently computed answers |
| `tests/doall.txt` | `gen arguments seed > index`; contiguous indices shared with manual tests; no shell loops or `> $` |
| `tests/validator/cases.json` | Valid and invalid strings covering every bound, syntax rule, and semantic invariant |
| `tests/stress.py` | Print one JSON array of small valid input strings, using a fixed seed or exhaustive enumeration |
| `review.md` | Contract/assumptions, correctness proof, independent-reference rationale, coverage by mode, and wrong-solution bugs |

Do not dump all files back into the chat. Keep summaries compact. Keep edits to
the target problem and README table; report CLI/harness defects to the parent
or user instead of silently entering project mode.

## 3. Generator and validator API you need

```cpp
#include "testlib.h"                  // first include
registerGen(argc, argv, 1);           // seeds rnd from all command arguments
opt<std::string>(1); opt<int>(2);     // positional arguments, starting at 1
rnd.next(low, high);                  // inclusive; use LL values for 64-bit ranges
rnd.perm(n);                          // permutation 0..n-1
shuffle(v.begin(), v.end());          // testlib's seeded shuffle
println(a, b);                       // space-separated tokens + final newline

registerValidation(argc, argv);
inf.readInt(lo, hi, "n");
inf.readLong(lo64, hi64, "a");
inf.readSpace(); inf.readEoln(); inf.readEof();
ensuref(condition, "constraint explanation");
```

Use literals such as `1'000'000`. Trees require more than n−1 edges: validate
endpoints, reject loops/duplicates/cycles, and ensure connectivity. Test cases
must include minimum and maximum size, chains, stars, random structures,
shuffled labels/edge order, s=t if allowed, and endpoints chosen to expose
plausible incorrect algorithms. Avoid recursive traversals at large n unless
their stack bound is safe. Coverage matters more than many redundant random cases.

Validator JSON format: `{"name":"label","input":"...\n","verdict":"VALID"}`
or `INVALID`. Checker JSON also has `answer`, `output`, and a verdict `OK`,
`WRONG_ANSWER`, or `PRESENTATION_ERROR`. Keep an empty-field fixture locally
with `"polygon": false`; Polygon's API cannot save it.
This applies to empty validator input as well as empty checker output.
Adapt the plain checker fixtures to the problem's real input/output grammar;
retain whitespace, wrong-token, missing-token, extra-token, and empty-output cases.

## 4. Verify once after completing meaningful edits

```bash
rtk proxy .venv/bin/cppl lint <slug>
rtk proxy .venv/bin/cppl verify <slug>
rtk proxy .venv/bin/cppl inspect <slug>
```

`verify` includes compile caching, validator/checker self-tests, deterministic
generation, validation of every input, main/reference/oracle comparison,
solution-tag checks, sample checks, independent stress tests, resource limits,
and content hashes. It rejects every unfinished draft. Do not separately run
generate/stress first unless diagnosing that specific stage. Re-run verify only
after a relevant edit or failure. Use `inspect` for compact performance evidence;
read `build/verification.json` only for a specific test or witness.

Before upload, independently inspect the proof and oracle, the generator modes,
all constraint checks, and maximum-case performance. Two copies of one algorithm
are not an independent correctness argument. Stress on small cases complements
maximum-case checks; it does not replace them. Limit measured time and memory
must have margin. These process limits are not a security sandbox for untrusted code.

## 5. Complete the remote workflow

An instruction to create a Polygon-ready problem authorizes `publish` using the
configured account. It also authorizes READ access for the `codeforces` user.
Do not ask again for those already authorized actions. If the user asks for an
offline draft only, stop after verification and catalog update.

```bash
rtk proxy .venv/bin/cppl plan <slug>
rtk proxy .venv/bin/cppl publish <slug>
rtk proxy .venv/bin/cppl status <slug>
```

The plan is local and reviewable. `publish` reuses fresh verification; it uploads,
reads back, commits, grants/verifies Codeforces import access, builds a full
verified package, downloads and compares every input/answer, renders statements,
and refreshes README. Do not manufacture ZIP/XML yourself or invent API methods.
Run `cppl catalog` separately only after metadata edits or an offline draft;
successful publication already refreshes the table.
When the tool environment restricts networking, use its network-escalation
mechanism for authorized Polygon commands. Offline checks need no escalation.
Re-run publish after transient network failures; it reconciles partial writes
and preserves incompatible remote changes. If it reports a conflict, explain
the specific conflict and do not discard or overwrite the user's working copy.

Inspect the rendered HTML or PDF: math, constraints, examples, readable sample
tables, and tutorial. Use a visual preview when available; report explicitly if
visual inspection was unavailable. Contest linking is not required.

## 6. Finish with evidence

Report the problem link/ID, assumptions, tests/stress count, rejected-solution
witnesses, measured maximum accepted-solution time/memory, package readiness,
and any remaining cautions. The README table must contain description, tags, and
creation date. For a requested agent benchmark, also report elapsed wall time,
commands/checks retried, unnecessary files read, and concrete harness/tool
friction. Actual LLM token usage may be unavailable: say so, or clearly label a
text-size estimate. Never report RTK shell-output savings as total LLM token usage.

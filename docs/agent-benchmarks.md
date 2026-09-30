# Fresh-agent authoring evaluation

Two independent agents were started with no conversation history. Each received
a short informal problem request, the repository path, authorization to publish,
and a request to record performance and friction. They onboarded through
`AGENTS.md` and the problem guide rather than existing problems or CLI internals.
These are single trials, not a statistical comparison between agents or models.

Wall intervals and shell/read counts below are recorded from the author agents'
reports; verification timings and solution metrics come from CLI reports. Wall
time includes authoring, local checks, network access, Polygon builds/renders,
and visual inspection. Actual LLM token usage is unavailable through the agent
tools. The focused onboarding text is 10,626 characters (10,630 UTF-8 bytes),
roughly 2,657 tokens at an explicitly approximate four characters per token.
This measures only the guide size, not total inference tokens or tool context.

## A Minus B

- Trial interval: 2026-09-30 12:24:00–12:38:13 UTC, **14m13s**.
- 25 shell commands; lint twice, verification once, publish twice, status twice;
  inspect, plan, and catalog once. The repeated publish/status attempts were
  restricted-network failures followed by successful authorized escalations.
- Read scope: 4 instruction files, 18 new scaffold files, one focused README
  row, and previews of the two PDFs. No unrelated problem or implementation
  files were read.
- Chosen contract: one signed pair in ±10^18, result in ±2×10^18;
  1 second / 64 MiB. Canonical decimal output matches the plain token checker.
- 27 packaged tests, 465 stress cases, 20 validator fixtures, 10 checker
  fixtures. A decimal-string C++ reference and Python exact arithmetic provide
  independent checks of the native 64-bit main solution.
- Trial verification took 29.596s. Main maximum wall/CPU: 4.425/2.935ms;
  reference: 5.139/3.566ms. Both peak RSS measurements were 16,520 KiB.
- The absolute-difference wrong solution failed 9 tests; sample `2 7` is a
  witness (expected −5, wrong output 5). All official inputs/answers matched,
  and both one-page PDFs were visually inspected.
- [Polygon 592590](https://polygon.codeforces.com/problem?problemId=592590),
  revision 1/package 1493079 READY at the end of the agent trial.

Parent review confirmed the arithmetic range, decimal-reference logic, strict
validation, independent oracle, and deterministic boundary/adversarial coverage.
Additional input-spelling probes confirmed that leading zeroes, plus signs,
and negative zero are rejected by the strict validator, matching the decimal
reference's canonical-input assumption.

The trial exposed small onboarding/diagnostic issues. The guide now explicitly
marks empty validator input local-only, describes network escalation, and avoids
a redundant catalog invocation after successful publication. Transport errors
now say to retry the CLI command rather than always suggesting `upload`.

Polygon also gave a SOFT unnamed-token warning for the plain checker. The parent
added named pattern reads without changing token comparison, and tested actual
compiled behavior with whitespace, punctuation, Unicode, missing/wrong/extra
tokens. A fresh local verification passed in 22.234s, recompiling only the checker.
The improved A−B problem is revision **2**, full package **1493088**, exported with
every test compared. This parent maintenance is outside the 14m13s agent interval.
The revision-2 readback reports no cautions, readiness issues, or package warnings.

## Tree distance

The second fresh agent receives only: “Given a tree of n vertices and s and t,
find their distance.” Its final measured outcome and parent quality review are
recorded below after publication.

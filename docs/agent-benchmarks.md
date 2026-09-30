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
tools. At the second trial's start, the focused onboarding text was 10,626
characters (10,630 UTF-8 bytes),
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
  reference: 5.139/3.566ms. The original RSS values were later found to include
  inherited Python memory and are not valid solution-memory measurements.
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
After the memory-accounting fix described below, verification at 13:10:50 UTC
passed in 42.258s. Main maximum wall/CPU/RSS was 11.265ms/7.824ms/3,680 KiB;
reference was 11.307ms/7.775ms/3,680 KiB. These measurements precede the later
shared generator-header expansion; that expansion invalidates local verification
freshness until the problem is verified again.

## Tree distance

The second fresh agent received: “Given a tree of n vertices and s and t,
find their distance.” It was dispatched at 2026-09-30 12:43:18 UTC. A user
interruption prevented a final agent timing/count report, so there is no claimed
end-to-end trial duration. The last received count was **25 launched shell
commands**, excluding polls; this is a partial count.

- Read scope: RTK instructions, `AGENTS.md`, the problem guide, 20 newly created
  scaffold files, the PDF skill, and relevant generated artifacts. It did not
  read other problems, CLI implementation, private configuration, the vendored
  header, architecture documentation, or pilot history.
- Chosen contract: an unweighted tree with 1 ≤ n ≤ 200,000 and one query s,t;
  s=t is allowed. Output the number of edges on their unique path. Limits:
  1 second / 256 MiB.
- Main solution: iterative BFS. Independent accepted solution: repeatedly prune
  leaves other than the two query endpoints. Python oracle: root the tree and
  climb parent/depth arrays to the common ancestor. All avoid recursive stack
  overflow on a maximum-size chain.
- 26 packaged tests and 538 stress cases, including every labelled tree for
  n ≤ 4 with all ordered query pairs and 250 seeded random cases. Packaged
  tests cover chains, stars, balanced trees, brooms, random trees, shuffled
  labels/edges, equal endpoints, adjacent endpoints, and maximum-size trees.
- Final fixtures: 32 validator cases (3,039 bytes) and 6 checker cases. The
  DSU validator checks bounds, syntax, loops, duplicates, cycles, connectivity,
  and end of input. Maximum-size generated cases exercise validator scalability.
- Wrong solutions using depth difference, label difference, and vertex count
  failed 14, 16, and 26 packaged tests respectively.
- The initial full package was revision 1/package 1493109 READY. Parent review
  checked both one-page statement/tutorial PDFs and the algorithms, validator,
  oracle, and stress enumeration. A suspected clipped tutorial heading was a
  preview artifact; inspection of the original image confirmed correct margins.

The trial found two consequential tool issues. A redundant 2.7 MB literal
validator fixture made onboarding output and repeated verification expensive.
Removing it during a rate-limited partial upload changed the local fingerprint
and initially blocked resumption. The agent restored it to finish the first
publication. The harness now recommends compact fixtures, and upload recovery
compares the desired remote payload: local-only edits can resume while changes
to that payload still require reconciliation. HTTP 429 responses retain the
pending upload state without blindly retrying mutations.

The second issue was memory accounting: `wait4` reported inherited parent RSS
(93,096 KiB even for a trivial solution). Independent GNU `time` probes exposed
the discrepancy. The CLI now obtains executed-program peak RSS through GNU
`time` and records it as unavailable when it cannot be collected. A regression
test verifies that a large Python parent does not inflate a trivial child's RSS.
Version-2 verification after these fixes passed in 87.139s at 13:16:47 UTC.

After adding the shared generator helpers, the parent performed fresh complete
verification at **17:09:29 UTC**: **48.3s**, 26 packaged tests and 538 stress
cases passed. Maximum main wall/CPU/RSS was **53.490ms/50.412ms/16,468 KiB**;
reference was **46.494ms/43.659ms/16,548 KiB**. Stage timings varied between
runs and are observations, not controlled performance comparisons.

[Polygon 592594](https://polygon.codeforces.com/problem?problemId=592594) is now
revision **2**, full package **1493379 READY**. Publication compared every
exported input and answer, verified `codeforces` READ access, and saved the
statement/tutorial renders. The local verified fingerprint matches the recorded
published fingerprint, and final readback reports no cautions, readiness issues,
or package warnings. Parent fixes, the interruption, and the later shared-header
work are outside the author-agent command count and must not be presented as a
single uninterrupted agent trial.

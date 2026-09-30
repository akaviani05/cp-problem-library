# A+B authoring review

One line contains two signed integers in [-10^18, 10^18]; output their sum.
The sum is in [-2*10^18, 2*10^18], inside signed 64-bit bounds. Direct addition
therefore computes the answer in constant time and space.

The accepted reference offsets both operands by 10^18 and subtracts 2*10^18
after adding. Its intermediate result is at most 4*10^18 and is also safe.
The independent oracle uses Python arbitrary-precision integers. Stress tests
exhaust all pairs of nine selected boundary values, then add 50 fixed-seed pairs.

The 34 packaged cases cover zero, each boundary and sign combination, 32-bit
overflow, exact cancellation, small values, and uniform random 64-bit inputs.
Wrong solutions truncate the answer to 32 bits or discard its sign. Both have
multiple rejection witnesses. Validator fixtures test each violated bound,
missing/extra tokens, malformed integers, and strict whitespace. Checker fixtures
cover correct integers, whitespace, incorrect values, malformed output and extra
tokens. The empty-output fixture is local-only because Polygon rejects empty
self-test fields through its API.

The original pilot passed Polygon verification at revision 3 and downloaded
inputs/answers matched local data. Current reusable-CLI evidence is generated
under build/ and is the upload gate; this prose is not a substitute for it.

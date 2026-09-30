# Contract and correctness

The informal request is interpreted as a single batch instance, an undirected
unweighted tree, and one query. Vertices are numbered 1 through n; 1 <= n <=
200,000; s and t may coincide. Input is `n s t` followed by exactly n-1 edge
lines. Output is the number of edges on the unique s-to-t path, including zero
when s=t. There are no multiple queries, weights, or disconnected inputs.
These are chosen assumptions. Limits are 1 second and 256 MiB. All solutions
use iterative traversals and 32-bit distances (the answer is at most n-1).

The main solution performs BFS from s. BFS first reaches each vertex by a
shortest path, and the tree has a unique simple path, so its depth at t is the
answer. Each vertex is enqueued once and each edge examined twice: O(n) time
and O(n) memory.

The accepted reference repeatedly removes leaves other than s and t. A removed
leaf cannot lie on the s-to-t path: an internal path vertex has two incident
path edges, and neither endpoint is removed. Every branch outside the path is
a finite tree attached to it, so repeated pruning removes that entire branch.
Exactly the path vertices remain, and their count minus one is the distance.
The s=t case is handled separately. This gives O(n) time and memory, and uses
a different invariant from BFS.

The Python oracle roots the tree at vertex 1 with an explicit stack, records
parents and depths, then climbs the deeper endpoint until depths agree and
climbs both until they meet. Each climb counts one path edge; the meeting point
is the lowest common ancestor, whose two ancestor paths partition the desired
path. This independently checks the packaged large cases as well as stress.

The samples are computed by inspection: the single vertex gives 0; path
4-2-1-3-6 gives 4; path 2-1-4 gives 2. The validator checks every numeric bound,
strict single-space and newline syntax, exactly n-1 edge lines, no loops,
unique unordered edges, acyclicity through DSU, explicit connectivity, and EOF.

Coverage: chain tests include the maximum distance, adjacent endpoints, and
coincident endpoints. Stars test two leaves with equal root depths, high degree,
adjacency, and s=t. Balanced binary trees and brooms exercise branching and
different diameter lengths. Random recursive trees exercise irregular degrees.
Each shape has small and maximum-n tests; labels, edge order, and orientation
are shuffled, and query modes include diameter ends, equality, adjacency, and
random endpoints. All generator randomness uses testlib's seed.

Stress enumerates every labelled tree through n=4 using Prüfer codes, with all
ordered endpoint pairs, plus 250 fixed-seed random trees through n=40: 538
cases total. It includes minimum trees, reversed queries, and s=t.

Rejected solutions: `wrong.cpp` outputs the absolute difference of depths
rooted at 1; the second sample requires 4 but it returns 0. `wrong-labels.cpp`
uses absolute label difference; the second sample requires 4 but it returns 2.
`wrong-vertices.cpp` counts path vertices; the first sample requires 0 but it
returns 1. All three are tagged WA and have readable rejecting witnesses.

Verification evidence is recorded by the CLI build reports after checks run.

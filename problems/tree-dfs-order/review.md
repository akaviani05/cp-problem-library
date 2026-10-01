# Contract and review

Input is `n r`, followed by exactly `n-1` undirected edges of a tree on labels `1..n`; `1 <= n <= 200000`, `1 <= r <= n`. The requested output is the unique first-visit order from DFS that processes each vertex's neighbors in ascending label order. Limits are 2 seconds and 256 MiB. The task has a unique answer, so the exact-token checker is appropriate.

The main solution sorts adjacency lists, then uses a LIFO stack. It marks a vertex on push and pushes its unvisited neighbors in descending order; therefore the lowest label is popped first. On a tree, each vertex has one parent on the root path, and the reverse push order makes the stack visit child subtrees in the same sequence as recursive DFS. Every vertex is pushed once. Sorting costs `O(n log n)` total and traversal uses `O(n)` time and memory. The reference and Python oracle instead simulate recursive calls with explicit `(vertex,next-neighbor)` frames, visiting neighbors forward one at a time. They do not use the main solution's reverse-push traversal.

The shared tree generator covers chains, stars, brooms, random labelled trees, chain-plus-random trees, and complete binary trees. Small and maximum-sized tests cover endpoint/interior roots, both permuted and original labels, shuffled edge ordering, and deep traversal. The fixed small stress set puts incident edges in orders that differ from label order and varies the root.

`wrong.cpp` treats input edge order as neighbor order. The sample input itself rejects it: at vertex 3, it visits 5 before 1, while the required order visits 1 first.

Assumptions: one batch case, one-based labels, a simple undirected tree, and a single output line of `n` labels. The root is allowed to be any vertex. No output alternatives exist.

# Contract and review

The input is one undirected tree with $1 \le n \le 200000$, a binary target
string of length $n$, then exactly $n-1$ one-based edges. The required output is
`NO` when no subset exists; otherwise it is `YES`, a count, and distinct input
edge indices for one valid subset. Edge-list order is used as the index order.
No output tie-break is required. The statement uses a 1-second time limit and
256 MB memory limit. Traversals are iterative.

For every chosen edge, both endpoint degrees change parity, so the XOR of all
target bits must be zero. Conversely, root the tree and process vertices from
the leaves upward. When a vertex still needs odd parity, select its parent edge
and toggle its parent's need. Every non-root vertex is then satisfied, and the
root is satisfied exactly when the total XOR is zero. This also determines the
only possible subset: removing any leaf forces the choice of its only incident
edge. Thus an even number of target ones is necessary and sufficient.

`main.cpp` performs the reverse-order need propagation. `reference.cpp`
accumulates subtree XOR values and chooses a parent edge for each subtree with
odd XOR. `oracle.py` independently removes leaves from the current tree and
propagates their needs. The checker verifies an arbitrary submitted subset
directly, including range, uniqueness, feasibility, and every vertex parity;
it does not compare against one canonical edge list.

The generator covers minimum-size, chain, star, broom, random, chain-plus-random,
and complete-binary shapes. Packaged tests include the minimum, two-vertex
tree, medium instances, and several 200000-vertex cases with shuffled labels and
edge order. Target strings cover all-zero, all-one, unrestricted random, and
random-even parity. The validator fixtures cover syntax, bounds, loops,
duplicate edges, and cyclic/disconnected input. The deterministic stress script
emits 500 small cases across chain, star, and random-parent trees, with both
feasible and infeasible bit strings.

`wrong.cpp` uses the plausible but incorrect rule of selecting every edge
incident to a target-odd vertex. On the path $1-2-3$ with target `011`, this
selects both edges and gives parities `101`; selecting only the second edge is
the valid answer.

The input contract assumes a tree as stated, and the validator confirms that
the graph is simple and connected. The checker accepts any edge ordering in a
valid witness and accepts an empty third line when the selected count is zero.

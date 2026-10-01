# Contract and assumptions

The input is a simple undirected graph with $1\le n\le 200{,}000$ and $0\le m\le\min(200{,}000, n(n-1)/2)$. Edge endpoints are distinct and each undirected pair appears at most once. The output is either the single token `FOREST`, or `CYCLE k` followed by the distinct vertices of a simple cycle in cyclic order. Any cycle is accepted. A forest can be disconnected. Limits are 1 second and 256 MiB.

# Correctness

The primary implementation performs iterative depth-first search in every component and records a parent for each discovered vertex. In an undirected DFS, every non-tree edge joins a vertex to one of its ancestors. When the search sees an already visited neighbor other than the current vertex's parent, it has found such an edge. The parent chains from its endpoints meet at a common ancestor; the tree path between the endpoints plus the detected edge is a simple cycle. If no such edge exists in any component, each component is a tree, so the graph is a forest. Both traversal and witness recovery take $O(n+m)$ time and $O(n+m)$ memory.

The semantic checker independently runs DFS to determine whether any cycle exists. It rejects `FOREST` when that search finds a cycle; for a cycle witness it checks the length, vertex uniqueness, every consecutive edge, and the closing edge. The checker accepts any valid witness rather than comparing against the answer file's particular cycle.

# Independent implementations

`reference.cpp` uses a disjoint-set structure while reading edges. It keeps only edges that join different components, so these edges form a forest. A redundant edge proves a cycle; breadth-first search in the maintained forest finds the path that the edge closes. The Python oracle uses the same DSU-plus-forest-path principle with Python containers and acts as an implementation-independent language/runtime cross-check for the iterative DFS solution. Each produces one valid witness; witness equality is not required.

# Test coverage

The generator has forest, arbitrary simple graph, connected cyclic graph, explicit long-cycle, and tree-shape modes. Packaged inputs cover an isolated vertex, disconnected forests, chain/star/broom/random trees, the minimum triangle, a 200,000-vertex cycle, large sparse cyclic and arbitrary graphs, and an empty graph at the maximum vertex bound. The validator checks exact line syntax, EOF, bounds, loops, reversed duplicate edges, and endpoint ranges. Checker fixtures cover false forest claims, cycles in disconnected components, alternate valid witnesses, repeated vertices, absent edges, invalid lengths, missing and extra tokens, and empty output. The fixed-seed stress set contains three edge cases plus 400 random simple graphs with up to ten vertices.

# Rejected-solution misconception

`wrong.cpp` reports any already visited neighbor as a cycle without excluding the DFS parent edge. Thus even a single tree edge is reported as a two-vertex cycle; the checker rejects this on the two-vertex one-edge graph.

# Assumptions

Because the request did not give limits or a wire format, this package selects a standard simple-graph contract and 200,000-vertex/edge bounds. The checker uses one-based labels and the explicit `FOREST` / `CYCLE k ...` format described in the statement. No remote problem identifier or publication is assumed.

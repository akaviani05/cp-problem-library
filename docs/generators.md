# Testlib extension: generator helpers

Include `testlib_ext.h` and call `registerGen(argc, argv, 1)` first. All randomness
uses testlib's `rnd`; identical arguments/seed reproduce the same result.
All graphs are undirected. Vertex labels are **0 through n−1**; add 1 when
printing a problem with one-based input labels.

A `cp::ParentArray` is a vector of n parents, with exactly one `-1` root.
Generated trees are rooted at 0; relabeling can move the root. Trees need n≥1.
A `cp::EdgeList` is a vector of `pair<int,int>`; edge orientation is arbitrary.

| Function | Result |
| --- | --- |
| `random_permutation(n)` | Uniform permutation of 0…n−1; n=0 is allowed |
| `chain_tree(n)` | Path 0–1–…–(n−1) |
| `star_tree(n)` | Every other vertex attached to 0 |
| `broom_tree(n, chain_length=-1)` | Chain followed by leaves attached to its last vertex |
| `random_tree(n)` | Uniform labelled tree via a Prüfer code, rooted at 0 |
| `chain_random_tree(n, chain_length=-1)` | Initial chain, then each vertex attaches to a random earlier vertex |
| `full_binary_tree(n)` | Every internal vertex has exactly two children; requires positive odd n |
| `complete_binary_tree(n)` | Heap-shaped binary tree, including even n; last level filled from the left |
| `generate_tree(n, mode, chain_length=-1)` | Dispatch to one of the tree functions |
| `tree_to_edges(parent)` | Validate a parent array and return its n−1 edges |
| `shuffle_tree_labels(parent)` | Return a relabelled parent array, preserving its root marker |
| `shuffle_edges(edges, shuffle_orientation=true)` | Shuffle order in place; optionally reverse undirected endpoints |
| `shuffle_labels_and_edges(n, edges, shuffle_orientation=true)` | Relabel/shuffle in place; return old-label → new-label mapping |
| `connected_graph(n, m, tree_mode="random", chain_length=-1)` | Tree backbone plus m−n+1 distinct non-tree edges |
| `random_graph(n, m)` | Uniform subset of m distinct edges; connectivity is not forced |
| `random_bipartite_graph(n, left_size, m)` | Uniform subset of m distinct edges across a fixed partition; connectivity is not forced |
| `connected_bipartite_graph(n, left_size, m)` | Random bipartite spanning tree plus m−n+1 distinct non-tree edges |
| `generate_bipartite_graph(n, left_size, m, connected=false)` | Dispatch to either bipartite generator |

Every function is in namespace `cp`. Modes are `chain`, `star`, `broom`, `random`,
`chain-random`, `full-binary`, and `complete-binary`. `binary` means complete;
`long-chain-random` aliases `chain-random`. Underscores can replace hyphens.
An unknown mode fails immediately.

`chain_length` counts **vertices**, ranging from 1 to n. Its default is
`max(1, n/2)` with integer division: even n splits the broom evenly into chain
vertices and leaves; odd n gives the extra vertex to the leaves. Set a larger
length explicitly for a longer backbone. Chain-plus-random trees are not uniform
over all labelled trees.

Graph edge counts use `long long`: `0 ≤ m ≤ n(n−1)/2`; connected graphs additionally
need n≥1 and m≥n−1. `random_graph(0,0)` and both one-vertex/zero-edge cases work.
Impossible sizes, malformed parent arrays, and invalid endpoint labels fail via
testlib. Allocation still needs enough memory for the requested output.

Graph generation samples distinct edge IDs without repeated duplicate draws.
Dense requests sample missing edges; connected graphs sample from the complement
of their tree's edges. Complete and nearly complete graphs therefore terminate
without coupon-collector slowdowns. Random graphs take O(m log n) time and O(m)
space; connected graphs take O(n log n + m log n) time and O(n+m) space. Most tree
shapes take O(n); the uniform Prüfer generator takes O(n log n). Connected graphs
follow the requested tree-plus-edges construction, not a uniform distribution
over connected graphs.

Bipartite generators partition vertices into `[0, left_size)` and
`[left_size, n)`, with `0 ≤ left_size ≤ n` and
`0 ≤ m ≤ left_size*(n-left_size)`. They preserve these labels while shuffling
edge order and orientation. The unrestricted generator may produce a connected
graph; it does not force disconnection. Empty partitions are allowed when m=0.
The connected generator requires n≥1 and m≥n−1; for n>1 both partitions must be
nonempty. A one-vertex graph with no edges is connected for either partition size.

The connected variant grows a tree by attaching each new vertex to a random
already introduced vertex on the opposite side, then samples additional distinct
cross-partition edges. Its tree and final graph are not uniformly distributed.
Both variants avoid duplicate-draw slowdowns even at complete bipartite density.
Unrestricted generation takes O(m) expected time and O(m) space; connected
generation takes O(n log n + m log n) time and O(n+m) space. All randomness uses
the same testlib seed. For example:

```cpp
auto edges = cp::generate_bipartite_graph(100, 40, 200, true);
// Vertices 0..39 are on the left; 40..99 are on the right.
for (auto [u, v] : edges) println(u + 1, v + 1);
```

If you subsequently call `shuffle_labels_and_edges`, map the partition through
its returned permutation as well as any query vertices.

```cpp
#include "testlib_ext.h"

int main(int argc, char** argv) {
    registerGen(argc, argv, 1);
    int n = opt<int>(1);
    auto parent = cp::generate_tree(n, "broom");
    auto edges = cp::tree_to_edges(parent);
    int s = 0, t = n - 1;
    auto labels = cp::shuffle_labels_and_edges(n, edges);
    println(n, labels[s] + 1, labels[t] + 1);
    for (auto [u, v] : edges) println(u + 1, v + 1);
}
```

Map query vertices through the returned permutation whenever you shuffle labels.
The helpers use iterative traversal, so a long chain does not require recursion.

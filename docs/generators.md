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

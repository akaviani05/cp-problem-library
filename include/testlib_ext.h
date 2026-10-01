#ifndef CP_PROBLEM_LIBRARY_TESTLIB_EXT_H
#define CP_PROBLEM_LIBRARY_TESTLIB_EXT_H

// Project helpers belong here; the vendored testlib.h is never modified.
#include "testlib.h"
#include <algorithm>
#include <limits>
#include <numeric>
#include <queue>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

namespace cp {
// Vertices are 0..n-1. A parent array has n entries and one root marked -1.
// Call registerGen(argc, argv, 1) before using any random helper.
using ParentArray = std::vector<int>;
using Edge = std::pair<int, int>;
using EdgeList = std::vector<Edge>;

namespace detail {
inline ParentArray tree_storage(int n) {
    ensuref(n >= 1, "a tree needs at least one vertex");
    ParentArray parent(n, 0);
    parent[0] = -1;
    return parent;
}

inline int chain_size(int n, int length) {
    if (length == -1) length = std::max(1, n / 2);
    ensuref(1 <= length && length <= n, "chain length must be in [1, n]");
    return length;
}

inline long long edge_count(int n) {
    ensuref(n >= 0, "vertex count must be nonnegative");
    return 1LL * n * (n - 1) / 2;
}

inline long long bipartite_edge_count(int n, int left_size) {
    ensuref(n >= 0 && 0 <= left_size && left_size <= n, "partition size must be in [0, n]");
    return 1LL * left_size * (n - left_size);
}

inline Edge bipartite_edge_from_id(int n, int left_size, long long id) {
    const int right_size = n - left_size;
    return {static_cast<int>(id / right_size), left_size + static_cast<int>(id % right_size)};
}

inline long long row_start(int n, int u) {
    return 1LL * u * (2LL * n - u - 1) / 2;
}

inline long long edge_id(int n, Edge edge) {
    if (edge.first > edge.second) std::swap(edge.first, edge.second);
    return row_start(n, edge.first) + edge.second - edge.first - 1;
}

inline Edge edge_from_id(int n, long long id) {
    int low = 0, high = n - 1;
    while (low + 1 < high) {
        const int middle = low + (high - low) / 2;
        if (row_start(n, middle) <= id) low = middle;
        else high = middle;
    }
    return {low, low + 1 + static_cast<int>(id - row_start(n, low))};
}

// Floyd sampling. Sample omissions for dense subsets, avoiding repeated draws.
inline std::vector<long long> sample_indices(long long total, long long count) {
    ensuref(0 <= count && count <= total, "invalid distinct-sample size");
    ensuref(static_cast<unsigned long long>(count) <= std::vector<long long>().max_size(),
            "sample cannot fit in a vector");
    const bool dense = count > total / 2;
    const long long draws = dense ? total - count : count;
    std::unordered_set<long long> selected;
    selected.reserve(static_cast<std::size_t>(draws));
    std::vector<long long> result;
    result.reserve(static_cast<std::size_t>(count));
    for (long long j = total - draws; j < total; ++j) {
        const long long candidate = rnd.next(0LL, j);
        const long long chosen = selected.insert(candidate).second ? candidate : j;
        if (chosen == j) selected.insert(j);
        if (!dense) result.push_back(chosen);
    }
    if (dense)
        for (long long id = 0; id < total; ++id)
            if (selected.find(id) == selected.end()) result.push_back(id);
    return result;
}
}  // namespace detail

inline std::vector<int> random_permutation(int n) {
    ensuref(n >= 0, "permutation size must be nonnegative");
    return rnd.perm(n);
}

inline ParentArray chain_tree(int n) {
    auto parent = detail::tree_storage(n);
    for (int v = 1; v < n; ++v) parent[v] = v - 1;
    return parent;
}

inline ParentArray star_tree(int n) {
    return detail::tree_storage(n);
}

// chain_length counts vertices, not edges. Remaining vertices attach to its tip.
inline ParentArray broom_tree(int n, int chain_length = -1) {
    auto parent = detail::tree_storage(n);
    chain_length = detail::chain_size(n, chain_length);
    for (int v = 1; v < n; ++v)
        parent[v] = v < chain_length ? v - 1 : chain_length - 1;
    return parent;
}

inline ParentArray chain_random_tree(int n, int chain_length = -1) {
    auto parent = detail::tree_storage(n);
    chain_length = detail::chain_size(n, chain_length);
    for (int v = 1; v < n; ++v)
        parent[v] = v < chain_length ? v - 1 : rnd.next(0, v - 1);
    return parent;
}

inline ParentArray complete_binary_tree(int n) {
    auto parent = detail::tree_storage(n);
    for (int v = 1; v < n; ++v) parent[v] = (v - 1) / 2;
    return parent;
}

// Full means every internal vertex has exactly two children: n must be odd.
inline ParentArray full_binary_tree(int n) {
    ensuref(n >= 1 && n % 2 == 1, "a full binary tree needs a positive odd n");
    return complete_binary_tree(n);
}

// Uniform labelled tree via a uniform Pruefer code; root it at vertex 0.
inline ParentArray random_tree(int n) {
    auto parent = detail::tree_storage(n);
    if (n == 1) return parent;
    std::vector<int> code(n - 2), degree(n, 1);
    for (int& v : code) { v = rnd.next(0, n - 1); ++degree[v]; }
    std::priority_queue<int, std::vector<int>, std::greater<int>> leaves;
    for (int v = 0; v < n; ++v) if (degree[v] == 1) leaves.push(v);
    std::vector<std::vector<int>> adjacency(n);
    auto add = [&](int u, int v) { adjacency[u].push_back(v); adjacency[v].push_back(u); };
    for (int v : code) {
        const int leaf = leaves.top(); leaves.pop();
        add(leaf, v);
        if (--degree[v] == 1) leaves.push(v);
    }
    const int u = leaves.top(); leaves.pop();
    add(u, leaves.top());
    std::vector<int> order{0};
    for (std::size_t i = 0; i < order.size(); ++i)
        for (int v : adjacency[order[i]]) if (v != parent[order[i]]) {
            parent[v] = order[i];
            order.push_back(v);
        }
    return parent;
}

inline ParentArray generate_tree(int n, std::string mode, int chain_length = -1) {
    std::replace(mode.begin(), mode.end(), '_', '-');
    if (mode == "chain") return chain_tree(n);
    if (mode == "star") return star_tree(n);
    if (mode == "broom") return broom_tree(n, chain_length);
    if (mode == "random") return random_tree(n);
    if (mode == "chain-random" || mode == "long-chain-random") return chain_random_tree(n, chain_length);
    if (mode == "full-binary") return full_binary_tree(n);
    if (mode == "binary" || mode == "complete-binary") return complete_binary_tree(n);
    quitf(_fail, "unknown tree mode: %s", mode.c_str());
}

// Validate arbitrary parent arrays, including trees with a relabelled root.
inline EdgeList tree_to_edges(const ParentArray& parent) {
    ensuref(!parent.empty() && parent.size() <= static_cast<std::size_t>(std::numeric_limits<int>::max()),
            "invalid parent-array size");
    const int n = static_cast<int>(parent.size());
    std::vector<int> representative(n), size(n, 1);
    std::iota(representative.begin(), representative.end(), 0);
    auto root = [&](int v) {
        while (representative[v] != v) {
            representative[v] = representative[representative[v]];
            v = representative[v];
        }
        return v;
    };
    EdgeList edges;
    edges.reserve(n - 1);
    int roots = 0;
    for (int v = 0; v < n; ++v) {
        const int p = parent[v];
        if (p == -1) { ++roots; continue; }
        ensuref(0 <= p && p < n && p != v, "invalid parent of vertex %d", v);
        int a = root(p), b = root(v);
        ensuref(a != b, "parent array contains a cycle");
        if (size[a] < size[b]) std::swap(a, b);
        representative[b] = a; size[a] += size[b];
        edges.emplace_back(p, v);
    }
    ensuref(roots == 1, "parent array needs exactly one root marked -1");
    return edges;
}

inline ParentArray shuffle_tree_labels(const ParentArray& parent) {
    tree_to_edges(parent);  // Validate before indexing the permutation.
    const auto labels = random_permutation(static_cast<int>(parent.size()));
    ParentArray result(parent.size());
    for (std::size_t v = 0; v < parent.size(); ++v)
        result[labels[v]] = parent[v] == -1 ? -1 : labels[parent[v]];
    return result;
}

inline void shuffle_edges(EdgeList& edges, bool shuffle_orientation = true) {
    ::shuffle(edges.begin(), edges.end());
    if (shuffle_orientation)
        for (auto& edge : edges) if (rnd.next(0, 1)) std::swap(edge.first, edge.second);
}

// Modifies edges in place; returns old-label -> new-label (also map s/t with it).
inline std::vector<int> shuffle_labels_and_edges(int n, EdgeList& edges, bool shuffle_orientation = true) {
    ensuref(n >= 0, "vertex count must be nonnegative");
    for (const auto& edge : edges)
        ensuref(0 <= edge.first && edge.first < n && 0 <= edge.second && edge.second < n
                && edge.first != edge.second, "invalid undirected edge");
    const auto labels = random_permutation(n);
    for (auto& edge : edges) { edge.first = labels[edge.first]; edge.second = labels[edge.second]; }
    shuffle_edges(edges, shuffle_orientation);
    return labels;
}

// Uniform m-edge subset of the complete undirected graph. Connectivity is not forced.
inline EdgeList random_graph(int n, long long m) {
    const long long total = detail::edge_count(n);
    ensuref(0 <= m && m <= total, "graph needs 0 <= m <= n(n-1)/2");
    ensuref(static_cast<unsigned long long>(m) <= EdgeList().max_size(), "edge count cannot fit in a vector");
    EdgeList edges;
    edges.reserve(static_cast<std::size_t>(m));
    for (long long id : detail::sample_indices(total, m)) edges.push_back(detail::edge_from_id(n, id));
    shuffle_edges(edges);
    return edges;
}

// Tree backbone plus exactly m-n+1 uniformly chosen non-tree edges.
inline EdgeList connected_graph(int n, long long m, const std::string& tree_mode = "random", int chain_length = -1) {
    ensuref(n >= 1, "a connected graph needs at least one vertex");
    const long long total = detail::edge_count(n);
    ensuref(n - 1 <= m && m <= total, "connected graph needs n-1 <= m <= n(n-1)/2");
    ensuref(static_cast<unsigned long long>(m) <= EdgeList().max_size(), "edge count cannot fit in a vector");
    auto edges = tree_to_edges(generate_tree(n, tree_mode, chain_length));
    std::vector<long long> holes;
    holes.reserve(n - 1);
    for (const auto& edge : edges) holes.push_back(detail::edge_id(n, edge));
    std::sort(holes.begin(), holes.end());
    for (std::size_t i = 0; i < holes.size(); ++i) holes[i] -= static_cast<long long>(i);
    edges.reserve(static_cast<std::size_t>(m));
    for (long long rank : detail::sample_indices(total - n + 1, m - n + 1)) {
        const long long id = rank + (std::upper_bound(holes.begin(), holes.end(), rank) - holes.begin());
        edges.push_back(detail::edge_from_id(n, id));
    }
    shuffle_edges(edges);
    return edges;
}

// Fixed partition: [0, left_size) and [left_size, n). Connectivity is not forced.
inline EdgeList random_bipartite_graph(int n, int left_size, long long m) {
    const long long total = detail::bipartite_edge_count(n, left_size);
    ensuref(0 <= m && m <= total, "bipartite graph needs 0 <= m <= left_size*(n-left_size)");
    ensuref(static_cast<unsigned long long>(m) <= EdgeList().max_size(), "edge count cannot fit in a vector");
    EdgeList edges;
    edges.reserve(static_cast<std::size_t>(m));
    for (long long id : detail::sample_indices(total, m))
        edges.push_back(detail::bipartite_edge_from_id(n, left_size, id));
    shuffle_edges(edges);
    return edges;
}

// Grow a spanning tree across the partition, then sample distinct non-tree edges.
inline EdgeList connected_bipartite_graph(int n, int left_size, long long m) {
    const long long total = detail::bipartite_edge_count(n, left_size);
    ensuref(n >= 1 && n - 1 <= m && m <= total,
            "connected bipartite graph needs n >= 1 and n-1 <= m <= left_size*(n-left_size)");
    ensuref(static_cast<unsigned long long>(m) <= EdgeList().max_size(), "edge count cannot fit in a vector");
    if (n == 1) return {};
    EdgeList edges;
    edges.reserve(static_cast<std::size_t>(m));
    std::vector<int> left{rnd.next(0, left_size - 1)}, right{rnd.next(left_size, n - 1)};
    left.reserve(left_size);
    right.reserve(n - left_size);
    edges.emplace_back(left[0], right[0]);
    for (int v : random_permutation(n)) {
        if (v == left[0] || v == right[0]) continue;
        if (v < left_size) {
            edges.emplace_back(v, right[rnd.next(0, static_cast<int>(right.size()) - 1)]);
            left.push_back(v);
        } else {
            edges.emplace_back(left[rnd.next(0, static_cast<int>(left.size()) - 1)], v);
            right.push_back(v);
        }
    }
    std::vector<long long> holes;
    holes.reserve(n - 1);
    for (const auto& edge : edges)
        holes.push_back(1LL * edge.first * (n - left_size) + edge.second - left_size);
    std::sort(holes.begin(), holes.end());
    for (std::size_t i = 0; i < holes.size(); ++i) holes[i] -= static_cast<long long>(i);
    for (long long rank : detail::sample_indices(total - n + 1, m - n + 1)) {
        const long long id = rank + (std::upper_bound(holes.begin(), holes.end(), rank) - holes.begin());
        edges.push_back(detail::bipartite_edge_from_id(n, left_size, id));
    }
    shuffle_edges(edges);
    return edges;
}

inline EdgeList generate_bipartite_graph(int n, int left_size, long long m, bool connected = false) {
    return connected ? connected_bipartite_graph(n, left_size, m) : random_bipartite_graph(n, left_size, m);
}

inline void require_output_eof() {
    if (!ouf.seekEof())
        quitf(_pe, "unexpected tokens after the answer");
}
}  // namespace cp

#endif

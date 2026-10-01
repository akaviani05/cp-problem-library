#include "testlib_ext.h"
#include <cassert>
#include <set>

using cp::EdgeList;

std::set<cp::Edge> normalized(const EdgeList& edges) {
    std::set<cp::Edge> result;
    for (auto e : edges) {
        if (e.first > e.second) std::swap(e.first, e.second);
        result.insert(e);
    }
    return result;
}

void graph_check(int n, const EdgeList& edges, long long m, bool connected) {
    assert(static_cast<long long>(edges.size()) == m);
    assert(normalized(edges).size() == edges.size());
    std::vector<std::vector<int>> adjacency(n);
    for (auto e : edges) {
        assert(0 <= e.first && e.first < n && 0 <= e.second && e.second < n && e.first != e.second);
        adjacency[e.first].push_back(e.second);
        adjacency[e.second].push_back(e.first);
    }
    if (connected) {
        std::vector<bool> seen(n);
        std::vector<int> order{0};
        seen[0] = true;
        for (std::size_t i = 0; i < order.size(); ++i)
            for (int v : adjacency[order[i]]) if (!seen[v]) { seen[v] = true; order.push_back(v); }
        assert(static_cast<int>(order.size()) == n);
    }
}

int main(int argc, char** argv) {
    registerGen(argc, argv, 1);
    const auto mode = opt<std::string>(1);
    if (mode == "trees") {
        for (int n = 1; n <= 80; ++n) {
            for (const auto& shape : {"chain", "star", "broom", "random", "chain-random", "binary"}) {
                const auto parent = cp::generate_tree(n, shape);
                assert(parent.size() == static_cast<std::size_t>(n) && parent[0] == -1);
                graph_check(n, cp::tree_to_edges(parent), n - 1, true);
                graph_check(n, cp::tree_to_edges(cp::shuffle_tree_labels(parent)), n - 1, true);
            }
            const auto chain = cp::chain_tree(n), star = cp::star_tree(n), broom = cp::broom_tree(n);
            for (int v = 1; v < n; ++v) {
                assert(chain[v] == v - 1);
                assert(star[v] == 0);
                assert(broom[v] == (v < std::max(1, n / 2) ? v - 1 : std::max(1, n / 2) - 1));
            }
            for (int length : {1, n}) {
                const auto mixed = cp::chain_random_tree(n, length);
                for (int v = 1; v < length; ++v) assert(mixed[v] == v - 1);
                graph_check(n, cp::tree_to_edges(mixed), n - 1, true);
                const auto broom_custom = cp::broom_tree(n, length);
                for (int v = length; v < n; ++v) assert(broom_custom[v] == length - 1);
            }
            if (n % 2) {
                const auto full = cp::full_binary_tree(n);
                std::vector<int> children(n);
                for (int v = 1; v < n; ++v) ++children[full[v]];
                for (int count : children) assert(count == 0 || count == 2);
            }
        }
        graph_check(200000, cp::tree_to_edges(cp::random_tree(200000)), 199999, true);
    } else if (mode == "graphs") {
        for (int n = 0; n <= 14; ++n) {
            const long long total = 1LL * n * (n - 1) / 2;
            for (long long m = 0; m <= total; ++m) {
                graph_check(n, cp::random_graph(n, m), m, false);
                if (n > 0 && m >= n - 1)
                    for (const auto& shape : {"chain", "star", "broom", "random", "chain-random", "binary"})
                        graph_check(n, cp::connected_graph(n, m, shape), m, true);
            }
        }
        graph_check(200000, cp::connected_graph(200000, 400000), 400000, true);
        graph_check(200000, cp::random_graph(200000, 400000), 400000, false);
        graph_check(1000, cp::random_graph(1000, 499499), 499499, false);
        graph_check(1000, cp::connected_graph(1000, 499500, "star"), 499500, true);
        // Exercise 64-bit edge ranks without allocating n-sized adjacency.
        const int huge_n = std::numeric_limits<int>::max();
        const auto huge = cp::random_graph(huge_n, 12);
        assert(huge.size() == 12 && normalized(huge).size() == 12);
        for (auto e : huge)
            assert(0 <= e.first && e.first < huge_n && 0 <= e.second && e.second < huge_n && e.first != e.second);
    } else if (mode == "bipartite") {
        auto check = [](int n, int left_size, long long m, bool connected) {
            const auto edges = cp::generate_bipartite_graph(n, left_size, m, connected);
            graph_check(n, edges, m, connected);
            for (auto e : edges) assert((e.first < left_size) != (e.second < left_size));
        };
        for (int n = 0; n <= 12; ++n)
            for (int left_size = 0; left_size <= n; ++left_size)
                for (long long m = 0; m <= 1LL * left_size * (n - left_size); ++m) {
                    check(n, left_size, m, false);
                    if (n >= 1 && m >= n - 1) check(n, left_size, m, true);
                }
        check(200000, 100000, 400000, false);
        check(200000, 100000, 400000, true);
        check(1000, 500, 249999, false);
        check(1000, 500, 250000, true);
        check(200000, 1, 199999, true);
        const int huge_n = std::numeric_limits<int>::max(), left_size = huge_n / 2;
        const auto huge = cp::random_bipartite_graph(huge_n, left_size, 12);
        assert(huge.size() == 12 && normalized(huge).size() == 12);
        for (auto e : huge) {
            assert(0 <= e.first && e.first < huge_n && 0 <= e.second && e.second < huge_n);
            assert((e.first < left_size) != (e.second < left_size));
        }
    } else if (mode == "shuffle") {
        assert(cp::random_permutation(0).empty());
        for (int n = 1; n <= 150; ++n) {
            auto permutation = cp::random_permutation(n);
            std::sort(permutation.begin(), permutation.end());
            for (int v = 0; v < n; ++v) assert(permutation[v] == v);
            auto edges = cp::tree_to_edges(cp::random_tree(n));
            const auto before = edges;
            const auto labels = cp::shuffle_labels_and_edges(n, edges);
            EdgeList expected;
            for (auto e : before) expected.emplace_back(labels[e.first], labels[e.second]);
            assert(normalized(edges) == normalized(expected));
            cp::shuffle_edges(edges);
            assert(normalized(edges) == normalized(expected));
        }
    } else if (mode == "sample") {
        auto edges = cp::connected_graph(30, 85);
        cp::shuffle_labels_and_edges(30, edges);
        for (auto e : edges) println(e.first, e.second);
        for (auto e : cp::random_bipartite_graph(30, 12, 85)) println(e.first, e.second);
        for (auto e : cp::connected_bipartite_graph(30, 12, 85)) println(e.first, e.second);
    } else if (mode == "invalid-full-binary") cp::full_binary_tree(4);
    else if (mode == "invalid-tree-size") cp::chain_tree(0);
    else if (mode == "invalid-chain-size") cp::broom_tree(4, 5);
    else if (mode == "invalid-mode") cp::generate_tree(4, "unknown");
    else if (mode == "invalid-parent-cycle") cp::tree_to_edges({-1, 2, 1});
    else if (mode == "invalid-parent-roots") cp::tree_to_edges({-1, -1});
    else if (mode == "invalid-parent-index") cp::tree_to_edges({-1, 2});
    else if (mode == "invalid-graph") cp::random_graph(3, 4);
    else if (mode == "invalid-negative-graph") cp::random_graph(-1, 0);
    else if (mode == "invalid-connected") cp::connected_graph(4, 2);
    else if (mode == "invalid-empty-connected") cp::connected_graph(0, 0);
    else if (mode == "invalid-shuffle") { EdgeList edges{{0, 2}}; cp::shuffle_labels_and_edges(2, edges); }
    else if (mode == "invalid-bipartite-partition") cp::random_bipartite_graph(4, 5, 0);
    else if (mode == "invalid-bipartite-negative-partition") cp::random_bipartite_graph(4, -1, 0);
    else if (mode == "invalid-bipartite-negative-size") cp::random_bipartite_graph(-1, 0, 0);
    else if (mode == "invalid-bipartite-edges") cp::random_bipartite_graph(4, 2, 5);
    else if (mode == "invalid-bipartite-negative-edges") cp::random_bipartite_graph(4, 2, -1);
    else if (mode == "invalid-bipartite-connected") cp::connected_bipartite_graph(4, 2, 2);
    else if (mode == "invalid-bipartite-empty-side") cp::connected_bipartite_graph(4, 0, 3);
    else if (mode == "invalid-bipartite-empty-connected") cp::connected_bipartite_graph(0, 0, 0);
    else quitf(_fail, "unknown test mode");
    if (mode != "sample") println("PASS", mode);
}

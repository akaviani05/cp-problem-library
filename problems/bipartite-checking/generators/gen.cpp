#include "testlib_ext.h"
#include <set>

int main(int argc, char** argv) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);
    const int m = opt<int>(3);
    cp::EdgeList edges;

    if (mode == "random") {
        edges = cp::random_graph(n, m);
    } else if (mode == "path" || mode == "star") {
        ensuref(m == n - 1, "tree modes need exactly n-1 edges");
        auto parent = cp::generate_tree(n, mode == "path" ? "chain" : "star");
        edges = cp::tree_to_edges(parent);
        cp::shuffle_labels_and_edges(n, edges);
    } else if (mode == "bipartite") {
        const int left = opt<int>(4);
        edges = cp::generate_bipartite_graph(n, left, m, false);
    } else if (mode == "connected-bipartite") {
        const int left = opt<int>(4);
        edges = cp::generate_bipartite_graph(n, left, m, true);
    } else if (mode == "odd-cycle") {
        ensuref(n >= 3 && m >= 3, "odd-cycle mode needs n,m >= 3");
        std::set<std::pair<int, int>> chosen;
        for (auto [u, v] : cp::random_graph(n, m)) chosen.insert(std::minmax(u, v));
        const std::set<std::pair<int, int>> triangle{{0, 1}, {0, 2}, {1, 2}};
        chosen.insert(triangle.begin(), triangle.end());
        while (static_cast<int>(chosen.size()) > m) {
            auto it = chosen.begin();
            while (triangle.count(*it)) ++it;
            chosen.erase(it);
        }
        edges.assign(chosen.begin(), chosen.end());
    } else if (mode == "disconnected-odd") {
        ensuref(n >= 4 && m == 3, "disconnected-odd mode needs n >= 4 and m = 3");
        edges = {{1, 2}, {1, 3}, {2, 3}};
    } else if (mode == "long-odd-cycle") {
        ensuref(n >= 3 && n % 2 == 1 && m == n,
                "long-odd-cycle mode needs odd n >= 3 and m = n");
        auto parent = cp::chain_tree(n);
        edges = cp::tree_to_edges(parent);
        edges.push_back({0, n - 1});
        cp::shuffle_labels_and_edges(n, edges);
    } else {
        quitf(_fail, "unknown mode: %s", mode.c_str());
    }

    println(n, static_cast<int>(edges.size()));
    for (auto [u, v] : edges) println(u + 1, v + 1);
}

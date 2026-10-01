#include "testlib_ext.h"

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);
    const int m = opt<int>(3);
    cp::EdgeList edges;
    if (mode == "forest") {
        ensuref(0 <= m && m <= n - 1, "forest requires m <= n-1");
        auto parent = cp::chain_tree(n);
        auto path = cp::tree_to_edges(parent);
        edges.assign(path.begin(), path.begin() + m);
    } else if (mode == "random") {
        edges = cp::random_graph(n, m);
    } else if (mode == "connected-cycle") {
        ensuref(n >= 3 && m >= n, "connected-cycle requires n >= 3 and m >= n");
        edges = cp::connected_graph(n, m, "chain");
    } else if (mode == "long-cycle") {
        ensuref(n >= 3 && m == n, "long-cycle requires n >= 3 and m=n");
        auto parent = cp::chain_tree(n);
        edges = cp::tree_to_edges(parent);
        edges.emplace_back(0, n - 1);
        cp::shuffle_edges(edges);
    } else if (mode == "tree") {
        ensuref(m == n - 1, "tree mode requires m=n-1");
        const std::string shape = opt<std::string>(4);
        auto parent = cp::generate_tree(n, shape);
        edges = cp::tree_to_edges(parent);
        cp::shuffle_labels_and_edges(n, edges);
    } else {
        quitf(_fail, "unknown mode '%s'", mode.c_str());
    }
    println(n, edges.size());
    for (auto [u, v] : edges) println(u + 1, v + 1);
}

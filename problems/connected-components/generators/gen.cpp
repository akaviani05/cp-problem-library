#include "testlib.h"
#include "testlib_ext.h"

int main(int argc, char** argv) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);
    const int m = opt<int>(3);
    const int seed = opt<int>(4);
    (void)seed;

    cp::EdgeList edges;
    if (mode == "chain") {
        ensuref(m == n - 1, "chain mode requires m=n-1");
        edges = cp::tree_to_edges(cp::chain_tree(n));
    } else if (mode == "shuffled-chain") {
        ensuref(m == n - 1, "shuffled-chain mode requires m=n-1");
        edges = cp::tree_to_edges(cp::chain_tree(n));
        cp::shuffle_labels_and_edges(n, edges);
    } else if (mode == "star") {
        ensuref(m == n - 1, "star mode requires m=n-1");
        edges = cp::tree_to_edges(cp::star_tree(n));
    } else if (mode == "random") {
        edges = cp::random_graph(n, m);
    } else if (mode == "disconnected") {
        ensuref(n >= 2, "disconnected mode requires n>=2");
        const int left = n / 2;
        const int right = n - left;
        const long long capLeft = 1LL * left * (left - 1) / 2;
        const long long capRight = 1LL * right * (right - 1) / 2;
        ensuref(m <= capLeft + capRight, "too many edges for disconnected mode");
        const int mLeft = (int)std::min<long long>(m, capLeft);
        const int mRight = m - mLeft;
        auto a = cp::random_graph(left, mLeft);
        auto b = cp::random_graph(right, mRight);
        edges = a;
        for (auto [u, v] : b) edges.emplace_back(u + left, v + left);
        cp::shuffle_edges(edges);
    } else if (mode == "complete") {
        ensuref(1LL * n * (n - 1) / 2 == m, "complete mode requires a complete graph");
        edges = cp::random_graph(n, m);
    } else {
        quitf(_fail, "unknown mode: %s", mode.c_str());
    }

    println(n, m);
    for (auto [u, v] : edges) println(u + 1, v + 1);
}

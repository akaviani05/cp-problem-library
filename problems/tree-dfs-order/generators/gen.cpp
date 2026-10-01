#include "testlib_ext.h"
#include <string>

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);
    const int root = opt<int>(3) - 1;
    const int permute = opt<int>(5);
    auto parent = cp::generate_tree(n, mode);
    auto edges = cp::tree_to_edges(parent);
    int outputRoot = root;
    if (permute) {
        auto labels = cp::shuffle_labels_and_edges(n, edges);
        outputRoot = labels[root];
    } else {
        cp::shuffle_edges(edges);
    }
    println(n, outputRoot + 1);
    for (auto [u, v] : edges) println(u + 1, v + 1);
}

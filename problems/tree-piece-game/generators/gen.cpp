#include "testlib.h"
#include "testlib_ext.h"

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);

    auto parent = cp::generate_tree(n, mode);
    auto edges = cp::tree_to_edges(parent);
    cp::shuffle_labels_and_edges(n, edges);
    const auto vertices = rnd.perm(n);
    const int x = vertices[0];
    const int y = vertices[1];

    println(n, x + 1, y + 1);
    for (const auto [u, v] : edges) println(u + 1, v + 1);
}

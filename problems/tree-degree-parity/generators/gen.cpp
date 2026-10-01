#include "testlib_ext.h"

int main(int argc, char** argv) {
    registerGen(argc, argv, 1);
    const int n = opt<int>(1);
    const std::string tree_mode = opt<std::string>(2);
    const std::string bits_mode = opt<std::string>(3);

    auto parent = cp::generate_tree(n, tree_mode);
    auto edges = cp::tree_to_edges(parent);
    cp::shuffle_labels_and_edges(n, edges);

    std::string bits(n, '0');
    if (bits_mode == "ones") {
        std::fill(bits.begin(), bits.end(), '1');
    } else if (bits_mode == "random") {
        for (char& bit : bits) bit = char('0' + rnd.next(0, 1));
    } else if (bits_mode == "even") {
        int parity = 0;
        for (char& bit : bits) {
            bit = char('0' + rnd.next(0, 1));
            parity ^= bit - '0';
        }
        if (parity) bits.back() = bits.back() == '0' ? '1' : '0';
    } else if (bits_mode != "zero") {
        quitf(_fail, "unknown bits mode: %s", bits_mode.c_str());
    }

    println(n);
    println(bits);
    for (auto [u, v] : edges) println(u + 1, v + 1);
}

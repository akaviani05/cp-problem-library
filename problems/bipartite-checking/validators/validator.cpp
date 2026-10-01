#include "testlib.h"
#include <algorithm>
#include <set>

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readSpace();
    const int m = inf.readInt(0, 200'000, "m");
    inf.readEoln();
    std::set<std::pair<int, int>> edges;
    for (int i = 0; i < m; ++i) {
        const int u = inf.readInt(1, n, "u");
        inf.readSpace();
        const int v = inf.readInt(1, n, "v");
        inf.readEoln();
        ensuref(u != v, "self-loops are not allowed");
        ensuref(edges.insert(std::minmax(u, v)).second,
                "each undirected edge must appear once");
    }
    inf.readEof();
}

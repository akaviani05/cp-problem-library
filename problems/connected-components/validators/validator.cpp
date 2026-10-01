#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readSpace();
    const int m = inf.readInt(0, 200'000, "m");
    inf.readEoln();
    ensuref(1LL * m <= 1LL * n * (n - 1) / 2, "m exceeds the number of simple edges");
    std::set<std::pair<int, int>> seen;
    for (int i = 0; i < m; ++i) {
        const int u = inf.readInt(1, n, "u");
        inf.readSpace();
        const int v = inf.readInt(1, n, "v");
        inf.readEoln();
        ensuref(u != v, "self-loops are not allowed");
        const auto edge = std::minmax(u, v);
        ensuref(seen.emplace(edge.first, edge.second).second, "edges must be distinct");
    }
    inf.readEof();
}

#include "testlib.h"

#include <algorithm>
#include <cstdint>
#include <unordered_set>

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readSpace();
    const int m = inf.readInt(0, 200'000, "m");
    inf.readEoln();
    ensuref(1LL * m <= 1LL * n * (n - 1) / 2, "too many edges for a simple graph");
    std::unordered_set<std::uint64_t> seen;
    seen.reserve(static_cast<std::size_t>(m) * 2 + 1);
    for (int i = 0; i < m; ++i) {
        const int u = inf.readInt(1, n, "u");
        inf.readSpace();
        const int v = inf.readInt(1, n, "v");
        inf.readEoln();
        ensuref(u != v, "self-loops are not allowed");
        const int a = std::min(u, v), b = std::max(u, v);
        const std::uint64_t key = (static_cast<std::uint64_t>(a) << 32) | b;
        ensuref(seen.insert(key).second, "duplicate undirected edge");
    }
    inf.readEof();
}

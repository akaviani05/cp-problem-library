#include "testlib.h"
#include <numeric>
#include <vector>

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readSpace();
    inf.readInt(1, n, "r");
    inf.readEoln();
    std::vector<int> parent(n), size(n, 1);
    std::iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        int y = x;
        while (parent[y] != y) y = parent[y];
        while (parent[x] != x) { int z = parent[x]; parent[x] = y; x = z; }
        return y;
    };
    for (int i = 0; i < n - 1; ++i) {
        int u = inf.readInt(1, n, "u") - 1;
        inf.readSpace();
        int v = inf.readInt(1, n, "v") - 1;
        inf.readEoln();
        ensuref(u != v, "self-loops are not allowed");
        int a = find(u), b = find(v);
        ensuref(a != b, "edges must form a tree without cycles or duplicates");
        if (size[a] < size[b]) { int t = a; a = b; b = t; }
        parent[b] = a;
        size[a] += size[b];
    }
    ensuref(size[find(0)] == n, "the graph must be connected");
    inf.readEof();
}

#include "testlib.h"

#include <utility>
#include <vector>

struct DSU {
    std::vector<int> parent;
    explicit DSU(int n) : parent(n, -1) {}

    int find(int v) {
        if (parent[v] < 0) return v;
        return parent[v] = find(parent[v]);
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) return false;
        if (parent[a] > parent[b]) std::swap(a, b);
        parent[a] += parent[b];
        parent[b] = a;
        return true;
    }
};

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(2, 200'000, "n");
    inf.readSpace();
    const int x = inf.readInt(1, n, "x");
    inf.readSpace();
    const int y = inf.readInt(1, n, "y");
    ensuref(x != y, "the starting vertices must be distinct");
    inf.readEoln();

    DSU dsu(n);
    for (int i = 0; i < n - 1; ++i) {
        const int u = inf.readInt(1, n, "u") - 1;
        inf.readSpace();
        const int v = inf.readInt(1, n, "v") - 1;
        ensuref(u != v, "an edge cannot be a loop");
        ensuref(dsu.unite(u, v), "the edges must not contain a cycle");
        inf.readEoln();
    }
    inf.readEof();
}

#include "testlib.h"

#include <numeric>
#include <set>
#include <utility>
#include <vector>

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readSpace();
    inf.readInt(1, n, "s");
    inf.readSpace();
    inf.readInt(1, n, "t");
    inf.readEoln();
    std::vector<int> parent(n + 1), size(n + 1, 1);
    std::iota(parent.begin(), parent.end(), 0);
    auto root = [&](int v) {
        while (parent[v] != v) {
            parent[v] = parent[parent[v]];
            v = parent[v];
        }
        return v;
    };
    std::set<std::pair<int, int>> edges;
    for (int i = 0; i < n - 1; ++i) {
        const int u = inf.readInt(1, n, "u");
        inf.readSpace();
        const int v = inf.readInt(1, n, "v");
        inf.readEoln();
        ensuref(u != v, "self-loops are forbidden");
        ensuref(edges.insert(std::minmax(u, v)).second, "repeated undirected edge");
        int a = root(u), b = root(v);
        ensuref(a != b, "edges must not contain a cycle");
        if (size[a] < size[b]) std::swap(a, b);
        parent[b] = a;
        size[a] += size[b];
    }
    for (int v = 1; v <= n; ++v)
        ensuref(root(v) == root(1), "tree must be connected");
    inf.readEof();
}

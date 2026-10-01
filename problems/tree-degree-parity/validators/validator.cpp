#include "testlib.h"

#include <numeric>
#include <set>
#include <vector>

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const int n = inf.readInt(1, 200'000, "n");
    inf.readEoln();
    const std::string bits = inf.readToken("[01]+", "s");
    ensuref(static_cast<int>(bits.size()) == n, "s must have length n");
    inf.readEoln();

    std::vector<int> parent(n), size(n, 1);
    std::iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        while (parent[x] != x) {
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    };
    std::set<std::pair<int, int>> seen;
    for (int i = 0; i < n - 1; ++i) {
        const int u = inf.readInt(1, n, "u") - 1;
        inf.readSpace();
        const int v = inf.readInt(1, n, "v") - 1;
        ensuref(u != v, "an edge cannot be a loop");
        auto edge = std::minmax(u, v);
        ensuref(seen.insert(edge).second, "duplicate edge");
        int ru = find(u), rv = find(v);
        ensuref(ru != rv, "the graph contains a cycle");
        if (size[ru] < size[rv]) std::swap(ru, rv);
        parent[rv] = ru;
        size[ru] += size[rv];
        inf.readEoln();
    }
    inf.readEof();
}

#include "testlib_ext.h"

#include <algorithm>
#include <cstdint>
#include <unordered_set>
#include <vector>

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    const int n = inf.readInt();
    const int m = inf.readInt();
    std::unordered_set<std::uint64_t> edges;
    edges.reserve(static_cast<std::size_t>(m) * 2 + 1);
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u = inf.readInt() - 1;
        int v = inf.readInt() - 1;
        if (u > v) std::swap(u, v);
        edges.insert((static_cast<std::uint64_t>(u) << 32) | static_cast<unsigned>(v));
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    // Determine the truth independently so a false FOREST claim is rejected.
    std::vector<int> parent(n, -1), depth(n, 0), iter(n, 0);
    std::vector<char> seen(n, false);
    bool hasCycle = false;
    for (int root = 0; root < n && !hasCycle; ++root) {
        if (seen[root]) continue;
        std::vector<int> stack{root};
        seen[root] = true;
        while (!stack.empty() && !hasCycle) {
            const int v = stack.back();
            if (iter[v] == static_cast<int>(graph[v].size())) {
                stack.pop_back();
                continue;
            }
            const int u = graph[v][iter[v]++];
            if (!seen[u]) {
                seen[u] = true;
                parent[u] = v;
                depth[u] = depth[v] + 1;
                stack.push_back(u);
            } else if (u != parent[v]) {
                hasCycle = true;
            }
        }
    }

    if (ouf.seekEof()) quitf(_wa, "missing result");
    const pattern resultPattern(R"(FOREST|CYCLE)");
    const std::string kind = ouf.readToken(resultPattern, "result");
    if (kind == "FOREST") {
        cp::require_output_eof();
        if (hasCycle) quitf(_wa, "the graph contains a cycle");
        quitf(_ok, "the graph is a forest");
    }
    if (kind != "CYCLE") quitf(_wa, "expected FOREST or CYCLE, found '%s'", kind.c_str());
    if (!hasCycle) quitf(_wa, "the graph is a forest, so no cycle can be output");

    if (ouf.seekEof()) quitf(_wa, "missing cycle length");
    const int k = ouf.readInt(3, n, "cycle_length");
    std::vector<int> cycle(k);
    std::vector<char> used(n, false);
    for (int& v : cycle) {
        if (ouf.seekEof()) quitf(_wa, "cycle witness has fewer than %d vertices", k);
        v = ouf.readInt(1, n, "cycle_vertex") - 1;
        if (used[v]) quitf(_wa, "cycle vertex %d appears more than once", v + 1);
        used[v] = true;
    }
    cp::require_output_eof();
    for (int i = 0; i < k; ++i) {
        int u = cycle[i], v = cycle[(i + 1) % k];
        if (u > v) std::swap(u, v);
        const std::uint64_t key = (static_cast<std::uint64_t>(u) << 32) | static_cast<unsigned>(v);
        if (!edges.count(key)) quitf(_wa, "edge %d-%d is not in the graph", u + 1, v + 1);
    }
    quitf(_ok, "valid simple cycle with %d vertices", k);
}

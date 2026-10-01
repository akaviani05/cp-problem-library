#include <iostream>
#include <vector>

// Wrong: reports every visited-neighbor edge, including the DFS parent edge.
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        std::cin >> u >> v;
        --u; --v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }
    std::vector<char> seen(n, false);
    for (int root = 0; root < n; ++root) {
        if (seen[root]) continue;
        std::vector<int> stack{root};
        seen[root] = true;
        while (!stack.empty()) {
            int v = stack.back();
            stack.pop_back();
            for (int u : graph[v]) {
                if (seen[u]) {
                    std::cout << "CYCLE 2 " << v + 1 << ' ' << u + 1 << '\n';
                    return 0;
                }
                seen[u] = true;
                stack.push_back(u);
            }
        }
    }
    std::cout << "FOREST\n";
}

#include <iostream>
#include <vector>
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
    std::vector<char> visited(n, false);
    int components = 0;
    std::vector<int> stack;
    for (int start = 0; start < n; ++start) {
        if (visited[start]) continue;
        ++components;
        visited[start] = true;
        stack.push_back(start);
        while (!stack.empty()) {
            const int v = stack.back();
            stack.pop_back();
            for (int to : graph[v]) {
                if (!visited[to]) {
                    visited[to] = true;
                    stack.push_back(to);
                }
            }
        }
    }
    std::cout << components << '\n';
}

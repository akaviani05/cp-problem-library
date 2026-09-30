#include <iostream>
#include <queue>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, s, t; std::cin >> n >> s >> t;
    std::vector<std::vector<int>> adj(n + 1);
    for (int i = 1; i < n; ++i) {
        int u, v; std::cin >> u >> v;
        adj[u].push_back(v); adj[v].push_back(u);
    }
    std::vector<int> count(n + 1, -1);
    std::queue<int> q; q.push(s); count[s] = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (count[v] < 0) {
            count[v] = count[u] + 1; q.push(v);
        }
    }
    // Counts vertices instead of edges.
    std::cout << count[t] << '\n';
}

#include <iostream>
#include <queue>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, s, t;
    std::cin >> n >> s >> t;
    std::vector<std::vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; ++i) {
        int u, v; std::cin >> u >> v;
        adj[u].push_back(v); adj[v].push_back(u);
    }
    std::vector<int> distance(n + 1, -1);
    std::queue<int> q;
    q.push(s); distance[s] = 0;
    while (!q.empty()) {
        const int u = q.front(); q.pop();
        for (int v : adj[u]) if (distance[v] == -1) {
            distance[v] = distance[u] + 1;
            q.push(v);
        }
    }
    std::cout << distance[t] << '\n';
}

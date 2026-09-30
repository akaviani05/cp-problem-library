#include <iostream>
#include <cstdlib>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, s, t; std::cin >> n >> s >> t;
    std::vector<std::vector<int>> adj(n + 1);
    for (int i = 1; i < n; ++i) {
        int a, b; std::cin >> a >> b;
        adj[a].push_back(b); adj[b].push_back(a);
    }
    std::vector<int> depth(n + 1, -1), stack{1};
    depth[1] = 0;
    while (!stack.empty()) {
        int u = stack.back(); stack.pop_back();
        for (int v : adj[u]) if (depth[v] < 0) {
            depth[v] = depth[u] + 1; stack.push_back(v);
        }
    }
    // Incorrectly assumes one endpoint is an ancestor of the other.
    std::cout << std::abs(depth[s] - depth[t]) << '\n';
}

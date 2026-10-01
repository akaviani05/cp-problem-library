#include <iostream>
#include <vector>
// Incorrectly assumes the input edge order determines neighbor visitation order.
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, root;
    if (!(std::cin >> n >> root)) return 0;
    std::vector<std::vector<int>> adj(n);
    for (int i = 1, u, v; i < n; ++i) { std::cin >> u >> v; --u; --v; adj[u].push_back(v); adj[v].push_back(u); }
    std::vector<char> seen(n, false);
    std::vector<int> stack{root - 1}, order;
    seen[root - 1] = true;
    while (!stack.empty()) {
        int v = stack.back(); stack.pop_back();
        order.push_back(v + 1);
        for (int u : adj[v]) if (!seen[u]) { seen[u] = true; stack.push_back(u); }
    }
    for (int v : order) std::cout << v << ' ';
    std::cout << '\n';
}

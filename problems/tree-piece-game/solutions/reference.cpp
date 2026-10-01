#include <iostream>
#include <stack>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n, x, y;
    if (!(std::cin >> n >> x >> y)) return 0;
    --x;
    --y;
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i + 1 < n; ++i) {
        int u, v;
        std::cin >> u >> v;
        --u;
        --v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    std::vector<int> color(n, -1);
    std::stack<int> pending;
    color[x] = 0;
    pending.push(x);
    while (!pending.empty()) {
        const int u = pending.top();
        pending.pop();
        for (const int v : graph[u]) {
            if (color[v] == -1) {
                color[v] = color[u] ^ 1;
                pending.push(v);
            }
        }
    }
    std::cout << (color[x] == color[y] ? "Alice\n" : "Bob\n");
}

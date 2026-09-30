#include <iostream>
#include <queue>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, s, t;
    std::cin >> n >> s >> t;
    std::vector<std::vector<int>> edges(n + 1);
    std::vector<int> degree(n + 1, 0);
    for (int i = 1; i < n; ++i) {
        int a, b; std::cin >> a >> b;
        edges[a].push_back(b); edges[b].push_back(a);
        ++degree[a]; ++degree[b];
    }
    if (s == t) { std::cout << 0 << '\n'; return 0; }
    std::queue<int> leaves;
    for (int v = 1; v <= n; ++v)
        if (degree[v] == 1 && v != s && v != t) leaves.push(v);
    std::vector<bool> removed(n + 1, false);
    int remaining = n;
    while (!leaves.empty()) {
        const int leaf = leaves.front(); leaves.pop();
        removed[leaf] = true;
        --remaining;
        for (int neighbor : edges[leaf]) if (!removed[neighbor]) {
            --degree[neighbor];
            if (degree[neighbor] == 1 && neighbor != s && neighbor != t)
                leaves.push(neighbor);
        }
    }
    std::cout << remaining - 1 << '\n';
}

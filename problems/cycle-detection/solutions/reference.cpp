#include <algorithm>
#include <iostream>
#include <queue>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    std::vector<std::vector<int>> forest(n);
    std::vector<int> parent(n), size(n, 1);
    for (int i = 0; i < n; ++i) parent[i] = i;
    auto find = [&](int x) {
        int r = x;
        while (parent[r] != r) r = parent[r];
        while (parent[x] != x) { int p = parent[x]; parent[x] = r; x = p; }
        return r;
    };
    for (int i = 0; i < m; ++i) {
        int u, v;
        std::cin >> u >> v;
        --u; --v;
        int a = find(u), b = find(v);
        if (a == b) {
            std::vector<int> prev(n, -1);
            std::queue<int> q;
            prev[u] = u;
            q.push(u);
            while (!q.empty() && prev[v] == -1) {
                int x = q.front(); q.pop();
                for (int y : forest[x]) if (prev[y] == -1) {
                    prev[y] = x;
                    q.push(y);
                }
            }
            std::vector<int> path;
            for (int x = v; x != u; x = prev[x]) path.push_back(x);
            path.push_back(u);
            std::reverse(path.begin(), path.end());
            std::cout << "CYCLE " << path.size();
            for (int x : path) std::cout << ' ' << x + 1;
            std::cout << '\n';
            return 0;
        }
        if (size[a] < size[b]) std::swap(a, b);
        parent[b] = a;
        size[a] += size[b];
        forest[u].push_back(v);
        forest[v].push_back(u);
    }
    std::cout << "FOREST\n";
}

#include <iostream>
#include <numeric>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    std::vector<int> parent(n), size(n, 1);
    std::iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        while (parent[x] != x) {
            const int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    };
    int components = n;
    for (int i = 0; i < m; ++i) {
        int u, v;
        std::cin >> u >> v;
        const int a = find(u - 1), b = find(v - 1);
        if (a != b) {
            if (size[a] < size[b]) {
                parent[a] = b;
                size[b] += size[a];
            } else {
                parent[b] = a;
                size[a] += size[b];
            }
            --components;
        }
    }
    std::cout << components << '\n';
}

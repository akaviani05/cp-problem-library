#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;
    std::string bits;
    std::cin >> bits;
    std::vector<std::vector<std::pair<int, int>>> graph(n);
    for (int id = 0; id < n - 1; ++id) {
        int u, v;
        std::cin >> u >> v;
        --u;
        --v;
        graph[u].push_back({v, id});
        graph[v].push_back({u, id});
    }

    int total_parity = 0;
    for (char bit : bits) total_parity ^= bit - '0';
    if (total_parity != 0) {
        std::cout << "NO\n";
        return 0;
    }

    std::vector<int> parent(n, -1), parent_edge(n, -1), order;
    order.reserve(n);
    std::vector<int> stack{0};
    parent[0] = 0;
    while (!stack.empty()) {
        int v = stack.back();
        stack.pop_back();
        order.push_back(v);
        for (auto [to, id] : graph[v]) {
            if (parent[to] != -1) continue;
            parent[to] = v;
            parent_edge[to] = id;
            stack.push_back(to);
        }
    }

    std::vector<int> need(n);
    for (int v = 0; v < n; ++v) need[v] = bits[v] - '0';
    std::vector<int> chosen;
    for (int i = n - 1; i > 0; --i) {
        int v = order[i];
        if (need[v]) {
            chosen.push_back(parent_edge[v]);
            need[parent[v]] ^= 1;
        }
    }
    std::cout << "YES\n" << chosen.size() << '\n';
    for (int id : chosen) std::cout << id + 1 << ' ';
    std::cout << '\n';
}

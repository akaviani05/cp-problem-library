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
    std::vector<int> edge_u(n - 1), edge_v(n - 1);
    for (int id = 0; id < n - 1; ++id) {
        std::cin >> edge_u[id] >> edge_v[id];
        --edge_u[id];
        --edge_v[id];
        graph[edge_u[id]].push_back({edge_v[id], id});
        graph[edge_v[id]].push_back({edge_u[id], id});
    }

    std::vector<int> parent(n, -1), order{0};
    parent[0] = 0;
    for (int at = 0; at < static_cast<int>(order.size()); ++at) {
        int v = order[at];
        for (auto [to, id] : graph[v]) {
            (void)id;
            if (parent[to] != -1) continue;
            parent[to] = v;
            order.push_back(to);
        }
    }

    std::vector<int> subtree_xor(n);
    int all = 0;
    for (int v = 0; v < n; ++v) {
        subtree_xor[v] = bits[v] - '0';
        all ^= subtree_xor[v];
    }
    if (all) {
        std::cout << "NO\n";
        return 0;
    }

    std::vector<int> chosen;
    for (int i = n - 1; i > 0; --i) {
        int v = order[i];
        if (subtree_xor[v]) {
            for (auto [to, id] : graph[v]) {
                if (to == parent[v]) {
                    chosen.push_back(id);
                    break;
                }
            }
        }
        subtree_xor[parent[v]] ^= subtree_xor[v];
    }
    std::cout << "YES\n" << chosen.size() << '\n';
    for (int id : chosen) std::cout << id + 1 << ' ';
    std::cout << '\n';
}

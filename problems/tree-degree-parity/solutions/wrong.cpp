#include <iostream>
#include <string>
#include <vector>

// Misconception: selecting every edge incident to a target-odd vertex works.
int main() {
    int n;
    std::cin >> n;
    std::string bits;
    std::cin >> bits;
    std::vector<std::pair<int, int>> edges(n - 1);
    for (auto& [u, v] : edges) std::cin >> u >> v;

    int parity = 0;
    for (char bit : bits) parity ^= bit - '0';
    if (parity) {
        std::cout << "NO\n";
        return 0;
    }
    std::vector<int> chosen;
    for (int id = 0; id < n - 1; ++id) {
        auto [u, v] = edges[id];
        if (bits[u - 1] == '1' || bits[v - 1] == '1') chosen.push_back(id + 1);
    }
    std::cout << "YES\n" << chosen.size() << '\n';
    for (int id : chosen) std::cout << id << ' ';
    std::cout << '\n';
}

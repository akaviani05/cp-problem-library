#include <algorithm>
#include <iostream>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, r;
    if (!(std::cin >> n >> r)) return 0;
    std::vector<std::vector<int>> g(n);
    for (int i = 1, u, v; i < n; ++i) { std::cin >> u >> v; --u; --v; g[u].push_back(v); g[v].push_back(u); }
    for (auto& a : g) std::sort(a.begin(), a.end());
    std::vector<char> seen(n, false);
    std::vector<int> st{r - 1}, order;
    seen[r - 1] = true;
    while (!st.empty()) {
        int v = st.back(); st.pop_back();
        order.push_back(v + 1);
        for (auto it = g[v].rbegin(); it != g[v].rend(); ++it) if (!seen[*it]) { seen[*it] = true; st.push_back(*it); }
    }
    for (int i = 0; i < n; ++i) std::cout << order[i] << (i + 1 == n ? '\n' : ' ');
}

#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        std::cin >> u >> v;
        --u; --v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    std::vector<int> parent(n, -1), next(n, 0), mark(n, 0);
    int stamp = 0;
    for (int root = 0; root < n; ++root) {
        if (parent[root] != -1) continue;
        std::vector<int> stack{root};
        parent[root] = root;
        mark[root] = ++stamp;
        while (!stack.empty()) {
            int v = stack.back();
            if (next[v] == static_cast<int>(graph[v].size())) {
                mark[v] = -1;
                stack.pop_back();
                continue;
            }
            int u = graph[v][next[v]++];
            if (parent[u] == -1) {
                parent[u] = v;
                mark[u] = stamp;
                stack.push_back(u);
            } else if (u != parent[v]) {
                std::vector<int> chainV, chainU;
                ++stamp;
                int x = v;
                while (true) {
                    mark[x] = stamp;
                    chainV.push_back(x);
                    if (x == parent[x]) break;
                    x = parent[x];
                }
                x = u;
                while (mark[x] != stamp) {
                    chainU.push_back(x);
                    x = parent[x];
                }
                const int lca = x;
                std::vector<int> cycle;
                for (int a : chainV) {
                    cycle.push_back(a);
                    if (a == lca) break;
                }
                std::reverse(chainU.begin(), chainU.end());
                cycle.insert(cycle.end(), chainU.begin(), chainU.end());
                std::cout << "CYCLE " << cycle.size();
                for (int a : cycle) std::cout << ' ' << a + 1;
                std::cout << '\n';
                return 0;
            }
        }
    }
    std::cout << "FOREST\n";
}

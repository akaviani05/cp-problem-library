#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    if (!(cin >> n >> m)) return 0;
    vector<vector<int>> adj(n);
    for (int i = 0, a, b; i < m; ++i) {
        cin >> a >> b; --a; --b;
        adj[a].push_back(b); adj[b].push_back(a);
    }
    vector<int> side(n, -1), par(n, -1), level(n, 0);
    for (int root = 0; root < n; ++root) {
        if (side[root] != -1) continue;
        vector<int> stack{root};
        side[root] = 0;
        while (!stack.empty()) {
            int u = stack.back(); stack.pop_back();
            for (int v : adj[u]) {
                if (side[v] == -1) {
                    side[v] = side[u] ^ 1;
                    par[v] = u;
                    level[v] = level[u] + 1;
                    stack.push_back(v);
                } else if (side[v] == side[u]) {
                    int x = u, y = v;
                    vector<int> path_x{u}, path_y{v};
                    while (level[x] > level[y]) { x = par[x]; path_x.push_back(x); }
                    while (level[y] > level[x]) { y = par[y]; path_y.push_back(y); }
                    while (x != y) {
                        x = par[x]; y = par[y];
                        path_x.push_back(x); path_y.push_back(y);
                    }
                    path_x.pop_back();
                    reverse(path_y.begin(), path_y.end());
                    path_x.insert(path_x.end(), path_y.begin(), path_y.end());
                    cout << "NO\n" << path_x.size() << '\n';
                    for (int w : path_x) cout << w + 1 << ' ';
                    cout << '\n';
                    return 0;
                }
            }
        }
    }
    cout << "YES\n";
    for (int x : side) cout << x << ' ';
    cout << '\n';
}

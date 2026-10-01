#include <iostream>
#include <vector>
#include <queue>
using namespace std;

// Wrong: only searches the connected component containing vertex 1.
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    if (!(cin >> n >> m)) return 0;
    vector<vector<int>> g(n);
    for (int i = 0, u, v; i < m; ++i) {
        cin >> u >> v; --u; --v;
        g[u].push_back(v); g[v].push_back(u);
    }
    vector<int> color(n, 0);
    queue<int> q;
    vector<char> seen(n, false);
    seen[0] = true; q.push(0);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : g[u]) {
            if (!seen[v]) { seen[v] = true; color[v] = color[u] ^ 1; q.push(v); }
            else if (color[v] == color[u]) {
                cout << "NO\n3\n1 2 3\n";
                return 0;
            }
        }
    }
    cout << "YES\n";
    for (int x : color) cout << x << ' ';
    cout << '\n';
}

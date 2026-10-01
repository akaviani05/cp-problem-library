#include <bits/stdc++.h>
using namespace std;

vector<int> make_cycle(int u, int v, const vector<int>& parent,
                       const vector<int>& depth) {
    int a = u, b = v;
    vector<int> left{a}, right{b};
    while (depth[a] > depth[b]) { a = parent[a]; left.push_back(a); }
    while (depth[b] > depth[a]) { b = parent[b]; right.push_back(b); }
    while (a != b) {
        a = parent[a]; b = parent[b];
        left.push_back(a); right.push_back(b);
    }
    left.pop_back();
    reverse(right.begin(), right.end());
    left.insert(left.end(), right.begin(), right.end());
    return left;
}

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
    vector<int> color(n, -1), parent(n, -1), depth(n);
    for (int s = 0; s < n; ++s) if (color[s] == -1) {
        queue<int> q;
        color[s] = 0; q.push(s);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : g[u]) {
                if (color[v] == -1) {
                    color[v] = color[u] ^ 1;
                    parent[v] = u; depth[v] = depth[u] + 1; q.push(v);
                } else if (color[v] == color[u]) {
                    vector<int> cycle = make_cycle(u, v, parent, depth);
                    cout << "NO\n" << cycle.size() << '\n';
                    for (int x : cycle) cout << x + 1 << ' ';
                    cout << '\n';
                    return 0;
                }
            }
        }
    }
    cout << "YES\n";
    for (int x : color) cout << x << ' ';
    cout << '\n';
}

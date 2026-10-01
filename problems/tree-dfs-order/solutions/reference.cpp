#include <algorithm>
#include <iostream>
#include <vector>
struct Frame { int vertex; std::size_t next; };
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, root;
    if (!(std::cin >> n >> root)) return 0;
    --root;
    std::vector<std::vector<int>> adj(n);
    for (int i = 0, a, b; i < n - 1; ++i) { std::cin >> a >> b; --a; --b; adj[a].push_back(b); adj[b].push_back(a); }
    for (auto& neighbors : adj) std::sort(neighbors.begin(), neighbors.end());
    std::vector<unsigned char> visited(n, 0);
    std::vector<int> answer{root};
    std::vector<Frame> callStack{{root, 0}};
    visited[root] = 1;
    while (!callStack.empty()) {
        Frame& f = callStack.back();
        if (f.next == adj[f.vertex].size()) { callStack.pop_back(); continue; }
        int child = adj[f.vertex][f.next++];
        if (visited[child]) continue;
        visited[child] = 1;
        answer.push_back(child);
        callStack.push_back({child, 0});
    }
    for (int v : answer) std::cout << v + 1 << ' ';
    std::cout << '\n';
}

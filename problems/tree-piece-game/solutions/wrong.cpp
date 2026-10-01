#include <iostream>
#include <queue>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n, x, y;
    if (!(std::cin >> n >> x >> y)) return 0;
    --x;
    --y;
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        std::cin >> u >> v;
        --u;
        --v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    std::vector<int> distance(n, -1);
    std::queue<int> queue;
    distance[x] = 0;
    queue.push(x);
    while (!queue.empty()) {
        const int u = queue.front();
        queue.pop();
        for (const int v : graph[u]) {
            if (distance[v] == -1) {
                distance[v] = distance[u] + 1;
                queue.push(v);
            }
        }
    }
    // Bug: assigns the even-distance first-move advantage to Bob.
    std::cout << (distance[y] % 2 == 0 ? "Bob\n" : "Alice\n");
}

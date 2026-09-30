#include "testlib.h"

#include <queue>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const int n = opt<int>(2);
    const std::string query = opt<std::string>(3);
    const std::string labels = opt<std::string>(4);
    ensuref(1 <= n && n <= 200'000, "n out of bounds");
    std::vector<std::pair<int, int>> edges;
    std::vector<std::vector<int>> adj(n);
    for (int v = 1; v < n; ++v) {
        int p;
        if (mode == "chain") p = v - 1;
        else if (mode == "star") p = 0;
        else if (mode == "balanced") p = (v - 1) / 2;
        else if (mode == "broom") p = v < n / 2 ? v - 1 : std::max(0, n / 2 - 1);
        else if (mode == "random") p = rnd.next(0, v - 1);
        else quitf(_fail, "unknown mode");
        edges.emplace_back(p, v);
        adj[p].push_back(v);
        adj[v].push_back(p);
    }
    auto farthest = [&](int start) {
        std::vector<int> distance(n, -1);
        std::queue<int> q;
        q.push(start);
        distance[start] = 0;
        int best = start;
        while (!q.empty()) {
            const int u = q.front(); q.pop();
            if (distance[u] > distance[best]) best = u;
            for (int v : adj[u]) if (distance[v] < 0) {
                distance[v] = distance[u] + 1;
                q.push(v);
            }
        }
        return best;
    };
    int s = 0, t = 0;
    if (query == "ends") { s = farthest(0); t = farthest(s); }
    else if (query == "same") { s = t = rnd.next(0, n - 1); }
    else if (query == "random") { s = rnd.next(0, n - 1); t = rnd.next(0, n - 1); }
    else if (query == "near") {
        if (!edges.empty()) {
            const auto e = edges[rnd.next(0, static_cast<int>(edges.size()) - 1)];
            s = e.first; t = e.second;
        }
    } else quitf(_fail, "unknown query");
    std::vector<int> permutation(n);
    for (int v = 0; v < n; ++v) permutation[v] = v;
    if (labels == "shuffled") permutation = rnd.perm(n);
    else ensuref(labels == "plain", "unknown labels");
    shuffle(edges.begin(), edges.end());
    println(n, permutation[s] + 1, permutation[t] + 1);
    for (auto e : edges) {
        if (rnd.next(0, 1)) std::swap(e.first, e.second);
        println(permutation[e.first] + 1, permutation[e.second] + 1);
    }
}

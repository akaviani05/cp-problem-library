#include "testlib_ext.h"
#include <set>

static int read_output_int(const char* name) {
    const std::string token = ouf.readToken(pattern(R"([+-]?[0-9]+)"), name);
    try {
        size_t used = 0;
        const long long value = std::stoll(token, &used);
        if (used != token.size() || value < INT_MIN || value > INT_MAX)
            quitf(_wa, "%s is outside the supported integer range", name);
        return static_cast<int>(value);
    } catch (...) {
        quitf(_wa, "%s is not a valid integer", name);
    }
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    const int n = inf.readInt();
    const int m = inf.readInt();
    std::vector<std::vector<int>> graph(n);
    std::set<std::pair<int, int>> edges;
    for (int i = 0; i < m; ++i) {
        const int u = inf.readInt() - 1;
        const int v = inf.readInt() - 1;
        graph[u].push_back(v);
        graph[v].push_back(u);
        edges.insert(std::minmax(u, v));
    }

    const std::string kind = ouf.readToken(pattern(R"([A-Za-z]+)"), "answer_type");
    if (kind == "YES") {
        std::vector<int> color(n);
        for (int i = 0; i < n; ++i) {
            color[i] = read_output_int("color");
            if (color[i] != 0 && color[i] != 1)
                quitf(_wa, "color of vertex %d must be 0 or 1", i + 1);
        }
        cp::require_output_eof();
        for (int u = 0; u < n; ++u)
            for (int v : graph[u])
                if (color[u] == color[v])
                    quitf(_wa, "edge %d-%d has equal endpoint colors", u + 1, v + 1);
        quitf(_ok, "valid bipartite coloring");
    }

    if (kind == "NO") {
        const int k = read_output_int("cycle length");
        if (k < 3 || k > n || k % 2 == 0)
            quitf(_wa, "cycle length must be odd and between 3 and n");
        std::vector<int> cycle(k);
        std::vector<unsigned char> seen(n, false);
        for (int& v : cycle) {
            const int raw_vertex = read_output_int("cycle vertex");
            if (raw_vertex < 1 || raw_vertex > n)
                quitf(_wa, "cycle vertex is outside 1..n");
            v = raw_vertex - 1;
            if (seen[v]) quitf(_wa, "cycle vertices must be distinct");
            seen[v] = true;
        }
        cp::require_output_eof();
        for (int i = 0; i < k; ++i) {
            const int u = cycle[i], v = cycle[(i + 1) % k];
            if (!edges.count(std::minmax(u, v)))
                quitf(_wa, "cycle edge %d-%d is absent", u + 1, v + 1);
        }
        quitf(_ok, "valid simple odd cycle of length %d", k);
    }
    quitf(_wa, "first token must be YES or NO");
}

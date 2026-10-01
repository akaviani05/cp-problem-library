#include "testlib_ext.h"

#include <string>
#include <vector>

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    const int n = inf.readInt();
    inf.readEoln();
    const std::string bits = inf.readToken();
    inf.readEoln();
    int parity_sum = 0;
    for (char bit : bits) parity_sum ^= bit - '0';
    std::vector<int> edge_u(n - 1), edge_v(n - 1);
    for (int i = 0; i < n - 1; ++i) {
        edge_u[i] = inf.readInt() - 1;
        inf.readSpace();
        edge_v[i] = inf.readInt() - 1;
        inf.readEoln();
    }
    inf.readEof();

    const std::string verdict = ouf.readToken("(YES|NO)", "verdict");
    if (verdict == "NO") {
        cp::require_output_eof();
        if (parity_sum == 0)
            quitf(_wa, "a valid edge subset exists, but the output says NO");
        quitf(_ok, "the requested parities have odd sum, so no subset exists");
    }
    if (parity_sum != 0)
        quitf(_wa, "the requested parities have odd sum, so no subset exists");

    const int count = ouf.readInt(0, n - 1, "selected_edge_count");
    std::vector<char> selected(n - 1, false);
    std::vector<int> degree_parity(n, 0);
    for (int i = 0; i < count; ++i) {
        const int id = ouf.readInt(1, n - 1, "edge_index") - 1;
        if (selected[id]) quitf(_wa, "edge %d is listed more than once", id + 1);
        selected[id] = true;
        degree_parity[edge_u[id]] ^= 1;
        degree_parity[edge_v[id]] ^= 1;
    }
    cp::require_output_eof();
    for (int v = 0; v < n; ++v) {
        if (degree_parity[v] != bits[v] - '0')
            quitf(_wa, "vertex %d has the wrong selected-degree parity", v + 1);
    }
    quitf(_ok, "the selected edges realize all requested degree parities");
}

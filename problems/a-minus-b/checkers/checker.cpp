#include "testlib_ext.h"

// Compares an exact sequence of tokens, ignoring whitespace.
int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    // Tokens contain no spaces. Name both streams for Polygon diagnostics.
    const pattern token(R"([^\ ]+)");
    int count = 0;
    while (!ans.seekEof()) {
        const std::string expected = ans.readToken(token, "answer_token");
        if (ouf.seekEof())
            quitf(_wa, "missing token %d", count + 1);
        const std::string actual = ouf.readToken(token, "output_token");
        ++count;
        if (actual != expected)
            quitf(_wa, "token %d differs: expected '%s', found '%s'", count,
                  expected.c_str(), actual.c_str());
    }
    cp::require_output_eof();
    quitf(_ok, "%d tokens match", count);
}

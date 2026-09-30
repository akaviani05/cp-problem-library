#include "testlib_ext.h"
#include <limits>

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    const long long minimum = std::numeric_limits<long long>::min();
    const long long maximum = std::numeric_limits<long long>::max();
    const long long expected = ans.readLong(minimum, maximum, "jury_sum");
    const long long actual = ouf.readLong(minimum, maximum, "sum");
    if (expected != actual)
        quitf(_wa, "expected %lld, found %lld", expected, actual);
    cp::require_output_eof();
    quitf(_ok, "sum is %lld", expected);
}

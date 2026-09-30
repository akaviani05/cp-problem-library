#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const long long limit = 1'000'000'000'000'000'000LL;
    inf.readLong(-limit, limit, "a");
    inf.readSpace();
    inf.readLong(-limit, limit, "b");
    inf.readEoln();
    inf.readEof();
}

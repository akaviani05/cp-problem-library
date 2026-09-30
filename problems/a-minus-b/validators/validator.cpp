#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    const long long bound = 1'000'000'000'000'000'000LL;
    inf.readLong(-bound, bound, "a");
    inf.readSpace();
    inf.readLong(-bound, bound, "b");
    inf.readEoln();
    inf.readEof();
}

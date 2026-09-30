#include "testlib.h"

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const long long bound = 1'000'000'000'000'000'000LL;
    const std::string mode = opt<std::string>(1);
    if (mode == "boundary") {
        const int index = opt<int>(2);
        ensuref(0 <= index && index < 9, "boundary index must be in [0, 8]");
        const long long values[] = {-bound, 0, bound};
        println(values[index / 3], values[index % 3]);
    } else if (mode == "fixed") {
        const long long a = opt<long long>(2);
        const long long b = opt<long long>(3);
        ensuref(-bound <= a && a <= bound && -bound <= b && b <= bound,
                "fixed operands must satisfy the bounds");
        println(a, b);
    } else if (mode == "random") {
        const long long limit = opt<long long>(2);
        ensuref(0 <= limit && limit <= bound, "random limit must be in [0, 10^18]");
        println(rnd.next(-limit, limit), rnd.next(-limit, limit));
    } else if (mode == "equal") {
        const long long a = rnd.next(-bound, bound);
        println(a, a);
    } else {
        quitf(_fail, "unknown generator mode: %s", mode.c_str());
    }
}

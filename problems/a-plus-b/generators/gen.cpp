#include "testlib.h"

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    const std::string mode = opt<std::string>(1);
    const long long limit = 1000000000000000000LL;
    long long a, b;
    if (mode == "fixed") {
        a = opt<long long>(2);
        b = opt<long long>(3);
    } else if (mode == "random") {
        a = rnd.next(-limit, limit);
        b = rnd.next(-limit, limit);
    } else if (mode == "small") {
        a = rnd.next(-100LL, 100LL);
        b = rnd.next(-100LL, 100LL);
    } else if (mode == "cancel") {
        a = rnd.next(-limit, limit);
        b = -a;
    } else {
        quitf(_fail, "unknown generator mode: %s", mode.c_str());
    }
    ensuref(-limit <= a && a <= limit && -limit <= b && b <= limit,
            "generated integers exceed the constraints");
    println(a, b);
}

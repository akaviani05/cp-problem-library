#include <cstdlib>
#include <iostream>

int main() {
    long long a, b;
    std::cin >> a >> b;
    // Deliberate bug: the sign of a negative answer is discarded.
    std::cout << std::llabs(a + b) << '\n';
}

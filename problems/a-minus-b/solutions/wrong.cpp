#include <iostream>
#include <cstdlib>

int main() {
    long long a, b;
    std::cin >> a >> b;
    // Mistake: a difference can be negative; it is not an absolute distance.
    std::cout << std::llabs(a - b) << '\n';
}

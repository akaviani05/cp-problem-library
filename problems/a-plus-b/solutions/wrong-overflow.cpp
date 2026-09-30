#include <iostream>

int main() {
    long long a, b;
    std::cin >> a >> b;
    // Deliberate bug: the answer is truncated to a 32-bit integer.
    std::cout << static_cast<int>(a + b) << '\n';
}

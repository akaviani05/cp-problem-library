#include <iostream>

int main() {
    long long a, b;
    std::cin >> a >> b;
    // Offset both operands so all intermediate sums are nonnegative.
    constexpr long long limit = 1000000000000000000LL;
    const long long shifted_sum = (a + limit) + (b + limit);
    std::cout << shifted_sum - 2 * limit << '\n';
}

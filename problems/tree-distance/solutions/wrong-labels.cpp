#include <cstdlib>
#include <iostream>
int main() {
    int n, s, t; std::cin >> n >> s >> t;
    // Vertex labels do not encode positions on a path.
    std::cout << std::abs(s - t) << '\n';
}

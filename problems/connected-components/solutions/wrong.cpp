#include <iostream>
int main() {
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    // Mistakenly assumes every edge joins two previously separate components.
    std::cout << n - m << '\n';
}

#include <iostream>
#include <algorithm>
#include <string>

struct Decimal {
    bool negative;
    std::string magnitude;
};

Decimal parse(const std::string& token) {
    const bool negative = token[0] == '-';
    return {negative, token.substr(negative ? 1 : 0)};
}

std::string add_magnitudes(const std::string& a, const std::string& b) {
    std::string result;
    int i = static_cast<int>(a.size()) - 1;
    int j = static_cast<int>(b.size()) - 1;
    int carry = 0;
    while (i >= 0 || j >= 0 || carry) {
        int value = carry;
        if (i >= 0) value += a[i--] - '0';
        if (j >= 0) value += b[j--] - '0';
        result += static_cast<char>('0' + value % 10);
        carry = value / 10;
    }
    std::reverse(result.begin(), result.end());
    return result;
}

// The caller guarantees a >= b when interpreted as nonnegative integers.
std::string subtract_magnitudes(const std::string& a, const std::string& b) {
    std::string result;
    int j = static_cast<int>(b.size()) - 1;
    int borrow = 0;
    for (int i = static_cast<int>(a.size()) - 1; i >= 0; --i) {
        int value = a[i] - '0' - borrow;
        if (j >= 0) value -= b[j--] - '0';
        borrow = value < 0;
        if (borrow) value += 10;
        result += static_cast<char>('0' + value);
    }
    while (result.size() > 1 && result.back() == '0') result.pop_back();
    std::reverse(result.begin(), result.end());
    return result;
}

bool smaller(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return a.size() < b.size();
    return a < b;
}

int main() {
    std::string a_token, b_token;
    std::cin >> a_token >> b_token;
    Decimal a = parse(a_token);
    Decimal b = parse(b_token);
    if (b.magnitude != "0") b.negative = !b.negative;

    bool negative;
    std::string magnitude;
    if (a.negative == b.negative) {
        magnitude = add_magnitudes(a.magnitude, b.magnitude);
        negative = a.negative;
    } else if (smaller(a.magnitude, b.magnitude)) {
        magnitude = subtract_magnitudes(b.magnitude, a.magnitude);
        negative = b.negative;
    } else {
        magnitude = subtract_magnitudes(a.magnitude, b.magnitude);
        negative = a.negative;
    }
    if (negative && magnitude != "0") std::cout << '-';
    std::cout << magnitude << '\n';
}

"""Exhaust all small signed pairs, then exercise decimal carries and borrows."""
import json

cases = [f"{a} {b}\n" for a in range(-10, 11) for b in range(-10, 11)]
for power in (10, 100, 1000, 10**9, 10**18):
    for a, b in ((power, 1), (-power, 1), (1, power), (1, -power),
                 (power - 1, -1), (-power + 1, 1)):
        case = f"{a} {b}\n"
        if case not in cases:
            cases.append(case)
print(json.dumps(cases))

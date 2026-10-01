"""Emit reproducible small trees with feasible and infeasible parity vectors."""
import json
import random


def make_case(rng: random.Random, case_id: int) -> str:
    n = 1 + (case_id % 12)
    shape = case_id % 3
    if shape == 0:
        edges = [(v - 1, v) for v in range(1, n)]
    elif shape == 1:
        edges = [(0, v) for v in range(1, n)]
    else:
        edges = [(v, rng.randrange(v)) for v in range(1, n)]
    rng.shuffle(edges)

    bits = [rng.randrange(2) for _ in range(n)]
    parity = sum(bits) & 1
    if case_id % 2 == 0:
        if parity:
            bits[rng.randrange(n)] ^= 1
    elif not parity:
        bits[rng.randrange(n)] ^= 1

    lines = [str(n), "".join(map(str, bits))]
    lines.extend(f"{u + 1} {v + 1}" for u, v in edges)
    return "\n".join(lines) + "\n"


def main() -> None:
    rng = random.Random(20260930)
    print(json.dumps([make_case(rng, i) for i in range(500)]))


if __name__ == "__main__":
    main()

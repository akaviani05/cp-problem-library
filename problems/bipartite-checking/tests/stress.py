"""Exhaustive very small graphs and fixed-seed random simple graphs."""
import itertools
import json
import random

cases = []
for n in range(1, 5):
    possible = list(itertools.combinations(range(1, n + 1), 2))
    for mask in range(1 << len(possible)):
        edges = [e for i, e in enumerate(possible) if mask >> i & 1]
        lines = [f"{n} {len(edges)}"]
        lines.extend(f"{u} {v}" for u, v in edges)
        cases.append("\n".join(lines) + "\n")

rng = random.Random(9023)
for _ in range(250):
    n = rng.randint(1, 9)
    possible = list(itertools.combinations(range(1, n + 1), 2))
    rng.shuffle(possible)
    m = rng.randint(0, min(len(possible), 2 * n + 3))
    edges = possible[:m]
    lines = [f"{n} {m}"]
    lines.extend(f"{u} {v}" for u, v in edges)
    cases.append("\n".join(lines) + "\n")

print(json.dumps(cases))

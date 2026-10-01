"""Deterministic small graphs covering forests, cycles, and disconnected cases."""
import json
import random

rng = random.Random(902301)
cases = ["1 0\n", "2 1\n1 2\n", "3 3\n1 2\n2 3\n3 1\n"]
for _ in range(400):
    n = rng.randint(1, 10)
    possible = [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1)]
    rng.shuffle(possible)
    m = rng.randint(0, min(len(possible), 2 * n + 3))
    edges = possible[:m]
    rng.shuffle(edges)
    lines = [f"{n} {m}"] + [f"{u} {v}" for u, v in edges]
    cases.append("\n".join(lines) + "\n")
print(json.dumps(cases))

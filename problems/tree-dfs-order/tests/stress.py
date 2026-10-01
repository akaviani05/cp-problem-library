#!/usr/bin/env python3
"""Deterministic small random trees with shuffled labels and edge order."""
import json
import random

rng = random.Random(9023)
cases = ["1 1\n", "4 1\n1 4\n1 3\n1 2\n"]
for _ in range(250):
    n = rng.randint(1, 24)
    edges = [(v, rng.randrange(v)) for v in range(1, n)]
    labels = list(range(n))
    rng.shuffle(labels)
    mapped = [(labels[u], labels[v]) for u, v in edges]
    rng.shuffle(mapped)
    for i, (u, v) in enumerate(mapped):
        if rng.randrange(2):
            mapped[i] = (v, u)
    root = labels[rng.randrange(n)]
    text = f"{n} {root + 1}\n" + "".join(f"{u + 1} {v + 1}\n" for u, v in mapped)
    cases.append(text)
print(json.dumps(cases))

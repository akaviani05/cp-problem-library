"""Exhaust all labelled trees through n=4, then use deterministic random trees."""
import heapq
import itertools
import json
import random

rng = random.Random(20300930)
cases = []

def add_case(n, s, t, edges):
    shuffled = list(edges)
    rng.shuffle(shuffled)
    shuffled = [(v, u) if rng.randrange(2) else (u, v) for u, v in shuffled]
    cases.append(f"{n} {s} {t}\n" + "".join(f"{u} {v}\n" for u, v in shuffled))

add_case(1, 1, 1, [])
for n in range(2, 5):
    for code in itertools.product(range(1, n + 1), repeat=n - 2):
        degree = [0] + [1] * n
        for v in code:
            degree[v] += 1
        leaves = [v for v in range(1, n + 1) if degree[v] == 1]
        heapq.heapify(leaves)
        edges = []
        for v in code:
            leaf = heapq.heappop(leaves)
            edges.append((leaf, v))
            degree[v] -= 1
            if degree[v] == 1:
                heapq.heappush(leaves, v)
        edges.append(tuple(leaves))
        for s in range(1, n + 1):
            for t in range(1, n + 1):
                add_case(n, s, t, edges)
for _ in range(250):
    n = rng.randint(2, 40)
    labels = list(range(1, n + 1))
    rng.shuffle(labels)
    edges = [(labels[v], labels[rng.randrange(v)]) for v in range(1, n)]
    s, t = rng.randint(1, n), rng.randint(1, n)
    add_case(n, s, t, edges)
print(json.dumps(cases))

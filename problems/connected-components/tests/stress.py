"""Exhaust every simple graph on at most five vertices."""
import json

cases = []
for n in range(1, 6):
    possible = [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1)]
    for mask in range(1 << len(possible)):
        edges = [edge for bit, edge in enumerate(possible) if (mask >> bit) & 1]
        lines = [f"{n} {len(edges)}"]
        lines.extend(f"{u} {v}" for u, v in edges)
        cases.append("\n".join(lines) + "\n")
print(json.dumps(cases))

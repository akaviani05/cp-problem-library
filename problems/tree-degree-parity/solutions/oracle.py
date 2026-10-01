#!/usr/bin/env python3
"""Independent oracle using repeated leaf elimination."""
import sys
from collections import deque


def main() -> None:
    tokens = sys.stdin.buffer.read().split()
    n = int(tokens[0])
    bits = tokens[1].decode()
    edges = [(int(tokens[i]) - 1, int(tokens[i + 1]) - 1)
             for i in range(2, len(tokens), 2)]
    total = 0
    for bit in bits:
        total ^= ord(bit) - ord("0")
    if total:
        print("NO")
        return

    graph = [[] for _ in range(n)]
    degree = [0] * n
    for edge_id, (u, v) in enumerate(edges):
        graph[u].append((v, edge_id))
        graph[v].append((u, edge_id))
        degree[u] += 1
        degree[v] += 1
    need = [ord(bit) - ord("0") for bit in bits]
    alive = [True] * n
    leaves = deque(v for v in range(n) if degree[v] <= 1)
    chosen = []
    while leaves:
        v = leaves.popleft()
        if not alive[v] or degree[v] == 0:
            continue
        p, edge_id = next((to, eid) for to, eid in graph[v] if alive[to])
        if need[v]:
            chosen.append(edge_id)
            need[p] ^= 1
        alive[v] = False
        degree[v] = 0
        degree[p] -= 1
        if degree[p] == 1:
            leaves.append(p)

    print("YES")
    print(len(chosen))
    print(*(edge_id + 1 for edge_id in chosen))


if __name__ == "__main__":
    main()

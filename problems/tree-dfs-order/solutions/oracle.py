#!/usr/bin/env python3
"""Independent iterative simulation of recursive, increasing-neighbor DFS."""
import sys

data = list(map(int, sys.stdin.buffer.read().split()))
if not data:
    raise SystemExit
n, root = data[0], data[1] - 1
adj = [[] for _ in range(n)]
for i in range(2, len(data), 2):
    u, v = data[i] - 1, data[i + 1] - 1
    adj[u].append(v)
    adj[v].append(u)
for neighbors in adj:
    neighbors.sort()
seen = [False] * n
seen[root] = True
order = [root + 1]
frames = [[root, 0]]
while frames:
    v, i = frames[-1]
    if i == len(adj[v]):
        frames.pop()
        continue
    frames[-1][1] += 1
    u = adj[v][i]
    if not seen[u]:
        seen[u] = True
        order.append(u + 1)
        frames.append([u, 0])
sys.stdout.write(" ".join(map(str, order)) + "\n")

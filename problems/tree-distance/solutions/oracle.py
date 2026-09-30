"""Root at vertex 1, then climb both endpoints to their common ancestor."""
import sys

values = iter(map(int, sys.stdin.buffer.read().split()))
n, s, t = next(values), next(values), next(values)
adj = [[] for _ in range(n + 1)]
for _ in range(n - 1):
    u, v = next(values), next(values)
    adj[u].append(v)
    adj[v].append(u)
parent = [0] * (n + 1)
depth = [0] * (n + 1)
stack = [1]
parent[1] = -1
while stack:
    u = stack.pop()
    for v in adj[u]:
        if v == parent[u]:
            continue
        parent[v] = u
        depth[v] = depth[u] + 1
        stack.append(v)
answer = 0
while depth[s] > depth[t]:
    s = parent[s]
    answer += 1
while depth[t] > depth[s]:
    t = parent[t]
    answer += 1
while s != t:
    s, t = parent[s], parent[t]
    answer += 2
print(answer)

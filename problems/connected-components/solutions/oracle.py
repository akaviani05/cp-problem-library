"""Independent breadth-first-search oracle for connected components."""
import sys

tokens = list(map(int, sys.stdin.buffer.read().split()))
n, m = tokens[0], tokens[1]
graph = [[] for _ in range(n)]
for i in range(m):
    u, v = tokens[2 + 2 * i] - 1, tokens[3 + 2 * i] - 1
    graph[u].append(v)
    graph[v].append(u)

seen = bytearray(n)
components = 0
for start in range(n):
    if seen[start]:
        continue
    components += 1
    seen[start] = 1
    queue = [start]
    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        for to in graph[v]:
            if not seen[to]:
                seen[to] = 1
                queue.append(to)
print(components)

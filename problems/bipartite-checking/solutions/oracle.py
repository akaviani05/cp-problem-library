#!/usr/bin/env python3
import sys
from collections import deque


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return
    n, m = data[:2]
    graph = [[] for _ in range(n)]
    edges = []
    at = 2
    for _ in range(m):
        u, v = data[at] - 1, data[at + 1] - 1
        at += 2
        edges.append((u, v))
        graph[u].append(v)
        graph[v].append(u)

    # For small graphs, decide bipartiteness by enumerating every coloring;
    # this is independent of the traversal used by the accepted solutions.
    if n <= 12:
        for mask in range(1 << n):
            if all(((mask >> u) & 1) != ((mask >> v) & 1) for u, v in edges):
                print("YES")
                print(*(mask >> v & 1 for v in range(n)))
                return

    color = [-1] * n
    parent = [-1] * n
    depth = [0] * n
    for root in range(n):
        if color[root] != -1:
            continue
        color[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    queue.append(v)
                elif color[v] == color[u]:
                    a, b = u, v
                    left, right = [a], [b]
                    while depth[a] > depth[b]:
                        a = parent[a]
                        left.append(a)
                    while depth[b] > depth[a]:
                        b = parent[b]
                        right.append(b)
                    while a != b:
                        a, b = parent[a], parent[b]
                        left.append(a)
                        right.append(b)
                    cycle = left[:-1] + right[::-1]
                    print("NO")
                    print(len(cycle))
                    print(*(x + 1 for x in cycle))
                    return
    print("YES")
    print(*color)


if __name__ == "__main__":
    main()

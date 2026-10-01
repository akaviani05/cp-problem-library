"""Independent graph oracle using disjoint sets and a forest-path search."""
import sys
from collections import deque


def solve(data: str) -> str:
    tokens = list(map(int, data.split()))
    n, m = tokens[:2]
    edges = list(zip(tokens[2::2], tokens[3::2]))
    representative = list(range(n + 1))
    weight = [1] * (n + 1)

    def find(x: int) -> int:
        while representative[x] != x:
            representative[x] = representative[representative[x]]
            x = representative[x]
        return x

    forest = [[] for _ in range(n + 1)]
    for u, v in edges:
        a, b = find(u), find(v)
        if a == b:
            predecessor = {u: 0}
            todo = deque([u])
            while v not in predecessor:
                x = todo.popleft()
                for y in forest[x]:
                    if y not in predecessor:
                        predecessor[y] = x
                        todo.append(y)
            path = []
            x = v
            while x:
                path.append(x)
                if x == u:
                    break
                x = predecessor[x]
            path.reverse()
            return "CYCLE " + str(len(path)) + " " + " ".join(map(str, path)) + "\n"
        if weight[a] < weight[b]:
            a, b = b, a
        representative[b] = a
        weight[a] += weight[b]
        forest[u].append(v)
        forest[v].append(u)
    return "FOREST\n"


if __name__ == "__main__":
    print(solve(sys.stdin.read()), end="")

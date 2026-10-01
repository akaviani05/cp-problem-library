#!/usr/bin/env python3
"""Small cases use cyclic-state retrograde analysis; large cases use tree coloring."""
from collections import deque
import sys


def retrograde(n, graph, x, y):
    states = [(a, b, turn) for a in range(n) for b in range(n)
              if a != b for turn in range(2)]
    index = {state: i for i, state in enumerate(states)}
    successors = [[] for _ in states]
    predecessors = [[] for _ in states]
    for i, (a, b, turn) in enumerate(states):
        moving, fixed = (a, b) if turn == 0 else (b, a)
        for v in graph[moving]:
            if v == fixed:
                continue
            nxt = (v, b, 1) if turn == 0 else (a, v, 0)
            j = index[nxt]
            successors[i].append(j)
            predecessors[j].append(i)

    # winner[i] is Alice, Bob, or unknown. Unresolved states are draws.
    winner = [-1] * len(states)
    remaining = [len(row) for row in successors]
    queue = deque()
    for i, (_, _, turn) in enumerate(states):
        if remaining[i] == 0:
            winner[i] = 1 - turn
            queue.append(i)

    while queue:
        j = queue.popleft()
        w = winner[j]
        for i in predecessors[j]:
            if winner[i] != -1:
                continue
            turn = states[i][2]
            if w == turn:
                winner[i] = w
                queue.append(i)
            else:
                remaining[i] -= 1
                if remaining[i] == 0:
                    winner[i] = w
                    queue.append(i)

    result = winner[index[(x, y, 0)]]
    if result == -1:
        raise ValueError("the supplied tree has an unresolved draw state")
    return result


def solve(data):
    tokens = list(map(int, data.split()))
    n, x, y = tokens[:3]
    x -= 1
    y -= 1
    graph = [[] for _ in range(n)]
    at = 3
    for _ in range(n - 1):
        u, v = tokens[at] - 1, tokens[at + 1] - 1
        at += 2
        graph[u].append(v)
        graph[v].append(u)

    if n <= 64:
        who = retrograde(n, graph, x, y)
    else:
        color = [-1] * n
        color[x] = 0
        stack = [x]
        while stack:
            u = stack.pop()
            for v in graph[u]:
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    stack.append(v)
        who = 0 if color[x] == color[y] else 1
    return "Alice\n" if who == 0 else "Bob\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.buffer.read()))

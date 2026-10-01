# Connected Components

## Contract and assumptions

Input is one simple undirected graph with 1 to 200,000 vertices and 0 to 200,000 distinct non-loop edges, additionally bounded by the number of possible vertex pairs. Vertices are numbered from 1. Output the number of connected components. The statement uses a 2-second time limit and a 256 MB memory limit. The task is batch, unweighted, and has no additional connectivity assumptions.

## Correctness

The main solution starts a depth-first traversal at every unvisited vertex and marks vertices when pushing them. Every vertex reachable from a start is visited during that traversal, and no vertex outside its connected component can be visited because every traversal step follows an edge. Thus each traversal visits exactly one previously unvisited component, and every component is eventually traversed once. Counting traversals gives the answer.

The main solution uses an iterative graph traversal in $O(n+m)$ time and $O(n+m)$ memory. The accepted reference instead unions edge endpoints with a disjoint-set union structure and counts successful unions from the initial $n$ singleton sets. The Python oracle independently uses breadth-first search and counts BFS starts.

## Tests and generator coverage

The manual example includes a three-vertex component, an isolated vertex, and a two-vertex component. Generator modes cover a one-vertex graph, a maximum-size empty graph, a long chain, a large star, a relabelled and shuffled chain, an unrestricted random graph, a guaranteed disconnected graph with two non-crossing vertex groups, and a complete graph. The suite includes maximum vertex and edge counts, zero-edge graphs, and cyclic graphs. Validator fixtures exercise lower and upper bounds, edge-count feasibility, loops, repeated/reversed edges, endpoint bounds, strict spacing, truncation, trailing tokens, and empty input. Small stress inputs exhaust all simple graphs on 1 through 5 vertices.

## Rejected solution

`wrong.cpp` assumes each edge reduces the component count by one and prints $n-m$. This is correct for forests but fails when an edge closes a cycle. For example, a triangle has one component while this solution prints $0$.

## Assumptions

The graph is simple and undirected, as specified by the input contract. The vertex count is positive, so every input has at least one component.

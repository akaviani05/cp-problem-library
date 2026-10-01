# Problem review

## Contract and assumptions

The input is one simple undirected graph with $1\le n\le 200000$ and
$0\le m\le 200000$. Vertices are numbered from 1 to n. Self-loops and
repeated undirected edges are forbidden. The graph may be disconnected.
The output begins with `YES` and a valid 0/1 coloring, or with `NO` and a
simple odd cycle listed in cyclic order. Output certificates are checked
semantically, so any valid coloring or odd cycle is accepted.

The statement chooses a common two-coloring definition of bipartite and makes
all certificate details explicit. There are no additional input cases or
queries.

## Accepted algorithms and proof

The main solution BFS-colors every connected component. A newly visited
neighbor gets the opposite color. If an edge joins equal-colored vertices,
the parent paths in the BFS forest meet at a common ancestor. The tree path
between these endpoints has even length because both endpoint depths have
the same parity. Adding the detected edge yields a simple odd cycle. If no
such edge exists, each edge joins opposite colors, so the coloring is valid.

The reference implementation uses an explicit depth-first traversal stack
instead of BFS. It applies the same parity invariant to the recorded forest
and constructs a cycle from parent paths. Both algorithms run in $O(n+m)$
time and use $O(n+m)$ memory; all traversals are iterative.

For graphs with at most 12 vertices, the Python oracle independently tries
every binary coloring and checks each edge directly. If none works, it uses a
queue traversal with parent-path reconstruction to produce an odd cycle. For
larger graphs it uses the queue traversal to decide and produce a certificate.
Its output is accepted by the semantic checker rather than compared token for
token.

## Checker

The checker reads the graph directly and ignores the jury answer as a source
of truth. For `YES`, it checks that exactly n binary colors are provided and
that every edge crosses the coloring. For `NO`, it checks an odd cycle length
from 3 through n, range and uniqueness of all listed vertices, and the
presence of every consecutive edge including the closing edge. It rejects
extra output. These conditions also establish that the claimed graph
classification is correct.

## Test coverage

The generator uses the documented `testlib_ext.h` helpers for arbitrary
simple graphs, bipartite graphs, connected bipartite graphs, paths, and
stars, and shuffles vertex labels and edge order in the path and star modes.
The long-odd-cycle mode closes a shuffled chain to form a single odd cycle on
199999 vertices; the triangle mode inserts a triangle while keeping the
requested edge count. Packaged tests cover a one-vertex empty graph; a
disconnected triangle outside vertex 1 to reject the known wrong solution;
200000-vertex path and star; a 200000-edge connected bipartite graph; a dense
bipartite graph; a 200000-edge graph containing an odd cycle; an arbitrary
200000-edge graph; a maximum-edge triangle-containing graph; and a
199999-vertex cycle, forcing recovery and output of a maximum-length odd-cycle
witness.

Validator fixtures cover minimum and maximum vertex bounds, count bounds,
endpoint bounds, exact line structure, EOF, loops, and both orientations of
duplicate edges. Packaged maximum tests exercise the maximum edge count.
Checker fixtures accept alternate valid colorings and cycles, ignore
whitespace, and reject same-color edges, even cycles, repeated cycle
vertices, missing edges, a false odd-cycle claim, invalid colors, extra
tokens, and empty output. The independent stress input set enumerates all
simple graphs up to four vertices and adds 250 fixed-seed random graphs.

## Known wrong approach

`wrong.cpp` only traverses the component containing vertex 1. It can miss an
odd cycle in another component and leave that component incorrectly colored.
The packaged arbitrary-graph and explicit checker cases cover disconnected
graphs; a minimal rejecting graph is an isolated vertex 1 together with a
triangle on vertices 2, 3, and 4.

## Verification evidence

The verified package has 11 tests, 325 stress cases, 17 validator fixtures,
and 14 checker fixtures. The wrong solution was rejected on test indices 7,
10, and 11; index 10 is the explicit isolated-vertex plus disconnected-triangle
case. The latest measured maximum accepted-solution use was 0.0635 seconds
and 18060 KiB RSS for `main.cpp`, and 0.0594 seconds and 18788 KiB RSS for
`reference.cpp`. Verification completed in 28.794 seconds on the local Linux
environment with g++ 13.3.0. These are local harness measurements, not a
claim about Polygon judge hardware.

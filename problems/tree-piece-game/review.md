# Review

## Contract and assumptions

Input is one tree with 2 to 200,000 vertices, two distinct starting vertices, then exactly n-1 undirected edges. Alice moves first. Each player must move their own piece to an adjacent vertex that is not occupied by the other piece; having no legal move loses. Both play optimally. Output exactly `Alice` or `Bob`. The source is credited in the legend as requested: https://quera.org/problemset/9023.

## Algorithm and correctness

The winner to move is determined by the parity of the distance between the pieces. At an even distance, the player to move has distance at least two and can move one step toward the other piece. After that move, the opponent's turn begins at odd distance. If the opponent moves toward the chaser, they advance along the same path, and on the chaser's next turn the chaser continues forward along that path. If the opponent moves in another direction, the unique path from the chaser to the opponent's new position goes through the opponent's old position, so the chaser's next move follows that same forward branch toward the old position. The opponent cannot move through or onto the chaser's occupied vertex. In either case, the chaser never reverses the edge they just used. Thus the chaser's successive moves form a walk in the tree with no immediate edge reversal. A finite tree has no infinite such walk: any nonbacktracking walk that repeats a vertex would contain a cycle. The chaser always has a legal move at even distance, so the play must end on the opponent's turn, when that opponent has no legal move.

At odd distance, the player to move either has no legal move and loses, or makes a move that changes the distance to even. The opponent can then use the strategy above. Therefore even distance is winning for the player to move and odd distance is losing. Alice wins precisely when dist(x,y) is even. `main.cpp` computes the distance with BFS in O(n) time and O(n) memory. `reference.cpp` independently two-colors the tree iteratively and compares the starting colors.

## Oracle and evidence

For n <= 64, `oracle.py` constructs the full directed configuration graph (piece positions and turn) and performs retrograde win/loss propagation. Any states left unclassified would be draws; it rejects those instead of silently assigning an outcome. This is independent of the distance-parity implementations and explicitly handles possible cyclic play. Larger oracle inputs use iterative tree coloring to keep verification linear in input size. The deterministic stress set contains 359 cases: every pair on paths of sizes 2 through 9, every pair in stars of sizes 3 through 9, and 120 seeded random labelled trees of sizes 2 through 12.

## Test and generator coverage

The generator uses the shared tree helpers and shuffled labels/edge order. Packaged cases cover a minimum chain, maximum chain (200,000 vertices), star, broom, uniform random tree, chain-plus-random tree, and complete binary tree. The validator checks bounds, distinct starts, endpoint range, loops, acyclicity, exact edge count, and EOF; n-1 acyclic edges ensure connectivity.

## Rejected solution

`wrong.cpp` reverses the parity result, assigning even distance to Bob. The statement sample is a rejecting witness: vertices 1 and 5 on the five-vertex path have distance four, so the correct answer is Alice.

## Limits

The selected limits are 1 second and 256 MB. Both accepted implementations use iterative traversals and O(n) memory; verification will measure maximum-case performance.

# Plain batch template

Use `cppl new` rather than copying this directory yourself. The manifest starts
as a draft and points to the shared pinned headers. Complete the problem-specific
generator, strict validator, solutions, independent Python oracle, stress inputs,
statement fragments, sample data, fixtures, and correctness/coverage review.

The checker compares exact tokens and ignores whitespace. Adapt its fixture
inputs/answers to the new problem. Replace it for alternative outputs or numeric
tolerance. Empty-output fixtures stay local with `polygon: false`.

Follow `docs/agents/problem.md` for the exact file contract. Future tree, graph,
and array templates should retain the same manifest and verification interface.

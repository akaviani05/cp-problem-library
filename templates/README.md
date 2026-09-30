# Problem templates

`plain/` is the supported standard batch template. Run `cppl new SLUG` with title,
description, and tags to instantiate it under `problems/`. It includes a working
whitespace-ignoring token checker and deliberately unfinished problem-specific
assets. Draft guards and unfinished markers prevent accidental publication.

Tree, graph, and array templates can be added later using the same manifest,
fixture, oracle, and test-recipe contracts. Do not include binaries, generated
testdata, credentials, or remote state in a template.

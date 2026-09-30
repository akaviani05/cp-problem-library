from pathlib import Path
import tempfile
import unittest

from cpplib.runner import execute

ROOT = Path(__file__).resolve().parents[1]


class GeneratorHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.work.name) / "helpers"
        result = execute(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-I", ROOT / "include",
                          ROOT / "tests/testlib_ext.cpp", "-o", cls.binary], timeout=90, memory_mib=0)
        if result.returncode:
            cls.work.cleanup()
            raise AssertionError(result.stderr.decode())

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def test_tree_shapes_and_parent_invariants(self):
        run = execute([self.binary, "trees", "123"], timeout=20, memory_mib=512)
        self.assertEqual(run.returncode, 0, run.stderr.decode())

    def test_sparse_dense_connected_and_disconnected_graphs(self):
        run = execute([self.binary, "graphs", "123"], timeout=30, memory_mib=512)
        self.assertEqual(run.returncode, 0, run.stderr.decode())

    def test_permutations_and_relabelled_edges(self):
        run = execute([self.binary, "shuffle", "123"], timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr.decode())

    def test_seed_reproducibility_and_variation(self):
        def sample(seed):
            run = execute([self.binary, "sample", seed])
            self.assertEqual(run.returncode, 0, run.stderr.decode())
            return run.stdout
        self.assertEqual(sample("111"), sample("111"))
        self.assertNotEqual(sample("111"), sample("222"))

    def test_invalid_requests_fail_promptly(self):
        for mode in ("invalid-full-binary", "invalid-tree-size", "invalid-chain-size", "invalid-mode",
                     "invalid-parent-cycle", "invalid-parent-roots", "invalid-parent-index", "invalid-graph",
                     "invalid-negative-graph", "invalid-connected", "invalid-empty-connected", "invalid-shuffle"):
            with self.subTest(mode=mode):
                run = execute([self.binary, mode], timeout=2)
                self.assertNotEqual(run.returncode, 0)
                self.assertIsNone(run.termination, run.stderr.decode())


if __name__ == "__main__":
    unittest.main()

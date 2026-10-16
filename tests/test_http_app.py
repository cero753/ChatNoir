"""Runtime proof through actual HTTP routes, not a reimplementation of their logic."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
probe = runpy.run_path(str(ROOT / "scripts/http_probe.py"))["probe"]


class HttpBoundaryTests(unittest.TestCase):
    def test_original_attacks_reach_all_three_broken_boundaries(self):
        result = probe(ROOT / "examples/http-app/vulnerable")
        for key in ("sql_injection_blocked", "cross_user_invoice_blocked", "path_traversal_blocked"):
            self.assertFalse(result.pop(key), key)
        self.assertTrue(all(result.values()), result)

    def test_fixed_boundaries_block_attacks_and_preserve_legitimate_requests(self):
        result = probe(ROOT / "examples/http-app/fixed")
        self.assertTrue(all(result.values()), result)


if __name__ == "__main__":
    unittest.main()

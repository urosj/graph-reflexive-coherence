from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from numerical_convergence import adjacent_relative_errors, observed_order  # noqa: E402


class NumericalConvergenceTest(unittest.TestCase):
    def test_adjacent_errors_and_second_order_sequence(self) -> None:
        errors = adjacent_relative_errors([0.25, 0.0625, 0.015625])
        self.assertEqual([0.1875, 0.046875], errors)
        self.assertAlmostEqual(2.0, observed_order(errors)[0])


if __name__ == "__main__":
    unittest.main()

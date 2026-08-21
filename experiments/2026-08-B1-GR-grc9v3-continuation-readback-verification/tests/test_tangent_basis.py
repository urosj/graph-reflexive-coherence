from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tangent_basis import basis_checks, zero_sum_basis  # noqa: E402


class TangentBasisTest(unittest.TestCase):
    def test_two_and_three_node_bases_are_orthonormal_and_zero_sum(self) -> None:
        for size in (2, 3, 8):
            basis = zero_sum_basis(size)
            checks = basis_checks(basis)
            self.assertEqual((size, size - 1), basis.shape)
            self.assertLess(checks["orthonormality_error"], 1e-12)
            self.assertLess(checks["zero_sum_error"], 1e-12)
            self.assertTrue(np.allclose(np.ones(size) @ basis, 0.0))


if __name__ == "__main__":
    unittest.main()

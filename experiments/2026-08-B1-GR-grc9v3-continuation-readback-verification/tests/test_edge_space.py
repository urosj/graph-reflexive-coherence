from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from edge_space import projector_diagnostics, weighted_cycle_projector  # noqa: E402


class EdgeSpaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.incidence = np.array([[-1.0, 0.0, 1.0], [1.0, -1.0, 0.0], [0.0, 1.0, -1.0]])
        self.conductance = np.array([1.0, 2.0, 3.0])

    def test_native_metric_cycle_projector_algebra(self) -> None:
        projector = weighted_cycle_projector(self.incidence, self.conductance)
        diagnostics = projector_diagnostics(self.incidence, self.conductance, projector)
        for error in diagnostics.values():
            self.assertLess(error, 1e-12)

    def test_edge_reorientation_covariance(self) -> None:
        signs = np.diag([-1.0, 1.0, -1.0])
        original = weighted_cycle_projector(self.incidence, self.conductance)
        reoriented = weighted_cycle_projector(self.incidence @ signs, self.conductance)
        self.assertTrue(np.allclose(reoriented, signs @ original @ signs, atol=1e-12))

    def test_nonpositive_conductance_blocks_native_metric(self) -> None:
        with self.assertRaises(ValueError):
            weighted_cycle_projector(self.incidence, np.array([1.0, 0.0, 1.0]))


if __name__ == "__main__":
    unittest.main()

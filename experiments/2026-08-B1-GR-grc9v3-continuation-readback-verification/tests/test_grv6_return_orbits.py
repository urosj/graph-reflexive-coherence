from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from grv6_methods import (  # noqa: E402
    branch_current_control,
    canonical_cycle_seed,
    evaluate_orbit,
    oriented_incidence,
    proper_divisors,
)
from pygrc.models import GRC9V3  # noqa: E402
from state_codec import BranchCoordinateChart  # noqa: E402


class GRV6ReturnOrbitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv6_current_recurrence.json").read_text(encoding="utf-8")
        )
        registry = json.loads(
            (ROOT / "outputs/fixed_branch_registry.json").read_text(encoding="utf-8")
        )["payload"]["branches"]
        cls.homogeneous = next(
            row for row in registry if row["branch_id"] == "grv2-f1-001"
        )
        cls.triangle = next(
            row for row in registry if row["branch_id"] == "grv2-f3-033"
        )
        cls.homogeneous_model = GRC9V3.load(
            str(REPO_ROOT / cls.homogeneous["state_snapshot_path"])
        )
        cls.triangle_model = GRC9V3.load(
            str(REPO_ROOT / cls.triangle["state_snapshot_path"])
        )

    def test_contract_freezes_complete_search_without_post_outcome_selection(
        self,
    ) -> None:
        self.assertEqual(48, self.config["source_scope"]["expected_branch_count"])
        self.assertEqual([2, 3, 4, 5, 6, 8], self.config["orbit_search"]["periods"])
        self.assertEqual(256, self.config["orbit_search"]["search_budget_per_period"])
        self.assertFalse(
            self.config["source_scope"]["post_outcome_branch_selection_allowed"]
        )
        self.assertFalse(
            self.config["claim_boundary"]["no_orbit_found_is_global_nonexistence_proof"]
        )

    def test_triangle_cycle_seed_is_divergence_free(self) -> None:
        incidence, _, _ = oriented_incidence(self.triangle_model)
        seed = canonical_cycle_seed(
            self.triangle_model,
            rank_tolerance=self.config["edge_space"]["rank_tolerance"],
        )
        self.assertIsNotNone(seed)
        assert seed is not None
        self.assertLess(np.linalg.norm(incidence @ seed), 1e-12)

    def test_cycle_seed_is_overwritten_and_sign_even_control_passes(self) -> None:
        row = branch_current_control(
            self.triangle_model, self.triangle["branch_id"], self.config
        )
        self.assertEqual(2, len(row["cycle_seed_rows"]))
        self.assertTrue(
            all(
                cycle["classification"]
                == "cycle_seed_overwritten_by_native_potential_flow"
                for cycle in row["cycle_seed_rows"]
            )
        )
        self.assertTrue(
            row["sign_even_magnitude_matched"]["conductance_write_sign_even"]
        )
        self.assertTrue(row["budget_conservation_passed"])
        self.assertTrue(row["topology_and_noncurrent_categorical_state_clean"])

    def test_periodic_search_rejects_fixed_point_as_proper_divisor(self) -> None:
        chart = BranchCoordinateChart.from_model(self.homogeneous_model, ("C", "W"))
        coordinate = chart.encode_model(self.homogeneous_model)
        result = evaluate_orbit(chart, coordinate, 2, self.config)
        self.assertTrue(result["physical_return"])
        self.assertFalse(result["primitive_period_supported"])
        self.assertEqual(
            "rejected_proper_divisor_or_period_one_fixed_point",
            result["classification"],
        )
        self.assertEqual([1], proper_divisors(2))
        self.assertEqual([1, 2, 4], proper_divisors(8))


if __name__ == "__main__":
    unittest.main()

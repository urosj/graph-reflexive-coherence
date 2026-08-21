from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from solve_strong_fixed_branches import (  # noqa: E402
    assert_search_contract,
    build_params,
    block_projection,
    certify_branch,
    replay_saved_branch,
    search_space_size,
    solve_seed,
)


class StrongFixedBranchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/branch_search.json").read_text(encoding="utf-8")
        )

    def test_search_space_is_complete_and_within_budget(self) -> None:
        assert_search_contract(self.config)
        self.assertEqual(16, search_space_size(self.config, "F1"))
        self.assertEqual(64, search_space_size(self.config, "F2"))
        self.assertEqual(64, search_space_size(self.config, "F3"))

    def test_homogeneous_two_node_branch_passes_strong_certification(self) -> None:
        params = build_params(0.5, 0.1, 1.0, 31001)
        _, result = certify_branch("F1", [2.0, 2.0], params, self.config)
        self.assertEqual(
            "provisional_physical_strong_branch", result["branch_class"]
        )
        self.assertEqual(
            0.0,
            result["internal_stage_residuals"]["budget_correction_l_inf"],
        )
        self.assertTrue(
            result["event_and_topology_assertions"]["full_step_no_events"]
        )

    def test_two_node_source_critical_nonuniform_seed_is_retained(self) -> None:
        params = build_params(1.0, 0.1, 1.0, 31001)
        solver = solve_seed("F2", [1.0, 3.0], params, self.config)
        self.assertEqual("converged", solver["status"])
        self.assertGreater(max(solver["final_coherence"]) - min(solver["final_coherence"]), 0.25)
        _, result = certify_branch(
            "F2", solver["final_coherence"], params, self.config
        )
        self.assertEqual(
            "provisional_physical_strong_branch", result["branch_class"]
        )

    def test_triangle_source_critical_nonuniform_seed_is_retained(self) -> None:
        params = build_params(1.5, 0.05, 0.5, 31001)
        solver = solve_seed("F3", [1.0, 2.0, 3.0], params, self.config)
        self.assertEqual("converged", solver["status"])
        _, result = certify_branch(
            "F3", solver["final_coherence"], params, self.config
        )
        self.assertEqual(
            "provisional_physical_strong_branch", result["branch_class"]
        )
        self.assertEqual(
            "GRV3",
            self.config["certification"]["causal_strong_branch_upgrade_gate"],
        )

    def test_triangle_snapshot_orientation_normalization_uses_frozen_tolerance(self) -> None:
        params = build_params(1.5, 0.05, 0.5, 31001)
        model, result = certify_branch("F3", [1.0, 2.0, 3.0], params, self.config)
        self.assertEqual(
            "provisional_physical_strong_branch", result["branch_class"]
        )
        model.rebase_reset_baseline()
        tolerances = json.loads(
            (ROOT / "configs/numerical_tolerances.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "triangle.json"
            model.save(str(path))
            replay = replay_saved_branch(path, block_projection(model), tolerances)
        self.assertEqual("passed", replay["status"])
        self.assertTrue(replay["load_projection_within_declared_tolerance"])
        self.assertLessEqual(
            replay["load_per_block_residuals"]["J"]["l_inf"],
            tolerances["absolute_tolerances"]["J"],
        )


if __name__ == "__main__":
    unittest.main()

"""Seed-driven structural lowering tests for the Phase 6 GRC9 landscape lane."""

from __future__ import annotations

from pathlib import Path
import unittest

from pygrc.core import digest_snapshot
from pygrc.models import (
    build_grc9_from_landscape_seed,
    resolve_grc9_landscape_params,
    run_grc9_landscape_seed,
)


_CELL1_SEED = Path("configs/landscapes/seed/cell-1.seed.yaml")


class GRC9LandscapeLoweringTest(unittest.TestCase):
    """Validate the structural seed-to-GRC9 mechanical lowering path."""

    def test_build_grc9_from_landscape_seed_is_deterministic(self) -> None:
        params = resolve_grc9_landscape_params(_CELL1_SEED)
        model_a = build_grc9_from_landscape_seed(_CELL1_SEED, params=params)
        model_b = build_grc9_from_landscape_seed(_CELL1_SEED, params=params)

        self.assertEqual(
            digest_snapshot(model_a.snapshot()),
            digest_snapshot(model_b.snapshot()),
        )
        state = model_a.get_state()
        self.assertEqual(
            "grc9_structural_graph_graft_v1",
            state.cached_quantities["landscape_projection_mode"],
        )
        self.assertEqual(
            "row_major_by_neighbor_then_edge",
            state.cached_quantities["landscape_port_assignment_mode"],
        )
        self.assertGreater(len(tuple(state.topology.iter_live_node_ids())), 0)
        self.assertGreater(len(tuple(state.topology.iter_live_edge_ids())), 0)

    def test_run_grc9_landscape_seed_executes_replay_stably(self) -> None:
        params = resolve_grc9_landscape_params(_CELL1_SEED)
        run_a = run_grc9_landscape_seed(_CELL1_SEED, params=params, num_steps=2)
        run_b = run_grc9_landscape_seed(_CELL1_SEED, params=params, num_steps=2)

        self.assertEqual(2, len(run_a.step_results))
        self.assertEqual(2, len(run_b.step_results))
        self.assertEqual(run_a.final_observables, run_b.final_observables)
        self.assertEqual(
            digest_snapshot(run_a.model.snapshot()),
            digest_snapshot(run_b.model.snapshot()),
        )


if __name__ == "__main__":
    unittest.main()

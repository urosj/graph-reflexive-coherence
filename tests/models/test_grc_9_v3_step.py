"""Executable step-loop tests for the Phase 7 GRC9V3 shell."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.models import GRC9V3


EXPECTED_STEP_ORDER = (
    "compute_row_basis_gradient_pre_flux",
    "compute_signed_hessian_row_basis_pre_flux",
    "compute_net_flux_summary_pre_flux",
    "compute_node_tensors",
    "compute_base_conductance",
    "compute_edge_labels_pre_flux",
    "compute_potential",
    "compute_flux",
    "compute_edge_labels_post_flux",
    "refresh_differential_summary_post_flux",
    "detect_flux_topology_identities",
    "validate_geometric_basin_seeds",
    "compute_effective_basin_masses",
    "detect_hybrid_spark_candidates",
    "apply_mechanical_expansion",
    "refresh_after_expansion",
    "evaluate_child_basin_stabilization",
    "register_completed_hybrid_sparks",
    "update_hierarchy",
    "update_choice_collapse_learning",
    "apply_growth",
    "apply_boundary_behavior",
    "apply_continuity",
    "enforce_quadrature_budget",
    "refresh_runtime_state_final",
    "refresh_or_invalidate_coarse_cache",
    "compute_observables",
)


def _two_node_step_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 0},
                    "payload": {},
                }
            ],
            "incidence": {"0": [0], "1": [0]},
            "port_structure": {},
        },
        "nodes": {
            "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
            "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 1.0,
                "flux_uv": 0.0,
            }
        },
        "coarse_cache": {"stale": {"field": "coherence"}},
    }


def _step_params(**modes: object) -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
            "eps_gradient": 0.5,
            "eps_hessian": 0.1,
            "eps_spark": 0.0,
            "compatibility_score_params": {
                "epsilon_choice": 0.10,
                "epsilon_collapse": 0.50,
            },
        },
        "constitutive_semantic_modes": dict(modes),
    }


class GRC9V3StepLoopTest(unittest.TestCase):
    """Validate Phase 7 Iteration 6 executable step closure."""

    def test_step_executes_documented_loop_and_advances_time(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_step_state(),
            params=_step_params(),
        )

        result = model.step()
        state = model.get_state()

        self.assertEqual(1, result.step_index)
        self.assertAlmostEqual(0.1, result.time)
        self.assertEqual(EXPECTED_STEP_ORDER, result.bookkeeping["step_order"])
        self.assertEqual(EXPECTED_STEP_ORDER, result.bookkeeping["expected_step_order"])
        self.assertEqual(EXPECTED_STEP_ORDER, state.cached_quantities["last_step_trace"])

    def test_step_preserves_fixed_budget_after_continuity_and_invalidates_coarse_cache(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_step_state(),
            params=_step_params(),
        )

        result = model.step()
        state = model.get_state()

        self.assertEqual([], result.events)
        self.assertEqual([], state.cached_quantities["current_step_events"])
        self.assertAlmostEqual(4.0, state.budget_target)
        self.assertAlmostEqual(
            4.0,
            sum(node_state.coherence for node_state in state.nodes.values()),
        )
        self.assertEqual({}, state.coarse_cache)
        self.assertEqual("post_semantic_update", state.cached_quantities["coarse_cache_invalidation_reason"])
        self.assertIn("last_continuity_delta", state.cached_quantities)
        self.assertEqual("prune_noop", state.cached_quantities["boundary_behavior_mode"])
        self.assertEqual([0], state.cached_quantities["continuity_live_edge_ids"])

    def test_snapshot_replay_after_step_preserves_settled_state(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_step_state(),
            params=_step_params(),
        )
        model.step()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9v3_step.json"
            model.save(str(path))
            restored = GRC9V3.load(str(path))

        self.assertEqual(1, restored.get_state().step_index)
        self.assertAlmostEqual(0.1, restored.get_state().time)
        self.assertEqual(
            EXPECTED_STEP_ORDER,
            tuple(restored.get_state().cached_quantities["last_step_trace"]),
        )
        self.assertAlmostEqual(
            model.get_state().nodes[0].coherence,
            restored.get_state().nodes[0].coherence,
        )
        self.assertAlmostEqual(
            model.get_state().nodes[1].coherence,
            restored.get_state().nodes[1].coherence,
        )


if __name__ == "__main__":
    unittest.main()

"""Choice, collapse, boundary, and budget tests for GRC9V3."""

from __future__ import annotations

import unittest

from pygrc.models import GRC9V3, PortEdge


def _choice_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
                {"node_id": 2, "payload": {}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 0},
                    "payload": {},
                },
                {
                    "edge_id": 1,
                    "endpoint_a": {"node_id": 0, "slot": 1},
                    "endpoint_b": {"node_id": 2, "slot": 0},
                    "payload": {},
                },
            ],
            "incidence": {"0": [0, 1], "1": [0], "2": [1]},
            "port_structure": {},
        },
        "nodes": {
            "0": {"coherence": 2.0, "basin_mass": 2.0, "basin_id": "choice"},
            "1": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": "1"},
            "2": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": "2"},
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 1.0,
                "flux_uv": 1.0,
            },
            "1": {
                "node_u": 0,
                "port_u": 2,
                "node_v": 2,
                "port_v": 1,
                "conductance": 1.0,
                "flux_uv": 0.95,
            },
        },
        "sink_set": [1, 2],
        "basins": {"1": [1], "2": [2]},
        "cached_quantities": {"successor_map": {"0": 1, "1": 1, "2": 2}},
    }


def _choice_params(
    *,
    evolution_overrides: dict[str, object] | None = None,
    **modes: object,
) -> dict[str, object]:
    evolution = {
        "compatibility_score_params": {
            "epsilon_choice": 0.10,
            "epsilon_collapse": 0.50,
        },
    }
    if evolution_overrides is not None:
        evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": dict(modes),
    }


class GRC9V3ChoiceBudgetTest(unittest.TestCase):
    """Validate Phase 7 Iteration 5 semantic maintenance behavior."""

    def test_choice_detection_uses_grc9v3_port_flux_successors(self) -> None:
        model = GRC9V3.from_state(state=_choice_state(), params=_choice_params())

        events = model.rebuild_choice_state()
        state = model.get_state()

        self.assertEqual(["choice_detected"], [event.kind for event in events])
        self.assertEqual(["1", "2"], state.choice_registry["0"]["viable_sink_ids"])
        self.assertAlmostEqual(
            1.0 / 1.95,
            state.choice_registry["0"]["scores"]["1"],
        )
        self.assertEqual("sink_compatibility", state.cached_quantities["choice_state"]["backend"])

    def test_collapse_records_learning_as_persistent_basin_assignment(self) -> None:
        model = GRC9V3.from_state(state=_choice_state(), params=_choice_params())
        model.rebuild_choice_state()
        state = model.get_state()
        state.step_index = 1
        state.port_edges[1] = PortEdge(
            node_u=0,
            port_u=2,
            node_v=2,
            port_v=1,
            conductance=1.0,
            flux_uv=0.1,
        )
        model.set_state(state)

        events = model.rebuild_choice_state()
        state = model.get_state()

        self.assertEqual(["collapse"], [event.kind for event in events])
        self.assertEqual({}, state.choice_registry)
        self.assertEqual("1", state.collapse_registry["0"]["collapsed_sink_id"])
        self.assertEqual("1", state.nodes[0].basin_id)
        self.assertEqual("1", state.cached_quantities["choice_learning_state"]["0"]["learned_basin_id"])

    def test_disabled_choice_backend_clears_choice_and_collapse_registries(self) -> None:
        state = _choice_state()
        state["choice_registry"] = {"0": {"backend": "sink_compatibility"}}
        state["collapse_registry"] = {"0": {"collapsed_sink_id": "1"}}
        model = GRC9V3.from_state(
            state=state,
            params=_choice_params(choice_backend="disabled"),
        )

        events = model.rebuild_choice_state()

        self.assertEqual([], events)
        self.assertEqual({}, model.get_state().choice_registry)
        self.assertEqual({}, model.get_state().collapse_registry)
        self.assertEqual("disabled", model.get_state().cached_quantities["choice_state"]["backend"])

    def test_boundary_prune_and_coarse_cache_invalidation_are_explicit(self) -> None:
        state = _choice_state()
        state["coarse_cache"] = {"old": {"field": "coherence"}}
        model = GRC9V3.from_state(state=state, params=_choice_params())

        model.apply_boundary_behavior()
        model.refresh_coarse_cache()

        self.assertEqual("prune_noop", model.get_state().cached_quantities["boundary_behavior_mode"])
        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertTrue(model.get_state().cached_quantities["coarse_cache_invalidated"])

    def test_growth_uses_outward_flux_pressure_and_invalidates_coarse_cache(self) -> None:
        state = _choice_state()
        state["coarse_cache"] = {"old": {"field": "coherence"}}
        model = GRC9V3.from_state(
            state=state,
            params=_choice_params(
                evolution_overrides={"lambda_birth": 100.0},
                choice_backend="disabled",
            ),
        )

        events = model.apply_growth()
        state = model.get_state()

        self.assertEqual(["growth"], [event.kind for event in events])
        self.assertEqual(3, events[0].payload["child_node_id"])
        self.assertEqual(4, len(tuple(state.topology.iter_live_node_ids())))
        self.assertAlmostEqual(0.2, events[0].payload["coherence_transfer"])
        self.assertEqual({}, state.coarse_cache)
        self.assertEqual(
            "growth_topology_change",
            state.cached_quantities["coarse_cache_invalidation_reason"],
        )

    def test_uniform_shift_budget_correction_matches_target(self) -> None:
        state = _choice_state()
        state["budget_target"] = 7.0
        model = GRC9V3.from_state(
            state=state,
            params=_choice_params(budget_correction_method="uniform_shift"),
        )

        summary = model.enforce_quadrature_budget()

        self.assertAlmostEqual(7.0, summary["budget_after"])
        self.assertAlmostEqual(0.0, summary["budget_error"])
        self.assertAlmostEqual(3.0, model.get_state().nodes[0].coherence)
        self.assertAlmostEqual(2.0, model.get_state().nodes[1].coherence)
        self.assertAlmostEqual(2.0, model.get_state().nodes[2].coherence)

    def test_simplex_projection_budget_correction_preserves_positivity(self) -> None:
        state = _choice_state()
        state["budget_target"] = 3.0
        state["nodes"]["0"]["coherence"] = 5.0
        state["nodes"]["1"]["coherence"] = 1.0
        state["nodes"]["2"]["coherence"] = 0.0
        model = GRC9V3.from_state(
            state=state,
            params=_choice_params(budget_correction_method="simplex_projection"),
        )

        summary = model.enforce_quadrature_budget()

        self.assertAlmostEqual(3.0, summary["budget_after"])
        self.assertAlmostEqual(0.0, summary["budget_error"])
        self.assertAlmostEqual(3.0, model.get_state().nodes[0].coherence)
        self.assertAlmostEqual(0.0, model.get_state().nodes[1].coherence)
        self.assertAlmostEqual(0.0, model.get_state().nodes[2].coherence)


if __name__ == "__main__":
    unittest.main()

"""Default-off frontier birth tests for GRCV3."""

from __future__ import annotations

import warnings
import unittest

from pygrc.core import InvalidParamsError, WeightedGraphBackend
from pygrc.models import GRCV3


def _attributes(*, coherence: float, basin_id: int) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def _frontier_graph_model(
    *,
    frontier_birth_mode: str | None,
    include_frontier_candidate: bool,
    frontier_birth_strict: str | None = None,
) -> tuple[GRCV3, int, int, int]:
    graph = WeightedGraphBackend()
    parent = graph.add_node({})
    neighbor = graph.add_node({})
    edge_id = graph.add_edge(parent, neighbor, {"base_conductance": 1.0})

    modes = {}
    if frontier_birth_mode is not None:
        modes["frontier_birth_mode"] = frontier_birth_mode
    if frontier_birth_strict is not None:
        modes["frontier_birth_strict"] = frontier_birth_strict
    params = {
        "dt": 0.1,
        "evolution": {
            "lambda_birth": 100.0,
            "alpha_seed": 0.2,
            "rng_seed": 0,
        },
        "constitutive_semantic_modes": modes,
    }
    cached_quantities = {}
    if include_frontier_candidate:
        cached_quantities["grcv3_frontier_birth_candidates"] = {
            str(parent): {
                "frontier_source": "pressure_boundary",
                "frontier_role": "pressure_boundary",
            }
        }
    model = GRCV3.from_state(
        state={
            "nodes": {
                str(parent): _attributes(coherence=10.0, basin_id=parent),
                str(neighbor): _attributes(coherence=1.0, basin_id=neighbor),
            },
            "base_conductance": {str(edge_id): 1.0},
            "cached_quantities": cached_quantities,
            "budget_target": 11.0,
        },
        params=params,
    )
    state = model.get_state()
    state.topology = graph
    state.flux = {
        (edge_id, parent): 2.0,
        (edge_id, neighbor): -2.0,
    }
    return model, parent, neighbor, edge_id


class GRCV3FrontierBirthTest(unittest.TestCase):
    def test_frontier_birth_mode_is_absent_by_default(self) -> None:
        model = GRCV3.from_config({"dt": 0.1})

        modes = dict(model.get_params().constitutive_semantic_modes)

        self.assertNotIn("frontier_birth_mode", modes)

    def test_unknown_frontier_birth_mode_is_rejected(self) -> None:
        with self.assertRaises(InvalidParamsError):
            GRCV3.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {
                        "frontier_birth_mode": "legacy_any_boundary",
                    },
                }
            )

    def test_unknown_frontier_birth_strict_mode_is_rejected(self) -> None:
        with self.assertRaises(InvalidParamsError):
            GRCV3.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {
                        "frontier_birth_strict": "sometimes",
                    },
                }
            )

    def test_missing_and_disabled_modes_have_identical_no_birth_step_trace(self) -> None:
        missing_model, *_ = _frontier_graph_model(
            frontier_birth_mode=None,
            include_frontier_candidate=True,
        )
        disabled_model, *_ = _frontier_graph_model(
            frontier_birth_mode="disabled",
            include_frontier_candidate=True,
        )

        with warnings.catch_warnings(record=True) as missing_warnings:
            warnings.simplefilter("always")
            missing_result = missing_model.step()
        with warnings.catch_warnings(record=True) as disabled_warnings:
            warnings.simplefilter("always")
            disabled_result = disabled_model.step()

        self.assertEqual([], [event.kind for event in missing_result.events])
        self.assertEqual([], [event.kind for event in disabled_result.events])
        self.assertEqual(1, len(missing_warnings))
        self.assertEqual(1, len(disabled_warnings))
        self.assertIn(
            "frontier_birth_mode is not active_frontier_pressure",
            str(missing_warnings[0].message),
        )
        self.assertIn(
            "frontier_birth_mode is not active_frontier_pressure",
            str(disabled_warnings[0].message),
        )
        self.assertEqual(
            missing_result.bookkeeping["step_order"],
            disabled_result.bookkeeping["step_order"],
        )
        self.assertNotIn("apply_frontier_birth", missing_result.bookkeeping["step_order"])
        self.assertEqual(
            len(tuple(missing_model.get_state().topology.iter_live_node_ids())),
            len(tuple(disabled_model.get_state().topology.iter_live_node_ids())),
        )

    def test_disabled_frontier_birth_warning_emits_once(self) -> None:
        model, *_ = _frontier_graph_model(
            frontier_birth_mode=None,
            include_frontier_candidate=True,
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.step()
            model.step()

        self.assertEqual(1, len(caught))
        self.assertIn("frontier-birth candidates are present", str(caught[0].message))
        self.assertTrue(
            model.get_state().cached_quantities["frontier_birth_disabled_warning_emitted"]
        )

    def test_no_frontier_candidates_do_not_warn_when_birth_disabled(self) -> None:
        model, *_ = _frontier_graph_model(
            frontier_birth_mode=None,
            include_frontier_candidate=False,
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.step()

        self.assertEqual([], caught)

    def test_strict_error_stops_disabled_frontier_birth_candidates(self) -> None:
        model, *_ = _frontier_graph_model(
            frontier_birth_mode=None,
            include_frontier_candidate=True,
            frontier_birth_strict="error",
        )

        with self.assertRaises(InvalidParamsError):
            model.step()

    def test_strict_allow_preserves_explicit_no_birth_control(self) -> None:
        model, *_ = _frontier_graph_model(
            frontier_birth_mode=None,
            include_frontier_candidate=True,
            frontier_birth_strict="allow",
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.step()

        self.assertEqual([], caught)
        self.assertEqual([], [event.kind for event in result.events])

    def test_opt_in_mode_requires_explicit_frontier_metadata(self) -> None:
        model, *_ = _frontier_graph_model(
            frontier_birth_mode="active_frontier_pressure",
            include_frontier_candidate=False,
        )

        events = model.apply_frontier_birth()

        self.assertEqual([], events)
        self.assertEqual(
            [],
            model.get_state().cached_quantities["last_frontier_birth_events"],
        )

    def test_opt_in_mode_creates_birth_from_pressure_boundary_frontier(self) -> None:
        model, parent, _neighbor, _edge_id = _frontier_graph_model(
            frontier_birth_mode="active_frontier_pressure",
            include_frontier_candidate=True,
        )

        events = model.apply_frontier_birth()
        state = model.get_state()

        self.assertEqual(["frontier_birth"], [event.kind for event in events])
        event = events[0]
        child_node_id = int(event.payload["child_node_id"])
        self.assertEqual(parent, event.payload["parent_node_id"])
        self.assertEqual("pressure_boundary", event.payload["frontier_source"])
        self.assertAlmostEqual(2.0, event.payload["outward_flux_pressure"])
        self.assertAlmostEqual(2.0, event.payload["coherence_transfer"])
        self.assertIn(child_node_id, state.nodes)
        self.assertEqual(parent, state.nodes[child_node_id].parent_id)
        self.assertAlmostEqual(8.0, state.nodes[parent].coherence)
        self.assertAlmostEqual(
            11.0,
            sum(attributes.coherence for attributes in state.nodes.values()),
        )


if __name__ == "__main__":
    unittest.main()

"""Choice / collapse contract tests for the GRCV3 family surface."""

from __future__ import annotations

import unittest

from pygrc.core import (
    SnapshotCompatibilityError,
    build_backend_selection,
    build_backend_selection_payload,
)
from pygrc.models import BasinAttributes, GRCV3


def _attributes(*, basin_id: int) -> BasinAttributes:
    return BasinAttributes(
        coherence=1.0,
        gradient=[0.0, 0.0],
        hessian=[[1.0, 0.0], [0.0, 1.0]],
        net_flux=[0.0, 0.0],
        basin_mass=1.0,
        basin_id=basin_id,
        parent_id=None,
        depth=0,
    )


class GRCV3ChoiceContractTest(unittest.TestCase):
    def test_disabled_choice_backend_clears_partial_state(self) -> None:
        model = GRCV3.from_state(
            state={
                "choice_registry": {"0": {"backend": "sink_compatibility"}},
                "collapse_registry": {"0": {"collapsed_sink_id": "3"}},
            },
            params={"dt": 0.1},
        )

        events = model.rebuild_choice_state()

        self.assertEqual([], events)
        self.assertEqual({}, model.get_state().choice_registry)
        self.assertEqual({}, model.get_state().collapse_registry)
        self.assertEqual(
            {"backend": "disabled", "evaluated_nodes": []},
            model.get_state().cached_quantities["choice_state"],
        )

    def test_sink_compatibility_emits_choice_then_collapse(self) -> None:
        model = GRCV3.from_config(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "backend_selections": build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="choice",
                                name="sink_compatibility",
                                params={
                                    "epsilon_choice": 0.10,
                                    "epsilon_collapse": 0.20,
                                },
                            )
                        ]
                    )
                },
            }
        )
        state = model.get_state()
        state.cached_quantities["hessian_sign"] = 1

        node_ids = [state.topology.add_node({}) for _ in range(5)]
        edge_01 = state.topology.add_edge(node_ids[0], node_ids[1], {})
        edge_02 = state.topology.add_edge(node_ids[0], node_ids[2], {})
        edge_13 = state.topology.add_edge(node_ids[1], node_ids[3], {})
        edge_24 = state.topology.add_edge(node_ids[2], node_ids[4], {})

        state.nodes = {node_id: _attributes(basin_id=node_id) for node_id in node_ids}
        state.flux = {
            (edge_01, node_ids[0]): 0.50,
            (edge_01, node_ids[1]): -0.50,
            (edge_02, node_ids[0]): 0.45,
            (edge_02, node_ids[2]): -0.45,
            (edge_13, node_ids[1]): 1.00,
            (edge_13, node_ids[3]): -1.00,
            (edge_24, node_ids[2]): 1.00,
            (edge_24, node_ids[4]): -1.00,
        }

        model.rebuild_identity_state()
        choice_events = model.rebuild_choice_state()

        self.assertEqual(["choice_detected"], [event.kind for event in choice_events])
        self.assertEqual(["3", "4"], model.get_state().choice_registry["0"]["viable_sink_ids"])

        state.flux[(edge_02, node_ids[0])] = 0.10
        state.flux[(edge_02, node_ids[2])] = -0.10

        model.rebuild_identity_state()
        collapse_events = model.rebuild_choice_state()

        self.assertEqual(["collapse"], [event.kind for event in collapse_events])
        self.assertEqual({}, model.get_state().choice_registry)
        self.assertEqual("3", model.get_state().collapse_registry["0"]["collapsed_sink_id"])
        self.assertEqual(
            "registry_only",
            model.get_state().collapse_registry["0"]["persistence_mode"],
        )

    def test_sink_compatibility_emits_choice_resolved_below_collapse_threshold(self) -> None:
        model = GRCV3.from_config(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "backend_selections": build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="choice",
                                name="sink_compatibility",
                                params={
                                    "epsilon_choice": 0.10,
                                    "epsilon_collapse": 0.50,
                                },
                            )
                        ]
                    )
                },
            }
        )
        state = model.get_state()
        state.cached_quantities["hessian_sign"] = 1

        node_ids = [state.topology.add_node({}) for _ in range(5)]
        edge_01 = state.topology.add_edge(node_ids[0], node_ids[1], {})
        edge_02 = state.topology.add_edge(node_ids[0], node_ids[2], {})
        edge_13 = state.topology.add_edge(node_ids[1], node_ids[3], {})
        edge_24 = state.topology.add_edge(node_ids[2], node_ids[4], {})

        state.nodes = {node_id: _attributes(basin_id=node_id) for node_id in node_ids}
        state.flux = {
            (edge_01, node_ids[0]): 0.50,
            (edge_01, node_ids[1]): -0.50,
            (edge_02, node_ids[0]): 0.45,
            (edge_02, node_ids[2]): -0.45,
            (edge_13, node_ids[1]): 1.00,
            (edge_13, node_ids[3]): -1.00,
            (edge_24, node_ids[2]): 1.00,
            (edge_24, node_ids[4]): -1.00,
        }

        model.rebuild_identity_state()
        choice_events = model.rebuild_choice_state()
        self.assertEqual(["choice_detected"], [event.kind for event in choice_events])

        state.flux[(edge_02, node_ids[0])] = 0.25
        state.flux[(edge_02, node_ids[2])] = -0.25

        model.rebuild_identity_state()
        resolved_events = model.rebuild_choice_state()

        self.assertEqual(["choice_resolved"], [event.kind for event in resolved_events])
        self.assertEqual({}, model.get_state().choice_registry)
        self.assertEqual({}, model.get_state().collapse_registry)
        self.assertEqual(
            "single_sink_below_collapse_threshold",
            resolved_events[0].payload["resolution_mode"],
        )
        self.assertEqual("3", resolved_events[0].payload["winner_sink_id"])

    def test_sink_compatibility_is_deterministic_under_fixed_inputs(self) -> None:
        config = {
            "dt": 0.1,
            "constitutive_semantic_modes": {
                "backend_selections": build_backend_selection_payload(
                    [
                        build_backend_selection(
                            category="choice",
                            name="sink_compatibility",
                            params={
                                "epsilon_choice": 0.10,
                                "epsilon_collapse": 0.20,
                            },
                        )
                    ]
                )
            },
        }

        def build_and_run() -> tuple[list[str], dict[str, object]]:
            model = GRCV3.from_config(config)
            state = model.get_state()
            state.cached_quantities["hessian_sign"] = 1
            node_ids = [state.topology.add_node({}) for _ in range(5)]
            edge_01 = state.topology.add_edge(node_ids[0], node_ids[1], {})
            edge_02 = state.topology.add_edge(node_ids[0], node_ids[2], {})
            edge_13 = state.topology.add_edge(node_ids[1], node_ids[3], {})
            edge_24 = state.topology.add_edge(node_ids[2], node_ids[4], {})
            state.nodes = {node_id: _attributes(basin_id=node_id) for node_id in node_ids}
            state.flux = {
                (edge_01, node_ids[0]): 0.50,
                (edge_01, node_ids[1]): -0.50,
                (edge_02, node_ids[0]): 0.45,
                (edge_02, node_ids[2]): -0.45,
                (edge_13, node_ids[1]): 1.00,
                (edge_13, node_ids[3]): -1.00,
                (edge_24, node_ids[2]): 1.00,
                (edge_24, node_ids[4]): -1.00,
            }
            model.rebuild_identity_state()
            events = model.rebuild_choice_state()
            payload = dict(model.get_state().choice_registry["0"])
            return [event.kind for event in events], payload

        left_events, left_payload = build_and_run()
        right_events, right_payload = build_and_run()

        self.assertEqual(left_events, right_events)
        self.assertEqual(left_payload, right_payload)

    def test_choice_state_wraps_invalid_successor_map_payloads(self) -> None:
        model = GRCV3.from_state(
            state={
                "choice_registry": {},
                "collapse_registry": {},
                "cached_quantities": {
                    "hessian_sign": 1,
                    "successor_map": {"0": "root"},
                },
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "backend_selections": build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="choice",
                                name="sink_compatibility",
                            )
                        ]
                    )
                },
            },
        )

        with self.assertRaises(SnapshotCompatibilityError):
            model.rebuild_choice_state()

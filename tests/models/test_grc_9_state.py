"""Construction and typed state-surface tests for the Phase 6 GRC9 shell."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import INTRINSIC_FRAME, InvalidParamsError, SnapshotCompatibilityError
from pygrc.models import (
    AdiabaticExpansionSchedule,
    ExpansionRecord,
    GRC9,
    GRC9State,
    PortEdge,
    occupied_ports_in_column,
    occupied_ports_in_row,
    port_to_rc,
    rc_to_port,
)


class GRC9StateContractTest(unittest.TestCase):
    """Validate the Iteration 2 GRC9 surface and port-helper boundary."""

    def test_minimal_config_resolves_defaults_and_constructs_grc9_state(self) -> None:
        model = GRC9.from_config({"dt": 0.1})

        params = model.get_params()
        modes = dict(params.constitutive_semantic_modes)
        state = model.get_state()

        self.assertEqual("fixed_port_chart", modes["frame_mode"])
        self.assertEqual("none", modes["curvature_backend"])
        self.assertEqual("prune", modes["boundary_mode"])
        self.assertEqual("equal", modes["expansion_distribution_mode"])
        self.assertEqual("all", modes["edge_label_selection"])
        self.assertIsInstance(state, GRC9State)
        self.assertEqual({}, state.node_coherence)
        self.assertEqual({}, state.port_edges)
        self.assertEqual({}, state.expansion_registry)
        self.assertEqual({}, state.prev_column_diagnostic)
        self.assertEqual(params.params_hash, state.params_identity)
        self.assertIsNotNone(state.rng_state)
        self.assertEqual(0.0, state.budget_target)
        self.assertEqual(
            "initial_state_sum",
            state.cached_quantities["budget_target_source"],
        )

    def test_capabilities_reflect_intrinsic_frame_only_for_phase6_baseline(self) -> None:
        intrinsic_model = GRC9.from_config({"dt": 0.1})
        intrinsic_claims = intrinsic_model.list_capabilities()

        self.assertIn(INTRINSIC_FRAME, intrinsic_claims)

    def test_invalid_mode_values_are_rejected_early(self) -> None:
        with self.assertRaises(InvalidParamsError):
            GRC9.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {"frame_mode": "host_embedding"},
                }
            )

        with self.assertRaises(InvalidParamsError):
            GRC9.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {"expansion_distribution_mode": "biased"},
                }
            )

        with self.assertRaisesRegex(InvalidParamsError, "only implements boundary_mode='prune'"):
            GRC9.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {"boundary_mode": "ghost"},
                }
            )

        with self.assertRaisesRegex(InvalidParamsError, "only implements boundary_mode='prune'"):
            GRC9.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {"boundary_mode": "barrier"},
                }
            )

    def test_port_helpers_cover_forward_inverse_and_membership(self) -> None:
        self.assertEqual((1, 1), port_to_rc(1))
        self.assertEqual((2, 3), port_to_rc(6))
        self.assertEqual(9, rc_to_port(3, 3))
        self.assertEqual(4, rc_to_port(2, 1))
        for port in range(1, 10):
            self.assertEqual(port, rc_to_port(*port_to_rc(port)))

        occupied = [1, 2, 4, 5, 6, 9]
        self.assertEqual((4, 5, 6), occupied_ports_in_row(occupied, 2))
        self.assertEqual((2, 5), occupied_ports_in_column(occupied, 2))

        with self.assertRaises(ValueError):
            port_to_rc(0)
        with self.assertRaises(ValueError):
            rc_to_port(4, 1)
        with self.assertRaises(ValueError):
            occupied_ports_in_column(occupied, 0)

    def test_from_state_restores_port_topology_and_typed_registries(self) -> None:
        state = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {"label": "A"}},
                    {"node_id": 1, "payload": {"label": "B"}},
                ],
                "edges": [
                    {
                        "edge_id": 0,
                        "endpoint_a": {"node_id": 0, "slot": 0},
                        "endpoint_b": {"node_id": 1, "slot": 4},
                        "payload": {"kind": "occupied"},
                    }
                ],
                "incidence": {"0": [0], "1": [0]},
                "port_structure": {
                    "0": {"ports": [{"slot": 0, "row": 0, "column": 0, "occupied": True, "edge_id": 0}]},
                    "1": {"ports": [{"slot": 4, "row": 1, "column": 1, "occupied": True, "edge_id": 0}]},
                },
            },
            "node_coherence": {"0": 1.5, "1": 0.5},
            "port_edges": {
                "0": {
                    "node_u": 0,
                    "port_u": 1,
                    "node_v": 1,
                    "port_v": 5,
                    "conductance": 0.25,
                    "flux_uv": 0.1,
                }
            },
            "potential": {"0": 1.0, "1": 0.2},
            "sink_set": [1],
            "basins": {"1": [0, 1]},
            "expansion_registry": {
                "spark-0": {
                    "parent_sink_id": 1,
                    "module_node_ids": [1],
                    "expansion_step": 2,
                    "distribution_weights": [0.5, 0.5],
                    "schedule": {
                        "total_substeps": 3,
                        "completed_substeps": 1,
                        "active": True,
                    },
                }
            },
            "prev_column_diagnostic": {"1": [0.0, 0.1, -0.1]},
        }

        model = GRC9.from_state(state=state, params={"dt": 0.1})
        restored = model.get_state()

        self.assertEqual((0, 1), tuple(restored.topology.iter_live_node_ids()))
        self.assertEqual((0,), tuple(restored.topology.iter_live_edge_ids()))
        self.assertEqual({0: 1.5, 1: 0.5}, restored.node_coherence)
        self.assertEqual({1}, restored.sink_set)
        self.assertEqual({1: {0, 1}}, restored.basins)
        self.assertIsInstance(restored.port_edges[0], PortEdge)
        self.assertIsInstance(restored.expansion_registry["spark-0"], ExpansionRecord)
        self.assertIsInstance(
            restored.expansion_registry["spark-0"].schedule,
            AdiabaticExpansionSchedule,
        )
        self.assertEqual([0.0, 0.1, -0.1], restored.prev_column_diagnostic[1])
        self.assertEqual(2.0, restored.budget_target)
        self.assertEqual(
            "initial_state_sum",
            restored.cached_quantities["budget_target_source"],
        )

    def test_budget_target_is_locked_from_initial_state_when_omitted(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                    "edges": [],
                    "incidence": {"0": [], "1": []},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 2.0},
            },
            params={"dt": 0.1},
        )

        state = model.get_state()
        self.assertEqual(3.0, state.budget_target)
        self.assertEqual("initial_state_sum", state.cached_quantities["budget_target_source"])

        state.node_coherence[0] = 10.0
        model._verify_budget_preservation(context="mutation_probe")

        self.assertEqual(3.0, state.budget_target)
        self.assertAlmostEqual(3.0, sum(state.node_coherence.values()))
        self.assertEqual("initial_state_sum", state.cached_quantities["budget_target_source"])

    def test_explicit_budget_targets_are_preserved_including_zero(self) -> None:
        explicit = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                    "edges": [],
                    "incidence": {"0": [], "1": []},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 2.0},
                "budget_target": 10.0,
            },
            params={"dt": 0.1},
        ).get_state()
        self.assertEqual(10.0, explicit.budget_target)
        self.assertEqual("provided", explicit.cached_quantities["budget_target_source"])

        explicit_zero = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [{"node_id": 0, "payload": {}}],
                    "edges": [],
                    "incidence": {"0": []},
                    "port_structure": {},
                },
                "node_coherence": {"0": 0.0},
                "budget_target": 0.0,
            },
            params={"dt": 0.1},
        )
        zero_state = explicit_zero.get_state()
        explicit_zero._ensure_budget_target()
        self.assertEqual(0.0, zero_state.budget_target)
        self.assertEqual(
            "provided_zero",
            zero_state.cached_quantities["budget_target_source"],
        )

    def test_set_state_rejects_incompatible_objects(self) -> None:
        model = GRC9.from_config({"dt": 0.1})

        with self.assertRaises(SnapshotCompatibilityError):
            model.set_state(object())  # type: ignore[arg-type]

        invalid_state = GRC9State(
            node_coherence={99: 1.0},
        )
        with self.assertRaises(Exception):
            model.set_state(invalid_state)

    def test_snapshot_save_load_preserves_grc9_surface(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [
                        {"node_id": 0, "payload": {"label": "A"}},
                        {"node_id": 1, "payload": {"label": "B"}},
                    ],
                    "edges": [
                        {
                            "edge_id": 0,
                            "endpoint_a": {"node_id": 0, "slot": 0},
                            "endpoint_b": {"node_id": 1, "slot": 4},
                            "payload": {"kind": "occupied"},
                        }
                    ],
                    "incidence": {"0": [0], "1": [0]},
                    "port_structure": {},
                },
                "node_coherence": {"0": 2.0, "1": 1.0},
                "port_edges": {
                    "0": {
                        "node_u": 0,
                        "port_u": 1,
                        "node_v": 1,
                        "port_v": 5,
                        "conductance": 0.75,
                        "flux_uv": 0.0,
                    }
                },
                "geometric_length": {"0": 1.25},
                "edge_label_computation_mode": {"geometric_length": "fixed_port_chart"},
                "edge_label_params": {"selection": "all"},
                "step_index": 2,
            },
            params={"dt": 0.1},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9.json"
            model.save(str(path))
            restored = GRC9.load(str(path))

        restored_state = restored.get_state()
        self.assertEqual(model.get_params().params_hash, restored.get_params().params_hash)
        self.assertEqual({0: 2.0, 1: 1.0}, restored_state.node_coherence)
        self.assertEqual(0.75, restored_state.port_edges[0].conductance)
        self.assertEqual(2, restored_state.step_index)
        self.assertEqual(
            {"geometric_length": "fixed_port_chart"},
            restored_state.edge_label_computation_mode,
        )
        self.assertEqual(3.0, restored_state.budget_target)
        self.assertEqual(
            "initial_state_sum",
            restored_state.cached_quantities["budget_target_source"],
        )

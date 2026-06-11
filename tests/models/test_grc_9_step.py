"""Step-loop and runtime-persistence tests for the Phase 6 GRC9 baseline."""

from __future__ import annotations

from pathlib import Path
import random
import tempfile
import unittest

from pygrc.core import StepResult, digest_snapshot, load_snapshot
from pygrc.models import GRC9


def _step_config(**evolution_overrides: object) -> dict[str, object]:
    evolution: dict[str, object] = {
        "alpha": 1.0,
        "beta": 1.0,
        "gamma": 1.0,
        "delta": 1.0,
        "kappa_c": 1.5,
        "eta": 0.5,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"mu": 0.0, "scale": 1.0},
        "lambda_birth": 1e9,
        "alpha_seed": 0.25,
        "rng_seed": 0,
        "w_bond": 1.0,
    }
    evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _topology_from_connections(
    connections: list[tuple[int, int, int, int, int]],
) -> dict[str, object]:
    node_ids: set[int] = set()
    incidence: dict[str, list[int]] = {}
    edges: list[dict[str, object]] = []
    for edge_id, node_a, slot_a, node_b, slot_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": slot_a},
                "endpoint_b": {"node_id": node_b, "slot": slot_b},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda edge: int(edge["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _port_edge_payload(
    *,
    node_u: int,
    port_u: int,
    node_v: int,
    port_v: int,
    conductance: float,
    flux_uv: float = 0.0,
) -> dict[str, float | int]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": flux_uv,
    }


def _step_state() -> dict[str, object]:
    return {
        "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
        "node_coherence": {"0": 1.0, "1": 3.0},
        "port_edges": {
            "0": _port_edge_payload(
                node_u=0,
                port_u=1,
                node_v=1,
                port_v=1,
                conductance=2.0,
            )
        },
    }


def _serialize_step_result(result: StepResult) -> dict[str, object]:
    return {
        "step_index": result.step_index,
        "time": result.time,
        "events": [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in result.events
        ],
        "observables": dict(result.observables),
        "bookkeeping": dict(result.bookkeeping),
    }


class GRC9StepLoopPersistenceTest(unittest.TestCase):
    """Validate Iteration 8 step ordering, determinism, and persistence."""

    def test_enforce_budget_uses_uniform_positive_shift_instead_of_single_node_patch(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [
                        {"node_id": 0, "payload": {}},
                        {"node_id": 1, "payload": {}},
                        {"node_id": 2, "payload": {}},
                    ],
                    "edges": [],
                    "incidence": {"0": [], "1": [], "2": []},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 2.0, "2": 0.0},
                "budget_target": 6.0,
            },
            params=_step_config(lambda_birth=0.0),
        )

        model._enforce_budget()

        self.assertEqual(
            {0: 2.0, 1: 3.0, 2: 1.0},
            model.get_state().node_coherence,
        )
        self.assertEqual(
            "uniform_shift",
            model.get_state().cached_quantities["budget_positive_correction_mode"],
        )
        self.assertAlmostEqual(0.0, model.get_state().cached_quantities["last_budget_error"])

    def test_compute_observables_uses_topology_updated_current_flux_abundance_contract(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 1, 1, 2, 0),
                    ]
                ),
                "node_coherence": {"0": 1.0, "1": 1.0, "2": 1.0},
                "sink_set": [0, 1],
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=1.0,
                    ),
                    "1": _port_edge_payload(
                        node_u=1,
                        port_u=2,
                        node_v=2,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=1.0,
                    ),
                },
            },
            params=_step_config(lambda_birth=0.0),
        )

        observables = model.compute_observables()

        self.assertEqual(1.0, observables["abundance"])
        self.assertEqual({0, 1}, model.get_state().sink_set)
        self.assertEqual(0, observables["expansion_count"])
        self.assertEqual({}, observables["sink_module_sizes"])

    def test_step_executes_full_phase6_order_and_updates_runtime_state(self) -> None:
        model = GRC9.from_state(state=_step_state(), params=_step_config())

        result = model.step()

        self.assertIsInstance(result, StepResult)
        self.assertEqual(1, result.step_index)
        self.assertEqual(0.1, result.time)
        self.assertEqual(
            (
                "compute_row_tensor",
                "compute_metric",
                "compute_edge_labels",
                "compute_potential",
                "compute_flux",
                "detect_identities",
                "detect_sparks",
                "apply_expansion",
                "apply_growth",
                "apply_boundary_behavior",
                "apply_continuity",
                "enforce_budget",
                "refresh_or_invalidate_coarse_cache",
                "compute_observables",
            ),
            result.bookkeeping["step_order"],
        )
        self.assertEqual(
            result.bookkeeping["expected_step_order"],
            result.bookkeeping["step_order"],
        )
        self.assertEqual(
            result.bookkeeping["step_order"],
            model.get_state().cached_quantities["last_step_trace"],
        )
        self.assertEqual((), model.get_state().cached_quantities["current_step_events"])
        self.assertEqual(model.get_params().params_hash, model.get_state().params_identity)
        self.assertEqual(["growth"], [event.kind for event in result.events])
        self.assertEqual(3, result.observables["num_nodes"])
        self.assertAlmostEqual(4.0, result.observables["budget_current"])
        self.assertEqual(1, model.get_state().step_index)
        self.assertAlmostEqual(0.1, model.get_state().time)

    def test_representative_lane_is_deterministic_from_same_state_and_rng(self) -> None:
        def run_lane() -> tuple[list[dict[str, object]], str]:
            model = GRC9.from_state(state=_step_state(), params=_step_config())
            results = [_serialize_step_result(model.step()) for _ in range(3)]
            return results, digest_snapshot(model.snapshot())

        left_results, left_digest = run_lane()
        right_results, right_digest = run_lane()

        self.assertEqual(left_results, right_results)
        self.assertEqual(left_digest, right_digest)
        self.assertEqual(
            left_results[-1]["bookkeeping"]["expected_step_order"],
            left_results[-1]["bookkeeping"]["step_order"],
        )

    def test_save_load_roundtrip_preserves_continued_runtime_progression(self) -> None:
        model = GRC9.from_state(state=_step_state(), params=_step_config())
        first = _serialize_step_result(model.step())

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9-runtime.json"
            model.save(str(path))
            restored = GRC9.load(str(path))

        continued_original = [
            _serialize_step_result(model.step()),
            _serialize_step_result(model.step()),
        ]
        continued_restored = [
            _serialize_step_result(restored.step()),
            _serialize_step_result(restored.step()),
        ]

        self.assertEqual(1, first["step_index"])
        self.assertEqual(continued_original, continued_restored)
        self.assertEqual(
            digest_snapshot(model.snapshot()),
            digest_snapshot(restored.snapshot()),
        )

    def test_snapshot_roundtrip_preserves_grc9_runtime_groups_and_rng(self) -> None:
        rng = random.Random(17)
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 2.5, "1": 1.5},
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=1.25,
                        flux_uv=0.2,
                    )
                },
                "geometric_length": {"0": 0.75},
                "temporal_delay": {"0": 0.5},
                "flux_coupling": {"0": 0.2},
                "potential": {"0": 1.0, "1": 0.5},
                "sink_set": [1],
                "basins": {"1": [0, 1]},
                "expansion_registry": {
                    "spark-2-0": {
                        "parent_sink_id": 0,
                        "module_node_ids": [0, 1],
                        "expansion_step": 2,
                        "distribution_weights": [1 / 3, 1 / 3, 1 / 3],
                        "schedule": {
                            "total_substeps": 3,
                            "completed_substeps": 1,
                            "active": True,
                        },
                    }
                },
                "coarse_cache": {
                    "exact_column_profile:conductance": {
                        "mode": "exact_column_profile",
                        "field_name": "conductance",
                        "by_node": {
                            "0": {
                                "column_totals": [1.25, 0.0, 0.0],
                                "profiles": [
                                    [1.0, 0.0, 0.0],
                                    [1 / 3, 1 / 3, 1 / 3],
                                    [1 / 3, 1 / 3, 1 / 3],
                                ],
                            }
                        },
                    }
                },
                "prev_column_diagnostic": {"0": [1.0, -1.0, 0.5]},
                "edge_label_computation_mode": {
                    "geometric_length": "fixed_port_chart",
                    "temporal_delay": "transport_ratio",
                    "flux_coupling": "absolute_flux",
                },
                "edge_label_params": {
                    "selection": "all",
                    "temporal_delay": {
                        "mode": "transport_ratio",
                        "v0": 1.0,
                        "rho": 1.0,
                        "eps_tau": 1e-12,
                        "geometric_length_mode": "fixed_port_chart",
                    },
                },
                "event_log": [
                    {
                        "kind": "expansion",
                        "step_index": 2,
                        "payload": {"expansion_id": "spark-2-0"},
                        "source_family": "GRC9",
                    }
                ],
                "observables": {"budget_current": 4.0},
                "rng_state": rng.getstate(),
                "step_index": 2,
                "time": 0.2,
                "budget_target": 4.0,
                "remainder": 0.0,
            },
            params=_step_config(lambda_birth=0.0),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9-serialization.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRC9.load(str(path))

        restored_state = restored.get_state()
        replay = random.Random()
        replay.setstate(restored_state.rng_state)

        self.assertEqual(
            {
                "metadata",
                "topology",
                "edge_labels",
                "dynamics",
                "observables",
                "events",
                "caches",
            },
            set(snapshot.keys()),
        )
        self.assertEqual("GRC9", snapshot["metadata"]["model_family"])
        self.assertIn("edge_label_computation_mode", snapshot["edge_labels"])
        self.assertIn("edge_label_params", snapshot["edge_labels"])
        self.assertIn("coarse_cache", snapshot["caches"])
        self.assertEqual(
            "exact_column_profile",
            snapshot["caches"]["coarse_cache"]["exact_column_profile:conductance"]["mode"],
        )
        self.assertEqual(
            model.get_state().edge_label_computation_mode,
            restored_state.edge_label_computation_mode,
        )
        self.assertEqual(model.get_state().edge_label_params, restored_state.edge_label_params)
        self.assertEqual(model.get_state().coarse_cache, restored_state.coarse_cache)
        self.assertEqual(
            model.get_state().prev_column_diagnostic,
            restored_state.prev_column_diagnostic,
        )
        self.assertEqual(
            model.get_state().expansion_registry["spark-2-0"].module_node_ids,
            restored_state.expansion_registry["spark-2-0"].module_node_ids,
        )
        self.assertEqual(
            3,
            restored_state.expansion_registry["spark-2-0"].schedule.total_substeps,
        )
        self.assertEqual(tuple(model.get_state().event_log), tuple(restored_state.event_log))
        self.assertEqual(model.get_state().rng_state, restored_state.rng_state)
        self.assertEqual(rng.random(), replay.random())

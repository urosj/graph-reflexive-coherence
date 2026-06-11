"""Config contract tests for the opt-in GRC9V3 column-H-assisted lane."""

from __future__ import annotations

import json
import math
import unittest

from pygrc.core import BACKEND_SELECTIONS_KEY, InvalidParamsError
from pygrc.models import GRC9V3, GRC9V3NodeState, GRC9V3State
from pygrc.models.grc_9 import port_to_rc
from pygrc.models.grc_9_v3_sparks import (
    COLUMN_H_COMPUTATION_VERSION,
    LANE_B_CANDIDATE_EVENT_SCHEMA_VERSION,
    LANE_B_SPARK_LANE_VERSION,
    apply_mechanical_expansion,
    compute_column_hessian_proxy,
    refresh_column_h_history,
)
from pygrc.telemetry.grc9v3_contract import (
    GRC9V3_COLUMN_H_ASSISTED_ALLOWED_GATE_REASONS,
    GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_KIND,
    GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_SCHEMA_VERSION,
    GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_REQUIRED_FIELDS,
    GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
    GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION,
    GRC9V3_COLUMN_H_COMPUTATION_VERSION,
)


def _config(
    *,
    evolution_overrides: dict[str, object] | None = None,
    **modes: object,
) -> dict[str, object]:
    evolution: dict[str, object] = {
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
        "eps_gradient": 0.01,
        "eps_hessian": 0.01,
        "eps_spark": 0.0,
        "eps_column_h": 0.001,
        "eps_column_h_crossing_zero": 0.0,
        "D_eff_target": 16,
        "w_bond": 1.0,
    }
    if evolution_overrides is not None:
        evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": dict(modes),
    }


def _column_h_state(
    *,
    occupied_ports: tuple[int, ...] = tuple(range(1, 10)),
) -> dict[str, object]:
    center_id = 0
    neighbor_coherence_by_port = {
        1: 13.0,
        2: 9.0,
        3: 7.0,
        4: 8.0,
        5: 11.0,
        6: 10.0,
        7: 10.25,
        8: 10.0,
        9: 12.0,
    }
    base_conductance_by_port = {
        1: 0.5,
        2: 1.0,
        3: 1.0,
        4: 2.0,
        5: 2.0,
        6: 2.0,
        7: 4.0,
        8: 5.0,
        9: 0.25,
    }
    nodes: list[dict[str, object]] = [
        {"node_id": center_id, "payload": {"role": "candidate"}}
    ]
    edges: list[dict[str, object]] = []
    incidence: dict[str, list[int]] = {"0": []}
    node_states: dict[str, dict[str, object]] = {
        "0": {
            "coherence": 10.0,
            "gradient_row_basis": [0.0, 0.0, 0.0],
            "signed_hessian_row_basis": [1.0, 1.0, 1.0],
            "basin_mass": 10.0,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, object]] = {}
    base_conductance: dict[str, float] = {}

    for port_id in occupied_ports:
        edge_id = port_id - 1
        neighbor_id = port_id
        remote_slot = 9 - port_id
        nodes.append({"node_id": neighbor_id, "payload": {"role": "neighbor"}})
        incidence["0"].append(edge_id)
        incidence[str(neighbor_id)] = [edge_id]
        if port_id % 2:
            endpoint_a = {"node_id": center_id, "slot": port_id - 1}
            endpoint_b = {"node_id": neighbor_id, "slot": remote_slot}
        else:
            endpoint_a = {"node_id": neighbor_id, "slot": remote_slot}
            endpoint_b = {"node_id": center_id, "slot": port_id - 1}
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": endpoint_a,
                "endpoint_b": endpoint_b,
                "payload": {"kind": "column_h_fixture"},
            }
        )
        node_states[str(neighbor_id)] = {
            "coherence": neighbor_coherence_by_port[port_id],
            "basin_mass": neighbor_coherence_by_port[port_id],
            "basin_id": neighbor_id,
        }
        port_edges[str(edge_id)] = {
            "node_u": center_id,
            "port_u": port_id,
            "node_v": neighbor_id,
            "port_v": remote_slot + 1,
            "conductance": 99.0,
            "flux_uv": 999.0,
        }
        base_conductance[str(edge_id)] = base_conductance_by_port[port_id]

    return {
        "topology": {
            "nodes": nodes,
            "edges": edges,
            "incidence": incidence,
            "port_structure": {},
        },
        "nodes": node_states,
        "port_edges": port_edges,
        "base_conductance": base_conductance,
        "sink_set": [center_id],
        "basins": {"0": [center_id, *occupied_ports]},
    }


def _parent_local_ports_by_edge(model: GRC9V3, *, parent_node_id: int) -> dict[int, int]:
    state = model.get_state()
    parent_ports: dict[int, int] = {}
    for edge_id in state.topology.incident_edge_ids(parent_node_id):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        if endpoint_a[0] == parent_node_id:
            parent_ports[edge_id] = int(endpoint_a[1]) + 1
        elif endpoint_b[0] == parent_node_id:
            parent_ports[edge_id] = int(endpoint_b[1]) + 1
        else:
            raise AssertionError(f"edge {edge_id} is not incident to {parent_node_id}")
    return parent_ports


def _remote_endpoints_by_edge(model: GRC9V3, *, parent_node_id: int) -> dict[int, tuple[int, int]]:
    state = model.get_state()
    remote_endpoints: dict[int, tuple[int, int]] = {}
    for edge_id in state.topology.incident_edge_ids(parent_node_id):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        if endpoint_a[0] == parent_node_id:
            remote_endpoints[edge_id] = endpoint_b
        elif endpoint_b[0] == parent_node_id:
            remote_endpoints[edge_id] = endpoint_a
        else:
            raise AssertionError(f"edge {edge_id} is not incident to {parent_node_id}")
    return remote_endpoints


class GRC9V3ColumnHAssistedConfigTest(unittest.TestCase):
    """Validate Iteration 1 Lane B config without changing spark behavior."""

    def test_default_config_keeps_lane_a(self) -> None:
        model = GRC9V3.from_config(_config())
        params = model.get_params()
        modes = dict(params.constitutive_semantic_modes)
        backend_payload = modes[BACKEND_SELECTIONS_KEY]

        self.assertEqual("current_hybrid_signed_hessian", modes["spark_lane"])
        self.assertTrue(modes["enable_column_h_threshold"])
        self.assertFalse(modes["enable_column_h_sign_crossing"])
        self.assertEqual("theory_product", modes["column_h_sign_crossing_mode"])
        self.assertFalse(modes["store_previous_column_h"])
        self.assertTrue(modes["require_sink_for_column_h_spark"])
        self.assertTrue(modes["require_active_degree_9"])
        self.assertFalse(modes["enable_near_saturation"])
        self.assertEqual(8, modes["near_saturation_degree"])
        self.assertEqual(0.001, params.evolution["eps_column_h"])
        self.assertEqual(0.0, params.evolution["eps_column_h_crossing_zero"])
        self.assertEqual(
            "current_hybrid_signed_hessian",
            backend_payload["spark"]["params"]["spark_lane"],
        )

    def test_explicit_lane_b_config_is_accepted(self) -> None:
        model = GRC9V3.from_config(
            _config(
                spark_lane="grc9v3_column_h_assisted",
                store_previous_column_h=True,
                enable_column_h_sign_crossing=True,
                column_h_sign_crossing_mode="theory_product",
            )
        )

        modes = dict(model.get_params().constitutive_semantic_modes)
        self.assertEqual("grc9v3_column_h_assisted", modes["spark_lane"])
        self.assertTrue(modes["enable_column_h_threshold"])
        self.assertTrue(modes["enable_column_h_sign_crossing"])
        self.assertTrue(modes["store_previous_column_h"])

    def test_unknown_lane_is_rejected(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "spark_lane must be one of"):
            GRC9V3.from_config(_config(spark_lane="canonical_column_h"))

    def test_lane_b_near_saturation_is_rejected_in_v1(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "enable_near_saturation"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    enable_near_saturation=True,
                )
            )

    def test_lane_b_requires_active_degree_nine_in_v1(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "require_active_degree_9"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    require_active_degree_9=False,
                )
            )

    def test_lane_b_requires_sink_scope_in_v1(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "require_sink_for_column_h_spark"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    require_sink_for_column_h_spark=False,
                )
            )

    def test_sign_crossing_requires_previous_h_storage(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "store_previous_column_h"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    enable_column_h_sign_crossing=True,
                    store_previous_column_h=False,
                )
            )

    def test_lane_b_requires_at_least_one_column_h_branch(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "at least one column-H branch"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    enable_column_h_threshold=False,
                    enable_column_h_sign_crossing=False,
                )
            )

    def test_column_h_numeric_params_are_validated(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "eps_column_h must be"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    evolution_overrides={"eps_column_h": -1.0},
                )
            )
        with self.assertRaisesRegex(InvalidParamsError, "eps_column_h must be"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    enable_column_h_threshold=False,
                    enable_column_h_sign_crossing=True,
                    store_previous_column_h=True,
                    evolution_overrides={"eps_column_h": -1.0},
                )
            )
        with self.assertRaisesRegex(
            InvalidParamsError,
            "eps_column_h_crossing_zero must be >= 0",
        ):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    evolution_overrides={"eps_column_h_crossing_zero": -1.0},
                )
            )

    def test_unknown_sign_crossing_mode_is_rejected(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "column_h_sign_crossing_mode"):
            GRC9V3.from_config(
                _config(
                    spark_lane="grc9v3_column_h_assisted",
                    column_h_sign_crossing_mode="product_with_deadband",
                )
            )


class GRC9V3ColumnHComputationTest(unittest.TestCase):
    """Validate Iteration 2 direct column-H diagnostic computation."""

    def test_column_h_values_match_hand_calculation(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(evolution_overrides={"eps_column_h": 1.1}),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            include_terms=True,
        )

        self.assertEqual(COLUMN_H_COMPUTATION_VERSION, result.column_h_computation_version)
        self.assertEqual(0, result.state_epoch)
        self.assertEqual((-1.5, 1.0, -2.5), result.column_h_values)
        self.assertEqual(1.0, result.min_abs_column_h)
        self.assertEqual(2, result.min_abs_column_h_column)
        self.assertTrue(result.column_h_threshold_hit)
        self.assertTrue(result.column_h_branch_hit)
        self.assertTrue(result.column_h_gate_hit)
        self.assertEqual(("column_h_threshold_hit",), result.column_h_gate_reasons)
        self.assertEqual(9, len(result.terms))

    def test_candidate_local_ports_drive_grouping_and_base_conductance(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            include_terms=True,
        )

        term_by_port = {term.port_id: term for term in result.terms}
        self.assertEqual(2, term_by_port[6].row)
        self.assertEqual(3, term_by_port[6].column)
        self.assertEqual(6, term_by_port[6].neighbor_id)
        self.assertEqual(2.0, term_by_port[6].base_conductance)
        self.assertEqual(0.0, term_by_port[6].contribution)
        self.assertNotEqual(99.0, term_by_port[6].base_conductance)

    def test_flux_coupling_does_not_change_canonical_column_h(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()
        state = model.get_state()
        baseline = compute_column_hessian_proxy(
            state,
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        state.flux_coupling = {edge_id: 1_000_000.0 for edge_id in state.base_conductance}
        changed = compute_column_hessian_proxy(
            state,
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual(baseline.column_h_values, changed.column_h_values)

    def test_base_conductance_changes_only_its_local_column(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()
        state = model.get_state()
        baseline = compute_column_hessian_proxy(
            state,
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        state.base_conductance[4] = 3.0
        changed = compute_column_hessian_proxy(
            state,
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual(baseline.column_h_values[0], changed.column_h_values[0])
        self.assertEqual(2.0, changed.column_h_values[1])
        self.assertEqual(baseline.column_h_values[2], changed.column_h_values[2])

    def test_degree_eight_node_computes_diagnostic_without_full_candidate(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(occupied_ports=tuple(range(1, 9))),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 2.0},
            ),
        )
        params = model.get_params()
        state = model.get_state()

        result = compute_column_hessian_proxy(
            state,
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual(8, len(tuple(state.topology.incident_edge_ids(0))))
        self.assertEqual((-1.5, 1.0, -3.0), result.column_h_values)
        self.assertTrue(result.column_h_threshold_hit)
        self.assertTrue(result.column_h_branch_hit)
        self.assertFalse(model.detect_hybrid_spark_candidates())

    def test_previous_column_h_storage_is_disabled_by_default(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()

        results = refresh_column_h_history(
            model.get_state(),
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual({}, results)
        self.assertNotIn("current_column_h_by_node", model.get_state().cached_quantities)
        self.assertEqual(
            "storage_disabled",
            model.get_state().cached_quantities["previous_column_h_storage_status"],
        )

    def test_previous_column_h_history_is_idempotent_per_state_epoch(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()
        state = model.get_state()

        first = refresh_column_h_history(
            state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )
        second = refresh_column_h_history(
            state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual((-1.5, 1.0, -2.5), first[0].column_h_values)
        self.assertEqual("unavailable_new_or_first_step", first[0].previous_column_h_status)
        self.assertEqual("unavailable_new_or_first_step", second[0].previous_column_h_status)
        self.assertEqual({}, state.cached_quantities["previous_column_h_by_node"])
        self.assertEqual(0, state.cached_quantities["current_column_h_state_epoch"])
        self.assertEqual(
            "grc9v3_column_h_assisted",
            state.cached_quantities["current_column_h_spark_lane"],
        )

    def test_previous_column_h_history_shifts_on_new_state_epoch(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
                evolution_overrides={"eps_column_h": 0.1},
            ),
        )
        params = model.get_params()
        state = model.get_state()
        refresh_column_h_history(
            state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        state.nodes[5].coherence = 9.0
        state.step_index += 1
        shifted = refresh_column_h_history(
            state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        self.assertEqual([-1.5, 1.0, -2.5], state.cached_quantities["previous_column_h_by_node"]["0"])
        self.assertEqual("available", shifted[0].previous_column_h_status)
        self.assertEqual((2,), shifted[0].column_h_sign_crossing_columns)
        self.assertTrue(shifted[0].column_h_sign_crossing_hit)
        self.assertEqual("updated", state.cached_quantities["previous_column_h_storage_status"])

    def test_previous_column_h_cache_is_invalidated_after_expansion(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()
        state = model.get_state()
        refresh_column_h_history(
            state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )
        state.nodes[0].signed_hessian_row_basis = [-1.0, 1.0, 1.0]
        candidate = model.detect_hybrid_spark_candidates()[0]

        apply_mechanical_expansion(
            state,
            candidate,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            source_family=GRC9V3.MODEL_FAMILY,
        )

        self.assertEqual({}, state.cached_quantities["previous_column_h_by_node"])
        self.assertEqual({}, state.cached_quantities["current_column_h_by_node"])
        self.assertEqual(
            "invalidated:hybrid_expansion_topology_change",
            state.cached_quantities["previous_column_h_storage_status"],
        )
        self.assertIn("0", state.cached_quantities["previous_column_h_invalidated_node_ids"])

    def test_duplicate_candidate_local_port_is_rejected(self) -> None:
        class DuplicatePortTopology:
            def has_node(self, node_id: int) -> bool:
                return node_id in {0, 1, 2}

            def incident_edge_ids(self, node_id: int) -> tuple[int, ...]:
                if node_id != 0:
                    return ()
                return (0, 1)

            def edge_ports(self, edge_id: int) -> tuple[tuple[int, int], tuple[int, int]]:
                if edge_id == 0:
                    return ((0, 0), (1, 0))
                return ((0, 0), (2, 1))

        state = GRC9V3State(
            topology=DuplicatePortTopology(),  # type: ignore[arg-type]
            nodes={
                0: GRC9V3NodeState(coherence=1.0),
                1: GRC9V3NodeState(coherence=2.0),
                2: GRC9V3NodeState(coherence=3.0),
            },
            base_conductance={0: 1.0, 1: 1.0},
        )

        with self.assertRaisesRegex(ValueError, "duplicate local port"):
            compute_column_hessian_proxy(
                state,
                0,
                evolution={"eps_column_h": 0.001, "eps_column_h_crossing_zero": 0.0},
                modes={},
            )

    def test_nonfinite_conductance_fails_clearly(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()
        state = model.get_state()
        state.base_conductance[0] = math.nan

        with self.assertRaisesRegex(ValueError, "base_conductance"):
            compute_column_hessian_proxy(
                state,
                0,
                evolution=params.evolution,
                modes=params.constitutive_semantic_modes,
            )

    def test_nonfinite_coherence_fails_clearly(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        params = model.get_params()
        state = model.get_state()
        state.nodes[1].coherence = math.nan

        with self.assertRaisesRegex(ValueError, "neighbor 1 coherence"):
            compute_column_hessian_proxy(
                state,
                0,
                evolution=params.evolution,
                modes=params.constitutive_semantic_modes,
            )

    def test_theory_product_sign_crossing_uses_direct_product_rule(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            previous_column_h_values=(-1.5, -0.05, -2.5),
        )

        self.assertFalse(result.column_h_threshold_hit)
        self.assertTrue(result.column_h_sign_crossing_hit)
        self.assertEqual((2,), result.column_h_sign_crossing_columns)
        self.assertTrue(result.column_h_branch_hit)
        self.assertEqual(("column_h_sign_crossing_hit",), result.column_h_gate_reasons)

    def test_theory_product_sign_crossing_fires_positive_to_negative(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            previous_column_h_values=(1.5, 1.0, 2.5),
        )

        self.assertEqual((1, 3), result.column_h_sign_crossing_columns)

    def test_theory_product_touching_zero_does_not_cross(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            previous_column_h_values=(0.0, 1.0, -2.5),
        )

        self.assertFalse(result.column_h_sign_crossing_hit)

    def test_invalid_explicit_previous_values_are_reported_unavailable(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            previous_column_h_values=(1.0, 2.0),
        )

        self.assertEqual("invalid_unavailable", result.previous_column_h_status)
        self.assertIsNone(result.previous_column_h_values)
        self.assertFalse(result.column_h_sign_crossing_hit)

    def test_zero_band_sign_crossing_suppresses_small_crossings(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
                column_h_sign_crossing_mode="zero_band",
                evolution_overrides={"eps_column_h_crossing_zero": 0.1},
            ),
        )
        params = model.get_params()

        result = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            previous_column_h_values=(-1.5, -0.05, -2.5),
        )

        self.assertEqual("zero_band", result.column_h_sign_crossing_mode)
        self.assertEqual(0.1, result.eps_column_h_crossing_zero)
        self.assertFalse(result.column_h_sign_crossing_hit)
        self.assertEqual((), result.column_h_sign_crossing_columns)
        self.assertFalse(result.column_h_branch_hit)
        self.assertFalse(result.column_h_gate_hit)


class GRC9V3ColumnHAssistedPredicateTest(unittest.TestCase):
    """Validate Iteration 4 Lane B candidate predicate behavior."""

    def test_lane_a_candidate_payload_remains_backward_compatible(self) -> None:
        model = GRC9V3.from_state(state=_column_h_state(), params=_config())
        model.get_state().nodes[0].signed_hessian_row_basis = [-0.1, 0.2, 0.3]

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        payload = candidates[0].payload
        self.assertEqual("hybrid_spark_candidate", candidates[0].kind)
        self.assertNotIn("lane_b_candidate_hit", payload)
        self.assertNotIn("spark_lane", payload)
        self.assertNotIn("column_h", payload)

    def test_lane_a_does_not_gate_on_column_h_by_default(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(evolution_overrides={"eps_column_h": 2.0}),
        )

        self.assertEqual([], model.detect_hybrid_spark_candidates())

    def test_same_fixture_contrasts_lane_a_and_lane_b_column_h_threshold(self) -> None:
        lane_a = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(evolution_overrides={"eps_column_h": 1.1}),
        )
        lane_b = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        lane_a_candidates = lane_a.detect_hybrid_spark_candidates()
        lane_b_candidates = lane_b.detect_hybrid_spark_candidates()

        self.assertEqual([], lane_a_candidates)
        self.assertEqual(1, len(lane_b_candidates))
        lane_b_payload = lane_b_candidates[0].payload
        self.assertEqual(["column_h_threshold_hit"], lane_b_payload["gate_reasons"])
        self.assertFalse(lane_b_payload["signed_hessian_hit"])
        self.assertTrue(lane_b_payload["column_h_branch_hit"])

    def test_lane_a_does_not_consume_or_update_existing_column_h_history(self) -> None:
        state_payload = _column_h_state()
        state_payload["cached_quantities"] = {
            "previous_column_h_by_node": {"0": [9.0, 9.0, 9.0]},
            "current_column_h_by_node": {"0": [-1.5, 1.0, -2.5]},
            "current_column_h_state_epoch": 0,
            "current_column_h_spark_lane": "grc9v3_column_h_assisted",
        }
        model = GRC9V3.from_state(state=state_payload, params=_config())

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual([], candidates)
        self.assertEqual(
            {"0": [9.0, 9.0, 9.0]},
            model.get_state().cached_quantities["previous_column_h_by_node"],
        )
        self.assertEqual(
            {"0": [-1.5, 1.0, -2.5]},
            model.get_state().cached_quantities["current_column_h_by_node"],
        )
        self.assertEqual(
            "grc9v3_column_h_assisted",
            model.get_state().cached_quantities["current_column_h_spark_lane"],
        )

    def test_lane_b_signed_hessian_hit_emits_candidate_without_column_h_hit(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 0.1},
            ),
        )
        model.get_state().nodes[0].signed_hessian_row_basis = [-0.1, 0.2, 0.3]

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        payload = candidates[0].payload
        self.assertEqual("grc9v3_column_h_assisted", payload["spark_lane"])
        self.assertTrue(payload["lane_b_candidate_hit"])
        self.assertTrue(payload["signed_hessian_hit"])
        self.assertFalse(payload["column_h_branch_hit"])
        self.assertEqual(["signed_hessian_hit"], payload["gate_reasons"])

    def test_lane_b_column_h_threshold_hit_emits_candidate_without_signed_hit(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        payload = candidates[0].payload
        self.assertEqual(0, payload["node_id"])
        self.assertEqual(0, payload["sink_node_id"])
        self.assertTrue(payload["sink_status"])
        self.assertFalse(payload["signed_hessian_hit"])
        self.assertEqual(payload["min_signed_hessian"], payload["signed_hessian_min"])
        self.assertEqual(payload["eps_spark"], payload["eps_signed_hessian"])
        self.assertTrue(payload["column_h_threshold_hit"])
        self.assertTrue(payload["column_h_branch_hit"])
        self.assertEqual(["column_h_threshold_hit"], payload["gate_reasons"])
        self.assertEqual(2, payload["min_abs_column_h_column"])
        self.assertEqual([], model.get_state().event_log)
        self.assertTrue(model.get_state().topology.has_node(0))

    def test_lane_b_event_payload_matches_telemetry_contract(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        payload = candidates[0].payload
        self.assertEqual(GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_KIND, candidates[0].kind)
        for field_name in GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_REQUIRED_FIELDS:
            self.assertIn(field_name, payload)
        self.assertEqual(
            GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_SCHEMA_VERSION,
            payload["event_schema_version"],
        )
        self.assertEqual(
            LANE_B_CANDIDATE_EVENT_SCHEMA_VERSION,
            payload["event_schema_version"],
        )
        self.assertEqual(
            GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            payload["spark_lane"],
        )
        self.assertEqual(
            GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION,
            payload["spark_lane_version"],
        )
        self.assertEqual(LANE_B_SPARK_LANE_VERSION, payload["spark_lane_version"])
        self.assertEqual(
            GRC9V3_COLUMN_H_COMPUTATION_VERSION,
            payload["column_h_computation_version"],
        )
        self.assertEqual(COLUMN_H_COMPUTATION_VERSION, payload["column_h_computation_version"])
        self.assertEqual("grc9v3-column-h-candidate-0-0", payload["candidate_event_id"])
        self.assertEqual(0, payload["step_index"])
        self.assertEqual(0, payload["state_epoch"])
        self.assertIsNone(payload["previous_column_h_values"])
        self.assertIsNone(payload["linked_expansion_event_id"])
        self.assertEqual(3, len(payload["column_h"]))
        self.assertTrue(
            set(payload["gate_reasons"]).issubset(
                set(GRC9V3_COLUMN_H_ASSISTED_ALLOWED_GATE_REASONS)
            )
        )
        self.assertEqual(payload, json.loads(json.dumps(payload)))

    def test_lane_b_candidate_id_is_stable_under_deterministic_rebuild(self) -> None:
        first = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        second = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        first_id = first.detect_hybrid_spark_candidates()[0].payload["candidate_event_id"]
        second_id = second.detect_hybrid_spark_candidates()[0].payload["candidate_event_id"]

        self.assertEqual("grc9v3-column-h-candidate-0-0", first_id)
        self.assertEqual(first_id, second_id)

    def test_lane_b_event_payload_matches_captured_column_h_result(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        params = model.get_params()
        captured = compute_column_hessian_proxy(
            model.get_state(),
            0,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        candidate = model.detect_hybrid_spark_candidates()[0]
        payload = candidate.payload

        self.assertEqual(list(captured.column_h_values), payload["column_h"])
        self.assertEqual(captured.min_abs_column_h, payload["min_abs_column_h"])
        self.assertEqual(
            captured.min_abs_column_h_column,
            payload["min_abs_column_h_column"],
        )
        self.assertEqual(captured.state_epoch, payload["state_epoch"])
        self.assertEqual(
            captured.column_h_computation_version,
            payload["column_h_computation_version"],
        )

    def test_lane_b_threshold_candidate_routes_to_existing_expansion(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        emitted_events = model.apply_hybrid_sparks()

        self.assertGreaterEqual(len(emitted_events), 2)
        candidate_event = emitted_events[0]
        expansion_event = emitted_events[1]
        self.assertEqual("hybrid_spark_candidate", candidate_event.kind)
        self.assertEqual("hybrid_mechanical_expansion", expansion_event.kind)
        self.assertEqual(
            "grc9v3_column_h_assisted",
            candidate_event.payload["spark_lane"],
        )
        self.assertEqual(["column_h_threshold_hit"], candidate_event.payload["gate_reasons"])
        self.assertEqual(
            expansion_event.payload["expansion_id"],
            candidate_event.payload["linked_expansion_event_id"],
        )
        self.assertEqual(
            candidate_event.payload["candidate_event_id"],
            expansion_event.payload["source_candidate_event_id"],
        )
        self.assertEqual(
            candidate_event.payload["spark_lane"],
            expansion_event.payload["source_candidate_spark_lane"],
        )
        self.assertEqual(
            candidate_event.payload["gate_reasons"],
            expansion_event.payload["source_candidate_gate_reasons"],
        )
        self.assertIn("reassignment_map", expansion_event.payload)
        self.assertAlmostEqual(0.0, expansion_event.payload["budget_error"])

    def test_lane_b_signed_hessian_only_candidate_routes_to_existing_expansion(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 0.1},
            ),
        )
        model.get_state().nodes[0].signed_hessian_row_basis = [-0.1, 0.2, 0.3]

        emitted_events = model.apply_hybrid_sparks()

        self.assertEqual(
            ["hybrid_spark_candidate", "hybrid_mechanical_expansion"],
            [event.kind for event in emitted_events],
        )
        candidate_event, expansion_event = emitted_events
        self.assertEqual(["signed_hessian_hit"], candidate_event.payload["gate_reasons"])
        self.assertFalse(candidate_event.payload["column_h_branch_hit"])
        self.assertEqual(
            expansion_event.payload["expansion_id"],
            candidate_event.payload["linked_expansion_event_id"],
        )
        self.assertEqual(
            candidate_event.payload["candidate_event_id"],
            expansion_event.payload["source_candidate_event_id"],
        )
        self.assertAlmostEqual(0.0, expansion_event.payload["budget_error"])

    def test_lane_b_sign_crossing_candidate_routes_to_existing_expansion(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        state = model.get_state()
        state.cached_quantities["current_column_h_by_node"] = {"0": [-1.5, -0.05, -2.5]}
        state.cached_quantities["current_column_h_state_epoch"] = 0
        state.step_index = 1

        emitted_events = model.apply_hybrid_sparks()

        self.assertEqual(
            ["hybrid_spark_candidate", "hybrid_mechanical_expansion"],
            [event.kind for event in emitted_events],
        )
        candidate_event, expansion_event = emitted_events
        self.assertEqual(
            ["column_h_sign_crossing_hit"],
            candidate_event.payload["gate_reasons"],
        )
        self.assertTrue(candidate_event.payload["column_h_branch_hit"])
        self.assertEqual([2], candidate_event.payload["column_h_sign_crossing_columns"])
        self.assertEqual(
            expansion_event.payload["expansion_id"],
            candidate_event.payload["linked_expansion_event_id"],
        )
        self.assertEqual(
            candidate_event.payload["candidate_event_id"],
            expansion_event.payload["source_candidate_event_id"],
        )
        self.assertEqual([-1.5, -0.05, -2.5], candidate_event.payload["previous_column_h_values"])

    def test_lane_b_expansion_reassignment_preserves_old_columns(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        pre_expansion_ports_by_edge = _parent_local_ports_by_edge(model, parent_node_id=0)
        pre_expansion_remote_by_edge = _remote_endpoints_by_edge(model, parent_node_id=0)

        emitted_events = model.apply_hybrid_sparks()

        expansion_event = emitted_events[1]
        reassignment_map = expansion_event.payload["reassignment_map"]
        self.assertEqual(9, len(reassignment_map))
        self.assertFalse(model.get_state().topology.has_node(0))
        for edge_id_text, reassignment in reassignment_map.items():
            edge_id = int(edge_id_text)
            old_port_id = pre_expansion_ports_by_edge[edge_id]
            old_remote_endpoint = pre_expansion_remote_by_edge[edge_id]
            from_port_id = int(reassignment["from_port_id"])
            to_port_id = int(reassignment["to_port_id"])
            self.assertEqual(old_port_id, from_port_id)
            _, old_column = port_to_rc(from_port_id)
            _, new_column = port_to_rc(to_port_id)
            self.assertEqual(old_column, new_column)
            self.assertIn(old_remote_endpoint, model.get_state().topology.edge_ports(edge_id))

    def test_lane_b_candidate_detection_does_not_expand_or_complete_identity(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        self.assertEqual([], model.get_state().event_log)
        self.assertTrue(model.get_state().topology.has_node(0))
        self.assertNotIn("last_hybrid_expansion", model.get_state().cached_quantities)
        self.assertNotIn("last_completed_hybrid_spark", model.get_state().cached_quantities)

    def test_lane_b_mechanical_expansion_is_not_identity_acceptance(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        emitted_events = model.apply_hybrid_sparks()

        self.assertEqual(
            ["hybrid_spark_candidate", "hybrid_mechanical_expansion"],
            [event.kind for event in emitted_events],
        )
        self.assertNotIn("hybrid_spark_completed", [event.kind for event in emitted_events])
        self.assertNotIn("last_completed_hybrid_spark", model.get_state().cached_quantities)

    def test_lane_b_column_h_sign_crossing_hit_emits_candidate(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_threshold=False,
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        state = model.get_state()
        state.cached_quantities["current_column_h_by_node"] = {"0": [-1.5, -0.05, -2.5]}
        state.cached_quantities["current_column_h_state_epoch"] = 0
        state.step_index = 1

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        payload = candidates[0].payload
        self.assertFalse(payload["signed_hessian_hit"])
        self.assertFalse(payload["column_h_threshold_hit"])
        self.assertTrue(payload["column_h_sign_crossing_hit"])
        self.assertEqual([2], payload["column_h_sign_crossing_columns"])
        self.assertEqual(["column_h_sign_crossing_hit"], payload["gate_reasons"])

    def test_lane_b_signed_and_column_h_hits_emit_one_candidate_with_both_reasons(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        model.get_state().nodes[0].signed_hessian_row_basis = [-0.1, 0.2, 0.3]

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        self.assertEqual(
            ["signed_hessian_hit", "column_h_threshold_hit"],
            candidates[0].payload["gate_reasons"],
        )

    def test_lane_b_degree_eight_column_h_hit_emits_no_candidate(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(occupied_ports=tuple(range(1, 9))),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 2.0},
            ),
        )

        self.assertEqual([], model.detect_hybrid_spark_candidates())

    def test_lane_b_large_gradient_column_h_hit_emits_no_candidate(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        model.get_state().nodes[0].gradient_row_basis = [1.0, 0.0, 0.0]

        self.assertEqual([], model.detect_hybrid_spark_candidates())

    def test_lane_b_fullness_without_spark_branch_emits_no_candidate(self) -> None:
        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 0.1},
            ),
        )

        self.assertEqual([], model.detect_hybrid_spark_candidates())

    def test_lane_b_non_sink_emits_no_candidate(self) -> None:
        state = _column_h_state()
        state["sink_set"] = []
        model = GRC9V3.from_state(
            state=state,
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )

        self.assertEqual([], model.detect_hybrid_spark_candidates())

    def test_lane_b_threshold_equalities_follow_strict_less_than(self) -> None:
        column_equal = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.0},
            ),
        )
        self.assertEqual([], column_equal.detect_hybrid_spark_candidates())

        gradient_equal = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        gradient_equal.get_state().nodes[0].gradient_row_basis = [0.01, 0.0, 0.0]
        self.assertEqual([], gradient_equal.detect_hybrid_spark_candidates())

        signed_equal = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 0.1},
            ),
        )
        signed_equal.get_state().nodes[0].signed_hessian_row_basis = [0.0, 0.2, 0.3]
        self.assertEqual([], signed_equal.detect_hybrid_spark_candidates())


if __name__ == "__main__":
    unittest.main()

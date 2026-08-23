"""Runtime-faithful preparation and reachability methods for B2-GR I4."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

from b2_artifact_io import REPO_ROOT, semantic_digest


SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402
from pygrc.models.grc_9_v3 import _state_payload_from_state  # noqa: E402


HISTORY_LENGTHS = (1, 2, 4, 8)
AMPLITUDE_FRACTIONS = (0.0001, 0.001, 0.01)
PARAMETER_VARIANTS = (
    ("dt_x_0p5", "dt", 0.5),
    ("dt_x_1p5", "dt", 1.5),
    ("eta_x_0p5", "eta", 0.5),
    ("eta_x_2p0", "eta", 2.0),
)
CURRENT_ZERO_BAND = 1e-10
CONDUCTANCE_FLOOR = 1e-12


def _l_inf(values: np.ndarray) -> float:
    return float(np.linalg.norm(values, ord=np.inf)) if values.size else 0.0


def _vector_delta(before: np.ndarray, after: np.ndarray) -> dict[str, Any]:
    delta = after - before
    return {
        "changed": bool(np.any(delta != 0.0)),
        "delta_l_inf": _l_inf(delta),
        "delta_l2": float(np.linalg.norm(delta)),
    }


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(child) for child in value]
    return deepcopy(value)


class InstrumentedGRC9V3(GRC9V3):
    """Observe native stages without replacing or reordering ``step()``."""

    def __init__(self, *, params: Any, state: Any | None = None) -> None:
        super().__init__(params=params, state=state)
        self.b2_budget_audits: list[dict[str, Any]] = []
        self.b2_boundary_audits: list[dict[str, Any]] = []
        self.b2_transport_audits: list[dict[str, Any]] = []
        self.b2_completed_step_audits: list[dict[str, Any]] = []

    def rebuild_transport_state(self) -> None:
        before_w = conductance_vector(self)
        before_j = current_vector(self)
        super().rebuild_transport_state()
        after_w = conductance_vector(self)
        after_j = current_vector(self)
        self.b2_transport_audits.append(
            {
                "step_index_before_increment": int(self.get_state().step_index),
                "W": after_w.tolist(),
                "J": after_j.tolist(),
                "W_change": _vector_delta(before_w, after_w),
                "J_change": _vector_delta(before_j, after_j),
                "conductance_floor_active": bool(np.any(after_w <= CONDUCTANCE_FLOOR)),
            }
        )

    def apply_boundary_behavior(self) -> None:
        before_c = coherence_vector(self)
        before_nodes = node_order(self)
        before_edges = edge_order(self)
        super().apply_boundary_behavior()
        after_c = coherence_vector(self)
        topology_changed = before_nodes != node_order(
            self
        ) or before_edges != edge_order(self)
        self.b2_boundary_audits.append(
            {
                "step_index_before_increment": int(self.get_state().step_index),
                "C_change": (
                    _vector_delta(before_c, after_c)
                    if not topology_changed
                    else {
                        "changed": True,
                        "delta_l_inf": 0.0,
                        "delta_l2": 0.0,
                        "comparison_status": "not_comparable_topology_changed",
                    }
                ),
                "topology_changed": topology_changed,
            }
        )

    def enforce_quadrature_budget(self) -> dict[str, Any]:
        before = coherence_vector(self)
        summary = super().enforce_quadrature_budget()
        after = coherence_vector(self)
        correction = after - before
        self.b2_budget_audits.append(
            {
                "step_index_before_increment": int(self.get_state().step_index),
                "mechanism_executed": True,
                "mechanism_changed_state": bool(np.any(correction != 0.0)),
                "pre_budget_minimum_C": float(np.min(before)),
                "post_budget_minimum_C": float(np.min(after)),
                "correction_l_inf": _l_inf(correction),
                "correction_l2": float(np.linalg.norm(correction)),
                "pre_budget_sum": float(np.sum(before)),
                "post_budget_sum": float(np.sum(after)),
                "summary": deepcopy(summary),
            }
        )
        return summary

    def step(self) -> Any:
        before = runtime_state(self)
        initial_events = len(self.get_state().event_log)
        initial_nodes = node_order(self)
        initial_edges = edge_order(self)
        start_budget = len(self.b2_budget_audits)
        start_boundary = len(self.b2_boundary_audits)
        start_transport = len(self.b2_transport_audits)
        result = super().step()
        after = runtime_state(self)
        budgets = deepcopy(self.b2_budget_audits[start_budget:])
        boundaries = deepcopy(self.b2_boundary_audits[start_boundary:])
        transports = deepcopy(self.b2_transport_audits[start_transport:])
        final_w = np.asarray(after["W"], dtype=float)
        maximum_internal_w_to_final = max(
            (_l_inf(np.asarray(row["W"], dtype=float) - final_w) for row in transports),
            default=0.0,
        )
        self.b2_completed_step_audits.append(
            {
                "before_state_digest": before["state_digest"],
                "after_state_digest": after["state_digest"],
                "before_step_index": before["step_index"],
                "after_step_index": after["step_index"],
                "before_time": before["time"],
                "after_time": after["time"],
                "event_count": len(self.get_state().event_log) - initial_events,
                "event_kinds": after["event_kinds"][initial_events:],
                "fixed_topology": node_order(self) == initial_nodes
                and edge_order(self) == initial_edges,
                "rng_state_unchanged": before["rng_state_sha256"]
                == after["rng_state_sha256"],
                "categorical_signature_before": before["categorical_signature"],
                "categorical_signature_after": after["categorical_signature"],
                "categorical_signature_changed": before["categorical_signature_digest"]
                != after["categorical_signature_digest"],
                "budget_stage_audits": budgets,
                "boundary_stage_audits": boundaries,
                "transport_stage_count": len(transports),
                "transport_stage_W": [row["W"] for row in transports],
                "maximum_internal_W_to_complete_step_l_inf": maximum_internal_w_to_final,
                "conductance_floor_active_in_any_transport_stage": any(
                    row["conductance_floor_active"] for row in transports
                ),
            }
        )
        return result


def node_order(model: GRC9V3) -> tuple[int, ...]:
    return tuple(sorted(model.get_state().topology.iter_live_node_ids()))


def edge_order(model: GRC9V3) -> tuple[int, ...]:
    return tuple(sorted(model.get_state().topology.iter_live_edge_ids()))


def coherence_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.nodes[node_id].coherence) for node_id in node_order(model)],
        dtype=float,
    )


def conductance_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.base_conductance[edge_id]) for edge_id in edge_order(model)],
        dtype=float,
    )


def current_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.port_edges[edge_id].flux_uv) for edge_id in edge_order(model)],
        dtype=float,
    )


def categorical_signature(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    current_sign = {}
    for edge_id in edge_order(model):
        value = float(state.port_edges[edge_id].flux_uv)
        current_sign[str(edge_id)] = (
            "zero"
            if abs(value) <= CURRENT_ZERO_BAND
            else ("positive" if value > 0.0 else "negative")
        )
    return {
        "topology_nodes": list(node_order(model)),
        "topology_edges": list(edge_order(model)),
        "edge_ports": {
            str(edge_id): [
                list(endpoint) for endpoint in state.topology.edge_ports(edge_id)
            ]
            for edge_id in edge_order(model)
        },
        "current_sign_class": current_sign,
        "sink_set": list(sorted(state.sink_set)),
        "basins": {
            str(key): list(sorted(value)) for key, value in sorted(state.basins.items())
        },
        "hierarchy": {
            str(key): list(value)
            for key, value in sorted(
                state.hierarchy.items(), key=lambda item: str(item[0])
            )
        },
        "expansion_registry_keys": list(sorted(state.expansion_registry)),
        "choice_registry_keys": list(sorted(state.choice_registry)),
        "collapse_registry_keys": list(sorted(state.collapse_registry)),
        "event_kinds": [event.kind for event in state.event_log],
    }


def complete_admitted_causal_state_digest(model: GRC9V3) -> str:
    """Digest current causal state while excluding B1-classified observer surfaces."""

    payload = _state_payload_from_state(model.get_state())
    observer_only_fields = {"coarse_cache", "event_log", "observables"}
    causal_payload = {
        key: value for key, value in payload.items() if key not in observer_only_fields
    }
    return semantic_digest(causal_payload)


def clone_instrumented(
    model: GRC9V3, params: dict[str, Any] | None = None
) -> InstrumentedGRC9V3:
    raw = _plain(params if params is not None else model.get_params().raw_config)
    return InstrumentedGRC9V3.from_state(deepcopy(model.get_state()), raw)


def runtime_state(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    categorical = categorical_signature(model)
    result = {
        "C": coherence_vector(model).tolist(),
        "W": conductance_vector(model).tolist(),
        "J": current_vector(model).tolist(),
        "step_index": int(state.step_index),
        "time": float(state.time),
        "budget_target": float(state.budget_target),
        "coherence_sum": float(np.sum(coherence_vector(model))),
        "minimum_C": float(np.min(coherence_vector(model))),
        "minimum_W": float(np.min(conductance_vector(model))),
        "rng_state_sha256": semantic_digest(state.rng_state),
        "params_identity_recorded_in_state": state.params_identity,
        "active_model_parameter_digest": semantic_digest(
            _plain(model.get_params().raw_config)
        ),
        "topology_nodes": list(node_order(model)),
        "topology_edges": list(edge_order(model)),
        "event_count": len(state.event_log),
        "event_kinds": [event.kind for event in state.event_log],
        "categorical_signature": categorical,
        "categorical_signature_digest": semantic_digest(categorical),
        "complete_admitted_causal_state_digest": (
            complete_admitted_causal_state_digest(model)
        ),
        "excluded_observer_only_state_fields": [
            "coarse_cache",
            "event_log",
            "observables",
        ],
    }
    result["state_digest"] = semantic_digest(result)
    return result


def step_audit(model: InstrumentedGRC9V3, count: int) -> dict[str, Any]:
    initial_events = len(model.get_state().event_log)
    initial_nodes = node_order(model)
    initial_edges = edge_order(model)
    initial_steps = len(model.b2_completed_step_audits)
    initial_state = runtime_state(model)
    for _ in range(count):
        model.step()
    steps = deepcopy(model.b2_completed_step_audits[initial_steps:])
    budgets = [audit for step in steps for audit in step["budget_stage_audits"]]
    boundaries = [audit for step in steps for audit in step["boundary_stage_audits"]]
    final_state = runtime_state(model)
    return {
        "native_step_count": count,
        "initial_state_digest": initial_state["state_digest"],
        "final_state_digest": final_state["state_digest"],
        "event_count": len(model.get_state().event_log) - initial_events,
        "fixed_topology": node_order(model) == initial_nodes
        and edge_order(model) == initial_edges,
        "budget_stage_executed_count": len(budgets),
        "budget_stage_changed_state_count": sum(
            audit["mechanism_changed_state"] for audit in budgets
        ),
        "maximum_budget_correction_l_inf": max(
            (audit["correction_l_inf"] for audit in budgets), default=0.0
        ),
        "minimum_pre_budget_C": min(
            (audit["pre_budget_minimum_C"] for audit in budgets),
            default=float(np.min(coherence_vector(model))),
        ),
        "minimum_post_budget_C": min(
            (audit["post_budget_minimum_C"] for audit in budgets),
            default=float(np.min(coherence_vector(model))),
        ),
        "boundary_stage_executed_count": len(boundaries),
        "boundary_stage_changed_state_count": sum(
            audit["C_change"]["changed"] or audit["topology_changed"]
            for audit in boundaries
        ),
        "maximum_boundary_C_change_l_inf": max(
            (audit["C_change"]["delta_l_inf"] for audit in boundaries), default=0.0
        ),
        "conductance_floor_active": any(
            step["conductance_floor_active_in_any_transport_stage"] for step in steps
        ),
        "maximum_internal_W_to_complete_step_l_inf": max(
            (step["maximum_internal_W_to_complete_step_l_inf"] for step in steps),
            default=0.0,
        ),
        "categorical_signature_changed": any(
            step["categorical_signature_changed"] for step in steps
        ),
        "rng_state_unchanged": initial_state["rng_state_sha256"]
        == final_state["rng_state_sha256"],
        "steps": steps,
    }


def modified_params(
    raw_config: dict[str, Any], parameter_name: str | None, multiplier: float | None
) -> dict[str, Any]:
    result = deepcopy(raw_config)
    if parameter_name is None:
        return result
    if parameter_name == "dt":
        result["dt"] = float(result["dt"]) * float(multiplier)
    elif parameter_name == "eta":
        result["evolution"]["eta"] = float(result["evolution"]["eta"]) * float(
            multiplier
        )
    else:
        raise ValueError(f"unsupported I4 parameter history: {parameter_name}")
    return result


def apply_pair_pulse(
    model: GRC9V3, source_node: int, destination_node: int, amount: float
) -> tuple[InstrumentedGRC9V3, np.ndarray]:
    state = deepcopy(model.get_state())
    nodes = node_order(model)
    index = {node_id: offset for offset, node_id in enumerate(nodes)}
    authored = np.zeros(len(nodes), dtype=float)
    authored[index[source_node]] = -float(amount)
    authored[index[destination_node]] = float(amount)
    proposed = coherence_vector(model) + authored
    if float(np.min(proposed)) <= 0.0:
        raise ValueError("pair_pulse_outside_positive_coherence_interior")
    for node_id, value in zip(nodes, proposed, strict=True):
        state.nodes[node_id].coherence = float(value)
    return (
        InstrumentedGRC9V3.from_state(state, _plain(model.get_params().raw_config)),
        authored,
    )


def oriented_edges(model: GRC9V3) -> list[tuple[int, int, int, str]]:
    result: list[tuple[int, int, int, str]] = []
    state = model.get_state()
    for edge_id in edge_order(model):
        edge = state.port_edges[edge_id]
        result.extend(
            (
                (edge_id, int(edge.node_u), int(edge.node_v), "u_to_v"),
                (edge_id, int(edge.node_v), int(edge.node_u), "v_to_u"),
            )
        )
    return result


def attempt_specs(model: GRC9V3, branch_id: str) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        {
            "attempt_id": f"{branch_id}--native-spontaneous",
            "preparation_family": "native_spontaneous_no_driver",
            "history_length": 1,
            "amplitude_fraction": 0.0,
            "edge_id": None,
            "source_node": None,
            "destination_node": None,
            "orientation": "not_applicable",
            "parameter_variant_id": "evaluation_parameters",
            "parameter_name": None,
            "parameter_multiplier": None,
        }
    ]
    for edge_id, source_node, destination_node, orientation in oriented_edges(model):
        for amplitude in AMPLITUDE_FRACTIONS:
            for history_length in HISTORY_LENGTHS:
                common = {
                    "history_length": history_length,
                    "amplitude_fraction": amplitude,
                    "edge_id": edge_id,
                    "source_node": source_node,
                    "destination_node": destination_node,
                    "orientation": orientation,
                }
                specs.append(
                    {
                        **common,
                        "attempt_id": (
                            f"{branch_id}--C-pulse--e{edge_id}-{orientation}--"
                            f"a{amplitude:.4f}--h{history_length}"
                        ),
                        "preparation_family": "budget_respecting_zero_sum_C_pair_pulse",
                        "parameter_variant_id": "evaluation_parameters",
                        "parameter_name": None,
                        "parameter_multiplier": None,
                    }
                )
                for variant_id, parameter_name, multiplier in PARAMETER_VARIANTS:
                    specs.append(
                        {
                            **common,
                            "attempt_id": (
                                f"{branch_id}--parameter-history--e{edge_id}-{orientation}--"
                                f"a{amplitude:.4f}--{variant_id}--h{history_length}"
                            ),
                            "preparation_family": "temporary_parameter_history_after_C_pair_pulse",
                            "parameter_variant_id": variant_id,
                            "parameter_name": parameter_name,
                            "parameter_multiplier": multiplier,
                        }
                    )
    ordered = sorted(specs, key=lambda row: row["attempt_id"])
    for attempt_index, spec in enumerate(ordered):
        spec["attempt_index_within_branch"] = attempt_index
        spec["allocated_budget_slot"] = f"{branch_id}:{attempt_index:04d}"
        spec["search_row_id"] = semantic_digest(
            {
                "source_branch_id": branch_id,
                "attempt_index": attempt_index,
                "preparation": spec,
            }
        )
    return ordered


def source_reconstruction_audit(
    model: GRC9V3,
    branch_row: dict[str, Any],
    registry_row: dict[str, Any],
) -> dict[str, Any]:
    coherence = coherence_vector(model).tolist()
    parameter_hash = str(model.get_params().params_hash)
    canonical_signature = semantic_digest(
        {
            "fixture_id": branch_row["fixture_id"],
            "sorted_coherence": sorted(round(value, 12) for value in coherence),
            "parameter_hash": registry_row["parameter_hash"],
        }
    )
    source_state = runtime_state(model)
    hold = clone_instrumented(model)
    hold_audit = step_audit(hold, 1)
    hold_state = runtime_state(hold)
    physical_hold_residual = max(
        _l_inf(np.asarray(hold_state[key]) - np.asarray(source_state[key]))
        for key in ("C", "W", "J")
    )
    checks = {
        "branch_id_matches": branch_row["branch_id"] == registry_row["branch_id"],
        "coherence_matches_registry": np.array_equal(
            np.asarray(coherence), np.asarray(registry_row["coherence"])
        ),
        "runtime_parameter_digest_matches_crosswalk": parameter_hash
        == branch_row["runtime_parameter_vector_digest"],
        "B1_search_parameter_hash_matches_registry": registry_row["parameter_hash"]
        == branch_row["parameter_hash"],
        "canonical_branch_signature_matches": canonical_signature
        == branch_row["canonical_branch_signature"]
        == registry_row["canonical_branch_signature"],
        "topology_node_order_matches": list(node_order(model))
        == branch_row["node_order"],
        "topology_edge_order_matches": list(edge_order(model))
        == branch_row["edge_order"],
        "fresh_fixed_branch_hold_event_free": hold_audit["event_count"] == 0,
        "fresh_fixed_branch_hold_topology_fixed": hold_audit["fixed_topology"],
        "fresh_fixed_branch_hold_budget_noop": hold_audit[
            "maximum_budget_correction_l_inf"
        ]
        <= 1e-10,
        "fresh_fixed_branch_hold_physical_residual_within_tolerance": physical_hold_residual
        <= 1e-10,
    }
    return {
        "source_branch_id": branch_row["branch_id"],
        "source_state_digest": source_state["state_digest"],
        "canonical_branch_signature_observed": canonical_signature,
        "fresh_hold_physical_l_inf": physical_hold_residual,
        "fresh_hold_audit": hold_audit,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "source_replay_failure",
    }


def _authored_projection(
    observed_delta: np.ndarray, authored_direction: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    denominator = float(np.dot(authored_direction, authored_direction))
    if denominator == 0.0:
        projected = np.zeros_like(observed_delta)
    else:
        projected = (
            float(np.dot(observed_delta, authored_direction)) / denominator
        ) * authored_direction
    return projected, observed_delta - projected


def carrier_measurements(
    positive: GRC9V3,
    sham: GRC9V3,
    authored_c: np.ndarray,
    formation_floor: float,
    numerical_uncertainty: float,
) -> dict[str, dict[str, Any]]:
    delta_c = coherence_vector(positive) - coherence_vector(sham)
    delta_w = conductance_vector(positive) - conductance_vector(sham)
    authored_projection, runtime_c = _authored_projection(delta_c, authored_c)
    c_scale = max(float(np.linalg.norm(coherence_vector(sham))), 1e-12)
    w_scale = max(float(np.linalg.norm(conductance_vector(sham))), 1e-12)
    apparent_c = float(np.linalg.norm(delta_c)) / c_scale
    authored_c_norm = float(np.linalg.norm(authored_projection)) / c_scale
    residual_c = float(np.linalg.norm(runtime_c)) / c_scale
    residual_w = float(np.linalg.norm(delta_w)) / w_scale
    apparent_joint = math.sqrt(apparent_c**2 + residual_w**2) / math.sqrt(2.0)
    authored_joint = authored_c_norm / math.sqrt(2.0)
    residual_joint = math.sqrt(residual_c**2 + residual_w**2) / math.sqrt(2.0)
    separation_floor = max(1e-10, 10.0 * float(numerical_uncertainty))

    def row(
        carrier_definition_id: str,
        apparent: float,
        authored: float,
        residual: float,
        formation_vector: list[float],
        apparent_vector: list[float],
        authored_vector: list[float],
        attribution: str,
    ) -> dict[str, Any]:
        positive = residual > float(formation_floor) and residual > separation_floor
        return {
            "carrier_definition_id": carrier_definition_id,
            "apparent_norm": apparent,
            "authored_component_norm": authored,
            "runtime_generated_residual_norm": residual,
            "formation_floor": float(formation_floor),
            "formation_margin": residual - float(formation_floor),
            "carrier_separation_floor": separation_floor,
            "carrier_separation_margin": residual - separation_floor,
            "apparent_carrier_vector": apparent_vector,
            "driver_authored_carrier_vector": authored_vector,
            "runtime_generated_formation_vector": formation_vector,
            "formation_attribution_rule": attribution,
            "full_apparent_carrier_used_for_formation": False,
            "authored_component_excluded": True,
            "discovery_positive": positive,
            "formation_status": (
                "runtime_generated_component_above_floor"
                if positive
                else "runtime_generated_component_not_above_floor"
            ),
        }

    return {
        "C_ZERO_SUM_V1": row(
            "C_ZERO_SUM_V1",
            apparent_c,
            authored_c_norm,
            residual_c,
            runtime_c.tolist(),
            delta_c.tolist(),
            authored_projection.tolist(),
            "orthogonal_projection_off_direct_authored_C_direction",
        ),
        "W_EDGE_CONDUCTANCE_OBSERVATION_V1": row(
            "W_EDGE_CONDUCTANCE_OBSERVATION_V1",
            residual_w,
            0.0,
            residual_w,
            delta_w.tolist(),
            delta_w.tolist(),
            np.zeros_like(delta_w).tolist(),
            "complete_step_W_delta_not_directly_authored_by_C_driver",
        ),
        "JOINT_C_W_BLOCK_V1": row(
            "JOINT_C_W_BLOCK_V1",
            apparent_joint,
            authored_joint,
            residual_joint,
            [*runtime_c.tolist(), *delta_w.tolist()],
            [*delta_c.tolist(), *delta_w.tolist()],
            [*authored_projection.tolist(), *np.zeros_like(delta_w).tolist()],
            "equal_weight_normalized_C_authorship_excluded_plus_complete_step_W",
        ),
    }


def _selected_carrier(
    carrier_rows: dict[str, dict[str, Any]], priority: list[str]
) -> str | None:
    return next(
        (
            carrier_id
            for carrier_id in priority
            if carrier_rows[carrier_id]["discovery_positive"]
        ),
        None,
    )


def _paired_path_summary(
    positive: dict[str, Any], sham: dict[str, Any], tolerance: float
) -> dict[str, Any]:
    budget_stage_executed = (
        positive["budget_stage_executed_count"] > 0
        or sham["budget_stage_executed_count"] > 0
    )
    budget_stage_changed_state = (
        positive["budget_stage_changed_state_count"] > 0
        or sham["budget_stage_changed_state_count"] > 0
    )
    boundary_stage_executed = (
        positive["boundary_stage_executed_count"] > 0
        or sham["boundary_stage_executed_count"] > 0
    )
    boundary_stage_changed_state = (
        positive["boundary_stage_changed_state_count"] > 0
        or sham["boundary_stage_changed_state_count"] > 0
    )
    return {
        "native_step_counts_match": positive["native_step_count"]
        == sham["native_step_count"],
        "event_free": positive["event_count"] == 0 and sham["event_count"] == 0,
        "fixed_topology": positive["fixed_topology"] and sham["fixed_topology"],
        "budget_stage_executed": budget_stage_executed,
        "budget_stage_changed_state": budget_stage_changed_state,
        "load_bearing_budget_projection": budget_stage_changed_state,
        "maximum_budget_correction_l_inf": max(
            positive["maximum_budget_correction_l_inf"],
            sham["maximum_budget_correction_l_inf"],
        ),
        "boundary_stage_executed": boundary_stage_executed,
        "boundary_stage_changed_state": boundary_stage_changed_state,
        "load_bearing_boundary_or_clipping": boundary_stage_changed_state,
        "maximum_boundary_C_change_l_inf": max(
            positive["maximum_boundary_C_change_l_inf"],
            sham["maximum_boundary_C_change_l_inf"],
        ),
        "counterfactual_delta_status": (
            "not_available_without_replacing_or_reordering_native_step"
        ),
        "magnitude_tolerance_recorded_not_used_to_excuse_state_change": tolerance,
        "conductance_floor_active": positive["conductance_floor_active"]
        or sham["conductance_floor_active"],
        "constraint_stage_executed_without_state_change": (
            positive["budget_stage_executed_count"] > 0
            and sham["budget_stage_executed_count"] > 0
            and positive["budget_stage_changed_state_count"] == 0
            and sham["budget_stage_changed_state_count"] == 0
            and positive["boundary_stage_changed_state_count"] == 0
            and sham["boundary_stage_changed_state_count"] == 0
        ),
        "categorical_signature_changed": positive["categorical_signature_changed"]
        or sham["categorical_signature_changed"],
    }


def _segment_failure_modes(segment: dict[str, Any], scope: str) -> list[str]:
    failures: list[str] = []
    if not segment["event_free"]:
        failures.append(f"eventful_{scope}")
    if not segment["fixed_topology"]:
        failures.append(f"topology_mutation_in_{scope}")
    if segment["load_bearing_budget_projection"]:
        failures.append(f"constraint_supported_{scope}")
    if segment["load_bearing_boundary_or_clipping"]:
        failures.append(f"boundary_or_clipping_supported_{scope}")
    if segment["conductance_floor_active"]:
        failures.append(f"conductance_floor_supported_{scope}")
    if segment["categorical_signature_changed"]:
        failures.append(f"categorical_transition_in_{scope}")
    return failures


def _path_failure_modes(
    history: dict[str, Any],
    continuation: dict[str, Any],
    *,
    rng_matched_at_k0: bool,
    administrative_matched_at_k0: bool,
    positive_interior_preserved: bool,
) -> list[str]:
    failures = [
        *_segment_failure_modes(history, "preparation_history"),
        *_segment_failure_modes(continuation, "first_post_driver_transition"),
    ]
    if not rng_matched_at_k0:
        failures.append("causal_rng_state_not_matched_at_k0")
    if not administrative_matched_at_k0:
        failures.append("administrative_phase_not_matched_at_k0")
    if not positive_interior_preserved:
        failures.append("positive_coherence_interior_not_preserved")
    return failures


def _internal_stage_comparison(
    positive: dict[str, Any], sham: dict[str, Any]
) -> dict[str, Any]:
    maximum = 0.0
    aligned = len(positive["steps"]) == len(sham["steps"])
    for positive_step, sham_step in zip(positive["steps"], sham["steps"], strict=False):
        positive_stages = positive_step["transport_stage_W"]
        sham_stages = sham_step["transport_stage_W"]
        aligned = aligned and len(positive_stages) == len(sham_stages)
        for positive_w, sham_w in zip(positive_stages, sham_stages, strict=False):
            positive_vector = np.asarray(positive_w, dtype=float)
            sham_vector = np.asarray(sham_w, dtype=float)
            scale = max(float(np.linalg.norm(sham_vector)), 1e-12)
            maximum = max(maximum, _l_inf(positive_vector - sham_vector) / scale)
    return {
        "stage_sequences_aligned": aligned,
        "maximum_normalized_positive_sham_internal_W_delta": maximum,
    }


def evaluate_attempt(
    base_model: GRC9V3,
    branch_row: dict[str, Any],
    source_audit: dict[str, Any],
    spec: dict[str, Any],
    *,
    formation_floor: float,
    numerical_uncertainty: float,
    persistence_horizon: int,
    carrier_priority: list[str],
) -> dict[str, Any]:
    evaluation_params = _plain(base_model.get_params().raw_config)
    history_params = modified_params(
        evaluation_params, spec["parameter_name"], spec["parameter_multiplier"]
    )
    source_state = runtime_state(base_model)
    authored_c = np.zeros(len(node_order(base_model)), dtype=float)
    pulse_amount = 0.0
    if spec["preparation_family"] == "native_spontaneous_no_driver":
        positive = clone_instrumented(base_model)
    else:
        pulse_amount = float(spec["amplitude_fraction"]) * float(
            np.sum(coherence_vector(base_model))
        )
        positive, authored_c = apply_pair_pulse(
            base_model,
            int(spec["source_node"]),
            int(spec["destination_node"]),
            pulse_amount,
        )
    sham = clone_instrumented(base_model)
    positive = InstrumentedGRC9V3.from_state(
        deepcopy(positive.get_state()), history_params
    )
    sham = InstrumentedGRC9V3.from_state(deepcopy(sham.get_state()), history_params)
    positive_history_audit = step_audit(positive, int(spec["history_length"]))
    sham_history_audit = step_audit(sham, int(spec["history_length"]))

    # Parameter restoration defines k=0; no washout transition is inserted.
    positive = InstrumentedGRC9V3.from_state(
        deepcopy(positive.get_state()), evaluation_params
    )
    sham = InstrumentedGRC9V3.from_state(deepcopy(sham.get_state()), evaluation_params)
    positive_k0 = runtime_state(positive)
    sham_k0 = runtime_state(sham)
    row_numerical_uncertainty = max(
        float(numerical_uncertainty), float(source_audit["fresh_hold_physical_l_inf"])
    )
    carrier_rows = carrier_measurements(
        positive, sham, authored_c, formation_floor, row_numerical_uncertainty
    )
    selected_carrier_id = _selected_carrier(carrier_rows, carrier_priority)

    positive_after = clone_instrumented(positive)
    sham_after = clone_instrumented(sham)
    positive_post_driver_audit = step_audit(positive_after, persistence_horizon)
    sham_post_driver_audit = step_audit(sham_after, persistence_horizon)
    carrier_rows_after = carrier_measurements(
        positive_after,
        sham_after,
        authored_c,
        formation_floor,
        row_numerical_uncertainty,
    )
    selected_after = _selected_carrier(carrier_rows_after, carrier_priority)

    budget_tolerance = max(1e-10, 10.0 * row_numerical_uncertainty)
    history_path = _paired_path_summary(
        positive_history_audit, sham_history_audit, budget_tolerance
    )
    continuation_path = _paired_path_summary(
        positive_post_driver_audit, sham_post_driver_audit, budget_tolerance
    )
    rng_matched_at_k0 = positive_k0["rng_state_sha256"] == sham_k0["rng_state_sha256"]
    administrative_matched_at_k0 = (
        positive_k0["step_index"] == sham_k0["step_index"]
        and positive_k0["time"] == sham_k0["time"]
    )
    source_reconstruction_passed = source_audit["status"] == "passed"
    k0_positive_interior_preserved = (
        positive_k0["minimum_C"] > 0.0 and sham_k0["minimum_C"] > 0.0
    )
    continuation_positive_interior_preserved = (
        float(np.min(coherence_vector(positive_after))) > 0.0
        and float(np.min(coherence_vector(sham_after))) > 0.0
    )
    history_failure_modes = _segment_failure_modes(history_path, "preparation_history")
    continuation_failure_modes = _segment_failure_modes(
        continuation_path, "first_post_driver_transition"
    )
    path_failure_modes = _path_failure_modes(
        history_path,
        continuation_path,
        rng_matched_at_k0=rng_matched_at_k0,
        administrative_matched_at_k0=administrative_matched_at_k0,
        positive_interior_preserved=(
            k0_positive_interior_preserved and continuation_positive_interior_preserved
        ),
    )
    if not source_reconstruction_passed:
        path_failure_modes.insert(0, "source_reconstruction_failed")
    clean_history = (
        source_reconstruction_passed
        and not history_failure_modes
        and rng_matched_at_k0
        and administrative_matched_at_k0
        and k0_positive_interior_preserved
    )
    continuation_clean = (
        not continuation_failure_modes and continuation_positive_interior_preserved
    )

    initial_residual = (
        float(carrier_rows[selected_carrier_id]["runtime_generated_residual_norm"])
        if selected_carrier_id
        else 0.0
    )
    later_residual = (
        float(
            carrier_rows_after[selected_carrier_id]["runtime_generated_residual_norm"]
        )
        if selected_carrier_id
        else 0.0
    )
    persistence_ratio = later_residual / initial_residual if initial_residual else 0.0
    delayed_formation = selected_carrier_id is None and selected_after is not None
    persistence_passed = (
        selected_carrier_id is not None
        and continuation_clean
        and persistence_ratio >= 0.9
    )
    internal_stage_history = _internal_stage_comparison(
        positive_history_audit, sham_history_audit
    )
    internal_stage_continuation = _internal_stage_comparison(
        positive_post_driver_audit, sham_post_driver_audit
    )
    internal_stage = {
        "preparation_history": internal_stage_history,
        "first_post_driver_transition": internal_stage_continuation,
        "maximum_normalized_positive_sham_internal_W_delta": max(
            internal_stage_history["maximum_normalized_positive_sham_internal_W_delta"],
            internal_stage_continuation[
                "maximum_normalized_positive_sham_internal_W_delta"
            ],
        ),
        "all_stage_sequences_aligned": internal_stage_history["stage_sequences_aligned"]
        and internal_stage_continuation["stage_sequences_aligned"],
    }
    complete_w_norm = float(
        carrier_rows["W_EDGE_CONDUCTANCE_OBSERVATION_V1"][
            "runtime_generated_residual_norm"
        ]
    )
    internal_stage_only = (
        internal_stage["maximum_normalized_positive_sham_internal_W_delta"]
        > formation_floor
        and complete_w_norm <= formation_floor
    )

    apparent_carrier_above_floor = any(
        row["apparent_norm"] > formation_floor for row in carrier_rows.values()
    )
    authored_or_unidentifiable_only = (
        selected_carrier_id is None and apparent_carrier_above_floor
    )

    if not source_reconstruction_passed:
        row_decision = "unresolved"
        candidate_status = "source_replay_failure"
        resolved_status = "search_unresolved"
        demotion = "source_reconstruction_failed"
    elif path_failure_modes:
        row_decision = "outside_envelope"
        candidate_status = "outside_envelope"
        resolved_status = "resolved_outside_envelope"
        demotion = "full_path_cleanliness_failed"
    elif delayed_formation:
        row_decision = "unresolved"
        candidate_status = "unresolved_delayed_post_driver_formation"
        resolved_status = "search_unresolved"
        demotion = "delayed_formation_has_no_frozen_I4_admission_path"
    elif selected_carrier_id is None:
        row_decision = "bounded_negative"
        candidate_status = (
            "internal_stage_only_candidate"
            if internal_stage_only
            else (
                "formation_entirely_authored_or_unidentifiable"
                if authored_or_unidentifiable_only
                else "bounded_negative"
            )
        )
        resolved_status = "resolved_negative"
        demotion = (
            "internal_stage_carrier_absent_at_complete_step_boundary"
            if internal_stage_only
            else (
                "apparent_carrier_present_but_runtime_generated_component_not_identifiable"
                if authored_or_unidentifiable_only
                else "no_runtime_generated_carrier_above_formation_and_separation_floors"
            )
        )
    elif not persistence_passed:
        row_decision = "bounded_negative"
        candidate_status = "overwritten_or_nonpersistent_after_driver"
        resolved_status = "resolved_negative"
        demotion = "first_post_driver_transition_persistence_failed"
    else:
        row_decision = "positive_witness"
        candidate_status = "positive_witness_pending_fresh_process_confirmation"
        resolved_status = "resolved_positive"
        demotion = "none"

    state_identity = {
        "runtime_config_digest": semantic_digest(evaluation_params),
        "source_branch_id": branch_row["branch_id"],
        "complete_admitted_causal_k0_state_digest": positive_k0[
            "complete_admitted_causal_state_digest"
        ],
        "observer_only_fields_excluded": positive_k0[
            "excluded_observer_only_state_fields"
        ],
    }
    preparation_history = {
        "family": spec["preparation_family"],
        "history_length": spec["history_length"],
        "pulse_amount": pulse_amount,
        "pulse_edge_id": spec["edge_id"],
        "pulse_source_node": spec["source_node"],
        "pulse_destination_node": spec["destination_node"],
        "parameter_variant_id": spec["parameter_variant_id"],
        "parameter_name": spec["parameter_name"],
        "parameter_multiplier": spec["parameter_multiplier"],
        "state_production_parameter_vector": history_params,
        "current_evaluation_parameter_vector": evaluation_params,
        "driver_exhaustion_boundary": "after_preparation_history_before_k0",
        "first_post_driver_transition": "k0_to_k1_under_evaluation_parameters",
        "unplanned_washout_step_used": False,
    }
    boundary_flags = {
        "amplitude_boundary_hit": spec["amplitude_fraction"]
        in {min(AMPLITUDE_FRACTIONS), max(AMPLITUDE_FRACTIONS)}
        if spec["amplitude_fraction"] > 0.0
        else False,
        "history_length_boundary_hit": spec["history_length"]
        in {min(HISTORY_LENGTHS), max(HISTORY_LENGTHS)},
        "parameter_variant_boundary_hit": spec["parameter_multiplier"] is not None,
        "proposal_projected_or_clipped_into_envelope": False,
    }
    secondary = []
    if history_path["categorical_signature_changed"]:
        secondary.append("categorical_transition_outside_clean_primary_lane")
    if history_path["constraint_stage_executed_without_state_change"]:
        secondary.append("constraint_stage_executed_as_numerical_noop")
    if any(boundary_flags.values()):
        secondary.append("frozen_search_or_schedule_boundary_hit")
    if not rng_matched_at_k0:
        secondary.append("causal_rng_state_not_matched_at_k0")

    source_c = np.asarray(source_state["C"], dtype=float)
    source_w = np.asarray(source_state["W"], dtype=float)
    sham_c = np.asarray(sham_k0["C"], dtype=float)
    sham_w = np.asarray(sham_k0["W"], dtype=float)
    normalized_sham_c_drift = float(np.linalg.norm(sham_c - source_c)) / max(
        float(np.linalg.norm(source_c)), 1e-12
    )
    normalized_sham_w_drift = float(np.linalg.norm(sham_w - source_w)) / max(
        float(np.linalg.norm(source_w)), 1e-12
    )
    normalized_joint_sham_drift = math.sqrt(
        normalized_sham_c_drift**2 + normalized_sham_w_drift**2
    ) / math.sqrt(2.0)
    formation_reference = max(
        row["runtime_generated_residual_norm"] for row in carrier_rows.values()
    )
    sham_drift_fraction = normalized_joint_sham_drift / max(
        formation_reference, formation_floor
    )
    outlier_flags = {
        "partial_driver_carrier_overlap": bool(
            selected_carrier_id
            and carrier_rows[selected_carrier_id]["authored_component_norm"] > 0.0
        ),
        "delayed_post_driver_formation": delayed_formation,
        "substantial_sham_drift_fraction": sham_drift_fraction >= 0.1,
        "categorical_boundary_source": branch_row["categorical_stratum_status"]
        == "recorded_separately",
        "constraint_stage_executed_without_state_change": history_path[
            "constraint_stage_executed_without_state_change"
        ],
        "internal_stage_complete_step_signature_disagreement": internal_stage_only,
        "fresh_process_confirmation_failure": False,
        "candidate_amplifies_on_first_post_driver_transition": persistence_ratio > 1.0,
    }

    return {
        "attempt_id": spec["attempt_id"],
        "search_row_id": spec["search_row_id"],
        "attempt_index_within_branch": spec["attempt_index_within_branch"],
        "allocated_budget_slot": spec["allocated_budget_slot"],
        "source_branch_id": branch_row["branch_id"],
        "fixture_id": branch_row["fixture_id"],
        "symmetry_orbit_id": branch_row["symmetry_orbit_id"],
        "source_snapshot_path": branch_row["source_snapshot_path"],
        "source_snapshot_sha256": branch_row["source_snapshot_sha256"],
        "source_reconstruction_status": source_audit["status"],
        "source_reconstruction_digest": semantic_digest(source_audit),
        "row_numerical_uncertainty": row_numerical_uncertainty,
        "runtime_config_digest": semantic_digest(evaluation_params),
        "preparation_spec": spec,
        "preparation_history": preparation_history,
        "preparation_history_digest": semantic_digest(preparation_history),
        "positive_history_audit": positive_history_audit,
        "sham_history_audit": sham_history_audit,
        "paired_history_summary": history_path,
        "forming_intervention_exhausted": True,
        "evaluation_parameters_restored_before_k0": True,
        "positive_k0_state": positive_k0,
        "sham_k0_state": sham_k0,
        "post_driver_k0_state_digest": positive_k0["state_digest"],
        "sham_k0_state_digest": sham_k0["state_digest"],
        "sham_preparation_trace_digest": semantic_digest(
            {
                "history": preparation_history,
                "audit": sham_history_audit,
                "omitted_action": "forming_C_pair_pulse",
            }
        ),
        "matched_sham": {
            "same_native_step_count_and_timing": history_path[
                "native_step_counts_match"
            ],
            "same_parameter_switching_schedule": True,
            "rng_state_matched_at_k0_where_causal": rng_matched_at_k0,
            "administrative_phase_matched_at_k0": administrative_matched_at_k0,
            "omitted_action": "none" if pulse_amount == 0.0 else "forming_C_pair_pulse",
        },
        "carrier_rows": carrier_rows,
        "carrier_rows_after_first_post_driver_transition": carrier_rows_after,
        "selected_carrier_definition_id": selected_carrier_id,
        "selected_carrier_after_first_post_driver_transition": selected_after,
        "delayed_post_driver_formation_detected": delayed_formation,
        "persistence": {
            "status": (
                "passed_first_post_driver_transition"
                if persistence_passed
                else (
                    "unresolved_delayed_post_driver_formation"
                    if delayed_formation
                    else "failed_or_not_applicable"
                )
            ),
            "horizon_native_steps": persistence_horizon,
            "initial_runtime_generated_residual_norm": initial_residual,
            "later_runtime_generated_residual_norm": later_residual,
            "persistence_ratio": persistence_ratio,
            "positive_state": runtime_state(positive_after),
            "sham_state": runtime_state(sham_after),
            "positive_step_audit": positive_post_driver_audit,
            "sham_step_audit": sham_post_driver_audit,
            "paired_continuation_summary": continuation_path,
        },
        "internal_stage_audit": internal_stage,
        "internal_stage_only_candidate": internal_stage_only,
        "event_free": history_path["event_free"] and continuation_path["event_free"],
        "fixed_topology": history_path["fixed_topology"]
        and continuation_path["fixed_topology"],
        "maximum_budget_correction_l_inf": max(
            positive_history_audit["maximum_budget_correction_l_inf"],
            sham_history_audit["maximum_budget_correction_l_inf"],
            positive_post_driver_audit["maximum_budget_correction_l_inf"],
            sham_post_driver_audit["maximum_budget_correction_l_inf"],
        ),
        "load_bearing_budget_projection": history_path["load_bearing_budget_projection"]
        or continuation_path["load_bearing_budget_projection"],
        "load_bearing_clipping": history_path["load_bearing_boundary_or_clipping"]
        or continuation_path["load_bearing_boundary_or_clipping"],
        "minimum_C": min(positive_k0["minimum_C"], sham_k0["minimum_C"]),
        "minimum_W": min(positive_k0["minimum_W"], sham_k0["minimum_W"]),
        "full_path_cleanliness_result": (
            "passed_clean_primary_lane"
            if not path_failure_modes
            else (
                "constraint_supported_history"
                if any("constraint_supported" in item for item in path_failure_modes)
                else (
                    "eventful_history_persistence"
                    if any("eventful" in item for item in path_failure_modes)
                    else "outside_clean_primary_lane"
                )
            )
        ),
        "full_path_failure_modes": path_failure_modes,
        "mechanism_execution_summary": {
            "history": history_path,
            "first_post_driver_transition": continuation_path,
            "execution_does_not_imply_load_bearing_change": True,
        },
        "row_decision": row_decision,
        "primary_demotion_reason": demotion,
        "secondary_demotion_reasons": secondary,
        "candidate_status": candidate_status,
        "resolved_status": resolved_status,
        "state_identity_digest": semantic_digest(state_identity),
        "history_aware_candidate_identity": semantic_digest(
            {
                "state": state_identity,
                "history": preparation_history,
                "carrier": selected_carrier_id,
            }
        ),
        "symmetry_signature_for_characterization_only": semantic_digest(
            {
                "runtime_config_digest": semantic_digest(evaluation_params),
                "symmetry_orbit_id": branch_row["symmetry_orbit_id"],
                "C_sorted": sorted(round(value, 14) for value in positive_k0["C"]),
                "W_sorted": sorted(round(value, 14) for value in positive_k0["W"]),
                "J_absolute_sorted": sorted(
                    round(abs(value), 14) for value in positive_k0["J"]
                ),
                "history_family": spec["preparation_family"],
                "history_length": spec["history_length"],
                "amplitude_fraction": spec["amplitude_fraction"],
            }
        ),
        "boundary_flags": boundary_flags,
        "sham_drift": {
            "normalized_C_drift_from_source": normalized_sham_c_drift,
            "normalized_W_drift_from_source": normalized_sham_w_drift,
            "normalized_joint_drift_from_source": normalized_joint_sham_drift,
            "fraction_of_formation_reference": sham_drift_fraction,
            "manual_review_threshold": 0.1,
            "used_for_candidate_admission": False,
        },
        "outlier_flags": outlier_flags,
        "discovery_features": {
            "runtime_reachability": True,
            "state_validity": clean_history and continuation_clean,
            "formation_contrast_norm": (
                carrier_rows[selected_carrier_id]["runtime_generated_residual_norm"]
                if selected_carrier_id
                else max(
                    row["runtime_generated_residual_norm"]
                    for row in carrier_rows.values()
                )
            ),
            "finite_horizon_persistence_magnitude": persistence_ratio,
        },
        "future_gate_features_computed_or_accessed": False,
        "adjudication_feature_accessed_during_discovery": False,
        "source_state_digest": source_state["state_digest"],
    }


def _failed_attempt_row(
    branch_row: dict[str, Any], spec: dict[str, Any], reason: str, status: str
) -> dict[str, Any]:
    row_decision = "unresolved" if status == "source_replay_failure" else status
    return {
        "attempt_id": spec["attempt_id"],
        "search_row_id": spec["search_row_id"],
        "attempt_index_within_branch": spec["attempt_index_within_branch"],
        "allocated_budget_slot": spec["allocated_budget_slot"],
        "source_branch_id": branch_row["branch_id"],
        "fixture_id": branch_row["fixture_id"],
        "symmetry_orbit_id": branch_row["symmetry_orbit_id"],
        "source_snapshot_path": branch_row["source_snapshot_path"],
        "source_snapshot_sha256": branch_row["source_snapshot_sha256"],
        "preparation_spec": spec,
        "preparation_history": {"family": spec["preparation_family"]},
        "preparation_history_digest": semantic_digest(spec),
        "selected_carrier_definition_id": None,
        "row_decision": row_decision,
        "candidate_status": status,
        "resolved_status": (
            "resolved_outside_envelope"
            if status == "outside_envelope"
            else "search_unresolved"
        ),
        "primary_demotion_reason": reason,
        "secondary_demotion_reasons": [],
        "discovery_features": {
            "runtime_reachability": False,
            "state_validity": False,
            "formation_contrast_norm": 0.0,
            "finite_horizon_persistence_magnitude": 0.0,
        },
        "future_gate_features_computed_or_accessed": False,
        "adjudication_feature_accessed_during_discovery": False,
    }


def evaluate_branch(
    branch_row: dict[str, Any],
    registry_row: dict[str, Any],
    *,
    formation_floor: float,
    numerical_uncertainty: float,
    persistence_horizon: int,
    carrier_priority: list[str],
) -> dict[str, Any]:
    base_model = GRC9V3.load(str(REPO_ROOT / Path(branch_row["source_snapshot_path"])))
    specs = attempt_specs(base_model, branch_row["branch_id"])
    source_audit = source_reconstruction_audit(base_model, branch_row, registry_row)
    if source_audit["status"] != "passed":
        return {
            "source_audit": source_audit,
            "rows": [
                _failed_attempt_row(
                    branch_row,
                    spec,
                    "source_reconstruction_failed_descendants_not_negative_evidence",
                    "source_replay_failure",
                )
                for spec in specs
            ],
        }
    rows = []
    for spec in specs:
        try:
            rows.append(
                evaluate_attempt(
                    base_model,
                    branch_row,
                    source_audit,
                    spec,
                    formation_floor=formation_floor,
                    numerical_uncertainty=numerical_uncertainty,
                    persistence_horizon=persistence_horizon,
                    carrier_priority=carrier_priority,
                )
            )
        except ValueError as exc:
            if str(exc) == "pair_pulse_outside_positive_coherence_interior":
                rows.append(
                    _failed_attempt_row(
                        branch_row,
                        spec,
                        "proposal_outside_positive_interior_not_projected_back",
                        "outside_envelope",
                    )
                )
            else:
                raise
        except (ArithmeticError, FloatingPointError, OverflowError) as exc:
            rows.append(
                _failed_attempt_row(
                    branch_row,
                    spec,
                    f"numerical_failure:{type(exc).__name__}",
                    "numerical_failure",
                )
            )
    return {"source_audit": source_audit, "rows": rows}

"""Hybrid spark and expansion helpers for the GRC9V3 family."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from pygrc.core import EdgeId, GRCEvent, NodeId

from .grc_9_expansion import (
    CANONICAL_CORE_SPINE_PORTS,
    PRIMARY_SATELLITE_COLUMNS,
    aggregate_bond_conductance,
    boundary_reassignment_order,
    compute_expansion_node_count,
    normalize_expansion_weights,
    round_robin_column_order,
)
from .grc_9_ports import port_id_to_slot, port_to_rc, rc_to_port, slot_to_port_id
from .grc_9_state import ExpansionRecord, PortEdge
from .grc_9_v3_state import GRC9V3NodeState, GRC9V3State


COLUMN_H_COMPUTATION_VERSION = "grc9v3_column_h_v1"
# Keep these runtime evidence ids synchronized with
# pygrc.telemetry.grc9v3_contract without importing telemetry from models.
LANE_B_CANDIDATE_EVENT_SCHEMA_VERSION = "grc9v3_column_h_assisted_candidate_v1"
LANE_B_SPARK_LANE_VERSION = "v1"


@dataclass(frozen=True)
class ColumnHTerm:
    """One candidate-local contribution to a column-H diagnostic."""

    edge_id: EdgeId
    port_id: int
    row: int
    column: int
    neighbor_id: NodeId
    base_conductance: float
    c_node: float
    c_neighbor: float
    delta_c: float
    contribution: float


@dataclass(frozen=True)
class ColumnHResult:
    """Auditable runtime result for the GRC9V3 column-H proxy."""

    node_id: NodeId
    state_epoch: int
    column_h_values: tuple[float, float, float]
    min_abs_column_h: float
    min_abs_column_h_column: int
    eps_column_h: float
    column_h_threshold_hit: bool
    column_h_sign_crossing_enabled: bool
    column_h_sign_crossing_mode: str
    eps_column_h_crossing_zero: float
    previous_column_h_values: tuple[float, float, float] | None
    previous_column_h_status: str
    column_h_sign_crossing_hit: bool
    column_h_sign_crossing_columns: tuple[int, ...]
    column_h_branch_hit: bool
    column_h_gate_hit: bool
    column_h_gate_reasons: tuple[str, ...]
    column_h_computation_version: str
    terms: tuple[ColumnHTerm, ...] = ()


def compute_column_hessian_proxy(
    state: GRC9V3State,
    node_id: NodeId,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
    previous_column_h_values: Sequence[float] | None = None,
    include_terms: bool = False,
) -> ColumnHResult:
    """Compute direct runtime column-H proxy values for one candidate node.

    This computes the Lane B v1 diagnostic only. It does not mutate state and
    does not participate in the spark predicate until the predicate iteration.
    """

    if not state.topology.has_node(node_id):
        raise ValueError(f"cannot compute column-H for missing node {node_id}")
    node_state = state.nodes.get(node_id)
    if node_state is None:
        raise ValueError(f"cannot compute column-H without node state for {node_id}")
    c_node = _finite_float(node_state.coherence, context=f"node {node_id} coherence")
    eps_column_h = _finite_float(
        evolution.get("eps_column_h", 1e-3),
        context="eps_column_h",
    )
    if eps_column_h < 0.0:
        raise ValueError("eps_column_h must be >= 0")
    eps_crossing_zero = _finite_float(
        evolution.get("eps_column_h_crossing_zero", 0.0),
        context="eps_column_h_crossing_zero",
    )
    if eps_crossing_zero < 0.0:
        raise ValueError("eps_column_h_crossing_zero must be >= 0")

    values = [0.0, 0.0, 0.0]
    terms: list[ColumnHTerm] = []
    seen_ports: set[int] = set()

    for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
        local_port_id = _local_port_id(state, edge_id=edge_id, node_id=node_id)
        if local_port_id in seen_ports:
            raise ValueError(
                f"duplicate local port {local_port_id} on node {node_id}"
            )
        seen_ports.add(local_port_id)
        row, column = port_to_rc(local_port_id)
        neighbor_id = _neighbor_node_id(state, edge_id=edge_id, node_id=node_id)
        neighbor_state = state.nodes.get(neighbor_id)
        if neighbor_state is None:
            raise ValueError(
                f"cannot compute column-H without node state for neighbor {neighbor_id}"
            )
        c_neighbor = _finite_float(
            neighbor_state.coherence,
            context=f"neighbor {neighbor_id} coherence",
        )
        conductance = _edge_base_conductance(state, edge_id=edge_id)
        delta_c = c_neighbor - c_node
        contribution = conductance * delta_c
        values[column - 1] += contribution
        if include_terms:
            terms.append(
                ColumnHTerm(
                    edge_id=edge_id,
                    port_id=local_port_id,
                    row=row,
                    column=column,
                    neighbor_id=neighbor_id,
                    base_conductance=conductance,
                    c_node=c_node,
                    c_neighbor=c_neighbor,
                    delta_c=delta_c,
                    contribution=contribution,
                )
            )

    column_h_values = (float(values[0]), float(values[1]), float(values[2]))
    abs_values = tuple(abs(value) for value in column_h_values)
    min_abs_column_h = min(abs_values)
    min_abs_column_h_column = int(abs_values.index(min_abs_column_h) + 1)
    threshold_enabled = bool(modes.get("enable_column_h_threshold", True))
    threshold_hit = bool(threshold_enabled and min_abs_column_h < eps_column_h)

    sign_crossing_enabled = bool(modes.get("enable_column_h_sign_crossing", False))
    sign_crossing_mode = str(modes.get("column_h_sign_crossing_mode", "theory_product"))
    try:
        previous_values = _resolve_previous_column_h_values(
            state,
            node_id=node_id,
            previous_column_h_values=previous_column_h_values,
        )
    except ValueError:
        if previous_column_h_values is None:
            raise
        previous_values = None
        previous_status = "invalid_unavailable"
    else:
        previous_status = _previous_column_h_status(
            previous_values,
            explicit_previous_values=previous_column_h_values,
            modes=modes,
        )
    crossing_columns: tuple[int, ...] = ()
    if sign_crossing_enabled and previous_values is not None:
        crossing_columns = _column_h_sign_crossing_columns(
            previous_values,
            column_h_values,
            mode=sign_crossing_mode,
            eps_zero=eps_crossing_zero,
        )
    sign_crossing_hit = bool(crossing_columns)

    reasons: list[str] = []
    if threshold_hit:
        reasons.append("column_h_threshold_hit")
    if sign_crossing_hit:
        reasons.append("column_h_sign_crossing_hit")

    return ColumnHResult(
        node_id=node_id,
        state_epoch=int(state.step_index),
        column_h_values=column_h_values,
        min_abs_column_h=min_abs_column_h,
        min_abs_column_h_column=min_abs_column_h_column,
        eps_column_h=eps_column_h,
        column_h_threshold_hit=threshold_hit,
        column_h_sign_crossing_enabled=sign_crossing_enabled,
        column_h_sign_crossing_mode=sign_crossing_mode,
        eps_column_h_crossing_zero=eps_crossing_zero,
        previous_column_h_values=previous_values,
        previous_column_h_status=previous_status,
        column_h_sign_crossing_hit=sign_crossing_hit,
        column_h_sign_crossing_columns=crossing_columns,
        column_h_branch_hit=bool(reasons),
        # Compatibility alias only: this is a column-H branch hit, not the
        # full Lane B candidate predicate (`lane_b_candidate_hit`).
        column_h_gate_hit=bool(reasons),
        column_h_gate_reasons=tuple(reasons),
        column_h_computation_version=COLUMN_H_COMPUTATION_VERSION,
        terms=tuple(terms),
    )


def refresh_column_h_history(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
) -> dict[NodeId, ColumnHResult]:
    """Store current column-H values as previous-step history when configured."""

    if not bool(modes.get("store_previous_column_h", False)):
        state.cached_quantities["previous_column_h_storage_status"] = "storage_disabled"
        return {}

    state_epoch = int(state.step_index)
    state.cached_quantities["current_column_h_spark_lane"] = str(
        modes.get("spark_lane", "current_hybrid_signed_hessian")
    )
    current_epoch = state.cached_quantities.get("current_column_h_state_epoch")
    current_by_node = state.cached_quantities.get("current_column_h_by_node", {})
    if current_epoch == state_epoch and isinstance(current_by_node, Mapping):
        return {
            node_id: compute_column_hessian_proxy(
                state,
                node_id,
                evolution=evolution,
                modes=modes,
            )
            for node_id in sorted(state.topology.iter_live_node_ids())
            if node_id in state.nodes
        }

    live_node_ids = set(state.topology.iter_live_node_ids())
    previous_history: dict[str, list[float]] = {}
    pruned_node_ids: list[str] = []
    if isinstance(current_by_node, Mapping):
        for raw_node_id, raw_values in current_by_node.items():
            node_id = int(raw_node_id)
            if node_id not in live_node_ids:
                pruned_node_ids.append(str(raw_node_id))
                continue
            previous_history[str(node_id)] = list(
                _resolve_previous_column_h_values(
                    state,
                    node_id=node_id,
                    previous_column_h_values=raw_values,
                )
                or ()
            )

    state.cached_quantities["previous_column_h_by_node"] = previous_history
    state.cached_quantities["previous_column_h_pruned_node_ids"] = pruned_node_ids

    results: dict[NodeId, ColumnHResult] = {}
    next_current: dict[str, list[float]] = {}
    for node_id in sorted(live_node_ids):
        if node_id not in state.nodes:
            continue
        result = compute_column_hessian_proxy(
            state,
            node_id,
            evolution=evolution,
            modes=modes,
        )
        results[node_id] = result
        next_current[str(node_id)] = list(result.column_h_values)

    state.cached_quantities["current_column_h_by_node"] = next_current
    state.cached_quantities["current_column_h_state_epoch"] = state_epoch
    state.cached_quantities["column_h_computation_version"] = COLUMN_H_COMPUTATION_VERSION
    state.cached_quantities["previous_column_h_storage_status"] = (
        "updated" if previous_history else "history_unavailable_first_step"
    )
    return results


def invalidate_previous_column_h_cache(
    state: GRC9V3State,
    *,
    reason: str,
) -> None:
    """Clear previous/current column-H history after topology identity changes."""

    invalidated_node_ids = sorted(
        set(_mapping_keys_as_strings(state.cached_quantities.get("previous_column_h_by_node", {})))
        | set(_mapping_keys_as_strings(state.cached_quantities.get("current_column_h_by_node", {})))
    )
    had_history = bool(invalidated_node_ids) or "current_column_h_state_epoch" in state.cached_quantities
    if not had_history:
        return
    state.cached_quantities["previous_column_h_by_node"] = {}
    state.cached_quantities["current_column_h_by_node"] = {}
    state.cached_quantities.pop("current_column_h_state_epoch", None)
    state.cached_quantities["previous_column_h_invalidated_node_ids"] = invalidated_node_ids
    state.cached_quantities["previous_column_h_storage_status"] = f"invalidated:{reason}"


def detect_hybrid_spark_candidates(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
    source_family: str,
) -> list[GRCEvent]:
    """Detect saturation-gated GRC9V3 spark candidates from live diagnostics."""

    eps_gradient = float(evolution.get("eps_gradient", 1e-3))
    eps_spark = float(evolution.get("eps_spark", 1e-3))
    spark_lane = str(modes.get("spark_lane", "current_hybrid_signed_hessian"))
    signed_crossing_enabled = bool(modes.get("spark_signed_crossing", False))
    previous_min_signed = _previous_min_signed_hessian_by_node(state)
    column_h_results: dict[NodeId, ColumnHResult] = {}
    if bool(modes.get("store_previous_column_h", False)):
        column_h_results = refresh_column_h_history(
            state,
            evolution=evolution,
            modes=modes,
        )
    candidates: list[GRCEvent] = []
    signed_status = "capability_disabled"

    for node_id in sorted(state.topology.iter_live_node_ids()):
        node_state = state.nodes.get(node_id)
        if node_state is None:
            continue
        active_degree = len(tuple(state.topology.incident_edge_ids(node_id)))
        gradient_norm = _gradient_norm(node_state)
        min_signed_hessian = _min_signed_hessian(node_state)
        saturation_gate = active_degree == 9
        basin_interior_gate = gradient_norm < eps_gradient
        degeneracy_gate = min_signed_hessian < eps_spark
        signed_crossing_gate: bool | None = None

        if spark_lane == "grc9v3_column_h_assisted":
            column_h_result = column_h_results.get(node_id)
            if column_h_result is None:
                column_h_result = compute_column_hessian_proxy(
                    state,
                    node_id,
                    evolution=evolution,
                    modes=modes,
                )
            sink_status = node_id in state.sink_set
            candidate_scope_status = bool(
                sink_status or not bool(modes.get("require_sink_for_column_h_spark", True))
            )
            signed_hessian_hit = degeneracy_gate
            column_h_branch_hit = column_h_result.column_h_branch_hit
            lane_b_candidate_hit = bool(
                candidate_scope_status
                and saturation_gate
                and basin_interior_gate
                and (signed_hessian_hit or column_h_branch_hit)
            )
            if not lane_b_candidate_hit:
                continue

            gate_reasons: list[str] = []
            if signed_hessian_hit:
                gate_reasons.append("signed_hessian_hit")
            gate_reasons.extend(column_h_result.column_h_gate_reasons)
            candidates.append(
                GRCEvent(
                    kind="hybrid_spark_candidate",
                    step_index=state.step_index,
                    payload={
                        "event_schema_version": LANE_B_CANDIDATE_EVENT_SCHEMA_VERSION,
                        "spark_lane_version": LANE_B_SPARK_LANE_VERSION,
                        "candidate_event_id": _lane_b_candidate_event_id(
                            state,
                            node_id=node_id,
                        ),
                        "step_index": state.step_index,
                        "sink_node_id": node_id,
                        "candidate_node_id": node_id,
                        "node_id": node_id,
                        "spark_lane": spark_lane,
                        "active_degree": active_degree,
                        "saturation_gate": saturation_gate,
                        "basin_interior_gate": basin_interior_gate,
                        "gradient_norm": gradient_norm,
                        "eps_gradient": eps_gradient,
                        "signed_hessian_degeneracy_gate": signed_hessian_hit,
                        "signed_hessian_hit": signed_hessian_hit,
                        "signed_hessian_min": min_signed_hessian,
                        "min_signed_hessian": min_signed_hessian,
                        "eps_signed_hessian": eps_spark,
                        "eps_spark": eps_spark,
                        "column_h": list(column_h_result.column_h_values),
                        "min_abs_column_h": column_h_result.min_abs_column_h,
                        "min_abs_column_h_column": column_h_result.min_abs_column_h_column,
                        "eps_column_h": column_h_result.eps_column_h,
                        "column_h_threshold_hit": column_h_result.column_h_threshold_hit,
                        "column_h_sign_crossing_enabled": (
                            column_h_result.column_h_sign_crossing_enabled
                        ),
                        "column_h_sign_crossing_mode": (
                            column_h_result.column_h_sign_crossing_mode
                        ),
                        "eps_column_h_crossing_zero": (
                            column_h_result.eps_column_h_crossing_zero
                        ),
                        "previous_column_h_status": (
                            column_h_result.previous_column_h_status
                        ),
                        "previous_column_h_values": (
                            None
                            if column_h_result.previous_column_h_values is None
                            else list(column_h_result.previous_column_h_values)
                        ),
                        "column_h_sign_crossing_hit": (
                            column_h_result.column_h_sign_crossing_hit
                        ),
                        "column_h_sign_crossing_columns": list(
                            column_h_result.column_h_sign_crossing_columns
                        ),
                        "column_h_branch_hit": column_h_branch_hit,
                        "column_h_gate_hit": column_h_branch_hit,
                        "lane_b_candidate_hit": lane_b_candidate_hit,
                        "gate_reasons": gate_reasons,
                        "sink_status": sink_status,
                        "candidate_scope_status": candidate_scope_status,
                        "require_sink_for_column_h_spark": bool(
                            modes.get("require_sink_for_column_h_spark", True)
                        ),
                        "require_active_degree_9": bool(
                            modes.get("require_active_degree_9", True)
                        ),
                        "near_saturation_enabled": bool(
                            modes.get("enable_near_saturation", False)
                        ),
                        "virtual_stubs_used": False,
                        "linked_expansion_event_id": None,
                        "column_h_computation_version": (
                            column_h_result.column_h_computation_version
                        ),
                        "state_epoch": column_h_result.state_epoch,
                        "basin_id": node_state.basin_id,
                        "parent_id": node_state.parent_id,
                        "depth": node_state.depth,
                    },
                    source_family=source_family,
                )
            )
            continue

        if signed_crossing_enabled:
            previous = previous_min_signed.get(node_id)
            if previous is None:
                signed_status = "history_unavailable"
                signed_crossing_gate = False
            else:
                signed_status = "evaluated"
                signed_crossing_gate = previous * min_signed_hessian < 0.0

        if not (saturation_gate and basin_interior_gate and degeneracy_gate):
            continue
        if signed_crossing_enabled and not signed_crossing_gate:
            continue

        candidates.append(
            GRCEvent(
                kind="hybrid_spark_candidate",
                step_index=state.step_index,
                payload={
                    "sink_node_id": node_id,
                    "candidate_node_id": node_id,
                    "active_degree": active_degree,
                    "saturation_gate": saturation_gate,
                    "basin_interior_gate": basin_interior_gate,
                    "gradient_norm": gradient_norm,
                    "eps_gradient": eps_gradient,
                    "signed_hessian_degeneracy_gate": degeneracy_gate,
                    "min_signed_hessian": min_signed_hessian,
                    "eps_spark": eps_spark,
                    "signed_crossing_enabled": signed_crossing_enabled,
                    "signed_crossing_gate": signed_crossing_gate,
                    "basin_id": node_state.basin_id,
                    "parent_id": node_state.parent_id,
                    "depth": node_state.depth,
                },
                source_family=source_family,
            )
        )

    state.cached_quantities["hybrid_spark_candidate_count"] = len(candidates)
    state.cached_quantities["hybrid_spark_signed_crossing_status"] = signed_status
    return candidates


def apply_mechanical_expansion(
    state: GRC9V3State,
    candidate_event: GRCEvent,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
    source_family: str,
) -> GRCEvent:
    """Adapt the Phase 6 GRC9 expansion module to a GRC9V3 node state."""

    parent_node_id = int(candidate_event.payload["sink_node_id"])
    if not state.topology.has_node(parent_node_id):
        raise ValueError(f"cannot expand missing candidate node {parent_node_id}")
    parent_state = state.nodes.get(parent_node_id, GRC9V3NodeState(coherence=0.0))
    parent_coherence = float(parent_state.coherence)
    budget_before = _unit_measure_budget(state)
    target_effective_degree = int(evolution.get("D_eff_target", 30))
    requested_node_count = compute_expansion_node_count(target_effective_degree)
    target_module_node_count = max(4, requested_node_count)
    distribution_weights = _expansion_distribution_weights(evolution=evolution, modes=modes)
    core_coherence_fraction = float(evolution.get("expansion_core_coherence_fraction", 0.0))
    if not 0.0 <= core_coherence_fraction <= 1.0:
        raise ValueError("expansion_core_coherence_fraction must be in [0, 1]")
    core_coherence = core_coherence_fraction * parent_coherence
    satellite_parent_coherence = parent_coherence - core_coherence

    boundary_edges_by_column: dict[int, list[tuple[EdgeId, int]]] = {1: [], 2: [], 3: []}
    boundary_conductance_by_column: dict[int, list[float]] = {1: [], 2: [], 3: []}
    for edge_id in sorted(state.topology.incident_edge_ids(parent_node_id)):
        local_port_id = _local_port_id(state, edge_id=edge_id, node_id=parent_node_id)
        _, column = port_to_rc(local_port_id)
        boundary_edges_by_column[column].append((edge_id, local_port_id))
        boundary_conductance_by_column[column].append(
            float(state.port_edges.get(edge_id, PortEdge(0, 1, 0, 1, 1.0, 0.0)).conductance)
        )

    core_node_id = state.topology.add_node(
        {"role": "hybrid_expansion_core", "parent_sink_id": parent_node_id}
    )
    satellite_node_ids = {
        column: state.topology.add_node(
            {
                "role": "hybrid_expansion_satellite",
                "column": column,
                "parent_sink_id": parent_node_id,
            }
        )
        for column in PRIMARY_SATELLITE_COLUMNS
    }
    column_tree_nodes: dict[int, list[NodeId]] = {
        column: [satellite_node_ids[column]] for column in PRIMARY_SATELLITE_COLUMNS
    }
    module_node_ids: list[NodeId] = [core_node_id] + [
        satellite_node_ids[column] for column in PRIMARY_SATELLITE_COLUMNS
    ]
    internal_edge_payloads: dict[EdgeId, PortEdge] = {}
    internal_edge_ids: list[EdgeId] = []

    for core_port_id, column in zip(
        CANONICAL_CORE_SPINE_PORTS,
        PRIMARY_SATELLITE_COLUMNS,
        strict=True,
    ):
        satellite_node_id = satellite_node_ids[column]
        conductance = aggregate_bond_conductance(
            boundary_conductance_by_column[column],
            fallback=float(evolution.get("w_bond", 1.0)),
        )
        edge_id = state.topology.connect_ports(
            core_node_id,
            port_id_to_slot(core_port_id),
            satellite_node_id,
            port_id_to_slot(5),
            payload={
                "kind": "hybrid_expansion_internal",
                "column": column,
                "parent_sink_id": parent_node_id,
            },
        )
        internal_edge_ids.append(edge_id)
        internal_edge_payloads[edge_id] = PortEdge(
            node_u=core_node_id,
            port_u=core_port_id,
            node_v=satellite_node_id,
            port_v=5,
            conductance=conductance,
            flux_uv=0.0,
        )

    reassignment_map: dict[EdgeId, dict[str, int]] = {}
    for column in PRIMARY_SATELLITE_COLUMNS:
        ordered_ports = boundary_reassignment_order(
            port_id for _, port_id in boundary_edges_by_column[column]
        )
        ordered_edge_items = [
            (edge_id, candidate_port_id)
            for port_id in ordered_ports
            for edge_id, candidate_port_id in boundary_edges_by_column[column]
            if candidate_port_id == port_id
        ]
        for edge_id, old_port_id in ordered_edge_items:
            target_node_id, target_port_id = _find_or_make_column_rewire_target(
                state,
                parent_node_id=parent_node_id,
                column=column,
                old_port_id=old_port_id,
                column_tree_nodes=column_tree_nodes,
                module_node_ids=module_node_ids,
                internal_edge_ids=internal_edge_ids,
                internal_edge_payloads=internal_edge_payloads,
                boundary_conductances=boundary_conductance_by_column[column],
                fallback_conductance=float(evolution.get("w_bond", 1.0)),
            )
            endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
            if endpoint_a[0] == parent_node_id:
                other_node_id, other_slot = endpoint_b
            else:
                other_node_id, other_slot = endpoint_a
            state.topology.rewire_edge(
                edge_id,
                target_node_id,
                port_id_to_slot(target_port_id),
                other_node_id,
                other_slot,
            )
            reassignment_map[edge_id] = {
                "from_port_id": old_port_id,
                "to_node_id": target_node_id,
                "to_port_id": target_port_id,
            }

    planned_extra_nodes = target_module_node_count - len(module_node_ids)
    for column in round_robin_column_order(planned_extra_nodes):
        _attach_column_tree_node(
            state,
            parent_node_id=parent_node_id,
            column=column,
            column_tree_nodes=column_tree_nodes,
            module_node_ids=module_node_ids,
            internal_edge_ids=internal_edge_ids,
            internal_edge_payloads=internal_edge_payloads,
            boundary_conductances=boundary_conductance_by_column[column],
            fallback_conductance=float(evolution.get("w_bond", 1.0)),
        )

    parent_basin_id = parent_state.basin_id
    parent_depth = int(parent_state.depth)
    state.nodes.pop(parent_node_id, None)
    state.nodes[core_node_id] = GRC9V3NodeState(
        coherence=core_coherence,
        basin_id=core_node_id,
        parent_id=parent_basin_id,
        depth=parent_depth + 1,
    )
    for column in PRIMARY_SATELLITE_COLUMNS:
        node_id = satellite_node_ids[column]
        state.nodes[node_id] = GRC9V3NodeState(
            coherence=distribution_weights[column - 1] * satellite_parent_coherence,
            basin_id=node_id,
            parent_id=parent_basin_id,
            depth=parent_depth + 1,
        )
    for node_id in module_node_ids[4:]:
        state.nodes[node_id] = GRC9V3NodeState(
            coherence=0.0,
            basin_id=node_id,
            parent_id=parent_basin_id,
            depth=parent_depth + 1,
        )

    state.topology.remove_node(parent_node_id)
    existing_port_edges = {
        edge_id: port_edge
        for edge_id, port_edge in state.port_edges.items()
        if state.topology.has_edge(edge_id)
    }
    existing_port_edges.update(internal_edge_payloads)
    state.port_edges = _hydrate_port_edges_from_topology(
        state,
        port_edges=existing_port_edges,
    )
    _prune_after_topology_change(state)
    budget_after_uncorrected = _unit_measure_budget(state)
    budget_error_uncorrected = budget_after_uncorrected - budget_before
    if abs(budget_error_uncorrected) > 1e-12:
        core_state = state.nodes[core_node_id]
        corrected_core_coherence = core_state.coherence - budget_error_uncorrected
        if corrected_core_coherence < -1e-12:
            raise ValueError("mechanical expansion budget correction would make core coherence negative")
        state.nodes[core_node_id] = GRC9V3NodeState(
            coherence=max(0.0, corrected_core_coherence),
            gradient_row_basis=list(core_state.gradient_row_basis),
            signed_hessian_row_basis=list(core_state.signed_hessian_row_basis),
            net_flux_summary=list(core_state.net_flux_summary),
            basin_mass=core_state.basin_mass,
            basin_id=core_state.basin_id,
            parent_id=core_state.parent_id,
            depth=core_state.depth,
        )
    budget_after = _unit_measure_budget(state)
    budget_error = budget_after - budget_before

    expansion_id = f"hybrid-spark-{state.step_index}-{parent_node_id}"
    if "linked_expansion_event_id" in candidate_event.payload:
        candidate_event.payload["linked_expansion_event_id"] = expansion_id
    state.expansion_registry[expansion_id] = ExpansionRecord(
        parent_sink_id=parent_node_id,
        module_node_ids=tuple(module_node_ids),
        expansion_step=state.step_index,
        distribution_weights=distribution_weights,
    )
    expansion_event = GRCEvent(
        kind="hybrid_mechanical_expansion",
        step_index=state.step_index,
        payload={
            "sink_node_id": parent_node_id,
            "expansion_id": expansion_id,
            "target_effective_degree": target_effective_degree,
            "requested_node_count": requested_node_count,
            "module_node_ids": list(module_node_ids),
            "internal_edge_ids": list(internal_edge_ids),
            "distribution_weights": list(distribution_weights),
            "core_coherence_fraction": core_coherence_fraction,
            "core_coherence": state.nodes[core_node_id].coherence,
            "budget_measure": "unit_measure",
            "budget_before": budget_before,
            "budget_after": budget_after,
            "budget_error": budget_error,
            "budget_preservation_path": "expansion_transfer_unit_measure",
            "parent_basin_id": parent_basin_id,
            "parent_depth": parent_depth,
            "source_candidate_event_id": candidate_event.payload.get(
                "candidate_event_id"
            ),
            "source_candidate_spark_lane": candidate_event.payload.get("spark_lane"),
            "source_candidate_gate_reasons": list(
                candidate_event.payload.get("gate_reasons", [])
            ),
            "reassignment_map": {
                str(edge_id): payload for edge_id, payload in sorted(reassignment_map.items())
            },
        },
        source_family=source_family,
    )
    state.cached_quantities["last_hybrid_expansion"] = dict(expansion_event.payload)
    state.cached_quantities["last_budget_preservation"] = {
        "context": "hybrid_mechanical_expansion",
        "measure": "unit_measure",
        "budget_before": budget_before,
        "budget_after": budget_after,
        "budget_error": budget_error,
        "budget_preservation_path": "expansion_transfer_unit_measure",
    }
    return expansion_event


def evaluate_child_basin_stabilization(
    state: GRC9V3State,
    expansion_event: GRCEvent,
) -> dict[str, Any]:
    """Return post-expansion child-basin stabilization evidence."""

    module_node_ids = {
        int(node_id) for node_id in expansion_event.payload.get("module_node_ids", [])
    }
    geometric_identity = state.cached_quantities.get("geometric_identity", {})
    seed_nodes = set()
    if isinstance(geometric_identity, Mapping):
        seed_nodes = {int(node_id) for node_id in geometric_identity.get("seed_nodes", [])}
    module_sink_nodes = set(state.sink_set) & module_node_ids
    stabilized_child_node_ids = sorted((module_node_ids & seed_nodes) | module_sink_nodes)
    module_basin_mass = {
        str(sink_id): float(
            sum(
                state.nodes[node_id].coherence
                for node_id in state.basins.get(sink_id, set())
                if node_id in state.nodes
            )
        )
        for sink_id in sorted(module_sink_nodes)
    }
    evidence = {
        "expansion_id": expansion_event.payload.get("expansion_id"),
        "module_node_ids": sorted(module_node_ids),
        "geometric_seed_nodes": sorted(seed_nodes),
        "module_sink_nodes": sorted(module_sink_nodes),
        "module_basin_mass": module_basin_mass,
        "stabilized_child_node_ids": stabilized_child_node_ids,
        "stable_child_basin_count": len(stabilized_child_node_ids),
        "stabilization_pass": bool(stabilized_child_node_ids),
    }
    state.cached_quantities["last_child_basin_stabilization"] = dict(evidence)
    return evidence


def register_completed_hybrid_spark(
    state: GRC9V3State,
    candidate_event: GRCEvent,
    expansion_event: GRCEvent,
    stabilization_evidence: Mapping[str, Any],
    *,
    source_family: str,
) -> GRCEvent | None:
    """Register a completed hybrid spark only when child basins stabilize."""

    stabilized_child_node_ids = [
        int(node_id)
        for node_id in stabilization_evidence.get("stabilized_child_node_ids", [])
    ]
    if not stabilized_child_node_ids:
        return None

    parent_basin_id = expansion_event.payload.get("parent_basin_id")
    parent_depth = int(expansion_event.payload.get("parent_depth", 0))
    hierarchy_key = str(parent_basin_id)
    existing_children = [str(child) for child in state.hierarchy.get(hierarchy_key, [])]
    for child_node_id in stabilized_child_node_ids:
        child_key = str(child_node_id)
        if child_key not in existing_children:
            existing_children.append(child_key)
        if child_node_id in state.nodes:
            node_state = state.nodes[child_node_id]
            state.nodes[child_node_id] = GRC9V3NodeState(
                coherence=node_state.coherence,
                gradient_row_basis=list(node_state.gradient_row_basis),
                signed_hessian_row_basis=list(node_state.signed_hessian_row_basis),
                net_flux_summary=list(node_state.net_flux_summary),
                basin_mass=node_state.basin_mass,
                basin_id=child_node_id,
                parent_id=parent_basin_id,
                depth=parent_depth + 1,
            )
    state.hierarchy[hierarchy_key] = sorted(existing_children, key=str)

    completed_event = GRCEvent(
        kind="hybrid_spark_completed",
        step_index=state.step_index,
        payload={
            "candidate_node_id": candidate_event.payload.get("candidate_node_id"),
            "sink_node_id": candidate_event.payload.get("sink_node_id"),
            "expansion_id": expansion_event.payload.get("expansion_id"),
            "parent_basin_id": parent_basin_id,
            "stabilized_child_node_ids": stabilized_child_node_ids,
            "stable_child_basin_count": len(stabilized_child_node_ids),
            "hierarchy_parent": hierarchy_key,
            "hierarchy_children": list(state.hierarchy[hierarchy_key]),
        },
        source_family=source_family,
    )
    state.cached_quantities["last_completed_hybrid_spark"] = dict(completed_event.payload)
    return completed_event


def _previous_min_signed_hessian_by_node(state: GRC9V3State) -> dict[NodeId, float]:
    previous = state.cached_quantities.get("previous_min_signed_hessian_by_node", {})
    if not isinstance(previous, Mapping):
        return {}
    return {int(node_id): float(value) for node_id, value in previous.items()}


def _unit_measure_budget(state: GRC9V3State) -> float:
    return float(sum(node_state.coherence for node_state in state.nodes.values()))


def _gradient_norm(node_state: GRC9V3NodeState) -> float:
    return float(math.sqrt(sum(value * value for value in node_state.gradient_row_basis)))


def _min_signed_hessian(node_state: GRC9V3NodeState) -> float:
    if not node_state.signed_hessian_row_basis:
        return float("inf")
    return float(min(node_state.signed_hessian_row_basis))


def _lane_b_candidate_event_id(state: GRC9V3State, *, node_id: NodeId) -> str:
    return f"grc9v3-column-h-candidate-{state.step_index}-{node_id}"


def _expansion_distribution_weights(
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
) -> tuple[float, float, float]:
    custom_weights = evolution.get("expansion_custom_weights")
    if custom_weights is not None:
        if not isinstance(custom_weights, Sequence) or isinstance(custom_weights, str):
            raise ValueError("expansion_custom_weights must be a length-3 sequence")
        custom_weights = tuple(float(value) for value in custom_weights)
    return normalize_expansion_weights(
        mode=str(modes.get("expansion_distribution_mode", "equal")),
        custom_weights=custom_weights,
    )


def _find_or_make_column_rewire_target(
    state: GRC9V3State,
    *,
    parent_node_id: NodeId,
    column: int,
    old_port_id: int,
    column_tree_nodes: dict[int, list[NodeId]],
    module_node_ids: list[NodeId],
    internal_edge_ids: list[EdgeId],
    internal_edge_payloads: dict[EdgeId, PortEdge],
    boundary_conductances: Sequence[float],
    fallback_conductance: float,
) -> tuple[NodeId, int]:
    preferred_ports = _same_column_ports(column, preferred=old_port_id)
    for target_node_id in column_tree_nodes[column]:
        target_port_id = _first_available_port(state, target_node_id, preferred_ports)
        if target_port_id is not None:
            return target_node_id, target_port_id

    child_node_id = _attach_column_tree_node(
        state,
        parent_node_id=parent_node_id,
        column=column,
        column_tree_nodes=column_tree_nodes,
        module_node_ids=module_node_ids,
        internal_edge_ids=internal_edge_ids,
        internal_edge_payloads=internal_edge_payloads,
        boundary_conductances=boundary_conductances,
        fallback_conductance=fallback_conductance,
    )
    target_port_id = _first_available_port(state, child_node_id, preferred_ports)
    if target_port_id is None:
        raise ValueError(f"new column tree node {child_node_id} has no free column port")
    return child_node_id, target_port_id


def _attach_column_tree_node(
    state: GRC9V3State,
    *,
    parent_node_id: NodeId,
    column: int,
    column_tree_nodes: dict[int, list[NodeId]],
    module_node_ids: list[NodeId],
    internal_edge_ids: list[EdgeId],
    internal_edge_payloads: dict[EdgeId, PortEdge],
    boundary_conductances: Sequence[float],
    fallback_conductance: float,
) -> NodeId:
    source_node_id = column_tree_nodes[column][-1]
    source_port_id = _first_available_port(state, source_node_id, range(1, 10))
    if source_port_id is None:
        raise ValueError(f"column tree node {source_node_id} has no available port")
    child_node_id = state.topology.add_node(
        {
            "role": "hybrid_expansion_column_tree",
            "column": column,
            "parent_sink_id": parent_node_id,
        }
    )
    child_port_id = 5
    edge_id = state.topology.connect_ports(
        source_node_id,
        port_id_to_slot(source_port_id),
        child_node_id,
        port_id_to_slot(child_port_id),
        payload={
            "kind": "hybrid_expansion_column_tree",
            "column": column,
            "parent_sink_id": parent_node_id,
        },
    )
    conductance = aggregate_bond_conductance(
        boundary_conductances,
        fallback=fallback_conductance,
    )
    internal_edge_ids.append(edge_id)
    internal_edge_payloads[edge_id] = PortEdge(
        node_u=source_node_id,
        port_u=source_port_id,
        node_v=child_node_id,
        port_v=child_port_id,
        conductance=conductance,
        flux_uv=0.0,
    )
    column_tree_nodes[column].append(child_node_id)
    module_node_ids.append(child_node_id)
    return child_node_id


def _same_column_ports(column: int, *, preferred: int) -> tuple[int, ...]:
    ports = [rc_to_port(row, column) for row in range(1, 4)]
    ordered = [int(preferred)] + [port_id for port_id in ports if port_id != preferred]
    return tuple(port_id for port_id in ordered if port_id in ports)


def _first_available_port(
    state: GRC9V3State,
    node_id: NodeId,
    preferred_port_ids: Sequence[int] | range,
) -> int | None:
    for port_id in preferred_port_ids:
        if 1 <= int(port_id) <= 9 and not state.topology.port_is_occupied(
            node_id,
            port_id_to_slot(int(port_id)),
        ):
            return int(port_id)
    return None


def _local_port_id(state: GRC9V3State, *, edge_id: EdgeId, node_id: NodeId) -> int:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return slot_to_port_id(endpoint_a[1])
    if endpoint_b[0] == node_id:
        return slot_to_port_id(endpoint_b[1])
    raise ValueError(f"edge {edge_id} is not incident to node {node_id}")


def _neighbor_node_id(state: GRC9V3State, *, edge_id: EdgeId, node_id: NodeId) -> NodeId:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return endpoint_b[0]
    if endpoint_b[0] == node_id:
        return endpoint_a[0]
    raise ValueError(f"edge {edge_id} is not incident to node {node_id}")


def _edge_base_conductance(state: GRC9V3State, *, edge_id: EdgeId) -> float:
    if edge_id in state.base_conductance:
        return _finite_float(
            state.base_conductance[edge_id],
            context=f"edge {edge_id} base_conductance",
        )
    port_edge = state.port_edges.get(edge_id)
    if port_edge is None:
        return 1.0
    return _finite_float(
        port_edge.conductance,
        context=f"edge {edge_id} port_edge.conductance",
    )


def _resolve_previous_column_h_values(
    state: GRC9V3State,
    *,
    node_id: NodeId,
    previous_column_h_values: Sequence[float] | None,
) -> tuple[float, float, float] | None:
    if previous_column_h_values is None:
        previous_by_node = state.cached_quantities.get("previous_column_h_by_node", {})
        if isinstance(previous_by_node, Mapping):
            previous_column_h_values = previous_by_node.get(node_id)
            if previous_column_h_values is None:
                previous_column_h_values = previous_by_node.get(str(node_id))
    if previous_column_h_values is None:
        return None
    if len(previous_column_h_values) != 3:
        raise ValueError("previous_column_h_values must contain exactly three values")
    return tuple(
        _finite_float(value, context=f"previous_column_h_values[{index}]")
        for index, value in enumerate(previous_column_h_values)
    )


def _previous_column_h_status(
    previous_values: tuple[float, float, float] | None,
    *,
    explicit_previous_values: Sequence[float] | None,
    modes: Mapping[str, Any],
) -> str:
    if previous_values is not None:
        return "available"
    if explicit_previous_values is not None:
        return "invalid_unavailable"
    if not bool(modes.get("store_previous_column_h", False)):
        return "unavailable_storage_disabled"
    return "unavailable_new_or_first_step"


def _column_h_sign_crossing_columns(
    previous_values: tuple[float, float, float],
    current_values: tuple[float, float, float],
    *,
    mode: str,
    eps_zero: float,
) -> tuple[int, ...]:
    if mode == "theory_product":
        return tuple(
            index + 1
            for index, (previous, current) in enumerate(zip(previous_values, current_values))
            if previous * current < 0.0
        )
    if mode == "zero_band":
        return tuple(
            index + 1
            for index, (previous, current) in enumerate(zip(previous_values, current_values))
            if _zero_band_sign(previous, eps_zero=eps_zero)
            * _zero_band_sign(current, eps_zero=eps_zero)
            == -1
        )
    raise ValueError("column_h_sign_crossing_mode must be theory_product or zero_band")


def _zero_band_sign(value: float, *, eps_zero: float) -> int:
    if value > eps_zero:
        return 1
    if value < -eps_zero:
        return -1
    return 0


def _finite_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{context} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{context} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{context} must be a finite number")
    return result


def _mapping_keys_as_strings(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ()
    return tuple(str(key) for key in value)


def _hydrate_port_edges_from_topology(
    state: GRC9V3State,
    *,
    port_edges: Mapping[EdgeId, PortEdge],
) -> dict[EdgeId, PortEdge]:
    hydrated: dict[EdgeId, PortEdge] = {}
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        existing = port_edges.get(edge_id)
        conductance = 1.0 if existing is None else float(existing.conductance)
        flux_uv = 0.0 if existing is None else float(existing.flux_uv)
        hydrated[edge_id] = _canonical_port_edge(
            endpoint_a,
            endpoint_b,
            conductance=conductance,
            flux_uv=flux_uv,
        )
    return hydrated


def _canonical_port_edge(
    endpoint_a: tuple[int, int],
    endpoint_b: tuple[int, int],
    *,
    conductance: float,
    flux_uv: float,
) -> PortEdge:
    port_a = slot_to_port_id(endpoint_a[1])
    port_b = slot_to_port_id(endpoint_b[1])
    if (endpoint_a[0], port_a) <= (endpoint_b[0], port_b):
        return PortEdge(
            node_u=endpoint_a[0],
            port_u=port_a,
            node_v=endpoint_b[0],
            port_v=port_b,
            conductance=conductance,
            flux_uv=flux_uv,
        )
    return PortEdge(
        node_u=endpoint_b[0],
        port_u=port_b,
        node_v=endpoint_a[0],
        port_v=port_a,
        conductance=conductance,
        flux_uv=-flux_uv,
    )


def _prune_after_topology_change(state: GRC9V3State) -> None:
    live_nodes = set(state.topology.iter_live_node_ids())
    live_edges = set(state.topology.iter_live_edge_ids())
    state.nodes = {node_id: node for node_id, node in state.nodes.items() if node_id in live_nodes}
    state.base_conductance = {
        edge_id: value for edge_id, value in state.base_conductance.items() if edge_id in live_edges
    }
    state.geometric_length = {
        edge_id: value for edge_id, value in state.geometric_length.items() if edge_id in live_edges
    }
    state.temporal_delay = {
        edge_id: value for edge_id, value in state.temporal_delay.items() if edge_id in live_edges
    }
    state.flux_coupling = {
        edge_id: value for edge_id, value in state.flux_coupling.items() if edge_id in live_edges
    }
    state.potential = {
        node_id: value for node_id, value in state.potential.items() if node_id in live_nodes
    }
    state.sink_set &= live_nodes
    state.basins = {
        sink_id: members & live_nodes
        for sink_id, members in state.basins.items()
        if sink_id in live_nodes
    }
    cleared = bool(state.coarse_cache)
    state.coarse_cache.clear()
    state.cached_quantities["coarse_cache_invalidated"] = bool(
        state.cached_quantities.get("coarse_cache_invalidated", False)
    ) or cleared
    state.cached_quantities["coarse_cache_invalidation_reason"] = (
        "hybrid_expansion_topology_change"
    )
    invalidate_previous_column_h_cache(
        state,
        reason="hybrid_expansion_topology_change",
    )


__all__ = [
    "COLUMN_H_COMPUTATION_VERSION",
    "ColumnHResult",
    "ColumnHTerm",
    "apply_mechanical_expansion",
    "compute_column_hessian_proxy",
    "detect_hybrid_spark_candidates",
    "evaluate_child_basin_stabilization",
    "invalidate_previous_column_h_cache",
    "register_completed_hybrid_spark",
    "refresh_column_h_history",
]

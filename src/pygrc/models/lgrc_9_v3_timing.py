"""LGRC9V3 timing, distance, causal annotation, and fixed-topology eligibility helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import heapq
import math
from typing import Any, Final

from pygrc.core import (
    digest_canonical_data,
    EdgeId,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    NodeId,
    SnapshotCompatibilityError,
)

from .grc_9_ports import port_to_rc
from .grc_9_v3_state import GRC9V3State

from .lgrc_9_v3_contract import *


@dataclass(frozen=True)
class LGRC9V3CausalAnnotation:
    """Annotation-only LGRC-0 causal overlay for a synchronous GRC9V3 state."""

    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    node_proper_time: dict[NodeId, float]
    node_last_update_proper_time: dict[NodeId, float]
    edge_causal_delay: dict[EdgeId, float]
    lapse: dict[NodeId, float]
    event_time_records: tuple[dict[str, Any], ...]
    geometric_distance_by_source: dict[NodeId, dict[NodeId, float]]
    causal_distance_by_source: dict[NodeId, dict[NodeId, float]]
    functional_distance_by_source: dict[NodeId, dict[NodeId, float]]
    causal_cone_by_source: dict[NodeId, tuple[NodeId, ...]]
    causal_basin_core_by_sink: dict[NodeId, tuple[NodeId, ...]]
    causal_cone_horizon: float | None
    policies: dict[str, Any]
    causal_layer_mode: str = CAUSAL_LAYER_MODE_ANNOTATION
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC0
    diagnostic_source: str = LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE
    evidence_class: str = LGRC9V3_DERIVED_EVIDENCE_CLASS
    annotation_only: bool = True

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible artifact payload with stable string keys."""

        return {
            "diagnostic_source": self.diagnostic_source,
            "artifact_kind": LGRC9V3_CAUSAL_ARTIFACT_KIND,
            "artifact_schema_version": LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION,
            "annotation_mode_version": LGRC9V3_ANNOTATION_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": self.evidence_class,
            "annotation_only": self.annotation_only,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "scheduler_event_index": self.scheduler_event_index,
            "checkpoint_index": self.checkpoint_index,
            "event_time_key": self.event_time_key,
            "causal_cone_horizon": self.causal_cone_horizon,
            "policies": dict(sorted(self.policies.items())),
            "node_proper_time": _string_keyed_float_map(self.node_proper_time),
            "node_last_update_proper_time": _string_keyed_float_map(
                self.node_last_update_proper_time
            ),
            "edge_causal_delay": _string_keyed_float_map(self.edge_causal_delay),
            "lapse": _string_keyed_float_map(self.lapse),
            "event_time_records": [dict(record) for record in self.event_time_records],
            "distance_surfaces": {
                "geometric": _string_keyed_nested_float_map(
                    self.geometric_distance_by_source
                ),
                "causal": _string_keyed_nested_float_map(
                    self.causal_distance_by_source
                ),
                "functional": _string_keyed_nested_float_map(
                    self.functional_distance_by_source
                ),
            },
            "causal_cone_by_source": _string_keyed_sequence_map(
                self.causal_cone_by_source
            ),
            "causal_basin_core_by_sink": _string_keyed_sequence_map(
                self.causal_basin_core_by_sink
            ),
            "causal_basin_core_evidence_class": self.evidence_class,
        }


@dataclass(frozen=True)
class LGRC9V3FixedTopologyEligibility:
    """LGRC-1 semi-causal eligibility evidence on fixed topology."""

    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    node_proper_time: dict[NodeId, float]
    node_last_update_proper_time: dict[NodeId, float]
    node_elapsed_proper_time: dict[NodeId, float]
    next_node_last_update_proper_time: dict[NodeId, float]
    edge_causal_delay: dict[EdgeId, float]
    lapse: dict[NodeId, float]
    eligible_node_ids: tuple[NodeId, ...]
    ineligible_node_ids: tuple[NodeId, ...]
    processed_node_ids: tuple[NodeId, ...]
    min_delta_tau: float
    budget_before: float
    budget_after: float
    budget_error: float
    topology_signature: dict[str, Any]
    policies: dict[str, Any]
    causal_layer_mode: str = CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC1
    diagnostic_source: str = LGRC9V3_LGRC1_DIAGNOSTIC_SOURCE
    evidence_class: str = LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS
    semi_causal: bool = True
    causal_availability_buffers: bool = False
    topology_change_allowed: bool = False
    mechanical_expansion_allowed: bool = False
    collapse_allowed: bool = False
    identity_acceptance_allowed: bool = False
    packetized_flux: bool = False
    proper_time_virtual_advance_all_nodes: bool = True

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible semi-causal eligibility artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC1_ARTIFACT_KIND,
            "artifact_schema_version": LGRC9V3_LGRC1_ARTIFACT_SCHEMA_VERSION,
            "mode_version": LGRC9V3_LGRC1_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "diagnostic_source": self.diagnostic_source,
            "evidence_class": self.evidence_class,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "semi_causal": self.semi_causal,
            "causal_availability_buffers": self.causal_availability_buffers,
            "topology_change_allowed": self.topology_change_allowed,
            "mechanical_expansion_allowed": self.mechanical_expansion_allowed,
            "collapse_allowed": self.collapse_allowed,
            "identity_acceptance_allowed": self.identity_acceptance_allowed,
            "packetized_flux": self.packetized_flux,
            "proper_time_virtual_advance_all_nodes": (
                self.proper_time_virtual_advance_all_nodes
            ),
            "scheduler_event_index": self.scheduler_event_index,
            "checkpoint_index": self.checkpoint_index,
            "event_time_key": self.event_time_key,
            "min_delta_tau": self.min_delta_tau,
            "budget_before": self.budget_before,
            "budget_after": self.budget_after,
            "budget_error": self.budget_error,
            "policies": dict(sorted(self.policies.items())),
            "topology_signature": dict(self.topology_signature),
            "node_proper_time": _string_keyed_float_map(self.node_proper_time),
            "node_last_update_proper_time": _string_keyed_float_map(
                self.node_last_update_proper_time
            ),
            "node_elapsed_proper_time": _string_keyed_float_map(
                self.node_elapsed_proper_time
            ),
            "next_node_last_update_proper_time": _string_keyed_float_map(
                self.next_node_last_update_proper_time
            ),
            "edge_causal_delay": _string_keyed_float_map(self.edge_causal_delay),
            "lapse": _string_keyed_float_map(self.lapse),
            "eligible_node_ids": [int(node_id) for node_id in self.eligible_node_ids],
            "ineligible_node_ids": [
                int(node_id) for node_id in self.ineligible_node_ids
            ],
            "processed_node_ids": [
                int(node_id) for node_id in self.processed_node_ids
            ],
        }



def _require_edge_value(
    values: Mapping[EdgeId, float],
    edge_id: EdgeId,
    *,
    context: str,
    positive: bool = True,
) -> float:
    if edge_id not in values:
        raise ValueError(f"{context} missing edge {edge_id}")
    if positive:
        return _positive_float(values[edge_id], context=f"{context}[{edge_id}]")
    return _nonnegative_float(values[edge_id], context=f"{context}[{edge_id}]")


def _neighbor_for_edge(
    state: GRC9V3State,
    *,
    edge_id: EdgeId,
    node_id: NodeId,
) -> NodeId:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return int(endpoint_b[0])
    if endpoint_b[0] == node_id:
        return int(endpoint_a[0])
    raise ValueError(f"edge {edge_id} is not incident to node {node_id}")


def compute_lgrc9v3_lapse_by_node(
    state: GRC9V3State,
    *,
    policy: str = LAPSE_POLICY_BOUNDED_DENSITY_TENSION,
    lambda_n: float = 0.1,
    mu_n: float = 0.1,
    c_ref: float | None = None,
    g_ref: float | None = None,
    eps_c: float = 1e-12,
    eps_g: float = 1e-12,
    n_min: float = 1e-6,
    n_max: float = 10.0,
) -> dict[NodeId, float]:
    """Compute node-local lapse values without mutating state.

    ``LAPSE_POLICY_UNIT`` returns ``N_i = 1`` for every live node and is the
    policy used by synchronous-limit tests.
    """

    live_node_ids = _live_node_ids(state)
    if not live_node_ids:
        return {}
    if policy == LAPSE_POLICY_UNIT:
        return {node_id: 1.0 for node_id in live_node_ids}
    if policy != LAPSE_POLICY_BOUNDED_DENSITY_TENSION:
        raise ValueError(f"unsupported lapse policy: {policy}")

    lambda_value = _nonnegative_float(lambda_n, context="lambda_n")
    mu_value = _nonnegative_float(mu_n, context="mu_n")
    eps_c_value = _positive_float(eps_c, context="eps_c")
    eps_g_value = _positive_float(eps_g, context="eps_g")
    n_min_value = _positive_float(n_min, context="n_min")
    n_max_value = _positive_float(n_max, context="n_max")
    if n_min_value > n_max_value:
        raise ValueError("n_min must be <= n_max")

    coherences = {
        node_id: _finite_float(
            state.nodes[node_id].coherence,
            context=f"node_coherence[{node_id}]",
        )
        for node_id in live_node_ids
        if node_id in state.nodes
    }
    missing_nodes = set(live_node_ids) - set(coherences)
    if missing_nodes:
        raise ValueError(f"node state missing for live nodes: {sorted(missing_nodes)}")

    gradient_norms: dict[NodeId, float] = {}
    for node_id in live_node_ids:
        gradient = state.nodes[node_id].gradient_row_basis
        values = [
            _finite_float(value, context=f"gradient_row_basis[{node_id}]")
            for value in gradient
        ]
        gradient_norms[node_id] = math.sqrt(sum(value * value for value in values))

    resolved_c_ref = (
        _positive_float(c_ref, context="c_ref")
        if c_ref is not None
        else max(eps_c_value, sorted(coherences.values())[len(coherences) // 2])
    )
    resolved_g_ref = (
        _positive_float(g_ref, context="g_ref")
        if g_ref is not None
        else max(eps_g_value, sorted(gradient_norms.values())[len(gradient_norms) // 2])
    )

    lapse_by_node: dict[NodeId, float] = {}
    for node_id in live_node_ids:
        raw_lapse = (
            1.0
            + lambda_value
            * (coherences[node_id] - resolved_c_ref)
            / (resolved_c_ref + eps_c_value)
            + mu_value * gradient_norms[node_id] / (resolved_g_ref + eps_g_value)
        )
        lapse_by_node[node_id] = min(n_max_value, max(n_min_value, raw_lapse))
    return lapse_by_node


def compute_lgrc9v3_edge_causal_delay(
    state: GRC9V3State,
    *,
    policy: str = EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
    tau_0: float = 1.0,
    tau_min: float = 1e-12,
    v0: float = 1.0,
    rho: float = 1.0,
    eps_tau: float = 1e-12,
) -> dict[EdgeId, float]:
    """Compute edge causal delays without mutating state."""

    tau_0_value = _positive_float(tau_0, context="tau_0")
    tau_min_value = _positive_float(tau_min, context="tau_min")
    v0_value = _positive_float(v0, context="v0")
    rho_value = _nonnegative_float(rho, context="rho")
    eps_tau_value = _positive_float(eps_tau, context="eps_tau")

    delays: dict[EdgeId, float] = {}
    for edge_id in _live_edge_ids(state):
        if policy == EDGE_DELAY_POLICY_CONSTANT_DELAY:
            delays[edge_id] = tau_0_value
            continue

        geometric_length = _require_edge_value(
            state.geometric_length,
            edge_id,
            context="geometric_length",
        )
        if policy == EDGE_DELAY_POLICY_GEOMETRY_BASELINE:
            delays[edge_id] = tau_0_value * geometric_length
        elif policy == EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL:
            flux_coupling = state.flux_coupling.get(edge_id)
            if flux_coupling is None:
                flux_coupling = abs(state.port_edges[edge_id].flux_uv)
            flux_value = _nonnegative_float(
                flux_coupling,
                context=f"flux_coupling[{edge_id}]",
            )
            delays[edge_id] = max(
                tau_min_value,
                geometric_length / (v0_value + rho_value * flux_value + eps_tau_value),
            )
        else:
            raise ValueError(f"unsupported edge delay policy: {policy}")
    return delays


def compute_lgrc9v3_geometric_edge_costs(
    state: GRC9V3State,
) -> dict[EdgeId, float]:
    """Return geometric edge costs from `state.geometric_length`."""

    return {
        edge_id: _require_edge_value(
            state.geometric_length,
            edge_id,
            context="geometric_length",
        )
        for edge_id in _live_edge_ids(state)
    }


def compute_lgrc9v3_causal_edge_costs(
    state: GRC9V3State,
    *,
    edge_causal_delay: Mapping[EdgeId, float],
) -> dict[EdgeId, float]:
    """Return causal/proper-time edge costs from explicit causal delays."""

    return {
        edge_id: _require_edge_value(
            edge_causal_delay,
            edge_id,
            context="edge_causal_delay",
        )
        for edge_id in _live_edge_ids(state)
    }


def compute_lgrc9v3_functional_edge_costs(
    state: GRC9V3State,
    *,
    policy: str = FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
    eps: float = 1e-12,
) -> dict[EdgeId, float]:
    """Return functional/coupling costs where stronger coupling is shorter."""

    if policy not in _ALLOWED_FUNCTIONAL_DISTANCE_POLICIES:
        raise ValueError(f"unsupported functional distance policy: {policy}")
    eps_value = _positive_float(eps, context="eps")

    costs: dict[EdgeId, float] = {}
    for edge_id in _live_edge_ids(state):
        if policy == FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE:
            strength = _require_edge_value(
                state.base_conductance,
                edge_id,
                context="base_conductance",
            )
        elif policy == FUNCTIONAL_DISTANCE_POLICY_INVERSE_FLUX_COUPLING:
            strength = _require_edge_value(
                state.flux_coupling,
                edge_id,
                context="flux_coupling",
            )
        else:
            base = _require_edge_value(
                state.base_conductance,
                edge_id,
                context="base_conductance",
            )
            flux = _require_edge_value(
                state.flux_coupling,
                edge_id,
                context="flux_coupling",
            )
            strength = base + flux
        costs[edge_id] = 1.0 / max(eps_value, strength)
    return costs


def compute_lgrc9v3_shortest_path_distances(
    state: GRC9V3State,
    *,
    source_node_id: NodeId,
    edge_costs: Mapping[EdgeId, float],
) -> dict[NodeId, float]:
    """Compute deterministic undirected shortest-path distances.

    LGRC-0 uses symmetric edge-delay annotations, so the helper walks incident
    port edges without orientation. Directed future/past cones require a
    directed adjacency surface and belong to a later packet/causal runtime.
    """

    source_id = int(source_node_id)
    if not state.topology.has_node(source_id):
        raise ValueError(f"source node {source_id} is not live")

    live_edge_ids = set(_live_edge_ids(state))
    costs = {
        edge_id: _require_edge_value(edge_costs, edge_id, context="edge_costs")
        for edge_id in live_edge_ids
    }
    distances: dict[NodeId, float] = {source_id: 0.0}
    queue: list[tuple[float, NodeId]] = [(0.0, source_id)]

    while queue:
        current_distance, node_id = heapq.heappop(queue)
        if current_distance > distances.get(node_id, math.inf):
            continue
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            edge_id = int(edge_id)
            if edge_id not in live_edge_ids:
                continue
            neighbor_id = _neighbor_for_edge(
                state,
                edge_id=edge_id,
                node_id=node_id,
            )
            candidate_distance = current_distance + costs[edge_id]
            if candidate_distance < distances.get(neighbor_id, math.inf):
                distances[neighbor_id] = candidate_distance
                heapq.heappush(queue, (candidate_distance, neighbor_id))
    return dict(sorted(distances.items()))


def compute_lgrc9v3_geometric_distances(
    state: GRC9V3State,
    *,
    source_node_id: NodeId,
) -> dict[NodeId, float]:
    """Compute shortest geometric distances from one source node."""

    return compute_lgrc9v3_shortest_path_distances(
        state,
        source_node_id=source_node_id,
        edge_costs=compute_lgrc9v3_geometric_edge_costs(state),
    )


def compute_lgrc9v3_causal_distances(
    state: GRC9V3State,
    *,
    source_node_id: NodeId,
    edge_causal_delay: Mapping[EdgeId, float],
) -> dict[NodeId, float]:
    """Compute shortest causal/proper-time distances from one source node."""

    return compute_lgrc9v3_shortest_path_distances(
        state,
        source_node_id=source_node_id,
        edge_costs=compute_lgrc9v3_causal_edge_costs(
            state,
            edge_causal_delay=edge_causal_delay,
        ),
    )


def compute_lgrc9v3_functional_distances(
    state: GRC9V3State,
    *,
    source_node_id: NodeId,
    policy: str = FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
) -> dict[NodeId, float]:
    """Compute shortest functional/coupling distances from one source node."""

    return compute_lgrc9v3_shortest_path_distances(
        state,
        source_node_id=source_node_id,
        edge_costs=compute_lgrc9v3_functional_edge_costs(state, policy=policy),
    )


def _resolve_source_node_ids(
    state: GRC9V3State,
    source_node_ids: Iterable[NodeId] | None,
) -> tuple[NodeId, ...]:
    live_node_ids = set(_live_node_ids(state))
    if source_node_ids is None:
        return tuple(sorted(live_node_ids))
    resolved = tuple(sorted({int(node_id) for node_id in source_node_ids}))
    missing = set(resolved) - live_node_ids
    if missing:
        raise ValueError(f"source nodes are not live: {sorted(missing)}")
    return resolved


def _event_time_for_event(
    event: GRCEvent,
    *,
    event_time_policy: str,
    event_time_scale: float,
) -> float:
    if event_time_policy == EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY:
        raw_value = event.payload.get("event_time_key")
        if raw_value is None:
            raw_value = event.payload.get("T_e")
        if raw_value is None:
            raise ValueError(
                "explicit_event_time_key requires event payload field "
                "'event_time_key'"
            )
        return _nonnegative_float(raw_value, context="event_time_key")
    return _nonnegative_float(
        float(event.step_index) * event_time_scale,
        context="derived event_time_key",
    )


def _event_time_records(
    events: Sequence[GRCEvent],
    *,
    event_time_policy: str,
    event_time_scale: float,
    scheduler_event_index: int,
) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for event_index, event in enumerate(events):
        records.append(
            {
                "diagnostic_source": LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE,
                "evidence_class": LGRC9V3_DERIVED_EVIDENCE_CLASS,
                "annotation_only": True,
                "event_index": event_index,
                "kind": event.kind,
                "step_index": int(event.step_index),
                "scheduler_event_index": int(scheduler_event_index) + event_index,
                "event_time_key": _event_time_for_event(
                    event,
                    event_time_policy=event_time_policy,
                    event_time_scale=event_time_scale,
                ),
                "source_family": event.source_family,
            }
        )
    return tuple(records)


def _distances_by_source(
    state: GRC9V3State,
    *,
    source_node_ids: Sequence[NodeId],
    surface: str,
    edge_causal_delay: Mapping[EdgeId, float] | None = None,
    functional_distance_policy: str = FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
) -> dict[NodeId, dict[NodeId, float]]:
    distances: dict[NodeId, dict[NodeId, float]] = {}
    for source_node_id in source_node_ids:
        if surface == "geometric":
            distances[source_node_id] = compute_lgrc9v3_geometric_distances(
                state,
                source_node_id=source_node_id,
            )
        elif surface == "causal":
            if edge_causal_delay is None:
                raise ValueError("edge_causal_delay is required for causal distances")
            distances[source_node_id] = compute_lgrc9v3_causal_distances(
                state,
                source_node_id=source_node_id,
                edge_causal_delay=edge_causal_delay,
            )
        elif surface == "functional":
            distances[source_node_id] = compute_lgrc9v3_functional_distances(
                state,
                source_node_id=source_node_id,
                policy=functional_distance_policy,
            )
        else:
            raise ValueError(f"unsupported distance surface: {surface}")
    return distances


def _causal_cones_from_distances(
    distances_by_source: Mapping[NodeId, Mapping[NodeId, float]],
    *,
    causal_cone_horizon: float | None,
) -> dict[NodeId, tuple[NodeId, ...]]:
    horizon = math.inf
    if causal_cone_horizon is not None:
        horizon = _nonnegative_float(
            causal_cone_horizon,
            context="causal_cone_horizon",
        )
    return {
        int(source_node_id): tuple(
            sorted(
                int(node_id)
                for node_id, distance in distances.items()
                if _nonnegative_float(
                    distance,
                    context=f"causal_distance[{source_node_id}][{node_id}]",
                )
                <= horizon
            )
        )
        for source_node_id, distances in sorted(distances_by_source.items())
    }


def _causal_basin_core_from_distances(
    state: GRC9V3State,
    *,
    causal_distance_by_source: Mapping[NodeId, Mapping[NodeId, float]],
    causal_cone_horizon: float | None,
) -> dict[NodeId, tuple[NodeId, ...]]:
    horizon = math.inf
    if causal_cone_horizon is not None:
        horizon = _nonnegative_float(
            causal_cone_horizon,
            context="causal_cone_horizon",
        )
    live_node_ids = set(_live_node_ids(state))
    core_by_sink: dict[NodeId, tuple[NodeId, ...]] = {}
    for sink_id, members in sorted(state.basins.items()):
        sink = int(sink_id)
        if sink not in live_node_ids:
            continue
        core_members: list[NodeId] = []
        for member_id in sorted(int(member) for member in members):
            if member_id not in live_node_ids:
                continue
            distance_to_sink = causal_distance_by_source.get(member_id, {}).get(sink)
            if distance_to_sink is None:
                continue
            if (
                _nonnegative_float(
                    distance_to_sink,
                    context=f"causal_basin_distance[{member_id}][{sink}]",
                )
                <= horizon
            ):
                core_members.append(member_id)
        core_by_sink[sink] = tuple(core_members)
    return core_by_sink


def annotate_lgrc9v3_causal_history(
    state: GRC9V3State,
    *,
    events: Sequence[GRCEvent] | None = None,
    causal_modes: Mapping[str, Any] | None = None,
    scheduler_event_index: int | None = None,
    checkpoint_index: int | None = None,
    event_time_key: float | None = None,
    event_time_scale: float = 1.0,
    causal_cone_horizon: float | None = None,
    source_node_ids: Iterable[NodeId] | None = None,
    previous_node_proper_time: Mapping[NodeId, float] | None = None,
    lapse_kwargs: Mapping[str, Any] | None = None,
    edge_delay_kwargs: Mapping[str, Any] | None = None,
    functional_distance_policy: str = (
        FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE
    ),
) -> LGRC9V3CausalAnnotation:
    """Build an LGRC-0 causal annotation overlay without mutating state.

    This is an evidence surface over an existing synchronous ``GRC9V3`` state.
    It derives proper-time, edge-delay, distance, cone, and basin-core fields
    for analysis artifacts. It does not execute an LGRC runtime, change event
    counts, mutate topology, update budgets, or alter observables.
    """

    modes = validate_lgrc9v3_causal_modes(causal_modes)
    if modes["causal_layer_mode"] != CAUSAL_LAYER_MODE_ANNOTATION:
        raise InvalidParamsError(
            "LGRC-0 annotation requires causal_layer_mode='annotation'"
        )
    if modes["lgrc_runtime_level"] != LGRC_RUNTIME_LEVEL_LGRC0:
        raise InvalidParamsError(
            "LGRC-0 annotation requires lgrc_runtime_level='lgrc0'"
        )

    scale = _positive_float(event_time_scale, context="event_time_scale")
    resolved_checkpoint_index = (
        int(state.step_index) if checkpoint_index is None else int(checkpoint_index)
    )
    if resolved_checkpoint_index < 0:
        raise ValueError("checkpoint_index must be >= 0")
    resolved_scheduler_event_index = (
        int(state.step_index)
        if scheduler_event_index is None
        else int(scheduler_event_index)
    )
    if resolved_scheduler_event_index < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    resolved_event_time_key = (
        float(resolved_checkpoint_index) * scale
        if event_time_key is None
        else _nonnegative_float(event_time_key, context="event_time_key")
    )
    resolved_horizon = (
        None
        if causal_cone_horizon is None
        else _nonnegative_float(causal_cone_horizon, context="causal_cone_horizon")
    )

    live_node_ids = _live_node_ids(state)
    selected_source_ids = _resolve_source_node_ids(state, source_node_ids)
    resolved_events = tuple(events or ())
    lapse_params = dict(lapse_kwargs or {})
    edge_delay_params = dict(edge_delay_kwargs or {})

    lapse = compute_lgrc9v3_lapse_by_node(
        state,
        policy=modes["lapse_policy"],
        **lapse_params,
    )
    edge_causal_delay = compute_lgrc9v3_edge_causal_delay(
        state,
        policy=modes["edge_delay_policy"],
        **edge_delay_params,
    )
    node_proper_time = {
        node_id: resolved_event_time_key * lapse[node_id]
        for node_id in live_node_ids
    }
    if previous_node_proper_time is None:
        node_last_update_proper_time = {node_id: 0.0 for node_id in live_node_ids}
    else:
        node_last_update_proper_time = {
            node_id: _nonnegative_float(
                previous_node_proper_time.get(node_id, 0.0),
                context=f"previous_node_proper_time[{node_id}]",
            )
            for node_id in live_node_ids
        }

    geometric_distance_by_source = _distances_by_source(
        state,
        source_node_ids=selected_source_ids,
        surface="geometric",
    )
    functional_distance_by_source = _distances_by_source(
        state,
        source_node_ids=selected_source_ids,
        surface="functional",
        functional_distance_policy=functional_distance_policy,
    )
    causal_distance_by_source: dict[NodeId, dict[NodeId, float]] = {}
    all_node_causal_distance_by_source: dict[NodeId, dict[NodeId, float]] = {}
    if modes["causal_distance_policy"] != CAUSAL_DISTANCE_POLICY_DISABLED:
        causal_distance_by_source = _distances_by_source(
            state,
            source_node_ids=selected_source_ids,
            surface="causal",
            edge_causal_delay=edge_causal_delay,
        )
        all_node_causal_distance_by_source = _distances_by_source(
            state,
            source_node_ids=live_node_ids,
            surface="causal",
            edge_causal_delay=edge_causal_delay,
        )

    causal_cone_by_source: dict[NodeId, tuple[NodeId, ...]] = {}
    if (
        modes["causal_cone_policy"] != CAUSAL_CONE_POLICY_DISABLED
        and causal_distance_by_source
    ):
        causal_cone_by_source = _causal_cones_from_distances(
            causal_distance_by_source,
            causal_cone_horizon=resolved_horizon,
        )

    causal_basin_core_by_sink: dict[NodeId, tuple[NodeId, ...]] = {}
    if (
        modes["causal_basin_core_policy"]
        == CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION
        and all_node_causal_distance_by_source
    ):
        causal_basin_core_by_sink = _causal_basin_core_from_distances(
            state,
            causal_distance_by_source=all_node_causal_distance_by_source,
            causal_cone_horizon=resolved_horizon,
        )

    policies = dict(modes)
    policies.update(
        {
            "event_time_scale": scale,
            "functional_distance_policy": functional_distance_policy,
            "lapse_params": dict(sorted(lapse_params.items())),
            "edge_delay_params": dict(sorted(edge_delay_params.items())),
            "causal_cone_horizon": resolved_horizon,
        }
    )

    return LGRC9V3CausalAnnotation(
        scheduler_event_index=resolved_scheduler_event_index,
        checkpoint_index=resolved_checkpoint_index,
        event_time_key=resolved_event_time_key,
        node_proper_time=node_proper_time,
        node_last_update_proper_time=node_last_update_proper_time,
        edge_causal_delay=edge_causal_delay,
        lapse=lapse,
        event_time_records=_event_time_records(
            resolved_events,
            event_time_policy=modes["event_time_policy"],
            event_time_scale=scale,
            scheduler_event_index=resolved_scheduler_event_index,
        ),
        geometric_distance_by_source=geometric_distance_by_source,
        causal_distance_by_source=causal_distance_by_source,
        functional_distance_by_source=functional_distance_by_source,
        causal_cone_by_source=causal_cone_by_source,
        causal_basin_core_by_sink=causal_basin_core_by_sink,
        causal_cone_horizon=resolved_horizon,
        policies=policies,
    )


def compute_lgrc9v3_fixed_topology_eligibility(
    state: GRC9V3State,
    *,
    causal_modes: Mapping[str, Any],
    scheduler_event_index: int | None = None,
    checkpoint_index: int | None = None,
    event_time_key: float | None = None,
    event_time_scale: float = 1.0,
    min_delta_tau: float = 0.0,
    node_last_update_proper_time: Mapping[NodeId, float] | None = None,
    processed_node_ids: Iterable[NodeId] | None = None,
    previous_topology_signature: Mapping[str, Any] | None = None,
    lapse_kwargs: Mapping[str, Any] | None = None,
    edge_delay_kwargs: Mapping[str, Any] | None = None,
    mechanical_expansion_requested: bool = False,
    collapse_requested: bool = False,
    identity_acceptance_requested: bool = False,
    packetized_flux_requested: bool = False,
) -> LGRC9V3FixedTopologyEligibility:
    """Compute opt-in LGRC-1 fixed-topology semi-causal eligibility.

    The helper makes proper-time eligibility operational while keeping the
    underlying ``GRC9V3State`` fixed. It virtually advances proper time for all
    live nodes, computes ``delta_tau_i`` since each node's last local update,
    and reports which nodes are eligible under ``min_delta_tau``. It does not
    move coherence, schedule packets, expand topology, emit identity events, or
    mutate the state.
    """

    modes = validate_lgrc9v3_causal_modes(causal_modes)
    if modes["causal_layer_mode"] != CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL:
        raise InvalidParamsError(
            "LGRC-1 eligibility requires "
            "causal_layer_mode='fixed_topology_semicausal'"
        )
    if modes["lgrc_runtime_level"] != LGRC_RUNTIME_LEVEL_LGRC1:
        raise InvalidParamsError("LGRC-1 eligibility requires lgrc_runtime_level='lgrc1'")
    if not modes["require_fixed_topology_for_lgrc1"]:
        raise InvalidParamsError("LGRC-1 v1 requires fixed topology")
    rejected_claims = {
        "mechanical_expansion_requested": mechanical_expansion_requested,
        "collapse_requested": collapse_requested,
        "identity_acceptance_requested": identity_acceptance_requested,
        "packetized_flux_requested": packetized_flux_requested,
    }
    for claim_name, requested in rejected_claims.items():
        if not isinstance(requested, bool):
            raise InvalidParamsError(f"{claim_name} must be a boolean")
        if requested:
            raise InvalidParamsError(f"{claim_name}=true is not supported in LGRC-1 v1")

    topology_signature = _validate_fixed_topology_signature(
        state,
        previous_topology_signature=previous_topology_signature,
    )
    scale = _positive_float(event_time_scale, context="event_time_scale")
    delta_threshold = _nonnegative_float(min_delta_tau, context="min_delta_tau")
    resolved_checkpoint_index = (
        int(state.step_index) if checkpoint_index is None else int(checkpoint_index)
    )
    if resolved_checkpoint_index < 0:
        raise ValueError("checkpoint_index must be >= 0")
    resolved_scheduler_event_index = (
        int(state.step_index)
        if scheduler_event_index is None
        else int(scheduler_event_index)
    )
    if resolved_scheduler_event_index < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    resolved_event_time_key = (
        float(resolved_checkpoint_index) * scale
        if event_time_key is None
        else _nonnegative_float(event_time_key, context="event_time_key")
    )

    live_node_ids = _live_node_ids(state)
    lapse_params = dict(lapse_kwargs or {})
    edge_delay_params = dict(edge_delay_kwargs or {})
    lapse = compute_lgrc9v3_lapse_by_node(
        state,
        policy=modes["lapse_policy"],
        **lapse_params,
    )
    edge_causal_delay = compute_lgrc9v3_edge_causal_delay(
        state,
        policy=modes["edge_delay_policy"],
        **edge_delay_params,
    )
    node_proper_time = {
        node_id: resolved_event_time_key * lapse[node_id]
        for node_id in live_node_ids
    }

    last_update = {
        node_id: 0.0
        if node_last_update_proper_time is None
        else _nonnegative_float(
            node_last_update_proper_time.get(node_id, 0.0),
            context=f"node_last_update_proper_time[{node_id}]",
        )
        for node_id in live_node_ids
    }
    elapsed: dict[NodeId, float] = {}
    for node_id in live_node_ids:
        delta_tau = node_proper_time[node_id] - last_update[node_id]
        if delta_tau < -1e-12:
            raise InvalidStateTransitionError(
                f"node {node_id} proper time moved backwards"
            )
        elapsed[node_id] = max(0.0, delta_tau)

    eligible = tuple(
        node_id for node_id in live_node_ids if elapsed[node_id] >= delta_threshold
    )
    ineligible = tuple(node_id for node_id in live_node_ids if node_id not in eligible)
    processed = (
        ()
        if processed_node_ids is None
        else tuple(sorted({int(node_id) for node_id in processed_node_ids}))
    )
    unknown_processed = set(processed) - set(live_node_ids)
    if unknown_processed:
        raise ValueError(f"processed nodes are not live: {sorted(unknown_processed)}")

    next_last_update = dict(last_update)
    for node_id in processed:
        next_last_update[node_id] = node_proper_time[node_id]

    budget_before = _coherence_budget(state)
    budget_after = _coherence_budget(state)
    policies = dict(modes)
    policies.update(
        {
            "event_time_scale": scale,
            "min_delta_tau": delta_threshold,
            "lapse_params": dict(sorted(lapse_params.items())),
            "edge_delay_params": dict(sorted(edge_delay_params.items())),
            "semi_causal": True,
            "causal_availability_buffers": False,
            "packetized_flux": False,
        }
    )

    return LGRC9V3FixedTopologyEligibility(
        scheduler_event_index=resolved_scheduler_event_index,
        checkpoint_index=resolved_checkpoint_index,
        event_time_key=resolved_event_time_key,
        node_proper_time=node_proper_time,
        node_last_update_proper_time=last_update,
        node_elapsed_proper_time=elapsed,
        next_node_last_update_proper_time=next_last_update,
        edge_causal_delay=edge_causal_delay,
        lapse=lapse,
        eligible_node_ids=eligible,
        ineligible_node_ids=ineligible,
        processed_node_ids=processed,
        min_delta_tau=delta_threshold,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_after - budget_before,
        topology_signature=topology_signature,
        policies=policies,
    )


def build_lgrc9v3_causal_history_artifact(
    annotation: LGRC9V3CausalAnnotation,
) -> dict[str, Any]:
    """Build a standalone LGRC9V3 causal-history artifact envelope."""

    return {
        "artifact_kind": LGRC9V3_CAUSAL_ARTIFACT_KIND,
        "artifact_schema_version": LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        LGRC9V3_CAUSAL_ARTIFACT_KEY: annotation.to_artifact(),
    }


def attach_lgrc9v3_causal_history_artifact(
    artifact: Mapping[str, Any],
    annotation: LGRC9V3CausalAnnotation,
) -> dict[str, Any]:
    """Return a top-level copy with an optional causal-history block.

    Nested groups from the original artifact are intentionally shared; the
    helper only attaches or replaces the top-level ``causal_history`` evidence
    block.
    """

    updated = dict(artifact)
    updated[LGRC9V3_CAUSAL_ARTIFACT_KEY] = annotation.to_artifact()
    return updated


def extract_lgrc9v3_causal_history_artifact(
    artifact: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Return the optional LGRC9V3 causal-history block from an artifact.

    Missing LGRC fields mean non-LGRC evidence. Readers must not invent causal
    semantics for older GRC/GRC9V3 snapshots that do not carry this block.
    """

    mapping = _require_artifact_mapping(artifact, context="artifact")
    if LGRC9V3_CAUSAL_ARTIFACT_KEY in mapping:
        block = _require_artifact_mapping(
            mapping[LGRC9V3_CAUSAL_ARTIFACT_KEY],
            context=LGRC9V3_CAUSAL_ARTIFACT_KEY,
        )
        return dict(block)
    if mapping.get("artifact_kind") == LGRC9V3_CAUSAL_ARTIFACT_KIND:
        return dict(mapping)
    return None


def restore_lgrc9v3_causal_annotation_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CausalAnnotation | None:
    """Restore an LGRC-0 annotation object from an optional artifact block."""

    block = extract_lgrc9v3_causal_history_artifact(artifact)
    if block is None:
        return None

    artifact_kind = _artifact_string(
        block.get("artifact_kind"),
        context="causal_history.artifact_kind",
    )
    if artifact_kind != LGRC9V3_CAUSAL_ARTIFACT_KIND:
        raise SnapshotCompatibilityError(
            f"unsupported LGRC9V3 artifact_kind: {artifact_kind!r}"
        )
    schema_version = _artifact_string(
        block.get("artifact_schema_version"),
        context="causal_history.artifact_schema_version",
    )
    if schema_version != LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            f"unsupported LGRC9V3 artifact_schema_version: {schema_version!r}"
        )
    runtime_family = _artifact_string(
        block.get("runtime_family"),
        context="causal_history.runtime_family",
    )
    if runtime_family != LGRC9V3_RUNTIME_FAMILY:
        raise SnapshotCompatibilityError("causal_history.runtime_family must be LGRC9V3")
    diagnostic_source = _artifact_string(
        block.get("diagnostic_source"),
        context="causal_history.diagnostic_source",
    )
    if diagnostic_source != LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE:
        raise SnapshotCompatibilityError(
            "causal_history.diagnostic_source must be lgrc0_causal_annotation"
        )
    evidence_class = _artifact_string(
        block.get("evidence_class"),
        context="causal_history.evidence_class",
    )
    if evidence_class != LGRC9V3_DERIVED_EVIDENCE_CLASS:
        raise SnapshotCompatibilityError(
            "causal_history.evidence_class must be derived_annotation"
        )
    basin_core_evidence_class = _artifact_string(
        block.get("causal_basin_core_evidence_class"),
        context="causal_history.causal_basin_core_evidence_class",
    )
    if basin_core_evidence_class != LGRC9V3_DERIVED_EVIDENCE_CLASS:
        raise SnapshotCompatibilityError(
            "causal_basin_core_evidence_class must be derived_annotation"
        )
    causal_layer_mode = _artifact_string(
        block.get("causal_layer_mode"),
        context="causal_history.causal_layer_mode",
    )
    if causal_layer_mode != CAUSAL_LAYER_MODE_ANNOTATION:
        raise SnapshotCompatibilityError(
            "causal_history.causal_layer_mode must be annotation"
        )
    runtime_level = _artifact_string(
        block.get("lgrc_runtime_level"),
        context="causal_history.lgrc_runtime_level",
    )
    if runtime_level != LGRC_RUNTIME_LEVEL_LGRC0:
        raise SnapshotCompatibilityError(
            "causal_history.lgrc_runtime_level must be lgrc0"
        )
    if not _artifact_bool(block.get("annotation_only"), context="annotation_only"):
        raise SnapshotCompatibilityError("LGRC-0 causal artifact must be annotation-only")

    policies = dict(
        _require_artifact_mapping(block.get("policies", {}), context="policies")
    )
    mode_subset = {
        key: policies[key]
        for key in LGRC9V3_CAUSAL_MODE_KEYS
        if key in policies
    }
    validate_lgrc9v3_causal_modes(mode_subset)

    distance_surfaces = _require_artifact_mapping(
        block.get("distance_surfaces", {}),
        context="distance_surfaces",
    )
    event_time_records_payload = block.get("event_time_records", [])
    if not isinstance(event_time_records_payload, list):
        raise SnapshotCompatibilityError("event_time_records must be a list")
    return LGRC9V3CausalAnnotation(
        scheduler_event_index=_artifact_int(
            block.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            block.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        event_time_key=_artifact_float(
            block.get("event_time_key"),
            context="event_time_key",
        ),
        node_proper_time=_parse_artifact_float_map(block, key="node_proper_time"),
        node_last_update_proper_time=_parse_artifact_float_map(
            block,
            key="node_last_update_proper_time",
        ),
        edge_causal_delay=_parse_artifact_float_map(block, key="edge_causal_delay"),
        lapse=_parse_artifact_float_map(block, key="lapse"),
        event_time_records=tuple(
            dict(_require_artifact_mapping(record, context="event_time_records[]"))
            for record in event_time_records_payload
        ),
        geometric_distance_by_source=_parse_artifact_nested_float_map(
            distance_surfaces,
            key="geometric",
        ),
        causal_distance_by_source=_parse_artifact_nested_float_map(
            distance_surfaces,
            key="causal",
        ),
        functional_distance_by_source=_parse_artifact_nested_float_map(
            distance_surfaces,
            key="functional",
        ),
        causal_cone_by_source=_parse_artifact_sequence_map(
            block,
            key="causal_cone_by_source",
        ),
        causal_basin_core_by_sink=_parse_artifact_sequence_map(
            block,
            key="causal_basin_core_by_sink",
        ),
        causal_cone_horizon=_artifact_optional_float(
            block.get("causal_cone_horizon"),
            context="causal_cone_horizon",
        ),
        policies=policies,
    )


__all__ = [
    'CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION',
    'CAUSAL_BASIN_CORE_POLICY_DISABLED',
    'CAUSAL_CONE_POLICY_BOUNDED_SHORTEST_PATH',
    'CAUSAL_CONE_POLICY_DISABLED',
    'CAUSAL_DISTANCE_POLICY_DISABLED',
    'CAUSAL_DISTANCE_POLICY_EDGE_DELAY_SHORTEST_PATH',
    'EDGE_DELAY_POLICY_CONSTANT_DELAY',
    'EDGE_DELAY_POLICY_GEOMETRY_BASELINE',
    'EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL',
    'EVENT_TIME_POLICY_DERIVED_FROM_SYNCHRONOUS_STEP',
    'EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY',
    'EVENT_TIME_POLICY_SYNCHRONOUS_LIMIT',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_COMBINED_COUPLING',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_FLUX_COUPLING',
    'LAPSE_POLICY_BOUNDED_DENSITY_TENSION',
    'LAPSE_POLICY_UNIT',
    'LGRC9V3CausalAnnotation',
    'LGRC9V3FixedTopologyEligibility',
    'LGRC9V3TimingFieldNames',
    'LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE',
    'LGRC9V3_ANNOTATION_MODE_VERSION',
    'LGRC9V3_CAUSAL_ARTIFACT_KEY',
    'LGRC9V3_CAUSAL_ARTIFACT_KIND',
    'LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION',
    'LGRC9V3_CAUSAL_MODES_KEY',
    'LGRC9V3_CAUSAL_MODE_KEYS',
    'LGRC9V3_DEFAULT_CAUSAL_MODES',
    'LGRC9V3_DERIVED_EVIDENCE_CLASS',
    'LGRC9V3_LGRC1_ARTIFACT_KIND',
    'LGRC9V3_LGRC1_ARTIFACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC1_DIAGNOSTIC_SOURCE',
    'LGRC9V3_LGRC1_MODE_VERSION',
    'LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS',
    'LGRC9V3_TIMING_ALIASES',
    'LGRC9V3_TIMING_FIELD_NAMES',
    'PROPER_TIME_POLICY_ANNOTATION',
    'PROPER_TIME_POLICY_GLOBAL_SCHEDULER',
    'PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER',
    'PROPER_TIME_POLICY_SYNCHRONOUS_LIMIT',
    '_causal_basin_core_from_distances',
    '_causal_cones_from_distances',
    '_distances_by_source',
    '_event_time_for_event',
    '_event_time_records',
    '_neighbor_for_edge',
    '_require_edge_value',
    '_resolve_source_node_ids',
    'annotate_lgrc9v3_causal_history',
    'attach_lgrc9v3_causal_history_artifact',
    'build_lgrc9v3_causal_history_artifact',
    'compute_lgrc9v3_causal_distances',
    'compute_lgrc9v3_causal_edge_costs',
    'compute_lgrc9v3_edge_causal_delay',
    'compute_lgrc9v3_fixed_topology_eligibility',
    'compute_lgrc9v3_functional_distances',
    'compute_lgrc9v3_functional_edge_costs',
    'compute_lgrc9v3_geometric_distances',
    'compute_lgrc9v3_geometric_edge_costs',
    'compute_lgrc9v3_lapse_by_node',
    'compute_lgrc9v3_shortest_path_distances',
    'extract_lgrc9v3_causal_history_artifact',
    'restore_lgrc9v3_causal_annotation_artifact',
]

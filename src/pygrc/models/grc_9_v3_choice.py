"""Choice, collapse, boundary, and budget helpers for GRC9V3."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygrc.core import GRCEvent, NodeId, SnapshotCompatibilityError

from .grc_9_v3_state import GRC9V3NodeState, GRC9V3State


def rebuild_grc9v3_choice_state(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
    source_family: str,
) -> list[GRCEvent]:
    """Evaluate deterministic sink-compatibility choice/collapse semantics."""

    choice_name = str(modes.get("choice_backend", "disabled"))
    if choice_name == "disabled":
        state.choice_registry = {}
        state.collapse_registry = {}
        state.cached_quantities["choice_state"] = {
            "backend": "disabled",
            "evaluated_nodes": {},
        }
        return []
    if choice_name != "sink_compatibility":
        raise NotImplementedError(
            "GRC9V3 choice supports only disabled or sink_compatibility"
        )

    score_params = _choice_score_params(evolution)
    epsilon_choice = score_params["epsilon_choice"]
    epsilon_collapse = score_params["epsilon_collapse"]
    successor_map = _successor_map_for_choice(state)
    sinks = set(state.sink_set)
    previous_registry = dict(state.choice_registry)
    collapse_registry = dict(state.collapse_registry)
    next_registry: dict[str, Any] = {}
    evaluated_nodes: dict[str, Any] = {}
    learning_updates: dict[str, Any] = dict(
        state.cached_quantities.get("choice_learning_state", {})
        if isinstance(state.cached_quantities.get("choice_learning_state"), Mapping)
        else {}
    )
    emitted_events: list[GRCEvent] = []

    for node_id in sorted(state.topology.iter_live_node_ids()):
        compatibility = _sink_compatibility_for_node(
            state,
            node_id,
            successor_map=successor_map,
            sinks=sinks,
            epsilon_choice=epsilon_choice,
        )
        if compatibility is None:
            continue

        key = str(node_id)
        evaluated_nodes[key] = {
            "scores": dict(compatibility["scores"]),
            "viable_sink_ids": list(compatibility["viable_sink_ids"]),
            "winner_sink_id": compatibility["winner_sink_id"],
            "winner_margin": compatibility["winner_margin"],
            "total_positive_flux": compatibility["total_positive_flux"],
        }
        viable_sink_ids = list(compatibility["viable_sink_ids"])
        previous_entry = previous_registry.get(key)

        if len(viable_sink_ids) >= 2:
            choice_entry = {
                "backend": choice_name,
                "node_id": node_id,
                "viable_sink_ids": viable_sink_ids,
                "scores": dict(compatibility["scores"]),
                "winner_sink_id": compatibility["winner_sink_id"],
                "winner_margin": compatibility["winner_margin"],
                "total_positive_flux": compatibility["total_positive_flux"],
                "epsilon_choice": epsilon_choice,
                "epsilon_collapse": epsilon_collapse,
            }
            next_registry[key] = choice_entry
            if previous_entry != choice_entry:
                emitted_events.append(
                    GRCEvent(
                        kind="choice_detected",
                        step_index=state.step_index,
                        source_family=source_family,
                        payload=dict(choice_entry),
                    )
                )
            continue

        if (
            previous_entry is not None
            and compatibility["winner_sink_id"] is not None
            and compatibility["winner_margin"] >= epsilon_collapse
        ):
            collapse_entry = {
                "backend": choice_name,
                "node_id": node_id,
                "collapsed_sink_id": compatibility["winner_sink_id"],
                "scores": dict(compatibility["scores"]),
                "winner_margin": compatibility["winner_margin"],
                "total_positive_flux": compatibility["total_positive_flux"],
                "previous_viable_sink_ids": list(previous_entry.get("viable_sink_ids", [])),
                "epsilon_choice": epsilon_choice,
                "epsilon_collapse": epsilon_collapse,
                "persistence_mode": "registry_and_basin_assignment",
                "collapsed_step_index": state.step_index,
            }
            collapse_registry[key] = collapse_entry
            _apply_learning_update(state, node_id=node_id, collapse_entry=collapse_entry)
            learning_updates[key] = {
                "node_id": node_id,
                "learned_basin_id": compatibility["winner_sink_id"],
                "source_event": "collapse",
                "step_index": state.step_index,
            }
            emitted_events.append(
                GRCEvent(
                    kind="collapse",
                    step_index=state.step_index,
                    source_family=source_family,
                    payload=dict(collapse_entry),
                )
            )
        elif previous_entry is not None:
            emitted_events.append(
                GRCEvent(
                    kind="choice_resolved",
                    step_index=state.step_index,
                    source_family=source_family,
                    payload={
                        "backend": choice_name,
                        "node_id": node_id,
                        "winner_sink_id": compatibility["winner_sink_id"],
                        "scores": dict(compatibility["scores"]),
                        "winner_margin": compatibility["winner_margin"],
                        "total_positive_flux": compatibility["total_positive_flux"],
                        "previous_viable_sink_ids": list(
                            previous_entry.get("viable_sink_ids", [])
                        ),
                        "epsilon_choice": epsilon_choice,
                        "epsilon_collapse": epsilon_collapse,
                        "resolution_mode": "single_sink_below_collapse_threshold",
                    },
                )
            )

    state.choice_registry = next_registry
    state.collapse_registry = collapse_registry
    state.cached_quantities["choice_state"] = {
        "backend": choice_name,
        "epsilon_choice": epsilon_choice,
        "epsilon_collapse": epsilon_collapse,
        "evaluated_nodes": evaluated_nodes,
    }
    state.cached_quantities["choice_learning_state"] = learning_updates
    return emitted_events


def apply_grc9v3_boundary_behavior(
    state: GRC9V3State,
    *,
    modes: Mapping[str, Any],
) -> None:
    """Apply configured boundary behavior for the baseline GRC9V3 runtime."""

    boundary_mode = str(modes.get("boundary_mode", "prune"))
    if boundary_mode == "prune":
        state.cached_quantities["boundary_behavior_mode"] = "prune_noop"
        return
    raise NotImplementedError(
        f"GRC9V3 boundary_mode {boundary_mode!r} requires boundary_barrier capability"
    )


def enforce_grc9v3_quadrature_budget(
    state: GRC9V3State,
    *,
    modes: Mapping[str, Any],
) -> dict[str, Any]:
    """Enforce B=sum_i mu_i C_i with baseline unit measure."""

    quadrature_mode = str(modes.get("quadrature_mode", "unit_measure"))
    if quadrature_mode != "unit_measure":
        raise NotImplementedError("GRC9V3 currently implements unit_measure quadrature only")
    method = str(modes.get("budget_correction_method", "simplex_projection"))
    live_node_ids = tuple(sorted(state.topology.iter_live_node_ids()))
    before = _budget(state)
    target = _ensure_budget_target(state)
    negative_mass_correction = 0.0
    for node_id in live_node_ids:
        node_state = state.nodes.get(node_id)
        if node_state is not None and node_state.coherence < 0.0:
            negative_mass_correction += -node_state.coherence
            _replace_node_coherence(state, node_id=node_id, coherence=0.0)

    after_clamp = _budget(state)
    if method == "uniform_shift":
        _apply_uniform_shift_budget(state, target=target, live_node_ids=live_node_ids)
    elif method == "simplex_projection":
        _apply_simplex_projection_budget(state, target=target, live_node_ids=live_node_ids)
    else:
        raise NotImplementedError(f"unsupported budget_correction_method {method!r}")

    after = _budget(state)
    budget_error = after - target
    state.remainder = 0.0 if abs(budget_error) <= 1e-12 else float(budget_error)
    summary = {
        "quadrature_mode": quadrature_mode,
        "budget_correction_method": method,
        "budget_before": before,
        "budget_after_negative_clamp": after_clamp,
        "budget_target": target,
        "budget_after": after,
        "budget_error": budget_error,
        "negative_mass_correction": negative_mass_correction,
    }
    state.cached_quantities["last_quadrature_budget"] = dict(summary)
    return summary


def refresh_grc9v3_coarse_cache(state: GRC9V3State) -> None:
    """Invalidate derived coarse summaries after value/topology changes."""

    cleared = bool(state.coarse_cache)
    state.coarse_cache.clear()
    state.cached_quantities["coarse_cache_refresh_mode"] = "invalidate_only"
    state.cached_quantities["coarse_cache_invalidated"] = bool(
        state.cached_quantities.get("coarse_cache_invalidated", False)
    ) or cleared
    state.cached_quantities["coarse_cache_invalidation_reason"] = "post_semantic_update"


def _choice_score_params(evolution: Mapping[str, Any]) -> dict[str, float]:
    raw_params = evolution.get("compatibility_score_params", {})
    if not isinstance(raw_params, Mapping):
        raise SnapshotCompatibilityError("compatibility_score_params must be a mapping")
    epsilon_choice = float(raw_params.get("epsilon_choice", 1e-3))
    epsilon_collapse = float(raw_params.get("epsilon_collapse", 1e-3))
    if epsilon_choice < 0.0:
        raise SnapshotCompatibilityError("epsilon_choice must be >= 0")
    if epsilon_collapse < 0.0:
        raise SnapshotCompatibilityError("epsilon_collapse must be >= 0")
    return {"epsilon_choice": epsilon_choice, "epsilon_collapse": epsilon_collapse}


def _successor_map_for_choice(state: GRC9V3State) -> dict[int, int | None]:
    raw_successor_map = state.cached_quantities.get("successor_map", {})
    if not isinstance(raw_successor_map, Mapping):
        raise SnapshotCompatibilityError(
            "GRC9V3 choice evaluation requires successor_map diagnostics"
        )
    successor_map: dict[int, int | None] = {}
    for node_id, successor in raw_successor_map.items():
        try:
            successor_map[int(node_id)] = None if successor is None else int(successor)
        except (TypeError, ValueError) as exc:
            raise SnapshotCompatibilityError(
                "successor_map keys and values must be int-compatible or null"
            ) from exc
    return successor_map


def _sink_compatibility_for_node(
    state: GRC9V3State,
    node_id: NodeId,
    *,
    successor_map: Mapping[int, int | None],
    sinks: set[int],
    epsilon_choice: float,
) -> dict[str, Any] | None:
    if node_id in sinks:
        return None

    flux_by_sink: dict[int, float] = {}
    total_positive_flux = 0.0
    for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
        edge = state.port_edges[edge_id]
        neighbor_id = edge.node_v if edge.node_u == node_id else edge.node_u
        outgoing_flux = _oriented_flux(edge, node_id=node_id)
        if outgoing_flux <= 0.0:
            continue
        sink_id = (
            neighbor_id
            if neighbor_id in sinks
            else _reachable_sink(neighbor_id, successor_map, sinks)
        )
        if sink_id is None:
            continue
        total_positive_flux += outgoing_flux
        flux_by_sink[sink_id] = flux_by_sink.get(sink_id, 0.0) + outgoing_flux

    if total_positive_flux <= 0.0 or not flux_by_sink:
        return None

    ordered_flux = sorted(flux_by_sink.items(), key=lambda item: (-item[1], item[0]))
    ordered_scores = [
        (str(sink_id), float(value / total_positive_flux))
        for sink_id, value in ordered_flux
    ]
    best_sink_id, best_score = ordered_scores[0]
    viable_sink_ids = [
        sink_id
        for sink_id, score in ordered_scores
        if best_score - score <= epsilon_choice
    ]
    second_best = ordered_scores[1][1] if len(ordered_scores) > 1 else 0.0
    return {
        "scores": {sink_id: score for sink_id, score in ordered_scores},
        "viable_sink_ids": viable_sink_ids,
        "winner_sink_id": best_sink_id,
        "winner_margin": float(best_score - second_best),
        "total_positive_flux": float(total_positive_flux),
    }


def _reachable_sink(
    origin_node_id: int,
    successor_map: Mapping[int, int | None],
    sinks: set[int],
) -> int | None:
    visited: set[int] = set()
    current = origin_node_id
    while current not in visited:
        visited.add(current)
        if current in sinks:
            return current
        next_node = successor_map.get(current)
        if next_node is None or next_node == current:
            return current if current in sinks else None
        current = next_node
    return None


def _oriented_flux(edge: Any, *, node_id: NodeId) -> float:
    if edge.node_u == node_id:
        return float(edge.flux_uv)
    if edge.node_v == node_id:
        return float(-edge.flux_uv)
    raise ValueError(f"edge is not incident to node {node_id}")


def _apply_learning_update(
    state: GRC9V3State,
    *,
    node_id: NodeId,
    collapse_entry: Mapping[str, Any],
) -> None:
    node_state = state.nodes.get(node_id)
    if node_state is None:
        return
    collapsed_sink_id = collapse_entry["collapsed_sink_id"]
    state.nodes[node_id] = GRC9V3NodeState(
        coherence=node_state.coherence,
        gradient_row_basis=list(node_state.gradient_row_basis),
        signed_hessian_row_basis=list(node_state.signed_hessian_row_basis),
        net_flux_summary=list(node_state.net_flux_summary),
        basin_mass=node_state.basin_mass,
        basin_id=collapsed_sink_id,
        parent_id=node_state.parent_id,
        depth=node_state.depth,
    )


def _ensure_budget_target(state: GRC9V3State) -> float:
    return float(state.budget_target)


def _budget(state: GRC9V3State) -> float:
    return float(sum(node_state.coherence for node_state in state.nodes.values()))


def _apply_uniform_shift_budget(
    state: GRC9V3State,
    *,
    target: float,
    live_node_ids: tuple[NodeId, ...],
) -> None:
    if not live_node_ids:
        state.remainder = target
        return
    correction = target - _budget(state)
    shift = correction / len(live_node_ids)
    for node_id in live_node_ids:
        node_state = state.nodes.get(node_id)
        if node_state is None:
            continue
        _replace_node_coherence(
            state,
            node_id=node_id,
            coherence=max(0.0, node_state.coherence + shift),
        )


def _apply_simplex_projection_budget(
    state: GRC9V3State,
    *,
    target: float,
    live_node_ids: tuple[NodeId, ...],
) -> None:
    if target < 0.0:
        raise SnapshotCompatibilityError("budget_target must be non-negative")
    if not live_node_ids:
        state.remainder = target
        return
    values = [float(state.nodes[node_id].coherence) for node_id in live_node_ids]
    projected = _project_to_simplex(values, target=target)
    for node_id, coherence in zip(live_node_ids, projected, strict=True):
        _replace_node_coherence(state, node_id=node_id, coherence=coherence)


def _project_to_simplex(values: list[float], *, target: float) -> list[float]:
    if not values:
        return []
    if target == 0.0:
        return [0.0 for _ in values]
    ordered = sorted(values, reverse=True)
    cumulative = 0.0
    rho = 0
    theta = 0.0
    for index, value in enumerate(ordered, start=1):
        cumulative += value
        candidate_theta = (cumulative - target) / index
        if value - candidate_theta > 0.0:
            rho = index
            theta = candidate_theta
    if rho == 0:
        theta = (sum(ordered) - target) / len(ordered)
    return [max(0.0, value - theta) for value in values]


def _replace_node_coherence(
    state: GRC9V3State,
    *,
    node_id: NodeId,
    coherence: float,
) -> None:
    node_state = state.nodes[node_id]
    state.nodes[node_id] = GRC9V3NodeState(
        coherence=float(coherence),
        gradient_row_basis=list(node_state.gradient_row_basis),
        signed_hessian_row_basis=list(node_state.signed_hessian_row_basis),
        net_flux_summary=list(node_state.net_flux_summary),
        basin_mass=node_state.basin_mass,
        basin_id=node_state.basin_id,
        parent_id=node_state.parent_id,
        depth=node_state.depth,
    )


__all__ = [
    "apply_grc9v3_boundary_behavior",
    "enforce_grc9v3_quadrature_budget",
    "rebuild_grc9v3_choice_state",
    "refresh_grc9v3_coarse_cache",
]

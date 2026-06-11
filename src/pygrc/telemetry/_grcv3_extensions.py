"""Private GRCV3 telemetry extension builders."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygrc.core import BACKEND_SELECTIONS_KEY, GRCParams, StepResult
from pygrc.models import GRCV3
from pygrc.models.grc_v3_differential import symmetric_eigenvalues

from .grcv3_contract import (
    GRCV3BackendTelemetry,
    GRCV3BasinSummary,
    GRCV3ChoiceStateSummary,
    GRCV3EventAlignedLandscapeObservation,
    GRCV3FrontierBirthStateSummary,
    GRCV3HierarchySummary,
    GRCV3LifecycleEventCounts,
    GRCV3ObservedInteriorSite,
    GRCV3RunSummaryExtension,
    GRCV3SignedHessianTelemetry,
    GRCV3SparkStateSummary,
    GRCV3StepTelemetryExtension,
    GRCV3TransientLandscapePrimitiveSummary,
    GRCV3TransientLandscapeRunSummary,
    GRCV3TransientLandscapeStepSummary,
)
from ._telemetry_utils import _vector_norm


def _build_grcv3_backend_summary(params: GRCParams) -> GRCV3BackendTelemetry:
    backend_payload = dict(params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY])
    return GRCV3BackendTelemetry(
        geometry_backend=str(dict(backend_payload["geometry"])["name"]),
        differential_backend=str(dict(backend_payload["differential_summary"])["name"]),
        metric_backend=str(dict(backend_payload["metric"])["name"]),
        spark_backend=str(dict(backend_payload["spark"])["name"]),
        hierarchy_backend=str(dict(backend_payload["hierarchy_update"])["name"]),
        choice_backend=str(dict(backend_payload["choice"])["name"]),
    )


def _build_grcv3_step_extension(
    model: GRCV3,
    transient_landscape: GRCV3TransientLandscapeStepSummary | None = None,
) -> GRCV3StepTelemetryExtension:
    return GRCV3StepTelemetryExtension(
        backend_summary=_build_grcv3_backend_summary(model.get_params()),
        signed_hessian=_build_grcv3_signed_hessian(model),
        basin_summary=_build_grcv3_basin_summary(model),
        spark_state=_build_grcv3_spark_state(model),
        hierarchy_state=_build_grcv3_hierarchy_state(model),
        choice_state=_build_grcv3_choice_state(model),
        frontier_birth_state=_build_grcv3_frontier_birth_state(model),
        transient_landscape=transient_landscape,
    )


def _build_grcv3_run_summary_extension(
    model: GRCV3,
    step_results: list[StepResult] | tuple[StepResult, ...],
    *,
    transient_landscape: GRCV3TransientLandscapeRunSummary | None = None,
) -> GRCV3RunSummaryExtension:
    return GRCV3RunSummaryExtension(
        backend_summary=_build_grcv3_backend_summary(model.get_params()),
        signed_hessian=_build_grcv3_signed_hessian(model),
        final_basin_summary=_build_grcv3_basin_summary(model),
        final_spark_state=_build_grcv3_spark_state(model),
        final_hierarchy_state=_build_grcv3_hierarchy_state(model),
        final_choice_state=_build_grcv3_choice_state(model),
        frontier_birth_summary=_build_grcv3_frontier_birth_run_summary(
            model,
            step_results,
        ),
        lifecycle_event_counts=_build_grcv3_lifecycle_event_counts(step_results),
        transient_landscape=transient_landscape,
    )


def _build_grcv3_signed_hessian(model: GRCV3) -> GRCV3SignedHessianTelemetry:
    hessian_sign = model.get_state().cached_quantities.get("hessian_sign")
    if hessian_sign not in (-1, 1):
        raise ValueError("GRCV3 telemetry requires a calibrated hessian_sign")
    return GRCV3SignedHessianTelemetry(hessian_sign=int(hessian_sign))


_LANDSCAPE_MONITORING_SURFACE_PRIORITY: tuple[tuple[str, str, str], ...] = (
    (
        "transfer_mediation",
        "landscape_grcv3_transfer_mediation_summary",
        "transfer_mediation_primitive_ids",
    ),
    (
        "interior_load_carriers",
        "landscape_grcv3_interior_load_carrier_summary",
        "interior_load_carrier_primitive_ids",
    ),
    (
        "interior_partition",
        "landscape_grcv3_interior_partition_summary",
        "interior_partition_primitive_ids",
    ),
    (
        "interior_geometry",
        "landscape_grcv3_interior_geometry_summary",
        "interior_geometry_primitive_ids",
    ),
)


def _coerce_runtime_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _landscape_monitoring_context(
    model: GRCV3,
) -> tuple[str, tuple[str, ...], Mapping[str, Mapping[str, Any]]] | None:
    state = model.get_state()
    runtime_summary = state.cached_quantities.get("landscape_runtime_assembly_summary")
    if not isinstance(runtime_summary, Mapping):
        return None
    for surface_kind, summary_key, primitive_ids_key in _LANDSCAPE_MONITORING_SURFACE_PRIORITY:
        primitive_ids_value = runtime_summary.get(primitive_ids_key)
        if not isinstance(primitive_ids_value, list | tuple):
            continue
        primitive_ids = tuple(str(value) for value in primitive_ids_value if value is not None)
        if not primitive_ids:
            continue
        surface_summary_raw = state.cached_quantities.get(summary_key, {})
        surface_summary = (
            {
                str(primitive_id): dict(summary)
                for primitive_id, summary in surface_summary_raw.items()
            }
            if isinstance(surface_summary_raw, Mapping)
            else {}
        )
        return surface_kind, primitive_ids, surface_summary
    return None


def _monitored_landscape_node_id(model: GRCV3, primitive_id: str) -> int | None:
    state = model.get_state()
    node_id_by_primitive_id = state.cached_quantities.get(
        "landscape_node_id_by_primitive_id", {}
    )
    if not isinstance(node_id_by_primitive_id, Mapping):
        return None
    node_id = _coerce_runtime_int(node_id_by_primitive_id.get(primitive_id))
    if node_id is None or node_id not in state.nodes:
        return None
    return node_id


def _signed_hessian_eigenvalues(
    model: GRCV3,
    *,
    node_id: int,
) -> list[float]:
    state = model.get_state()
    hessian_sign = state.cached_quantities.get("hessian_sign")
    if hessian_sign not in (-1, 1):
        return []
    attributes = state.nodes[node_id]
    signed_hessian = [
        [float(hessian_sign) * float(value) for value in row]
        for row in attributes.hessian
    ]
    if not signed_hessian:
        return []
    return symmetric_eigenvalues(signed_hessian)


def _build_grcv3_observed_interior_site(
    model: GRCV3,
    *,
    primitive_id: str,
) -> GRCV3ObservedInteriorSite | None:
    node_id = _monitored_landscape_node_id(model, primitive_id)
    if node_id is None:
        return None
    state = model.get_state()
    attributes = state.nodes[node_id]
    gradient_norm = _vector_norm(attributes.gradient)
    ordered_eigenvalues = sorted(_signed_hessian_eigenvalues(model, node_id=node_id))
    weak_mode_signed_curvature = ordered_eigenvalues[0] if ordered_eigenvalues else None
    min_signed_eigenvalue = ordered_eigenvalues[0] if ordered_eigenvalues else None
    max_signed_eigenvalue = ordered_eigenvalues[-1] if ordered_eigenvalues else None
    eps_gradient = float(model.get_params().evolution["eps_gradient"])
    eps_hessian = float(model.get_params().evolution["eps_hessian"])
    eps_spark = float(model.get_params().evolution["eps_spark"])
    gradient_gate_pass = gradient_norm < eps_gradient
    geometric_validation_pass = (
        gradient_gate_pass
        and min_signed_eigenvalue is not None
        and min_signed_eigenvalue > eps_hessian
    )
    spark_candidate_regime = (
        gradient_gate_pass
        and min_signed_eigenvalue is not None
        and min_signed_eigenvalue < eps_spark
        and not any(value <= eps_hessian for value in ordered_eigenvalues[1:])
    )
    return GRCV3ObservedInteriorSite(
        primitive_id=primitive_id,
        node_id=node_id,
        gradient_norm=float(gradient_norm),
        min_signed_eigenvalue=min_signed_eigenvalue,
        max_signed_eigenvalue=max_signed_eigenvalue,
        weak_mode_signed_curvature=weak_mode_signed_curvature,
        gradient_gate_pass=gradient_gate_pass,
        geometric_validation_pass=geometric_validation_pass,
        spark_candidate_regime=spark_candidate_regime,
    )


def _build_grcv3_landscape_step_observability(
    model: GRCV3,
) -> GRCV3TransientLandscapeStepSummary | None:
    context = _landscape_monitoring_context(model)
    if context is None:
        return None
    surface_kind, primitive_ids, _surface_summary = context
    observed_sites = tuple(
        site
        for primitive_id in primitive_ids
        if (site := _build_grcv3_observed_interior_site(model, primitive_id=primitive_id))
        is not None
    )
    if not observed_sites:
        return None
    return GRCV3TransientLandscapeStepSummary(
        monitoring_surface_kind=surface_kind,
        observed_sites=observed_sites,
    )


def _event_matches_observed_site(
    event: Any,
    site: GRCV3ObservedInteriorSite,
) -> bool:
    payload = event.payload if isinstance(getattr(event, "payload", None), Mapping) else {}
    event_node_id = _coerce_runtime_int(payload.get("node_id", payload.get("parent_node_id")))
    if event_node_id == site.node_id:
        return True
    event_basin_id = payload.get("basin_id", payload.get("parent_basin_id"))
    return event_basin_id == site.primitive_id


def _first_matching_event_step(
    *,
    event_kind: str,
    primitive_id: str,
    node_id: int,
    step_results: list[StepResult] | tuple[StepResult, ...],
) -> int | None:
    observed_site = GRCV3ObservedInteriorSite(
        primitive_id=primitive_id,
        node_id=node_id,
        gradient_norm=0.0,
    )
    for step_result in step_results:
        for event in step_result.events:
            if event.kind != event_kind:
                continue
            if _event_matches_observed_site(event, observed_site):
                return int(step_result.step_index)
    return None


def _build_grcv3_landscape_run_summary(
    model: GRCV3,
    *,
    initial_observability: GRCV3TransientLandscapeStepSummary | None,
    step_observability: tuple[GRCV3TransientLandscapeStepSummary | None, ...],
    step_results: list[StepResult] | tuple[StepResult, ...],
) -> GRCV3TransientLandscapeRunSummary | None:
    if initial_observability is None:
        return None
    context = _landscape_monitoring_context(model)
    if context is None:
        return None
    surface_kind, primitive_ids, surface_summary = context
    global_first_event_steps = {
        event_kind: next(
            (
                int(step_result.step_index)
                for step_result in step_results
                if any(event.kind == event_kind for event in step_result.events)
            ),
            None,
        )
        for event_kind in ("spark_candidate", "spark", "split_init", "split_complete")
    }

    observations_by_primitive: dict[str, list[tuple[int, GRCV3ObservedInteriorSite]]] = {}
    for site in initial_observability.observed_sites:
        observations_by_primitive.setdefault(site.primitive_id, []).append((0, site))
    for step_result, transient in zip(step_results, step_observability, strict=False):
        if transient is None:
            continue
        for site in transient.observed_sites:
            observations_by_primitive.setdefault(site.primitive_id, []).append(
                (int(step_result.step_index), site)
            )

    primitive_summaries: list[GRCV3TransientLandscapePrimitiveSummary] = []
    monitored_node_ids_by_primitive_id: dict[str, int] = {}
    for primitive_id in primitive_ids:
        series = observations_by_primitive.get(primitive_id, [])
        if not series:
            continue
        node_id = series[-1][1].node_id
        monitored_node_ids_by_primitive_id[primitive_id] = node_id
        gradient_values = [site.gradient_norm for _, site in series]
        weak_values = [
            site.weak_mode_signed_curvature
            for _, site in series
            if site.weak_mode_signed_curvature is not None
        ]
        min_signed_values = [
            site.min_signed_eigenvalue
            for _, site in series
            if site.min_signed_eigenvalue is not None
        ]
        first_spark_candidate_step = _first_matching_event_step(
            event_kind="spark_candidate",
            primitive_id=primitive_id,
            node_id=node_id,
            step_results=step_results,
        )
        first_spark_step = _first_matching_event_step(
            event_kind="spark",
            primitive_id=primitive_id,
            node_id=node_id,
            step_results=step_results,
        )
        first_split_init_step = _first_matching_event_step(
            event_kind="split_init",
            primitive_id=primitive_id,
            node_id=node_id,
            step_results=step_results,
        )
        if len(primitive_ids) == 1:
            if first_spark_candidate_step is None:
                first_spark_candidate_step = global_first_event_steps["spark_candidate"]
            if first_spark_step is None:
                first_spark_step = global_first_event_steps["spark"]
            if first_split_init_step is None:
                first_split_init_step = global_first_event_steps["split_init"]
        primitive_summaries.append(
            GRCV3TransientLandscapePrimitiveSummary(
                primitive_id=primitive_id,
                node_id=node_id,
                initial_gradient_norm=series[0][1].gradient_norm,
                min_gradient_norm=min(gradient_values),
                final_gradient_norm=series[-1][1].gradient_norm,
                initial_weak_mode_signed_curvature=series[0][1].weak_mode_signed_curvature,
                min_weak_mode_signed_curvature=(min(weak_values) if weak_values else None),
                final_weak_mode_signed_curvature=series[-1][1].weak_mode_signed_curvature,
                initial_min_signed_eigenvalue=series[0][1].min_signed_eigenvalue,
                min_signed_eigenvalue=(min(min_signed_values) if min_signed_values else None),
                final_min_signed_eigenvalue=series[-1][1].min_signed_eigenvalue,
                first_gradient_gate_pass_step=next(
                    (step_index for step_index, site in series if site.gradient_gate_pass),
                    None,
                ),
                first_geometric_validation_step=next(
                    (
                        step_index
                        for step_index, site in series
                        if site.geometric_validation_pass
                    ),
                    None,
                ),
                first_spark_candidate_step=first_spark_candidate_step,
                first_spark_step=first_spark_step,
                first_split_init_step=first_split_init_step,
            )
        )

    if not primitive_summaries:
        return None

    event_aligned_observations: list[GRCV3EventAlignedLandscapeObservation] = []
    recorded_event_kinds: set[str] = set()
    for step_result, transient in zip(step_results, step_observability, strict=False):
        if transient is None:
            continue
        event_kinds = {event.kind for event in step_result.events}
        for event_kind in ("spark_candidate", "spark", "split_init", "split_complete"):
            if event_kind not in event_kinds or event_kind in recorded_event_kinds:
                continue
            event_aligned_observations.append(
                GRCV3EventAlignedLandscapeObservation(
                    event_kind=event_kind,
                    step_index=int(step_result.step_index),
                    observed_sites=transient.observed_sites,
                )
            )
            recorded_event_kinds.add(event_kind)

    return GRCV3TransientLandscapeRunSummary(
        monitoring_surface_kind=surface_kind,
        monitored_node_ids_by_primitive_id=monitored_node_ids_by_primitive_id,
        surface_realization_summary=surface_summary,
        primitive_summaries=tuple(primitive_summaries),
        event_aligned_observations=tuple(event_aligned_observations),
    )


def _build_grcv3_basin_summary(model: GRCV3) -> GRCV3BasinSummary:
    """Summarize the currently materialized basin surface.

    `active_basin_count` prefers the explicit runtime basin map, then falls back
    to validated geometric basin ids, and only finally to hierarchy nodes as a
    coarse proxy when neither basin surface has been materialized yet.
    """

    state = model.get_state()
    geometric_identity = state.cached_quantities.get("geometric_identity", {})
    seed_nodes = (
        geometric_identity.get("seed_nodes", [])
        if isinstance(geometric_identity, dict)
        else []
    )
    validated_basin_ids = (
        geometric_identity.get("validated_basin_ids", [])
        if isinstance(geometric_identity, dict)
        else []
    )
    active_basin_count = len(state.basins)
    if active_basin_count == 0:
        active_basin_count = len(validated_basin_ids)
    if active_basin_count == 0:
        active_basin_count = len(state.hierarchy)
    return GRCV3BasinSummary(
        attributed_node_count=len(state.nodes),
        active_basin_count=active_basin_count,
        geometric_seed_count=len(seed_nodes),
        geometric_validated_basin_count=len(validated_basin_ids),
        max_hierarchy_depth=max(
            (attributes.depth for attributes in state.nodes.values()),
            default=0,
        ),
    )


def _build_grcv3_spark_state(model: GRCV3) -> GRCV3SparkStateSummary:
    state = model.get_state()
    split_registry_raw = state.cached_quantities.get("split_registry", {})
    split_registry = split_registry_raw if isinstance(split_registry_raw, dict) else {}
    active_split_count = 0
    confirmed_split_count = 0
    pending_spark_count = 0
    for entry in split_registry.values():
        if not isinstance(entry, dict):
            continue
        complete = bool(entry.get("complete", False))
        spark_confirmed = bool(entry.get("spark_confirmed", False))
        if not complete:
            active_split_count += 1
        if spark_confirmed:
            confirmed_split_count += 1
        if not spark_confirmed and not complete:
            pending_spark_count += 1
    return GRCV3SparkStateSummary(
        split_registry_size=len(split_registry),
        active_split_count=active_split_count,
        confirmed_split_count=confirmed_split_count,
        pending_spark_count=pending_spark_count,
    )


def _build_grcv3_hierarchy_state(model: GRCV3) -> GRCV3HierarchySummary:
    state = model.get_state()
    hierarchy_roots = state.cached_quantities.get("hierarchy_roots", [])
    root_count = len(hierarchy_roots) if isinstance(hierarchy_roots, list | tuple | set) else 0
    child_link_count = sum(len(children) for children in state.hierarchy.values())
    return GRCV3HierarchySummary(
        hierarchy_root_count=root_count,
        hierarchy_node_count=len(state.hierarchy),
        child_basin_link_count=child_link_count,
    )


def _build_grcv3_choice_state(model: GRCV3) -> GRCV3ChoiceStateSummary:
    state = model.get_state()
    choice_state = state.cached_quantities.get("choice_state", {})
    evaluated_nodes = (
        choice_state.get("evaluated_nodes", {})
        if isinstance(choice_state, dict)
        else {}
    )
    return GRCV3ChoiceStateSummary(
        choice_regime_count=len(state.choice_registry),
        collapse_registry_count=len(state.collapse_registry),
        evaluated_node_count=len(evaluated_nodes) if isinstance(evaluated_nodes, dict) else 0,
    )


def _frontier_birth_candidates_by_node(model: GRCV3) -> dict[int, dict[str, Any]]:
    state = model.get_state()
    candidates: dict[int, dict[str, Any]] = {}
    raw_candidates = state.cached_quantities.get("grcv3_frontier_birth_candidates", {})
    if isinstance(raw_candidates, Mapping):
        for node_id, candidate_raw in raw_candidates.items():
            runtime_node_id = _coerce_runtime_int(node_id)
            if runtime_node_id is None:
                continue
            if candidate_raw is True:
                candidate = {"frontier_source": "active_frontier"}
            elif isinstance(candidate_raw, Mapping):
                if not bool(candidate_raw.get("enabled", True)):
                    continue
                candidate = dict(candidate_raw)
            else:
                continue
            candidate.setdefault("frontier_source", "active_frontier")
            candidates[runtime_node_id] = candidate
    raw_active = state.cached_quantities.get("grcv3_active_frontier_node_ids", ())
    if isinstance(raw_active, list | tuple | set | frozenset):
        for node_id in raw_active:
            runtime_node_id = _coerce_runtime_int(node_id)
            if runtime_node_id is not None:
                candidates.setdefault(runtime_node_id, {"frontier_source": "active_frontier"})
    raw_pressure = state.cached_quantities.get(
        "grcv3_pressure_boundary_frontier_node_ids",
        (),
    )
    if isinstance(raw_pressure, list | tuple | set | frozenset):
        for node_id in raw_pressure:
            runtime_node_id = _coerce_runtime_int(node_id)
            if runtime_node_id is not None:
                candidates.setdefault(
                    runtime_node_id,
                    {"frontier_source": "pressure_boundary"},
                )
    live_node_ids = set(state.topology.iter_live_node_ids())
    return {
        node_id: candidate
        for node_id, candidate in sorted(candidates.items())
        if node_id in live_node_ids
    }


def _summary_stats(values: list[float]) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)


def _build_frontier_birth_summary_from_events(
    *,
    mode: str,
    rule: str,
    candidates: Mapping[int, Mapping[str, Any]],
    events: list[Mapping[str, Any]],
) -> GRCV3FrontierBirthStateSummary:
    sources = tuple(
        sorted(
            {
                str(event.get("frontier_source"))
                for event in events
                if event.get("frontier_source") not in (None, "")
            }
        )
    )
    outward_values = [
        float(event["outward_flux_pressure"])
        for event in events
        if isinstance(event.get("outward_flux_pressure"), int | float)
        and not isinstance(event.get("outward_flux_pressure"), bool)
    ]
    probability_values = [
        float(event["birth_probability"])
        for event in events
        if isinstance(event.get("birth_probability"), int | float)
        and not isinstance(event.get("birth_probability"), bool)
    ]
    outward_min, outward_max, outward_mean = _summary_stats(outward_values)
    probability_min, probability_max, probability_mean = _summary_stats(probability_values)
    pressure_candidate_count = sum(
        1
        for candidate in candidates.values()
        if str(candidate.get("frontier_source", "")) == "pressure_boundary"
    )
    pressure_birth_count = sum(
        1
        for event in events
        if str(event.get("frontier_source", "")) == "pressure_boundary"
    )
    return GRCV3FrontierBirthStateSummary(
        frontier_birth_mode=mode,
        frontier_birth_rule=rule,
        frontier_candidate_count=len(candidates),
        pressure_boundary_candidate_count=pressure_candidate_count,
        frontier_birth_count=len(events),
        pressure_boundary_birth_count=pressure_birth_count,
        frontier_sources_observed=sources,
        outward_flux_pressure_min=outward_min,
        outward_flux_pressure_max=outward_max,
        outward_flux_pressure_mean=outward_mean,
        birth_probability_min=probability_min,
        birth_probability_max=probability_max,
        birth_probability_mean=probability_mean,
    )


def _build_grcv3_frontier_birth_state(model: GRCV3) -> GRCV3FrontierBirthStateSummary:
    state = model.get_state()
    mode = str(
        model.get_params().constitutive_semantic_modes.get(
            "frontier_birth_mode",
            "disabled",
        )
    )
    rule = str(
        state.cached_quantities.get(
            "frontier_birth_rule_mode",
            "disabled" if mode == "disabled" else "bernoulli_outward_flux_pressure",
        )
    )
    last_events_raw = state.cached_quantities.get("last_frontier_birth_events", [])
    events = [
        dict(event)
        for event in last_events_raw
        if isinstance(event, Mapping)
    ] if isinstance(last_events_raw, list | tuple) else []
    return _build_frontier_birth_summary_from_events(
        mode=mode,
        rule=rule,
        candidates=_frontier_birth_candidates_by_node(model),
        events=events,
    )


def _build_grcv3_frontier_birth_run_summary(
    model: GRCV3,
    step_results: list[StepResult] | tuple[StepResult, ...],
) -> GRCV3FrontierBirthStateSummary:
    mode = str(
        model.get_params().constitutive_semantic_modes.get(
            "frontier_birth_mode",
            "disabled",
        )
    )
    rule = (
        "disabled" if mode == "disabled" else "bernoulli_outward_flux_pressure"
    )
    events = [
        dict(event.payload)
        for step_result in step_results
        for event in step_result.events
        if event.kind == "frontier_birth" and isinstance(event.payload, Mapping)
    ]
    return _build_frontier_birth_summary_from_events(
        mode=mode,
        rule=rule,
        candidates=_frontier_birth_candidates_by_node(model),
        events=events,
    )


def _build_grcv3_lifecycle_event_counts(
    step_results: list[StepResult] | tuple[StepResult, ...],
) -> GRCV3LifecycleEventCounts:
    counts = {
        "spark_candidate": 0,
        "spark_pending": 0,
        "spark": 0,
        "split_init": 0,
        "split_progress": 0,
        "split_complete": 0,
        "choice_detected": 0,
        "choice_resolved": 0,
        "collapse": 0,
        "frontier_birth": 0,
    }
    for step_result in step_results:
        for event in step_result.events:
            if event.kind in counts:
                counts[event.kind] += 1
    return GRCV3LifecycleEventCounts(
        spark_candidate_count=counts["spark_candidate"],
        spark_pending_count=counts["spark_pending"],
        spark_confirmed_count=counts["spark"],
        split_init_count=counts["split_init"],
        split_progress_count=counts["split_progress"],
        split_complete_count=counts["split_complete"],
        choice_detected_count=counts["choice_detected"],
        choice_resolved_count=counts["choice_resolved"],
        collapse_count=counts["collapse"],
        frontier_birth_count=counts["frontier_birth"],
    )

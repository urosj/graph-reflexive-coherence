"""Private GRC9 telemetry extension builders."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from itertools import combinations
import math
from typing import Any

from pygrc.core import GRCEvent, GRCParams, StepResult
from pygrc.models import GRC9
from pygrc.models.grc_9_expansion import compute_expansion_node_count
from pygrc.models.grc_9_ports import port_to_rc, slot_to_port_id

from .grc9_contract import (
    GRC9_ABUNDANCE_CONTRACT,
    GRC9BackendConfigTelemetry,
    GRC9BudgetCorrectionSummary,
    GRC9CoarseGrainingSummary,
    GRC9ColumnDiagnosticSummary,
    GRC9EventTelemetryExtension,
    GRC9ExpansionSummary,
    GRC9GrowthSummary,
    GRC9IdentityAbundanceSummary,
    GRC9LabelAvailability,
    GRC9LaneContext,
    GRC9LifecycleEventCounts,
    GRC9PortChartSummary,
    GRC9RowTensorSummary,
    GRC9CalibrationSummary,
    GRC9RunSummaryExtension,
    GRC9SparkCalibrationTelemetry,
    GRC9StepTelemetryExtension,
    GRC9TransportSummary,
    classify_grc9_event_extension,
)


_CONTRACT_SOURCE_REFERENCE = "implementation/Phase-T-GRC9-TelemetryContract.md"
_BUDGET_POLICY = "uniform_shift_with_positive_fallback"
_SUPPORTED_COARSE_FIELDS = (
    "conductance",
    "geometric_length",
    "temporal_delay",
    "flux_coupling",
    "abs_flux",
    "signed_flux",
)


def _build_grc9_backend_config(params: GRCParams) -> GRC9BackendConfigTelemetry:
    modes = params.constitutive_semantic_modes
    evolution = params.evolution
    expansion_substeps = _coerce_non_negative_int(
        evolution.get("adiabatic_expansion_substeps", 1)
    )
    expansion_schedule = (
        "adiabatic" if expansion_substeps is not None and expansion_substeps > 1 else "instantaneous"
    )
    edge_label_selection = modes.get("edge_label_selection", "all")
    if isinstance(edge_label_selection, str):
        edge_label_selection_payload = edge_label_selection
    elif isinstance(edge_label_selection, Sequence):
        edge_label_selection_payload = ",".join(str(value) for value in edge_label_selection)
    else:
        edge_label_selection_payload = str(edge_label_selection)

    return GRC9BackendConfigTelemetry(
        frame_mode=str(modes.get("frame_mode", "fixed_port_chart")),
        curvature_backend=str(modes.get("curvature_backend", "none")),
        metric_backend="tensor_exponential_conductance_update",
        spark_backend="saturation_instability_column_proxy_sign_crossing",
        birth_backend="outward_flux_bernoulli_growth",
        growth_parent_eligibility_mode=str(
            modes.get("growth_parent_eligibility", "legacy_any_inactive_port")
        ),
        coarse_graining_backend="exact_column_profile_with_signed_flux_split",
        boundary_mode=str(modes.get("boundary_mode", "prune")),
        budget_preservation_policy=_BUDGET_POLICY,
        expansion_distribution_mode=str(modes.get("expansion_distribution_mode", "equal")),
        expansion_schedule=expansion_schedule,
        expansion_schedule_tau=(
            expansion_substeps
            if expansion_substeps is not None and expansion_substeps > 1
            else None
        ),
        edge_label_selection=edge_label_selection_payload,
    )


def _build_grc9_step_extension(
    model: GRC9,
    *,
    lane_context: GRC9LaneContext | None = None,
) -> GRC9StepTelemetryExtension:
    state = model.get_state()
    params = model.get_params()
    resolved_lane_context = lane_context or GRC9LaneContext(
        source_reference=_CONTRACT_SOURCE_REFERENCE
    )
    return GRC9StepTelemetryExtension(
        lane_context=resolved_lane_context,
        backend_config=_build_grc9_backend_config(params),
        port_chart=_build_grc9_port_chart(model),
        row_tensor=_build_grc9_row_tensor(model),
        column_diagnostic=_build_grc9_column_diagnostic(model),
        transport=_build_grc9_transport(model),
        identity_abundance=_build_grc9_identity_abundance(model),
        coarse_graining=_build_grc9_coarse_graining(model),
        budget_correction=_build_grc9_budget_correction(model),
    )


def _build_grc9_event_extension(
    model: GRC9,
    event: GRCEvent,
    *,
    lane_context: GRC9LaneContext | None = None,
) -> GRC9EventTelemetryExtension:
    payload = dict(event.payload)
    if event.kind == "spark":
        payload.update(_grc9_spark_event_context(model, payload))
    elif event.kind == "expansion":
        payload.update(_grc9_expansion_event_context(model, payload))
    elif event.kind == "growth":
        payload.update(_grc9_growth_event_context(model, payload))
    elif event.kind == "budget_correction":
        payload.setdefault("budget_preservation_policy", _BUDGET_POLICY)
    return classify_grc9_event_extension(
        event.kind,
        payload,
        lane_context=lane_context,
    )


def _build_grc9_run_summary_extension(
    model: GRC9,
    step_results: Sequence[StepResult],
    *,
    lane_context: GRC9LaneContext | None = None,
    identity_fission_observations: Sequence[Mapping[str, Any]] | None = None,
    identity_fission_persistence_delta: int | None = None,
    identity_fission_min_basin_mass: float | None = None,
) -> GRC9RunSummaryExtension:
    resolved_lane_context = lane_context or GRC9LaneContext(
        source_reference=_CONTRACT_SOURCE_REFERENCE
    )
    final_step_extension = _build_grc9_step_extension(
        model,
        lane_context=resolved_lane_context,
    )
    fission_evaluation = None
    if identity_fission_observations is not None:
        fission_evaluation = _evaluate_grc9_identity_fission_persistence(
            identity_fission_observations,
            delta=_resolve_identity_fission_delta(
                model,
                identity_fission_persistence_delta,
            ),
            min_basin_mass=_resolve_identity_fission_min_basin_mass(
                model,
                identity_fission_min_basin_mass,
            ),
        )
    return GRC9RunSummaryExtension(
        lane_context=resolved_lane_context,
        backend_summary=final_step_extension.backend_config,
        final_port_chart_summary=final_step_extension.port_chart,
        final_row_tensor_summary=final_step_extension.row_tensor,
        final_column_diagnostic_summary=final_step_extension.column_diagnostic,
        final_transport_summary=final_step_extension.transport,
        final_identity_summary=final_step_extension.identity_abundance,
        final_coarse_graining_summary=final_step_extension.coarse_graining,
        lifecycle_event_counts=_build_grc9_lifecycle_event_counts(step_results),
        expansion_summary=_build_grc9_expansion_summary(
            model,
            step_results,
            fission_evaluation=fission_evaluation,
        ),
        growth_summary=_build_grc9_growth_summary(step_results),
        calibration_summary=_build_grc9_calibration_summary(model, step_results),
        diagnostic_status_summary={
            "identity_fission_confirmed": (
                "artifact_backed"
                if fission_evaluation is not None
                or _coerce_non_negative_int(
                    model.get_state().cached_quantities.get(
                        "identity_fission_confirmed_count"
                    )
                )
                is not None
                else "reserved_future"
            )
        },
    )


def _build_grc9_lifecycle_event_counts(
    step_results: Sequence[StepResult],
) -> GRC9LifecycleEventCounts:
    spark_confirmed_count = 0
    spark_instability_count = 0
    spark_column_proxy_count = 0
    spark_sign_crossing_count = 0
    expansion_count = 0
    growth_count = 0
    coarse_cache_invalidation_count = 0
    budget_correction_count = 0
    budget_uniform_correction_count = 0
    budget_simplex_correction_count = 0

    for event in _iter_step_events(step_results):
        if event.kind == "spark":
            spark_confirmed_count += 1
            spark_kind = str(event.payload.get("spark_kind", ""))
            if spark_kind == "saturation_instability":
                spark_instability_count += 1
            elif spark_kind == "saturation_column_proxy":
                spark_column_proxy_count += 1
            elif spark_kind == "saturation_sign_crossing":
                spark_sign_crossing_count += 1
        elif event.kind == "expansion":
            expansion_count += 1
        elif event.kind == "growth":
            growth_count += 1
        elif event.kind == "coarse_cache_invalidation":
            coarse_cache_invalidation_count += 1
        elif event.kind == "budget_correction":
            budget_correction_count += 1
            correction_path = str(event.payload.get("correction_path", ""))
            simplex_applied = bool(event.payload.get("simplex_projection_applied", False))
            if simplex_applied or "simplex" in correction_path or "projection" in correction_path:
                budget_simplex_correction_count += 1
            elif "uniform" in correction_path:
                budget_uniform_correction_count += 1

    return GRC9LifecycleEventCounts(
        spark_candidate_count=spark_confirmed_count,
        spark_confirmed_count=spark_confirmed_count,
        spark_instability_count=spark_instability_count,
        spark_column_proxy_count=spark_column_proxy_count,
        spark_sign_crossing_count=spark_sign_crossing_count,
        expansion_count=expansion_count,
        growth_count=growth_count,
        coarse_cache_invalidation_count=coarse_cache_invalidation_count,
        budget_correction_count=budget_correction_count,
        budget_uniform_correction_count=budget_uniform_correction_count,
        budget_simplex_correction_count=budget_simplex_correction_count,
    )


def _build_grc9_expansion_summary(
    model: GRC9,
    step_results: Sequence[StepResult],
    *,
    fission_evaluation: Mapping[str, int | float] | None = None,
) -> GRC9ExpansionSummary:
    state = model.get_state()
    module_sizes = [
        len(record.module_node_ids)
        for _, record in sorted(state.expansion_registry.items())
    ]
    total_boundary_reassignments = 0
    for event in _iter_step_events(step_results):
        if event.kind != "expansion":
            continue
        reassignment_map = event.payload.get("reassignment_map", {})
        if isinstance(reassignment_map, Mapping):
            total_boundary_reassignments += len(reassignment_map)
    if fission_evaluation is not None:
        confirmed_count = _coerce_non_negative_int(
            fission_evaluation.get("identity_fission_confirmed_count")
        )
        persistence_steps = _coerce_non_negative_int(
            fission_evaluation.get("identity_fission_max_persistence_steps")
        )
    else:
        confirmed_count = _coerce_non_negative_int(
            state.cached_quantities.get("identity_fission_confirmed_count")
        )
        persistence_steps = _coerce_non_negative_int(
            state.cached_quantities.get("identity_fission_max_persistence_steps")
        )
    return GRC9ExpansionSummary(
        final_expansion_registry_size=len(state.expansion_registry),
        total_module_nodes_created=sum(module_sizes),
        total_boundary_reassignments=total_boundary_reassignments,
        max_module_node_count=int(_maximum(module_sizes)),
        identity_fission_candidate_count=_identity_fission_candidate_count(model),
        identity_fission_confirmed_count=0 if confirmed_count is None else confirmed_count,
        identity_fission_max_persistence_steps=(
            0 if persistence_steps is None else persistence_steps
        ),
    )


def _build_grc9_growth_summary(
    step_results: Sequence[StepResult],
) -> GRC9GrowthSummary:
    growth_events = [
        event for event in _iter_step_events(step_results) if event.kind == "growth"
    ]
    parent_ids = {
        parent_id
        for event in growth_events
        if (parent_id := _coerce_non_negative_int(event.payload.get("parent_node_id")))
        is not None
    }
    birth_probabilities = [
        probability
        for event in growth_events
        if (
            probability := _coerce_finite_float(event.payload.get("birth_probability"))
        )
        is not None
        and probability >= 0.0
    ]
    lowest_port_attachment_count = sum(
        1
        for event in growth_events
        if _coerce_non_negative_int(event.payload.get("parent_port_id")) is not None
    )
    return GRC9GrowthSummary(
        growth_count=len(growth_events),
        unique_growth_parent_count=len(parent_ids),
        lowest_port_attachment_count=lowest_port_attachment_count,
        front_capacity_growth_count=sum(
            1
            for event in growth_events
            if event.payload.get("growth_parent_eligibility_mode") == "grc9_front_capacity"
        ),
        pressure_boundary_growth_count=sum(
            1
            for event in growth_events
            if event.payload.get("growth_parent_eligibility_mode") == "grc9_front_capacity"
            and event.payload.get("growth_parent_capacity_source") == "pressure_boundary"
        ),
        legacy_broad_growth_count=sum(
            1
            for event in growth_events
            if event.payload.get("growth_parent_eligibility_mode", "legacy_any_inactive_port")
            == "legacy_any_inactive_port"
        ),
        birth_probability_min=(
            _minimum(birth_probabilities) if birth_probabilities else None
        ),
        birth_probability_max=(
            _maximum(birth_probabilities) if birth_probabilities else None
        ),
        birth_probability_mean=(
            _mean(birth_probabilities) if birth_probabilities else None
        ),
    )


def _build_grc9_calibration_summary(
    model: GRC9,
    step_results: Sequence[StepResult],
) -> GRC9CalibrationSummary:
    params = model.get_params()
    spark_threshold = _coerce_finite_float(params.evolution.get("eps_spark", 0.01))
    if spark_threshold is None or spark_threshold < 0.0:
        spark_threshold = 0.0
    burn_in_m_h = _coerce_finite_float(params.evolution.get("burn_in_M_H"))
    burn_in_m_c = _coerce_finite_float(params.evolution.get("burn_in_M_C"))
    threshold_mode = str(params.evolution.get("spark_threshold_mode", "absolute"))
    if burn_in_m_h is not None or burn_in_m_c is not None:
        threshold_mode = str(
            params.evolution.get("spark_threshold_mode", "calibrated_fraction")
        )
    spark_count = sum(1 for event in _iter_step_events(step_results) if event.kind == "spark")
    return GRC9CalibrationSummary(
        spark_threshold=spark_threshold,
        spark_threshold_mode=threshold_mode,
        burn_in_M_H=burn_in_m_h,
        burn_in_M_C=burn_in_m_c,
        spark_rate_observed=(
            None
            if not step_results
            else float(spark_count / len(tuple(step_results)))
        ),
    )


def _identity_fission_candidate_count(model: GRC9) -> int:
    state = model.get_state()
    candidate_count = 0
    for record in state.expansion_registry.values():
        module_nodes = set(record.module_node_ids)
        module_sinks = module_nodes & set(state.sink_set)
        if len(module_sinks) >= 2:
            candidate_count += 1
    return candidate_count


def _capture_grc9_identity_fission_observation(model: GRC9) -> Mapping[str, Any]:
    """Capture one compact non-mutating identity-fission observation."""

    state = model.get_state()
    modules: dict[str, Any] = {}
    for expansion_id, record in sorted(state.expansion_registry.items()):
        module_node_ids = tuple(int(node_id) for node_id in record.module_node_ids)
        module_node_set = set(module_node_ids)
        sink_observations: list[Mapping[str, Any]] = []
        for sink_id in sorted(module_node_set & set(state.sink_set)):
            basin_members = set(state.basins.get(sink_id, set()))
            basin_mass = sum(
                float(state.node_coherence.get(node_id, 0.0))
                for node_id in basin_members
            )
            sink_observations.append(
                {
                    "sink_id": int(sink_id),
                    "basin_size": len(basin_members),
                    "basin_mass": float(basin_mass),
                }
            )
        modules[str(expansion_id)] = {
            "parent_sink_id": int(record.parent_sink_id),
            "module_node_ids": list(module_node_ids),
            "sink_observations": sink_observations,
        }
    return {
        "step_index": int(state.step_index),
        "time": float(state.time),
        "modules": modules,
    }


def _evaluate_grc9_identity_fission_persistence(
    observations: Sequence[Mapping[str, Any]],
    *,
    delta: int,
    min_basin_mass: float,
) -> Mapping[str, int | float]:
    """Evaluate Appendix E-style fission persistence over captured observations."""

    if delta <= 0:
        raise ValueError("identity fission persistence delta must be > 0")
    if min_basin_mass < 0.0:
        raise ValueError("identity fission minimum basin mass must be non-negative")

    pair_streaks_by_module: dict[str, dict[tuple[int, int], int]] = {}
    max_streak_by_module: dict[str, int] = {}
    confirmed_modules: set[str] = set()
    sorted_observations = sorted(
        observations,
        key=lambda item: int(item.get("step_index", 0)),
    )
    for observation in sorted_observations:
        modules = observation.get("modules", {})
        if not isinstance(modules, Mapping):
            continue
        observed_module_keys: set[str] = set()
        for module_id, module_payload in sorted(modules.items(), key=lambda item: str(item[0])):
            if not isinstance(module_payload, Mapping):
                continue
            sink_observations = module_payload.get("sink_observations", ())
            if not isinstance(sink_observations, Sequence):
                continue
            qualifying_sink_ids: list[int] = []
            for sink_payload in sink_observations:
                if not isinstance(sink_payload, Mapping):
                    continue
                sink_id = _coerce_non_negative_int(sink_payload.get("sink_id"))
                basin_mass = _coerce_finite_float(sink_payload.get("basin_mass"))
                if (
                    sink_id is not None
                    and basin_mass is not None
                    and basin_mass >= min_basin_mass
                ):
                    qualifying_sink_ids.append(sink_id)
            module_key = str(module_id)
            observed_module_keys.add(module_key)
            previous_pair_streaks = pair_streaks_by_module.get(module_key, {})
            current_pair_streaks: dict[tuple[int, int], int] = {}
            for pair in combinations(sorted(set(qualifying_sink_ids)), 2):
                current_pair_streaks[pair] = previous_pair_streaks.get(pair, 0) + 1
            pair_streaks_by_module[module_key] = current_pair_streaks
            current_streak = max(current_pair_streaks.values(), default=0)
            max_streak_by_module[module_key] = max(
                max_streak_by_module.get(module_key, 0),
                current_streak,
            )
            if current_streak >= delta:
                confirmed_modules.add(module_key)
        for module_key in set(pair_streaks_by_module) - observed_module_keys:
            pair_streaks_by_module[module_key] = {}

    return {
        "identity_fission_confirmed_count": len(confirmed_modules),
        "identity_fission_max_persistence_steps": max(
            max_streak_by_module.values(),
            default=0,
        ),
        "identity_fission_persistence_delta": int(delta),
        "identity_fission_min_basin_mass": float(min_basin_mass),
    }


def _resolve_identity_fission_delta(model: GRC9, value: int | None) -> int:
    if value is not None:
        return int(value)
    configured = _coerce_non_negative_int(
        model.get_params().evolution.get("identity_fission_persistence_delta")
    )
    if configured is not None and configured > 0:
        return configured
    return 2


def _resolve_identity_fission_min_basin_mass(model: GRC9, value: float | None) -> float:
    if value is not None:
        return float(value)
    configured = _coerce_finite_float(
        model.get_params().evolution.get("identity_fission_min_basin_mass")
    )
    if configured is not None and configured >= 0.0:
        return configured
    return 0.0


def _iter_step_events(step_results: Sequence[StepResult]) -> tuple[GRCEvent, ...]:
    return tuple(event for step_result in step_results for event in step_result.events)


def _grc9_spark_event_context(model: GRC9, payload: Mapping[str, Any]) -> dict[str, Any]:
    params = model.get_params()
    state = model.get_state()
    sink_node_id = _coerce_non_negative_int(payload.get("sink_node_id"))
    target_effective_degree = _coerce_non_negative_int(
        payload.get("target_effective_degree")
    )
    if target_effective_degree is None:
        target_effective_degree = _coerce_non_negative_int(
            params.evolution.get("D_eff_target", 30)
        )
    requested_node_count = (
        None
        if target_effective_degree is None
        else compute_expansion_node_count(target_effective_degree)
    )
    context: dict[str, Any] = {
        "tau_instability": params.evolution.get("tau_instability", 0.5),
        "eps_spark": params.evolution.get("eps_spark", 0.01),
        "target_effective_degree": target_effective_degree,
        "requested_node_count": requested_node_count,
        "predicted_module_size": (
            None if requested_node_count is None else max(4, requested_node_count)
        ),
        "predicted_satellite_count": 3,
    }
    if sink_node_id is None:
        return context
    diagnostics = _coerce_mapping(state.cached_quantities.get("spark_diagnostics", {}))
    raw_diagnostic = diagnostics.get(str(sink_node_id), diagnostics.get(sink_node_id, {}))
    if isinstance(raw_diagnostic, Mapping):
        for key in (
            "sign_crossing",
            "trigger_column",
            "tau_instability",
            "eps_spark",
            "spark_kind",
        ):
            if key in raw_diagnostic:
                context[key] = raw_diagnostic[key]
    return context


def _grc9_expansion_event_context(
    model: GRC9,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    params = model.get_params()
    state = model.get_state()
    distribution_mode = str(
        params.constitutive_semantic_modes.get("expansion_distribution_mode", "equal")
    )
    internal_edge_ids = tuple(
        edge_id
        for raw_edge_id in payload.get("internal_edge_ids", ())
        if (edge_id := _coerce_non_negative_int(raw_edge_id)) is not None
    )
    internal_conductances = [
        float(state.port_edges[edge_id].conductance)
        for edge_id in internal_edge_ids
        if edge_id in state.port_edges
    ]
    w_bond = _coerce_finite_float(params.evolution.get("w_bond", 1.0)) or 1.0
    expansion_substeps = _coerce_non_negative_int(
        params.evolution.get("adiabatic_expansion_substeps", 1)
    ) or 1
    context: dict[str, Any] = {
        "coherence_transfer_mode": distribution_mode,
        "bond_weight_mode": _bond_weight_mode(
            internal_conductances,
            fallback=w_bond,
        ),
        "bond_weight": _mean(internal_conductances) if internal_conductances else w_bond,
        "internal_conductance_stats": _conductance_stats(internal_conductances),
        "expansion_schedule": (
            "adiabatic" if expansion_substeps > 1 else "instantaneous"
        ),
        "expansion_substeps": expansion_substeps,
    }
    return context


def _grc9_growth_event_context(model: GRC9, payload: Mapping[str, Any]) -> dict[str, Any]:
    state = model.get_state()
    return {
        "birth_rule": state.cached_quantities.get(
            "birth_rule_mode",
            "bernoulli_probability",
        ),
        "parent_selection_mode": state.cached_quantities.get(
            "birth_parent_selection_mode",
            "outward_flux_parent_selection",
        ),
        "growth_parent_eligibility_mode": state.cached_quantities.get(
            "birth_parent_eligibility_mode",
            payload.get("growth_parent_eligibility_mode", "legacy_any_inactive_port"),
        ),
        "growth_parent_capacity_source": payload.get(
            "growth_parent_capacity_source",
            "legacy_any_inactive_port",
        ),
    }


def _build_grc9_port_chart(model: GRC9) -> GRC9PortChartSummary:
    state = model.get_state()
    topology = state.topology
    live_node_ids = tuple(sorted(topology.iter_live_node_ids()))
    live_edge_ids = tuple(sorted(topology.iter_live_edge_ids()))
    active_degree_histogram = {degree: 0 for degree in range(10)}
    row_occupancy = [0, 0, 0]
    column_occupancy = [0, 0, 0]
    inactive_capacity_by_column = [0, 0, 0]
    saturated_node_ids: list[int] = []
    near_saturated_count = 0

    for node_id in live_node_ids:
        active_degree = len(tuple(topology.incident_edge_ids(node_id)))
        active_degree_histogram[active_degree] = (
            active_degree_histogram.get(active_degree, 0) + 1
        )
        if active_degree >= 9:
            saturated_node_ids.append(node_id)
        elif active_degree == 8:
            near_saturated_count += 1
        for slot in topology.iter_port_slots(node_id):
            port_id = slot_to_port_id(int(slot))
            _, column = port_to_rc(port_id)
            if not topology.port_is_occupied(node_id, int(slot)):
                inactive_capacity_by_column[column - 1] += 1

    for edge_id in live_edge_ids:
        for _, slot in topology.edge_ports(edge_id):
            port_id = slot_to_port_id(int(slot))
            row, column = port_to_rc(port_id)
            row_occupancy[row - 1] += 1
            column_occupancy[column - 1] += 1

    return GRC9PortChartSummary(
        num_nodes=len(live_node_ids),
        num_port_edges=len(live_edge_ids),
        active_degree_histogram=active_degree_histogram,
        inactive_port_count=sum(max(0, 9 - len(tuple(topology.incident_edge_ids(node_id)))) for node_id in live_node_ids),
        saturated_node_count=len(saturated_node_ids),
        near_saturated_node_count=near_saturated_count,
        row_occupancy_totals=tuple(row_occupancy),
        column_occupancy_totals=tuple(column_occupancy),
        saturated_node_ids_sample=tuple(saturated_node_ids[:8]),
        inactive_capacity_by_column=tuple(inactive_capacity_by_column),
    )


def _build_grc9_row_tensor(model: GRC9) -> GRC9RowTensorSummary:
    caches = model.get_state().cached_quantities
    raw_row_tensor = caches.get("row_tensor_diagonal", {})
    row_tensor = _coerce_node_vector_mapping(raw_row_tensor, expected_len=3)
    all_values = [value for values in row_tensor.values() for value in values]
    tensor_terms = _coerce_mapping(caches.get("tensor_terms", {}))
    density_terms = _coerce_float_sequence(
        entry.get("density_term")
        for entry in tensor_terms.values()
        if isinstance(entry, Mapping)
    )
    flux_feedback_terms = _coerce_float_sequence(
        entry.get("flux_feedback_term")
        for entry in tensor_terms.values()
        if isinstance(entry, Mapping)
    )
    row_mismatch_terms = _coerce_mapping(caches.get("row_mismatch_terms", {}))
    mismatch_items: list[tuple[float, int, int]] = []
    for raw_node_id, raw_by_row in row_mismatch_terms.items():
        node_id = _coerce_non_negative_int(raw_node_id)
        if node_id is None or not isinstance(raw_by_row, Mapping):
            continue
        for raw_row, raw_value in raw_by_row.items():
            row = _coerce_non_negative_int(raw_row)
            value = _coerce_finite_float(raw_value)
            if row is not None and value is not None:
                mismatch_items.append((value, node_id, row))
    mismatch_values = [item[0] for item in mismatch_items]
    hotspots = tuple(
        {
            "node_id": node_id,
            "row": row,
            "row_mismatch_term": value,
        }
        for value, node_id, row in sorted(
            mismatch_items, key=lambda item: (-item[0], item[1], item[2])
        )[:5]
        if value > 0.0
    )
    row_sample = {
        node_id: tuple(values)
        for node_id, values in sorted(row_tensor.items())[:5]
    }

    return GRC9RowTensorSummary(
        row_tensor_min=_minimum(all_values),
        row_tensor_max=_maximum(all_values),
        row_tensor_mean=_mean(all_values),
        row_tensor_anisotropy_max=max(
            (max(values) - min(values) for values in row_tensor.values()),
            default=0.0,
        ),
        density_term_mean=_mean(density_terms),
        row_mismatch_term_max=_maximum(mismatch_values),
        flux_feedback_term_mean=_mean(flux_feedback_terms),
        row_mismatch_hotspots=hotspots,
        row_tensor_by_node_sample=row_sample,
    )


def _build_grc9_column_diagnostic(model: GRC9) -> GRC9ColumnDiagnosticSummary:
    state = model.get_state()
    params = model.get_params()
    eps_spark = _coerce_finite_float(params.evolution.get("eps_spark", 0.01)) or 0.0
    raw_diagnostics = _coerce_mapping(state.cached_quantities.get("spark_diagnostics", {}))
    diagnostics: dict[int, tuple[float, float, float]] = {}
    min_abs_values: list[float] = []
    proxy_candidates = 0
    sign_crossing_candidates = 0
    hotspots: list[Mapping[str, Any]] = []

    for raw_node_id, raw_payload in raw_diagnostics.items():
        node_id = _coerce_non_negative_int(raw_node_id)
        if node_id is None or not isinstance(raw_payload, Mapping):
            continue
        vector = _coerce_float_sequence(raw_payload.get("column_diagnostic", ()))
        if len(vector) == 3:
            diagnostics[node_id] = tuple(vector)  # type: ignore[assignment]
        min_abs = _coerce_finite_float(raw_payload.get("min_abs_column"))
        if min_abs is not None and min_abs >= 0.0:
            min_abs_values.append(min_abs)
            if min_abs < eps_spark:
                proxy_candidates += 1
            hotspots.append(
                {
                    "node_id": node_id,
                    "min_abs_column": min_abs,
                    "active_degree": _coerce_non_negative_int(raw_payload.get("active_degree")),
                    "spark_kind": raw_payload.get("spark_kind"),
                }
            )
        if bool(raw_payload.get("sign_crossing", False)):
            sign_crossing_candidates += 1

    sparsity = _column_profile_sparsity_from_state(model)
    return GRC9ColumnDiagnosticSummary(
        column_diagnostic_min_abs=_minimum(min_abs_values),
        column_diagnostic_mean_abs=_mean(min_abs_values),
        column_proxy_candidate_count=proxy_candidates,
        sign_crossing_candidate_count=sign_crossing_candidates,
        column_profile_sparsity=sparsity,
        column_diagnostic_by_candidate=diagnostics,
        column_diagnostic_hotspots=tuple(
            sorted(hotspots, key=lambda item: (float(item["min_abs_column"]), int(item["node_id"])))[:5]
        ),
        spark_calibration=GRC9SparkCalibrationTelemetry(
            spark_threshold=eps_spark,
            spark_threshold_mode="absolute",
        ),
    )


def _build_grc9_transport(model: GRC9) -> GRC9TransportSummary:
    state = model.get_state()
    live_edge_ids = tuple(sorted(state.topology.iter_live_edge_ids()))
    live_port_edges = [
        state.port_edges[edge_id]
        for edge_id in live_edge_ids
        if edge_id in state.port_edges
    ]
    conductances = [float(port_edge.conductance) for port_edge in live_port_edges]
    fluxes = [float(port_edge.flux_uv) for port_edge in live_port_edges]
    strongest_flux_edges = tuple(
        {
            "edge_id": edge_id,
            "node_u": state.port_edges[edge_id].node_u,
            "node_v": state.port_edges[edge_id].node_v,
            "flux_uv": float(state.port_edges[edge_id].flux_uv),
            "abs_flux": abs(float(state.port_edges[edge_id].flux_uv)),
        }
        for edge_id in sorted(
            (edge_id for edge_id in live_edge_ids if edge_id in state.port_edges),
            key=lambda item: (-abs(float(state.port_edges[item].flux_uv)), item),
        )[:5]
    )
    potentials = _coerce_float_sequence(state.potential.values())
    potential_min = _minimum(potentials) if potentials else None
    potential_max = _maximum(potentials) if potentials else None
    label_availability = _build_grc9_label_availability(model)
    label_modes = dict(state.edge_label_computation_mode)
    if not label_modes:
        label_modes = {
            str(key): str(value)
            for key, value in _coerce_mapping(
                state.cached_quantities.get("edge_label_computation_mode", {})
            ).items()
        }

    return GRC9TransportSummary(
        conductance_min=_minimum(conductances),
        conductance_max=_maximum(conductances),
        conductance_mean=_mean(conductances),
        flux_abs_sum=sum(abs(value) for value in fluxes),
        flux_signed_balance=sum(fluxes),
        positive_flux_edge_count=sum(1 for value in fluxes if value > 0.0),
        negative_flux_edge_count=sum(1 for value in fluxes if value < 0.0),
        strongest_flux_edges_sample=strongest_flux_edges,
        potential_min=potential_min,
        potential_max=potential_max,
        potential_range=(
            None
            if potential_min is None or potential_max is None
            else potential_max - potential_min
        ),
        label_availability=label_availability,
        label_computation_mode=label_modes,
    )


def _build_grc9_identity_abundance(model: GRC9) -> GRC9IdentityAbundanceSummary:
    state = model.get_state()
    params = model.get_params()
    basin_sizes = [len(members) for members in state.basins.values()]
    basin_masses: list[float] = []
    for members in state.basins.values():
        basin_masses.append(
            sum(float(state.node_coherence.get(node_id, 0.0)) for node_id in members)
        )
    successor_map = _coerce_mapping(state.cached_quantities.get("successor_map", {}))
    successor_self_loops = 0
    for raw_node_id, raw_successor_id in successor_map.items():
        node_id = _coerce_non_negative_int(raw_node_id)
        successor_id = _coerce_non_negative_int(raw_successor_id)
        if node_id is not None and successor_id is not None and node_id == successor_id:
            successor_self_loops += 1
    scale_gamma = _scale_weighted_abundance_gamma(params)
    scale_weighted_abundance = (
        None
        if scale_gamma is None
        else float(sum(float(size) ** scale_gamma for size in basin_sizes))
    )

    return GRC9IdentityAbundanceSummary(
        sink_count=len(state.sink_set),
        basin_count=len(state.basins),
        basin_size_min=int(_minimum(basin_sizes)),
        basin_size_max=int(_maximum(basin_sizes)),
        basin_size_mean=_mean(basin_sizes),
        abundance_contract=GRC9_ABUNDANCE_CONTRACT,
        scale_weighted_abundance=scale_weighted_abundance,
        scale_weighted_abundance_gamma=scale_gamma,
        successor_self_loop_count=successor_self_loops,
        successor_tie_count=_successor_tie_count(model),
        successor_tie_break_policy="max_positive_flux_then_neighbor_id_then_edge_id",
        basin_mass_summary={
            "min": _minimum(basin_masses),
            "max": _maximum(basin_masses),
            "mean": _mean(basin_masses),
        },
    )


def _successor_tie_count(model: GRC9) -> int:
    state = model.get_state()
    tie_count = 0
    for node_id in sorted(state.topology.iter_live_node_ids()):
        outgoing_candidates: list[float] = []
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            if edge_id not in state.port_edges:
                continue
            outgoing_flux = _oriented_flux_from_port_edge(
                state.port_edges[edge_id],
                node_id=node_id,
            )
            if outgoing_flux > 0.0:
                outgoing_candidates.append(outgoing_flux)
        if len(outgoing_candidates) < 2:
            continue
        max_outgoing = max(outgoing_candidates)
        max_tie_size = sum(
            1
            for outgoing_flux in outgoing_candidates
            if math.isclose(outgoing_flux, max_outgoing, rel_tol=0.0, abs_tol=1e-12)
        )
        if max_tie_size > 1:
            tie_count += 1
    return tie_count


def _oriented_flux_from_port_edge(port_edge: Any, *, node_id: int) -> float:
    if port_edge.node_u == node_id:
        return float(port_edge.flux_uv)
    if port_edge.node_v == node_id:
        return float(-port_edge.flux_uv)
    return 0.0


def _bond_weight_mode(values: Sequence[float], *, fallback: float) -> str:
    if not values:
        return "fixed"
    if all(math.isclose(value, fallback, rel_tol=0.0, abs_tol=1e-12) for value in values):
        return "fixed"
    return "column_geometric_mean"


def _conductance_stats(values: Sequence[float]) -> Mapping[str, float] | None:
    if not values:
        return None
    return {
        "min": _minimum(values),
        "max": _maximum(values),
        "mean": _mean(values),
    }


def _scale_weighted_abundance_gamma(params: GRCParams) -> float | None:
    for key in (
        "scale_weighted_abundance_gamma",
        "abundance_gamma",
        "gamma",
    ):
        gamma = _coerce_finite_float(params.evolution.get(key))
        if gamma is not None and gamma >= 0.0:
            return gamma
    return None


def _build_grc9_coarse_graining(model: GRC9) -> GRC9CoarseGrainingSummary:
    state = model.get_state()
    coarse_fields: set[str] = set()
    coarse_field_types: dict[str, str] = {}
    column_total_sparsity_by_field: dict[str, float] = {}

    for cache_key, raw_payload in sorted(state.coarse_cache.items()):
        mode, _, suffix = str(cache_key).partition(":")
        field_name = suffix or str(cache_key)
        if isinstance(raw_payload, Mapping):
            field_name = str(raw_payload.get("field_name", field_name))
            mode = str(raw_payload.get("mode", mode))
        coarse_fields.add(field_name)
        if mode == "signed_flux_split":
            coarse_field_types[field_name] = "signed_lossless"
        elif mode == "exact_column_profile":
            coarse_field_types[field_name] = "nonnegative"
        else:
            coarse_field_types[field_name] = "signed_compressed"
        sparsity = _coarse_column_total_sparsity(raw_payload)
        if sparsity is not None:
            column_total_sparsity_by_field[field_name] = sparsity

    return GRC9CoarseGrainingSummary(
        coarse_fields_list=tuple(sorted(coarse_fields)),
        coarse_cache_state="warm" if state.coarse_cache else "empty",
        coarse_cache_invalidation_reason=_coerce_optional_string(
            state.cached_quantities.get("coarse_cache_invalidation_reason")
        ),
        exact_split_supported_fields=_SUPPORTED_COARSE_FIELDS,
        signed_flux_mode="signed_flux_split",
        coarse_field_types=coarse_field_types,
        column_total_sparsity_by_field=(
            column_total_sparsity_by_field if column_total_sparsity_by_field else None
        ),
        profile_compression_mode="full",
    )


def _build_grc9_budget_correction(model: GRC9) -> GRC9BudgetCorrectionSummary:
    state = model.get_state()
    budget_current = float(sum(state.node_coherence.values()))
    budget_target = float(state.budget_target)
    budget_error = float(budget_current - budget_target)
    correction_path = _coerce_optional_string(
        state.cached_quantities.get("budget_positive_correction_mode")
    )
    if correction_path is None:
        correction_path = "none"
    negative_correction = _coerce_finite_float(
        state.cached_quantities.get("negative_mass_correction")
    )
    return GRC9BudgetCorrectionSummary(
        budget_current=budget_current,
        budget_target=budget_target,
        budget_error=budget_error,
        budget_preservation_policy=_BUDGET_POLICY,
        last_budget_correction_path=correction_path,
        simplex_projection_applied=False,
        negative_clamp_count=1 if negative_correction and negative_correction > 0.0 else 0,
    )


def _build_grc9_label_availability(model: GRC9) -> GRC9LabelAvailability:
    state = model.get_state()
    live_edge_count = len(tuple(state.topology.iter_live_edge_ids()))
    geometric = _label_map_complete(state.geometric_length, live_edge_count)
    temporal = _label_map_complete(state.temporal_delay, live_edge_count)
    coupling = _label_map_complete(state.flux_coupling, live_edge_count)
    available_count = sum((geometric, temporal, coupling))
    if available_count == 3:
        overall = "all"
    elif available_count == 0:
        overall = "none"
    else:
        overall = "partial"
    return GRC9LabelAvailability(
        overall=overall,
        geometric_length_available=geometric,
        temporal_delay_available=temporal,
        flux_coupling_available=coupling,
    )


def _label_map_complete(values: Mapping[int, float], live_edge_count: int) -> bool:
    return live_edge_count > 0 and len(values) >= live_edge_count


def _column_profile_sparsity_from_state(model: GRC9) -> float:
    state = model.get_state()
    live_node_ids = tuple(sorted(state.topology.iter_live_node_ids()))
    if not live_node_ids:
        return 0.0
    zero_column_count = 0
    for node_id in live_node_ids:
        for column in (1, 2, 3):
            column_occupied = any(
                state.topology.port_edge_id(node_id, (row - 1) * 3 + (column - 1))
                is not None
                for row in (1, 2, 3)
            )
            if not column_occupied:
                zero_column_count += 1
    return float(zero_column_count / (3 * len(live_node_ids)))


def _coarse_column_total_sparsity(raw_payload: Any) -> float | None:
    if not isinstance(raw_payload, Mapping):
        return None
    mode = str(raw_payload.get("mode", ""))
    if mode == "signed_flux_split":
        positive = _coarse_column_total_sparsity(raw_payload.get("positive"))
        negative = _coarse_column_total_sparsity(raw_payload.get("negative"))
        if positive is None and negative is None:
            return None
        values = [value for value in (positive, negative) if value is not None]
        return _mean(values)
    by_node = raw_payload.get("by_node")
    if not isinstance(by_node, Mapping):
        return None
    total_count = 0
    zero_count = 0
    for raw_entry in by_node.values():
        if not isinstance(raw_entry, Mapping):
            continue
        totals = raw_entry.get("column_totals")
        if not isinstance(totals, Sequence):
            continue
        for raw_total in totals:
            total = _coerce_finite_float(raw_total)
            if total is None:
                continue
            total_count += 1
            if total == 0.0:
                zero_count += 1
    if total_count == 0:
        return None
    return float(zero_count / total_count)


def _coerce_node_vector_mapping(
    value: Any,
    *,
    expected_len: int,
) -> dict[int, tuple[float, ...]]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[int, tuple[float, ...]] = {}
    for raw_key, raw_values in value.items():
        node_id = _coerce_non_negative_int(raw_key)
        if node_id is None:
            continue
        values = _coerce_float_sequence(raw_values)
        if len(values) == expected_len:
            result[node_id] = tuple(values)
    return result


def _coerce_mapping(value: Any) -> Mapping[Any, Any]:
    return value if isinstance(value, Mapping) else {}


def _coerce_float_sequence(values: Any) -> list[float]:
    if isinstance(values, Sequence) and not isinstance(values, str | bytes):
        iterable = values
    else:
        iterable = tuple(values) if hasattr(values, "__iter__") else ()
    result: list[float] = []
    for value in iterable:
        numeric = _coerce_finite_float(value)
        if numeric is not None:
            result.append(numeric)
    return result


def _coerce_finite_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    numeric = float(value)
    return numeric if math.isfinite(numeric) else None


def _coerce_non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str):
        try:
            numeric = int(value)
        except ValueError:
            return None
        return numeric if numeric >= 0 else None
    return None


def _coerce_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _minimum(values: Sequence[float] | Sequence[int]) -> float:
    return float(min(values)) if values else 0.0


def _maximum(values: Sequence[float] | Sequence[int]) -> float:
    return float(max(values)) if values else 0.0


def _mean(values: Sequence[float] | Sequence[int]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


__all__ = [
    "_build_grc9_backend_config",
    "_build_grc9_event_extension",
    "_build_grc9_run_summary_extension",
    "_build_grc9_step_extension",
    "_capture_grc9_identity_fission_observation",
    "_evaluate_grc9_identity_fission_persistence",
]

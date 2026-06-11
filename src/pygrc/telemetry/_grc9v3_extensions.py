"""Private builders for GRC9V3 telemetry extension payloads."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import math
from typing import Any

from pygrc.core import GRCEvent, StepResult
from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_to_rc, slot_to_port_id
from pygrc.models.grc_9_v3_state import GRC9V3State

from .grc9v3_contract import (
    GRC9V3BackendConfigTelemetry,
    GRC9V3AppendixESummary,
    GRC9V3BudgetCorrectionSummary,
    GRC9V3ChoiceCollapseSummary,
    GRC9V3CoarseCacheSummary,
    GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
    GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION,
    GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE,
    GRC9V3EventTelemetryExtension,
    GRC9V3GrowthStateSummary,
    GRC9V3HierarchyStateSummary,
    GRC9V3HybridSparkStateSummary,
    GRC9V3HybridTensorSummary,
    GRC9V3IdentityBasinSummary,
    GRC9V3LabelAvailability,
    GRC9V3LaneContext,
    GRC9V3LifecycleEventCounts,
    GRC9V3PortChartSummary,
    GRC9V3RowBasisDifferentialSummary,
    GRC9V3RunSummaryExtension,
    GRC9V3StepTelemetryExtension,
    GRC9V3TransportSummary,
    classify_grc9v3_event_extension,
)


def _build_grc9v3_step_extension(
    model: GRC9V3,
    *,
    lane_context: GRC9V3LaneContext | None = None,
) -> GRC9V3StepTelemetryExtension:
    """Build the stable GRC9V3 family-extension payload for one step row."""

    state = model.get_state()
    params = model.get_params()
    resolved_lane_context = lane_context or GRC9V3LaneContext(
        source_reference="implementation/Phase-T-GRC9V3-TelemetryContract.md",
        fixture_name="runtime_state",
        run_role="unspecified",
    )
    return GRC9V3StepTelemetryExtension(
        lane_context=resolved_lane_context,
        backend_config=_build_backend_config(params.constitutive_semantic_modes),
        port_chart=_build_port_chart(state),
        row_basis_differential=_build_row_basis_differential(state, params.constitutive_semantic_modes),
        hybrid_tensor=_build_hybrid_tensor(state),
        transport=_build_transport(state),
        identity_basin=_build_identity_basin(state),
        hybrid_spark_state=_build_hybrid_spark_state(state),
        hierarchy_state=_build_hierarchy_state(state),
        choice_collapse=_build_choice_collapse(state, params.evolution, params.constitutive_semantic_modes),
        growth_state=_build_growth_state(state),
        budget_correction=_build_budget_correction(state, params.constitutive_semantic_modes),
        coarse_cache=_build_coarse_cache(state),
    )


def _build_grc9v3_event_extension(
    model: GRC9V3,
    event: GRCEvent,
    *,
    lane_context: GRC9V3LaneContext | None = None,
) -> GRC9V3EventTelemetryExtension:
    """Build the stable GRC9V3 family-extension payload for one event row."""

    del model
    return classify_grc9v3_event_extension(
        event.kind,
        event.payload,
        lane_context=lane_context,
    )


def _build_grc9v3_event_extensions(
    model: GRC9V3,
    events: Sequence[GRCEvent],
    *,
    lane_context: GRC9V3LaneContext | None = None,
) -> tuple[GRC9V3EventTelemetryExtension, ...]:
    """Build event extensions in the same order as raw runtime events."""

    return tuple(
        _build_grc9v3_event_extension(
            model,
            event,
            lane_context=lane_context,
        )
        for event in events
    )


def _build_grc9v3_run_summary_extension(
    model: GRC9V3,
    step_results: Sequence[StepResult],
    *,
    lane_context: GRC9V3LaneContext | None = None,
    replay_digest_match: bool | None = None,
) -> GRC9V3RunSummaryExtension:
    """Build the stable GRC9V3 family-extension payload for one run summary."""

    resolved_lane_context = lane_context or GRC9V3LaneContext(
        source_reference="implementation/Phase-T-GRC9V3-TelemetryContract.md",
        fixture_name="runtime_state",
        run_role="unspecified",
    )
    final_step_extension = _build_grc9v3_step_extension(
        model,
        lane_context=resolved_lane_context,
    )
    return GRC9V3RunSummaryExtension(
        lane_context=resolved_lane_context,
        backend_summary=final_step_extension.backend_config,
        final_port_chart_summary=final_step_extension.port_chart,
        final_differential_summary=final_step_extension.row_basis_differential,
        final_identity_basin_summary=final_step_extension.identity_basin,
        final_hierarchy_summary=final_step_extension.hierarchy_state,
        final_choice_collapse_summary=final_step_extension.choice_collapse,
        final_budget_summary=final_step_extension.budget_correction,
        lifecycle_event_counts=_build_grc9v3_lifecycle_event_counts(step_results),
        representative_appendix_e_summary=_build_appendix_e_summary(
            model,
            lane_context=resolved_lane_context,
            replay_digest_match=bool(replay_digest_match),
        ),
    )


def _build_grc9v3_lifecycle_event_counts(
    step_results: Sequence[StepResult],
) -> GRC9V3LifecycleEventCounts:
    events = _iter_step_events(step_results)
    counts = Counter(event.kind for event in events)
    growth_events = [event for event in events if event.kind == "growth"]
    front_capacity_growth_count = sum(
        1
        for event in growth_events
        if event.payload.get("growth_parent_eligibility_mode")
        == "grcl9v3_front_capacity"
    )
    pressure_boundary_growth_count = sum(
        1
        for event in growth_events
        if event.payload.get("growth_parent_eligibility_mode")
        == "grcl9v3_front_capacity"
        and event.payload.get("growth_parent_capacity_source") == "pressure_boundary"
    )
    return GRC9V3LifecycleEventCounts(
        hybrid_spark_candidate_count=counts.get("hybrid_spark_candidate", 0),
        hybrid_mechanical_expansion_count=counts.get("hybrid_mechanical_expansion", 0),
        hybrid_spark_completed_count=counts.get("hybrid_spark_completed", 0),
        choice_detected_count=counts.get("choice_detected", 0),
        choice_resolved_count=counts.get("choice_resolved", 0),
        collapse_count=counts.get("collapse", 0),
        growth_count=counts.get("growth", 0),
        front_capacity_growth_count=front_capacity_growth_count,
        pressure_boundary_growth_count=pressure_boundary_growth_count,
        legacy_broad_growth_count=len(growth_events) - front_capacity_growth_count,
        budget_correction_count=counts.get("budget_correction", 0),
        coarse_invalidation_count=counts.get("coarse_cache_invalidation", 0),
        boundary_event_count=counts.get("boundary", 0),
    )


def _build_appendix_e_summary(
    model: GRC9V3,
    *,
    lane_context: GRC9V3LaneContext,
    replay_digest_match: bool,
) -> GRC9V3AppendixESummary | None:
    if not lane_context.fixture_name.startswith("appendix_e_cell_division"):
        return None
    state = model.get_state()
    completed = _mapping_or_empty(state.cached_quantities.get("last_completed_hybrid_spark"))
    stabilization = _mapping_or_empty(
        state.cached_quantities.get("last_child_basin_stabilization")
    )
    hierarchy_parent = _optional_string(completed.get("hierarchy_parent"))
    if hierarchy_parent is None:
        return None
    daughter_sink_node_ids = tuple(
        int(value) for value in _sequence_or_empty(completed.get("stabilized_child_node_ids"))
    )
    final_budget = _mapping_or_empty(state.cached_quantities.get("last_quadrature_budget"))
    budget_error = _optional_float(final_budget.get("budget_error"))
    if budget_error is None:
        budget_error = float(sum(node.coherence for node in state.nodes.values()) - state.budget_target)
    return GRC9V3AppendixESummary(
        fixture_name=lane_context.fixture_name,
        spark_completed=bool(daughter_sink_node_ids),
        daughter_sink_count=len(daughter_sink_node_ids),
        daughter_sink_node_ids=daughter_sink_node_ids,
        module_basin_mass=_float_mapping(stabilization.get("module_basin_mass")),
        hierarchy_parent=hierarchy_parent,
        hierarchy_children=tuple(
            str(value) for value in _sequence_or_empty(completed.get("hierarchy_children"))
        ),
        budget_preserved=abs(float(budget_error)) <= 1e-9,
        replay_digest_match=bool(replay_digest_match),
    )


def _iter_step_events(step_results: Sequence[StepResult]) -> tuple[GRCEvent, ...]:
    return tuple(event for step_result in step_results for event in step_result.events)


def _build_backend_config(modes: Mapping[str, Any]) -> GRC9V3BackendConfigTelemetry:
    spark_lane = str(
        modes.get("spark_lane", GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE)
    )
    spark_lane_version = (
        GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION
        if spark_lane == GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE
        else None
    )
    return GRC9V3BackendConfigTelemetry(
        frame_mode=str(modes.get("frame_mode", "fixed_port_chart")),
        hessian_backend=str(modes.get("hessian_backend", "row_basis_diagonal")),
        curvature_backend=str(modes.get("curvature_backend", "none")),
        choice_backend=str(modes.get("choice_backend", "sink_compatibility")),
        boundary_mode=str(modes.get("boundary_mode", "prune")),
        quadrature_mode=str(modes.get("quadrature_mode", "unit_measure")),
        budget_correction_method=str(
            modes.get("budget_correction_method", "simplex_projection")
        ),
        expansion_distribution_mode=str(modes.get("expansion_distribution_mode", "equal")),
        edge_label_selection=_edge_label_selection_name(modes.get("edge_label_selection", "all")),
        spark_signed_crossing=bool(modes.get("spark_signed_crossing", False)),
        spark_lane=spark_lane,
        spark_lane_version=spark_lane_version,
        default_evolution_provenance=_plain_mapping_or_none(
            modes.get("default_evolution_provenance")
        ),
        reserved_modes={
            "boundary_barrier": "reserved_until_boundary_barrier_capability"
        },
    )


def _build_port_chart(state: GRC9V3State) -> GRC9V3PortChartSummary:
    live_node_ids = tuple(sorted(state.topology.iter_live_node_ids()))
    live_edge_ids = tuple(sorted(state.topology.iter_live_edge_ids()))
    active_degree_by_node = {
        node_id: len(tuple(state.topology.incident_edge_ids(node_id)))
        for node_id in live_node_ids
    }
    active_histogram = dict(sorted(Counter(active_degree_by_node.values()).items()))
    saturated_node_ids = tuple(
        node_id for node_id, active_degree in active_degree_by_node.items() if active_degree == 9
    )
    row_totals = [0, 0, 0]
    column_totals = [0, 0, 0]
    inactive_capacity: dict[int, int] = {}

    for node_id in live_node_ids:
        inactive_capacity[node_id] = 9 - active_degree_by_node[node_id]
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            local_port_id = _local_port_id(state, edge_id=edge_id, node_id=node_id)
            row, column = port_to_rc(local_port_id)
            row_totals[row - 1] += 1
            column_totals[column - 1] += 1

    module_node_ids = _latest_module_node_ids(state)
    return GRC9V3PortChartSummary(
        num_nodes=len(live_node_ids),
        num_port_edges=len(live_edge_ids),
        active_degree_histogram=active_histogram,
        inactive_port_count=sum(inactive_capacity.values()),
        saturated_node_count=len(saturated_node_ids),
        saturated_node_ids_sample=saturated_node_ids[:10],
        row_occupancy_totals=tuple(row_totals),
        column_occupancy_totals=tuple(column_totals),
        inactive_capacity_by_node_sample=dict(sorted(inactive_capacity.items())[:10]),
        module_node_count=len(module_node_ids) if module_node_ids else None,
    )


def _build_row_basis_differential(
    state: GRC9V3State,
    modes: Mapping[str, Any],
) -> GRC9V3RowBasisDifferentialSummary:
    gradient_norms = [
        math.sqrt(sum(float(value) * float(value) for value in node.gradient_row_basis))
        for _, node in sorted(state.nodes.items())
        if node.gradient_row_basis
    ]
    signed_values = [
        float(value)
        for _, node in sorted(state.nodes.items())
        for value in node.signed_hessian_row_basis
    ]
    current_min_signed = _float_mapping_values(
        state.cached_quantities.get("current_min_signed_hessian_by_node")
    )
    previous_min_signed = state.cached_quantities.get("previous_min_signed_hessian_by_node")
    weighted_hessian = state.cached_quantities.get("weighted_least_squares_hessian")
    geometric_identity = _mapping_or_empty(state.cached_quantities.get("geometric_identity"))

    hessian_backend = str(
        state.cached_quantities.get(
            "hessian_backend",
            modes.get("hessian_backend", "row_basis_diagonal"),
        )
    )
    return GRC9V3RowBasisDifferentialSummary(
        gradient_norm_min=_min_or_zero(gradient_norms),
        gradient_norm_max=_max_or_zero(gradient_norms),
        gradient_norm_mean=_mean_or_zero(gradient_norms),
        signed_hessian_min=_min_or_zero(signed_values),
        signed_hessian_max=_max_or_zero(signed_values),
        signed_hessian_mean=_mean_or_zero(signed_values),
        current_min_signed_hessian_min=_min_or_zero(current_min_signed),
        hessian_backend=hessian_backend,
        hessian_sign=_valid_hessian_sign(state.cached_quantities.get("hessian_sign")),
        previous_min_signed_hessian_available=bool(
            isinstance(previous_min_signed, Mapping) and previous_min_signed
        ),
        signed_hessian_history_pruned_count=len(
            _sequence_or_empty(
                state.cached_quantities.get("signed_hessian_history_pruned_node_ids")
            )
        ),
        weighted_least_squares_hessian_available=(
            hessian_backend == "weighted_least_squares"
            and isinstance(weighted_hessian, Mapping)
            and bool(weighted_hessian)
        ),
        geometric_seed_count=len(_sequence_or_empty(geometric_identity.get("seed_nodes"))),
    )


def _build_hybrid_tensor(state: GRC9V3State) -> GRC9V3HybridTensorSummary:
    tensor_by_node = _mapping_or_empty(state.cached_quantities.get("hybrid_node_tensors"))
    trace_by_node: dict[int, float] = {}
    anisotropy_by_node: dict[int, float] = {}
    for node_id, matrix in tensor_by_node.items():
        rows = _matrix_rows(matrix)
        if not rows:
            continue
        diagonal = [
            float(rows[index][index])
            for index in range(min(len(rows), min(len(row) for row in rows)))
        ]
        if not diagonal:
            continue
        node_id_int = int(node_id)
        trace_by_node[node_id_int] = float(sum(diagonal))
        anisotropy_by_node[node_id_int] = float(max(diagonal) - min(diagonal))

    mismatch_by_node = _mapping_or_empty(state.cached_quantities.get("row_mismatch_sums"))
    mismatch_sums: dict[int, float] = {}
    for node_id, values in mismatch_by_node.items():
        row_values = _float_sequence(values)
        if row_values:
            mismatch_sums[int(node_id)] = float(sum(abs(value) for value in row_values))

    flux_feedback = [
        float(sum(node.net_flux_summary) ** 2)
        for _, node in sorted(state.nodes.items())
        if node.net_flux_summary
    ]
    trace_values = list(trace_by_node.values())
    return GRC9V3HybridTensorSummary(
        tensor_trace_min=_min_or_zero(trace_values),
        tensor_trace_max=_max_or_zero(trace_values),
        tensor_trace_mean=_mean_or_zero(trace_values),
        tensor_anisotropy_max=_max_or_zero(anisotropy_by_node.values()),
        row_mismatch_sum_max=_max_or_zero(mismatch_sums.values()),
        flux_feedback_sum_mean=_mean_or_zero(flux_feedback),
        tensor_hotspot_node_ids_sample=_top_node_ids(trace_by_node),
        row_mismatch_hotspot_node_ids_sample=_top_node_ids(mismatch_sums),
    )


def _build_transport(state: GRC9V3State) -> GRC9V3TransportSummary:
    live_edge_ids = tuple(sorted(state.topology.iter_live_edge_ids()))
    base_values = [
        float(state.base_conductance.get(edge_id, state.port_edges[edge_id].conductance))
        for edge_id in live_edge_ids
        if edge_id in state.port_edges
    ]
    potential_values = [float(value) for _, value in sorted(state.potential.items())]
    flux_values = [
        float(state.port_edges[edge_id].flux_uv)
        for edge_id in live_edge_ids
        if edge_id in state.port_edges
    ]
    return GRC9V3TransportSummary(
        base_conductance_min=_min_or_zero(base_values),
        base_conductance_max=_max_or_zero(base_values),
        base_conductance_mean=_mean_or_zero(base_values),
        potential_min=_min_or_zero(potential_values),
        potential_max=_max_or_zero(potential_values),
        flux_abs_sum=float(sum(abs(value) for value in flux_values)),
        positive_flux_edge_count=sum(1 for value in flux_values if value > 0.0),
        negative_flux_edge_count=sum(1 for value in flux_values if value < 0.0),
        label_availability=GRC9V3LabelAvailability(
            geometric_length_available=bool(state.geometric_length),
            temporal_delay_available=bool(state.temporal_delay),
            flux_coupling_available=bool(state.flux_coupling),
        ),
        label_computation_mode={
            str(key): str(value)
            for key, value in sorted(state.edge_label_computation_mode.items())
        },
    )


def _build_identity_basin(state: GRC9V3State) -> GRC9V3IdentityBasinSummary:
    basin_sizes = [len(members) for _, members in sorted(state.basins.items())]
    geometric_identity = _mapping_or_empty(state.cached_quantities.get("geometric_identity"))
    successor_map = _mapping_or_empty(state.cached_quantities.get("successor_map"))
    stabilization = _mapping_or_empty(
        state.cached_quantities.get("last_child_basin_stabilization")
    )
    module_sink_nodes = _sequence_or_empty(stabilization.get("module_sink_nodes"))
    daughter_nodes = _sequence_or_empty(stabilization.get("stabilized_child_node_ids"))
    basin_mass_summary = _float_mapping(stabilization.get("module_basin_mass"))
    if not basin_mass_summary:
        basin_mass_summary = _float_mapping(
            geometric_identity.get("basin_mass_by_basin_id")
        )
    basin_mass_summary = basin_mass_summary or None

    return GRC9V3IdentityBasinSummary(
        sink_count=len(state.sink_set),
        basin_count=len(state.basins),
        basin_size_min=int(_min_or_zero(basin_sizes)),
        basin_size_max=int(_max_or_zero(basin_sizes)),
        basin_size_mean=_mean_or_zero(basin_sizes),
        geometric_seed_count=len(_sequence_or_empty(geometric_identity.get("seed_nodes"))),
        validated_basin_count=len(
            _sequence_or_empty(geometric_identity.get("validated_basin_ids"))
        ),
        successor_self_loop_count=sum(
            1
            for node_id, successor in successor_map.items()
            if str(node_id) == str(successor)
        ),
        successor_tie_count=_successor_tie_count(state),
        basin_mass_summary=basin_mass_summary,
        module_sink_count=len(module_sink_nodes) if stabilization else None,
        daughter_sink_count=len(daughter_nodes) if stabilization else None,
    )


def _build_hybrid_spark_state(state: GRC9V3State) -> GRC9V3HybridSparkStateSummary:
    latest_candidate = _latest_event_payload(state, "hybrid_spark_candidate")
    stabilization = _mapping_or_empty(
        state.cached_quantities.get("last_child_basin_stabilization")
    )
    candidate_count = int(state.cached_quantities.get("hybrid_spark_candidate_count", 0))
    live_node_count = len(tuple(state.topology.iter_live_node_ids()))
    evaluated_candidate_count = live_node_count if "hybrid_spark_candidate_count" in state.cached_quantities else None
    candidate_pass_rate = None
    if evaluated_candidate_count and evaluated_candidate_count > 0:
        candidate_pass_rate = float(candidate_count / evaluated_candidate_count)

    return GRC9V3HybridSparkStateSummary(
        hybrid_spark_candidate_count=candidate_count,
        completed_hybrid_spark_count=_event_count(state, "hybrid_spark_completed"),
        last_candidate_saturation_gate=_optional_bool(
            latest_candidate.get("saturation_gate")
        ),
        last_candidate_basin_interior_gate=_optional_bool(
            latest_candidate.get("basin_interior_gate")
        ),
        last_candidate_signed_hessian_gate=_optional_bool(
            latest_candidate.get("signed_hessian_degeneracy_gate")
        ),
        last_child_stabilization_pass=_optional_bool(
            stabilization.get("stabilization_pass")
        ),
        signed_crossing_status=_optional_string(
            state.cached_quantities.get("hybrid_spark_signed_crossing_status")
        ),
        last_candidate_spark_lane=_optional_string(latest_candidate.get("spark_lane")),
        last_candidate_gradient_norm=_optional_float(latest_candidate.get("gradient_norm")),
        last_candidate_min_signed_hessian=_optional_float(
            latest_candidate.get("min_signed_hessian")
        ),
        last_candidate_column_h=tuple(
            float(value) for value in _sequence_or_empty(latest_candidate.get("column_h"))
        ),
        last_candidate_min_abs_column_h=_optional_float(
            latest_candidate.get("min_abs_column_h")
        ),
        last_candidate_min_abs_column_h_column=_optional_int(
            latest_candidate.get("min_abs_column_h_column")
        ),
        last_candidate_column_h_branch_hit=_optional_bool(
            latest_candidate.get("column_h_branch_hit")
        ),
        last_candidate_column_h_gate_reasons=tuple(
            str(value) for value in _sequence_or_empty(latest_candidate.get("gate_reasons"))
        ),
        evaluated_candidate_count=evaluated_candidate_count,
        candidate_pass_rate=candidate_pass_rate,
        candidate_failure_reason=(
            "no_candidate_recorded"
            if evaluated_candidate_count is not None and candidate_count == 0
            else None
        ),
        last_stabilized_child_node_ids=tuple(
            int(value) for value in _sequence_or_empty(stabilization.get("stabilized_child_node_ids"))
        ),
        last_module_sink_node_ids=tuple(
            int(value) for value in _sequence_or_empty(stabilization.get("module_sink_nodes"))
        ),
    )


def _build_hierarchy_state(state: GRC9V3State) -> GRC9V3HierarchyStateSummary:
    completed = _mapping_or_empty(state.cached_quantities.get("last_completed_hybrid_spark"))
    return GRC9V3HierarchyStateSummary(
        hierarchy_root_count=len(state.hierarchy),
        hierarchy_child_link_count=sum(len(children) for children in state.hierarchy.values()),
        max_hierarchy_depth=max(
            (int(node.depth) for node in state.nodes.values()),
            default=0,
        ),
        last_hierarchy_parent=_optional_string(completed.get("hierarchy_parent")),
        last_hierarchy_children=tuple(
            str(value) for value in _sequence_or_empty(completed.get("hierarchy_children"))
        ),
    )


def _build_choice_collapse(
    state: GRC9V3State,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
) -> GRC9V3ChoiceCollapseSummary:
    score_params = _mapping_or_empty(evolution.get("compatibility_score_params"))
    choice_state = _mapping_or_empty(state.cached_quantities.get("choice_state"))
    evaluated_nodes = _mapping_or_empty(choice_state.get("evaluated_nodes"))
    learning_state = _mapping_or_empty(state.cached_quantities.get("choice_learning_state"))
    last_choice = _latest_event_payload(state, "choice_detected")
    last_collapse = _latest_event_payload(state, "collapse")

    return GRC9V3ChoiceCollapseSummary(
        choice_backend=str(modes.get("choice_backend", "sink_compatibility")),
        choice_regime_count=len(state.choice_registry),
        collapse_registry_count=len(state.collapse_registry),
        evaluated_node_count=len(evaluated_nodes),
        learning_state_count=len(learning_state),
        last_choice_node_id=_optional_int(last_choice.get("node_id")),
        last_collapse_node_id=_optional_int(last_collapse.get("node_id")),
        last_collapsed_sink_id=last_collapse.get("collapsed_sink_id"),
        epsilon_choice=_optional_float(score_params.get("epsilon_choice")),
        epsilon_collapse=_optional_float(score_params.get("epsilon_collapse")),
    )


def _build_growth_state(state: GRC9V3State) -> GRC9V3GrowthStateSummary:
    growth_events = [
        payload
        for payload in _sequence_or_empty(state.cached_quantities.get("last_growth_events"))
        if isinstance(payload, Mapping)
    ]
    latest = growth_events[-1] if growth_events else {}
    return GRC9V3GrowthStateSummary(
        birth_rule_mode=str(state.cached_quantities.get("birth_rule_mode", "unavailable")),
        parent_selection_mode=str(
            state.cached_quantities.get("birth_parent_selection_mode", "unavailable")
        ),
        growth_event_count=len(growth_events),
        last_parent_node_id=_optional_int(latest.get("parent_node_id")),
        last_child_node_id=_optional_int(latest.get("child_node_id")),
        last_birth_probability=_optional_float(latest.get("birth_probability")),
        last_outward_flux_pressure=_optional_float(latest.get("outward_flux_pressure")),
    )


def _build_budget_correction(
    state: GRC9V3State,
    modes: Mapping[str, Any],
) -> GRC9V3BudgetCorrectionSummary:
    budget_summary = _mapping_or_empty(state.cached_quantities.get("last_quadrature_budget"))
    current_budget = float(sum(node.coherence for node in state.nodes.values()))
    target = float(state.budget_target if state.budget_target != 0.0 else current_budget)
    budget_before = float(budget_summary.get("budget_before", current_budget))
    budget_after = float(budget_summary.get("budget_after", current_budget))
    return GRC9V3BudgetCorrectionSummary(
        quadrature_mode=str(
            budget_summary.get(
                "quadrature_mode",
                modes.get("quadrature_mode", "unit_measure"),
            )
        ),
        budget_correction_method=str(
            budget_summary.get(
                "budget_correction_method",
                modes.get("budget_correction_method", "simplex_projection"),
            )
        ),
        budget_target=float(budget_summary.get("budget_target", target)),
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=float(budget_summary.get("budget_error", budget_after - target)),
        negative_mass_correction=float(budget_summary.get("negative_mass_correction", 0.0)),
        post_expansion_budget_check_available=isinstance(
            state.cached_quantities.get("post_expansion_budget_check"),
            Mapping,
        ),
        budget_target_source=_optional_string(
            state.cached_quantities.get("budget_target_source")
        ),
    )


def _build_coarse_cache(state: GRC9V3State) -> GRC9V3CoarseCacheSummary:
    invalidated = bool(state.cached_quantities.get("coarse_cache_invalidated", False))
    reason = str(state.cached_quantities.get("coarse_cache_invalidation_reason", "none"))
    cache_state = "empty" if not state.coarse_cache else "warm"
    coarse_fields: set[str] = set()
    coarse_field_types: dict[str, str] = {}
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
            coarse_field_types[field_name] = "unknown"
    return GRC9V3CoarseCacheSummary(
        coarse_cache_state=cache_state,
        coarse_cache_invalidated=invalidated,
        coarse_cache_invalidation_reason=reason,
        coarse_cache_refresh_mode=_optional_string(
            state.cached_quantities.get("coarse_cache_refresh_mode")
        ),
        coarse_fields_list=tuple(sorted(coarse_fields)),
        coarse_field_types=coarse_field_types if coarse_field_types else None,
    )


def _edge_label_selection_name(selection: Any) -> str:
    if selection == "all":
        return "all"
    if isinstance(selection, str):
        return selection
    if isinstance(selection, Sequence):
        return ",".join(str(value) for value in sorted(selection, key=str))
    return str(selection)


def _plain_mapping_or_none(value: Any) -> Mapping[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    return {str(key): str(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))}


def _mapping_or_empty(value: Any) -> Mapping[Any, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_or_empty(value: Any) -> tuple[Any, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return ()
    return tuple(value)


def _float_sequence(value: Any) -> tuple[float, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return ()
    values: list[float] = []
    for item in value:
        try:
            values.append(float(item))
        except (TypeError, ValueError):
            continue
    return tuple(values)


def _float_mapping_values(value: Any) -> tuple[float, ...]:
    if not isinstance(value, Mapping):
        return ()
    return tuple(
        float(inner)
        for _, inner in sorted(value.items(), key=lambda item: str(item[0]))
        if _is_finite_number(inner)
    )


def _float_mapping(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key): float(inner)
        for key, inner in sorted(value.items(), key=lambda item: str(item[0]))
        if _is_finite_number(inner)
    }


def _matrix_rows(value: Any) -> tuple[tuple[float, ...], ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return ()
    rows: list[tuple[float, ...]] = []
    for row in value:
        row_values = _float_sequence(row)
        if row_values:
            rows.append(row_values)
    return tuple(rows)


def _min_or_zero(values: Any) -> float:
    finite = [float(value) for value in values if _is_finite_number(value)]
    return float(min(finite)) if finite else 0.0


def _max_or_zero(values: Any) -> float:
    finite = [float(value) for value in values if _is_finite_number(value)]
    return float(max(finite)) if finite else 0.0


def _mean_or_zero(values: Any) -> float:
    finite = [float(value) for value in values if _is_finite_number(value)]
    return float(sum(finite) / len(finite)) if finite else 0.0


def _is_finite_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, int | float)
        and math.isfinite(float(value))
    )


def _valid_hessian_sign(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value in (-1, 1):
        return int(value)
    return 1


def _top_node_ids(values_by_node: Mapping[int, float], *, limit: int = 5) -> tuple[int, ...]:
    return tuple(
        node_id
        for node_id, _ in sorted(
            values_by_node.items(),
            key=lambda item: (-abs(item[1]), item[0]),
        )[:limit]
    )


def _latest_module_node_ids(state: GRC9V3State) -> tuple[int, ...]:
    if not state.expansion_registry:
        return ()
    _, record = sorted(
        state.expansion_registry.items(),
        key=lambda item: (item[1].expansion_step, item[0]),
    )[-1]
    return tuple(int(node_id) for node_id in record.module_node_ids)


def _latest_event_payload(state: GRC9V3State, kind: str) -> Mapping[str, Any]:
    for event in reversed(state.event_log):
        if event.kind == kind:
            return event.payload if isinstance(event.payload, Mapping) else {}
    return {}


def _event_count(state: GRC9V3State, kind: str) -> int:
    return sum(1 for event in state.event_log if event.kind == kind)


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _optional_float(value: Any) -> float | None:
    return float(value) if _is_finite_number(value) else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _local_port_id(state: GRC9V3State, *, edge_id: int, node_id: int) -> int:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return slot_to_port_id(endpoint_a[1])
    if endpoint_b[0] == node_id:
        return slot_to_port_id(endpoint_b[1])
    raise ValueError(f"edge {edge_id} is not incident to node {node_id}")


def _successor_tie_count(state: GRC9V3State) -> int:
    tie_count = 0
    for node_id in sorted(state.topology.iter_live_node_ids()):
        positive_outflows: list[float] = []
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            edge = state.port_edges.get(edge_id)
            if edge is None:
                continue
            if edge.node_u == node_id:
                outgoing_flux = float(edge.flux_uv)
            elif edge.node_v == node_id:
                outgoing_flux = float(-edge.flux_uv)
            else:
                continue
            if outgoing_flux > 0.0:
                positive_outflows.append(outgoing_flux)
        if not positive_outflows:
            continue
        max_outflow = max(positive_outflows)
        if sum(1 for value in positive_outflows if abs(value - max_outflow) <= 1e-12) > 1:
            tie_count += 1
    return tie_count


__all__ = [
    "_build_grc9v3_event_extension",
    "_build_grc9v3_event_extensions",
    "_build_grc9v3_run_summary_extension",
    "_build_grc9v3_step_extension",
]

"""Explicit GRC9V3 telemetry extension contracts.

Lane B column-H-assisted fields are optional extensions on the shared
``hybrid_spark_candidate`` event kind. Consumers must use ``spark_lane`` to
distinguish default Lane A candidates from opt-in
``grc9v3_column_h_assisted`` candidates.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from .schema import TelemetryFamilyExtensions


GRC9V3_TELEMETRY_FAMILY = "grc9v3"
GRC9V3_TELEMETRY_CONTRACT_VERSION = "phase_t_grc9v3_iter1_v1"
GRC9V3_COLUMN_H_COMPUTATION_VERSION = "grc9v3_column_h_v1"
GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE = "current_hybrid_signed_hessian"
GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE = "grc9v3_column_h_assisted"
GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION = "v1"
GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_KIND = "hybrid_spark_candidate"
GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_SCHEMA_VERSION = (
    "grc9v3_column_h_assisted_candidate_v1"
)
GRC9V3_COLUMN_H_ASSISTED_ALLOWED_GATE_REASONS = (
    "signed_hessian_hit",
    "column_h_threshold_hit",
    "column_h_sign_crossing_hit",
)
GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_REQUIRED_FIELDS = (
    "event_schema_version",
    "spark_lane_version",
    "candidate_event_id",
    "step_index",
    "state_epoch",
    "column_h_computation_version",
    "spark_lane",
    "node_id",
    "active_degree",
    "require_active_degree_9",
    "sink_status",
    "require_sink_for_column_h_spark",
    "candidate_scope_status",
    "gradient_norm",
    "eps_gradient",
    "signed_hessian_min",
    "eps_signed_hessian",
    "signed_hessian_hit",
    "column_h",
    "min_abs_column_h",
    "min_abs_column_h_column",
    "eps_column_h",
    "column_h_threshold_hit",
    "column_h_sign_crossing_enabled",
    "column_h_sign_crossing_mode",
    "eps_column_h_crossing_zero",
    "previous_column_h_status",
    "previous_column_h_values",
    "column_h_sign_crossing_hit",
    "column_h_sign_crossing_columns",
    "column_h_branch_hit",
    "column_h_gate_hit",
    "lane_b_candidate_hit",
    "gate_reasons",
    "near_saturation_enabled",
    "virtual_stubs_used",
    "linked_expansion_event_id",
)

_AVAILABILITY_STATUSES = frozenset(
    {"artifact_backed", "diagnostic_only", "reserved_future", "out_of_scope"}
)
_OWNERSHIPS = frozenset(
    {"grc9_mechanical", "grcv3_semantic", "grc9v3_hybrid", "shared_runtime"}
)
_EVENT_DOMAINS = frozenset(
    {
        "spark",
        "expansion",
        "choice",
        "collapse",
        "growth",
        "budget",
        "coarse",
        "boundary",
        "other",
    }
)
_LIFECYCLE_STAGES = frozenset(
    {
        "candidate",
        "module_created",
        "completed",
        "detected",
        "resolved",
        "collapsed",
        "child_attached",
        "corrected",
        "invalidated",
        "other",
    }
)


def _validate_non_empty(value: str, *, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} must not be empty")


def _validate_enum(value: str, allowed: frozenset[str], *, field_name: str) -> None:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {tuple(sorted(allowed))}")


def _validate_optional_enum(
    value: str | None, allowed: frozenset[str], *, field_name: str
) -> None:
    if value is not None:
        _validate_enum(value, allowed, field_name=field_name)


def _validate_non_negative_int(value: int, *, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")


def _validate_optional_non_negative_int(value: int | None, *, field_name: str) -> None:
    if value is not None:
        _validate_non_negative_int(value, field_name=field_name)


def _validate_finite_float(value: float, *, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _validate_non_negative_float(value: float, *, field_name: str) -> None:
    _validate_finite_float(value, field_name=field_name)
    if value < 0.0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_optional_finite_float(value: float | None, *, field_name: str) -> None:
    if value is not None:
        _validate_finite_float(value, field_name=field_name)


def _validate_optional_non_negative_float(
    value: float | None, *, field_name: str
) -> None:
    if value is not None:
        _validate_non_negative_float(value, field_name=field_name)


def _validate_non_negative_int_sequence(
    values: Sequence[int], *, field_name: str
) -> None:
    for index, value in enumerate(values):
        _validate_non_negative_int(value, field_name=f"{field_name}[{index}]")


def _validate_finite_float_sequence(values: Sequence[float], *, field_name: str) -> None:
    for index, value in enumerate(values):
        _validate_finite_float(value, field_name=f"{field_name}[{index}]")


def _validate_mapping_non_negative_ints(
    values: Mapping[Any, int], *, field_name: str
) -> None:
    for key, value in values.items():
        _validate_non_negative_int(value, field_name=f"{field_name}[{key!r}]")


def _mapping_with_string_keys(values: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(key): values[key] for key in sorted(values, key=str)}


def _optional_dataclass_payload(instance: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field_name in instance.__dataclass_fields__:
        value = getattr(instance, field_name)
        if value is None:
            continue
        if isinstance(value, tuple):
            payload[field_name] = list(value)
        elif isinstance(value, Mapping):
            payload[field_name] = dict(sorted(value.items(), key=lambda item: str(item[0])))
        else:
            payload[field_name] = value
    return payload


@dataclass(frozen=True)
class GRC9V3LaneContext:
    """Shared lane/provenance context for GRC9V3 telemetry extensions."""

    source_reference: str
    fixture_name: str
    run_role: str
    experiment_id: str | None = None
    representative_lane_name: str | None = None
    source_runtime_artifact: str | None = None
    ownership: str = "shared_runtime"

    def __post_init__(self) -> None:
        for field_name in ("source_reference", "fixture_name", "run_role"):
            _validate_non_empty(getattr(self, field_name), field_name=field_name)
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3BackendConfigTelemetry:
    """Configured backend and policy summary for GRC9V3 telemetry."""

    frame_mode: str
    hessian_backend: str
    curvature_backend: str
    choice_backend: str
    boundary_mode: str
    quadrature_mode: str
    budget_correction_method: str
    expansion_distribution_mode: str
    edge_label_selection: str
    spark_signed_crossing: bool
    spark_lane: str | None = None
    spark_lane_version: str | None = None
    default_evolution_provenance: Mapping[str, str] | None = None
    reserved_modes: Mapping[str, str] | None = None
    ownership: str = "shared_runtime"

    def __post_init__(self) -> None:
        for field_name in (
            "frame_mode",
            "hessian_backend",
            "curvature_backend",
            "choice_backend",
            "boundary_mode",
            "quadrature_mode",
            "budget_correction_method",
            "expansion_distribution_mode",
            "edge_label_selection",
        ):
            _validate_non_empty(getattr(self, field_name), field_name=field_name)
        if not isinstance(self.spark_signed_crossing, bool):
            raise ValueError("spark_signed_crossing must be a boolean")
        if self.spark_lane is not None:
            _validate_non_empty(self.spark_lane, field_name="spark_lane")
        if self.spark_lane_version is not None:
            _validate_non_empty(
                self.spark_lane_version, field_name="spark_lane_version"
            )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3PortChartSummary:
    """Compressed nine-slot port chart summary."""

    num_nodes: int
    num_port_edges: int
    active_degree_histogram: Mapping[int, int]
    inactive_port_count: int
    saturated_node_count: int
    saturated_node_ids_sample: tuple[int, ...]
    row_occupancy_totals: tuple[int, int, int]
    column_occupancy_totals: tuple[int, int, int]
    inactive_capacity_by_node_sample: Mapping[int, int] | None = None
    module_node_count: int | None = None
    ownership: str = "grc9_mechanical"

    def __post_init__(self) -> None:
        for field_name in (
            "num_nodes",
            "num_port_edges",
            "inactive_port_count",
            "saturated_node_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_mapping_non_negative_ints(
            self.active_degree_histogram, field_name="active_degree_histogram"
        )
        for field_name in (
            "saturated_node_ids_sample",
            "row_occupancy_totals",
            "column_occupancy_totals",
        ):
            _validate_non_negative_int_sequence(getattr(self, field_name), field_name=field_name)
        if len(self.row_occupancy_totals) != 3:
            raise ValueError("row_occupancy_totals must contain exactly 3 values")
        if len(self.column_occupancy_totals) != 3:
            raise ValueError("column_occupancy_totals must contain exactly 3 values")
        if self.inactive_capacity_by_node_sample is not None:
            _validate_mapping_non_negative_ints(
                self.inactive_capacity_by_node_sample,
                field_name="inactive_capacity_by_node_sample",
            )
        _validate_optional_non_negative_int(self.module_node_count, field_name="module_node_count")
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = _optional_dataclass_payload(self)
        payload["active_degree_histogram"] = _mapping_with_string_keys(
            self.active_degree_histogram
        )
        if self.inactive_capacity_by_node_sample is not None:
            payload["inactive_capacity_by_node_sample"] = _mapping_with_string_keys(
                self.inactive_capacity_by_node_sample
            )
        return payload


@dataclass(frozen=True)
class GRC9V3RowBasisDifferentialSummary:
    """Compressed GRCV3 semantic differential state in the GRC9V3 row basis."""

    gradient_norm_min: float
    gradient_norm_max: float
    gradient_norm_mean: float
    signed_hessian_min: float
    signed_hessian_max: float
    signed_hessian_mean: float
    current_min_signed_hessian_min: float
    hessian_backend: str
    hessian_sign: int
    previous_min_signed_hessian_available: bool | None = None
    signed_hessian_history_pruned_count: int | None = None
    weighted_least_squares_hessian_available: bool | None = None
    geometric_seed_count: int | None = None
    ownership: str = "grcv3_semantic"

    def __post_init__(self) -> None:
        for field_name in (
            "gradient_norm_min",
            "gradient_norm_max",
            "gradient_norm_mean",
            "signed_hessian_min",
            "signed_hessian_max",
            "signed_hessian_mean",
            "current_min_signed_hessian_min",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        _validate_non_empty(self.hessian_backend, field_name="hessian_backend")
        if self.hessian_sign not in (-1, 1):
            raise ValueError("hessian_sign must be either -1 or 1")
        _validate_optional_non_negative_int(
            self.signed_hessian_history_pruned_count,
            field_name="signed_hessian_history_pruned_count",
        )
        _validate_optional_non_negative_int(
            self.geometric_seed_count, field_name="geometric_seed_count"
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3HybridTensorSummary:
    """Compressed GRC9 Eq. (1) tensor diagnostics in the GRC9V3 row basis."""

    tensor_trace_min: float
    tensor_trace_max: float
    tensor_trace_mean: float
    tensor_anisotropy_max: float
    row_mismatch_sum_max: float
    flux_feedback_sum_mean: float
    tensor_hotspot_node_ids_sample: tuple[int, ...] = ()
    row_mismatch_hotspot_node_ids_sample: tuple[int, ...] = ()
    ownership: str = "grc9v3_hybrid"

    def __post_init__(self) -> None:
        for field_name in (
            "tensor_trace_min",
            "tensor_trace_max",
            "tensor_trace_mean",
            "tensor_anisotropy_max",
            "row_mismatch_sum_max",
            "flux_feedback_sum_mean",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_int_sequence(
            self.tensor_hotspot_node_ids_sample,
            field_name="tensor_hotspot_node_ids_sample",
        )
        _validate_non_negative_int_sequence(
            self.row_mismatch_hotspot_node_ids_sample,
            field_name="row_mismatch_hotspot_node_ids_sample",
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3LabelAvailability:
    """Availability flags for analytic edge labels."""

    geometric_length_available: bool
    temporal_delay_available: bool
    flux_coupling_available: bool

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "geometric_length_available": self.geometric_length_available,
            "temporal_delay_available": self.temporal_delay_available,
            "flux_coupling_available": self.flux_coupling_available,
        }


@dataclass(frozen=True)
class GRC9V3TransportSummary:
    """Compressed transport and analytic label summary."""

    base_conductance_min: float
    base_conductance_max: float
    base_conductance_mean: float
    potential_min: float
    potential_max: float
    flux_abs_sum: float
    positive_flux_edge_count: int
    negative_flux_edge_count: int
    label_availability: GRC9V3LabelAvailability
    label_computation_mode: Mapping[str, str]
    ownership: str = "grc9v3_hybrid"

    def __post_init__(self) -> None:
        for field_name in (
            "base_conductance_min",
            "base_conductance_max",
            "base_conductance_mean",
            "potential_min",
            "potential_max",
            "flux_abs_sum",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        for field_name in ("positive_flux_edge_count", "negative_flux_edge_count"):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "base_conductance_min": self.base_conductance_min,
            "base_conductance_max": self.base_conductance_max,
            "base_conductance_mean": self.base_conductance_mean,
            "potential_min": self.potential_min,
            "potential_max": self.potential_max,
            "flux_abs_sum": self.flux_abs_sum,
            "positive_flux_edge_count": self.positive_flux_edge_count,
            "negative_flux_edge_count": self.negative_flux_edge_count,
            "label_availability": self.label_availability.to_mapping(),
            "label_computation_mode": dict(sorted(self.label_computation_mode.items())),
            "ownership": self.ownership,
        }


@dataclass(frozen=True)
class GRC9V3IdentityBasinSummary:
    """Compressed hybrid identity and basin summary."""

    sink_count: int
    basin_count: int
    basin_size_min: int
    basin_size_max: int
    basin_size_mean: float
    geometric_seed_count: int
    validated_basin_count: int
    successor_self_loop_count: int
    successor_tie_count: int | None = None
    basin_mass_summary: Mapping[str, float] | None = None
    module_sink_count: int | None = None
    daughter_sink_count: int | None = None
    ownership: str = "grc9v3_hybrid"

    def __post_init__(self) -> None:
        for field_name in (
            "sink_count",
            "basin_count",
            "basin_size_min",
            "basin_size_max",
            "geometric_seed_count",
            "validated_basin_count",
            "successor_self_loop_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_float(self.basin_size_mean, field_name="basin_size_mean")
        for field_name in ("successor_tie_count", "module_sink_count", "daughter_sink_count"):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        if self.basin_mass_summary is not None:
            for key, value in self.basin_mass_summary.items():
                _validate_non_negative_float(value, field_name=f"basin_mass_summary[{key!r}]")
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3HybridSparkStateSummary:
    """Compressed hybrid spark candidate/completion state."""

    hybrid_spark_candidate_count: int
    completed_hybrid_spark_count: int
    last_candidate_saturation_gate: bool | None
    last_candidate_basin_interior_gate: bool | None
    last_candidate_signed_hessian_gate: bool | None
    last_child_stabilization_pass: bool | None
    signed_crossing_status: str | None = None
    last_candidate_spark_lane: str | None = None
    last_candidate_gradient_norm: float | None = None
    last_candidate_min_signed_hessian: float | None = None
    last_candidate_column_h: tuple[float, ...] = ()
    last_candidate_min_abs_column_h: float | None = None
    last_candidate_min_abs_column_h_column: int | None = None
    last_candidate_column_h_branch_hit: bool | None = None
    last_candidate_column_h_gate_reasons: tuple[str, ...] = ()
    evaluated_candidate_count: int | None = None
    candidate_pass_rate: float | None = None
    candidate_failure_reason: str | None = None
    last_stabilized_child_node_ids: tuple[int, ...] = ()
    last_module_sink_node_ids: tuple[int, ...] = ()
    ownership: str = "grc9v3_hybrid"

    def __post_init__(self) -> None:
        _validate_non_negative_int(
            self.hybrid_spark_candidate_count,
            field_name="hybrid_spark_candidate_count",
        )
        _validate_non_negative_int(
            self.completed_hybrid_spark_count,
            field_name="completed_hybrid_spark_count",
        )
        _validate_optional_finite_float(
            self.last_candidate_gradient_norm,
            field_name="last_candidate_gradient_norm",
        )
        _validate_optional_finite_float(
            self.last_candidate_min_signed_hessian,
            field_name="last_candidate_min_signed_hessian",
        )
        _validate_finite_float_sequence(
            self.last_candidate_column_h,
            field_name="last_candidate_column_h",
        )
        if self.last_candidate_column_h and len(self.last_candidate_column_h) != 3:
            raise ValueError("last_candidate_column_h must contain exactly three values")
        _validate_optional_finite_float(
            self.last_candidate_min_abs_column_h,
            field_name="last_candidate_min_abs_column_h",
        )
        _validate_optional_non_negative_int(
            self.last_candidate_min_abs_column_h_column,
            field_name="last_candidate_min_abs_column_h_column",
        )
        _validate_optional_non_negative_int(
            self.evaluated_candidate_count, field_name="evaluated_candidate_count"
        )
        _validate_optional_non_negative_float(
            self.candidate_pass_rate, field_name="candidate_pass_rate"
        )
        if self.candidate_pass_rate is not None and self.candidate_pass_rate > 1.0:
            raise ValueError("candidate_pass_rate must be <= 1")
        _validate_non_negative_int_sequence(
            self.last_stabilized_child_node_ids,
            field_name="last_stabilized_child_node_ids",
        )
        _validate_non_negative_int_sequence(
            self.last_module_sink_node_ids,
            field_name="last_module_sink_node_ids",
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3HierarchyStateSummary:
    """Compressed hierarchy state for GRC9V3 telemetry."""

    hierarchy_root_count: int
    hierarchy_child_link_count: int
    max_hierarchy_depth: int
    last_hierarchy_parent: str | None = None
    last_hierarchy_children: tuple[str, ...] = ()
    ownership: str = "grcv3_semantic"

    def __post_init__(self) -> None:
        for field_name in (
            "hierarchy_root_count",
            "hierarchy_child_link_count",
            "max_hierarchy_depth",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3ChoiceCollapseSummary:
    """Compressed choice/collapse state for GRC9V3 telemetry."""

    choice_backend: str
    choice_regime_count: int
    collapse_registry_count: int
    evaluated_node_count: int
    learning_state_count: int
    last_choice_node_id: int | None = None
    last_collapse_node_id: int | None = None
    last_collapsed_sink_id: str | int | None = None
    epsilon_choice: float | None = None
    epsilon_collapse: float | None = None
    ownership: str = "grcv3_semantic"

    def __post_init__(self) -> None:
        _validate_non_empty(self.choice_backend, field_name="choice_backend")
        for field_name in (
            "choice_regime_count",
            "collapse_registry_count",
            "evaluated_node_count",
            "learning_state_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_optional_non_negative_int(
            self.last_choice_node_id, field_name="last_choice_node_id"
        )
        _validate_optional_non_negative_int(
            self.last_collapse_node_id, field_name="last_collapse_node_id"
        )
        _validate_optional_non_negative_float(self.epsilon_choice, field_name="epsilon_choice")
        _validate_optional_non_negative_float(
            self.epsilon_collapse, field_name="epsilon_collapse"
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3GrowthStateSummary:
    """Compressed inactive-port growth state."""

    birth_rule_mode: str
    parent_selection_mode: str
    growth_event_count: int
    last_parent_node_id: int | None = None
    last_child_node_id: int | None = None
    last_birth_probability: float | None = None
    last_outward_flux_pressure: float | None = None
    ownership: str = "grc9_mechanical"

    def __post_init__(self) -> None:
        _validate_non_empty(self.birth_rule_mode, field_name="birth_rule_mode")
        _validate_non_empty(self.parent_selection_mode, field_name="parent_selection_mode")
        _validate_non_negative_int(self.growth_event_count, field_name="growth_event_count")
        for field_name in ("last_parent_node_id", "last_child_node_id"):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_optional_non_negative_float(
            self.last_birth_probability, field_name="last_birth_probability"
        )
        _validate_optional_non_negative_float(
            self.last_outward_flux_pressure, field_name="last_outward_flux_pressure"
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3BudgetCorrectionSummary:
    """Compressed quadrature budget closure summary."""

    quadrature_mode: str
    budget_correction_method: str
    budget_target: float
    budget_before: float
    budget_after: float
    budget_error: float
    negative_mass_correction: float
    post_expansion_budget_check_available: bool | None = None
    budget_target_source: str | None = None
    ownership: str = "grcv3_semantic"

    def __post_init__(self) -> None:
        _validate_non_empty(self.quadrature_mode, field_name="quadrature_mode")
        _validate_non_empty(
            self.budget_correction_method, field_name="budget_correction_method"
        )
        for field_name in (
            "budget_target",
            "budget_before",
            "budget_after",
            "budget_error",
            "negative_mass_correction",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3CoarseCacheSummary:
    """Compressed coarse-cache hygiene state."""

    coarse_cache_state: str
    coarse_cache_invalidated: bool
    coarse_cache_invalidation_reason: str
    coarse_cache_refresh_mode: str | None = None
    coarse_fields_list: tuple[str, ...] = ()
    coarse_field_types: Mapping[str, str] | None = None
    ownership: str = "shared_runtime"

    def __post_init__(self) -> None:
        _validate_non_empty(self.coarse_cache_state, field_name="coarse_cache_state")
        _validate_non_empty(
            self.coarse_cache_invalidation_reason,
            field_name="coarse_cache_invalidation_reason",
        )
        if not isinstance(self.coarse_cache_invalidated, bool):
            raise ValueError("coarse_cache_invalidated must be a boolean")
        for field_name in self.coarse_fields_list:
            _validate_non_empty(field_name, field_name="coarse_fields_list item")
        if self.coarse_field_types is not None:
            for field_name, field_type in self.coarse_field_types.items():
                _validate_non_empty(field_name, field_name="coarse_field_types key")
                _validate_non_empty(
                    field_type,
                    field_name=f"coarse_field_types[{field_name!r}]",
                )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3StepTelemetryExtension:
    """Canonical GRC9V3 family-extension payload for step rows."""

    lane_context: GRC9V3LaneContext
    backend_config: GRC9V3BackendConfigTelemetry
    port_chart: GRC9V3PortChartSummary
    row_basis_differential: GRC9V3RowBasisDifferentialSummary
    hybrid_tensor: GRC9V3HybridTensorSummary
    transport: GRC9V3TransportSummary
    identity_basin: GRC9V3IdentityBasinSummary
    hybrid_spark_state: GRC9V3HybridSparkStateSummary
    hierarchy_state: GRC9V3HierarchyStateSummary
    choice_collapse: GRC9V3ChoiceCollapseSummary
    growth_state: GRC9V3GrowthStateSummary
    budget_correction: GRC9V3BudgetCorrectionSummary
    coarse_cache: GRC9V3CoarseCacheSummary
    contract_version: str = GRC9V3_TELEMETRY_CONTRACT_VERSION

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "contract_version": self.contract_version,
            "lane_context": self.lane_context.to_mapping(),
            "backend_config": self.backend_config.to_mapping(),
            "port_chart": self.port_chart.to_mapping(),
            "row_basis_differential": self.row_basis_differential.to_mapping(),
            "hybrid_tensor": self.hybrid_tensor.to_mapping(),
            "transport": self.transport.to_mapping(),
            "identity_basin": self.identity_basin.to_mapping(),
            "hybrid_spark_state": self.hybrid_spark_state.to_mapping(),
            "hierarchy_state": self.hierarchy_state.to_mapping(),
            "choice_collapse": self.choice_collapse.to_mapping(),
            "growth_state": self.growth_state.to_mapping(),
            "budget_correction": self.budget_correction.to_mapping(),
            "coarse_cache": self.coarse_cache.to_mapping(),
        }


@dataclass(frozen=True)
class GRC9V3SparkEvidence:
    """Hybrid spark candidate evidence for event rows."""

    candidate_node_id: int | None = None
    sink_node_id: int | None = None
    spark_lane: str | None = None
    active_degree: int | None = None
    saturation_gate: bool | None = None
    basin_interior_gate: bool | None = None
    gradient_norm: float | None = None
    signed_hessian_degeneracy_gate: bool | None = None
    min_signed_hessian: float | None = None
    signed_crossing_enabled: bool | None = None
    signed_crossing_gate: bool | None = None
    column_h: tuple[float, ...] = ()
    min_abs_column_h: float | None = None
    min_abs_column_h_column: int | None = None
    column_h_threshold_hit: bool | None = None
    column_h_sign_crossing_enabled: bool | None = None
    column_h_sign_crossing_mode: str | None = None
    eps_column_h_crossing_zero: float | None = None
    previous_column_h_status: str | None = None
    previous_column_h_values: tuple[float, ...] = ()
    column_h_sign_crossing_hit: bool | None = None
    column_h_sign_crossing_columns: tuple[int, ...] = ()
    column_h_branch_hit: bool | None = None
    column_h_gate_hit: bool | None = None
    lane_b_candidate_hit: bool | None = None
    gate_reasons: tuple[str, ...] = ()
    depth: int | None = None

    def __post_init__(self) -> None:
        for field_name in ("candidate_node_id", "sink_node_id", "active_degree", "depth"):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_optional_finite_float(self.gradient_norm, field_name="gradient_norm")
        _validate_optional_finite_float(
            self.min_signed_hessian, field_name="min_signed_hessian"
        )
        _validate_finite_float_sequence(self.column_h, field_name="column_h")
        if self.column_h and len(self.column_h) != 3:
            raise ValueError("column_h must contain exactly three values")
        _validate_optional_finite_float(
            self.min_abs_column_h,
            field_name="min_abs_column_h",
        )
        _validate_optional_non_negative_int(
            self.min_abs_column_h_column,
            field_name="min_abs_column_h_column",
        )
        _validate_optional_finite_float(
            self.eps_column_h_crossing_zero,
            field_name="eps_column_h_crossing_zero",
        )
        _validate_finite_float_sequence(
            self.previous_column_h_values,
            field_name="previous_column_h_values",
        )
        if self.previous_column_h_values and len(self.previous_column_h_values) != 3:
            raise ValueError("previous_column_h_values must contain exactly three values")
        _validate_non_negative_int_sequence(
            self.column_h_sign_crossing_columns,
            field_name="column_h_sign_crossing_columns",
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3ExpansionEvidence:
    """Mechanical expansion evidence for event rows."""

    parent_sink_id: int | None = None
    target_effective_degree: int | None = None
    requested_node_count: int | None = None
    module_node_ids: tuple[int, ...] = ()
    internal_edge_ids: tuple[int, ...] = ()
    distribution_weights: tuple[float, ...] = ()
    core_coherence_fraction: float | None = None
    core_coherence: float | None = None
    budget_before: float | None = None
    budget_after: float | None = None
    budget_error: float | None = None
    budget_preservation_path: str | None = None
    reassignment_count: int | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "parent_sink_id",
            "target_effective_degree",
            "requested_node_count",
            "reassignment_count",
        ):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_int_sequence(self.module_node_ids, field_name="module_node_ids")
        _validate_non_negative_int_sequence(self.internal_edge_ids, field_name="internal_edge_ids")
        _validate_finite_float_sequence(self.distribution_weights, field_name="distribution_weights")
        for field_name in (
            "core_coherence_fraction",
            "core_coherence",
            "budget_before",
            "budget_after",
            "budget_error",
        ):
            _validate_optional_finite_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3CompletionEvidence:
    """Completed hybrid spark evidence for event rows."""

    stabilized_child_node_ids: tuple[int, ...] = ()
    stable_child_basin_count: int | None = None
    hierarchy_parent: str | None = None
    hierarchy_children: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_non_negative_int_sequence(
            self.stabilized_child_node_ids, field_name="stabilized_child_node_ids"
        )
        _validate_optional_non_negative_int(
            self.stable_child_basin_count, field_name="stable_child_basin_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3ChoiceCollapseEvidence:
    """Choice/collapse event evidence."""

    node_id: int | None = None
    viable_sink_ids: tuple[str, ...] = ()
    winner_sink_id: str | None = None
    winner_margin: float | None = None
    collapsed_sink_id: str | None = None
    epsilon_choice: float | None = None
    epsilon_collapse: float | None = None
    persistence_mode: str | None = None

    def __post_init__(self) -> None:
        _validate_optional_non_negative_int(self.node_id, field_name="node_id")
        for field_name in ("winner_margin", "epsilon_choice", "epsilon_collapse"):
            _validate_optional_non_negative_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3GrowthEvidence:
    """Growth event evidence."""

    parent_node_id: int | None = None
    child_node_id: int | None = None
    parent_port_id: int | None = None
    child_port_id: int | None = None
    outward_flux_pressure: float | None = None
    birth_probability: float | None = None
    rng_sample: float | None = None
    coherence_transfer: float | None = None

    def __post_init__(self) -> None:
        for field_name in ("parent_node_id", "child_node_id", "parent_port_id", "child_port_id"):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        for field_name in (
            "outward_flux_pressure",
            "birth_probability",
            "rng_sample",
            "coherence_transfer",
        ):
            _validate_optional_non_negative_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3EventTelemetryExtension:
    """Canonical GRC9V3 family-extension payload for event rows."""

    event_domain: str
    lifecycle_stage: str
    ownership: str
    topology_mutation: bool
    hierarchy_mutation: bool
    budget_mutation: bool
    lane_context: GRC9V3LaneContext | None = None
    primary_node_id: int | None = None
    primary_edge_id: int | None = None
    registry_key: str | None = None
    expansion_id: str | None = None
    spark_evidence: GRC9V3SparkEvidence | None = None
    expansion_evidence: GRC9V3ExpansionEvidence | None = None
    completion_evidence: GRC9V3CompletionEvidence | None = None
    choice_collapse_evidence: GRC9V3ChoiceCollapseEvidence | None = None
    growth_evidence: GRC9V3GrowthEvidence | None = None
    contract_version: str = GRC9V3_TELEMETRY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _validate_enum(self.event_domain, _EVENT_DOMAINS, field_name="event_domain")
        _validate_enum(
            self.lifecycle_stage, _LIFECYCLE_STAGES, field_name="lifecycle_stage"
        )
        _validate_enum(self.ownership, _OWNERSHIPS, field_name="ownership")
        for field_name in ("primary_node_id", "primary_edge_id"):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "event_domain": self.event_domain,
            "lifecycle_stage": self.lifecycle_stage,
            "ownership": self.ownership,
            "topology_mutation": self.topology_mutation,
            "hierarchy_mutation": self.hierarchy_mutation,
            "budget_mutation": self.budget_mutation,
        }
        if self.lane_context is not None:
            payload["lane_context"] = self.lane_context.to_mapping()
        for field_name in ("primary_node_id", "primary_edge_id", "registry_key", "expansion_id"):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        for field_name in (
            "spark_evidence",
            "expansion_evidence",
            "completion_evidence",
            "choice_collapse_evidence",
            "growth_evidence",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value.to_mapping()
        return payload


@dataclass(frozen=True)
class GRC9V3LifecycleEventCounts:
    """Fixed lifecycle event-count surface for GRC9V3 run summaries."""

    hybrid_spark_candidate_count: int = 0
    hybrid_mechanical_expansion_count: int = 0
    hybrid_spark_completed_count: int = 0
    choice_detected_count: int = 0
    choice_resolved_count: int = 0
    collapse_count: int = 0
    growth_count: int = 0
    front_capacity_growth_count: int = 0
    pressure_boundary_growth_count: int = 0
    legacy_broad_growth_count: int = 0
    budget_correction_count: int = 0
    coarse_invalidation_count: int = 0
    boundary_event_count: int = 0

    def __post_init__(self) -> None:
        for field_name in self.__dataclass_fields__:
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3AppendixESummary:
    """Representative Appendix E fixture summary for GRC9V3 telemetry."""

    fixture_name: str
    spark_completed: bool
    daughter_sink_count: int
    daughter_sink_node_ids: tuple[int, ...]
    module_basin_mass: Mapping[str, float]
    hierarchy_parent: str
    hierarchy_children: tuple[str, ...]
    budget_preserved: bool
    replay_digest_match: bool

    def __post_init__(self) -> None:
        _validate_non_empty(self.fixture_name, field_name="fixture_name")
        _validate_non_negative_int(self.daughter_sink_count, field_name="daughter_sink_count")
        _validate_non_negative_int_sequence(
            self.daughter_sink_node_ids, field_name="daughter_sink_node_ids"
        )
        for key, value in self.module_basin_mass.items():
            _validate_non_negative_float(value, field_name=f"module_basin_mass[{key!r}]")
        _validate_non_empty(self.hierarchy_parent, field_name="hierarchy_parent")

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9V3RunSummaryExtension:
    """Canonical GRC9V3 family-extension payload for run summaries."""

    lane_context: GRC9V3LaneContext
    backend_summary: GRC9V3BackendConfigTelemetry
    final_port_chart_summary: GRC9V3PortChartSummary
    final_differential_summary: GRC9V3RowBasisDifferentialSummary
    final_identity_basin_summary: GRC9V3IdentityBasinSummary
    final_hierarchy_summary: GRC9V3HierarchyStateSummary
    final_choice_collapse_summary: GRC9V3ChoiceCollapseSummary
    final_budget_summary: GRC9V3BudgetCorrectionSummary
    lifecycle_event_counts: GRC9V3LifecycleEventCounts
    representative_appendix_e_summary: GRC9V3AppendixESummary | None = None
    contract_version: str = GRC9V3_TELEMETRY_CONTRACT_VERSION

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "lane_context": self.lane_context.to_mapping(),
            "backend_summary": self.backend_summary.to_mapping(),
            "final_port_chart_summary": self.final_port_chart_summary.to_mapping(),
            "final_differential_summary": self.final_differential_summary.to_mapping(),
            "final_identity_basin_summary": self.final_identity_basin_summary.to_mapping(),
            "final_hierarchy_summary": self.final_hierarchy_summary.to_mapping(),
            "final_choice_collapse_summary": self.final_choice_collapse_summary.to_mapping(),
            "final_budget_summary": self.final_budget_summary.to_mapping(),
            "lifecycle_event_counts": self.lifecycle_event_counts.to_mapping(),
        }
        if self.representative_appendix_e_summary is not None:
            payload["representative_appendix_e_summary"] = (
                self.representative_appendix_e_summary.to_mapping()
            )
        return payload


def _ownership_for_event(domain: str, stage: str) -> str:
    if (domain, stage) in {
        ("spark", "candidate"),
        ("spark", "completed"),
    }:
        return "grc9v3_hybrid"
    if (domain, stage) in {
        ("expansion", "module_created"),
        ("growth", "child_attached"),
    }:
        return "grc9_mechanical"
    if domain in {"choice", "collapse", "budget"}:
        return "grcv3_semantic"
    return "shared_runtime"


def classify_grc9v3_event_extension(
    event_kind: str,
    payload: Mapping[str, Any],
    *,
    lane_context: GRC9V3LaneContext | None = None,
) -> GRC9V3EventTelemetryExtension:
    """Classify a raw GRC9V3 event into the stable telemetry taxonomy."""

    domain = "other"
    stage = "other"
    topology_mutation = False
    hierarchy_mutation = False
    budget_mutation = False
    spark_evidence = None
    expansion_evidence = None
    completion_evidence = None
    choice_collapse_evidence = None
    growth_evidence = None

    if event_kind == "hybrid_spark_candidate":
        domain, stage = "spark", "candidate"
        spark_evidence = GRC9V3SparkEvidence(
            candidate_node_id=_coerce_optional_int(payload.get("candidate_node_id")),
            sink_node_id=_coerce_optional_int(payload.get("sink_node_id")),
            spark_lane=_coerce_optional_string(payload.get("spark_lane")),
            active_degree=_coerce_optional_int(payload.get("active_degree")),
            saturation_gate=_coerce_optional_bool(payload.get("saturation_gate")),
            basin_interior_gate=_coerce_optional_bool(payload.get("basin_interior_gate")),
            gradient_norm=_coerce_optional_float(payload.get("gradient_norm")),
            signed_hessian_degeneracy_gate=_coerce_optional_bool(
                payload.get("signed_hessian_degeneracy_gate")
            ),
            min_signed_hessian=_coerce_optional_float(payload.get("min_signed_hessian")),
            signed_crossing_enabled=_coerce_optional_bool(
                payload.get("signed_crossing_enabled")
            ),
            signed_crossing_gate=_coerce_optional_bool(payload.get("signed_crossing_gate")),
            column_h=tuple(float(value) for value in payload.get("column_h", ())),
            min_abs_column_h=_coerce_optional_float(payload.get("min_abs_column_h")),
            min_abs_column_h_column=_coerce_optional_int(
                payload.get("min_abs_column_h_column")
            ),
            column_h_threshold_hit=_coerce_optional_bool(
                payload.get("column_h_threshold_hit")
            ),
            column_h_sign_crossing_enabled=_coerce_optional_bool(
                payload.get("column_h_sign_crossing_enabled")
            ),
            column_h_sign_crossing_mode=_coerce_optional_string(
                payload.get("column_h_sign_crossing_mode")
            ),
            eps_column_h_crossing_zero=_coerce_optional_float(
                payload.get("eps_column_h_crossing_zero")
            ),
            previous_column_h_status=_coerce_optional_string(
                payload.get("previous_column_h_status")
            ),
            previous_column_h_values=tuple(
                float(value) for value in payload.get("previous_column_h_values") or ()
            ),
            column_h_sign_crossing_hit=_coerce_optional_bool(
                payload.get("column_h_sign_crossing_hit")
            ),
            column_h_sign_crossing_columns=tuple(
                int(value) for value in payload.get("column_h_sign_crossing_columns", ())
            ),
            column_h_branch_hit=_coerce_optional_bool(payload.get("column_h_branch_hit")),
            column_h_gate_hit=_coerce_optional_bool(payload.get("column_h_gate_hit")),
            lane_b_candidate_hit=_coerce_optional_bool(payload.get("lane_b_candidate_hit")),
            gate_reasons=tuple(str(value) for value in payload.get("gate_reasons", ())),
            depth=_coerce_optional_int(payload.get("depth")),
        )
    elif event_kind == "hybrid_mechanical_expansion":
        domain, stage = "expansion", "module_created"
        topology_mutation = True
        budget_mutation = True
        expansion_evidence = GRC9V3ExpansionEvidence(
            parent_sink_id=_coerce_optional_int(payload.get("sink_node_id")),
            target_effective_degree=_coerce_optional_int(
                payload.get("target_effective_degree")
            ),
            requested_node_count=_coerce_optional_int(payload.get("requested_node_count")),
            module_node_ids=tuple(int(value) for value in payload.get("module_node_ids", ())),
            internal_edge_ids=tuple(int(value) for value in payload.get("internal_edge_ids", ())),
            distribution_weights=tuple(
                float(value) for value in payload.get("distribution_weights", ())
            ),
            core_coherence_fraction=_coerce_optional_float(
                payload.get("core_coherence_fraction")
            ),
            core_coherence=_coerce_optional_float(payload.get("core_coherence")),
            budget_before=_coerce_optional_float(payload.get("budget_before")),
            budget_after=_coerce_optional_float(payload.get("budget_after")),
            budget_error=_coerce_optional_float(payload.get("budget_error")),
            budget_preservation_path=_coerce_optional_string(
                payload.get("budget_preservation_path")
            ),
            reassignment_count=len(payload.get("reassignment_map", {}))
            if isinstance(payload.get("reassignment_map", {}), Mapping)
            else None,
        )
    elif event_kind == "hybrid_spark_completed":
        domain, stage = "spark", "completed"
        hierarchy_mutation = True
        completion_evidence = GRC9V3CompletionEvidence(
            stabilized_child_node_ids=tuple(
                int(value) for value in payload.get("stabilized_child_node_ids", ())
            ),
            stable_child_basin_count=_coerce_optional_int(
                payload.get("stable_child_basin_count")
            ),
            hierarchy_parent=_coerce_optional_string(payload.get("hierarchy_parent")),
            hierarchy_children=tuple(str(value) for value in payload.get("hierarchy_children", ())),
        )
    elif event_kind in {"choice_detected", "choice_resolved", "collapse"}:
        domain = "collapse" if event_kind == "collapse" else "choice"
        stage = {
            "choice_detected": "detected",
            "choice_resolved": "resolved",
            "collapse": "collapsed",
        }[event_kind]
        hierarchy_mutation = event_kind == "collapse"
        choice_collapse_evidence = GRC9V3ChoiceCollapseEvidence(
            node_id=_coerce_optional_int(payload.get("node_id")),
            viable_sink_ids=tuple(str(value) for value in payload.get("viable_sink_ids", ())),
            winner_sink_id=_coerce_optional_string(payload.get("winner_sink_id")),
            winner_margin=_coerce_optional_float(payload.get("winner_margin")),
            collapsed_sink_id=_coerce_optional_string(payload.get("collapsed_sink_id")),
            epsilon_choice=_coerce_optional_float(payload.get("epsilon_choice")),
            epsilon_collapse=_coerce_optional_float(payload.get("epsilon_collapse")),
            persistence_mode=_coerce_optional_string(payload.get("persistence_mode")),
        )
    elif event_kind == "growth":
        domain, stage = "growth", "child_attached"
        topology_mutation = True
        budget_mutation = True
        growth_evidence = GRC9V3GrowthEvidence(
            parent_node_id=_coerce_optional_int(payload.get("parent_node_id")),
            child_node_id=_coerce_optional_int(payload.get("child_node_id")),
            parent_port_id=_coerce_optional_int(payload.get("parent_port_id")),
            child_port_id=_coerce_optional_int(payload.get("child_port_id")),
            outward_flux_pressure=_coerce_optional_float(payload.get("outward_flux_pressure")),
            birth_probability=_coerce_optional_float(payload.get("birth_probability")),
            rng_sample=_coerce_optional_float(payload.get("rng_sample")),
            coherence_transfer=_coerce_optional_float(payload.get("coherence_transfer")),
        )

    return GRC9V3EventTelemetryExtension(
        event_domain=domain,
        lifecycle_stage=stage,
        ownership=_ownership_for_event(domain, stage),
        topology_mutation=topology_mutation,
        hierarchy_mutation=hierarchy_mutation,
        budget_mutation=budget_mutation,
        lane_context=lane_context,
        primary_node_id=_primary_node_id_for_event(payload),
        primary_edge_id=_coerce_optional_int(payload.get("primary_edge_id")),
        registry_key=_coerce_optional_string(payload.get("registry_key")),
        expansion_id=_coerce_optional_string(payload.get("expansion_id")),
        spark_evidence=spark_evidence,
        expansion_evidence=expansion_evidence,
        completion_evidence=completion_evidence,
        choice_collapse_evidence=choice_collapse_evidence,
        growth_evidence=growth_evidence,
    )


def _primary_node_id_for_event(payload: Mapping[str, Any]) -> int | None:
    for key in (
        "candidate_node_id",
        "sink_node_id",
        "node_id",
        "parent_node_id",
        "child_node_id",
    ):
        value = _coerce_optional_int(payload.get(key))
        if value is not None:
            return value
    return None


def _coerce_optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _coerce_optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float) and math.isfinite(float(value)):
        return float(value)
    return None


def _coerce_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _coerce_optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def grc9v3_step_family_extensions(
    extension: GRC9V3StepTelemetryExtension,
) -> TelemetryFamilyExtensions:
    """Wrap one GRC9V3 step extension under the family key."""

    return {GRC9V3_TELEMETRY_FAMILY: extension.to_mapping()}


def grc9v3_event_family_extensions(
    extension: GRC9V3EventTelemetryExtension,
) -> TelemetryFamilyExtensions:
    """Wrap one GRC9V3 event extension under the family key."""

    return {GRC9V3_TELEMETRY_FAMILY: extension.to_mapping()}


def grc9v3_run_summary_family_extensions(
    extension: GRC9V3RunSummaryExtension,
) -> TelemetryFamilyExtensions:
    """Wrap one GRC9V3 run-summary extension under the family key."""

    return {GRC9V3_TELEMETRY_FAMILY: extension.to_mapping()}


__all__ = [
    "GRC9V3_COLUMN_H_ASSISTED_ALLOWED_GATE_REASONS",
    "GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_KIND",
    "GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_SCHEMA_VERSION",
    "GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_REQUIRED_FIELDS",
    "GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE",
    "GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION",
    "GRC9V3_COLUMN_H_COMPUTATION_VERSION",
    "GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE",
    "GRC9V3_TELEMETRY_CONTRACT_VERSION",
    "GRC9V3_TELEMETRY_FAMILY",
    "GRC9V3AppendixESummary",
    "GRC9V3BackendConfigTelemetry",
    "GRC9V3BudgetCorrectionSummary",
    "GRC9V3ChoiceCollapseEvidence",
    "GRC9V3ChoiceCollapseSummary",
    "GRC9V3CoarseCacheSummary",
    "GRC9V3CompletionEvidence",
    "GRC9V3EventTelemetryExtension",
    "GRC9V3ExpansionEvidence",
    "GRC9V3GrowthEvidence",
    "GRC9V3GrowthStateSummary",
    "GRC9V3HierarchyStateSummary",
    "GRC9V3HybridSparkStateSummary",
    "GRC9V3HybridTensorSummary",
    "GRC9V3IdentityBasinSummary",
    "GRC9V3LabelAvailability",
    "GRC9V3LaneContext",
    "GRC9V3LifecycleEventCounts",
    "GRC9V3PortChartSummary",
    "GRC9V3RowBasisDifferentialSummary",
    "GRC9V3RunSummaryExtension",
    "GRC9V3SparkEvidence",
    "GRC9V3StepTelemetryExtension",
    "GRC9V3TransportSummary",
    "classify_grc9v3_event_extension",
    "grc9v3_event_family_extensions",
    "grc9v3_run_summary_family_extensions",
    "grc9v3_step_family_extensions",
]

"""Explicit GRC9 telemetry extension contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from .schema import TelemetryFamilyExtensions


GRC9_TELEMETRY_FAMILY = "grc9"
GRC9_TELEMETRY_CONTRACT_VERSION = "phase_t_grc9_iter1_v1"

GRC9_ABUNDANCE_CONTRACT = "topology_updated_current_flux_diagnostic"
GRC9_LANDSCAPE_LOWERING_MODE = "structural_graph_graft_v1"

_AVAILABILITY_STATUSES = frozenset(
    {"artifact_backed", "diagnostic_only", "reserved_future", "out_of_scope"}
)
_EVENT_DOMAINS = frozenset(
    {"spark", "expansion", "growth", "coarse", "budget", "boundary", "other"}
)
_LIFECYCLE_STAGES = frozenset(
    {
        "candidate",
        "confirmed",
        "fission_confirmed",
        "module_created",
        "boundary_reassigned",
        "child_attached",
        "invalidated",
        "corrected",
        "other",
    }
)
_EXPANSION_SCHEDULES = frozenset({"instantaneous", "adiabatic"})
_SIGNED_FLUX_MODES = frozenset({"signed_flux_split", "signed_lossless", "signed_compressed", "none"})
_COARSE_FIELD_TYPES = frozenset({"nonnegative", "signed_lossless", "signed_compressed"})
_PROFILE_COMPRESSION_MODES = frozenset({"full", "dominant_index_residual", "custom"})


def _validate_non_negative_int(value: int, *, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")


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


def _validate_optional_non_negative_int(value: int | None, *, field_name: str) -> None:
    if value is not None:
        _validate_non_negative_int(value, field_name=field_name)


def _validate_non_negative_int_sequence(
    values: Sequence[int], *, field_name: str, expected_len: int | None = None
) -> None:
    if expected_len is not None and len(values) != expected_len:
        raise ValueError(f"{field_name} must contain exactly {expected_len} values")
    for index, value in enumerate(values):
        _validate_non_negative_int(value, field_name=f"{field_name}[{index}]")


def _validate_finite_float_sequence(
    values: Sequence[float], *, field_name: str, expected_len: int | None = None
) -> None:
    if expected_len is not None and len(values) != expected_len:
        raise ValueError(f"{field_name} must contain exactly {expected_len} values")
    for index, value in enumerate(values):
        _validate_finite_float(value, field_name=f"{field_name}[{index}]")


def _validate_mapping_non_negative_ints(
    values: Mapping[Any, int], *, field_name: str
) -> None:
    for key, value in values.items():
        _validate_non_negative_int(value, field_name=f"{field_name}[{key!r}]")


def _validate_enum(value: str, allowed: frozenset[str], *, field_name: str) -> None:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {tuple(sorted(allowed))}")


def _validate_non_empty(value: str, *, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} must not be empty")


def _mapping_with_string_keys(values: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(key): values[key] for key in sorted(values, key=str)}


def _optional_sequence(values: Sequence[Any] | None) -> list[Any] | None:
    if values is None:
        return None
    return list(values)


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


@dataclass(frozen=True)
class GRC9LaneContext:
    """Shared lane/provenance context for GRC9 telemetry extensions."""

    abundance_contract: str = GRC9_ABUNDANCE_CONTRACT
    source_reference: str = ""
    lane_name: str | None = None
    role: str | None = None
    profile_name: str | None = None
    seed_source_reference: str | None = None
    source_lowering_mode: str | None = None

    def __post_init__(self) -> None:
        if not self.source_reference:
            raise ValueError("source_reference must not be empty")
        if self.source_lowering_mode is not None and not self.source_lowering_mode:
            raise ValueError("source_lowering_mode must not be empty when provided")

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "abundance_contract": self.abundance_contract,
            "source_reference": self.source_reference,
        }
        for field_name in (
            "lane_name",
            "role",
            "profile_name",
            "seed_source_reference",
            "source_lowering_mode",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload


@dataclass(frozen=True)
class GRC9BackendConfigTelemetry:
    """Backend and configured policy summary for GRC9 telemetry."""

    frame_mode: str
    curvature_backend: str
    metric_backend: str
    spark_backend: str
    birth_backend: str
    growth_parent_eligibility_mode: str
    coarse_graining_backend: str
    boundary_mode: str
    budget_preservation_policy: str
    expansion_distribution_mode: str
    expansion_schedule: str
    edge_label_selection: str
    source_lowering_mode: str | None = None
    expansion_schedule_tau: int | None = None
    reserved_modes: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "frame_mode",
            "curvature_backend",
            "metric_backend",
            "spark_backend",
            "birth_backend",
            "growth_parent_eligibility_mode",
            "coarse_graining_backend",
            "boundary_mode",
            "budget_preservation_policy",
            "expansion_distribution_mode",
            "edge_label_selection",
        ):
            _validate_non_empty(getattr(self, field_name), field_name=field_name)
        _validate_enum(
            self.expansion_schedule,
            _EXPANSION_SCHEDULES,
            field_name="expansion_schedule",
        )
        _validate_optional_non_negative_int(
            self.expansion_schedule_tau, field_name="expansion_schedule_tau"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "frame_mode": self.frame_mode,
            "curvature_backend": self.curvature_backend,
            "metric_backend": self.metric_backend,
            "spark_backend": self.spark_backend,
            "birth_backend": self.birth_backend,
            "growth_parent_eligibility_mode": self.growth_parent_eligibility_mode,
            "coarse_graining_backend": self.coarse_graining_backend,
            "boundary_mode": self.boundary_mode,
            "budget_preservation_policy": self.budget_preservation_policy,
            "expansion_distribution_mode": self.expansion_distribution_mode,
            "expansion_schedule": self.expansion_schedule,
            "edge_label_selection": self.edge_label_selection,
        }
        if self.source_lowering_mode is not None:
            payload["source_lowering_mode"] = self.source_lowering_mode
        if self.expansion_schedule_tau is not None:
            payload["expansion_schedule_tau"] = self.expansion_schedule_tau
        if self.reserved_modes is not None:
            payload["reserved_modes"] = dict(sorted(self.reserved_modes.items()))
        return payload


@dataclass(frozen=True)
class GRC9PortChartSummary:
    """Compressed nine-slot port chart summary for step telemetry."""

    num_nodes: int
    num_port_edges: int
    active_degree_histogram: Mapping[int, int]
    inactive_port_count: int
    saturated_node_count: int
    near_saturated_node_count: int
    row_occupancy_totals: tuple[int, int, int]
    column_occupancy_totals: tuple[int, int, int]
    saturated_node_ids_sample: tuple[int, ...] = ()
    inactive_capacity_by_column: tuple[int, int, int] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "num_nodes",
            "num_port_edges",
            "inactive_port_count",
            "saturated_node_count",
            "near_saturated_node_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_mapping_non_negative_ints(
            self.active_degree_histogram, field_name="active_degree_histogram"
        )
        _validate_non_negative_int_sequence(
            self.row_occupancy_totals,
            field_name="row_occupancy_totals",
            expected_len=3,
        )
        _validate_non_negative_int_sequence(
            self.column_occupancy_totals,
            field_name="column_occupancy_totals",
            expected_len=3,
        )
        _validate_non_negative_int_sequence(
            self.saturated_node_ids_sample, field_name="saturated_node_ids_sample"
        )
        if self.inactive_capacity_by_column is not None:
            _validate_non_negative_int_sequence(
                self.inactive_capacity_by_column,
                field_name="inactive_capacity_by_column",
                expected_len=3,
            )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "num_nodes": self.num_nodes,
            "num_port_edges": self.num_port_edges,
            "active_degree_histogram": _mapping_with_string_keys(
                self.active_degree_histogram
            ),
            "inactive_port_count": self.inactive_port_count,
            "saturated_node_count": self.saturated_node_count,
            "near_saturated_node_count": self.near_saturated_node_count,
            "row_occupancy_totals": list(self.row_occupancy_totals),
            "column_occupancy_totals": list(self.column_occupancy_totals),
        }
        if self.saturated_node_ids_sample:
            payload["saturated_node_ids_sample"] = list(self.saturated_node_ids_sample)
        if self.inactive_capacity_by_column is not None:
            payload["inactive_capacity_by_column"] = list(
                self.inactive_capacity_by_column
            )
        return payload


@dataclass(frozen=True)
class GRC9RowTensorSummary:
    """Compressed row-basis tensor diagnostics for step telemetry."""

    row_tensor_min: float
    row_tensor_max: float
    row_tensor_mean: float
    row_tensor_anisotropy_max: float
    density_term_mean: float
    row_mismatch_term_max: float
    flux_feedback_term_mean: float
    row_mismatch_hotspots: tuple[Mapping[str, Any], ...] = ()
    row_tensor_by_node_sample: Mapping[int, Sequence[float]] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "row_tensor_min",
            "row_tensor_max",
            "row_tensor_mean",
            "row_tensor_anisotropy_max",
            "density_term_mean",
            "row_mismatch_term_max",
            "flux_feedback_term_mean",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        if self.row_tensor_by_node_sample is not None:
            for node_id, values in self.row_tensor_by_node_sample.items():
                _validate_non_negative_int(node_id, field_name="row_tensor_by_node_sample key")
                _validate_finite_float_sequence(
                    values,
                    field_name=f"row_tensor_by_node_sample[{node_id}]",
                    expected_len=3,
                )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "row_tensor_min": self.row_tensor_min,
            "row_tensor_max": self.row_tensor_max,
            "row_tensor_mean": self.row_tensor_mean,
            "row_tensor_anisotropy_max": self.row_tensor_anisotropy_max,
            "density_term_mean": self.density_term_mean,
            "row_mismatch_term_max": self.row_mismatch_term_max,
            "flux_feedback_term_mean": self.flux_feedback_term_mean,
        }
        if self.row_mismatch_hotspots:
            payload["row_mismatch_hotspots"] = [
                dict(item) for item in self.row_mismatch_hotspots
            ]
        if self.row_tensor_by_node_sample is not None:
            payload["row_tensor_by_node_sample"] = {
                str(node_id): list(values)
                for node_id, values in sorted(self.row_tensor_by_node_sample.items())
            }
        return payload


@dataclass(frozen=True)
class GRC9SparkCalibrationTelemetry:
    """Optional spark-threshold calibration diagnostic."""

    spark_threshold: float
    spark_threshold_mode: str
    burn_in_M_H: float | None = None
    burn_in_M_C: float | None = None

    def __post_init__(self) -> None:
        _validate_non_negative_float(self.spark_threshold, field_name="spark_threshold")
        _validate_non_empty(self.spark_threshold_mode, field_name="spark_threshold_mode")
        _validate_optional_non_negative_float(self.burn_in_M_H, field_name="burn_in_M_H")
        _validate_optional_non_negative_float(self.burn_in_M_C, field_name="burn_in_M_C")

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "spark_threshold": self.spark_threshold,
            "spark_threshold_mode": self.spark_threshold_mode,
        }
        if self.burn_in_M_H is not None:
            payload["burn_in_M_H"] = self.burn_in_M_H
        if self.burn_in_M_C is not None:
            payload["burn_in_M_C"] = self.burn_in_M_C
        return payload


@dataclass(frozen=True)
class GRC9ColumnDiagnosticSummary:
    """Compressed column-diagnostic telemetry for GRC9 sparks and scale."""

    column_diagnostic_min_abs: float
    column_diagnostic_mean_abs: float
    column_proxy_candidate_count: int
    sign_crossing_candidate_count: int
    column_profile_sparsity: float
    column_diagnostic_by_candidate: Mapping[int, Sequence[float]] | None = None
    column_diagnostic_hotspots: tuple[Mapping[str, Any], ...] = ()
    spark_calibration: GRC9SparkCalibrationTelemetry | None = None

    def __post_init__(self) -> None:
        _validate_non_negative_float(
            self.column_diagnostic_min_abs, field_name="column_diagnostic_min_abs"
        )
        _validate_non_negative_float(
            self.column_diagnostic_mean_abs, field_name="column_diagnostic_mean_abs"
        )
        _validate_non_negative_int(
            self.column_proxy_candidate_count, field_name="column_proxy_candidate_count"
        )
        _validate_non_negative_int(
            self.sign_crossing_candidate_count,
            field_name="sign_crossing_candidate_count",
        )
        _validate_non_negative_float(
            self.column_profile_sparsity, field_name="column_profile_sparsity"
        )
        if self.column_diagnostic_by_candidate is not None:
            for node_id, values in self.column_diagnostic_by_candidate.items():
                _validate_non_negative_int(
                    node_id, field_name="column_diagnostic_by_candidate key"
                )
                _validate_finite_float_sequence(
                    values,
                    field_name=f"column_diagnostic_by_candidate[{node_id}]",
                    expected_len=3,
                )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "column_diagnostic_min_abs": self.column_diagnostic_min_abs,
            "column_diagnostic_mean_abs": self.column_diagnostic_mean_abs,
            "column_proxy_candidate_count": self.column_proxy_candidate_count,
            "sign_crossing_candidate_count": self.sign_crossing_candidate_count,
            "column_profile_sparsity": self.column_profile_sparsity,
        }
        if self.column_diagnostic_by_candidate is not None:
            payload["column_diagnostic_by_candidate"] = {
                str(node_id): list(values)
                for node_id, values in sorted(
                    self.column_diagnostic_by_candidate.items()
                )
            }
        if self.column_diagnostic_hotspots:
            payload["column_diagnostic_hotspots"] = [
                dict(item) for item in self.column_diagnostic_hotspots
            ]
        if self.spark_calibration is not None:
            payload["spark_calibration"] = self.spark_calibration.to_mapping()
        return payload


@dataclass(frozen=True)
class GRC9LabelAvailability:
    """Per-label availability and computation-mode summary."""

    overall: str
    geometric_length_available: bool
    temporal_delay_available: bool
    flux_coupling_available: bool

    def __post_init__(self) -> None:
        _validate_enum(
            self.overall, frozenset({"all", "partial", "none"}), field_name="overall"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "overall": self.overall,
            "geometric_length_available": self.geometric_length_available,
            "temporal_delay_available": self.temporal_delay_available,
            "flux_coupling_available": self.flux_coupling_available,
        }


@dataclass(frozen=True)
class GRC9TransportSummary:
    """Conductance, flux, potential, and label summary for step telemetry."""

    conductance_min: float
    conductance_max: float
    conductance_mean: float
    flux_abs_sum: float
    flux_signed_balance: float
    positive_flux_edge_count: int
    negative_flux_edge_count: int
    strongest_flux_edges_sample: tuple[Mapping[str, Any], ...]
    potential_min: float | None = None
    potential_max: float | None = None
    potential_range: float | None = None
    label_availability: GRC9LabelAvailability | None = None
    label_computation_mode: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in ("conductance_min", "conductance_max", "conductance_mean"):
            _validate_non_negative_float(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_float(self.flux_abs_sum, field_name="flux_abs_sum")
        _validate_finite_float(self.flux_signed_balance, field_name="flux_signed_balance")
        _validate_non_negative_int(
            self.positive_flux_edge_count, field_name="positive_flux_edge_count"
        )
        _validate_non_negative_int(
            self.negative_flux_edge_count, field_name="negative_flux_edge_count"
        )
        for field_name in ("potential_min", "potential_max", "potential_range"):
            _validate_optional_finite_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "conductance_min": self.conductance_min,
            "conductance_max": self.conductance_max,
            "conductance_mean": self.conductance_mean,
            "flux_abs_sum": self.flux_abs_sum,
            "flux_signed_balance": self.flux_signed_balance,
            "positive_flux_edge_count": self.positive_flux_edge_count,
            "negative_flux_edge_count": self.negative_flux_edge_count,
            "strongest_flux_edges_sample": [
                dict(item) for item in self.strongest_flux_edges_sample
            ],
        }
        for field_name in ("potential_min", "potential_max", "potential_range"):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        if self.label_availability is not None:
            payload["label_availability"] = self.label_availability.to_mapping()
        if self.label_computation_mode is not None:
            payload["label_computation_mode"] = dict(
                sorted(self.label_computation_mode.items())
            )
        return payload


@dataclass(frozen=True)
class GRC9IdentityAbundanceSummary:
    """Sink, basin, successor, and abundance summary for GRC9 telemetry."""

    sink_count: int
    basin_count: int
    basin_size_min: int
    basin_size_max: int
    basin_size_mean: float
    abundance_contract: str = GRC9_ABUNDANCE_CONTRACT
    scale_weighted_abundance: float | None = None
    scale_weighted_abundance_gamma: float | None = None
    successor_self_loop_count: int | None = None
    successor_tie_count: int | None = None
    successor_tie_break_policy: str | None = None
    basin_mass_summary: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "sink_count",
            "basin_count",
            "basin_size_min",
            "basin_size_max",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_float(self.basin_size_mean, field_name="basin_size_mean")
        _validate_optional_non_negative_float(
            self.scale_weighted_abundance, field_name="scale_weighted_abundance"
        )
        _validate_optional_non_negative_float(
            self.scale_weighted_abundance_gamma,
            field_name="scale_weighted_abundance_gamma",
        )
        _validate_optional_non_negative_int(
            self.successor_self_loop_count, field_name="successor_self_loop_count"
        )
        _validate_optional_non_negative_int(
            self.successor_tie_count, field_name="successor_tie_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "sink_count": self.sink_count,
            "basin_count": self.basin_count,
            "basin_size_min": self.basin_size_min,
            "basin_size_max": self.basin_size_max,
            "basin_size_mean": self.basin_size_mean,
            "abundance_contract": self.abundance_contract,
        }
        for field_name in (
            "scale_weighted_abundance",
            "scale_weighted_abundance_gamma",
            "successor_self_loop_count",
            "successor_tie_count",
            "successor_tie_break_policy",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        if self.basin_mass_summary is not None:
            payload["basin_mass_summary"] = dict(self.basin_mass_summary)
        return payload


@dataclass(frozen=True)
class GRC9CoarseGrainingSummary:
    """Column coarse-graining and Split summary."""

    coarse_fields_list: tuple[str, ...]
    coarse_cache_state: str
    coarse_cache_invalidation_reason: str | None
    exact_split_supported_fields: tuple[str, ...]
    signed_flux_mode: str
    coarse_field_types: Mapping[str, str] | None = None
    max_reconstruction_error_by_field: Mapping[str, float] | None = None
    column_total_sparsity_by_field: Mapping[str, float] | None = None
    dominant_mode_profile_count: int | None = None
    profile_compression_mode: str | None = None

    def __post_init__(self) -> None:
        _validate_non_empty(self.coarse_cache_state, field_name="coarse_cache_state")
        _validate_enum(self.signed_flux_mode, _SIGNED_FLUX_MODES, field_name="signed_flux_mode")
        if self.coarse_field_types is not None:
            for field_name, field_type in self.coarse_field_types.items():
                _validate_non_empty(field_name, field_name="coarse_field_types key")
                _validate_enum(
                    field_type,
                    _COARSE_FIELD_TYPES,
                    field_name=f"coarse_field_types[{field_name!r}]",
                )
        for mapping_name in (
            "max_reconstruction_error_by_field",
            "column_total_sparsity_by_field",
        ):
            mapping = getattr(self, mapping_name)
            if mapping is not None:
                for key, value in mapping.items():
                    _validate_non_empty(key, field_name=f"{mapping_name} key")
                    _validate_non_negative_float(
                        value, field_name=f"{mapping_name}[{key!r}]"
                    )
        _validate_optional_non_negative_int(
            self.dominant_mode_profile_count, field_name="dominant_mode_profile_count"
        )
        if self.profile_compression_mode is not None:
            _validate_enum(
                self.profile_compression_mode,
                _PROFILE_COMPRESSION_MODES,
                field_name="profile_compression_mode",
            )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "coarse_fields_list": list(self.coarse_fields_list),
            "coarse_cache_state": self.coarse_cache_state,
            "coarse_cache_invalidation_reason": self.coarse_cache_invalidation_reason,
            "exact_split_supported_fields": list(self.exact_split_supported_fields),
            "signed_flux_mode": self.signed_flux_mode,
        }
        for field_name in (
            "coarse_field_types",
            "max_reconstruction_error_by_field",
            "column_total_sparsity_by_field",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = dict(sorted(value.items()))
        if self.dominant_mode_profile_count is not None:
            payload["dominant_mode_profile_count"] = self.dominant_mode_profile_count
        if self.profile_compression_mode is not None:
            payload["profile_compression_mode"] = self.profile_compression_mode
        return payload


@dataclass(frozen=True)
class GRC9BudgetCorrectionSummary:
    """Budget policy and latest correction-path summary."""

    budget_current: float
    budget_target: float
    budget_error: float
    budget_preservation_policy: str
    last_budget_correction_path: str
    uniform_shift_delta: float | None = None
    simplex_projection_applied: bool | None = None
    negative_clamp_count: int | None = None

    def __post_init__(self) -> None:
        for field_name in ("budget_current", "budget_target", "budget_error"):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        _validate_non_empty(
            self.budget_preservation_policy, field_name="budget_preservation_policy"
        )
        _validate_non_empty(
            self.last_budget_correction_path, field_name="last_budget_correction_path"
        )
        _validate_optional_finite_float(
            self.uniform_shift_delta, field_name="uniform_shift_delta"
        )
        _validate_optional_non_negative_int(
            self.negative_clamp_count, field_name="negative_clamp_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "budget_current": self.budget_current,
            "budget_target": self.budget_target,
            "budget_error": self.budget_error,
            "budget_preservation_policy": self.budget_preservation_policy,
            "last_budget_correction_path": self.last_budget_correction_path,
        }
        if self.uniform_shift_delta is not None:
            payload["uniform_shift_delta"] = self.uniform_shift_delta
        if self.simplex_projection_applied is not None:
            payload["simplex_projection_applied"] = self.simplex_projection_applied
        if self.negative_clamp_count is not None:
            payload["negative_clamp_count"] = self.negative_clamp_count
        return payload


@dataclass(frozen=True)
class GRC9StepTelemetryExtension:
    """Canonical GRC9 family-extension payload for step rows."""

    lane_context: GRC9LaneContext
    backend_config: GRC9BackendConfigTelemetry
    port_chart: GRC9PortChartSummary
    row_tensor: GRC9RowTensorSummary
    column_diagnostic: GRC9ColumnDiagnosticSummary
    transport: GRC9TransportSummary
    identity_abundance: GRC9IdentityAbundanceSummary
    coarse_graining: GRC9CoarseGrainingSummary
    budget_correction: GRC9BudgetCorrectionSummary
    contract_version: str = GRC9_TELEMETRY_CONTRACT_VERSION

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "contract_version": self.contract_version,
            "lane_context": self.lane_context.to_mapping(),
            "backend_config": self.backend_config.to_mapping(),
            "port_chart": self.port_chart.to_mapping(),
            "row_tensor": self.row_tensor.to_mapping(),
            "column_diagnostic": self.column_diagnostic.to_mapping(),
            "transport": self.transport.to_mapping(),
            "identity_abundance": self.identity_abundance.to_mapping(),
            "coarse_graining": self.coarse_graining.to_mapping(),
            "budget_correction": self.budget_correction.to_mapping(),
        }


@dataclass(frozen=True)
class GRC9SparkEvidence:
    """Spark trigger evidence extracted for event telemetry."""

    spark_kind: str | None = None
    active_degree: int | None = None
    saturation_gate_pass: bool | None = None
    instability_score: float | None = None
    instability_gate_pass: bool | None = None
    column_proxy_min_abs: float | None = None
    column_proxy_gate_pass: bool | None = None
    sign_crossing_gate_pass: bool | None = None
    trigger_column: int | None = None
    predicted_D_eff: int | None = None
    predicted_module_size: int | None = None
    predicted_satellite_count: int | None = None

    def __post_init__(self) -> None:
        _validate_optional_non_negative_int(self.active_degree, field_name="active_degree")
        _validate_optional_non_negative_float(
            self.instability_score, field_name="instability_score"
        )
        _validate_optional_non_negative_float(
            self.column_proxy_min_abs, field_name="column_proxy_min_abs"
        )
        _validate_optional_non_negative_int(self.trigger_column, field_name="trigger_column")
        _validate_optional_non_negative_int(self.predicted_D_eff, field_name="predicted_D_eff")
        _validate_optional_non_negative_int(
            self.predicted_module_size, field_name="predicted_module_size"
        )
        _validate_optional_non_negative_int(
            self.predicted_satellite_count, field_name="predicted_satellite_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9ExpansionEvidence:
    """Expansion module evidence extracted for event telemetry."""

    parent_sink_id: int | None = None
    target_effective_degree: int | None = None
    module_size_formula: str | None = None
    module_node_count: int | None = None
    core_node_id: int | None = None
    satellite_node_ids: tuple[int, ...] = ()
    helper_node_ids: tuple[int, ...] = ()
    reassigned_edge_count: int | None = None
    reassigned_edge_count_by_column: Mapping[int, int] | None = None
    internal_edge_count: int | None = None
    coherence_transfer_mode: str | None = None
    coherence_transfer_ratios: tuple[float, float, float] | None = None
    coherence_transfer_ratios_sum: float | None = None
    bond_weight_mode: str | None = None
    bond_weight: float | None = None
    internal_conductance_stats: Mapping[str, float] | None = None
    expansion_schedule: str | None = None
    expansion_substeps: int | None = None
    budget_preserved_by_construction: bool | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "parent_sink_id",
            "target_effective_degree",
            "module_node_count",
            "core_node_id",
            "reassigned_edge_count",
            "internal_edge_count",
            "expansion_substeps",
        ):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_non_negative_int_sequence(self.satellite_node_ids, field_name="satellite_node_ids")
        _validate_non_negative_int_sequence(self.helper_node_ids, field_name="helper_node_ids")
        if self.reassigned_edge_count_by_column is not None:
            _validate_mapping_non_negative_ints(
                self.reassigned_edge_count_by_column,
                field_name="reassigned_edge_count_by_column",
            )
        if self.coherence_transfer_ratios is not None:
            _validate_finite_float_sequence(
                self.coherence_transfer_ratios,
                field_name="coherence_transfer_ratios",
                expected_len=3,
            )
            if any(value < 0.0 for value in self.coherence_transfer_ratios):
                raise ValueError("coherence_transfer_ratios must be non-negative")
        _validate_optional_finite_float(
            self.coherence_transfer_ratios_sum,
            field_name="coherence_transfer_ratios_sum",
        )
        if self.coherence_transfer_ratios_sum is not None:
            if not math.isclose(self.coherence_transfer_ratios_sum, 1.0, abs_tol=1e-9):
                raise ValueError("coherence_transfer_ratios_sum must be close to 1.0")
        _validate_optional_non_negative_float(self.bond_weight, field_name="bond_weight")
        if self.internal_conductance_stats is not None:
            for key, value in self.internal_conductance_stats.items():
                _validate_non_negative_float(
                    value, field_name=f"internal_conductance_stats[{key!r}]"
                )
        if self.expansion_schedule is not None:
            _validate_enum(
                self.expansion_schedule,
                _EXPANSION_SCHEDULES,
                field_name="expansion_schedule",
            )

    def to_mapping(self) -> Mapping[str, Any]:
        payload = _optional_dataclass_payload(self)
        if "reassigned_edge_count_by_column" in payload:
            payload["reassigned_edge_count_by_column"] = _mapping_with_string_keys(
                self.reassigned_edge_count_by_column or {}
            )
        return payload


@dataclass(frozen=True)
class GRC9GrowthEvidence:
    """Growth event evidence extracted for event telemetry."""

    parent_node_id: int | None = None
    child_node_id: int | None = None
    selected_parent_port: int | None = None
    child_port: int | None = None
    parent_selection_mode: str | None = None
    parent_eligibility_mode: str | None = None
    parent_capacity_source: str | None = None
    front_growth_provenance_present: bool | None = None
    legacy_broad_growth: bool | None = None
    outward_flux_pressure: float | None = None
    birth_rule: str | None = None
    birth_probability: float | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "parent_node_id",
            "child_node_id",
            "selected_parent_port",
            "child_port",
        ):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name=field_name)
        _validate_optional_non_negative_float(
            self.outward_flux_pressure, field_name="outward_flux_pressure"
        )
        _validate_optional_non_negative_float(
            self.birth_probability, field_name="birth_probability"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


@dataclass(frozen=True)
class GRC9BudgetEvidence:
    """Budget correction evidence extracted for event telemetry."""

    budget_preservation_policy: str | None = None
    correction_path: str | None = None
    uniform_shift_delta: float | None = None
    simplex_projection_applied: bool | None = None
    budget_error_before: float | None = None
    budget_error_after: float | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "uniform_shift_delta",
            "budget_error_before",
            "budget_error_after",
        ):
            _validate_optional_finite_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return _optional_dataclass_payload(self)


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
class GRC9EventTelemetryExtension:
    """Canonical GRC9 family-extension payload for event rows."""

    event_domain: str
    lifecycle_stage: str
    topology_mutation: bool
    port_mutation: bool
    budget_mutation: bool
    lane_context: GRC9LaneContext | None = None
    primary_node_id: int | None = None
    primary_edge_id: int | None = None
    registry_key: str | None = None
    spark_evidence: GRC9SparkEvidence | None = None
    expansion_evidence: GRC9ExpansionEvidence | None = None
    growth_evidence: GRC9GrowthEvidence | None = None
    budget_evidence: GRC9BudgetEvidence | None = None
    contract_version: str = GRC9_TELEMETRY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _validate_enum(self.event_domain, _EVENT_DOMAINS, field_name="event_domain")
        _validate_enum(
            self.lifecycle_stage, _LIFECYCLE_STAGES, field_name="lifecycle_stage"
        )
        _validate_optional_non_negative_int(
            self.primary_node_id, field_name="primary_node_id"
        )
        _validate_optional_non_negative_int(
            self.primary_edge_id, field_name="primary_edge_id"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "event_domain": self.event_domain,
            "lifecycle_stage": self.lifecycle_stage,
            "topology_mutation": self.topology_mutation,
            "port_mutation": self.port_mutation,
            "budget_mutation": self.budget_mutation,
        }
        if self.lane_context is not None:
            payload["lane_context"] = self.lane_context.to_mapping()
        for field_name in ("primary_node_id", "primary_edge_id", "registry_key"):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        for field_name in (
            "spark_evidence",
            "expansion_evidence",
            "growth_evidence",
            "budget_evidence",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value.to_mapping()
        return payload


@dataclass(frozen=True)
class GRC9LifecycleEventCounts:
    """Fixed lifecycle event-count surface for GRC9 run summaries."""

    spark_candidate_count: int = 0
    spark_confirmed_count: int = 0
    spark_instability_count: int = 0
    spark_column_proxy_count: int = 0
    spark_sign_crossing_count: int = 0
    expansion_count: int = 0
    growth_count: int = 0
    coarse_cache_invalidation_count: int = 0
    budget_correction_count: int = 0
    budget_uniform_correction_count: int = 0
    budget_simplex_correction_count: int = 0

    def __post_init__(self) -> None:
        for field_name in self.__dataclass_fields__:
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class GRC9ExpansionSummary:
    """Run-level expansion and identity-fission summary."""

    final_expansion_registry_size: int
    total_module_nodes_created: int
    total_boundary_reassignments: int
    max_module_node_count: int
    identity_fission_candidate_count: int
    identity_fission_confirmed_count: int
    identity_fission_max_persistence_steps: int

    def __post_init__(self) -> None:
        for field_name in self.__dataclass_fields__:
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class GRC9GrowthSummary:
    """Run-level growth summary."""

    growth_count: int
    unique_growth_parent_count: int
    lowest_port_attachment_count: int
    front_capacity_growth_count: int = 0
    pressure_boundary_growth_count: int = 0
    legacy_broad_growth_count: int = 0
    birth_probability_min: float | None = None
    birth_probability_max: float | None = None
    birth_probability_mean: float | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "growth_count",
            "unique_growth_parent_count",
            "lowest_port_attachment_count",
            "front_capacity_growth_count",
            "pressure_boundary_growth_count",
            "legacy_broad_growth_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        for field_name in (
            "birth_probability_min",
            "birth_probability_max",
            "birth_probability_mean",
        ):
            _validate_optional_non_negative_float(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "growth_count": self.growth_count,
            "unique_growth_parent_count": self.unique_growth_parent_count,
            "lowest_port_attachment_count": self.lowest_port_attachment_count,
            "front_capacity_growth_count": self.front_capacity_growth_count,
            "pressure_boundary_growth_count": self.pressure_boundary_growth_count,
            "legacy_broad_growth_count": self.legacy_broad_growth_count,
        }
        for field_name in (
            "birth_probability_min",
            "birth_probability_max",
            "birth_probability_mean",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload


@dataclass(frozen=True)
class GRC9CalibrationSummary:
    """Run-level spark calibration summary."""

    spark_threshold: float
    spark_threshold_mode: str
    burn_in_M_H: float | None = None
    burn_in_M_C: float | None = None
    spark_rate_observed: float | None = None

    def __post_init__(self) -> None:
        _validate_non_negative_float(self.spark_threshold, field_name="spark_threshold")
        _validate_non_empty(self.spark_threshold_mode, field_name="spark_threshold_mode")
        _validate_optional_non_negative_float(self.burn_in_M_H, field_name="burn_in_M_H")
        _validate_optional_non_negative_float(self.burn_in_M_C, field_name="burn_in_M_C")
        _validate_optional_non_negative_float(
            self.spark_rate_observed, field_name="spark_rate_observed"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "spark_threshold": self.spark_threshold,
            "spark_threshold_mode": self.spark_threshold_mode,
        }
        for field_name in ("burn_in_M_H", "burn_in_M_C", "spark_rate_observed"):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload


@dataclass(frozen=True)
class GRC9RunSummaryExtension:
    """Canonical GRC9 family-extension payload for run summaries."""

    lane_context: GRC9LaneContext
    backend_summary: GRC9BackendConfigTelemetry
    final_port_chart_summary: GRC9PortChartSummary
    final_row_tensor_summary: GRC9RowTensorSummary
    final_column_diagnostic_summary: GRC9ColumnDiagnosticSummary
    final_transport_summary: GRC9TransportSummary
    final_identity_summary: GRC9IdentityAbundanceSummary
    final_coarse_graining_summary: GRC9CoarseGrainingSummary
    lifecycle_event_counts: GRC9LifecycleEventCounts
    expansion_summary: GRC9ExpansionSummary
    growth_summary: GRC9GrowthSummary
    calibration_summary: GRC9CalibrationSummary | None = None
    diagnostic_status_summary: Mapping[str, str] | None = None
    contract_version: str = GRC9_TELEMETRY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.diagnostic_status_summary is not None:
            for field_name, status in self.diagnostic_status_summary.items():
                _validate_non_empty(field_name, field_name="diagnostic_status_summary key")
                _validate_enum(
                    status,
                    _AVAILABILITY_STATUSES,
                    field_name=f"diagnostic_status_summary[{field_name!r}]",
                )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "lane_context": self.lane_context.to_mapping(),
            "backend_summary": self.backend_summary.to_mapping(),
            "final_port_chart_summary": self.final_port_chart_summary.to_mapping(),
            "final_row_tensor_summary": self.final_row_tensor_summary.to_mapping(),
            "final_column_diagnostic_summary": self.final_column_diagnostic_summary.to_mapping(),
            "final_transport_summary": self.final_transport_summary.to_mapping(),
            "final_identity_summary": self.final_identity_summary.to_mapping(),
            "final_coarse_graining_summary": self.final_coarse_graining_summary.to_mapping(),
            "lifecycle_event_counts": self.lifecycle_event_counts.to_mapping(),
            "expansion_summary": self.expansion_summary.to_mapping(),
            "growth_summary": self.growth_summary.to_mapping(),
        }
        if self.calibration_summary is not None:
            payload["calibration_summary"] = self.calibration_summary.to_mapping()
        if self.diagnostic_status_summary is not None:
            payload["diagnostic_status_summary"] = dict(
                sorted(self.diagnostic_status_summary.items())
            )
        return payload


def classify_grc9_event_extension(
    event_kind: str,
    payload: Mapping[str, Any] | None = None,
    *,
    lane_context: GRC9LaneContext | None = None,
) -> GRC9EventTelemetryExtension:
    """Classify a raw GRC9 event into the canonical family-extension contract."""

    normalized_payload = {} if payload is None else dict(payload)
    if event_kind == "spark":
        active_degree = _coerce_optional_int(normalized_payload.get("active_degree"))
        instability = _coerce_optional_float(normalized_payload.get("instability"))
        min_abs_column = _coerce_optional_float(normalized_payload.get("min_abs_column"))
        target_effective_degree = _coerce_optional_int(
            normalized_payload.get("target_effective_degree")
        )
        tau_instability = _coerce_optional_float(
            normalized_payload.get("tau_instability")
        )
        eps_spark = _coerce_optional_float(normalized_payload.get("eps_spark"))
        spark_kind = _coerce_optional_string(normalized_payload.get("spark_kind"))
        sign_crossing = (
            normalized_payload.get("sign_crossing")
            if isinstance(normalized_payload.get("sign_crossing"), bool)
            else None
        )
        predicted_module_size = _coerce_optional_int(
            normalized_payload.get("predicted_module_size")
        )
        if predicted_module_size is None:
            requested_node_count = _coerce_optional_int(
                normalized_payload.get("requested_node_count")
            )
            if requested_node_count is not None:
                predicted_module_size = max(4, requested_node_count)
        if predicted_module_size is None and target_effective_degree is not None:
            predicted_module_size = max(
                4,
                math.ceil((target_effective_degree - 2) / 7),
            )
        return GRC9EventTelemetryExtension(
            lane_context=lane_context,
            event_domain="spark",
            lifecycle_stage="confirmed",
            topology_mutation=False,
            port_mutation=False,
            budget_mutation=False,
            primary_node_id=_coerce_optional_int(normalized_payload.get("sink_node_id")),
            spark_evidence=GRC9SparkEvidence(
                spark_kind=spark_kind,
                active_degree=active_degree,
                saturation_gate_pass=(
                    None if active_degree is None else active_degree == 9
                ),
                instability_score=instability,
                instability_gate_pass=(
                    spark_kind == "saturation_instability"
                    if tau_instability is None or instability is None
                    else instability >= tau_instability
                ),
                column_proxy_min_abs=min_abs_column,
                column_proxy_gate_pass=(
                    spark_kind == "saturation_column_proxy"
                    if eps_spark is None or min_abs_column is None
                    else min_abs_column < eps_spark
                ),
                sign_crossing_gate_pass=(
                    spark_kind == "saturation_sign_crossing"
                    if sign_crossing is None
                    else sign_crossing
                ),
                trigger_column=_coerce_optional_int(
                    normalized_payload.get("trigger_column")
                ),
                predicted_D_eff=target_effective_degree,
                predicted_module_size=predicted_module_size,
                predicted_satellite_count=_coerce_optional_int(
                    normalized_payload.get("predicted_satellite_count", 3)
                ),
            ),
        )
    if event_kind == "expansion":
        module_node_ids = tuple(
            int(value) for value in normalized_payload.get("module_node_ids", ())
        )
        internal_edge_ids = tuple(
            int(value) for value in normalized_payload.get("internal_edge_ids", ())
        )
        distribution_weights = tuple(
            float(value) for value in normalized_payload.get("distribution_weights", ())
        )
        reassignment_map = normalized_payload.get("reassignment_map", {})
        reassigned_edge_count = (
            len(reassignment_map) if isinstance(reassignment_map, Mapping) else None
        )
        reassigned_edge_count_by_column = _reassignment_count_by_column(
            reassignment_map
        )
        return GRC9EventTelemetryExtension(
            lane_context=lane_context,
            event_domain="expansion",
            lifecycle_stage="module_created",
            topology_mutation=True,
            port_mutation=True,
            budget_mutation=True,
            primary_node_id=_coerce_optional_int(normalized_payload.get("sink_node_id")),
            registry_key=_coerce_optional_string(normalized_payload.get("expansion_id")),
            expansion_evidence=GRC9ExpansionEvidence(
                parent_sink_id=_coerce_optional_int(normalized_payload.get("sink_node_id")),
                target_effective_degree=_coerce_optional_int(
                    normalized_payload.get("target_effective_degree")
                ),
                module_size_formula="max(4, ceil((D_eff - 2) / 7))",
                module_node_count=len(module_node_ids) if module_node_ids else None,
                core_node_id=module_node_ids[0] if module_node_ids else None,
                satellite_node_ids=module_node_ids[1:4],
                helper_node_ids=module_node_ids[4:],
                reassigned_edge_count=reassigned_edge_count,
                reassigned_edge_count_by_column=reassigned_edge_count_by_column,
                internal_edge_count=len(internal_edge_ids) if internal_edge_ids else None,
                coherence_transfer_mode=_coerce_optional_string(
                    normalized_payload.get("coherence_transfer_mode")
                )
                or "expansion_distribution_mode",
                coherence_transfer_ratios=(
                    distribution_weights  # type: ignore[arg-type]
                    if len(distribution_weights) == 3
                    else None
                ),
                coherence_transfer_ratios_sum=(
                    sum(distribution_weights)
                    if len(distribution_weights) == 3
                    else None
                ),
                bond_weight_mode=_coerce_optional_string(
                    normalized_payload.get("bond_weight_mode")
                ),
                bond_weight=_coerce_optional_float(normalized_payload.get("bond_weight")),
                internal_conductance_stats=_coerce_optional_float_mapping(
                    normalized_payload.get("internal_conductance_stats")
                ),
                expansion_schedule=_coerce_optional_string(
                    normalized_payload.get("expansion_schedule")
                ),
                expansion_substeps=_coerce_optional_int(
                    normalized_payload.get("expansion_substeps")
                ),
                budget_preserved_by_construction=(
                    abs(float(normalized_payload.get("budget_error", 0.0))) <= 1e-12
                ),
            ),
        )
    if event_kind == "growth":
        parent_eligibility_mode = (
            _coerce_optional_string(
                normalized_payload.get("growth_parent_eligibility_mode")
            )
            or _coerce_optional_string(normalized_payload.get("parent_eligibility_mode"))
            or "legacy_any_inactive_port"
        )
        parent_capacity_source = (
            _coerce_optional_string(normalized_payload.get("growth_parent_capacity_source"))
            or _coerce_optional_string(normalized_payload.get("parent_capacity_source"))
            or "legacy_any_inactive_port"
        )
        front_growth_provenance_present = (
            parent_eligibility_mode == "grc9_front_capacity"
            and parent_capacity_source not in {"", "unknown", "legacy_any_inactive_port"}
        )
        return GRC9EventTelemetryExtension(
            lane_context=lane_context,
            event_domain="growth",
            lifecycle_stage="child_attached",
            topology_mutation=True,
            port_mutation=True,
            budget_mutation=True,
            primary_node_id=_coerce_optional_int(normalized_payload.get("parent_node_id")),
            growth_evidence=GRC9GrowthEvidence(
                parent_node_id=_coerce_optional_int(normalized_payload.get("parent_node_id")),
                child_node_id=_coerce_optional_int(normalized_payload.get("child_node_id")),
                selected_parent_port=_coerce_optional_int(
                    normalized_payload.get("parent_port_id")
                ),
                child_port=_coerce_optional_int(normalized_payload.get("child_port_id")),
                parent_selection_mode=_coerce_optional_string(
                    normalized_payload.get("parent_selection_mode")
                )
                or "outward_flux_parent_selection",
                parent_eligibility_mode=parent_eligibility_mode,
                parent_capacity_source=parent_capacity_source,
                front_growth_provenance_present=front_growth_provenance_present,
                legacy_broad_growth=parent_eligibility_mode == "legacy_any_inactive_port",
                outward_flux_pressure=_coerce_optional_float(
                    normalized_payload.get("outward_flux")
                ),
                birth_rule=_coerce_optional_string(normalized_payload.get("birth_rule"))
                or "bernoulli_probability",
                birth_probability=_coerce_optional_float(
                    normalized_payload.get("birth_probability")
                ),
            ),
        )
    if event_kind == "budget_correction":
        return GRC9EventTelemetryExtension(
            lane_context=lane_context,
            event_domain="budget",
            lifecycle_stage="corrected",
            topology_mutation=False,
            port_mutation=False,
            budget_mutation=True,
            budget_evidence=GRC9BudgetEvidence(
                budget_preservation_policy=_coerce_optional_string(
                    normalized_payload.get("budget_preservation_policy")
                ),
                correction_path=_coerce_optional_string(
                    normalized_payload.get("correction_path")
                ),
                uniform_shift_delta=_coerce_optional_float(
                    normalized_payload.get("uniform_shift_delta")
                ),
                simplex_projection_applied=(
                    normalized_payload.get("simplex_projection_applied")
                    if isinstance(
                        normalized_payload.get("simplex_projection_applied"), bool
                    )
                    else None
                ),
                budget_error_before=_coerce_optional_float(
                    normalized_payload.get("budget_error_before")
                ),
                budget_error_after=_coerce_optional_float(
                    normalized_payload.get("budget_error_after")
                ),
            ),
        )
    if event_kind == "coarse_cache_invalidation":
        return GRC9EventTelemetryExtension(
            lane_context=lane_context,
            event_domain="coarse",
            lifecycle_stage="invalidated",
            topology_mutation=False,
            port_mutation=False,
            budget_mutation=False,
            registry_key=_coerce_optional_string(normalized_payload.get("cache_key")),
        )
    return GRC9EventTelemetryExtension(
        lane_context=lane_context,
        event_domain="other",
        lifecycle_stage="other",
        topology_mutation=False,
        port_mutation=False,
        budget_mutation=False,
    )


def _reassignment_count_by_column(value: Any) -> Mapping[int, int] | None:
    if not isinstance(value, Mapping):
        return None
    counts: dict[int, int] = {}
    for raw_payload in value.values():
        if not isinstance(raw_payload, Mapping):
            continue
        from_port_id = _coerce_optional_int(raw_payload.get("from_port_id"))
        if from_port_id is None or from_port_id < 1:
            continue
        column = ((from_port_id - 1) % 3) + 1
        counts[column] = counts.get(column, 0) + 1
    return counts or None


def _coerce_optional_float_mapping(value: Any) -> Mapping[str, float] | None:
    if not isinstance(value, Mapping):
        return None
    result: dict[str, float] = {}
    for key, raw_value in value.items():
        numeric = _coerce_optional_float(raw_value)
        if numeric is None:
            continue
        result[str(key)] = numeric
    return result or None


def grc9_step_family_extensions(
    extension: GRC9StepTelemetryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRC9_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


def grc9_event_family_extensions(
    extension: GRC9EventTelemetryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRC9_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


def grc9_run_summary_family_extensions(
    extension: GRC9RunSummaryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRC9_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


__all__ = [
    "GRC9_ABUNDANCE_CONTRACT",
    "GRC9_LANDSCAPE_LOWERING_MODE",
    "GRC9_TELEMETRY_CONTRACT_VERSION",
    "GRC9_TELEMETRY_FAMILY",
    "GRC9BackendConfigTelemetry",
    "GRC9BudgetCorrectionSummary",
    "GRC9BudgetEvidence",
    "GRC9CalibrationSummary",
    "GRC9CoarseGrainingSummary",
    "GRC9ColumnDiagnosticSummary",
    "GRC9EventTelemetryExtension",
    "GRC9ExpansionEvidence",
    "GRC9ExpansionSummary",
    "GRC9GrowthEvidence",
    "GRC9GrowthSummary",
    "GRC9IdentityAbundanceSummary",
    "GRC9LabelAvailability",
    "GRC9LaneContext",
    "GRC9LifecycleEventCounts",
    "GRC9PortChartSummary",
    "GRC9RowTensorSummary",
    "GRC9RunSummaryExtension",
    "GRC9SparkCalibrationTelemetry",
    "GRC9SparkEvidence",
    "GRC9StepTelemetryExtension",
    "GRC9TransportSummary",
    "classify_grc9_event_extension",
    "grc9_event_family_extensions",
    "grc9_run_summary_family_extensions",
    "grc9_step_family_extensions",
]

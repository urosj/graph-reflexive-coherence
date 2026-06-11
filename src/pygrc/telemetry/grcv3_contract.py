"""Explicit GRCV3 telemetry extension contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any

from .schema import TelemetryFamilyExtensions


GRCV3_TELEMETRY_FAMILY = "grcv3"
GRCV3_TELEMETRY_CONTRACT_VERSION = "phase_t_iter26_v1"

_EVENT_DOMAINS = frozenset({"spark", "split", "choice", "hierarchy", "birth", "other"})
_LIFECYCLE_STAGES = frozenset(
    {
        "candidate",
        "pending",
        "confirmed",
        "init",
        "progress",
        "complete",
        "detected",
        "resolved",
        "collapse",
        "update",
        "created",
        "other",
    }
)


def _validate_non_negative_int(value: int, *, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_finite_float(value: float, *, field_name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _coerce_optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _coerce_optional_identity(value: Any) -> str | int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str | int):
        return value
    return None


@dataclass(frozen=True)
class GRCV3BackendTelemetry:
    """Normalized backend identity surface for GRCV3 telemetry."""

    geometry_backend: str
    differential_backend: str
    metric_backend: str
    spark_backend: str
    hierarchy_backend: str
    choice_backend: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "geometry_backend": self.geometry_backend,
            "differential_backend": self.differential_backend,
            "metric_backend": self.metric_backend,
            "spark_backend": self.spark_backend,
            "hierarchy_backend": self.hierarchy_backend,
            "choice_backend": self.choice_backend,
        }


@dataclass(frozen=True)
class GRCV3BasinSummary:
    """Compressed basin-attribute summary for step or run telemetry."""

    attributed_node_count: int
    active_basin_count: int
    geometric_seed_count: int
    geometric_validated_basin_count: int
    max_hierarchy_depth: int

    def __post_init__(self) -> None:
        _validate_non_negative_int(
            self.attributed_node_count, field_name="attributed_node_count"
        )
        _validate_non_negative_int(self.active_basin_count, field_name="active_basin_count")
        _validate_non_negative_int(
            self.geometric_seed_count, field_name="geometric_seed_count"
        )
        _validate_non_negative_int(
            self.geometric_validated_basin_count,
            field_name="geometric_validated_basin_count",
        )
        _validate_non_negative_int(
            self.max_hierarchy_depth, field_name="max_hierarchy_depth"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "attributed_node_count": self.attributed_node_count,
            "active_basin_count": self.active_basin_count,
            "geometric_seed_count": self.geometric_seed_count,
            "geometric_validated_basin_count": self.geometric_validated_basin_count,
            "max_hierarchy_depth": self.max_hierarchy_depth,
        }


@dataclass(frozen=True)
class GRCV3SignedHessianTelemetry:
    """Signed-Hessian metadata surface for GRCV3 telemetry."""

    hessian_sign: int

    def __post_init__(self) -> None:
        if self.hessian_sign not in (-1, 1):
            raise ValueError("hessian_sign must be either -1 or 1")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "hessian_sign": self.hessian_sign,
        }


@dataclass(frozen=True)
class GRCV3SparkStateSummary:
    """Compressed spark/split state summary for GRCV3 telemetry."""

    split_registry_size: int
    active_split_count: int
    confirmed_split_count: int
    pending_spark_count: int

    def __post_init__(self) -> None:
        _validate_non_negative_int(
            self.split_registry_size, field_name="split_registry_size"
        )
        _validate_non_negative_int(
            self.active_split_count, field_name="active_split_count"
        )
        _validate_non_negative_int(
            self.confirmed_split_count, field_name="confirmed_split_count"
        )
        _validate_non_negative_int(
            self.pending_spark_count, field_name="pending_spark_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "split_registry_size": self.split_registry_size,
            "active_split_count": self.active_split_count,
            "confirmed_split_count": self.confirmed_split_count,
            "pending_spark_count": self.pending_spark_count,
        }


@dataclass(frozen=True)
class GRCV3HierarchySummary:
    """Compressed hierarchy-state summary for GRCV3 telemetry."""

    hierarchy_root_count: int
    hierarchy_node_count: int
    child_basin_link_count: int

    def __post_init__(self) -> None:
        _validate_non_negative_int(
            self.hierarchy_root_count, field_name="hierarchy_root_count"
        )
        _validate_non_negative_int(
            self.hierarchy_node_count, field_name="hierarchy_node_count"
        )
        _validate_non_negative_int(
            self.child_basin_link_count, field_name="child_basin_link_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "hierarchy_root_count": self.hierarchy_root_count,
            "hierarchy_node_count": self.hierarchy_node_count,
            "child_basin_link_count": self.child_basin_link_count,
        }


@dataclass(frozen=True)
class GRCV3ChoiceStateSummary:
    """Compressed choice/collapse state summary for GRCV3 telemetry."""

    choice_regime_count: int
    collapse_registry_count: int
    evaluated_node_count: int

    def __post_init__(self) -> None:
        _validate_non_negative_int(
            self.choice_regime_count, field_name="choice_regime_count"
        )
        _validate_non_negative_int(
            self.collapse_registry_count, field_name="collapse_registry_count"
        )
        _validate_non_negative_int(
            self.evaluated_node_count, field_name="evaluated_node_count"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "choice_regime_count": self.choice_regime_count,
            "collapse_registry_count": self.collapse_registry_count,
            "evaluated_node_count": self.evaluated_node_count,
        }


@dataclass(frozen=True)
class GRCV3FrontierBirthStateSummary:
    """Compressed opt-in frontier-birth state summary for GRCV3 telemetry."""

    frontier_birth_mode: str
    frontier_birth_rule: str
    frontier_candidate_count: int
    pressure_boundary_candidate_count: int
    frontier_birth_count: int
    pressure_boundary_birth_count: int
    frontier_sources_observed: tuple[str, ...] = ()
    outward_flux_pressure_min: float | None = None
    outward_flux_pressure_max: float | None = None
    outward_flux_pressure_mean: float | None = None
    birth_probability_min: float | None = None
    birth_probability_max: float | None = None
    birth_probability_mean: float | None = None

    def __post_init__(self) -> None:
        if not self.frontier_birth_mode:
            raise ValueError("frontier_birth_mode must not be empty")
        if not self.frontier_birth_rule:
            raise ValueError("frontier_birth_rule must not be empty")
        for field_name in (
            "frontier_candidate_count",
            "pressure_boundary_candidate_count",
            "frontier_birth_count",
            "pressure_boundary_birth_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)
        for field_name in (
            "outward_flux_pressure_min",
            "outward_flux_pressure_max",
            "outward_flux_pressure_mean",
            "birth_probability_min",
            "birth_probability_max",
            "birth_probability_mean",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_finite_float(value, field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "frontier_birth_mode": self.frontier_birth_mode,
            "frontier_birth_rule": self.frontier_birth_rule,
            "frontier_candidate_count": self.frontier_candidate_count,
            "pressure_boundary_candidate_count": self.pressure_boundary_candidate_count,
            "frontier_birth_count": self.frontier_birth_count,
            "pressure_boundary_birth_count": self.pressure_boundary_birth_count,
            "frontier_sources_observed": list(self.frontier_sources_observed),
        }
        for field_name in (
            "outward_flux_pressure_min",
            "outward_flux_pressure_max",
            "outward_flux_pressure_mean",
            "birth_probability_min",
            "birth_probability_max",
            "birth_probability_mean",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload


@dataclass(frozen=True)
class GRCV3LifecycleEventCounts:
    """Fixed lifecycle event-count surface for run summaries."""

    spark_candidate_count: int = 0
    spark_pending_count: int = 0
    spark_confirmed_count: int = 0
    split_init_count: int = 0
    split_progress_count: int = 0
    split_complete_count: int = 0
    choice_detected_count: int = 0
    choice_resolved_count: int = 0
    collapse_count: int = 0
    frontier_birth_count: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "spark_candidate_count",
            "spark_pending_count",
            "spark_confirmed_count",
            "split_init_count",
            "split_progress_count",
            "split_complete_count",
            "choice_detected_count",
            "choice_resolved_count",
            "collapse_count",
            "frontier_birth_count",
        ):
            _validate_non_negative_int(getattr(self, field_name), field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "spark_candidate_count": self.spark_candidate_count,
            "spark_pending_count": self.spark_pending_count,
            "spark_confirmed_count": self.spark_confirmed_count,
            "split_init_count": self.split_init_count,
            "split_progress_count": self.split_progress_count,
            "split_complete_count": self.split_complete_count,
            "choice_detected_count": self.choice_detected_count,
            "choice_resolved_count": self.choice_resolved_count,
            "collapse_count": self.collapse_count,
            "frontier_birth_count": self.frontier_birth_count,
        }


@dataclass(frozen=True)
class GRCV3ObservedInteriorSite:
    """Observed interior-site metrics for one monitored landscape primitive."""

    primitive_id: str
    node_id: int
    gradient_norm: float
    min_signed_eigenvalue: float | None = None
    max_signed_eigenvalue: float | None = None
    weak_mode_signed_curvature: float | None = None
    gradient_gate_pass: bool = False
    geometric_validation_pass: bool = False
    spark_candidate_regime: bool = False

    def __post_init__(self) -> None:
        if not self.primitive_id:
            raise ValueError("primitive_id must not be empty")
        _validate_non_negative_int(self.node_id, field_name="node_id")
        _validate_finite_float(self.gradient_norm, field_name="gradient_norm")
        for field_name in (
            "min_signed_eigenvalue",
            "max_signed_eigenvalue",
            "weak_mode_signed_curvature",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_finite_float(value, field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "primitive_id": self.primitive_id,
            "node_id": self.node_id,
            "gradient_norm": self.gradient_norm,
            "gradient_gate_pass": self.gradient_gate_pass,
            "geometric_validation_pass": self.geometric_validation_pass,
            "spark_candidate_regime": self.spark_candidate_regime,
        }
        if self.min_signed_eigenvalue is not None:
            payload["min_signed_eigenvalue"] = self.min_signed_eigenvalue
        if self.max_signed_eigenvalue is not None:
            payload["max_signed_eigenvalue"] = self.max_signed_eigenvalue
        if self.weak_mode_signed_curvature is not None:
            payload["weak_mode_signed_curvature"] = self.weak_mode_signed_curvature
        return payload


@dataclass(frozen=True)
class GRCV3TransientLandscapeStepSummary:
    """Step-level transient landscape observability surface for GRCV3."""

    monitoring_surface_kind: str
    observed_sites: tuple[GRCV3ObservedInteriorSite, ...]

    def __post_init__(self) -> None:
        if not self.monitoring_surface_kind:
            raise ValueError("monitoring_surface_kind must not be empty")
        if not self.observed_sites:
            raise ValueError("observed_sites must not be empty")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "monitoring_surface_kind": self.monitoring_surface_kind,
            "observed_sites": [site.to_mapping() for site in self.observed_sites],
        }


@dataclass(frozen=True)
class GRCV3TransientLandscapePrimitiveSummary:
    """Run-level trajectory summary for one monitored landscape primitive."""

    primitive_id: str
    node_id: int
    initial_gradient_norm: float
    min_gradient_norm: float
    final_gradient_norm: float
    initial_weak_mode_signed_curvature: float | None = None
    min_weak_mode_signed_curvature: float | None = None
    final_weak_mode_signed_curvature: float | None = None
    initial_min_signed_eigenvalue: float | None = None
    min_signed_eigenvalue: float | None = None
    final_min_signed_eigenvalue: float | None = None
    first_gradient_gate_pass_step: int | None = None
    first_geometric_validation_step: int | None = None
    first_spark_candidate_step: int | None = None
    first_spark_step: int | None = None
    first_split_init_step: int | None = None

    def __post_init__(self) -> None:
        if not self.primitive_id:
            raise ValueError("primitive_id must not be empty")
        _validate_non_negative_int(self.node_id, field_name="node_id")
        for field_name in (
            "initial_gradient_norm",
            "min_gradient_norm",
            "final_gradient_norm",
        ):
            _validate_finite_float(getattr(self, field_name), field_name=field_name)
        for field_name in (
            "initial_weak_mode_signed_curvature",
            "min_weak_mode_signed_curvature",
            "final_weak_mode_signed_curvature",
            "initial_min_signed_eigenvalue",
            "min_signed_eigenvalue",
            "final_min_signed_eigenvalue",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_finite_float(value, field_name=field_name)
        for field_name in (
            "first_gradient_gate_pass_step",
            "first_geometric_validation_step",
            "first_spark_candidate_step",
            "first_spark_step",
            "first_split_init_step",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_non_negative_int(value, field_name=field_name)

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "primitive_id": self.primitive_id,
            "node_id": self.node_id,
            "initial_gradient_norm": self.initial_gradient_norm,
            "min_gradient_norm": self.min_gradient_norm,
            "final_gradient_norm": self.final_gradient_norm,
        }
        for field_name in (
            "initial_weak_mode_signed_curvature",
            "min_weak_mode_signed_curvature",
            "final_weak_mode_signed_curvature",
            "initial_min_signed_eigenvalue",
            "min_signed_eigenvalue",
            "final_min_signed_eigenvalue",
            "first_gradient_gate_pass_step",
            "first_geometric_validation_step",
            "first_spark_candidate_step",
            "first_spark_step",
            "first_split_init_step",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload


@dataclass(frozen=True)
class GRCV3EventAlignedLandscapeObservation:
    """First event-aligned landscape observation snapshot for one event kind."""

    event_kind: str
    step_index: int
    observed_sites: tuple[GRCV3ObservedInteriorSite, ...]

    def __post_init__(self) -> None:
        if not self.event_kind:
            raise ValueError("event_kind must not be empty")
        _validate_non_negative_int(self.step_index, field_name="step_index")
        if not self.observed_sites:
            raise ValueError("observed_sites must not be empty")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "event_kind": self.event_kind,
            "step_index": self.step_index,
            "observed_sites": [site.to_mapping() for site in self.observed_sites],
        }


@dataclass(frozen=True)
class GRCV3TransientLandscapeRunSummary:
    """Run-level transient-path observability summary for GRCV3 landscapes."""

    monitoring_surface_kind: str
    monitored_node_ids_by_primitive_id: Mapping[str, int]
    surface_realization_summary: Mapping[str, Mapping[str, Any]]
    primitive_summaries: tuple[GRCV3TransientLandscapePrimitiveSummary, ...]
    event_aligned_observations: tuple[GRCV3EventAlignedLandscapeObservation, ...] = ()

    def __post_init__(self) -> None:
        if not self.monitoring_surface_kind:
            raise ValueError("monitoring_surface_kind must not be empty")
        if not self.monitored_node_ids_by_primitive_id:
            raise ValueError("monitored_node_ids_by_primitive_id must not be empty")
        if not self.primitive_summaries:
            raise ValueError("primitive_summaries must not be empty")
        for primitive_id, node_id in self.monitored_node_ids_by_primitive_id.items():
            if not primitive_id:
                raise ValueError("monitored primitive ids must not be empty")
            _validate_non_negative_int(node_id, field_name="monitored node id")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "monitoring_surface_kind": self.monitoring_surface_kind,
            "monitored_node_ids_by_primitive_id": dict(
                sorted(self.monitored_node_ids_by_primitive_id.items())
            ),
            "surface_realization_summary": {
                primitive_id: dict(summary)
                for primitive_id, summary in sorted(self.surface_realization_summary.items())
            },
            "primitive_summaries": [
                summary.to_mapping() for summary in self.primitive_summaries
            ],
            "event_aligned_observations": [
                observation.to_mapping() for observation in self.event_aligned_observations
            ],
        }


@dataclass(frozen=True)
class GRCV3StepTelemetryExtension:
    """Canonical GRCV3 family-extension payload for step rows."""

    backend_summary: GRCV3BackendTelemetry
    signed_hessian: GRCV3SignedHessianTelemetry
    basin_summary: GRCV3BasinSummary
    spark_state: GRCV3SparkStateSummary
    hierarchy_state: GRCV3HierarchySummary
    choice_state: GRCV3ChoiceStateSummary
    frontier_birth_state: GRCV3FrontierBirthStateSummary
    transient_landscape: GRCV3TransientLandscapeStepSummary | None = None
    contract_version: str = GRCV3_TELEMETRY_CONTRACT_VERSION

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "backend_summary": self.backend_summary.to_mapping(),
            "signed_hessian": self.signed_hessian.to_mapping(),
            "basin_summary": self.basin_summary.to_mapping(),
            "spark_state": self.spark_state.to_mapping(),
            "hierarchy_state": self.hierarchy_state.to_mapping(),
            "choice_state": self.choice_state.to_mapping(),
            "frontier_birth_state": self.frontier_birth_state.to_mapping(),
        }
        if self.transient_landscape is not None:
            payload["transient_landscape"] = self.transient_landscape.to_mapping()
        return payload


@dataclass(frozen=True)
class GRCV3EventTelemetryExtension:
    """Canonical GRCV3 family-extension payload for event rows."""

    event_domain: str
    lifecycle_stage: str
    topology_mutation: bool
    hierarchy_mutation: bool
    primary_node_id: int | None = None
    primary_basin_id: str | int | None = None
    registry_key: str | None = None
    contract_version: str = GRCV3_TELEMETRY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.event_domain not in _EVENT_DOMAINS:
            raise ValueError(
                f"event_domain must be one of {tuple(sorted(_EVENT_DOMAINS))}"
            )
        if self.lifecycle_stage not in _LIFECYCLE_STAGES:
            raise ValueError(
                f"lifecycle_stage must be one of {tuple(sorted(_LIFECYCLE_STAGES))}"
            )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "event_domain": self.event_domain,
            "lifecycle_stage": self.lifecycle_stage,
            "topology_mutation": self.topology_mutation,
            "hierarchy_mutation": self.hierarchy_mutation,
        }
        if self.primary_node_id is not None:
            payload["primary_node_id"] = self.primary_node_id
        if self.primary_basin_id is not None:
            payload["primary_basin_id"] = self.primary_basin_id
        if self.registry_key is not None:
            payload["registry_key"] = self.registry_key
        return payload


@dataclass(frozen=True)
class GRCV3RunSummaryExtension:
    """Canonical GRCV3 family-extension payload for run summaries."""

    backend_summary: GRCV3BackendTelemetry
    signed_hessian: GRCV3SignedHessianTelemetry
    final_basin_summary: GRCV3BasinSummary
    final_spark_state: GRCV3SparkStateSummary
    final_hierarchy_state: GRCV3HierarchySummary
    final_choice_state: GRCV3ChoiceStateSummary
    frontier_birth_summary: GRCV3FrontierBirthStateSummary
    lifecycle_event_counts: GRCV3LifecycleEventCounts
    transient_landscape: GRCV3TransientLandscapeRunSummary | None = None
    contract_version: str = GRCV3_TELEMETRY_CONTRACT_VERSION

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "backend_summary": self.backend_summary.to_mapping(),
            "signed_hessian": self.signed_hessian.to_mapping(),
            "final_basin_summary": self.final_basin_summary.to_mapping(),
            "final_spark_state": self.final_spark_state.to_mapping(),
            "final_hierarchy_state": self.final_hierarchy_state.to_mapping(),
            "final_choice_state": self.final_choice_state.to_mapping(),
            "frontier_birth_summary": self.frontier_birth_summary.to_mapping(),
            "lifecycle_event_counts": self.lifecycle_event_counts.to_mapping(),
        }
        if self.transient_landscape is not None:
            payload["transient_landscape"] = self.transient_landscape.to_mapping()
        return payload


def classify_grcv3_event_extension(
    event_kind: str,
    payload: Mapping[str, Any] | None = None,
) -> GRCV3EventTelemetryExtension:
    """Classify a raw GRCV3 event into the canonical family-extension contract."""

    normalized_payload = {} if payload is None else dict(payload)
    mapping = {
        "spark_candidate": ("spark", "candidate", False, False),
        "spark_pending": ("spark", "pending", False, False),
        "spark": ("spark", "confirmed", False, False),
        "split_init": ("split", "init", True, True),
        "split_progress": ("split", "progress", False, False),
        "split_complete": ("split", "complete", True, False),
        "choice_detected": ("choice", "detected", False, False),
        "choice_resolved": ("choice", "resolved", False, False),
        "collapse": ("choice", "collapse", False, False),
        "frontier_birth": ("birth", "created", True, True),
    }
    event_domain, lifecycle_stage, topology_mutation, hierarchy_mutation = mapping.get(
        event_kind,
        ("other", "other", False, False),
    )
    return GRCV3EventTelemetryExtension(
        event_domain=event_domain,
        lifecycle_stage=lifecycle_stage,
        topology_mutation=topology_mutation,
        hierarchy_mutation=hierarchy_mutation,
        primary_node_id=_coerce_optional_int(
            normalized_payload.get("node_id", normalized_payload.get("parent_node_id"))
        ),
        primary_basin_id=_coerce_optional_identity(
            normalized_payload.get("basin_id", normalized_payload.get("parent_basin_id"))
        ),
        registry_key=(
            str(normalized_payload["registry_key"])
            if "registry_key" in normalized_payload
            and normalized_payload["registry_key"] is not None
            else None
        ),
    )


def grcv3_step_family_extensions(
    extension: GRCV3StepTelemetryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRCV3_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


def grcv3_event_family_extensions(
    extension: GRCV3EventTelemetryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRCV3_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


def grcv3_run_summary_family_extensions(
    extension: GRCV3RunSummaryExtension,
) -> TelemetryFamilyExtensions:
    return {
        GRCV3_TELEMETRY_FAMILY: dict(extension.to_mapping()),
    }


__all__ = [
    "GRCV3_TELEMETRY_FAMILY",
    "GRCV3_TELEMETRY_CONTRACT_VERSION",
    "GRCV3BackendTelemetry",
    "GRCV3BasinSummary",
    "GRCV3ChoiceStateSummary",
    "GRCV3EventAlignedLandscapeObservation",
    "GRCV3EventTelemetryExtension",
    "GRCV3HierarchySummary",
    "GRCV3FrontierBirthStateSummary",
    "GRCV3LifecycleEventCounts",
    "GRCV3ObservedInteriorSite",
    "GRCV3RunSummaryExtension",
    "GRCV3SignedHessianTelemetry",
    "GRCV3SparkStateSummary",
    "GRCV3StepTelemetryExtension",
    "GRCV3TransientLandscapePrimitiveSummary",
    "GRCV3TransientLandscapeRunSummary",
    "GRCV3TransientLandscapeStepSummary",
    "classify_grcv3_event_extension",
    "grcv3_event_family_extensions",
    "grcv3_run_summary_family_extensions",
    "grcv3_step_family_extensions",
]

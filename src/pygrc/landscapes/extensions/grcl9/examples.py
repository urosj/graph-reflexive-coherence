"""GRCL/Morse-facing examples that compile to GRCL-9 source documents."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import math
import re
from typing import Any

from pygrc.core import InvalidLandscapeSeedError

from ...io import load_landscape_seed
from ...seed import LandscapeSeed
from .manifest import GRCL9_BASE_NON_CLAIMS, default_grcl9_lowering_manifest
from .schema import (
    GRCL9BridgePolicy,
    GRCL9ColumnProxyProfile,
    GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus,
    GRCL9InstabilityProfile,
    GRCL9PostExpansionFissionGeometry,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
)


GRCL9_LANDSCAPE_EXAMPLE_VERSION = "grcl9.landscape_example.v1"

GRCL9_LANDSCAPE_EXAMPLE_NAMES = (
    "spark_column_proxy_eps_pass",
    "spark_column_proxy_eps_fail",
    "spark_instability_tau_pass",
    "spark_instability_tau_fail",
    "spark_to_expansion_d_eff_low",
    "spark_to_expansion_d_eff_high",
    "corrected_front_growth_positive_high",
    "corrected_pressure_boundary_positive_high",
    "corrected_front_growth_no_growth_low",
    "corrected_front_growth_no_front_fail",
    "corrected_front_growth_closed_front_fail",
    "growth_pressure_lambda_high",
    "growth_pressure_lambda_low",
    "post_expansion_fission_min_mass_pass",
    "post_expansion_fission_min_mass_fail",
    "cell_boundary_ridge_membrane_spark_pass",
    "cell_internal_valley_transport_growth_high",
    "cell_plateau_nested_basins_fission_pass",
    "cell_saddle_branch_instability_pass",
    "cell_refinement_budget_partition_expansion_high",
    "cell_membrane_rupture_structural_probe",
    "cell_basin_merge_before_persistence_probe",
    "cell_support_loss_identity_decay_probe",
    "cell_saddle_choice_pressure_structural_probe",
    "cell_basin_merge_runtime_collapse_probe",
    "cell_basin_merge_runtime_stability_control",
    "cell_developed_basin_centroid_collapse_long_window",
    "cell_full_capacity_phenomenology_cascade",
    "cell_full_capacity_cascade_low_growth",
    "cell_full_capacity_cascade_high_growth",
    "cell_full_capacity_cascade_no_merge_bridge",
    "cell_full_capacity_cascade_weak_merge_bridge",
    "cell_full_capacity_cascade_isolated_bridge",
    "cell_full_capacity_cascade_larger_basin_support",
    "cell_full_capacity_cascade_no_refinement",
    "cell_full_capacity_cascade_no_growth",
    "cell_full_capacity_cascade_balanced_basins",
    "cell_full_capacity_cascade_mild_asymmetry",
    "cell_full_capacity_cascade_threshold_asymmetry",
    "cell_full_capacity_cascade_deep_collapse",
    "cell_full_capacity_cascade_isolated_threshold",
    "cell_full_capacity_phase_balanced_no_growth",
    "cell_full_capacity_phase_balanced_low_growth",
    "cell_full_capacity_phase_balanced_nominal_growth",
    "cell_full_capacity_phase_mild_no_growth",
    "cell_full_capacity_phase_mild_low_growth",
    "cell_full_capacity_phase_mild_nominal_growth",
    "cell_full_capacity_phase_threshold_no_growth",
    "cell_full_capacity_phase_threshold_low_growth",
    "cell_full_capacity_phase_threshold_nominal_growth",
    "cell_full_capacity_phase_deep_no_growth",
    "cell_full_capacity_phase_deep_low_growth",
    "cell_full_capacity_phase_deep_nominal_growth",
)

GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS = (
    Path("configs/landscapes/seed/grcl9-spark-column-proxy-eps-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-spark-column-proxy-eps-fail.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-spark-instability-tau-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-spark-instability-tau-fail.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-spark-to-expansion-d-eff-low.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-spark-to-expansion-d-eff-high.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-front-growth-positive-high.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-pressure-boundary-positive-high.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-front-growth-no-growth-low.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-front-growth-no-front-fail.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-front-growth-closed-front-fail.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-post-expansion-fission-min-mass-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-post-expansion-fission-min-mass-fail.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-boundary-ridge-membrane-spark-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-plateau-nested-basins-fission-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-saddle-branch-instability-pass.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-refinement-budget-partition-expansion-high.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-membrane-rupture-structural-probe.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-basin-merge-before-persistence-probe.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-saddle-choice-pressure-structural-probe.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-basin-merge-runtime-collapse-probe.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-basin-merge-runtime-stability-control.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-cell-developed-basin-centroid-collapse-long-window.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-internal-valley-transport-growth-high.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-support-loss-identity-decay-probe.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phenomenology-cascade.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-high-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-no-merge-bridge.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-weak-merge-bridge.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-isolated-bridge.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-larger-basin-support.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-no-refinement.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-balanced-basins.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-mild-asymmetry.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-threshold-asymmetry.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-deep-collapse.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-cascade-isolated-threshold.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-balanced-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-balanced-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-balanced-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-mild-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-mild-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-mild-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-threshold-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-threshold-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-threshold-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-deep-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-deep-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9-corrected-cell-full-capacity-phase-deep-nominal-growth.seed.yaml"),
)
GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES = (
    "spark_column_proxy_eps_pass",
    "spark_column_proxy_eps_fail",
    "spark_instability_tau_pass",
    "spark_instability_tau_fail",
    "spark_to_expansion_d_eff_low",
    "spark_to_expansion_d_eff_high",
    "corrected_front_growth_positive_high",
    "corrected_pressure_boundary_positive_high",
    "corrected_front_growth_no_growth_low",
    "corrected_front_growth_no_front_fail",
    "corrected_front_growth_closed_front_fail",
    "post_expansion_fission_min_mass_pass",
    "post_expansion_fission_min_mass_fail",
    "cell_boundary_ridge_membrane_spark_pass",
    "cell_plateau_nested_basins_fission_pass",
    "cell_saddle_branch_instability_pass",
    "cell_refinement_budget_partition_expansion_high",
    "cell_membrane_rupture_structural_probe",
    "cell_basin_merge_before_persistence_probe",
    "cell_saddle_choice_pressure_structural_probe",
    "cell_basin_merge_runtime_collapse_probe",
    "cell_basin_merge_runtime_stability_control",
    "cell_developed_basin_centroid_collapse_long_window",
    "corrected_cell_internal_valley_transport_growth_high",
    "corrected_cell_support_loss_identity_decay_probe",
    "corrected_cell_full_capacity_phenomenology_cascade",
    "corrected_cell_full_capacity_cascade_low_growth",
    "corrected_cell_full_capacity_cascade_high_growth",
    "corrected_cell_full_capacity_cascade_no_merge_bridge",
    "corrected_cell_full_capacity_cascade_weak_merge_bridge",
    "corrected_cell_full_capacity_cascade_isolated_bridge",
    "corrected_cell_full_capacity_cascade_larger_basin_support",
    "corrected_cell_full_capacity_cascade_no_refinement",
    "corrected_cell_full_capacity_cascade_no_growth",
    "corrected_cell_full_capacity_cascade_balanced_basins",
    "corrected_cell_full_capacity_cascade_mild_asymmetry",
    "corrected_cell_full_capacity_cascade_threshold_asymmetry",
    "corrected_cell_full_capacity_cascade_deep_collapse",
    "corrected_cell_full_capacity_cascade_isolated_threshold",
    "corrected_cell_full_capacity_phase_balanced_no_growth",
    "corrected_cell_full_capacity_phase_balanced_low_growth",
    "corrected_cell_full_capacity_phase_balanced_nominal_growth",
    "corrected_cell_full_capacity_phase_mild_no_growth",
    "corrected_cell_full_capacity_phase_mild_low_growth",
    "corrected_cell_full_capacity_phase_mild_nominal_growth",
    "corrected_cell_full_capacity_phase_threshold_no_growth",
    "corrected_cell_full_capacity_phase_threshold_low_growth",
    "corrected_cell_full_capacity_phase_threshold_nominal_growth",
    "corrected_cell_full_capacity_phase_deep_no_growth",
    "corrected_cell_full_capacity_phase_deep_low_growth",
    "corrected_cell_full_capacity_phase_deep_nominal_growth",
)
GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS = (
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-growth-pressure-lambda-high.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-growth-pressure-lambda-low.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-internal-valley-transport-growth-high.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-support-loss-identity-decay-probe.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phenomenology-cascade.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-high-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-no-merge-bridge.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-weak-merge-bridge.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-isolated-bridge.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-larger-basin-support.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-no-refinement.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-balanced-basins.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-mild-asymmetry.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-threshold-asymmetry.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-deep-collapse.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-cascade-isolated-threshold.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-balanced-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-balanced-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-balanced-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-mild-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-mild-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-mild-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-threshold-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-threshold-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-threshold-nominal-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-deep-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-deep-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9-overaggressive-growth/grcl9-cell-full-capacity-phase-deep-nominal-growth.seed.yaml"),
)
GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES = (
    "growth_pressure_lambda_high",
    "growth_pressure_lambda_low",
    "cell_internal_valley_transport_growth_high",
    "cell_support_loss_identity_decay_probe",
    "cell_full_capacity_phenomenology_cascade",
    "cell_full_capacity_cascade_low_growth",
    "cell_full_capacity_cascade_high_growth",
    "cell_full_capacity_cascade_no_merge_bridge",
    "cell_full_capacity_cascade_weak_merge_bridge",
    "cell_full_capacity_cascade_isolated_bridge",
    "cell_full_capacity_cascade_larger_basin_support",
    "cell_full_capacity_cascade_no_refinement",
    "cell_full_capacity_cascade_no_growth",
    "cell_full_capacity_cascade_balanced_basins",
    "cell_full_capacity_cascade_mild_asymmetry",
    "cell_full_capacity_cascade_threshold_asymmetry",
    "cell_full_capacity_cascade_deep_collapse",
    "cell_full_capacity_cascade_isolated_threshold",
    "cell_full_capacity_phase_balanced_no_growth",
    "cell_full_capacity_phase_balanced_low_growth",
    "cell_full_capacity_phase_balanced_nominal_growth",
    "cell_full_capacity_phase_mild_no_growth",
    "cell_full_capacity_phase_mild_low_growth",
    "cell_full_capacity_phase_mild_nominal_growth",
    "cell_full_capacity_phase_threshold_no_growth",
    "cell_full_capacity_phase_threshold_low_growth",
    "cell_full_capacity_phase_threshold_nominal_growth",
    "cell_full_capacity_phase_deep_no_growth",
    "cell_full_capacity_phase_deep_low_growth",
    "cell_full_capacity_phase_deep_nominal_growth",
)

_SEED_TOP_LEVEL_ALLOWED_KEYS = frozenset(
    {
        "contract_version",
        "grcl9_required",
        "example_name",
        "manifest_entry_id",
        "expected_selector_ids",
        "non_claims",
        "notes",
    }
)

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_FORBIDDEN_EXAMPLE_KEYS = frozenset(
    {
        "basins",
        "birth_event",
        "current_flux",
        "edge_id",
        "event_counts_by_kind",
        "event_history",
        "event_rows",
        "events",
        "expansion_completed",
        "fission_confirmed",
        "flux_uv",
        "graph_checkpoint",
        "growth_count",
        "node_id",
        "port_edge",
        "port_edges",
        "runtime_events",
        "solved_diagnostic",
        "solved_flux",
        "spark_happened",
        "step_rows",
        "telemetry_summary",
        "topology",
    }
)


def _require_string(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _require_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _require_float(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{field_name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be finite")
    return result


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    _validate_no_forbidden_example_fields(value, field_name=field_name)
    return value


def _require_sequence(value: Any, *, field_name: str) -> Sequence[Any]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence")
    return value


def _string_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    return tuple(
        _require_string(item, field_name=f"{field_name}[{index}]")
        for index, item in enumerate(_require_sequence(value, field_name=field_name))
    )


def _validate_token(value: str, *, field_name: str) -> None:
    _require_string(value, field_name=field_name)
    if not _TOKEN_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use lowercase snake-case tokens")


def _validate_port(value: int, *, field_name: str) -> None:
    if value < 1 or value > 9:
        raise ValueError(f"{field_name} must be in the GRC9 port range [1, 9]")


def _validate_column(value: int, *, field_name: str) -> None:
    if value < 1 or value > 3:
        raise ValueError(f"{field_name} must be one of the three GRC9 columns")


def _validate_no_forbidden_example_fields(value: Any, *, field_name: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_EXAMPLE_KEYS:
                raise ValueError(f"{field_name}.{key_text} is not allowed in GRCL-9 examples")
            _validate_no_forbidden_example_fields(item, field_name=f"{field_name}.{key_text}")
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for index, item in enumerate(value):
            _validate_no_forbidden_example_fields(item, field_name=f"{field_name}[{index}]")


def _validate_no_forbidden_example_text(value: str, *, field_name: str) -> None:
    for forbidden in _FORBIDDEN_EXAMPLE_KEYS:
        if forbidden in value:
            raise ValueError(
                f"{field_name} contains {forbidden!r}, which is not allowed in GRCL-9 examples"
            )


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


@dataclass(frozen=True)
class _LandscapeTermBase:
    term_id: str
    motif_id: str
    non_claims: tuple[str, ...] = GRCL9_BASE_NON_CLAIMS

    def __post_init__(self) -> None:
        _validate_token(self.term_id, field_name="term_id")
        _validate_token(self.motif_id, field_name="motif_id")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")

    def _base_mapping(self, term_kind: str) -> dict[str, Any]:
        return {
            "term_kind": term_kind,
            "term_id": self.term_id,
            "motif_id": self.motif_id,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class GRCL9CriticalRegion(_LandscapeTermBase):
    """Morse-facing critical region that may compile to a spark-capable chart."""

    region_id: str = ""
    stability_intent: str = "critical"
    coherence_profile: Mapping[str, Any] | None = None
    boundary_gradient_profile: Mapping[str, Any] | None = None
    columnwise_near_cancellation: Mapping[str, Any] | None = None
    spark_gate_intent: str = "saturation_column_proxy"

    term_kind = "critical_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.region_id, field_name="region_id")
        _validate_token(self.stability_intent, field_name="stability_intent")
        _require_mapping(self.coherence_profile or {}, field_name="coherence_profile")
        _require_mapping(self.boundary_gradient_profile or {}, field_name="boundary_gradient_profile")
        _require_mapping(
            self.columnwise_near_cancellation or {},
            field_name="columnwise_near_cancellation",
        )
        if self.spark_gate_intent not in {
            "saturation_column_proxy",
            "saturation_instability",
        }:
            raise ValueError("spark_gate_intent must align with executable GRC9 spark kinds")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "region_id": self.region_id,
                "stability_intent": self.stability_intent,
                "coherence_profile": _json_safe(self.coherence_profile or {}),
                "boundary_gradient_profile": _json_safe(self.boundary_gradient_profile or {}),
                "columnwise_near_cancellation": _json_safe(
                    self.columnwise_near_cancellation or {}
                ),
                "spark_gate_intent": self.spark_gate_intent,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9CriticalRegion":
        mapping = _require_mapping(value, field_name="critical_region")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            region_id=_require_string(mapping.get("region_id"), field_name="region_id"),
            stability_intent=_require_string(
                mapping.get("stability_intent", "critical"),
                field_name="stability_intent",
            ),
            coherence_profile=dict(
                _require_mapping(mapping.get("coherence_profile", {}), field_name="coherence_profile")
            ),
            boundary_gradient_profile=dict(
                _require_mapping(
                    mapping.get("boundary_gradient_profile", {}),
                    field_name="boundary_gradient_profile",
                )
            ),
            columnwise_near_cancellation=dict(
                _require_mapping(
                    mapping.get("columnwise_near_cancellation", {}),
                    field_name="columnwise_near_cancellation",
                )
            ),
            spark_gate_intent=_require_string(
                mapping.get("spark_gate_intent", "saturation_column_proxy"),
                field_name="spark_gate_intent",
            ),
        )


@dataclass(frozen=True)
class GRCL9StableBasin(_LandscapeTermBase):
    """Morse-facing stable basin region."""

    basin_id: str = ""
    stability_class: str = "stable"
    mass_hint: float = 0.5
    support_node_count: int = 1
    selection_policy: str = "member_node"

    term_kind = "stable_basin"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.basin_id, field_name="basin_id")
        _validate_token(self.stability_class, field_name="stability_class")
        if _require_float(self.mass_hint, field_name="mass_hint") < 0.0:
            raise ValueError("mass_hint must be non-negative")
        if _require_int(self.support_node_count, field_name="support_node_count") < 1:
            raise ValueError("support_node_count must be positive")
        _validate_token(self.selection_policy, field_name="selection_policy")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "basin_id": self.basin_id,
                "stability_class": self.stability_class,
                "mass_hint": self.mass_hint,
                "support_node_count": self.support_node_count,
                "selection_policy": self.selection_policy,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9StableBasin":
        mapping = _require_mapping(value, field_name="stable_basin")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            basin_id=_require_string(mapping.get("basin_id"), field_name="basin_id"),
            stability_class=_require_string(
                mapping.get("stability_class", "stable"),
                field_name="stability_class",
            ),
            mass_hint=_require_float(mapping.get("mass_hint", 0.5), field_name="mass_hint"),
            support_node_count=_require_int(
                mapping.get("support_node_count", 1),
                field_name="support_node_count",
            ),
            selection_policy=_require_string(
                mapping.get("selection_policy", "member_node"),
                field_name="selection_policy",
            ),
        )


@dataclass(frozen=True)
class GRCL9UnstableDirection(_LandscapeTermBase):
    """Morse-facing unstable direction near a critical region."""

    direction_id: str = ""
    region_id: str = ""
    axis_role: str = "row_1"
    support_class: str = "weak_support"
    cut_class: str = "high_cut"
    tau_instability: float = 0.25

    term_kind = "unstable_direction"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.direction_id, field_name="direction_id")
        _validate_token(self.region_id, field_name="region_id")
        _validate_token(self.axis_role, field_name="axis_role")
        _validate_token(self.support_class, field_name="support_class")
        _validate_token(self.cut_class, field_name="cut_class")
        if _require_float(self.tau_instability, field_name="tau_instability") < 0.0:
            raise ValueError("tau_instability must be non-negative")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "direction_id": self.direction_id,
                "region_id": self.region_id,
                "axis_role": self.axis_role,
                "support_class": self.support_class,
                "cut_class": self.cut_class,
                "tau_instability": self.tau_instability,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9UnstableDirection":
        mapping = _require_mapping(value, field_name="unstable_direction")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            direction_id=_require_string(mapping.get("direction_id"), field_name="direction_id"),
            region_id=_require_string(mapping.get("region_id"), field_name="region_id"),
            axis_role=_require_string(mapping.get("axis_role", "row_1"), field_name="axis_role"),
            support_class=_require_string(
                mapping.get("support_class", "weak_support"),
                field_name="support_class",
            ),
            cut_class=_require_string(mapping.get("cut_class", "high_cut"), field_name="cut_class"),
            tau_instability=_require_float(
                mapping.get("tau_instability", 0.25),
                field_name="tau_instability",
            ),
        )


@dataclass(frozen=True)
class GRCL9Separatrix(_LandscapeTermBase):
    """Morse-facing separator between regions."""

    separatrix_id: str = ""
    region_a: str = ""
    region_b: str = ""
    conductance_class: str = "separating"

    term_kind = "separatrix"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.separatrix_id, field_name="separatrix_id")
        _validate_token(self.region_a, field_name="region_a")
        _validate_token(self.region_b, field_name="region_b")
        if self.region_a == self.region_b:
            raise ValueError("separatrix regions must be distinct")
        _validate_token(self.conductance_class, field_name="conductance_class")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "separatrix_id": self.separatrix_id,
                "region_a": self.region_a,
                "region_b": self.region_b,
                "conductance_class": self.conductance_class,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9Separatrix":
        mapping = _require_mapping(value, field_name="separatrix")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            separatrix_id=_require_string(mapping.get("separatrix_id"), field_name="separatrix_id"),
            region_a=_require_string(mapping.get("region_a"), field_name="region_a"),
            region_b=_require_string(mapping.get("region_b"), field_name="region_b"),
            conductance_class=_require_string(
                mapping.get("conductance_class", "separating"),
                field_name="conductance_class",
            ),
        )


@dataclass(frozen=True)
class GRCL9SaddleBridge(_LandscapeTermBase):
    """Morse-facing weak bridge/saddle relation."""

    bridge_id: str = ""
    region_a: str = ""
    region_b: str = ""
    bridge_class: str = "weak_saddle_bridge"

    term_kind = "saddle_bridge"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.bridge_id, field_name="bridge_id")
        _validate_token(self.region_a, field_name="region_a")
        _validate_token(self.region_b, field_name="region_b")
        if self.region_a == self.region_b:
            raise ValueError("bridge regions must be distinct")
        _validate_token(self.bridge_class, field_name="bridge_class")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "bridge_id": self.bridge_id,
                "region_a": self.region_a,
                "region_b": self.region_b,
                "bridge_class": self.bridge_class,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9SaddleBridge":
        mapping = _require_mapping(value, field_name="saddle_bridge")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            bridge_id=_require_string(mapping.get("bridge_id"), field_name="bridge_id"),
            region_a=_require_string(mapping.get("region_a"), field_name="region_a"),
            region_b=_require_string(mapping.get("region_b"), field_name="region_b"),
            bridge_class=_require_string(
                mapping.get("bridge_class", "weak_saddle_bridge"),
                field_name="bridge_class",
            ),
        )


@dataclass(frozen=True)
class GRCL9BoundaryStratum(_LandscapeTermBase):
    """Morse-facing boundary stratum for growth loci."""

    stratum_id: str = ""
    parent_region_id: str = ""
    inactive_port: int = 5
    boundary_role: str = "growth_boundary"

    term_kind = "boundary_stratum"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.stratum_id, field_name="stratum_id")
        _validate_token(self.parent_region_id, field_name="parent_region_id")
        _validate_port(self.inactive_port, field_name="inactive_port")
        _validate_token(self.boundary_role, field_name="boundary_role")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "stratum_id": self.stratum_id,
                "parent_region_id": self.parent_region_id,
                "inactive_port": self.inactive_port,
                "boundary_role": self.boundary_role,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9BoundaryStratum":
        mapping = _require_mapping(value, field_name="boundary_stratum")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            stratum_id=_require_string(mapping.get("stratum_id"), field_name="stratum_id"),
            parent_region_id=_require_string(
                mapping.get("parent_region_id"),
                field_name="parent_region_id",
            ),
            inactive_port=_require_int(mapping.get("inactive_port", 5), field_name="inactive_port"),
            boundary_role=_require_string(
                mapping.get("boundary_role", "growth_boundary"),
                field_name="boundary_role",
            ),
        )


@dataclass(frozen=True)
class GRCL9GradientPressure(_LandscapeTermBase):
    """Morse-facing outward gradient/flux pressure declaration."""

    pressure_id: str = ""
    boundary_stratum_id: str = ""
    pressure_class: str = "high"
    lambda_birth: float = 1.0
    growth_semantics: str = "legacy_growth_locus"
    front_capacity_source: str = "legacy_source_growth_locus"
    front_source_construct_id: str | None = None

    term_kind = "gradient_pressure"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.pressure_id, field_name="pressure_id")
        _validate_token(self.boundary_stratum_id, field_name="boundary_stratum_id")
        _validate_token(self.pressure_class, field_name="pressure_class")
        if _require_float(self.lambda_birth, field_name="lambda_birth") < 0.0:
            raise ValueError("lambda_birth must be non-negative")
        _validate_token(self.growth_semantics, field_name="growth_semantics")
        _validate_token(self.front_capacity_source, field_name="front_capacity_source")
        if self.front_source_construct_id is not None:
            _validate_token(self.front_source_construct_id, field_name="front_source_construct_id")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "pressure_id": self.pressure_id,
                "boundary_stratum_id": self.boundary_stratum_id,
                "pressure_class": self.pressure_class,
                "lambda_birth": self.lambda_birth,
                "growth_semantics": self.growth_semantics,
                "front_capacity_source": self.front_capacity_source,
            }
        )
        if self.front_source_construct_id is not None:
            payload["front_source_construct_id"] = self.front_source_construct_id
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9GradientPressure":
        mapping = _require_mapping(value, field_name="gradient_pressure")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            pressure_id=_require_string(mapping.get("pressure_id"), field_name="pressure_id"),
            boundary_stratum_id=_require_string(
                mapping.get("boundary_stratum_id"),
                field_name="boundary_stratum_id",
            ),
            pressure_class=_require_string(mapping.get("pressure_class", "high"), field_name="pressure_class"),
            lambda_birth=_require_float(mapping.get("lambda_birth", 1.0), field_name="lambda_birth"),
            growth_semantics=_require_string(
                mapping.get("growth_semantics", "legacy_growth_locus"),
                field_name="growth_semantics",
            ),
            front_capacity_source=_require_string(
                mapping.get("front_capacity_source", "legacy_source_growth_locus"),
                field_name="front_capacity_source",
            ),
            front_source_construct_id=(
                None
                if mapping.get("front_source_construct_id") is None
                else _require_string(mapping.get("front_source_construct_id"), field_name="front_source_construct_id")
            ),
        )


@dataclass(frozen=True)
class GRCL9RefinementLocus(_LandscapeTermBase):
    """Morse-facing refinement locus."""

    locus_id: str = ""
    region_id: str = ""
    target_effective_degree: int = 16
    coherence_transfer_mode: str = "equal"

    term_kind = "refinement_locus"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.locus_id, field_name="locus_id")
        _validate_token(self.region_id, field_name="region_id")
        if _require_int(self.target_effective_degree, field_name="target_effective_degree") <= 0:
            raise ValueError("target_effective_degree must be positive")
        _validate_token(self.coherence_transfer_mode, field_name="coherence_transfer_mode")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "locus_id": self.locus_id,
                "region_id": self.region_id,
                "target_effective_degree": self.target_effective_degree,
                "coherence_transfer_mode": self.coherence_transfer_mode,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9RefinementLocus":
        mapping = _require_mapping(value, field_name="refinement_locus")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            locus_id=_require_string(mapping.get("locus_id"), field_name="locus_id"),
            region_id=_require_string(mapping.get("region_id"), field_name="region_id"),
            target_effective_degree=_require_int(
                mapping.get("target_effective_degree", 16),
                field_name="target_effective_degree",
            ),
            coherence_transfer_mode=_require_string(
                mapping.get("coherence_transfer_mode", "equal"),
                field_name="coherence_transfer_mode",
            ),
        )


@dataclass(frozen=True)
class GRCL9PostRefinementTwoSinkRegion(_LandscapeTermBase):
    """Morse-facing post-refinement two-sink candidate region."""

    region_id: str = ""
    module_region_id: str = "module"
    sink_region_a: str = "sink_a"
    sink_region_b: str = "sink_b"
    identity_fission_min_basin_mass: float = 0.1
    identity_fission_persistence_delta: int = 3

    term_kind = "post_refinement_two_sink_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.region_id, field_name="region_id")
        _validate_token(self.module_region_id, field_name="module_region_id")
        _validate_token(self.sink_region_a, field_name="sink_region_a")
        _validate_token(self.sink_region_b, field_name="sink_region_b")
        if self.sink_region_a == self.sink_region_b:
            raise ValueError("sink regions must be distinct")
        if _require_float(
            self.identity_fission_min_basin_mass,
            field_name="identity_fission_min_basin_mass",
        ) < 0.0:
            raise ValueError("identity_fission_min_basin_mass must be non-negative")
        if _require_int(
            self.identity_fission_persistence_delta,
            field_name="identity_fission_persistence_delta",
        ) < 0:
            raise ValueError("identity_fission_persistence_delta must be non-negative")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.term_kind)
        payload.update(
            {
                "region_id": self.region_id,
                "module_region_id": self.module_region_id,
                "sink_region_a": self.sink_region_a,
                "sink_region_b": self.sink_region_b,
                "identity_fission_min_basin_mass": self.identity_fission_min_basin_mass,
                "identity_fission_persistence_delta": self.identity_fission_persistence_delta,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9PostRefinementTwoSinkRegion":
        mapping = _require_mapping(value, field_name="post_refinement_two_sink_region")
        return cls(
            term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            region_id=_require_string(mapping.get("region_id"), field_name="region_id"),
            module_region_id=_require_string(
                mapping.get("module_region_id", "module"),
                field_name="module_region_id",
            ),
            sink_region_a=_require_string(mapping.get("sink_region_a", "sink_a"), field_name="sink_region_a"),
            sink_region_b=_require_string(mapping.get("sink_region_b", "sink_b"), field_name="sink_region_b"),
            identity_fission_min_basin_mass=_require_float(
                mapping.get("identity_fission_min_basin_mass", 0.1),
                field_name="identity_fission_min_basin_mass",
            ),
            identity_fission_persistence_delta=_require_int(
                mapping.get("identity_fission_persistence_delta", 3),
                field_name="identity_fission_persistence_delta",
            ),
        )


GRCL9LandscapeTerm = (
    GRCL9CriticalRegion
    | GRCL9StableBasin
    | GRCL9UnstableDirection
    | GRCL9Separatrix
    | GRCL9SaddleBridge
    | GRCL9BoundaryStratum
    | GRCL9GradientPressure
    | GRCL9RefinementLocus
    | GRCL9PostRefinementTwoSinkRegion
)

_TERM_BY_KIND = {
    GRCL9CriticalRegion.term_kind: GRCL9CriticalRegion,
    GRCL9StableBasin.term_kind: GRCL9StableBasin,
    GRCL9UnstableDirection.term_kind: GRCL9UnstableDirection,
    GRCL9Separatrix.term_kind: GRCL9Separatrix,
    GRCL9SaddleBridge.term_kind: GRCL9SaddleBridge,
    GRCL9BoundaryStratum.term_kind: GRCL9BoundaryStratum,
    GRCL9GradientPressure.term_kind: GRCL9GradientPressure,
    GRCL9RefinementLocus.term_kind: GRCL9RefinementLocus,
    GRCL9PostRefinementTwoSinkRegion.term_kind: GRCL9PostRefinementTwoSinkRegion,
}


def grcl9_landscape_term_from_mapping(value: Mapping[str, Any]) -> GRCL9LandscapeTerm:
    """Parse one GRCL-9 landscape example term."""

    mapping = _require_mapping(value, field_name="landscape_term")
    term_kind = _require_string(mapping.get("term_kind"), field_name="term_kind")
    parser = _TERM_BY_KIND.get(term_kind)
    if parser is None:
        raise ValueError(f"unsupported GRCL-9 landscape term kind {term_kind!r}")
    return parser.from_mapping(mapping)


def extract_grcl9_landscape_example_from_seed(
    seed: LandscapeSeed,
    *,
    seed_path: str | Path | None = None,
) -> GRCL9LandscapeExampleDocument | None:
    """Extract one GRCL-9 landscape example from a normalized seed.

    This mirrors the GRCL-V3 rich-extension boundary: neutral seeds with no
    `extensions.grcl9` are ignored, while seeds declaring GRCL-9 intent must
    carry a supported contract version and `grcl9_required = true`.
    """

    raw_top_level = seed.extensions.get("grcl9")
    primitive_payloads = tuple(
        (primitive.id, primitive.extensions.get("grcl9"))
        for primitive in seed.primitives
        if isinstance(primitive.extensions, Mapping) and "grcl9" in primitive.extensions
    )
    if raw_top_level is None and not primitive_payloads:
        return None
    if raw_top_level is None:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9 is required when primitive-level grcl9 "
            "extensions are present"
        )
    if not isinstance(raw_top_level, Mapping):
        raise InvalidLandscapeSeedError("seed.extensions.grcl9 must be a mapping")
    top_level = dict(raw_top_level)
    unknown = set(top_level) - _SEED_TOP_LEVEL_ALLOWED_KEYS
    if unknown:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9 contains unsupported keys: "
            + ", ".join(sorted(str(key) for key in unknown))
        )
    contract_version = top_level.get("contract_version")
    if contract_version != GRCL9_LANDSCAPE_EXAMPLE_VERSION:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9.contract_version must be "
            f"{GRCL9_LANDSCAPE_EXAMPLE_VERSION!r}"
        )
    if top_level.get("grcl9_required") is not True:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9.grcl9_required must be true"
        )

    terms = []
    for primitive_id, raw_extension in primitive_payloads:
        if not isinstance(raw_extension, Mapping):
            raise InvalidLandscapeSeedError(
                f"primitive[{primitive_id}].extensions.grcl9 must be a mapping"
            )
        if "term_kind" not in raw_extension:
            raise InvalidLandscapeSeedError(
                f"primitive[{primitive_id}].extensions.grcl9.term_kind is required"
            )
        try:
            terms.append(grcl9_landscape_term_from_mapping(raw_extension))
        except ValueError as exc:
            raise InvalidLandscapeSeedError(
                f"invalid primitive[{primitive_id}].extensions.grcl9 term"
            ) from exc
    if not terms:
        raise InvalidLandscapeSeedError(
            "GRCL-9 landscape seed examples require at least one primitive term"
        )

    try:
        return GRCL9LandscapeExampleDocument(
            example_name=_require_string(
                top_level.get("example_name"),
                field_name="seed.extensions.grcl9.example_name",
            ),
            manifest_entry_id=_require_string(
                top_level.get("manifest_entry_id"),
                field_name="seed.extensions.grcl9.manifest_entry_id",
            ),
            expected_selector_ids=_string_tuple(
                top_level.get("expected_selector_ids", ()),
                field_name="seed.extensions.grcl9.expected_selector_ids",
            ),
            terms=tuple(terms),
            non_claims=_string_tuple(
                top_level.get("non_claims", GRCL9_BASE_NON_CLAIMS),
                field_name="seed.extensions.grcl9.non_claims",
            ),
            source_seed_reference=(
                str(seed_path)
                if seed_path is not None
                else (seed.meta.source_reference or seed.meta.name)
            ),
            notes=str(top_level.get("notes", "")),
        )
    except ValueError as exc:
        raise InvalidLandscapeSeedError("invalid GRCL-9 landscape seed example") from exc


def load_grcl9_landscape_seed_example(
    path: str | Path,
) -> GRCL9LandscapeExampleDocument:
    """Load a seed-backed GRCL-9 landscape example."""

    seed_path = Path(path)
    example = extract_grcl9_landscape_example_from_seed(
        load_landscape_seed(seed_path),
        seed_path=seed_path,
    )
    if example is None:
        raise InvalidLandscapeSeedError(
            f"landscape seed {seed_path} does not declare a GRCL-9 example"
        )
    return example


def default_grcl9_landscape_seed_examples(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9LandscapeExampleDocument, ...]:
    """Load the built-in GRCL-9 seed-backed examples."""

    return _load_grcl9_landscape_seed_examples(
        root=root,
        paths=GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS,
        names=GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
        label="GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES",
    )


def legacy_grcl9_growth_landscape_seed_examples(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9LandscapeExampleDocument, ...]:
    """Load quarantined legacy standalone-growth GRCL-9 seed examples."""

    return _load_grcl9_landscape_seed_examples(
        root=root,
        paths=GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS,
        names=GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
        label="GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES",
    )


def _load_grcl9_landscape_seed_examples(
    *,
    root: str | Path,
    paths: Sequence[Path],
    names: Sequence[str],
    label: str,
) -> tuple[GRCL9LandscapeExampleDocument, ...]:
    """Load and validate a GRCL-9 seed example collection."""

    base = Path(root)
    examples = tuple(
        load_grcl9_landscape_seed_example(base / path)
        for path in paths
    )
    if tuple(example.example_name for example in examples) != tuple(names):
        raise AssertionError(f"seed-example ordering drifted from {label}")
    return examples


def grcl9_landscape_seed_example_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, GRCL9LandscapeExampleDocument]:
    """Return built-in seed-backed examples keyed by example name."""

    return {
        example.example_name: example
        for example in default_grcl9_landscape_seed_examples(root=root)
    }


def grcl9_landscape_seed_example_path_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, Path]:
    """Return built-in seed-backed example paths keyed by example name."""

    examples = grcl9_landscape_seed_example_by_name(root=root)
    base = Path(root)
    return {
        name: base / path
        for name, path in zip(
            GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
            GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS,
            strict=True,
        )
        if name in examples
    }


def legacy_grcl9_growth_landscape_seed_example_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, GRCL9LandscapeExampleDocument]:
    """Return quarantined legacy growth seed examples keyed by example name."""

    return {
        example.example_name: example
        for example in legacy_grcl9_growth_landscape_seed_examples(root=root)
    }


def legacy_grcl9_growth_landscape_seed_example_path_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, Path]:
    """Return quarantined legacy growth seed paths keyed by example name."""

    examples = legacy_grcl9_growth_landscape_seed_example_by_name(root=root)
    base = Path(root)
    return {
        name: base / path
        for name, path in zip(
            GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
            GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS,
            strict=True,
        )
        if name in examples
    }


@dataclass(frozen=True)
class GRCL9LandscapeExampleDocument:
    """One GRCL/Morse-facing source example before mechanical GRCL-9 lowering."""

    example_name: str
    manifest_entry_id: str
    terms: tuple[GRCL9LandscapeTerm, ...]
    example_schema_version: str = GRCL9_LANDSCAPE_EXAMPLE_VERSION
    grcl9_required: bool = True
    expected_selector_ids: tuple[str, ...] = ()
    expected_telemetry: tuple[Any, ...] = ()
    non_claims: tuple[str, ...] = GRCL9_BASE_NON_CLAIMS
    source_seed_reference: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.example_schema_version != GRCL9_LANDSCAPE_EXAMPLE_VERSION:
            raise ValueError(
                f"example_schema_version must be {GRCL9_LANDSCAPE_EXAMPLE_VERSION!r}"
            )
        _validate_token(self.example_name, field_name="example_name")
        _validate_token(self.manifest_entry_id, field_name="manifest_entry_id")
        if not _require_bool(self.grcl9_required, field_name="grcl9_required"):
            raise ValueError("GRCL-9 landscape examples require grcl9_required = true")
        if not self.terms:
            raise ValueError("terms must not be empty")
        term_ids = [term.term_id for term in self.terms]
        if len(term_ids) != len(set(term_ids)):
            raise ValueError("term_id values must be unique")
        for selector_id in self.expected_selector_ids:
            _validate_token(selector_id, field_name="expected_selector_ids[]")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")
        if self.source_seed_reference is not None:
            _require_string(
                self.source_seed_reference,
                field_name="source_seed_reference",
            )
        _validate_no_forbidden_example_text(self.notes, field_name="notes")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = {
            "example_schema_version": self.example_schema_version,
            "example_name": self.example_name,
            "manifest_entry_id": self.manifest_entry_id,
            "grcl9_required": self.grcl9_required,
            "expected_selector_ids": list(self.expected_selector_ids),
            "terms": [term.to_mapping() for term in self.terms],
            "expected_telemetry": [
                item.to_mapping() if hasattr(item, "to_mapping") else _json_safe(item)
                for item in self.expected_telemetry
            ],
            "non_claims": list(self.non_claims),
            "notes": self.notes,
        }
        if self.source_seed_reference is not None:
            payload["source_seed_reference"] = self.source_seed_reference
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GRCL9LandscapeExampleDocument":
        mapping = _require_mapping(value, field_name="landscape_example")
        return cls(
            example_schema_version=_require_string(
                mapping.get("example_schema_version", GRCL9_LANDSCAPE_EXAMPLE_VERSION),
                field_name="example_schema_version",
            ),
            example_name=_require_string(mapping.get("example_name"), field_name="example_name"),
            manifest_entry_id=_require_string(
                mapping.get("manifest_entry_id"),
                field_name="manifest_entry_id",
            ),
            grcl9_required=_require_bool(mapping.get("grcl9_required", False), field_name="grcl9_required"),
            expected_selector_ids=_string_tuple(
                mapping.get("expected_selector_ids", ()),
                field_name="expected_selector_ids",
            ),
            terms=tuple(
                grcl9_landscape_term_from_mapping(item)
                for item in _require_sequence(mapping.get("terms", ()), field_name="terms")
            ),
            expected_telemetry=tuple(mapping.get("expected_telemetry", ())),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            source_seed_reference=(
                None
                if mapping.get("source_seed_reference") is None
                else _require_string(
                    mapping.get("source_seed_reference"),
                    field_name="source_seed_reference",
                )
            ),
            notes=str(mapping.get("notes", "")),
        )


def compile_grcl9_landscape_example_to_source(
    example: GRCL9LandscapeExampleDocument | Mapping[str, Any],
) -> GRCL9SourceDocument:
    """Compile a GRCL/Morse-facing example into a mechanical GRCL-9 source."""

    document = (
        example
        if isinstance(example, GRCL9LandscapeExampleDocument)
        else GRCL9LandscapeExampleDocument.from_mapping(example)
    )
    manifest_entry = default_grcl9_lowering_manifest().by_entry_id().get(
        document.manifest_entry_id
    )
    if manifest_entry is None:
        raise ValueError(f"unknown GRCL-9 manifest entry {document.manifest_entry_id!r}")
    controls = [
        control
        for control in manifest_entry.controls
        if control.source_fixture_name == document.example_name
    ]
    if len(controls) > 1:
        raise ValueError(
            f"example {document.example_name!r} must match one pass/fail control in "
            f"{manifest_entry.entry_id!r}"
        )
    selector_ids = tuple(document.expected_selector_ids)
    if len(controls) == 1 and not selector_ids:
        selector_ids = controls[0].selector_ids
    if not selector_ids:
        raise ValueError(
            f"example {document.example_name!r} is not a manifest control and must "
            "declare expected_selector_ids"
        )
    constructs, construct_term_map = _compile_terms(document)
    return GRCL9SourceDocument(
        fixture_name=document.example_name,
        manifest_entry_id=document.manifest_entry_id,
        expected_selector_ids=selector_ids,
        bridge_policy=GRCL9BridgePolicy(conductance_hint=0.001),
        constructs=constructs,
        expected_telemetry=manifest_entry.expected_telemetry,
        non_claims=document.non_claims,
        compiled_source_provenance={
            "source_example_schema_version": document.example_schema_version,
            "source_example_name": document.example_name,
            "source_seed_reference": document.source_seed_reference,
            "source_terms": [term.to_mapping() for term in document.terms],
            "source_term_ids_by_construct_id": construct_term_map,
            "compiler": "compile_grcl9_landscape_example_to_source",
        },
        notes=(
            "Compiled from GRCL/Morse-facing landscape example; source terms "
            "declare preconditions and intent only."
        ),
    )


def compile_default_grcl9_landscape_examples_to_sources() -> tuple[GRCL9SourceDocument, ...]:
    """Compile all built-in GRCL-9 landscape examples."""

    return tuple(
        compile_grcl9_landscape_example_to_source(example)
        for example in default_grcl9_landscape_examples()
    )


def compile_default_grcl9_landscape_seed_examples_to_sources(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9SourceDocument, ...]:
    """Compile all built-in seed-backed GRCL-9 landscape examples."""

    return tuple(
        compile_grcl9_landscape_example_to_source(example)
        for example in default_grcl9_landscape_seed_examples(root=root)
    )


def compile_legacy_grcl9_growth_landscape_seed_examples_to_sources(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9SourceDocument, ...]:
    """Compile quarantined legacy growth seeds for diagnostic replay."""

    return tuple(
        compile_grcl9_landscape_example_to_source(example)
        for example in legacy_grcl9_growth_landscape_seed_examples(root=root)
    )


def default_grcl9_landscape_examples() -> tuple[GRCL9LandscapeExampleDocument, ...]:
    """Return the built-in GRCL/Morse-facing GRCL-9 examples."""

    manifest = default_grcl9_lowering_manifest().by_seed_family()
    examples = (
        _column_proxy_example(
            "spark_column_proxy_eps_pass",
            manifest["spark_column_proxy_emitter"].entry_id,
            diagnostic_mode="near_epsilon",
        ),
        _column_proxy_example(
            "spark_column_proxy_eps_fail",
            manifest["spark_column_proxy_emitter"].entry_id,
            diagnostic_mode="off_epsilon",
        ),
        _instability_example(
            "spark_instability_tau_pass",
            manifest["spark_instability_emitter"].entry_id,
            tau_instability=0.25,
            support_class="weak_support",
            cut_class="high_cut",
        ),
        _instability_example(
            "spark_instability_tau_fail",
            manifest["spark_instability_emitter"].entry_id,
            tau_instability=0.95,
            support_class="balanced_support",
            cut_class="balanced_cut",
        ),
        _expansion_example(
            "spark_to_expansion_d_eff_low",
            manifest["spark_to_expansion_emitter"].entry_id,
            target_effective_degree=16,
        ),
        _expansion_example(
            "spark_to_expansion_d_eff_high",
            manifest["spark_to_expansion_emitter"].entry_id,
            target_effective_degree=44,
        ),
        _corrected_front_growth_example(
            "corrected_front_growth_positive_high",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="controlled_high",
            lambda_birth=100.0,
        ),
        _corrected_front_growth_example(
            "corrected_pressure_boundary_positive_high",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="controlled_high",
            lambda_birth=100.0,
            boundary_role="pressure_boundary",
            front_capacity_source="pressure_boundary",
            front_source_construct_id=None,
            selector_ids=("growth_count", "pressure_boundary_growth_provenance"),
        ),
        _corrected_front_growth_example(
            "corrected_front_growth_no_growth_low",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="controlled_high",
            lambda_birth=0.0,
        ),
        _corrected_front_growth_example(
            "corrected_front_growth_no_front_fail",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="no_front_capacity",
            lambda_birth=100.0,
            boundary_role="no_front_capacity",
            front_capacity_source="preexisting_front",
            front_source_construct_id=None,
        ),
        _corrected_front_growth_example(
            "corrected_front_growth_closed_front_fail",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="closed_front",
            lambda_birth=100.0,
            boundary_role="closed_spark_refinement_front",
        ),
        _growth_example(
            "growth_pressure_lambda_high",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="high",
            lambda_birth=2.0,
        ),
        _growth_example(
            "growth_pressure_lambda_low",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="low",
            lambda_birth=0.05,
        ),
        _fission_example(
            "post_expansion_fission_min_mass_pass",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.0,
        ),
        _fission_example(
            "post_expansion_fission_min_mass_fail",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.90,
        ),
        _column_proxy_example(
            "cell_boundary_ridge_membrane_spark_pass",
            manifest["spark_column_proxy_emitter"].entry_id,
            diagnostic_mode="near_epsilon",
            selector_ids=("spark_column_proxy_count",),
        ),
        _growth_example(
            "cell_internal_valley_transport_growth_high",
            manifest["growth_pressure_emitter"].entry_id,
            pressure_class="high",
            lambda_birth=2.0,
            selector_ids=("growth_count",),
        ),
        _fission_example(
            "cell_plateau_nested_basins_fission_pass",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.0,
            selector_ids=("fission_confirmed_count",),
        ),
        _instability_example(
            "cell_saddle_branch_instability_pass",
            manifest["spark_instability_emitter"].entry_id,
            tau_instability=0.25,
            support_class="weak_support",
            cut_class="high_cut",
            selector_ids=("spark_instability_count",),
        ),
        _expansion_example(
            "cell_refinement_budget_partition_expansion_high",
            manifest["spark_to_expansion_emitter"].entry_id,
            target_effective_degree=44,
            selector_ids=("expansion_module_size",),
        ),
        _membrane_rupture_example(
            "cell_membrane_rupture_structural_probe",
            manifest["spark_column_proxy_emitter"].entry_id,
        ),
        _fission_example(
            "cell_basin_merge_before_persistence_probe",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.95,
            selector_ids=(
                "fission_persistence_failed_candidate",
                "basin_merge_pressure_candidate",
            ),
        ),
        _support_loss_example(
            "cell_support_loss_identity_decay_probe",
            manifest["growth_pressure_emitter"].entry_id,
        ),
        _saddle_choice_pressure_example(
            "cell_saddle_choice_pressure_structural_probe",
            manifest["spark_instability_emitter"].entry_id,
        ),
        _fission_example(
            "cell_basin_merge_runtime_collapse_probe",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.10,
            basin_a_mass=0.85,
            basin_b_mass=0.05,
            basin_b_stability="collapsing",
            bridge_class="merge_saddle_bridge",
            selector_ids=("runtime_collapse_like_observed",),
        ),
        _fission_example(
            "cell_basin_merge_runtime_stability_control",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.10,
            basin_a_mass=0.75,
            basin_b_mass=0.75,
            bridge_class="weak_saddle_bridge",
            selector_ids=("structural_only",),
        ),
        _fission_example(
            "cell_developed_basin_centroid_collapse_long_window",
            manifest["post_expansion_fission_emitter"].entry_id,
            min_basin_mass=0.10,
            basin_a_mass=0.90,
            basin_b_mass=0.04,
            basin_b_stability="collapsing",
            basin_a_support_count=6,
            basin_b_support_count=6,
            basin_a_selection_policy="group_centroid",
            bridge_class="merge_saddle_bridge",
            selector_ids=("runtime_collapse_like_long_window",),
        ),
        _cascade_example(
            "cell_full_capacity_phenomenology_cascade",
            manifest["post_expansion_fission_emitter"].entry_id,
        ),
        _cascade_example(
            "cell_full_capacity_cascade_low_growth",
            manifest["post_expansion_fission_emitter"].entry_id,
            growth_lambda_birth=0.02,
        ),
        _cascade_example(
            "cell_full_capacity_cascade_high_growth",
            manifest["post_expansion_fission_emitter"].entry_id,
            growth_lambda_birth=0.10,
        ),
        _cascade_example(
            "cell_full_capacity_cascade_no_merge_bridge",
            manifest["post_expansion_fission_emitter"].entry_id,
            bridge_class="weak_saddle_bridge",
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "structural_only",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_weak_merge_bridge",
            manifest["post_expansion_fission_emitter"].entry_id,
            bridge_class="moderate_saddle_bridge",
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "structural_only",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_isolated_bridge",
            manifest["post_expansion_fission_emitter"].entry_id,
            bridge_class="isolated_saddle_bridge",
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "structural_only",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_larger_basin_support",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_support_count=8,
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "runtime_collapse_like_ambiguous",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_no_refinement",
            manifest["post_expansion_fission_emitter"].entry_id,
            include_refinement=False,
            selector_ids=(
                "spark_column_proxy_count",
                "runtime_expansion_count",
                "growth_count",
                "runtime_collapse_like_long_window",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_no_growth",
            manifest["post_expansion_fission_emitter"].entry_id,
            include_growth=False,
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "runtime_collapse_like_long_window",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_balanced_basins",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_a_mass=0.75,
            basin_b_mass=0.75,
            basin_b_stability="stable",
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "structural_only",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_mild_asymmetry",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_a_mass=0.85,
            basin_b_mass=0.35,
            basin_b_stability="stable",
            selector_ids=(
                "spark_column_proxy_count",
                "expansion_module_size",
                "growth_count",
                "structural_only",
            ),
        ),
        _cascade_example(
            "cell_full_capacity_cascade_threshold_asymmetry",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_a_mass=0.90,
            basin_b_mass=0.12,
            basin_b_stability="weak",
        ),
        _cascade_example(
            "cell_full_capacity_cascade_deep_collapse",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_a_mass=0.90,
            basin_b_mass=0.02,
            basin_b_stability="collapsing",
        ),
        _cascade_example(
            "cell_full_capacity_cascade_isolated_threshold",
            manifest["post_expansion_fission_emitter"].entry_id,
            basin_a_mass=0.90,
            basin_b_mass=0.12,
            basin_b_stability="weak",
            bridge_class="isolated_saddle_bridge",
        ),
        *_phase_diagram_examples(manifest["post_expansion_fission_emitter"].entry_id),
    )
    if tuple(example.example_name for example in examples) != GRCL9_LANDSCAPE_EXAMPLE_NAMES:
        raise AssertionError("example ordering drifted from GRCL9_LANDSCAPE_EXAMPLE_NAMES")
    return examples


def grcl9_landscape_example_by_name() -> Mapping[str, GRCL9LandscapeExampleDocument]:
    """Return built-in GRCL-9 landscape examples keyed by example name."""

    return {example.example_name: example for example in default_grcl9_landscape_examples()}


def _compile_terms(
    document: GRCL9LandscapeExampleDocument,
) -> tuple[tuple[Any, ...], dict[str, list[str]]]:
    critical = _first(document.terms, GRCL9CriticalRegion)
    unstable = _first(document.terms, GRCL9UnstableDirection)
    refinement = _first(document.terms, GRCL9RefinementLocus)
    boundary = _first(document.terms, GRCL9BoundaryStratum)
    pressure = _first(document.terms, GRCL9GradientPressure)
    two_sink = _first(document.terms, GRCL9PostRefinementTwoSinkRegion)
    bridge = _first(document.terms, GRCL9SaddleBridge)

    construct_groups: list[tuple[Any, ...]] = []
    if critical is not None and refinement is not None:
        construct_groups.append(_compile_expansion(document, critical, refinement))
    elif critical is not None and unstable is not None:
        construct_groups.append(_compile_instability(document, critical, unstable))
    elif critical is not None:
        construct_groups.append(_compile_column_proxy(document, critical))
    if boundary is not None and pressure is not None:
        construct_groups.append(_compile_growth(document, boundary, pressure))
    if two_sink is not None and bridge is not None:
        construct_groups.append(_compile_fission(document, two_sink, bridge))
    if not construct_groups:
        raise ValueError("example terms do not form a supported GRCL-9 compiler mapping")
    constructs = tuple(construct for group in construct_groups for construct in group)

    construct_term_map = {
        construct.construct_id: list(_term_ids_for_construct(construct, document.terms))
        for construct in constructs
    }
    return constructs, construct_term_map


def _first(terms: Sequence[GRCL9LandscapeTerm], cls: type[Any]) -> Any | None:
    for term in terms:
        if isinstance(term, cls):
            return term
    return None


def _source_terms(document: GRCL9LandscapeExampleDocument, *terms: _LandscapeTermBase) -> Mapping[str, Any]:
    return {
        "example_name": document.example_name,
        "source_term_ids": [term.term_id for term in terms],
        "source_term_kinds": [term.term_kind for term in terms],
    }


def _term_ids_for_construct(construct: Any, terms: Sequence[GRCL9LandscapeTerm]) -> tuple[str, ...]:
    provenance = None
    if isinstance(construct, GRCL9SparkCandidateRegion):
        provenance = (construct.coherence_allocation or {}).get("compiled_from")
    elif isinstance(construct, GRCL9ColumnProxyProfile):
        provenance = (construct.coherence_profile or {}).get("compiled_from")
    elif isinstance(construct, GRCL9InstabilityProfile):
        provenance = (construct.support_cut_profile or {}).get("compiled_from")
    elif isinstance(construct, GRCL9ExpansionRefinementRegion):
        return tuple(term.term_id for term in terms if isinstance(term, GRCL9RefinementLocus | GRCL9CriticalRegion))
    elif isinstance(construct, GRCL9GrowthLocus):
        provenance = (construct.pressure_profile or {}).get("compiled_from")
    elif isinstance(construct, GRCL9PostExpansionFissionGeometry):
        return tuple(
            term.term_id
            for term in terms
            if isinstance(term, GRCL9PostRefinementTwoSinkRegion | GRCL9SaddleBridge | GRCL9StableBasin)
        )
    if isinstance(provenance, Mapping):
        raw_ids = provenance.get("source_term_ids", ())
        if isinstance(raw_ids, Sequence) and not isinstance(raw_ids, str):
            return tuple(str(item) for item in raw_ids)
    return tuple(term.term_id for term in terms)


def _compile_column_proxy(
    document: GRCL9LandscapeExampleDocument,
    critical: GRCL9CriticalRegion,
) -> tuple[Any, ...]:
    profile = critical.columnwise_near_cancellation or {}
    target_column = int(profile.get("target_column", 2))
    _validate_column(target_column, field_name="target_column")
    diagnostic_mode = str(profile.get("diagnostic_mode", "near_epsilon"))
    spark_threshold = float(profile.get("spark_threshold", 0.02))
    provenance = _source_terms(document, critical)
    return (
        GRCL9SparkCandidateRegion(
            construct_id=f"{document.example_name}_spark_region",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            coherence_allocation={
                "candidate": 1.0,
                "neighbors": 0.5,
                "profile": _json_safe(critical.coherence_profile or {}),
                "compiled_from": provenance,
            },
            neighbor_coherence_profile={
                "port_occupancy": "all_nine_ports",
                "boundary_gradient_profile": _json_safe(
                    critical.boundary_gradient_profile or {}
                ),
                "compiled_from": provenance,
            },
            spark_gate_intent="saturation_column_proxy",
        ),
        GRCL9ColumnProxyProfile(
            construct_id=f"{document.example_name}_column_profile",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            target_column=target_column,
            cancellation_mode=(
                "cancellation" if diagnostic_mode == "near_epsilon" else "imbalance"
            ),
            conductance_profile={
                "column": target_column,
                "row_pattern": (
                    "balanced_pairs"
                    if diagnostic_mode == "near_epsilon"
                    else "unbalanced_pairs"
                ),
                "spark_threshold": spark_threshold,
                "compiled_from": provenance,
            },
            coherence_profile={
                "column": target_column,
                "diagnostic_mode": diagnostic_mode,
                "compiled_from": provenance,
            },
        ),
    )


def _compile_instability(
    document: GRCL9LandscapeExampleDocument,
    critical: GRCL9CriticalRegion,
    unstable: GRCL9UnstableDirection,
) -> tuple[Any, ...]:
    provenance = _source_terms(document, critical, unstable)
    return (
        GRCL9SparkCandidateRegion(
            construct_id=f"{document.example_name}_spark_region",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            coherence_allocation={
                "candidate": 1.0,
                "neighbors": 0.5,
                "profile": _json_safe(critical.coherence_profile or {}),
                "compiled_from": provenance,
            },
            neighbor_coherence_profile={
                "port_occupancy": "all_nine_ports",
                "unstable_direction": unstable.direction_id,
                "compiled_from": provenance,
            },
            spark_gate_intent="saturation_instability",
        ),
        GRCL9InstabilityProfile(
            construct_id=f"{document.example_name}_instability_profile",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            row_anisotropy_profile={
                "axis_role": unstable.axis_role,
                "basis_terms": ("coherence", "mismatch", "flux_feedback"),
                "compiled_from": provenance,
            },
            support_cut_profile={
                "support_class": unstable.support_class,
                "cut_class": unstable.cut_class,
                "proxy": "cut_out_over_cut_plus_support",
                "compiled_from": provenance,
            },
            tau_instability=unstable.tau_instability,
        ),
    )


def _compile_expansion(
    document: GRCL9LandscapeExampleDocument,
    critical: GRCL9CriticalRegion,
    refinement: GRCL9RefinementLocus,
) -> tuple[Any, ...]:
    provenance = _source_terms(document, critical, refinement)
    profile = critical.columnwise_near_cancellation or {}
    target_column = int(profile.get("target_column", 2))
    _validate_column(target_column, field_name="target_column")
    diagnostic_mode = str(profile.get("diagnostic_mode", "near_epsilon"))
    spark_threshold = float(profile.get("spark_threshold", 0.02))
    return (
        GRCL9SparkCandidateRegion(
            construct_id=f"{document.example_name}_spark_region",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            coherence_allocation={
                "candidate": 1.0,
                "neighbors": 0.5,
                "profile": _json_safe(critical.coherence_profile or {}),
                "compiled_from": provenance,
            },
            neighbor_coherence_profile={
                "port_occupancy": "all_nine_ports",
                "refinement_locus": refinement.locus_id,
                "compiled_from": provenance,
            },
            spark_gate_intent="saturation_column_proxy",
        ),
        GRCL9ColumnProxyProfile(
            construct_id=f"{document.example_name}_column_profile",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            target_column=target_column,
            cancellation_mode=(
                "cancellation" if diagnostic_mode == "near_epsilon" else "imbalance"
            ),
            conductance_profile={
                "column": target_column,
                "row_pattern": (
                    "balanced_pairs"
                    if diagnostic_mode == "near_epsilon"
                    else "unbalanced_pairs"
                ),
                "spark_threshold": spark_threshold,
                "compiled_from": provenance,
            },
            coherence_profile={
                "column": target_column,
                "diagnostic_mode": diagnostic_mode,
                "compiled_from": provenance,
            },
        ),
        GRCL9ExpansionRefinementRegion(
            construct_id=f"{document.example_name}_expansion_region",
            motif_id=critical.motif_id,
            candidate_id=critical.region_id,
            target_effective_degree=refinement.target_effective_degree,
            module_size_formula="max(1, ceil((D_eff - 2) / 7))",
            bond_weight_mode="fixed",
            coherence_transfer_mode=refinement.coherence_transfer_mode,
            coherence_transfer_ratios=(1 / 3, 1 / 3, 1 / 3),
        ),
    )


def _compile_growth(
    document: GRCL9LandscapeExampleDocument,
    boundary: GRCL9BoundaryStratum,
    pressure: GRCL9GradientPressure,
) -> tuple[Any, ...]:
    provenance = _source_terms(document, boundary, pressure)
    return (
        GRCL9GrowthLocus(
            construct_id=f"{document.example_name}_growth_locus",
            motif_id=boundary.motif_id,
            parent_id=boundary.parent_region_id,
            inactive_parent_port=boundary.inactive_port,
            pressure_profile={
                "class": pressure.pressure_class,
                "boundary": boundary.boundary_role,
                "pressure_formula": "one_minus_exp_minus_lambda_flux",
                "compiled_from": provenance,
            },
            birth_rule="outward_flux_pressure",
            lambda_birth=pressure.lambda_birth,
            growth_semantics=pressure.growth_semantics,
            front_capacity_source=pressure.front_capacity_source,
            front_source_construct_id=pressure.front_source_construct_id,
        ),
    )


def _compile_fission(
    document: GRCL9LandscapeExampleDocument,
    two_sink: GRCL9PostRefinementTwoSinkRegion,
    bridge: GRCL9SaddleBridge,
) -> tuple[Any, ...]:
    return (
        GRCL9PostExpansionFissionGeometry(
            construct_id=f"{document.example_name}_fission_geometry",
            motif_id=two_sink.motif_id,
            module_region_id=two_sink.module_region_id,
            sink_region_a=two_sink.sink_region_a,
            sink_region_b=two_sink.sink_region_b,
            identity_fission_min_basin_mass=two_sink.identity_fission_min_basin_mass,
            identity_fission_persistence_delta=two_sink.identity_fission_persistence_delta,
            separable_conductance_geometry=bridge.bridge_class == "weak_saddle_bridge",
        ),
    )


def _example_document(
    example_name: str,
    manifest_entry_id: str,
    terms: tuple[GRCL9LandscapeTerm, ...],
    *,
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    matching_controls = [
        control
        for control in default_grcl9_lowering_manifest().by_entry_id()[
            manifest_entry_id
        ].controls
        if control.source_fixture_name == example_name
    ]
    if len(matching_controls) > 1:
        raise ValueError(f"example {example_name!r} is not linked to {manifest_entry_id!r}")
    if len(matching_controls) == 1:
        expected_selector_ids = matching_controls[0].selector_ids
    elif selector_ids:
        expected_selector_ids = selector_ids
    else:
        raise ValueError(f"example {example_name!r} is not linked to {manifest_entry_id!r}")
    entry = default_grcl9_lowering_manifest().by_entry_id()[manifest_entry_id]
    return GRCL9LandscapeExampleDocument(
        example_name=example_name,
        manifest_entry_id=manifest_entry_id,
        expected_selector_ids=expected_selector_ids,
        expected_telemetry=entry.expected_telemetry,
        terms=terms,
        notes=(
            "GRCL/Morse-facing example; compiles into grcl9.source.v1 before "
            "lowering and runtime replay."
        ),
    )


def _critical(
    example_name: str,
    motif_id: str,
    *,
    spark_gate_intent: str,
    diagnostic_mode: str | None = None,
) -> GRCL9CriticalRegion:
    return GRCL9CriticalRegion(
        term_id=f"{example_name}_critical_region",
        motif_id=motif_id,
        region_id="candidate",
        stability_intent="critical",
        coherence_profile={
            "critical_region": "saturated_identity_support",
            "local_basin": "single_candidate",
        },
        boundary_gradient_profile={
            "boundary_ports": "all_nine",
            "gradient_structure": "columnwise" if diagnostic_mode else "anisotropic",
        },
        columnwise_near_cancellation=(
            {}
            if diagnostic_mode is None
            else {
                "target_column": 2,
                "diagnostic_mode": diagnostic_mode,
                "spark_threshold": 0.02,
            }
        ),
        spark_gate_intent=spark_gate_intent,
    )


def _column_proxy_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    diagnostic_mode: str,
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            _critical(
                example_name,
                "spark_column_proxy",
                spark_gate_intent="saturation_column_proxy",
                diagnostic_mode=diagnostic_mode,
            ),
        ),
        selector_ids=selector_ids,
    )


def _membrane_rupture_example(
    example_name: str,
    manifest_entry_id: str,
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            GRCL9CriticalRegion(
                term_id=f"{example_name}_critical_region",
                motif_id="spark_column_proxy",
                region_id="candidate",
                stability_intent="critical",
                coherence_profile={
                    "critical_region": "saturated_identity_support",
                    "local_basin": "membrane_bounded_cell",
                    "collapse_probe_kind": "membrane_rupture_structural_probe",
                },
                boundary_gradient_profile={
                    "boundary_ports": "all_nine",
                    "gradient_structure": "columnwise_membrane",
                    "ridge_role": "rupture_prone_membrane",
                    "support_status": "weakening_boundary",
                },
                columnwise_near_cancellation={
                    "target_column": 2,
                    "diagnostic_mode": "near_epsilon",
                    "spark_threshold": 0.02,
                },
                spark_gate_intent="saturation_column_proxy",
            ),
        ),
        selector_ids=("membrane_rupture_structural_probe",),
    )


def _instability_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    tau_instability: float,
    support_class: str,
    cut_class: str,
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            _critical(
                example_name,
                "spark_instability",
                spark_gate_intent="saturation_instability",
            ),
            GRCL9UnstableDirection(
                term_id=f"{example_name}_unstable_direction",
                motif_id="spark_instability",
                direction_id="unstable_row_1",
                region_id="candidate",
                axis_role="row_1",
                support_class=support_class,
                cut_class=cut_class,
                tau_instability=tau_instability,
            ),
        ),
        selector_ids=selector_ids,
    )


def _saddle_choice_pressure_example(
    example_name: str,
    manifest_entry_id: str,
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            _critical(
                example_name,
                "spark_instability",
                spark_gate_intent="saturation_instability",
            ),
            GRCL9UnstableDirection(
                term_id=f"{example_name}_unstable_direction",
                motif_id="spark_instability",
                direction_id="choice_pressure_direction",
                region_id="candidate",
                axis_role="row_1",
                support_class="asymmetric_support",
                cut_class="high_cut",
                tau_instability=0.25,
            ),
            GRCL9SaddleBridge(
                term_id=f"{example_name}_saddle_bridge",
                motif_id="spark_instability",
                bridge_id="choice_pressure_saddle",
                region_a="candidate",
                region_b="outer_basin",
                bridge_class="weak_saddle_bridge",
            ),
        ),
        selector_ids=("saddle_pressure_structural_probe",),
    )


def _expansion_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    target_effective_degree: int,
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            _critical(
                example_name,
                "expansion_refinement",
                spark_gate_intent="saturation_column_proxy",
                diagnostic_mode="near_epsilon",
            ),
            GRCL9RefinementLocus(
                term_id=f"{example_name}_refinement_locus",
                motif_id="expansion_refinement",
                locus_id="refinement_locus",
                region_id="candidate",
                target_effective_degree=target_effective_degree,
                coherence_transfer_mode="equal",
            ),
        ),
        selector_ids=selector_ids,
    )


def _growth_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    pressure_class: str,
    lambda_birth: float,
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            GRCL9BoundaryStratum(
                term_id=f"{example_name}_boundary_stratum",
                motif_id="growth_pressure",
                stratum_id="growth_boundary",
                parent_region_id="parent",
                inactive_port=5,
                boundary_role="growth_boundary",
            ),
            GRCL9GradientPressure(
                term_id=f"{example_name}_gradient_pressure",
                motif_id="growth_pressure",
                pressure_id="outward_pressure",
                boundary_stratum_id="growth_boundary",
                pressure_class=pressure_class,
                lambda_birth=lambda_birth,
            ),
        ),
        selector_ids=selector_ids,
    )


def _corrected_front_growth_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    pressure_class: str,
    lambda_birth: float,
    boundary_role: str = "spark_refinement_front",
    include_pressure: bool = True,
    front_capacity_source: str = "spark_expansion_front",
    front_source_construct_id: str | None = "",
    selector_ids: tuple[str, ...] = ("growth_count",),
) -> GRCL9LandscapeExampleDocument:
    terms: list[GRCL9LandscapeTerm] = [
        GRCL9CriticalRegion(
            term_id=f"{example_name}_critical_region",
            motif_id="front_growth",
            region_id="candidate",
            stability_intent="critical",
            coherence_profile={"critical_region": "front_growth_parent"},
            boundary_gradient_profile={"boundary_ports": "all_nine"},
            columnwise_near_cancellation={
                "target_column": 2,
                "diagnostic_mode": "near_epsilon",
                "spark_threshold": 0.02,
            },
            spark_gate_intent="saturation_column_proxy",
        ),
        GRCL9RefinementLocus(
            term_id=f"{example_name}_refinement_locus",
            motif_id="front_growth",
            locus_id="front_refinement",
            region_id="candidate",
            target_effective_degree=16,
            coherence_transfer_mode="equal",
        ),
        GRCL9BoundaryStratum(
            term_id=f"{example_name}_boundary_stratum",
            motif_id="front_growth",
            stratum_id="front_boundary",
            parent_region_id="candidate",
            inactive_port=5,
            boundary_role=boundary_role,
        ),
    ]
    if include_pressure:
        resolved_front_source_construct_id = (
            f"{example_name}_expansion_region"
            if front_source_construct_id == ""
            else front_source_construct_id
        )
        terms.append(
            GRCL9GradientPressure(
                term_id=f"{example_name}_gradient_pressure",
                motif_id="front_growth",
                pressure_id="front_pressure",
                boundary_stratum_id="front_boundary",
                pressure_class=pressure_class,
                lambda_birth=lambda_birth,
                growth_semantics="front_capacity",
                front_capacity_source=front_capacity_source,
                front_source_construct_id=resolved_front_source_construct_id,
            )
        )
    return _example_document(
        example_name,
        manifest_entry_id,
        tuple(terms),
        selector_ids=selector_ids,
    )


def _support_loss_example(
    example_name: str,
    manifest_entry_id: str,
) -> GRCL9LandscapeExampleDocument:
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            GRCL9BoundaryStratum(
                term_id=f"{example_name}_boundary_stratum",
                motif_id="growth_pressure",
                stratum_id="support_loss_boundary",
                parent_region_id="parent",
                inactive_port=5,
                boundary_role="identity_support_boundary",
            ),
            GRCL9GradientPressure(
                term_id=f"{example_name}_gradient_pressure",
                motif_id="growth_pressure",
                pressure_id="weakening_support_pressure",
                boundary_stratum_id="support_loss_boundary",
                pressure_class="support_loss_low",
                lambda_birth=0.05,
            ),
        ),
        selector_ids=("support_loss_pressure_candidate",),
    )


def _fission_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    min_basin_mass: float,
    basin_a_mass: float = 0.75,
    basin_b_mass: float | None = None,
    basin_a_stability: str = "stable",
    basin_b_stability: str = "stable",
    basin_a_support_count: int = 1,
    basin_b_support_count: int = 1,
    basin_a_selection_policy: str = "member_node",
    basin_b_selection_policy: str = "member_node",
    bridge_class: str = "weak_saddle_bridge",
    selector_ids: tuple[str, ...] = (),
) -> GRCL9LandscapeExampleDocument:
    resolved_basin_b_mass = (
        (0.75 if min_basin_mass < 0.5 else 0.25)
        if basin_b_mass is None
        else basin_b_mass
    )
    return _example_document(
        example_name,
        manifest_entry_id,
        (
            GRCL9PostRefinementTwoSinkRegion(
                term_id=f"{example_name}_two_sink_region",
                motif_id="post_expansion_fission",
                region_id="post_refinement_region",
                module_region_id="module",
                sink_region_a="sink_a",
                sink_region_b="sink_b",
                identity_fission_min_basin_mass=min_basin_mass,
                identity_fission_persistence_delta=3,
            ),
            GRCL9StableBasin(
                term_id=f"{example_name}_stable_basin_a",
                motif_id="post_expansion_fission",
                basin_id="sink_a",
                stability_class=basin_a_stability,
                mass_hint=basin_a_mass,
                support_node_count=basin_a_support_count,
                selection_policy=basin_a_selection_policy,
            ),
            GRCL9StableBasin(
                term_id=f"{example_name}_stable_basin_b",
                motif_id="post_expansion_fission",
                basin_id="sink_b",
                stability_class=basin_b_stability,
                mass_hint=resolved_basin_b_mass,
                support_node_count=basin_b_support_count,
                selection_policy=basin_b_selection_policy,
            ),
            GRCL9SaddleBridge(
                term_id=f"{example_name}_saddle_bridge",
                motif_id="post_expansion_fission",
                bridge_id="weak_bridge",
                region_a="sink_a",
                region_b="sink_b",
                bridge_class=bridge_class,
            ),
        ),
        selector_ids=selector_ids,
    )


def _cascade_example(
    example_name: str,
    manifest_entry_id: str,
    *,
    include_refinement: bool = True,
    include_growth: bool = True,
    growth_lambda_birth: float = 0.05,
    bridge_class: str = "merge_saddle_bridge",
    basin_support_count: int = 4,
    basin_a_mass: float = 0.90,
    basin_b_mass: float = 0.04,
    basin_a_stability: str = "stable",
    basin_b_stability: str = "collapsing",
    selector_ids: tuple[str, ...] = (
        "spark_column_proxy_count",
        "expansion_module_size",
        "growth_count",
        "runtime_collapse_like_long_window",
    ),
) -> GRCL9LandscapeExampleDocument:
    terms: list[GRCL9LandscapeTerm] = []
    if include_refinement:
        terms.extend(
            (
                GRCL9CriticalRegion(
                    term_id=f"{example_name}_critical_region",
                    motif_id="cascade_refinement",
                    region_id="candidate",
                    stability_intent="critical",
                    coherence_profile={
                        "critical_region": "saturated_membrane_bounded_identity",
                        "local_basin": "cascade_source_cell",
                    },
                    boundary_gradient_profile={
                        "boundary_ports": "all_nine",
                        "gradient_structure": "columnwise_membrane",
                        "ridge_role": "rupture_prone_membrane",
                    },
                    columnwise_near_cancellation={
                        "target_column": 2,
                        "diagnostic_mode": "near_epsilon",
                        "spark_threshold": 0.02,
                    },
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9RefinementLocus(
                    term_id=f"{example_name}_refinement_locus",
                    motif_id="cascade_refinement",
                    locus_id="refinement_locus",
                    region_id="candidate",
                    target_effective_degree=44,
                    coherence_transfer_mode="equal",
                ),
            )
        )
    if include_growth:
        terms.extend(
            (
                GRCL9BoundaryStratum(
                    term_id=f"{example_name}_boundary_stratum",
                    motif_id="cascade_growth",
                    stratum_id="growth_boundary",
                    parent_region_id="parent",
                    inactive_port=5,
                    boundary_role="growth_boundary",
                ),
                GRCL9GradientPressure(
                    term_id=f"{example_name}_gradient_pressure",
                    motif_id="cascade_growth",
                    pressure_id="outward_pressure",
                    boundary_stratum_id="growth_boundary",
                    pressure_class="high",
                    lambda_birth=growth_lambda_birth,
                ),
            )
        )
    terms.extend(
        (
            GRCL9PostRefinementTwoSinkRegion(
                term_id=f"{example_name}_two_sink_region",
                motif_id="cascade_fission",
                region_id="post_refinement_region",
                module_region_id="module",
                sink_region_a="sink_a",
                sink_region_b="sink_b",
                identity_fission_min_basin_mass=0.10,
                identity_fission_persistence_delta=6,
            ),
            GRCL9StableBasin(
                term_id=f"{example_name}_stable_basin_a",
                motif_id="cascade_fission",
                basin_id="sink_a",
                stability_class=basin_a_stability,
                mass_hint=basin_a_mass,
                support_node_count=basin_support_count,
                selection_policy="group_centroid",
            ),
            GRCL9StableBasin(
                term_id=f"{example_name}_stable_basin_b",
                motif_id="cascade_fission",
                basin_id="sink_b",
                stability_class=basin_b_stability,
                mass_hint=basin_b_mass,
                support_node_count=basin_support_count,
                selection_policy="member_node",
            ),
            GRCL9SaddleBridge(
                term_id=f"{example_name}_saddle_bridge",
                motif_id="cascade_fission",
                bridge_id="cascade_merge_bridge",
                region_a="sink_a",
                region_b="sink_b",
                bridge_class=bridge_class,
            ),
        )
    )
    return _example_document(
        example_name,
        manifest_entry_id,
        tuple(terms),
        selector_ids=selector_ids,
    )


def _phase_diagram_examples(
    manifest_entry_id: str,
) -> tuple[GRCL9LandscapeExampleDocument, ...]:
    regimes = (
        ("balanced", 0.75, 0.75, "stable"),
        ("mild", 0.85, 0.35, "stable"),
        ("threshold", 0.90, 0.12, "weak"),
        ("deep", 0.90, 0.02, "collapsing"),
    )
    growth_settings = (
        ("no_growth", False, 0.05),
        ("low_growth", True, 0.02),
        ("nominal_growth", True, 0.05),
    )
    selector_ids = (
        "spark_column_proxy_count",
        "expansion_module_size",
        "growth_count",
        "runtime_collapse_like_classification",
    )
    return tuple(
        _cascade_example(
            f"cell_full_capacity_phase_{regime}_{growth_label}",
            manifest_entry_id,
            include_growth=include_growth,
            growth_lambda_birth=lambda_birth,
            basin_a_mass=basin_a_mass,
            basin_b_mass=basin_b_mass,
            basin_b_stability=basin_b_stability,
            selector_ids=selector_ids,
        )
        for regime, basin_a_mass, basin_b_mass, basin_b_stability in regimes
        for growth_label, include_growth, lambda_birth in growth_settings
    )

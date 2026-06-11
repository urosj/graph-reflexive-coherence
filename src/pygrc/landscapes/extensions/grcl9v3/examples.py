"""GRCL/Morse-facing examples that compile to GRCL-9V3 source documents."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, ClassVar

from pygrc.core import InvalidLandscapeSeedError

from ...io import load_landscape_seed
from ...seed import LandscapeSeed
from .manifest import (
    GRCL9V3_BASE_NON_CLAIMS,
    default_grcl9v3_lowering_manifest,
)
from .schema import (
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3BridgePolicy,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3ColumnProxyFallbackProfile,
    GRCL9V3ExpansionRefinementRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3HybridTensorProfile,
    GRCL9V3QuiescentHybridRegion,
    GRCL9V3RowBasisHessianProfile,
    GRCL9V3SourceConstruct,
    GRCL9V3SourceDocument,
    GRCL9V3TransportReroutingRegion,
)


GRCL9V3_LANDSCAPE_EXAMPLE_VERSION = "grcl9v3.landscape_example.v1"
GRCL9V3_LANDSCAPE_EXAMPLE_NAMES = (
    "hybrid_spark_gate_positive_control",
    "hybrid_spark_gate_negative_control",
    "spark_to_expansion_positive_control",
    "spark_to_expansion_negative_control",
    "appendix_e_cell_division_positive_control",
    "appendix_e_cell_division_negative_control",
    "choice_collapse_positive_control",
    "choice_collapse_negative_control",
    "growth_pressure_positive_control",
    "growth_pressure_negative_control",
    "pressure_boundary_positive_control",
    "transport_basin_rerouting_positive_control",
    "quiescent_hybrid_control_no_event_control",
)
GRCL9V3_LANDSCAPE_SEED_EXAMPLE_PATHS = (
    Path("configs/landscapes/seed/grcl9v3-hybrid-spark-gate-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-hybrid-spark-gate-negative.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-spark-to-expansion-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-spark-to-expansion-negative.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-appendix-e-cell-division-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-choice-collapse-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-choice-collapse-negative.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-front-growth-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-front-growth-no-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-transport-basin-rerouting-positive.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-quiescent-hybrid-control.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-hybrid-spark-expansion-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-hybrid-choice-transport.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-hybrid-appendix-e-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-cell-boundary-membrane-spark.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-cell-internal-valley-growth-transport.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-cell-nested-basin-hierarchy.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-cell-saddle-tensor-choice.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-cell-refinement-budget-expansion.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-cell-choice-collapse.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-appendix-e-cell-division-composing-cell.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-cascade.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-bounded-growth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-balanced-choice.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-zero-birth.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-closed-front.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-multi-center-collapse-learning.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-multi-center-delayed-collapse-learning.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-multi-center-relay-attempt.seed.yaml"),
    Path("configs/landscapes/seed/grcl9v3-corrected-propagated-front-relay.seed.yaml"),
)
GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES = (
    "hybrid_spark_gate_positive_control",
    "hybrid_spark_gate_negative_control",
    "spark_to_expansion_positive_control",
    "spark_to_expansion_negative_control",
    "appendix_e_cell_division_positive_control",
    "choice_collapse_positive_control",
    "choice_collapse_negative_control",
    "corrected_front_growth_positive_control",
    "corrected_front_growth_no_growth_control",
    "transport_basin_rerouting_positive_control",
    "quiescent_hybrid_control_no_event_control",
    "corrected_hybrid_spark_expansion_growth_composition",
    "hybrid_choice_transport_composition",
    "corrected_hybrid_appendix_e_growth_composition",
    "corrected_hybrid_full_composition",
    "cell_boundary_membrane_spark",
    "corrected_cell_internal_valley_growth_transport",
    "cell_nested_basin_hierarchy",
    "cell_saddle_tensor_choice",
    "cell_refinement_budget_expansion",
    "cell_choice_collapse",
    "appendix_e_cell_division_composing_cell",
    "appendix_e_cell_division_corrected_full_capacity_cascade",
    "appendix_e_cell_division_corrected_full_capacity_bounded_growth",
    "appendix_e_cell_division_corrected_full_capacity_balanced_choice",
    "appendix_e_cell_division_corrected_full_capacity_zero_birth",
    "appendix_e_cell_division_corrected_full_capacity_closed_front",
    "corrected_multi_center_collapse_learning",
    "corrected_multi_center_delayed_collapse_learning",
    "corrected_multi_center_relay_attempt",
    "corrected_propagated_front_relay",
)
GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS = (
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-growth-pressure-positive.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-growth-pressure-negative.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-spark-expansion-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-appendix-e-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-full-composition.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-cell-internal-valley-growth-transport.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-cascade.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-balanced-choice.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-low-growth-balanced-choice.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-ultra-low-growth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-zero-birth.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-closed-growth-port.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-zero-birth-balanced-choice.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-collapse-learning.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-delayed-collapse-learning.seed.yaml"),
    Path("configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-balanced-no-collapse.seed.yaml"),
)
GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES = (
    "growth_pressure_positive_control",
    "growth_pressure_negative_control",
    "hybrid_spark_expansion_growth_composition",
    "hybrid_appendix_e_growth_composition",
    "hybrid_full_composition",
    "cell_internal_valley_growth_transport",
    "appendix_e_cell_division_full_capacity_cascade",
    "appendix_e_cell_division_full_capacity_low_growth",
    "appendix_e_cell_division_full_capacity_balanced_choice",
    "appendix_e_cell_division_full_capacity_low_growth_balanced_choice",
    "appendix_e_cell_division_full_capacity_ultra_low_growth",
    "appendix_e_cell_division_full_capacity_zero_birth",
    "appendix_e_cell_division_full_capacity_closed_growth_port",
    "appendix_e_cell_division_full_capacity_zero_birth_balanced_choice",
    "multi_center_collapse_learning",
    "multi_center_delayed_collapse_learning",
    "multi_center_balanced_no_collapse",
)
_SEED_TOP_LEVEL_ALLOWED_KEYS = frozenset(
    {
        "contract_version",
        "grcl9v3_required",
        "example_name",
        "manifest_entry_id",
        "motif_id",
        "expected_selector_ids",
        "non_claims",
        "notes",
    }
)

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_REVIEWED_MOTIF_ID_RE = re.compile(r"^grc9v3-motif-[a-z0-9]+(?:-[a-z0-9]+)*$")
_FORBIDDEN_EXAMPLE_KEYS = frozenset(
    {
        "birth_event",
        "choice_happened",
        "collapse_happened",
        "current_flux",
        "daughter_sink_confirmed",
        "edge_id",
        "event_counts_by_kind",
        "event_history",
        "event_rows",
        "events",
        "expansion_happened",
        "flux_uv",
        "graph_checkpoint",
        "growth_count",
        "growth_happened",
        "hybrid_spark_completed",
        "node_id",
        "port_edge",
        "port_edges",
        "runtime_events",
        "solved_basin",
        "solved_diagnostic",
        "solved_flux",
        "solved_hessian",
        "solved_tensor",
        "spark_count",
        "spark_happened",
        "step_rows",
        "telemetry_summary",
        "topology",
    }
)
_MOTIF_IDS = {
    "hybrid_spark_gate_positive_control": "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
    "hybrid_spark_gate_negative_control": "grc9v3-motif-s0006-hybrid-spark-gate-negative-control",
    "spark_to_expansion_positive_control": "grc9v3-motif-s0006-spark-to-expansion-positive-control",
    "spark_to_expansion_negative_control": "grc9v3-motif-s0006-spark-to-expansion-negative-control",
    "appendix_e_cell_division_positive_control": "grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
    "appendix_e_cell_division_negative_control": "grc9v3-motif-s0006-appendix-e-cell-division-negative-control",
    "choice_collapse_positive_control": "grc9v3-motif-s0006-choice-collapse-positive-control",
    "choice_collapse_negative_control": "grc9v3-motif-s0006-choice-collapse-negative-control",
    "growth_pressure_positive_control": "grc9v3-motif-s0006-growth-pressure-positive-control",
    "growth_pressure_negative_control": "grc9v3-motif-s0006-growth-pressure-negative-control",
    "pressure_boundary_positive_control": "grc9v3-motif-s0073-pressure-boundary-growth-positive-control",
    "transport_basin_rerouting_positive_control": "grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
    "quiescent_hybrid_control_no_event_control": "grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
    "hybrid_spark_expansion_growth_composition": "grc9v3-motif-s0016-hybrid-spark-expansion-growth-composition",
    "hybrid_choice_transport_composition": "grc9v3-motif-s0016-hybrid-choice-transport-composition",
    "hybrid_appendix_e_growth_composition": "grc9v3-motif-s0016-hybrid-appendix-e-growth-composition",
    "hybrid_full_composition": "grc9v3-motif-s0016-hybrid-full-composition",
    "cell_boundary_membrane_spark": "grc9v3-motif-s0019-cell-boundary-membrane-spark",
    "cell_internal_valley_growth_transport": "grc9v3-motif-s0019-cell-internal-valley-growth-transport",
    "cell_nested_basin_hierarchy": "grc9v3-motif-s0019-cell-nested-basin-hierarchy",
    "cell_saddle_tensor_choice": "grc9v3-motif-s0019-cell-saddle-tensor-choice",
    "cell_refinement_budget_expansion": "grc9v3-motif-s0019-cell-refinement-budget-expansion",
    "cell_choice_collapse": "grc9v3-motif-s0019-cell-choice-collapse",
    "appendix_e_cell_division_composing_cell": "grc9v3-motif-s0019-appendix-e-cell-division-composing-cell",
    "appendix_e_cell_division_full_capacity_cascade": "grc9v3-motif-s0022-appendix-e-cell-division-full-capacity-cascade",
    "appendix_e_cell_division_full_capacity_low_growth": "grc9v3-motif-s0022-appendix-e-cell-division-full-capacity-low-growth",
    "appendix_e_cell_division_full_capacity_balanced_choice": "grc9v3-motif-s0022-appendix-e-cell-division-full-capacity-balanced-choice",
    "appendix_e_cell_division_full_capacity_low_growth_balanced_choice": "grc9v3-motif-s0022-appendix-e-cell-division-full-capacity-low-growth-balanced-choice",
    "appendix_e_cell_division_full_capacity_ultra_low_growth": "grc9v3-motif-s0025-appendix-e-cell-division-full-capacity-ultra-low-growth",
    "appendix_e_cell_division_full_capacity_zero_birth": "grc9v3-motif-s0025-appendix-e-cell-division-full-capacity-zero-birth",
    "appendix_e_cell_division_full_capacity_closed_growth_port": "grc9v3-motif-s0025-appendix-e-cell-division-full-capacity-closed-growth-port",
    "appendix_e_cell_division_full_capacity_zero_birth_balanced_choice": "grc9v3-motif-s0025-appendix-e-cell-division-full-capacity-zero-birth-balanced-choice",
    "multi_center_collapse_learning": "grc9v3-motif-s0028-multi-center-collapse-learning",
    "multi_center_delayed_collapse_learning": "grc9v3-motif-s0028-multi-center-delayed-collapse-learning",
    "multi_center_balanced_no_collapse": "grc9v3-motif-s0028-multi-center-balanced-no-collapse",
}


def _require_string(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


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


def _validate_reviewed_motif_id(value: str, *, field_name: str) -> None:
    _require_string(value, field_name=field_name)
    if not _REVIEWED_MOTIF_ID_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use reviewed GRC9V3 motif-id format")


def _validate_no_forbidden_example_fields(value: Any, *, field_name: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_EXAMPLE_KEYS:
                raise ValueError(
                    f"{field_name}.{key_text} is not allowed in GRCL-9V3 examples"
                )
            _validate_no_forbidden_example_fields(
                item,
                field_name=f"{field_name}.{key_text}",
            )
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for index, item in enumerate(value):
            _validate_no_forbidden_example_fields(
                item,
                field_name=f"{field_name}[{index}]",
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
    """Common source-facing GRCL-9V3 landscape term."""

    term_id: str
    region_id: str
    source_role: str
    profile: Mapping[str, Any] | None = None

    term_kind: ClassVar[str] = "landscape_term"

    def __post_init__(self) -> None:
        _validate_token(self.term_id, field_name="term_id")
        _validate_token(self.region_id, field_name="region_id")
        _validate_token(self.source_role, field_name="source_role")
        _require_mapping(self.profile or {}, field_name="profile")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "term_kind": self.term_kind,
            "term_id": self.term_id,
            "region_id": self.region_id,
            "source_role": self.source_role,
            "profile": _json_safe(self.profile or {}),
        }


@dataclass(frozen=True)
class GRCL9V3CriticalRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "critical_region"


@dataclass(frozen=True)
class GRCL9V3StableBasin(_LandscapeTermBase):
    term_kind: ClassVar[str] = "stable_basin"


@dataclass(frozen=True)
class GRCL9V3UnstableDirection(_LandscapeTermBase):
    term_kind: ClassVar[str] = "unstable_direction"


@dataclass(frozen=True)
class GRCL9V3Separatrix(_LandscapeTermBase):
    term_kind: ClassVar[str] = "separatrix"


@dataclass(frozen=True)
class GRCL9V3SaddleRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "saddle_region"


@dataclass(frozen=True)
class GRCL9V3RidgeMembrane(_LandscapeTermBase):
    term_kind: ClassVar[str] = "ridge_membrane"


@dataclass(frozen=True)
class GRCL9V3ValleyChannel(_LandscapeTermBase):
    term_kind: ClassVar[str] = "valley_channel"


@dataclass(frozen=True)
class GRCL9V3PlateauSupport(_LandscapeTermBase):
    term_kind: ClassVar[str] = "plateau_support"


@dataclass(frozen=True)
class GRCL9V3BoundaryStratum(_LandscapeTermBase):
    term_kind: ClassVar[str] = "boundary_stratum"


@dataclass(frozen=True)
class GRCL9V3RefinementLocus(_LandscapeTermBase):
    term_kind: ClassVar[str] = "refinement_locus"


@dataclass(frozen=True)
class GRCL9V3TensorHessianProfile(_LandscapeTermBase):
    term_kind: ClassVar[str] = "tensor_hessian_profile"


@dataclass(frozen=True)
class GRCL9V3ChoiceCollapseLandscapeRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "choice_collapse_region"


@dataclass(frozen=True)
class GRCL9V3GrowthLandscapeLocus(_LandscapeTermBase):
    term_kind: ClassVar[str] = "growth_locus"


@dataclass(frozen=True)
class GRCL9V3TransportReroutingLandscapeRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "transport_rerouting_region"


@dataclass(frozen=True)
class GRCL9V3QuiescentLandscapeRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "quiescent_region"


@dataclass(frozen=True)
class GRCL9V3AppendixECellDivisionRegion(_LandscapeTermBase):
    term_kind: ClassVar[str] = "appendix_e_cell_division_region"


GRCL9V3LandscapeTerm = (
    GRCL9V3CriticalRegion
    | GRCL9V3StableBasin
    | GRCL9V3UnstableDirection
    | GRCL9V3Separatrix
    | GRCL9V3SaddleRegion
    | GRCL9V3RidgeMembrane
    | GRCL9V3ValleyChannel
    | GRCL9V3PlateauSupport
    | GRCL9V3BoundaryStratum
    | GRCL9V3RefinementLocus
    | GRCL9V3TensorHessianProfile
    | GRCL9V3ChoiceCollapseLandscapeRegion
    | GRCL9V3GrowthLandscapeLocus
    | GRCL9V3TransportReroutingLandscapeRegion
    | GRCL9V3QuiescentLandscapeRegion
    | GRCL9V3AppendixECellDivisionRegion
)

_TERM_BY_KIND = {
    term.term_kind: term
    for term in (
        GRCL9V3CriticalRegion,
        GRCL9V3StableBasin,
        GRCL9V3UnstableDirection,
        GRCL9V3Separatrix,
        GRCL9V3SaddleRegion,
        GRCL9V3RidgeMembrane,
        GRCL9V3ValleyChannel,
        GRCL9V3PlateauSupport,
        GRCL9V3BoundaryStratum,
        GRCL9V3RefinementLocus,
        GRCL9V3TensorHessianProfile,
        GRCL9V3ChoiceCollapseLandscapeRegion,
        GRCL9V3GrowthLandscapeLocus,
        GRCL9V3TransportReroutingLandscapeRegion,
        GRCL9V3QuiescentLandscapeRegion,
        GRCL9V3AppendixECellDivisionRegion,
    )
}


def grcl9v3_landscape_term_from_mapping(value: Mapping[str, Any]) -> GRCL9V3LandscapeTerm:
    mapping = _require_mapping(value, field_name="landscape_term")
    term_kind = _require_string(mapping.get("term_kind"), field_name="term_kind")
    term_type = _TERM_BY_KIND.get(term_kind)
    if term_type is None:
        raise ValueError(f"unsupported GRCL-9V3 landscape term kind {term_kind!r}")
    return term_type(
        term_id=_require_string(mapping.get("term_id"), field_name="term_id"),
        region_id=_require_string(mapping.get("region_id"), field_name="region_id"),
        source_role=_require_string(mapping.get("source_role"), field_name="source_role"),
        profile=dict(_require_mapping(mapping.get("profile", {}), field_name="profile")),
    )


@dataclass(frozen=True)
class GRCL9V3LandscapeExampleDocument:
    """GRCL/Morse-facing source example compiled into GRCL-9V3 source."""

    example_name: str
    manifest_entry_id: str
    motif_id: str
    expected_selector_ids: tuple[str, ...]
    terms: tuple[GRCL9V3LandscapeTerm, ...]
    grcl9v3_required: bool = True
    example_schema_version: str = GRCL9V3_LANDSCAPE_EXAMPLE_VERSION
    non_claims: tuple[str, ...] = (
        "source_preconditions_only",
        "no_runtime_event_claim",
        "no_solved_telemetry",
    )
    notes: Mapping[str, Any] | None = None
    source_seed_reference: str | None = None

    def __post_init__(self) -> None:
        if self.example_schema_version != GRCL9V3_LANDSCAPE_EXAMPLE_VERSION:
            raise ValueError(
                f"example_schema_version must be {GRCL9V3_LANDSCAPE_EXAMPLE_VERSION!r}"
            )
        _validate_token(self.example_name, field_name="example_name")
        _validate_token(self.manifest_entry_id, field_name="manifest_entry_id")
        _validate_reviewed_motif_id(self.motif_id, field_name="motif_id")
        if not _require_bool(self.grcl9v3_required, field_name="grcl9v3_required"):
            raise ValueError("grcl9v3_required = true is required")
        if not self.expected_selector_ids:
            raise ValueError("expected_selector_ids must not be empty")
        for selector_id in self.expected_selector_ids:
            _validate_token(selector_id, field_name="expected_selector_ids[]")
        if not self.terms:
            raise ValueError("terms must not be empty")
        term_ids = [term.term_id for term in self.terms]
        if len(term_ids) != len(set(term_ids)):
            raise ValueError("term_id values must be unique")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")
        _require_mapping(self.notes or {}, field_name="notes")
        if self.source_seed_reference is not None:
            _require_string(self.source_seed_reference, field_name="source_seed_reference")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = {
            "example_schema_version": self.example_schema_version,
            "example_name": self.example_name,
            "manifest_entry_id": self.manifest_entry_id,
            "motif_id": self.motif_id,
            "expected_selector_ids": list(self.expected_selector_ids),
            "grcl9v3_required": self.grcl9v3_required,
            "terms": [term.to_mapping() for term in self.terms],
            "non_claims": list(self.non_claims),
            "notes": _json_safe(self.notes or {}),
        }
        if self.source_seed_reference is not None:
            payload["source_seed_reference"] = self.source_seed_reference
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3LandscapeExampleDocument:
        mapping = _require_mapping(value, field_name="landscape_example")
        return cls(
            example_schema_version=_require_string(
                mapping.get("example_schema_version", GRCL9V3_LANDSCAPE_EXAMPLE_VERSION),
                field_name="example_schema_version",
            ),
            example_name=_require_string(mapping.get("example_name"), field_name="example_name"),
            manifest_entry_id=_require_string(
                mapping.get("manifest_entry_id"),
                field_name="manifest_entry_id",
            ),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            expected_selector_ids=_string_tuple(
                mapping.get("expected_selector_ids", ()),
                field_name="expected_selector_ids",
            ),
            grcl9v3_required=_require_bool(
                mapping.get("grcl9v3_required", False),
                field_name="grcl9v3_required",
            ),
            terms=tuple(
                grcl9v3_landscape_term_from_mapping(item)
                for item in _require_sequence(mapping.get("terms", ()), field_name="terms")
            ),
            non_claims=_string_tuple(
                mapping.get(
                    "non_claims",
                    (
                        "source_preconditions_only",
                        "no_runtime_event_claim",
                        "no_solved_telemetry",
                    ),
                ),
                field_name="non_claims",
            ),
            notes=dict(_require_mapping(mapping.get("notes", {}), field_name="notes")),
            source_seed_reference=(
                None
                if mapping.get("source_seed_reference") is None
                else _require_string(
                    mapping.get("source_seed_reference"),
                    field_name="source_seed_reference",
                )
            ),
        )


def extract_grcl9v3_landscape_example_from_seed(
    seed: LandscapeSeed,
    *,
    seed_path: str | Path | None = None,
) -> GRCL9V3LandscapeExampleDocument | None:
    """Extract one GRCL-9V3 landscape example from a normalized seed."""

    raw_top_level = seed.extensions.get("grcl9v3")
    primitive_payloads = tuple(
        (primitive.id, primitive.extensions.get("grcl9v3"))
        for primitive in seed.primitives
        if isinstance(primitive.extensions, Mapping) and "grcl9v3" in primitive.extensions
    )
    if raw_top_level is None and not primitive_payloads:
        return None
    if raw_top_level is None:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9v3 is required when primitive-level grcl9v3 "
            "extensions are present"
        )
    if not isinstance(raw_top_level, Mapping):
        raise InvalidLandscapeSeedError("seed.extensions.grcl9v3 must be a mapping")
    top_level = dict(raw_top_level)
    unknown = set(top_level) - _SEED_TOP_LEVEL_ALLOWED_KEYS
    if unknown:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9v3 contains unsupported keys: "
            + ", ".join(sorted(str(key) for key in unknown))
        )
    if top_level.get("contract_version") != GRCL9V3_LANDSCAPE_EXAMPLE_VERSION:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9v3.contract_version must be "
            f"{GRCL9V3_LANDSCAPE_EXAMPLE_VERSION!r}"
        )
    if top_level.get("grcl9v3_required") is not True:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcl9v3.grcl9v3_required must be true"
        )

    terms: list[GRCL9V3LandscapeTerm] = []
    for primitive_id, raw_extension in primitive_payloads:
        if not isinstance(raw_extension, Mapping):
            raise InvalidLandscapeSeedError(
                f"primitive[{primitive_id}].extensions.grcl9v3 must be a mapping"
            )
        if "term_kind" not in raw_extension:
            raise InvalidLandscapeSeedError(
                f"primitive[{primitive_id}].extensions.grcl9v3.term_kind is required"
            )
        try:
            terms.append(grcl9v3_landscape_term_from_mapping(raw_extension))
        except ValueError as exc:
            raise InvalidLandscapeSeedError(
                f"invalid primitive[{primitive_id}].extensions.grcl9v3 term"
            ) from exc
    if not terms:
        raise InvalidLandscapeSeedError(
            "GRCL-9V3 landscape seed examples require at least one primitive term"
        )

    try:
        return GRCL9V3LandscapeExampleDocument(
            example_name=_require_string(
                top_level.get("example_name"),
                field_name="seed.extensions.grcl9v3.example_name",
            ),
            manifest_entry_id=_require_string(
                top_level.get("manifest_entry_id"),
                field_name="seed.extensions.grcl9v3.manifest_entry_id",
            ),
            motif_id=_require_string(
                top_level.get("motif_id"),
                field_name="seed.extensions.grcl9v3.motif_id",
            ),
            expected_selector_ids=_string_tuple(
                top_level.get("expected_selector_ids", ()),
                field_name="seed.extensions.grcl9v3.expected_selector_ids",
            ),
            terms=tuple(terms),
            non_claims=_string_tuple(
                top_level.get(
                    "non_claims",
                    (
                        "source_preconditions_only",
                        "no_runtime_event_claim",
                        "no_solved_telemetry",
                    ),
                ),
                field_name="seed.extensions.grcl9v3.non_claims",
            ),
            notes=dict(_require_mapping(top_level.get("notes", {}), field_name="notes")),
            source_seed_reference=(
                str(seed_path)
                if seed_path is not None
                else (seed.meta.source_reference or seed.meta.name)
            ),
        )
    except ValueError as exc:
        raise InvalidLandscapeSeedError("invalid GRCL-9V3 landscape seed example") from exc


def load_grcl9v3_landscape_seed_example(
    path: str | Path,
) -> GRCL9V3LandscapeExampleDocument:
    """Load a seed-backed GRCL-9V3 landscape example."""

    seed_path = Path(path)
    example = extract_grcl9v3_landscape_example_from_seed(
        load_landscape_seed(seed_path),
        seed_path=seed_path,
    )
    if example is None:
        raise InvalidLandscapeSeedError(
            f"landscape seed {seed_path} does not declare a GRCL-9V3 example"
        )
    return example


def default_grcl9v3_landscape_seed_examples(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9V3LandscapeExampleDocument, ...]:
    """Load the built-in seed-backed GRCL-9V3 landscape examples."""

    return _load_grcl9v3_landscape_seed_examples(
        root=root,
        paths=GRCL9V3_LANDSCAPE_SEED_EXAMPLE_PATHS,
        names=GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
        label="GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES",
    )


def legacy_grcl9v3_growth_landscape_seed_examples(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9V3LandscapeExampleDocument, ...]:
    """Load quarantined legacy standalone-growth GRCL-9V3 seed examples."""

    return _load_grcl9v3_landscape_seed_examples(
        root=root,
        paths=GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS,
        names=GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
        label="GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES",
    )


def _load_grcl9v3_landscape_seed_examples(
    *,
    root: str | Path,
    paths: Sequence[Path],
    names: Sequence[str],
    label: str,
) -> tuple[GRCL9V3LandscapeExampleDocument, ...]:
    base = Path(root)
    examples = tuple(load_grcl9v3_landscape_seed_example(base / path) for path in paths)
    if tuple(example.example_name for example in examples) != tuple(names):
        raise AssertionError(f"seed-example ordering drifted from {label}")
    return examples


def grcl9v3_landscape_seed_example_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, GRCL9V3LandscapeExampleDocument]:
    """Return built-in seed-backed examples keyed by example name."""

    return {
        example.example_name: example
        for example in default_grcl9v3_landscape_seed_examples(root=root)
    }


def legacy_grcl9v3_growth_landscape_seed_example_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, GRCL9V3LandscapeExampleDocument]:
    """Return quarantined legacy growth seed examples keyed by example name."""

    return {
        example.example_name: example
        for example in legacy_grcl9v3_growth_landscape_seed_examples(root=root)
    }


def grcl9v3_landscape_seed_example_path_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, Path]:
    """Return built-in seed-backed example paths keyed by example name."""

    examples = grcl9v3_landscape_seed_example_by_name(root=root)
    base = Path(root)
    return {
        name: base / path
        for name, path in zip(
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_PATHS,
            strict=True,
        )
        if name in examples
    }


def legacy_grcl9v3_growth_landscape_seed_example_path_by_name(
    *,
    root: str | Path = ".",
) -> Mapping[str, Path]:
    """Return quarantined legacy growth seed paths keyed by example name."""

    examples = legacy_grcl9v3_growth_landscape_seed_example_by_name(root=root)
    base = Path(root)
    return {
        name: base / path
        for name, path in zip(
            GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
            GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS,
            strict=True,
        )
        if name in examples
    }


def default_grcl9v3_landscape_examples() -> tuple[GRCL9V3LandscapeExampleDocument, ...]:
    """Return authored GRCL/Morse-facing examples, independent of fixtures."""

    examples = (
        _hybrid_spark_example(
            "hybrid_spark_gate_positive_control",
            manifest_entry_id="grcl9v3_lowering_hybrid_spark_gate_v1",
            source_role="positive_control",
            expected_selector_ids=("hybrid_spark_events", "hybrid_tensor_available"),
            active_degree=9,
            tensor_mode="anisotropic",
            include_column_proxy=True,
        ),
        _hybrid_spark_example(
            "hybrid_spark_gate_negative_control",
            manifest_entry_id="future_vocabulary_hybrid_spark_gate_v1",
            source_role="negative_control",
            expected_selector_ids=("no_lifecycle_events",),
            active_degree=7,
            tensor_mode="stable",
            include_column_proxy=False,
        ),
        _expansion_example(
            "spark_to_expansion_positive_control",
            manifest_entry_id="grcl9v3_lowering_spark_to_expansion_v1",
            source_role="positive_control",
            expected_selector_ids=("hybrid_expansion_events",),
            active_degree=9,
            target_effective_degree=30,
        ),
        _expansion_example(
            "spark_to_expansion_negative_control",
            manifest_entry_id="future_vocabulary_spark_to_expansion_v1",
            source_role="negative_control",
            expected_selector_ids=("no_lifecycle_events",),
            active_degree=8,
            target_effective_degree=30,
        ),
        _appendix_e_example(
            "appendix_e_cell_division_positive_control",
            manifest_entry_id="grcl9v3_lowering_appendix_e_cell_division_v1",
            source_role="positive_control",
            expected_selector_ids=("appendix_e_summary",),
            module_support="balanced_daughter_support",
        ),
        _appendix_e_example(
            "appendix_e_cell_division_negative_control",
            manifest_entry_id="future_vocabulary_appendix_e_cell_division_v1",
            source_role="negative_control",
            expected_selector_ids=("appendix_e_no_completion",),
            module_support="daughter_support_below_minimum",
        ),
        _choice_example(
            "choice_collapse_positive_control",
            manifest_entry_id="grcl9v3_lowering_choice_collapse_v1",
            source_role="positive_control",
            expected_selector_ids=("choice_collapse_events",),
            compatibility="high_contrast",
        ),
        _choice_example(
            "choice_collapse_negative_control",
            manifest_entry_id="future_vocabulary_choice_collapse_v1",
            source_role="negative_control",
            expected_selector_ids=("no_choice_collapse_events",),
            compatibility="low_contrast",
        ),
        _growth_example(
            "growth_pressure_positive_control",
            manifest_entry_id="grcl9v3_lowering_growth_pressure_v1",
            source_role="positive_control",
            expected_selector_ids=("growth_events",),
            lambda_birth=1.4,
            pressure="high_outward_pressure",
        ),
        _growth_example(
            "growth_pressure_negative_control",
            manifest_entry_id="future_vocabulary_growth_pressure_v1",
            source_role="negative_control",
            expected_selector_ids=("no_growth_events",),
            lambda_birth=0.02,
            pressure="low_outward_pressure",
        ),
        _growth_example(
            "pressure_boundary_positive_control",
            manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
            source_role="positive_control",
            expected_selector_ids=("pressure_boundary_growth_provenance",),
            lambda_birth=1.0,
            pressure="boundary_front",
            inactive_parent_port=6,
            growth_semantics="front_capacity",
            front_capacity_source="pressure_boundary",
            notes_extra={
                "composed_source_ancestry": (
                    "pressure_boundary",
                    "growth_pressure",
                )
            },
        ),
        _transport_example(
            "transport_basin_rerouting_positive_control",
            manifest_entry_id="future_vocabulary_transport_basin_rerouting_v1",
            source_role="positive_control",
            expected_selector_ids=("transport_rerouting_signature",),
        ),
        _quiescent_example(
            "quiescent_hybrid_control_no_event_control",
            manifest_entry_id="future_vocabulary_quiescent_hybrid_control_v1",
            source_role="no_event_control",
            expected_selector_ids=("no_lifecycle_events",),
        ),
    )
    if tuple(example.example_name for example in examples) != GRCL9V3_LANDSCAPE_EXAMPLE_NAMES:
        raise AssertionError("example ordering drifted from GRCL9V3_LANDSCAPE_EXAMPLE_NAMES")
    return examples


def grcl9v3_landscape_example_by_name() -> Mapping[str, GRCL9V3LandscapeExampleDocument]:
    """Return default GRCL-9V3 landscape examples keyed by name."""

    return {example.example_name: example for example in default_grcl9v3_landscape_examples()}


def compile_grcl9v3_landscape_example_to_source(
    example: GRCL9V3LandscapeExampleDocument,
) -> GRCL9V3SourceDocument:
    """Compile one GRCL/Morse-facing example to the mechanical source schema."""

    manifest = default_grcl9v3_lowering_manifest()
    expected_telemetry = _expected_telemetry_for_example(example, manifest)
    constructs, source_term_ids_by_construct_id = _compile_terms(example)
    term_ids = tuple(term.term_id for term in example.terms)
    provenance = {
        "compiler_version": "grcl9v3_landscape_compiler_v1",
        "source_example_schema_version": example.example_schema_version,
        "source_example_name": example.example_name,
        "source_term_ids": list(term_ids),
        "source_term_kinds": sorted({term.term_kind for term in example.terms}),
        "source_term_ids_by_construct_id": source_term_ids_by_construct_id,
        "source_seed_reference": example.source_seed_reference,
        "claim_boundary": (
            "GRCL-9V3 landscape examples declare source preconditions; "
            "runtime events and summaries remain telemetry observations."
        ),
    }
    if isinstance(example.notes, Mapping) and "composed_source_ancestry" in example.notes:
        provenance["composed_source_ancestry"] = list(
            _string_tuple(
                example.notes.get("composed_source_ancestry", ()),
                field_name="composed_source_ancestry",
            )
        )
    return GRCL9V3SourceDocument(
        fixture_name=example.example_name,
        manifest_entry_id=example.manifest_entry_id,
        expected_selector_ids=example.expected_selector_ids,
        bridge_policy=GRCL9V3BridgePolicy(conductance_hint=0.001),
        constructs=constructs,
        expected_telemetry=expected_telemetry,
        non_claims=tuple(dict.fromkeys((*GRCL9V3_BASE_NON_CLAIMS, *example.non_claims))),
        notes={
            "boundary": "compiled GRCL/Morse example declares preconditions only",
            "compiled_from": "grcl9v3_landscape_example",
            "source_example_name": example.example_name,
            **dict(example.notes or {}),
        },
        compiled_source_provenance=provenance,
    )


def compile_default_grcl9v3_landscape_examples_to_sources() -> tuple[GRCL9V3SourceDocument, ...]:
    """Compile all default landscape examples to GRCL-9V3 source documents."""

    return tuple(
        compile_grcl9v3_landscape_example_to_source(example)
        for example in default_grcl9v3_landscape_examples()
    )


def compile_default_grcl9v3_landscape_seed_examples_to_sources(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9V3SourceDocument, ...]:
    """Compile all built-in seed-backed GRCL-9V3 landscape examples."""

    return tuple(
        compile_grcl9v3_landscape_example_to_source(example)
        for example in default_grcl9v3_landscape_seed_examples(root=root)
    )


def compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources(
    *,
    root: str | Path = ".",
) -> tuple[GRCL9V3SourceDocument, ...]:
    """Compile quarantined legacy growth seeds for diagnostic replay."""

    return tuple(
        compile_grcl9v3_landscape_example_to_source(example)
        for example in legacy_grcl9v3_growth_landscape_seed_examples(root=root)
    )


def _example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    terms: tuple[GRCL9V3LandscapeTerm, ...],
    notes_extra: Mapping[str, Any] | None = None,
) -> GRCL9V3LandscapeExampleDocument:
    notes = {
        "boundary": "authored GRCL/Morse example, not a solved runtime trace",
        "compiled_target": "grcl9v3.source.v1",
        "source_role": source_role,
    }
    notes.update(dict(notes_extra or {}))
    return GRCL9V3LandscapeExampleDocument(
        example_name=example_name,
        manifest_entry_id=manifest_entry_id,
        motif_id=_MOTIF_IDS[example_name],
        expected_selector_ids=expected_selector_ids,
        terms=terms,
        notes=notes,
    )


def _hybrid_spark_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    active_degree: int,
    tensor_mode: str,
    include_column_proxy: bool,
) -> GRCL9V3LandscapeExampleDocument:
    terms: list[GRCL9V3LandscapeTerm] = [
        GRCL9V3CriticalRegion(
            term_id=f"{example_name}_critical",
            region_id="candidate",
            source_role=source_role,
            profile={
                "criticality": "hybrid_spark_gate",
                "saturation": {
                    "active_degree": active_degree,
                    "port_chart": "nine_port_candidate",
                },
                "spark_gate_intent": "hybrid_hessian_tensor",
                "spark_threshold": 0.05,
            },
        ),
        GRCL9V3RidgeMembrane(
            term_id=f"{example_name}_ridge",
            region_id="candidate_boundary",
            source_role=source_role,
            profile={"boundary": "nine_port_membrane"},
        ),
        GRCL9V3TensorHessianProfile(
            term_id=f"{example_name}_hessian",
            region_id="candidate",
            source_role=source_role,
            profile={
                "hessian_backend": "row_basis_diagonal",
                "row_basis_profile": {
                    "hessian_mode": tensor_mode,
                    "basis": "row_basis_diagonal",
                },
                "signed_history_required": False,
            },
        ),
        GRCL9V3UnstableDirection(
            term_id=f"{example_name}_unstable_direction",
            region_id="candidate",
            source_role=source_role,
            profile={"basis": "row_basis"},
        ),
        GRCL9V3TensorHessianProfile(
            term_id=f"{example_name}_tensor",
            region_id="candidate",
            source_role=source_role,
            profile={
                "anisotropy_axis": "row_2" if tensor_mode == "anisotropic" else "row_1",
                "tensor_profile": {
                    "tensor_mode": tensor_mode,
                    "row_mismatch": "high" if tensor_mode == "anisotropic" else "low",
                },
            },
        ),
    ]
    if include_column_proxy:
        terms.append(
            GRCL9V3ValleyChannel(
                term_id=f"{example_name}_column_channel",
                region_id="candidate",
                source_role=source_role,
                profile={
                    "target_column": 2,
                    "cancellation_mode": "near_cancellation",
                    "column_profile": {"column_2": "near_cancellation"},
                },
            )
        )
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=tuple(terms),
    )


def _expansion_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    active_degree: int,
    target_effective_degree: int,
) -> GRCL9V3LandscapeExampleDocument:
    base = _hybrid_spark_example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        active_degree=active_degree,
        tensor_mode="anisotropic",
        include_column_proxy=False,
    )
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            base.terms[0],
            GRCL9V3RefinementLocus(
                term_id=f"{example_name}_refinement",
                region_id="candidate",
                source_role=source_role,
                profile={
                    "target_effective_degree": target_effective_degree,
                    "expansion_distribution_mode": "equal",
                    "coherence_transfer_ratios": (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
                },
            ),
        ),
    )


def _appendix_e_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    module_support: str,
) -> GRCL9V3LandscapeExampleDocument:
    expansion = _expansion_example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        active_degree=9,
        target_effective_degree=30,
    )
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            *expansion.terms,
            GRCL9V3AppendixECellDivisionRegion(
                term_id=f"{example_name}_appendix_e",
                region_id="parent",
                source_role=source_role,
                profile={
                    "daughter_region_a": "daughter_a",
                    "daughter_region_b": "daughter_b",
                    "module_basin_support": {"support_mode": module_support},
                },
            ),
            GRCL9V3Separatrix(
                term_id=f"{example_name}_daughter_separatrix",
                region_id="daughter_separator",
                source_role=source_role,
                profile={"separates": ("daughter_a", "daughter_b")},
            ),
        ),
    )


def _choice_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    compatibility: str,
) -> GRCL9V3LandscapeExampleDocument:
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            GRCL9V3ChoiceCollapseLandscapeRegion(
                term_id=f"{example_name}_choice",
                region_id="choice_region",
                source_role=source_role,
                profile={
                    "basin_region_a": "basin_a",
                    "basin_region_b": "basin_b",
                    "collapse_target_region": "basin_a",
                    "compatibility_profile": {"compatibility": compatibility},
                },
            ),
            GRCL9V3StableBasin(
                term_id=f"{example_name}_basin_a",
                region_id="basin_a",
                source_role=source_role,
                profile={"basin": "choice_branch_a"},
            ),
            GRCL9V3StableBasin(
                term_id=f"{example_name}_basin_b",
                region_id="basin_b",
                source_role=source_role,
                profile={"basin": "choice_branch_b"},
            ),
        ),
    )


def _growth_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
    lambda_birth: float,
    pressure: str,
    inactive_parent_port: int = 5,
    growth_semantics: str = "legacy_growth_locus",
    front_capacity_source: str = "legacy_source_growth_locus",
    front_source_construct_id: str | None = None,
    notes_extra: Mapping[str, Any] | None = None,
) -> GRCL9V3LandscapeExampleDocument:
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            GRCL9V3BoundaryStratum(
                term_id=f"{example_name}_boundary",
                region_id="parent",
                source_role=source_role,
                profile={"inactive_parent_port": inactive_parent_port},
            ),
            GRCL9V3GrowthLandscapeLocus(
                term_id=f"{example_name}_growth",
                region_id="parent",
                source_role=source_role,
                profile={
                    "outward_pressure_profile": {"pressure": pressure},
                    "lambda_birth": lambda_birth,
                    "growth_semantics": growth_semantics,
                    "front_capacity_source": front_capacity_source,
                    "front_source_construct_id": front_source_construct_id,
                },
            ),
        ),
        notes_extra=notes_extra,
    )


def _transport_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
) -> GRCL9V3LandscapeExampleDocument:
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            GRCL9V3TransportReroutingLandscapeRegion(
                term_id=f"{example_name}_transport",
                region_id="route",
                source_role=source_role,
                profile={
                    "source_region_id": "source",
                    "sink_region_id": "sink",
                    "route_preference_profile": {"corridor": "preferred"},
                },
            ),
            GRCL9V3ValleyChannel(
                term_id=f"{example_name}_valley",
                region_id="route",
                source_role=source_role,
                profile={"channel": "transport_corridor"},
            ),
        ),
    )


def _quiescent_example(
    example_name: str,
    *,
    manifest_entry_id: str,
    source_role: str,
    expected_selector_ids: tuple[str, ...],
) -> GRCL9V3LandscapeExampleDocument:
    return _example(
        example_name,
        manifest_entry_id=manifest_entry_id,
        source_role=source_role,
        expected_selector_ids=expected_selector_ids,
        terms=(
            GRCL9V3QuiescentLandscapeRegion(
                term_id=f"{example_name}_quiet",
                region_id="quiet",
                source_role=source_role,
                profile={"active_degree": 5, "pressure": "low"},
            ),
            GRCL9V3PlateauSupport(
                term_id=f"{example_name}_plateau",
                region_id="quiet",
                source_role=source_role,
                profile={"support": "stable_plateau"},
            ),
        ),
    )


def _expected_telemetry_for_example(
    example: GRCL9V3LandscapeExampleDocument,
    manifest: Any,
) -> tuple[Any, ...]:
    if example.manifest_entry_id == "composed_grcl9v3_hybrid_composition_v1":
        return ()
    entry = manifest.by_entry_id().get(example.manifest_entry_id)
    if entry is not None:
        if example.motif_id not in entry.reviewed_motif_ids:
            raise ValueError("example motif_id is not linked to manifest entry")
        controls = [
            control
            for control in entry.controls
            if control.source_fixture_name == example.example_name
        ]
        if len(controls) != 1:
            raise ValueError("example is not linked to exactly one manifest control")
        if set(controls[0].selector_ids) != set(example.expected_selector_ids):
            raise ValueError("example selector ids do not match manifest control")
        return entry.expected_telemetry

    future_entry_id = _future_entry_id_for_motif(example.motif_id, manifest)
    if example.manifest_entry_id != future_entry_id:
        raise ValueError("future-vocabulary example manifest_entry_id does not match motif")
    return ()


def _future_entry_id_for_motif(motif_id: str, manifest: Any) -> str:
    future_by_motif = {record.motif_id: record for record in manifest.future_vocabulary_records}
    record = future_by_motif.get(motif_id)
    if record is None:
        raise ValueError("example motif_id is not linked to a manifest future-vocabulary record")
    return f"future_vocabulary_{record.phenomenon}_v1"


def _compile_terms(
    example: GRCL9V3LandscapeExampleDocument,
) -> tuple[tuple[GRCL9V3SourceConstruct, ...], dict[str, list[str]]]:
    constructs: list[GRCL9V3SourceConstruct] = []
    provenance: dict[str, list[str]] = {}

    critical = _first(example.terms, GRCL9V3CriticalRegion)
    if critical is not None:
        construct = GRCL9V3HybridSparkRegion(
            construct_id=f"{example.example_name}_spark_region",
            motif_id=example.motif_id,
            source_role=critical.source_role,
            ownership="grc9v3_hybrid",
            expected_selector_ids=tuple(
                selector_id
                for selector_id in example.expected_selector_ids
                if selector_id == "hybrid_spark_events"
            ),
            candidate_region_id=critical.region_id,
            saturation_profile=dict(critical.profile or {}).get(
                "saturation",
                {"active_degree": 9, "port_chart": "nine_port_candidate"},
            ),
            spark_gate_intent=str(
                dict(critical.profile or {}).get(
                    "spark_gate_intent",
                    "hybrid_hessian_tensor",
                )
            ),
            spark_threshold=float(dict(critical.profile or {}).get("spark_threshold", 0.05)),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [critical.term_id]

    hessian_terms = [
        term
        for term in example.terms
        if isinstance(term, GRCL9V3TensorHessianProfile)
        and "row_basis_profile" in dict(term.profile or {})
    ]
    if hessian_terms:
        term = hessian_terms[0]
        profile = dict(term.profile or {})
        construct = GRCL9V3RowBasisHessianProfile(
            construct_id=f"{example.example_name}_hessian_profile",
            motif_id=example.motif_id,
            source_role=term.source_role,
            ownership="grcv3_semantic",
            candidate_region_id=term.region_id,
            hessian_backend=str(profile.get("hessian_backend", "row_basis_diagonal")),
            row_basis_profile=dict(profile.get("row_basis_profile", {})),
            signed_history_required=bool(profile.get("signed_history_required", False)),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [term.term_id]

    tensor_terms = [
        term
        for term in example.terms
        if isinstance(term, GRCL9V3TensorHessianProfile)
        and "tensor_profile" in dict(term.profile or {})
    ]
    if tensor_terms:
        term = tensor_terms[0]
        profile = dict(term.profile or {})
        construct = GRCL9V3HybridTensorProfile(
            construct_id=f"{example.example_name}_tensor_profile",
            motif_id=example.motif_id,
            source_role=term.source_role,
            ownership="grc9v3_hybrid",
            region_id=term.region_id,
            anisotropy_axis=str(profile.get("anisotropy_axis", "row_1")),
            tensor_profile=dict(profile.get("tensor_profile", {})),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [term.term_id]

    column_term = _first_matching(
        example.terms,
        GRCL9V3ValleyChannel,
        lambda term: "target_column" in dict(term.profile or {}),
    )
    if column_term is not None:
        profile = dict(column_term.profile or {})
        construct = GRCL9V3ColumnProxyFallbackProfile(
            construct_id=f"{example.example_name}_column_proxy",
            motif_id=example.motif_id,
            source_role=column_term.source_role,
            ownership="grc9_mechanical",
            candidate_region_id=column_term.region_id,
            target_column=int(profile.get("target_column", 2)),
            cancellation_mode=str(profile.get("cancellation_mode", "near_cancellation")),
            column_profile=dict(profile.get("column_profile", {"column_2": "near_cancellation"})),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [column_term.term_id]

    refinement = _first(example.terms, GRCL9V3RefinementLocus)
    if refinement is not None:
        profile = dict(refinement.profile or {})
        construct = GRCL9V3ExpansionRefinementRegion(
            construct_id=f"{example.example_name}_expansion_region",
            motif_id=example.motif_id,
            source_role=refinement.source_role,
            ownership="grc9_mechanical",
            candidate_region_id=refinement.region_id,
            target_effective_degree=int(profile.get("target_effective_degree", 30)),
            expansion_distribution_mode=str(profile.get("expansion_distribution_mode", "equal")),
            coherence_transfer_ratios=tuple(
                float(item)
                for item in profile.get(
                    "coherence_transfer_ratios",
                    (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
                )
            ),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [refinement.term_id]

    appendix_e = _first(example.terms, GRCL9V3AppendixECellDivisionRegion)
    if appendix_e is not None:
        profile = dict(appendix_e.profile or {})
        construct = GRCL9V3AppendixEDivisionRegion(
            construct_id=f"{example.example_name}_division_region",
            motif_id=example.motif_id,
            source_role=appendix_e.source_role,
            ownership="grc9v3_hybrid",
            parent_region_id=appendix_e.region_id,
            daughter_region_a=str(profile.get("daughter_region_a", "daughter_a")),
            daughter_region_b=str(profile.get("daughter_region_b", "daughter_b")),
            module_basin_support=dict(
                profile.get("module_basin_support", {"support_mode": "balanced_daughter_support"})
            ),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [
            appendix_e.term_id,
            *[
                term.term_id
                for term in example.terms
                if isinstance(term, GRCL9V3Separatrix)
            ],
        ]

    for choice in _all(example.terms, GRCL9V3ChoiceCollapseLandscapeRegion):
        profile = dict(choice.profile or {})
        construct = GRCL9V3ChoiceCollapseRegion(
            construct_id=f"{example.example_name}_{choice.region_id}_choice_region",
            motif_id=example.motif_id,
            source_role=choice.source_role,
            ownership="grcv3_semantic",
            choice_region_id=choice.region_id,
            basin_region_a=str(profile.get("basin_region_a", "basin_a")),
            basin_region_b=str(profile.get("basin_region_b", "basin_b")),
            collapse_target_region=str(profile.get("collapse_target_region", "basin_a")),
            compatibility_profile=dict(
                profile.get("compatibility_profile", {"compatibility": "high_contrast"})
            ),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [
            choice.term_id,
            *[
                term.term_id
                for term in example.terms
                if isinstance(term, GRCL9V3StableBasin)
            ],
        ]

    boundaries = [
        term for term in example.terms if isinstance(term, GRCL9V3BoundaryStratum)
    ]
    for growth in _all(example.terms, GRCL9V3GrowthLandscapeLocus):
        profile = dict(growth.profile or {})
        boundary = next(
            (
                term
                for term in boundaries
                if term.region_id == growth.region_id
                or dict(term.profile or {}).get("growth_region_id") == growth.region_id
            ),
            boundaries[0] if boundaries else None,
        )
        boundary_profile = dict(boundary.profile or {}) if boundary is not None else {}
        construct = GRCL9V3GrowthLocus(
            construct_id=f"{example.example_name}_{growth.region_id}_growth_locus",
            motif_id=example.motif_id,
            source_role=growth.source_role,
            ownership="grc9_mechanical",
            parent_region_id=growth.region_id,
            inactive_parent_port=int(boundary_profile.get("inactive_parent_port", 5)),
            outward_pressure_profile=dict(
                profile.get("outward_pressure_profile", {"pressure": "high_outward_pressure"})
            ),
            lambda_birth=float(profile.get("lambda_birth", 1.4)),
            growth_semantics=str(profile.get("growth_semantics", "legacy_growth_locus")),
            front_capacity_source=str(
                profile.get("front_capacity_source", "legacy_source_growth_locus")
            ),
            front_source_construct_id=(
                None
                if profile.get("front_source_construct_id") is None
                else str(profile.get("front_source_construct_id"))
            ),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [
            growth.term_id,
            *([] if boundary is None else [boundary.term_id]),
        ]

    transport = _first(example.terms, GRCL9V3TransportReroutingLandscapeRegion)
    if transport is not None:
        profile = dict(transport.profile or {})
        construct = GRCL9V3TransportReroutingRegion(
            construct_id=f"{example.example_name}_transport_region",
            motif_id=example.motif_id,
            source_role=transport.source_role,
            ownership="shared_runtime",
            route_region_id=transport.region_id,
            source_region_id=str(profile.get("source_region_id", "source")),
            sink_region_id=str(profile.get("sink_region_id", "sink")),
            route_preference_profile=dict(
                profile.get("route_preference_profile", {"corridor": "preferred"})
            ),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [
            transport.term_id,
            *[
                term.term_id
                for term in example.terms
                if isinstance(term, GRCL9V3ValleyChannel)
                and "channel" in dict(term.profile or {})
            ],
        ]

    quiescent = _first(example.terms, GRCL9V3QuiescentLandscapeRegion)
    if quiescent is not None:
        construct = GRCL9V3QuiescentHybridRegion(
            construct_id=f"{example.example_name}_quiescent_region",
            motif_id=example.motif_id,
            source_role=quiescent.source_role,
            ownership="grc9v3_hybrid",
            region_id=quiescent.region_id,
            stability_margin_profile=dict(quiescent.profile or {}),
        )
        constructs.append(construct)
        provenance[construct.construct_id] = [
            quiescent.term_id,
            *[
                term.term_id
                for term in example.terms
                if isinstance(term, GRCL9V3PlateauSupport)
            ],
        ]

    if not constructs:
        raise ValueError(f"example {example.example_name!r} produced no mechanical constructs")
    return tuple(constructs), provenance


def _first(
    terms: tuple[GRCL9V3LandscapeTerm, ...],
    term_type: type[Any],
) -> Any | None:
    return next((term for term in terms if isinstance(term, term_type)), None)


def _all(
    terms: tuple[GRCL9V3LandscapeTerm, ...],
    term_type: type[Any],
) -> tuple[Any, ...]:
    return tuple(term for term in terms if isinstance(term, term_type))


def _first_matching(
    terms: tuple[GRCL9V3LandscapeTerm, ...],
    term_type: type[Any],
    predicate: Any,
) -> Any | None:
    return next(
        (
            term
            for term in terms
            if isinstance(term, term_type) and predicate(term)
        ),
        None,
    )


__all__ = [
    "GRCL9V3_LANDSCAPE_EXAMPLE_NAMES",
    "GRCL9V3_LANDSCAPE_EXAMPLE_VERSION",
    "GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES",
    "GRCL9V3_LANDSCAPE_SEED_EXAMPLE_PATHS",
    "GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES",
    "GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_PATHS",
    "GRCL9V3AppendixECellDivisionRegion",
    "GRCL9V3BoundaryStratum",
    "GRCL9V3ChoiceCollapseLandscapeRegion",
    "GRCL9V3CriticalRegion",
    "GRCL9V3GrowthLandscapeLocus",
    "GRCL9V3LandscapeExampleDocument",
    "GRCL9V3LandscapeTerm",
    "GRCL9V3PlateauSupport",
    "GRCL9V3QuiescentLandscapeRegion",
    "GRCL9V3RefinementLocus",
    "GRCL9V3RidgeMembrane",
    "GRCL9V3SaddleRegion",
    "GRCL9V3Separatrix",
    "GRCL9V3StableBasin",
    "GRCL9V3TensorHessianProfile",
    "GRCL9V3TransportReroutingLandscapeRegion",
    "GRCL9V3UnstableDirection",
    "GRCL9V3ValleyChannel",
    "compile_default_grcl9v3_landscape_examples_to_sources",
    "compile_default_grcl9v3_landscape_seed_examples_to_sources",
    "compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources",
    "compile_grcl9v3_landscape_example_to_source",
    "default_grcl9v3_landscape_examples",
    "default_grcl9v3_landscape_seed_examples",
    "extract_grcl9v3_landscape_example_from_seed",
    "grcl9v3_landscape_example_by_name",
    "grcl9v3_landscape_seed_example_by_name",
    "grcl9v3_landscape_seed_example_path_by_name",
    "grcl9v3_landscape_term_from_mapping",
    "legacy_grcl9v3_growth_landscape_seed_example_by_name",
    "legacy_grcl9v3_growth_landscape_seed_example_path_by_name",
    "legacy_grcl9v3_growth_landscape_seed_examples",
    "load_grcl9v3_landscape_seed_example",
]

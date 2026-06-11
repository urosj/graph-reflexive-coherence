"""Source schema contract for GRCL-9V3 Revision 1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
import re
from typing import Any

from .manifest import (
    GRCL9V3_BASE_NON_CLAIMS,
    GRCL9V3LoweringManifest,
    GRCL9V3_OWNERSHIP_TAGS,
    GRCL9V3_SOURCE_SCHEMA_VERSION,
    GRCL9V3TelemetryExpectation,
    default_grcl9v3_lowering_manifest,
)


_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_REVIEWED_MOTIF_ID_RE = re.compile(r"^grc9v3-motif-[a-z0-9]+(?:-[a-z0-9]+)*$")
_FORBIDDEN_RUNTIME_SOURCE_KEYS = frozenset(
    {
        "birth_event",
        "choice_happened",
        "collapse_happened",
        "current_flux",
        "daughter_sink_confirmed",
        "event_counts_by_kind",
        "event_history",
        "expansion_happened",
        "growth_count",
        "growth_happened",
        "hybrid_spark_completed",
        "runtime_events",
        "solved_basin",
        "solved_diagnostic",
        "solved_flux",
        "solved_hessian",
        "solved_tensor",
        "spark_count",
        "spark_happened",
    }
)
_HESSIAN_BACKENDS = frozenset({"row_basis_diagonal", "weighted_least_squares"})
_EXPANSION_DISTRIBUTION_MODES = frozenset({"equal", "custom"})
_BUDGET_POLICIES = frozenset({"none", "uniform_shift", "simplex_projection"})
_GROWTH_SEMANTICS = frozenset({"legacy_growth_locus", "front_capacity"})
_GROWTH_FRONT_CAPACITY_SOURCES = frozenset(
    {
        "spark_expansion_front",
        "refinement_boundary_capacity",
        "pressure_boundary",
        "preexisting_front",
        "legacy_source_growth_locus",
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


def _require_finite_float(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{field_name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be finite")
    return result


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    _validate_no_forbidden_runtime_fields(value, field_name=field_name)
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


def _validate_port(value: int, *, field_name: str) -> None:
    if value < 1 or value > 9:
        raise ValueError(f"{field_name} must be in the GRC9 port range [1, 9]")


def _validate_column(value: int, *, field_name: str) -> None:
    if value < 1 or value > 3:
        raise ValueError(f"{field_name} must be one of the three GRC9 columns")


def _validate_ownership(value: str, *, field_name: str = "ownership") -> None:
    if value not in GRCL9V3_OWNERSHIP_TAGS:
        raise ValueError(f"{field_name} is not a supported GRCL-9V3 ownership tag")


def _validate_no_forbidden_runtime_fields(value: Any, *, field_name: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_RUNTIME_SOURCE_KEYS:
                raise ValueError(f"{field_name}.{key_text} encodes runtime results")
            _validate_no_forbidden_runtime_fields(item, field_name=f"{field_name}.{key_text}")
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for index, item in enumerate(value):
            _validate_no_forbidden_runtime_fields(item, field_name=f"{field_name}[{index}]")


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
class GRCL9V3BridgePolicy:
    """Source bridge policy for connected lowered graphs."""

    edge_kind: str = "bridge"
    bridge_role: str = "mechanism_isolation"
    conductance_hint: float | None = None

    def __post_init__(self) -> None:
        if self.edge_kind != "bridge":
            raise ValueError('bridge edge policy must use grcl9v3_edge_kind = "bridge"')
        _validate_token(self.bridge_role, field_name="bridge_role")
        if self.conductance_hint is not None and (
            _require_finite_float(self.conductance_hint, field_name="conductance_hint") < 0.0
        ):
            raise ValueError("conductance_hint must be non-negative")

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "edge_kind": self.edge_kind,
            "bridge_role": self.bridge_role,
        }
        if self.conductance_hint is not None:
            payload["conductance_hint"] = self.conductance_hint
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3BridgePolicy:
        mapping = _require_mapping(value, field_name="bridge_policy")
        return cls(
            edge_kind=_require_string(mapping.get("edge_kind", "bridge"), field_name="edge_kind"),
            bridge_role=_require_string(
                mapping.get("bridge_role", "mechanism_isolation"),
                field_name="bridge_role",
            ),
            conductance_hint=(
                None
                if mapping.get("conductance_hint") is None
                else _require_finite_float(mapping.get("conductance_hint"), field_name="conductance_hint")
            ),
        )


@dataclass(frozen=True)
class GRCL9V3BudgetPolicy:
    """Source budget policy declaration."""

    budget_preservation_policy: str = "simplex_projection"

    def __post_init__(self) -> None:
        if self.budget_preservation_policy not in _BUDGET_POLICIES:
            raise ValueError("budget_preservation_policy is not recognized")

    def to_mapping(self) -> Mapping[str, Any]:
        return {"budget_preservation_policy": self.budget_preservation_policy}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3BudgetPolicy:
        mapping = _require_mapping(value, field_name="budget_policy")
        return cls(
            budget_preservation_policy=_require_string(
                mapping.get("budget_preservation_policy", "simplex_projection"),
                field_name="budget_preservation_policy",
            )
        )


@dataclass(frozen=True)
class GRCL9V3ProvenancePolicy:
    """Source provenance policy required by GRCL-9V3 lowering."""

    lowerer_revision: str = "grcl9v3_lowerer_rev1"
    require_node_edge_provenance: bool = True
    source_member_path: str = "extensions.grcl9v3"

    def __post_init__(self) -> None:
        _validate_token(self.lowerer_revision, field_name="lowerer_revision")
        _require_bool(self.require_node_edge_provenance, field_name="require_node_edge_provenance")
        if self.source_member_path != "extensions.grcl9v3":
            raise ValueError("source_member_path must be extensions.grcl9v3")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "lowerer_revision": self.lowerer_revision,
            "require_node_edge_provenance": self.require_node_edge_provenance,
            "source_member_path": self.source_member_path,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3ProvenancePolicy:
        mapping = _require_mapping(value, field_name="provenance_policy")
        return cls(
            lowerer_revision=_require_string(
                mapping.get("lowerer_revision", "grcl9v3_lowerer_rev1"),
                field_name="lowerer_revision",
            ),
            require_node_edge_provenance=_require_bool(
                mapping.get("require_node_edge_provenance", True),
                field_name="require_node_edge_provenance",
            ),
            source_member_path=_require_string(
                mapping.get("source_member_path", "extensions.grcl9v3"),
                field_name="source_member_path",
            ),
        )


@dataclass(frozen=True)
class _ConstructBase:
    construct_id: str
    motif_id: str
    source_role: str
    ownership: str
    expected_selector_ids: tuple[str, ...] = ()
    executable: bool = True
    non_claims: tuple[str, ...] = GRCL9V3_BASE_NON_CLAIMS

    def __post_init__(self) -> None:
        _validate_token(self.construct_id, field_name="construct_id")
        _validate_reviewed_motif_id(self.motif_id, field_name="motif_id")
        _validate_token(self.source_role, field_name="source_role")
        _validate_ownership(self.ownership)
        if not self.executable and "non_executable_source_construct" not in self.non_claims:
            raise ValueError(
                "non-executable constructs must include non_executable_source_construct"
            )
        for selector_id in self.expected_selector_ids:
            _validate_token(selector_id, field_name="expected_selector_ids[]")
        _require_bool(self.executable, field_name="executable")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")

    def _base_mapping(self, construct_kind: str) -> dict[str, Any]:
        return {
            "construct_kind": construct_kind,
            "construct_id": self.construct_id,
            "motif_id": self.motif_id,
            "source_role": self.source_role,
            "ownership": self.ownership,
            "expected_selector_ids": list(self.expected_selector_ids),
            "executable": self.executable,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class GRCL9V3HybridSparkRegion(_ConstructBase):
    candidate_region_id: str = ""
    saturation_profile: Mapping[str, Any] | None = None
    spark_gate_intent: str = "hybrid_hessian_tensor"
    spark_threshold: float = 0.0

    construct_kind = "hybrid_spark_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_region_id, field_name="candidate_region_id")
        _require_mapping(self.saturation_profile or {}, field_name="saturation_profile")
        _validate_token(self.spark_gate_intent, field_name="spark_gate_intent")
        if _require_finite_float(self.spark_threshold, field_name="spark_threshold") < 0.0:
            raise ValueError("spark_threshold must be non-negative")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_region_id": self.candidate_region_id,
                "saturation_profile": _json_safe(self.saturation_profile or {}),
                "spark_gate_intent": self.spark_gate_intent,
                "spark_threshold": self.spark_threshold,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3HybridSparkRegion:
        mapping = _require_mapping(value, field_name="hybrid_spark_region")
        return cls(**_base_kwargs(mapping), candidate_region_id=_require_string(mapping.get("candidate_region_id"), field_name="candidate_region_id"), saturation_profile=dict(_require_mapping(mapping.get("saturation_profile", {}), field_name="saturation_profile")), spark_gate_intent=_require_string(mapping.get("spark_gate_intent", "hybrid_hessian_tensor"), field_name="spark_gate_intent"), spark_threshold=_require_finite_float(mapping.get("spark_threshold", 0.0), field_name="spark_threshold"))


@dataclass(frozen=True)
class GRCL9V3RowBasisHessianProfile(_ConstructBase):
    candidate_region_id: str = ""
    hessian_backend: str = "row_basis_diagonal"
    row_basis_profile: Mapping[str, Any] | None = None
    signed_history_required: bool = False

    construct_kind = "row_basis_hessian_profile"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_region_id, field_name="candidate_region_id")
        if self.hessian_backend not in _HESSIAN_BACKENDS:
            raise ValueError("hessian_backend is not recognized")
        _require_mapping(self.row_basis_profile or {}, field_name="row_basis_profile")
        _require_bool(self.signed_history_required, field_name="signed_history_required")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_region_id": self.candidate_region_id,
                "hessian_backend": self.hessian_backend,
                "row_basis_profile": _json_safe(self.row_basis_profile or {}),
                "signed_history_required": self.signed_history_required,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3RowBasisHessianProfile:
        mapping = _require_mapping(value, field_name="row_basis_hessian_profile")
        return cls(**_base_kwargs(mapping), candidate_region_id=_require_string(mapping.get("candidate_region_id"), field_name="candidate_region_id"), hessian_backend=_require_string(mapping.get("hessian_backend", "row_basis_diagonal"), field_name="hessian_backend"), row_basis_profile=dict(_require_mapping(mapping.get("row_basis_profile", {}), field_name="row_basis_profile")), signed_history_required=_require_bool(mapping.get("signed_history_required", False), field_name="signed_history_required"))


@dataclass(frozen=True)
class GRCL9V3HybridTensorProfile(_ConstructBase):
    region_id: str = ""
    anisotropy_axis: str = "row_1"
    tensor_profile: Mapping[str, Any] | None = None

    construct_kind = "hybrid_tensor_profile"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.region_id, field_name="region_id")
        _validate_token(self.anisotropy_axis, field_name="anisotropy_axis")
        _require_mapping(self.tensor_profile or {}, field_name="tensor_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "region_id": self.region_id,
                "anisotropy_axis": self.anisotropy_axis,
                "tensor_profile": _json_safe(self.tensor_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3HybridTensorProfile:
        mapping = _require_mapping(value, field_name="hybrid_tensor_profile")
        return cls(**_base_kwargs(mapping), region_id=_require_string(mapping.get("region_id"), field_name="region_id"), anisotropy_axis=_require_string(mapping.get("anisotropy_axis", "row_1"), field_name="anisotropy_axis"), tensor_profile=dict(_require_mapping(mapping.get("tensor_profile", {}), field_name="tensor_profile")))


@dataclass(frozen=True)
class GRCL9V3ColumnProxyFallbackProfile(_ConstructBase):
    candidate_region_id: str = ""
    target_column: int = 1
    cancellation_mode: str = "near_cancellation"
    column_profile: Mapping[str, Any] | None = None

    construct_kind = "column_proxy_fallback_profile"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_region_id, field_name="candidate_region_id")
        _validate_column(self.target_column, field_name="target_column")
        _validate_token(self.cancellation_mode, field_name="cancellation_mode")
        _require_mapping(self.column_profile or {}, field_name="column_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_region_id": self.candidate_region_id,
                "target_column": self.target_column,
                "cancellation_mode": self.cancellation_mode,
                "column_profile": _json_safe(self.column_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3ColumnProxyFallbackProfile:
        mapping = _require_mapping(value, field_name="column_proxy_fallback_profile")
        return cls(**_base_kwargs(mapping), candidate_region_id=_require_string(mapping.get("candidate_region_id"), field_name="candidate_region_id"), target_column=_require_int(mapping.get("target_column"), field_name="target_column"), cancellation_mode=_require_string(mapping.get("cancellation_mode", "near_cancellation"), field_name="cancellation_mode"), column_profile=dict(_require_mapping(mapping.get("column_profile", {}), field_name="column_profile")))


@dataclass(frozen=True)
class GRCL9V3ExpansionRefinementRegion(_ConstructBase):
    candidate_region_id: str = ""
    target_effective_degree: int = 9
    expansion_distribution_mode: str = "equal"
    coherence_transfer_ratios: tuple[float, ...] = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    construct_kind = "expansion_refinement_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_region_id, field_name="candidate_region_id")
        if _require_int(self.target_effective_degree, field_name="target_effective_degree") < 1:
            raise ValueError("target_effective_degree must be positive")
        if self.expansion_distribution_mode not in _EXPANSION_DISTRIBUTION_MODES:
            raise ValueError("expansion_distribution_mode is not recognized")
        ratios = tuple(
            _require_finite_float(item, field_name="coherence_transfer_ratios[]")
            for item in self.coherence_transfer_ratios
        )
        if len(ratios) != 3 or any(item < 0.0 for item in ratios):
            raise ValueError("coherence_transfer_ratios must contain three non-negative values")
        if not math.isclose(sum(ratios), 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("coherence_transfer_ratios must sum to 1")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_region_id": self.candidate_region_id,
                "target_effective_degree": self.target_effective_degree,
                "expansion_distribution_mode": self.expansion_distribution_mode,
                "coherence_transfer_ratios": list(self.coherence_transfer_ratios),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3ExpansionRefinementRegion:
        mapping = _require_mapping(value, field_name="expansion_refinement_region")
        return cls(**_base_kwargs(mapping), candidate_region_id=_require_string(mapping.get("candidate_region_id"), field_name="candidate_region_id"), target_effective_degree=_require_int(mapping.get("target_effective_degree"), field_name="target_effective_degree"), expansion_distribution_mode=_require_string(mapping.get("expansion_distribution_mode", "equal"), field_name="expansion_distribution_mode"), coherence_transfer_ratios=tuple(_require_finite_float(item, field_name="coherence_transfer_ratios[]") for item in _require_sequence(mapping.get("coherence_transfer_ratios", (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)), field_name="coherence_transfer_ratios")))


@dataclass(frozen=True)
class GRCL9V3ChoiceCollapseRegion(_ConstructBase):
    choice_region_id: str = ""
    basin_region_a: str = ""
    basin_region_b: str = ""
    collapse_target_region: str = ""
    compatibility_profile: Mapping[str, Any] | None = None

    construct_kind = "choice_collapse_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name, value in (
            ("choice_region_id", self.choice_region_id),
            ("basin_region_a", self.basin_region_a),
            ("basin_region_b", self.basin_region_b),
            ("collapse_target_region", self.collapse_target_region),
        ):
            _validate_token(value, field_name=field_name)
        if self.basin_region_a == self.basin_region_b:
            raise ValueError("basin regions must be distinct")
        _require_mapping(self.compatibility_profile or {}, field_name="compatibility_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "choice_region_id": self.choice_region_id,
                "basin_region_a": self.basin_region_a,
                "basin_region_b": self.basin_region_b,
                "collapse_target_region": self.collapse_target_region,
                "compatibility_profile": _json_safe(self.compatibility_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3ChoiceCollapseRegion:
        mapping = _require_mapping(value, field_name="choice_collapse_region")
        return cls(**_base_kwargs(mapping), choice_region_id=_require_string(mapping.get("choice_region_id"), field_name="choice_region_id"), basin_region_a=_require_string(mapping.get("basin_region_a"), field_name="basin_region_a"), basin_region_b=_require_string(mapping.get("basin_region_b"), field_name="basin_region_b"), collapse_target_region=_require_string(mapping.get("collapse_target_region"), field_name="collapse_target_region"), compatibility_profile=dict(_require_mapping(mapping.get("compatibility_profile", {}), field_name="compatibility_profile")))


@dataclass(frozen=True)
class GRCL9V3GrowthLocus(_ConstructBase):
    parent_region_id: str = ""
    inactive_parent_port: int = 1
    outward_pressure_profile: Mapping[str, Any] | None = None
    lambda_birth: float = 0.0
    growth_semantics: str = "legacy_growth_locus"
    front_capacity_source: str = "legacy_source_growth_locus"
    front_source_construct_id: str | None = None

    construct_kind = "growth_locus"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.parent_region_id, field_name="parent_region_id")
        _validate_port(_require_int(self.inactive_parent_port, field_name="inactive_parent_port"), field_name="inactive_parent_port")
        _require_mapping(self.outward_pressure_profile or {}, field_name="outward_pressure_profile")
        if _require_finite_float(self.lambda_birth, field_name="lambda_birth") < 0.0:
            raise ValueError("lambda_birth must be non-negative")
        if self.growth_semantics not in _GROWTH_SEMANTICS:
            raise ValueError("growth_semantics is not recognized")
        if self.front_capacity_source not in _GROWTH_FRONT_CAPACITY_SOURCES:
            raise ValueError("front_capacity_source is not recognized")
        if self.front_source_construct_id is not None:
            _validate_token(self.front_source_construct_id, field_name="front_source_construct_id")
        if self.growth_semantics == "legacy_growth_locus":
            if self.front_capacity_source != "legacy_source_growth_locus":
                raise ValueError(
                    "legacy growth_locus must use legacy_source_growth_locus capacity source"
                )
        else:
            if self.front_capacity_source == "legacy_source_growth_locus":
                raise ValueError(
                    "front_capacity growth cannot use legacy_source_growth_locus"
                )
            if (
                self.front_capacity_source
                in {"spark_expansion_front", "refinement_boundary_capacity"}
                and self.front_source_construct_id is None
            ):
                raise ValueError(
                    "spark/refinement front growth requires front_source_construct_id"
                )

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "parent_region_id": self.parent_region_id,
                "inactive_parent_port": self.inactive_parent_port,
                "outward_pressure_profile": _json_safe(self.outward_pressure_profile or {}),
                "lambda_birth": self.lambda_birth,
                "growth_semantics": self.growth_semantics,
                "front_capacity_source": self.front_capacity_source,
            }
        )
        if self.front_source_construct_id is not None:
            payload["front_source_construct_id"] = self.front_source_construct_id
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3GrowthLocus:
        mapping = _require_mapping(value, field_name="growth_locus")
        return cls(**_base_kwargs(mapping), parent_region_id=_require_string(mapping.get("parent_region_id"), field_name="parent_region_id"), inactive_parent_port=_require_int(mapping.get("inactive_parent_port"), field_name="inactive_parent_port"), outward_pressure_profile=dict(_require_mapping(mapping.get("outward_pressure_profile", {}), field_name="outward_pressure_profile")), lambda_birth=_require_finite_float(mapping.get("lambda_birth"), field_name="lambda_birth"), growth_semantics=_require_string(mapping.get("growth_semantics", "legacy_growth_locus"), field_name="growth_semantics"), front_capacity_source=_require_string(mapping.get("front_capacity_source", "legacy_source_growth_locus"), field_name="front_capacity_source"), front_source_construct_id=(None if mapping.get("front_source_construct_id") is None else _require_string(mapping.get("front_source_construct_id"), field_name="front_source_construct_id")))


@dataclass(frozen=True)
class GRCL9V3TransportReroutingRegion(_ConstructBase):
    route_region_id: str = ""
    source_region_id: str = ""
    sink_region_id: str = ""
    route_preference_profile: Mapping[str, Any] | None = None

    construct_kind = "transport_rerouting_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name, value in (
            ("route_region_id", self.route_region_id),
            ("source_region_id", self.source_region_id),
            ("sink_region_id", self.sink_region_id),
        ):
            _validate_token(value, field_name=field_name)
        _require_mapping(self.route_preference_profile or {}, field_name="route_preference_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "route_region_id": self.route_region_id,
                "source_region_id": self.source_region_id,
                "sink_region_id": self.sink_region_id,
                "route_preference_profile": _json_safe(self.route_preference_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3TransportReroutingRegion:
        mapping = _require_mapping(value, field_name="transport_rerouting_region")
        return cls(**_base_kwargs(mapping), route_region_id=_require_string(mapping.get("route_region_id"), field_name="route_region_id"), source_region_id=_require_string(mapping.get("source_region_id"), field_name="source_region_id"), sink_region_id=_require_string(mapping.get("sink_region_id"), field_name="sink_region_id"), route_preference_profile=dict(_require_mapping(mapping.get("route_preference_profile", {}), field_name="route_preference_profile")))


@dataclass(frozen=True)
class GRCL9V3AppendixEDivisionRegion(_ConstructBase):
    parent_region_id: str = ""
    daughter_region_a: str = ""
    daughter_region_b: str = ""
    module_basin_support: Mapping[str, Any] | None = None

    construct_kind = "appendix_e_division_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name, value in (
            ("parent_region_id", self.parent_region_id),
            ("daughter_region_a", self.daughter_region_a),
            ("daughter_region_b", self.daughter_region_b),
        ):
            _validate_token(value, field_name=field_name)
        if self.daughter_region_a == self.daughter_region_b:
            raise ValueError("daughter regions must be distinct")
        _require_mapping(self.module_basin_support or {}, field_name="module_basin_support")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "parent_region_id": self.parent_region_id,
                "daughter_region_a": self.daughter_region_a,
                "daughter_region_b": self.daughter_region_b,
                "module_basin_support": _json_safe(self.module_basin_support or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3AppendixEDivisionRegion:
        mapping = _require_mapping(value, field_name="appendix_e_division_region")
        return cls(**_base_kwargs(mapping), parent_region_id=_require_string(mapping.get("parent_region_id"), field_name="parent_region_id"), daughter_region_a=_require_string(mapping.get("daughter_region_a"), field_name="daughter_region_a"), daughter_region_b=_require_string(mapping.get("daughter_region_b"), field_name="daughter_region_b"), module_basin_support=dict(_require_mapping(mapping.get("module_basin_support", {}), field_name="module_basin_support")))


@dataclass(frozen=True)
class GRCL9V3QuiescentHybridRegion(_ConstructBase):
    region_id: str = ""
    stability_margin_profile: Mapping[str, Any] | None = None

    construct_kind = "quiescent_hybrid_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.region_id, field_name="region_id")
        _require_mapping(self.stability_margin_profile or {}, field_name="stability_margin_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "region_id": self.region_id,
                "stability_margin_profile": _json_safe(self.stability_margin_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3QuiescentHybridRegion:
        mapping = _require_mapping(value, field_name="quiescent_hybrid_region")
        return cls(**_base_kwargs(mapping), region_id=_require_string(mapping.get("region_id"), field_name="region_id"), stability_margin_profile=dict(_require_mapping(mapping.get("stability_margin_profile", {}), field_name="stability_margin_profile")))


GRCL9V3SourceConstruct = (
    GRCL9V3HybridSparkRegion
    | GRCL9V3RowBasisHessianProfile
    | GRCL9V3HybridTensorProfile
    | GRCL9V3ColumnProxyFallbackProfile
    | GRCL9V3ExpansionRefinementRegion
    | GRCL9V3ChoiceCollapseRegion
    | GRCL9V3GrowthLocus
    | GRCL9V3TransportReroutingRegion
    | GRCL9V3AppendixEDivisionRegion
    | GRCL9V3QuiescentHybridRegion
)

_CONSTRUCT_BY_KIND = {
    GRCL9V3HybridSparkRegion.construct_kind: GRCL9V3HybridSparkRegion,
    GRCL9V3RowBasisHessianProfile.construct_kind: GRCL9V3RowBasisHessianProfile,
    GRCL9V3HybridTensorProfile.construct_kind: GRCL9V3HybridTensorProfile,
    GRCL9V3ColumnProxyFallbackProfile.construct_kind: GRCL9V3ColumnProxyFallbackProfile,
    GRCL9V3ExpansionRefinementRegion.construct_kind: GRCL9V3ExpansionRefinementRegion,
    GRCL9V3ChoiceCollapseRegion.construct_kind: GRCL9V3ChoiceCollapseRegion,
    GRCL9V3GrowthLocus.construct_kind: GRCL9V3GrowthLocus,
    GRCL9V3TransportReroutingRegion.construct_kind: GRCL9V3TransportReroutingRegion,
    GRCL9V3AppendixEDivisionRegion.construct_kind: GRCL9V3AppendixEDivisionRegion,
    GRCL9V3QuiescentHybridRegion.construct_kind: GRCL9V3QuiescentHybridRegion,
}


def grcl9v3_source_construct_from_mapping(value: Mapping[str, Any]) -> GRCL9V3SourceConstruct:
    mapping = _require_mapping(value, field_name="source_construct")
    construct_kind = _require_string(mapping.get("construct_kind"), field_name="construct_kind")
    construct_type = _CONSTRUCT_BY_KIND.get(construct_kind)
    if construct_type is None:
        raise ValueError(f"unsupported GRCL-9V3 source construct kind {construct_kind!r}")
    return construct_type.from_mapping(mapping)


@dataclass(frozen=True)
class GRCL9V3SourceDocument:
    fixture_name: str
    manifest_entry_id: str
    expected_selector_ids: tuple[str, ...]
    constructs: tuple[GRCL9V3SourceConstruct, ...]
    source_schema_version: str = GRCL9V3_SOURCE_SCHEMA_VERSION
    bridge_policy: GRCL9V3BridgePolicy = GRCL9V3BridgePolicy()
    budget_policy: GRCL9V3BudgetPolicy = GRCL9V3BudgetPolicy()
    provenance_policy: GRCL9V3ProvenancePolicy = GRCL9V3ProvenancePolicy()
    expected_telemetry: tuple[GRCL9V3TelemetryExpectation, ...] = ()
    non_claims: tuple[str, ...] = GRCL9V3_BASE_NON_CLAIMS
    notes: Mapping[str, Any] | None = None
    compiled_source_provenance: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.source_schema_version != GRCL9V3_SOURCE_SCHEMA_VERSION:
            raise ValueError(f"source_schema_version must be {GRCL9V3_SOURCE_SCHEMA_VERSION!r}")
        _validate_token(self.fixture_name, field_name="fixture_name")
        _validate_token(self.manifest_entry_id, field_name="manifest_entry_id")
        if not self.expected_selector_ids:
            raise ValueError("expected_selector_ids must not be empty")
        for selector_id in self.expected_selector_ids:
            _validate_token(selector_id, field_name="expected_selector_ids[]")
        if not self.constructs:
            raise ValueError("constructs must not be empty")
        construct_ids = [item.construct_id for item in self.constructs]
        if len(construct_ids) != len(set(construct_ids)):
            raise ValueError("construct_id values must be unique")
        motif_ids = {item.motif_id for item in self.constructs}
        if len(motif_ids) != 1:
            raise ValueError("all constructs in a source document must share one motif_id")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")
        _require_mapping(self.notes or {}, field_name="notes")
        _require_mapping(
            self.compiled_source_provenance or {},
            field_name="compiled_source_provenance",
        )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "source_schema_version": self.source_schema_version,
            "fixture_name": self.fixture_name,
            "manifest_entry_id": self.manifest_entry_id,
            "expected_selector_ids": list(self.expected_selector_ids),
            "constructs": [item.to_mapping() for item in self.constructs],
            "bridge_policy": self.bridge_policy.to_mapping(),
            "budget_policy": self.budget_policy.to_mapping(),
            "provenance_policy": self.provenance_policy.to_mapping(),
            "expected_telemetry": [item.to_mapping() for item in self.expected_telemetry],
            "non_claims": list(self.non_claims),
            "notes": _json_safe(self.notes or {}),
        }
        if self.compiled_source_provenance:
            payload["compiled_source_provenance"] = _json_safe(
                self.compiled_source_provenance
            )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3SourceDocument:
        mapping = _require_mapping(value, field_name="source_document")
        return cls(
            source_schema_version=_require_string(
                mapping.get("source_schema_version", GRCL9V3_SOURCE_SCHEMA_VERSION),
                field_name="source_schema_version",
            ),
            fixture_name=_require_string(mapping.get("fixture_name"), field_name="fixture_name"),
            manifest_entry_id=_require_string(
                mapping.get("manifest_entry_id"),
                field_name="manifest_entry_id",
            ),
            expected_selector_ids=_string_tuple(
                mapping.get("expected_selector_ids", ()),
                field_name="expected_selector_ids",
            ),
            constructs=tuple(
                grcl9v3_source_construct_from_mapping(item)
                for item in _require_sequence(mapping.get("constructs", ()), field_name="constructs")
            ),
            bridge_policy=GRCL9V3BridgePolicy.from_mapping(
                mapping.get("bridge_policy", GRCL9V3BridgePolicy().to_mapping())
            ),
            budget_policy=GRCL9V3BudgetPolicy.from_mapping(
                mapping.get("budget_policy", GRCL9V3BudgetPolicy().to_mapping())
            ),
            provenance_policy=GRCL9V3ProvenancePolicy.from_mapping(
                mapping.get("provenance_policy", GRCL9V3ProvenancePolicy().to_mapping())
            ),
            expected_telemetry=tuple(
                GRCL9V3TelemetryExpectation.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("expected_telemetry", ()),
                    field_name="expected_telemetry",
                )
            ),
            non_claims=_string_tuple(
                mapping.get("non_claims", GRCL9V3_BASE_NON_CLAIMS),
                field_name="non_claims",
            ),
            notes=dict(_require_mapping(mapping.get("notes", {}), field_name="notes")),
            compiled_source_provenance=dict(
                _require_mapping(
                    mapping.get("compiled_source_provenance", {}),
                    field_name="compiled_source_provenance",
                )
            ),
    )


def validate_grcl9v3_source_document_against_manifest(
    document: GRCL9V3SourceDocument,
    manifest: GRCL9V3LoweringManifest | None = None,
    *,
    allow_future_vocabulary: bool = False,
) -> Mapping[str, Any]:
    """Validate a source document link against a GRCL-9V3 lowering manifest."""

    active_manifest = manifest or default_grcl9v3_lowering_manifest()
    if document.manifest_entry_id == "composed_grcl9v3_hybrid_composition_v1":
        return _validate_composed_source_document(document, active_manifest)
    entry = active_manifest.by_entry_id().get(document.manifest_entry_id)
    if entry is None:
        if allow_future_vocabulary:
            return _validate_future_vocabulary_document(document, active_manifest)
        raise ValueError(f"manifest_entry_id {document.manifest_entry_id!r} is not in manifest")
    document_motif_ids = {construct.motif_id for construct in document.constructs}
    if not document_motif_ids <= set(entry.reviewed_motif_ids):
        raise ValueError("source document motif_id is not covered by manifest entry")
    construct_kinds = {
        str(construct.to_mapping()["construct_kind"]) for construct in document.constructs
    }
    if not construct_kinds <= set(entry.source_construct_kinds):
        raise ValueError("source document construct kinds are not allowed by manifest entry")
    ownership_tags = {construct.ownership for construct in document.constructs}
    if not ownership_tags <= set(entry.ownership_tags):
        raise ValueError("source document ownership tags are not allowed by manifest entry")
    expected_selectors = set(document.expected_selector_ids)
    entry_selectors = {
        selector_id for control in entry.controls for selector_id in control.selector_ids
    }
    if entry_selectors and not expected_selectors <= entry_selectors:
        raise ValueError("source document expected selectors are not covered by manifest entry")
    return {
        "linkage_kind": "manifest_entry",
        "manifest_entry_id": document.manifest_entry_id,
        "motif_ids": sorted(document_motif_ids),
        "construct_kinds": sorted(construct_kinds),
        "ownership_tags": sorted(ownership_tags),
    }


def validate_grcl9v3_paper_facing_growth_semantics(
    document: GRCL9V3SourceDocument,
) -> Mapping[str, Any]:
    """Validate that executable growth uses paper-facing front semantics.

    Legacy standalone growth loci remain loadable for replay diagnostics, but
    they are not valid paper-facing GRCL-9V3 growth evidence.
    """

    construct_ids = {construct.construct_id for construct in document.constructs}
    growth_records: list[dict[str, Any]] = []
    for construct in document.constructs:
        if not isinstance(construct, GRCL9V3GrowthLocus) or not construct.executable:
            continue
        if construct.growth_semantics != "front_capacity":
            raise ValueError(
                "standalone executable growth_locus is legacy diagnostic evidence; "
                "paper-facing growth requires front_capacity semantics"
            )
        if construct.front_capacity_source == "legacy_source_growth_locus":
            raise ValueError("paper-facing growth cannot use legacy_source_growth_locus")
        if (
            construct.front_source_construct_id is not None
            and construct.front_source_construct_id not in construct_ids
        ):
            raise ValueError("front_source_construct_id must reference a source construct")
        growth_records.append(
            {
                "construct_id": construct.construct_id,
                "parent_region_id": construct.parent_region_id,
                "inactive_parent_port": construct.inactive_parent_port,
                "front_capacity_source": construct.front_capacity_source,
                "front_source_construct_id": construct.front_source_construct_id,
            }
        )
    return {
        "growth_semantics": "front_capacity" if growth_records else "none",
        "growth_records": growth_records,
    }


def _validate_future_vocabulary_document(
    document: GRCL9V3SourceDocument,
    manifest: GRCL9V3LoweringManifest,
) -> Mapping[str, Any]:
    future_by_motif = {record.motif_id: record for record in manifest.future_vocabulary_records}
    document_motif_ids = {construct.motif_id for construct in document.constructs}
    if len(document_motif_ids) != 1:
        raise ValueError("future vocabulary document must have one motif_id")
    motif_id = next(iter(document_motif_ids))
    record = future_by_motif.get(motif_id)
    if record is None:
        raise ValueError("source document motif_id is not covered by manifest entry")
    if document.manifest_entry_id != f"future_vocabulary_{record.phenomenon}_v1":
        raise ValueError("future vocabulary document manifest_entry_id does not match record")
    return {
        "linkage_kind": "future_vocabulary_record",
        "manifest_entry_id": document.manifest_entry_id,
        "motif_ids": [motif_id],
        "construct_kinds": sorted(str(item.to_mapping()["construct_kind"]) for item in document.constructs),
        "ownership_tags": sorted({construct.ownership for construct in document.constructs}),
    }


def _validate_composed_source_document(
    document: GRCL9V3SourceDocument,
    manifest: GRCL9V3LoweringManifest,
) -> Mapping[str, Any]:
    provenance = document.compiled_source_provenance or {}
    ancestry = provenance.get("composed_source_ancestry") or document.notes.get(
        "composed_source_ancestry"
    )
    if (
        not isinstance(ancestry, Sequence)
        or isinstance(ancestry, str)
        or len(tuple(ancestry)) < 2
    ):
        raise ValueError("composed GRCL-9V3 source documents require source ancestry")
    construct_kinds = {
        str(construct.to_mapping()["construct_kind"]) for construct in document.constructs
    }
    allowed_kinds = set(_CONSTRUCT_BY_KIND)
    allowed_ownership = set()
    allowed_selectors = set()
    for entry in manifest.entries:
        allowed_kinds.update(entry.source_construct_kinds)
        allowed_ownership.update(entry.ownership_tags)
        for control in entry.controls:
            allowed_selectors.update(control.selector_ids)
    from .selector_expansions import GRCL9V3_SOURCE_SELECTOR_EXPANSIONS

    allowed_selectors.update(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS)
    if not construct_kinds <= allowed_kinds:
        raise ValueError("composed source document construct kinds are not allowed")
    ownership_tags = {construct.ownership for construct in document.constructs}
    if not ownership_tags <= allowed_ownership:
        raise ValueError("composed source document ownership tags are not allowed")
    if not set(document.expected_selector_ids) <= allowed_selectors:
        raise ValueError("composed source document expected selectors are not covered")
    return {
        "linkage_kind": "composed_source",
        "manifest_entry_id": document.manifest_entry_id,
        "motif_ids": sorted({construct.motif_id for construct in document.constructs}),
        "construct_kinds": sorted(construct_kinds),
        "ownership_tags": sorted(ownership_tags),
        "composed_source_ancestry": [str(item) for item in ancestry],
    }


def _base_kwargs(mapping: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "construct_id": _require_string(mapping.get("construct_id"), field_name="construct_id"),
        "motif_id": _require_string(mapping.get("motif_id"), field_name="motif_id"),
        "source_role": _require_string(mapping.get("source_role"), field_name="source_role"),
        "ownership": _require_string(mapping.get("ownership"), field_name="ownership"),
        "expected_selector_ids": _string_tuple(
            mapping.get("expected_selector_ids", ()),
            field_name="expected_selector_ids",
        ),
        "executable": _require_bool(mapping.get("executable", True), field_name="executable"),
        "non_claims": _string_tuple(
            mapping.get("non_claims", GRCL9V3_BASE_NON_CLAIMS),
            field_name="non_claims",
        ),
    }


__all__ = [
    "GRCL9V3AppendixEDivisionRegion",
    "GRCL9V3BridgePolicy",
    "GRCL9V3BudgetPolicy",
    "GRCL9V3ChoiceCollapseRegion",
    "GRCL9V3ColumnProxyFallbackProfile",
    "GRCL9V3ExpansionRefinementRegion",
    "GRCL9V3GrowthLocus",
    "GRCL9V3HybridSparkRegion",
    "GRCL9V3HybridTensorProfile",
    "GRCL9V3ProvenancePolicy",
    "GRCL9V3QuiescentHybridRegion",
    "GRCL9V3RowBasisHessianProfile",
    "GRCL9V3SourceConstruct",
    "GRCL9V3SourceDocument",
    "GRCL9V3TransportReroutingRegion",
    "grcl9v3_source_construct_from_mapping",
    "validate_grcl9v3_paper_facing_growth_semantics",
    "validate_grcl9v3_source_document_against_manifest",
]

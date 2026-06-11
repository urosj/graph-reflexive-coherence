"""Source schema contract for GRCL-9 Revision 1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
import re
from typing import Any

from .manifest import (
    GRCL9_BASE_NON_CLAIMS,
    GRCL9_RESERVED_SPARK_GATE_INTENTS,
    GRCL9_SOURCE_SCHEMA_VERSION,
    GRCL9_SPARK_GATE_INTENTS,
    GRCL9TelemetryExpectation,
)


_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_FORBIDDEN_RUNTIME_SOURCE_KEYS = frozenset(
    {
        "birth_event",
        "current_flux",
        "event_counts_by_kind",
        "event_history",
        "expansion_completed",
        "expansion_count",
        "fission_confirmed",
        "growth_count",
        "runtime_events",
        "solved_diagnostic",
        "solved_flux",
        "spark_count",
        "spark_happened",
    }
)
_BUDGET_POLICIES = frozenset(
    {
        "none",
        "uniform_shift",
        "simplex_projection",
        "proportional_removal",
        "negative_mass_clamp",
        "remainder_tracking",
    }
)
_MASS_PARTITION_MODES = frozenset({"conserved", "source_budget_partition"})
_GROWTH_SEMANTICS = frozenset({"legacy_growth_locus", "front_capacity"})
_GROWTH_FRONT_CAPACITY_SOURCES = frozenset(
    {
        "spark_expansion_front",
        "refinement_boundary_capacity",
        "preexisting_front",
        "pressure_boundary",
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


def _validate_port(value: int, *, field_name: str) -> None:
    if value < 1 or value > 9:
        raise ValueError(f"{field_name} must be in the GRC9 port range [1, 9]")


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
class GRCL9BridgePolicy:
    """Source bridge policy for connected lowered graphs."""

    edge_kind: str = "bridge"
    bridge_role: str = "mechanism_isolation"
    conductance_hint: float | None = None

    def __post_init__(self) -> None:
        if self.edge_kind != "bridge":
            raise ValueError('bridge edge policy must use grcl9_edge_kind = "bridge"')
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
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9BridgePolicy:
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
class GRCL9BudgetPolicy:
    """Source budget policy declaration."""

    budget_preservation_policy: str = "simplex_projection"
    mass_partition_mode: str = "source_budget_partition"

    def __post_init__(self) -> None:
        if self.budget_preservation_policy not in _BUDGET_POLICIES:
            raise ValueError("budget_preservation_policy is not recognized")
        if self.mass_partition_mode not in _MASS_PARTITION_MODES:
            raise ValueError("mass_partition_mode is not recognized")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "budget_preservation_policy": self.budget_preservation_policy,
            "mass_partition_mode": self.mass_partition_mode,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9BudgetPolicy:
        mapping = _require_mapping(value, field_name="budget_policy")
        return cls(
            budget_preservation_policy=_require_string(
                mapping.get("budget_preservation_policy", "simplex_projection"),
                field_name="budget_preservation_policy",
            ),
            mass_partition_mode=_require_string(
                mapping.get("mass_partition_mode", "source_budget_partition"),
                field_name="mass_partition_mode",
            ),
        )


@dataclass(frozen=True)
class GRCL9ProvenancePolicy:
    """Source provenance policy required by GRCL-9 lowering."""

    projector_revision: str = "grcl9_projector_rev1"
    require_node_edge_provenance: bool = True
    source_member_path: str = "extensions.grcl9"

    def __post_init__(self) -> None:
        _validate_token(self.projector_revision, field_name="projector_revision")
        _require_bool(self.require_node_edge_provenance, field_name="require_node_edge_provenance")
        _require_string(self.source_member_path, field_name="source_member_path")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "projector_revision": self.projector_revision,
            "require_node_edge_provenance": self.require_node_edge_provenance,
            "source_member_path": self.source_member_path,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9ProvenancePolicy:
        mapping = _require_mapping(value, field_name="provenance_policy")
        return cls(
            projector_revision=_require_string(
                mapping.get("projector_revision", "grcl9_projector_rev1"),
                field_name="projector_revision",
            ),
            require_node_edge_provenance=_require_bool(
                mapping.get("require_node_edge_provenance", True),
                field_name="require_node_edge_provenance",
            ),
            source_member_path=_require_string(
                mapping.get("source_member_path", "extensions.grcl9"),
                field_name="source_member_path",
            ),
        )


@dataclass(frozen=True)
class _ConstructBase:
    construct_id: str
    motif_id: str
    executable: bool = True
    non_claims: tuple[str, ...] = GRCL9_BASE_NON_CLAIMS

    def __post_init__(self) -> None:
        _validate_token(self.construct_id, field_name="construct_id")
        _validate_token(self.motif_id, field_name="motif_id")
        _require_bool(self.executable, field_name="executable")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")

    def _base_mapping(self, construct_kind: str) -> dict[str, Any]:
        return {
            "construct_kind": construct_kind,
            "construct_id": self.construct_id,
            "motif_id": self.motif_id,
            "executable": self.executable,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class GRCL9SparkCandidateRegion(_ConstructBase):
    """Source-declared saturated spark-capable region."""

    candidate_id: str = ""
    coherence_allocation: Mapping[str, Any] | None = None
    neighbor_coherence_profile: Mapping[str, Any] | None = None
    spark_gate_intent: str = "saturation_column_proxy"

    construct_kind = "spark_candidate_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_id, field_name="candidate_id")
        _require_mapping(self.coherence_allocation or {}, field_name="coherence_allocation")
        _require_mapping(self.neighbor_coherence_profile or {}, field_name="neighbor_coherence_profile")
        if self.spark_gate_intent in GRCL9_RESERVED_SPARK_GATE_INTENTS and self.executable:
            raise ValueError("reserved spark gate intents require executable=false")
        if self.spark_gate_intent not in GRCL9_SPARK_GATE_INTENTS | GRCL9_RESERVED_SPARK_GATE_INTENTS:
            raise ValueError("spark_gate_intent is not recognized")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_id": self.candidate_id,
                "coherence_allocation": _json_safe(self.coherence_allocation or {}),
                "neighbor_coherence_profile": _json_safe(self.neighbor_coherence_profile or {}),
                "spark_gate_intent": self.spark_gate_intent,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9SparkCandidateRegion:
        mapping = _require_mapping(value, field_name="spark_candidate_region")
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            candidate_id=_require_string(mapping.get("candidate_id"), field_name="candidate_id"),
            coherence_allocation=dict(
                _require_mapping(mapping.get("coherence_allocation", {}), field_name="coherence_allocation")
            ),
            neighbor_coherence_profile=dict(
                _require_mapping(
                    mapping.get("neighbor_coherence_profile", {}),
                    field_name="neighbor_coherence_profile",
                )
            ),
            spark_gate_intent=_require_string(
                mapping.get("spark_gate_intent"),
                field_name="spark_gate_intent",
            ),
        )


@dataclass(frozen=True)
class GRCL9ColumnProxyProfile(_ConstructBase):
    """Source-declared column diagnostic profile."""

    candidate_id: str = ""
    target_column: int = 1
    cancellation_mode: str = "cancellation"
    conductance_profile: Mapping[str, Any] | None = None
    coherence_profile: Mapping[str, Any] | None = None

    construct_kind = "column_proxy_profile"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_id, field_name="candidate_id")
        _validate_port(self.target_column, field_name="target_column")
        if self.target_column > 3:
            raise ValueError("target_column must be one of the three GRC9 columns")
        _validate_token(self.cancellation_mode, field_name="cancellation_mode")
        _require_mapping(self.conductance_profile or {}, field_name="conductance_profile")
        _require_mapping(self.coherence_profile or {}, field_name="coherence_profile")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_id": self.candidate_id,
                "target_column": self.target_column,
                "cancellation_mode": self.cancellation_mode,
                "conductance_profile": _json_safe(self.conductance_profile or {}),
                "coherence_profile": _json_safe(self.coherence_profile or {}),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9ColumnProxyProfile:
        mapping = _require_mapping(value, field_name="column_proxy_profile")
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            candidate_id=_require_string(mapping.get("candidate_id"), field_name="candidate_id"),
            target_column=_require_int(mapping.get("target_column"), field_name="target_column"),
            cancellation_mode=_require_string(mapping.get("cancellation_mode"), field_name="cancellation_mode"),
            conductance_profile=dict(
                _require_mapping(mapping.get("conductance_profile", {}), field_name="conductance_profile")
            ),
            coherence_profile=dict(
                _require_mapping(mapping.get("coherence_profile", {}), field_name="coherence_profile")
            ),
        )


@dataclass(frozen=True)
class GRCL9InstabilityProfile(_ConstructBase):
    """Source-declared row tensor and cut/support profile."""

    candidate_id: str = ""
    row_anisotropy_profile: Mapping[str, Any] | None = None
    support_cut_profile: Mapping[str, Any] | None = None
    tau_instability: float = 0.0

    construct_kind = "instability_profile"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_id, field_name="candidate_id")
        _require_mapping(self.row_anisotropy_profile or {}, field_name="row_anisotropy_profile")
        _require_mapping(self.support_cut_profile or {}, field_name="support_cut_profile")
        if _require_finite_float(self.tau_instability, field_name="tau_instability") < 0.0:
            raise ValueError("tau_instability must be non-negative")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_id": self.candidate_id,
                "row_anisotropy_profile": _json_safe(self.row_anisotropy_profile or {}),
                "support_cut_profile": _json_safe(self.support_cut_profile or {}),
                "tau_instability": self.tau_instability,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9InstabilityProfile:
        mapping = _require_mapping(value, field_name="instability_profile")
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            candidate_id=_require_string(mapping.get("candidate_id"), field_name="candidate_id"),
            row_anisotropy_profile=dict(
                _require_mapping(
                    mapping.get("row_anisotropy_profile", {}),
                    field_name="row_anisotropy_profile",
                )
            ),
            support_cut_profile=dict(
                _require_mapping(mapping.get("support_cut_profile", {}), field_name="support_cut_profile")
            ),
            tau_instability=_require_finite_float(mapping.get("tau_instability"), field_name="tau_instability"),
        )


@dataclass(frozen=True)
class GRCL9ExpansionRefinementRegion(_ConstructBase):
    """Source-declared expansion policy region."""

    candidate_id: str = ""
    target_effective_degree: int = 0
    module_size_formula: str = "max(1, ceil((D_eff - 2) / 7))"
    bond_weight_mode: str = "fixed"
    coherence_transfer_mode: str = "equal"
    coherence_transfer_ratios: tuple[float, float, float] = (1 / 3, 1 / 3, 1 / 3)

    construct_kind = "expansion_refinement_region"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.candidate_id, field_name="candidate_id")
        if _require_int(self.target_effective_degree, field_name="target_effective_degree") <= 0:
            raise ValueError("target_effective_degree must be positive")
        _require_string(self.module_size_formula, field_name="module_size_formula")
        _validate_token(self.bond_weight_mode, field_name="bond_weight_mode")
        _validate_token(self.coherence_transfer_mode, field_name="coherence_transfer_mode")
        if len(self.coherence_transfer_ratios) != 3:
            raise ValueError("coherence_transfer_ratios must contain three ratios")
        ratios = tuple(
            _require_finite_float(item, field_name=f"coherence_transfer_ratios[{index}]")
            for index, item in enumerate(self.coherence_transfer_ratios)
        )
        if any(item < 0.0 for item in ratios) or sum(ratios) <= 0.0:
            raise ValueError("coherence_transfer_ratios must be non-negative and nonzero")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "candidate_id": self.candidate_id,
                "target_effective_degree": self.target_effective_degree,
                "module_size_formula": self.module_size_formula,
                "bond_weight_mode": self.bond_weight_mode,
                "coherence_transfer_mode": self.coherence_transfer_mode,
                "coherence_transfer_ratios": list(self.coherence_transfer_ratios),
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9ExpansionRefinementRegion:
        mapping = _require_mapping(value, field_name="expansion_refinement_region")
        ratios_raw = _require_sequence(
            mapping.get("coherence_transfer_ratios", (1 / 3, 1 / 3, 1 / 3)),
            field_name="coherence_transfer_ratios",
        )
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            candidate_id=_require_string(mapping.get("candidate_id"), field_name="candidate_id"),
            target_effective_degree=_require_int(
                mapping.get("target_effective_degree"),
                field_name="target_effective_degree",
            ),
            module_size_formula=_require_string(
                mapping.get("module_size_formula", "max(1, ceil((D_eff - 2) / 7))"),
                field_name="module_size_formula",
            ),
            bond_weight_mode=_require_string(mapping.get("bond_weight_mode", "fixed"), field_name="bond_weight_mode"),
            coherence_transfer_mode=_require_string(
                mapping.get("coherence_transfer_mode", "equal"),
                field_name="coherence_transfer_mode",
            ),
            coherence_transfer_ratios=tuple(
                _require_finite_float(item, field_name=f"coherence_transfer_ratios[{index}]")
                for index, item in enumerate(ratios_raw)
            ),  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class GRCL9GrowthLocus(_ConstructBase):
    """Source-declared growth locus."""

    parent_id: str = ""
    inactive_parent_port: int = 1
    pressure_profile: Mapping[str, Any] | None = None
    birth_rule: str = "outward_flux_pressure"
    lambda_birth: float = 0.0
    growth_semantics: str = "legacy_growth_locus"
    front_capacity_source: str = "legacy_source_growth_locus"
    front_source_construct_id: str | None = None

    construct_kind = "growth_locus"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.parent_id, field_name="parent_id")
        _validate_port(self.inactive_parent_port, field_name="inactive_parent_port")
        _require_mapping(self.pressure_profile or {}, field_name="pressure_profile")
        if self.birth_rule != "outward_flux_pressure":
            raise ValueError("birth_rule must be outward_flux_pressure")
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
                "parent_id": self.parent_id,
                "inactive_parent_port": self.inactive_parent_port,
                "pressure_profile": _json_safe(self.pressure_profile or {}),
                "birth_rule": self.birth_rule,
                "lambda_birth": self.lambda_birth,
                "growth_semantics": self.growth_semantics,
                "front_capacity_source": self.front_capacity_source,
            }
        )
        if self.front_source_construct_id is not None:
            payload["front_source_construct_id"] = self.front_source_construct_id
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9GrowthLocus:
        mapping = _require_mapping(value, field_name="growth_locus")
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            parent_id=_require_string(mapping.get("parent_id"), field_name="parent_id"),
            inactive_parent_port=_require_int(
                mapping.get("inactive_parent_port"),
                field_name="inactive_parent_port",
            ),
            pressure_profile=dict(
                _require_mapping(mapping.get("pressure_profile", {}), field_name="pressure_profile")
            ),
            birth_rule=_require_string(mapping.get("birth_rule", "outward_flux_pressure"), field_name="birth_rule"),
            lambda_birth=_require_finite_float(mapping.get("lambda_birth"), field_name="lambda_birth"),
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
class GRCL9PostExpansionFissionGeometry(_ConstructBase):
    """Source-declared two-sink-capable fission geometry."""

    module_region_id: str = ""
    sink_region_a: str = ""
    sink_region_b: str = ""
    identity_fission_min_basin_mass: float = 0.0
    identity_fission_persistence_delta: int = 0
    separable_conductance_geometry: bool = True

    construct_kind = "post_expansion_fission_geometry"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validate_token(self.module_region_id, field_name="module_region_id")
        _validate_token(self.sink_region_a, field_name="sink_region_a")
        _validate_token(self.sink_region_b, field_name="sink_region_b")
        if self.sink_region_a == self.sink_region_b:
            raise ValueError("sink regions must be distinct")
        if _require_finite_float(
            self.identity_fission_min_basin_mass,
            field_name="identity_fission_min_basin_mass",
        ) < 0.0:
            raise ValueError("identity_fission_min_basin_mass must be non-negative")
        if _require_int(
            self.identity_fission_persistence_delta,
            field_name="identity_fission_persistence_delta",
        ) < 0:
            raise ValueError("identity_fission_persistence_delta must be non-negative")
        _require_bool(self.separable_conductance_geometry, field_name="separable_conductance_geometry")

    def to_mapping(self) -> Mapping[str, Any]:
        payload = self._base_mapping(self.construct_kind)
        payload.update(
            {
                "module_region_id": self.module_region_id,
                "sink_region_a": self.sink_region_a,
                "sink_region_b": self.sink_region_b,
                "identity_fission_min_basin_mass": self.identity_fission_min_basin_mass,
                "identity_fission_persistence_delta": self.identity_fission_persistence_delta,
                "separable_conductance_geometry": self.separable_conductance_geometry,
            }
        )
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9PostExpansionFissionGeometry:
        mapping = _require_mapping(value, field_name="post_expansion_fission_geometry")
        return cls(
            construct_id=_require_string(mapping.get("construct_id"), field_name="construct_id"),
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            executable=_require_bool(mapping.get("executable", True), field_name="executable"),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            module_region_id=_require_string(mapping.get("module_region_id"), field_name="module_region_id"),
            sink_region_a=_require_string(mapping.get("sink_region_a"), field_name="sink_region_a"),
            sink_region_b=_require_string(mapping.get("sink_region_b"), field_name="sink_region_b"),
            identity_fission_min_basin_mass=_require_finite_float(
                mapping.get("identity_fission_min_basin_mass"),
                field_name="identity_fission_min_basin_mass",
            ),
            identity_fission_persistence_delta=_require_int(
                mapping.get("identity_fission_persistence_delta"),
                field_name="identity_fission_persistence_delta",
            ),
            separable_conductance_geometry=_require_bool(
                mapping.get("separable_conductance_geometry", True),
                field_name="separable_conductance_geometry",
            ),
        )


GRCL9SourceConstruct = (
    GRCL9SparkCandidateRegion
    | GRCL9ColumnProxyProfile
    | GRCL9InstabilityProfile
    | GRCL9ExpansionRefinementRegion
    | GRCL9GrowthLocus
    | GRCL9PostExpansionFissionGeometry
)

_CONSTRUCT_BY_KIND = {
    GRCL9SparkCandidateRegion.construct_kind: GRCL9SparkCandidateRegion,
    GRCL9ColumnProxyProfile.construct_kind: GRCL9ColumnProxyProfile,
    GRCL9InstabilityProfile.construct_kind: GRCL9InstabilityProfile,
    GRCL9ExpansionRefinementRegion.construct_kind: GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus.construct_kind: GRCL9GrowthLocus,
    GRCL9PostExpansionFissionGeometry.construct_kind: GRCL9PostExpansionFissionGeometry,
}


def grcl9_source_construct_from_mapping(value: Mapping[str, Any]) -> GRCL9SourceConstruct:
    """Parse a source construct from its mapping representation."""

    mapping = _require_mapping(value, field_name="source_construct")
    construct_kind = _require_string(mapping.get("construct_kind"), field_name="construct_kind")
    parser = _CONSTRUCT_BY_KIND.get(construct_kind)
    if parser is None:
        raise ValueError(f"unsupported GRCL-9 source construct kind {construct_kind!r}")
    return parser.from_mapping(mapping)


@dataclass(frozen=True)
class GRCL9SourceDocument:
    """One GRCL-9 source fixture document."""

    fixture_name: str
    constructs: tuple[GRCL9SourceConstruct, ...]
    manifest_entry_id: str
    source_schema_version: str = GRCL9_SOURCE_SCHEMA_VERSION
    expected_selector_ids: tuple[str, ...] = ()
    bridge_policy: GRCL9BridgePolicy = GRCL9BridgePolicy()
    budget_policy: GRCL9BudgetPolicy = GRCL9BudgetPolicy()
    provenance_policy: GRCL9ProvenancePolicy = GRCL9ProvenancePolicy()
    expected_telemetry: tuple[GRCL9TelemetryExpectation, ...] = ()
    non_claims: tuple[str, ...] = GRCL9_BASE_NON_CLAIMS
    compiled_source_provenance: Mapping[str, Any] | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.source_schema_version != GRCL9_SOURCE_SCHEMA_VERSION:
            raise ValueError(f"source_schema_version must be {GRCL9_SOURCE_SCHEMA_VERSION!r}")
        _validate_token(self.fixture_name, field_name="fixture_name")
        _validate_token(self.manifest_entry_id, field_name="manifest_entry_id")
        for selector_id in self.expected_selector_ids:
            _validate_token(selector_id, field_name="expected_selector_ids[]")
        if not self.constructs:
            raise ValueError("constructs must not be empty")
        construct_ids = [item.construct_id for item in self.constructs]
        if len(construct_ids) != len(set(construct_ids)):
            raise ValueError("construct_id values must be unique")
        motif_ids = [item.motif_id for item in self.constructs]
        if any(not motif_id for motif_id in motif_ids):
            raise ValueError("motif_id values must be non-empty")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")
        _require_mapping(
            self.compiled_source_provenance or {},
            field_name="compiled_source_provenance",
        )
        _validate_no_forbidden_runtime_fields(self.notes, field_name="notes")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "source_schema_version": self.source_schema_version,
            "fixture_name": self.fixture_name,
            "manifest_entry_id": self.manifest_entry_id,
            "expected_selector_ids": list(self.expected_selector_ids),
            "bridge_policy": self.bridge_policy.to_mapping(),
            "budget_policy": self.budget_policy.to_mapping(),
            "provenance_policy": self.provenance_policy.to_mapping(),
            "constructs": [item.to_mapping() for item in self.constructs],
            "expected_telemetry": [item.to_mapping() for item in self.expected_telemetry],
            "non_claims": list(self.non_claims),
            "compiled_source_provenance": _json_safe(self.compiled_source_provenance or {}),
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9SourceDocument:
        mapping = _require_mapping(value, field_name="source_document")
        return cls(
            source_schema_version=_require_string(
                mapping.get("source_schema_version", GRCL9_SOURCE_SCHEMA_VERSION),
                field_name="source_schema_version",
            ),
            fixture_name=_require_string(mapping.get("fixture_name"), field_name="fixture_name"),
            manifest_entry_id=_require_string(mapping.get("manifest_entry_id"), field_name="manifest_entry_id"),
            expected_selector_ids=_string_tuple(
                mapping.get("expected_selector_ids", ()),
                field_name="expected_selector_ids",
            ),
            bridge_policy=GRCL9BridgePolicy.from_mapping(mapping.get("bridge_policy", {})),
            budget_policy=GRCL9BudgetPolicy.from_mapping(mapping.get("budget_policy", {})),
            provenance_policy=GRCL9ProvenancePolicy.from_mapping(
                mapping.get("provenance_policy", {})
            ),
            constructs=tuple(
                grcl9_source_construct_from_mapping(item)
                for item in _require_sequence(mapping.get("constructs", ()), field_name="constructs")
            ),
            expected_telemetry=tuple(
                GRCL9TelemetryExpectation.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("expected_telemetry", ()),
                    field_name="expected_telemetry",
                )
            ),
            non_claims=_string_tuple(mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS), field_name="non_claims"),
            compiled_source_provenance=dict(
                _require_mapping(
                    mapping.get("compiled_source_provenance", {}),
                    field_name="compiled_source_provenance",
                )
            ),
            notes=str(mapping.get("notes", "")),
        )


def validate_grcl9_paper_facing_growth_semantics(
    document: GRCL9SourceDocument,
) -> Mapping[str, Any]:
    """Validate that executable GRCL-9 growth uses front-capacity semantics.

    Legacy standalone growth loci remain loadable for replaying and debugging
    the old broad-growth behavior, but they are not valid paper-facing GRCL-9
    growth evidence.
    """

    construct_ids = {construct.construct_id for construct in document.constructs}
    growth_records: list[dict[str, Any]] = []
    for construct in document.constructs:
        if not isinstance(construct, GRCL9GrowthLocus) or not construct.executable:
            continue
        if construct.growth_semantics != "front_capacity":
            raise ValueError(
                "standalone executable growth_locus is legacy non-evidence; "
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
                "parent_id": construct.parent_id,
                "inactive_parent_port": construct.inactive_parent_port,
                "front_capacity_source": construct.front_capacity_source,
                "front_source_construct_id": construct.front_source_construct_id,
            }
        )
    return {
        "growth_semantics": "front_capacity" if growth_records else "none",
        "growth_records": growth_records,
    }

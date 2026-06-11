"""Runtime seed model for normalized landscape seeds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


PrimitiveId: TypeAlias = str
ExtensionMap: TypeAlias = dict[str, Any]

PRIMITIVE_BASIN = "basin"
PRIMITIVE_PLATEAU = "plateau"
PRIMITIVE_RIDGE = "ridge"
PRIMITIVE_VALLEY = "valley"
PRIMITIVE_JUNCTION = "junction"
PRIMITIVE_SADDLE = "saddle"

LANDSCAPE_PRIMITIVE_TYPES: tuple[str, ...] = (
    PRIMITIVE_BASIN,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_RIDGE,
    PRIMITIVE_VALLEY,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_SADDLE,
)

TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION = "lossless_source_normalization"
TRANSLATION_MODE_SEMANTIC_ENRICHMENT = "semantic_enrichment"

TRANSLATION_MODES: tuple[str, ...] = (
    TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
    TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
)


@dataclass
class SeedDocumentMeta:
    """Document-level metadata and provenance for one normalized landscape seed."""

    name: str
    source_kind: str
    source_reference: str | None = None
    source_schema_version: str | None = None
    source_domain: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    translator_name: str | None = None
    translator_version: str | None = None
    translation_mode: str | None = None
    translation_notes: list[str] = field(default_factory=list)


@dataclass
class SeedPotential:
    """Potential-family selection attached to a normalized seed."""

    type: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class SeedConstitutiveProfile:
    """Constitutive coefficients and potential profile for one seed."""

    lambda_c: float
    xi_c: float
    zeta_c: float
    kappa_c: float
    dt: float
    potential: SeedPotential
    budget_b: float | None = None
    notes: str | None = None
    source_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class SeedGeometryHints:
    """Document-wide source-chart hints preserved from source landscapes."""

    source_chart: str | None = None
    periodicity: dict[str, Any] = field(default_factory=dict)
    scale_units: str | None = None
    separation_hints: dict[str, Any] = field(default_factory=dict)
    coordinate_convention: str | None = None


@dataclass
class SeedTransportIntent:
    """Source-declared transport preference carried by the seed layer."""

    id: str
    mode: str
    sources: list[PrimitiveId] = field(default_factory=list)
    targets: list[PrimitiveId] = field(default_factory=list)
    magnitude_hint: float | None = None
    priority: float | None = None
    carrier_id: PrimitiveId | None = None
    direction_hint: str | None = None
    notes: str | None = None


@dataclass
class SeedPrimitive:
    """Base primitive record shared across normalized seed primitive variants."""

    id: PrimitiveId
    type: str
    label: str | None = None
    role: str | None = None
    tags: list[str] = field(default_factory=list)
    hints: dict[str, Any] = field(default_factory=dict)
    extensions: ExtensionMap = field(default_factory=dict)


@dataclass
class BasinSeedPrimitive(SeedPrimitive):
    """Normalized basin primitive."""

    type: str = PRIMITIVE_BASIN
    parent_id: PrimitiveId | None = None
    depth_hint: int | None = None
    coherence_prior: float | None = None
    chart_center_hint: list[float] | None = None
    chart_scale_hint: dict[str, Any] = field(default_factory=dict)
    shape_hint: dict[str, Any] = field(default_factory=dict)
    stability_class: str | None = None
    boundary_ids: list[PrimitiveId] = field(default_factory=list)
    notes: str | None = None


@dataclass
class PlateauSeedPrimitive(SeedPrimitive):
    """Normalized plateau primitive."""

    type: str = PRIMITIVE_PLATEAU
    parent_id: PrimitiveId | None = None
    depth_hint: int | None = None
    coherence_prior: float | None = None
    chart_center_hint: list[float] | None = None
    chart_scale_hint: dict[str, Any] = field(default_factory=dict)
    stability_class: str | None = None
    hosted_primitive_ids: list[PrimitiveId] = field(default_factory=list)
    notes: str | None = None


@dataclass
class RidgeSeedPrimitive(SeedPrimitive):
    """Normalized ridge primitive."""

    type: str = PRIMITIVE_RIDGE
    ridge_kind: str | None = None
    owner_id: PrimitiveId | None = None
    adjacent_ids: list[PrimitiveId] = field(default_factory=list)
    interior_coherence_hint: float | None = None
    exterior_coherence_hint: float | None = None
    thickness_hint: float | None = None
    chart_principal_axis_hint: list[float] | None = None
    anisotropy_hint: dict[str, Any] = field(default_factory=dict)
    permeability_hint: dict[str, Any] = field(default_factory=dict)
    notes: str | None = None


@dataclass
class ValleySeedPrimitive(SeedPrimitive):
    """Normalized valley primitive."""

    type: str = PRIMITIVE_VALLEY
    from_id: PrimitiveId | None = None
    to_id: PrimitiveId | None = None
    path_hint: str | None = None
    width_hint: float | None = None
    coherence_prior: float | None = None
    channel_role: str | None = None
    waypoints: list[list[float]] = field(default_factory=list)
    notes: str | None = None


@dataclass
class JunctionSeedPrimitive(SeedPrimitive):
    """Normalized routing/saddle bridge primitive."""

    type: str = PRIMITIVE_JUNCTION
    host_id: PrimitiveId | None = None
    branch_target_ids: list[PrimitiveId] = field(default_factory=list)
    junction_role: str | None = None
    coherence_prior: float | None = None
    chart_center_hint: list[float] | None = None
    notes: str | None = None


LandscapePrimitive: TypeAlias = (
    BasinSeedPrimitive
    | PlateauSeedPrimitive
    | RidgeSeedPrimitive
    | ValleySeedPrimitive
    | JunctionSeedPrimitive
)


@dataclass
class LandscapeSeed:
    """Top-level normalized landscape seed runtime object."""

    seed_schema: str
    seed_version: str
    meta: SeedDocumentMeta
    constitutive_profile: SeedConstitutiveProfile
    primitives: list[LandscapePrimitive] = field(default_factory=list)
    transport_intent: list[SeedTransportIntent] = field(default_factory=list)
    geometry_hints: SeedGeometryHints | None = None
    extensions: ExtensionMap = field(default_factory=dict)


__all__ = [
    "BasinSeedPrimitive",
    "ExtensionMap",
    "JunctionSeedPrimitive",
    "LANDSCAPE_PRIMITIVE_TYPES",
    "LandscapePrimitive",
    "LandscapeSeed",
    "PlateauSeedPrimitive",
    "PRIMITIVE_BASIN",
    "PRIMITIVE_JUNCTION",
    "PRIMITIVE_PLATEAU",
    "PRIMITIVE_RIDGE",
    "PRIMITIVE_SADDLE",
    "PRIMITIVE_VALLEY",
    "PrimitiveId",
    "RidgeSeedPrimitive",
    "SeedConstitutiveProfile",
    "SeedDocumentMeta",
    "SeedGeometryHints",
    "SeedPotential",
    "SeedPrimitive",
    "SeedTransportIntent",
    "TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION",
    "TRANSLATION_MODE_SEMANTIC_ENRICHMENT",
    "TRANSLATION_MODES",
    "ValleySeedPrimitive",
]

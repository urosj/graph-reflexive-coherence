"""Typed `GRCL-v3` extension parsing and validation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from pygrc.core import InvalidLandscapeSeedError

from ..seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PRIMITIVE_BASIN,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_RIDGE,
    PRIMITIVE_SADDLE,
    PRIMITIVE_VALLEY,
    PlateauSeedPrimitive,
    RidgeSeedPrimitive,
    ValleySeedPrimitive,
)


GRCV3_RICH_V1_CONTRACT_VERSION = "grcv3.rich.v1"
GRCV3_RICH_V2_CONTRACT_VERSION = "grcv3.rich.v2"
GRCV3_RICH_V3_CONTRACT_VERSION = "grcv3.rich.v3"
GRCV3_RICH_V4_CONTRACT_VERSION = "grcv3.rich.v4"

_SUPPORTED_GRCV3_CONTRACT_VERSIONS = {
    GRCV3_RICH_V1_CONTRACT_VERSION,
    GRCV3_RICH_V2_CONTRACT_VERSION,
    GRCV3_RICH_V3_CONTRACT_VERSION,
    GRCV3_RICH_V4_CONTRACT_VERSION,
}

_ALLOWED_TOP_LEVEL_KEYS = {"contract_version", "rich_required"}
_ALLOWED_PRIMITIVE_KEYS_V1 = {"realization", "local_geometry", "interfaces"}
_ALLOWED_PRIMITIVE_KEYS_V2_JUNCTION = {
    "realization",
    "local_geometry",
    "curvature_intent",
    "interfaces",
}
_ALLOWED_PRIMITIVE_KEYS_V2_BASIN = {
    "local_geometry",
    "curvature_intent",
    "interfaces",
}
_ALLOWED_PRIMITIVE_KEYS_V3_JUNCTION = {
    "realization",
    "local_geometry",
    "curvature_intent",
    "interfaces",
    "interior_geometry",
}
_ALLOWED_PRIMITIVE_KEYS_V3_BASIN = {
    "local_geometry",
    "curvature_intent",
    "interfaces",
    "interior_geometry",
    "interior_partition",
    "interior_load_carriers",
}
_ALLOWED_PRIMITIVE_KEYS_V4_JUNCTION = _ALLOWED_PRIMITIVE_KEYS_V3_JUNCTION
_ALLOWED_PRIMITIVE_KEYS_V4_BASIN = {
    "local_geometry",
    "curvature_intent",
    "interfaces",
    "interior_geometry",
    "interior_partition",
    "interior_load_carriers",
    "transfer_mediation",
    "settlement_regime",
}
_ALLOWED_PRIMITIVE_KEYS_V2_RIDGE = {"boundary_geometry", "interfaces"}
_ALLOWED_PRIMITIVE_KEYS_V2_VALLEY = {"channel_geometry", "interfaces"}
_ALLOWED_REALIZATION_KEYS = {
    "kind",
    "support_count",
    "radius_scale",
    "branch_order",
}
_ALLOWED_LOCAL_GEOMETRY_KEYS_V1 = {"frame_mode", "weak_axis_role"}
_ALLOWED_LOCAL_GEOMETRY_KEYS_V2 = {
    "frame_mode",
    "weak_axis_role",
    "axis_roles",
    "symmetry_class",
    "center_role",
}
_ALLOWED_CURVATURE_INTENT_KEYS = {
    "class",
    "stable_axis_roles",
    "weak_axis_role",
    "ordering",
}
_ALLOWED_INTERFACE_KEYS_V1 = {"branch_targets"}
_ALLOWED_INTERFACE_KEYS_V2 = {
    "branch_targets",
    "boundary_roles",
    "channel_roles",
    "preferred_attachment_sites",
}
_ALLOWED_BOUNDARY_GEOMETRY_KEYS = {
    "realization_kind",
    "normal_role",
    "tangent_role",
    "arc_span",
    "support_distribution",
}
_ALLOWED_CHANNEL_GEOMETRY_KEYS = {
    "realization_kind",
    "interior_count",
    "waypoint_policy",
    "entry_role",
    "exit_role",
}
_ALLOWED_INTERIOR_GEOMETRY_KEYS = {
    "probe_mode",
    "support_profile",
    "attachment_isolation",
    "interior_clearance_class",
    "support_connectivity",
    "support_role_groups",
}
_ALLOWED_INTERIOR_PARTITION_KEYS = {
    "partition_mode",
    "load_role_groups",
    "load_transfer_mode",
    "probe_protection_class",
    "attachment_transfer_roles",
}
_ALLOWED_INTERIOR_LOAD_CARRIER_KEYS = {
    "carrier_layout_mode",
    "carrier_anchor_policy",
    "transfer_topology_mode",
    "transfer_role_pairs",
    "carrier_attachment_roles",
}
_ALLOWED_TRANSFER_MEDIATION_KEYS = {
    "mediation_mode",
    "pair_mediation_classes",
    "probe_guard_class",
    "lateral_spill_policy",
    "spill_branch_mode",
    "center_coupling_classes",
    "path_topology",
}
_ALLOWED_SETTLEMENT_REGIME_KEYS = {
    "regime_class",
    "initial_locus_class",
    "split_inheritance_mode",
}
_ALLOWED_REALIZATION_KINDS = {"junction_motif"}
_ALLOWED_FRAME_MODES_V1 = {"branch_ordered"}
_ALLOWED_FRAME_MODES_V2 = {"branch_ordered", "axis_declared"}
_ALLOWED_SYMMETRY_CLASSES = {"radial", "bilateral", "cross", "branch_biased"}
_ALLOWED_CENTER_ROLES = {"anchor", "interior_probe", "routing_core"}
_ALLOWED_CURVATURE_CLASSES = {
    "stable_interior",
    "near_degenerate",
    "boundary_barrier",
    "channel_axis",
}
_ALLOWED_ORDERINGS = {"weak << stable"}
_ALLOWED_BOUNDARY_REALIZATION_KINDS = {
    "support_arc",
    "double_support_arc",
    "barrier_stencil",
}
_ALLOWED_SUPPORT_DISTRIBUTIONS = {"uniform", "end_weighted", "center_weighted"}
_ALLOWED_CHANNEL_REALIZATION_KINDS = {
    "single_channel",
    "double_channel",
    "curved_chain",
}
_ALLOWED_WAYPOINT_POLICIES = {"preserve_all", "midpoint_only", "fit_curvature"}
_ALLOWED_PROBE_MODES = {"interior_candidate", "routing_core", "stable_anchor"}
_ALLOWED_ATTACHMENT_ISOLATIONS = {
    "center_allowed",
    "support_only",
    "interface_roles_only",
}
_ALLOWED_INTERIOR_CLEARANCE_CLASSES = {"shielded", "semi_open", "through_loaded"}
_ALLOWED_SUPPORT_CONNECTIVITIES = {
    "ring",
    "paired_clamps",
    "spindle",
    "branch_only",
}
_ALLOWED_SUPPORT_PROFILE_VALUES = {"tight", "neutral", "loose"}
_ALLOWED_PARTITION_MODES = {
    "two_tier_probe_shell",
    "probe_plus_clamp_shell",
    "single_surface",
}
_ALLOWED_LOAD_TRANSFER_MODES = {
    "support_mediated",
    "clamp_mediated",
    "transport_mediated",
    "direct_open",
}
_ALLOWED_PROBE_PROTECTION_CLASSES = {"shielded", "semi_open", "open"}
_ALLOWED_CARRIER_LAYOUT_MODES = {
    "offset_ring",
    "paired_tracks",
    "staggered_arc",
    "group_midpoints",
}
_ALLOWED_CARRIER_ANCHOR_POLICIES = {
    "role_aligned",
    "between_roles",
    "group_centroid",
}
_ALLOWED_TRANSFER_TOPOLOGY_MODES = {
    "nearest_probe_role",
    "group_bridge",
    "cross_axis_bridge",
    "paired_role_bridge",
}
_ALLOWED_MEDIATION_MODES = {
    "attenuated_pairs",
    "guarded_pairs",
    "confined_pairs",
}
_ALLOWED_PAIR_MEDIATION_CLASSES = {"blocked", "weak", "medium", "strong"}
_ALLOWED_PROBE_GUARD_CLASSES = {"shell_only", "guarded_center", "open_center"}
_ALLOWED_LATERAL_SPILL_POLICIES = {"role_locked", "axis_locked", "open"}
_ALLOWED_SPILL_BRANCH_MODES = {"carrier_branch", "mediated_branch"}
_ALLOWED_PATH_TOPOLOGY_CLASSES = {"direct", "single_intermediate", "fan_in"}
_ALLOWED_SETTLEMENT_REGIME_CLASSES = {
    "carrier_site_regime",
    "path_node_regime",
}
_ALLOWED_SETTLEMENT_INITIAL_LOCUS_CLASSES = {
    "carrier_site",
    "path_node",
}
_ALLOWED_SETTLEMENT_SPLIT_INHERITANCE_MODES = {
    "anchored",
    "split_child_inheriting",
}
_ALLOWED_PRIMITIVE_TYPES_V1 = {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}
_ALLOWED_PRIMITIVE_TYPES_V2 = {
    PRIMITIVE_BASIN,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_SADDLE,
    PRIMITIVE_RIDGE,
    PRIMITIVE_VALLEY,
}


@dataclass(frozen=True)
class GRCV3RichRealization:
    """Typed realization intent for a rich primitive."""

    kind: str
    support_count: int
    radius_scale: float
    branch_order: tuple[str, ...]


@dataclass(frozen=True)
class GRCV3RichLocalGeometry:
    """Typed local-geometry intent."""

    frame_mode: str
    weak_axis_role: str | None = None
    axis_roles: tuple[str, ...] = ()
    symmetry_class: str | None = None
    center_role: str | None = None


@dataclass(frozen=True)
class GRCV3RichCurvatureIntent:
    """Typed qualitative curvature intent."""

    curvature_class: str
    stable_axis_roles: tuple[str, ...] = ()
    weak_axis_role: str | None = None
    ordering: str | None = None


@dataclass(frozen=True)
class GRCV3RichInterfaces:
    """Typed interface-preservation contract."""

    branch_targets: Mapping[str, str] = MappingProxyType({})
    boundary_roles: tuple[str, ...] = ()
    channel_roles: tuple[str, ...] = ()
    preferred_attachment_sites: Mapping[str, str] = MappingProxyType({})


@dataclass(frozen=True)
class GRCV3RichBoundaryGeometry:
    """Typed boundary-support geometry intent."""

    realization_kind: str
    normal_role: str
    tangent_role: str
    arc_span: float | str
    support_distribution: str


@dataclass(frozen=True)
class GRCV3RichChannelGeometry:
    """Typed channel-support geometry intent."""

    realization_kind: str
    interior_count: int
    waypoint_policy: str
    entry_role: str
    exit_role: str


@dataclass(frozen=True)
class GRCV3RichInteriorGeometry:
    """Typed interior-shaping intent for direct `GRCV3` assembly."""

    probe_mode: str
    support_profile: Mapping[str, str] = MappingProxyType({})
    attachment_isolation: str = "support_only"
    interior_clearance_class: str = "shielded"
    support_connectivity: str = "ring"
    support_role_groups: Mapping[str, tuple[str, ...]] = MappingProxyType({})


@dataclass(frozen=True)
class GRCV3RichInteriorPartition:
    """Typed inner-probe versus outer-load partition intent."""

    partition_mode: str
    load_role_groups: Mapping[str, tuple[str, ...]] = MappingProxyType({})
    load_transfer_mode: str = "support_mediated"
    probe_protection_class: str = "shielded"
    attachment_transfer_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class GRCV3RichInteriorLoadCarriers:
    """Typed non-coincident load-carrier placement and transfer intent."""

    carrier_layout_mode: str
    carrier_anchor_policy: str
    transfer_topology_mode: str
    transfer_role_pairs: tuple[tuple[str, str], ...] = ()
    carrier_attachment_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class GRCV3RichTransferMediation:
    """Typed transfer-mediation semantics for explicit carrier/probe pairs."""

    mediation_mode: str
    pair_mediation_classes: tuple[tuple[str, str, str], ...] = ()
    probe_guard_class: str = "guarded_center"
    lateral_spill_policy: str = "axis_locked"
    spill_branch_mode: str = "carrier_branch"
    center_coupling_classes: tuple[tuple[str, str], ...] = ()
    path_topology: tuple[tuple[str, str, str], ...] = ()


@dataclass(frozen=True)
class GRCV3RichSettlementRegime:
    """Typed settlement-regime semantics for operative spark settlement."""

    regime_class: str | None = None
    initial_locus_class: str | None = None
    split_inheritance_mode: str | None = None


@dataclass(frozen=True)
class GRCV3RichPrimitiveExtension:
    """Typed `GRCV3` rich-seed payload for one primitive."""

    primitive_id: str
    realization: GRCV3RichRealization | None = None
    local_geometry: GRCV3RichLocalGeometry | None = None
    curvature_intent: GRCV3RichCurvatureIntent | None = None
    interfaces: GRCV3RichInterfaces | None = None
    boundary_geometry: GRCV3RichBoundaryGeometry | None = None
    channel_geometry: GRCV3RichChannelGeometry | None = None
    interior_geometry: GRCV3RichInteriorGeometry | None = None
    interior_partition: GRCV3RichInteriorPartition | None = None
    interior_load_carriers: GRCV3RichInteriorLoadCarriers | None = None
    transfer_mediation: GRCV3RichTransferMediation | None = None
    settlement_regime: GRCV3RichSettlementRegime | None = None


@dataclass(frozen=True)
class GRCV3RichSeedExtension:
    """Typed top-level `GRCV3` rich-seed contract."""

    contract_version: str
    rich_required: bool
    primitive_extensions: Mapping[str, GRCV3RichPrimitiveExtension]


def _require_mapping(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise InvalidLandscapeSeedError(f"{context} must be a mapping")
    return {str(key): inner for key, inner in value.items()}


def _require_non_empty_string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidLandscapeSeedError(f"{context} must be a non-empty string")
    return value.strip()


def _require_bool(value: object, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise InvalidLandscapeSeedError(f"{context} must be a boolean")
    return value


def _require_positive_int(value: object, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidLandscapeSeedError(f"{context} must be a positive integer")
    if value <= 0:
        raise InvalidLandscapeSeedError(f"{context} must be > 0")
    return int(value)


def _require_positive_float(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(
            f"{context} must be a positive float-compatible number"
        )
    number = float(value)
    if not number > 0.0:
        raise InvalidLandscapeSeedError(f"{context} must be > 0")
    return number


def _require_string_sequence(value: object, *, context: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    items = tuple(
        _require_non_empty_string(item, context=f"{context}[{index}]")
        for index, item in enumerate(value)
    )
    if not items:
        raise InvalidLandscapeSeedError(f"{context} must not be empty")
    if len(set(items)) != len(items):
        raise InvalidLandscapeSeedError(f"{context} must contain unique role labels")
    return items


def _require_arc_span(value: object, *, context: str) -> float | str:
    if isinstance(value, bool):
        raise InvalidLandscapeSeedError(
            f"{context} must be a positive number or non-empty qualitative label"
        )
    if isinstance(value, int | float):
        number = float(value)
        if not number > 0.0:
            raise InvalidLandscapeSeedError(f"{context} must be > 0")
        return number
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise InvalidLandscapeSeedError(
        f"{context} must be a positive number or non-empty qualitative label"
    )


def _freeze_mapping(value: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType({str(key): str(value[key]) for key in sorted(value)})


def _freeze_group_mapping(value: Mapping[str, tuple[str, ...]]) -> Mapping[str, tuple[str, ...]]:
    return MappingProxyType(
        {str(key): tuple(value[key]) for key in sorted(value)}
    )


def _reject_unknown_keys(
    mapping: Mapping[str, Any],
    *,
    allowed: set[str],
    context: str,
    contract_version: str,
) -> None:
    unknown_keys = sorted(str(key) for key in mapping.keys() if str(key) not in allowed)
    if unknown_keys:
        raise InvalidLandscapeSeedError(
            f"{context} includes unsupported keys {unknown_keys!r} for the "
            f"{contract_version} contract"
        )


def _primitive_index(seed: LandscapeSeed) -> dict[str, LandscapePrimitive]:
    return {primitive.id: primitive for primitive in seed.primitives}


def _incident_neighbor_ids(seed: LandscapeSeed, primitive_id: str) -> set[str]:
    neighbor_ids: set[str] = set()
    for primitive in seed.primitives:
        if not isinstance(primitive, ValleySeedPrimitive):
            continue
        if primitive.from_id == primitive_id and primitive.to_id is not None:
            neighbor_ids.add(primitive.to_id)
        elif primitive.to_id == primitive_id and primitive.from_id is not None:
            neighbor_ids.add(primitive.from_id)
    neighbor_ids.discard(primitive_id)
    return neighbor_ids


def _role_universe(
    *,
    realization: GRCV3RichRealization | None,
    local_geometry: GRCV3RichLocalGeometry | None,
) -> tuple[str, ...]:
    if local_geometry is not None and local_geometry.axis_roles:
        return local_geometry.axis_roles
    if realization is not None:
        return realization.branch_order
    return ()


def _validate_role_membership(
    role: str,
    *,
    role_universe: tuple[str, ...],
    context: str,
) -> None:
    if role_universe and role not in role_universe:
        raise InvalidLandscapeSeedError(
            f"{context} must be one of {list(role_universe)!r}"
        )


def _parse_branch_targets(
    value: object,
    *,
    primitive_id: str,
    branch_order: tuple[str, ...],
    seed: LandscapeSeed,
    context: str,
) -> Mapping[str, str]:
    raw_mapping = _require_mapping(value, context=context)
    role_keys = tuple(sorted(raw_mapping))
    if set(role_keys) != set(branch_order):
        raise InvalidLandscapeSeedError(
            f"{context} keys must match realization.branch_order for primitive "
            f"{primitive_id!r}"
        )
    primitive_index = _primitive_index(seed)
    target_ids: list[str] = []
    normalized: dict[str, str] = {}
    for role in branch_order:
        target_id = _require_non_empty_string(
            raw_mapping.get(role),
            context=f"{context}.{role}",
        )
        if target_id not in primitive_index:
            raise InvalidLandscapeSeedError(
                f"{context}.{role} refers to unknown primitive {target_id!r}"
            )
        if target_id == primitive_id:
            raise InvalidLandscapeSeedError(
                f"{context}.{role} must not target the owning primitive {primitive_id!r}"
            )
        target_ids.append(target_id)
        normalized[role] = target_id
    if len(set(target_ids)) != len(target_ids):
        raise InvalidLandscapeSeedError(f"{context} target primitive IDs must be unique")
    incident_neighbor_ids = _incident_neighbor_ids(seed, primitive_id)
    if set(target_ids) != incident_neighbor_ids:
        raise InvalidLandscapeSeedError(
            f"{context} must map exactly the incident valley neighbors of "
            f"{primitive_id!r}; expected {sorted(incident_neighbor_ids)!r}. "
            "Boundary/ridge-adjacent shells must be expressed through "
            "boundary_roles/preferred_attachment_sites rather than branch_targets."
        )
    return _freeze_mapping(normalized)


def _parse_realization(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    required: bool,
) -> GRCV3RichRealization | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.realization"
    if value is None:
        if required:
            raise InvalidLandscapeSeedError(f"{context} is required")
        return None
    realization_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        realization_mapping,
        allowed=_ALLOWED_REALIZATION_KEYS,
        context=context,
        contract_version=contract_version,
    )
    kind = _require_non_empty_string(realization_mapping.get("kind"), context=f"{context}.kind")
    if kind not in _ALLOWED_REALIZATION_KINDS:
        raise InvalidLandscapeSeedError(
            f"{context}.kind must be one of {sorted(_ALLOWED_REALIZATION_KINDS)!r}"
        )
    support_count = _require_positive_int(
        realization_mapping.get("support_count"),
        context=f"{context}.support_count",
    )
    radius_scale = _require_positive_float(
        realization_mapping.get("radius_scale"),
        context=f"{context}.radius_scale",
    )
    branch_order = _require_string_sequence(
        realization_mapping.get("branch_order"),
        context=f"{context}.branch_order",
    )
    if support_count != len(branch_order):
        raise InvalidLandscapeSeedError(
            f"{context}.support_count must equal the number of branch-order roles"
        )
    return GRCV3RichRealization(
        kind=kind,
        support_count=support_count,
        radius_scale=radius_scale,
        branch_order=branch_order,
    )


def _parse_local_geometry(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    realization: GRCV3RichRealization | None,
    required: bool,
) -> GRCV3RichLocalGeometry | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.local_geometry"
    if value is None:
        if required:
            raise InvalidLandscapeSeedError(f"{context} is required")
        return None
    local_geometry_mapping = _require_mapping(value, context=context)
    allowed_keys = (
        _ALLOWED_LOCAL_GEOMETRY_KEYS_V1
        if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION
        else _ALLOWED_LOCAL_GEOMETRY_KEYS_V2
    )
    _reject_unknown_keys(
        local_geometry_mapping,
        allowed=allowed_keys,
        context=context,
        contract_version=contract_version,
    )
    frame_mode = _require_non_empty_string(
        local_geometry_mapping.get("frame_mode"),
        context=f"{context}.frame_mode",
    )
    allowed_frame_modes = (
        _ALLOWED_FRAME_MODES_V1
        if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION
        else _ALLOWED_FRAME_MODES_V2
    )
    if frame_mode not in allowed_frame_modes:
        raise InvalidLandscapeSeedError(
            f"{context}.frame_mode must be one of {sorted(allowed_frame_modes)!r}"
        )

    axis_roles: tuple[str, ...] = ()
    symmetry_class: str | None = None
    center_role: str | None = None
    if contract_version in {
        GRCV3_RICH_V2_CONTRACT_VERSION,
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raw_axis_roles = local_geometry_mapping.get("axis_roles")
        if raw_axis_roles is not None:
            axis_roles = _require_string_sequence(
                raw_axis_roles,
                context=f"{context}.axis_roles",
            )
        if frame_mode == "axis_declared" and not axis_roles:
            raise InvalidLandscapeSeedError(
                f"{context}.axis_roles is required when frame_mode='axis_declared'"
            )
        raw_symmetry_class = local_geometry_mapping.get("symmetry_class")
        if raw_symmetry_class is not None:
            symmetry_class = _require_non_empty_string(
                raw_symmetry_class,
                context=f"{context}.symmetry_class",
            )
            if symmetry_class not in _ALLOWED_SYMMETRY_CLASSES:
                raise InvalidLandscapeSeedError(
                    f"{context}.symmetry_class must be one of "
                    f"{sorted(_ALLOWED_SYMMETRY_CLASSES)!r}"
                )
        raw_center_role = local_geometry_mapping.get("center_role")
        if raw_center_role is not None:
            center_role = _require_non_empty_string(
                raw_center_role,
                context=f"{context}.center_role",
            )
            if center_role not in _ALLOWED_CENTER_ROLES:
                raise InvalidLandscapeSeedError(
                    f"{context}.center_role must be one of "
                    f"{sorted(_ALLOWED_CENTER_ROLES)!r}"
                )

    raw_weak_axis_role = local_geometry_mapping.get("weak_axis_role")
    weak_axis_role: str | None
    if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION:
        weak_axis_role = _require_non_empty_string(
            raw_weak_axis_role,
            context=f"{context}.weak_axis_role",
        )
    else:
        weak_axis_role = None
        if raw_weak_axis_role is not None:
            weak_axis_role = _require_non_empty_string(
                raw_weak_axis_role,
                context=f"{context}.weak_axis_role",
            )

    role_universe = axis_roles or (realization.branch_order if realization is not None else ())
    if weak_axis_role is not None:
        _validate_role_membership(
            weak_axis_role,
            role_universe=role_universe,
            context=f"{context}.weak_axis_role",
        )

    return GRCV3RichLocalGeometry(
        frame_mode=frame_mode,
        weak_axis_role=weak_axis_role,
        axis_roles=axis_roles,
        symmetry_class=symmetry_class,
        center_role=center_role,
    )


def _parse_curvature_intent(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    realization: GRCV3RichRealization | None,
    local_geometry: GRCV3RichLocalGeometry | None,
) -> GRCV3RichCurvatureIntent | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.curvature_intent"
    if value is None:
        return None
    if contract_version not in {
        GRCV3_RICH_V2_CONTRACT_VERSION,
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    curvature_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        curvature_mapping,
        allowed=_ALLOWED_CURVATURE_INTENT_KEYS,
        context=context,
        contract_version=contract_version,
    )
    curvature_class = _require_non_empty_string(
        curvature_mapping.get("class"),
        context=f"{context}.class",
    )
    if curvature_class not in _ALLOWED_CURVATURE_CLASSES:
        raise InvalidLandscapeSeedError(
            f"{context}.class must be one of {sorted(_ALLOWED_CURVATURE_CLASSES)!r}"
        )
    stable_axis_roles: tuple[str, ...] = ()
    raw_stable_axis_roles = curvature_mapping.get("stable_axis_roles")
    if raw_stable_axis_roles is not None:
        stable_axis_roles = _require_string_sequence(
            raw_stable_axis_roles,
            context=f"{context}.stable_axis_roles",
        )
    weak_axis_role: str | None = None
    raw_weak_axis_role = curvature_mapping.get("weak_axis_role")
    if raw_weak_axis_role is not None:
        weak_axis_role = _require_non_empty_string(
            raw_weak_axis_role,
            context=f"{context}.weak_axis_role",
        )
    ordering: str | None = None
    raw_ordering = curvature_mapping.get("ordering")
    if raw_ordering is not None:
        ordering = _require_non_empty_string(
            raw_ordering,
            context=f"{context}.ordering",
        )
        if ordering not in _ALLOWED_ORDERINGS:
            raise InvalidLandscapeSeedError(
                f"{context}.ordering must be one of {sorted(_ALLOWED_ORDERINGS)!r}"
            )

    role_universe = _role_universe(realization=realization, local_geometry=local_geometry)
    for index, role in enumerate(stable_axis_roles):
        _validate_role_membership(
            role,
            role_universe=role_universe,
            context=f"{context}.stable_axis_roles[{index}]",
        )
    if weak_axis_role is not None:
        _validate_role_membership(
            weak_axis_role,
            role_universe=role_universe,
            context=f"{context}.weak_axis_role",
        )
        if weak_axis_role in stable_axis_roles:
            raise InvalidLandscapeSeedError(
                f"{context}.weak_axis_role must not also appear in stable_axis_roles"
            )

    return GRCV3RichCurvatureIntent(
        curvature_class=curvature_class,
        stable_axis_roles=stable_axis_roles,
        weak_axis_role=weak_axis_role,
        ordering=ordering,
    )


def _parse_preferred_attachment_sites(
    value: object,
    *,
    context: str,
    role_labels: set[str],
    local_roles: tuple[str, ...],
) -> Mapping[str, str]:
    if not role_labels:
        raise InvalidLandscapeSeedError(
            f"{context} requires boundary_roles and/or channel_roles to be declared"
        )
    if not local_roles:
        raise InvalidLandscapeSeedError(
            f"{context} requires local roles to be declared before attachment sites can be mapped"
        )
    raw_mapping = _require_mapping(value, context=context)
    normalized: dict[str, str] = {}
    for label, local_role in raw_mapping.items():
        label_name = _require_non_empty_string(label, context=f"{context}.<label>")
        if label_name not in role_labels:
            raise InvalidLandscapeSeedError(
                f"{context} key {label_name!r} must be one of {sorted(role_labels)!r}"
            )
        local_role_name = _require_non_empty_string(
            local_role,
            context=f"{context}.{label_name}",
        )
        _validate_role_membership(
            local_role_name,
            role_universe=local_roles,
            context=f"{context}.{label_name}",
        )
        normalized[label_name] = local_role_name
    return _freeze_mapping(normalized)


def _parse_interfaces(
    value: object,
    *,
    primitive: LandscapePrimitive,
    seed: LandscapeSeed,
    contract_version: str,
    realization: GRCV3RichRealization | None,
    local_geometry: GRCV3RichLocalGeometry | None,
    boundary_geometry: GRCV3RichBoundaryGeometry | None,
    channel_geometry: GRCV3RichChannelGeometry | None,
    required: bool,
) -> GRCV3RichInterfaces | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.interfaces"
    if value is None:
        if required:
            raise InvalidLandscapeSeedError(f"{context} is required")
        return None
    interfaces_mapping = _require_mapping(value, context=context)
    allowed_keys = (
        _ALLOWED_INTERFACE_KEYS_V1
        if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION
        else _ALLOWED_INTERFACE_KEYS_V2
    )
    _reject_unknown_keys(
        interfaces_mapping,
        allowed=allowed_keys,
        context=context,
        contract_version=contract_version,
    )

    branch_targets = MappingProxyType({})
    branch_order = realization.branch_order if realization is not None else ()
    branch_targets_required = (
        isinstance(primitive, JunctionSeedPrimitive) and realization is not None
    )
    raw_branch_targets = interfaces_mapping.get("branch_targets")
    if raw_branch_targets is not None:
        if not branch_order:
            raise InvalidLandscapeSeedError(
                f"{context}.branch_targets requires realization.branch_order"
            )
        branch_targets = _parse_branch_targets(
            raw_branch_targets,
            primitive_id=primitive.id,
            branch_order=branch_order,
            seed=seed,
            context=f"{context}.branch_targets",
        )
    elif branch_targets_required:
        raise InvalidLandscapeSeedError(f"{context}.branch_targets is required")

    if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION:
        return GRCV3RichInterfaces(branch_targets=branch_targets)

    boundary_roles: tuple[str, ...] = ()
    channel_roles: tuple[str, ...] = ()
    raw_boundary_roles = interfaces_mapping.get("boundary_roles")
    if raw_boundary_roles is not None:
        boundary_roles = _require_string_sequence(
            raw_boundary_roles,
            context=f"{context}.boundary_roles",
        )
    raw_channel_roles = interfaces_mapping.get("channel_roles")
    if raw_channel_roles is not None:
        channel_roles = _require_string_sequence(
            raw_channel_roles,
            context=f"{context}.channel_roles",
        )

    preferred_attachment_sites = MappingProxyType({})
    raw_preferred_attachment_sites = interfaces_mapping.get("preferred_attachment_sites")
    if raw_preferred_attachment_sites is not None:
        local_roles = _role_universe(realization=realization, local_geometry=local_geometry)
        if not local_roles and boundary_geometry is not None:
            local_roles = (
                boundary_geometry.normal_role,
                boundary_geometry.tangent_role,
            )
        if not local_roles and channel_geometry is not None:
            local_roles = (
                channel_geometry.entry_role,
                channel_geometry.exit_role,
            )
        preferred_attachment_sites = _parse_preferred_attachment_sites(
            raw_preferred_attachment_sites,
            context=f"{context}.preferred_attachment_sites",
            role_labels=set(boundary_roles) | set(channel_roles),
            local_roles=local_roles,
        )

    return GRCV3RichInterfaces(
        branch_targets=branch_targets,
        boundary_roles=boundary_roles,
        channel_roles=channel_roles,
        preferred_attachment_sites=preferred_attachment_sites,
    )


def _parse_boundary_geometry(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    required: bool,
) -> GRCV3RichBoundaryGeometry | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.boundary_geometry"
    if value is None:
        if required:
            raise InvalidLandscapeSeedError(f"{context} is required")
        return None
    if contract_version not in {
        GRCV3_RICH_V2_CONTRACT_VERSION,
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    boundary_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        boundary_mapping,
        allowed=_ALLOWED_BOUNDARY_GEOMETRY_KEYS,
        context=context,
        contract_version=contract_version,
    )
    realization_kind = _require_non_empty_string(
        boundary_mapping.get("realization_kind"),
        context=f"{context}.realization_kind",
    )
    if realization_kind not in _ALLOWED_BOUNDARY_REALIZATION_KINDS:
        raise InvalidLandscapeSeedError(
            f"{context}.realization_kind must be one of "
            f"{sorted(_ALLOWED_BOUNDARY_REALIZATION_KINDS)!r}"
        )
    normal_role = _require_non_empty_string(
        boundary_mapping.get("normal_role"),
        context=f"{context}.normal_role",
    )
    tangent_role = _require_non_empty_string(
        boundary_mapping.get("tangent_role"),
        context=f"{context}.tangent_role",
    )
    if normal_role == tangent_role:
        raise InvalidLandscapeSeedError(
            f"{context}.normal_role and tangent_role must differ"
        )
    arc_span = _require_arc_span(boundary_mapping.get("arc_span"), context=f"{context}.arc_span")
    support_distribution = _require_non_empty_string(
        boundary_mapping.get("support_distribution"),
        context=f"{context}.support_distribution",
    )
    if support_distribution not in _ALLOWED_SUPPORT_DISTRIBUTIONS:
        raise InvalidLandscapeSeedError(
            f"{context}.support_distribution must be one of "
            f"{sorted(_ALLOWED_SUPPORT_DISTRIBUTIONS)!r}"
        )
    return GRCV3RichBoundaryGeometry(
        realization_kind=realization_kind,
        normal_role=normal_role,
        tangent_role=tangent_role,
        arc_span=arc_span,
        support_distribution=support_distribution,
    )


def _parse_channel_geometry(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    required: bool,
) -> GRCV3RichChannelGeometry | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.channel_geometry"
    if value is None:
        if required:
            raise InvalidLandscapeSeedError(f"{context} is required")
        return None
    if contract_version not in {
        GRCV3_RICH_V2_CONTRACT_VERSION,
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    channel_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        channel_mapping,
        allowed=_ALLOWED_CHANNEL_GEOMETRY_KEYS,
        context=context,
        contract_version=contract_version,
    )
    realization_kind = _require_non_empty_string(
        channel_mapping.get("realization_kind"),
        context=f"{context}.realization_kind",
    )
    if realization_kind not in _ALLOWED_CHANNEL_REALIZATION_KINDS:
        raise InvalidLandscapeSeedError(
            f"{context}.realization_kind must be one of "
            f"{sorted(_ALLOWED_CHANNEL_REALIZATION_KINDS)!r}"
        )
    interior_count = _require_positive_int(
        channel_mapping.get("interior_count"),
        context=f"{context}.interior_count",
    )
    waypoint_policy = _require_non_empty_string(
        channel_mapping.get("waypoint_policy"),
        context=f"{context}.waypoint_policy",
    )
    if waypoint_policy not in _ALLOWED_WAYPOINT_POLICIES:
        raise InvalidLandscapeSeedError(
            f"{context}.waypoint_policy must be one of "
            f"{sorted(_ALLOWED_WAYPOINT_POLICIES)!r}"
        )
    entry_role = _require_non_empty_string(
        channel_mapping.get("entry_role"),
        context=f"{context}.entry_role",
    )
    exit_role = _require_non_empty_string(
        channel_mapping.get("exit_role"),
        context=f"{context}.exit_role",
    )
    return GRCV3RichChannelGeometry(
        realization_kind=realization_kind,
        interior_count=interior_count,
        waypoint_policy=waypoint_policy,
        entry_role=entry_role,
        exit_role=exit_role,
    )


def _parse_support_profile(
    value: object,
    *,
    context: str,
    role_universe: tuple[str, ...],
) -> Mapping[str, str]:
    raw_mapping = _require_mapping(value, context=context)
    if set(raw_mapping) != set(role_universe):
        raise InvalidLandscapeSeedError(
            f"{context} keys must match the declared local-role universe "
            f"{list(role_universe)!r}"
        )
    normalized: dict[str, str] = {}
    for role in role_universe:
        profile_value = _require_non_empty_string(
            raw_mapping.get(role),
            context=f"{context}.{role}",
        )
        if profile_value not in _ALLOWED_SUPPORT_PROFILE_VALUES:
            raise InvalidLandscapeSeedError(
                f"{context}.{role} must be one of "
                f"{sorted(_ALLOWED_SUPPORT_PROFILE_VALUES)!r}"
            )
        normalized[role] = profile_value
    return _freeze_mapping(normalized)


def _parse_support_role_groups(
    value: object,
    *,
    context: str,
    role_universe: tuple[str, ...],
) -> Mapping[str, tuple[str, ...]]:
    raw_mapping = _require_mapping(value, context=context)
    if not raw_mapping:
        raise InvalidLandscapeSeedError(f"{context} must not be empty")
    normalized: dict[str, tuple[str, ...]] = {}
    assigned_roles: dict[str, str] = {}
    for group_name in sorted(raw_mapping):
        normalized_group_name = _require_non_empty_string(
            group_name,
            context=f"{context}.<group>",
        )
        if normalized_group_name in normalized:
            raise InvalidLandscapeSeedError(f"{context} group names must be unique")
        group_roles = _require_string_sequence(
            raw_mapping[group_name],
            context=f"{context}.{normalized_group_name}",
        )
        for role in group_roles:
            _validate_role_membership(
                role,
                role_universe=role_universe,
                context=f"{context}.{normalized_group_name}",
            )
            previous_group = assigned_roles.get(role)
            if previous_group is not None:
                raise InvalidLandscapeSeedError(
                    f"{context} role {role!r} must not appear in both "
                    f"{previous_group!r} and {normalized_group_name!r}"
                )
            assigned_roles[role] = normalized_group_name
        normalized[normalized_group_name] = group_roles
    if set(assigned_roles) != set(role_universe):
        raise InvalidLandscapeSeedError(
            f"{context} must cover the full declared local-role universe "
            f"{list(role_universe)!r}"
        )
    return _freeze_group_mapping(normalized)


def _parse_interior_geometry(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    realization: GRCV3RichRealization | None,
    local_geometry: GRCV3RichLocalGeometry | None,
    interfaces: GRCV3RichInterfaces | None,
) -> GRCV3RichInteriorGeometry | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.interior_geometry"
    if value is None:
        return None
    if contract_version not in {
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    role_universe = _role_universe(realization=realization, local_geometry=local_geometry)
    if not role_universe:
        raise InvalidLandscapeSeedError(
            f"{context} requires declared local roles before interior geometry can be used"
        )
    interior_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        interior_mapping,
        allowed=_ALLOWED_INTERIOR_GEOMETRY_KEYS,
        context=context,
        contract_version=contract_version,
    )
    probe_mode = _require_non_empty_string(
        interior_mapping.get("probe_mode"),
        context=f"{context}.probe_mode",
    )
    if probe_mode not in _ALLOWED_PROBE_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.probe_mode must be one of {sorted(_ALLOWED_PROBE_MODES)!r}"
        )
    support_profile = _parse_support_profile(
        interior_mapping.get("support_profile"),
        context=f"{context}.support_profile",
        role_universe=role_universe,
    )
    attachment_isolation = _require_non_empty_string(
        interior_mapping.get("attachment_isolation"),
        context=f"{context}.attachment_isolation",
    )
    if attachment_isolation not in _ALLOWED_ATTACHMENT_ISOLATIONS:
        raise InvalidLandscapeSeedError(
            f"{context}.attachment_isolation must be one of "
            f"{sorted(_ALLOWED_ATTACHMENT_ISOLATIONS)!r}"
        )
    interior_clearance_class = _require_non_empty_string(
        interior_mapping.get("interior_clearance_class"),
        context=f"{context}.interior_clearance_class",
    )
    if interior_clearance_class not in _ALLOWED_INTERIOR_CLEARANCE_CLASSES:
        raise InvalidLandscapeSeedError(
            f"{context}.interior_clearance_class must be one of "
            f"{sorted(_ALLOWED_INTERIOR_CLEARANCE_CLASSES)!r}"
        )
    support_connectivity = _require_non_empty_string(
        interior_mapping.get("support_connectivity"),
        context=f"{context}.support_connectivity",
    )
    if support_connectivity not in _ALLOWED_SUPPORT_CONNECTIVITIES:
        raise InvalidLandscapeSeedError(
            f"{context}.support_connectivity must be one of "
            f"{sorted(_ALLOWED_SUPPORT_CONNECTIVITIES)!r}"
        )
    support_role_groups = _parse_support_role_groups(
        interior_mapping.get("support_role_groups"),
        context=f"{context}.support_role_groups",
        role_universe=role_universe,
    )

    expected_center_roles = {
        "interior_candidate": "interior_probe",
        "routing_core": "routing_core",
        "stable_anchor": "anchor",
    }
    expected_center_role = expected_center_roles[probe_mode]
    actual_center_role = local_geometry.center_role if local_geometry is not None else None
    if actual_center_role != expected_center_role:
        raise InvalidLandscapeSeedError(
            f"{context}.probe_mode={probe_mode!r} requires "
            f"local_geometry.center_role={expected_center_role!r}"
        )
    if (
        support_connectivity == "branch_only"
        and not isinstance(primitive, JunctionSeedPrimitive)
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.support_connectivity='branch_only' is only valid for "
            "junction/saddle primitives"
        )
    if attachment_isolation == "interface_roles_only":
        if interfaces is None or (
            not interfaces.branch_targets
            and not interfaces.boundary_roles
            and not interfaces.channel_roles
        ):
            raise InvalidLandscapeSeedError(
                f"{context}.attachment_isolation='interface_roles_only' requires "
                "declared interfaces"
            )

    return GRCV3RichInteriorGeometry(
        probe_mode=probe_mode,
        support_profile=support_profile,
        attachment_isolation=attachment_isolation,
        interior_clearance_class=interior_clearance_class,
        support_connectivity=support_connectivity,
        support_role_groups=support_role_groups,
    )


def _parse_interior_partition(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    local_geometry: GRCV3RichLocalGeometry | None,
    interfaces: GRCV3RichInterfaces | None,
    interior_geometry: GRCV3RichInteriorGeometry | None,
) -> GRCV3RichInteriorPartition | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.interior_partition"
    if value is None:
        return None
    if contract_version not in {
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    if not isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
        raise InvalidLandscapeSeedError(
            f"{context} is only supported for basin/plateau primitives in the "
            f"{contract_version} contract"
        )
    if local_geometry is None or local_geometry.center_role != "interior_probe":
        raise InvalidLandscapeSeedError(
            f"{context} requires local_geometry.center_role='interior_probe'"
        )
    if interior_geometry is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires interior_geometry to be declared first"
        )
    role_universe = _role_universe(realization=None, local_geometry=local_geometry)
    if not role_universe:
        raise InvalidLandscapeSeedError(
            f"{context} requires declared local roles before partition semantics can be used"
        )
    partition_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        partition_mapping,
        allowed=_ALLOWED_INTERIOR_PARTITION_KEYS,
        context=context,
        contract_version=contract_version,
    )
    partition_mode = _require_non_empty_string(
        partition_mapping.get("partition_mode"),
        context=f"{context}.partition_mode",
    )
    if partition_mode not in _ALLOWED_PARTITION_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.partition_mode must be one of "
            f"{sorted(_ALLOWED_PARTITION_MODES)!r}"
        )
    load_role_groups = _parse_support_role_groups(
        partition_mapping.get("load_role_groups"),
        context=f"{context}.load_role_groups",
        role_universe=role_universe,
    )
    load_roles = {
        role
        for group_roles in load_role_groups.values()
        for role in group_roles
    }
    load_transfer_mode = _require_non_empty_string(
        partition_mapping.get("load_transfer_mode"),
        context=f"{context}.load_transfer_mode",
    )
    if load_transfer_mode not in _ALLOWED_LOAD_TRANSFER_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.load_transfer_mode must be one of "
            f"{sorted(_ALLOWED_LOAD_TRANSFER_MODES)!r}"
        )
    probe_protection_class = _require_non_empty_string(
        partition_mapping.get("probe_protection_class"),
        context=f"{context}.probe_protection_class",
    )
    if probe_protection_class not in _ALLOWED_PROBE_PROTECTION_CLASSES:
        raise InvalidLandscapeSeedError(
            f"{context}.probe_protection_class must be one of "
            f"{sorted(_ALLOWED_PROBE_PROTECTION_CLASSES)!r}"
        )
    attachment_transfer_roles = _require_string_sequence(
        partition_mapping.get("attachment_transfer_roles"),
        context=f"{context}.attachment_transfer_roles",
    )
    for index, role in enumerate(attachment_transfer_roles):
        _validate_role_membership(
            role,
            role_universe=role_universe,
            context=f"{context}.attachment_transfer_roles[{index}]",
        )
        if role not in load_roles:
            raise InvalidLandscapeSeedError(
                f"{context}.attachment_transfer_roles[{index}] must belong to "
                "the declared outer load-role groups"
            )

    if partition_mode == "single_surface" and probe_protection_class != "open":
        raise InvalidLandscapeSeedError(
            f"{context}.partition_mode='single_surface' requires "
            "probe_protection_class='open'"
        )
    if partition_mode == "single_surface" and load_transfer_mode != "direct_open":
        raise InvalidLandscapeSeedError(
            f"{context}.partition_mode='single_surface' requires "
            "load_transfer_mode='direct_open'"
        )
    if probe_protection_class == "shielded" and load_transfer_mode == "direct_open":
        raise InvalidLandscapeSeedError(
            f"{context}.probe_protection_class='shielded' is incompatible with "
            "load_transfer_mode='direct_open'"
        )
    if (
        interfaces is not None
        and interfaces.preferred_attachment_sites
        and not set(attachment_transfer_roles).intersection(load_roles)
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.attachment_transfer_roles must intersect the declared "
            "load-bearing roles"
        )

    return GRCV3RichInteriorPartition(
        partition_mode=partition_mode,
        load_role_groups=load_role_groups,
        load_transfer_mode=load_transfer_mode,
        probe_protection_class=probe_protection_class,
        attachment_transfer_roles=attachment_transfer_roles,
    )


def _parse_transfer_role_pairs(
    value: object,
    *,
    context: str,
    load_roles: set[str],
    role_universe: tuple[str, ...],
) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    if not value:
        raise InvalidLandscapeSeedError(f"{context} must not be empty")
    pairs: list[tuple[str, str]] = []
    seen_load_roles: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(value):
        pair_context = f"{context}[{index}]"
        if not isinstance(item, list) or len(item) != 2:
            raise InvalidLandscapeSeedError(
                f"{pair_context} must be a two-item [carrier_role, probe_role] list"
            )
        carrier_role = _require_non_empty_string(
            item[0],
            context=f"{pair_context}[0]",
        )
        probe_role = _require_non_empty_string(
            item[1],
            context=f"{pair_context}[1]",
        )
        if carrier_role not in load_roles:
            raise InvalidLandscapeSeedError(
                f"{pair_context}[0] must belong to the declared outer load-role universe"
            )
        _validate_role_membership(
            probe_role,
            role_universe=role_universe,
            context=f"{pair_context}[1]",
        )
        if carrier_role in seen_load_roles:
            raise InvalidLandscapeSeedError(
                f"{context} carrier role {carrier_role!r} must not appear more than once"
            )
        pair = (carrier_role, probe_role)
        if pair in seen_pairs:
            raise InvalidLandscapeSeedError(f"{context} must contain unique role pairs")
        seen_load_roles.add(carrier_role)
        seen_pairs.add(pair)
        pairs.append(pair)
    return tuple(pairs)


def _parse_interior_load_carriers(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    local_geometry: GRCV3RichLocalGeometry | None,
    interfaces: GRCV3RichInterfaces | None,
    interior_geometry: GRCV3RichInteriorGeometry | None,
    interior_partition: GRCV3RichInteriorPartition | None,
) -> GRCV3RichInteriorLoadCarriers | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.interior_load_carriers"
    if value is None:
        return None
    if contract_version not in {
        GRCV3_RICH_V3_CONTRACT_VERSION,
        GRCV3_RICH_V4_CONTRACT_VERSION,
    }:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    if not isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
        raise InvalidLandscapeSeedError(
            f"{context} is only supported for basin/plateau primitives in the "
            f"{contract_version} contract"
        )
    if local_geometry is None or local_geometry.center_role != "interior_probe":
        raise InvalidLandscapeSeedError(
            f"{context} requires local_geometry.center_role='interior_probe'"
        )
    if interior_geometry is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires interior_geometry to be declared first"
        )
    if interior_partition is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires interior_partition to be declared first"
        )
    role_universe = _role_universe(realization=None, local_geometry=local_geometry)
    if not role_universe:
        raise InvalidLandscapeSeedError(
            f"{context} requires declared local roles before load-carrier semantics can be used"
        )
    load_roles = {
        role
        for group_roles in interior_partition.load_role_groups.values()
        for role in group_roles
    }
    carrier_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        carrier_mapping,
        allowed=_ALLOWED_INTERIOR_LOAD_CARRIER_KEYS,
        context=context,
        contract_version=contract_version,
    )
    carrier_layout_mode = _require_non_empty_string(
        carrier_mapping.get("carrier_layout_mode"),
        context=f"{context}.carrier_layout_mode",
    )
    if carrier_layout_mode not in _ALLOWED_CARRIER_LAYOUT_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.carrier_layout_mode must be one of "
            f"{sorted(_ALLOWED_CARRIER_LAYOUT_MODES)!r}"
        )
    carrier_anchor_policy = _require_non_empty_string(
        carrier_mapping.get("carrier_anchor_policy"),
        context=f"{context}.carrier_anchor_policy",
    )
    if carrier_anchor_policy not in _ALLOWED_CARRIER_ANCHOR_POLICIES:
        raise InvalidLandscapeSeedError(
            f"{context}.carrier_anchor_policy must be one of "
            f"{sorted(_ALLOWED_CARRIER_ANCHOR_POLICIES)!r}"
        )
    transfer_topology_mode = _require_non_empty_string(
        carrier_mapping.get("transfer_topology_mode"),
        context=f"{context}.transfer_topology_mode",
    )
    if transfer_topology_mode not in _ALLOWED_TRANSFER_TOPOLOGY_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.transfer_topology_mode must be one of "
            f"{sorted(_ALLOWED_TRANSFER_TOPOLOGY_MODES)!r}"
        )
    transfer_role_pairs = _parse_transfer_role_pairs(
        carrier_mapping.get("transfer_role_pairs"),
        context=f"{context}.transfer_role_pairs",
        load_roles=load_roles,
        role_universe=role_universe,
    )
    carrier_attachment_roles = _require_string_sequence(
        carrier_mapping.get("carrier_attachment_roles"),
        context=f"{context}.carrier_attachment_roles",
    )
    for index, role in enumerate(carrier_attachment_roles):
        if role not in load_roles:
            raise InvalidLandscapeSeedError(
                f"{context}.carrier_attachment_roles[{index}] must belong to "
                "the declared outer load-role universe"
            )
    transfer_load_roles = {load_role for load_role, _ in transfer_role_pairs}
    missing_attachment_roles = set(carrier_attachment_roles) - transfer_load_roles
    if missing_attachment_roles:
        raise InvalidLandscapeSeedError(
            f"{context}.transfer_role_pairs must cover every carrier attachment role; "
            f"missing {sorted(missing_attachment_roles)!r}"
        )

    if (
        carrier_anchor_policy == "group_centroid"
        and carrier_layout_mode not in {"group_midpoints", "staggered_arc"}
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.carrier_anchor_policy='group_centroid' requires "
            "carrier_layout_mode='group_midpoints' or 'staggered_arc'"
        )
    if (
        transfer_topology_mode == "nearest_probe_role"
        and any(carrier_role != probe_role for carrier_role, probe_role in transfer_role_pairs)
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.transfer_topology_mode='nearest_probe_role' requires "
            "identity transfer pairs"
        )
    if transfer_topology_mode == "cross_axis_bridge" and all(
        carrier_role == probe_role for carrier_role, probe_role in transfer_role_pairs
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.transfer_topology_mode='cross_axis_bridge' requires at least "
            "one non-identity carrier/probe pair"
        )
    if transfer_topology_mode == "group_bridge":
        support_group_by_role: dict[str, str] = {}
        for group_name, roles in interior_geometry.support_role_groups.items():
            for role in roles:
                support_group_by_role[str(role)] = str(group_name)
        for carrier_role, probe_role in transfer_role_pairs:
            if support_group_by_role.get(carrier_role) != support_group_by_role.get(probe_role):
                raise InvalidLandscapeSeedError(
                    f"{context}.transfer_topology_mode='group_bridge' requires "
                    "carrier/probe pairs to remain inside one support-role group"
                )
    if (
        interfaces is not None
        and interfaces.preferred_attachment_sites
        and not set(carrier_attachment_roles).intersection(load_roles)
    ):
        raise InvalidLandscapeSeedError(
            f"{context}.carrier_attachment_roles must intersect the declared "
            "load-bearing role universe"
        )

    return GRCV3RichInteriorLoadCarriers(
        carrier_layout_mode=carrier_layout_mode,
        carrier_anchor_policy=carrier_anchor_policy,
        transfer_topology_mode=transfer_topology_mode,
        transfer_role_pairs=transfer_role_pairs,
        carrier_attachment_roles=carrier_attachment_roles,
    )


def _parse_pair_mediation_classes(
    value: object,
    *,
    context: str,
    transfer_role_pairs: tuple[tuple[str, str], ...],
) -> tuple[tuple[str, str, str], ...]:
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    if not value:
        raise InvalidLandscapeSeedError(f"{context} must not be empty")
    classes: list[tuple[str, str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()
    expected_pairs = set(transfer_role_pairs)
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        if not isinstance(item, list) or len(item) != 3:
            raise InvalidLandscapeSeedError(
                f"{item_context} must be a three-item [carrier_role, probe_role, mediation_class] list"
            )
        carrier_role = _require_non_empty_string(
            item[0],
            context=f"{item_context}[0]",
        )
        probe_role = _require_non_empty_string(
            item[1],
            context=f"{item_context}[1]",
        )
        mediation_class = _require_non_empty_string(
            item[2],
            context=f"{item_context}[2]",
        )
        if mediation_class not in _ALLOWED_PAIR_MEDIATION_CLASSES:
            raise InvalidLandscapeSeedError(
                f"{item_context}[2] must be one of "
                f"{sorted(_ALLOWED_PAIR_MEDIATION_CLASSES)!r}"
            )
        pair = (carrier_role, probe_role)
        if pair in seen_pairs:
            raise InvalidLandscapeSeedError(f"{context} must contain unique pair assignments")
        if pair not in expected_pairs:
            raise InvalidLandscapeSeedError(
                f"{context} pair {pair!r} must match a declared transfer_role_pair"
            )
        seen_pairs.add(pair)
        classes.append((carrier_role, probe_role, mediation_class))
    missing_pairs = expected_pairs - seen_pairs
    if missing_pairs:
        raise InvalidLandscapeSeedError(
            f"{context} must cover exactly the declared transfer_role_pairs; missing "
            f"{sorted(missing_pairs)!r}"
        )
    return tuple(classes)


def _parse_center_coupling_classes(
    value: object,
    *,
    context: str,
    probe_roles: set[str],
) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    classes: list[tuple[str, str]] = []
    seen_roles: set[str] = set()
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        if not isinstance(item, list) or len(item) != 2:
            raise InvalidLandscapeSeedError(
                f"{item_context} must be a two-item [probe_role, coupling_class] list"
            )
        probe_role = _require_non_empty_string(
            item[0],
            context=f"{item_context}[0]",
        )
        coupling_class = _require_non_empty_string(
            item[1],
            context=f"{item_context}[1]",
        )
        if probe_role not in probe_roles:
            raise InvalidLandscapeSeedError(
                f"{context} role {probe_role!r} must match a declared transfer probe role"
            )
        if coupling_class not in _ALLOWED_PAIR_MEDIATION_CLASSES:
            raise InvalidLandscapeSeedError(
                f"{item_context}[1] must be one of "
                f"{sorted(_ALLOWED_PAIR_MEDIATION_CLASSES)!r}"
            )
        if probe_role in seen_roles:
            raise InvalidLandscapeSeedError(
                f"{context} must contain unique probe-role assignments"
            )
        seen_roles.add(probe_role)
        classes.append((probe_role, coupling_class))
    return tuple(classes)


def _parse_path_topology(
    value: object,
    *,
    context: str,
    transfer_role_pairs: tuple[tuple[str, str], ...],
) -> tuple[tuple[str, str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    if not value:
        raise InvalidLandscapeSeedError(f"{context} must not be empty")
    path_topology: list[tuple[str, str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()
    expected_pairs = set(transfer_role_pairs)
    fan_in_pairs_by_probe_role: dict[str, set[tuple[str, str]]] = {}
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        if not isinstance(item, list) or len(item) != 3:
            raise InvalidLandscapeSeedError(
                f"{item_context} must be a three-item [carrier_role, probe_role, topology_class] list"
            )
        carrier_role = _require_non_empty_string(
            item[0],
            context=f"{item_context}[0]",
        )
        probe_role = _require_non_empty_string(
            item[1],
            context=f"{item_context}[1]",
        )
        topology_class = _require_non_empty_string(
            item[2],
            context=f"{item_context}[2]",
        )
        if topology_class not in _ALLOWED_PATH_TOPOLOGY_CLASSES:
            raise InvalidLandscapeSeedError(
                f"{item_context}[2] must be one of "
                f"{sorted(_ALLOWED_PATH_TOPOLOGY_CLASSES)!r}"
            )
        pair = (carrier_role, probe_role)
        if pair in seen_pairs:
            raise InvalidLandscapeSeedError(f"{context} must contain unique pair assignments")
        if pair not in expected_pairs:
            raise InvalidLandscapeSeedError(
                f"{context} pair {pair!r} must match a declared transfer_role_pair"
            )
        seen_pairs.add(pair)
        path_topology.append((carrier_role, probe_role, topology_class))
        if topology_class == "fan_in":
            fan_in_pairs_by_probe_role.setdefault(probe_role, set()).add(pair)
    missing_pairs = expected_pairs - seen_pairs
    if missing_pairs:
        raise InvalidLandscapeSeedError(
            f"{context} must cover exactly the declared transfer_role_pairs; missing "
            f"{sorted(missing_pairs)!r}"
        )
    declared_pairs_by_probe_role: dict[str, set[tuple[str, str]]] = {}
    for carrier_role, probe_role in transfer_role_pairs:
        declared_pairs_by_probe_role.setdefault(str(probe_role), set()).add(
            (str(carrier_role), str(probe_role))
        )
    for probe_role, fan_in_pairs in fan_in_pairs_by_probe_role.items():
        declared_pairs = declared_pairs_by_probe_role.get(probe_role, set())
        if len(declared_pairs) < 2:
            raise InvalidLandscapeSeedError(
                f"{context} probe role {probe_role!r} cannot use fan_in without at least "
                "two declared transfer pairs"
            )
        if fan_in_pairs != declared_pairs:
            raise InvalidLandscapeSeedError(
                f"{context} probe role {probe_role!r} must assign fan_in to all declared "
                "pairs targeting that probe role"
            )
    return tuple(path_topology)


def _parse_transfer_mediation(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    local_geometry: GRCV3RichLocalGeometry | None,
    interior_load_carriers: GRCV3RichInteriorLoadCarriers | None,
) -> GRCV3RichTransferMediation | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.transfer_mediation"
    if value is None:
        return None
    if contract_version != GRCV3_RICH_V4_CONTRACT_VERSION:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    if not isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
        raise InvalidLandscapeSeedError(
            f"{context} is only supported for basin/plateau primitives in the "
            f"{GRCV3_RICH_V4_CONTRACT_VERSION} contract"
        )
    if local_geometry is None or local_geometry.center_role != "interior_probe":
        raise InvalidLandscapeSeedError(
            f"{context} requires local_geometry.center_role='interior_probe'"
        )
    if interior_load_carriers is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires interior_load_carriers to be declared first"
        )
    mediation_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        mediation_mapping,
        allowed=_ALLOWED_TRANSFER_MEDIATION_KEYS,
        context=context,
        contract_version=contract_version,
    )
    mediation_mode = _require_non_empty_string(
        mediation_mapping.get("mediation_mode"),
        context=f"{context}.mediation_mode",
    )
    if mediation_mode not in _ALLOWED_MEDIATION_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.mediation_mode must be one of "
            f"{sorted(_ALLOWED_MEDIATION_MODES)!r}"
        )
    pair_mediation_classes = _parse_pair_mediation_classes(
        mediation_mapping.get("pair_mediation_classes"),
        context=f"{context}.pair_mediation_classes",
        transfer_role_pairs=interior_load_carriers.transfer_role_pairs,
    )
    probe_guard_class = _require_non_empty_string(
        mediation_mapping.get("probe_guard_class"),
        context=f"{context}.probe_guard_class",
    )
    if probe_guard_class not in _ALLOWED_PROBE_GUARD_CLASSES:
        raise InvalidLandscapeSeedError(
            f"{context}.probe_guard_class must be one of "
            f"{sorted(_ALLOWED_PROBE_GUARD_CLASSES)!r}"
        )
    lateral_spill_policy = _require_non_empty_string(
        mediation_mapping.get("lateral_spill_policy"),
        context=f"{context}.lateral_spill_policy",
    )
    if lateral_spill_policy not in _ALLOWED_LATERAL_SPILL_POLICIES:
        raise InvalidLandscapeSeedError(
            f"{context}.lateral_spill_policy must be one of "
            f"{sorted(_ALLOWED_LATERAL_SPILL_POLICIES)!r}"
        )
    spill_branch_mode = _require_non_empty_string(
        mediation_mapping.get("spill_branch_mode", "carrier_branch"),
        context=f"{context}.spill_branch_mode",
    )
    if spill_branch_mode not in _ALLOWED_SPILL_BRANCH_MODES:
        raise InvalidLandscapeSeedError(
            f"{context}.spill_branch_mode must be one of "
            f"{sorted(_ALLOWED_SPILL_BRANCH_MODES)!r}"
        )
    if mediation_mode == "guarded_pairs" and probe_guard_class == "open_center":
        raise InvalidLandscapeSeedError(
            f"{context}.mediation_mode='guarded_pairs' is incompatible with "
            "probe_guard_class='open_center'"
        )
    if mediation_mode == "confined_pairs" and lateral_spill_policy == "open":
        raise InvalidLandscapeSeedError(
            f"{context}.mediation_mode='confined_pairs' is incompatible with "
            "lateral_spill_policy='open'"
        )
    center_coupling_classes = _parse_center_coupling_classes(
        mediation_mapping.get("center_coupling_classes"),
        context=f"{context}.center_coupling_classes",
        probe_roles={probe_role for _, probe_role in interior_load_carriers.transfer_role_pairs},
    )
    path_topology = _parse_path_topology(
        mediation_mapping.get("path_topology"),
        context=f"{context}.path_topology",
        transfer_role_pairs=interior_load_carriers.transfer_role_pairs,
    )
    return GRCV3RichTransferMediation(
        mediation_mode=mediation_mode,
        pair_mediation_classes=pair_mediation_classes,
        probe_guard_class=probe_guard_class,
        lateral_spill_policy=lateral_spill_policy,
        spill_branch_mode=spill_branch_mode,
        center_coupling_classes=center_coupling_classes,
        path_topology=path_topology,
    )


def _parse_settlement_regime(
    value: object,
    *,
    primitive: LandscapePrimitive,
    contract_version: str,
    local_geometry: GRCV3RichLocalGeometry | None,
    interior_load_carriers: GRCV3RichInteriorLoadCarriers | None,
    transfer_mediation: GRCV3RichTransferMediation | None,
) -> GRCV3RichSettlementRegime | None:
    context = f"primitive[{primitive.id}].extensions.grcv3.settlement_regime"
    if value is None:
        return None
    if contract_version != GRCV3_RICH_V4_CONTRACT_VERSION:
        raise InvalidLandscapeSeedError(
            f"{context} is not supported for the {contract_version} contract"
        )
    if not isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
        raise InvalidLandscapeSeedError(
            f"{context} is only supported for basin/plateau primitives in the "
            f"{GRCV3_RICH_V4_CONTRACT_VERSION} contract"
        )
    if local_geometry is None or local_geometry.center_role != "interior_probe":
        raise InvalidLandscapeSeedError(
            f"{context} requires local_geometry.center_role='interior_probe'"
        )
    if interior_load_carriers is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires interior_load_carriers to be declared first"
        )
    if transfer_mediation is None:
        raise InvalidLandscapeSeedError(
            f"{context} requires transfer_mediation to be declared first"
        )
    regime_mapping = _require_mapping(value, context=context)
    _reject_unknown_keys(
        regime_mapping,
        allowed=_ALLOWED_SETTLEMENT_REGIME_KEYS,
        context=context,
        contract_version=contract_version,
    )
    regime_class_raw = regime_mapping.get("regime_class")
    regime_class = None
    if regime_class_raw is not None:
        regime_class = _require_non_empty_string(
            regime_class_raw,
            context=f"{context}.regime_class",
        )
        if regime_class not in _ALLOWED_SETTLEMENT_REGIME_CLASSES:
            raise InvalidLandscapeSeedError(
                f"{context}.regime_class must be one of "
                f"{sorted(_ALLOWED_SETTLEMENT_REGIME_CLASSES)!r}"
            )
    initial_locus_raw = regime_mapping.get("initial_locus_class")
    initial_locus_class = None
    if initial_locus_raw is not None:
        initial_locus_class = _require_non_empty_string(
            initial_locus_raw,
            context=f"{context}.initial_locus_class",
        )
        if initial_locus_class not in _ALLOWED_SETTLEMENT_INITIAL_LOCUS_CLASSES:
            raise InvalidLandscapeSeedError(
                f"{context}.initial_locus_class must be one of "
                f"{sorted(_ALLOWED_SETTLEMENT_INITIAL_LOCUS_CLASSES)!r}"
            )
    split_inheritance_raw = regime_mapping.get("split_inheritance_mode")
    split_inheritance_mode = None
    if split_inheritance_raw is not None:
        split_inheritance_mode = _require_non_empty_string(
            split_inheritance_raw,
            context=f"{context}.split_inheritance_mode",
        )
        if split_inheritance_mode not in _ALLOWED_SETTLEMENT_SPLIT_INHERITANCE_MODES:
            raise InvalidLandscapeSeedError(
                f"{context}.split_inheritance_mode must be one of "
                f"{sorted(_ALLOWED_SETTLEMENT_SPLIT_INHERITANCE_MODES)!r}"
            )
    implied_mapping = {
        "carrier_site_regime": ("carrier_site", "anchored"),
        "path_node_regime": ("path_node", "split_child_inheriting"),
    }
    if regime_class is None and (
        initial_locus_class is None or split_inheritance_mode is None
    ):
        raise InvalidLandscapeSeedError(
            f"{context} requires either regime_class or both initial_locus_class "
            "and split_inheritance_mode"
        )
    if regime_class is not None:
        implied_locus_class, implied_split_mode = implied_mapping[regime_class]
        if initial_locus_class is None:
            initial_locus_class = implied_locus_class
        elif initial_locus_class != implied_locus_class:
            raise InvalidLandscapeSeedError(
                f"{context}.initial_locus_class must match regime_class={regime_class!r}"
            )
        if split_inheritance_mode is None:
            split_inheritance_mode = implied_split_mode
        elif split_inheritance_mode != implied_split_mode:
            raise InvalidLandscapeSeedError(
                f"{context}.split_inheritance_mode must match regime_class={regime_class!r}"
            )
    assert initial_locus_class is not None
    assert split_inheritance_mode is not None
    if initial_locus_class == "path_node":
        path_topology = tuple(transfer_mediation.path_topology)
        if not path_topology or not any(
            str(topology_class) != "direct" for _, _, topology_class in path_topology
        ):
            raise InvalidLandscapeSeedError(
                f"{context}.initial_locus_class='path_node' requires at least one "
                "non-direct transfer_mediation.path_topology assignment"
            )
    return GRCV3RichSettlementRegime(
        regime_class=regime_class,
        initial_locus_class=initial_locus_class,
        split_inheritance_mode=split_inheritance_mode,
    )


def _allowed_keys_for_primitive(
    primitive: LandscapePrimitive,
    *,
    contract_version: str,
) -> set[str]:
    if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION:
        return _ALLOWED_PRIMITIVE_KEYS_V1
    if contract_version == GRCV3_RICH_V4_CONTRACT_VERSION:
        if isinstance(primitive, JunctionSeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V4_JUNCTION
        if isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
            return _ALLOWED_PRIMITIVE_KEYS_V4_BASIN
        if isinstance(primitive, RidgeSeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V2_RIDGE
        if isinstance(primitive, ValleySeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V2_VALLEY
        raise InvalidLandscapeSeedError(
            f"primitive[{primitive.id}].extensions.grcv3 is not supported for type "
            f"{primitive.type!r} in the {contract_version} contract"
        )
    if contract_version == GRCV3_RICH_V3_CONTRACT_VERSION:
        if isinstance(primitive, JunctionSeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V3_JUNCTION
        if isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
            return _ALLOWED_PRIMITIVE_KEYS_V3_BASIN
        if isinstance(primitive, RidgeSeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V2_RIDGE
        if isinstance(primitive, ValleySeedPrimitive):
            return _ALLOWED_PRIMITIVE_KEYS_V2_VALLEY
        raise InvalidLandscapeSeedError(
            f"primitive[{primitive.id}].extensions.grcv3 is not supported for type "
            f"{primitive.type!r} in the {contract_version} contract"
        )
    if isinstance(primitive, JunctionSeedPrimitive):
        return _ALLOWED_PRIMITIVE_KEYS_V2_JUNCTION
    if isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
        return _ALLOWED_PRIMITIVE_KEYS_V2_BASIN
    if isinstance(primitive, RidgeSeedPrimitive):
        return _ALLOWED_PRIMITIVE_KEYS_V2_RIDGE
    if isinstance(primitive, ValleySeedPrimitive):
        return _ALLOWED_PRIMITIVE_KEYS_V2_VALLEY
    raise InvalidLandscapeSeedError(
        f"primitive[{primitive.id}].extensions.grcv3 is not supported for type "
        f"{primitive.type!r} in the {contract_version} contract"
    )


def _parse_primitive_extension(
    primitive: LandscapePrimitive,
    raw_extension: object,
    *,
    seed: LandscapeSeed,
    contract_version: str,
) -> GRCV3RichPrimitiveExtension:
    context = f"primitive[{primitive.id}].extensions.grcv3"
    if contract_version == GRCV3_RICH_V1_CONTRACT_VERSION:
        if primitive.type not in _ALLOWED_PRIMITIVE_TYPES_V1 or not isinstance(
            primitive, JunctionSeedPrimitive
        ):
            raise InvalidLandscapeSeedError(
                f"{context} is only supported for junction/saddle primitives in the "
                f"{GRCV3_RICH_V1_CONTRACT_VERSION} contract"
            )
    elif primitive.type not in _ALLOWED_PRIMITIVE_TYPES_V2:
        raise InvalidLandscapeSeedError(
            f"{context} is only supported for basin/plateau/junction/saddle/ridge/valley "
            f"primitives in the {contract_version} contract"
        )

    extension_mapping = _require_mapping(raw_extension, context=context)
    _reject_unknown_keys(
        extension_mapping,
        allowed=_allowed_keys_for_primitive(primitive, contract_version=contract_version),
        context=context,
        contract_version=contract_version,
    )

    realization_required = isinstance(primitive, JunctionSeedPrimitive)
    realization = _parse_realization(
        extension_mapping.get("realization"),
        primitive=primitive,
        contract_version=contract_version,
        required=realization_required,
    )
    local_geometry_required = isinstance(
        primitive, JunctionSeedPrimitive | BasinSeedPrimitive | PlateauSeedPrimitive
    )
    local_geometry = _parse_local_geometry(
        extension_mapping.get("local_geometry"),
        primitive=primitive,
        contract_version=contract_version,
        realization=realization,
        required=local_geometry_required,
    )
    curvature_intent = _parse_curvature_intent(
        extension_mapping.get("curvature_intent"),
        primitive=primitive,
        contract_version=contract_version,
        realization=realization,
        local_geometry=local_geometry,
    )
    boundary_geometry = _parse_boundary_geometry(
        extension_mapping.get("boundary_geometry"),
        primitive=primitive,
        contract_version=contract_version,
        required=isinstance(primitive, RidgeSeedPrimitive),
    )
    channel_geometry = _parse_channel_geometry(
        extension_mapping.get("channel_geometry"),
        primitive=primitive,
        contract_version=contract_version,
        required=isinstance(primitive, ValleySeedPrimitive),
    )
    interfaces_required = isinstance(primitive, JunctionSeedPrimitive)
    interfaces = _parse_interfaces(
        extension_mapping.get("interfaces"),
        primitive=primitive,
        seed=seed,
        contract_version=contract_version,
        realization=realization,
        local_geometry=local_geometry,
        boundary_geometry=boundary_geometry,
        channel_geometry=channel_geometry,
        required=interfaces_required,
    )
    interior_geometry = _parse_interior_geometry(
        extension_mapping.get("interior_geometry"),
        primitive=primitive,
        contract_version=contract_version,
        realization=realization,
        local_geometry=local_geometry,
        interfaces=interfaces,
    )
    interior_partition = _parse_interior_partition(
        extension_mapping.get("interior_partition"),
        primitive=primitive,
        contract_version=contract_version,
        local_geometry=local_geometry,
        interfaces=interfaces,
        interior_geometry=interior_geometry,
    )
    interior_load_carriers = _parse_interior_load_carriers(
        extension_mapping.get("interior_load_carriers"),
        primitive=primitive,
        contract_version=contract_version,
        local_geometry=local_geometry,
        interfaces=interfaces,
        interior_geometry=interior_geometry,
        interior_partition=interior_partition,
    )
    transfer_mediation = _parse_transfer_mediation(
        extension_mapping.get("transfer_mediation"),
        primitive=primitive,
        contract_version=contract_version,
        local_geometry=local_geometry,
        interior_load_carriers=interior_load_carriers,
    )
    settlement_regime = _parse_settlement_regime(
        extension_mapping.get("settlement_regime"),
        primitive=primitive,
        contract_version=contract_version,
        local_geometry=local_geometry,
        interior_load_carriers=interior_load_carriers,
        transfer_mediation=transfer_mediation,
    )

    return GRCV3RichPrimitiveExtension(
        primitive_id=primitive.id,
        realization=realization,
        local_geometry=local_geometry,
        curvature_intent=curvature_intent,
        interfaces=interfaces,
        boundary_geometry=boundary_geometry,
        channel_geometry=channel_geometry,
        interior_geometry=interior_geometry,
        interior_partition=interior_partition,
        interior_load_carriers=interior_load_carriers,
        transfer_mediation=transfer_mediation,
        settlement_regime=settlement_regime,
    )


def extract_grcv3_seed_extension(seed: LandscapeSeed) -> GRCV3RichSeedExtension | None:
    """Extract the supported typed `GRCL-v3` seed extension.

    Returns `None` when the seed has no `GRCV3` rich extension or when the
    extension is present but uses an unknown contract version with
    `rich_required = false`.
    """

    primitive_extension_payloads = {
        primitive.id: primitive.extensions.get("grcv3")
        for primitive in seed.primitives
        if isinstance(primitive.extensions, Mapping) and "grcv3" in primitive.extensions
    }
    raw_top_level = seed.extensions.get("grcv3")
    if raw_top_level is None and not primitive_extension_payloads:
        return None
    if raw_top_level is None:
        raise InvalidLandscapeSeedError(
            "seed.extensions.grcv3 is required when primitive-level grcv3 "
            "extensions are present"
        )

    top_level_mapping = _require_mapping(raw_top_level, context="seed.extensions.grcv3")
    _reject_unknown_keys(
        top_level_mapping,
        allowed=_ALLOWED_TOP_LEVEL_KEYS,
        context="seed.extensions.grcv3",
        contract_version="grcv3",
    )
    contract_version = _require_non_empty_string(
        top_level_mapping.get("contract_version"),
        context="seed.extensions.grcv3.contract_version",
    )
    rich_required = _require_bool(
        top_level_mapping.get("rich_required"),
        context="seed.extensions.grcv3.rich_required",
    )
    if contract_version not in _SUPPORTED_GRCV3_CONTRACT_VERSIONS:
        if rich_required:
            raise InvalidLandscapeSeedError(
                f"unsupported GRCV3 rich contract version {contract_version!r}; "
                f"expected one of {sorted(_SUPPORTED_GRCV3_CONTRACT_VERSIONS)!r}"
            )
        return None

    primitive_index = _primitive_index(seed)
    primitive_extensions: dict[str, GRCV3RichPrimitiveExtension] = {}
    for primitive_id, raw_extension in sorted(primitive_extension_payloads.items()):
        primitive = primitive_index[primitive_id]
        primitive_extensions[primitive_id] = _parse_primitive_extension(
            primitive,
            raw_extension,
            seed=seed,
            contract_version=contract_version,
        )

    return GRCV3RichSeedExtension(
        contract_version=contract_version,
        rich_required=rich_required,
        primitive_extensions=MappingProxyType(
            {
                primitive_id: primitive_extensions[primitive_id]
                for primitive_id in sorted(primitive_extensions)
            }
        ),
    )


__all__ = [
    "GRCV3RichBoundaryGeometry",
    "GRCV3RichChannelGeometry",
    "GRCV3RichCurvatureIntent",
    "GRCV3RichInteriorGeometry",
    "GRCV3RichInteriorLoadCarriers",
    "GRCV3RichInteriorPartition",
    "GRCV3RichInterfaces",
    "GRCV3RichLocalGeometry",
    "GRCV3RichPrimitiveExtension",
    "GRCV3RichRealization",
    "GRCV3RichSeedExtension",
    "GRCV3RichTransferMediation",
    "GRCV3_RICH_V1_CONTRACT_VERSION",
    "GRCV3_RICH_V2_CONTRACT_VERSION",
    "GRCV3_RICH_V3_CONTRACT_VERSION",
    "GRCV3_RICH_V4_CONTRACT_VERSION",
    "extract_grcv3_seed_extension",
]

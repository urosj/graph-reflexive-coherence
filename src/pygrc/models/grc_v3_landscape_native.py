"""Family-native lowering support for `GRCV3` rich landscape seeds."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_BASIN,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_RIDGE,
    PRIMITIVE_SADDLE,
    PRIMITIVE_VALLEY,
    RidgeSeedPrimitive,
    ValleySeedPrimitive,
)
from pygrc.landscapes.extensions.grcv3 import (
    GRCV3RichBoundaryGeometry,
    GRCV3RichChannelGeometry,
    GRCV3RichCurvatureIntent,
    GRCV3RichInteriorGeometry,
    GRCV3RichInteriorLoadCarriers,
    GRCV3RichInteriorPartition,
    GRCV3RichInterfaces,
    GRCV3RichLocalGeometry,
    GRCV3RichPrimitiveExtension,
    GRCV3RichRealization,
    GRCV3RichSeedExtension,
    GRCV3RichSettlementRegime,
    GRCV3RichTransferMediation,
    GRCV3_RICH_V2_CONTRACT_VERSION,
)


LOWERING_LANE_COMPATIBILITY = "compatibility"
LOWERING_LANE_FAMILY_NATIVE = "family_native"

_TEMPORARY_BLUEPRINT_UTILITY_FUNCTIONS = (
    "_euclidean_length",
    "_freeze_optional_mapping",
    "_to_plain_data",
    "_transport_intent_metadata",
)

_PROHIBITED_BLUEPRINT_SEMANTIC_AUTHORITIES = (
    "GRCV2LandscapeBlueprint",
    "realize_grcv2_landscape_blueprint",
)


@dataclass(frozen=True)
class GRCV3NativePrimitiveSurface:
    """Direct seed-primitive surface for the family-native lowering lane."""

    rich_contract_version: str
    primitive_index: Mapping[str, LandscapePrimitive]
    primitive_ids_by_type: Mapping[str, tuple[str, ...]]
    node_carrier_ids: tuple[str, ...]
    edge_carrier_ids: tuple[str, ...]
    basin_like_plans: Mapping[str, "GRCV3NativeBasinLikePlan"]
    junction_plans: Mapping[str, "GRCV3NativeJunctionPlan"]
    valley_plans: Mapping[str, "GRCV3NativeValleyPlan"]
    ridge_plans: Mapping[str, "GRCV3NativeRidgePlan"]
    ridge_ids_by_owner: Mapping[str, tuple[str, ...]]
    metadata_only_ridge_ids: tuple[str, ...]
    junction_like_ids: tuple[str, ...]
    rich_primitive_ids: tuple[str, ...]
    temporary_blueprint_utility_functions: tuple[str, ...]
    prohibited_blueprint_semantic_authorities: tuple[str, ...]


@dataclass(frozen=True)
class GRCV3NativeBasinLikePlan:
    primitive_id: str
    primitive_type: str
    role: str | None
    parent_id: str | None
    coherence_prior: float | None
    depth: int
    chart_center_hint: tuple[float, float] | None
    chart_scale_hint: Mapping[str, Any]
    source_extensions: Mapping[str, Any]
    boundary_ids: tuple[str, ...]
    hosted_primitive_ids: tuple[str, ...]
    role_order: tuple[str, ...]
    center_role: str | None
    symmetry_class: str | None
    weak_axis_role: str | None
    curvature_class: str | None
    stable_axis_roles: tuple[str, ...]
    preferred_attachment_sites: Mapping[str, str]
    interior_geometry: GRCV3RichInteriorGeometry | None
    interior_partition: GRCV3RichInteriorPartition | None
    interior_load_carriers: GRCV3RichInteriorLoadCarriers | None
    transfer_mediation: GRCV3RichTransferMediation | None
    settlement_regime: GRCV3RichSettlementRegime | None


@dataclass(frozen=True)
class GRCV3NativeJunctionPlan:
    primitive_id: str
    primitive_type: str
    role: str | None
    parent_id: str | None
    coherence_prior: float | None
    depth: int
    chart_center_hint: tuple[float, float] | None
    chart_scale_hint: Mapping[str, Any]
    source_extensions: Mapping[str, Any]
    host_id: str | None
    hostless: bool
    branch_target_ids: tuple[str, ...]
    junction_role: str | None
    support_count: int
    radius_scale: float
    branch_order: tuple[str, ...]
    frame_mode: str | None
    weak_axis_role: str | None
    branch_targets: Mapping[str, str]
    interior_geometry: GRCV3RichInteriorGeometry | None


@dataclass(frozen=True)
class GRCV3NativeValleyPlan:
    primitive_id: str
    primitive_type: str
    role: str | None
    source_primitive_id: str
    target_primitive_id: str
    coherence_prior: float | None
    width_hint: float | None
    path_hint: str | None
    depth: int
    waypoints: tuple[tuple[float, float], ...]
    source_extensions: Mapping[str, Any]
    channel_role: str | None
    channel_geometry: GRCV3RichChannelGeometry | None
    preferred_attachment_sites: Mapping[str, str]


@dataclass(frozen=True)
class GRCV3NativeRidgePlan:
    primitive_id: str
    primitive_type: str
    role: str | None
    source_primitive_id: str
    target_primitive_id: str | None
    adjacent_ids: tuple[str, ...]
    ridge_kind: str | None
    thickness_hint: float | None
    interior_coherence_hint: float | None
    exterior_coherence_hint: float | None
    chart_principal_axis_hint: tuple[float, float] | None
    source_extensions: Mapping[str, Any]
    boundary_geometry: GRCV3RichBoundaryGeometry | None
    boundary_roles: tuple[str, ...]
    preferred_attachment_sites: Mapping[str, str]
    metadata_only: bool


def _freeze_plain_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_plain_value(inner) for key, inner in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_freeze_plain_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_plain_value(item) for item in value)
    return value


def _freeze_plain_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if value is None:
        return MappingProxyType({})
    return MappingProxyType(
        {str(key): _freeze_plain_value(inner) for key, inner in sorted(value.items())}
    )


def _freeze_string_mapping(value: Mapping[str, str] | None) -> Mapping[str, str]:
    if value is None:
        return MappingProxyType({})
    return MappingProxyType({str(key): str(inner) for key, inner in sorted(value.items())})


def _optional_center(point: list[float] | None) -> tuple[float, float] | None:
    if point is None:
        return None
    return (float(point[0]), float(point[1]))


def _optional_axis(point: list[float] | None) -> tuple[float, float] | None:
    if point is None:
        return None
    return (float(point[0]), float(point[1]))


def _primitive_depth(primitive: LandscapePrimitive) -> int:
    raw_depth = getattr(primitive, "depth_hint", None)
    return 0 if raw_depth is None else int(raw_depth)


def _role_order_from_local_geometry(
    local_geometry: GRCV3RichLocalGeometry | None,
) -> tuple[str, ...]:
    if local_geometry is None:
        return ()
    return tuple(local_geometry.axis_roles)


def _preferred_attachment_sites(
    interfaces: GRCV3RichInterfaces | None,
) -> Mapping[str, str]:
    if interfaces is None:
        return MappingProxyType({})
    return _freeze_string_mapping(interfaces.preferred_attachment_sites)


def _boundary_roles(interfaces: GRCV3RichInterfaces | None) -> tuple[str, ...]:
    if interfaces is None:
        return ()
    return tuple(interfaces.boundary_roles)


def _branch_targets(interfaces: GRCV3RichInterfaces | None) -> Mapping[str, str]:
    if interfaces is None:
        return MappingProxyType({})
    return _freeze_string_mapping(interfaces.branch_targets)


def _build_basin_like_plan(
    primitive: BasinSeedPrimitive | PlateauSeedPrimitive,
    *,
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
) -> GRCV3NativeBasinLikePlan:
    local_geometry = None if rich_primitive_extension is None else rich_primitive_extension.local_geometry
    curvature_intent = (
        None if rich_primitive_extension is None else rich_primitive_extension.curvature_intent
    )
    interfaces = None if rich_primitive_extension is None else rich_primitive_extension.interfaces
    return GRCV3NativeBasinLikePlan(
        primitive_id=primitive.id,
        primitive_type=primitive.type,
        role=primitive.role,
        parent_id=primitive.parent_id,
        coherence_prior=primitive.coherence_prior,
        depth=_primitive_depth(primitive),
        chart_center_hint=_optional_center(primitive.chart_center_hint),
        chart_scale_hint=_freeze_plain_mapping(primitive.chart_scale_hint),
        source_extensions=_freeze_plain_mapping(primitive.extensions),
        boundary_ids=tuple(getattr(primitive, "boundary_ids", ())),
        hosted_primitive_ids=tuple(getattr(primitive, "hosted_primitive_ids", ())),
        role_order=_role_order_from_local_geometry(local_geometry),
        center_role=None if local_geometry is None else local_geometry.center_role,
        symmetry_class=None if local_geometry is None else local_geometry.symmetry_class,
        weak_axis_role=None if local_geometry is None else local_geometry.weak_axis_role,
        curvature_class=(
            None if curvature_intent is None else curvature_intent.curvature_class
        ),
        stable_axis_roles=(
            () if curvature_intent is None else tuple(curvature_intent.stable_axis_roles)
        ),
        preferred_attachment_sites=_preferred_attachment_sites(interfaces),
        interior_geometry=(
            None if rich_primitive_extension is None else rich_primitive_extension.interior_geometry
        ),
        interior_partition=(
            None if rich_primitive_extension is None else rich_primitive_extension.interior_partition
        ),
        interior_load_carriers=(
            None
            if rich_primitive_extension is None
            else rich_primitive_extension.interior_load_carriers
        ),
        transfer_mediation=(
            None
            if rich_primitive_extension is None
            else rich_primitive_extension.transfer_mediation
        ),
        settlement_regime=(
            None
            if rich_primitive_extension is None
            else rich_primitive_extension.settlement_regime
        ),
    )


def _build_junction_plan(
    primitive: JunctionSeedPrimitive,
    *,
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
) -> GRCV3NativeJunctionPlan:
    realization = None if rich_primitive_extension is None else rich_primitive_extension.realization
    local_geometry = None if rich_primitive_extension is None else rich_primitive_extension.local_geometry
    interfaces = None if rich_primitive_extension is None else rich_primitive_extension.interfaces
    return GRCV3NativeJunctionPlan(
        primitive_id=primitive.id,
        primitive_type=primitive.type,
        role=primitive.role,
        parent_id=primitive.host_id,
        coherence_prior=primitive.coherence_prior,
        depth=_primitive_depth(primitive),
        chart_center_hint=_optional_center(primitive.chart_center_hint),
        chart_scale_hint=MappingProxyType({}),
        source_extensions=_freeze_plain_mapping(primitive.extensions),
        host_id=primitive.host_id,
        hostless=primitive.host_id is None,
        branch_target_ids=tuple(primitive.branch_target_ids),
        junction_role=primitive.junction_role,
        support_count=(
            len(primitive.branch_target_ids)
            if realization is None
            else int(realization.support_count)
        ),
        radius_scale=1.0 if realization is None else float(realization.radius_scale),
        branch_order=(
            tuple(f"branch_{index}" for index in range(len(primitive.branch_target_ids)))
            if realization is None
            else tuple(realization.branch_order)
        ),
        frame_mode=None if local_geometry is None else local_geometry.frame_mode,
        weak_axis_role=None if local_geometry is None else local_geometry.weak_axis_role,
        branch_targets=_branch_targets(interfaces),
        interior_geometry=(
            None if rich_primitive_extension is None else rich_primitive_extension.interior_geometry
        ),
    )


def _build_valley_plan(
    primitive: ValleySeedPrimitive,
    *,
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
    primitive_depth_by_id: Mapping[str, int],
) -> GRCV3NativeValleyPlan:
    interfaces = None if rich_primitive_extension is None else rich_primitive_extension.interfaces
    source_depth = primitive_depth_by_id.get(primitive.from_id or "", 0)
    target_depth = primitive_depth_by_id.get(primitive.to_id or "", 0)
    return GRCV3NativeValleyPlan(
        primitive_id=primitive.id,
        primitive_type=primitive.type,
        role=primitive.role,
        source_primitive_id=str(primitive.from_id),
        target_primitive_id=str(primitive.to_id),
        coherence_prior=primitive.coherence_prior,
        width_hint=primitive.width_hint,
        path_hint=primitive.path_hint,
        depth=max(source_depth, target_depth),
        waypoints=tuple(
            (float(point[0]), float(point[1]))
            for point in primitive.waypoints
            if len(point) >= 2
        ),
        source_extensions=_freeze_plain_mapping(primitive.extensions),
        channel_role=primitive.channel_role,
        channel_geometry=(
            None if rich_primitive_extension is None else rich_primitive_extension.channel_geometry
        ),
        preferred_attachment_sites=_preferred_attachment_sites(interfaces),
    )


def _build_ridge_plan(
    primitive: RidgeSeedPrimitive,
    *,
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
) -> GRCV3NativeRidgePlan:
    interfaces = None if rich_primitive_extension is None else rich_primitive_extension.interfaces
    adjacent_ids = tuple(primitive.adjacent_ids)
    return GRCV3NativeRidgePlan(
        primitive_id=primitive.id,
        primitive_type=primitive.type,
        role=primitive.role,
        source_primitive_id=str(primitive.owner_id),
        target_primitive_id=(None if not adjacent_ids else adjacent_ids[0]),
        adjacent_ids=adjacent_ids,
        ridge_kind=primitive.ridge_kind,
        thickness_hint=primitive.thickness_hint,
        interior_coherence_hint=primitive.interior_coherence_hint,
        exterior_coherence_hint=primitive.exterior_coherence_hint,
        chart_principal_axis_hint=_optional_axis(primitive.chart_principal_axis_hint),
        source_extensions=_freeze_plain_mapping(primitive.extensions),
        boundary_geometry=(
            None if rich_primitive_extension is None else rich_primitive_extension.boundary_geometry
        ),
        boundary_roles=_boundary_roles(interfaces),
        preferred_attachment_sites=_preferred_attachment_sites(interfaces),
        metadata_only=not adjacent_ids,
    )


def _is_junction_like_basin(primitive: LandscapePrimitive) -> bool:
    if getattr(primitive, "type", None) != PRIMITIVE_BASIN:
        return False
    if not isinstance(getattr(primitive, "extensions", None), Mapping):
        return False
    source_pde = primitive.extensions.get("source_pde")
    if not isinstance(source_pde, Mapping):
        return False
    implied_role = source_pde.get("implied_role")
    return isinstance(implied_role, str) and implied_role == "saddle_like_hub"


def is_junction_like_primitive(primitive: LandscapePrimitive) -> bool:
    primitive_type = getattr(primitive, "type", None)
    if primitive_type in {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}:
        return True
    return _is_junction_like_basin(primitive)


def select_grcv3_lowering_lane(
    rich_seed_extension: GRCV3RichSeedExtension | None,
) -> str:
    """Select the lowering lane from the parsed rich-seed contract."""

    if rich_seed_extension is None:
        return LOWERING_LANE_COMPATIBILITY
    if rich_seed_extension.contract_version >= GRCV3_RICH_V2_CONTRACT_VERSION:
        return LOWERING_LANE_FAMILY_NATIVE
    return LOWERING_LANE_COMPATIBILITY


def lowering_semantic_authority(lowering_lane: str) -> str:
    """Describe which semantic surface is authoritative for the selected lane."""

    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE:
        return "direct_seed_primitives"
    return "grcv2_blueprint"


def lowering_blueprint_usage(lowering_lane: str) -> str:
    """Describe how the `GRCV2` blueprint is allowed to appear in a lane."""

    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE:
        return "implementation_carrier_reuse_only"
    return "authoritative_semantic_intermediate"


def build_grcv3_native_primitive_surface(
    seed: LandscapeSeed,
    *,
    rich_seed_extension: GRCV3RichSeedExtension,
) -> GRCV3NativePrimitiveSurface:
    """Build the direct primitive surface for the family-native lowering lane."""

    primitive_index = {primitive.id: primitive for primitive in seed.primitives}
    primitive_ids_by_type: dict[str, list[str]] = {
        PRIMITIVE_BASIN: [],
        PRIMITIVE_PLATEAU: [],
        PRIMITIVE_JUNCTION: [],
        PRIMITIVE_SADDLE: [],
        PRIMITIVE_RIDGE: [],
        PRIMITIVE_VALLEY: [],
    }
    primitive_depth_by_id = {primitive.id: _primitive_depth(primitive) for primitive in seed.primitives}
    node_carrier_ids: list[str] = []
    edge_carrier_ids: list[str] = []
    basin_like_plans: dict[str, GRCV3NativeBasinLikePlan] = {}
    junction_plans: dict[str, GRCV3NativeJunctionPlan] = {}
    valley_plans: dict[str, GRCV3NativeValleyPlan] = {}
    ridge_plans: dict[str, GRCV3NativeRidgePlan] = {}
    ridge_ids_by_owner: dict[str, list[str]] = {}
    metadata_only_ridge_ids: list[str] = []
    junction_like_ids: list[str] = []
    for primitive in seed.primitives:
        rich_primitive_extension = rich_seed_extension.primitive_extensions.get(primitive.id)
        primitive_ids_by_type.setdefault(primitive.type, []).append(primitive.id)
        if isinstance(primitive, (BasinSeedPrimitive, PlateauSeedPrimitive)):
            node_carrier_ids.append(primitive.id)
            basin_like_plans[primitive.id] = _build_basin_like_plan(
                primitive,
                rich_primitive_extension=rich_primitive_extension,
            )
        if isinstance(primitive, JunctionSeedPrimitive):
            node_carrier_ids.append(primitive.id)
            junction_plans[primitive.id] = _build_junction_plan(
                primitive,
                rich_primitive_extension=rich_primitive_extension,
            )
        if isinstance(primitive, ValleySeedPrimitive):
            edge_carrier_ids.append(primitive.id)
            valley_plans[primitive.id] = _build_valley_plan(
                primitive,
                rich_primitive_extension=rich_primitive_extension,
                primitive_depth_by_id=primitive_depth_by_id,
            )
        if isinstance(primitive, RidgeSeedPrimitive):
            edge_carrier_ids.append(primitive.id)
            ridge_plans[primitive.id] = _build_ridge_plan(
                primitive,
                rich_primitive_extension=rich_primitive_extension,
            )
            if primitive.owner_id is not None:
                ridge_ids_by_owner.setdefault(str(primitive.owner_id), []).append(primitive.id)
            if not primitive.adjacent_ids:
                metadata_only_ridge_ids.append(primitive.id)
        if is_junction_like_primitive(primitive):
            junction_like_ids.append(primitive.id)
    return GRCV3NativePrimitiveSurface(
        rich_contract_version=rich_seed_extension.contract_version,
        primitive_index=MappingProxyType(
            {primitive_id: primitive_index[primitive_id] for primitive_id in sorted(primitive_index)}
        ),
        primitive_ids_by_type=MappingProxyType(
            {
                primitive_type: tuple(sorted(primitive_ids))
                for primitive_type, primitive_ids in sorted(primitive_ids_by_type.items())
                if primitive_ids
            }
        ),
        node_carrier_ids=tuple(node_carrier_ids),
        edge_carrier_ids=tuple(edge_carrier_ids),
        basin_like_plans=MappingProxyType(
            {primitive_id: basin_like_plans[primitive_id] for primitive_id in sorted(basin_like_plans)}
        ),
        junction_plans=MappingProxyType(
            {primitive_id: junction_plans[primitive_id] for primitive_id in sorted(junction_plans)}
        ),
        valley_plans=MappingProxyType(
            {primitive_id: valley_plans[primitive_id] for primitive_id in sorted(valley_plans)}
        ),
        ridge_plans=MappingProxyType(
            {primitive_id: ridge_plans[primitive_id] for primitive_id in sorted(ridge_plans)}
        ),
        ridge_ids_by_owner=MappingProxyType(
            {
                primitive_id: tuple(ridge_ids)
                for primitive_id, ridge_ids in sorted(ridge_ids_by_owner.items())
            }
        ),
        metadata_only_ridge_ids=tuple(metadata_only_ridge_ids),
        junction_like_ids=tuple(sorted(junction_like_ids)),
        rich_primitive_ids=tuple(sorted(rich_seed_extension.primitive_extensions)),
        temporary_blueprint_utility_functions=_TEMPORARY_BLUEPRINT_UTILITY_FUNCTIONS,
        prohibited_blueprint_semantic_authorities=_PROHIBITED_BLUEPRINT_SEMANTIC_AUTHORITIES,
    )


__all__ = [
    "GRCV3NativePrimitiveSurface",
    "GRCV3NativeBasinLikePlan",
    "GRCV3NativeJunctionPlan",
    "GRCV3NativeRidgePlan",
    "GRCV3NativeValleyPlan",
    "LOWERING_LANE_COMPATIBILITY",
    "LOWERING_LANE_FAMILY_NATIVE",
    "build_grcv3_native_primitive_surface",
    "is_junction_like_primitive",
    "lowering_blueprint_usage",
    "lowering_semantic_authority",
    "select_grcv3_lowering_lane",
]

"""Validation boundary for normalized landscape seed documents."""

from __future__ import annotations

import math

from pygrc.core import InvalidLandscapeSeedError

from .seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LANDSCAPE_PRIMITIVE_TYPES,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_SADDLE,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedGeometryHints,
    SeedTransportIntent,
    ValleySeedPrimitive,
)


INFERRED_OBSERVED_LANDSCAPE_SOURCE_KIND = "inferred_observed_landscape"


def _require_non_empty_string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidLandscapeSeedError(f"{context} must be a non-empty string")
    return value


def _require_real_number(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(f"{context} must be a float-compatible number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidLandscapeSeedError(f"{context} must be a finite real number")
    return number


def _validate_chart_point(point: object, *, context: str) -> None:
    if point is None:
        return
    if not isinstance(point, list) or len(point) != 2:
        raise InvalidLandscapeSeedError(f"{context} must be a 2D point list [x, y]")
    for index, component in enumerate(point):
        _require_real_number(component, context=f"{context}[{index}]")


def _validate_string_list(values: object, *, context: str) -> None:
    if not isinstance(values, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    for index, value in enumerate(values):
        _require_non_empty_string(value, context=f"{context}[{index}]")


def _validate_mapping(value: object, *, context: str) -> None:
    if not isinstance(value, dict):
        raise InvalidLandscapeSeedError(f"{context} must be a mapping")


def _validate_constitutive_profile(profile: SeedConstitutiveProfile) -> None:
    _require_real_number(profile.lambda_c, context="constitutive_profile.lambda_c")
    _require_real_number(profile.xi_c, context="constitutive_profile.xi_c")
    _require_real_number(profile.zeta_c, context="constitutive_profile.zeta_c")
    _require_real_number(profile.kappa_c, context="constitutive_profile.kappa_c")
    dt = _require_real_number(profile.dt, context="constitutive_profile.dt")
    if dt <= 0.0:
        raise InvalidLandscapeSeedError("constitutive_profile.dt must be > 0")
    _require_non_empty_string(
        profile.potential.type,
        context="constitutive_profile.potential.type",
    )
    _validate_mapping(
        profile.potential.params,
        context="constitutive_profile.potential.params",
    )
    if profile.budget_b is not None:
        budget = _require_real_number(
            profile.budget_b,
            context="constitutive_profile.budget_b",
        )
        if budget <= 0.0:
            raise InvalidLandscapeSeedError(
                "constitutive_profile.budget_b must be > 0 when present"
            )


def _validate_geometry_hints(geometry: SeedGeometryHints) -> None:
    if geometry.source_chart is not None:
        _require_non_empty_string(
            geometry.source_chart,
            context="geometry_hints.source_chart",
        )
    _validate_mapping(geometry.periodicity, context="geometry_hints.periodicity")
    _validate_mapping(
        geometry.separation_hints,
        context="geometry_hints.separation_hints",
    )


def _validate_basin_like(
    primitive: BasinSeedPrimitive | PlateauSeedPrimitive,
    *,
    context: str,
    known_ids: set[str],
) -> None:
    if primitive.depth_hint is not None:
        if not isinstance(primitive.depth_hint, int) or primitive.depth_hint < 0:
            raise InvalidLandscapeSeedError(f"{context}.depth_hint must be a non-negative int")
    if primitive.coherence_prior is not None:
        _require_real_number(primitive.coherence_prior, context=f"{context}.coherence_prior")
    _validate_chart_point(
        primitive.chart_center_hint,
        context=f"{context}.chart_center_hint",
    )
    _validate_mapping(
        primitive.chart_scale_hint,
        context=f"{context}.chart_scale_hint",
    )
    if isinstance(primitive, BasinSeedPrimitive):
        _validate_string_list(primitive.boundary_ids, context=f"{context}.boundary_ids")
        for boundary_id in primitive.boundary_ids:
            if boundary_id not in known_ids:
                raise InvalidLandscapeSeedError(
                    f"{context}.boundary_ids includes unknown primitive {boundary_id!r}"
                )
    elif isinstance(primitive, PlateauSeedPrimitive):
        _validate_string_list(
            primitive.hosted_primitive_ids,
            context=f"{context}.hosted_primitive_ids",
        )
        for hosted_id in primitive.hosted_primitive_ids:
            if hosted_id not in known_ids:
                raise InvalidLandscapeSeedError(
                    f"{context}.hosted_primitive_ids includes unknown primitive {hosted_id!r}"
                )


def _validate_primitive(primitive: LandscapePrimitive, known_ids: set[str]) -> None:
    context = f"primitive[{primitive.id}]"
    _require_non_empty_string(primitive.id, context=f"{context}.id")
    if primitive.type not in LANDSCAPE_PRIMITIVE_TYPES:
        raise InvalidLandscapeSeedError(
            f"{context}.type must be one of {list(LANDSCAPE_PRIMITIVE_TYPES)}"
        )
    if primitive.label is not None:
        _require_non_empty_string(primitive.label, context=f"{context}.label")
    if primitive.role is not None:
        _require_non_empty_string(primitive.role, context=f"{context}.role")
    _validate_string_list(primitive.tags, context=f"{context}.tags")
    _validate_mapping(primitive.hints, context=f"{context}.hints")
    _validate_mapping(primitive.extensions, context=f"{context}.extensions")

    if isinstance(primitive, BasinSeedPrimitive | PlateauSeedPrimitive):
        _validate_basin_like(primitive, context=context, known_ids=known_ids)
        if primitive.parent_id is not None and primitive.parent_id not in known_ids:
            raise InvalidLandscapeSeedError(
                f"{context}.parent_id refers to unknown primitive {primitive.parent_id!r}"
            )
        if primitive.parent_id is None and primitive.depth_hint not in (None, 0):
            raise InvalidLandscapeSeedError(
                f"{context}.depth_hint must be 0 or omitted for root primitives"
            )
    elif isinstance(primitive, RidgeSeedPrimitive):
        if primitive.owner_id is not None and primitive.owner_id not in known_ids:
            raise InvalidLandscapeSeedError(
                f"{context}.owner_id refers to unknown primitive {primitive.owner_id!r}"
            )
        for adjacent_id in primitive.adjacent_ids:
            if adjacent_id not in known_ids:
                raise InvalidLandscapeSeedError(
                    f"{context}.adjacent_ids includes unknown primitive {adjacent_id!r}"
                )
        if primitive.interior_coherence_hint is not None:
            _require_real_number(
                primitive.interior_coherence_hint,
                context=f"{context}.interior_coherence_hint",
            )
        if primitive.exterior_coherence_hint is not None:
            _require_real_number(
                primitive.exterior_coherence_hint,
                context=f"{context}.exterior_coherence_hint",
            )
        if primitive.thickness_hint is not None:
            thickness = _require_real_number(
                primitive.thickness_hint,
                context=f"{context}.thickness_hint",
            )
            if thickness <= 0.0:
                raise InvalidLandscapeSeedError(f"{context}.thickness_hint must be > 0")
        _validate_chart_point(
            primitive.chart_principal_axis_hint,
            context=f"{context}.chart_principal_axis_hint",
        )
        _validate_mapping(
            primitive.anisotropy_hint,
            context=f"{context}.anisotropy_hint",
        )
        _validate_mapping(
            primitive.permeability_hint,
            context=f"{context}.permeability_hint",
        )
    elif isinstance(primitive, ValleySeedPrimitive):
        if primitive.from_id is None or primitive.to_id is None:
            raise InvalidLandscapeSeedError(f"{context} requires from_id and to_id")
        if primitive.from_id not in known_ids:
            raise InvalidLandscapeSeedError(
                f"{context}.from_id refers to unknown primitive {primitive.from_id!r}"
            )
        if primitive.to_id not in known_ids:
            raise InvalidLandscapeSeedError(
                f"{context}.to_id refers to unknown primitive {primitive.to_id!r}"
            )
        if primitive.width_hint is not None:
            width = _require_real_number(
                primitive.width_hint,
                context=f"{context}.width_hint",
            )
            if width <= 0.0:
                raise InvalidLandscapeSeedError(f"{context}.width_hint must be > 0")
        if primitive.coherence_prior is not None:
            _require_real_number(primitive.coherence_prior, context=f"{context}.coherence_prior")
        if primitive.path_hint is not None:
            _require_non_empty_string(primitive.path_hint, context=f"{context}.path_hint")
        if primitive.channel_role is not None:
            _require_non_empty_string(
                primitive.channel_role,
                context=f"{context}.channel_role",
            )
        if not isinstance(primitive.waypoints, list):
            raise InvalidLandscapeSeedError(f"{context}.waypoints must be a list")
        for index, waypoint in enumerate(primitive.waypoints):
            _validate_chart_point(waypoint, context=f"{context}.waypoints[{index}]")
    elif isinstance(primitive, JunctionSeedPrimitive):
        if primitive.type not in {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}:
            raise InvalidLandscapeSeedError(
                f"{context}.type must be junction or saddle for junction primitives"
            )
        if primitive.host_id is not None and primitive.host_id not in known_ids:
            raise InvalidLandscapeSeedError(
                f"{context}.host_id refers to unknown primitive {primitive.host_id!r}"
            )
        if (
            primitive.host_id is None
            and not primitive.branch_target_ids
            and not _is_observed_inference_primitive(primitive)
        ):
            raise InvalidLandscapeSeedError(
                f"{context} must provide host_id or at least one branch_target_ids entry"
            )
        for target_id in primitive.branch_target_ids:
            if target_id not in known_ids:
                raise InvalidLandscapeSeedError(
                    f"{context}.branch_target_ids includes unknown primitive {target_id!r}"
                )
        if primitive.coherence_prior is not None:
            _require_real_number(primitive.coherence_prior, context=f"{context}.coherence_prior")
        _validate_chart_point(
            primitive.chart_center_hint,
            context=f"{context}.chart_center_hint",
        )
    else:
        raise InvalidLandscapeSeedError(f"{context} has unsupported runtime primitive type")


def _is_observed_inference_primitive(primitive: LandscapePrimitive) -> bool:
    extension = primitive.extensions.get("landscape_inference")
    return isinstance(extension, dict) and extension.get("authority") == "observed"


def _validate_parent_hierarchy(seed: LandscapeSeed) -> None:
    parents: dict[str, str] = {}
    depth_hints: dict[str, int | None] = {}
    for primitive in seed.primitives:
        if isinstance(primitive, BasinSeedPrimitive | PlateauSeedPrimitive):
            if primitive.parent_id is not None:
                parents[primitive.id] = primitive.parent_id
            depth_hints[primitive.id] = primitive.depth_hint

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> int:
        if node_id in visited:
            cached_depth = depth_hints.get(node_id)
            return 0 if cached_depth is None else cached_depth
        if node_id in visiting:
            raise InvalidLandscapeSeedError("seed containment hierarchy must be acyclic")
        visiting.add(node_id)
        parent_id = parents.get(node_id)
        implied_depth = 0 if parent_id is None else visit(parent_id) + 1
        if depth_hints.get(node_id) is not None and depth_hints[node_id] != implied_depth:
            raise InvalidLandscapeSeedError(
                f"primitive[{node_id}].depth_hint contradicts parent-implied depth {implied_depth}"
            )
        visiting.remove(node_id)
        visited.add(node_id)
        return implied_depth

    for primitive_id in depth_hints:
        visit(primitive_id)


def _validate_transport_intent(item: SeedTransportIntent, known_ids: set[str]) -> None:
    _require_non_empty_string(item.id, context="transport_intent.id")
    _require_non_empty_string(item.mode, context=f"transport_intent[{item.id}].mode")
    _validate_string_list(item.sources, context=f"transport_intent[{item.id}].sources")
    _validate_string_list(item.targets, context=f"transport_intent[{item.id}].targets")
    for source in item.sources:
        if source not in known_ids:
            raise InvalidLandscapeSeedError(
                f"transport_intent[{item.id}].sources includes unknown primitive {source!r}"
            )
    for target in item.targets:
        if target not in known_ids:
            raise InvalidLandscapeSeedError(
                f"transport_intent[{item.id}].targets includes unknown primitive {target!r}"
            )
    if item.carrier_id is not None and item.carrier_id not in known_ids:
        raise InvalidLandscapeSeedError(
            f"transport_intent[{item.id}].carrier_id refers to unknown primitive {item.carrier_id!r}"
        )
    if item.magnitude_hint is not None:
        _require_real_number(
            item.magnitude_hint,
            context=f"transport_intent[{item.id}].magnitude_hint",
        )
    if item.priority is not None:
        _require_real_number(item.priority, context=f"transport_intent[{item.id}].priority")


def validate_landscape_seed(seed: LandscapeSeed) -> None:
    """Validate one normalized landscape seed runtime object."""

    _require_non_empty_string(seed.seed_schema, context="seed.seed_schema")
    _require_non_empty_string(seed.seed_version, context="seed.seed_version")
    _require_non_empty_string(seed.meta.name, context="seed.meta.name")
    _require_non_empty_string(seed.meta.source_kind, context="seed.meta.source_kind")
    if seed.meta.translation_mode is not None:
        _require_non_empty_string(
            seed.meta.translation_mode,
            context="seed.meta.translation_mode",
        )
    _validate_constitutive_profile(seed.constitutive_profile)
    if not isinstance(seed.primitives, list):
        raise InvalidLandscapeSeedError("seed.primitives must be a list")
    if not seed.primitives:
        if seed.meta.source_kind != INFERRED_OBSERVED_LANDSCAPE_SOURCE_KIND:
            raise InvalidLandscapeSeedError("seed.primitives must be a non-empty list")
        _validate_mapping(seed.extensions, context="seed.extensions")
        if "landscape_inference" not in seed.extensions:
            raise InvalidLandscapeSeedError(
                "empty inferred observed landscape seeds require extensions.landscape_inference"
            )
        if seed.geometry_hints is not None:
            _validate_geometry_hints(seed.geometry_hints)
        if not isinstance(seed.transport_intent, list) or seed.transport_intent:
            raise InvalidLandscapeSeedError(
                "empty inferred observed landscape seeds must not carry transport_intent"
            )
        return

    known_ids: set[str] = set()
    for primitive in seed.primitives:
        if primitive.id in known_ids:
            raise InvalidLandscapeSeedError(
                f"seed.primitives contains duplicate primitive id {primitive.id!r}"
            )
        known_ids.add(primitive.id)

    for primitive in seed.primitives:
        _validate_primitive(primitive, known_ids)

    _validate_parent_hierarchy(seed)

    if seed.geometry_hints is not None:
        _validate_geometry_hints(seed.geometry_hints)
    _validate_mapping(seed.extensions, context="seed.extensions")
    if not isinstance(seed.transport_intent, list):
        raise InvalidLandscapeSeedError("seed.transport_intent must be a list")
    for item in seed.transport_intent:
        _validate_transport_intent(item, known_ids)


__all__ = ["validate_landscape_seed"]

"""PDE landscape DSL to normalized seed translation boundary."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Any

from pygrc.core import InvalidLandscapeSeedError

from .seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_SADDLE,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
    TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
    ValleySeedPrimitive,
)
from .validation import validate_landscape_seed


PDE_TRANSLATOR_NAME = "pde_landscape_to_seed"
PDE_TRANSLATOR_VERSION = "0.1"
_GEOMETRY_SOURCE_CHARTS = {
    "euclidean": "planar_hint",
    "periodic_torus": "planar_periodic_hint",
}
_RIDGE_ANISOTROPY_KEYS = (
    "shape_mode",
    "anisotropy_ratio",
    "angular_modulation_amplitude",
    "angular_modulation_phase_deg",
    "distance_mode_override",
)
_AXIS_SNAP_ABS_TOL = 1e-12
_UNIT_BOX_ABS_TOL = 1e-9
_DERIVED_FLOAT_DECIMALS = 12


def _require_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise InvalidLandscapeSeedError(f"{context} must be a mapping")
    return dict(value)


def _require_list(value: Any, *, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise InvalidLandscapeSeedError(f"{context} must be a list")
    return list(value)


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


def _require_identifier(value: Any, *, context: str) -> str:
    identifier = _optional_string(value)
    if identifier is None:
        raise InvalidLandscapeSeedError(f"{context} must be a non-empty string")
    return identifier


def _as_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(f"{context} must be a float-compatible number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidLandscapeSeedError(f"{context} must be a finite real number")
    return number


def _normalize_derived_float(value: float) -> float:
    return round(value, _DERIVED_FLOAT_DECIMALS)


def _copy_extra_fields(
    source: Mapping[str, Any],
    consumed_keys: set[str],
) -> dict[str, Any]:
    return {
        key: deepcopy(value)
        for key, value in source.items()
        if key not in consumed_keys
    }


def _normalize_center(value: Any, *, context: str) -> list[float] | None:
    if value is None:
        return None
    points = _require_list(value, context=context)
    if len(points) != 2:
        raise InvalidLandscapeSeedError(f"{context} must contain exactly two coordinates")
    return [
        _as_float(points[0], context=f"{context}[0]"),
        _as_float(points[1], context=f"{context}[1]"),
    ]


def _normalize_waypoints(value: Any, *, context: str) -> list[list[float]]:
    if value is None:
        return []
    payload = _require_list(value, context=context)
    return [
        _normalize_center(point, context=f"{context}[{index}]")
        for index, point in enumerate(payload)
    ]


def _normalize_axis_from_orientation(orientation_deg: Any) -> list[float] | None:
    def normalize_component(value: float) -> float:
        if math.isclose(value, 0.0, rel_tol=0.0, abs_tol=_AXIS_SNAP_ABS_TOL):
            return 0.0
        if math.isclose(value, 1.0, rel_tol=0.0, abs_tol=_AXIS_SNAP_ABS_TOL):
            return 1.0
        if math.isclose(value, -1.0, rel_tol=0.0, abs_tol=_AXIS_SNAP_ABS_TOL):
            return -1.0
        return value

    if orientation_deg is None:
        return None
    theta = math.radians(_as_float(orientation_deg, context="ridge.orientation_deg"))
    return [
        normalize_component(math.cos(theta)),
        normalize_component(math.sin(theta)),
    ]


def _compute_depth_hints(primitives: list[LandscapePrimitive]) -> None:
    basin_like = {
        primitive.id: primitive
        for primitive in primitives
        if isinstance(primitive, BasinSeedPrimitive | PlateauSeedPrimitive)
    }

    visiting: set[str] = set()

    def visit(primitive_id: str) -> int:
        primitive = basin_like[primitive_id]
        if primitive.depth_hint is not None:
            return primitive.depth_hint
        if primitive_id in visiting:
            raise InvalidLandscapeSeedError(
                "source basin hierarchy must be acyclic for depth_hint derivation"
            )
        visiting.add(primitive_id)
        parent_id = primitive.parent_id
        if parent_id is None:
            depth = 0
        else:
            if parent_id not in basin_like:
                raise InvalidLandscapeSeedError(
                    f"basin parent {parent_id!r} does not name another translated basin"
                )
            depth = visit(parent_id) + 1
        primitive.depth_hint = depth
        visiting.remove(primitive_id)
        return depth

    for primitive_id in basin_like:
        visit(primitive_id)


def _record_translation_note(seed: LandscapeSeed, note: str) -> None:
    if note not in seed.meta.translation_notes:
        seed.meta.translation_notes.append(note)
    source_pde_extension = seed.extensions.setdefault("source_pde", {})
    translation_notes = source_pde_extension.setdefault("translation_notes", [])
    if note not in translation_notes:
        translation_notes.append(note)


def _translate_constitutive_profile(source: Mapping[str, Any]) -> SeedConstitutiveProfile:
    params = _require_mapping(source.get("params"), context="pde.params")
    potential_data = _require_mapping(source.get("potential"), context="pde.potential")

    budget_b: float | None = None
    compile_block = source.get("compile")
    if compile_block is not None:
        compile_mapping = _require_mapping(compile_block, context="pde.compile")
        mass_normalization = compile_mapping.get("mass_normalization")
        if mass_normalization is not None:
            mass_mapping = _require_mapping(
                mass_normalization,
                context="pde.compile.mass_normalization",
            )
            if mass_mapping.get("mode") == "target_mass" and "target" in mass_mapping:
                budget_b = _as_float(
                    mass_mapping["target"],
                    context="pde.compile.mass_normalization.target",
                )

    return SeedConstitutiveProfile(
        lambda_c=_as_float(params.get("lambda_C"), context="pde.params.lambda_C"),
        xi_c=_as_float(params.get("xi_C"), context="pde.params.xi_C"),
        zeta_c=_as_float(params.get("zeta_C"), context="pde.params.zeta_C"),
        kappa_c=_as_float(params.get("kappa_C"), context="pde.params.kappa_C"),
        dt=_as_float(params.get("dt"), context="pde.params.dt"),
        potential=SeedPotential(
            type=_require_identifier(potential_data.get("type"), context="pde.potential.type"),
            params=_require_mapping(
                potential_data.get("params", {}),
                context="pde.potential.params",
            ),
        ),
        budget_b=budget_b,
    )


def _translate_basin_primitive(source: Mapping[str, Any]) -> BasinSeedPrimitive:
    consumed = {"type", "name", "parent", "center", "radius", "coherence"}
    extras = _copy_extra_fields(source, consumed)
    extensions = {"source_pde": extras} if extras else {}
    radius = source.get("radius")
    chart_scale_hint: dict[str, Any] = {}
    if radius is not None:
        chart_scale_hint["radius"] = _as_float(radius, context="basin.radius")

    return BasinSeedPrimitive(
        id=_require_identifier(source.get("name"), context="basin.name"),
        parent_id=_optional_string(source.get("parent")),
        coherence_prior=(
            None
            if source.get("coherence") is None
            else _as_float(source.get("coherence"), context="basin.coherence")
        ),
        chart_center_hint=_normalize_center(source.get("center"), context="basin.center"),
        chart_scale_hint=chart_scale_hint,
        extensions=extensions,
    )


def _translate_plateau_primitive(source: Mapping[str, Any]) -> PlateauSeedPrimitive:
    consumed = {
        "type",
        "name",
        "parent",
        "center",
        "radius",
        "coherence",
        "depth_hint",
        "stability_class",
        "hosted_primitive_ids",
        "notes",
        "role",
        "label",
        "tags",
    }
    extras = _copy_extra_fields(source, consumed)
    extensions = {"source_pde": extras} if extras else {}
    radius = source.get("radius")
    chart_scale_hint: dict[str, Any] = {}
    if radius is not None:
        chart_scale_hint["radius"] = _as_float(radius, context="plateau.radius")

    hosted_primitive_ids = source.get("hosted_primitive_ids", [])
    hosted_ids: list[str] = []
    if hosted_primitive_ids is not None:
        hosted_ids = [
            _require_identifier(item, context=f"plateau.hosted_primitive_ids[{index}]")
            for index, item in enumerate(
                _require_list(hosted_primitive_ids, context="plateau.hosted_primitive_ids")
            )
        ]

    tags = source.get("tags", [])
    normalized_tags: list[str] = []
    if tags is not None:
        normalized_tags = [
            _require_identifier(item, context=f"plateau.tags[{index}]")
            for index, item in enumerate(_require_list(tags, context="plateau.tags"))
        ]

    depth_hint = source.get("depth_hint")
    normalized_depth_hint: int | None = None
    if depth_hint is not None:
        if not isinstance(depth_hint, int) or depth_hint < 0:
            raise InvalidLandscapeSeedError("plateau.depth_hint must be a non-negative int")
        normalized_depth_hint = depth_hint

    return PlateauSeedPrimitive(
        id=_require_identifier(source.get("name"), context="plateau.name"),
        label=_optional_string(source.get("label")),
        role=_optional_string(source.get("role")),
        tags=normalized_tags,
        parent_id=_optional_string(source.get("parent")),
        depth_hint=normalized_depth_hint,
        coherence_prior=(
            None
            if source.get("coherence") is None
            else _as_float(source.get("coherence"), context="plateau.coherence")
        ),
        chart_center_hint=_normalize_center(source.get("center"), context="plateau.center"),
        chart_scale_hint=chart_scale_hint,
        stability_class=_optional_string(source.get("stability_class")),
        hosted_primitive_ids=hosted_ids,
        notes=_optional_string(source.get("notes")),
        extensions=extensions,
    )


def _translate_ridge_primitive(source: Mapping[str, Any]) -> RidgeSeedPrimitive:
    consumed = {
        "type",
        "name",
        "parent",
        "ridge_type",
        "inner_radius",
        "outer_radius",
        "interior_coherence",
        "exterior_coherence",
        "orientation_deg",
        *_RIDGE_ANISOTROPY_KEYS,
    }
    extras = _copy_extra_fields(source, consumed)
    extensions = {"source_pde": extras} if extras else {}

    inner_radius = source.get("inner_radius")
    outer_radius = source.get("outer_radius")
    thickness_hint: float | None = None
    if inner_radius is not None and outer_radius is not None:
        outer_radius_value = _as_float(outer_radius, context="ridge.outer_radius")
        inner_radius_value = _as_float(inner_radius, context="ridge.inner_radius")
        if outer_radius_value <= inner_radius_value:
            raise InvalidLandscapeSeedError(
                "ridge.outer_radius must be greater than ridge.inner_radius"
            )
        thickness_hint = _normalize_derived_float(
            outer_radius_value - inner_radius_value
        )

    hints: dict[str, Any] = {}
    if inner_radius is not None:
        hints["inner_radius"] = _as_float(inner_radius, context="ridge.inner_radius")
    if outer_radius is not None:
        hints["outer_radius"] = _as_float(outer_radius, context="ridge.outer_radius")

    anisotropy_hint = {
        key: source[key]
        for key in _RIDGE_ANISOTROPY_KEYS
        if key in source
    }

    return RidgeSeedPrimitive(
        id=_require_identifier(source.get("name"), context="ridge.name"),
        owner_id=_optional_string(source.get("parent")),
        ridge_kind=_optional_string(source.get("ridge_type")),
        interior_coherence_hint=(
            None
            if source.get("interior_coherence") is None
            else _as_float(
                source.get("interior_coherence"),
                context="ridge.interior_coherence",
            )
        ),
        exterior_coherence_hint=(
            None
            if source.get("exterior_coherence") is None
            else _as_float(
                source.get("exterior_coherence"),
                context="ridge.exterior_coherence",
            )
        ),
        thickness_hint=thickness_hint,
        chart_principal_axis_hint=_normalize_axis_from_orientation(
            source.get("orientation_deg")
        ),
        anisotropy_hint=anisotropy_hint,
        hints=hints,
        extensions=extensions,
    )


def _translate_junction_primitive(
    source: Mapping[str, Any],
    *,
    primitive_type: str,
) -> JunctionSeedPrimitive:
    consumed = {
        "type",
        "name",
        "host_id",
        "branch_target_ids",
        "coherence",
        "center",
        "junction_role",
        "notes",
        "role",
        "label",
        "tags",
    }
    extras = _copy_extra_fields(source, consumed)
    extensions = {"source_pde": extras} if extras else {}

    branch_target_ids = source.get("branch_target_ids", [])
    branch_targets: list[str] = []
    if branch_target_ids is not None:
        branch_targets = [
            _require_identifier(item, context=f"{primitive_type}.branch_target_ids[{index}]")
            for index, item in enumerate(
                _require_list(branch_target_ids, context=f"{primitive_type}.branch_target_ids")
            )
        ]

    tags = source.get("tags", [])
    normalized_tags: list[str] = []
    if tags is not None:
        normalized_tags = [
            _require_identifier(item, context=f"{primitive_type}.tags[{index}]")
            for index, item in enumerate(_require_list(tags, context=f"{primitive_type}.tags"))
        ]

    return JunctionSeedPrimitive(
        id=_require_identifier(source.get("name"), context=f"{primitive_type}.name"),
        type=primitive_type,
        label=_optional_string(source.get("label")),
        role=_optional_string(source.get("role")),
        tags=normalized_tags,
        host_id=_optional_string(source.get("host_id")),
        branch_target_ids=branch_targets,
        junction_role=_optional_string(source.get("junction_role")),
        coherence_prior=(
            None
            if source.get("coherence") is None
            else _as_float(source.get("coherence"), context=f"{primitive_type}.coherence")
        ),
        chart_center_hint=_normalize_center(source.get("center"), context=f"{primitive_type}.center"),
        notes=_optional_string(source.get("notes")),
        extensions=extensions,
    )


def _translate_valley_primitive(source: Mapping[str, Any]) -> ValleySeedPrimitive:
    consumed = {
        "type",
        "name",
        "from",
        "to",
        "path_type",
        "width",
        "coherence",
        "control_points",
    }
    extras = _copy_extra_fields(source, consumed)
    extensions = {"source_pde": extras} if extras else {}
    return ValleySeedPrimitive(
        id=_require_identifier(source.get("name"), context="valley.name"),
        from_id=_optional_string(source.get("from")),
        to_id=_optional_string(source.get("to")),
        path_hint=_optional_string(source.get("path_type")),
        width_hint=(
            None
            if source.get("width") is None
            else _as_float(source.get("width"), context="valley.width")
        ),
        coherence_prior=(
            None
            if source.get("coherence") is None
            else _as_float(source.get("coherence"), context="valley.coherence")
        ),
        waypoints=_normalize_waypoints(
            source.get("control_points"),
            context="valley.control_points",
        ),
        extensions=extensions,
    )


def _translate_primitives(source: Mapping[str, Any]) -> list[LandscapePrimitive]:
    primitive_payloads = _require_list(source.get("primitives"), context="pde.primitives")
    translated: list[LandscapePrimitive] = []
    for index, item in enumerate(primitive_payloads):
        primitive = _require_mapping(item, context=f"pde.primitives[{index}]")
        primitive_type = _optional_string(primitive.get("type"))
        if primitive_type == "basin":
            translated.append(_translate_basin_primitive(primitive))
            continue
        if primitive_type == PRIMITIVE_PLATEAU:
            translated.append(_translate_plateau_primitive(primitive))
            continue
        if primitive_type == "ridge":
            translated.append(_translate_ridge_primitive(primitive))
            continue
        if primitive_type == "valley":
            translated.append(_translate_valley_primitive(primitive))
            continue
        if primitive_type in {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}:
            translated.append(
                _translate_junction_primitive(
                    primitive,
                    primitive_type=primitive_type,
                )
            )
            continue
        raise InvalidLandscapeSeedError(
            f"unsupported PDE primitive type {primitive_type!r}"
        )

    _compute_depth_hints(translated)
    return translated


def _translate_geometry_hints(source: Mapping[str, Any]) -> SeedGeometryHints | None:
    geometry = source.get("geometry")
    if geometry is None:
        return None

    geometry_mapping = _require_mapping(geometry, context="pde.geometry")
    distance_mode = _optional_string(geometry_mapping.get("distance_mode"))
    source_chart = _GEOMETRY_SOURCE_CHARTS.get(distance_mode)
    periodicity: dict[str, Any] = {}
    if "period_x" in geometry_mapping:
        periodicity["x"] = True
    if "period_y" in geometry_mapping:
        periodicity["y"] = True

    scale_units: str | None = None
    period_x = geometry_mapping.get("period_x")
    period_y = geometry_mapping.get("period_y")
    if (
        period_x is not None
        and period_y is not None
        and math.isclose(_as_float(period_x, context="pde.geometry.period_x"), 1.0, rel_tol=0.0, abs_tol=_UNIT_BOX_ABS_TOL)
        and math.isclose(_as_float(period_y, context="pde.geometry.period_y"), 1.0, rel_tol=0.0, abs_tol=_UNIT_BOX_ABS_TOL)
    ):
        scale_units = "unit_box"

    return SeedGeometryHints(
        source_chart=source_chart,
        periodicity=periodicity,
        scale_units=scale_units,
    )


def _resolve_transport_mode(direction: str | None, *, has_channels: bool) -> str | None:
    if direction == "source_to_sink":
        return "directed_bias"
    if direction == "custom":
        return "channel_preference" if has_channels else "directed_bias"
    if direction in {None, "none"}:
        return None
    raise InvalidLandscapeSeedError(
        f"pde.initial_flux.direction {direction!r} is not supported"
    )


def _resolve_channel_carrier(
    channel: Mapping[str, Any],
    valleys: list[ValleySeedPrimitive],
) -> str | None:
    if channel.get("type") != "valley":
        return None
    channel_name = _optional_string(channel.get("name"))
    if channel_name is not None and any(valley.id == channel_name for valley in valleys):
        return channel_name

    source_id = _optional_string(channel.get("from"))
    target_id = _optional_string(channel.get("to"))
    matches = [
        valley.id
        for valley in valleys
        if valley.from_id == source_id and valley.to_id == target_id
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise InvalidLandscapeSeedError(
            "pde.initial_flux valley channel carrier resolution is ambiguous for "
            f"{source_id!r} -> {target_id!r}"
        )
    return None


def _translate_transport_intent(
    source: Mapping[str, Any],
    primitives: list[LandscapePrimitive],
) -> list[SeedTransportIntent]:
    initial_flux = source.get("initial_flux")
    if initial_flux is None:
        return []

    flux_mapping = _require_mapping(initial_flux, context="pde.initial_flux")
    channels = _require_list(flux_mapping.get("channels", []), context="pde.initial_flux.channels")
    direction = _optional_string(flux_mapping.get("direction"))
    has_channels = len(channels) > 0
    mode = _resolve_transport_mode(direction, has_channels=has_channels)
    enabled = bool(flux_mapping.get("enabled", False))
    valleys = [
        primitive for primitive in primitives if isinstance(primitive, ValleySeedPrimitive)
    ]

    if not enabled and not has_channels:
        return []

    intents: list[SeedTransportIntent] = []
    if has_channels:
        for index, channel in enumerate(channels):
            channel_mapping = _require_mapping(
                channel,
                context=f"pde.initial_flux.channels[{index}]",
            )
            channel_id = _optional_string(channel_mapping.get("name")) or f"channel_{index}"
            source_id = _optional_string(channel_mapping.get("from"))
            target_id = _optional_string(channel_mapping.get("to"))
            magnitude_value = channel_mapping.get("weight", flux_mapping.get("magnitude"))
            magnitude_hint = None
            if magnitude_value is not None:
                magnitude_hint = _as_float(
                    magnitude_value,
                    context=f"pde.initial_flux.channels[{index}].weight",
                )
            intents.append(
                SeedTransportIntent(
                    id=channel_id,
                    mode=mode or "channel_preference",
                    sources=[] if source_id is None else [source_id],
                    targets=[] if target_id is None else [target_id],
                    magnitude_hint=magnitude_hint,
                    carrier_id=_resolve_channel_carrier(channel_mapping, valleys),
                    direction_hint=direction,
                )
            )
        return intents

    magnitude_hint = None
    if flux_mapping.get("magnitude") is not None:
        magnitude_hint = _as_float(
            flux_mapping["magnitude"],
            context="pde.initial_flux.magnitude",
        )
    return [
        SeedTransportIntent(
            id="initial_flux",
            mode=mode or "directed_bias",
            magnitude_hint=magnitude_hint,
            direction_hint=direction,
        )
    ]


def _annotate_source_implied_structures(seed: LandscapeSeed) -> None:
    basins = {
        primitive.id: primitive
        for primitive in seed.primitives
        if isinstance(primitive, BasinSeedPrimitive)
    }
    ridges_by_owner: dict[str, list[str]] = {}
    outgoing_valleys_by_source: dict[str, list[ValleySeedPrimitive]] = {}
    incoming_valleys_by_target: dict[str, list[ValleySeedPrimitive]] = {}

    for primitive in seed.primitives:
        if isinstance(primitive, RidgeSeedPrimitive) and primitive.owner_id is not None:
            ridges_by_owner.setdefault(primitive.owner_id, []).append(primitive.id)
        elif isinstance(primitive, ValleySeedPrimitive):
            if primitive.from_id is not None:
                outgoing_valleys_by_source.setdefault(primitive.from_id, []).append(primitive)
            if primitive.to_id is not None:
                incoming_valleys_by_target.setdefault(primitive.to_id, []).append(primitive)

    for basin_id, basin in basins.items():
        outgoing_valleys = outgoing_valleys_by_source.get(basin_id, [])
        incoming_valleys = incoming_valleys_by_target.get(basin_id, [])
        owned_ridges = ridges_by_owner.get(basin_id, [])
        if len(outgoing_valleys) < 2:
            continue

        source_pde_extension = basin.extensions.setdefault("source_pde", {})
        source_pde_extension["implied_role"] = "saddle_like_hub"
        source_pde_extension["implied_structure"] = {
            "outgoing_valley_ids": [valley.id for valley in outgoing_valleys],
            "incoming_valley_ids": [valley.id for valley in incoming_valleys],
            "owned_ridge_ids": owned_ridges,
        }
        note = (
            f"Routing hub {basin_id!r} is preserved conservatively as a basin "
            "with implied_role 'saddle_like_hub'; no explicit saddle primitive "
            "is synthesized in lossless_source_normalization mode."
        )
        _record_translation_note(seed, note)


def _build_source_pde_extension(
    source: Mapping[str, Any],
    *,
    meta: Mapping[str, Any],
) -> dict[str, Any]:
    source_meta_extension = {
        key: deepcopy(value)
        for key, value in meta.items()
        if key not in {"name", "description", "domain", "tags"}
    }
    extension: dict[str, Any] = {}
    if source_meta_extension:
        extension["meta"] = source_meta_extension
    if "geometry" in source:
        extension["geometry"] = deepcopy(
            _require_mapping(source["geometry"], context="pde.geometry")
        )
    if "compile" in source:
        extension["compile"] = deepcopy(
            _require_mapping(source["compile"], context="pde.compile")
        )
    potential = source.get("potential")
    if potential is not None:
        potential_mapping = _require_mapping(potential, context="pde.potential")
        compile_policy = potential_mapping.get("compile_policy")
        if compile_policy is not None:
            extension["potential_compile_policy"] = deepcopy(
                _require_mapping(
                    compile_policy,
                    context="pde.potential.compile_policy",
                )
            )
    if "initial_flux" in source:
        extension["initial_flux"] = deepcopy(
            _require_mapping(
                source["initial_flux"],
                context="pde.initial_flux",
            )
        )
    return extension


def translate_pde_landscape_data(
    source: Mapping[str, Any],
    *,
    source_reference: str | None = None,
    translator_version: str = PDE_TRANSLATOR_VERSION,
    translation_mode: str = TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
) -> LandscapeSeed:
    """Translate one PDE landscape mapping into one normalized seed object."""

    if translation_mode != TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION:
        raise InvalidLandscapeSeedError(
            "lossless_source_normalization is the only supported translation mode; "
            "semantic_enrichment remains deferred"
        )

    source_mapping = _require_mapping(source, context="pde landscape source")
    meta_mapping = _require_mapping(source_mapping.get("meta"), context="pde.meta")
    primitives = _translate_primitives(source_mapping)

    translated = LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(
            name=_require_identifier(meta_mapping.get("name"), context="pde.meta.name"),
            description=_optional_string(meta_mapping.get("description")),
            source_kind="pde_landscape_dsl",
            source_reference=source_reference,
            source_schema_version=_optional_string(source_mapping.get("schema_version")),
            source_domain=_optional_string(meta_mapping.get("domain")),
            tags=[
                normalized_tag
                for normalized_tag in (
                    _optional_string(tag)
                    for tag in _require_list(
                        meta_mapping.get("tags", []),
                        context="pde.meta.tags",
                    )
                )
                if normalized_tag is not None
            ],
            translator_name=PDE_TRANSLATOR_NAME,
            translator_version=translator_version,
            translation_mode=translation_mode,
        ),
        constitutive_profile=_translate_constitutive_profile(source_mapping),
        primitives=primitives,
        transport_intent=_translate_transport_intent(source_mapping, primitives),
        geometry_hints=_translate_geometry_hints(source_mapping),
        extensions={
            "source_pde": _build_source_pde_extension(source_mapping, meta=meta_mapping),
        },
    )
    _annotate_source_implied_structures(translated)
    validate_landscape_seed(translated)
    return translated


def translate_pde_landscape_json(
    path: str | Path,
    *,
    source_reference: str | None = None,
    translator_version: str = PDE_TRANSLATOR_VERSION,
    translation_mode: str = TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
) -> LandscapeSeed:
    """Translate one PDE landscape JSON file into one normalized seed object."""

    source_path = Path(path)
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InvalidLandscapeSeedError(
            f"failed to read PDE landscape JSON from {source_path}"
        ) from exc

    return translate_pde_landscape_data(
        payload,
        source_reference=source_reference or str(source_path),
        translator_version=translator_version,
        translation_mode=translation_mode,
    )


__all__ = [
    "PDE_TRANSLATOR_NAME",
    "PDE_TRANSLATOR_VERSION",
    "translate_pde_landscape_data",
    "translate_pde_landscape_json",
]

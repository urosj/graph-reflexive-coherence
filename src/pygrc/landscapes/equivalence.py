"""Executable PDE-to-seed translation equivalence checks."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from pygrc.core import (
    InvalidLandscapeSeedError,
    LandscapeTranslationEquivalenceError,
    canonicalize_json_value,
)

from .seed import (
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
    SeedTransportIntent,
    TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
    ValleySeedPrimitive,
)
from .validation import validate_landscape_seed


_RIDGE_ANISOTROPY_KEYS = (
    "shape_mode",
    "anisotropy_ratio",
    "angular_modulation_amplitude",
    "angular_modulation_phase_deg",
    "distance_mode_override",
)
_GEOMETRY_SOURCE_CHARTS = {
    "euclidean": "planar_hint",
    "periodic_torus": "planar_periodic_hint",
}
_UNIT_BOX_ABS_TOL = 1e-9


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


def _as_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(f"{context} must be a float-compatible number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidLandscapeSeedError(f"{context} must be a finite real number")
    return number


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise LandscapeTranslationEquivalenceError(message)


def _assert_float_equal(
    actual: float | None,
    expected: float | None,
    *,
    context: str,
    abs_tol: float = 1e-9,
) -> None:
    if actual is None or expected is None:
        _assert(actual is expected, f"{context} expected {expected!r}, got {actual!r}")
        return
    _assert(
        math.isclose(actual, expected, rel_tol=0.0, abs_tol=abs_tol),
        f"{context} expected {expected!r}, got {actual!r}",
    )


def _assert_point_equal(
    actual: list[float] | None,
    expected: list[float] | None,
    *,
    context: str,
) -> None:
    if actual is None or expected is None:
        _assert(actual is expected, f"{context} expected {expected!r}, got {actual!r}")
        return
    _assert(len(actual) == len(expected), f"{context} length mismatch")
    for index, (actual_value, expected_value) in enumerate(zip(actual, expected)):
        _assert_float_equal(
            actual_value,
            expected_value,
            context=f"{context}[{index}]",
        )


def _normalize_point_list(value: Any, *, context: str) -> list[float] | None:
    if value is None:
        return None
    payload = _require_list(value, context=context)
    _assert(len(payload) == 2, f"{context} must contain exactly two coordinates")
    return [
        _as_float(payload[0], context=f"{context}[0]"),
        _as_float(payload[1], context=f"{context}[1]"),
    ]


def _normalize_waypoints(value: Any, *, context: str) -> list[list[float]]:
    if value is None:
        return []
    payload = _require_list(value, context=context)
    return [
        _normalize_point_list(point, context=f"{context}[{index}]")
        for index, point in enumerate(payload)
    ]


def _expected_basin_depths(source: Mapping[str, Any]) -> dict[str, int]:
    primitive_payloads = _require_list(source.get("primitives"), context="pde.primitives")
    parents: dict[str, str | None] = {}
    for index, item in enumerate(primitive_payloads):
        primitive = _require_mapping(item, context=f"pde.primitives[{index}]")
        if _optional_string(primitive.get("type")) in {"basin", PRIMITIVE_PLATEAU}:
            name = _optional_string(primitive.get("name"))
            _assert(name is not None, f"pde.primitives[{index}].name must be present")
            parents[name] = _optional_string(primitive.get("parent"))

    visiting: set[str] = set()
    depths: dict[str, int] = {}

    def visit(primitive_id: str) -> int:
        if primitive_id in depths:
            return depths[primitive_id]
        if primitive_id in visiting:
            raise InvalidLandscapeSeedError(
                "source basin hierarchy must be acyclic for equivalence validation"
            )
        visiting.add(primitive_id)
        parent_id = parents[primitive_id]
        if parent_id is None:
            depth = 0
        else:
            _assert(
                parent_id in parents,
                f"source basin parent {parent_id!r} must name another source basin",
            )
            depth = visit(parent_id) + 1
        visiting.remove(primitive_id)
        depths[primitive_id] = depth
        return depth

    for primitive_id in parents:
        visit(primitive_id)
    return depths


def _build_seed_primitive_index(seed: LandscapeSeed) -> dict[str, LandscapePrimitive]:
    return {primitive.id: primitive for primitive in seed.primitives}


def _build_source_meta_extension(source_meta: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in source_meta.items()
        if key not in {"name", "description", "domain", "tags"}
    }


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


def _resolve_expected_carrier_id(
    channel: Mapping[str, Any],
    valleys: dict[str, ValleySeedPrimitive],
) -> str | None:
    if channel.get("type") != "valley":
        return None
    channel_name = _optional_string(channel.get("name"))
    if channel_name is not None and channel_name in valleys:
        return channel_name
    source_id = _optional_string(channel.get("from"))
    target_id = _optional_string(channel.get("to"))
    matches = [
        valley.id
        for valley in valleys.values()
        if valley.from_id == source_id and valley.to_id == target_id
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def _validate_constitutive_profile_equivalence(
    source: Mapping[str, Any],
    seed: LandscapeSeed,
) -> None:
    params = _require_mapping(source.get("params"), context="pde.params")
    potential = _require_mapping(source.get("potential"), context="pde.potential")

    _assert_float_equal(
        seed.constitutive_profile.lambda_c,
        _as_float(params.get("lambda_C"), context="pde.params.lambda_C"),
        context="constitutive_profile.lambda_c",
    )
    _assert_float_equal(
        seed.constitutive_profile.xi_c,
        _as_float(params.get("xi_C"), context="pde.params.xi_C"),
        context="constitutive_profile.xi_c",
    )
    _assert_float_equal(
        seed.constitutive_profile.zeta_c,
        _as_float(params.get("zeta_C"), context="pde.params.zeta_C"),
        context="constitutive_profile.zeta_c",
    )
    _assert_float_equal(
        seed.constitutive_profile.kappa_c,
        _as_float(params.get("kappa_C"), context="pde.params.kappa_C"),
        context="constitutive_profile.kappa_c",
    )
    _assert_float_equal(
        seed.constitutive_profile.dt,
        _as_float(params.get("dt"), context="pde.params.dt"),
        context="constitutive_profile.dt",
    )
    _assert(
        seed.constitutive_profile.potential.type == _optional_string(potential.get("type")),
        "constitutive_profile.potential.type mismatch",
    )
    _assert(
        canonicalize_json_value(seed.constitutive_profile.potential.params)
        == canonicalize_json_value(
            _require_mapping(potential.get("params", {}), context="pde.potential.params")
        ),
        "constitutive_profile.potential.params mismatch",
    )

    expected_budget: float | None = None
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
                expected_budget = _as_float(
                    mass_mapping["target"],
                    context="pde.compile.mass_normalization.target",
                )
    _assert_float_equal(
        seed.constitutive_profile.budget_b,
        expected_budget,
        context="constitutive_profile.budget_b",
    )


def _validate_meta_and_extension_equivalence(
    source: Mapping[str, Any],
    seed: LandscapeSeed,
    *,
    expected_source_reference: str | None,
) -> None:
    source_meta = _require_mapping(source.get("meta"), context="pde.meta")
    _assert(seed.meta.source_kind == "pde_landscape_dsl", "meta.source_kind mismatch")
    _assert(
        seed.meta.translation_mode == TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
        "meta.translation_mode must stay lossless_source_normalization",
    )
    _assert(seed.meta.name == _optional_string(source_meta.get("name")), "meta.name mismatch")
    _assert(
        seed.meta.description == _optional_string(source_meta.get("description")),
        "meta.description mismatch",
    )
    _assert(
        seed.meta.source_schema_version == _optional_string(source.get("schema_version")),
        "meta.source_schema_version mismatch",
    )
    _assert(
        seed.meta.source_domain == _optional_string(source_meta.get("domain")),
        "meta.source_domain mismatch",
    )
    _assert(
        canonicalize_json_value(seed.meta.tags)
        == canonicalize_json_value(_require_list(source_meta.get("tags", []), context="pde.meta.tags")),
        "meta.tags mismatch",
    )
    if expected_source_reference is not None:
        _assert(
            seed.meta.source_reference == expected_source_reference,
            "meta.source_reference mismatch",
        )

    source_extension = _require_mapping(
        seed.extensions.get("source_pde", {}),
        context="seed.extensions.source_pde",
    )
    _assert(
        canonicalize_json_value(source_extension.get("meta", {}))
        == canonicalize_json_value(_build_source_meta_extension(source_meta)),
        "extensions.source_pde.meta mismatch",
    )
    if "geometry" in source:
        _assert(
            canonicalize_json_value(source_extension.get("geometry"))
            == canonicalize_json_value(
                _require_mapping(source["geometry"], context="pde.geometry")
            ),
            "extensions.source_pde.geometry mismatch",
        )
    if "compile" in source:
        _assert(
            canonicalize_json_value(source_extension.get("compile"))
            == canonicalize_json_value(
                _require_mapping(source["compile"], context="pde.compile")
            ),
            "extensions.source_pde.compile mismatch",
        )
    potential = source.get("potential")
    if potential is not None:
        potential_mapping = _require_mapping(potential, context="pde.potential")
        compile_policy = potential_mapping.get("compile_policy", {})
        _assert(
            canonicalize_json_value(source_extension.get("potential_compile_policy", {}))
            == canonicalize_json_value(compile_policy),
            "extensions.source_pde.potential_compile_policy mismatch",
        )
    if "initial_flux" in source:
        _assert(
            canonicalize_json_value(source_extension.get("initial_flux"))
            == canonicalize_json_value(
                _require_mapping(source["initial_flux"], context="pde.initial_flux")
            ),
            "extensions.source_pde.initial_flux mismatch",
        )


def _validate_geometry_equivalence(source: Mapping[str, Any], seed: LandscapeSeed) -> None:
    geometry = source.get("geometry")
    if geometry is None:
        _assert(seed.geometry_hints is None, "geometry_hints should be omitted when source has no geometry")
        return

    geometry_mapping = _require_mapping(geometry, context="pde.geometry")
    _assert(seed.geometry_hints is not None, "geometry_hints missing for source geometry")
    expected_chart = _GEOMETRY_SOURCE_CHARTS.get(_optional_string(geometry_mapping.get("distance_mode")))
    _assert(
        seed.geometry_hints.source_chart == expected_chart,
        "geometry_hints.source_chart mismatch",
    )
    expected_periodicity: dict[str, Any] = {}
    if "period_x" in geometry_mapping:
        expected_periodicity["x"] = True
    if "period_y" in geometry_mapping:
        expected_periodicity["y"] = True
    _assert(
        canonicalize_json_value(seed.geometry_hints.periodicity)
        == canonicalize_json_value(expected_periodicity),
        "geometry_hints.periodicity mismatch",
    )

    expected_scale_units: str | None = None
    period_x = geometry_mapping.get("period_x")
    period_y = geometry_mapping.get("period_y")
    if (
        period_x is not None
        and period_y is not None
        and math.isclose(_as_float(period_x, context="pde.geometry.period_x"), 1.0, rel_tol=0.0, abs_tol=_UNIT_BOX_ABS_TOL)
        and math.isclose(_as_float(period_y, context="pde.geometry.period_y"), 1.0, rel_tol=0.0, abs_tol=_UNIT_BOX_ABS_TOL)
    ):
        expected_scale_units = "unit_box"
    _assert(
        seed.geometry_hints.scale_units == expected_scale_units,
        "geometry_hints.scale_units mismatch",
    )


def _validate_basin_equivalence(
    source_primitive: Mapping[str, Any],
    seed_primitive: BasinSeedPrimitive,
    *,
    expected_depth: int,
) -> None:
    _assert(seed_primitive.type == PRIMITIVE_BASIN, f"primitive[{seed_primitive.id}] type mismatch")
    _assert(
        seed_primitive.parent_id == _optional_string(source_primitive.get("parent")),
        f"primitive[{seed_primitive.id}].parent_id mismatch",
    )
    _assert_float_equal(
        seed_primitive.coherence_prior,
        None
        if source_primitive.get("coherence") is None
        else _as_float(source_primitive.get("coherence"), context="basin.coherence"),
        context=f"primitive[{seed_primitive.id}].coherence_prior",
    )
    _assert_point_equal(
        seed_primitive.chart_center_hint,
        _normalize_point_list(source_primitive.get("center"), context="basin.center"),
        context=f"primitive[{seed_primitive.id}].chart_center_hint",
    )
    expected_radius = None
    if source_primitive.get("radius") is not None:
        expected_radius = _as_float(source_primitive.get("radius"), context="basin.radius")
    _assert_float_equal(
        (
            None
            if "radius" not in seed_primitive.chart_scale_hint
            else float(seed_primitive.chart_scale_hint["radius"])
        ),
        expected_radius,
        context=f"primitive[{seed_primitive.id}].chart_scale_hint.radius",
    )
    _assert(
        seed_primitive.depth_hint == expected_depth,
        f"primitive[{seed_primitive.id}].depth_hint mismatch",
    )


def _validate_plateau_equivalence(
    source_primitive: Mapping[str, Any],
    seed_primitive: PlateauSeedPrimitive,
    *,
    expected_depth: int,
) -> None:
    _assert(seed_primitive.type == PRIMITIVE_PLATEAU, f"primitive[{seed_primitive.id}] type mismatch")
    _assert(
        seed_primitive.parent_id == _optional_string(source_primitive.get("parent")),
        f"primitive[{seed_primitive.id}].parent_id mismatch",
    )
    _assert_float_equal(
        seed_primitive.coherence_prior,
        None
        if source_primitive.get("coherence") is None
        else _as_float(source_primitive.get("coherence"), context="plateau.coherence"),
        context=f"primitive[{seed_primitive.id}].coherence_prior",
    )
    _assert_point_equal(
        seed_primitive.chart_center_hint,
        _normalize_point_list(source_primitive.get("center"), context="plateau.center"),
        context=f"primitive[{seed_primitive.id}].chart_center_hint",
    )
    expected_radius = None
    if source_primitive.get("radius") is not None:
        expected_radius = _as_float(source_primitive.get("radius"), context="plateau.radius")
    _assert_float_equal(
        (
            None
            if "radius" not in seed_primitive.chart_scale_hint
            else float(seed_primitive.chart_scale_hint["radius"])
        ),
        expected_radius,
        context=f"primitive[{seed_primitive.id}].chart_scale_hint.radius",
    )
    _assert(
        seed_primitive.depth_hint == expected_depth,
        f"primitive[{seed_primitive.id}].depth_hint mismatch",
    )
    _assert(
        seed_primitive.stability_class == _optional_string(source_primitive.get("stability_class")),
        f"primitive[{seed_primitive.id}].stability_class mismatch",
    )
    expected_hosted = source_primitive.get("hosted_primitive_ids", [])
    expected_hosted_ids = []
    if expected_hosted is not None:
        expected_hosted_ids = [
            _optional_string(item)
            for item in _require_list(expected_hosted, context="plateau.hosted_primitive_ids")
        ]
    _assert(
        seed_primitive.hosted_primitive_ids == expected_hosted_ids,
        f"primitive[{seed_primitive.id}].hosted_primitive_ids mismatch",
    )
    _assert(
        seed_primitive.role == _optional_string(source_primitive.get("role")),
        f"primitive[{seed_primitive.id}].role mismatch",
    )


def _validate_ridge_equivalence(
    source_primitive: Mapping[str, Any],
    seed_primitive: RidgeSeedPrimitive,
) -> None:
    _assert(seed_primitive.type == PRIMITIVE_RIDGE, f"primitive[{seed_primitive.id}] type mismatch")
    _assert(
        seed_primitive.owner_id == _optional_string(source_primitive.get("parent")),
        f"primitive[{seed_primitive.id}].owner_id mismatch",
    )
    _assert(
        seed_primitive.ridge_kind == _optional_string(source_primitive.get("ridge_type")),
        f"primitive[{seed_primitive.id}].ridge_kind mismatch",
    )
    _assert_float_equal(
        seed_primitive.interior_coherence_hint,
        None
        if source_primitive.get("interior_coherence") is None
        else _as_float(
            source_primitive.get("interior_coherence"),
            context="ridge.interior_coherence",
        ),
        context=f"primitive[{seed_primitive.id}].interior_coherence_hint",
    )
    _assert_float_equal(
        seed_primitive.exterior_coherence_hint,
        None
        if source_primitive.get("exterior_coherence") is None
        else _as_float(
            source_primitive.get("exterior_coherence"),
            context="ridge.exterior_coherence",
        ),
        context=f"primitive[{seed_primitive.id}].exterior_coherence_hint",
    )
    expected_thickness: float | None = None
    if source_primitive.get("inner_radius") is not None and source_primitive.get("outer_radius") is not None:
        expected_thickness = _as_float(
            source_primitive.get("outer_radius"),
            context="ridge.outer_radius",
        ) - _as_float(
            source_primitive.get("inner_radius"),
            context="ridge.inner_radius",
        )
    _assert_float_equal(
        seed_primitive.thickness_hint,
        expected_thickness,
        context=f"primitive[{seed_primitive.id}].thickness_hint",
    )
    expected_axis = None
    if source_primitive.get("orientation_deg") is not None:
        theta = math.radians(
            _as_float(source_primitive.get("orientation_deg"), context="ridge.orientation_deg")
        )
        expected_axis = [math.cos(theta), math.sin(theta)]
    _assert_point_equal(
        seed_primitive.chart_principal_axis_hint,
        expected_axis,
        context=f"primitive[{seed_primitive.id}].chart_principal_axis_hint",
    )
    expected_anisotropy = {
        key: source_primitive[key]
        for key in _RIDGE_ANISOTROPY_KEYS
        if key in source_primitive
    }
    _assert(
        canonicalize_json_value(seed_primitive.anisotropy_hint)
        == canonicalize_json_value(expected_anisotropy),
        f"primitive[{seed_primitive.id}].anisotropy_hint mismatch",
    )
    expected_hints: dict[str, Any] = {}
    if source_primitive.get("inner_radius") is not None:
        expected_hints["inner_radius"] = _as_float(
            source_primitive.get("inner_radius"),
            context="ridge.inner_radius",
        )
    if source_primitive.get("outer_radius") is not None:
        expected_hints["outer_radius"] = _as_float(
            source_primitive.get("outer_radius"),
            context="ridge.outer_radius",
        )
    _assert(
        canonicalize_json_value(seed_primitive.hints)
        == canonicalize_json_value(expected_hints),
        f"primitive[{seed_primitive.id}].hints mismatch",
    )


def _validate_valley_equivalence(
    source_primitive: Mapping[str, Any],
    seed_primitive: ValleySeedPrimitive,
) -> None:
    _assert(seed_primitive.type == PRIMITIVE_VALLEY, f"primitive[{seed_primitive.id}] type mismatch")
    _assert(
        seed_primitive.from_id == _optional_string(source_primitive.get("from")),
        f"primitive[{seed_primitive.id}].from_id mismatch",
    )
    _assert(
        seed_primitive.to_id == _optional_string(source_primitive.get("to")),
        f"primitive[{seed_primitive.id}].to_id mismatch",
    )
    _assert(
        seed_primitive.path_hint == _optional_string(source_primitive.get("path_type")),
        f"primitive[{seed_primitive.id}].path_hint mismatch",
    )
    _assert_float_equal(
        seed_primitive.width_hint,
        None
        if source_primitive.get("width") is None
        else _as_float(source_primitive.get("width"), context="valley.width"),
        context=f"primitive[{seed_primitive.id}].width_hint",
    )
    _assert_float_equal(
        seed_primitive.coherence_prior,
        None
        if source_primitive.get("coherence") is None
        else _as_float(source_primitive.get("coherence"), context="valley.coherence"),
        context=f"primitive[{seed_primitive.id}].coherence_prior",
    )
    _assert(
        canonicalize_json_value(seed_primitive.waypoints)
        == canonicalize_json_value(
            _normalize_waypoints(source_primitive.get("control_points"), context="valley.control_points")
        ),
        f"primitive[{seed_primitive.id}].waypoints mismatch",
    )


def _validate_junction_equivalence(
    source_primitive: Mapping[str, Any],
    seed_primitive: JunctionSeedPrimitive,
) -> None:
    source_type = _optional_string(source_primitive.get("type"))
    _assert(
        seed_primitive.type == source_type,
        f"primitive[{seed_primitive.id}].type mismatch",
    )
    _assert(
        seed_primitive.host_id == _optional_string(source_primitive.get("host_id")),
        f"primitive[{seed_primitive.id}].host_id mismatch",
    )
    expected_targets = source_primitive.get("branch_target_ids", [])
    expected_target_ids = []
    if expected_targets is not None:
        expected_target_ids = [
            _optional_string(item)
            for item in _require_list(expected_targets, context=f"{source_type}.branch_target_ids")
        ]
    _assert(
        seed_primitive.branch_target_ids == expected_target_ids,
        f"primitive[{seed_primitive.id}].branch_target_ids mismatch",
    )
    _assert(
        seed_primitive.junction_role == _optional_string(source_primitive.get("junction_role")),
        f"primitive[{seed_primitive.id}].junction_role mismatch",
    )
    _assert_float_equal(
        seed_primitive.coherence_prior,
        None
        if source_primitive.get("coherence") is None
        else _as_float(source_primitive.get("coherence"), context=f"{source_type}.coherence"),
        context=f"primitive[{seed_primitive.id}].coherence_prior",
    )
    _assert_point_equal(
        seed_primitive.chart_center_hint,
        _normalize_point_list(source_primitive.get("center"), context=f"{source_type}.center"),
        context=f"primitive[{seed_primitive.id}].chart_center_hint",
    )
    _assert(
        seed_primitive.role == _optional_string(source_primitive.get("role")),
        f"primitive[{seed_primitive.id}].role mismatch",
    )


def _validate_primitive_equivalence(source: Mapping[str, Any], seed: LandscapeSeed) -> None:
    seed_index = _build_seed_primitive_index(seed)
    source_primitives = _require_list(source.get("primitives"), context="pde.primitives")
    _assert(
        len(seed.primitives) == len(source_primitives),
        "lossless translation must preserve primitive count",
    )
    _assert(
        {primitive.id for primitive in seed.primitives}
        == {
            _optional_string(_require_mapping(item, context=f"pde.primitives[{index}]").get("name"))
            for index, item in enumerate(source_primitives)
        },
        "lossless translation must preserve primitive ids",
    )
    expected_depths = _expected_basin_depths(source)
    for index, item in enumerate(source_primitives):
        source_primitive = _require_mapping(item, context=f"pde.primitives[{index}]")
        primitive_id = _optional_string(source_primitive.get("name"))
        _assert(primitive_id is not None, f"pde.primitives[{index}].name must be present")
        seed_primitive = seed_index[primitive_id]
        source_type = _optional_string(source_primitive.get("type"))
        if source_type == "basin":
            _assert(isinstance(seed_primitive, BasinSeedPrimitive), f"primitive[{primitive_id}] must remain a basin")
            _validate_basin_equivalence(
                source_primitive,
                seed_primitive,
                expected_depth=expected_depths[primitive_id],
            )
            continue
        if source_type == PRIMITIVE_PLATEAU:
            _assert(
                isinstance(seed_primitive, PlateauSeedPrimitive),
                f"primitive[{primitive_id}] must remain a plateau",
            )
            _validate_plateau_equivalence(
                source_primitive,
                seed_primitive,
                expected_depth=expected_depths[primitive_id],
            )
            continue
        if source_type == "ridge":
            _assert(isinstance(seed_primitive, RidgeSeedPrimitive), f"primitive[{primitive_id}] must remain a ridge")
            _validate_ridge_equivalence(source_primitive, seed_primitive)
            continue
        if source_type == "valley":
            _assert(isinstance(seed_primitive, ValleySeedPrimitive), f"primitive[{primitive_id}] must remain a valley")
            _validate_valley_equivalence(source_primitive, seed_primitive)
            continue
        if source_type in {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}:
            _assert(
                isinstance(seed_primitive, JunctionSeedPrimitive),
                f"primitive[{primitive_id}] must remain a junction/saddle",
            )
            _validate_junction_equivalence(source_primitive, seed_primitive)
            continue
        raise InvalidLandscapeSeedError(f"unsupported PDE primitive type {source_type!r}")


def _validate_transport_equivalence(source: Mapping[str, Any], seed: LandscapeSeed) -> None:
    initial_flux = source.get("initial_flux")
    if initial_flux is None:
        _assert(seed.transport_intent == [], "transport_intent should be empty when source has no initial_flux")
        return

    flux_mapping = _require_mapping(initial_flux, context="pde.initial_flux")
    channels = _require_list(flux_mapping.get("channels", []), context="pde.initial_flux.channels")
    enabled = bool(flux_mapping.get("enabled", False))
    direction = _optional_string(flux_mapping.get("direction"))
    if not enabled and not channels:
        _assert(seed.transport_intent == [], "transport_intent should be empty when initial_flux is disabled and channel-free")
        return

    valleys = {
        primitive.id: primitive
        for primitive in seed.primitives
        if isinstance(primitive, ValleySeedPrimitive)
    }
    if channels:
        _assert(
            len(seed.transport_intent) == len(channels),
            "transport_intent count must match channel count",
        )
        for index, channel in enumerate(channels):
            channel_mapping = _require_mapping(
                channel,
                context=f"pde.initial_flux.channels[{index}]",
            )
            intent = seed.transport_intent[index]
            _assert(isinstance(intent, SeedTransportIntent), "transport_intent item type mismatch")
            expected_id = _optional_string(channel_mapping.get("name")) or f"channel_{index}"
            _assert(intent.id == expected_id, f"transport_intent[{index}].id mismatch")
            expected_mode = _resolve_transport_mode(direction, has_channels=True) or "channel_preference"
            _assert(intent.mode == expected_mode, f"transport_intent[{index}].mode mismatch")
            expected_source = _optional_string(channel_mapping.get("from"))
            expected_target = _optional_string(channel_mapping.get("to"))
            _assert(
                intent.sources == ([] if expected_source is None else [expected_source]),
                f"transport_intent[{index}].sources mismatch",
            )
            _assert(
                intent.targets == ([] if expected_target is None else [expected_target]),
                f"transport_intent[{index}].targets mismatch",
            )
            expected_magnitude = channel_mapping.get("weight", flux_mapping.get("magnitude"))
            _assert_float_equal(
                intent.magnitude_hint,
                None
                if expected_magnitude is None
                else _as_float(
                    expected_magnitude,
                    context=f"pde.initial_flux.channels[{index}].weight",
                ),
                context=f"transport_intent[{index}].magnitude_hint",
            )
            _assert(
                intent.carrier_id == _resolve_expected_carrier_id(channel_mapping, valleys),
                f"transport_intent[{index}].carrier_id mismatch",
            )
            _assert(
                intent.direction_hint == direction,
                f"transport_intent[{index}].direction_hint mismatch",
            )
        return

    _assert(len(seed.transport_intent) == 1, "transport_intent should contain one aggregate item")
    intent = seed.transport_intent[0]
    expected_mode = _resolve_transport_mode(direction, has_channels=False) or "directed_bias"
    _assert(intent.id == "initial_flux", "transport_intent[0].id mismatch")
    _assert(intent.mode == expected_mode, "transport_intent[0].mode mismatch")
    _assert_float_equal(
        intent.magnitude_hint,
        None
        if flux_mapping.get("magnitude") is None
        else _as_float(flux_mapping.get("magnitude"), context="pde.initial_flux.magnitude"),
        context="transport_intent[0].magnitude_hint",
    )
    _assert(intent.direction_hint == direction, "transport_intent[0].direction_hint mismatch")


def validate_pde_seed_translation_equivalence(
    source: Mapping[str, Any],
    seed: LandscapeSeed,
    *,
    expected_source_reference: str | None = None,
) -> None:
    """Validate executable seed-layer invariants between PDE source and one seed."""

    validate_landscape_seed(seed)
    source_mapping = _require_mapping(source, context="pde landscape source")
    _validate_meta_and_extension_equivalence(
        source_mapping,
        seed,
        expected_source_reference=expected_source_reference,
    )
    _validate_constitutive_profile_equivalence(source_mapping, seed)
    _validate_geometry_equivalence(source_mapping, seed)
    _validate_primitive_equivalence(source_mapping, seed)
    _validate_transport_equivalence(source_mapping, seed)


__all__ = ["validate_pde_seed_translation_equivalence"]

"""Family-local landscape projector boundary for seed-driven GRCV3 work."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, TypeAlias

from pygrc.core import GRCParams, InvalidLandscapeSeedError, StepResult, WeightedGraphBackend
from pygrc.landscapes import JunctionSeedPrimitive, LandscapeSeed, PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE
from pygrc.landscapes.extensions.grcv3 import (
    GRCV3RichBoundaryGeometry,
    GRCV3RichChannelGeometry,
    GRCV3RichInteriorGeometry,
    GRCV3RichInteriorLoadCarriers,
    GRCV3RichInteriorPartition,
    GRCV3RichPrimitiveExtension,
    GRCV3RichSeedExtension,
    GRCV3_RICH_V2_CONTRACT_VERSION,
    GRCV3_RICH_V3_CONTRACT_VERSION,
    GRCV3_RICH_V4_CONTRACT_VERSION,
    extract_grcv3_seed_extension,
)

from .grc_v2_landscape import (
    GRCV2LandscapeBlueprint,
    GRCV2LandscapeEdgeBlueprint,
    GRCV2LandscapeNodeBlueprint,
    _coerce_landscape_seed,
    _deep_merge_mapping,
    _edge_directionality_semantics,
    _edge_weight_from_blueprint,
    _euclidean_length,
    _freeze_optional_mapping,
    _required_node_mass,
    _site_potential_from_seed,
    _strict_seed_validation_mode,
    _to_plain_data,
    _transport_intent_metadata,
    get_grcv2_landscape_param_family,
    realize_grcv2_landscape_blueprint,
)
from .grc_v3 import GRCV3
from .grc_v3_landscape_native import (
    GRCV3NativeBasinLikePlan,
    GRCV3NativeJunctionPlan,
    GRCV3NativePrimitiveSurface,
    GRCV3NativeRidgePlan,
    GRCV3NativeValleyPlan,
    LOWERING_LANE_COMPATIBILITY,
    LOWERING_LANE_FAMILY_NATIVE,
    build_grcv3_native_primitive_surface,
    is_junction_like_primitive,
    lowering_blueprint_usage,
    lowering_semantic_authority,
    select_grcv3_lowering_lane,
)
from .grc_v3_state import BasinAttributes, GRCV3State

if TYPE_CHECKING:
    from pygrc.telemetry.recorder import TelemetryCaptureResult


LandscapeSeedInput: TypeAlias = LandscapeSeed | str | Path
GRCV3ParamsInput: TypeAlias = GRCParams | Mapping[str, Any]

DEFAULT_GRCV3_LANDSCAPE_PROFILE = "seed_baseline"
_GRCV3_GRCV2_ALIGNED_PROFILES = {
    "quiet_conservative",
    "balanced_baseline",
    "hot_exploratory",
    "precursor_sensitive",
    "commitment_dominant",
    "holdout_counterexample_locked",
}

_DEFAULT_PROJECTOR_RADIUS = 0.05
_BASIN_SUPPORT_RADIUS_SCALE = 0.45
_BASIN_SUPPORT_ANGLES = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
_BASIN_CENTER_MASS_FRACTION = 0.7
_JUNCTION_CENTER_MASS_FRACTION = 0.6
_RIDGE_SUPPORT_NODE_COUNT = 2
_RICH_SUPPORT_ARC_NODE_COUNT = 3
_CHANNEL_NODES_WITHOUT_WAYPOINTS = 1
_CHANNEL_NODES_WITH_WAYPOINTS = 2
_CARDINAL_BRANCH_ANGLES = {
    "east": 0.0,
    "northeast": math.pi / 4.0,
    "north": math.pi / 2.0,
    "northwest": 3.0 * math.pi / 4.0,
    "west": math.pi,
    "southwest": 5.0 * math.pi / 4.0,
    "south": 3.0 * math.pi / 2.0,
    "southeast": 7.0 * math.pi / 4.0,
}
_SUPPORT_PROFILE_RADIUS_MULTIPLIERS = {
    "tight": 0.72,
    "neutral": 1.0,
    "loose": 1.38,
}
_SUPPORT_PROFILE_SPOKE_MULTIPLIERS = {
    "tight": 0.85,
    "neutral": 0.75,
    "loose": 0.55,
}
_SUPPORT_CONNECTIVITY_WEIGHT_MULTIPLIERS = {
    "ring": 1.0,
    "paired_clamps": 1.1,
    "spindle": 1.25,
    "branch_only": 0.0,
}
_INTERIOR_CLEARANCE_SPOKE_SCALE = {
    "shielded": 0.45,
    "semi_open": 0.8,
    "through_loaded": 1.0,
}
_INTERIOR_CLEARANCE_SUPPORT_SCALE = {
    "shielded": 1.6,
    "semi_open": 1.0,
    "through_loaded": 0.8,
}
_PARTITION_PROBE_SHELL_RADIUS_SCALE = {
    "shielded": 1.55,
    "semi_open": 1.35,
    "open": 1.15,
}
_PARTITION_TRANSFER_WEIGHT_SCALE = {
    "support_mediated": 0.8,
    "clamp_mediated": 0.65,
    "transport_mediated": 0.65,
    "direct_open": 1.0,
}
_LOAD_CARRIER_RADIUS_SCALE = {
    "offset_ring": 1.18,
    "paired_tracks": 1.24,
    "staggered_arc": 1.16,
    "group_midpoints": 1.28,
}
_LOAD_CARRIER_TRANSFER_WEIGHT_SCALE = {
    "nearest_probe_role": 0.9,
    "group_bridge": 0.7,
    "cross_axis_bridge": 0.62,
    "paired_role_bridge": 0.78,
}
_TRANSFER_MEDIATION_MODE_WEIGHT_SCALE = {
    "attenuated_pairs": 0.82,
    "guarded_pairs": 0.68,
    "confined_pairs": 0.54,
}
_TRANSFER_MEDIATION_PAIR_CLASS_WEIGHT_SCALE = {
    "blocked": 0.0,
    "weak": 0.45,
    "medium": 0.78,
    "strong": 1.05,
}
_TRANSFER_MEDIATION_GUARD_SPOKE_SCALE = {
    "shell_only": 0.3,
    "guarded_center": 0.55,
    "open_center": 0.92,
}
_TRANSFER_MEDIATION_CENTER_COUPLING_SCALE = {
    "blocked": 0.0,
    "weak": 0.22,
    "medium": 0.55,
    "strong": 1.0,
}
_TRANSFER_MEDIATION_SPILL_SCALE = {
    "role_locked": 0.0,
    "axis_locked": 0.22,
    "open": 0.34,
}
_TRANSFER_PATH_NODE_MASS_SCALE = 0.8
_TRANSFER_PATH_EDGE_WEIGHT_SCALE = 1.0


@dataclass(frozen=True)
class _RealizedNodeSpec:
    source_primitive_id: str
    source_primitive_type: str
    realized_key: str
    role: str | None
    parent_id: str | None
    raw_mass: float
    chart_center_hint: tuple[float, float] | None
    chart_scale_hint: Mapping[str, Any]
    metadata: Mapping[str, Any]
    basin_id: str
    depth: int
    semantic_anchor: bool
    motif_role: str


@dataclass(frozen=True)
class _NativeStructuralEdgeSpec:
    source_node_id: int
    target_node_id: int
    edge_role: str
    load_group: str | None
    weight_multiplier: float
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class GRCV3LandscapeProjectionRequest:
    """Validated family-local projector input for seed-driven GRCV3 work."""

    seed: LandscapeSeed
    params: GRCParams
    seed_path: Path | None = None
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE


@dataclass(frozen=True)
class _GRCV3LoweringContext:
    request: GRCV3LandscapeProjectionRequest
    blueprint: GRCV2LandscapeBlueprint | None
    rich_seed_extension: GRCV3RichSeedExtension | None
    lowering_lane: str
    native_surface: GRCV3NativePrimitiveSurface | None


@dataclass
class GRCV3LandscapeRunResult:
    """Executable trajectory result for one seed-driven GRCV3 run."""

    request: GRCV3LandscapeProjectionRequest
    blueprint: GRCV2LandscapeBlueprint | None
    model: GRCV3
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    telemetry: TelemetryCaptureResult | None = None


def _coerce_grcv3_params(params: GRCV3ParamsInput) -> GRCParams:
    if isinstance(params, GRCParams):
        return params
    if not isinstance(params, Mapping):
        raise TypeError("params input must be a GRCParams instance or a mapping")
    return GRCV3.from_config(dict(params)).get_params()


def _grcv3_profile_name(profile_name: str) -> str:
    normalized = profile_name.strip()
    if normalized not in {DEFAULT_GRCV3_LANDSCAPE_PROFILE, *_GRCV3_GRCV2_ALIGNED_PROFILES}:
        raise InvalidLandscapeSeedError(
            f"unknown GRCV3 landscape profile {profile_name!r}; "
            "expected one of "
            f"{sorted({DEFAULT_GRCV3_LANDSCAPE_PROFILE, *_GRCV3_GRCV2_ALIGNED_PROFILES})!r}"
        )
    return normalized


def resolve_grcv3_landscape_params(
    seed: LandscapeSeedInput,
    *,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    overrides: Mapping[str, Any] | None = None,
    validate_seed: bool = True,
) -> GRCParams:
    """Resolve the seed-aligned baseline profile plus overrides into GRCV3 params."""

    resolved_seed, _ = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    normalized_profile_name = _grcv3_profile_name(profile_name)
    site_selection, site_params, site_projection_meta = _site_potential_from_seed(
        resolved_seed
    )
    if normalized_profile_name == DEFAULT_GRCV3_LANDSCAPE_PROFILE:
        config: dict[str, Any] = {
            "dt": float(resolved_seed.constitutive_profile.dt),
            "evolution": {
                "alpha": 1.0,
                "beta": 1.0,
                "gamma": 1.0,
                "delta": 1.0,
                "eta": 1.0,
                "kappa_c": float(resolved_seed.constitutive_profile.kappa_c),
                "lambda_c": float(resolved_seed.constitutive_profile.lambda_c),
                "xi_c": float(resolved_seed.constitutive_profile.xi_c),
                "zeta_c": float(resolved_seed.constitutive_profile.zeta_c),
                "eps_gradient": 1e-3,
                "eps_hessian": 1e-3,
                "eps_spark": 1e-3,
                "tau_split": 2.0,
                "site_potential_selection": site_selection,
                "site_potential_params": site_params,
            },
            "constitutive_semantic_modes": {
                "frame_mode": "induced_local_frame",
                "boundary_mode": "prune",
                "split_distribution_mode": "equal",
                "edge_label_selection": "all",
                "curvature_backend": "none",
            },
            "numerical_backend": {
                "landscape_param_profile": normalized_profile_name,
                "seed_potential_projection": site_projection_meta,
            },
        }
    else:
        family = get_grcv2_landscape_param_family(normalized_profile_name)
        activity = float(family.latent_axes["activity"])
        collapse_damping = float(family.latent_axes["collapse_damping"])
        closure_softness = float(family.latent_axes["closure_softness"])
        spark_sensitivity = float(family.latent_axes["spark_sensitivity"])
        config = {
            "dt": float(resolved_seed.constitutive_profile.dt),
            "evolution": {
                "alpha": 0.8 + 0.8 * closure_softness,
                "beta": 0.8 + 0.8 * closure_softness,
                "gamma": 0.7 + 1.1 * collapse_damping,
                "delta": 0.25 + 0.75 * collapse_damping,
                "eta": 0.8 + 0.8 * activity,
                "kappa_c": float(resolved_seed.constitutive_profile.kappa_c),
                "lambda_c": float(resolved_seed.constitutive_profile.lambda_c),
                "xi_c": float(resolved_seed.constitutive_profile.xi_c),
                "zeta_c": float(resolved_seed.constitutive_profile.zeta_c),
                "eps_gradient": 1e-3,
                "eps_hessian": 1e-3,
                "eps_spark": max(0.005, 0.12 - 0.10 * spark_sensitivity),
                "tau_split": max(1.0, 3.0 - 2.0 * activity),
                "site_potential_selection": site_selection,
                "site_potential_params": site_params,
            },
            "constitutive_semantic_modes": {
                "frame_mode": "induced_local_frame",
                "boundary_mode": "prune",
                "split_distribution_mode": "equal",
                "edge_label_selection": "all",
                "curvature_backend": "none",
            },
            "numerical_backend": {
                "landscape_param_profile": normalized_profile_name,
                "landscape_param_axes": dict(family.latent_axes),
                "profile_alignment_source": "grcv2_family_envelope",
                "profile_alignment_note": (
                    "shared envelope coefficients are aligned to the GRCV2 family, "
                    "but geometry backend remains GRCV3-native induced_local_frame "
                    "because combinatorial geometry is not yet executable in GRCV3"
                ),
                "seed_potential_projection": site_projection_meta,
            },
        }
    if overrides is not None:
        config = _deep_merge_mapping(config, overrides)
    return _coerce_grcv3_params(config)


def prepare_grcv3_landscape_projection(
    seed: LandscapeSeedInput,
    *,
    params: GRCV3ParamsInput,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    validate_seed: bool = True,
) -> GRCV3LandscapeProjectionRequest:
    """Normalize seed and params into one validated family-local request."""

    resolved_seed, seed_path = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    resolved_params = _coerce_grcv3_params(params)
    return GRCV3LandscapeProjectionRequest(
        seed=resolved_seed,
        params=resolved_params,
        seed_path=seed_path,
        profile_name=_grcv3_profile_name(profile_name),
    )


def _build_native_runtime_blueprint(
    native_surface: GRCV3NativePrimitiveSurface,
) -> GRCV2LandscapeBlueprint:
    node_blueprints: list[GRCV2LandscapeNodeBlueprint] = []
    for primitive_id in native_surface.node_carrier_ids:
        if primitive_id in native_surface.basin_like_plans:
            plan = native_surface.basin_like_plans[primitive_id]
            node_blueprints.append(
                GRCV2LandscapeNodeBlueprint(
                    primitive_id=plan.primitive_id,
                    primitive_type=plan.primitive_type,
                    role=plan.role,
                    parent_id=plan.parent_id,
                    coherence_prior=plan.coherence_prior,
                    chart_center_hint=plan.chart_center_hint,
                    chart_scale_hint=plan.chart_scale_hint,
                    metadata=MappingProxyType(
                        {
                            "boundary_ids": tuple(plan.boundary_ids),
                            "hosted_primitive_ids": tuple(plan.hosted_primitive_ids),
                            "grcv3_native_lowering": True,
                        }
                    ),
                )
            )
            continue
        plan = native_surface.junction_plans[primitive_id]
        node_blueprints.append(
            GRCV2LandscapeNodeBlueprint(
                primitive_id=plan.primitive_id,
                primitive_type=plan.primitive_type,
                role=plan.role,
                parent_id=plan.parent_id,
                coherence_prior=plan.coherence_prior,
                chart_center_hint=plan.chart_center_hint,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=MappingProxyType(
                    {
                        "host_id": plan.host_id,
                        "is_hostless": plan.hostless,
                        "junction_anchor_mode": "standalone" if plan.hostless else "hosted",
                        "branch_target_ids": tuple(plan.branch_target_ids),
                        "junction_role": plan.junction_role,
                        "grcv3_native_lowering": True,
                    }
                ),
            )
        )
    edge_blueprints: list[GRCV2LandscapeEdgeBlueprint] = []
    for primitive_id in native_surface.edge_carrier_ids:
        if primitive_id in native_surface.valley_plans:
            plan = native_surface.valley_plans[primitive_id]
            edge_blueprints.append(
                GRCV2LandscapeEdgeBlueprint(
                    primitive_id=plan.primitive_id,
                    primitive_type=plan.primitive_type,
                    source_primitive_id=plan.source_primitive_id,
                    target_primitive_id=plan.target_primitive_id,
                    coherence_prior=plan.coherence_prior,
                    width_hint=plan.width_hint,
                    path_hint=plan.path_hint,
                    role=plan.role,
                    metadata=MappingProxyType(
                        {
                            "waypoints": tuple(plan.waypoints),
                            "channel_role": plan.channel_role,
                            "grcv3_native_lowering": True,
                        }
                    ),
                )
            )
            continue
        plan = native_surface.ridge_plans[primitive_id]
        edge_blueprints.append(
            GRCV2LandscapeEdgeBlueprint(
                primitive_id=plan.primitive_id,
                primitive_type=plan.primitive_type,
                source_primitive_id=plan.source_primitive_id,
                target_primitive_id=(
                    plan.source_primitive_id
                    if plan.target_primitive_id is None
                    else plan.target_primitive_id
                ),
                coherence_prior=None,
                width_hint=plan.thickness_hint,
                path_hint="ridge_support_arc",
                role=plan.role,
                metadata=MappingProxyType(
                    {
                        "interior_coherence_hint": plan.interior_coherence_hint,
                        "exterior_coherence_hint": plan.exterior_coherence_hint,
                        "adjacent_ids": tuple(plan.adjacent_ids),
                        "grcv3_native_lowering": True,
                    }
                ),
            )
        )
    return GRCV2LandscapeBlueprint(
        node_blueprints=tuple(node_blueprints),
        edge_blueprints=tuple(edge_blueprints),
        ridge_ids_by_owner=native_surface.ridge_ids_by_owner,
        metadata_only_ridge_ids=native_surface.metadata_only_ridge_ids,
        node_primitive_ids=tuple(blueprint.primitive_id for blueprint in node_blueprints),
        edge_primitive_ids=tuple(blueprint.primitive_id for blueprint in edge_blueprints),
    )


def _resolve_grcv3_lowering_context(
    seed: LandscapeSeedInput,
    *,
    params: GRCV3ParamsInput,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    validate_seed: bool = True,
) -> _GRCV3LoweringContext:
    request = prepare_grcv3_landscape_projection(
        seed,
        params=params,
        profile_name=profile_name,
        validate_seed=validate_seed,
    )
    rich_seed_extension = extract_grcv3_seed_extension(request.seed)
    lowering_lane = select_grcv3_lowering_lane(rich_seed_extension)
    native_surface = (
        None
        if lowering_lane != LOWERING_LANE_FAMILY_NATIVE or rich_seed_extension is None
        else build_grcv3_native_primitive_surface(
            request.seed,
            rich_seed_extension=rich_seed_extension,
        )
    )
    blueprint = (
        _build_native_runtime_blueprint(native_surface)
        if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None
        else realize_grcv2_landscape_blueprint(request.seed, validate_seed=False)
    )
    return _GRCV3LoweringContext(
        request=request,
        blueprint=blueprint,
        rich_seed_extension=rich_seed_extension,
        lowering_lane=lowering_lane,
        native_surface=native_surface,
    )


def _edge_label_modes(frame_mode: str) -> dict[str, str]:
    geometric_length_mode = (
        "ambient_metric" if frame_mode == "host_embedding" else "induced_intrinsic"
    )
    return {
        "geometric_length": geometric_length_mode,
        "temporal_delay": "transport_ratio",
        "flux_coupling": "absolute_flux",
    }


def _primitive_radius(chart_scale_hint: Mapping[str, Any]) -> float:
    radius = chart_scale_hint.get("radius")
    if isinstance(radius, int | float) and float(radius) > 0.0:
        return float(radius)
    return _DEFAULT_PROJECTOR_RADIUS


def _offset_point(
    center: tuple[float, float] | None,
    *,
    radius: float,
    angle: float,
) -> tuple[float, float] | None:
    if center is None:
        return None
    return (
        float(center[0] + radius * math.cos(angle)),
        float(center[1] + radius * math.sin(angle)),
    )


def _midpoint(
    point_a: tuple[float, float] | None,
    point_b: tuple[float, float] | None,
) -> tuple[float, float] | None:
    if point_a is None or point_b is None:
        return None
    return ((point_a[0] + point_b[0]) * 0.5, (point_a[1] + point_b[1]) * 0.5)


def _point_distance_squared(
    point_a: tuple[float, float] | None,
    point_b: tuple[float, float] | None,
) -> float:
    if point_a is None or point_b is None:
        return float("inf")
    dx = float(point_a[0] - point_b[0])
    dy = float(point_a[1] - point_b[1])
    return dx * dx + dy * dy


def _branch_angles_for_order(branch_order: tuple[str, ...]) -> tuple[float, ...]:
    normalized_roles = tuple(role.strip().lower() for role in branch_order)
    if all(role in _CARDINAL_BRANCH_ANGLES for role in normalized_roles):
        return tuple(_CARDINAL_BRANCH_ANGLES[role] for role in normalized_roles)
    if not branch_order:
        return ()
    step = 2.0 * math.pi / float(len(branch_order))
    return tuple(float(index) * step for index in range(len(branch_order)))


def _angles_for_role_order(role_order: tuple[str, ...]) -> tuple[float, ...]:
    return _branch_angles_for_order(role_order)


def _rich_extension_for_primitive(
    rich_seed_extension: GRCV3RichSeedExtension | None,
    primitive_id: str,
) -> GRCV3RichPrimitiveExtension | None:
    if rich_seed_extension is None:
        return None
    return rich_seed_extension.primitive_extensions.get(primitive_id)


def _role_sequence_for_primitive_extension(
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
) -> tuple[str, ...]:
    if rich_primitive_extension is None:
        return ()
    if (
        rich_primitive_extension.local_geometry is not None
        and rich_primitive_extension.local_geometry.axis_roles
    ):
        return rich_primitive_extension.local_geometry.axis_roles
    if rich_primitive_extension.realization is not None:
        return rich_primitive_extension.realization.branch_order
    return ()


def _role_angle_map_for_primitive_extension(
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
) -> dict[str, float]:
    role_order = _role_sequence_for_primitive_extension(rich_primitive_extension)
    if not role_order:
        return {}
    angles = _angles_for_role_order(role_order)
    return {
        str(role): float(angle)
        for role, angle in zip(role_order, angles, strict=False)
    }


def _normalize_arc_span_radians(arc_span: float | str) -> float:
    if isinstance(arc_span, int | float):
        return max(0.05, float(arc_span) * math.pi)
    normalized = str(arc_span).strip().lower()
    qualitative_map = {
        "tight": math.pi / 6.0,
        "medium": math.pi / 4.0,
        "wide": math.pi / 3.0,
    }
    return float(qualitative_map.get(normalized, math.pi / 4.0))


def _sample_polyline_points(
    polyline: list[tuple[float, float] | None],
    *,
    count: int,
) -> list[tuple[float, float] | None]:
    if count <= 0:
        return []
    valid_points = [point for point in polyline if point is not None]
    if len(valid_points) < 2:
        return [valid_points[0] if valid_points else None for _ in range(count)]
    segment_lengths: list[float] = []
    cumulative = [0.0]
    for point_a, point_b in zip(valid_points[:-1], valid_points[1:], strict=False):
        dx = float(point_b[0] - point_a[0])
        dy = float(point_b[1] - point_a[1])
        length = math.sqrt(dx * dx + dy * dy)
        segment_lengths.append(length)
        cumulative.append(cumulative[-1] + length)
    total_length = cumulative[-1]
    if total_length <= 1e-12:
        return [valid_points[0] for _ in range(count)]
    samples: list[tuple[float, float] | None] = []
    for sample_index in range(count):
        distance = total_length * float(sample_index + 1) / float(count + 1)
        segment_index = 0
        while segment_index + 1 < len(cumulative) and cumulative[segment_index + 1] < distance:
            segment_index += 1
        start_point = valid_points[segment_index]
        end_point = valid_points[min(segment_index + 1, len(valid_points) - 1)]
        segment_start = cumulative[segment_index]
        segment_length = max(1e-12, segment_lengths[min(segment_index, len(segment_lengths) - 1)])
        ratio = (distance - segment_start) / segment_length
        samples.append(
            (
                float(start_point[0] + (end_point[0] - start_point[0]) * ratio),
                float(start_point[1] + (end_point[1] - start_point[1]) * ratio),
            )
        )
    return samples


def _primitive_depth_index(seed: LandscapeSeed) -> dict[str, int]:
    return {
        primitive.id: int(primitive.depth_hint)
        for primitive in seed.primitives
        if getattr(primitive, "depth_hint", None) is not None
    }


def _primitive_index(seed: LandscapeSeed) -> dict[str, Any]:
    return {primitive.id: primitive for primitive in seed.primitives}


def _realized_node_metadata(
    blueprint_node: GRCV2LandscapeNodeBlueprint,
    *,
    motif_role: str,
    motif_index: int,
    semantic_anchor: bool,
    extra_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _realized_node_metadata_from_source(
        source_role=blueprint_node.role,
        source_metadata=blueprint_node.metadata,
        motif_role=motif_role,
        motif_index=motif_index,
        semantic_anchor=semantic_anchor,
        extra_metadata=extra_metadata,
    )


def _realized_node_metadata_from_source(
    *,
    source_role: str | None,
    source_metadata: Mapping[str, Any],
    motif_role: str,
    motif_index: int,
    semantic_anchor: bool,
    extra_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {
        "motif_role": motif_role,
        "motif_index": motif_index,
        "semantic_anchor": semantic_anchor,
        "source_role": source_role,
        "source_metadata": _to_plain_data(source_metadata),
    }
    if extra_metadata is not None:
        metadata.update({str(key): _to_plain_data(value) for key, value in extra_metadata.items()})
    return metadata


def _required_native_node_mass(
    primitive_id: str,
    coherence_prior: float | None,
) -> float:
    if coherence_prior is None:
        raise InvalidLandscapeSeedError(
            f"node-carrying primitive {primitive_id!r} requires coherence_prior "
            "for GRCV3 native lowering initialization"
        )
    return float(coherence_prior)


def _build_basin_patch_specs(
    primitive: Any,
    blueprint_node: GRCV2LandscapeNodeBlueprint,
    *,
    depth: int,
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None = None,
    rich_contract_version: str | None = None,
) -> list[_RealizedNodeSpec]:
    primitive_mass = _required_node_mass(blueprint_node)
    center_mass = primitive_mass * _BASIN_CENTER_MASS_FRACTION
    primitive_radius = _primitive_radius(blueprint_node.chart_scale_hint)
    support_radius = max(1e-6, primitive_radius * _BASIN_SUPPORT_RADIUS_SCALE)
    role_order = _role_sequence_for_primitive_extension(rich_primitive_extension)
    support_angles = (
        _angles_for_role_order(role_order)
        if role_order and rich_contract_version == GRCV3_RICH_V2_CONTRACT_VERSION
        else _BASIN_SUPPORT_ANGLES
    )
    support_mass = (primitive_mass - center_mass) / float(len(support_angles))
    center_extra_metadata: dict[str, Any] = {
        "projector_radius": primitive_radius,
        "support_radius": support_radius,
    }
    if rich_primitive_extension is not None and rich_contract_version is not None:
        center_extra_metadata.update(
            {
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_rich_role_order": role_order,
                "grcv3_rich_center_role": (
                    None
                    if rich_primitive_extension.local_geometry is None
                    else rich_primitive_extension.local_geometry.center_role
                ),
                "grcv3_rich_symmetry_class": (
                    None
                    if rich_primitive_extension.local_geometry is None
                    else rich_primitive_extension.local_geometry.symmetry_class
                ),
                "grcv3_rich_curvature_class": (
                    None
                    if rich_primitive_extension.curvature_intent is None
                    else rich_primitive_extension.curvature_intent.curvature_class
                ),
                "grcv3_rich_stable_axis_roles": (
                    ()
                    if rich_primitive_extension.curvature_intent is None
                    else rich_primitive_extension.curvature_intent.stable_axis_roles
                ),
                "grcv3_rich_preferred_attachment_sites": (
                    {}
                    if rich_primitive_extension.interfaces is None
                    else dict(rich_primitive_extension.interfaces.preferred_attachment_sites)
                ),
            }
        )
    center_metadata = _realized_node_metadata(
        blueprint_node,
        motif_role="basin_center",
        motif_index=0,
        semantic_anchor=True,
        extra_metadata=center_extra_metadata,
    )
    realized_specs = [
        _RealizedNodeSpec(
            source_primitive_id=blueprint_node.primitive_id,
            source_primitive_type=blueprint_node.primitive_type,
            realized_key=f"{blueprint_node.primitive_id}::center",
            role=blueprint_node.role,
            parent_id=blueprint_node.parent_id,
            raw_mass=float(center_mass),
            chart_center_hint=blueprint_node.chart_center_hint,
            chart_scale_hint=blueprint_node.chart_scale_hint,
            metadata=center_metadata,
            basin_id=blueprint_node.primitive_id,
            depth=depth,
            semantic_anchor=True,
            motif_role="basin_center",
        )
    ]
    for index, angle in enumerate(support_angles):
        support_point = _offset_point(
            blueprint_node.chart_center_hint,
            radius=support_radius,
            angle=angle,
        )
        role_label = (
            None
            if not role_order
            else role_order[index]
        )
        support_metadata = _realized_node_metadata(
            blueprint_node,
            motif_role="basin_support",
            motif_index=index,
            semantic_anchor=False,
            extra_metadata={
                "projector_radius": primitive_radius,
                "support_radius": support_radius,
                "support_angle": angle,
                "source_extensions": _to_plain_data(getattr(primitive, "extensions", {})),
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": rich_primitive_extension is not None,
                "grcv3_role_label": role_label,
                "grcv3_rich_curvature_class": (
                    None
                    if rich_primitive_extension is None
                    or rich_primitive_extension.curvature_intent is None
                    else rich_primitive_extension.curvature_intent.curvature_class
                ),
                "grcv3_rich_weak_axis_role": (
                    None
                    if rich_primitive_extension is None
                    or rich_primitive_extension.local_geometry is None
                    else rich_primitive_extension.local_geometry.weak_axis_role
                ),
            },
        )
        realized_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=blueprint_node.primitive_id,
                source_primitive_type=blueprint_node.primitive_type,
                realized_key=f"{blueprint_node.primitive_id}::support:{index}",
                role=blueprint_node.role,
                parent_id=blueprint_node.parent_id,
                raw_mass=float(support_mass),
                chart_center_hint=support_point,
                chart_scale_hint=blueprint_node.chart_scale_hint,
                metadata=support_metadata,
                basin_id=blueprint_node.primitive_id,
                depth=depth,
                semantic_anchor=False,
                motif_role="basin_support",
            )
        )
    return realized_specs


def _build_native_basin_patch_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    rich_contract_version: str,
) -> list[_RealizedNodeSpec]:
    primitive_mass = _required_native_node_mass(plan.primitive_id, plan.coherence_prior)
    center_mass = primitive_mass * _BASIN_CENTER_MASS_FRACTION
    primitive_radius = _primitive_radius(plan.chart_scale_hint)
    support_angles = (
        _angles_for_role_order(plan.role_order)
        if plan.role_order
        else _BASIN_SUPPORT_ANGLES
    )
    interior_partition = plan.interior_partition
    interior_load_carriers = plan.interior_load_carriers
    support_shell_count = len(support_angles)
    load_shell_count = (
        0
        if interior_partition is None or not plan.role_order
        else len(plan.role_order)
    )
    remaining_mass = primitive_mass - center_mass
    total_shell_slots = max(1, support_shell_count + load_shell_count)
    support_mass = remaining_mass / float(total_shell_slots)
    interior_geometry = plan.interior_geometry
    support_role_group_by_role = _native_support_role_group_by_role(interior_geometry)
    partition_load_group_by_role = _native_partition_load_group_by_role(interior_partition)
    center_metadata = _realized_node_metadata_from_source(
        source_role=plan.role,
        source_metadata={},
        motif_role="basin_center",
        motif_index=0,
        semantic_anchor=True,
        extra_metadata={
            "projector_radius": primitive_radius,
            "support_radius": max(1e-6, primitive_radius * _BASIN_SUPPORT_RADIUS_SCALE),
            "grcv3_rich_contract_version": rich_contract_version,
            "grcv3_rich": True,
            "grcv3_rich_role_order": plan.role_order,
            "grcv3_rich_center_role": plan.center_role,
            "grcv3_rich_symmetry_class": plan.symmetry_class,
            "grcv3_rich_curvature_class": plan.curvature_class,
            "grcv3_rich_stable_axis_roles": plan.stable_axis_roles,
            "grcv3_rich_preferred_attachment_sites": dict(plan.preferred_attachment_sites),
            "grcv3_rich_interior_probe_mode": (
                None if interior_geometry is None else interior_geometry.probe_mode
            ),
            "grcv3_rich_attachment_isolation": (
                None if interior_geometry is None else interior_geometry.attachment_isolation
            ),
            "grcv3_rich_interior_clearance_class": (
                None
                if interior_geometry is None
                else interior_geometry.interior_clearance_class
            ),
            "grcv3_rich_support_connectivity": (
                None if interior_geometry is None else interior_geometry.support_connectivity
            ),
            "grcv3_rich_support_role_groups": (
                {}
                if interior_geometry is None
                else {
                    group_name: list(group_roles)
                    for group_name, group_roles in interior_geometry.support_role_groups.items()
                }
            ),
            "grcv3_rich_partition_mode": (
                None if interior_partition is None else interior_partition.partition_mode
            ),
            "grcv3_rich_probe_protection_class": (
                None
                if interior_partition is None
                else interior_partition.probe_protection_class
            ),
            "grcv3_rich_load_transfer_mode": (
                None if interior_partition is None else interior_partition.load_transfer_mode
            ),
            "grcv3_native_lowering": True,
        },
    )
    realized_specs = [
        _RealizedNodeSpec(
            source_primitive_id=plan.primitive_id,
            source_primitive_type=plan.primitive_type,
            realized_key=f"{plan.primitive_id}::center",
            role=plan.role,
            parent_id=plan.parent_id,
            raw_mass=float(center_mass),
            chart_center_hint=plan.chart_center_hint,
            chart_scale_hint=plan.chart_scale_hint,
            metadata=center_metadata,
            basin_id=plan.primitive_id,
            depth=plan.depth,
            semantic_anchor=True,
            motif_role="basin_center",
        )
    ]
    for index, angle in enumerate(support_angles):
        role_label = None if not plan.role_order else plan.role_order[index]
        profile_value = (
            "neutral"
            if role_label is None
            else _native_support_profile_value(plan, role_label)
        )
        support_radius = _native_support_radius(
            primitive_radius,
            profile_value=profile_value,
        )
        support_point = _offset_point(
            plan.chart_center_hint,
            radius=support_radius,
            angle=angle,
        )
        support_metadata = _realized_node_metadata_from_source(
            source_role=plan.role,
            source_metadata={},
            motif_role="basin_support",
            motif_index=index,
            semantic_anchor=False,
            extra_metadata={
                "projector_radius": primitive_radius,
                "support_radius": support_radius,
                "support_angle": angle,
                "source_extensions": plan.source_extensions,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_role_label": role_label,
                "grcv3_support_profile": profile_value,
                "grcv3_support_role_group": (
                    None if role_label is None else support_role_group_by_role.get(role_label)
                ),
                "grcv3_partition_tier": (
                    "probe_shell" if interior_partition is not None else None
                ),
                "grcv3_partition_load_group": (
                    None if role_label is None else partition_load_group_by_role.get(role_label)
                ),
                "grcv3_rich_curvature_class": plan.curvature_class,
                "grcv3_rich_weak_axis_role": plan.weak_axis_role,
                "grcv3_rich_attachment_isolation": (
                    None if interior_geometry is None else interior_geometry.attachment_isolation
                ),
                "grcv3_rich_support_connectivity": (
                    None if interior_geometry is None else interior_geometry.support_connectivity
                ),
                "grcv3_native_lowering": True,
            },
        )
        realized_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=plan.primitive_id,
                source_primitive_type=plan.primitive_type,
                realized_key=f"{plan.primitive_id}::support:{index}",
                role=plan.role,
                parent_id=plan.parent_id,
                raw_mass=float(support_mass),
                chart_center_hint=support_point,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=support_metadata,
                basin_id=plan.primitive_id,
                depth=plan.depth,
                semantic_anchor=False,
                motif_role="basin_support",
            )
        )
    if (
        interior_partition is not None
        and plan.role_order
        and interior_load_carriers is None
    ):
        protection_scale = _PARTITION_PROBE_SHELL_RADIUS_SCALE.get(
            str(interior_partition.probe_protection_class),
            1.35,
        )
        for index, angle in enumerate(support_angles):
            role_label = plan.role_order[index]
            profile_value = _native_support_profile_value(plan, role_label)
            load_radius = _native_support_radius(
                primitive_radius,
                profile_value=profile_value,
            ) * float(protection_scale)
            load_point = _offset_point(
                plan.chart_center_hint,
                radius=load_radius,
                angle=angle,
            )
            load_metadata = _realized_node_metadata_from_source(
                source_role=plan.role,
                source_metadata={},
                motif_role="basin_load_shell",
                motif_index=index,
                semantic_anchor=False,
                extra_metadata={
                    "projector_radius": primitive_radius,
                    "support_radius": load_radius,
                    "support_angle": angle,
                    "source_extensions": plan.source_extensions,
                    "grcv3_rich_contract_version": rich_contract_version,
                    "grcv3_rich": True,
                    "grcv3_role_label": role_label,
                    "grcv3_support_profile": profile_value,
                    "grcv3_partition_tier": "load_shell",
                    "grcv3_partition_mode": interior_partition.partition_mode,
                    "grcv3_partition_load_group": partition_load_group_by_role.get(role_label),
                    "grcv3_load_transfer_mode": interior_partition.load_transfer_mode,
                    "grcv3_probe_protection_class": (
                        interior_partition.probe_protection_class
                    ),
                    "grcv3_native_lowering": True,
                },
            )
            realized_specs.append(
                _RealizedNodeSpec(
                    source_primitive_id=plan.primitive_id,
                    source_primitive_type=plan.primitive_type,
                    realized_key=f"{plan.primitive_id}::load:{index}",
                    role=plan.role,
                    parent_id=plan.parent_id,
                    raw_mass=float(support_mass),
                    chart_center_hint=load_point,
                    chart_scale_hint=plan.chart_scale_hint,
                    metadata=load_metadata,
                    basin_id=plan.primitive_id,
                    depth=plan.depth,
                    semantic_anchor=False,
                    motif_role="basin_load_shell",
                )
            )
    if interior_load_carriers is not None and plan.role_order:
        carrier_specs = _native_load_carrier_specs(
            plan,
            primitive_radius=primitive_radius,
            support_mass=support_mass,
            rich_contract_version=rich_contract_version,
        )
        realized_specs.extend(carrier_specs)
        if plan.transfer_mediation is not None and plan.transfer_mediation.path_topology:
            probe_points_by_role = {
                str(spec.metadata["grcv3_role_label"]): spec.chart_center_hint
                for spec in realized_specs
                if spec.motif_role == "basin_support"
                and spec.metadata.get("grcv3_partition_tier") == "probe_shell"
                and isinstance(spec.metadata.get("grcv3_role_label"), str)
                and spec.chart_center_hint is not None
            }
            carrier_points_by_role = {
                str(spec.metadata["grcv3_role_label"]): spec.chart_center_hint
                for spec in carrier_specs
                if isinstance(spec.metadata.get("grcv3_role_label"), str)
                and spec.chart_center_hint is not None
            }
            realized_specs.extend(
                _native_transfer_path_node_specs(
                    plan,
                    support_mass=support_mass,
                    rich_contract_version=rich_contract_version,
                    probe_points_by_role=probe_points_by_role,
                    carrier_points_by_role=carrier_points_by_role,
                )
            )
    return realized_specs


def _build_single_node_spec(
    blueprint_node: GRCV2LandscapeNodeBlueprint,
    *,
    depth: int,
) -> list[_RealizedNodeSpec]:
    return [
        _RealizedNodeSpec(
            source_primitive_id=blueprint_node.primitive_id,
            source_primitive_type=blueprint_node.primitive_type,
            realized_key=f"{blueprint_node.primitive_id}::anchor",
            role=blueprint_node.role,
            parent_id=blueprint_node.parent_id,
            raw_mass=float(_required_node_mass(blueprint_node)),
            chart_center_hint=blueprint_node.chart_center_hint,
            chart_scale_hint=blueprint_node.chart_scale_hint,
            metadata=_realized_node_metadata(
                blueprint_node,
                motif_role="single_anchor",
                motif_index=0,
                semantic_anchor=True,
            ),
            basin_id=blueprint_node.primitive_id,
            depth=depth,
            semantic_anchor=True,
            motif_role="single_anchor",
        )
    ]


def _incident_valley_blueprints(
    primitive_id: str,
    *,
    blueprint: GRCV2LandscapeBlueprint,
) -> list[GRCV2LandscapeEdgeBlueprint]:
    valleys = [
        edge_blueprint
        for edge_blueprint in blueprint.edge_blueprints
        if edge_blueprint.primitive_type == "valley"
        and (
            edge_blueprint.source_primitive_id == primitive_id
            or edge_blueprint.target_primitive_id == primitive_id
        )
    ]
    return sorted(valleys, key=lambda edge_blueprint: edge_blueprint.primitive_id)


def _point_toward(
    source_point: tuple[float, float] | None,
    target_point: tuple[float, float] | None,
    *,
    distance: float,
) -> tuple[float, float] | None:
    if source_point is None or target_point is None:
        return None
    dx = float(target_point[0] - source_point[0])
    dy = float(target_point[1] - source_point[1])
    norm = math.sqrt(dx * dx + dy * dy)
    if norm <= 1e-12:
        return source_point
    scale = float(distance / norm)
    return (source_point[0] + dx * scale, source_point[1] + dy * scale)


def _branch_target_point(
    junction_primitive_id: str,
    valley_blueprint: GRCV2LandscapeEdgeBlueprint,
    *,
    node_blueprint_by_primitive_id: Mapping[str, GRCV2LandscapeNodeBlueprint],
) -> tuple[float, float] | None:
    if valley_blueprint.source_primitive_id == junction_primitive_id:
        other_primitive_id = valley_blueprint.target_primitive_id
        waypoint_index = 0
    else:
        other_primitive_id = valley_blueprint.source_primitive_id
        waypoint_index = -1
    waypoints_raw = valley_blueprint.metadata.get("waypoints", ())
    if isinstance(waypoints_raw, (list, tuple)) and waypoints_raw:
        waypoint = waypoints_raw[waypoint_index]
        if isinstance(waypoint, (list, tuple)) and len(waypoint) >= 2:
            return (float(waypoint[0]), float(waypoint[1]))
    return node_blueprint_by_primitive_id[other_primitive_id].chart_center_hint


def _build_junction_motif_specs(
    primitive: Any,
    blueprint_node: GRCV2LandscapeNodeBlueprint,
    *,
    depth: int,
    blueprint: GRCV2LandscapeBlueprint,
    node_blueprint_by_primitive_id: Mapping[str, GRCV2LandscapeNodeBlueprint],
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None,
    rich_contract_version: str | None,
) -> list[_RealizedNodeSpec]:
    primitive_mass = _required_node_mass(blueprint_node)
    incident_valleys = _incident_valley_blueprints(blueprint_node.primitive_id, blueprint=blueprint)
    if not incident_valleys:
        return _build_basin_patch_specs(
            primitive,
            blueprint_node,
            depth=depth,
            rich_primitive_extension=rich_primitive_extension,
            rich_contract_version=rich_contract_version,
        )
    if rich_primitive_extension is not None:
        branch_count = rich_primitive_extension.realization.support_count
    else:
        branch_count = len(incident_valleys)
    center_mass = primitive_mass * _JUNCTION_CENTER_MASS_FRACTION
    branch_mass = (primitive_mass - center_mass) / float(branch_count)
    primitive_radius = _primitive_radius(blueprint_node.chart_scale_hint)
    if rich_primitive_extension is not None:
        branch_radius = max(
            1e-6,
            primitive_radius * rich_primitive_extension.realization.radius_scale,
        )
    else:
        branch_radius = max(1e-6, primitive_radius * _BASIN_SUPPORT_RADIUS_SCALE)
    extra_metadata: dict[str, Any] = {
        "projector_radius": primitive_radius,
        "branch_radius": branch_radius,
        "junction_like_source": True,
        "junction_incident_valley_ids": tuple(
            edge_blueprint.primitive_id for edge_blueprint in incident_valleys
        ),
        "source_extensions": _to_plain_data(getattr(primitive, "extensions", {})),
    }
    if isinstance(primitive, JunctionSeedPrimitive):
        extra_metadata.update(
            {
                "host_id": primitive.host_id,
                "is_hostless": primitive.host_id is None,
                "junction_anchor_mode": "standalone" if primitive.host_id is None else "hosted",
                "branch_target_ids": tuple(primitive.branch_target_ids),
                "junction_role": primitive.junction_role,
            }
        )
    if rich_primitive_extension is not None:
        extra_metadata.update(
            {
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_rich_kind": rich_primitive_extension.realization.kind,
                "grcv3_rich_support_count": rich_primitive_extension.realization.support_count,
                "grcv3_rich_branch_order": rich_primitive_extension.realization.branch_order,
                "grcv3_rich_frame_mode": rich_primitive_extension.local_geometry.frame_mode,
                "grcv3_rich_weak_axis_role": rich_primitive_extension.local_geometry.weak_axis_role,
                "grcv3_rich_branch_targets": dict(rich_primitive_extension.interfaces.branch_targets),
            }
        )
    center_metadata = _realized_node_metadata(
        blueprint_node,
        motif_role="junction_center",
        motif_index=0,
        semantic_anchor=True,
        extra_metadata=extra_metadata,
    )
    realized_specs = [
        _RealizedNodeSpec(
            source_primitive_id=blueprint_node.primitive_id,
            source_primitive_type=blueprint_node.primitive_type,
            realized_key=f"{blueprint_node.primitive_id}::junction_center",
            role=blueprint_node.role,
            parent_id=blueprint_node.parent_id,
            raw_mass=float(center_mass),
            chart_center_hint=blueprint_node.chart_center_hint,
            chart_scale_hint=blueprint_node.chart_scale_hint,
            metadata=center_metadata,
            basin_id=blueprint_node.primitive_id,
            depth=depth,
            semantic_anchor=True,
            motif_role="junction_center",
        )
    ]
    if rich_primitive_extension is not None:
        branch_order = rich_primitive_extension.realization.branch_order
        branch_angles = _branch_angles_for_order(branch_order)
        branch_blueprints: list[tuple[int, str, str, tuple[float, float] | None]] = []
        for index, role in enumerate(branch_order):
            target_primitive_id = rich_primitive_extension.interfaces.branch_targets[role]
            branch_target = node_blueprint_by_primitive_id[target_primitive_id].chart_center_hint
            branch_point = _offset_point(
                blueprint_node.chart_center_hint,
                radius=branch_radius,
                angle=branch_angles[index],
            )
            branch_blueprints.append((index, role, target_primitive_id, branch_target))
    else:
        branch_blueprints = []
        for index, valley_blueprint in enumerate(incident_valleys):
            if valley_blueprint.source_primitive_id == blueprint_node.primitive_id:
                target_primitive_id = valley_blueprint.target_primitive_id
            else:
                target_primitive_id = valley_blueprint.source_primitive_id
            branch_target = _branch_target_point(
                blueprint_node.primitive_id,
                valley_blueprint,
                node_blueprint_by_primitive_id=node_blueprint_by_primitive_id,
            )
            branch_blueprints.append((index, f"branch_{index}", target_primitive_id, branch_target))
    for index, branch_role, target_primitive_id, branch_target in branch_blueprints:
        if rich_primitive_extension is not None:
            branch_point = _offset_point(
                blueprint_node.chart_center_hint,
                radius=branch_radius,
                angle=_branch_angles_for_order(rich_primitive_extension.realization.branch_order)[index],
            )
        else:
            branch_point = _point_toward(
                blueprint_node.chart_center_hint,
                branch_target,
                distance=branch_radius,
            )
        branch_metadata = _realized_node_metadata(
            blueprint_node,
            motif_role="junction_branch",
            motif_index=index,
            semantic_anchor=False,
            extra_metadata={
                "projector_radius": primitive_radius,
                "branch_radius": branch_radius,
                "branch_role": branch_role,
                "branch_target_primitive_id": target_primitive_id,
                "branch_target_point": branch_target,
                "junction_like_source": True,
                "source_extensions": _to_plain_data(getattr(primitive, "extensions", {})),
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": rich_primitive_extension is not None,
                "grcv3_rich_branch_role": branch_role,
                "grcv3_rich_target_primitive_id": target_primitive_id,
                "grcv3_rich_weak_axis_role": (
                    None
                    if rich_primitive_extension is None
                    else rich_primitive_extension.local_geometry.weak_axis_role
                ),
            },
        )
        realized_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=blueprint_node.primitive_id,
                source_primitive_type=blueprint_node.primitive_type,
                realized_key=f"{blueprint_node.primitive_id}::junction_branch:{index}",
                role=blueprint_node.role,
                parent_id=blueprint_node.parent_id,
                raw_mass=float(branch_mass),
                chart_center_hint=branch_point,
                chart_scale_hint=blueprint_node.chart_scale_hint,
                metadata=branch_metadata,
                basin_id=blueprint_node.primitive_id,
                depth=depth,
                semantic_anchor=False,
                motif_role="junction_branch",
            )
        )
    return realized_specs


def _build_native_junction_motif_specs(
    plan: GRCV3NativeJunctionPlan,
    *,
    rich_contract_version: str,
    target_center_by_primitive_id: Mapping[str, tuple[float, float] | None],
) -> list[_RealizedNodeSpec]:
    primitive_mass = _required_native_node_mass(plan.primitive_id, plan.coherence_prior)
    center_mass = primitive_mass * _JUNCTION_CENTER_MASS_FRACTION
    branch_mass = (primitive_mass - center_mass) / float(plan.support_count)
    primitive_radius = _primitive_radius(plan.chart_scale_hint)
    branch_radius = max(1e-6, primitive_radius * plan.radius_scale)
    center_metadata = _realized_node_metadata_from_source(
        source_role=plan.role,
        source_metadata={},
        motif_role="junction_center",
        motif_index=0,
        semantic_anchor=True,
        extra_metadata={
            "projector_radius": primitive_radius,
            "branch_radius": branch_radius,
            "junction_like_source": True,
            "junction_incident_valley_ids": (),
            "source_extensions": plan.source_extensions,
            "host_id": plan.host_id,
            "is_hostless": plan.hostless,
            "junction_anchor_mode": "standalone" if plan.hostless else "hosted",
            "branch_target_ids": plan.branch_target_ids,
            "junction_role": plan.junction_role,
            "grcv3_rich_contract_version": rich_contract_version,
            "grcv3_rich": True,
            "grcv3_rich_kind": "junction_motif",
            "grcv3_rich_support_count": plan.support_count,
            "grcv3_rich_branch_order": plan.branch_order,
            "grcv3_rich_frame_mode": plan.frame_mode,
            "grcv3_rich_weak_axis_role": plan.weak_axis_role,
            "grcv3_rich_branch_targets": dict(plan.branch_targets),
            "grcv3_native_lowering": True,
        },
    )
    realized_specs = [
        _RealizedNodeSpec(
            source_primitive_id=plan.primitive_id,
            source_primitive_type=plan.primitive_type,
            realized_key=f"{plan.primitive_id}::junction_center",
            role=plan.role,
            parent_id=plan.parent_id,
            raw_mass=float(center_mass),
            chart_center_hint=plan.chart_center_hint,
            chart_scale_hint=plan.chart_scale_hint,
            metadata=center_metadata,
            basin_id=plan.primitive_id,
            depth=plan.depth,
            semantic_anchor=True,
            motif_role="junction_center",
        )
    ]
    branch_angles = _branch_angles_for_order(plan.branch_order)
    for index, branch_role in enumerate(plan.branch_order):
        target_primitive_id = plan.branch_targets[branch_role]
        branch_target = target_center_by_primitive_id.get(target_primitive_id)
        branch_point = _offset_point(
            plan.chart_center_hint,
            radius=branch_radius,
            angle=branch_angles[index],
        )
        branch_metadata = _realized_node_metadata_from_source(
            source_role=plan.role,
            source_metadata={},
            motif_role="junction_branch",
            motif_index=index,
            semantic_anchor=False,
            extra_metadata={
                "projector_radius": primitive_radius,
                "branch_radius": branch_radius,
                "branch_role": branch_role,
                "branch_target_primitive_id": target_primitive_id,
                "branch_target_point": branch_target,
                "junction_like_source": True,
                "source_extensions": plan.source_extensions,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_rich_branch_role": branch_role,
                "grcv3_rich_target_primitive_id": target_primitive_id,
                "grcv3_rich_weak_axis_role": plan.weak_axis_role,
                "grcv3_native_lowering": True,
            },
        )
        realized_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=plan.primitive_id,
                source_primitive_type=plan.primitive_type,
                realized_key=f"{plan.primitive_id}::junction_branch:{index}",
                role=plan.role,
                parent_id=plan.parent_id,
                raw_mass=float(branch_mass),
                chart_center_hint=branch_point,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=branch_metadata,
                basin_id=plan.primitive_id,
                depth=plan.depth,
                semantic_anchor=False,
                motif_role="junction_branch",
            )
        )
    return realized_specs


def _build_node_specs(
    request: GRCV3LandscapeProjectionRequest,
    blueprint: GRCV2LandscapeBlueprint | None,
    *,
    lowering_lane: str,
    native_surface: GRCV3NativePrimitiveSurface | None,
    rich_seed_extension: GRCV3RichSeedExtension | None,
) -> tuple[
    list[_RealizedNodeSpec],
    dict[str, GRCV2LandscapeNodeBlueprint],
    dict[str, float],
]:
    primitive_index = _primitive_index(request.seed)
    primitive_depths = _primitive_depth_index(request.seed)
    realized_specs: list[_RealizedNodeSpec] = []
    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None:
        node_blueprint_by_primitive_id: dict[str, GRCV2LandscapeNodeBlueprint] = {}
        primitive_raw_node_masses: dict[str, float] = {}
        target_center_by_primitive_id = {
            primitive_id: plan.chart_center_hint
            for primitive_id, plan in native_surface.basin_like_plans.items()
        }
        target_center_by_primitive_id.update(
            {
                primitive_id: plan.chart_center_hint
                for primitive_id, plan in native_surface.junction_plans.items()
            }
        )
        for primitive_id in native_surface.node_carrier_ids:
            primitive = primitive_index[primitive_id]
            if primitive_id in native_surface.junction_plans:
                plan = native_surface.junction_plans[primitive_id]
                primitive_raw_node_masses[primitive_id] = _required_native_node_mass(
                    plan.primitive_id,
                    plan.coherence_prior,
                )
                realized_specs.extend(
                    _build_native_junction_motif_specs(
                        plan,
                        rich_contract_version=native_surface.rich_contract_version,
                        target_center_by_primitive_id=target_center_by_primitive_id,
                    )
                )
                continue
            if primitive_id in native_surface.basin_like_plans:
                plan = native_surface.basin_like_plans[primitive_id]
                primitive_raw_node_masses[primitive_id] = _required_native_node_mass(
                    plan.primitive_id,
                    plan.coherence_prior,
                )
                realized_specs.extend(
                    _build_native_basin_patch_specs(
                        plan,
                        rich_contract_version=native_surface.rich_contract_version,
                    )
                )
                continue
            raise InvalidLandscapeSeedError(
                f"family-native node carrier {primitive_id!r} has no lowering plan"
            )
        return realized_specs, node_blueprint_by_primitive_id, primitive_raw_node_masses

    if blueprint is None:
        raise InvalidLandscapeSeedError(
            "compatibility lowering requires a realized GRCV2 blueprint"
        )
    node_blueprint_by_primitive_id = {
        blueprint_node.primitive_id: blueprint_node for blueprint_node in blueprint.node_blueprints
    }
    primitive_raw_node_masses = {
        primitive_id: float(_required_node_mass(node_blueprint))
        for primitive_id, node_blueprint in node_blueprint_by_primitive_id.items()
    }
    for blueprint_node in blueprint.node_blueprints:
        depth = primitive_depths.get(blueprint_node.primitive_id, 0)
        primitive = primitive_index[blueprint_node.primitive_id]
        if is_junction_like_primitive(primitive):
            rich_primitive_extension = None
            if rich_seed_extension is not None:
                rich_primitive_extension = rich_seed_extension.primitive_extensions.get(
                    blueprint_node.primitive_id
                )
            realized_specs.extend(
                _build_junction_motif_specs(
                    primitive,
                    blueprint_node,
                    depth=depth,
                    blueprint=blueprint,
                    node_blueprint_by_primitive_id=node_blueprint_by_primitive_id,
                    rich_primitive_extension=rich_primitive_extension,
                    rich_contract_version=(
                        None
                        if rich_seed_extension is None
                        else rich_seed_extension.contract_version
                    ),
                )
            )
        elif blueprint_node.primitive_type == "basin":
            rich_primitive_extension = _rich_extension_for_primitive(
                rich_seed_extension,
                blueprint_node.primitive_id,
            )
            realized_specs.extend(
                _build_basin_patch_specs(
                    primitive,
                    blueprint_node,
                    depth=depth,
                    rich_primitive_extension=rich_primitive_extension,
                    rich_contract_version=(
                        None if rich_seed_extension is None else rich_seed_extension.contract_version
                    ),
                )
            )
        else:
            realized_specs.extend(_build_single_node_spec(blueprint_node, depth=depth))
    return realized_specs, node_blueprint_by_primitive_id, primitive_raw_node_masses


def _channel_point_sequence(
    edge_blueprint: GRCV2LandscapeEdgeBlueprint,
    *,
    source_center: tuple[float, float] | None,
    target_center: tuple[float, float] | None,
    rich_channel_geometry: GRCV3RichChannelGeometry | None = None,
) -> list[tuple[float, float] | None]:
    waypoints = [
        (float(point[0]), float(point[1]))
        for point in edge_blueprint.metadata.get("waypoints", ())
        if isinstance(point, (list, tuple)) and len(point) >= 2
    ]
    return _channel_point_sequence_from_waypoints(
        waypoints,
        source_center=source_center,
        target_center=target_center,
        rich_channel_geometry=rich_channel_geometry,
    )


def _channel_point_sequence_from_waypoints(
    waypoints: list[tuple[float, float]],
    *,
    source_center: tuple[float, float] | None,
    target_center: tuple[float, float] | None,
    rich_channel_geometry: GRCV3RichChannelGeometry | None = None,
) -> list[tuple[float, float] | None]:
    if rich_channel_geometry is not None:
        polyline = [source_center, *waypoints, target_center]
        count = rich_channel_geometry.interior_count
        if rich_channel_geometry.waypoint_policy == "midpoint_only":
            polyline = [source_center, _midpoint(source_center, target_center), target_center]
        return _sample_polyline_points(polyline, count=count)
    channel_count = (
        _CHANNEL_NODES_WITH_WAYPOINTS if waypoints else _CHANNEL_NODES_WITHOUT_WAYPOINTS
    )
    if channel_count == 1:
        if waypoints:
            return [waypoints[len(waypoints) // 2]]
        return [_midpoint(source_center, target_center)]
    if len(waypoints) >= 2:
        return [waypoints[0], waypoints[-1]]
    if waypoints:
        waypoint = waypoints[0]
        midpoint_a = _midpoint(source_center, waypoint)
        midpoint_b = _midpoint(waypoint, target_center)
        return [midpoint_a, midpoint_b]
    if source_center is None or target_center is None:
        return [None, None]
    return [
        (
            (2.0 * source_center[0] + target_center[0]) / 3.0,
            (2.0 * source_center[1] + target_center[1]) / 3.0,
        ),
        (
            (source_center[0] + 2.0 * target_center[0]) / 3.0,
            (source_center[1] + 2.0 * target_center[1]) / 3.0,
        ),
    ]


def _build_native_valley_channel_specs(
    plan: GRCV3NativeValleyPlan,
    *,
    source_center: tuple[float, float] | None,
    target_center: tuple[float, float] | None,
    rich_contract_version: str,
) -> list[_RealizedNodeSpec]:
    channel_points = _channel_point_sequence_from_waypoints(
        list(plan.waypoints),
        source_center=source_center,
        target_center=target_center,
        rich_channel_geometry=plan.channel_geometry,
    )
    raw_mass_total = 0.0 if plan.coherence_prior is None else float(plan.coherence_prior)
    per_node_mass = raw_mass_total / float(len(channel_points)) if channel_points else 0.0
    return [
        _RealizedNodeSpec(
            source_primitive_id=plan.primitive_id,
            source_primitive_type=plan.primitive_type,
            realized_key=f"{plan.primitive_id}::channel:{index}",
            role=plan.role,
            parent_id=None,
            raw_mass=float(per_node_mass),
            chart_center_hint=channel_point,
            chart_scale_hint=_freeze_optional_mapping({}),
            metadata={
                "motif_role": "valley_channel",
                "motif_index": index,
                "semantic_anchor": False,
                "source_metadata": {
                    "path_hint": plan.path_hint,
                    "width_hint": plan.width_hint,
                    "waypoints": [list(point) for point in plan.waypoints],
                },
                "source_role": plan.role,
                "path_hint": plan.path_hint,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_rich_channel_realization_kind": (
                    None
                    if plan.channel_geometry is None
                    else plan.channel_geometry.realization_kind
                ),
                "grcv3_native_lowering": True,
            },
            basin_id=plan.primitive_id,
            depth=plan.depth,
            semantic_anchor=False,
            motif_role="valley_channel",
        )
        for index, channel_point in enumerate(channel_points)
    ]


def _build_valley_channel_specs(
    edge_blueprint: GRCV2LandscapeEdgeBlueprint,
    *,
    node_blueprint_by_primitive_id: Mapping[str, GRCV2LandscapeNodeBlueprint],
    primitive_depths: Mapping[str, int],
    rich_primitive_extension: GRCV3RichPrimitiveExtension | None = None,
    rich_contract_version: str | None = None,
) -> list[_RealizedNodeSpec]:
    source_blueprint = node_blueprint_by_primitive_id[edge_blueprint.source_primitive_id]
    target_blueprint = node_blueprint_by_primitive_id[edge_blueprint.target_primitive_id]
    channel_points = _channel_point_sequence(
        edge_blueprint,
        source_center=source_blueprint.chart_center_hint,
        target_center=target_blueprint.chart_center_hint,
        rich_channel_geometry=(
            None if rich_primitive_extension is None else rich_primitive_extension.channel_geometry
        ),
    )
    raw_mass_total = (
        float(edge_blueprint.coherence_prior)
        if edge_blueprint.coherence_prior is not None
        else 0.0
    )
    per_node_mass = raw_mass_total / float(len(channel_points)) if channel_points else 0.0
    channel_depth = max(
        primitive_depths.get(edge_blueprint.source_primitive_id, 0),
        primitive_depths.get(edge_blueprint.target_primitive_id, 0),
    )
    return [
        _RealizedNodeSpec(
            source_primitive_id=edge_blueprint.primitive_id,
            source_primitive_type=edge_blueprint.primitive_type,
            realized_key=f"{edge_blueprint.primitive_id}::channel:{index}",
            role=edge_blueprint.role,
            parent_id=None,
            raw_mass=float(per_node_mass),
            chart_center_hint=channel_point,
            chart_scale_hint=_freeze_optional_mapping({}),
            metadata={
                "motif_role": "valley_channel",
                "motif_index": index,
                "semantic_anchor": False,
                "source_metadata": _to_plain_data(edge_blueprint.metadata),
                "source_role": edge_blueprint.role,
                "path_hint": edge_blueprint.path_hint,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": rich_primitive_extension is not None,
                "grcv3_rich_channel_realization_kind": (
                    None
                    if rich_primitive_extension is None
                    or rich_primitive_extension.channel_geometry is None
                    else rich_primitive_extension.channel_geometry.realization_kind
                ),
            },
            basin_id=edge_blueprint.primitive_id,
            depth=channel_depth,
            semantic_anchor=False,
            motif_role="valley_channel",
        )
        for index, channel_point in enumerate(channel_points)
    ]


def _node_id_for_role(
    primitive_id: str,
    role_label: str | None,
    *,
    role_node_ids_by_primitive_id: Mapping[str, Mapping[str, int]],
) -> int | None:
    if role_label is None:
        return None
    primitive_map = role_node_ids_by_primitive_id.get(primitive_id)
    if primitive_map is None:
        return None
    return primitive_map.get(role_label)


def _preferred_attachment_role(
    primitive_id: str,
    attachment_label: str | None,
    *,
    rich_seed_extension: GRCV3RichSeedExtension | None,
) -> str | None:
    if attachment_label is None or rich_seed_extension is None:
        return None
    primitive_extension = rich_seed_extension.primitive_extensions.get(primitive_id)
    if primitive_extension is None or primitive_extension.interfaces is None:
        return None
    return primitive_extension.interfaces.preferred_attachment_sites.get(attachment_label)


def _ridge_support_points_from_geometry(
    owner_center: tuple[float, float] | None,
    *,
    primitive_radius: float,
    role_angle_map: Mapping[str, float],
    boundary_geometry: GRCV3RichBoundaryGeometry | None,
) -> list[tuple[float, float] | None]:
    if boundary_geometry is None:
        return _ridge_support_points(owner_center, owner_center)
    if owner_center is None:
        node_count = (
            _RICH_SUPPORT_ARC_NODE_COUNT
            if boundary_geometry.realization_kind != "double_support_arc"
            else _RICH_SUPPORT_ARC_NODE_COUNT + 1
        )
        return [None for _ in range(node_count)]
    base_angle = role_angle_map.get(boundary_geometry.normal_role)
    tangent_angle = role_angle_map.get(boundary_geometry.tangent_role)
    if base_angle is None or tangent_angle is None:
        return _ridge_support_points(owner_center, owner_center)
    span = _normalize_arc_span_radians(boundary_geometry.arc_span)
    if boundary_geometry.realization_kind == "double_support_arc":
        offsets = (-0.5, -0.15, 0.15, 0.5)
    else:
        offsets = (-0.5, 0.0, 0.5)
    tangent_sign = 1.0 if math.sin(tangent_angle - base_angle) >= 0.0 else -1.0
    support_radius = max(1e-6, primitive_radius * 1.05)
    return [
        _offset_point(
            owner_center,
            radius=support_radius,
            angle=base_angle + tangent_sign * span * offset,
        )
        for offset in offsets
    ]


def _select_connection_node(
    primitive_id: str,
    *,
    target_point: tuple[float, float] | None,
    anchor_node_id_by_primitive_id: Mapping[str, int],
    interface_node_ids_by_primitive_id: Mapping[str, tuple[int, ...]],
    support_node_ids_by_primitive_id: Mapping[str, tuple[int, ...]],
    node_center_by_id: Mapping[int, tuple[float, float] | None],
    allow_anchor_fallback: bool = True,
) -> int:
    interface_node_ids = interface_node_ids_by_primitive_id.get(primitive_id, ())
    if interface_node_ids and target_point is not None:
        return min(
            interface_node_ids,
            key=lambda node_id: (
                _point_distance_squared(node_center_by_id.get(node_id), target_point),
                node_id,
            ),
        )
    support_node_ids = support_node_ids_by_primitive_id.get(primitive_id, ())
    if support_node_ids:
        if target_point is None:
            return min(support_node_ids)
        return min(
            support_node_ids,
            key=lambda node_id: (
                _point_distance_squared(node_center_by_id.get(node_id), target_point),
                node_id,
            ),
        )
    if allow_anchor_fallback:
        return anchor_node_id_by_primitive_id[primitive_id]
    raise InvalidLandscapeSeedError(
        f"primitive {primitive_id!r} requires support/interface attachment, "
        "but no realized support/interface nodes are available"
    )


def _native_support_profile_value(
    plan: GRCV3NativeBasinLikePlan | GRCV3NativeJunctionPlan,
    role: str,
) -> str:
    if plan.interior_geometry is None:
        return "neutral"
    return str(plan.interior_geometry.support_profile.get(role, "neutral"))


def _native_support_radius(
    primitive_radius: float,
    *,
    profile_value: str,
) -> float:
    multiplier = _SUPPORT_PROFILE_RADIUS_MULTIPLIERS.get(str(profile_value), 1.0)
    return max(1e-6, primitive_radius * _BASIN_SUPPORT_RADIUS_SCALE * float(multiplier))


def _native_support_spoke_weight(
    base_spoke_weight: float,
    *,
    profile_value: str,
    clearance_class: str | None = None,
) -> float:
    multiplier = _SUPPORT_PROFILE_SPOKE_MULTIPLIERS.get(str(profile_value), 1.0)
    clearance_scale = _INTERIOR_CLEARANCE_SPOKE_SCALE.get(
        "semi_open" if clearance_class is None else str(clearance_class),
        1.0,
    )
    return max(
        1e-6,
        float(base_spoke_weight) * float(multiplier) * float(clearance_scale),
    )


def _native_support_role_group_by_role(
    interior_geometry: GRCV3RichInteriorGeometry | None,
) -> dict[str, str]:
    if interior_geometry is None:
        return {}
    role_group_by_role: dict[str, str] = {}
    for group_name, roles in interior_geometry.support_role_groups.items():
        for role in roles:
            role_group_by_role[str(role)] = str(group_name)
    return role_group_by_role


def _native_partition_load_group_by_role(
    interior_partition: GRCV3RichInteriorPartition | None,
) -> dict[str, str]:
    if interior_partition is None:
        return {}
    load_group_by_role: dict[str, str] = {}
    for group_name, roles in interior_partition.load_role_groups.items():
        for role in roles:
            load_group_by_role[str(role)] = str(group_name)
    return load_group_by_role


def _native_transfer_mediation_class_by_pair(
    plan: GRCV3NativeBasinLikePlan,
) -> dict[tuple[str, str], str]:
    if plan.transfer_mediation is None:
        return {}
    return {
        (str(carrier_role), str(probe_role)): str(mediation_class)
        for carrier_role, probe_role, mediation_class in plan.transfer_mediation.pair_mediation_classes
    }


def _native_transfer_path_topology_by_pair(
    plan: GRCV3NativeBasinLikePlan,
) -> dict[tuple[str, str], str]:
    if plan.transfer_mediation is None:
        return {}
    return {
        (str(carrier_role), str(probe_role)): str(topology_class)
        for carrier_role, probe_role, topology_class in plan.transfer_mediation.path_topology
    }


def _native_transfer_spill_branch_mode(plan: GRCV3NativeBasinLikePlan) -> str:
    if plan.transfer_mediation is None:
        return "carrier_branch"
    return str(plan.transfer_mediation.spill_branch_mode)


def _native_transfer_spill_roles_for_target(
    plan: GRCV3NativeBasinLikePlan,
    target_probe_role: str,
) -> tuple[str, ...]:
    if plan.transfer_mediation is None:
        return ()
    spill_policy = str(plan.transfer_mediation.lateral_spill_policy)
    ordered_roles = tuple(str(role) for role in plan.role_order)
    if spill_policy == "role_locked" or not ordered_roles:
        return ()
    if spill_policy == "open":
        return tuple(role for role in ordered_roles if role != target_probe_role)
    support_group_by_role = _native_support_role_group_by_role(plan.interior_geometry)
    target_group = support_group_by_role.get(str(target_probe_role))
    if target_group is None:
        return ()
    return tuple(
        role
        for role in ordered_roles
        if role != target_probe_role and support_group_by_role.get(role) == target_group
    )


def _native_transfer_impacted_probe_roles(
    plan: GRCV3NativeBasinLikePlan,
) -> set[str]:
    impacted_roles: set[str] = set()
    mediation_class_by_pair = _native_transfer_mediation_class_by_pair(plan)
    if not mediation_class_by_pair:
        return impacted_roles
    for pair, mediation_class in mediation_class_by_pair.items():
        if str(mediation_class) == "blocked":
            continue
        _, probe_role = pair
        impacted_roles.add(str(probe_role))
        impacted_roles.update(_native_transfer_spill_roles_for_target(plan, str(probe_role)))
    return impacted_roles


def _native_transfer_guard_spoke_scale(
    plan: GRCV3NativeBasinLikePlan,
    role: str | None,
) -> float:
    if role is None or plan.transfer_mediation is None:
        return 1.0
    if str(role) not in _native_transfer_impacted_probe_roles(plan):
        return 1.0
    return float(
        _TRANSFER_MEDIATION_GUARD_SPOKE_SCALE.get(
            str(plan.transfer_mediation.probe_guard_class),
            1.0,
        )
    )


def _native_center_coupling_class_by_role(
    plan: GRCV3NativeBasinLikePlan,
) -> dict[str, str]:
    if plan.transfer_mediation is None:
        return {}
    return {
        str(probe_role): str(coupling_class)
        for probe_role, coupling_class in plan.transfer_mediation.center_coupling_classes
    }


def _native_transfer_center_spoke_scale(
    plan: GRCV3NativeBasinLikePlan,
    role: str | None,
) -> float:
    if role is None:
        return 1.0
    center_coupling_class_by_role = _native_center_coupling_class_by_role(plan)
    coupling_class = center_coupling_class_by_role.get(str(role))
    if coupling_class is not None:
        return float(_TRANSFER_MEDIATION_CENTER_COUPLING_SCALE.get(coupling_class, 1.0))
    return _native_transfer_guard_spoke_scale(plan, role)


def _native_support_angle_by_role(plan: GRCV3NativeBasinLikePlan) -> dict[str, float]:
    if not plan.role_order:
        return {}
    support_angles = _angles_for_role_order(plan.role_order)
    return {
        role_label: float(support_angles[index])
        for index, role_label in enumerate(plan.role_order)
    }


def _native_load_carrier_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    primitive_radius: float,
    support_mass: float,
    rich_contract_version: str,
) -> list[_RealizedNodeSpec]:
    interior_partition = plan.interior_partition
    interior_load_carriers = plan.interior_load_carriers
    if (
        interior_partition is None
        or interior_load_carriers is None
        or not plan.role_order
    ):
        return []
    role_angles = _native_support_angle_by_role(plan)
    ordered_roles = [role for role in plan.role_order if role in role_angles]
    if not ordered_roles:
        return []
    partition_load_group_by_role = _native_partition_load_group_by_role(interior_partition)
    center_offset = math.pi / float(len(ordered_roles))
    max_probe_radius = max(
        _native_support_radius(
            primitive_radius,
            profile_value=_native_support_profile_value(plan, role_label),
        )
        for role_label in ordered_roles
    )
    radius_scale = _LOAD_CARRIER_RADIUS_SCALE.get(
        str(interior_load_carriers.carrier_layout_mode),
        1.18,
    )
    base_radius = max(
        1e-6,
        max_probe_radius * float(radius_scale),
    )
    realized_specs: list[_RealizedNodeSpec] = []
    for index, role_label in enumerate(ordered_roles):
        role_angle = role_angles[role_label]
        if interior_load_carriers.carrier_layout_mode in {
            "offset_ring",
            "group_midpoints",
            "paired_tracks",
        }:
            carrier_angle = role_angle + center_offset
        else:
            carrier_angle = role_angle - center_offset
        if interior_load_carriers.carrier_anchor_policy == "role_aligned":
            carrier_angle = role_angle
        if interior_load_carriers.carrier_anchor_policy == "between_roles":
            carrier_angle = role_angle + center_offset
        role_group = partition_load_group_by_role.get(role_label)
        carrier_point = _offset_point(
            plan.chart_center_hint,
            radius=base_radius,
            angle=carrier_angle,
        )
        carrier_metadata = _realized_node_metadata_from_source(
            source_role=plan.role,
            source_metadata={},
            motif_role="basin_load_carrier",
            motif_index=index,
            semantic_anchor=False,
            extra_metadata={
                "projector_radius": primitive_radius,
                "support_radius": base_radius,
                "support_angle": carrier_angle,
                "source_extensions": plan.source_extensions,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_role_label": role_label,
                "grcv3_partition_tier": "load_carrier",
                "grcv3_partition_load_group": role_group,
                "grcv3_partition_mode": interior_partition.partition_mode,
                "grcv3_load_transfer_mode": interior_partition.load_transfer_mode,
                "grcv3_probe_protection_class": (
                    interior_partition.probe_protection_class
                ),
                "grcv3_load_carrier_layout_mode": (
                    interior_load_carriers.carrier_layout_mode
                ),
                "grcv3_load_carrier_anchor_policy": (
                    interior_load_carriers.carrier_anchor_policy
                ),
                "grcv3_load_carrier_transfer_topology_mode": (
                    interior_load_carriers.transfer_topology_mode
                ),
                "grcv3_load_carrier_attachment_roles": list(
                    interior_load_carriers.carrier_attachment_roles
                ),
                "grcv3_native_lowering": True,
            },
        )
        realized_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=plan.primitive_id,
                source_primitive_type=plan.primitive_type,
                realized_key=f"{plan.primitive_id}::carrier:{index}",
                role=plan.role,
                parent_id=plan.parent_id,
                raw_mass=float(support_mass),
                chart_center_hint=carrier_point,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=carrier_metadata,
                basin_id=plan.primitive_id,
                depth=plan.depth,
                semantic_anchor=False,
                motif_role="basin_load_carrier",
            )
        )
    return realized_specs


def _centroid_point(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if not points:
        return None
    x = sum(float(point[0]) for point in points) / float(len(points))
    y = sum(float(point[1]) for point in points) / float(len(points))
    return (x, y)


def _native_transfer_path_node_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    support_mass: float,
    rich_contract_version: str,
    probe_points_by_role: Mapping[str, tuple[float, float]],
    carrier_points_by_role: Mapping[str, tuple[float, float]],
) -> list[_RealizedNodeSpec]:
    if plan.transfer_mediation is None or not plan.transfer_mediation.path_topology:
        return []
    load_group_by_role = _native_partition_load_group_by_role(plan.interior_partition)
    path_specs: list[_RealizedNodeSpec] = []
    path_topology_by_pair = _native_transfer_path_topology_by_pair(plan)
    fan_in_pairs_by_probe_role: dict[str, list[tuple[str, str]]] = {}
    path_mass = max(1e-6, float(support_mass) * float(_TRANSFER_PATH_NODE_MASS_SCALE))
    for carrier_role, probe_role, topology_class in plan.transfer_mediation.path_topology:
        if topology_class != "single_intermediate":
            if topology_class == "fan_in":
                fan_in_pairs_by_probe_role.setdefault(str(probe_role), []).append(
                    (str(carrier_role), str(probe_role))
                )
            continue
        carrier_point = carrier_points_by_role.get(str(carrier_role))
        probe_point = probe_points_by_role.get(str(probe_role))
        if carrier_point is None or probe_point is None:
            continue
        path_point = _centroid_point([carrier_point, probe_point])
        if path_point is None:
            continue
        path_metadata = _realized_node_metadata_from_source(
            source_role=plan.role,
            source_metadata={},
            motif_role="basin_transfer_path_node",
            motif_index=len(path_specs),
            semantic_anchor=False,
            extra_metadata={
                "source_extensions": plan.source_extensions,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_transfer_path_scope": "pair",
                "grcv3_transfer_path_topology_class": str(topology_class),
                "grcv3_transfer_carrier_role": str(carrier_role),
                "grcv3_transfer_probe_role": str(probe_role),
                "grcv3_partition_load_group": load_group_by_role.get(str(carrier_role)),
                "grcv3_native_lowering": True,
            },
        )
        path_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=plan.primitive_id,
                source_primitive_type=plan.primitive_type,
                realized_key=f"{plan.primitive_id}::transfer_path:{carrier_role}:{probe_role}",
                role=plan.role,
                parent_id=plan.parent_id,
                raw_mass=path_mass,
                chart_center_hint=path_point,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=path_metadata,
                basin_id=plan.primitive_id,
                depth=plan.depth,
                semantic_anchor=False,
                motif_role="basin_transfer_path_node",
            )
        )
    for probe_role, pairs in sorted(fan_in_pairs_by_probe_role.items()):
        probe_point = probe_points_by_role.get(probe_role)
        if probe_point is None:
            continue
        carrier_points = [
            carrier_points_by_role[carrier_role]
            for carrier_role, _ in pairs
            if carrier_role in carrier_points_by_role
        ]
        path_point = _centroid_point([probe_point, *carrier_points])
        if path_point is None:
            continue
        path_metadata = _realized_node_metadata_from_source(
            source_role=plan.role,
            source_metadata={},
            motif_role="basin_transfer_path_node",
            motif_index=len(path_specs),
            semantic_anchor=False,
            extra_metadata={
                "source_extensions": plan.source_extensions,
                "grcv3_rich_contract_version": rich_contract_version,
                "grcv3_rich": True,
                "grcv3_transfer_path_scope": "probe_fan_in",
                "grcv3_transfer_path_topology_class": "fan_in",
                "grcv3_transfer_carrier_roles": [carrier_role for carrier_role, _ in pairs],
                "grcv3_transfer_probe_role": str(probe_role),
                "grcv3_native_lowering": True,
            },
        )
        path_specs.append(
            _RealizedNodeSpec(
                source_primitive_id=plan.primitive_id,
                source_primitive_type=plan.primitive_type,
                realized_key=f"{plan.primitive_id}::transfer_fan_in:{probe_role}",
                role=plan.role,
                parent_id=plan.parent_id,
                raw_mass=path_mass,
                chart_center_hint=path_point,
                chart_scale_hint=plan.chart_scale_hint,
                metadata=path_metadata,
                basin_id=plan.primitive_id,
                depth=plan.depth,
                semantic_anchor=False,
                motif_role="basin_transfer_path_node",
            )
        )
    return path_specs


def _native_support_edge_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    support_node_ids_by_role: Mapping[str, int],
) -> list[tuple[int, int, str, str | None, float]]:
    ordered_roles = [role for role in plan.role_order if role in support_node_ids_by_role]
    if len(ordered_roles) < 2:
        return []
    if plan.interior_geometry is None:
        return [
            (
                support_node_ids_by_role[ordered_roles[index]],
                support_node_ids_by_role[ordered_roles[(index + 1) % len(ordered_roles)]],
                "basin_patch_ring",
                None,
                1.0,
            )
            for index in range(len(ordered_roles))
        ]
    connectivity = str(plan.interior_geometry.support_connectivity)
    if connectivity == "branch_only":
        return []
    if connectivity == "ring":
        return [
            (
                support_node_ids_by_role[ordered_roles[index]],
                support_node_ids_by_role[ordered_roles[(index + 1) % len(ordered_roles)]],
                "basin_patch_ring",
                None,
                1.0,
            )
            for index in range(len(ordered_roles))
        ]
    role_group_by_role = _native_support_role_group_by_role(plan.interior_geometry)
    grouped_specs: list[tuple[int, int, str, str | None, float]] = []
    for group_name, roles in sorted(plan.interior_geometry.support_role_groups.items()):
        ordered_group_roles = [role for role in ordered_roles if role in set(roles)]
        if len(ordered_group_roles) < 2:
            continue
        if len(ordered_group_roles) == 2:
            role_pairs = [(ordered_group_roles[0], ordered_group_roles[1])]
        else:
            role_pairs = list(
                zip(ordered_group_roles[:-1], ordered_group_roles[1:], strict=False)
            )
        edge_role = (
            "basin_patch_spindle_pair"
            if connectivity == "spindle"
            else "basin_patch_group_pair"
        )
        weight_multiplier = 1.15 if group_name == "stable" else 0.65
        grouped_specs.extend(
            (
                support_node_ids_by_role[source_role],
                support_node_ids_by_role[target_role],
                edge_role,
                str(group_name),
                weight_multiplier,
            )
            for source_role, target_role in role_pairs
        )
    if grouped_specs:
        return grouped_specs
    return [
        (
            support_node_ids_by_role[ordered_roles[index]],
            support_node_ids_by_role[ordered_roles[(index + 1) % len(ordered_roles)]],
            "basin_patch_ring",
            role_group_by_role.get(ordered_roles[index]),
            1.0,
        )
        for index in range(len(ordered_roles))
    ]


def _native_partition_transfer_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    probe_node_ids_by_role: Mapping[str, int],
    load_node_ids_by_role: Mapping[str, int],
) -> list[_NativeStructuralEdgeSpec]:
    if plan.interior_partition is None:
        return []
    ordered_roles = [
        role
        for role in plan.interior_partition.attachment_transfer_roles
        if role in probe_node_ids_by_role and role in load_node_ids_by_role
    ]
    if not ordered_roles:
        return []
    load_group_by_role = _native_partition_load_group_by_role(plan.interior_partition)
    weight_scale = _PARTITION_TRANSFER_WEIGHT_SCALE.get(
        str(plan.interior_partition.load_transfer_mode),
        0.8,
    )
    return [
        _NativeStructuralEdgeSpec(
            source_node_id=probe_node_ids_by_role[role],
            target_node_id=load_node_ids_by_role[role],
            edge_role="basin_patch_partition_transfer",
            load_group=load_group_by_role.get(role),
            weight_multiplier=float(weight_scale),
            metadata=MappingProxyType(
                {
                    "transfer_kind": "partition_pair",
                    "transfer_role": str(role),
                }
            ),
        )
        for role in ordered_roles
    ]


def _native_load_carrier_transfer_specs(
    plan: GRCV3NativeBasinLikePlan,
    *,
    probe_node_ids_by_role: Mapping[str, int],
    carrier_node_ids_by_role: Mapping[str, int],
    path_node_ids_by_pair: Mapping[tuple[str, str], int],
    fan_in_node_ids_by_probe_role: Mapping[str, int],
) -> list[_NativeStructuralEdgeSpec]:
    if plan.interior_load_carriers is None:
        return []
    load_group_by_role = _native_partition_load_group_by_role(plan.interior_partition)
    topology_scale = _LOAD_CARRIER_TRANSFER_WEIGHT_SCALE.get(
        str(plan.interior_load_carriers.transfer_topology_mode),
        0.7,
    )
    mediation_class_by_pair = _native_transfer_mediation_class_by_pair(plan)
    path_topology_by_pair = _native_transfer_path_topology_by_pair(plan)
    if plan.transfer_mediation is None:
        mode_scale = 1.0
        spill_scale = 0.0
        probe_guard_class = None
        lateral_spill_policy = None
        spill_branch_mode = "carrier_branch"
        mediation_mode = None
    else:
        mode_scale = _TRANSFER_MEDIATION_MODE_WEIGHT_SCALE.get(
            str(plan.transfer_mediation.mediation_mode),
            1.0,
        )
        spill_scale = _TRANSFER_MEDIATION_SPILL_SCALE.get(
            str(plan.transfer_mediation.lateral_spill_policy),
            0.0,
        )
        probe_guard_class = str(plan.transfer_mediation.probe_guard_class)
        lateral_spill_policy = str(plan.transfer_mediation.lateral_spill_policy)
        spill_branch_mode = _native_transfer_spill_branch_mode(plan)
        mediation_mode = str(plan.transfer_mediation.mediation_mode)
    specs: list[_NativeStructuralEdgeSpec] = []
    fan_in_egress_specs: dict[str, dict[str, object]] = {}
    path_edge_weight_scale = float(_TRANSFER_PATH_EDGE_WEIGHT_SCALE)
    for carrier_role, probe_role in plan.interior_load_carriers.transfer_role_pairs:
        carrier_node_id = carrier_node_ids_by_role.get(carrier_role)
        probe_node_id = probe_node_ids_by_role.get(probe_role)
        if carrier_node_id is None or probe_node_id is None:
            continue
        mediation_class = mediation_class_by_pair.get((str(carrier_role), str(probe_role)))
        class_scale = (
            1.0
            if mediation_class is None
            else _TRANSFER_MEDIATION_PAIR_CLASS_WEIGHT_SCALE.get(str(mediation_class), 1.0)
        )
        main_weight_scale = float(topology_scale) * float(mode_scale) * float(class_scale)
        topology_class = path_topology_by_pair.get((str(carrier_role), str(probe_role)), "direct")
        spill_source_node_id = carrier_node_id
        spill_transfer_kind = "carrier_spill"
        if main_weight_scale > 0.0 and topology_class == "direct":
            specs.append(
                _NativeStructuralEdgeSpec(
                    source_node_id=carrier_node_id,
                    target_node_id=probe_node_id,
                    edge_role="basin_patch_load_carrier_transfer",
                    load_group=load_group_by_role.get(carrier_role),
                    weight_multiplier=float(main_weight_scale),
                    metadata=MappingProxyType(
                        {
                            "transfer_kind": "carrier_pair",
                            "carrier_role": str(carrier_role),
                            "probe_role": str(probe_role),
                            "mediation_class": mediation_class,
                            "mediation_mode": mediation_mode,
                            "probe_guard_class": probe_guard_class,
                            "lateral_spill_policy": lateral_spill_policy,
                            "spill_branch_mode": spill_branch_mode,
                            "transfer_path_topology_class": topology_class,
                        }
                    ),
                )
            )
        elif main_weight_scale > 0.0 and topology_class == "single_intermediate":
            path_node_id = path_node_ids_by_pair.get((str(carrier_role), str(probe_role)))
            if path_node_id is None:
                raise InvalidLandscapeSeedError(
                    f"family-native transfer path for {(carrier_role, probe_role)!r} requires "
                    "a realized path node"
                )
            ingress_metadata = {
                "transfer_kind": "carrier_path_ingress",
                "carrier_role": str(carrier_role),
                "probe_role": str(probe_role),
                "mediation_class": mediation_class,
                "mediation_mode": mediation_mode,
                "probe_guard_class": probe_guard_class,
                "lateral_spill_policy": lateral_spill_policy,
                "spill_branch_mode": spill_branch_mode,
                "transfer_path_topology_class": topology_class,
            }
            specs.append(
                _NativeStructuralEdgeSpec(
                    source_node_id=carrier_node_id,
                    target_node_id=path_node_id,
                    edge_role="basin_patch_transfer_path_ingress",
                    load_group=load_group_by_role.get(carrier_role),
                    weight_multiplier=float(main_weight_scale) * float(path_edge_weight_scale),
                    metadata=MappingProxyType(ingress_metadata),
                )
            )
            specs.append(
                _NativeStructuralEdgeSpec(
                    source_node_id=path_node_id,
                    target_node_id=probe_node_id,
                    edge_role="basin_patch_transfer_path_egress",
                    load_group=load_group_by_role.get(carrier_role),
                    weight_multiplier=float(main_weight_scale) * float(path_edge_weight_scale),
                    metadata=MappingProxyType(
                        {
                            **ingress_metadata,
                            "transfer_kind": "path_probe_egress",
                        }
                    ),
                )
            )
            if spill_branch_mode == "mediated_branch":
                spill_source_node_id = path_node_id
                spill_transfer_kind = "path_spill"
        elif main_weight_scale > 0.0 and topology_class == "fan_in":
            path_node_id = fan_in_node_ids_by_probe_role.get(str(probe_role))
            if path_node_id is None:
                raise InvalidLandscapeSeedError(
                    f"family-native fan_in path for probe role {probe_role!r} requires "
                    "a realized shared path node"
                )
            ingress_metadata = {
                "transfer_kind": "carrier_path_ingress",
                "carrier_role": str(carrier_role),
                "probe_role": str(probe_role),
                "mediation_class": mediation_class,
                "mediation_mode": mediation_mode,
                "probe_guard_class": probe_guard_class,
                "lateral_spill_policy": lateral_spill_policy,
                "spill_branch_mode": spill_branch_mode,
                "transfer_path_topology_class": topology_class,
            }
            specs.append(
                _NativeStructuralEdgeSpec(
                    source_node_id=carrier_node_id,
                    target_node_id=path_node_id,
                    edge_role="basin_patch_transfer_path_ingress",
                    load_group=load_group_by_role.get(carrier_role),
                    weight_multiplier=float(main_weight_scale) * float(path_edge_weight_scale),
                    metadata=MappingProxyType(ingress_metadata),
                )
            )
            probe_key = str(probe_role)
            egress_bucket = fan_in_egress_specs.setdefault(
                probe_key,
                {
                    "source_node_id": path_node_id,
                    "target_node_id": probe_node_id,
                    "carrier_roles": [],
                    "weight_multipliers": [],
                },
            )
            carrier_roles = egress_bucket["carrier_roles"]
            weight_multipliers = egress_bucket["weight_multipliers"]
            assert isinstance(carrier_roles, list)
            assert isinstance(weight_multipliers, list)
            carrier_roles.append(str(carrier_role))
            weight_multipliers.append(float(main_weight_scale))
            if spill_branch_mode == "mediated_branch":
                spill_source_node_id = path_node_id
                spill_transfer_kind = "path_spill"
        if spill_scale <= 0.0 or mediation_class == "blocked":
            continue
        for spill_role in _native_transfer_spill_roles_for_target(plan, str(probe_role)):
            spill_node_id = probe_node_ids_by_role.get(spill_role)
            if spill_node_id is None:
                continue
            specs.append(
                _NativeStructuralEdgeSpec(
                    source_node_id=spill_source_node_id,
                    target_node_id=spill_node_id,
                    edge_role="basin_patch_transfer_mediation_spill",
                    load_group=load_group_by_role.get(carrier_role),
                    weight_multiplier=float(main_weight_scale) * float(spill_scale),
                    metadata=MappingProxyType(
                        {
                            "transfer_kind": spill_transfer_kind,
                            "carrier_role": str(carrier_role),
                            "probe_role": str(probe_role),
                            "spill_role": str(spill_role),
                            "mediation_class": mediation_class,
                            "mediation_mode": mediation_mode,
                            "probe_guard_class": probe_guard_class,
                            "lateral_spill_policy": lateral_spill_policy,
                            "spill_branch_mode": spill_branch_mode,
                            "transfer_path_topology_class": topology_class,
                        }
                    ),
                )
            )
    for probe_role, egress_spec in sorted(fan_in_egress_specs.items()):
        weight_multipliers = egress_spec["weight_multipliers"]
        carrier_roles = egress_spec["carrier_roles"]
        assert isinstance(weight_multipliers, list)
        assert isinstance(carrier_roles, list)
        if not weight_multipliers:
            continue
        specs.append(
            _NativeStructuralEdgeSpec(
                source_node_id=int(egress_spec["source_node_id"]),
                target_node_id=int(egress_spec["target_node_id"]),
                edge_role="basin_patch_transfer_path_egress",
                load_group=None,
                weight_multiplier=(
                    float(sum(weight_multipliers) / float(len(weight_multipliers)))
                    * float(path_edge_weight_scale)
                ),
                metadata=MappingProxyType(
                    {
                        "transfer_kind": "fan_in_probe_egress",
                        "probe_role": str(probe_role),
                        "carrier_roles": sorted(str(role) for role in carrier_roles),
                        "transfer_path_topology_class": "fan_in",
                        "mediation_mode": mediation_mode,
                        "probe_guard_class": probe_guard_class,
                        "lateral_spill_policy": lateral_spill_policy,
                        "spill_branch_mode": spill_branch_mode,
                    }
                ),
            )
        )
    return specs


def _native_attachment_allows_anchor_fallback(
    primitive_id: str,
    *,
    native_surface: GRCV3NativePrimitiveSurface | None,
) -> bool:
    if native_surface is None:
        return True
    basin_plan = native_surface.basin_like_plans.get(primitive_id)
    junction_plan = native_surface.junction_plans.get(primitive_id)
    interior_geometry = None
    if basin_plan is not None:
        interior_geometry = basin_plan.interior_geometry
    elif junction_plan is not None:
        interior_geometry = junction_plan.interior_geometry
    if interior_geometry is None:
        return True
    return str(interior_geometry.attachment_isolation) == "center_allowed"


def _patch_internal_weights(primitive_mass: float) -> tuple[float, float]:
    # Keep the semantic center more strongly coupled to the support ring than
    # the support nodes are to each other. This biases the initial patch toward
    # a coherent interior with local boundary support rather than a free ring.
    spoke_weight = max(1e-6, float(primitive_mass))
    ring_weight = max(1e-6, float(primitive_mass) * 0.5)
    return spoke_weight, ring_weight


def _ridge_support_points(
    source_point: tuple[float, float] | None,
    target_point: tuple[float, float] | None,
) -> list[tuple[float, float] | None]:
    if source_point is None or target_point is None:
        return [None for _ in range(_RIDGE_SUPPORT_NODE_COUNT)]
    return [
        (
            ((3.0 - index) * source_point[0] + (index + 1.0) * target_point[0]) / 4.0,
            ((3.0 - index) * source_point[1] + (index + 1.0) * target_point[1]) / 4.0,
        )
        for index in range(_RIDGE_SUPPORT_NODE_COUNT)
    ]


def _transport_intent_edge_multipliers_for_realized_edges(
    seed: LandscapeSeed,
    *,
    edge_ids_by_primitive_id: Mapping[str, tuple[int, ...]],
) -> dict[int, float]:
    multipliers: dict[int, float] = {}
    for intent in seed.transport_intent:
        if intent.carrier_id is None:
            continue
        edge_ids = edge_ids_by_primitive_id.get(intent.carrier_id, ())
        if not edge_ids:
            continue
        magnitude = 0.0 if intent.magnitude_hint is None else float(intent.magnitude_hint)
        priority = 0.0 if intent.priority is None else float(intent.priority)
        multiplier = max(1.0, 1.0 + magnitude + priority)
        for edge_id in edge_ids:
            multipliers[edge_id] = multipliers.get(edge_id, 1.0) * multiplier
    return multipliers


def _native_edge_directionality_semantics(primitive_type: str) -> str:
    if primitive_type == "ridge":
        return "structural_support"
    if primitive_type == "valley":
        return "transport_channel"
    return "runtime_oriented_edge"


def _native_edge_weight_from_valley_plan(
    plan: GRCV3NativeValleyPlan,
    *,
    node_mass_by_primitive_id: Mapping[str, float],
) -> float:
    base = (
        float(plan.coherence_prior)
        if plan.coherence_prior is not None
        else 0.5
        * (
            node_mass_by_primitive_id[plan.source_primitive_id]
            + node_mass_by_primitive_id[plan.target_primitive_id]
        )
    )
    width = 0.0 if plan.width_hint is None else float(plan.width_hint)
    return max(1e-6, base / (1.0 + width))


def _native_edge_weight_from_ridge_plan(
    plan: GRCV3NativeRidgePlan,
    *,
    node_mass_by_primitive_id: Mapping[str, float],
) -> float:
    interior_value = (
        float(plan.interior_coherence_hint)
        if isinstance(plan.interior_coherence_hint, int | float)
        else node_mass_by_primitive_id[plan.source_primitive_id]
    )
    exterior_value = (
        float(plan.exterior_coherence_hint)
        if isinstance(plan.exterior_coherence_hint, int | float)
        else node_mass_by_primitive_id.get(
            "" if plan.target_primitive_id is None else plan.target_primitive_id,
            node_mass_by_primitive_id[plan.source_primitive_id],
        )
    )
    width = 0.0 if plan.thickness_hint is None else float(plan.thickness_hint)
    return max(1e-6, (0.5 * (interior_value + exterior_value)) / (1.0 + width))


def _build_grcv3_state_from_projection(
    request: GRCV3LandscapeProjectionRequest,
    blueprint: GRCV2LandscapeBlueprint | None,
    *,
    rich_seed_extension: GRCV3RichSeedExtension | None,
    lowering_lane: str,
    native_surface: GRCV3NativePrimitiveSurface | None,
) -> GRCV3State:
    topology = WeightedGraphBackend()
    node_id_by_primitive_id: dict[str, int] = {}
    node_ids_by_primitive_id: dict[str, list[int]] = {}
    support_node_ids_by_primitive_id: dict[str, list[int]] = {}
    interface_node_ids_by_primitive_id: dict[str, list[int]] = {}
    rich_branch_node_ids_by_target: dict[str, dict[str, int]] = {}
    role_node_ids_by_primitive_id: dict[str, dict[str, int]] = {}
    probe_role_node_ids_by_primitive_id: dict[str, dict[str, int]] = {}
    load_role_node_ids_by_primitive_id: dict[str, dict[str, int]] = {}
    carrier_role_node_ids_by_primitive_id: dict[str, dict[str, int]] = {}
    transfer_path_node_ids_by_pair_by_primitive_id: dict[
        str, dict[tuple[str, str], int]
    ] = {}
    transfer_fan_in_node_ids_by_probe_by_primitive_id: dict[str, dict[str, int]] = {}
    realized_node_id_by_key: dict[str, int] = {}
    node_center_by_id: dict[int, tuple[float, float] | None] = {}
    node_specs, node_blueprint_by_primitive_id, primitive_raw_node_masses = _build_node_specs(
        request,
        blueprint,
        lowering_lane=lowering_lane,
        native_surface=native_surface,
        rich_seed_extension=rich_seed_extension,
    )
    primitive_depths = _primitive_depth_index(request.seed)
    valley_channel_specs_by_primitive_id: dict[str, list[_RealizedNodeSpec]] = {}
    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None:
        target_center_by_primitive_id = {
            primitive_id: plan.chart_center_hint
            for primitive_id, plan in native_surface.basin_like_plans.items()
        }
        target_center_by_primitive_id.update(
            {
                primitive_id: plan.chart_center_hint
                for primitive_id, plan in native_surface.junction_plans.items()
            }
        )
        for primitive_id, plan in native_surface.valley_plans.items():
            valley_channel_specs_by_primitive_id[primitive_id] = _build_native_valley_channel_specs(
                plan,
                source_center=target_center_by_primitive_id.get(plan.source_primitive_id),
                target_center=target_center_by_primitive_id.get(plan.target_primitive_id),
                rich_contract_version=native_surface.rich_contract_version,
            )
            node_specs.extend(valley_channel_specs_by_primitive_id[primitive_id])
    else:
        if blueprint is None:
            raise InvalidLandscapeSeedError(
                "compatibility lowering requires a realized GRCV2 blueprint"
            )
        for edge_blueprint in blueprint.edge_blueprints:
            if edge_blueprint.primitive_type != "valley":
                continue
            rich_primitive_extension = _rich_extension_for_primitive(
                rich_seed_extension,
                edge_blueprint.primitive_id,
            )
            valley_channel_specs_by_primitive_id[edge_blueprint.primitive_id] = _build_valley_channel_specs(
                edge_blueprint,
                node_blueprint_by_primitive_id=node_blueprint_by_primitive_id,
                primitive_depths=primitive_depths,
                rich_primitive_extension=rich_primitive_extension,
                rich_contract_version=(
                    None if rich_seed_extension is None else rich_seed_extension.contract_version
                ),
            )
            node_specs.extend(valley_channel_specs_by_primitive_id[edge_blueprint.primitive_id])

    total_raw_mass = float(sum(spec.raw_mass for spec in node_specs))
    budget_target = (
        float(request.seed.constitutive_profile.budget_b)
        if request.seed.constitutive_profile.budget_b is not None
        else total_raw_mass
    )
    if total_raw_mass <= 0.0:
        raise InvalidLandscapeSeedError(
            "projected GRCV3 node priors must sum to a positive initial mass"
        )
    mass_scale = budget_target / total_raw_mass

    for spec in node_specs:
        node_payload = {
            "primitive_id": spec.source_primitive_id,
            "primitive_type": spec.source_primitive_type,
            "role": spec.role,
            "parent_id": spec.parent_id,
            "chart_center_hint": spec.chart_center_hint,
            "chart_scale_hint": _to_plain_data(spec.chart_scale_hint),
            "metadata": _to_plain_data(spec.metadata),
            "realized_key": spec.realized_key,
            "motif_role": spec.motif_role,
            "semantic_anchor": spec.semantic_anchor,
        }
        if "junction_anchor_mode" in spec.metadata:
            node_payload["is_hostless"] = bool(spec.metadata.get("is_hostless", False))
            node_payload["junction_anchor_mode"] = spec.metadata.get(
                "junction_anchor_mode",
                "hosted",
            )
        node_id = topology.add_node(node_payload)
        realized_node_id_by_key[spec.realized_key] = node_id
        node_center_by_id[node_id] = spec.chart_center_hint
        node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(node_id)
        if spec.semantic_anchor and spec.source_primitive_id not in node_id_by_primitive_id:
            node_id_by_primitive_id[spec.source_primitive_id] = node_id
        partition_tier = spec.metadata.get("grcv3_partition_tier")
        if spec.motif_role == "basin_support":
            support_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(node_id)
            if partition_tier != "probe_shell":
                interface_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(
                    node_id
                )
        if spec.motif_role == "basin_load_shell":
            interface_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(node_id)
        if spec.motif_role == "basin_load_carrier":
            interface_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(node_id)
        if spec.motif_role == "basin_transfer_path_node":
            path_scope = spec.metadata.get("grcv3_transfer_path_scope")
            carrier_role = spec.metadata.get("grcv3_transfer_carrier_role")
            probe_role = spec.metadata.get("grcv3_transfer_probe_role")
            if path_scope == "pair" and isinstance(carrier_role, str) and isinstance(probe_role, str):
                transfer_path_node_ids_by_pair_by_primitive_id.setdefault(
                    spec.source_primitive_id, {}
                )[(carrier_role, probe_role)] = node_id
            elif path_scope == "probe_fan_in" and isinstance(probe_role, str):
                transfer_fan_in_node_ids_by_probe_by_primitive_id.setdefault(
                    spec.source_primitive_id, {}
                )[probe_role] = node_id
        if spec.motif_role == "junction_branch":
            interface_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, []).append(node_id)
            rich_target_primitive_id = spec.metadata.get("grcv3_rich_target_primitive_id")
            if isinstance(rich_target_primitive_id, str) and rich_target_primitive_id:
                rich_branch_node_ids_by_target.setdefault(spec.source_primitive_id, {})[
                    rich_target_primitive_id
                ] = node_id
        role_label = spec.metadata.get("grcv3_role_label")
        if isinstance(role_label, str) and role_label:
            if partition_tier == "probe_shell":
                probe_role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
            elif partition_tier == "load_shell":
                load_role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
                role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
            elif partition_tier == "load_carrier":
                carrier_role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
                load_role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
                role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
            else:
                role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                    role_label
                ] = node_id
        rich_branch_role = spec.metadata.get("grcv3_rich_branch_role")
        if isinstance(rich_branch_role, str) and rich_branch_role:
            role_node_ids_by_primitive_id.setdefault(spec.source_primitive_id, {})[
                rich_branch_role
            ] = node_id

    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None:
        for primitive_id, plan in native_surface.basin_like_plans.items():
            if plan.primitive_type != "plateau":
                continue
            plateau_payload = topology.node_payload(node_id_by_primitive_id[primitive_id])
            plateau_payload["contained_primitive_ids"] = list(plan.hosted_primitive_ids)
            plateau_payload["contained_node_ids"] = [
                node_id_by_primitive_id[hosted_id]
                for hosted_id in plan.hosted_primitive_ids
                if hosted_id in node_id_by_primitive_id
            ]
    else:
        if blueprint is None:
            raise InvalidLandscapeSeedError(
                "compatibility lowering requires a realized GRCV2 blueprint"
            )
        for blueprint_node in blueprint.node_blueprints:
            if blueprint_node.primitive_type != "plateau":
                continue
            hosted_primitive_ids = tuple(blueprint_node.metadata.get("hosted_primitive_ids", ()))
            plateau_payload = topology.node_payload(node_id_by_primitive_id[blueprint_node.primitive_id])
            plateau_payload["contained_primitive_ids"] = list(hosted_primitive_ids)
            plateau_payload["contained_node_ids"] = [
                node_id_by_primitive_id[primitive_id]
                for primitive_id in hosted_primitive_ids
                if primitive_id in node_id_by_primitive_id
            ]

    base_conductance: dict[int, float] = {}
    edge_id_by_primitive_id: dict[str, int] = {}
    edge_ids_by_primitive_id: dict[str, list[int]] = {}
    geometric_length: dict[int, float] = {}
    skipped_patch_ids: list[str] = []
    realized_ridge_support_node_ids: dict[str, list[int]] = {}
    ridge_support_attributes_by_node_id: dict[int, BasinAttributes] = {}
    primitive_member_mass_by_id = {
        primitive_id: float(sum(spec.raw_mass for spec in node_specs if spec.source_primitive_id == primitive_id))
        for primitive_id in sorted({spec.source_primitive_id for spec in node_specs})
    }

    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None:
        patch_primitive_ids = tuple(native_surface.basin_like_plans)
    else:
        if blueprint is None:
            raise InvalidLandscapeSeedError(
                "compatibility lowering requires a realized GRCV2 blueprint"
            )
        patch_primitive_ids = tuple(
            blueprint_node.primitive_id
            for blueprint_node in blueprint.node_blueprints
            if blueprint_node.primitive_type == "basin"
        )
    for primitive_id in patch_primitive_ids:
        member_node_ids = node_ids_by_primitive_id.get(primitive_id, [])
        if len(member_node_ids) < 4:
            skipped_patch_ids.append(primitive_id)
            continue
        center_node_id = node_id_by_primitive_id[primitive_id]
        support_node_ids = tuple(support_node_ids_by_primitive_id.get(primitive_id, ()))
        interface_node_ids = tuple(interface_node_ids_by_primitive_id.get(primitive_id, ()))
        native_basin_plan = (
            None
            if lowering_lane != LOWERING_LANE_FAMILY_NATIVE or native_surface is None
            else native_surface.basin_like_plans.get(primitive_id)
        )
        primitive_type = (
            native_basin_plan.primitive_type
            if native_basin_plan is not None
            else node_blueprint_by_primitive_id[primitive_id].primitive_type
        )
        primitive_role = (
            native_basin_plan.role
            if native_basin_plan is not None
            else node_blueprint_by_primitive_id[primitive_id].role
        )
        source_metadata = (
            {}
            if native_basin_plan is not None
            else _to_plain_data(node_blueprint_by_primitive_id[primitive_id].metadata)
        )
        if not support_node_ids and interface_node_ids:
            primitive_mass = primitive_raw_node_masses[primitive_id]
            spoke_weight, _ = _patch_internal_weights(primitive_mass)
            for index, branch_node_id in enumerate(interface_node_ids):
                edge_payload = {
                    "primitive_id": primitive_id,
                    "primitive_type": primitive_type,
                    "role": primitive_role,
                    "path_hint": "junction_branch_spoke",
                    "directionality_semantics": "structural_support",
                    "metadata": {
                        "motif_edge_role": "junction_branch_spoke",
                        "motif_index": index,
                        "source_metadata": source_metadata,
                    },
                }
                edge_id = topology.add_edge(center_node_id, branch_node_id, edge_payload)
                edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
                base_conductance[edge_id] = float(spoke_weight)
                ambient_length = _euclidean_length(
                    node_center_by_id.get(center_node_id),
                    node_center_by_id.get(branch_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            continue
        if len(support_node_ids) < 3:
            if interface_node_ids_by_primitive_id.get(primitive_id):
                continue
            skipped_patch_ids.append(primitive_id)
            continue
        if (
            native_basin_plan is not None
            and native_basin_plan.interior_geometry is not None
            and native_basin_plan.role_order
        ):
            primitive_mass = primitive_raw_node_masses[primitive_id]
            base_spoke_weight, base_ring_weight = _patch_internal_weights(primitive_mass)
            probe_node_ids_by_role = probe_role_node_ids_by_primitive_id.get(primitive_id, {})
            if not probe_node_ids_by_role:
                probe_node_ids_by_role = role_node_ids_by_primitive_id.get(primitive_id, {})
            support_node_ids_by_role: dict[str, int] = {}
            for role_label in native_basin_plan.role_order:
                role_node_id = probe_node_ids_by_role.get(role_label)
                if role_node_id is None:
                    raise InvalidLandscapeSeedError(
                        f"family-native interior geometry for {primitive_id!r} requires "
                        f"a realized role node for {role_label!r}"
                    )
                support_node_ids_by_role[role_label] = role_node_id
            for index, role_label in enumerate(native_basin_plan.role_order):
                support_node_id = support_node_ids_by_role[role_label]
                support_profile = _native_support_profile_value(native_basin_plan, role_label)
                edge_payload = {
                    "primitive_id": primitive_id,
                    "primitive_type": primitive_type,
                    "role": primitive_role,
                    "path_hint": "basin_patch_support_spoke",
                    "directionality_semantics": "structural_support",
                    "metadata": {
                        "motif_edge_role": "basin_patch_support_spoke",
                        "motif_index": index,
                        "source_metadata": source_metadata,
                        "grcv3_support_profile": support_profile,
                        "grcv3_attachment_isolation": (
                            native_basin_plan.interior_geometry.attachment_isolation
                        ),
                        "grcv3_support_connectivity": (
                            native_basin_plan.interior_geometry.support_connectivity
                        ),
                        "grcv3_transfer_center_coupling_class": (
                            _native_center_coupling_class_by_role(native_basin_plan).get(role_label)
                        ),
                    },
                }
                support_spoke_weight = _native_support_spoke_weight(
                    base_spoke_weight,
                    profile_value=support_profile,
                    clearance_class=(
                        native_basin_plan.interior_geometry.interior_clearance_class
                    ),
                )
                support_spoke_weight *= _native_transfer_center_spoke_scale(
                    native_basin_plan,
                    role_label,
                )
                if support_spoke_weight <= 0.0:
                    continue
                edge_id = topology.add_edge(center_node_id, support_node_id, edge_payload)
                edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
                base_conductance[edge_id] = max(1e-6, float(support_spoke_weight))
                ambient_length = _euclidean_length(
                    node_center_by_id.get(center_node_id),
                    node_center_by_id.get(support_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            if native_basin_plan.interior_load_carriers is not None:
                load_node_ids_by_role = carrier_role_node_ids_by_primitive_id.get(
                    primitive_id, {}
                )
                transfer_edge_specs = _native_load_carrier_transfer_specs(
                    native_basin_plan,
                    probe_node_ids_by_role=support_node_ids_by_role,
                    carrier_node_ids_by_role=load_node_ids_by_role,
                    path_node_ids_by_pair=transfer_path_node_ids_by_pair_by_primitive_id.get(
                        primitive_id, {}
                    ),
                    fan_in_node_ids_by_probe_role=(
                        transfer_fan_in_node_ids_by_probe_by_primitive_id.get(
                            primitive_id, {}
                        )
                    ),
                )
            else:
                load_node_ids_by_role = load_role_node_ids_by_primitive_id.get(
                    primitive_id, {}
                )
                transfer_edge_specs = _native_partition_transfer_specs(
                    native_basin_plan,
                    probe_node_ids_by_role=support_node_ids_by_role,
                    load_node_ids_by_role=load_node_ids_by_role,
                )
            for index, transfer_edge_spec in enumerate(transfer_edge_specs):
                edge_payload = {
                    "primitive_id": primitive_id,
                    "primitive_type": primitive_type,
                    "role": primitive_role,
                    "path_hint": transfer_edge_spec.edge_role,
                    "directionality_semantics": "structural_support",
                    "metadata": {
                        "motif_edge_role": transfer_edge_spec.edge_role,
                        "motif_index": index,
                        "source_metadata": source_metadata,
                        "grcv3_partition_mode": native_basin_plan.interior_partition.partition_mode,
                        "grcv3_load_transfer_mode": (
                            native_basin_plan.interior_partition.load_transfer_mode
                        ),
                        "grcv3_probe_protection_class": (
                            native_basin_plan.interior_partition.probe_protection_class
                        ),
                        "grcv3_partition_load_group": transfer_edge_spec.load_group,
                        "grcv3_load_carrier_transfer_topology_mode": (
                            None
                            if native_basin_plan.interior_load_carriers is None
                            else native_basin_plan.interior_load_carriers.transfer_topology_mode
                        ),
                        **dict(transfer_edge_spec.metadata),
                    },
                }
                edge_id = topology.add_edge(
                    transfer_edge_spec.source_node_id,
                    transfer_edge_spec.target_node_id,
                    edge_payload,
                )
                edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
                base_conductance[edge_id] = max(
                    1e-6,
                    float(base_ring_weight) * float(transfer_edge_spec.weight_multiplier),
                )
                ambient_length = _euclidean_length(
                    node_center_by_id.get(transfer_edge_spec.source_node_id),
                    node_center_by_id.get(transfer_edge_spec.target_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            connectivity_multiplier = _SUPPORT_CONNECTIVITY_WEIGHT_MULTIPLIERS.get(
                str(native_basin_plan.interior_geometry.support_connectivity),
                1.0,
            )
            clearance_support_scale = _INTERIOR_CLEARANCE_SUPPORT_SCALE.get(
                str(native_basin_plan.interior_geometry.interior_clearance_class),
                1.0,
            )
            support_edge_specs = _native_support_edge_specs(
                native_basin_plan,
                support_node_ids_by_role=support_node_ids_by_role,
            )
            base_support_weight = max(
                1e-6,
                base_ring_weight
                * float(connectivity_multiplier)
                * float(clearance_support_scale),
            )
            for index, (
                source_node_id,
                target_node_id,
                edge_role,
                role_group,
                weight_multiplier,
            ) in enumerate(support_edge_specs):
                edge_payload = {
                    "primitive_id": primitive_id,
                    "primitive_type": primitive_type,
                    "role": primitive_role,
                    "path_hint": edge_role,
                    "directionality_semantics": "structural_support",
                    "metadata": {
                        "motif_edge_role": edge_role,
                        "motif_index": index,
                        "source_metadata": source_metadata,
                        "grcv3_support_connectivity": (
                            native_basin_plan.interior_geometry.support_connectivity
                        ),
                        "grcv3_support_role_group": role_group,
                    },
                }
                edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
                edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
                base_conductance[edge_id] = max(
                    1e-6,
                    float(base_support_weight) * float(weight_multiplier),
                )
                ambient_length = _euclidean_length(
                    node_center_by_id.get(source_node_id),
                    node_center_by_id.get(target_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            continue
        primitive_mass = primitive_raw_node_masses[primitive_id]
        spoke_weight, ring_weight = _patch_internal_weights(primitive_mass)
        ordered_ring_edges = tuple(
            (
                support_node_ids[index],
                support_node_ids[(index + 1) % len(support_node_ids)],
            )
            for index in range(len(support_node_ids))
        )
        for index, support_node_id in enumerate(support_node_ids):
            edge_payload = {
                "primitive_id": primitive_id,
                "primitive_type": primitive_type,
                "role": primitive_role,
                "path_hint": "basin_patch_spoke",
                "directionality_semantics": "structural_support",
                "metadata": {
                    "motif_edge_role": "basin_patch_spoke",
                    "motif_index": index,
                    "source_metadata": source_metadata,
                },
            }
            edge_id = topology.add_edge(center_node_id, support_node_id, edge_payload)
            edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
            edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
            base_conductance[edge_id] = float(spoke_weight)
            source_center = node_center_by_id.get(center_node_id)
            target_center = node_center_by_id.get(support_node_id)
            ambient_length = _euclidean_length(source_center, target_center)
            if ambient_length is not None:
                geometric_length[edge_id] = max(1e-12, ambient_length)
                topology.edge_payload(edge_id)["ambient_length"] = ambient_length
        for index, (source_node_id, target_node_id) in enumerate(ordered_ring_edges):
            edge_payload = {
                "primitive_id": primitive_id,
                "primitive_type": primitive_type,
                "role": primitive_role,
                "path_hint": "basin_patch_ring",
                "directionality_semantics": "structural_support",
                "metadata": {
                    "motif_edge_role": "basin_patch_ring",
                    "motif_index": index,
                    "source_metadata": source_metadata,
                },
            }
            edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
            edge_ids_by_primitive_id.setdefault(primitive_id, []).append(edge_id)
            edge_id_by_primitive_id.setdefault(primitive_id, edge_id)
            base_conductance[edge_id] = float(ring_weight)
            source_center = node_center_by_id.get(source_node_id)
            target_center = node_center_by_id.get(target_node_id)
            ambient_length = _euclidean_length(source_center, target_center)
            if ambient_length is not None:
                geometric_length[edge_id] = max(1e-12, ambient_length)
                topology.edge_payload(edge_id)["ambient_length"] = ambient_length

    for edge_blueprint in blueprint.edge_blueprints:
        if edge_blueprint.primitive_type == "ridge":
            ridge_plan = (
                None
                if native_surface is None
                else native_surface.ridge_plans.get(edge_blueprint.primitive_id)
            )
            if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and ridge_plan is not None:
                if ridge_plan.metadata_only:
                    continue
                source_center = node_center_by_id.get(
                    node_id_by_primitive_id[ridge_plan.source_primitive_id]
                )
                target_center = (
                    None
                    if ridge_plan.target_primitive_id is None
                    else node_center_by_id.get(node_id_by_primitive_id[ridge_plan.target_primitive_id])
                )
                owner_basin_plan = None if native_surface is None else native_surface.basin_like_plans.get(
                    ridge_plan.source_primitive_id
                )
                owner_role_order = () if owner_basin_plan is None else owner_basin_plan.role_order
                owner_role_angle_map = {
                    role: angle
                    for role, angle in zip(
                        owner_role_order,
                        _angles_for_role_order(owner_role_order),
                        strict=False,
                    )
                }
                support_points = _ridge_support_points_from_geometry(
                    source_center,
                    primitive_radius=_primitive_radius(
                        MappingProxyType({})
                        if owner_basin_plan is None
                        else owner_basin_plan.chart_scale_hint
                    ),
                    role_angle_map=owner_role_angle_map,
                    boundary_geometry=ridge_plan.boundary_geometry,
                )
                ridge_support_node_ids: list[int] = []
                for index, support_point in enumerate(support_points):
                    support_payload = {
                        "primitive_id": ridge_plan.primitive_id,
                        "primitive_type": ridge_plan.primitive_type,
                        "role": ridge_plan.role,
                        "parent_id": ridge_plan.source_primitive_id,
                        "chart_center_hint": support_point,
                        "chart_scale_hint": {},
                        "metadata": {
                            "motif_role": "ridge_support",
                            "motif_index": index,
                            "semantic_anchor": False,
                            "source_metadata": {
                                "ridge_kind": ridge_plan.ridge_kind,
                                "thickness_hint": ridge_plan.thickness_hint,
                                "interior_coherence_hint": ridge_plan.interior_coherence_hint,
                                "exterior_coherence_hint": ridge_plan.exterior_coherence_hint,
                                "adjacent_ids": list(ridge_plan.adjacent_ids),
                            },
                            "source_role": ridge_plan.role,
                            "source_owner_id": ridge_plan.source_primitive_id,
                            "source_target_id": ridge_plan.target_primitive_id,
                            "grcv3_rich_contract_version": native_surface.rich_contract_version,
                            "grcv3_rich": True,
                            "grcv3_rich_boundary_realization_kind": (
                                None
                                if ridge_plan.boundary_geometry is None
                                else ridge_plan.boundary_geometry.realization_kind
                            ),
                            "grcv3_native_lowering": True,
                        },
                        "realized_key": f"{ridge_plan.primitive_id}::ridge_support:{index}",
                        "motif_role": "ridge_support",
                        "semantic_anchor": False,
                    }
                    node_id = topology.add_node(support_payload)
                    node_center_by_id[node_id] = support_point
                    node_ids_by_primitive_id.setdefault(ridge_plan.primitive_id, []).append(node_id)
                    ridge_support_node_ids.append(node_id)
                    ridge_support_attributes_by_node_id[node_id] = BasinAttributes(
                        coherence=0.0,
                        gradient=[],
                        hessian=[],
                        net_flux=[],
                        basin_mass=0.0,
                        basin_id=ridge_plan.primitive_id,
                        parent_id=ridge_plan.source_primitive_id,
                        depth=primitive_depths.get(ridge_plan.source_primitive_id, 0),
                    )
                realized_ridge_support_node_ids[ridge_plan.primitive_id] = list(ridge_support_node_ids)
                boundary_label = None if not ridge_plan.boundary_roles else ridge_plan.boundary_roles[0]
                source_attach_node_id = _node_id_for_role(
                    ridge_plan.source_primitive_id,
                    ridge_plan.preferred_attachment_sites.get(boundary_label),
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
                if source_attach_node_id is None:
                    source_attach_node_id = _node_id_for_role(
                        ridge_plan.source_primitive_id,
                        None
                        if ridge_plan.boundary_geometry is None
                        else ridge_plan.boundary_geometry.normal_role,
                        role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                    )
                if source_attach_node_id is None:
                    source_attach_node_id = _select_connection_node(
                        ridge_plan.source_primitive_id,
                        target_point=support_points[0],
                        anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                        interface_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                        },
                        support_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                        },
                        node_center_by_id=node_center_by_id,
                        allow_anchor_fallback=_native_attachment_allows_anchor_fallback(
                            ridge_plan.source_primitive_id,
                            native_surface=native_surface,
                        ),
                    )
                target_attach_node_id = _select_connection_node(
                    ridge_plan.target_primitive_id,
                    target_point=support_points[-1],
                    anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                    interface_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                    },
                    support_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                    },
                    node_center_by_id=node_center_by_id,
                    allow_anchor_fallback=_native_attachment_allows_anchor_fallback(
                        ridge_plan.target_primitive_id,
                        native_surface=native_surface,
                    ),
                )
                ridge_path = [source_attach_node_id, *ridge_support_node_ids, target_attach_node_id]
                base_weight = _native_edge_weight_from_ridge_plan(
                    ridge_plan,
                    node_mass_by_primitive_id=primitive_raw_node_masses,
                )
                for index, (source_node_id, target_node_id) in enumerate(
                    zip(ridge_path[:-1], ridge_path[1:], strict=False)
                ):
                    edge_payload = {
                        "primitive_id": ridge_plan.primitive_id,
                        "primitive_type": ridge_plan.primitive_type,
                        "role": ridge_plan.role,
                        "path_hint": "ridge_support_arc",
                        "directionality_semantics": _native_edge_directionality_semantics(
                            ridge_plan.primitive_type
                        ),
                        "metadata": {
                            "motif_edge_role": "ridge_support_segment",
                            "motif_index": index,
                            "source_metadata": {
                                "ridge_kind": ridge_plan.ridge_kind,
                                "thickness_hint": ridge_plan.thickness_hint,
                                "adjacent_ids": list(ridge_plan.adjacent_ids),
                            },
                            "grcv3_rich_contract_version": native_surface.rich_contract_version,
                            "grcv3_rich": True,
                            "grcv3_native_lowering": True,
                        },
                    }
                    edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
                    edge_ids_by_primitive_id.setdefault(ridge_plan.primitive_id, []).append(edge_id)
                    edge_id_by_primitive_id.setdefault(ridge_plan.primitive_id, edge_id)
                    base_conductance[edge_id] = float(base_weight)
                    ambient_length = _euclidean_length(
                        node_center_by_id.get(source_node_id),
                        node_center_by_id.get(target_node_id),
                    )
                    if ambient_length is not None:
                        geometric_length[edge_id] = max(1e-12, ambient_length)
                        topology.edge_payload(edge_id)["ambient_length"] = ambient_length
                continue
            if edge_blueprint.primitive_id in blueprint.metadata_only_ridge_ids:
                continue
            rich_edge_extension = _rich_extension_for_primitive(
                rich_seed_extension,
                edge_blueprint.primitive_id,
            )
            source_center = node_blueprint_by_primitive_id[
                edge_blueprint.source_primitive_id
            ].chart_center_hint
            target_center = node_blueprint_by_primitive_id[
                edge_blueprint.target_primitive_id
            ].chart_center_hint
            owner_extension = _rich_extension_for_primitive(
                rich_seed_extension,
                edge_blueprint.source_primitive_id,
            )
            support_points = _ridge_support_points_from_geometry(
                source_center,
                primitive_radius=_primitive_radius(
                    node_blueprint_by_primitive_id[edge_blueprint.source_primitive_id].chart_scale_hint
                ),
                role_angle_map=_role_angle_map_for_primitive_extension(owner_extension),
                boundary_geometry=(
                    None if rich_edge_extension is None else rich_edge_extension.boundary_geometry
                ),
            )
            ridge_support_node_ids: list[int] = []
            for index, support_point in enumerate(support_points):
                support_payload = {
                    "primitive_id": edge_blueprint.primitive_id,
                    "primitive_type": edge_blueprint.primitive_type,
                    "role": edge_blueprint.role,
                    "parent_id": edge_blueprint.source_primitive_id,
                    "chart_center_hint": support_point,
                    "chart_scale_hint": {},
                    "metadata": {
                        "motif_role": "ridge_support",
                        "motif_index": index,
                        "semantic_anchor": False,
                        "source_metadata": _to_plain_data(edge_blueprint.metadata),
                        "source_role": edge_blueprint.role,
                        "source_owner_id": edge_blueprint.source_primitive_id,
                        "source_target_id": edge_blueprint.target_primitive_id,
                        "grcv3_rich_contract_version": (
                            None if rich_seed_extension is None else rich_seed_extension.contract_version
                        ),
                        "grcv3_rich": rich_edge_extension is not None,
                        "grcv3_rich_boundary_realization_kind": (
                            None
                            if rich_edge_extension is None
                            or rich_edge_extension.boundary_geometry is None
                            else rich_edge_extension.boundary_geometry.realization_kind
                        ),
                    },
                    "realized_key": f"{edge_blueprint.primitive_id}::ridge_support:{index}",
                    "motif_role": "ridge_support",
                    "semantic_anchor": False,
                }
                node_id = topology.add_node(support_payload)
                node_center_by_id[node_id] = support_point
                node_ids_by_primitive_id.setdefault(edge_blueprint.primitive_id, []).append(node_id)
                ridge_support_node_ids.append(node_id)
                ridge_support_attributes_by_node_id[node_id] = BasinAttributes(
                    coherence=0.0,
                    gradient=[],
                    hessian=[],
                    net_flux=[],
                    basin_mass=0.0,
                    basin_id=edge_blueprint.primitive_id,
                    parent_id=edge_blueprint.source_primitive_id,
                    depth=primitive_depths.get(edge_blueprint.source_primitive_id, 0),
                )
            realized_ridge_support_node_ids[edge_blueprint.primitive_id] = list(ridge_support_node_ids)
            boundary_label = None
            if (
                rich_edge_extension is not None
                and rich_edge_extension.interfaces is not None
                and rich_edge_extension.interfaces.boundary_roles
            ):
                boundary_label = rich_edge_extension.interfaces.boundary_roles[0]
            source_attach_node_id = _node_id_for_role(
                edge_blueprint.source_primitive_id,
                _preferred_attachment_role(
                    edge_blueprint.source_primitive_id,
                    boundary_label,
                    rich_seed_extension=rich_seed_extension,
                ),
                role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
            )
            if source_attach_node_id is None:
                source_attach_node_id = _node_id_for_role(
                    edge_blueprint.source_primitive_id,
                    None
                    if rich_edge_extension is None
                    or rich_edge_extension.boundary_geometry is None
                    else rich_edge_extension.boundary_geometry.normal_role,
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
            if source_attach_node_id is None:
                source_attach_node_id = _select_connection_node(
                    edge_blueprint.source_primitive_id,
                    target_point=support_points[0],
                    anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                    interface_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                    },
                    support_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                    },
                    node_center_by_id=node_center_by_id,
                )
            target_attach_node_id = _select_connection_node(
                edge_blueprint.target_primitive_id,
                target_point=support_points[-1],
                anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                interface_node_ids_by_primitive_id={
                    key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                },
                support_node_ids_by_primitive_id={
                    key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                },
                node_center_by_id=node_center_by_id,
            )
            ridge_path = [source_attach_node_id, *ridge_support_node_ids, target_attach_node_id]
            base_weight = _edge_weight_from_blueprint(
                edge_blueprint,
                node_mass_by_primitive_id=primitive_raw_node_masses,
            )
            for index, (source_node_id, target_node_id) in enumerate(
                zip(ridge_path[:-1], ridge_path[1:], strict=False)
            ):
                edge_payload = {
                    "primitive_id": edge_blueprint.primitive_id,
                    "primitive_type": edge_blueprint.primitive_type,
                    "role": edge_blueprint.role,
                    "path_hint": "ridge_support_arc",
                    "directionality_semantics": _edge_directionality_semantics(edge_blueprint),
                    "metadata": {
                        "motif_edge_role": "ridge_support_segment",
                        "motif_index": index,
                        "source_metadata": _to_plain_data(edge_blueprint.metadata),
                        "grcv3_rich_contract_version": (
                            None if rich_seed_extension is None else rich_seed_extension.contract_version
                        ),
                        "grcv3_rich": rich_edge_extension is not None,
                    },
                }
                edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
                edge_ids_by_primitive_id.setdefault(edge_blueprint.primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(edge_blueprint.primitive_id, edge_id)
                base_conductance[edge_id] = float(base_weight)
                ambient_length = _euclidean_length(
                    node_center_by_id.get(source_node_id),
                    node_center_by_id.get(target_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            continue

        if edge_blueprint.primitive_type == "valley":
            valley_plan = (
                None
                if native_surface is None
                else native_surface.valley_plans.get(edge_blueprint.primitive_id)
            )
            if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and valley_plan is not None:
                channel_specs = valley_channel_specs_by_primitive_id.get(valley_plan.primitive_id, [])
                channel_node_ids = [realized_node_id_by_key[spec.realized_key] for spec in channel_specs]
                if not channel_node_ids:
                    continue
                channel_points = [node_center_by_id[node_id] for node_id in channel_node_ids]
                channel_label = valley_plan.channel_role
                source_attach_node_id = rich_branch_node_ids_by_target.get(
                    valley_plan.source_primitive_id, {}
                ).get(valley_plan.target_primitive_id)
                if source_attach_node_id is None:
                    source_attach_node_id = _node_id_for_role(
                        valley_plan.source_primitive_id,
                        valley_plan.preferred_attachment_sites.get(channel_label),
                        role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                    )
                if (
                    source_attach_node_id is None
                    and valley_plan.channel_geometry is not None
                ):
                    source_attach_node_id = _node_id_for_role(
                        valley_plan.source_primitive_id,
                        valley_plan.channel_geometry.entry_role,
                        role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                    )
                if source_attach_node_id is None:
                    source_attach_node_id = _select_connection_node(
                        valley_plan.source_primitive_id,
                        target_point=channel_points[0],
                        anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                        interface_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                        },
                        support_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                        },
                        node_center_by_id=node_center_by_id,
                        allow_anchor_fallback=_native_attachment_allows_anchor_fallback(
                            valley_plan.source_primitive_id,
                            native_surface=native_surface,
                        ),
                    )
                target_attach_node_id = rich_branch_node_ids_by_target.get(
                    valley_plan.target_primitive_id, {}
                ).get(valley_plan.source_primitive_id)
                if target_attach_node_id is None:
                    target_attach_node_id = _node_id_for_role(
                        valley_plan.target_primitive_id,
                        valley_plan.preferred_attachment_sites.get(channel_label),
                        role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                    )
                if (
                    target_attach_node_id is None
                    and valley_plan.channel_geometry is not None
                ):
                    target_attach_node_id = _node_id_for_role(
                        valley_plan.target_primitive_id,
                        valley_plan.channel_geometry.exit_role,
                        role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                    )
                if target_attach_node_id is None:
                    target_attach_node_id = _select_connection_node(
                        valley_plan.target_primitive_id,
                        target_point=channel_points[-1],
                        anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                        interface_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                        },
                        support_node_ids_by_primitive_id={
                            key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                        },
                        node_center_by_id=node_center_by_id,
                        allow_anchor_fallback=_native_attachment_allows_anchor_fallback(
                            valley_plan.target_primitive_id,
                            native_surface=native_surface,
                        ),
                    )
                connection_path = [source_attach_node_id, *channel_node_ids, target_attach_node_id]
                base_weight = _native_edge_weight_from_valley_plan(
                    valley_plan,
                    node_mass_by_primitive_id=primitive_raw_node_masses,
                )
                for index, (source_node_id, target_node_id) in enumerate(
                    zip(connection_path[:-1], connection_path[1:], strict=False)
                ):
                    edge_payload = {
                        "primitive_id": valley_plan.primitive_id,
                        "primitive_type": valley_plan.primitive_type,
                        "role": valley_plan.role,
                        "path_hint": valley_plan.path_hint,
                        "directionality_semantics": _native_edge_directionality_semantics(
                            valley_plan.primitive_type
                        ),
                        "metadata": {
                            "motif_edge_role": "valley_channel_segment",
                            "motif_index": index,
                            "source_metadata": {
                                "path_hint": valley_plan.path_hint,
                                "width_hint": valley_plan.width_hint,
                                "channel_role": valley_plan.channel_role,
                                "waypoints": [list(point) for point in valley_plan.waypoints],
                            },
                            "grcv3_rich_contract_version": native_surface.rich_contract_version,
                            "grcv3_rich": True,
                            "grcv3_native_lowering": True,
                        },
                    }
                    edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
                    edge_ids_by_primitive_id.setdefault(valley_plan.primitive_id, []).append(edge_id)
                    edge_id_by_primitive_id.setdefault(valley_plan.primitive_id, edge_id)
                    base_conductance[edge_id] = float(base_weight)
                    ambient_length = _euclidean_length(
                        node_center_by_id.get(source_node_id),
                        node_center_by_id.get(target_node_id),
                    )
                    if ambient_length is not None:
                        geometric_length[edge_id] = max(1e-12, ambient_length)
                        topology.edge_payload(edge_id)["ambient_length"] = ambient_length
                continue
            rich_edge_extension = _rich_extension_for_primitive(
                rich_seed_extension,
                edge_blueprint.primitive_id,
            )
            channel_specs = valley_channel_specs_by_primitive_id.get(edge_blueprint.primitive_id, [])
            channel_node_ids = [
                realized_node_id_by_key[spec.realized_key]
                for spec in channel_specs
            ]
            if not channel_node_ids:
                continue
            channel_points = [node_center_by_id[node_id] for node_id in channel_node_ids]
            channel_label = None
            if (
                rich_edge_extension is not None
                and rich_edge_extension.interfaces is not None
                and rich_edge_extension.interfaces.channel_roles
            ):
                channel_label = rich_edge_extension.interfaces.channel_roles[0]
            source_attach_node_id = rich_branch_node_ids_by_target.get(
                edge_blueprint.source_primitive_id, {}
            ).get(edge_blueprint.target_primitive_id)
            if source_attach_node_id is None:
                source_attach_node_id = _node_id_for_role(
                    edge_blueprint.source_primitive_id,
                    _preferred_attachment_role(
                        edge_blueprint.source_primitive_id,
                        channel_label,
                        rich_seed_extension=rich_seed_extension,
                    ),
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
            if source_attach_node_id is None and rich_edge_extension is not None and rich_edge_extension.channel_geometry is not None:
                source_attach_node_id = _node_id_for_role(
                    edge_blueprint.source_primitive_id,
                    rich_edge_extension.channel_geometry.entry_role,
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
            if source_attach_node_id is None:
                source_attach_node_id = _select_connection_node(
                    edge_blueprint.source_primitive_id,
                    target_point=channel_points[0],
                    anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                    interface_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                    },
                    support_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                    },
                    node_center_by_id=node_center_by_id,
                )
            target_attach_node_id = rich_branch_node_ids_by_target.get(
                edge_blueprint.target_primitive_id, {}
            ).get(edge_blueprint.source_primitive_id)
            if target_attach_node_id is None:
                target_attach_node_id = _node_id_for_role(
                    edge_blueprint.target_primitive_id,
                    _preferred_attachment_role(
                        edge_blueprint.target_primitive_id,
                        channel_label,
                        rich_seed_extension=rich_seed_extension,
                    ),
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
            if target_attach_node_id is None and rich_edge_extension is not None and rich_edge_extension.channel_geometry is not None:
                target_attach_node_id = _node_id_for_role(
                    edge_blueprint.target_primitive_id,
                    rich_edge_extension.channel_geometry.exit_role,
                    role_node_ids_by_primitive_id=role_node_ids_by_primitive_id,
                )
            if target_attach_node_id is None:
                target_attach_node_id = _select_connection_node(
                    edge_blueprint.target_primitive_id,
                    target_point=channel_points[-1],
                    anchor_node_id_by_primitive_id=node_id_by_primitive_id,
                    interface_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in interface_node_ids_by_primitive_id.items()
                    },
                    support_node_ids_by_primitive_id={
                        key: tuple(value) for key, value in support_node_ids_by_primitive_id.items()
                    },
                    node_center_by_id=node_center_by_id,
                )
            connection_path = [source_attach_node_id, *channel_node_ids, target_attach_node_id]
            base_weight = _edge_weight_from_blueprint(
                edge_blueprint,
                node_mass_by_primitive_id=primitive_raw_node_masses,
            )
            for index, (source_node_id, target_node_id) in enumerate(
                zip(connection_path[:-1], connection_path[1:], strict=False)
            ):
                edge_payload = {
                    "primitive_id": edge_blueprint.primitive_id,
                    "primitive_type": edge_blueprint.primitive_type,
                    "role": edge_blueprint.role,
                    "path_hint": edge_blueprint.path_hint,
                    "directionality_semantics": _edge_directionality_semantics(edge_blueprint),
                    "metadata": {
                        "motif_edge_role": "valley_channel_segment",
                        "motif_index": index,
                        "source_metadata": _to_plain_data(edge_blueprint.metadata),
                        "grcv3_rich_contract_version": (
                            None if rich_seed_extension is None else rich_seed_extension.contract_version
                        ),
                        "grcv3_rich": rich_edge_extension is not None,
                    },
                }
                edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
                edge_ids_by_primitive_id.setdefault(edge_blueprint.primitive_id, []).append(edge_id)
                edge_id_by_primitive_id.setdefault(edge_blueprint.primitive_id, edge_id)
                base_conductance[edge_id] = float(base_weight)
                ambient_length = _euclidean_length(
                    node_center_by_id.get(source_node_id),
                    node_center_by_id.get(target_node_id),
                )
                if ambient_length is not None:
                    geometric_length[edge_id] = max(1e-12, ambient_length)
                    topology.edge_payload(edge_id)["ambient_length"] = ambient_length
            continue

        source_node_id = node_id_by_primitive_id[edge_blueprint.source_primitive_id]
        target_node_id = node_id_by_primitive_id[edge_blueprint.target_primitive_id]
        source_center = node_center_by_id.get(source_node_id)
        target_center = node_center_by_id.get(target_node_id)
        ambient_length = _euclidean_length(source_center, target_center)
        edge_payload = {
            "primitive_id": edge_blueprint.primitive_id,
            "primitive_type": edge_blueprint.primitive_type,
            "role": edge_blueprint.role,
            "path_hint": edge_blueprint.path_hint,
            "directionality_semantics": _edge_directionality_semantics(edge_blueprint),
            "metadata": _to_plain_data(edge_blueprint.metadata),
        }
        if ambient_length is not None:
            edge_payload["ambient_length"] = ambient_length
        edge_id = topology.add_edge(source_node_id, target_node_id, edge_payload)
        edge_ids_by_primitive_id.setdefault(edge_blueprint.primitive_id, []).append(edge_id)
        edge_id_by_primitive_id.setdefault(edge_blueprint.primitive_id, edge_id)
        base_conductance[edge_id] = _edge_weight_from_blueprint(
            edge_blueprint,
            node_mass_by_primitive_id=primitive_raw_node_masses,
        )
        if ambient_length is not None:
            geometric_length[edge_id] = max(1e-12, ambient_length)

    landscape_base_edge_conductance = dict(base_conductance)
    edge_weight_multipliers = _transport_intent_edge_multipliers_for_realized_edges(
        request.seed,
        edge_ids_by_primitive_id={
            primitive_id: tuple(edge_ids)
            for primitive_id, edge_ids in edge_ids_by_primitive_id.items()
        },
    )
    for edge_id in sorted(base_conductance):
        multiplier = float(edge_weight_multipliers.get(edge_id, 1.0))
        edge_payload = topology.edge_payload(edge_id)
        edge_payload["landscape_base_conductance"] = float(
            landscape_base_edge_conductance[edge_id]
        )
        edge_payload["transport_intent_multiplier"] = multiplier
        base_conductance[edge_id] = float(base_conductance[edge_id] * multiplier)
        edge_payload["transport_biased_initial_conductance"] = float(base_conductance[edge_id])

    frame_mode = str(request.params.constitutive_semantic_modes["frame_mode"])
    temporal_label_params = dict(request.params.evolution["temporal_label_params"])
    runtime_assembly_mode = (
        "native_runtime_blueprint"
        if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None
        else "compatibility_blueprint"
    )
    node_attributes = {
        realized_node_id_by_key[spec.realized_key]: BasinAttributes(
            coherence=float(spec.raw_mass * mass_scale),
            gradient=[],
            hessian=[],
            net_flux=[],
            basin_mass=float(spec.raw_mass * mass_scale),
            basin_id=spec.basin_id,
            parent_id=spec.parent_id,
            depth=spec.depth,
        )
        for spec in node_specs
    }
    node_attributes.update(ridge_support_attributes_by_node_id)

    state = GRCV3State(
        topology=topology,
        nodes=node_attributes,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay={},
        flux_coupling={},
        flux={},
        potential={node_id: 0.0 for node_id in topology.iter_live_node_ids()},
        sink_set=set(),
        basins={},
        hierarchy={},
        choice_registry={},
        collapse_registry={},
        edge_label_computation_mode=_edge_label_modes(frame_mode),
        edge_label_params={
            "temporal_delay": {
                "v0": float(temporal_label_params["v0"]),
                "rho": float(temporal_label_params["rho"]),
                "eps_tau": float(temporal_label_params["eps_tau"]),
            },
            "geometric_length_bootstrap": (
                "ambient_chart_hint" if geometric_length else "not_available"
            ),
        },
        step_index=0,
        time=0.0,
        budget_target=float(budget_target),
        remainder=0.0,
        cached_quantities={
            "landscape_seed_name": request.seed.meta.name,
            "landscape_seed_source_reference": request.seed.meta.source_reference,
            "landscape_seed_path": None if request.seed_path is None else str(request.seed_path),
            "landscape_seed_validation_mode": _strict_seed_validation_mode(),
            "landscape_profile_name": request.profile_name,
            "landscape_lowering_lane": lowering_lane,
            "landscape_lowering_semantic_authority": lowering_semantic_authority(lowering_lane),
            "landscape_compatibility_blueprint_usage": lowering_blueprint_usage(lowering_lane),
            "landscape_transport_intent": _transport_intent_metadata(request.seed.transport_intent),
            "landscape_node_id_by_primitive_id": dict(sorted(node_id_by_primitive_id.items())),
            "landscape_node_ids_by_primitive_id": {
                primitive_id: list(node_ids)
                for primitive_id, node_ids in sorted(node_ids_by_primitive_id.items())
            },
            "landscape_support_node_ids_by_primitive_id": {
                primitive_id: list(node_ids)
                for primitive_id, node_ids in sorted(support_node_ids_by_primitive_id.items())
            },
            "landscape_interface_node_ids_by_primitive_id": {
                primitive_id: list(node_ids)
                for primitive_id, node_ids in sorted(interface_node_ids_by_primitive_id.items())
            },
            "landscape_grcv3_role_node_ids_by_primitive_id": {
                primitive_id: {
                    role_label: int(node_id)
                    for role_label, node_id in sorted(role_map.items())
                }
                for primitive_id, role_map in sorted(role_node_ids_by_primitive_id.items())
            },
            "landscape_grcv3_probe_role_node_ids_by_primitive_id": {
                primitive_id: {
                    role_label: int(node_id)
                    for role_label, node_id in sorted(role_map.items())
                }
                for primitive_id, role_map in sorted(probe_role_node_ids_by_primitive_id.items())
            },
            "landscape_grcv3_load_role_node_ids_by_primitive_id": {
                primitive_id: {
                    role_label: int(node_id)
                    for role_label, node_id in sorted(role_map.items())
                }
                for primitive_id, role_map in sorted(load_role_node_ids_by_primitive_id.items())
            },
            "landscape_grcv3_carrier_role_node_ids_by_primitive_id": {
                primitive_id: {
                    role_label: int(node_id)
                    for role_label, node_id in sorted(role_map.items())
                }
                for primitive_id, role_map in sorted(carrier_role_node_ids_by_primitive_id.items())
            },
            "landscape_grcv3_transfer_path_node_ids_by_pair_by_primitive_id": {
                primitive_id: {
                    f"{carrier_role}->{probe_role}": int(node_id)
                    for (carrier_role, probe_role), node_id in sorted(path_map.items())
                }
                for primitive_id, path_map in sorted(transfer_path_node_ids_by_pair_by_primitive_id.items())
            },
            "landscape_grcv3_transfer_fan_in_node_ids_by_probe_by_primitive_id": {
                primitive_id: {
                    probe_role: int(node_id)
                    for probe_role, node_id in sorted(probe_map.items())
                }
                for primitive_id, probe_map in sorted(
                    transfer_fan_in_node_ids_by_probe_by_primitive_id.items()
                )
            },
            "landscape_ridge_support_node_ids_by_primitive_id": {
                primitive_id: list(node_ids)
                for primitive_id, node_ids in sorted(realized_ridge_support_node_ids.items())
            },
            "landscape_edge_id_by_primitive_id": dict(sorted(edge_id_by_primitive_id.items())),
            "landscape_edge_ids_by_primitive_id": {
                primitive_id: list(edge_ids)
                for primitive_id, edge_ids in sorted(edge_ids_by_primitive_id.items())
            },
            "landscape_base_edge_conductance": {
                edge_id: float(value)
                for edge_id, value in sorted(landscape_base_edge_conductance.items())
            },
            "landscape_transport_intent_multiplier": {
                edge_id: float(edge_weight_multipliers.get(edge_id, 1.0))
                for edge_id in sorted(base_conductance)
            },
            "landscape_ridge_ids_by_owner": {
                owner_id: list(ridge_ids)
                for owner_id, ridge_ids in blueprint.ridge_ids_by_owner.items()
            },
            "landscape_metadata_only_ridge_ids": list(blueprint.metadata_only_ridge_ids),
            "landscape_runtime_assembly_mode": runtime_assembly_mode,
            "landscape_runtime_assembly_summary": {
                "mode": runtime_assembly_mode,
                "semantic_authority": lowering_semantic_authority(lowering_lane),
                "carrier_source": (
                    "native_surface_runtime_carrier"
                    if runtime_assembly_mode == "native_runtime_blueprint"
                    else "grcv2_landscape_projector"
                ),
                "node_primitive_ids": list(blueprint.node_primitive_ids),
                "edge_primitive_ids": list(blueprint.edge_primitive_ids),
                "realized_node_count": len(node_specs),
                "realized_edge_count": len(base_conductance),
                "interior_geometry_primitive_ids": (
                    []
                    if native_surface is None
                    else sorted(
                        primitive_id
                        for primitive_id, plan in native_surface.basin_like_plans.items()
                        if plan.interior_geometry is not None
                    )
                ),
                "interior_partition_primitive_ids": (
                    []
                    if native_surface is None
                    else sorted(
                        primitive_id
                        for primitive_id, plan in native_surface.basin_like_plans.items()
                        if plan.interior_partition is not None
                    )
                ),
                "interior_load_carrier_primitive_ids": (
                    []
                    if native_surface is None
                    else sorted(
                        primitive_id
                        for primitive_id, plan in native_surface.basin_like_plans.items()
                        if plan.interior_load_carriers is not None
                    )
                ),
                "transfer_mediation_primitive_ids": (
                    []
                    if native_surface is None
                    else sorted(
                        primitive_id
                        for primitive_id, plan in native_surface.basin_like_plans.items()
                        if plan.transfer_mediation is not None
                    )
                ),
            },
            "landscape_blueprint_summary": {
                "node_primitive_ids": list(blueprint.node_primitive_ids),
                "edge_primitive_ids": list(blueprint.edge_primitive_ids),
                "realized_node_count": len(node_specs),
                "realized_edge_count": len(base_conductance),
            },
            "landscape_transport_bias_mode": "carrier_edge_weight_multiplier",
            "landscape_mass_scale": float(mass_scale),
            "landscape_realized_raw_mass_total": float(total_raw_mass),
            "landscape_primitive_member_mass_by_id": {
                primitive_id: float(value)
                for primitive_id, value in sorted(primitive_member_mass_by_id.items())
            },
            "landscape_realization_mode": (
                (
                    "basin_patch_valley_channel_junction_ridge_grcv3_rich_v4"
                    if rich_seed_extension is not None
                    and rich_seed_extension.contract_version == GRCV3_RICH_V4_CONTRACT_VERSION
                    and rich_seed_extension.primitive_extensions
                    else
                    "basin_patch_valley_channel_junction_ridge_grcv3_rich_v3"
                    if rich_seed_extension is not None
                    and rich_seed_extension.contract_version == GRCV3_RICH_V3_CONTRACT_VERSION
                    and rich_seed_extension.primitive_extensions
                    else "basin_patch_valley_channel_junction_ridge_grcv3_rich_v2"
                    if rich_seed_extension is not None
                    and rich_seed_extension.contract_version == GRCV3_RICH_V2_CONTRACT_VERSION
                    and rich_seed_extension.primitive_extensions
                    else (
                        "basin_patch_valley_channel_junction_ridge_grcv3_rich_v1"
                        if rich_seed_extension is not None
                        and rich_seed_extension.primitive_extensions
                        else "basin_patch_valley_channel_junction_ridge_v2"
                    )
                )
            ),
            "landscape_skipped_patch_ids": list(skipped_patch_ids),
            "landscape_grcv3_rich_contract_version": (
                None if rich_seed_extension is None else rich_seed_extension.contract_version
            ),
            "landscape_grcv3_rich_required": (
                False if rich_seed_extension is None else rich_seed_extension.rich_required
            ),
            "landscape_grcv3_rich_primitive_ids": (
                []
                if rich_seed_extension is None
                else sorted(rich_seed_extension.primitive_extensions)
            ),
            "landscape_grcv3_branch_node_ids_by_target": {
                primitive_id: {
                    target_primitive_id: int(node_id)
                    for target_primitive_id, node_id in sorted(target_map.items())
                }
                for primitive_id, target_map in sorted(rich_branch_node_ids_by_target.items())
            },
            "landscape_grcv3_interior_geometry_summary": (
                {}
                if native_surface is None
                else {
                    primitive_id: {
                        "probe_mode": plan.interior_geometry.probe_mode,
                        "attachment_isolation": plan.interior_geometry.attachment_isolation,
                        "interior_clearance_class": plan.interior_geometry.interior_clearance_class,
                        "support_connectivity": plan.interior_geometry.support_connectivity,
                        "support_profile": dict(plan.interior_geometry.support_profile),
                        "support_role_groups": {
                            group_name: list(group_roles)
                            for group_name, group_roles in plan.interior_geometry.support_role_groups.items()
                        },
                    }
                    for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                    if plan.interior_geometry is not None
                }
            ),
            "landscape_grcv3_interior_partition_summary": (
                {}
                if native_surface is None
                else {
                    primitive_id: {
                        "partition_mode": plan.interior_partition.partition_mode,
                        "load_role_groups": {
                            group_name: list(group_roles)
                            for group_name, group_roles in plan.interior_partition.load_role_groups.items()
                        },
                        "load_transfer_mode": plan.interior_partition.load_transfer_mode,
                        "probe_protection_class": plan.interior_partition.probe_protection_class,
                        "attachment_transfer_roles": list(
                            plan.interior_partition.attachment_transfer_roles
                        ),
                    }
                    for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                    if plan.interior_partition is not None
                }
            ),
            "landscape_grcv3_interior_load_carrier_summary": (
                {}
                if native_surface is None
                else {
                    primitive_id: {
                        "carrier_layout_mode": plan.interior_load_carriers.carrier_layout_mode,
                        "carrier_anchor_policy": plan.interior_load_carriers.carrier_anchor_policy,
                        "transfer_topology_mode": (
                            plan.interior_load_carriers.transfer_topology_mode
                        ),
                        "transfer_role_pairs": [
                            [carrier_role, probe_role]
                            for carrier_role, probe_role in plan.interior_load_carriers.transfer_role_pairs
                        ],
                        "carrier_attachment_roles": list(
                            plan.interior_load_carriers.carrier_attachment_roles
                        ),
                    }
                    for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                    if plan.interior_load_carriers is not None
                }
            ),
            "landscape_grcv3_transfer_mediation_summary": (
                {}
                if native_surface is None
                else {
                    primitive_id: {
                        "mediation_mode": plan.transfer_mediation.mediation_mode,
                        "pair_mediation_classes": [
                            [carrier_role, probe_role, mediation_class]
                            for carrier_role, probe_role, mediation_class in plan.transfer_mediation.pair_mediation_classes
                        ],
                        "probe_guard_class": plan.transfer_mediation.probe_guard_class,
                        "lateral_spill_policy": plan.transfer_mediation.lateral_spill_policy,
                        "spill_branch_mode": plan.transfer_mediation.spill_branch_mode,
                        "center_coupling_classes": [
                            [probe_role, coupling_class]
                            for probe_role, coupling_class in plan.transfer_mediation.center_coupling_classes
                        ],
                        "path_topology": [
                            [carrier_role, probe_role, topology_class]
                            for carrier_role, probe_role, topology_class in plan.transfer_mediation.path_topology
                        ],
                    }
                    for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                    if plan.transfer_mediation is not None
                }
            ),
            "landscape_grcv3_settlement_regime_summary": (
                {}
                if native_surface is None
                else {
                    primitive_id: {
                        "regime_class": plan.settlement_regime.regime_class,
                        "initial_locus_class": plan.settlement_regime.initial_locus_class,
                        "split_inheritance_mode": plan.settlement_regime.split_inheritance_mode,
                    }
                    for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                    if plan.settlement_regime is not None
                }
            ),
            "landscape_grcv3_lowering_notes": [
                "attachment roles are resolved deterministically from preferred_attachment_sites first, then family-local role labels, then geometric fallback",
                "boundary support arcs are constructive approximations of source boundary intent, not solved metric imports",
                *(
                    [
                        "family-native basin and plateau lowering realize declared local axes as direct role nodes; constructive support-ring sampling remains a discretization choice",
                        "family-native valley lowering consumes channel_geometry and preferred attachment sites directly from source-rich seed fields",
                        "family-native ridge lowering consumes boundary_geometry and preferred attachment sites directly from source-rich seed fields",
                        "grcv3.rich.v3 interior_geometry changes realized support spacing, spoke coupling, support-support connectivity, and center-attachment fallback policy directly in the family-native assembly path",
                        "grcv3.rich.v3 interior_partition adds an outer load shell while preserving the inner probe shell as the weak-axis support stencil used for basin-patch coupling",
                        "grcv3.rich.v3 interior_load_carriers refines the attachment-facing outer layer into non-coincident carrier nodes and routes carrier-to-probe transfer through explicit role-pair topology",
                        "grcv3.rich.v4 transfer_mediation changes only the assembled ingress structure over already-declared carrier/probe pairs; runtime transport still emerges through the normal conductance, potential, and flux loop",
                    ]
                    if lowering_lane == LOWERING_LANE_FAMILY_NATIVE and native_surface is not None
                    else []
                ),
            ],
            "landscape_grcv3_native_surface_summary": (
                None
                if native_surface is None
                else {
                    "rich_contract_version": native_surface.rich_contract_version,
                    "node_carrier_ids": list(native_surface.node_carrier_ids),
                    "edge_carrier_ids": list(native_surface.edge_carrier_ids),
                    "primitive_ids_by_type": {
                        primitive_type: list(primitive_ids)
                        for primitive_type, primitive_ids in native_surface.primitive_ids_by_type.items()
                    },
                    "metadata_only_ridge_ids": list(native_surface.metadata_only_ridge_ids),
                    "junction_like_ids": list(native_surface.junction_like_ids),
                    "rich_primitive_ids": list(native_surface.rich_primitive_ids),
                    "interior_geometry_primitive_ids": [
                        primitive_id
                        for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                        if plan.interior_geometry is not None
                    ],
                    "interior_partition_primitive_ids": [
                        primitive_id
                        for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                        if plan.interior_partition is not None
                    ],
                    "interior_load_carrier_primitive_ids": [
                        primitive_id
                        for primitive_id, plan in sorted(native_surface.basin_like_plans.items())
                        if plan.interior_load_carriers is not None
                    ],
                    "temporary_blueprint_utility_functions": list(
                        native_surface.temporary_blueprint_utility_functions
                    ),
                    "prohibited_blueprint_semantic_authorities": list(
                        native_surface.prohibited_blueprint_semantic_authorities
                    ),
                }
            ),
            "landscape_motif_contract": {
                "basin_support_count": len(_BASIN_SUPPORT_ANGLES),
                "basin_center_mass_fraction": _BASIN_CENTER_MASS_FRACTION,
                "junction_center_mass_fraction": _JUNCTION_CENTER_MASS_FRACTION,
                "ridge_support_node_count": _RIDGE_SUPPORT_NODE_COUNT,
                "channel_nodes_without_waypoints": _CHANNEL_NODES_WITHOUT_WAYPOINTS,
                "channel_nodes_with_waypoints": _CHANNEL_NODES_WITH_WAYPOINTS,
                "default_projector_radius": _DEFAULT_PROJECTOR_RADIUS,
            },
            "landscape_budget_mode": (
                "explicit_budget_b"
                if request.seed.constitutive_profile.budget_b is not None
                else "sum_of_realized_node_priors"
            ),
        },
        event_log=[],
        observables={},
        rng_state=None,
        params_identity=request.params.params_hash,
    )
    return state


def project_landscape_seed_to_grcv3_state(
    seed: LandscapeSeedInput,
    *,
    params: GRCV3ParamsInput,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    validate_seed: bool = True,
) -> GRCV3State:
    """Project one validated landscape seed into an initial GRCV3 state."""

    context = _resolve_grcv3_lowering_context(
        seed,
        params=params,
        profile_name=profile_name,
        validate_seed=validate_seed,
    )
    return _build_grcv3_state_from_projection(
        context.request,
        context.blueprint,
        rich_seed_extension=context.rich_seed_extension,
        lowering_lane=context.lowering_lane,
        native_surface=context.native_surface,
    )


def build_grcv3_from_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    params: GRCV3ParamsInput,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    validate_seed: bool = True,
) -> GRCV3:
    """Construct one executable GRCV3 model from a landscape seed."""

    context = _resolve_grcv3_lowering_context(
        seed,
        params=params,
        profile_name=profile_name,
        validate_seed=validate_seed,
    )
    state = _build_grcv3_state_from_projection(
        context.request,
        context.blueprint,
        rich_seed_extension=context.rich_seed_extension,
        lowering_lane=context.lowering_lane,
        native_surface=context.native_surface,
    )
    return GRCV3(params=context.request.params, state=state)


def run_grcv3_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    num_steps: int,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    overrides: Mapping[str, Any] | None = None,
    validate_seed: bool = True,
) -> GRCV3LandscapeRunResult:
    """Run one landscape seed through GRCV3 for a fixed number of steps."""

    resolved_seed, seed_path = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    resolved_params = resolve_grcv3_landscape_params(
        resolved_seed,
        profile_name=profile_name,
        overrides=overrides,
        validate_seed=False,
    )
    context = _resolve_grcv3_lowering_context(
        resolved_seed,
        params=resolved_params,
        profile_name=profile_name,
        validate_seed=False,
    )
    request = GRCV3LandscapeProjectionRequest(
        seed=context.request.seed,
        params=context.request.params,
        seed_path=seed_path,
        profile_name=context.request.profile_name,
    )
    state = _build_grcv3_state_from_projection(
        request,
        context.blueprint,
        rich_seed_extension=context.rich_seed_extension,
        lowering_lane=context.lowering_lane,
        native_surface=context.native_surface,
    )
    model = GRCV3(params=request.params, state=state)
    initial_observables = dict(model.compute_observables())
    step_results: list[StepResult] = []
    for _ in range(num_steps):
        step_results.append(model.step())
    final_observables = dict(model.compute_observables())
    return GRCV3LandscapeRunResult(
        request=request,
        blueprint=context.blueprint,
        model=model,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
    )


__all__ = [
    "DEFAULT_GRCV3_LANDSCAPE_PROFILE",
    "GRCV3LandscapeProjectionRequest",
    "GRCV3LandscapeRunResult",
    "build_grcv3_from_landscape_seed",
    "prepare_grcv3_landscape_projection",
    "project_landscape_seed_to_grcv3_state",
    "resolve_grcv3_landscape_params",
    "run_grcv3_landscape_seed",
]

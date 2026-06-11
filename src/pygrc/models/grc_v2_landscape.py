"""Family-local landscape projector boundary for seed-driven GRCV2 work."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import math
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, TypeAlias

from pygrc.core import GRCParams, InvalidLandscapeSeedError, StepResult, WeightedGraphBackend
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    RidgeSeedPrimitive,
    SeedTransportIntent,
    ValleySeedPrimitive,
    load_landscape_seed,
    validate_landscape_seed,
)

from .grc_v2 import GRCV2
from .grc_v2_checkpoints import export_grcv2_graph_checkpoint
from .grc_v2_state import GRCV2State

if TYPE_CHECKING:
    from pygrc.telemetry.recorder import TelemetryCaptureResult


LandscapeSeedInput: TypeAlias = LandscapeSeed | str | Path
GRCV2ParamsInput: TypeAlias = GRCParams | Mapping[str, Any]


@dataclass(frozen=True)
class GRCV2LandscapeProjectionRequest:
    """Validated family-local projector input for seed-driven GRCV2 work."""

    seed: LandscapeSeed
    params: GRCParams
    seed_path: Path | None = None


@dataclass(frozen=True)
class GRCV2LandscapeNodeBlueprint:
    """One node-carrying primitive realized for the baseline GRCV2 projector."""

    primitive_id: str
    primitive_type: str
    role: str | None
    parent_id: str | None
    coherence_prior: float | None
    chart_center_hint: tuple[float, float] | None
    chart_scale_hint: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class GRCV2LandscapeEdgeBlueprint:
    """One edge-carrying primitive realized for the baseline GRCV2 projector."""

    primitive_id: str
    primitive_type: str
    source_primitive_id: str
    target_primitive_id: str
    coherence_prior: float | None
    width_hint: float | None
    path_hint: str | None
    role: str | None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class GRCV2LandscapeBlueprint:
    """Deterministic primitive-to-topology realization for the baseline projector."""

    node_blueprints: tuple[GRCV2LandscapeNodeBlueprint, ...]
    edge_blueprints: tuple[GRCV2LandscapeEdgeBlueprint, ...]
    ridge_ids_by_owner: Mapping[str, tuple[str, ...]]
    metadata_only_ridge_ids: tuple[str, ...]
    node_primitive_ids: tuple[str, ...]
    edge_primitive_ids: tuple[str, ...]


@dataclass(frozen=True)
class GRCV2LandscapeParamFamily:
    """Named PDE-informed preset family for seed-driven GRCV2 runs."""

    name: str
    description: str
    anchor_roles: tuple[str, ...]
    latent_axes: Mapping[str, float]


@dataclass
class GRCV2LandscapeRunResult:
    """Executable trajectory result for one seed-driven GRCV2 run."""

    request: GRCV2LandscapeProjectionRequest
    blueprint: GRCV2LandscapeBlueprint
    model: GRCV2
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    telemetry: TelemetryCaptureResult | None = None


_PARAM_FAMILY_LIBRARY: dict[str, GRCV2LandscapeParamFamily] = {
    "quiet_conservative": GRCV2LandscapeParamFamily(
        name="quiet_conservative",
        description="Low-activity conservative baseline for stability-first runs.",
        anchor_roles=(),
        latent_axes=MappingProxyType(
            {
                "activity": 0.20,
                "identity_budget": 0.25,
                "birth_permissiveness": 0.20,
                "spark_sensitivity": 0.25,
                "collapse_damping": 0.85,
                "closure_softness": 0.25,
            }
        ),
    ),
    "balanced_baseline": GRCV2LandscapeParamFamily(
        name="balanced_baseline",
        description="Mid-activity reference family for first cross-seed comparisons.",
        anchor_roles=("cell1",),
        latent_axes=MappingProxyType(
            {
                "activity": 0.50,
                "identity_budget": 0.50,
                "birth_permissiveness": 0.50,
                "spark_sensitivity": 0.50,
                "collapse_damping": 0.50,
                "closure_softness": 0.50,
            }
        ),
    ),
    "hot_exploratory": GRCV2LandscapeParamFamily(
        name="hot_exploratory",
        description="High-activity exploratory family for event-rich runs.",
        anchor_roles=(),
        latent_axes=MappingProxyType(
            {
                "activity": 0.82,
                "identity_budget": 0.80,
                "birth_permissiveness": 0.78,
                "spark_sensitivity": 0.75,
                "collapse_damping": 0.25,
                "closure_softness": 0.75,
            }
        ),
    ),
    "precursor_sensitive": GRCV2LandscapeParamFamily(
        name="precursor_sensitive",
        description="Higher spark-sensitivity family for near-threshold precursor behavior.",
        anchor_roles=("z2c@anchorb",),
        latent_axes=MappingProxyType(
            {
                "activity": 0.58,
                "identity_budget": 0.52,
                "birth_permissiveness": 0.42,
                "spark_sensitivity": 0.82,
                "collapse_damping": 0.40,
                "closure_softness": 0.72,
            }
        ),
    ),
    "commitment_dominant": GRCV2LandscapeParamFamily(
        name="commitment_dominant",
        description="Higher collapse-damping family for committed continuation pressure.",
        anchor_roles=("z2c@anchorb", "s6@anchora"),
        latent_axes=MappingProxyType(
            {
                "activity": 0.42,
                "identity_budget": 0.42,
                "birth_permissiveness": 0.34,
                "spark_sensitivity": 0.40,
                "collapse_damping": 0.92,
                "closure_softness": 0.36,
            }
        ),
    ),
    "holdout_counterexample_locked": GRCV2LandscapeParamFamily(
        name="holdout_counterexample_locked",
        description="Conservative family for retained negative and holdout cases.",
        anchor_roles=("s6@anchora",),
        latent_axes=MappingProxyType(
            {
                "activity": 0.18,
                "identity_budget": 0.20,
                "birth_permissiveness": 0.16,
                "spark_sensitivity": 0.18,
                "collapse_damping": 0.97,
                "closure_softness": 0.20,
            }
        ),
    ),
}


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    frozen_items: dict[str, Any] = {}
    for key in sorted(value):
        inner_value = value[key]
        if isinstance(inner_value, Mapping):
            frozen_items[key] = _freeze_mapping(inner_value)
        elif isinstance(inner_value, list):
            frozen_items[key] = tuple(inner_value)
        else:
            frozen_items[key] = inner_value
    return MappingProxyType(frozen_items)


def _freeze_optional_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if value is None:
        return MappingProxyType({})
    return _freeze_mapping(value)


def _strict_seed_validation_mode() -> str:
    return "strict_always_on"


def _optional_center(point: list[float] | None) -> tuple[float, float] | None:
    if point is None:
        return None
    return (float(point[0]), float(point[1]))


def _to_plain_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _to_plain_data(inner_value) for key, inner_value in value.items()}
    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]
    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]
    return value


def _supports_grcv2_node_carrier(primitive: LandscapePrimitive) -> bool:
    return isinstance(
        primitive,
        BasinSeedPrimitive | PlateauSeedPrimitive | JunctionSeedPrimitive,
    )


def _primitive_index(seed: LandscapeSeed) -> dict[str, LandscapePrimitive]:
    index: dict[str, LandscapePrimitive] = {}
    for primitive in seed.primitives:
        if primitive.id in index:
            raise InvalidLandscapeSeedError(
                f"seed contains duplicate primitive id {primitive.id!r}; "
                "GRCV2 landscape realization requires unique primitive ids even "
                "when validate_seed=False"
            )
        index[primitive.id] = primitive
    return index


def _require_node_carrier(
    primitive_id: str,
    *,
    index: Mapping[str, LandscapePrimitive],
    context: str,
) -> LandscapePrimitive:
    primitive = index[primitive_id]
    if not _supports_grcv2_node_carrier(primitive):
        raise InvalidLandscapeSeedError(
            f"{context} must reference a node-carrying primitive for GRCV2; "
            f"got {primitive.type!r} at {primitive_id!r}"
        )
    return primitive


def _realize_node_blueprint(
    primitive: LandscapePrimitive,
) -> GRCV2LandscapeNodeBlueprint:
    if isinstance(primitive, BasinSeedPrimitive):
        metadata = _freeze_mapping(
            {
                "boundary_ids": tuple(primitive.boundary_ids),
                "shape_hint": dict(primitive.shape_hint),
                "stability_class": primitive.stability_class,
                "notes": primitive.notes,
            }
        )
        return GRCV2LandscapeNodeBlueprint(
            primitive_id=primitive.id,
            primitive_type=primitive.type,
            role=primitive.role,
            parent_id=primitive.parent_id,
            coherence_prior=primitive.coherence_prior,
            chart_center_hint=_optional_center(primitive.chart_center_hint),
            chart_scale_hint=_freeze_optional_mapping(primitive.chart_scale_hint),
            metadata=metadata,
        )
    if isinstance(primitive, PlateauSeedPrimitive):
        metadata = _freeze_mapping(
            {
                "hosted_primitive_ids": tuple(primitive.hosted_primitive_ids),
                "stability_class": primitive.stability_class,
                "notes": primitive.notes,
            }
        )
        return GRCV2LandscapeNodeBlueprint(
            primitive_id=primitive.id,
            primitive_type=primitive.type,
            role=primitive.role,
            parent_id=primitive.parent_id,
            coherence_prior=primitive.coherence_prior,
            chart_center_hint=_optional_center(primitive.chart_center_hint),
            chart_scale_hint=_freeze_optional_mapping(primitive.chart_scale_hint),
            metadata=metadata,
        )
    if isinstance(primitive, JunctionSeedPrimitive):
        metadata = _freeze_mapping(
            {
                "host_id": primitive.host_id,
                "is_hostless": primitive.host_id is None,
                "junction_anchor_mode": "standalone" if primitive.host_id is None else "hosted",
                "branch_target_ids": tuple(primitive.branch_target_ids),
                "junction_role": primitive.junction_role,
                "notes": primitive.notes,
            }
        )
        return GRCV2LandscapeNodeBlueprint(
            primitive_id=primitive.id,
            primitive_type=primitive.type,
            role=primitive.role,
            parent_id=primitive.host_id,
            coherence_prior=primitive.coherence_prior,
            chart_center_hint=_optional_center(primitive.chart_center_hint),
            chart_scale_hint=MappingProxyType({}),
            metadata=metadata,
        )
    raise InvalidLandscapeSeedError(
        f"primitive {primitive.id!r} of type {primitive.type!r} is not a GRCV2 node carrier"
    )


def _validate_basin_like_projection_policy(seed: LandscapeSeed) -> None:
    index = _primitive_index(seed)
    for primitive in seed.primitives:
        if isinstance(primitive, BasinSeedPrimitive):
            for boundary_id in primitive.boundary_ids:
                boundary = index[boundary_id]
                if not isinstance(boundary, RidgeSeedPrimitive):
                    raise InvalidLandscapeSeedError(
                        f"basin {primitive.id!r} boundary_ids must reference ridge primitives; "
                        f"got {boundary.type!r} at {boundary_id!r}"
                    )
        if isinstance(primitive, PlateauSeedPrimitive):
            for hosted_id in primitive.hosted_primitive_ids:
                hosted = index[hosted_id]
                if not _supports_grcv2_node_carrier(hosted):
                    raise InvalidLandscapeSeedError(
                        f"plateau {primitive.id!r} hosted_primitive_ids must reference "
                        f"node-carrying primitives for GRCV2; got {hosted.type!r} at {hosted_id!r}"
                    )
        if isinstance(primitive, JunctionSeedPrimitive):
            if primitive.host_id is not None:
                _require_node_carrier(
                    primitive.host_id,
                    index=index,
                    context=f"junction {primitive.id!r} host_id",
                )
            for target_id in primitive.branch_target_ids:
                _require_node_carrier(
                    target_id,
                    index=index,
                    context=f"junction {primitive.id!r} branch_target_ids",
                )
            if (
                primitive.host_id is None
                and primitive.chart_center_hint is None
                and not _has_incident_valley(seed, primitive.id)
            ):
                raise InvalidLandscapeSeedError(
                    f"junction {primitive.id!r} is hostless and not realizable as a "
                    "standalone GRCV2 routing node; provide chart_center_hint or at least "
                    "one incident valley"
                )


def _has_incident_valley(seed: LandscapeSeed, primitive_id: str) -> bool:
    for primitive in seed.primitives:
        if isinstance(primitive, ValleySeedPrimitive) and (
            primitive.from_id == primitive_id or primitive.to_id == primitive_id
        ):
            return True
    return False


def _is_metadata_only_boundary_ridge(
    primitive: RidgeSeedPrimitive,
    *,
    owner: LandscapePrimitive,
) -> bool:
    if primitive.adjacent_ids:
        return False
    if primitive.ridge_kind != "boundary":
        return False
    if not isinstance(owner, BasinSeedPrimitive | PlateauSeedPrimitive):
        return False
    return owner.parent_id is None


def _maybe_support_target_for_ridge(
    primitive: RidgeSeedPrimitive,
    *,
    index: Mapping[str, LandscapePrimitive],
) -> tuple[str, ...]:
    explicit_targets = tuple(primitive.adjacent_ids)
    if explicit_targets:
        for target_id in explicit_targets:
            _require_node_carrier(
                target_id,
                index=index,
                context=f"ridge {primitive.id!r} adjacent_ids",
            )
        return explicit_targets
    owner = _require_node_carrier(
        primitive.owner_id,
        index=index,
        context=f"ridge {primitive.id!r} owner_id",
    )
    if isinstance(owner, BasinSeedPrimitive | PlateauSeedPrimitive):
        if owner.parent_id is not None and _supports_grcv2_node_carrier(index[owner.parent_id]):
            return (owner.parent_id,)
        return ()
    if isinstance(owner, JunctionSeedPrimitive):
        if owner.host_id is not None and _supports_grcv2_node_carrier(index[owner.host_id]):
            return (owner.host_id,)
        return ()
    return ()


def _assert_unique_blueprint_primitive_ids(
    *,
    node_blueprints: list[GRCV2LandscapeNodeBlueprint],
    edge_blueprints: list[GRCV2LandscapeEdgeBlueprint],
) -> None:
    seen_node_ids: set[str] = set()
    for blueprint in node_blueprints:
        if blueprint.primitive_id in seen_node_ids:
            raise InvalidLandscapeSeedError(
                f"GRCV2 landscape realization produced duplicate node blueprint id "
                f"{blueprint.primitive_id!r}"
            )
        seen_node_ids.add(blueprint.primitive_id)

    seen_edge_ids: set[str] = set()
    for blueprint in edge_blueprints:
        if blueprint.primitive_id in seen_edge_ids:
            raise InvalidLandscapeSeedError(
                f"GRCV2 landscape realization produced duplicate edge blueprint id "
                f"{blueprint.primitive_id!r}; one primitive must not realize to "
                "multiple indistinguishable edge identities in the baseline projector"
            )
        seen_edge_ids.add(blueprint.primitive_id)


def _ridge_edge_role(primitive: RidgeSeedPrimitive) -> str:
    ridge_kind = primitive.ridge_kind or "ridge"
    return f"{ridge_kind}_support"


def realize_grcv2_landscape_blueprint(
    seed: LandscapeSeedInput,
    *,
    validate_seed: bool = True,
) -> GRCV2LandscapeBlueprint:
    """Realize one validated seed into the baseline GRCV2 topology blueprint."""

    resolved_seed, _ = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    primitive_index = _primitive_index(resolved_seed)
    _validate_basin_like_projection_policy(resolved_seed)

    node_blueprints: list[GRCV2LandscapeNodeBlueprint] = []
    edge_blueprints: list[GRCV2LandscapeEdgeBlueprint] = []
    ridge_ids_by_owner: dict[str, list[str]] = {}
    metadata_only_ridge_ids: list[str] = []

    for primitive in resolved_seed.primitives:
        if _supports_grcv2_node_carrier(primitive):
            node_blueprints.append(_realize_node_blueprint(primitive))
            continue

        if isinstance(primitive, RidgeSeedPrimitive):
            if primitive.owner_id is None:
                raise InvalidLandscapeSeedError(
                    f"ridge {primitive.id!r} requires owner_id for GRCV2 realization"
                )
            owner = _require_node_carrier(
                primitive.owner_id,
                index=primitive_index,
                context=f"ridge {primitive.id!r} owner_id",
            )
            ridge_ids_by_owner.setdefault(primitive.owner_id, []).append(primitive.id)
            support_targets = _maybe_support_target_for_ridge(
                primitive,
                index=primitive_index,
            )
            owner_role = owner.role
            if not support_targets:
                if _is_metadata_only_boundary_ridge(primitive, owner=owner):
                    metadata_only_ridge_ids.append(primitive.id)
                    continue
                raise InvalidLandscapeSeedError(
                    f"ridge {primitive.id!r} could not resolve to a GRCV2 support edge; "
                    "provide adjacent_ids or an owner with a realizable parent/host, "
                    "or use an explicit root boundary ridge if metadata-only treatment "
                    "is intended"
                )
            for target_id in support_targets:
                edge_blueprints.append(
                    GRCV2LandscapeEdgeBlueprint(
                        primitive_id=primitive.id,
                        primitive_type=primitive.type,
                        source_primitive_id=primitive.owner_id,
                        target_primitive_id=target_id,
                        coherence_prior=None,
                        width_hint=primitive.thickness_hint,
                        path_hint="ridge_support",
                        role=_ridge_edge_role(primitive),
                        metadata=_freeze_mapping(
                            {
                                "ridge_kind": primitive.ridge_kind,
                                "owner_role": owner_role,
                                "interior_coherence_hint": primitive.interior_coherence_hint,
                                "exterior_coherence_hint": primitive.exterior_coherence_hint,
                                "anisotropy_hint": dict(primitive.anisotropy_hint),
                                "permeability_hint": dict(primitive.permeability_hint),
                                "notes": primitive.notes,
                            }
                        ),
                    )
                )
            continue

        if isinstance(primitive, ValleySeedPrimitive):
            if primitive.from_id is None or primitive.to_id is None:
                raise InvalidLandscapeSeedError(
                    f"valley {primitive.id!r} requires from_id and to_id for GRCV2 realization"
                )
            _require_node_carrier(
                primitive.from_id,
                index=primitive_index,
                context=f"valley {primitive.id!r} from_id",
            )
            _require_node_carrier(
                primitive.to_id,
                index=primitive_index,
                context=f"valley {primitive.id!r} to_id",
            )
            edge_blueprints.append(
                GRCV2LandscapeEdgeBlueprint(
                    primitive_id=primitive.id,
                    primitive_type=primitive.type,
                    source_primitive_id=primitive.from_id,
                    target_primitive_id=primitive.to_id,
                    coherence_prior=primitive.coherence_prior,
                    width_hint=primitive.width_hint,
                    path_hint=primitive.path_hint,
                    role=primitive.channel_role or primitive.role,
                    metadata=_freeze_mapping(
                        {
                            "waypoints": tuple(tuple(point) for point in primitive.waypoints),
                            "notes": primitive.notes,
                        }
                    ),
                )
            )
            continue

        raise InvalidLandscapeSeedError(
            f"unsupported GRCV2 realization primitive type {primitive.type!r}"
        )

    _assert_unique_blueprint_primitive_ids(
        node_blueprints=node_blueprints,
        edge_blueprints=edge_blueprints,
    )
    frozen_ridge_ids_by_owner = MappingProxyType(
        {owner_id: tuple(ridge_ids) for owner_id, ridge_ids in ridge_ids_by_owner.items()}
    )
    return GRCV2LandscapeBlueprint(
        node_blueprints=tuple(node_blueprints),
        edge_blueprints=tuple(edge_blueprints),
        ridge_ids_by_owner=frozen_ridge_ids_by_owner,
        metadata_only_ridge_ids=tuple(metadata_only_ridge_ids),
        node_primitive_ids=tuple(node.primitive_id for node in node_blueprints),
        edge_primitive_ids=tuple(edge.primitive_id for edge in edge_blueprints),
    )


def _coerce_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    validate_seed: bool,
) -> tuple[LandscapeSeed, Path | None]:
    resolved_seed: LandscapeSeed
    seed_path: Path | None = None
    if isinstance(seed, LandscapeSeed):
        resolved_seed = seed
    elif isinstance(seed, str | Path):
        seed_path = Path(seed)
        resolved_seed = load_landscape_seed(seed_path, validate=validate_seed)
    else:
        raise InvalidLandscapeSeedError(
            "seed input must be a LandscapeSeed instance or a seed file path"
        )
    # Public landscape projection/runtime entrypoints remain strict even when
    # validate_seed=False is passed. The flag is kept for API compatibility and
    # to avoid duplicate load-time validation, but unsafe unvalidated seeds are
    # not allowed through the GRCV2 boundary.
    validate_landscape_seed(resolved_seed)
    return resolved_seed, seed_path


def _coerce_grcv2_params(params: GRCV2ParamsInput) -> GRCParams:
    if isinstance(params, GRCParams):
        return params
    if not isinstance(params, Mapping):
        raise TypeError("params input must be a GRCParams instance or a mapping")
    # Reuse the family's own construction/validation path so the projector
    # boundary does not introduce a second params contract.
    return GRCV2.from_config(dict(params)).get_params()


def prepare_grcv2_landscape_projection(
    seed: LandscapeSeedInput,
    *,
    params: GRCV2ParamsInput,
    validate_seed: bool = True,
) -> GRCV2LandscapeProjectionRequest:
    """Normalize seed and params into one validated family-local request."""

    resolved_seed, seed_path = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    resolved_params = _coerce_grcv2_params(params)
    return GRCV2LandscapeProjectionRequest(
        seed=resolved_seed,
        params=resolved_params,
        seed_path=seed_path,
    )


def list_grcv2_landscape_param_families() -> tuple[str, ...]:
    """Return the available PDE-informed preset names in deterministic order."""

    return tuple(sorted(_PARAM_FAMILY_LIBRARY))


def get_grcv2_landscape_param_family(name: str) -> GRCV2LandscapeParamFamily:
    """Return one named PDE-informed family definition."""

    try:
        return _PARAM_FAMILY_LIBRARY[name]
    except KeyError as exc:
        raise InvalidLandscapeSeedError(
            f"unknown GRCV2 landscape param family {name!r}; "
            f"expected one of {sorted(_PARAM_FAMILY_LIBRARY)}"
        ) from exc


def _site_potential_from_seed(seed: LandscapeSeed) -> tuple[str, dict[str, Any], dict[str, Any]]:
    potential = seed.constitutive_profile.potential
    potential_type = potential.type
    params = dict(potential.params)
    if potential_type == "double_well":
        # GRCV2 currently exposes quadratic/linear site-potential selections.
        # Use a deterministic quadratic surrogate and preserve the source
        # potential metadata in the numerical-backend domain.
        scale = float(params.get("a", 1.0))
        mu = -float(params.get("b", 0.0))
        return (
            "quadratic",
            {"scale": scale, "mu": mu},
            {
                "source_potential_type": potential_type,
                "source_potential_params": deepcopy(params),
                "projection_mode": "quadratic_surrogate",
            },
        )
    if potential_type == "quadratic":
        return (
            "quadratic",
            {"scale": float(params.get("scale", 1.0)), "mu": float(params.get("mu", 0.0))},
            {
                "source_potential_type": potential_type,
                "source_potential_params": deepcopy(params),
                "projection_mode": "direct",
            },
        )
    if potential_type == "linear":
        return (
            "linear",
            {
                "scale": float(params.get("scale", 1.0)),
                "bias": float(params.get("bias", 0.0)),
            },
            {
                "source_potential_type": potential_type,
                "source_potential_params": deepcopy(params),
                "projection_mode": "direct",
            },
        )
    raise InvalidLandscapeSeedError(
        f"unsupported seed potential type {potential_type!r} for GRCV2 landscape projection"
    )


def _deep_merge_mapping(
    base: Mapping[str, Any],
    overrides: Mapping[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key, value in overrides.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, Mapping)
        ):
            merged[key] = _deep_merge_mapping(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _resolved_family_config(
    seed: LandscapeSeed,
    family: GRCV2LandscapeParamFamily,
    *,
    rng_seed: int | None,
) -> dict[str, Any]:
    axes = family.latent_axes
    activity = float(axes["activity"])
    identity_budget = float(axes["identity_budget"])
    birth_permissiveness = float(axes["birth_permissiveness"])
    spark_sensitivity = float(axes["spark_sensitivity"])
    collapse_damping = float(axes["collapse_damping"])
    closure_softness = float(axes["closure_softness"])
    site_selection, site_params, site_projection_meta = _site_potential_from_seed(seed)

    evolution: dict[str, Any] = {
        "alpha": 0.8 + 0.8 * closure_softness,
        "beta": 0.8 + 0.8 * closure_softness,
        "gamma": 0.7 + 1.1 * collapse_damping,
        "delta": 0.25 + 0.75 * collapse_damping,
        "eta": 0.8 + 0.8 * activity,
        "kappa_c": float(seed.constitutive_profile.kappa_c),
        "lambda_c": float(seed.constitutive_profile.lambda_c),
        "xi_c": float(seed.constitutive_profile.xi_c),
        "zeta_c": float(seed.constitutive_profile.zeta_c),
        "site_potential_selection": site_selection,
        "site_potential_params": site_params,
        "eps_spark": max(0.005, 0.12 - 0.10 * spark_sensitivity),
        "tau_split": max(1.0, 3.0 - 2.0 * activity),
        "lambda_birth": 0.08 + 0.62 * birth_permissiveness,
        "alpha_seed": 0.15 + 0.70 * identity_budget,
        "eps_prune": 0.0005 + 0.0095 * collapse_damping,
        "spark_backend": "cheeger_proxy",
        "temporal_v0": 1.0,
        "temporal_rho": 1.0,
        "eps_tau": 1e-12,
    }
    if rng_seed is not None:
        evolution["rng_seed"] = int(rng_seed)
    return {
        "dt": float(seed.constitutive_profile.dt),
        "evolution": evolution,
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
        "numerical_backend": {
            "landscape_param_family": family.name,
            "landscape_param_axes": dict(family.latent_axes),
            "seed_potential_projection": site_projection_meta,
        },
    }


def resolve_grcv2_landscape_params(
    seed: LandscapeSeedInput,
    *,
    family_name: str = "balanced_baseline",
    overrides: Mapping[str, Any] | None = None,
    rng_seed: int | None = None,
    validate_seed: bool = True,
) -> GRCParams:
    """Resolve one PDE-informed family plus overrides into GRCV2 params."""

    resolved_seed, _ = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    family = get_grcv2_landscape_param_family(family_name)
    config = _resolved_family_config(resolved_seed, family, rng_seed=rng_seed)
    if overrides is not None:
        config = _deep_merge_mapping(config, overrides)
    return _coerce_grcv2_params(config)


def _required_node_mass(blueprint: GRCV2LandscapeNodeBlueprint) -> float:
    if blueprint.coherence_prior is None:
        raise InvalidLandscapeSeedError(
            f"node-carrying primitive {blueprint.primitive_id!r} requires coherence_prior "
            "for GRCV2 initialization"
        )
    return float(blueprint.coherence_prior)


def _euclidean_length(
    point_a: tuple[float, float] | None,
    point_b: tuple[float, float] | None,
) -> float | None:
    if point_a is None or point_b is None:
        return None
    return math.dist(point_a, point_b)


def _edge_weight_from_blueprint(
    edge_blueprint: GRCV2LandscapeEdgeBlueprint,
    *,
    node_mass_by_primitive_id: Mapping[str, float],
) -> float:
    if edge_blueprint.primitive_type == "valley":
        base = (
            float(edge_blueprint.coherence_prior)
            if edge_blueprint.coherence_prior is not None
            else 0.5
            * (
                node_mass_by_primitive_id[edge_blueprint.source_primitive_id]
                + node_mass_by_primitive_id[edge_blueprint.target_primitive_id]
            )
        )
        width = 0.0 if edge_blueprint.width_hint is None else float(edge_blueprint.width_hint)
        return max(1e-6, base / (1.0 + width))

    interior = edge_blueprint.metadata.get("interior_coherence_hint")
    exterior = edge_blueprint.metadata.get("exterior_coherence_hint")
    interior_value = (
        float(interior)
        if isinstance(interior, int | float)
        else node_mass_by_primitive_id[edge_blueprint.source_primitive_id]
    )
    exterior_value = (
        float(exterior)
        if isinstance(exterior, int | float)
        else node_mass_by_primitive_id[edge_blueprint.target_primitive_id]
    )
    width = 0.0 if edge_blueprint.width_hint is None else float(edge_blueprint.width_hint)
    return max(1e-6, (0.5 * (interior_value + exterior_value)) / (1.0 + width))


def _transport_intent_edge_multipliers(
    seed: LandscapeSeed,
    *,
    edge_id_by_primitive_id: Mapping[str, int],
) -> dict[int, float]:
    multipliers: dict[int, float] = {}
    for intent in seed.transport_intent:
        if intent.carrier_id is None:
            continue
        edge_id = edge_id_by_primitive_id.get(intent.carrier_id)
        if edge_id is None:
            continue
        magnitude = 0.0 if intent.magnitude_hint is None else float(intent.magnitude_hint)
        priority = 0.0 if intent.priority is None else float(intent.priority)
        multiplier = max(1.0, 1.0 + magnitude + priority)
        multipliers[edge_id] = multipliers.get(edge_id, 1.0) * multiplier
    return multipliers


def _transport_intent_metadata(intents: list[SeedTransportIntent]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "id": intent.id,
            "mode": intent.mode,
            "sources": tuple(intent.sources),
            "targets": tuple(intent.targets),
            "magnitude_hint": intent.magnitude_hint,
            "priority": intent.priority,
            "carrier_id": intent.carrier_id,
            "direction_hint": intent.direction_hint,
            "notes": intent.notes,
        }
        for intent in intents
    )


def _edge_directionality_semantics(edge_blueprint: GRCV2LandscapeEdgeBlueprint) -> str:
    if edge_blueprint.primitive_type == "ridge":
        return "structural_support"
    if edge_blueprint.primitive_type == "valley":
        return "transport_channel"
    return "runtime_oriented_edge"


def project_landscape_seed_to_grcv2_state(
    seed: LandscapeSeedInput,
    *,
    params: GRCV2ParamsInput,
    validate_seed: bool = True,
) -> GRCV2State:
    """Project one validated landscape seed into an initial GRCV2 state."""

    request = prepare_grcv2_landscape_projection(
        seed,
        params=params,
        validate_seed=validate_seed,
    )
    blueprint = realize_grcv2_landscape_blueprint(request.seed, validate_seed=False)

    topology = WeightedGraphBackend()
    node_id_by_primitive_id: dict[str, int] = {}
    node_blueprint_by_primitive_id = {
        blueprint_node.primitive_id: blueprint_node for blueprint_node in blueprint.node_blueprints
    }
    raw_node_masses = {
        blueprint_node.primitive_id: _required_node_mass(blueprint_node)
        for blueprint_node in blueprint.node_blueprints
    }
    total_raw_mass = float(sum(raw_node_masses.values()))
    budget_target = (
        float(request.seed.constitutive_profile.budget_b)
        if request.seed.constitutive_profile.budget_b is not None
        else total_raw_mass
    )
    if total_raw_mass <= 0.0:
        raise InvalidLandscapeSeedError(
            "projected GRCV2 node priors must sum to a positive initial mass"
        )
    mass_scale = budget_target / total_raw_mass

    for blueprint_node in blueprint.node_blueprints:
        node_payload = {
            "primitive_id": blueprint_node.primitive_id,
            "primitive_type": blueprint_node.primitive_type,
            "role": blueprint_node.role,
            "parent_id": blueprint_node.parent_id,
            "chart_center_hint": blueprint_node.chart_center_hint,
            "chart_scale_hint": _to_plain_data(blueprint_node.chart_scale_hint),
            "metadata": _to_plain_data(blueprint_node.metadata),
        }
        if "junction_anchor_mode" in blueprint_node.metadata:
            node_payload["is_hostless"] = bool(blueprint_node.metadata.get("is_hostless", False))
            node_payload["junction_anchor_mode"] = blueprint_node.metadata.get(
                "junction_anchor_mode",
                "hosted",
            )
        node_id_by_primitive_id[blueprint_node.primitive_id] = topology.add_node(node_payload)

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

    edges: dict[int, float] = {}
    edge_id_by_primitive_id: dict[str, int] = {}
    geometric_length: dict[int, float] = {}
    for edge_blueprint in blueprint.edge_blueprints:
        source_node_id = node_id_by_primitive_id[edge_blueprint.source_primitive_id]
        target_node_id = node_id_by_primitive_id[edge_blueprint.target_primitive_id]
        source_center = node_blueprint_by_primitive_id[
            edge_blueprint.source_primitive_id
        ].chart_center_hint
        target_center = node_blueprint_by_primitive_id[
            edge_blueprint.target_primitive_id
        ].chart_center_hint
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
        edge_id_by_primitive_id[edge_blueprint.primitive_id] = edge_id
        edges[edge_id] = _edge_weight_from_blueprint(
            edge_blueprint,
            node_mass_by_primitive_id=raw_node_masses,
        )
        if ambient_length is not None:
            geometric_length[edge_id] = max(1e-12, ambient_length)

    landscape_base_edge_conductance = dict(edges)
    edge_weight_multipliers = _transport_intent_edge_multipliers(
        request.seed,
        edge_id_by_primitive_id=edge_id_by_primitive_id,
    )
    for edge_id in sorted(edges):
        multiplier = float(edge_weight_multipliers.get(edge_id, 1.0))
        edge_payload = topology.edge_payload(edge_id)
        edge_payload["landscape_base_conductance"] = float(landscape_base_edge_conductance[edge_id])
        edge_payload["transport_intent_multiplier"] = multiplier
        edges[edge_id] = float(edges[edge_id] * multiplier)
        edge_payload["transport_biased_initial_conductance"] = float(edges[edge_id])

    state = GRCV2State(
        topology=topology,
        nodes={
            node_id_by_primitive_id[primitive_id]: float(raw_mass * mass_scale)
            for primitive_id, raw_mass in raw_node_masses.items()
        },
        edges=edges,
        geometric_length=geometric_length,
        temporal_delay={},
        flux_coupling={},
        flux={},
        potential={node_id: 0.0 for node_id in topology.iter_live_node_ids()},
        sink_set=set(),
        basins={},
        split_registry={},
        step_index=0,
        time=0.0,
        budget_target=float(budget_target),
        remainder=0.0,
        cached_quantities={
            "landscape_seed_name": request.seed.meta.name,
            "landscape_seed_source_reference": request.seed.meta.source_reference,
            "landscape_seed_path": None if request.seed_path is None else str(request.seed_path),
            "landscape_seed_validation_mode": _strict_seed_validation_mode(),
            "landscape_transport_intent": _transport_intent_metadata(request.seed.transport_intent),
            "landscape_node_id_by_primitive_id": dict(sorted(node_id_by_primitive_id.items())),
            "landscape_edge_id_by_primitive_id": dict(sorted(edge_id_by_primitive_id.items())),
            "landscape_base_edge_conductance": {
                edge_id: float(value)
                for edge_id, value in sorted(landscape_base_edge_conductance.items())
            },
            "landscape_transport_intent_multiplier": {
                edge_id: float(edge_weight_multipliers.get(edge_id, 1.0))
                for edge_id in sorted(edges)
            },
            "landscape_ridge_ids_by_owner": {
                owner_id: list(ridge_ids)
                for owner_id, ridge_ids in blueprint.ridge_ids_by_owner.items()
            },
            "landscape_metadata_only_ridge_ids": list(blueprint.metadata_only_ridge_ids),
            "landscape_blueprint_summary": {
                "node_primitive_ids": list(blueprint.node_primitive_ids),
                "edge_primitive_ids": list(blueprint.edge_primitive_ids),
            },
            "landscape_transport_bias_mode": "carrier_edge_weight_multiplier",
            "landscape_mass_scale": float(mass_scale),
            "landscape_budget_mode": (
                "explicit_budget_b"
                if request.seed.constitutive_profile.budget_b is not None
                else "sum_of_node_priors"
            ),
        },
        event_log=[],
        observables={},
        rng_state=None,
        params_identity=request.params.params_hash,
    )
    return state


def build_grcv2_from_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    params: GRCV2ParamsInput,
    validate_seed: bool = True,
) -> GRCV2:
    """Construct one executable GRCV2 model from a landscape seed."""

    state = project_landscape_seed_to_grcv2_state(
        seed,
        params=params,
        validate_seed=validate_seed,
    )
    request = prepare_grcv2_landscape_projection(
        seed,
        params=params,
        validate_seed=False,
    )
    return GRCV2(params=request.params, state=state)


def build_grcv2_from_landscape_family(
    seed: LandscapeSeedInput,
    *,
    family_name: str = "balanced_baseline",
    overrides: Mapping[str, Any] | None = None,
    rng_seed: int | None = None,
    validate_seed: bool = True,
) -> GRCV2:
    """Construct one executable GRCV2 model from a seed plus named family."""

    resolved_params = resolve_grcv2_landscape_params(
        seed,
        family_name=family_name,
        overrides=overrides,
        rng_seed=rng_seed,
        validate_seed=validate_seed,
    )
    return build_grcv2_from_landscape_seed(
        seed,
        params=resolved_params,
        validate_seed=False,
    )


def run_grcv2_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    num_steps: int,
    family_name: str = "balanced_baseline",
    overrides: Mapping[str, Any] | None = None,
    rng_seed: int | None = None,
    telemetry_root: str | Path | None = None,
    telemetry_experiment_path: str | Path | None = None,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
    validate_seed: bool = True,
) -> GRCV2LandscapeRunResult:
    """Run one landscape seed through GRCV2 for a fixed number of steps."""

    resolved_seed, seed_path = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    resolved_params = resolve_grcv2_landscape_params(
        resolved_seed,
        family_name=family_name,
        overrides=overrides,
        rng_seed=rng_seed,
        validate_seed=False,
    )
    request = GRCV2LandscapeProjectionRequest(
        seed=resolved_seed,
        params=resolved_params,
        seed_path=seed_path,
    )
    blueprint = realize_grcv2_landscape_blueprint(resolved_seed, validate_seed=False)
    model = build_grcv2_from_landscape_seed(
        resolved_seed,
        params=resolved_params,
        validate_seed=False,
    )
    initial_observables = dict(model.compute_observables())
    step_results: list[StepResult] = []
    from pygrc.telemetry import (
        DEFAULT_TELEMETRY_ROOT,
        GraphCheckpointCaptureConfig,
        GraphCheckpointChunkWriter,
        GraphCheckpointIndex,
        GraphCheckpointReference,
        RunTelemetryIdentity,
        TelemetryCaptureConfig,
        build_telemetry_artifact_layout,
        build_run_id,
        capture_run_telemetry,
    )

    resolved_checkpoint_storage_mode = checkpoint_storage_mode
    if resolved_checkpoint_storage_mode is None:
        resolved_checkpoint_storage_mode = (
            "jsonl_chunks" if checkpoint_every_step else "per_checkpoint_files"
        )
    checkpoint_config = (
        GraphCheckpointCaptureConfig(
            include_initial=True,
            include_final=True,
            every_step=checkpoint_every_step,
            every_n_steps=checkpoint_every_n_steps,
            include_flow_overlays=include_flow_overlays,
            storage_mode=resolved_checkpoint_storage_mode,
            chunk_size=checkpoint_chunk_size,
        )
        if record_graph_checkpoints
        else None
    )
    run_identity = RunTelemetryIdentity(
        run_id=build_run_id(
            model_family="grcv2",
            params_identity=resolved_params.params_hash,
            seed_name=resolved_seed.meta.name,
            seed_source_reference=resolved_seed.meta.source_reference,
            seed_path=None if seed_path is None else str(seed_path),
            param_family=family_name,
            rng_seed=rng_seed,
            requested_steps=num_steps,
            overrides=overrides,
        ),
        model_family="grcv2",
        params_identity=resolved_params.params_hash,
        seed_name=resolved_seed.meta.name,
        seed_source_reference=resolved_seed.meta.source_reference,
        seed_path=None if seed_path is None else str(seed_path),
        param_family=family_name,
        rng_seed=rng_seed,
        requested_steps=num_steps,
    )
    write_telemetry_artifacts = telemetry_root is not None
    streamed_artifact_layout = None
    checkpoint_chunk_writer: GraphCheckpointChunkWriter | None = None
    streamed_checkpoint_references: list[GraphCheckpointReference] = []
    graph_checkpoints: list[Any] = []
    if checkpoint_config is not None and checkpoint_config.storage_mode == "jsonl_chunks":
        if not write_telemetry_artifacts:
            raise ValueError(
                "checkpoint_storage_mode='jsonl_chunks' requires telemetry_root so "
                "dense checkpoints can be streamed to artifacts"
            )
        streamed_artifact_layout = build_telemetry_artifact_layout(
            run_identity.run_id,
            root_dir=DEFAULT_TELEMETRY_ROOT if telemetry_root is None else telemetry_root,
            experiment_path=telemetry_experiment_path,
        )
        checkpoint_chunk_writer = GraphCheckpointChunkWriter(
            streamed_artifact_layout,
            chunk_size=checkpoint_config.chunk_size,
        )

    def record_graph_checkpoint(checkpoint: Any) -> None:
        if checkpoint_chunk_writer is not None:
            streamed_checkpoint_references.append(checkpoint_chunk_writer.write(checkpoint))
            return
        graph_checkpoints.append(checkpoint)

    if checkpoint_config is not None and checkpoint_config.include_initial:
        record_graph_checkpoint(
            export_grcv2_graph_checkpoint(
                model,
                identity=run_identity,
                checkpoint_id="step-00000000",
                checkpoint_label="initial",
                checkpoint_reason="initial",
                event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
                event_count_window=0,
                event_counts_by_kind_window={},
                include_flow_overlays=checkpoint_config.include_flow_overlays,
            )
        )

    last_checkpoint_step_index = 0
    event_counts_since_checkpoint: dict[str, int] = {}
    event_count_since_checkpoint = 0
    for _ in range(num_steps):
        step_result = model.step()
        step_results.append(step_result)
        for event in step_result.events:
            event_counts_since_checkpoint[event.kind] = (
                event_counts_since_checkpoint.get(event.kind, 0) + 1
            )
        event_count_since_checkpoint += len(step_result.events)
        if checkpoint_config is None:
            continue
        should_capture = False
        checkpoint_label = "interval"
        checkpoint_reason = "interval"
        if checkpoint_config.every_step:
            should_capture = True
        elif (
            checkpoint_config.every_n_steps is not None
            and step_result.step_index % checkpoint_config.every_n_steps == 0
        ):
            should_capture = True
        if checkpoint_config.include_final and step_result.step_index == num_steps:
            should_capture = True
            checkpoint_label = "final"
            checkpoint_reason = "final"
        if not should_capture:
            continue
        record_graph_checkpoint(
            export_grcv2_graph_checkpoint(
                model,
                identity=run_identity,
                checkpoint_id=f"step-{step_result.step_index:08d}",
                checkpoint_label=checkpoint_label,
                checkpoint_reason=checkpoint_reason,
                event_step_range={
                    "start_step_inclusive": last_checkpoint_step_index + 1,
                    "end_step_inclusive": step_result.step_index,
                },
                event_count_window=event_count_since_checkpoint,
                event_counts_by_kind_window=dict(sorted(event_counts_since_checkpoint.items())),
                include_flow_overlays=checkpoint_config.include_flow_overlays,
            )
        )
        last_checkpoint_step_index = step_result.step_index
        event_counts_since_checkpoint = {}
        event_count_since_checkpoint = 0
    final_observables = dict(model.compute_observables())
    model.get_state().cached_quantities["landscape_param_family"] = family_name
    graph_checkpoint_index = (
        GraphCheckpointIndex(
            identity=run_identity,
            selection_policy=checkpoint_config.selection_policy,
            selection_params=checkpoint_config.selection_params,
            checkpoints=tuple(streamed_checkpoint_references),
        )
        if streamed_checkpoint_references
        else None
    )
    telemetry = capture_run_telemetry(
        model_family="grcv2",
        params_identity=resolved_params.params_hash,
        seed_name=resolved_seed.meta.name,
        seed_source_reference=resolved_seed.meta.source_reference,
        seed_path=None if seed_path is None else str(seed_path),
        param_family=family_name,
        rng_seed=rng_seed,
        requested_steps=num_steps,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
        resolved_params=resolved_params.resolved_config,
        raw_params=resolved_params.raw_config,
        overrides=overrides,
        family_extensions={
            "grcv2": {
                "param_family": family_name,
                "seed_schema": resolved_seed.seed_schema,
                "budget_mode": model.get_state().cached_quantities.get("landscape_budget_mode"),
            }
        },
        graph_checkpoints=graph_checkpoints,
        graph_checkpoint_index=graph_checkpoint_index,
        artifact_layout=streamed_artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=DEFAULT_TELEMETRY_ROOT if telemetry_root is None else telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=write_telemetry_artifacts,
            graph_checkpoints=checkpoint_config,
        ),
    )
    return GRCV2LandscapeRunResult(
        request=request,
        blueprint=blueprint,
        model=model,
        initial_observables=initial_observables,
        step_results=list(step_results),
        final_observables=final_observables,
        telemetry=telemetry,
    )


__all__ = [
    "GRCV2LandscapeBlueprint",
    "GRCV2LandscapeEdgeBlueprint",
    "GRCV2LandscapeNodeBlueprint",
    "GRCV2LandscapeParamFamily",
    "GRCV2LandscapeProjectionRequest",
    "GRCV2LandscapeRunResult",
    "GRCV2ParamsInput",
    "LandscapeSeedInput",
    "build_grcv2_from_landscape_family",
    "build_grcv2_from_landscape_seed",
    "get_grcv2_landscape_param_family",
    "list_grcv2_landscape_param_families",
    "prepare_grcv2_landscape_projection",
    "realize_grcv2_landscape_blueprint",
    "project_landscape_seed_to_grcv2_state",
    "resolve_grcv2_landscape_params",
    "run_grcv2_landscape_seed",
]

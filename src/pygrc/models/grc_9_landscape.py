"""Structural landscape-seed lowering for the Phase 6 GRC9 mechanical family."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
import math
from pathlib import Path
import random
from typing import TYPE_CHECKING, Any, TypeAlias

from pygrc.core import (
    GRCParams,
    InvalidLandscapeSeedError,
    PortGraphBackend,
    StepResult,
)
from pygrc.landscapes import (
    LandscapeSeed,
    SeedTransportIntent,
    load_landscape_seed,
    validate_landscape_seed,
)

from .grc_9 import GRC9
from .grc_9_ports import port_id_to_slot
from .grc_9_state import GRC9State, PortEdge
from .grc_v2_landscape import (
    GRCV2LandscapeBlueprint,
    GRCV2LandscapeEdgeBlueprint,
    GRCV2LandscapeNodeBlueprint,
    realize_grcv2_landscape_blueprint,
)

if TYPE_CHECKING:
    from pygrc.telemetry.recorder import TelemetryCaptureResult


LandscapeSeedInput: TypeAlias = LandscapeSeed | str | Path
GRC9ParamsInput: TypeAlias = GRCParams | Mapping[str, Any]

_DEFAULT_GRC9_LANDSCAPE_DT = 0.1
_DEFAULT_GRC9_LANDSCAPE_RNG_SEED = 7


@dataclass(frozen=True)
class GRC9LandscapeProjectionRequest:
    """Validated family-local input for seed-driven GRC9 structural lowering."""

    seed: LandscapeSeed
    params: GRCParams
    seed_path: Path | None = None


@dataclass
class GRC9LandscapeRunResult:
    """Executable trajectory result for one seed-driven GRC9 run."""

    request: GRC9LandscapeProjectionRequest
    blueprint: GRCV2LandscapeBlueprint
    model: GRC9
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    telemetry: TelemetryCaptureResult | None = None


def _coerce_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    validate_seed: bool,
) -> tuple[LandscapeSeed, Path | None]:
    seed_path: Path | None = None
    if isinstance(seed, LandscapeSeed):
        resolved_seed = seed
    else:
        seed_path = Path(seed)
        resolved_seed = load_landscape_seed(seed_path)
    if validate_seed:
        validate_landscape_seed(resolved_seed)
    return resolved_seed, seed_path


def _coerce_grc9_params(params: GRC9ParamsInput) -> GRCParams:
    if isinstance(params, GRCParams):
        return params
    if not isinstance(params, Mapping):
        raise TypeError("params input must be a GRCParams instance or a mapping")
    return GRC9.from_config(dict(params)).get_params()


def _deep_merge_mapping(
    base: Mapping[str, Any],
    overrides: Mapping[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key, value in overrides.items():
        if (
            key in merged
            and isinstance(merged[key], Mapping)
            and isinstance(value, Mapping)
        ):
            merged[key] = _deep_merge_mapping(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _required_node_mass(blueprint: GRCV2LandscapeNodeBlueprint) -> float:
    if blueprint.coherence_prior is None:
        raise InvalidLandscapeSeedError(
            f"node-carrying primitive {blueprint.primitive_id!r} requires coherence_prior "
            "for GRC9 structural initialization"
        )
    return float(blueprint.coherence_prior)


def _site_potential_from_seed(seed: LandscapeSeed) -> tuple[str, dict[str, Any], dict[str, Any]]:
    potential = seed.constitutive_profile.potential
    potential_type = potential.type
    params = dict(potential.params)
    if potential_type == "double_well":
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
        f"unsupported seed potential type {potential_type!r} for GRC9 landscape projection"
    )


def _to_plain_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _to_plain_data(inner_value) for key, inner_value in value.items()}
    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]
    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]
    return value


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
    intents: list[SeedTransportIntent],
) -> dict[str, float]:
    multipliers: dict[str, float] = {}
    for intent in intents:
        if intent.carrier_id is None:
            continue
        magnitude = 0.0 if intent.magnitude_hint is None else float(intent.magnitude_hint)
        priority = 0.0 if intent.priority is None else float(intent.priority)
        multiplier = max(1.0, 1.0 + magnitude + priority)
        multipliers[intent.carrier_id] = multipliers.get(intent.carrier_id, 1.0) * multiplier
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


def _canonical_port_edge(
    *,
    node_a: int,
    port_a: int,
    node_b: int,
    port_b: int,
    conductance: float,
    flux_uv: float,
) -> PortEdge:
    if (node_a, port_a) <= (node_b, port_b):
        return PortEdge(
            node_u=node_a,
            port_u=port_a,
            node_v=node_b,
            port_v=port_b,
            conductance=float(conductance),
            flux_uv=float(flux_uv),
        )
    return PortEdge(
        node_u=node_b,
        port_u=port_b,
        node_v=node_a,
        port_v=port_a,
        conductance=float(conductance),
        flux_uv=float(-flux_uv),
    )


def prepare_grc9_landscape_projection(
    seed: LandscapeSeedInput,
    *,
    params: GRC9ParamsInput,
    validate_seed: bool = True,
) -> GRC9LandscapeProjectionRequest:
    """Normalize seed and params into one validated GRC9 landscape request."""

    resolved_seed, seed_path = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    resolved_params = _coerce_grc9_params(params)
    return GRC9LandscapeProjectionRequest(
        seed=resolved_seed,
        params=resolved_params,
        seed_path=seed_path,
    )


def resolve_grc9_landscape_params(
    seed: LandscapeSeedInput,
    *,
    overrides: Mapping[str, Any] | None = None,
    rng_seed: int | None = _DEFAULT_GRC9_LANDSCAPE_RNG_SEED,
    validate_seed: bool = True,
) -> GRCParams:
    """Resolve the baseline mechanical GRC9 config for one landscape seed."""

    resolved_seed, _ = _coerce_landscape_seed(seed, validate_seed=validate_seed)
    site_selection, site_params, _ = _site_potential_from_seed(resolved_seed)
    config: dict[str, Any] = {
        "dt": _DEFAULT_GRC9_LANDSCAPE_DT,
        "evolution": {
            "rng_seed": rng_seed,
            "eps_spark": 1e6,
            "lambda_birth": 0.0,
            "D_eff_target": 30,
            "w_bond": 1.0,
            "alpha_seed": 0.1,
            "adiabatic_expansion_substeps": 1,
            "site_potential_selection": site_selection,
            "site_potential_params": site_params,
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }
    if overrides is not None:
        config = _deep_merge_mapping(config, overrides)
    return _coerce_grc9_params(config)


def project_landscape_seed_to_grc9_state(
    seed: LandscapeSeedInput,
    *,
    params: GRC9ParamsInput,
    validate_seed: bool = True,
) -> GRC9State:
    """Project one validated landscape seed into an initial GRC9 mechanical state."""

    request = prepare_grc9_landscape_projection(
        seed,
        params=params,
        validate_seed=validate_seed,
    )
    blueprint = realize_grcv2_landscape_blueprint(request.seed, validate_seed=False)

    topology = PortGraphBackend()
    node_id_by_primitive_id: dict[str, int] = {}
    node_blueprint_by_primitive_id = {
        node_blueprint.primitive_id: node_blueprint
        for node_blueprint in blueprint.node_blueprints
    }
    raw_node_masses = {
        node_blueprint.primitive_id: _required_node_mass(node_blueprint)
        for node_blueprint in blueprint.node_blueprints
    }
    total_raw_mass = float(sum(raw_node_masses.values()))
    budget_target = (
        float(request.seed.constitutive_profile.budget_b)
        if request.seed.constitutive_profile.budget_b is not None
        else total_raw_mass
    )
    if total_raw_mass <= 0.0:
        raise InvalidLandscapeSeedError(
            "projected GRC9 node priors must sum to a positive initial mass"
        )
    mass_scale = budget_target / total_raw_mass
    site_selection, site_params, site_metadata = _site_potential_from_seed(request.seed)

    for node_blueprint in blueprint.node_blueprints:
        node_payload = {
            "primitive_id": node_blueprint.primitive_id,
            "primitive_type": node_blueprint.primitive_type,
            "role": node_blueprint.role,
            "parent_id": node_blueprint.parent_id,
            "chart_center_hint": node_blueprint.chart_center_hint,
            "chart_scale_hint": _to_plain_data(node_blueprint.chart_scale_hint),
            "metadata": _to_plain_data(node_blueprint.metadata),
            "landscape_realization": "grc9_structural_graph_graft_v1",
        }
        node_id_by_primitive_id[node_blueprint.primitive_id] = topology.add_node(node_payload)

    transport_intent_multipliers = _transport_intent_edge_multipliers(request.seed.transport_intent)
    edge_assignments_by_primitive_id: dict[str, tuple[int, str, str]] = {}
    incident_edges_by_primitive_id: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge_index, edge_blueprint in enumerate(blueprint.edge_blueprints):
        edge_assignments_by_primitive_id[edge_blueprint.primitive_id] = (
            edge_index,
            edge_blueprint.source_primitive_id,
            edge_blueprint.target_primitive_id,
        )
        incident_edges_by_primitive_id[edge_blueprint.source_primitive_id].append(
            (edge_blueprint.primitive_id, edge_blueprint.target_primitive_id)
        )
        incident_edges_by_primitive_id[edge_blueprint.target_primitive_id].append(
            (edge_blueprint.primitive_id, edge_blueprint.source_primitive_id)
        )

    port_id_by_node_and_edge: dict[int, dict[str, int]] = {}
    for primitive_id, node_id in sorted(
        node_id_by_primitive_id.items(),
        key=lambda item: item[1],
    ):
        incident_edges = incident_edges_by_primitive_id.get(primitive_id, [])
        if len(incident_edges) > 9:
            raise InvalidLandscapeSeedError(
                f"primitive {primitive_id!r} lowers to degree {len(incident_edges)}, "
                "which exceeds the GRC9 nine-slot capacity"
            )
        sorted_incident_edges = sorted(
            incident_edges,
            key=lambda item: (
                node_id_by_primitive_id[item[1]],
                item[1],
                edge_assignments_by_primitive_id[item[0]][0],
                item[0],
            ),
        )
        port_id_by_node_and_edge[node_id] = {
            edge_primitive_id: index + 1
            for index, (edge_primitive_id, _) in enumerate(sorted_incident_edges)
        }

    port_edges: dict[int, PortEdge] = {}
    geometric_length: dict[int, float] = {}
    edge_id_by_primitive_id: dict[str, int] = {}
    landscape_base_edge_conductance: dict[int, float] = {}
    landscape_transport_intent_multiplier: dict[int, float] = {}
    for edge_blueprint in blueprint.edge_blueprints:
        source_node_id = node_id_by_primitive_id[edge_blueprint.source_primitive_id]
        target_node_id = node_id_by_primitive_id[edge_blueprint.target_primitive_id]
        source_port_id = port_id_by_node_and_edge[source_node_id][edge_blueprint.primitive_id]
        target_port_id = port_id_by_node_and_edge[target_node_id][edge_blueprint.primitive_id]
        source_center = node_blueprint_by_primitive_id[
            edge_blueprint.source_primitive_id
        ].chart_center_hint
        target_center = node_blueprint_by_primitive_id[
            edge_blueprint.target_primitive_id
        ].chart_center_hint
        ambient_length = _euclidean_length(source_center, target_center)
        base_conductance = _edge_weight_from_blueprint(
            edge_blueprint,
            node_mass_by_primitive_id=raw_node_masses,
        )
        transport_multiplier = float(
            transport_intent_multipliers.get(edge_blueprint.primitive_id, 1.0)
        )
        conductance = float(base_conductance * transport_multiplier)
        edge_payload = {
            "primitive_id": edge_blueprint.primitive_id,
            "primitive_type": edge_blueprint.primitive_type,
            "role": edge_blueprint.role,
            "path_hint": edge_blueprint.path_hint,
            "directionality_semantics": _edge_directionality_semantics(edge_blueprint),
            "metadata": _to_plain_data(edge_blueprint.metadata),
            "landscape_realization": "grc9_structural_graph_graft_v1",
            "landscape_base_conductance": float(base_conductance),
            "transport_intent_multiplier": transport_multiplier,
            "transport_biased_initial_conductance": conductance,
        }
        if ambient_length is not None:
            edge_payload["ambient_length"] = ambient_length
        edge_id = topology.connect_ports(
            source_node_id,
            port_id_to_slot(source_port_id),
            target_node_id,
            port_id_to_slot(target_port_id),
            edge_payload,
        )
        edge_id_by_primitive_id[edge_blueprint.primitive_id] = edge_id
        landscape_base_edge_conductance[edge_id] = float(base_conductance)
        landscape_transport_intent_multiplier[edge_id] = transport_multiplier
        if ambient_length is not None:
            geometric_length[edge_id] = max(1e-12, ambient_length)
        port_edges[edge_id] = _canonical_port_edge(
            node_a=source_node_id,
            port_a=source_port_id,
            node_b=target_node_id,
            port_b=target_port_id,
            conductance=conductance,
            flux_uv=0.0,
        )

    rng_seed = request.params.evolution.get("rng_seed")
    rng_state = None if rng_seed is None else random.Random(int(rng_seed)).getstate()
    return GRC9State(
        topology=topology,
        node_coherence={
            node_id_by_primitive_id[primitive_id]: float(raw_mass * mass_scale)
            for primitive_id, raw_mass in raw_node_masses.items()
        },
        port_edges=port_edges,
        geometric_length=geometric_length,
        temporal_delay={},
        flux_coupling={},
        potential={node_id: 0.0 for node_id in topology.iter_live_node_ids()},
        sink_set=set(),
        basins={},
        expansion_registry={},
        coarse_cache={},
        rng_state=rng_state,
        prev_column_diagnostic={},
        edge_label_computation_mode={},
        edge_label_params={},
        step_index=0,
        time=0.0,
        budget_target=float(budget_target),
        remainder=0.0,
        cached_quantities={
            "landscape_seed_name": request.seed.meta.name,
            "landscape_seed_source_reference": request.seed.meta.source_reference,
            "landscape_seed_path": None if request.seed_path is None else str(request.seed_path),
            "landscape_projection_mode": "grc9_structural_graph_graft_v1",
            "landscape_port_assignment_mode": "row_major_by_neighbor_then_edge",
            "landscape_node_id_by_primitive_id": dict(sorted(node_id_by_primitive_id.items())),
            "landscape_edge_id_by_primitive_id": dict(sorted(edge_id_by_primitive_id.items())),
            "landscape_port_id_by_node_and_edge": {
                str(node_id): {
                    edge_primitive_id: int(port_id)
                    for edge_primitive_id, port_id in sorted(edge_mapping.items())
                }
                for node_id, edge_mapping in sorted(port_id_by_node_and_edge.items())
            },
            "landscape_base_edge_conductance": {
                edge_id: float(value)
                for edge_id, value in sorted(landscape_base_edge_conductance.items())
            },
            "landscape_transport_intent_multiplier": {
                edge_id: float(value)
                for edge_id, value in sorted(landscape_transport_intent_multiplier.items())
            },
            "landscape_transport_intent": _transport_intent_metadata(
                request.seed.transport_intent
            ),
            "landscape_blueprint_summary": {
                "node_primitive_ids": list(blueprint.node_primitive_ids),
                "edge_primitive_ids": list(blueprint.edge_primitive_ids),
            },
            "landscape_ridge_ids_by_owner": {
                owner_id: list(ridge_ids)
                for owner_id, ridge_ids in blueprint.ridge_ids_by_owner.items()
            },
            "landscape_metadata_only_ridge_ids": list(blueprint.metadata_only_ridge_ids),
            "landscape_mass_scale": float(mass_scale),
            "landscape_budget_mode": (
                "explicit_budget_b"
                if request.seed.constitutive_profile.budget_b is not None
                else "sum_of_node_priors"
            ),
            "landscape_site_potential": {
                "selection": site_selection,
                "params": deepcopy(site_params),
                "source_metadata": deepcopy(site_metadata),
            },
        },
        params_identity=request.params.params_hash,
    )


def build_grc9_from_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    params: GRC9ParamsInput,
    validate_seed: bool = True,
) -> GRC9:
    """Construct one executable GRC9 model from a landscape seed."""

    request = prepare_grc9_landscape_projection(
        seed,
        params=params,
        validate_seed=validate_seed,
    )
    state = project_landscape_seed_to_grc9_state(
        request.seed,
        params=request.params,
        validate_seed=False,
    )
    return GRC9(params=request.params, state=state)


def run_grc9_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    num_steps: int,
    params: GRC9ParamsInput,
    validate_seed: bool = True,
) -> GRC9LandscapeRunResult:
    """Run one landscape seed through GRC9 for a fixed number of steps."""

    request = prepare_grc9_landscape_projection(
        seed,
        params=params,
        validate_seed=validate_seed,
    )
    blueprint = realize_grcv2_landscape_blueprint(request.seed, validate_seed=False)
    model = build_grc9_from_landscape_seed(
        request.seed,
        params=request.params,
        validate_seed=False,
    )
    initial_observables = dict(model.compute_observables())
    step_results: list[StepResult] = []
    for _ in range(num_steps):
        step_results.append(model.step())
    final_observables = dict(model.compute_observables())
    return GRC9LandscapeRunResult(
        request=request,
        blueprint=blueprint,
        model=model,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
    )


__all__ = [
    "GRC9LandscapeProjectionRequest",
    "GRC9LandscapeRunResult",
    "build_grc9_from_landscape_seed",
    "prepare_grc9_landscape_projection",
    "project_landscape_seed_to_grc9_state",
    "resolve_grc9_landscape_params",
    "run_grc9_landscape_seed",
]

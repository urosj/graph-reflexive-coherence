"""Construction and state surface for the GRC9V3 hybrid family."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import math
import random
from typing import Any, Final

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    GRC9V3_CAPABILITY_PROFILE,
    GRCEvent,
    GRCModel,
    GRCParams,
    InvalidParamsError,
    InvalidStateTransitionError,
    ObservableMap,
    SnapshotCompatibilityError,
    StepResult,
    build_dynamics_group,
    build_event_records,
    build_reset_baseline_group,
    build_snapshot_metadata,
    build_standard_snapshot,
    deserialize_rng_state,
    export_port_topology,
    load_snapshot,
    require_snapshot_family,
    reset_baseline_snapshot,
    restore_port_graph,
    save_snapshot,
    serialize_rng_state,
)

from .grc_9_coarse import (
    coarse_grain_nonnegative_port_field,
    coarse_grain_signed_flux_field,
    split_nonnegative_port_field,
    split_signed_flux_field,
)
from .grc_9_ports import port_id_to_slot, slot_to_port_id
from .grc_9_state import AdiabaticExpansionSchedule, ExpansionRecord, PortEdge
from .grc_9_v3_choice import (
    apply_grc9v3_boundary_behavior,
    enforce_grc9v3_quadrature_budget,
    rebuild_grc9v3_choice_state,
    refresh_grc9v3_coarse_cache,
)
from .grc_9_v3_sparks import (
    apply_mechanical_expansion,
    detect_hybrid_spark_candidates,
    evaluate_child_basin_stabilization,
    register_completed_hybrid_spark,
)
from .grc_9_v3_runtime import (
    rebuild_grc9v3_differential_state,
    rebuild_grc9v3_identity_state,
    rebuild_grc9v3_transport_state,
)
from .grc_9_v3_state import GRC9V3NodeState, GRC9V3State


_ALLOWED_FRAME_MODES: Final[set[str]] = {"fixed_port_chart"}
_ALLOWED_BOUNDARY_MODES: Final[set[str]] = {"prune", "barrier", "ghost"}
_ALLOWED_EXPANSION_DISTRIBUTION_MODES: Final[set[str]] = {"equal", "custom"}
_ALLOWED_CURVATURE_BACKENDS: Final[set[str]] = {"none", "forman", "ollivier"}
_ALLOWED_HESSIAN_BACKENDS: Final[set[str]] = {
    "row_basis_diagonal",
    "weighted_least_squares",
}
_ALLOWED_BUDGET_CORRECTION_METHODS: Final[set[str]] = {
    "uniform_shift",
    "simplex_projection",
}
_ALLOWED_CHOICE_BACKENDS: Final[set[str]] = {
    "disabled",
    "sink_compatibility",
}
_ALLOWED_QUADRATURE_MODES: Final[set[str]] = {"unit_measure"}
_ALLOWED_SPARK_LANES: Final[set[str]] = {
    "current_hybrid_signed_hessian",
    "grc9v3_column_h_assisted",
}
_ALLOWED_COLUMN_H_SIGN_CROSSING_MODES: Final[set[str]] = {
    "theory_product",
    "zero_band",
}
_ALLOWED_EDGE_LABELS: Final[set[str]] = {
    "geometric_length",
    "temporal_delay",
    "flux_coupling",
}
_ALLOWED_GROWTH_FRONT_CAPACITY_SOURCES: Final[set[str]] = {
    "closed_front_capacity",
    "preexisting_front",
    "pressure_boundary",
    "propagated_front_growth",
    "refinement_boundary_capacity",
    "spark_expansion_front",
    "spark_refinement_boundary_front",
    "spark_refinement_front",
}

_DEFAULT_EVOLUTION: Final[dict[str, Any]] = {
    # GRCV3 semantic metric/identity defaults.
    "alpha": 1.0,
    "beta": 1.0,
    "gamma": 1.0,
    "delta": 1.0,
    "kappa_c": 1.0,
    "eta": 1.0,
    "lambda_c": 1.0,
    "xi_c": 1.0,
    "zeta_c": 1.0,
    "eps_gradient": 1e-3,
    "eps_hessian": 1e-3,
    "eps_spark": 1e-3,
    "eps_column_h": 1e-3,
    "eps_column_h_crossing_zero": 0.0,
    "hessian_regularization": 1e-9,
    # GRC9 mechanical refinement/growth defaults.
    "tau_instability": 0.5,
    "D_eff_target": 30,
    "w_bond": 1.0,
    "lambda_birth": 0.0,
    "alpha_seed": 0.1,
    "rng_seed": 0,
    # GRCV3 temporal-label and choice/collapse defaults, adapted to port edges.
    "v0": 1.0,
    "rho": 1.0,
    "eps_tau": 1e-9,
    "compatibility_score_params": {
        "epsilon_choice": 1e-3,
        "epsilon_collapse": 1e-3,
    },
    "site_potential_selection": "quadratic",
    "site_potential_params": {"mu": 0.0, "scale": 1.0},
}
_DEFAULT_EVOLUTION_PROVENANCE: Final[dict[str, str]] = {
    "alpha": "GRCV3 metric law default",
    "beta": "GRCV3 metric law default",
    "gamma": "GRCV3 metric law default",
    "delta": "GRCV3 metric law default",
    "kappa_c": "GRCV3/GRC9 potential default",
    "eta": "GRCV3 transport default",
    "lambda_c": "GRCV3 tensor default",
    "xi_c": "GRCV3 tensor default",
    "zeta_c": "GRCV3 tensor default",
    "eps_gradient": "GRCV3 basin/spark semantic threshold",
    "eps_hessian": "GRCV3 basin/spark semantic threshold",
    "eps_spark": "GRCV3 signed-Hessian spark threshold",
    "eps_column_h": "GRC9 column-H proxy threshold for opt-in GRC9V3 Lane B",
    "eps_column_h_crossing_zero": (
        "GRC9V3 Lane B optional column-H sign-crossing zero band"
    ),
    "hessian_regularization": "GRCV3 weighted least-squares comparison backend",
    "tau_instability": "GRC9 instability diagnostic threshold",
    "D_eff_target": "GRC9 mechanical expansion default",
    "w_bond": "GRC9 expansion/growth bond default",
    "lambda_birth": "GRC9 growth default",
    "alpha_seed": "GRC9 growth seed-transfer default",
    "rng_seed": "GRC9 deterministic RNG default",
    "v0": "GRCV3 temporal-label default",
    "rho": "GRCV3 temporal-label default",
    "eps_tau": "GRCV3 temporal-label default",
    "compatibility_score_params": "GRCV3 choice/collapse defaults",
    "site_potential_selection": "GRCV3/GRC9 potential default",
    "site_potential_params": "GRCV3/GRC9 potential default",
}

_DEFAULT_MODES: Final[dict[str, Any]] = {
    "frame_mode": "fixed_port_chart",
    "boundary_mode": "prune",
    "expansion_distribution_mode": "equal",
    "edge_label_selection": "all",
    "curvature_backend": "none",
    "hessian_backend": "row_basis_diagonal",
    "choice_backend": "sink_compatibility",
    "quadrature_mode": "unit_measure",
    "budget_correction_method": "simplex_projection",
    "spark_lane": "current_hybrid_signed_hessian",
    "spark_signed_crossing": False,
    "enable_column_h_threshold": True,
    "enable_column_h_sign_crossing": False,
    "column_h_sign_crossing_mode": "theory_product",
    "store_previous_column_h": False,
    "require_sink_for_column_h_spark": True,
    "require_active_degree_9": True,
    "enable_near_saturation": False,
    "near_saturation_degree": 8,
}

_DEFAULT_EDGE_LABEL_COMPUTATION_MODE: Final[dict[str, str]] = {
    "geometric_length": "fixed_port_chart",
    "temporal_delay": "transport_ratio",
    "flux_coupling": "absolute_flux",
}
_STEP_ORDER: Final[tuple[str, ...]] = (
    "compute_row_basis_gradient_pre_flux",
    "compute_signed_hessian_row_basis_pre_flux",
    "compute_net_flux_summary_pre_flux",
    "compute_node_tensors",
    "compute_base_conductance",
    "compute_edge_labels_pre_flux",
    "compute_potential",
    "compute_flux",
    "compute_edge_labels_post_flux",
    "refresh_differential_summary_post_flux",
    "detect_flux_topology_identities",
    "validate_geometric_basin_seeds",
    "compute_effective_basin_masses",
    "detect_hybrid_spark_candidates",
    "apply_mechanical_expansion",
    "refresh_after_expansion",
    "evaluate_child_basin_stabilization",
    "register_completed_hybrid_sparks",
    "update_hierarchy",
    "update_choice_collapse_learning",
    "apply_growth",
    "apply_boundary_behavior",
    "apply_continuity",
    "enforce_quadrature_budget",
    "refresh_runtime_state_final",
    "refresh_or_invalidate_coarse_cache",
    "compute_observables",
)


def _merge_nested(defaults: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(defaults))
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_nested(merged[key], value)
        else:
            merged[key] = value
    return merged


def _validate_edge_label_selection(selection: Any) -> None:
    if selection == "all":
        return
    if isinstance(selection, str) or not isinstance(selection, (list, tuple, set, frozenset)):
        raise InvalidParamsError(
            "edge_label_selection must be 'all' or an iterable of label names"
        )
    unknown = set(str(label) for label in selection) - _ALLOWED_EDGE_LABELS
    if unknown:
        raise InvalidParamsError(
            f"edge_label_selection contains unknown labels: {sorted(unknown)}"
        )


def _resolve_backend_selection_payload(modes: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "geometry": {"name": "fixed_port_chart", "params": {}},
        "hessian": {"name": str(modes["hessian_backend"]), "params": {}},
        "curvature": {"name": str(modes["curvature_backend"]), "params": {}},
        "spark": {
            "name": "saturation_signed_hessian",
            "params": {
                "spark_lane": str(modes["spark_lane"]),
                "signed_crossing": bool(modes["spark_signed_crossing"]),
                "enable_column_h_threshold": bool(modes["enable_column_h_threshold"]),
                "enable_column_h_sign_crossing": bool(
                    modes["enable_column_h_sign_crossing"]
                ),
                "column_h_sign_crossing_mode": str(
                    modes["column_h_sign_crossing_mode"]
                ),
            },
        },
        "choice": {"name": str(modes["choice_backend"]), "params": {}},
        "budget": {
            "name": str(modes["budget_correction_method"]),
            "params": {"quadrature_mode": str(modes["quadrature_mode"])},
        },
    }


def _build_params(config: Mapping[str, Any]) -> GRCParams:
    params_input = dict(config.get("params", config))
    evolution = _merge_nested(
        _DEFAULT_EVOLUTION,
        dict(params_input.get("evolution", {})),
    )
    modes = _merge_nested(
        _DEFAULT_MODES,
        dict(params_input.get("constitutive_semantic_modes", {})),
    )

    if modes["frame_mode"] not in _ALLOWED_FRAME_MODES:
        raise InvalidParamsError("frame_mode must be 'fixed_port_chart'")
    if modes["boundary_mode"] not in _ALLOWED_BOUNDARY_MODES:
        raise InvalidParamsError("boundary_mode must be one of prune, barrier, ghost")
    if modes["boundary_mode"] != "prune":
        raise InvalidParamsError(
            "Phase 7 Iteration 1 only implements boundary_mode='prune'; "
            "barrier/ghost require boundary_barrier runtime support"
        )
    if modes["expansion_distribution_mode"] not in _ALLOWED_EXPANSION_DISTRIBUTION_MODES:
        raise InvalidParamsError("expansion_distribution_mode must be one of equal, custom")
    if modes["curvature_backend"] not in _ALLOWED_CURVATURE_BACKENDS:
        raise InvalidParamsError("curvature_backend must be one of none, forman, ollivier")
    if modes["hessian_backend"] not in _ALLOWED_HESSIAN_BACKENDS:
        raise InvalidParamsError(
            "hessian_backend must be one of row_basis_diagonal, weighted_least_squares"
        )
    if modes["budget_correction_method"] not in _ALLOWED_BUDGET_CORRECTION_METHODS:
        raise InvalidParamsError(
            "budget_correction_method must be one of uniform_shift, simplex_projection"
        )
    if modes["choice_backend"] not in _ALLOWED_CHOICE_BACKENDS:
        raise InvalidParamsError("choice_backend must be one of disabled, sink_compatibility")
    if modes["quadrature_mode"] not in _ALLOWED_QUADRATURE_MODES:
        raise InvalidParamsError("quadrature_mode must be unit_measure")
    if modes["spark_lane"] not in _ALLOWED_SPARK_LANES:
        raise InvalidParamsError(
            "spark_lane must be one of current_hybrid_signed_hessian, "
            "grc9v3_column_h_assisted"
        )
    if not isinstance(modes["spark_signed_crossing"], bool):
        raise InvalidParamsError("spark_signed_crossing must be a boolean")
    for key in (
        "enable_column_h_threshold",
        "enable_column_h_sign_crossing",
        "store_previous_column_h",
        "require_sink_for_column_h_spark",
        "require_active_degree_9",
        "enable_near_saturation",
    ):
        if not isinstance(modes[key], bool):
            raise InvalidParamsError(f"{key} must be a boolean")
    if modes["column_h_sign_crossing_mode"] not in _ALLOWED_COLUMN_H_SIGN_CROSSING_MODES:
        raise InvalidParamsError(
            "column_h_sign_crossing_mode must be one of theory_product, zero_band"
        )
    if (
        isinstance(modes["near_saturation_degree"], bool)
        or not isinstance(modes["near_saturation_degree"], int)
    ):
        raise InvalidParamsError("near_saturation_degree must be an integer")
    if int(modes["near_saturation_degree"]) < 0:
        raise InvalidParamsError("near_saturation_degree must be >= 0")
    if modes["enable_near_saturation"]:
        raise InvalidParamsError("enable_near_saturation=true is not supported in Lane B v1")
    if not modes["require_active_degree_9"]:
        raise InvalidParamsError("require_active_degree_9=false is not supported in Lane B v1")
    if not modes["require_sink_for_column_h_spark"]:
        raise InvalidParamsError(
            "require_sink_for_column_h_spark=false is not supported in Lane B v1"
        )
    if modes["enable_column_h_sign_crossing"] and not modes["store_previous_column_h"]:
        raise InvalidParamsError(
            "enable_column_h_sign_crossing requires store_previous_column_h=true"
        )
    if (
        modes["spark_lane"] == "grc9v3_column_h_assisted"
        and not modes["enable_column_h_threshold"]
        and not modes["enable_column_h_sign_crossing"]
    ):
        raise InvalidParamsError(
            "grc9v3_column_h_assisted requires at least one column-H branch"
        )
    _validate_edge_label_selection(modes["edge_label_selection"])
    if (
        isinstance(evolution.get("rng_seed"), bool)
        or not isinstance(evolution.get("rng_seed"), int)
    ):
        raise InvalidParamsError("rng_seed must be an integer")
    if str(evolution.get("site_potential_selection", "")) != "quadratic":
        raise InvalidParamsError("site_potential_selection must be quadratic")
    if not isinstance(evolution.get("site_potential_params"), Mapping):
        raise InvalidParamsError("site_potential_params must be a mapping")
    if float(evolution.get("eps_tau", 0.0)) <= 0.0:
        raise InvalidParamsError("eps_tau must be > 0")
    if float(evolution.get("eps_spark", 0.0)) < 0.0:
        raise InvalidParamsError("eps_spark must be >= 0")
    try:
        eps_column_h = float(evolution["eps_column_h"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidParamsError("eps_column_h must be a finite number") from exc
    if not math.isfinite(eps_column_h):
        raise InvalidParamsError("eps_column_h must be finite")
    if eps_column_h < 0.0:
        raise InvalidParamsError("eps_column_h must be >= 0")
    try:
        eps_column_h_crossing_zero = float(evolution["eps_column_h_crossing_zero"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidParamsError("eps_column_h_crossing_zero must be a finite number") from exc
    if not math.isfinite(eps_column_h_crossing_zero):
        raise InvalidParamsError("eps_column_h_crossing_zero must be finite")
    if eps_column_h_crossing_zero < 0.0:
        raise InvalidParamsError("eps_column_h_crossing_zero must be >= 0")
    for key in (
        "alpha",
        "beta",
        "gamma",
        "delta",
        "kappa_c",
        "eta",
        "lambda_c",
        "xi_c",
        "zeta_c",
        "eps_gradient",
        "eps_hessian",
        "D_eff_target",
        "w_bond",
        "alpha_seed",
    ):
        if float(evolution.get(key, 0.0)) <= 0.0:
            raise InvalidParamsError(f"{key} must be > 0")
    for key in ("tau_instability", "lambda_birth", "v0", "rho"):
        if float(evolution.get(key, 0.0)) < 0.0:
            raise InvalidParamsError(f"{key} must be >= 0")
    if float(evolution.get("alpha_seed", 0.0)) > 1.0:
        raise InvalidParamsError("alpha_seed must be <= 1")
    compatibility_score_params = evolution.get("compatibility_score_params")
    if not isinstance(compatibility_score_params, Mapping):
        raise InvalidParamsError("compatibility_score_params must be a mapping")

    modes[BACKEND_SELECTIONS_KEY] = _resolve_backend_selection_payload(modes)
    modes["default_evolution_provenance"] = dict(_DEFAULT_EVOLUTION_PROVENANCE)

    try:
        return GRCParams.from_mapping(
            {
                "dt": params_input.get("dt", config.get("dt", 0.0)),
                "evolution": evolution,
                "constitutive_semantic_modes": modes,
                "numerical_backend": dict(params_input.get("numerical_backend", {})),
            }
        )
    except ValueError as exc:
        raise InvalidParamsError(str(exc)) from exc


def _coerce_plain_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return value


def _restore_numeric_mapping(value: Any, *, context: str) -> dict[int, float]:
    mapping = _coerce_plain_mapping(value, context=context)
    return {int(key): float(inner) for key, inner in mapping.items()}


def _restore_basin_mapping(value: Any, *, context: str) -> dict[int, set[int]]:
    mapping = _coerce_plain_mapping(value, context=context)
    basins: dict[int, set[int]] = {}
    for sink_id, members in mapping.items():
        if not isinstance(members, (list, tuple, set, frozenset)):
            raise SnapshotCompatibilityError(f"{context}[{sink_id!r}] must be list-like")
        basins[int(sink_id)] = {int(member) for member in members}
    return basins


def _restore_event_log(value: Any) -> list[GRCEvent]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SnapshotCompatibilityError("GRC9V3 state.event_log must be a list")
    restored: list[GRCEvent] = []
    for index, event in enumerate(value):
        if isinstance(event, GRCEvent):
            restored.append(event)
            continue
        if not isinstance(event, Mapping):
            raise SnapshotCompatibilityError(
                f"GRC9V3 state.event_log[{index}] must be a mapping"
            )
        payload = event.get("payload", {})
        if not isinstance(payload, Mapping):
            raise SnapshotCompatibilityError(
                f"GRC9V3 state.event_log[{index}].payload must be a mapping"
            )
        restored.append(
            GRCEvent(
                kind=str(event.get("kind", "")),
                step_index=int(event.get("step_index", 0)),
                payload=dict(payload),
                source_family=(
                    None
                    if event.get("source_family") is None
                    else str(event.get("source_family"))
                ),
            )
        )
    return restored


def _restore_rng_state(value: Any) -> Any:
    if (
        isinstance(value, tuple)
        and len(value) == 3
        and isinstance(value[0], int)
        and not isinstance(value[0], bool)
    ):
        return value
    return deserialize_rng_state(value)


def _default_rng_state(seed: int = 0) -> Any:
    return random.Random(seed).getstate()


def _restore_node_state(raw_value: Any, *, context: str) -> GRC9V3NodeState:
    if isinstance(raw_value, GRC9V3NodeState):
        return deepcopy(raw_value)
    if not isinstance(raw_value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return GRC9V3NodeState(
        coherence=float(raw_value.get("coherence", 0.0)),
        gradient_row_basis=[float(value) for value in raw_value.get("gradient_row_basis", [])],
        signed_hessian_row_basis=[
            float(value) for value in raw_value.get("signed_hessian_row_basis", [])
        ],
        net_flux_summary=[float(value) for value in raw_value.get("net_flux_summary", [])],
        basin_mass=float(raw_value.get("basin_mass", 0.0)),
        basin_id=raw_value.get("basin_id", 0),
        parent_id=raw_value.get("parent_id"),
        depth=int(raw_value.get("depth", 0)),
    )


def _serialize_node_state(node_state: GRC9V3NodeState) -> dict[str, Any]:
    return {
        "coherence": node_state.coherence,
        "gradient_row_basis": list(node_state.gradient_row_basis),
        "signed_hessian_row_basis": list(node_state.signed_hessian_row_basis),
        "net_flux_summary": list(node_state.net_flux_summary),
        "basin_mass": node_state.basin_mass,
        "basin_id": node_state.basin_id,
        "parent_id": node_state.parent_id,
        "depth": node_state.depth,
    }


def _restore_port_edge(raw_value: Any, *, context: str) -> PortEdge:
    if isinstance(raw_value, PortEdge):
        return raw_value
    if not isinstance(raw_value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return PortEdge(
        node_u=int(raw_value.get("node_u", 0)),
        port_u=int(raw_value.get("port_u", 0)),
        node_v=int(raw_value.get("node_v", 0)),
        port_v=int(raw_value.get("port_v", 0)),
        conductance=float(raw_value.get("conductance", 0.0)),
        flux_uv=float(raw_value.get("flux_uv", 0.0)),
    )


def _serialize_port_edge(port_edge: PortEdge) -> dict[str, Any]:
    return {
        "node_u": port_edge.node_u,
        "port_u": port_edge.port_u,
        "node_v": port_edge.node_v,
        "port_v": port_edge.port_v,
        "conductance": port_edge.conductance,
        "flux_uv": port_edge.flux_uv,
    }


def _restore_expansion_schedule(
    raw_value: Any,
    *,
    context: str,
) -> AdiabaticExpansionSchedule | None:
    if raw_value is None:
        return None
    if isinstance(raw_value, AdiabaticExpansionSchedule):
        return raw_value
    if not isinstance(raw_value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping or null")
    return AdiabaticExpansionSchedule(
        total_substeps=int(raw_value.get("total_substeps", 0)),
        completed_substeps=int(raw_value.get("completed_substeps", 0)),
        active=bool(raw_value.get("active", True)),
    )


def _restore_expansion_record(raw_value: Any, *, context: str) -> ExpansionRecord:
    if isinstance(raw_value, ExpansionRecord):
        return raw_value
    if not isinstance(raw_value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return ExpansionRecord(
        parent_sink_id=int(raw_value.get("parent_sink_id", 0)),
        module_node_ids=tuple(int(value) for value in raw_value.get("module_node_ids", [])),
        expansion_step=int(raw_value.get("expansion_step", 0)),
        distribution_weights=tuple(
            float(value) for value in raw_value.get("distribution_weights", [])
        ),
        schedule=_restore_expansion_schedule(
            raw_value.get("schedule"),
            context=f"{context}.schedule",
        ),
    )


def _serialize_expansion_record(record: ExpansionRecord) -> dict[str, Any]:
    schedule = None
    if record.schedule is not None:
        schedule = {
            "total_substeps": record.schedule.total_substeps,
            "completed_substeps": record.schedule.completed_substeps,
            "active": record.schedule.active,
        }
    return {
        "parent_sink_id": record.parent_sink_id,
        "module_node_ids": list(record.module_node_ids),
        "expansion_step": record.expansion_step,
        "distribution_weights": list(record.distribution_weights),
        "schedule": schedule,
    }


def _canonical_port_edge(
    endpoint_a: tuple[int, int],
    endpoint_b: tuple[int, int],
    *,
    conductance: float,
    flux_uv: float,
) -> PortEdge:
    port_a = slot_to_port_id(endpoint_a[1])
    port_b = slot_to_port_id(endpoint_b[1])
    if (endpoint_a[0], port_a) <= (endpoint_b[0], port_b):
        return PortEdge(
            node_u=endpoint_a[0],
            port_u=port_a,
            node_v=endpoint_b[0],
            port_v=port_b,
            conductance=conductance,
            flux_uv=flux_uv,
        )
    return PortEdge(
        node_u=endpoint_b[0],
        port_u=port_b,
        node_v=endpoint_a[0],
        port_v=port_a,
        conductance=conductance,
        flux_uv=-flux_uv,
    )


def _hydrate_port_edges_from_topology(
    topology: Any,
    *,
    port_edges: Mapping[int, PortEdge],
) -> dict[int, PortEdge]:
    hydrated: dict[int, PortEdge] = {}
    for edge_id in sorted(topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = topology.edge_ports(edge_id)
        existing = port_edges.get(edge_id)
        conductance = 1.0 if existing is None else float(existing.conductance)
        flux_uv = 0.0 if existing is None else float(existing.flux_uv)
        hydrated[edge_id] = _canonical_port_edge(
            endpoint_a,
            endpoint_b,
            conductance=conductance,
            flux_uv=flux_uv,
        )
    return hydrated


def _state_from_inputs(
    *,
    params: GRCParams,
    state_mapping: Mapping[str, Any] | None = None,
    topology: Any | None = None,
) -> GRC9V3State:
    mapping = {} if state_mapping is None else dict(state_mapping)

    topology_payload = topology
    if topology_payload is None:
        topology_input = mapping.get("topology")
        if topology_input is None:
            from pygrc.core import PortGraphBackend

            topology_payload = PortGraphBackend()
        elif hasattr(topology_input, "iter_live_node_ids") and hasattr(topology_input, "edge_ports"):
            topology_payload = deepcopy(topology_input)
        elif isinstance(topology_input, Mapping):
            topology_payload = restore_port_graph(
                topology_input,
                {
                    "next_node_id": mapping.get("next_node_id"),
                    "next_edge_id": mapping.get("next_edge_id"),
                },
            )
        else:
            raise SnapshotCompatibilityError(
                "GRC9V3 state topology must be a PortGraphBackend or topology mapping"
            )

    node_mapping = _coerce_plain_mapping(mapping.get("nodes", {}), context="GRC9V3 state.nodes")
    nodes = {
        int(node_id): _restore_node_state(
            raw_value,
            context=f"GRC9V3 state.nodes[{node_id!r}]",
        )
        for node_id, raw_value in node_mapping.items()
    }

    port_edges_mapping = _coerce_plain_mapping(
        mapping.get("port_edges", {}),
        context="GRC9V3 state.port_edges",
    )
    restored_port_edges = {
        int(edge_id): _restore_port_edge(
            raw_value,
            context=f"GRC9V3 state.port_edges[{edge_id!r}]",
        )
        for edge_id, raw_value in port_edges_mapping.items()
    }

    state = GRC9V3State(
        topology=topology_payload,
        nodes=nodes,
        port_edges=_hydrate_port_edges_from_topology(
            topology_payload,
            port_edges=restored_port_edges,
        ),
        base_conductance=_restore_numeric_mapping(
            mapping.get("base_conductance", {}),
            context="GRC9V3 state.base_conductance",
        ),
        geometric_length=_restore_numeric_mapping(
            mapping.get("geometric_length", {}),
            context="GRC9V3 state.geometric_length",
        ),
        temporal_delay=_restore_numeric_mapping(
            mapping.get("temporal_delay", {}),
            context="GRC9V3 state.temporal_delay",
        ),
        flux_coupling=_restore_numeric_mapping(
            mapping.get("flux_coupling", {}),
            context="GRC9V3 state.flux_coupling",
        ),
        potential=_restore_numeric_mapping(
            mapping.get("potential", {}),
            context="GRC9V3 state.potential",
        ),
        sink_set={int(node_id) for node_id in mapping.get("sink_set", [])},
        basins=_restore_basin_mapping(
            mapping.get("basins", {}),
            context="GRC9V3 state.basins",
        ),
        hierarchy=dict(
            _coerce_plain_mapping(mapping.get("hierarchy", {}), context="GRC9V3 state.hierarchy")
        ),
        expansion_registry={
            str(expansion_id): _restore_expansion_record(
                raw_value,
                context=f"GRC9V3 state.expansion_registry[{expansion_id!r}]",
            )
            for expansion_id, raw_value in _coerce_plain_mapping(
                mapping.get("expansion_registry", {}),
                context="GRC9V3 state.expansion_registry",
            ).items()
        },
        choice_registry=dict(
            _coerce_plain_mapping(
                mapping.get("choice_registry", {}),
                context="GRC9V3 state.choice_registry",
            )
        ),
        collapse_registry=dict(
            _coerce_plain_mapping(
                mapping.get("collapse_registry", {}),
                context="GRC9V3 state.collapse_registry",
            )
        ),
        coarse_cache=dict(
            _coerce_plain_mapping(mapping.get("coarse_cache", {}), context="GRC9V3 state.coarse_cache")
        ),
        edge_label_computation_mode=dict(
            mapping.get("edge_label_computation_mode", _DEFAULT_EDGE_LABEL_COMPUTATION_MODE)
        ),
        edge_label_params=dict(
            mapping.get(
                "edge_label_params",
                {
                    "selection": params.constitutive_semantic_modes["edge_label_selection"],
                    "hessian_backend": params.constitutive_semantic_modes["hessian_backend"],
                },
            )
        ),
        step_index=int(mapping.get("step_index", 0)),
        time=float(mapping.get("time", 0.0)),
        budget_target=float(mapping.get("budget_target", 0.0)),
        remainder=float(mapping.get("remainder", 0.0)),
        cached_quantities=dict(
            _coerce_plain_mapping(
                mapping.get("cached_quantities", {}),
                context="GRC9V3 state.cached_quantities",
            )
        ),
        event_log=_restore_event_log(mapping.get("event_log", [])),
        observables=dict(
            _coerce_plain_mapping(mapping.get("observables", {}), context="GRC9V3 state.observables")
        ),
        rng_state=_restore_rng_state(mapping.get("rng_state")),
        params_identity=(
            None
            if mapping.get("params_identity") is None
            else str(mapping.get("params_identity"))
        ),
    )
    if state.params_identity is None:
        state.params_identity = params.params_hash
    if state.rng_state is None:
        state.rng_state = _default_rng_state(int(params.evolution["rng_seed"]))
    if "budget_target" not in mapping:
        state.budget_target = float(
            sum(node_state.coherence for node_state in state.nodes.values())
        )
        state.cached_quantities["budget_target_source"] = "initial_state_sum"
    else:
        state.cached_quantities.setdefault("budget_target_source", "explicit_state")
    return state


def _stringify_mapping_keys(mapping: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in mapping.items()}


def _state_payload_from_state(state: GRC9V3State) -> dict[str, Any]:
    return {
        "nodes": {
            str(node_id): _serialize_node_state(node_state)
            for node_id, node_state in state.nodes.items()
        },
        "port_edges": {
            str(edge_id): _serialize_port_edge(port_edge)
            for edge_id, port_edge in state.port_edges.items()
        },
        "base_conductance": _stringify_mapping_keys(state.base_conductance),
        "geometric_length": _stringify_mapping_keys(state.geometric_length),
        "temporal_delay": _stringify_mapping_keys(state.temporal_delay),
        "flux_coupling": _stringify_mapping_keys(state.flux_coupling),
        "potential": _stringify_mapping_keys(state.potential),
        "sink_set": sorted(state.sink_set),
        "basins": {
            str(node_id): sorted(members) for node_id, members in state.basins.items()
        },
        "hierarchy": _stringify_mapping_keys(state.hierarchy),
        "expansion_registry": {
            str(expansion_id): _serialize_expansion_record(record)
            for expansion_id, record in sorted(state.expansion_registry.items())
        },
        "choice_registry": _stringify_mapping_keys(state.choice_registry),
        "collapse_registry": _stringify_mapping_keys(state.collapse_registry),
        "coarse_cache": _stringify_mapping_keys(state.coarse_cache),
        "edge_label_computation_mode": dict(state.edge_label_computation_mode),
        "edge_label_params": _stringify_mapping_keys(state.edge_label_params),
        "step_index": state.step_index,
        "time": state.time,
        "budget_target": state.budget_target,
        "remainder": state.remainder,
        "cached_quantities": _stringify_mapping_keys(state.cached_quantities),
        "event_log": [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in state.event_log
        ],
        "observables": _stringify_mapping_keys(state.observables),
        "rng_state": serialize_rng_state(state.rng_state),
        "params_identity": state.params_identity,
    }


class GRC9V3(GRCModel):
    """Phase 7 hybrid model shell for the GRC9V3 family."""

    MODEL_FAMILY = "GRC9V3"
    CAPABILITY_PROFILE = GRC9V3_CAPABILITY_PROFILE

    def __init__(self, params: GRCParams, state: GRC9V3State | None = None) -> None:
        self._params = params
        self._state = deepcopy(state) if state is not None else _state_from_inputs(params=params)
        self._validate_state(self._state)
        self._initial_state: GRC9V3State | None = deepcopy(self._state)
        self._reset_baseline_unavailable_reason: str | None = None

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "GRC9V3":
        params = _build_params(config)
        state_input = config.get("state", {})
        if not isinstance(state_input, Mapping):
            raise InvalidParamsError("state must be a mapping when provided")
        state = _state_from_inputs(params=params, state_mapping=state_input)
        return cls(params=params, state=state)

    @classmethod
    def from_state(
        cls,
        state: Mapping[str, Any] | GRC9V3State,
        params: Mapping[str, Any],
    ) -> "GRC9V3":
        resolved_params = _build_params(dict(params))
        if isinstance(state, GRC9V3State):
            return cls(params=resolved_params, state=deepcopy(state))
        resolved_state = _state_from_inputs(
            params=resolved_params,
            state_mapping=dict(state),
        )
        return cls(params=resolved_params, state=resolved_state)

    @classmethod
    def load(cls, path: str) -> "GRC9V3":
        snapshot = load_snapshot(path)
        return cls._from_snapshot(snapshot, restore_reset_baseline=True)

    @classmethod
    def _from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
        *,
        restore_reset_baseline: bool = False,
    ) -> "GRC9V3":
        """Restore a GRC9V3 model from an already-loaded snapshot payload."""

        require_snapshot_family(snapshot, expected_family=cls.MODEL_FAMILY)

        metadata = snapshot["metadata"]
        if not isinstance(metadata, Mapping):
            raise SnapshotCompatibilityError("snapshot metadata must be a mapping")
        params_payload = metadata.get("params")
        if not isinstance(params_payload, Mapping):
            raise SnapshotCompatibilityError("snapshot metadata.params must be a mapping")
        params = _build_params(dict(params_payload))

        topology_payload = snapshot.get("topology", {})
        if not isinstance(topology_payload, Mapping):
            raise SnapshotCompatibilityError("snapshot topology must be a mapping")
        topology = restore_port_graph(topology_payload, metadata)

        basin_group = snapshot.get("basin_attributes", {})
        edge_labels_group = snapshot.get("edge_labels", {})
        dynamics = snapshot.get("dynamics", {})
        caches = snapshot.get("caches", {})
        if basin_group is not None and not isinstance(basin_group, Mapping):
            raise SnapshotCompatibilityError("snapshot basin_attributes must be a mapping")
        if edge_labels_group is not None and not isinstance(edge_labels_group, Mapping):
            raise SnapshotCompatibilityError("snapshot edge_labels must be a mapping")
        if dynamics is not None and not isinstance(dynamics, Mapping):
            raise SnapshotCompatibilityError("snapshot dynamics must be a mapping")
        if caches is not None and not isinstance(caches, Mapping):
            raise SnapshotCompatibilityError("snapshot caches must be a mapping")

        state_mapping: dict[str, Any] = {}
        if isinstance(basin_group, Mapping):
            state_mapping["nodes"] = dict(
                _coerce_plain_mapping(
                    basin_group.get("nodes", {}),
                    context="snapshot basin_attributes.nodes",
                )
            )
            state_mapping["hierarchy"] = dict(
                _coerce_plain_mapping(
                    basin_group.get("hierarchy", {}),
                    context="snapshot basin_attributes.hierarchy",
                )
            )
            state_mapping["expansion_registry"] = dict(
                _coerce_plain_mapping(
                    basin_group.get("expansion_registry", {}),
                    context="snapshot basin_attributes.expansion_registry",
                )
            )
        if isinstance(edge_labels_group, Mapping):
            state_mapping.update(
                {
                    "base_conductance": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("base_conductance", {}),
                            context="snapshot edge_labels.base_conductance",
                        )
                    ),
                    "geometric_length": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("geometric_length", {}),
                            context="snapshot edge_labels.geometric_length",
                        )
                    ),
                    "temporal_delay": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("temporal_delay", {}),
                            context="snapshot edge_labels.temporal_delay",
                        )
                    ),
                    "flux_coupling": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("flux_coupling", {}),
                            context="snapshot edge_labels.flux_coupling",
                        )
                    ),
                    "edge_label_computation_mode": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("edge_label_computation_mode", {}),
                            context="snapshot edge_labels.edge_label_computation_mode",
                        )
                    ),
                    "edge_label_params": dict(
                        _coerce_plain_mapping(
                            edge_labels_group.get("edge_label_params", {}),
                            context="snapshot edge_labels.edge_label_params",
                        )
                    ),
                }
            )
        if isinstance(dynamics, Mapping):
            state_mapping.update(
                dict(
                    _coerce_plain_mapping(
                        dynamics.get("state", {}),
                        context="snapshot dynamics.state",
                    )
                )
            )
        if isinstance(caches, Mapping) and "coarse_cache" not in state_mapping:
            coarse_cache = caches.get("coarse_cache")
            if isinstance(coarse_cache, Mapping):
                state_mapping["coarse_cache"] = dict(coarse_cache)
        if "event_log" not in state_mapping and "events" in snapshot:
            event_payload = snapshot.get("events", [])
            if not isinstance(event_payload, list):
                raise SnapshotCompatibilityError("snapshot events must be a list")
            state_mapping["event_log"] = list(event_payload)
        if "observables" not in state_mapping and "observables" in snapshot:
            observables_payload = snapshot.get("observables", {})
            if not isinstance(observables_payload, Mapping):
                raise SnapshotCompatibilityError("snapshot observables must be a mapping")
            state_mapping["observables"] = dict(observables_payload)
        if "rng_state" not in state_mapping and "rng_state" in metadata:
            state_mapping["rng_state"] = metadata.get("rng_state")
        if "params_identity" not in state_mapping:
            state_mapping["params_identity"] = metadata.get("params_hash", params.params_hash)

        state = _state_from_inputs(
            params=params,
            state_mapping=state_mapping,
            topology=topology,
        )
        model = cls(params=params, state=state)
        if restore_reset_baseline:
            model._restore_reset_baseline(snapshot)
        return model

    def _restore_reset_baseline(self, snapshot: Mapping[str, Any]) -> None:
        baseline_snapshot = reset_baseline_snapshot(
            snapshot,
            expected_family=self.MODEL_FAMILY,
        )
        if baseline_snapshot is None:
            group = snapshot.get("reset_baseline")
            reason = "legacy_snapshot_missing_reset_baseline"
            if isinstance(group, Mapping):
                raw_reason = group.get("unavailable_reason")
                if isinstance(raw_reason, str) and raw_reason:
                    reason = raw_reason
            self._initial_state = None
            self._reset_baseline_unavailable_reason = reason
            return
        baseline_model = type(self)._from_snapshot(
            baseline_snapshot,
            restore_reset_baseline=False,
        )
        self._initial_state = deepcopy(baseline_model.get_state())
        self._reset_baseline_unavailable_reason = None

    def get_state(self) -> GRC9V3State:
        return self._state

    def set_state(self, state: GRC9V3State) -> None:
        if not isinstance(state, GRC9V3State):
            raise SnapshotCompatibilityError("state must be a GRC9V3State instance")
        self._validate_state(state)
        self._state = deepcopy(state)

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        claims = set(self.CAPABILITY_PROFILE.required)
        self.CAPABILITY_PROFILE.validate_claims(claims)
        return claims

    def compute_observables(self) -> ObservableMap:
        observables = dict(self._state.observables)
        observables.setdefault("node_count", float(len(tuple(self._state.topology.iter_live_node_ids()))))
        observables.setdefault("edge_count", float(len(tuple(self._state.topology.iter_live_edge_ids()))))
        observables.setdefault("active_basin_count", float(len(self._state.basins)))
        observables.setdefault(
            "max_hierarchy_depth",
            float(max((node.depth for node in self._state.nodes.values()), default=0)),
        )
        observables.setdefault("choice_regime_count", float(len(self._state.choice_registry)))
        observables.setdefault("collapse_event_count", float(len(self._state.collapse_registry)))
        return observables

    def rebuild_differential_state(self) -> None:
        """Materialize the Iteration 2 row-basis differential layer."""

        rebuild_grc9v3_differential_state(
            self._state,
            evolution=self._params.evolution,
            hessian_backend=str(self._params.constitutive_semantic_modes["hessian_backend"]),
        )
        self._validate_state(self._state)

    def rebuild_transport_state(self) -> None:
        """Materialize the Iteration 3 scalar transport and label layer."""

        rebuild_grc9v3_transport_state(
            self._state,
            evolution=self._params.evolution,
            modes=self._params.constitutive_semantic_modes,
        )
        self._invalidate_coarse_cache("transport_recomputation")
        self._validate_state(self._state)

    def rebuild_identity_state(self) -> None:
        """Materialize the Iteration 3 flux and geometric identity layers."""

        rebuild_grc9v3_identity_state(
            self._state,
            evolution=self._params.evolution,
        )
        self._validate_state(self._state)

    def detect_hybrid_spark_candidates(self) -> list[GRCEvent]:
        """Return Iteration 4 hybrid spark candidates without mutating topology."""

        return detect_hybrid_spark_candidates(
            self._state,
            evolution=self._params.evolution,
            modes=self._params.constitutive_semantic_modes,
            source_family=self.MODEL_FAMILY,
        )

    def apply_hybrid_sparks(self) -> list[GRCEvent]:
        """Run the Iteration 4 candidate-expansion-stabilization spark layer."""

        emitted_events = self._apply_hybrid_spark_stages()
        self._validate_state(self._state)
        return emitted_events

    def _apply_hybrid_spark_stages(self, trace: list[str] | None = None) -> list[GRCEvent]:
        """Run spark stages with optional canonical trace recording."""

        emitted_events: list[GRCEvent] = []
        candidates = self.detect_hybrid_spark_candidates()
        if trace is not None:
            trace.append("detect_hybrid_spark_candidates")
        for candidate_event in candidates:
            if not self._state.topology.has_node(int(candidate_event.payload["sink_node_id"])):
                continue
            self._state.event_log.append(candidate_event)
            emitted_events.append(candidate_event)

            expansion_event = apply_mechanical_expansion(
                self._state,
                candidate_event,
                evolution=self._params.evolution,
                modes=self._params.constitutive_semantic_modes,
                source_family=self.MODEL_FAMILY,
            )
            self._state.event_log.append(expansion_event)
            emitted_events.append(expansion_event)
            self.enforce_quadrature_budget()
            self._state.cached_quantities["post_expansion_budget_check"] = dict(
                self._state.cached_quantities.get("last_quadrature_budget", {})
            )

            self.rebuild_differential_state()
            self.rebuild_transport_state()
            self.rebuild_identity_state()
            stabilization_evidence = evaluate_child_basin_stabilization(
                self._state,
                expansion_event,
            )
            completed_event = register_completed_hybrid_spark(
                self._state,
                candidate_event,
                expansion_event,
                stabilization_evidence,
                source_family=self.MODEL_FAMILY,
            )
            if completed_event is not None:
                self._state.event_log.append(completed_event)
                emitted_events.append(completed_event)

        if trace is not None:
            trace.extend(
                (
                    "apply_mechanical_expansion",
                    "refresh_after_expansion",
                    "evaluate_child_basin_stabilization",
                    "register_completed_hybrid_sparks",
                    "update_hierarchy",
                )
            )
        return emitted_events

    def rebuild_choice_state(self) -> list[GRCEvent]:
        """Materialize Iteration 5 choice, collapse, and learning semantics."""

        emitted_events = rebuild_grc9v3_choice_state(
            self._state,
            evolution=self._params.evolution,
            modes=self._params.constitutive_semantic_modes,
            source_family=self.MODEL_FAMILY,
        )
        self._state.event_log.extend(emitted_events)
        self._validate_state(self._state)
        return emitted_events

    def apply_boundary_behavior(self) -> None:
        """Apply the configured Iteration 5 boundary behavior."""

        apply_grc9v3_boundary_behavior(
            self._state,
            modes=self._params.constitutive_semantic_modes,
        )
        self._validate_state(self._state)

    def enforce_quadrature_budget(self) -> dict[str, Any]:
        """Enforce the Iteration 5 quadrature budget invariant."""

        summary = enforce_grc9v3_quadrature_budget(
            self._state,
            modes=self._params.constitutive_semantic_modes,
        )
        self._validate_state(self._state)
        return summary

    def refresh_coarse_cache(self) -> None:
        """Invalidate coarse state after topology or value changes."""

        refresh_grc9v3_coarse_cache(self._state)
        self._validate_state(self._state)

    def coarse_grain_columns(self, field_name: str) -> dict[str, Any]:
        """Return the exact GRC9 column coarse state for a GRC9V3 port field."""

        normalized_field_name = str(field_name)
        if normalized_field_name == "signed_flux":
            coarse_state = coarse_grain_signed_flux_field(
                self._build_signed_flux_port_field()
            )
            coarse_state["field_name"] = normalized_field_name
            self._state.coarse_cache[f"signed_flux_split:{normalized_field_name}"] = deepcopy(
                coarse_state
            )
            self._state.cached_quantities["coarse_cache_refresh_mode"] = "operator_backed"
            self._state.cached_quantities["coarse_cache_invalidated"] = False
            self._state.cached_quantities["coarse_cache_invalidation_reason"] = "none"
            return coarse_state

        coarse_state = coarse_grain_nonnegative_port_field(
            self._build_nonnegative_port_field(field_name=normalized_field_name)
        )
        coarse_state["field_name"] = normalized_field_name
        self._state.coarse_cache[f"exact_column_profile:{normalized_field_name}"] = deepcopy(
            coarse_state
        )
        self._state.cached_quantities["coarse_cache_refresh_mode"] = "operator_backed"
        self._state.cached_quantities["coarse_cache_invalidated"] = False
        self._state.cached_quantities["coarse_cache_invalidation_reason"] = "none"
        return coarse_state

    def split_columns(self, coarse_state: Mapping[str, Any]) -> dict[str, Any]:
        """Return an exact fine GRC9V3 port field from a column coarse state."""

        mode = str(coarse_state.get("mode", ""))
        field_name = str(coarse_state.get("field_name", ""))
        if mode == "signed_flux_split":
            return {
                "field_name": field_name,
                "mode": mode,
                "port_field": split_signed_flux_field(coarse_state),
            }
        if mode == "exact_column_profile":
            return {
                "field_name": field_name,
                "mode": mode,
                "port_field": split_nonnegative_port_field(coarse_state),
            }
        raise InvalidStateTransitionError(
            f"unsupported coarse_state mode {mode!r} for split_columns"
        )

    def apply_semantic_maintenance(self) -> list[GRCEvent]:
        """Run Iteration 5 semantic maintenance stages in baseline order."""

        events = self.rebuild_choice_state()
        events.extend(self.apply_growth())
        self.apply_boundary_behavior()
        self.enforce_quadrature_budget()
        self.refresh_coarse_cache()
        return events

    def apply_growth(self) -> list[GRCEvent]:
        """Apply baseline inactive-port growth from outward flux pressure."""

        lambda_birth = float(self._params.evolution.get("lambda_birth", 0.0))
        alpha_seed = float(self._params.evolution.get("alpha_seed", 0.1))
        w_bond = float(self._params.evolution.get("w_bond", 1.0))
        self._state.cached_quantities["birth_rule_mode"] = "outward_flux_pressure"
        self._state.cached_quantities["birth_parent_selection_mode"] = (
            "deterministic_scan_with_rng_acceptance"
        )
        parent_eligibility_mode = str(
            self._params.constitutive_semantic_modes.get(
                "growth_parent_eligibility",
                "legacy_any_inactive_port",
            )
        )
        if parent_eligibility_mode not in {
            "legacy_any_inactive_port",
            "grcl9v3_front_capacity",
        }:
            raise InvalidParamsError(
                "growth_parent_eligibility must be legacy_any_inactive_port "
                "or grcl9v3_front_capacity"
            )
        self._state.cached_quantities["birth_parent_eligibility_mode"] = (
            parent_eligibility_mode
        )
        if lambda_birth <= 0.0:
            self._state.cached_quantities["last_growth_events"] = []
            return []

        rng = random.Random()
        rng.setstate(self._state.rng_state)
        selected_parents: list[tuple[int, int, float, float, float]] = []
        front_eligible_ports = self._growth_front_eligible_ports()
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            inactive_ports = self._inactive_port_ids(node_id)
            if parent_eligibility_mode == "grcl9v3_front_capacity":
                eligible_ports = front_eligible_ports.get(node_id, ())
                inactive_ports = [
                    port_id for port_id in inactive_ports if port_id in set(eligible_ports)
                ]
            if not inactive_ports:
                continue
            outward_flux = self._outward_flux_pressure(node_id)
            if outward_flux <= 0.0:
                continue
            birth_probability = 1.0 - math.exp(-lambda_birth * outward_flux)
            rng_sample = rng.random()
            if rng_sample < birth_probability:
                selected_parents.append(
                    (
                        node_id,
                        inactive_ports[0],
                        outward_flux,
                        birth_probability,
                        rng_sample,
                    )
                )

        growth_events: list[GRCEvent] = []
        for node_id, parent_port_id, outward_flux, birth_probability, rng_sample in selected_parents:
            if not self._state.topology.has_node(node_id):
                continue
            if self._state.topology.port_is_occupied(node_id, port_id_to_slot(parent_port_id)):
                continue
            parent_state = self._state.nodes.get(node_id)
            if parent_state is None:
                continue
            child_node_id = self._state.topology.add_node(
                {"role": "hybrid_growth_child", "parent_node_id": node_id}
            )
            edge_id = self._state.topology.connect_ports(
                node_id,
                port_id_to_slot(parent_port_id),
                child_node_id,
                port_id_to_slot(1),
                payload={"kind": "hybrid_growth", "parent_node_id": node_id},
            )
            self._state.port_edges[edge_id] = PortEdge(
                node_u=node_id,
                port_u=parent_port_id,
                node_v=child_node_id,
                port_v=1,
                conductance=w_bond,
                flux_uv=0.0,
            )
            transfer = max(0.0, min(parent_state.coherence, alpha_seed * parent_state.coherence))
            self._state.nodes[node_id] = GRC9V3NodeState(
                coherence=parent_state.coherence - transfer,
                gradient_row_basis=list(parent_state.gradient_row_basis),
                signed_hessian_row_basis=list(parent_state.signed_hessian_row_basis),
                net_flux_summary=list(parent_state.net_flux_summary),
                basin_mass=parent_state.basin_mass,
                basin_id=parent_state.basin_id,
                parent_id=parent_state.parent_id,
                depth=parent_state.depth,
            )
            self._state.nodes[child_node_id] = GRC9V3NodeState(
                coherence=transfer,
                basin_mass=transfer,
                basin_id=child_node_id,
                parent_id=parent_state.basin_id,
                depth=parent_state.depth + 1,
            )
            self._state.potential[child_node_id] = 0.0
            event = GRCEvent(
                kind="growth",
                step_index=self._state.step_index,
                payload={
                    "parent_node_id": node_id,
                    "child_node_id": child_node_id,
                    "parent_port_id": parent_port_id,
                    "child_port_id": 1,
                    "outward_flux_pressure": outward_flux,
                    "birth_probability": birth_probability,
                    "rng_sample": rng_sample,
                    "coherence_transfer": transfer,
                    "growth_parent_eligibility_mode": parent_eligibility_mode,
                    "growth_parent_capacity_source": (
                        self._growth_capacity_source(node_id, parent_port_id)
                    ),
                },
                source_family=self.MODEL_FAMILY,
            )
            growth_events.append(event)
            self._propagate_grcl9v3_front_capacity(
                parent_node_id=node_id,
                parent_port_id=parent_port_id,
                child_node_id=child_node_id,
            )

        self._state.rng_state = rng.getstate()
        if growth_events:
            self._state.event_log.extend(growth_events)
            self._invalidate_coarse_cache("growth_topology_change")
        self._state.cached_quantities["last_growth_events"] = [
            dict(event.payload) for event in growth_events
        ]
        self._validate_state(self._state)
        return growth_events

    def _propagate_grcl9v3_front_capacity(
        self,
        *,
        parent_node_id: int,
        parent_port_id: int,
        child_node_id: int,
    ) -> None:
        """Expose a bounded GRCL-9V3 front on a newly grown child when declared."""

        raw_sources = self._state.cached_quantities.get(
            "grcl9v3_growth_parent_capacity_sources", {}
        )
        if not isinstance(raw_sources, Mapping):
            return
        source_record = raw_sources.get(str(parent_node_id)) or raw_sources.get(
            parent_node_id
        )
        if not isinstance(source_record, Mapping):
            return
        record_port = source_record.get("inactive_parent_port")
        if isinstance(record_port, int) and record_port != parent_port_id:
            return
        if not bool(source_record.get("propagate_child_front", False)):
            return
        parent_depth = int(source_record.get("front_generation_depth", 0))
        max_depth = int(source_record.get("child_front_max_depth", 0))
        if parent_depth >= max_depth:
            return
        child_front_port = int(source_record.get("child_front_port", 2))
        if not 1 <= child_front_port <= 9:
            return
        if self._state.topology.port_is_occupied(
            child_node_id,
            port_id_to_slot(child_front_port),
        ):
            return

        raw_eligible = self._state.cached_quantities.setdefault(
            "grcl9v3_front_growth_eligible_ports", {}
        )
        if not isinstance(raw_eligible, dict):
            return
        raw_eligible[str(child_node_id)] = [child_front_port]

        raw_sources[str(child_node_id)] = {
            "construct_id": source_record.get("construct_id"),
            "growth_semantics": "front_capacity",
            "front_capacity_source": "propagated_front_growth",
            "front_source_construct_id": source_record.get("front_source_construct_id"),
            "inactive_parent_port": child_front_port,
            "propagate_child_front": bool(source_record.get("propagate_child_front")),
            "child_front_port": child_front_port,
            "child_front_max_depth": max_depth,
            "child_front_activation_delay_steps": int(
                source_record.get("child_front_activation_delay_steps", 0)
            ),
            "child_front_outlet": bool(source_record.get("child_front_outlet", False)),
            "child_front_outlet_port": int(
                source_record.get("child_front_outlet_port", 3)
            ),
            "child_front_outlet_conductance": float(
                source_record.get("child_front_outlet_conductance", 0.25)
            ),
            "child_front_outlet_coherence": float(
                source_record.get("child_front_outlet_coherence", 0.0)
            ),
            "front_activation_step_index": self._state.step_index
            + int(source_record.get("child_front_activation_delay_steps", 0)),
            "front_generation_depth": parent_depth + 1,
            "parent_front_node_id": parent_node_id,
        }
        self._add_grcl9v3_propagated_front_outlet(
            source_record=source_record,
            child_node_id=child_node_id,
        )

    def _add_grcl9v3_propagated_front_outlet(
        self,
        *,
        source_record: Mapping[str, Any],
        child_node_id: int,
    ) -> None:
        if not bool(source_record.get("child_front_outlet", False)):
            return
        outlet_port = int(source_record.get("child_front_outlet_port", 3))
        if not 1 <= outlet_port <= 9:
            return
        if self._state.topology.port_is_occupied(
            child_node_id,
            port_id_to_slot(outlet_port),
        ):
            return
        outlet_node_id = self._state.topology.add_node(
            {
                "role": "hybrid_growth_front_outlet",
                "parent_node_id": child_node_id,
            }
        )
        edge_id = self._state.topology.connect_ports(
            child_node_id,
            port_id_to_slot(outlet_port),
            outlet_node_id,
            port_id_to_slot(1),
            payload={
                "kind": "hybrid_growth_front_outlet",
                "parent_node_id": child_node_id,
            },
        )
        conductance = float(source_record.get("child_front_outlet_conductance", 0.25))
        self._state.port_edges[edge_id] = PortEdge(
            node_u=child_node_id,
            port_u=outlet_port,
            node_v=outlet_node_id,
            port_v=1,
            conductance=conductance,
            flux_uv=0.0,
        )
        coherence = float(source_record.get("child_front_outlet_coherence", 0.0))
        self._state.nodes[outlet_node_id] = GRC9V3NodeState(coherence=coherence)
        self._state.potential[outlet_node_id] = 0.0

    def _growth_front_eligible_ports(self) -> dict[int, tuple[int, ...]]:
        raw = self._state.cached_quantities.get("grcl9v3_front_growth_eligible_ports", {})
        if not isinstance(raw, Mapping):
            return {}
        result: dict[int, tuple[int, ...]] = {}
        for node_key, ports in raw.items():
            try:
                node_id = int(node_key)
            except (TypeError, ValueError):
                continue
            raw_sources = self._state.cached_quantities.get(
                "grcl9v3_growth_parent_capacity_sources", {}
            )
            source_record = (
                raw_sources.get(str(node_id)) or raw_sources.get(node_id)
                if isinstance(raw_sources, Mapping)
                else None
            )
            if isinstance(source_record, Mapping):
                activation_step = source_record.get("front_activation_step_index")
                if (
                    isinstance(activation_step, int)
                    and self._state.step_index < activation_step
                ):
                    continue
            if not isinstance(ports, Sequence) or isinstance(ports, str):
                continue
            clean_ports: list[int] = []
            for port in ports:
                if isinstance(port, bool) or not isinstance(port, int):
                    continue
                if 1 <= port <= 9:
                    clean_ports.append(port)
            if clean_ports:
                result[node_id] = tuple(sorted(set(clean_ports)))
        return result

    def _growth_capacity_source(self, node_id: int, port_id: int) -> str:
        raw = self._state.cached_quantities.get("grcl9v3_growth_parent_capacity_sources", {})
        if not isinstance(raw, Mapping):
            return "legacy_any_inactive_port"
        record = raw.get(str(node_id)) or raw.get(node_id)
        if not isinstance(record, Mapping):
            return "legacy_any_inactive_port"
        record_port = record.get("inactive_parent_port")
        if isinstance(record_port, int) and record_port != port_id:
            return "legacy_any_inactive_port"
        source = record.get("front_capacity_source")
        source_name = str(source) if source is not None else "unknown"
        if source_name not in _ALLOWED_GROWTH_FRONT_CAPACITY_SOURCES:
            return "unknown"
        return source_name

    def apply_continuity(self) -> None:
        """Apply one continuity update from current antisymmetric port flux."""

        dt = float(self._params.dt)
        coherence_deltas: dict[int, float] = {}
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            divergence = 0.0
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                if edge_id not in live_edge_ids:
                    raise SnapshotCompatibilityError(
                        "GRC9V3 continuity encountered a stale incident edge"
                    )
                port_edge = self._state.port_edges[edge_id]
                if port_edge.node_u == node_id:
                    divergence += float(port_edge.flux_uv)
                elif port_edge.node_v == node_id:
                    divergence -= float(port_edge.flux_uv)
            coherence_deltas[node_id] = -dt * divergence

        for node_id in sorted(coherence_deltas):
            node_state = self._state.nodes.get(node_id)
            if node_state is None:
                continue
            coherence = float(node_state.coherence + coherence_deltas[node_id])
            self._state.nodes[node_id] = GRC9V3NodeState(
                coherence=coherence,
                gradient_row_basis=list(node_state.gradient_row_basis),
                signed_hessian_row_basis=list(node_state.signed_hessian_row_basis),
                net_flux_summary=list(node_state.net_flux_summary),
                basin_mass=node_state.basin_mass,
                basin_id=node_state.basin_id,
                parent_id=node_state.parent_id,
                depth=node_state.depth,
            )
        self._state.cached_quantities["last_continuity_delta"] = {
            str(node_id): value for node_id, value in sorted(coherence_deltas.items())
        }
        self._state.cached_quantities["continuity_live_edge_ids"] = sorted(live_edge_ids)

    def _inactive_port_ids(self, node_id: int) -> tuple[int, ...]:
        return tuple(
            port_id
            for port_id in range(1, 10)
            if not self._state.topology.port_is_occupied(node_id, port_id_to_slot(port_id))
        )

    def _outward_flux_pressure(self, node_id: int) -> float:
        return float(
            sum(
                max(0.0, self._oriented_flux(edge_id=edge_id, node_id=node_id))
                for edge_id in self._state.topology.incident_edge_ids(node_id)
            )
        )

    def _build_nonnegative_port_field(self, *, field_name: str) -> dict[int, dict[int, float]]:
        if field_name not in {
            "conductance",
            "geometric_length",
            "temporal_delay",
            "flux_coupling",
            "abs_flux",
        }:
            raise InvalidStateTransitionError(
                f"unsupported nonnegative coarse-grain field {field_name!r}"
            )
        port_field: dict[int, dict[int, float]] = {}
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            node_ports: dict[int, float] = {port_id: 0.0 for port_id in range(1, 10)}
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                if edge_id not in live_edge_ids:
                    raise SnapshotCompatibilityError(
                        "GRC9V3 coarse-graining encountered a stale incident edge"
                    )
                port_id = self._local_port_id(edge_id=edge_id, node_id=node_id)
                if field_name == "conductance":
                    value = float(self._state.port_edges[edge_id].conductance)
                elif field_name == "geometric_length":
                    value = float(self._state.geometric_length.get(edge_id, 0.0))
                elif field_name == "temporal_delay":
                    value = float(self._state.temporal_delay.get(edge_id, 0.0))
                elif field_name == "flux_coupling":
                    value = float(self._state.flux_coupling.get(edge_id, 0.0))
                else:
                    value = abs(self._oriented_flux(edge_id=edge_id, node_id=node_id))
                if value < 0.0:
                    raise InvalidStateTransitionError(
                        f"coarse-grain field {field_name!r} must remain nonnegative"
                    )
                node_ports[port_id] = value
            port_field[node_id] = node_ports
        return port_field

    def _build_signed_flux_port_field(self) -> dict[int, dict[int, float]]:
        port_field: dict[int, dict[int, float]] = {}
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            node_ports: dict[int, float] = {port_id: 0.0 for port_id in range(1, 10)}
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                if edge_id not in live_edge_ids:
                    raise SnapshotCompatibilityError(
                        "GRC9V3 coarse-graining encountered a stale incident edge"
                    )
                port_id = self._local_port_id(edge_id=edge_id, node_id=node_id)
                node_ports[port_id] = self._oriented_flux(edge_id=edge_id, node_id=node_id)
            port_field[node_id] = node_ports
        return port_field

    def _local_port_id(self, *, edge_id: int, node_id: int) -> int:
        endpoint_a, endpoint_b = self._state.topology.edge_ports(edge_id)
        if endpoint_a[0] == node_id:
            return slot_to_port_id(endpoint_a[1])
        if endpoint_b[0] == node_id:
            return slot_to_port_id(endpoint_b[1])
        raise InvalidStateTransitionError("edge is not incident to node_id")

    def _oriented_flux(self, *, edge_id: int, node_id: int) -> float:
        port_edge = self._state.port_edges[edge_id]
        if port_edge.node_u == node_id:
            return float(port_edge.flux_uv)
        if port_edge.node_v == node_id:
            return float(-port_edge.flux_uv)
        raise SnapshotCompatibilityError(f"edge {edge_id} is not incident to node {node_id}")

    def _invalidate_coarse_cache(self, reason: str) -> None:
        cleared = bool(self._state.coarse_cache)
        self._state.coarse_cache.clear()
        existing_invalidated = bool(
            self._state.cached_quantities.get("coarse_cache_invalidated", False)
        )
        existing_reason = str(
            self._state.cached_quantities.get("coarse_cache_invalidation_reason", "none")
        )
        self._state.cached_quantities["coarse_cache_invalidated"] = bool(
            existing_invalidated or cleared
        )
        if (
            reason == "transport_recomputation"
            and not cleared
            and existing_invalidated
            and existing_reason != "none"
        ):
            return
        self._state.cached_quantities["coarse_cache_invalidation_reason"] = reason

    def step(self) -> StepResult:
        """Advance one full Phase 7 GRC9V3 hybrid step."""

        trace: list[str] = []
        initial_event_count = len(self._state.event_log)

        self.rebuild_differential_state()
        trace.extend(
            (
                "compute_row_basis_gradient_pre_flux",
                "compute_signed_hessian_row_basis_pre_flux",
                "compute_net_flux_summary_pre_flux",
                "compute_node_tensors",
            )
        )

        self.rebuild_transport_state()
        trace.extend(
            (
                "compute_base_conductance",
                "compute_edge_labels_pre_flux",
                "compute_potential",
                "compute_flux",
                "compute_edge_labels_post_flux",
            )
        )

        self.rebuild_differential_state()
        trace.append("refresh_differential_summary_post_flux")

        self.rebuild_identity_state()
        trace.append("detect_flux_topology_identities")
        trace.append("validate_geometric_basin_seeds")
        trace.append("compute_effective_basin_masses")

        self._apply_hybrid_spark_stages(trace)

        self.rebuild_choice_state()
        trace.append("update_choice_collapse_learning")

        self.apply_growth()
        trace.append("apply_growth")

        self.apply_boundary_behavior()
        trace.append("apply_boundary_behavior")

        self.apply_continuity()
        trace.append("apply_continuity")

        self.enforce_quadrature_budget()
        trace.append("enforce_quadrature_budget")

        self.rebuild_differential_state()
        self.rebuild_transport_state()
        self.rebuild_differential_state()
        self.rebuild_identity_state()
        trace.append("refresh_runtime_state_final")

        self.refresh_coarse_cache()
        trace.append("refresh_or_invalidate_coarse_cache")

        observables = self.compute_observables()
        trace.append("compute_observables")
        final_events = list(self._state.event_log[initial_event_count:])

        self._state.step_index += 1
        self._state.time += self._params.dt
        self._state.observables = dict(observables)
        self._state.params_identity = self._params.params_hash
        self._state.cached_quantities["last_step_trace"] = tuple(trace)
        self._state.cached_quantities["current_step_events"] = [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in final_events
        ]
        self._validate_state(self._state)

        return StepResult(
            step_index=self._state.step_index,
            time=self._state.time,
            events=final_events,
            observables=dict(observables),
            bookkeeping={
                "step_order": tuple(trace),
                "expected_step_order": _STEP_ORDER,
            },
        )

    def reset(self) -> None:
        if self._initial_state is None:
            raise SnapshotCompatibilityError(
                "reset baseline is unavailable; call rebase_reset_baseline() "
                "explicitly before reset()"
            )
        self._state = deepcopy(self._initial_state)

    def rebase_reset_baseline(self) -> None:
        self._initial_state = deepcopy(self._state)
        self._reset_baseline_unavailable_reason = None

    def _snapshot_payload(
        self,
        *,
        reset_baseline: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        edge_labels = {
            "base_conductance": _stringify_mapping_keys(self._state.base_conductance),
            "geometric_length": _stringify_mapping_keys(self._state.geometric_length),
            "temporal_delay": _stringify_mapping_keys(self._state.temporal_delay),
            "flux_coupling": _stringify_mapping_keys(self._state.flux_coupling),
            "edge_label_computation_mode": dict(self._state.edge_label_computation_mode),
            "edge_label_params": _stringify_mapping_keys(self._state.edge_label_params),
        }
        return build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family=self.MODEL_FAMILY,
                step_index=self._state.step_index,
                params=dict(self._params.raw_config),
                resolved_params=dict(self._params.resolved_config),
                params_hash=self._params.params_hash,
                capabilities=self.list_capabilities(),
                rng_state=self._state.rng_state,
                next_node_id=self._state.topology.next_node_id,
                next_edge_id=self._state.topology.next_edge_id,
            ),
            topology=export_port_topology(self._state.topology),
            basin_attributes={
                "nodes": {
                    str(node_id): _serialize_node_state(node_state)
                    for node_id, node_state in self._state.nodes.items()
                },
                "hierarchy": _stringify_mapping_keys(self._state.hierarchy),
                "expansion_registry": {
                    str(expansion_id): _serialize_expansion_record(record)
                    for expansion_id, record in sorted(self._state.expansion_registry.items())
                },
            },
            edge_labels=edge_labels,
            dynamics=build_dynamics_group(state=_state_payload_from_state(self._state)),
            observables=_stringify_mapping_keys(self.compute_observables()),
            events=build_event_records(
                [
                    {
                        "kind": event.kind,
                        "step_index": event.step_index,
                        "payload": dict(event.payload),
                        "source_family": event.source_family,
                    }
                    for event in self._state.event_log
                ]
            ),
            reset_baseline=reset_baseline,
            caches={"coarse_cache": _stringify_mapping_keys(self._state.coarse_cache)},
        )

    def snapshot(self) -> dict[str, Any]:
        if self._initial_state is None:
            reset_baseline = build_reset_baseline_group(
                model_family=self.MODEL_FAMILY,
                baseline_snapshot=None,
                unavailable_reason=(
                    self._reset_baseline_unavailable_reason
                    or "reset_baseline_unavailable"
                ),
            )
        else:
            baseline_model = type(self)(
                params=self._params,
                state=deepcopy(self._initial_state),
            )
            reset_baseline = build_reset_baseline_group(
                model_family=self.MODEL_FAMILY,
                baseline_snapshot=baseline_model._snapshot_payload(
                    reset_baseline=None
                ),
            )
        return self._snapshot_payload(reset_baseline=reset_baseline)

    def save(self, path: str) -> None:
        save_snapshot(path, self.snapshot())

    def _validate_state(self, state: GRC9V3State) -> None:
        live_nodes = set(state.topology.iter_live_node_ids())
        live_edges = set(state.topology.iter_live_edge_ids())
        if set(state.nodes) - live_nodes:
            raise SnapshotCompatibilityError(
                "GRC9V3State.nodes keys must reference live topology nodes"
            )
        if set(state.port_edges) != live_edges:
            raise SnapshotCompatibilityError(
                "GRC9V3State.port_edges keys must exactly match live topology edges"
            )
        if set(state.base_conductance) - live_edges:
            raise SnapshotCompatibilityError(
                "GRC9V3State.base_conductance keys must reference live topology edges"
            )
        for label_name, label_values in (
            ("geometric_length", state.geometric_length),
            ("temporal_delay", state.temporal_delay),
            ("flux_coupling", state.flux_coupling),
        ):
            if set(label_values) - live_edges:
                raise SnapshotCompatibilityError(
                    f"GRC9V3State.{label_name} keys must reference live topology edges"
                )
        if set(state.potential) - live_nodes:
            raise SnapshotCompatibilityError(
                "GRC9V3State.potential keys must reference live topology nodes"
            )
        if state.sink_set - live_nodes:
            raise SnapshotCompatibilityError(
                "GRC9V3State.sink_set must reference live topology nodes"
            )
        if set(state.basins) - live_nodes:
            raise SnapshotCompatibilityError(
                "GRC9V3State.basins keys must reference live topology nodes"
            )
        for members in state.basins.values():
            if members - live_nodes:
                raise SnapshotCompatibilityError(
                    "GRC9V3State.basins memberships must reference live topology nodes"
                )
        for record in state.expansion_registry.values():
            if not all(node_id in live_nodes for node_id in record.module_node_ids):
                raise SnapshotCompatibilityError(
                    "GRC9V3State.expansion_registry module nodes must reference live topology nodes"
                )
        for node_id, node_state in state.nodes.items():
            if node_state.coherence < 0.0:
                raise SnapshotCompatibilityError(
                    f"GRC9V3State.nodes[{node_id}].coherence must be non-negative"
                )


__all__ = ["GRC9V3"]

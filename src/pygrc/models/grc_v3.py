"""Construction and state surface for the GRCV3 semantic family."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
import math
import random
import warnings
from typing import Any, Final

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    BOUNDARY_BARRIER,
    GRCEvent,
    GRCModel,
    GRCParams,
    GRCV3_CAPABILITY_PROFILE,
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    InvalidParamsError,
    ObservableMap,
    SnapshotCompatibilityError,
    StepResult,
    WeightedGraphBackend,
    build_backend_selection,
    build_backend_selection_payload,
    build_event_records,
    build_reset_baseline_group,
    build_snapshot_metadata,
    build_standard_snapshot,
    build_topology_snapshot,
    deserialize_rng_state,
    export_weighted_topology,
    load_snapshot,
    require_snapshot_family,
    reset_baseline_snapshot,
    restore_backend_selections,
    restore_weighted_graph,
    save_snapshot,
    serialize_rng_state,
    validate_supported_backend_selections,
)

from .grc_v3_differential import (
    calibrate_hessian_sign,
    induced_local_frame_displacements,
    net_flux_summary,
    symmetric_eigenvalues,
    weighted_least_squares_gradient,
    weighted_least_squares_hessian,
)
from .grc_v3_state import BasinAttributes, GRCV3State, OrientedEdgeId


_ALLOWED_FRAME_MODES: Final[set[str]] = {
    "host_embedding",
    "induced_local_frame",
    "combinatorial",
}
_ALLOWED_BOUNDARY_MODES: Final[set[str]] = {"prune", "barrier", "ghost"}
_ALLOWED_SPLIT_DISTRIBUTION_MODES: Final[set[str]] = {"equal", "custom"}
_ALLOWED_CURVATURE_BACKENDS: Final[set[str]] = {"ollivier", "forman", "none"}
_ALLOWED_FRONTIER_BIRTH_MODES: Final[set[str]] = {
    "disabled",
    "active_frontier_pressure",
}
_ALLOWED_FRONTIER_BIRTH_STRICT_VALUES: Final[set[str]] = {
    "warn",
    "error",
    "allow",
}
_ALLOWED_EDGE_LABELS: Final[set[str]] = {
    "geometric_length",
    "temporal_delay",
    "flux_coupling",
}
_SUPPORTED_BACKEND_NAMES_BY_CATEGORY: Final[dict[str, set[str]]] = {
    "geometry": {"host_embedding", "induced_local_frame", "combinatorial"},
    "differential_summary": {
        "weighted_least_squares",
        "combinatorial_surrogate",
    },
    "metric": {"tensor_exponential"},
    "curvature": {"none", "forman", "ollivier"},
    "spark": {
        "signed_hessian_degeneracy",
        "signed_hessian_plus_attractor_delta",
    },
    "hierarchy_update": {"basin_parent_child"},
    "choice": {"disabled", "sink_compatibility"},
}

_DEFAULT_EVOLUTION: Final[dict[str, Any]] = {
    "alpha": 1.0,
    "beta": 1.0,
    "gamma": 1.0,
    "delta": 1.0,
    "eta": 1.0,
    "kappa_c": 1.0,
    "lambda_c": 1.0,
    "xi_c": 1.0,
    "zeta_c": 1.0,
    "eps_gradient": 1e-3,
    "eps_hessian": 1e-3,
    "eps_spark": 1e-3,
    "tau_split": 2.0,
    "site_potential_selection": "quadratic",
    "site_potential_params": {
        "mu": 0.0,
        "scale": 1.0,
    },
    "temporal_label_params": {
        "v0": 1.0,
        "rho": 1.0,
        "eps_tau": 1e-9,
    },
    "compatibility_score_params": {
        "epsilon_choice": 1e-3,
        "epsilon_collapse": 1e-3,
    },
}

_DEFAULT_MODES: Final[dict[str, Any]] = {
    "frame_mode": "induced_local_frame",
    "boundary_mode": "prune",
    "split_distribution_mode": "equal",
    "edge_label_selection": "all",
    "curvature_backend": "none",
    "budget_measure_mode": "measure_absorbed",
}

_DEFAULT_EDGE_LABEL_COMPUTATION_MODE: Final[dict[str, str]] = {
    "geometric_length": "induced_intrinsic",
    "temporal_delay": "transport_ratio",
    "flux_coupling": "absolute_flux",
}

_STEP_ORDER: Final[tuple[str, ...]] = (
    "compute_differential_summary_pre_flux",
    "compute_node_tensors",
    "compute_metric",
    "compute_edge_labels_pre_flux",
    "compute_potential",
    "compute_flux",
    "compute_edge_labels_post_flux",
    "refresh_differential_summary_post_flux",
    "detect_identities",
    "detect_sparks",
    "advance_splits",
    "update_choice_state",
    "apply_continuity",
    "enforce_budget",
    "refresh_runtime_state",
    "compute_observables",
)
_STEP_ORDER_WITH_FRONTIER_BIRTH: Final[tuple[str, ...]] = (
    *_STEP_ORDER[:12],
    "apply_frontier_birth",
    *_STEP_ORDER[12:],
)


def _as_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidParamsError(f"{context} must be a float-compatible number")
    return float(value)


def _as_runtime_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SnapshotCompatibilityError(f"{context} must be a float-compatible number")
    return float(value)


def _default_rng_state(seed: int = 0) -> Any:
    return random.Random(seed).getstate()


def _identity_matrix(dimension: int) -> list[list[float]]:
    return [
        [1.0 if row_index == column_index else 0.0 for column_index in range(dimension)]
        for row_index in range(dimension)
    ]


def _pad_vector(values: list[float], *, dimension: int) -> list[float]:
    if dimension <= 0:
        return []
    padded = list(values[:dimension])
    if len(padded) < dimension:
        padded.extend(0.0 for _ in range(dimension - len(padded)))
    return padded


def _pad_matrix(values: list[list[float]], *, dimension: int) -> list[list[float]]:
    padded = _zero_matrix(dimension)
    for row_index in range(min(dimension, len(values))):
        row = values[row_index]
        for column_index in range(min(dimension, len(row))):
            padded[row_index][column_index] = float(row[column_index])
    return padded


def _zero_matrix(dimension: int) -> list[list[float]]:
    return [[0.0 for _ in range(dimension)] for _ in range(dimension)]


def _outer_product(values: list[float]) -> list[list[float]]:
    dimension = len(values)
    return [
        [float(values[row_index] * values[column_index]) for column_index in range(dimension)]
        for row_index in range(dimension)
    ]


def _matrix_add_scaled(
    target: list[list[float]],
    source: list[list[float]],
    *,
    scale: float,
) -> None:
    for row_index in range(len(target)):
        for column_index in range(len(target[row_index])):
            target[row_index][column_index] += scale * source[row_index][column_index]


def _matrix_average(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    dimension = max(len(left), len(right))
    left_padded = _pad_matrix(left, dimension=dimension)
    right_padded = _pad_matrix(right, dimension=dimension)
    averaged = _zero_matrix(dimension)
    for row_index in range(dimension):
        for column_index in range(dimension):
            averaged[row_index][column_index] = (
                left_padded[row_index][column_index]
                + right_padded[row_index][column_index]
            ) / 2.0
    return averaged


def _quadratic_form(matrix: list[list[float]], vector: list[float]) -> float:
    total = 0.0
    for row_index, row in enumerate(matrix):
        if row_index >= len(vector):
            break
        for column_index, value in enumerate(row):
            if column_index >= len(vector):
                break
            total += vector[row_index] * float(value) * vector[column_index]
    return float(total)


def _euclidean_distance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise SnapshotCompatibilityError("host geometry coordinate dimensions must match")
    total = 0.0
    for left_value, right_value in zip(left, right, strict=True):
        total += (left_value - right_value) ** 2
    return float(math.sqrt(total))


def _restore_coordinate_vector(value: Any, *, context: str) -> list[float] | None:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)):
        raise SnapshotCompatibilityError(f"{context} must be a coordinate sequence")
    coordinates = [_as_runtime_float(item, context=context) for item in value]
    if not coordinates:
        raise SnapshotCompatibilityError(f"{context} must not be empty")
    return coordinates


def _validate_site_potential(evolution: Mapping[str, Any]) -> None:
    if "site_potential_selection" not in evolution:
        raise InvalidParamsError("GRCV3 requires site_potential_selection")
    if "site_potential_params" not in evolution:
        raise InvalidParamsError("GRCV3 requires site_potential_params")
    if not isinstance(evolution["site_potential_selection"], str):
        raise InvalidParamsError("site_potential_selection must be a string")
    if not isinstance(evolution["site_potential_params"], Mapping):
        raise InvalidParamsError("site_potential_params must be a mapping")


def _json_safe_cached_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe_cached_value(inner_value)
            for key, inner_value in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple):
        return [_json_safe_cached_value(item) for item in value]
    if isinstance(value, list):
        return [_json_safe_cached_value(item) for item in value]
    if isinstance(value, set | frozenset):
        return sorted(_json_safe_cached_value(item) for item in value)
    return value


def _restore_basin_attributes(value: Any, *, context: str) -> BasinAttributes:
    if isinstance(value, BasinAttributes):
        return deepcopy(value)
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")

    coherence = _as_float(value.get("coherence", 0.0), context=f"{context}.coherence")
    gradient = _restore_float_vector(
        value.get("gradient", []), context=f"{context}.gradient"
    )
    net_flux = _restore_float_vector(
        value.get("net_flux", []), context=f"{context}.net_flux"
    )
    hessian = _restore_float_matrix(
        value.get("hessian", []), context=f"{context}.hessian"
    )
    basin_mass = _as_float(
        value.get("basin_mass", coherence), context=f"{context}.basin_mass"
    )
    basin_id = value.get("basin_id", 0)
    if basin_id is None or not isinstance(basin_id, str | int):
        raise SnapshotCompatibilityError(f"{context}.basin_id must be a string or int")
    parent_id = value.get("parent_id")
    if parent_id is not None and not isinstance(parent_id, str | int):
        raise SnapshotCompatibilityError(
            f"{context}.parent_id must be a string, int, or null"
        )
    depth = value.get("depth", 0)
    if not isinstance(depth, int):
        raise SnapshotCompatibilityError(f"{context}.depth must be an int")

    return BasinAttributes(
        coherence=coherence,
        gradient=gradient,
        hessian=hessian,
        net_flux=net_flux,
        basin_mass=basin_mass,
        basin_id=basin_id,
        parent_id=parent_id,
        depth=depth,
    )


def _restore_float_vector(value: Any, *, context: str) -> list[float]:
    if not isinstance(value, list | tuple):
        raise SnapshotCompatibilityError(f"{context} must be a sequence")
    return [_as_float(item, context=context) for item in value]


def _restore_float_matrix(value: Any, *, context: str) -> list[list[float]]:
    if not isinstance(value, list | tuple):
        raise SnapshotCompatibilityError(f"{context} must be a sequence of rows")
    matrix: list[list[float]] = []
    for row_index, row in enumerate(value):
        matrix.append(
            _restore_float_vector(row, context=f"{context}[{row_index}]")
        )
    return matrix


def _require_numeric_mapping(
    values: Mapping[Any, Any],
    *,
    key_context: str,
    value_context: str,
) -> dict[int, float]:
    numeric_mapping: dict[int, float] = {}
    for raw_key, raw_value in values.items():
        if isinstance(raw_key, int):
            key = raw_key
        elif isinstance(raw_key, str):
            try:
                key = int(raw_key)
            except ValueError as exc:
                raise SnapshotCompatibilityError(
                    f"{key_context} keys must be int-compatible"
                ) from exc
        else:
            raise SnapshotCompatibilityError(f"{key_context} keys must be int-compatible")
        numeric_mapping[key] = _as_float(raw_value, context=value_context)
    return numeric_mapping


def _require_basin_mapping(values: Mapping[Any, Any]) -> dict[int, set[int]]:
    basin_mapping: dict[int, set[int]] = {}
    for raw_key, raw_value in values.items():
        if isinstance(raw_key, int):
            key = raw_key
        elif isinstance(raw_key, str):
            try:
                key = int(raw_key)
            except ValueError as exc:
                raise SnapshotCompatibilityError(
                    "basin keys must be int-compatible node IDs"
                ) from exc
        else:
            raise SnapshotCompatibilityError("basin keys must be int-compatible node IDs")
        if not isinstance(raw_value, (set, list, tuple)):
            raise SnapshotCompatibilityError("basin values must be collections of node IDs")
        members: set[int] = set()
        for node_id in raw_value:
            if isinstance(node_id, int):
                members.add(node_id)
            elif isinstance(node_id, str):
                try:
                    members.add(int(node_id))
                except ValueError as exc:
                    raise SnapshotCompatibilityError(
                        "basin memberships must be int-compatible"
                    ) from exc
            else:
                raise SnapshotCompatibilityError(
                    "basin memberships must contain only int-compatible values"
                )
        basin_mapping[key] = members
    return basin_mapping


def _require_flux_mapping(values: Mapping[Any, Any]) -> dict[OrientedEdgeId, float]:
    flux_mapping: dict[OrientedEdgeId, float] = {}
    for raw_key, raw_value in values.items():
        edge_id: int
        node_id: int
        if isinstance(raw_key, tuple) and len(raw_key) == 2:
            edge_id, node_id = raw_key
        elif isinstance(raw_key, str):
            parts = raw_key.split(":")
            if len(parts) != 2:
                raise SnapshotCompatibilityError(
                    "flux string keys must be 'edge_id:node_id'"
                )
            try:
                edge_id = int(parts[0])
                node_id = int(parts[1])
            except ValueError as exc:
                raise SnapshotCompatibilityError(
                    "flux string keys must contain int-compatible IDs"
                ) from exc
        else:
            raise SnapshotCompatibilityError(
                "flux keys must be oriented edge tuples or 'edge_id:node_id' strings"
            )

        if not isinstance(edge_id, int) or not isinstance(node_id, int):
            raise SnapshotCompatibilityError(
                "flux keys must use int-compatible edge and node IDs"
            )
        flux_mapping[(edge_id, node_id)] = _as_float(
            raw_value, context="flux values"
        )
    return flux_mapping


def _restore_hierarchy_mapping(value: Any) -> dict[str | int, list[str | int]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError("hierarchy must be a mapping")
    hierarchy: dict[str | int, list[str | int]] = {}
    for raw_key, raw_children in value.items():
        key: str | int
        if isinstance(raw_key, int):
            key = raw_key
        elif isinstance(raw_key, str):
            try:
                key = int(raw_key)
            except ValueError:
                key = raw_key
        else:
            raise SnapshotCompatibilityError(
                "hierarchy keys must be strings or ints"
            )
        if not isinstance(raw_children, list | tuple):
            raise SnapshotCompatibilityError(
                "hierarchy values must be sequences of strings or ints"
            )
        children: list[str | int] = []
        for child in raw_children:
            if isinstance(child, int):
                children.append(child)
                continue
            if not isinstance(child, str | int):
                raise SnapshotCompatibilityError(
                    "hierarchy entries must be strings or ints"
                )
            if isinstance(child, str):
                try:
                    children.append(int(child))
                except ValueError:
                    children.append(child)
        hierarchy[key] = children
    return hierarchy


def _state_payload_from_state(state: GRCV3State) -> dict[str, Any]:
    return {
        "potential": {str(node_id): value for node_id, value in state.potential.items()},
        "flux": {
            f"{edge_id}:{node_id}": value
            for (edge_id, node_id), value in state.flux.items()
        },
        "sink_set": sorted(state.sink_set),
        "basins": {
            str(node_id): sorted(members) for node_id, members in state.basins.items()
        },
        "hierarchy": {
            str(key): list(children) for key, children in state.hierarchy.items()
        },
        "choice_registry": dict(state.choice_registry),
        "collapse_registry": dict(state.collapse_registry),
        "step_index": state.step_index,
        "time": state.time,
        "budget_target": state.budget_target,
        "remainder": state.remainder,
        "cached_quantities": _json_safe_cached_value(state.cached_quantities),
        "event_log": [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in state.event_log
        ],
        "observables": dict(state.observables),
        "rng_state": serialize_rng_state(state.rng_state),
        "params_identity": state.params_identity,
    }


def _basin_attributes_group_from_state(state: GRCV3State) -> dict[str, Any]:
    return {
        "nodes": {
            str(node_id): {
                "coherence": attributes.coherence,
                "gradient": list(attributes.gradient),
                "hessian": [list(row) for row in attributes.hessian],
                "net_flux": list(attributes.net_flux),
                "basin_mass": attributes.basin_mass,
                "basin_id": attributes.basin_id,
                "parent_id": attributes.parent_id,
                "depth": attributes.depth,
            }
            for node_id, attributes in state.nodes.items()
        },
        "hierarchy": {str(key): list(children) for key, children in state.hierarchy.items()},
    }


def _edge_labels_group_from_state(state: GRCV3State) -> dict[str, Any]:
    return {
        "base_conductance": {
            str(edge_id): value for edge_id, value in state.base_conductance.items()
        },
        "geometric_length": {
            str(edge_id): value for edge_id, value in state.geometric_length.items()
        },
        "temporal_delay": {
            str(edge_id): value for edge_id, value in state.temporal_delay.items()
        },
        "flux_coupling": {
            str(edge_id): value for edge_id, value in state.flux_coupling.items()
        },
        "edge_label_computation_mode": dict(state.edge_label_computation_mode),
        "edge_label_params": dict(state.edge_label_params),
    }


def _coerce_plain_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return dict(value)


def _restore_event_log(values: Any) -> list[GRCEvent]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise SnapshotCompatibilityError("GRCV3 state.event_log must be a list")
    event_log: list[GRCEvent] = []
    for index, raw_event in enumerate(values):
        if not isinstance(raw_event, Mapping):
            raise SnapshotCompatibilityError(
                f"GRCV3 state.event_log[{index}] must be a mapping"
            )
        kind = raw_event.get("kind")
        if not isinstance(kind, str):
            raise SnapshotCompatibilityError(
                f"GRCV3 state.event_log[{index}].kind must be a string"
            )
        step_index = raw_event.get("step_index", 0)
        if not isinstance(step_index, int):
            raise SnapshotCompatibilityError(
                f"GRCV3 state.event_log[{index}].step_index must be an int"
            )
        payload = raw_event.get("payload", {})
        if not isinstance(payload, Mapping):
            raise SnapshotCompatibilityError(
                f"GRCV3 state.event_log[{index}].payload must be a mapping"
            )
        source_family = raw_event.get("source_family")
        if source_family is not None and not isinstance(source_family, str):
            raise SnapshotCompatibilityError(
                f"GRCV3 state.event_log[{index}].source_family must be a string when present"
            )
        event_log.append(
            GRCEvent(
                kind=kind,
                step_index=step_index,
                payload=dict(payload),
                source_family=source_family,
            )
        )
    return event_log


def _restore_runtime_rng_state(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, tuple) and len(value) == 3 and isinstance(value[0], int):
        return value
    if isinstance(value, list) and len(value) == 3 and isinstance(value[0], int):
        return deserialize_rng_state({"engine": "python_random", "state": value})
    return deserialize_rng_state(value)


def _validate_edge_label_selection(selection: Any) -> None:
    if selection == "all":
        return
    if not isinstance(selection, (list, tuple, set, frozenset)):
        raise InvalidParamsError(
            "edge_label_selection must be 'all' or an iterable of label names"
        )
    normalized = set(selection)
    if not normalized:
        raise InvalidParamsError("edge_label_selection must not be empty")
    unknown = normalized - _ALLOWED_EDGE_LABELS
    if unknown:
        raise InvalidParamsError(
            f"edge_label_selection includes unknown labels: {sorted(unknown)}"
        )


def _merge_nested(defaults: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    merged = {key: deepcopy(value) for key, value in defaults.items()}
    for key, value in overrides.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, Mapping)
        ):
            merged[key] = _merge_nested(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _resolve_backend_selection_payload(
    modes: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw_backend_payload = modes.get(BACKEND_SELECTIONS_KEY, {})
    if raw_backend_payload in (None, {}):
        provided = {}
    else:
        if not isinstance(raw_backend_payload, Mapping):
            raise InvalidParamsError("backend_selections must be a mapping")
        try:
            provided = restore_backend_selections(raw_backend_payload)
        except (TypeError, ValueError) as exc:
            raise InvalidParamsError(str(exc)) from exc

    frame_mode = str(modes["frame_mode"])
    curvature_backend = str(modes["curvature_backend"])

    selections = {
        "geometry": build_backend_selection(
            category="geometry",
            name=frame_mode,
            params={"dimension": 2},
        ),
        "differential_summary": build_backend_selection(
            category="differential_summary",
            name="weighted_least_squares",
            params={"regularization": 1e-9, "hessian_regularization": 1e-9},
        ),
        "metric": build_backend_selection(
            category="metric",
            name="tensor_exponential",
        ),
        "curvature": build_backend_selection(
            category="curvature",
            name=curvature_backend,
        ),
        "spark": build_backend_selection(
            category="spark",
            name="signed_hessian_plus_attractor_delta",
            params={"min_child_basins": 1},
        ),
        "hierarchy_update": build_backend_selection(
            category="hierarchy_update",
            name="basin_parent_child",
        ),
        "choice": build_backend_selection(
            category="choice",
            name="disabled",
        ),
    }

    for category, selection in provided.items():
        selections[category] = selection

    if selections["geometry"].name != frame_mode:
        raise InvalidParamsError(
            "geometry backend selection must match frame_mode in GRCV3"
        )
    if selections["curvature"].name != curvature_backend:
        raise InvalidParamsError(
            "curvature backend selection must match curvature_backend in GRCV3"
        )

    try:
        validate_supported_backend_selections(
            selections,
            allowed_names_by_category=_SUPPORTED_BACKEND_NAMES_BY_CATEGORY,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidParamsError(str(exc)) from exc
    return build_backend_selection_payload(selections)


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

    frame_mode = modes["frame_mode"]
    boundary_mode = modes["boundary_mode"]
    split_distribution_mode = modes["split_distribution_mode"]
    curvature_backend = modes["curvature_backend"]
    budget_measure_mode = modes["budget_measure_mode"]
    frontier_birth_mode = modes.get("frontier_birth_mode", "disabled")

    if frame_mode not in _ALLOWED_FRAME_MODES:
        raise InvalidParamsError(
            "frame_mode must be one of host_embedding, induced_local_frame, combinatorial"
        )
    if boundary_mode not in _ALLOWED_BOUNDARY_MODES:
        raise InvalidParamsError("boundary_mode must be one of prune, barrier, ghost")
    if split_distribution_mode not in _ALLOWED_SPLIT_DISTRIBUTION_MODES:
        raise InvalidParamsError(
            "split_distribution_mode must be one of equal, custom"
        )
    if curvature_backend not in _ALLOWED_CURVATURE_BACKENDS:
        raise InvalidParamsError(
            "curvature_backend must be one of ollivier, forman, none"
        )
    if budget_measure_mode not in {"measure_absorbed", "unit_measure"}:
        raise InvalidParamsError(
            "budget_measure_mode must be one of measure_absorbed, unit_measure"
        )
    if frontier_birth_mode not in _ALLOWED_FRONTIER_BIRTH_MODES:
        raise InvalidParamsError(
            "frontier_birth_mode must be one of disabled, active_frontier_pressure"
        )
    frontier_birth_strict = modes.get("frontier_birth_strict", "warn")
    if not isinstance(frontier_birth_strict, str):
        raise InvalidParamsError("frontier_birth_strict must be one of warn, error, allow")
    if frontier_birth_strict not in _ALLOWED_FRONTIER_BIRTH_STRICT_VALUES:
        raise InvalidParamsError("frontier_birth_strict must be one of warn, error, allow")

    if frame_mode == "host_embedding":
        host_geometry_fields = modes.get("host_geometry_fields")
        if not isinstance(host_geometry_fields, (list, tuple, set, frozenset)) or not host_geometry_fields:
            raise InvalidParamsError(
                "host_embedding frame_mode requires non-empty host_geometry_fields"
            )

    _validate_edge_label_selection(modes["edge_label_selection"])

    temporal_label_params = evolution["temporal_label_params"]
    if not isinstance(temporal_label_params, Mapping):
        raise InvalidParamsError("temporal_label_params must be a mapping")
    _as_float(temporal_label_params.get("v0", 1.0), context="temporal_label_params.v0")
    _as_float(
        temporal_label_params.get("rho", 1.0),
        context="temporal_label_params.rho",
    )
    eps_tau = _as_float(
        temporal_label_params.get("eps_tau", 1e-9),
        context="temporal_label_params.eps_tau",
    )
    if eps_tau <= 0.0:
        raise InvalidParamsError("temporal_label_params.eps_tau must be > 0")

    compatibility_score_params = evolution["compatibility_score_params"]
    if not isinstance(compatibility_score_params, Mapping):
        raise InvalidParamsError("compatibility_score_params must be a mapping")
    _validate_site_potential(evolution)

    for key in (
        "alpha",
        "beta",
        "gamma",
        "delta",
        "eta",
        "kappa_c",
        "lambda_c",
        "xi_c",
        "zeta_c",
        "eps_gradient",
        "eps_hessian",
        "eps_spark",
        "tau_split",
    ):
        value = _as_float(evolution[key], context=key)
        if key != "eps_spark" and value <= 0.0:
            raise InvalidParamsError(f"{key} must be > 0")
        if key == "eps_spark" and value < 0.0:
            raise InvalidParamsError("eps_spark must be >= 0")

    if "lambda_birth" in evolution:
        lambda_birth = _as_float(evolution["lambda_birth"], context="lambda_birth")
        if lambda_birth < 0.0:
            raise InvalidParamsError("lambda_birth must be >= 0")
    if "alpha_seed" in evolution:
        alpha_seed = _as_float(evolution["alpha_seed"], context="alpha_seed")
        if not 0.0 <= alpha_seed <= 1.0:
            raise InvalidParamsError("alpha_seed must be between 0 and 1")
    if "frontier_birth_edge_conductance" in evolution:
        edge_conductance = _as_float(
            evolution["frontier_birth_edge_conductance"],
            context="frontier_birth_edge_conductance",
        )
        if edge_conductance <= 0.0:
            raise InvalidParamsError("frontier_birth_edge_conductance must be > 0")
    if "rng_seed" in evolution and (
        isinstance(evolution["rng_seed"], bool) or not isinstance(evolution["rng_seed"], int)
    ):
        raise InvalidParamsError("rng_seed must be an integer")

    modes[BACKEND_SELECTIONS_KEY] = _resolve_backend_selection_payload(modes)

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


def _state_from_inputs(
    *,
    params: GRCParams,
    state_mapping: Mapping[str, Any] | None = None,
    topology: WeightedGraphBackend | None = None,
) -> GRCV3State:
    mapping = {} if state_mapping is None else dict(state_mapping)
    resolved_modes = dict(params.constitutive_semantic_modes)
    resolved_evolution = dict(params.evolution)

    node_payload = _coerce_plain_mapping(mapping.get("nodes", {}), context="GRCV3 state.nodes")
    nodes = {
        int(node_id): _restore_basin_attributes(attributes, context=f"GRCV3 state.nodes[{node_id!r}]")
        for node_id, attributes in node_payload.items()
    }

    hessian_sign = mapping.get("hessian_sign")
    event_log = _restore_event_log(mapping.get("event_log", []))
    observables = _coerce_plain_mapping(
        mapping.get("observables", {}),
        context="GRCV3 state.observables",
    )

    state = GRCV3State(
        topology=topology if topology is not None else WeightedGraphBackend(),
        nodes=nodes,
        base_conductance=_require_numeric_mapping(
            _coerce_plain_mapping(
                mapping.get("base_conductance", {}),
                context="GRCV3 state.base_conductance",
            ),
            key_context="GRCV3 state.base_conductance",
            value_context="GRCV3 state.base_conductance",
        ),
        geometric_length=_require_numeric_mapping(
            _coerce_plain_mapping(
                mapping.get("geometric_length", {}),
                context="GRCV3 state.geometric_length",
            ),
            key_context="GRCV3 state.geometric_length",
            value_context="GRCV3 state.geometric_length",
        ),
        temporal_delay=_require_numeric_mapping(
            _coerce_plain_mapping(
                mapping.get("temporal_delay", {}),
                context="GRCV3 state.temporal_delay",
            ),
            key_context="GRCV3 state.temporal_delay",
            value_context="GRCV3 state.temporal_delay",
        ),
        flux_coupling=_require_numeric_mapping(
            _coerce_plain_mapping(
                mapping.get("flux_coupling", {}),
                context="GRCV3 state.flux_coupling",
            ),
            key_context="GRCV3 state.flux_coupling",
            value_context="GRCV3 state.flux_coupling",
        ),
        flux=_require_flux_mapping(
            _coerce_plain_mapping(mapping.get("flux", {}), context="GRCV3 state.flux")
        ),
        potential=_require_numeric_mapping(
            _coerce_plain_mapping(mapping.get("potential", {}), context="GRCV3 state.potential"),
            key_context="GRCV3 state.potential",
            value_context="GRCV3 state.potential",
        ),
        sink_set=set(mapping.get("sink_set", [])),
        basins=_require_basin_mapping(
            _coerce_plain_mapping(mapping.get("basins", {}), context="GRCV3 state.basins")
        ),
        hierarchy=_restore_hierarchy_mapping(mapping.get("hierarchy", {})),
        choice_registry=_coerce_plain_mapping(
            mapping.get("choice_registry", {}),
            context="GRCV3 state.choice_registry",
        ),
        collapse_registry=_coerce_plain_mapping(
            mapping.get("collapse_registry", {}),
            context="GRCV3 state.collapse_registry",
        ),
        edge_label_computation_mode=dict(
            mapping.get(
                "edge_label_computation_mode",
                _DEFAULT_EDGE_LABEL_COMPUTATION_MODE,
            )
        ),
        edge_label_params=dict(
            mapping.get(
                "edge_label_params",
                {
                    "temporal_delay": dict(resolved_evolution["temporal_label_params"]),
                    "selection": resolved_modes["edge_label_selection"],
                },
            )
        ),
        step_index=int(mapping.get("step_index", 0)),
        time=float(mapping.get("time", 0.0)),
        budget_target=float(mapping.get("budget_target", 0.0)),
        remainder=float(mapping.get("remainder", 0.0)),
        cached_quantities=dict(mapping.get("cached_quantities", {})),
        event_log=event_log,
        observables=observables,
        rng_state=_restore_runtime_rng_state(mapping.get("rng_state")),
        params_identity=str(mapping.get("params_identity", params.params_hash)),
    )

    if hessian_sign is not None:
        state.cached_quantities["hessian_sign"] = hessian_sign
    return state


class GRCV3(GRCModel):
    """Semantic reference implementation surface for the GRCV3 family."""

    MODEL_FAMILY = "GRCV3"
    CAPABILITY_PROFILE = GRCV3_CAPABILITY_PROFILE

    def __init__(self, params: GRCParams, state: GRCV3State | None = None) -> None:
        self._params = params
        self._state = deepcopy(state) if state is not None else _state_from_inputs(params=params)
        self._initial_state: GRCV3State | None = deepcopy(self._state)
        self._reset_baseline_unavailable_reason: str | None = None

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "GRCV3":
        params = _build_params(config)
        state_input = dict(config.get("state", {}))
        state = _state_from_inputs(params=params, state_mapping=state_input)
        return cls(params=params, state=state)

    @classmethod
    def from_state(
        cls,
        state: Mapping[str, Any] | GRCV3State,
        params: Mapping[str, Any],
    ) -> "GRCV3":
        resolved_params = _build_params(dict(params))
        if isinstance(state, GRCV3State):
            return cls(params=resolved_params, state=deepcopy(state))
        resolved_state = _state_from_inputs(
            params=resolved_params,
            state_mapping=dict(state),
        )
        return cls(params=resolved_params, state=resolved_state)

    @classmethod
    def load(cls, path: str) -> "GRCV3":
        snapshot = load_snapshot(path)
        return cls._from_snapshot(snapshot, restore_reset_baseline=True)

    @classmethod
    def _from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
        *,
        restore_reset_baseline: bool = False,
    ) -> "GRCV3":
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
        topology = restore_weighted_graph(topology_payload, metadata)

        basin_group = snapshot.get("basin_attributes", {})
        edge_labels_group = snapshot.get("edge_labels", {})
        dynamics = snapshot.get("dynamics", {})
        if basin_group is not None and not isinstance(basin_group, Mapping):
            raise SnapshotCompatibilityError("snapshot basin_attributes must be a mapping")
        if edge_labels_group is not None and not isinstance(edge_labels_group, Mapping):
            raise SnapshotCompatibilityError("snapshot edge_labels must be a mapping")
        if dynamics is not None and not isinstance(dynamics, Mapping):
            raise SnapshotCompatibilityError("snapshot dynamics must be a mapping")

        node_payload = {}
        hierarchy_payload = {}
        if isinstance(basin_group, Mapping):
            node_payload = dict(_coerce_plain_mapping(basin_group.get("nodes", {}), context="snapshot basin_attributes.nodes"))
            hierarchy_payload = dict(_coerce_plain_mapping(basin_group.get("hierarchy", {}), context="snapshot basin_attributes.hierarchy"))

        state_mapping = {
            "nodes": node_payload,
            "base_conductance": dict(_coerce_plain_mapping(edge_labels_group.get("base_conductance", {}), context="snapshot edge_labels.base_conductance")) if isinstance(edge_labels_group, Mapping) else {},
            "geometric_length": dict(_coerce_plain_mapping(edge_labels_group.get("geometric_length", {}), context="snapshot edge_labels.geometric_length")) if isinstance(edge_labels_group, Mapping) else {},
            "temporal_delay": dict(_coerce_plain_mapping(edge_labels_group.get("temporal_delay", {}), context="snapshot edge_labels.temporal_delay")) if isinstance(edge_labels_group, Mapping) else {},
            "flux_coupling": dict(_coerce_plain_mapping(edge_labels_group.get("flux_coupling", {}), context="snapshot edge_labels.flux_coupling")) if isinstance(edge_labels_group, Mapping) else {},
            "edge_label_computation_mode": dict(_coerce_plain_mapping(edge_labels_group.get("edge_label_computation_mode", {}), context="snapshot edge_labels.edge_label_computation_mode")) if isinstance(edge_labels_group, Mapping) else {},
            "edge_label_params": dict(_coerce_plain_mapping(edge_labels_group.get("edge_label_params", {}), context="snapshot edge_labels.edge_label_params")) if isinstance(edge_labels_group, Mapping) else {},
            "hierarchy": hierarchy_payload,
        }
        if isinstance(dynamics, Mapping):
            state_mapping.update(dict(_coerce_plain_mapping(dynamics.get("state", {}), context="snapshot dynamics.state")))
        if "event_log" not in state_mapping:
            event_records = snapshot.get("events", [])
            if event_records not in (None, []):
                if not isinstance(event_records, list):
                    raise SnapshotCompatibilityError("snapshot events must be a list")
                state_mapping["event_log"] = list(event_records)
        if "observables" not in state_mapping and "observables" in snapshot:
            state_mapping["observables"] = snapshot.get("observables", {})
        if "rng_state" not in state_mapping and "rng_state" in metadata:
            state_mapping["rng_state"] = metadata.get("rng_state")
        if "params_identity" not in state_mapping:
            state_mapping["params_identity"] = metadata.get("params_hash", params.params_hash)
        if "hessian_sign" in metadata:
            state_mapping["hessian_sign"] = metadata["hessian_sign"]

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

    def get_state(self) -> GRCV3State:
        return self._state

    def set_state(self, state: GRCV3State) -> None:
        if not isinstance(state, GRCV3State):
            raise SnapshotCompatibilityError("state must be a GRCV3State instance")
        self._state = deepcopy(state)

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        claims = set(self.CAPABILITY_PROFILE.required)
        frame_mode = self._params.constitutive_semantic_modes["frame_mode"]
        boundary_mode = self._params.constitutive_semantic_modes["boundary_mode"]
        if frame_mode == "host_embedding":
            claims.add(HOST_EMBEDDING_FRAME)
        else:
            claims.add(INTRINSIC_FRAME)
        if boundary_mode in {"barrier", "ghost"}:
            claims.add(BOUNDARY_BARRIER)
        self.CAPABILITY_PROFILE.validate_claims(claims)
        return claims

    def compute_observables(self) -> ObservableMap:
        observables = dict(self._state.observables)
        observables.setdefault(
            "active_basin_count",
            float(len(self._state.basins) or len(self._state.hierarchy) or len(self._state.nodes)),
        )
        observables.setdefault(
            "max_hierarchy_depth",
            float(
                max((attributes.depth for attributes in self._state.nodes.values()), default=0)
            ),
        )
        geometric_identity = self._state.cached_quantities.get("geometric_identity", {})
        if isinstance(geometric_identity, Mapping):
            geometric_seeds = geometric_identity.get("seed_nodes", [])
            geometric_validated = geometric_identity.get("validated_basin_ids", [])
            if isinstance(geometric_seeds, list | tuple | set | frozenset):
                observables.setdefault(
                    "geometric_seed_count",
                    float(len(geometric_seeds)),
                )
            if isinstance(geometric_validated, list | tuple | set | frozenset):
                observables.setdefault(
                    "geometric_validated_basin_count",
                    float(len(geometric_validated)),
                )
        observables.setdefault(
            "choice_regime_count",
            float(len(self._state.choice_registry)),
        )
        observables.setdefault(
            "collapse_event_count",
            float(len(self._state.collapse_registry)),
        )
        split_registry_raw = self._state.cached_quantities.get("split_registry", {})
        if split_registry_raw in (None, {}):
            split_registry: Mapping[str, Any] = {}
        elif not isinstance(split_registry_raw, Mapping):
            raise SnapshotCompatibilityError("split_registry cache must be a mapping")
        else:
            split_registry = split_registry_raw
        observables.setdefault(
            "active_split_count",
            float(
                sum(
                    1
                    for entry in split_registry.values()
                    if isinstance(entry, Mapping) and not bool(entry.get("complete", False))
                )
            ),
        )
        observables.setdefault(
            "spark_event_count",
            float(sum(1 for event in self._state.event_log if event.kind == "spark")),
        )
        return observables

    def rebuild_basin_attributes(self) -> None:
        """Materialize the Iteration 3 differential-summary baseline."""

        backend_payload = dict(
            self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]
        )
        geometry_payload = dict(backend_payload["geometry"])
        differential_payload = dict(backend_payload["differential_summary"])
        geometry_name = str(geometry_payload["name"])
        differential_name = str(differential_payload["name"])

        if geometry_name != "induced_local_frame":
            raise NotImplementedError(
                "Phase 5 Iteration 3 implements only geometry=induced_local_frame"
            )
        if differential_name != "weighted_least_squares":
            raise NotImplementedError(
                "Phase 5 Iteration 3 implements only "
                "differential_summary=weighted_least_squares"
            )

        dimension = int(dict(geometry_payload.get("params", {})).get("dimension", 2))
        differential_params = dict(differential_payload.get("params", {}))
        regularization = float(differential_params.get("regularization", 1e-9))
        hessian_regularization = float(
            differential_params.get("hessian_regularization", 0.0)
        )

        coherence_by_node = self._coherence_by_node()
        base_conductance = self._base_conductance_by_edge()
        rebuilt_attributes: dict[int, BasinAttributes] = {}

        for node_id in self._state.topology.iter_live_node_ids():
            displacements = induced_local_frame_displacements(
                self._state.topology,
                node_id=node_id,
                base_conductance=base_conductance,
                dimension=dimension,
            )
            neighbor_values = {
                neighbor_id: coherence_by_node.get(neighbor_id, 0.0)
                for neighbor_id in displacements
            }
            weights = self._neighbor_weights(
                node_id=node_id,
                displacements=displacements,
                base_conductance=base_conductance,
            )
            gradient = weighted_least_squares_gradient(
                center_value=coherence_by_node.get(node_id, 0.0),
                displacements=displacements,
                neighbor_values=neighbor_values,
                weights=weights,
                regularization=regularization,
            )
            hessian = weighted_least_squares_hessian(
                center_value=coherence_by_node.get(node_id, 0.0),
                gradient=gradient,
                displacements=displacements,
                neighbor_values=neighbor_values,
                weights=weights,
                regularization=hessian_regularization,
            )
            net_flux = net_flux_summary(
                node_id=node_id,
                graph=self._state.topology,
                flux=self._state.flux,
                displacements=displacements,
                dimension=dimension,
            )
            previous_attributes = self._state.nodes.get(node_id)
            rebuilt_attributes[node_id] = BasinAttributes(
                coherence=coherence_by_node.get(node_id, 0.0),
                gradient=gradient,
                hessian=hessian,
                net_flux=net_flux,
                basin_mass=self._basin_mass_for_node(node_id, coherence_by_node),
                basin_id=(
                    previous_attributes.basin_id
                    if previous_attributes is not None
                    else node_id
                ),
                parent_id=(
                    previous_attributes.parent_id
                    if previous_attributes is not None
                    else None
                ),
                depth=(
                    previous_attributes.depth
                    if previous_attributes is not None
                    else 0
                ),
            )

        current_hessian_sign = self._state.cached_quantities.get("hessian_sign")
        if isinstance(current_hessian_sign, int) and not isinstance(
            current_hessian_sign, bool
        ) and current_hessian_sign in (-1, 1):
            hessian_sign = int(current_hessian_sign)
        else:
            candidate_seed_ids = (
                sorted(self._state.sink_set)
                if self._state.sink_set
                else sorted(rebuilt_attributes)
            )
            gradient_threshold = float(self._params.evolution["eps_gradient"])
            hessian_threshold = float(self._params.evolution["eps_hessian"])
            hessian_sign = calibrate_hessian_sign(
                candidate_seed_ids=candidate_seed_ids,
                basin_attributes=rebuilt_attributes,
                gradient_threshold=gradient_threshold,
                hessian_threshold=hessian_threshold,
            )

        self._state.nodes = rebuilt_attributes
        self._state.cached_quantities["hessian_sign"] = hessian_sign
        self._state.cached_quantities["differential_backend"] = differential_name
        self._state.cached_quantities["geometry_backend"] = geometry_name

    def rebuild_transport_state(self) -> None:
        """Materialize the Iteration 4 tensor, metric, label, potential, and flux state."""

        self._compute_node_tensors()
        self._compute_metric()
        self._compute_edge_labels(pre_flux_only=True)
        self._compute_potential()
        self._compute_flux()
        self._compute_edge_labels(pre_flux_only=False)

    def rebuild_identity_state(self) -> None:
        """Materialize the Iteration 5 identity and hierarchy baseline."""

        self._detect_identities()
        self._validate_geometric_basins()
        self._update_hierarchy_state()

    def rebuild_choice_state(self) -> list[GRCEvent]:
        """Materialize the Iteration 7 optional choice/collapse baseline."""

        choice_selection = self._choice_backend_selection()
        choice_name = str(choice_selection["name"])

        if choice_name == "disabled":
            self._state.choice_registry = {}
            self._state.collapse_registry = {}
            self._state.cached_quantities["choice_state"] = {
                "backend": "disabled",
                "evaluated_nodes": [],
            }
            return []

        if choice_name != "sink_compatibility":
            raise NotImplementedError(
                "Phase 5 Iteration 7 implements only choice=disabled or "
                "choice=sink_compatibility"
            )

        score_params = self._resolved_choice_score_params(choice_selection)
        epsilon_choice = score_params["epsilon_choice"]
        epsilon_collapse = score_params["epsilon_collapse"]
        successor_map = self._successor_map_for_choice()
        sinks = set(self._state.sink_set)
        previous_registry = dict(self._state.choice_registry)
        collapse_registry = dict(self._state.collapse_registry)
        next_registry: dict[str, Any] = {}
        evaluated_nodes: dict[str, Any] = {}
        emitted_events: list[GRCEvent] = []

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            compatibility = self._sink_compatibility_for_node(
                node_id,
                successor_map=successor_map,
                sinks=sinks,
                epsilon_choice=epsilon_choice,
            )
            if compatibility is None:
                continue

            key = str(node_id)
            evaluated_nodes[key] = {
                "scores": dict(compatibility["scores"]),
                "viable_sink_ids": list(compatibility["viable_sink_ids"]),
                "winner_sink_id": compatibility["winner_sink_id"],
                "winner_margin": compatibility["winner_margin"],
                "total_positive_flux": compatibility["total_positive_flux"],
            }
            viable_sink_ids = list(compatibility["viable_sink_ids"])
            previous_entry = previous_registry.get(key)

            if len(viable_sink_ids) >= 2:
                choice_entry = {
                    "backend": choice_name,
                    "node_id": node_id,
                    "viable_sink_ids": viable_sink_ids,
                    "scores": dict(compatibility["scores"]),
                    "winner_sink_id": compatibility["winner_sink_id"],
                    "winner_margin": compatibility["winner_margin"],
                    "total_positive_flux": compatibility["total_positive_flux"],
                    "epsilon_choice": epsilon_choice,
                    "epsilon_collapse": epsilon_collapse,
                }
                next_registry[key] = choice_entry
                if previous_entry != choice_entry:
                    emitted_events.append(
                        GRCEvent(
                            kind="choice_detected",
                            step_index=self._state.step_index,
                            source_family=self.MODEL_FAMILY,
                            payload=dict(choice_entry),
                        )
                    )
                continue

            if (
                previous_entry is not None
                and compatibility["winner_sink_id"] is not None
                and compatibility["winner_margin"] >= epsilon_collapse
            ):
                collapse_entry = {
                    "backend": choice_name,
                    "node_id": node_id,
                    "collapsed_sink_id": compatibility["winner_sink_id"],
                    "scores": dict(compatibility["scores"]),
                    "winner_margin": compatibility["winner_margin"],
                    "total_positive_flux": compatibility["total_positive_flux"],
                    "previous_viable_sink_ids": list(previous_entry.get("viable_sink_ids", [])),
                    "epsilon_choice": epsilon_choice,
                    "epsilon_collapse": epsilon_collapse,
                    "persistence_mode": "registry_only",
                    "collapsed_step_index": self._state.step_index,
                }
                collapse_registry[key] = collapse_entry
                emitted_events.append(
                    GRCEvent(
                        kind="collapse",
                        step_index=self._state.step_index,
                        source_family=self.MODEL_FAMILY,
                        payload=dict(collapse_entry),
                    )
                )
            elif previous_entry is not None:
                resolution_event = GRCEvent(
                    kind="choice_resolved",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={
                        "backend": choice_name,
                        "node_id": node_id,
                        "winner_sink_id": compatibility["winner_sink_id"],
                        "scores": dict(compatibility["scores"]),
                        "winner_margin": compatibility["winner_margin"],
                        "total_positive_flux": compatibility["total_positive_flux"],
                        "previous_viable_sink_ids": list(
                            previous_entry.get("viable_sink_ids", [])
                        ),
                        "epsilon_choice": epsilon_choice,
                        "epsilon_collapse": epsilon_collapse,
                        "resolution_mode": "single_sink_below_collapse_threshold",
                    },
                )
                emitted_events.append(resolution_event)

        self._state.choice_registry = next_registry
        self._state.collapse_registry = collapse_registry
        self._state.cached_quantities["choice_state"] = {
            "backend": choice_name,
            "epsilon_choice": epsilon_choice,
            "epsilon_collapse": epsilon_collapse,
            "evaluated_nodes": evaluated_nodes,
        }
        self._append_events(emitted_events)
        return emitted_events

    def _settlement_regime_payload_for_node(self, node_id: int) -> Mapping[str, Any] | None:
        visited: set[int] = set()
        current_node_id = int(node_id)
        while current_node_id not in visited and self._state.topology.has_node(current_node_id):
            visited.add(current_node_id)
            payload = self._state.topology.node_payload(current_node_id)
            if not isinstance(payload, Mapping):
                return None
            metadata = payload.get("metadata")
            if isinstance(metadata, Mapping):
                source_extensions = metadata.get("source_extensions")
                if isinstance(source_extensions, Mapping):
                    grcv3_extension = source_extensions.get("grcv3")
                    if isinstance(grcv3_extension, Mapping):
                        settlement_regime = grcv3_extension.get("settlement_regime")
                        if isinstance(settlement_regime, Mapping):
                            return settlement_regime
            parent_node_id = payload.get("parent_node_id")
            if not isinstance(parent_node_id, int):
                return None
            current_node_id = int(parent_node_id)
        return None

    def _settlement_regime_initial_locus_class_for_node(self, node_id: int) -> str | None:
        settlement_regime = self._settlement_regime_payload_for_node(node_id)
        if not isinstance(settlement_regime, Mapping):
            return None
        initial_locus_class = settlement_regime.get("initial_locus_class")
        if isinstance(initial_locus_class, str) and initial_locus_class.strip():
            return initial_locus_class.strip()
        regime_class = settlement_regime.get("regime_class")
        implied_mapping = {
            "carrier_site_regime": "carrier_site",
            "path_node_regime": "path_node",
        }
        if isinstance(regime_class, str):
            return implied_mapping.get(regime_class.strip())
        return None

    def _settlement_regime_split_inheritance_mode_for_node(
        self,
        node_id: int,
    ) -> str | None:
        settlement_regime = self._settlement_regime_payload_for_node(node_id)
        if not isinstance(settlement_regime, Mapping):
            return None
        split_inheritance_mode = settlement_regime.get("split_inheritance_mode")
        if isinstance(split_inheritance_mode, str) and split_inheritance_mode.strip():
            return split_inheritance_mode.strip()
        regime_class = settlement_regime.get("regime_class")
        implied_mapping = {
            "carrier_site_regime": "anchored",
            "path_node_regime": "split_child_inheriting",
        }
        if isinstance(regime_class, str):
            return implied_mapping.get(regime_class.strip())
        return None

    def _node_is_eligible_for_settlement_regime(self, node_id: int) -> bool:
        initial_locus_class = self._settlement_regime_initial_locus_class_for_node(node_id)
        split_inheritance_mode = self._settlement_regime_split_inheritance_mode_for_node(
            node_id
        )
        if initial_locus_class is None and split_inheritance_mode is None:
            return True
        payload = self._state.topology.node_payload(node_id)
        if not isinstance(payload, Mapping):
            return False
        motif_role = payload.get("motif_role")
        kind = payload.get("kind")
        if kind == "split_child":
            return split_inheritance_mode == "split_child_inheriting"
        if initial_locus_class == "carrier_site":
            return motif_role == "basin_load_carrier"
        if initial_locus_class == "path_node":
            return motif_role == "basin_transfer_path_node"
        return True

    def detect_spark_candidates(self) -> list[GRCEvent]:
        """Detect Iteration 6 spark candidates without applying topology changes."""

        backend_payload = dict(
            self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]
        )
        spark_payload = dict(backend_payload["spark"])
        spark_name = str(spark_payload["name"])
        if spark_name != "signed_hessian_plus_attractor_delta":
            raise NotImplementedError(
                "Phase 5 Iteration 6 implements only "
                "spark=signed_hessian_plus_attractor_delta"
            )

        hessian_sign = self._state.cached_quantities.get("hessian_sign")
        if hessian_sign not in (-1, 1):
            raise SnapshotCompatibilityError(
                "GRCV3 spark detection requires a calibrated hessian_sign"
            )

        geometric_identity = self._state.cached_quantities.get("geometric_identity", {})
        if not isinstance(geometric_identity, Mapping):
            raise SnapshotCompatibilityError(
                "GRCV3 spark detection requires geometric identity diagnostics"
            )

        seed_nodes_raw = geometric_identity.get("seed_nodes", [])
        if not isinstance(seed_nodes_raw, (list, tuple, set, frozenset)):
            raise SnapshotCompatibilityError("geometric_identity.seed_nodes must be sequence-like")
        seed_nodes = {int(node_id) for node_id in seed_nodes_raw}
        basin_representatives = {
            node_id
            for node_id in sorted(self._state.topology.iter_live_node_ids())
            if self._require_basin_attributes(node_id).basin_id == node_id
        }
        interior_candidates = seed_nodes | basin_representatives
        eps_gradient = float(self._params.evolution["eps_gradient"])
        eps_hessian = float(self._params.evolution["eps_hessian"])
        eps_spark = float(self._params.evolution["eps_spark"])
        active_parent_ids = self._active_split_parent_ids()

        candidates: list[GRCEvent] = []
        for node_id in sorted(interior_candidates):
            if node_id in active_parent_ids:
                continue
            if not self._node_is_eligible_for_settlement_regime(node_id):
                continue
            attributes = self._require_basin_attributes(node_id)
            gradient_norm = math.sqrt(sum(value * value for value in attributes.gradient))
            if gradient_norm >= eps_gradient:
                continue
            signed_hessian = [
                [float(hessian_sign) * float(value) for value in row]
                for row in attributes.hessian
            ]
            eigenvalues = symmetric_eigenvalues(signed_hessian) if signed_hessian else []
            if not eigenvalues:
                continue
            ordered = sorted(float(value) for value in eigenvalues)
            if ordered[0] >= eps_spark:
                continue
            if any(value <= eps_hessian for value in ordered[1:]):
                continue
            candidate_rank = len(candidates)
            candidates.append(
                GRCEvent(
                    kind="spark_candidate",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={
                        "backend": spark_name,
                        "node_id": node_id,
                        "basin_id": attributes.basin_id,
                        "gradient_norm": gradient_norm,
                        "signed_eigenvalues": ordered,
                        "epsilon_gradient": eps_gradient,
                        "epsilon_hessian": eps_hessian,
                        "epsilon_spark": eps_spark,
                        "candidate_rank": candidate_rank,
                        "weak_axis_index": self._weakest_curvature_axis(node_id),
                    },
                )
            )
        return candidates

    def apply_spark_candidates(self, candidates: list[GRCEvent]) -> list[GRCEvent]:
        """Apply candidate sparks through soft split and attractor-delta confirmation."""

        emitted_events: list[GRCEvent] = []
        for event in candidates:
            if event.kind != "spark_candidate":
                continue
            split_events = self._initialize_split_from_candidate(event)
            emitted_events.extend(split_events)
            if not split_events:
                continue
            self._refresh_after_topology_change()
            emitted_events.extend(self._evaluate_split_completion())

        self._append_events(emitted_events)
        return emitted_events

    def advance_split_state(self) -> list[GRCEvent]:
        """Advance any active soft splits by one deterministic progress step."""

        split_registry = self._split_registry()
        if not split_registry:
            return []
        total_steps = max(
            1,
            int(math.ceil(float(self._params.evolution["tau_split"]))),
        )
        emitted_events: list[GRCEvent] = []
        for registry_key in sorted(split_registry):
            entry = split_registry[registry_key]
            if not isinstance(entry, Mapping):
                continue
            if bool(entry.get("complete", False)):
                continue
            parent_node_id = int(entry["parent_node_id"])
            progress_step = int(entry.get("progress_step", 0)) + 1
            fraction = min(1.0, progress_step / total_steps)
            initial_weight = float(entry.get("initial_edge_weight", 1e-6))

            for edge_info in entry.get("parent_edge_targets", []):
                edge_id = int(edge_info["edge_id"])
                initial_parent_weight = float(edge_info["initial_weight"])
                target_weight = float(edge_info["target_weight"])
                self._state.base_conductance[edge_id] = initial_parent_weight + fraction * (
                    target_weight - initial_parent_weight
                )

            for edge_info in entry.get("child_edge_targets", []):
                edge_id = int(edge_info["edge_id"])
                target_weight = float(edge_info["target_weight"])
                self._state.base_conductance[edge_id] = initial_weight + fraction * (
                    target_weight - initial_weight
                )

            for edge_id in entry.get("split_link_edge_ids", []):
                edge_id_int = int(edge_id)
                target_weight = float(entry.get("split_link_target_weight", initial_weight))
                self._state.base_conductance[edge_id_int] = initial_weight + fraction * (
                    target_weight - initial_weight
                )

            if isinstance(entry, dict):
                entry["progress_step"] = progress_step
                entry["progress_fraction"] = fraction
            emitted_events.append(
                GRCEvent(
                    kind="split_progress",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={
                        "registry_key": registry_key,
                        "parent_node_id": parent_node_id,
                        "child_node_ids": list(entry.get("child_node_ids", [])),
                        "progress_step": progress_step,
                        "progress_fraction": fraction,
                    },
                )
            )

            if fraction >= 1.0:
                if self._state.topology.has_node(parent_node_id):
                    self._state.topology.remove_node(parent_node_id)
                self._cleanup_state_against_live_topology()
                if isinstance(entry, dict):
                    entry["complete"] = True
                    entry["parent_removed"] = True
                emitted_events.append(
                    GRCEvent(
                        kind="split_complete",
                        step_index=self._state.step_index,
                        source_family=self.MODEL_FAMILY,
                        payload={
                            "registry_key": registry_key,
                            "parent_node_id": parent_node_id,
                            "child_node_ids": list(entry.get("child_node_ids", [])),
                        },
                    )
                )

        self._refresh_after_topology_change()
        emitted_events.extend(self._evaluate_split_completion())
        self._append_events(emitted_events)
        return emitted_events

    def rebuild_spark_state(self) -> list[GRCEvent]:
        """Detect and apply the Iteration 6 spark baseline."""

        candidates = self.detect_spark_candidates()
        self._append_events(candidates)
        applied = self.apply_spark_candidates(candidates)
        return [*candidates, *applied]

    def _compute_node_tensors(self) -> None:
        lambda_c = float(self._params.evolution["lambda_c"])
        xi_c = float(self._params.evolution["xi_c"])
        zeta_c = float(self._params.evolution["zeta_c"])
        dimension = self._geometry_dimension()
        node_tensors: dict[int, dict[str, Any]] = {}

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            attributes = self._require_basin_attributes(node_id)
            gradient = _pad_vector(attributes.gradient, dimension=dimension)
            net_flux = _pad_vector(attributes.net_flux, dimension=dimension)

            tensor = _zero_matrix(dimension)
            _matrix_add_scaled(tensor, _identity_matrix(dimension), scale=lambda_c * attributes.coherence)
            _matrix_add_scaled(tensor, _outer_product(gradient), scale=xi_c)
            _matrix_add_scaled(tensor, _outer_product(net_flux), scale=zeta_c)

            node_tensors[node_id] = {
                "matrix": tensor,
                "trace": float(sum(tensor[index][index] for index in range(dimension))),
                "dimension": dimension,
                "coherence": float(attributes.coherence),
                "gradient_norm_squared": float(sum(value * value for value in gradient)),
                "net_flux_norm_squared": float(sum(value * value for value in net_flux)),
            }

        self._state.cached_quantities["node_tensors"] = node_tensors
        self._state.cached_quantities["metric_backend"] = "tensor_exponential"

    def _compute_metric(self) -> None:
        alpha = float(self._params.evolution["alpha"])
        beta = float(self._params.evolution["beta"])
        gamma = float(self._params.evolution["gamma"])
        delta = float(self._params.evolution["delta"])
        coherence_by_node = self._coherence_by_node()
        reference_edge_weights = self._base_conductance_by_edge()
        edge_curvature: dict[int, float] = {}
        updated_conductance: dict[int, float] = {}

        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            coherence_a = float(coherence_by_node.get(node_a, 0.0))
            coherence_b = float(coherence_by_node.get(node_b, 0.0))
            gradient_a = self._require_basin_attributes(node_a).gradient
            gradient_b = self._require_basin_attributes(node_b).gradient
            gradient_gap_squared = self._squared_vector_gap(gradient_a, gradient_b)
            previous_flux = self._signed_edge_flux(edge_id)
            ricci = self._edge_curvature_term(
                edge_id=edge_id,
                node_a=node_a,
                node_b=node_b,
                edge_weights=reference_edge_weights,
            )
            exponent = (
                -alpha * (coherence_a + coherence_b) / 2.0
                -beta * gradient_gap_squared / 2.0
                -gamma * (previous_flux ** 2) / 2.0
                -delta * ricci
            )
            updated_conductance[edge_id] = max(1e-12, float(math.exp(exponent)))
            edge_curvature[edge_id] = float(ricci)

        self._state.base_conductance = updated_conductance
        self._state.cached_quantities["edge_curvature"] = edge_curvature

    def _compute_edge_labels(self, *, pre_flux_only: bool) -> None:
        selected_labels = self._selected_edge_labels()
        live_edge_ids = tuple(sorted(self._state.topology.iter_live_edge_ids()))
        if not pre_flux_only:
            self._state.flux_coupling = {}
            self._state.temporal_delay = {}
        if pre_flux_only:
            self._state.geometric_length = {}

        edge_label_computation_mode = dict(self._state.edge_label_computation_mode)
        edge_label_params = dict(self._state.edge_label_params)
        edge_label_params["selection"] = (
            "all"
            if self._params.constitutive_semantic_modes["edge_label_selection"] == "all"
            else tuple(sorted(selected_labels))
        )

        if pre_flux_only and "geometric_length" in selected_labels:
            geometric_mode = self._geometric_length_mode_for_state()
            edge_label_computation_mode["geometric_length"] = geometric_mode
            edge_label_params["geometric_length"] = self._geometric_length_params(geometric_mode)
            for edge_id in live_edge_ids:
                self._state.geometric_length[edge_id] = self._compute_geometric_length(
                    edge_id,
                    mode=geometric_mode,
                )

        if not pre_flux_only and "flux_coupling" in selected_labels:
            edge_label_computation_mode["flux_coupling"] = "absolute_flux"
            edge_label_params["flux_coupling"] = {"mode": "absolute_flux"}
            for edge_id in live_edge_ids:
                self._state.flux_coupling[edge_id] = abs(self._signed_edge_flux(edge_id))

        if not pre_flux_only and "temporal_delay" in selected_labels:
            if "geometric_length" in selected_labels:
                geometric_mode = edge_label_computation_mode.get(
                    "geometric_length",
                    self._geometric_length_mode_for_state(),
                )
                geometric_lengths = dict(self._state.geometric_length)
            else:
                geometric_mode = self._geometric_length_mode_for_state()
                geometric_lengths = {
                    edge_id: self._compute_geometric_length(edge_id, mode=geometric_mode)
                    for edge_id in live_edge_ids
                }
            temporal_params = dict(self._params.evolution["temporal_label_params"])
            v0 = float(temporal_params["v0"])
            rho = float(temporal_params["rho"])
            eps_tau = float(temporal_params["eps_tau"])
            edge_label_computation_mode["temporal_delay"] = "transport_ratio"
            edge_label_params["temporal_delay"] = {
                "mode": "transport_ratio",
                "v0": v0,
                "rho": rho,
                "eps_tau": eps_tau,
                "geometric_length_mode": geometric_mode,
            }
            for edge_id in live_edge_ids:
                flux_coupling = self._state.flux_coupling.get(edge_id, abs(self._signed_edge_flux(edge_id)))
                self._state.temporal_delay[edge_id] = geometric_lengths[edge_id] / (
                    v0 + rho * flux_coupling + eps_tau
                )

        self._state.edge_label_computation_mode = edge_label_computation_mode
        self._state.edge_label_params = edge_label_params
        self._state.cached_quantities["edge_label_computation_mode"] = dict(
            edge_label_computation_mode
        )
        self._state.cached_quantities["edge_label_params"] = dict(edge_label_params)

    def _compute_potential(self) -> None:
        kappa_c = float(self._params.evolution["kappa_c"])
        selection = self._params.evolution["site_potential_selection"]
        params = self._params.evolution["site_potential_params"]
        coherence_by_node = self._coherence_by_node()
        potential: dict[int, float] = {}

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            coherence = float(coherence_by_node.get(node_id, 0.0))
            interaction_term = 0.0
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                interaction_term += float(self._state.base_conductance.get(edge_id, 1.0)) * (
                    coherence - float(coherence_by_node.get(neighbor_id, 0.0))
                )
            potential[node_id] = (
                kappa_c * interaction_term
                - self._site_potential_derivative(
                    coherence=coherence,
                    selection=selection,
                    params=params,
                )
            )
        self._state.potential = potential

    def _compute_flux(self) -> None:
        eta = float(self._params.evolution["eta"])
        flux: dict[OrientedEdgeId, float] = {}
        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            potential_a = float(self._state.potential.get(node_a, 0.0))
            potential_b = float(self._state.potential.get(node_b, 0.0))
            conductance = float(self._state.base_conductance.get(edge_id, 1.0))
            flux_value = -eta * conductance * (potential_a - potential_b)
            flux[(edge_id, node_a)] = flux_value
            flux[(edge_id, node_b)] = -flux_value
        self._state.flux = flux

    def _detect_identities(self) -> None:
        sinks: set[int] = set()
        basins: dict[int, set[int]] = {}
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        successor_map: dict[int, int | None] = {node_id: None for node_id in live_node_ids}

        for node_id in live_node_ids:
            total_incoming_flux = 0.0
            violates_sink_inflow_condition = False
            outgoing_candidates: list[tuple[float, int, int]] = []
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                outgoing_flux = float(self._state.flux.get((edge_id, node_id), 0.0))
                incoming_flux = float(self._state.flux.get((edge_id, neighbor_id), 0.0))
                if outgoing_flux > 0.0:
                    outgoing_candidates.append((outgoing_flux, neighbor_id, edge_id))
                if incoming_flux < 0.0:
                    violates_sink_inflow_condition = True
                    break
                total_incoming_flux += incoming_flux
            if not violates_sink_inflow_condition and total_incoming_flux > 0.0:
                sinks.add(node_id)
            if outgoing_candidates:
                outgoing_candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
                successor_map[node_id] = outgoing_candidates[0][1]

        for origin_node_id in live_node_ids:
            reached_sink = self._reachable_sink(origin_node_id, successor_map, sinks)
            if reached_sink is not None:
                basins.setdefault(reached_sink, set()).add(origin_node_id)

        self._state.sink_set = sinks
        self._state.basins = basins
        self._state.cached_quantities["successor_map"] = dict(sorted(successor_map.items()))
        self._state.cached_quantities["flux_identity"] = {
            "sink_nodes": sorted(sinks),
            "basins": {
                str(node_id): sorted(members) for node_id, members in sorted(basins.items())
            },
            "successor_map": {
                str(node_id): successor_map[node_id]
                for node_id in sorted(successor_map)
            },
        }

    def _validate_geometric_basins(self) -> None:
        hessian_sign = self._state.cached_quantities.get("hessian_sign")
        if hessian_sign not in (-1, 1):
            raise SnapshotCompatibilityError(
                "GRCV3 geometric identity validation requires a serialized hessian_sign"
            )

        gradient_threshold = float(self._params.evolution["eps_gradient"])
        hessian_threshold = float(self._params.evolution["eps_hessian"])

        geometric_seed_nodes: set[int] = set()
        min_signed_eigenvalue_by_node: dict[int, float] = {}
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            attributes = self._require_basin_attributes(node_id)
            gradient_norm = math.sqrt(sum(value * value for value in attributes.gradient))
            signed_hessian = [
                [float(hessian_sign) * float(value) for value in row]
                for row in attributes.hessian
            ]
            eigenvalues = symmetric_eigenvalues(signed_hessian) if signed_hessian else []
            min_signed = min(eigenvalues) if eigenvalues else float("-inf")
            min_signed_eigenvalue_by_node[node_id] = float(min_signed)
            if gradient_norm < gradient_threshold and min_signed > hessian_threshold:
                geometric_seed_nodes.add(node_id)

        validated_basin_ids: set[str | int] = set()
        basin_seed_nodes: dict[int, list[int]] = {}
        seed_to_flux_sink: dict[int, int | None] = {}
        geometric_basin_members: dict[str | int, set[int]] = {}
        basin_id_by_node: dict[int, str | int] = {}

        for sink_node_id in sorted(self._state.basins):
            members = set(self._state.basins[sink_node_id])
            seed_nodes = sorted(node_id for node_id in members if node_id in geometric_seed_nodes)
            basin_seed_nodes[sink_node_id] = seed_nodes
            for seed_node_id in seed_nodes:
                seed_to_flux_sink[seed_node_id] = sink_node_id
            if len(seed_nodes) == 1:
                basin_id: str | int = seed_nodes[0]
                validated_basin_ids.add(basin_id)
            else:
                basin_id = sink_node_id
            geometric_basin_members[basin_id] = set(sorted(members))
            for member_id in sorted(members):
                basin_id_by_node[member_id] = basin_id

        unassigned_seed_nodes = sorted(
            node_id for node_id in geometric_seed_nodes if node_id not in basin_id_by_node
        )
        for node_id in unassigned_seed_nodes:
            validated_basin_ids.add(node_id)
            geometric_basin_members[node_id] = {node_id}
            basin_id_by_node[node_id] = node_id

        active_split_child_ids = self._active_split_child_ids()
        for child_node_id in sorted(active_split_child_ids):
            for basin_members in geometric_basin_members.values():
                basin_members.discard(child_node_id)
            validated_basin_ids.add(child_node_id)
            geometric_basin_members[child_node_id] = {child_node_id}
            basin_id_by_node[child_node_id] = child_node_id

        geometric_basin_members = {
            basin_id: members
            for basin_id, members in geometric_basin_members.items()
            if members
        }

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            basin_id_by_node.setdefault(node_id, node_id)

        self._state.cached_quantities["geometric_identity"] = {
            "seed_nodes": sorted(geometric_seed_nodes),
            "min_signed_eigenvalue_by_node": {
                str(node_id): min_signed_eigenvalue_by_node[node_id]
                for node_id in sorted(min_signed_eigenvalue_by_node)
            },
            "validated_basin_ids": sorted(validated_basin_ids, key=str),
            "basin_seed_nodes": {
                str(sink_node_id): list(seed_nodes)
                for sink_node_id, seed_nodes in sorted(basin_seed_nodes.items())
            },
            "seed_to_flux_sink": {
                str(seed_node_id): seed_to_flux_sink[seed_node_id]
                for seed_node_id in sorted(seed_to_flux_sink)
            },
            "basin_id_by_node": {
                str(node_id): basin_id_by_node[node_id]
                for node_id in sorted(basin_id_by_node)
            },
            "geometric_basins": {
                str(basin_id): sorted(members)
                for basin_id, members in sorted(
                    geometric_basin_members.items(),
                    key=lambda item: str(item[0]),
                )
            },
        }

    def _update_hierarchy_state(self) -> None:
        backend_payload = dict(
            self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]
        )
        hierarchy_payload = dict(backend_payload["hierarchy_update"])
        if str(hierarchy_payload["name"]) != "basin_parent_child":
            raise NotImplementedError(
                "Phase 5 Iteration 5 implements only hierarchy_update=basin_parent_child"
            )

        geometric_identity = self._state.cached_quantities.get("geometric_identity", {})
        basin_id_by_node_raw = (
            dict(geometric_identity.get("basin_id_by_node", {}))
            if isinstance(geometric_identity, Mapping)
            else {}
        )

        updated_nodes: dict[int, BasinAttributes] = {}
        hierarchy_children: dict[str | int, set[str | int]] = {}
        hierarchy_roots: set[str | int] = set()
        child_basin_ids: set[str | int] = set()
        explicit_parent_ids: set[str | int] = set()
        coherence_by_node = self._coherence_by_node()

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            attributes = self._require_basin_attributes(node_id)
            if node_id in basin_id_by_node_raw:
                basin_id = basin_id_by_node_raw[node_id]
            elif str(node_id) in basin_id_by_node_raw:
                basin_id = basin_id_by_node_raw[str(node_id)]
            else:
                basin_id = attributes.basin_id if attributes.basin_id is not None else node_id

            parent_id = attributes.parent_id
            depth = int(attributes.depth)

            updated_nodes[node_id] = BasinAttributes(
                coherence=attributes.coherence,
                gradient=list(attributes.gradient),
                hessian=[list(row) for row in attributes.hessian],
                net_flux=list(attributes.net_flux),
                basin_mass=self._basin_mass_for_node(node_id, coherence_by_node),
                basin_id=basin_id,
                parent_id=parent_id,
                depth=depth,
            )
            if parent_id is None:
                hierarchy_roots.add(basin_id)
                hierarchy_children.setdefault(basin_id, set())
            else:
                explicit_parent_ids.add(parent_id)
                child_basin_ids.add(basin_id)
                hierarchy_children.setdefault(parent_id, set()).add(basin_id)
                hierarchy_children.setdefault(basin_id, set())

        for parent_id in sorted(explicit_parent_ids, key=str):
            if parent_id not in child_basin_ids:
                hierarchy_roots.add(parent_id)
            hierarchy_children.setdefault(parent_id, set())

        self._state.nodes = updated_nodes
        self._state.hierarchy = {
            key: sorted(children, key=str)
            for key, children in sorted(hierarchy_children.items(), key=lambda item: str(item[0]))
        }
        self._state.cached_quantities["hierarchy_roots"] = sorted(hierarchy_roots, key=str)
        self._state.cached_quantities["hierarchy_backend"] = "basin_parent_child"

    def _min_child_basins(self) -> int:
        backend_payload = dict(
            self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]
        )
        spark_payload = dict(backend_payload["spark"])
        spark_params = dict(spark_payload.get("params", {}))
        return max(1, int(spark_params.get("min_child_basins", 1)))

    def _selected_edge_labels(self) -> set[str]:
        selection = self._params.constitutive_semantic_modes["edge_label_selection"]
        if selection == "all":
            return set(_ALLOWED_EDGE_LABELS)
        return {str(value) for value in selection}

    def _geometry_dimension(self) -> int:
        backend_payload = dict(
            self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]
        )
        geometry_payload = dict(backend_payload["geometry"])
        geometry_params = dict(geometry_payload.get("params", {}))
        return max(1, int(geometry_params.get("dimension", 2)))

    def _require_basin_attributes(self, node_id: int) -> BasinAttributes:
        attributes = self._state.nodes.get(node_id)
        if attributes is None:
            raise SnapshotCompatibilityError(
                f"GRCV3 node {node_id} is missing basin attributes"
            )
        return attributes

    def _node_tensor_matrix(self, node_id: int) -> list[list[float]]:
        node_tensors = self._state.cached_quantities.get("node_tensors")
        if not isinstance(node_tensors, Mapping) or node_id not in node_tensors:
            raise SnapshotCompatibilityError(
                "GRCV3 node tensors are not materialized; call rebuild_transport_state() first"
            )
        entry = node_tensors[node_id]
        if not isinstance(entry, Mapping):
            raise SnapshotCompatibilityError("node tensor entry must be a mapping")
        matrix = entry.get("matrix")
        if not isinstance(matrix, list):
            raise SnapshotCompatibilityError("node tensor matrix must be a matrix")
        restored: list[list[float]] = []
        for row_index, row in enumerate(matrix):
            if not isinstance(row, list):
                raise SnapshotCompatibilityError(
                    f"node tensor row {row_index} must be a list"
                )
            restored.append(
                [_as_runtime_float(value, context=f"node tensor row {row_index}") for value in row]
            )
        return restored

    def _squared_vector_gap(self, left: list[float], right: list[float]) -> float:
        dimension = max(len(left), len(right), 1)
        left_padded = _pad_vector(left, dimension=dimension)
        right_padded = _pad_vector(right, dimension=dimension)
        return float(
            sum((left_value - right_value) ** 2 for left_value, right_value in zip(left_padded, right_padded, strict=True))
        )

    def _signed_edge_flux(self, edge_id: int) -> float:
        node_a, node_b = self._state.topology.edge_endpoints(edge_id)
        primary_node = min(node_a, node_b)
        return float(self._state.flux.get((edge_id, primary_node), 0.0))

    def _geometric_length_mode_for_state(self) -> str:
        frame_mode = self._params.constitutive_semantic_modes["frame_mode"]
        if frame_mode == "induced_local_frame":
            return "induced_intrinsic"
        if frame_mode == "host_embedding" and self._host_geometry_complete():
            return "ambient_metric"
        return "intrinsic_surrogate"

    def _host_geometry_complete(self) -> bool:
        for edge_id in self._state.topology.iter_live_edge_ids():
            if self._ambient_edge_length(edge_id) is None:
                return False
        return True

    def _geometric_length_params(self, mode: str) -> dict[str, Any]:
        if mode == "ambient_metric":
            fields = sorted(
                str(value)
                for value in self._params.constitutive_semantic_modes.get(
                    "host_geometry_fields",
                    (),
                )
            )
            return {"mode": mode, "host_geometry_fields": fields}
        if mode == "induced_intrinsic":
            return {"mode": mode, "source": "local_tensor_quadratic_form"}
        return {"mode": mode, "source": "inverse_base_conductance"}

    def _compute_geometric_length(self, edge_id: int, *, mode: str) -> float:
        if mode == "ambient_metric":
            ambient = self._ambient_edge_length(edge_id)
            if ambient is not None:
                return max(1e-12, ambient)
        if mode == "induced_intrinsic":
            intrinsic = self._intrinsic_edge_length(edge_id)
            if intrinsic is not None:
                return max(1e-12, intrinsic)
        conductance = float(self._state.base_conductance.get(edge_id, 1.0))
        return max(1e-12, 1.0 / (conductance + 1e-12))

    def _ambient_edge_length(self, edge_id: int) -> float | None:
        edge_payload = self._state.topology.edge_payload(edge_id)
        raw_ambient_length = edge_payload.get("ambient_length")
        if raw_ambient_length is not None:
            return _as_runtime_float(raw_ambient_length, context="ambient_length")

        fields = self._params.constitutive_semantic_modes.get("host_geometry_fields", ())
        node_a, node_b = self._state.topology.edge_endpoints(edge_id)
        payload_a = self._state.topology.node_payload(node_a)
        payload_b = self._state.topology.node_payload(node_b)
        for field_name in fields:
            coordinates_a = _restore_coordinate_vector(
                payload_a.get(field_name),
                context=f"node[{node_a}].{field_name}",
            )
            coordinates_b = _restore_coordinate_vector(
                payload_b.get(field_name),
                context=f"node[{node_b}].{field_name}",
            )
            if coordinates_a is None or coordinates_b is None:
                continue
            return _euclidean_distance(coordinates_a, coordinates_b)
        return None

    def _intrinsic_edge_length(self, edge_id: int) -> float | None:
        node_a, node_b = self._state.topology.edge_endpoints(edge_id)
        dimension = self._geometry_dimension()
        displacements_a = induced_local_frame_displacements(
            self._state.topology,
            node_id=node_a,
            base_conductance=self._state.base_conductance,
            dimension=dimension,
        )
        displacements_b = induced_local_frame_displacements(
            self._state.topology,
            node_id=node_b,
            base_conductance=self._state.base_conductance,
            dimension=dimension,
        )
        tensor_average = _matrix_average(
            self._node_tensor_matrix(node_a),
            self._node_tensor_matrix(node_b),
        )
        candidates: list[float] = []
        for displacement in (
            displacements_a.get(node_b),
            displacements_b.get(node_a),
        ):
            if displacement is None:
                continue
            quadratic = _quadratic_form(tensor_average, displacement)
            candidates.append(math.sqrt(max(quadratic, 1e-12)))
        if not candidates:
            return None
        return float(sum(candidates) / len(candidates))

    def _edge_curvature_term(
        self,
        *,
        edge_id: int,
        node_a: int,
        node_b: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        backend = self._params.constitutive_semantic_modes["curvature_backend"]
        if backend == "none":
            return 0.0
        if backend == "forman":
            return self._forman_ricci_edge_curvature(
                edge_id=edge_id,
                node_a=node_a,
                node_b=node_b,
                edge_weights=edge_weights,
            )
        if backend == "ollivier":
            return self._ollivier_ricci_edge_curvature(
                edge_id=edge_id,
                node_a=node_a,
                node_b=node_b,
                edge_weights=edge_weights,
            )
        raise SnapshotCompatibilityError(f"unsupported curvature_backend {backend!r}")

    def _current_edge_weight(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        if edge_weights is not None and edge_id in edge_weights:
            return float(edge_weights[edge_id])
        return float(self._state.base_conductance.get(edge_id, 1.0))

    def _weakest_curvature_axis(self, node_id: int) -> int:
        attributes = self._require_basin_attributes(node_id)
        hessian_sign = int(self._state.cached_quantities.get("hessian_sign", 1))
        signed_hessian = [
            [hessian_sign * float(value) for value in row]
            for row in attributes.hessian
        ]
        if not signed_hessian:
            return 0
        diagonal = [
            float(signed_hessian[index][index])
            for index in range(min(len(signed_hessian), len(signed_hessian[0])))
        ]
        if not diagonal:
            return 0
        return min(range(len(diagonal)), key=lambda index: (diagonal[index], index))

    def _current_node_weight(self, node_id: int) -> float:
        return max(float(self._coherence_by_node().get(node_id, 0.0)), 1e-12)

    def _edge_length_cost(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        return 1.0 / max(self._current_edge_weight(edge_id, edge_weights=edge_weights), 1e-12)

    def _neighbor_measure(
        self,
        node_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> dict[int, float]:
        weights: dict[int, float] = {}
        total = 0.0
        for edge_id in self._state.topology.incident_edge_ids(node_id):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == node_id else node_a
            weight = self._current_edge_weight(edge_id, edge_weights=edge_weights)
            weights[neighbor_id] = weights.get(neighbor_id, 0.0) + weight
            total += weight
        if total <= 0.0:
            return {}
        return {neighbor_id: weight / total for neighbor_id, weight in sorted(weights.items())}

    def _earth_movers_distance(
        self,
        left_measure: Mapping[int, float],
        right_measure: Mapping[int, float],
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        support = sorted(set(left_measure) | set(right_measure))
        distance = 0.0
        for node_id in support:
            left_mass = float(left_measure.get(node_id, 0.0))
            right_mass = float(right_measure.get(node_id, 0.0))
            distance += abs(left_mass - right_mass)
        return distance / 2.0

    def _forman_ricci_edge_curvature(
        self,
        *,
        edge_id: int,
        node_a: int,
        node_b: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        edge_weight = self._current_edge_weight(edge_id, edge_weights=edge_weights)
        node_a_weight = self._current_node_weight(node_a)
        node_b_weight = self._current_node_weight(node_b)
        node_a_term = node_a_weight / edge_weight
        node_b_term = node_b_weight / edge_weight
        adjacent_a_term = 0.0
        adjacent_b_term = 0.0
        for adjacent_edge_id in self._state.topology.incident_edge_ids(node_a):
            if adjacent_edge_id == edge_id:
                continue
            adjacent_a_term += node_a_weight / math.sqrt(
                edge_weight * self._current_edge_weight(adjacent_edge_id, edge_weights=edge_weights)
            )
        for adjacent_edge_id in self._state.topology.incident_edge_ids(node_b):
            if adjacent_edge_id == edge_id:
                continue
            adjacent_b_term += node_b_weight / math.sqrt(
                edge_weight * self._current_edge_weight(adjacent_edge_id, edge_weights=edge_weights)
            )
        return float(
            edge_weight * (node_a_term + node_b_term - adjacent_a_term - adjacent_b_term)
        )

    def _ollivier_ricci_edge_curvature(
        self,
        *,
        edge_id: int,
        node_a: int,
        node_b: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        edge_distance = self._edge_length_cost(edge_id, edge_weights=edge_weights)
        if edge_distance <= 0.0:
            raise SnapshotCompatibilityError("edge distance must remain positive")
        transport_cost = self._earth_movers_distance(
            self._neighbor_measure(node_a, edge_weights=edge_weights),
            self._neighbor_measure(node_b, edge_weights=edge_weights),
            edge_weights=edge_weights,
        )
        return float(1.0 - transport_cost / edge_distance)

    def _site_potential_derivative(
        self,
        *,
        coherence: float,
        selection: Any,
        params: Any,
    ) -> float:
        if not isinstance(selection, str):
            raise SnapshotCompatibilityError("site_potential_selection must be a string")
        if not isinstance(params, Mapping):
            raise SnapshotCompatibilityError("site_potential_params must be a mapping")

        if selection == "quadratic":
            mu = _as_runtime_float(params.get("mu", 0.0), context="site_potential_params.mu")
            scale = _as_runtime_float(
                params.get("scale", 1.0),
                context="site_potential_params.scale",
            )
            return 2.0 * scale * coherence + mu
        if selection == "linear":
            bias = _as_runtime_float(
                params.get("bias", 0.0),
                context="site_potential_params.bias",
            )
            scale = _as_runtime_float(
                params.get("scale", 1.0),
                context="site_potential_params.scale",
            )
            return scale + bias
        raise SnapshotCompatibilityError(
            f"unsupported site_potential_selection {selection!r}"
        )

    def _coherence_by_node(self) -> dict[int, float]:
        coherence_by_node: dict[int, float] = {}
        for node_id in self._state.topology.iter_live_node_ids():
            attributes = self._state.nodes.get(node_id)
            if attributes is not None:
                coherence_by_node[node_id] = float(attributes.coherence)
                continue
            payload = self._state.topology.node_payload(node_id)
            raw_coherence = payload.get("coherence", 0.0)
            coherence_by_node[node_id] = float(raw_coherence) if isinstance(
                raw_coherence, int | float
            ) and not isinstance(raw_coherence, bool) else 0.0
        return coherence_by_node

    def _base_conductance_by_edge(self) -> dict[int, float]:
        conductance_by_edge: dict[int, float] = {}
        for edge_id in self._state.topology.iter_live_edge_ids():
            if edge_id in self._state.base_conductance:
                conductance_by_edge[edge_id] = float(
                    self._state.base_conductance[edge_id]
                )
                continue
            payload = self._state.topology.edge_payload(edge_id)
            raw_conductance = payload.get("base_conductance", 1.0)
            conductance_by_edge[edge_id] = (
                float(raw_conductance)
                if isinstance(raw_conductance, int | float)
                and not isinstance(raw_conductance, bool)
                else 1.0
            )
        return conductance_by_edge

    def _neighbor_weights(
        self,
        *,
        node_id: int,
        displacements: Mapping[int, Any],
        base_conductance: Mapping[int, float],
    ) -> dict[int, float]:
        weights: dict[int, float] = {}
        for neighbor_id in displacements:
            total = 0.0
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                if {node_a, node_b} == {node_id, neighbor_id}:
                    total += float(base_conductance.get(edge_id, 1.0))
            weights[neighbor_id] = total if total > 0.0 else 1.0
        return weights

    def _basin_mass_for_node(
        self,
        node_id: int,
        coherence_by_node: Mapping[int, float],
    ) -> float:
        if node_id in self._state.basins:
            return float(
                sum(coherence_by_node.get(member_id, 0.0) for member_id in self._state.basins[node_id])
            )
        return float(coherence_by_node.get(node_id, 0.0))

    def _split_registry(self) -> dict[str, Any]:
        registry = self._state.cached_quantities.get("split_registry")
        if registry is None:
            registry = {}
            self._state.cached_quantities["split_registry"] = registry
        if not isinstance(registry, dict):
            raise SnapshotCompatibilityError("split_registry cache must be a mapping")
        return registry

    def _active_split_parent_ids(self) -> set[int]:
        active: set[int] = set()
        for entry in self._split_registry().values():
            if isinstance(entry, Mapping) and not bool(entry.get("complete", False)):
                active.add(int(entry.get("parent_node_id", -1)))
        return active

    def _active_split_child_ids(self) -> set[int]:
        active: set[int] = set()
        for entry in self._split_registry().values():
            if not isinstance(entry, Mapping) or bool(entry.get("complete", False)):
                continue
            for child_node_id in entry.get("child_node_ids", []):
                active.add(int(child_node_id))
        return active

    def _initialize_split_from_candidate(self, event: GRCEvent) -> list[GRCEvent]:
        if event.kind != "spark_candidate":
            return []
        parent_node_id = int(event.payload["node_id"])
        if not self._state.topology.has_node(parent_node_id):
            return []
        if parent_node_id in self._active_split_parent_ids():
            return []
        split_distribution_mode = self._params.constitutive_semantic_modes[
            "split_distribution_mode"
        ]
        if split_distribution_mode != "equal":
            raise NotImplementedError(
                "Phase 5 Iteration 6 implements only split_distribution_mode=equal"
            )

        parent_attributes = self._require_basin_attributes(parent_node_id)
        parent_payload = self._state.topology.node_payload(parent_node_id)
        inherited_child_metadata = (
            dict(parent_payload.get("metadata", {}))
            if isinstance(parent_payload, Mapping)
            and isinstance(parent_payload.get("metadata"), Mapping)
            else {}
        )
        parent_mass = float(parent_attributes.coherence)
        split_ratio = 0.5
        child_masses = [parent_mass * split_ratio, parent_mass * (1.0 - split_ratio)]
        initial_edge_weight = 1e-6
        split_link_target_weight = max(
            1e-6,
            float(self._params.evolution.get("alpha_seed", 1.0)),
        )
        weak_axis_index = int(event.payload.get("weak_axis_index", 0))

        parent_neighbors: list[tuple[int, float, dict[str, Any]]] = []
        parent_edge_targets: list[dict[str, Any]] = []
        for edge_id in self._state.topology.incident_edge_ids(parent_node_id):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == parent_node_id else node_a
            parent_edge_weight = float(self._state.base_conductance.get(edge_id, 1.0))
            parent_neighbors.append(
                (
                    neighbor_id,
                    parent_edge_weight,
                    dict(self._state.topology.edge_payload(edge_id)),
                )
            )
            parent_edge_targets.append(
                {
                    "edge_id": edge_id,
                    "neighbor_id": neighbor_id,
                    "initial_weight": parent_edge_weight,
                    "target_weight": 0.0,
                }
            )
        parent_neighbors.sort(key=lambda item: item[0])
        parent_edge_targets.sort(key=lambda item: (int(item["neighbor_id"]), int(item["edge_id"])))

        child_node_ids: list[int] = []
        split_link_edge_ids: list[int] = []
        child_edge_targets: list[dict[str, Any]] = []
        emitted_events: list[GRCEvent] = []

        for child_index, child_mass in enumerate(child_masses):
            child_node_id = self._state.topology.add_node(
                {
                    "kind": "split_child",
                    "parent_node_id": parent_node_id,
                    "child_index": child_index,
                    "metadata": inherited_child_metadata,
                }
            )
            child_node_ids.append(child_node_id)
            child_attributes = self._build_child_basin_attributes(
                parent_attributes=parent_attributes,
                child_node_id=child_node_id,
                child_mass=child_mass,
                child_index=child_index,
                weak_axis_index=weak_axis_index,
            )
            self._state.nodes[child_node_id] = child_attributes
            self._state.potential[child_node_id] = 0.0

            split_link_edge_id = self._state.topology.add_edge(
                parent_node_id,
                child_node_id,
                {"kind": "split_link", "parent_node_id": parent_node_id},
            )
            split_link_edge_ids.append(split_link_edge_id)
            self._state.base_conductance[split_link_edge_id] = initial_edge_weight
            self._state.flux[(split_link_edge_id, parent_node_id)] = 0.0
            self._state.flux[(split_link_edge_id, child_node_id)] = -0.0

            child_ratio = split_ratio if child_index == 0 else (1.0 - split_ratio)
            for neighbor_id, parent_edge_weight, payload in parent_neighbors:
                child_edge_id = self._state.topology.add_edge(
                    child_node_id,
                    neighbor_id,
                    {
                        **payload,
                        "kind": "split_child_neighbor",
                        "parent_node_id": parent_node_id,
                        "child_node_id": child_node_id,
                    },
                )
                target_weight = max(1e-6, parent_edge_weight * child_ratio)
                self._state.base_conductance[child_edge_id] = initial_edge_weight
                self._state.flux[(child_edge_id, child_node_id)] = 0.0
                self._state.flux[(child_edge_id, neighbor_id)] = -0.0
                child_edge_targets.append(
                    {
                        "edge_id": child_edge_id,
                        "target_weight": target_weight,
                        "child_node_id": child_node_id,
                        "neighbor_id": neighbor_id,
                    }
                )

        self._state.nodes[parent_node_id] = BasinAttributes(
            coherence=0.0,
            gradient=list(parent_attributes.gradient),
            hessian=[list(row) for row in parent_attributes.hessian],
            net_flux=list(parent_attributes.net_flux),
            basin_mass=0.0,
            basin_id=parent_attributes.basin_id,
            parent_id=parent_attributes.parent_id,
            depth=parent_attributes.depth,
        )

        registry_key = (
            f"split:{self._state.step_index}:{parent_node_id}:"
            f"{int(event.payload.get('candidate_rank', 0))}"
        )
        self._split_registry()[registry_key] = {
            "parent_node_id": parent_node_id,
            "parent_basin_id": parent_attributes.basin_id,
            "pre_metrics": self._attractor_metrics(),
            "child_node_ids": child_node_ids,
            "split_ratio": split_ratio,
            "progress_step": 0,
            "progress_fraction": 0.0,
            "total_steps": max(1, int(math.ceil(float(self._params.evolution["tau_split"])))),
            "complete": False,
            "spark_confirmed": False,
            "parent_removed": False,
            "initial_parent_mass": parent_mass,
            "initial_edge_weight": initial_edge_weight,
            "split_link_target_weight": split_link_target_weight,
            "split_link_edge_ids": split_link_edge_ids,
            "parent_edge_targets": parent_edge_targets,
            "child_edge_targets": child_edge_targets,
            "child_basin_ids": list(child_node_ids),
            "candidate_rank": int(event.payload.get("candidate_rank", 0)),
            "min_child_basins": self._min_child_basins(),
        }

        emitted_events.append(
            GRCEvent(
                kind="split_init",
                step_index=self._state.step_index,
                source_family=self.MODEL_FAMILY,
                payload={
                    "registry_key": registry_key,
                    "parent_node_id": parent_node_id,
                    "parent_basin_id": parent_attributes.basin_id,
                    "child_node_ids": list(child_node_ids),
                    "weak_axis_index": weak_axis_index,
                },
            )
        )
        return emitted_events

    def _build_child_basin_attributes(
        self,
        *,
        parent_attributes: BasinAttributes,
        child_node_id: int,
        child_mass: float,
        child_index: int,
        weak_axis_index: int,
    ) -> BasinAttributes:
        dimension = max(
            len(parent_attributes.gradient),
            len(parent_attributes.net_flux),
            len(parent_attributes.hessian),
            1,
        )
        gradient = [0.0] * dimension
        net_flux = [0.0] * dimension
        hessian_sign = int(self._state.cached_quantities.get("hessian_sign", 1))
        signed_parent_hessian = [
            [hessian_sign * float(value) for value in row]
            for row in _pad_matrix(parent_attributes.hessian, dimension=dimension)
        ]
        child_signed_hessian = _zero_matrix(dimension)
        stable_curvature = max(
            float(self._params.evolution["eps_hessian"]) * 2.0,
            float(self._params.evolution["eps_spark"]) * 2.0,
        )
        axis = min(max(weak_axis_index, 0), dimension - 1)
        parent_diagonal = [
            float(signed_parent_hessian[index][index]) for index in range(dimension)
        ]
        child_signed_hessian[axis][axis] = stable_curvature
        for index in range(dimension):
            if index == axis:
                continue
            child_signed_hessian[index][index] = max(
                parent_diagonal[index],
                stable_curvature,
            )
        child_hessian = [
            [float(hessian_sign) * value for value in row]
            for row in child_signed_hessian
        ]
        return BasinAttributes(
            coherence=child_mass,
            gradient=gradient,
            hessian=child_hessian,
            net_flux=net_flux,
            basin_mass=child_mass,
            basin_id=child_node_id,
            parent_id=parent_attributes.basin_id,
            depth=int(parent_attributes.depth) + 1,
        )

    def _attractor_metrics(self) -> dict[str, int]:
        geometric_identity = self._state.cached_quantities.get("geometric_identity", {})
        validated = geometric_identity.get("validated_basin_ids", []) if isinstance(
            geometric_identity, Mapping
        ) else []
        validated_count = len(validated) if isinstance(
            validated, (list, tuple, set, frozenset)
        ) else 0
        return {
            "sink_count": len(self._state.sink_set),
            "validated_basin_count": validated_count,
        }

    def _append_events(self, events: list[GRCEvent]) -> None:
        if not events:
            return
        self._state.event_log.extend(events)
        self._state.cached_quantities["last_events"] = [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in events
        ]

    def _choice_backend_selection(self) -> dict[str, Any]:
        backend_payload = dict(self._params.constitutive_semantic_modes[BACKEND_SELECTIONS_KEY])
        selection = backend_payload.get("choice", {})
        if not isinstance(selection, Mapping):
            raise SnapshotCompatibilityError("GRCV3 choice backend selection must be a mapping")
        return dict(selection)

    def _resolved_choice_score_params(
        self,
        choice_selection: Mapping[str, Any],
    ) -> dict[str, float]:
        base_params = dict(self._params.evolution["compatibility_score_params"])
        override_params = choice_selection.get("params", {})
        if override_params not in ({}, None) and not isinstance(override_params, Mapping):
            raise SnapshotCompatibilityError("choice backend params must be a mapping")
        if isinstance(override_params, Mapping):
            for key, value in override_params.items():
                base_params[key] = value
        epsilon_choice = _as_runtime_float(
            base_params.get("epsilon_choice", 1e-3),
            context="choice epsilon_choice",
        )
        epsilon_collapse = _as_runtime_float(
            base_params.get("epsilon_collapse", 1e-3),
            context="choice epsilon_collapse",
        )
        if epsilon_choice < 0.0:
            raise SnapshotCompatibilityError("choice epsilon_choice must be >= 0")
        if epsilon_collapse < 0.0:
            raise SnapshotCompatibilityError("choice epsilon_collapse must be >= 0")
        return {
            "epsilon_choice": epsilon_choice,
            "epsilon_collapse": epsilon_collapse,
        }

    def _successor_map_for_choice(self) -> dict[int, int | None]:
        raw_successor_map = self._state.cached_quantities.get("successor_map", {})
        if not isinstance(raw_successor_map, Mapping):
            raise SnapshotCompatibilityError(
                "GRCV3 choice evaluation requires successor_map diagnostics"
            )
        successor_map: dict[int, int | None] = {}
        for node_id, successor in raw_successor_map.items():
            try:
                node_id_int = int(node_id)
                successor_map[node_id_int] = None if successor is None else int(successor)
            except (TypeError, ValueError) as exc:
                raise SnapshotCompatibilityError(
                    "successor_map keys and values must be int-compatible or null"
                ) from exc
        return successor_map

    def _sink_compatibility_for_node(
        self,
        node_id: int,
        *,
        successor_map: Mapping[int, int | None],
        sinks: set[int],
        epsilon_choice: float,
    ) -> dict[str, Any] | None:
        if node_id in sinks:
            return None

        flux_by_sink: dict[int, float] = {}
        total_positive_flux = 0.0

        for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == node_id else node_a
            outgoing_flux = float(self._state.flux.get((edge_id, node_id), 0.0))
            if outgoing_flux <= 0.0:
                continue
            sink_id = (
                neighbor_id
                if neighbor_id in sinks
                else self._reachable_sink(neighbor_id, successor_map, sinks)
            )
            if sink_id is None:
                continue
            total_positive_flux += outgoing_flux
            flux_by_sink[sink_id] = flux_by_sink.get(sink_id, 0.0) + outgoing_flux

        if total_positive_flux <= 0.0 or not flux_by_sink:
            return None

        ordered_flux = sorted(flux_by_sink.items(), key=lambda item: (-item[1], item[0]))
        ordered_scores = [
            (str(sink_id), float(value / total_positive_flux))
            for sink_id, value in ordered_flux
        ]
        best_sink_id, best_score = ordered_scores[0]
        viable_sink_ids = [
            sink_id
            for sink_id, score in ordered_scores
            if best_score - score <= epsilon_choice
        ]
        second_best = ordered_scores[1][1] if len(ordered_scores) > 1 else 0.0

        return {
            "scores": {sink_id: score for sink_id, score in ordered_scores},
            "viable_sink_ids": viable_sink_ids,
            "winner_sink_id": best_sink_id,
            "winner_margin": float(best_score - second_best),
            "total_positive_flux": float(total_positive_flux),
        }

    def _refresh_after_topology_change(self) -> None:
        """Refresh local transport and identity after topology or split-weight edits.

        This intentionally preserves the currently active `base_conductance`
        values, including soft-split interpolation overrides, instead of
        re-running the full metric law.
        """

        self._compute_potential()
        self._compute_flux()
        self.rebuild_basin_attributes()
        self._compute_node_tensors()
        self._compute_edge_labels(pre_flux_only=True)
        self._compute_edge_labels(pre_flux_only=False)
        self.rebuild_identity_state()

    def _evaluate_split_completion(self) -> list[GRCEvent]:
        emitted_events: list[GRCEvent] = []
        split_registry = self._split_registry()
        current_metrics = self._attractor_metrics()
        for registry_key in sorted(split_registry):
            entry = split_registry[registry_key]
            if not isinstance(entry, Mapping):
                continue
            if bool(entry.get("spark_confirmed", False)):
                continue
            pre_metrics_raw = entry.get("pre_metrics", {})
            if not isinstance(pre_metrics_raw, Mapping):
                pre_metrics: dict[str, int] = {"sink_count": 0, "validated_basin_count": 0}
            else:
                pre_metrics = {
                    "sink_count": int(pre_metrics_raw.get("sink_count", 0)),
                    "validated_basin_count": int(
                        pre_metrics_raw.get("validated_basin_count", 0)
                    ),
                }
            min_child_basins = max(1, int(entry.get("min_child_basins", 1)))
            geometric_delta = (
                current_metrics["validated_basin_count"] - pre_metrics["validated_basin_count"]
            )
            sink_delta = current_metrics["sink_count"] - pre_metrics["sink_count"]
            completed = geometric_delta >= min_child_basins or sink_delta >= 1
            completion_event = GRCEvent(
                kind="spark" if completed else "spark_pending",
                step_index=self._state.step_index,
                source_family=self.MODEL_FAMILY,
                payload={
                    "registry_key": registry_key,
                    "parent_node_id": int(entry["parent_node_id"]),
                    "parent_basin_id": entry.get("parent_basin_id"),
                    "candidate_rank": int(entry.get("candidate_rank", 0)),
                    "min_child_basins": min_child_basins,
                    "pre_metrics": dict(pre_metrics),
                    "post_metrics": dict(current_metrics),
                    "geometric_delta": geometric_delta,
                    "sink_delta": sink_delta,
                },
            )
            emitted_events.append(completion_event)
            if completed and isinstance(entry, dict):
                entry["spark_confirmed"] = True
                entry["spark_confirmed_step_index"] = self._state.step_index
        return emitted_events

    def _cleanup_state_against_live_topology(self) -> None:
        live_node_ids = set(self._state.topology.iter_live_node_ids())
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())

        self._state.nodes = {
            node_id: attributes
            for node_id, attributes in self._state.nodes.items()
            if node_id in live_node_ids
        }
        self._state.potential = {
            node_id: value
            for node_id, value in self._state.potential.items()
            if node_id in live_node_ids
        }
        self._state.sink_set = {
            node_id for node_id in self._state.sink_set if node_id in live_node_ids
        }
        self._state.basins = {
            sink_node_id: {member for member in members if member in live_node_ids}
            for sink_node_id, members in self._state.basins.items()
            if sink_node_id in live_node_ids
        }
        self._state.base_conductance = {
            edge_id: value
            for edge_id, value in self._state.base_conductance.items()
            if edge_id in live_edge_ids
        }
        self._state.geometric_length = {
            edge_id: value
            for edge_id, value in self._state.geometric_length.items()
            if edge_id in live_edge_ids
        }
        self._state.temporal_delay = {
            edge_id: value
            for edge_id, value in self._state.temporal_delay.items()
            if edge_id in live_edge_ids
        }
        self._state.flux_coupling = {
            edge_id: value
            for edge_id, value in self._state.flux_coupling.items()
            if edge_id in live_edge_ids
        }
        self._state.flux = {
            (edge_id, source_node_id): flux_value
            for (edge_id, source_node_id), flux_value in self._state.flux.items()
            if edge_id in live_edge_ids and source_node_id in live_node_ids
        }

    def _reachable_sink(
        self,
        origin_node_id: int,
        successor_map: Mapping[int, int | None],
        sinks: set[int],
    ) -> int | None:
        if origin_node_id in sinks:
            return origin_node_id

        visited = {origin_node_id}
        node_id = successor_map.get(origin_node_id)
        while node_id is not None:
            if node_id in visited:
                return None
            visited.add(node_id)
            if node_id in sinks:
                return node_id
            node_id = successor_map.get(node_id)
        return None

    def _frontier_birth_mode(self) -> str:
        mode = str(
            self._params.constitutive_semantic_modes.get(
                "frontier_birth_mode",
                "disabled",
            )
        )
        if mode not in _ALLOWED_FRONTIER_BIRTH_MODES:
            raise InvalidParamsError(
                "frontier_birth_mode must be one of disabled, active_frontier_pressure"
            )
        return mode

    def _frontier_birth_strict(self) -> str:
        value = self._params.constitutive_semantic_modes.get(
            "frontier_birth_strict",
            "warn",
        )
        if not isinstance(value, str):
            raise InvalidParamsError("frontier_birth_strict must be one of warn, error, allow")
        if value not in _ALLOWED_FRONTIER_BIRTH_STRICT_VALUES:
            raise InvalidParamsError("frontier_birth_strict must be one of warn, error, allow")
        return value

    def _frontier_birth_candidates(self) -> dict[int, dict[str, Any]]:
        raw_candidates = self._state.cached_quantities.get(
            "grcv3_frontier_birth_candidates",
            {},
        )
        candidates: dict[int, dict[str, Any]] = {}
        if raw_candidates not in ({}, None):
            if not isinstance(raw_candidates, Mapping):
                raise SnapshotCompatibilityError(
                    "grcv3_frontier_birth_candidates must be a mapping"
                )
            for node_id_raw, candidate_raw in raw_candidates.items():
                try:
                    node_id = int(node_id_raw)
                except (TypeError, ValueError) as exc:
                    raise SnapshotCompatibilityError(
                        "grcv3_frontier_birth_candidates node ids must be int-compatible"
                    ) from exc
                if candidate_raw is False or candidate_raw is None:
                    continue
                if candidate_raw is True:
                    candidate = {"frontier_source": "active_frontier"}
                elif isinstance(candidate_raw, Mapping):
                    candidate = dict(candidate_raw)
                    if not bool(candidate.get("enabled", True)):
                        continue
                else:
                    raise SnapshotCompatibilityError(
                        "grcv3_frontier_birth_candidates values must be mappings or booleans"
                    )
                candidate.setdefault("frontier_source", "active_frontier")
                candidates[node_id] = candidate

        raw_active_frontiers = self._state.cached_quantities.get(
            "grcv3_active_frontier_node_ids",
            (),
        )
        if raw_active_frontiers not in ((), [], None):
            if not isinstance(raw_active_frontiers, (list, tuple, set, frozenset)):
                raise SnapshotCompatibilityError(
                    "grcv3_active_frontier_node_ids must be sequence-like"
                )
            for node_id_raw in raw_active_frontiers:
                try:
                    node_id = int(node_id_raw)
                except (TypeError, ValueError) as exc:
                    raise SnapshotCompatibilityError(
                        "grcv3_active_frontier_node_ids must contain int-compatible ids"
                    ) from exc
                candidates.setdefault(node_id, {"frontier_source": "active_frontier"})

        raw_pressure_frontiers = self._state.cached_quantities.get(
            "grcv3_pressure_boundary_frontier_node_ids",
            (),
        )
        if raw_pressure_frontiers not in ((), [], None):
            if not isinstance(raw_pressure_frontiers, (list, tuple, set, frozenset)):
                raise SnapshotCompatibilityError(
                    "grcv3_pressure_boundary_frontier_node_ids must be sequence-like"
                )
            for node_id_raw in raw_pressure_frontiers:
                try:
                    node_id = int(node_id_raw)
                except (TypeError, ValueError) as exc:
                    raise SnapshotCompatibilityError(
                        "grcv3_pressure_boundary_frontier_node_ids must contain "
                        "int-compatible ids"
                    ) from exc
                candidates.setdefault(node_id, {"frontier_source": "pressure_boundary"})

        live_node_ids = set(self._state.topology.iter_live_node_ids())
        return {
            node_id: candidate
            for node_id, candidate in sorted(candidates.items())
            if node_id in live_node_ids
        }

    def _outward_flux_pressure(self, node_id: int) -> float:
        outward_flux = 0.0
        for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
            outward_flux += max(0.0, float(self._state.flux.get((edge_id, node_id), 0.0)))
        return float(outward_flux)

    def apply_frontier_birth(self) -> list[GRCEvent]:
        mode = self._frontier_birth_mode()
        self._state.cached_quantities["frontier_birth_mode"] = mode
        self._state.cached_quantities["frontier_birth_rule_mode"] = (
            "disabled" if mode == "disabled" else "bernoulli_outward_flux_pressure"
        )
        if mode == "disabled":
            self._state.cached_quantities["last_frontier_birth_events"] = []
            return []

        lambda_birth = _as_runtime_float(
            self._params.evolution.get("lambda_birth", 0.0),
            context="lambda_birth",
        )
        alpha_seed = _as_runtime_float(
            self._params.evolution.get("alpha_seed", 0.1),
            context="alpha_seed",
        )
        edge_conductance = _as_runtime_float(
            self._params.evolution.get("frontier_birth_edge_conductance", 1.0),
            context="frontier_birth_edge_conductance",
        )
        if lambda_birth <= 0.0:
            self._state.cached_quantities["last_frontier_birth_events"] = []
            return []
        if not 0.0 <= alpha_seed <= 1.0:
            raise SnapshotCompatibilityError("alpha_seed must be between 0 and 1")
        if edge_conductance <= 0.0:
            raise SnapshotCompatibilityError("frontier_birth_edge_conductance must be > 0")

        if self._state.rng_state is None:
            seed = int(self._params.evolution.get("rng_seed", 0))
            self._state.rng_state = _default_rng_state(seed)
        rng = random.Random()
        rng.setstate(self._state.rng_state)

        selected_parents: list[tuple[int, dict[str, Any], float, float, float]] = []
        for node_id, candidate in self._frontier_birth_candidates().items():
            outward_flux = self._outward_flux_pressure(node_id)
            if outward_flux <= 0.0:
                continue
            birth_probability = 1.0 - math.exp(-lambda_birth * outward_flux)
            rng_sample = rng.random()
            if rng_sample < birth_probability:
                selected_parents.append(
                    (node_id, candidate, outward_flux, birth_probability, rng_sample)
                )

        birth_events: list[GRCEvent] = []
        for node_id, candidate, outward_flux, birth_probability, rng_sample in selected_parents:
            if not self._state.topology.has_node(node_id):
                continue
            parent_attributes = self._require_basin_attributes(node_id)
            child_node_id = self._state.topology.add_node(
                {
                    "role": "frontier_birth_child",
                    "parent_node_id": node_id,
                    "frontier_source": str(candidate.get("frontier_source", "active_frontier")),
                }
            )
            edge_id = self._state.topology.add_edge(
                node_id,
                child_node_id,
                payload={
                    "kind": "frontier_birth",
                    "parent_node_id": node_id,
                    "frontier_source": str(candidate.get("frontier_source", "active_frontier")),
                },
            )
            self._state.base_conductance[edge_id] = edge_conductance
            transfer = max(
                0.0,
                min(float(parent_attributes.coherence), alpha_seed * float(parent_attributes.coherence)),
            )
            self._state.nodes[node_id] = BasinAttributes(
                coherence=float(parent_attributes.coherence - transfer),
                gradient=list(parent_attributes.gradient),
                hessian=[list(row) for row in parent_attributes.hessian],
                net_flux=list(parent_attributes.net_flux),
                basin_mass=parent_attributes.basin_mass,
                basin_id=parent_attributes.basin_id,
                parent_id=parent_attributes.parent_id,
                depth=parent_attributes.depth,
            )
            self._state.nodes[child_node_id] = BasinAttributes(
                coherence=transfer,
                gradient=[0.0 for _ in parent_attributes.gradient],
                hessian=_zero_matrix(len(parent_attributes.hessian)),
                net_flux=[0.0 for _ in parent_attributes.net_flux],
                basin_mass=transfer,
                basin_id=child_node_id,
                parent_id=parent_attributes.basin_id,
                depth=int(parent_attributes.depth) + 1,
            )
            self._state.potential[child_node_id] = 0.0
            event = GRCEvent(
                kind="frontier_birth",
                step_index=self._state.step_index,
                source_family=self.MODEL_FAMILY,
                payload={
                    "parent_node_id": node_id,
                    "child_node_id": child_node_id,
                    "edge_id": edge_id,
                    "frontier_birth_mode": mode,
                    "frontier_source": str(candidate.get("frontier_source", "active_frontier")),
                    "frontier_role": candidate.get("frontier_role"),
                    "outward_flux_pressure": outward_flux,
                    "birth_rule": "outward_flux_pressure",
                    "birth_probability": birth_probability,
                    "rng_sample": rng_sample,
                    "coherence_transfer": transfer,
                },
            )
            birth_events.append(event)

        self._state.rng_state = rng.getstate()
        self._append_events(birth_events)
        self._state.cached_quantities["last_frontier_birth_events"] = [
            dict(event.payload) for event in birth_events
        ]
        return birth_events

    def _handle_frontier_birth_disabled_with_candidates(self, mode: str) -> None:
        if mode == "active_frontier_pressure":
            return
        if not self._frontier_birth_candidates():
            return
        strict = self._frontier_birth_strict()
        if strict == "allow":
            return
        if strict == "error":
            raise InvalidParamsError(
                "GRCV3 frontier-birth candidates are present, but node birth is "
                "disabled. Set constitutive_semantic_modes.frontier_birth_mode="
                "'active_frontier_pressure', or set frontier_birth_strict='allow' "
                "only for explicit legacy/no-birth compatibility lanes."
            )
        warning_key = "frontier_birth_disabled_warning_emitted"
        if self._state.cached_quantities.get(warning_key):
            return
        message = (
            "GRCV3 frontier-birth candidates are present, but node birth is "
            "disabled because constitutive_semantic_modes.frontier_birth_mode "
            "is not active_frontier_pressure. Set frontier_birth_mode="
            "'active_frontier_pressure' to enable pressure-boundary node birth."
        )
        self._state.cached_quantities[warning_key] = True
        self._state.cached_quantities["frontier_birth_disabled_warning"] = message
        warnings.warn(message, RuntimeWarning, stacklevel=2)

    def _apply_continuity(self) -> None:
        dt = self._params.dt
        coherence_deltas: dict[int, float] = {}
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            divergence = sum(
                float(self._state.flux.get((edge_id, node_id), 0.0))
                for edge_id in self._state.topology.incident_edge_ids(node_id)
            )
            coherence_deltas[node_id] = -dt * divergence

        for node_id in sorted(coherence_deltas):
            attributes = self._require_basin_attributes(node_id)
            self._state.nodes[node_id] = BasinAttributes(
                coherence=float(attributes.coherence + coherence_deltas[node_id]),
                gradient=list(attributes.gradient),
                hessian=[list(row) for row in attributes.hessian],
                net_flux=list(attributes.net_flux),
                basin_mass=attributes.basin_mass,
                basin_id=attributes.basin_id,
                parent_id=attributes.parent_id,
                depth=attributes.depth,
            )
        self._state.cached_quantities["last_continuity_delta"] = dict(coherence_deltas)

    def _enforce_budget(self) -> None:
        negative_mass_correction = 0.0
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            attributes = self._require_basin_attributes(node_id)
            if attributes.coherence >= 0.0:
                continue
            negative_mass_correction += -float(attributes.coherence)
            self._state.nodes[node_id] = BasinAttributes(
                coherence=0.0,
                gradient=list(attributes.gradient),
                hessian=[list(row) for row in attributes.hessian],
                net_flux=list(attributes.net_flux),
                basin_mass=attributes.basin_mass,
                basin_id=attributes.basin_id,
                parent_id=attributes.parent_id,
                depth=attributes.depth,
            )

        abundance = float(
            sum(
                self._require_basin_attributes(node_id).coherence
                for node_id in self._state.topology.iter_live_node_ids()
            )
        )
        if self._state.budget_target == 0.0:
            self._state.budget_target = abundance
        correction = float(self._state.budget_target - abundance)
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        self._state.remainder = 0.0

        if correction > 0.0:
            if live_node_ids:
                target_node_id = live_node_ids[0]
                attributes = self._require_basin_attributes(target_node_id)
                self._state.nodes[target_node_id] = BasinAttributes(
                    coherence=float(attributes.coherence + correction),
                    gradient=list(attributes.gradient),
                    hessian=[list(row) for row in attributes.hessian],
                    net_flux=list(attributes.net_flux),
                    basin_mass=attributes.basin_mass,
                    basin_id=attributes.basin_id,
                    parent_id=attributes.parent_id,
                    depth=attributes.depth,
                )
            else:
                self._state.remainder = correction
                return
        elif correction < 0.0:
            remaining_removal = -correction
            for node_id in live_node_ids:
                if remaining_removal <= 0.0:
                    break
                attributes = self._require_basin_attributes(node_id)
                removal = min(float(attributes.coherence), remaining_removal)
                self._state.nodes[node_id] = BasinAttributes(
                    coherence=float(attributes.coherence - removal),
                    gradient=list(attributes.gradient),
                    hessian=[list(row) for row in attributes.hessian],
                    net_flux=list(attributes.net_flux),
                    basin_mass=attributes.basin_mass,
                    basin_id=attributes.basin_id,
                    parent_id=attributes.parent_id,
                    depth=attributes.depth,
                )
                remaining_removal -= removal
            if remaining_removal > 1e-12:
                self._state.remainder = -remaining_removal

        self._state.cached_quantities["negative_mass_correction"] = float(
            negative_mass_correction
        )

    def step(self) -> StepResult:
        """Advance one full Phase 5 reference step.

        The representative runtime seed used in Iteration 11 is intentionally
        simple, but this method is not a reduced "minimal" loop. It is the
        current paper-facing Phase 5 baseline and therefore performs the full
        pre-flux build, post-flux differential refresh, event layers,
        continuity/budget closure, and final post-step refresh before exposing
        the next state.
        """
        trace: list[str] = []
        initial_event_count = len(self._state.event_log)

        self.rebuild_basin_attributes()
        trace.append("compute_differential_summary_pre_flux")

        self._compute_node_tensors()
        trace.append("compute_node_tensors")

        self._compute_metric()
        trace.append("compute_metric")

        self._compute_edge_labels(pre_flux_only=True)
        trace.append("compute_edge_labels_pre_flux")

        self._compute_potential()
        trace.append("compute_potential")

        self._compute_flux()
        trace.append("compute_flux")

        self._compute_edge_labels(pre_flux_only=False)
        trace.append("compute_edge_labels_post_flux")

        self.rebuild_basin_attributes()
        trace.append("refresh_differential_summary_post_flux")

        self.rebuild_identity_state()
        trace.append("detect_identities")

        self.rebuild_spark_state()
        trace.append("detect_sparks")

        self.advance_split_state()
        trace.append("advance_splits")

        self.rebuild_choice_state()
        trace.append("update_choice_state")

        frontier_birth_mode = self._frontier_birth_mode()
        if frontier_birth_mode == "active_frontier_pressure":
            self.apply_frontier_birth()
            trace.append("apply_frontier_birth")
        else:
            self._handle_frontier_birth_disabled_with_candidates(frontier_birth_mode)

        self._apply_continuity()
        trace.append("apply_continuity")

        self._enforce_budget()
        trace.append("enforce_budget")

        self.rebuild_basin_attributes()
        self._compute_node_tensors()
        self._compute_metric()
        self._compute_edge_labels(pre_flux_only=True)
        self._compute_potential()
        self._compute_flux()
        self._compute_edge_labels(pre_flux_only=False)
        self.rebuild_basin_attributes()
        self.rebuild_identity_state()
        trace.append("refresh_runtime_state")

        observables = self.compute_observables()
        trace.append("compute_observables")

        final_events = list(self._state.event_log[initial_event_count:])

        self._state.step_index += 1
        self._state.time += self._params.dt
        self._state.observables = dict(observables)
        self._state.params_identity = self._params.params_hash
        self._state.cached_quantities["last_step_trace"] = tuple(trace)

        return StepResult(
            step_index=self._state.step_index,
            time=self._state.time,
            events=final_events,
            observables=dict(observables),
            bookkeeping={
                "step_order": tuple(trace),
                "expected_step_order": (
                    _STEP_ORDER_WITH_FRONTIER_BIRTH
                    if "apply_frontier_birth" in trace
                    else _STEP_ORDER
                ),
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
        topology = (
            export_weighted_topology(self._state.topology)
            if isinstance(self._state.topology, WeightedGraphBackend)
            else build_topology_snapshot()
        )
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
                hessian_sign=self._state.cached_quantities.get("hessian_sign"),
            ),
            topology=topology,
            basin_attributes=_basin_attributes_group_from_state(self._state),
            edge_labels=_edge_labels_group_from_state(self._state),
            dynamics={"state": _state_payload_from_state(self._state)},
            observables=self.compute_observables(),
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


__all__ = [
    "BasinAttributes",
    "GRCV3",
    "GRCV3State",
]

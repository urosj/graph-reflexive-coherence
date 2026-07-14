"""Construction and state surface for the executable GRCV2 baseline."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
import heapq
import math
import random
from typing import Any

from pygrc.core import (
    GRCEvent,
    BOUNDARY_BARRIER,
    GRCModel,
    GRCParams,
    GRCState,
    GRCV2_CAPABILITY_PROFILE,
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    InvalidParamsError,
    InvalidStateTransitionError,
    ObservableMap,
    SnapshotCompatibilityError,
    StepResult,
    WeightedGraphBackend,
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
    restore_weighted_graph,
    save_snapshot,
    serialize_rng_state,
)

from .grc_v2_state import GRCV2State, OrientedEdgeId


_REQUIRED_EVOLUTION_KEYS = (
    "alpha",
    "beta",
    "gamma",
    "delta",
    "eta",
    "kappa_c",
    "lambda_c",
    "xi_c",
    "zeta_c",
    "tau_split",
    "lambda_birth",
    "alpha_seed",
    "eps_prune",
)

_REQUIRED_MODE_KEYS = (
    "curvature_backend",
    "frame_mode",
    "boundary_mode",
    "split_distribution_mode",
    "edge_label_selection",
)

_ALLOWED_CURVATURE_BACKENDS = {"ollivier", "forman", "none"}
_ALLOWED_FRAME_MODES = {"host_embedding", "induced_local_frame", "combinatorial"}
_ALLOWED_BOUNDARY_MODES = {"prune", "barrier", "ghost"}
_ALLOWED_SPLIT_DISTRIBUTION_MODES = {"equal", "custom"}
_ALLOWED_EDGE_LABELS = {"geometric_length", "temporal_delay", "flux_coupling"}
_SUPPORTED_SPARK_BACKENDS = {"cheeger_proxy"}


def _coerce_plain_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return dict(value)


def _stringify_mapping_keys(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _stringify_mapping_keys(inner_value)
            for key, inner_value in value.items()
        }
    if isinstance(value, list):
        return [_stringify_mapping_keys(item) for item in value]
    if isinstance(value, tuple):
        return [_stringify_mapping_keys(item) for item in value]
    if isinstance(value, set):
        return [_stringify_mapping_keys(item) for item in sorted(value)]
    return value


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
        if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
            raise SnapshotCompatibilityError(
                f"{value_context} values must be float-compatible numbers"
            )
        numeric_mapping[key] = float(raw_value)
    return numeric_mapping


def _require_flux_mapping(values: Mapping[Any, Any]) -> dict[OrientedEdgeId, float]:
    flux_mapping: dict[OrientedEdgeId, float] = {}
    for raw_key, raw_value in values.items():
        if (
            not isinstance(raw_key, tuple)
            or len(raw_key) != 2
            or not isinstance(raw_key[0], int)
            or not isinstance(raw_key[1], int)
        ):
            raise SnapshotCompatibilityError(
                "flux keys must be oriented edge tuples (edge_id, node_id)"
            )
        if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
            raise SnapshotCompatibilityError(
                "flux values must be float-compatible numbers"
            )
        flux_mapping[(raw_key[0], raw_key[1])] = float(raw_value)
    return flux_mapping


def _restore_event_log(values: Any) -> list[GRCEvent]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise SnapshotCompatibilityError("GRCV2 state.event_log must be a list")
    event_log: list[GRCEvent] = []
    for index, raw_event in enumerate(values):
        if not isinstance(raw_event, Mapping):
            raise SnapshotCompatibilityError(
                f"GRCV2 state.event_log[{index}] must be a mapping"
            )
        kind = raw_event.get("kind")
        if not isinstance(kind, str):
            raise SnapshotCompatibilityError(
                f"GRCV2 state.event_log[{index}].kind must be a string"
            )
        step_index = raw_event.get("step_index", 0)
        if not isinstance(step_index, int):
            raise SnapshotCompatibilityError(
                f"GRCV2 state.event_log[{index}].step_index must be an int"
            )
        payload = raw_event.get("payload", {})
        if not isinstance(payload, Mapping):
            raise SnapshotCompatibilityError(
                f"GRCV2 state.event_log[{index}].payload must be a mapping"
            )
        source_family = raw_event.get("source_family")
        if source_family is not None and not isinstance(source_family, str):
            raise SnapshotCompatibilityError(
                f"GRCV2 state.event_log[{index}].source_family must be a string when present"
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


def _validate_site_potential(evolution: Mapping[str, Any]) -> None:
    if "site_potential_selection" not in evolution:
        raise InvalidParamsError("GRCV2 requires site_potential_selection")
    if "site_potential_params" not in evolution:
        raise InvalidParamsError("GRCV2 requires site_potential_params")
    if not isinstance(evolution["site_potential_selection"], str):
        raise InvalidParamsError("site_potential_selection must be a string")
    if not isinstance(evolution["site_potential_params"], Mapping):
        raise InvalidParamsError("site_potential_params must be a mapping")


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


def _require_positive_param(evolution: Mapping[str, Any], key: str) -> None:
    value = evolution[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidParamsError(f"{key} must be a float-compatible number")
    if float(value) <= 0.0:
        raise InvalidParamsError(f"{key} must be > 0")


def _require_non_negative_param(evolution: Mapping[str, Any], key: str) -> None:
    value = evolution[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidParamsError(f"{key} must be a float-compatible number")
    if float(value) < 0.0:
        raise InvalidParamsError(f"{key} must be >= 0")


def _validate_grcv2_params(params: GRCParams) -> None:
    evolution = params.evolution
    missing_evolution = [key for key in _REQUIRED_EVOLUTION_KEYS if key not in evolution]
    if missing_evolution:
        raise InvalidParamsError(
            f"GRCV2 is missing required evolution params: {missing_evolution}"
        )
    if "eps_spark" not in evolution and "h_thr" not in evolution:
        raise InvalidParamsError("GRCV2 requires either eps_spark or h_thr")
    if "spark_backend" in evolution:
        spark_backend = evolution["spark_backend"]
        if not isinstance(spark_backend, str):
            raise InvalidParamsError("spark_backend must be a string")
        if spark_backend not in _SUPPORTED_SPARK_BACKENDS:
            raise InvalidParamsError(
                f"spark_backend must be one of {sorted(_SUPPORTED_SPARK_BACKENDS)}"
            )

    _validate_site_potential(evolution)

    for key in _REQUIRED_EVOLUTION_KEYS:
        if isinstance(evolution[key], bool) or not isinstance(
            evolution[key], int | float
        ):
            raise InvalidParamsError(f"{key} must be a float-compatible number")
    if params.dt <= 0.0:
        raise InvalidParamsError("dt must be > 0")
    for key in ("alpha", "beta", "gamma", "delta", "eta", "kappa_c", "tau_split"):
        _require_positive_param(evolution, key)
    for key in ("lambda_c", "xi_c", "zeta_c", "lambda_birth", "alpha_seed", "eps_prune"):
        _require_non_negative_param(evolution, key)

    if "eps_spark" in evolution and (
        isinstance(evolution["eps_spark"], bool)
        or not isinstance(evolution["eps_spark"], int | float)
    ):
        raise InvalidParamsError("eps_spark must be a float-compatible number")
    if "eps_spark" in evolution and float(evolution["eps_spark"]) < 0.0:
        raise InvalidParamsError("eps_spark must be >= 0")
    if "h_thr" in evolution and (
        isinstance(evolution["h_thr"], bool)
        or not isinstance(evolution["h_thr"], int | float)
    ):
        raise InvalidParamsError("h_thr must be a float-compatible number")
    if "h_thr" in evolution and float(evolution["h_thr"]) < 0.0:
        raise InvalidParamsError("h_thr must be >= 0")
    if "temporal_v0" in evolution:
        _require_positive_param(evolution, "temporal_v0")
    if "temporal_rho" in evolution:
        _require_non_negative_param(evolution, "temporal_rho")
    if "eps_tau" in evolution:
        _require_positive_param(evolution, "eps_tau")
    if "rng_seed" in evolution:
        if isinstance(evolution["rng_seed"], bool) or not isinstance(evolution["rng_seed"], int):
            raise InvalidParamsError("rng_seed must be an integer")

    modes = params.constitutive_semantic_modes
    missing_modes = [key for key in _REQUIRED_MODE_KEYS if key not in modes]
    if missing_modes:
        raise InvalidParamsError(f"GRCV2 is missing required mode params: {missing_modes}")

    if modes["curvature_backend"] not in _ALLOWED_CURVATURE_BACKENDS:
        raise InvalidParamsError(
            "curvature_backend must be one of ollivier, forman, none"
        )
    if modes["frame_mode"] not in _ALLOWED_FRAME_MODES:
        raise InvalidParamsError(
            "frame_mode must be one of host_embedding, induced_local_frame, combinatorial"
        )
    if modes["boundary_mode"] not in _ALLOWED_BOUNDARY_MODES:
        raise InvalidParamsError("boundary_mode must be one of prune, barrier, ghost")
    if modes["split_distribution_mode"] not in _ALLOWED_SPLIT_DISTRIBUTION_MODES:
        raise InvalidParamsError(
            "split_distribution_mode must be one of equal, custom"
        )
    if modes["frame_mode"] == "host_embedding":
        host_geometry_fields = modes.get("host_geometry_fields")
        if not isinstance(host_geometry_fields, (list, tuple, set, frozenset)) or not host_geometry_fields:
            raise InvalidParamsError(
                "host_embedding frame_mode requires non-empty host_geometry_fields"
            )
    _validate_edge_label_selection(modes["edge_label_selection"])


def _build_params(config: Mapping[str, Any]) -> GRCParams:
    params_input = dict(config.get("params", config))
    try:
        params = GRCParams.from_mapping(params_input)
    except ValueError as exc:
        raise InvalidParamsError(str(exc)) from exc
    _validate_grcv2_params(params)
    return params


def _state_payload_from_state(state: GRCV2State) -> dict[str, Any]:
    return {
        "nodes": {str(node_id): value for node_id, value in state.nodes.items()},
        "edges": {str(edge_id): value for edge_id, value in state.edges.items()},
        "geometric_length": {
            str(edge_id): value for edge_id, value in state.geometric_length.items()
        },
        "temporal_delay": {
            str(edge_id): value for edge_id, value in state.temporal_delay.items()
        },
        "flux_coupling": {
            str(edge_id): value for edge_id, value in state.flux_coupling.items()
        },
        "flux": {f"{edge_id}:{node_id}": value for (edge_id, node_id), value in state.flux.items()},
        "potential": {str(node_id): value for node_id, value in state.potential.items()},
        "sink_set": sorted(state.sink_set),
        "basins": {str(node_id): sorted(members) for node_id, members in state.basins.items()},
        "split_registry": dict(state.split_registry),
        "step_index": state.step_index,
        "time": state.time,
        "budget_target": state.budget_target,
        "remainder": state.remainder,
        "cached_quantities": _stringify_mapping_keys(dict(state.cached_quantities)),
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


_STEP_ORDER: tuple[str, ...] = (
    "compute_geometry",
    "compute_metric",
    "compute_edge_labels",
    "build_laplacian",
    "compute_potential",
    "compute_flux",
    "detect_identities",
    "detect_events",
    "apply_topology_changes",
    "apply_front_birth",
    "apply_boundary_behavior",
    "apply_continuity",
    "enforce_budget",
    "compute_observables",
)


def _as_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidParamsError(f"{context} must be a float-compatible number")
    return float(value)


def _restore_flux_from_mapping(values: Mapping[str, Any]) -> dict[OrientedEdgeId, float]:
    restored: dict[OrientedEdgeId, float] = {}
    for raw_key, raw_value in values.items():
        if not isinstance(raw_key, str) or ":" not in raw_key:
            raise SnapshotCompatibilityError(
                "serialized GRCV2 flux keys must use 'edge_id:node_id' strings"
            )
        edge_id_raw, node_id_raw = raw_key.split(":", 1)
        try:
            edge_id = int(edge_id_raw)
            node_id = int(node_id_raw)
        except ValueError as exc:
            raise SnapshotCompatibilityError(
                "serialized GRCV2 flux keys must encode integer IDs"
            ) from exc
        if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
            raise SnapshotCompatibilityError(
                "serialized GRCV2 flux values must be float-compatible numbers"
            )
        restored[(edge_id, node_id)] = float(raw_value)
    return restored


def _state_from_mapping(
    state: Mapping[str, Any],
    *,
    metadata: Mapping[str, Any] | None = None,
) -> GRCV2State:
    topology_payload = state.get("topology")
    if topology_payload is None:
        topology = WeightedGraphBackend()
    elif isinstance(topology_payload, WeightedGraphBackend):
        topology = deepcopy(topology_payload)
    elif isinstance(topology_payload, Mapping):
        topology = restore_weighted_graph(
            topology_payload,
            {
                "next_node_id": state.get("next_node_id")
                if metadata is None
                else metadata.get("next_node_id"),
                "next_edge_id": state.get("next_edge_id")
                if metadata is None
                else metadata.get("next_edge_id"),
            },
        )
    else:
        raise SnapshotCompatibilityError("GRCV2 state topology must be weighted or mapping")

    nodes = _require_numeric_mapping(
        _coerce_plain_mapping(state.get("nodes"), context="GRCV2 state.nodes"),
        key_context="GRCV2 state.nodes",
        value_context="GRCV2 state.nodes",
    )
    edges = _require_numeric_mapping(
        _coerce_plain_mapping(state.get("edges"), context="GRCV2 state.edges"),
        key_context="GRCV2 state.edges",
        value_context="GRCV2 state.edges",
    )
    geometric_length = _require_numeric_mapping(
        _coerce_plain_mapping(
            state.get("geometric_length"), context="GRCV2 state.geometric_length"
        ),
        key_context="GRCV2 state.geometric_length",
        value_context="GRCV2 state.geometric_length",
    )
    temporal_delay = _require_numeric_mapping(
        _coerce_plain_mapping(
            state.get("temporal_delay"), context="GRCV2 state.temporal_delay"
        ),
        key_context="GRCV2 state.temporal_delay",
        value_context="GRCV2 state.temporal_delay",
    )
    flux_coupling = _require_numeric_mapping(
        _coerce_plain_mapping(
            state.get("flux_coupling"), context="GRCV2 state.flux_coupling"
        ),
        key_context="GRCV2 state.flux_coupling",
        value_context="GRCV2 state.flux_coupling",
    )
    potential = _require_numeric_mapping(
        _coerce_plain_mapping(state.get("potential"), context="GRCV2 state.potential"),
        key_context="GRCV2 state.potential",
        value_context="GRCV2 state.potential",
    )

    flux_mapping = _coerce_plain_mapping(state.get("flux"), context="GRCV2 state.flux")
    if flux_mapping and all(isinstance(key, str) for key in flux_mapping):
        flux = _restore_flux_from_mapping(flux_mapping)
    else:
        flux = _require_flux_mapping(flux_mapping)

    sink_values = state.get("sink_set", [])
    if not isinstance(sink_values, (list, set, tuple)):
        raise SnapshotCompatibilityError("GRCV2 state.sink_set must be list-like")
    if any(not isinstance(node_id, int) for node_id in sink_values):
        raise SnapshotCompatibilityError("GRCV2 state.sink_set must contain ints")
    basins_raw = state.get("basins", {})
    basins_mapping = _coerce_plain_mapping(basins_raw, context="GRCV2 state.basins")
    basins = {
        int(node_id): {int(member) for member in members}
        for node_id, members in basins_mapping.items()
    } if basins_mapping and all(
        isinstance(node_id, str) and isinstance(members, (list, set, tuple))
        for node_id, members in basins_mapping.items()
    ) else _require_basin_mapping(basins_mapping)

    split_registry = _coerce_plain_mapping(
        state.get("split_registry"), context="GRCV2 state.split_registry"
    )
    cached_quantities = _coerce_plain_mapping(
        state.get("cached_quantities"), context="GRCV2 state.cached_quantities"
    )
    observables = _coerce_plain_mapping(
        state.get("observables"), context="GRCV2 state.observables"
    )
    event_log = _restore_event_log(state.get("event_log", []))

    grc_state = GRCV2State(
        topology=topology,
        nodes=nodes,
        edges=edges,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
        flux=flux,
        potential=potential,
        sink_set=set(sink_values),
        basins=basins,
        split_registry=split_registry,
        step_index=int(state.get("step_index", 0)),
        time=float(state.get("time", 0.0)),
        budget_target=float(state.get("budget_target", 0.0)),
        remainder=float(state.get("remainder", 0.0)),
        cached_quantities=cached_quantities,
        event_log=event_log,
        observables=observables,
        rng_state=deserialize_rng_state(state.get("rng_state")),
        params_identity=(
            None
            if state.get("params_identity") is None
            else str(state.get("params_identity"))
        ),
    )
    return grc_state


class GRCV2(GRCModel):
    """Executable-construction surface for the GRCV2 family."""

    MODEL_FAMILY = "GRCV2"
    CAPABILITY_PROFILE = GRCV2_CAPABILITY_PROFILE

    def __init__(self, params: GRCParams, state: GRCV2State | None = None) -> None:
        _validate_grcv2_params(params)
        self._params = params
        initial_state = state if state is not None else GRCV2State()
        self._validate_state(initial_state)
        self._state = deepcopy(initial_state)
        if self._state.rng_state is None:
            self._state.rng_state = self._default_rng_state()
        self._initial_state: GRCV2State | None = deepcopy(initial_state)
        self._reset_baseline_unavailable_reason: str | None = None
        if self._initial_state.rng_state is None:
            self._initial_state.rng_state = deepcopy(self._state.rng_state)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "GRCV2":
        params = _build_params(config)
        state_input = config.get("state", {})
        if not isinstance(state_input, Mapping):
            raise InvalidParamsError("state must be a mapping when provided")
        state = _state_from_mapping(state_input)
        if state.params_identity is None:
            state.params_identity = params.params_hash
        return cls(params=params, state=state)

    @classmethod
    def from_state(cls, state: Mapping[str, Any], params: Mapping[str, Any]) -> "GRCV2":
        params_obj = _build_params({"params": dict(params)})
        restored_state = _state_from_mapping(state)
        if restored_state.params_identity is None:
            restored_state.params_identity = params_obj.params_hash
        return cls(params=params_obj, state=restored_state)

    @classmethod
    def load(cls, path: str) -> "GRCV2":
        snapshot = load_snapshot(path)
        return cls._from_snapshot(snapshot, restore_reset_baseline=True)

    @classmethod
    def _from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
        *,
        restore_reset_baseline: bool = False,
    ) -> "GRCV2":
        require_snapshot_family(snapshot, expected_family=cls.MODEL_FAMILY)
        dynamics = snapshot.get("dynamics", {})
        if not isinstance(dynamics, Mapping):
            raise SnapshotCompatibilityError("GRCV2 snapshot dynamics must be a mapping")
        state_payload = dynamics.get("state", {})
        if not isinstance(state_payload, Mapping):
            raise SnapshotCompatibilityError("GRCV2 snapshot dynamics.state must be a mapping")
        topology = snapshot.get("topology", {})
        if not isinstance(topology, Mapping):
            raise SnapshotCompatibilityError("GRCV2 snapshot topology must be a mapping")
        restored_state = _state_from_mapping(
            {**dict(state_payload), "topology": topology},
            metadata=snapshot["metadata"],
        )
        params = _build_params({"params": snapshot["metadata"]["params"]})
        if restored_state.params_identity is None:
            restored_state.params_identity = params.params_hash
        model = cls(params=params, state=restored_state)
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

    def get_state(self) -> GRCV2State:
        return self._state

    def set_state(self, state: GRCState) -> None:
        if not isinstance(state, GRCV2State):
            raise SnapshotCompatibilityError("GRCV2 state must be a GRCV2State instance")
        self._validate_state(state)
        self._state = deepcopy(state)
        if self._state.rng_state is None:
            self._state.rng_state = self._default_rng_state()

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        claims = set(self.CAPABILITY_PROFILE.required)
        frame_mode = self._params.constitutive_semantic_modes["frame_mode"]
        if frame_mode == "host_embedding":
            claims.add(HOST_EMBEDDING_FRAME)
        else:
            claims.add(INTRINSIC_FRAME)
        if self._params.constitutive_semantic_modes["boundary_mode"] in {"barrier", "ghost"}:
            claims.add(BOUNDARY_BARRIER)
        self.CAPABILITY_PROFILE.validate_claims(claims)
        return claims

    def compute_observables(self) -> ObservableMap:
        current_step_events = tuple(
            event
            for event in self._state.cached_quantities.get("current_step_events", ())
            if isinstance(event, GRCEvent)
        )
        combined_events = tuple(self._state.event_log) + current_step_events
        abundance = float(len(self._state.sink_set))
        weighted_abundance_exponent = _as_float(
            self._params.evolution["gamma"],
            context="gamma",
        )
        weighted_abundance = float(
            sum(
                len(basin_members) ** weighted_abundance_exponent
                for basin_members in self._state.basins.values()
            )
        )
        budget_current = float(sum(self._state.nodes.values()))
        average_conductance = 0.0
        if self._state.edges:
            average_conductance = float(sum(self._state.edges.values()) / len(self._state.edges))
        observables: ObservableMap = {
            "abundance": abundance,
            "weighted_abundance": weighted_abundance,
            "sink_count": len(self._state.sink_set),
            "budget_current": budget_current,
            "budget_error": float(budget_current - self._state.budget_target),
            "num_nodes": len(tuple(self._state.topology.iter_live_node_ids())),
            "num_edges": len(tuple(self._state.topology.iter_live_edge_ids())),
            "spark_count": sum(1 for event in combined_events if event.kind == "spark"),
            "birth_count": sum(1 for event in combined_events if event.kind == "birth"),
            "prune_count": sum(1 for event in combined_events if event.kind == "prune"),
            "average_conductance": average_conductance,
        }
        return observables

    def step(self) -> StepResult:
        trace: list[str] = []
        self._state.cached_quantities["current_step_events"] = []

        self._compute_geometry()
        trace.append("compute_geometry")
        self._compute_metric()
        trace.append("compute_metric")
        self._compute_edge_labels()
        trace.append("compute_edge_labels")
        self._build_laplacian_if_required()
        trace.append("build_laplacian")
        self._compute_potential()
        trace.append("compute_potential")
        self._compute_flux()
        trace.append("compute_flux")
        self._detect_identities()
        trace.append("detect_identities")
        events = self._detect_events()
        self._state.cached_quantities["current_step_events"] = list(events)
        trace.append("detect_events")
        self._apply_topology_changes(events)
        trace.append("apply_topology_changes")
        self._apply_front_birth()
        trace.append("apply_front_birth")
        self._apply_boundary_behavior()
        trace.append("apply_boundary_behavior")
        self._apply_continuity()
        trace.append("apply_continuity")
        self._enforce_budget()
        trace.append("enforce_budget")
        self._refresh_post_step_identity_state()
        observables = self.compute_observables()
        trace.append("compute_observables")
        final_events = list(
            event
            for event in self._state.cached_quantities.get("current_step_events", ())
            if isinstance(event, GRCEvent)
        )

        self._state.step_index += 1
        self._state.time += self._params.dt
        self._state.observables = dict(observables)
        self._state.event_log.extend(final_events)
        self._state.params_identity = self._params.params_hash
        self._state.cached_quantities["last_step_trace"] = tuple(trace)
        self._state.cached_quantities["current_step_events"] = ()

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
            ),
            topology=topology,
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

    def _compute_geometry(self) -> None:
        lambda_c = _as_float(self._params.evolution["lambda_c"], context="lambda_c")
        xi_c = _as_float(self._params.evolution["xi_c"], context="xi_c")
        zeta_c = _as_float(self._params.evolution["zeta_c"], context="zeta_c")
        node_tensors: dict[int, dict[str, Any]] = {}
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            coherence = float(self._state.nodes.get(node_id, 0.0))
            incident_edges = tuple(sorted(self._state.topology.incident_edge_ids(node_id)))
            basis_neighbors: list[int | None] = []
            basis_edges: list[int | None] = []
            gradient_diagonal: list[float] = []
            neighbor_values: list[float] = []
            flux_sum = 0.0
            for edge_id in incident_edges:
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                neighbor_coherence = float(self._state.nodes.get(neighbor_id, 0.0))
                neighbor_values.append(neighbor_coherence)
                basis_neighbors.append(neighbor_id)
                basis_edges.append(edge_id)
                conductance = float(self._state.edges.get(edge_id, 1.0))
                gradient_diagonal.append(
                    xi_c * conductance * ((neighbor_coherence - coherence) ** 2)
                )
                flux_sum += float(self._state.flux.get((edge_id, node_id), 0.0))
            if neighbor_values:
                neighbor_mean = float(sum(neighbor_values) / len(neighbor_values))
            else:
                neighbor_mean = coherence
                basis_neighbors.append(None)
                basis_edges.append(None)
                gradient_diagonal.append(0.0)
            local_pressure = coherence - neighbor_mean
            density_term = lambda_c * coherence
            flux_feedback_term = zeta_c * (flux_sum**2)
            identity_term = density_term + flux_feedback_term
            tensor_diagonal = tuple(
                float(identity_term + gradient_component)
                for gradient_component in gradient_diagonal
            )
            curvature_term = self._curvature_term(
                node_id=node_id,
                neighbors=tuple(
                    neighbor_id for neighbor_id in basis_neighbors if neighbor_id is not None
                ),
            )
            node_tensors[node_id] = {
                "coherence": coherence,
                "neighbor_mean": neighbor_mean,
                "local_pressure": local_pressure,
                "basis_neighbors": tuple(basis_neighbors),
                "basis_edges": tuple(basis_edges),
                "density_term": float(density_term),
                "gradient_diagonal": tuple(float(value) for value in gradient_diagonal),
                "flux_sum": float(flux_sum),
                "flux_feedback_term": float(flux_feedback_term),
                "identity_term": float(identity_term),
                "tensor_diagonal": tensor_diagonal,
                "tensor_trace": float(sum(tensor_diagonal)),
                "curvature_term": curvature_term,
            }
        self._state.cached_quantities["node_tensors"] = node_tensors

    def _compute_metric(self) -> None:
        alpha = _as_float(self._params.evolution["alpha"], context="alpha")
        beta = _as_float(self._params.evolution["beta"], context="beta")
        gamma = _as_float(self._params.evolution["gamma"], context="gamma")
        delta = _as_float(self._params.evolution["delta"], context="delta")
        reference_edge_weights = {
            edge_id: float(self._state.edges.get(edge_id, 1.0))
            for edge_id in self._state.topology.iter_live_edge_ids()
        }
        edge_curvature: dict[int, float] = {}
        updated_conductances: dict[int, float] = {}
        for edge_id in self._state.topology.iter_live_edge_ids():
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            coherence_a = float(self._state.nodes.get(node_a, 0.0))
            coherence_b = float(self._state.nodes.get(node_b, 0.0))
            previous_flux = float(self._state.flux.get((edge_id, node_a), 0.0))
            ricci_ij = self._edge_curvature_term(
                edge_id=edge_id,
                node_a=node_a,
                node_b=node_b,
                edge_weights=reference_edge_weights,
            )
            edge_curvature[edge_id] = float(ricci_ij)
            exponent = (
                -alpha * (coherence_a + coherence_b) / 2.0
                - beta * ((coherence_a - coherence_b) ** 2) / 2.0
                - gamma * (previous_flux**2) / 2.0
                - delta * ricci_ij
            )
            conductance = max(1e-12, math.exp(exponent))
            updated_conductances[edge_id] = float(conductance)
        self._state.edges.update(updated_conductances)
        self._state.cached_quantities["edge_curvature"] = edge_curvature

    def _compute_edge_labels(self) -> None:
        edge_label_selection = self._params.constitutive_semantic_modes[
            "edge_label_selection"
        ]
        edge_ids = tuple(self._state.topology.iter_live_edge_ids())
        self._state.geometric_length = {}
        self._state.temporal_delay = {}
        self._state.flux_coupling = {}
        selected_labels = (
            set(_ALLOWED_EDGE_LABELS)
            if edge_label_selection == "all"
            else set(edge_label_selection)
        )
        edge_label_computation_mode: dict[str, str] = {}
        edge_label_params: dict[str, dict[str, Any]] = {}
        if "geometric_length" in selected_labels:
            mode = self._geometric_length_mode()
            edge_label_computation_mode["geometric_length"] = mode
            edge_label_params["geometric_length"] = {"mode": mode}
            for edge_id in edge_ids:
                self._state.geometric_length[edge_id] = self._compute_geometric_length(edge_id)
        if "flux_coupling" in selected_labels:
            edge_label_computation_mode["flux_coupling"] = "absolute_flux"
            edge_label_params["flux_coupling"] = {"mode": "absolute_flux"}
            for edge_id in edge_ids:
                primary_node = self._primary_flux_node(edge_id)
                self._state.flux_coupling[edge_id] = abs(
                    self._state.flux.get((edge_id, primary_node), 0.0)
                )
        if "temporal_delay" in selected_labels:
            edge_label_computation_mode["temporal_delay"] = "transport_ratio"
            v0 = _as_float(self._params.evolution.get("temporal_v0", 1.0), context="temporal_v0")
            rho = _as_float(self._params.evolution.get("temporal_rho", 1.0), context="temporal_rho")
            eps_tau = _as_float(self._params.evolution.get("eps_tau", 1e-12), context="eps_tau")
            edge_label_params["temporal_delay"] = {
                "mode": "transport_ratio",
                "v0": v0,
                "rho": rho,
                "eps_tau": eps_tau,
            }
            for edge_id in edge_ids:
                geometric_length = self._state.geometric_length.get(
                    edge_id, self._compute_geometric_length(edge_id)
                )
                primary_node = self._primary_flux_node(edge_id)
                flux_coupling = self._state.flux_coupling.get(
                    edge_id,
                    abs(self._state.flux.get((edge_id, primary_node), 0.0)),
                )
                self._state.temporal_delay[edge_id] = geometric_length / (
                    v0 + rho * flux_coupling + eps_tau
                )

        self._state.cached_quantities["edge_label_computation_mode"] = edge_label_computation_mode
        self._state.cached_quantities["edge_label_params"] = {
            "selection": (
                "all" if edge_label_selection == "all" else tuple(sorted(selected_labels))
            ),
            **edge_label_params,
        }

    def _build_laplacian_if_required(self) -> None:
        self._state.cached_quantities["laplacian_required"] = bool(self._state.edges)

    def _compute_potential(self) -> None:
        kappa_c = _as_float(self._params.evolution["kappa_c"], context="kappa_c")
        site_selection = self._params.evolution["site_potential_selection"]
        site_params = self._params.evolution["site_potential_params"]
        for node_id in self._state.topology.iter_live_node_ids():
            coherence = float(self._state.nodes.get(node_id, 0.0))
            interaction_term = 0.0
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                neighbor_coherence = float(self._state.nodes.get(neighbor_id, 0.0))
                interaction_term += self._state.edges.get(edge_id, 0.0) * (
                    coherence - neighbor_coherence
                )
            site_term = self._site_potential_derivative(
                coherence=coherence,
                selection=site_selection,
                params=site_params,
            )
            self._state.potential[node_id] = kappa_c * interaction_term - site_term

    def _compute_flux(self) -> None:
        eta = _as_float(self._params.evolution["eta"], context="eta")
        for edge_id in self._state.topology.iter_live_edge_ids():
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            potential_a = self._state.potential.get(node_a, 0.0)
            potential_b = self._state.potential.get(node_b, 0.0)
            conductance = self._state.edges.get(edge_id, 1.0)
            flux_value = -eta * conductance * (potential_a - potential_b)
            self._state.flux[(edge_id, node_a)] = flux_value
            self._state.flux[(edge_id, node_b)] = -flux_value

    def _detect_identities(self) -> None:
        sinks: set[int] = set()
        basins: dict[int, set[int]] = {}
        live_node_ids = tuple(self._state.topology.iter_live_node_ids())
        successor_map: dict[int, int | None] = {node_id: None for node_id in live_node_ids}

        for node_id in live_node_ids:
            total_incoming_flux = 0.0
            violates_sink_inflow_condition = False
            outgoing_candidates: list[tuple[float, int, int]] = []
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                outgoing_flux = self._state.flux.get((edge_id, node_id), 0.0)
                # The v2 paper defines a sink s by the stricter incoming condition:
                # J_js >= 0 for every incident neighbor j, with strictly positive
                # total incoming flux sum_j J_js.
                incoming_flux = self._state.flux.get((edge_id, neighbor_id), 0.0)
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

    def _detect_events(self) -> list[GRCEvent]:
        spark_backend = self._spark_backend()
        if spark_backend != "cheeger_proxy":
            raise InvalidStateTransitionError(
                f"unsupported spark_backend {spark_backend!r}"
            )

        threshold, threshold_source = self._spark_threshold()
        candidates: list[tuple[float, int, tuple[int, ...], float, float, float]] = []
        for sink_node_id in sorted(self._state.sink_set):
            basin_members = tuple(sorted(self._state.basins.get(sink_node_id, {sink_node_id})))
            score, boundary_cut, basin_volume, complement_volume = (
                self._cheeger_conductance(basin_members)
            )
            if score < threshold:
                candidates.append(
                    (
                        score,
                        sink_node_id,
                        basin_members,
                        boundary_cut,
                        basin_volume,
                        complement_volume,
                    )
                )

        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        spark_events: list[GRCEvent] = []
        for candidate_rank, (
            score,
            sink_node_id,
            basin_members,
            boundary_cut,
            basin_volume,
            complement_volume,
        ) in enumerate(candidates):
            spark_events.append(
                GRCEvent(
                    kind="spark",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={
                        "backend": spark_backend,
                        "sink_node_id": sink_node_id,
                        "basin_members": list(basin_members),
                        "score": score,
                        "threshold": threshold,
                        "threshold_source": threshold_source,
                        "boundary_cut": boundary_cut,
                        "basin_volume": basin_volume,
                        "complement_volume": complement_volume,
                        "candidate_rank": candidate_rank,
                        "topology_event_kind": "soft_split",
                    },
                )
            )
        return spark_events

    def _apply_topology_changes(self, events: list[GRCEvent]) -> None:
        unsupported_events = [event for event in events if event.kind != "spark"]
        if unsupported_events:
            raise InvalidStateTransitionError(
                "GRCV2 topology changes are not implemented until later Phase 4 iterations"
            )
        self._progress_split_registry()
        if events:
            self._state.cached_quantities["pending_topology_events"] = [
                {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "payload": dict(event.payload),
                }
                for event in events
            ]
            for event in events:
                self._initialize_split_from_event(event)

    def _apply_front_birth(self) -> None:
        lambda_birth = _as_float(self._params.evolution["lambda_birth"], context="lambda_birth")
        alpha_seed = _as_float(self._params.evolution["alpha_seed"], context="alpha_seed")
        dt = self._params.dt
        self._state.cached_quantities["birth_rule_mode"] = "bernoulli_probability"
        rng = self._runtime_rng()
        birth_candidates: list[tuple[int, float, float, float]] = []
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            outward_flux = sum(
                max(0.0, float(self._state.flux.get((edge_id, node_id), 0.0)))
                for edge_id in self._state.topology.incident_edge_ids(node_id)
            )
            parent_mass = float(self._state.nodes.get(node_id, 0.0))
            if outward_flux <= 0.0 or parent_mass <= 0.0:
                continue
            birth_probability = 1.0 - math.exp(-lambda_birth * outward_flux)
            rng_sample = rng.random()
            if rng_sample < birth_probability:
                birth_candidates.append((node_id, outward_flux, birth_probability, rng_sample))
        self._state.rng_state = rng.getstate()

        for node_id, outward_flux, birth_probability, rng_sample in birth_candidates:
            parent_mass = float(self._state.nodes.get(node_id, 0.0))
            seed_mass = min(parent_mass, alpha_seed * outward_flux * dt)
            if seed_mass <= 0.0:
                continue
            new_node_id = self._state.topology.add_node(
                {"kind": "birth", "parent_node_id": node_id}
            )
            seed_weight = max(1e-6, alpha_seed * outward_flux)
            new_edge_id = self._state.topology.add_edge(
                node_id,
                new_node_id,
                {"kind": "birth", "parent_node_id": node_id},
            )
            self._state.nodes[node_id] = parent_mass - seed_mass
            self._state.nodes[new_node_id] = seed_mass
            self._state.potential[new_node_id] = 0.0
            self._state.edges[new_edge_id] = seed_weight
            self._state.flux[(new_edge_id, node_id)] = 0.0
            self._state.flux[(new_edge_id, new_node_id)] = -0.0
            self._append_current_step_event(
                GRCEvent(
                    kind="birth",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={
                        "parent_node_id": node_id,
                        "child_node_id": new_node_id,
                        "edge_id": new_edge_id,
                        "seed_mass": seed_mass,
                        "seed_weight": seed_weight,
                        "outward_flux": outward_flux,
                        "birth_probability": birth_probability,
                        "rng_sample": rng_sample,
                    },
                )
            )

    def _apply_boundary_behavior(self) -> None:
        boundary_mode = self._params.constitutive_semantic_modes["boundary_mode"]
        if boundary_mode == "prune":
            self._apply_prune_boundary()
            return None
        raise InvalidStateTransitionError(
            f"GRCV2 boundary_mode {boundary_mode!r} is not implemented yet"
        )

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
            self._state.nodes[node_id] = float(
                self._state.nodes.get(node_id, 0.0) + coherence_deltas[node_id]
            )
        self._state.cached_quantities["last_continuity_delta"] = dict(coherence_deltas)

    def _enforce_budget(self) -> None:
        negative_mass_correction = 0.0
        for node_id in sorted(self._state.nodes):
            coherence = float(self._state.nodes[node_id])
            if coherence < 0.0:
                negative_mass_correction += -coherence
                self._state.nodes[node_id] = 0.0

        abundance = float(sum(self._state.nodes.values()))
        if self._state.budget_target == 0.0:
            self._state.budget_target = abundance
        correction = float(self._state.budget_target - abundance)
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        if correction > 0.0:
            if live_node_ids:
                target_node_id = live_node_ids[0]
                self._state.nodes[target_node_id] = float(
                    self._state.nodes.get(target_node_id, 0.0) + correction
                )
            else:
                self._state.remainder = correction
                return
        elif correction < 0.0:
            remaining_removal = -correction
            for node_id in live_node_ids:
                if remaining_removal <= 0.0:
                    break
                available = float(self._state.nodes.get(node_id, 0.0))
                removal = min(available, remaining_removal)
                self._state.nodes[node_id] = float(available - removal)
                remaining_removal -= removal
            if remaining_removal > 1e-12:
                self._state.remainder = -remaining_removal
                self._state.cached_quantities["negative_mass_correction"] = float(
                    negative_mass_correction
                )
                self._state.cached_quantities["last_budget_error"] = float(
                    -remaining_removal
                )
                if any(coherence < 0.0 for coherence in self._state.nodes.values()):
                    raise InvalidStateTransitionError(
                        "GRCV2 coherence must remain non-negative after budget correction"
                    )
                return

        corrected_abundance = float(sum(self._state.nodes.values()))
        budget_error = corrected_abundance - self._state.budget_target
        self._state.remainder = 0.0 if abs(budget_error) <= 1e-12 else float(budget_error)
        if any(coherence < 0.0 for coherence in self._state.nodes.values()):
            raise InvalidStateTransitionError(
                "GRCV2 coherence must remain non-negative after budget correction"
            )
        self._state.cached_quantities["last_budget_error"] = float(budget_error)
        self._state.cached_quantities["negative_mass_correction"] = float(
            negative_mass_correction
        )

    def _geometric_length_mode(self) -> str:
        frame_mode = self._params.constitutive_semantic_modes["frame_mode"]
        if frame_mode == "host_embedding":
            return "ambient_metric"
        if frame_mode == "induced_local_frame":
            return "induced_intrinsic"
        return "intrinsic_surrogate"

    def _compute_geometric_length(self, edge_id: int) -> float:
        mode = self._geometric_length_mode()
        if mode == "ambient_metric":
            payload = self._state.topology.edge_payload(edge_id)
            ambient_length = payload.get("ambient_length", 1.0)
            return max(1e-12, _as_float(ambient_length, context="ambient_length"))
        if mode == "induced_intrinsic":
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            coherence_a = float(self._state.nodes.get(node_a, 0.0))
            coherence_b = float(self._state.nodes.get(node_b, 0.0))
            return max(1e-12, 2.0 / (1.0 + coherence_a + coherence_b))
        conductance = float(self._state.edges.get(edge_id, 1.0))
        return max(1e-12, 1.0 / (conductance + 1e-12))

    def _primary_flux_node(self, edge_id: int) -> int:
        node_a, node_b = self._state.topology.edge_endpoints(edge_id)
        return min(node_a, node_b)

    def _curvature_term(self, *, node_id: int, neighbors: tuple[int, ...]) -> float:
        backend = self._params.constitutive_semantic_modes["curvature_backend"]
        if backend == "none":
            return 0.0
        if not neighbors:
            return 0.0
        incident_edges = tuple(self._state.topology.incident_edge_ids(node_id))
        if not incident_edges:
            return 0.0
        edge_curvatures = [
            self._edge_curvature_term(
                edge_id=edge_id,
                node_a=self._state.topology.edge_endpoints(edge_id)[0],
                node_b=self._state.topology.edge_endpoints(edge_id)[1],
            )
            for edge_id in incident_edges
        ]
        return float(sum(edge_curvatures) / len(edge_curvatures))

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
        raise InvalidStateTransitionError(f"unsupported curvature_backend {backend!r}")

    def _site_potential_derivative(
        self,
        *,
        coherence: float,
        selection: Any,
        params: Any,
    ) -> float:
        if not isinstance(selection, str):
            raise InvalidStateTransitionError("site_potential_selection must be a string")
        if not isinstance(params, Mapping):
            raise InvalidStateTransitionError("site_potential_params must be a mapping")

        if selection == "quadratic":
            mu = _as_float(params.get("mu", 0.0), context="site_potential_params.mu")
            scale = _as_float(
                params.get("scale", 1.0), context="site_potential_params.scale"
            )
            return 2.0 * scale * coherence + mu
        if selection == "linear":
            bias = _as_float(
                params.get("bias", 0.0), context="site_potential_params.bias"
            )
            scale = _as_float(
                params.get("scale", 1.0), context="site_potential_params.scale"
            )
            return scale + bias

        raise InvalidStateTransitionError(
            f"unsupported site_potential_selection {selection!r}"
        )

    def _default_rng_state(self) -> Any:
        rng_seed = int(self._params.evolution.get("rng_seed", 0))
        rng = random.Random(rng_seed)
        return rng.getstate()

    def _runtime_rng(self) -> random.Random:
        rng = random.Random()
        rng_state = self._state.rng_state
        if rng_state is None:
            rng_state = self._default_rng_state()
            self._state.rng_state = rng_state
        rng.setstate(rng_state)
        return rng

    def _current_edge_weight(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        weight_source = self._state.edges if edge_weights is None else edge_weights
        return max(1e-12, float(weight_source.get(edge_id, 1.0)))

    def _current_node_weight(self, node_id: int) -> float:
        return max(1e-12, float(self._state.nodes.get(node_id, 0.0)))

    def _edge_length_cost(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        return 1.0 / self._current_edge_weight(edge_id, edge_weights=edge_weights)

    def _neighbor_measure(
        self,
        node_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> list[tuple[int, float]]:
        incident_edges = tuple(self._state.topology.incident_edge_ids(node_id))
        if not incident_edges:
            return [(node_id, 1.0)]
        weighted_neighbors: list[tuple[int, float]] = []
        total_weight = 0.0
        for edge_id in incident_edges:
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == node_id else node_a
            weight = self._current_edge_weight(edge_id, edge_weights=edge_weights)
            weighted_neighbors.append((neighbor_id, weight))
            total_weight += weight
        if total_weight <= 0.0:
            return [(node_id, 1.0)]
        return [
            (neighbor_id, weight / total_weight)
            for neighbor_id, weight in weighted_neighbors
        ]

    def _shortest_path_distance(
        self,
        source_node_id: int,
        target_node_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        if source_node_id == target_node_id:
            return 0.0
        distances: dict[int, float] = {source_node_id: 0.0}
        frontier: list[tuple[float, int]] = [(0.0, source_node_id)]
        while frontier:
            current_distance, node_id = heapq.heappop(frontier)
            if node_id == target_node_id:
                return current_distance
            if current_distance > distances.get(node_id, math.inf):
                continue
            for edge_id in self._state.topology.incident_edge_ids(node_id):
                node_a, node_b = self._state.topology.edge_endpoints(edge_id)
                neighbor_id = node_b if node_a == node_id else node_a
                candidate_distance = current_distance + self._edge_length_cost(
                    edge_id,
                    edge_weights=edge_weights,
                )
                if candidate_distance + 1e-15 < distances.get(neighbor_id, math.inf):
                    distances[neighbor_id] = candidate_distance
                    heapq.heappush(frontier, (candidate_distance, neighbor_id))
        return math.inf

    def _earth_movers_distance(
        self,
        left_measure: list[tuple[int, float]],
        right_measure: list[tuple[int, float]],
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        node_count = 2 + len(left_measure) + len(right_measure)
        source = 0
        sink = node_count - 1
        graph: list[list[list[float | int]]] = [[] for _ in range(node_count)]

        def add_edge(start: int, end: int, capacity: float, cost: float) -> None:
            forward = [end, len(graph[end]), capacity, cost]
            backward = [start, len(graph[start]), 0.0, -cost]
            graph[start].append(forward)
            graph[end].append(backward)

        for index, (_, supply) in enumerate(left_measure):
            add_edge(source, 1 + index, supply, 0.0)
        for left_index, (left_node_id, _) in enumerate(left_measure):
            for right_index, (right_node_id, _) in enumerate(right_measure):
                add_edge(
                    1 + left_index,
                    1 + len(left_measure) + right_index,
                    1.0,
                    self._shortest_path_distance(
                        left_node_id,
                        right_node_id,
                        edge_weights=edge_weights,
                    ),
                )
        for index, (_, demand) in enumerate(right_measure):
            add_edge(1 + len(left_measure) + index, sink, demand, 0.0)

        required_flow = min(
            sum(weight for _, weight in left_measure),
            sum(weight for _, weight in right_measure),
        )
        flow = 0.0
        total_cost = 0.0
        eps = 1e-12
        while flow + eps < required_flow:
            distances = [math.inf] * node_count
            previous_node = [-1] * node_count
            previous_edge = [-1] * node_count
            distances[source] = 0.0
            for _ in range(node_count - 1):
                updated = False
                for node_id in range(node_count):
                    if distances[node_id] == math.inf:
                        continue
                    for edge_index, edge in enumerate(graph[node_id]):
                        target_id = int(edge[0])
                        capacity = float(edge[2])
                        cost = float(edge[3])
                        if capacity <= eps:
                            continue
                        candidate = distances[node_id] + cost
                        if candidate + 1e-15 < distances[target_id]:
                            distances[target_id] = candidate
                            previous_node[target_id] = node_id
                            previous_edge[target_id] = edge_index
                            updated = True
                if not updated:
                    break
            if distances[sink] == math.inf:
                raise InvalidStateTransitionError("unable to compute Ollivier transport plan")

            augment = required_flow - flow
            node_id = sink
            while node_id != source:
                edge = graph[previous_node[node_id]][previous_edge[node_id]]
                augment = min(augment, float(edge[2]))
                node_id = previous_node[node_id]

            node_id = sink
            while node_id != source:
                edge = graph[previous_node[node_id]][previous_edge[node_id]]
                reverse = graph[node_id][int(edge[1])]
                edge[2] = float(edge[2]) - augment
                reverse[2] = float(reverse[2]) + augment
                node_id = previous_node[node_id]

            flow += augment
            total_cost += augment * distances[sink]
        return total_cost

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
            raise InvalidStateTransitionError("edge distance must remain positive")
        transport_cost = self._earth_movers_distance(
            self._neighbor_measure(node_a, edge_weights=edge_weights),
            self._neighbor_measure(node_b, edge_weights=edge_weights),
            edge_weights=edge_weights,
        )
        return float(1.0 - transport_cost / edge_distance)

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
            visited.add(node_id)
            if node_id in sinks:
                return node_id
            node_id = successor_map.get(node_id)
            if node_id in visited:
                return None
        return None

    def _append_current_step_event(self, event: GRCEvent) -> None:
        current_step_events = self._state.cached_quantities.get("current_step_events")
        if not isinstance(current_step_events, list):
            current_step_events = []
            self._state.cached_quantities["current_step_events"] = current_step_events
        current_step_events.append(event)

    def _spark_backend(self) -> str:
        spark_backend = self._params.evolution.get("spark_backend", "cheeger_proxy")
        if not isinstance(spark_backend, str):
            raise InvalidStateTransitionError("spark_backend must be a string")
        return spark_backend

    def _spark_threshold(self) -> tuple[float, str]:
        if "h_thr" in self._params.evolution:
            return (
                _as_float(self._params.evolution["h_thr"], context="h_thr"),
                "h_thr",
            )
        return (
            _as_float(self._params.evolution["eps_spark"], context="eps_spark"),
            "eps_spark",
        )

    def _cheeger_conductance(
        self,
        basin_members: tuple[int, ...],
    ) -> tuple[float, float, float, float]:
        if not basin_members:
            return (math.inf, 0.0, 0.0, 0.0)

        basin_set = set(basin_members)
        live_node_ids = set(self._state.topology.iter_live_node_ids())
        complement_nodes = live_node_ids - basin_set
        if not complement_nodes:
            return (math.inf, 0.0, 0.0, 0.0)

        boundary_cut = 0.0
        basin_volume = 0.0
        complement_volume = 0.0

        for edge_id in self._state.topology.iter_live_edge_ids():
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            weight = float(self._state.edges.get(edge_id, 0.0))
            node_a_in_basin = node_a in basin_set
            node_b_in_basin = node_b in basin_set
            if node_a_in_basin:
                basin_volume += weight
            else:
                complement_volume += weight
            if node_b_in_basin:
                basin_volume += weight
            else:
                complement_volume += weight
            if node_a_in_basin != node_b_in_basin:
                boundary_cut += weight

        denominator = min(basin_volume, complement_volume)
        if denominator <= 0.0:
            return (math.inf, boundary_cut, basin_volume, complement_volume)
        return (
            boundary_cut / denominator,
            boundary_cut,
            basin_volume,
            complement_volume,
        )

    def _progress_split_registry(self) -> None:
        if not self._state.split_registry:
            return
        total_steps = max(
            1,
            int(math.ceil(_as_float(self._params.evolution["tau_split"], context="tau_split"))),
        )
        for registry_key in sorted(self._state.split_registry):
            entry = self._state.split_registry[registry_key]
            if not isinstance(entry, Mapping):
                continue
            if bool(entry.get("complete", False)):
                continue
            parent_node_id = int(entry["parent_node_id"])
            progress_step = int(entry.get("progress_step", 0)) + 1
            fraction = min(1.0, progress_step / total_steps)
            initial_weight = float(entry.get("initial_edge_weight", 1e-6))

            for edge_info in entry.get("child_edge_targets", []):
                edge_id = int(edge_info["edge_id"])
                target_weight = float(edge_info["target_weight"])
                self._state.edges[edge_id] = initial_weight + fraction * (
                    target_weight - initial_weight
                )

            for edge_id in entry.get("split_link_edge_ids", []):
                edge_id_int = int(edge_id)
                target_weight = float(entry.get("split_link_target_weight", initial_weight))
                self._state.edges[edge_id_int] = initial_weight + fraction * (
                    target_weight - initial_weight
                )

            entry["progress_step"] = progress_step
            entry["progress_fraction"] = fraction
            self._append_current_step_event(
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
                entry["complete"] = True
                entry["parent_removed"] = True
                self._append_current_step_event(
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

    def _initialize_split_from_event(self, event: GRCEvent) -> None:
        if event.kind != "spark":
            return
        sink_node_id = int(event.payload["sink_node_id"])
        if not self._state.topology.has_node(sink_node_id):
            return
        if any(
            isinstance(entry, Mapping)
            and not bool(entry.get("complete", False))
            and int(entry.get("parent_node_id", -1)) == sink_node_id
            for entry in self._state.split_registry.values()
        ):
            return
        split_distribution_mode = self._params.constitutive_semantic_modes[
            "split_distribution_mode"
        ]
        if split_distribution_mode != "equal":
            raise InvalidStateTransitionError(
                f"unsupported split_distribution_mode {split_distribution_mode!r}"
            )

        parent_mass = float(self._state.nodes.get(sink_node_id, 0.0))
        split_ratio = 0.5
        child_masses = [parent_mass * split_ratio, parent_mass * (1.0 - split_ratio)]
        initial_edge_weight = 1e-6
        split_link_target_weight = max(
            1e-6,
            _as_float(self._params.evolution["alpha_seed"], context="alpha_seed"),
        )

        parent_neighbors: list[tuple[int, float, dict[str, Any]]] = []
        for edge_id in self._state.topology.incident_edge_ids(sink_node_id):
            node_a, node_b = self._state.topology.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == sink_node_id else node_a
            parent_neighbors.append(
                (
                    neighbor_id,
                    float(self._state.edges.get(edge_id, 1.0)),
                    dict(self._state.topology.edge_payload(edge_id)),
                )
            )
        parent_neighbors.sort(key=lambda item: item[0])

        child_node_ids: list[int] = []
        split_link_edge_ids: list[int] = []
        child_edge_targets: list[dict[str, Any]] = []
        for child_index, child_mass in enumerate(child_masses):
            child_node_id = self._state.topology.add_node(
                {
                    "kind": "split_child",
                    "parent_node_id": sink_node_id,
                    "child_index": child_index,
                }
            )
            child_node_ids.append(child_node_id)
            self._state.nodes[child_node_id] = child_mass
            self._state.potential[child_node_id] = 0.0

            split_link_edge_id = self._state.topology.add_edge(
                sink_node_id,
                child_node_id,
                {"kind": "split_link", "parent_node_id": sink_node_id},
            )
            split_link_edge_ids.append(split_link_edge_id)
            self._state.edges[split_link_edge_id] = initial_edge_weight
            self._state.flux[(split_link_edge_id, sink_node_id)] = 0.0
            self._state.flux[(split_link_edge_id, child_node_id)] = -0.0

            child_ratio = split_ratio if child_index == 0 else (1.0 - split_ratio)
            for neighbor_id, parent_edge_weight, payload in parent_neighbors:
                child_edge_id = self._state.topology.add_edge(
                    child_node_id,
                    neighbor_id,
                    {
                        **payload,
                        "kind": "split_child_neighbor",
                        "parent_node_id": sink_node_id,
                        "child_node_id": child_node_id,
                    },
                )
                target_weight = max(1e-6, parent_edge_weight * child_ratio)
                self._state.edges[child_edge_id] = initial_edge_weight
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

        self._state.nodes[sink_node_id] = 0.0
        registry_key = (
            f"split:{self._state.step_index}:{sink_node_id}:"
            f"{int(event.payload.get('candidate_rank', 0))}"
        )
        self._state.split_registry[registry_key] = {
            "parent_node_id": sink_node_id,
            "child_node_ids": child_node_ids,
            "split_ratio": split_ratio,
            "progress_step": 0,
            "progress_fraction": 0.0,
            "total_steps": max(
                1,
                int(
                    math.ceil(
                        _as_float(self._params.evolution["tau_split"], context="tau_split")
                    )
                ),
            ),
            "complete": False,
            "parent_removed": False,
            "initial_parent_mass": parent_mass,
            "initial_edge_weight": initial_edge_weight,
            "split_link_target_weight": split_link_target_weight,
            "split_link_edge_ids": split_link_edge_ids,
            "child_edge_targets": child_edge_targets,
        }
        self._append_current_step_event(
            GRCEvent(
                kind="split_init",
                step_index=self._state.step_index,
                source_family=self.MODEL_FAMILY,
                payload={
                    "registry_key": registry_key,
                    "parent_node_id": sink_node_id,
                    "child_node_ids": list(child_node_ids),
                    "split_ratio": split_ratio,
                },
            )
        )

    def _apply_prune_boundary(self) -> None:
        eps_prune = _as_float(self._params.evolution["eps_prune"], context="eps_prune")
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        prune_candidates = [
            node_id
            for node_id in live_node_ids
            if len(tuple(self._state.topology.incident_edge_ids(node_id))) == 0
            and float(self._state.nodes.get(node_id, 0.0)) < eps_prune
        ]
        if not prune_candidates or len(prune_candidates) == len(live_node_ids):
            return

        redistributed_mass = float(
            sum(self._state.nodes.get(node_id, 0.0) for node_id in prune_candidates)
        )
        for node_id in prune_candidates:
            self._state.topology.remove_node(node_id)
        self._cleanup_state_against_live_topology()

        survivors = tuple(sorted(self._state.topology.iter_live_node_ids()))
        if survivors and redistributed_mass > 0.0:
            share = redistributed_mass / len(survivors)
            for node_id in survivors:
                self._state.nodes[node_id] = float(self._state.nodes.get(node_id, 0.0) + share)

        for node_id in prune_candidates:
            self._append_current_step_event(
                GRCEvent(
                    kind="prune",
                    step_index=self._state.step_index,
                    source_family=self.MODEL_FAMILY,
                    payload={"node_id": node_id, "redistributed_mass": redistributed_mass},
                )
            )

    def _cleanup_state_against_live_topology(self) -> None:
        live_node_ids = set(self._state.topology.iter_live_node_ids())
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())
        self._state.nodes = {
            node_id: value
            for node_id, value in self._state.nodes.items()
            if node_id in live_node_ids
        }
        self._state.potential = {
            node_id: value
            for node_id, value in self._state.potential.items()
            if node_id in live_node_ids
        }
        self._state.edges = {
            edge_id: value
            for edge_id, value in self._state.edges.items()
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
            oriented_edge_id: value
            for oriented_edge_id, value in self._state.flux.items()
            if oriented_edge_id[0] in live_edge_ids and oriented_edge_id[1] in live_node_ids
        }
        self._state.sink_set = {
            node_id for node_id in self._state.sink_set if node_id in live_node_ids
        }
        self._state.basins = {
            sink_node_id: {member for member in members if member in live_node_ids}
            for sink_node_id, members in self._state.basins.items()
            if sink_node_id in live_node_ids
        }

    def _refresh_post_step_identity_state(self) -> None:
        self._cleanup_state_against_live_topology()
        self._detect_identities()

    def _validate_state(self, state: GRCV2State) -> None:
        if not isinstance(state.topology, WeightedGraphBackend):
            raise InvalidStateTransitionError(
                "GRCV2State.topology must be a WeightedGraphBackend"
            )
        live_node_ids = set(state.topology.iter_live_node_ids())
        live_edge_ids = set(state.topology.iter_live_edge_ids())
        if any(node_id not in live_node_ids for node_id in state.nodes):
            raise InvalidStateTransitionError(
                "GRCV2State.nodes keys must reference live topology nodes"
            )
        if any(edge_id not in live_edge_ids for edge_id in state.edges):
            raise InvalidStateTransitionError(
                "GRCV2State.edges keys must reference live topology edges"
            )
        for label_mapping in (
            state.geometric_length,
            state.temporal_delay,
            state.flux_coupling,
        ):
            if any(edge_id not in live_edge_ids for edge_id in label_mapping):
                raise InvalidStateTransitionError(
                    "GRCV2 edge-label keys must reference live topology edges"
                )
        if any(node_id not in live_node_ids for node_id in state.potential):
            raise InvalidStateTransitionError(
                "GRCV2State.potential keys must reference live topology nodes"
            )
        if any(node_id not in live_node_ids for node_id in state.sink_set):
            raise InvalidStateTransitionError(
                "GRCV2State.sink_set must reference live topology nodes"
            )
        if any(node_id not in live_node_ids for node_id in state.basins):
            raise InvalidStateTransitionError(
                "GRCV2State.basins keys must reference live topology nodes"
            )
        for members in state.basins.values():
            if any(node_id not in live_node_ids for node_id in members):
                raise InvalidStateTransitionError(
                    "GRCV2State.basins memberships must reference live topology nodes"
                )
        for (edge_id, source_node_id), flux_value in state.flux.items():
            if edge_id not in live_edge_ids or source_node_id not in live_node_ids:
                raise InvalidStateTransitionError(
                    "GRCV2State.flux keys must reference live topology edges/nodes"
                )
            if not isinstance(flux_value, float):
                raise InvalidStateTransitionError(
                    "GRCV2State.flux values must be floats"
                )
        if any(coherence < 0.0 for coherence in state.nodes.values()):
            raise InvalidStateTransitionError(
                "GRCV2State.nodes coherence values must be non-negative"
            )

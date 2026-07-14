"""Construction/state surface for the Phase 6 GRC9 model shell."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from enum import Enum
import heapq
import math
from typing import Any
import random

from pygrc.core import (
    GRC9_CAPABILITY_PROFILE,
    GRCEvent,
    GRCModel,
    GRCParams,
    InvalidParamsError,
    InvalidStateTransitionError,
    ObservableMap,
    PortGraphBackend,
    SnapshotCompatibilityError,
    StepResult,
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
from .grc_9_expansion import (
    CANONICAL_CORE_SPINE_PORTS,
    PRIMARY_SATELLITE_COLUMNS,
    aggregate_bond_conductance,
    boundary_reassignment_order,
    compute_expansion_node_count,
    normalize_expansion_weights,
    round_robin_column_order,
)
from .grc_9_ports import port_id_to_slot, port_to_rc, rc_to_port, slot_to_port_id
from .grc_9_state import (
    AdiabaticExpansionSchedule,
    ExpansionRecord,
    GRC9State,
    PortEdge,
)


_ALLOWED_CURVATURE_BACKENDS = {"ollivier", "forman", "none"}
_ALLOWED_FRAME_MODES = {"fixed_port_chart"}
_ALLOWED_BOUNDARY_MODES = {"prune", "barrier", "ghost"}
_ALLOWED_EXPANSION_DISTRIBUTION_MODES = {"equal", "custom"}
_ALLOWED_EDGE_LABELS = {"geometric_length", "temporal_delay", "flux_coupling"}
_ALLOWED_GROWTH_PARENT_ELIGIBILITY = {
    "legacy_any_inactive_port",
    "grc9_front_capacity",
}
_ALLOWED_GROWTH_FRONT_CAPACITY_SOURCES = {
    "closed_front_capacity",
    "preexisting_front",
    "preexisting_front_capacity",
    "pressure_boundary",
    "propagated_front_growth",
    "refinement_boundary_capacity",
    "spark_expansion_front",
    "spark_refinement_boundary_front",
    "spark_refinement_front",
}
_DEFAULT_TEMPORAL_LABEL_PARAMS = {"v0": 1.0, "rho": 1.0, "eps_tau": 1e-12}


class SparkKind(str, Enum):
    """Deterministic spark classification vocabulary for the GRC9 trigger."""

    SATURATION_INSTABILITY = "saturation_instability"
    SATURATION_COLUMN_PROXY = "saturation_column_proxy"
    SATURATION_SIGN_CROSSING = "saturation_sign_crossing"


def _coerce_plain_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return dict(value)


def _restore_numeric_mapping(
    value: Any,
    *,
    context: str,
) -> dict[int, float]:
    mapping = _coerce_plain_mapping(value, context=context)
    restored: dict[int, float] = {}
    for raw_key, raw_value in mapping.items():
        if isinstance(raw_key, int):
            key = raw_key
        elif isinstance(raw_key, str):
            try:
                key = int(raw_key)
            except ValueError as exc:
                raise SnapshotCompatibilityError(
                    f"{context} keys must be int-compatible"
                ) from exc
        else:
            raise SnapshotCompatibilityError(f"{context} keys must be int-compatible")
        if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
            raise SnapshotCompatibilityError(
                f"{context} values must be float-compatible numbers"
            )
        restored[key] = float(raw_value)
    return restored


def _restore_basin_mapping(value: Any, *, context: str) -> dict[int, set[int]]:
    mapping = _coerce_plain_mapping(value, context=context)
    restored: dict[int, set[int]] = {}
    for raw_key, raw_members in mapping.items():
        if isinstance(raw_key, int):
            key = raw_key
        elif isinstance(raw_key, str):
            try:
                key = int(raw_key)
            except ValueError as exc:
                raise SnapshotCompatibilityError(
                    f"{context} keys must be int-compatible node IDs"
                ) from exc
        else:
            raise SnapshotCompatibilityError(
                f"{context} keys must be int-compatible node IDs"
            )
        if not isinstance(raw_members, (list, tuple, set)):
            raise SnapshotCompatibilityError(
                f"{context} values must be collections of node IDs"
            )
        members: set[int] = set()
        for raw_member in raw_members:
            if isinstance(raw_member, int):
                members.add(raw_member)
            elif isinstance(raw_member, str):
                try:
                    members.add(int(raw_member))
                except ValueError as exc:
                    raise SnapshotCompatibilityError(
                        f"{context} members must be int-compatible"
                    ) from exc
            else:
                raise SnapshotCompatibilityError(
                    f"{context} members must be int-compatible"
                )
        restored[key] = members
    return restored


def _restore_event_log(values: Any) -> list[GRCEvent]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise SnapshotCompatibilityError("GRC9 state.event_log must be a list")
    event_log: list[GRCEvent] = []
    for index, raw_event in enumerate(values):
        if not isinstance(raw_event, Mapping):
            raise SnapshotCompatibilityError(
                f"GRC9 state.event_log[{index}] must be a mapping"
            )
        payload = raw_event.get("payload", {})
        if not isinstance(payload, Mapping):
            raise SnapshotCompatibilityError(
                f"GRC9 state.event_log[{index}].payload must be a mapping"
            )
        event_log.append(
            GRCEvent(
                kind=str(raw_event.get("kind", "")),
                step_index=int(raw_event.get("step_index", 0)),
                payload=dict(payload),
                source_family=(
                    None
                    if raw_event.get("source_family") is None
                    else str(raw_event.get("source_family"))
                ),
            )
        )
    return event_log


def _restore_nested_tuple(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_restore_nested_tuple(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_restore_nested_tuple(item) for item in value)
    return value


def _restore_rng_state(value: Any) -> Any:
    restored = deserialize_rng_state(value)
    if (
        isinstance(restored, list | tuple)
        and len(restored) == 3
        and isinstance(restored[0], int)
    ):
        return _restore_nested_tuple(restored)
    return restored


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


def _validate_edge_label_selection(selection: Any) -> None:
    if selection == "all":
        return
    if not isinstance(selection, (list, tuple, set, frozenset)):
        raise InvalidParamsError(
            "edge_label_selection must be 'all' or an iterable of label names"
        )
    normalized = set(selection)
    unknown = normalized - _ALLOWED_EDGE_LABELS
    if unknown:
        raise InvalidParamsError(
            f"edge_label_selection contains unknown labels: {sorted(unknown)}"
        )


def _build_params(config: Mapping[str, Any]) -> GRCParams:
    params_input = dict(config.get("params", config))
    evolution = dict(params_input.get("evolution", {}))
    modes = dict(params_input.get("constitutive_semantic_modes", {}))

    evolution.setdefault("kappa_c", 1.0)
    evolution.setdefault("eta", 1.0)
    evolution.setdefault("tau_instability", 0.5)
    evolution.setdefault("eps_spark", 0.01)
    evolution.setdefault("enable_sign_crossing_spark", False)
    evolution.setdefault("D_eff_target", 30)
    evolution.setdefault("w_bond", 1.0)
    evolution.setdefault("lambda_birth", 0.0)
    evolution.setdefault("alpha_seed", 0.1)
    evolution.setdefault("adiabatic_expansion_substeps", 1)
    evolution.setdefault("site_potential_selection", "quadratic")
    evolution.setdefault("site_potential_params", {"mu": 0.0, "scale": 1.0})

    modes.setdefault("frame_mode", "fixed_port_chart")
    modes.setdefault("curvature_backend", "none")
    modes.setdefault("boundary_mode", "prune")
    modes.setdefault("expansion_distribution_mode", "equal")
    modes.setdefault("edge_label_selection", "all")
    modes.setdefault("growth_parent_eligibility", "legacy_any_inactive_port")

    if modes["frame_mode"] not in _ALLOWED_FRAME_MODES:
        raise InvalidParamsError("frame_mode must be 'fixed_port_chart'")
    if modes["curvature_backend"] not in _ALLOWED_CURVATURE_BACKENDS:
        raise InvalidParamsError(
            "curvature_backend must be one of ollivier, forman, none"
        )
    if modes["boundary_mode"] not in _ALLOWED_BOUNDARY_MODES:
        raise InvalidParamsError("boundary_mode must be one of prune, barrier, ghost")
    if modes["boundary_mode"] != "prune":
        raise InvalidParamsError(
            "Phase 6 GRC9 only implements boundary_mode='prune'; "
            "barrier/ghost remain reserved until explicit boundary behavior "
            "and boundary_barrier capability support are implemented"
        )
    if (
        modes["expansion_distribution_mode"]
        not in _ALLOWED_EXPANSION_DISTRIBUTION_MODES
    ):
        raise InvalidParamsError(
            "expansion_distribution_mode must be one of equal, custom"
        )
    if modes["growth_parent_eligibility"] not in _ALLOWED_GROWTH_PARENT_ELIGIBILITY:
        raise InvalidParamsError(
            "growth_parent_eligibility must be legacy_any_inactive_port "
            "or grc9_front_capacity"
        )
    _validate_edge_label_selection(modes["edge_label_selection"])
    if "rng_seed" in evolution and (
        isinstance(evolution["rng_seed"], bool)
        or not isinstance(evolution["rng_seed"], int)
    ):
        raise InvalidParamsError("rng_seed must be an integer")

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


def _default_rng_state(seed: int = 0) -> Any:
    return random.Random(seed).getstate()


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


def _restore_schedule(raw_value: Any, *, context: str) -> AdiabaticExpansionSchedule | None:
    if raw_value is None:
        return None
    if isinstance(raw_value, AdiabaticExpansionSchedule):
        return raw_value
    if not isinstance(raw_value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
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
    module_node_ids = raw_value.get("module_node_ids", ())
    if not isinstance(module_node_ids, (list, tuple, set)):
        raise SnapshotCompatibilityError(f"{context}.module_node_ids must be list-like")
    distribution_weights = raw_value.get("distribution_weights", ())
    if not isinstance(distribution_weights, (list, tuple)):
        raise SnapshotCompatibilityError(
            f"{context}.distribution_weights must be list-like"
        )
    schedule = _restore_schedule(raw_value.get("schedule"), context=f"{context}.schedule")
    return ExpansionRecord(
        parent_sink_id=int(raw_value.get("parent_sink_id", 0)),
        module_node_ids=tuple(int(node_id) for node_id in module_node_ids),
        expansion_step=int(raw_value.get("expansion_step", 0)),
        distribution_weights=tuple(float(value) for value in distribution_weights),
        schedule=schedule,
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


def _serialize_expansion_record(record: ExpansionRecord) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "parent_sink_id": record.parent_sink_id,
        "module_node_ids": list(record.module_node_ids),
        "expansion_step": record.expansion_step,
        "distribution_weights": list(record.distribution_weights),
    }
    if record.schedule is not None:
        payload["schedule"] = {
            "total_substeps": record.schedule.total_substeps,
            "completed_substeps": record.schedule.completed_substeps,
            "active": record.schedule.active,
        }
    return payload


def _canonical_port_edge(
    *,
    endpoint_a: tuple[int, int],
    endpoint_b: tuple[int, int],
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
    topology: PortGraphBackend,
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
            endpoint_a=endpoint_a,
            endpoint_b=endpoint_b,
            conductance=conductance,
            flux_uv=flux_uv,
        )
    return hydrated


def _initial_budget_sum(state: GRC9State) -> float:
    return float(sum(state.node_coherence.values()))


def _lock_budget_target(
    state: GRC9State,
    *,
    budget_target_provided: bool,
) -> None:
    cached_source = state.cached_quantities.get("budget_target_source")
    if cached_source is not None:
        state.cached_quantities["budget_target_source"] = str(cached_source)
        return
    if budget_target_provided:
        state.cached_quantities["budget_target_source"] = (
            "provided_zero" if state.budget_target == 0.0 else "provided"
        )
        return
    state.budget_target = _initial_budget_sum(state)
    state.cached_quantities["budget_target_source"] = "initial_state_sum"


def _state_from_inputs(
    *,
    params: GRCParams,
    state_mapping: Mapping[str, Any] | None = None,
    topology: PortGraphBackend | None = None,
) -> GRC9State:
    mapping = {} if state_mapping is None else dict(state_mapping)

    topology_payload = topology
    if topology_payload is None:
        topology_input = mapping.get("topology")
        if topology_input is None:
            topology_payload = PortGraphBackend()
        elif isinstance(topology_input, PortGraphBackend):
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
                "GRC9 state topology must be a PortGraphBackend or topology mapping"
            )

    port_edges_mapping = _coerce_plain_mapping(
        mapping.get("port_edges", {}),
        context="GRC9 state.port_edges",
    )
    restored_port_edges = {
        int(edge_id): _restore_port_edge(
            raw_value,
            context=f"GRC9 state.port_edges[{edge_id!r}]",
        )
        for edge_id, raw_value in port_edges_mapping.items()
    }
    port_edges = _hydrate_port_edges_from_topology(
        topology_payload,
        port_edges=restored_port_edges,
    )

    expansion_registry_mapping = _coerce_plain_mapping(
        mapping.get("expansion_registry", {}),
        context="GRC9 state.expansion_registry",
    )
    expansion_registry = {
        str(expansion_id): _restore_expansion_record(
            raw_value,
            context=f"GRC9 state.expansion_registry[{expansion_id!r}]",
        )
        for expansion_id, raw_value in expansion_registry_mapping.items()
    }

    previous_column_mapping = _coerce_plain_mapping(
        mapping.get("prev_column_diagnostic", {}),
        context="GRC9 state.prev_column_diagnostic",
    )
    prev_column_diagnostic = {
        int(node_id): [float(value) for value in values]
        for node_id, values in previous_column_mapping.items()
    }

    state = GRC9State(
        topology=topology_payload,
        node_coherence=_restore_numeric_mapping(
            mapping.get("node_coherence", {}),
            context="GRC9 state.node_coherence",
        ),
        port_edges=port_edges,
        geometric_length=_restore_numeric_mapping(
            mapping.get("geometric_length", {}),
            context="GRC9 state.geometric_length",
        ),
        temporal_delay=_restore_numeric_mapping(
            mapping.get("temporal_delay", {}),
            context="GRC9 state.temporal_delay",
        ),
        flux_coupling=_restore_numeric_mapping(
            mapping.get("flux_coupling", {}),
            context="GRC9 state.flux_coupling",
        ),
        potential=_restore_numeric_mapping(
            mapping.get("potential", {}),
            context="GRC9 state.potential",
        ),
        sink_set=set(
            int(node_id)
            for node_id in mapping.get("sink_set", [])
        ),
        basins=_restore_basin_mapping(
            mapping.get("basins", {}),
            context="GRC9 state.basins",
        ),
        expansion_registry=expansion_registry,
        coarse_cache=_coerce_plain_mapping(
            mapping.get("coarse_cache", {}),
            context="GRC9 state.coarse_cache",
        ),
        prev_column_diagnostic=prev_column_diagnostic,
        edge_label_computation_mode=dict(
            _coerce_plain_mapping(
                mapping.get("edge_label_computation_mode", {}),
                context="GRC9 state.edge_label_computation_mode",
            )
        ),
        edge_label_params=dict(
            _coerce_plain_mapping(
                mapping.get("edge_label_params", {}),
                context="GRC9 state.edge_label_params",
            )
        ),
        step_index=int(mapping.get("step_index", 0)),
        time=float(mapping.get("time", 0.0)),
        budget_target=float(mapping.get("budget_target", 0.0)),
        remainder=float(mapping.get("remainder", 0.0)),
        cached_quantities=dict(
            _coerce_plain_mapping(
                mapping.get("cached_quantities", {}),
                context="GRC9 state.cached_quantities",
            )
        ),
        event_log=_restore_event_log(mapping.get("event_log", [])),
        observables=dict(
            _coerce_plain_mapping(
                mapping.get("observables", {}),
                context="GRC9 state.observables",
            )
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
        seed = int(params.evolution.get("rng_seed", 0))
        state.rng_state = _default_rng_state(seed)
    _lock_budget_target(state, budget_target_provided="budget_target" in mapping)
    return state


def _state_payload_from_state(state: GRC9State) -> dict[str, Any]:
    return {
        "node_coherence": {
            str(node_id): value for node_id, value in state.node_coherence.items()
        },
        "port_edges": {
            str(edge_id): _serialize_port_edge(port_edge)
            for edge_id, port_edge in state.port_edges.items()
        },
        "potential": {str(node_id): value for node_id, value in state.potential.items()},
        "sink_set": sorted(state.sink_set),
        "basins": {
            str(node_id): sorted(members) for node_id, members in state.basins.items()
        },
        "expansion_registry": {
            expansion_id: _serialize_expansion_record(record)
            for expansion_id, record in state.expansion_registry.items()
        },
        "coarse_cache": _stringify_mapping_keys(dict(state.coarse_cache)),
        "prev_column_diagnostic": {
            str(node_id): list(values)
            for node_id, values in state.prev_column_diagnostic.items()
        },
        "edge_label_computation_mode": dict(state.edge_label_computation_mode),
        "edge_label_params": _stringify_mapping_keys(dict(state.edge_label_params)),
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
        "observables": _stringify_mapping_keys(dict(state.observables)),
        "rng_state": serialize_rng_state(state.rng_state),
        "params_identity": state.params_identity,
    }


class GRC9(GRCModel):
    """Phase 6 real model shell for the mechanically explicit GRC9 family."""

    MODEL_FAMILY = "GRC9"
    CAPABILITY_PROFILE = GRC9_CAPABILITY_PROFILE

    def __init__(self, params: GRCParams, state: GRC9State | None = None) -> None:
        self._params = params
        self._state = deepcopy(state) if state is not None else _state_from_inputs(params=params)
        _lock_budget_target(
            self._state,
            budget_target_provided=state is not None and state.budget_target != 0.0,
        )
        self._validate_state(self._state)
        self._initial_state: GRC9State | None = deepcopy(self._state)
        self._reset_baseline_unavailable_reason: str | None = None

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "GRC9":
        params = _build_params(config)
        state_input = config.get("state", {})
        if not isinstance(state_input, Mapping):
            raise InvalidParamsError("state must be a mapping when provided")
        state = _state_from_inputs(params=params, state_mapping=state_input)
        return cls(params=params, state=state)

    @classmethod
    def from_state(
        cls,
        state: Mapping[str, Any] | GRC9State,
        params: Mapping[str, Any],
    ) -> "GRC9":
        resolved_params = _build_params(dict(params))
        if isinstance(state, GRC9State):
            return cls(params=resolved_params, state=deepcopy(state))
        resolved_state = _state_from_inputs(
            params=resolved_params,
            state_mapping=dict(state),
        )
        return cls(params=resolved_params, state=resolved_state)

    @classmethod
    def load(cls, path: str) -> "GRC9":
        snapshot = load_snapshot(path)
        return cls._from_snapshot(snapshot, restore_reset_baseline=True)

    @classmethod
    def _from_snapshot(
        cls,
        snapshot: Mapping[str, Any],
        *,
        restore_reset_baseline: bool = False,
    ) -> "GRC9":
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

        edge_labels_group = snapshot.get("edge_labels", {})
        dynamics = snapshot.get("dynamics", {})
        caches = snapshot.get("caches", {})
        if edge_labels_group is not None and not isinstance(edge_labels_group, Mapping):
            raise SnapshotCompatibilityError("snapshot edge_labels must be a mapping")
        if dynamics is not None and not isinstance(dynamics, Mapping):
            raise SnapshotCompatibilityError("snapshot dynamics must be a mapping")
        if caches is not None and not isinstance(caches, Mapping):
            raise SnapshotCompatibilityError("snapshot caches must be a mapping")

        state_mapping: dict[str, Any] = {}
        if isinstance(edge_labels_group, Mapping):
            state_mapping.update(
                {
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

    def get_state(self) -> GRC9State:
        return self._state

    def set_state(self, state: GRC9State) -> None:
        if not isinstance(state, GRC9State):
            raise SnapshotCompatibilityError("state must be a GRC9State instance")
        next_state = deepcopy(state)
        _lock_budget_target(
            next_state,
            budget_target_provided=next_state.budget_target != 0.0,
        )
        self._validate_state(next_state)
        self._state = next_state

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        claims = set(self.CAPABILITY_PROFILE.required)
        self.CAPABILITY_PROFILE.validate_claims(claims)
        return claims

    def compute_observables(self) -> ObservableMap:
        budget_current = float(sum(self._state.node_coherence.values()))
        spark_count = sum(1 for event in self._state.event_log if event.kind == "spark")
        observable_sink_set, _, _ = self._derive_identity_diagnostic_from_current_flux()
        active_degree_histogram = {degree: 0 for degree in range(10)}
        zero_column_count = 0
        for node_id in self._state.topology.iter_live_node_ids():
            degree = len(tuple(self._state.topology.incident_edge_ids(node_id)))
            active_degree_histogram[degree] = active_degree_histogram.get(degree, 0) + 1
            for column in (1, 2, 3):
                if all(
                    self._state.topology.port_edge_id(node_id, port_id_to_slot(rc_to_port(row, column)))
                    is None
                    for row in (1, 2, 3)
                ):
                    zero_column_count += 1
        live_node_count = len(tuple(self._state.topology.iter_live_node_ids()))
        total_column_count = 3 * live_node_count
        observables: ObservableMap = {
            "abundance": float(len(observable_sink_set)),
            "budget_current": budget_current,
            "budget_error": abs(budget_current - self._state.budget_target),
            "num_nodes": live_node_count,
            "num_port_edges": len(tuple(self._state.topology.iter_live_edge_ids())),
            "spark_count": spark_count,
            "active_degree_histogram": active_degree_histogram,
            "column_profile_sparsity": (
                0.0
                if total_column_count == 0
                else float(zero_column_count / total_column_count)
            ),
            "expansion_count": len(self._state.expansion_registry),
            "sink_module_sizes": {
                expansion_id: len(record.module_node_ids)
                for expansion_id, record in sorted(self._state.expansion_registry.items())
            },
        }
        return observables

    def _derive_identity_diagnostic_from_current_flux(
        self,
    ) -> tuple[set[int], dict[int, set[int]], dict[int, int]]:
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        successor_map: dict[int, int] = {}
        sinks: set[int] = set()
        basins: dict[int, set[int]] = {}

        for node_id in live_node_ids:
            outgoing_candidates: list[tuple[float, int, int]] = []
            positive_inflow = False
            max_outgoing = 0.0
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
                outgoing_flux = self._oriented_flux(edge_id=edge_id, node_id=node_id)
                incoming_flux = self._oriented_flux(edge_id=edge_id, node_id=neighbor_id)
                if outgoing_flux > 0.0:
                    outgoing_candidates.append((outgoing_flux, neighbor_id, edge_id))
                if incoming_flux > 0.0:
                    positive_inflow = True
                if outgoing_flux > max_outgoing:
                    max_outgoing = outgoing_flux
            if outgoing_candidates:
                outgoing_candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
                successor_map[node_id] = outgoing_candidates[0][1]
            else:
                successor_map[node_id] = node_id
            if max_outgoing <= 0.0 and positive_inflow:
                sinks.add(node_id)

        for origin_node_id in live_node_ids:
            reached_sink = self._reachable_sink(
                origin_node_id=origin_node_id,
                successor_map=successor_map,
                sinks=sinks,
            )
            if reached_sink is not None:
                basins.setdefault(reached_sink, set()).add(origin_node_id)

        return sinks, basins, successor_map

    def _compute_geometry(self) -> None:
        row_neighborhoods: dict[int, dict[int, tuple[int, ...]]] = {}
        row_mismatch_terms: dict[int, dict[int, float]] = {}
        row_tensor_diagonal: dict[int, list[float]] = {}
        tensor_terms: dict[int, dict[str, float]] = {}

        lambda_c = float(self._params.evolution.get("lambda_c", 1.0))
        xi_c = float(self._params.evolution.get("xi_c", 1.0))
        zeta_c = float(self._params.evolution.get("zeta_c", 1.0))

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            coherence_i = float(self._state.node_coherence.get(node_id, 0.0))
            row_edges: dict[int, list[int]] = {1: [], 2: [], 3: []}
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                local_port = self._local_port_id(edge_id=edge_id, node_id=node_id)
                row, _ = port_to_rc(local_port)
                row_edges[row].append(edge_id)

            density_term = lambda_c * coherence_i
            flux_sum = sum(
                self._oriented_flux(edge_id=edge_id, node_id=node_id)
                for edge_id in sorted(self._state.topology.incident_edge_ids(node_id))
            )
            flux_feedback_term = zeta_c * (flux_sum**2)

            row_diagonal: list[float] = []
            row_neighborhoods[node_id] = {}
            row_mismatch_terms[node_id] = {}
            for row in (1, 2, 3):
                incident_row_edges = tuple(sorted(row_edges[row]))
                row_neighborhoods[node_id][row] = incident_row_edges
                mismatch_sum = 0.0
                for edge_id in incident_row_edges:
                    neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
                    coherence_j = float(self._state.node_coherence.get(neighbor_id, 0.0))
                    conductance = self._state.port_edges[edge_id].conductance
                    mismatch_sum += conductance * ((coherence_j - coherence_i) ** 2)
                row_mismatch = xi_c * mismatch_sum
                row_mismatch_terms[node_id][row] = float(row_mismatch)
                row_diagonal.append(float(density_term + row_mismatch + flux_feedback_term))

            row_tensor_diagonal[node_id] = row_diagonal
            tensor_terms[node_id] = {
                "density_term": float(density_term),
                "flux_feedback_term": float(flux_feedback_term),
                "net_flux_sum": float(flux_sum),
            }

        self._state.cached_quantities["row_neighborhoods"] = row_neighborhoods
        self._state.cached_quantities["row_mismatch_terms"] = row_mismatch_terms
        self._state.cached_quantities["row_tensor_diagonal"] = row_tensor_diagonal
        self._state.cached_quantities["tensor_terms"] = tensor_terms

    def _compute_metric(self) -> None:
        alpha = float(self._params.evolution.get("alpha", 1.0))
        beta = float(self._params.evolution.get("beta", 1.0))
        gamma = float(self._params.evolution.get("gamma", 1.0))
        delta = float(self._params.evolution.get("delta", 1.0))

        reference_conductance = {
            edge_id: float(port_edge.conductance)
            for edge_id, port_edge in self._state.port_edges.items()
        }
        edge_curvature: dict[int, float] = {}
        updated_port_edges: dict[int, PortEdge] = {}

        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            port_edge = self._state.port_edges[edge_id]
            coherence_u = float(self._state.node_coherence.get(port_edge.node_u, 0.0))
            coherence_v = float(self._state.node_coherence.get(port_edge.node_v, 0.0))
            flux_uv = float(port_edge.flux_uv)
            ricci = self._edge_curvature_term(
                edge_id=edge_id,
                node_u=port_edge.node_u,
                node_v=port_edge.node_v,
                edge_weights=reference_conductance,
            )
            exponent = (
                -alpha * (coherence_u + coherence_v) / 2.0
                -beta * ((coherence_u - coherence_v) ** 2) / 2.0
                -gamma * (flux_uv**2) / 2.0
                -delta * ricci
            )
            conductance = max(1e-12, math.exp(exponent))
            updated_port_edges[edge_id] = PortEdge(
                node_u=port_edge.node_u,
                port_u=port_edge.port_u,
                node_v=port_edge.node_v,
                port_v=port_edge.port_v,
                conductance=float(conductance),
                flux_uv=port_edge.flux_uv,
            )
            edge_curvature[edge_id] = float(ricci)

        self._state.port_edges = updated_port_edges
        self._state.cached_quantities["edge_curvature"] = edge_curvature
        self._invalidate_coarse_cache(reason="conductance_recomputation")

    def _compute_edge_labels(self) -> None:
        selected_labels = self._selected_edge_labels()
        live_edge_ids = tuple(sorted(self._state.topology.iter_live_edge_ids()))
        self._state.geometric_length = {}
        self._state.temporal_delay = {}
        self._state.flux_coupling = {}

        edge_label_computation_mode: dict[str, str] = {}
        edge_label_params: dict[str, Any] = {
            "selection": (
                "all"
                if self._params.constitutive_semantic_modes["edge_label_selection"] == "all"
                else tuple(sorted(selected_labels))
            )
        }

        geometric_mode = self._geometric_length_mode()
        if "geometric_length" in selected_labels:
            edge_label_computation_mode["geometric_length"] = geometric_mode
            edge_label_params["geometric_length"] = {
                "mode": geometric_mode,
                "source": "fixed_port_chart_row_tensor",
            }
            for edge_id in live_edge_ids:
                self._state.geometric_length[edge_id] = self._compute_geometric_length(
                    edge_id=edge_id
                )

        if "flux_coupling" in selected_labels:
            edge_label_computation_mode["flux_coupling"] = "absolute_flux"
            edge_label_params["flux_coupling"] = {"mode": "absolute_flux"}
            for edge_id in live_edge_ids:
                self._state.flux_coupling[edge_id] = abs(self._state.port_edges[edge_id].flux_uv)

        if "temporal_delay" in selected_labels:
            temporal_params = dict(_DEFAULT_TEMPORAL_LABEL_PARAMS)
            temporal_params.update(
                {
                    key: float(value)
                    for key, value in dict(self._params.evolution).items()
                    if key in {"v0", "rho", "eps_tau"}
                }
            )
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
                geometric_length = self._state.geometric_length.get(
                    edge_id,
                    self._compute_geometric_length(edge_id=edge_id),
                )
                flux_coupling = self._state.flux_coupling.get(
                    edge_id,
                    abs(self._state.port_edges[edge_id].flux_uv),
                )
                self._state.temporal_delay[edge_id] = geometric_length / (
                    v0 + rho * flux_coupling + eps_tau
                )

        self._state.edge_label_computation_mode = edge_label_computation_mode
        self._state.edge_label_params = edge_label_params
        self._state.cached_quantities["edge_label_computation_mode"] = dict(
            edge_label_computation_mode
        )
        self._state.cached_quantities["edge_label_params"] = dict(edge_label_params)
        self._invalidate_coarse_cache(reason="edge_label_recomputation")

    def _compute_potential(self) -> None:
        kappa_c = float(self._params.evolution.get("kappa_c", 1.0))
        selection = self._params.evolution["site_potential_selection"]
        params = self._params.evolution["site_potential_params"]
        potential: dict[int, float] = {}

        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            coherence_i = float(self._state.node_coherence.get(node_id, 0.0))
            interaction_term = 0.0
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
                coherence_j = float(self._state.node_coherence.get(neighbor_id, 0.0))
                interaction_term += float(self._state.port_edges[edge_id].conductance) * (
                    coherence_i - coherence_j
                )
            potential[node_id] = (
                kappa_c * interaction_term
                - self._site_potential_derivative(
                    coherence=coherence_i,
                    selection=selection,
                    params=params,
                )
            )

        self._state.potential = potential

    def _compute_flux(self) -> None:
        eta = float(self._params.evolution.get("eta", 1.0))
        updated_port_edges: dict[int, PortEdge] = {}
        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            port_edge = self._state.port_edges[edge_id]
            potential_u = float(self._state.potential.get(port_edge.node_u, 0.0))
            potential_v = float(self._state.potential.get(port_edge.node_v, 0.0))
            flux_uv = -eta * port_edge.conductance * (potential_u - potential_v)
            updated_port_edges[edge_id] = PortEdge(
                node_u=port_edge.node_u,
                port_u=port_edge.port_u,
                node_v=port_edge.node_v,
                port_v=port_edge.port_v,
                conductance=port_edge.conductance,
                flux_uv=float(flux_uv),
            )
        self._state.port_edges = updated_port_edges
        self._assert_flux_antisymmetry()
        self._invalidate_coarse_cache(reason="flux_recomputation")

    def _detect_identities(self) -> None:
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        successor_map: dict[int, int] = {}
        sinks: set[int] = set()
        basins: dict[int, set[int]] = {}

        for node_id in live_node_ids:
            outgoing_candidates: list[tuple[float, int, int]] = []
            positive_inflow = False
            max_outgoing = 0.0
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
                outgoing_flux = self._oriented_flux(edge_id=edge_id, node_id=node_id)
                incoming_flux = self._oriented_flux(edge_id=edge_id, node_id=neighbor_id)
                if outgoing_flux > 0.0:
                    outgoing_candidates.append((outgoing_flux, neighbor_id, edge_id))
                if incoming_flux > 0.0:
                    positive_inflow = True
                if outgoing_flux > max_outgoing:
                    max_outgoing = outgoing_flux
            if outgoing_candidates:
                outgoing_candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
                successor_map[node_id] = outgoing_candidates[0][1]
            else:
                successor_map[node_id] = node_id
            if max_outgoing <= 0.0 and positive_inflow:
                sinks.add(node_id)

        for origin_node_id in live_node_ids:
            reached_sink = self._reachable_sink(
                origin_node_id=origin_node_id,
                successor_map=successor_map,
                sinks=sinks,
            )
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

    def _compute_column_diagnostic(self, *, node_id: int) -> list[float]:
        diagnostics: list[float] = []
        coherence_i = float(self._state.node_coherence.get(node_id, 0.0))
        for column in (1, 2, 3):
            column_sum = 0.0
            for row in (1, 2, 3):
                port_id = rc_to_port(row, column)
                slot = port_id_to_slot(port_id)
                edge_id = self._state.topology.port_edge_id(node_id, slot)
                if edge_id is None:
                    column_sum += 0.0
                    continue
                neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
                coherence_j = float(self._state.node_coherence.get(neighbor_id, 0.0))
                conductance = float(self._state.port_edges[edge_id].conductance)
                column_sum += conductance * (coherence_j - coherence_i)
            diagnostics.append(float(column_sum))
        return diagnostics

    def _active_degree(self, *, node_id: int) -> int:
        return len(tuple(self._state.topology.incident_edge_ids(node_id)))

    def _instability_proxy(self, *, sink_node_id: int) -> float:
        patch_nodes = {sink_node_id}
        patch_nodes.update(self._state.topology.neighbors(sink_node_id))
        cut_out = 0.0
        support_in = 0.0
        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            port_edge = self._state.port_edges[edge_id]
            in_u = port_edge.node_u in patch_nodes
            in_v = port_edge.node_v in patch_nodes
            if in_u and in_v:
                support_in += port_edge.conductance
            elif in_u != in_v:
                cut_out += port_edge.conductance
        eps = 1e-12
        # Phase 6 baseline instability proxy:
        # Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)
        return float(cut_out / max(cut_out + support_in, eps))

    def _detect_events(self) -> list[GRCEvent]:
        tau_instability = float(self._params.evolution.get("tau_instability", 0.5))
        eps_spark = float(self._params.evolution.get("eps_spark", 0.01))
        enable_sign_crossing = bool(
            self._params.evolution.get("enable_sign_crossing_spark", False)
        )

        spark_diagnostics: dict[int, dict[str, Any]] = {}
        events: list[GRCEvent] = []
        next_prev_column_diagnostic = dict(self._state.prev_column_diagnostic)

        # The canonical GRC9 trigger requires full saturation deg_act == 9.
        # The optional near-saturation relaxation deg_act >= 8 is intentionally
        # deferred and is not applied in the Phase 6 baseline.
        for sink_node_id in sorted(self._state.sink_set):
            active_degree = self._active_degree(node_id=sink_node_id)
            column_diagnostic = self._compute_column_diagnostic(node_id=sink_node_id)
            instability = self._instability_proxy(sink_node_id=sink_node_id)
            min_abs_column = min(abs(value) for value in column_diagnostic)
            previous_diagnostic = self._state.prev_column_diagnostic.get(sink_node_id)
            sign_crossing = bool(
                enable_sign_crossing
                and previous_diagnostic is not None
                and len(previous_diagnostic) == len(column_diagnostic)
                and any(
                    float(previous_value) * float(current_value) < 0.0
                    for previous_value, current_value in zip(
                        previous_diagnostic, column_diagnostic, strict=True
                    )
                )
            )

            spark_kind: SparkKind | None = None
            if active_degree == 9:
                if instability >= tau_instability:
                    spark_kind = SparkKind.SATURATION_INSTABILITY
                elif min_abs_column < eps_spark:
                    spark_kind = SparkKind.SATURATION_COLUMN_PROXY
                elif sign_crossing:
                    spark_kind = SparkKind.SATURATION_SIGN_CROSSING

            spark_diagnostics[sink_node_id] = {
                "active_degree": active_degree,
                "tau_instability": tau_instability,
                "eps_spark": eps_spark,
                "instability": instability,
                "column_diagnostic": list(column_diagnostic),
                "min_abs_column": min_abs_column,
                "near_saturation_extension": "deferred",
                "sign_crossing_enabled": enable_sign_crossing,
                "sign_crossing": sign_crossing,
                "spark_kind": None if spark_kind is None else spark_kind.value,
            }

            next_prev_column_diagnostic[sink_node_id] = list(column_diagnostic)

            if spark_kind is not None:
                events.append(
                    GRCEvent(
                        kind="spark",
                        step_index=self._state.step_index,
                        payload={
                            "sink_node_id": sink_node_id,
                            "spark_kind": spark_kind.value,
                            "active_degree": active_degree,
                            "instability": instability,
                            "column_diagnostic": list(column_diagnostic),
                            "min_abs_column": min_abs_column,
                        },
                        source_family=self.MODEL_FAMILY,
                    )
                )

        self._state.cached_quantities["spark_diagnostics"] = {
            str(node_id): payload for node_id, payload in sorted(spark_diagnostics.items())
        }
        self._state.cached_quantities["spark_trigger_order"] = tuple(
            event.payload["sink_node_id"] for event in events
        )
        self._state.prev_column_diagnostic = next_prev_column_diagnostic
        return events

    def _apply_topology_changes(self, events: list[GRCEvent]) -> None:
        if not events:
            self._state.cached_quantities["topology_event_order"] = ()
            self._state.cached_quantities["topology_event_mode"] = "sequential"
            return

        self._ensure_budget_target()
        self._state.cached_quantities["topology_event_mode"] = "sequential"
        ordered_events = sorted(
            [event for event in events if event.kind == "spark"],
            key=lambda event: (
                int(event.payload.get("sink_node_id", -1)),
                int(event.payload.get("candidate_rank", 0)),
            ),
        )

        processed_sink_ids: list[int] = []
        remaining_events = list(ordered_events)
        appended_event_keys = {
            (
                event.kind,
                event.step_index,
                event.source_family,
                tuple(sorted((key, repr(value)) for key, value in event.payload.items())),
            )
            for event in self._state.event_log
        }

        while remaining_events:
            event = remaining_events.pop(0)
            sink_node_id = int(event.payload.get("sink_node_id", -1))
            if not self._state.topology.has_node(sink_node_id):
                continue
            if self._state.sink_set and sink_node_id not in self._state.sink_set:
                continue

            event_key = (
                event.kind,
                event.step_index,
                event.source_family,
                tuple(sorted((key, repr(value)) for key, value in event.payload.items())),
            )
            if event_key not in appended_event_keys:
                self._state.event_log.append(event)
                appended_event_keys.add(event_key)

            self._apply_expansion(event)
            processed_sink_ids.append(sink_node_id)

            self._detect_identities()
            remaining_events = [
                candidate
                for candidate in remaining_events
                if self._state.topology.has_node(
                    int(candidate.payload.get("sink_node_id", -1))
                )
                and (
                    not self._state.sink_set
                    or int(candidate.payload.get("sink_node_id", -1)) in self._state.sink_set
                )
            ]

        self._state.cached_quantities["topology_event_order"] = tuple(processed_sink_ids)

    def _apply_expansion(self, spark_event: GRCEvent) -> None:
        sink_node_id = int(spark_event.payload["sink_node_id"])
        if not self._state.topology.has_node(sink_node_id):
            raise InvalidStateTransitionError(
                f"cannot expand missing sink node {sink_node_id}"
            )

        parent_coherence = float(self._state.node_coherence.get(sink_node_id, 0.0))
        target_effective_degree = self._target_effective_degree(
            sink_node_id=sink_node_id,
            spark_event=spark_event,
        )
        requested_node_count = compute_expansion_node_count(target_effective_degree)
        target_module_node_count = max(4, requested_node_count)
        distribution_weights = self._expansion_distribution_weights()
        adiabatic_schedule = self._build_expansion_schedule()

        boundary_edges_by_column: dict[int, list[tuple[int, int]]] = {1: [], 2: [], 3: []}
        boundary_conductance_by_column: dict[int, list[float]] = {1: [], 2: [], 3: []}
        for edge_id in sorted(self._state.topology.incident_edge_ids(sink_node_id)):
            local_port_id = self._local_port_id(edge_id=edge_id, node_id=sink_node_id)
            _, column = port_to_rc(local_port_id)
            boundary_edges_by_column[column].append((edge_id, local_port_id))
            boundary_conductance_by_column[column].append(
                float(self._state.port_edges[edge_id].conductance)
            )

        core_node_id = self._state.topology.add_node(
            {"role": "expansion_core", "parent_sink_id": sink_node_id}
        )
        satellite_node_ids = {
            column: self._state.topology.add_node(
                {
                    "role": "expansion_satellite",
                    "column": column,
                    "parent_sink_id": sink_node_id,
                }
            )
            for column in PRIMARY_SATELLITE_COLUMNS
        }
        column_tree_nodes: dict[int, list[int]] = {
            column: [satellite_node_ids[column]] for column in PRIMARY_SATELLITE_COLUMNS
        }
        module_node_ids: list[int] = [core_node_id] + [
            satellite_node_ids[column] for column in PRIMARY_SATELLITE_COLUMNS
        ]

        internal_edge_payloads: dict[int, PortEdge] = {}
        internal_edge_ids: list[int] = []
        for core_port_id, column in zip(CANONICAL_CORE_SPINE_PORTS, PRIMARY_SATELLITE_COLUMNS, strict=True):
            conductance = aggregate_bond_conductance(
                boundary_conductance_by_column[column],
                fallback=float(self._params.evolution.get("w_bond", 1.0)),
            )
            edge_id = self._state.topology.connect_ports(
                core_node_id,
                port_id_to_slot(core_port_id),
                satellite_node_ids[column],
                port_id_to_slot(5),
                payload={
                    "kind": "expansion_internal",
                    "column": column,
                    "parent_sink_id": sink_node_id,
                },
            )
            internal_edge_ids.append(edge_id)
            internal_edge_payloads[edge_id] = PortEdge(
                node_u=core_node_id,
                port_u=core_port_id,
                node_v=satellite_node_ids[column],
                port_v=5,
                conductance=conductance,
                flux_uv=0.0,
            )

        reassignment_map: dict[int, dict[str, int]] = {}
        for column in PRIMARY_SATELLITE_COLUMNS:
            ordered_ports = boundary_reassignment_order(
                port_id for _, port_id in boundary_edges_by_column[column]
            )
            ordered_edge_items: list[tuple[int, int]] = []
            for port_id in ordered_ports:
                for edge_id, candidate_port_id in boundary_edges_by_column[column]:
                    if candidate_port_id == port_id:
                        ordered_edge_items.append((edge_id, candidate_port_id))
            for edge_id, old_port_id in ordered_edge_items:
                target_node_id, target_port_id, new_edge_id = self._find_or_make_column_rewire_target(
                    sink_node_id=sink_node_id,
                    column=column,
                    old_port_id=old_port_id,
                    column_tree_nodes=column_tree_nodes,
                    module_node_ids=module_node_ids,
                    internal_edge_ids=internal_edge_ids,
                    internal_edge_payloads=internal_edge_payloads,
                    boundary_conductance_by_column=boundary_conductance_by_column,
                )
                reassignment_map[edge_id] = {
                    "from_port_id": old_port_id,
                    "to_node_id": target_node_id,
                    "to_port_id": target_port_id,
                }

                endpoint_a, endpoint_b = self._state.topology.edge_ports(edge_id)
                if endpoint_a[0] == sink_node_id:
                    other_node_id, other_slot = endpoint_b
                else:
                    other_node_id, other_slot = endpoint_a
                self._state.topology.rewire_edge(
                    edge_id,
                    target_node_id,
                    port_id_to_slot(target_port_id),
                    other_node_id,
                    other_slot,
                )

        planned_extra_nodes = target_module_node_count - len(module_node_ids)
        for column in round_robin_column_order(planned_extra_nodes):
            new_node_id, new_edge_id, port_edge = self._attach_column_tree_node(
                sink_node_id=sink_node_id,
                column=column,
                column_tree_nodes=column_tree_nodes,
                boundary_conductance_by_column=boundary_conductance_by_column,
            )
            module_node_ids.append(new_node_id)
            internal_edge_ids.append(new_edge_id)
            internal_edge_payloads[new_edge_id] = port_edge

        self._state.node_coherence.pop(sink_node_id, None)
        self._state.node_coherence[core_node_id] = 0.0
        for column in PRIMARY_SATELLITE_COLUMNS:
            self._state.node_coherence[satellite_node_ids[column]] = (
                distribution_weights[column - 1] * parent_coherence
            )
        for node_id in module_node_ids[4:]:
            self._state.node_coherence[node_id] = 0.0

        self._state.potential = {
            node_id: value
            for node_id, value in self._state.potential.items()
            if self._state.topology.has_node(node_id) and node_id != sink_node_id
        }
        for node_id in module_node_ids:
            self._state.potential.setdefault(node_id, 0.0)

        self._state.topology.remove_node(sink_node_id)

        existing_port_edges = {
            edge_id: port_edge
            for edge_id, port_edge in self._state.port_edges.items()
            if self._state.topology.has_edge(edge_id)
        }
        existing_port_edges.update(internal_edge_payloads)
        self._state.port_edges = _hydrate_port_edges_from_topology(
            self._state.topology,
            port_edges=existing_port_edges,
        )

        self._prune_runtime_state_after_topology_change()

        expansion_id = f"spark-{self._state.step_index}-{sink_node_id}"
        self._state.expansion_registry[expansion_id] = ExpansionRecord(
            parent_sink_id=sink_node_id,
            module_node_ids=tuple(module_node_ids),
            expansion_step=self._state.step_index,
            distribution_weights=distribution_weights,
            schedule=adiabatic_schedule,
        )
        budget_error = self._verify_budget_preservation(context="expansion")
        expansion_event = GRCEvent(
            kind="expansion",
            step_index=self._state.step_index,
            payload={
                "sink_node_id": sink_node_id,
                "expansion_id": expansion_id,
                "target_effective_degree": target_effective_degree,
                "requested_node_count": requested_node_count,
                "module_node_ids": list(module_node_ids),
                "internal_edge_ids": list(internal_edge_ids),
                "distribution_weights": list(distribution_weights),
                "budget_error": budget_error,
                "reassignment_map": {
                    str(edge_id): payload for edge_id, payload in sorted(reassignment_map.items())
                },
            },
            source_family=self.MODEL_FAMILY,
        )
        self._state.event_log.append(expansion_event)
        self._state.cached_quantities["last_expansion"] = dict(expansion_event.payload)

    def _apply_growth(self) -> None:
        self._ensure_budget_target()
        lambda_birth = float(self._params.evolution.get("lambda_birth", 0.0))
        alpha_seed = float(self._params.evolution.get("alpha_seed", 0.1))
        w_bond = float(self._params.evolution.get("w_bond", 1.0))
        parent_eligibility_mode = str(
            self._params.constitutive_semantic_modes.get(
                "growth_parent_eligibility",
                "legacy_any_inactive_port",
            )
        )
        if parent_eligibility_mode not in _ALLOWED_GROWTH_PARENT_ELIGIBILITY:
            raise InvalidParamsError(
                "growth_parent_eligibility must be legacy_any_inactive_port "
                "or grc9_front_capacity"
            )
        self._state.cached_quantities["birth_rule_mode"] = "bernoulli_probability"
        self._state.cached_quantities["birth_parent_selection_mode"] = (
            "outward_flux_parent_selection"
        )
        self._state.cached_quantities["birth_parent_eligibility_mode"] = (
            parent_eligibility_mode
        )
        if lambda_birth <= 0.0:
            self._state.cached_quantities["last_growth_events"] = []
            return

        rng = random.Random()
        rng.setstate(self._state.rng_state)
        selected_parents: list[tuple[int, int, float, float, float]] = []
        front_eligible_ports = self._growth_front_eligible_ports()
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            inactive_ports = self._inactive_port_ids(node_id=node_id)
            if parent_eligibility_mode == "grc9_front_capacity":
                eligible_ports = front_eligible_ports.get(node_id, ())
                inactive_ports = tuple(
                    port_id for port_id in inactive_ports if port_id in eligible_ports
                )
            if not inactive_ports:
                continue
            outward_flux = self._outward_flux_pressure(node_id=node_id)
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
        new_port_edges: dict[int, PortEdge] = {}
        for node_id, parent_port_id, outward_flux, birth_probability, rng_sample in selected_parents:
            if not self._state.topology.has_node(node_id):
                continue
            if self._state.topology.port_is_occupied(
                node_id, port_id_to_slot(parent_port_id)
            ):
                continue
            child_node_id = self._state.topology.add_node(
                {"role": "growth_child", "parent_node_id": node_id}
            )
            edge_id = self._state.topology.connect_ports(
                node_id,
                port_id_to_slot(parent_port_id),
                child_node_id,
                port_id_to_slot(1),
                payload={"kind": "growth", "parent_node_id": node_id},
            )
            new_port_edges[edge_id] = PortEdge(
                node_u=node_id,
                port_u=parent_port_id,
                node_v=child_node_id,
                port_v=1,
                conductance=w_bond,
                flux_uv=0.0,
            )

            parent_coherence = float(self._state.node_coherence.get(node_id, 0.0))
            transfer = max(0.0, min(parent_coherence, alpha_seed * parent_coherence))
            self._state.node_coherence[node_id] = parent_coherence - transfer
            self._state.node_coherence[child_node_id] = transfer
            self._state.potential[child_node_id] = 0.0

            growth_events.append(
                GRCEvent(
                    kind="growth",
                    step_index=self._state.step_index,
                    payload={
                        "parent_node_id": node_id,
                        "child_node_id": child_node_id,
                        "parent_port_id": parent_port_id,
                        "child_port_id": 1,
                        "outward_flux": outward_flux,
                        "birth_probability": birth_probability,
                        "rng_sample": rng_sample,
                        "growth_parent_eligibility_mode": parent_eligibility_mode,
                        "growth_parent_capacity_source": (
                            self._growth_capacity_source(node_id, parent_port_id)
                        ),
                    },
                    source_family=self.MODEL_FAMILY,
                )
            )

        self._state.rng_state = rng.getstate()
        if not growth_events:
            self._state.cached_quantities["last_growth_events"] = []
            return

        existing_port_edges = {
            edge_id: port_edge
            for edge_id, port_edge in self._state.port_edges.items()
            if self._state.topology.has_edge(edge_id)
        }
        existing_port_edges.update(new_port_edges)
        self._state.port_edges = _hydrate_port_edges_from_topology(
            self._state.topology,
            port_edges=existing_port_edges,
        )
        self._prune_runtime_state_after_topology_change()
        self._state.cached_quantities["birth_rule_mode"] = "bernoulli_probability"
        self._state.cached_quantities["birth_parent_selection_mode"] = (
            "outward_flux_parent_selection"
        )
        self._state.cached_quantities["birth_parent_eligibility_mode"] = (
            parent_eligibility_mode
        )
        budget_error = self._verify_budget_preservation(context="growth")
        for event in growth_events:
            event.payload["budget_error"] = budget_error
            self._state.event_log.append(event)
        self._state.cached_quantities["last_growth_events"] = [
            dict(event.payload) for event in growth_events
        ]

    def _apply_boundary_behavior(self) -> None:
        boundary_mode = self._params.constitutive_semantic_modes["boundary_mode"]
        if boundary_mode == "prune":
            self._state.cached_quantities["boundary_behavior_mode"] = "prune_noop"
            return
        raise InvalidStateTransitionError(
            f"GRC9 boundary_mode {boundary_mode!r} is not implemented yet"
        )

    def _apply_continuity(self) -> None:
        dt = float(self._params.dt)
        coherence_deltas: dict[int, float] = {}
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            divergence = sum(
                self._oriented_flux(edge_id=edge_id, node_id=node_id)
                for edge_id in self._state.topology.incident_edge_ids(node_id)
            )
            coherence_deltas[node_id] = -dt * divergence

        for node_id in sorted(coherence_deltas):
            self._state.node_coherence[node_id] = float(
                self._state.node_coherence.get(node_id, 0.0) + coherence_deltas[node_id]
            )
        self._state.cached_quantities["last_continuity_delta"] = dict(coherence_deltas)

    def _enforce_budget(self) -> None:
        negative_mass_correction = 0.0
        for node_id in sorted(self._state.node_coherence):
            coherence = float(self._state.node_coherence[node_id])
            if coherence < 0.0:
                negative_mass_correction += -coherence
                self._state.node_coherence[node_id] = 0.0

        self._ensure_budget_target()
        abundance = float(sum(self._state.node_coherence.values()))
        correction = float(self._state.budget_target - abundance)
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        if correction > 0.0:
            if live_node_ids:
                uniform_share = correction / len(live_node_ids)
                for node_id in live_node_ids:
                    self._state.node_coherence[node_id] = float(
                        self._state.node_coherence.get(node_id, 0.0) + uniform_share
                    )
                self._state.cached_quantities["budget_positive_correction_mode"] = (
                    "uniform_shift"
                )
            else:
                self._state.remainder = correction
                return
        elif correction < 0.0:
            remaining_removal = -correction
            for node_id in live_node_ids:
                if remaining_removal <= 0.0:
                    break
                available = float(self._state.node_coherence.get(node_id, 0.0))
                removal = min(available, remaining_removal)
                self._state.node_coherence[node_id] = float(available - removal)
                remaining_removal -= removal
            if remaining_removal > 1e-12:
                self._state.remainder = -remaining_removal
                self._state.cached_quantities["negative_mass_correction"] = float(
                    negative_mass_correction
                )
                self._state.cached_quantities["last_budget_error"] = float(
                    -remaining_removal
                )
                return

        corrected_abundance = float(sum(self._state.node_coherence.values()))
        budget_error = corrected_abundance - self._state.budget_target
        self._state.remainder = 0.0 if abs(budget_error) <= 1e-12 else float(budget_error)
        self._state.cached_quantities["last_budget_error"] = float(budget_error)
        self._state.cached_quantities["negative_mass_correction"] = float(
            negative_mass_correction
        )

    def _refresh_coarse_cache(self) -> None:
        if self._state.coarse_cache:
            self._state.coarse_cache.clear()
            self._state.cached_quantities["coarse_cache_invalidation_reason"] = (
                "post_step_refresh"
            )
        self._state.cached_quantities["coarse_cache_refresh_mode"] = "invalidate_only"

    def _target_effective_degree(
        self,
        *,
        sink_node_id: int,
        spark_event: GRCEvent,
    ) -> int:
        raw_value = spark_event.payload.get(
            "target_effective_degree",
            self._params.evolution.get("D_eff_target", 30),
        )
        target = int(raw_value)
        if target < 0:
            raise InvalidStateTransitionError(
                f"target effective degree for sink {sink_node_id} must be non-negative"
            )
        return target

    def _expansion_distribution_weights(self) -> tuple[float, float, float]:
        return normalize_expansion_weights(
            mode=self._params.constitutive_semantic_modes["expansion_distribution_mode"],
            custom_weights=self._params.evolution.get("expansion_distribution_weights"),
        )

    def _build_expansion_schedule(self) -> AdiabaticExpansionSchedule | None:
        total_substeps = int(self._params.evolution.get("adiabatic_expansion_substeps", 1))
        if total_substeps <= 1:
            return None
        return AdiabaticExpansionSchedule(
            total_substeps=total_substeps,
            completed_substeps=0,
            active=True,
        )

    def _find_or_make_column_rewire_target(
        self,
        *,
        sink_node_id: int,
        column: int,
        old_port_id: int,
        column_tree_nodes: dict[int, list[int]],
        module_node_ids: list[int],
        internal_edge_ids: list[int],
        internal_edge_payloads: dict[int, PortEdge],
        boundary_conductance_by_column: Mapping[int, list[float]],
    ) -> tuple[int, int, int | None]:
        target = self._find_column_rewire_target(
            column=column,
            old_port_id=old_port_id,
            column_tree_nodes=column_tree_nodes,
        )
        if target is not None:
            return (target[0], target[1], None)
        new_node_id, edge_id, port_edge = self._attach_column_tree_node(
            sink_node_id=sink_node_id,
            column=column,
            column_tree_nodes=column_tree_nodes,
            boundary_conductance_by_column=boundary_conductance_by_column,
        )
        module_node_ids.append(new_node_id)
        internal_edge_ids.append(edge_id)
        internal_edge_payloads[edge_id] = port_edge
        target = self._find_column_rewire_target(
            column=column,
            old_port_id=old_port_id,
            column_tree_nodes=column_tree_nodes,
        )
        if target is None:
            raise InvalidStateTransitionError(
                f"unable to find rewire target for column {column} port {old_port_id}"
            )
        return (target[0], target[1], edge_id)

    def _find_column_rewire_target(
        self,
        *,
        column: int,
        old_port_id: int,
        column_tree_nodes: Mapping[int, list[int]],
    ) -> tuple[int, int] | None:
        candidate_port_ids = tuple(
            rc_to_port(row, column) for row in (1, 2, 3)
        )
        if old_port_id in candidate_port_ids:
            for node_id in column_tree_nodes[column]:
                if not self._state.topology.port_is_occupied(
                    node_id, port_id_to_slot(old_port_id)
                ):
                    return (node_id, old_port_id)
        for node_id in column_tree_nodes[column]:
            for port_id in candidate_port_ids:
                if not self._state.topology.port_is_occupied(
                    node_id, port_id_to_slot(port_id)
                ):
                    return (node_id, port_id)
        return None

    def _attach_column_tree_node(
        self,
        *,
        sink_node_id: int,
        column: int,
        column_tree_nodes: dict[int, list[int]],
        boundary_conductance_by_column: Mapping[int, list[float]],
    ) -> tuple[int, int, PortEdge]:
        new_node_id = self._state.topology.add_node(
            {
                "role": "expansion_tree",
                "column": column,
                "parent_sink_id": sink_node_id,
            }
        )
        attachment_node_id, attachment_port_id = self._lowest_available_tree_attachment(
            column_tree_nodes[column]
        )
        conductance = aggregate_bond_conductance(
            boundary_conductance_by_column[column],
            fallback=float(self._params.evolution.get("w_bond", 1.0)),
        )
        edge_id = self._state.topology.connect_ports(
            attachment_node_id,
            port_id_to_slot(attachment_port_id),
            new_node_id,
            port_id_to_slot(5),
            payload={
                "kind": "expansion_tree",
                "column": column,
                "parent_sink_id": sink_node_id,
            },
        )
        column_tree_nodes[column].append(new_node_id)
        port_edge = PortEdge(
            node_u=min(attachment_node_id, new_node_id),
            port_u=attachment_port_id if attachment_node_id <= new_node_id else 5,
            node_v=max(attachment_node_id, new_node_id),
            port_v=5 if attachment_node_id <= new_node_id else attachment_port_id,
            conductance=conductance,
            flux_uv=0.0 if attachment_node_id <= new_node_id else -0.0,
        )
        return (new_node_id, edge_id, port_edge)

    def _lowest_available_tree_attachment(
        self,
        column_tree_nodes: list[int],
    ) -> tuple[int, int]:
        for node_id in column_tree_nodes:
            for port_id in range(1, 10):
                if port_id == 5:
                    continue
                if not self._state.topology.port_is_occupied(
                    node_id, port_id_to_slot(port_id)
                ):
                    return (node_id, port_id)
        raise InvalidStateTransitionError("no attachment port available in column tree")

    def _inactive_port_ids(self, *, node_id: int) -> tuple[int, ...]:
        return tuple(
            port_id
            for port_id in range(1, 10)
            if not self._state.topology.port_is_occupied(node_id, port_id_to_slot(port_id))
        )

    def _outward_flux_pressure(self, *, node_id: int) -> float:
        return float(
            sum(
                max(0.0, self._oriented_flux(edge_id=edge_id, node_id=node_id))
                for edge_id in self._state.topology.incident_edge_ids(node_id)
            )
        )

    def _growth_front_eligible_ports(self) -> dict[int, tuple[int, ...]]:
        raw = self._state.cached_quantities.get("grc9_front_growth_eligible_ports", {})
        if not isinstance(raw, Mapping):
            return {}
        result: dict[int, tuple[int, ...]] = {}
        for node_key, raw_ports in raw.items():
            try:
                node_id = int(node_key)
            except (TypeError, ValueError):
                continue
            if not isinstance(raw_ports, (list, tuple, set, frozenset)):
                continue
            clean_ports: list[int] = []
            for port_id in raw_ports:
                if isinstance(port_id, bool) or not isinstance(port_id, int):
                    continue
                if 1 <= port_id <= 9:
                    clean_ports.append(port_id)
            if clean_ports:
                result[node_id] = tuple(sorted(set(clean_ports)))
        return result

    def _growth_capacity_source(self, node_id: int, port_id: int) -> str:
        raw = self._state.cached_quantities.get("grc9_growth_parent_capacity_sources", {})
        if not isinstance(raw, Mapping):
            return "legacy_any_inactive_port"
        record = raw.get(str(node_id)) or raw.get(node_id)
        if not isinstance(record, Mapping):
            return "legacy_any_inactive_port"
        record_port = record.get("inactive_parent_port")
        if isinstance(record_port, int) and record_port != port_id:
            return "legacy_any_inactive_port"
        source = record.get("front_capacity_source")
        if source is None:
            return "unknown"
        normalized_source = str(source)
        if normalized_source not in _ALLOWED_GROWTH_FRONT_CAPACITY_SOURCES:
            return "unknown"
        return normalized_source

    def _ensure_budget_target(self) -> None:
        if (
            self._state.budget_target == 0.0
            and "budget_target_source" not in self._state.cached_quantities
        ):
            self._state.budget_target = float(sum(self._state.node_coherence.values()))
            self._state.cached_quantities["budget_target_source"] = (
                "compatibility_lazy_inference"
            )
        elif "budget_target_source" not in self._state.cached_quantities:
            self._state.cached_quantities["budget_target_source"] = (
                "provided_zero" if self._state.budget_target == 0.0 else "provided"
            )

    def _verify_budget_preservation(self, *, context: str) -> float:
        self._ensure_budget_target()
        budget_current = float(sum(self._state.node_coherence.values()))
        budget_error = float(budget_current - self._state.budget_target)
        if abs(budget_error) > 1e-12:
            self._correct_budget_drift(-budget_error)
            budget_current = float(sum(self._state.node_coherence.values()))
            budget_error = float(budget_current - self._state.budget_target)
        self._state.remainder = 0.0 if abs(budget_error) <= 1e-12 else budget_error
        self._state.cached_quantities[f"{context}_budget_check"] = {
            "budget_target": self._state.budget_target,
            "budget_current": budget_current,
            "budget_error": budget_error,
        }
        return budget_error

    def _correct_budget_drift(self, correction: float) -> None:
        live_node_ids = tuple(sorted(self._state.topology.iter_live_node_ids()))
        if not live_node_ids:
            self._state.remainder = correction
            return
        if correction > 0.0:
            uniform_share = correction / len(live_node_ids)
            for node_id in live_node_ids:
                self._state.node_coherence[node_id] = float(
                    self._state.node_coherence.get(node_id, 0.0) + uniform_share
                )
            self._state.cached_quantities["budget_positive_correction_mode"] = (
                "uniform_shift"
            )
            return

        remaining = -correction
        for node_id in live_node_ids:
            if remaining <= 0.0:
                break
            available = float(self._state.node_coherence.get(node_id, 0.0))
            removal = min(available, remaining)
            self._state.node_coherence[node_id] = available - removal
            remaining -= removal
        if remaining > 1e-12:
            self._state.remainder = -remaining

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
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            node_ports: dict[int, float] = {port_id: 0.0 for port_id in range(1, 10)}
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
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
        for node_id in sorted(self._state.topology.iter_live_node_ids()):
            node_ports: dict[int, float] = {port_id: 0.0 for port_id in range(1, 10)}
            for edge_id in sorted(self._state.topology.incident_edge_ids(node_id)):
                port_id = self._local_port_id(edge_id=edge_id, node_id=node_id)
                node_ports[port_id] = self._oriented_flux(edge_id=edge_id, node_id=node_id)
            port_field[node_id] = node_ports
        return port_field

    def _invalidate_coarse_cache(self, *, reason: str) -> None:
        self._state.coarse_cache.clear()
        self._state.cached_quantities["coarse_cache_invalidation_reason"] = reason

    def _prune_runtime_state_after_topology_change(self) -> None:
        live_node_ids = set(self._state.topology.iter_live_node_ids())
        live_edge_ids = set(self._state.topology.iter_live_edge_ids())
        self._state.node_coherence = {
            node_id: value
            for node_id, value in self._state.node_coherence.items()
            if node_id in live_node_ids
        }
        self._state.potential = {
            node_id: value
            for node_id, value in self._state.potential.items()
            if node_id in live_node_ids
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
        self._state.prev_column_diagnostic = {
            node_id: values
            for node_id, values in self._state.prev_column_diagnostic.items()
            if node_id in live_node_ids
        }
        self._state.sink_set = {
            node_id for node_id in self._state.sink_set if node_id in live_node_ids
        }
        self._state.basins = {
            sink_node_id: {
                member_node_id
                for member_node_id in members
                if member_node_id in live_node_ids
            }
            for sink_node_id, members in self._state.basins.items()
            if sink_node_id in live_node_ids
        }
        preserved_source_caches = {
            key: value
            for key, value in self._state.cached_quantities.items()
            if str(key).startswith("grcl9_")
            or key
            in {
                "budget_target_source",
                "grc9_front_growth_eligible_ports",
                "grc9_growth_parent_capacity_sources",
            }
        }
        self._state.coarse_cache.clear()
        self._state.cached_quantities.clear()
        self._state.cached_quantities.update(preserved_source_caches)
        self._state.cached_quantities["coarse_cache_invalidation_reason"] = (
            "topology_mutation"
        )

    def step(self) -> StepResult:
        trace: list[str] = []
        self._state.cached_quantities["current_step_events"] = []
        initial_event_count = len(self._state.event_log)

        self._compute_geometry()
        trace.append("compute_row_tensor")
        self._compute_metric()
        trace.append("compute_metric")
        self._compute_edge_labels()
        trace.append("compute_edge_labels")
        self._compute_potential()
        trace.append("compute_potential")
        self._compute_flux()
        trace.append("compute_flux")
        self._detect_identities()
        trace.append("detect_identities")
        events = self._detect_events()
        self._state.cached_quantities["current_step_events"] = list(events)
        trace.append("detect_sparks")
        self._apply_topology_changes(events)
        trace.append("apply_expansion")
        self._apply_growth()
        trace.append("apply_growth")
        self._apply_boundary_behavior()
        trace.append("apply_boundary_behavior")
        self._apply_continuity()
        trace.append("apply_continuity")
        self._enforce_budget()
        trace.append("enforce_budget")
        self._refresh_coarse_cache()
        trace.append("refresh_or_invalidate_coarse_cache")
        observables = self.compute_observables()
        trace.append("compute_observables")

        final_events = list(self._state.event_log[initial_event_count:])

        self._state.step_index += 1
        self._state.time += self._params.dt
        self._state.observables = dict(observables)
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
                "expected_step_order": (
                    "compute_row_tensor",
                    "compute_metric",
                    "compute_edge_labels",
                    "compute_potential",
                    "compute_flux",
                    "detect_identities",
                    "detect_sparks",
                    "apply_expansion",
                    "apply_growth",
                    "apply_boundary_behavior",
                    "apply_continuity",
                    "enforce_budget",
                    "refresh_or_invalidate_coarse_cache",
                    "compute_observables",
                ),
            },
        )

    def coarse_grain_columns(self, field_name: str) -> dict[str, Any]:
        normalized_field_name = str(field_name)
        if normalized_field_name == "signed_flux":
            coarse_state = coarse_grain_signed_flux_field(
                self._build_signed_flux_port_field()
            )
            coarse_state["field_name"] = normalized_field_name
            self._state.coarse_cache[f"signed_flux_split:{normalized_field_name}"] = deepcopy(
                coarse_state
            )
            return coarse_state

        coarse_state = coarse_grain_nonnegative_port_field(
            self._build_nonnegative_port_field(field_name=normalized_field_name)
        )
        coarse_state["field_name"] = normalized_field_name
        self._state.coarse_cache[f"exact_column_profile:{normalized_field_name}"] = deepcopy(
            coarse_state
        )
        return coarse_state

    def split_columns(self, coarse_state: Mapping[str, Any]) -> dict[str, Any]:
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
            "geometric_length": {
                str(edge_id): value
                for edge_id, value in self._state.geometric_length.items()
            },
            "temporal_delay": {
                str(edge_id): value
                for edge_id, value in self._state.temporal_delay.items()
            },
            "flux_coupling": {
                str(edge_id): value
                for edge_id, value in self._state.flux_coupling.items()
            },
            "edge_label_computation_mode": dict(self._state.edge_label_computation_mode),
            "edge_label_params": _stringify_mapping_keys(
                dict(self._state.edge_label_params)
            ),
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
            edge_labels=edge_labels,
            dynamics={"state": _state_payload_from_state(self._state)},
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
            caches={"coarse_cache": _stringify_mapping_keys(dict(self._state.coarse_cache))},
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

    def _selected_edge_labels(self) -> set[str]:
        selection = self._params.constitutive_semantic_modes["edge_label_selection"]
        if selection == "all":
            return set(_ALLOWED_EDGE_LABELS)
        return {str(label) for label in selection}

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
            mu = float(params.get("mu", 0.0))
            scale = float(params.get("scale", 1.0))
            return 2.0 * scale * coherence + mu
        if selection == "linear":
            bias = float(params.get("bias", 0.0))
            scale = float(params.get("scale", 1.0))
            return scale + bias
        raise InvalidStateTransitionError(
            f"unsupported site_potential_selection {selection!r}"
        )

    def _neighbor_for_edge(self, *, edge_id: int, node_id: int) -> int:
        endpoint_a, endpoint_b = self._state.topology.edge_ports(edge_id)
        if endpoint_a[0] == node_id:
            return endpoint_b[0]
        if endpoint_b[0] == node_id:
            return endpoint_a[0]
        raise InvalidStateTransitionError("edge is not incident to node_id")

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
        raise InvalidStateTransitionError("edge is not incident to node_id")

    def _signed_edge_flux(self, edge_id: int) -> float:
        return float(self._state.port_edges[edge_id].flux_uv)

    def _assert_flux_antisymmetry(self) -> None:
        antisymmetry: dict[int, dict[int, float]] = {}
        for edge_id in sorted(self._state.topology.iter_live_edge_ids()):
            port_edge = self._state.port_edges[edge_id]
            forward = self._oriented_flux(edge_id=edge_id, node_id=port_edge.node_u)
            reverse = self._oriented_flux(edge_id=edge_id, node_id=port_edge.node_v)
            if abs(forward + reverse) > 1e-12:
                raise InvalidStateTransitionError(
                    f"GRC9 oriented flux antisymmetry failed for edge {edge_id}"
                )
            antisymmetry[edge_id] = {
                port_edge.node_u: forward,
                port_edge.node_v: reverse,
            }
        self._state.cached_quantities["oriented_flux"] = antisymmetry

    def _geometric_length_mode(self) -> str:
        return "induced_intrinsic"

    def _compute_geometric_length(self, *, edge_id: int) -> float:
        row_tensor = self._state.cached_quantities.get("row_tensor_diagonal", {})
        if not isinstance(row_tensor, Mapping):
            raise InvalidStateTransitionError(
                "row_tensor_diagonal must exist before geometric_length is computed"
            )
        port_edge = self._state.port_edges[edge_id]
        row_u, _ = port_to_rc(port_edge.port_u)
        row_v, _ = port_to_rc(port_edge.port_v)
        tensor_u = row_tensor.get(port_edge.node_u, [0.0, 0.0, 0.0])
        tensor_v = row_tensor.get(port_edge.node_v, [0.0, 0.0, 0.0])
        stiffness_u = float(tensor_u[row_u - 1])
        stiffness_v = float(tensor_v[row_v - 1])
        return max(1e-12, 2.0 / (1.0 + stiffness_u + stiffness_v))

    def _edge_curvature_term(
        self,
        *,
        edge_id: int,
        node_u: int,
        node_v: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        backend = self._params.constitutive_semantic_modes["curvature_backend"]
        if backend == "none":
            return 0.0
        if backend == "forman":
            return self._forman_ricci_edge_curvature(
                edge_id=edge_id,
                node_u=node_u,
                node_v=node_v,
                edge_weights=edge_weights,
            )
        if backend == "ollivier":
            return self._ollivier_ricci_edge_curvature(
                edge_id=edge_id,
                node_u=node_u,
                node_v=node_v,
                edge_weights=edge_weights,
            )
        raise InvalidStateTransitionError(f"unsupported curvature_backend {backend!r}")

    def _current_edge_conductance(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        if edge_weights is not None:
            return max(1e-12, float(edge_weights.get(edge_id, 1.0)))
        return max(1e-12, float(self._state.port_edges[edge_id].conductance))

    def _current_node_weight(self, node_id: int) -> float:
        return max(1e-12, float(self._state.node_coherence.get(node_id, 0.0)))

    def _edge_length_cost(
        self,
        edge_id: int,
        *,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        return 1.0 / self._current_edge_conductance(edge_id, edge_weights=edge_weights)

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
            neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
            weight = self._current_edge_conductance(edge_id, edge_weights=edge_weights)
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
                neighbor_id = self._neighbor_for_edge(edge_id=edge_id, node_id=node_id)
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
        node_u: int,
        node_v: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        edge_weight = self._current_edge_conductance(edge_id, edge_weights=edge_weights)
        node_u_weight = self._current_node_weight(node_u)
        node_v_weight = self._current_node_weight(node_v)
        node_u_term = node_u_weight / edge_weight
        node_v_term = node_v_weight / edge_weight
        adjacent_u_term = 0.0
        adjacent_v_term = 0.0
        for adjacent_edge_id in self._state.topology.incident_edge_ids(node_u):
            if adjacent_edge_id == edge_id:
                continue
            adjacent_u_term += node_u_weight / math.sqrt(
                edge_weight
                * self._current_edge_conductance(
                    adjacent_edge_id, edge_weights=edge_weights
                )
            )
        for adjacent_edge_id in self._state.topology.incident_edge_ids(node_v):
            if adjacent_edge_id == edge_id:
                continue
            adjacent_v_term += node_v_weight / math.sqrt(
                edge_weight
                * self._current_edge_conductance(
                    adjacent_edge_id, edge_weights=edge_weights
                )
            )
        return float(
            edge_weight * (node_u_term + node_v_term - adjacent_u_term - adjacent_v_term)
        )

    def _ollivier_ricci_edge_curvature(
        self,
        *,
        edge_id: int,
        node_u: int,
        node_v: int,
        edge_weights: Mapping[int, float] | None = None,
    ) -> float:
        edge_distance = self._edge_length_cost(edge_id, edge_weights=edge_weights)
        if edge_distance <= 0.0:
            raise InvalidStateTransitionError("edge distance must remain positive")
        transport_cost = self._earth_movers_distance(
            self._neighbor_measure(node_u, edge_weights=edge_weights),
            self._neighbor_measure(node_v, edge_weights=edge_weights),
            edge_weights=edge_weights,
        )
        return float(1.0 - transport_cost / edge_distance)

    def _reachable_sink(
        self,
        *,
        origin_node_id: int,
        successor_map: Mapping[int, int],
        sinks: set[int],
    ) -> int | None:
        if origin_node_id in sinks:
            return origin_node_id

        visited = {origin_node_id}
        node_id = successor_map.get(origin_node_id)
        while node_id is not None:
            if node_id in sinks:
                return node_id
            if node_id in visited:
                return None
            visited.add(node_id)
            node_id = successor_map.get(node_id)
        return None

    def _validate_state(self, state: GRC9State) -> None:
        if not isinstance(state.topology, PortGraphBackend):
            raise InvalidStateTransitionError(
                "GRC9State.topology must be a PortGraphBackend"
            )
        live_node_ids = set(state.topology.iter_live_node_ids())
        live_edge_ids = set(state.topology.iter_live_edge_ids())

        if any(node_id not in live_node_ids for node_id in state.node_coherence):
            raise InvalidStateTransitionError(
                "GRC9State.node_coherence keys must reference live topology nodes"
            )
        if any(node_id not in live_node_ids for node_id in state.potential):
            raise InvalidStateTransitionError(
                "GRC9State.potential keys must reference live topology nodes"
            )
        if any(node_id not in live_node_ids for node_id in state.sink_set):
            raise InvalidStateTransitionError(
                "GRC9State.sink_set must reference live topology nodes"
            )
        if any(node_id not in live_node_ids for node_id in state.basins):
            raise InvalidStateTransitionError(
                "GRC9State.basins keys must reference live topology nodes"
            )
        for members in state.basins.values():
            if any(node_id not in live_node_ids for node_id in members):
                raise InvalidStateTransitionError(
                    "GRC9State.basins memberships must reference live topology nodes"
                )
        for node_id in state.prev_column_diagnostic:
            if node_id not in live_node_ids:
                raise InvalidStateTransitionError(
                    "GRC9State.prev_column_diagnostic keys must reference live topology nodes"
                )
        if set(state.port_edges) != live_edge_ids:
            raise InvalidStateTransitionError(
                "GRC9State.port_edges keys must exactly match live topology edges"
            )
        for edge_id, port_edge in state.port_edges.items():
            if not isinstance(port_edge, PortEdge):
                raise InvalidStateTransitionError(
                    "GRC9State.port_edges values must be PortEdge instances"
                )
            if port_edge.node_u not in live_node_ids or port_edge.node_v not in live_node_ids:
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge endpoints must reference live topology nodes"
                )
            if port_edge.node_u > port_edge.node_v or (
                port_edge.node_u == port_edge.node_v and port_edge.port_u > port_edge.port_v
            ):
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge orientation must follow the canonical ordering"
                )
            try:
                backend_port_u = port_id_to_slot(port_edge.port_u)
                backend_port_v = port_id_to_slot(port_edge.port_v)
            except ValueError as exc:
                raise InvalidStateTransitionError(str(exc)) from exc
            endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
            expected = _canonical_port_edge(
                endpoint_a=endpoint_a,
                endpoint_b=endpoint_b,
                conductance=port_edge.conductance,
                flux_uv=port_edge.flux_uv,
            )
            if (
                expected.node_u != port_edge.node_u
                or expected.port_u != port_edge.port_u
                or expected.node_v != port_edge.node_v
                or expected.port_v != port_edge.port_v
            ):
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge endpoint metadata must match topology edge endpoints"
                )
            if (
                endpoint_a != (port_edge.node_u, backend_port_u)
                and endpoint_b != (port_edge.node_u, backend_port_u)
            ):
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge port_u must match a live topology endpoint"
                )
            if (
                endpoint_a != (port_edge.node_v, backend_port_v)
                and endpoint_b != (port_edge.node_v, backend_port_v)
            ):
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge port_v must match a live topology endpoint"
                )
            if port_edge.conductance < 0.0:
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge conductance must be non-negative"
                )
            if not isinstance(port_edge.flux_uv, float):
                raise InvalidStateTransitionError(
                    "GRC9 PortEdge flux_uv must be a float"
                )
        for label_mapping in (
            state.geometric_length,
            state.temporal_delay,
            state.flux_coupling,
        ):
            if any(edge_id not in live_edge_ids for edge_id in label_mapping):
                raise InvalidStateTransitionError(
                    "GRC9 edge-label keys must reference live topology edges"
                )
        for expansion_id, record in state.expansion_registry.items():
            if not isinstance(expansion_id, str):
                raise InvalidStateTransitionError(
                    "GRC9 expansion_registry keys must be strings"
                )
            if not isinstance(record, ExpansionRecord):
                raise InvalidStateTransitionError(
                    "GRC9 expansion_registry values must be ExpansionRecord instances"
                )
            if any(node_id not in live_node_ids for node_id in record.module_node_ids):
                raise InvalidStateTransitionError(
                    "GRC9 expansion module_node_ids must reference live topology nodes"
                )
        if any(coherence < 0.0 for coherence in state.node_coherence.values()):
            raise InvalidStateTransitionError(
                "GRC9State.node_coherence values must be non-negative"
            )


__all__ = ["GRC9", "SparkKind"]

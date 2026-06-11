"""Construction and queue-priming facades for executable LGRC9V3.

This module owns source-to-runtime wiring and reusable queue-priming policies.
It does not define new LGRC semantics; it moves accepted example orchestration
into tested library helpers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from pygrc.core import GRCParams, InvalidLandscapeSeedError, canonicalize_json_value
from pygrc.landscapes import LandscapeSeed, load_landscape_seed, validate_landscape_seed
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3LandscapeExampleDocument,
    GRCL9V3SourceDocument,
    compile_grcl9v3_landscape_example_to_source,
    extract_grcl9v3_landscape_example_from_seed,
)

from .grc_9_v3 import GRC9V3
from .grc_9_v3_grcl9v3_lowering import (
    GRCL9V3LoweringResult,
    lower_grcl9v3_source_to_grc9v3_state,
)
from .lgrc_9_v3_contract import (
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
)
from .lgrc_9_v3_runtime import LGRC9V3


LandscapeSeedInput: TypeAlias = LandscapeSeed | str | Path
LGRC9V3ParamsInput: TypeAlias = GRCParams | Mapping[str, Any] | None


@dataclass(frozen=True)
class LGRC9V3LandscapeBuildResult:
    """Source-to-runtime build record for one landscape-backed LGRC9V3 model."""

    seed: LandscapeSeed
    seed_path: Path | None
    example: GRCL9V3LandscapeExampleDocument
    source: GRCL9V3SourceDocument
    lowering: GRCL9V3LoweringResult
    model: LGRC9V3

    def metadata(self) -> dict[str, Any]:
        """Return compact metadata suitable for examples and telemetry labels."""

        return {
            "seed_name": self.seed.meta.name,
            "seed_path": None if self.seed_path is None else str(self.seed_path),
            "example_name": self.example.example_name,
            "source_construct_kinds": [
                construct.construct_kind for construct in self.source.constructs
            ],
            "node_id_by_role": dict(self.lowering.node_id_by_role),
            "edge_id_by_role": dict(self.lowering.edge_id_by_role),
        }


@dataclass(frozen=True)
class LGRC9V3PacketDepartureSpec:
    """Library-owned packet departure specification for queue priming."""

    source_node_id: int
    target_node_id: int
    edge_id: int
    amount: float
    departure_event_time_key: float
    arrival_event_time_key: float | None = None
    scheduler_event_index: int | None = None
    packet_index: int = 0
    source_lineage_id: str | None = None
    target_lineage_id: str | None = None


@dataclass(frozen=True)
class LGRC9V3BroadSeedPacketPolicy:
    """Deterministic broad packet-seeding policy for a current topology."""

    start_time: float = 1.0
    start_scheduler_index: int = 10
    packet_index_start: int = 1000
    time_spacing: float = 0.002
    max_amount: float = 0.001
    source_fraction: float = 0.02
    min_amount_epsilon: float = 1e-12


@dataclass(frozen=True)
class LGRC9V3QueuePrimingResult:
    """Summary of queue entries scheduled by one priming helper."""

    scheduled_count: int
    skipped_zero_or_low_coherence: int = 0
    min_amount: float = 0.0
    max_amount: float = 0.0
    event_ids: tuple[str, ...] = ()

    def to_summary(self) -> dict[str, Any]:
        """Return the stable summary shape used by examples."""

        return {
            "scheduled": self.scheduled_count,
            "skipped_zero_or_low_coherence": self.skipped_zero_or_low_coherence,
            "min_amount": self.min_amount,
            "max_amount": self.max_amount,
        }


@dataclass(frozen=True)
class LGRC9V3CorrectedCascadeScenarioPolicy:
    """Accepted corrected-cascade reproduction policy.

    The values mirror the tracked comparison example. They are policy data, not
    new runtime semantics.
    """

    initial_packet: LGRC9V3PacketDepartureSpec = LGRC9V3PacketDepartureSpec(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=1e-6,
        departure_event_time_key=0.0,
        arrival_event_time_key=0.1,
        scheduler_event_index=1,
        packet_index=1,
    )
    boundary_birth_parent_node_id: int = 16
    boundary_birth_parent_port_id: int = 5
    boundary_birth_outward_flux_pressure: float = 9.559979992827932
    boundary_birth_event_time_key: float = 0.2
    boundary_birth_scheduler_event_index: int = 3
    boundary_birth_rng_sample: float = 0.8444218515250481
    boundary_birth_edge_delay: float = 1.0
    route_total_forward_fraction: float = 0.05
    broad_seed_policy: LGRC9V3BroadSeedPacketPolicy = LGRC9V3BroadSeedPacketPolicy()

    def causal_modes(self) -> dict[str, Any]:
        """Return the LGRC-3 causal modes for the accepted scenario."""

        return {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY,
            "proper_time_accumulation_policy": PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
            "causal_boundary_birth_coherence_source": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT
            ),
            "causal_boundary_birth_edge_delay_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
            ),
            "causal_topology_integration_allowed": True,
            "causal_spark_expansion_allowed": True,
            "causal_refinement_packet_transport_allowed": True,
            "causal_proper_time_inheritance_allowed": True,
            "causal_collapse_reabsorption_allowed": False,
            "causal_identity_acceptance_allowed": False,
        }


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


def _params_mapping(
    seed: LandscapeSeed,
    params: LGRC9V3ParamsInput,
) -> dict[str, Any]:
    if params is None:
        return {"dt": float(seed.constitutive_profile.dt)}
    if isinstance(params, GRCParams):
        return dict(canonicalize_json_value(params.raw_config))
    if not isinstance(params, Mapping):
        raise TypeError("params input must be a GRCParams instance, mapping, or None")
    return deepcopy(dict(params))


def _split_runtime_config(
    config: Mapping[str, Any],
    *,
    causal_modes: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    grc_config = deepcopy(dict(config))
    existing_modes = grc_config.pop("causal_modes", None)
    runtime_config = deepcopy(grc_config)
    if causal_modes is not None:
        runtime_config["causal_modes"] = deepcopy(dict(causal_modes))
    elif existing_modes is not None:
        if not isinstance(existing_modes, Mapping):
            raise TypeError("params['causal_modes'] must be a mapping")
        runtime_config["causal_modes"] = deepcopy(dict(existing_modes))
    return grc_config, runtime_config


def prepare_lgrc9v3_landscape_runtime(
    seed: LandscapeSeedInput,
    *,
    params: LGRC9V3ParamsInput = None,
    causal_modes: Mapping[str, Any] | None = None,
    validate_seed: bool = True,
) -> LGRC9V3LandscapeBuildResult:
    """Lower one GRCL9V3 seed and construct executable `LGRC9V3`.

    The preserved sequence is:

    `LandscapeSeed -> GRCL9V3 source -> GRC9V3State -> LGRC9V3RuntimeState`.
    """

    resolved_seed, seed_path = _coerce_landscape_seed(
        seed,
        validate_seed=validate_seed,
    )
    example = extract_grcl9v3_landscape_example_from_seed(
        resolved_seed,
        seed_path=seed_path,
    )
    if example is None:
        raise InvalidLandscapeSeedError(
            "landscape seed does not declare a GRCL9V3 example"
        )
    source = compile_grcl9v3_landscape_example_to_source(example)
    base_config = _params_mapping(resolved_seed, params)
    grc_config, runtime_config = _split_runtime_config(
        base_config,
        causal_modes=causal_modes,
    )
    lowering = lower_grcl9v3_source_to_grc9v3_state(source, params=grc_config)
    model = LGRC9V3.from_state(lowering.state, runtime_config)
    return LGRC9V3LandscapeBuildResult(
        seed=resolved_seed,
        seed_path=seed_path,
        example=example,
        source=source,
        lowering=lowering,
        model=model,
    )


def build_lgrc9v3_from_landscape_seed(
    seed: LandscapeSeedInput,
    *,
    params: LGRC9V3ParamsInput = None,
    causal_modes: Mapping[str, Any] | None = None,
    validate_seed: bool = True,
) -> LGRC9V3:
    """Construct executable LGRC9V3 from one landscape seed."""

    return prepare_lgrc9v3_landscape_runtime(
        seed,
        params=params,
        causal_modes=causal_modes,
        validate_seed=validate_seed,
    ).model


def prepare_lgrc9v3_grc9v3_diagnostics(model: LGRC9V3) -> LGRC9V3:
    """Refresh inherited GRC9V3 diagnostic labels without running GRC9V3.step()."""

    prep = GRC9V3(params=model.get_params(), state=model.get_state().base_state)
    prep.rebuild_differential_state()
    prep.rebuild_transport_state()
    prep.rebuild_differential_state()
    prep.rebuild_identity_state()
    model.get_state().base_state = prep.get_state()
    return model


def build_lgrc9v3_corrected_cascade_runtime(
    base_model: GRC9V3,
    *,
    policy: LGRC9V3CorrectedCascadeScenarioPolicy = LGRC9V3CorrectedCascadeScenarioPolicy(),
) -> LGRC9V3:
    """Wrap a corrected GRC9V3 source state in accepted LGRC9V3 scenario modes."""

    raw = dict(canonicalize_json_value(base_model.get_params().raw_config))
    raw["causal_modes"] = policy.causal_modes()
    model = LGRC9V3.from_state(base_model.get_state(), raw)
    return prepare_lgrc9v3_grc9v3_diagnostics(model)


def lgrc9v3_graph_routes_for_current_topology(
    model: LGRC9V3,
    *,
    total_forward_fraction: float = 0.05,
) -> dict[int, list[dict[str, Any]]]:
    """Route a fixed fraction of arrivals across all current incident edges."""

    if total_forward_fraction < 0.0:
        raise ValueError("total_forward_fraction must be >= 0")
    state = model.get_state().base_state
    routes: dict[int, list[dict[str, Any]]] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        incident = sorted(state.topology.incident_edge_ids(node_id))
        if not incident:
            routes[int(node_id)] = []
            continue
        fraction = float(total_forward_fraction) / float(len(incident))
        node_routes: list[dict[str, Any]] = []
        for edge_id in incident:
            edge = state.port_edges[int(edge_id)]
            if int(edge.node_u) == int(node_id):
                target = int(edge.node_v)
            elif int(edge.node_v) == int(node_id):
                target = int(edge.node_u)
            else:
                continue
            node_routes.append(
                {
                    "target_node_id": target,
                    "edge_id": int(edge_id),
                    "amount_fraction": fraction,
                }
            )
        routes[int(node_id)] = node_routes
    return routes


def lgrc9v3_directed_seed_packet_amount(
    model: LGRC9V3,
    *,
    source_node_id: int,
    policy: LGRC9V3BroadSeedPacketPolicy = LGRC9V3BroadSeedPacketPolicy(),
) -> float:
    """Scale seed packets so low-coherence sources are not over-debited."""

    state = model.get_state().base_state
    coherence = float(state.nodes[int(source_node_id)].coherence)
    degree = max(1, len(tuple(state.topology.incident_edge_ids(int(source_node_id)))))
    return max(
        0.0,
        min(
            float(policy.max_amount),
            float(policy.source_fraction) * coherence / float(degree),
        ),
    )


def prime_lgrc9v3_packet_departures(
    model: LGRC9V3,
    packet_specs: Sequence[LGRC9V3PacketDepartureSpec],
) -> LGRC9V3QueuePrimingResult:
    """Schedule explicit packet departures into a model-owned event queue."""

    before_event_ids = {
        event.event_id
        for event in model.get_state().packet_ledger.event_queue_records
    }
    amounts: list[float] = []
    for spec in packet_specs:
        model.schedule_packet_departure(
            source_node_id=spec.source_node_id,
            target_node_id=spec.target_node_id,
            edge_id=spec.edge_id,
            amount=spec.amount,
            departure_event_time_key=spec.departure_event_time_key,
            arrival_event_time_key=spec.arrival_event_time_key,
            scheduler_event_index=spec.scheduler_event_index,
            packet_index=spec.packet_index,
            source_lineage_id=spec.source_lineage_id,
            target_lineage_id=spec.target_lineage_id,
        )
        amounts.append(float(spec.amount))
    after_events = model.get_state().packet_ledger.event_queue_records
    event_ids = tuple(
        sorted(event.event_id for event in after_events if event.event_id not in before_event_ids)
    )
    return LGRC9V3QueuePrimingResult(
        scheduled_count=len(packet_specs),
        min_amount=min(amounts) if amounts else 0.0,
        max_amount=max(amounts) if amounts else 0.0,
        event_ids=event_ids,
    )


def prime_lgrc9v3_broad_seed_packets(
    model: LGRC9V3,
    *,
    policy: LGRC9V3BroadSeedPacketPolicy = LGRC9V3BroadSeedPacketPolicy(),
) -> LGRC9V3QueuePrimingResult:
    """Seed packet traffic across all directed current-topology edges."""

    scheduled = 0
    skipped = 0
    amounts: list[float] = []
    before_event_ids = {
        event.event_id
        for event in model.get_state().packet_ledger.event_queue_records
    }
    state = model.get_state().base_state
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        edge = state.port_edges[int(edge_id)]
        for source, target in (
            (int(edge.node_u), int(edge.node_v)),
            (int(edge.node_v), int(edge.node_u)),
        ):
            amount = lgrc9v3_directed_seed_packet_amount(
                model,
                source_node_id=source,
                policy=policy,
            )
            if amount <= float(policy.min_amount_epsilon):
                skipped += 1
                continue
            departure_time = float(policy.start_time) + float(policy.time_spacing) * scheduled
            model.schedule_packet_departure(
                source_node_id=source,
                target_node_id=target,
                edge_id=int(edge_id),
                amount=amount,
                departure_event_time_key=departure_time,
                scheduler_event_index=int(policy.start_scheduler_index) + scheduled * 2,
                packet_index=int(policy.packet_index_start) + scheduled,
            )
            amounts.append(amount)
            scheduled += 1
    after_events = model.get_state().packet_ledger.event_queue_records
    event_ids = tuple(
        sorted(event.event_id for event in after_events if event.event_id not in before_event_ids)
    )
    return LGRC9V3QueuePrimingResult(
        scheduled_count=scheduled,
        skipped_zero_or_low_coherence=skipped,
        min_amount=min(amounts) if amounts else 0.0,
        max_amount=max(amounts) if amounts else 0.0,
        event_ids=event_ids,
    )


def prime_lgrc9v3_corrected_cascade_queues(
    model: LGRC9V3,
    *,
    policy: LGRC9V3CorrectedCascadeScenarioPolicy = LGRC9V3CorrectedCascadeScenarioPolicy(),
) -> dict[str, Any]:
    """Prime the accepted corrected-cascade initial packet and birth queues."""

    packet_result = prime_lgrc9v3_packet_departures(
        model,
        (policy.initial_packet,),
    )
    before_birth_count = len(model.get_state().boundary_birth_trial_queue)
    model.schedule_causal_boundary_birth_trial(
        parent_node_id=policy.boundary_birth_parent_node_id,
        parent_port_id=policy.boundary_birth_parent_port_id,
        outward_flux_pressure=policy.boundary_birth_outward_flux_pressure,
        event_time_key=policy.boundary_birth_event_time_key,
        scheduler_event_index=policy.boundary_birth_scheduler_event_index,
        rng_sample=policy.boundary_birth_rng_sample,
        edge_delay=policy.boundary_birth_edge_delay,
    )
    return {
        "initial_packets": packet_result.to_summary(),
        "boundary_birth_trials_scheduled": (
            len(model.get_state().boundary_birth_trial_queue) - before_birth_count
        ),
    }


def prime_lgrc9v3_corrected_cascade_broad_seed(
    model: LGRC9V3,
    *,
    policy: LGRC9V3CorrectedCascadeScenarioPolicy = LGRC9V3CorrectedCascadeScenarioPolicy(),
) -> LGRC9V3QueuePrimingResult:
    """Prime accepted corrected-cascade routes and broad seed packets."""

    model.set_causal_flux_routes(
        lgrc9v3_graph_routes_for_current_topology(
            model,
            total_forward_fraction=policy.route_total_forward_fraction,
        )
    )
    return prime_lgrc9v3_broad_seed_packets(
        model,
        policy=policy.broad_seed_policy,
    )


__all__ = [
    "LandscapeSeedInput",
    "LGRC9V3BroadSeedPacketPolicy",
    "LGRC9V3CorrectedCascadeScenarioPolicy",
    "LGRC9V3LandscapeBuildResult",
    "LGRC9V3PacketDepartureSpec",
    "LGRC9V3ParamsInput",
    "LGRC9V3QueuePrimingResult",
    "build_lgrc9v3_corrected_cascade_runtime",
    "build_lgrc9v3_from_landscape_seed",
    "lgrc9v3_directed_seed_packet_amount",
    "lgrc9v3_graph_routes_for_current_topology",
    "prepare_lgrc9v3_grc9v3_diagnostics",
    "prepare_lgrc9v3_landscape_runtime",
    "prime_lgrc9v3_broad_seed_packets",
    "prime_lgrc9v3_corrected_cascade_broad_seed",
    "prime_lgrc9v3_corrected_cascade_queues",
    "prime_lgrc9v3_packet_departures",
]

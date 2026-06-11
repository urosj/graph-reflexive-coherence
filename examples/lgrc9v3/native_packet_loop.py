"""Run a native LGRC9V3 surplus-triggered packet loop.

This example demonstrates the Phase 8 native packet-loop surface:

    returned packet arrival
    -> measured pole surplus trigger
    -> child packet departure scheduled by producer
    -> child departure processed by step()

The example is intentionally small. It uses a two-node/two-channel loop so the
runtime evidence is easy to inspect. It does not make movement, agency, or
native GRC9V3 proposal-flux loop claims.
"""

from __future__ import annotations

import json

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
)


N_CYCLES = 3


def build_state() -> GRC9V3State:
    """Build a two-pole fixed-topology substrate."""

    graph = PortGraphBackend()
    source = graph.add_node({"label": "source_pole"})
    sink = graph.add_node({"label": "sink_pole"})
    edge_forward = graph.connect_ports(source, 0, sink, 0, {"kind": "forward"})
    edge_return = graph.connect_ports(sink, 1, source, 1, {"kind": "return"})
    return GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=2.0),
            sink: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge_forward: PortEdge(source, 1, sink, 1, conductance=1.0, flux_uv=0.0),
            edge_return: PortEdge(sink, 2, source, 2, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_forward: 1.0, edge_return: 1.0},
        geometric_length={edge_forward: 1.0, edge_return: 1.0},
        temporal_delay={edge_forward: 1.0, edge_return: 1.0},
        flux_coupling={edge_forward: 0.0, edge_return: 0.0},
    )


def build_route_aspect() -> LGRC9V3RouteAspect:
    """Define the source/sink pole route semantics."""

    return LGRC9V3RouteAspect(
        route_aspect_id="example_two_pole_native_packet_loop",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            LGRC9V3RouteAspectChannel(
                channel_id="S_to_K",
                source_pole_id="S",
                target_pole_id="K",
                expected_next_channel_id="K_to_S",
                route_hops=(
                    LGRC9V3RouteAspectHop(
                        source_node_id=0,
                        target_node_id=1,
                        edge_id=0,
                    ),
                ),
            ),
            LGRC9V3RouteAspectChannel(
                channel_id="K_to_S",
                source_pole_id="K",
                target_pole_id="S",
                expected_next_channel_id="S_to_K",
                route_hops=(
                    LGRC9V3RouteAspectHop(
                        source_node_id=1,
                        target_node_id=0,
                        edge_id=1,
                    ),
                ),
            ),
        ),
        channel_sequence=("S_to_K", "K_to_S"),
    )


def configure_trigger(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
    reference_mass: float,
    eligible_channel_id: str,
) -> None:
    """Configure one surplus trigger without mutating packet budget."""

    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        trigger_threshold=0.049,
        packet_amount=0.1,
        eligible_channel_id=eligible_channel_id,
    )


def seed_parent_return(model: LGRC9V3) -> None:
    """Create the initial returned arrival that makes self-rearm auditable."""

    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=1,
        amount=0.25,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.run_event_queue(max_events=2)


def main() -> None:
    """Run three native self-rearming packet cycles and print a compact report."""

    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    route_aspect = build_route_aspect()
    producer_results = []
    seed_parent_return(model)

    for _cycle_index in range(N_CYCLES):
        configure_trigger(
            model,
            route_aspect=route_aspect,
            source_pole_id="S",
            reference_mass=2.15,
            eligible_channel_id="S_to_K",
        )
        produced_source = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        producer_results.append(produced_source.to_artifact())
        model.step()
        model.step()

        configure_trigger(
            model,
            route_aspect=route_aspect,
            source_pole_id="K",
            reference_mass=0.75,
            eligible_channel_id="K_to_S",
        )
        produced_sink = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        producer_results.append(produced_sink.to_artifact())
        model.step()
        model.step()

    snapshot = model.snapshot()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=snapshot["events"],
        production_results=tuple(producer_results),
    )
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    report = {
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_d2_3_equivalent": validation["valid"],
        "completed_self_rearm_count": validation["completed_count"],
        "cycle_count": validation["completed_count"] // 2,
        "route_aspect_digest": route_aspect.route_aspect_digest,
        "node_plus_packet_budget": runtime["packet_ledger"]["conserved_budget_total"],
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }

    print("LGRC9V3 native packet loop")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

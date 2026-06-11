"""Run the current active LGRC-3 causal-history helper chain.

What this example does:
    Builds the shared Lane B `GRC9V3` fixture, creates one LGRC-2 in-flight
    packet, consumes the existing GRC9V3 mechanical expansion event, and then
    runs the current active LGRC-3 evidence processors:

    - packet transport through refinement;
    - uniform proper-time inheritance after refinement;
    - collapse/reabsorption lineage and budget evidence;
    - packet transport through collapse/reabsorption;
    - sink-local proper-time identity persistence evaluation;
    - explicit identity-acceptance event emission;
    - topology-event replay validation.

Why it is needed:
    Iteration 23 closes the active LGRC-3 helper/evidence slice. The point is
    to show that the pieces compose into an auditable causal-history chain
    while still being honest about the runtime boundary.

What it is not:
    This helper-chain example is not the executable `LGRC9V3.step()` path. The
    spark/refinement trigger still comes from the proven synchronous `GRC9V3`
    Lane B path. LGRC9V3 helper processors then own packet transport,
    proper-time inheritance, collapse/reabsorption evidence, identity evidence,
    and replay validation around that event.

Alternatives:
    Use `packetized_causal_flux.py` for fixed-topology LGRC-2 only. Use
    `refinement_packet_transport.py` when you only want the first LGRC-3
    refinement-transport slice.

References:
    docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
    specs/lgrc-9-v3-spec.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC9V3_EXAMPLES = REPO_ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_model  # noqa: E402
from pygrc.core import GRCEvent  # noqa: E402
from pygrc.models import (  # noqa: E402
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    build_lgrc9v3_packet_ledger,
    compact_lgrc9v3_packet_ledger,
    compute_lgrc9v3_edge_causal_delay,
    derive_lgrc9v3_packet_arrival_event_time_key,
    emit_lgrc9v3_proper_time_identity_acceptance,
    evaluate_lgrc9v3_proper_time_identity_persistence,
    process_lgrc9v3_collapse_reabsorption,
    process_lgrc9v3_packet_departure,
    process_lgrc9v3_proper_time_inheritance,
    transport_lgrc9v3_packets_through_collapse_reabsorption,
    transport_lgrc9v3_packets_through_refinement,
    validate_lgrc9v3_topology_event_replay,
)


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON so the evidence shape is easy to inspect."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def topology_signature(state: object) -> dict[str, Any]:
    """Return the topology signature consumed by refinement transport.

    Why this helper is local:
        LGRC9V3 does not yet have a concrete model class that owns checkpoint
        export. Until Iteration 24+ decides that boundary, examples provide the
        small signature explicitly.
    """

    graph = getattr(state, "topology")
    edge_records: list[dict[str, Any]] = []
    for edge_id in sorted(int(edge_id) for edge_id in graph.iter_live_edge_ids()):
        endpoint_a, endpoint_b = graph.edge_ports(edge_id)
        edge_records.append(
            {
                "edge_id": int(edge_id),
                "endpoints": [
                    [int(endpoint_a[0]), int(endpoint_a[1])],
                    [int(endpoint_b[0]), int(endpoint_b[1])],
                ],
            }
        )
    return {
        "node_ids": sorted(int(node_id) for node_id in graph.iter_live_node_ids()),
        "edge_records": edge_records,
    }


def first_event(events: list[GRCEvent], *, kind: str) -> GRCEvent:
    """Return the first event of a given kind or fail with a direct message."""

    for event in events:
        if event.kind == kind:
            return event
    raise RuntimeError(f"expected event kind {kind!r}")


def main() -> None:
    """Run one active LGRC-3 helper chain over an existing GRC9V3 state."""

    model = make_model(spark_lane=LANE_B)
    state = model.get_state()
    ledger = build_lgrc9v3_packet_ledger(state=state)
    edge_delay = compute_lgrc9v3_edge_causal_delay(
        state,
        policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
        tau_0=2.0,
    )
    arrival_key = derive_lgrc9v3_packet_arrival_event_time_key(
        departure_event_time_key=1.0,
        edge_id=0,
        edge_causal_delay=edge_delay,
    )

    departure = process_lgrc9v3_packet_departure(
        state,
        ledger,
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        arrival_event_time_key=arrival_key,
        scheduler_event_index=1,
        source_lineage_id="sink-0-before-refinement",
        target_lineage_id="node-1",
    )
    compact = compact_lgrc9v3_packet_ledger(departure.ledger)

    expansion = first_event(
        model.apply_hybrid_sparks(),
        kind="hybrid_mechanical_expansion",
    )
    refinement_transport = transport_lgrc9v3_packets_through_refinement(
        departure.ledger,
        expansion,
        post_topology_signature=topology_signature(state),
        pending_flux_ledger=compact,
    )
    inheritance = process_lgrc9v3_proper_time_inheritance(
        expansion,
        parent_node_proper_time={0: 1.0},
        event_time_key=1.0,
        scheduler_event_index=2,
        checkpoint_index=1,
    )

    collapse = process_lgrc9v3_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        competing_sink_ids=(0, 2),
        selected_sink_id=2,
        losing_sink_ids=(0,),
        transferred_node_ids=(0,),
        lineage_transfer_map={0: "sink-2"},
        source_lineage_ids={0: "sink-0-before-refinement"},
        target_lineage_id="sink-2",
        node_proper_time={0: 4.0, 2: 9.0},
        coherence_transfer_amount=1.0,
        budget_before=refinement_transport.budget_after,
        event_time_key=8.0,
        scheduler_event_index=6,
        checkpoint_index=3,
        packet_ledger=departure.ledger,
        pending_flux_ledger=compact,
        collapse_reabsorption_allowed=True,
    )
    collapse_transport = transport_lgrc9v3_packets_through_collapse_reabsorption(
        departure.ledger,
        collapse,
        pending_flux_ledger=compact,
    )

    identity_evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
        source_topology_event_ids=(collapse.topology_event_id,),
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        sink_node_id=2,
        lineage_id="sink-2",
        basin_node_ids=(2, 5),
        node_proper_time={2: 13.0, 5: 12.0},
        window_start_sink_proper_time=4.0,
        window_start_event_time_key=8.0,
        window_end_event_time_key=12.0,
        scheduler_event_index=8,
        checkpoint_index=4,
        event_time_key=12.0,
        local_median_edge_delay=2.0,
        source_basin_evidence_id="basin-core-sink-2",
        budget_before=collapse_transport.budget_after,
        budget_after=collapse_transport.budget_after,
    )
    identity_event = emit_lgrc9v3_proper_time_identity_acceptance(
        identity_evaluation,
        identity_acceptance_allowed=True,
    )
    replay = validate_lgrc9v3_topology_event_replay(
        (
            refinement_transport.to_artifact(),
            inheritance.to_artifact(),
            collapse.to_artifact(),
            collapse_transport.to_artifact(),
            identity_evaluation.to_artifact(),
            identity_event,
        )
    )

    print("LGRC9V3 active LGRC-3 causal-history helper chain")
    print_json(
        "source_expansion",
        {
            "kind": expansion.kind,
            "source": "existing GRC9V3 Lane B mechanical expansion",
            "expansion_id": expansion.payload.get("expansion_id"),
            "source_candidate_event_id": expansion.payload.get(
                "source_candidate_event_id"
            ),
        },
    )
    print_json(
        "active_lgrc3_evidence",
        {
            "refinement_transport_kind": refinement_transport.to_artifact()[
                "artifact_kind"
            ],
            "proper_time_inheritance_kind": inheritance.to_artifact()[
                "artifact_kind"
            ],
            "collapse_kind": collapse.to_artifact()["artifact_kind"],
            "collapse_packet_transport_kind": collapse_transport.to_artifact()[
                "artifact_kind"
            ],
            "identity_evaluation_kind": identity_evaluation.to_artifact()[
                "artifact_kind"
            ],
            "identity_event_kind": identity_event.kind,
            "replay_validation_kind": replay.to_artifact()["artifact_kind"],
        },
    )
    print_json(
        "budget_and_identity",
        {
            "refinement_budget_error": refinement_transport.budget_error,
            "collapse_budget_error": collapse.budget_error,
            "collapse_transport_budget_error": collapse_transport.budget_error,
            "identity_persistence_passed": identity_evaluation.persistence_passed,
            "identity_acceptance_emitted": identity_event.payload[
                "identity_acceptance_emitted"
            ],
            "mechanical_expansion_is_identity_acceptance": identity_event.payload[
                "mechanical_expansion_is_identity_acceptance"
            ],
            "refinement_packet_transport_is_identity_transfer": (
                identity_event.payload[
                    "refinement_packet_transport_is_identity_transfer"
                ]
            ),
        },
    )
    print_json(
        "replay_validation",
        {
            "accepted_artifact_count": replay.accepted_artifact_count,
            "event_time_order_valid": replay.event_time_order_valid,
            "lineage_continuity_valid": replay.lineage_continuity_valid,
            "budget_conservation_valid": replay.budget_conservation_valid,
            "replay_valid": replay.replay_valid,
            "budget_error": replay.budget_error,
        },
    )

    print(
        "\nInterpretation: this is active LGRC-3 processing around a known "
        "GRC9V3 topology event. It proves the current helper/evidence surfaces "
        "compose with packet budget, proper time, lineage, identity, and replay "
        "audits. It is separate from the executable LGRC9V3.step() examples, "
        "which cover causal queue processing and causally scheduled Lane A/"
        "Lane B spark diagnostics."
    )


if __name__ == "__main__":
    main()

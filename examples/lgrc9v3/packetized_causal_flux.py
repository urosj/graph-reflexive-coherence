"""Process one fixed-topology LGRC-2 packet departure/arrival cycle.

What this example does:
    Builds the shared `GRC9V3` fixture, creates an external LGRC-2 packet
    ledger, derives the arrival event-time key from a captured edge-delay
    surface, processes one packet departure from node 0 to node 1, then
    processes the queued arrival.

Why it is needed:
    This script preserves the lower-level helper API because it is still useful
    for inspecting packet transition contracts without model orchestration. The
    executable `LGRC9V3` model class now wraps the same packet semantics in its
    queue loop.

    `GRC9V3State + LGRC9V3PacketLedger + processing helpers`

Alternatives:
    Use `causal_history_surfaces.py` for LGRC-0/LGRC-1 annotation and
    eligibility evidence. Use `executable_runtime.py` or
    `executable_packet_queue.py` when you want the model-owned LGRC9V3 event
    queue.

References:
    docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
    specs/lgrc-9-v3-spec.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC9V3_EXAMPLES = REPO_ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import make_model  # noqa: E402
from pygrc.models import (  # noqa: E402
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    build_lgrc9v3_packet_ledger,
    compact_lgrc9v3_packet_ledger,
    compute_lgrc9v3_edge_causal_delay,
    derive_lgrc9v3_packet_arrival_eligibility,
    derive_lgrc9v3_packet_arrival_event_time_key,
    process_lgrc9v3_next_packet_event,
    schedule_lgrc9v3_packet_departure,
)


def print_json(label: str, payload: object) -> None:
    """Print compact deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def ledger_summary(result: object) -> dict[str, object]:
    """Return the LGRC-2 budget fields worth checking first."""

    ledger = getattr(result, "ledger")
    event = getattr(result, "processed_event")
    packet = getattr(result, "packet_record")
    return {
        "processed_event_kind": event.event_kind,
        "scheduler_event_index": event.scheduler_event_index,
        "event_time_key": event.event_time_key,
        "packet_state": packet.packet_state,
        "source_node_id": event.source_node_id,
        "target_node_id": event.target_node_id,
        "edge_id": event.edge_id,
        "amount": event.amount,
        "node_coherence_total": ledger.node_coherence_total,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "conserved_budget_total": ledger.conserved_budget_total,
        "budget_before": result.budget_before,
        "budget_after": result.budget_after,
        "budget_error": result.budget_error,
        "topology_mutated": result.topology_mutated,
        "spark_event_emitted": result.spark_event_emitted,
        "mechanical_expansion_emitted": result.mechanical_expansion_emitted,
        "identity_acceptance_emitted": result.identity_acceptance_emitted,
    }


def main() -> None:
    """Run one fixed-topology LGRC-2 packet cycle over `GRC9V3State`."""

    model = make_model()
    state = model.get_state()
    ledger = build_lgrc9v3_packet_ledger(state=state)
    edge_delay = compute_lgrc9v3_edge_causal_delay(
        state,
        policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
        tau_0=2.0,
    )
    departure_key = 1.0
    arrival_key = derive_lgrc9v3_packet_arrival_event_time_key(
        departure_event_time_key=departure_key,
        edge_id=0,
        edge_causal_delay=edge_delay,
    )

    scheduled = schedule_lgrc9v3_packet_departure(
        state,
        ledger,
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.5,
        departure_event_time_key=departure_key,
        arrival_event_time_key=arrival_key,
        scheduler_event_index=1,
    )
    departure = process_lgrc9v3_next_packet_event(state, scheduled)
    compact = compact_lgrc9v3_packet_ledger(departure.ledger)
    arrival = process_lgrc9v3_next_packet_event(state, departure.ledger)
    eligibility = derive_lgrc9v3_packet_arrival_eligibility(arrival)

    print("LGRC9V3 fixed-topology packetized causal flux")
    print_json(
        "scheduled",
        {
            "packet_state": scheduled.packet_records[0].packet_state,
            "queued_event_kind": scheduled.event_queue_records[0].event_kind,
            "edge_causal_delay": edge_delay[0],
            "node_coherence_total": scheduled.node_coherence_total,
            "in_flight_packet_total": scheduled.in_flight_packet_total,
            "conserved_budget_total": scheduled.conserved_budget_total,
        },
    )
    print_json("departure", ledger_summary(departure))
    print_json(
        "compact_pending_flux",
        {
            "artifact_kind": compact.to_artifact()["artifact_kind"],
            "expanded_packet_count": compact.expanded_packet_count,
            "compact_entry_count": compact.compact_entry_count,
            "pending_flux_total": compact.pending_flux_total,
            "conserved_budget_total": compact.conserved_budget_total,
            "lineage_preserved": compact.lineage_preserved,
            "transport_ready_for_refinement": compact.transport_ready_for_refinement,
        },
    )
    print_json("arrival", ledger_summary(arrival))
    print_json(
        "arrival_eligibility",
        {
            "artifact_kind": eligibility.to_artifact()["artifact_kind"],
            "target_node_id": eligibility.target_node_id,
            "local_update_eligible": eligibility.local_update_eligible,
            "spark_diagnostic_eligible": eligibility.spark_diagnostic_eligible,
            "spark_event_emitted": eligibility.spark_event_emitted,
        },
    )
    print_json(
        "final_node_coherence",
        {
            "node_0": state.nodes[0].coherence,
            "node_1": state.nodes[1].coherence,
        },
    )

    print(
        "\nInterpretation: this is active LGRC-2 packet processing over an "
        "existing GRC9V3State. It preserves sum_i C_i + sum_p C_p on fixed "
        "topology through the helper API. Use executable_runtime.py for the "
        "model-owned LGRC9V3 queue loop."
    )


if __name__ == "__main__":
    main()

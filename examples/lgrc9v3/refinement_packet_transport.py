"""Transport LGRC-2 packet evidence through one GRC9V3 refinement.

What this example does:
    Builds the shared Lane B `GRC9V3` fixture, creates one in-flight LGRC-2
    packet from the saturated center node, lets the existing synchronous
    `GRC9V3` spark layer produce a mechanical expansion, then transports the
    external packet evidence through that expansion.

Why it is needed:
    This is the current LGRC-3 implementation slice. It proves that the
    causal-history layer can consume GRC9V3 refinement evidence and preserve
    packet ids, packet amount, endpoint lineage, queued arrival targets, and
    budget evidence.

What it is not:
    This does not run a full LGRC9V3 model loop. It does not causally schedule
    spark predicates. It does not implement collapse/reabsorption or
    proper-time identity acceptance.

Alternatives:
    Use `packetized_causal_flux.py` for fixed-topology LGRC-2 packet
    departure/arrival. Use `examples/grc9v3/lane_b_column_h.py` to inspect
    the underlying synchronous Lane B candidate that produces the expansion.

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
    build_lgrc9v3_packet_ledger,
    compact_lgrc9v3_packet_ledger,
    compute_lgrc9v3_edge_causal_delay,
    derive_lgrc9v3_packet_arrival_event_time_key,
    process_lgrc9v3_packet_departure,
    transport_lgrc9v3_packets_through_refinement,
)


def print_json(label: str, payload: object) -> None:
    """Print compact deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def topology_signature(state: object) -> dict[str, Any]:
    """Return the small topology signature needed by LGRC-3 transport.

    Why it is local:
        The current LGRC-3 transport helper is still a helper/evidence surface,
        not a model class. A future LGRC9V3 runtime can own this export as a
        stable method once Iteration 24 accepts a concrete runtime boundary.
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
    """Return the first event of a given kind or fail clearly."""

    for event in events:
        if event.kind == kind:
            return event
    raise RuntimeError(f"expected event kind {kind!r}")


def main() -> None:
    """Run one LGRC-3 refinement packet transport smoke path."""

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
        amount=0.01,
        departure_event_time_key=1.0,
        arrival_event_time_key=arrival_key,
        scheduler_event_index=1,
        source_lineage_id="center-before-refinement",
        target_lineage_id="neighbor-1",
    )
    compact = compact_lgrc9v3_packet_ledger(departure.ledger)
    expansion_events = model.apply_hybrid_sparks()
    expansion = first_event(expansion_events, kind="hybrid_mechanical_expansion")

    transport = transport_lgrc9v3_packets_through_refinement(
        departure.ledger,
        expansion,
        post_topology_signature=topology_signature(state),
        pending_flux_ledger=compact,
    )
    artifact = transport.to_artifact()
    record = artifact["packet_transport_records"][0]
    queued = artifact["transported_ledger"]["event_queue_records"][0]

    print("LGRC9V3 refinement packet transport")
    print_json(
        "expansion",
        {
            "kind": expansion.kind,
            "expansion_id": expansion.payload.get("expansion_id"),
            "source_candidate_event_id": expansion.payload.get(
                "source_candidate_event_id"
            ),
            "sink_node_id": expansion.payload.get("sink_node_id"),
            "module_node_ids": expansion.payload.get("module_node_ids"),
        },
    )
    print_json(
        "transport",
        {
            "artifact_kind": artifact["artifact_kind"],
            "topology_event_kind": artifact["topology_event_kind"],
            "evidence_class": artifact["evidence_class"],
            "source_packet_ids": artifact["source_packet_ids"],
            "transported_packet_ids": artifact["transported_packet_ids"],
            "source_pending_flux_entry_ids": artifact[
                "source_pending_flux_entry_ids"
            ],
            "amount_total": artifact["amount_total"],
            "budget_before": artifact["budget_before"],
            "budget_after": artifact["budget_after"],
            "budget_error": artifact["budget_error"],
            "identity_acceptance_emitted": artifact[
                "identity_acceptance_emitted"
            ],
            "packet_transport_identity_transfer": artifact[
                "packet_transport_identity_transfer"
            ],
        },
    )
    print_json(
        "transport_record",
        {
            "source_node_id_before": record["source_node_id_before"],
            "source_node_id_after": record["source_node_id_after"],
            "target_node_id_before": record["target_node_id_before"],
            "target_node_id_after": record["target_node_id_after"],
            "source_lineage_id_before": record["source_lineage_id_before"],
            "source_lineage_id_after": record["source_lineage_id_after"],
            "old_parent_port": record["old_parent_port"],
            "new_endpoint_port": record["new_endpoint_port"],
            "old_parent_column": record["old_parent_column"],
            "new_endpoint_column": record["new_endpoint_column"],
        },
    )
    print_json(
        "queued_arrival_after_transport",
        {
            "event_kind": queued["event_kind"],
            "packet_id": queued["packet_id"],
            "source_node_id": queued["source_node_id"],
            "target_node_id": queued["target_node_id"],
            "event_time_key": queued["event_time_key"],
        },
    )

    print(
        "\nInterpretation: this is LGRC-3 packet transport through one "
        "GRC9V3 mechanical expansion. It preserves packet budget and lineage "
        "evidence, but it is still helper-based. It is not full LGRC9V3 event "
        "loop parity, not causally scheduled spark evaluation, not collapse/"
        "reabsorption, and not identity acceptance."
    )


if __name__ == "__main__":
    main()

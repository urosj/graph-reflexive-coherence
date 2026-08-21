"""Declare two allowed pathways and let consumer code choose one branch."""

from __future__ import annotations

import argparse
from pathlib import Path

from _shared import (
    accepted_authority,
    artifact_paths,
    print_summary,
    two_node_runtime,
)

from pygrc.causal_pathways import PathwayBindingSession


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--choice", choices=("packet", "snapshot"), default="snapshot")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    model = two_node_runtime()
    session = PathwayBindingSession(accepted_authority())
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    restoration = session.bind_pathway(
        "pygrc.restoration_replay_identity",
        stage_ids=("snapshot_serialization",),
    )
    schedule = packet.symbol("packet_schedule", instance=model)
    snapshot = restoration.symbol("snapshot_serialization", instance=model)
    alternatives = session.declare_alternatives(
        alternative_set_id="example.packet_or_snapshot",
        pathway_ids=(packet.pathway_id, restoration.pathway_id),
        selection_authority="--choice consumer argument",
    )

    lock = session.freeze_lock()
    with alternatives.selection_scope():
        if args.choice == "packet":
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
        else:
            snapshot()
    receipt = session.build_receipt()
    record = receipt.to_record()
    actual = record["allowed_pathway_alternatives_actual_use"][0]

    print_summary(
        {
            "example": "dynamic_choice",
            "consumer_choice": args.choice,
            "selected_pathway_ids": actual["selected_pathway_ids"],
            "declared_but_unused_pathway_binding_ids": record[
                "declared_but_unused"
            ]["pathway_binding_ids"],
            "selection_performed_by": actual["selection_scopes"][0][
                "selection_performed_by"
            ],
            "claim_scope": record["claim_scope"],
            "claim_qualified": record["claim_qualified"],
            "written_artifacts": artifact_paths(
                lock=lock,
                receipt=receipt,
                output_dir=args.output_dir,
                stem="dynamic-choice",
            ),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

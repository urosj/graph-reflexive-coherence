"""Bind and execute one admitted packet-transport pathway."""

from __future__ import annotations

import argparse
from pathlib import Path

from _shared import (
    accepted_authority,
    artifact_paths,
    execute_packet_lifecycle,
    print_summary,
    two_node_runtime,
)

from pygrc.causal_pathways import PathwayBindingSession


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    model = two_node_runtime()
    session = PathwayBindingSession(accepted_authority())
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule", "source_debit", "target_credit"),
    )
    schedule = packet.symbol("packet_schedule", instance=model)
    debit = packet.symbol("source_debit")
    credit = packet.symbol("target_credit")

    lock = session.freeze_lock()
    execute_packet_lifecycle(
        model=model,
        schedule=schedule,
        debit=debit,
        credit=credit,
    )
    receipt = session.build_receipt()
    record = receipt.to_record()

    print_summary(
        {
            "example": "admitted_pathway",
            "lock_digest": lock.digest,
            "receipt_digest": receipt.digest,
            "actual_pathway_ids": [
                item["pathway_id"] for item in record["actual_bound_pathways_used"]
            ],
            "claim_scope": record["claim_scope"],
            "claim_qualified": record["claim_qualified"],
            "overall_claim_status": record["claim_envelope"][
                "overall_claim_status"
            ],
            "written_artifacts": artifact_paths(
                lock=lock,
                receipt=receipt,
                output_dir=args.output_dir,
                stem="admitted-pathway",
            ),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

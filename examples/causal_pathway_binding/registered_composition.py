"""Bind and execute registered composition CMP-02."""

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
    composition = session.bind_composition("CMP-02")
    packet = composition.pathway("lgrc9v3.explicit_packet_transport")
    schedule = packet.symbol("packet_schedule", instance=model)
    debit = packet.symbol("source_debit")
    credit = packet.symbol("target_credit")

    lock = session.freeze_lock()
    with composition.evidence_scope():
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
            "example": "registered_composition",
            "lock_digest": lock.digest,
            "receipt_digest": receipt.digest,
            "registered_composition_ids": [
                item["composition_id"]
                for item in record["registered_compositions_exercised"]
            ],
            "composition_edge_count": len(record["pathway_use_graph"]["edges"]),
            "claim_scope": record["claim_scope"],
            "claim_qualified": record["claim_qualified"],
            "written_artifacts": artifact_paths(
                lock=lock,
                receipt=receipt,
                output_dir=args.output_dir,
                stem="registered-composition",
            ),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

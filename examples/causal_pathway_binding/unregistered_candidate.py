"""Execute a conservative, explicitly unregistered composition candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from _shared import (
    ROOT,
    accepted_authority,
    artifact_paths,
    print_summary,
    two_node_runtime,
)

from pygrc.causal_pathways import PathwayBindingSession, sha256_file

CANDIDATE_EVIDENCE_PATH = Path(
    "examples/causal_pathway_binding/candidate_mechanism_evidence.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
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
    candidate = session.declare_candidate(
        candidate_id="example.packet_to_snapshot_relation",
        candidate_kind="composition",
        purpose="Demonstrate a distinct relation that is not admitted.",
        owner="example_consumer",
        consumed_pathway_ids=(packet.pathway_id, restoration.pathway_id),
        proposed_source_pathway_id=packet.pathway_id,
        proposed_target_pathway_id=restoration.pathway_id,
        proposed_relation="example-only post-packet snapshot relation",
        evidence_owner="example_consumer",
        mechanism_evidence={
            "evidence_kind": "executable_candidate_mechanism",
            "mechanism_id": "example.packet_schedule_then_snapshot",
            "path": CANDIDATE_EVIDENCE_PATH.as_posix(),
            "sha256": sha256_file(ROOT / CANDIDATE_EVIDENCE_PATH),
        },
        blocked_claims=("admitted relation", "native promotion"),
    )
    crossing = candidate.mechanism()

    lock = session.freeze_lock()
    with candidate.evidence_scope():
        schedule_result = schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )
        crossing(schedule_result)
        snapshot()
    session.record_candidate_use(candidate.candidate_id)
    receipt = session.build_receipt()
    record = receipt.to_record()
    candidate_use = record["candidate_relations_exercised"][0]

    print_summary(
        {
            "example": "unregistered_candidate",
            "candidate_id": candidate_use["candidate_id"],
            "claim_ceiling": candidate_use["claim_ceiling"],
            "promotion_status": candidate_use["promotion_status"],
            "proposed_relation_claim_status": candidate_use[
                "proposed_relation_claim_status"
            ],
            "overall_claim_status": record["claim_envelope"][
                "overall_claim_status"
            ],
            "claim_scope": record["claim_scope"],
            "written_artifacts": artifact_paths(
                lock=lock,
                receipt=receipt,
                output_dir=args.output_dir,
                stem="unregistered-candidate",
            ),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

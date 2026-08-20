"""Contrast valid direct execution with one evidence-bearing bound call."""

from __future__ import annotations

import argparse
from pathlib import Path

from _shared import (
    accepted_authority,
    artifact_paths,
    print_summary,
    two_node_runtime,
)

from pygrc.causal_pathways import (
    PathwayBindingSession,
    unbound_execution_classification,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    direct_model = two_node_runtime()
    direct_model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
    )
    direct = unbound_execution_classification()

    bound_model = two_node_runtime()
    session = PathwayBindingSession(accepted_authority())
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    schedule = packet.symbol("packet_schedule", instance=bound_model)
    lock = session.freeze_lock()
    schedule(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
    )
    receipt = session.build_receipt()
    record = receipt.to_record()

    print_summary(
        {
            "example": "direct_unbound",
            "direct_execution": dict(direct),
            "bound_execution": {
                "claim_scope": record["claim_scope"],
                "claim_qualified": record["claim_qualified"],
                "recorded_invocation_count": len(
                    record["actual_stage_symbol_invocations"]
                ),
                "whole_run_causal_closure_claimed": record[
                    "whole_run_causal_closure_claimed"
                ],
            },
            "warning": (
                "The receipt certifies only represented bound invocations; "
                "it does not observe or qualify the direct call."
            ),
            "written_artifacts": artifact_paths(
                lock=lock,
                receipt=receipt,
                output_dir=args.output_dir,
                stem="direct-unbound",
            ),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Read-only A_RG2b research queries and five-realization Candidate-A closure."""
import argparse
import json
import sys
from pathlib import Path

SIDE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import atc_rgatc as rg
from grcv4_explorer.paths import repository_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("audit", "discover", "claim", "debt", "summary"))
    parser.add_argument("identifier", nargs="?")
    args = parser.parse_args()
    if (args.operation in ("claim", "debt")) != (args.identifier is not None):
        parser.error("only claim/debt requires an identifier")
    root = repository_root()
    if args.operation == "discover":
        value = rg.observe_sources(root, rg.pinned_admission(SIDE))
        print(json.dumps(value, indent=2))
        return 0 if value["state"] == "current_bundle_exact" else 2
    context = rg.load_current_forensic_context(root, SIDE)
    if args.operation == "audit":
        ledger = context.documents_by_record[rg.RECORD_ID].data
        summary = rg.candidate_a_closure(context)
        value = dict(status="passed", accepted_research_claims=len(ledger["claims"]),
            profile_scope=["A_RG2b"], debt_statuses=ledger["classifications"],
            graph_digest=context.graph_digest, source_bundle_digest=context.source_bundle_digest,
            authority_extension_digest=context.authority_extension_digest,
            closed_candidate_a_research_programs=[r["row_id"] for r in summary["rows"]],
            native_authority=False, ATC2_closed=False, ATC3_closed=False)
    elif args.operation == "summary":
        value = rg.candidate_a_closure(context)
    else:
        value = (rg.reconstruction_path if args.operation == "claim" else rg.debt_lifecycle)(
            context, args.identifier)
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

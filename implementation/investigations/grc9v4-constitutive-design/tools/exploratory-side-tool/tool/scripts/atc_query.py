#!/usr/bin/env python3
"""Read-only ATC research discovery, audit and typed claim/debt queries."""
import argparse
import json
import sys
from pathlib import Path

SIDE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer.atc import (ADMISSION, load_current_forensic_context,
                               observe_sources, reconstruction_path, debt_lifecycle)
from grcv4_explorer.canonical import load_json_object
from grcv4_explorer.paths import repository_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("audit", "discover", "claim", "debt"))
    parser.add_argument("identifier", nargs="?")
    args = parser.parse_args()
    root = repository_root()
    if args.operation == "discover":
        # Loading first ensures the observation's roster is itself pinned.
        # On drift still show the failure-closed observation, not stale traces.
        from grcv4_explorer.atc import ADMISSION_DIGEST
        from grcv4_explorer.canonical import record_digest
        a = load_json_object(SIDE / "records" / ADMISSION)
        if a.get("record_digest") != record_digest(a, "record_digest") or a["record_digest"] != ADMISSION_DIGEST:
            raise ValueError("ATC discovery roster is not pinned")
        result = observe_sources(root, a)
        print(json.dumps(result, indent=2))
        return 0 if result["state"] == "current_bundle_exact" else 2
    context = load_current_forensic_context(root, SIDE)
    if args.operation == "audit":
        ledger = context.documents_by_record["GRCV4-ATC-AOS-LEDGER-v1"].data
        result = dict(status="passed", accepted_research_claims=len(ledger["claims"]),
                      origin_proposals=len(ledger["origin_claims"]), debt_statuses=ledger["classifications"],
                      graph_digest=context.graph_digest, source_bundle_digest=context.source_bundle_digest,
                      authority_extension_digest=context.authority_extension_digest,
                      ATC2_closed=False, native_authority=False)
    else:
        if args.identifier is None:
            parser.error("claim/debt requires an identifier")
        result = (reconstruction_path if args.operation == "claim" else debt_lifecycle)(context, args.identifier)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

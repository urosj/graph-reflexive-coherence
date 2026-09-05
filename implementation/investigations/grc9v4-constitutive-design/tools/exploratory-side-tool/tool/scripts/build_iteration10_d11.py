#!/usr/bin/env python3
"""Build the accepted append-only ET-C10 D11 forensic extension."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, record_digest  # noqa: E402
from grcv4_explorer.forensic import load_forensic_context  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor import (  # noqa: E402
    D11_FORENSIC_ADMISSION,
    D11_GRAPH_SNAPSHOT,
    D11_SOURCE_MANIFEST,
    build_d11_graph,
    build_d11_source_bundle,
    validate_d11_graph,
)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def main() -> int:
    repo_root = repository_root()
    historical = load_forensic_context(repo_root, SIDE_TOOL_ROOT)
    manifest, documents = build_d11_source_bundle(repo_root, SIDE_TOOL_ROOT)
    graph = build_d11_graph(historical, manifest, documents)
    validate_d11_graph(graph, historical.graph)
    records = SIDE_TOOL_ROOT / "records"
    admission: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C10_D11_forensic_admission_v1",
        "status": "accepted",
        "gate_id": "ET-C10-D11",
        "historical_ET_C2_record_digest": historical.et_c2_record_digest,
        "historical_ET_C2_graph_digest": historical.graph_digest,
        "source_contract_digest": manifest["source_contract_digest"],
        "source_bundle_digest": manifest["source_bundle_digest"],
        "graph_digest": graph["graph_digest"],
        "population": graph["population"],
        "successor_population": graph["successor_population"],
        "authority_boundary": {
            "D11_C_status": "accepted_bounded",
            "D11_G9_status": "accepted_bounded",
            "D10_claims_or_debts_reclassified": 0,
            "historical_ET_C0_through_ET_C9_artifacts_rewritten": False,
            "paper_propagation_verified": False,
            "specification_propagation_verified": False,
            "implementation_conformance_verified": False,
            "GRC9_or_GRC9V3_change_authorized": False,
        },
        "query_surface": {
            "loader": "grcv4_explorer.successor.load_successor_forensic_context",
            "historical_loader_retained": "grcv4_explorer.forensic.load_forensic_context",
            "supported_D11_claim_ids": ["D11-C-CL-O-001", "D11-G9-CL-N-001"],
            "supported_D11_debt_ids": [
                "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY",
                "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION",
            ],
            "successor_scenario_ids": ["S1", "S2", "S3", "S4", "S5", "S6"],
        },
        "record_digest": None,
    }
    admission["record_digest"] = record_digest(admission, "record_digest")
    write_json(records / D11_SOURCE_MANIFEST, manifest)
    write_json(records / D11_GRAPH_SNAPSHOT, graph)
    write_json(records / D11_FORENSIC_ADMISSION, admission)
    print(
        "ET_C10_D11_BUILD_PASS "
        f"sources={manifest['D11_record_count']} "
        f"claims={graph['population']['current_claim']} "
        f"objects={graph['population']['normative_object']} "
        f"contracts={graph['population']['equation_contract']} "
        f"graph_digest={graph['graph_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

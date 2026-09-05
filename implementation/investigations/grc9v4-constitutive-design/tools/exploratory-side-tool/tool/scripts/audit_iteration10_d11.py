#!/usr/bin/env python3
"""Audit the accepted ET-C10 D11 forensic extension."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object  # noqa: E402
from grcv4_explorer.forensic import (  # noqa: E402
    candidate_career,
    contract_provenance,
    debt_lifecycle,
    load_forensic_context,
    object_dependents,
    reconstruction_path,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor import (  # noqa: E402
    D11_FORENSIC_ADMISSION,
    D11_GRAPH_SNAPSHOT,
    D11_SOURCE_MANIFEST,
    build_d11_graph,
    build_d11_source_bundle,
    load_successor_forensic_context,
    validate_d11_graph,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def trace_check(
    context: Any,
    operation: Callable[[Any, str], dict[str, Any]],
    identifier: str,
) -> dict[str, Any]:
    trace = operation(context, identifier)
    require(trace["row_count"] == len(trace["rows"]), f"trace rows: {identifier}")
    require(bool(trace.get("trace_digest")), f"trace digest: {identifier}")
    require(
        trace.get("authority_extension_digest") == context.authority_extension_digest,
        f"authority extension digest: {identifier}",
    )
    require(
        all(row.get("source_ref") and row.get("edge_refs") for row in trace["rows"]),
        f"source/edge evidence: {identifier}",
    )
    return trace


def main() -> int:
    repo_root = repository_root()
    records = SIDE_TOOL_ROOT / "records"
    historical = load_forensic_context(repo_root, SIDE_TOOL_ROOT)
    manifest, documents = build_d11_source_bundle(repo_root, SIDE_TOOL_ROOT)
    graph = build_d11_graph(historical, manifest, documents)
    validate_d11_graph(graph, historical.graph)
    require(
        canonical_bytes(manifest)
        == canonical_bytes(load_json_object(records / D11_SOURCE_MANIFEST)),
        "D11 source manifest does not rebuild byte-exactly",
    )
    require(
        canonical_bytes(graph)
        == canonical_bytes(load_json_object(records / D11_GRAPH_SNAPSHOT)),
        "D11 graph does not rebuild byte-exactly",
    )
    context = load_successor_forensic_context(repo_root, SIDE_TOOL_ROOT)
    admission = load_json_object(records / D11_FORENSIC_ADMISSION)
    require(
        admission["query_surface"]["successor_scenario_ids"]
        == ["S1", "S2", "S3", "S4", "S5", "S6"],
        "D11 successor scenario roster",
    )
    plan = (SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolImplementationPlan.md").read_text(
        encoding="utf-8"
    )
    checklist = (
        SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolImplementationChecklist.md"
    ).read_text(encoding="utf-8")
    scenarios = (
        SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolD11SuccessorScenarios.md"
    ).read_text(encoding="utf-8")
    require("Iterations 0-10 accepted" in plan, "implementation plan status")
    require("Iterations 0-10 accepted" in checklist, "checklist status")
    require(
        all(f"## S{index}." in scenarios for index in range(1, 7)),
        "successor scenario definitions",
    )
    require("current governed scenarios              41" in scenarios, "scenario total")
    counts = Counter(row["kind"] for row in context.graph["nodes"])
    expected = {
        "current_claim": 41,
        "historical_claim": 29,
        "debt_transformation": 31,
        "verification_obligation": 18,
        "normative_object": 80,
        "equation_contract": 183,
    }
    require(all(counts[key] == value for key, value in expected.items()), "counts")
    require(
        context.graph["successor_population"]
        == {
            "current_claim": 2,
            "debt_transformation": 2,
            "equation_contract": 31,
            "investigation_candidate": 12,
            "normative_object": 13,
            "pending_forward_verification_obligation_total": 17,
            "selected_profile": 2,
            "verification_obligation": 7,
        },
        "D11 successor population",
    )

    for claim_id in ("D11-C-CL-O-001", "D11-G9-CL-N-001"):
        trace = trace_check(context, reconstruction_path, claim_id)
        nodes = trace["rows"][0]["payload"]["nodes"]
        require(
            any(row["kind"] == "debt_transformation" for row in nodes),
            f"debt reconstruction: {claim_id}",
        )
        require(
            not any(row["kind"] == "verification_obligation" for row in nodes),
            f"forward obligation leaked into reconstruction: {claim_id}",
        )

    contract_expectations = {
        "D11-C-EC-C-J0-CURRENT": "accepted_bounded_D11_C_successor",
        "D11-G9-EC-EXACT-OLD-PORT-MAP": "accepted_bounded_GRC9V4_successor",
    }
    for contract_id, support in contract_expectations.items():
        trace = trace_check(context, contract_provenance, contract_id)
        disposition = trace["rows"][0]["payload"]["support_disposition"]
        require(support in disposition, f"contract support semantics: {contract_id}")

    for object_id in (
        "C-BASELINE-CURRENT",
        "GRC9-EXPANSION-RECURSIVE-SAME-PORT-TREE",
    ):
        trace = trace_check(context, object_dependents, object_id)
        require(
            bool(trace["rows"][0]["payload"]["direct_contract_nodes"]),
            f"object has no contracts: {object_id}",
        )

    debt_rows = {
        "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY": 5,
        "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION": 6,
    }
    for debt_id, row_count in debt_rows.items():
        trace = trace_check(context, debt_lifecycle, debt_id)
        require(trace["row_count"] == row_count, f"debt lifecycle rows: {debt_id}")
        require(
            any(
                row["classification"].startswith("resolved_bounded")
                for row in trace["rows"]
            ),
            f"debt resolution missing: {debt_id}",
        )

    for candidate_id in ("D11-C-T3a", "D11-G9-P4a"):
        trace = trace_check(context, candidate_career, candidate_id)
        require(
            trace["rows"][0]["classification"] == "selected_accepted_bounded",
            f"selected candidate disposition: {candidate_id}",
        )

    try:
        reconstruction_path(historical, "D11-C-CL-O-001")
    except KeyError:
        pass
    else:
        raise RuntimeError("historical ET-C2 loader silently admitted a D11 claim")
    try:
        reconstruction_path(context, "D10_2_CL_N_001")
    except KeyError:
        pass
    else:
        raise RuntimeError("record-local D10.2 reference became a graph claim")

    print(
        "ET_C10_D11_AUDIT_PASS "
        f"source_bundle_digest={context.source_bundle_digest} "
        f"graph_digest={context.graph_digest} "
        "claims=41 historical_claims=29 debts=31 obligations=18 "
        "pending_forward_obligations=17 objects=80 contracts=183 "
        "historical_graph_rewritten=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

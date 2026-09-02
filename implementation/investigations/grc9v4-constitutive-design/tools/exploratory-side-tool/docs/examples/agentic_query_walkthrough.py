#!/usr/bin/env python3
"""Run source-bound examples for every admitted forensic query operation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
SIDE_TOOL_ROOT = SCRIPT.parents[2]
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.forensic import (  # noqa: E402
    ForensicContext,
    candidate_career,
    contract_provenance,
    debt_lifecycle,
    gate_act,
    gate_contribution,
    load_forensic_context,
    negative_claims,
    object_dependents,
    pruned_choices_at,
    reconstruction_path,
    write_trace,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


Query = Callable[[ForensicContext], dict[str, Any]]


QUERIES: dict[str, tuple[str, Query]] = {
    "gate-act": (
        "gate-act.json",
        lambda context: gate_act(context, "GRC9V4-CD-D7V2-v1"),
    ),
    "gate-contribution": (
        "gate-contribution.json",
        lambda context: gate_contribution(context, "GRC9V4-CD-D7V2-v1"),
    ),
    "debt-lifecycle": (
        "debt-lifecycle.json",
        lambda context: debt_lifecycle(
            context,
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
        ),
    ),
    "reconstruction-path": (
        "reconstruction-path.json",
        lambda context: reconstruction_path(context, "D10-CL-N-001"),
    ),
    "candidate-career": (
        "candidate-career.json",
        lambda context: candidate_career(
            context,
            "V4-B-independent-derived-carrier",
        ),
    ),
    "pruned-choices": (
        "pruned-choices.json",
        lambda context: pruned_choices_at(context, "GRC9V4-CD-D1-v1"),
    ),
    "negative-claims": (
        "negative-claims.json",
        negative_claims,
    ),
    "object-dependents": (
        "object-dependents.json",
        lambda context: object_dependents(context, "CORE-C-AUTHORITY"),
    ),
    "contract-provenance": (
        "contract-provenance.json",
        lambda context: contract_provenance(
            context,
            "D10.2-EC-PARENT-CORE-C-AUTHORITY",
        ),
    ),
}


def validate_trace(name: str, trace: dict[str, Any]) -> None:
    if trace.get("output_class") != "forensic_evidence_trace":
        raise RuntimeError(f"{name}: unexpected output class")
    if trace.get("row_count") != len(trace.get("rows", [])):
        raise RuntimeError(f"{name}: row count mismatch")
    if not isinstance(trace.get("trace_digest"), str):
        raise RuntimeError(f"{name}: trace digest missing")
    for index, row in enumerate(trace["rows"]):
        source = row.get("source_ref", {})
        edges = row.get("edge_refs", [])
        if not source.get("record_id") or not source.get("source_json_pointer"):
            raise RuntimeError(f"{name}:{index}: source reference missing")
        if not edges:
            raise RuntimeError(f"{name}:{index}: edge witnesses missing")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    parser = argparse.ArgumentParser()
    parser.add_argument("query", choices=["all", *sorted(QUERIES)])
    args = parser.parse_args()

    context = load_forensic_context(repo_root, SIDE_TOOL_ROOT)
    selected = sorted(QUERIES) if args.query == "all" else [args.query]
    output_dir = TOOL_ROOT / "generated/agent-guide"
    for name in selected:
        filename, operation = QUERIES[name]
        trace = operation(context)
        validate_trace(name, trace)
        destination = output_dir / filename
        write_trace(destination, trace)
        classifications = sorted({row["classification"] for row in trace["rows"]})
        print(
            f"{name}: rows={trace['row_count']} "
            f"classifications={','.join(classifications)} "
            f"digest={trace['trace_digest']} output={destination.relative_to(TOOL_ROOT)}"
        )
    print(f"AGENTIC_QUERY_WALKTHROUGH_PASS queries={len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

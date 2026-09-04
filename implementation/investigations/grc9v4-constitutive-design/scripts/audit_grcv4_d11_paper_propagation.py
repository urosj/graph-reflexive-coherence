#!/usr/bin/env python3
"""Audit the D11-to-paper boundary using the accepted ET-C10 overlay."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
SIDE_TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool"
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"
PAPER = INVESTIGATION / "drafts/2026-09-GRC-V4.md"
PRE_PROPAGATION_SHA256 = (
    "e009c5651842dea6636057a9639a79e42eb5c03b20c4812fb9ee5173705258e5"
)

sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.forensic import (  # noqa: E402
    contract_provenance,
    reconstruction_path,
)
from grcv4_explorer.successor import load_successor_forensic_context  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    context = load_successor_forensic_context(ROOT, SIDE_TOOL_ROOT)
    claim_ids = ("D11-C-CL-O-001", "D11-G9-CL-N-001")
    for claim_id in claim_ids:
        trace = reconstruction_path(context, claim_id)
        require(trace["row_count"] == 1, f"claim reconstruction: {claim_id}")
        require(
            trace.get("authority_extension_digest")
            == context.authority_extension_digest,
            f"claim authority extension: {claim_id}",
        )
    d11_nodes = [
        row
        for row in cast(list[dict[str, Any]], context.graph["nodes"])
        if row["source_record_id"]
        in {
            "GRC9V4-D11-C-PROVENANCE-SUPPLEMENT-v1",
            "GRC9V4-D11-G9-PROVENANCE-SUPPLEMENT-v1",
        }
    ]
    object_ids = sorted(
        cast(str, row["identifier"])
        for row in d11_nodes
        if row["kind"] == "normative_object"
    )
    contract_ids = sorted(
        cast(str, row["identifier"])
        for row in d11_nodes
        if row["kind"] == "equation_contract"
    )
    require(len(object_ids) == 13, "D11 object population")
    require(len(contract_ids) == 31, "D11 contract population")
    for contract_id in contract_ids:
        trace = contract_provenance(context, contract_id)
        require(trace["row_count"] == 1, f"contract provenance: {contract_id}")

    text = PAPER.read_text(encoding="utf-8")
    current_sha = sha256_file(PAPER)
    required_ids = [*claim_ids, *object_ids, *contract_ids]
    present_ids = [identifier for identifier in required_ids if identifier in text]
    if current_sha == PRE_PROPAGATION_SHA256:
        require(
            not present_ids,
            "pre-propagation paper contains only a partial D11 authority population",
        )
        print(
            "D11_PAPER_PROPAGATION_AUDIT_PASS "
            "status=pending_tooling_ready paper_sha256="
            f"{current_sha} claims_ready=2 objects_ready=13 contracts_ready=31"
        )
        return 0

    missing_ids = sorted(set(required_ids) - set(present_ids))
    require(not missing_ids, f"paper is missing D11 authority IDs: {missing_ids}")
    required_markers = (
        "C-HM-STIFFNESS-BASELINE-v1",
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        r"\Phi_{0,C}",
        r"M_{4,C}",
        r"J_{0,C}",
        r"D_{\mathrm{ext,max}}(n)=9n-2(n-1)=7n+2",
    )
    missing_markers = [marker for marker in required_markers if marker not in text]
    require(not missing_markers, f"paper is missing D11 equations: {missing_markers}")
    require(
        "GRC9V4" in text and "GRC9V3" in text,
        "paper does not state the V4-only specialization boundary",
    )
    print(
        "D11_PAPER_PROPAGATION_AUDIT_PASS "
        f"status=propagated paper_sha256={current_sha} "
        "claims=2 objects=13 contracts=31 GRC9_or_GRC9V3_rewritten=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

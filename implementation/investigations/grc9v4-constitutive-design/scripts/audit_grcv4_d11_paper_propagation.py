#!/usr/bin/env python3
"""Audit the D11-to-paper boundary using the accepted ET-C10 overlay."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
SIDE_TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool"
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"
PAPER = INVESTIGATION / "drafts/2026-09-GRC-V4.md"
PROPOSAL = INVESTIGATION / "drafts/GRCV4-proposal.md"
BOUNDARY = INVESTIGATION / "specification/PostD10SpecificationBoundary.json"
PRE_PROPAGATION_SHA256 = (
    "e009c5651842dea6636057a9639a79e42eb5c03b20c4812fb9ee5173705258e5"
)
PRE_PROPOSAL_PROPAGATION_SHA256 = (
    "379a5668065a5bd4ffe9bc8375629b53ec210adf716a7a081dbf8f21b38fc920"
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

    required_ids = [*claim_ids, *object_ids, *contract_ids]
    required_markers = (
        "C-HM-STIFFNESS-BASELINE-v1",
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        r"\Phi_{0,C}",
        r"M_{4,C}",
        r"J_{0,C}",
        r"D_{\mathrm{ext,max}}(n)=9n-2(n-1)=7n+2",
    )
    proposal_correction_markers = (
        "D11-integrated proposal review candidate",
        "D11-C-T3a",
        "82e8008e8edade39db7b5327a31a807031b712dcc86b3fe3e8c0977bda51e797",
        "D11-G9-P4a",
        "a0813ceead2c992ec197790abd8a0ceea167ae2d952f853cf48f1db4d8001615",
        r"d_0:=B^\top",
        r"E_{\mathrm{stable}}",
        r"H_{1,\mathrm{form,pre}}",
        r"\mathsf D_C",
        r"W_{C,\mathrm{tr},ij}",
        "enabled GRC-v4 Candidate C law",
        "module_chirality_required",
        "module_growth_phase_required",
        "reject_noncanonical_inactive_growth_phase",
        "another admitted full-target edge-history policy",
        "witness_d11_c_hm_stiffness_baseline.py",
        "6.206335383118183e-17",
        "witness_d11_g9_canonical_expansion.py",
        "23,256",
        r"P_J=[I\;0]",
        "broader conditional analysis envelope",
        "Historical D10.2 extraction verdict for Sections 8–10",
        "Historical D10.2 extraction verdict for Appendix A",
    )
    forbidden_proposal_markers = (
        "selected-to-physical one-form identification",
        "Selected/physical one-form identification",
        r"\partial_{\mathrm{ref}}",
        r"K_4\to H_4\to h_4",
        r"K_4\rightarrow H_4\rightarrow h_4",
        "exact old-edge lineage plus an admitted positive target\n"
        "  initializer or explicit full-target history loss",
    )

    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    phase = boundary["active_phase"]
    proposal_text = PROPOSAL.read_text(encoding="utf-8")
    proposal_sha = sha256_file(PROPOSAL)
    paper_text = PAPER.read_text(encoding="utf-8")
    paper_sha = sha256_file(PAPER)

    if phase == "proposal_propagation":
        require(
            proposal_sha != PRE_PROPOSAL_PROPAGATION_SHA256,
            "proposal-propagation phase still has the pre-D11 proposal",
        )
        missing_ids = sorted(
            identifier for identifier in required_ids if identifier not in proposal_text
        )
        require(not missing_ids, f"proposal is missing D11 authority IDs: {missing_ids}")
        missing_markers = [
            marker for marker in required_markers if marker not in proposal_text
        ]
        require(
            not missing_markers,
            f"proposal is missing D11 equations: {missing_markers}",
        )
        missing_corrections = [
            marker
            for marker in proposal_correction_markers
            if marker not in proposal_text
        ]
        require(
            not missing_corrections,
            f"proposal is missing D11 review corrections: {missing_corrections}",
        )
        stale_markers = [
            marker for marker in forbidden_proposal_markers if marker in proposal_text
        ]
        require(
            not stale_markers,
            f"proposal retains stale D11 review wording: {stale_markers}",
        )
        require(
            proposal_text.count("another admitted full-target edge-history policy")
            == 8,
            "Candidate A event-policy alternatives are not synchronized",
        )
        require(
            proposal_text.count(
                "the event may not switch policies after observing target admission"
            )
            == 6,
            "Candidate A policy-selection boundary is not synchronized",
        )
        require(
            "D11-integrated proposal review candidate" in proposal_text,
            "proposal does not declare review-candidate status",
        )
        require(
            paper_sha == PRE_PROPAGATION_SHA256,
            "paper changed before proposal review acceptance",
        )
        paper_d11_ids = [
            identifier for identifier in required_ids if identifier in paper_text
        ]
        require(
            not paper_d11_ids,
            "paper contains partial D11 authority before proposal acceptance",
        )
        print(
            "D11_PAPER_PROPAGATION_AUDIT_PASS "
            f"status=proposal_review_candidate proposal_sha256={proposal_sha} "
            f"paper_sha256={paper_sha} claims=2 objects=13 contracts=31 "
            "paper_unchanged=true specifications_unchanged=true"
        )
        return 0

    text = paper_text
    current_sha = paper_sha
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

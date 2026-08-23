"""Build the separately reviewable GRV8 Stage 2 closeout candidate."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from artifact_io import (
    EXPERIMENT_ROOT,
    artifact_envelope,
    assert_payload_digest,
    file_manifest,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    tracked_files,
    write_json,
)
from gate_receipts import (
    finalize_receipt,
    validate_acceptance_anchor,
    validate_receipt,
)


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/build_grv8_closeout_candidate.py"
)
POLICY_PATH = EXPERIMENT_ROOT / "configs/grv8_closeout_policy.json"
BUNDLE_PATH = EXPERIMENT_ROOT / "outputs/evidence_bundle_manifest.json"
SUCCESSOR_PATH = EXPERIMENT_ROOT / (
    "implementation/"
    "GRC9V3ContinuationReadBackVerificationSpecification_EvidenceGrounded_v1.md"
)
HANDOFF_PATH = EXPERIMENT_ROOT / "outputs/continuation_readback_next_route_handoff.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports/b1_grv8_stage2_closeout_candidate.md"
RECEIPT_PATH = EXPERIMENT_ROOT / "outputs/gates/grv8_closeout_result_receipt.json"
CLOSEOUT_ANCHOR_PATH = EXPERIMENT_ROOT / "outputs/gates/grv8_closeout_acceptance_anchor.json"
PREDECESSOR_SPEC_PATH = EXPERIMENT_ROOT / (
    "implementation/GRC9V3ContinuationReadBackVerificationSpecification.md"
)


def envelope(path: Path) -> dict[str, Any]:
    value = read_json(path)
    assert_payload_digest(value)
    return value


def accepted_grv8() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv8_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv8_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if anchor["acceptance_status"] != "accepted":
        raise ValueError("GRV8 classification is not scientifically accepted")
    if anchor["receipt_payload_sha256"] != receipt["receipt_payload_sha256"]:
        raise ValueError("GRV8 acceptance anchor does not bind the current receipt")
    git("merge-base", "--is-ancestor", anchor["result_revision"], "HEAD")
    for relative, digest in receipt["output_artifact_digests"].items():
        if sha256_file(EXPERIMENT_ROOT / relative) != digest:
            raise ValueError(f"accepted GRV8 artifact changed: {relative}")
    return receipt, anchor


def collect_evidence_bundle(policy: dict[str, Any]) -> dict[str, Any]:
    accepted_gate_results: list[dict[str, Any]] = []
    anchor_digests: list[dict[str, Any]] = []
    artifact_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    replaced: list[dict[str, Any]] = []

    for index in range(9):
        gate_id = f"GRV{index}"
        receipt_path = EXPERIMENT_ROOT / f"outputs/gates/grv{index}_result_receipt.json"
        anchor_path = EXPERIMENT_ROOT / f"outputs/gates/grv{index}_acceptance_anchor.json"
        receipt = read_json(receipt_path)
        anchor = read_json(anchor_path)
        validate_receipt(receipt)
        validate_acceptance_anchor(anchor)
        if anchor["acceptance_status"] != "accepted":
            raise ValueError(f"{gate_id} is not accepted")
        if anchor["receipt_payload_sha256"] != receipt["receipt_payload_sha256"]:
            raise ValueError(f"{gate_id} anchor/receipt mismatch")
        accepted_gate_results.append(
            {
                "gate_id": gate_id,
                "result_revision": anchor["result_revision"],
                "result_receipt_path": repo_relative(receipt_path),
                "result_receipt_payload_sha256": receipt["receipt_payload_sha256"],
                "acceptance_anchor_path": repo_relative(anchor_path),
                "acceptance_anchor_sha256": sha256_file(anchor_path),
            }
        )
        anchor_digests.append(
            {
                "gate_id": gate_id,
                "path": repo_relative(anchor_path),
                "sha256": sha256_file(anchor_path),
                "semantic_sha256": semantic_digest(anchor),
            }
        )
        artifact_sources[(repo_relative(receipt_path), sha256_file(receipt_path))].add(
            gate_id
        )
        artifact_sources[(repo_relative(anchor_path), sha256_file(anchor_path))].add(
            gate_id
        )
        for relative, accepted_digest in receipt["output_artifact_digests"].items():
            path = EXPERIMENT_ROOT / relative
            repository_relative = repo_relative(path)
            current_digest = sha256_file(path) if path.is_file() else None
            if current_digest == accepted_digest:
                artifact_sources[(repository_relative, accepted_digest)].add(gate_id)
            else:
                replaced.append(
                    {
                        "accepted_sha256": accepted_digest,
                        "current_sha256": current_digest,
                        "gate_id": gate_id,
                        "path": repository_relative,
                        "status": "superseded_or_replaced_after_gate_acceptance",
                    }
                )

    artifacts = [
        {"path": path, "sha256": digest, "source_gates": sorted(gates)}
        for (path, digest), gates in sorted(artifact_sources.items())
    ]
    contradictions = envelope(
        EXPERIMENT_ROOT / "outputs/final_contradiction_routing.json"
    )["payload"]["entries"]
    debts = envelope(EXPERIMENT_ROOT / "outputs/final_theory_debt_register.json")[
        "payload"
    ]["rows"]
    return {
        "experiment_id": "B1-GR",
        "accepted_gate_results": accepted_gate_results,
        "accepted_anchor_digests": anchor_digests,
        "artifacts": artifacts,
        "superseded_or_replaced_artifacts": sorted(
            replaced, key=lambda row: (row["path"], row["gate_id"])
        ),
        "bundle_excluded_paths": policy["bundle_excluded_paths"],
        "claim_ceiling": policy["claim_ceiling"],
        "contradictions": [
            {
                "contradiction_id": row["contradiction_id"],
                "route": row["route"],
                "scope_limit": row.get("scope_limit"),
                "subject": row["subject"],
                "theory_contradicted": row["theory_contradicted"],
            }
            for row in contradictions
        ],
        "open_debt": [
            {
                "debt_id": row["Debt ID"],
                "primary_route": row["GRV8_primary_route"],
                "status": row["GRV8_status"],
            }
            for row in debts
        ],
        "grv_c6_assigned": False,
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        values = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def render_successor(
    policy: dict[str, Any],
    bundle: dict[str, Any],
    grv8_anchor: dict[str, Any],
) -> str:
    assumptions = envelope(EXPERIMENT_ROOT / "outputs/assumption_status_matrix.json")[
        "payload"
    ]["rows"]
    claims = envelope(EXPERIMENT_ROOT / "outputs/final_claim_classification.json")[
        "payload"
    ]["rows"]
    debts = envelope(EXPERIMENT_ROOT / "outputs/final_theory_debt_register.json")[
        "payload"
    ]["rows"]
    contradictions = envelope(
        EXPERIMENT_ROOT / "outputs/final_contradiction_routing.json"
    )["payload"]["entries"]
    extensions = envelope(EXPERIMENT_ROOT / "outputs/extension_decision.json")[
        "payload"
    ]["decisions"]
    superseded = envelope(
        EXPERIMENT_ROOT / "outputs/superseded_exploratory_claims.json"
    )["payload"]["records"]
    predecessor = PREDECESSOR_SPEC_PATH.read_text(encoding="utf-8")
    predecessor_digest = sha256_file(PREDECESSOR_SPEC_PATH)

    lines = [
        "# GRC9V3 Continuation And Read-Back Verification Specification - Evidence-Grounded v1",
        "",
        "## Status And Provenance",
        "",
        "```text",
        "specification_id = GRC9V3-Continuation-ReadBack-Verification-EvidenceGrounded-v1",
        f"predecessor_path = {repo_relative(PREDECESSOR_SPEC_PATH)}",
        f"predecessor_sha256 = {predecessor_digest}",
        f"accepted_grv8_result_revision = {grv8_anchor['result_revision']}",
        f"accepted_grv8_receipt_payload_sha256 = {grv8_anchor['receipt_payload_sha256']}",
        f"evidence_bundle_payload_sha256 = {bundle['payload_sha256']}",
        "closeout_status = candidate_pending_human_review",
        "GRV_C6_assigned = false",
        "runtime_change_authorized = false",
        "```",
        "",
        "This successor records the accepted unchanged-`GRC9V3` evidence and its",
        "bounded next routes. It does not alter the preserved pre-execution",
        "specification below, implement an extension, or promote an LGRC-specific",
        "question into the umbrella handoff.",
        "",
        "## Evidence-Grounded Route Order",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Order", "Lane", "Status", "Role"],
            [
                [row["lane_order"], row["lane_id"], row["status"], row["role"]]
                for row in policy["handoff_lanes"]
            ],
        )
    )
    lines.extend(
        [
            "",
            "The first downstream work is GRC-side: unchanged-runtime",
            "constructibility where still required, followed by a separately",
            "selected revision-distinct GRC extension when a target contract needs",
            "current temporalization or oriented current. LGRC event, delay,",
            "lineage, and topology-changing work is a later distinct lane over an",
            "explicit GRC base.",
            "",
            "## Final Assumption Statuses",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            ["Assumption", "Status", "Scope"],
            [[row["assumption_id"], row["status"], row["scope"]] for row in assumptions],
        )
    )
    lines.extend(["", "## Final Claim Classification", ""])
    lines.extend(
        markdown_table(
            ["Claim", "Disposition", "Primary route", "Maximum supported claim"],
            [
                [
                    row["claim_id"],
                    row["disposition"],
                    row["primary_decision_route"],
                    row["maximum_supported_claim"],
                ]
                for row in claims
            ],
        )
    )
    lines.extend(["", "## Final Open Debt", ""])
    lines.extend(
        markdown_table(
            ["Debt", "Status", "Primary route", "Blocked claim"],
            [
                [
                    row["Debt ID"],
                    row["GRV8_status"],
                    row["GRV8_primary_route"],
                    row["Claim blocked"],
                ]
                for row in debts
            ],
        )
    )
    lines.extend(["", "## Extension Decisions", ""])
    lines.extend(
        markdown_table(
            ["Decision", "Target", "Route", "Claim ceiling"],
            [
                [row["decision_id"], row["target"], row["route"], row["claim_ceiling"]]
                for row in extensions
            ],
        )
    )
    lines.extend(["", "## Contradiction Routing", ""])
    lines.extend(
        markdown_table(
            ["ID", "Subject", "Route", "Theory contradicted"],
            [
                [
                    row["contradiction_id"],
                    row["subject"],
                    row["route"],
                    row["theory_contradicted"],
                ]
                for row in contradictions
            ],
        )
    )
    lines.extend(["", "## Superseded Exploratory Statements", ""])
    lines.extend(
        markdown_table(
            ["ID", "Disposition", "Superseded statement", "Replacement"],
            [
                [
                    row["exploratory_claim_id"],
                    row["disposition"],
                    row["superseded_statement"],
                    row["replacement"],
                ]
                for row in superseded
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Preserved Pre-Execution Specification",
            "",
            "The following text is preserved verbatim from the accepted predecessor",
            "and remains the controlling account of the executed protocol.",
            "",
            predecessor.rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def handoff_payload(
    policy: dict[str, Any],
    bundle: dict[str, Any],
    successor_digest: str,
    grv8_anchor: dict[str, Any],
) -> dict[str, Any]:
    extension = envelope(EXPERIMENT_ROOT / "outputs/extension_decision.json")[
        "payload"
    ]
    decisions = {row["decision_id"]: row for row in extension["decisions"]}
    lanes = []
    for source in policy["handoff_lanes"]:
        row = dict(source)
        row["source_decisions"] = [
            {
                "claim_ceiling": decisions[decision_id]["claim_ceiling"],
                "decision_id": decision_id,
                "route": decisions[decision_id]["route"],
                "target": decisions[decision_id]["target"],
            }
            for decision_id in source["source_decision_ids"]
        ]
        lanes.append(row)
    return {
        "handoff_id": policy["handoff_id"],
        "source_experiment": "B1-GR",
        "source_closeout_ceiling": "GRV-C5",
        "source_closeout_target": "GRV-C6",
        "accepted_grv8_anchor": {
            "path": "outputs/gates/grv8_acceptance_anchor.json",
            "sha256": sha256_file(
                EXPERIMENT_ROOT / "outputs/gates/grv8_acceptance_anchor.json"
            ),
            "result_revision": grv8_anchor["result_revision"],
            "receipt_payload_sha256": grv8_anchor["receipt_payload_sha256"],
        },
        "evidence_bundle": {
            "path": "outputs/evidence_bundle_manifest.json",
            "payload_sha256": bundle["payload_sha256"],
        },
        "successor_specification": {
            "path": repo_relative(SUCCESSOR_PATH),
            "sha256": successor_digest,
        },
        "handoff_status": "candidate_pending_closeout_review",
        "handoff_lanes": lanes,
        "legacy_lgrc_handoff_disposition": policy[
            "legacy_lgrc_handoff_disposition"
        ],
        "blocked_claims": policy["required_blocked_claims"],
        "source_artifacts": [
            "outputs/extension_decision.json",
            "outputs/equivalence_classification.json",
            "outputs/final_claim_classification.json",
            "outputs/final_theory_debt_register.json",
            "outputs/final_contradiction_routing.json",
            "outputs/final_theory_test_traceability.json",
        ],
        "grv_c6_assigned": False,
    }


def write_report(
    policy: dict[str, Any],
    bundle: dict[str, Any],
    handoff: dict[str, Any],
    successor_digest: str,
) -> None:
    lines = [
        "# B1-GR GRV8 Stage 2 Closeout Candidate",
        "",
        "## Result",
        "",
        "```text",
        "mechanical_status = passed",
        "scientific_acceptance = awaiting_human_review",
        "accepted_GRV8_classification = true",
        f"evidence_bundle_payload_sha256 = {bundle['payload_sha256']}",
        f"successor_sha256 = {successor_digest}",
        f"route_handoff_payload_sha256 = {handoff['payload_sha256']}",
        "GRV_C6_assigned = false",
        "B1_L_execution_authorized = false",
        "runtime_change_authorized = false",
        "```",
        "",
        "## Route Order",
        "",
    ]
    lines.extend(
        f"{row['lane_order']}. `{row['lane_id']}`: {row['role']}"
        for row in policy["handoff_lanes"]
    )
    lines.extend(
        [
            "",
            "The Stage 2 candidate does not use LGRC as the umbrella destination.",
            "It records GRC constructibility and selectable-extension work first,",
            "then preserves LGRC-specific questions as a separate downstream lane.",
            "A separate human closeout acceptance is required before `GRV-C6`.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV8 Stage 2 requires a clean committed method revision")
    if CLOSEOUT_ANCHOR_PATH.exists():
        raise SystemExit("closeout acceptance anchor already exists")
    input_revision = git("rev-parse", "HEAD")
    grv8_receipt, grv8_anchor = accepted_grv8()
    policy = read_json(POLICY_PATH)

    bundle_payload = collect_evidence_bundle(policy)
    bundle = artifact_envelope(
        bundle_payload,
        schema_version="b1_grv8_evidence_bundle_manifest_v1",
        generating_command=COMMAND,
    )
    write_json(BUNDLE_PATH, bundle)

    SUCCESSOR_PATH.write_text(
        render_successor(policy, bundle, grv8_anchor), encoding="utf-8"
    )
    successor_digest = sha256_file(SUCCESSOR_PATH)
    handoff = artifact_envelope(
        handoff_payload(policy, bundle, successor_digest, grv8_anchor),
        schema_version="b1_continuation_readback_handoff_v1",
        generating_command=COMMAND,
    )
    write_json(HANDOFF_PATH, handoff)
    write_report(policy, bundle, handoff, successor_digest)

    experiment_prefix = repo_relative(EXPERIMENT_ROOT)
    input_tree = file_manifest(tracked_files([experiment_prefix]))
    output_paths = [BUNDLE_PATH, SUCCESSOR_PATH, HANDOFF_PATH, REPORT_PATH]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV8",
            "input_execution_revision": input_revision,
            "substrate_base_revision": grv8_receipt["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [
                grv8_receipt["receipt_payload_sha256"]
            ],
            "prerequisite_acceptance_anchors": [
                {
                    "anchor_payload_sha256": semantic_digest(grv8_anchor),
                    "gate_id": "GRV8",
                    "immutable_ref": f"git:{grv8_anchor['result_revision']}",
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in output_paths
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": ["GRV8_closeout_acceptance", "GRV-C6", "B1-L"],
            "claim_ceiling": policy["claim_ceiling"],
        }
    )
    validate_receipt(receipt)
    write_json(RECEIPT_PATH, receipt)
    print("GRV8 Stage 2 closeout candidate built; human closeout review is pending.")


if __name__ == "__main__":
    build()

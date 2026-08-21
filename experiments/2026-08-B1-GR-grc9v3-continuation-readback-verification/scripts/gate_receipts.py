"""Result-receipt and human acceptance-anchor validation for B1-GR."""

from __future__ import annotations

from typing import Any

from artifact_io import assert_required_fields, semantic_digest


RECEIPT_STATUSES = {"generated", "mechanically_validated", "awaiting_scientific_review", "rejected", "blocked", "superseded"}
ANCHOR_STATUSES = {"accepted", "rejected", "blocked", "superseded"}


def receipt_payload_digest(receipt: dict[str, Any]) -> str:
    payload = dict(receipt)
    payload.pop("receipt_payload_sha256", None)
    return semantic_digest(payload)


def finalize_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    validate_receipt(receipt, require_digest=False)
    result = dict(receipt)
    result["receipt_payload_sha256"] = receipt_payload_digest(result)
    return result


def validate_receipt(receipt: dict[str, Any], *, require_digest: bool = True) -> None:
    assert_required_fields(receipt, ["gate_id", "input_execution_revision", "substrate_base_revision", "input_experiment_tree_sha256", "prerequisite_result_receipt_digests", "prerequisite_acceptance_anchors", "output_artifact_digests", "status", "blocked_gates", "claim_ceiling"])
    if receipt["status"] not in RECEIPT_STATUSES:
        raise ValueError("invalid receipt status")
    if require_digest and receipt.get("receipt_payload_sha256") != receipt_payload_digest(receipt):
        raise ValueError("receipt payload digest mismatch")
    if any(path.endswith("result_receipt.json") for path in receipt["output_artifact_digests"]):
        raise ValueError("receipt must exclude itself from output artifact digests")


def validate_acceptance_anchor(anchor: dict[str, Any]) -> None:
    assert_required_fields(anchor, ["gate_id", "result_revision", "receipt_payload_sha256", "accepted_by", "acceptance_role", "review_method", "acceptance_timestamp", "acceptance_status", "acceptance_signature_or_ref"])
    if anchor["acceptance_status"] not in ANCHOR_STATUSES:
        raise ValueError("invalid acceptance-anchor status")
    if anchor["accepted_by"] in {"run_all.py", "mechanical_script", "automation"}:
        raise ValueError("mechanical tooling cannot be an accepting authority")


def prerequisite_is_authorized(anchor: dict[str, Any]) -> bool:
    validate_acceptance_anchor(anchor)
    return anchor["acceptance_status"] == "accepted"

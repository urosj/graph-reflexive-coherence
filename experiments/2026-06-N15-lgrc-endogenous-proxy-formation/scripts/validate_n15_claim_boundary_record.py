#!/usr/bin/env python3
"""Validate the N15 Iteration 7 claim-boundary artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
DEFAULT_OUTPUT = EXPERIMENT / "outputs" / "n15_claim_boundary_record.json"

EXPECTED_ACCEPTANCE = "accepted_ap5_classification_claim_boundary_clean_pending_closeout"
EXPECTED_CLAIM_CEILING = "artifact_level_ap5_endogenous_proxy_formation_candidate"
EXPECTED_I4_BLOCKED_CLAIMS = {
    "agency",
    "intention",
    "semantic_choice",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "selfhood",
    "personhood",
    "biological_behavior",
    "unrestricted_agency",
    "fully_native_agentic_like_integration",
    "native_support_without_phase8",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def validate(output: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            errors.append(label)

    checks = output.get("checks", {})
    gates = output.get("ap5_gate_resolution", [])
    gate_summary = output.get("ap5_gate_summary", {})
    hypotheses = output.get("hypothesis_classification", {})
    boundary_rows = output.get("boundary_rows", [])
    boundary_summary = output.get("boundary_summary", {})
    claim_boundary = output.get("claim_boundary_record", {})
    idempotency = output.get("idempotency_digest_plan", {})
    rows_scope = output.get("rows_scope_note", {})
    schema_evolution = output.get("schema_evolution", {})
    control_coverage = output.get("claim_boundary_control_coverage", {})
    interpretation_scope = output.get("interpretation_scope", {})
    review_gap_closure = output.get("review_gap_closure", {})
    iteration_result = output.get("iteration_result", {})

    require(output.get("status") == "passed", "status_not_passed")
    require(output.get("acceptance_state") == EXPECTED_ACCEPTANCE, "acceptance_mismatch")
    require(output.get("iteration") == 7, "iteration_not_7")
    require(output.get("artifact_id") == "n15_claim_boundary_record", "artifact_id_mismatch")
    require(output.get("output_digest") == output_digest(output), "output_digest_mismatch")
    require(not contains_absolute_path(output), "absolute_path_present")
    require(bool(checks) and all(checks.values()), "checks_not_all_true")

    require(gate_summary.get("gate_count") == 36, "gate_count_not_36")
    require(
        gate_summary.get("validated_gate_count") == 36
        and gate_summary.get("blocked_gate_count") == 0,
        "gate_summary_not_all_validated",
    )
    require(
        len(gates) == 36 and all(gate.get("validated") is True for gate in gates),
        "ap5_gates_not_all_validated",
    )
    require(
        all(record.get("supported") is True for record in hypotheses.values())
        and set(hypotheses)
        == {
            "hypothesis_a_runtime_state_proxy_sources",
            "hypothesis_b_bounded_endogenous_proxy_formation",
            "hypothesis_c_goal_ownership_and_agency_boundary",
        },
        "hypotheses_not_all_supported",
    )

    require(output.get("rows") == [], "top_level_rows_not_empty")
    require(rows_scope.get("rows_empty") is True, "rows_scope_not_recorded")
    require(rows_scope.get("not_evidence_gap") is True, "rows_scope_gap_not_closed")

    require(len(boundary_rows) == 10, "boundary_row_count_not_10")
    require(
        boundary_summary.get("boundary_row_count") == 10
        and boundary_summary.get("all_boundary_claims_blocked") is True,
        "boundary_summary_not_blocked",
    )
    require(
        boundary_rows == claim_boundary.get("boundary_rows"),
        "boundary_rows_mirror_mismatch",
    )
    require(
        boundary_summary == claim_boundary.get("boundary_summary"),
        "boundary_summary_mirror_mismatch",
    )
    require(
        claim_boundary.get("claim_ceiling_candidate") == EXPECTED_CLAIM_CEILING,
        "claim_ceiling_mismatch",
    )
    require(claim_boundary.get("final_ap5_supported") is False, "i7_final_ap5_true")

    require(
        set(control_coverage.get("observed_blocked_claims", []))
        == EXPECTED_I4_BLOCKED_CLAIMS,
        "observed_blocked_claims_mismatch",
    )
    require(
        control_coverage.get("coverage_asymmetry_recorded") is True
        and control_coverage.get("all_expected_claims_covered") is True,
        "control_coverage_not_closed",
    )
    require(
        schema_evolution.get("schema_evolution_recorded") is True
        and schema_evolution.get("runtime_output_fields_preserved") is True,
        "schema_evolution_not_recorded",
    )
    require(
        all(interpretation_scope.get("consistency_checks", {}).values()),
        "interpretation_scope_inconsistent",
    )
    require(
        review_gap_closure.get("review_gap_closure_recorded") is True
        and len(review_gap_closure.get("closures", [])) == 10,
        "review_gap_closure_not_recorded",
    )
    require(
        idempotency.get("digest") == digest_value(idempotency.get("scope", {})),
        "idempotency_digest_mismatch",
    )
    require(bool(idempotency.get("scope_note")), "idempotency_scope_note_missing")

    require(
        set(output.get("iteration_7_top_level_output_fields", [])) == set(output),
        "top_level_field_declaration_mismatch",
    )
    require(all(value is False for value in output.get("claim_flags", {}).values()), "claim_flag_true")
    require(iteration_result.get("classified_ap_level") == "AP5", "ap_level_not_ap5")
    require(
        iteration_result.get("final_ap5_supported") is False
        and iteration_result.get("final_ap_freeze_pending_iteration8") is True,
        "i7_final_freeze_state_mismatch",
    )
    require(iteration_result.get("phase8_opened") is False, "phase8_opened")
    require(iteration_result.get("native_support_opened") is False, "native_support_opened")
    require(
        iteration_result.get("fully_native_integration_opened") is False,
        "fully_native_integration_opened",
    )

    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUTPUT
    if not path.is_absolute():
        path = ROOT / path
    output = load_json(path)
    errors = validate(output)
    result = {
        "status": "passed" if not errors else "failed",
        "artifact": rel(path),
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

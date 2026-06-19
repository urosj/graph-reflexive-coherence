#!/usr/bin/env python3
"""Build N19 Iteration 2 naturalization schema and control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
INVENTORY = EXPERIMENT / "outputs" / "n19_ap3_ap8_source_inventory.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_naturalization_schema_v1.json"
REPORT = EXPERIMENT / "reports" / "n19_naturalization_schema_v1.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_naturalization_schema_v1.py"
)

NAT_LEVELS = ["NAT0", "NAT1", "NAT2", "NAT3", "NAT4", "NAT5", "NAT6"]

PRIMARY_DISPOSITIONS = [
    "scaffold",
    "native_contract_candidate",
    "phase8_ready_native_policy_candidate",
    "implementation_gap_blocker",
    "theory_sensitive_blocker",
    "unsafe_relabel_rejected",
    "not_applicable",
]

ROW_DECISIONS = [
    "supported",
    "partial",
    "blocked",
    "rejected",
    "not_applicable",
]

PHASE8_READY_DERIVATION = (
    "phase8_ready = true only when nat_level = NAT4 and all NAT4 gates pass"
)

CLAIM_FLAGS = [
    "agency_claim_allowed",
    "intention_claim_allowed",
    "choice_claim_allowed",
    "semantic_action_claim_allowed",
    "semantic_perception_claim_allowed",
    "semantic_goal_ownership_claim_allowed",
    "selfhood_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_opened",
    "phase8_opened",
    "organism_life_claim_allowed",
    "fully_native_agentic_like_integration_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "ap9_opened",
]

CLAIM_FLAG_TO_BLOCKED_CLAIM = {
    "agency_claim_allowed": "agency",
    "intention_claim_allowed": "intention",
    "choice_claim_allowed": "choice",
    "semantic_action_claim_allowed": "semantic action",
    "semantic_perception_claim_allowed": "semantic perception",
    "semantic_goal_ownership_claim_allowed": "semantic goal ownership",
    "selfhood_claim_allowed": "selfhood",
    "identity_acceptance_claim_allowed": "identity acceptance",
    "native_support_opened": "native support",
    "phase8_opened": "Phase 8 opened",
    "organism_life_claim_allowed": "organism/life behavior",
    "fully_native_agentic_like_integration_claim_allowed": "fully native agentic-like integration",
    "unrestricted_autonomy_claim_allowed": "unrestricted autonomy",
    "ap9_opened": "AP9",
}

REQUIRED_ROW_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration_or_closeout",
    "source_artifacts",
    "source_reports",
    "source_sha256",
    "source_output_digest",
    "source_final_supported_ap_level",
    "source_final_claim_ceiling",
    "artifact_supported",
    "artifact_claim_scope",
    "native_question",
    "primary_disposition",
    "nat_level",
    "phase8_ready",
    "phase8_ready_derivation",
    "native_policy_or_telemetry_surface_name",
    "runtime_visible_inputs",
    "native_state_needed",
    "state_mutation_owner",
    "record_schema_sketch",
    "default_off_flags",
    "enabled_validated_supported_separation",
    "budget_surface",
    "telemetry_requirements",
    "snapshot_replay_requirements",
    "negative_controls",
    "non_rc_quantity_audit",
    "minimal_producer_code_needed",
    "implementation_boundary",
    "claim_flags",
    "blocked_claims",
    "phase8_opened",
    "native_support_opened",
    "src_diff_empty",
    "row_decision",
]

NAT4_GATES = [
    "native_policy_or_telemetry_surface_name_present",
    "record_schema_sketch_present",
    "default_off_flags_present",
    "enabled_validated_supported_separation_present",
    "runtime_visible_inputs_source_backed",
    "state_mutation_owner_specified",
    "budget_surface_specified",
    "telemetry_requirements_specified",
    "snapshot_replay_requirements_specified",
    "negative_controls_specified",
    "non_rc_quantity_audit_passes",
    "claim_flags_forced_false",
    "phase8_opened_false",
    "native_support_opened_false",
    "src_diff_empty_true",
]

UNSAFE_RELABEL_CONTROLS = [
    {
        "control_id": "artifact_replay_as_native_support_rejected",
        "blocked_claim": "native_support",
    },
    {
        "control_id": "nat3_as_nat4_rejected",
        "blocked_claim": "phase8_ready_without_all_nat4_gates",
    },
    {
        "control_id": "nat4_as_native_implementation_rejected",
        "blocked_claim": "phase8_implementation",
    },
    {
        "control_id": "phase8_opened_by_classification_flag_rejected",
        "blocked_claim": "phase8_opened",
    },
    {
        "control_id": "direct_native_support_flag_write_rejected",
        "blocked_claim": "native_support_opened",
    },
    {
        "control_id": "ap_evidence_as_agency_rejected",
        "blocked_claim": "agency",
    },
    {
        "control_id": "response_as_semantic_action_rejected",
        "blocked_claim": "semantic_action",
    },
    {
        "control_id": "feedback_as_semantic_perception_rejected",
        "blocked_claim": "semantic_perception",
    },
    {
        "control_id": "proxy_as_semantic_goal_rejected",
        "blocked_claim": "semantic_goal_ownership",
    },
    {
        "control_id": "boundary_as_selfhood_rejected",
        "blocked_claim": "selfhood",
    },
    {
        "control_id": "identity_acceptance_relabel_rejected",
        "blocked_claim": "identity_acceptance",
    },
    {
        "control_id": "organism_life_relabel_rejected",
        "blocked_claim": "organism_life",
    },
    {
        "control_id": "limited_h4_l5_as_general_ap8_rejected",
        "blocked_claim": "general_ap8",
    },
    {
        "control_id": "derived_b4c5_as_original_b4c5_rejected",
        "blocked_claim": "original_b4c5_reverse_replay",
    },
    {
        "control_id": "non_rc_quantity_inserted_to_pass_rejected",
        "blocked_claim": "non_rc_quantity",
    },
    {
        "control_id": "src_diff_non_empty_rejected",
        "blocked_claim": "native_implementation_inside_n19",
    },
    {
        "control_id": "absolute_path_in_record_rejected",
        "blocked_claim": "non_portable_record",
    },
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 2 - Naturalization Schema V1",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"candidate_rows_classified = {str(artifact['candidate_rows_classified']).lower()}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Frozen enums:",
        "",
        "```json",
        json.dumps(artifact["enums"], indent=2, sort_keys=True),
        "```",
        "",
        "Required row fields:",
        "",
        "```json",
        json.dumps(artifact["candidate_row_schema"]["required_fields"], indent=2),
        "```",
        "",
        "Claim flag mapping:",
        "",
        "```json",
        json.dumps(
            artifact["candidate_row_schema"]["claim_flag_to_blocked_claim_mapping"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "NAT4 gates:",
        "",
        "```json",
        json.dumps(artifact["nat4_readiness_gates"], indent=2),
        "```",
        "",
        "Controls:",
        "",
        "| Control | Blocked Claim |",
        "| --- | --- |",
    ]
    for control in artifact["unsafe_relabel_controls"]:
        lines.append(f"| {control['control_id']} | {control['blocked_claim']} |")
    lines.extend(
        [
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.extend([""])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = load_json(INVENTORY)
    candidate_rows: list[dict[str, Any]] = []
    checks = [
        {
            "check_id": "source_inventory_available",
            "passed": inventory.get("status") == "passed",
            "detail": rel(INVENTORY),
        },
        {
            "check_id": "primary_disposition_enum_frozen",
            "passed": len(PRIMARY_DISPOSITIONS) == len(set(PRIMARY_DISPOSITIONS)),
            "detail": PRIMARY_DISPOSITIONS,
        },
        {
            "check_id": "nat_level_enum_frozen",
            "passed": NAT_LEVELS == ["NAT0", "NAT1", "NAT2", "NAT3", "NAT4", "NAT5", "NAT6"],
            "detail": NAT_LEVELS,
        },
        {
            "check_id": "phase8_ready_derivation_frozen",
            "passed": (
                "nat_level = NAT4" in PHASE8_READY_DERIVATION
                and "all NAT4 gates pass" in PHASE8_READY_DERIVATION
                and "NAT4" in NAT_LEVELS
                and len(NAT4_GATES) == 15
            ),
            "detail": PHASE8_READY_DERIVATION,
        },
        {
            "check_id": "nat4_gates_frozen",
            "passed": len(NAT4_GATES) == 15,
            "detail": len(NAT4_GATES),
        },
        {
            "check_id": "row_decision_enum_frozen",
            "passed": ROW_DECISIONS == [
                "supported",
                "partial",
                "blocked",
                "rejected",
                "not_applicable",
            ],
            "detail": ROW_DECISIONS,
        },
        {
            "check_id": "claim_flags_forced_false_schema_present",
            "passed": (
                set(CLAIM_FLAGS) == set(CLAIM_FLAG_TO_BLOCKED_CLAIM)
                and "native_support_opened" in CLAIM_FLAGS
                and "phase8_opened" in CLAIM_FLAGS
            ),
            "detail": CLAIM_FLAG_TO_BLOCKED_CLAIM,
        },
        {
            "check_id": "non_rc_quantity_audit_required",
            "passed": "non_rc_quantity_audit" in REQUIRED_ROW_FIELDS,
            "detail": "required row field",
        },
        {
            "check_id": "minimal_producer_code_needed_required",
            "passed": "minimal_producer_code_needed" in REQUIRED_ROW_FIELDS,
            "detail": "required row field",
        },
        {
            "check_id": "unsafe_relabel_controls_frozen",
            "passed": len(UNSAFE_RELABEL_CONTROLS) >= 15,
            "detail": len(UNSAFE_RELABEL_CONTROLS),
        },
        {
            "check_id": "no_candidate_rows_classified_in_iteration_2",
            "passed": len(candidate_rows) == 0,
            "detail": {
                "candidate_row_count": len(candidate_rows),
                "reason": "schema/control freeze only",
            },
        },
    ]
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_naturalization_schema_v1",
        "schema_version": "n19_naturalization_schema_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 2,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "Freeze N19 row schema, NAT ladder enums, NAT4 gates, and controls before candidate classification.",
        "source_inventory": {
            "path": rel(INVENTORY),
            "sha256": sha256_file(INVENTORY),
            "output_digest": inventory["output_digest"],
            "row_count": inventory["row_count"],
        },
        "candidate_rows": candidate_rows,
        "candidate_rows_classified": len(candidate_rows) > 0,
        "candidate_row_schema": {
            "required_fields": REQUIRED_ROW_FIELDS,
            "exactly_one_primary_disposition_required": True,
            "phase8_ready_derivation": PHASE8_READY_DERIVATION,
            "nat5_nat6_out_of_scope": True,
            "claim_flags_forced_false": CLAIM_FLAGS,
            "claim_flag_to_blocked_claim_mapping": CLAIM_FLAG_TO_BLOCKED_CLAIM,
            "portable_paths_required": True,
            "source_digests_required": True,
        },
        "enums": {
            "nat_level": NAT_LEVELS,
            "primary_disposition": PRIMARY_DISPOSITIONS,
            "row_decision": ROW_DECISIONS,
        },
        "nat4_readiness_gates": NAT4_GATES,
        "nat_level_policy": {
            "NAT0": "artifact scaffold only",
            "NAT1": "source-backed producer pattern",
            "NAT2": "replayable producer pattern with controls",
            "NAT3": "native contract candidate but not phase8_ready",
            "NAT4": "Phase 8-ready native policy candidate with no implementation",
            "NAT5": "out_of_scope_for_n19",
            "NAT6": "out_of_scope_for_n19",
        },
        "field_policies": {
            "phase8_ready": PHASE8_READY_DERIVATION,
            "native_support_opened": "must remain false in N19",
            "phase8_opened": "must remain false in N19",
            "src_diff_empty": "required true before closeout",
            "minimal_producer_code_needed": "records future implementation work without implementing it",
            "non_rc_quantity_audit": "blocks rows that require hidden or non-RC state to pass",
            "phase8_implementation": (
                "blocked separately by nat4_as_native_implementation_rejected; "
                "phase8_opened blocks opening the phase itself"
            ),
        },
        "unsafe_relabel_controls": UNSAFE_RELABEL_CONTROLS,
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
        "claim_boundary": (
            "N19 freezes schema and controls only. It does not classify candidates yet, "
            "open Phase 8, open native support, or create AP9."
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

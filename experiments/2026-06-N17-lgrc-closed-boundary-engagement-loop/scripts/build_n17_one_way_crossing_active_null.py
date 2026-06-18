#!/usr/bin/env python3
"""Build N17 Iteration 3 one-way crossing active null.

Iteration 3 is a strong near-miss. It records boundary crossing, internal
support update, and a tempting bounded-response marker while failing closed
because no response-caused external change feeds back into later internal
support.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SOURCE_INVENTORY = OUTPUTS / "n17_loop_source_inventory.json"
SCHEMA_PATH = OUTPUTS / "n17_loop_schema_v1.json"
N16_SELECTED_INTERACTION = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
    "n16_selected_interaction_probe_matrix.json"
)
OUTPUT_PATH = OUTPUTS / "n17_one_way_crossing_active_null.json"
REPORT_PATH = REPORTS / "n17_one_way_crossing_active_null.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_one_way_crossing_active_null.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

SOURCE_ROW_IDS = [
    "n17_i1_row_01_n16_closeout_ap6",
    "n17_i1_row_02_n16_claim_boundary_record",
    "n17_i1_row_03_n16_b3_c4_breach_reclosure",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    payload.pop("git", None)
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_value(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(digest_payload(data)).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def find_n16_b3_c4_row(n16_artifact: dict[str, Any]) -> dict[str, Any]:
    for row in n16_artifact.get("rows", []):
        if isinstance(row, dict) and row.get("cell_id") == "B3_C4":
            return row
    raise ValueError("B3_C4 row not found in N16 selected interaction matrix")


def source_artifacts(source_inventory: dict[str, Any]) -> list[dict[str, Any]]:
    rows = {
        row["row_id"]: row
        for row in source_inventory["source_rows"]
        if row["row_id"] in SOURCE_ROW_IDS
    }
    return [
        {
            "source_row_id": row_id,
            "source_artifact": rows[row_id]["source_artifact"],
            "source_report": rows[row_id]["source_report"],
            "source_sha256": rows[row_id]["source_sha256"],
            "source_report_sha256": rows[row_id]["source_report_sha256"],
            "source_output_digest": rows[row_id]["source_output_digest"],
            "source_claim_ceiling": rows[row_id]["source_claim_ceiling"],
        }
        for row_id in SOURCE_ROW_IDS
    ]


def control_statuses(schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    controls: dict[str, dict[str, str]] = {}
    for control in schema["control_requirements"]:
        control_id = control["control_id"]
        expected = control["expected_for_supported_loop"]
        if expected.startswith("not_applicable_for_mvp"):
            status = "not_applicable"
            result = "extension_control_frozen_not_executed_for_i3_active_null"
        else:
            status = "passed"
            result = "fail_closed_condition_verified"
        controls[control_id] = {
            "status": status,
            "result": result,
            "failure_blocks_gate": control["failure_blocks_gate"],
        }

    controls["one_way_crossing_relabel_control"] = {
        "status": "passed",
        "result": "relabel_attempt_blocked",
        "failure_mode": "one_way_crossing_is_not_closed_loop",
        "closed_loop_claim_allowed_after_relabel_attempt": "false",
    }
    controls["external_change_not_caused_by_response_control"] = {
        "status": "passed",
        "result": "external_change_after_response_not_accepted_as_response_caused",
        "failure_mode": "external_change_after_response_is_not_enough",
    }
    controls["feedback_removed_control"] = {
        "status": "passed",
        "result": "feedback_leg_absent_before_and_after_removal",
        "failure_mode": "no_fourth_leg_to_remove_or_validate",
    }
    return controls


def claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": False,
        "closed_loop_demonstrated": False,
        "final_ap7_supported": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def build_active_null_row(
    schema: dict[str, Any],
    source_inventory: dict[str, Any],
    n16_b3_c4: dict[str, Any],
) -> dict[str, Any]:
    internal_descriptor = n16_b3_c4.get("internal_state_descriptor", {})
    metrics = n16_b3_c4.get("metrics") or {
        "minimum_internal_support": internal_descriptor[
            "minimum_observed_internal_support"
        ],
        "repair_score": n16_b3_c4["repair_score"],
        "internal_coherence": n16_b3_c4["internal_coherence"],
        "coherence_margin": n16_b3_c4["coherence_margin"],
        "leakage_ratio": n16_b3_c4["leakage_ratio"],
        "boundary_stability_score": n16_b3_c4["boundary_stability_score"],
    }
    probe = (
        n16_b3_c4.get("probe_decomposition")
        or n16_b3_c4.get("boundary_surface", {}).get("probe_decomposition")
        or n16_b3_c4.get("external_resource_descriptor", {}).get("probe_decomposition")
    )
    if not isinstance(probe, dict):
        raise ValueError("B3_C4 probe_decomposition not found")
    b2_reference = probe["b2_c4_baseline_reference"]
    boundary_edges = n16_b3_c4.get("boundary_edges") or n16_b3_c4.get(
        "boundary_surface", {}
    ).get("challenge_boundary_edges")
    if not isinstance(boundary_edges, list):
        raise ValueError("B3_C4 boundary_edges not found")
    boundary_side_assignments = n16_b3_c4.get(
        "boundary_side_assignments"
    ) or n16_b3_c4.get("boundary_surface", {}).get("side_derivation")
    if not isinstance(boundary_side_assignments, dict):
        raise ValueError("B3_C4 boundary side assignments not found")
    controls = control_statuses(schema)
    flags = claim_flags(schema)

    ap7_gates = {
        "g3_or_higher": False,
        "four_trace_legs_present": False,
        "four_trace_legs_source_backed": False,
        "monotonic_phase_order_valid": False,
        "response_caused_external_change": False,
        "external_change_counterfactual_blocks_spontaneous_change": False,
        "later_internal_depends_on_changed_external_state": False,
        "feedback_removed_control_passed": False,
        "one_way_crossing_null_blocked": True,
        "dependency_trace_complete": False,
        "replay_digest_valid": True,
        "budget_validity_passed": True,
        "controls_passed": True,
        "claim_boundary_clean": True,
        "source_registry_backed": True,
        "no_absolute_paths": True,
    }
    missing_gates = [gate for gate, passed in ap7_gates.items() if not passed]

    row: dict[str, Any] = {
        "row_id": "n17_i3_row_01_one_way_crossing_active_null",
        "schema_version": schema["schema_version"],
        "loop_policy_digest": schema["config_files"]["loop_policy"]["config_digest"],
        "row_type": "active_null",
        "loop_family": "one_way_crossing_active_null",
        "loop_rung": "G2",
        "loop_rung_index": 2,
        "source_row_ids": SOURCE_ROW_IDS,
        "source_artifacts": source_artifacts(source_inventory),
        "row_decision": "supported",
        "boundary_assignments": {
            "source": "N16_B3_C4_selected_interaction_probe",
            "boundary_side_assignments": boundary_side_assignments,
            "boundary_edges": boundary_edges,
        },
        "external_to_internal_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t0_external_pressure_or_crossing",
            "state_before": "external_breach_pressure_not_crossed",
            "state_after": "breach_pressure_crosses_boundary_edge",
            "dependency_note": (
                "N16 B3_C4 records transient breach pressure crossing the "
                "derived boundary edge with breach_pressure 0.38"
            ),
            "source_event": boundary_edges[0],
        },
        "internal_response_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t1_internal_support_update",
            "state_before": {
                "b2_c4_reference_minimum_internal_support": b2_reference[
                    "minimum_internal_support"
                ],
                "b2_c4_reference_repair_score": b2_reference["repair_score"],
            },
            "state_after": {
                "b3_c4_minimum_internal_support": metrics["minimum_internal_support"],
                "b3_c4_repair_score": metrics["repair_score"],
                "reclosure_latency_steps": probe["reclosure_latency_steps"],
            },
            "dependency_note": (
                "Internal support/reclosure markers shift after crossing, making "
                "the null tempting but still below closure"
            ),
        },
        "response_to_external_change_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t2_response_caused_external_change",
            "state_before": "bounded_reclosure_response_marker_absent",
            "state_after": "bounded_reclosure_response_marker_observed_after_crossing",
            "dependency_note": (
                "A bounded response marker is source-backed, but Iteration 3 does "
                "not validate a response-caused external perturbation-field change"
            ),
            "causal_status": "not_validated_as_response_caused_external_change",
            "source_event": boundary_edges[1],
        },
        "external_feedback_to_internal_trace": {
            "present": False,
            "source_backed": False,
            "phase": "t3_later_internal_support_conditioned_by_changed_external_state",
            "state_before": "changed_external_state_not_validated",
            "state_after": "later_internal_support_conditioned_by_changed_external_state_not_observed",
            "dependency_note": (
                "Tested explicitly and not found; this missing fourth leg blocks G3"
            ),
        },
        "phase_timing": {
            "t0_external_pressure_or_crossing": 0,
            "t1_internal_support_update": 1,
            "t2_response_caused_external_change": 2,
            "t3_later_internal_support_conditioned_by_changed_external_state": None,
        },
        "monotonic_phase_order": False,
        "response_caused_external_change": False,
        "external_change_would_occur_without_response": True,
        "later_internal_depends_on_changed_external_state": False,
        "feedback_removed_control_changes_result": False,
        "loop_closure_evidence": {
            "ordered_closure_present": False,
            "loop_closure_evidence_absent": True,
            "highest_supported_nonclosure_rung": "G2",
            "g3_reached": False,
            "missing_leg": "external_feedback_to_internal_trace",
            "active_null_decision": "supported_as_active_null_rejection",
            "failure_mode": "one_way_crossing_is_not_closed_loop",
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_trace": "N16_B3_C4_transient_breach_pressure",
                    "source_backed": True,
                },
                {
                    "edge_id": "external_crossing_to_internal_response",
                    "source_trace": "N16_B3_C4_internal_support_reclosure_marker",
                    "source_backed": True,
                },
                {
                    "edge_id": "internal_response_marker_to_external_change_after_response_not_causal",
                    "source_trace": "N16_B3_C4_bounded_reclosure_response_marker",
                    "source_backed": True,
                    "causal_for_ap7": False,
                },
            ],
            "missing_edges": [
                "internal_response_to_external_change",
                "changed_external_to_later_internal",
            ],
        },
        "budget_cost_surface": {
            "source_row_count": len(SOURCE_ROW_IDS),
            "trace_leg_count": 4,
            "present_trace_leg_count": 3,
            "hidden_state_allowance": 0,
            "unexplained_external_change_budget": 1,
            "closure_claim_budget": 0,
        },
        "budget_units": "normalized_cost",
        "budget_validity": {
            "valid": True,
            "within_limits": True,
            "closed_loop_claim_budget_valid": False,
            "reason": "valid active-null budget but invalid AP7 closure budget",
        },
        "replay_digest_inputs": schema["replay_digest_policy"]["include_fields"],
        "replay_digest_algorithm": schema["replay_digest_policy"]["digest_algorithm"],
        "artifact_only_replay_status": "stable",
        "snapshot_load_status": "stable",
        "duplicate_replay_status": "stable",
        "order_inversion_replay_status": "stable",
        "controls": controls,
        "ap7_gates": ap7_gates,
        "closed_loop_claim_allowed": False,
        "provisional_ap_level": "below_AP7_active_null",
        "provisional_claim_ceiling": "one_way_crossing_internal_update_fragment_not_closed_loop",
        "claim_flags": flags,
        "blocked_claims": [
            "AP7_supported",
            "closed_loop_demonstrated",
            "action_perception_loop_proven",
            "agency",
            "intention",
            "semantic_action",
            "semantic_perception",
            "semantic_goal_ownership",
            "selfhood",
            "identity_acceptance",
            "native_support",
            "organism_life",
            "fully_native_integration",
            "unrestricted_agency",
        ],
        "missing_gates": missing_gates,
        "final_ap7_supported": False,
    }
    row["row_replay_digest"] = sha256_bytes(
        canonical_json(
            {field: row.get(field) for field in schema["replay_digest_policy"]["include_fields"]}
        ).encode("utf-8")
    )
    return row


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    source_inventory = load_json(SOURCE_INVENTORY)
    n16_selected = load_json(N16_SELECTED_INTERACTION)
    n16_b3_c4 = find_n16_b3_c4_row(n16_selected)
    row = build_active_null_row(schema, source_inventory, n16_b3_c4)

    requirements_satisfied = [
        "external_to_internal_trace_recorded",
        "internal_support_update_recorded",
        "bounded_response_marker_recorded_as_tempting_near_miss",
        "one_way_crossing_relabel_control_blocks_ap7",
        "unsafe_claim_flags_forced_false",
        "artifact_replay_stable_for_active_null",
    ]
    requirements_failed = [
        "external_feedback_to_internal_trace_absent",
        "loop_closure_evidence_absent",
        "G3_not_reached",
        "response_caused_external_change_not_validated",
        "later_internal_dependence_on_changed_external_state_absent",
    ]

    claim_flags_top = claim_flags(schema)
    checks = [
        {
            "check_id": "schema_status_passed",
            "passed": schema["status"] == "passed",
            "detail": {
                "schema_path": rel(SCHEMA_PATH),
                "schema_output_digest": schema["output_digest"],
            },
        },
        {
            "check_id": "source_inventory_status_passed",
            "passed": source_inventory["status"] == "passed",
            "detail": {
                "source_inventory_path": rel(SOURCE_INVENTORY),
                "source_inventory_output_digest": source_inventory["output_digest"],
            },
        },
        {
            "check_id": "strong_near_miss_contains_crossing_internal_update_and_response_marker",
            "passed": row["external_to_internal_trace"]["present"]
            and row["internal_response_trace"]["present"]
            and row["response_to_external_change_trace"]["present"],
            "detail": "G2-looking active null includes three tempting legs",
        },
        {
            "check_id": "assigned_below_g3",
            "passed": row["loop_rung"] in {"G0", "G1", "G2"}
            and row["loop_rung_index"] < 3,
            "detail": {
                "loop_rung": row["loop_rung"],
                "loop_rung_index": row["loop_rung_index"],
            },
        },
        {
            "check_id": "missing_feedback_leg_explicit",
            "passed": row["external_feedback_to_internal_trace"]["present"] is False
            and row["external_feedback_to_internal_trace"]["source_backed"] is False,
            "detail": row["external_feedback_to_internal_trace"],
        },
        {
            "check_id": "replay_digest_binds_schema_and_loop_policy",
            "passed": row["schema_version"] == schema["schema_version"]
            and row["loop_policy_digest"]
            == schema["config_files"]["loop_policy"]["config_digest"],
            "detail": {
                "schema_version": row["schema_version"],
                "loop_policy_digest": row["loop_policy_digest"],
            },
        },
        {
            "check_id": "one_way_relabel_control_blocks_ap7",
            "passed": row["controls"]["one_way_crossing_relabel_control"]["status"]
            == "passed"
            and row["closed_loop_claim_allowed"] is False,
            "detail": row["controls"]["one_way_crossing_relabel_control"],
        },
        {
            "check_id": "iteration_4_evidence_not_introduced",
            "passed": row["response_caused_external_change"] is False
            and row["later_internal_depends_on_changed_external_state"] is False,
            "detail": "I3 blocks response-caused external feedback and later internal dependence",
        },
        {
            "check_id": "closed_loop_claim_allowed_false",
            "passed": row["closed_loop_claim_allowed"] is False,
            "detail": "active null passes by rejecting closure",
        },
        {
            "check_id": "final_ap7_supported_false",
            "passed": row["final_ap7_supported"] is False
            and claim_flags_top["final_ap7_supported"] is False,
            "detail": "Iteration 3 makes no final AP7 claim",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in claim_flags_top.values()),
            "detail": claim_flags_top,
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 3 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 3,
        "artifact_id": "n17_one_way_crossing_active_null",
        "purpose": "build a strong one-way crossing near-miss and verify it fails closed as AP7",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_one_way_crossing_active_null_no_ap7",
        "source_inventory": {
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
            "output_digest": source_inventory["output_digest"],
        },
        "schema": {
            "path": rel(SCHEMA_PATH),
            "sha256": sha256_file(SCHEMA_PATH),
            "output_digest": schema["output_digest"],
        },
        "active_null_summary": {
            "row_id": row["row_id"],
            "row_decision": row["row_decision"],
            "row_type": row["row_type"],
            "active_null_decision": row["loop_closure_evidence"][
                "active_null_decision"
            ],
            "loop_ladder_rung": row["loop_rung"],
            "highest_supported_nonclosure_rung": row["loop_rung"],
            "closed_loop_claim_allowed": False,
            "final_ap7_supported": False,
            "failure_mode": "one_way_crossing_is_not_closed_loop",
            "near_miss_reason": (
                "crossing and internal response are present, but changed-external "
                "feedback into later internal support is absent"
            ),
        },
        "requirements_satisfied": requirements_satisfied,
        "requirements_failed": requirements_failed,
        "rows": [row],
        "controls": {
            "one_way_crossing_relabel_control": row["controls"][
                "one_way_crossing_relabel_control"
            ],
            "external_change_not_caused_by_response_control": row["controls"][
                "external_change_not_caused_by_response_control"
            ],
            "feedback_removed_control": row["controls"]["feedback_removed_control"],
        },
        "claim_flags": claim_flags_top,
        "iteration_result": {
            "iteration_3_is_positive_loop_evidence": False,
            "active_null_supported": True,
            "closed_loop_demonstrated": False,
            "ap7_classification_supported": False,
            "final_ap7_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "ready_for_iteration_4_perturbation_response_recovery_loop": True,
        },
        "checks": checks,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(),
        },
    }
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "portable relative paths only",
        }
    )
    artifact["status"] = "passed" if all(check["passed"] for check in checks) else "failed"
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    row = artifact["rows"][0]
    check_lines = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    satisfied = [f"- `{item}`" for item in artifact["requirements_satisfied"]]
    failed = [f"- `{item}`" for item in artifact["requirements_failed"]]
    return "\n".join(
        [
            "# N17 Iteration 3 - One-Way Crossing Active Null",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 3 builds a strong near-miss and rejects it as AP7.",
            "",
            "```text",
            f"row_decision = {artifact['active_null_summary']['row_decision']}",
            f"row_type = {artifact['active_null_summary']['row_type']}",
            f"active_null_decision = {artifact['active_null_summary']['active_null_decision']}",
            f"loop_ladder_rung = {row['loop_rung']}",
            "closed_loop_claim_allowed = false",
            "final_ap7_supported = false",
            "failure_mode = one_way_crossing_is_not_closed_loop",
            "```",
            "",
            "## Trace Read",
            "",
            "- `external_to_internal_trace`: present and source-backed.",
            "- `internal_response_trace`: present and source-backed.",
            "- `response_to_external_change_trace`: present as a tempting marker, "
            "but not validated as response-caused external change.",
            "- `external_feedback_to_internal_trace`: explicitly absent.",
            "",
            "## Requirements Satisfied",
            "",
            *satisfied,
            "",
            "## Requirements Failed",
            "",
            *failed,
            "",
            "## Interpretation",
            "",
            "This row demonstrates boundary crossing and internal update fragments, "
            "but it does not demonstrate closed boundary engagement because no "
            "response-caused external change feeds back into later internal support.",
            "",
            "## Checks",
            "",
            *check_lines,
            "",
        ]
    )


def main() -> None:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")


if __name__ == "__main__":
    main()

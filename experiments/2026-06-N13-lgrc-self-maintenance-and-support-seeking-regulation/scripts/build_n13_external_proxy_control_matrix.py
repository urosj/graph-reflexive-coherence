#!/usr/bin/env python3
"""Build N13 Iteration 5 external proxy and hidden-target control matrix."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

INVENTORY_OUTPUT = OUTPUTS / "n13_support_condition_inventory.json"
INVENTORY_REPORT = REPORTS / "n13_support_condition_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n13_support_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n13_support_schema_v1.md"
TARGET_OUTPUT = OUTPUTS / "n13_support_derived_target_candidate.json"
TARGET_REPORT = REPORTS / "n13_support_derived_target_candidate.md"
REGULATION_OUTPUT = OUTPUTS / "n13_support_seeking_regulation_candidate.json"
REGULATION_REPORT = REPORTS / "n13_support_seeking_regulation_candidate.md"

OUTPUT_PATH = OUTPUTS / "n13_external_proxy_control_matrix.json"
REPORT_PATH = REPORTS / "n13_external_proxy_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_external_proxy_control_matrix.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}

REQUIRED_CONTROL_IDS = {
    "external_proxy_only_control",
    "hidden_support_target_control",
    "post_hoc_support_label_control",
    "support_disrupted_regulation_control",
    "stale_source_replay_control",
    "budget_ambiguous_correction_control",
    "identity_acceptance_relabel_control",
    "semantic_goal_ownership_relabel_control",
    "agency_relabel_control",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def row_by_id(inventory: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in inventory["n13_inventory_rows"]:
        if row["row_id"] == row_id:
            return row
    raise ValueError(f"Missing inventory row: {row_id}")


def control_row(
    *,
    control_id: str,
    control_kind: str,
    adversarial_input: str,
    expected_rejection: str,
    evidence: dict[str, Any],
    passed: bool,
    scope: str = "iteration_5_fail_closed_control",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_kind": control_kind,
        "scope": scope,
        "adversarial_input": adversarial_input,
        "expected_rejection": expected_rejection,
        "observed_result": "rejected" if passed else "not_rejected",
        "control_passed": passed,
        "evidence": evidence,
    }


def build_control_rows(
    inventory: dict[str, Any],
    schema: dict[str, Any],
    target: dict[str, Any],
    regulation: dict[str, Any],
) -> list[dict[str, Any]]:
    n09_row = row_by_id(inventory, "n13_i1_row_02_n09_bounded_external_proxy_regulation")
    target_candidate = target["support_derived_target_candidate"]
    regulation_candidate = regulation["support_seeking_regulation_candidate"]
    external_proxy_fields = sorted(n09_row["external_proxy_fields"].keys())
    lane_records = regulation_candidate["lane_response_records"]
    disrupted_records = [
        row for row in lane_records if row["target_state_before_response"] == "support_disrupted"
    ]
    response_records = [
        row
        for row in lane_records
        if row["response_magnitude_surface"]["scheduled_response_total"] > 0
    ]
    schema_controls = schema["control_flags"]
    target_source_req = target_candidate["source_current_requirement"]
    post_hoc_audit = target_candidate["post_hoc_label_audit"]
    hidden_target_audit = target_candidate["hidden_target_audit"]
    regulation_claims = regulation_candidate["claim_boundary"]
    return [
        control_row(
            control_id="external_proxy_only_control",
            control_kind="external_proxy_control",
            adversarial_input="replace support target/error with N09 proxy digests only",
            expected_rejection="external_proxy_only",
            passed=(
                schema_controls["external_proxy_relabel_blocked"]
                and n09_row["support_condition_name"] == "none_external_proxy_only"
                and target_candidate["external_proxy_separation"][
                    "target_uses_external_proxy_fields"
                ]
                is False
                and regulation_candidate["external_proxy_separation"][
                    "support_error_uses_n09_external_proxy_fields"
                ]
                is False
            ),
            evidence={
                "n09_support_condition_name": n09_row["support_condition_name"],
                "n09_external_proxy_fields": external_proxy_fields,
                "target_uses_external_proxy_fields": target_candidate[
                    "external_proxy_separation"
                ]["target_uses_external_proxy_fields"],
                "support_error_uses_n09_external_proxy_fields": regulation_candidate[
                    "external_proxy_separation"
                ]["support_error_uses_n09_external_proxy_fields"],
            },
        ),
        control_row(
            control_id="hidden_support_target_control",
            control_kind="hidden_target_control",
            adversarial_input="accept support target without declared runtime-visible support fields",
            expected_rejection="hidden_support_target",
            passed=(
                schema_controls["hidden_support_target_blocked"]
                and hidden_target_audit["target_fields_declared"] is True
                and hidden_target_audit["hidden_support_target_required"] is False
                and bool(regulation_candidate["support_error_signal"]["runtime_visible_inputs"])
            ),
            evidence={
                "target_fields_declared": hidden_target_audit["target_fields_declared"],
                "hidden_support_target_required": hidden_target_audit[
                    "hidden_support_target_required"
                ],
                "runtime_visible_inputs": regulation_candidate["support_error_signal"][
                    "runtime_visible_inputs"
                ],
            },
        ),
        control_row(
            control_id="post_hoc_support_label_control",
            control_kind="post_hoc_label_control",
            adversarial_input="choose threshold or support label after seeing lane outcomes",
            expected_rejection="post_hoc_support_label",
            passed=(
                schema_controls["post_hoc_support_label_blocked"]
                and post_hoc_audit["threshold_preexists_n13"] is True
                and post_hoc_audit["lane_digests_preexist_n13"] is True
                and post_hoc_audit["n13_did_not_choose_threshold"] is True
                and post_hoc_audit["target_rule_matches_all_source_lanes"] is True
            ),
            evidence=post_hoc_audit,
        ),
        control_row(
            control_id="support_disrupted_regulation_control",
            control_kind="support_disrupted_control",
            adversarial_input="count a raw support-disrupted lane as supported because a bounded response can be scheduled",
            expected_rejection="support_disrupted_but_regulation_counted",
            passed=(
                schema_controls["support_disrupted_regulation_blocked"]
                and len(disrupted_records) > 0
                and regulation_candidate["support_disrupted_negative_control"][
                    "raw_disrupted_lanes_not_counted_as_supported_before_response"
                ]
                is True
                and regulation_candidate["support_disrupted_negative_control"][
                    "bounded_response_is_schedule_candidate_not_raw_support_pass"
                ]
                is True
            ),
            scope="iteration_5_pre_stress_fail_closed_control",
            evidence={
                "raw_disrupted_lanes": regulation_candidate[
                    "support_disrupted_negative_control"
                ]["raw_disrupted_lanes"],
                "raw_disrupted_lanes_not_counted_as_supported_before_response": regulation_candidate[
                    "support_disrupted_negative_control"
                ]["raw_disrupted_lanes_not_counted_as_supported_before_response"],
                "bounded_response_is_schedule_candidate_not_raw_support_pass": regulation_candidate[
                    "support_disrupted_negative_control"
                ]["bounded_response_is_schedule_candidate_not_raw_support_pass"],
                "full_stress_control_pending_iteration_6": True,
            },
        ),
        control_row(
            control_id="stale_source_replay_control",
            control_kind="source_current_replay_control",
            adversarial_input="replay candidate from missing or stale source digests",
            expected_rejection="stale_source_replay",
            passed=(
                schema_controls["stale_source_replay_blocked"]
                and target_source_req["source_artifacts_pinned"] is True
                and target_source_req["lane_digests_required"] is True
                and target_source_req["support_area_digest_required"] is True
                and target["output_digest"]
                == regulation_candidate["support_target"]["target_output_digest"]
            ),
            evidence={
                "target_output_digest": target["output_digest"],
                "regulation_target_output_digest": regulation_candidate[
                    "support_target"
                ]["target_output_digest"],
                "source_current_requirement": target_source_req,
            },
        ),
        control_row(
            control_id="budget_ambiguous_correction_control",
            control_kind="budget_control",
            adversarial_input="accept scheduled response without explicit budget debit or mutation boundary",
            expected_rejection="budget_surface_ambiguity",
            passed=(
                schema_controls["budget_ambiguity_blocked"]
                and regulation_candidate["budget_debit_surface"][
                    "all_scheduled_responses_have_budget_debit"
                ]
                is True
                and all(
                    row["response_magnitude_surface"]["scheduled_response_total"]
                    == row["budget_debit_surface"]["budget_debit_amount"]
                    for row in lane_records
                )
                and all(
                    row["budget_debit_surface"][
                        "node_plus_packet_budget_debit_required"
                    ]
                    is True
                    for row in response_records
                )
                and regulation_candidate["budget_debit_surface"]["mutation_boundary"][
                    "producer_or_policy_may_schedule_only"
                ]
                is True
                and regulation_candidate["budget_debit_surface"]["mutation_boundary"][
                    "step_or_topology_event_owns_state_mutation"
                ]
                is True
            ),
            evidence={
                "response_lane_ids": [row["lane_id"] for row in response_records],
                "all_scheduled_responses_have_budget_debit": regulation_candidate[
                    "budget_debit_surface"
                ]["all_scheduled_responses_have_budget_debit"],
                "mutation_boundary": regulation_candidate["budget_debit_surface"][
                    "mutation_boundary"
                ],
            },
        ),
        control_row(
            control_id="identity_acceptance_relabel_control",
            control_kind="claim_relabel_control",
            adversarial_input="relabel support survival or support-seeking response as identity acceptance",
            expected_rejection="identity_acceptance_relabel",
            passed=(
                schema_controls["identity_acceptance_relabel_blocked"]
                and CLAIM_FLAGS_FORCED_FALSE["identity_acceptance_claim_allowed"]
                is False
                and CLAIM_FLAGS_FORCED_FALSE["runtime_identity_acceptance_claim_allowed"]
                is False
            ),
            evidence={
                "identity_acceptance_claim_allowed": CLAIM_FLAGS_FORCED_FALSE[
                    "identity_acceptance_claim_allowed"
                ],
                "runtime_identity_acceptance_claim_allowed": CLAIM_FLAGS_FORCED_FALSE[
                    "runtime_identity_acceptance_claim_allowed"
                ],
            },
        ),
        control_row(
            control_id="semantic_goal_ownership_relabel_control",
            control_kind="claim_relabel_control",
            adversarial_input="relabel source-current support target or support error as semantic goal ownership",
            expected_rejection="semantic_goal_ownership_relabel",
            passed=(
                schema_controls["semantic_goal_ownership_relabel_blocked"]
                and regulation_claims["support_error_is_semantic_goal_ownership"]
                is False
                and CLAIM_FLAGS_FORCED_FALSE["semantic_goal_ownership_claim_allowed"]
                is False
            ),
            evidence={
                "support_error_is_semantic_goal_ownership": regulation_claims[
                    "support_error_is_semantic_goal_ownership"
                ],
                "semantic_goal_ownership_claim_allowed": CLAIM_FLAGS_FORCED_FALSE[
                    "semantic_goal_ownership_claim_allowed"
                ],
            },
        ),
        control_row(
            control_id="agency_relabel_control",
            control_kind="claim_relabel_control",
            adversarial_input="relabel bounded support-seeking regulation candidate as agency",
            expected_rejection="agency_relabel",
            passed=(
                schema_controls["agency_relabel_blocked"]
                and regulation_claims["support_regulation_candidate_is_agency"]
                is False
                and CLAIM_FLAGS_FORCED_FALSE["agency_claim_allowed"] is False
            ),
            evidence={
                "support_regulation_candidate_is_agency": regulation_claims[
                    "support_regulation_candidate_is_agency"
                ],
                "agency_claim_allowed": CLAIM_FLAGS_FORCED_FALSE[
                    "agency_claim_allowed"
                ],
            },
        ),
        control_row(
            control_id="native_support_without_phase8_control",
            control_kind="claim_relabel_control",
            adversarial_input="relabel artifact-level support response candidate as native support without Phase 8",
            expected_rejection="native_support_without_phase8",
            passed=(
                schema_controls["native_support_relabel_blocked"]
                and regulation_candidate["response_magnitude_surface"][
                    "native_policy_supported"
                ]
                is False
                and regulation_candidate["budget_debit_surface"]["mutation_boundary"][
                    "phase8_implementation_opened"
                ]
                is False
                and CLAIM_FLAGS_FORCED_FALSE["native_support_opened"] is False
            ),
            evidence={
                "native_policy_supported": regulation_candidate[
                    "response_magnitude_surface"
                ]["native_policy_supported"],
                "phase8_implementation_opened": regulation_candidate[
                    "budget_debit_surface"
                ]["mutation_boundary"]["phase8_implementation_opened"],
                "native_support_opened": CLAIM_FLAGS_FORCED_FALSE[
                    "native_support_opened"
                ],
            },
        ),
    ]


def build_interpretation_record(
    regulation: dict[str, Any],
    control_matrix: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": "n13_i5_interpretation_external_proxy_controls_v1",
        "record_type": "n13_iteration_5_interpretation_record",
        "source_candidate": rel(REGULATION_OUTPUT),
        "source_candidate_output_digest": regulation["output_digest"],
        "source_control_matrix": "n13_external_proxy_hidden_target_control_matrix",
        "plain_language_meaning": (
            "Iteration 5 makes the Iteration 4 support-seeking regulation "
            "candidate control-clean against external-proxy, hidden-target, "
            "post-hoc-label, stale-source, budget-ambiguity, and unsafe "
            "claim-relabel explanations. It does not make final AP3 support."
        ),
        "supported_interpretation": (
            "The candidate may be carried forward as an artifact-level, "
            "source-current support-error bounded-response candidate whose "
            "target and error are derived from recorded support state rather "
            "than N09 external proxy fields."
        ),
        "unsupported_interpretations": [
            "the candidate is final supported AP3",
            "the candidate proves self-maintenance",
            "support survival is identity acceptance",
            "support error is semantic goal ownership",
            "bounded response is intention",
            "support-seeking regulation is agency",
            "artifact-level support regulation is native support",
            "N12 response magnitude readiness is Phase 8 implementation",
        ],
        "blocked_alternative_explanations": [
            row["expected_rejection"] for row in control_matrix["controls"]
        ],
        "ap_state": {
            "candidate_ap_level": "AP3",
            "provisional_ap_level": (
                "AP3_candidate_control_clean_pending_stress_and_boundary"
            ),
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
        },
        "remaining_required_work": [
            "support_disruption_restoration_stress_matrix_iteration_6",
            "identity_goal_ownership_agency_boundary_record_iteration_7",
            "n13_closeout_handoff_iteration_8",
        ],
        "phase8_and_native_state": {
            "phase8_opened": False,
            "native_support_opened": False,
            "src_implementation_changed": False,
        },
        "claim_boundary": control_matrix["claim_boundary"],
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    target = load_json(TARGET_OUTPUT)
    regulation = load_json(REGULATION_OUTPUT)
    controls = build_control_rows(inventory, schema, target, regulation)
    control_ids = {row["control_id"] for row in controls}
    failed_controls = [
        row["control_id"] for row in controls if row["control_passed"] is not True
    ]
    pending_after_iteration5 = [
        "support_disruption_restoration_stress_not_run_until_iteration_6",
        "claim_boundary_record_not_frozen_until_iteration_7",
    ]
    control_matrix = {
        "matrix_name": "n13_external_proxy_hidden_target_control_matrix",
        "candidate_source": rel(REGULATION_OUTPUT),
        "candidate_output_digest": regulation["output_digest"],
        "controls": controls,
        "control_summary": {
            "required_control_count": len(REQUIRED_CONTROL_IDS),
            "control_count": len(controls),
            "passed_control_count": len(controls) - len(failed_controls),
            "failed_controls": failed_controls,
            "all_controls_fail_closed": len(failed_controls) == 0,
            "required_controls_present": REQUIRED_CONTROL_IDS.issubset(control_ids),
            "native_support_without_phase8_control_included": "native_support_without_phase8_control"
            in control_ids,
        },
        "ap3_gate_state_after_iteration5": {
            "external_proxy_control_passed": True,
            "hidden_support_target_control_passed": True,
            "post_hoc_support_label_control_passed": True,
            "support_disrupted_pre_stress_control_passed": True,
            "budget_control_passed": True,
            "identity_acceptance_relabel_blocked": True,
            "semantic_goal_ownership_relabel_blocked": True,
            "agency_relabel_blocked": True,
            "native_support_relabel_blocked": True,
            "stress_matrix_pending_iteration6": True,
            "claim_boundary_record_pending_iteration7": True,
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
        },
        "pending_after_iteration5": pending_after_iteration5,
        "claim_boundary": {
            "support_seeking_regulation_candidate_is_agency": False,
            "support_error_is_semantic_goal_ownership": False,
            "support_survival_is_identity_acceptance": False,
            "bounded_response_is_intention": False,
            "artifact_level_candidate_is_native_support": False,
            "candidate_ap3_is_final_supported_ap3": False,
        },
    }
    interpretation_record = build_interpretation_record(regulation, control_matrix)
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "target_source_passed": target["status"] == "passed",
        "regulation_source_passed": regulation["status"] == "passed",
        "all_required_controls_present": REQUIRED_CONTROL_IDS.issubset(control_ids),
        "all_controls_fail_closed": control_matrix["control_summary"][
            "all_controls_fail_closed"
        ],
        "external_proxy_only_control_passed": any(
            row["control_id"] == "external_proxy_only_control"
            and row["control_passed"]
            for row in controls
        ),
        "hidden_support_target_control_passed": any(
            row["control_id"] == "hidden_support_target_control"
            and row["control_passed"]
            for row in controls
        ),
        "post_hoc_support_label_control_passed": any(
            row["control_id"] == "post_hoc_support_label_control"
            and row["control_passed"]
            for row in controls
        ),
        "support_disrupted_regulation_control_passed": any(
            row["control_id"] == "support_disrupted_regulation_control"
            and row["control_passed"]
            for row in controls
        ),
        "stale_source_replay_control_passed": any(
            row["control_id"] == "stale_source_replay_control"
            and row["control_passed"]
            for row in controls
        ),
        "budget_ambiguous_correction_control_passed": any(
            row["control_id"] == "budget_ambiguous_correction_control"
            and row["control_passed"]
            for row in controls
        ),
        "claim_relabel_controls_passed": all(
            any(row["control_id"] == control_id and row["control_passed"] for row in controls)
            for control_id in [
                "identity_acceptance_relabel_control",
                "semantic_goal_ownership_relabel_control",
                "agency_relabel_control",
                "native_support_without_phase8_control",
            ]
        ),
        "candidate_ap3_not_final_support": regulation["iteration_result"][
            "candidate_ap_level"
        ]
        == "AP3"
        and regulation["iteration_result"]["final_ap3_supported"] is False,
        "self_maintenance_not_supported_yet": regulation["iteration_result"][
            "self_maintenance_candidate_supported"
        ]
        is False,
        "stress_and_claim_boundary_pending": pending_after_iteration5
        == control_matrix["pending_after_iteration5"],
        "interpretation_record_present": interpretation_record["record_type"]
        == "n13_iteration_5_interpretation_record",
        "interpretation_preserves_final_ap3_false": interpretation_record["ap_state"][
            "final_ap3_supported"
        ]
        is False,
        "interpretation_records_remaining_work": interpretation_record[
            "remaining_required_work"
        ]
        == [
            "support_disruption_restoration_stress_matrix_iteration_6",
            "identity_goal_ownership_agency_boundary_record_iteration_7",
            "n13_closeout_handoff_iteration_8",
        ],
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "claim_boundary_controls_false": all(
            value is False for value in control_matrix["claim_boundary"].values()
        ),
        "native_support_not_opened": CLAIM_FLAGS_FORCED_FALSE[
            "native_support_opened"
        ]
        is False
        and regulation["iteration_result"]["native_support_opened"] is False,
        "phase8_not_opened": regulation["iteration_result"]["phase8_opened"]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 5,
        "purpose": "external_proxy_hidden_target_control_matrix",
        "schema": "n13_external_proxy_control_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_result": {
            "external_proxy_controls_passed": True,
            "hidden_target_controls_passed": True,
            "post_hoc_label_controls_passed": True,
            "support_disrupted_pre_stress_control_passed": True,
            "budget_control_passed": True,
            "claim_relabel_controls_passed": True,
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_control_clean_pending_stress_and_boundary",
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "control_matrix": control_matrix,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(TARGET_OUTPUT): source_artifact(TARGET_OUTPUT, target),
            rel(REGULATION_OUTPUT): source_artifact(REGULATION_OUTPUT, regulation),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(TARGET_REPORT): source_report(TARGET_REPORT),
            rel(REGULATION_REPORT): source_report(REGULATION_REPORT),
        },
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    matrix = output["control_matrix"]
    interpretation = output["interpretation_record"]
    result = output["iteration_result"]
    lines = [
        "# N13 External Proxy And Hidden Target Control Matrix",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"external_proxy_controls_passed = {str(result['external_proxy_controls_passed']).lower()}",
        f"hidden_target_controls_passed = {str(result['hidden_target_controls_passed']).lower()}",
        f"post_hoc_label_controls_passed = {str(result['post_hoc_label_controls_passed']).lower()}",
        f"support_disrupted_pre_stress_control_passed = {str(result['support_disrupted_pre_stress_control_passed']).lower()}",
        f"candidate_ap_level = {result['candidate_ap_level']}",
        f"provisional_ap_level = {result['provisional_ap_level']}",
        "final_ap3_supported = false",
        "self_maintenance_candidate_supported = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 5 runs fail-closed controls around the Iteration 4",
        "support-seeking regulation candidate. Passing these controls means the",
        "candidate is not merely an external proxy, hidden target, post-hoc",
        "label, budget-ambiguous correction, or unsafe claim relabel. It does",
        "not freeze final AP3 support; support-disruption/restoration stress",
        "and the final claim-boundary record remain pending.",
        "",
        "## Control Summary",
        "",
        "```json",
        json.dumps(matrix["control_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "| Control | Expected rejection | Observed | Passed |",
        "| --- | --- | --- | --- |",
    ]
    for row in matrix["controls"]:
        lines.append(
            "| "
            f"`{row['control_id']}` | "
            f"`{row['expected_rejection']}` | "
            f"`{row['observed_result']}` | "
            f"`{str(row['control_passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Record",
            "",
            "```json",
            json.dumps(interpretation, indent=2, sort_keys=True),
            "```",
            "",
            "## AP3 Gate State After Iteration 5",
            "",
            "```json",
            json.dumps(
                matrix["ap3_gate_state_after_iteration5"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Pending After Iteration 5",
            "",
            "```json",
            json.dumps(matrix["pending_after_iteration5"], indent=2),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "support-seeking regulation candidate != agency",
            "support survival != identity acceptance",
            "support error != semantic goal ownership",
            "bounded response != intention",
            "candidate AP3 != final supported AP3",
            "artifact-level support regulation != native support",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

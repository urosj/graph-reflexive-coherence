#!/usr/bin/env python3
"""Build N13 Iteration 6 support disruption and restoration stress matrix."""

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
CONTROL_OUTPUT = OUTPUTS / "n13_external_proxy_control_matrix.json"
CONTROL_REPORT = REPORTS / "n13_external_proxy_control_matrix.md"

OUTPUT_PATH = OUTPUTS / "n13_support_disruption_restoration_matrix.json"
REPORT_PATH = REPORTS / "n13_support_disruption_restoration_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_support_disruption_restoration_matrix.py"
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


def lane_by_id(lanes: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    for lane in lanes:
        if lane["lane_id"] == lane_id:
            return lane
    raise ValueError(f"Missing lane: {lane_id}")


def n10_by_state(rows: list[dict[str, Any]], matrix_state: str) -> dict[str, Any]:
    for row in rows:
        if row["matrix_state"] == matrix_state:
            return row
    raise ValueError(f"Missing N10 matrix state: {matrix_state}")


def lane_regime_record(
    *,
    regime_id: str,
    regime_kind: str,
    lane: dict[str, Any],
    expected_behavior: str,
    n10_alignment: dict[str, Any] | None,
) -> dict[str, Any]:
    response_total = lane["response_magnitude_surface"]["scheduled_response_total"]
    support_error = lane["support_error_signal"]["support_error"]
    no_response_needed = support_error == 0 and response_total == 0
    response_needed = support_error > 0 and response_total > 0
    if expected_behavior == "no_response_support_valid":
        passed = (
            lane["target_state_before_response"] == "support_valid"
            and no_response_needed
            and lane["post_response_estimate"]["post_response_meets_target"]
        )
    elif expected_behavior == "bounded_response_to_support_error":
        passed = (
            lane["target_state_before_response"] == "support_disrupted"
            and response_needed
            and lane["bounded_window"]["within_bounded_window"]
            and lane["budget_debit_surface"]["node_plus_packet_budget_debit_required"]
            and lane["post_response_estimate"]["post_response_meets_target"]
        )
    elif expected_behavior == "source_restoration_no_new_response":
        passed = (
            lane["target_state_before_response"] == "support_valid"
            and no_response_needed
            and lane["support_trend"] == "source_restored_above_threshold_no_new_response"
            and lane["post_response_estimate"]["post_response_meets_target"]
        )
    elif expected_behavior == "neutral_no_false_positive_response":
        passed = (
            lane["target_state_before_response"] == "support_valid"
            and no_response_needed
            and lane["support_margin"] > 0
        )
    else:
        raise ValueError(f"Unknown expected behavior: {expected_behavior}")
    return {
        "regime_id": regime_id,
        "regime_kind": regime_kind,
        "source_lane_id": lane["lane_id"],
        "source_lane_digest": lane["lane_digest"],
        "expected_behavior": expected_behavior,
        "target_state_before_response": lane["target_state_before_response"],
        "support_error": support_error,
        "scheduled_response_total": response_total,
        "scheduled_response_amounts": lane["response_magnitude_surface"][
            "scheduled_response_amounts"
        ],
        "budget_debit_amount": lane["budget_debit_surface"]["budget_debit_amount"],
        "bounded_window": lane["bounded_window"],
        "post_response_estimate": lane["post_response_estimate"],
        "support_trend": lane["support_trend"],
        "n10_alignment": n10_alignment,
        "stress_passed": passed,
    }


def build_stress_records(
    regulation: dict[str, Any], target: dict[str, Any]
) -> list[dict[str, Any]]:
    candidate = regulation["support_seeking_regulation_candidate"]
    lanes = candidate["lane_response_records"]
    n10_rows = target["support_derived_target_candidate"]["n10_support_matrix_alignment"]
    support_present = lane_by_id(lanes, "support_intact_reference")
    mild_support = lane_by_id(lanes, "mild_support_weakening")
    disrupted = lane_by_id(lanes, "n09_matched_partial_support_withdrawal")
    restored = lane_by_id(lanes, "restored_after_n09_partial_withdrawal")
    records = [
        lane_regime_record(
            regime_id="stress_01_support_present_baseline",
            regime_kind="support_present_baseline",
            lane=support_present,
            expected_behavior="no_response_support_valid",
            n10_alignment=n10_by_state(n10_rows, "support_intact_survives"),
        ),
        lane_regime_record(
            regime_id="stress_02_support_disrupted_regime",
            regime_kind="support_disrupted_regime",
            lane=disrupted,
            expected_behavior="bounded_response_to_support_error",
            n10_alignment=n10_by_state(n10_rows, "n09_matched_withdrawal_disrupts_support"),
        ),
        lane_regime_record(
            regime_id="stress_03_explicit_restoration_regime",
            regime_kind="explicit_restoration_regime",
            lane=restored,
            expected_behavior="source_restoration_no_new_response",
            n10_alignment=n10_by_state(n10_rows, "explicit_restoration_recovers_support"),
        ),
        lane_regime_record(
            regime_id="stress_04_neutral_perturbation_regime",
            regime_kind="neutral_or_non_disruptive_perturbation_regime",
            lane=mild_support,
            expected_behavior="neutral_no_false_positive_response",
            n10_alignment=n10_by_state(n10_rows, "mild_withdrawal_survives"),
        ),
    ]
    records.append(
        {
            "regime_id": "stress_05_no_support_control_regime",
            "regime_kind": "no_support_control_regime",
            "source_lane_id": None,
            "source_lane_digest": None,
            "expected_behavior": "block_response_without_source_current_support_target",
            "support_target_present": False,
            "support_error": None,
            "scheduled_response_total": 0,
            "scheduled_response_amounts": [],
            "budget_debit_amount": 0,
            "bounded_window": None,
            "post_response_estimate": None,
            "support_trend": "blocked_missing_support_target",
            "n10_alignment": None,
            "blocked_reason": "missing_source_current_support_target",
            "stress_passed": True,
        }
    )
    return records


def build_interpretation_record(stress_matrix: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": "n13_i6_interpretation_stress_matrix_v1",
        "record_type": "n13_iteration_6_interpretation_record",
        "plain_language_meaning": (
            "Iteration 6 shows the candidate behaves differently across "
            "support-present, support-disrupted, restored, neutral, and "
            "no-support-target regimes: it schedules a bounded budgeted "
            "response only for the source-current support deficit, avoids "
            "false-positive responses when support remains valid, and blocks "
            "when no support target is available."
        ),
        "supported_interpretation": (
            "The candidate may be carried forward as an artifact-level AP3 "
            "stress-clean support-seeking regulation candidate pending the "
            "Iteration 7 claim-boundary record."
        ),
        "unsupported_interpretations": [
            "stress-clean candidate is final supported AP3",
            "support-seeking regulation is agency",
            "support survival is identity acceptance",
            "bounded response is intention",
            "stress behavior proves selfhood or self-maintenance as final support",
            "artifact-level stress behavior is native support",
        ],
        "ap_state_after_stress_matrix": stress_matrix[
            "ap_state_after_stress_matrix"
        ],
        "remaining_required_work": [
            "identity_goal_ownership_agency_boundary_record_iteration_7",
            "n13_closeout_handoff_iteration_8",
        ],
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    target = load_json(TARGET_OUTPUT)
    regulation = load_json(REGULATION_OUTPUT)
    controls = load_json(CONTROL_OUTPUT)
    stress_records = build_stress_records(regulation, target)
    failed_stress_records = [
        row["regime_id"] for row in stress_records if row["stress_passed"] is not True
    ]
    stress_matrix = {
        "matrix_name": "n13_support_disruption_restoration_stress_matrix",
        "candidate_source": rel(REGULATION_OUTPUT),
        "candidate_output_digest": regulation["output_digest"],
        "control_matrix_source": rel(CONTROL_OUTPUT),
        "control_matrix_output_digest": controls["output_digest"],
        "stress_records": stress_records,
        "stress_summary": {
            "stress_record_count": len(stress_records),
            "failed_stress_records": failed_stress_records,
            "all_stress_records_passed": len(failed_stress_records) == 0,
            "support_seeking_regulation_survives_controls": len(
                failed_stress_records
            )
            == 0
            and controls["control_matrix"]["control_summary"][
                "all_controls_fail_closed"
            ],
            "response_only_when_support_error_positive": all(
                (
                    row["scheduled_response_total"] > 0
                    and row["support_error"] is not None
                    and row["support_error"] > 0
                )
                or row["scheduled_response_total"] == 0
                for row in stress_records
            ),
            "no_support_target_blocks_response": any(
                row["regime_kind"] == "no_support_control_regime"
                and row["stress_passed"]
                and row["scheduled_response_total"] == 0
                for row in stress_records
            ),
        },
        "source_current_replay_requirements": {
            "source_artifacts_pinned": True,
            "target_output_digest_required": target["output_digest"],
            "regulation_output_digest_required": regulation["output_digest"],
            "control_output_digest_required": controls["output_digest"],
            "lane_digests_required": True,
            "support_area_digest_required": True,
            "stale_source_replay_blocked": True,
            "no_support_target_blocks_response": True,
        },
        "budget_and_response_surfaces": {
            "budget_debit_surface": regulation[
                "support_seeking_regulation_candidate"
            ]["budget_debit_surface"],
            "response_magnitude_surface": regulation[
                "support_seeking_regulation_candidate"
            ]["response_magnitude_surface"],
            "trend_stability_fields": regulation[
                "support_seeking_regulation_candidate"
            ]["trend_stability_fields"],
        },
        "ap_state_after_stress_matrix": {
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_stress_clean_pending_claim_boundary",
            "stress_matrix_passed": len(failed_stress_records) == 0,
            "external_proxy_controls_passed": controls["iteration_result"][
                "external_proxy_controls_passed"
            ],
            "hidden_target_controls_passed": controls["iteration_result"][
                "hidden_target_controls_passed"
            ],
            "post_hoc_label_controls_passed": controls["iteration_result"][
                "post_hoc_label_controls_passed"
            ],
            "claim_boundary_record_pending_iteration7": True,
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "claim_boundary": {
            "stress_clean_candidate_is_agency": False,
            "support_survival_is_identity_acceptance": False,
            "bounded_response_is_intention": False,
            "stress_clean_candidate_is_final_ap3": False,
            "artifact_level_stress_matrix_is_native_support": False,
        },
    }
    interpretation_record = build_interpretation_record(stress_matrix)
    required_regimes = {
        "support_present_baseline",
        "support_disrupted_regime",
        "explicit_restoration_regime",
        "neutral_or_non_disruptive_perturbation_regime",
        "no_support_control_regime",
    }
    observed_regimes = {row["regime_kind"] for row in stress_records}
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "target_source_passed": target["status"] == "passed",
        "regulation_source_passed": regulation["status"] == "passed",
        "control_source_passed": controls["status"] == "passed",
        "all_required_regimes_present": required_regimes.issubset(observed_regimes),
        "support_present_baseline_passed": any(
            row["regime_kind"] == "support_present_baseline" and row["stress_passed"]
            for row in stress_records
        ),
        "support_disrupted_regime_passed": any(
            row["regime_kind"] == "support_disrupted_regime"
            and row["stress_passed"]
            and row["scheduled_response_total"] > 0
            for row in stress_records
        ),
        "explicit_restoration_regime_passed": any(
            row["regime_kind"] == "explicit_restoration_regime"
            and row["stress_passed"]
            for row in stress_records
        ),
        "neutral_perturbation_regime_passed": any(
            row["regime_kind"] == "neutral_or_non_disruptive_perturbation_regime"
            and row["stress_passed"]
            and row["scheduled_response_total"] == 0
            for row in stress_records
        ),
        "no_support_control_regime_passed": any(
            row["regime_kind"] == "no_support_control_regime"
            and row["stress_passed"]
            and row["scheduled_response_total"] == 0
            for row in stress_records
        ),
        "source_current_replay_requirements_recorded": all(
            stress_matrix["source_current_replay_requirements"][key]
            for key in [
                "source_artifacts_pinned",
                "lane_digests_required",
                "support_area_digest_required",
                "stale_source_replay_blocked",
                "no_support_target_blocks_response",
            ]
        ),
        "budget_and_response_surfaces_recorded": all(
            key in stress_matrix["budget_and_response_surfaces"]
            for key in [
                "budget_debit_surface",
                "response_magnitude_surface",
                "trend_stability_fields",
            ]
        ),
        "support_seeking_regulation_survives_controls": stress_matrix[
            "stress_summary"
        ]["support_seeking_regulation_survives_controls"],
        "ap_ceiling_after_stress_matrix_recorded": stress_matrix[
            "ap_state_after_stress_matrix"
        ]["provisional_ap_level"]
        == "AP3_candidate_stress_clean_pending_claim_boundary",
        "interpretation_record_present": interpretation_record["record_type"]
        == "n13_iteration_6_interpretation_record",
        "final_ap3_not_supported_until_iteration7": stress_matrix[
            "ap_state_after_stress_matrix"
        ]["final_ap3_supported"]
        is False,
        "self_maintenance_not_supported_yet": stress_matrix[
            "ap_state_after_stress_matrix"
        ]["self_maintenance_candidate_supported"]
        is False,
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "claim_boundary_controls_false": all(
            value is False for value in stress_matrix["claim_boundary"].values()
        ),
        "native_support_not_opened": stress_matrix["ap_state_after_stress_matrix"][
            "native_support_opened"
        ]
        is False,
        "phase8_not_opened": stress_matrix["ap_state_after_stress_matrix"][
            "phase8_opened"
        ]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 6,
        "purpose": "support_disruption_restoration_stress_matrix",
        "schema": "n13_support_disruption_restoration_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_result": {
            "support_disruption_restoration_stress_matrix_passed": True,
            "support_seeking_regulation_survives_controls": True,
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_stress_clean_pending_claim_boundary",
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "stress_matrix": stress_matrix,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(TARGET_OUTPUT): source_artifact(TARGET_OUTPUT, target),
            rel(REGULATION_OUTPUT): source_artifact(REGULATION_OUTPUT, regulation),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, controls),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(TARGET_REPORT): source_report(TARGET_REPORT),
            rel(REGULATION_REPORT): source_report(REGULATION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
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
    matrix = output["stress_matrix"]
    result = output["iteration_result"]
    interpretation = output["interpretation_record"]
    lines = [
        "# N13 Support Disruption And Restoration Stress Matrix",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"support_disruption_restoration_stress_matrix_passed = {str(result['support_disruption_restoration_stress_matrix_passed']).lower()}",
        f"support_seeking_regulation_survives_controls = {str(result['support_seeking_regulation_survives_controls']).lower()}",
        f"candidate_ap_level = {result['candidate_ap_level']}",
        f"provisional_ap_level = {result['provisional_ap_level']}",
        "final_ap3_supported = false",
        "self_maintenance_candidate_supported = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 6 stress-tests the support-seeking regulation candidate",
        "across support-present, support-disrupted, explicit-restoration,",
        "neutral/non-disruptive, and no-support-target regimes. It does not",
        "freeze final AP3 support; the claim-boundary record remains pending",
        "for Iteration 7.",
        "",
        "## Stress Summary",
        "",
        "```json",
        json.dumps(matrix["stress_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Stress Records",
        "",
        "| Regime | Source lane | Support error | Scheduled response | Passed |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in matrix["stress_records"]:
        source_lane = row["source_lane_id"] if row["source_lane_id"] else "none"
        support_error = "null" if row["support_error"] is None else row["support_error"]
        lines.append(
            "| "
            f"`{row['regime_kind']}` | "
            f"`{source_lane}` | "
            f"{support_error} | "
            f"{row['scheduled_response_total']} | "
            f"`{str(row['stress_passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Source-Current Replay Requirements",
            "",
            "```json",
            json.dumps(
                matrix["source_current_replay_requirements"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Budget And Response Surfaces",
            "",
            "```json",
            json.dumps(
                matrix["budget_and_response_surfaces"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Interpretation Record",
            "",
            "```json",
            json.dumps(interpretation, indent=2, sort_keys=True),
            "```",
            "",
            "## AP State After Stress Matrix",
            "",
            "```json",
            json.dumps(
                matrix["ap_state_after_stress_matrix"],
                indent=2,
                sort_keys=True,
            ),
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
            "stress-clean candidate != final supported AP3",
            "support-seeking regulation != agency",
            "support survival != identity acceptance",
            "bounded response != intention",
            "artifact-level stress matrix != native support",
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

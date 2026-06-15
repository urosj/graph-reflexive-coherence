#!/usr/bin/env python3
"""Build N13 Iteration 4 support-seeking regulation candidate."""

from __future__ import annotations

import hashlib
import json
import math
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

N12_RESPONSE_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "outputs"
    / "n12_response_magnitude_candidate.json"
)
N12_RESPONSE_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "reports"
    / "n12_response_magnitude_candidate.md"
)
N12_PHASE8_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "outputs"
    / "n12_phase8_readiness_matrix.json"
)
N12_PHASE8_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "reports"
    / "n12_phase8_readiness_matrix.md"
)

OUTPUT_PATH = OUTPUTS / "n13_support_seeking_regulation_candidate.json"
REPORT_PATH = REPORTS / "n13_support_seeking_regulation_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_support_seeking_regulation_candidate.py"
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

PENDING_CONTROLS = [
    "external_proxy_controls_not_run_until_iteration_5",
    "hidden_target_controls_not_run_until_iteration_5",
    "post_hoc_label_controls_not_run_until_iteration_5",
    "support_disruption_restoration_stress_not_run_until_iteration_6",
    "claim_boundary_record_not_frozen_until_iteration_7",
]


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


def rounded(value: float) -> float:
    return round(value, 12)


def response_schedule(error: float, max_correction: float) -> list[float]:
    remaining = error
    schedule: list[float] = []
    while remaining > 1e-12:
        amount = min(remaining, max_correction)
        schedule.append(rounded(amount))
        remaining = rounded(remaining - amount)
    return schedule


def trend_for_lane(lane: dict[str, Any], support_error: float) -> str:
    if lane["restoration_fraction"] > 0 and lane["target_state"] == "support_valid":
        return "source_restored_above_threshold_no_new_response"
    if support_error > 0:
        return "bounded_correction_needed"
    if lane["withdrawal_depth"] > 0:
        return "mild_support_above_threshold_no_response"
    return "stable_above_threshold_no_response"


def build_lane_response_records(
    lanes: list[dict[str, Any]],
    response_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    max_correction = response_policy["max_correction_per_window"]
    window_count = response_policy["bounded_window_count"]
    total_capacity = rounded(max_correction * window_count)
    records = []
    for lane in lanes:
        support_error = rounded(
            max(0.0, lane["support_survival_threshold"] - lane["final_A_support_retention"])
        )
        support_margin = rounded(
            lane["final_A_support_retention"] - lane["support_survival_threshold"]
        )
        out_of_envelope = support_error > total_capacity + 1e-12
        schedule = [] if out_of_envelope else response_schedule(support_error, max_correction)
        scheduled_total = rounded(sum(schedule))
        post_response_support = rounded(
            lane["final_A_support_retention"] + scheduled_total
        )
        post_response_error = rounded(
            max(0.0, lane["support_survival_threshold"] - post_response_support)
        )
        if out_of_envelope:
            saturation_status = "blocked_out_of_envelope"
        elif support_error > 0 and len(schedule) == window_count:
            saturation_status = "bounded_window_fully_used"
        elif support_error > 0:
            saturation_status = "not_saturated_within_bounded_window"
        else:
            saturation_status = "not_applicable_no_response"
        if out_of_envelope:
            overcorrection_status = "not_evaluated_blocked_out_of_envelope"
        elif support_error > 0:
            overcorrection_status = "capped_at_support_threshold"
        else:
            overcorrection_status = "not_applicable_no_response"
        records.append(
            {
                "lane_id": lane["lane_id"],
                "lane_digest": lane["lane_digest"],
                "target_state_before_response": lane["target_state"],
                "final_A_support_retention": lane["final_A_support_retention"],
                "support_survival_threshold": lane["support_survival_threshold"],
                "support_margin": support_margin,
                "support_error_signal": {
                    "error_expression": "max(0, support_survival_threshold - final_A_support_retention)",
                    "support_error": support_error,
                    "error_direction": "raise_support_retention_toward_threshold",
                    "source_current_fields": [
                        "final_A_support_retention",
                        "support_survival_threshold",
                    ],
                    "uses_external_proxy_fields": False,
                },
                "response_magnitude_surface": {
                    "max_correction_per_window": max_correction,
                    "bounded_window_count": window_count,
                    "total_bounded_correction_capacity": total_capacity,
                    "scheduled_response_amounts": schedule,
                    "scheduled_response_total": scheduled_total,
                    "out_of_envelope_blocked": out_of_envelope,
                    "out_of_envelope_blocker": response_policy[
                        "out_of_envelope_blocker"
                    ],
                },
                "budget_debit_surface": {
                    "surface_name": "support_response_packet_budget_debit",
                    "node_plus_packet_budget_debit_required": scheduled_total > 0,
                    "budget_debit_amount": scheduled_total,
                    "budget_debit_unit": "bounded_response_packet_amount",
                    "budget_mutation_owner": "LGRC step or committed packet scheduling event boundary",
                },
                "support_trend": trend_for_lane(lane, support_error),
                "saturation_status": saturation_status,
                "overcorrection_status": overcorrection_status,
                "bounded_window": {
                    "window_count": window_count,
                    "windows_used": len(schedule),
                    "within_bounded_window": not out_of_envelope
                    and len(schedule) <= window_count,
                },
                "post_response_estimate": {
                    "estimate_scope": "policy-envelope estimate only; not native state mutation",
                    "post_response_support_retention": post_response_support,
                    "post_response_error": post_response_error,
                    "post_response_meets_target": post_response_error <= 1e-12,
                },
            }
        )
    return records


def find_ready_response_contract(phase8_matrix: dict[str, Any]) -> dict[str, Any]:
    for row in phase8_matrix.get("phase8_ready_contracts", []):
        if row.get("native_policy_name") == "native_response_magnitude_policy":
            return row
    raise ValueError("Missing native_response_magnitude_policy readiness row")


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    target = load_json(TARGET_OUTPUT)
    n12_response = load_json(N12_RESPONSE_OUTPUT)
    n12_phase8 = load_json(N12_PHASE8_OUTPUT)

    n07_row = row_by_id(inventory, "n13_i1_row_01_n07_support_withdrawal_baseline")
    n09_row = row_by_id(inventory, "n13_i1_row_02_n09_bounded_external_proxy_regulation")
    n12_row = row_by_id(inventory, "n13_i1_row_06_n12_phase8_readiness_inputs")
    target_candidate = target["support_derived_target_candidate"]
    response_candidate = n12_response["response_magnitude_candidate"]
    response_policy = response_candidate["response_magnitude_policy"]
    ready_response_contract = find_ready_response_contract(n12_phase8)
    lane_records = build_lane_response_records(
        target_candidate["target_lane_records"], response_policy
    )
    disrupted_records = [
        row
        for row in lane_records
        if row["target_state_before_response"] == "support_disrupted"
    ]
    response_needed_records = [
        row
        for row in lane_records
        if row["support_error_signal"]["support_error"] > 0
    ]
    support_seeking_regulation_candidate = {
        "candidate_name": "support_error_bounded_response_candidate",
        "candidate_kind": "bounded_support_error_response_candidate",
        "support_seeking_regulation_candidate": True,
        "candidate_ap_level": "AP3",
        "provisional_ap_level": "AP3_candidate_pending_controls",
        "ap3_candidate_pending_controls": True,
        "final_ap3_supported": False,
        "self_maintenance_candidate_supported": False,
        "support_target": {
            "target_name": target_candidate["target_name"],
            "target_kind": target_candidate["target_kind"],
            "target_derivation_rule": target_candidate["target_derivation_rule"],
            "target_output_digest": target["output_digest"],
            "target_source": rel(TARGET_OUTPUT),
        },
        "support_error_signal": {
            "error_name": "support_retention_threshold_deficit",
            "error_expression": "max(0, support_survival_threshold - final_A_support_retention)",
            "error_is_source_current_support_state_derived": True,
            "error_is_external_proxy": False,
            "runtime_visible_inputs": [
                "final_A_support_retention",
                "support_survival_threshold",
                "lane_digest",
                "support_area_digest",
            ],
        },
        "response_magnitude_surface": {
            "source": rel(N12_RESPONSE_OUTPUT),
            "native_policy_name": "native_response_magnitude_policy",
            "native_policy_enabled": False,
            "native_policy_supported": False,
            "phase8_ready_input_only": True,
            "max_correction_per_window": response_policy[
                "max_correction_per_window"
            ],
            "bounded_window_count": response_policy["bounded_window_count"],
            "total_bounded_correction_capacity": rounded(
                response_policy["max_correction_per_window"]
                * response_policy["bounded_window_count"]
            ),
            "response_gain_source": response_policy["response_gain_source"],
            "out_of_envelope_blocker": response_policy["out_of_envelope_blocker"],
        },
        "lane_response_records": lane_records,
        "bounded_window": {
            "source": rel(N12_RESPONSE_OUTPUT),
            "window_count": response_policy["bounded_window_count"],
            "max_correction_per_window": response_policy[
                "max_correction_per_window"
            ],
            "all_source_lanes_within_window": all(
                row["bounded_window"]["within_bounded_window"] for row in lane_records
            ),
        },
        "budget_debit_surface": {
            "budget_surfaces": [
                "support_response_packet_budget_debit",
                "response_packet_budget_surface",
                "node_plus_packet_budget_error",
                "final_budget_error",
            ],
            "debit_rule": "scheduled bounded response amount must debit node-plus-packet or explicit response packet budget before commit",
            "mutation_boundary": {
                "producer_or_policy_may_schedule_only": True,
                "step_or_topology_event_owns_state_mutation": True,
                "producer_direct_mutation_allowed": False,
                "phase8_implementation_opened": False,
            },
            "all_scheduled_responses_have_budget_debit": all(
                row["response_magnitude_surface"]["scheduled_response_total"]
                == row["budget_debit_surface"]["budget_debit_amount"]
                for row in lane_records
            ),
        },
        "trend_stability_fields": {
            "support_trend": sorted({row["support_trend"] for row in lane_records}),
            "saturation_status": sorted(
                {row["saturation_status"] for row in lane_records}
            ),
            "overcorrection_status": sorted(
                {row["overcorrection_status"] for row in lane_records}
            ),
            "out_of_envelope_blocker": response_policy["out_of_envelope_blocker"],
        },
        "support_disrupted_negative_control": {
            "raw_disrupted_lane_count": len(disrupted_records),
            "raw_disrupted_lanes": [row["lane_id"] for row in disrupted_records],
            "raw_disrupted_lanes_not_counted_as_supported_before_response": all(
                row["target_state_before_response"] == "support_disrupted"
                for row in disrupted_records
            ),
            "bounded_response_is_schedule_candidate_not_raw_support_pass": True,
            "full_stress_control_pending_iteration_6": True,
        },
        "external_proxy_separation": {
            "support_error_uses_n09_external_proxy_fields": False,
            "n09_external_proxy_fields_available_but_excluded": sorted(
                n09_row["external_proxy_fields"].keys()
            ),
            "n09_role": "bounded_external_proxy_regulation_baseline_only",
            "response_magnitude_uses_n12_readiness_input": True,
            "target_is_source_current_support_state": True,
        },
        "claim_boundary": {
            "bounded_response_is_intention": False,
            "support_error_is_semantic_goal_ownership": False,
            "support_regulation_candidate_is_agency": False,
            "candidate_ap3_is_final_ap3_support": False,
            "artifact_level_candidate_is_native_support": False,
            "native_response_magnitude_readiness_is_phase8_implementation": False,
        },
        "pending_controls": PENDING_CONTROLS,
        "source_rows": {
            "support_source": n07_row["row_id"],
            "external_proxy_baseline": n09_row["row_id"],
            "n12_response_readiness_input": n12_row["row_id"],
            "n12_phase8_ready_contract_row": ready_response_contract["row_id"],
        },
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "target_source_passed": target["status"] == "passed",
        "n12_response_source_passed": n12_response["status"] == "passed",
        "n12_phase8_source_passed": n12_phase8["status"] == "passed",
        "support_error_signal_recorded": all(
            "support_error_signal" in row for row in lane_records
        ),
        "response_magnitude_surface_recorded": all(
            "response_magnitude_surface" in row for row in lane_records
        ),
        "bounded_window_recorded": "bounded_window" in support_seeking_regulation_candidate
        and all("bounded_window" in row for row in lane_records),
        "budget_debit_surface_recorded": all(
            "budget_debit_surface" in row for row in lane_records
        ),
        "support_trend_recorded": all("support_trend" in row for row in lane_records),
        "saturation_status_recorded": all(
            "saturation_status" in row for row in lane_records
        ),
        "overcorrection_status_recorded": all(
            "overcorrection_status" in row for row in lane_records
        ),
        "out_of_envelope_blocker_recorded": bool(
            support_seeking_regulation_candidate["trend_stability_fields"][
                "out_of_envelope_blocker"
            ]
        ),
        "response_packet_scheduling_boundary_recorded": support_seeking_regulation_candidate[
            "budget_debit_surface"
        ]["mutation_boundary"]["producer_or_policy_may_schedule_only"]
        is True
        and support_seeking_regulation_candidate["budget_debit_surface"][
            "mutation_boundary"
        ]["step_or_topology_event_owns_state_mutation"]
        is True,
        "support_disrupted_negative_control_recorded": support_seeking_regulation_candidate[
            "support_disrupted_negative_control"
        ]["raw_disrupted_lane_count"]
        > 0
        and support_seeking_regulation_candidate["support_disrupted_negative_control"][
            "raw_disrupted_lanes_not_counted_as_supported_before_response"
        ],
        "response_needed_case_present": len(response_needed_records) > 0,
        "all_source_lanes_within_bounded_window": support_seeking_regulation_candidate[
            "bounded_window"
        ]["all_source_lanes_within_window"],
        "scheduled_response_does_not_overcorrect": all(
            row["post_response_estimate"]["post_response_support_retention"]
            <= row["support_survival_threshold"]
            or row["support_error_signal"]["support_error"] == 0
            for row in lane_records
        ),
        "external_proxy_fields_excluded_from_support_error": not support_seeking_regulation_candidate[
            "external_proxy_separation"
        ]["support_error_uses_n09_external_proxy_fields"],
        "candidate_ap3_recorded_without_final_support": support_seeking_regulation_candidate[
            "candidate_ap_level"
        ]
        == "AP3"
        and support_seeking_regulation_candidate["final_ap3_supported"] is False,
        "self_maintenance_not_supported_yet": support_seeking_regulation_candidate[
            "self_maintenance_candidate_supported"
        ]
        is False,
        "pending_controls_recorded": set(PENDING_CONTROLS)
        == set(support_seeking_regulation_candidate["pending_controls"]),
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "claim_boundary_controls_false": all(
            value is False
            for value in support_seeking_regulation_candidate[
                "claim_boundary"
            ].values()
        ),
        "phase8_not_opened": support_seeking_regulation_candidate[
            "response_magnitude_surface"
        ]["native_policy_enabled"]
        is False
        and support_seeking_regulation_candidate["budget_debit_surface"][
            "mutation_boundary"
        ]["phase8_implementation_opened"]
        is False,
        "native_support_not_opened": support_seeking_regulation_candidate[
            "response_magnitude_surface"
        ]["native_policy_supported"]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 4,
        "purpose": "support_seeking_regulation_candidate",
        "schema": "n13_support_seeking_regulation_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_result": {
            "support_seeking_regulation_candidate": True,
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_pending_controls",
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "support_seeking_regulation_candidate": support_seeking_regulation_candidate,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(TARGET_OUTPUT): source_artifact(TARGET_OUTPUT, target),
            rel(N12_RESPONSE_OUTPUT): source_artifact(N12_RESPONSE_OUTPUT, n12_response),
            rel(N12_PHASE8_OUTPUT): source_artifact(N12_PHASE8_OUTPUT, n12_phase8),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(TARGET_REPORT): source_report(TARGET_REPORT),
            rel(N12_RESPONSE_REPORT): source_report(N12_RESPONSE_REPORT),
            rel(N12_PHASE8_REPORT): source_report(N12_PHASE8_REPORT),
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
    candidate = output["support_seeking_regulation_candidate"]
    lines = [
        "# N13 Support-Seeking Regulation Candidate",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"support_seeking_regulation_candidate = {str(candidate['support_seeking_regulation_candidate']).lower()}",
        f"candidate_ap_level = {candidate['candidate_ap_level']}",
        f"provisional_ap_level = {candidate['provisional_ap_level']}",
        "final_ap3_supported = false",
        "self_maintenance_candidate_supported = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 4 records a bounded support-error response candidate against",
        "the Iteration 3 source-current support target. It does not freeze final",
        "AP3 support; external-proxy, hidden-target, post-hoc-label, disruption,",
        "restoration, and claim-boundary controls remain pending for Iterations",
        "5-7.",
        "",
        "## Support Error Signal",
        "",
        "```json",
        json.dumps(candidate["support_error_signal"], indent=2, sort_keys=True),
        "```",
        "",
        "## Response Magnitude Surface",
        "",
        "```json",
        json.dumps(
            candidate["response_magnitude_surface"], indent=2, sort_keys=True
        ),
        "```",
        "",
        "## Lane Responses",
        "",
        "| Lane | Target before response | Support error | Scheduled response | Windows | Out of envelope | Post-response estimate | Trend |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in candidate["lane_response_records"]:
        lines.append(
            "| "
            f"`{row['lane_id']}` | "
            f"`{row['target_state_before_response']}` | "
            f"{row['support_error_signal']['support_error']} | "
            f"{row['response_magnitude_surface']['scheduled_response_total']} | "
            f"{row['bounded_window']['windows_used']} | "
            f"`{str(row['response_magnitude_surface']['out_of_envelope_blocked']).lower()}` | "
            f"{row['post_response_estimate']['post_response_support_retention']} | "
            f"`{row['support_trend']}` |"
        )
    lines.extend(
        [
            "",
            "## Budget And Mutation Boundary",
            "",
            "```json",
            json.dumps(candidate["budget_debit_surface"], indent=2, sort_keys=True),
            "```",
            "",
            "## Stability Fields",
            "",
            "```json",
            json.dumps(
                candidate["trend_stability_fields"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Support-Disrupted Negative Control Record",
            "",
            "```json",
            json.dumps(
                candidate["support_disrupted_negative_control"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Pending Controls",
            "",
            "```json",
            json.dumps(candidate["pending_controls"], indent=2),
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
            "bounded response != intention",
            "support error != semantic goal ownership",
            "candidate AP3 != final supported AP3",
            "self-maintenance candidate != selfhood",
            "artifact-level response scheduling != native support",
            "N12 response magnitude readiness != Phase 8 implementation",
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

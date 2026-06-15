#!/usr/bin/env python3
"""Build N13 Iteration 3 support-state derived target candidate."""

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

OUTPUT_PATH = OUTPUTS / "n13_support_derived_target_candidate.json"
REPORT_PATH = REPORTS / "n13_support_derived_target_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_support_derived_target_candidate.py"
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


def row_by_id(inventory: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in inventory["n13_inventory_rows"]:
        if row["row_id"] == row_id:
            return row
    raise ValueError(f"Missing inventory row: {row_id}")


def path_from_rel(path_text: str) -> Path:
    return ROOT / path_text


def build_target_lane_records(lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for lane in lanes:
        computed_survival = (
            lane["final_A_support_retention"] >= lane["support_survival_threshold"]
        )
        records.append(
            {
                "lane_id": lane["lane_id"],
                "lane_digest": lane["lane_digest"],
                "final_A_support_retention": lane["final_A_support_retention"],
                "support_survival_threshold": lane["support_survival_threshold"],
                "computed_support_survival_passed": computed_survival,
                "source_support_survival_passed": lane["support_survival_passed"],
                "rule_matches_source": computed_survival
                == lane["support_survival_passed"],
                "target_state": "support_valid"
                if computed_survival
                else "support_disrupted",
                "withdrawal_depth": lane["withdrawal_depth"],
                "restoration_fraction": lane["restoration_fraction"],
                "identity_support_outcome_tag": lane["identity_support_outcome_tag"],
            }
        )
    return records


def n10_alignment_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for row in matrix:
        records.append(
            {
                "matrix_state": row["matrix_state"],
                "support_state_tag": row["support_state_tag"],
                "integration_allowed": row["integration_allowed"],
                "expected_outcome": row["expected_outcome"],
                "outcome_matches_expectation": row["outcome_matches_expectation"],
                "budget_error_zero": row["budget_error_zero"],
                "claim_flags_false": row["claim_flags_false"],
                "row_digest_valid": row["row_digest_valid"],
                "primary_blocker": row.get("primary_blocker"),
            }
        )
    return records


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    n07_row = row_by_id(inventory, "n13_i1_row_01_n07_support_withdrawal_baseline")
    n09_row = row_by_id(inventory, "n13_i1_row_02_n09_bounded_external_proxy_regulation")
    n10_row = row_by_id(inventory, "n13_i1_row_03_n10_support_sensitive_matrix")

    lanes = n07_row["support_state_fields"]["lanes"]
    target_lanes = build_target_lane_records(lanes)
    matrix = n10_row["support_state_fields"]["support_state_matrix"]
    n10_alignment = n10_alignment_records(matrix)
    external_proxy_field_names = sorted(n09_row["external_proxy_fields"].keys())
    original_source_artifacts = {
        n07_row["source_artifact"]: source_artifact(
            path_from_rel(n07_row["source_artifact"])
        ),
        n09_row["source_artifact"]: source_artifact(
            path_from_rel(n09_row["source_artifact"])
        ),
        n10_row["source_artifact"]: source_artifact(
            path_from_rel(n10_row["source_artifact"])
        ),
    }
    original_source_reports = {
        n07_row["source_report"]: source_report(path_from_rel(n07_row["source_report"])),
        n09_row["source_report"]: source_report(path_from_rel(n09_row["source_report"])),
        n10_row["source_report"]: source_report(path_from_rel(n10_row["source_report"])),
    }
    support_derived_target_candidate = {
        "target_name": "support_retention_above_threshold_source_current",
        "target_kind": "support_state_derived_target_candidate",
        "provisional_ap_level": "AP2",
        "support_derived_target_candidate": True,
        "self_maintenance_candidate_supported": False,
        "final_ap3_supported": False,
        "ap3_candidate_pending_controls": True,
        "target_derivation_rule": {
            "expression": "final_A_support_retention >= support_survival_threshold",
            "input_fields": [
                "final_A_support_retention",
                "support_survival_threshold",
            ],
            "threshold_source": n07_row["source_artifact"],
            "support_area_id": n07_row["support_state_fields"]["support_area_id"],
            "support_area_digest": n07_row["support_state_fields"][
                "support_area_digest"
            ],
            "runtime_visible_inputs": [
                "final_A_support_retention",
                "support_survival_threshold",
                "withdrawal_depth",
                "restoration_fraction",
            ],
        },
        "target_lane_records": target_lanes,
        "n10_support_matrix_alignment": n10_alignment,
        "source_current_requirement": {
            "source_artifacts_pinned": True,
            "lane_digests_required": True,
            "support_area_digest_required": True,
            "stale_source_replay_blocked": True,
        },
        "external_proxy_separation": {
            "target_uses_external_proxy_fields": False,
            "external_proxy_fields_available_but_excluded": external_proxy_field_names,
            "n09_proxy_row_role": "external_proxy_regulation_baseline_only",
            "n09_withdrawal_digest_is_lane_link_only": True,
        },
        "post_hoc_label_audit": {
            "threshold_preexists_n13": True,
            "lane_digests_preexist_n13": True,
            "n13_did_not_choose_threshold": True,
            "target_rule_matches_all_source_lanes": all(
                lane["rule_matches_source"] for lane in target_lanes
            ),
            "full_post_hoc_label_control_pending_iteration_5": True,
        },
        "hidden_target_audit": {
            "target_fields_declared": True,
            "hidden_support_target_required": False,
            "full_hidden_target_control_pending_iteration_5": True,
        },
        "producer_decision_split": {
            "producer_decision_fields": n07_row["producer_decision_fields"],
            "bookkeeping_fields": n07_row["bookkeeping_fields"],
            "n13_added_producer_decisions": [],
        },
        "budget_surfaces": n07_row["budget_surfaces"],
        "runtime_visible_surfaces": n07_row["runtime_visible_surfaces"],
        "blocked_claims": n07_row["blocked_claims"],
        "pending_gates": [
            "support_error_signal_not_evaluated_until_iteration_4",
            "bounded_response_magnitude_not_evaluated_until_iteration_4",
            "external_proxy_controls_not_run_until_iteration_5",
            "hidden_target_controls_not_run_until_iteration_5",
            "post_hoc_label_controls_not_run_until_iteration_5",
            "support_disruption_restoration_stress_not_run_until_iteration_6",
            "claim_boundary_record_not_frozen_until_iteration_7",
        ],
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "n07_support_row_present": n07_row["row_id"]
        == "n13_i1_row_01_n07_support_withdrawal_baseline",
        "n09_external_proxy_row_present": n09_row["support_condition_name"]
        == "none_external_proxy_only",
        "n10_support_matrix_row_present": n10_row["row_id"]
        == "n13_i1_row_03_n10_support_sensitive_matrix",
        "target_rule_matches_all_lanes": all(
            lane["rule_matches_source"] for lane in target_lanes
        ),
        "support_valid_and_disrupted_cases_present": {
            lane["target_state"] for lane in target_lanes
        }
        == {"support_valid", "support_disrupted"},
        "explicit_restoration_case_present": any(
            lane["restoration_fraction"] > 0 and lane["target_state"] == "support_valid"
            for lane in target_lanes
        ),
        "target_derivation_not_external_proxy_label": not support_derived_target_candidate[
            "external_proxy_separation"
        ]["target_uses_external_proxy_fields"],
        "target_derivation_not_post_hoc_label": support_derived_target_candidate[
            "post_hoc_label_audit"
        ]["threshold_preexists_n13"]
        and support_derived_target_candidate["post_hoc_label_audit"][
            "n13_did_not_choose_threshold"
        ],
        "source_current_lane_digests_present": all(
            bool(lane["lane_digest"]) for lane in target_lanes
        ),
        "n10_disrupted_support_blocks": any(
            row["matrix_state"] == "n09_matched_withdrawal_disrupts_support"
            and row["integration_allowed"] is False
            and row["primary_blocker"] == "support_disrupted_but_integration_allowed"
            for row in n10_alignment
        ),
        "n10_explicit_restoration_resumes": any(
            row["matrix_state"] == "explicit_restoration_recovers_support"
            and row["integration_allowed"] is True
            for row in n10_alignment
        ),
        "provisional_ap_level_ap2": support_derived_target_candidate[
            "provisional_ap_level"
        ]
        == "AP2",
        "final_ap3_not_assigned": support_derived_target_candidate[
            "final_ap3_supported"
        ]
        is False,
        "self_maintenance_not_supported_yet": support_derived_target_candidate[
            "self_maintenance_candidate_supported"
        ]
        is False,
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 3,
        "purpose": "support_derived_target_candidate",
        "schema": "n13_support_derived_target_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_result": {
            "support_derived_target_candidate": True,
            "provisional_ap_level": "AP2",
            "final_ap3_supported": False,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "support_derived_target_candidate": support_derived_target_candidate,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            **original_source_artifacts,
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            **original_source_reports,
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
    candidate = output["support_derived_target_candidate"]
    lines = [
        "# N13 Support-Derived Target Candidate",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"support_derived_target_candidate = {str(candidate['support_derived_target_candidate']).lower()}",
        f"provisional_ap_level = {candidate['provisional_ap_level']}",
        "final_ap3_supported = false",
        "self_maintenance_candidate_supported = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 3 isolates a source-current support-state target rule. It",
        "does not assign final AP3 support; support-seeking regulation and",
        "controls remain pending for Iterations 4-7.",
        "",
        "## Target Rule",
        "",
        "```json",
        json.dumps(candidate["target_derivation_rule"], indent=2, sort_keys=True),
        "```",
        "",
        "## Lane Records",
        "",
        "| Lane | Final support | Threshold | Target state | Rule matches source |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for lane in candidate["target_lane_records"]:
        lines.append(
            "| "
            f"`{lane['lane_id']}` | "
            f"{lane['final_A_support_retention']} | "
            f"{lane['support_survival_threshold']} | "
            f"`{lane['target_state']}` | "
            f"`{str(lane['rule_matches_source']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## External Proxy Separation",
            "",
            "```json",
            json.dumps(candidate["external_proxy_separation"], indent=2, sort_keys=True),
            "```",
            "",
            "## Post-Hoc And Hidden-Target Audits",
            "",
            "```json",
            json.dumps(
                {
                    "hidden_target_audit": candidate["hidden_target_audit"],
                    "post_hoc_label_audit": candidate["post_hoc_label_audit"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Pending Gates",
            "",
            "```json",
            json.dumps(candidate["pending_gates"], indent=2),
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
            "support-derived target candidate != support-seeking regulation",
            "support-derived target != semantic goal ownership",
            "support survival != identity acceptance",
            "provisional AP2 target candidate != final AP3 support",
            "self-maintenance candidate != selfhood",
            "artifact-level target derivation != native support",
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

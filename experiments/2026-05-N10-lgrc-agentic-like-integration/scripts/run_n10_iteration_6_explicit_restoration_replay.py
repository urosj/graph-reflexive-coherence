#!/usr/bin/env python3
"""Run N10 Iteration 6 explicit-restoration replay.

Iteration 6 is the positive counterpart to Iteration 5. It consumes the N07
explicit-restoration lane and allows support-aware regulation to resume only
because restoration evidence is source-backed, above threshold, and tied to the
same N09 withdrawal event recorded in the disrupted-support control.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
BASELINE_PATH = EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json"
ITERATION_3_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_3_support_aware_regulation_replay.json"
)
ITERATION_4_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_4_mild_withdrawal_survival_replay.json"
)
ITERATION_5_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_5_disrupted_support_control.json"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_6_explicit_restoration_replay.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_6_explicit_restoration_replay.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_6_explicit_restoration_replay.py"
)


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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({k: v for k, v in output.items() if k not in excluded})


def source_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_artifacts"][key]["path"]


def report_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_reports"][key]["path"]


def find_lane(rows: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("lane_id") == lane_id:
            return row
    raise KeyError(f"lane not found: {lane_id}")


def find_fixture_lane(manifest: dict[str, Any], lane_id: str) -> dict[str, Any]:
    return find_lane(manifest["fixture_lanes"], lane_id)


def source_support_state_tag(manifest: dict[str, Any], support_lane: dict[str, Any]) -> str:
    outcome = support_lane["identity_support_outcome_tag"]
    return manifest["allowed_values"]["source_support_outcome_map"][outcome]


def build_source_records(
    baseline: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_keys = [
        "n07_withdrawal_baseline",
        "n09_hypothesis_a_closeout",
    ]
    report_keys = [
        "n07_withdrawal_baseline",
        "n09_hypothesis_a_closeout",
    ]
    source_artifacts = {
        "n10_baseline_inventory": {
            "path": rel(BASELINE_PATH),
            "sha256": digest_file(BASELINE_PATH),
        },
        "n10_fixture_manifest": {
            "path": rel(MANIFEST_PATH),
            "sha256": digest_file(MANIFEST_PATH),
        },
        "n10_iteration_3_support_aware_regulation_replay": {
            "path": rel(ITERATION_3_PATH),
            "sha256": digest_file(ITERATION_3_PATH),
        },
        "n10_iteration_4_mild_withdrawal_survival_replay": {
            "path": rel(ITERATION_4_PATH),
            "sha256": digest_file(ITERATION_4_PATH),
        },
        "n10_iteration_5_disrupted_support_control": {
            "path": rel(ITERATION_5_PATH),
            "sha256": digest_file(ITERATION_5_PATH),
        },
    }
    for key in artifact_keys:
        path = source_path(baseline, key)
        current_digest = digest_file(path)
        source_artifacts[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_artifacts"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_artifacts"][key]["sha256"],
        }

    source_reports = {}
    for key in report_keys:
        path = report_path(baseline, key)
        current_digest = digest_file(path)
        source_reports[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_reports"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_reports"][key]["sha256"],
        }
    return source_artifacts, source_reports


def build_restoration_row(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n09: dict[str, Any],
    support_lane: dict[str, Any],
    fixture_lane: dict[str, Any],
    iteration_5: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    support_state_tag = source_support_state_tag(manifest, support_lane)
    disrupted_record = iteration_5["blocked_integration_record"]
    disrupted_support = disrupted_record["support_evidence"]
    disruption_history_preserved = (
        support_lane["n09_withdrawal_digest"]
        == disrupted_support["n09_withdrawal_digest"]
        and support_lane["withdrawal_depth"] == disrupted_support["withdrawal_depth"]
        and disrupted_record["integration_allowed"] is False
    )
    row = {
        "integration_row_id": "n10_i6_explicit_restoration_replay_row_v1",
        "integration_level": "A4",
        "attempted_integration_level": "A4",
        "accepted_integration_level": "A4",
        "n10_category_level": "ALI3",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i6",
        "scheduler_event_index": None,
        "source_experiment_ids": ["N07", "N09", "N10"],
        "source_artifacts": {
            key: value["path"] for key, value in source_artifacts.items()
        },
        "source_reports": {
            key: value["path"] for key, value in source_reports.items()
        },
        "source_artifact_digests": {
            key: value["sha256"] for key, value in source_artifacts.items()
        },
        "route_choice_artifact": None,
        "route_choice_digest": None,
        "memory_affordance_artifact": None,
        "memory_affordance_digest": None,
        "identity_support_artifact": "n07_withdrawal_baseline",
        "identity_support_digest": source_artifacts["n07_withdrawal_baseline"][
            "sha256"
        ],
        "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
        "goal_proxy_regulation_digest": source_artifacts["n09_hypothesis_a_closeout"][
            "sha256"
        ],
        "support_state_tag": support_state_tag,
        "route_context_tag": "route_context_not_applicable",
        "memory_scope_tag": "memory_scope_not_applicable",
        "regulation_scope_tag": "artifact_only_goal_proxy_regulation_candidate",
        "integration_outcome_tag": "restoration_gated_integration_candidate",
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "not_applicable_ali3_restoration_replay",
        "proxy_budget_surface": "n09_source_proxy_budget_compatibility",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": baseline["native_policy_gaps"],
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "claim_flags": claim_flags,
        "integration_allowed": True,
        "positive_integration_row_emitted": True,
        "primary_blocker": None,
        "blocker_reason": None,
        "category_boundary": (
            "ALI3 support-sensitive regulation is satisfied for the bounded "
            "artifact-only support/regulation replay path: support-intact and "
            "mild-withdrawal lanes proceed, disrupted support blocks, and "
            "explicit restoration resumes integration. Route/memory "
            "composition remains deferred to ALI4."
        ),
        "ali3_status": "support_sensitive_regulation_closed_for_artifact_only_support_regulation_path",
        "a5_relevance": "restoration_gated_support_regulation_component_not_a5_closeout",
        "fixture_lane": {
            "lane_id": fixture_lane["lane_id"],
            "expected_role": fixture_lane["expected_role"],
            "required_support_state_tag": fixture_lane[
                "required_support_state_tag"
            ],
            "source_support_lane_id": fixture_lane["source_support_lane_id"],
        },
        "prior_disruption_evidence": {
            "source_iteration": 5,
            "blocked_record_digest": disrupted_record["integration_row_digest"],
            "primary_blocker": disrupted_record["primary_blocker"],
            "integration_allowed": disrupted_record["integration_allowed"],
            "positive_integration_row_emitted": disrupted_record[
                "positive_integration_row_emitted"
            ],
            "support_lane_id": disrupted_support["source_lane_id"],
            "support_lane_digest": disrupted_support["lane_digest"],
            "n09_withdrawal_digest": disrupted_support["n09_withdrawal_digest"],
            "withdrawal_depth": disrupted_support["withdrawal_depth"],
            "support_survival_passed": disrupted_support["support_survival_passed"],
            "disruption_history_preserved": disruption_history_preserved,
        },
        "support_evidence": {
            "source_lane_id": support_lane["lane_id"],
            "lane_digest": support_lane["lane_digest"],
            "identity_support_outcome_tag": support_lane[
                "identity_support_outcome_tag"
            ],
            "support_survival_passed": support_lane["support_survival_passed"],
            "support_survival_threshold": support_lane["support_survival_threshold"],
            "final_A_support_retention": support_lane["final_A_support_retention"],
            "reference_A_support_retention": support_lane[
                "reference_A_support_retention"
            ],
            "support_loss_from_reference": support_lane[
                "support_loss_from_reference"
            ],
            "final_basin_separability": support_lane["final_basin_separability"],
            "final_budget_error": support_lane["final_budget_error"],
            "withdrawal_depth": support_lane["withdrawal_depth"],
            "withdrawal_kind": support_lane["withdrawal_kind"],
            "restoration_fraction": support_lane["restoration_fraction"],
            "n09_withdrawal_digest": support_lane["n09_withdrawal_digest"],
            "support_above_threshold_after_restoration": (
                support_lane["final_A_support_retention"]
                >= support_lane["support_survival_threshold"]
            ),
            "explicit_restoration_present": support_lane["restoration_fraction"] > 0.0,
        },
        "regulation_evidence": {
            "source_gpr_level": n09["ceiling_algorithm_result"][
                "strongest_passing_gpr_level"
            ],
            "source_claim_ceiling": n09["claim_ceiling"],
            "source_hypothesis_a_status": n09["ceiling_algorithm_result"][
                "hypothesis_a_status"
            ],
            "source_budget_control_passed": n09["controls"]["budget_violation"][
                "control_passed"
            ],
            "source_artifact_only_runtime_fallback_blocked": n09["controls"][
                "artifact_runtime_fallback"
            ]["control_passed"],
        },
        "budget_mode": "source_artifact_budget_compatibility_not_single_runtime_continuity",
    }
    return with_digest(row, "integration_row_digest")


def build_controls(
    manifest: dict[str, Any],
    integration_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    manifest_support_lane: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    support = integration_row["support_evidence"]
    prior = integration_row["prior_disruption_evidence"]
    return {
        "missing_identity_support_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "restoration replay requires N07 Iteration 13 support lane evidence",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "restoration replay requires N09 GPR closeout evidence",
        },
        "source_artifact_digest_mismatch": {
            "control_passed": all(
                value.get("matches_baseline", True) for value in source_artifacts.values()
            ),
            "primary_blocker": blockers["source_artifact_digest_mismatch"],
            "reason": "N07/N09 source artifact digests are rechecked against Iteration 1",
        },
        "stale_identity_support_baseline": {
            "control_passed": support["lane_digest"]
            == manifest_support_lane["lane_digest"]
            and support["final_A_support_retention"]
            == manifest_support_lane["final_A_support_retention"],
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "restored support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary",
        },
        "restoration_required_but_missing": {
            "control_passed": support["explicit_restoration_present"] is True
            and support["support_above_threshold_after_restoration"] is True
            and integration_row["integration_allowed"] is True,
            "primary_blocker": blockers["restoration_required_but_missing"],
            "reason": "integration resumes only because the explicit restoration lane is present and above threshold",
        },
        "disruption_history_preserved": {
            "control_passed": prior["disruption_history_preserved"] is True
            and prior["integration_allowed"] is False
            and prior["positive_integration_row_emitted"] is False,
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "restoration references the same N09 withdrawal digest and preserves the Iteration 5 blocked history",
        },
        "support_disrupted_control_not_erased": {
            "control_passed": prior["primary_blocker"]
            == blockers["support_disrupted_but_integration_allowed"],
            "primary_blocker": blockers["support_disrupted_but_integration_allowed"],
            "reason": "restoration resumes after, rather than deletes, the disrupted-support blocker",
        },
        "budget_surface_ambiguity": {
            "control_passed": integration_row["node_plus_packet_budget_error"] == 0.0
            and support["final_budget_error"] == 0.0
            and integration_row["regulation_evidence"]["source_budget_control_passed"]
            is True,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "Iteration 6 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in integration_row["claim_flags"].values()
            ),
            "primary_blocker": blockers["claim_promotion"],
            "reason": "explicit restoration does not emit agency, A6, identity acceptance, or goal-ownership claims",
        },
    }


def validate_output(
    manifest: dict[str, Any],
    n09: dict[str, Any],
    integration_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    row_fields = set(integration_row)
    support = integration_row["support_evidence"]
    prior = integration_row["prior_disruption_evidence"]
    fixture = integration_row["fixture_lane"]
    return {
        "integration_row_required_fields_present": required_fields.issubset(
            row_fields
        ),
        "integration_row_digest_valid": integration_row["integration_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in integration_row.items()
                if key != "integration_row_digest"
            }
        ),
        "n10_category_level_is_ali3": integration_row["n10_category_level"] == "ALI3",
        "attempted_integration_level_is_a4": integration_row[
            "attempted_integration_level"
        ]
        == "A4",
        "accepted_integration_level_is_a4": integration_row[
            "accepted_integration_level"
        ]
        == "A4",
        "support_state_tag_is_explicit_restoration": integration_row[
            "support_state_tag"
        ]
        == "explicit_restoration_recovers_support",
        "fixture_required_support_state_tag_matched": integration_row[
            "support_state_tag"
        ]
        == fixture["required_support_state_tag"],
        "restored_support_lane_survives": support["support_survival_passed"] is True,
        "restored_support_retention_meets_threshold": support[
            "final_A_support_retention"
        ]
        >= support["support_survival_threshold"],
        "explicit_restoration_present": support["restoration_fraction"] > 0.0,
        "restored_support_budget_error_zero": support["final_budget_error"] == 0.0,
        "prior_disruption_history_preserved": prior[
            "disruption_history_preserved"
        ]
        is True,
        "prior_disruption_was_blocked": prior["integration_allowed"] is False
        and prior["positive_integration_row_emitted"] is False,
        "same_n09_withdrawal_digest_as_disruption": support[
            "n09_withdrawal_digest"
        ]
        == prior["n09_withdrawal_digest"],
        "integration_allowed_true_after_restoration": integration_row[
            "integration_allowed"
        ]
        is True,
        "positive_integration_row_emitted": integration_row[
            "positive_integration_row_emitted"
        ]
        is True,
        "primary_blocker_absent_after_restoration": integration_row[
            "primary_blocker"
        ]
        is None,
        "ali3_closed_for_support_regulation_path": integration_row["ali3_status"]
        == "support_sensitive_regulation_closed_for_artifact_only_support_regulation_path",
        "n09_gpr6_available": n09["ceiling_algorithm_result"][
            "strongest_passing_gpr_level"
        ]
        == "GPR6",
        "n09_goal_proxy_candidate_available": n09["claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "n09_budget_control_passed": n09["controls"]["budget_violation"][
            "control_passed"
        ]
        is True,
        "source_artifact_digests_match_baseline": all(
            value.get("matches_baseline", True) for value in source_artifacts.values()
        ),
        "artifact_only_replay": integration_row["artifact_only"] is True
        and integration_row["runtime_state_used"] is False,
        "route_memory_not_consumed_for_ali3": integration_row["route_choice_artifact"]
        is None
        and integration_row["memory_affordance_artifact"] is None,
        "claim_flags_all_false": all(
            value is False for value in integration_row["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "a5_relevant_not_a5_closeout": integration_row["a5_relevance"]
        == "restoration_gated_support_regulation_component_not_a5_closeout",
        "a6_not_supported_by_iteration_6": integration_row["integration_level"]
        != "A6"
        and integration_row["n10_category_level"] != "ALI6",
        "src_clean_for_iteration_6": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n09 = load_json(source_path(baseline, "n09_hypothesis_a_closeout"))
    iteration_5 = load_json(ITERATION_5_PATH)
    support_lane = find_lane(
        n07_i13["withdrawal_lanes"], "restored_after_n09_partial_withdrawal"
    )
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "restored_after_n09_partial_withdrawal"
    )
    fixture_lane = find_fixture_lane(manifest, "explicit_restoration_replay")
    source_artifacts, source_reports = build_source_records(baseline)
    integration_row = build_restoration_row(
        baseline,
        manifest,
        n09,
        support_lane,
        fixture_lane,
        iteration_5,
        source_artifacts,
        source_reports,
    )
    controls = build_controls(
        manifest, integration_row, source_artifacts, manifest_support_lane
    )
    checks = validate_output(
        manifest, n09, integration_row, source_artifacts, controls
    )
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_n09_goal_proxy_regulation_closeout",
                "artifact": source_artifacts["n09_hypothesis_a_closeout"]["path"],
                "digest": source_artifacts["n09_hypothesis_a_closeout"]["sha256"],
            },
            {
                "step": "load_iteration_5_disrupted_support_blocker",
                "artifact": source_artifacts[
                    "n10_iteration_5_disrupted_support_control"
                ]["path"],
                "digest": source_artifacts[
                    "n10_iteration_5_disrupted_support_control"
                ]["sha256"],
                "blocked_record_digest": integration_row[
                    "prior_disruption_evidence"
                ]["blocked_record_digest"],
            },
            {
                "step": "load_n07_explicit_restoration_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
                "support_survival_threshold": support_lane[
                    "support_survival_threshold"
                ],
                "restoration_fraction": support_lane["restoration_fraction"],
                "n09_withdrawal_digest": support_lane["n09_withdrawal_digest"],
            },
            {
                "step": "resume_support_aware_regulation_replay_after_restoration",
                "accepted_integration_level": integration_row[
                    "accepted_integration_level"
                ],
                "integration_allowed": integration_row["integration_allowed"],
                "positive_integration_row_emitted": integration_row[
                    "positive_integration_row_emitted"
                ],
            },
            {
                "step": "emit_restoration_gated_integration_row",
                "integration_row_digest": integration_row["integration_row_digest"],
                "n10_category_level": integration_row["n10_category_level"],
                "ali3_status": integration_row["ali3_status"],
            },
        ],
        "n07_source_status": n07_i13.get("status"),
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 6 passes if integration can resume after support "
            "disruption only through explicit, source-backed restoration "
            "evidence, while preserving the history of disruption and "
            "restoration."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_6_explicit_restoration_replay_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 6,
        "purpose": "explicit_restoration_gated_support_regulation_replay",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "manifest_digest": manifest["manifest_digest"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "integration_row": integration_row,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "7_route_memory_regulation_composition",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    row = output["integration_row"]
    support = row["support_evidence"]
    prior = row["prior_disruption_evidence"]
    lines = [
        "# N10 Iteration 6 Explicit Restoration Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 6 consumed the N07 explicit-restoration lane and resumed the",
        "support-aware regulation replay only after source-backed restoration",
        "evidence. The restored lane remains above its survival threshold and",
        "references the same N09 withdrawal digest as the Iteration 5 disrupted",
        "support control.",
        "",
        "This closes the ALI3 support-sensitive regulation path for the bounded",
        "artifact-only support/regulation replay. It does not close ALI4, ALI5,",
        "ALI6, A5, A6, agency, or identity acceptance.",
        "",
        "```text",
        f"attempted_integration_level = {row['attempted_integration_level']}",
        f"accepted_integration_level = {row['accepted_integration_level']}",
        f"n10_category_level = {row['n10_category_level']}",
        f"ali3_status = {row['ali3_status']}",
        f"integration_outcome_tag = {row['integration_outcome_tag']}",
        f"support_state_tag = {row['support_state_tag']}",
        f"integration_allowed = {row['integration_allowed']}",
        f"positive_integration_row_emitted = {row['positive_integration_row_emitted']}",
        "route/memory consumed = false",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Support Evidence",
        "",
        "```json",
        json.dumps(support, indent=2, sort_keys=True),
        "```",
        "",
        "Interpretation:",
        "",
        "```text",
        f"final_A_support_retention = {support['final_A_support_retention']}",
        f"support_survival_threshold = {support['support_survival_threshold']}",
        f"support_loss_from_reference = {support['support_loss_from_reference']}",
        f"withdrawal_depth = {support['withdrawal_depth']}",
        f"restoration_fraction = {support['restoration_fraction']}",
        "```",
        "",
        "## Preserved Disruption History",
        "",
        "```json",
        json.dumps(prior, indent=2, sort_keys=True),
        "```",
        "",
        "The disrupted-support blocker remains part of the replay chain. The",
        "restored row resumes integration after that blocker; it does not erase",
        "or overwrite it.",
        "",
        "## Regulation Evidence",
        "",
        "```json",
        json.dumps(row["regulation_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Budget Boundary",
        "",
        "Iteration 6 claims source-artifact budget compatibility only. It does",
        "not claim one continuous packet ledger across separate N07 and N09",
        "runs.",
        "",
        "```text",
        f"budget_mode = {row['budget_mode']}",
        f"node_plus_packet_budget_error = {row['node_plus_packet_budget_error']}",
        f"support_lane_final_budget_error = {support['final_budget_error']}",
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 6 replay failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

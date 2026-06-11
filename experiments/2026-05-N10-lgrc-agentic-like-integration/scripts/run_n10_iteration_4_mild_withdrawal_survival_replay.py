#!/usr/bin/env python3
"""Run N10 Iteration 4 mild-withdrawal survival replay.

Iteration 4 is the mild-withdrawal companion to Iteration 3. It replays the
same N09 goal-proxy regulation evidence against the N07 mild support-weakening
lane and records whether support-aware regulation remains consumable. It does
not close ALI3/A5/A6 because disrupted-support and explicit-restoration
controls remain assigned to later iterations.
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
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_4_mild_withdrawal_survival_replay.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_4_mild_withdrawal_survival_replay.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_4_mild_withdrawal_survival_replay.py"
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


def build_integration_row(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n09: dict[str, Any],
    support_lane: dict[str, Any],
    fixture_lane: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    support_state_tag = source_support_state_tag(manifest, support_lane)
    row = {
        "integration_row_id": "n10_i4_mild_withdrawal_survival_replay_row_v1",
        "integration_level": "A4",
        "n10_category_level": "ALI2",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i4",
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
        "integration_outcome_tag": "support_aware_regulation_candidate",
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "not_applicable_ali2_support_aware_regulation",
        "proxy_budget_surface": "n09_source_proxy_budget_compatibility",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": baseline["native_policy_gaps"],
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "claim_flags": claim_flags,
        "category_boundary": (
            "ALI2 remains the ceiling for mild-withdrawal support-aware "
            "regulation replay. The row is A5-relevant support-survival "
            "evidence, but disrupted-support and explicit-restoration "
            "controls are required before ALI3/A5/A6 closeout."
        ),
        "a5_relevance": "mild_withdrawal_survival_component_not_a5_closeout",
        "fixture_lane": {
            "lane_id": fixture_lane["lane_id"],
            "expected_role": fixture_lane["expected_role"],
            "required_support_state_tag": fixture_lane[
                "required_support_state_tag"
            ],
            "source_support_lane_id": fixture_lane["source_support_lane_id"],
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
    return {
        "missing_identity_support_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "mild-withdrawal replay requires N07 Iteration 13 support lane evidence",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "mild-withdrawal replay requires N09 GPR closeout evidence",
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
            "reason": "mild support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary",
        },
        "hidden_support_assumption": {
            "control_passed": support["support_survival_passed"] is True
            and support["final_A_support_retention"]
            >= support["support_survival_threshold"],
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "support survival is backed by the N07 lane threshold, not by an N10-side assumption",
        },
        "hidden_restoration_not_used": {
            "control_passed": support["restoration_fraction"] == 0.0,
            "primary_blocker": blockers["restoration_required_but_missing"],
            "reason": "the mild-withdrawal lane remains above threshold without consuming restoration evidence",
        },
        "budget_surface_ambiguity": {
            "control_passed": integration_row["node_plus_packet_budget_error"] == 0.0
            and support["final_budget_error"] == 0.0
            and integration_row["regulation_evidence"]["source_budget_control_passed"]
            is True,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "Iteration 4 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in integration_row["claim_flags"].values()
            ),
            "primary_blocker": blockers["claim_promotion"],
            "reason": "mild withdrawal survival does not emit agency, A6, identity acceptance, or goal-ownership claims",
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
        "n10_category_level_is_ali2": integration_row["n10_category_level"] == "ALI2",
        "integration_level_is_a4_not_a6": integration_row["integration_level"] == "A4",
        "support_state_tag_is_mild_withdrawal": integration_row[
            "support_state_tag"
        ]
        == "mild_withdrawal_survives",
        "fixture_required_support_state_tag_matched": integration_row[
            "support_state_tag"
        ]
        == fixture["required_support_state_tag"],
        "mild_support_lane_survives": support["support_survival_passed"] is True,
        "mild_support_retention_meets_threshold": support[
            "final_A_support_retention"
        ]
        >= support["support_survival_threshold"],
        "mild_support_budget_error_zero": support["final_budget_error"] == 0.0,
        "no_hidden_restoration_used": support["restoration_fraction"] == 0.0,
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
        "route_memory_not_consumed_for_ali2": integration_row["route_choice_artifact"]
        is None
        and integration_row["memory_affordance_artifact"] is None,
        "claim_flags_all_false": all(
            value is False for value in integration_row["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "a5_relevant_not_a5_closeout": integration_row["a5_relevance"]
        == "mild_withdrawal_survival_component_not_a5_closeout",
        "a6_not_supported_by_iteration_4": integration_row["n10_category_level"]
        != "ALI6",
        "src_clean_for_iteration_4": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n09 = load_json(source_path(baseline, "n09_hypothesis_a_closeout"))
    support_lane = find_lane(n07_i13["withdrawal_lanes"], "mild_support_weakening")
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "mild_support_weakening"
    )
    fixture_lane = find_fixture_lane(manifest, "mild_withdrawal_survival_replay")
    source_artifacts, source_reports = build_source_records(baseline)
    integration_row = build_integration_row(
        baseline,
        manifest,
        n09,
        support_lane,
        fixture_lane,
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
                "step": "load_n07_mild_withdrawal_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
                "support_survival_threshold": support_lane[
                    "support_survival_threshold"
                ],
            },
            {
                "step": "compare_to_iteration_3_support_intact_replay",
                "artifact": source_artifacts[
                    "n10_iteration_3_support_aware_regulation_replay"
                ]["path"],
                "digest": source_artifacts[
                    "n10_iteration_3_support_aware_regulation_replay"
                ]["sha256"],
            },
            {
                "step": "emit_mild_withdrawal_support_aware_regulation_row",
                "integration_row_digest": integration_row["integration_row_digest"],
                "n10_category_level": integration_row["n10_category_level"],
            },
        ],
        "n07_source_status": n07_i13.get("status"),
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 4 passes if N10 records whether support-aware regulation "
            "remains consumable under mild support weakening, with source-backed "
            "support survival and no hidden restoration."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_4_mild_withdrawal_survival_replay_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 4,
        "purpose": "mild_withdrawal_survival_replay_no_route_memory_composition",
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
        "next_iteration": "5_disrupted_support_control",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    row = output["integration_row"]
    support = row["support_evidence"]
    lines = [
        "# N10 Iteration 4 Mild Withdrawal Survival Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 4 replayed the N09 goal-proxy regulation evidence against",
        "the N07 mild support-weakening lane. The support lane remains above",
        "its survival threshold without restoration, so the row remains",
        "consumable as ALI2 support-aware regulation evidence.",
        "",
        "This is A5-relevant support-survival evidence, but it does not close",
        "ALI3, A5, or A6. Disrupted-support and explicit-restoration controls",
        "remain assigned to Iterations 5 and 6.",
        "",
        "```text",
        f"integration_level = {row['integration_level']}",
        f"n10_category_level = {row['n10_category_level']}",
        f"integration_outcome_tag = {row['integration_outcome_tag']}",
        f"support_state_tag = {row['support_state_tag']}",
        f"a5_relevance = {row['a5_relevance']}",
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
        "The mild-withdrawal lane weakens support but does not destroy it. N10",
        "therefore keeps the support-aware regulation row consumable while",
        "recording that this is not yet a disruption/restoration closeout.",
        "",
        "## Regulation Evidence",
        "",
        "```json",
        json.dumps(row["regulation_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Budget Boundary",
        "",
        "Iteration 4 claims source-artifact budget compatibility only. It does",
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
        raise SystemExit(f"Iteration 4 replay failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

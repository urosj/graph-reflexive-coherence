#!/usr/bin/env python3
"""Run N10 Iteration 3 support-aware regulation replay.

Iteration 3 is the first positive N10 replay, but it is intentionally bounded:
it attaches N09 goal-proxy regulation evidence to the N07 support-intact
baseline. It does not consume route/memory as a full ALI4 composition and does
not support A6/ALI6.
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
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_3_support_aware_regulation_replay.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_3_support_aware_regulation_replay.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_3_support_aware_regulation_replay.py"
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


def find_lane(manifest: dict[str, Any], lane_id: str) -> dict[str, Any]:
    for lane in manifest["source_support_lanes"]:
        if lane.get("lane_id") == lane_id:
            return lane
    raise KeyError(f"support lane not found: {lane_id}")


def build_source_records(baseline: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
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
    }
    for key in artifact_keys:
        path = source_path(baseline, key)
        source_artifacts[key] = {
            "path": rel(path),
            "sha256": digest_file(path),
            "baseline_sha256": baseline["source_artifacts"][key]["sha256"],
            "matches_baseline": digest_file(path)
            == baseline["source_artifacts"][key]["sha256"],
        }

    source_reports = {}
    for key in report_keys:
        path = report_path(baseline, key)
        source_reports[key] = {
            "path": rel(path),
            "sha256": digest_file(path),
            "baseline_sha256": baseline["source_reports"][key]["sha256"],
            "matches_baseline": digest_file(path)
            == baseline["source_reports"][key]["sha256"],
        }
    return source_artifacts, source_reports


def build_integration_row(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n09: dict[str, Any],
    support_lane: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    row = {
        "integration_row_id": "n10_i3_support_aware_regulation_replay_row_v1",
        "integration_level": "A4",
        "n10_category_level": "ALI2",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i3",
        "scheduler_event_index": None,
        "source_experiment_ids": ["N07", "N09"],
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
        "support_state_tag": "support_intact_survives",
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
            "ALI2 consumes N09 regulation and N07 support-intact evidence only; "
            "route and memory composition starts at ALI4."
        ),
        "support_evidence": {
            "source_lane_id": support_lane["lane_id"],
            "lane_digest": support_lane["lane_digest"],
            "support_survival_passed": support_lane["support_survival_passed"],
            "final_A_support_retention": support_lane["final_A_support_retention"],
            "final_basin_separability": support_lane["final_basin_separability"],
            "final_budget_error": support_lane["final_budget_error"],
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
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    return {
        "missing_identity_support_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "support-aware replay requires N07 Iteration 13 support lane evidence",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "support-aware replay requires N09 GPR closeout evidence",
        },
        "source_artifact_digest_mismatch": {
            "control_passed": all(
                value.get("matches_baseline", True) for value in source_artifacts.values()
            ),
            "primary_blocker": blockers["source_artifact_digest_mismatch"],
            "reason": "N07/N09 source artifact digests are rechecked against Iteration 1",
        },
        "hidden_support_assumption": {
            "control_passed": integration_row["support_evidence"][
                "support_survival_passed"
            ]
            is True,
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "support state is read from N07 Iteration 13 support_intact_reference lane",
        },
        "budget_surface_ambiguity": {
            "control_passed": integration_row["node_plus_packet_budget_error"] == 0.0
            and integration_row["support_evidence"]["final_budget_error"] == 0.0
            and integration_row["regulation_evidence"]["source_budget_control_passed"]
            is True,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "Iteration 3 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in integration_row["claim_flags"].values()
            ),
            "primary_blocker": blockers["claim_promotion"],
            "reason": "ALI2 support-aware regulation replay cannot emit agency, A6, identity acceptance, or goal-ownership claims",
        },
    }


def validate_output(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n09: dict[str, Any],
    integration_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    row_fields = set(integration_row)
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
        "support_state_tag_valid": integration_row["support_state_tag"]
        in manifest["allowed_values"]["support_state_tag"],
        "support_intact_lane_survives": integration_row["support_evidence"][
            "support_survival_passed"
        ]
        is True,
        "support_lane_budget_error_zero": integration_row["support_evidence"][
            "final_budget_error"
        ]
        == 0.0,
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
        "a6_not_supported_by_iteration_3": integration_row["n10_category_level"]
        != "ALI6",
        "src_clean_for_iteration_3": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n09 = load_json(source_path(baseline, "n09_hypothesis_a_closeout"))
    support_lane = find_lane(manifest, "support_intact_reference")
    source_artifacts, source_reports = build_source_records(baseline)
    integration_row = build_integration_row(
        baseline, manifest, n09, support_lane, source_artifacts, source_reports
    )
    controls = build_controls(manifest, integration_row, source_artifacts)
    checks = validate_output(
        baseline, manifest, n09, integration_row, source_artifacts, controls
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
                "step": "load_n07_support_intact_baseline_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
            },
            {
                "step": "emit_support_aware_regulation_row",
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
            "Iteration 3 passes if N09 goal-proxy regulation can be replayed as "
            "support-aware under the N07 support-intact baseline without hidden "
            "support assumptions or claim promotion."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_3_support_aware_regulation_replay_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 3,
        "purpose": "support_aware_regulation_replay_no_route_memory_composition",
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
        "next_iteration": "4_mild_withdrawal_survival_replay",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    row = output["integration_row"]
    lines = [
        "# N10 Iteration 3 Support-Aware Regulation Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 3 replayed N09 goal-proxy regulation as support-aware under",
        "the N07 support-intact baseline. This is an ALI2 row, not full",
        "route-memory-regulation composition and not A6/ALI6.",
        "",
        "```text",
        f"integration_level = {row['integration_level']}",
        f"n10_category_level = {row['n10_category_level']}",
        f"integration_outcome_tag = {row['integration_outcome_tag']}",
        "route/memory consumed = false",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Support Evidence",
        "",
        "```json",
        json.dumps(row["support_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Regulation Evidence",
        "",
        "```json",
        json.dumps(row["regulation_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Budget Boundary",
        "",
        "Iteration 3 claims source-artifact budget compatibility only. It does",
        "not claim one continuous packet ledger across separate N07 and N09",
        "runs.",
        "",
        "```text",
        f"budget_mode = {row['budget_mode']}",
        f"node_plus_packet_budget_error = {row['node_plus_packet_budget_error']}",
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
        raise SystemExit(f"Iteration 3 replay failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

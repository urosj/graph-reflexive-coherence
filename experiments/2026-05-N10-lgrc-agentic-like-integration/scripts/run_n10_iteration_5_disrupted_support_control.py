#!/usr/bin/env python3
"""Run N10 Iteration 5 disrupted-support control.

Iteration 5 consumes the N07 N09-matched support withdrawal lane and attempts
the same support-aware regulation replay used in Iterations 3 and 4. The
expected result is fail-closed: the support lane is below its survival
threshold, no restoration evidence is consumed, and no positive integration row
may be emitted.
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
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_5_disrupted_support_control.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_5_disrupted_support_control.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_5_disrupted_support_control.py"
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


def build_blocked_integration_record(
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
    blocker = manifest["control_blockers"]["support_disrupted_but_integration_allowed"]
    support_below_threshold = (
        support_lane["final_A_support_retention"]
        < support_lane["support_survival_threshold"]
    )
    no_restoration = support_lane["restoration_fraction"] == 0.0
    record = {
        "integration_row_id": "n10_i5_disrupted_support_blocked_attempt_v1",
        "integration_level": "A4",
        "attempted_integration_level": "A4",
        "accepted_integration_level": None,
        "n10_category_level": "ALI3",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i5",
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
        "integration_outcome_tag": "support_disruption_blocked_integration",
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "not_applicable_ali3_support_disruption_control",
        "proxy_budget_surface": "n09_source_proxy_budget_compatibility",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": baseline["native_policy_gaps"],
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "claim_flags": claim_flags,
        "integration_allowed": False,
        "positive_integration_row_emitted": False,
        "primary_blocker": blocker,
        "blocker_reason": (
            "N07 N09-matched support withdrawal is below the survival threshold "
            "and has no explicit restoration lane attached."
        ),
        "category_boundary": (
            "Iteration 5 is an ALI3 support-sensitivity control component. It "
            "does not close ALI3 until Iteration 6 verifies explicit "
            "restoration-gated resumption."
        ),
        "ali3_relevance": "disrupted_support_control_component_not_ali3_closeout",
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
            "n09_withdrawal_digest": support_lane["n09_withdrawal_digest"],
            "support_below_threshold": support_below_threshold,
            "no_restoration": no_restoration,
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
    return with_digest(record, "integration_row_digest")


def build_controls(
    manifest: dict[str, Any],
    blocked_record: dict[str, Any],
    source_artifacts: dict[str, Any],
    manifest_support_lane: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    support = blocked_record["support_evidence"]
    return {
        "missing_identity_support_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "disrupted-support control requires N07 Iteration 13 support lane evidence",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": True,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "disrupted-support control requires N09 GPR closeout evidence",
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
            "reason": "disrupted support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary",
        },
        "support_disrupted_but_integration_allowed": {
            "control_passed": support["support_survival_passed"] is False
            and support["support_below_threshold"] is True
            and blocked_record["integration_allowed"] is False
            and blocked_record["positive_integration_row_emitted"] is False,
            "primary_blocker": blockers["support_disrupted_but_integration_allowed"],
            "reason": "the N09-matched support withdrawal is below threshold, so the attempted support-aware regulation replay is blocked",
        },
        "restoration_required_but_missing": {
            "control_passed": support["restoration_fraction"] == 0.0
            and blocked_record["integration_allowed"] is False,
            "primary_blocker": blockers["restoration_required_but_missing"],
            "reason": "integration may resume only in a later explicit-restoration lane",
        },
        "budget_surface_ambiguity": {
            "control_passed": blocked_record["node_plus_packet_budget_error"] == 0.0
            and support["final_budget_error"] == 0.0
            and blocked_record["regulation_evidence"]["source_budget_control_passed"]
            is True,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "Iteration 5 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in blocked_record["claim_flags"].values()
            )
            and blocked_record["positive_integration_row_emitted"] is False,
            "primary_blocker": blockers["claim_promotion"],
            "reason": "disrupted support cannot emit agency, A6, identity acceptance, or goal-ownership claims",
        },
    }


def validate_output(
    manifest: dict[str, Any],
    n09: dict[str, Any],
    blocked_record: dict[str, Any],
    source_artifacts: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    row_fields = set(blocked_record)
    support = blocked_record["support_evidence"]
    fixture = blocked_record["fixture_lane"]
    return {
        "integration_record_required_fields_present": required_fields.issubset(
            row_fields
        ),
        "integration_record_digest_valid": blocked_record["integration_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in blocked_record.items()
                if key != "integration_row_digest"
            }
        ),
        "n10_category_level_is_ali3_control_component": blocked_record[
            "n10_category_level"
        ]
        == "ALI3",
        "attempted_integration_level_is_a4": blocked_record[
            "attempted_integration_level"
        ]
        == "A4",
        "accepted_integration_level_absent": blocked_record[
            "accepted_integration_level"
        ]
        is None,
        "support_state_tag_is_n09_matched_disruption": blocked_record[
            "support_state_tag"
        ]
        == "n09_matched_withdrawal_disrupts_support",
        "fixture_required_support_state_tag_matched": blocked_record[
            "support_state_tag"
        ]
        == fixture["required_support_state_tag"],
        "disrupted_support_lane_fails_survival": support[
            "support_survival_passed"
        ]
        is False,
        "disrupted_support_retention_below_threshold": support[
            "final_A_support_retention"
        ]
        < support["support_survival_threshold"],
        "disrupted_support_budget_error_zero": support["final_budget_error"] == 0.0,
        "no_restoration_available": support["restoration_fraction"] == 0.0,
        "integration_allowed_false": blocked_record["integration_allowed"] is False,
        "positive_integration_row_not_emitted": blocked_record[
            "positive_integration_row_emitted"
        ]
        is False,
        "primary_blocker_recorded": blocked_record["primary_blocker"]
        == manifest["control_blockers"]["support_disrupted_but_integration_allowed"],
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
        "artifact_only_replay": blocked_record["artifact_only"] is True
        and blocked_record["runtime_state_used"] is False,
        "route_memory_not_consumed_for_control": blocked_record[
            "route_choice_artifact"
        ]
        is None
        and blocked_record["memory_affordance_artifact"] is None,
        "claim_flags_all_false": all(
            value is False for value in blocked_record["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "ali3_relevant_not_ali3_closeout": blocked_record["ali3_relevance"]
        == "disrupted_support_control_component_not_ali3_closeout",
        "a6_not_supported_by_iteration_5": blocked_record["integration_level"]
        != "A6",
        "src_clean_for_iteration_5": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n09 = load_json(source_path(baseline, "n09_hypothesis_a_closeout"))
    support_lane = find_lane(
        n07_i13["withdrawal_lanes"], "n09_matched_partial_support_withdrawal"
    )
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "n09_matched_partial_support_withdrawal"
    )
    fixture_lane = find_fixture_lane(manifest, "disrupted_support_control")
    source_artifacts, source_reports = build_source_records(baseline)
    blocked_record = build_blocked_integration_record(
        baseline,
        manifest,
        n09,
        support_lane,
        fixture_lane,
        source_artifacts,
        source_reports,
    )
    controls = build_controls(
        manifest, blocked_record, source_artifacts, manifest_support_lane
    )
    checks = validate_output(
        manifest, n09, blocked_record, source_artifacts, controls
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
                "step": "load_n07_n09_matched_disrupted_support_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
                "support_survival_threshold": support_lane[
                    "support_survival_threshold"
                ],
                "n09_withdrawal_digest": support_lane["n09_withdrawal_digest"],
            },
            {
                "step": "attempt_support_aware_regulation_replay",
                "attempted_integration_level": blocked_record[
                    "attempted_integration_level"
                ],
                "integration_allowed": blocked_record["integration_allowed"],
                "primary_blocker": blocked_record["primary_blocker"],
            },
            {
                "step": "emit_blocked_support_disruption_record",
                "integration_row_digest": blocked_record["integration_row_digest"],
                "n10_category_level": blocked_record["n10_category_level"],
                "positive_integration_row_emitted": blocked_record[
                    "positive_integration_row_emitted"
                ],
            },
        ],
        "n07_source_status": n07_i13.get("status"),
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 5 passes if N10 fails closed when the identity/support "
            "baseline is disrupted. A disrupted-support lane must not become "
            "an agentic-like integration row unless explicit restoration "
            "evidence exists."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_5_disrupted_support_control_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 5,
        "purpose": "disrupted_support_control_fail_closed_no_positive_integration_row",
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
        "blocked_integration_record": blocked_record,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "6_explicit_restoration_replay",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    record = output["blocked_integration_record"]
    support = record["support_evidence"]
    lines = [
        "# N10 Iteration 5 Disrupted Support Control",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 5 consumed the N07 N09-matched partial-withdrawal lane and",
        "attempted the same support-aware regulation replay used in Iterations",
        "3 and 4. The support lane is below its survival threshold and has no",
        "explicit restoration evidence, so N10 blocks the integration attempt.",
        "",
        "This is an ALI3 support-sensitivity control component, not an ALI3",
        "closeout by itself. Iteration 6 must still show explicit restoration",
        "before integration can resume after disruption.",
        "",
        "```text",
        f"attempted_integration_level = {record['attempted_integration_level']}",
        f"accepted_integration_level = {record['accepted_integration_level']}",
        f"n10_category_level = {record['n10_category_level']}",
        f"integration_outcome_tag = {record['integration_outcome_tag']}",
        f"support_state_tag = {record['support_state_tag']}",
        f"integration_allowed = {record['integration_allowed']}",
        f"positive_integration_row_emitted = {record['positive_integration_row_emitted']}",
        f"primary_blocker = {record['primary_blocker']}",
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
        "The N09-matched withdrawal disrupts support because retention drops",
        "below threshold. N10 therefore records a blocked attempt instead of a",
        "positive support-aware regulation row.",
        "",
        "## Regulation Evidence",
        "",
        "```json",
        json.dumps(record["regulation_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Budget Boundary",
        "",
        "Iteration 5 claims source-artifact budget compatibility only. It does",
        "not claim one continuous packet ledger across separate N07 and N09",
        "runs.",
        "",
        "```text",
        f"budget_mode = {record['budget_mode']}",
        f"node_plus_packet_budget_error = {record['node_plus_packet_budget_error']}",
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
        raise SystemExit(f"Iteration 5 control failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

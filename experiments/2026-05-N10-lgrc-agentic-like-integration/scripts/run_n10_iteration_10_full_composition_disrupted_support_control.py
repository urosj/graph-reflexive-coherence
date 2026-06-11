#!/usr/bin/env python3
"""Run N10 Iteration 10 full-composition disrupted-support control.

Iteration 10 strengthens the earlier Iteration 5 support-disruption control.
It takes the accepted Iteration 9 Hypothesis A full route-memory-support-
regulation chain as the positive source, then attempts to replay that full
composition under the N07 N09-matched disrupted-support lane.

The expected result is fail-closed: route, memory, and regulation source links
remain valid, but the full composition is blocked because the identity/support
baseline is disrupted and no explicit restoration evidence is attached.
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
ITERATION_7_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
)
ITERATION_8_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_8_bounded_repeated_integration.json"
)
ITERATION_9_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
)
OUTPUT_PATH = (
    EXPERIMENT
    / "outputs"
    / "n10_iteration_10_full_composition_disrupted_support_control.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports"
    / "n10_iteration_10_full_composition_disrupted_support_control.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_10_full_composition_disrupted_support_control.py"
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
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def all_claim_flags_false(row: dict[str, Any]) -> bool:
    return all(value is False for value in row["claim_flags"].values())


def row_digest_valid(row: dict[str, Any], digest_field: str = "integration_row_digest") -> bool:
    return row[digest_field] == digest_value(
        {key: value for key, value in row.items() if key != digest_field}
    )


def prior_output_digest_valid(artifact: dict[str, Any]) -> bool:
    if "output_digest" not in artifact:
        return True
    return artifact["output_digest"] == output_digest(artifact)


def source_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_artifacts"][key]["path"]


def report_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_reports"][key]["path"]


def find_lane(rows: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("lane_id") == lane_id:
            return row
    raise KeyError(f"lane not found: {lane_id}")


def build_source_records(
    baseline: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_paths = {
        "n10_baseline_inventory": BASELINE_PATH,
        "n10_fixture_manifest": MANIFEST_PATH,
        "n10_iteration_7_route_memory_regulation_composition": ITERATION_7_PATH,
        "n10_iteration_8_bounded_repeated_integration": ITERATION_8_PATH,
        "n10_iteration_9_hypothesis_a_closeout": ITERATION_9_PATH,
    }
    report_paths = {
        "n10_iteration_7_route_memory_regulation_composition": (
            EXPERIMENT / "reports" / "n10_iteration_7_route_memory_regulation_composition.md"
        ),
        "n10_iteration_8_bounded_repeated_integration": (
            EXPERIMENT / "reports" / "n10_iteration_8_bounded_repeated_integration.md"
        ),
        "n10_iteration_9_hypothesis_a_closeout": (
            EXPERIMENT / "reports" / "n10_iteration_9_artifact_only_closeout.md"
        ),
    }

    baseline_artifact_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]
    baseline_report_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]

    source_artifacts = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in artifact_paths.items()
    }
    for key in baseline_artifact_keys:
        path = source_path(baseline, key)
        current_digest = digest_file(path)
        source_artifacts[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_artifacts"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_artifacts"][key]["sha256"],
        }

    source_reports = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in report_paths.items()
        if path.exists()
    }
    for key in baseline_report_keys:
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


def build_blocked_full_composition_record(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    i7: dict[str, Any],
    i8: dict[str, Any],
    i9: dict[str, Any],
    support_lane: dict[str, Any],
    manifest_support_lane: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    blocker = manifest["control_blockers"]["support_disrupted_but_integration_allowed"]
    source_support_tag = manifest["allowed_values"]["source_support_outcome_map"][
        support_lane["identity_support_outcome_tag"]
    ]
    support_below_threshold = (
        support_lane["final_A_support_retention"]
        < support_lane["support_survival_threshold"]
    )
    route_memory_row = i7["integration_row"]
    bounded_row = i8["main_integration_row"]
    closeout = i9["closeout"]
    record = {
        "integration_row_id": "n10_i10_full_composition_disrupted_support_blocked_v1",
        "integration_level": "A0",
        "attempted_integration_level": closeout["integration_level"],
        "accepted_integration_level": None,
        "n10_category_level": "ALI3",
        "attempted_n10_category_level": closeout["n10_category_level"],
        "accepted_n10_category_level": None,
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i10",
        "scheduler_event_index": None,
        "source_experiment_ids": ["N06", "N07", "N08", "N09", "N10"],
        "source_artifacts": {
            key: value["path"] for key, value in source_artifacts.items()
        },
        "source_reports": {
            key: value["path"] for key, value in source_reports.items()
        },
        "source_artifact_digests": {
            key: value["sha256"] for key, value in source_artifacts.items()
        },
        "route_choice_artifact": "n06_closeout",
        "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
        "memory_affordance_artifact": "n08_hypothesis_a_closeout",
        "memory_affordance_digest": source_artifacts["n08_hypothesis_a_closeout"][
            "sha256"
        ],
        "identity_support_artifact": "n07_withdrawal_baseline",
        "identity_support_digest": source_artifacts["n07_withdrawal_baseline"][
            "sha256"
        ],
        "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
        "goal_proxy_regulation_digest": source_artifacts["n09_hypothesis_a_closeout"][
            "sha256"
        ],
        "support_state_tag": source_support_tag,
        "route_context_tag": route_memory_row["route_context_tag"],
        "memory_scope_tag": route_memory_row["memory_scope_tag"],
        "regulation_scope_tag": route_memory_row["regulation_scope_tag"],
        "integration_outcome_tag": "support_disruption_blocked_integration",
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "n08_source_memory_budget_compatibility",
        "proxy_budget_surface": "n09_source_proxy_budget_compatibility",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": closeout["native_policy_gaps_preserved"],
        "blocked_claims": closeout["blocked_claims"],
        "claim_flags": claim_flags,
        "integration_allowed": False,
        "positive_integration_row_emitted": False,
        "primary_blocker": blocker,
        "blocker_reason": (
            "The full route-memory-support-regulation chain is source-backed, "
            "but the selected N07 support lane is below its survival threshold "
            "and has no explicit restoration attached."
        ),
        "full_composition_source": {
            "iteration_7_row_digest": route_memory_row["integration_row_digest"],
            "iteration_8_main_row_digest": bounded_row["integration_row_digest"],
            "iteration_8_window_digest": bounded_row["bounded_window"][
                "window_digest"
            ],
            "iteration_9_closeout_row_digest": closeout["closeout_row_digest"],
            "iteration_9_ceiling": closeout["final_n10_ceiling"],
            "iteration_9_ceiling_supported": closeout["final_ceiling_supported"],
        },
        "preserved_source_links": {
            "route_choice_link_present": True,
            "memory_affordance_link_present": True,
            "identity_support_link_present": True,
            "goal_proxy_regulation_link_present": True,
            "n10_hypothesis_a_closeout_link_present": True,
        },
        "support_evidence": {
            "source_lane_id": support_lane["lane_id"],
            "lane_digest": support_lane["lane_digest"],
            "manifest_lane_digest": manifest_support_lane["lane_digest"],
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
            "no_restoration": support_lane["restoration_fraction"] == 0.0,
        },
        "route_evidence_preserved": {
            "route_context_tag": route_memory_row["route_context_tag"],
            "route_choice_artifact": "n06_closeout",
            "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
            "source_scope": "N06_SC6_selection_only_pre_topology_commit",
        },
        "memory_evidence_preserved": {
            "memory_scope_tag": route_memory_row["memory_scope_tag"],
            "memory_affordance_artifact": "n08_hypothesis_a_closeout",
            "memory_affordance_digest": source_artifacts[
                "n08_hypothesis_a_closeout"
            ]["sha256"],
            "source_scope": "N08_MEM6_serialized_producer_policy_memory_or_trail",
        },
        "regulation_evidence_preserved": {
            "regulation_scope_tag": route_memory_row["regulation_scope_tag"],
            "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
            "goal_proxy_regulation_digest": source_artifacts[
                "n09_hypothesis_a_closeout"
            ]["sha256"],
            "source_scope": "N09_GPR6_goal_proxy_regulation_closeout",
        },
        "hypothesis_b_relevance": (
            "This is the full-composition support-disruption half of the "
            "Hypothesis B matrix. Iteration 11 must still show explicit "
            "restoration-gated full-composition resumption."
        ),
        "budget_mode": "source_artifact_budget_compatibility_not_single_runtime_continuity",
    }
    return with_digest(record, "integration_row_digest")


def build_controls(
    manifest: dict[str, Any],
    blocked_record: dict[str, Any],
    source_artifacts: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    support = blocked_record["support_evidence"]
    return {
        "missing_route_choice_artifact": {
            "control_passed": blocked_record["route_choice_artifact"] is not None,
            "primary_blocker": blockers["missing_route_choice_artifact"],
            "reason": "full-composition control keeps the N06 route-choice source link present",
        },
        "missing_memory_affordance_artifact": {
            "control_passed": blocked_record["memory_affordance_artifact"] is not None,
            "primary_blocker": blockers["missing_memory_affordance_artifact"],
            "reason": "full-composition control keeps the N08 memory/trail source link present",
        },
        "missing_identity_support_artifact": {
            "control_passed": blocked_record["identity_support_artifact"] is not None,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "full-composition control consumes the N07 disrupted support lane",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": blocked_record["goal_proxy_regulation_artifact"] is not None,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "full-composition control keeps the N09 goal-proxy regulation source link present",
        },
        "source_artifact_digest_mismatch": {
            "control_passed": all(
                value.get("matches_baseline", True) for value in source_artifacts.values()
            ),
            "primary_blocker": blockers["source_artifact_digest_mismatch"],
            "reason": "N06/N07/N08/N09 source digests are checked against the Iteration 1 baseline",
        },
        "stale_identity_support_baseline": {
            "control_passed": support["lane_digest"] == support["manifest_lane_digest"],
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "the disrupted lane digest is matched against the frozen N10 manifest lane summary",
        },
        "support_disrupted_but_full_composition_allowed": {
            "control_passed": support["support_survival_passed"] is False
            and support["support_below_threshold"] is True
            and blocked_record["integration_allowed"] is False
            and blocked_record["positive_integration_row_emitted"] is False,
            "primary_blocker": blockers["support_disrupted_but_integration_allowed"],
            "reason": "the A6/ALI6 source chain is blocked because support is disrupted",
        },
        "restoration_required_but_missing": {
            "control_passed": support["restoration_fraction"] == 0.0
            and blocked_record["integration_allowed"] is False,
            "primary_blocker": blockers["restoration_required_but_missing"],
            "reason": "full composition may resume only through an explicit restoration record",
        },
        "artifact_only_replay_missing_link": {
            "control_passed": all(
                blocked_record["preserved_source_links"].values()
            )
            and blocked_record["artifact_only"] is True
            and blocked_record["runtime_state_used"] is False,
            "primary_blocker": blockers["artifact_only_replay_missing_link"],
            "reason": "the blocked row is still reconstructable from exported source artifacts only",
        },
        "hidden_experiment_side_steering": {
            "control_passed": blocked_record["integration_allowed"] is False,
            "primary_blocker": blockers["hidden_experiment_side_steering"],
            "reason": "N10 does not override the disrupted support lane by report-side steering",
        },
        "budget_surface_ambiguity": {
            "control_passed": blocked_record["node_plus_packet_budget_error"] == 0.0
            and support["final_budget_error"] == 0.0,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "route, memory, support, and proxy budgets remain source-artifact compatibility checks, not a cross-run live ledger claim",
        },
        "claim_promotion": {
            "control_passed": all_claim_flags_false(blocked_record)
            and blocked_record["attempted_integration_level"] == "A6"
            and blocked_record["accepted_integration_level"] is None,
            "primary_blocker": blockers["claim_promotion"],
            "reason": "blocked full composition cannot emit agency, identity acceptance, goal ownership, or fully native agentic-like claims",
        },
    }


def build_checks(
    manifest: dict[str, Any],
    i7: dict[str, Any],
    i8: dict[str, Any],
    i9: dict[str, Any],
    blocked_record: dict[str, Any],
    controls: dict[str, Any],
    source_artifacts: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    row_fields = set(blocked_record)
    support = blocked_record["support_evidence"]
    return {
        "integration_record_required_fields_present": required_fields.issubset(
            row_fields
        ),
        "integration_record_digest_valid": row_digest_valid(blocked_record),
        "iteration_9_hypothesis_a_closeout_available": i9["status"] == "passed"
        and i9["closeout"]["final_ceiling_supported"] is True,
        "attempted_integration_level_is_a6": blocked_record[
            "attempted_integration_level"
        ]
        == "A6",
        "attempted_n10_category_level_is_ali6": blocked_record[
            "attempted_n10_category_level"
        ]
        == "ALI6",
        "accepted_integration_level_absent": blocked_record[
            "accepted_integration_level"
        ]
        is None,
        "positive_integration_row_not_emitted": blocked_record[
            "positive_integration_row_emitted"
        ]
        is False,
        "integration_allowed_false": blocked_record["integration_allowed"] is False,
        "primary_blocker_support_specific": blocked_record["primary_blocker"]
        == manifest["control_blockers"]["support_disrupted_but_integration_allowed"],
        "full_composition_sources_preserved": all(
            blocked_record["preserved_source_links"].values()
        ),
        "route_link_present": blocked_record["route_choice_artifact"] == "n06_closeout",
        "memory_link_present": blocked_record["memory_affordance_artifact"]
        == "n08_hypothesis_a_closeout",
        "regulation_link_present": blocked_record["goal_proxy_regulation_artifact"]
        == "n09_hypothesis_a_closeout",
        "support_state_tag_is_n09_matched_disruption": blocked_record[
            "support_state_tag"
        ]
        == "n09_matched_withdrawal_disrupts_support",
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
        "route_context_selection_only_preserved": blocked_record[
            "route_context_tag"
        ]
        == "route_context_selection_only"
        and i7["integration_row"]["route_context_tag"] == "route_context_selection_only",
        "memory_scope_preserved": blocked_record["memory_scope_tag"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "iteration_8_main_window_available": i8["main_integration_row"][
            "n10_category_level"
        ]
        == "ALI5",
        "source_artifact_digests_match_baseline": all(
            value.get("matches_baseline", True) for value in source_artifacts.values()
        ),
        "artifact_only_replay": blocked_record["artifact_only"] is True
        and blocked_record["runtime_state_used"] is False,
        "claim_flags_all_false": all_claim_flags_false(blocked_record),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "a6_not_accepted_under_disrupted_support": blocked_record[
            "accepted_integration_level"
        ]
        is None
        and blocked_record["accepted_n10_category_level"] is None,
        "src_clean_for_iteration_10": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    i7 = load_json(ITERATION_7_PATH)
    i8 = load_json(ITERATION_8_PATH)
    i9 = load_json(ITERATION_9_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    support_lane = find_lane(
        n07_i13["withdrawal_lanes"], "n09_matched_partial_support_withdrawal"
    )
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "n09_matched_partial_support_withdrawal"
    )
    source_artifacts, source_reports = build_source_records(baseline)
    blocked_record = build_blocked_full_composition_record(
        baseline,
        manifest,
        i7,
        i8,
        i9,
        support_lane,
        manifest_support_lane,
        source_artifacts,
        source_reports,
    )
    controls = build_controls(manifest, blocked_record, source_artifacts)
    checks = build_checks(
        manifest, i7, i8, i9, blocked_record, controls, source_artifacts
    )
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_hypothesis_a_closeout",
                "artifact": rel(ITERATION_9_PATH),
                "closeout_row_digest": i9["closeout"]["closeout_row_digest"],
                "hypothesis_a_ceiling": i9["closeout"]["final_n10_ceiling"],
            },
            {
                "step": "preserve_route_memory_regulation_source_links",
                "iteration_7_row_digest": i7["integration_row"][
                    "integration_row_digest"
                ],
                "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
                "memory_affordance_digest": source_artifacts[
                    "n08_hypothesis_a_closeout"
                ]["sha256"],
                "goal_proxy_regulation_digest": source_artifacts[
                    "n09_hypothesis_a_closeout"
                ]["sha256"],
            },
            {
                "step": "replace_support_lane_with_n09_matched_disruption",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
                "support_survival_passed": support_lane["support_survival_passed"],
            },
            {
                "step": "attempt_full_composition_replay",
                "attempted_integration_level": blocked_record[
                    "attempted_integration_level"
                ],
                "attempted_n10_category_level": blocked_record[
                    "attempted_n10_category_level"
                ],
                "integration_allowed": blocked_record["integration_allowed"],
                "primary_blocker": blocked_record["primary_blocker"],
            },
            {
                "step": "emit_blocked_full_composition_record",
                "integration_row_digest": blocked_record["integration_row_digest"],
                "positive_integration_row_emitted": blocked_record[
                    "positive_integration_row_emitted"
                ],
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 10 passes if the full Hypothesis A route-memory-support-"
            "regulation composition blocks or downgrades under the N07 "
            "N09-matched disrupted-support lane with a distinct support-"
            "specific blocker, while preserving route, memory, and regulation "
            "source links and all claim boundaries."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_10_full_composition_disrupted_support_control_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 10,
        "purpose": (
            "hypothesis_b_full_composition_disrupted_support_control_"
            "no_a6_acceptance"
        ),
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
        "blocked_full_composition_record": blocked_record,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "11_full_composition_explicit_restoration_replay",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    record = output["blocked_full_composition_record"]
    support = record["support_evidence"]
    lines = [
        "# N10 Iteration 10 Full-Composition Disrupted Support Control",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 10 takes the Iteration 9 Hypothesis A closeout as the",
        "positive full-composition source, preserves the route, memory, and",
        "goal-proxy regulation links, and replaces the support lane with the",
        "N07 N09-matched disrupted-support lane.",
        "",
        "The result is intentionally negative: the full composition blocks for a",
        "support-specific reason. This strengthens Hypothesis B because the",
        "support-disruption control now operates at the full A6/ALI6 boundary,",
        "not only at the earlier support/regulation sub-chain.",
        "",
        "```text",
        f"attempted_integration_level = {record['attempted_integration_level']}",
        f"attempted_n10_category_level = {record['attempted_n10_category_level']}",
        f"accepted_integration_level = {record['accepted_integration_level']}",
        f"accepted_n10_category_level = {record['accepted_n10_category_level']}",
        f"integration_allowed = {record['integration_allowed']}",
        f"positive_integration_row_emitted = {record['positive_integration_row_emitted']}",
        f"primary_blocker = {record['primary_blocker']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Preserved Links",
        "",
        "```json",
        json.dumps(record["preserved_source_links"], indent=2, sort_keys=True),
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
        "support_survival_passed = false",
        "restoration_fraction = 0.0",
        "```",
        "",
        "The route/memory/regulation chain did not fail because a source was",
        "missing. It failed because the support baseline was below the declared",
        "survival threshold and no explicit restoration was present.",
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
        "```json",
        json.dumps(output["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "All claim flags remain false. Iteration 10 does not emit agency,",
        "semantic goal ownership, identity acceptance, ACO, biological,",
        "personhood, unrestricted agency, or fully native agentic-like",
        "integration claims.",
        "",
        "## Reproduction",
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
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 10 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

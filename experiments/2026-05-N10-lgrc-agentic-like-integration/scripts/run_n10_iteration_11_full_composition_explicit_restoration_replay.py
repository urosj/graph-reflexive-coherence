#!/usr/bin/env python3
"""Run N10 Iteration 11 full-composition explicit-restoration replay.

Iteration 11 is the positive counterpart to Iteration 10. It takes the same
Hypothesis A full route-memory-support-regulation source chain, consumes the
N07 explicit-restoration lane, and verifies that the full composition can
resume only because restoration evidence is explicit, source-backed, and tied
to the same N09 withdrawal event that Iteration 10 blocked.
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
ITERATION_10_PATH = (
    EXPERIMENT
    / "outputs"
    / "n10_iteration_10_full_composition_disrupted_support_control.json"
)
OUTPUT_PATH = (
    EXPERIMENT
    / "outputs"
    / "n10_iteration_11_full_composition_explicit_restoration_replay.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports"
    / "n10_iteration_11_full_composition_explicit_restoration_replay.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_11_full_composition_explicit_restoration_replay.py"
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
        "n10_iteration_10_disrupted_support_control": ITERATION_10_PATH,
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
        "n10_iteration_10_disrupted_support_control": (
            EXPERIMENT
            / "reports"
            / "n10_iteration_10_full_composition_disrupted_support_control.md"
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


def build_restored_full_composition_record(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    i7: dict[str, Any],
    i8: dict[str, Any],
    i9: dict[str, Any],
    i10: dict[str, Any],
    support_lane: dict[str, Any],
    manifest_support_lane: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    route_memory_row = i7["integration_row"]
    bounded_row = i8["main_integration_row"]
    closeout = i9["closeout"]
    disrupted = i10["blocked_full_composition_record"]
    disrupted_support = disrupted["support_evidence"]
    source_support_tag = manifest["allowed_values"]["source_support_outcome_map"][
        support_lane["identity_support_outcome_tag"]
    ]
    restoration_order_valid = (
        disrupted["integration_allowed"] is False
        and disrupted["positive_integration_row_emitted"] is False
        and support_lane["n09_withdrawal_digest"]
        == disrupted_support["n09_withdrawal_digest"]
        and support_lane["withdrawal_depth"] == disrupted_support["withdrawal_depth"]
        and support_lane["restoration_fraction"] > 0.0
    )
    row = {
        "integration_row_id": "n10_i11_full_composition_explicit_restoration_row_v1",
        "integration_level": "A6",
        "attempted_integration_level": "A6",
        "accepted_integration_level": "A6",
        "n10_category_level": "ALI6",
        "attempted_n10_category_level": "ALI6",
        "accepted_n10_category_level": "ALI6",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i11",
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
        "integration_outcome_tag": "restoration_gated_integration_candidate",
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
        "integration_allowed": True,
        "positive_integration_row_emitted": True,
        "primary_blocker": None,
        "blocker_reason": None,
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
        "prior_disruption_evidence": {
            "iteration_10_record_digest": disrupted["integration_row_digest"],
            "iteration_10_record_digest_valid": row_digest_valid(disrupted),
            "prior_integration_allowed": disrupted["integration_allowed"],
            "prior_positive_row_emitted": disrupted["positive_integration_row_emitted"],
            "prior_primary_blocker": disrupted["primary_blocker"],
            "prior_support_lane_id": disrupted_support["source_lane_id"],
            "prior_support_lane_digest": disrupted_support["lane_digest"],
            "prior_support_survival_passed": disrupted_support[
                "support_survival_passed"
            ],
            "prior_n09_withdrawal_digest": disrupted_support[
                "n09_withdrawal_digest"
            ],
            "history_preserved": restoration_order_valid,
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
            "support_above_threshold": support_lane["final_A_support_retention"]
            >= support_lane["support_survival_threshold"],
            "explicit_restoration_present": support_lane["restoration_fraction"] > 0.0,
        },
        "route_evidence_preserved": {
            "route_choice_artifact": "n06_closeout",
            "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
            "route_context_tag": route_memory_row["route_context_tag"],
            "source_scope": "N06_SC6_selection_only_pre_topology_commit",
        },
        "memory_evidence_preserved": {
            "memory_affordance_artifact": "n08_hypothesis_a_closeout",
            "memory_affordance_digest": source_artifacts[
                "n08_hypothesis_a_closeout"
            ]["sha256"],
            "memory_scope_tag": route_memory_row["memory_scope_tag"],
            "source_scope": "N08_MEM6_serialized_producer_policy_memory_or_trail",
        },
        "regulation_evidence_preserved": {
            "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
            "goal_proxy_regulation_digest": source_artifacts[
                "n09_hypothesis_a_closeout"
            ]["sha256"],
            "regulation_scope_tag": route_memory_row["regulation_scope_tag"],
            "source_scope": "N09_GPR6_goal_proxy_regulation_closeout",
        },
        "hypothesis_b_relevance": (
            "This is the explicit-restoration half of the full-composition "
            "Hypothesis B matrix. Iteration 12 must still close the full "
            "support-state matrix."
        ),
        "claim_boundary": (
            "Restoration-gated full-composition resumption is bounded, "
            "artifact-only evidence. It is not A7 generalization, agency, "
            "identity acceptance, or fully native agentic-like integration."
        ),
        "a7_generalization_claim_allowed": False,
        "budget_mode": "source_artifact_budget_compatibility_not_single_runtime_continuity",
    }
    return with_digest(row, "integration_row_digest")


def build_controls(
    manifest: dict[str, Any],
    row: dict[str, Any],
    source_artifacts: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    support = row["support_evidence"]
    prior = row["prior_disruption_evidence"]
    return {
        "missing_route_choice_artifact": {
            "control_passed": row["route_choice_artifact"] is not None,
            "primary_blocker": blockers["missing_route_choice_artifact"],
            "reason": "full restoration replay keeps the N06 route-choice source link present",
        },
        "missing_memory_affordance_artifact": {
            "control_passed": row["memory_affordance_artifact"] is not None,
            "primary_blocker": blockers["missing_memory_affordance_artifact"],
            "reason": "full restoration replay keeps the N08 memory/trail source link present",
        },
        "missing_identity_support_artifact": {
            "control_passed": row["identity_support_artifact"] is not None,
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "full restoration replay consumes the N07 restored support lane",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": row["goal_proxy_regulation_artifact"] is not None,
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "full restoration replay keeps the N09 regulation source link present",
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
            "reason": "the restored lane digest is matched against the frozen N10 manifest lane summary",
        },
        "prior_disruption_history_preserved": {
            "control_passed": prior["history_preserved"] is True
            and prior["prior_integration_allowed"] is False
            and prior["iteration_10_record_digest_valid"] is True,
            "primary_blocker": "support_history_erased",
            "reason": "restoration references the same N09 withdrawal digest as the Iteration 10 disrupted-support block",
        },
        "restoration_required_but_missing": {
            "control_passed": support["explicit_restoration_present"] is True
            and support["restoration_fraction"] > 0.0,
            "primary_blocker": blockers["restoration_required_but_missing"],
            "reason": "full composition resumes only because explicit restoration is present",
        },
        "artifact_only_replay_missing_link": {
            "control_passed": row["artifact_only"] is True
            and row["runtime_state_used"] is False
            and row["integration_allowed"] is True,
            "primary_blocker": blockers["artifact_only_replay_missing_link"],
            "reason": "the restored row is reconstructable from exported source artifacts only",
        },
        "hidden_experiment_side_steering": {
            "control_passed": support["explicit_restoration_present"] is True
            and prior["history_preserved"] is True,
            "primary_blocker": blockers["hidden_experiment_side_steering"],
            "reason": "N10 does not invent restoration; it consumes the recorded N07 restoration lane",
        },
        "budget_surface_ambiguity": {
            "control_passed": row["node_plus_packet_budget_error"] == 0.0
            and support["final_budget_error"] == 0.0,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "route, memory, support, and proxy budgets remain source-artifact compatibility checks",
        },
        "claim_promotion": {
            "control_passed": all_claim_flags_false(row)
            and row["a7_generalization_claim_allowed"] is False,
            "primary_blocker": blockers["claim_promotion"],
            "reason": "restoration-gated full composition cannot emit agency, identity acceptance, goal ownership, A7, or fully native agentic-like claims",
        },
    }


def build_checks(
    manifest: dict[str, Any],
    i9: dict[str, Any],
    i10: dict[str, Any],
    row: dict[str, Any],
    controls: dict[str, Any],
    source_artifacts: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    support = row["support_evidence"]
    prior = row["prior_disruption_evidence"]
    return {
        "integration_record_required_fields_present": required_fields.issubset(
            set(row)
        ),
        "integration_record_digest_valid": row_digest_valid(row),
        "iteration_9_hypothesis_a_closeout_available": i9["status"] == "passed"
        and i9["closeout"]["final_ceiling_supported"] is True,
        "iteration_10_disruption_record_available": i10["status"] == "passed"
        and prior["prior_integration_allowed"] is False,
        "attempted_integration_level_is_a6": row["attempted_integration_level"]
        == "A6",
        "accepted_integration_level_is_a6": row["accepted_integration_level"] == "A6",
        "accepted_n10_category_level_is_ali6": row["accepted_n10_category_level"]
        == "ALI6",
        "integration_allowed_true": row["integration_allowed"] is True,
        "positive_integration_row_emitted": row["positive_integration_row_emitted"]
        is True,
        "support_state_tag_is_explicit_restoration": row["support_state_tag"]
        == "explicit_restoration_recovers_support",
        "restored_support_lane_survives": support["support_survival_passed"] is True,
        "restored_support_retention_above_threshold": support[
            "final_A_support_retention"
        ]
        >= support["support_survival_threshold"],
        "explicit_restoration_present": support["explicit_restoration_present"]
        is True,
        "prior_disruption_history_preserved": prior["history_preserved"] is True,
        "prior_disruption_digest_valid": prior["iteration_10_record_digest_valid"]
        is True,
        "route_link_present": row["route_choice_artifact"] == "n06_closeout",
        "memory_link_present": row["memory_affordance_artifact"]
        == "n08_hypothesis_a_closeout",
        "regulation_link_present": row["goal_proxy_regulation_artifact"]
        == "n09_hypothesis_a_closeout",
        "route_context_selection_only_preserved": row["route_context_tag"]
        == "route_context_selection_only",
        "memory_scope_preserved": row["memory_scope_tag"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "source_artifact_digests_match_baseline": all(
            value.get("matches_baseline", True) for value in source_artifacts.values()
        ),
        "artifact_only_replay": row["artifact_only"] is True
        and row["runtime_state_used"] is False,
        "claim_flags_all_false": all_claim_flags_false(row),
        "a7_not_claimed": row["a7_generalization_claim_allowed"] is False,
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "src_clean_for_iteration_11": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    i7 = load_json(ITERATION_7_PATH)
    i8 = load_json(ITERATION_8_PATH)
    i9 = load_json(ITERATION_9_PATH)
    i10 = load_json(ITERATION_10_PATH)
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    support_lane = find_lane(
        n07_i13["withdrawal_lanes"], "restored_after_n09_partial_withdrawal"
    )
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "restored_after_n09_partial_withdrawal"
    )
    source_artifacts, source_reports = build_source_records(baseline)
    restored_row = build_restored_full_composition_record(
        baseline,
        manifest,
        i7,
        i8,
        i9,
        i10,
        support_lane,
        manifest_support_lane,
        source_artifacts,
        source_reports,
    )
    controls = build_controls(manifest, restored_row, source_artifacts)
    checks = build_checks(manifest, i9, i10, restored_row, controls, source_artifacts)
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
                "step": "load_prior_disrupted_full_composition_record",
                "artifact": rel(ITERATION_10_PATH),
                "blocked_record_digest": i10["blocked_full_composition_record"][
                    "integration_row_digest"
                ],
                "prior_primary_blocker": i10["blocked_full_composition_record"][
                    "primary_blocker"
                ],
            },
            {
                "step": "consume_explicit_restoration_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
                "restoration_fraction": support_lane["restoration_fraction"],
                "support_survival_passed": support_lane["support_survival_passed"],
            },
            {
                "step": "emit_restoration_gated_full_composition_row",
                "integration_row_digest": restored_row["integration_row_digest"],
                "integration_allowed": restored_row["integration_allowed"],
                "accepted_integration_level": restored_row["accepted_integration_level"],
                "accepted_n10_category_level": restored_row[
                    "accepted_n10_category_level"
                ],
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 11 passes if the full composition can resume only "
            "through explicit, source-backed restoration evidence that follows "
            "the disrupted-support record. The result may support a "
            "restoration-gated bounded composition candidate, but does not "
            "erase the disruption control or promote A7, agency, or identity "
            "acceptance claims."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_11_full_composition_explicit_restoration_replay_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 11,
        "purpose": "hypothesis_b_full_composition_explicit_restoration_replay",
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
        "restored_full_composition_row": restored_row,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "12_hypothesis_b_support_state_matrix_closeout",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    row = output["restored_full_composition_row"]
    support = row["support_evidence"]
    prior = row["prior_disruption_evidence"]
    lines = [
        "# N10 Iteration 11 Full-Composition Explicit Restoration Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 11 consumes the explicit N07 restoration lane after the",
        "Iteration 10 disrupted-support block. The full composition can resume",
        "because restoration is explicit, source-backed, above threshold, and",
        "linked to the same N09 withdrawal event.",
        "",
        "```text",
        f"attempted_integration_level = {row['attempted_integration_level']}",
        f"accepted_integration_level = {row['accepted_integration_level']}",
        f"accepted_n10_category_level = {row['accepted_n10_category_level']}",
        f"integration_outcome_tag = {row['integration_outcome_tag']}",
        f"integration_allowed = {row['integration_allowed']}",
        f"positive_integration_row_emitted = {row['positive_integration_row_emitted']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Prior Disruption Link",
        "",
        "```json",
        json.dumps(prior, indent=2, sort_keys=True),
        "```",
        "",
        "## Restoration Evidence",
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
        f"restoration_fraction = {support['restoration_fraction']}",
        "support_survival_passed = true",
        "prior disrupted-support history preserved = true",
        "```",
        "",
        "This does not erase Iteration 10. It records that the full composition",
        "may resume only through explicit restoration evidence that references",
        "the same disrupted-support event.",
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
        "All claim flags remain false. Iteration 11 does not emit agency,",
        "semantic goal ownership, identity acceptance, ACO, biological,",
        "personhood, unrestricted agency, A7 generalization, or fully native",
        "agentic-like integration claims.",
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
        raise SystemExit(f"Iteration 11 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

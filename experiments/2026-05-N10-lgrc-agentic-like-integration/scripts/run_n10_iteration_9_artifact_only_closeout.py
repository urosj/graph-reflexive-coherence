#!/usr/bin/env python3
"""Run N10 Iteration 9 artifact-only replay and closeout.

Iteration 9 validates the full N10 route-memory-support-regulation chain from
exported artifacts only. If every positive row and negative control remains
valid, the conservative N10 ceiling becomes
bounded_artifact_only_agentic_like_integration_candidate / ALI6. This is still
not an agency, intention, identity-acceptance, ACO, or personhood claim.
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
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_9_artifact_only_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_9_artifact_only_closeout.py"
)

ITERATION_PATHS = {
    "n10_iteration_1_baseline_inventory": (
        EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
    ),
    "n10_iteration_2_fixture_manifest_validation": (
        EXPERIMENT / "outputs" / "n10_iteration_2_fixture_manifest_validation.json"
    ),
    "n10_iteration_3_support_aware_regulation_replay": (
        EXPERIMENT / "outputs" / "n10_iteration_3_support_aware_regulation_replay.json"
    ),
    "n10_iteration_4_mild_withdrawal_survival_replay": (
        EXPERIMENT / "outputs" / "n10_iteration_4_mild_withdrawal_survival_replay.json"
    ),
    "n10_iteration_5_disrupted_support_control": (
        EXPERIMENT / "outputs" / "n10_iteration_5_disrupted_support_control.json"
    ),
    "n10_iteration_6_explicit_restoration_replay": (
        EXPERIMENT / "outputs" / "n10_iteration_6_explicit_restoration_replay.json"
    ),
    "n10_iteration_7_route_memory_regulation_composition": (
        EXPERIMENT / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
    ),
    "n10_iteration_8_bounded_repeated_integration": (
        EXPERIMENT / "outputs" / "n10_iteration_8_bounded_repeated_integration.json"
    ),
}
REPORT_PATHS = {
    "n10_iteration_1_baseline_inventory": (
        EXPERIMENT / "reports" / "n10_iteration_1_baseline_inventory.md"
    ),
    "n10_iteration_2_fixture_manifest_validation": (
        EXPERIMENT / "reports" / "n10_iteration_2_fixture_manifest_validation.md"
    ),
    "n10_iteration_3_support_aware_regulation_replay": (
        EXPERIMENT / "reports" / "n10_iteration_3_support_aware_regulation_replay.md"
    ),
    "n10_iteration_4_mild_withdrawal_survival_replay": (
        EXPERIMENT / "reports" / "n10_iteration_4_mild_withdrawal_survival_replay.md"
    ),
    "n10_iteration_5_disrupted_support_control": (
        EXPERIMENT / "reports" / "n10_iteration_5_disrupted_support_control.md"
    ),
    "n10_iteration_6_explicit_restoration_replay": (
        EXPERIMENT / "reports" / "n10_iteration_6_explicit_restoration_replay.md"
    ),
    "n10_iteration_7_route_memory_regulation_composition": (
        EXPERIMENT / "reports" / "n10_iteration_7_route_memory_regulation_composition.md"
    ),
    "n10_iteration_8_bounded_repeated_integration": (
        EXPERIMENT / "reports" / "n10_iteration_8_bounded_repeated_integration.md"
    ),
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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def controls_passed(artifact: dict[str, Any]) -> bool:
    return all(control["control_passed"] is True for control in artifact["controls"].values())


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


def build_artifact_records() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifacts = {key: load_json(path) for key, path in ITERATION_PATHS.items()}
    artifact_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
            "output_digest": artifacts[key].get("output_digest"),
            "status": artifacts[key].get("status"),
            "output_digest_valid": prior_output_digest_valid(artifacts[key]),
        }
        for key, path in ITERATION_PATHS.items()
    }
    report_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in REPORT_PATHS.items()
        if path.exists()
    }
    return artifacts, artifact_records, report_records


def build_positive_replay_records(artifacts: dict[str, Any]) -> list[dict[str, Any]]:
    i3 = artifacts["n10_iteration_3_support_aware_regulation_replay"]
    i4 = artifacts["n10_iteration_4_mild_withdrawal_survival_replay"]
    i6 = artifacts["n10_iteration_6_explicit_restoration_replay"]
    i7 = artifacts["n10_iteration_7_route_memory_regulation_composition"]
    i8 = artifacts["n10_iteration_8_bounded_repeated_integration"]
    rows = [
        {
            "step": "support_intact_regulation_replay",
            "source_iteration": 3,
            "artifact_key": "n10_iteration_3_support_aware_regulation_replay",
            "row_digest": i3["integration_row"]["integration_row_digest"],
            "n10_category_level": i3["integration_row"]["n10_category_level"],
            "integration_level": i3["integration_row"]["integration_level"],
            "support_state_tag": i3["integration_row"]["support_state_tag"],
            "artifact_only": i3["integration_row"]["artifact_only"],
            "runtime_state_used": i3["integration_row"]["runtime_state_used"],
            "claim_flags_false": all_claim_flags_false(i3["integration_row"]),
            "row_digest_valid": row_digest_valid(i3["integration_row"]),
            "checks_passed": all(i3["checks"].values()),
            "controls_passed": controls_passed(i3),
        },
        {
            "step": "mild_withdrawal_support_survival_replay",
            "source_iteration": 4,
            "artifact_key": "n10_iteration_4_mild_withdrawal_survival_replay",
            "row_digest": i4["integration_row"]["integration_row_digest"],
            "n10_category_level": i4["integration_row"]["n10_category_level"],
            "integration_level": i4["integration_row"]["integration_level"],
            "support_state_tag": i4["integration_row"]["support_state_tag"],
            "artifact_only": i4["integration_row"]["artifact_only"],
            "runtime_state_used": i4["integration_row"]["runtime_state_used"],
            "claim_flags_false": all_claim_flags_false(i4["integration_row"]),
            "row_digest_valid": row_digest_valid(i4["integration_row"]),
            "checks_passed": all(i4["checks"].values()),
            "controls_passed": controls_passed(i4),
        },
        {
            "step": "explicit_restoration_resumes_support_sensitive_replay",
            "source_iteration": 6,
            "artifact_key": "n10_iteration_6_explicit_restoration_replay",
            "row_digest": i6["integration_row"]["integration_row_digest"],
            "n10_category_level": i6["integration_row"]["n10_category_level"],
            "integration_level": i6["integration_row"]["integration_level"],
            "support_state_tag": i6["integration_row"]["support_state_tag"],
            "artifact_only": i6["integration_row"]["artifact_only"],
            "runtime_state_used": i6["integration_row"]["runtime_state_used"],
            "claim_flags_false": all_claim_flags_false(i6["integration_row"]),
            "row_digest_valid": row_digest_valid(i6["integration_row"]),
            "integration_allowed": i6["integration_row"]["integration_allowed"],
            "checks_passed": all(i6["checks"].values()),
            "controls_passed": controls_passed(i6),
        },
        {
            "step": "route_memory_regulation_composition",
            "source_iteration": 7,
            "artifact_key": "n10_iteration_7_route_memory_regulation_composition",
            "row_digest": i7["integration_row"]["integration_row_digest"],
            "n10_category_level": i7["integration_row"]["n10_category_level"],
            "integration_level": i7["integration_row"]["integration_level"],
            "support_state_tag": i7["integration_row"]["support_state_tag"],
            "route_context_tag": i7["integration_row"]["route_context_tag"],
            "memory_scope_tag": i7["integration_row"]["memory_scope_tag"],
            "artifact_only": i7["integration_row"]["artifact_only"],
            "runtime_state_used": i7["integration_row"]["runtime_state_used"],
            "claim_flags_false": all_claim_flags_false(i7["integration_row"]),
            "row_digest_valid": row_digest_valid(i7["integration_row"]),
            "integration_allowed": i7["integration_row"]["integration_allowed"],
            "checks_passed": all(i7["checks"].values()),
            "controls_passed": controls_passed(i7),
        },
        {
            "step": "bounded_repeated_integration_main",
            "source_iteration": 8,
            "artifact_key": "n10_iteration_8_bounded_repeated_integration",
            "row_digest": i8["main_integration_row"]["integration_row_digest"],
            "n10_category_level": i8["main_integration_row"]["n10_category_level"],
            "integration_level": i8["main_integration_row"]["integration_level"],
            "support_state_tag": i8["main_integration_row"]["support_state_tag"],
            "route_context_tag": i8["main_integration_row"]["route_context_tag"],
            "memory_scope_tag": i8["main_integration_row"]["memory_scope_tag"],
            "window_count": i8["main_integration_row"]["bounded_window"]["window_count"],
            "artifact_only": i8["main_integration_row"]["artifact_only"],
            "runtime_state_used": i8["main_integration_row"]["runtime_state_used"],
            "claim_flags_false": all_claim_flags_false(i8["main_integration_row"]),
            "row_digest_valid": row_digest_valid(i8["main_integration_row"]),
            "integration_allowed": i8["main_integration_row"]["integration_allowed"],
            "checks_passed": all(i8["checks"].values()),
            "controls_passed": controls_passed(i8),
        },
        {
            "step": "bounded_repeated_integration_mild_withdrawal_companion",
            "source_iteration": 8,
            "artifact_key": "n10_iteration_8_bounded_repeated_integration",
            "row_digest": i8["mild_withdrawal_companion_row"][
                "integration_row_digest"
            ],
            "n10_category_level": i8["mild_withdrawal_companion_row"][
                "n10_category_level"
            ],
            "integration_level": i8["mild_withdrawal_companion_row"][
                "integration_level"
            ],
            "support_state_tag": i8["mild_withdrawal_companion_row"][
                "support_state_tag"
            ],
            "route_context_tag": i8["mild_withdrawal_companion_row"][
                "route_context_tag"
            ],
            "memory_scope_tag": i8["mild_withdrawal_companion_row"][
                "memory_scope_tag"
            ],
            "window_count": i8["mild_withdrawal_companion_row"]["bounded_window"][
                "window_count"
            ],
            "artifact_only": i8["mild_withdrawal_companion_row"]["artifact_only"],
            "runtime_state_used": i8["mild_withdrawal_companion_row"][
                "runtime_state_used"
            ],
            "claim_flags_false": all_claim_flags_false(
                i8["mild_withdrawal_companion_row"]
            ),
            "row_digest_valid": row_digest_valid(
                i8["mild_withdrawal_companion_row"]
            ),
            "integration_allowed": i8["mild_withdrawal_companion_row"][
                "integration_allowed"
            ],
            "checks_passed": all(i8["checks"].values()),
            "controls_passed": controls_passed(i8),
        },
    ]
    return [with_digest(row, "replay_step_digest") for row in rows]


def build_negative_control_records(artifacts: dict[str, Any]) -> dict[str, Any]:
    i5 = artifacts["n10_iteration_5_disrupted_support_control"]
    i6 = artifacts["n10_iteration_6_explicit_restoration_replay"]
    i7 = artifacts["n10_iteration_7_route_memory_regulation_composition"]
    i8 = artifacts["n10_iteration_8_bounded_repeated_integration"]
    disrupted = i5["blocked_integration_record"]
    restoration = i6["integration_row"]
    return {
        "support_disruption_blocks": {
            "control_passed": disrupted["integration_allowed"] is False
            and disrupted["positive_integration_row_emitted"] is False
            and disrupted["primary_blocker"] == "support_disrupted_but_integration_allowed"
            and disrupted["support_evidence"]["support_survival_passed"] is False
            and row_digest_valid(disrupted),
            "primary_blocker": "support_disrupted_but_integration_allowed",
            "source_iteration": 5,
            "blocked_record_digest": disrupted["integration_row_digest"],
        },
        "explicit_restoration_resumes_without_erasing_disruption": {
            "control_passed": restoration["integration_allowed"] is True
            and restoration["positive_integration_row_emitted"] is True
            and restoration["prior_disruption_evidence"]["integration_allowed"] is False
            and restoration["prior_disruption_evidence"]["blocked_record_digest"]
            == disrupted["integration_row_digest"]
            and restoration["support_evidence"]["explicit_restoration_present"] is True,
            "primary_blocker": None,
            "source_iterations": [5, 6],
        },
        "stale_source_controls": {
            "control_passed": i7["controls"]["stale_route_context"]["control_passed"]
            and i7["controls"]["stale_memory_surface"]["control_passed"]
            and i7["controls"]["stale_identity_support_baseline"]["control_passed"]
            and i8["controls"]["stale_route_context"]["control_passed"]
            and i8["controls"]["stale_memory_surface"]["control_passed"]
            and i8["controls"]["stale_identity_support_baseline"]["control_passed"]
            and i8["controls"]["stale_regulation_window"]["control_passed"],
            "primary_blocker": "stale_source_control_failed",
            "source_iterations": [7, 8],
        },
        "hidden_steering_controls": {
            "control_passed": i7["controls"]["hidden_experiment_side_steering"][
                "control_passed"
            ]
            and i8["controls"]["hidden_experiment_side_steering"]["control_passed"],
            "primary_blocker": "hidden_experiment_side_steering",
            "source_iterations": [7, 8],
        },
        "budget_controls": {
            "control_passed": i3_to_i8_budget_controls_pass(artifacts),
            "primary_blocker": "budget_surface_ambiguity",
            "source_iterations": [3, 4, 5, 6, 7, 8],
        },
        "claim_promotion_controls": {
            "control_passed": all(
                artifacts[key]["controls"]["claim_promotion"]["control_passed"]
                for key in [
                    "n10_iteration_3_support_aware_regulation_replay",
                    "n10_iteration_4_mild_withdrawal_survival_replay",
                    "n10_iteration_5_disrupted_support_control",
                    "n10_iteration_6_explicit_restoration_replay",
                    "n10_iteration_7_route_memory_regulation_composition",
                    "n10_iteration_8_bounded_repeated_integration",
                ]
            ),
            "primary_blocker": "claim_promotion_blocked",
            "source_iterations": [3, 4, 5, 6, 7, 8],
        },
    }


def i3_to_i8_budget_controls_pass(artifacts: dict[str, Any]) -> bool:
    for key in [
        "n10_iteration_3_support_aware_regulation_replay",
        "n10_iteration_4_mild_withdrawal_survival_replay",
        "n10_iteration_5_disrupted_support_control",
        "n10_iteration_6_explicit_restoration_replay",
        "n10_iteration_7_route_memory_regulation_composition",
        "n10_iteration_8_bounded_repeated_integration",
    ]:
        if not artifacts[key]["controls"]["budget_surface_ambiguity"]["control_passed"]:
            return False
    i8 = artifacts["n10_iteration_8_bounded_repeated_integration"]
    return (
        i8["main_integration_row"]["bounded_window"]["all_cycle_budgets_exact"]
        and i8["mild_withdrawal_companion_row"]["bounded_window"][
            "all_cycle_budgets_exact"
        ]
        and i8["main_integration_row"]["node_plus_packet_budget_error"] == 0.0
        and i8["mild_withdrawal_companion_row"][
            "node_plus_packet_budget_error"
        ]
        == 0.0
    )


def build_closeout_record(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    artifacts: dict[str, Any],
    positive_replay_records: list[dict[str, Any]],
    negative_controls: dict[str, Any],
) -> dict[str, Any]:
    i8 = artifacts["n10_iteration_8_bounded_repeated_integration"]
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    all_replay_steps_pass = all(
        row["artifact_only"]
        and not row["runtime_state_used"]
        and row["claim_flags_false"]
        and row["row_digest_valid"]
        and row["checks_passed"]
        and row["controls_passed"]
        for row in positive_replay_records
    )
    all_controls_pass = all(
        control["control_passed"] is True for control in negative_controls.values()
    )
    final_ceiling_supported = (
        all_replay_steps_pass
        and all_controls_pass
        and i8["main_integration_row"]["n10_category_level"] == "ALI5"
        and i8["main_integration_row"]["bounded_window"]["all_cycle_rows_source_current"]
        and i8["main_integration_row"]["bounded_window"]["all_cycle_budgets_exact"]
        and i8["main_integration_row"]["bounded_window"]["all_cycle_claim_flags_false"]
    )
    row = {
        "closeout_row_id": "n10_i9_artifact_only_closeout_row_v1",
        "integration_level": "A6" if final_ceiling_supported else "A5",
        "n10_category_level": "ALI6" if final_ceiling_supported else "ALI5",
        "final_n10_ceiling": "bounded_artifact_only_agentic_like_integration_candidate"
        if final_ceiling_supported
        else "blocked_bounded_agentic_like_integration_candidate",
        "final_ceiling_supported": final_ceiling_supported,
        "primary_blocker": None if final_ceiling_supported else "n10_closeout_validation_failed",
        "artifact_only": True,
        "runtime_state_used": False,
        "source_scope": "bounded_artifact_only_source_backed_replay",
        "support_scope": "support_intact_main_lane_with_mild_withdrawal_companion",
        "route_context_scope": "N06_SC6_selection_only_pre_topology_commit",
        "memory_scope": "N08_MEM6_serialized_producer_policy_memory_or_trail",
        "regulation_scope": "N09_GPR5_repeated_window_and_GPR6_closeout",
        "bounded_window_count": i8["main_integration_row"]["bounded_window"][
            "window_count"
        ],
        "bounded_window_digest": i8["main_integration_row"]["bounded_window"][
            "window_digest"
        ],
        "companion_window_digest": i8["mild_withdrawal_companion_row"][
            "bounded_window"
        ]["window_digest"],
        "main_ali5_row_digest": i8["main_integration_row"][
            "integration_row_digest"
        ],
        "companion_ali5_row_digest": i8["mild_withdrawal_companion_row"][
            "integration_row_digest"
        ],
        "positive_replay_step_digests": [
            row["replay_step_digest"] for row in positive_replay_records
        ],
        "negative_control_names": sorted(negative_controls),
        "claim_flags": claim_flags,
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "native_policy_gaps_preserved": baseline["native_policy_gaps"],
        "interpretation": {
            "summary": (
                "N10 is significant because it shows that the N06-N09 "
                "mechanisms compose into a bounded, replayable integration "
                "chain: route choice, memory-shaped affordance, identity/"
                "support survival, and goal-proxy regulation."
            ),
            "why_it_matters": [
                "the chain survives repeated cycles",
                "source links remain clean and digest-backed",
                "budget checks remain exact under the declared surfaces",
                "stale-source and hidden-steering controls fail closed",
                "claim flags remain false",
                "the mild-withdrawal companion shows the result is not limited to the perfectly intact support baseline",
            ],
            "claim_boundary": (
                "The result is impressive as bounded artifact-only "
                "agentic-like integration evidence, not because it proves "
                "agency. Agency, intention, goal ownership, identity "
                "acceptance, ACO behavior, biology, personhood, and "
                "unrestricted agency remain blocked."
            ),
        },
        "non_claims": [
            "agency",
            "intention",
            "semantic_goal_ownership",
            "semantic_goal_understanding",
            "identity_acceptance",
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "ant_colony_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "personhood",
            "unrestricted_agency",
        ],
        "n11_handoff": {
            "ready": final_ceiling_supported,
            "next_question": (
                "Does bounded agentic-like integration generalize across "
                "changing contexts, support states, and proxy conditions "
                "without hidden steering or claim leakage?"
            ),
            "carry_forward_boundaries": [
                "N10 is artifact-only and source-backed, not native agency",
                "N06 route context remains selection-only",
                "N08 memory/trail is serialized producer-policy evidence",
                "N09 regulation remains goal-proxy regulation, not goal ownership",
                "N07 support evidence is support/invariance evidence, not identity acceptance",
            ],
        },
    }
    return with_digest(row, "closeout_row_digest")


def build_checks(
    artifacts: dict[str, Any],
    artifact_records: dict[str, Any],
    positive_replay_records: list[dict[str, Any]],
    negative_controls: dict[str, Any],
    closeout: dict[str, Any],
) -> dict[str, bool]:
    return {
        "all_required_artifacts_present": set(ITERATION_PATHS).issubset(
            artifact_records
        ),
        "all_required_artifacts_status_passed": all(
            artifact_records[key]["status"] == "passed"
            for key in ITERATION_PATHS
            if key != "n10_iteration_1_baseline_inventory"
        ),
        "prior_output_digests_valid": all(
            record["output_digest_valid"] for record in artifact_records.values()
        ),
        "positive_replay_records_all_pass": all(
            row["checks_passed"] and row["controls_passed"]
            for row in positive_replay_records
        ),
        "positive_replay_records_artifact_only": all(
            row["artifact_only"] and not row["runtime_state_used"]
            for row in positive_replay_records
        ),
        "positive_replay_record_digests_valid": all(
            row["row_digest_valid"] for row in positive_replay_records
        ),
        "support_disruption_control_passed": negative_controls[
            "support_disruption_blocks"
        ]["control_passed"],
        "explicit_restoration_control_passed": negative_controls[
            "explicit_restoration_resumes_without_erasing_disruption"
        ]["control_passed"],
        "stale_source_controls_passed": negative_controls["stale_source_controls"][
            "control_passed"
        ],
        "hidden_steering_controls_passed": negative_controls[
            "hidden_steering_controls"
        ]["control_passed"],
        "budget_controls_passed": negative_controls["budget_controls"][
            "control_passed"
        ],
        "claim_promotion_controls_passed": negative_controls[
            "claim_promotion_controls"
        ]["control_passed"],
        "iteration_8_main_is_ali5": artifacts[
            "n10_iteration_8_bounded_repeated_integration"
        ]["main_integration_row"]["n10_category_level"]
        == "ALI5",
        "iteration_8_mild_companion_is_ali5": artifacts[
            "n10_iteration_8_bounded_repeated_integration"
        ]["mild_withdrawal_companion_row"]["n10_category_level"]
        == "ALI5",
        "closeout_ceiling_is_ali6": closeout["n10_category_level"] == "ALI6"
        and closeout["integration_level"] == "A6",
        "closeout_row_digest_valid": closeout["closeout_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in closeout.items()
                if key != "closeout_row_digest"
            }
        ),
        "closeout_claim_flags_all_false": all_claim_flags_false(closeout),
        "runtime_state_not_used": closeout["runtime_state_used"] is False,
        "src_clean_for_iteration_9": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    artifacts, artifact_records, report_records = build_artifact_records()
    baseline = artifacts["n10_iteration_1_baseline_inventory"]
    manifest = load_json(EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json")
    artifact_records["n10_fixture_manifest"] = {
        "path": "experiments/2026-05-N10-lgrc-agentic-like-integration/configs/n10_integration_fixture_manifest_v1.json",
        "sha256": digest_file(
            EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json"
        ),
        "output_digest": None,
        "status": "passed",
        "output_digest_valid": True,
    }
    positive_replay_records = build_positive_replay_records(artifacts)
    negative_controls = build_negative_control_records(artifacts)
    closeout = build_closeout_record(
        baseline, manifest, artifacts, positive_replay_records, negative_controls
    )
    checks = build_checks(
        artifacts, artifact_records, positive_replay_records, negative_controls, closeout
    )
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_baseline_and_manifest",
                "baseline_artifact": artifact_records[
                    "n10_iteration_1_baseline_inventory"
                ]["path"],
                "manifest_artifact": artifact_records["n10_fixture_manifest"]["path"],
            },
            {
                "step": "validate_support_regulation_base_rows",
                "source_iterations": [3, 4, 5, 6],
                "support_disruption_blocked": negative_controls[
                    "support_disruption_blocks"
                ]["control_passed"],
                "explicit_restoration_resumed": negative_controls[
                    "explicit_restoration_resumes_without_erasing_disruption"
                ]["control_passed"],
            },
            {
                "step": "validate_route_memory_regulation_composition",
                "source_iteration": 7,
                "replay_step_digest": positive_replay_records[3][
                    "replay_step_digest"
                ],
            },
            {
                "step": "validate_bounded_repeated_integration_window",
                "source_iteration": 8,
                "main_row_digest": closeout["main_ali5_row_digest"],
                "companion_row_digest": closeout["companion_ali5_row_digest"],
                "bounded_window_count": closeout["bounded_window_count"],
            },
            {
                "step": "emit_n10_closeout_row",
                "closeout_row_digest": closeout["closeout_row_digest"],
                "final_n10_ceiling": closeout["final_n10_ceiling"],
                "n10_category_level": closeout["n10_category_level"],
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 9 passes if an artifact-only closeout validator "
            "reconstructs the bounded N10 route-memory-support-regulation "
            "integration chain and all controls without private runtime state. "
            "The closeout must either set the conservative ceiling to "
            "`bounded_artifact_only_agentic_like_integration_candidate` or "
            "record the exact blocker that prevents it."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_9_artifact_only_closeout_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 9,
        "purpose": "artifact_only_replay_and_closeout",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "artifact_records": artifact_records,
        "report_records": report_records,
        "positive_replay_records": positive_replay_records,
        "negative_controls": negative_controls,
        "closeout": closeout,
        "artifact_only_replay": artifact_only_replay,
        "checks": checks,
        "acceptance": acceptance,
        "next_experiment": "N11_broader_general_agentic_like_integration",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    closeout = output["closeout"]
    lines = [
        "# N10 Iteration 9 Artifact-Only Replay And Closeout",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 9 reconstructed the N10 integration chain from exported",
        "artifacts only. The closeout validates the support/regulation base,",
        "the disrupted-support negative control, explicit restoration, the",
        "route-memory-regulation composition, and the bounded repeated",
        "integration window.",
        "",
        "```text",
        f"final_n10_ceiling = {closeout['final_n10_ceiling']}",
        f"integration_level = {closeout['integration_level']}",
        f"n10_category_level = {closeout['n10_category_level']}",
        f"bounded_window_count = {closeout['bounded_window_count']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Boundary",
        "",
        "This closeout is an artifact-only bounded integration candidate. It is",
        "not a claim of agency, intention, semantic goal ownership, identity",
        "acceptance, ACO behavior, biological behavior, personhood, or",
        "unrestricted agency.",
        "",
        "```json",
        json.dumps(
            {
                "route_context_scope": closeout["route_context_scope"],
                "memory_scope": closeout["memory_scope"],
                "regulation_scope": closeout["regulation_scope"],
                "support_scope": closeout["support_scope"],
                "native_policy_gaps_preserved": closeout[
                    "native_policy_gaps_preserved"
                ],
                "claim_flags": closeout["claim_flags"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Interpretation",
        "",
        "What makes the N10 closeout significant is not that it proves agency;",
        "it explicitly does not. It shows that the N06-N09 pieces can be",
        "composed into a bounded, replayable integration chain:",
        "",
        "```text",
        "route choice",
        "-> memory-shaped affordance",
        "-> identity/support survival",
        "-> goal-proxy regulation",
        "```",
        "",
        "The composition survives repeated cycles with clean source links, exact",
        "budget checks, stale-source controls, hidden-steering controls, and no",
        "claim leakage. The mild-withdrawal companion is especially useful",
        "because it shows the integration is not only valid in the perfectly",
        "intact support baseline.",
        "",
        "## Positive Replay Records",
        "",
        "```json",
        json.dumps(output["positive_replay_records"], indent=2, sort_keys=True),
        "```",
        "",
        "## Negative Controls",
        "",
        "```json",
        json.dumps(output["negative_controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## N11 Handoff",
        "",
        "```json",
        json.dumps(closeout["n11_handoff"], indent=2, sort_keys=True),
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
        raise SystemExit(f"Iteration 9 closeout failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

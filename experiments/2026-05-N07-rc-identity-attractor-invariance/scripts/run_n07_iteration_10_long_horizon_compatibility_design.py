"""Run N07 Iteration 10 long-horizon compatibility design.

Iteration 10 is contract/design only. It consumes the 9-C closeout and freezes
the long-horizon survivability criteria and recovery/re-separation hypotheses
needed before any new compatibility probe can strengthen N07.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"

SOURCE_9B_OUTPUT = OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json"
SOURCE_9B2_OUTPUT = OUTPUTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.json"
SOURCE_9C_OUTPUT = OUTPUTS / "n07_iteration_9c_short_window_evidence_closeout.json"
SOURCE_9C_REPORT = REPORTS / "n07_iteration_9c_short_window_evidence_closeout.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_10_long_horizon_compatibility_design.json"
REPORT_PATH = REPORTS / "n07_iteration_10_long_horizon_compatibility_design.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_10_long_horizon_compatibility_design.py"
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _claim_flags(source_9c: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(source_9c["claim_flags"])}


def _source_artifacts(
    source_9b: Mapping[str, Any],
    source_9b2: Mapping[str, Any],
    source_9c: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_9b_c3_compatibility_interference_probe",
            "path": _rel(SOURCE_9B_OUTPUT),
            "sha256": _file_sha256(SOURCE_9B_OUTPUT),
            "object_digest": _digest(source_9b),
            "status": source_9b.get("status"),
        },
        {
            "name": "n07_iteration_9b2_c3_compatibility_prolonged_stress",
            "path": _rel(SOURCE_9B2_OUTPUT),
            "sha256": _file_sha256(SOURCE_9B2_OUTPUT),
            "object_digest": _digest(source_9b2),
            "status": source_9b2.get("status"),
        },
        {
            "name": "n07_iteration_9c_short_window_evidence_closeout",
            "path": _rel(SOURCE_9C_OUTPUT),
            "sha256": _file_sha256(SOURCE_9C_OUTPUT),
            "object_digest": _digest(source_9c),
            "status": source_9c.get("status"),
        },
    ]


def _source_reports() -> list[dict[str, str]]:
    return [
        {
            "name": "n07_iteration_9c_short_window_evidence_closeout_report",
            "path": _rel(SOURCE_9C_REPORT),
            "sha256": _file_sha256(SOURCE_9C_REPORT),
        }
    ]


def _metric(source_9b: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    for row in source_9b["compatibility_metric_rows"]:
        if row["metric_name"] == name:
            return row
    raise KeyError(name)


def _source_boundary(
    source_9b: Mapping[str, Any],
    source_9b2: Mapping[str, Any],
    source_9c: Mapping[str, Any],
) -> dict[str, Any]:
    failure = source_9b2["stress_model"]["first_failure"]
    return {
        "source_closeout_digest": source_9c["artifact_digests"]["closeout_row_digest"],
        "current_ceiling": source_9c["short_window_closeout_row"][
            "derived_id_ceiling"
        ],
        "current_primary_blocker": source_9c["short_window_closeout_row"][
            "primary_blocker"
        ],
        "one_window_metrics": {
            "A_support_retention_near_B": _metric(
                source_9b, "a_support_retention_near_b"
            )["value"],
            "B_support_retention_near_A": _metric(
                source_9b, "b_support_retention_near_a"
            )["value"],
            "wrong_basin_leakage_score": _metric(
                source_9b, "wrong_basin_leakage_score"
            )["value"],
            "destructive_interference_score": _metric(
                source_9b, "destructive_interference_score"
            )["value"],
            "ambiguous_overlap_score": _metric(
                source_9b, "ambiguous_overlap_score"
            )["value"],
        },
        "prolonged_failure": failure,
        "stress_model_id": source_9b2["stress_model"]["stress_model_id"],
        "stress_window_count": source_9b2["stress_model"]["stress_window_count"],
    }


def _survivability_contract(boundary: Mapping[str, Any]) -> dict[str, Any]:
    horizon = int(boundary["stress_window_count"])
    wrong_threshold = 0.1
    return {
        "contract_id": "n07_long_horizon_compatibility_survivability_contract_v1",
        "design_only": True,
        "new_probe_run": False,
        "stress_horizon_windows": horizon,
        "baseline_failure_to_beat": {
            "source": "iteration_9b2",
            "first_failure_window": boundary["prolonged_failure"]["stress_window"],
            "primary_blockers": boundary["prolonged_failure"]["primary_blockers"],
            "cumulative_wrong_basin_leakage_score": boundary["prolonged_failure"][
                "cumulative_wrong_basin_leakage_score"
            ],
        },
        "survivability_criteria": {
            "A_support_retention_min_each_window": 0.85,
            "B_support_retention_min_each_window": 0.85,
            "cumulative_wrong_basin_leakage_max_each_window": wrong_threshold,
            "net_unresolved_wrong_basin_leakage_budget_per_window": wrong_threshold
            / horizon,
            "destructive_interference_score_max_each_window": 0.15,
            "ambiguous_overlap_score_max": 0.2,
            "node_plus_packet_budget_error_max": 0.0,
            "hidden_support_field_count": 0,
            "first_failure_window_must_be_none": True,
        },
        "measurement_requirements": [
            "per_window_A_support_retention",
            "per_window_B_support_retention",
            "per_window_wrong_basin_leakage",
            "cumulative_wrong_basin_leakage",
            "post_recovery_unresolved_wrong_basin_leakage",
            "destructive_interference_score",
            "ambiguous_overlap_score",
            "node_plus_packet_budget_error",
            "support_area_digest_replay_for_A_and_B",
        ],
        "artifact_replay_requirements": [
            "source_support_rows",
            "shared_U_rows",
            "recovery_or_reseparation_records",
            "per_window_metric_records",
            "budget_records",
            "control_rows",
            "long_horizon_closeout_row",
        ],
    }


def _deltas(values: list[float]) -> list[float]:
    return [values[index] - values[index - 1] for index in range(1, len(values))]


def _second_deltas(values: list[float]) -> list[float]:
    return _deltas(_deltas(values))


def _slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return (values[-1] - values[0]) / (len(values) - 1)


def _change_function_contract(
    source_9b2: Mapping[str, Any],
    survivability_contract: Mapping[str, Any],
) -> dict[str, Any]:
    windows = sorted(
        source_9b2["stress_model"]["stress_windows"],
        key=lambda row: row["stress_window"],
    )
    series_fields = {
        "wrong_basin_leakage_level": "cumulative_wrong_basin_leakage_score",
        "A_support_retention_level": "A_cumulative_support_retention",
        "B_support_retention_level": "B_cumulative_support_retention",
        "destructive_interference_level": "cumulative_destructive_interference_score",
        "ambiguous_overlap_level": "ambiguous_overlap_score",
        "budget_error_level": "node_plus_packet_budget_error",
    }
    window_indices = [int(row["stress_window"]) for row in windows]
    metric_series = {
        name: [float(row[source_field]) for row in windows]
        for name, source_field in series_fields.items()
    }
    metric_deltas = {
        f"delta_{name}": _deltas(values) for name, values in metric_series.items()
    }
    metric_second_deltas = {
        f"delta_delta_{name}": _second_deltas(values)
        for name, values in metric_series.items()
    }
    metric_slopes = {
        f"{name}_slope_per_window": _slope(values)
        for name, values in metric_series.items()
    }
    criteria = survivability_contract["survivability_criteria"]
    return {
        "contract_id": "n07_long_horizon_compatibility_change_function_v1",
        "design_only": True,
        "input_domain": "ordered_stress_windows",
        "window_index_field": "stress_window",
        "window_indices": window_indices,
        "source_9b2_baseline_trajectory": {
            "metric_series": metric_series,
            "metric_deltas": metric_deltas,
            "metric_second_deltas": metric_second_deltas,
            "metric_slopes": metric_slopes,
            "trajectory_regime": "unbounded_degrading_without_recovery",
            "interpretation": (
                "The 9-B2 source is not only a failed endpoint. It expresses "
                "monotone leakage accumulation and support-retention decay "
                "under repeated no-recovery pressure."
            ),
        },
        "required_iteration_11_outputs": [
            "per_window_metric_series",
            "per_window_metric_deltas",
            "per_window_metric_second_deltas",
            "metric_slopes_per_window",
            "endpoint_pass_status",
            "first_failure_window",
            "trajectory_regime",
            "trajectory_interpretation",
        ],
        "tracked_metrics": [
            "wrong_basin_leakage_level",
            "A_support_retention_level",
            "B_support_retention_level",
            "destructive_interference_level",
            "ambiguous_overlap_level",
            "budget_error_level",
        ],
        "trend_acceptance_criteria": {
            "wrong_basin_leakage_level_max": criteria[
                "cumulative_wrong_basin_leakage_max_each_window"
            ],
            "wrong_basin_leakage_slope_after_transient_max": 0.0,
            "wrong_basin_positive_delta_streak_max_after_transient": 1,
            "A_support_retention_level_min": criteria[
                "A_support_retention_min_each_window"
            ],
            "B_support_retention_level_min": criteria[
                "B_support_retention_min_each_window"
            ],
            "support_retention_negative_delta_streak_max_after_transient": 1,
            "destructive_interference_level_max": criteria[
                "destructive_interference_score_max_each_window"
            ],
            "destructive_interference_slope_after_transient_max": 0.0,
            "ambiguous_overlap_level_max": criteria["ambiguous_overlap_score_max"],
            "budget_error_level_max": criteria["node_plus_packet_budget_error_max"],
            "budget_error_slope_required": 0.0,
            "endpoint_pass_is_necessary_not_sufficient": True,
        },
        "trajectory_regime_classes": {
            "bounded_improving": (
                "Levels remain inside thresholds and leakage/interference "
                "slopes are negative after transient pressure while support "
                "retention recovers or improves."
            ),
            "bounded_flat": (
                "Levels remain inside thresholds and slopes are near zero; "
                "this is stable compatibility but not growth evidence."
            ),
            "bounded_degrading": (
                "Levels remain inside endpoint thresholds but slopes trend "
                "toward future failure. This blocks stronger identity wording."
            ),
            "unbounded_degrading": (
                "Levels cross thresholds with positive leakage/interference "
                "slope or negative support-retention slope."
            ),
            "oscillatory_recovering": (
                "Metric deltas alternate while amplitude damps and thresholds "
                "remain unbreached after transient pressure."
            ),
            "unstable": (
                "Metric deltas or second deltas show accelerating leakage, "
                "support loss, or budget drift before sustained recovery."
            ),
        },
        "interpretation_boundary": {
            "fixed_horizon_role": "measurement_frame_not_result",
            "endpoint_pass_role": "claim_gate_only",
            "trajectory_regime_role": "evidence_interpretation",
            "endpoint_pass_is_necessary_not_sufficient": True,
            "positive_endpoint_with_bounded_degrading_trend_blocks_id6": True,
        },
        "arc_of_becoming_alignment": [
            {
                "paper": "Classification of Becoming",
                "record": (
                    "Classify what property was expressed before converting "
                    "the run into pass/fail wording."
                ),
            },
            {
                "paper": "Cultivation of Becoming",
                "record": (
                    "Treat each long-horizon probe as a question-answer pair "
                    "that should sharpen the next probe, not as proof by "
                    "endpoint alone."
                ),
            },
            {
                "paper": "Naturalization of Becoming",
                "record": (
                    "Future strengthening must ask whether compatibility "
                    "support is regenerated by the regime itself rather than "
                    "only supplied by the fixture."
                ),
            },
        ],
    }


def _mechanism_hypotheses() -> list[dict[str, Any]]:
    return [
        {
            "mechanism_id": "source_digest_reentry_buffer_v1",
            "role": "primary_candidate",
            "description": (
                "Route leakage through shared U into a serialized neutral "
                "buffer, then re-enter the originating support area using "
                "runtime-visible support_area_digest and declared U ports."
            ),
            "uses_existing_evidence": [
                "iteration_7b_reflexive_reentry_pattern",
                "iteration_9b_A_B_support_rows",
                "iteration_9b_shared_U_ports",
            ],
            "required_records": [
                "leakage_event",
                "neutral_buffer_state",
                "source_digest_reentry_event",
                "post_reentry_support_measurement",
            ],
            "hidden_inputs_allowed": False,
            "claim_boundary": "recovery_mechanism_not_agency_or_identity_acceptance",
        },
        {
            "mechanism_id": "neutral_absorber_reservoir_v1",
            "role": "baseline_recovery_variant",
            "description": (
                "Absorb ambiguous shared-U flux into a neutral reservoir so it "
                "does not immediately become competitor support. Re-separation "
                "must be serialized before any support credit is restored."
            ),
            "uses_existing_evidence": [
                "iteration_9b_shared_U",
                "iteration_9b_wrong_basin_leakage_metric",
            ],
            "required_records": [
                "absorber_capture_event",
                "reservoir_budget_record",
                "reseparation_event",
            ],
            "hidden_inputs_allowed": False,
            "claim_boundary": "neutral_absorption_not_choice_or_preference",
        },
        {
            "mechanism_id": "symmetric_dual_reentry_v1",
            "role": "symmetry_variant",
            "description": (
                "Apply the same digest-visible reentry rule to both A and B. "
                "This variant requires B to remain source-backed across the "
                "long-horizon probe instead of serving only as a context row."
            ),
            "uses_existing_evidence": [
                "iteration_9b_B_source_backed_support_row",
                "iteration_9b_A_source_backed_support_row",
            ],
            "required_records": [
                "A_reentry_event",
                "B_reentry_event",
                "symmetry_metric_record",
            ],
            "hidden_inputs_allowed": False,
            "claim_boundary": "symmetric_reentry_not_semantic_choice",
        },
    ]


def _control_matrix() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "baseline_no_recovery_reproduces_9b2_failure",
            "expected_status": "blocked",
            "primary_blocker": "wrong_basin",
            "purpose": "Prove the long-horizon probe still sees the source failure.",
        },
        {
            "control_id": "source_digest_scrambled",
            "expected_status": "blocked",
            "primary_blocker": "wrong_support_area",
            "purpose": "Reject recovery credited to the wrong basin digest.",
        },
        {
            "control_id": "hidden_recovery_preference",
            "expected_status": "blocked",
            "primary_blocker": "hidden_support_field",
            "purpose": "Reject report-side or fixture-side recovery routing.",
        },
        {
            "control_id": "asymmetric_recovery_preference",
            "expected_status": "blocked",
            "primary_blocker": "ambiguous_overlap",
            "purpose": "Reject unrecorded preference that favors A or B.",
        },
        {
            "control_id": "budget_discontinuity_after_recovery",
            "expected_status": "blocked",
            "primary_blocker": "budget_discontinuity",
            "purpose": "Reject recovery by mass creation or silent normalization.",
        },
        {
            "control_id": "support_drift_after_recovery",
            "expected_status": "blocked",
            "primary_blocker": "support_drift_beyond_threshold",
            "purpose": "Reject recovery that controls leakage but loses support.",
        },
        {
            "control_id": "identity_claim_promotion",
            "expected_status": "blocked",
            "primary_blocker": "identity_claim_promotion",
            "purpose": "Reject ID6 or identity-acceptance wording before replay.",
        },
    ]


def _iteration_11_plan() -> dict[str, Any]:
    return {
        "iteration": "11",
        "name": "long_horizon_compatibility_recovery_probe_series",
        "series_scope": "11_star_long_horizon_c3_classification_learning_series",
        "series_rationale": (
            "A single fixed-horizon probe is not enough to classify long-term "
            "C3 basin compatibility. Iteration 11 may therefore branch into "
            "11-A, 11-B, and later 11-* probes until the trajectory regimes "
            "are understood well enough for artifact-only closeout."
        ),
        "branch_iteration_policy": {
            "branch_ids": "11, 11-A, 11-B, 11-C, ...",
            "each_branch_must_record": [
                "question_answered",
                "mechanism_or_fixture_change",
                "endpoint_pass_status",
                "trajectory_regime",
                "trajectory_interpretation",
                "what_was_learned",
                "next_question",
                "claim_flags_false",
            ],
            "branch_continuation_allowed": True,
            "branch_continuation_rule": (
                "Continue 11-* while trajectory evidence distinguishes new "
                "regimes or exposes new blockers. Stop when branches are "
                "repetitive, blocked by the same unresolved missing mechanism, "
                "or sufficient to define the current long-term C3 class."
            ),
        },
        "iteration_12_entry_gate": {
            "closeout_only_after_11_star_series": True,
            "required_before_closeout": [
                "baseline_no_recovery_trend_replayed",
                "at_least_one_recovery_or_reseparation_branch_evaluated",
                "trajectory_regime_inventory_complete_for_attempted_branches",
                "common_blockers_or_success_conditions_recorded",
                "claim_boundaries_clean",
            ],
            "iteration_12_role": (
                "Artifact-only replay and classification closeout of the "
                "11-* learning series, not a forced close immediately after "
                "one branch."
            ),
        },
        "required_outputs": [
            "endpoint_pass_status",
            "first_failure_window",
            "per_window_metric_series",
            "per_window_metric_deltas",
            "metric_slopes_per_window",
            "trajectory_regime",
            "trajectory_interpretation",
            "control_rows",
        ],
        "lanes": [
            {
                "lane_id": "11-0",
                "name": "baseline_no_recovery_replay",
                "expected": "fail_at_or_before_window_3_with_wrong_basin",
            },
            {
                "lane_id": "11-A",
                "name": "source_digest_reentry_buffer",
                "expected": "attempt_to_bound_wrong_basin_leakage_across_12_windows",
            },
            {
                "lane_id": "11-B",
                "name": "neutral_absorber_reservoir",
                "expected": "test_whether_neutral_U_absorption_prevents_competitor_capture",
            },
            {
                "lane_id": "11-C",
                "name": "symmetric_dual_reentry_optional",
                "expected": "only_valid_if_B_is_source_backed_across_the_probe",
            },
        ],
        "promotion_boundary": (
            "A positive 11-* branch can strengthen long-horizon "
            "compatibility evidence but cannot claim ID6 until Iteration 12 "
            "artifact-only replay closes the 11-* series."
        ),
    }


def _design_row(
    source_9c: Mapping[str, Any],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
    design_contract: Mapping[str, Any],
    change_function_contract: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    closeout = source_9c["short_window_closeout_row"]
    activity_scope = {
        "source_9c_closeout_digest": closeout["closeout_row_digest"],
        "survivability_contract_digest": _digest(design_contract),
        "change_function_contract_digest": _digest(change_function_contract),
        "planned_next_iteration": "11_long_horizon_compatibility_recovery_probe",
    }
    row = {
        "row_id": "n07_i10_long_horizon_compatibility_design_row_v1",
        "id_level": "ID5",
        "topology_family_id": "n07_T7_compatibility",
        "composite_topology_id": "n07_C3_competing_basin_compatibility_candidate",
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": closeout["support_area_id"],
        "support_area_digest": closeout["support_area_digest"],
        "source_artifacts": [row["path"] for row in source_artifacts],
        "source_artifact_sha256": {
            row["path"]: row["sha256"] for row in source_artifacts
        },
        "source_reports": [row["path"] for row in source_reports],
        "runtime_family": "experiment_local",
        "implementation_surface": "experiment_local",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": "blocked",
            "artifact_replay": "pass",
        },
        "derived_id_ceiling": "ID5",
        "primary_blocker": "long_horizon_probe_not_run",
        "native_support_status": "experiment_local",
        "native_observables_used": ["source_support_area_digest"],
        "experiment_local_observables_used": [
            "survivability_contract",
            "change_function_trajectory_contract",
            "wrong_basin_leakage_budget",
            "recovery_reseparation_hypotheses",
        ],
        "native_policy_blockers": [
            "native_long_horizon_compatibility_policy_missing",
            "long_horizon_probe_not_run",
        ],
        "becoming_class_status": "reusable_class",
        "becoming_interpretation_rule": (
            "Endpoint pass/fail gates claims, but trajectory regime classifies "
            "what compatibility behavior was expressed."
        ),
        "trajectory_contract_id": change_function_contract["contract_id"],
        "probe_role": "diagnostic_probe",
        "boundary_rung": "eligible_state",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest_scope": activity_scope,
        "activity_history_digest": _digest(activity_scope),
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "id6_claimed": False,
        "id6_blocker": "long_horizon_probe_not_run",
        "claim_ceiling": "long_horizon_compatibility_design_only_no_promotion",
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["design_row_digest"] = _digest(row)
    return row


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    contract = result["survivability_contract"]
    trajectory = result["change_function_contract"]
    boundary = result["source_boundary"]
    design_row = result["design_row"]
    mechanisms = result["recovery_reseparation_hypotheses"]
    controls = result["control_matrix"]
    claim_flags = result["claim_flags"]
    criteria = contract["survivability_criteria"]
    trend_criteria = trajectory["trend_acceptance_criteria"]
    return {
        "source_9c_passed": result["source_status"]["iteration_9c_status"]
        == "passed",
        "source_boundary_wrong_basin": boundary["current_primary_blocker"]
        == "wrong_basin",
        "source_failure_window_3": boundary["prolonged_failure"]["stress_window"] == 3,
        "design_only_no_probe": contract["design_only"] is True
        and contract["new_probe_run"] is False,
        "stress_horizon_reuses_9b2": contract["stress_horizon_windows"]
        == boundary["stress_window_count"],
        "leakage_budget_tighter_than_source_window": criteria[
            "net_unresolved_wrong_basin_leakage_budget_per_window"
        ]
        < boundary["one_window_metrics"]["wrong_basin_leakage_score"],
        "criteria_include_support_retention": all(
            key in criteria
            for key in [
                "A_support_retention_min_each_window",
                "B_support_retention_min_each_window",
            ]
        ),
        "criteria_include_budget_exactness": criteria[
            "node_plus_packet_budget_error_max"
        ]
        == 0.0,
        "criteria_include_hidden_support_rejection": criteria[
            "hidden_support_field_count"
        ]
        == 0,
        "change_function_contract_declared": trajectory["contract_id"]
        == "n07_long_horizon_compatibility_change_function_v1",
        "trend_metrics_declared": all(
            metric in trajectory["tracked_metrics"]
            for metric in [
                "wrong_basin_leakage_level",
                "A_support_retention_level",
                "B_support_retention_level",
                "destructive_interference_level",
                "budget_error_level",
            ]
        ),
        "trajectory_regime_classes_declared": len(
            trajectory["trajectory_regime_classes"]
        )
        >= 6,
        "endpoint_not_only_interpretation": trajectory["interpretation_boundary"][
            "endpoint_pass_is_necessary_not_sufficient"
        ]
        is True
        and trend_criteria["endpoint_pass_is_necessary_not_sufficient"] is True,
        "source_trend_classified": trajectory["source_9b2_baseline_trajectory"][
            "trajectory_regime"
        ]
        == "unbounded_degrading_without_recovery",
        "arc_of_becoming_alignment_recorded": {
            row["paper"] for row in trajectory["arc_of_becoming_alignment"]
        }
        == {
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        },
        "recovery_mechanisms_declared": len(mechanisms) >= 3,
        "primary_reentry_buffer_declared": mechanisms[0]["mechanism_id"]
        == "source_digest_reentry_buffer_v1",
        "mechanisms_reject_hidden_inputs": all(
            row["hidden_inputs_allowed"] is False for row in mechanisms
        ),
        "baseline_failure_control_present": any(
            row["control_id"] == "baseline_no_recovery_reproduces_9b2_failure"
            for row in controls
        ),
        "control_blockers_distinct": len(
            {row["primary_blocker"] for row in controls}
        )
        == len(controls),
        "iteration_11_lanes_declared": len(result["iteration_11_probe_plan"]["lanes"])
        >= 3,
        "iteration_11_series_policy_declared": result["iteration_11_probe_plan"][
            "branch_iteration_policy"
        ]["branch_continuation_allowed"]
        is True,
        "iteration_12_closeout_deferred_until_11_star": result[
            "iteration_11_probe_plan"
        ]["iteration_12_entry_gate"]["closeout_only_after_11_star_series"]
        is True,
        "iteration_11_requires_trend_outputs": all(
            field in result["iteration_11_probe_plan"]["required_outputs"]
            for field in [
                "per_window_metric_series",
                "per_window_metric_deltas",
                "metric_slopes_per_window",
                "trajectory_regime",
                "trajectory_interpretation",
            ]
        ),
        "design_row_ceiling_id5": design_row["derived_id_ceiling"] == "ID5",
        "design_row_no_id6": design_row["id6_claimed"] is False,
        "claim_flags_false": not any(claim_flags.values()),
        "design_row_claim_flags_false": not any(design_row["claim_flags"].values()),
        "next_iteration_is_11_probe": result["next_iteration"]
        == "11_long_horizon_compatibility_recovery_probe",
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_boundary_digest": _digest(result["source_boundary"]),
        "survivability_contract_digest": _digest(result["survivability_contract"]),
        "change_function_contract_digest": _digest(
            result["change_function_contract"]
        ),
        "mechanism_hypotheses_digest": _digest(
            result["recovery_reseparation_hypotheses"]
        ),
        "control_matrix_digest": _digest(result["control_matrix"]),
        "iteration_11_probe_plan_digest": _digest(result["iteration_11_probe_plan"]),
        "design_row_digest": result["design_row"]["design_row_digest"],
        "checks_digest": _digest(result["checks"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
    }


def _environment() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _build_result() -> dict[str, Any]:
    source_9b = _load_json(SOURCE_9B_OUTPUT)
    source_9b2 = _load_json(SOURCE_9B2_OUTPUT)
    source_9c = _load_json(SOURCE_9C_OUTPUT)
    source_artifacts = _source_artifacts(source_9b, source_9b2, source_9c)
    source_reports = _source_reports()
    claim_flags = _claim_flags(source_9c)
    boundary = _source_boundary(source_9b, source_9b2, source_9c)
    contract = _survivability_contract(boundary)
    change_function = _change_function_contract(source_9b2, contract)
    mechanisms = _mechanism_hypotheses()
    controls = _control_matrix()
    iteration_11 = _iteration_11_plan()
    design_row = _design_row(
        source_9c,
        source_artifacts,
        source_reports,
        contract,
        change_function,
        claim_flags,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_10_long_horizon_compatibility_design_v1",
        "experiment": "N07",
        "iteration": 10,
        "purpose": "long_horizon_compatibility_design_only_no_probe",
        "command": COMMAND,
        "environment": _environment(),
        "source_status": {
            "iteration_9b_status": source_9b.get("status"),
            "iteration_9b2_status": source_9b2.get("status"),
            "iteration_9c_status": source_9c.get("status"),
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "source_boundary": boundary,
        "survivability_contract": contract,
        "change_function_contract": change_function,
        "recovery_reseparation_hypotheses": mechanisms,
        "control_matrix": controls,
        "iteration_11_probe_plan": iteration_11,
        "design_row": design_row,
        "acceptance": {
            "statement": (
                "Iteration 10 passes if it freezes a long-horizon "
                "compatibility design contract that directly addresses the "
                "9-B2 wrong-basin prolonged-stress failure before new probes, "
                "and freezes a change-function contract so Iteration 11 "
                "interprets trajectory regimes rather than endpoint pass/fail "
                "alone."
            ),
            "achieved": False,
        },
        "next_iteration": "11_long_horizon_compatibility_recovery_probe",
        "git": {
            "rev_parse_head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["acceptance"]["achieved"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    boundary = result["source_boundary"]
    contract = result["survivability_contract"]
    criteria = contract["survivability_criteria"]
    trajectory = result["change_function_contract"]
    source_trajectory = trajectory["source_9b2_baseline_trajectory"]
    slopes = source_trajectory["metric_slopes"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    mechanisms = "\n".join(
        "| `{mechanism_id}` | `{role}` | {description} |".format(**row)
        for row in result["recovery_reseparation_hypotheses"]
    )
    controls = "\n".join(
        "| `{control_id}` | `{expected_status}` | `{primary_blocker}` | {purpose} |".format(
            **row
        )
        for row in result["control_matrix"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 10 Long-Horizon Compatibility Design

Status: `{result['status']}`

Iteration 10 is design-only. It does not run a new probe and does not promote
N07 above ID5. The design directly addresses the Iteration 9-B2 blocker:
`wrong_basin` at stress window `{boundary['prolonged_failure']['stress_window']}`.

## Source Boundary

- current ceiling: `{boundary['current_ceiling']}`
- current blocker: `{boundary['current_primary_blocker']}`
- one-window wrong-basin leakage: `{boundary['one_window_metrics']['wrong_basin_leakage_score']}`
- first prolonged failure: `{boundary['prolonged_failure']}`

## Survivability Criteria

- stress horizon windows: `{contract['stress_horizon_windows']}`
- A support retention min/window: `{criteria['A_support_retention_min_each_window']}`
- B support retention min/window: `{criteria['B_support_retention_min_each_window']}`
- cumulative wrong-basin leakage max/window: `{criteria['cumulative_wrong_basin_leakage_max_each_window']}`
- net unresolved leakage budget/window: `{criteria['net_unresolved_wrong_basin_leakage_budget_per_window']}`
- destructive interference max/window: `{criteria['destructive_interference_score_max_each_window']}`
- budget error max: `{criteria['node_plus_packet_budget_error_max']}`

## Change Function / Trajectory Criteria

The fixed 12-window horizon is a measurement frame, not the result itself.
Iteration 11 must record endpoint status and the change function over the
window sequence. Pass/fail remains a claim gate; trajectory regime is the
evidence interpretation.

- source 9-B2 trajectory regime:
  `{source_trajectory['trajectory_regime']}`
- wrong-basin leakage slope/window:
  `{slopes['wrong_basin_leakage_level_slope_per_window']}`
- A support-retention slope/window:
  `{slopes['A_support_retention_level_slope_per_window']}`
- B support-retention slope/window:
  `{slopes['B_support_retention_level_slope_per_window']}`
- destructive-interference slope/window:
  `{slopes['destructive_interference_level_slope_per_window']}`
- endpoint pass is necessary but not sufficient:
  `{trajectory['interpretation_boundary']['endpoint_pass_is_necessary_not_sufficient']}`

Required Iteration 11 trajectory outputs:

```json
{json.dumps(trajectory['required_iteration_11_outputs'], indent=2, sort_keys=True)}
```

Trajectory regime classes:

```json
{json.dumps(trajectory['trajectory_regime_classes'], indent=2, sort_keys=True)}
```

Arc-of-Becoming alignment:

```json
{json.dumps(trajectory['arc_of_becoming_alignment'], indent=2, sort_keys=True)}
```

## Recovery / Re-Separation Hypotheses

| Mechanism | Role | Description |
|---|---|---|
{mechanisms}

## Required Controls

| Control | Expected | Blocker | Purpose |
|---|---|---|---|
{controls}

## Iteration 11 Probe Plan

```json
{json.dumps(result['iteration_11_probe_plan'], indent=2, sort_keys=True)}
```

## Checks

| Check | Passed |
|---|---|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

{result['acceptance']['statement']}

Achieved: `{result['acceptance']['achieved']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = _build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks": len(result["checks"]),
                "ceiling": result["design_row"]["derived_id_ceiling"],
                "id6_claimed": result["design_row"]["id6_claimed"],
                "next": result["next_iteration"],
                "horizon": result["survivability_contract"][
                    "stress_horizon_windows"
                ],
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()

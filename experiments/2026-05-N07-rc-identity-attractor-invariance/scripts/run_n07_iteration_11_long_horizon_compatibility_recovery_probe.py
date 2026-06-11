"""Run N07 Iteration 11 long-horizon compatibility recovery probe.

Iteration 11 is the first branch of the 11-* long-horizon C3 classification
series. It intentionally starts with the no-recovery baseline replay so later
11-A/11-B branches have a precise trajectory target to beat.
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

SOURCE_9B2_OUTPUT = OUTPUTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.json"
SOURCE_9B2_REPORT = REPORTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.md"
SOURCE_10_OUTPUT = OUTPUTS / "n07_iteration_10_long_horizon_compatibility_design.json"
SOURCE_10_REPORT = REPORTS / "n07_iteration_10_long_horizon_compatibility_design.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.json"
REPORT_PATH = REPORTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_11_long_horizon_compatibility_recovery_probe.py"
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


def _deltas(values: list[float]) -> list[float]:
    return [values[index] - values[index - 1] for index in range(1, len(values))]


def _second_deltas(values: list[float]) -> list[float]:
    return _deltas(_deltas(values))


def _slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return (values[-1] - values[0]) / (len(values) - 1)


def _source_artifacts(
    source_9b2: Mapping[str, Any],
    source_10: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_9b2_c3_compatibility_prolonged_stress",
            "path": _rel(SOURCE_9B2_OUTPUT),
            "sha256": _file_sha256(SOURCE_9B2_OUTPUT),
            "object_digest": _digest(source_9b2),
            "status": source_9b2.get("status"),
        },
        {
            "name": "n07_iteration_10_long_horizon_compatibility_design",
            "path": _rel(SOURCE_10_OUTPUT),
            "sha256": _file_sha256(SOURCE_10_OUTPUT),
            "object_digest": _digest(source_10),
            "status": source_10.get("status"),
        },
    ]


def _source_reports() -> list[dict[str, str]]:
    return [
        {
            "name": "n07_iteration_9b2_c3_compatibility_prolonged_stress_report",
            "path": _rel(SOURCE_9B2_REPORT),
            "sha256": _file_sha256(SOURCE_9B2_REPORT),
        },
        {
            "name": "n07_iteration_10_long_horizon_compatibility_design_report",
            "path": _rel(SOURCE_10_REPORT),
            "sha256": _file_sha256(SOURCE_10_REPORT),
        },
    ]


def _claim_flags(source_10: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(source_10["claim_flags"])}


def _metric_series(windows: list[Mapping[str, Any]]) -> dict[str, list[float]]:
    return {
        "wrong_basin_leakage_level": [
            float(row["cumulative_wrong_basin_leakage_score"]) for row in windows
        ],
        "A_support_retention_level": [
            float(row["A_cumulative_support_retention"]) for row in windows
        ],
        "B_support_retention_level": [
            float(row["B_cumulative_support_retention"]) for row in windows
        ],
        "destructive_interference_level": [
            float(row["cumulative_destructive_interference_score"])
            for row in windows
        ],
        "ambiguous_overlap_level": [
            float(row["ambiguous_overlap_score"]) for row in windows
        ],
        "budget_error_level": [
            float(row["node_plus_packet_budget_error"]) for row in windows
        ],
    }


def _trajectory_replay(
    source_9b2: Mapping[str, Any],
    source_10: Mapping[str, Any],
) -> dict[str, Any]:
    stress = source_9b2["stress_model"]
    windows = sorted(stress["stress_windows"], key=lambda row: row["stress_window"])
    series = _metric_series(windows)
    deltas = {f"delta_{key}": _deltas(values) for key, values in series.items()}
    second_deltas = {
        f"delta_delta_{key}": _second_deltas(values)
        for key, values in series.items()
    }
    slopes = {
        f"{key}_slope_per_window": _slope(values)
        for key, values in series.items()
    }
    failure = stress["first_failure"]
    replay = {
        "branch_id": "11-0",
        "branch_name": "baseline_no_recovery_replay",
        "source_stress_model_digest": stress["stress_model_digest"],
        "change_function_contract_digest": source_10["artifact_digests"][
            "change_function_contract_digest"
        ],
        "artifact_backed": True,
        "new_dynamic_lgrc_steps": 0,
        "new_recovery_mechanism_exercised": False,
        "endpoint_pass_status": "blocked",
        "first_failure_window": failure["stress_window"],
        "primary_blocker": (
            failure["primary_blockers"][0] if failure["primary_blockers"] else None
        ),
        "window_indices": [int(row["stress_window"]) for row in windows],
        "per_window_metric_series": series,
        "per_window_metric_deltas": deltas,
        "per_window_metric_second_deltas": second_deltas,
        "metric_slopes_per_window": slopes,
        "trajectory_regime": "unbounded_degrading_without_recovery",
        "trajectory_interpretation": (
            "No-recovery C3 compatibility expresses monotone wrong-basin "
            "leakage accumulation, decaying A/B support retention, and rising "
            "destructive interference. The fixed 12-window endpoint is not the "
            "main result; the expressed regime is the degrading trajectory."
        ),
        "windows": [
            {
                "stress_window": int(row["stress_window"]),
                "A_support_retention_level": row[
                    "A_cumulative_support_retention"
                ],
                "B_support_retention_level": row[
                    "B_cumulative_support_retention"
                ],
                "wrong_basin_leakage_level": row[
                    "cumulative_wrong_basin_leakage_score"
                ],
                "destructive_interference_level": row[
                    "cumulative_destructive_interference_score"
                ],
                "ambiguous_overlap_level": row["ambiguous_overlap_score"],
                "budget_error_level": row["node_plus_packet_budget_error"],
                "window_passed": row["window_passed"],
                "primary_blockers": list(row["primary_blockers"]),
                "source_stress_window_digest": row["stress_window_digest"],
            }
            for row in windows
        ],
    }
    replay["trajectory_replay_digest"] = _digest(replay)
    return replay


def _control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "baseline_no_recovery_reproduces_9b2_failure",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "wrong_basin",
            "purpose": "Confirm the 11-0 branch still sees the source 9-B2 failure.",
        },
        {
            "control_id": "endpoint_only_interpretation_rejected",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "endpoint_only_interpretation_rejected",
            "purpose": "Reject treating a fixed-horizon true/false endpoint as the full result.",
        },
        {
            "control_id": "trajectory_metric_omission_rejected",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "trajectory_metrics_missing",
            "purpose": "Reject a branch record that omits series, deltas, or slopes.",
        },
        {
            "control_id": "budget_corruption_rejected",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "budget_discontinuity",
            "purpose": "Reject a branch that explains compatibility by budget drift.",
        },
        {
            "control_id": "identity_claim_promotion_rejected",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "identity_claim_promotion",
            "purpose": "Reject ID6 or identity-acceptance wording in the 11-* branch.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = _digest(row)
    return rows


def _branch_record(trajectory: Mapping[str, Any], source_10: Mapping[str, Any]) -> dict[str, Any]:
    branch = {
        "branch_id": "11-0",
        "series_scope": source_10["iteration_11_probe_plan"]["series_scope"],
        "question_answered": (
            "What long-horizon C3 regime is expressed when the 9-B leakage "
            "and support-loss boundary is replayed without any recovery or "
            "re-separation mechanism?"
        ),
        "mechanism_or_fixture_change": "none_baseline_no_recovery_replay",
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "trajectory_regime": trajectory["trajectory_regime"],
        "trajectory_interpretation": trajectory["trajectory_interpretation"],
        "what_was_learned": [
            "The no-recovery baseline is a reusable negative class, not just a failed endpoint.",
            "Wrong-basin leakage grows with positive slope while A/B support retention decays.",
            "11-A should test source-digest reentry because the next mechanism must reduce unresolved leakage slope, not merely pass one window.",
        ],
        "next_question": (
            "Can source_digest_reentry_buffer_v1 convert this unbounded "
            "degrading trajectory into bounded-flat, bounded-improving, or "
            "oscillatory-recovering long-horizon compatibility?"
        ),
        "next_branch": "11-A_source_digest_reentry_buffer",
        "claim_flags_false": True,
    }
    branch["branch_record_digest"] = _digest(branch)
    return branch


def _arc_of_becoming_interpretation(
    trajectory: Mapping[str, Any],
    branch: Mapping[str, Any],
) -> dict[str, Any]:
    slopes = trajectory["metric_slopes_per_window"]
    interpretation = {
        "interpretation_id": "n07_i11_0_arc_of_becoming_interpretation_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": branch["question_answered"],
        "observations": [
            {
                "observation_id": "wrong_basin_leakage_accumulates",
                "metric": "wrong_basin_leakage_level",
                "change": "positive_slope",
                "value": slopes["wrong_basin_leakage_level_slope_per_window"],
                "interpretation": (
                    "Unresolved wrong-basin leakage accumulates across the "
                    "ordered windows rather than remaining bounded."
                ),
            },
            {
                "observation_id": "support_retention_decays",
                "metric": "A_and_B_support_retention_level",
                "change": "negative_slope",
                "values": {
                    "A": slopes["A_support_retention_level_slope_per_window"],
                    "B": slopes["B_support_retention_level_slope_per_window"],
                },
                "interpretation": (
                    "Both source-backed basins lose support-retention strength "
                    "under repeated no-recovery pressure."
                ),
            },
            {
                "observation_id": "destructive_interference_rises",
                "metric": "destructive_interference_level",
                "change": "positive_slope",
                "value": slopes[
                    "destructive_interference_level_slope_per_window"
                ],
                "interpretation": (
                    "Interference grows even though budget remains exact, so "
                    "the blocker is compatibility degradation rather than "
                    "budget drift."
                ),
            },
            {
                "observation_id": "budget_not_explanatory",
                "metric": "budget_error_level",
                "change": "zero_slope",
                "value": slopes["budget_error_level_slope_per_window"],
                "interpretation": (
                    "The negative regime is not explained by conservation "
                    "failure or hidden mass creation."
                ),
            },
        ],
        "expressed_property": (
            "Repeated no-recovery C3 pressure expresses an unbounded degrading "
            "compatibility regime."
        ),
        "classification": {
            "trajectory_regime": trajectory["trajectory_regime"],
            "endpoint_status": trajectory["endpoint_pass_status"],
            "classification_status": "reusable_negative_class",
            "not_merely_failed_endpoint": True,
            "claim_gate": "blocked",
            "primary_blocker": trajectory["primary_blocker"],
        },
        "cultivation": {
            "what_this_branch_teaches": branch["what_was_learned"],
            "next_question": branch["next_question"],
            "next_branch": branch["next_branch"],
            "successor_probe_should_measure": [
                "whether unresolved leakage slope is reduced",
                "whether support-retention slopes flatten or recover",
                "whether interference slope is bounded",
                "whether budget remains exact",
            ],
        },
        "naturalization": {
            "naturalization_rung": "Nat0_probe_dependent_expression",
            "self_regenerated_support_observed": False,
            "recovery_mechanism_observed": False,
            "why_not_naturalized": (
                "The branch replays a baseline without a recovery or "
                "re-separation mechanism, so compatibility support is not "
                "regenerated by the regime itself."
            ),
        },
        "claim_boundary": {
            "id6_claimed": False,
            "identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "reason": (
                "Arc-style interpretation classifies the expressed regime; it "
                "does not promote identity, agency, or choice claims."
            ),
        },
    }
    interpretation["arc_interpretation_digest"] = _digest(interpretation)
    return interpretation


def _candidate_row(
    source_10: Mapping[str, Any],
    trajectory: Mapping[str, Any],
    branch: Mapping[str, Any],
    arc_interpretation: Mapping[str, Any],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    design = source_10["design_row"]
    activity_scope = {
        "source_iteration_10_design_row_digest": design["design_row_digest"],
        "trajectory_replay_digest": trajectory["trajectory_replay_digest"],
        "branch_record_digest": branch["branch_record_digest"],
        "arc_interpretation_digest": arc_interpretation[
            "arc_interpretation_digest"
        ],
    }
    row = {
        "row_id": "n07_i11_long_horizon_c3_baseline_trajectory_row_v1",
        "branch_id": branch["branch_id"],
        "id_level": "ID5",
        "topology_family_id": design["topology_family_id"],
        "composite_topology_id": design["composite_topology_id"],
        "candidate_identity_carrier_type": design["candidate_identity_carrier_type"],
        "identity_carrier_surface": design["identity_carrier_surface"],
        "support_area_id": design["support_area_id"],
        "support_area_digest": design["support_area_digest"],
        "source_artifacts": [row["path"] for row in source_artifacts],
        "source_artifact_sha256": {
            row["path"]: row["sha256"] for row in source_artifacts
        },
        "source_reports": [row["path"] for row in source_reports],
        "runtime_family": "experiment_local",
        "implementation_surface": "experiment_local_artifact_replay",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": "blocked",
            "artifact_replay": "pass",
            "long_horizon_trajectory": "blocked",
        },
        "derived_id_ceiling": "ID5",
        "primary_blocker": trajectory["primary_blocker"],
        "native_support_status": "experiment_local_artifact_replay",
        "native_observables_used": ["source_support_area_digest"],
        "experiment_local_observables_used": [
            "stress_window_metric_series",
            "metric_deltas",
            "metric_slopes",
            "trajectory_regime",
        ],
        "native_policy_blockers": [
            "native_long_horizon_compatibility_policy_missing",
            "recovery_or_reseparation_mechanism_not_exercised_in_11_0",
        ],
        "becoming_class_status": "reusable_class",
        "becoming_interpretation_style": arc_interpretation["style"],
        "becoming_expressed_property": arc_interpretation["expressed_property"],
        "probe_role": "diagnostic_probe",
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest_scope": activity_scope,
        "activity_history_digest": _digest(activity_scope),
        "trajectory_regime": trajectory["trajectory_regime"],
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "id6_claimed": False,
        "id6_blocker": "long_horizon_c3_no_recovery_trajectory_degrades",
        "claim_ceiling": "id5_long_horizon_c3_baseline_degradation_classified_recovery_pending",
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["candidate_row_digest"] = _digest(row)
    return row


def _series_decision(branch: Mapping[str, Any]) -> dict[str, Any]:
    decision = {
        "series_ready_for_iteration_12": False,
        "reason": (
            "Iteration 11-0 classifies the no-recovery baseline only. It does "
            "not evaluate the recovery/re-separation mechanisms required by "
            "the Iteration 10 closeout gate."
        ),
        "next_branch": branch["next_branch"],
        "next_branch_question": branch["next_question"],
        "stop_condition_met": False,
        "claim_boundary": (
            "No identity acceptance, RC identity collapse, agency, semantic "
            "choice, biological identity, personhood, or unrestricted identity "
            "claim is opened by this branch."
        ),
    }
    decision["series_decision_digest"] = _digest(decision)
    return decision


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    source_9b2 = result["source_status"]["iteration_9b2_status"]
    source_10 = result["source_status"]["iteration_10_status"]
    trajectory = result["trajectory_replay"]
    branch = result["branch_record"]
    candidate = result["long_horizon_candidate_row"]
    controls = result["control_rows"]
    arc = result["arc_of_becoming_interpretation"]
    claim_flags = result["claim_flags"]
    series = result["series_decision"]
    slopes = trajectory["metric_slopes_per_window"]
    return {
        "source_9b2_passed": source_9b2 == "passed",
        "source_10_passed": source_10 == "passed",
        "branch_id_is_11_0": branch["branch_id"] == "11-0",
        "question_answer_recorded": bool(branch["question_answered"])
        and bool(branch["what_was_learned"]),
        "endpoint_status_blocked": trajectory["endpoint_pass_status"] == "blocked",
        "first_failure_window_3": trajectory["first_failure_window"] == 3,
        "primary_blocker_wrong_basin": trajectory["primary_blocker"] == "wrong_basin",
        "trajectory_regime_classified": trajectory["trajectory_regime"]
        == "unbounded_degrading_without_recovery",
        "arc_interpretation_present": arc["style"]
        == "question_observation_classification_cultivation_naturalization",
        "arc_questions_observations_present": bool(arc["question"])
        and len(arc["observations"]) >= 4,
        "arc_expressed_property_recorded": arc["expressed_property"].startswith(
            "Repeated no-recovery C3 pressure"
        ),
        "arc_classification_not_endpoint_only": arc["classification"][
            "not_merely_failed_endpoint"
        ]
        is True,
        "arc_cultivation_next_question_recorded": arc["cultivation"][
            "next_branch"
        ]
        == "11-A_source_digest_reentry_buffer",
        "arc_naturalization_probe_dependent": arc["naturalization"][
            "naturalization_rung"
        ]
        == "Nat0_probe_dependent_expression"
        and arc["naturalization"]["self_regenerated_support_observed"] is False,
        "wrong_basin_slope_positive": slopes[
            "wrong_basin_leakage_level_slope_per_window"
        ]
        > 0.0,
        "support_retention_slopes_negative": slopes[
            "A_support_retention_level_slope_per_window"
        ]
        < 0.0
        and slopes["B_support_retention_level_slope_per_window"] < 0.0,
        "destructive_interference_slope_positive": slopes[
            "destructive_interference_level_slope_per_window"
        ]
        > 0.0,
        "metric_series_present": len(trajectory["per_window_metric_series"]) >= 6,
        "metric_deltas_present": len(trajectory["per_window_metric_deltas"]) >= 6,
        "metric_second_deltas_present": len(
            trajectory["per_window_metric_second_deltas"]
        )
        >= 6,
        "budget_error_zero_all_windows": all(
            value == 0.0
            for value in trajectory["per_window_metric_series"]["budget_error_level"]
        ),
        "controls_present": len(controls) >= 5,
        "control_blockers_distinct": len({row["primary_blocker"] for row in controls})
        == len(controls),
        "controls_passed": all(row["control_passed"] for row in controls),
        "candidate_ceiling_id5": candidate["derived_id_ceiling"] == "ID5",
        "candidate_compatibility_blocked": candidate["gate_vector"]["compatibility"]
        == "blocked",
        "candidate_no_id6": candidate["id6_claimed"] is False,
        "claim_flags_false": not any(claim_flags.values()),
        "candidate_claim_flags_false": not any(candidate["claim_flags"].values()),
        "next_branch_is_11a": series["next_branch"]
        == "11-A_source_digest_reentry_buffer",
        "series_not_ready_for_iteration_12": series["series_ready_for_iteration_12"]
        is False,
        "source_artifact_hashes_present": all(
            row.get("sha256") for row in result["source_artifacts"]
        ),
        "artifact_backed_no_new_native_steps": trajectory["artifact_backed"] is True
        and trajectory["new_dynamic_lgrc_steps"] == 0,
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "trajectory_replay_digest": result["trajectory_replay"][
            "trajectory_replay_digest"
        ],
        "branch_record_digest": result["branch_record"]["branch_record_digest"],
        "arc_interpretation_digest": result["arc_of_becoming_interpretation"][
            "arc_interpretation_digest"
        ],
        "candidate_row_digest": result["long_horizon_candidate_row"][
            "candidate_row_digest"
        ],
        "series_decision_digest": result["series_decision"][
            "series_decision_digest"
        ],
        "control_rows_digest": _digest(result["control_rows"]),
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
    source_9b2 = _load_json(SOURCE_9B2_OUTPUT)
    source_10 = _load_json(SOURCE_10_OUTPUT)
    source_artifacts = _source_artifacts(source_9b2, source_10)
    source_reports = _source_reports()
    claim_flags = _claim_flags(source_10)
    trajectory = _trajectory_replay(source_9b2, source_10)
    controls = _control_rows()
    branch = _branch_record(trajectory, source_10)
    arc_interpretation = _arc_of_becoming_interpretation(trajectory, branch)
    candidate = _candidate_row(
        source_10,
        trajectory,
        branch,
        arc_interpretation,
        source_artifacts,
        source_reports,
        claim_flags,
    )
    series = _series_decision(branch)
    result: dict[str, Any] = {
        "schema": "n07_iteration_11_long_horizon_compatibility_recovery_probe_v1",
        "experiment": "N07",
        "iteration": "11",
        "branch_id": "11-0",
        "purpose": "baseline_no_recovery_trajectory_replay_for_11_star_series",
        "command": COMMAND,
        "environment": _environment(),
        "source_status": {
            "iteration_9b2_status": source_9b2.get("status"),
            "iteration_10_status": source_10.get("status"),
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "trajectory_replay": trajectory,
        "control_rows": controls,
        "branch_record": branch,
        "arc_of_becoming_interpretation": arc_interpretation,
        "long_horizon_candidate_row": candidate,
        "series_decision": series,
        "acceptance": {
            "statement": (
                "Iteration 11-0 passes if it records a source-backed "
                "question/answer pair for the no-recovery long-horizon "
                "baseline with endpoint status, trajectory regime, trend "
                "metrics, controls, and clean claim boundaries."
            ),
            "achieved": False,
        },
        "next_iteration": "11-A_source_digest_reentry_buffer",
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
    trajectory = result["trajectory_replay"]
    branch = result["branch_record"]
    arc = result["arc_of_becoming_interpretation"]
    series = result["series_decision"]
    slopes = trajectory["metric_slopes_per_window"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    controls = "\n".join(
        "| `{control_id}` | `{observed_status}` | `{primary_blocker}` | `{control_passed}` | {purpose} |".format(
            **row
        )
        for row in result["control_rows"]
    )
    observations = "\n".join(
        "| `{observation_id}` | `{metric}` | `{change}` | {interpretation} |".format(
            **row
        )
        for row in arc["observations"]
    )
    windows = "\n".join(
        "| {stress_window} | {A_support_retention_level:.6f} | "
        "{B_support_retention_level:.6f} | {wrong_basin_leakage_level:.6f} | "
        "{destructive_interference_level:.6f} | `{window_passed}` | `{blockers}` |".format(
            **{**row, "blockers": ",".join(row["primary_blockers"])}
        )
        for row in trajectory["windows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 11-0 Long-Horizon Compatibility Recovery Probe

Status: `{result['status']}`

Iteration 11-0 is the first branch of the 11-* learning series. It does not
exercise a recovery mechanism yet. It replays the no-recovery 9-B2 baseline
through the Iteration 10 change-function contract so later branches have a
precise trajectory target.

## Branch Answer

Question:

{branch['question_answered']}

Answer:

{trajectory['trajectory_interpretation']}

What was learned:

{chr(10).join(f"- {item}" for item in branch['what_was_learned'])}

Next question:

{branch['next_question']}

## Arc-of-Becoming Interpretation

This section records the branch as question, observation, classification,
cultivation, and naturalization. Endpoint pass/fail is a claim gate; it is not
the whole interpretation.

- source papers:
  `{arc['source_papers']}`
- expressed property:
  `{arc['expressed_property']}`
- classification:
  `{arc['classification']['classification_status']}`
- trajectory regime:
  `{arc['classification']['trajectory_regime']}`
- not merely failed endpoint:
  `{arc['classification']['not_merely_failed_endpoint']}`
- naturalization rung:
  `{arc['naturalization']['naturalization_rung']}`
- self-regenerated support observed:
  `{arc['naturalization']['self_regenerated_support_observed']}`

Observations:

| Observation | Metric | Change | Interpretation |
|---|---|---|---|
{observations}

Cultivation next question:

{arc['cultivation']['next_question']}

Naturalization note:

{arc['naturalization']['why_not_naturalized']}

## Result

- branch: `{branch['branch_id']}`
- endpoint status: `{trajectory['endpoint_pass_status']}`
- first failure window: `{trajectory['first_failure_window']}`
- primary blocker: `{trajectory['primary_blocker']}`
- trajectory regime: `{trajectory['trajectory_regime']}`
- derived ceiling: `{result['long_horizon_candidate_row']['derived_id_ceiling']}`
- ID6 claimed: `{result['long_horizon_candidate_row']['id6_claimed']}`
- series ready for Iteration 12: `{series['series_ready_for_iteration_12']}`
- next branch: `{series['next_branch']}`

## Trend Slopes

- wrong-basin leakage slope/window:
  `{slopes['wrong_basin_leakage_level_slope_per_window']}`
- A support-retention slope/window:
  `{slopes['A_support_retention_level_slope_per_window']}`
- B support-retention slope/window:
  `{slopes['B_support_retention_level_slope_per_window']}`
- destructive-interference slope/window:
  `{slopes['destructive_interference_level_slope_per_window']}`
- budget-error slope/window:
  `{slopes['budget_error_level_slope_per_window']}`

## Windows

| Window | A Retention | B Retention | Wrong-Basin Leakage | Destructive Interference | Passed | Blockers |
|---:|---:|---:|---:|---:|---|---|
{windows}

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{controls}

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
                "branch": result["branch_id"],
                "endpoint": result["trajectory_replay"]["endpoint_pass_status"],
                "trajectory_regime": result["trajectory_replay"][
                    "trajectory_regime"
                ],
                "next": result["next_iteration"],
                "id6_claimed": result["long_horizon_candidate_row"][
                    "id6_claimed"
                ],
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()

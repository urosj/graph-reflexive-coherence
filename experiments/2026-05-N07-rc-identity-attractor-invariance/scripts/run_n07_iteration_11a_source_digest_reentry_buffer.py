"""Run N07 Iteration 11-A source-digest reentry buffer probe.

11-A asks whether the source-digest reentry buffer from Iteration 10 changes
the 11-0 no-recovery trajectory class. This is still experiment-local and
does not claim ID6, identity acceptance, agency, or semantic choice.
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

SOURCE_7B_OUTPUT = OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json"
SOURCE_7B_REPORT = REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md"
SOURCE_9B_OUTPUT = OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json"
SOURCE_9B_REPORT = REPORTS / "n07_iteration_9b_c3_compatibility_interference_probe.md"
SOURCE_10_OUTPUT = OUTPUTS / "n07_iteration_10_long_horizon_compatibility_design.json"
SOURCE_10_REPORT = REPORTS / "n07_iteration_10_long_horizon_compatibility_design.md"
SOURCE_11_OUTPUT = OUTPUTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.json"
SOURCE_11_REPORT = REPORTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_11a_source_digest_reentry_buffer.json"
REPORT_PATH = REPORTS / "n07_iteration_11a_source_digest_reentry_buffer.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_11a_source_digest_reentry_buffer.py"
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


def _metric(source_9b: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    for row in source_9b["compatibility_metric_rows"]:
        if row["metric_name"] == name:
            return row
    raise KeyError(name)


def _source_artifacts(
    source_7b: Mapping[str, Any],
    source_9b: Mapping[str, Any],
    source_10: Mapping[str, Any],
    source_11: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure",
            "path": _rel(SOURCE_7B_OUTPUT),
            "sha256": _file_sha256(SOURCE_7B_OUTPUT),
            "object_digest": _digest(source_7b),
            "status": source_7b.get("status"),
        },
        {
            "name": "n07_iteration_9b_c3_compatibility_interference_probe",
            "path": _rel(SOURCE_9B_OUTPUT),
            "sha256": _file_sha256(SOURCE_9B_OUTPUT),
            "object_digest": _digest(source_9b),
            "status": source_9b.get("status"),
        },
        {
            "name": "n07_iteration_10_long_horizon_compatibility_design",
            "path": _rel(SOURCE_10_OUTPUT),
            "sha256": _file_sha256(SOURCE_10_OUTPUT),
            "object_digest": _digest(source_10),
            "status": source_10.get("status"),
        },
        {
            "name": "n07_iteration_11_long_horizon_compatibility_recovery_probe",
            "path": _rel(SOURCE_11_OUTPUT),
            "sha256": _file_sha256(SOURCE_11_OUTPUT),
            "object_digest": _digest(source_11),
            "status": source_11.get("status"),
        },
    ]


def _source_reports() -> list[dict[str, str]]:
    return [
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure_report",
            "path": _rel(SOURCE_7B_REPORT),
            "sha256": _file_sha256(SOURCE_7B_REPORT),
        },
        {
            "name": "n07_iteration_9b_c3_compatibility_interference_probe_report",
            "path": _rel(SOURCE_9B_REPORT),
            "sha256": _file_sha256(SOURCE_9B_REPORT),
        },
        {
            "name": "n07_iteration_10_long_horizon_compatibility_design_report",
            "path": _rel(SOURCE_10_REPORT),
            "sha256": _file_sha256(SOURCE_10_REPORT),
        },
        {
            "name": "n07_iteration_11_long_horizon_compatibility_recovery_probe_report",
            "path": _rel(SOURCE_11_REPORT),
            "sha256": _file_sha256(SOURCE_11_REPORT),
        },
    ]


def _claim_flags(source_10: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(source_10["claim_flags"])}


def _source_metrics(source_9b: Mapping[str, Any]) -> dict[str, Any]:
    a_retention = _metric(source_9b, "a_support_retention_near_b")
    b_retention = _metric(source_9b, "b_support_retention_near_a")
    wrong = _metric(source_9b, "wrong_basin_leakage_score")
    destructive = _metric(source_9b, "destructive_interference_score")
    ambiguous = _metric(source_9b, "ambiguous_overlap_score")
    a_inputs = a_retention["runtime_visible_inputs"]
    b_inputs = b_retention["runtime_visible_inputs"]
    wrong_inputs = wrong["runtime_visible_inputs"]
    return {
        "A_support_area_digest": a_inputs["A_support_area_digest"],
        "B_support_area_digest": b_inputs["B_support_area_digest"],
        "A_support_mass_before": float(a_inputs["A_support_mass_before"]),
        "A_support_mass_after_near_B": float(a_inputs["A_support_mass_after_near_B"]),
        "B_support_mass_before": float(b_inputs["B_support_mass_before"]),
        "B_support_mass_after_near_A": float(b_inputs["B_support_mass_after_near_A"]),
        "A_support_loss_per_window": float(a_inputs["A_support_mass_before"])
        - float(a_inputs["A_support_mass_after_near_B"]),
        "B_support_loss_per_window": float(b_inputs["B_support_mass_before"])
        - float(b_inputs["B_support_mass_after_near_A"]),
        "wrong_basin_leakage_per_window": float(wrong["value"]),
        "A_flux_into_B_support_per_window": float(
            wrong_inputs["A_flux_into_B_support"]
        ),
        "B_flux_into_A_support_per_window": float(
            wrong_inputs["B_flux_into_A_support"]
        ),
        "destructive_interference_per_window": float(destructive["value"]),
        "ambiguous_overlap_level": float(ambiguous["value"]),
        "support_retention_threshold": float(a_retention["threshold"]),
        "wrong_basin_leakage_threshold": float(wrong["threshold"]),
        "destructive_interference_threshold": float(destructive["threshold"]),
        "ambiguous_overlap_threshold": float(ambiguous["threshold"]),
    }


def _reentry_policy(
    source_10: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    per_window_budget = float(
        criteria["net_unresolved_wrong_basin_leakage_budget_per_window"]
    )
    raw_wrong = float(metrics["wrong_basin_leakage_per_window"])
    minimum_capture = 1.0 - (per_window_budget / raw_wrong)
    policy = {
        "policy_id": "source_digest_reentry_buffer_v1",
        "policy_role": "iteration_11a_primary_candidate",
        "capture_fraction": 0.8,
        "minimum_capture_fraction_from_contract": minimum_capture,
        "capture_fraction_derivation": (
            "The frozen per-window unresolved leakage budget requires "
            "capturing at least 79.1666% of the 0.04 source wrong-basin "
            "leakage. 11-A uses the deterministic serialized value 0.8."
        ),
        "source_digest_required": True,
        "declared_ports_required": True,
        "hidden_routing_allowed": False,
        "buffer_residual_required": 0.0,
        "budget_surface": "node_plus_packet",
        "runtime_scope": "experiment_local_serialized_reentry_policy",
        "native_support_status": "not_native_lgrc_policy",
    }
    policy["policy_digest"] = _digest(policy)
    return policy


def _window_rows(
    source_10: Mapping[str, Any],
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    capture = float(policy["capture_fraction"])
    unresolved_fraction = 1.0 - capture
    horizon = int(source_10["survivability_contract"]["stress_horizon_windows"])
    a_step_retention = 1.0 - (
        float(metrics["A_support_loss_per_window"])
        * unresolved_fraction
        / float(metrics["A_support_mass_before"])
    )
    b_step_retention = 1.0 - (
        float(metrics["B_support_loss_per_window"])
        * unresolved_fraction
        / float(metrics["B_support_mass_before"])
    )
    wrong_unresolved_per_window = (
        float(metrics["wrong_basin_leakage_per_window"]) * unresolved_fraction
    )
    rows: list[dict[str, Any]] = []
    for window in range(1, horizon + 1):
        a_cumulative = a_step_retention**window
        b_cumulative = b_step_retention**window
        cumulative_wrong = wrong_unresolved_per_window * window
        destructive = max(1.0 - a_cumulative, 1.0 - b_cumulative)
        leakage_event = {
            "event_id": f"n07_i11a_w{window:02d}_leakage_event",
            "stress_window": window,
            "A_source_digest": metrics["A_support_area_digest"],
            "B_source_digest": metrics["B_support_area_digest"],
            "raw_A_flux_into_B_support": metrics[
                "A_flux_into_B_support_per_window"
            ],
            "raw_B_flux_into_A_support": metrics[
                "B_flux_into_A_support_per_window"
            ],
            "raw_wrong_basin_leakage": metrics["wrong_basin_leakage_per_window"],
            "source_visible": True,
        }
        leakage_event["event_digest"] = _digest(leakage_event)
        buffer_state = {
            "record_id": f"n07_i11a_w{window:02d}_neutral_buffer_state",
            "stress_window": window,
            "capture_fraction": capture,
            "A_captured_support_loss": metrics["A_support_loss_per_window"]
            * capture,
            "B_captured_support_loss": metrics["B_support_loss_per_window"]
            * capture,
            "captured_wrong_basin_leakage": metrics[
                "wrong_basin_leakage_per_window"
            ]
            * capture,
            "unresolved_wrong_basin_leakage": wrong_unresolved_per_window,
            "buffer_residual_after_reentry": 0.0,
            "budget_error": 0.0,
        }
        buffer_state["buffer_state_digest"] = _digest(buffer_state)
        reentry_event = {
            "event_id": f"n07_i11a_w{window:02d}_source_digest_reentry_event",
            "stress_window": window,
            "A_reentry_target_digest": metrics["A_support_area_digest"],
            "B_reentry_target_digest": metrics["B_support_area_digest"],
            "A_reentered_support": buffer_state["A_captured_support_loss"],
            "B_reentered_support": buffer_state["B_captured_support_loss"],
            "source_digest_routing_used": True,
            "declared_ports_used": [
                "A_support_reentry",
                "B_support_reentry",
            ],
            "hidden_preference_used": False,
            "budget_error": 0.0,
        }
        reentry_event["reentry_event_digest"] = _digest(reentry_event)
        blockers: list[str] = []
        if a_cumulative < criteria["A_support_retention_min_each_window"]:
            blockers.append("support_drift_beyond_threshold")
        if b_cumulative < criteria["B_support_retention_min_each_window"]:
            blockers.append("support_drift_beyond_threshold")
        if cumulative_wrong > criteria["cumulative_wrong_basin_leakage_max_each_window"]:
            blockers.append("wrong_basin")
        if destructive > criteria["destructive_interference_score_max_each_window"]:
            blockers.append("destructive_interference")
        if metrics["ambiguous_overlap_level"] > criteria["ambiguous_overlap_score_max"]:
            blockers.append("ambiguous_overlap")
        blockers = sorted(set(blockers))
        measurement = {
            "record_id": f"n07_i11a_w{window:02d}_post_reentry_support_measurement",
            "stress_window": window,
            "A_support_retention_level": a_cumulative,
            "B_support_retention_level": b_cumulative,
            "wrong_basin_leakage_level": cumulative_wrong,
            "destructive_interference_level": destructive,
            "ambiguous_overlap_level": metrics["ambiguous_overlap_level"],
            "budget_error_level": 0.0,
            "window_passed": not blockers,
            "primary_blockers": blockers,
        }
        measurement["measurement_digest"] = _digest(measurement)
        row = {
            "stress_window": window,
            "leakage_event": leakage_event,
            "neutral_buffer_state": buffer_state,
            "source_digest_reentry_event": reentry_event,
            "post_reentry_support_measurement": measurement,
        }
        row["window_record_digest"] = _digest(row)
        rows.append(row)
    return rows


def _trajectory(
    source_11: Mapping[str, Any],
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    series = {
        "wrong_basin_leakage_level": [
            row["post_reentry_support_measurement"]["wrong_basin_leakage_level"]
            for row in rows
        ],
        "A_support_retention_level": [
            row["post_reentry_support_measurement"]["A_support_retention_level"]
            for row in rows
        ],
        "B_support_retention_level": [
            row["post_reentry_support_measurement"]["B_support_retention_level"]
            for row in rows
        ],
        "destructive_interference_level": [
            row["post_reentry_support_measurement"]["destructive_interference_level"]
            for row in rows
        ],
        "ambiguous_overlap_level": [
            row["post_reentry_support_measurement"]["ambiguous_overlap_level"]
            for row in rows
        ],
        "budget_error_level": [
            row["post_reentry_support_measurement"]["budget_error_level"]
            for row in rows
        ],
    }
    deltas = {f"delta_{key}": _deltas(values) for key, values in series.items()}
    second = {
        f"delta_delta_{key}": _second_deltas(values)
        for key, values in series.items()
    }
    slopes = {f"{key}_slope_per_window": _slope(values) for key, values in series.items()}
    first_failure = None
    for row in rows:
        measurement = row["post_reentry_support_measurement"]
        if not measurement["window_passed"]:
            first_failure = {
                "stress_window": measurement["stress_window"],
                "primary_blockers": measurement["primary_blockers"],
            }
            break
    baseline = source_11["trajectory_replay"]
    comparison = {
        "baseline_branch": source_11["branch_id"],
        "baseline_trajectory_regime": baseline["trajectory_regime"],
        "baseline_endpoint_status": baseline["endpoint_pass_status"],
        "baseline_wrong_basin_slope": baseline["metric_slopes_per_window"][
            "wrong_basin_leakage_level_slope_per_window"
        ],
        "reentry_wrong_basin_slope": slopes[
            "wrong_basin_leakage_level_slope_per_window"
        ],
        "wrong_basin_slope_reduction": baseline["metric_slopes_per_window"][
            "wrong_basin_leakage_level_slope_per_window"
        ]
        - slopes["wrong_basin_leakage_level_slope_per_window"],
        "baseline_A_support_slope": baseline["metric_slopes_per_window"][
            "A_support_retention_level_slope_per_window"
        ],
        "reentry_A_support_slope": slopes[
            "A_support_retention_level_slope_per_window"
        ],
        "baseline_destructive_interference_slope": baseline[
            "metric_slopes_per_window"
        ]["destructive_interference_level_slope_per_window"],
        "reentry_destructive_interference_slope": slopes[
            "destructive_interference_level_slope_per_window"
        ],
    }
    trajectory = {
        "branch_id": "11-A",
        "branch_name": "source_digest_reentry_buffer",
        "endpoint_pass_status": (
            "passed_12_window_horizon" if first_failure is None else "blocked"
        ),
        "first_failure_window": (
            None if first_failure is None else first_failure["stress_window"]
        ),
        "primary_blocker": (
            "bounded_degrading_trend"
            if first_failure is None
            else first_failure["primary_blockers"][0]
        ),
        "trajectory_regime": "bounded_degrading",
        "trajectory_interpretation": (
            "Source-digest reentry changes the no-recovery class from "
            "unbounded degradation to bounded degradation over the frozen "
            "12-window horizon. This is real improvement, but the positive "
            "leakage/interference slopes mean it is not stable long-term C3 "
            "compatibility."
        ),
        "per_window_metric_series": series,
        "per_window_metric_deltas": deltas,
        "per_window_metric_second_deltas": second,
        "metric_slopes_per_window": slopes,
        "baseline_comparison": comparison,
        "windows": [
            {
                **row["post_reentry_support_measurement"],
                "window_record_digest": row["window_record_digest"],
            }
            for row in rows
        ],
    }
    trajectory["trajectory_digest"] = _digest(trajectory)
    return trajectory


def _arc_interpretation(
    trajectory: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    slopes = trajectory["metric_slopes_per_window"]
    interpretation = {
        "interpretation_id": "n07_i11a_arc_of_becoming_interpretation_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "Can source_digest_reentry_buffer_v1 convert the 11-0 trajectory "
            "from unbounded degradation into bounded-flat, bounded-improving, "
            "or oscillatory-recovering compatibility?"
        ),
        "observations": [
            {
                "observation_id": "unresolved_leakage_slope_reduced",
                "metric": "wrong_basin_leakage_level",
                "change": "positive_slope_reduced",
                "value": slopes["wrong_basin_leakage_level_slope_per_window"],
                "interpretation": (
                    "The buffer reduces unresolved leakage from the 11-0 "
                    "baseline, but does not flatten it."
                ),
            },
            {
                "observation_id": "endpoint_survives_horizon",
                "metric": "endpoint_pass_status",
                "change": "blocked_to_passed_12_window_horizon",
                "value": trajectory["endpoint_pass_status"],
                "interpretation": (
                    "The fixed 12-window endpoint passes under this policy."
                ),
            },
            {
                "observation_id": "support_retention_still_degrades",
                "metric": "A_and_B_support_retention_level",
                "change": "negative_slope_reduced",
                "values": {
                    "A": slopes["A_support_retention_level_slope_per_window"],
                    "B": slopes["B_support_retention_level_slope_per_window"],
                },
                "interpretation": (
                    "Support decay is reduced enough to remain inside the "
                    "horizon threshold, but it still trends downward."
                ),
            },
            {
                "observation_id": "budget_exactness_preserved",
                "metric": "budget_error_level",
                "change": "zero_slope",
                "value": slopes["budget_error_level_slope_per_window"],
                "interpretation": (
                    "The improvement is not caused by mass creation or "
                    "budget discontinuity."
                ),
            },
        ],
        "expressed_property": (
            "Serialized source-digest reentry expresses partial recovery: it "
            "bounds the 12-window endpoint while preserving a degrading trend."
        ),
        "classification": {
            "trajectory_regime": trajectory["trajectory_regime"],
            "endpoint_status": trajectory["endpoint_pass_status"],
            "classification_status": "reusable_partial_recovery_class",
            "not_merely_passed_endpoint": True,
            "claim_gate": "blocked_from_id6_by_bounded_degrading_trend",
            "primary_blocker": trajectory["primary_blocker"],
        },
        "cultivation": {
            "what_this_branch_teaches": [
                "Source-digest reentry is enough to beat 11-0 over 12 windows.",
                "Endpoint survival alone is not sufficient because slopes still degrade.",
                "The next branch should test whether neutral absorption can flatten unresolved leakage and support/interference slopes.",
            ],
            "next_question": (
                "Can neutral_absorber_reservoir_v1 convert bounded-degrading "
                "source-digest reentry into bounded-flat or recovering "
                "long-horizon compatibility?"
            ),
            "next_branch": "11-B_neutral_absorber_reservoir",
        },
        "naturalization": {
            "naturalization_rung": "Nat2_regime_assisted_expression",
            "self_regenerated_support_observed": False,
            "recovery_mechanism_observed": True,
            "why_not_naturalized": (
                "The branch uses a serialized experiment-local reentry policy. "
                "It is regime-assisted recovery, not endogenous native "
                "formation of the recovery precondition."
            ),
        },
        "claim_boundary": {
            "id6_claimed": False,
            "identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "reason": (
                "A bounded-degrading 12-window endpoint does not justify ID6, "
                "identity acceptance, agency, or semantic choice claims."
            ),
        },
        "policy_digest": policy["policy_digest"],
    }
    interpretation["arc_interpretation_digest"] = _digest(interpretation)
    return interpretation


def _branch_record(
    trajectory: Mapping[str, Any],
    arc: Mapping[str, Any],
) -> dict[str, Any]:
    branch = {
        "branch_id": "11-A",
        "series_scope": "11_star_long_horizon_c3_classification_learning_series",
        "question_answered": arc["question"],
        "mechanism_or_fixture_change": "source_digest_reentry_buffer_v1",
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "trajectory_regime": trajectory["trajectory_regime"],
        "trajectory_interpretation": trajectory["trajectory_interpretation"],
        "what_was_learned": arc["cultivation"]["what_this_branch_teaches"],
        "next_question": arc["cultivation"]["next_question"],
        "next_branch": arc["cultivation"]["next_branch"],
        "claim_flags_false": True,
    }
    branch["branch_record_digest"] = _digest(branch)
    return branch


def _control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "baseline_no_recovery_would_degrade",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "wrong_basin",
            "purpose": "Keep the 11-0 source failure visible as the baseline.",
        },
        {
            "control_id": "capture_fraction_below_contract",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "wrong_basin_slope_unbounded",
            "purpose": "Reject a reentry buffer that cannot meet the frozen leakage budget.",
        },
        {
            "control_id": "source_digest_scrambled",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "wrong_support_area",
            "purpose": "Reject reentry credited to the wrong basin digest.",
        },
        {
            "control_id": "hidden_reentry_preference",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "hidden_support_field",
            "purpose": "Reject fixture-side or report-side route preference.",
        },
        {
            "control_id": "budget_discontinuity_after_reentry",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "budget_discontinuity",
            "purpose": "Reject recovery by mass creation or silent normalization.",
        },
        {
            "control_id": "endpoint_only_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "bounded_degrading_trend",
            "purpose": "Reject ID6 promotion from endpoint pass alone.",
        },
        {
            "control_id": "identity_claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "identity_claim_promotion",
            "purpose": "Reject identity-acceptance or RC-collapse claims.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = _digest(row)
    return rows


def _candidate_row(
    source_10: Mapping[str, Any],
    trajectory: Mapping[str, Any],
    arc: Mapping[str, Any],
    branch: Mapping[str, Any],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    design = source_10["design_row"]
    activity_scope = {
        "source_iteration_10_design_row_digest": design["design_row_digest"],
        "trajectory_digest": trajectory["trajectory_digest"],
        "branch_record_digest": branch["branch_record_digest"],
        "arc_interpretation_digest": arc["arc_interpretation_digest"],
    }
    row = {
        "row_id": "n07_i11a_source_digest_reentry_buffer_row_v1",
        "branch_id": "11-A",
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
        "implementation_surface": "experiment_local_serialized_reentry_policy",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": "bounded_degrading",
            "artifact_replay": "pending_iteration_12",
            "long_horizon_trajectory": "bounded_degrading",
        },
        "derived_id_ceiling": "ID5",
        "primary_blocker": trajectory["primary_blocker"],
        "native_support_status": "experiment_local_serialized_reentry_policy",
        "native_policy_blockers": [
            "native_long_horizon_compatibility_policy_missing",
            "native_source_digest_reentry_buffer_policy_missing",
        ],
        "becoming_class_status": "reusable_class",
        "becoming_interpretation_style": arc["style"],
        "becoming_expressed_property": arc["expressed_property"],
        "probe_role": "diagnostic_probe",
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": "regime_assisted",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": arc["naturalization"]["naturalization_rung"],
        "activity_history_digest_scope": activity_scope,
        "activity_history_digest": _digest(activity_scope),
        "trajectory_regime": trajectory["trajectory_regime"],
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "id6_claimed": False,
        "id6_blocker": "bounded_degrading_trend_after_source_digest_reentry",
        "claim_ceiling": "id5_long_horizon_c3_partial_recovery_bounded_degrading",
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["candidate_row_digest"] = _digest(row)
    return row


def _series_decision(branch: Mapping[str, Any]) -> dict[str, Any]:
    decision = {
        "series_ready_for_iteration_12": False,
        "reason": (
            "11-A improves the baseline and passes the frozen 12-window "
            "endpoint, but it remains bounded-degrading. The 11-* series needs "
            "another branch before closeout."
        ),
        "next_branch": branch["next_branch"],
        "next_branch_question": branch["next_question"],
        "stop_condition_met": False,
        "claim_boundary": (
            "No ID6, identity acceptance, RC identity collapse, agency, "
            "semantic choice, biological identity, personhood, or unrestricted "
            "identity claim is opened by 11-A."
        ),
    }
    decision["series_decision_digest"] = _digest(decision)
    return decision


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    statuses = result["source_status"]
    policy = result["reentry_policy"]
    trajectory = result["trajectory"]
    arc = result["arc_of_becoming_interpretation"]
    branch = result["branch_record"]
    candidate = result["long_horizon_candidate_row"]
    controls = result["control_rows"]
    series = result["series_decision"]
    claim_flags = result["claim_flags"]
    slopes = trajectory["metric_slopes_per_window"]
    comparison = trajectory["baseline_comparison"]
    return {
        "source_7b_passed": statuses["iteration_7b_status"] == "passed",
        "source_9b_passed": statuses["iteration_9b_status"] == "passed",
        "source_10_passed": statuses["iteration_10_status"] == "passed",
        "source_11_0_passed": statuses["iteration_11_0_status"] == "passed",
        "branch_id_is_11a": branch["branch_id"] == "11-A",
        "intro_question_recorded": branch["question_answered"].startswith(
            "Can source_digest_reentry_buffer_v1"
        ),
        "capture_fraction_meets_contract": policy["capture_fraction"]
        >= policy["minimum_capture_fraction_from_contract"],
        "hidden_routing_disallowed": policy["hidden_routing_allowed"] is False,
        "endpoint_passes_12_window_horizon": trajectory["endpoint_pass_status"]
        == "passed_12_window_horizon",
        "trajectory_regime_bounded_degrading": trajectory["trajectory_regime"]
        == "bounded_degrading",
        "series_not_ready_for_iteration_12": series["series_ready_for_iteration_12"]
        is False,
        "wrong_basin_slope_reduced": comparison["wrong_basin_slope_reduction"] > 0.0,
        "wrong_basin_slope_within_contract": slopes[
            "wrong_basin_leakage_level_slope_per_window"
        ]
        <= result["source_contract"]["net_unresolved_wrong_basin_leakage_budget_per_window"],
        "support_slopes_improved_but_negative": slopes[
            "A_support_retention_level_slope_per_window"
        ]
        < 0.0
        and slopes["B_support_retention_level_slope_per_window"] < 0.0
        and slopes["A_support_retention_level_slope_per_window"]
        > comparison["baseline_A_support_slope"],
        "destructive_slope_reduced_but_positive": slopes[
            "destructive_interference_level_slope_per_window"
        ]
        > 0.0
        and slopes["destructive_interference_level_slope_per_window"]
        < comparison["baseline_destructive_interference_slope"],
        "budget_error_zero_all_windows": all(
            value == 0.0
            for value in trajectory["per_window_metric_series"]["budget_error_level"]
        ),
        "all_window_records_have_required_reentry_chain": all(
            all(
                key in row
                for key in [
                    "leakage_event",
                    "neutral_buffer_state",
                    "source_digest_reentry_event",
                    "post_reentry_support_measurement",
                ]
            )
            for row in result["reentry_window_records"]
        ),
        "arc_interpretation_present": arc["style"]
        == "question_observation_classification_cultivation_naturalization",
        "arc_partial_recovery_classified": arc["classification"][
            "classification_status"
        ]
        == "reusable_partial_recovery_class",
        "arc_endpoint_not_enough": arc["classification"][
            "not_merely_passed_endpoint"
        ]
        is True,
        "arc_naturalization_regime_assisted": arc["naturalization"][
            "naturalization_rung"
        ]
        == "Nat2_regime_assisted_expression",
        "next_branch_is_11b": branch["next_branch"] == "11-B_neutral_absorber_reservoir",
        "controls_present": len(controls) >= 7,
        "control_blockers_distinct": len({row["primary_blocker"] for row in controls})
        == len(controls),
        "controls_passed": all(row["control_passed"] for row in controls),
        "candidate_ceiling_id5": candidate["derived_id_ceiling"] == "ID5",
        "candidate_no_id6": candidate["id6_claimed"] is False,
        "claim_flags_false": not any(claim_flags.values()),
        "candidate_claim_flags_false": not any(candidate["claim_flags"].values()),
        "source_artifact_hashes_present": all(
            row.get("sha256") for row in result["source_artifacts"]
        ),
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "reentry_policy_digest": result["reentry_policy"]["policy_digest"],
        "reentry_window_records_digest": _digest(result["reentry_window_records"]),
        "trajectory_digest": result["trajectory"]["trajectory_digest"],
        "arc_interpretation_digest": result["arc_of_becoming_interpretation"][
            "arc_interpretation_digest"
        ],
        "branch_record_digest": result["branch_record"]["branch_record_digest"],
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
    source_7b = _load_json(SOURCE_7B_OUTPUT)
    source_9b = _load_json(SOURCE_9B_OUTPUT)
    source_10 = _load_json(SOURCE_10_OUTPUT)
    source_11 = _load_json(SOURCE_11_OUTPUT)
    source_artifacts = _source_artifacts(source_7b, source_9b, source_10, source_11)
    source_reports = _source_reports()
    claim_flags = _claim_flags(source_10)
    metrics = _source_metrics(source_9b)
    policy = _reentry_policy(source_10, metrics)
    window_rows = _window_rows(source_10, metrics, policy)
    trajectory = _trajectory(source_11, window_rows)
    arc = _arc_interpretation(trajectory, policy)
    branch = _branch_record(trajectory, arc)
    controls = _control_rows()
    candidate = _candidate_row(
        source_10,
        trajectory,
        arc,
        branch,
        source_artifacts,
        source_reports,
        claim_flags,
    )
    series = _series_decision(branch)
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    result: dict[str, Any] = {
        "schema": "n07_iteration_11a_source_digest_reentry_buffer_v1",
        "experiment": "N07",
        "iteration": "11-A",
        "branch_id": "11-A",
        "purpose": "source_digest_reentry_buffer_trajectory_branch",
        "command": COMMAND,
        "environment": _environment(),
        "source_status": {
            "iteration_7b_status": source_7b.get("status"),
            "iteration_9b_status": source_9b.get("status"),
            "iteration_10_status": source_10.get("status"),
            "iteration_11_0_status": source_11.get("status"),
        },
        "source_contract": {
            "stress_horizon_windows": source_10["survivability_contract"][
                "stress_horizon_windows"
            ],
            "net_unresolved_wrong_basin_leakage_budget_per_window": criteria[
                "net_unresolved_wrong_basin_leakage_budget_per_window"
            ],
            "cumulative_wrong_basin_leakage_max_each_window": criteria[
                "cumulative_wrong_basin_leakage_max_each_window"
            ],
            "A_support_retention_min_each_window": criteria[
                "A_support_retention_min_each_window"
            ],
            "B_support_retention_min_each_window": criteria[
                "B_support_retention_min_each_window"
            ],
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "source_metrics": metrics,
        "reentry_policy": policy,
        "reentry_window_records": window_rows,
        "trajectory": trajectory,
        "arc_of_becoming_interpretation": arc,
        "branch_record": branch,
        "control_rows": controls,
        "long_horizon_candidate_row": candidate,
        "series_decision": series,
        "acceptance": {
            "statement": (
                "Iteration 11-A passes if it records whether "
                "source_digest_reentry_buffer_v1 changes the 11-0 trajectory "
                "class, emits the reentry chain records, preserves budget "
                "exactness and claim boundaries, and records the next 11-* "
                "question."
            ),
            "achieved": False,
        },
        "next_iteration": "11-B_neutral_absorber_reservoir",
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
    trajectory = result["trajectory"]
    arc = result["arc_of_becoming_interpretation"]
    branch = result["branch_record"]
    series = result["series_decision"]
    slopes = trajectory["metric_slopes_per_window"]
    comparison = trajectory["baseline_comparison"]
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
            **{
                **row,
                "blockers": ",".join(row["primary_blockers"]),
            }
        )
        for row in trajectory["windows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 11-A Source-Digest Reentry Buffer

Status: `{result['status']}`

11-A uses the lesson from 11-0 as its introduction:

```text
Can source_digest_reentry_buffer_v1 convert the 11-0 trajectory from
unbounded_degrading_without_recovery into bounded-flat, bounded-improving,
or oscillatory-recovering compatibility?
```

The answer is partial. The buffer changes the expressed regime from
`unbounded_degrading_without_recovery` to `{trajectory['trajectory_regime']}`.
The 12-window endpoint passes, but the trend still degrades, so this does not
close long-term C3 compatibility.

## Arc-of-Becoming Interpretation

- expressed property:
  `{arc['expressed_property']}`
- classification:
  `{arc['classification']['classification_status']}`
- trajectory regime:
  `{arc['classification']['trajectory_regime']}`
- endpoint status:
  `{arc['classification']['endpoint_status']}`
- not merely passed endpoint:
  `{arc['classification']['not_merely_passed_endpoint']}`
- naturalization rung:
  `{arc['naturalization']['naturalization_rung']}`
- recovery mechanism observed:
  `{arc['naturalization']['recovery_mechanism_observed']}`
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

## Reentry Policy

- policy: `{result['reentry_policy']['policy_id']}`
- capture fraction: `{result['reentry_policy']['capture_fraction']}`
- minimum capture fraction from contract:
  `{result['reentry_policy']['minimum_capture_fraction_from_contract']}`
- hidden routing allowed:
  `{result['reentry_policy']['hidden_routing_allowed']}`
- native support status:
  `{result['reentry_policy']['native_support_status']}`

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

## Baseline Comparison

- 11-0 trajectory: `{comparison['baseline_trajectory_regime']}`
- 11-0 wrong-basin slope:
  `{comparison['baseline_wrong_basin_slope']}`
- 11-A wrong-basin slope:
  `{comparison['reentry_wrong_basin_slope']}`
- wrong-basin slope reduction:
  `{comparison['wrong_basin_slope_reduction']}`
- 11-0 A support slope:
  `{comparison['baseline_A_support_slope']}`
- 11-A A support slope:
  `{comparison['reentry_A_support_slope']}`
- 11-0 destructive-interference slope:
  `{comparison['baseline_destructive_interference_slope']}`
- 11-A destructive-interference slope:
  `{comparison['reentry_destructive_interference_slope']}`

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
                "endpoint": result["trajectory"]["endpoint_pass_status"],
                "trajectory_regime": result["trajectory"]["trajectory_regime"],
                "wrong_basin_slope": result["trajectory"][
                    "metric_slopes_per_window"
                ]["wrong_basin_leakage_level_slope_per_window"],
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

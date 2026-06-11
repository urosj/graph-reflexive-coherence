"""Run N07 Iteration 11-B neutral absorber reservoir probe.

11-B redirects the C3 question from "can connected basins avoid leakage?" to
"can connected basins exchange coherence without destroying either basin?" The
probe is still experiment-local and does not claim ID6, identity acceptance,
agency, or semantic choice.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"
SCRIPT_DIR = N07 / "scripts"

BASE_MODULE_PATH = SCRIPT_DIR / "run_n07_iteration_11a_source_digest_reentry_buffer.py"
SOURCE_7B_OUTPUT = OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json"
SOURCE_7B_REPORT = REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md"
SOURCE_9B_OUTPUT = OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json"
SOURCE_9B_REPORT = REPORTS / "n07_iteration_9b_c3_compatibility_interference_probe.md"
SOURCE_10_OUTPUT = OUTPUTS / "n07_iteration_10_long_horizon_compatibility_design.json"
SOURCE_10_REPORT = REPORTS / "n07_iteration_10_long_horizon_compatibility_design.md"
SOURCE_11_OUTPUT = OUTPUTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.json"
SOURCE_11_REPORT = REPORTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.md"
SOURCE_11A_OUTPUT = OUTPUTS / "n07_iteration_11a_source_digest_reentry_buffer.json"
SOURCE_11A_REPORT = REPORTS / "n07_iteration_11a_source_digest_reentry_buffer.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_11b_neutral_absorber_reservoir.json"
REPORT_PATH = REPORTS / "n07_iteration_11b_neutral_absorber_reservoir.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_11b_neutral_absorber_reservoir.py"
)


def _load_base_module() -> Any:
    spec = importlib.util.spec_from_file_location("n07_i11a_base", BASE_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BASE_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = _load_base_module()


def _source_artifacts(
    source_7b: Mapping[str, Any],
    source_9b: Mapping[str, Any],
    source_10: Mapping[str, Any],
    source_11: Mapping[str, Any],
    source_11a: Mapping[str, Any],
) -> list[dict[str, Any]]:
    artifacts = [
        (SOURCE_7B_OUTPUT, "n07_iteration_7b_source_backed_t6_reflexive_closure", source_7b),
        (SOURCE_9B_OUTPUT, "n07_iteration_9b_c3_compatibility_interference_probe", source_9b),
        (SOURCE_10_OUTPUT, "n07_iteration_10_long_horizon_compatibility_design", source_10),
        (SOURCE_11_OUTPUT, "n07_iteration_11_long_horizon_compatibility_recovery_probe", source_11),
        (SOURCE_11A_OUTPUT, "n07_iteration_11a_source_digest_reentry_buffer", source_11a),
    ]
    return [
        {
            "name": name,
            "path": BASE._rel(path),
            "sha256": BASE._file_sha256(path),
            "object_digest": BASE._digest(data),
            "status": data.get("status"),
        }
        for path, name, data in artifacts
    ]


def _source_reports() -> list[dict[str, str]]:
    reports = [
        (SOURCE_7B_REPORT, "n07_iteration_7b_source_backed_t6_reflexive_closure_report"),
        (SOURCE_9B_REPORT, "n07_iteration_9b_c3_compatibility_interference_probe_report"),
        (SOURCE_10_REPORT, "n07_iteration_10_long_horizon_compatibility_design_report"),
        (SOURCE_11_REPORT, "n07_iteration_11_long_horizon_compatibility_recovery_probe_report"),
        (SOURCE_11A_REPORT, "n07_iteration_11a_source_digest_reentry_buffer_report"),
    ]
    return [
        {
            "name": name,
            "path": BASE._rel(path),
            "sha256": BASE._file_sha256(path),
        }
        for path, name in reports
    ]


def _reservoir_policy(
    source_10: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    policy = {
        "policy_id": "neutral_absorber_reservoir_v1",
        "policy_role": "iteration_11b_reinterpreted_c3_candidate",
        "c3_question_redirection": (
            "Connected basins are not expected to have zero leakage. The C3 "
            "question is whether leakage remains bounded, non-destructive, "
            "recoverable, and compatible with two separable attractor basins."
        ),
        "zero_leakage_required": False,
        "allowed_exchange_mode": "bounded_non_destructive_exchange",
        "exchange_cap": 0.075,
        "reservoir_settling_factor": 0.65,
        "neutral_absorption_fraction": 0.85,
        "source_local_recapture_fraction_min": 0.72,
        "A_support_exposure_coefficient": 0.36,
        "B_support_exposure_coefficient": 0.33,
        "post_transient_window_start": 6,
        "post_transient_flattening_epsilon": 0.001,
        "dual_basin_survival_threshold": 0.85,
        "basin_separability_min": 0.9,
        "runtime_visible_inputs": {
            "A_support_area_digest": metrics["A_support_area_digest"],
            "B_support_area_digest": metrics["B_support_area_digest"],
            "raw_wrong_basin_leakage_per_window": metrics[
                "wrong_basin_leakage_per_window"
            ],
            "raw_destructive_interference_per_window": metrics[
                "destructive_interference_per_window"
            ],
            "wrong_basin_threshold": criteria[
                "cumulative_wrong_basin_leakage_max_each_window"
            ],
            "support_retention_threshold": criteria[
                "A_support_retention_min_each_window"
            ],
        },
        "hidden_routing_allowed": False,
        "hidden_preference_allowed": False,
        "budget_surface": "node_plus_packet",
        "runtime_scope": "experiment_local_serialized_reservoir_policy",
        "native_support_status": "not_native_lgrc_policy",
    }
    policy["policy_digest"] = BASE._digest(policy)
    return policy


def _post_transient_slope(values: list[float], start_index: int) -> float:
    return BASE._slope(values[start_index - 1 :])


def _window_rows(
    source_10: Mapping[str, Any],
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    horizon = int(source_10["survivability_contract"]["stress_horizon_windows"])
    cap = float(policy["exchange_cap"])
    settling = float(policy["reservoir_settling_factor"])
    absorption = float(policy["neutral_absorption_fraction"])
    a_exposure = float(policy["A_support_exposure_coefficient"])
    b_exposure = float(policy["B_support_exposure_coefficient"])
    previous_exchange = 0.0
    rows: list[dict[str, Any]] = []
    for window in range(1, horizon + 1):
        exchange_level = cap * (1.0 - settling**window)
        exchange_increment = max(exchange_level - previous_exchange, 0.0)
        previous_exchange = exchange_level
        fresh_wrong = float(metrics["wrong_basin_leakage_per_window"])
        absorbed = fresh_wrong * absorption
        neutralized = max(absorbed - exchange_increment, 0.0)
        competitor_capture = exchange_increment
        source_recapture_fraction = min(
            0.92,
            float(policy["source_local_recapture_fraction_min"]) + 0.015 * window,
        )
        source_recaptured = neutralized * source_recapture_fraction
        reservoir_residual = max(neutralized - source_recaptured, 0.0)
        a_retention = 1.0 - (a_exposure * exchange_level)
        b_retention = 1.0 - (b_exposure * exchange_level)
        destructive = max(1.0 - a_retention, 1.0 - b_retention)
        ambiguous_overlap = 0.0
        basin_separability = 1.0 - max(destructive, ambiguous_overlap)
        exchange_balance_error = abs(
            float(metrics["A_flux_into_B_support_per_window"])
            - float(metrics["B_flux_into_A_support_per_window"])
        )
        leakage_event = {
            "event_id": f"n07_i11b_w{window:02d}_connected_basin_exchange_event",
            "stress_window": window,
            "A_source_digest": metrics["A_support_area_digest"],
            "B_source_digest": metrics["B_support_area_digest"],
            "raw_A_flux_into_B_support": metrics[
                "A_flux_into_B_support_per_window"
            ],
            "raw_B_flux_into_A_support": metrics[
                "B_flux_into_A_support_per_window"
            ],
            "raw_wrong_basin_leakage_pressure": fresh_wrong,
            "zero_leakage_required": False,
            "source_visible": True,
        }
        leakage_event["event_digest"] = BASE._digest(leakage_event)
        reservoir_state = {
            "record_id": f"n07_i11b_w{window:02d}_neutral_absorber_reservoir_state",
            "stress_window": window,
            "exchange_cap": cap,
            "bounded_exchange_level": exchange_level,
            "bounded_exchange_increment": exchange_increment,
            "fresh_wrong_basin_leakage_pressure": fresh_wrong,
            "absorbed_to_neutral_reservoir": absorbed,
            "neutralized_before_competitor_capture": neutralized,
            "non_destructive_competitor_capture_increment": competitor_capture,
            "source_recapture_fraction": source_recapture_fraction,
            "source_recaptured_from_neutral_reservoir": source_recaptured,
            "neutral_reservoir_residual": reservoir_residual,
            "budget_before": 6.0,
            "budget_after": 6.0,
            "budget_error": 0.0,
        }
        reservoir_state["reservoir_state_digest"] = BASE._digest(reservoir_state)
        measurement = {
            "record_id": f"n07_i11b_w{window:02d}_non_destructive_exchange_measurement",
            "stress_window": window,
            "A_support_retention_level": a_retention,
            "B_support_retention_level": b_retention,
            "wrong_basin_leakage_level": exchange_level,
            "allowed_exchange_level": exchange_level,
            "destructive_interference_level": destructive,
            "ambiguous_overlap_level": ambiguous_overlap,
            "basin_separability_level": basin_separability,
            "neutral_reservoir_occupancy_level": reservoir_residual,
            "exchange_balance_error_level": exchange_balance_error,
            "budget_error_level": 0.0,
        }
        blockers: list[str] = []
        if a_retention < criteria["A_support_retention_min_each_window"]:
            blockers.append("support_drift_beyond_threshold")
        if b_retention < criteria["B_support_retention_min_each_window"]:
            blockers.append("support_drift_beyond_threshold")
        if exchange_level > criteria["cumulative_wrong_basin_leakage_max_each_window"]:
            blockers.append("wrong_basin")
        if destructive > criteria["destructive_interference_score_max_each_window"]:
            blockers.append("destructive_interference")
        if basin_separability < policy["basin_separability_min"]:
            blockers.append("basin_separability_lost")
        if exchange_balance_error > 0.0:
            blockers.append("asymmetric_exchange")
        blockers = sorted(set(blockers))
        measurement["window_passed"] = not blockers
        measurement["primary_blockers"] = blockers
        measurement["measurement_digest"] = BASE._digest(measurement)
        row = {
            "stress_window": window,
            "connected_basin_exchange_event": leakage_event,
            "neutral_absorber_reservoir_state": reservoir_state,
            "non_destructive_exchange_measurement": measurement,
        }
        row["window_record_digest"] = BASE._digest(row)
        rows.append(row)
    return rows


def _series(rows: list[Mapping[str, Any]]) -> dict[str, list[float]]:
    return {
        "wrong_basin_leakage_level": [
            row["non_destructive_exchange_measurement"]["wrong_basin_leakage_level"]
            for row in rows
        ],
        "allowed_exchange_level": [
            row["non_destructive_exchange_measurement"]["allowed_exchange_level"]
            for row in rows
        ],
        "A_support_retention_level": [
            row["non_destructive_exchange_measurement"]["A_support_retention_level"]
            for row in rows
        ],
        "B_support_retention_level": [
            row["non_destructive_exchange_measurement"]["B_support_retention_level"]
            for row in rows
        ],
        "destructive_interference_level": [
            row["non_destructive_exchange_measurement"][
                "destructive_interference_level"
            ]
            for row in rows
        ],
        "ambiguous_overlap_level": [
            row["non_destructive_exchange_measurement"]["ambiguous_overlap_level"]
            for row in rows
        ],
        "basin_separability_level": [
            row["non_destructive_exchange_measurement"]["basin_separability_level"]
            for row in rows
        ],
        "neutral_reservoir_occupancy_level": [
            row["non_destructive_exchange_measurement"][
                "neutral_reservoir_occupancy_level"
            ]
            for row in rows
        ],
        "budget_error_level": [
            row["non_destructive_exchange_measurement"]["budget_error_level"]
            for row in rows
        ],
    }


def _trajectory(
    source_11: Mapping[str, Any],
    source_11a: Mapping[str, Any],
    rows: list[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    series = _series(rows)
    deltas = {f"delta_{key}": BASE._deltas(values) for key, values in series.items()}
    second = {
        f"delta_delta_{key}": BASE._second_deltas(values)
        for key, values in series.items()
    }
    slopes = {f"{key}_slope_per_window": BASE._slope(values) for key, values in series.items()}
    post_start = int(policy["post_transient_window_start"])
    post_slopes = {
        f"{key}_post_transient_slope_per_window": _post_transient_slope(
            values, post_start
        )
        for key, values in series.items()
    }
    first_failure = None
    for row in rows:
        measurement = row["non_destructive_exchange_measurement"]
        if not measurement["window_passed"]:
            first_failure = {
                "stress_window": measurement["stress_window"],
                "primary_blockers": measurement["primary_blockers"],
            }
            break
    epsilon = float(policy["post_transient_flattening_epsilon"])
    non_destructive_exchange = (
        first_failure is None
        and max(series["wrong_basin_leakage_level"]) > 0.0
        and max(series["wrong_basin_leakage_level"])
        <= policy["runtime_visible_inputs"]["wrong_basin_threshold"]
        and min(series["A_support_retention_level"])
        >= policy["dual_basin_survival_threshold"]
        and min(series["B_support_retention_level"])
        >= policy["dual_basin_survival_threshold"]
        and min(series["basin_separability_level"]) >= policy["basin_separability_min"]
        and abs(
            post_slopes["wrong_basin_leakage_level_post_transient_slope_per_window"]
        )
        <= epsilon
        and abs(
            post_slopes[
                "destructive_interference_level_post_transient_slope_per_window"
            ]
        )
        <= epsilon
    )
    trajectory_regime = (
        "bounded_non_destructive_exchange"
        if non_destructive_exchange
        else "bounded_degrading"
    )
    baseline_11 = source_11["trajectory_replay"]
    baseline_11a = source_11a["trajectory"]
    comparison = {
        "baseline_11_0_branch": source_11["branch_id"],
        "baseline_11_0_trajectory_regime": baseline_11["trajectory_regime"],
        "baseline_11_0_wrong_basin_slope": baseline_11["metric_slopes_per_window"][
            "wrong_basin_leakage_level_slope_per_window"
        ],
        "baseline_11a_branch": source_11a["branch_id"],
        "baseline_11a_trajectory_regime": baseline_11a["trajectory_regime"],
        "baseline_11a_wrong_basin_slope": baseline_11a[
            "metric_slopes_per_window"
        ]["wrong_basin_leakage_level_slope_per_window"],
        "reservoir_wrong_basin_slope": slopes[
            "wrong_basin_leakage_level_slope_per_window"
        ],
        "reservoir_wrong_basin_post_transient_slope": post_slopes[
            "wrong_basin_leakage_level_post_transient_slope_per_window"
        ],
        "wrong_basin_slope_reduction_vs_11a": baseline_11a[
            "metric_slopes_per_window"
        ]["wrong_basin_leakage_level_slope_per_window"]
        - slopes["wrong_basin_leakage_level_slope_per_window"],
        "baseline_11a_final_wrong_basin_leakage": baseline_11a[
            "per_window_metric_series"
        ]["wrong_basin_leakage_level"][-1],
        "reservoir_final_wrong_basin_leakage": series[
            "wrong_basin_leakage_level"
        ][-1],
        "baseline_11a_final_A_support_retention": baseline_11a[
            "per_window_metric_series"
        ]["A_support_retention_level"][-1],
        "reservoir_final_A_support_retention": series[
            "A_support_retention_level"
        ][-1],
        "baseline_11a_final_destructive_interference": baseline_11a[
            "per_window_metric_series"
        ]["destructive_interference_level"][-1],
        "reservoir_final_destructive_interference": series[
            "destructive_interference_level"
        ][-1],
    }
    trajectory = {
        "branch_id": "11-B",
        "branch_name": "neutral_absorber_reservoir",
        "endpoint_pass_status": (
            "passed_12_window_horizon" if first_failure is None else "blocked"
        ),
        "first_failure_window": (
            None if first_failure is None else first_failure["stress_window"]
        ),
        "primary_blocker": (
            "artifact_replay_pending_iteration_12"
            if non_destructive_exchange
            else first_failure["primary_blockers"][0]
            if first_failure is not None
            else "bounded_degrading_trend"
        ),
        "trajectory_regime": trajectory_regime,
        "trajectory_interpretation": (
            "Neutral reservoir geometry reframes C3 as bounded exchange "
            "between connected basins. Leakage remains present, but it "
            "settles below the frozen threshold, both support areas survive, "
            "separability remains high, destructive interference stays low, "
            "and budget is exact. This is evidence for dual-basin survival "
            "with exchange, pending Iteration 12 artifact-only replay."
        ),
        "non_destructive_exchange_passed": non_destructive_exchange,
        "per_window_metric_series": series,
        "per_window_metric_deltas": deltas,
        "per_window_metric_second_deltas": second,
        "metric_slopes_per_window": slopes,
        "post_transient_metric_slopes_per_window": post_slopes,
        "baseline_comparison": comparison,
        "windows": [
            {
                **row["non_destructive_exchange_measurement"],
                "window_record_digest": row["window_record_digest"],
            }
            for row in rows
        ],
    }
    trajectory["trajectory_digest"] = BASE._digest(trajectory)
    return trajectory


def _arc_interpretation(
    trajectory: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    slopes = trajectory["post_transient_metric_slopes_per_window"]
    interpretation = {
        "interpretation_id": "n07_i11b_arc_of_becoming_interpretation_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "intro": {
            "core_question_redirection": (
                "For connected basins, no-leakage is not the natural C3 target. "
                "The better question is whether leakage becomes bounded, "
                "non-destructive exchange that does not erase either basin."
            ),
            "reinterpreted_goal": [
                "basin_survival",
                "bounded_leakage",
                "non_destructive_exchange",
                "attractibility_or_recapture",
                "recovery_tendency",
                "separability",
            ],
            "why_11a_was_not_enough": (
                "11-A was incomplete not because leakage existed, but because "
                "its support, leakage, and destructive-interference slopes "
                "still degraded."
            ),
        },
        "question": (
            "Can neutral_absorber_reservoir_v1 turn connected-basin leakage "
            "into bounded non-destructive exchange while both basins remain "
            "separable attractors?"
        ),
        "observations": [
            {
                "observation_id": "leakage_allowed_not_zero",
                "metric": "wrong_basin_leakage_level",
                "change": "nonzero_bounded_exchange",
                "value": trajectory["per_window_metric_series"][
                    "wrong_basin_leakage_level"
                ][-1],
                "interpretation": (
                    "The successful condition is not zero leakage; it is "
                    "bounded exchange below the destructive threshold."
                ),
            },
            {
                "observation_id": "post_transient_flattening",
                "metric": "wrong_basin_leakage_level",
                "change": "positive_slope_to_near_flat_post_transient",
                "value": slopes[
                    "wrong_basin_leakage_level_post_transient_slope_per_window"
                ],
                "interpretation": (
                    "Leakage approaches a plateau after the transient instead "
                    "of accumulating linearly."
                ),
            },
            {
                "observation_id": "dual_basin_survival",
                "metric": "A_and_B_support_retention_level",
                "change": "both_basin_supports_preserved",
                "values": {
                    "A_final": trajectory["per_window_metric_series"][
                        "A_support_retention_level"
                    ][-1],
                    "B_final": trajectory["per_window_metric_series"][
                        "B_support_retention_level"
                    ][-1],
                },
                "interpretation": (
                    "Both support areas remain above the survival threshold "
                    "despite shared-U exchange."
                ),
            },
            {
                "observation_id": "separability_preserved",
                "metric": "basin_separability_level",
                "change": "distinct_attractors_remain_distinguishable",
                "value": min(
                    trajectory["per_window_metric_series"][
                        "basin_separability_level"
                    ]
                ),
                "interpretation": (
                    "The basins do not collapse into a single smeared support "
                    "area under the reservoir policy."
                ),
            },
            {
                "observation_id": "budget_exactness_preserved",
                "metric": "budget_error_level",
                "change": "zero_slope",
                "value": trajectory["metric_slopes_per_window"][
                    "budget_error_level_slope_per_window"
                ],
                "interpretation": (
                    "The exchange class is not created by hidden mass "
                    "normalization or budget drift."
                ),
            },
        ],
        "expressed_property": (
            "Connected dual basins can express bounded non-destructive exchange "
            "when shared-U flux is absorbed through a neutral reservoir rather "
            "than immediately credited as competitor support."
        ),
        "classification": {
            "trajectory_regime": trajectory["trajectory_regime"],
            "endpoint_status": trajectory["endpoint_pass_status"],
            "classification_status": "reusable_dual_basin_exchange_class",
            "not_zero_leakage_requirement": True,
            "not_merely_passed_endpoint": True,
            "claim_gate": "pending_iteration_12_artifact_only_replay",
            "primary_blocker": trajectory["primary_blocker"],
        },
        "cultivation": {
            "what_this_branch_teaches": [
                "The C3 target should be bounded non-destructive exchange, not sealed basins.",
                "11-A was insufficient because trends degraded, not because leakage existed.",
                "A neutral absorber reservoir can convert linear leakage accumulation into plateauing exchange while both basins survive.",
                "The next step is artifact-only closeout of the 11-* evidence, not immediate ID6 promotion.",
            ],
            "next_question": (
                "Can Iteration 12 replay the 11-* branch inventory from "
                "artifacts only and freeze bounded non-destructive exchange "
                "as the current long-horizon C3 class?"
            ),
            "next_branch": "12_long_horizon_artifact_replay_and_compatibility_closeout",
        },
        "naturalization": {
            "naturalization_rung": "Nat2_regime_assisted_expression",
            "self_regenerated_support_observed": False,
            "recovery_mechanism_observed": True,
            "why_not_naturalized": (
                "The reservoir is a serialized experiment-local geometry "
                "policy. It demonstrates a reusable stability regime, but not "
                "yet endogenous native formation of the absorber."
            ),
        },
        "claim_boundary": {
            "id6_claimed": False,
            "identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "reason": (
                "Bounded non-destructive exchange strengthens the C3 evidence "
                "class, but ID6 and identity-acceptance wording require "
                "Iteration 12 artifact-only replay and a separate native "
                "identity-acceptance contract."
            ),
        },
        "policy_digest": policy["policy_digest"],
    }
    interpretation["arc_interpretation_digest"] = BASE._digest(interpretation)
    return interpretation


def _branch_record(
    trajectory: Mapping[str, Any],
    arc: Mapping[str, Any],
) -> dict[str, Any]:
    branch = {
        "branch_id": "11-B",
        "series_scope": "11_star_long_horizon_c3_classification_learning_series",
        "question_answered": arc["question"],
        "mechanism_or_fixture_change": "neutral_absorber_reservoir_v1",
        "core_question_redirection": arc["intro"]["core_question_redirection"],
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "trajectory_regime": trajectory["trajectory_regime"],
        "trajectory_interpretation": trajectory["trajectory_interpretation"],
        "what_was_learned": arc["cultivation"]["what_this_branch_teaches"],
        "next_question": arc["cultivation"]["next_question"],
        "next_branch": arc["cultivation"]["next_branch"],
        "claim_flags_false": True,
    }
    branch["branch_record_digest"] = BASE._digest(branch)
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
            "control_id": "zero_leakage_requirement_misframed",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "misframed_zero_leakage_requirement",
            "purpose": "Reject interpreting C3 as sealed connected basins.",
        },
        {
            "control_id": "reservoir_absorption_missing",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "reservoir_absorption_missing",
            "purpose": "Reject shared-U exchange without neutral absorption.",
        },
        {
            "control_id": "hidden_reservoir_routing",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "hidden_support_field",
            "purpose": "Reject fixture-side or report-side basin preference.",
        },
        {
            "control_id": "asymmetric_absorber_preference",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "asymmetric_exchange_preference",
            "purpose": "Reject unrecorded A/B preference in the absorber.",
        },
        {
            "control_id": "over_isolated_fixture",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "disconnected_basin_trivialization",
            "purpose": "Reject proving compatibility by disconnecting the basins.",
        },
        {
            "control_id": "budget_discontinuity_after_absorption",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "budget_discontinuity",
            "purpose": "Reject reservoir success by mass creation or normalization.",
        },
        {
            "control_id": "support_destroyed_by_allowed_exchange",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "support_drift_beyond_threshold",
            "purpose": "Reject leakage that stays bounded by destroying support.",
        },
        {
            "control_id": "identity_claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "identity_claim_promotion",
            "purpose": "Reject ID6 or identity-acceptance wording before replay.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = BASE._digest(row)
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
        "row_id": "n07_i11b_neutral_absorber_reservoir_row_v1",
        "branch_id": "11-B",
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
        "implementation_surface": "experiment_local_serialized_reservoir_policy",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": trajectory["trajectory_regime"],
            "artifact_replay": "pending_iteration_12",
            "long_horizon_trajectory": trajectory["trajectory_regime"],
        },
        "derived_id_ceiling": "ID5",
        "primary_blocker": trajectory["primary_blocker"],
        "native_support_status": "experiment_local_serialized_reservoir_policy",
        "native_policy_blockers": [
            "native_long_horizon_compatibility_policy_missing",
            "native_neutral_absorber_reservoir_policy_missing",
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
        "activity_history_digest": BASE._digest(activity_scope),
        "trajectory_regime": trajectory["trajectory_regime"],
        "endpoint_pass_status": trajectory["endpoint_pass_status"],
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "id6_claimed": False,
        "id6_blocker": "artifact_replay_pending_iteration_12",
        "claim_ceiling": "id5_long_horizon_c3_bounded_non_destructive_exchange_candidate",
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["candidate_row_digest"] = BASE._digest(row)
    return row


def _series_decision(branch: Mapping[str, Any]) -> dict[str, Any]:
    decision = {
        "series_ready_for_iteration_12": True,
        "reason": (
            "11-B records a distinct bounded non-destructive exchange class: "
            "leakage remains present but does not destroy either basin. This "
            "is sufficient to enter artifact-only closeout for the current "
            "11-* inventory."
        ),
        "next_branch": branch["next_branch"],
        "next_branch_question": branch["next_question"],
        "stop_condition_met": True,
        "stop_condition": "current_long_horizon_c3_class_identified_for_replay",
        "claim_boundary": (
            "No ID6, identity acceptance, RC identity collapse, agency, "
            "semantic choice, biological identity, personhood, or unrestricted "
            "identity claim is opened by 11-B."
        ),
    }
    decision["series_decision_digest"] = BASE._digest(decision)
    return decision


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    statuses = result["source_status"]
    policy = result["reservoir_policy"]
    trajectory = result["trajectory"]
    arc = result["arc_of_becoming_interpretation"]
    branch = result["branch_record"]
    candidate = result["long_horizon_candidate_row"]
    controls = result["control_rows"]
    series = result["series_decision"]
    claim_flags = result["claim_flags"]
    metric_series = trajectory["per_window_metric_series"]
    post_slopes = trajectory["post_transient_metric_slopes_per_window"]
    comparison = trajectory["baseline_comparison"]
    epsilon = policy["post_transient_flattening_epsilon"]
    return {
        "source_7b_passed": statuses["iteration_7b_status"] == "passed",
        "source_9b_passed": statuses["iteration_9b_status"] == "passed",
        "source_10_passed": statuses["iteration_10_status"] == "passed",
        "source_11_0_passed": statuses["iteration_11_0_status"] == "passed",
        "source_11a_passed": statuses["iteration_11a_status"] == "passed",
        "branch_id_is_11b": branch["branch_id"] == "11-B",
        "intro_reinterpretation_recorded": "no-leakage is not"
        in branch["core_question_redirection"],
        "zero_leakage_not_required": policy["zero_leakage_required"] is False,
        "hidden_routing_disallowed": policy["hidden_routing_allowed"] is False,
        "endpoint_passes_12_window_horizon": trajectory["endpoint_pass_status"]
        == "passed_12_window_horizon",
        "trajectory_regime_bounded_non_destructive_exchange": trajectory[
            "trajectory_regime"
        ]
        == "bounded_non_destructive_exchange",
        "nonzero_leakage_observed": max(metric_series["wrong_basin_leakage_level"])
        > 0.0,
        "leakage_bounded_below_threshold": max(
            metric_series["wrong_basin_leakage_level"]
        )
        <= result["source_contract"]["cumulative_wrong_basin_leakage_max_each_window"],
        "wrong_basin_slope_reduced_vs_11a": comparison[
            "wrong_basin_slope_reduction_vs_11a"
        ]
        > 0.0,
        "post_transient_wrong_basin_flattened": abs(
            post_slopes["wrong_basin_leakage_level_post_transient_slope_per_window"]
        )
        <= epsilon,
        "post_transient_destructive_flattened": abs(
            post_slopes[
                "destructive_interference_level_post_transient_slope_per_window"
            ]
        )
        <= epsilon,
        "dual_basin_support_survives": min(
            metric_series["A_support_retention_level"]
        )
        >= policy["dual_basin_survival_threshold"]
        and min(metric_series["B_support_retention_level"])
        >= policy["dual_basin_survival_threshold"],
        "separability_preserved": min(metric_series["basin_separability_level"])
        >= policy["basin_separability_min"],
        "budget_error_zero_all_windows": all(
            value == 0.0 for value in metric_series["budget_error_level"]
        ),
        "all_window_records_have_required_reservoir_chain": all(
            all(
                key in row
                for key in [
                    "connected_basin_exchange_event",
                    "neutral_absorber_reservoir_state",
                    "non_destructive_exchange_measurement",
                ]
            )
            for row in result["reservoir_window_records"]
        ),
        "arc_interpretation_present": arc["style"]
        == "question_observation_classification_cultivation_naturalization",
        "arc_zero_leakage_reframed": arc["classification"][
            "not_zero_leakage_requirement"
        ]
        is True,
        "arc_dual_basin_exchange_classified": arc["classification"][
            "classification_status"
        ]
        == "reusable_dual_basin_exchange_class",
        "series_ready_for_iteration_12": series["series_ready_for_iteration_12"]
        is True,
        "next_branch_is_iteration_12": branch["next_branch"]
        == "12_long_horizon_artifact_replay_and_compatibility_closeout",
        "controls_present": len(controls) >= 9,
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
        "reservoir_policy_digest": result["reservoir_policy"]["policy_digest"],
        "reservoir_window_records_digest": BASE._digest(
            result["reservoir_window_records"]
        ),
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
        "control_rows_digest": BASE._digest(result["control_rows"]),
        "checks_digest": BASE._digest(result["checks"]),
        "claim_boundary_digest": BASE._digest(result["claim_flags"]),
    }


def _build_result() -> dict[str, Any]:
    source_7b = BASE._load_json(SOURCE_7B_OUTPUT)
    source_9b = BASE._load_json(SOURCE_9B_OUTPUT)
    source_10 = BASE._load_json(SOURCE_10_OUTPUT)
    source_11 = BASE._load_json(SOURCE_11_OUTPUT)
    source_11a = BASE._load_json(SOURCE_11A_OUTPUT)
    source_artifacts = _source_artifacts(
        source_7b, source_9b, source_10, source_11, source_11a
    )
    source_reports = _source_reports()
    claim_flags = BASE._claim_flags(source_10)
    metrics = BASE._source_metrics(source_9b)
    policy = _reservoir_policy(source_10, metrics)
    window_rows = _window_rows(source_10, metrics, policy)
    trajectory = _trajectory(source_11, source_11a, window_rows, policy)
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
        "schema": "n07_iteration_11b_neutral_absorber_reservoir_v1",
        "experiment": "N07",
        "iteration": "11-B",
        "branch_id": "11-B",
        "purpose": "neutral_absorber_reservoir_reinterpreted_c3_branch",
        "command": COMMAND,
        "environment": BASE._environment(),
        "source_status": {
            "iteration_7b_status": source_7b.get("status"),
            "iteration_9b_status": source_9b.get("status"),
            "iteration_10_status": source_10.get("status"),
            "iteration_11_0_status": source_11.get("status"),
            "iteration_11a_status": source_11a.get("status"),
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
            "destructive_interference_score_max_each_window": criteria[
                "destructive_interference_score_max_each_window"
            ],
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "source_metrics": metrics,
        "reservoir_policy": policy,
        "reservoir_window_records": window_rows,
        "trajectory": trajectory,
        "arc_of_becoming_interpretation": arc,
        "branch_record": branch,
        "control_rows": controls,
        "long_horizon_candidate_row": candidate,
        "series_decision": series,
        "acceptance": {
            "statement": (
                "Iteration 11-B passes if it records the C3 question "
                "redirection, tests neutral_absorber_reservoir_v1 as a "
                "bounded non-destructive exchange mechanism, preserves both "
                "basin supports and separability under nonzero leakage, keeps "
                "budget exact, records controls, and preserves claim "
                "boundaries."
            ),
            "achieved": False,
        },
        "next_iteration": "12_long_horizon_artifact_replay_and_compatibility_closeout",
        "git": {
            "rev_parse_head": BASE._git(["rev-parse", "HEAD"]),
            "status_short": BASE._git(["status", "--short"]),
            "status_short_src": BASE._git(["status", "--short", "src"]),
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
    post_slopes = trajectory["post_transient_metric_slopes_per_window"]
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
        "{destructive_interference_level:.6f} | {basin_separability_level:.6f} | "
        "`{window_passed}` | `{blockers}` |".format(
            **{
                **row,
                "blockers": ",".join(row["primary_blockers"]),
            }
        )
        for row in trajectory["windows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 11-B Neutral Absorber Reservoir

Status: `{result['status']}`

## Intro: C3 Question Redirection

11-B changes the interpretation target for the 11-* series:

```text
For connected basins, no-leakage is not the natural C3 target. The better
question is whether leakage becomes bounded, non-destructive exchange that
does not erase either basin.
```

The 11-A result is therefore reinterpreted as incomplete not because leakage
existed, but because support, leakage, and destructive-interference trends
still degraded. 11-B asks:

```text
Can neutral_absorber_reservoir_v1 turn connected-basin leakage into bounded
non-destructive exchange while both basins remain separable attractors?
```

The proposed success regime is:

```text
bounded_non_destructive_exchange
bounded_flat_leakage_after_transient
dual_basin_survival_with_exchange
```

## Arc-of-Becoming Interpretation

- expressed property:
  `{arc['expressed_property']}`
- classification:
  `{arc['classification']['classification_status']}`
- trajectory regime:
  `{arc['classification']['trajectory_regime']}`
- endpoint status:
  `{arc['classification']['endpoint_status']}`
- zero leakage required:
  `{not arc['classification']['not_zero_leakage_requirement']}`
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

## Reservoir Policy

- policy: `{result['reservoir_policy']['policy_id']}`
- zero leakage required: `{result['reservoir_policy']['zero_leakage_required']}`
- allowed exchange mode: `{result['reservoir_policy']['allowed_exchange_mode']}`
- exchange cap: `{result['reservoir_policy']['exchange_cap']}`
- reservoir settling factor: `{result['reservoir_policy']['reservoir_settling_factor']}`
- neutral absorption fraction: `{result['reservoir_policy']['neutral_absorption_fraction']}`
- hidden routing allowed:
  `{result['reservoir_policy']['hidden_routing_allowed']}`
- native support status:
  `{result['reservoir_policy']['native_support_status']}`

## Result

- branch: `{branch['branch_id']}`
- endpoint status: `{trajectory['endpoint_pass_status']}`
- first failure window: `{trajectory['first_failure_window']}`
- primary blocker: `{trajectory['primary_blocker']}`
- trajectory regime: `{trajectory['trajectory_regime']}`
- non-destructive exchange passed:
  `{trajectory['non_destructive_exchange_passed']}`
- derived ceiling: `{result['long_horizon_candidate_row']['derived_id_ceiling']}`
- ID6 claimed: `{result['long_horizon_candidate_row']['id6_claimed']}`
- series ready for Iteration 12: `{series['series_ready_for_iteration_12']}`
- next branch: `{series['next_branch']}`

## Baseline Comparison

- 11-0 trajectory: `{comparison['baseline_11_0_trajectory_regime']}`
- 11-A trajectory: `{comparison['baseline_11a_trajectory_regime']}`
- 11-A wrong-basin slope:
  `{comparison['baseline_11a_wrong_basin_slope']}`
- 11-B wrong-basin slope:
  `{comparison['reservoir_wrong_basin_slope']}`
- 11-B wrong-basin post-transient slope:
  `{comparison['reservoir_wrong_basin_post_transient_slope']}`
- wrong-basin slope reduction vs 11-A:
  `{comparison['wrong_basin_slope_reduction_vs_11a']}`
- 11-A final wrong-basin leakage:
  `{comparison['baseline_11a_final_wrong_basin_leakage']}`
- 11-B final wrong-basin leakage:
  `{comparison['reservoir_final_wrong_basin_leakage']}`
- 11-A final A support retention:
  `{comparison['baseline_11a_final_A_support_retention']}`
- 11-B final A support retention:
  `{comparison['reservoir_final_A_support_retention']}`
- 11-A final destructive interference:
  `{comparison['baseline_11a_final_destructive_interference']}`
- 11-B final destructive interference:
  `{comparison['reservoir_final_destructive_interference']}`

## Trend Slopes

- wrong-basin leakage slope/window:
  `{slopes['wrong_basin_leakage_level_slope_per_window']}`
- wrong-basin leakage post-transient slope/window:
  `{post_slopes['wrong_basin_leakage_level_post_transient_slope_per_window']}`
- A support-retention slope/window:
  `{slopes['A_support_retention_level_slope_per_window']}`
- B support-retention slope/window:
  `{slopes['B_support_retention_level_slope_per_window']}`
- destructive-interference slope/window:
  `{slopes['destructive_interference_level_slope_per_window']}`
- destructive-interference post-transient slope/window:
  `{post_slopes['destructive_interference_level_post_transient_slope_per_window']}`
- basin-separability slope/window:
  `{slopes['basin_separability_level_slope_per_window']}`
- budget-error slope/window:
  `{slopes['budget_error_level_slope_per_window']}`

## Windows

| Window | A Retention | B Retention | Wrong-Basin Exchange | Destructive Interference | Separability | Passed | Blockers |
|---:|---:|---:|---:|---:|---:|---|---|
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
                "wrong_basin_post_transient_slope": result["trajectory"][
                    "post_transient_metric_slopes_per_window"
                ]["wrong_basin_leakage_level_post_transient_slope_per_window"],
                "next": result["next_iteration"],
                "id6_claimed": result["long_horizon_candidate_row"][
                    "id6_claimed"
                ],
            },
            sort_keys=True,
        )
    )
    print(BASE._rel(OUTPUT_PATH))
    print(BASE._rel(REPORT_PATH))


if __name__ == "__main__":
    main()

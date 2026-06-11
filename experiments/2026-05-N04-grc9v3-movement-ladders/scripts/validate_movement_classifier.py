"""Freeze the N04 M0-M3 movement classifier.

Iteration 6 is a classifier validation pass. It reads already-generated
Iteration 4 synthetic observable cases and Iteration 5 fixed-substrate lanes,
then applies one deterministic M0-M3 classifier without re-running dynamics.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OBSERVABLES_PATH = N04 / "outputs/movement_observables_validation.json"
TRANCHE_A_PATH = N04 / "outputs/fixed_substrate_tranche_a_report.json"
OUTPUT_PATH = N04 / "outputs/movement_classifier_m0_m3_validation.json"
REPORT_PATH = N04 / "reports/movement_classifier_m0_m3_validation.md"


CLASSIFIER_VERSION = "movement_m0_m3_classifier_v1"
PAIR_NEGLIGIBLE_DISPLACEMENT = 1e-9
SCHEMA_V1_REQUIRED_FIELDS = {
    "schema",
    "runtime_family",
    "execution_surface",
    "native_lgrc9v3_e3_pulse_used",
    "native_grc9v3_proposal_flux_control_used",
    "substrate",
    "loop_dependency",
    "drive",
    "identity_tracking",
    "movement_metrics",
    "taxonomies",
    "conservation",
    "topology",
    "gates",
    "claim_ceiling",
    "blocked_claims",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _canonical_digest(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _normalize_case(
    source: str,
    run_id: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    gates = record["gates"]
    if source == "iteration_4_observable_synthetic":
        observables = record["observables"]
        return {
            "source": source,
            "run_id": run_id,
            "fixture_id": record["fixture_id"],
            "lane_or_case_id": record["case_id"],
            "budget_passed": bool(gates["budget_passed"]),
            "displacement_passed": bool(gates["displacement_passed"]),
            "identity_passed": bool(gates["identity_passed"]),
            "shape_passed": bool(gates["shape_passed"]),
            "topology_passed": bool(gates["topology_passed"]),
            "nonnegative_passed": True,
            "centroid_displacement": observables["centroid"]["delta_x_total"],
            "centroid_displacement_abs": observables["centroid"]["delta_x_abs"],
            "width_relative_change_max": observables["shape"]["width_relative_change_max"],
            "profile_similarity": observables["profile_similarity"]["aligned"],
            "budget_surface": observables["conservation"]["budget_surface"],
            "identity_level_input": observables["support_tracking"][
                "identity_continuity_level"
            ],
            "boundary_flip_count": observables["boundary_flip_count"],
            "front_entered_mass": observables["boundary_flips"]["front_entered_mass"],
            "rear_left_mass": observables["boundary_flips"]["rear_left_mass"],
            "boundary_reassignment_passed": (
                observables["boundary_flips"]["front_entered_mass"] > 0.0
                and observables["boundary_flips"]["rear_left_mass"] > 0.0
            ),
            "diagnostic_signal": record.get("directional_bias_classification"),
            "m0_subtype_hint": (
                "null_symmetric"
                if record["case_id"] in {"null_static", "uniform_jitter"}
                else None
            ),
            "claim_flags": record["claim_flags"],
        }

    observables = record["observables"]
    metrics = record["movement_metrics"]
    drive = record["drive"]
    lane_id = record["lane_id"]
    m0_subtype_hint = None
    if lane_id in {"U0", "B0"} and drive["type"] == "none":
        m0_subtype_hint = "null_symmetric"
    elif drive["type"] == "one_time_zero_sum_kick":
        m0_subtype_hint = "no_kick_response"
    return {
        "source": source,
        "run_id": run_id,
        "fixture_id": record["fixture_id"],
        "lane_or_case_id": lane_id,
        "budget_passed": bool(gates["budget_passed"]),
        "displacement_passed": bool(gates["displacement_passed"]),
        "identity_passed": bool(gates["identity_passed"]),
        "shape_passed": bool(gates["shape_passed"]),
        "topology_passed": bool(gates["topology_passed"]),
        "nonnegative_passed": bool(gates.get("nonnegative_passed", True)),
        "centroid_displacement": metrics["centroid_displacement"],
        "centroid_displacement_abs": metrics["centroid_displacement_abs"],
        "width_relative_change_max": metrics["shape"]["width_relative_change_max"],
        "profile_similarity": metrics["profile_similarity"]["aligned"],
        "budget_surface": record["conservation"]["budget_surface"],
        "identity_level_input": observables["support_tracking"][
            "identity_continuity_level"
        ],
        "boundary_flip_count": observables["boundary_flip_count"],
        "front_entered_mass": observables["boundary_flips"]["front_entered_mass"],
        "rear_left_mass": observables["boundary_flips"]["rear_left_mass"],
        "boundary_reassignment_passed": (
            observables["boundary_flips"]["front_entered_mass"] > 0.0
            and observables["boundary_flips"]["rear_left_mass"] > 0.0
        ),
        "diagnostic_signal": record.get("directional_bias_classification"),
        "m0_subtype_hint": m0_subtype_hint,
        "claim_flags": record["claim_flags"],
    }


def _m0_subtype(item: dict[str, Any], primary_reason: str) -> str:
    if primary_reason == "budget_gate_failed":
        return "M0_budget_failure"
    if primary_reason == "topology_gate_failed":
        return "M0_topology_failure"
    if primary_reason == "nonnegative_coherence_gate_failed":
        return "M0_nonnegative_failure"
    if item.get("diagnostic_signal") == "subthreshold_directional_bias_observed":
        return "M0_subthreshold_directional_bias"
    if item.get("m0_subtype_hint") == "null_symmetric":
        return "M0_null_symmetric"
    if item.get("m0_subtype_hint") == "no_kick_response":
        return "M0_no_kick_response"
    return "M0_no_threshold_response"


def _all_gate_failures(item: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not item["topology_passed"]:
        failures.append("topology_gate_failed")
    if not item["budget_passed"]:
        failures.append("budget_gate_failed")
    if not item["nonnegative_passed"]:
        failures.append("nonnegative_coherence_gate_failed")
    if not item["displacement_passed"]:
        failures.append("displacement_below_threshold")
    if not item["identity_passed"]:
        failures.append("identity_gate_failed")
    if not item["boundary_reassignment_passed"]:
        failures.append("boundary_reassignment_failed")
    if not item["shape_passed"]:
        failures.append("shape_gate_failed")
    return failures


def _secondary_gate_failures(item: dict[str, Any], primary_reason: str) -> list[str]:
    return [
        failure
        for failure in _all_gate_failures(item)
        if failure != primary_reason
    ]


def _classifier_claim_flags() -> dict[str, bool]:
    return {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
    }


def _classify(item: dict[str, Any]) -> dict[str, Any]:
    hard_failures = []
    if not item["topology_passed"]:
        hard_failures.append("topology_gate_failed")
    if not item["budget_passed"]:
        hard_failures.append("budget_gate_failed")
    if not item["nonnegative_passed"]:
        hard_failures.append("nonnegative_coherence_gate_failed")

    gates_failed: list[str] = list(hard_failures)
    blocked_claims = [
        "loop_driven_movement",
        "locomotion_like_basin_dynamics",
        "adaptive_topology_movement",
        "movement_inherited_from_n03",
    ]

    if hard_failures:
        primary_reason = hard_failures[0]
        blocked_claims.extend(
            [
                "movement_response",
                "identity_preserving_displacement",
                "shape_preserving_displacement",
            ]
        )
        return {
            "classifier": CLASSIFIER_VERSION,
            "movement_level": "M0_blocked",
            "movement_level_index": 0,
            "classification": "blocked_by_hard_gate",
            "diagnostic_subtype": _m0_subtype(item, primary_reason),
            "gates_failed": gates_failed,
            "secondary_gate_failures": _secondary_gate_failures(item, primary_reason),
            "all_gate_failures": _all_gate_failures(item),
            "primary_blocked_reason": primary_reason,
            "blocked_reasons": list(gates_failed),
            "blocked_claims": blocked_claims,
            "movement_claim_allowed": False,
            "claim_flags": _classifier_claim_flags(),
        }

    if not item["displacement_passed"]:
        primary_reason = "displacement_below_threshold"
        gates_failed.append("displacement_below_threshold")
        blocked_claims.extend(
            [
                "movement_response",
                "identity_preserving_displacement",
                "shape_preserving_displacement",
            ]
        )
        return {
            "classifier": CLASSIFIER_VERSION,
            "movement_level": "M0_no_threshold_displacement",
            "movement_level_index": 0,
            "classification": "no_threshold_displacement",
            "diagnostic_subtype": _m0_subtype(item, primary_reason),
            "gates_failed": gates_failed,
            "secondary_gate_failures": _secondary_gate_failures(item, primary_reason),
            "all_gate_failures": _all_gate_failures(item),
            "primary_blocked_reason": primary_reason,
            "blocked_reasons": list(gates_failed),
            "blocked_claims": blocked_claims,
            "movement_claim_allowed": False,
            "claim_flags": _classifier_claim_flags(),
        }

    if not item["identity_passed"]:
        primary_reason = "identity_gate_failed"
        gates_failed.append("identity_gate_failed")
        blocked_claims.extend(
            ["identity_preserving_displacement", "shape_preserving_displacement"]
        )
        return {
            "classifier": CLASSIFIER_VERSION,
            "movement_level": "M1_apparent_centroid_displacement",
            "movement_level_index": 1,
            "classification": "apparent_displacement_identity_blocked",
            "diagnostic_subtype": "M1_identity_replacement_or_untracked_basin",
            "gates_failed": gates_failed,
            "secondary_gate_failures": _secondary_gate_failures(item, primary_reason),
            "all_gate_failures": _all_gate_failures(item),
            "primary_blocked_reason": primary_reason,
            "blocked_reasons": list(gates_failed),
            "blocked_claims": blocked_claims,
            "movement_claim_allowed": False,
            "claim_flags": _classifier_claim_flags(),
        }

    if not item["boundary_reassignment_passed"]:
        primary_reason = "boundary_reassignment_failed"
        gates_failed.append("boundary_reassignment_failed")
        blocked_claims.extend(
            ["boundary_reassignment", "shape_preserving_displacement"]
        )
        return {
            "classifier": CLASSIFIER_VERSION,
            "movement_level": "M1_apparent_centroid_displacement",
            "movement_level_index": 1,
            "classification": "apparent_displacement_boundary_blocked",
            "diagnostic_subtype": "M1_centroid_without_directed_boundary_reassignment",
            "gates_failed": gates_failed,
            "secondary_gate_failures": _secondary_gate_failures(item, primary_reason),
            "all_gate_failures": _all_gate_failures(item),
            "primary_blocked_reason": primary_reason,
            "blocked_reasons": list(gates_failed),
            "blocked_claims": blocked_claims,
            "movement_claim_allowed": False,
            "claim_flags": _classifier_claim_flags(),
        }

    if not item["shape_passed"]:
        primary_reason = "shape_gate_failed"
        gates_failed.append("shape_gate_failed")
        blocked_claims.append("shape_preserving_displacement")
        return {
            "classifier": CLASSIFIER_VERSION,
            "movement_level": "M2_identity_preserving_displacement",
            "movement_level_index": 2,
            "classification": "identity_displacement_shape_blocked",
            "diagnostic_subtype": "M2_boundary_reassignment_shape_blocked",
            "gates_failed": gates_failed,
            "secondary_gate_failures": _secondary_gate_failures(item, primary_reason),
            "all_gate_failures": _all_gate_failures(item),
            "primary_blocked_reason": primary_reason,
            "blocked_reasons": list(gates_failed),
            "blocked_claims": blocked_claims,
            "movement_claim_allowed": False,
            "claim_flags": _classifier_claim_flags(),
        }

    return {
        "classifier": CLASSIFIER_VERSION,
        "movement_level": "M3_shape_preserving_identity_displacement",
        "movement_level_index": 3,
        "classification": "shape_preserving_identity_displacement_candidate",
        "diagnostic_subtype": "M3_boundary_and_shape_preserved",
        "gates_failed": [],
        "secondary_gate_failures": [],
        "all_gate_failures": [],
        "primary_blocked_reason": None,
        "blocked_reasons": [],
        "blocked_claims": blocked_claims,
        "movement_claim_allowed": False,
        "claim_flags": _classifier_claim_flags(),
    }


def _schema_v1_fields_present(tranche_a: dict[str, Any]) -> bool:
    return all(
        SCHEMA_V1_REQUIRED_FIELDS <= set(lane_result)
        for lane_result in tranche_a["lane_results"].values()
    )


def _paired_control_results(
    classifications: dict[str, Any], tranche_a: dict[str, Any]
) -> dict[str, Any]:
    results = {}
    for pair_id, check in tranche_a["reversal_checks"].items():
        fixture_id, lane = pair_id.rsplit("_", 1)
        forward_id = f"{fixture_id}_{lane}"
        reverse_id = f"{fixture_id}_{lane}_reversed"
        forward = classifications[forward_id]
        reverse = classifications[reverse_id]
        if (
            abs(check["forward_displacement"]) <= PAIR_NEGLIGIBLE_DISPLACEMENT
            and abs(check["reverse_displacement"]) <= PAIR_NEGLIGIBLE_DISPLACEMENT
        ):
            paired_result = "no_threshold_response"
        elif check["opposite_sign"] and check["both_below_displacement_threshold"]:
            paired_result = "subthreshold_opposite_sign_bias"
        elif check["substrate_bias_possible"]:
            paired_result = "possible_substrate_bias"
        elif check["both_below_displacement_threshold"]:
            paired_result = "no_threshold_response"
        else:
            paired_result = "requires_review"
        results[pair_id] = {
            "forward_run_id": forward_id,
            "reverse_run_id": reverse_id,
            "forward_level": forward["movement_level"],
            "reverse_level": reverse["movement_level"],
            "forward_diagnostic_subtype": forward["diagnostic_subtype"],
            "reverse_diagnostic_subtype": reverse["diagnostic_subtype"],
            "forward_displacement": check["forward_displacement"],
            "reverse_displacement": check["reverse_displacement"],
            "paired_control_result": paired_result,
            "movement_claim_allowed": False,
        }
    return results


def _classifier_adversarial_cases() -> dict[str, dict[str, Any]]:
    base_claim_flags = {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
    }
    return {
        "iteration_6_adversarial_m2_shape_failure": {
            "source": "iteration_6_classifier_adversarial",
            "run_id": "iteration_6_adversarial_m2_shape_failure",
            "fixture_id": "classifier_adversarial_fixture",
            "lane_or_case_id": "m2_shape_failure",
            "budget_passed": True,
            "displacement_passed": True,
            "identity_passed": True,
            "shape_passed": False,
            "topology_passed": True,
            "nonnegative_passed": True,
            "centroid_displacement": 0.25,
            "centroid_displacement_abs": 0.25,
            "width_relative_change_max": 0.5,
            "profile_similarity": 0.2,
            "budget_surface": "node_only",
            "identity_level_input": "I2_gate_passed",
            "boundary_flip_count": 4,
            "front_entered_mass": 0.2,
            "rear_left_mass": 0.2,
            "boundary_reassignment_passed": True,
            "diagnostic_signal": "adversarial_shape_failure_after_boundary",
            "m0_subtype_hint": None,
            "claim_flags": base_claim_flags,
        },
        "iteration_6_adversarial_nonnegative_failure": {
            "source": "iteration_6_classifier_adversarial",
            "run_id": "iteration_6_adversarial_nonnegative_failure",
            "fixture_id": "classifier_adversarial_fixture",
            "lane_or_case_id": "nonnegative_failure",
            "budget_passed": True,
            "displacement_passed": True,
            "identity_passed": True,
            "shape_passed": True,
            "topology_passed": True,
            "nonnegative_passed": False,
            "centroid_displacement": 0.25,
            "centroid_displacement_abs": 0.25,
            "width_relative_change_max": 0.01,
            "profile_similarity": 0.99,
            "budget_surface": "node_only",
            "identity_level_input": "I2_gate_passed",
            "boundary_flip_count": 4,
            "front_entered_mass": 0.2,
            "rear_left_mass": 0.2,
            "boundary_reassignment_passed": True,
            "diagnostic_signal": "adversarial_negative_coherence",
            "m0_subtype_hint": None,
            "claim_flags": base_claim_flags,
        },
        "iteration_6_adversarial_boundary_churn_only": {
            "source": "iteration_6_classifier_adversarial",
            "run_id": "iteration_6_adversarial_boundary_churn_only",
            "fixture_id": "classifier_adversarial_fixture",
            "lane_or_case_id": "boundary_churn_only",
            "budget_passed": True,
            "displacement_passed": True,
            "identity_passed": True,
            "shape_passed": True,
            "topology_passed": True,
            "nonnegative_passed": True,
            "centroid_displacement": 0.25,
            "centroid_displacement_abs": 0.25,
            "width_relative_change_max": 0.01,
            "profile_similarity": 0.99,
            "budget_surface": "node_only",
            "identity_level_input": "I2_gate_passed",
            "boundary_flip_count": 32,
            "front_entered_mass": 0.0,
            "rear_left_mass": 0.0,
            "boundary_reassignment_passed": False,
            "diagnostic_signal": "adversarial_boundary_churn_without_handoff",
            "m0_subtype_hint": None,
            "claim_flags": base_claim_flags,
        },
    }


def validate_classifier() -> dict[str, Any]:
    observables = _load_json(OBSERVABLES_PATH)
    tranche_a = _load_json(TRANCHE_A_PATH)

    normalized: dict[str, Any] = {}
    for run_id, record in observables["case_results"].items():
        normalized[run_id] = _normalize_case(
            "iteration_4_observable_synthetic", run_id, record
        )
    for run_id, record in tranche_a["lane_results"].items():
        normalized[run_id] = _normalize_case("iteration_5_fixed_substrate", run_id, record)
    normalized.update(_classifier_adversarial_cases())

    classifications = {
        run_id: {**item, **_classify(item)} for run_id, item in normalized.items()
    }
    classifications_second_pass = {
        run_id: {**item, **_classify(item)} for run_id, item in normalized.items()
    }

    def _level(run_id: str) -> str:
        return classifications[run_id]["movement_level"]

    budget_blocked = [
        run_id
        for run_id, result in classifications.items()
        if "budget" in run_id and result["primary_blocked_reason"] == "budget_gate_failed"
    ]
    topology_blocked = [
        run_id
        for run_id, result in classifications.items()
        if "topology_changed" in run_id
        and result["primary_blocked_reason"] == "topology_gate_failed"
    ]
    identity_blocked = [
        run_id
        for run_id, result in classifications.items()
        if "basin_replacement" in run_id
        and result["primary_blocked_reason"] == "identity_gate_failed"
    ]
    shape_blocked = [
        run_id
        for run_id, result in classifications.items()
        if "smeared_shift" in run_id
        and result["movement_level"] != "M3_shape_preserving_identity_displacement"
    ]
    m2_shape_blocked = [
        run_id
        for run_id, result in classifications.items()
        if result["movement_level"] == "M2_identity_preserving_displacement"
        and result["primary_blocked_reason"] == "shape_gate_failed"
    ]
    nonnegative_blocked = [
        run_id
        for run_id, result in classifications.items()
        if result["primary_blocked_reason"] == "nonnegative_coherence_gate_failed"
    ]
    tranche_a_levels = {
        run_id: result["movement_level"]
        for run_id, result in classifications.items()
        if result["source"] == "iteration_5_fixed_substrate"
    }
    paired_controls = _paired_control_results(classifications, tranche_a)
    subtype_distribution: dict[str, int] = {}
    for result in classifications.values():
        subtype = result["diagnostic_subtype"]
        subtype_distribution[subtype] = subtype_distribution.get(subtype, 0) + 1

    checks = {
        "deterministic_classification": _canonical_digest(classifications)
        == _canonical_digest(classifications_second_pass),
        "m0_m3_levels_emitted": all(
            result["movement_level"].startswith(("M0", "M1", "M2", "M3"))
            for result in classifications.values()
        ),
        "budget_failure_blocks_promotion": bool(budget_blocked),
        "topology_failure_blocks_promotion": bool(topology_blocked),
        "identity_failure_blocks_m2_m3": bool(identity_blocked)
        and all(
            classifications[run_id]["movement_level_index"] <= 1
            for run_id in identity_blocked
        ),
        "shape_failure_blocks_m3": bool(shape_blocked)
        and all(classifications[run_id]["movement_level_index"] < 3 for run_id in shape_blocked),
        "m2_shape_failure_gate_exercised": bool(m2_shape_blocked),
        "nonnegative_failure_blocks_promotion": bool(nonnegative_blocked)
        and all(
            classifications[run_id]["movement_level"] == "M0_blocked"
            for run_id in nonnegative_blocked
        ),
        "synthetic_positive_reaches_m3": all(
            _level(run_id) == "M3_shape_preserving_identity_displacement"
            for run_id in classifications
            if "shape_preserving_shift" in run_id
            or "boundary_reassignment_front_gain_rear_loss" in run_id
            or "ring_wrap_" in run_id
        ),
        "iteration_5_tranche_a_remains_m0": all(
            level.startswith("M0") for level in tranche_a_levels.values()
        ),
        "iteration_5_subthreshold_bias_preserved": all(
            classifications[run_id]["movement_level"] == "M0_no_threshold_displacement"
            and classifications[run_id]["diagnostic_subtype"]
            == "M0_subthreshold_directional_bias"
            for run_id in [
                "S0_chain_v1_B1",
                "S0_chain_v1_B1_reversed",
                "S1_ring_v1_B1",
                "S1_ring_v1_B1_reversed",
            ]
        ),
        "boundary_churn_not_m2": (
            classifications["iteration_6_adversarial_boundary_churn_only"][
                "movement_level_index"
            ]
            < 2
            and classifications["iteration_6_adversarial_boundary_churn_only"][
                "primary_blocked_reason"
            ]
            == "boundary_reassignment_failed"
        ),
        "paired_control_results_emitted": bool(paired_controls)
        and all(
            result["paired_control_result"]
            in {
                "subthreshold_opposite_sign_bias",
                "possible_substrate_bias",
                "no_threshold_response",
            }
            for result in paired_controls.values()
        ),
        "schema_v1_required_fields_present": _schema_v1_fields_present(tranche_a),
        "all_reports_keep_claims_false": all(
            not any(result["claim_flags"].values()) for result in classifications.values()
        ),
        "secondary_gate_failures_visible": any(
            result["secondary_gate_failures"]
            for result in classifications.values()
        ),
    }

    distribution: dict[str, int] = {}
    for result in classifications.values():
        distribution[result["movement_level"]] = distribution.get(result["movement_level"], 0) + 1

    return {
        "schema": "movement_classifier_m0_m3_validation_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "classifier_version": CLASSIFIER_VERSION,
        "source_artifacts": {
            "observables": OBSERVABLES_PATH.relative_to(ROOT).as_posix(),
            "fixed_substrate_tranche_a": TRANCHE_A_PATH.relative_to(ROOT).as_posix(),
        },
        "classifier_rules": {
            "hard_blockers": [
                "budget_gate_failed",
                "topology_gate_failed",
                "nonnegative_coherence_gate_failed",
            ],
            "M0": "no threshold displacement or hard-gate blocked",
            "M1": "threshold centroid displacement with budget/topology/nonnegative gates, but identity may fail",
            "M2": "M1 plus identity gate passed and directed boundary reassignment observed, but shape may fail",
            "M3": "M2 plus shape/profile gates passed",
            "claim_policy": "M0-M3 classifier labels evidence only; movement_claim_allowed remains false until later report policy opens it.",
            "m0_subtype_policy": "M0 subtypes are derived from explicit diagnostic signals and lane/drive metadata where available; otherwise the classifier falls back to M0_no_threshold_response.",
            "validation_scope": "Iteration 6 validates Iteration 4/5 movement-observable artifacts plus classifier-adversarial cases. Iteration 7 E3 pulse import is not a movement run and is validated separately.",
            "primary_blocked_reason_precedence": [
                "topology_gate_failed",
                "budget_gate_failed",
                "nonnegative_coherence_gate_failed",
                "identity_gate_failed",
                "displacement_below_threshold",
                "boundary_reassignment_failed",
                "shape_gate_failed",
            ],
        },
        "checks": checks,
        "movement_level_distribution": distribution,
        "diagnostic_subtype_distribution": subtype_distribution,
        "classifications": classifications,
        "paired_control_results": paired_controls,
        "environment": _environment_record(),
        "summary": {
            "budget_blocked_runs": budget_blocked,
            "topology_blocked_runs": topology_blocked,
            "identity_blocked_runs": identity_blocked,
            "shape_blocked_runs": shape_blocked,
            "m2_shape_blocked_runs": m2_shape_blocked,
            "nonnegative_blocked_runs": nonnegative_blocked,
            "iteration_5_tranche_a_levels": tranche_a_levels,
        },
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Movement Classifier M0-M3 Validation",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_classifier.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        f"Classifier: `{result['classifier_version']}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(["", "## Distribution", "", "| Level | Count |", "|---|---:|"])
    for level, count in sorted(result["movement_level_distribution"].items()):
        lines.append(f"| `{level}` | `{count}` |")

    lines.extend(["", "## Diagnostic Subtypes", "", "| Subtype | Count |", "|---|---:|"])
    for subtype, count in sorted(result["diagnostic_subtype_distribution"].items()):
        lines.append(f"| `{subtype}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Iteration 5 Classifications",
            "",
            "| Run | Level | Subtype | Primary Blocker | dX |",
            "|---|---|---|---|---:|",
        ]
    )
    for run_id, item in result["classifications"].items():
        if item["source"] != "iteration_5_fixed_substrate":
            continue
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.9f}` |".format(
                run_id,
                item["movement_level"],
                item["diagnostic_subtype"],
                item["primary_blocked_reason"],
                item["centroid_displacement"],
            )
        )

    lines.extend(
        [
            "",
            "## Paired Controls",
            "",
            "| Pair | Result | Forward dX | Reverse dX |",
            "|---|---|---:|---:|",
        ]
    )
    for pair_id, pair in result["paired_control_results"].items():
        lines.append(
            "| `{}` | `{}` | `{:.9f}` | `{:.9f}` |".format(
                pair_id,
                pair["paired_control_result"],
                pair["forward_displacement"],
                pair["reverse_displacement"],
            )
        )

    lines.extend(
        [
            "",
            "## Blocker Audits",
            "",
            f"- Budget-blocked runs: `{result['summary']['budget_blocked_runs']}`",
            f"- Topology-blocked runs: `{result['summary']['topology_blocked_runs']}`",
            f"- Identity-blocked runs: `{result['summary']['identity_blocked_runs']}`",
            f"- Shape-blocked runs: `{result['summary']['shape_blocked_runs']}`",
            f"- M2 shape-blocked runs: `{result['summary']['m2_shape_blocked_runs']}`",
            f"- Nonnegative-blocked runs: `{result['summary']['nonnegative_blocked_runs']}`",
            "",
            "## Notes",
            "",
            "- M0-M3 labels classify evidence only; movement claim flags remain false in this validation.",
            "- Budget, topology, and nonnegative coherence failures are hard blockers.",
            "- Identity failure caps evidence at M1.",
            "- Directed boundary reassignment is required before M2.",
            "- Shape/profile failure caps evidence below M3.",
            "- Boundary churn without coherent front/rear handoff is not M2, even when displacement and identity gates pass.",
            "- Iteration 5 B1/B1_reversed are preserved as M0 subthreshold directional bias.",
            "- Iteration 5 fixed-substrate tranche A remains M0 because no lane reaches threshold displacement.",
            "- Iteration 7 E3 pulse import is not a movement run and is validated separately.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_classifier()
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

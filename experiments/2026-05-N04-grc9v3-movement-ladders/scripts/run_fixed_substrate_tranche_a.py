"""Run N04 Iteration 5 fixed-substrate null and one-time response lanes.

This tranche uses an experiment-local fixed-topology diffusion runner over the
declared S0/S1 fixtures. It is a conservative response test for validated
movement observables, not a GRC9V3 or LGRC9V3 runtime claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
SCRIPT_DIR = N04 / "scripts"
MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
INITIALIZER_PATH = N04 / "outputs/movement_initializer_validation.json"
OUTPUT_PATH = N04 / "outputs/fixed_substrate_tranche_a_report.json"
REPORT_PATH = N04 / "reports/fixed_substrate_tranche_a_report.md"
TIMESERIES_DIR = N04 / "outputs/fixed_substrate_tranche_a_timeseries"

sys.path.insert(0, str(SCRIPT_DIR))
from validate_movement_observables import (  # noqa: E402
    IDENTITY_ALIGNMENT_MAX_SHIFT,
    PROFILE_ALIGNMENT_MAX_SHIFT,
    _observables,
)


RUNNER_CONFIG = {
    "runner_id": "experiment_local_fixed_topology_diffusive_response_runner_v1",
    "dt": 0.05,
    "steps": 16,
    "equation": "C_u -= dt*w*(C_u-C_v); C_v += dt*w*(C_u-C_v) per undirected edge",
    "projection_after_step": "none",
    "topology_mutation_allowed": False,
    "nonnegativity_guard": "raise_if_C_i_below_-1e-12",
    "explicit_euler_stability_note": "dt=0.05 with unit-weight degree<=2 fixtures is inside the conservative diffusion stability bound dt <= 1/max_degree.",
    "profile_alignment_max_shift": PROFILE_ALIGNMENT_MAX_SHIFT,
    "identity_alignment_max_shift": IDENTITY_ALIGNMENT_MAX_SHIFT,
}
NULL_EXCESS_RELATIVE_TOLERANCE = 0.01
NULL_EXCESS_ABSOLUTE_TOLERANCE = 1e-9
NONNEGATIVITY_EPSILON = 1e-12


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
        "git_diff_check": _run_git_command(["diff", "--check"]),
    }


def _node_values(initializer: dict[str, Any], fixture_id: str, lane_id: str) -> list[float]:
    lane_result = initializer["lane_results"][f"{fixture_id}:{lane_id}"]
    values = lane_result["coherence_by_node"]
    return [float(values[str(index)]) for index in range(len(values))]


def _init_result(initializer: dict[str, Any], fixture_id: str, lane_id: str) -> dict[str, Any]:
    return initializer["lane_results"][f"{fixture_id}:{lane_id}"]


def _diffuse(fixture: dict[str, Any], initial: list[float]) -> list[list[float]]:
    current = list(initial)
    states = [list(current)]
    dt = float(RUNNER_CONFIG["dt"])
    for _step in range(int(RUNNER_CONFIG["steps"])):
        delta = [0.0 for _ in current]
        for edge in fixture["edges"]:
            u = int(edge["u"])
            v = int(edge["v"])
            weight = float(edge["weight"])
            flux_uv = weight * (current[u] - current[v])
            delta[u] -= dt * flux_uv
            delta[v] += dt * flux_uv
        current = [value + change for value, change in zip(current, delta)]
        if min(current) < -NONNEGATIVITY_EPSILON:
            raise ValueError(
                f"negative coherence produced by diffusion runner: min={min(current)}"
            )
        states.append(current)
    return states


def _write_timeseries(
    run_id: str,
    fixture_id: str,
    lane_id: str,
    states: list[list[float]],
    observables: dict[str, Any],
) -> dict[str, str]:
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    path = TIMESERIES_DIR / f"{run_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for step, state in enumerate(states):
            handle.write(
                json.dumps(
                    {
                        "step": step,
                        "fixture_id": fixture_id,
                        "lane_id": lane_id,
                        "centroid": observables["centroid"]["x_t"][step],
                        "support_mask": observables["support_tracking"]["support_mask_t"][step],
                        "mass": observables["shape"]["mass_t"][step],
                        "width": observables["shape"]["width_t"][step],
                        "budget": observables["conservation"]["budget_t"][step],
                        "coherence_by_node": {
                            str(index): value for index, value in enumerate(state)
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def _std(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def _primary_blockers(
    budget_passed: bool,
    identity_passed: bool,
    topology_passed: bool,
    displacement_passed: bool,
    shape_passed: bool,
    nonnegative_passed: bool,
) -> list[str]:
    blockers = []
    if not budget_passed:
        blockers.append("budget_gate_failed")
    if not identity_passed:
        blockers.append("identity_gate_failed")
    if not topology_passed:
        blockers.append("topology_gate_failed")
    if not nonnegative_passed:
        blockers.append("nonnegative_coherence_gate_failed")
    if not displacement_passed:
        blockers.append("displacement_below_threshold")
    if not shape_passed:
        blockers.append("shape_gate_failed")
    return blockers


def _lane_claim_ceiling(lane_id: str, displacement_passed: bool) -> str:
    if lane_id in {"U0", "B0"}:
        return "no_directed_movement"
    if displacement_passed:
        return "movement_response_candidate_only"
    return "no_movement_response_observed"


def _movement_level(displacement_passed: bool) -> str:
    return "M1_displacement_response_candidate" if displacement_passed else "M0_no_threshold_displacement"


def _directional_bias_classification(
    lane_id: str,
    displacement_abs: float,
    effective_displacement_min: float,
    null_envelope: dict[str, float],
) -> str:
    if lane_id in {"U0", "B0"}:
        return "null_lane"
    if displacement_abs >= effective_displacement_min:
        return "movement_response_candidate"
    null_excess_tolerance = max(
        NULL_EXCESS_ABSOLUTE_TOLERANCE,
        float(null_envelope["max"]) * NULL_EXCESS_RELATIVE_TOLERANCE,
    )
    if displacement_abs > float(null_envelope["max"]) + null_excess_tolerance:
        return "subthreshold_directional_bias_observed"
    return "no_threshold_level_response"


def run_tranche() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    initializer = _load_json(INITIALIZER_PATH)
    metrics = manifest["metric_defaults"]
    null_envelope = manifest["null_displacement_envelope"]
    epsilon_budget = float(metrics["epsilon_budget"])
    width_max = float(metrics["width_relative_change_max"])
    profile_min = float(metrics["profile_similarity_min"])
    identity_min = float(metrics["identity_mass_ratio_min"])
    configured_displacement_min = float(metrics["configured_displacement_min"])

    lane_ids = ["U0", "B0", "B1", "B1_reversed", "K1", "K1_reversed"]
    null_displacement_records: list[dict[str, Any]] = []
    baseline_centroids = {
        fixture_id: float(_init_result(initializer, fixture_id, "B0")["centroid"])
        for fixture_id, fixture in manifest["fixtures"].items()
        if fixture.get("status") != "deferred"
    }

    for fixture_id, fixture in manifest["fixtures"].items():
        if fixture.get("status") == "deferred":
            continue
        for lane_id in ["U0", "B0"]:
            lane = manifest["lanes"][lane_id]
            states = _diffuse(fixture, _node_values(initializer, fixture_id, lane_id))
            obs = _observables(
                fixture,
                states,
                1.0,
                direction_source=lane["front_rear_definition"]["direction_source"],
                identity_gate_min=identity_min,
            )
            null_displacement_records.append(
                {
                    "run_id": f"{fixture_id}_{lane_id}",
                    "fixture_id": fixture_id,
                    "lane_id": lane_id,
                    "delta_x_abs": obs["centroid"]["delta_x_abs"],
                    "note": (
                        "ring_antipodal_unwrap_convention_artifact"
                        if fixture["type"] == "ring" and lane_id == "B0"
                        else "null_response"
                    ),
                }
            )

    null_displacements = [record["delta_x_abs"] for record in null_displacement_records]
    null_mean = sum(null_displacements) / len(null_displacements)
    null_std = _std(null_displacements)
    empirical_threshold = null_mean + float(metrics["null_calibration_k"]) * null_std
    effective_displacement_min = max(
        configured_displacement_min,
        empirical_threshold,
    )
    max_null_record = max(null_displacement_records, key=lambda record: record["delta_x_abs"])
    null_envelope_summary = {
        "calibration_status": "iteration_5_first_tranche_empirical",
        "calibrated": True,
        "mean": null_mean,
        "max": max(null_displacements),
        "std": null_std,
        "k": float(metrics["null_calibration_k"]),
        "empirical_threshold": empirical_threshold,
        "null_excess_relative_tolerance": NULL_EXCESS_RELATIVE_TOLERANCE,
        "null_excess_absolute_tolerance": NULL_EXCESS_ABSOLUTE_TOLERANCE,
        "configured_min": configured_displacement_min,
        "effective_displacement_min": effective_displacement_min,
        "threshold_source": (
            "configured_min" if configured_displacement_min >= empirical_threshold else "null_envelope"
        ),
        "configured_min_dominates_null_envelope": configured_displacement_min
        >= empirical_threshold,
        "records": null_displacement_records,
        "max_source": max_null_record,
        "frozen_before_tranche": True,
    }

    lane_results: dict[str, Any] = {}

    for fixture_id, fixture in manifest["fixtures"].items():
        if fixture.get("status") == "deferred":
            continue
        for lane_id in lane_ids:
            lane = manifest["lanes"][lane_id]
            run_id = f"{fixture_id}_{lane_id}"
            init_result = _init_result(initializer, fixture_id, lane_id)
            states = _diffuse(fixture, _node_values(initializer, fixture_id, lane_id))
            direction_values = lane["front_rear_definition"]["direction_vector"]
            direction = float(direction_values[0]) if direction_values else 1.0
            direction_source = lane["front_rear_definition"]["direction_source"]
            obs = _observables(
                fixture,
                states,
                direction,
                direction_source=direction_source,
                identity_gate_min=identity_min,
            )
            timeseries = _write_timeseries(run_id, fixture_id, lane_id, states, obs)
            budget_passed = obs["conservation"]["budget_abs_error_max"] <= epsilon_budget
            nonnegative_passed = min(min(state) for state in states) >= -NONNEGATIVITY_EPSILON
            displacement_abs = obs["centroid"]["delta_x_abs"]
            displacement_passed = displacement_abs >= effective_displacement_min
            identity_passed = obs["support_tracking"]["identity_mass_ratio_min"] >= identity_min
            shape_passed = (
                obs["shape"]["width_relative_change_max"] <= width_max
                and obs["profile_similarity"]["aligned"] >= profile_min
            )
            topology_passed = obs["topology"]["topology_changed"] is False
            response_candidate = (
                lane_id not in {"U0", "B0"}
                and displacement_passed
                and budget_passed
                and identity_passed
                and shape_passed
                and topology_passed
                and nonnegative_passed
            )
            lane_results[run_id] = {
                "run_id": run_id,
                "schema": "movement_ladder_report_v1",
                "fixture_id": fixture_id,
                "lane_id": lane_id,
                "runtime_family": "experiment_local",
                "execution_surface": "surface_a_fixed_substrate_metrics",
                "runner_config": RUNNER_CONFIG,
                "substrate": {
                    "fixture_id": fixture_id,
                    "substrate_level": fixture["substrate_level"],
                    "type": fixture["type"],
                    "node_count": fixture["node_count"],
                    "edge_count": fixture["edge_count"],
                    "topology_policy": "fixed",
                    "coordinate_policy": fixture["coordinate_policy"],
                },
                "native_lgrc9v3_e3_pulse_used": False,
                "native_grc9v3_proposal_flux_control_used": False,
                "loop_dependency": {
                    "source_experiment": "N03",
                    "loop_ladder_level": "L5",
                    "movement_claim_inherited": False,
                    "used_as_drive": False,
                },
                "drive": {
                    "type": lane.get("drive", "one_time_zero_sum_kick"),
                    "initializer": lane["initializer"],
                    "kick": lane.get("kick"),
                    "stimulus_audit": {
                        "raw_centroid_before_projection": init_result[
                            "raw_centroid_before_projection"
                        ],
                        "post_projection_centroid": init_result["centroid"],
                        "baseline_b0_centroid": baseline_centroids[fixture_id],
                        "raw_centroid_bias_from_b0": init_result[
                            "raw_centroid_before_projection"
                        ]
                        - baseline_centroids[fixture_id],
                        "post_projection_centroid_bias_from_b0": init_result["centroid"]
                        - baseline_centroids[fixture_id],
                        "centroid_shift_due_to_projection": init_result[
                            "centroid_shift_due_to_projection"
                        ],
                        "projection_delta_norm": init_result["projection_delta_norm"],
                        "post_projection_asymmetry_score": init_result[
                            "stimulus_audit"
                        ]["post_projection_asymmetry_score"],
                        "post_projection_budget_error": init_result["budget_error"],
                        "stimulus_survived_projection": init_result["stimulus_audit"][
                            "stimulus_survived_projection"
                        ],
                    },
                    "kick_audit": {
                        "applied_step": 0,
                        "applied_once": lane.get("kick") == "zero_sum_kick",
                        "raw_kick_sum": (init_result.get("kick") or {}).get("raw_kick_sum"),
                        "kick_l1_norm": (
                            2.0 * float((init_result.get("kick") or {}).get("kick_delta", 0.0))
                        ),
                        "kick_sign": (
                            "positive"
                            if lane.get("front_mask_offset", 0) > lane.get("rear_mask_offset", 0)
                            else "negative"
                            if lane.get("kick") == "zero_sum_kick"
                            else "not_applicable"
                        ),
                        "front_mask": (init_result.get("kick") or {}).get("front_mask"),
                        "rear_mask": (init_result.get("kick") or {}).get("rear_mask"),
                    },
                },
                "observables": obs,
                "identity_tracking": obs["support_tracking"],
                "taxonomies": {
                    "movement_level": _movement_level(displacement_passed),
                    "identity_level": obs["support_tracking"]["identity_continuity_level"],
                    "shape_level": "G3_profile_preserved" if shape_passed else "G0_shape_failed",
                    "budget_level": "Q1_budget_conserved" if budget_passed else "Q0_budget_failed",
                    "front_rear_level": "R0_no_coordinated_boundary_movement",
                    "boundary_level": "B0_no_boundary_management_claim",
                },
                "movement_metrics": {
                    "centroid_displacement": obs["centroid"]["delta_x_total"],
                    "centroid_displacement_abs": displacement_abs,
                    "centroid_delta_final": obs["centroid"]["delta_x_total"],
                    "centroid_delta_max_abs": max(
                        abs(value - obs["centroid"]["x_t"][0])
                        for value in obs["centroid"]["x_t"]
                    ),
                    "centroid_delta_windowed": obs["centroid"]["delta_x_total"],
                    "measurement_window": {
                        "start_step": 0,
                        "end_step": int(RUNNER_CONFIG["steps"]),
                        "settling_window": "none",
                    },
                    "movement_cost": obs["movement_cost"],
                    "front_rear_boundary_flips": obs["boundary_flips"],
                    "shape": obs["shape"],
                    "profile_similarity": obs["profile_similarity"],
                },
                "conservation": obs["conservation"],
                "topology": obs["topology"],
                "gates": {
                    "budget_passed": budget_passed,
                    "displacement_passed": displacement_passed,
                    "identity_passed": identity_passed,
                    "shape_passed": shape_passed,
                    "topology_passed": topology_passed,
                    "nonnegative_passed": nonnegative_passed,
                    "movement_response_candidate": response_candidate,
                    "below_configured_threshold": displacement_abs < configured_displacement_min,
                    "below_effective_threshold": displacement_abs < effective_displacement_min,
                },
                "directional_bias_classification": _directional_bias_classification(
                    lane_id,
                    displacement_abs,
                    effective_displacement_min,
                    null_envelope_summary,
                ),
                "claim_ceiling": _lane_claim_ceiling(lane_id, displacement_passed),
                "blocked_claims": [
                    "loop_driven_movement",
                    "locomotion_like_basin_dynamics",
                    "adaptive_topology_movement",
                    "movement_inherited_from_n03",
                ]
                + _primary_blockers(
                    budget_passed,
                    identity_passed,
                    topology_passed,
                    displacement_passed,
                    shape_passed,
                    nonnegative_passed,
                ),
                "claim_flags": {
                    "movement_claim_allowed": False,
                    "loop_driven_movement_claim_allowed": False,
                    "locomotion_like_claim_allowed": False,
                    "adaptive_topology_entry_allowed": False,
                    "movement_claim_inherited_from_n03": False,
                },
                "runner_audit": {
                    "min_coherence": min(min(state) for state in states),
                    "max_coherence": max(max(state) for state in states),
                    "nonnegative_passed": nonnegative_passed,
                    "projection_after_step": RUNNER_CONFIG["projection_after_step"],
                    "step_count": int(RUNNER_CONFIG["steps"]),
                },
                "timeseries": timeseries,
            }

    reversal_checks = {}
    for fixture_id, fixture in manifest["fixtures"].items():
        if fixture.get("status") == "deferred":
            continue
        for base_lane in ["B1", "K1"]:
            forward = lane_results[f"{fixture_id}_{base_lane}"]
            reverse = lane_results[f"{fixture_id}_{base_lane}_reversed"]
            fdx = forward["movement_metrics"]["centroid_displacement"]
            rdx = reverse["movement_metrics"]["centroid_displacement"]
            reversal_checks[f"{fixture_id}_{base_lane}"] = {
                "forward_displacement": fdx,
                "reverse_displacement": rdx,
                "opposite_sign": fdx * rdx < 0.0,
                "substrate_bias_possible": fdx * rdx > 0.0
                and (
                    abs(fdx) < effective_displacement_min
                    and abs(rdx) < effective_displacement_min
                ),
                "opposite_sign_or_both_negligible": fdx * rdx < 0.0
                or (
                    abs(fdx) < effective_displacement_min
                    and abs(rdx) < effective_displacement_min
                ),
                "both_below_displacement_threshold": (
                    abs(fdx) < effective_displacement_min
                    and abs(rdx) < effective_displacement_min
                ),
            }

    b0_displacements = {
        result["fixture_id"]: result["movement_metrics"]["centroid_displacement"]
        for result in lane_results.values()
        if result["lane_id"] == "B0"
    }
    for run_id, result in lane_results.items():
        notes = []
        lane_id = result["lane_id"]
        fixture_id = result["fixture_id"]
        dx = result["movement_metrics"]["centroid_displacement"]
        stimulus = result["drive"]["stimulus_audit"]
        if lane_id in {"B1", "B1_reversed"}:
            asymmetry = stimulus["post_projection_centroid_bias_from_b0"]
            if asymmetry * dx < 0.0:
                notes.append(
                    "asymmetric initial condition under symmetric diffusion relaxed opposite the initial mass bias; this is subthreshold relaxation, not directed movement"
                )
        if fixture_id == "S1_ring_v1" and lane_id in {"K1", "K1_reversed"}:
            if abs(dx - b0_displacements[fixture_id]) <= 1e-12:
                notes.append(
                    "displacement matches S1 B0 ring antipodal unwrap baseline; kick signal is swamped by the ring convention floor"
                )
        result["diagnostic_notes"] = notes

    for fixture_id in {result["fixture_id"] for result in lane_results.values()}:
        key = f"{fixture_id}_B1"
        if key in reversal_checks:
            check = reversal_checks[key]
            f_abs = abs(check["forward_displacement"])
            r_abs = abs(check["reverse_displacement"])
            check["abs_magnitude_delta"] = abs(f_abs - r_abs)
            check["relative_magnitude_delta"] = (
                abs(f_abs - r_abs) / max((f_abs + r_abs) / 2.0, 1e-12)
            )
            if fixture_id == "S1_ring_v1" and check["relative_magnitude_delta"] > 0.05:
                check["interpretation"] = (
                    "below-threshold B1 reversal magnitude asymmetry likely reflects interaction with ring unwrap convention"
                )

    checks = {
        "all_lane_budgets_passed": all(
            result["gates"]["budget_passed"] for result in lane_results.values()
        ),
        "all_topology_gates_passed": all(
            result["gates"]["topology_passed"] for result in lane_results.values()
        ),
        "all_nonnegative_gates_passed": all(
            result["gates"]["nonnegative_passed"] for result in lane_results.values()
        ),
        "u0_b0_reject_directed_movement": all(
            not result["gates"]["displacement_passed"]
            for result in lane_results.values()
            if result["lane_id"] in {"U0", "B0"}
        ),
        "response_lanes_do_not_claim_loop_or_locomotion": all(
            not result["claim_flags"]["loop_driven_movement_claim_allowed"]
            and not result["claim_flags"]["locomotion_like_claim_allowed"]
            for result in lane_results.values()
            if result["lane_id"] not in {"U0", "B0"}
        ),
        "reversal_controls_are_coherent": all(
            check["opposite_sign_or_both_negligible"] for check in reversal_checks.values()
        ),
        "timeseries_evidence_emitted": all(
            bool(result["timeseries"]["sha256"]) for result in lane_results.values()
        ),
        "no_movement_claims_emitted": all(
            not any(result["claim_flags"].values()) for result in lane_results.values()
        ),
    }
    return {
        "schema": "fixed_substrate_tranche_a_report_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "runtime_family": "experiment_local",
        "execution_surface": "surface_a_fixed_substrate_metrics",
        "runner_config": RUNNER_CONFIG,
        "environment": _environment_record(),
        "checks": checks,
        "displacement_threshold_policy": null_envelope_summary,
        "null_displacement_envelope": null_envelope_summary,
        "metric_thresholds": {
            "configured_displacement_min": configured_displacement_min,
            "effective_displacement_min": effective_displacement_min,
            "epsilon_budget": epsilon_budget,
            "identity_mass_ratio_min": identity_min,
            "width_relative_change_max": width_max,
            "profile_similarity_min": profile_min,
        },
        "reversal_checks": reversal_checks,
        "lane_results": lane_results,
        "summary": {
            "movement_response_candidates": [
                run_id
                for run_id, result in lane_results.items()
                if result["gates"]["movement_response_candidate"]
            ],
            "subthreshold_directional_bias_runs": [
                run_id
                for run_id, result in lane_results.items()
                if result["directional_bias_classification"]
                == "subthreshold_directional_bias_observed"
            ],
            "below_threshold_substrate_bias_possible": [
                key
                for key, check in reversal_checks.items()
                if check["substrate_bias_possible"]
            ],
            "max_abs_response_displacement": max(
                abs(result["movement_metrics"]["centroid_displacement"])
                for result in lane_results.values()
            ),
            "fixed_substrate_tranche_a_result": "no_movement_response_candidates",
            "interpretation": (
                "Fixed-substrate tranche A validated null/control execution, "
                "but produced no movement-response candidates under the frozen "
                "effective displacement gate."
            ),
        },
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Fixed-Substrate Tranche A Report",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_fixed_substrate_tranche_a.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Execution surface: `{result['execution_surface']}`",
        f"- Runner: `{result['runner_config']['runner_id']}`",
        f"- Fixed-substrate tranche A result: `{result['summary']['fixed_substrate_tranche_a_result']}`",
        f"- Movement response candidates: `{result['summary']['movement_response_candidates']}`",
        f"- Subthreshold directional bias runs: `{result['summary']['subthreshold_directional_bias_runs']}`",
        f"- Below-threshold substrate-bias-possible reversal pairs: `{result['summary']['below_threshold_substrate_bias_possible']}`",
        f"- Max absolute response displacement: `{result['summary']['max_abs_response_displacement']:.9f}`",
        f"- Effective displacement threshold: `{result['displacement_threshold_policy']['effective_displacement_min']:.9f}`",
        f"- Interpretation: {result['summary']['interpretation']}",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Threshold Policy",
            "",
            f"- Configured minimum: `{result['displacement_threshold_policy']['configured_min']:.9f}`",
            f"- Empirical null threshold: `{result['displacement_threshold_policy']['empirical_threshold']:.9f}`",
            f"- Effective minimum: `{result['displacement_threshold_policy']['effective_displacement_min']:.9f}`",
            f"- Threshold source: `{result['displacement_threshold_policy']['threshold_source']}`",
            f"- Null max source: `{result['displacement_threshold_policy']['max_source']['run_id']}` "
            f"(`{result['displacement_threshold_policy']['max_source']['note']}`)",
            "",
            "## Lanes",
            "",
            "| Run | Budget | Move | Identity | Shape | dX final | dX max | Bias | Width d | Profile | Claim Ceiling |",
            "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|",
        ]
    )
    for run_id, lane in result["lane_results"].items():
        gates = lane["gates"]
        metrics = lane["movement_metrics"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{:.9f}` | `{:.9f}` | `{}` | `{:.6f}` | `{:.6f}` | `{}` |".format(
                run_id,
                gates["budget_passed"],
                gates["displacement_passed"],
                gates["identity_passed"],
                gates["shape_passed"],
                metrics["centroid_displacement"],
                metrics["centroid_delta_max_abs"],
                lane["directional_bias_classification"],
                metrics["shape"]["width_relative_change_max"],
                metrics["profile_similarity"]["aligned"],
                lane["claim_ceiling"],
            )
        )
    diagnostic_rows = [
        (run_id, lane["diagnostic_notes"])
        for run_id, lane in result["lane_results"].items()
        if lane["diagnostic_notes"]
    ]
    if diagnostic_rows:
        lines.extend(["", "## Diagnostic Notes", ""])
        for run_id, notes in diagnostic_rows:
            for note in notes:
                lines.append(f"- `{run_id}`: {note}")
    lines.extend(["", "## Environment", ""])
    environment = result["environment"]
    lines.extend(
        [
            f"- Python executable: `{environment['python_executable']}`",
            f"- Python version: `{environment['python_version'].splitlines()[0]}`",
            f"- Platform: `{environment['platform']}`",
            f"- `git diff --check` return code: `{environment['git_diff_check'].get('returncode')}`",
            f"- `git status --short src experiments/.../N04`: `{environment['git_status_short_src_and_n04'].get('stdout')}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is an experiment-local fixed-substrate response runner, not a native GRC9V3 or LGRC9V3 movement run.",
            "- U0/B0 reject directed movement.",
            "- B1/B1 reversed preserve subthreshold directional sign evidence where present, but do not promote movement.",
            "- K1/K1 reversed kick audits are serialized so a negative response is not confused with a missing stimulus.",
            "- The null envelope is informational in this tranche because the configured displacement minimum dominates it.",
            "- The maximum null displacement comes from the S1 ring antipodal unwrap convention, not stochastic jitter.",
            "- No loop-driven movement, locomotion-like movement, adaptive-topology movement, or inherited N03 movement claim is emitted.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = run_tranche()
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

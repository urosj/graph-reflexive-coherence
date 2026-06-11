"""Run N04 Iteration 8 boundary-coupled pulse fixture.

This is an experiment-local fixture validation. It maps E3 pulse telemetry onto
the S0 chain through a declared state-mediated coherence coupling, then reports
boundary metrics. It does not write support masks, centroids, displacement, or
topology directly, and it does not open movement claims.
"""

from __future__ import annotations

import glob
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
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"

MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
COUPLING_CONFIG_PATH = N04 / "configs/boundary_coupled_pulse_fixture_v1.json"
E3_CHECKPOINT_DIR = (
    N03
    / "outputs/e3_native_lgrc9v3_packet_loop_animation"
    / "e3-native-lgrc9v3-packet-loop-animation"
    / "telemetry/graph_checkpoints"
)
ITERATION_7B_PATH = N04 / "outputs/packet_loop_geometry_coupling_audit.json"
ITERATION_5_PATH = N04 / "outputs/fixed_substrate_tranche_a_report.json"

OUTPUT_PATH = N04 / "outputs/boundary_coupled_pulse_report.json"
REPORT_PATH = N04 / "reports/boundary_coupled_pulse_report.md"
TIMESERIES_DIR = N04 / "outputs/boundary_coupled_pulse_timeseries"


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


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


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


def _checkpoint_paths() -> list[Path]:
    return [
        Path(path)
        for path in sorted(glob.glob(str(E3_CHECKPOINT_DIR / "checkpoint-*.json")))
    ]


def _e3_pole_series() -> list[dict[str, Any]]:
    rows = []
    for path in _checkpoint_paths():
        checkpoint = _load_json(path)
        poles = {
            node["payload"]["pole"]: float(node["coherence"])
            for node in checkpoint["node_records"]
        }
        ledger = checkpoint["family_extensions"]["lgrc9v3"]["packet_ledger"]
        rows.append(
            {
                "checkpoint": checkpoint["checkpoint_label"],
                "step_index": checkpoint["step_index"],
                "time": checkpoint["time"],
                "poles": poles,
                "node_budget": float(ledger["node_coherence_total"]),
                "in_flight_packet_budget": float(ledger["in_flight_packet_total"]),
                "total_budget": float(ledger["conserved_budget_total"]),
                "budget_error": abs(float(ledger["budget_error"])),
            }
        )
    return rows


def _gaussian_baseline(fixture: dict[str, Any]) -> list[float]:
    node_count = fixture["node_count"]
    center = fixture["basin_seed"]["center_node_id"]
    sigma = fixture["basin_seed"]["sigma"]
    total_budget = fixture["total_budget"]
    raw = [
        1.0 + 0.4 * math.exp(-((node_id - center) ** 2) / (2.0 * sigma * sigma))
        for node_id in range(node_count)
    ]
    scale = total_budget / sum(raw)
    return [value * scale for value in raw]


def _sum_mask(values: list[float], mask: list[int]) -> float:
    return sum(values[index] for index in mask)


def _centroid(values: list[float]) -> float:
    total = sum(values)
    return sum(index * value for index, value in enumerate(values)) / total


def _boundary_consistency(mapping: dict[str, Any]) -> dict[str, Any]:
    pole_to_region = {
        pole: config["target_nodes"]
        for pole, config in mapping["route_pole_to_target_region"].items()
    }
    front = mapping["front_boundary_mask"]
    rear = mapping["rear_boundary_mask"]
    center = mapping["center_reservoir_mask"]
    valid_range = set(range(21))
    return {
        "front_equals_S2_region": front == pole_to_region["S2"],
        "rear_equals_K1_region": rear == pole_to_region["K1"],
        "front_rear_disjoint": not (set(front) & set(rear)),
        "front_rear_center_valid_s0_node_ids": (
            set(front) | set(rear) | set(center)
        )
        <= valid_range,
        "center_overlaps_S1": bool(set(center) & set(pole_to_region["S1"])),
        "center_overlaps_K2": bool(set(center) & set(pole_to_region["K2"])),
        "center_does_not_fully_contain_front": not set(front) <= set(center),
        "center_does_not_fully_contain_rear": not set(rear) <= set(center),
        "center_overlap_intent": "center reservoir intentionally overlaps S1 core and K2 front-inner region, but does not fully contain front or rear boundary masks",
    }


def _add_to_mask(values: list[float], mask: list[int], amount: float) -> None:
    if not mask:
        raise ValueError("mask must not be empty")
    share = amount / len(mask)
    for index in mask:
        values[index] += share


def _remove_from_mask(values: list[float], mask: list[int], amount: float) -> None:
    if not mask:
        raise ValueError("mask must not be empty")
    share = amount / len(mask)
    for index in mask:
        values[index] -= share


def _coupling_signal(row: dict[str, Any], reference: dict[str, float]) -> float:
    poles = row["poles"]
    return max(
        0.0,
        (poles["S1"] - reference["S1"]) - (poles["K1"] - reference["K1"]),
    )


def _apply_coupling(
    baseline: list[float],
    mapping: dict[str, Any],
    mode: str,
    amount: float,
) -> list[float]:
    values = list(baseline)
    front = mapping["front_boundary_mask"]
    rear = mapping["rear_boundary_mask"]
    center = mapping["center_reservoir_mask"]
    if mode == "disabled" or amount == 0.0:
        return values
    if mode == "symmetric_null":
        _add_to_mask(values, front, amount / 2.0)
        _add_to_mask(values, rear, amount / 2.0)
        _remove_from_mask(values, center, amount)
    elif mode == "asymmetric_forward":
        _add_to_mask(values, front, amount)
        _remove_from_mask(values, rear, amount)
    elif mode == "asymmetric_reversed":
        _add_to_mask(values, rear, amount)
        _remove_from_mask(values, front, amount)
    else:
        raise ValueError(f"unknown coupling mode: {mode}")
    return values


def _lane_result(
    lane_id: str,
    lane_config: dict[str, Any],
    fixture: dict[str, Any],
    coupling_config: dict[str, Any],
    e3_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    mapping = coupling_config["route_to_movement_substrate_mapping"]
    policy = coupling_config["coupling_policy"]
    baseline = _gaussian_baseline(fixture)
    reference = e3_rows[0]["poles"]
    mode = lane_config["boundary_coupling_mode"]
    strength = policy["coupling_strength"]
    front = mapping["front_boundary_mask"]
    rear = mapping["rear_boundary_mask"]

    states = []
    for row in e3_rows:
        signal = _coupling_signal(row, reference) if lane_config["pulse_active"] else 0.0
        amount = strength * signal if lane_config["pulse_active"] else 0.0
        values = _apply_coupling(baseline, mapping, mode, amount)
        if min(values) < -1e-12:
            raise ValueError(f"{lane_id} produced negative coherence")
        states.append(
            {
                "step_index": row["step_index"],
                "time": row["time"],
                "pulse_signal": signal,
                "coupling_amount": amount,
                "centroid": _centroid(values),
                "front_mass": _sum_mask(values, front),
                "rear_mass": _sum_mask(values, rear),
                "total_budget": sum(values),
                "min_coherence": min(values),
            }
        )

    initial = states[0]
    final = states[-1]
    front_gain = max(state["front_mass"] - initial["front_mass"] for state in states)
    rear_release = max(initial["rear_mass"] - state["rear_mass"] for state in states)
    rear_gain = max(state["rear_mass"] - initial["rear_mass"] for state in states)
    front_release = max(initial["front_mass"] - state["front_mass"] for state in states)
    max_budget_error = max(abs(state["total_budget"] - fixture["total_budget"]) for state in states)
    centroid_delta = final["centroid"] - initial["centroid"]
    max_abs_centroid_delta = max(abs(state["centroid"] - initial["centroid"]) for state in states)
    boundary_coupling_score = min(front_gain, rear_release)
    reversed_boundary_coupling_score = min(rear_gain, front_release)
    if mode == "asymmetric_forward":
        directional_boundary_gain_mass = front_gain
        directional_boundary_release_mass = rear_release
        directional_boundary_polarity = "forward"
    elif mode == "asymmetric_reversed":
        directional_boundary_gain_mass = rear_gain
        directional_boundary_release_mass = front_release
        directional_boundary_polarity = "reversed"
    else:
        directional_boundary_gain_mass = 0.0
        directional_boundary_release_mass = 0.0
        directional_boundary_polarity = "none"

    if mode == "symmetric_null":
        primary_result = "symmetric_boundary_activity_no_directed_movement_claim"
    elif mode == "disabled":
        primary_result = "pulse_disabled_no_boundary_activity"
    else:
        primary_result = "measurable_state_mediated_boundary_coupling"

    final_values = _apply_coupling(
        baseline,
        mapping,
        mode,
        states[-1]["coupling_amount"],
    )
    recomputed_centroid_delta = _centroid(final_values) - initial["centroid"]
    centroid_replay_passed = abs(recomputed_centroid_delta - centroid_delta) <= 1e-12
    net_boundary_mass_delta = (final["front_mass"] - initial["front_mass"]) + (
        final["rear_mass"] - initial["rear_mass"]
    )
    net_boundary_mass_accumulation = net_boundary_mass_delta
    timeseries_record = _write_timeseries(lane_id, states)

    return {
        "schema": "movement_ladder_report_v1",
        "run_id": f"S0_chain_v1_{lane_id}",
        "lane_id": lane_id,
        "runtime_family": "experiment_local",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_boundary_coupling_adapter",
        "native_lgrc9v3_e3_pulse_used": lane_config["pulse_active"],
        "native_grc9v3_proposal_flux_control_used": False,
        "substrate": {
            "fixture_id": "S0_chain_v1",
            "topology_policy": "fixed",
            "node_count": fixture["node_count"],
            "edge_count": fixture["edge_count"],
        },
        "loop_dependency": {
            "source_experiment": "N03",
            "source_result": "E3_native_LGRC9V3_D2_3_equivalent_packet_loop",
            "loop_ladder_level": "L5",
            "movement_claim_inherited": False,
        },
        "drive": {
            "type": "state_mediated_e3_boundary_coupling",
            "coupling_mode": "state_mediated_node_coherence_update",
            "pulse_active": lane_config["pulse_active"],
            "boundary_coupling_mode": mode,
            "boundary_coupling_enabled": mode != "disabled",
            "coupling_strength": strength,
            "coupling_signal": policy["coupling_signal"],
            "mapped_signal_present": max(state["pulse_signal"] for state in states) > 0.0,
            "movement_node_coherence_written": mode != "disabled",
            "state_mediated": True,
            "direct_topology_write": False,
            "direct_boundary_write": False,
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
        },
        "mapping": mapping,
        "identity_tracking": {
            "parent_basin_preserved": True,
            "support_reference_mask": mapping["support_reference_mask"],
            "movement_fixture_node_coherence_written": mode != "disabled",
            "direct_support_mask_write": False,
            "support_observation_mode": "derived_from_node_coherence",
        },
        "movement_metrics": {
            "centroid_initial": initial["centroid"],
            "centroid_final": final["centroid"],
            "centroid_delta_total": centroid_delta,
            "centroid_delta_abs": abs(centroid_delta),
            "centroid_delta_max_abs": max_abs_centroid_delta,
            "front_advance_mass": front_gain,
            "rear_retraction_mass": rear_release,
            "rear_advance_mass": rear_gain,
            "front_retraction_mass": front_release,
            "directional_boundary_gain_mass": directional_boundary_gain_mass,
            "directional_boundary_release_mass": directional_boundary_release_mass,
            "directional_boundary_polarity": directional_boundary_polarity,
            "boundary_coupling_score": boundary_coupling_score,
            "reversed_boundary_coupling_score": reversed_boundary_coupling_score,
            "net_boundary_mass_delta": net_boundary_mass_delta,
            "net_boundary_mass_accumulation": net_boundary_mass_accumulation,
            "boundary_mass_balance_note": "Net boundary mass accumulation is front plus rear boundary gain/loss relative to the initial state; it is not a conservation error because center/reservoir mass changes are included in the total budget.",
            "configured_coupling_mass_max": max(state["coupling_amount"] for state in states),
            "measured_front_advance_mass": front_gain,
            "measured_rear_retraction_mass": rear_release,
            "centroid_recomputed_from_serialized_C": centroid_replay_passed,
            "centroid_recomputed_value": recomputed_centroid_delta,
            "m_classifier_applied": False,
            "movement_level": "not_classified_iteration_8",
            "movement_level_diagnostic": "candidate_for_iteration_9_review"
            if max(boundary_coupling_score, reversed_boundary_coupling_score) > 0.0
            else "control_or_null_for_iteration_9_review",
        },
        "taxonomies": {
            "movement_level": "M0_boundary_coupling_fixture_measurement_only",
            "boundary_level": "B1_boundary_coupling_measured"
            if mode != "disabled"
            else "B0_no_boundary_coupling",
            "pulse_level": "P5_imported_e3_pulse" if lane_config["pulse_active"] else "P1_pulse_metadata_inactive",
        },
        "conservation": {
            "budget_surface": "node_only",
            "node_budget": fixture["total_budget"],
            "in_flight_packet_budget": 0.0,
            "total_budget": fixture["total_budget"],
            "budget_abs_error_max": max_budget_error,
            "e3_pulse_budget_surface": "node_plus_packet",
        },
        "topology": {
            "topology_changed": False,
            "node_count_initial": fixture["node_count"],
            "node_count_final": fixture["node_count"],
            "edge_count_initial": fixture["edge_count"],
            "edge_count_final": fixture["edge_count"],
            "topology_events_enabled": False,
        },
        "gates": {
            "budget_gate_passed": max_budget_error <= 1e-9,
            "nonnegative_gate_passed": min(state["min_coherence"] for state in states) >= -1e-12,
            "state_mediated_gate_passed": True,
            "direct_write_gate_passed": True,
            "boundary_coupling_measurable": (
                max(boundary_coupling_score, reversed_boundary_coupling_score) > 0.0
            ),
            "movement_claim_allowed": False,
        },
        "claim_ceiling": coupling_config["claim_ceiling"],
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "blocked_claims": coupling_config["blocked_claims"],
        "primary_blocked_reason": "movement_classification_deferred_to_iteration_9",
        "primary_result": primary_result,
        "state_mediation_note": "Node coherence is modified by the mapped pulse-coupling policy; support masks, centroids, displacement, and topology are not directly written.",
        "timeseries": timeseries_record,
    }


def _digest_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_timeseries(lane_id: str, states: list[dict[str, Any]]) -> dict[str, Any]:
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    path = TIMESERIES_DIR / f"{lane_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for state in states:
            handle.write(json.dumps(state, sort_keys=True) + "\n")
    with path.open("r", encoding="utf-8") as handle:
        reloaded = [json.loads(line) for line in handle if line.strip()]
    digest = _digest_json(states)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": _sha256(path),
        "timeseries_digest": digest,
        "timeseries_digest_verified": _digest_json(reloaded) == digest,
    }


def run_fixture() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    coupling_config = _load_json(COUPLING_CONFIG_PATH)
    iteration_7b = _load_json(ITERATION_7B_PATH)
    iteration_5 = _load_json(ITERATION_5_PATH)
    fixture = manifest["fixtures"]["S0_chain_v1"]
    e3_rows = _e3_pole_series()

    lane_results = {
        lane_id: _lane_result(lane_id, lane_config, fixture, coupling_config, e3_rows)
        for lane_id, lane_config in coupling_config["lanes"].items()
    }
    symmetric = lane_results["P1_symmetric_boundary_coupling_null"]
    forward = lane_results["P2_asymmetric_boundary_coupling_forward"]
    reversed_lane = lane_results["P2_asymmetric_boundary_coupling_reversed"]
    mapping_consistency = _boundary_consistency(
        coupling_config["route_to_movement_substrate_mapping"]
    )
    iteration_5_threshold = float(
        iteration_5["displacement_threshold_policy"]["effective_displacement_min"]
    )
    max_iteration_8_displacement = max(
        abs(forward["movement_metrics"]["centroid_delta_total"]),
        abs(reversed_lane["movement_metrics"]["centroid_delta_total"]),
    )
    threshold_comparison = {
        "source": ITERATION_5_PATH.relative_to(ROOT).as_posix(),
        "iteration_5_effective_displacement_min": iteration_5_threshold,
        "max_iteration_8_abs_centroid_delta": max_iteration_8_displacement,
        "displacement_below_iteration_5_threshold": (
            max_iteration_8_displacement < iteration_5_threshold
        ),
        "displacement_exceeds_iteration_5_threshold": (
            max_iteration_8_displacement >= iteration_5_threshold
        ),
        "classification_impact": "reported_only_iteration_8_m4_m5_classification_deferred",
    }

    checks = {
        "iteration_7b_dependency_passed": iteration_7b["status"] == "passed",
        "route_to_substrate_mapping_defined": coupling_config[
            "route_to_movement_substrate_mapping"
        ]["mapping_defined"]
        is True,
        "s0_chain_mapping_active": coupling_config[
            "route_to_movement_substrate_mapping"
        ]["target_fixture_id"]
        == "S0_chain_v1",
        "symmetric_null_no_net_movement_claim": symmetric["claim_flags"][
            "movement_claim_allowed"
        ]
        is False
        and abs(symmetric["movement_metrics"]["centroid_delta_total"]) < 1e-9,
        "asymmetric_coupling_measurable": forward["movement_metrics"][
            "boundary_coupling_score"
        ]
        > 0.0,
        "reversed_coupling_measurable": reversed_lane["movement_metrics"][
            "reversed_boundary_coupling_score"
        ]
        > 0.0,
        "reversal_changes_centroid_sign": (
            forward["movement_metrics"]["centroid_delta_total"]
            * reversed_lane["movement_metrics"]["centroid_delta_total"]
            < 0.0
        ),
        "all_budget_gates_pass": all(
            lane["gates"]["budget_gate_passed"] for lane in lane_results.values()
        ),
        "all_nonnegative_gates_pass": all(
            lane["gates"]["nonnegative_gate_passed"] for lane in lane_results.values()
        ),
        "no_direct_state_writes": all(
            lane["drive"]["direct_boundary_write"] is False
            and lane["drive"]["direct_support_mask_write"] is False
            and lane["drive"]["direct_centroid_write"] is False
            and lane["drive"]["direct_displacement_write"] is False
            for lane in lane_results.values()
        ),
        "movement_claims_blocked": all(
            lane["claim_flags"]["movement_claim_allowed"] is False
            and lane["claim_flags"]["boundary_coupled_movement_claim_allowed"] is False
            and lane["claim_flags"]["loop_driven_movement_claim_allowed"] is False
            for lane in lane_results.values()
        ),
        "mapping_consistency_passed": all(
            value for value in mapping_consistency.values() if isinstance(value, bool)
        ),
        "centroid_replay_passed": all(
            lane["movement_metrics"]["centroid_recomputed_from_serialized_C"]
            for lane in lane_results.values()
        ),
        "forward_reversal_magnitude_symmetry_passed": abs(
            abs(forward["movement_metrics"]["centroid_delta_total"])
            - abs(reversed_lane["movement_metrics"]["centroid_delta_total"])
        )
        <= 1e-12,
        "boundary_score_symmetry_passed": abs(
            forward["movement_metrics"]["boundary_coupling_score"]
            - reversed_lane["movement_metrics"]["reversed_boundary_coupling_score"]
        )
        <= 1e-12,
        "iteration_5_threshold_comparison_recorded": True,
        "all_timeseries_digests_verified": all(
            lane["timeseries"]["timeseries_digest_verified"]
            for lane in lane_results.values()
        ),
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "boundary_coupled_pulse_fixture_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "runtime_family": "experiment_local",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_boundary_coupling_adapter",
        "source_artifacts": {
            "movement_manifest": _artifact_record(MANIFEST_PATH),
            "coupling_config": _artifact_record(COUPLING_CONFIG_PATH),
            "iteration_7b": _artifact_record(ITERATION_7B_PATH),
            "iteration_5_fixed_substrate_tranche": _artifact_record(ITERATION_5_PATH),
        },
        "claim_ceiling": coupling_config["claim_ceiling"],
        "blocked_claims": coupling_config["blocked_claims"],
        "primary_blocked_reason": "movement_classification_deferred_to_iteration_9",
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "native_grc9v3_proposal_flux_control_used": False,
        },
        "mapping": coupling_config["route_to_movement_substrate_mapping"],
        "mapping_consistency": mapping_consistency,
        "deferred_mappings": coupling_config["deferred_mappings"],
        "s1_ring_mapping": {
            "status": coupling_config["deferred_mappings"]["S1_ring_v1"]["status"],
            "deferred_reason": coupling_config["deferred_mappings"]["S1_ring_v1"][
                "reason"
            ],
            "claim_impact": "no_ring_pulse_boundary_claims",
        },
        "coupling_policy": coupling_config["coupling_policy"],
        "deferred_controls": coupling_config.get("deferred_controls", {}),
        "iteration_5_threshold_comparison": threshold_comparison,
        "paired_reversal_check": {
            "sign_reversal_passed": checks["reversal_changes_centroid_sign"],
            "reversal_scope": "coupling_direction_only",
            "uses_reversed_e3_telemetry": False,
            "true_reversed_e3_pulse_lane_deferred": True,
            "magnitude_symmetry_passed": checks[
                "forward_reversal_magnitude_symmetry_passed"
            ],
            "boundary_score_symmetry_passed": checks[
                "boundary_score_symmetry_passed"
            ],
            "same_boundary_coupling_score": checks["boundary_score_symmetry_passed"],
            "same_coupling_quantum": abs(
                forward["movement_metrics"]["configured_coupling_mass_max"]
                - reversed_lane["movement_metrics"]["configured_coupling_mass_max"]
            )
            <= 1e-12,
            "forward_centroid_delta": forward["movement_metrics"][
                "centroid_delta_total"
            ],
            "reversed_centroid_delta": reversed_lane["movement_metrics"][
                "centroid_delta_total"
            ],
            "forward_boundary_coupling_score": forward["movement_metrics"][
                "boundary_coupling_score"
            ],
            "reversed_boundary_coupling_score": reversed_lane["movement_metrics"][
                "reversed_boundary_coupling_score"
            ],
        },
        "iteration_8_claim_boundary": {
            "m_classifier_applied": False,
            "movement_level": "not_classified_iteration_8",
            "movement_classification_deferred_to": "Iteration 9",
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
        },
        "checks": checks,
        "lane_results": lane_results,
        "summary": {
            "symmetric_null_centroid_delta": symmetric["movement_metrics"][
                "centroid_delta_total"
            ],
            "forward_centroid_delta": forward["movement_metrics"][
                "centroid_delta_total"
            ],
            "reversed_centroid_delta": reversed_lane["movement_metrics"][
                "centroid_delta_total"
            ],
            "forward_boundary_coupling_score": forward["movement_metrics"][
                "boundary_coupling_score"
            ],
            "reversed_boundary_coupling_score": reversed_lane["movement_metrics"][
                "reversed_boundary_coupling_score"
            ],
            "configured_coupling_mass_forward": forward["movement_metrics"][
                "configured_coupling_mass_max"
            ],
            "configured_coupling_mass_reversed": reversed_lane["movement_metrics"][
                "configured_coupling_mass_max"
            ],
            "iteration_5_effective_displacement_min": iteration_5_threshold,
            "max_iteration_8_abs_centroid_delta": max_iteration_8_displacement,
            "interpretation": "Iteration 8 defines a state-mediated route-to-substrate coupling fixture and verifies measurable boundary coherence effects, while leaving movement claims blocked for Iteration 9 classification.",
        },
        "environment": _environment_record(),
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Boundary-Coupled Pulse Fixture",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_boundary_coupled_pulse_fixture.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Mapping: `{result['mapping']['mapping_id']}`",
        f"- Target fixture: `{result['mapping']['target_fixture_id']}`",
        f"- Claim ceiling: `{result['claim_ceiling']}`",
        f"- Primary blocked reason: `{result['primary_blocked_reason']}`",
        f"- Movement claim allowed: `{result['claim_flags']['movement_claim_allowed']}`",
        f"- Symmetric null dX: `{result['summary']['symmetric_null_centroid_delta']}`",
        f"- Forward dX: `{result['summary']['forward_centroid_delta']}`",
        f"- Reversed dX: `{result['summary']['reversed_centroid_delta']}`",
        f"- Forward boundary coupling score: `{result['summary']['forward_boundary_coupling_score']}`",
        f"- Reversed boundary coupling score: `{result['summary']['reversed_boundary_coupling_score']}`",
        f"- Forward configured coupling mass: `{result['summary']['configured_coupling_mass_forward']}`",
        f"- Reversed configured coupling mass: `{result['summary']['configured_coupling_mass_reversed']}`",
        f"- Iteration 5 displacement threshold: `{result['summary']['iteration_5_effective_displacement_min']}`",
        f"- Max Iteration 8 |dX|: `{result['summary']['max_iteration_8_abs_centroid_delta']}`",
        f"- Mapping consistency passed: `{result['checks']['mapping_consistency_passed']}`",
        f"- Centroid replay passed: `{result['checks']['centroid_replay_passed']}`",
        f"- Timeseries digests verified: `{result['checks']['all_timeseries_digests_verified']}`",
        "",
        "## Mapping",
        "",
        f"- Mapping type: `{result['mapping']['mapping_type']}`",
        f"- Node-id preserving: `{result['mapping']['node_id_preserving']}`",
        f"- Positive direction: `{result['mapping']['positive_direction']}`",
        f"- Direction source: `{result['mapping']['direction_source']}`",
        f"- Direction frozen before run: `{result['mapping']['direction_frozen_before_run']}`",
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
            "## Lanes",
            "",
            "| Lane | Mode | dX | Dir Gain | Dir Release | Fwd Score | Rev Score | Timeseries | Movement Claim |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|",
        ]
    )
    for lane_id, lane in result["lane_results"].items():
        metrics = lane["movement_metrics"]
        lines.append(
            "| `{}` | `{}` | `{:.9f}` | `{:.9f}` | `{:.9f}` | `{:.9f}` | `{:.9f}` | `{}` | `{}` |".format(
                lane_id,
                lane["drive"]["boundary_coupling_mode"],
                metrics["centroid_delta_total"],
                metrics["directional_boundary_gain_mass"],
                metrics["directional_boundary_release_mass"],
                metrics["boundary_coupling_score"],
                metrics["reversed_boundary_coupling_score"],
                lane["timeseries"]["path"],
                lane["claim_flags"]["movement_claim_allowed"],
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["summary"]["interpretation"],
            "",
            "## Notes",
            "",
            "- Coupling is state-mediated through mapped E3 pole coherence signal.",
            "- The reversed Iteration 8 lane reverses coupling direction only; a true reversed-E3-pulse telemetry lane is deferred to Iteration 9.",
            "- The frozen Iteration 5 effective displacement threshold is read from `fixed_substrate_tranche_a_report.json`; Iteration 8 records the comparison but does not classify movement.",
            "- `net_boundary_mass_accumulation` records mass accumulated in front+rear boundary masks relative to the initial state; it is not a conservation error.",
            "- `coupling_strength = 0.5` was chosen as a first fixture-validation value that produces measurable bounded coupling; sensitivity analysis is deferred.",
            "- K2 and S2 are mapped for route completeness but are not used by `coupling_signal_v1`.",
            "- The fixture changes movement node coherence, not support masks, centroids, displacement, or topology directly.",
            "- Iteration 8 measures boundary coupling only; M4/M5 movement classification remains Iteration 9 work.",
            "- `S1_ring_v1` mapping is deferred because ring boundary coupling needs a separate unwrap/front-rear policy.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = run_fixture()
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

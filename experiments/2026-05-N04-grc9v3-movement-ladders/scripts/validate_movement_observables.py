"""Validate N04 movement observables on synthetic traces.

Iteration 4 defines observable behavior only. It does not execute a movement
runner and does not claim movement from N03/E3. Synthetic traces are used to
verify that metrics distinguish no movement, coherent shift, smeared shift,
identity replacement, budget failure, topology failure, and ring wrap artifacts.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
INITIALIZER_PATH = N04 / "outputs/movement_initializer_validation.json"
OUTPUT_PATH = N04 / "outputs/movement_observables_validation.json"
REPORT_PATH = N04 / "reports/movement_observables_validation.md"
TIMESERIES_DIR = N04 / "outputs/movement_observables_timeseries"
PROFILE_ALIGNMENT_MAX_SHIFT = 6
IDENTITY_ALIGNMENT_MAX_SHIFT = 3
IDENTITY_CANDIDATE_MIN = 0.50
MOVEMENT_COST_DISPLACEMENT_EPSILON = 1e-12


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


def _node_values(lane_result: dict[str, Any], node_count: int) -> list[float]:
    values_by_node = lane_result["coherence_by_node"]
    return [float(values_by_node[str(index)]) for index in range(node_count)]


def _signed_distance(fixture: dict[str, Any], node_id: int, center: float) -> float:
    node_count = int(fixture["node_count"])
    if fixture["type"] == "ring":
        return float(((node_id - center + node_count / 2) % node_count) - node_count / 2)
    return float(node_id - center)


def _project_nonnegative_simplex(values: list[float], total: float) -> list[float]:
    sorted_values = sorted(values, reverse=True)
    cumulative = 0.0
    rho = -1
    for index, value in enumerate(sorted_values, start=1):
        cumulative += value
        theta = (cumulative - total) / index
        if value - theta > 0.0:
            rho = index
    if rho < 1:
        return [total / len(values) for _ in values]
    theta = (sum(sorted_values[:rho]) - total) / rho
    return [max(value - theta, 0.0) for value in values]


def _centroid(fixture: dict[str, Any], values: list[float], reference_center: float) -> float:
    total = sum(values)
    if fixture["type"] == "ring":
        return reference_center + sum(
            _signed_distance(fixture, index, reference_center) * value
            for index, value in enumerate(values)
        ) / total
    return sum(float(index) * value for index, value in enumerate(values)) / total


def _width(fixture: dict[str, Any], values: list[float], centroid: float) -> float:
    total = sum(values)
    variance = sum(
        (_signed_distance(fixture, index, centroid) ** 2) * value
        for index, value in enumerate(values)
    ) / total
    return math.sqrt(max(variance, 0.0))


def _support(values: list[float]) -> list[int]:
    mean = sum(values) / len(values)
    maximum = max(values)
    threshold = mean + 0.10 * (maximum - mean)
    return [index for index, value in enumerate(values) if value >= threshold]


def _boundary_nodes(fixture: dict[str, Any], support: list[int]) -> list[int]:
    support_set = set(support)
    node_count = int(fixture["node_count"])
    boundary = []
    for node in support:
        if fixture["type"] == "ring":
            neighbors = {(node - 1) % node_count, (node + 1) % node_count}
        else:
            neighbors = set()
            if node > 0:
                neighbors.add(node - 1)
            if node < node_count - 1:
                neighbors.add(node + 1)
        if any(neighbor not in support_set for neighbor in neighbors):
            boundary.append(node)
    return sorted(boundary)


def _front_rear_masks(
    fixture: dict[str, Any],
    boundary: list[int],
    centroid: float,
    direction: float,
) -> dict[str, list[int]]:
    front = []
    rear = []
    for node in boundary:
        projected = _signed_distance(fixture, node, centroid) * direction
        if projected > 0.0:
            front.append(node)
        elif projected < 0.0:
            rear.append(node)
    return {"front": sorted(front), "rear": sorted(rear)}


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    da = [value - mean_a for value in a]
    db = [value - mean_b for value in b]
    denom = math.sqrt(sum(value * value for value in da) * sum(value * value for value in db))
    if denom == 0.0:
        return 1.0 if all(abs(x - y) < 1e-12 for x, y in zip(a, b)) else 0.0
    return sum(x * y for x, y in zip(da, db)) / denom


def _shift_discrete(values: list[float], shift: int, ring: bool) -> list[float]:
    count = len(values)
    if shift == 0:
        return list(values)
    if ring:
        return [values[(index - shift) % count] for index in range(count)]
    edge_fill = min(values)
    shifted = []
    for index in range(count):
        source = index - shift
        shifted.append(values[source] if 0 <= source < count else edge_fill)
    return shifted


def _aligned_profile_similarity(
    fixture: dict[str, Any], initial: list[float], final: list[float]
) -> float:
    max_shift = min(PROFILE_ALIGNMENT_MAX_SHIFT, len(initial) // 2)
    ring = fixture["type"] == "ring"
    return max(
        _pearson(initial, _shift_discrete(final, shift, ring))
        for shift in range(-max_shift, max_shift + 1)
    )


def _curvature_proxy(values: list[float], node: int, ring: bool) -> float:
    count = len(values)
    if ring:
        left = values[(node - 1) % count]
        right = values[(node + 1) % count]
    else:
        left = values[node - 1] if node > 0 else values[node]
        right = values[node + 1] if node < count - 1 else values[node]
    return right - 2.0 * values[node] + left


def _curvature_summary(
    fixture: dict[str, Any],
    values: list[float],
    masks: dict[str, list[int]],
) -> dict[str, float]:
    ring = fixture["type"] == "ring"
    front_trace = sum(_curvature_proxy(values, node, ring) for node in masks["front"])
    rear_trace = sum(_curvature_proxy(values, node, ring) for node in masks["rear"])
    return {
        "front_trace": front_trace,
        "rear_trace": rear_trace,
        "front_rear_trace_delta": abs(front_trace - rear_trace),
    }


def _move_cost(initial: list[float], final: list[float]) -> float:
    return sum(abs(after - before) for before, after in zip(initial, final))


def _translate_profile(fixture: dict[str, Any], values: list[float], delta: int) -> list[float]:
    shifted = _shift_discrete(values, delta, fixture["type"] == "ring")
    return _project_nonnegative_simplex(shifted, sum(values))


def _smear_profile(values: list[float], total: float) -> list[float]:
    uniform = total / len(values)
    return [uniform for _ in values]


def _support_overlap_ratio(initial: list[int], current: list[int]) -> float:
    if not initial:
        return 0.0
    return len(set(initial) & set(current)) / len(set(initial))


def _shift_support(support: list[int], shift: int, node_count: int, ring: bool) -> list[int]:
    shifted = []
    for node in support:
        candidate = node + shift
        if ring:
            shifted.append(candidate % node_count)
        elif 0 <= candidate < node_count:
            shifted.append(candidate)
    return sorted(shifted)


def _aligned_support_overlap_ratio(
    fixture: dict[str, Any], initial: list[int], current: list[int]
) -> float:
    if not initial:
        return 0.0
    node_count = int(fixture["node_count"])
    ring = fixture["type"] == "ring"
    return max(
        _support_overlap_ratio(_shift_support(initial, shift, node_count, ring), current)
        for shift in range(-IDENTITY_ALIGNMENT_MAX_SHIFT, IDENTITY_ALIGNMENT_MAX_SHIFT + 1)
    )


def _boundary_flip_summary(
    fixture: dict[str, Any],
    initial: list[float],
    final: list[float],
    direction: float,
    initial_centroid: float,
) -> dict[str, Any]:
    initial_support = _support(initial)
    final_support = _support(final)
    entered = sorted(set(final_support) - set(initial_support))
    left = sorted(set(initial_support) - set(final_support))
    front_entered = []
    rear_entered = []
    front_left = []
    rear_left = []
    for node in entered:
        projected = _signed_distance(fixture, node, initial_centroid) * direction
        if projected >= 0.0:
            front_entered.append(node)
        else:
            rear_entered.append(node)
    for node in left:
        projected = _signed_distance(fixture, node, initial_centroid) * direction
        if projected >= 0.0:
            front_left.append(node)
        else:
            rear_left.append(node)
    return {
        "entered_support_count": len(entered),
        "left_support_count": len(left),
        "entered_support_nodes": entered,
        "left_support_nodes": left,
        "front_entered_nodes": front_entered,
        "rear_entered_nodes": rear_entered,
        "front_left_nodes": front_left,
        "rear_left_nodes": rear_left,
        "front_entered_mass": sum(final[node] for node in front_entered),
        "rear_entered_mass": sum(final[node] for node in rear_entered),
        "front_left_mass": sum(initial[node] for node in front_left),
        "rear_left_mass": sum(initial[node] for node in rear_left),
    }


def _frame_observables(
    fixture: dict[str, Any], states: list[list[float]], direction: float
) -> dict[str, Any]:
    reference_center = float(fixture["basin_seed"]["center_node_id"])
    centroid_t = [_centroid(fixture, state, reference_center) for state in states]
    support_t = [_support(state) for state in states]
    boundary_t = [_boundary_nodes(fixture, support) for support in support_t]
    width_t = [_width(fixture, state, centroid) for state, centroid in zip(states, centroid_t)]
    mass_t = [sum(state) for state in states]
    initial_support = support_t[0]
    overlap_t = [
        _aligned_support_overlap_ratio(fixture, initial_support, support) for support in support_t
    ]
    step_delta_t = [
        centroid_t[index + 1] - centroid_t[index] for index in range(len(centroid_t) - 1)
    ]
    return {
        "centroid_t": centroid_t,
        "support_t": support_t,
        "boundary_t": boundary_t,
        "width_t": width_t,
        "mass_t": mass_t,
        "overlap_t": overlap_t,
        "step_delta_t": step_delta_t,
        "front_rear_masks_t": [
            _front_rear_masks(fixture, boundary, centroid, direction)
            for boundary, centroid in zip(boundary_t, centroid_t)
        ],
    }


def _observables(
    fixture: dict[str, Any],
    states: list[list[float]],
    direction: float,
    *,
    direction_source: str,
    identity_gate_min: float,
    topology_changed: bool = False,
) -> dict[str, Any]:
    initial = states[0]
    final = states[-1]
    frames = _frame_observables(fixture, states, direction)
    displacement = frames["centroid_t"][-1] - frames["centroid_t"][0]
    width_relative_change_max = max(
        abs(width - frames["width_t"][0]) / max(frames["width_t"][0], 1e-12)
        for width in frames["width_t"]
    )
    profile_raw = _pearson(initial, final)
    profile_aligned = _aligned_profile_similarity(fixture, initial, final)
    masks = frames["front_rear_masks_t"][-1]
    curvature = _curvature_summary(fixture, final, masks)
    budget_initial = frames["mass_t"][0]
    budget_error_t = [abs(mass - budget_initial) for mass in frames["mass_t"]]
    identity_mass_ratio_min = min(frames["overlap_t"])
    if identity_mass_ratio_min >= identity_gate_min:
        identity_level = "I2_gate_passed"
    elif identity_mass_ratio_min >= IDENTITY_CANDIDATE_MIN:
        identity_level = "I1_candidate_continuity"
    else:
        identity_level = "I0_identity_lost"
    movement_load = _move_cost(initial, final)
    displacement_abs = abs(displacement)
    topology = {
        "topology_events_enabled": False,
        "initial_node_count": fixture["node_count"],
        "final_node_count": fixture["node_count"],
        "initial_edge_count": fixture["edge_count"],
        "final_edge_count": fixture["edge_count"],
        "topology_event_count": 1 if topology_changed else 0,
        "topology_changed": topology_changed,
    }
    return {
        "centroid": {
            "x_t": frames["centroid_t"],
            "delta_x_total": displacement,
            "delta_x_abs": abs(displacement),
            "max_step_delta": max((abs(value) for value in frames["step_delta_t"]), default=0.0),
            "coordinate_frame": fixture["coordinate_policy"]["centroid_coordinate_frame"],
        },
        "support_tracking": {
            "support_mask_t": frames["support_t"],
            "overlap_t": frames["overlap_t"],
            "mutual_best_match": identity_mass_ratio_min >= IDENTITY_CANDIDATE_MIN,
            "identity_mass_ratio_min": identity_mass_ratio_min,
            "identity_continuity_level": identity_level,
            "identity_candidate_min": IDENTITY_CANDIDATE_MIN,
            "identity_gate_min": identity_gate_min,
            "alignment_max_shift": IDENTITY_ALIGNMENT_MAX_SHIFT,
            "threshold_policy": "mean_plus_0.10_of_peak_excess",
            "tie_breaking_policy": "node_id_order",
        },
        "boundary_flips": _boundary_flip_summary(
            fixture, initial, final, direction, frames["centroid_t"][0]
        ),
        "boundary_flip_count": len(set(frames["support_t"][0]).symmetric_difference(frames["support_t"][-1])),
        "front_rear_definition": {
            "direction_source": direction_source,
            "direction_vector": [direction],
            "posthoc": direction_source == "centroid_velocity",
            "claim_eligible": direction_source in {"configured", "perturbation", "packet_route"},
        },
        "front_rear_masks": masks,
        "shape": {
            "mass_t": frames["mass_t"],
            "width_t": frames["width_t"],
            "width_relative_change_max": width_relative_change_max,
            "mass_ratio_min": min(frames["mass_t"]) / max(frames["mass_t"][0], 1e-12),
        },
        "profile_similarity": {
            "alignment_policy": "centroid_aligned_discrete_shift",
            "similarity_metric": "pearson_correlation",
            "alignment_max_shift": PROFILE_ALIGNMENT_MAX_SHIFT,
            "raw": profile_raw,
            "aligned": profile_aligned,
        },
        "curvature_proxy": curvature,
        "movement_cost": {
            "redistribution_load_total": movement_load,
            "redistribution_load_per_displacement": (
                None
                if displacement_abs < MOVEMENT_COST_DISPLACEMENT_EPSILON
                else movement_load / displacement_abs
            ),
            "displacement_too_small_for_cost_ratio": (
                displacement_abs < MOVEMENT_COST_DISPLACEMENT_EPSILON
            ),
        },
        "conservation": {
            "budget_surface": "node_only",
            "budget_t": frames["mass_t"],
            "budget_initial": budget_initial,
            "budget_final": frames["mass_t"][-1],
            "budget_abs_error_max": max(budget_error_t),
        },
        "topology": topology,
    }


def _write_timeseries(
    run_id: str,
    fixture_id: str,
    states: list[list[float]],
    observables: dict[str, Any],
) -> dict[str, Any]:
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    path = TIMESERIES_DIR / f"{run_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for step, values in enumerate(states):
            handle.write(
                json.dumps(
                    {
                        "step": step,
                        "fixture_id": fixture_id,
                        "centroid": observables["centroid"]["x_t"][step],
                        "support_mask": observables["support_tracking"]["support_mask_t"][step],
                        "mass": observables["shape"]["mass_t"][step],
                        "width": observables["shape"]["width_t"][step],
                        "budget": observables["conservation"]["budget_t"][step],
                        "coherence_by_node": {
                            str(index): value for index, value in enumerate(values)
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": _sha256(path),
    }


def _uniform_jitter(values: list[float], total: float) -> list[float]:
    jittered = list(values)
    if len(jittered) >= 4:
        jittered[0] += 1e-5
        jittered[1] -= 1e-5
        jittered[-2] += 1e-5
        jittered[-1] -= 1e-5
    return _project_nonnegative_simplex(jittered, total)


def _bump_at(fixture: dict[str, Any], node_count: int, center: int, total: float) -> list[float]:
    sigma = float(fixture["basin_seed"]["sigma"])
    values = []
    for node in range(node_count):
        distance = _signed_distance(fixture, node, center)
        values.append(1.0 + 0.4 * math.exp(-(distance * distance) / (2.0 * sigma * sigma)))
    return _project_nonnegative_simplex(values, total)


def _synthetic_cases(
    fixture: dict[str, Any],
    base: list[float],
    uniform: list[float],
) -> dict[str, dict[str, Any]]:
    shifted = _translate_profile(fixture, base, 1)
    reverse_shifted = _translate_profile(fixture, base, -1)
    smeared = _smear_profile(shifted, sum(base))
    budget_drift = list(shifted)
    budget_drift[0] += 0.25
    base_center = int(fixture["basin_seed"]["center_node_id"])
    if fixture["type"] == "ring":
        far_center = (base_center + int(fixture["node_count"]) // 2) % int(fixture["node_count"])
    else:
        far_center = min(int(fixture["node_count"]) - 2, base_center + int(fixture["node_count"]) // 3)
    replacement = _bump_at(fixture, int(fixture["node_count"]), far_center, sum(base))
    cases = {
        "null_static": {
            "states": [list(base), list(base)],
            "expectations": {
                "should_move": False,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
            },
        },
        "uniform_jitter": {
            "states": [list(uniform), _uniform_jitter(uniform, sum(uniform))],
            "expectations": {
                "should_move": False,
                "should_preserve_shape": None,
                "should_preserve_budget": True,
                "should_preserve_identity": None,
                "should_preserve_topology": True,
            },
        },
        "shape_preserving_shift": {
            "states": [list(base), shifted],
            "expectations": {
                "should_move": True,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
            },
        },
        "reversed_shape_preserving_shift": {
            "states": [list(base), reverse_shifted],
            "expectations": {
                "should_move": True,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
            },
            "direction": -1.0,
        },
        "boundary_reassignment_front_gain_rear_loss": {
            "states": [list(base), shifted],
            "expectations": {
                "should_move": True,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
                "requires_front_rear_flip_signal": True,
            },
        },
        "smeared_shift": {
            "states": [list(base), smeared],
            "expectations": {
                "should_move": None,
                "should_preserve_shape": False,
                "should_preserve_budget": True,
                "should_preserve_identity": None,
                "should_preserve_topology": True,
            },
        },
        "basin_replacement": {
            "states": [list(base), replacement],
            "expectations": {
                "should_move": None,
                "should_preserve_shape": None,
                "should_preserve_budget": True,
                "should_preserve_identity": False,
                "should_preserve_topology": True,
            },
        },
        "budget_drift": {
            "states": [list(base), budget_drift],
            "expectations": {
                "should_move": None,
                "should_preserve_shape": True,
                "should_preserve_budget": False,
                "should_preserve_identity": None,
                "should_preserve_topology": True,
            },
        },
        "topology_changed_apparent_displacement": {
            "states": [list(base), shifted],
            "topology_changed": True,
            "expectations": {
                "should_move": None,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": False,
            },
        },
    }
    if fixture["type"] == "ring":
        cases["ring_wrap_forward"] = {
            "states": [
                _translate_profile(fixture, base, -2),
                _translate_profile(fixture, base, -1),
                list(base),
                shifted,
            ],
            "expectations": {
                "should_move": True,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
                "should_have_no_wrap_jump": True,
            },
        }
        cases["ring_wrap_reverse"] = {
            "states": [
                shifted,
                list(base),
                _translate_profile(fixture, base, -1),
                _translate_profile(fixture, base, -2),
            ],
            "direction": -1.0,
            "expectations": {
                "should_move": True,
                "should_preserve_shape": True,
                "should_preserve_budget": True,
                "should_preserve_identity": True,
                "should_preserve_topology": True,
                "should_have_no_wrap_jump": True,
            },
        }
    return cases


def validate_observables() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    initializer = _load_json(INITIALIZER_PATH)
    metrics = manifest["metric_defaults"]
    null_envelope = manifest["null_displacement_envelope"]
    displacement_min = max(
        float(metrics["configured_displacement_min"]),
        float(null_envelope["mean"]) + float(metrics["null_calibration_k"]) * float(null_envelope["std"]),
    )
    epsilon_budget = float(metrics["epsilon_budget"])
    width_max = float(metrics["width_relative_change_max"])
    profile_min = float(metrics["profile_similarity_min"])
    identity_min = float(metrics["identity_mass_ratio_min"])

    case_results: dict[str, Any] = {}
    for fixture_id, fixture in manifest["fixtures"].items():
        if fixture.get("status") == "deferred":
            continue
        base_lane = initializer["lane_results"][f"{fixture_id}:B0"]
        uniform_lane = initializer["lane_results"][f"{fixture_id}:U0"]
        base = _node_values(base_lane, int(fixture["node_count"]))
        uniform = _node_values(uniform_lane, int(fixture["node_count"]))
        direction = float(fixture["front_rear_definition"]["direction_vector"][0])
        for case_id, case_spec in _synthetic_cases(fixture, base, uniform).items():
            run_id = f"{fixture_id}_{case_id}"
            case_direction = direction * float(case_spec.get("direction", 1.0))
            obs = _observables(
                fixture,
                case_spec["states"],
                case_direction,
                direction_source="configured",
                identity_gate_min=identity_min,
                topology_changed=bool(case_spec.get("topology_changed", False)),
            )
            ts = _write_timeseries(run_id, fixture_id, case_spec["states"], obs)
            budget_passed = obs["conservation"]["budget_abs_error_max"] <= epsilon_budget
            displacement_passed = obs["centroid"]["delta_x_abs"] >= displacement_min
            shape_passed = (
                obs["shape"]["width_relative_change_max"] <= width_max
                and obs["profile_similarity"]["aligned"] >= profile_min
            )
            identity_passed = (
                obs["support_tracking"]["identity_mass_ratio_min"] >= identity_min
            )
            topology_passed = obs["topology"]["topology_changed"] is False
            expectations = case_spec["expectations"]
            has_front_rear_signal = (
                obs["boundary_flips"]["front_entered_mass"] > 0.0
                and obs["boundary_flips"]["rear_left_mass"] > 0.0
            )
            no_wrap_jump_passed = obs["centroid"]["max_step_delta"] < (
                int(fixture["node_count"]) / 2.0
            )
            movement_promotion_blocked = not (
                budget_passed and identity_passed and topology_passed
            )
            checks = {
                "budget_gate_matches_expectation": budget_passed
                == expectations["should_preserve_budget"],
                "movement_gate_matches_expectation": (
                    True
                    if expectations["should_move"] is None
                    else displacement_passed == expectations["should_move"]
                ),
                "shape_gate_matches_expectation": (
                    True
                    if expectations["should_preserve_shape"] is None
                    else shape_passed == expectations["should_preserve_shape"]
                ),
                "identity_gate_matches_expectation": (
                    True
                    if expectations["should_preserve_identity"] is None
                    else identity_passed == expectations["should_preserve_identity"]
                ),
                "topology_gate_matches_expectation": topology_passed
                == expectations["should_preserve_topology"],
                "front_rear_signal_matches_expectation": (
                    has_front_rear_signal
                    if expectations.get("requires_front_rear_flip_signal", False)
                    else True
                ),
                "ring_wrap_jump_gate_matches_expectation": (
                    no_wrap_jump_passed
                    if expectations.get("should_have_no_wrap_jump", False)
                    else True
                ),
                "timeseries_emitted": bool(ts["sha256"]),
            }
            case_results[run_id] = {
                "fixture_id": fixture_id,
                "case_id": case_id,
                "observables": obs,
                "gates": {
                    "budget_passed": budget_passed,
                    "displacement_passed": displacement_passed,
                    "shape_passed": shape_passed,
                    "identity_passed": identity_passed,
                    "topology_passed": topology_passed,
                    "movement_promotion_blocked_by_budget": not budget_passed,
                    "movement_promotion_blocked_by_identity": not identity_passed,
                    "movement_promotion_blocked_by_topology": not topology_passed,
                    "movement_promotion_blocked": movement_promotion_blocked,
                },
                "expectations": expectations,
                "checks": checks,
                "passed": all(checks.values()),
                "timeseries": ts,
                "claim_flags": {
                    "movement_claim_allowed": False,
                    "loop_driven_movement_claim_allowed": False,
                    "locomotion_like_claim_allowed": False,
                    "adaptive_topology_entry_allowed": False,
                    "movement_claim_inherited_from_n03": False,
                },
            }

    def _reversal_pair_passes(fixture_id: str) -> bool:
        forward = case_results.get(f"{fixture_id}_shape_preserving_shift")
        reverse = case_results.get(f"{fixture_id}_reversed_shape_preserving_shift")
        if not forward or not reverse:
            return False
        forward_obs = forward["observables"]
        reverse_obs = reverse["observables"]
        forward_dx = forward_obs["centroid"]["delta_x_total"]
        reverse_dx = reverse_obs["centroid"]["delta_x_total"]
        forward_front_entered = forward_obs["boundary_flips"]["front_entered_mass"]
        reverse_front_entered = reverse_obs["boundary_flips"]["front_entered_mass"]
        forward_rear_left = forward_obs["boundary_flips"]["rear_left_mass"]
        reverse_rear_left = reverse_obs["boundary_flips"]["rear_left_mass"]
        return (
            forward_dx * reverse_dx < 0.0
            and abs(abs(forward_dx) - abs(reverse_dx)) < 0.02
            and forward_front_entered > 0.0
            and reverse_front_entered > 0.0
            and forward_rear_left > 0.0
            and reverse_rear_left > 0.0
        )

    active_fixture_ids = [
        fixture_id
        for fixture_id, fixture in manifest["fixtures"].items()
        if fixture.get("status") != "deferred"
    ]
    checks = {
        "all_cases_passed": all(case["passed"] for case in case_results.values()),
        "synthetic_positive_present": any(
            case["case_id"] == "shape_preserving_shift" and case["passed"]
            for case in case_results.values()
        ),
        "synthetic_negatives_present": all(
            any(case["case_id"] == expected for case in case_results.values())
            for expected in ["null_static", "smeared_shift", "budget_drift"]
        ),
        "identity_replacement_negative_present": any(
            case["case_id"] == "basin_replacement" and case["passed"]
            for case in case_results.values()
        ),
        "topology_changed_negative_present": any(
            case["case_id"] == "topology_changed_apparent_displacement" and case["passed"]
            for case in case_results.values()
        ),
        "ring_wrap_cases_present": all(
            any(case["case_id"] == expected for case in case_results.values())
            for expected in ["ring_wrap_forward", "ring_wrap_reverse"]
        ),
        "reversal_cross_check_passed": all(
            _reversal_pair_passes(fixture_id) for fixture_id in active_fixture_ids
        ),
        "timeseries_evidence_emitted": all(
            bool(case["timeseries"]["sha256"]) for case in case_results.values()
        ),
        "claim_flags_remain_false": all(
            not any(case["claim_flags"].values()) for case in case_results.values()
        ),
    }
    return {
        "schema": "movement_observables_validation_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "metric_thresholds": {
            "effective_displacement_min": displacement_min,
            "epsilon_budget": epsilon_budget,
            "width_relative_change_max": width_max,
            "profile_similarity_min": profile_min,
            "identity_mass_ratio_min": identity_min,
            "identity_candidate_min": IDENTITY_CANDIDATE_MIN,
            "identity_alignment_max_shift": IDENTITY_ALIGNMENT_MAX_SHIFT,
            "profile_alignment_max_shift": PROFILE_ALIGNMENT_MAX_SHIFT,
            "null_displacement_calibrated": bool(null_envelope["calibrated"]),
        },
        "case_results": case_results,
        "notes": [
            "Synthetic traces validate observables only; they are not movement evidence.",
            "Centroid drift is emitted as a time series and only supports early displacement evidence.",
            "Centroid drift is separated from identity, boundary/support, shape, budget, and topology gates.",
            "Budget drift blocks movement promotion even when displacement is present.",
            "Identity replacement blocks movement promotion even when a new basin appears elsewhere.",
            "Identity continuity levels distinguish candidate continuity from gate-passed identity.",
            "Movement-cost per displacement is null when displacement is effectively zero.",
            "Shape-preserving forward/reverse synthetic cases are cross-checked for opposite displacement signs.",
            "Ring wrap cases validate the tracked-basin unwrapped centroid convention.",
            "All movement claim flags remain false in Iteration 4.",
        ],
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Movement Observables Validation",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_observables.py",
        "```",
        "",
        f"Status: `{result['status']}`",
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
            "## Cases",
            "",
            "| Run | Passed | Budget | Move | Identity | Shape | Topology | dX | Width d | Profile | Boundary Flips |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for run_id, case in result["case_results"].items():
        obs = case["observables"]
        gates = case["gates"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{}` |".format(
                run_id,
                case["passed"],
                gates["budget_passed"],
                gates["displacement_passed"],
                gates["identity_passed"],
                gates["shape_passed"],
                gates["topology_passed"],
                obs["centroid"]["delta_x_total"],
                obs["shape"]["width_relative_change_max"],
                obs["profile_similarity"]["aligned"],
                obs["boundary_flip_count"],
            )
        )
    lines.extend(["", "## Notes", ""])
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_observables()
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

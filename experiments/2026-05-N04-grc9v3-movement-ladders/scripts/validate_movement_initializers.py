"""Validate N04 movement initializers and projection.

The validator reads the movement fixture manifest, builds the first tranche
lane initial states on S0/S1, applies conserved nonnegative projection, and
checks that lane-specific asymmetry/kick rules are deterministic and
budget-preserving.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
OUTPUT_PATH = N04 / "outputs/movement_initializer_validation.json"
REPORT_PATH = N04 / "reports/movement_initializer_validation.md"


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be an object")
    return data


def _signed_distance(fixture: dict[str, Any], node_id: int, center: int) -> float:
    node_count = int(fixture["node_count"])
    if fixture["type"] == "ring":
        return float(((node_id - center + node_count / 2) % node_count) - node_count / 2)
    return float(node_id - center)


def _distance(fixture: dict[str, Any], node_id: int, center: int) -> float:
    return abs(_signed_distance(fixture, node_id, center))


def _project_nonnegative_simplex(values: list[float], total: float) -> list[float]:
    """Euclidean projection onto {x >= 0, sum(x) = total}."""
    if total <= 0.0:
        raise ValueError("simplex total must be positive")
    if not values:
        raise ValueError("cannot project empty vector")
    sorted_values = sorted(values, reverse=True)
    cumulative = 0.0
    rho = -1
    theta = 0.0
    for index, value in enumerate(sorted_values, start=1):
        cumulative += value
        candidate_theta = (cumulative - total) / index
        if value - candidate_theta > 0.0:
            rho = index
            theta = candidate_theta
    if rho < 1:
        return [total / len(values) for _ in values]
    theta = (sum(sorted_values[:rho]) - total) / rho
    return [max(value - theta, 0.0) for value in values]


def _uniform(fixture: dict[str, Any]) -> list[float]:
    node_count = int(fixture["node_count"])
    total = float(fixture["total_budget"])
    return [total / node_count for _ in range(node_count)]


def _symmetric_bump(
    fixture: dict[str, Any],
    defaults: dict[str, Any],
    lane: dict[str, Any],
) -> tuple[list[float], dict[str, Any]]:
    seed = fixture["basin_seed"]
    center = int(seed["center_node_id"])
    sigma = float(seed["sigma"])
    baseline = float(defaults["baseline_coherence"])
    amplitude = float(lane.get("bump_amplitude", defaults["bump_amplitude"]))
    raw = []
    for node in fixture["nodes"]:
        node_id = int(node["node_id"])
        dist = _distance(fixture, node_id, center)
        raw.append(baseline + amplitude * math.exp(-(dist * dist) / (2.0 * sigma * sigma)))
    return raw, {
        "baseline_coherence": baseline,
        "bump_amplitude": amplitude,
        "center_node_id": center,
        "sigma": sigma,
    }


def _asymmetric_bump(
    fixture: dict[str, Any],
    defaults: dict[str, Any],
    lane: dict[str, Any],
) -> tuple[list[float], dict[str, Any]]:
    symmetric_raw, params = _symmetric_bump(fixture, defaults, lane)
    seed = fixture["basin_seed"]
    center = int(seed["center_node_id"])
    sigma_tilt = float(seed["sigma_tilt"])
    epsilon = float(lane.get("tilt_epsilon", defaults["tilt_epsilon"]))
    tilt_sign = float(lane["tilt_sign"])
    tilt_values = []
    raw = []
    for node, base_value in zip(fixture["nodes"], symmetric_raw):
        node_id = int(node["node_id"])
        signed = _signed_distance(fixture, node_id, center)
        tilt = (
            epsilon
            * tilt_sign
            * signed
            * math.exp(-(signed * signed) / (2.0 * sigma_tilt * sigma_tilt))
        )
        tilt_values.append(tilt)
        raw.append(base_value + tilt)
    params.update(
        {
            "tilt_epsilon": epsilon,
            "tilt_sign": tilt_sign,
            "sigma_tilt": sigma_tilt,
            "max_abs_tilt": max(abs(value) for value in tilt_values),
            "max_abs_tilt_outside_local_window": max(
                (
                    abs(value)
                    for value, node in zip(tilt_values, fixture["nodes"])
                    if _distance(fixture, int(node["node_id"]), center) > 3.0 * sigma_tilt
                ),
                default=0.0,
            ),
        }
    )
    return raw, params


def _kick_masks(
    fixture: dict[str, Any],
    lane: dict[str, Any],
    defaults: dict[str, Any],
) -> tuple[list[int], list[int]]:
    center = int(fixture["basin_seed"]["center_node_id"])
    node_count = int(fixture["node_count"])
    mask_node_count = int(lane.get("kick_mask_node_count", defaults["kick_mask_node_count"]))
    if mask_node_count != 1:
        raise ValueError("Iteration 3 only supports kick_mask_node_count = 1")
    front = center + int(lane["front_mask_offset"])
    rear = center + int(lane["rear_mask_offset"])
    if fixture["type"] == "ring":
        front %= node_count
        rear %= node_count
    return [front], [rear]


def _apply_zero_sum_kick(
    values: list[float],
    fixture: dict[str, Any],
    lane: dict[str, Any],
    defaults: dict[str, Any],
) -> tuple[list[float], dict[str, Any]]:
    front_mask, rear_mask = _kick_masks(fixture, lane, defaults)
    kicked = list(values)
    delta = float(lane["kick_delta"])
    for node_id in front_mask:
        kicked[node_id] += delta
    for node_id in rear_mask:
        kicked[node_id] -= delta
    return kicked, {
        "kick_delta": delta,
        "front_mask": front_mask,
        "rear_mask": rear_mask,
        "kick_mask_node_count": int(lane.get("kick_mask_node_count", defaults["kick_mask_node_count"])),
        "raw_kick_sum": delta * len(front_mask) - delta * len(rear_mask),
    }


def _centroid(fixture: dict[str, Any], values: list[float]) -> float:
    total = sum(values)
    if fixture["type"] == "ring":
        center = int(fixture["basin_seed"]["center_node_id"])
        return float(center) + (
            sum(
                _signed_distance(fixture, int(node["node_id"]), center) * values[index]
                for index, node in enumerate(fixture["nodes"])
            )
            / total
        )
    return sum(float(node["coord"][0]) * values[index] for index, node in enumerate(fixture["nodes"])) / total


def _build_lane(
    fixture_id: str,
    fixture: dict[str, Any],
    lane_id: str,
    lane: dict[str, Any],
    defaults: dict[str, Any],
    epsilon_budget: float,
) -> dict[str, Any]:
    initializer = lane["initializer"]
    params: dict[str, Any]
    if initializer == "uniform":
        raw = _uniform(fixture)
        params = {"baseline_coherence": float(fixture["total_budget"]) / int(fixture["node_count"])}
    elif initializer == "symmetric_bump":
        raw, params = _symmetric_bump(fixture, defaults, lane)
    elif initializer == "locally_tapered_asymmetric_bump":
        raw, params = _asymmetric_bump(fixture, defaults, lane)
    else:
        raise ValueError(f"unsupported initializer {initializer!r}")

    kick_params: dict[str, Any] | None = None
    if lane.get("kick") == "zero_sum_kick":
        raw, kick_params = _apply_zero_sum_kick(raw, fixture, lane, defaults)

    total_budget = float(fixture["total_budget"])
    projected = _project_nonnegative_simplex(raw, total_budget)
    budget_error = abs(sum(projected) - total_budget)
    min_value = min(projected)
    raw_centroid = _centroid(fixture, raw)
    centroid = _centroid(fixture, projected)
    raw_sum = sum(raw)
    projection_delta_norm = math.sqrt(
        sum((after - before) * (after - before) for before, after in zip(raw, projected))
    )
    raw_min = min(raw)
    raw_max = max(raw)

    checks = {
        "budget_preserved": budget_error <= epsilon_budget,
        "nonnegative": min_value >= -epsilon_budget,
        "projection_sum_matches": abs(sum(projected) - total_budget) <= epsilon_budget,
    }
    if initializer == "locally_tapered_asymmetric_bump":
        checks["local_tilt_tapered"] = params["max_abs_tilt_outside_local_window"] <= max(
            1e-6, params["max_abs_tilt"] * 0.05
        )
        checks["tilt_nonzero"] = params["max_abs_tilt"] > 0.0
    if kick_params is not None:
        checks["kick_zero_sum"] = abs(kick_params["raw_kick_sum"]) <= epsilon_budget
        checks["kick_masks_equal_size"] = len(kick_params["front_mask"]) == len(kick_params["rear_mask"])

    return {
        "fixture_id": fixture_id,
        "lane_id": lane_id,
        "initializer": initializer,
        "raw_sum_before_projection": raw_sum,
        "raw_min_before_projection": raw_min,
        "raw_max_before_projection": raw_max,
        "projected_budget": sum(projected),
        "projection_delta_norm": projection_delta_norm,
        "budget_error": budget_error,
        "min_value": min_value,
        "max_value": max(projected),
        "raw_centroid_before_projection": raw_centroid,
        "centroid": centroid,
        "centroid_shift_due_to_projection": centroid - raw_centroid,
        "post_projection_centroid_bias_from_seed": centroid
        - float(fixture["basin_seed"]["center_node_id"]),
        "stimulus_audit": {
            "post_projection_asymmetry_score": centroid
            - float(fixture["basin_seed"]["center_node_id"]),
            "post_projection_width": None,
            "stimulus_survived_projection": (
                initializer not in {"locally_tapered_asymmetric_bump"}
                or abs(centroid - float(fixture["basin_seed"]["center_node_id"])) > 0.0
            )
            and (
                kick_params is None
                or abs(centroid - float(fixture["basin_seed"]["center_node_id"])) > 0.0
            ),
        },
        "params": params,
        "formula": initializer,
        "kick": kick_params,
        "checks": checks,
        "passed": all(checks.values()),
        "coherence_by_node": {
            str(node["node_id"]): projected[index] for index, node in enumerate(fixture["nodes"])
        },
    }


def validate_initializers() -> dict[str, Any]:
    manifest = _load_manifest()
    defaults = manifest["initializer_defaults"]
    epsilon_budget = float(manifest["metric_defaults"]["epsilon_budget"])
    fixtures = {
        key: value
        for key, value in manifest["fixtures"].items()
        if value.get("status") != "deferred"
    }
    lanes = manifest["lanes"]

    lane_results: dict[str, Any] = {}
    for fixture_id, fixture in fixtures.items():
        for lane_id, lane in lanes.items():
            lane_results[f"{fixture_id}:{lane_id}"] = _build_lane(
                fixture_id,
                fixture,
                lane_id,
                lane,
                defaults,
                epsilon_budget,
            )

    reversal_checks: dict[str, Any] = {}
    for fixture_id in fixtures:
        b1 = lane_results[f"{fixture_id}:B1"]
        b1r = lane_results[f"{fixture_id}:B1_reversed"]
        b0 = lane_results[f"{fixture_id}:B0"]
        k1 = lane_results[f"{fixture_id}:K1"]
        k1r = lane_results[f"{fixture_id}:K1_reversed"]
        baseline_centroid = float(b0["centroid"])
        reversal_checks[fixture_id] = {
            "b1_centroid_offsets_opposite": (b1["centroid"] - baseline_centroid)
            * (b1r["centroid"] - baseline_centroid)
            < 0.0,
            "k1_centroid_offsets_opposite": (k1["centroid"] - baseline_centroid)
            * (k1r["centroid"] - baseline_centroid)
            < 0.0,
            "b1_equal_budget": abs(b1["projected_budget"] - b1r["projected_budget"]) <= epsilon_budget,
            "k1_equal_budget": abs(k1["projected_budget"] - k1r["projected_budget"]) <= epsilon_budget,
            "baseline_centroid": baseline_centroid,
        }

    checks = {
        "all_lanes_passed": all(result["passed"] for result in lane_results.values()),
        "reversed_controls_deterministic": all(
            all(item.values()) for item in reversal_checks.values()
        ),
        "formulas_serialized": set(manifest["initializer_formulas"]) >= {
            "uniform",
            "symmetric_bump",
            "locally_tapered_asymmetric_bump",
            "zero_sum_kick",
        },
        "projection_declared": all(
            formula.get("projection") == "conserved_nonnegative_simplex"
            for formula in manifest["initializer_formulas"].values()
        ),
    }

    return {
        "schema": "movement_initializer_validation_v1",
        "manifest_path": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "initializer_defaults": defaults,
        "initializer_formulas": manifest["initializer_formulas"],
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "lane_results": lane_results,
        "reversal_checks": reversal_checks,
        "notes": [
            "Projection uses conserved nonnegative simplex projection.",
            "Projection delta norm is reported per lane.",
            "Ring signed distances use shortest unwrapped distance around the tracked basin representative.",
            "For even-N rings, the antipodal node uses negative signed distance; uniform S1_ring_v1 therefore has centroid -0.5 by convention.",
            "B1/B1_reversed centroid offsets must have opposite signs.",
            "K1/K1_reversed centroid offsets must have opposite signs.",
        ],
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Movement Initializer Validation",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_initializers.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Top-Level Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Lane Summary",
            "",
            "| Fixture/Lane | Passed | Budget Error | Min C | Max C | Centroid |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for key, lane in result["lane_results"].items():
        lines.append(
            "| `{}` | `{}` | `{:.3e}` | `{:.6f}` | `{:.6f}` | `{:.6f}` |".format(
                key,
                lane["passed"],
                lane["budget_error"],
                lane["min_value"],
                lane["max_value"],
                lane["centroid"],
            )
        )

    lines.extend(
        [
            "",
            "## Projection Diagnostics",
            "",
            "| Fixture/Lane | Raw Sum | Projection Delta Norm |",
            "|---|---:|---:|",
        ]
    )
    for key, lane in result["lane_results"].items():
        lines.append(
            "| `{}` | `{:.6f}` | `{:.6f}` |".format(
                key,
                lane["raw_sum_before_projection"],
                lane["projection_delta_norm"],
            )
        )

    lines.extend(["", "## Reversal Checks", "", "| Fixture | Checks |", "|---|---|"])
    for fixture_id, checks in result["reversal_checks"].items():
        lines.append(f"| `{fixture_id}` | `{checks}` |")

    lines.extend(["", "## Notes", ""])
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_initializers()
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

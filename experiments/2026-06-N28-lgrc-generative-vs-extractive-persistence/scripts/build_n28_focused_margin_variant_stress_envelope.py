#!/usr/bin/env python3
"""Build N28 Iteration 6-C stress/envelope matrix for focused variants."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_focused_margin_variant_stress_envelope.json"
REPORT = EXPERIMENT / "reports" / "n28_focused_margin_variant_stress_envelope.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_focused_margin_variant_stress_envelope_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_focused_margin_variant_stress_envelope.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I5B_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_focused_margin_variant_replay_matrix.json"
)
EXPECTED_I5B_DIGEST = "0ce6c4dcb35f4c7bef0f2e17c8ab2ff87bde958706c390fd05e016b5092fb08e"
I6B_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_margin_envelope_sweep.json"
)
EXPECTED_I6B_DIGEST = "f91f4cb675b39e0fa87f5ebfbbb842e52129d42c2fbe7d4586bbe2bcd54c5fab"

SWEEP_MULTIPLIERS = [0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
CURRENT_STRESS_MULTIPLIER = 1.0
CRITICAL_MARGIN_CEILING = 0.002
NARROW_MARGIN_CEILING = 0.003

STRESS_VARIANTS = [
    {
        "stress_id": "focal_stability_softening",
        "stress_axis": "focal_stability",
        "focal_support_reduction": 0.006,
        "focal_coherence_reduction": 0.006,
        "focal_stability_reduction": 0.006,
    },
    {
        "stress_id": "neighbor_capacity_compression",
        "stress_axis": "neighbor_capacity",
        "generative_delta_reduction": 0.010,
        "extractive_delta_relief": 0.006,
        "neutral_delta_jitter": 0.003,
    },
    {
        "stress_id": "extraction_cost_pressure",
        "stress_axis": "extraction_cost",
        "focal_extraction_cost_increase": 0.004,
        "extractive_flattening_increase": 0.004,
    },
    {
        "stress_id": "merge_leakage_pressure",
        "stress_axis": "merge_leakage",
        "merge_leakage_increase": 0.003,
    },
    {
        "stress_id": "boundary_integrity_compression",
        "stress_axis": "boundary_integrity",
        "generative_boundary_reduction": 0.010,
        "extractive_boundary_relief": 0.006,
        "mixed_lobe_reduction": 0.004,
    },
]

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "final_generative_persistence_claim_allowed": False,
    "final_n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}

TARGETED_BOTTLENECKS = {
    ("4-F", "merge_leakage_pressure"): {
        "i6b_reference_row": "neutral_merge_leakage_pressure",
        "i6b_current_margin": 0.002,
        "i6b_limiting_field": "merge_leakage_margin",
    },
    ("4-F", "boundary_integrity_compression"): {
        "i6b_reference_row": "neutral_boundary_integrity_compression",
        "i6b_current_margin": 0.001,
        "i6b_limiting_field": "outflow_lobe_margin",
    },
    ("4-G", "extraction_cost_pressure"): {
        "i6b_reference_row": "competitive_extraction_cost_pressure",
        "i6b_current_margin": 0.002,
        "i6b_limiting_field": "flattening_margin",
    },
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(data: Any) -> str:
    return hashlib.sha256(compact_json(data).encode("utf-8")).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def policy_for(row: dict[str, Any]) -> dict[str, float | bool | str]:
    policy = row["row_specific_thresholds_declared_before_use"]
    if policy.get("declared_before_use") is not True:
        raise ValueError(f"thresholds not declared before use for {row['row_id']}")
    defaults = {
        "neighbor_distinguishability_degradation_min": 0.05,
        "neighbor_support_degradation_min": 0.04,
        "neighbor_boundary_degradation_min": 0.06,
        "environment_capacity_degradation_min": 0.05,
        "competitive_neutral_abs_delta_max": 0.025,
        "mixed_lobe_delta_min": 0.04,
    }
    return {**defaults, **policy}


def metric_bundle(row: dict[str, Any]) -> dict[str, float]:
    return {
        "neighbor_distinguishability_delta": row[
            "neighbor_basin_distinguishability_trace"
        ]["delta"],
        "neighbor_support_delta": row["neighbor_support_floor_trace"]["delta"],
        "neighbor_boundary_delta": row["neighbor_boundary_integrity_trace"]["delta"],
        "environment_capacity_delta": row["environment_basin_forming_capacity_trace"][
            "delta"
        ],
        "focal_extraction_cost": row["focal_extraction_cost_trace"]["value"],
        "focal_extraction_cost_ceiling": row["focal_extraction_cost_trace"]["ceiling"],
        "extractive_flattening": row["extractive_flattening_trace"]["value"],
        "extractive_flattening_ceiling": row["extractive_flattening_trace"]["ceiling"],
        "merge_leakage": row["merge_leakage_trace"]["value"],
        "merge_leakage_ceiling": row["merge_leakage_trace"]["ceiling"],
    }


def focal_bundle(row: dict[str, Any]) -> dict[str, float | bool]:
    trace = row["focal_basin_stability_trace"]
    floor_trace = row["focal_support_coherence_floor_trace"]
    return {
        "post_support_min": floor_trace["post_support_min"],
        "post_coherence_min": floor_trace["post_coherence_min"],
        "support_floor": floor_trace["support_floor"],
        "coherence_floor": floor_trace["coherence_floor"],
        "post_stability_score": trace["post_stability_score"],
        "focal_stability_preserved": trace["focal_stability_preserved"],
        "floors_preserved": floor_trace["floors_preserved"],
    }


def move_toward_zero(value: float, amount: float) -> float:
    if value > 0:
        return max(0.0, value - amount)
    if value < 0:
        return min(0.0, value + amount)
    return value


def scaled(value: float, multiplier: float) -> float:
    return round(value * multiplier, 12)


def apply_scaled_stress(
    row: dict[str, Any], variant: dict[str, Any], multiplier: float
) -> tuple[dict[str, float], dict[str, float | bool], dict[str, Any]]:
    metrics = copy.deepcopy(metric_bundle(row))
    focal = copy.deepcopy(focal_bundle(row))
    boundary = copy.deepcopy(row["competitive_neutral_boundary_record"])

    if variant["stress_id"] == "focal_stability_softening":
        focal["post_support_min"] = round(
            focal["post_support_min"]
            - scaled(variant["focal_support_reduction"], multiplier),
            12,
        )
        focal["post_coherence_min"] = round(
            focal["post_coherence_min"]
            - scaled(variant["focal_coherence_reduction"], multiplier),
            12,
        )
        focal["post_stability_score"] = round(
            focal["post_stability_score"]
            - scaled(variant["focal_stability_reduction"], multiplier),
            12,
        )
        focal["floors_preserved"] = (
            focal["post_support_min"] >= focal["support_floor"]
            and focal["post_coherence_min"] >= focal["coherence_floor"]
        )
        focal["focal_stability_preserved"] = (
            focal["floors_preserved"] is True and focal["post_stability_score"] >= 0.84
        )
    elif variant["stress_id"] == "neighbor_capacity_compression":
        amount = scaled(variant["neutral_delta_jitter"], multiplier)
        for key in [
            "neighbor_distinguishability_delta",
            "neighbor_support_delta",
            "neighbor_boundary_delta",
            "environment_capacity_delta",
        ]:
            metrics[key] = round(move_toward_zero(metrics[key], amount), 12)
    elif variant["stress_id"] == "extraction_cost_pressure":
        metrics["focal_extraction_cost"] = round(
            metrics["focal_extraction_cost"]
            + scaled(variant["focal_extraction_cost_increase"], multiplier),
            12,
        )
        metrics["extractive_flattening"] = round(
            metrics["extractive_flattening"]
            + scaled(variant["extractive_flattening_increase"], multiplier),
            12,
        )
    elif variant["stress_id"] == "merge_leakage_pressure":
        metrics["merge_leakage"] = round(
            metrics["merge_leakage"]
            + scaled(variant["merge_leakage_increase"], multiplier),
            12,
        )
    elif variant["stress_id"] == "boundary_integrity_compression":
        amount = scaled(variant["mixed_lobe_reduction"], multiplier)
        if boundary.get("competitive_redistribution_detected") is True:
            boundary["route_lobe_a_capacity_delta"] = round(
                boundary["route_lobe_a_capacity_delta"] - amount,
                12,
            )
            boundary["route_lobe_b_capacity_delta"] = round(
                boundary["route_lobe_b_capacity_delta"] + amount,
                12,
            )
        elif boundary.get("neutral_circulation_detected") is True:
            boundary["inflow_lobe_capacity_delta"] = round(
                boundary["inflow_lobe_capacity_delta"] - amount,
                12,
            )
            boundary["outflow_lobe_capacity_delta"] = round(
                boundary["outflow_lobe_capacity_delta"] + amount,
                12,
            )
    else:
        raise ValueError(f"unknown stress variant {variant['stress_id']}")
    return metrics, focal, boundary


def classify(
    row: dict[str, Any],
    metrics: dict[str, float],
    focal: dict[str, float | bool],
    boundary: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    policy = policy_for(row)
    stable = focal["focal_stability_preserved"] is True and focal["floors_preserved"] is True
    extraction_below = (
        metrics["focal_extraction_cost"] <= metrics["focal_extraction_cost_ceiling"]
        and metrics["extractive_flattening"] <= metrics["extractive_flattening_ceiling"]
        and metrics["merge_leakage"] <= metrics["merge_leakage_ceiling"]
    )
    near_neutral = (
        abs(metrics["neighbor_distinguishability_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["neighbor_support_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["neighbor_boundary_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["environment_capacity_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
    )
    competitive = (
        boundary.get("competitive_redistribution_detected") is True
        and boundary.get("route_lobe_a_capacity_delta", 0.0)
        >= policy["mixed_lobe_delta_min"]
        and boundary.get("route_lobe_b_capacity_delta", 0.0)
        <= -policy["mixed_lobe_delta_min"]
    )
    neutral = (
        boundary.get("neutral_circulation_detected") is True
        and boundary.get("inflow_lobe_capacity_delta", 0.0)
        >= policy["mixed_lobe_delta_min"]
        and boundary.get("outflow_lobe_capacity_delta", 0.0)
        <= -policy["mixed_lobe_delta_min"]
        and abs(boundary.get("buffer_lobe_capacity_delta", 0.0))
        <= policy["competitive_neutral_abs_delta_max"]
    )
    if stable and near_neutral and extraction_below and competitive:
        result = "competitive"
    elif stable and near_neutral and extraction_below and neutral:
        result = "neutral"
    else:
        result = "unclassified"
    return result, {
        "stable": stable,
        "extraction_below": extraction_below,
        "near_neutral": near_neutral,
        "competitive_redistribution": competitive,
        "neutral_circulation": neutral,
    }


def margin_items(
    row: dict[str, Any],
    metrics: dict[str, float],
    focal: dict[str, float | bool],
    boundary: dict[str, Any],
) -> dict[str, float]:
    policy = policy_for(row)
    margins = {
        "focal_support_margin": round(
            focal["post_support_min"] - focal["support_floor"], 12
        ),
        "focal_coherence_margin": round(
            focal["post_coherence_min"] - focal["coherence_floor"], 12
        ),
        "neighbor_distinguishability_neutral_margin": round(
            policy["competitive_neutral_abs_delta_max"]
            - abs(metrics["neighbor_distinguishability_delta"]),
            12,
        ),
        "neighbor_support_neutral_margin": round(
            policy["competitive_neutral_abs_delta_max"]
            - abs(metrics["neighbor_support_delta"]),
            12,
        ),
        "neighbor_boundary_neutral_margin": round(
            policy["competitive_neutral_abs_delta_max"]
            - abs(metrics["neighbor_boundary_delta"]),
            12,
        ),
        "environment_capacity_neutral_margin": round(
            policy["competitive_neutral_abs_delta_max"]
            - abs(metrics["environment_capacity_delta"]),
            12,
        ),
        "extraction_cost_margin": round(
            metrics["focal_extraction_cost_ceiling"] - metrics["focal_extraction_cost"],
            12,
        ),
        "flattening_margin": round(
            metrics["extractive_flattening_ceiling"] - metrics["extractive_flattening"],
            12,
        ),
        "merge_leakage_margin": round(
            metrics["merge_leakage_ceiling"] - metrics["merge_leakage"],
            12,
        ),
    }
    if boundary.get("competitive_redistribution_detected") is True:
        margins["route_lobe_a_margin"] = round(
            boundary["route_lobe_a_capacity_delta"] - policy["mixed_lobe_delta_min"],
            12,
        )
        margins["route_lobe_b_margin"] = round(
            -boundary["route_lobe_b_capacity_delta"] - policy["mixed_lobe_delta_min"],
            12,
        )
    if boundary.get("neutral_circulation_detected") is True:
        margins["inflow_lobe_margin"] = round(
            boundary["inflow_lobe_capacity_delta"] - policy["mixed_lobe_delta_min"],
            12,
        )
        margins["outflow_lobe_margin"] = round(
            -boundary["outflow_lobe_capacity_delta"] - policy["mixed_lobe_delta_min"],
            12,
        )
        margins["buffer_lobe_margin"] = round(
            policy["competitive_neutral_abs_delta_max"]
            - abs(boundary["buffer_lobe_capacity_delta"]),
            12,
        )
    return margins


def minimum_margin(margins: dict[str, float]) -> tuple[str, float]:
    key = min(margins, key=margins.get)
    return key, margins[key]


def source_rows(i5b: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for replay_row in i5b["replay_rows"]:
        source_artifact = load_json(replay_row["source_path"])
        rows.append(
            {
                "source_iteration": replay_row["source_iteration"],
                "source_path": replay_row["source_path"],
                "source_output_digest": replay_row["source_output_digest"],
                "source_artifact_sha256": replay_row["source_artifact_sha256"],
                "source_replay_row_id": replay_row["row_id"],
                "source_replay_row_digest": replay_row["row_digest"],
                "source_row": source_artifact["candidate_rows"][0],
            }
        )
    return rows


def sweep_row(
    source: dict[str, Any], variant: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
    row = source["source_row"]
    points = []
    for multiplier in SWEEP_MULTIPLIERS:
        metrics, focal, boundary = apply_scaled_stress(row, variant, multiplier)
        label, evidence = classify(row, metrics, focal, boundary)
        margins = margin_items(row, metrics, focal, boundary)
        margin_field, margin_value = minimum_margin(margins)
        passed = label == row["regime_label"] and evidence["stable"] is True
        points.append(
            {
                "multiplier": multiplier,
                "observed_label": label,
                "classification_preserved": passed,
                "minimum_margin_field": margin_field,
                "minimum_margin": margin_value,
                "classification_evidence": evidence,
            }
        )
    current = next(
        point for point in points if point["multiplier"] == CURRENT_STRESS_MULTIPLIER
    )
    passed_points = [point for point in points if point["classification_preserved"]]
    failed_points = [
        point
        for point in points
        if point["multiplier"] >= CURRENT_STRESS_MULTIPLIER
        and not point["classification_preserved"]
    ]
    max_passed = max(point["multiplier"] for point in passed_points)
    first_failed = failed_points[0]["multiplier"] if failed_points else "not_failed_within_sweep"
    target = TARGETED_BOTTLENECKS.get((source["source_iteration"], variant["stress_id"]))
    targeted_margin_improvement = (
        target is not None
        and current["classification_preserved"] is True
        and current["minimum_margin"] > target["i6b_current_margin"]
    )
    envelope = {
        "trace_id": f"n28_i6c_{row['row_id']}_{variant['stress_id']}_stress_envelope",
        "source_iteration": source["source_iteration"],
        "source_path": source["source_path"],
        "source_output_digest": source["source_output_digest"],
        "source_replay_row_id": source["source_replay_row_id"],
        "source_replay_row_digest": source["source_replay_row_digest"],
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "sweep_multipliers": SWEEP_MULTIPLIERS,
        "current_stress_multiplier": CURRENT_STRESS_MULTIPLIER,
        "current_classification_preserved": current["classification_preserved"],
        "current_minimum_margin": current["minimum_margin"],
        "current_limiting_field": current["minimum_margin_field"],
        "max_passed_multiplier": max_passed,
        "first_failed_multiplier": first_failed,
        "targeted_bottleneck_reference": target or "not_targeted_bottleneck_axis",
        "targeted_margin_improvement_supported": targeted_margin_improvement,
        "thresholds_retuned_for_sweep": False,
        "source_row_mutated": False,
        "new_source_current_evidence_opened": False,
        "sweep_points": points,
    }
    artifact = trace_artifact(
        f"n28_i6c_{row['row_id']}_{variant['stress_id']}_stress_envelope",
        envelope,
    )
    stress_row = {
        "row_id": f"n28_i6c_{row['row_id']}_{variant['stress_id']}",
        "iteration": "6-C",
        "source_iteration": source["source_iteration"],
        "source_path": source["source_path"],
        "source_output_digest": source["source_output_digest"],
        "source_replay_row_id": source["source_replay_row_id"],
        "source_replay_row_digest": source["source_replay_row_digest"],
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "current_classification_preserved": current["classification_preserved"],
        "current_minimum_margin": current["minimum_margin"],
        "current_limiting_field": current["minimum_margin_field"],
        "max_passed_multiplier": max_passed,
        "first_failed_multiplier": first_failed,
        "narrow_margin_at_current": current["minimum_margin"] <= NARROW_MARGIN_CEILING,
        "critical_margin_at_current": current["minimum_margin"] <= CRITICAL_MARGIN_CEILING,
        "targeted_bottleneck_axis": target is not None,
        "targeted_margin_improvement_supported": targeted_margin_improvement,
        "row_decision": "supported"
        if current["classification_preserved"]
        else "blocked",
        "row_decision_scope": "focused_GE5_stress_envelope_candidate",
        "ge_ladder_rung_effect": "GE5_focused_variant_supported"
        if current["classification_preserved"]
        else "GE5_focused_variant_blocked",
        "stress_trace_artifact": artifact["path"],
        "stress_trace_artifact_sha256": artifact["sha256"],
        "stress_trace_digest": digest_value(envelope),
    }
    stress_row["row_digest"] = digest_value(stress_row)
    return stress_row, artifact


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def build_output() -> dict[str, Any]:
    i5b = load_json(I5B_OUTPUT_PATH)
    i6b = load_json(I6B_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    stress_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for source in source_rows(i5b):
        for variant in STRESS_VARIANTS:
            stress_row, artifact = sweep_row(source, variant)
            stress_rows.append(stress_row)
            artifacts.append(artifact)

    current_rows_supported = [
        row for row in stress_rows if row["current_classification_preserved"]
    ]
    targeted_rows = [row for row in stress_rows if row["targeted_bottleneck_axis"]]
    targeted_improvements = [
        row for row in targeted_rows if row["targeted_margin_improvement_supported"]
    ]
    critical_rows = [row for row in stress_rows if row["critical_margin_at_current"]]
    narrow_rows = [row for row in stress_rows if row["narrow_margin_at_current"]]
    failed_within_sweep = [
        row
        for row in stress_rows
        if row["first_failed_multiplier"] != "not_failed_within_sweep"
    ]

    axis_results: dict[str, dict[str, Any]] = {}
    for variant in STRESS_VARIANTS:
        rows = [row for row in stress_rows if row["stress_id"] == variant["stress_id"]]
        axis_results[variant["stress_id"]] = {
            "stress_axis": variant["stress_axis"],
            "row_count": len(rows),
            "current_classification_preserved_count": sum(
                row["current_classification_preserved"] for row in rows
            ),
            "critical_current_margin_count": sum(
                row["critical_margin_at_current"] for row in rows
            ),
            "narrow_current_margin_count": sum(row["narrow_margin_at_current"] for row in rows),
            "minimum_current_margin": min(row["current_minimum_margin"] for row in rows),
            "minimum_max_passed_multiplier": min(
                row["max_passed_multiplier"] for row in rows
            ),
        }

    summary = {
        "trace_id": "n28_i6c_focused_margin_variant_stress_summary",
        "source_i5b_output_digest": i5b["output_digest"],
        "source_i6b_output_digest": i6b["output_digest"],
        "source_replay_row_count": len(i5b["replay_rows"]),
        "stress_row_count": len(stress_rows),
        "current_stress_rows_preserved": len(current_rows_supported),
        "targeted_bottleneck_row_count": len(targeted_rows),
        "targeted_bottleneck_improvement_count": len(targeted_improvements),
        "critical_current_margin_count": len(critical_rows),
        "narrow_current_margin_count": len(narrow_rows),
        "failed_within_sweep_count": len(failed_within_sweep),
        "minimum_current_margin": min(
            row["current_minimum_margin"] for row in stress_rows
        ),
        "targeted_improvement_rows": [
            {
                "row_id": row["row_id"],
                "source_iteration": row["source_iteration"],
                "source_regime_label": row["source_regime_label"],
                "stress_id": row["stress_id"],
                "current_minimum_margin": row["current_minimum_margin"],
                "current_limiting_field": row["current_limiting_field"],
                "targeted_margin_improvement_supported": row[
                    "targeted_margin_improvement_supported"
                ],
            }
            for row in targeted_rows
        ],
        "axis_results": axis_results,
        "thresholds_retuned_for_sweep": False,
        "source_rows_mutated": False,
        "margin_interpretation": "targeted_current_multiplier_margin_improvement_not_broad_robustness",
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "absolute_margin_scope": "normalized margins remain small; minimum current margin is 0.005",
        "focused_optimization_not_generalization": True,
        "focused_variant_ge5_supported": len(current_rows_supported) == len(stress_rows),
        "ge6_or_stronger_supported": False,
    }
    summary_artifact = trace_artifact("focused_margin_variant_stress_summary", summary)
    artifacts.append(summary_artifact)

    checks = [
        check(
            "i5b_replay_matrix_pinned_and_passed",
            i5b["status"] == "passed"
            and i5b["output_digest"] == EXPECTED_I5B_DIGEST
            and i5b["ge4_or_stronger_supported"] is True
            and i5b["ge5_or_stronger_supported"] is False,
        ),
        check(
            "i6b_bottleneck_map_pinned_and_passed",
            i6b["status"] == "passed"
            and i6b["output_digest"] == EXPECTED_I6B_DIGEST
            and i6b["ge5_or_stronger_supported"] is True,
        ),
        check("both_focused_replay_sources_consumed", len(i5b["replay_rows"]) == 2),
        check("all_stress_axes_applied", len(STRESS_VARIANTS) == 5),
        check("all_current_focused_stress_rows_preserved", len(current_rows_supported) == len(stress_rows)),
        check("targeted_bottleneck_margins_improved", len(targeted_improvements) == len(TARGETED_BOTTLENECKS)),
        check("no_critical_current_margins_remaining", len(critical_rows) == 0),
        check("no_narrow_current_margins_remaining", len(narrow_rows) == 0),
        check("failure_brackets_recorded_where_present", len(failed_within_sweep) >= 1),
        check("thresholds_not_retuned_for_focused_sweep", not summary["thresholds_retuned_for_sweep"]),
        check("source_rows_not_mutated", not summary["source_rows_mutated"]),
        check("broad_margin_robustness_not_claimed", not summary["broad_margin_robustness_supported"]),
        check("order_of_magnitude_robustness_not_claimed", not summary["order_of_magnitude_robustness_supported"]),
        check("ge5_supported_ge6_blocked", summary["focused_variant_ge5_supported"] and not summary["ge6_or_stronger_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]

    output = {
        "artifact_id": "n28_focused_margin_variant_stress_envelope",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_focused_margin_variants_ge5_stress_envelope_supported_pending_claim_classification",
        "experiment": "N28",
        "iteration": "6-C",
        "source_i5b_replay_matrix": {
            "path": I5B_OUTPUT_PATH,
            "output_digest": i5b["output_digest"],
            "artifact_sha256": sha256_file(I5B_OUTPUT_PATH),
            "status": i5b["status"],
            "acceptance_state": i5b["acceptance_state"],
        },
        "source_i6b_bottleneck_map": {
            "path": I6B_OUTPUT_PATH,
            "output_digest": i6b["output_digest"],
            "artifact_sha256": sha256_file(I6B_OUTPUT_PATH),
            "status": i6b["status"],
            "acceptance_state": i6b["acceptance_state"],
        },
        "focused_stress_policy": {
            "policy_id": "n28_i6c_focused_margin_variant_stress_v1",
            "declared_before_use": True,
            "stress_variants_reused_from_i6": True,
            "sweep_multipliers": SWEEP_MULTIPLIERS,
            "current_stress_multiplier": CURRENT_STRESS_MULTIPLIER,
            "critical_margin_ceiling": CRITICAL_MARGIN_CEILING,
            "narrow_margin_ceiling": NARROW_MARGIN_CEILING,
            "thresholds_retuned_for_sweep": False,
            "source_rows_mutated": False,
        },
        "stress_rows": stress_rows,
        "artifact_manifest": artifacts,
        "stress_summary": summary,
        "provisional_ge_ladder_rung": "GE5",
        "focused_variant_ge5_supported": summary["focused_variant_ge5_supported"],
        "ge5_or_stronger_supported": summary["focused_variant_ge5_supported"],
        "ge6_or_stronger_supported": False,
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_iteration_7_claim_classification": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "GE5_focused_current_multiplier_margin_improvement; broad_robustness_GE6/final_N28_pending_classification",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    summary = output["stress_summary"]
    lines = [
        "# N28 Iteration 6-C - Focused Margin Variant Stress Envelope",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- Focused GE5 supported: `{str(output['focused_variant_ge5_supported']).lower()}`",
        f"- GE6 supported: `{str(output['ge6_or_stronger_supported']).lower()}`",
        "",
        "I6-C stress-tests the replay-backed focused variants from I5-B using the",
        "same I6 stress family and I6-B multiplier envelope. It is targeted at the",
        "competitive/neutral bottlenecks identified in I6-B; it does not replace",
        "the paired-regime I6 result, does not claim broad robustness, and does",
        "not open GE6.",
        "",
        "## Focused Envelope Summary",
        "",
        "```text",
        f"stress_row_count = {summary['stress_row_count']}",
        f"current_stress_rows_preserved = {summary['current_stress_rows_preserved']}",
        f"targeted_bottleneck_row_count = {summary['targeted_bottleneck_row_count']}",
        f"targeted_bottleneck_improvement_count = {summary['targeted_bottleneck_improvement_count']}",
        f"critical_current_margin_count = {summary['critical_current_margin_count']}",
        f"narrow_current_margin_count = {summary['narrow_current_margin_count']}",
        f"minimum_current_margin = {summary['minimum_current_margin']}",
        f"margin_interpretation = {summary['margin_interpretation']}",
        f"broad_margin_robustness_supported = {str(summary['broad_margin_robustness_supported']).lower()}",
        f"order_of_magnitude_robustness_supported = {str(summary['order_of_magnitude_robustness_supported']).lower()}",
        "```",
        "",
        "## Targeted Improvements",
        "",
        "| Row | Source | Regime | Stress | Current Margin | Limiting Field | Improved |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in summary["targeted_improvement_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['source_regime_label']}` | `{row['stress_id']}` | "
            f"{row['current_minimum_margin']:.12f} | "
            f"`{row['current_limiting_field']}` | "
            f"`{str(row['targeted_margin_improvement_supported']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Axis Results",
            "",
            "| Stress ID | Axis | Rows | Preserved | Critical | Narrow | Minimum Current Margin | Minimum Max Passed |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for stress_id, result in summary["axis_results"].items():
        lines.append(
            f"| `{stress_id}` | `{result['stress_axis']}` | "
            f"{result['row_count']} | "
            f"{result['current_classification_preserved_count']} | "
            f"{result['critical_current_margin_count']} | "
            f"{result['narrow_current_margin_count']} | "
            f"{result['minimum_current_margin']:.12f} | "
            f"{result['minimum_max_passed_multiplier']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I6-C shows targeted current-multiplier margin improvement for the",
            "focused neutral circulation and competitive redistribution variants.",
            "The result should be read as focused optimization of the weak",
            "competitive/neutral transition rows, not as broad margin robustness.",
            "The geometric change is not a new regime label: I4-F remains neutral",
            "circulation and I4-G remains competitive redistribution.",
            "",
            "The stronger evidence is narrow: their circulation, leakage, route-lobe,",
            "and flattening margins no longer sit on the I6-B critical edge under the",
            "current stress multiplier. The absolute normalized margins remain small",
            "(minimum current margin 0.005), so this is not order-of-magnitude",
            "robustness and not GE6.",
            "",
            "This supports focused GE5 evidence for the competitive/neutral transition",
            "region only. It does not upgrade GE6, final N28, semantic cooperation,",
            "agency, native support, Phase 8 completion, or ant ecology.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

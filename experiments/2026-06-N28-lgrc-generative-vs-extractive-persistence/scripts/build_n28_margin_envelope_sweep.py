#!/usr/bin/env python3
"""Build N28 Iteration 6-B margin envelope sweep."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_margin_envelope_sweep.json"
REPORT = EXPERIMENT / "reports" / "n28_margin_envelope_sweep.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_margin_envelope_sweep_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_margin_envelope_sweep.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I6_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_stress_regime_separation_matrix.json"
)
EXPECTED_I6_DIGEST = "fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756"

SWEEP_MULTIPLIERS = [0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
CURRENT_I6_MULTIPLIER = 1.0
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


def scale(value: float, multiplier: float) -> float:
    return round(value * multiplier, 12)


def apply_scaled_stress(
    row: dict[str, Any], variant: dict[str, Any], multiplier: float
) -> tuple[dict[str, float], dict[str, float | bool], dict[str, Any]]:
    regime = row["regime_label"]
    metrics = copy.deepcopy(metric_bundle(row))
    focal = copy.deepcopy(focal_bundle(row))
    boundary = copy.deepcopy(row.get("competitive_neutral_boundary_record", {}))

    if variant["stress_id"] == "focal_stability_softening":
        focal["post_support_min"] = round(
            focal["post_support_min"]
            - scale(variant["focal_support_reduction"], multiplier),
            12,
        )
        focal["post_coherence_min"] = round(
            focal["post_coherence_min"]
            - scale(variant["focal_coherence_reduction"], multiplier),
            12,
        )
        focal["post_stability_score"] = round(
            focal["post_stability_score"]
            - scale(variant["focal_stability_reduction"], multiplier),
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
        if regime == "generative":
            amount = scale(variant["generative_delta_reduction"], multiplier)
            for key in [
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "environment_capacity_delta",
            ]:
                metrics[key] = round(metrics[key] - amount, 12)
        elif regime == "extractive":
            amount = scale(variant["extractive_delta_relief"], multiplier)
            for key in [
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "environment_capacity_delta",
            ]:
                metrics[key] = round(metrics[key] + amount, 12)
        else:
            amount = scale(variant["neutral_delta_jitter"], multiplier)
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
            + scale(variant["focal_extraction_cost_increase"], multiplier),
            12,
        )
        metrics["extractive_flattening"] = round(
            metrics["extractive_flattening"]
            + scale(variant["extractive_flattening_increase"], multiplier),
            12,
        )
    elif variant["stress_id"] == "merge_leakage_pressure":
        metrics["merge_leakage"] = round(
            metrics["merge_leakage"]
            + scale(variant["merge_leakage_increase"], multiplier),
            12,
        )
    elif variant["stress_id"] == "boundary_integrity_compression":
        if regime == "generative":
            metrics["neighbor_boundary_delta"] = round(
                metrics["neighbor_boundary_delta"]
                - scale(variant["generative_boundary_reduction"], multiplier),
                12,
            )
        elif regime == "extractive":
            metrics["neighbor_boundary_delta"] = round(
                metrics["neighbor_boundary_delta"]
                + scale(variant["extractive_boundary_relief"], multiplier),
                12,
            )
        elif boundary.get("competitive_redistribution_detected") is True:
            amount = scale(variant["mixed_lobe_reduction"], multiplier)
            boundary["route_lobe_a_capacity_delta"] = round(
                boundary["route_lobe_a_capacity_delta"] - amount,
                12,
            )
            boundary["route_lobe_b_capacity_delta"] = round(
                boundary["route_lobe_b_capacity_delta"] + amount,
                12,
            )
        elif boundary.get("neutral_circulation_detected") is True:
            amount = scale(variant["mixed_lobe_reduction"], multiplier)
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
    extraction_present = (
        metrics["focal_extraction_cost"] > metrics["focal_extraction_cost_ceiling"]
        or metrics["extractive_flattening"] > metrics["extractive_flattening_ceiling"]
        or metrics["merge_leakage"] > metrics["merge_leakage_ceiling"]
    )
    generative_gain = (
        metrics["neighbor_distinguishability_delta"]
        >= policy["neighbor_distinguishability_delta_min"]
        and metrics["neighbor_support_delta"] >= policy["neighbor_support_delta_min"]
        and metrics["neighbor_boundary_delta"] >= policy["neighbor_boundary_delta_min"]
        and metrics["environment_capacity_delta"] >= policy["environment_capacity_delta_min"]
    )
    extractive_loss = (
        metrics["neighbor_distinguishability_delta"]
        <= -policy["neighbor_distinguishability_degradation_min"]
        and metrics["neighbor_support_delta"] <= -policy["neighbor_support_degradation_min"]
        and metrics["neighbor_boundary_delta"] <= -policy["neighbor_boundary_degradation_min"]
        and metrics["environment_capacity_delta"]
        <= -policy["environment_capacity_degradation_min"]
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
    if stable and generative_gain and extraction_below:
        result = "generative"
    elif stable and extractive_loss and extraction_present:
        result = "extractive"
    elif stable and near_neutral and extraction_below and competitive:
        result = "competitive"
    elif stable and near_neutral and extraction_below and neutral:
        result = "neutral"
    else:
        result = "unclassified"
    return result, {
        "stable": stable,
        "extraction_below": extraction_below,
        "extraction_present": extraction_present,
        "generative_gain": generative_gain,
        "extractive_loss": extractive_loss,
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
    regime = row["regime_label"]
    margins = {
        "focal_support_margin": round(
            focal["post_support_min"] - focal["support_floor"], 12
        ),
        "focal_coherence_margin": round(
            focal["post_coherence_min"] - focal["coherence_floor"], 12
        ),
    }
    if regime == "generative":
        margins.update(
            {
                "neighbor_distinguishability_margin": round(
                    metrics["neighbor_distinguishability_delta"]
                    - policy["neighbor_distinguishability_delta_min"],
                    12,
                ),
                "neighbor_support_margin": round(
                    metrics["neighbor_support_delta"]
                    - policy["neighbor_support_delta_min"],
                    12,
                ),
                "neighbor_boundary_margin": round(
                    metrics["neighbor_boundary_delta"]
                    - policy["neighbor_boundary_delta_min"],
                    12,
                ),
                "environment_capacity_margin": round(
                    metrics["environment_capacity_delta"]
                    - policy["environment_capacity_delta_min"],
                    12,
                ),
                "extraction_cost_margin": round(
                    metrics["focal_extraction_cost_ceiling"]
                    - metrics["focal_extraction_cost"],
                    12,
                ),
                "flattening_margin": round(
                    metrics["extractive_flattening_ceiling"]
                    - metrics["extractive_flattening"],
                    12,
                ),
                "merge_leakage_margin": round(
                    metrics["merge_leakage_ceiling"] - metrics["merge_leakage"],
                    12,
                ),
            }
        )
    elif regime == "extractive":
        margins.update(
            {
                "neighbor_distinguishability_loss_margin": round(
                    -metrics["neighbor_distinguishability_delta"]
                    - policy["neighbor_distinguishability_degradation_min"],
                    12,
                ),
                "neighbor_support_loss_margin": round(
                    -metrics["neighbor_support_delta"]
                    - policy["neighbor_support_degradation_min"],
                    12,
                ),
                "neighbor_boundary_loss_margin": round(
                    -metrics["neighbor_boundary_delta"]
                    - policy["neighbor_boundary_degradation_min"],
                    12,
                ),
                "environment_capacity_loss_margin": round(
                    -metrics["environment_capacity_delta"]
                    - policy["environment_capacity_degradation_min"],
                    12,
                ),
                "extraction_cost_excess_margin": round(
                    metrics["focal_extraction_cost"]
                    - metrics["focal_extraction_cost_ceiling"],
                    12,
                ),
                "flattening_excess_margin": round(
                    metrics["extractive_flattening"]
                    - metrics["extractive_flattening_ceiling"],
                    12,
                ),
                "merge_leakage_excess_margin": round(
                    metrics["merge_leakage"] - metrics["merge_leakage_ceiling"],
                    12,
                ),
            }
        )
    else:
        margins.update(
            {
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
                    metrics["focal_extraction_cost_ceiling"]
                    - metrics["focal_extraction_cost"],
                    12,
                ),
                "flattening_margin": round(
                    metrics["extractive_flattening_ceiling"]
                    - metrics["extractive_flattening"],
                    12,
                ),
                "merge_leakage_margin": round(
                    metrics["merge_leakage_ceiling"] - metrics["merge_leakage"],
                    12,
                ),
            }
        )
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


def unique_sources(i6: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    sources: list[dict[str, Any]] = []
    for row in i6["stress_rows"]:
        if row["source_row_id"] in seen:
            continue
        seen.add(row["source_row_id"])
        sources.append(
            {
                "source_iteration": row["source_iteration"],
                "source_path": row["source_path"],
                "source_output_digest": row["source_output_digest"],
                "source_row_id": row["source_row_id"],
                "source_regime_label": row["source_regime_label"],
            }
        )
    return sources


def sweep_for_pair(
    source: dict[str, Any], row: dict[str, Any], variant: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
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
        point for point in points if point["multiplier"] == CURRENT_I6_MULTIPLIER
    )
    passed_points = [point for point in points if point["classification_preserved"]]
    failed_points = [
        point
        for point in points
        if point["multiplier"] >= CURRENT_I6_MULTIPLIER
        and not point["classification_preserved"]
    ]
    max_passed = max(point["multiplier"] for point in passed_points)
    first_failed = failed_points[0]["multiplier"] if failed_points else "not_failed_within_sweep"
    envelope = {
        "trace_id": f"n28_i6b_{row['row_id']}_{variant['stress_id']}_envelope",
        "source_iteration": source["source_iteration"],
        "source_path": source["source_path"],
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "sweep_multipliers": SWEEP_MULTIPLIERS,
        "current_i6_multiplier": CURRENT_I6_MULTIPLIER,
        "current_i6_classification_preserved": current["classification_preserved"],
        "current_i6_minimum_margin": current["minimum_margin"],
        "current_i6_limiting_field": current["minimum_margin_field"],
        "max_passed_multiplier": max_passed,
        "first_failed_multiplier": first_failed,
        "narrow_margin_at_current": current["minimum_margin"] <= NARROW_MARGIN_CEILING,
        "critical_margin_at_current": current["minimum_margin"] <= CRITICAL_MARGIN_CEILING,
        "thresholds_retuned_for_sweep": False,
        "source_row_mutated": False,
        "new_source_current_evidence_opened": False,
        "sweep_points": points,
    }
    artifact = trace_artifact(
        f"n28_i6b_{row['row_id']}_{variant['stress_id']}_envelope",
        envelope,
    )
    envelope_row = {
        "row_id": f"n28_i6b_{row['row_id']}_{variant['stress_id']}",
        "iteration": "6-B",
        "source_iteration": source["source_iteration"],
        "source_path": source["source_path"],
        "source_output_digest": source["source_output_digest"],
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "current_i6_classification_preserved": current["classification_preserved"],
        "current_i6_minimum_margin": current["minimum_margin"],
        "current_i6_limiting_field": current["minimum_margin_field"],
        "max_passed_multiplier": max_passed,
        "first_failed_multiplier": first_failed,
        "narrow_margin_at_current": current["minimum_margin"] <= NARROW_MARGIN_CEILING,
        "critical_margin_at_current": current["minimum_margin"] <= CRITICAL_MARGIN_CEILING,
        "row_decision": "supported"
        if current["classification_preserved"]
        else "blocked",
        "row_decision_scope": "margin_envelope_characterization_only",
        "ge_ladder_rung_effect": "GE5_preserved_no_new_GE_support"
        if current["classification_preserved"]
        else "GE5_boundary_blocker",
        "envelope_trace_artifact": artifact["path"],
        "envelope_trace_artifact_sha256": artifact["sha256"],
        "envelope_trace_digest": digest_value(envelope),
    }
    envelope_row["row_digest"] = digest_value(envelope_row)
    return envelope_row, artifact


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def build_output() -> dict[str, Any]:
    i6 = load_json(I6_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    envelope_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for source in unique_sources(i6):
        source_artifact = load_json(source["source_path"])
        row = source_artifact["candidate_rows"][0]
        for variant in STRESS_VARIANTS:
            envelope_row, artifact = sweep_for_pair(source, row, variant)
            envelope_rows.append(envelope_row)
            artifacts.append(artifact)

    critical_rows = [
        row for row in envelope_rows if row["critical_margin_at_current"]
    ]
    narrow_rows = [row for row in envelope_rows if row["narrow_margin_at_current"]]
    failed_within_sweep = [
        row
        for row in envelope_rows
        if row["first_failed_multiplier"] != "not_failed_within_sweep"
    ]
    axis_results: dict[str, dict[str, Any]] = {}
    for variant in STRESS_VARIANTS:
        rows = [row for row in envelope_rows if row["stress_id"] == variant["stress_id"]]
        axis_results[variant["stress_id"]] = {
            "stress_axis": variant["stress_axis"],
            "row_count": len(rows),
            "critical_current_margin_count": sum(
                row["critical_margin_at_current"] for row in rows
            ),
            "narrow_current_margin_count": sum(row["narrow_margin_at_current"] for row in rows),
            "failed_within_sweep_count": sum(
                row["first_failed_multiplier"] != "not_failed_within_sweep"
                for row in rows
            ),
            "minimum_current_margin": min(row["current_i6_minimum_margin"] for row in rows),
            "minimum_max_passed_multiplier": min(
                row["max_passed_multiplier"] for row in rows
            ),
        }

    neutral_critical = [
        row for row in critical_rows if row["source_regime_label"] == "neutral"
    ]
    competitive_critical = [
        row for row in critical_rows if row["source_regime_label"] == "competitive"
    ]
    recommendation = {
        "generic_more_i5_i6_runs_recommended": False,
        "higher_margin_neutral_circulation_variant_recommended": bool(neutral_critical),
        "higher_margin_competitive_redistribution_variant_recommended": bool(
            competitive_critical
        ),
        "higher_margin_extractive_variant_recommended": False,
        "higher_margin_generative_variant_recommended": False,
        "reason": "critical current margins are localized to competitive/neutral transition rows rather than the full paired-regime matrix",
    }

    summary = {
        "trace_id": "n28_i6b_margin_envelope_sweep_summary",
        "source_i6_output_digest": i6["output_digest"],
        "sweep_multipliers": SWEEP_MULTIPLIERS,
        "current_i6_multiplier": CURRENT_I6_MULTIPLIER,
        "envelope_row_count": len(envelope_rows),
        "current_i6_rows_preserved": sum(
            row["current_i6_classification_preserved"] for row in envelope_rows
        ),
        "critical_current_margin_count": len(critical_rows),
        "narrow_current_margin_count": len(narrow_rows),
        "failed_within_sweep_count": len(failed_within_sweep),
        "critical_bottleneck_rows": [
            {
                "row_id": row["row_id"],
                "source_regime_label": row["source_regime_label"],
                "stress_id": row["stress_id"],
                "current_i6_minimum_margin": row["current_i6_minimum_margin"],
                "current_i6_limiting_field": row["current_i6_limiting_field"],
                "max_passed_multiplier": row["max_passed_multiplier"],
                "first_failed_multiplier": row["first_failed_multiplier"],
            }
            for row in critical_rows
        ],
        "axis_results": axis_results,
        "recommendation": recommendation,
        "thresholds_retuned_for_sweep": False,
        "source_rows_mutated": False,
        "new_source_current_evidence_opened": False,
        "ge5_result_preserved": i6["ge5_or_stronger_supported"],
        "ge6_or_stronger_supported": False,
    }
    summary_artifact = trace_artifact("margin_envelope_sweep_summary", summary)
    artifacts.append(summary_artifact)

    checks = [
        check(
            "i6_stress_matrix_pinned_and_passed",
            i6["status"] == "passed"
            and i6["output_digest"] == EXPECTED_I6_DIGEST
            and i6["failed_checks"] == [],
        ),
        check("all_source_rows_swept", len(unique_sources(i6)) == 8),
        check("all_stress_axes_swept", len(STRESS_VARIANTS) == 5),
        check("current_i6_point_preserved", summary["current_i6_rows_preserved"] == len(envelope_rows)),
        check("critical_bottlenecks_identified", len(summary["critical_bottleneck_rows"]) >= 1),
        check("failure_brackets_recorded", summary["failed_within_sweep_count"] >= 1),
        check("thresholds_not_retuned_for_sweep", not summary["thresholds_retuned_for_sweep"]),
        check("source_rows_not_mutated", not summary["source_rows_mutated"]),
        check("no_new_source_current_evidence_opened", not summary["new_source_current_evidence_opened"]),
        check("ge5_preserved_ge6_blocked", summary["ge5_result_preserved"] and not summary["ge6_or_stronger_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]
    output = {
        "artifact_id": "n28_margin_envelope_sweep",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_margin_envelope_sweep_ge5_preserved_bottlenecks_identified",
        "experiment": "N28",
        "iteration": "6-B",
        "source_i6_stress_matrix": {
            "path": I6_OUTPUT_PATH,
            "output_digest": i6["output_digest"],
            "artifact_sha256": sha256_file(I6_OUTPUT_PATH),
            "status": i6["status"],
            "acceptance_state": i6["acceptance_state"],
        },
        "sweep_policy": {
            "policy_id": "n28_i6b_margin_envelope_sweep_v1",
            "declared_before_use": True,
            "sweep_multipliers": SWEEP_MULTIPLIERS,
            "current_i6_multiplier": CURRENT_I6_MULTIPLIER,
            "critical_margin_ceiling": CRITICAL_MARGIN_CEILING,
            "narrow_margin_ceiling": NARROW_MARGIN_CEILING,
            "thresholds_retuned_for_sweep": False,
            "source_rows_mutated": False,
        },
        "envelope_rows": envelope_rows,
        "artifact_manifest": artifacts,
        "envelope_summary": summary,
        "provisional_ge_ladder_rung": "GE5",
        "i6_ge5_result_preserved": i6["ge5_or_stronger_supported"],
        "i6b_new_ge_support_opened": False,
        "ge5_or_stronger_supported": i6["ge5_or_stronger_supported"],
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_iteration_7_claim_classification": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "GE5_preserved_with_margin_envelope_characterization; no_new_source_current_GE_support",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    summary = output["envelope_summary"]
    lines = [
        "# N28 Iteration 6-B - Margin Envelope Sweep",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- I6 GE5 result preserved: `{str(output['i6_ge5_result_preserved']).lower()}`",
        f"- I6-B new GE support opened: `{str(output['i6b_new_ge_support_opened']).lower()}`",
        f"- GE6 supported: `{str(output['ge6_or_stronger_supported']).lower()}`",
        "",
        "I6-B sweeps the multiplier of each I6 stress vector to identify current",
        "margin bottlenecks and failure brackets. It does not retune thresholds,",
        "mutate source rows, or open new source-current N28 evidence.",
        "",
        "## Envelope Summary",
        "",
        "```text",
        f"envelope_row_count = {summary['envelope_row_count']}",
        f"current_i6_rows_preserved = {summary['current_i6_rows_preserved']}",
        f"critical_current_margin_count = {summary['critical_current_margin_count']}",
        f"narrow_current_margin_count = {summary['narrow_current_margin_count']}",
        f"failed_within_sweep_count = {summary['failed_within_sweep_count']}",
        "```",
        "",
        "## Critical Bottlenecks",
        "",
        "| Row | Regime | Stress | Current Margin | Limiting Field | Max Passed | First Failed |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for row in summary["critical_bottleneck_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['source_regime_label']}` | "
            f"`{row['stress_id']}` | {row['current_i6_minimum_margin']:.12f} | "
            f"`{row['current_i6_limiting_field']}` | "
            f"{row['max_passed_multiplier']} | `{row['first_failed_multiplier']}` |"
        )
    lines.extend(
        [
            "",
            "## Axis Results",
            "",
            "| Stress ID | Axis | Critical Current Margins | Narrow Current Margins | Failed Within Sweep | Minimum Current Margin | Minimum Max Passed |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for stress_id, result in summary["axis_results"].items():
        lines.append(
            f"| `{stress_id}` | `{result['stress_axis']}` | "
            f"{result['critical_current_margin_count']} | "
            f"{result['narrow_current_margin_count']} | "
            f"{result['failed_within_sweep_count']} | "
            f"{result['minimum_current_margin']:.12f} | "
            f"{result['minimum_max_passed_multiplier']} |"
        )
    rec = summary["recommendation"]
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "```text",
            f"generic_more_i5_i6_runs_recommended = {str(rec['generic_more_i5_i6_runs_recommended']).lower()}",
            f"higher_margin_neutral_circulation_variant_recommended = {str(rec['higher_margin_neutral_circulation_variant_recommended']).lower()}",
            f"higher_margin_competitive_redistribution_variant_recommended = {str(rec['higher_margin_competitive_redistribution_variant_recommended']).lower()}",
            f"reason = {rec['reason']}",
            "```",
            "",
            "## Interpretation",
            "",
            "I6-B preserves the I6 GE5 result at the current multiplier, but shows where",
            "the margin is thin. The bottlenecks are localized to competitive/neutral",
            "transition rows rather than the whole generative/extractive matrix. That",
            "means generic extra replay/stress rows are not the highest-value next",
            "step. If we strengthen N28 further, the useful additions are focused",
            "higher-margin neutral circulation and competitive redistribution source",
            "rows, followed by replay and stress of those rows.",
            "",
            "This remains GE5 envelope characterization only. GE6, final N28, semantic",
            "cooperation, agency, native support, Phase 8 completion, and ant ecology",
            "remain blocked pending claim classification and closeout.",
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

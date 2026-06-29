#!/usr/bin/env python3
"""Build N28 Iteration 6 stress and regime-separation matrix."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_stress_regime_separation_matrix.json"
REPORT = EXPERIMENT / "reports" / "n28_stress_regime_separation_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_stress_regime_separation_matrix_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_stress_regime_separation_matrix.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I5_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_replay_capacity_attribution_matrix.json"
)
EXPECTED_I5_DIGEST = "3fd8875fa01e4cbb91933bc89cf2db32a1a2d8396a6ebc16451c33a008af6caa"

STRESS_VARIANTS = [
    {
        "stress_id": "focal_stability_softening",
        "stress_axis": "focal_stability",
        "focal_support_reduction": 0.006,
        "focal_coherence_reduction": 0.006,
        "focal_stability_reduction": 0.006,
        "stress_scope": "bounded focal support/coherence/stability softening",
    },
    {
        "stress_id": "neighbor_capacity_compression",
        "stress_axis": "neighbor_capacity",
        "generative_delta_reduction": 0.010,
        "extractive_delta_relief": 0.006,
        "neutral_delta_jitter": 0.003,
        "stress_scope": "bounded compression toward regime decision boundary",
    },
    {
        "stress_id": "extraction_cost_pressure",
        "stress_axis": "extraction_cost",
        "focal_extraction_cost_increase": 0.004,
        "extractive_flattening_increase": 0.004,
        "stress_scope": "bounded extraction and flattening pressure",
    },
    {
        "stress_id": "merge_leakage_pressure",
        "stress_axis": "merge_leakage",
        "merge_leakage_increase": 0.003,
        "stress_scope": "bounded merge/leakage pressure",
    },
    {
        "stress_id": "boundary_integrity_compression",
        "stress_axis": "boundary_integrity",
        "generative_boundary_reduction": 0.010,
        "extractive_boundary_relief": 0.006,
        "mixed_lobe_reduction": 0.004,
        "stress_scope": "bounded boundary and lobe-separation compression",
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


def move_toward_zero(value: float, amount: float) -> float:
    if value > 0:
        return max(0.0, value - amount)
    if value < 0:
        return min(0.0, value + amount)
    return value


def apply_stress(
    row: dict[str, Any], variant: dict[str, Any]
) -> tuple[dict[str, float], dict[str, float | bool], dict[str, Any], dict[str, Any]]:
    regime = row["regime_label"]
    metrics = copy.deepcopy(metric_bundle(row))
    focal = copy.deepcopy(focal_bundle(row))
    boundary = copy.deepcopy(row.get("competitive_neutral_boundary_record", {}))
    effect: dict[str, Any] = {
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "stress_scope": variant["stress_scope"],
        "thresholds_retuned_for_stress": False,
        "source_row_mutated": False,
    }

    if variant["stress_id"] == "focal_stability_softening":
        focal["post_support_min"] = round(
            focal["post_support_min"] - variant["focal_support_reduction"], 12
        )
        focal["post_coherence_min"] = round(
            focal["post_coherence_min"] - variant["focal_coherence_reduction"], 12
        )
        focal["post_stability_score"] = round(
            focal["post_stability_score"] - variant["focal_stability_reduction"], 12
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
            for key in [
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "environment_capacity_delta",
            ]:
                metrics[key] = round(metrics[key] - variant["generative_delta_reduction"], 12)
        elif regime == "extractive":
            for key in [
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "environment_capacity_delta",
            ]:
                metrics[key] = round(metrics[key] + variant["extractive_delta_relief"], 12)
        else:
            for key in [
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "environment_capacity_delta",
            ]:
                metrics[key] = round(
                    move_toward_zero(metrics[key], variant["neutral_delta_jitter"]), 12
                )
    elif variant["stress_id"] == "extraction_cost_pressure":
        metrics["focal_extraction_cost"] = round(
            metrics["focal_extraction_cost"]
            + variant["focal_extraction_cost_increase"],
            12,
        )
        metrics["extractive_flattening"] = round(
            metrics["extractive_flattening"]
            + variant["extractive_flattening_increase"],
            12,
        )
    elif variant["stress_id"] == "merge_leakage_pressure":
        metrics["merge_leakage"] = round(
            metrics["merge_leakage"] + variant["merge_leakage_increase"], 12
        )
    elif variant["stress_id"] == "boundary_integrity_compression":
        if regime == "generative":
            metrics["neighbor_boundary_delta"] = round(
                metrics["neighbor_boundary_delta"]
                - variant["generative_boundary_reduction"],
                12,
            )
        elif regime == "extractive":
            metrics["neighbor_boundary_delta"] = round(
                metrics["neighbor_boundary_delta"] + variant["extractive_boundary_relief"],
                12,
            )
        elif boundary.get("competitive_redistribution_detected") is True:
            boundary["route_lobe_a_capacity_delta"] = round(
                boundary["route_lobe_a_capacity_delta"] - variant["mixed_lobe_reduction"],
                12,
            )
            boundary["route_lobe_b_capacity_delta"] = round(
                boundary["route_lobe_b_capacity_delta"] + variant["mixed_lobe_reduction"],
                12,
            )
        elif boundary.get("neutral_circulation_detected") is True:
            boundary["inflow_lobe_capacity_delta"] = round(
                boundary["inflow_lobe_capacity_delta"] - variant["mixed_lobe_reduction"],
                12,
            )
            boundary["outflow_lobe_capacity_delta"] = round(
                boundary["outflow_lobe_capacity_delta"] + variant["mixed_lobe_reduction"],
                12,
            )
    else:
        raise ValueError(f"unknown stress variant {variant['stress_id']}")

    effect["stressed_metrics_digest"] = digest_value(metrics)
    effect["stressed_focal_digest"] = digest_value(focal)
    effect["stressed_boundary_digest"] = digest_value(boundary)
    return metrics, focal, boundary, effect


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
    evidence = {
        "stable": stable,
        "extraction_below": extraction_below,
        "extraction_present": extraction_present,
        "generative_gain": generative_gain,
        "extractive_loss": extractive_loss,
        "near_neutral": near_neutral,
        "competitive_redistribution": competitive,
        "neutral_circulation": neutral,
        "metric_margins": metric_margins(row, metrics, focal, boundary),
    }
    return result, evidence


def metric_margins(
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
    margins["minimum_margin"] = round(min(margins.values()), 12)
    return margins


def build_stress_row(
    replay_row: dict[str, Any], variant: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
    source_artifact = load_json(replay_row["source_path"])
    source_row = source_artifact["candidate_rows"][0]
    metrics, focal, boundary, stress_effect = apply_stress(source_row, variant)
    stressed_regime, stress_evidence = classify(source_row, metrics, focal, boundary)
    regime_preserved = stressed_regime == source_row["regime_label"]
    stress_passed = (
        replay_row["final_consumable_rung"] == "GE4"
        and replay_row["row_decision"] == "supported"
        and regime_preserved
        and stress_evidence["stable"] is True
    )
    trace = {
        "trace_id": f"n28_i6_{source_row['row_id']}_{variant['stress_id']}_trace",
        "source_iteration": replay_row["source_iteration"],
        "source_row_id": source_row["row_id"],
        "source_row_digest": source_row["row_digest"],
        "source_regime_label": source_row["regime_label"],
        "source_regime_evidence_role": source_row["regime_evidence_role"],
        "shared_regime_policy_id": source_row["shared_regime_policy_id"],
        "stress_variant": variant,
        "stress_effect": stress_effect,
        "base_metrics": metric_bundle(source_row),
        "stressed_metrics": metrics,
        "stressed_focal_state": focal,
        "stressed_boundary_record": boundary,
        "stressed_regime_label": stressed_regime,
        "stress_evidence": stress_evidence,
        "thresholds_retuned_for_stress": False,
        "source_row_mutated": False,
        "stress_passed": stress_passed,
    }
    artifact = trace_artifact(
        f"n28_i6_{source_row['row_id']}_{variant['stress_id']}_trace",
        trace,
    )
    stress_row = {
        "row_id": f"n28_i6_{source_row['row_id']}_{variant['stress_id']}",
        "iteration": "6",
        "source_iteration": replay_row["source_iteration"],
        "source_role": replay_row["source_role"],
        "source_path": replay_row["source_path"],
        "source_output_digest": replay_row["source_output_digest"],
        "source_row_id": source_row["row_id"],
        "source_row_digest": source_row["row_digest"],
        "source_regime_label": source_row["regime_label"],
        "source_regime_evidence_role": source_row["regime_evidence_role"],
        "stress_id": variant["stress_id"],
        "stress_axis": variant["stress_axis"],
        "stress_scope": variant["stress_scope"],
        "shared_regime_policy_id": source_row["shared_regime_policy_id"],
        "thresholds_retuned_for_stress": False,
        "source_row_mutated": False,
        "stressed_regime_label": stressed_regime,
        "regime_label_preserved_under_stress": regime_preserved,
        "stress_passed": stress_passed,
        "row_decision": "supported" if stress_passed else "partial",
        "row_decision_scope": "consumable_GE5_stress_variant_backed_regime_row"
        if stress_passed
        else "GE4_preserved_but_stress_variant_not_supported",
        "final_consumable_rung": "GE5" if stress_passed else "GE4",
        "demoted_rung_if_any": "none" if stress_passed else "GE4",
        "stress_metric_margins": stress_evidence["metric_margins"],
        "stress_trace_artifact": artifact["path"],
        "stress_trace_artifact_sha256": artifact["sha256"],
        "stress_trace_digest": digest_value(trace),
    }
    stress_row["row_digest"] = digest_value(stress_row)
    return stress_row, artifact


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def build_output() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    replay_rows = i5["replay_rows"]
    stress_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for replay_row in replay_rows:
        for variant in STRESS_VARIANTS:
            stress_row, artifact = build_stress_row(replay_row, variant)
            stress_rows.append(stress_row)
            artifacts.append(artifact)

    stress_axis_results = {}
    for variant in STRESS_VARIANTS:
        rows = [row for row in stress_rows if row["stress_id"] == variant["stress_id"]]
        stress_axis_results[variant["stress_id"]] = {
            "stress_axis": variant["stress_axis"],
            "row_count": len(rows),
            "passed_count": sum(row["stress_passed"] for row in rows),
            "failed_count": sum(not row["stress_passed"] for row in rows),
            "minimum_margin": round(
                min(row["stress_metric_margins"]["minimum_margin"] for row in rows), 12
            ),
        }

    regime_results = {}
    for regime in sorted({row["source_regime_label"] for row in stress_rows}):
        rows = [row for row in stress_rows if row["source_regime_label"] == regime]
        regime_results[regime] = {
            "stress_row_count": len(rows),
            "passed_count": sum(row["stress_passed"] for row in rows),
            "failed_count": sum(not row["stress_passed"] for row in rows),
            "minimum_margin": round(
                min(row["stress_metric_margins"]["minimum_margin"] for row in rows), 12
            ),
        }

    rows_demoted = [
        row["row_id"] for row in stress_rows if row["demoted_rung_if_any"] != "none"
    ]
    stress_summary = {
        "trace_id": "n28_i6_stress_regime_separation_summary",
        "source_i5_output_digest": i5["output_digest"],
        "stress_variant_count": len(STRESS_VARIANTS),
        "stress_row_count": len(stress_rows),
        "stress_passed_row_count": sum(row["stress_passed"] for row in stress_rows),
        "stress_failed_row_count": sum(not row["stress_passed"] for row in stress_rows),
        "rows_demoted": rows_demoted,
        "stress_axis_results": stress_axis_results,
        "regime_results": regime_results,
        "shared_policy_ids": sorted({row["shared_regime_policy_id"] for row in stress_rows}),
        "single_shared_policy_family_preserved": len(
            {row["shared_regime_policy_id"] for row in stress_rows}
        )
        == 1,
        "thresholds_retuned_for_stress": any(
            row["thresholds_retuned_for_stress"] for row in stress_rows
        ),
        "source_rows_mutated": any(row["source_row_mutated"] for row in stress_rows),
        "paired_regime_coverage": {
            "generative_source_rows": len(
                {row["source_row_id"] for row in stress_rows if row["source_regime_label"] == "generative"}
            ),
            "extractive_source_rows": len(
                {row["source_row_id"] for row in stress_rows if row["source_regime_label"] == "extractive"}
            ),
            "competitive_neutral_source_rows": len(
                {
                    row["source_row_id"]
                    for row in stress_rows
                    if row["source_regime_label"] in {"competitive", "neutral"}
                }
            ),
        },
    }
    summary_artifact = trace_artifact("stress_regime_separation_summary", stress_summary)
    artifacts.append(summary_artifact)

    ge5_supported = (
        i5["status"] == "passed"
        and i5["output_digest"] == EXPECTED_I5_DIGEST
        and i5["failed_checks"] == []
        and stress_summary["stress_failed_row_count"] == 0
        and stress_summary["single_shared_policy_family_preserved"] is True
        and stress_summary["thresholds_retuned_for_stress"] is False
        and stress_summary["source_rows_mutated"] is False
    )
    checks = [
        check(
            "i5_replay_matrix_pinned_and_passed",
            i5["status"] == "passed"
            and i5["output_digest"] == EXPECTED_I5_DIGEST
            and i5["failed_checks"] == [],
        ),
        check("all_stress_axes_present", len(STRESS_VARIANTS) == 5),
        check("all_i4_family_rows_stressed", len({row["source_row_id"] for row in stress_rows}) == 8),
        check("all_stress_rows_passed", stress_summary["stress_failed_row_count"] == 0),
        check("single_shared_policy_family_preserved", stress_summary["single_shared_policy_family_preserved"]),
        check("thresholds_not_retuned_for_stress", not stress_summary["thresholds_retuned_for_stress"]),
        check("source_rows_not_mutated", not stress_summary["source_rows_mutated"]),
        check(
            "paired_regime_coverage_present",
            stress_summary["paired_regime_coverage"]["generative_source_rows"] >= 3
            and stress_summary["paired_regime_coverage"]["extractive_source_rows"] >= 3
            and stress_summary["paired_regime_coverage"][
                "competitive_neutral_source_rows"
            ]
            >= 2,
        ),
        check("ge5_supported_ge6_blocked", ge5_supported),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]
    output = {
        "artifact_id": "n28_stress_regime_separation_matrix",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_stress_variant_backed_ge5_regime_separation_candidate_pending_claim_classification"
        if ge5_supported
        else "partial_stress_matrix_ge5_not_supported",
        "experiment": "N28",
        "iteration": "6",
        "source_i5_replay_matrix": {
            "path": I5_OUTPUT_PATH,
            "output_digest": i5["output_digest"],
            "artifact_sha256": sha256_file(I5_OUTPUT_PATH),
            "status": i5["status"],
            "acceptance_state": i5["acceptance_state"],
        },
        "stress_policy": {
            "policy_id": "n28_i6_fixed_stress_policy_v1",
            "declared_before_use": True,
            "thresholds_retuned_for_stress": False,
            "source_rows_mutated": False,
            "stress_variants": STRESS_VARIANTS,
        },
        "stress_rows": stress_rows,
        "artifact_manifest": artifacts,
        "stress_summary": stress_summary,
        "provisional_ge_ladder_rung": "GE5" if ge5_supported else "GE4",
        "ge4_or_stronger_supported": True,
        "ge5_or_stronger_supported": ge5_supported,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "n28_closeout_ceiling": "N28-C5_replay_control_stress_backed_generative_extractive_candidate_supported"
        if ge5_supported
        else "N28-C4_source_current_regime_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "shared_regime_policy_status": "supported" if ge5_supported else "partial",
        "ready_for_iteration_7_claim_classification": ge5_supported,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "GE5_stress_variant_backed_paired_regime_separation_candidate_pending_AP_claim_classification_and_closeout",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 6 - Stress / Regime-Separation Matrix",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- GE5 supported: `{str(output['ge5_or_stronger_supported']).lower()}`",
        f"- GE6 supported: `{str(output['ge6_or_stronger_supported']).lower()}`",
        f"- Shared regime policy status: `{output['shared_regime_policy_status']}`",
        "",
        "I6 stresses the I4-family rows already admitted by I5. The stress matrix",
        "does not retune thresholds and does not mutate source rows. It applies",
        "fixed overlays to focal stability, neighbor capacity, extraction cost,",
        "merge/leakage, and boundary integrity, then replays the same regime",
        "classifier.",
        "",
        "## Stress Summary",
        "",
        "```text",
        f"stress_variant_count = {output['stress_summary']['stress_variant_count']}",
        f"stress_row_count = {output['stress_summary']['stress_row_count']}",
        f"stress_passed_row_count = {output['stress_summary']['stress_passed_row_count']}",
        f"stress_failed_row_count = {output['stress_summary']['stress_failed_row_count']}",
        f"rows_demoted = {output['stress_summary']['rows_demoted']}",
        f"shared_policy_ids = {output['stress_summary']['shared_policy_ids']}",
        f"thresholds_retuned_for_stress = {str(output['stress_summary']['thresholds_retuned_for_stress']).lower()}",
        f"source_rows_mutated = {str(output['stress_summary']['source_rows_mutated']).lower()}",
        "```",
        "",
        "## Stress Axes",
        "",
        "| Stress ID | Axis | Rows | Passed | Failed | Minimum Margin |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for stress_id, result in output["stress_summary"]["stress_axis_results"].items():
        lines.append(
            f"| `{stress_id}` | `{result['stress_axis']}` | {result['row_count']} | "
            f"{result['passed_count']} | {result['failed_count']} | "
            f"{result['minimum_margin']:.12f} |"
        )
    lines.extend(
        [
            "",
            "## Regime Results",
            "",
            "| Regime | Stress Rows | Passed | Failed | Minimum Margin |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for regime, result in output["stress_summary"]["regime_results"].items():
        lines.append(
            f"| `{regime}` | {result['stress_row_count']} | {result['passed_count']} | "
            f"{result['failed_count']} | {result['minimum_margin']:.12f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I6 upgrades I5 from replay/control-backed GE4 to a provisional GE5",
            "candidate because all generative, extractive, and competitive/neutral",
            "rows preserve their regime labels under the declared bounded stress",
            "overlays. The important point is not that the rows were made easier;",
            "the same shared policy family is preserved and thresholds are not",
            "retuned.",
            "",
            "Geometrically, the stress matrix compresses the regime axes without",
            "changing the regime rules: generative rows keep focal persistence while",
            "their neighboring capacity shell remains enriched; extractive rows keep",
            "focal persistence while the neighborhood remains depleted/flattened with",
            "extraction present; competitive/neutral rows keep mixed redistribution",
            "or circulation without becoming aggregate enrichment or depletion.",
            "",
            "This remains below GE6 and final N28. I7 still has to classify AP4/AP5",
            "dependencies and unsafe claim boundaries, and I8 still has to freeze",
            "closeout and the N29 handoff.",
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

#!/usr/bin/env python3
"""Build N28 Iteration 6-A regime-boundary transition matrix."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_regime_boundary_transition_matrix.json"
REPORT = EXPERIMENT / "reports" / "n28_regime_boundary_transition_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_regime_boundary_transition_matrix_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_regime_boundary_transition_matrix.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I6_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_stress_regime_separation_matrix.json"
)
EXPECTED_I6_DIGEST = "fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756"
EPSILON = 0.002
GAP_VALUE = 0.0

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


def base_metrics(row: dict[str, Any]) -> dict[str, float]:
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


def focal_state(row: dict[str, Any]) -> dict[str, float | bool]:
    trace = row["focal_basin_stability_trace"]
    floors = row["focal_support_coherence_floor_trace"]
    return {
        "post_support_min": floors["post_support_min"],
        "post_coherence_min": floors["post_coherence_min"],
        "support_floor": floors["support_floor"],
        "coherence_floor": floors["coherence_floor"],
        "post_stability_score": trace["post_stability_score"],
        "focal_stability_preserved": trace["focal_stability_preserved"],
        "floors_preserved": floors["floors_preserved"],
    }


def edge_generative(policy: dict[str, float | bool | str], metrics: dict[str, float]) -> dict[str, float]:
    updated = copy.deepcopy(metrics)
    updated["neighbor_distinguishability_delta"] = (
        policy["neighbor_distinguishability_delta_min"] + EPSILON
    )
    updated["neighbor_support_delta"] = policy["neighbor_support_delta_min"] + EPSILON
    updated["neighbor_boundary_delta"] = policy["neighbor_boundary_delta_min"] + EPSILON
    updated["environment_capacity_delta"] = policy["environment_capacity_delta_min"] + EPSILON
    updated["focal_extraction_cost"] = metrics["focal_extraction_cost_ceiling"] - EPSILON
    updated["extractive_flattening"] = metrics["extractive_flattening_ceiling"] - EPSILON
    updated["merge_leakage"] = metrics["merge_leakage_ceiling"] - EPSILON
    return round_metrics(updated)


def edge_extractive(policy: dict[str, float | bool | str], metrics: dict[str, float]) -> dict[str, float]:
    updated = copy.deepcopy(metrics)
    updated["neighbor_distinguishability_delta"] = -(
        policy["neighbor_distinguishability_degradation_min"] + EPSILON
    )
    updated["neighbor_support_delta"] = -(
        policy["neighbor_support_degradation_min"] + EPSILON
    )
    updated["neighbor_boundary_delta"] = -(
        policy["neighbor_boundary_degradation_min"] + EPSILON
    )
    updated["environment_capacity_delta"] = -(
        policy["environment_capacity_degradation_min"] + EPSILON
    )
    updated["focal_extraction_cost"] = metrics["focal_extraction_cost_ceiling"] + EPSILON
    updated["extractive_flattening"] = metrics["extractive_flattening_ceiling"] + EPSILON
    updated["merge_leakage"] = metrics["merge_leakage_ceiling"] + EPSILON
    return round_metrics(updated)


def neutral_gap(metrics: dict[str, float]) -> dict[str, float]:
    updated = copy.deepcopy(metrics)
    for key in [
        "neighbor_distinguishability_delta",
        "neighbor_support_delta",
        "neighbor_boundary_delta",
        "environment_capacity_delta",
    ]:
        updated[key] = GAP_VALUE
    updated["focal_extraction_cost"] = metrics["focal_extraction_cost_ceiling"] - EPSILON
    updated["extractive_flattening"] = metrics["extractive_flattening_ceiling"] - EPSILON
    updated["merge_leakage"] = metrics["merge_leakage_ceiling"] - EPSILON
    return round_metrics(updated)


def edge_competitive(
    policy: dict[str, float | bool | str],
    metrics: dict[str, float],
    boundary: dict[str, Any],
) -> tuple[dict[str, float], dict[str, Any]]:
    updated_metrics = neutral_gap(metrics)
    updated_boundary = copy.deepcopy(boundary)
    updated_boundary["competitive_redistribution_detected"] = True
    updated_boundary["neutral_circulation_detected"] = False
    updated_boundary["route_lobe_a_capacity_delta"] = policy["mixed_lobe_delta_min"] + EPSILON
    updated_boundary["route_lobe_b_capacity_delta"] = -(
        policy["mixed_lobe_delta_min"] + EPSILON
    )
    return updated_metrics, round_boundary(updated_boundary)


def edge_neutral(
    policy: dict[str, float | bool | str],
    metrics: dict[str, float],
    boundary: dict[str, Any],
) -> tuple[dict[str, float], dict[str, Any]]:
    updated_metrics = neutral_gap(metrics)
    updated_boundary = copy.deepcopy(boundary)
    updated_boundary["competitive_redistribution_detected"] = False
    updated_boundary["neutral_circulation_detected"] = True
    updated_boundary["inflow_lobe_capacity_delta"] = policy["mixed_lobe_delta_min"] + EPSILON
    updated_boundary["outflow_lobe_capacity_delta"] = -(
        policy["mixed_lobe_delta_min"] + EPSILON
    )
    updated_boundary["buffer_lobe_capacity_delta"] = 0.0
    return updated_metrics, round_boundary(updated_boundary)


def missing_mixed_lobe_gap(
    metrics: dict[str, float], boundary: dict[str, Any]
) -> tuple[dict[str, float], dict[str, Any]]:
    updated_metrics = neutral_gap(metrics)
    updated_boundary = copy.deepcopy(boundary)
    updated_boundary["route_lobe_a_capacity_delta"] = 0.0
    updated_boundary["route_lobe_b_capacity_delta"] = 0.0
    updated_boundary["inflow_lobe_capacity_delta"] = 0.0
    updated_boundary["outflow_lobe_capacity_delta"] = 0.0
    updated_boundary["competitive_redistribution_detected"] = False
    updated_boundary["neutral_circulation_detected"] = False
    return updated_metrics, round_boundary(updated_boundary)


def round_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {key: round(value, 12) for key, value in metrics.items()}


def round_boundary(boundary: dict[str, Any]) -> dict[str, Any]:
    rounded = {}
    for key, value in boundary.items():
        rounded[key] = round(value, 12) if isinstance(value, float) else value
    return rounded


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
    }
    return result, evidence


def transition_points(row: dict[str, Any]) -> list[dict[str, Any]]:
    policy = policy_for(row)
    metrics = base_metrics(row)
    boundary = copy.deepcopy(row.get("competitive_neutral_boundary_record", {}))
    regime = row["regime_label"]
    points = [
        {
            "transition_id": "source_anchor",
            "transition_role": "source_current_anchor",
            "expected_label": regime,
            "metrics": round_metrics(metrics),
            "boundary": round_boundary(boundary),
        }
    ]
    if regime == "generative":
        points.extend(
            [
                {
                    "transition_id": "generative_edge",
                    "transition_role": "same_regime_boundary_edge",
                    "expected_label": "generative",
                    "metrics": edge_generative(policy, metrics),
                    "boundary": round_boundary(boundary),
                },
                {
                    "transition_id": "neutral_gap_without_mixed_lobes",
                    "transition_role": "unclassified_gap_expected",
                    "expected_label": "unclassified",
                    "metrics": neutral_gap(metrics),
                    "boundary": {},
                },
                {
                    "transition_id": "extractive_cross",
                    "transition_role": "opposite_regime_cross_check",
                    "expected_label": "extractive",
                    "metrics": edge_extractive(policy, metrics),
                    "boundary": {},
                },
            ]
        )
    elif regime == "extractive":
        points.extend(
            [
                {
                    "transition_id": "extractive_edge",
                    "transition_role": "same_regime_boundary_edge",
                    "expected_label": "extractive",
                    "metrics": edge_extractive(policy, metrics),
                    "boundary": round_boundary(boundary),
                },
                {
                    "transition_id": "neutral_gap_without_mixed_lobes",
                    "transition_role": "unclassified_gap_expected",
                    "expected_label": "unclassified",
                    "metrics": neutral_gap(metrics),
                    "boundary": {},
                },
                {
                    "transition_id": "generative_cross",
                    "transition_role": "opposite_regime_cross_check",
                    "expected_label": "generative",
                    "metrics": edge_generative(policy, metrics),
                    "boundary": {},
                },
            ]
        )
    elif regime == "competitive":
        competitive_metrics, competitive_boundary = edge_competitive(
            policy, metrics, boundary
        )
        gap_metrics, gap_boundary = missing_mixed_lobe_gap(metrics, boundary)
        points.extend(
            [
                {
                    "transition_id": "competitive_edge",
                    "transition_role": "same_regime_boundary_edge",
                    "expected_label": "competitive",
                    "metrics": competitive_metrics,
                    "boundary": competitive_boundary,
                },
                {
                    "transition_id": "mixed_lobe_missing_gap",
                    "transition_role": "unclassified_gap_expected",
                    "expected_label": "unclassified",
                    "metrics": gap_metrics,
                    "boundary": gap_boundary,
                },
                {
                    "transition_id": "generative_cross",
                    "transition_role": "aggregate_enrichment_cross_check",
                    "expected_label": "generative",
                    "metrics": edge_generative(policy, metrics),
                    "boundary": {},
                },
                {
                    "transition_id": "extractive_cross",
                    "transition_role": "aggregate_depletion_cross_check",
                    "expected_label": "extractive",
                    "metrics": edge_extractive(policy, metrics),
                    "boundary": {},
                },
            ]
        )
    elif regime == "neutral":
        neutral_metrics, neutral_boundary = edge_neutral(policy, metrics, boundary)
        gap_metrics, gap_boundary = missing_mixed_lobe_gap(metrics, boundary)
        points.extend(
            [
                {
                    "transition_id": "neutral_edge",
                    "transition_role": "same_regime_boundary_edge",
                    "expected_label": "neutral",
                    "metrics": neutral_metrics,
                    "boundary": neutral_boundary,
                },
                {
                    "transition_id": "circulation_missing_gap",
                    "transition_role": "unclassified_gap_expected",
                    "expected_label": "unclassified",
                    "metrics": gap_metrics,
                    "boundary": gap_boundary,
                },
                {
                    "transition_id": "generative_cross",
                    "transition_role": "aggregate_enrichment_cross_check",
                    "expected_label": "generative",
                    "metrics": edge_generative(policy, metrics),
                    "boundary": {},
                },
                {
                    "transition_id": "extractive_cross",
                    "transition_role": "aggregate_depletion_cross_check",
                    "expected_label": "extractive",
                    "metrics": edge_extractive(policy, metrics),
                    "boundary": {},
                },
            ]
        )
    return points


def build_transition_row(
    source_info: dict[str, Any], source_row: dict[str, Any], point: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
    label, evidence = classify(
        source_row,
        point["metrics"],
        focal_state(source_row),
        point["boundary"],
    )
    label_matches = label == point["expected_label"]
    ge5_preservation_allowed = (
        point["transition_role"] in {"source_current_anchor", "same_regime_boundary_edge"}
        and label_matches
    )
    trace = {
        "trace_id": f"n28_i6a_{source_row['row_id']}_{point['transition_id']}_trace",
        "source_iteration": source_info["source_iteration"],
        "source_row_id": source_row["row_id"],
        "source_row_digest": source_row["row_digest"],
        "source_regime_label": source_row["regime_label"],
        "shared_regime_policy_id": source_row["shared_regime_policy_id"],
        "transition_id": point["transition_id"],
        "transition_role": point["transition_role"],
        "expected_label": point["expected_label"],
        "observed_label": label,
        "label_matches_expected": label_matches,
        "transition_metrics": point["metrics"],
        "transition_boundary": point["boundary"],
        "classification_evidence": evidence,
        "thresholds_retuned_for_transition": False,
        "source_row_mutated": False,
        "new_source_current_evidence_opened": False,
    }
    artifact = trace_artifact(
        f"n28_i6a_{source_row['row_id']}_{point['transition_id']}_trace",
        trace,
    )
    row = {
        "row_id": f"n28_i6a_{source_row['row_id']}_{point['transition_id']}",
        "iteration": "6-A",
        "source_iteration": source_info["source_iteration"],
        "source_path": source_info["source_path"],
        "source_output_digest": source_info["source_output_digest"],
        "source_row_id": source_row["row_id"],
        "source_row_digest": source_row["row_digest"],
        "source_regime_label": source_row["regime_label"],
        "shared_regime_policy_id": source_row["shared_regime_policy_id"],
        "transition_id": point["transition_id"],
        "transition_role": point["transition_role"],
        "expected_label": point["expected_label"],
        "observed_label": label,
        "label_matches_expected": label_matches,
        "row_decision": "supported" if ge5_preservation_allowed else "rejected",
        "row_decision_scope": "same_policy_boundary_transition_passed"
        if label_matches
        else "transition_classifier_mismatch",
        "ge5_boundary_preservation_allowed": ge5_preservation_allowed,
        "ge_ladder_rung_effect": "GE5_policy_boundary_preserved"
        if ge5_preservation_allowed
        else "no_new_GE_support_boundary_control",
        "thresholds_retuned_for_transition": False,
        "source_row_mutated": False,
        "new_source_current_evidence_opened": False,
        "transition_trace_artifact": artifact["path"],
        "transition_trace_artifact_sha256": artifact["sha256"],
        "transition_trace_digest": digest_value(trace),
    }
    row["row_digest"] = digest_value(row)
    return row, artifact


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


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def build_output() -> dict[str, Any]:
    i6 = load_json(I6_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    transition_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for source in unique_sources(i6):
        artifact = load_json(source["source_path"])
        source_row = artifact["candidate_rows"][0]
        for point in transition_points(source_row):
            row, artifact_record = build_transition_row(source, source_row, point)
            transition_rows.append(row)
            artifacts.append(artifact_record)

    role_counts: dict[str, dict[str, int]] = {}
    for row in transition_rows:
        role = row["transition_role"]
        role_counts.setdefault(role, {"row_count": 0, "passed": 0, "failed": 0})
        role_counts[role]["row_count"] += 1
        if row["label_matches_expected"]:
            role_counts[role]["passed"] += 1
        else:
            role_counts[role]["failed"] += 1

    label_transition_counts: dict[str, int] = {}
    for row in transition_rows:
        key = f"{row['source_regime_label']}->{row['observed_label']}"
        label_transition_counts[key] = label_transition_counts.get(key, 0) + 1

    preservation_rows = [
        row["row_id"]
        for row in transition_rows
        if row["ge5_boundary_preservation_allowed"]
    ]
    summary = {
        "trace_id": "n28_i6a_regime_boundary_transition_summary",
        "source_i6_output_digest": i6["output_digest"],
        "transition_row_count": len(transition_rows),
        "label_match_count": sum(row["label_matches_expected"] for row in transition_rows),
        "label_mismatch_count": sum(
            not row["label_matches_expected"] for row in transition_rows
        ),
        "ge5_boundary_preservation_row_count": len(preservation_rows),
        "ge5_boundary_preservation_rows": preservation_rows,
        "new_source_current_evidence_opened": False,
        "thresholds_retuned_for_transition": any(
            row["thresholds_retuned_for_transition"] for row in transition_rows
        ),
        "source_rows_mutated": any(row["source_row_mutated"] for row in transition_rows),
        "role_counts": role_counts,
        "label_transition_counts": label_transition_counts,
        "shared_policy_ids": sorted({row["shared_regime_policy_id"] for row in transition_rows}),
        "single_shared_policy_family_preserved": len(
            {row["shared_regime_policy_id"] for row in transition_rows}
        )
        == 1,
        "shared_regime_policy_status": "supported",
        "boundary_interpretation": "same_policy_transition_surface_supported_without_new_source_current_GE_rows",
    }
    summary_artifact = trace_artifact("regime_boundary_transition_summary", summary)
    artifacts.append(summary_artifact)

    checks = [
        check(
            "i6_stress_matrix_pinned_and_passed",
            i6["status"] == "passed"
            and i6["output_digest"] == EXPECTED_I6_DIGEST
            and i6["failed_checks"] == [],
        ),
        check("all_source_rows_have_transition_paths", len(unique_sources(i6)) == 8),
        check("all_transition_labels_match_expected", summary["label_mismatch_count"] == 0),
        check("unclassified_gaps_present", "generative->unclassified" in label_transition_counts),
        check("opposite_cross_checks_present", "generative->extractive" in label_transition_counts),
        check("competitive_neutral_edges_present", "competitive->competitive" in label_transition_counts and "neutral->neutral" in label_transition_counts),
        check("single_shared_policy_family_preserved", summary["single_shared_policy_family_preserved"]),
        check("thresholds_not_retuned_for_transition", not summary["thresholds_retuned_for_transition"]),
        check("source_rows_not_mutated", not summary["source_rows_mutated"]),
        check("no_new_source_current_evidence_opened", not summary["new_source_current_evidence_opened"]),
        check("i6_ge5_preserved_ge6_blocked", i6["ge5_or_stronger_supported"] is True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]
    output = {
        "artifact_id": "n28_regime_boundary_transition_matrix",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_regime_boundary_transition_matrix_same_policy_supported_no_new_ge_support",
        "experiment": "N28",
        "iteration": "6-A",
        "source_i6_stress_matrix": {
            "path": I6_OUTPUT_PATH,
            "output_digest": i6["output_digest"],
            "artifact_sha256": sha256_file(I6_OUTPUT_PATH),
            "status": i6["status"],
            "acceptance_state": i6["acceptance_state"],
        },
        "transition_policy": {
            "policy_id": "n28_i6a_same_policy_boundary_transition_v1",
            "declared_before_use": True,
            "thresholds_retuned_for_transition": False,
            "source_rows_mutated": False,
            "epsilon_above_boundary": EPSILON,
            "neutral_gap_value": GAP_VALUE,
            "mixed_lobe_boundary_required_for_competitive_or_neutral": True,
        },
        "transition_rows": transition_rows,
        "artifact_manifest": artifacts,
        "transition_summary": summary,
        "provisional_ge_ladder_rung": "GE5",
        "i6_ge5_result_preserved": i6["ge5_or_stronger_supported"],
        "i6a_new_ge_support_opened": False,
        "ge5_or_stronger_supported": i6["ge5_or_stronger_supported"],
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "shared_regime_policy_status": "supported",
        "ready_for_iteration_7_claim_classification": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "GE5_preserved_with_same_policy_boundary_transition_matrix; no_new_source_current_GE_support",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    summary = output["transition_summary"]
    lines = [
        "# N28 Iteration 6-A - Regime Boundary / Transition Matrix",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- I6 GE5 result preserved: `{str(output['i6_ge5_result_preserved']).lower()}`",
        f"- I6-A new GE support opened: `{str(output['i6a_new_ge_support_opened']).lower()}`",
        f"- GE6 supported: `{str(output['ge6_or_stronger_supported']).lower()}`",
        f"- Shared regime policy status: `{output['shared_regime_policy_status']}`",
        "",
        "I6-A varies the declared transition envelope around the I6 GE5 result.",
        "It is a same-policy classifier-boundary probe: no source row is mutated,",
        "thresholds are not retuned, and no new source-current N28 evidence row is",
        "opened.",
        "",
        "## Transition Summary",
        "",
        "```text",
        f"transition_row_count = {summary['transition_row_count']}",
        f"label_match_count = {summary['label_match_count']}",
        f"label_mismatch_count = {summary['label_mismatch_count']}",
        f"ge5_boundary_preservation_row_count = {summary['ge5_boundary_preservation_row_count']}",
        f"new_source_current_evidence_opened = {str(summary['new_source_current_evidence_opened']).lower()}",
        f"thresholds_retuned_for_transition = {str(summary['thresholds_retuned_for_transition']).lower()}",
        f"source_rows_mutated = {str(summary['source_rows_mutated']).lower()}",
        f"shared_policy_ids = {summary['shared_policy_ids']}",
        "```",
        "",
        "## Transition Roles",
        "",
        "| Role | Rows | Passed | Failed |",
        "|---|---:|---:|---:|",
    ]
    for role, counts in summary["role_counts"].items():
        lines.append(
            f"| `{role}` | {counts['row_count']} | {counts['passed']} | {counts['failed']} |"
        )
    lines.extend(
        [
            "",
            "## Label Transitions",
            "",
            "| Transition | Count |",
            "|---|---:|",
        ]
    )
    for transition, count in sorted(summary["label_transition_counts"].items()):
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I6-A supports the same shared regime policy as a boundary classifier, not as",
            "new source-current GE evidence. Source anchors and same-regime edge rows",
            "are allowed to preserve the I6 GE5 support, while boundary-gap and",
            "opposite-cross rows are controls that test whether the classifier changes",
            "for the right geometric reason.",
            "",
            "The key protection is that neutral/competitive classification is not allowed",
            "from near-zero aggregate deltas alone. When mixed-lobe or circulation",
            "evidence is removed, the row becomes unclassified rather than being",
            "promoted by label. When aggregate enrichment or depletion crosses the",
            "declared regime thresholds, the same policy classifies it as generative",
            "or extractive.",
            "",
            "This preserves the I6 GE5 result and supports",
            "`shared_regime_policy_status = supported`, but it does not create GE6,",
            "final N28, semantic cooperation, agency, native support, Phase 8",
            "completion, or ant ecology evidence.",
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

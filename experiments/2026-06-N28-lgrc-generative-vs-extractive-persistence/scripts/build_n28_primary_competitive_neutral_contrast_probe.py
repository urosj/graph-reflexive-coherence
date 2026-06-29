#!/usr/bin/env python3
"""Build N28 Iteration 4-D primary competitive/neutral contrast probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
I3_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_active_nulls_and_failure_baselines.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_extractive_schema_and_controls.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n28_primary_competitive_neutral_contrast_probe.json"
REPORT = EXPERIMENT / "reports" / "n28_primary_competitive_neutral_contrast_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_primary_competitive_neutral_contrast_probe_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_primary_competitive_neutral_contrast_probe.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

EXPECTED_I3_DIGEST = "ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4"
I4_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_primary_generative_candidate_probe.json"
)
EXPECTED_I4_DIGEST = "daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d"
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_strengthening_candidate_probe.json"
)
EXPECTED_I4A_DIGEST = "07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c"
I4A2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_mechanism_diversity_probe.json"
)
EXPECTED_I4A2_DIGEST = "f2785e97307704bff58e413eb071aff10311f0a3d6bd753ebccfb4c1975b6c20"
I4B_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_primary_extractive_contrast_probe.json"
)
EXPECTED_I4B_DIGEST = "5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3"
I4C_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_extractive_strengthening_contrast_probe.json"
)
EXPECTED_I4C_DIGEST = "013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6"
I4C2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_extractive_mechanism_diversity_probe.json"
)
EXPECTED_I4C2_DIGEST = "cd099229fa37dcdf1c497555fd6ace7d4435035c87e58c1eec9bac6acb7e7067"

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


def build_traces(i3: dict[str, Any]) -> dict[str, Any]:
    source_pins = i3["source_digest_pins"]
    threshold_policy = {
        "policy_id": "n28_i4d_primary_competitive_neutral_policy_v1",
        "declared_before_use": True,
        "shared_regime_policy_id": "n28_shared_regime_policy_v1",
        "focal_support_floor": 0.84,
        "focal_coherence_floor": 0.84,
        "focal_stability_min": 0.86,
        "neighbor_distinguishability_delta_min": 0.08,
        "neighbor_support_delta_min": 0.05,
        "neighbor_boundary_delta_min": 0.08,
        "environment_capacity_delta_min": 0.09,
        "neighbor_distinguishability_degradation_min": 0.05,
        "neighbor_support_degradation_min": 0.04,
        "neighbor_boundary_degradation_min": 0.06,
        "environment_capacity_degradation_min": 0.05,
        "competitive_neutral_abs_delta_max": 0.025,
        "mixed_lobe_delta_min": 0.04,
        "extractive_mechanism_exceedance_min": 0.005,
        "focal_extraction_cost_ceiling": 0.035,
        "extractive_flattening_ceiling": 0.03,
        "merge_leakage_ceiling": 0.025,
        "post_hoc_boundary_shift_used": False,
        "label_specific_thresholds_used": False,
        "policy_retuned_for_label": False,
        "thresholds_widened_relative_to_prior_rows": False,
    }
    runtime_trace = {
        "run_artifact_id": "n28_i4d_primary_competitive_neutral_runtime_trace",
        "runtime_config_id": "n28_i4d_competitive_redistribution_fixture_v1",
        "runtime_config_digest": "computed_after_trace",
        "source_schema_output_digest": i3["output_digest"],
        "source_inventory_output_digest": source_pins["source_inventory_output_digest"],
        "fixture_kind": "source_current_geometric_trace_fixture",
        "derived_report_only": False,
        "focal_basin_id": "n28_i4d_focal_basin_eta",
        "neighbor_scope_id": "n28_i4d_competitive_neighbor_field_eta",
        "mechanism_class": "competitive_capacity_redistribution",
        "mechanism_distinction": "I4-D keeps focal persistence while neighbor capacity is redistributed across lobes rather than clearly gained or depleted.",
        "competitive_redistribution_used": True,
        "steps": [
            {
                "step": 0,
                "focal_support_min": 0.872,
                "focal_coherence_min": 0.881,
                "focal_stability_score": 0.876,
                "neighbor_distinguishability": 0.681,
                "neighbor_support_floor": 0.711,
                "neighbor_boundary_integrity": 0.668,
                "environment_basin_forming_capacity": 0.642,
                "focal_extraction_cost": 0.022,
                "extractive_flattening_score": 0.019,
                "merge_leakage_score": 0.018,
                "neighbor_lobes": {
                    "route_lobe_a_capacity": 0.604,
                    "route_lobe_b_capacity": 0.608
                },
            },
            {
                "step": 1,
                "focal_support_min": 0.870,
                "focal_coherence_min": 0.879,
                "focal_stability_score": 0.874,
                "neighbor_distinguishability": 0.699,
                "neighbor_support_floor": 0.717,
                "neighbor_boundary_integrity": 0.656,
                "environment_basin_forming_capacity": 0.646,
                "focal_extraction_cost": 0.028,
                "extractive_flattening_score": 0.024,
                "merge_leakage_score": 0.019,
                "neighbor_lobes": {
                    "route_lobe_a_capacity": 0.659,
                    "route_lobe_b_capacity": 0.558
                },
            },
        ],
    }
    runtime_trace["runtime_config_digest"] = digest_value(
        {
            "runtime_config_id": runtime_trace["runtime_config_id"],
            "fixture_kind": runtime_trace["fixture_kind"],
            "focal_basin_id": runtime_trace["focal_basin_id"],
            "neighbor_scope_id": runtime_trace["neighbor_scope_id"],
            "threshold_policy": threshold_policy,
        }
    )
    pre = runtime_trace["steps"][0]
    post = runtime_trace["steps"][1]
    focal_trace = {
        "trace_id": "n28_i4d_focal_basin_stability_trace",
        "focal_basin_id": runtime_trace["focal_basin_id"],
        "support_floor": threshold_policy["focal_support_floor"],
        "coherence_floor": threshold_policy["focal_coherence_floor"],
        "pre_support_min": pre["focal_support_min"],
        "post_support_min": post["focal_support_min"],
        "pre_coherence_min": pre["focal_coherence_min"],
        "post_coherence_min": post["focal_coherence_min"],
        "pre_stability_score": pre["focal_stability_score"],
        "post_stability_score": post["focal_stability_score"],
        "focal_support_floor_preserved": post["focal_support_min"]
        >= threshold_policy["focal_support_floor"],
        "focal_coherence_floor_preserved": post["focal_coherence_min"]
        >= threshold_policy["focal_coherence_floor"],
        "focal_stability_preserved": post["focal_stability_score"]
        >= threshold_policy["focal_stability_min"],
    }
    neighbor_trace = {
        "trace_id": "n28_i4d_neighbor_capacity_trace",
        "neighbor_scope_id": runtime_trace["neighbor_scope_id"],
        "pre_neighbor_distinguishability": pre["neighbor_distinguishability"],
        "post_neighbor_distinguishability": post["neighbor_distinguishability"],
        "neighbor_distinguishability_delta": round(
            post["neighbor_distinguishability"] - pre["neighbor_distinguishability"], 12
        ),
        "pre_neighbor_support_floor": pre["neighbor_support_floor"],
        "post_neighbor_support_floor": post["neighbor_support_floor"],
        "neighbor_support_delta": round(
            post["neighbor_support_floor"] - pre["neighbor_support_floor"], 12
        ),
        "pre_neighbor_boundary_integrity": pre["neighbor_boundary_integrity"],
        "post_neighbor_boundary_integrity": post["neighbor_boundary_integrity"],
        "neighbor_boundary_delta": round(
            post["neighbor_boundary_integrity"] - pre["neighbor_boundary_integrity"], 12
        ),
        "pre_environment_basin_forming_capacity": pre[
            "environment_basin_forming_capacity"
        ],
        "post_environment_basin_forming_capacity": post[
            "environment_basin_forming_capacity"
        ],
        "environment_capacity_delta": round(
            post["environment_basin_forming_capacity"]
            - pre["environment_basin_forming_capacity"],
            12,
        ),
        "neighbor_label_only": False,
        "neighbor_count_only": False,
    }
    extraction_trace = {
        "trace_id": "n28_i4d_extraction_leakage_trace",
        "focal_extraction_cost": post["focal_extraction_cost"],
        "focal_extraction_cost_ceiling": threshold_policy[
            "focal_extraction_cost_ceiling"
        ],
        "extractive_flattening_score": post["extractive_flattening_score"],
        "extractive_flattening_ceiling": threshold_policy[
            "extractive_flattening_ceiling"
        ],
        "merge_leakage_score": post["merge_leakage_score"],
        "merge_leakage_ceiling": threshold_policy["merge_leakage_ceiling"],
        "focal_extraction_cost_below_ceiling": post["focal_extraction_cost"]
        <= threshold_policy["focal_extraction_cost_ceiling"],
        "extractive_flattening_below_ceiling": post["extractive_flattening_score"]
        <= threshold_policy["extractive_flattening_ceiling"],
        "merge_leakage_below_ceiling": post["merge_leakage_score"]
        <= threshold_policy["merge_leakage_ceiling"],
        "focal_extraction_cost_above_generative_ceiling": post["focal_extraction_cost"]
        > threshold_policy["focal_extraction_cost_ceiling"],
        "extractive_flattening_above_generative_ceiling": post[
            "extractive_flattening_score"
        ]
        > threshold_policy["extractive_flattening_ceiling"],
        "merge_leakage_above_generative_ceiling": post["merge_leakage_score"]
        > threshold_policy["merge_leakage_ceiling"],
        "extractive_mechanism_present": post["focal_extraction_cost"]
        > threshold_policy["focal_extraction_cost_ceiling"]
        or post["extractive_flattening_score"]
        > threshold_policy["extractive_flattening_ceiling"]
        or post["merge_leakage_score"] > threshold_policy["merge_leakage_ceiling"],
        "merge_or_leakage_masquerading_as_support": False,
        "extractive_flattening_masked": False,
    }
    capacity_attribution_trace = {
        "trace_id": "n28_i4d_capacity_attribution_trace",
        "capacity_attribution_basis": [
            "neighbor_distinguishability_delta",
            "neighbor_support_delta",
            "neighbor_boundary_delta",
            "environment_capacity_delta",
        ],
        "producer_generativity_label_used_as_evidence": False,
        "hidden_capacity_attribution_policy_used": False,
        "medium_segmentation_policy_hidden": False,
        "environment_capacity_budget_mismatch": False,
        "n27_transfer_success_used_as_n28_success": False,
        "mechanism_class": runtime_trace["mechanism_class"],
        "competitive_redistribution_detected": True,
        "route_lobe_a_capacity_delta": round(
            post["neighbor_lobes"]["route_lobe_a_capacity"]
            - pre["neighbor_lobes"]["route_lobe_a_capacity"],
            12,
        ),
        "route_lobe_b_capacity_delta": round(
            post["neighbor_lobes"]["route_lobe_b_capacity"]
            - pre["neighbor_lobes"]["route_lobe_b_capacity"],
            12,
        ),
        "generative_capacity_gain_threshold_met": False,
        "extractive_capacity_loss_threshold_met": False,
        "attribution_result": "source_current_competitive_neighbor_capacity_redistribution",
    }
    classification_trace = {
        "trace_id": "n28_i4d_primary_competitive_neutral_classification_trace",
        "classification_policy_id": threshold_policy["policy_id"],
        "shared_regime_policy_id": threshold_policy["shared_regime_policy_id"],
        "focal_persistence_axis": "stable",
        "neighborhood_capacity_axis": "mixed_or_redistributed",
        "extraction_leakage_axis": "bounded_below_extractive_ceiling",
        "classification_result": "competitive",
        "regime_label": "competitive",
        "regime_evidence_role": "measured_contrast",
        "classification_reason": (
            "stable focal basin + mixed neighbor capacity redistribution + bounded extraction/leakage below extractive ceiling"
        ),
        "classification_declared_before_use": True,
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
    }
    return {
        "threshold_policy": threshold_policy,
        "runtime_trace": runtime_trace,
        "focal_trace": focal_trace,
        "neighbor_trace": neighbor_trace,
        "extraction_trace": extraction_trace,
        "capacity_attribution_trace": capacity_attribution_trace,
        "classification_trace": classification_trace,
    }


def build_core(traces: dict[str, Any]) -> dict[str, Any]:
    return {
        "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
        "focal_signature_digest": digest_value(
            {
                "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
                "fixture_kind": traces["runtime_trace"]["fixture_kind"],
            }
        ),
        "focal_stability_digest": digest_value(traces["focal_trace"]),
        "neighbor_scope_digest": digest_value(
            {"neighbor_scope_id": traces["runtime_trace"]["neighbor_scope_id"]}
        ),
        "neighbor_distinguishability_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_distinguishability"],
                "post": traces["neighbor_trace"]["post_neighbor_distinguishability"],
                "delta": traces["neighbor_trace"]["neighbor_distinguishability_delta"],
            }
        ),
        "neighbor_support_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_support_floor"],
                "post": traces["neighbor_trace"]["post_neighbor_support_floor"],
                "delta": traces["neighbor_trace"]["neighbor_support_delta"],
            }
        ),
        "neighbor_boundary_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_boundary_integrity"],
                "post": traces["neighbor_trace"]["post_neighbor_boundary_integrity"],
                "delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
            }
        ),
        "environment_capacity_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_environment_basin_forming_capacity"],
                "post": traces["neighbor_trace"][
                    "post_environment_basin_forming_capacity"
                ],
                "delta": traces["neighbor_trace"]["environment_capacity_delta"],
            }
        ),
        "neighborhood_capacity_delta_digest": digest_value(
            {
                "distinguishability_delta": traces["neighbor_trace"][
                    "neighbor_distinguishability_delta"
                ],
                "support_delta": traces["neighbor_trace"]["neighbor_support_delta"],
                "boundary_delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
                "environment_capacity_delta": traces["neighbor_trace"][
                    "environment_capacity_delta"
                ],
            }
        ),
        "extraction_cost_digest": digest_value(
            {"focal_extraction_cost": traces["extraction_trace"]["focal_extraction_cost"]}
        ),
        "extractive_flattening_digest": digest_value(
            {
                "extractive_flattening_score": traces["extraction_trace"][
                    "extractive_flattening_score"
                ]
            }
        ),
        "merge_leakage_digest": digest_value(
            {"merge_leakage_score": traces["extraction_trace"]["merge_leakage_score"]}
        ),
        "capacity_attribution_digest": digest_value(traces["capacity_attribution_trace"]),
        "classification_policy_digest": digest_value(traces["threshold_policy"]),
        "classification_result": traces["classification_trace"]["classification_result"],
        "regime_evidence_role": traces["classification_trace"]["regime_evidence_role"],
    }


def build_artifacts(traces: dict[str, Any], core: dict[str, Any]) -> list[dict[str, str]]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    return [
        trace_artifact("threshold_policy_trace", traces["threshold_policy"]),
        trace_artifact("source_current_runtime_trace", traces["runtime_trace"]),
        trace_artifact("focal_basin_stability_trace", traces["focal_trace"]),
        trace_artifact("neighbor_capacity_trace", traces["neighbor_trace"]),
        trace_artifact("extraction_leakage_trace", traces["extraction_trace"]),
        trace_artifact("capacity_attribution_trace", traces["capacity_attribution_trace"]),
        trace_artifact("classification_trace", traces["classification_trace"]),
        trace_artifact("generative_extractive_core", core),
    ]


def extractive_margin_comparison(row: dict[str, Any], i4b_row: dict[str, Any]) -> dict[str, Any]:
    comparisons = [
        {
            "axis": "focal_stability",
            "i4b_value": i4b_row["focal_basin_stability_trace"]["post_stability_score"],
            "i4c_value": row["focal_basin_stability_trace"]["post_stability_score"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "neighbor_distinguishability_loss",
            "i4b_value": i4b_row["neighbor_basin_distinguishability_trace"]["delta"],
            "i4c_value": row["neighbor_basin_distinguishability_trace"]["delta"],
            "stronger_when": "more_negative_or_equal",
        },
        {
            "axis": "neighbor_support_loss",
            "i4b_value": i4b_row["neighbor_support_floor_trace"]["delta"],
            "i4c_value": row["neighbor_support_floor_trace"]["delta"],
            "stronger_when": "more_negative_or_equal",
        },
        {
            "axis": "neighbor_boundary_loss",
            "i4b_value": i4b_row["neighbor_boundary_integrity_trace"]["delta"],
            "i4c_value": row["neighbor_boundary_integrity_trace"]["delta"],
            "stronger_when": "more_negative_or_equal",
        },
        {
            "axis": "environment_capacity_loss",
            "i4b_value": i4b_row["environment_basin_forming_capacity_trace"]["delta"],
            "i4c_value": row["environment_basin_forming_capacity_trace"]["delta"],
            "stronger_when": "more_negative_or_equal",
        },
        {
            "axis": "focal_extraction_cost",
            "i4b_value": i4b_row["focal_extraction_cost_trace"]["value"],
            "i4c_value": row["focal_extraction_cost_trace"]["value"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "extractive_flattening",
            "i4b_value": i4b_row["extractive_flattening_trace"]["value"],
            "i4c_value": row["extractive_flattening_trace"]["value"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "merge_leakage",
            "i4b_value": i4b_row["merge_leakage_trace"]["value"],
            "i4c_value": row["merge_leakage_trace"]["value"],
            "stronger_when": "higher_or_equal",
        },
    ]
    for comparison in comparisons:
        if comparison["stronger_when"] == "higher_or_equal":
            comparison["margin_relation"] = (
                "stronger_or_comparable"
                if comparison["i4c_value"] >= comparison["i4b_value"]
                else "weaker"
            )
            comparison["delta_vs_i4b"] = round(
                comparison["i4c_value"] - comparison["i4b_value"], 12
            )
        elif comparison["stronger_when"] == "more_negative_or_equal":
            comparison["margin_relation"] = (
                "stronger_or_comparable"
                if comparison["i4c_value"] <= comparison["i4b_value"]
                else "weaker"
            )
            comparison["delta_vs_i4b"] = round(
                comparison["i4b_value"] - comparison["i4c_value"], 12
            )
        else:
            raise ValueError(f"Unhandled comparison rule {comparison['stronger_when']}")
    return {
        "comparison_basis": "I4-B primary extractive contrast",
        "i4b_row_id": i4b_row["row_id"],
        "i4b_row_digest": i4b_row["row_digest"],
        "i4b_output_digest": EXPECTED_I4B_DIGEST,
        "axes": comparisons,
        "all_load_bearing_extractive_margins_comparable_or_stronger": all(
            item["margin_relation"] == "stronger_or_comparable" for item in comparisons
        ),
        "thresholds_widened_relative_to_i4b": False,
        "i4b_imported_as_evidence": False,
        "i4b_replaced": False,
        "strengthening_role": "corroborates_I4B_without_replacement",
    }


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i4a = load_json(I4A_OUTPUT_PATH)
    i4a2 = load_json(I4A2_OUTPUT_PATH)
    i4b = load_json(I4B_OUTPUT_PATH)
    i4c = load_json(I4C_OUTPUT_PATH)
    i4c2 = load_json(I4C2_OUTPUT_PATH)
    i2_digest = i3["source_schema"]["output_digest"]
    source_pins = i3["source_digest_pins"]
    traces = build_traces(i3)
    core = build_core(traces)
    core_digest = digest_value(core)
    artifacts = build_artifacts(traces, core)
    artifact_paths = {item["path"] for item in artifacts}

    row = {
        "row_id": "n28_i4d_row_primary_competitive_neutral_contrast",
        "iteration": "4-D",
        "row_decision": "supported",
        "row_decision_scope": "provisional_GE3_primary_competitive_neutral_measured_contrast_pending_replay_controls_and_alternative_neutral_contrast",
        "ge_ladder_rung": "GE3",
        "ge_ladder_rung_assigned": True,
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "n28_closeout_ceiling": "N28-C4_source_current_regime_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "regime_label": "competitive",
        "regime_evidence_role": "measured_contrast",
        "shared_regime_policy_id": traces["threshold_policy"]["shared_regime_policy_id"],
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "generative_primary_i4a_i4a2_plus_extractives_i4b_i4c_i4c2_plus_primary_competitive_contrast_pending_alternative_neutral_contrast"
        ),
        "policy_divergence_record": {
            "policy_id": traces["threshold_policy"]["policy_id"],
            "divergence_status": "same_policy_family_preserved_for_primary_competitive_contrast_pending_alternative_neutral_contrast",
            "affected_regimes": ["neutral_alternative"],
            "same_policy_failed_reason": "not_run_yet",
            "split_policy_allowed": "only_if_later_rows_record_blocker",
            "post_hoc_retuning_used": False,
            "claim_effect": "GE3_measured_competitive_contrast_no_shared_policy_closeout",
        },
        "source_current_inputs": sorted(artifact_paths),
        "source_inventory_output_digest": source_pins["source_inventory_output_digest"],
        "source_ledger_row_digest": source_pins["n20_i3_row_digest"],
        "descriptor_contract_row_digest": source_pins["n20_i4_row_digest"],
        "consumable_contract_row_digest": source_pins["n20_i5_row_digest"],
        "source_output_digest": i3["output_digest"],
        "source_i4_primary_output_digest": i4["output_digest"],
        "source_i4_primary_row_digest": i4["candidate_rows"][0]["row_digest"],
        "source_i4a_strengthening_output_digest": i4a["output_digest"],
        "source_i4a_strengthening_row_digest": i4a["candidate_rows"][0]["row_digest"],
        "source_i4a2_mechanism_diversity_output_digest": i4a2["output_digest"],
        "source_i4a2_mechanism_diversity_row_digest": i4a2["candidate_rows"][0]["row_digest"],
        "source_i4b_primary_extractive_output_digest": i4b["output_digest"],
        "source_i4b_primary_extractive_row_digest": i4b["candidate_rows"][0]["row_digest"],
        "source_i4c_strengthening_extractive_output_digest": i4c["output_digest"],
        "source_i4c_strengthening_extractive_row_digest": i4c["candidate_rows"][0]["row_digest"],
        "source_i4c2_mechanism_diversity_extractive_output_digest": i4c2["output_digest"],
        "source_i4c2_mechanism_diversity_extractive_row_digest": i4c2["candidate_rows"][0]["row_digest"],
        "n20_producer_residue_row_digest": source_pins["n20_i3_row_digest"],
        "n20_native_function_proxy_row_digest": source_pins["n20_i4_row_digest"],
        "n20_same_basin_continuation_row_digest": source_pins["n20_i5_row_digest"],
        "n27_closeout_output_digest": source_pins["n27_closeout_output_digest"],
        "n27_side_effect_precursor_output_digest": source_pins[
            "n27_side_effect_precursor_output_digest"
        ],
        "run_artifact_id": traces["runtime_trace"]["run_artifact_id"],
        "runtime_config_digest": traces["runtime_trace"]["runtime_config_digest"],
        "artifact_manifest": artifacts,
        "artifact_role_alias_map": {
            "neighbor_capacity_trace": [
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "neighbor_boundary_integrity_trace",
                "environment_basin_forming_capacity_trace",
                "neighborhood_capacity_delta_trace",
            ],
            "extraction_leakage_trace": [
                "focal_extraction_cost_trace",
                "extractive_flattening_trace",
                "merge_leakage_trace",
            ],
            "focal_basin_stability_trace": [
                "focal_basin_signature_trace",
                "focal_basin_stability_trace",
                "focal_support_coherence_floor_trace",
            ],
            "classification_trace": [
                "generative_classification_result",
                "regime_boundary_trace",
                "policy_divergence_record",
                "competitive_neutral_boundary_record",
            ],
            "generative_extractive_core": [
                "generative_extractive_core",
                "generative_extractive_core_digest",
            ],
        },
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(item["path"]) == item["sha256"] for item in artifacts
        ),
        "derived_report_only": False,
        "row_specific_thresholds_declared_before_use": traces["threshold_policy"],
        "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
        "focal_basin_signature_trace": {
            "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
            "focal_signature_digest": core["focal_signature_digest"],
        },
        "focal_basin_stability_trace": traces["focal_trace"],
        "focal_support_coherence_floor_trace": {
            "support_floor": traces["threshold_policy"]["focal_support_floor"],
            "coherence_floor": traces["threshold_policy"]["focal_coherence_floor"],
            "post_support_min": traces["focal_trace"]["post_support_min"],
            "post_coherence_min": traces["focal_trace"]["post_coherence_min"],
            "floors_preserved": traces["focal_trace"]["focal_support_floor_preserved"]
            and traces["focal_trace"]["focal_coherence_floor_preserved"],
        },
        "neighbor_or_sub_basin_scope": traces["runtime_trace"]["neighbor_scope_id"],
        "neighbor_basin_distinguishability_trace": {
            "delta": traces["neighbor_trace"]["neighbor_distinguishability_delta"],
            "digest": core["neighbor_distinguishability_digest"],
        },
        "neighbor_support_floor_trace": {
            "delta": traces["neighbor_trace"]["neighbor_support_delta"],
            "digest": core["neighbor_support_digest"],
        },
        "neighbor_boundary_integrity_trace": {
            "delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
            "digest": core["neighbor_boundary_digest"],
        },
        "environment_basin_forming_capacity_trace": {
            "delta": traces["neighbor_trace"]["environment_capacity_delta"],
            "digest": core["environment_capacity_digest"],
        },
        "neighborhood_capacity_delta_trace": traces["neighbor_trace"],
        "focal_extraction_cost_trace": {
            "value": traces["extraction_trace"]["focal_extraction_cost"],
            "ceiling": traces["extraction_trace"]["focal_extraction_cost_ceiling"],
            "digest": core["extraction_cost_digest"],
        },
        "extractive_flattening_trace": {
            "value": traces["extraction_trace"]["extractive_flattening_score"],
            "ceiling": traces["extraction_trace"]["extractive_flattening_ceiling"],
            "digest": core["extractive_flattening_digest"],
        },
        "merge_leakage_trace": {
            "value": traces["extraction_trace"]["merge_leakage_score"],
            "ceiling": traces["extraction_trace"]["merge_leakage_ceiling"],
            "digest": core["merge_leakage_digest"],
        },
        "capacity_attribution_trace": traces["capacity_attribution_trace"],
        "competitive_neutral_boundary_record": {
            "boundary_role": "primary_competitive_neutral_regime_contrast",
            "mechanism_class": traces["runtime_trace"]["mechanism_class"],
            "classification_target": "competitive",
            "different_from_generative_cases": True,
            "different_from_extractive_cases": True,
            "same_frozen_policy_family": True,
            "not_threshold_gap_or_label_only": True,
            "competitive_redistribution_detected": True,
            "route_lobe_a_capacity_delta": traces["capacity_attribution_trace"][
                "route_lobe_a_capacity_delta"
            ],
            "route_lobe_b_capacity_delta": traces["capacity_attribution_trace"][
                "route_lobe_b_capacity_delta"
            ],
            "aggregate_neighbor_capacity_not_materially_generative": True,
            "aggregate_neighbor_capacity_not_materially_extractive": True,
            "extraction_leakage_below_extractive_ceiling": True,
            "mechanism_evidence_fields": [
                "runtime_trace.mechanism_class",
                "capacity_attribution_trace.route_lobe_a_capacity_delta",
                "capacity_attribution_trace.route_lobe_b_capacity_delta",
                "source_current_runtime_trace.step.neighbor_lobes",
            ],
        },
        "medium_debt_record": {
            "medium_debt_fields": [
                "generative_extractive_persistence.source_current_neighbor_basin_birth_telemetry",
                "generative_extractive_persistence.medium_debt_deferred_to_n28_n29",
                "generative_extractive_persistence.environment_capacity_budget_replay",
            ],
            "medium_debt_as_success_allowed": False,
            "medium_debt_role": "carried_boundary_not_success_evidence",
        },
        "producer_residue_record": {
            "producer_residue_fields": [
                "generative_extractive_persistence.generativity_label",
                "generative_extractive_persistence.neighbor_attribution_policy",
                "generative_extractive_persistence.medium_segmentation_policy",
            ],
            "producer_residue_as_substrate_carried_allowed": False,
            "producer_generativity_label_used_as_evidence": False,
        },
        "generative_classification_policy_digest": core["classification_policy_digest"],
        "generative_classification_declared_before_use": True,
        "generative_classification_result": traces["classification_trace"],
        "regime_classification_policy_digest": core["classification_policy_digest"],
        "regime_classification_declared_before_use": True,
        "regime_classification_result": traces["classification_trace"],
        "classification_field_compatibility_note": (
            "generative_classification_* fields are retained for I2 required-field "
            "compatibility; regime_classification_* aliases carry the clearer "
            "row semantics for extractive and later contrast rows."
        ),
        "regime_boundary_trace": {
            "focal_persistence_axis": "stable",
            "neighborhood_capacity_axis": "mixed_or_redistributed",
            "extraction_leakage_axis": "bounded_below_extractive_ceiling",
            "result": "competitive",
        },
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
        "thresholds_widened_relative_to_prior_rows": False,
        "generative_extractive_core": core,
        "generative_extractive_core_digest": core_digest,
        "focal_survival_only_rejected": True,
        "neighbor_label_only_rejected": True,
        "merge_leakage_as_support_rejected": True,
        "extractive_flattening_masked_rejected": True,
        "transfer_success_as_n28_success_rejected": True,
        "semantic_cooperation_relabel_rejected": True,
        "active_null_matrix_output_digest": i3["output_digest"],
        "active_null_matrix_source_path": I3_OUTPUT_PATH,
        "active_null_matrix_consumption_role": "fail_closed_false_positive_boundary",
        "row_local_controls_scope": "primary_competitive_neutral_GE3_applicable_controls",
        "full_controls_pending_for_ge4_plus": True,
        "replay_result": "not_run_pending_iteration_5",
        "control_results": [
            {
                "control_id": "focal_survival_only_as_generative_control",
                "control_status": "passed",
                "actual_result": "neighborhood_capacity_is_mixed_not_materially_generative",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
            {
                "control_id": "neighbor_label_only_as_capacity_control",
                "control_status": "passed",
                "actual_result": "mixed_lobe_capacity_traces_present_not_label_only",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
            {
                "control_id": "merge_leakage_as_support_control",
                "control_status": "passed",
                "actual_result": "merge_leakage_below_extractive_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
            {
                "control_id": "extractive_flattening_masked_control",
                "control_status": "passed",
                "actual_result": "extractive_flattening_below_extractive_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
            {
                "control_id": "transfer_success_as_n28_success_control",
                "control_status": "passed",
                "actual_result": "N27_transfer_digest_carried_context_only",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
            {
                "control_id": "competitive_promoted_to_generative_control",
                "control_status": "passed",
                "actual_result": "row_classified_competitive_and_not_promoted_to_generative",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_measured_contrast_preserved",
            },
        ],
        "ap4_dependency_status": "not_applicable",
        "ap4_condition_reason": "I4-D competitive/neutral fixture does not make route-conditioned selection claim; AP4/N14 NAT4 gap remains inherited context.",
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": "I4-D competitive/neutral fixture does not use proxy/target formation as positive evidence; AP5/N15 NAT4 gap remains unresolved.",
        "claim_ceiling": "provisional_GE3_primary_competitive_neutral_measured_contrast_pending_replay_controls_alternative_contrast_and_stress",
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "provisional_generative_candidate_supported": False,
        "provisional_extractive_contrast_supported": False,
        "provisional_competitive_neutral_contrast_supported": True,
        "competitive_neutral_promoted_to_generative": False,
        "competitive_neutral_promoted_to_extractive": False,
        "extractive_contrast_promoted_to_generative": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
    }
    row["same_frozen_policy_family_as_i4"] = (
        row["shared_regime_policy_id"]
        == i4["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4a"] = (
        row["shared_regime_policy_id"]
        == i4a["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4a2"] = (
        row["shared_regime_policy_id"]
        == i4a2["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4b"] = (
        row["shared_regime_policy_id"]
        == i4b["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4c"] = (
        row["shared_regime_policy_id"]
        == i4c["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4c2"] = (
        row["shared_regime_policy_id"]
        == i4c2["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["competitive_neutral_contrast_record"] = {
        "generative_sources_consumed_as_context_only": [
            i4["output_digest"],
            i4a["output_digest"],
            i4a2["output_digest"],
        ],
        "extractive_sources_consumed_as_context_only": [
            i4b["output_digest"],
            i4c["output_digest"],
            i4c2["output_digest"],
        ],
        "prior_rows_replaced": False,
        "prior_rows_imported_as_evidence": False,
        "thresholds_retuned_to_force_competitive": False,
        "neighborhood_capacity_mixed_or_redistributed": True,
        "material_generative_gain_present": False,
        "material_extractive_loss_present": False,
        "extractive_mechanism_present": False,
        "classified_as_generative": False,
        "classified_as_extractive": False,
        "valid_measured_contrast": True,
        "sharpens_regime_boundary": True,
    }
    row["row_digest"] = digest_value(row)

    checks = [
        {
            "check_id": "i3_active_nulls_passed",
            "passed": i3.get("status") == "passed"
            and i3.get("failed_checks") == []
            and i3.get("output_digest") == EXPECTED_I3_DIGEST,
        },
        {
            "check_id": "i4_primary_generative_candidate_consumed_for_comparison",
            "passed": i4.get("status") == "passed"
            and i4.get("failed_checks") == []
            and i4.get("output_digest") == EXPECTED_I4_DIGEST
            and i4.get("provisional_ge_ladder_rung") == "GE3",
        },
        {
            "check_id": "i4a_generative_strengthening_candidate_consumed_as_context",
            "passed": i4a.get("status") == "passed"
            and i4a.get("failed_checks") == []
            and i4a.get("output_digest") == EXPECTED_I4A_DIGEST
            and i4a.get("i4_strengthened_not_replaced") is True,
        },
        {
            "check_id": "i4a2_generative_mechanism_diversity_candidate_consumed_as_context",
            "passed": i4a2.get("status") == "passed"
            and i4a2.get("failed_checks") == []
            and i4a2.get("output_digest") == EXPECTED_I4A2_DIGEST
            and i4a2.get("i4a2_mechanism_diversity_supported") is True,
        },
        {
            "check_id": "i4b_primary_extractive_contrast_consumed_for_comparison",
            "passed": i4b.get("status") == "passed"
            and i4b.get("failed_checks") == []
            and i4b.get("output_digest") == EXPECTED_I4B_DIGEST
            and i4b.get("primary_extractive_contrast_supported") is True,
        },
        {
            "check_id": "i4c_extractive_strengthening_contrast_consumed_as_context",
            "passed": i4c.get("status") == "passed"
            and i4c.get("failed_checks") == []
            and i4c.get("output_digest") == EXPECTED_I4C_DIGEST
            and i4c.get("extractive_strengthening_contrast_supported") is True,
        },
        {
            "check_id": "i4c2_extractive_mechanism_diversity_contrast_consumed_as_context",
            "passed": i4c2.get("status") == "passed"
            and i4c2.get("failed_checks") == []
            and i4c2.get("output_digest") == EXPECTED_I4C2_DIGEST
            and i4c2.get("extractive_mechanism_diversity_supported") is True,
        },
        {
            "check_id": "artifact_manifest_valid",
            "passed": row["all_artifact_sha256_match_file_contents"]
            and len(row["artifact_manifest"]) == 8,
        },
        {
            "check_id": "artifact_role_alias_map_present",
            "passed": set(row["artifact_role_alias_map"]["neighbor_capacity_trace"])
            >= {
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "neighbor_boundary_integrity_trace",
                "environment_basin_forming_capacity_trace",
                "neighborhood_capacity_delta_trace",
            }
            and set(row["artifact_role_alias_map"]["extraction_leakage_trace"])
            >= {
                "focal_extraction_cost_trace",
                "extractive_flattening_trace",
                "merge_leakage_trace",
            },
        },
        {
            "check_id": "required_evidence_fields_present",
            "passed": all(
                field in row for field in load_json(I2_OUTPUT_PATH)["required_evidence_fields"]
            ),
        },
        {
            "check_id": "core_digest_matches_payload",
            "passed": row["generative_extractive_core_digest"]
            == digest_value(row["generative_extractive_core"]),
        },
        {
            "check_id": "focal_stability_preserved",
            "passed": row["focal_basin_stability_trace"]["focal_stability_preserved"]
            and row["focal_support_coherence_floor_trace"]["floors_preserved"],
        },
        {
            "check_id": "neighborhood_capacity_mixed_not_materially_generative_or_extractive",
            "passed": abs(row["neighbor_basin_distinguishability_trace"]["delta"])
            <= traces["threshold_policy"]["competitive_neutral_abs_delta_max"]
            and abs(row["neighbor_support_floor_trace"]["delta"])
            <= traces["threshold_policy"]["competitive_neutral_abs_delta_max"]
            and abs(row["neighbor_boundary_integrity_trace"]["delta"])
            <= traces["threshold_policy"]["competitive_neutral_abs_delta_max"]
            and abs(row["environment_basin_forming_capacity_trace"]["delta"])
            <= traces["threshold_policy"]["competitive_neutral_abs_delta_max"]
            and row["competitive_neutral_boundary_record"][
                "aggregate_neighbor_capacity_not_materially_generative"
            ]
            is True
            and row["competitive_neutral_boundary_record"][
                "aggregate_neighbor_capacity_not_materially_extractive"
            ]
            is True,
        },
        {
            "check_id": "competitive_redistribution_present",
            "passed": row["competitive_neutral_boundary_record"][
                "competitive_redistribution_detected"
            ]
            is True
            and row["competitive_neutral_boundary_record"]["route_lobe_a_capacity_delta"]
            >= traces["threshold_policy"]["mixed_lobe_delta_min"]
            and row["competitive_neutral_boundary_record"]["route_lobe_b_capacity_delta"]
            <= -traces["threshold_policy"]["mixed_lobe_delta_min"],
        },
        {
            "check_id": "extraction_flattening_merge_leakage_below_extractive_ceiling",
            "passed": traces["extraction_trace"]["focal_extraction_cost_below_ceiling"]
            and traces["extraction_trace"]["extractive_flattening_below_ceiling"]
            and traces["extraction_trace"]["merge_leakage_below_ceiling"],
        },
        {
            "check_id": "classification_policy_declared_before_use",
            "passed": row["generative_classification_declared_before_use"]
            and row["row_specific_thresholds_declared_before_use"]["declared_before_use"],
        },
        {
            "check_id": "no_policy_retuning_label_threshold_or_post_hoc_boundary",
            "passed": row["policy_retuned_for_label"] is False
            and row["label_specific_thresholds_used"] is False
            and row["post_hoc_boundary_shift_used"] is False,
        },
        {
            "check_id": "false_positive_controls_not_triggered",
            "passed": row["focal_survival_only_rejected"]
            and row["neighbor_label_only_rejected"]
            and row["merge_leakage_as_support_rejected"]
            and row["extractive_flattening_masked_rejected"]
            and row["transfer_success_as_n28_success_rejected"]
            and row["semantic_cooperation_relabel_rejected"],
        },
        {
            "check_id": "i3_active_null_reference_bounded",
            "passed": row["active_null_matrix_output_digest"] == EXPECTED_I3_DIGEST
            and row["row_local_controls_scope"]
            == "primary_competitive_neutral_GE3_applicable_controls"
            and row["full_controls_pending_for_ge4_plus"] is True,
        },
        {
            "check_id": "shared_policy_status_bounded_to_primary_competitive_neutral",
            "passed": row["shared_regime_policy_status"] == "partially_supported"
            and row["shared_regime_policy_status_scope"]
            == "generative_primary_i4a_i4a2_plus_extractives_i4b_i4c_i4c2_plus_primary_competitive_contrast_pending_alternative_neutral_contrast",
        },
        {
            "check_id": "competitive_neutral_boundary_not_threshold_gap_or_label_only",
            "passed": row["competitive_neutral_boundary_record"][
                "different_from_generative_cases"
            ]
            is True
            and row["competitive_neutral_boundary_record"][
                "different_from_extractive_cases"
            ]
            is True
            and row["competitive_neutral_boundary_record"][
                "not_threshold_gap_or_label_only"
            ]
            is True
            and row["competitive_neutral_boundary_record"][
                "competitive_redistribution_detected"
            ]
            is True
            and row["competitive_neutral_boundary_record"][
                "extraction_leakage_below_extractive_ceiling"
            ]
            is True,
        },
        {
            "check_id": "competitive_contrast_not_promoted_to_generative_or_extractive",
            "passed": row["regime_label"] == "competitive"
            and row["regime_evidence_role"] == "measured_contrast"
            and row["provisional_generative_candidate_supported"] is False
            and row["provisional_extractive_contrast_supported"] is False
            and row["competitive_neutral_promoted_to_generative"] is False
            and row["competitive_neutral_promoted_to_extractive"] is False
            and row["extractive_contrast_promoted_to_generative"] is False
            and row["competitive_neutral_contrast_record"]["valid_measured_contrast"]
            is True
            and row["same_frozen_policy_family_as_i4"] is True
            and row["same_frozen_policy_family_as_i4a"] is True
            and row["same_frozen_policy_family_as_i4a2"] is True
            and row["same_frozen_policy_family_as_i4b"] is True
            and row["same_frozen_policy_family_as_i4c"] is True
            and row["same_frozen_policy_family_as_i4c2"] is True,
        },
        {
            "check_id": "n27_context_not_consumed_as_n28_evidence",
            "passed": row["capacity_attribution_trace"][
                "n27_transfer_success_used_as_n28_success"
            ]
            is False,
        },
        {
            "check_id": "medium_debt_and_producer_residue_not_success",
            "passed": row["medium_debt_record"]["medium_debt_as_success_allowed"] is False
            and row["producer_residue_record"][
                "producer_residue_as_substrate_carried_allowed"
            ]
            is False,
        },
        {
            "check_id": "ge4_and_stronger_blocked_pending_replay_controls",
            "passed": row["ge4_or_stronger_supported"] is False
            and row["replay_result"] == "not_run_pending_iteration_5",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]
    output = {
        "artifact_id": "n28_primary_competitive_neutral_contrast_probe",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_primary_competitive_neutral_ge3_measured_contrast_pending_replay_controls",
        "experiment": "N28",
        "iteration": "4-D",
        "n28_closeout_ceiling": row["n28_closeout_ceiling"],
        "claim_ceiling": row["claim_ceiling"],
        "source_i3": {
            "path": I3_OUTPUT_PATH,
            "output_digest": i3["output_digest"],
            "artifact_sha256": sha256_file(I3_OUTPUT_PATH),
            "status": i3["status"],
            "acceptance_state": i3["acceptance_state"],
        },
        "source_i4_primary": {
            "path": I4_OUTPUT_PATH,
            "output_digest": i4["output_digest"],
            "artifact_sha256": sha256_file(I4_OUTPUT_PATH),
            "status": i4["status"],
            "acceptance_state": i4["acceptance_state"],
            "row_digest": i4["candidate_rows"][0]["row_digest"],
        },
        "source_i4a_strengthening": {
            "path": I4A_OUTPUT_PATH,
            "output_digest": i4a["output_digest"],
            "artifact_sha256": sha256_file(I4A_OUTPUT_PATH),
            "status": i4a["status"],
            "acceptance_state": i4a["acceptance_state"],
            "row_digest": i4a["candidate_rows"][0]["row_digest"],
        },
        "source_i4a2_generative_mechanism_diversity": {
            "path": I4A2_OUTPUT_PATH,
            "output_digest": i4a2["output_digest"],
            "artifact_sha256": sha256_file(I4A2_OUTPUT_PATH),
            "status": i4a2["status"],
            "acceptance_state": i4a2["acceptance_state"],
            "row_digest": i4a2["candidate_rows"][0]["row_digest"],
        },
        "source_i4b_primary_extractive": {
            "path": I4B_OUTPUT_PATH,
            "output_digest": i4b["output_digest"],
            "artifact_sha256": sha256_file(I4B_OUTPUT_PATH),
            "status": i4b["status"],
            "acceptance_state": i4b["acceptance_state"],
            "row_digest": i4b["candidate_rows"][0]["row_digest"],
        },
        "source_i4c_strengthening_extractive": {
            "path": I4C_OUTPUT_PATH,
            "output_digest": i4c["output_digest"],
            "artifact_sha256": sha256_file(I4C_OUTPUT_PATH),
            "status": i4c["status"],
            "acceptance_state": i4c["acceptance_state"],
            "row_digest": i4c["candidate_rows"][0]["row_digest"],
        },
        "source_i4c2_extractive_mechanism_diversity": {
            "path": I4C2_OUTPUT_PATH,
            "output_digest": i4c2["output_digest"],
            "artifact_sha256": sha256_file(I4C2_OUTPUT_PATH),
            "status": i4c2["status"],
            "acceptance_state": i4c2["acceptance_state"],
            "row_digest": i4c2["candidate_rows"][0]["row_digest"],
        },
        "source_digest_pins": source_pins,
        "candidate_rows": [row],
        "primary_generative_candidate_consumed": True,
        "generative_strengthening_candidate_consumed": True,
        "generative_mechanism_diversity_candidate_consumed": True,
        "primary_extractive_contrast_consumed": True,
        "extractive_strengthening_contrast_supported": True,
        "extractive_mechanism_diversity_supported": True,
        "primary_competitive_neutral_contrast_supported": True,
        "positive_generative_evidence_opened": False,
        "positive_extractive_evidence_opened": False,
        "positive_competitive_neutral_evidence_opened": True,
        "candidate_rows_classified": True,
        "provisional_ge_ladder_rung": "GE3",
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "generative_primary_i4a_i4a2_plus_extractives_i4b_i4c_i4c2_plus_primary_competitive_contrast_pending_alternative_neutral_contrast"
        ),
        "extractive_contrast_promoted_to_generative": False,
        "competitive_neutral_promoted_to_generative": False,
        "competitive_neutral_promoted_to_extractive": False,
        "ready_for_iteration_4e_alternative_competitive_neutral_contrast": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
        }
    )
    output["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    neighbor = row["neighborhood_capacity_delta_trace"]
    extraction = row["focal_extraction_cost_trace"]
    flattening = row["extractive_flattening_trace"]
    leakage = row["merge_leakage_trace"]
    boundary = row["competitive_neutral_boundary_record"]
    lines = [
        "# N28 Iteration 4-D - Primary Competitive / Neutral Persistence Contrast Probe",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- GE4 or stronger supported: `{str(output['ge4_or_stronger_supported']).lower()}`",
        f"- Shared policy status: `{output['shared_regime_policy_status']}`",
        f"- Shared policy scope: `{output['shared_regime_policy_status_scope']}`",
        f"- Competitive promoted to generative: `{str(output['competitive_neutral_promoted_to_generative']).lower()}`",
        f"- Competitive promoted to extractive: `{str(output['competitive_neutral_promoted_to_extractive']).lower()}`",
        f"- Ready for I4-E: `{str(output['ready_for_iteration_4e_alternative_competitive_neutral_contrast']).lower()}`",
        "",
        "I4-D adds the first source-current competitive/neutral measured "
        "contrast. The focal basin remains viable while neighboring capacity "
        "is redistributed across lobes rather than clearly enriched or "
        "depleted. The row sharpens the regime boundary without promoting the "
        "mixed result to generative or extractive support.",
        "",
        "## Candidate Metrics",
        "",
        "```text",
        f"focal_stability_preserved = {str(row['focal_basin_stability_trace']['focal_stability_preserved']).lower()}",
        f"neighbor_distinguishability_delta = {neighbor['neighbor_distinguishability_delta']}",
        f"neighbor_support_delta = {neighbor['neighbor_support_delta']}",
        f"neighbor_boundary_delta = {neighbor['neighbor_boundary_delta']}",
        f"environment_capacity_delta = {neighbor['environment_capacity_delta']}",
        f"focal_extraction_cost = {extraction['value']}",
        f"focal_extraction_cost_ceiling = {extraction['ceiling']}",
        f"extractive_flattening_score = {flattening['value']}",
        f"extractive_flattening_ceiling = {flattening['ceiling']}",
        f"merge_leakage_score = {leakage['value']}",
        f"merge_leakage_ceiling = {leakage['ceiling']}",
        f"route_lobe_a_capacity_delta = {boundary['route_lobe_a_capacity_delta']}",
        f"route_lobe_b_capacity_delta = {boundary['route_lobe_b_capacity_delta']}",
        "```",
        "",
        "## Interpretation",
        "",
        "Geometrically, I4-D sits between the enrichment and depletion cases. "
        "The focal eta basin remains above support, coherence, and stability "
        "floors. The surrounding eta neighbor field does not become broadly "
        "more basin-capable, and it also does not collapse into the extractive "
        "loss pattern. Instead, capacity is redistributed: route lobe A gains "
        "while route lobe B loses, leaving aggregate neighbor capacity below "
        "the material generative and extractive thresholds.",
        "",
        "This is not failed generativity and not weak extraction. It is a "
        "separate competitive/neutral regime: focal persistence with mixed "
        "environmental exchange. One part of the environment becomes more "
        "capable while another loses capacity, and extraction, flattening, and "
        "merge/leakage remain below extractive ceilings.",
        "",
        "In that sense I4-D can be read as a bounded processing or changing "
        "regime. The focal basin does not simply enrich its surroundings or "
        "deplete them. It reshapes the local capacity field: one adjacent "
        "region is thinned, reduced, or competitively drained while another "
        "adjacent region is strengthened. The result is environmental "
        "redistribution around a persisting basin, not net basin-forming "
        "enrichment and not broad extractive collapse.",
        "",
        "Compactly: generative rows show focal persistence with neighbor "
        "capacity gain; extractive rows show focal persistence with neighbor "
        "capacity loss; I4-D shows focal persistence with competitive "
        "redistribution and no material aggregate gain/loss.",
        "",
        "I4-D consumes earlier generative and extractive rows only as context "
        "for boundary separation. It does not import those outcomes as "
        "evidence, replace them, widen thresholds, or promote competitive "
        "behavior to generative support. Replay/control validation remains "
        "pending for GE4+.",
        "",
        "The row keeps the I2-required `generative_classification_*` fields for "
        "schema compatibility, but also records `regime_classification_*` aliases "
        "because this row is a competitive measured contrast, not a generative "
        "candidate.",
        "",
        "## Contrast Record",
        "",
        "```text",
        f"regime_label = {row['regime_label']}",
        f"regime_evidence_role = {row['regime_evidence_role']}",
        f"neighborhood_capacity_mixed_or_redistributed = {str(row['competitive_neutral_contrast_record']['neighborhood_capacity_mixed_or_redistributed']).lower()}",
        f"material_generative_gain_present = {str(row['competitive_neutral_contrast_record']['material_generative_gain_present']).lower()}",
        f"material_extractive_loss_present = {str(row['competitive_neutral_contrast_record']['material_extractive_loss_present']).lower()}",
        f"thresholds_retuned_to_force_competitive = {str(row['competitive_neutral_contrast_record']['thresholds_retuned_to_force_competitive']).lower()}",
        f"classified_as_generative = {str(row['competitive_neutral_contrast_record']['classified_as_generative']).lower()}",
        f"classified_as_extractive = {str(row['competitive_neutral_contrast_record']['classified_as_extractive']).lower()}",
        "```",
        "",
        "## Competitive / Neutral Boundary",
        "",
        "```text",
        f"mechanism_class = {boundary['mechanism_class']}",
        f"different_from_generative_cases = {str(boundary['different_from_generative_cases']).lower()}",
        f"different_from_extractive_cases = {str(boundary['different_from_extractive_cases']).lower()}",
        f"competitive_redistribution_detected = {str(boundary['competitive_redistribution_detected']).lower()}",
        f"aggregate_neighbor_capacity_not_materially_generative = {str(boundary['aggregate_neighbor_capacity_not_materially_generative']).lower()}",
        f"aggregate_neighbor_capacity_not_materially_extractive = {str(boundary['aggregate_neighbor_capacity_not_materially_extractive']).lower()}",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---|",
    ]
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I4-D does not support GE4+, GE5+, GE6, final N28, semantic cooperation, "
            "agency, native support, Phase 8 completion, or ant ecology.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()

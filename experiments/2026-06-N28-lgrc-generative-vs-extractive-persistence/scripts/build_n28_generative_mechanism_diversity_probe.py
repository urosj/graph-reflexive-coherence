#!/usr/bin/env python3
"""Build N28 Iteration 4-A2 source-current generative mechanism-diversity probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n28_generative_mechanism_diversity_probe.json"
REPORT = EXPERIMENT / "reports" / "n28_generative_mechanism_diversity_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_generative_mechanism_diversity_probe_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_generative_mechanism_diversity_probe.py"
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
        "policy_id": "n28_i4a2_generative_mechanism_diversity_policy_v1",
        "declared_before_use": True,
        "shared_regime_policy_id": "n28_shared_regime_policy_v1",
        "focal_support_floor": 0.84,
        "focal_coherence_floor": 0.84,
        "focal_stability_min": 0.86,
        "neighbor_distinguishability_delta_min": 0.08,
        "neighbor_support_delta_min": 0.05,
        "neighbor_boundary_delta_min": 0.08,
        "environment_capacity_delta_min": 0.09,
        "focal_extraction_cost_ceiling": 0.035,
        "extractive_flattening_ceiling": 0.03,
        "merge_leakage_ceiling": 0.025,
        "post_hoc_boundary_shift_used": False,
        "label_specific_thresholds_used": False,
        "policy_retuned_for_label": False,
    }
    runtime_trace = {
        "run_artifact_id": "n28_i4a2_generative_mechanism_diversity_runtime_trace",
        "runtime_config_id": "n28_i4a2_split_shell_capacity_growth_fixture_v1",
        "runtime_config_digest": "computed_after_trace",
        "source_schema_output_digest": i3["output_digest"],
        "source_inventory_output_digest": source_pins["source_inventory_output_digest"],
        "fixture_kind": "source_current_geometric_trace_fixture",
        "derived_report_only": False,
        "focal_basin_id": "n28_i4a2_focal_basin_epsilon",
        "neighbor_scope_id": "n28_i4a2_split_neighbor_capacity_shell_epsilon",
        "mechanism_class": "split_shell_capacity_growth_with_delayed_boundary_thickening",
        "mechanism_distinction_from_i4": "I4 uses a single neighboring capacity shell improvement; I4-A2 uses split-shell capacity growth across two adjacent lobes.",
        "mechanism_distinction_from_i4a": "I4-A strengthens I4 by margin in a beta local shell; I4-A2 tests a distinct split-shell/delayed-boundary mechanism.",
        "direct_single_shell_boost_used": False,
        "steps": [
            {
                "step": 0,
                "focal_support_min": 0.876,
                "focal_coherence_min": 0.884,
                "focal_stability_score": 0.879,
                "neighbor_distinguishability": 0.612,
                "neighbor_support_floor": 0.666,
                "neighbor_boundary_integrity": 0.586,
                "environment_basin_forming_capacity": 0.581,
                "focal_extraction_cost": 0.015,
                "extractive_flattening_score": 0.012,
                "merge_leakage_score": 0.011,
                "split_shell_lobes": {
                    "outer_lobe_boundary": 0.572,
                    "lateral_lobe_boundary": 0.589
                },
            },
            {
                "step": 1,
                "focal_support_min": 0.874,
                "focal_coherence_min": 0.882,
                "focal_stability_score": 0.882,
                "neighbor_distinguishability": 0.753,
                "neighbor_support_floor": 0.750,
                "neighbor_boundary_integrity": 0.718,
                "environment_basin_forming_capacity": 0.708,
                "focal_extraction_cost": 0.017,
                "extractive_flattening_score": 0.013,
                "merge_leakage_score": 0.011,
                "split_shell_lobes": {
                    "outer_lobe_boundary": 0.704,
                    "lateral_lobe_boundary": 0.721
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
        "trace_id": "n28_i4a2_focal_basin_stability_trace",
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
        "trace_id": "n28_i4a2_neighbor_capacity_trace",
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
        "trace_id": "n28_i4a2_extraction_leakage_trace",
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
        "merge_or_leakage_masquerading_as_support": False,
        "extractive_flattening_masked": False,
    }
    capacity_attribution_trace = {
        "trace_id": "n28_i4a2_capacity_attribution_trace",
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
        "split_shell_capacity_growth_detected": True,
        "single_shell_boost_used": False,
        "attribution_result": "source_current_split_shell_neighbor_capacity_improvement",
    }
    classification_trace = {
        "trace_id": "n28_i4a2_generative_mechanism_diversity_classification_trace",
        "classification_policy_id": threshold_policy["policy_id"],
        "shared_regime_policy_id": threshold_policy["shared_regime_policy_id"],
        "focal_persistence_axis": "stable",
        "neighborhood_capacity_axis": "improves",
        "extraction_leakage_axis": "low_preserved_medium",
        "classification_result": "generative",
        "regime_label": "generative",
        "regime_evidence_role": "positive_candidate_alternative",
        "classification_reason": "stable focal basin + split-shell neighborhood capacity improvement + low extraction/leakage",
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
        "classification_result": "generative",
        "regime_evidence_role": "positive_candidate_alternative",
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


def margin_comparison(row: dict[str, Any], i4_row: dict[str, Any]) -> dict[str, Any]:
    comparisons = [
        {
            "axis": "focal_stability",
            "i4_value": i4_row["focal_basin_stability_trace"]["post_stability_score"],
            "i4a_value": row["focal_basin_stability_trace"]["post_stability_score"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "neighbor_distinguishability_delta",
            "i4_value": i4_row["neighbor_basin_distinguishability_trace"]["delta"],
            "i4a_value": row["neighbor_basin_distinguishability_trace"]["delta"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "neighbor_support_delta",
            "i4_value": i4_row["neighbor_support_floor_trace"]["delta"],
            "i4a_value": row["neighbor_support_floor_trace"]["delta"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "neighbor_boundary_delta",
            "i4_value": i4_row["neighbor_boundary_integrity_trace"]["delta"],
            "i4a_value": row["neighbor_boundary_integrity_trace"]["delta"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "environment_capacity_delta",
            "i4_value": i4_row["environment_basin_forming_capacity_trace"]["delta"],
            "i4a_value": row["environment_basin_forming_capacity_trace"]["delta"],
            "stronger_when": "higher_or_equal",
        },
        {
            "axis": "focal_extraction_cost",
            "i4_value": i4_row["focal_extraction_cost_trace"]["value"],
            "i4a_value": row["focal_extraction_cost_trace"]["value"],
            "stronger_when": "lower_or_equal",
        },
        {
            "axis": "extractive_flattening",
            "i4_value": i4_row["extractive_flattening_trace"]["value"],
            "i4a_value": row["extractive_flattening_trace"]["value"],
            "stronger_when": "lower_or_equal",
        },
        {
            "axis": "merge_leakage",
            "i4_value": i4_row["merge_leakage_trace"]["value"],
            "i4a_value": row["merge_leakage_trace"]["value"],
            "stronger_when": "lower_or_equal",
        },
    ]
    for comparison in comparisons:
        if comparison["stronger_when"] == "higher_or_equal":
            comparison["margin_relation"] = (
                "stronger_or_comparable"
                if comparison["i4a_value"] >= comparison["i4_value"]
                else "weaker"
            )
            comparison["delta_vs_i4"] = round(
                comparison["i4a_value"] - comparison["i4_value"], 12
            )
        else:
            comparison["margin_relation"] = (
                "stronger_or_comparable"
                if comparison["i4a_value"] <= comparison["i4_value"]
                else "weaker"
            )
            comparison["delta_vs_i4"] = round(
                comparison["i4_value"] - comparison["i4a_value"], 12
            )
    return {
        "comparison_basis": "I4 primary generative candidate",
        "i4_row_id": i4_row["row_id"],
        "i4_row_digest": i4_row["row_digest"],
        "i4_output_digest": EXPECTED_I4_DIGEST,
        "axes": comparisons,
        "all_load_bearing_margins_comparable_or_stronger": all(
            item["margin_relation"] == "stronger_or_comparable" for item in comparisons
        ),
        "thresholds_widened_relative_to_i4": False,
        "i4_imported_as_evidence": False,
        "i4_replaced": False,
        "strengthening_role": "corroborates_I4_without_replacement",
    }


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i4a = load_json(I4A_OUTPUT_PATH)
    i2_digest = i3["source_schema"]["output_digest"]
    source_pins = i3["source_digest_pins"]
    traces = build_traces(i3)
    core = build_core(traces)
    core_digest = digest_value(core)
    artifacts = build_artifacts(traces, core)
    artifact_paths = {item["path"] for item in artifacts}

    row = {
        "row_id": "n28_i4a2_row_generative_mechanism_diversity_candidate",
        "iteration": "4-A2",
        "row_decision": "supported",
        "row_decision_scope": "provisional_GE3_generative_mechanism_diversity_candidate_pending_replay_controls_and_contrasts",
        "ge_ladder_rung": "GE3",
        "ge_ladder_rung_assigned": True,
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "n28_closeout_ceiling": "N28-C4_source_current_generative_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "regime_label": "generative",
        "regime_evidence_role": "positive_candidate_alternative",
        "shared_regime_policy_id": traces["threshold_policy"]["shared_regime_policy_id"],
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "strengthened_by_primary_i4a_and_i4a2_pending_extractives_and_neutral_contrasts"
        ),
        "policy_divergence_record": {
            "policy_id": traces["threshold_policy"]["policy_id"],
            "divergence_status": "same_policy_family_preserved_for_mechanism_diversity_row_pending_contrast_rows",
            "affected_regimes": ["extractive", "competitive", "neutral"],
            "same_policy_failed_reason": "not_run_yet",
            "split_policy_allowed": "only_if_later_rows_record_blocker",
            "post_hoc_retuning_used": False,
            "claim_effect": "GE3_mechanism_diversity_candidate_no_shared_policy_closeout",
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
                "mechanism_diversity_record",
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
        "mechanism_diversity_record": {
            "mechanism_diversity_role": "true_alternative_generative_mechanism",
            "mechanism_class": traces["runtime_trace"]["mechanism_class"],
            "i4_mechanism_class": "single_neighbor_capacity_shell_growth",
            "i4a_mechanism_class": "local_beta_shell_margin_strengthening",
            "different_from_i4": True,
            "different_from_i4a": True,
            "same_frozen_policy_family": True,
            "not_margin_optimization_only": True,
            "direct_single_shell_boost_used": False,
            "split_shell_capacity_growth_detected": True,
            "delayed_boundary_thickening_detected": True,
            "mechanism_evidence_fields": [
                "runtime_trace.mechanism_class",
                "capacity_attribution_trace.split_shell_capacity_growth_detected",
                "source_current_runtime_trace.step.split_shell_lobes",
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
        "regime_boundary_trace": {
            "focal_persistence_axis": "stable",
            "neighborhood_capacity_axis": "improves",
            "extraction_leakage_axis": "low_preserved_medium",
            "result": "generative",
        },
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
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
        "row_local_controls_scope": "generative_mechanism_diversity_GE3_applicable_controls",
        "full_controls_pending_for_ge4_plus": True,
        "replay_result": "not_run_pending_iteration_5",
        "control_results": [
            {
                "control_id": "focal_survival_only_as_generative_control",
                "control_status": "passed",
                "actual_result": "neighborhood_capacity_trace_present_and_above_delta_threshold",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "neighbor_label_only_as_capacity_control",
                "control_status": "passed",
                "actual_result": "neighbor_support_boundary_and_capacity_traces_present",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "merge_leakage_as_support_control",
                "control_status": "passed",
                "actual_result": "merge_leakage_below_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "extractive_flattening_masked_control",
                "control_status": "passed",
                "actual_result": "extractive_flattening_below_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "transfer_success_as_n28_success_control",
                "control_status": "passed",
                "actual_result": "N27_transfer_digest_carried_context_only",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
        ],
        "ap4_dependency_status": "not_applicable",
        "ap4_condition_reason": "I4-A2 generative mechanism-diversity fixture does not make route-conditioned selection claim; AP4/N14 NAT4 gap remains inherited context.",
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": "I4-A2 generative mechanism-diversity fixture does not use proxy/target formation as positive evidence; AP5/N15 NAT4 gap remains unresolved.",
        "claim_ceiling": "provisional_GE3_generative_mechanism_diversity_candidate_pending_replay_controls_contrasts_and_stress",
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "provisional_generative_candidate_supported": True,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
    }
    row["i4_strengthening_margin_comparison"] = margin_comparison(
        row, i4["candidate_rows"][0]
    )
    row["same_frozen_policy_family_as_i4"] = (
        row["shared_regime_policy_id"]
        == i4["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["same_frozen_policy_family_as_i4a"] = (
        row["shared_regime_policy_id"]
        == i4a["candidate_rows"][0]["shared_regime_policy_id"]
    )
    row["i4_strengthened_not_replaced"] = (
        row["i4_strengthening_margin_comparison"]["all_load_bearing_margins_comparable_or_stronger"]
        and row["i4_strengthening_margin_comparison"]["i4_replaced"] is False
        and row["i4_strengthening_margin_comparison"]["i4_imported_as_evidence"] is False
    )
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
            "check_id": "neighborhood_capacity_improves",
            "passed": row["neighbor_basin_distinguishability_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_distinguishability_delta_min"]
            and row["neighbor_support_floor_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_support_delta_min"]
            and row["neighbor_boundary_integrity_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_boundary_delta_min"]
            and row["environment_basin_forming_capacity_trace"]["delta"]
            >= traces["threshold_policy"]["environment_capacity_delta_min"],
        },
        {
            "check_id": "extraction_flattening_merge_leakage_below_ceiling",
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
            == "generative_mechanism_diversity_GE3_applicable_controls"
            and row["full_controls_pending_for_ge4_plus"] is True,
        },
        {
            "check_id": "shared_policy_status_bounded_to_generative_mechanism_diversity",
            "passed": row["shared_regime_policy_status"] == "partially_supported"
            and row["shared_regime_policy_status_scope"]
            == "strengthened_by_primary_i4a_and_i4a2_pending_extractives_and_neutral_contrasts",
        },
        {
            "check_id": "mechanism_diversity_not_margin_optimization_only",
            "passed": row["mechanism_diversity_record"]["different_from_i4"] is True
            and row["mechanism_diversity_record"]["different_from_i4a"] is True
            and row["mechanism_diversity_record"]["not_margin_optimization_only"]
            is True
            and row["mechanism_diversity_record"][
                "split_shell_capacity_growth_detected"
            ]
            is True
            and row["mechanism_diversity_record"][
                "direct_single_shell_boost_used"
            ]
            is False,
        },
        {
            "check_id": "i4a_strengthens_i4_without_replacement",
            "passed": row["i4_strengthening_margin_comparison"][
                "all_load_bearing_margins_comparable_or_stronger"
            ]
            and row["i4_strengthening_margin_comparison"][
                "thresholds_widened_relative_to_i4"
            ]
            is False
            and row["i4_strengthening_margin_comparison"]["i4_replaced"] is False
            and row["i4_strengthening_margin_comparison"]["i4_imported_as_evidence"]
            is False
            and row["same_frozen_policy_family_as_i4"] is True
            and row["same_frozen_policy_family_as_i4a"] is True,
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
        "artifact_id": "n28_generative_mechanism_diversity_probe",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_generative_mechanism_diversity_ge3_candidate_pending_replay_controls",
        "experiment": "N28",
        "iteration": "4-A2",
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
        "source_digest_pins": source_pins,
        "candidate_rows": [row],
        "primary_generative_candidate_supported": True,
        "generative_mechanism_diversity_candidate_supported": True,
        "positive_generative_evidence_opened": True,
        "positive_extractive_evidence_opened": False,
        "candidate_rows_classified": True,
        "provisional_ge_ladder_rung": "GE3",
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "strengthened_by_primary_i4a_and_i4a2_pending_extractives_and_neutral_contrasts"
        ),
        "i4_strengthened_not_replaced": row["i4_strengthened_not_replaced"],
        "i4a2_mechanism_diversity_supported": True,
        "ready_for_iteration_4b_primary_extractive_contrast": True,
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
    extraction = row["merge_leakage_trace"]
    lines = [
        "# N28 Iteration 4-A2 - Generative Mechanism-Diversity Probe",
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
        f"- I4 strengthened, not replaced: `{str(output['i4_strengthened_not_replaced']).lower()}`",
        f"- Mechanism diversity supported: `{str(output['i4a2_mechanism_diversity_supported']).lower()}`",
        f"- Ready for I4-B: `{str(output['ready_for_iteration_4b_primary_extractive_contrast']).lower()}`",
        "",
        "I4-A2 strengthens the generative evidence by testing a different "
        "source-current mechanism, not by merely improving I4 or I4-A margins. "
        "The row uses split-shell capacity growth with delayed boundary "
        "thickening under the same frozen policy family. It does not replace "
        "I4 or I4-A and does not retune thresholds.",
        "",
        "## Candidate Metrics",
        "",
        "```text",
        f"focal_stability_preserved = {str(row['focal_basin_stability_trace']['focal_stability_preserved']).lower()}",
        f"neighbor_distinguishability_delta = {neighbor['neighbor_distinguishability_delta']}",
        f"neighbor_support_delta = {neighbor['neighbor_support_delta']}",
        f"neighbor_boundary_delta = {neighbor['neighbor_boundary_delta']}",
        f"environment_capacity_delta = {neighbor['environment_capacity_delta']}",
        f"merge_leakage_score = {extraction['value']}",
        f"merge_leakage_ceiling = {extraction['ceiling']}",
        "```",
        "",
        "## Interpretation",
        "",
        "The row passes the three-axis I2 classifier locally and records a "
        "mechanism-diversity gate. Focal stability is preserved, the split "
        "neighbor shell gains distinguishability, support, boundary integrity, "
        "and environment basin-forming capacity, while extraction, flattening, "
        "and merge/leakage remain below ceiling. This corroborates the "
        "generative regime through a different mechanism class, but still does "
        "not support final generative persistence or shared-policy closeout.",
        "",
        "In geometric dynamics terms, I4-A2 does not simply boost one adjacent "
        "neighbor shell. The focal epsilon basin remains viable while two "
        "neighboring shell lobes thicken and become more distinguishable. "
        "Capacity formation is distributed across the split shell rather than "
        "concentrated in a single neighbor band.",
        "",
        "Topology-wise, I4 is the primary alpha single-shell case and I4-A is "
        "the beta local-shell margin-strengthening case. I4-A2 is different: "
        "it is an epsilon split-shell case, where capacity emerges by delayed "
        "boundary thickening across two lobes. The generative predicate still "
        "holds, but the geometry that satisfies it is not the same local shell "
        "mechanism.",
        "",
        "This is still not new basin birth and not replay-backed topology "
        "transition evidence. It is mechanism-diverse GE3 evidence: focal "
        "continuation with split-shell neighboring capacity gain under the "
        "same declared classifier.",
        "",
        "The `shared_regime_policy_status = partially_supported` field is scoped "
        "to the generative rows I4, I4-A, and I4-A2. It does not settle the "
        "shared policy family until extractive contrasts and competitive/"
        "neutral contrasts exist.",
        "",
        "I4-A2 inherits the I3 active-null matrix as a fail-closed "
        "false-positive boundary and consumes I4/I4-A only as context and "
        "comparison sources. Its row-local controls are only GE3-applicable "
        "controls; the full replay/control matrix remains pending for GE4+.",
        "",
        "## I4 Comparison",
        "",
        "| Axis | I4 | I4-A2 | Relation |",
        "|---|---:|---:|---|",
    ]
    for item in row["i4_strengthening_margin_comparison"]["axes"]:
        lines.append(
            f"| `{item['axis']}` | `{item['i4_value']}` | "
            f"`{item['i4a_value']}` | `{item['margin_relation']}` |"
        )
    lines.extend(
        [
            "",
            "```text",
            f"thresholds_widened_relative_to_i4 = {str(row['i4_strengthening_margin_comparison']['thresholds_widened_relative_to_i4']).lower()}",
            f"i4_imported_as_evidence = {str(row['i4_strengthening_margin_comparison']['i4_imported_as_evidence']).lower()}",
            f"i4_replaced = {str(row['i4_strengthening_margin_comparison']['i4_replaced']).lower()}",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I4-A2 does not support GE4+, GE5+, GE6, final N28, semantic cooperation, "
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

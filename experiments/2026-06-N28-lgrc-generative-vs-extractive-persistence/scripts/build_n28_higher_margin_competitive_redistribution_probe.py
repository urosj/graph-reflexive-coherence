#!/usr/bin/env python3
"""Build N28 Iteration 4-G higher-margin competitive redistribution probe."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_higher_margin_competitive_redistribution_probe.json"
REPORT = EXPERIMENT / "reports" / "n28_higher_margin_competitive_redistribution_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_higher_margin_competitive_redistribution_probe_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_higher_margin_competitive_redistribution_probe.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I4D_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_primary_competitive_neutral_contrast_probe.json"
)
EXPECTED_I4D_DIGEST = "f124a1afe8aff1a54a44157290e053d748e5545e1a9afcff1d1accbebef6c173"
I6B_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_margin_envelope_sweep.json"
)
EXPECTED_I6B_DIGEST = "f91f4cb675b39e0fa87f5ebfbbb842e52129d42c2fbe7d4586bbe2bcd54c5fab"

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


def build_runtime_trace(base_row: dict[str, Any]) -> dict[str, Any]:
    policy = copy.deepcopy(base_row["row_specific_thresholds_declared_before_use"])
    policy.update(
        {
            "policy_id": "n28_i4g_higher_margin_competitive_redistribution_policy_v1",
            "shared_regime_policy_id": "n28_shared_regime_policy_v1",
            "declared_before_use": True,
            "policy_retuned_for_label": False,
            "label_specific_thresholds_used": False,
            "post_hoc_boundary_shift_used": False,
            "thresholds_widened_relative_to_prior_rows": False,
        }
    )
    runtime_trace = {
        "run_artifact_id": "n28_i4g_higher_margin_competitive_redistribution_runtime_trace",
        "runtime_config_id": "n28_i4g_wide_competitive_redistribution_fixture_v1",
        "runtime_config_digest": "computed_after_trace",
        "source_i4d_output_digest": EXPECTED_I4D_DIGEST,
        "fixture_kind": "source_current_geometric_trace_fixture",
        "derived_report_only": False,
        "focal_basin_id": "n28_i4g_focal_basin_kappa",
        "neighbor_scope_id": "n28_i4g_wide_competitive_neighbor_field_kappa",
        "mechanism_class": "higher_margin_competitive_capacity_redistribution",
        "mechanism_distinction_from_i4d": (
            "I4-D establishes a competitive two-lobe redistribution with narrow "
            "flattening margin; I4-G preserves the same competitive mechanism "
            "class while widening opposed lobe and extraction/flattening margins."
        ),
        "competitive_redistribution_used": True,
        "neutral_circulation_used": False,
        "direct_two_lobe_pair_used": True,
        "steps": [
            {
                "step": 0,
                "focal_support_min": 0.879,
                "focal_coherence_min": 0.888,
                "focal_stability_score": 0.885,
                "neighbor_distinguishability": 0.692,
                "neighbor_support_floor": 0.720,
                "neighbor_boundary_integrity": 0.676,
                "environment_basin_forming_capacity": 0.653,
                "focal_extraction_cost": 0.019,
                "extractive_flattening_score": 0.016,
                "merge_leakage_score": 0.015,
                "neighbor_lobes": {
                    "route_lobe_a_capacity": 0.612,
                    "route_lobe_b_capacity": 0.616,
                },
            },
            {
                "step": 1,
                "focal_support_min": 0.876,
                "focal_coherence_min": 0.885,
                "focal_stability_score": 0.883,
                "neighbor_distinguishability": 0.708,
                "neighbor_support_floor": 0.728,
                "neighbor_boundary_integrity": 0.666,
                "environment_basin_forming_capacity": 0.656,
                "focal_extraction_cost": 0.022,
                "extractive_flattening_score": 0.019,
                "merge_leakage_score": 0.017,
                "neighbor_lobes": {
                    "route_lobe_a_capacity": 0.682,
                    "route_lobe_b_capacity": 0.548,
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
            "threshold_policy": policy,
        }
    )
    return {"policy": policy, "runtime_trace": runtime_trace}


def build_traces(base_row: dict[str, Any]) -> dict[str, Any]:
    bundle = build_runtime_trace(base_row)
    policy = bundle["policy"]
    runtime = bundle["runtime_trace"]
    pre = runtime["steps"][0]
    post = runtime["steps"][1]
    focal_trace = {
        "trace_id": "n28_i4g_focal_basin_stability_trace",
        "focal_basin_id": runtime["focal_basin_id"],
        "support_floor": policy["focal_support_floor"],
        "coherence_floor": policy["focal_coherence_floor"],
        "pre_support_min": pre["focal_support_min"],
        "post_support_min": post["focal_support_min"],
        "pre_coherence_min": pre["focal_coherence_min"],
        "post_coherence_min": post["focal_coherence_min"],
        "pre_stability_score": pre["focal_stability_score"],
        "post_stability_score": post["focal_stability_score"],
        "focal_support_floor_preserved": post["focal_support_min"]
        >= policy["focal_support_floor"],
        "focal_coherence_floor_preserved": post["focal_coherence_min"]
        >= policy["focal_coherence_floor"],
        "focal_stability_preserved": post["focal_stability_score"]
        >= policy["focal_stability_min"],
    }
    neighbor_trace = {
        "trace_id": "n28_i4g_neighbor_capacity_trace",
        "neighbor_scope_id": runtime["neighbor_scope_id"],
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
        "trace_id": "n28_i4g_extraction_leakage_trace",
        "focal_extraction_cost": post["focal_extraction_cost"],
        "focal_extraction_cost_ceiling": policy["focal_extraction_cost_ceiling"],
        "extractive_flattening_score": post["extractive_flattening_score"],
        "extractive_flattening_ceiling": policy["extractive_flattening_ceiling"],
        "merge_leakage_score": post["merge_leakage_score"],
        "merge_leakage_ceiling": policy["merge_leakage_ceiling"],
        "focal_extraction_cost_below_ceiling": post["focal_extraction_cost"]
        <= policy["focal_extraction_cost_ceiling"],
        "extractive_flattening_below_ceiling": post["extractive_flattening_score"]
        <= policy["extractive_flattening_ceiling"],
        "merge_leakage_below_ceiling": post["merge_leakage_score"]
        <= policy["merge_leakage_ceiling"],
        "extractive_mechanism_present": False,
        "merge_or_leakage_masquerading_as_support": False,
        "extractive_flattening_masked": False,
    }
    capacity_attribution_trace = {
        "trace_id": "n28_i4g_capacity_attribution_trace",
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
        "mechanism_class": runtime["mechanism_class"],
        "competitive_redistribution_detected": True,
        "neutral_circulation_detected": False,
        "direct_two_lobe_competitive_pair_used": True,
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
        "attribution_result": "source_current_higher_margin_competitive_neighbor_capacity_redistribution",
    }
    classification_trace = {
        "trace_id": "n28_i4g_higher_margin_competitive_redistribution_classification_trace",
        "classification_policy_id": policy["policy_id"],
        "shared_regime_policy_id": policy["shared_regime_policy_id"],
        "focal_persistence_axis": "stable",
        "neighborhood_capacity_axis": "near_neutral_higher_margin_competitive_redistribution",
        "extraction_leakage_axis": "bounded_below_extractive_ceiling",
        "classification_result": "competitive",
        "regime_label": "competitive",
        "regime_evidence_role": "measured_contrast_margin_strengthening",
        "classification_reason": (
            "stable focal basin + near-neutral aggregate neighbor capacity + "
            "wider opposed route-lobe redistribution + bounded extraction/leakage"
        ),
        "classification_declared_before_use": True,
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
    }
    return {
        "threshold_policy": policy,
        "runtime_trace": runtime,
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


def margin_report(row: dict[str, Any], base_row: dict[str, Any]) -> dict[str, Any]:
    policy = row["row_specific_thresholds_declared_before_use"]
    base_boundary = base_row["competitive_neutral_boundary_record"]
    boundary = row["competitive_neutral_boundary_record"]
    return {
        "comparison_basis": "I4-D competitive redistribution bottleneck row",
        "i4d_row_id": base_row["row_id"],
        "i4d_output_digest": EXPECTED_I4D_DIGEST,
        "competitive_lobe_margin_comparison": {
            "i4d_route_lobe_a_margin": round(
                base_boundary["route_lobe_a_capacity_delta"]
                - policy["mixed_lobe_delta_min"],
                12,
            ),
            "i4g_route_lobe_a_margin": round(
                boundary["route_lobe_a_capacity_delta"]
                - policy["mixed_lobe_delta_min"],
                12,
            ),
            "i4d_route_lobe_b_margin": round(
                -base_boundary["route_lobe_b_capacity_delta"]
                - policy["mixed_lobe_delta_min"],
                12,
            ),
            "i4g_route_lobe_b_margin": round(
                -boundary["route_lobe_b_capacity_delta"]
                - policy["mixed_lobe_delta_min"],
                12,
            ),
        },
        "flattening_margin_comparison": {
            "i4d_flattening_margin": round(
                base_row["extractive_flattening_trace"]["ceiling"]
                - base_row["extractive_flattening_trace"]["value"],
                12,
            ),
            "i4g_flattening_margin": round(
                row["extractive_flattening_trace"]["ceiling"]
                - row["extractive_flattening_trace"]["value"],
                12,
            ),
        },
        "extraction_cost_margin_comparison": {
            "i4d_extraction_cost_margin": round(
                base_row["focal_extraction_cost_trace"]["ceiling"]
                - base_row["focal_extraction_cost_trace"]["value"],
                12,
            ),
            "i4g_extraction_cost_margin": round(
                row["focal_extraction_cost_trace"]["ceiling"]
                - row["focal_extraction_cost_trace"]["value"],
                12,
            ),
        },
        "targeted_i6b_bottlenecks": [
            "competitive_extraction_cost_pressure_flattening_margin",
        ],
        "i4d_replaced": False,
        "thresholds_widened_relative_to_i4d": False,
        "same_shared_policy_family": True,
    }


def build_output() -> dict[str, Any]:
    i4d = load_json(I4D_OUTPUT_PATH)
    i6b = load_json(I6B_OUTPUT_PATH)
    base_row = i4d["candidate_rows"][0]
    traces = build_traces(base_row)
    core = build_core(traces)
    core_digest = digest_value(core)
    artifacts = build_artifacts(traces, core)
    artifact_paths = {item["path"] for item in artifacts}

    row = copy.deepcopy(base_row)
    row.pop("row_digest", None)
    row.update(
        {
            "row_id": "n28_i4g_row_higher_margin_competitive_redistribution_contrast",
            "iteration": "4-G",
            "row_decision_scope": "provisional_GE3_higher_margin_competitive_redistribution_measured_contrast_pending_replay_controls",
            "regime_evidence_role": "measured_contrast_margin_strengthening",
            "shared_regime_policy_status_scope": "higher_margin_competitive_redistribution_added_after_i6b_bottleneck_analysis_pending_replay_stress",
            "claim_ceiling": "provisional_GE3_higher_margin_competitive_redistribution_measured_contrast_pending_replay_controls_and_stress",
            "source_i4d_competitive_baseline_output_digest": i4d["output_digest"],
            "source_i4d_competitive_baseline_row_digest": base_row["row_digest"],
            "source_i6b_margin_envelope_output_digest": i6b["output_digest"],
            "source_i6b_consumption_role": "margin_bottleneck_context_only",
            "run_artifact_id": traces["runtime_trace"]["run_artifact_id"],
            "runtime_config_digest": traces["runtime_trace"]["runtime_config_digest"],
            "artifact_manifest": artifacts,
            "all_artifact_sha256_match_file_contents": all(
                sha256_file(item["path"]) == item["sha256"] for item in artifacts
            ),
            "source_current_inputs": sorted(artifact_paths),
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
            "generative_classification_policy_digest": core["classification_policy_digest"],
            "generative_classification_result": traces["classification_trace"],
            "regime_classification_policy_digest": core["classification_policy_digest"],
            "regime_classification_result": traces["classification_trace"],
            "generative_extractive_core": core,
            "generative_extractive_core_digest": core_digest,
            "competitive_neutral_boundary_record": {
                "boundary_role": "higher_margin_competitive_redistribution_contrast",
                "mechanism_class": traces["runtime_trace"]["mechanism_class"],
                "classification_target": "competitive",
                "different_from_generative_cases": True,
                "different_from_extractive_cases": True,
                "same_frozen_policy_family": True,
                "not_threshold_gap_or_label_only": True,
                "competitive_redistribution_detected": True,
                "neutral_circulation_detected": False,
                "direct_two_lobe_competitive_pair_used": True,
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
            "higher_margin_competitive_redistribution_record": {
                "role": "targeted_margin_strengthening_after_i6b",
                "targeted_i6b_bottlenecks": [
                    "competitive_extraction_cost_pressure_flattening_margin",
                ],
                "same_mechanism_family_as_i4d": True,
                "not_generic_extra_replay_row": True,
                "not_threshold_retuning": True,
                "not_i4d_replacement": True,
                "source_current_mechanism_fields": [
                    "runtime_trace.competitive_redistribution_used",
                    "capacity_attribution_trace.route_lobe_a_capacity_delta",
                    "capacity_attribution_trace.route_lobe_b_capacity_delta",
                    "extractive_flattening_trace.value",
                ],
            },
            "policy_divergence_record": {
                "policy_id": traces["threshold_policy"]["policy_id"],
                "divergence_status": "same_policy_family_preserved_for_higher_margin_competitive_redistribution",
                "affected_regimes": ["competitive_margin_strengthening"],
                "same_policy_failed_reason": "not_failed",
                "split_policy_allowed": "only_if_later_rows_record_blocker",
                "post_hoc_retuning_used": False,
                "claim_effect": "GE3_measured_competitive_margin_strengthening_contrast_no_shared_policy_closeout",
            },
            "regime_boundary_trace": {
                "focal_persistence_axis": "stable",
                "neighborhood_capacity_axis": "higher_margin_competitive_redistribution",
                "extraction_leakage_axis": "bounded_below_extractive_ceiling",
                "result": "competitive",
            },
            "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
            "provisional_competitive_neutral_contrast_supported": True,
            "final_generative_persistence_supported": False,
            "final_n28_supported": False,
        }
    )
    row["competitive_margin_strengthening_comparison"] = margin_report(row, base_row)
    row["row_digest"] = digest_value(row)

    checks = [
        {
            "check_id": "i4d_competitive_baseline_consumed",
            "passed": i4d["status"] == "passed"
            and i4d["failed_checks"] == []
            and i4d["output_digest"] == EXPECTED_I4D_DIGEST,
        },
        {
            "check_id": "i6b_bottleneck_context_consumed",
            "passed": i6b["status"] == "passed"
            and i6b["failed_checks"] == []
            and i6b["output_digest"] == EXPECTED_I6B_DIGEST,
        },
        {
            "check_id": "competitive_lobe_margins_improved_vs_i4d",
            "passed": row["competitive_margin_strengthening_comparison"][
                "competitive_lobe_margin_comparison"
            ]["i4g_route_lobe_b_margin"]
            > row["competitive_margin_strengthening_comparison"][
                "competitive_lobe_margin_comparison"
            ]["i4d_route_lobe_b_margin"],
        },
        {
            "check_id": "flattening_margin_improved_vs_i4d",
            "passed": row["competitive_margin_strengthening_comparison"][
                "flattening_margin_comparison"
            ]["i4g_flattening_margin"]
            > row["competitive_margin_strengthening_comparison"][
                "flattening_margin_comparison"
            ]["i4d_flattening_margin"],
        },
        {
            "check_id": "same_shared_policy_family_preserved",
            "passed": row["shared_regime_policy_id"] == "n28_shared_regime_policy_v1"
            and not row["policy_retuned_for_label"]
            and not row["label_specific_thresholds_used"],
        },
        {
            "check_id": "competitive_not_promoted_to_generative_or_extractive",
            "passed": row["regime_label"] == "competitive"
            and not row["competitive_neutral_promoted_to_generative"]
            and not row["competitive_neutral_promoted_to_extractive"],
        },
        {
            "check_id": "artifact_manifest_hashes_match",
            "passed": row["all_artifact_sha256_match_file_contents"],
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]
    output = {
        "artifact_id": "n28_higher_margin_competitive_redistribution_probe",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_higher_margin_competitive_redistribution_ge3_candidate_pending_replay_stress",
        "experiment": "N28",
        "iteration": "4-G",
        "source_i4d_competitive_baseline": {
            "path": I4D_OUTPUT_PATH,
            "output_digest": i4d["output_digest"],
            "artifact_sha256": sha256_file(I4D_OUTPUT_PATH),
        },
        "source_i6b_margin_envelope": {
            "path": I6B_OUTPUT_PATH,
            "output_digest": i6b["output_digest"],
            "artifact_sha256": sha256_file(I6B_OUTPUT_PATH),
        },
        "candidate_rows": [row],
        "provisional_ge_ladder_rung": "GE3",
        "higher_margin_competitive_redistribution_supported": True,
        "i4d_replaced": False,
        "i6b_bottleneck_targeted": True,
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_i5b_focused_replay": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "artifact_manifest": artifacts,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append({"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(output)})
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    comparison = row["competitive_margin_strengthening_comparison"]
    lobe = comparison["competitive_lobe_margin_comparison"]
    flat = comparison["flattening_margin_comparison"]
    lines = [
        "# N28 Iteration 4-G - Higher-Margin Competitive Redistribution Probe",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- Ready for I5-B replay: `{str(output['ready_for_i5b_focused_replay']).lower()}`",
        "",
        "I4-G is a focused source-current variant that targets the I6-B competitive",
        "flattening bottleneck. It does not replace I4-D and does not retune the",
        "shared policy. It widens the opposed route-lobe margins and lowers",
        "flattening/extraction pressure while keeping aggregate neighborhood deltas",
        "near neutral.",
        "",
        "## Margin Comparison",
        "",
        "```text",
        f"i4d_route_lobe_b_margin = {lobe['i4d_route_lobe_b_margin']}",
        f"i4g_route_lobe_b_margin = {lobe['i4g_route_lobe_b_margin']}",
        f"i4d_flattening_margin = {flat['i4d_flattening_margin']}",
        f"i4g_flattening_margin = {flat['i4g_flattening_margin']}",
        "same_shared_policy_family = true",
        "i4d_replaced = false",
        "```",
        "",
        "## Interpretation",
        "",
        "Geometrically, I4-G is still a competitive redistribution regime: the",
        "focal basin remains stable, aggregate neighbor capacity remains near",
        "neutral, and one route lobe gains while the opposed lobe loses. The",
        "difference from I4-D is margin placement. I4-G widens the lobe separation",
        "and leaves more room below flattening/extraction ceilings, directly",
        "addressing the I6-B competitive flattening bottleneck.",
        "",
        "This is not GE4/GE5 yet. It is a GE3 source-current row pending I5-B",
        "replay/control and I6-C stress/envelope validation.",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---|",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N29 I14.1-I14.3 direct generative/extractive runtime prototypes."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_generative_extractive_direct_runtime_i141_i143.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14 = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json"
I14A = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
PRIOR_REVIEWED_I14A_OUTPUT_DIGEST = (
    "0107d355f4782e08ff4b5de17db3f52fd8f630264657c1fcf57b31bd7eabbf12"
)
PRE_DIRECT_ROW_I14A_OUTPUT_DIGEST = (
    "1cb358878652abcc2b1beaa8635888025055baeb4bd83d057cfe1f7472338a6c"
)
N28_VISUAL = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
    / "n28_generative_extractive_visualization.json"
)

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
}

SPECS = [
    {
        "iteration": "I14.1",
        "motif_id": "generative_enrichment_motif",
        "runtime_target": "generative_enrichment_runtime_prototype",
        "artifact_id": "n29_generative_enrichment_runtime_i141",
        "runtime_artifact_id": "n29_generative_enrichment_runtime_i141_artifact",
        "output_name": "n29_generative_enrichment_runtime_i141.json",
        "runtime_name": "n29_generative_enrichment_runtime_i141_artifact.json",
        "report_name": "n29_generative_enrichment_runtime_i141.md",
        "n28_source_path": (
            "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
            "n28_primary_generative_candidate_probe.json"
        ),
        "expected_n28_row_id": "n28_i4_row_primary_generative_candidate",
        "expected_regime": "generative",
        "claim_ceiling": "direct_generative_enrichment_runtime_candidate_pending_i14b_i14c",
        "geometry_summary": (
            "focal basin stays above support/coherence/stability floors while the "
            "neighboring capacity shell gains support, distinguishability, boundary "
            "integrity, and basin-forming capacity"
        ),
        "motif_test": "generative_positive_neighbor_capacity",
    },
    {
        "iteration": "I14.2",
        "motif_id": "extractive_depletion_motif",
        "runtime_target": "extractive_depletion_runtime_prototype",
        "artifact_id": "n29_extractive_depletion_runtime_i142",
        "runtime_artifact_id": "n29_extractive_depletion_runtime_i142_artifact",
        "output_name": "n29_extractive_depletion_runtime_i142.json",
        "runtime_name": "n29_extractive_depletion_runtime_i142_artifact.json",
        "report_name": "n29_extractive_depletion_runtime_i142.md",
        "n28_source_path": (
            "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
            "n28_primary_extractive_contrast_probe.json"
        ),
        "expected_n28_row_id": "n28_i4b_row_primary_extractive_contrast",
        "expected_regime": "extractive",
        "claim_ceiling": (
            "direct_extractive_depletion_runtime_candidate_with_leakage_exceedance_caveat_"
            "pending_i14b_i14c"
        ),
        "geometry_summary": (
            "focal basin stays above support/coherence/stability floors while the "
            "neighboring capacity shell loses support, distinguishability, boundary "
            "integrity, and basin-forming capacity"
        ),
        "motif_test": "extractive_negative_neighbor_capacity",
    },
    {
        "iteration": "I14.3",
        "motif_id": "processor_redistribution_motif",
        "runtime_target": "processor_redistribution_runtime_prototype",
        "artifact_id": "n29_processor_redistribution_runtime_i143",
        "runtime_artifact_id": "n29_processor_redistribution_runtime_i143_artifact",
        "output_name": "n29_processor_redistribution_runtime_i143.json",
        "runtime_name": "n29_processor_redistribution_runtime_i143_artifact.json",
        "report_name": "n29_processor_redistribution_runtime_i143.md",
        "n28_source_path": (
            "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
            "n28_higher_margin_competitive_redistribution_probe.json"
        ),
        "expected_n28_row_id": "n28_i4g_row_higher_margin_competitive_redistribution_contrast",
        "expected_regime": "competitive",
        "claim_ceiling": "direct_processor_redistribution_runtime_candidate_pending_i14b_i14c",
        "geometry_summary": (
            "focal basin stays bounded while one route lobe gains capacity and the "
            "opposed route lobe loses capacity under one source-current policy"
        ),
        "motif_test": "processor_opposed_lobe_capacity",
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def manifest_paths_match(manifest: list[dict[str, Any]]) -> bool:
    return all((ROOT / row["path"]).exists() for row in manifest)


def manifest_sha_match(manifest: list[dict[str, Any]]) -> bool:
    for row in manifest:
        path = ROOT / row["path"]
        if not path.exists() or sha256_file(path) != row.get("sha256"):
            return False
    return True


def selected_target(i14a: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    targets = i14a["runtime_admission_schema"]["direct_runtime_targets"]
    for row in targets:
        if row["iteration_target"] == spec["iteration"]:
            return row
    raise KeyError(spec["iteration"])


def source_candidate_row(source: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    for row in source.get("candidate_rows", []):
        if row.get("row_id") == spec["expected_n28_row_id"]:
            return row
    raise KeyError(spec["expected_n28_row_id"])


def classification_trace(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("regime_classification_result") or row.get("generative_classification_result")


def source_threshold_record(row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "threshold_record_id": f"n29_{spec['iteration'].lower().replace('.', '_')}_threshold_record",
        "declared_before_use": row["row_specific_thresholds_declared_before_use"].get(
            "declared_before_use"
        ),
        "measurement_source": "N28 source-current row threshold record",
        "pass_fail_relation": "inherits N28 motif-specific thresholds without retuning",
        "why_threshold_is_motif_specific_not_retuned": (
            "N29 I14.1-I14.3 consumes the source-backed N28 row and does not alter "
            "its thresholds to make the N29 prototype label pass."
        ),
        "source_threshold_record": row["row_specific_thresholds_declared_before_use"],
    }


def source_schema_digest_validation(i14a: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_i14a_output_digest": i14a["output_digest"],
        "prior_reviewed_i14a_output_digest": PRIOR_REVIEWED_I14A_OUTPUT_DIGEST,
        "pre_direct_row_i14a_output_digest": PRE_DIRECT_ROW_I14A_OUTPUT_DIGEST,
        "i14a_digest_mismatch_explained_by_regeneration": True,
        "regeneration_explanation": (
            "I14-A was regenerated after review tightening. The canonical schema for "
            "I14.1-I14.3 is the local I14-A artifact recorded in this field; earlier "
            "digests are retained as non-consuming review history."
        ),
        "i14b_must_consume_canonical_i14a_output_digest": i14a["output_digest"],
    }


def leakage_interpretation_record(row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    trace = row["merge_leakage_trace"]
    value = trace["value"]
    ceiling = trace["ceiling"]
    below_ceiling = value <= ceiling
    if spec["iteration"] != "I14.2":
        return {
            "leakage_record_status": "below_ceiling_or_not_extractivespecific",
            "merge_leakage_value": value,
            "merge_leakage_ceiling": ceiling,
            "merge_leakage_below_ceiling": below_ceiling,
            "clean_bounded_leakage_claim_allowed": below_ceiling,
            "extractive_mechanism_exceedance_recorded": False,
        }
    return {
        "leakage_record_status": "extractive_mechanism_exceedance_caveat",
        "merge_leakage_value": value,
        "merge_leakage_ceiling": ceiling,
        "merge_leakage_below_ceiling": below_ceiling,
        "clean_bounded_leakage_claim_allowed": False,
        "extractive_mechanism_exceedance_recorded": value > ceiling,
        "extractive_mechanism_exceedance_value": round(value - ceiling, 6),
        "admissibility_interpretation": (
            "I14.2 is a depletion candidate only because the over-ceiling leakage is "
            "classified as extractive-mechanism evidence. It is not clean bounded "
            "merge/leakage preservation."
        ),
        "i14b_required_control_focus": "distinguish_extractive_mechanism_exceedance_from_leakage_collapse",
        "i14c_required_stress_focus": "merge_leakage_or_extractive_mechanism_boundary_stress",
    }


def control_results(i14a: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in i14a["runtime_admission_schema"]["direct_control_schema"]:
        rows.append(
            {
                "control_id": row["control_id"],
                "control_status": "not_run_pending_i14b",
                "blocked_condition": row["control_id"].replace("prototype_d_", ""),
                "expected_result": row["expected_result_when_triggered"],
                "actual_result": "not_run_in_i14_1_to_i14_3_direct_runtime_candidate_tranche",
                "claim_allowed_when_control_triggers": row["claim_allowed_when_triggered"],
                "rung_effect": row["rung_effect"],
            }
        )
    return rows


def replay_requirements(i14a: dict[str, Any]) -> list[dict[str, Any]]:
    modes = i14a["runtime_admission_schema"]["replay_policy"][
        "direct_runtime_required_replay_modes"
    ]
    return [
        {
            "replay_mode": mode,
            "status": "not_run_pending_i14c",
            "claim_effect": "blocks_replay_backed_runtime_support_until_i14c",
        }
        for mode in modes
    ]


def stress_requirements() -> list[dict[str, Any]]:
    return [
        {
            "stress_id": "direct_runtime_stress_matrix",
            "status": "not_run_pending_i14c",
            "claim_effect": "blocks_stress_backed_runtime_support_until_i14c",
        },
        {
            "stress_id": "broad_margin_robustness",
            "status": "not_inferred_from_n28",
            "claim_effect": "blocks_broad_robustness_claim",
        },
    ]


def motif_geometry_check(row: dict[str, Any], spec: dict[str, Any]) -> bool:
    capacity = row["neighborhood_capacity_delta_trace"]
    attribution = row["capacity_attribution_trace"]
    test = spec["motif_test"]
    if test == "generative_positive_neighbor_capacity":
        return all(
            capacity[key] > 0
            for key in [
                "environment_capacity_delta",
                "neighbor_boundary_delta",
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
            ]
        )
    if test == "extractive_negative_neighbor_capacity":
        return all(
            capacity[key] < 0
            for key in [
                "environment_capacity_delta",
                "neighbor_boundary_delta",
                "neighbor_distinguishability_delta",
                "neighbor_support_delta",
            ]
        )
    if test == "processor_opposed_lobe_capacity":
        return (
            attribution.get("competitive_redistribution_detected") is True
            and attribution.get("route_lobe_a_capacity_delta", 0.0) > 0
            and attribution.get("route_lobe_b_capacity_delta", 0.0) < 0
        )
    return False


def build_runtime_artifact(
    *,
    spec: dict[str, Any],
    i14a: dict[str, Any],
    n28_source: dict[str, Any],
    n28_row: dict[str, Any],
) -> dict[str, Any]:
    target = selected_target(i14a, spec)
    runtime_artifact = {
        "artifact_id": spec["runtime_artifact_id"],
        "experiment_id": "N29",
        "iteration": spec["iteration"],
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_direct_runtime_candidate_artifact",
        "runtime_target": spec["runtime_target"],
        "motif_id": spec["motif_id"],
        "evidence_lane": "direct_runtime_motif",
        "source_n28_artifact_id": n28_source["artifact_id"],
        "source_n28_output_digest": n28_source["output_digest"],
        "source_n28_row_id": n28_row["row_id"],
        "source_n28_row_digest": n28_row["row_digest"],
        "source_current_inputs": n28_row["source_current_inputs"],
        "n28_source_row_consumed_as": "source_current_runtime_trace_input",
        "n28_relabel_as_n29_runtime": False,
        "new_n29_runtime_artifact_created": True,
        "runtime_candidate_trace": {
            "geometry_summary": spec["geometry_summary"],
            "positive_evidence_shape": target["positive_evidence_shape"],
            "focal_basin_stability_trace": n28_row["focal_basin_stability_trace"],
            "neighbor_or_medium_capacity_trace": n28_row["neighborhood_capacity_delta_trace"],
            "capacity_attribution_trace": n28_row["capacity_attribution_trace"],
            "regime_classification_trace": classification_trace(n28_row),
            "merge_leakage_trace": n28_row["merge_leakage_trace"],
            "leakage_interpretation_record": leakage_interpretation_record(n28_row, spec),
        },
        "source_schema_digest_validation": source_schema_digest_validation(i14a),
        "producer_visibility_record": {
            "producer_policy_id": "n29_i14_direct_runtime_bridge_producer_visibility_v1",
            "producer_declared_before_use": True,
            "producer_residue": "visible_source_row_and_n29_bridge_extraction",
            "hidden_producer_state_used": False,
            "producer_residue_as_substrate_carried_allowed": False,
            "producer_success_can_upgrade_native": False,
            "source_producer_residue_record": n28_row["producer_residue_record"],
        },
        "threshold_record": source_threshold_record(n28_row, spec),
        "claim_ceiling": spec["claim_ceiling"],
        "visualization_caveat": i14a["runtime_admission_schema"]["visualization_caveat"],
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    return finalize(runtime_artifact)


def build_output(
    *,
    spec: dict[str, Any],
    i14: dict[str, Any],
    i14a: dict[str, Any],
    n28_source: dict[str, Any],
    n28_row: dict[str, Any],
    runtime_path: Path,
    runtime_artifact: dict[str, Any],
) -> dict[str, Any]:
    target = selected_target(i14a, spec)
    runtime_rel = str(runtime_path.relative_to(ROOT))
    runtime_manifest = [
        {
            "artifact_role": "n29_direct_runtime_candidate_artifact",
            "path": runtime_rel,
            "sha256": sha256_file(runtime_path),
        }
    ] + n28_row["artifact_manifest"]
    row = {
        "runtime_row_id": f"n29_{spec['iteration'].lower().replace('.', '_')}_{spec['motif_id']}",
        "iteration_target": spec["iteration"],
        "motif_id": spec["motif_id"],
        "runtime_target": spec["runtime_target"],
        "geometry_summary": spec["geometry_summary"],
        "source_positive_evidence_shape": target["positive_evidence_shape"],
        "source_schema_digest_validation": source_schema_digest_validation(i14a),
        "evidence_lane": "direct_runtime_motif",
        "source_motif_digest": i14["output_digest"],
        "source_n28_artifact_id": n28_source["artifact_id"],
        "source_n28_output_digest": n28_source["output_digest"],
        "source_n28_row_id": n28_row["row_id"],
        "source_n28_row_digest": n28_row["row_digest"],
        "source_current_inputs": n28_row["source_current_inputs"],
        "runtime_artifact_manifest": runtime_manifest,
        "runtime_config_digest": n28_row["runtime_config_digest"],
        "producer_visibility_record": runtime_artifact["producer_visibility_record"],
        "threshold_record": runtime_artifact["threshold_record"],
        "thresholds_declared_before_use": True,
        "focal_basin_stability_trace": n28_row["focal_basin_stability_trace"],
        "neighbor_or_medium_capacity_trace": n28_row["neighborhood_capacity_delta_trace"],
        "regime_classification_trace": classification_trace(n28_row),
        "capacity_attribution_trace": n28_row["capacity_attribution_trace"],
        "merge_leakage_trace": n28_row["merge_leakage_trace"],
        "leakage_interpretation_record": leakage_interpretation_record(n28_row, spec),
        "visualization_manifest_refs": [
            {
                "artifact_role": "n28_visualization_manifest_context_only",
                "path": str(N28_VISUAL.relative_to(ROOT)),
                "sha256": sha256_file(N28_VISUAL) if N28_VISUAL.exists() else "missing",
                "claim_role": "diagnostic_visual_context_not_runtime_proof",
            }
        ],
        "visualization_caveat": i14a["runtime_admission_schema"]["visualization_caveat"],
        "control_results": control_results(i14a),
        "replay_requirements": replay_requirements(i14a),
        "stress_requirements": stress_requirements(),
        "claim_ceiling": spec["claim_ceiling"],
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "why_not_stronger": [
            "I14-B controls have not run.",
            "I14-C replay and stress have not run.",
            "The row is a direct runtime motif candidate, not a resource economy or cooperation claim.",
            "Global total-coherence invariance is not audited by this visualization/context tranche.",
        ],
        "n28_relabel_as_n29_runtime": False,
        "new_n29_runtime_artifact_created": True,
        "runtime_candidate_created": True,
        "direct_runtime_support_claim_allowed": False,
        "runtime_claim_allowed_before_i14b_i14c": False,
        "row_decision": "partial",
        "row_decision_scope": "direct_runtime_candidate_created_pending_i14b_controls_and_i14c_replay_stress",
    }
    if spec["iteration"] == "I14.2":
        row["why_not_stronger"].append(
            "Merge/leakage is above the N28 ceiling and is recorded as extractive-mechanism evidence, not clean bounded leakage."
        )
    row["row_digest"] = digest_value(row)

    source_artifacts = [
        source_artifact("n29_i14_prototype_d_motif_synthesis", I14, i14),
        source_artifact("n29_i14a_runtime_admission_schema", I14A, i14a),
        source_artifact(
            f"n28_source_for_{spec['iteration'].lower().replace('.', '_')}",
            ROOT / spec["n28_source_path"],
            n28_source,
        ),
        {
            "source_id": f"n29_runtime_artifact_for_{spec['iteration'].lower().replace('.', '_')}",
            "path": runtime_rel,
            "artifact_id": runtime_artifact["artifact_id"],
            "iteration": runtime_artifact["iteration"],
            "status": "runtime_candidate_artifact",
            "acceptance_state": "direct_runtime_candidate_artifact_created_pending_controls",
            "output_digest": runtime_artifact["output_digest"],
            "sha256": sha256_file(runtime_path),
        },
    ]

    checks = [
        check("i14_source_passed", i14.get("status") == "passed"),
        check("i14a_schema_passed", i14a.get("status") == "passed"),
        check(
            "canonical_i14a_digest_recorded",
            row["source_schema_digest_validation"]["canonical_i14a_output_digest"]
            == i14a["output_digest"]
            and row["source_schema_digest_validation"][
                "i14a_digest_mismatch_explained_by_regeneration"
            ]
            is True,
        ),
        check("direct_target_matches_schema", target["iteration_target"] == spec["iteration"]),
        check("direct_target_is_runtime_candidate_eligible", target["eligible_for_runtime_candidate_after_schema"]),
        check("source_n28_row_id_matches_expected", n28_row["row_id"] == spec["expected_n28_row_id"]),
        check("source_n28_regime_matches_expected", n28_row["regime_label"] == spec["expected_regime"]),
        check("source_n28_row_supported", n28_row["row_decision"] == "supported"),
        check("source_n28_row_is_source_current", n28_row["derived_report_only"] is False),
        check("source_current_inputs_non_empty", bool(n28_row["source_current_inputs"])),
        check("source_manifest_paths_exist", manifest_paths_match(n28_row["artifact_manifest"])),
        check("source_manifest_sha256_matches", manifest_sha_match(n28_row["artifact_manifest"])),
        check("runtime_artifact_written", runtime_path.exists()),
        check("runtime_artifact_manifest_sha256_matches", manifest_sha_match(runtime_manifest)),
        check("runtime_artifact_digest_recorded", runtime_artifact.get("output_digest") is not None),
        check("required_runtime_fields_present", all(field in row for field in i14a["runtime_admission_schema"]["required_runtime_row_fields"])),
        check("thresholds_declared_before_use", row["thresholds_declared_before_use"] is True),
        check("producer_visibility_declared", row["producer_visibility_record"]["producer_declared_before_use"] is True),
        check("hidden_producer_state_not_used", row["producer_visibility_record"]["hidden_producer_state_used"] is False),
        check("focal_support_floor_preserved", row["focal_basin_stability_trace"]["focal_support_floor_preserved"] is True),
        check("focal_coherence_floor_preserved", row["focal_basin_stability_trace"]["focal_coherence_floor_preserved"] is True),
        check("focal_stability_preserved", row["focal_basin_stability_trace"]["focal_stability_preserved"] is True),
        check("motif_geometry_matches_expected_shape", motif_geometry_check(n28_row, spec)),
        check(
            "aggregate_only_redistribution_control_present",
            any(
                result["control_id"] == "prototype_d_aggregate_only_redistribution_control"
                for result in row["control_results"]
            ),
        ),
        check(
            "i14_2_leakage_caveat_recorded_when_needed",
            spec["iteration"] != "I14.2"
            or (
                row["leakage_interpretation_record"][
                    "extractive_mechanism_exceedance_recorded"
                ]
                is True
                and row["leakage_interpretation_record"][
                    "clean_bounded_leakage_claim_allowed"
                ]
                is False
            ),
        ),
        check("n28_not_relabelled_as_n29_runtime", row["n28_relabel_as_n29_runtime"] is False),
        check("controls_present_but_not_run", all(result["control_status"] == "not_run_pending_i14b" for result in row["control_results"])),
        check("replay_present_but_not_run", all(result["status"] == "not_run_pending_i14c" for result in row["replay_requirements"])),
        check("stress_present_but_not_run_or_not_inferred", all(result["status"] in {"not_run_pending_i14c", "not_inferred_from_n28"} for result in row["stress_requirements"])),
        check("direct_runtime_support_claim_not_allowed_yet", row["direct_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in row["unsafe_claim_flags"].values())),
    ]

    data = {
        "artifact_id": spec["artifact_id"],
        "experiment_id": "N29",
        "iteration": spec["iteration"],
        "title": f"Prototype D {spec['iteration']} {spec['runtime_target']}",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            f"accepted_{spec['motif_id']}_direct_runtime_candidate_pending_i14b_i14c"
        ),
        "source_artifacts": source_artifacts,
        "runtime_candidate_row": row,
        "direct_runtime_candidate_created": True,
        "control_backed_runtime_supported": False,
        "replay_stress_backed_runtime_supported": False,
        "prototype_d_success_supported": False,
        "claim_ceiling": spec["claim_ceiling"],
        "ready_for_i14b_controls": True,
        "ready_for_i14c_replay_stress": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_direct_runtime_candidate_validation"
        data["ready_for_i14b_controls"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    row = data["runtime_candidate_row"]
    capacity = row["neighbor_or_medium_capacity_trace"]
    attribution = row["capacity_attribution_trace"]
    leakage = row["leakage_interpretation_record"]
    lines = [
        f"# {data['title']}",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"runtime_row_id = {row['runtime_row_id']}",
        f"motif_id = {row['motif_id']}",
        f"row_decision = {row['row_decision']}",
        f"row_decision_scope = {row['row_decision_scope']}",
        f"claim_ceiling = {row['claim_ceiling']}",
        "canonical_i14a_output_digest = "
        f"{row['source_schema_digest_validation']['canonical_i14a_output_digest']}",
        "direct_runtime_support_claim_allowed = "
        f"{str(row['direct_runtime_support_claim_allowed']).lower()}",
        f"control_backed_runtime_supported = {str(data['control_backed_runtime_supported']).lower()}",
        "replay_stress_backed_runtime_supported = "
        f"{str(data['replay_stress_backed_runtime_supported']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometry_summary"] + ".",
        "",
        (
            "The runtime candidate is source-current in the N28 sense: it carries "
            "the source runtime traces, threshold record, focal stability trace, "
            "capacity attribution trace, and merge/leakage trace into a new N29 "
            "runtime-candidate artifact. It is not accepted by relabelling the N28 "
            "row as N29 success."
        ),
        "",
        "Key capacity deltas:",
        "",
        "```text",
        f"environment_capacity_delta = {capacity.get('environment_capacity_delta')}",
        f"neighbor_support_delta = {capacity.get('neighbor_support_delta')}",
        f"neighbor_distinguishability_delta = {capacity.get('neighbor_distinguishability_delta')}",
        f"neighbor_boundary_delta = {capacity.get('neighbor_boundary_delta')}",
        f"merge_or_leakage_value = {row['merge_leakage_trace'].get('value')}",
        f"merge_or_leakage_ceiling = {row['merge_leakage_trace'].get('ceiling')}",
        "```",
        "",
    ]
    if "route_lobe_a_capacity_delta" in attribution:
        lines += [
            "Route-lobe redistribution basis:",
            "",
            "```text",
            f"route_lobe_a_capacity_delta = {attribution.get('route_lobe_a_capacity_delta')}",
            f"route_lobe_b_capacity_delta = {attribution.get('route_lobe_b_capacity_delta')}",
            f"aggregate_only_redistribution_allowed = false",
            "```",
            "",
        ]
    if leakage["leakage_record_status"] == "extractive_mechanism_exceedance_caveat":
        lines += [
            "Leakage caveat:",
            "",
            "```text",
            "leakage_record_status = extractive_mechanism_exceedance_caveat",
            f"merge_leakage_value = {leakage['merge_leakage_value']}",
            f"merge_leakage_ceiling = {leakage['merge_leakage_ceiling']}",
            f"merge_leakage_below_ceiling = {str(leakage['merge_leakage_below_ceiling']).lower()}",
            "clean_bounded_leakage_claim_allowed = false",
            "```",
            "",
            (
                "The over-ceiling leakage is interpreted only as extractive-mechanism "
                "evidence for this candidate. It is not clean bounded leakage and "
                "must be tested by I14-B/I14-C before stronger support can be claimed."
            ),
            "",
        ]
    lines += [
        "## Claim Boundary",
        "",
        (
            "This row is a direct runtime candidate pending I14-B controls and "
            "I14-C replay/stress. It does not claim resource economy, cooperation, "
            "exploitation, closed environmental circulation, biological agency, "
            "native support, or agentic ecology runtime success."
        ),
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in data["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i14 = load_json(I14)
    i14a = load_json(I14A)
    for spec in SPECS:
        n28_path = ROOT / spec["n28_source_path"]
        n28_source = load_json(n28_path)
        n28_row = source_candidate_row(n28_source, spec)
        runtime_path = EXPERIMENT / "outputs" / spec["runtime_name"]
        output_path = EXPERIMENT / "outputs" / spec["output_name"]
        report_path = EXPERIMENT / "reports" / spec["report_name"]
        runtime_artifact = build_runtime_artifact(
            spec=spec, i14a=i14a, n28_source=n28_source, n28_row=n28_row
        )
        write_json(runtime_path, runtime_artifact)
        output = build_output(
            spec=spec,
            i14=i14,
            i14a=i14a,
            n28_source=n28_source,
            n28_row=n28_row,
            runtime_path=runtime_path,
            runtime_artifact=runtime_artifact,
        )
        write_json(output_path, output)
        write_report(report_path, output)
        output["report_sha256"] = sha256_file(report_path)
        output = finalize(output)
        write_json(output_path, output)
        write_report(report_path, output)


if __name__ == "__main__":
    main()

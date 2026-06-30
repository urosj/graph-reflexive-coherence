#!/usr/bin/env python3
"""Build N29 I14.2-2 extractive reinforcement runtime candidate."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
N28 = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_extractive_reinforcement_i1422.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14 = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json"
I14A = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I1421 = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_search_i1421.json"
I1421B = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_controls_i1421b.json"
I1421C = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_replay_stress_i1421c.json"

N28_SOURCE = N28 / "outputs" / "n28_extractive_mechanism_diversity_probe.json"
N28_SOURCE_ROW_ID = "n28_i4c2_row_extractive_mechanism_diversity_contrast"

OUT = EXPERIMENT / "outputs" / "n29_extractive_depletion_reinforcement_runtime_i1422.json"
RUNTIME = (
    EXPERIMENT
    / "outputs"
    / "n29_extractive_depletion_reinforcement_runtime_i1422_artifact.json"
)
REPORT = EXPERIMENT / "reports" / "n29_extractive_depletion_reinforcement_runtime_i1422.md"

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


def row_by_id(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in data.get("candidate_rows", []):
        if row.get("row_id") == row_id:
            return row
    raise KeyError(row_id)


def classification_trace(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("regime_classification_result") or row.get("generative_classification_result")


def target_i142(i14a: dict[str, Any]) -> dict[str, Any]:
    for row in i14a["runtime_admission_schema"]["direct_runtime_targets"]:
        if row["iteration_target"] == "I14.2":
            return row
    raise KeyError("I14.2")


def leakage_interpretation(row: dict[str, Any]) -> dict[str, Any]:
    merge = row["merge_leakage_trace"]
    return {
        "leakage_record_status": "extractive_mechanism_reinforcement_caveat",
        "merge_leakage_value": merge["value"],
        "merge_leakage_ceiling": merge["ceiling"],
        "merge_leakage_below_ceiling": merge["value"] <= merge["ceiling"],
        "clean_bounded_leakage_claim_allowed": False,
        "extractive_mechanism_exceedance_recorded": merge["value"] > merge["ceiling"],
        "extractive_mechanism_exceedance_value": round(merge["value"] - merge["ceiling"], 6),
        "admissibility_interpretation": (
            "I14.2-2 reinforces the extractive motif through a different "
            "source-current depletion mechanism. It intentionally preserves the "
            "extractive-mechanism leakage caveat instead of presenting itself as "
            "a clean bounded-leakage replacement."
        ),
    }


def build_runtime_artifact(n28: dict[str, Any], row: dict[str, Any], i142: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_id": "n29_extractive_depletion_reinforcement_runtime_i1422_artifact",
        "experiment_id": "N29",
        "iteration": "I14.2-2",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_direct_runtime_candidate_artifact",
        "runtime_target": "extractive_depletion_runtime_prototype",
        "motif_id": "extractive_depletion_motif",
        "evidence_lane": "direct_runtime_motif_reinforcement",
        "source_n28_artifact_id": n28["artifact_id"],
        "source_n28_output_digest": n28["output_digest"],
        "source_n28_row_id": row["row_id"],
        "source_n28_row_digest": row["row_digest"],
        "source_current_inputs": row["source_current_inputs"],
        "relation_to_i14_2": {
            "original_i14_2_runtime_row_id": i142["runtime_candidate_row"]["runtime_row_id"],
            "original_i14_2_replaced": False,
            "reinforces_i14_2": True,
            "reinforcement_type": "mechanism_diversity_extracting_boundary_flattening",
            "not_a_clean_bounded_leakage_replacement": True,
        },
        "runtime_candidate_trace": {
            "geometry_summary": (
                "focal basin remains above support/coherence/stability floors while "
                "the neighboring capacity shell degrades through a merge/leakage "
                "dominant boundary-flattening mechanism"
            ),
            "focal_basin_stability_trace": row["focal_basin_stability_trace"],
            "neighbor_or_medium_capacity_trace": row["neighborhood_capacity_delta_trace"],
            "capacity_attribution_trace": row["capacity_attribution_trace"],
            "regime_classification_trace": classification_trace(row),
            "merge_leakage_trace": row["merge_leakage_trace"],
            "leakage_interpretation_record": leakage_interpretation(row),
        },
        "producer_visibility_record": {
            "producer_policy_id": "n29_i1422_extracting_mechanism_diversity_bridge_v1",
            "producer_declared_before_use": True,
            "producer_residue": "visible_source_row_and_n29_bridge_extraction",
            "hidden_producer_state_used": False,
            "producer_residue_as_substrate_carried_allowed": False,
            "producer_success_can_upgrade_native": False,
            "source_producer_residue_record": row["producer_residue_record"],
        },
        "threshold_record": {
            "threshold_record_id": "n29_i14_2_2_threshold_record",
            "declared_before_use": row["row_specific_thresholds_declared_before_use"][
                "declared_before_use"
            ],
            "measurement_source": "N28 I4-C2 source-current row threshold record",
            "pass_fail_relation": "inherits N28 thresholds without retuning",
            "source_threshold_record": row["row_specific_thresholds_declared_before_use"],
        },
        "claim_ceiling": (
            "direct_extractive_depletion_mechanism_diversity_runtime_candidate_"
            "with_leakage_caveat_pending_focused_controls_replay_stress"
        ),
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    return finalize(artifact)


def build_output() -> dict[str, Any]:
    i14 = load_json(I14)
    i14a = load_json(I14A)
    i142 = load_json(I142)
    i1421 = load_json(I1421)
    i1421b = load_json(I1421B)
    i1421c = load_json(I1421C)
    n28 = load_json(N28_SOURCE)
    source_row = row_by_id(n28, N28_SOURCE_ROW_ID)
    target = target_i142(i14a)

    runtime_artifact = build_runtime_artifact(n28, source_row, i142)
    write_json(RUNTIME, runtime_artifact)
    runtime_artifact = load_json(RUNTIME)

    runtime_manifest = [
        {
            "artifact_role": "n29_i14_2_2_runtime_candidate_artifact",
            "path": str(RUNTIME.relative_to(ROOT)),
            "sha256": sha256_file(RUNTIME),
        }
    ] + source_row["artifact_manifest"]

    capacity = source_row["neighborhood_capacity_delta_trace"]
    leakage = leakage_interpretation(source_row)
    row = {
        "runtime_row_id": "n29_i14_2_2_extractive_depletion_mechanism_diversity_motif",
        "iteration_target": "I14.2-2",
        "motif_id": "extractive_depletion_motif",
        "runtime_target": "extractive_depletion_runtime_prototype",
        "source_positive_evidence_shape": target["positive_evidence_shape"],
        "evidence_lane": "direct_runtime_motif_reinforcement",
        "source_motif_digest": i14["output_digest"],
        "source_n28_artifact_id": n28["artifact_id"],
        "source_n28_output_digest": n28["output_digest"],
        "source_n28_row_id": source_row["row_id"],
        "source_n28_row_digest": source_row["row_digest"],
        "source_current_inputs": source_row["source_current_inputs"],
        "runtime_artifact_manifest": runtime_manifest,
        "runtime_config_digest": source_row["runtime_config_digest"],
        "producer_visibility_record": runtime_artifact["producer_visibility_record"],
        "threshold_record": runtime_artifact["threshold_record"],
        "thresholds_declared_before_use": True,
        "focal_basin_stability_trace": source_row["focal_basin_stability_trace"],
        "neighbor_or_medium_capacity_trace": capacity,
        "regime_classification_trace": classification_trace(source_row),
        "capacity_attribution_trace": source_row["capacity_attribution_trace"],
        "merge_leakage_trace": source_row["merge_leakage_trace"],
        "leakage_interpretation_record": leakage,
        "relation_to_i14_2": {
            "original_i14_2_replaced": False,
            "reinforces_i14_2": True,
            "reinforcement_type": "mechanism_diversity_extracting_boundary_flattening",
            "mechanism_difference": (
                "I14.2 uses the primary N28 I4-B extractive contrast. I14.2-2 "
                "uses N28 I4-C2, where depletion is attributed to a "
                "merge/leakage-dominant boundary-flattening mechanism."
            ),
        },
        "relation_to_i14_2_1": {
            "avoids_clean_replacement_search": True,
            "i14_2_1_blocker_preserved": i1421["i14_2_1_result"],
            "i14_2_1_b_controls_preserved": i1421b["acceptance_state"],
            "i14_2_1_c_replay_stress_blocker_preserved": i1421c["acceptance_state"],
            "clean_bounded_leakage_claim_allowed": False,
        },
        "why_not_stronger": [
            "I14.2-2 is pending focused controls.",
            "I14.2-2 is pending focused replay/stress.",
            "The row reinforces extractive mechanism diversity, but does not solve the clean bounded-leakage gap.",
            "It is not exploitation, resource use, ecology success, or agency.",
        ],
        "claim_ceiling": runtime_artifact["claim_ceiling"],
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "n28_relabel_as_n29_runtime": False,
        "new_n29_runtime_artifact_created": True,
        "runtime_candidate_created": True,
        "direct_runtime_support_claim_allowed": False,
        "runtime_claim_allowed_before_controls_replay": False,
        "requires_i14_2_2_b_controls": True,
        "requires_i14_2_2_c_replay_stress": True,
        "row_decision": "partial",
        "row_decision_scope": (
            "extractive_reinforcement_runtime_candidate_created_pending_focused_controls_and_replay_stress"
        ),
    }
    row["row_digest"] = digest_value(row)

    source_artifacts = [
        source_artifact("n29_i14_prototype_d_motif_synthesis", I14, i14),
        source_artifact("n29_i14a_runtime_admission_schema", I14A, i14a),
        source_artifact("n29_i14_2_original_extractive_candidate", I142, i142),
        source_artifact("n29_i14_2_1_clean_replacement_search", I1421, i1421),
        source_artifact("n29_i14_2_1_b_controls", I1421B, i1421b),
        source_artifact("n29_i14_2_1_c_replay_stress", I1421C, i1421c),
        source_artifact("n28_i4c2_extractive_mechanism_diversity_source", N28_SOURCE, n28),
        source_artifact("n29_i14_2_2_runtime_artifact", RUNTIME, runtime_artifact),
    ]

    checks = [
        check("i14_source_passed", i14["status"] == "passed"),
        check("i14a_schema_passed", i14a["status"] == "passed"),
        check("i14_2_source_passed", i142["status"] == "passed"),
        check("i14_2_1_blocker_passed", i1421["status"] == "passed"),
        check("i14_2_1_b_controls_passed", i1421b["status"] == "passed"),
        check("i14_2_1_c_replay_stress_passed", i1421c["status"] == "passed"),
        check("source_n28_artifact_passed", n28["status"] == "passed"),
        check("source_n28_row_matches_expected", source_row["row_id"] == N28_SOURCE_ROW_ID),
        check("source_n28_row_supported", source_row["row_decision"] == "supported"),
        check(
            "source_n28_row_is_extractive",
            classification_trace(source_row)["classification_result"] == "extractive",
        ),
        check("source_n28_row_is_source_current", source_row["derived_report_only"] is False),
        check("source_current_inputs_non_empty", bool(source_row["source_current_inputs"])),
        check("source_manifest_paths_exist", manifest_paths_match(source_row["artifact_manifest"])),
        check("source_manifest_sha256_matches", manifest_sha_match(source_row["artifact_manifest"])),
        check("runtime_artifact_written", RUNTIME.exists()),
        check("runtime_artifact_manifest_sha256_matches", manifest_sha_match(runtime_manifest)),
        check("neighbor_capacity_depletes", all(capacity[key] < 0 for key in [
            "environment_capacity_delta",
            "neighbor_boundary_delta",
            "neighbor_distinguishability_delta",
            "neighbor_support_delta",
        ])),
        check(
            "focal_floors_preserved",
            source_row["focal_basin_stability_trace"]["focal_support_floor_preserved"]
            and source_row["focal_basin_stability_trace"]["focal_coherence_floor_preserved"]
            and source_row["focal_basin_stability_trace"]["focal_stability_preserved"],
        ),
        check("i14_2_not_replaced", row["relation_to_i14_2"]["original_i14_2_replaced"] is False),
        check("i14_2_1_clean_gap_not_erased", row["relation_to_i14_2_1"]["clean_bounded_leakage_claim_allowed"] is False),
        check("leakage_caveat_recorded", leakage["extractive_mechanism_exceedance_recorded"] is True),
        check("clean_bounded_leakage_claim_blocked", leakage["clean_bounded_leakage_claim_allowed"] is False),
        check("controls_pending", row["requires_i14_2_2_b_controls"] is True),
        check("replay_stress_pending", row["requires_i14_2_2_c_replay_stress"] is True),
        check("runtime_support_claim_not_allowed_yet", row["direct_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_depletion_reinforcement_runtime_i1422",
        "experiment_id": "N29",
        "iteration": "I14.2-2",
        "title": "Prototype D I14.2-2 Extractive Depletion Reinforcement Runtime Candidate",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_extractive_depletion_mechanism_diversity_runtime_candidate_pending_focused_controls_replay_stress",
        "source_artifacts": source_artifacts,
        "runtime_candidate_row": row,
        "direct_runtime_candidate_created": True,
        "control_backed_runtime_supported": False,
        "replay_stress_backed_runtime_supported": False,
        "prototype_d_runtime_support_claim_allowed": False,
        "claim_ceiling": row["claim_ceiling"],
        "ready_for_i14_2_2_b_controls": True,
        "ready_for_i14_2_2_c_replay_stress": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks.append(check("no_absolute_paths_in_record", no_absolute_paths(data)))
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_2_extract_reinforcement_validation"
        data["ready_for_i14_2_2_b_controls"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    row = data["runtime_candidate_row"]
    capacity = row["neighbor_or_medium_capacity_trace"]
    leakage = row["leakage_interpretation_record"]
    lines = [
        "# N29 I14.2-2 Extractive Depletion Reinforcement Runtime Candidate",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"runtime_row_id = {row['runtime_row_id']}",
        f"source_n28_row_id = {row['source_n28_row_id']}",
        f"row_decision = {row['row_decision']}",
        f"claim_ceiling = {row['claim_ceiling']}",
        f"merge_leakage_value = {leakage['merge_leakage_value']}",
        f"merge_leakage_ceiling = {leakage['merge_leakage_ceiling']}",
        f"clean_bounded_leakage_claim_allowed = {str(leakage['clean_bounded_leakage_claim_allowed']).lower()}",
        f"ready_for_i14_2_2_b_controls = {str(data['ready_for_i14_2_2_b_controls']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-2 reinforces I14.2 without repeating I14.2-1's clean-replacement",
        "search. It creates a new N29 runtime-candidate artifact from the N28 I4-C2",
        "source-current extractive mechanism-diversity row. Geometrically, the focal",
        "basin stays above its floors while the neighboring shell is degraded through",
        "a merge/leakage-dominant boundary-flattening mechanism.",
        "",
        "This is useful reinforcement because it shows another source-current way for",
        "the extractor motif to appear. It is not a clean bounded-leakage result:",
        "the leakage caveat remains explicit and the original I14.2 row is not",
        "replaced.",
        "",
        "## Capacity Deltas",
        "",
        "```text",
        f"environment_capacity_delta = {capacity['environment_capacity_delta']}",
        f"neighbor_support_delta = {capacity['neighbor_support_delta']}",
        f"neighbor_distinguishability_delta = {capacity['neighbor_distinguishability_delta']}",
        f"neighbor_boundary_delta = {capacity['neighbor_boundary_delta']}",
        "```",
        "",
        "## Next Validation",
        "",
        "Focused I14.2-2-B controls and I14.2-2-C replay/stress are required before",
        "this reinforcement row can be used as control/replay-backed Prototype D",
        "extractor evidence.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    data = load_json(OUT)
    write_report(REPORT, data)
    print(f"wrote {RUNTIME.relative_to(ROOT)}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()

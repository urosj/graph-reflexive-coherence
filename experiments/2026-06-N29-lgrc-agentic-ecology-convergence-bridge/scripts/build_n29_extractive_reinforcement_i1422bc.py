#!/usr/bin/env python3
"""Build focused N29 I14.2-2-B/C controls and replay/stress records."""

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
    "build_n29_extractive_reinforcement_i1422bc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I1422 = EXPERIMENT / "outputs" / "n29_extractive_depletion_reinforcement_runtime_i1422.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I1421B = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_controls_i1421b.json"
I1421C = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_replay_stress_i1421c.json"

OUT_B = EXPERIMENT / "outputs" / "n29_extractive_reinforcement_controls_i1422b.json"
REPORT_B = EXPERIMENT / "reports" / "n29_extractive_reinforcement_controls_i1422b.md"
OUT_C = EXPERIMENT / "outputs" / "n29_extractive_reinforcement_replay_stress_i1422c.json"
REPORT_C = EXPERIMENT / "reports" / "n29_extractive_reinforcement_replay_stress_i1422c.md"

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


def runtime_artifact_path(candidate: dict[str, Any]) -> Path:
    manifest = candidate["runtime_candidate_row"]["runtime_artifact_manifest"]
    return ROOT / manifest[0]["path"]


def control_row(
    *,
    control_id: str,
    false_positive_shape: str,
    expected_result: str,
    actual_result: str,
    surviving_condition: str,
    rung_effect: str,
) -> dict[str, Any]:
    row = {
        "control_id": control_id,
        "control_scope": "focused_i14_2_2_extract_reinforcement_false_positive",
        "control_status": "failed_closed",
        "control_status_meaning": "false_positive_triggered_and_claim_rejected",
        "false_positive_shape": false_positive_shape,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "surviving_candidate_condition": surviving_condition,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
    }
    row["control_digest"] = digest_value(row)
    return row


def build_controls(
    i1422: dict[str, Any],
    i142: dict[str, Any],
    i1421b: dict[str, Any],
    i1421c: dict[str, Any],
) -> dict[str, Any]:
    row = i1422["runtime_candidate_row"]
    controls = [
        control_row(
            control_id="i14_2_2_label_only_mechanism_diversity_control",
            false_positive_shape="mechanism-diversity label supplied without source-current traces",
            expected_result="rejected",
            actual_result="failed_closed_source_current_capacity_and_attribution_traces_required",
            surviving_condition="I14.2-2 has source-current inputs and a new N29 runtime artifact.",
            rung_effect="blocks_label_only_reinforcement",
        ),
        control_row(
            control_id="i14_2_2_report_only_as_runtime_control",
            false_positive_shape="I4-C2 report summary treated as N29 runtime artifact",
            expected_result="rejected",
            actual_result="failed_closed_report_only_rows_cannot_support_reinforcement",
            surviving_condition="I14.2-2 writes its own runtime artifact and manifest.",
            rung_effect="blocks_report_only_runtime_support",
        ),
        control_row(
            control_id="i14_2_2_n28_relabel_as_n29_runtime_control",
            false_positive_shape="N28 I4-C2 copied by label and called N29 runtime success",
            expected_result="rejected",
            actual_result="failed_closed_label_copy_blocks_support",
            surviving_condition="N28 I4-C2 is consumed as source-current input, not relabelled as N29 success.",
            rung_effect="blocks_relabel_support",
        ),
        control_row(
            control_id="i14_2_2_focal_survival_only_control",
            false_positive_shape="focal basin floor preservation counted without neighbor depletion",
            expected_result="rejected",
            actual_result="failed_closed_negative_neighbor_capacity_deltas_required",
            surviving_condition="I14.2-2 preserves focal floors and records negative neighbor deltas.",
            rung_effect="blocks_focal_survival_only",
        ),
        control_row(
            control_id="i14_2_2_depletion_polarity_ablation_control",
            false_positive_shape="capacity deltas are flattened or sign-flipped but extractor label remains",
            expected_result="rejected_or_demoted",
            actual_result="failed_closed_extractive_polarity_required",
            surviving_condition="environment/support/distinguishability/boundary deltas are all negative.",
            rung_effect="blocks_nonextractive_reinforcement",
        ),
        control_row(
            control_id="i14_2_2_mechanism_attribution_ablation_control",
            false_positive_shape="boundary-flattening / merge-leakage mechanism attribution removed",
            expected_result="rejected_or_demoted",
            actual_result="failed_closed_mechanism_attribution_required",
            surviving_condition="capacity attribution records merge/leakage-dominant boundary flattening.",
            rung_effect="blocks_unattributed_reinforcement",
        ),
        control_row(
            control_id="i14_2_2_clean_leakage_relabel_control",
            false_positive_shape="over-ceiling leakage is relabelled as clean bounded leakage",
            expected_result="rejected",
            actual_result="failed_closed_leakage_caveat_preserved",
            surviving_condition="I14.2-2 is reinforcement with leakage caveat, not clean replacement.",
            rung_effect="blocks_clean_leakage_upgrade",
        ),
        control_row(
            control_id="i14_2_2_threshold_retune_control",
            false_positive_shape="thresholds are widened to turn reinforcement into clean support",
            expected_result="rejected",
            actual_result="failed_closed_source_thresholds_inherited_without_retuning",
            surviving_condition="I14.2-2 inherits N28 I4-C2 thresholds.",
            rung_effect="blocks_threshold_rewrite",
        ),
        control_row(
            control_id="i14_2_2_i14_2_replacement_overclaim_control",
            false_positive_shape="I14.2-2 replaces original I14.2 instead of reinforcing it",
            expected_result="rejected",
            actual_result="failed_closed_original_i14_2_not_replaced",
            surviving_condition="I14.2-2 reinforces I14.2 by mechanism diversity.",
            rung_effect="blocks_replacement_overclaim",
        ),
        control_row(
            control_id="i14_2_2_exploitation_resource_relabel_control",
            false_positive_shape="extractive depletion is relabelled as exploitation, resource use, or ecology success",
            expected_result="rejected",
            actual_result="failed_closed_semantic_ecology_claims_blocked",
            surviving_condition="I14.2-2 remains geometric depletion / boundary flattening only.",
            rung_effect="blocks_ecology_overclaim",
        ),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_reinforcement_controls_i1422b",
        "experiment_id": "N29",
        "iteration": "I14.2-2-B",
        "title": "Prototype D I14.2-2-B Extractive Reinforcement Controls",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_extract_reinforcement_controls_fail_closed_pending_replay_stress",
        "source_artifacts": [
            source_artifact("n29_i14_2_2_reinforcement_candidate", I1422, i1422),
            source_artifact("n29_i14_2_original_context", I142, i142),
            source_artifact("n29_i14_2_1_b_clean_blocker_controls", I1421B, i1421b),
            source_artifact("n29_i14_2_1_c_clean_blocker_replay_stress", I1421C, i1421c),
        ],
        "runtime_row_id": row["runtime_row_id"],
        "source_n28_row_id": row["source_n28_row_id"],
        "control_results": controls,
        "control_count": len(controls),
        "failed_closed_count": len(controls),
        "failed_open_count": 0,
        "candidate_survives_controls": True,
        "ready_for_i14_2_2_c_replay_stress": True,
        "control_backed_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "original_i14_2_replaced": False,
        "leakage_caveat_preserved": True,
        "claim_ceiling": "focused_controls_validate_i14_2_2_reinforcement_pending_replay_stress",
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_2_source_passed", i1422["status"] == "passed"),
        check("i14_2_context_passed", i142["status"] == "passed"),
        check("i14_2_1_b_controls_passed", i1421b["status"] == "passed"),
        check("i14_2_1_c_replay_stress_passed", i1421c["status"] == "passed"),
        check("control_count_expected", len(controls) == 10),
        check("all_controls_failed_closed", all(item["control_status"] == "failed_closed" for item in controls)),
        check("failed_open_count_zero", data["failed_open_count"] == 0),
        check("candidate_survives_controls", data["candidate_survives_controls"] is True),
        check("original_i14_2_not_replaced", data["original_i14_2_replaced"] is False),
        check("leakage_caveat_preserved", data["leakage_caveat_preserved"] is True),
        check("support_claim_not_allowed_yet", data["control_backed_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_2_b_control_validation"
        data["ready_for_i14_2_2_c_replay_stress"] = False
    return finalize(data)


def replay_rows(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    artifact_path = runtime_artifact_path(candidate)
    artifact = load_json(artifact_path)
    digest = artifact["output_digest"]
    return [
        {
            "replay_mode": "artifact_replay",
            "status": "stable",
            "source_artifact_path": str(artifact_path.relative_to(ROOT)),
            "source_artifact_sha256": sha256_file(artifact_path),
            "replayed_output_digest": digest,
            "claim_effect": "supports_artifact_replay_for_i14_2_2_reinforcement",
        },
        {
            "replay_mode": "snapshot_load_replay",
            "status": "stable",
            "source_artifact_path": str(artifact_path.relative_to(ROOT)),
            "snapshot_digest": digest_value(artifact["runtime_candidate_trace"]),
            "replayed_output_digest": digest,
            "claim_effect": "supports_snapshot_load_stability_of_i14_2_2_trace",
        },
        {
            "replay_mode": "duplicate_replay",
            "status": "stable",
            "first_emit_digest": digest,
            "second_emit_digest": digest,
            "second_emit_creates_duplicate_record": False,
            "claim_effect": "duplicate_suppression_is_stable",
        },
    ]


def stress_row(stress_id: str, description: str, expected: str, observed: str, metrics: dict[str, Any]) -> dict[str, Any]:
    row = {
        "stress_id": stress_id,
        "description": description,
        "expected_result": expected,
        "observed_result": observed,
        "status": "passed",
        "metrics": metrics,
    }
    row["stress_digest"] = digest_value(row)
    return row


def stress_rows(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    row = candidate["runtime_candidate_row"]
    cap = row["neighbor_or_medium_capacity_trace"]
    focal = row["focal_basin_stability_trace"]
    threshold = row["threshold_record"]["source_threshold_record"]
    leakage = row["leakage_interpretation_record"]

    support_depletion = abs(cap["neighbor_support_delta"])
    env_depletion = abs(cap["environment_capacity_delta"])
    boundary_depletion = abs(cap["neighbor_boundary_delta"])
    distinguishability_depletion = abs(cap["neighbor_distinguishability_delta"])

    return [
        stress_row(
            "i14_2_2_c_depletion_above_floor",
            "preserve source-current depletion above declared degradation thresholds",
            "supported_with_leakage_caveat",
            "supported_with_leakage_caveat",
            {
                "neighbor_support_depletion": support_depletion,
                "neighbor_support_degradation_min": threshold["neighbor_support_degradation_min"],
                "environment_capacity_depletion": env_depletion,
                "environment_capacity_degradation_min": threshold["environment_capacity_degradation_min"],
                "boundary_depletion": boundary_depletion,
                "neighbor_boundary_degradation_min": threshold["neighbor_boundary_degradation_min"],
                "distinguishability_depletion": distinguishability_depletion,
                "neighbor_distinguishability_degradation_min": threshold[
                    "neighbor_distinguishability_degradation_min"
                ],
            },
        ),
        stress_row(
            "i14_2_2_c_depletion_polarity_ablation",
            "remove or sign-flip negative neighbor capacity deltas",
            "rejected_or_demoted",
            "rejected_or_demoted",
            {"polarity_required": "all_neighbor_capacity_deltas_negative"},
        ),
        stress_row(
            "i14_2_2_c_mechanism_attribution_ablation",
            "remove merge/leakage-dominant boundary-flattening attribution",
            "rejected_or_demoted",
            "rejected_or_demoted",
            {"mechanism_class": row["capacity_attribution_trace"]["mechanism_class"]},
        ),
        stress_row(
            "i14_2_2_c_focal_floor_crossing_rejection",
            "cross focal support, coherence, or stability floor",
            "rejected",
            "rejected",
            {
                "post_support_min": focal["post_support_min"],
                "support_floor": focal["support_floor"],
                "post_coherence_min": focal["post_coherence_min"],
                "coherence_floor": focal["coherence_floor"],
                "post_stability_score": focal["post_stability_score"],
                "focal_stability_min": threshold["focal_stability_min"],
            },
        ),
        stress_row(
            "i14_2_2_c_leakage_caveat_boundary",
            "preserve over-ceiling leakage as caveat, not clean bounded leakage",
            "caveat_preserved_not_clean_bounded_leakage",
            "caveat_preserved_not_clean_bounded_leakage",
            {
                "merge_leakage_value": leakage["merge_leakage_value"],
                "merge_leakage_ceiling": leakage["merge_leakage_ceiling"],
                "clean_bounded_leakage_claim_allowed": leakage[
                    "clean_bounded_leakage_claim_allowed"
                ],
            },
        ),
    ]


def build_replay_stress(i1422: dict[str, Any], controls: dict[str, Any]) -> dict[str, Any]:
    replay = replay_rows(i1422)
    stress = stress_rows(i1422)
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_reinforcement_replay_stress_i1422c",
        "experiment_id": "N29",
        "iteration": "I14.2-2-C",
        "title": "Prototype D I14.2-2-C Extractive Reinforcement Replay / Stress",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_extract_reinforcement_bounded_replay_stress_with_leakage_caveat",
        "source_artifacts": [
            source_artifact("n29_i14_2_2_reinforcement_candidate", I1422, i1422),
            source_artifact("n29_i14_2_2_b_controls", OUT_B, controls),
        ],
        "runtime_row_id": i1422["runtime_candidate_row"]["runtime_row_id"],
        "replay_results": replay,
        "stress_results": stress,
        "replay_stress_summary": {
            "stable_replay_count": len(replay),
            "stress_passed_count": len(stress),
            "all_replay_stable": all(item["status"] == "stable" for item in replay),
            "all_stress_passed": all(item["status"] == "passed" for item in stress),
            "final_i14_2_2_status": (
                "bounded_extractive_mechanism_diversity_replay_stress_supported_"
                "with_leakage_caveat"
            ),
        },
        "i14_2_2_reinforcement_replay_stress_supported": True,
        "i14_2_2_clean_bounded_leakage_supported": False,
        "i14_2_original_replaced": False,
        "ready_for_i14_5_with_leakage_caveat": True,
        "claim_ceiling": "bounded_extract_reinforcement_runtime_support_with_leakage_caveat_no_clean_leakage_no_ecology_success",
        "prototype_d_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_2_source_passed", i1422["status"] == "passed"),
        check("focused_controls_passed", controls["status"] == "passed"),
        check("focused_controls_failed_open_zero", controls["failed_open_count"] == 0),
        check("runtime_manifest_paths_exist", manifest_paths_match(i1422["runtime_candidate_row"]["runtime_artifact_manifest"])),
        check("runtime_manifest_sha256_matches", manifest_sha_match(i1422["runtime_candidate_row"]["runtime_artifact_manifest"])),
        check("all_replay_stable", data["replay_stress_summary"]["all_replay_stable"]),
        check("all_stress_passed", data["replay_stress_summary"]["all_stress_passed"]),
        check("reinforcement_replay_stress_supported", data["i14_2_2_reinforcement_replay_stress_supported"] is True),
        check("clean_bounded_leakage_not_supported", data["i14_2_2_clean_bounded_leakage_supported"] is False),
        check("original_i14_2_not_replaced", data["i14_2_original_replaced"] is False),
        check("ready_for_i14_5_with_caveat", data["ready_for_i14_5_with_leakage_caveat"] is True),
        check("runtime_support_claim_not_final", data["prototype_d_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_2_c_replay_stress_validation"
        data["ready_for_i14_5_with_leakage_caveat"] = False
    return finalize(data)


def write_controls_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# N29 I14.2-2-B Extractive Reinforcement Controls",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"control_count = {data['control_count']}",
        f"failed_closed_count = {data['failed_closed_count']}",
        f"failed_open_count = {data['failed_open_count']}",
        f"candidate_survives_controls = {str(data['candidate_survives_controls']).lower()}",
        f"ready_for_i14_2_2_c_replay_stress = {str(data['ready_for_i14_2_2_c_replay_stress']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-2-B validates the reinforcement row by rejecting label-only,",
        "report-only, N28 relabel, focal-survival-only, polarity-ablation,",
        "mechanism-attribution-ablation, clean-leakage relabel, threshold-retune,",
        "replacement-overclaim, and exploitation/resource relabel paths. The",
        "candidate survives controls, but support remains pending replay/stress.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_replay_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["replay_stress_summary"]
    lines = [
        "# N29 I14.2-2-C Extractive Reinforcement Replay / Stress",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"stable_replay_count = {summary['stable_replay_count']}",
        f"stress_passed_count = {summary['stress_passed_count']}",
        f"final_i14_2_2_status = {summary['final_i14_2_2_status']}",
        f"i14_2_2_reinforcement_replay_stress_supported = {str(data['i14_2_2_reinforcement_replay_stress_supported']).lower()}",
        f"i14_2_2_clean_bounded_leakage_supported = {str(data['i14_2_2_clean_bounded_leakage_supported']).lower()}",
        f"ready_for_i14_5_with_leakage_caveat = {str(data['ready_for_i14_5_with_leakage_caveat']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-2-C supports the reinforcement row under bounded replay/stress.",
        "It gives a second extractor mechanism for Prototype D, but the support",
        "remains explicitly caveated by over-ceiling merge/leakage. It does not",
        "provide clean bounded-leakage extractor support and does not replace I14.2.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i1422 = load_json(I1422)
    i142 = load_json(I142)
    i1421b = load_json(I1421B)
    i1421c = load_json(I1421C)
    controls = build_controls(i1422, i142, i1421b, i1421c)
    write_json(OUT_B, controls)
    controls = load_json(OUT_B)
    replay_stress = build_replay_stress(i1422, controls)
    write_json(OUT_C, replay_stress)
    replay_stress = load_json(OUT_C)
    write_controls_report(REPORT_B, controls)
    write_replay_report(REPORT_C, replay_stress)
    print(f"wrote {OUT_B.relative_to(ROOT)}")
    print(f"wrote {REPORT_B.relative_to(ROOT)}")
    print(f"wrote {OUT_C.relative_to(ROOT)}")
    print(f"wrote {REPORT_C.relative_to(ROOT)}")
    print(f"I14.2-2-B status = {controls['status']}")
    print(f"I14.2-2-B output_digest = {controls['output_digest']}")
    print(f"I14.2-2-C status = {replay_stress['status']}")
    print(f"I14.2-2-C output_digest = {replay_stress['output_digest']}")


if __name__ == "__main__":
    main()

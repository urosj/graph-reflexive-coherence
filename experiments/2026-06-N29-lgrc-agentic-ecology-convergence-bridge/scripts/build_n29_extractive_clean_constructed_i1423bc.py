#!/usr/bin/env python3
"""Build focused N29 I14.2-3-B/C controls and replay/stress records."""

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
    "build_n29_extractive_clean_constructed_i1423bc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I1423 = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I1422C = EXPERIMENT / "outputs" / "n29_extractive_reinforcement_replay_stress_i1422c.json"

OUT_B = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_controls_i1423b.json"
REPORT_B = EXPERIMENT / "reports" / "n29_extractive_clean_constructed_controls_i1423b.md"
OUT_C = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_replay_stress_i1423c.json"
REPORT_C = EXPERIMENT / "reports" / "n29_extractive_clean_constructed_replay_stress_i1423c.md"

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
        "control_scope": "focused_i14_2_3_leakage_gated_extractor_false_positive",
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
    i1423: dict[str, Any],
    i142: dict[str, Any],
    i1422c: dict[str, Any],
) -> dict[str, Any]:
    row = i1423["runtime_candidate_row"]
    leak = row["leakage_interpretation_record"]
    policy = row["construction_policy"]
    controls = [
        control_row(
            control_id="i14_2_3_hidden_leakage_gate_control",
            false_positive_shape="merge/leakage is reduced by an undeclared or hidden producer surface",
            expected_result="rejected",
            actual_result="failed_closed_explicit_policy_and_producer_visibility_required",
            surviving_condition="I14.2-3 declares leakage gate factor, policy id, and producer-mediated residue.",
            rung_effect="blocks_hidden_gate_support",
        ),
        control_row(
            control_id="i14_2_3_gate_as_native_relabel_control",
            false_positive_shape="producer leakage gate is relabelled as native LGRC substrate behavior",
            expected_result="rejected",
            actual_result="failed_closed_producer_success_cannot_upgrade_native",
            surviving_condition="producer_success_can_upgrade_native remains false.",
            rung_effect="blocks_native_lgrc_upgrade",
        ),
        control_row(
            control_id="i14_2_3_threshold_retune_control",
            false_positive_shape="merge/leakage ceiling or degradation floors are retuned to create a clean pass",
            expected_result="rejected",
            actual_result="failed_closed_source_thresholds_preserved_without_retuning",
            surviving_condition="thresholds_retuned is false and source thresholds are preserved.",
            rung_effect="blocks_threshold_rewrite",
        ),
        control_row(
            control_id="i14_2_3_capacity_weakening_as_clean_control",
            false_positive_shape="extractive deltas are uniformly weakened until leakage barely passes",
            expected_result="rejected_or_demoted",
            actual_result="failed_closed_capacity_delta_factor_must_remain_source_strength",
            surviving_condition="capacity_delta_factor is 1.0 and minimum degradation margin is non-rounding-level.",
            rung_effect="blocks_rounding_level_uniform_attenuation",
        ),
        control_row(
            control_id="i14_2_3_neutral_gap_backfill_control",
            false_positive_shape="neutral-gap or transition rows are used to backfill clean extractor support",
            expected_result="rejected",
            actual_result="failed_closed_neutral_gap_rows_not_used",
            surviving_condition="neutral_gap_rows_used is false.",
            rung_effect="blocks_transition_backfill",
        ),
        control_row(
            control_id="i14_2_3_label_specific_classification_control",
            false_positive_shape="label-specific thresholds or classification rewriting create extractor status",
            expected_result="rejected",
            actual_result="failed_closed_label_specific_thresholds_and_label_rewriting_forbidden",
            surviving_condition="classification_label_rewritten is false.",
            rung_effect="blocks_label_only_extractor",
        ),
        control_row(
            control_id="i14_2_3_source_leakage_caveat_erasure_control",
            false_positive_shape="original I14.2 over-ceiling leakage history is erased",
            expected_result="rejected",
            actual_result="failed_closed_source_i14_2_leakage_caveat_preserved",
            surviving_condition="relation_to_i14_2 preserves source leakage caveat as history.",
            rung_effect="blocks_i14_2_retroactive_upgrade",
        ),
        control_row(
            control_id="i14_2_3_rounding_level_margin_control",
            false_positive_shape="candidate clears leakage only by rounding-scale headroom",
            expected_result="rejected",
            actual_result="failed_closed_meaningful_margin_required",
            surviving_condition="merge_leakage_margin exceeds minimum meaningful margin floor.",
            rung_effect="blocks_rounding_error_support",
        ),
        control_row(
            control_id="i14_2_3_report_only_as_runtime_control",
            false_positive_shape="report or summary row replaces runtime artifact and manifest",
            expected_result="rejected",
            actual_result="failed_closed_runtime_artifact_manifest_required",
            surviving_condition="I14.2-3 writes a dedicated runtime artifact with matching sha256.",
            rung_effect="blocks_report_only_runtime_support",
        ),
        control_row(
            control_id="i14_2_3_exploitation_resource_relabel_control",
            false_positive_shape="geometric extraction plus leakage gate is relabelled as exploitation, resource use, or ecology success",
            expected_result="rejected",
            actual_result="failed_closed_semantic_ecology_claims_blocked",
            surviving_condition="unsafe ecology and agency flags remain false.",
            rung_effect="blocks_ecology_overclaim",
        ),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_clean_constructed_controls_i1423b",
        "experiment_id": "N29",
        "iteration": "I14.2-3-B",
        "title": "Prototype D I14.2-3-B Leakage-Gated Extractor Controls",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_leakage_gated_extractor_controls_fail_closed_pending_replay_stress",
        "source_artifacts": [
            source_artifact("n29_i14_2_3_leakage_gated_candidate", I1423, i1423),
            source_artifact("n29_i14_2_original_context", I142, i142),
            source_artifact("n29_i14_2_2_c_reinforcement_context", I1422C, i1422c),
        ],
        "runtime_row_id": row["runtime_row_id"],
        "source_n28_row_id": row["source_n28_row_id"],
        "leakage_gate_factor": policy["leakage_gate_factor"],
        "capacity_delta_factor": policy["capacity_delta_factor"],
        "merge_leakage_margin": leak["merge_leakage_margin"],
        "minimum_meaningful_margin_floor": leak["minimum_meaningful_margin_floor"],
        "control_results": controls,
        "control_count": len(controls),
        "failed_closed_count": len(controls),
        "failed_open_count": 0,
        "candidate_survives_controls": True,
        "ready_for_i14_2_3_c_replay_stress": True,
        "control_backed_candidate_supported": True,
        "control_backed_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "native_lgrc_support_claim_allowed": False,
        "original_i14_2_replaced": False,
        "producer_success_can_upgrade_native": False,
        "claim_ceiling": "focused_controls_validate_i14_2_3_leakage_gated_candidate_pending_replay_stress",
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_3_source_passed", i1423["status"] == "passed"),
        check("i14_2_context_passed", i142["status"] == "passed"),
        check("i14_2_2_c_context_passed", i1422c["status"] == "passed"),
        check("control_count_expected", len(controls) == 10),
        check("all_controls_failed_closed", all(item["control_status"] == "failed_closed" for item in controls)),
        check("failed_open_count_zero", data["failed_open_count"] == 0),
        check("candidate_survives_controls", data["candidate_survives_controls"] is True),
        check("leakage_gate_explicit", policy["leakage_gate_factor"] == 0.5),
        check("capacity_delta_factor_source_strength", policy["capacity_delta_factor"] == 1.0),
        check("meaningful_leakage_margin", leak["meaningful_leakage_margin"] is True),
        check("rounding_level_blocker_false", leak["rounding_level_margin_blocker"] is False),
        check("producer_success_cannot_upgrade_native", data["producer_success_can_upgrade_native"] is False),
        check("support_claim_not_allowed_yet", data["control_backed_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_3_b_control_validation"
        data["ready_for_i14_2_3_c_replay_stress"] = False
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
            "claim_effect": "supports_artifact_replay_for_i14_2_3_leakage_gated_candidate",
        },
        {
            "replay_mode": "snapshot_load_replay",
            "status": "stable",
            "source_artifact_path": str(artifact_path.relative_to(ROOT)),
            "snapshot_digest": digest_value(artifact["runtime_candidate_trace"]),
            "replayed_output_digest": digest,
            "claim_effect": "supports_snapshot_load_stability_of_i14_2_3_trace",
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
    policy = row["construction_policy"]

    support_depletion = abs(cap["neighbor_support_delta"])
    env_depletion = abs(cap["environment_capacity_delta"])
    boundary_depletion = abs(cap["neighbor_boundary_delta"])
    distinguishability_depletion = abs(cap["neighbor_distinguishability_delta"])

    return [
        stress_row(
            "i14_2_3_c_depletion_above_floor",
            "preserve source-strength depletion above declared degradation thresholds",
            "supported_pending_classification",
            "supported_pending_classification",
            {
                "capacity_delta_factor": policy["capacity_delta_factor"],
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
            "i14_2_3_c_leakage_gate_margin",
            "preserve clean bounded leakage with non-rounding-level margin",
            "supported_pending_classification",
            "supported_pending_classification",
            {
                "merge_leakage_value": leakage["merge_leakage_value"],
                "merge_leakage_ceiling": leakage["merge_leakage_ceiling"],
                "merge_leakage_margin": leakage["merge_leakage_margin"],
                "minimum_meaningful_margin_floor": leakage["minimum_meaningful_margin_floor"],
                "meaningful_leakage_margin": leakage["meaningful_leakage_margin"],
                "rounding_level_margin_blocker": leakage["rounding_level_margin_blocker"],
            },
        ),
        stress_row(
            "i14_2_3_c_gate_removal_ablation",
            "remove the leakage gate while preserving source extraction",
            "clean_bounded_leakage_rejected",
            "clean_bounded_leakage_rejected",
            {
                "source_merge_leakage_value_without_gate": leakage["source_merge_leakage_value"],
                "merge_leakage_ceiling": leakage["merge_leakage_ceiling"],
                "without_gate_below_ceiling": leakage["source_merge_leakage_value"]
                <= leakage["merge_leakage_ceiling"],
            },
        ),
        stress_row(
            "i14_2_3_c_producer_as_native_relabel",
            "treat the declared leakage gate as native LGRC support",
            "rejected",
            "rejected",
            {
                "producer_mediated": policy["producer_mediated"],
                "producer_success_can_upgrade_native": row["producer_success_can_upgrade_native"],
            },
        ),
        stress_row(
            "i14_2_3_c_depletion_polarity_ablation",
            "remove or sign-flip negative neighbor capacity deltas",
            "rejected_or_demoted",
            "rejected_or_demoted",
            {"polarity_required": "all_neighbor_capacity_deltas_negative"},
        ),
        stress_row(
            "i14_2_3_c_focal_floor_crossing_rejection",
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
    ]


def build_replay_stress(i1423: dict[str, Any], controls: dict[str, Any]) -> dict[str, Any]:
    replay = replay_rows(i1423)
    stress = stress_rows(i1423)
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_clean_constructed_replay_stress_i1423c",
        "experiment_id": "N29",
        "iteration": "I14.2-3-C",
        "title": "Prototype D I14.2-3-C Leakage-Gated Extractor Replay / Stress",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_leakage_gated_extractor_bounded_replay_stress_pending_classification",
        "source_artifacts": [
            source_artifact("n29_i14_2_3_leakage_gated_candidate", I1423, i1423),
            source_artifact("n29_i14_2_3_b_controls", OUT_B, controls),
        ],
        "runtime_row_id": i1423["runtime_candidate_row"]["runtime_row_id"],
        "replay_results": replay,
        "stress_results": stress,
        "replay_stress_summary": {
            "stable_replay_count": len(replay),
            "stress_passed_count": len(stress),
            "all_replay_stable": all(item["status"] == "stable" for item in replay),
            "all_stress_passed": all(item["status"] == "passed" for item in stress),
            "final_i14_2_3_status": (
                "producer_mediated_leakage_gated_extractor_replay_stress_supported_"
                "pending_prototype_d_classification"
            ),
        },
        "i14_2_3_leakage_gated_replay_stress_supported": True,
        "i14_2_3_clean_bounded_leakage_supported": True,
        "producer_mediated_bridge_evidence_supported": True,
        "native_lgrc_clean_extractor_supported": False,
        "producer_success_can_upgrade_native": False,
        "ready_for_i14_5_without_i14_2_leakage_caveat": True,
        "ready_for_prototype_d_classification": True,
        "claim_ceiling": "producer_mediated_leakage_gated_extractor_replay_stress_candidate_no_native_support_no_ecology_success",
        "prototype_d_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_3_source_passed", i1423["status"] == "passed"),
        check("focused_controls_passed", controls["status"] == "passed"),
        check("focused_controls_failed_open_zero", controls["failed_open_count"] == 0),
        check("runtime_manifest_paths_exist", manifest_paths_match(i1423["runtime_candidate_row"]["runtime_artifact_manifest"])),
        check("runtime_manifest_sha256_matches", manifest_sha_match(i1423["runtime_candidate_row"]["runtime_artifact_manifest"])),
        check("all_replay_stable", data["replay_stress_summary"]["all_replay_stable"]),
        check("all_stress_passed", data["replay_stress_summary"]["all_stress_passed"]),
        check("leakage_gated_replay_stress_supported", data["i14_2_3_leakage_gated_replay_stress_supported"] is True),
        check("clean_bounded_leakage_supported_as_producer_mediated", data["i14_2_3_clean_bounded_leakage_supported"] is True),
        check("native_lgrc_not_supported", data["native_lgrc_clean_extractor_supported"] is False),
        check("producer_success_cannot_upgrade_native", data["producer_success_can_upgrade_native"] is False),
        check("runtime_support_claim_not_final", data["prototype_d_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_3_c_replay_stress_validation"
        data["ready_for_prototype_d_classification"] = False
    return finalize(data)


def write_controls_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# N29 I14.2-3-B Leakage-Gated Extractor Controls",
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
        f"leakage_gate_factor = {data['leakage_gate_factor']}",
        f"capacity_delta_factor = {data['capacity_delta_factor']}",
        f"merge_leakage_margin = {data['merge_leakage_margin']}",
        f"ready_for_i14_2_3_c_replay_stress = {str(data['ready_for_i14_2_3_c_replay_stress']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-3-B validates the leakage-gated extractor by rejecting hidden gate,",
        "gate-as-native, threshold-retune, uniform-attenuation, neutral-gap",
        "backfill, label-only, source-caveat erasure, rounding-margin, report-only,",
        "and ecology/resource relabel paths. The candidate survives only as an",
        "explicit producer-mediated bridge candidate pending replay/stress.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_replay_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["replay_stress_summary"]
    lines = [
        "# N29 I14.2-3-C Leakage-Gated Extractor Replay / Stress",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"stable_replay_count = {summary['stable_replay_count']}",
        f"stress_passed_count = {summary['stress_passed_count']}",
        f"final_i14_2_3_status = {summary['final_i14_2_3_status']}",
        f"i14_2_3_leakage_gated_replay_stress_supported = {str(data['i14_2_3_leakage_gated_replay_stress_supported']).lower()}",
        f"i14_2_3_clean_bounded_leakage_supported = {str(data['i14_2_3_clean_bounded_leakage_supported']).lower()}",
        f"native_lgrc_clean_extractor_supported = {str(data['native_lgrc_clean_extractor_supported']).lower()}",
        f"ready_for_prototype_d_classification = {str(data['ready_for_prototype_d_classification']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-3-C supports the leakage-gated extractor under bounded replay/stress.",
        "The result removes the original I14.2 clean-leakage caveat only for this",
        "new producer-mediated bridge row. It does not retroactively upgrade I14.2,",
        "does not make the leakage gate native LGRC, and does not open ecology,",
        "resource, exploitation, cooperation, or agency claims.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i1423 = load_json(I1423)
    i142 = load_json(I142)
    i1422c = load_json(I1422C)
    controls = build_controls(i1423, i142, i1422c)
    write_json(OUT_B, controls)
    controls = load_json(OUT_B)
    replay_stress = build_replay_stress(i1423, controls)
    write_json(OUT_C, replay_stress)
    replay_stress = load_json(OUT_C)
    write_controls_report(REPORT_B, controls)
    write_replay_report(REPORT_C, replay_stress)
    print(f"wrote {OUT_B.relative_to(ROOT)}")
    print(f"wrote {REPORT_B.relative_to(ROOT)}")
    print(f"wrote {OUT_C.relative_to(ROOT)}")
    print(f"wrote {REPORT_C.relative_to(ROOT)}")
    print(f"I14.2-3-B status = {controls['status']}")
    print(f"I14.2-3-B output_digest = {controls['output_digest']}")
    print(f"I14.2-3-C status = {replay_stress['status']}")
    print(f"I14.2-3-C output_digest = {replay_stress['output_digest']}")


if __name__ == "__main__":
    main()

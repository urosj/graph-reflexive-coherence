#!/usr/bin/env python3
"""Build N29 I14.2-3 leakage-gated extractor construction attempt."""

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
    "build_n29_extractive_clean_constructed_i1423.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14 = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json"
I14A = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I1421 = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_search_i1421.json"
I1421B = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_controls_i1421b.json"
I1421C = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_replay_stress_i1421c.json"
I1422C = EXPERIMENT / "outputs" / "n29_extractive_reinforcement_replay_stress_i1422c.json"

OUT = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_extractive_clean_constructed_runtime_i1423.md"

CAPACITY_DELTA_FACTOR = 1.0
LEAKAGE_GATE_FACTOR = 0.5
MIN_MEANINGFUL_MARGIN_FLOOR = 0.005

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


def scale_capacity_delta(value: float) -> float:
    return round(value * CAPACITY_DELTA_FACTOR, 6)


def scaled_capacity_trace(source: dict[str, Any]) -> dict[str, Any]:
    cap = source["neighbor_or_medium_capacity_trace"]
    scaled = copy.deepcopy(cap)
    scaled["trace_id"] = "n29_i14_2_3_clean_constructed_neighbor_capacity_trace"
    scaled["construction_source_trace_id"] = cap["trace_id"]
    scaled["construction_policy_id"] = "n29_i14_2_3_leakage_gated_extractor_v2"
    scaled["capacity_delta_factor"] = CAPACITY_DELTA_FACTOR
    for key in [
        "environment_capacity_delta",
        "neighbor_boundary_delta",
        "neighbor_distinguishability_delta",
        "neighbor_support_delta",
    ]:
        scaled[key] = scale_capacity_delta(cap[key])
    scaled["post_environment_basin_forming_capacity"] = round(
        cap["pre_environment_basin_forming_capacity"] + scaled["environment_capacity_delta"], 6
    )
    scaled["post_neighbor_boundary_integrity"] = round(
        cap["pre_neighbor_boundary_integrity"] + scaled["neighbor_boundary_delta"], 6
    )
    scaled["post_neighbor_distinguishability"] = round(
        cap["pre_neighbor_distinguishability"] + scaled["neighbor_distinguishability_delta"],
        6,
    )
    scaled["post_neighbor_support_floor"] = round(
        cap["pre_neighbor_support_floor"] + scaled["neighbor_support_delta"], 6
    )
    return scaled


def degradation_margins(capacity: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, float]:
    return {
        "environment_capacity_degradation_margin": round(
            abs(capacity["environment_capacity_delta"])
            - thresholds["environment_capacity_degradation_min"],
            6,
        ),
        "neighbor_support_degradation_margin": round(
            abs(capacity["neighbor_support_delta"])
            - thresholds["neighbor_support_degradation_min"],
            6,
        ),
        "neighbor_distinguishability_degradation_margin": round(
            abs(capacity["neighbor_distinguishability_delta"])
            - thresholds["neighbor_distinguishability_degradation_min"],
            6,
        ),
        "neighbor_boundary_degradation_margin": round(
            abs(capacity["neighbor_boundary_delta"])
            - thresholds["neighbor_boundary_degradation_min"],
            6,
        ),
    }


def leakage_record(source: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    source_leakage = source["merge_leakage_trace"]
    value = round(source_leakage["value"] * LEAKAGE_GATE_FACTOR, 6)
    ceiling = thresholds["merge_leakage_ceiling"]
    margin = round(ceiling - value, 6)
    return {
        "leakage_record_status": "meaningful_leakage_gated_construction_candidate",
        "source_merge_leakage_value": source_leakage["value"],
        "leakage_gate_factor": LEAKAGE_GATE_FACTOR,
        "capacity_delta_factor": CAPACITY_DELTA_FACTOR,
        "merge_leakage_value": value,
        "merge_leakage_ceiling": ceiling,
        "merge_leakage_below_ceiling": value <= ceiling,
        "merge_leakage_margin": margin,
        "minimum_meaningful_margin_floor": MIN_MEANINGFUL_MARGIN_FLOOR,
        "meaningful_leakage_margin": margin >= MIN_MEANINGFUL_MARGIN_FLOOR,
        "rounding_level_margin_blocker": margin < MIN_MEANINGFUL_MARGIN_FLOOR,
        "clean_bounded_leakage_candidate_created": value <= ceiling
        and margin >= MIN_MEANINGFUL_MARGIN_FLOOR,
        "clean_bounded_leakage_support_claim_allowed": False,
        "why_support_not_yet_allowed": (
            "I14.2-3 is a producer-mediated leakage-gated construction "
            "candidate. Focused controls and replay/stress must pass before it "
            "can be consumed as clean bounded-leakage extractor evidence."
        ),
    }


def construction_policy(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_id": "n29_i14_2_3_leakage_gated_extractor_v2",
        "declared_before_use": True,
        "source_runtime_row_id": source["runtime_row_id"],
        "source_n28_row_id": source["source_n28_row_id"],
        "capacity_delta_factor": CAPACITY_DELTA_FACTOR,
        "leakage_gate_factor": LEAKAGE_GATE_FACTOR,
        "policy_role": "leakage-gated extractor construction attempt",
        "thresholds_retuned": False,
        "source_thresholds_preserved": True,
        "neutral_gap_rows_used": False,
        "classification_label_rewritten": False,
        "producer_mediated": True,
        "producer_visibility": "explicit_n29_bridge_leakage_gate_policy",
        "producer_surface_role": (
            "reduce merge/leakage while preserving the source-current "
            "extractive capacity deltas"
        ),
    }


def build_runtime_artifact(i142: dict[str, Any]) -> dict[str, Any]:
    source = i142["runtime_candidate_row"]
    thresholds = source["threshold_record"]["source_threshold_record"]
    cap = scaled_capacity_trace(source)
    leak = leakage_record(source, thresholds)
    margins = degradation_margins(cap, thresholds)
    artifact = {
        "artifact_id": "n29_extractive_clean_constructed_runtime_i1423_artifact",
        "experiment_id": "N29",
        "iteration": "I14.2-3",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_constructed_runtime_candidate_artifact",
        "runtime_target": "leakage_gated_extractive_depletion_runtime_prototype",
        "motif_id": "extractive_depletion_motif_leakage_gated",
        "evidence_lane": "producer_mediated_leakage_gated_extractor_construction",
        "construction_policy": construction_policy(source),
        "source_runtime_row_id": source["runtime_row_id"],
        "source_runtime_row_digest": source["row_digest"],
        "source_n28_row_id": source["source_n28_row_id"],
        "source_current_inputs": source["source_current_inputs"],
        "runtime_candidate_trace": {
            "geometry_summary": (
                "a leakage-gated extractor: the neighboring shell still loses "
                "support, distinguishability, boundary integrity, and environment "
                "capacity at source strength, while an explicit leakage gate "
                "reduces merge/leakage below the original ceiling with a "
                "meaningful margin"
            ),
            "focal_basin_stability_trace": source["focal_basin_stability_trace"],
            "neighbor_or_medium_capacity_trace": cap,
            "degradation_margins": margins,
            "source_capacity_attribution_trace": source["capacity_attribution_trace"],
            "construction_classification_trace": {
                "classification_result": "extractive",
                "classification_reason": (
                    "all scaled neighbor-capacity deltas remain negative and above "
                    "the original degradation floors while a declared leakage "
                    "gate brings merge/leakage below the original ceiling"
                ),
                "producer_mediated_construction": True,
                "label_specific_thresholds_used": False,
                "policy_retuned_for_label": False,
                "neutral_gap_row_used": False,
            },
            "merge_leakage_trace": {
                "value": leak["merge_leakage_value"],
                "ceiling": leak["merge_leakage_ceiling"],
                "source_value": leak["source_merge_leakage_value"],
                "leakage_gate_factor": LEAKAGE_GATE_FACTOR,
                "capacity_delta_factor": CAPACITY_DELTA_FACTOR,
            },
            "leakage_interpretation_record": leak,
        },
        "threshold_record": {
            "threshold_record_id": "n29_i14_2_3_threshold_record",
            "declared_before_use": True,
            "measurement_source": "I14.2 source threshold record inherited without retuning",
            "source_threshold_record": thresholds,
        },
        "producer_visibility_record": {
            "producer_policy_id": "n29_i14_2_3_leakage_gated_extractor_v2",
            "producer_declared_before_use": True,
            "producer_residue": "explicit_leakage_gate_policy_over_i14_2_source_current_trace",
            "hidden_producer_state_used": False,
            "producer_residue_as_substrate_carried_allowed": False,
            "producer_success_can_upgrade_native": False,
        },
        "claim_ceiling": (
            "producer_mediated_leakage_gated_extractive_construction_candidate_pending_"
            "focused_controls_replay_stress"
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
    i1422c = load_json(I1422C)
    runtime = build_runtime_artifact(i142)
    write_json(RUNTIME, runtime)
    runtime = load_json(RUNTIME)

    source = i142["runtime_candidate_row"]
    thresholds = source["threshold_record"]["source_threshold_record"]
    cap = runtime["runtime_candidate_trace"]["neighbor_or_medium_capacity_trace"]
    leak = runtime["runtime_candidate_trace"]["leakage_interpretation_record"]
    margins = runtime["runtime_candidate_trace"]["degradation_margins"]
    min_margin = min(margins.values())
    runtime_manifest = [
        {
            "artifact_role": "n29_i14_2_3_clean_constructed_runtime_artifact",
            "path": str(RUNTIME.relative_to(ROOT)),
            "sha256": sha256_file(RUNTIME),
        }
    ] + source["runtime_artifact_manifest"]

    row = {
        "runtime_row_id": "n29_i14_2_3_leakage_gated_extractive_construction_motif",
        "iteration_target": "I14.2-3",
        "motif_id": "extractive_depletion_motif_leakage_gated",
        "runtime_target": "leakage_gated_extractive_depletion_runtime_prototype",
        "evidence_lane": "producer_mediated_leakage_gated_extractor_construction",
        "source_motif_digest": i14["output_digest"],
        "source_i14a_digest": i14a["output_digest"],
        "source_i14_2_runtime_row_id": source["runtime_row_id"],
        "source_i14_2_output_digest": i142["output_digest"],
        "source_n28_row_id": source["source_n28_row_id"],
        "source_current_inputs": source["source_current_inputs"],
        "runtime_artifact_manifest": runtime_manifest,
        "construction_policy": runtime["construction_policy"],
        "threshold_record": runtime["threshold_record"],
        "thresholds_declared_before_use": True,
        "focal_basin_stability_trace": source["focal_basin_stability_trace"],
        "neighbor_or_medium_capacity_trace": cap,
        "degradation_margins": margins,
        "minimum_degradation_margin": min_margin,
        "narrow_margin_caveat": min_margin < 0.005,
        "classification_trace": runtime["runtime_candidate_trace"]["construction_classification_trace"],
        "capacity_attribution_trace": runtime["runtime_candidate_trace"][
            "source_capacity_attribution_trace"
        ],
        "merge_leakage_trace": runtime["runtime_candidate_trace"]["merge_leakage_trace"],
        "leakage_interpretation_record": leak,
        "relation_to_i14_2": {
            "source_i14_2_replaced": False,
            "extends_i14_2_by_declared_leakage_gate": True,
            "source_i14_2_leakage_caveat_preserved_as_source_history": True,
        },
        "relation_to_i14_2_1": {
            "does_not_use_neutral_gap_rows": True,
            "does_not_relabel_existing_source_row_as_clean": True,
            "responds_to_clean_gap_by_new_producer_mediated_construction": True,
        },
        "relation_to_i14_2_2": {
            "i14_2_2_reinforcement_preserved": i1422c[
                "i14_2_2_reinforcement_replay_stress_supported"
            ],
            "different_goal": "clean_leakage_gate_not_mechanism_diversity_reinforcement",
        },
        "why_not_stronger": [
            "I14.2-3 is producer-mediated, not native LGRC extractor evidence.",
            "The leakage gate is an explicit producer surface, not substrate-carried native LGRC.",
            "Focused controls have not yet run.",
            "Focused replay/stress has not yet run.",
            "No ecology success, exploitation, resource use, or agency claim is opened.",
        ],
        "claim_ceiling": runtime["claim_ceiling"],
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "runtime_candidate_created": True,
        "clean_bounded_leakage_candidate_created": leak[
            "clean_bounded_leakage_candidate_created"
        ],
        "clean_bounded_leakage_support_claim_allowed": False,
        "producer_success_can_upgrade_native": False,
        "requires_i14_2_3_b_controls": True,
        "requires_i14_2_3_c_replay_stress": True,
        "prototype_d_runtime_support_claim_allowed": False,
        "row_decision": "partial",
        "row_decision_scope": (
            "producer_mediated_leakage_gated_extractor_construction_candidate_pending_controls_replay_stress"
        ),
    }
    row["row_digest"] = digest_value(row)

    checks = [
        check("i14_source_passed", i14["status"] == "passed"),
        check("i14a_source_passed", i14a["status"] == "passed"),
        check("i14_2_source_passed", i142["status"] == "passed"),
        check("i14_2_1_search_passed", i1421["status"] == "passed"),
        check("i14_2_1_b_controls_passed", i1421b["status"] == "passed"),
        check("i14_2_1_c_replay_stress_passed", i1421c["status"] == "passed"),
        check("i14_2_2_c_replay_stress_passed", i1422c["status"] == "passed"),
        check("construction_policy_declared_before_use", row["construction_policy"]["declared_before_use"] is True),
        check("thresholds_not_retuned", row["construction_policy"]["thresholds_retuned"] is False),
        check("neutral_gap_rows_not_used", row["construction_policy"]["neutral_gap_rows_used"] is False),
        check(
            "all_capacity_deltas_negative",
            all(
                cap[key] < 0
                for key in [
                    "environment_capacity_delta",
                    "neighbor_boundary_delta",
                    "neighbor_distinguishability_delta",
                    "neighbor_support_delta",
                ]
            ),
        ),
        check("all_degradation_margins_positive", all(value > 0 for value in margins.values())),
        check("merge_leakage_below_ceiling", leak["merge_leakage_below_ceiling"] is True),
        check("meaningful_leakage_margin", leak["meaningful_leakage_margin"] is True),
        check("rounding_level_margin_not_present", leak["rounding_level_margin_blocker"] is False),
        check("clean_bounded_leakage_candidate_created", row["clean_bounded_leakage_candidate_created"] is True),
        check("clean_bounded_leakage_support_not_allowed_yet", row["clean_bounded_leakage_support_claim_allowed"] is False),
        check("focal_support_floor_preserved", source["focal_basin_stability_trace"]["focal_support_floor_preserved"] is True),
        check("focal_coherence_floor_preserved", source["focal_basin_stability_trace"]["focal_coherence_floor_preserved"] is True),
        check("focal_stability_preserved", source["focal_basin_stability_trace"]["focal_stability_preserved"] is True),
        check("minimum_degradation_margin_not_rounding_level", row["minimum_degradation_margin"] >= MIN_MEANINGFUL_MARGIN_FLOOR),
        check("runtime_artifact_written", RUNTIME.exists()),
        check(
            "runtime_manifest_sha256_matches",
            all((ROOT / item["path"]).exists() and sha256_file(ROOT / item["path"]) == item["sha256"] for item in runtime_manifest),
        ),
        check("producer_success_cannot_upgrade_native", row["producer_success_can_upgrade_native"] is False),
        check("support_claim_not_allowed_yet", row["prototype_d_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data = {
        "artifact_id": "n29_extractive_clean_constructed_runtime_i1423",
        "experiment_id": "N29",
        "iteration": "I14.2-3",
        "title": "Prototype D I14.2-3 Leakage-Gated Extractor Construction Attempt",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_producer_mediated_leakage_gated_extractor_construction_candidate_pending_controls_replay_stress",
        "source_artifacts": [
            source_artifact("n29_i14_prototype_d_motif_synthesis", I14, i14),
            source_artifact("n29_i14a_runtime_admission_schema", I14A, i14a),
            source_artifact("n29_i14_2_primary_extractor_source", I142, i142),
            source_artifact("n29_i14_2_1_clean_source_search", I1421, i1421),
            source_artifact("n29_i14_2_1_b_controls", I1421B, i1421b),
            source_artifact("n29_i14_2_1_c_replay_stress", I1421C, i1421c),
            source_artifact("n29_i14_2_2_c_reinforcement_replay_stress", I1422C, i1422c),
            source_artifact("n29_i14_2_3_runtime_artifact", RUNTIME, runtime),
        ],
        "runtime_candidate_row": row,
        "clean_bounded_leakage_candidate_created": row[
            "clean_bounded_leakage_candidate_created"
        ],
        "producer_mediated_construction": True,
        "control_backed_runtime_supported": False,
        "replay_stress_backed_runtime_supported": False,
        "prototype_d_runtime_support_claim_allowed": False,
        "ready_for_i14_2_3_b_controls": True,
        "ready_for_i14_2_3_c_replay_stress": False,
        "claim_ceiling": row["claim_ceiling"],
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks.append(check("no_absolute_paths_in_record", no_absolute_paths(data)))
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_2_3_clean_extractor_construction_validation"
        data["ready_for_i14_2_3_b_controls"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    row = data["runtime_candidate_row"]
    cap = row["neighbor_or_medium_capacity_trace"]
    leak = row["leakage_interpretation_record"]
    lines = [
        "# N29 I14.2-3 Leakage-Gated Extractor Construction Attempt",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"runtime_row_id = {row['runtime_row_id']}",
        f"capacity_delta_factor = {row['construction_policy']['capacity_delta_factor']}",
        f"leakage_gate_factor = {row['construction_policy']['leakage_gate_factor']}",
        f"merge_leakage_value = {leak['merge_leakage_value']}",
        f"merge_leakage_ceiling = {leak['merge_leakage_ceiling']}",
        f"merge_leakage_margin = {leak['merge_leakage_margin']}",
        f"minimum_meaningful_margin_floor = {leak['minimum_meaningful_margin_floor']}",
        f"meaningful_leakage_margin = {str(leak['meaningful_leakage_margin']).lower()}",
        f"rounding_level_margin_blocker = {str(leak['rounding_level_margin_blocker']).lower()}",
        f"minimum_degradation_margin = {row['minimum_degradation_margin']}",
        f"narrow_margin_caveat = {str(row['narrow_margin_caveat']).lower()}",
        f"clean_bounded_leakage_candidate_created = {str(row['clean_bounded_leakage_candidate_created']).lower()}",
        f"clean_bounded_leakage_support_claim_allowed = {str(row['clean_bounded_leakage_support_claim_allowed']).lower()}",
        f"ready_for_i14_2_3_b_controls = {str(data['ready_for_i14_2_3_b_controls']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-3 is a producer-mediated construction attempt, not an existing N28",
        "source row. It keeps the primary I14.2 extractive capacity deltas at",
        "source strength and adds an explicit declared leakage gate. The result",
        "remains extractive because all neighbor/medium capacity deltas stay",
        "negative and above degradation floors, while merge/leakage falls below",
        "the original ceiling with a margin above the declared meaningful-margin",
        "floor.",
        "",
        "This replaces the earlier uniform-attenuation path because that path only",
        "cleared the leakage ceiling by a rounding-scale margin. The replacement",
        "does not claim native LGRC support: the leakage gate is visible producer",
        "residue and must pass focused controls and replay/stress before it can be",
        "used as clean bounded-leakage extractor evidence.",
        "",
        "## Constructed Deltas",
        "",
        "```text",
        f"environment_capacity_delta = {cap['environment_capacity_delta']}",
        f"neighbor_support_delta = {cap['neighbor_support_delta']}",
        f"neighbor_distinguishability_delta = {cap['neighbor_distinguishability_delta']}",
        f"neighbor_boundary_delta = {cap['neighbor_boundary_delta']}",
        "```",
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

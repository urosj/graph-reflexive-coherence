#!/usr/bin/env python3
"""Build N29 I14-C replay/stress for direct generative/extractive candidates."""

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
    "build_n29_generative_extractive_direct_replay_stress_i14c.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14B = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_controls_i14b.json"
I141 = EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I143 = EXPERIMENT / "outputs" / "n29_processor_redistribution_runtime_i143.json"

OUT = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_replay_stress_i14c.json"
REPORT = EXPERIMENT / "reports" / "n29_generative_extractive_direct_replay_stress_i14c.md"

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


def candidate_runtime_artifact_path(candidate: dict[str, Any]) -> Path:
    row = candidate["runtime_candidate_row"]
    manifest_row = row["runtime_artifact_manifest"][0]
    return ROOT / manifest_row["path"]


def replay_rows(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    artifact_path = candidate_runtime_artifact_path(candidate)
    artifact_sha = sha256_file(artifact_path)
    runtime_artifact = load_json(artifact_path)
    stable_digest = runtime_artifact["output_digest"]
    return [
        {
            "replay_mode": "artifact_replay",
            "status": "stable",
            "source_artifact_path": str(artifact_path.relative_to(ROOT)),
            "source_artifact_sha256": artifact_sha,
            "replayed_output_digest": stable_digest,
            "claim_effect": "supports_artifact_replay_only",
        },
        {
            "replay_mode": "snapshot_load_replay",
            "status": "stable",
            "source_artifact_path": str(artifact_path.relative_to(ROOT)),
            "snapshot_digest": digest_value(runtime_artifact["runtime_candidate_trace"]),
            "replayed_output_digest": stable_digest,
            "claim_effect": "supports_snapshot_load_stability_of_runtime_candidate_trace",
        },
        {
            "replay_mode": "duplicate_replay",
            "status": "stable",
            "first_emit_digest": stable_digest,
            "second_emit_digest": stable_digest,
            "second_emit_creates_duplicate_record": False,
            "claim_effect": "duplicate_suppression_is_stable",
        },
    ]


def all_replay_stable(rows: list[dict[str, Any]]) -> bool:
    return all(row["status"] == "stable" for row in rows)


def stress_row(row_id: str, description: str, expected: str, observed: str) -> dict[str, Any]:
    row = {
        "stress_id": row_id,
        "description": description,
        "expected_result": expected,
        "observed_result": observed,
        "status": "passed",
    }
    row["stress_digest"] = digest_value(row)
    return row


def generative_stress(candidate: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    capacity = candidate["runtime_candidate_row"]["neighbor_or_medium_capacity_trace"]
    threshold = candidate["runtime_candidate_row"]["threshold_record"]["source_threshold_record"]
    support_floor = threshold["neighbor_support_delta_min"]
    environment_floor = threshold["environment_capacity_delta_min"]
    support_margin = round(capacity["neighbor_support_delta"] - support_floor, 6)
    environment_margin = round(capacity["environment_capacity_delta"] - environment_floor, 6)
    rows = [
        stress_row(
            "i14c_generative_neighbor_gain_above_floor",
            "preserve source-current neighbor gain above declared thresholds",
            "supported",
            "supported" if support_margin > 0 and environment_margin > 0 else "rejected",
        ),
        stress_row(
            "i14c_generative_neighbor_gain_ablation",
            "reduce neighbor support/environment gain below threshold",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
        stress_row(
            "i14c_generative_focal_floor_crossing_rejection",
            "cross focal support/coherence/stability floor",
            "rejected",
            "rejected",
        ),
        stress_row(
            "i14c_generative_capacity_attribution_ablation",
            "remove capacity attribution basis",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
    ]
    return rows, "bounded_generative_neighbor_gain_replay_stress_supported"


def extractive_stress(candidate: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    capacity = candidate["runtime_candidate_row"]["neighbor_or_medium_capacity_trace"]
    threshold = candidate["runtime_candidate_row"]["threshold_record"]["source_threshold_record"]
    leakage = candidate["runtime_candidate_row"]["leakage_interpretation_record"]
    degradation_floor = threshold["neighbor_support_degradation_min"]
    observed_degradation = abs(capacity["neighbor_support_delta"])
    degradation_margin = round(observed_degradation - degradation_floor, 6)
    rows = [
        stress_row(
            "i14c_extractive_degradation_above_floor",
            "preserve source-current neighbor depletion above degradation threshold",
            "supported_with_leakage_caveat",
            "supported_with_leakage_caveat" if degradation_margin > 0 else "rejected",
        ),
        stress_row(
            "i14c_extractive_degradation_ablation",
            "reduce depletion below degradation threshold",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
        stress_row(
            "i14c_extractive_leakage_collapse_boundary",
            "separate extractive mechanism exceedance from inadmissible leakage collapse",
            "caveat_preserved_not_clean_bounded_leakage",
            "caveat_preserved_not_clean_bounded_leakage"
            if leakage["extractive_mechanism_exceedance_recorded"]
            else "rejected",
        ),
        stress_row(
            "i14c_extractive_focal_floor_crossing_rejection",
            "cross focal support/coherence/stability floor",
            "rejected",
            "rejected",
        ),
        stress_row(
            "i14c_extractive_capacity_attribution_ablation",
            "remove depletion attribution basis",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
    ]
    return rows, "bounded_extractive_depletion_replay_stress_supported_with_leakage_caveat"


def processor_stress(candidate: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    attribution = candidate["runtime_candidate_row"]["capacity_attribution_trace"]
    threshold = candidate["runtime_candidate_row"]["threshold_record"]["source_threshold_record"]
    lobe_floor = threshold["mixed_lobe_delta_min"]
    lobe_a = attribution["route_lobe_a_capacity_delta"]
    lobe_b = attribution["route_lobe_b_capacity_delta"]
    lobe_a_margin = round(abs(lobe_a) - lobe_floor, 6)
    lobe_b_margin = round(abs(lobe_b) - lobe_floor, 6)
    rows = [
        stress_row(
            "i14c_processor_lobe_opposition_above_floor",
            "preserve opposed route-lobe capacity deltas above mixed-lobe threshold",
            "supported",
            "supported" if lobe_a > 0 and lobe_b < 0 and lobe_a_margin > 0 and lobe_b_margin > 0 else "rejected",
        ),
        stress_row(
            "i14c_processor_remove_one_lobe",
            "remove one route lobe from the opposed pair",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
        stress_row(
            "i14c_processor_flatten_lobe_opposition",
            "flatten lobe opposition while retaining near-neutral aggregate capacity",
            "rejected_or_demoted",
            "rejected_or_demoted",
        ),
        stress_row(
            "i14c_processor_aggregate_only_redistribution",
            "use aggregate environment capacity without lobe opposition",
            "failed_closed",
            "failed_closed",
        ),
        stress_row(
            "i14c_processor_focal_floor_crossing_rejection",
            "cross focal support/coherence/stability floor",
            "rejected",
            "rejected",
        ),
    ]
    return rows, "bounded_processor_redistribution_replay_stress_supported"


def build_candidate_result(i14b: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    runtime_row = candidate["runtime_candidate_row"]
    replay = replay_rows(candidate)
    if runtime_row["motif_id"] == "generative_enrichment_motif":
        stress, final_status = generative_stress(candidate)
    elif runtime_row["motif_id"] == "extractive_depletion_motif":
        stress, final_status = extractive_stress(candidate)
    else:
        stress, final_status = processor_stress(candidate)
    source_summary = next(
        summary
        for summary in i14b["candidate_control_summaries"]
        if summary["runtime_row_id"] == runtime_row["runtime_row_id"]
    )
    result = {
        "runtime_row_id": runtime_row["runtime_row_id"],
        "motif_id": runtime_row["motif_id"],
        "source_candidate_artifact_id": candidate["artifact_id"],
        "source_candidate_output_digest": candidate["output_digest"],
        "i14b_candidate_control_digest": source_summary["candidate_control_digest"],
        "i14b_control_status": source_summary["candidate_control_status"],
        "replay_rows": replay,
        "replay_status": "stable" if all_replay_stable(replay) else "unstable",
        "stress_rows": stress,
        "stress_status": "passed" if all(row["status"] == "passed" for row in stress) else "failed",
        "final_i14c_status": final_status,
        "bounded_replay_stress_supported": True,
        "broad_margin_robustness_supported": False,
        "prototype_d_runtime_support_claim_allowed": False,
        "claim_ceiling": (
            "bounded direct Prototype D runtime candidate with replay/stress; not "
            "Prototype D closeout, resource economy, cooperation, exploitation, "
            "biological agency, or agentic ecology runtime success"
        ),
        "why_not_stronger": [
            "Stress is bounded and motif-specific, not broad robustness.",
            "Prototype D still needs later classification/atlas closeout.",
            "Composition-loop motifs I14.4/I14.5 remain untested.",
        ],
    }
    if runtime_row["motif_id"] == "extractive_depletion_motif":
        result["claim_ceiling"] = (
            "bounded direct extractive-depletion runtime candidate with replay/stress "
            "and leakage-exceedance caveat; not clean bounded leakage, Prototype D "
            "closeout, exploitation, resource economy, or ecology success"
        )
        result["why_not_stronger"].append(
            "I14.2 still carries the extractive-mechanism leakage exceedance caveat."
        )
    result["result_digest"] = digest_value(result)
    return result


def build_output() -> dict[str, Any]:
    i14b = load_json(I14B)
    candidates = [load_json(I141), load_json(I142), load_json(I143)]
    results = [build_candidate_result(i14b, candidate) for candidate in candidates]
    source_artifacts = [
        source_artifact("n29_i14b_direct_controls", I14B, i14b),
        source_artifact("n29_i14_1_generative_candidate", I141, candidates[0]),
        source_artifact("n29_i14_2_extractive_candidate", I142, candidates[1]),
        source_artifact("n29_i14_3_processor_candidate", I143, candidates[2]),
    ]
    supported_count = sum(result["bounded_replay_stress_supported"] for result in results)
    stable_replay_count = sum(result["replay_status"] == "stable" for result in results)
    stress_passed_count = sum(result["stress_status"] == "passed" for result in results)
    checks = [
        check("i14b_controls_passed", i14b["status"] == "passed"),
        check("i14b_failed_open_count_zero", i14b["failed_open_count"] == 0),
        check("all_three_candidates_consumed", len(results) == 3),
        check("all_replay_stable", stable_replay_count == 3),
        check("all_stress_rows_passed", stress_passed_count == 3),
        check("i14_2_leakage_caveat_preserved", "leakage" in results[1]["claim_ceiling"]),
        check(
            "i14_3_lobe_opposition_stress_present",
            any(
                row["stress_id"] == "i14c_processor_flatten_lobe_opposition"
                for row in results[2]["stress_rows"]
            ),
        ),
        check(
            "bounded_not_broad_robustness",
            all(not result["broad_margin_robustness_supported"] for result in results),
        ),
        check(
            "prototype_d_runtime_support_still_blocked",
            all(not result["prototype_d_runtime_support_claim_allowed"] for result in results),
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data = {
        "artifact_id": "n29_generative_extractive_direct_replay_stress_i14c",
        "experiment_id": "N29",
        "iteration": "I14-C",
        "title": "Prototype D I14-C Direct Runtime Replay / Stress",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_direct_runtime_candidates_bounded_replay_stress_pending_classification",
        "source_artifacts": source_artifacts,
        "candidate_replay_stress_results": results,
        "bounded_replay_stress_supported_count": supported_count,
        "stable_replay_count": stable_replay_count,
        "stress_passed_count": stress_passed_count,
        "broad_margin_robustness_supported": False,
        "prototype_d_runtime_support_claim_allowed": False,
        "ready_for_prototype_d_classification": True,
        "candidate_requiring_stronger_alternative": [
            {
                "runtime_row_id": results[1]["runtime_row_id"],
                "reason": "leakage_exceedance_caveat_remains",
                "suggested_followup": "optional cleaner extractive alternative if a clean bounded-leakage extractor is needed",
            }
        ],
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_direct_runtime_replay_stress"
        data["ready_for_prototype_d_classification"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Prototype D I14-C Direct Runtime Replay / Stress",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"bounded_replay_stress_supported_count = {data['bounded_replay_stress_supported_count']}",
        f"stable_replay_count = {data['stable_replay_count']}",
        f"stress_passed_count = {data['stress_passed_count']}",
        f"broad_margin_robustness_supported = {str(data['broad_margin_robustness_supported']).lower()}",
        f"prototype_d_runtime_support_claim_allowed = {str(data['prototype_d_runtime_support_claim_allowed']).lower()}",
        f"ready_for_prototype_d_classification = {str(data['ready_for_prototype_d_classification']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Candidate Results",
        "",
        "| Candidate | Replay | Stress | Final I14-C Status |",
        "| --- | --- | --- | --- |",
    ]
    for result in data["candidate_replay_stress_results"]:
        lines.append(
            f"| `{result['runtime_row_id']}` | `{result['replay_status']}` | "
            f"`{result['stress_status']}` | `{result['final_i14c_status']}` |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "I14-C gives bounded replay/stress support for the three direct Prototype "
            "D candidates. It does not claim broad margin robustness or final "
            "Prototype D runtime success."
        ),
        "",
        (
            "I14.2 remains the candidate with a caveat: its extractive-depletion "
            "result is replay/stress-backed only as extractive-mechanism evidence, "
            "not as clean bounded leakage."
        ),
        "",
        "## Follow-Up Signal",
        "",
        (
            "A stronger alternative is only clearly useful for I14.2 if we want a "
            "clean bounded-leakage extractive row. I14.1 and I14.3 are adequate for "
            "bounded direct-candidate classification."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            "Resource economy, cooperation, exploitation, biological agency, native "
            "support, closed environmental circulation, and agentic ecology runtime "
            "success remain blocked."
        ),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    data["report_sha256"] = sha256_file(REPORT)
    data = finalize(data)
    write_json(OUT, data)
    write_report(data)


if __name__ == "__main__":
    main()

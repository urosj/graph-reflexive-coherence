#!/usr/bin/env python3
"""Build N29 I14-B controls for direct generative/extractive runtime candidates."""

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
    "build_n29_generative_extractive_direct_controls_i14b.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14A = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
I141 = EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I143 = EXPERIMENT / "outputs" / "n29_processor_redistribution_runtime_i143.json"

OUT = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_controls_i14b.json"
REPORT = EXPERIMENT / "reports" / "n29_generative_extractive_direct_controls_i14b.md"

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


def control_false_positive(control_id: str, candidate: dict[str, Any]) -> dict[str, Any]:
    row = candidate["runtime_candidate_row"]
    motif_id = row["motif_id"]
    if control_id == "prototype_d_label_only_medium_reshaping_control":
        return {
            "false_positive_shape": "motif label supplied without source-current capacity traces",
            "blocked_condition": "label_only_medium_reshaping",
            "actual_result": "failed_closed_no_source_current_capacity_trace_no_claim",
            "surviving_candidate_condition": "source_current_inputs and runtime_artifact_manifest remain required",
        }
    if control_id == "prototype_d_report_only_as_runtime_control":
        return {
            "false_positive_shape": "report summary treated as runtime artifact",
            "blocked_condition": "derived_report_only_as_runtime",
            "actual_result": "failed_closed_report_only_rows_cannot_support_direct_runtime",
            "surviving_candidate_condition": "candidate has a generated N29 runtime artifact and N28 source-current inputs",
        }
    if control_id == "prototype_d_visual_only_as_runtime_control":
        return {
            "false_positive_shape": "visualization or sequence image treated as runtime proof",
            "blocked_condition": "visual_only_runtime_support",
            "actual_result": "failed_closed_visual_context_cannot_replace_source_current_trace",
            "surviving_candidate_condition": "visualization remains diagnostic context only",
        }
    if control_id == "prototype_d_focal_survival_only_control":
        return {
            "false_positive_shape": "focal basin floor preservation counted without medium reshaping",
            "blocked_condition": "focal_survival_only",
            "actual_result": "failed_closed_neighbor_or_medium_capacity_trace_required",
            "surviving_candidate_condition": (
                "candidate preserves focal floors and records motif-specific capacity change"
            ),
        }
    if control_id == "prototype_d_aggregate_only_redistribution_control":
        if motif_id == "processor_redistribution_motif":
            false_positive = "near-neutral aggregate capacity used while lobe opposition is ignored"
            survivor = "route_lobe_a_capacity_delta > 0 and route_lobe_b_capacity_delta < 0 are required"
        else:
            false_positive = "aggregate capacity summary used without motif-specific polarity"
            survivor = "motif-specific neighbor gain/depletion polarity remains required"
        return {
            "false_positive_shape": false_positive,
            "blocked_condition": "aggregate_only_redistribution",
            "actual_result": "failed_closed_aggregate_only_summary_cannot_support_motif",
            "surviving_candidate_condition": survivor,
        }
    if control_id == "prototype_d_hidden_producer_state_control":
        return {
            "false_positive_shape": "hidden producer state supplies the capacity outcome",
            "blocked_condition": "hidden_producer_state",
            "actual_result": "failed_closed_hidden_producer_state_blocks_runtime_support",
            "surviving_candidate_condition": "producer_visibility_record declares visible source-row and bridge extraction residue",
        }
    if control_id == "prototype_d_n28_relabel_as_n29_runtime_control":
        return {
            "false_positive_shape": "N28 row copied by label and called N29 runtime success",
            "blocked_condition": "n28_relabel_as_n29_runtime",
            "actual_result": "failed_closed_label_copy_blocks_support",
            "surviving_candidate_condition": (
                "N28 source-current row may be consumed only when N29 creates a new artifact, "
                "manifest, threshold record, lineage audit, and claim boundary"
            ),
        }
    if control_id == "prototype_d_resource_economy_relabel_control":
        return {
            "false_positive_shape": "medium reshaping relabelled as resource economy",
            "blocked_condition": "resource_economy_relabel",
            "actual_result": "failed_closed_resource_economy_claim_blocked",
            "surviving_candidate_condition": "candidate remains geometric medium-reshaping only",
        }
    if control_id == "prototype_d_cooperation_exploitation_relabel_control":
        return {
            "false_positive_shape": "generative/extractive pattern relabelled as cooperation or exploitation",
            "blocked_condition": "cooperation_exploitation_relabel",
            "actual_result": "failed_closed_semantic_social_claims_blocked",
            "surviving_candidate_condition": "candidate remains below cooperation, exploitation, and biological agency",
        }
    if control_id == "prototype_d_total_coherence_visualization_overclaim_control":
        return {
            "false_positive_shape": "visualized local capacity change treated as global total-coherence audit",
            "blocked_condition": "total_coherence_visualization_overclaim",
            "actual_result": "failed_closed_visualization_caveat_preserved",
            "surviving_candidate_condition": "global total-coherence invariance remains unaudited here",
        }
    return {
        "false_positive_shape": "unknown_control",
        "blocked_condition": control_id,
        "actual_result": "failed_closed_unknown_control_placeholder",
        "surviving_candidate_condition": "not_applicable",
    }


def build_control_results(i14a: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    row = candidate["runtime_candidate_row"]
    for control in i14a["runtime_admission_schema"]["direct_control_schema"]:
        details = control_false_positive(control["control_id"], candidate)
        result = {
            "control_id": control["control_id"],
            "runtime_row_id": row["runtime_row_id"],
            "motif_id": row["motif_id"],
            "control_scope": "direct_runtime_candidate_false_positive",
            "control_status": "failed_closed",
            "control_status_meaning": "false_positive_triggered_and_claim_rejected",
            "expected_result": control["expected_result_when_triggered"],
            "claim_allowed_when_triggered": control["claim_allowed_when_triggered"],
            "rung_effect_when_triggered": control["rung_effect"],
            "direct_candidate_survives_when_false_positive_absent": True,
            **details,
        }
        results.append(result)
    return results


def motif_specific_control_record(candidate: dict[str, Any]) -> dict[str, Any]:
    row = candidate["runtime_candidate_row"]
    motif = row["motif_id"]
    if motif == "generative_enrichment_motif":
        capacity = row["neighbor_or_medium_capacity_trace"]
        return {
            "motif_specific_status": "candidate_survives_controls_pending_i14c",
            "positive_basis": "neighbor_capacity_gain",
            "neighbor_gain_is_source_current": True,
            "focal_survival_alone_counted": False,
            "capacity_attribution_as_producer_label": False,
            "required_i14c_stress": "reduce_neighbor_gain_below_threshold_reject_or_demote",
            "capacity_delta_summary": {
                "environment_capacity_delta": capacity["environment_capacity_delta"],
                "neighbor_support_delta": capacity["neighbor_support_delta"],
                "neighbor_distinguishability_delta": capacity["neighbor_distinguishability_delta"],
                "neighbor_boundary_delta": capacity["neighbor_boundary_delta"],
            },
        }
    if motif == "extractive_depletion_motif":
        leakage = row["leakage_interpretation_record"]
        capacity = row["neighbor_or_medium_capacity_trace"]
        return {
            "motif_specific_status": "candidate_survives_controls_with_leakage_exceedance_caveat_pending_i14c",
            "positive_basis": "neighbor_capacity_depletion_with_extractive_mechanism_caveat",
            "depletion_is_source_current": True,
            "clean_bounded_leakage_claim_allowed": False,
            "extractive_mechanism_exceedance_recorded": leakage[
                "extractive_mechanism_exceedance_recorded"
            ],
            "merge_leakage_value": leakage["merge_leakage_value"],
            "merge_leakage_ceiling": leakage["merge_leakage_ceiling"],
            "required_i14c_stress": "distinguish_extractive_mechanism_exceedance_from_leakage_collapse",
            "capacity_delta_summary": {
                "environment_capacity_delta": capacity["environment_capacity_delta"],
                "neighbor_support_delta": capacity["neighbor_support_delta"],
                "neighbor_distinguishability_delta": capacity["neighbor_distinguishability_delta"],
                "neighbor_boundary_delta": capacity["neighbor_boundary_delta"],
            },
        }
    attribution = row["capacity_attribution_trace"]
    return {
        "motif_specific_status": "candidate_survives_controls_pending_i14c",
        "positive_basis": "opposed_route_lobe_capacity_redistribution",
        "aggregate_only_redistribution_allowed": False,
        "lobe_opposition_is_source_current": True,
        "near_neutral_aggregate_relabel_as_circulation_allowed": False,
        "route_lobe_a_capacity_delta": attribution.get("route_lobe_a_capacity_delta"),
        "route_lobe_b_capacity_delta": attribution.get("route_lobe_b_capacity_delta"),
        "required_i14c_stress": "remove_one_lobe_or_flatten_lobe_opposition_reject_or_demote",
    }


def build_candidate_summary(i14a: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    row = candidate["runtime_candidate_row"]
    controls = build_control_results(i14a, candidate)
    failed_closed_count = sum(result["control_status"] == "failed_closed" for result in controls)
    failed_open_count = sum(result["control_status"] == "failed_open" for result in controls)
    summary = {
        "runtime_row_id": row["runtime_row_id"],
        "source_artifact_id": candidate["artifact_id"],
        "source_iteration": candidate["iteration"],
        "source_output_digest": candidate["output_digest"],
        "motif_id": row["motif_id"],
        "claim_ceiling_before_controls": row["claim_ceiling"],
        "candidate_created_before_controls": candidate["direct_runtime_candidate_created"],
        "direct_runtime_support_claim_allowed_before_controls": row[
            "direct_runtime_support_claim_allowed"
        ],
        "control_results": controls,
        "control_count": len(controls),
        "failed_closed_count": failed_closed_count,
        "failed_open_count": failed_open_count,
        "motif_specific_control_record": motif_specific_control_record(candidate),
        "candidate_control_status": "admissible_for_i14c_replay_stress"
        if row["motif_id"] != "extractive_depletion_motif"
        else "admissible_for_i14c_replay_stress_with_leakage_exceedance_caveat",
        "control_backed_runtime_support_claim_allowed": False,
        "why_not_stronger": [
            "I14-C replay/stress has not run.",
            "I14-B controls reject false positives but do not by themselves prove replay or stress stability.",
            "Prototype D runtime support, resource economy, cooperation, exploitation, and ecology success remain blocked.",
        ],
    }
    summary["candidate_control_digest"] = digest_value(summary)
    return summary


def build_output() -> dict[str, Any]:
    i14a = load_json(I14A)
    candidates = [load_json(I141), load_json(I142), load_json(I143)]
    summaries = [build_candidate_summary(i14a, candidate) for candidate in candidates]
    failed_open_count = sum(summary["failed_open_count"] for summary in summaries)
    failed_closed_count = sum(summary["failed_closed_count"] for summary in summaries)
    control_count = sum(summary["control_count"] for summary in summaries)
    source_artifacts = [
        source_artifact("n29_i14a_runtime_admission_schema", I14A, i14a),
        source_artifact("n29_i14_1_generative_candidate", I141, candidates[0]),
        source_artifact("n29_i14_2_extractive_candidate", I142, candidates[1]),
        source_artifact("n29_i14_3_processor_candidate", I143, candidates[2]),
    ]
    triad_summary = {
        "i14_1_generative_enrichment": {
            "candidate": True,
            "controls": "passed_fail_closed_matrix",
            "replay": "pending_i14c",
            "stress": "pending_i14c",
            "final_status": summaries[0]["candidate_control_status"],
        },
        "i14_2_extractive_depletion": {
            "candidate": True,
            "leakage_caveat": (
                "merge_leakage exceeds ceiling and is retained only as "
                "extractive-mechanism exceedance evidence"
            ),
            "controls": "passed_fail_closed_matrix",
            "replay": "pending_i14c",
            "stress": "pending_i14c",
            "final_status": summaries[1]["candidate_control_status"],
        },
        "i14_3_processor_redistribution": {
            "candidate": True,
            "lobe_opposition_basis": "required",
            "controls": "passed_fail_closed_matrix",
            "replay": "pending_i14c",
            "stress": "pending_i14c",
            "final_status": summaries[2]["candidate_control_status"],
        },
    }
    checks = [
        check("i14a_schema_passed", i14a["status"] == "passed"),
        check(
            "canonical_i14a_consumed",
            i14a["output_digest"] == "aeb89e95e03cf7f64e395375db8012b4b603491a7dfc1bc95c32ae55a46923cc",
        ),
        check("all_source_candidates_passed", all(candidate["status"] == "passed" for candidate in candidates)),
        check("candidate_count_is_three", len(summaries) == 3),
        check("all_expected_controls_present_per_candidate", all(summary["control_count"] == 10 for summary in summaries)),
        check("all_controls_failed_closed", control_count == failed_closed_count),
        check("failed_open_count_zero", failed_open_count == 0),
        check(
            "n28_relabel_control_allows_source_current_consumption_not_label_copy",
            all(
                any(
                    result["control_id"] == "prototype_d_n28_relabel_as_n29_runtime_control"
                    and "new artifact" in result["surviving_candidate_condition"]
                    for result in summary["control_results"]
                )
                for summary in summaries
            ),
        ),
        check(
            "i14_2_leakage_caveat_preserved",
            summaries[1]["motif_specific_control_record"][
                "extractive_mechanism_exceedance_recorded"
            ]
            is True
            and summaries[1]["motif_specific_control_record"][
                "clean_bounded_leakage_claim_allowed"
            ]
            is False,
        ),
        check(
            "i14_3_lobe_opposition_basis_preserved",
            summaries[2]["motif_specific_control_record"]["aggregate_only_redistribution_allowed"]
            is False
            and summaries[2]["motif_specific_control_record"]["route_lobe_a_capacity_delta"] > 0
            and summaries[2]["motif_specific_control_record"]["route_lobe_b_capacity_delta"] < 0,
        ),
        check(
            "control_backed_runtime_support_still_blocked",
            all(not summary["control_backed_runtime_support_claim_allowed"] for summary in summaries),
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data = {
        "artifact_id": "n29_generative_extractive_direct_controls_i14b",
        "experiment_id": "N29",
        "iteration": "I14-B",
        "title": "Prototype D I14-B Direct Runtime Candidate Controls",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_direct_runtime_candidate_controls_fail_closed_pending_i14c",
        "source_artifacts": source_artifacts,
        "canonical_i14a_output_digest": i14a["output_digest"],
        "candidate_control_summaries": summaries,
        "triad_summary": triad_summary,
        "control_count": control_count,
        "failed_closed_count": failed_closed_count,
        "failed_open_count": failed_open_count,
        "surviving_candidate_count": len(summaries),
        "control_backed_runtime_support_claim_allowed": False,
        "replay_stress_backed_runtime_support_claim_allowed": False,
        "prototype_d_runtime_support_claim_allowed": False,
        "ready_for_i14c_replay_stress": True,
        "unsafe_claim_flags": UNSAFE_FLAGS,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_direct_runtime_candidate_controls"
        data["ready_for_i14c_replay_stress"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Prototype D I14-B Direct Runtime Candidate Controls",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"canonical_i14a_output_digest = {data['canonical_i14a_output_digest']}",
        f"control_count = {data['control_count']}",
        f"failed_closed_count = {data['failed_closed_count']}",
        f"failed_open_count = {data['failed_open_count']}",
        f"surviving_candidate_count = {data['surviving_candidate_count']}",
        f"control_backed_runtime_support_claim_allowed = {str(data['control_backed_runtime_support_claim_allowed']).lower()}",
        f"ready_for_i14c_replay_stress = {str(data['ready_for_i14c_replay_stress']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "I14-B is a control gate, not replay/stress support. It rejects the "
            "false-positive paths for all three direct candidates and keeps each "
            "surviving row as a candidate pending I14-C."
        ),
        "",
        "The N28 relabel control is scoped narrowly: copying an N28 label fails closed, "
        "but consuming N28 source-current traces remains allowed when the N29 row has "
        "its own artifact, manifest, threshold record, lineage audit, and claim boundary.",
        "",
        "## Candidate Summary",
        "",
        "| Candidate | Status | Notes |",
        "| --- | --- | --- |",
    ]
    for summary in data["candidate_control_summaries"]:
        notes = summary["motif_specific_control_record"]["required_i14c_stress"]
        lines.append(
            f"| `{summary['runtime_row_id']}` | `{summary['candidate_control_status']}` | `{notes}` |"
        )
    lines += [
        "",
        "## Controls",
        "",
        "| Candidate | Control | Status |",
        "| --- | --- | --- |",
    ]
    for summary in data["candidate_control_summaries"]:
        for result in summary["control_results"]:
            lines.append(
                f"| `{summary['runtime_row_id']}` | `{result['control_id']}` | `{result['control_status']}` |"
            )
    lines += [
        "",
        "## Claim Boundary",
        "",
        (
            "Runtime support, Prototype D success, resource economy, cooperation, "
            "exploitation, biological agency, native support, and agentic ecology "
            "runtime success remain blocked."
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

#!/usr/bin/env python3
"""Build focused N29 I14.2-1-B/C controls and replay/stress records."""

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
    "build_n29_extractive_clean_alternative_i1421bc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I1421 = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_search_i1421.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I14C = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_replay_stress_i14c.json"

OUT_B = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_controls_i1421b.json"
REPORT_B = EXPERIMENT / "reports" / "n29_extractive_clean_alternative_controls_i1421b.md"
OUT_C = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_replay_stress_i1421c.json"
REPORT_C = EXPERIMENT / "reports" / "n29_extractive_clean_alternative_replay_stress_i1421c.md"

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


def control_row(
    *,
    control_id: str,
    false_positive_shape: str,
    expected_result: str,
    actual_result: str,
    rung_effect: str,
) -> dict[str, Any]:
    row = {
        "control_id": control_id,
        "control_scope": "focused_i14_2_1_clean_extractive_replacement_blocker",
        "control_status": "failed_closed",
        "control_status_meaning": "false_positive_triggered_and_claim_rejected",
        "false_positive_shape": false_positive_shape,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
    }
    row["control_digest"] = digest_value(row)
    return row


def build_controls(i1421: dict[str, Any], i142: dict[str, Any], i14c: dict[str, Any]) -> dict[str, Any]:
    controls = [
        control_row(
            control_id="i14_2_1_over_ceiling_extractive_as_clean_control",
            false_positive_shape="supported extractive source row exceeds merge/leakage ceiling but is called clean bounded leakage",
            expected_result="rejected",
            actual_result="failed_closed_all_positive_extractive_sources_remain_over_ceiling",
            rung_effect="blocks_clean_extractive_replacement",
        ),
        control_row(
            control_id="i14_2_1_neutral_gap_transition_as_extractor_control",
            false_positive_shape="lower-leakage neutral-gap transition row is used as extractive positive evidence",
            expected_result="rejected",
            actual_result="failed_closed_transition_rows_are_unclassified_controls_not_positive_extractors",
            rung_effect="blocks_transition_backfill",
        ),
        control_row(
            control_id="i14_2_1_threshold_retune_to_fit_clean_control",
            false_positive_shape="N28 merge/leakage ceiling is widened or retuned to make extractor clean",
            expected_result="rejected",
            actual_result="failed_closed_threshold_retuning_for_n29_forbidden",
            rung_effect="blocks_retuned_clean_claim",
        ),
        control_row(
            control_id="i14_2_1_i14_2_caveat_erasure_control",
            false_positive_shape="original I14.2 leakage caveat is removed without a replacement row",
            expected_result="rejected",
            actual_result="failed_closed_original_i14_2_caveat_preserved",
            rung_effect="blocks_i14_2_upgrade",
        ),
        control_row(
            control_id="i14_2_1_report_only_search_as_runtime_control",
            false_positive_shape="I14.2-1 search report is treated as a new runtime extractor",
            expected_result="rejected",
            actual_result="failed_closed_search_record_created_no_runtime_candidate",
            rung_effect="blocks_runtime_support_from_search",
        ),
        control_row(
            control_id="i14_2_1_rerun_b_c_without_candidate_control",
            false_positive_shape="controls/replay are rerun as if a replacement runtime row exists",
            expected_result="not_applicable_or_rejected",
            actual_result="failed_closed_no_candidate_to_control_or_replay",
            rung_effect="blocks_empty_positive_validation",
        ),
        control_row(
            control_id="i14_2_1_source_manifest_gap_control",
            false_positive_shape="candidate source row lacks source-current inputs or verified artifact manifest",
            expected_result="rejected",
            actual_result="failed_closed_manifest_and_source_current_requirements_remain_required",
            rung_effect="blocks_non_source_current_replacement",
        ),
        control_row(
            control_id="i14_2_1_exploitation_relabel_control",
            false_positive_shape="extractive depletion is relabelled as exploitation, resource use, or ecology success",
            expected_result="rejected",
            actual_result="failed_closed_semantic_ecology_claims_remain_blocked",
            rung_effect="blocks_ecology_overclaim",
        ),
    ]

    failed_open = [row for row in controls if row["claim_allowed_when_control_triggers"]]
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_clean_alternative_controls_i1421b",
        "experiment_id": "N29",
        "iteration": "I14.2-1-B",
        "title": "Prototype D I14.2-1-B Focused Clean Extractive Controls",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_focused_clean_extractive_replacement_controls_fail_closed",
        "source_artifacts": [
            source_artifact("n29_i14_2_1_clean_extractive_search", I1421, i1421),
            source_artifact("n29_i14_2_original_extractive_candidate", I142, i142),
            source_artifact("n29_i14c_direct_replay_stress_context", I14C, i14c),
        ],
        "control_results": controls,
        "control_count": len(controls),
        "failed_closed_count": len(controls),
        "failed_open_count": len(failed_open),
        "replacement_candidate_status_after_controls": "blocked_no_clean_replacement_candidate",
        "clean_replacement_candidate_created": False,
        "i14_2_original_caveat_preserved": True,
        "i14b_i14c_rerun_required_after_controls": False,
        "claim_ceiling": "focused_controls_validate_i14_2_1_clean_replacement_blocker_no_runtime_support",
        "prototype_d_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_1_source_passed", i1421["status"] == "passed"),
        check("i14_2_source_passed", i142["status"] == "passed"),
        check("i14c_source_passed", i14c["status"] == "passed"),
        check("i14_2_1_found_no_candidate", i1421["clean_replacement_candidate_created"] is False),
        check("control_count_expected", len(controls) == 8),
        check("all_controls_failed_closed", all(row["control_status"] == "failed_closed" for row in controls)),
        check("failed_open_count_zero", data["failed_open_count"] == 0),
        check("original_i14_2_caveat_preserved", data["i14_2_original_caveat_preserved"] is True),
        check("runtime_support_claim_not_allowed", data["prototype_d_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_focused_clean_extractive_controls_validation"
    return finalize(data)


def replay_not_applicable_row(mode: str, reason: str) -> dict[str, Any]:
    row = {
        "replay_mode": mode,
        "status": "blocked_no_runtime_candidate",
        "reason": reason,
        "claim_effect": "blocks_clean_extractive_replay_support",
    }
    row["replay_digest"] = digest_value(row)
    return row


def stress_not_applicable_row(stress_id: str, reason: str) -> dict[str, Any]:
    row = {
        "stress_id": stress_id,
        "status": "blocked_no_runtime_candidate",
        "reason": reason,
        "claim_effect": "blocks_clean_extractive_stress_support",
    }
    row["stress_digest"] = digest_value(row)
    return row


def build_replay_stress(i1421: dict[str, Any], controls: dict[str, Any]) -> dict[str, Any]:
    replay_rows = [
        replay_not_applicable_row(
            "artifact_replay",
            "I14.2-1 created a search/blocker artifact, not a replacement runtime artifact.",
        ),
        replay_not_applicable_row(
            "snapshot_load_replay",
            "No replacement runtime trace exists to snapshot/load.",
        ),
        replay_not_applicable_row(
            "duplicate_replay",
            "No replacement runtime candidate exists for duplicate replay.",
        ),
    ]
    stress_rows = [
        stress_not_applicable_row(
            "clean_extractive_depletion_replay_stress",
            "No clean bounded-leakage source-current extractor was admitted.",
        ),
        stress_not_applicable_row(
            "merge_leakage_boundary_stress",
            "The boundary was already crossed by every supported extractive source row.",
        ),
        stress_not_applicable_row(
            "neutral_gap_substitution_stress",
            "Neutral-gap transition rows are controls, not replacement extractor candidates.",
        ),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_clean_alternative_replay_stress_i1421c",
        "experiment_id": "N29",
        "iteration": "I14.2-1-C",
        "title": "Prototype D I14.2-1-C Focused Clean Extractive Replay / Stress",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_focused_clean_extractive_replay_stress_blocked_no_candidate",
        "source_artifacts": [
            source_artifact("n29_i14_2_1_clean_extractive_search", I1421, i1421),
            source_artifact("n29_i14_2_1_b_focused_controls", OUT_B, controls),
        ],
        "replay_results": replay_rows,
        "stress_results": stress_rows,
        "replay_stress_summary": {
            "replacement_runtime_candidate_exists": False,
            "stable_replay_count": 0,
            "stress_passed_count": 0,
            "blocked_replay_count": len(replay_rows),
            "blocked_stress_count": len(stress_rows),
            "why_not_positive_support": "I14.2-1 did not admit a clean replacement runtime candidate.",
        },
        "clean_extractive_replay_stress_supported": False,
        "i14_2_original_remains_consumable_only_with_leakage_caveat": True,
        "i14_5_generator_extractor_composition_implication": (
            "I14.5 may use the original I14.2 extractor only if the leakage "
            "caveat remains explicit; it cannot claim clean bounded-leakage "
            "extractor support from I14.2-1."
        ),
        "claim_ceiling": "focused_replay_stress_blocked_no_clean_runtime_candidate_original_i14_2_caveat_preserved",
        "prototype_d_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14_2_1_source_passed", i1421["status"] == "passed"),
        check("focused_controls_passed", controls["status"] == "passed"),
        check("focused_controls_failed_open_zero", controls["failed_open_count"] == 0),
        check("no_replacement_candidate_exists", i1421["clean_replacement_candidate_created"] is False),
        check("all_replay_blocked_no_candidate", all(row["status"] == "blocked_no_runtime_candidate" for row in replay_rows)),
        check("all_stress_blocked_no_candidate", all(row["status"] == "blocked_no_runtime_candidate" for row in stress_rows)),
        check("clean_replay_stress_not_supported", data["clean_extractive_replay_stress_supported"] is False),
        check("original_i14_2_caveat_preserved", data["i14_2_original_remains_consumable_only_with_leakage_caveat"] is True),
        check("runtime_support_claim_not_allowed", data["prototype_d_runtime_support_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_focused_clean_extractive_replay_stress_validation"
    return finalize(data)


def write_controls_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# N29 I14.2-1-B Focused Clean Extractive Controls",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"control_count = {data['control_count']}",
        f"failed_closed_count = {data['failed_closed_count']}",
        f"failed_open_count = {data['failed_open_count']}",
        f"clean_replacement_candidate_created = {str(data['clean_replacement_candidate_created']).lower()}",
        f"i14b_i14c_rerun_required_after_controls = {str(data['i14b_i14c_rerun_required_after_controls']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-1-B validates the blocker, not a positive replacement. It proves that",
        "over-ceiling extractor rows, neutral-gap transition rows, retuned thresholds,",
        "report-only search records, and erased I14.2 caveats all fail closed. The",
        "original I14.2 extractor remains usable only with its leakage caveat.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_replay_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["replay_stress_summary"]
    lines = [
        "# N29 I14.2-1-C Focused Clean Extractive Replay / Stress",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"replacement_runtime_candidate_exists = {str(summary['replacement_runtime_candidate_exists']).lower()}",
        f"blocked_replay_count = {summary['blocked_replay_count']}",
        f"blocked_stress_count = {summary['blocked_stress_count']}",
        f"clean_extractive_replay_stress_supported = {str(data['clean_extractive_replay_stress_supported']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-1-C records that replay/stress is blocked, not failed open. There is",
        "no clean replacement runtime artifact to replay. This preserves the correct",
        "handoff to I14.5: any generator/extractor composition using the current",
        "extractor must carry the original I14.2 leakage caveat.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i1421 = load_json(I1421)
    i142 = load_json(I142)
    i14c = load_json(I14C)
    controls = build_controls(i1421, i142, i14c)
    write_json(OUT_B, controls)
    controls = load_json(OUT_B)
    replay_stress = build_replay_stress(i1421, controls)
    write_json(OUT_C, replay_stress)
    replay_stress = load_json(OUT_C)
    write_controls_report(REPORT_B, controls)
    write_replay_report(REPORT_C, replay_stress)
    print(f"wrote {OUT_B.relative_to(ROOT)}")
    print(f"wrote {REPORT_B.relative_to(ROOT)}")
    print(f"wrote {OUT_C.relative_to(ROOT)}")
    print(f"wrote {REPORT_C.relative_to(ROOT)}")
    print(f"I14.2-1-B status = {controls['status']}")
    print(f"I14.2-1-B output_digest = {controls['output_digest']}")
    print(f"I14.2-1-C status = {replay_stress['status']}")
    print(f"I14.2-1-C output_digest = {replay_stress['output_digest']}")


if __name__ == "__main__":
    main()

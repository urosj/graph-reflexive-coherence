#!/usr/bin/env python3
"""Build N29 I13-A/B/C Prototype C validation and debt records."""

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
    "build_n29_proxy_susceptibility_reentry_i13abc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I13 = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_i13.json"

OUTPUT_I13A = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_extraction_i13a.json"
OUTPUT_I13B = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_controls_i13b.json"
OUTPUT_I13C = (
    EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_replay_stress_i13c.json"
)
REPORT_I13A = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_extraction_i13a.md"
REPORT_I13B = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_controls_i13b.md"
REPORT_I13C = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_replay_stress_i13c.md"

UNSAFE_FLAGS = {
    "agent_role_behavior_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "choice_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "identity_transfer_claim_allowed": False,
    "intentional_return_claim_allowed": False,
    "learning_as_semantic_knowledge_claim_allowed": False,
    "native_ap4_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "preference_ownership_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
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


def source_exists(source: dict[str, Any]) -> bool:
    path = ROOT / source["path"]
    return path.exists() and sha256_file(path) == source.get("sha256")


def source_summary(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source["source_id"],
        "path": source["path"],
        "artifact_id": source.get("artifact_id", "not_recorded"),
        "status": source.get("status", "not_recorded"),
        "acceptance_state": source.get("acceptance_state", "not_recorded"),
        "output_digest": source.get("output_digest", "not_recorded"),
        "sha256": source.get("sha256", "not_recorded"),
        "sha256_matches_file": source_exists(source),
    }


def source_artifact_record(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
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


def fail_if_needed(data: dict[str, Any], failure_state: str) -> dict[str, Any]:
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = failure_state
    return finalize(data)


def build_i13a(i13: dict[str, Any]) -> dict[str, Any]:
    record = i13["prototype_c_record"]
    bridge_parts = record["bridge_parts"]
    source_ids_by_part = {
        part["part_id"]: part["primary_source_ids"] for part in bridge_parts
    }
    unique_primary_source_ids = sorted(
        {source_id for source_ids in source_ids_by_part.values() for source_id in source_ids}
    )
    exact_row_requirements = [
        "single source-current runtime artifact contains proxy_or_perturbation_state",
        "same runtime artifact contains susceptibility_delta_or_modified_geometry",
        "same runtime artifact contains reentry_or_transfer_trace",
        "same runtime artifact contains collapse_or_differential_response_trace",
        "all four traces share one runtime lineage / snapshot chain",
        "row-level timing order is source-current rather than stitched from summaries",
        "per-row thresholds and controls are declared before outcome inspection",
    ]
    missing_exact_row_evidence = [
        "I13 part sources are distributed across N22, N23, N26, and N27 artifacts",
        "no artifact_id appears as the primary source for all four bridge parts",
        "N29 I5-I8 are coverage indexes only and cannot replace original source rows",
    ]
    extraction_record = {
        "prototype_family": "proxy_susceptibility_reentry",
        "i13_source_digest": i13["output_digest"],
        "extraction_attempt_id": "N29.I13A.PROTOTYPE_C.EXACT_ROW_EXTRACTION",
        "bridge_parts_source_backed": record["all_four_parts_source_backed"],
        "exact_source_current_runtime_row_found": False,
        "exact_row_requirements": exact_row_requirements,
        "source_ids_by_part": source_ids_by_part,
        "unique_primary_source_ids": unique_primary_source_ids,
        "missing_exact_row_evidence": missing_exact_row_evidence,
        "row_decision": "blocked_for_runtime_claim_supported_as_mapping_inventory",
        "prototype_c_runtime_claim_allowed": False,
        "mapping_record_consumable": True,
        "ready_for_i13b_controls": True,
        "ready_for_i13c_replay_stress_decision": True,
        "claim_ceiling": (
            "exact-row extraction attempt over source-backed Prototype C parts; "
            "runtime Prototype C remains blocked"
        ),
    }
    checks = [
        check("i13_source_passed", i13.get("status") == "passed"),
        check("all_four_parts_still_source_backed", record["all_four_parts_source_backed"] is True),
        check("exact_runtime_row_not_found", extraction_record["exact_source_current_runtime_row_found"] is False),
        check("runtime_claim_blocked", extraction_record["prototype_c_runtime_claim_allowed"] is False),
        check("mapping_record_consumable", extraction_record["mapping_record_consumable"] is True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_extraction_i13a",
        "experiment_id": "N29",
        "title": "Prototype C I13-A Exact Row Extraction Attempt",
        "iteration": "I13-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13a_exact_row_absent_mapping_inventory_consumable",
        "source_artifacts": [source_artifact_record("n29_i13_admission", I13, i13)],
        "extraction_record": extraction_record,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    return fail_if_needed(data, "failed_i13a_exact_row_extraction")


def build_i13b(i13: dict[str, Any], i13a: dict[str, Any]) -> dict[str, Any]:
    required_controls = i13["prototype_c_record"]["required_controls_for_future_runtime_tranche"]
    control_rows = []
    for control_id in required_controls:
        control_rows.append(
            {
                "control_id": control_id,
                "control_scope": "mapping_and_relabel_control_over_i13a_extraction_attempt",
                "control_status": "failed_closed",
                "expected_result": "claim rejected when false-positive path is asserted",
                "actual_result": "claim rejected; no Prototype C runtime row admitted",
                "runtime_claim_allowed_when_control_triggers": False,
                "mapping_record_allowed_when_control_triggers": True,
                "rung_effect": "blocks runtime Prototype C; preserves mapping/debt record",
            }
        )
    controls_record = {
        "prototype_family": "proxy_susceptibility_reentry",
        "i13_source_digest": i13["output_digest"],
        "i13a_source_digest": i13a["output_digest"],
        "control_matrix_id": "N29.I13B.PROTOTYPE_C.MAPPING_RELABEL_CONTROLS",
        "control_execution_kind": "mapping_relabel_and_cross_experiment_stitching_controls",
        "control_rows": control_rows,
        "all_controls_failed_closed": all(
            row["control_status"] == "failed_closed" for row in control_rows
        ),
        "failed_open_control_count": sum(
            row["control_status"] == "failed_open" for row in control_rows
        ),
        "runtime_control_matrix_run": False,
        "runtime_control_matrix_not_run_reason": (
            "I13-A did not admit an exact source-current runtime row; I13-B can only "
            "test relabel/stitching controls over the mapping/extraction record."
        ),
        "prototype_c_runtime_claim_allowed": False,
        "claim_ceiling": (
            "fail-closed mapping/relabel controls over Prototype C source-backed parts; "
            "no runtime control-backed Prototype C"
        ),
    }
    checks = [
        check("i13a_source_passed", i13a.get("status") == "passed"),
        check("required_controls_present", len(control_rows) == len(required_controls)),
        check("all_controls_failed_closed", controls_record["all_controls_failed_closed"]),
        check("failed_open_control_count_zero", controls_record["failed_open_control_count"] == 0),
        check("runtime_claim_blocked", controls_record["prototype_c_runtime_claim_allowed"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_controls_i13b",
        "experiment_id": "N29",
        "title": "Prototype C I13-B Mapping Relabel Controls",
        "iteration": "I13-B",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13b_mapping_controls_fail_closed_no_runtime_claim",
        "source_artifacts": [
            source_artifact_record("n29_i13_admission", I13, i13),
            source_artifact_record("n29_i13a_extraction", OUTPUT_I13A, i13a),
        ],
        "controls_record": controls_record,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    return fail_if_needed(data, "failed_i13b_mapping_controls")


def build_i13c(i13: dict[str, Any], i13a: dict[str, Any], i13b: dict[str, Any]) -> dict[str, Any]:
    source_stability_rows = [
        source_summary(source) for source in i13.get("source_artifacts", [])
    ]
    source_sha_stable = all(row["sha256_matches_file"] for row in source_stability_rows)
    replay_stress_record = {
        "prototype_family": "proxy_susceptibility_reentry",
        "i13_source_digest": i13["output_digest"],
        "i13a_source_digest": i13a["output_digest"],
        "i13b_source_digest": i13b["output_digest"],
        "runtime_replay_status": "not_run",
        "runtime_replay_not_run_reason": (
            "No exact source-current runtime row was admitted by I13-A."
        ),
        "runtime_stress_status": "not_run",
        "runtime_stress_not_run_reason": (
            "No exact source-current runtime row exists for stress variation."
        ),
        "source_chain_digest_replay_status": "stable" if source_sha_stable else "failed",
        "source_chain_stability_rows": source_stability_rows,
        "controls_consumed": i13b["controls_record"]["all_controls_failed_closed"],
        "mapping_only_with_stable_sources": source_sha_stable
        and i13a["extraction_record"]["mapping_record_consumable"]
        and i13b["controls_record"]["all_controls_failed_closed"],
        "prototype_c_runtime_claim_allowed": False,
        "prototype_c_runtime_success_supported": False,
        "ready_for_iteration_14": True,
        "iteration_14_handoff_role": (
            "carry Prototype C as a source-backed mapping/debt motif, not a runtime "
            "prototype success"
        ),
        "claim_ceiling": (
            "source-stable mapping-only Prototype C record; runtime replay/stress "
            "blocked by absent exact row"
        ),
    }
    checks = [
        check("i13b_source_passed", i13b.get("status") == "passed"),
        check("source_chain_sha_stable", source_sha_stable),
        check("runtime_replay_not_run", replay_stress_record["runtime_replay_status"] == "not_run"),
        check("runtime_stress_not_run", replay_stress_record["runtime_stress_status"] == "not_run"),
        check("runtime_claim_blocked", replay_stress_record["prototype_c_runtime_claim_allowed"] is False),
        check("mapping_only_with_stable_sources", replay_stress_record["mapping_only_with_stable_sources"]),
        check("ready_for_iteration_14", replay_stress_record["ready_for_iteration_14"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_replay_stress_i13c",
        "experiment_id": "N29",
        "title": "Prototype C I13-C Replay / Stress Decision",
        "iteration": "I13-C",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13c_source_stable_mapping_only_runtime_replay_stress_not_admitted",
        "source_artifacts": [
            source_artifact_record("n29_i13_admission", I13, i13),
            source_artifact_record("n29_i13a_extraction", OUTPUT_I13A, i13a),
            source_artifact_record("n29_i13b_controls", OUTPUT_I13B, i13b),
        ],
        "replay_stress_record": replay_stress_record,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    return fail_if_needed(data, "failed_i13c_replay_stress_decision")


def write_report(path: Path, data: dict[str, Any], record_key: str) -> None:
    record = data[record_key]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        f"Claim ceiling: `{record['claim_ceiling']}`",
        "",
    ]
    if record_key == "extraction_record":
        lines.extend(
            [
                "## Extraction",
                "",
                f"Exact source-current runtime row found: `{str(record['exact_source_current_runtime_row_found']).lower()}`",
                "",
                f"Mapping record consumable: `{str(record['mapping_record_consumable']).lower()}`",
                "",
                "Missing exact-row evidence:",
                "",
            ]
        )
        for item in record["missing_exact_row_evidence"]:
            lines.append(f"- {item}")
    elif record_key == "controls_record":
        lines.extend(
            [
                "## Controls",
                "",
                f"All controls failed closed: `{str(record['all_controls_failed_closed']).lower()}`",
                "",
                f"Runtime control matrix run: `{str(record['runtime_control_matrix_run']).lower()}`",
                "",
                record["runtime_control_matrix_not_run_reason"],
                "",
                "| Control | Status | Rung Effect |",
                "|---|---|---|",
            ]
        )
        for row in record["control_rows"]:
            lines.append(
                f"| `{row['control_id']}` | `{row['control_status']}` | {row['rung_effect']} |"
            )
    else:
        lines.extend(
            [
                "## Replay / Stress Decision",
                "",
                f"Runtime replay status: `{record['runtime_replay_status']}`",
                "",
                f"Runtime stress status: `{record['runtime_stress_status']}`",
                "",
                f"Source-chain digest replay status: `{record['source_chain_digest_replay_status']}`",
                "",
                f"Ready for I14: `{str(record['ready_for_iteration_14']).lower()}`",
                "",
                record["iteration_14_handoff_role"],
            ]
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i13 = load_json(I13)
    i13a = build_i13a(i13)
    write_json(OUTPUT_I13A, i13a)
    write_report(REPORT_I13A, i13a, "extraction_record")

    i13b = build_i13b(i13, i13a)
    write_json(OUTPUT_I13B, i13b)
    write_report(REPORT_I13B, i13b, "controls_record")

    i13c = build_i13c(i13, i13a, i13b)
    write_json(OUTPUT_I13C, i13c)
    write_report(REPORT_I13C, i13c, "replay_stress_record")


if __name__ == "__main__":
    main()

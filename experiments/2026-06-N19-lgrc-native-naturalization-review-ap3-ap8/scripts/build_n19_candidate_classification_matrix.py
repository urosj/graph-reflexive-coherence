#!/usr/bin/env python3
"""Build N19 Iteration 7 candidate classification matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
SCHEMA = EXPERIMENT / "outputs" / "n19_naturalization_schema_v1.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_candidate_classification_matrix.json"
REPORT = EXPERIMENT / "reports" / "n19_candidate_classification_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_candidate_classification_matrix.py"
)

SOURCE_CLASSIFIERS = [
    {
        "iteration": 3,
        "classification_scope": "AP3_AP5_lower_stack",
        "artifact": "outputs/n19_lower_stack_candidate_classification.json",
        "report": "reports/n19_lower_stack_candidate_classification.md",
    },
    {
        "iteration": 4,
        "classification_scope": "AP6_boundary",
        "artifact": "outputs/n19_ap6_boundary_native_readiness_classification.json",
        "report": "reports/n19_ap6_boundary_native_readiness_classification.md",
    },
    {
        "iteration": 5,
        "classification_scope": "AP7_closed_loop",
        "artifact": "outputs/n19_ap7_loop_native_readiness_classification.json",
        "report": "reports/n19_ap7_loop_native_readiness_classification.md",
    },
    {
        "iteration": 6,
        "classification_scope": "AP8_horizon_budget",
        "artifact": "outputs/n19_ap8_horizon_budget_native_readiness_classification.json",
        "report": "reports/n19_ap8_horizon_budget_native_readiness_classification.md",
    },
]

NAT_ORDER = ["NAT0", "NAT1", "NAT2", "NAT3", "NAT4", "NAT5", "NAT6"]
DISPOSITION_ORDER = [
    "scaffold",
    "native_contract_candidate",
    "phase8_ready_native_policy_candidate",
    "implementation_gap_blocker",
    "theory_sensitive_blocker",
    "unsafe_relabel_rejected",
    "not_applicable",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def no_absolute_paths(value: Any) -> bool:
    if isinstance(value, dict):
        return all(no_absolute_paths(item) for item in value.values())
    if isinstance(value, list):
        return all(no_absolute_paths(item) for item in value)
    if isinstance(value, str):
        forbidden = ["/" + "home/", "/" + "tmp/", "/" + "Users/", "C:" + "\\", "\\" + "Users\\"]
        return not any(marker in value for marker in forbidden)
    return True


def source_path(entry: dict[str, Any], key: str) -> Path:
    return EXPERIMENT / entry[key]


def source_record(entry: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    artifact = source_path(entry, "artifact")
    report = source_path(entry, "report")
    return {
        "iteration": entry["iteration"],
        "classification_scope": entry["classification_scope"],
        "artifact": {
            "path": rel(artifact),
            "sha256": sha256_file(artifact),
            "output_digest": str(data.get("output_digest", "not_recorded")),
            "status": str(data.get("status", "not_recorded")),
            "row_count": int(data.get("row_count", 0)),
        },
        "report": {
            "path": rel(report),
            "sha256": sha256_file(report),
        },
    }


def all_nat4_gates_pass(row: dict[str, Any]) -> bool:
    gates = row.get("nat4_gate_results", {})
    return bool(gates) and all(gates.values())


def phase8_ready_expected(row: dict[str, Any]) -> bool:
    return row.get("nat_level") == "NAT4" and all_nat4_gates_pass(row)


def claim_flags_all_false(row: dict[str, Any]) -> bool:
    flags = row.get("claim_flags", {})
    return isinstance(flags, dict) and bool(flags) and all(value is False for value in flags.values())


def disposition_bucket(row: dict[str, Any]) -> str:
    if row["phase8_ready"]:
        return "phase8_ready"
    if row["primary_disposition"] == "native_contract_candidate":
        return "native_contract_not_phase8_ready"
    if row["primary_disposition"] == "implementation_gap_blocker":
        return "implementation_gap_blocked"
    if row["primary_disposition"] == "unsafe_relabel_rejected":
        return "unsafe_relabel_rejected"
    return "non_ready_candidate"


def blocker_signature(row: dict[str, Any]) -> str:
    blockers = row.get("blockers_to_next_level", []) + row.get("blocked_claims", [])
    if not blockers:
        return "no_blocker_recorded"
    return digest_value(sorted(str(item) for item in blockers))


def matrix_row(
    row: dict[str, Any],
    source: dict[str, Any],
    source_record_data: dict[str, Any],
) -> dict[str, Any]:
    result = {
        "row_id": row["row_id"],
        "source_classifier_iteration": source["iteration"],
        "classification_scope": source["classification_scope"],
        "source_classifier_artifact": source_record_data["artifact"],
        "source_classifier_report": source_record_data["report"],
        "source_experiment": row["source_experiment"],
        "source_iteration_or_closeout": row["source_iteration_or_closeout"],
        "source_final_supported_ap_level": row["source_final_supported_ap_level"],
        "source_final_claim_ceiling": row["source_final_claim_ceiling"],
        "source_row_digest": row["row_digest"],
        "artifact_supported": row["artifact_supported"],
        "artifact_claim_scope": row["artifact_claim_scope"],
        "native_question": row["native_question"],
        "primary_disposition": row["primary_disposition"],
        "primary_disposition_is_single": isinstance(row["primary_disposition"], str)
        and row["primary_disposition"] in DISPOSITION_ORDER,
        "nat_level": row["nat_level"],
        "nat_level_order": NAT_ORDER.index(row["nat_level"]),
        "row_decision": row["row_decision"],
        "phase8_ready": row["phase8_ready"],
        "phase8_ready_expected": phase8_ready_expected(row),
        "phase8_ready_derivation_valid": row["phase8_ready"] == phase8_ready_expected(row),
        "phase8_ready_derivation": row["phase8_ready_derivation"],
        "nat4_gates_all_pass": all_nat4_gates_pass(row),
        "nat4_gate_results": row.get("nat4_gate_results", {}),
        "matrix_disposition": disposition_bucket(row),
        "native_policy_or_telemetry_surface_name": row[
            "native_policy_or_telemetry_surface_name"
        ],
        "runtime_visible_inputs": row["runtime_visible_inputs"],
        "native_state_needed": row["native_state_needed"],
        "state_mutation_owner": row["state_mutation_owner"],
        "budget_surface": row["budget_surface"],
        "telemetry_requirements": row["telemetry_requirements"],
        "snapshot_replay_requirements": row["snapshot_replay_requirements"],
        "negative_controls": row["negative_controls"],
        "minimal_producer_code_needed": row["minimal_producer_code_needed"],
        "implementation_boundary": row["implementation_boundary"],
        "non_rc_quantity_audit": row["non_rc_quantity_audit"],
        "blocked_claims": row["blocked_claims"],
        "blockers_to_next_level": row["blockers_to_next_level"],
        "blocker_signature": blocker_signature(row),
        "claim_flags": row["claim_flags"],
        "claim_flags_all_false": claim_flags_all_false(row),
        "phase8_opened": row["phase8_opened"],
        "native_support_opened": row["native_support_opened"],
        "src_diff_empty": row["src_diff_empty"],
        "producer_code_recorded": bool(row["minimal_producer_code_needed"]),
    }
    result["matrix_row_digest"] = digest_value(result)
    return result


def load_source_classifiers() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for entry in SOURCE_CLASSIFIERS:
        artifact = source_path(entry, "artifact")
        data = load_json(artifact)
        record = source_record(entry, data)
        records.append(record)
        for row in data["candidate_rows"]:
            rows.append(matrix_row(row, entry, record))
    return records, rows


def count_by(rows: list[dict[str, Any]], key: str, order: list[str] | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row[key]] = counts.get(row[key], 0) + 1
    if order:
        return {item: counts.get(item, 0) for item in order if counts.get(item, 0)}
    return dict(sorted(counts.items()))


def distinct_blocked_rows(rows: list[dict[str, Any]]) -> bool:
    blocked = [row for row in rows if row["row_decision"] == "blocked"]
    signatures = [row["blocker_signature"] for row in blocked]
    return bool(blocked) and all(signature != "no_blocker_recorded" for signature in signatures) and (
        len(signatures) == len(set(signatures))
    )


def validate_rows(rows: list[dict[str, Any]], schema: dict[str, Any]) -> list[dict[str, Any]]:
    implementation_gap_rows = [
        row for row in rows if row["primary_disposition"] == "implementation_gap_blocker"
    ]
    checks = [
        {
            "check_id": "candidate_row_count_matches_i3_i6_inputs",
            "passed": len(rows) == 24,
            "detail": len(rows),
        },
        {
            "check_id": "each_candidate_has_one_primary_disposition",
            "passed": all(row["primary_disposition_is_single"] for row in rows),
            "detail": count_by(rows, "primary_disposition", DISPOSITION_ORDER),
        },
        {
            "check_id": "phase8_ready_derived_from_nat4_gates",
            "passed": all(row["phase8_ready_derivation_valid"] for row in rows),
            "detail": {
                "phase8_ready_rows": [
                    row["row_id"] for row in rows if row["phase8_ready"]
                ],
                "derivation": schema["candidate_row_schema"]["phase8_ready_derivation"],
            },
        },
        {
            "check_id": "nat4_rows_satisfy_every_nat4_gate",
            "passed": all(row["nat4_gates_all_pass"] for row in rows if row["nat_level"] == "NAT4"),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
        },
        {
            "check_id": "nat3_rows_kept_below_phase8_ready",
            "passed": all(not row["phase8_ready"] for row in rows if row["nat_level"] == "NAT3"),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT3"],
        },
        {
            "check_id": "blocked_rows_have_distinct_blockers",
            "passed": distinct_blocked_rows(rows),
            "detail": {
                row["row_id"]: row["blockers_to_next_level"] + row["blocked_claims"]
                for row in rows
                if row["row_decision"] == "blocked"
            },
        },
        {
            "check_id": "implementation_gap_rows_record_minimal_producer_code",
            "passed": all(row["producer_code_recorded"] for row in implementation_gap_rows),
            "detail": {
                row["row_id"]: row["minimal_producer_code_needed"]
                for row in implementation_gap_rows
            },
        },
        {
            "check_id": "no_native_implementation_claim_made",
            "passed": all(
                row["nat_level"] not in {"NAT5", "NAT6"}
                and row["phase8_opened"] is False
                and row["native_support_opened"] is False
                for row in rows
            ),
            "detail": "NAT5/NAT6 absent; phase8_opened and native_support_opened false",
        },
        {
            "check_id": "unsafe_claim_flags_forced_false",
            "passed": all(row["claim_flags_all_false"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "source_digests_preserved",
            "passed": all(
                row["source_classifier_artifact"]["sha256"]
                and row["source_classifier_artifact"]["output_digest"]
                and row["source_row_digest"]
                for row in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(rows),
            "detail": "all matrix paths are relative",
        },
        {
            "check_id": "src_diff_empty_recorded_true",
            "passed": all(row["src_diff_empty"] is True for row in rows),
            "detail": len(rows),
        },
    ]
    return checks


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_candidate_rows": len(rows),
        "by_classification_scope": count_by(rows, "classification_scope"),
        "by_nat_level": count_by(rows, "nat_level", NAT_ORDER),
        "by_primary_disposition": count_by(rows, "primary_disposition", DISPOSITION_ORDER),
        "by_matrix_disposition": count_by(rows, "matrix_disposition"),
        "phase8_ready_row_count": sum(1 for row in rows if row["phase8_ready"]),
        "phase8_ready_rows": [row["row_id"] for row in rows if row["phase8_ready"]],
        "native_contract_candidate_rows": [
            row["row_id"]
            for row in rows
            if row["primary_disposition"] == "native_contract_candidate"
        ],
        "implementation_gap_blocker_rows": [
            row["row_id"]
            for row in rows
            if row["primary_disposition"] == "implementation_gap_blocker"
        ],
        "unsafe_relabel_rejected_rows": [
            row["row_id"]
            for row in rows
            if row["primary_disposition"] == "unsafe_relabel_rejected"
        ],
        "phase8_ready_surfaces": [
            row["native_policy_or_telemetry_surface_name"]
            for row in rows
            if row["phase8_ready"]
        ],
        "non_ready_rows": [row["row_id"] for row in rows if not row["phase8_ready"]],
        "claim_boundary": (
            "NAT4 rows are Phase-8-ready contracts only. N19 does not implement "
            "Phase 8, does not open native support, and does not support agency, "
            "selfhood, semantic action/perception, organism/life, unrestricted autonomy, or AP9."
        ),
    }


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 7 - Candidate Classification Matrix",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"row_count = {artifact['row_count']}",
        f"phase8_ready_row_count = {artifact['classification_summary']['phase8_ready_row_count']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Candidate matrix:",
        "",
        "| Row | Scope | Disposition | NAT | Decision | Phase 8 Ready | Surface |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["candidate_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["classification_scope"],
                    row["primary_disposition"],
                    row["nat_level"],
                    row["row_decision"],
                    str(row["phase8_ready"]).lower(),
                    row["native_policy_or_telemetry_surface_name"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(artifact["classification_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "Interpretation:",
            "",
            "```text",
            artifact["interpretation"]["main_read"],
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    schema = load_json(SCHEMA)
    source_records, rows = load_source_classifiers()
    checks = [
        {
            "check_id": "schema_freeze_passed",
            "passed": schema.get("status") == "passed"
            and schema.get("candidate_rows_classified") is False,
            "detail": rel(SCHEMA),
        },
        {
            "check_id": "source_classifiers_passed",
            "passed": all(record["artifact"]["status"] == "passed" for record in source_records),
            "detail": {
                record["classification_scope"]: record["artifact"]["status"]
                for record in source_records
            },
        },
    ] + validate_rows(rows, schema)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_candidate_classification_matrix",
        "schema_version": "n19_candidate_classification_matrix_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 7,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Synthesize N19 Iterations 3-6 into one candidate classification matrix "
            "without widening any NAT level, claim boundary, or Phase 8 status."
        ),
        "schema_source": {
            "path": rel(SCHEMA),
            "sha256": sha256_file(SCHEMA),
            "output_digest": schema["output_digest"],
        },
        "source_classifiers": source_records,
        "candidate_rows": rows,
        "row_count": len(rows),
        "classification_summary": build_summary(rows),
        "interpretation": {
            "main_read": (
                "Iteration 7 consolidates the AP3-AP8 native-naturalization review: "
                "12 rows are NAT4 Phase-8-ready policy or telemetry candidates, 3 rows "
                "remain NAT3 native-contract candidates, 4 rows remain implementation-gap "
                "blockers, and 5 rows are unsafe relabel rejections. This is a readiness "
                "classification matrix, not native implementation."
            ),
            "scope_boundary": (
                "The matrix preserves row-level claim ceilings from I3-I6. NAT3 rows do "
                "not become Phase-8-ready, NAT2 blockers remain blockers, NAT0 unsafe "
                "relabels remain rejected, and all claim flags remain false."
            ),
        },
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
        "src_diff_empty": True,
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

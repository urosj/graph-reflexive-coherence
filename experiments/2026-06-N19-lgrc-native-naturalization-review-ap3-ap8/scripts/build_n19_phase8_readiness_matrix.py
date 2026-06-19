#!/usr/bin/env python3
"""Build N19 Iteration 7 Phase 8 readiness matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
CANDIDATE_MATRIX = EXPERIMENT / "outputs" / "n19_candidate_classification_matrix.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_phase8_readiness_matrix.json"
REPORT = EXPERIMENT / "reports" / "n19_phase8_readiness_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_phase8_readiness_matrix.py"
)


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


def all_nat4_gates_pass(row: dict[str, Any]) -> bool:
    gates = row.get("nat4_gate_results", {})
    return bool(gates) and all(gates.values())


def readiness_domain(row: dict[str, Any]) -> str:
    scope = row["classification_scope"]
    if scope == "AP3_AP5_lower_stack":
        return "support_regulation_lower_stack"
    if scope == "AP6_boundary":
        return "boundary_separability"
    if scope == "AP7_closed_loop":
        return "closed_boundary_engagement_loop"
    if scope == "AP8_horizon_budget":
        return "long_horizon_budget_and_continuity"
    return "unknown"


def readiness_row(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        "readiness_id": "phase8_ready_" + row["row_id"],
        "source_candidate_row_id": row["row_id"],
        "classification_scope": row["classification_scope"],
        "readiness_domain": readiness_domain(row),
        "source_experiment": row["source_experiment"],
        "source_iteration_or_closeout": row["source_iteration_or_closeout"],
        "source_classifier_artifact": row["source_classifier_artifact"],
        "source_row_digest": row["source_row_digest"],
        "native_policy_or_telemetry_surface_name": row[
            "native_policy_or_telemetry_surface_name"
        ],
        "phase8_ready": True,
        "nat_level": row["nat_level"],
        "nat4_gate_results": row["nat4_gate_results"],
        "nat4_gates_all_pass": row["nat4_gates_all_pass"],
        "native_implementation_claimed": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "runtime_visible_inputs": row["runtime_visible_inputs"],
        "native_state_needed": row["native_state_needed"],
        "state_mutation_owner": row["state_mutation_owner"],
        "budget_surface": row["budget_surface"],
        "telemetry_requirements": row["telemetry_requirements"],
        "snapshot_replay_requirements": row["snapshot_replay_requirements"],
        "negative_controls": row["negative_controls"],
        "minimal_producer_code_needed": row["minimal_producer_code_needed"],
        "implementation_boundary": row["implementation_boundary"],
        "blocked_claims": row["blocked_claims"],
        "producer_implementation_scope": (
            "future default-off Phase 8 producer/runtime work only; N19 records "
            "the required surface and validation contract without implementing it"
        ),
        "claim_flags": row["claim_flags"],
        "claim_flags_all_false": row["claim_flags_all_false"],
    }
    result["readiness_row_digest"] = digest_value(result)
    return result


def non_ready_row(row: dict[str, Any]) -> dict[str, Any]:
    if row["nat_level"] == "NAT3":
        reason = "native contract candidate below Phase 8 readiness"
    elif row["primary_disposition"] == "implementation_gap_blocker":
        reason = "implementation gap blocker"
    elif row["primary_disposition"] == "unsafe_relabel_rejected":
        reason = "unsafe relabel rejected"
    else:
        reason = "not Phase 8 ready"
    return {
        "source_candidate_row_id": row["row_id"],
        "classification_scope": row["classification_scope"],
        "source_experiment": row["source_experiment"],
        "primary_disposition": row["primary_disposition"],
        "nat_level": row["nat_level"],
        "row_decision": row["row_decision"],
        "phase8_ready": False,
        "reason": reason,
        "native_policy_or_telemetry_surface_name": row[
            "native_policy_or_telemetry_surface_name"
        ],
        "minimal_producer_code_needed": row["minimal_producer_code_needed"],
        "blockers_to_next_level": row["blockers_to_next_level"],
        "blocked_claims": row["blocked_claims"],
        "blocker_signature": row["blocker_signature"],
        "claim_flags_all_false": row["claim_flags_all_false"],
    }


def build_implementation_gap_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for row in rows:
        if row["phase8_ready"]:
            continue
        if row["primary_disposition"] not in {
            "native_contract_candidate",
            "implementation_gap_blocker",
        }:
            continue
        gaps.append(
            {
                "source_candidate_row_id": row["row_id"],
                "classification_scope": row["classification_scope"],
                "source_experiment": row["source_experiment"],
                "current_nat_level": row["nat_level"],
                "current_disposition": row["primary_disposition"],
                "gap_type": (
                    "contract_to_nat4_gap"
                    if row["primary_disposition"] == "native_contract_candidate"
                    else "implementation_blocker_to_contract_gap"
                ),
                "surface": row["native_policy_or_telemetry_surface_name"],
                "minimal_producer_code_needed": row["minimal_producer_code_needed"],
                "blockers_to_next_level": row["blockers_to_next_level"],
                "blocked_claims": row["blocked_claims"],
            }
        )
    return gaps


def blocked_signatures_distinct(rows: list[dict[str, Any]]) -> bool:
    blocked = [row for row in rows if row["row_decision"] == "blocked"]
    signatures = [row["blocker_signature"] for row in blocked]
    return bool(blocked) and len(signatures) == len(set(signatures)) and all(
        signature != "no_blocker_recorded" for signature in signatures
    )


def validate(
    candidate_matrix: dict[str, Any],
    rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    non_ready_rows: list[dict[str, Any]],
    implementation_gap_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "candidate_matrix_passed",
            "passed": candidate_matrix.get("status") == "passed",
            "detail": rel(CANDIDATE_MATRIX),
        },
        {
            "check_id": "readiness_rows_are_nat4_only",
            "passed": all(row["nat_level"] == "NAT4" for row in readiness_rows),
            "detail": len(readiness_rows),
        },
        {
            "check_id": "all_readiness_rows_satisfy_nat4_gates",
            "passed": all(row["nat4_gates_all_pass"] for row in readiness_rows),
            "detail": [row["source_candidate_row_id"] for row in readiness_rows],
        },
        {
            "check_id": "nat3_rows_kept_below_phase8_ready",
            "passed": all(
                row["phase8_ready"] is False
                for row in non_ready_rows
                if row["nat_level"] == "NAT3"
            ),
            "detail": [
                row["source_candidate_row_id"]
                for row in non_ready_rows
                if row["nat_level"] == "NAT3"
            ],
        },
        {
            "check_id": "blocked_rows_have_distinct_blockers",
            "passed": blocked_signatures_distinct(rows),
            "detail": {
                row["row_id"]: row["blockers_to_next_level"] + row["blocked_claims"]
                for row in rows
                if row["row_decision"] == "blocked"
            },
        },
        {
            "check_id": "implementation_gap_rows_record_minimal_producer_code",
            "passed": all(row["minimal_producer_code_needed"] for row in implementation_gap_rows),
            "detail": {
                row["source_candidate_row_id"]: row["minimal_producer_code_needed"]
                for row in implementation_gap_rows
            },
        },
        {
            "check_id": "no_native_implementation_claim_made",
            "passed": all(
                row["native_implementation_claimed"] is False
                and row["phase8_opened"] is False
                and row["native_support_opened"] is False
                for row in readiness_rows
            ),
            "detail": "readiness rows are future default-off contracts only",
        },
        {
            "check_id": "unsafe_claim_flags_remain_false",
            "passed": all(row["claim_flags_all_false"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "phase8_ready_count_matches_candidate_matrix",
            "passed": len(readiness_rows)
            == candidate_matrix["classification_summary"]["phase8_ready_row_count"],
            "detail": {
                "readiness_rows": len(readiness_rows),
                "candidate_matrix_ready_count": candidate_matrix["classification_summary"][
                    "phase8_ready_row_count"
                ],
            },
        },
        {
            "check_id": "source_digest_present",
            "passed": bool(candidate_matrix.get("output_digest"))
            and CANDIDATE_MATRIX.exists()
            and bool(sha256_file(CANDIDATE_MATRIX)),
            "detail": rel(CANDIDATE_MATRIX),
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(
                {
                    "readiness_rows": readiness_rows,
                    "non_ready_rows": non_ready_rows,
                    "implementation_gap_rows": implementation_gap_rows,
                }
            ),
            "detail": "all readiness matrix paths are relative",
        },
    ]
    return checks


def readiness_summary(
    rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    non_ready_rows: list[dict[str, Any]],
    implementation_gap_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_domain: dict[str, int] = {}
    for row in readiness_rows:
        by_domain[row["readiness_domain"]] = by_domain.get(row["readiness_domain"], 0) + 1
    return {
        "total_candidate_rows": len(rows),
        "phase8_ready_surface_count": len(readiness_rows),
        "non_ready_row_count": len(non_ready_rows),
        "producer_gap_row_count": len(implementation_gap_rows),
        "native_contract_gap_count": sum(
            1 for row in implementation_gap_rows if row["gap_type"] == "contract_to_nat4_gap"
        ),
        "implementation_gap_blocker_count": sum(
            1
            for row in implementation_gap_rows
            if row["gap_type"] == "implementation_blocker_to_contract_gap"
        ),
        "phase8_ready_by_domain": dict(sorted(by_domain.items())),
        "phase8_ready_surfaces": [
            row["native_policy_or_telemetry_surface_name"] for row in readiness_rows
        ],
        "native_contract_candidates_below_phase8": [
            row["source_candidate_row_id"]
            for row in non_ready_rows
            if row["nat_level"] == "NAT3"
        ],
        "implementation_gap_blockers": [
            row["source_candidate_row_id"]
            for row in non_ready_rows
            if row["primary_disposition"] == "implementation_gap_blocker"
        ],
        "unsafe_relabel_rejections": [
            row["source_candidate_row_id"]
            for row in non_ready_rows
            if row["primary_disposition"] == "unsafe_relabel_rejected"
        ],
        "final_readiness_boundary": (
            "Phase 8-ready means NAT4 gate-complete validation contract only. It does "
            "not mean native implementation, native support, agency, selfhood, semantic "
            "action/perception, organism/life behavior, unrestricted autonomy, or AP9."
        ),
    }


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 7 - Phase 8 Readiness Matrix",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"phase8_ready_surface_count = {artifact['readiness_summary']['phase8_ready_surface_count']}",
        f"non_ready_row_count = {artifact['readiness_summary']['non_ready_row_count']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Phase 8-ready surfaces:",
        "",
        "| Source Row | Domain | Surface | Implementation Claimed |",
        "| --- | --- | --- | --- |",
    ]
    for row in artifact["phase8_ready_surfaces"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["source_candidate_row_id"],
                    row["readiness_domain"],
                    row["native_policy_or_telemetry_surface_name"],
                    str(row["native_implementation_claimed"]).lower(),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Non-ready rows:",
            "",
            "| Source Row | NAT | Disposition | Reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in artifact["non_ready_candidate_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["source_candidate_row_id"],
                    row["nat_level"],
                    row["primary_disposition"],
                    row["reason"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Readiness summary:",
            "",
            "```json",
            json.dumps(artifact["readiness_summary"], indent=2, sort_keys=True),
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
    candidate_matrix = load_json(CANDIDATE_MATRIX)
    rows = candidate_matrix["candidate_rows"]
    ready_source_rows = [
        row
        for row in rows
        if row["phase8_ready"] and row["nat_level"] == "NAT4" and all_nat4_gates_pass(row)
    ]
    readiness_rows = [readiness_row(row) for row in ready_source_rows]
    non_ready_rows = [non_ready_row(row) for row in rows if not row["phase8_ready"]]
    implementation_gap_rows = build_implementation_gap_matrix(rows)
    checks = validate(
        candidate_matrix,
        rows,
        readiness_rows,
        non_ready_rows,
        implementation_gap_rows,
    )
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_phase8_readiness_matrix",
        "schema_version": "n19_phase8_readiness_matrix_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 7,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Derive the Phase 8 readiness matrix from the I7 candidate matrix, allowing "
            "only NAT4 gate-complete rows to become Phase-8-ready surfaces."
        ),
        "candidate_matrix_source": {
            "path": rel(CANDIDATE_MATRIX),
            "sha256": sha256_file(CANDIDATE_MATRIX),
            "output_digest": candidate_matrix["output_digest"],
            "status": candidate_matrix["status"],
        },
        "phase8_ready_surfaces": readiness_rows,
        "non_ready_candidate_rows": non_ready_rows,
        "implementation_gap_matrix": implementation_gap_rows,
        "readiness_summary": readiness_summary(
            rows, readiness_rows, non_ready_rows, implementation_gap_rows
        ),
        "interpretation": {
            "main_read": (
                "Iteration 7 records a Phase 8 readiness matrix with 12 gate-complete "
                "NAT4 surfaces. The remaining 12 rows stay below readiness as NAT3 "
                "contracts, NAT2 implementation blockers, or NAT0 unsafe relabel "
                "rejections. No native implementation claim is made."
            ),
            "scope_boundary": (
                "Readiness is a future implementation contract. Phase 8 remains unopened, "
                "native support remains unopened, NAT5/NAT6 remain out of scope, and "
                "blocked/rejected rows remain blocked or rejected."
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

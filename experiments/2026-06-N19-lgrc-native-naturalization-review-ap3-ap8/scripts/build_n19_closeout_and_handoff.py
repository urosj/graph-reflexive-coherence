#!/usr/bin/env python3
"""Build N19 Iteration 8 closeout and handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
CANDIDATE_MATRIX = EXPERIMENT / "outputs" / "n19_candidate_classification_matrix.json"
READINESS_MATRIX = EXPERIMENT / "outputs" / "n19_phase8_readiness_matrix.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_closeout_and_handoff.json"
REPORT = EXPERIMENT / "reports" / "n19_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_closeout_and_handoff.py"
)

NAT_ORDER = {"NAT0": 0, "NAT1": 1, "NAT2": 2, "NAT3": 3, "NAT4": 4, "NAT5": 5, "NAT6": 6}

AP_LEVELS = [
    {
        "ap_level": "AP3",
        "source_experiment": "N13",
        "claimed_artifact_role": "support-seeking regulation and bounded response magnitude",
        "claim_scope": "artifact-level AP3 support/regulation candidate",
        "required_for_current_ladder": True,
    },
    {
        "ap_level": "AP4",
        "source_experiment": "N14",
        "claimed_artifact_role": "consequence-sensitive route selection",
        "claim_scope": "artifact-level AP4 consequence-sensitive selection candidate",
        "required_for_current_ladder": True,
    },
    {
        "ap_level": "AP5",
        "source_experiment": "N15",
        "claimed_artifact_role": "endogenous proxy / target formation",
        "claim_scope": "artifact-level AP5 endogenous proxy formation candidate",
        "required_for_current_ladder": True,
    },
    {
        "ap_level": "AP6",
        "source_experiment": "N16",
        "claimed_artifact_role": "self/environment boundary requirements",
        "claim_scope": "artifact-level AP6 self/environment boundary candidate",
        "required_for_current_ladder": True,
    },
    {
        "ap_level": "AP7",
        "source_experiment": "N17",
        "claimed_artifact_role": "closed boundary engagement loop",
        "claim_scope": "artifact-level AP7 closed-loop boundary engagement candidate",
        "required_for_current_ladder": True,
    },
    {
        "ap_level": "AP8",
        "source_experiment": "N18",
        "claimed_artifact_role": "limited h4/L5 long-horizon closure stress envelope",
        "claim_scope": "limited artifact-level AP8 h4/L5 candidate",
        "required_for_current_ladder": True,
    },
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


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def all_claim_flags_false(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        flags = row.get("claim_flags", {})
        if not isinstance(flags, dict) or not flags or any(value is not False for value in flags.values()):
            return False
    return True


def best_nat_level(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "none"
    return max((row["nat_level"] for row in rows), key=lambda value: NAT_ORDER[value])


def nat4_gap_explanation(ap_level: str, ap_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if ap_level == "AP4":
        return {
            "ap_level": "AP4",
            "source_experiment": "N14",
            "best_current_evidence": (
                "N14 route consequence-selection telemetry is a NAT3 native-contract "
                "candidate, not NAT4 Phase-8-ready evidence."
            ),
            "missing_for_nat4": [
                "source-current route-conditioned support/regulation rows",
                "observed route-conditioned support/regulation inputs instead of constructed followout",
                "peer-route same-horizon comparison records",
                "peer-route same-budget comparison records",
                "default-off native route-selection telemetry surface with replay and stale-record controls",
                "rejection record for generic support/regulation reuse as route-conditioned evidence",
            ],
            "why_this_blocks_ladder_generation": (
                "AP4 is the consequence-sensitive selection rung. Without source-current "
                "route-conditioned support/regulation evidence, a native producer could "
                "record route consequences, but it could not generate the claimed AP4 "
                "selection step as a NAT4 Phase-8-ready rung."
            ),
            "source_rows": [
                row["row_id"]
                for row in ap_rows
                if row["source_experiment"] == "N14"
            ],
        }
    if ap_level == "AP5":
        return {
            "ap_level": "AP5",
            "source_experiment": "N15",
            "best_current_evidence": (
                "N15 proxy derivation is a NAT3 native-contract candidate, not NAT4 "
                "Phase-8-ready evidence."
            ),
            "missing_for_nat4": [
                "native lower-stack input vector captured after AP3/AP4 native surfaces exist",
                "AP4 NAT4 route-conditioned support/regulation evidence",
                "default-off native proxy derivation policy record",
                "target condition digest recorded before use",
                "replay digest over target derivation, bridge ranking, budget, and claim flags",
                "validation that readiness-only context remains non-mutating support context",
            ],
            "why_this_blocks_ladder_generation": (
                "AP5 derives a proxy/target from lower-stack inputs. Because AP4 is not "
                "yet NAT4, and because the proxy derivation policy is not implemented as "
                "a native default-off surface, the current implementation cannot generate "
                "the AP5 rung as NAT4 Phase-8-ready evidence."
            ),
            "source_rows": [
                row["row_id"]
                for row in ap_rows
                if row["source_experiment"] == "N15"
            ],
        }
    return {
        "ap_level": ap_level,
        "source_experiment": "not_applicable",
        "best_current_evidence": "not_applicable",
        "missing_for_nat4": [],
        "why_this_blocks_ladder_generation": "not_applicable",
        "source_rows": [],
    }


def coverage_for_ap(ap: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    ap_rows = [row for row in rows if row["source_experiment"] == ap["source_experiment"]]
    nat4_rows = [row for row in ap_rows if row["nat_level"] == "NAT4" and row["phase8_ready"]]
    nat3_rows = [row for row in ap_rows if row["nat_level"] == "NAT3"]
    blocker_rows = [
        row for row in ap_rows if row["primary_disposition"] == "implementation_gap_blocker"
    ]
    rejected_rows = [
        row for row in ap_rows if row["primary_disposition"] == "unsafe_relabel_rejected"
    ]
    has_nat4 = bool(nat4_rows)
    if has_nat4 and ap["ap_level"] == "AP8":
        coverage_status = "nat4_present_for_limited_h4_l5_claim"
    elif has_nat4:
        coverage_status = "nat4_present_for_current_claim"
    elif nat3_rows:
        coverage_status = "nat4_absent_contract_only"
    elif blocker_rows:
        coverage_status = "nat4_absent_blocked"
    else:
        coverage_status = "nat4_absent"
    current_claim_nat4_supported = has_nat4
    generalization_note = "not_applicable"
    if ap["ap_level"] == "AP8":
        generalization_note = (
            "NAT4 evidence covers only N18's limited h4/L5 AP8 claim; h8, h16, "
            "and general AP8 remain blocked."
        )
    if ap["ap_level"] == "AP6" and has_nat4 and blocker_rows:
        generalization_note = (
            "Core AP6 boundary telemetry has NAT4 evidence, while original B4/C5 "
            "reverse-perspective backfill remains blocked."
        )
    if ap["ap_level"] == "AP7" and has_nat4 and blocker_rows:
        generalization_note = (
            "Core and scoped AP7 loop telemetry has NAT4 evidence, while general "
            "shared-medium reverse-perspective evidence remains blocked."
        )
    coverage = {
        "ap_level": ap["ap_level"],
        "source_experiment": ap["source_experiment"],
        "claimed_artifact_role": ap["claimed_artifact_role"],
        "claim_scope": ap["claim_scope"],
        "required_for_current_ladder": ap["required_for_current_ladder"],
        "candidate_row_ids": [row["row_id"] for row in ap_rows],
        "best_nat_level": best_nat_level(ap_rows),
        "nat4_row_ids": [row["row_id"] for row in nat4_rows],
        "nat3_row_ids": [row["row_id"] for row in nat3_rows],
        "implementation_gap_blocker_row_ids": [row["row_id"] for row in blocker_rows],
        "unsafe_relabel_rejected_row_ids": [row["row_id"] for row in rejected_rows],
        "nat4_evidence_present": has_nat4,
        "current_claim_nat4_supported": current_claim_nat4_supported,
        "coverage_status": coverage_status,
        "minimal_producer_code_needed_for_gaps": [
            {
                "row_id": row["row_id"],
                "surface": row["native_policy_or_telemetry_surface_name"],
                "minimal_producer_code_needed": row["minimal_producer_code_needed"],
                "blockers_to_next_level": row["blockers_to_next_level"],
            }
            for row in ap_rows
            if not row["phase8_ready"]
            and row["primary_disposition"]
            in {"native_contract_candidate", "implementation_gap_blocker"}
        ],
        "generalization_note": generalization_note,
    }
    if not has_nat4:
        coverage["nat4_gap_explanation"] = nat4_gap_explanation(ap["ap_level"], ap_rows)
    return coverage


def future_phase8_tasks(
    ap_coverage: list[dict[str, Any]],
    readiness_matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    source_to_ap = {
        row["source_experiment"]: row["ap_level"]
        for row in ap_coverage
    }
    for row in ap_coverage:
        if row["current_claim_nat4_supported"]:
            continue
        tasks.append(
            {
                "task_id": "phase8_upgrade_" + row["ap_level"].lower() + "_to_nat4",
                "ap_level": row["ap_level"],
                "reason": "current AP rung lacks NAT4 evidence",
                "required_before_native_ladder_generation": True,
                "minimal_producer_code_needed": row[
                    "minimal_producer_code_needed_for_gaps"
                ],
            }
        )
    for gap in readiness_matrix["implementation_gap_matrix"]:
        if gap["source_candidate_row_id"] in {
            "n19_i4_row_05_n16_original_b4c5_reverse_backfill_blocker",
            "n19_i5_row_06_n17_original_b4c5_general_shared_medium_blocker",
            "n19_i6_row_04_n18_h8_h16_general_ap8_extrapolation_blocker",
        }:
            tasks.append(
                {
                    "task_id": "phase8_optional_gap_" + gap["source_candidate_row_id"],
                    "ap_level": source_to_ap[gap["source_experiment"]],
                    "reason": "optional/generalization gap preserved by N19 closeout",
                    "required_before_native_ladder_generation": False,
                    "minimal_producer_code_needed": gap["minimal_producer_code_needed"],
                    "blocked_claims": gap["blocked_claims"],
                }
            )
    return tasks


def validate_closeout(
    candidate_matrix: dict[str, Any],
    readiness_matrix: dict[str, Any],
    candidate_rows: list[dict[str, Any]],
    ap_coverage: list[dict[str, Any]],
    closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    lacking_nat4 = [row["ap_level"] for row in ap_coverage if not row["nat4_evidence_present"]]
    checks = [
        {
            "check_id": "candidate_matrix_passed",
            "passed": candidate_matrix.get("status") == "passed",
            "detail": rel(CANDIDATE_MATRIX),
        },
        {
            "check_id": "phase8_readiness_matrix_passed",
            "passed": readiness_matrix.get("status") == "passed",
            "detail": rel(READINESS_MATRIX),
        },
        {
            "check_id": "ap_level_nat4_coverage_answered",
            "passed": [row["ap_level"] for row in ap_coverage]
            == ["AP3", "AP4", "AP5", "AP6", "AP7", "AP8"],
            "detail": {row["ap_level"]: row["coverage_status"] for row in ap_coverage},
        },
        {
            "check_id": "ap4_ap5_nat4_gaps_detected",
            "passed": lacking_nat4 == ["AP4", "AP5"],
            "detail": lacking_nat4,
        },
        {
            "check_id": "ap4_ap5_missing_evidence_explained",
            "passed": all(
                row["ap_level"] in {"AP4", "AP5"}
                and row.get("nat4_gap_explanation", {}).get("missing_for_nat4")
                and row.get("nat4_gap_explanation", {}).get(
                    "why_this_blocks_ladder_generation"
                )
                for row in ap_coverage
                if row["ap_level"] in {"AP4", "AP5"}
            ),
            "detail": {
                row["ap_level"]: row.get("nat4_gap_explanation", {}).get(
                    "missing_for_nat4", []
                )
                for row in ap_coverage
                if row["ap_level"] in {"AP4", "AP5"}
            },
        },
        {
            "check_id": "full_ladder_generation_blocked_when_any_ap_lacks_nat4",
            "passed": closeout["full_ap3_ap8_nat4_ladder_generation_supported"] is False
            and closeout["current_implementation_can_generate_claimed_ap_ladder"] is False,
            "detail": closeout["claimed_ladder_generation_status"],
        },
        {
            "check_id": "limited_ap8_boundary_preserved",
            "passed": any(
                row["ap_level"] == "AP8"
                and row["coverage_status"] == "nat4_present_for_limited_h4_l5_claim"
                and "general AP8 remain blocked" in row["generalization_note"]
                for row in ap_coverage
            ),
            "detail": "AP8 NAT4 is limited to h4/L5",
        },
        {
            "check_id": "future_phase8_tasks_named_without_implementation",
            "passed": bool(closeout["future_phase8_handoff_tasks"])
            and all(
                task.get("minimal_producer_code_needed") is not None
                for task in closeout["future_phase8_handoff_tasks"]
            ),
            "detail": len(closeout["future_phase8_handoff_tasks"]),
        },
        {
            "check_id": "unsafe_claim_flags_blocked",
            "passed": all_claim_flags_false(candidate_rows),
            "detail": len(candidate_rows),
        },
        {
            "check_id": "phase8_native_support_ap9_not_opened",
            "passed": closeout["phase8_opened"] is False
            and closeout["native_support_opened"] is False
            and closeout["ap9_opened"] is False,
            "detail": "N19 remains review/classification only",
        },
        {
            "check_id": "final_claim_ceiling_preserved",
            "passed": closeout["final_claim_ceiling"]
            == "artifact_level_phase8_readiness_review_for_ap3_ap8",
            "detail": closeout["final_claim_ceiling"],
        },
        {
            "check_id": "src_diff_empty",
            "passed": closeout["src_diff_empty"] is True,
            "detail": closeout["src_diff_empty"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(closeout),
            "detail": "closeout paths are relative",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 8 - Closeout And Handoff",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"final_claim_ceiling = {artifact['final_claim_ceiling']}",
        "full_ap3_ap8_nat4_ladder_generation_supported = "
        + str(artifact["full_ap3_ap8_nat4_ladder_generation_supported"]).lower(),
        "current_implementation_can_generate_claimed_ap_ladder = "
        + str(artifact["current_implementation_can_generate_claimed_ap_ladder"]).lower(),
        f"claimed_ladder_generation_status = {artifact['claimed_ladder_generation_status']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "AP-level NAT4 coverage:",
        "",
        "| AP | Source | Best NAT | NAT4 Evidence | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in artifact["ap_level_nat4_coverage"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["ap_level"],
                    row["source_experiment"],
                    row["best_nat_level"],
                    str(row["nat4_evidence_present"]).lower(),
                    row["coverage_status"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Main interpretation:",
            "",
            "```text",
            artifact["interpretation"]["main_read"],
            "```",
            "",
            "Implication:",
            "",
            "```text",
            artifact["interpretation"]["ladder_generation_implication"],
            "```",
            "",
            "AP4/AP5 NAT4 gaps:",
            "",
        ]
    )
    for row in artifact["ap_level_nat4_coverage"]:
        if row["ap_level"] not in {"AP4", "AP5"}:
            continue
        gap = row["nat4_gap_explanation"]
        lines.extend(
            [
                f"### {row['ap_level']} / {row['source_experiment']}",
                "",
                "Best current evidence:",
                "",
                "```text",
                gap["best_current_evidence"],
                "```",
                "",
                "Missing for NAT4:",
                "",
            ]
        )
        for item in gap["missing_for_nat4"]:
            lines.append(f"- {item}")
        lines.extend(
            [
                "",
                "Why this blocks ladder generation:",
                "",
                "```text",
                gap["why_this_blocks_ladder_generation"],
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "Future handoff tasks:",
            "",
            "| Task | AP | Required Before Native Ladder Generation |",
            "| --- | --- | --- |",
        ]
    )
    for task in artifact["future_phase8_handoff_tasks"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    task["task_id"],
                    task["ap_level"],
                    str(task["required_before_native_ladder_generation"]).lower(),
                ]
            )
            + " |"
        )
    lines.extend(
        [
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
    readiness_matrix = load_json(READINESS_MATRIX)
    candidate_rows = candidate_matrix["candidate_rows"]
    ap_coverage = [coverage_for_ap(ap, candidate_rows) for ap in AP_LEVELS]
    lacking_nat4 = [row["ap_level"] for row in ap_coverage if not row["nat4_evidence_present"]]
    full_ladder_ready = not lacking_nat4
    closeout_core = {
        "artifact_id": "n19_closeout_and_handoff",
        "schema_version": "n19_closeout_and_handoff_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 8,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Close N19 as a native-readiness review and answer whether every AP3-AP8 "
            "rung has NAT4 evidence sufficient for current native ladder generation."
        ),
        "candidate_matrix_source": {
            "path": rel(CANDIDATE_MATRIX),
            "sha256": sha256_file(CANDIDATE_MATRIX),
            "output_digest": candidate_matrix["output_digest"],
            "status": candidate_matrix["status"],
        },
        "phase8_readiness_matrix_source": {
            "path": rel(READINESS_MATRIX),
            "sha256": sha256_file(READINESS_MATRIX),
            "output_digest": readiness_matrix["output_digest"],
            "status": readiness_matrix["status"],
        },
        "final_supported_status": (
            "partial_phase8_readiness_review_with_ap4_ap5_nat4_generation_gaps"
        ),
        "final_claim_ceiling": "artifact_level_phase8_readiness_review_for_ap3_ap8",
        "ap_level_nat4_coverage": ap_coverage,
        "ap_levels_lacking_nat4_evidence": lacking_nat4,
        "full_ap3_ap8_nat4_ladder_generation_supported": full_ladder_ready,
        "current_implementation_can_generate_claimed_ap_ladder": full_ladder_ready,
        "claimed_ladder_generation_status": (
            "blocked_by_ap4_ap5_nat4_evidence_gaps"
            if not full_ladder_ready
            else "supported_for_current_claimed_ap_ladder"
        ),
        "phase8_ready_surfaces": readiness_matrix["phase8_ready_surfaces"],
        "phase8_ready_surface_count": readiness_matrix["readiness_summary"][
            "phase8_ready_surface_count"
        ],
        "non_ready_row_count": readiness_matrix["readiness_summary"]["non_ready_row_count"],
        "future_phase8_handoff_tasks": future_phase8_tasks(ap_coverage, readiness_matrix),
        "blocked_claims_preserved": [
            "native support",
            "Phase 8 implementation",
            "general AP8",
            "AP9",
            "agency",
            "choice",
            "intention",
            "semantic action",
            "semantic perception",
            "semantic goal ownership",
            "selfhood",
            "identity acceptance",
            "organism/life behavior",
            "fully native agentic-like integration",
            "unrestricted autonomy",
        ],
        "interpretation": {
            "main_read": (
                "N19 closes as a native-readiness review, not as native implementation. "
                "It finds 12 NAT4 Phase-8-ready surfaces, but the AP-level coverage gate "
                "fails for the full AP3-AP8 ladder because AP4/N14 and AP5/N15 do not "
                "yet have NAT4 evidence."
            ),
            "ladder_generation_implication": (
                "With the current implementations and source records, the claimed AP3-AP8 "
                "ladder cannot be generated as a complete NAT4 Phase-8-ready ladder. "
                "AP3, AP6, AP7, and limited AP8 have NAT4 evidence; AP4 and AP5 remain "
                "below NAT4 and must be upgraded before a current native ladder-generation "
                "claim is allowed."
            ),
            "ap8_boundary": (
                "AP8 coverage is limited to N18's h4/L5 claim. h8, h16, and general AP8 "
                "remain blocked and are not required for the limited AP8 row, but they "
                "remain future/generalization blockers."
            ),
            "ap4_ap5_gap_summary": (
                "AP4 is missing source-current route-conditioned support/regulation "
                "evidence and native route-selection telemetry. AP5 is missing native "
                "lower-stack input capture after AP3/AP4 native surfaces exist and a "
                "default-off native proxy derivation policy."
            ),
        },
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
        "src_diff_empty": src_diff_empty(),
        "output_digest": "pending",
    }
    checks = validate_closeout(
        candidate_matrix,
        readiness_matrix,
        candidate_rows,
        ap_coverage,
        closeout_core,
    )
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        **closeout_core,
        "status": "passed" if not failed_checks else "failed",
        "checks": checks,
        "failed_checks": failed_checks,
    }
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

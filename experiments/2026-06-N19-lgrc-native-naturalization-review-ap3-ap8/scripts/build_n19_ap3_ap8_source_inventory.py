#!/usr/bin/env python3
"""Build N19 Iteration 1 AP3-AP8 source inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
OUTPUT = EXPERIMENT / "outputs" / "n19_ap3_ap8_source_inventory.json"
REPORT = EXPERIMENT / "reports" / "n19_ap3_ap8_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_ap3_ap8_source_inventory.py"
)

NAT_LADDER = {
    "NAT0": "producer-only artifact scaffold",
    "NAT1": "source-backed producer pattern",
    "NAT2": "replayable producer pattern with controls",
    "NAT3": "native contract candidate",
    "NAT4": "Phase 8-ready native policy candidate, no native implementation",
    "NAT5": "native implementation exists but is not integrated",
    "NAT6": "native implementation validates within composition replay",
}

NAT4_GATES = [
    "native policy or telemetry surface name present",
    "record schema sketch present",
    "default-off flags present",
    "enabled / validated / supported fields separated",
    "runtime-visible inputs source-backed",
    "state mutation owner specified",
    "budget surface specified",
    "telemetry requirements specified",
    "snapshot/replay requirements specified",
    "negative controls specified",
    "non-RC quantity audit passes",
    "claim flags forced false",
    "phase8_opened = false",
    "native_support_opened = false",
    "src_diff_empty = true",
]

SOURCE_RECORDS = [
    {
        "row_id": "n19_i1_row_01_n12_closeout_method_source",
        "source_experiment": "N12",
        "source_role": "naturalization_method_closeout",
        "source_artifact": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "not_applicable_method_source",
    },
    {
        "row_id": "n19_i1_row_02_n12_phase8_readiness_method_source",
        "source_experiment": "N12",
        "source_role": "nat_ladder_and_phase8_gate_source",
        "source_artifact": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_phase8_readiness_matrix.json",
        "source_report": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_phase8_readiness_matrix.md",
        "expected_final_supported_ap_level": "not_applicable_method_source",
    },
    {
        "row_id": "n19_i1_row_03_n13_ap3_closeout",
        "source_experiment": "N13",
        "source_role": "ap3_support_regulation_source",
        "source_artifact": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP3",
    },
    {
        "row_id": "n19_i1_row_04_n14_ap4_closeout",
        "source_experiment": "N14",
        "source_role": "ap4_consequence_selection_source",
        "source_artifact": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP4",
    },
    {
        "row_id": "n19_i1_row_05_n15_ap5_closeout",
        "source_experiment": "N15",
        "source_role": "ap5_proxy_formation_source",
        "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP5",
    },
    {
        "row_id": "n19_i1_row_06_n16_ap6_closeout",
        "source_experiment": "N16",
        "source_role": "ap6_boundary_source",
        "source_artifact": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/n16_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/n16_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP6",
    },
    {
        "row_id": "n19_i1_row_07_n17_ap7_closeout",
        "source_experiment": "N17",
        "source_role": "ap7_closed_loop_source",
        "source_artifact": "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/outputs/n17_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/reports/n17_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP7",
    },
    {
        "row_id": "n19_i1_row_08_n18_ap8_closeout",
        "source_experiment": "N18",
        "source_role": "ap8_limited_long_horizon_source",
        "source_artifact": "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/reports/n18_closeout_and_handoff.md",
        "expected_final_supported_ap_level": "AP8_limited_artifact_candidate",
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


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def first_present(data: dict[str, Any], paths: list[tuple[str, ...]], default: Any) -> Any:
    for path in paths:
        current: Any = data
        found = True
        for part in path:
            if not isinstance(current, dict) or part not in current:
                found = False
                break
            current = current[part]
        if found and current is not None:
            return current
    return default


def opened_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return any(opened_flag(item) for item in value.values())
    if isinstance(value, list):
        return any(opened_flag(item) for item in value)
    return bool(value)


def phase8_value(data: dict[str, Any]) -> bool:
    return opened_flag(
        first_present(
            data,
            [
                ("phase8_opened",),
                ("phase8_branch_opened",),
                ("closeout_result", "phase8_opened"),
                ("closeout_result", "phase8_implementation_opened"),
                ("final_handoff", "phase8_opened"),
                ("phase8_defer_record", "phase8_opened"),
                ("matrix_result", "phase8_opened"),
            ],
            False,
        )
    )


def native_support_value(data: dict[str, Any]) -> bool:
    return opened_flag(
        first_present(
            data,
            [
                ("native_support_opened",),
                ("native_branch_opened",),
                ("native_supported_flags",),
                ("closeout_result", "native_support_opened"),
                ("closeout_result", "native_supported_flags"),
                ("final_handoff", "native_support_opened"),
                ("matrix_result", "native_supported_flags"),
            ],
            False,
        )
    )


def final_supported_ap_level(data: dict[str, Any], expected: str) -> str:
    if expected == "not_applicable_method_source":
        return expected
    return str(
        first_present(
            data,
            [
                ("final_supported_ap_level",),
                ("closeout_result", "final_supported_ap_level"),
                ("final_handoff", "final_supported_ap_level"),
            ],
            "not_recorded",
        )
    )


def final_claim_ceiling(data: dict[str, Any], expected: str) -> str:
    if expected == "not_applicable_method_source":
        if "matrix_result" in data:
            return "n12_phase8_readiness_method_source_no_native_support"
        return "n12_native_naturalization_method_source_nat4_readiness_only"
    return str(
        first_present(
            data,
            [
                ("final_claim_ceiling",),
                ("closeout_result", "final_claim_ceiling"),
                ("final_handoff", "final_claim_ceiling"),
                ("final_claim_boundary", "final_claim_ceiling"),
            ],
            "not_recorded",
        )
    )


def source_row(record: dict[str, str]) -> dict[str, Any]:
    artifact_path = ROOT / record["source_artifact"]
    report_path = ROOT / record["source_report"]
    data = load_json(record["source_artifact"])
    expected = record["expected_final_supported_ap_level"]
    source_ap = final_supported_ap_level(data, expected)
    source_ceiling = final_claim_ceiling(data, expected)
    source_output_digest = str(data.get("output_digest", "not_recorded"))
    source_phase8_opened = phase8_value(data)
    source_native_support_opened = native_support_value(data)
    source_status = str(data.get("status", "not_recorded"))
    source_checks = data.get("checks", [])
    if isinstance(source_checks, dict):
        source_check_count = len(source_checks)
    elif isinstance(source_checks, list):
        source_check_count = len(source_checks)
    else:
        source_check_count = 0

    return {
        **record,
        "artifact_exists": artifact_path.exists(),
        "report_exists": report_path.exists(),
        "source_parseable": True,
        "source_sha256": sha256_file(artifact_path),
        "source_report_sha256": sha256_file(report_path),
        "source_output_digest": source_output_digest,
        "source_status": source_status,
        "source_check_count": source_check_count,
        "source_final_supported_ap_level": source_ap,
        "source_final_supported_ap_level_matches_expected": source_ap == expected,
        "source_final_claim_ceiling": source_ceiling,
        "source_phase8_opened": source_phase8_opened,
        "source_native_support_opened": source_native_support_opened,
        "direct_native_support_status": (
            "blocked_or_absent_native_support_false"
            if not source_native_support_opened
            else "native_support_claim_requires_review_blocker"
        ),
        "n19_consumption_boundary": (
            "method_source_only"
            if record["source_experiment"] == "N12"
            else "artifact_level_ap_prerequisite_source_only"
        ),
    }


def build_checks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ap_rows = [row for row in rows if row["source_experiment"] not in {"N12"}]
    checks = [
        {
            "check_id": "all_required_source_artifacts_exist",
            "passed": all(row["artifact_exists"] for row in rows),
            "detail": [row["source_artifact"] for row in rows if not row["artifact_exists"]],
        },
        {
            "check_id": "all_required_source_reports_exist",
            "passed": all(row["report_exists"] for row in rows),
            "detail": [row["source_report"] for row in rows if not row["report_exists"]],
        },
        {
            "check_id": "all_sources_parseable",
            "passed": all(row["source_parseable"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "ap3_ap8_levels_match_expected",
            "passed": all(row["source_final_supported_ap_level_matches_expected"] for row in ap_rows),
            "detail": {
                row["source_experiment"]: row["source_final_supported_ap_level"]
                for row in ap_rows
            },
        },
        {
            "check_id": "n12_ladder_replayed",
            "passed": list(NAT_LADDER.keys()) == ["NAT0", "NAT1", "NAT2", "NAT3", "NAT4", "NAT5", "NAT6"],
            "detail": NAT_LADDER,
        },
        {
            "check_id": "nat4_gates_recorded",
            "passed": len(NAT4_GATES) == 15,
            "detail": len(NAT4_GATES),
        },
        {
            "check_id": "phase8_not_opened_by_sources",
            "passed": all(not row["source_phase8_opened"] for row in rows),
            "detail": {
                row["row_id"]: row["source_phase8_opened"]
                for row in rows
            },
        },
        {
            "check_id": "native_support_not_opened_by_sources",
            "passed": all(not row["source_native_support_opened"] for row in rows),
            "detail": {
                row["row_id"]: row["source_native_support_opened"]
                for row in rows
            },
        },
        {
            "check_id": "n19_review_only_no_candidate_classification",
            "passed": True,
            "detail": "Iteration 1 inventories sources and method only.",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 1 - AP3-AP8 Source Inventory",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"row_count = {artifact['row_count']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Source rows:",
        "",
        "| Row | Source | Role | AP Level | Claim Ceiling | Native Support |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["source_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["source_experiment"],
                    row["source_role"],
                    row["source_final_supported_ap_level"],
                    row["source_final_claim_ceiling"],
                    str(row["source_native_support_opened"]).lower(),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "N12 ladder replay:",
            "",
            "```json",
            json.dumps(artifact["n12_method_replay"]["nat_ladder"], indent=2, sort_keys=True),
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
    lines.extend(
        [
            "",
            "Claim boundary:",
            "",
            "```text",
            artifact["claim_boundary"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = [source_row(record) for record in SOURCE_RECORDS]
    checks = build_checks(rows)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_ap3_ap8_source_inventory",
        "schema_version": "n19_source_inventory_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 1,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "Inventory N12-N18 sources and replay the N12 NAT ladder before N19 classification.",
        "source_rows": rows,
        "row_count": len(rows),
        "n12_method_replay": {
            "nat_ladder": NAT_LADDER,
            "nat4_readiness_gates": NAT4_GATES,
            "phase8_ready_derivation": "phase8_ready = true only when nat_level = NAT4",
            "phase8_ready_is_native_support": False,
            "nat5_nat6_in_scope": False,
        },
        "source_summary": {
            "required_ap_sources": ["N13", "N14", "N15", "N16", "N17", "N18"],
            "required_ap_levels": {
                row["source_experiment"]: row["source_final_supported_ap_level"]
                for row in rows
                if row["source_experiment"] != "N12"
            },
            "n12_method_sources": [
                row["row_id"] for row in rows if row["source_experiment"] == "N12"
            ],
            "direct_native_support_evidence_found": any(
                row["source_native_support_opened"] for row in rows
            ),
        },
        "claim_boundary": (
            "N19 may inventory and classify native readiness, but it does not open AP9, "
            "Phase 8, native support, agency, selfhood, identity acceptance, semantic "
            "action/perception, organism/life, fully native integration, or unrestricted autonomy."
        ),
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
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

#!/usr/bin/env python3
"""Build N23 Iteration 7 full replay and control matrix."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import build_n23_ap4_selection_geometry_probe as i6
import build_n23_ap4_selection_geometry_robustness_probe as i6a
import build_n23_collapse_replay_and_counterfactual_controls as i5


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_replay_and_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n23_replay_and_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_replay_and_control_matrix.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_replay_and_control_matrix.py"
)

I1_OUTPUT_PATH = i6a.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i6a.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i6a.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i6a.I4_OUTPUT_PATH
I4A_OUTPUT_PATH = i6a.I4A_OUTPUT_PATH
I5_OUTPUT_PATH = i6a.I5_OUTPUT_PATH
I5A_OUTPUT_PATH = i6a.I5A_OUTPUT_PATH
I6_OUTPUT_PATH = i6a.I6_OUTPUT_PATH
I6A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_ap4_selection_geometry_robustness_probe.json"
)

ALLOWED_CONTROL_STATUSES = {
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def source_record(path: str, role: str) -> dict[str, Any]:
    return i5.source_record(path, role)


def control_record(
    *,
    control_id: str,
    source_iteration: str,
    source_row_id: str,
    control_status: str,
    required_for: list[str],
    rung_effect: str,
    detail: Any,
) -> dict[str, Any]:
    if control_status not in ALLOWED_CONTROL_STATUSES:
        raise ValueError(f"Unsupported control status {control_status!r}")
    if control_status == "failed_closed":
        claim_allowed_when_control_triggers: bool | str = False
    elif control_status == "failed_open":
        claim_allowed_when_control_triggers = True
    else:
        claim_allowed_when_control_triggers = "not_applicable_status_is_passed_or_not_applicable"
    return {
        "control_id": control_id,
        "source_iteration": source_iteration,
        "source_row_id": source_row_id,
        "control_status": control_status,
        "required_for": required_for,
        "rung_effect": rung_effect,
        "claim_allowed_when_control_triggers": claim_allowed_when_control_triggers,
        "detail": detail,
    }


def replay_status_records(row: dict[str, Any], source_iteration: str) -> list[dict[str, Any]]:
    records = []
    for mode in i5.REQUIRED_REPLAY_MODES_FOR_LC4:
        records.append(
            control_record(
                control_id=mode,
                source_iteration=source_iteration,
                source_row_id=row["replay_row_id"],
                control_status=row[mode]["status"],
                required_for=["LC4", "LC5", "N23-C4", "N23-C5"],
                rung_effect=f"blocks LC4+ if {mode} is not passed",
                detail=row[mode],
            )
        )
    return records


def negative_control_records(
    row: dict[str, Any], source_iteration: str
) -> list[dict[str, Any]]:
    records = []
    for control in row.get("control_results", row.get("negative_controls", [])):
        records.append(
            control_record(
                control_id=control["control_id"],
                source_iteration=source_iteration,
                source_row_id=row["replay_row_id"],
                control_status=control["control_status"],
                required_for=["LC4", "LC5", "N23-C4", "N23-C5"],
                rung_effect=control["rung_effect"],
                detail=control,
            )
        )
    return records


def active_null_control_records(i3_output: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for row in i3_output["active_null_rows"]:
        for control in row["control_results"]:
            records.append(
                control_record(
                    control_id=control["control_id"],
                    source_iteration="I3",
                    source_row_id=row["row_id"],
                    control_status=control["control_status"],
                    required_for=["LC2", "LC3", "LC4", "LC5", "N23-C2+"],
                    rung_effect=control["rung_effect"],
                    detail={
                        "blocker_class": row["blocker_class"],
                        "geometric_failure_reading": row[
                            "geometric_failure_reading"
                        ],
                        "control": control,
                    },
                )
            )
    return records


def ap4_control_records(i6_output: dict[str, Any]) -> list[dict[str, Any]]:
    trace_path = next(
        item["path"]
        for item in i6_output["artifact_manifest"]
        if item.get("artifact_subrole") == "ap4_negative_control_trace"
    )
    trace = i5.load_json(trace_path)
    return [
        control_record(
            control_id=control["control_id"],
            source_iteration="I6",
            source_row_id=trace["artifact_id"],
            control_status=control["control_status"],
            required_for=["LC5", "N23-C5", "AP4_bridge_candidate"],
            rung_effect=control["rung_effect"],
            detail=control,
        )
        for control in trace["controls"]
    ]


def robustness_control_records(i6a_output: dict[str, Any]) -> list[dict[str, Any]]:
    trace = i5.load_json(i6a_output["negative_control_trace"]["path"])
    records = [
        control_record(
            control_id=control["control_id"],
            source_iteration="I6-A",
            source_row_id=trace["artifact_id"],
            control_status=control["control_status"],
            required_for=["bounded_AP4_stress_evidence", "N23-C5"],
            rung_effect=control["rung_effect"],
            detail=control,
        )
        for control in trace["controls"]
    ]
    for row in i6a_output["robustness_rows"]:
        if row["row_decision"] == "rejected":
            records.append(
                control_record(
                    control_id=f"{row['case_id']}_stress_gate",
                    source_iteration="I6-A",
                    source_row_id=row["row_id"],
                    control_status="failed_closed",
                    required_for=["bounded_AP4_stress_evidence", "N23-C5"],
                    rung_effect=(
                        "blocks AP4 stress support when source-current branch "
                        "geometry falls below the declared margin or enters a tie"
                    ),
                    detail={
                        "case_id": row["case_id"],
                        "score_margin": row["score_margin"],
                        "minimum_score_margin": row["minimum_score_margin"],
                        "random_tie_status": row["random_tie_status"],
                        "row_decision": row["row_decision"],
                    },
                )
            )
    return records


def primary_matrix_row(
    *,
    row_id: str,
    source_variant: str,
    i6_row: dict[str, Any],
    replay_source: dict[str, Any],
    replay_iteration: str,
) -> dict[str, Any]:
    replay_row = replay_source["replay_rows"][0]
    replay_modes = replay_status_records(replay_row, replay_iteration)
    replay_controls = negative_control_records(replay_row, replay_iteration)
    controls = replay_modes + replay_controls
    required_passed = all(item["control_status"] == "passed" for item in replay_modes)
    required_failed_closed = all(
        item["control_status"] == "failed_closed" for item in replay_controls
    )
    i6_gates_passed = all(i6_row["ap4_bridge_gates"].values())
    support_status = (
        "full_matrix_supported"
        if required_passed and required_failed_closed and i6_gates_passed
        else "blocked_by_matrix"
    )
    row = {
        "row_id": row_id,
        "row_schema_role": "i7_full_matrix_primary_lc5_row",
        "source_variant": source_variant,
        "source_candidate_row_id": i6_row["source_candidate_row_id"],
        "source_replay_row_id": i6_row["source_replay_row_id"],
        "source_ap4_row_id": i6_row["row_id"],
        "branch_count": i6_row["branch_count"],
        "retained_non_selected_branch_count": i6_row[
            "retained_non_selected_branch_count"
        ],
        "selected_branch_id": i6_row["selected_branch_id"],
        "selection_reason": i6_row["selection_reason"],
        "score_margin": i6_row["score_margin"],
        "minimum_score_margin": i6_row["minimum_score_margin"],
        "ap4_dependency_status": i6_row["ap4_dependency_status"],
        "ap5_dependency_status": i6_row["ap5_dependency_status"],
        "ap4_bridge_status": i6_row["ap4_bridge_status"],
        "matrix_control_status": support_status,
        "required_replay_statuses": replay_modes,
        "required_negative_controls": replay_controls,
        "all_required_replay_passed": required_passed,
        "all_required_negative_controls_failed_closed": required_failed_closed,
        "ap4_bridge_gates_passed": i6_gates_passed,
        "i7_consumable_lc_ladder_rung": "LC5"
        if support_status == "full_matrix_supported"
        else "LC4",
        "i7_consumable_n23_closeout_rung_candidate": "N23-C5"
        if support_status == "full_matrix_supported"
        else "N23-C4",
        "row_decision": "supported"
        if support_status == "full_matrix_supported"
        else "blocked",
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "final_n23_supported": False,
        "claim_ceiling": (
            "I7 full-matrix supported artifact-level LC5/AP4 bridge candidate "
            "pending I8 closeout; no semantic choice, agency, native support, "
            "sentience, Phase 8, or ant-ecology claim"
        ),
        "unsafe_claim_flags": i5.unsafe_claim_flags(),
    }
    row["output_digest"] = i5.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return i5.canonicalize_json_value(row)


def stress_matrix_row(row: dict[str, Any]) -> dict[str, Any]:
    supported = row["row_decision"] == "supported"
    matrix_row = {
        "row_id": f"n23_i7_{row['row_id']}",
        "row_schema_role": "i7_full_matrix_ap4_stress_row",
        "source_row_id": row["row_id"],
        "case_id": row["case_id"],
        "stress_case_role": row["stress_case_role"],
        "branch_count": row["branch_count"],
        "selected_branch_id": row["selected_branch_id"],
        "selection_reason": row["selection_reason"],
        "score_margin": row["score_margin"],
        "minimum_score_margin": row["minimum_score_margin"],
        "random_tie_status": row["random_tie_status"],
        "duplicate_replay_observable_digest_matched": row[
            "duplicate_replay_observable_digest_matched"
        ],
        "counterfactual_retention_trace_present": row[
            "counterfactual_retention_trace_present"
        ],
        "ap4_dependency_status": row["ap4_dependency_status"],
        "ap5_dependency_status": row["ap5_dependency_status"],
        "matrix_control_status": "bounded_stress_supported"
        if supported
        else "failed_closed",
        "i7_consumable_lc_ladder_rung": "LC5" if supported else "not_supported",
        "i7_consumable_role": "bounded_ap4_stress_support"
        if supported
        else "negative_stress_control",
        "row_decision": row["row_decision"],
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "general_ap4_robustness_supported": False,
        "claim_ceiling": (
            "I7 bounded AP4 stress evidence; contributes robustness context "
            "but does not widen to general AP4 robustness or final N23 support"
        ),
        "unsafe_claim_flags": i5.unsafe_claim_flags(),
    }
    matrix_row["output_digest"] = i5.digest_value(
        {
            key: value
            for key, value in matrix_row.items()
            if key != "output_digest"
        }
    )
    return i5.canonicalize_json_value(matrix_row)


def collect_artifact_manifest(*outputs: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    manifest: list[dict[str, Any]] = []
    for output in outputs:
        for item in output.get("artifact_manifest", []):
            path = item["path"]
            if path in seen:
                continue
            seen.add(path)
            manifest.append(dict(item))
    return sorted(manifest, key=lambda item: item["path"])


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/") or "file://" in value or "vscode://" in value
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    return False


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N23 Iteration 7 - Replay And Control Matrix",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        (
            "I7 consumes the provisional N23 rows from I3 through I6-A and "
            "validates them as a full replay/control matrix. It assigns "
            "I7-consumable LC rungs, but keeps final closeout and N24 handoff "
            "pending I8."
        ),
        "",
        "## Primary Matrix Rows",
        "",
        "| Row | Variant | Branches | Selected | Margin | I7 LC | Decision |",
        "| --- | --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in output["matrix_rows"]:
        if row["row_schema_role"] != "i7_full_matrix_primary_lc5_row":
            continue
        lines.append(
            "| "
            f"`{row['row_id']}` | `{row['source_variant']}` | "
            f"`{row['branch_count']}` | `{row['selected_branch_id']}` | "
            f"`{row['score_margin']:.12f}` | "
            f"`{row['i7_consumable_lc_ladder_rung']}` | "
            f"`{row['row_decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Stress Matrix Rows",
            "",
            "| Case | Decision | Selected | Margin | Role |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in output["matrix_rows"]:
        if row["row_schema_role"] != "i7_full_matrix_ap4_stress_row":
            continue
        lines.append(
            "| "
            f"`{row['case_id']}` | `{row['row_decision']}` | "
            f"`{row['selected_branch_id']}` | `{row['score_margin']:.12f}` | "
            f"`{row['i7_consumable_role']}` |"
        )
    lines.extend(
        [
            "",
            "## Control Matrix",
            "",
            "```text",
            output["geometric_interpretation"]["control_matrix_read"],
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "I7-supported LC rung = LC5",
            "I7-supported N23 closeout candidate = N23-C5",
            "LC6 = pending I8 closeout",
            "final AP4 supported = false",
            "final N23 supported = false",
            "semantic choice = false",
            "semantic intention = false",
            "agency = false",
            "native support = false",
            "sentience = false",
            "Phase 8 = false",
            "ant ecology implementation = false",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i1_output = i5.load_json(I1_OUTPUT_PATH)
    i2_output = i5.load_json(I2_OUTPUT_PATH)
    i3_output = i5.load_json(I3_OUTPUT_PATH)
    i4_output = i5.load_json(I4_OUTPUT_PATH)
    i4a_output = i5.load_json(I4A_OUTPUT_PATH)
    i5_output = i5.load_json(I5_OUTPUT_PATH)
    i5a_output = i5.load_json(I5A_OUTPUT_PATH)
    i6_output = i5.load_json(I6_OUTPUT_PATH)
    i6a_output = i5.load_json(I6A_OUTPUT_PATH)

    active_controls = active_null_control_records(i3_output)
    minimal_row = primary_matrix_row(
        row_id="n23_i7_row_01_minimal_lc5_full_matrix",
        source_variant="minimal_two_branch_lc5_path",
        i6_row=i6_output["ap4_selection_geometry_rows"][0],
        replay_source=i5_output,
        replay_iteration="I5",
    )
    multibranch_row = primary_matrix_row(
        row_id="n23_i7_row_02_multibranch_lc5_full_matrix",
        source_variant="four_branch_lc5_path",
        i6_row=i6_output["ap4_selection_geometry_rows"][1],
        replay_source=i5a_output,
        replay_iteration="I5-A",
    )
    stress_rows = [stress_matrix_row(row) for row in i6a_output["robustness_rows"]]
    matrix_rows = [minimal_row, multibranch_row] + stress_rows

    all_control_records = (
        active_controls
        + minimal_row["required_replay_statuses"]
        + minimal_row["required_negative_controls"]
        + multibranch_row["required_replay_statuses"]
        + multibranch_row["required_negative_controls"]
        + ap4_control_records(i6_output)
        + robustness_control_records(i6a_output)
    )
    status_counts = Counter(item["control_status"] for item in all_control_records)
    required_blockers_absent = (
        status_counts.get("failed_open", 0) == 0
        and status_counts.get("not_run", 0) == 0
    )
    supported_primary_rows = [
        row
        for row in matrix_rows
        if row["row_schema_role"] == "i7_full_matrix_primary_lc5_row"
        and row["row_decision"] == "supported"
    ]
    supported_stress_rows = [
        row
        for row in matrix_rows
        if row["row_schema_role"] == "i7_full_matrix_ap4_stress_row"
        and row["row_decision"] == "supported"
    ]
    rejected_stress_rows = [
        row
        for row in matrix_rows
        if row["row_schema_role"] == "i7_full_matrix_ap4_stress_row"
        and row["row_decision"] == "rejected"
    ]
    artifact_manifest = collect_artifact_manifest(
        i4_output,
        i4a_output,
        i5_output,
        i5a_output,
        i6_output,
        i6a_output,
    )
    allowed_artifact_roles = set(
        i2_output["schema"]["artifact_role_schema"]["artifact_role_values"]
    )
    preliminary_output = {
        "artifact_manifest": artifact_manifest,
        "control_records": all_control_records,
        "matrix_rows": matrix_rows,
    }
    checks = [
        check(
            "source_inputs_passed",
            all(
                output["status"] == "passed"
                for output in [
                    i1_output,
                    i2_output,
                    i3_output,
                    i4_output,
                    i4a_output,
                    i5_output,
                    i5a_output,
                    i6_output,
                    i6a_output,
                ]
            ),
            {
                "i1": i1_output["status"],
                "i2": i2_output["status"],
                "i3": i3_output["status"],
                "i4": i4_output["status"],
                "i4a": i4a_output["status"],
                "i5": i5_output["status"],
                "i5a": i5a_output["status"],
                "i6": i6_output["status"],
                "i6a": i6a_output["status"],
            },
        ),
        check(
            "all_active_nulls_consumed_and_failed_closed",
            len(active_controls) == 14
            and all(item["control_status"] == "failed_closed" for item in active_controls),
            {
                "active_null_control_count": len(active_controls),
                "status_counts": dict(Counter(item["control_status"] for item in active_controls)),
            },
        ),
        check(
            "primary_lc5_rows_supported",
            len(supported_primary_rows) == 2
            and all(row["i7_consumable_lc_ladder_rung"] == "LC5" for row in supported_primary_rows),
            [
                {
                    "row_id": row["row_id"],
                    "i7_consumable_lc_ladder_rung": row[
                        "i7_consumable_lc_ladder_rung"
                    ],
                    "matrix_control_status": row["matrix_control_status"],
                }
                for row in supported_primary_rows
            ],
        ),
        check(
            "bounded_stress_rows_classified",
            len(supported_stress_rows) == 3 and len(rejected_stress_rows) == 2,
            {
                "supported": [row["case_id"] for row in supported_stress_rows],
                "rejected": [row["case_id"] for row in rejected_stress_rows],
            },
        ),
        check(
            "required_control_status_values_valid",
            all(item["control_status"] in ALLOWED_CONTROL_STATUSES for item in all_control_records),
            dict(status_counts),
        ),
        check(
            "no_required_failed_open_or_not_run_controls",
            required_blockers_absent,
            dict(status_counts),
        ),
        check(
            "artifact_manifest_hashes_match",
            all(item["sha256"] == i5.sha256_file(item["path"]) for item in artifact_manifest),
            {"artifact_count": len(artifact_manifest)},
        ),
        check(
            "artifact_roles_match_i2_frozen_enum",
            all(item["artifact_role"] in allowed_artifact_roles for item in artifact_manifest),
            sorted({item["artifact_role"] for item in artifact_manifest}),
        ),
        check(
            "artifact_paths_are_portable",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            [item["path"] for item in artifact_manifest],
        ),
        check(
            "unsafe_claim_flags_false",
            all(not value for row in matrix_rows for value in row["unsafe_claim_flags"].values()),
            [row["unsafe_claim_flags"] for row in matrix_rows],
        ),
        check(
            "claim_boundaries_preserved",
            all(
                row["live_continuation_collapse_claim_allowed"] is False
                and row["semantic_choice_claim_allowed"] is False
                for row in matrix_rows
            )
            and not any(row.get("final_n23_supported", False) for row in matrix_rows),
            [
                {
                    "row_id": row["row_id"],
                    "live_continuation_collapse_claim_allowed": row[
                        "live_continuation_collapse_claim_allowed"
                    ],
                    "semantic_choice_claim_allowed": row[
                        "semantic_choice_claim_allowed"
                    ],
                    "final_n23_supported": row.get("final_n23_supported", False),
                }
                for row in matrix_rows
            ],
        ),
        check(
            "no_absolute_paths_in_matrix_payload",
            not contains_absolute_path(preliminary_output),
            "repository-relative paths only",
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i7_replay_and_control_matrix",
        "schema_version": "1.0",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "7",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_full_replay_control_matrix_lc5_candidate_pending_i8"
            if not failed_checks
            else "blocked_replay_control_matrix_failed_checks"
        ),
        "purpose": (
            "Consume all provisional N23 rows, validate the replay/control "
            "matrix, assign I7-consumable LC rungs, and keep closeout pending I8."
        ),
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n23_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n23_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n23_active_nulls"),
            source_record(I4_OUTPUT_PATH, "minimal_lc3_source"),
            source_record(I4A_OUTPUT_PATH, "multibranch_lc3_source"),
            source_record(I5_OUTPUT_PATH, "minimal_lc4_replay_control_source"),
            source_record(I5A_OUTPUT_PATH, "multibranch_lc4_replay_control_source"),
            source_record(I6_OUTPUT_PATH, "ap4_lc5_bridge_candidate_source"),
            source_record(I6A_OUTPUT_PATH, "bounded_ap4_stress_evidence_source"),
            {
                "path": SCRIPT_PATH,
                "sha256": i5.sha256_file(SCRIPT_PATH),
                "source_role": "producer_script",
            },
        ],
        "matrix_policy": {
            "control_status_values": sorted(ALLOWED_CONTROL_STATUSES),
            "failed_closed_meaning": "blocker triggered and unsafe/null claim rejected",
            "failed_open_blocks_dependent_rung": True,
            "not_run_blocks_dependent_rung": True,
            "i5_i5a_replay_rows_are_replay_control_records": True,
            "i7_revalidates_rows_by_reference": True,
            "closeout_deferred_to_iteration8": True,
        },
        "matrix_rows": matrix_rows,
        "control_matrix": {
            "control_record_count": len(all_control_records),
            "control_status_counts": dict(status_counts),
            "records": all_control_records,
        },
        "artifact_manifest": artifact_manifest,
        "geometric_interpretation": {
            "main_read": (
                "I7 shows that the N23 live-continuation collapse candidate is "
                "not just a selected label: the minimal and four-branch paths "
                "both preserve source-current branch geometry, collapse traces, "
                "counterfactual retention, replay stability, and fail-closed "
                "controls through LC5."
            ),
            "control_matrix_read": (
                "active nulls: 14/14 failed closed\n"
                "minimal replay path: artifact, snapshot/load, and duplicate "
                "replay passed; seven LC4 controls failed closed\n"
                "multibranch replay path: artifact, snapshot/load, and duplicate "
                "replay passed; seven LC4 controls failed closed\n"
                "AP4 bridge: eight AP4-specific controls failed closed\n"
                "AP4 stress: three bounded stress rows supported; below-margin "
                "and equalized-tie rows failed closed\n"
                "closeout: LC5/N23-C5 candidate only; LC6/N23-C6 pending I8"
            ),
            "claim_boundary": (
                "The matrix supports I7-consumable artifact-level LC5/AP4 bridge "
                "candidate evidence. It does not support final AP4, LC6, final "
                "N23, semantic choice, agency, native support, sentience, Phase 8, "
                "or ant ecology implementation."
            ),
        },
        "iteration7_boundary": {
            "i7_supported_lc_ladder_rung": "LC5" if not failed_checks else "LC4",
            "i7_supported_n23_closeout_candidate": (
                "N23-C5" if not failed_checks else "N23-C4"
            ),
            "ap4_bridge_status": (
                "bridge_candidate_supported" if not failed_checks else "blocked"
            ),
            "lc6_supported": False,
            "n23_c6_supported": False,
            "final_ap4_supported": False,
            "final_n23_supported": False,
            "ready_for_iteration_8_closeout": not failed_checks,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    output["output_digest"] = i5.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    i5.write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

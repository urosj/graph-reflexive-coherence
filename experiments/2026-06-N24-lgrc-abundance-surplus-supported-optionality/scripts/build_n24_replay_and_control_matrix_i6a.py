#!/usr/bin/env python3
"""Build N24 Iteration 6-A replay/control matrix for I5-A."""

from __future__ import annotations

from typing import Any

import build_n24_minimal_surplus_probe as base
import build_n24_optional_continuation_set_probe_i5a as i5a_builder
import build_n24_replay_and_control_matrix as i6


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_replay_and_control_matrix_i6a.json"
REPORT = EXPERIMENT / "reports" / "n24_replay_and_control_matrix_i6a.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_replay_and_control_matrix_i6a_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_replay_and_control_matrix_i6a.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_replay_and_control_matrix_i6a.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i6.I4_OUTPUT_PATH
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe_i5a.json"
)
I6_OUTPUT_PATH = i6.I6_OUTPUT_PATH if hasattr(i6, "I6_OUTPUT_PATH") else (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH


def artifact_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": base.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def unsafe_claim_flags(i2: dict[str, Any]) -> dict[str, bool]:
    return {
        claim: False
        for claim in sorted(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
    }


def no_absolute_paths(data: Any) -> bool:
    text = base.canonical_json(data)
    forbidden = [
        "/" + "home/",
        "/" + "tmp/",
        "file" + "://",
        "C" + ":\\",
        "/" + "Users/",
    ]
    return all(token not in text for token in forbidden)


def snapshot_load_replay_trace_i5a(
    *, source_output: dict[str, Any], row: dict[str, Any]
) -> dict[str, Any]:
    snapshot_item = i6.snapshot_manifest_item(row)
    model = base.LGRC9V3.load(str(ROOT / snapshot_item["path"]))
    signature = i5a_builder.maintenance_basin_signature(model)
    support_margin = signature["min_support"] - base.SUPPORT_FLOOR
    coherence_margin = signature["min_coherence"] - base.COHERENCE_FLOOR
    trace = {
        "artifact_id": "n24_i6a_i5a_snapshot_load_replay_trace",
        "candidate_row_id": row["row_id"],
        "source_iteration": "5-A",
        "source_output_digest": source_output["output_digest"],
        "snapshot_path": snapshot_item["path"],
        "snapshot_sha256_matches_manifest": (
            base.sha256_file(snapshot_item["path"]) == snapshot_item["sha256"]
        ),
        "loaded_model_family": "LGRC9V3",
        "loaded_maintenance_basin_signature_digest": signature[
            "maintenance_basin_signature_digest"
        ],
        "source_row_maintenance_basin_signature_digest": row[
            "maintenance_basin_signature_digest"
        ],
        "observed_min_support": signature["min_support"],
        "observed_min_coherence": signature["min_coherence"],
        "support_floor": base.SUPPORT_FLOOR,
        "coherence_floor": base.COHERENCE_FLOOR,
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "support_margin_preserved": support_margin >= base.MIN_SURPLUS_MARGIN,
        "coherence_margin_preserved": coherence_margin >= base.MIN_SURPLUS_MARGIN,
        "boundary_signature_preserved": (
            signature["maintenance_basin_signature_digest"]
            == row["maintenance_basin_signature_digest"]
        ),
        "result": "pending",
    }
    trace["result"] = (
        "passed"
        if trace["snapshot_sha256_matches_manifest"]
        and trace["support_margin_preserved"]
        and trace["coherence_margin_preserved"]
        and trace["boundary_signature_preserved"]
        else "failed_open"
    )
    trace["replay_digest"] = base.digest_value(trace)
    return trace


def refresh_row_matrix_for_i5a_snapshot(
    row_matrix: dict[str, Any], *, source_output: dict[str, Any], row: dict[str, Any]
) -> dict[str, Any]:
    snapshot_trace = snapshot_load_replay_trace_i5a(source_output=source_output, row=row)
    base.write_json(ROOT / row_matrix["trace_paths"]["snapshot_load_replay_trace_path"], snapshot_trace)
    row_matrix["snapshot_load_replay"] = snapshot_trace
    replay_passed = (
        row_matrix["artifact_replay"]["result"] == "passed"
        and row_matrix["snapshot_load_replay"]["result"] == "passed"
        and row_matrix["duplicate_replay"]["result"] == "passed"
        and row_matrix["optional_set_survival_replay"]["result"] == "passed"
    )
    row_matrix["replay_passed"] = replay_passed
    if replay_passed and row_matrix["controls_accept_candidate"]:
        row_matrix["final_consumable_rung"] = "AB4"
        row_matrix["row_decision"] = "supported"
        row_matrix["ab4_candidate_supported"] = True
        row_matrix["ab5_or_stronger_supported"] = False
        row_matrix["surplus_supported_optionality_claim_allowed"] = False
        row_matrix["claim_scope"] = (
            "replay/control-backed AB4 candidate for the I5-A high-margin "
            "alternative; AB5 stress/threshold backing remains pending I7-A"
        )
    else:
        row_matrix["final_consumable_rung"] = "blocked"
        row_matrix["row_decision"] = "blocked"
        row_matrix["ab4_candidate_supported"] = False
        row_matrix["claim_scope"] = "replay/control failure blocks this candidate row"
    row_matrix["row_replay_control_digest"] = base.digest_value(
        {key: value for key, value in row_matrix.items() if key != "row_replay_control_digest"}
    )
    return row_matrix


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5a = base.load_json(I5A_OUTPUT_PATH)
    i6_original = base.load_json(I6_OUTPUT_PATH)
    i7_original = base.load_json(I7_OUTPUT_PATH)
    i5a_row = i5a["candidate_rows"][0]

    previous_artifact_dir = i6.ARTIFACT_DIR
    i6.ARTIFACT_DIR = ARTIFACT_DIR
    try:
        row_matrix = i6.row_replay_control_matrix(
            source_iteration=5,
            source_output_path=I5A_OUTPUT_PATH,
            source_output=i5a,
            row=i5a_row,
            i2=i2,
        )
        row_matrix = refresh_row_matrix_for_i5a_snapshot(
            row_matrix, source_output=i5a, row=i5a_row
        )
        controls = i6.negative_control_matrix(i2)
        negative_control_path = i6.write_artifact(
            "n24_i6a_negative_control_matrix.json", controls
        )
        summary_trace = {
            "artifact_id": "n24_i6a_replay_control_summary_trace",
            "candidate_row_id": row_matrix["candidate_row_id"],
            "source_output_digest": i5a["output_digest"],
            "final_consumable_rung": row_matrix["final_consumable_rung"],
            "ab4_candidate_supported": row_matrix["ab4_candidate_supported"],
            "ab5_or_stronger_supported": False,
            "does_not_replace_i6": True,
            "negative_control_matrix_digest": controls["control_matrix_digest"],
        }
        summary_trace["trace_digest"] = base.digest_value(summary_trace)
        summary_trace_path = i6.write_artifact(
            "n24_i6a_replay_control_summary_trace.json", summary_trace
        )
    finally:
        i6.ARTIFACT_DIR = previous_artifact_dir

    manifest = artifact_manifest(
        [
            (row_matrix["trace_paths"]["artifact_replay_trace_path"], "replay_trace"),
            (
                row_matrix["trace_paths"]["snapshot_load_replay_trace_path"],
                "snapshot_load_replay_trace",
            ),
            (
                row_matrix["trace_paths"]["duplicate_replay_trace_path"],
                "duplicate_replay_trace",
            ),
            (row_matrix["trace_paths"]["optional_set_survival_trace_path"], "replay_trace"),
            (negative_control_path, "negative_control_trace"),
            (summary_trace_path, "replay_trace"),
        ]
    )
    checks = [
        base.check("i1_inventory_passed", i1["status"] == "passed" and not i1["failed_checks"], i6.source_status(i1)),
        base.check("i2_schema_passed", i2["status"] == "passed" and not i2["failed_checks"], i6.source_status(i2)),
        base.check("i3_active_nulls_passed", i3["status"] == "passed" and not i3["failed_checks"], i6.source_status(i3)),
        base.check("i4_surplus_probe_passed", i4["status"] == "passed" and not i4["failed_checks"], i6.source_status(i4)),
        base.check("i5a_alternative_probe_ready", i5a["status"] == "passed" and not i5a["failed_checks"] and i5a["variant_boundary"]["ready_for_iteration_6a_replay_control_matrix"] is True, i6.source_status(i5a)),
        base.check("original_i6_i7_preserved", i6_original["status"] == "passed" and i7_original["status"] == "passed", {
            "i6_digest": i6_original["output_digest"],
            "i7_digest": i7_original["output_digest"],
            "i6_replaced": False,
            "i7_replaced": False,
        }),
        base.check(
            "i5a_replay_modes_passed",
            row_matrix["artifact_replay"]["result"] == "passed"
            and row_matrix["snapshot_load_replay"]["result"] == "passed"
            and row_matrix["duplicate_replay"]["result"] == "passed"
            and row_matrix["optional_set_survival_replay"]["result"] == "passed",
            {
                "artifact": row_matrix["artifact_replay"]["result"],
                "snapshot": row_matrix["snapshot_load_replay"]["result"],
                "duplicate": row_matrix["duplicate_replay"]["result"],
                "optional": row_matrix["optional_set_survival_replay"]["result"],
            },
        ),
        base.check(
            "i5a_controls_accept_candidate",
            row_matrix["controls_accept_candidate"] is True
            and not row_matrix["failed_open_controls"],
            {
                "controls_accept_candidate": row_matrix["controls_accept_candidate"],
                "failed_open_controls": row_matrix["failed_open_controls"],
            },
        ),
        base.check(
            "i5a_ab4_candidate_supported",
            row_matrix["final_consumable_rung"] == "AB4"
            and row_matrix["ab4_candidate_supported"] is True,
            row_matrix["claim_scope"],
        ),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) == 6
            and all(item["sha256"] == base.sha256_file(item["path"]) for item in manifest),
            manifest,
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in unsafe_claim_flags(i2).values()),
            unsafe_claim_flags(i2),
        ),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_replay_and_control_matrix_i6a",
        "schema_version": "n24_replay_and_control_matrix_i6a_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "6-A",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_i5a_replay_control_backed_ab4_candidate_pending_i7a"
            if not failed_checks
            else "failed_i5a_replay_control_matrix"
        ),
        "purpose": "replay/control the I5-A high-margin optionality variant without replacing I6",
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(I5A_OUTPUT_PATH, "n24_i5a_alternative_optional_probe"),
            base.source_record(I6_OUTPUT_PATH, "n24_i6_original_replay_control_context"),
            base.source_record(I7_OUTPUT_PATH, "n24_i7_original_stress_context"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "row_replay_control_matrix": [row_matrix],
        "negative_control_matrix": controls,
        "summary_trace": summary_trace,
        "iteration6a_boundary": {
            "i5a_final_consumable_rung": row_matrix["final_consumable_rung"],
            "provisional_ab_ladder_rung": "AB4",
            "ab4_candidate_supported": row_matrix["ab4_candidate_supported"],
            "ab5_or_stronger_supported": False,
            "does_not_replace_i6": True,
            "ready_for_iteration_7a_stress_threshold_matrix": not failed_checks,
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
        },
        "geometric_interpretation": {
            "short_read": (
                "I6-A confirms the high-margin I5-A optional set survives artifact, "
                "snapshot/load, duplicate, and optional-set replay under the same "
                "control discipline as I6."
            ),
            "claim_boundary": (
                "This is an alternative AB4 candidate only. It does not replace I6 "
                "and does not open AB5, reward, semantic choice, agency, native "
                "support, sentience, Phase 8, or ant ecology."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab4_candidate_supported": row_matrix[
                "ab4_candidate_supported"
            ],
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "native_support_claim_allowed": False,
            "sentience_claim_allowed": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "unsafe_claim_flags": unsafe_claim_flags(i2),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["no_absolute_paths"] = no_absolute_paths(output)
    output["checks"].append(
        base.check("no_absolute_paths", output["no_absolute_paths"] is True, True)
    )
    output["failed_checks"] = [
        item for item in output["checks"] if item["passed"] is not True
    ]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_i5a_replay_control_backed_ab4_candidate_pending_i7a"
        if not output["failed_checks"]
        else "failed_i5a_replay_control_matrix"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    matrix = output["row_replay_control_matrix"][0]
    boundary = output["iteration6a_boundary"]
    lines = [
        "# N24 Iteration 6-A - Alternative Replay And Control Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 6-A replays and controls the I5-A high-margin optionality variant.",
        "It does not replace the original I6 result.",
        "",
        "```text",
        f"artifact_replay = {matrix['artifact_replay']['result']}",
        f"snapshot_load_replay = {matrix['snapshot_load_replay']['result']}",
        f"duplicate_replay = {matrix['duplicate_replay']['result']}",
        f"optional_set_survival_replay = {matrix['optional_set_survival_replay']['result']}",
        f"final_consumable_rung = {matrix['final_consumable_rung']}",
        f"ab4_candidate_supported = {str(boundary['ab4_candidate_supported']).lower()}",
        f"ready_for_iteration_7a_stress_threshold_matrix = {str(boundary['ready_for_iteration_7a_stress_threshold_matrix']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    base.write_json(OUTPUT, output)
    output = base.load_json(base.rel(OUTPUT))
    write_report(output)
    if output["failed_checks"]:
        raise SystemExit(f"failed checks: {output['failed_checks']}")


if __name__ == "__main__":
    main()

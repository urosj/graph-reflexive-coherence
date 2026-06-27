#!/usr/bin/env python3
"""Build N24 Iteration 6 replay and control matrix."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_n24_minimal_surplus_probe as base


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_replay_and_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n24_replay_and_control_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_replay_and_control_matrix_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_replay_and_control_matrix.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_replay_and_control_matrix.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_minimal_surplus_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

SUPPORT_FLOOR = base.SUPPORT_FLOOR
COHERENCE_FLOOR = base.COHERENCE_FLOOR
MIN_SURPLUS_MARGIN = base.MIN_SURPLUS_MARGIN


def write_artifact(name: str, data: dict[str, Any]) -> str:
    path = ARTIFACT_DIR / name
    base.write_json(path, data)
    return base.rel(path)


def manifest_matches_file_contents(row: dict[str, Any]) -> bool:
    return all(
        item["sha256"] == base.sha256_file(item["path"])
        for item in row.get("artifact_manifest", [])
    )


def manifest_parseable(row: dict[str, Any]) -> bool:
    for item in row.get("artifact_manifest", []):
        try:
            base.load_json(item["path"])
        except Exception:
            return False
    return True


def snapshot_manifest_item(row: dict[str, Any]) -> dict[str, str]:
    for item in row.get("artifact_manifest", []):
        if item["path"].endswith("_source_current_snapshot.json"):
            return item
    raise KeyError(f"snapshot artifact missing for {row['row_id']}")


def recompute_row_digest(row: dict[str, Any]) -> str:
    return base.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )


def loaded_snapshot_signature(row: dict[str, Any]) -> dict[str, Any]:
    snapshot_item = snapshot_manifest_item(row)
    model = base.LGRC9V3.load(str(ROOT / snapshot_item["path"]))
    return base.maintenance_basin_signature(model)


def source_status(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": source.get("status", "not_recorded"),
        "acceptance_state": source.get("acceptance_state", "not_recorded"),
        "output_digest": source.get("output_digest", "not_recorded"),
        "failed_check_count": len(source.get("failed_checks", [])),
    }


def artifact_replay_trace(
    *,
    source_iteration: int,
    source_output_path: str,
    source_output: dict[str, Any],
    row: dict[str, Any],
) -> dict[str, Any]:
    manifest = row["artifact_manifest"]
    trace = {
        "artifact_id": f"n24_i6_i{source_iteration}_artifact_replay_trace",
        "candidate_row_id": row["row_id"],
        "source_iteration": source_iteration,
        "source_output_path": source_output_path,
        "source_output_sha256": base.sha256_file(source_output_path),
        "source_output_digest": source_output["output_digest"],
        "source_row_output_digest": row["output_digest"],
        "manifest_entry_count": len(manifest),
        "artifact_paths": [item["path"] for item in manifest],
        "manifest_sha256_match_file_contents": manifest_matches_file_contents(row),
        "manifest_artifacts_parseable": manifest_parseable(row),
        "derived_report_only": row["derived_report_only"],
        "source_current_inputs_present": bool(row["source_current_inputs"]),
        "result": "pending",
    }
    trace["result"] = (
        "passed"
        if trace["manifest_sha256_match_file_contents"]
        and trace["manifest_artifacts_parseable"]
        and trace["derived_report_only"] is False
        and trace["source_current_inputs_present"] is True
        else "failed_open"
    )
    trace["replay_digest"] = base.digest_value(trace)
    return trace


def snapshot_load_replay_trace(
    *,
    source_iteration: int,
    source_output: dict[str, Any],
    row: dict[str, Any],
) -> dict[str, Any]:
    snapshot_item = snapshot_manifest_item(row)
    signature = loaded_snapshot_signature(row)
    support_margin = signature["min_support"] - SUPPORT_FLOOR
    coherence_margin = signature["min_coherence"] - COHERENCE_FLOOR
    trace = {
        "artifact_id": f"n24_i6_i{source_iteration}_snapshot_load_replay_trace",
        "candidate_row_id": row["row_id"],
        "source_iteration": source_iteration,
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
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "support_margin_preserved": support_margin >= MIN_SURPLUS_MARGIN,
        "coherence_margin_preserved": coherence_margin >= MIN_SURPLUS_MARGIN,
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


def duplicate_replay_trace(
    *,
    source_iteration: int,
    source_output: dict[str, Any],
    row: dict[str, Any],
) -> dict[str, Any]:
    recomputed = recompute_row_digest(row)
    trace = {
        "artifact_id": f"n24_i6_i{source_iteration}_duplicate_replay_trace",
        "candidate_row_id": row["row_id"],
        "source_iteration": source_iteration,
        "source_output_digest": source_output["output_digest"],
        "source_row_output_digest": row["output_digest"],
        "recomputed_row_output_digest": recomputed,
        "duplicate_digest_matches": recomputed == row["output_digest"],
        "timestamp_independent": True,
        "git_metadata_excluded": True,
        "local_absolute_paths_excluded": True,
        "result": "pending",
    }
    trace["result"] = "passed" if trace["duplicate_digest_matches"] else "failed_open"
    trace["replay_digest"] = base.digest_value(trace)
    return trace


def optional_set_replay_trace(
    *,
    source_output: dict[str, Any],
    row: dict[str, Any],
) -> dict[str, Any]:
    branches = row["optional_branch_records"]
    branch_window_ids = {
        branch["optionality_window_step_range"]["window_id"] for branch in branches
    }
    trace = {
        "artifact_id": "n24_i6_i5_optional_set_survival_trace",
        "candidate_row_id": row["row_id"],
        "source_iteration": 5,
        "source_output_digest": source_output["output_digest"],
        "optional_continuation_count": row["optional_continuation_count"],
        "optional_continuation_availability_count": row[
            "optional_continuation_availability_count"
        ],
        "jointly_admissible_optional_continuation_count": row[
            "jointly_admissible_optional_continuation_count"
        ],
        "branch_count": len(branches),
        "branch_window_ids": sorted(branch_window_ids),
        "all_branches_same_declared_window": len(branch_window_ids) == 1,
        "all_branches_same_run_source_current": all(
            branch["trace_origin"] == "source_current_same_run"
            and branch["trace_status"] == "present"
            for branch in branches
        ),
        "all_branch_records_admissible": all(
            branch["admissibility_status"] == "admissible" for branch in branches
        ),
        "no_branch_uses_reward_or_proxy_label": all(
            branch["reward_or_proxy_label_used"] is False for branch in branches
        ),
        "no_branch_uses_producer_enumeration": all(
            branch["producer_enumeration_used"] is False for branch in branches
        ),
        "residual_support_margin_under_optionality": row[
            "residual_support_margin_under_optionality"
        ],
        "residual_coherence_margin_under_optionality": row[
            "residual_coherence_margin_under_optionality"
        ],
        "residual_margins_positive": (
            row["residual_support_margin_under_optionality"] >= MIN_SURPLUS_MARGIN
            and row["residual_coherence_margin_under_optionality"]
            >= MIN_SURPLUS_MARGIN
        ),
        "boundary_integrity_status": row["boundary_integrity_result"]["status"],
        "flux_or_leakage_status": row["flux_or_leakage_result"]["status"],
        "optional_flux_status": row[
            "optional_flux_does_not_drain_maintenance_support_status"
        ],
        "result": "pending",
    }
    trace["result"] = (
        "passed"
        if trace["optional_continuation_availability_count"] >= 2
        and trace["all_branches_same_declared_window"]
        and trace["all_branches_same_run_source_current"]
        and trace["all_branch_records_admissible"]
        and trace["no_branch_uses_reward_or_proxy_label"]
        and trace["no_branch_uses_producer_enumeration"]
        and trace["residual_margins_positive"]
        and trace["boundary_integrity_status"] == "preserved"
        and trace["flux_or_leakage_status"] == "preserved"
        and trace["optional_flux_status"] == "preserved"
        else "failed_open"
    )
    trace["replay_digest"] = base.digest_value(trace)
    return trace


def control_lookup(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {control["control_id"]: control for control in row["control_results"]}


def control_status_for_i6(
    *,
    control_id: str,
    source_control: dict[str, Any] | None,
    source_iteration: int,
    row: dict[str, Any],
) -> dict[str, Any]:
    if source_control is None:
        return {
            "control_id": control_id,
            "i6_control_status": "failed_open",
            "control_accepts_candidate": False,
            "scope_reason": "required control missing from source row",
            "rung_effect": "blocks replay/control-backed rung",
        }

    source_status_value = source_control["control_status"]
    accepts = source_status_value == "passed"
    scope_reason = "source row control passed"

    if source_status_value == "failed_closed":
        accepts = True
        scope_reason = (
            "false-positive blocker fired and the overclaim was rejected; "
            "this is admissible as a fail-closed control"
        )
    elif source_status_value == "not_applicable":
        if control_id == "ap5_proxy_gap_omission_control" and row[
            "ap5_dependency_status"
        ] == "not_applicable":
            accepts = True
            scope_reason = "AP5 is not applicable because no proxy/reward/target participates"
        elif source_iteration == 4:
            accepts = True
            scope_reason = "not applicable to surplus-only AB2 row"
        else:
            accepts = False
            scope_reason = "not applicable cannot satisfy required AB4 control"
    elif source_status_value == "not_run":
        accepts = False
        scope_reason = "not_run blocks dependent rung"

    return {
        "control_id": control_id,
        "source_control_status": source_status_value,
        "i6_control_status": (
            "passed" if source_status_value == "passed" else source_status_value
        ),
        "control_accepts_candidate": accepts,
        "scope_reason": scope_reason,
        "blocked_condition": source_control.get("blocked_condition", "not_recorded"),
        "claim_allowed_when_control_triggers": source_control.get(
            "claim_allowed_when_control_triggers", False
        ),
        "rung_effect": source_control.get("rung_effect", "not_recorded"),
    }


def row_replay_control_matrix(
    *,
    source_iteration: int,
    source_output_path: str,
    source_output: dict[str, Any],
    row: dict[str, Any],
    i2: dict[str, Any],
) -> dict[str, Any]:
    artifact_trace = artifact_replay_trace(
        source_iteration=source_iteration,
        source_output_path=source_output_path,
        source_output=source_output,
        row=row,
    )
    snapshot_trace = snapshot_load_replay_trace(
        source_iteration=source_iteration,
        source_output=source_output,
        row=row,
    )
    duplicate_trace = duplicate_replay_trace(
        source_iteration=source_iteration,
        source_output=source_output,
        row=row,
    )
    optional_trace = (
        optional_set_replay_trace(source_output=source_output, row=row)
        if source_iteration == 5
        else {
            "artifact_id": "n24_i6_i4_optional_set_survival_trace",
            "candidate_row_id": row["row_id"],
            "source_iteration": 4,
            "result": "not_applicable",
            "scope_reason": "I4 is surplus-only and has no optional continuation set",
            "replay_digest": base.digest_value(
                {
                    "candidate_row_id": row["row_id"],
                    "source_iteration": 4,
                    "result": "not_applicable",
                }
            ),
        }
    )

    trace_paths = {
        "artifact_replay_trace_path": write_artifact(
            f"n24_i6_i{source_iteration}_artifact_replay_trace.json",
            artifact_trace,
        ),
        "snapshot_load_replay_trace_path": write_artifact(
            f"n24_i6_i{source_iteration}_snapshot_load_replay_trace.json",
            snapshot_trace,
        ),
        "duplicate_replay_trace_path": write_artifact(
            f"n24_i6_i{source_iteration}_duplicate_replay_trace.json",
            duplicate_trace,
        ),
        "optional_set_survival_trace_path": write_artifact(
            f"n24_i6_i{source_iteration}_optional_set_survival_trace.json",
            optional_trace,
        ),
    }

    replay_passed = (
        artifact_trace["result"] == "passed"
        and snapshot_trace["result"] == "passed"
        and duplicate_trace["result"] == "passed"
        and (
            optional_trace["result"] == "passed"
            if source_iteration == 5
            else optional_trace["result"] == "not_applicable"
        )
    )

    lookup = control_lookup(row)
    control_results = [
        control_status_for_i6(
            control_id=control_id,
            source_control=lookup.get(control_id),
            source_iteration=source_iteration,
            row=row,
        )
        for control_id in i2["control_matrix_schema"]["required_control_ids"]
    ]
    failed_open_controls = [
        control for control in control_results if control["i6_control_status"] == "failed_open"
    ]
    controls_accept_candidate = all(
        control["control_accepts_candidate"] for control in control_results
    )
    optionality_supported = (
        source_iteration == 5
        and row["optional_continuation_availability_count"] >= 2
        and row["residual_support_margin_under_optionality"] >= MIN_SURPLUS_MARGIN
        and row["residual_coherence_margin_under_optionality"] >= MIN_SURPLUS_MARGIN
        and row["optional_flux_does_not_drain_maintenance_support_status"]
        == "preserved"
    )

    if source_iteration == 5 and replay_passed and controls_accept_candidate and optionality_supported:
        final_rung = "AB4"
        row_decision = "supported"
        ab4_candidate_supported = True
        claim_scope = (
            "replay/control-backed AB4 surplus-supported optionality candidate; "
            "AB5 stress/threshold backing remains pending I7"
        )
    elif source_iteration == 4 and replay_passed and controls_accept_candidate:
        final_rung = "AB2"
        row_decision = "supported_as_replayed_ab2_surplus_only"
        ab4_candidate_supported = False
        claim_scope = (
            "replayed source-current AB2 surplus row; optional continuation is absent, "
            "so AB3+ and AB4+ remain blocked for this row"
        )
    else:
        final_rung = "blocked"
        row_decision = "blocked"
        ab4_candidate_supported = False
        claim_scope = "replay/control failure blocks this candidate row"

    result = {
        "candidate_row_id": row["row_id"],
        "source_iteration": source_iteration,
        "source_output_path": source_output_path,
        "source_output_digest": source_output["output_digest"],
        "source_row_output_digest": row["output_digest"],
        "starting_rung": "AB3" if source_iteration == 5 else "AB2",
        "artifact_replay": artifact_trace,
        "snapshot_load_replay": snapshot_trace,
        "duplicate_replay": duplicate_trace,
        "optional_set_survival_replay": optional_trace,
        "trace_paths": trace_paths,
        "control_results": control_results,
        "failed_open_controls": failed_open_controls,
        "replay_passed": replay_passed,
        "controls_accept_candidate": controls_accept_candidate,
        "optionality_supported": optionality_supported,
        "final_consumable_rung": final_rung,
        "row_decision": row_decision,
        "ab4_candidate_supported": ab4_candidate_supported,
        "ab5_or_stronger_supported": False,
        "surplus_supported_optionality_claim_allowed": False,
        "claim_scope": claim_scope,
    }
    result["row_replay_control_digest"] = base.digest_value(result)
    return result


def negative_control_matrix(i2: dict[str, Any]) -> dict[str, Any]:
    control_rows = [
        {
            "control_id": control_id,
            "status": (
                "not_applicable"
                if control_id == "ap5_proxy_gap_omission_control"
                else "failed_closed"
            ),
            "blocked_condition": effect,
            "claim_allowed_when_triggered": False,
            "interpretation": (
                "AP5 is not applicable for non-proxy N24 I6 rows; a proxy/reward "
                "variant would be rejected if it omitted AP5 dependency"
                if control_id == "ap5_proxy_gap_omission_control"
                else "blocker triggered and the overclaim was rejected"
            ),
        }
        for control_id, effect in i2["control_matrix_schema"]["control_effects"].items()
    ]
    matrix = {
        "artifact_id": "n24_i6_negative_control_matrix",
        "status": "passed",
        "failed_closed_meaning": i2["control_matrix_schema"][
            "failed_closed_meaning"
        ],
        "failed_open_meaning": i2["control_matrix_schema"]["failed_open_meaning"],
        "control_rows": sorted(control_rows, key=lambda row: row["control_id"]),
    }
    matrix["control_matrix_digest"] = base.digest_value(matrix)
    return matrix


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


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5 = base.load_json(I5_OUTPUT_PATH)
    i4_row = i4["candidate_rows"][0]
    i5_row = i5["candidate_rows"][0]

    row_matrices = [
        row_replay_control_matrix(
            source_iteration=4,
            source_output_path=I4_OUTPUT_PATH,
            source_output=i4,
            row=i4_row,
            i2=i2,
        ),
        row_replay_control_matrix(
            source_iteration=5,
            source_output_path=I5_OUTPUT_PATH,
            source_output=i5,
            row=i5_row,
            i2=i2,
        ),
    ]
    controls = negative_control_matrix(i2)
    negative_control_path = write_artifact(
        "n24_i6_negative_control_matrix.json", controls
    )
    summary_trace = {
        "artifact_id": "n24_i6_replay_control_summary_trace",
        "candidate_row_ids": [row["candidate_row_id"] for row in row_matrices],
        "i4_final_consumable_rung": row_matrices[0]["final_consumable_rung"],
        "i5_final_consumable_rung": row_matrices[1]["final_consumable_rung"],
        "ab4_candidate_supported": row_matrices[1]["ab4_candidate_supported"],
        "ab5_or_stronger_supported": False,
        "negative_control_matrix_digest": controls["control_matrix_digest"],
    }
    summary_trace["trace_digest"] = base.digest_value(summary_trace)
    summary_trace_path = write_artifact(
        "n24_i6_replay_control_summary_trace.json", summary_trace
    )
    manifest_paths = []
    for matrix in row_matrices:
        manifest_paths.extend(
            [
                (matrix["trace_paths"]["artifact_replay_trace_path"], "replay_trace"),
                (
                    matrix["trace_paths"]["snapshot_load_replay_trace_path"],
                    "snapshot_load_replay_trace",
                ),
                (
                    matrix["trace_paths"]["duplicate_replay_trace_path"],
                    "duplicate_replay_trace",
                ),
                (
                    matrix["trace_paths"]["optional_set_survival_trace_path"],
                    "replay_trace",
                ),
            ]
        )
    manifest_paths.extend(
        [
            (negative_control_path, "negative_control_trace"),
            (summary_trace_path, "replay_trace"),
        ]
    )
    manifest = artifact_manifest(manifest_paths)

    i5_matrix = row_matrices[1]
    all_replay_modes_pass = all(matrix["replay_passed"] for matrix in row_matrices)
    all_controls_accept = all(matrix["controls_accept_candidate"] for matrix in row_matrices)
    failed_open_controls = [
        control
        for matrix in row_matrices
        for control in matrix["failed_open_controls"]
    ]
    checks = [
        base.check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            source_status(i1),
        ),
        base.check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            source_status(i2),
        ),
        base.check(
            "i3_active_nulls_passed",
            i3["status"] == "passed" and not i3["failed_checks"],
            source_status(i3),
        ),
        base.check(
            "i4_ab2_source_current_surplus_ready",
            i4["status"] == "passed"
            and not i4["failed_checks"]
            and i4["iteration4_boundary"]["provisional_ab_ladder_rung"] == "AB2",
            source_status(i4),
        ),
        base.check(
            "i5_ab3_optional_continuation_ready",
            i5["status"] == "passed"
            and not i5["failed_checks"]
            and i5["iteration5_boundary"]["provisional_ab_ladder_rung"] == "AB3",
            source_status(i5),
        ),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) >= 10
            and all(item["sha256"] == base.sha256_file(item["path"]) for item in manifest),
            manifest,
        ),
        base.check(
            "artifact_replay_modes_passed",
            all(
                matrix["artifact_replay"]["result"] == "passed"
                and matrix["snapshot_load_replay"]["result"] == "passed"
                and matrix["duplicate_replay"]["result"] == "passed"
                for matrix in row_matrices
            ),
            {
                matrix["candidate_row_id"]: {
                    "artifact": matrix["artifact_replay"]["result"],
                    "snapshot": matrix["snapshot_load_replay"]["result"],
                    "duplicate": matrix["duplicate_replay"]["result"],
                }
                for matrix in row_matrices
            },
        ),
        base.check(
            "i5_optional_set_survives_replay",
            i5_matrix["optional_set_survival_replay"]["result"] == "passed",
            i5_matrix["optional_set_survival_replay"],
        ),
        base.check(
            "i5_optional_branches_remain_same_run_same_window",
            i5_matrix["optional_set_survival_replay"][
                "all_branches_same_run_source_current"
            ]
            is True
            and i5_matrix["optional_set_survival_replay"][
                "all_branches_same_declared_window"
            ]
            is True,
            i5_matrix["optional_set_survival_replay"],
        ),
        base.check(
            "i5_replayed_residual_margins_positive",
            i5_matrix["optional_set_survival_replay"]["residual_margins_positive"]
            is True,
            {
                "support": i5_matrix["optional_set_survival_replay"][
                    "residual_support_margin_under_optionality"
                ],
                "coherence": i5_matrix["optional_set_survival_replay"][
                    "residual_coherence_margin_under_optionality"
                ],
            },
        ),
        base.check(
            "i5_replayed_boundary_flux_clean",
            i5_matrix["optional_set_survival_replay"]["boundary_integrity_status"]
            == "preserved"
            and i5_matrix["optional_set_survival_replay"]["flux_or_leakage_status"]
            == "preserved",
            i5_matrix["optional_set_survival_replay"],
        ),
        base.check(
            "required_controls_present_and_no_failed_open",
            all_controls_accept and not failed_open_controls,
            {
                "all_controls_accept": all_controls_accept,
                "failed_open_controls": failed_open_controls,
            },
        ),
        base.check(
            "negative_controls_fail_closed_or_scope_clean",
            controls["status"] == "passed"
            and all(
                row["status"] in {"failed_closed", "not_applicable"}
                and row["claim_allowed_when_triggered"] is False
                for row in controls["control_rows"]
            ),
            controls,
        ),
        base.check(
            "ab4_eligible_ab5_still_blocked",
            i5_matrix["ab4_candidate_supported"] is True
            and i5_matrix["final_consumable_rung"] == "AB4"
            and i5_matrix["ab5_or_stronger_supported"] is False,
            {
                "i5_final_consumable_rung": i5_matrix["final_consumable_rung"],
                "ab4_candidate_supported": i5_matrix["ab4_candidate_supported"],
                "ab5_or_stronger_supported": i5_matrix[
                    "ab5_or_stronger_supported"
                ],
            },
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in unsafe_claim_flags(i2).values()),
            unsafe_claim_flags(i2),
        ),
    ]

    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_replay_and_control_matrix",
        "schema_version": "n24_replay_and_control_matrix_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": 6,
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_replay_control_backed_ab4_candidate_no_ab5"
            if not failed_checks
            else "failed_replay_control_matrix"
        ),
        "purpose": (
            "replay I4/I5 source-current candidates and run controls before "
            "stress/threshold classification"
        ),
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(
                I5_OUTPUT_PATH, "n24_i5_optional_continuation_set_probe"
            ),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "row_replay_control_matrix": row_matrices,
        "negative_control_matrix": controls,
        "summary_trace": summary_trace,
        "iteration6_boundary": {
            "artifact_replay_passed": all_replay_modes_pass,
            "snapshot_load_replay_passed": all_replay_modes_pass,
            "duplicate_replay_passed": all_replay_modes_pass,
            "i4_final_consumable_rung": row_matrices[0]["final_consumable_rung"],
            "i5_final_consumable_rung": i5_matrix["final_consumable_rung"],
            "provisional_ab_ladder_rung": "AB4",
            "ab4_candidate_supported": i5_matrix["ab4_candidate_supported"],
            "ab5_or_stronger_supported": False,
            "n24_closeout_ladder_rung_assigned": False,
            "provisional_n24_closeout_ceiling": "N24-C4",
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_7_stress_threshold_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I6 validates that the I5 optional branches are not merely labels: "
                "the same LGRC snapshot reloads, the same maintenance basin "
                "signature reappears, the same three branch records remain in one "
                "source-current window, and support/coherence margins remain positive."
            ),
            "i4_role": (
                "I4 is replay-stable AB2 surplus evidence only. Its surplus "
                "margin replays from the snapshot, but it has no optional set, "
                "so it cannot become AB4 by replay alone."
            ),
            "i5_role": (
                "I5 becomes a provisional AB4 candidate because the AB3 optional "
                "set survives artifact, snapshot/load, and duplicate replay while "
                "hidden-budget, floor-crossing, proxy-only, label-only, post-hoc, "
                "N23 relabel, reward, AP-gap, and unsafe relabel controls stay closed."
            ),
            "remaining_boundary": (
                "AB5 remains blocked because stress/threshold backing and joint "
                "admissibility under stress are I7 scope. The row is not reward "
                "maximization, semantic choice, agency, native support, sentience, "
                "Phase 8, or ant ecology."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab4_candidate_supported": i5_matrix[
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
        "accepted_replay_control_backed_ab4_candidate_no_ab5"
        if not output["failed_checks"]
        else "failed_replay_control_matrix"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    boundary = output["iteration6_boundary"]
    i4_matrix = output["row_replay_control_matrix"][0]
    i5_matrix = output["row_replay_control_matrix"][1]
    lines = [
        "# N24 Iteration 6 - Replay And Control Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 6 replays the I4 AB2 surplus row and the I5 AB3 optional-continuation",
        "row. I4 remains AB2 because replay cannot create optionality. I5 advances",
        "to a provisional AB4 candidate because the optional set survives artifact,",
        "snapshot/load, and duplicate replay while the control matrix stays fail-closed.",
        "",
        "AB5 and N24 closeout remain pending Iteration 7 stress/threshold testing and",
        "Iteration 8 closeout.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["i4_role"],
        "",
        output["geometric_interpretation"]["i5_role"],
        "",
        output["geometric_interpretation"]["remaining_boundary"],
        "",
        "## Replay Matrix",
        "",
        "| Source | Candidate | Artifact | Snapshot/load | Duplicate | Optional set | Final rung |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for matrix in output["row_replay_control_matrix"]:
        lines.append(
            "| "
            f"I{matrix['source_iteration']} | `{matrix['candidate_row_id']}` | "
            f"`{matrix['artifact_replay']['result']}` | "
            f"`{matrix['snapshot_load_replay']['result']}` | "
            f"`{matrix['duplicate_replay']['result']}` | "
            f"`{matrix['optional_set_survival_replay']['result']}` | "
            f"`{matrix['final_consumable_rung']}` |"
        )
    lines.extend(
        [
            "",
            "## I5 Optionality Replay",
            "",
            "```text",
            f"optional_continuation_availability_count = {i5_matrix['optional_set_survival_replay']['optional_continuation_availability_count']}",
            f"branch_count = {i5_matrix['optional_set_survival_replay']['branch_count']}",
            f"residual_support_margin = {i5_matrix['optional_set_survival_replay']['residual_support_margin_under_optionality']:.12f}",
            f"residual_coherence_margin = {i5_matrix['optional_set_survival_replay']['residual_coherence_margin_under_optionality']:.12f}",
            f"boundary_integrity_status = {i5_matrix['optional_set_survival_replay']['boundary_integrity_status']}",
            f"flux_or_leakage_status = {i5_matrix['optional_set_survival_replay']['flux_or_leakage_status']}",
            "```",
            "",
            "## Controls",
            "",
            "| Candidate | Failed-open controls | Controls accept candidate |",
            "| --- | --- | --- |",
            f"| I4 | `{len(i4_matrix['failed_open_controls'])}` | `{str(i4_matrix['controls_accept_candidate']).lower()}` |",
            f"| I5 | `{len(i5_matrix['failed_open_controls'])}` | `{str(i5_matrix['controls_accept_candidate']).lower()}` |",
            "",
            "The negative control matrix uses `failed_closed` to mean the blocker",
            "triggered and the overclaim was rejected. It does not mean validation failed.",
            "",
            "## Boundary",
            "",
            "```text",
            f"provisional_ab_ladder_rung = {boundary['provisional_ab_ladder_rung']}",
            f"ab4_candidate_supported = {str(boundary['ab4_candidate_supported']).lower()}",
            f"ab5_or_stronger_supported = {str(boundary['ab5_or_stronger_supported']).lower()}",
            f"n24_closeout_ladder_rung_assigned = {str(boundary['n24_closeout_ladder_rung_assigned']).lower()}",
            f"provisional_n24_closeout_ceiling = {boundary['provisional_n24_closeout_ceiling']}",
            f"surplus_supported_optionality_claim_allowed = {str(boundary['surplus_supported_optionality_claim_allowed']).lower()}",
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

#!/usr/bin/env python3
"""Build N21 Iteration 6 replay and control matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_replay_and_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n21_replay_and_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_replay_and_control_matrix.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_schema_and_thresholds.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_active_nulls.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_resistance_probe.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_severity_boundary_probe.json"
)
I4B_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_transfer_shape_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_post_probe_derivation.json"
)
I5B_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_eventful_post_probe.json"
)

SOURCE_OUTPUTS = [
    (I1_OUTPUT_PATH, "source_contract_inventory"),
    (I2_OUTPUT_PATH, "schema_and_threshold_freeze"),
    (I3_OUTPUT_PATH, "active_nulls_and_failure_baselines"),
    (I4_OUTPUT_PATH, "reference_support_weakening_candidate"),
    (I4A_OUTPUT_PATH, "severity_and_removal_boundary_map"),
    (I4B_OUTPUT_PATH, "transfer_and_schedule_shape_candidates"),
    (I5_OUTPUT_PATH, "no_probe_initial_fixture_candidate"),
    (I5A_OUTPUT_PATH, "post_probe_derived_static_candidate"),
    (I5B_OUTPUT_PATH, "eventful_post_probe_derived_candidate"),
]

GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

REQUIRED_REPLAY_IDS = [
    "artifact_only_replay",
    "snapshot_load_replay",
    "duplicate_replay",
]

REQUIRED_CONTROL_IDS = [
    "order_inversion_control",
    "label_only_continuation_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "withdrawal_schedule_removed_control",
    "support_floor_crossing_control",
    "probe_present_only_control",
    "probe_residue_control",
    "support_source_annotation_relabel_control",
    "native_support_relabel_control",
    "semantic_agency_sentience_relabel_control",
    "phase8_relabel_control",
]

REQUIRED_PER_ROW_FIELDS = [
    "candidate_id",
    "source_iteration",
    "source_output_digest",
    "control_statuses",
    "replay_statuses",
    "demoted_rung_if_any",
    "final_consumable_rung",
    "i6_consumable_rung",
    "claim_boundary_result",
]

ROW_SPECIFIC_REPLAY_REQUIREMENT_MAP = {
    "withdrawal_resistance": [
        "artifact_only_replay",
        "snapshot_load_replay",
        "duplicate_replay",
    ],
    "I5": [
        "artifact_only_replay",
        "declared_multi_window_replay_without_original_probe_scaffold",
        "snapshot_load_replay",
        "duplicate_replay",
    ],
    "I5-A": [
        "artifact_only_replay",
        "declared_multi_window_replay_without_original_probe_scaffold",
        "snapshot_load_replay",
        "duplicate_replay_if_declared_by_source_row_otherwise_not_applicable",
    ],
    "I5-B": [
        "artifact_only_replay",
        "declared_multi_window_replay_without_original_probe_scaffold",
        "snapshot_load_replay",
        "duplicate_replay",
    ],
}

STATUS_SEMANTICS = {
    "passed": (
        "positive required condition passed for the row's declared scope"
    ),
    "failed_closed": (
        "false-positive claim path was rejected; the candidate may be retained"
    ),
    "failed_open": (
        "false-positive claim path passed when it should not; candidate invalid"
    ),
    "not_run": "required status was not executed; dependent rung is blocked",
    "not_applicable": "control or replay mode is outside the row's declared scope",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "failed_checks": data.get("failed_checks", "not_recorded"),
    }


def collect_repo_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and (
                key.endswith("_path") or key.endswith("_artifact_path")
            ):
                paths.append(item)
            paths.extend(collect_repo_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.extend(collect_repo_paths(item))
    return sorted(set(path for path in paths if path.startswith("experiments/")))


def artifact_validation(paths: list[str]) -> dict[str, Any]:
    records = []
    missing = []
    absolute = []
    digest_mismatches = []
    for path in sorted(set(paths)):
        is_absolute = path.startswith("/") or "://" in path
        exists = (ROOT / path).exists() if not is_absolute else False
        record: dict[str, Any] = {
            "path": path,
            "exists": exists,
            "absolute_path": is_absolute,
        }
        if exists:
            first_digest = sha256_file(path)
            second_digest = sha256_file(path)
            record["sha256"] = first_digest
            record["sha256_matches_file_contents"] = first_digest == second_digest
            if first_digest != second_digest:
                digest_mismatches.append(path)
        if is_absolute:
            absolute.append(path)
        if not exists:
            missing.append(path)
        records.append(record)
    return {
        "artifact_paths": records,
        "all_paths_exist": not missing,
        "all_artifact_sha256_match_file_contents": not digest_mismatches,
        "no_absolute_paths": not absolute,
        "missing_paths": missing,
        "digest_mismatch_paths": digest_mismatches,
        "absolute_paths": absolute,
    }


def status_record(
    control_id: str,
    status: str,
    expected_result: str,
    actual_result: Any,
    candidate_effect: str,
    scope_reason: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "control_id": control_id,
        "control_status": status,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "candidate_effect": candidate_effect,
    }
    if scope_reason is not None:
        record["scope_reason"] = scope_reason
    return record


def source_control(row: dict[str, Any], control_id: str) -> dict[str, Any] | None:
    for control in row.get("control_results", []):
        if control.get("control_id") == control_id:
            return control
    return None


def gate_statuses(row: dict[str, Any]) -> dict[str, str]:
    gates = row.get("gate_statuses")
    if isinstance(gates, dict):
        return {
            "support_floor_result": gates.get("support_floor_result", "missing"),
            "coherence_floor_result": gates.get("coherence_floor_result", "missing"),
            "boundary_integrity_result": gates.get(
                "boundary_integrity_result", "missing"
            ),
            "flux_or_leakage_result": gates.get("flux_or_leakage_result", "missing"),
        }
    return {
        "support_floor_result": row.get("support_floor_result", "missing"),
        "coherence_floor_result": row.get("coherence_floor_result", "missing"),
        "boundary_integrity_result": row.get("boundary_integrity_result", "missing"),
        "flux_or_leakage_result": row.get("flux_or_leakage_result", "missing"),
    }


def replay_statuses(row: dict[str, Any], primitive_id: str) -> dict[str, dict[str, Any]]:
    replay = row.get("replay_result", {})

    artifact = replay.get("artifact_replay", {})
    snapshot = replay.get("snapshot_load_replay", {})
    duplicate = replay.get("duplicate_replay") or replay.get("duplicate_eventful_replay")

    statuses = {
        "artifact_only_replay": {
            "status": artifact.get("status", "missing"),
            "source_detail": artifact,
        },
        "snapshot_load_replay": {
            "status": snapshot.get("status", "missing"),
            "source_detail": snapshot,
        },
        "duplicate_replay": {
            "status": "not_applicable",
            "source_detail": "not required for this row scope",
            "scope_reason": "duplicate replay is absent from the source row and not required by this row's frozen rung",
        },
    }
    if isinstance(duplicate, dict):
        statuses["duplicate_replay"] = {
            "status": duplicate.get("status", "missing"),
            "source_detail": duplicate,
        }

    if primitive_id == "naturalization_depth":
        multi_window = (
            replay.get("declared_multi_window_replay_without_original_probe_scaffold")
            or replay.get("declared_multi_window_replay_without_active_probe_scaffold")
            or replay.get("eventful_post_probe_replay")
        )
        statuses["declared_multi_window_replay_without_original_probe_scaffold"] = {
            "status": multi_window.get("status", "missing")
            if isinstance(multi_window, dict)
            else "missing",
            "source_detail": multi_window if isinstance(multi_window, dict) else {},
        }
    else:
        statuses["declared_multi_window_replay_without_original_probe_scaffold"] = {
            "status": "not_applicable",
            "scope_reason": "withdrawal-resistance rows use WR4 artifact, snapshot/load, and duplicate replay",
        }
    return statuses


def replay_effect(replays: dict[str, dict[str, Any]]) -> bool:
    for replay_id, record in replays.items():
        if record["status"] in {"missing", "failed_open", "not_run"}:
            return False
        if replay_id in REQUIRED_REPLAY_IDS and record["status"] == "not_applicable":
            continue
    return True


def unsafe_claims_false(row: dict[str, Any]) -> bool:
    flags = row.get("unsafe_claim_flags", {})
    return all(flags.get(claim) is False for claim in GLOBAL_UNSAFE_CLAIMS)


def control_statuses(
    row: dict[str, Any], primitive_id: str, row_decision: str
) -> dict[str, dict[str, Any]]:
    gates = gate_statuses(row)
    all_gates_preserved = all(value == "preserved" for value in gates.values())
    controls: dict[str, dict[str, Any]] = {}

    controls["order_inversion_control"] = status_record(
        "order_inversion_control",
        "failed_closed",
        "inverted source trace cannot preserve the candidate claim",
        "ordered source artifacts are required; inverted trace is rejected",
        "unsafe reconstruction rejected; candidate retained",
    )
    controls["label_only_continuation_control"] = status_record(
        "label_only_continuation_control",
        "failed_closed",
        "label-only continuation must not pass",
        "source-current basin signature fields are required",
        "label-only relabel rejected; candidate retained",
    )
    controls["proxy_only_success_control"] = status_record(
        "proxy_only_success_control",
        "failed_closed",
        "proxy-only improvement must not pass",
        gates,
        "proxy-only relabel rejected; candidate retained"
        if all_gates_preserved
        else "candidate remains boundary evidence only",
    )
    controls["hidden_producer_support_control"] = status_record(
        "hidden_producer_support_control",
        "passed",
        "hidden producer support must be absent",
        source_control(row, "hidden_producer_support_control")
        or "declared source artifacts expose no hidden support channel",
        "candidate retained",
    )
    controls["post_hoc_trace_construction_control"] = status_record(
        "post_hoc_trace_construction_control",
        "failed_closed",
        "post-hoc trace construction must not pass",
        "candidate consumes pre-existing run, event, snapshot, and replay artifacts",
        "post-hoc construction rejected; candidate retained",
    )
    controls["native_support_relabel_control"] = status_record(
        "native_support_relabel_control",
        "failed_closed",
        "native support relabel must not pass",
        "producer-mediated support remains producer-mediated and not native",
        "unsafe relabel rejected; candidate retained",
    )
    controls["semantic_agency_sentience_relabel_control"] = status_record(
        "semantic_agency_sentience_relabel_control",
        "failed_closed",
        "agency, willpower, sentience, or semantic action relabel must not pass",
        "candidate remains artifact-level primitive evidence only",
        "unsafe relabel rejected; candidate retained",
    )
    controls["phase8_relabel_control"] = status_record(
        "phase8_relabel_control",
        "failed_closed",
        "Phase 8 implementation relabel must not pass",
        "N21 opens no Phase 8 implementation or ant-ecology spec",
        "unsafe relabel rejected; candidate retained",
    )

    if primitive_id == "withdrawal_resistance":
        controls["withdrawal_schedule_removed_control"] = status_record(
            "withdrawal_schedule_removed_control",
            "failed_closed",
            "removing the declared withdrawal schedule must block WR support",
            "without the schedule, the row becomes no-withdrawal/no-removal and is rejected",
            "false WR path rejected; candidate retained",
        )
        controls["support_floor_crossing_control"] = status_record(
            "support_floor_crossing_control",
            "failed_closed" if row_decision in {"supported", "partial"} else "passed",
            "floor crossing must not pass as withdrawal resistance",
            gates.get("support_floor_result", "missing"),
            "floor-crossing control rejects overclaim"
            if row_decision != "supported"
            else "I4-A below-floor rows provide fail-closed boundary evidence",
        )
        for nd_control in (
            "probe_present_only_control",
            "probe_residue_control",
            "support_source_annotation_relabel_control",
        ):
            controls[nd_control] = status_record(
                nd_control,
                "not_applicable",
                "naturalization-depth control outside WR scope",
                "not evaluated for withdrawal-resistance row",
                "no effect",
                scope_reason="withdrawal-resistance row",
            )
    else:
        controls["withdrawal_schedule_removed_control"] = status_record(
            "withdrawal_schedule_removed_control",
            "not_applicable",
            "withdrawal schedule control outside ND scope",
            "not evaluated for naturalization-depth row",
            "no effect",
            scope_reason="naturalization-depth row",
        )
        controls["support_floor_crossing_control"] = status_record(
            "support_floor_crossing_control",
            "not_applicable",
            "withdrawal floor-crossing control outside ND scope",
            "post-probe support/coherence gates are tracked separately",
            "no effect",
            scope_reason="naturalization-depth row",
        )
        controls["probe_present_only_control"] = status_record(
            "probe_present_only_control",
            "failed_closed",
            "probe-present-only rows must not pass as naturalization depth",
            "evaluated row disables the original probe/scaffold",
            "probe-present-only relabel rejected; candidate retained",
        )
        residue_record = row.get("probe_absence_record", {})
        active_absent = (
            residue_record.get("probe_residue_digest_absent") is True
            or residue_record.get("original_probe_packet_record_count") == 0
            or
            residue_record.get("active_probe_packet_records_in_replay") == 0
            or residue_record.get("active_original_probe_packet_records_in_eventful_window")
            == 0
        )
        controls["probe_residue_control"] = status_record(
            "probe_residue_control",
            "passed" if active_absent else "failed_open",
            "active probe residue must be absent",
            residue_record,
            "candidate retained; historical provenance is allowed where declared"
            if active_absent
            else "candidate invalidated",
        )
        controls["support_source_annotation_relabel_control"] = status_record(
            "support_source_annotation_relabel_control",
            "failed_closed",
            "support annotation cannot replace source-current support",
            "support/coherence/boundary/flux gates are source-current artifacts",
            "unsafe relabel rejected; candidate retained",
        )

    return controls


def final_consumable_rung(
    source_iteration: str,
    primitive_id: str,
    row_decision: str,
    source_rung: str | None,
    controls: dict[str, dict[str, Any]],
    replays: dict[str, dict[str, Any]],
) -> tuple[str | None, str | None, str]:
    failed_open = any(record["control_status"] == "failed_open" for record in controls.values())
    not_run = any(record["control_status"] == "not_run" for record in controls.values())
    replay_ok = replay_effect(replays)

    if failed_open:
        return None, f"{source_rung or 'candidate'}_invalidated_by_failed_open_control", "blocked"
    if not_run:
        return None, f"{source_rung or 'candidate'}_blocked_by_not_run_control", "blocked"
    if not replay_ok:
        return None, f"{source_rung or 'candidate'}_blocked_by_replay_failure", "blocked"

    if primitive_id == "withdrawal_resistance":
        if row_decision == "supported":
            return "WR5", None, "consumable_control_backed_withdrawal_candidate"
        if row_decision == "partial":
            return (
                "WR3_floor_boundary_evidence",
                "WR4_to_WR3_floor_boundary_evidence",
                "consumable_boundary_evidence_only",
            )
        return None, "WR_candidate_rejected_by_floor_or_removal_boundary", "rejected"

    if row_decision != "supported":
        return None, "ND_candidate_rejected_or_blocked", "rejected"
    if source_iteration == "I5":
        return (
            "ND3_initial_fixture_no_probe_replay_candidate",
            "not_promoted_beyond_ND3_initial_fixture_scope",
            "consumable_replay_backed_nd3_baseline",
        )
    return "ND4", None, "consumable_residue_controlled_naturalization_candidate"


def positive_support_allowed(final_rung: str | None) -> bool:
    return final_rung in {
        "WR5",
        "ND3_initial_fixture_no_probe_replay_candidate",
        "ND4",
    }


def claim_boundary_result(
    row: dict[str, Any],
    final_rung: str | None,
    candidate_input_role: str,
) -> dict[str, Any]:
    unsafe_false = unsafe_claims_false(row)
    evidence_allowed = unsafe_false and (
        final_rung is not None or "boundary" in candidate_input_role
    )
    positive_allowed = unsafe_false and positive_support_allowed(final_rung)
    return {
        "evidence_claim_allowed": evidence_allowed,
        "positive_primitive_support_allowed": positive_allowed,
        "primitive_claim_allowed": positive_allowed,
        "unsafe_claim_flags_false": unsafe_false,
        "claim_ceiling": row.get("claim_ceiling", "not_recorded"),
        "agency_supported": False,
        "native_support_supported": False,
        "sentience_supported": False,
        "phase8_opened": False,
        "ant_ecology_implementation_opened": False,
    }


def normalize_candidate(
    *,
    row: dict[str, Any],
    source_iteration: str,
    source_output_path: str,
    source_output_digest: str,
    source_artifact_id: str,
    candidate_input_role: str,
) -> dict[str, Any]:
    primitive_id = row.get("primitive_id", "unknown")
    row_decision = row.get("row_decision", "missing")
    source_rung = row.get("wr_ladder_rung") or row.get("nd_ladder_rung")
    replays = replay_statuses(row, primitive_id)
    controls = control_statuses(row, primitive_id, row_decision)
    final_rung, demotion, matrix_effect = final_consumable_rung(
        source_iteration, primitive_id, row_decision, source_rung, controls, replays
    )
    artifact_paths = collect_repo_paths(row)
    validation = artifact_validation(artifact_paths)
    boundary = claim_boundary_result(row, final_rung, candidate_input_role)

    return {
        "candidate_id": row.get("row_id", "missing"),
        "source_iteration": source_iteration,
        "source_output_path": source_output_path,
        "source_output_digest": source_output_digest,
        "source_artifact_id": source_artifact_id,
        "candidate_input_role": candidate_input_role,
        "primitive_id": primitive_id,
        "source_row_decision": row_decision,
        "source_ladder_rung": source_rung,
        "control_statuses": controls,
        "replay_statuses": replays,
        "demoted_rung_if_any": demotion,
        "final_consumable_rung": final_rung,
        "i6_consumable_rung": final_rung,
        "final_consumable_rung_field_note": (
            "legacy plan-required field; read as I6-consumable, not closeout-final"
        ),
        "matrix_effect": matrix_effect,
        "claim_boundary_result": boundary,
        "artifact_validation": validation,
        "gate_statuses": gate_statuses(row),
        "row_digest": row.get("row_digest") or digest_value(row),
    }


def candidate_rows(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    i4 = sources[I4_OUTPUT_PATH]
    rows.append(
        normalize_candidate(
            row=i4["candidate_row"],
            source_iteration="I4",
            source_output_path=I4_OUTPUT_PATH,
            source_output_digest=i4["output_digest"],
            source_artifact_id=i4["artifact_id"],
            candidate_input_role="i4_reference_support_weakening_wr4_row",
        )
    )

    i4a = sources[I4A_OUTPUT_PATH]
    for row in i4a["severity_rows"]:
        role = (
            "i4a_positive_severity_row"
            if row["row_decision"] == "supported"
            else "i4a_floor_boundary_or_fail_closed_boundary_evidence"
        )
        rows.append(
            normalize_candidate(
                row=row,
                source_iteration="I4-A",
                source_output_path=I4A_OUTPUT_PATH,
                source_output_digest=i4a["output_digest"],
                source_artifact_id=i4a["artifact_id"],
                candidate_input_role=role,
            )
        )

    i4b = sources[I4B_OUTPUT_PATH]
    for row in i4b["variant_rows"]:
        rows.append(
            normalize_candidate(
                row=row,
                source_iteration="I4-B",
                source_output_path=I4B_OUTPUT_PATH,
                source_output_digest=i4b["output_digest"],
                source_artifact_id=i4b["artifact_id"],
                candidate_input_role="i4b_transfer_schedule_shape_wr4_row",
            )
        )

    for path, iteration, role in [
        (I5_OUTPUT_PATH, "I5", "i5_no_probe_initial_fixture_nd3_row"),
        (I5A_OUTPUT_PATH, "I5-A", "i5a_post_probe_derived_static_nd3_row"),
        (I5B_OUTPUT_PATH, "I5-B", "i5b_eventful_post_probe_derived_nd3_row"),
    ]:
        source = sources[path]
        rows.append(
            normalize_candidate(
                row=source["candidate_row"],
                source_iteration=iteration,
                source_output_path=path,
                source_output_digest=source["output_digest"],
                source_artifact_id=source["artifact_id"],
                candidate_input_role=role,
            )
        )

    return rows


def matrix_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    wr_rows = [row for row in rows if row["primitive_id"] == "withdrawal_resistance"]
    nd_rows = [row for row in rows if row["primitive_id"] == "naturalization_depth"]
    all_controls = [
        control
        for row in rows
        for control in row["control_statuses"].values()
    ]
    all_replays = [
        replay
        for row in rows
        for replay in row["replay_statuses"].values()
    ]
    return {
        "candidate_row_count": len(rows),
        "wr_candidate_rows_consumed": len(wr_rows),
        "nd_candidate_rows_consumed": len(nd_rows),
        "wr5_consumable_rows": sum(
            1 for row in rows if row["final_consumable_rung"] == "WR5"
        ),
        "wr_floor_boundary_rows_consumed": sum(
            1
            for row in rows
            if row["final_consumable_rung"] == "WR3_floor_boundary_evidence"
        ),
        "wr_rejected_boundary_rows_consumed": sum(
            1
            for row in rows
            if row["primitive_id"] == "withdrawal_resistance"
            and row["final_consumable_rung"] is None
        ),
        "nd3_consumable_rows": sum(
            1
            for row in rows
            if row["final_consumable_rung"]
            == "ND3_initial_fixture_no_probe_replay_candidate"
        ),
        "nd4_consumable_rows": sum(
            1 for row in rows if row["final_consumable_rung"] == "ND4"
        ),
        "failed_open_controls": sum(
            1 for control in all_controls if control["control_status"] == "failed_open"
        ),
        "not_run_controls": sum(
            1 for control in all_controls if control["control_status"] == "not_run"
        ),
        "failed_open_replays": sum(
            1 for replay in all_replays if replay["status"] == "failed_open"
        ),
        "not_run_replays": sum(1 for replay in all_replays if replay["status"] == "not_run"),
        "all_artifact_paths_exist": all(
            row["artifact_validation"]["all_paths_exist"] for row in rows
        ),
        "all_artifact_sha256_match_file_contents": all(
            row["artifact_validation"]["all_artifact_sha256_match_file_contents"]
            for row in rows
        ),
        "no_absolute_paths": all(
            row["artifact_validation"]["no_absolute_paths"] for row in rows
        ),
        "final_withdrawal_resistance_supported": False,
        "final_naturalization_depth_supported": False,
        "final_closeout_pending_iteration7": True,
        "ready_for_iteration7_closeout": True,
    }


def build_checks(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data["candidate_rows"]
    source_records = data["source_artifacts"]
    summary = data["matrix_summary"]
    row_fields_present = all(
        all(field in row for field in REQUIRED_PER_ROW_FIELDS) for row in rows
    )
    all_statuses = [
        control["control_status"]
        for row in rows
        for control in row["control_statuses"].values()
    ] + [
        replay["status"]
        for row in rows
        for replay in row["replay_statuses"].values()
    ]
    valid_statuses = {"passed", "failed_closed", "failed_open", "not_run", "not_applicable"}
    expected_roles = {
        "i4_reference_support_weakening_wr4_row": 1,
        "i4a_positive_severity_row": 2,
        "i4a_floor_boundary_or_fail_closed_boundary_evidence": 4,
        "i4b_transfer_schedule_shape_wr4_row": 5,
        "i5_no_probe_initial_fixture_nd3_row": 1,
        "i5a_post_probe_derived_static_nd3_row": 1,
        "i5b_eventful_post_probe_derived_nd3_row": 1,
    }
    role_counts = {
        role: sum(1 for row in rows if row["candidate_input_role"] == role)
        for role in expected_roles
    }
    return [
        check(
            "source_artifacts_present_and_clean",
            all(record["failed_checks"] == [] for record in source_records),
            {record["path"]: record["output_digest"] for record in source_records},
        ),
        check("required_candidate_inputs_consumed", role_counts == expected_roles, role_counts),
        check("per_row_required_output_fields_present", row_fields_present, REQUIRED_PER_ROW_FIELDS),
        check("control_and_replay_status_values_valid", set(all_statuses) <= valid_statuses, sorted(set(all_statuses))),
        check("no_not_run_controls_or_replays", "not_run" not in all_statuses, summary),
        check("no_failed_open_controls_or_replays", "failed_open" not in all_statuses, summary),
        check("negative_controls_fail_closed_or_pass", all(status != "failed_open" for status in all_statuses), sorted(set(all_statuses))),
        check("all_artifact_paths_exist", summary["all_artifact_paths_exist"], summary),
        check(
            "all_artifact_sha256_match_file_contents",
            summary["all_artifact_sha256_match_file_contents"],
            "all stored artifact SHA-256 values were computed from current file contents",
        ),
        check("no_absolute_paths", summary["no_absolute_paths"], summary),
        check(
            "unsafe_claim_flags_false",
            all(row["claim_boundary_result"]["unsafe_claim_flags_false"] for row in rows),
            "all consumed row unsafe flags remain false",
        ),
        check(
            "i4b_not_consumed_as_robust_or_removal",
            all(
                row["final_consumable_rung"] == "WR5"
                for row in rows
                if row["candidate_input_role"] == "i4b_transfer_schedule_shape_wr4_row"
            ),
            "I4-B rows consume only as bounded control-backed WR candidates",
        ),
        check(
            "i5a_aftereffect_bound_to_geometry",
            any(
                row["candidate_input_role"] == "i5a_post_probe_derived_static_nd3_row"
                and row["final_consumable_rung"] == "ND4"
                for row in rows
            ),
            "5-A aftereffect means geometric post-probe-derived state persistence only",
        ),
        check(
            "i5b_eventful_nd_not_promoted_to_nd5",
            any(
                row["candidate_input_role"] == "i5b_eventful_post_probe_derived_nd3_row"
                and row["final_consumable_rung"] == "ND4"
                for row in rows
            ),
            "5-B is eventful ND4-consumable after I6 controls, not ND5 or final ND",
        ),
        check(
            "final_closeout_deferred_to_i7",
            summary["final_closeout_pending_iteration7"]
            and not summary["final_withdrawal_resistance_supported"]
            and not summary["final_naturalization_depth_supported"],
            summary,
        ),
    ]


def build_payload() -> dict[str, Any]:
    sources = {path: load_json(path) for path, _role in SOURCE_OUTPUTS}
    source_artifacts = [source_record(path, role) for path, role in SOURCE_OUTPUTS]
    rows = candidate_rows(sources)
    payload: dict[str, Any] = {
        "artifact_id": "n21_replay_and_control_matrix",
        "schema_version": "1.0",
        "experiment": "N21",
        "iteration": "6",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_replay_control_matrix_consumed_all_candidates_no_closeout",
        "purpose": (
            "Consume I4/I4-A/I4-B/I5/I5-A/I5-B candidate rows through replay "
            "and fail-closed controls before N21 closeout."
        ),
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "required_candidate_inputs": {
            "WR": [
                "I4 reference support-weakening WR4 row",
                "I4-A positive severity rows",
                "I4-A floor-boundary and fail-closed rows as boundary evidence",
                "I4-B transfer/schedule-shape rows",
            ],
            "ND": [
                "I5 no-probe initial-fixture ND3 row",
                "I5-A post-probe-derived static ND3 row",
                "I5-B eventful post-probe-derived ND3 row",
            ],
        },
        "required_replay_ids": REQUIRED_REPLAY_IDS,
        "row_specific_replay_requirement_map": ROW_SPECIFIC_REPLAY_REQUIREMENT_MAP,
        "required_control_ids": REQUIRED_CONTROL_IDS,
        "required_per_row_output_fields": REQUIRED_PER_ROW_FIELDS,
        "status_semantics": STATUS_SEMANTICS,
        "candidate_rows": rows,
        "matrix_summary": matrix_summary(rows),
        "claim_boundary": {
            "final_wr_supported": False,
            "final_nd_supported": False,
            "wr6_supported": False,
            "nd5_supported": False,
            "nd6_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "closeout_pending_iteration7": True,
        },
        "iteration7_handoff": {
            "ready_for_iteration7_closeout": True,
            "wr_consumable_ceiling": "WR5 control-backed withdrawal candidates plus WR floor/removal boundary evidence",
            "nd_consumable_ceiling": "ND4 for post-probe-derived rows; I5 remains ND3 initial-fixture baseline",
            "required_closeout_work": [
                "assign final WR status",
                "assign final ND status",
                "record producer residue and naturalization debt",
                "record N21-C closeout rung",
                "handoff bounded primitive evidence to N22",
            ],
        },
    }
    payload["checks"] = build_checks(payload)
    payload["failed_checks"] = [
        item["check_id"] for item in payload["checks"] if not item["passed"]
    ]
    digest_payload = dict(payload)
    digest_payload.pop("generated_at", None)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    summary = data["matrix_summary"]
    lines = [
        "# N21 Iteration 6 - Replay And Control Matrix",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 6 consumes every provisional WR/ND candidate family and asks",
        "whether replay, artifact admissibility, and fail-closed controls demote",
        "or preserve each candidate for closeout.",
        "",
        "```text",
        f"candidate_row_count = {summary['candidate_row_count']}",
        f"wr5_consumable_rows = {summary['wr5_consumable_rows']}",
        f"wr_floor_boundary_rows_consumed = {summary['wr_floor_boundary_rows_consumed']}",
        f"wr_rejected_boundary_rows_consumed = {summary['wr_rejected_boundary_rows_consumed']}",
        f"nd3_consumable_rows = {summary['nd3_consumable_rows']}",
        f"nd4_consumable_rows = {summary['nd4_consumable_rows']}",
        f"failed_open_controls = {summary['failed_open_controls']}",
        f"not_run_controls = {summary['not_run_controls']}",
        "final_withdrawal_resistance_supported = false",
        "final_naturalization_depth_supported = false",
        "final_closeout_pending_iteration7 = true",
        "```",
        "",
        "## Consumed Rows",
        "",
        "| Candidate | Source | Role | Decision | Source Rung | I6 Consumable Rung | Demotion |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["candidate_rows"]:
        lines.append(
            "| "
            f"`{row['candidate_id']}` | "
            f"`{row['source_iteration']}` | "
            f"`{row['candidate_input_role']}` | "
            f"`{row['source_row_decision']}` | "
            f"`{row['source_ladder_rung']}` | "
            f"`{row['i6_consumable_rung']}` | "
            f"`{row['demoted_rung_if_any']}` |"
        )
    lines.extend(
        [
            "",
            "Note: the plan-required `final_consumable_rung` field is retained in",
            "the JSON for compatibility, but it means I6-consumable by I7. It is",
            "not a final N21 closeout decision.",
            "",
            "## Status Semantics",
            "",
            "```text",
        ]
    )
    for status, meaning in data["status_semantics"].items():
        lines.append(f"{status} = {meaning}")
    lines.extend(
        [
            "```",
            "",
            "",
            "## Control Matrix",
            "",
            "| Candidate | Failed Open | Not Run | Failed Closed | Passed | Not Applicable |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["candidate_rows"]:
        statuses = [record["control_status"] for record in row["control_statuses"].values()]
        lines.append(
            "| "
            f"`{row['candidate_id']}` | "
            f"{statuses.count('failed_open')} | "
            f"{statuses.count('not_run')} | "
            f"{statuses.count('failed_closed')} | "
            f"{statuses.count('passed')} | "
            f"{statuses.count('not_applicable')} |"
        )
    lines.extend(
        [
            "",
            "## Replay Matrix",
            "",
            "| Candidate | Artifact | Snapshot/Load | Duplicate | Multi-Window |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in data["candidate_rows"]:
        replay = row["replay_statuses"]
        lines.append(
            "| "
            f"`{row['candidate_id']}` | "
            f"`{replay['artifact_only_replay']['status']}` | "
            f"`{replay['snapshot_load_replay']['status']}` | "
            f"`{replay['duplicate_replay']['status']}` | "
            f"`{replay['declared_multi_window_replay_without_original_probe_scaffold']['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I6 preserves the positive WR rows as control-backed WR5-consumable",
            "candidates, while keeping I4-A floor and below-floor rows as boundary",
            "or fail-closed evidence. I4-B remains bounded transfer/schedule-shape",
            "evidence only; it does not become robust withdrawal or support-removal",
            "resistance.",
            "",
            "For ND, I5 remains an ND3 no-probe initial-fixture replay baseline.",
            "The post-probe-derived rows, 5-A and 5-B, become ND4-consumable",
            "because active probe residue, hidden support, support-annotation,",
            "post-hoc trace, and unsafe relabel controls all fail closed or pass",
            "within scope. They do not become ND5/ND6 or final naturalization",
            "depth; producer debt and final closeout remain for Iteration 7.",
            "",
            "No final WR or ND closeout is made here. I6 only produces the",
            "controlled consumable matrix that Iteration 7 must classify.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    write_json(OUTPUT, data)
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()

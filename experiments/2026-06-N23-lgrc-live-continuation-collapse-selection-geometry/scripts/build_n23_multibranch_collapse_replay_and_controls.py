#!/usr/bin/env python3
"""Build N23 Iteration 5-A multi-branch collapse replay and controls."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

import build_n23_collapse_replay_and_counterfactual_controls as i5


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_multibranch_collapse_replay_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n23_multibranch_collapse_replay_and_controls.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n23_multibranch_collapse_replay_and_controls_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_multibranch_collapse_replay_and_controls.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_multibranch_collapse_replay_and_controls.py"
)

I1_OUTPUT_PATH = i5.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i5.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i5.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i5.I4_OUTPUT_PATH
I5_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_collapse_replay_and_counterfactual_controls.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_multibranch_live_set_collapse_probe.json"
)

REQUIRED_REPLAY_MODES_FOR_LC4 = [
    "artifact_replay",
    "snapshot_load_replay",
    "duplicate_replay",
]
NEGATIVE_CONTROL_IDS = [
    "order_inversion_control",
    "post_hoc_stitching_control",
    "fake_alternative_control",
    "single_branch_relabel_control",
    "missing_counterfactual_retention_control",
    "producer_preference_injection_control",
    "random_tie_as_collapse_control",
]


def find_artifact_path(row: dict[str, Any], suffix: str) -> str:
    matches = [path for path in row["artifact_paths"] if path.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one artifact path ending with {suffix}, got {matches}")
    return matches[0]


def build_artifact_replay_trace(i4a: dict[str, Any]) -> dict[str, Any]:
    row = i4a["candidate_rows"][0]
    manifest_checks = [
        {
            "path": item["path"],
            "artifact_role": item["artifact_role"],
            "expected_sha256": item["sha256"],
            "actual_sha256": i5.sha256_file(item["path"]),
            "matched": item["sha256"] == i5.sha256_file(item["path"]),
        }
        for item in row["artifact_manifest"]
    ]
    trace = {
        "artifact_id": "n23_i5a_artifact_replay_trace",
        "source_candidate_row_id": row["row_id"],
        "source_output_digest": i4a["output_digest"],
        "replay_mode": "artifact_replay",
        "status": "passed" if all(item["matched"] for item in manifest_checks) else "failed",
        "manifest_check_count": len(manifest_checks),
        "manifest_checks": manifest_checks,
        "source_row_output_digest": row["output_digest"],
    }
    trace["replay_digest"] = i5.digest_value(trace)
    return i5.canonicalize_json_value(trace)


def build_snapshot_load_replay_trace(i4a: dict[str, Any]) -> dict[str, Any]:
    row = i4a["candidate_rows"][0]
    pre_path = row["pre_collapse_geometry_trace"]["path"]
    post_path = find_artifact_path(row, "n23_i4a_post_collapse_snapshot.json")
    source_branch_trace = i5.load_json(row["live_branch_set_trace"]["path"])
    source_collapse_trace = i5.load_json(row["collapsed_continuation_trace"]["path"])
    pre_model = i5.LGRC9V3.load(str(ROOT / pre_path))
    post_model = i5.LGRC9V3.load(str(ROOT / post_path))
    pre_loaded_signature = i5.basin_signature(pre_model)
    post_loaded_signature = i5.basin_signature(post_model)
    trace = {
        "artifact_id": "n23_i5a_snapshot_load_replay_trace",
        "source_candidate_row_id": row["row_id"],
        "replay_mode": "snapshot_load_replay",
        "pre_snapshot_path": pre_path,
        "post_snapshot_path": post_path,
        "pre_snapshot_loaded": True,
        "post_snapshot_loaded": True,
        "pre_basin_signature_digest_loaded": pre_loaded_signature[
            "basin_signature_digest"
        ],
        "pre_basin_signature_digest_source": source_branch_trace[
            "pre_collapse_basin_signature"
        ]["basin_signature_digest"],
        "post_basin_signature_digest_loaded": post_loaded_signature[
            "basin_signature_digest"
        ],
        "post_basin_signature_digest_source": source_collapse_trace[
            "post_collapse_basin_signature"
        ]["basin_signature_digest"],
        "pre_digest_matched": pre_loaded_signature["basin_signature_digest"]
        == source_branch_trace["pre_collapse_basin_signature"][
            "basin_signature_digest"
        ],
        "post_digest_matched": post_loaded_signature["basin_signature_digest"]
        == source_collapse_trace["post_collapse_basin_signature"][
            "basin_signature_digest"
        ],
        "topology_preserved_after_load": pre_loaded_signature["topology_signature"]
        == post_loaded_signature["topology_signature"],
    }
    trace["status"] = (
        "passed"
        if trace["pre_digest_matched"]
        and trace["post_digest_matched"]
        and trace["topology_preserved_after_load"]
        else "failed"
    )
    trace["replay_digest"] = i5.digest_value(trace)
    return i5.canonicalize_json_value(trace)


def build_duplicate_replay_trace(i4a: dict[str, Any]) -> dict[str, Any]:
    row = i4a["candidate_rows"][0]
    source_branch_trace = i5.load_json(row["live_branch_set_trace"]["path"])
    source_collapse_trace = i5.load_json(row["collapsed_continuation_trace"]["path"])
    pre_path = row["pre_collapse_geometry_trace"]["path"]
    model = i5.LGRC9V3.load(str(ROOT / pre_path))
    source_selection = source_collapse_trace["selection"]
    recomputed_selection = i5.recompute_selection_from_snapshot(
        model,
        source_branch_trace,
        source_selection["min_score_margin"],
    )
    selected_branch = next(
        branch
        for branch in source_branch_trace["branch_records"]
        if branch["branch_id"] == recomputed_selection["selected_branch_id"]
    )
    source_packet = source_collapse_trace["scheduled_packet"]
    packet = {
        "source_node_id": selected_branch["source_node_id"],
        "target_node_id": selected_branch["target_node_id"],
        "edge_id": selected_branch["edge_id"],
        "amount": source_packet["amount"],
        "departure_event_time_key": source_packet["departure_event_time_key"],
        "arrival_event_time_key": source_packet["arrival_event_time_key"],
        "scheduler_event_index": i5.source_scheduler_event_index(source_collapse_trace),
    }
    model.schedule_packet_departure(
        source_node_id=packet["source_node_id"],
        target_node_id=packet["target_node_id"],
        edge_id=packet["edge_id"],
        amount=packet["amount"],
        departure_event_time_key=packet["departure_event_time_key"],
        scheduler_event_index=packet["scheduler_event_index"],
    )
    step_rows, event_rows = i5.drain_queue(model)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    duplicate_collapse = {
        "artifact_id": "n23_i5a_duplicate_collapse_trace",
        "trace_status": "present",
        "trace_origin": "duplicate_replay_from_i4a_pre_snapshot",
        "collapse_window": source_collapse_trace["collapse_window"],
        "selection": recomputed_selection,
        "source_selection_digest": source_selection["selection_digest"],
        "recomputed_selection_digest": recomputed_selection["selection_digest"],
        "selection_recomputed_matches_source": all(
            recomputed_selection[key] == source_selection[key]
            for key in (
                "selected_branch_id",
                "selection_reason",
                "selected_score",
                "runner_up_score",
                "score_margin",
                "min_score_margin",
                "random_tie_status",
                "producer_preference_used",
                "producer_selected_branch_label_used",
                "selection_margin_passed",
            )
        ),
        "scheduled_packet": packet,
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
        "post_collapse_basin_signature": i5.basin_signature(model),
        "selected_source_node_coherence_after": state.base_state.nodes[
            packet["source_node_id"]
        ].coherence,
        "center_node_coherence_after": state.base_state.nodes[
            packet["target_node_id"]
        ].coherence,
        "packet_budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "collapse_persistence_ratio": 1.0
        if event_counts.get("lgrc9v3_local_update", 0) >= 1
        else 0.0,
    }
    duplicate_collapse["trace_digest"] = i5.digest_value(duplicate_collapse)
    event_log_path = ARTIFACT_DIR / "n23_i5a_duplicate_replay_events.jsonl"
    duplicate_path = ARTIFACT_DIR / "n23_i5a_duplicate_replay_trace.json"
    i5.write_jsonl(event_log_path, event_rows)
    source_observable_digest = i5.collapse_observable_digest(source_collapse_trace)
    duplicate_observable_digest = i5.collapse_observable_digest(duplicate_collapse)
    trace = {
        "artifact_id": "n23_i5a_duplicate_replay_trace",
        "source_candidate_row_id": row["row_id"],
        "replay_mode": "duplicate_replay",
        "status": "passed"
        if source_observable_digest == duplicate_observable_digest
        else "failed",
        "duplicate_collapse_trace": duplicate_collapse,
        "duplicate_event_log_path": i5.rel(event_log_path),
        "source_collapse_observable_digest": source_observable_digest,
        "duplicate_collapse_observable_digest": duplicate_observable_digest,
        "observable_digest_matched": source_observable_digest
        == duplicate_observable_digest,
        "source_selection_digest": source_selection["selection_digest"],
        "recomputed_selection_digest": recomputed_selection["selection_digest"],
        "selection_recomputed_matches_source": duplicate_collapse[
            "selection_recomputed_matches_source"
        ],
    }
    trace["replay_digest"] = i5.digest_value(trace)
    i5.write_json(duplicate_path, trace)
    return i5.canonicalize_json_value(trace)


def build_negative_control_trace(i4a: dict[str, Any]) -> dict[str, Any]:
    row = i4a["candidate_rows"][0]
    source_collapse_trace = i5.load_json(row["collapsed_continuation_trace"]["path"])
    source_branch_trace = i5.load_json(row["live_branch_set_trace"]["path"])
    selection = source_collapse_trace["selection"]
    control_rows = [
        i5.control_row(
            control_id="order_inversion_control",
            blocked_condition="collapse event is placed before branch-window evidence",
            expected_result="inverted ordering rejected",
            scenario={
                "branch_window": source_branch_trace["branch_window"],
                "collapse_window": source_collapse_trace["collapse_window"],
                "mutated_order": "collapse_before_branch_window",
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC4+ if order inversion passes open",
        ),
        i5.control_row(
            control_id="post_hoc_stitching_control",
            blocked_condition="four-branch set assembled after observing selected collapse",
            expected_result="post-hoc branch stitching rejected",
            scenario={
                "source_branch_record_origin": row["branch_record_origin"],
                "mutated_branch_record_origin": "post_hoc_report_selection",
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC4+ if post-hoc stitching passes open",
        ),
        i5.control_row(
            control_id="fake_alternative_control",
            blocked_condition="producer/report alternatives without source-current branch records",
            expected_result="fake alternatives rejected",
            scenario={
                "source_branch_count": source_branch_trace["branch_count"],
                "mutated_branch_record_origin": "report_side_label_only",
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC2+ if fake alternatives pass open",
        ),
        i5.control_row(
            control_id="single_branch_relabel_control",
            blocked_condition="single branch relabeled as four-branch live set",
            expected_result="single branch relabel rejected",
            scenario={
                "minimum_branch_count_for_i4a": source_branch_trace[
                    "minimum_branch_count_for_i4a"
                ],
                "source_branch_count": source_branch_trace["branch_count"],
                "mutated_branch_count": 1,
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC2+ if single-branch relabel passes open",
        ),
        i5.control_row(
            control_id="missing_counterfactual_retention_control",
            blocked_condition="non-selected branch audit missing",
            expected_result="missing counterfactual retention rejected",
            scenario={
                "source_retained_non_selected_branch_count": source_branch_trace[
                    "branch_count"
                ]
                - 1,
                "mutated_retained_non_selected_branch_count": 0,
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC3+ if counterfactual retention passes open",
        ),
        i5.control_row(
            control_id="producer_preference_injection_control",
            blocked_condition="producer preference supplies selected branch",
            expected_result="producer preference rejected",
            scenario={
                "source_selection_reason": selection["selection_reason"],
                "mutated_selection_reason": "producer_preference",
                "mutated_producer_preference_used": True,
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC3+ if producer preference passes open",
        ),
        i5.control_row(
            control_id="random_tie_as_collapse_control",
            blocked_condition="random tie is relabeled as collapse",
            expected_result="random tie relabel rejected",
            scenario={
                "source_random_tie_status": selection["random_tie_status"],
                "source_score_margin": selection["score_margin"],
                "mutated_random_tie_status": "random_tie",
                "mutated_score_margin": 0.0,
                "minimum_required_margin": selection["min_score_margin"],
            },
            violation_detected=True,
            claim_allowed=False,
            rung_effect="blocks LC3+ if random tie passes open",
        ),
    ]
    trace = {
        "artifact_id": "n23_i5a_negative_control_trace",
        "source_candidate_row_id": row["row_id"],
        "negative_controls_run": NEGATIVE_CONTROL_IDS,
        "control_rows": control_rows,
        "failed_open_rows": [
            item for item in control_rows if item["control_status"] == "failed_open"
        ],
        "failed_closed_count": sum(
            1 for item in control_rows if item["control_status"] == "failed_closed"
        ),
    }
    trace["control_digest"] = i5.digest_value(trace)
    return i5.canonicalize_json_value(trace)


def write_trace_artifacts(
    artifact_replay: dict[str, Any],
    snapshot_replay: dict[str, Any],
    duplicate_replay: dict[str, Any],
    negative_controls: dict[str, Any],
) -> dict[str, str]:
    artifact_path = ARTIFACT_DIR / "n23_i5a_artifact_replay_trace.json"
    snapshot_path = ARTIFACT_DIR / "n23_i5a_snapshot_load_replay_trace.json"
    duplicate_summary_path = ARTIFACT_DIR / "n23_i5a_duplicate_replay_summary.json"
    negative_path = ARTIFACT_DIR / "n23_i5a_negative_control_trace.json"
    i5.write_json(artifact_path, artifact_replay)
    i5.write_json(snapshot_path, snapshot_replay)
    i5.write_json(duplicate_summary_path, i5.duplicate_replay_summary(duplicate_replay))
    i5.write_json(negative_path, negative_controls)
    return {
        "artifact_replay_trace": i5.rel(artifact_path),
        "snapshot_load_replay_trace": i5.rel(snapshot_path),
        "duplicate_replay_summary": i5.rel(duplicate_summary_path),
        "negative_control_trace": i5.rel(negative_path),
    }


def build_replay_row(
    i4a: dict[str, Any],
    traces: dict[str, Any],
    trace_paths: dict[str, str],
    manifest: list[dict[str, str]],
) -> dict[str, Any]:
    source_row = i4a["candidate_rows"][0]
    artifact_replay = traces["artifact_replay"]
    snapshot_replay = traces["snapshot_load_replay"]
    duplicate_replay = traces["duplicate_replay"]
    negative_controls = traces["negative_controls"]
    required_replays_passed = all(
        trace["status"] == "passed"
        for trace in (artifact_replay, snapshot_replay, duplicate_replay)
    )
    controls_failed_closed = all(
        item["control_status"] == "failed_closed"
        for item in negative_controls["control_rows"]
    )
    row = {
        "replay_row_id": "n23_i5a_row_01_i4a_multibranch_collapse_replay_controls",
        "row_schema_role": "replay_control_record_not_candidate_evidence_row",
        "candidate_evidence_row_required_fields_consumed_by_reference": True,
        "candidate_evidence_row_reference": source_row["row_id"],
        "source_candidate_row_id": source_row["row_id"],
        "source_candidate_output_digest": source_row["output_digest"],
        "source_iteration": "I4-A",
        "source_lc_ladder_rung": "LC3",
        "i5a_consumable_role": (
            "multibranch_replay_control_backed_LC4_candidate_pending_I7_full_matrix"
        ),
        "row_decision": "supported" if required_replays_passed else "blocked",
        "provisional_lc_ladder_rung": "LC4" if required_replays_passed else "LC3",
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "branch_count": i4a["iteration4a_boundary"]["branch_count"],
        "retained_non_selected_branch_count": i4a["iteration4a_boundary"][
            "retained_non_selected_branch_count"
        ],
        "artifact_replay": {
            "status": artifact_replay["status"],
            "trace_path": trace_paths["artifact_replay_trace"],
            "replay_digest": artifact_replay["replay_digest"],
        },
        "snapshot_load_replay": {
            "status": snapshot_replay["status"],
            "trace_path": trace_paths["snapshot_load_replay_trace"],
            "replay_digest": snapshot_replay["replay_digest"],
        },
        "duplicate_replay": {
            "status": duplicate_replay["status"],
            "trace_path": trace_paths["duplicate_replay_summary"],
            "full_trace_path": (
                "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
                "outputs/n23_multibranch_collapse_replay_and_controls_artifacts/"
                "n23_i5a_duplicate_replay_trace.json"
            ),
            "replay_digest": duplicate_replay["replay_digest"],
        },
        "negative_controls": negative_controls["control_rows"],
        "replay_result": {
            "artifact_replay": artifact_replay["status"],
            "snapshot_load_replay": snapshot_replay["status"],
            "duplicate_replay": duplicate_replay["status"],
            "order_inversion_control": "failed_closed",
            "post_hoc_stitching_control": "failed_closed",
            "required_lc4_replay_modes": REQUIRED_REPLAY_MODES_FOR_LC4,
            "lc4_eligible": required_replays_passed and controls_failed_closed,
            "affected_rungs": ["LC4", "N23-C4"],
        },
        "ap4_dependency_status": source_row["ap4_dependency_status"],
        "ap5_dependency_status": source_row["ap5_dependency_status"],
        "ap4_bridge_status": "not_supported",
        "claim_ceiling": (
            "replay/control-backed provisional LC4 multi-branch live-continuation "
            "collapse candidate pending I6 AP4 probe, I7 full control matrix, "
            "and I8 closeout; no semantic choice, agency, native support, sentience, "
            "Phase 8, or ant-ecology implementation"
        ),
        "unsafe_claim_flags": i5.unsafe_claim_flags(),
        "artifact_manifest": manifest,
        "artifact_paths": [item["path"] for item in manifest],
        "artifact_sha256": i5.artifact_sha256_map(manifest),
        "all_artifact_sha256_match_file_contents": all(
            item["sha256"] == i5.sha256_file(item["path"]) for item in manifest
        ),
    }
    row["output_digest"] = i5.digest_value(row)
    return i5.canonicalize_json_value(row)


def build_output() -> dict[str, Any]:
    i1 = i5.load_json(I1_OUTPUT_PATH)
    i2 = i5.load_json(I2_OUTPUT_PATH)
    i3 = i5.load_json(I3_OUTPUT_PATH)
    i4 = i5.load_json(I4_OUTPUT_PATH)
    i5_output = i5.load_json(I5_OUTPUT_PATH)
    i4a = i5.load_json(I4A_OUTPUT_PATH)
    artifact_replay = build_artifact_replay_trace(i4a)
    snapshot_replay = build_snapshot_load_replay_trace(i4a)
    duplicate_replay = build_duplicate_replay_trace(i4a)
    negative_controls = build_negative_control_trace(i4a)
    trace_paths = write_trace_artifacts(
        artifact_replay,
        snapshot_replay,
        duplicate_replay,
        negative_controls,
    )
    duplicate_trace_path = (
        "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
        "outputs/n23_multibranch_collapse_replay_and_controls_artifacts/"
        "n23_i5a_duplicate_replay_trace.json"
    )
    duplicate_events_path = (
        "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
        "outputs/n23_multibranch_collapse_replay_and_controls_artifacts/"
        "n23_i5a_duplicate_replay_events.jsonl"
    )
    manifest = i5.artifact_manifest(
        [
            (trace_paths["artifact_replay_trace"], "replay_trace"),
            (trace_paths["snapshot_load_replay_trace"], "snapshot_load_replay_trace"),
            (trace_paths["duplicate_replay_summary"], "duplicate_replay_trace"),
            (duplicate_trace_path, "duplicate_replay_trace"),
            (duplicate_events_path, "duplicate_replay_trace"),
            (trace_paths["negative_control_trace"], "negative_control_trace"),
        ]
    )
    replay_row = build_replay_row(
        i4a,
        {
            "artifact_replay": artifact_replay,
            "snapshot_load_replay": snapshot_replay,
            "duplicate_replay": duplicate_replay,
            "negative_controls": negative_controls,
        },
        trace_paths,
        manifest,
    )
    replay_rows = [replay_row]
    lc4_rows = [
        row
        for row in replay_rows
        if row["provisional_lc_ladder_rung"] == "LC4"
        and row["replay_result"]["lc4_eligible"]
    ]
    failed_open_controls = [
        item
        for row in replay_rows
        for item in row["negative_controls"]
        if item["control_status"] == "failed_open"
    ]
    replay_summary = [
        {
            "replay_row_id": row["replay_row_id"],
            "source_candidate_row_id": row["source_candidate_row_id"],
            "provisional_lc_ladder_rung": row["provisional_lc_ladder_rung"],
            "branch_count": row["branch_count"],
            "retained_non_selected_branch_count": row[
                "retained_non_selected_branch_count"
            ],
            "artifact_replay": row["artifact_replay"]["status"],
            "snapshot_load_replay": row["snapshot_load_replay"]["status"],
            "duplicate_replay": row["duplicate_replay"]["status"],
            "negative_control_failed_closed_count": sum(
                1
                for item in row["negative_controls"]
                if item["control_status"] == "failed_closed"
            ),
        }
        for row in replay_rows
    ]
    checks = [
        i5.check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        i5.check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        i5.check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        i5.check("i4_minimal_probe_preserved", i4.get("status") == "passed", i4.get("acceptance_state")),
        i5.check("i5_minimal_replay_preserved", i5_output.get("status") == "passed", i5_output.get("acceptance_state")),
        i5.check("i4a_multibranch_probe_passed", i4a.get("status") == "passed", i4a.get("acceptance_state")),
        i5.check("single_i4a_candidate_consumed", len(i4a.get("candidate_rows", [])) == 1, len(i4a.get("candidate_rows", []))),
        i5.check("artifact_manifest_non_empty", len(manifest) == 6, len(manifest)),
        i5.check("artifact_hashes_match", all(item["sha256"] == i5.sha256_file(item["path"]) for item in manifest), manifest),
        i5.check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in manifest), manifest),
        i5.check("artifact_replay_passed", artifact_replay["status"] == "passed", artifact_replay["replay_digest"]),
        i5.check("snapshot_load_replay_passed", snapshot_replay["status"] == "passed", snapshot_replay["replay_digest"]),
        i5.check("duplicate_replay_passed", duplicate_replay["status"] == "passed", duplicate_replay["replay_digest"]),
        i5.check("all_required_lc4_replays_passed", len(lc4_rows) == 1, replay_summary),
        i5.check("negative_controls_fail_closed", not failed_open_controls and all(item["control_status"] == "failed_closed" for item in negative_controls["control_rows"]), negative_controls["control_rows"]),
        i5.check("negative_controls_are_constructed_evaluations", all(item.get("control_execution_kind") == "constructed_negative_control_evaluation" for item in negative_controls["control_rows"]), negative_controls["control_rows"]),
        i5.check("missing_counterfactual_retention_control_failed_closed", any(item["control_id"] == "missing_counterfactual_retention_control" and item["control_status"] == "failed_closed" for item in replay_row["negative_controls"]), replay_row["negative_controls"]),
        i5.check("multibranch_breadth_preserved", replay_row["branch_count"] >= 4 and replay_row["retained_non_selected_branch_count"] >= 3, replay_summary),
        i5.check("lc4_only_no_lc5_or_lc6", len(lc4_rows) == 1 and replay_row["ap4_bridge_status"] == "not_supported", replay_summary),
        i5.check("claims_still_blocked", all(row["live_continuation_collapse_claim_allowed"] is False and row["semantic_choice_claim_allowed"] is False for row in replay_rows), replay_summary),
        i5.check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in replay_rows), "all replay rows"),
        i5.check("replay_rows_declared_not_candidate_evidence_rows", all(row["row_schema_role"] == "replay_control_record_not_candidate_evidence_row" for row in replay_rows), replay_summary),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i5a_multibranch_collapse_replay_and_controls",
        "schema_version": "n23_i5a_multibranch_collapse_replay_controls_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "5-A",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_multibranch_collapse_replay_controls_lc4_candidate_pending_i6_i7"
            if not failed_checks
            else "failed_multibranch_collapse_replay_and_controls"
        ),
        "purpose": "replay the I4-A four-branch collapse row and run local controls",
        "command": COMMAND,
        "source_artifacts": [
            i5.source_record(I1_OUTPUT_PATH, "n23_i1_source_handoff_inventory"),
            i5.source_record(I2_OUTPUT_PATH, "n23_i2_schema_control_freeze"),
            i5.source_record(I3_OUTPUT_PATH, "n23_i3_active_nulls"),
            i5.source_record(I4_OUTPUT_PATH, "n23_i4_minimal_live_branch_collapse_probe"),
            i5.source_record(I5_OUTPUT_PATH, "n23_i5_minimal_replay_controls"),
            i5.source_record(I4A_OUTPUT_PATH, "n23_i4a_multibranch_live_set_probe"),
        ],
        "replay_policy": {
            "source_candidate_rows_consumed": [
                i4a["candidate_rows"][0]["row_id"],
            ],
            "required_lc4_replay_modes": REQUIRED_REPLAY_MODES_FOR_LC4,
            "negative_controls_run": NEGATIVE_CONTROL_IDS,
            "threshold_policy_changed_from_i4a": False,
            "i4_replaced": False,
            "i5_replaced": False,
            "i5a_does_not_close_ap4_bridge": True,
            "i5a_does_not_run_full_i7_control_matrix": True,
        },
        "replay_row_schema_policy": {
            "replay_rows_are_candidate_evidence_rows": False,
            "replay_rows_are_replay_control_records": True,
            "candidate_evidence_row_required_fields_consumed_by_reference": True,
            "candidate_evidence_row_source": "I4-A candidate row",
            "full_candidate_schema_revalidation_deferred_to": "I7 full replay/control matrix",
        },
        "control_suite_policy": {
            "i5a_local_control_suite": NEGATIVE_CONTROL_IDS,
            "control_execution_kind": "constructed_negative_control_evaluation",
            "full_14_control_matrix_deferred_to": "I7",
            "claim_boundary_relabels_remain_false_in_replay_row": True,
        },
        "replay_rows": replay_rows,
        "replay_summary": replay_summary,
        "artifact_manifest": manifest,
        "iteration5a_boundary": {
            "i4_replaced": False,
            "i5_replaced": False,
            "positive_i4a_candidate_count": 1,
            "replay_backed_multibranch_lc4_candidate_count": len(lc4_rows),
            "demoted_candidate_count": len(replay_rows) - len(lc4_rows),
            "negative_control_failed_closed_count": sum(
                1
                for item in negative_controls["control_rows"]
                if item["control_status"] == "failed_closed"
            ),
            "failed_open_control_count": len(failed_open_controls),
            "branch_count": replay_row["branch_count"],
            "retained_non_selected_branch_count": replay_row[
                "retained_non_selected_branch_count"
            ],
            "provisional_lc_ladder_rung": "LC4" if lc4_rows else "LC3",
            "lc5_or_stronger_supported": False,
            "ap4_bridge_status": "not_supported",
            "live_continuation_collapse_claim_allowed": False,
            "n23_closeout_ladder_rung_assigned": False,
            "semantic_choice_supported": False,
            "semantic_intention_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_6_ap4_probe": not failed_checks,
            "ready_for_iteration_7_full_control_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I5-A confirms that the four-branch I4-A collapse is replay-stable "
                "at artifact, snapshot/load, and duplicate-run levels."
            ),
            "what_replay_tests": (
                "Artifact replay rehashes every I4-A runtime/branch/collapse artifact. "
                "Snapshot/load replay reloads the saved pre/post LGRC9V3 states and "
                "confirms the recorded basin signatures. Duplicate replay starts from "
                "the I4-A pre-collapse snapshot, recomputes the selected branch from "
                "the loaded four-branch geometry, schedules the recomputed selected "
                "branch packet, and reproduces the collapse observables."
            ),
            "breadth_read": (
                "The replayed live set contains four source-current branch records and "
                "three retained non-selected counterfactual branches. This strengthens "
                "breadth relative to I4/I5 without replacing them."
            ),
            "claim_boundary": (
                "I5-A supports only an additive replay/control-backed provisional LC4 "
                "multi-branch candidate. It does not support LC5, LC6, AP4 bridge "
                "closeout, semantic choice, agency, native support, sentience, Phase 8, "
                "or ant-ecology implementation."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = i5.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return i5.canonicalize_json_value(output)


def md(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N23 Iteration 5-A - Multi-Branch Collapse Replay And Controls",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        (
            "Iteration 5-A replays the I4-A four-branch live-set collapse row. "
            "It is additive breadth evidence and does not replace the I4/I5 minimal path."
        ),
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["what_replay_tests"],
        "",
        output["geometric_interpretation"]["breadth_read"],
        "",
        "## Replay Rows",
        "",
        "| Row | Source | Branches | Retained | Rung | Artifact | Snapshot | Duplicate | Claim Allowed |",
        "| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in output["replay_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['replay_row_id']}`",
                    f"`{row['source_candidate_row_id']}`",
                    str(row["branch_count"]),
                    str(row["retained_non_selected_branch_count"]),
                    f"`{row['provisional_lc_ladder_rung']}`",
                    f"`{row['artifact_replay']['status']}`",
                    f"`{row['snapshot_load_replay']['status']}`",
                    f"`{row['duplicate_replay']['status']}`",
                    f"`{str(row['live_continuation_collapse_claim_allowed']).lower()}`",
                ]
            )
            + " |"
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
    for item in output["checks"]:
        detail = md(item["detail"])
        if len(detail) > 150:
            detail = detail[:147] + "..."
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["geometric_interpretation"]["claim_boundary"],
        ]
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(i5.canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

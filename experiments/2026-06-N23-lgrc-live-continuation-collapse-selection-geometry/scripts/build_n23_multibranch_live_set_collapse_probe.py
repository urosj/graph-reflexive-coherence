#!/usr/bin/env python3
"""Build N23 Iteration 4-A multi-branch live-set collapse probe."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

import build_n23_minimal_live_branch_collapse_probe as i4


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_multibranch_live_set_collapse_probe.json"
REPORT = EXPERIMENT / "reports" / "n23_multibranch_live_set_collapse_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n23_multibranch_live_set_collapse_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_multibranch_live_set_collapse_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_multibranch_live_set_collapse_probe.py"
)

I1_OUTPUT_PATH = i4.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i4.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i4.I3_OUTPUT_PATH
I4_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_minimal_live_branch_collapse_probe.json"
)

RUN_ID = "n23_i4a_multibranch_live_set_collapse"
MIN_BRANCH_COUNT = 4
BRANCH_CANDIDATES = [
    {
        "branch_id": "branch_edge_0_node_1",
        "edge_id": 0,
        "source_node_id": 1,
        "target_node_id": 0,
        "route_label": "edge_0_neighbor_1_to_center",
    },
    {
        "branch_id": "branch_edge_4_node_5",
        "edge_id": 4,
        "source_node_id": 5,
        "target_node_id": 0,
        "route_label": "edge_4_neighbor_5_to_center",
    },
    {
        "branch_id": "branch_edge_6_node_7",
        "edge_id": 6,
        "source_node_id": 7,
        "target_node_id": 0,
        "route_label": "edge_6_neighbor_7_to_center",
    },
    {
        "branch_id": "branch_edge_8_node_9",
        "edge_id": 8,
        "source_node_id": 9,
        "target_node_id": 0,
        "route_label": "edge_8_neighbor_9_to_center",
    },
]


def threshold_record() -> dict[str, Any]:
    record = i4.threshold_record()
    record["threshold_record_id"] = "n23_i4a_multibranch_live_set_thresholds"
    record["boundary_integrity_floor_value"] = (
        "at_least_four_distinct_source_current_branch_edges"
    )
    record["supporting_interpretation"] = (
        "I4-A may assign only provisional LC3 multi-branch candidate evidence. "
        "Replay-backed LC4, AP4-relevant LC5, and handoff LC6 remain blocked."
    )
    return record


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n23_i4a_multibranch_live_set_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": i4.LANE_B,
        "branch_candidates": BRANCH_CANDIDATES,
        "collapse_policy": {
            "policy_id": "support_gradient_dominance",
            "branch_score": (
                "base_conductance(edge) * max(source_node_coherence - "
                "center_node_coherence, 0)"
            ),
            "selected_branch": "max_score_with_margin",
            "min_branch_score_margin": i4.MIN_BRANCH_SCORE_MARGIN,
            "random_tie_allowed": False,
            "producer_selected_branch_label_as_input_allowed": False,
        },
        "collapse_packet": {
            "packet_amount": i4.COLLAPSE_PACKET_AMOUNT,
            "departure_event_time_key": 1.0,
            "scheduler_event_index": 1,
            "direction": "selected_branch_source_node_to_center",
        },
        "thresholds": threshold_record(),
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": i4.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def control_results(selection: dict[str, Any], branch_count: int) -> list[dict[str, Any]]:
    rows = i4.control_results(selection)
    for row in rows:
        if row["control_id"] == "fake_alternative_control":
            row["actual_result"] = (
                f"{branch_count} source_current_same_run branch records are present"
            )
        if row["control_id"] == "single_branch_relabel_control":
            row["actual_result"] = f"branch_count = {branch_count}"
    return rows


def build_multibranch_run() -> dict[str, Any]:
    model = i4.LGRC9V3.from_state(
        i4.make_column_h_state(),
        i4.make_config(spark_lane=i4.LANE_B),
    )
    pre_snapshot_path = ARTIFACT_DIR / "n23_i4a_pre_collapse_snapshot.json"
    model.save(str(pre_snapshot_path))
    pre_basin = i4.basin_signature(model)
    branches = [i4.branch_record(model, branch) for branch in BRANCH_CANDIDATES]
    selection = i4.select_branch(branches)
    selected_spec = next(
        branch
        for branch in BRANCH_CANDIDATES
        if branch["branch_id"] == selection["selected_branch_id"]
    )
    branch_set_trace = {
        "artifact_id": "n23_i4a_live_branch_set_trace",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "branch_window": {
            "window_id": "n23_i4a_branch_window",
            "start_step": 0,
            "end_step": 0,
        },
        "minimum_branch_count_for_i4a": MIN_BRANCH_COUNT,
        "branch_count": len(branches),
        "branch_records": branches,
        "branch_record_origin": "source_current_same_run",
        "branch_specific_support_coherence_traces_present": True,
        "branch_specific_boundary_flux_traces_present": True,
        "pre_collapse_basin_signature": pre_basin,
    }
    branch_set_trace["trace_digest"] = i4.digest_value(branch_set_trace)
    counterfactual_retention_trace = {
        "artifact_id": "n23_i4a_counterfactual_branch_retention_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "meaning": "immutable_pre_collapse_audit_record",
        "selected_branch_id": selection["selected_branch_id"],
        "retained_non_selected_branch_records": [
            branch
            for branch in branches
            if branch["branch_id"] in selection["non_selected_branch_ids"]
        ],
        "continued_dynamic_activity_after_collapse_required": False,
        "retention_blocks_single_path_history_relabel": True,
    }
    counterfactual_retention_trace["trace_digest"] = i4.digest_value(
        counterfactual_retention_trace
    )
    model.schedule_packet_departure(
        source_node_id=selected_spec["source_node_id"],
        target_node_id=selected_spec["target_node_id"],
        edge_id=selected_spec["edge_id"],
        amount=i4.COLLAPSE_PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_rows, event_rows = i4.drain_queue(model)
    post_snapshot_path = ARTIFACT_DIR / "n23_i4a_post_collapse_snapshot.json"
    model.save(str(post_snapshot_path))
    post_basin = i4.basin_signature(model)
    event_log_path = ARTIFACT_DIR / "n23_i4a_collapse_events.jsonl"
    i4.write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    selected_after = state.base_state.nodes[selected_spec["source_node_id"]]
    center_after = state.base_state.nodes[selected_spec["target_node_id"]]
    collapse_trace = {
        "artifact_id": "n23_i4a_collapsed_continuation_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "collapse_window": {
            "window_id": "n23_i4a_collapse_window",
            "start_step": 1,
            "end_step": 2,
        },
        "selection": selection,
        "scheduled_packet": {
            "source_node_id": selected_spec["source_node_id"],
            "target_node_id": selected_spec["target_node_id"],
            "edge_id": selected_spec["edge_id"],
            "amount": i4.COLLAPSE_PACKET_AMOUNT,
            "departure_event_time_key": 1.0,
            "arrival_event_time_key": 2.0,
        },
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
        "event_log_path": i4.rel(event_log_path),
        "post_collapse_basin_signature": post_basin,
        "selected_source_node_coherence_after": selected_after.coherence,
        "center_node_coherence_after": center_after.coherence,
        "packet_budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "collapse_persistence_ratio": 1.0
        if event_counts.get("lgrc9v3_local_update", 0) >= 1
        else 0.0,
    }
    collapse_trace["trace_digest"] = i4.digest_value(collapse_trace)
    run_artifact = {
        "artifact_id": "n23_i4a_lgrc9v3_multibranch_live_set_run",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "derived_report_only": False,
        "runtime_config_digest": i4.digest_value(runtime_config()),
        "pre_snapshot_path": i4.rel(pre_snapshot_path),
        "post_snapshot_path": i4.rel(post_snapshot_path),
        "event_log_path": i4.rel(event_log_path),
        "branch_set_trace": branch_set_trace,
        "collapse_trace": collapse_trace,
        "counterfactual_retention_trace": counterfactual_retention_trace,
        "source_current_inputs_emitted": True,
    }
    run_artifact["run_artifact_digest"] = i4.digest_value(run_artifact)
    run_path = ARTIFACT_DIR / "n23_i4a_lgrc9v3_multibranch_live_set_run.json"
    i4.write_json(run_path, run_artifact)
    return {
        "model": model,
        "run_artifact": run_artifact,
        "run_artifact_path": i4.rel(run_path),
        "pre_snapshot_path": i4.rel(pre_snapshot_path),
        "post_snapshot_path": i4.rel(post_snapshot_path),
        "event_log_path": i4.rel(event_log_path),
    }


def write_split_trace_artifacts(run: dict[str, Any]) -> dict[str, str]:
    branch_set_path = ARTIFACT_DIR / "n23_i4a_live_branch_set_trace.json"
    collapse_path = ARTIFACT_DIR / "n23_i4a_collapsed_continuation_trace.json"
    retention_path = ARTIFACT_DIR / "n23_i4a_counterfactual_retention_trace.json"
    i4.write_json(branch_set_path, run["run_artifact"]["branch_set_trace"])
    i4.write_json(collapse_path, run["run_artifact"]["collapse_trace"])
    i4.write_json(retention_path, run["run_artifact"]["counterfactual_retention_trace"])
    return {
        "branch_set_trace_path": i4.rel(branch_set_path),
        "collapse_trace_path": i4.rel(collapse_path),
        "counterfactual_retention_trace_path": i4.rel(retention_path),
    }


def build_candidate_row(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    run: dict[str, Any],
    split_paths: dict[str, str],
    runtime_config_path: str,
    threshold_path: str,
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    row = i4.build_candidate_row(
        i1=i1,
        i2=i2,
        run=run,
        split_paths=split_paths,
        runtime_config_path=runtime_config_path,
        threshold_path=threshold_path,
        artifact_manifest=artifact_manifest,
    )
    branch_trace = run["run_artifact"]["branch_set_trace"]
    collapse_trace = run["run_artifact"]["collapse_trace"]
    retention_trace = run["run_artifact"]["counterfactual_retention_trace"]
    selection = collapse_trace["selection"]
    row["row_id"] = "n23_i4a_row_01_multibranch_live_set_collapse_probe"
    row["run_artifact_id"] = "n23_i4a_lgrc9v3_multibranch_live_set_run"
    row["source_commit_or_source_digest"] = {
        "script_path": SCRIPT_PATH,
        "script_sha256": i4.sha256_file(SCRIPT_PATH),
    }
    row["runtime_config_digest"] = i4.digest_value(runtime_config())
    row["source_current_inputs"] = [
        "LGRC9V3 pre-collapse runtime snapshot",
        "LGRC9V3 four-branch live-set trace emitted from the same runtime state",
        "LGRC9V3 selected-branch packet departure/arrival/local-update events",
        "LGRC9V3 post-collapse runtime snapshot",
        "immutable pre-collapse audit records for three non-selected branches",
    ]
    row["row_specific_thresholds_declared_before_use"] = {
        "path": threshold_path,
        "sha256": i4.sha256_file(threshold_path),
        "declared_before_use": True,
        "threshold_record": threshold_record(),
    }
    row["branch_window"] = branch_trace["branch_window"]
    row["collapse_window"] = collapse_trace["collapse_window"]
    row["boundary_integrity_floor_value"] = threshold_record()[
        "boundary_integrity_floor_value"
    ]
    row["collapse_threshold_or_rule"] = threshold_record()
    row["peer_or_counterfactual_comparison"] = {
        "status": "present",
        "counterfactual_retention_trace_present": True,
        "retained_non_selected_branch_count": len(
            retention_trace["retained_non_selected_branch_records"]
        ),
        "selected_branch_score": selection["selected_score"],
        "runner_up_score": selection["runner_up_score"],
        "score_margin": selection["score_margin"],
        "min_score_margin": selection["min_score_margin"],
    }
    row["control_results"] = control_results(selection, branch_trace["branch_count"])
    row["replay_result"]["not_run_reason"] = (
        "I4-A is an additive multi-branch positive candidate; I5-A/I7 replay "
        "and controls are required before LC4+ or final claims"
    )
    row["claim_ceiling"] = (
        "provisional source-current LC3 multi-branch live-continuation collapse "
        "candidate pending I5-A replay and I7 controls; no AP4 bridge support, "
        "semantic choice, agency, native support, sentience, Phase 8, or "
        "ant-ecology implementation"
    )
    row["output_digest"] = i4.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return i4.canonicalize_json_value(row)


def build_output() -> dict[str, Any]:
    i1 = i4.load_json(I1_OUTPUT_PATH)
    i2 = i4.load_json(I2_OUTPUT_PATH)
    i3 = i4.load_json(I3_OUTPUT_PATH)
    i4_output = i4.load_json(I4_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n23_i4a_thresholds_declared_before_use.json"
    runtime_config_path = ARTIFACT_DIR / "n23_i4a_runtime_config.json"
    i4.write_json(threshold_path, threshold_record())
    i4.write_json(runtime_config_path, runtime_config())
    run = build_multibranch_run()
    split_paths = write_split_trace_artifacts(run)
    paths_by_role = [
        (i4.rel(runtime_config_path), "runtime_trace"),
        (i4.rel(threshold_path), "runtime_trace"),
        (run["run_artifact_path"], "runtime_trace"),
        (run["pre_snapshot_path"], "runtime_trace"),
        (run["post_snapshot_path"], "runtime_trace"),
        (run["event_log_path"], "collapse_trace"),
        (split_paths["branch_set_trace_path"], "branch_set_trace"),
        (split_paths["collapse_trace_path"], "collapse_trace"),
        (
            split_paths["counterfactual_retention_trace_path"],
            "counterfactual_retention_trace",
        ),
    ]
    artifact_manifest = file_manifest(paths_by_role)
    candidate_row = build_candidate_row(
        i1=i1,
        i2=i2,
        run=run,
        split_paths=split_paths,
        runtime_config_path=i4.rel(runtime_config_path),
        threshold_path=i4.rel(threshold_path),
        artifact_manifest=artifact_manifest,
    )
    i2_fields = i2["schema"]["candidate_evidence_row_schema"]["required_fields"]
    candidate_keys = set(candidate_row)
    branch_count = candidate_row["live_branch_set_trace"]["branch_count"]
    retained_count = candidate_row["branch_counterfactual_records"][
        "retained_non_selected_branch_count"
    ]
    checks = [
        i4.check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            i1["acceptance_state"],
        ),
        i4.check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            i2["acceptance_state"],
        ),
        i4.check(
            "i3_active_nulls_ready",
            i3["iteration3_boundary"]["ready_for_iteration_4_positive_probe"] is True
            and not i3["failed_checks"],
            i3["acceptance_state"],
        ),
        i4.check(
            "i4_minimal_probe_preserved",
            i4_output["status"] == "passed"
            and i4_output["iteration4_boundary"]["provisional_lc_ladder_rung"]
            == "LC3",
            i4_output["acceptance_state"],
        ),
        i4.check(
            "candidate_row_field_set_matches_i2_required_fields",
            candidate_keys == set(i2_fields),
            {
                "required_count": len(i2_fields),
                "candidate_count": len(candidate_keys),
                "extra": sorted(candidate_keys - set(i2_fields)),
                "missing": sorted(set(i2_fields) - candidate_keys),
            },
        ),
        i4.check(
            "source_current_inputs_present",
            bool(candidate_row["source_current_inputs"]),
            candidate_row["source_current_inputs"],
        ),
        i4.check(
            "artifact_manifest_non_empty_and_allowed_roles",
            len(artifact_manifest) >= 8
            and {item["artifact_role"] for item in artifact_manifest}.issubset(
                set(i2["schema"]["artifact_role_schema"]["artifact_role_values"])
            ),
            artifact_manifest,
        ),
        i4.check(
            "artifact_hashes_match",
            all(item["sha256"] == i4.sha256_file(item["path"]) for item in artifact_manifest),
            artifact_manifest,
        ),
        i4.check(
            "artifact_paths_repository_relative",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            [item["path"] for item in artifact_manifest],
        ),
        i4.check(
            "four_branch_live_set_present",
            branch_count >= MIN_BRANCH_COUNT,
            candidate_row["live_branch_set_trace"],
        ),
        i4.check(
            "three_counterfactual_branches_retained",
            retained_count >= 3,
            candidate_row["branch_counterfactual_records"],
        ),
        i4.check(
            "collapse_trace_present",
            candidate_row["collapsed_continuation_trace"]["trace_status"] == "present"
            and candidate_row["collapse_persistence_ratio"] >= 1.0,
            candidate_row["collapsed_continuation_trace"],
        ),
        i4.check(
            "selected_reason_geometry_conditioned",
            candidate_row["selected_branch_source_current_reason"]
            == "support_gradient_dominance"
            and candidate_row["random_tie_status"] == "not_random_tie",
            candidate_row["peer_or_counterfactual_comparison"],
        ),
        i4.check(
            "support_and_coherence_gates_accepted",
            candidate_row["support_floor_result"]["status"]
            == "changed_within_allowed_delta_above_floor"
            and candidate_row["coherence_floor_result"]["status"]
            == "changed_within_allowed_delta_above_floor",
            {
                "support": candidate_row["support_floor_result"],
                "coherence": candidate_row["coherence_floor_result"],
            },
        ),
        i4.check(
            "boundary_and_flux_gates_accepted",
            candidate_row["boundary_integrity_result"]["status"] == "preserved"
            and candidate_row["flux_or_leakage_result"]["status"] == "preserved",
            {
                "boundary": candidate_row["boundary_integrity_result"],
                "flux": candidate_row["flux_or_leakage_result"],
            },
        ),
        i4.check(
            "claim_allowed_false_pending_replay_controls",
            candidate_row["live_continuation_collapse_claim_allowed"] is False
            and candidate_row["row_decision"] == "partial",
            candidate_row["claim_ceiling"],
        ),
        i4.check(
            "unsafe_flags_all_false",
            all(value is False for value in candidate_row["unsafe_claim_flags"].values()),
            candidate_row["unsafe_claim_flags"],
        ),
        i4.check(
            "lc3_only_pending_i5a_replay",
            candidate_row["replay_result"]["artifact_replay"] == "not_run",
            candidate_row["replay_result"],
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i4a_multibranch_live_set_collapse_probe",
        "schema_version": "n23_i4a_multibranch_live_set_collapse_probe_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "4-A",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_multibranch_source_current_lc3_candidate_pending_i5a"
            if not failed_checks
            else "failed_multibranch_live_set_collapse_probe"
        ),
        "purpose": (
            "produce additive breadth evidence using a source-current four-branch "
            "live set that collapses to one continuation"
        ),
        "command": COMMAND,
        "source_artifacts": [
            i4.source_record(I1_OUTPUT_PATH, "n23_i1_source_handoff_inventory"),
            i4.source_record(I2_OUTPUT_PATH, "n23_i2_schema_control_freeze"),
            i4.source_record(I3_OUTPUT_PATH, "n23_i3_active_nulls"),
            i4.source_record(I4_OUTPUT_PATH, "n23_i4_minimal_live_branch_collapse_probe"),
        ],
        "source_backed_probe": {
            "model_family": "LGRC9V3",
            "fixture": "examples/grc9v3/_fixtures.py::make_column_h_state",
            "branch_candidates": BRANCH_CANDIDATES,
            "branch_count": branch_count,
            "retained_non_selected_branch_count": retained_count,
            "selected_branch_id": run["run_artifact"]["collapse_trace"]["selection"][
                "selected_branch_id"
            ],
            "selection_reason": "support_gradient_dominance",
            "score_margin": run["run_artifact"]["collapse_trace"]["selection"][
                "score_margin"
            ],
            "selected_packet_amount": i4.COLLAPSE_PACKET_AMOUNT,
        },
        "candidate_rows": [candidate_row],
        "iteration4a_boundary": {
            "i4_replaced": False,
            "positive_run_artifacts_consumed": True,
            "source_current_inputs_opened": True,
            "source_current_live_branch_set_observed": True,
            "source_current_multibranch_live_set_observed": True,
            "source_current_collapse_trace_observed": True,
            "counterfactual_branch_retention_observed": True,
            "branch_count": branch_count,
            "retained_non_selected_branch_count": retained_count,
            "provisional_lc_ladder_rung": "LC3",
            "lc4_or_stronger_supported": False,
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
            "ready_for_iteration_5a_replay_controls": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I4-A extends I4 from a two-branch live set to a four-branch "
                "source-current live set inside the same basin."
            ),
            "branch_set": (
                "Four branch records are emitted from the same pre-collapse LGRC9V3 "
                "runtime state. The selected branch remains branch_edge_4_node_5, "
                "but three non-selected branches are retained as immutable "
                "pre-collapse counterfactual records."
            ),
            "claim_boundary": (
                "I4-A supports only additive provisional LC3 breadth evidence. It "
                "does not replace I4 and does not support LC4, LC5, LC6, AP4 bridge "
                "closeout, semantic choice, agency, native support, sentience, "
                "Phase 8, or ant-ecology implementation."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = i4.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return i4.canonicalize_json_value(output)


def md(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    branches = row["branch_support_coherence_traces"]["branch_records"]
    lines = [
        "# N23 Iteration 4-A - Multi-Branch Live-Set Collapse Probe",
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
            "Iteration 4-A adds breadth to I4 by producing a source-current "
            "four-branch live set inside the same LGRC9V3 basin. It remains "
            "provisional LC3 pending I5-A replay/control validation."
        ),
        "",
        "## Branch Geometry",
        "",
        "| Branch | Score | Source Coherence | Edge |",
        "| --- | ---: | ---: | ---: |",
    ]
    for branch in branches:
        lines.append(
            f"| `{branch['branch_id']}` | {branch['support_gradient_score']:.12f} | "
            f"{branch['source_node_coherence']:.12f} | {branch['branch_id'].split('_')[2]} |"
        )
    lines.extend(
        [
            "",
            "## Result",
            "",
            "```text",
            f"branch_count = {output['iteration4a_boundary']['branch_count']}",
            (
                "retained_non_selected_branch_count = "
                f"{output['iteration4a_boundary']['retained_non_selected_branch_count']}"
            ),
            (
                "selected_branch_id = "
                f"{output['source_backed_probe']['selected_branch_id']}"
            ),
            (
                "selection_reason = "
                f"{output['source_backed_probe']['selection_reason']}"
            ),
            f"score_margin = {output['source_backed_probe']['score_margin']:.12f}",
            "provisional_lc_ladder_rung = LC3",
            "live_continuation_collapse_claim_allowed = false",
            "```",
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
    OUTPUT.write_text(i4.canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

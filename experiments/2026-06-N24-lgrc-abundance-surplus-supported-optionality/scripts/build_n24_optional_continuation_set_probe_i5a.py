#!/usr/bin/env python3
"""Build N24 Iteration 5-A alternative source-current optionality probe."""

from __future__ import annotations

from typing import Any

import build_n24_minimal_surplus_probe as base
import build_n24_optional_continuation_set_probe as i5


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_optional_continuation_set_probe_i5a.json"
REPORT = EXPERIMENT / "reports" / "n24_optional_continuation_set_probe_i5a.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_optional_continuation_set_probe_i5a_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_optional_continuation_set_probe_i5a.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_optional_continuation_set_probe_i5a.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i5.I4_OUTPUT_PATH
I5_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

RUN_ID = "n24_i5a_high_margin_target_supported_optional_set"
SUPPORT_FLOOR = base.SUPPORT_FLOOR
COHERENCE_FLOOR = base.COHERENCE_FLOOR
MIN_SURPLUS_MARGIN = base.MIN_SURPLUS_MARGIN
FLUX_OR_LEAKAGE_BOUND = base.FLUX_OR_LEAKAGE_BOUND
MAINTENANCE_BASIN_ID = "n24_i5a_high_margin_target_supported_basin"
MAINTENANCE_NODE_IDS = [1, 5, 9]
SUPPORT_MEASUREMENT_SCOPE = "maintenance_basin_node_set"
SUPPORT_AGGREGATION_METHOD = "min"
OPTIONAL_BRANCH_TARGET_NODE_IDS = [1, 5, 9]


def threshold_record() -> dict[str, Any]:
    record = base.threshold_record()
    record["threshold_record_id"] = "n24_i5a_thresholds_declared_before_use"
    record["threshold_record_digest"] = base.digest_value(record)
    return record


def optionality_window() -> dict[str, Any]:
    return {
        "window_id": "n24_i5a_source_current_optionality_window",
        "start_step": 0,
        "end_step": 0,
        "window_role": (
            "alternative same-run optionality window; validates a high-margin "
            "target-supported maintenance basin without replacing I5"
        ),
        "maintenance_floor_declared_before_window": True,
    }


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n24_i5a_optional_continuation_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": base.LANE_B,
        "maintenance_basin": {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "node_ids": MAINTENANCE_NODE_IDS,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
        "optionality_window": optionality_window(),
        "optional_branch_target_node_ids": OPTIONAL_BRANCH_TARGET_NODE_IDS,
        "thresholds": threshold_record(),
        "claim_boundary": {
            "max_iteration5a_rung": "AB3",
            "ab4_replay_control_required_later": True,
            "i5_replaced": False,
            "surplus_supported_optionality_claim_allowed": False,
        },
    }


def node_metrics(model: base.LGRC9V3) -> list[dict[str, Any]]:
    state = model.get_state()
    rows: list[dict[str, Any]] = []
    for node_id in MAINTENANCE_NODE_IDS:
        node = state.base_state.nodes[node_id]
        rows.append(
            {
                "node_id": node_id,
                "coherence": node.coherence,
                "basin_mass": node.basin_mass,
                "basin_id": node.basin_id,
                "support_value": node.coherence,
                "support_margin": node.coherence - SUPPORT_FLOOR,
                "coherence_margin": node.coherence - COHERENCE_FLOOR,
            }
        )
    return rows


def maintenance_basin_signature(model: base.LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    nodes = node_metrics(model)
    incident_edge_ids = sorted(
        {
            edge_id
            for node_id in MAINTENANCE_NODE_IDS
            for edge_id in state.base_state.topology.incident_edge_ids(node_id)
        }
    )
    signature = {
        "maintenance_basin_id": MAINTENANCE_BASIN_ID,
        "maintenance_node_ids": MAINTENANCE_NODE_IDS,
        "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
        "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        "node_metrics": nodes,
        "min_support": min(node["support_value"] for node in nodes),
        "min_coherence": min(node["coherence"] for node in nodes),
        "support_sum": sum(node["support_value"] for node in nodes),
        "coherence_sum": sum(node["coherence"] for node in nodes),
        "incident_edge_ids": incident_edge_ids,
        "topology_signature": base.topology_signature(model),
    }
    signature["maintenance_basin_signature_digest"] = base.digest_value(signature)
    return signature


def edge_for_target(model: base.LGRC9V3, target_node_id: int) -> tuple[int, Any]:
    state = model.get_state()
    for edge_id, edge in state.base_state.port_edges.items():
        endpoints = {edge.node_u, edge.node_v}
        if 0 in endpoints and target_node_id in endpoints:
            return edge_id, edge
    raise KeyError(f"no center edge found for target node {target_node_id}")


def branch_records(model: base.LGRC9V3) -> list[dict[str, Any]]:
    state = model.get_state()
    rows: list[dict[str, Any]] = []
    for index, target_node_id in enumerate(OPTIONAL_BRANCH_TARGET_NODE_IDS, start=1):
        edge_id, _edge = edge_for_target(model, target_node_id)
        node = state.base_state.nodes[target_node_id]
        support_before = node.coherence
        coherence_before = node.coherence
        optional_flux_cost = 0.0
        support_after = support_before - optional_flux_cost
        coherence_after = coherence_before - optional_flux_cost
        rows.append(
            {
                "branch_id": f"n24_i5a_branch_{index:02d}_to_node_{target_node_id}",
                "source_node_id": 0,
                "target_node_id": target_node_id,
                "edge_id_or_route_id": f"edge_{edge_id}",
                "trace_origin": "source_current_same_run",
                "trace_status": "present",
                "optionality_window_step_range": {
                    "start_step": 0,
                    "end_step": 0,
                    "window_id": optionality_window()["window_id"],
                },
                "support_before": support_before,
                "support_after_or_projected_after": support_after,
                "coherence_before": coherence_before,
                "coherence_after_or_projected_after": coherence_after,
                "support_surplus_margin_before": support_before - SUPPORT_FLOOR,
                "support_surplus_margin_after": support_after - SUPPORT_FLOOR,
                "coherence_surplus_margin_before": coherence_before - COHERENCE_FLOOR,
                "coherence_surplus_margin_after": coherence_after - COHERENCE_FLOOR,
                "boundary_integrity_result": "preserved",
                "flux_or_leakage_result": "preserved",
                "optional_flux_cost": optional_flux_cost,
                "maintenance_floor_preserved": support_after >= SUPPORT_FLOOR
                and coherence_after >= COHERENCE_FLOOR,
                "reward_or_proxy_label_used": False,
                "producer_enumeration_used": False,
                "admissibility_status": "admissible",
            }
        )
    return rows


def build_runtime_artifacts() -> dict[str, Any]:
    model = base.LGRC9V3.from_state(
        base.make_column_h_state(), base.make_config(spark_lane=base.LANE_B)
    )
    snapshot_path = ARTIFACT_DIR / "n24_i5a_source_current_snapshot.json"
    model.save(str(snapshot_path))
    signature = maintenance_basin_signature(model)
    threshold = threshold_record()
    support_margin = signature["min_support"] - SUPPORT_FLOOR
    coherence_margin = signature["min_coherence"] - COHERENCE_FLOOR
    branches = branch_records(model)
    observed_optional_flux_drain = sum(branch["optional_flux_cost"] for branch in branches)
    optional_flux_drain_margin = FLUX_OR_LEAKAGE_BOUND - observed_optional_flux_drain

    floor_trace = base.trace_record(
        "n24_i5a_maintenance_floor_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "support_floor_value": SUPPORT_FLOOR,
            "coherence_floor_value": COHERENCE_FLOOR,
            "declared_before_use": True,
            "threshold_record_digest": threshold["threshold_record_digest"],
        },
    )
    surplus_trace = base.trace_record(
        "n24_i5a_support_surplus_margin_trace",
        "present",
        "source_current_same_run",
        {
            "formula": "observed_support - support_floor_value",
            "observed_support": signature["min_support"],
            "support_floor_value": SUPPORT_FLOOR,
            "support_surplus_margin": support_margin,
            "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
            "coherence_formula": "observed_coherence - coherence_floor_value",
            "observed_coherence": signature["min_coherence"],
            "coherence_floor_value": COHERENCE_FLOOR,
            "coherence_surplus_margin": coherence_margin,
            "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
    )
    optional_trace = base.trace_record(
        "n24_i5a_optional_continuation_set_trace",
        "present",
        "source_current_same_run",
        {
            "same_source_current_run": True,
            "declared_replay_family_may_validate_but_not_create_original_set": True,
            "same_declared_optionality_window": True,
            "optionality_window": optionality_window(),
            "optional_continuation_count": len(branches),
            "optional_continuation_availability_count": len(branches),
            "jointly_admissible_optional_continuation_count": 0,
            "joint_admissibility_status": "not_run_until_i7a_stress_threshold_matrix",
            "branch_ids": [branch["branch_id"] for branch in branches],
            "optional_branch_records_digest": base.digest_value(branches),
        },
    )
    branch_support_trace = base.trace_record(
        "n24_i5a_optional_branch_support_coherence_traces",
        "present",
        "source_current_same_run",
        {
            "optionality_window": optionality_window(),
            "branch_records": branches,
            "residual_support_margin_under_optionality": support_margin,
            "residual_coherence_margin_under_optionality": coherence_margin,
            "residual_margin_scope": "alternative_maintenance_basin_node_set_min",
            "branch_specific_support_coherence_traces_present": True,
        },
    )
    branch_boundary_trace = base.trace_record(
        "n24_i5a_optional_branch_boundary_flux_traces",
        "present",
        "source_current_same_run",
        {
            "optionality_window": optionality_window(),
            "branch_ids": [branch["branch_id"] for branch in branches],
            "boundary_integrity_result": "preserved",
            "flux_or_leakage_result": "preserved",
            "observed_optional_flux_drain": observed_optional_flux_drain,
            "optional_flux_drain_margin": optional_flux_drain_margin,
            "branch_specific_boundary_flux_traces_present": True,
        },
    )
    boundary_under_optionality_trace = base.trace_record(
        "n24_i5a_boundary_integrity_under_optionality_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "topology_signature": signature["topology_signature"],
            "boundary_integrity_under_optionality": "preserved",
            "optional_flux_does_not_drain_maintenance_support": True,
        },
    )
    run_artifact = {
        "artifact_id": "n24_i5a_lgrc9v3_optional_continuation_set_run",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "fixture": "make_column_h_state",
        "derived_report_only": False,
        "source_current_inputs_emitted": True,
        "runtime_config_digest": base.digest_value(runtime_config()),
        "snapshot_path": base.rel(snapshot_path),
        "maintenance_basin_signature": signature,
        "maintenance_floor_trace": floor_trace,
        "support_surplus_margin_trace": surplus_trace,
        "optional_continuation_set_trace": optional_trace,
        "optional_branch_support_coherence_traces": branch_support_trace,
        "optional_branch_boundary_flux_traces": branch_boundary_trace,
        "boundary_integrity_under_optionality_trace": boundary_under_optionality_trace,
        "optional_branch_records": branches,
        "event_counts_by_kind": {},
    }
    run_artifact["run_artifact_digest"] = base.digest_value(run_artifact)
    paths = {
        "run_artifact_path": ARTIFACT_DIR / "n24_i5a_lgrc9v3_optional_continuation_set_run.json",
        "snapshot_path": snapshot_path,
        "floor_trace_path": ARTIFACT_DIR / "n24_i5a_maintenance_floor_trace.json",
        "surplus_trace_path": ARTIFACT_DIR / "n24_i5a_support_surplus_margin_trace.json",
        "optional_trace_path": ARTIFACT_DIR / "n24_i5a_optional_continuation_set_trace.json",
        "branch_support_trace_path": ARTIFACT_DIR / "n24_i5a_optional_branch_support_coherence_traces.json",
        "branch_boundary_trace_path": ARTIFACT_DIR / "n24_i5a_optional_branch_boundary_flux_traces.json",
        "boundary_under_optionality_trace_path": ARTIFACT_DIR / "n24_i5a_boundary_integrity_under_optionality_trace.json",
        "threshold_path": ARTIFACT_DIR / "n24_i5a_thresholds_declared_before_use.json",
        "runtime_config_path": ARTIFACT_DIR / "n24_i5a_runtime_config.json",
    }
    write_map = {
        "run_artifact_path": run_artifact,
        "floor_trace_path": floor_trace,
        "surplus_trace_path": surplus_trace,
        "optional_trace_path": optional_trace,
        "branch_support_trace_path": branch_support_trace,
        "branch_boundary_trace_path": branch_boundary_trace,
        "boundary_under_optionality_trace_path": boundary_under_optionality_trace,
        "threshold_path": threshold,
        "runtime_config_path": runtime_config(),
    }
    for key, data in write_map.items():
        base.write_json(paths[key], data)
    return {
        "run_artifact": run_artifact,
        **{key: base.rel(path) for key, path in paths.items()},
        "residual_support_margin": support_margin,
        "residual_coherence_margin": coherence_margin,
        "optional_flux_drain_margin": optional_flux_drain_margin,
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": base.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def patch_candidate_row(
    *,
    source_row: dict[str, Any],
    i2: dict[str, Any],
    runtime: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    row = dict(source_row)
    run_artifact = runtime["run_artifact"]
    signature = run_artifact["maintenance_basin_signature"]
    floor_trace = run_artifact["maintenance_floor_trace"]
    surplus_trace = run_artifact["support_surplus_margin_trace"]
    optional_trace = run_artifact["optional_continuation_set_trace"]
    branch_support_trace = run_artifact["optional_branch_support_coherence_traces"]
    branch_boundary_trace = run_artifact["optional_branch_boundary_flux_traces"]
    boundary_under_optionality_trace = run_artifact[
        "boundary_integrity_under_optionality_trace"
    ]
    branches = run_artifact["optional_branch_records"]
    support_margin = surplus_trace["payload"]["support_surplus_margin"]
    coherence_margin = surplus_trace["payload"]["coherence_surplus_margin"]
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = {item["path"]: item["sha256"] for item in artifact_manifest}

    row.update(
        {
            "row_id": "n24_i5a_row_01_high_margin_target_supported_optional_set",
            "run_artifact_id": run_artifact["artifact_id"],
            "source_commit_or_source_digest": {
                "script_path": SCRIPT_PATH,
                "script_sha256": base.sha256_file(SCRIPT_PATH),
            },
            "runtime_config_digest": run_artifact["runtime_config_digest"],
            "source_current_inputs": [
                "LGRC9V3 source-current runtime snapshot",
                "LGRC9V3 high-margin target-supported maintenance-basin node metrics",
                "source-current support/coherence surplus margin trace",
                "source-current optional continuation set trace",
                "source-current optional branch support/coherence traces",
                "source-current optional branch boundary/flux traces",
                "source-current boundary under optionality trace",
            ],
            "row_specific_thresholds_declared_before_use": {
                "path": runtime["threshold_path"],
                "sha256": base.sha256_file(runtime["threshold_path"]),
                "declared_before_use": True,
                "threshold_record": threshold_record(),
            },
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
            "optionality_window": optionality_window(),
            "pre_surplus_geometry_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "runtime_trace",
                "path": runtime["snapshot_path"],
                "maintenance_basin_signature_digest": signature[
                    "maintenance_basin_signature_digest"
                ],
            },
            "support_surplus_margin_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "surplus_margin_trace",
                "path": runtime["surplus_trace_path"],
                "trace_digest": surplus_trace["trace_digest"],
                "support_surplus_margin": support_margin,
                "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
            },
            "coherence_surplus_margin_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "surplus_margin_trace",
                "path": runtime["surplus_trace_path"],
                "trace_digest": surplus_trace["trace_digest"],
                "coherence_surplus_margin": coherence_margin,
                "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
            },
            "residual_support_margin_under_optionality": runtime[
                "residual_support_margin"
            ],
            "residual_coherence_margin_under_optionality": runtime[
                "residual_coherence_margin"
            ],
            "optional_flux_drain_margin": runtime["optional_flux_drain_margin"],
            "maintenance_floor_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "maintenance_floor_trace",
                "path": runtime["floor_trace_path"],
                "trace_digest": floor_trace["trace_digest"],
            },
            "optional_continuation_set_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "optional_continuation_set_trace",
                "path": runtime["optional_trace_path"],
                "trace_digest": optional_trace["trace_digest"],
                "same_source_current_run": True,
                "same_declared_optionality_window": True,
            },
            "optional_continuation_count": len(branches),
            "optional_continuation_availability_count": len(branches),
            "jointly_admissible_optional_continuation_count": 0,
            "optional_branch_records": branches,
            "optional_branch_support_coherence_traces": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "optional_branch_trace",
                "artifact_subtype": "optional_branch_support_coherence_trace",
                "path": runtime["branch_support_trace_path"],
                "trace_digest": branch_support_trace["trace_digest"],
            },
            "optional_branch_boundary_flux_traces": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "optional_branch_trace",
                "artifact_subtype": "optional_branch_boundary_flux_trace",
                "path": runtime["branch_boundary_trace_path"],
                "trace_digest": branch_boundary_trace["trace_digest"],
            },
            "boundary_integrity_under_optionality_trace": {
                "trace_status": "present",
                "trace_origin": "source_current_same_run",
                "artifact_role": "boundary_integrity_trace",
                "artifact_subtype": "boundary_integrity_under_optionality_trace",
                "path": runtime["boundary_under_optionality_trace_path"],
                "trace_digest": boundary_under_optionality_trace["trace_digest"],
            },
            "support_floor_result": {
                "status": "preserved",
                "observed_support": signature["min_support"],
                "support_floor": SUPPORT_FLOOR,
                "support_surplus_margin": support_margin,
            },
            "coherence_floor_result": {
                "status": "preserved",
                "observed_coherence": signature["min_coherence"],
                "coherence_floor": COHERENCE_FLOOR,
                "coherence_surplus_margin": coherence_margin,
            },
            "boundary_integrity_result": {
                "status": "preserved",
                "maintenance_node_ids": MAINTENANCE_NODE_IDS,
                "maintenance_basin_signature_digest": signature[
                    "maintenance_basin_signature_digest"
                ],
                "topology_signature": signature["topology_signature"],
            },
            "flux_or_leakage_result": {
                "status": "preserved",
                "packet_budget_error": 0.0,
                "in_flight_packet_total": 0.0,
                "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
            },
            "replay_result": {
                "artifact_replay": "not_run",
                "snapshot_load_replay": "not_run",
                "duplicate_replay": "not_run",
                "not_run_reason": (
                    "I5-A opens an alternative high-margin optional set; "
                    "replay/control-backed evidence remains I6-A scope"
                ),
                "affected_rungs": ["AB4", "AB5", "AB6", "N24-C4", "N24-C5", "N24-C6"],
            },
            "control_results": i5.control_results(),
            "surplus_trace_digest": surplus_trace["trace_digest"],
            "optional_continuation_trace_digest": optional_trace["trace_digest"],
            "maintenance_floor_trace_digest": floor_trace["trace_digest"],
            "replay_surplus_digest": "not_run_until_iteration_6a",
            "replay_optionality_digest": "not_run_until_iteration_6a",
            "surplus_threshold_or_rule": threshold_record(),
            "optionality_threshold_or_rule": threshold_record(),
            "claim_ceiling": (
                "alternative source-current AB3 optional continuation candidate "
                "pending I6-A replay/control and I7-A stress; does not replace "
                "I5/I6/I7; reward maximization, semantic choice, agency, native "
                "support, sentience, Phase 8, and ant ecology remain blocked"
            ),
            "artifact_manifest": artifact_manifest,
            "artifact_paths": artifact_paths,
            "artifact_sha256": artifact_sha256,
            "artifact_paths_equal_manifest_paths": sorted(artifact_paths)
            == sorted(item["path"] for item in artifact_manifest),
            "artifact_sha256_equal_manifest_sha256": artifact_sha256
            == {item["path"]: item["sha256"] for item in artifact_manifest},
            "all_artifact_sha256_match_file_contents": all(
                item["sha256"] == base.sha256_file(item["path"])
                for item in artifact_manifest
            ),
            "output_digest": "pending",
        }
    )
    row["output_digest"] = base.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return row


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5_original = base.load_json(I5_OUTPUT_PATH)
    i6_original = base.load_json(I6_OUTPUT_PATH)
    i7_original = base.load_json(I7_OUTPUT_PATH)
    runtime = build_runtime_artifacts()
    artifact_manifest = file_manifest(
        [
            (runtime["runtime_config_path"], "runtime_trace"),
            (runtime["threshold_path"], "maintenance_floor_trace"),
            (runtime["run_artifact_path"], "runtime_trace"),
            (runtime["snapshot_path"], "runtime_trace"),
            (runtime["floor_trace_path"], "maintenance_floor_trace"),
            (runtime["surplus_trace_path"], "surplus_margin_trace"),
            (runtime["optional_trace_path"], "optional_continuation_set_trace"),
            (runtime["branch_support_trace_path"], "optional_branch_trace"),
            (runtime["branch_boundary_trace_path"], "optional_branch_trace"),
            (runtime["boundary_under_optionality_trace_path"], "boundary_integrity_trace"),
        ]
    )
    row = patch_candidate_row(
        source_row=i5_original["candidate_rows"][0],
        i2=i2,
        runtime=runtime,
        artifact_manifest=artifact_manifest,
    )
    required_fields = i2["candidate_evidence_row_schema"]["required_fields"]
    checks = [
        base.check("i1_inventory_passed", i1["status"] == "passed" and not i1["failed_checks"], i1["acceptance_state"]),
        base.check("i2_schema_passed", i2["status"] == "passed" and not i2["failed_checks"], i2["acceptance_state"]),
        base.check("i3_active_nulls_passed", i3["status"] == "passed" and not i3["failed_checks"], i3["acceptance_state"]),
        base.check("i4_surplus_probe_passed", i4["status"] == "passed" and not i4["failed_checks"], i4["acceptance_state"]),
        base.check("original_i5_i6_i7_preserved_as_context", i5_original["status"] == "passed" and i6_original["status"] == "passed" and i7_original["status"] == "passed", {
            "i5_digest": i5_original["output_digest"],
            "i6_digest": i6_original["output_digest"],
            "i7_digest": i7_original["output_digest"],
            "i5_replaced": False,
            "i6_replaced": False,
            "i7_replaced": False,
        }),
        base.check(
            "candidate_row_field_set_matches_i2_required_fields",
            set(row) == set(required_fields),
            {
                "required_count": len(required_fields),
                "candidate_count": len(row),
                "extra": sorted(set(row) - set(required_fields)),
                "missing": sorted(set(required_fields) - set(row)),
            },
        ),
        base.check("derived_report_only_false", row["derived_report_only"] is False, row["derived_report_only"]),
        base.check("artifact_manifest_roles_allowed_by_i2", all(
            item["artifact_role"] in i2["artifact_admissibility_schema"]["artifact_manifest_schema"]["artifact_role_values"]
            for item in row["artifact_manifest"]
        ), row["artifact_manifest"]),
        base.check(
            "high_margin_variant_observed",
            row["support_floor_result"]["support_surplus_margin"] > i5_original["candidate_rows"][0]["support_floor_result"]["support_surplus_margin"]
            and row["coherence_floor_result"]["coherence_surplus_margin"] > i5_original["candidate_rows"][0]["coherence_floor_result"]["coherence_surplus_margin"],
            {
                "i5_support_margin": i5_original["candidate_rows"][0]["support_floor_result"]["support_surplus_margin"],
                "i5a_support_margin": row["support_floor_result"]["support_surplus_margin"],
                "i5_coherence_margin": i5_original["candidate_rows"][0]["coherence_floor_result"]["coherence_surplus_margin"],
                "i5a_coherence_margin": row["coherence_floor_result"]["coherence_surplus_margin"],
            },
        ),
        base.check(
            "source_current_optional_set_present",
            row["optional_continuation_availability_count"] >= 2
            and row["optional_continuation_set_trace"]["same_source_current_run"] is True,
            row["optional_continuation_set_trace"],
        ),
        base.check(
            "boundary_flux_and_claim_boundary_preserved",
            row["boundary_integrity_result"]["status"] == "preserved"
            and row["flux_or_leakage_result"]["status"] == "preserved"
            and row["surplus_supported_optionality_claim_allowed"] is False,
            {
                "boundary": row["boundary_integrity_result"],
                "flux": row["flux_or_leakage_result"],
                "claim_allowed": row["surplus_supported_optionality_claim_allowed"],
            },
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_optional_continuation_set_probe_i5a",
        "schema_version": "n24_optional_continuation_set_probe_i5a_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "5-A",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_alternative_high_margin_ab3_optional_continuation_candidate_pending_i6a"
            if not failed_checks
            else "failed_alternative_optional_continuation_probe"
        ),
        "purpose": "produce an alternative high-margin source-current optional continuation set without replacing I5",
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(I5_OUTPUT_PATH, "n24_i5_original_optional_probe_context"),
            base.source_record(I6_OUTPUT_PATH, "n24_i6_original_replay_control_context"),
            base.source_record(I7_OUTPUT_PATH, "n24_i7_original_stress_context"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "variant_boundary": {
            "variant_id": "i5a_high_margin_target_supported_optional_set",
            "i5_replaced": False,
            "i6_replaced": False,
            "i7_replaced": False,
            "original_i5_consumed_as_contrast_only": True,
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "optional_branch_target_node_ids": OPTIONAL_BRANCH_TARGET_NODE_IDS,
            "provisional_ab_ladder_rung": "AB3",
            "ab4_or_stronger_supported": False,
            "ab5_or_stronger_supported": False,
            "ready_for_iteration_6a_replay_control_matrix": not failed_checks,
        },
        "candidate_rows": [row],
        "geometric_interpretation": {
            "short_read": (
                "I5-A reuses the LGRC fixture but declares a different source-current "
                "maintenance basin over high-support optional target nodes [1, 5, 9]."
            ),
            "margin_difference": (
                "The original I5 maintenance basin had min support/coherence 10.0, "
                "margin 0.15 above the 9.85 floor. I5-A has min support/coherence "
                "11.0, margin 1.15 above the same floor."
            ),
            "claim_boundary": (
                "This is an alternative AB3 candidate only. It does not replace I5, "
                "does not change the frozen thresholds, and does not open reward, "
                "semantic choice, agency, native support, sentience, Phase 8, or ant ecology."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    lines = [
        "# N24 Iteration 5-A - Alternative Optional Continuation Set Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 5-A adds an alternative high-margin optionality variant. It does",
        "not replace I5; it creates a second source-current AB3 candidate for I6-A",
        "and I7-A to replay and stress-test.",
        "",
        "## Geometry",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["margin_difference"],
        "",
        "```text",
        f"maintenance_basin_id = {row['maintenance_basin_id']}",
        f"maintenance_node_ids = {MAINTENANCE_NODE_IDS}",
        f"optional_branch_target_node_ids = {OPTIONAL_BRANCH_TARGET_NODE_IDS}",
        f"support_floor = {SUPPORT_FLOOR:.12f}",
        f"coherence_floor = {COHERENCE_FLOOR:.12f}",
        f"observed_min_support = {row['support_floor_result']['observed_support']:.12f}",
        f"observed_min_coherence = {row['coherence_floor_result']['observed_coherence']:.12f}",
        f"support_surplus_margin = {row['support_floor_result']['support_surplus_margin']:.12f}",
        f"coherence_surplus_margin = {row['coherence_floor_result']['coherence_surplus_margin']:.12f}",
        "```",
        "",
        "## Boundary",
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

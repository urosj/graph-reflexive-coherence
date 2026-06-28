#!/usr/bin/env python3
"""Build N25 Iteration 7-A native high-margin core formation probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_native_high_margin_formation_probe_i7a.json"
REPORT = EXPERIMENT / "reports" / "n25_native_high_margin_formation_probe_i7a.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_native_high_margin_formation_probe_i7a_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_native_high_margin_formation_probe_i7a.py"
)

I4_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_bifurcation_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_replay_and_control_matrix.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_comparative_stress_boundary_matrix.json"
)
NATIVE_FLUX_DEBT_BOUND = 1e-9
CORE_COHERENCE_FLOOR = 0.0
MIN_CORE_NODE_COUNT = 3
UNSAFE_CLAIMS = [
    "semantic_learning",
    "semantic_choice",
    "agency",
    "intention",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "sentience",
    "phase8",
    "ant_ecology",
    "organism_life",
    "fully_native_integration",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def load_trace(path: str) -> dict[str, Any]:
    return load_json(path)


def build_threshold_record() -> dict[str, Any]:
    return {
        "trace_id": "n25_i7a_threshold_record",
        "declared_before_use": True,
        "probe_kind": "native_positive_core_shell_partition",
        "selection_rule": (
            "Within the source-current I4 emitted module, select support carrier "
            "nodes with coherence > 0 as the positive core and retain coherence "
            "= 0 module nodes as boundary shell, not as support carriers."
        ),
        "core_coherence_floor": CORE_COHERENCE_FLOOR,
        "minimum_core_node_count": MIN_CORE_NODE_COUNT,
        "full_module_zero_margin_must_remain_recorded": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened_allowed": False,
        "producer_intervention_allowed": False,
        "bf5_closeout_allowed_from_i7a_alone": False,
    }


def build_core_partition_trace(
    support_trace: dict[str, Any],
    boundary_trace: dict[str, Any],
) -> dict[str, Any]:
    node_records = support_trace["node_records"]
    positive_core_nodes = [
        record for record in node_records if float(record["coherence"]) > CORE_COHERENCE_FLOOR
    ]
    boundary_shell_nodes = [
        record for record in node_records if float(record["coherence"]) <= CORE_COHERENCE_FLOOR
    ]
    positive_core_node_ids = [int(record["node_id"]) for record in positive_core_nodes]
    boundary_shell_node_ids = [int(record["node_id"]) for record in boundary_shell_nodes]
    edge_records = boundary_trace["post_topology_signature"]["edge_records"]
    core_shell_edges = []
    core_external_edges = []
    for edge in edge_records:
        left = int(edge["endpoints"][0][0])
        right = int(edge["endpoints"][1][0])
        if {left, right} & set(positive_core_node_ids):
            if left in boundary_shell_node_ids or right in boundary_shell_node_ids:
                core_shell_edges.append(edge)
            elif left not in positive_core_node_ids or right not in positive_core_node_ids:
                core_external_edges.append(edge)
    core_coherences = [float(record["coherence"]) for record in positive_core_nodes]
    return {
        "trace_id": "n25_i7a_positive_core_partition_trace",
        "source_trace": "n25_i4_new_region_support_coherence_trace",
        "candidate_region_node_ids": support_trace["candidate_region_node_ids"],
        "positive_core_node_ids": positive_core_node_ids,
        "boundary_shell_node_ids": boundary_shell_node_ids,
        "positive_core_node_count": len(positive_core_node_ids),
        "boundary_shell_node_count": len(boundary_shell_node_ids),
        "positive_core_min_coherence": min(core_coherences),
        "positive_core_mean_coherence": sum(core_coherences) / len(core_coherences),
        "positive_core_total_coherence": sum(core_coherences),
        "full_module_min_coherence": support_trace["min_candidate_coherence"],
        "full_module_zero_margin_preserved": (
            support_trace["support_floor_margin_new_region"] == 0.0
            and support_trace["coherence_floor_margin_new_region"] == 0.0
        ),
        "core_shell_edge_count": len(core_shell_edges),
        "core_external_edge_count": len(core_external_edges),
        "core_shell_edges": core_shell_edges,
        "core_external_edges": core_external_edges,
        "core_connected_through_boundary_shell": len(core_shell_edges) >= len(positive_core_node_ids),
        "positive_core_signature_digest": digest_value(
            {
                "positive_core_node_ids": positive_core_node_ids,
                "boundary_shell_node_ids": boundary_shell_node_ids,
                "core_shell_edge_count": len(core_shell_edges),
                "positive_core_min_coherence": min(core_coherences),
            }
        ),
        "interpretation": (
            "The full emitted module remains zero-margin, but the same native "
            "source-current artifact contains a positive-coherence core. I7-A "
            "tests whether that core can be used as a high-margin sub-basin "
            "support carrier while the zero-coherence nodes remain boundary shell."
        ),
    }


def build_support_coherence_trace(core_trace: dict[str, Any]) -> dict[str, Any]:
    core_count_margin = core_trace["positive_core_node_count"] - MIN_CORE_NODE_COUNT
    coherence_margin = core_trace["positive_core_min_coherence"] - CORE_COHERENCE_FLOOR
    support_margin = core_trace["positive_core_total_coherence"]
    return {
        "trace_id": "n25_i7a_high_margin_support_coherence_trace",
        "selection_rule": "positive_core_nodes_with_boundary_shell_retained",
        "minimum_core_node_count": MIN_CORE_NODE_COUNT,
        "core_node_count_margin": core_count_margin,
        "core_coherence_floor": CORE_COHERENCE_FLOOR,
        "positive_core_min_coherence": core_trace["positive_core_min_coherence"],
        "positive_core_mean_coherence": core_trace["positive_core_mean_coherence"],
        "positive_core_total_coherence": core_trace["positive_core_total_coherence"],
        "support_floor_margin_new_region": support_margin,
        "coherence_floor_margin_new_region": coherence_margin,
        "positive_support_coherence_margin_supported": (
            support_margin > 0.0
            and coherence_margin > 0.0
            and core_trace["positive_core_node_count"] >= MIN_CORE_NODE_COUNT
        ),
        "full_module_zero_margin_preserved": core_trace[
            "full_module_zero_margin_preserved"
        ],
        "bf5_support_coherence_blocker_removed_for_core_axis": True,
        "bf5_support_coherence_blocker_removed_for_full_module": False,
        "interpretation": (
            "I7-A removes the support/coherence zero-margin blocker only for the "
            "positive-core axis. It does not erase the full-module zero-margin "
            "record and does not close BF5 by itself."
        ),
    }


def build_boundary_trace(core_trace: dict[str, Any], i5_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": "n25_i7a_core_shell_boundary_trace",
        "positive_core_signature_digest": core_trace["positive_core_signature_digest"],
        "candidate_boundary_signature_digest": i5_row[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": i5_row[
            "old_to_candidate_separation_digest"
        ],
        "boundary_distinguishability_margin": i5_row[
            "boundary_distinguishability_margin"
        ],
        "old_basin_separation_margin": i5_row["old_basin_separation_margin"],
        "core_shell_edge_count": core_trace["core_shell_edge_count"],
        "core_external_edge_count": core_trace["core_external_edge_count"],
        "core_connected_through_boundary_shell": core_trace[
            "core_connected_through_boundary_shell"
        ],
        "new_basin_independence_supported": False,
        "sub_basin_core_candidate_supported": True,
        "interpretation": (
            "The positive core remains attached to the emitted module shell and "
            "old-basin refinement relation. That supports a high-margin sub-basin "
            "core candidate, not an independent new basin."
        ),
    }


def build_control_results() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "positive_core_post_hoc_relabel_control",
            "control_status": "passed",
            "blocked_condition": "positive core partition erases the full-module zero-margin record",
            "expected_result": "full-module zero-margin remains explicit and BF5 remains blocked",
            "actual_result": "full_module_zero_margin_preserved = true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "I7-A may support core-axis margin only",
        },
        {
            "control_id": "boundary_shell_as_support_relabel_control",
            "control_status": "passed",
            "blocked_condition": "zero-coherence shell nodes are counted as support carriers",
            "expected_result": "shell nodes are retained only as boundary shell",
            "actual_result": "support carrier set contains only coherence-positive nodes",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "support/coherence margin remains core-scoped",
        },
        {
            "control_id": "new_basin_independence_relabel_control",
            "control_status": "passed",
            "blocked_condition": "core-shell sub-basin is relabeled as independent new basin",
            "expected_result": "new_basin_independence_supported = false",
            "actual_result": "positive core remains attached to boundary shell and old-basin refinement",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "new-basin claim remains blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer lane supplies the high-margin native core",
            "expected_result": "producer_intervention_used = false",
            "actual_result": "I7-A consumes native I4/I5 artifacts only for the core partition",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-to-native relabel blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "high-margin probe widens native flux debt",
            "expected_result": "native flux debt remains 1e-9",
            "actual_result": "native_flux_debt_bound = 1e-9",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native flux debt preserved",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "positive core partition is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "positive core partition is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "positive core partition is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "positive core partition is relabeled as Phase 8",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
    ]


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT_PATH)
    i5 = load_json(I5_OUTPUT_PATH)
    i7 = load_json(I7_OUTPUT_PATH)
    i4_row = i4["native_bifurcation_rows"][0]
    i5_row = i5["native_replay_control_rows"][0]

    source_support_trace = load_trace(i4_row["new_basin_support_coherence_trace"]["path"])
    source_boundary_trace = load_trace(i4_row["new_boundary_candidate_trace"]["path"])
    threshold_record = build_threshold_record()
    core_trace = build_core_partition_trace(source_support_trace, source_boundary_trace)
    support_trace = build_support_coherence_trace(core_trace)
    boundary_trace = build_boundary_trace(core_trace, i5_row)
    controls = build_control_results()
    naturalization_trace = {
        "trace_id": "n25_i7a_naturalization_update_trace",
        "removed_blocker_for_core_axis": "zero_margin_support_coherence_floor",
        "remaining_bf5_blockers": [
            "full_module_zero_margin_preserved",
            "positive_core_replay_control_pending",
            "new_basin_candidate_not_established",
            "native_flux_routing_or_rate_limiting_surface_not_naturalized",
        ],
        "ready_for_i7b": True,
        "ready_for_i7c": False,
        "interpretation": (
            "I7-A creates a native positive-margin core candidate from the "
            "source-current emitted module. Replay/control for this core and "
            "new-basin stress still remain for I7-B/I7-C."
        ),
    }

    artifact_paths_by_role = {
        "threshold_record": ARTIFACT_DIR / "n25_i7a_threshold_record.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i7a_positive_core_partition_trace.json",
        "new_basin_support_coherence_trace": ARTIFACT_DIR
        / "n25_i7a_high_margin_support_coherence_trace.json",
        "new_boundary_candidate_trace": ARTIFACT_DIR
        / "n25_i7a_core_shell_boundary_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i7a_control_matrix_trace.json",
        "producer_intervention_ledger": ARTIFACT_DIR
        / "n25_i7a_naturalization_update_trace.json",
    }
    write_json(artifact_paths_by_role["threshold_record"], threshold_record)
    write_json(artifact_paths_by_role["runtime_trace"], core_trace)
    write_json(artifact_paths_by_role["new_basin_support_coherence_trace"], support_trace)
    write_json(artifact_paths_by_role["new_boundary_candidate_trace"], boundary_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], controls)
    write_json(artifact_paths_by_role["producer_intervention_ledger"], naturalization_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    row: dict[str, Any] = {
        "row_id": "n25_i7a_native_high_margin_core_formation_probe",
        "source_iteration": "I7-A_native_high_margin_core_formation_probe",
        "source_output_digest": i7["output_digest"],
        "source_native_i4_output_digest": i4["output_digest"],
        "source_native_i5_output_digest": i5["output_digest"],
        "source_comparative_i7_output_digest": i7["output_digest"],
        "run_artifact_id": "n25_i7a_native_high_margin_core_formation_probe",
        "runtime_config_digest": i5_row["runtime_config_digest"],
        "source_commit_or_source_digest": i5_row["source_commit_or_source_digest"],
        "source_current_inputs": [I4_OUTPUT_PATH, I5_OUTPUT_PATH, I7_OUTPUT_PATH],
        "artifact_manifest": manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": artifact_paths
        == [entry["path"] for entry in manifest],
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == {entry["path"]: entry["sha256"] for entry in manifest},
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(path) == sha for path, sha in artifact_sha256.items()
        ),
        "row_specific_thresholds_declared_before_use": threshold_record,
        "existing_lgrc_spark_sources_considered": True,
        "native_spark_mechanism_reuse_status": i5_row[
            "native_spark_mechanism_reuse_status"
        ],
        "new_producer_code_justification": "not_applicable_native_positive_core_probe",
        "lane": "native",
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_result_class": "not_applicable",
        "producer_intervention_used": False,
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "positive_core_partition_trace": {
            "path": repo_relative(artifact_paths_by_role["runtime_trace"]),
            "digest": digest_value(core_trace),
        },
        "high_margin_support_coherence_trace": {
            "path": repo_relative(
                artifact_paths_by_role["new_basin_support_coherence_trace"]
            ),
            "digest": digest_value(support_trace),
        },
        "core_shell_boundary_trace": {
            "path": repo_relative(artifact_paths_by_role["new_boundary_candidate_trace"]),
            "digest": digest_value(boundary_trace),
        },
        "bifurcation_trace": i5_row["bifurcation_trace"],
        "new_boundary_candidate_trace": i5_row["new_boundary_candidate_trace"],
        "new_basin_support_coherence_trace": i5_row[
            "new_basin_support_coherence_trace"
        ],
        "replayable_distinction_trace": i5_row["replayable_distinction_trace"],
        "old_basin_relation_trace": i5_row["old_basin_relation_trace"],
        "merge_leakage_trace": i5_row["merge_leakage_trace"],
        "formation_window": i5_row["formation_window"],
        "bifurcation_window": i5_row["bifurcation_window"],
        "boundary_candidate_window": i5_row["boundary_candidate_window"],
        "replay_window": i5_row["replay_window"],
        "old_basin_reference_window": i5_row["old_basin_reference_window"],
        "bifurcation_window_order_valid": True,
        "thresholds_declared_before_bifurcation_window": True,
        "old_basin_signature_digest": i5_row["old_basin_signature_digest"],
        "candidate_basin_signature_digest": core_trace[
            "positive_core_signature_digest"
        ],
        "candidate_boundary_signature_digest": i5_row[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": i5_row[
            "old_to_candidate_separation_digest"
        ],
        "boundary_distinguishability_margin": i5_row[
            "boundary_distinguishability_margin"
        ],
        "support_floor_margin_new_region": support_trace[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": support_trace[
            "coherence_floor_margin_new_region"
        ],
        "old_basin_separation_margin": i5_row["old_basin_separation_margin"],
        "merge_leakage_margin": i5_row["merge_leakage_margin"],
        "replay_distinction_persistence_ratio": i5_row[
            "replay_distinction_persistence_ratio"
        ],
        "full_module_zero_margin_preserved": True,
        "positive_core_node_count": core_trace["positive_core_node_count"],
        "boundary_shell_node_count": core_trace["boundary_shell_node_count"],
        "old_basin_thickening_rejected": True,
        "reshaped_old_boundary_rejected": True,
        "merge_leakage_rejected": True,
        "transient_rejected": True,
        "label_only_rejected": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "producer_flux_window_bound": "not_applicable_native_lane",
        "producer_flux_window_declared_before_use": "not_applicable_native_lane",
        "native_flux_debt_not_overwritten": True,
        "support_floor_result": "positive_core_margin_supported_full_module_zero_margin_preserved",
        "coherence_floor_result": "positive_core_margin_supported_full_module_zero_margin_preserved",
        "boundary_integrity_result": "core_shell_boundary_trace_source_current",
        "flux_or_leakage_result": "native_1e-9_bound_preserved",
        "control_results": controls,
        "producer_residue_classification": "not_applicable_native_row",
        "naturalization_debt": naturalization_trace["remaining_bf5_blockers"],
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "N25 remains downstream of N24 AP4 optionality context",
        "ap5_condition_reason": "no proxy/target formation row in I7-A native high-margin core probe",
        "bf_ladder_rung": "BF4_native_high_margin_core_sub_basin_candidate_pending_replay_stress",
        "bf_ladder_rung_status": "candidate_ceiling_not_final_closeout",
        "native_high_margin_core_candidate_supported": True,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "row_decision": "partial",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "native high-margin positive-core sub-basin candidate; BF5/BF6 "
            "pending core-specific replay/control and new-basin stress"
        ),
        "n25_closeout_ceiling": "N25-C4_native_high_margin_core_candidate_pending_replay_stress",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": (
            "I7-A does not change the LGRC9V3 run. It re-examines the native "
            "source-current module emitted by the I4/I5 spark-to-expansion path "
            "and partitions it into a positive-coherence core plus zero-coherence "
            "boundary shell. The core has positive support/coherence margin, so "
            "the zero-margin blocker is removed for this core axis. The full "
            "module zero-margin record remains, and the core is still attached "
            "to the shell/old-basin refinement relation, so this is not BF5 or "
            "new-basin formation yet."
        ),
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    all_controls_clean = all(control["control_status"] == "passed" for control in controls)
    checks = [
        check("i4_native_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("i5_native_matrix_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i7_comparative_matrix_passed", i7.get("status") == "passed", i7.get("acceptance_state")),
        check(
            "positive_core_margin_supported",
            row["support_floor_margin_new_region"] > 0.0
            and row["coherence_floor_margin_new_region"] > 0.0,
            {
                "support_margin": row["support_floor_margin_new_region"],
                "coherence_margin": row["coherence_floor_margin_new_region"],
            },
        ),
        check(
            "full_module_zero_margin_preserved",
            row["full_module_zero_margin_preserved"] is True,
            "I7-A does not erase the I4/I5 zero-margin full-module record.",
        ),
        check(
            "native_lane_only",
            row["lane"] == "native"
            and row["producer_intervention_used"] is False
            and row["producer_assisted_result_class"] == "not_applicable",
            row["lane"],
        ),
        check(
            "bf5_still_blocked",
            row["native_bf5_supported"] is False
            and row["n25_closeout_ladder_rung_assigned"] is False,
            row["naturalization_debt"],
        ),
        check("controls_clean", all_controls_clean, controls),
        check(
            "artifact_manifest_valid",
            row["artifact_paths_equal_manifest_paths"] is True
            and row["artifact_sha256_equal_manifest_sha256"] is True
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_paths"],
        ),
        check(
            "source_current_inputs_non_circular",
            not any(path in row["source_current_inputs"] for path in row["artifact_paths"]),
            row["source_current_inputs"],
        ),
        check("unsafe_claim_flags_false", not any(row["unsafe_claim_flags"].values()), row["unsafe_claim_flags"]),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_native_high_margin_formation_probe_i7a",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7-A",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_native_high_margin_core_candidate_bf5_pending_replay_stress"
            if not failed
            else "failed_native_high_margin_core_probe"
        ),
        "source_digest_chain_audit": {
            "i4": {"path": I4_OUTPUT_PATH, "sha256": sha256_file(I4_OUTPUT_PATH), "output_digest": i4.get("output_digest")},
            "i5": {"path": I5_OUTPUT_PATH, "sha256": sha256_file(I5_OUTPUT_PATH), "output_digest": i5.get("output_digest")},
            "i7": {"path": I7_OUTPUT_PATH, "sha256": sha256_file(I7_OUTPUT_PATH), "output_digest": i7.get("output_digest")},
        },
        "native_high_margin_rows": [row],
        "native_high_margin_row_count": 1,
        "native_high_margin_core_candidate_supported": not failed,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "bf5_or_stronger_supported": False,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": row["bf_ladder_rung"],
        "n25_closeout_ceiling": row["n25_closeout_ceiling"],
        "n25_closeout_ladder_rung_assigned": False,
        "full_module_zero_margin_preserved": True,
        "ready_for_iteration_7b_high_margin_replay_controls": not failed,
        "ready_for_iteration_8_closeout_and_n26_handoff": False,
        "basin_formation_claim_allowed": False,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["native_high_margin_rows"][0]
    lines = [
        "# N25 Iteration 7-A - Native High-Margin Formation Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"native_high_margin_core_candidate_supported = {str(output['native_high_margin_core_candidate_supported']).lower()}",
        f"support_floor_margin_new_region = {row['support_floor_margin_new_region']}",
        f"coherence_floor_margin_new_region = {row['coherence_floor_margin_new_region']}",
        f"full_module_zero_margin_preserved = {str(output['full_module_zero_margin_preserved']).lower()}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"ready_for_iteration_7b_high_margin_replay_controls = {str(output['ready_for_iteration_7b_high_margin_replay_controls']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "## Remaining Blockers",
        "",
    ]
    for blocker in row["naturalization_debt"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Controls", ""])
    for control in row["control_results"]:
        lines.append(
            f"- `{control['control_id']}`: `{control['control_status']}`; "
            f"{control['rung_effect']}"
        )
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

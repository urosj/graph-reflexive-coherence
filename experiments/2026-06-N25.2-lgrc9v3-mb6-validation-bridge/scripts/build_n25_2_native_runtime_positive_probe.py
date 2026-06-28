#!/usr/bin/env python3
"""Build N25.2 Iteration 4 native LGRC9V3 runtime positive probe."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I3_OUTPUT = EXPERIMENT / "outputs" / "n25_2_phase8_mb5_evidence_chain_audit.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
REPORT = EXPERIMENT / "reports" / "n25_2_native_runtime_positive_probe.md"
EXAMPLE_FIXTURE = ROOT / "examples" / "lgrc9v3" / "multi_basin_formation_bundle.py"
RUNTIME_CONTRACT = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_contract.py"
RUNTIME_CODE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
RUNTIME_STATE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime_state.py"
TELEMETRY_CODE = ROOT / "src" / "pygrc" / "telemetry" / "lgrc9v3_contract.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_native_runtime_positive_probe.py"
)

UNSAFE_CLAIMS = [
    "semantic_learning_claim_allowed",
    "semantic_choice_claim_allowed",
    "agency_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "sentience_claim_allowed",
    "organism_life_claim_allowed",
    "ant_ecology_claim_allowed",
    "phase8_completion_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
]

RUNTIME_DIGEST_PATHS = [
    RUNTIME_CONTRACT,
    RUNTIME_CODE,
    RUNTIME_STATE,
    TELEMETRY_CODE,
    EXAMPLE_FIXTURE,
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def import_example_fixture() -> Any:
    spec = importlib.util.spec_from_file_location(
        "n25_2_i4_multi_basin_fixture",
        EXAMPLE_FIXTURE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load LGRC9V3 multi-basin fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    if hasattr(payload, "kind") and hasattr(payload, "payload"):
        return {
            "kind": str(payload.kind),
            "step_index": int(payload.step_index),
            "payload": jsonable(payload.payload),
            "source_family": str(payload.source_family),
        }
    return payload


def git_diff_paths(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *paths],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def implementation_digest_bundle(runtime_config: dict[str, Any]) -> dict[str, Any]:
    file_digests = {
        repo_path(path): sha256_file(path) for path in RUNTIME_DIGEST_PATHS
    }
    return {
        "runtime_config_digest": digest_value(jsonable(runtime_config)),
        "runtime_source_digest": digest_value(file_digests),
        "source_file_sha256": file_digests,
        "lgrc9v3_runtime_file_sha256": file_digests[repo_path(RUNTIME_CODE)],
        "lgrc9v3_runtime_state_file_sha256": file_digests[repo_path(RUNTIME_STATE)],
        "lgrc9v3_contract_file_sha256": file_digests[repo_path(RUNTIME_CONTRACT)],
        "telemetry_contract_file_sha256": file_digests[repo_path(TELEMETRY_CODE)],
    }


def run_native_runtime_probe() -> dict[str, Any]:
    fixture = import_example_fixture()
    model = fixture.LGRC9V3.from_state(
        fixture.three_node_state(),
        fixture.multi_basin_params(),
    )
    runtime_config = model.get_params().raw_config
    initial_snapshot_digest = digest_value(model.snapshot())
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_result = model.step()
    surface = model.get_state().causal_pulse_substrate_surface_log[-1]
    candidate_result = model.emit_native_route_candidate_set(
        arbitration_window_id="window:n25-2-i4-reference",
        source_surface_digest=str(surface.surface_digest),
        unresolved_tie_policy=(
            fixture.LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED
        ),
        candidate_routes=(
            fixture.native_route_candidate_spec(
                candidate_route_id="candidate:low",
                selected_sink_id=2,
                losing_sink_ids=(0,),
                score=0.25,
            ),
            fixture.native_route_candidate_spec(
                candidate_route_id="candidate:high",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=0.75,
            ),
        ),
    )
    candidate_set = candidate_result["candidate_set_record"]
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    arbitration = arbitration_result["route_arbitration_record"]
    commit_result = model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(arbitration.native_route_arbitration_digest),
    )
    state = model.get_state()
    final_snapshot = model.snapshot()
    flow_records = [record.to_artifact() for record in state.post_refinement_flow_window_log]
    child_records = [record.to_artifact() for record in state.child_basin_state_log]
    replay_records = [
        record.to_artifact() for record in state.multi_basin_replay_validation_log
    ]
    control_records = [
        record.to_artifact() for record in state.merge_leakage_control_matrix_log
    ]
    topology_events = [
        {
            "kind": event.kind,
            "step_index": int(event.step_index),
            "payload": jsonable(event.payload),
            "source_family": str(event.source_family),
        }
        for event in state.topology_event_log
    ]
    event_counts = dict(Counter(event.kind for event in state.topology_event_log))
    return {
        "runtime_config": runtime_config,
        "params_hash": model.get_params().params_hash,
        "initial_snapshot_digest": initial_snapshot_digest,
        "final_snapshot_digest": digest_value(final_snapshot),
        "runtime_snapshot_artifact": final_snapshot,
        "step_result": {
            "step_index": int(step_result.step_index),
            "time": float(step_result.time),
            "event_count": len(step_result.events),
            "events": [jsonable(event) for event in step_result.events],
        },
        "candidate_result": {
            "emitted": bool(candidate_result["emitted"]),
            "reason_code": str(candidate_result["reason_code"]),
            "candidate_records": [
                record.to_artifact() for record in candidate_result["candidate_records"]
            ],
            "candidate_set_record": candidate_set.to_artifact(),
        },
        "arbitration_result": {
            "emitted": bool(arbitration_result["emitted"]),
            "reason_code": str(arbitration_result["reason_code"]),
            "route_arbitration_record": arbitration.to_artifact(),
        },
        "commit_result": {
            "committed": bool(commit_result["committed"]),
            "reason_code": str(commit_result["reason_code"]),
            "selected_topology_event_digest": str(
                commit_result["selected_topology_event_digest"]
            ),
            "selected_candidate_route_record": (
                commit_result["selected_candidate_route_record"].to_artifact()
            ),
            "flow_record_count": len(commit_result["post_refinement_flow_window_records"]),
            "child_basin_record_count": len(commit_result["child_basin_state_records"]),
            "surface_lineage_record_count": len(commit_result["surface_lineage_records"]),
            "topology_state_reabsorption_record_count": len(
                commit_result["topology_state_reabsorption_records"]
            ),
        },
        "topology_events": topology_events,
        "event_counts_by_kind": event_counts,
        "flow_window_records": flow_records,
        "child_basin_state_records": child_records,
        "replay_validation_records": replay_records,
        "merge_leakage_control_records": control_records,
        "causal_modes_after_commit": dict(sorted(state.causal_modes.items())),
    }


def child_field_summary(child_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for child in child_records:
        summaries.append(
            {
                "child_basin_id": child["child_basin_state_record_id"],
                "birth_or_detection_step": child["source_flow_window_digest"],
                "parent_or_source_basin_id": child["old_basin_relation_trace"].get(
                    "source_topology_event_digest"
                ),
                "boundary_birth_or_refinement_provenance": child[
                    "old_basin_relation_trace"
                ],
                "support_core_nodes": child["child_basin_support_floor_records"],
                "coherence_core_nodes": child["child_basin_coherence_floor_records"],
                "basin_signature_digest": child["child_basin_membership_digest"],
                "flow_window_id": child["source_flow_window_digest"],
                "merge_leakage_status": child["merge_leakage_trace"],
                "producer_native_mutation_owner": child[
                    "producer_residue_classification"
                ],
                "producer_residue_status": "not_load_bearing_for_claim",
                "source_current_status": "native_runtime_emitted",
                "trace_origin": "LGRC9V3_runtime_commit_native_route_arbitration_selection",
                "trace_digest": child["child_basin_state_digest"],
            }
        )
    return summaries


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT)
    runtime = run_native_runtime_probe()
    flow_records = runtime["flow_window_records"]
    child_records = runtime["child_basin_state_records"]
    snapshot_runtime = runtime["runtime_snapshot_artifact"]["dynamics"][
        "lgrc9v3_runtime"
    ]
    diff_paths = git_diff_paths(["src", "specs", "tests", "examples", "implementation"])
    no_mutation_proof = {
        "implementation_modification_allowed": False,
        "implementation_source_modification_observed": bool(diff_paths),
        "src_diff_observed": any(path.startswith("src/") for path in diff_paths),
        "spec_diff_observed": any(path.startswith("specs/") for path in diff_paths),
        "test_diff_observed": any(path.startswith("tests/") for path in diff_paths),
        "example_diff_observed": any(
            path.startswith("examples/") for path in diff_paths
        ),
        "implementation_diff_observed": any(
            path.startswith("implementation/") for path in diff_paths
        ),
        "observed_diff_paths": diff_paths,
        "runtime_execution_from_closed_implementation": not diff_paths,
        "defect_fix_attempted": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
    }
    implementation_digests = implementation_digest_bundle(runtime["runtime_config"])
    child_summaries = child_field_summary(child_records)
    section_digests = {
        "runtime_execution_trace_digest": digest_value(runtime["step_result"]),
        "flow_window_records_digest": digest_value(flow_records),
        "child_basin_state_records_digest": digest_value(child_records),
        "topology_refinement_provenance_digest": digest_value(
            runtime["topology_events"]
        ),
        "runtime_snapshot_digest": runtime["final_snapshot_digest"],
    }
    embedded_artifact_manifest = [
        {
            "artifact_role": "runtime_execution_trace",
            "json_pointer": "#/runtime_execution_trace",
            "digest": section_digests["runtime_execution_trace_digest"],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "flow_window_records",
            "json_pointer": "#/runtime_surface_evidence/flow_window_records",
            "digest": section_digests["flow_window_records_digest"],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "child_basin_state_records",
            "json_pointer": "#/child_basin_state_records/records",
            "digest": section_digests["child_basin_state_records_digest"],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "topology_refinement_provenance",
            "json_pointer": "#/topology_refinement_provenance/topology_events",
            "digest": section_digests["topology_refinement_provenance_digest"],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "runtime_snapshot",
            "json_pointer": "#/runtime_snapshot_artifact",
            "digest": section_digests["runtime_snapshot_digest"],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    topology_mutated_values = [
        bool(event.get("payload", {}).get("topology_mutated", False))
        for event in runtime["topology_events"]
    ]
    topology_provenance_shape = (
        "collapse_reabsorption_shaped_existing_graph"
        if topology_mutated_values and not any(topology_mutated_values)
        else "topology_mutating_or_mixed"
    )
    all_flow_claim_flags_false = all(
        not any(record["claim_flags"].values()) for record in flow_records
    )
    all_child_claim_flags_false = all(
        not any(record["claim_flags"].values()) for record in child_records
    )
    replay_pending = len(runtime["replay_validation_records"]) == 0
    controls_pending = len(runtime["merge_leakage_control_records"]) == 0
    checks = [
        check(
            "i3_mb5_chain_validated",
            i3["status"] == "passed"
            and i3["phase8_mb5_evidence_chain_status"]
            == "mb5_validated_for_runtime_probe"
            and i3["ready_for_iteration_4_native_runtime_positive_probe"] is True,
            {"i3_output_digest": i3["output_digest"]},
        ),
        check(
            "existing_runtime_executed_without_source_edits",
            no_mutation_proof["runtime_execution_from_closed_implementation"] is True,
            no_mutation_proof,
        ),
        check(
            "runtime_execution_trace_emitted",
            runtime["step_result"]["event_count"] > 0
            and runtime["candidate_result"]["emitted"] is True
            and runtime["arbitration_result"]["emitted"] is True
            and runtime["commit_result"]["committed"] is True,
            {
                "step_event_count": runtime["step_result"]["event_count"],
                "candidate_emitted": runtime["candidate_result"]["emitted"],
                "arbitration_emitted": runtime["arbitration_result"]["emitted"],
                "commit_committed": runtime["commit_result"]["committed"],
            },
        ),
        check(
            "flow_window_records_emitted",
            len(flow_records) == 1
            and flow_records[0]["native_multi_basin_enabled"] is True,
            {"flow_window_record_count": len(flow_records)},
        ),
        check(
            "child_basin_state_records_emitted",
            len(child_records) == 1
            and child_records[0]["native_multi_basin_enabled"] is True
            and child_records[0]["child_basin_core_ids"],
            {
                "child_basin_record_count": len(child_records),
                "child_basin_core_ids": child_records[0]["child_basin_core_ids"],
            },
        ),
        check(
            "snapshot_contains_runtime_emitted_records",
            snapshot_runtime["post_refinement_flow_window_log"] == flow_records
            and snapshot_runtime["child_basin_state_log"] == child_records,
            "snapshot runtime logs match source-current emitted records",
        ),
        check(
            "topology_refinement_provenance_present",
            bool(runtime["topology_events"])
            and runtime["commit_result"]["selected_topology_event_digest"],
            {
                "topology_event_count": len(runtime["topology_events"]),
                "selected_topology_event_digest": runtime["commit_result"][
                    "selected_topology_event_digest"
                ],
            },
        ),
        check(
            "collapse_reabsorption_shape_recorded_and_controls_deferred",
            topology_provenance_shape == "collapse_reabsorption_shaped_existing_graph",
            {
                "topology_provenance_shape": topology_provenance_shape,
                "required_i6_controls": [
                    "collapse_reabsorption_relabel_control",
                    "old_basin_thickening_relabel_control",
                    "transient_flow_sink_relabel_control",
                    "label_only_basin_formation_control",
                ],
            },
        ),
        check(
            "producer_native_mutation_ownership_recorded",
            child_records[0]["producer_residue_classification"]
            == "native_source_current"
            and "post_refinement_flow_window_digest"
            in child_records[0]["runtime_visible_inputs"],
            {
                "producer_residue_classification": child_records[0][
                    "producer_residue_classification"
                ],
                "runtime_visible_inputs": child_records[0]["runtime_visible_inputs"],
            },
        ),
        check(
            "implementation_digests_recorded",
            all(implementation_digests["source_file_sha256"].values())
            and implementation_digests["runtime_config_digest"],
            implementation_digests,
        ),
        check(
            "child_basin_required_fields_recorded",
            all(
                key in child_summaries[0]
                for key in [
                    "child_basin_id",
                    "birth_or_detection_step",
                    "parent_or_source_basin_id",
                    "boundary_birth_or_refinement_provenance",
                    "support_core_nodes",
                    "coherence_core_nodes",
                    "basin_signature_digest",
                    "flow_window_id",
                    "merge_leakage_status",
                    "producer_native_mutation_owner",
                    "trace_origin",
                    "trace_digest",
                ]
            ),
            child_summaries[0],
        ),
        check(
            "embedded_artifact_manifest_has_json_pointers",
            all(
                item["json_pointer"].startswith("#/")
                and item["digest_algorithm"] == "sha256_canonical_json"
                and item["digest_matches_embedded_payload"] is True
                for item in embedded_artifact_manifest
            ),
            embedded_artifact_manifest,
        ),
        check(
            "replay_controls_stress_mb6_and_n26_pending",
            replay_pending
            and controls_pending
            and runtime["causal_modes_after_commit"][
                "native_lgrc_multi_basin_formation_validated"
            ]
            is False
            and runtime["causal_modes_after_commit"][
                "native_lgrc_multi_basin_formation_supported"
            ]
            is False,
            {
                "replay_record_count": len(runtime["replay_validation_records"]),
                "control_record_count": len(runtime["merge_leakage_control_records"]),
                "validated_flag": runtime["causal_modes_after_commit"][
                    "native_lgrc_multi_basin_formation_validated"
                ],
                "supported_flag": runtime["causal_modes_after_commit"][
                    "native_lgrc_multi_basin_formation_supported"
                ],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all_flow_claim_flags_false
            and all_child_claim_flags_false
            and all(flag is False for flag in unsafe_claim_flags().values()),
            {
                "flow_claim_flags_false": all_flow_claim_flags_false,
                "child_claim_flags_false": all_child_claim_flags_false,
                "global_unsafe_claim_flags": unsafe_claim_flags(),
            },
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_native_runtime_positive_probe",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_native_runtime_positive_mb3_candidate_pending_replay_controls_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": 4,
        "command": COMMAND,
        "source_chain": {
            "i3_output_digest": i3["output_digest"],
            "i3_artifact_sha256": sha256_file(I3_OUTPUT),
            "i3_mb5_chain_status": i3["phase8_mb5_evidence_chain_status"],
        },
        "row_id": "n25_2_i4_native_runtime_positive_probe",
        "source_artifact_path": "generated_in_this_artifact",
        "source_artifact_digest": section_digests["child_basin_state_records_digest"],
        "source_role": "n25_2_native_runtime_execution_evidence",
        "source_admissibility_decision": "admissible_positive_runtime_candidate",
        "source_evidence_kind": "source_current_runtime_execution",
        "may_consume_as": [
            "MB3_source_current_child_basin_candidate",
            "I5_replay_input",
            "I6_control_input",
        ],
        "must_not_consume_as": [
            "MB5_control_backed_candidate",
            "MB6",
            "N26_unscoped_consumption",
            "native_support",
            "agency",
        ],
        "mb_ladder_input": "Phase_8_MB5_chain_validated_for_runtime_probe",
        "mb_ladder_candidate": "MB3_source_current_child_basin_candidate_emission",
        "n25_2_closeout_candidate": "pending_I5_I8",
        "runtime_execution_performed": True,
        "native_runtime_positive_probe_opened": True,
        "runtime_execution_trace": runtime["step_result"],
        "native_runtime_execution_evidence": {
            "fixture_source": repo_path(EXAMPLE_FIXTURE),
            "params_hash": runtime["params_hash"],
            "candidate_result": runtime["candidate_result"],
            "arbitration_result": runtime["arbitration_result"],
            "commit_result": runtime["commit_result"],
        },
        "runtime_surface_evidence": {
            "flow_window_record_count": len(flow_records),
            "child_basin_state_record_count": len(child_records),
            "replay_validation_record_count": len(runtime["replay_validation_records"]),
            "merge_leakage_control_record_count": len(
                runtime["merge_leakage_control_records"]
            ),
            "flow_window_records": flow_records,
        },
        "source_current_inputs": sorted(
            set(flow_records[0]["runtime_visible_inputs"])
            | set(child_records[0]["runtime_visible_inputs"])
        ),
        "child_basin_state_records": {
            "record_count": len(child_records),
            "records": child_records,
            "required_field_summary": child_summaries,
        },
        "child_basin_state_record_schema": {
            "schema_basis": "Phase_8_contract_schema_and_runtime_record",
            "candidate_name_mapping": "N25.2 child_basin_id maps to Phase 8 child_basin_state_record_id/core/membership digest",
        },
        "multi_basin_substrate_persistence": {
            "status": "pending_iteration_5_replay",
            "supporting_i4_evidence": "source_current_child_basin_state_record_emitted",
        },
        "topology_refinement_provenance": {
            "topology_provenance_shape": topology_provenance_shape,
            "topology_events": runtime["topology_events"],
            "event_counts_by_kind": runtime["event_counts_by_kind"],
            "selected_topology_event_digest": runtime["commit_result"][
                "selected_topology_event_digest"
            ],
            "required_i6_controls_for_stronger_claims": [
                "collapse_reabsorption_relabel_control",
                "old_basin_thickening_relabel_control",
                "transient_flow_sink_relabel_control",
                "label_only_basin_formation_control",
            ],
        },
        "replay_evidence": {
            "status": "not_run_until_iteration_5",
            "records": runtime["replay_validation_records"],
        },
        "control_evidence": {
            "status": "not_run_until_iteration_6",
            "records": runtime["merge_leakage_control_records"],
        },
        "producer_audit_evidence": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_classification": child_records[0][
                "producer_residue_classification"
            ],
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "native_runtime_emitted",
            "producer_success_as_native_support_allowed": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "telemetry_example_evidence": {
            "fixture_source": repo_path(EXAMPLE_FIXTURE),
            "consumption_role": "fixture_pattern_only_runtime_artifact_generated_by_N25_2",
            "must_not_consume_as": ["proof_by_visualization", "MB6_support"],
        },
        "artifact_manifest": [
            {
                "artifact_role": "runtime_execution_trace",
                "digest": section_digests["runtime_execution_trace_digest"],
            },
            {
                "artifact_role": "flow_window_records",
                "digest": section_digests["flow_window_records_digest"],
            },
            {
                "artifact_role": "child_basin_state_records",
                "digest": section_digests["child_basin_state_records_digest"],
            },
            {
                "artifact_role": "topology_refinement_provenance",
                "digest": section_digests["topology_refinement_provenance_digest"],
            },
            {
                "artifact_role": "runtime_snapshot",
                "digest": section_digests["runtime_snapshot_digest"],
            },
        ],
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": embedded_artifact_manifest,
        "runtime_snapshot_digest": runtime["final_snapshot_digest"],
        "runtime_snapshot_artifact": runtime["runtime_snapshot_artifact"],
        "implementation_digest_bundle": implementation_digests,
        "implementation_no_mutation_proof": no_mutation_proof,
        "runtime_mutation_owner": "LGRC9V3_runtime_transition",
        "runtime_execution_from_closed_implementation": no_mutation_proof[
            "runtime_execution_from_closed_implementation"
        ],
        "defect_fix_attempted": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
        "mb6_gate_status": "not_applied",
        "mb6_gate_results": [],
        "mb6_blockers": [
            "replay_matrix_pending_iteration_5",
            "control_matrix_pending_iteration_6",
            "stress_matrix_pending_iteration_7",
            "mb6_gate_pending_iteration_8",
        ],
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_scope": {
            "unscoped_multi_basin_consumption_allowed": False,
            "scoped_consumption_status": "pending_iteration_8",
        },
        "producer_native_discipline": {
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "visual_evidence_limits": {
            "visual_evidence_used": False,
            "visual_evidence_role": "not_used_in_i4_runtime_probe",
        },
        "variant_comparability": {
            "variant_probe": False,
            "reference_probe": True,
        },
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": (
            "source-current MB3 child-basin candidate pending replay/control/stress; "
            "not MB5, not MB6"
        ),
        "ready_for_iteration_5_replay_persistence_matrix": True,
        "ready_for_iteration_4a_variant_probe": True,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    data_without_digest["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(data_without_digest),
            "repo_relative_paths_only",
        )
    )
    data_without_digest["failed_checks"] = [
        item["check_id"] for item in data_without_digest["checks"] if not item["passed"]
    ]
    data_without_digest["output_digest"] = digest_value(data_without_digest)
    return data_without_digest


def write_report(data: dict[str, Any]) -> None:
    checks = ["| Check | Passed |", "|---|---|"]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    child = data["child_basin_state_records"]["required_field_summary"][0]
    report = f"""# N25.2 Iteration 4 - Native LGRC9V3 Runtime Positive Probe

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

Iteration 4 runs the closed LGRC9V3 runtime and emits the first N25.2
source-current positive multi-basin candidate. It stops before replay and
controls, so the ceiling is MB3 candidate emission.

```text
i3_output_digest = {data['source_chain']['i3_output_digest']}
runtime_execution_performed = true
flow_window_record_count = {data['runtime_surface_evidence']['flow_window_record_count']}
child_basin_state_record_count = {data['runtime_surface_evidence']['child_basin_state_record_count']}
replay_validation_record_count = {data['runtime_surface_evidence']['replay_validation_record_count']}
merge_leakage_control_record_count = {data['runtime_surface_evidence']['merge_leakage_control_record_count']}
mb_ladder_candidate = {data['mb_ladder_candidate']}
mb6_gate_status = not_applied
mb6_supported = false
n26_consumption_effect = unscoped_consumption_blocked
runtime_execution_from_closed_implementation = {str(data['runtime_execution_from_closed_implementation']).lower()}
artifact_manifest_scope = {data['artifact_manifest_scope']}
topology_provenance_shape = {data['topology_refinement_provenance']['topology_provenance_shape']}
```

## Child-Basin Candidate

```text
child_basin_id = {child['child_basin_id']}
basin_signature_digest = {child['basin_signature_digest']}
trace_digest = {child['trace_digest']}
producer_native_mutation_owner = {child['producer_native_mutation_owner']}
producer_residue_status = {child['producer_residue_status']}
source_current_status = {child['source_current_status']}
flow_window_id = {child['flow_window_id']}
```

## Boundary

I4 does not validate persistence and does not run fail-closed controls. I5 must
consume this artifact for replay/persistence, I6 must consume it for controls,
and I8 must apply the MB6 gate.

The emitted topology/refinement provenance is collapse/reabsorption-shaped over
the existing graph. That is admissible for MB3 candidate emission, but I6 must
fail-close collapse/reabsorption relabel, old-basin thickening relabel,
transient-flow-sink relabel, and label-only basin formation before this row can
contribute to anything stronger.

Blocked in I4:

```text
MB5_control_backed_candidate
MB6
N26_unscoped_consumption
native_support
agency
semantic_learning
sentience
Phase_8_completion
```

## Checks

{chr(10).join(checks)}

Output digest:

```text
{data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()

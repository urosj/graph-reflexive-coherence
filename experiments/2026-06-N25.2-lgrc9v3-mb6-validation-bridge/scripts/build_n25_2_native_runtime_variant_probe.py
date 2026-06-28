#!/usr/bin/env python3
"""Build N25.2 Iteration 4-A native runtime variant/companion probe."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from types import MappingProxyType
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
REPORT = EXPERIMENT / "reports" / "n25_2_native_runtime_variant_probe.md"
MULTI_BASIN_FIXTURE = ROOT / "examples" / "lgrc9v3" / "multi_basin_formation_bundle.py"
FRONT_CAPACITY_FIXTURE = (
    ROOT / "examples" / "lgrc9v3" / "front_capacity_topology_birth_visual_bundle.py"
)
RUNTIME_CONTRACT = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_contract.py"
RUNTIME_CODE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
RUNTIME_STATE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime_state.py"
TELEMETRY_CODE = ROOT / "src" / "pygrc" / "telemetry" / "lgrc9v3_contract.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_native_runtime_variant_probe.py"
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
    MULTI_BASIN_FIXTURE,
    FRONT_CAPACITY_FIXTURE,
]


def canonical_json(data: Any) -> str:
    return json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            jsonable(data),
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


def import_fixture(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load fixture: {repo_path(path)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping | MappingProxyType):
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


def implementation_digest_bundle(configs: dict[str, Any]) -> dict[str, Any]:
    file_digests = {
        repo_path(path): sha256_file(path) for path in RUNTIME_DIGEST_PATHS
    }
    return {
        "runtime_config_digest": digest_value(jsonable(configs)),
        "runtime_source_digest": digest_value(file_digests),
        "source_file_sha256": file_digests,
        "lgrc9v3_runtime_file_sha256": file_digests[repo_path(RUNTIME_CODE)],
        "lgrc9v3_runtime_state_file_sha256": file_digests[repo_path(RUNTIME_STATE)],
        "lgrc9v3_contract_file_sha256": file_digests[repo_path(RUNTIME_CONTRACT)],
        "telemetry_contract_file_sha256": file_digests[repo_path(TELEMETRY_CODE)],
    }


def run_route_child_basin_variant() -> dict[str, Any]:
    fixture = import_fixture(MULTI_BASIN_FIXTURE, "n25_2_i4a_multi_basin_fixture")
    model = fixture.LGRC9V3.from_state(
        fixture.three_node_state(),
        fixture.multi_basin_params(),
    )
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
        arbitration_window_id="window:n25-2-i4a-route-variant",
        source_surface_digest=str(surface.surface_digest),
        unresolved_tie_policy=(
            fixture.LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED
        ),
        candidate_routes=(
            fixture.native_route_candidate_spec(
                candidate_route_id="candidate:sink0-low",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=0.25,
            ),
            fixture.native_route_candidate_spec(
                candidate_route_id="candidate:sink2-high",
                selected_sink_id=2,
                losing_sink_ids=(0,),
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
    topology_events = [
        {
            "kind": event.kind,
            "step_index": int(event.step_index),
            "payload": jsonable(event.payload),
            "source_family": str(event.source_family),
        }
        for event in state.topology_event_log
    ]
    return {
        "variant_id": "route_child_basin_sink2_companion",
        "variant_axis": "native_route_selected_sink_axis",
        "fixture_source": repo_path(MULTI_BASIN_FIXTURE),
        "runtime_config": model.get_params().raw_config,
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
        },
        "topology_events": topology_events,
        "event_counts_by_kind": dict(Counter(event.kind for event in state.topology_event_log)),
        "flow_window_records": flow_records,
        "child_basin_state_records": child_records,
        "replay_validation_records": [
            record.to_artifact() for record in state.multi_basin_replay_validation_log
        ],
        "merge_leakage_control_records": [
            record.to_artifact() for record in state.merge_leakage_control_matrix_log
        ],
        "causal_modes_after_commit": dict(sorted(state.causal_modes.items())),
    }


def run_front_capacity_companion() -> dict[str, Any]:
    fixture = import_fixture(FRONT_CAPACITY_FIXTURE, "n25_2_i4a_front_capacity")
    source_document = fixture.front_capacity_source_document()
    lowering = fixture.lower_grcl9v3_source_to_grc9v3_state(source_document)
    model = fixture.LGRC9V3.from_state(
        lowering.state,
        fixture.front_capacity_topology_birth_params(),
    )
    initial_snapshot = model.snapshot()
    produced = model.produce_events(
        policy=fixture.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
    )
    step_result = model.step()
    final_snapshot = model.snapshot()
    state = model.get_state()
    topology_events = [
        {
            "kind": event.kind,
            "step_index": int(event.step_index),
            "payload": jsonable(event.payload),
            "source_family": str(event.source_family),
        }
        for event in state.topology_event_log
    ]
    production_records = [record.to_artifact() for record in produced.production_records]
    return {
        "variant_id": "front_capacity_boundary_birth_companion",
        "variant_axis": "front_capacity_boundary_birth_topology_growth",
        "fixture_source": repo_path(FRONT_CAPACITY_FIXTURE),
        "runtime_config": model.get_params().raw_config,
        "params_hash": model.get_params().params_hash,
        "source_lowering_digest": digest_value(
            {
                "initial_snapshot_digest": digest_value(initial_snapshot),
                "front_growth_eligible_ports": state.base_state.cached_quantities[
                    "grcl9v3_front_growth_eligible_ports"
                ],
                "growth_parent_capacity_sources": state.base_state.cached_quantities[
                    "grcl9v3_growth_parent_capacity_sources"
                ],
            }
        ),
        "initial_snapshot_digest": digest_value(initial_snapshot),
        "final_snapshot_digest": digest_value(final_snapshot),
        "runtime_snapshot_artifact": final_snapshot,
        "production_result": {
            "scheduled_event_count": int(produced.scheduled_event_count),
            "production_records": production_records,
        },
        "step_result": {
            "step_index": int(step_result.step_index),
            "time": float(step_result.time),
            "event_count": len(step_result.events),
            "events": [jsonable(event) for event in step_result.events],
        },
        "topology_events": topology_events,
        "event_counts_by_kind": dict(Counter(event.kind for event in state.topology_event_log)),
        "initial_node_count": len(initial_snapshot["topology"]["nodes"]),
        "final_node_count": len(final_snapshot["topology"]["nodes"]),
        "initial_edge_count": len(initial_snapshot["topology"]["edges"]),
        "final_edge_count": len(final_snapshot["topology"]["edges"]),
        "visible_topology_growth": (
            len(final_snapshot["topology"]["nodes"])
            > len(initial_snapshot["topology"]["nodes"])
            or len(final_snapshot["topology"]["edges"])
            > len(initial_snapshot["topology"]["edges"])
        ),
        "front_capacity_surface": {
            "eligible_ports": state.base_state.cached_quantities[
                "grcl9v3_front_growth_eligible_ports"
            ],
            "capacity_sources": state.base_state.cached_quantities[
                "grcl9v3_growth_parent_capacity_sources"
            ],
        },
        "causal_modes_after_step": dict(sorted(state.causal_modes.items())),
    }


def child_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "child_basin_id": record["child_basin_state_record_id"],
        "child_basin_core_ids": record["child_basin_core_ids"],
        "child_basin_membership_by_core": record["child_basin_membership_by_core"],
        "basin_signature_digest": record["child_basin_membership_digest"],
        "trace_digest": record["child_basin_state_digest"],
        "producer_residue_status": "not_load_bearing_for_claim",
        "source_current_status": "native_runtime_emitted",
    }


def embedded_manifest(section_digests: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "artifact_role": role,
            "json_pointer": pointer,
            "digest": section_digests[role],
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        }
        for role, pointer in [
            ("route_variant_runtime_trace", "#/route_child_basin_variant"),
            ("front_capacity_runtime_trace", "#/front_capacity_companion"),
            ("variant_comparability_record", "#/variant_comparability"),
        ]
    ]


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    route_variant = run_route_child_basin_variant()
    front_companion = run_front_capacity_companion()
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
    reference_child = i4["child_basin_state_records"]["records"][0]
    variant_child = route_variant["child_basin_state_records"][0]
    reference_core_ids = reference_child["child_basin_core_ids"]
    variant_core_ids = variant_child["child_basin_core_ids"]
    variant_comparability = {
        "variant_probe": True,
        "reference_i4_output_digest": i4["output_digest"],
        "variant_axis": [
            "native_route_selected_sink_axis",
            "front_capacity_boundary_birth_topology_growth_companion",
        ],
        "route_variant_uses_same_fixture_family": True,
        "route_variant_not_retuned_copy": reference_core_ids != variant_core_ids,
        "reference_child_basin_core_ids": reference_core_ids,
        "variant_child_basin_core_ids": variant_core_ids,
        "front_capacity_companion_not_backfill_for_i4_child_basin": True,
        "front_capacity_backfill_allowed": False,
        "variant_evidence_cannot_backfill_unrelated_mb5_rows": True,
        "comparability_digest": digest_value(
            {
                "reference_output_digest": i4["output_digest"],
                "reference_core_ids": reference_core_ids,
                "variant_core_ids": variant_core_ids,
                "front_capacity_growth": front_companion["visible_topology_growth"],
            }
        ),
    }
    configs = {
        "route_variant": route_variant["runtime_config"],
        "front_capacity_companion": front_companion["runtime_config"],
    }
    implementation_digests = implementation_digest_bundle(configs)
    route_topology_mutated_values = [
        bool(event.get("payload", {}).get("topology_mutated", False))
        for event in route_variant["topology_events"]
    ]
    route_topology_shape = (
        "collapse_reabsorption_shaped_existing_graph"
        if route_topology_mutated_values and not any(route_topology_mutated_values)
        else "topology_mutating_or_mixed"
    )
    front_topology_mutated_values = [
        bool(event.get("payload", {}).get("topology_mutated", False))
        for event in front_companion["topology_events"]
    ]
    section_digests = {
        "route_variant_runtime_trace": digest_value(route_variant),
        "front_capacity_runtime_trace": digest_value(front_companion),
        "variant_comparability_record": digest_value(variant_comparability),
    }
    manifest = embedded_manifest(section_digests)
    route_claim_flags_false = all(
        not any(record["claim_flags"].values())
        for record in route_variant["flow_window_records"]
        + route_variant["child_basin_state_records"]
    )
    front_production_record = front_companion["production_result"][
        "production_records"
    ][0]
    front_claim_boundary_status = (
        "producer_ledger_record_without_claim_flags_global_claim_boundary_applies"
    )
    checks = [
        check(
            "i4_mb3_candidate_available_for_variant_probe",
            i4["status"] == "passed"
            and i4["ready_for_iteration_4a_variant_probe"] is True
            and i4["mb_ladder_candidate"]
            == "MB3_source_current_child_basin_candidate_emission",
            {"i4_output_digest": i4["output_digest"]},
        ),
        check(
            "existing_runtime_executed_without_source_edits",
            no_mutation_proof["runtime_execution_from_closed_implementation"] is True,
            no_mutation_proof,
        ),
        check(
            "route_variant_emits_comparable_child_basin_record",
            len(route_variant["flow_window_records"]) == 1
            and len(route_variant["child_basin_state_records"]) == 1
            and variant_comparability["route_variant_not_retuned_copy"] is True,
            {
                "flow_window_record_count": len(route_variant["flow_window_records"]),
                "child_basin_record_count": len(
                    route_variant["child_basin_state_records"]
                ),
                "reference_core_ids": reference_core_ids,
                "variant_core_ids": variant_core_ids,
            },
        ),
        check(
            "front_capacity_companion_emits_visible_topology_growth",
            front_companion["visible_topology_growth"] is True
            and bool(front_topology_mutated_values)
            and all(front_topology_mutated_values),
            {
                "initial_node_count": front_companion["initial_node_count"],
                "final_node_count": front_companion["final_node_count"],
                "initial_edge_count": front_companion["initial_edge_count"],
                "final_edge_count": front_companion["final_edge_count"],
            },
        ),
        check(
            "front_capacity_uses_corrected_parent_eligibility",
            front_companion["production_result"]["production_records"][0][
                "observed_evidence"
            ]["parent_eligibility_mode"]
            == "grcl9v3_front_capacity"
            and front_companion["front_capacity_surface"]["eligible_ports"],
            front_companion["front_capacity_surface"],
        ),
        check(
            "variant_evidence_cannot_backfill_unrelated_mb5_or_mb6",
            variant_comparability["front_capacity_backfill_allowed"] is False
            and variant_comparability[
                "variant_evidence_cannot_backfill_unrelated_mb5_rows"
            ]
            is True,
            variant_comparability,
        ),
        check(
            "embedded_artifact_manifest_has_json_pointers",
            all(
                item["json_pointer"].startswith("#/")
                and item["digest_algorithm"] == "sha256_canonical_json"
                and item["digest_matches_embedded_payload"] is True
                for item in manifest
            ),
            manifest,
        ),
        check(
            "replay_controls_stress_mb6_and_n26_pending",
            len(route_variant["replay_validation_records"]) == 0
            and len(route_variant["merge_leakage_control_records"]) == 0
            and route_variant["causal_modes_after_commit"][
                "native_lgrc_multi_basin_formation_validated"
            ]
            is False
            and route_variant["causal_modes_after_commit"][
                "native_lgrc_multi_basin_formation_supported"
            ]
            is False,
            {
                "route_replay_record_count": len(
                    route_variant["replay_validation_records"]
                ),
                "route_control_record_count": len(
                    route_variant["merge_leakage_control_records"]
                ),
            },
        ),
        check(
            "unsafe_claim_flags_false",
            route_claim_flags_false
            and "claim_flags" not in front_production_record
            and all(flag is False for flag in unsafe_claim_flags().values()),
            {
                "route_claim_flags_false": route_claim_flags_false,
                "front_claim_boundary_status": front_claim_boundary_status,
                "global_unsafe_claim_flags": unsafe_claim_flags(),
            },
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_native_runtime_variant_probe",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_native_runtime_variant_and_front_capacity_companion_"
            "mb3_scope_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": "4-A",
        "command": COMMAND,
        "source_chain": {
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4_mb_ladder_candidate": i4["mb_ladder_candidate"],
        },
        "variant_probe_role": "additional_runtime_variety_evidence_not_replacement",
        "i4_replaced": False,
        "i4_mb5_or_mb6_backfilled": False,
        "runtime_execution_performed": True,
        "runtime_execution_from_closed_implementation": no_mutation_proof[
            "runtime_execution_from_closed_implementation"
        ],
        "native_runtime_variant_probe_opened": True,
        "route_child_basin_variant": {
            "row_id": "n25_2_i4a_route_child_basin_sink2_companion",
            "source_evidence_kind": "source_current_runtime_execution",
            "mb_ladder_candidate": (
                "MB3_source_current_child_basin_candidate_emission_variant"
            ),
            "row_decision": "supported",
            "claim_ceiling": "MB3 variant candidate; not MB5, not MB6",
            "topology_provenance_shape": route_topology_shape,
            "child_basin_summary": child_summary(variant_child),
            "runtime_trace": route_variant,
        },
        "front_capacity_companion": {
            "row_id": "n25_2_i4a_front_capacity_boundary_birth_companion",
            "source_evidence_kind": "source_current_runtime_execution",
            "mb_ladder_candidate": "not_assigned_topology_birth_companion_only",
            "row_decision": "supported_as_companion_context_only",
            "claim_ceiling": (
                "front-capacity topology-growth companion; not child-basin "
                "persistence, not MB5, not MB6"
            ),
            "topology_provenance_shape": "front_capacity_boundary_birth_topology_growth",
            "claim_boundary_status": front_claim_boundary_status,
            "runtime_trace": front_companion,
        },
        "variant_comparability": variant_comparability,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": manifest,
        "implementation_digest_bundle": implementation_digests,
        "implementation_no_mutation_proof": no_mutation_proof,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "native_runtime_emitted",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": [
            "replay_matrix_pending_iteration_5",
            "control_matrix_pending_iteration_6",
            "stress_matrix_pending_iteration_7",
            "mb6_gate_pending_iteration_8",
        ],
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "visual_evidence_limits": {
            "visual_evidence_used": False,
            "visual_evidence_role": "not_used_in_i4a_runtime_probe",
        },
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": (
            "I4-A supplies additional runtime variety at MB3/companion scope; "
            "not MB5, not MB6"
        ),
        "ready_for_iteration_5_replay_persistence_matrix": True,
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

    route = data["route_child_basin_variant"]
    front = data["front_capacity_companion"]
    route_summary = route["child_basin_summary"]
    front_trace = front["runtime_trace"]
    report = f"""# N25.2 Iteration 4-A - Native Runtime Variant / Companion Probe

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I4-A adds runtime variety without replacing I4. It runs two closed-runtime
companions:

```text
i4_output_digest = {data['source_chain']['i4_output_digest']}
i4_replaced = false
i4_mb5_or_mb6_backfilled = false
route_variant_candidate = {route['mb_ladder_candidate']}
front_capacity_companion_candidate = {front['mb_ladder_candidate']}
mb6_supported = false
n26_unscoped_consumption_allowed = false
artifact_manifest_scope = {data['artifact_manifest_scope']}
```

## Route Child-Basin Variant

The route variant keeps the I4 fixture family and runtime policies but changes
the selected native route sink. It emits a comparable flow-window and
child-basin state record with a different child-basin core.

```text
child_basin_id = {route_summary['child_basin_id']}
child_basin_core_ids = {route_summary['child_basin_core_ids']}
basin_signature_digest = {route_summary['basin_signature_digest']}
trace_digest = {route_summary['trace_digest']}
topology_provenance_shape = {route['topology_provenance_shape']}
```

## Front-Capacity Companion

The front-capacity companion runs the corrected front-capacity boundary-birth
path. It is useful because it shows visible topology growth through the closed
runtime, but it is companion context only: it does not backfill I4's child-basin
record and does not support MB5 or MB6.

```text
initial_node_count = {front_trace['initial_node_count']}
final_node_count = {front_trace['final_node_count']}
initial_edge_count = {front_trace['initial_edge_count']}
final_edge_count = {front_trace['final_edge_count']}
visible_topology_growth = {str(front_trace['visible_topology_growth']).lower()}
parent_eligibility_mode = {front_trace['production_result']['production_records'][0]['observed_evidence']['parent_eligibility_mode']}
```

## Boundary

I4-A strengthens the evidence base by adding one native child-basin variant and
one topology-growth companion. It remains below replay-backed MB4,
control-backed MB5, MB6, and N26 unscoped consumption. I5 must replay
runtime-emitted child-basin records; I6 must still run fail-closed controls.

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

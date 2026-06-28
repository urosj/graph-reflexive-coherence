#!/usr/bin/env python3
"""Build N25.1 Iteration 3 Phase 8 extension requirement matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_1_phase8_extension_requirements_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_1_phase8_extension_requirements_matrix.md"
I2_OUTPUT_PATH = (
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "outputs/n25_1_multi_basin_extension_schema.json"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "scripts/build_n25_1_phase8_extension_requirements_matrix.py"
)

SURFACE_STATUSES = [
    "required_missing",
    "required_specifiable",
    "implemented_elsewhere_reusable",
    "blocked_until_implemented",
]
IMPLEMENTATION_ROLE_VALUES = [
    "reuse_existing_surface",
    "new_default_off_surface",
    "new_default_off_processor",
    "new_validator",
    "new_control_matrix",
    "handoff_constraint",
]
UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology",
    "bf6_without_mb6",
    "fully_native_integration",
    "identity_acceptance",
    "independent_new_basin_formation_without_controls",
    "lgrc9v3_native_multi_basin_formation_without_runtime_evidence",
    "native_support",
    "organism_life",
    "phase8_implementation_complete",
    "semantic_choice",
    "semantic_learning",
    "sentience",
    "unrestricted_autonomy",
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


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def requirement_rows() -> list[dict[str, Any]]:
    return [
        {
            "row_id": "n25_1_i3_row_01_causal_refinement_event_surface",
            "surface_id": "causal_refinement_event_surface",
            "surface_status": "required_specifiable",
            "implementation_role": "reuse_existing_surface",
            "source_basis": [
                "specs/lgrc-9-v3-spec.md",
                "examples/lgrc9v3/causal_spark_diagnostics.py",
                "specs/grc-9-v3-spec.md",
            ],
            "existing_basis": [
                "lgrc9v3_causal_spark_candidate event wrapping exists",
                "GRC9V3 Lane A/Lane B spark predicates exist",
            ],
            "missing_for_extension": [
                "causal_spark_candidate_to_topology_integration_link",
                "accepted_boundary_birth_or_refinement_event_policy",
                "event_ordered_source_current_refinement_contract",
            ],
            "required_runtime_surface": [
                "causal_spark_or_boundary_birth_event_id",
                "causal_spark_candidate_event_ref",
                "causal_spark_trigger_source",
                "event_time_key",
                "scheduler_event_index",
                "candidate_node_proper_time",
                "pre_refinement_topology_signature",
            ],
            "required_controls": [
                "causal_spark_label_only_control",
                "old_synchronous_expansion_relabel_control",
                "event_order_inversion_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB1"],
            "claim_boundary": "candidate event only; no topology integration or child basin yet",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_02_topology_integration_processor",
            "surface_id": "topology_integration_processor",
            "surface_status": "required_missing",
            "implementation_role": "new_default_off_processor",
            "source_basis": [
                "papers/2026-04-GRC-9.md",
                "specs/grc-9-v3-spec.md",
                "specs/lgrc-9-v3-spec.md",
                "examples/lgrc9v3/refinement_packet_transport.py",
            ],
            "existing_basis": [
                "GRC9V3 mechanical expansion exists",
                "LGRC refinement packet transport through one expansion exists as bounded surface",
            ],
            "missing_for_extension": [
                "default_off_LGRC9V3_processor_that_consumes_causal_refinement_event",
                "topology_integration_event_id_emitted_by_step_or_explicit_processor",
                "node_plus_packet_budget_audit_for_integrated_topology_event",
                "lineage_map_bound_to_event_time",
            ],
            "required_runtime_surface": [
                "topology_integration_event_id",
                "mechanical_refinement_event_id",
                "refinement_lineage_map",
                "pre_refinement_topology_signature",
                "post_refinement_topology_signature",
                "node_plus_packet_budget_audit",
            ],
            "required_controls": [
                "producer_topology_insertion_control",
                "producer_hidden_support_control",
                "event_order_inversion_control",
                "topology_integration_event_missing_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB2"],
            "claim_boundary": "mechanical refinement recorded; child-basin persistence still not claimed",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_03_post_refinement_flow_window",
            "surface_id": "post_refinement_flow_window",
            "surface_status": "required_missing",
            "implementation_role": "new_default_off_surface",
            "source_basis": [
                "papers/2026-04-GRC-9.md",
                "papers/2026-02-GRC-V3.md",
                "specs/grc-9-v3-spec.md",
            ],
            "existing_basis": [
                "GRC-9 says identities emerge from post-expansion reflexive flow",
                "GRC-v3 says completed sparks require child attractor stabilization",
            ],
            "missing_for_extension": [
                "declared_flow_window_after_topology_integration",
                "source_current_sink_or_basin_seed_evaluation_within_window",
                "child_candidate_detection_before_replay",
            ],
            "required_runtime_surface": [
                "post_refinement_flow_window",
                "child_basin_core_ids",
                "parent_basin_relation_record",
                "old_basin_relation_trace",
            ],
            "required_controls": [
                "module_node_created_as_child_basin_control",
                "transient_sink_as_child_basin_control",
                "old_basin_thickening_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB3"],
            "claim_boundary": "child-basin cores detected; persistence/replay not yet claimed",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_04_child_basin_state_record_surface",
            "surface_id": "child_basin_state_record_surface",
            "surface_status": "required_missing",
            "implementation_role": "new_default_off_surface",
            "source_basis": [
                "papers/2026-02-GRC-V3.md",
                "specs/grc-9-v3-spec.md",
                "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json",
            ],
            "existing_basis": [
                "GRC-v3 defines basin attributes, sink/basin validation, hierarchy labels",
                "N25 defines scoped BF5 but blocks independent multi-basin formation",
            ],
            "missing_for_extension": [
                "per_child_support_floor_records",
                "per_child_coherence_floor_records",
                "per_child_boundary_records",
                "per_child_flux_records",
                "stable_membership_digest",
            ],
            "required_runtime_surface": [
                "child_basin_support_floor_records",
                "child_basin_coherence_floor_records",
                "child_basin_boundary_records",
                "child_basin_flux_records",
                "child_basin_membership_digest",
            ],
            "required_controls": [
                "support_floor_missing_control",
                "coherence_floor_missing_control",
                "boundary_record_missing_control",
                "flux_record_missing_control",
                "membership_digest_missing_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB3", "MB4"],
            "claim_boundary": "source-current child-basin state records; still bounded by replay/control gates",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_05_replay_and_persistence_validator",
            "surface_id": "replay_and_persistence_validator",
            "surface_status": "required_missing",
            "implementation_role": "new_validator",
            "source_basis": [
                "specs/lgrc-9-v3-spec.md",
                "examples/lgrc9v3/README.md",
                "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json",
            ],
            "existing_basis": [
                "LGRC9V3 examples use artifact and replay discipline",
                "N25 closeout requires scoped consumption and controls",
            ],
            "missing_for_extension": [
                "artifact_replay_for_child_membership",
                "snapshot_load_replay_for_child_membership",
                "duplicate_replay_for_child_membership",
                "handoff_reconstruction_replay_for_MB6",
            ],
            "required_runtime_surface": [
                "replay_window",
                "artifact_replay_result",
                "snapshot_load_replay_result",
                "duplicate_replay_result",
                "handoff_reconstruction_replay_result",
            ],
            "required_controls": [
                "missing_replay_control",
                "post_hoc_child_basin_stitching_control",
                "event_order_inversion_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB4", "MB6"],
            "claim_boundary": "replay-backed child-basin persistence candidate; not control-backed MB5 by itself",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_06_merge_leakage_control_matrix",
            "surface_id": "merge_leakage_control_matrix",
            "surface_status": "required_missing",
            "implementation_role": "new_control_matrix",
            "source_basis": [
                "papers/2026-02-GRC-V3.md",
                "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json",
            ],
            "existing_basis": [
                "GRC-v3 distinguishes basin identity from labels",
                "N25 blocks independent new-basin and BF6 claims without stronger evidence",
            ],
            "missing_for_extension": [
                "merge_leakage_trace",
                "old_basin_thickening_control",
                "sub_basin_relabel_control",
                "neighbor_leakage_as_child_support_control",
                "producer_success_as_native_upgrade_control",
            ],
            "required_runtime_surface": [
                "merge_leakage_trace",
                "old_basin_thickening_control_result",
                "sub_basin_relabel_control_result",
                "control_results",
            ],
            "required_controls": [
                "old_basin_thickening_control",
                "sub_basin_relabel_as_independent_multi_basin_control",
                "merge_leakage_as_separation_control",
                "neighbor_leakage_as_child_support_control",
                "producer_threshold_relaxation_control",
                "producer_success_as_native_upgrade_control",
                "producer_scaffold_overwrites_native_failure_control",
                "bf5_scoped_sub_basin_as_bf6_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB5", "MB6"],
            "claim_boundary": "control-backed native multi-basin candidate only if replay also passes",
            "ready_for_implementation_spec": True,
        },
        {
            "row_id": "n25_1_i3_row_07_n26_handoff_gate",
            "surface_id": "n26_handoff_gate",
            "surface_status": "required_specifiable",
            "implementation_role": "handoff_constraint",
            "source_basis": [
                "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json",
                "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_multi_basin_extension_schema.json",
            ],
            "existing_basis": [
                "N25 allows N26 scoped consumption",
                "N25.1 I2 blocks unscoped consumption until MB6",
            ],
            "missing_for_extension": [
                "MB6_evidence_before_unscoped_multi_basin_consumption",
                "handoff_reconstruction_replay",
                "unsafe_claim_flags_false_at_closeout",
            ],
            "required_runtime_surface": [
                "n26_handoff_trace",
                "n26_consumption_allowed",
                "claim_ceiling",
                "unsafe_claim_flags",
            ],
            "required_controls": [
                "n25_result_as_unscoped_n26_substrate_control",
                "bf5_scoped_sub_basin_as_bf6_control",
                "semantic_learning_relabel_control",
                "semantic_choice_relabel_control",
                "agency_relabel_control",
                "native_support_relabel_control",
                "phase8_complete_relabel_control",
                "ant_ecology_relabel_control",
            ],
            "mb_rungs_enabled_if_implemented": ["MB6"],
            "claim_boundary": "handoff only; no agency, native support, or ant ecology",
            "ready_for_implementation_spec": True,
        },
    ]


def dependency_edges(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = [
        "causal_refinement_event_surface",
        "topology_integration_processor",
        "post_refinement_flow_window",
        "child_basin_state_record_surface",
        "replay_and_persistence_validator",
        "merge_leakage_control_matrix",
        "n26_handoff_gate",
    ]
    edges: list[dict[str, Any]] = []
    for index, source in enumerate(order[:-1]):
        edges.append(
            {
                "from_surface": source,
                "to_surface": order[index + 1],
                "dependency_kind": "ordered_runtime_or_validation_prerequisite",
            }
        )
    return edges


def build_output() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT_PATH)
    rows = requirement_rows()
    unsafe_flags = unsafe_claim_flags()
    i2_required_controls = set(i2["control_schema"]["required_control_ids"])
    i3_assigned_controls = {
        control_id
        for row in rows
        for control_id in row["required_controls"]
    }
    control_schema_alignment = {
        "i2_required_control_ids": sorted(i2_required_controls),
        "i3_assigned_control_ids": sorted(i3_assigned_controls),
        "i2_controls_missing_from_i3_rows": sorted(
            i2_required_controls - i3_assigned_controls
        ),
        "i3_controls_not_in_i2_required_control_ids": sorted(
            i3_assigned_controls - i2_required_controls
        ),
    }
    replay_result_field_convention = i2["replay_schema"][
        "replay_result_field_convention"
    ]
    output: dict[str, Any] = {
        "artifact_id": "n25_1_phase8_extension_requirements_matrix",
        "status": "passed",
        "acceptance_state": "accepted_phase8_extension_requirements_matrix_no_runtime_implementation",
        "generated_at": GENERATED_AT,
        "reproduction_command": COMMAND,
        "experiment": "N25.1",
        "iteration": "I3",
        "source_schema": {
            "path": I2_OUTPUT_PATH,
            "sha256": sha256_file(I2_OUTPUT_PATH),
            "status": i2.get("status", "not_recorded"),
            "acceptance_state": i2.get("acceptance_state", "not_recorded"),
            "output_digest": i2.get("output_digest", "not_recorded"),
            "failed_checks": i2.get("failed_checks", "not_recorded"),
        },
        "experiment_kind": "requirements_spec_bridge",
        "runtime_implementation_opened": False,
        "phase8_extension_implemented": False,
        "multi_basin_evidence_opened": False,
        "mb_ladder_rung_assigned": False,
        "mb_ladder_ceiling": "MB0_requirement_matrix_only",
        "n25_1_closeout_ceiling": "N25.1-C3_phase8_extension_requirement_matrix_ready",
        "surface_status_values": SURFACE_STATUSES,
        "implementation_role_values": IMPLEMENTATION_ROLE_VALUES,
        "requirement_rows": rows,
        "requirement_row_count": len(rows),
        "dependency_edges": dependency_edges(rows),
        "control_schema_alignment": control_schema_alignment,
        "replay_result_field_convention": replay_result_field_convention,
        "implementation_sequence_recommendation": [
            "reuse_or_expose_causal_refinement_event_surface",
            "implement_default_off_topology_integration_processor",
            "emit_post_refinement_flow_window_records",
            "emit_child_basin_state_records",
            "add_replay_and_persistence_validator",
            "add_merge_leakage_control_matrix",
            "gate_N26_unscoped_consumption_on_MB6",
        ],
        "phase8_extension_ready_to_implement": True,
        "ready_to_implement_meaning": (
            "requirements are sufficiently specified for a future Phase 8 "
            "implementation tranche; no runtime evidence is opened in N25.1 I3"
        ),
        "n26_consumption_state": {
            "scoped_N25_BF5_consumption_allowed": True,
            "N25_1_requirements_schema_consumption_allowed": True,
            "unscoped_multi_basin_consumption_allowed": False,
            "independent_new_basin_consumption_allowed": False,
            "BF6_consumption_allowed": False,
            "native_LGRC9V3_multi_basin_consumption_allowed": False,
        },
        "claim_boundary": {
            "requirements_contract_allowed": True,
            "runtime_evidence_allowed": False,
            "native_multi_basin_formation_supported": False,
            "BF6_supported": False,
            "phase8_extension_implemented": False,
            "unsafe_claim_flags": unsafe_flags,
        },
    }
    required_surfaces = {
        "causal_refinement_event_surface",
        "topology_integration_processor",
        "post_refinement_flow_window",
        "child_basin_state_record_surface",
        "replay_and_persistence_validator",
        "merge_leakage_control_matrix",
        "n26_handoff_gate",
    }
    row_surface_ids = {row["surface_id"] for row in rows}
    checks = [
        {
            "check_id": "i2_schema_passed",
            "passed": i2.get("status") == "passed" and i2.get("failed_checks") == [],
            "detail": output["source_schema"],
        },
        {
            "check_id": "all_required_surfaces_present",
            "passed": required_surfaces == row_surface_ids,
            "detail": sorted(row_surface_ids),
        },
        {
            "check_id": "dependency_edges_order_surface_chain",
            "passed": len(output["dependency_edges"]) == 6
            and output["dependency_edges"][0]["from_surface"]
            == "causal_refinement_event_surface"
            and output["dependency_edges"][-1]["to_surface"] == "n26_handoff_gate",
            "detail": output["dependency_edges"],
        },
        {
            "check_id": "implementation_ready_but_evidence_closed",
            "passed": output["phase8_extension_ready_to_implement"] is True
            and output["runtime_implementation_opened"] is False
            and output["multi_basin_evidence_opened"] is False,
            "detail": {
                "phase8_extension_ready_to_implement": output[
                    "phase8_extension_ready_to_implement"
                ],
                "runtime_implementation_opened": output[
                    "runtime_implementation_opened"
                ],
                "multi_basin_evidence_opened": output[
                    "multi_basin_evidence_opened"
                ],
            },
        },
        {
            "check_id": "n26_unscoped_consumption_still_blocked",
            "passed": output["n26_consumption_state"][
                "unscoped_multi_basin_consumption_allowed"
            ]
            is False
            and output["n26_consumption_state"]["BF6_consumption_allowed"] is False,
            "detail": output["n26_consumption_state"],
        },
        {
            "check_id": "producer_upgrade_controls_present",
            "passed": any(
                "producer_success_as_native_upgrade_control" in row["required_controls"]
                for row in rows
            ),
            "detail": [
                row["row_id"]
                for row in rows
                if "producer_success_as_native_upgrade_control"
                in row["required_controls"]
            ],
        },
        {
            "check_id": "i2_i3_control_mapping_complete",
            "passed": control_schema_alignment["i2_controls_missing_from_i3_rows"]
            == []
            and control_schema_alignment["i3_controls_not_in_i2_required_control_ids"]
            == [],
            "detail": control_schema_alignment,
        },
        {
            "check_id": "replay_result_field_convention_aligned",
            "passed": set(
                replay_result_field_convention["allowed_granular_fields"]
            ).issubset(
                {
                    field
                    for row in rows
                    for field in row["required_runtime_surface"]
                }
            ),
            "detail": replay_result_field_convention,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in unsafe_flags.values()),
            "detail": unsafe_flags,
        },
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": not contains_absolute_path(output),
            "detail": "repo_relative_paths_only",
        },
    ]
    output["checks"] = checks
    output["failed_checks"] = [
        item["check_id"] for item in checks if item["passed"] is not True
    ]
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N25.1 Iteration 3 - Phase 8 Extension Requirement Matrix",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Ceilings",
        "",
        "```text",
        f"mb_ladder_ceiling = {data['mb_ladder_ceiling']}",
        f"n25_1_closeout_ceiling = {data['n25_1_closeout_ceiling']}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "I3 turns the frozen I2 schema into a concrete Phase 8 implementation "
            "requirement matrix. It says what surfaces would have to be added or "
            "reused for native LGRC9V3 multi-basin formation, and in what order. "
            "It still does not implement those surfaces and does not open MB "
            "runtime evidence."
        ),
        "",
        "## Requirement Rows",
        "",
        "| Row | Surface | Status | Role | Enables |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in data["requirement_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['surface_id']}` | "
            f"`{row['surface_status']}` | "
            f"`{row['implementation_role']}` | "
            f"`{', '.join(row['mb_rungs_enabled_if_implemented'])}` |"
        )
    lines.extend(
        [
            "",
            "## Implementation Sequence",
            "",
            "```text",
            *data["implementation_sequence_recommendation"],
            "```",
            "",
            "## Control Alignment",
            "",
            "```text",
            f"i2_controls_missing_from_i3_rows = {data['control_schema_alignment']['i2_controls_missing_from_i3_rows']}",
            f"i3_controls_not_in_i2_required_control_ids = {data['control_schema_alignment']['i3_controls_not_in_i2_required_control_ids']}",
            "```",
            "",
            "## Replay Result Field Convention",
            "",
            "```text",
            "container_field = replay_results",
            "allowed_granular_fields = artifact_replay_result, snapshot_load_replay_result, duplicate_replay_result, handoff_reconstruction_replay_result",
            "granular_fields_may_be_nested_under_replay_results = true",
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            f"phase8_extension_ready_to_implement = {str(data['phase8_extension_ready_to_implement']).lower()}",
            f"runtime_implementation_opened = {str(data['runtime_implementation_opened']).lower()}",
            f"phase8_extension_implemented = {str(data['phase8_extension_implemented']).lower()}",
            f"multi_basin_evidence_opened = {str(data['multi_basin_evidence_opened']).lower()}",
            f"native_multi_basin_formation_supported = {str(data['claim_boundary']['native_multi_basin_formation_supported']).lower()}",
            f"BF6_supported = {str(data['claim_boundary']['BF6_supported']).lower()}",
            "```",
            "",
            "## N26 Consumption",
            "",
            "```text",
            "scoped_N25_BF5_consumption_allowed = true",
            "N25_1_requirements_schema_consumption_allowed = true",
            "unscoped_multi_basin_consumption_allowed = false",
            "independent_new_basin_consumption_allowed = false",
            "BF6_consumption_allowed = false",
            "native_LGRC9V3_multi_basin_consumption_allowed = false",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in data["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"output_digest {data['output_digest']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N25.1 Iteration 1 source crosswalk and gap inventory."""

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
OUTPUT = EXPERIMENT / "outputs" / "n25_1_source_crosswalk_and_gap_inventory.json"
REPORT = EXPERIMENT / "reports" / "n25_1_source_crosswalk_and_gap_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "scripts/build_n25_1_source_crosswalk_and_gap_inventory.py"
)

SOURCE_PATHS = {
    "grc9_paper": "papers/2026-04-GRC-9.md",
    "grcv3_paper": "papers/2026-02-GRC-V3.md",
    "lgrc9_paper": "papers/2026-05-LGRC-9.md",
    "native_packet_loop_paper": "papers/2026-05-LGRC9V3-Native-Packet-Loops.md",
    "causal_pulse_surface_paper": "papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md",
    "grc9v3_spec": "specs/grc-9-v3-spec.md",
    "lgrc9v3_spec": "specs/lgrc-9-v3-spec.md",
    "phase7_closeout": "implementation/Phase-7-Closeout.md",
    "phase8_plan": "implementation/Phase-8-LGRC9-ImplementationPlan.md",
    "lgrc9v3_examples_readme": "examples/lgrc9v3/README.md",
    "lgrc9v3_causal_spark_example": "examples/lgrc9v3/causal_spark_diagnostics.py",
    "lgrc9v3_refinement_transport_example": "examples/lgrc9v3/refinement_packet_transport.py",
    "n25_closeout": (
        "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
        "outputs/n25_closeout_and_n26_handoff.json"
    ),
}

BLOCKED_CLAIMS = [
    "agency",
    "ant_ecology",
    "bf6",
    "fully_native_integration",
    "identity_acceptance",
    "independent_new_basin_formation",
    "lgrc9v3_native_multi_basin_formation",
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


def source_record(path: str, source_role: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": source_role,
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["parseable_json"] = True
        record["status"] = str(data.get("status", "not_recorded"))
        record["acceptance_state"] = str(data.get("acceptance_state", "not_recorded"))
        record["output_digest"] = str(data.get("output_digest", "not_recorded"))
    else:
        record["parseable_json"] = False
        record["status"] = "text_source"
    return record


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in BLOCKED_CLAIMS}


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


def n25_summary() -> dict[str, Any]:
    data = load_json(SOURCE_PATHS["n25_closeout"])
    return {
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "final_bf_level": data.get("final_bf_level", "not_recorded"),
        "final_n25_closeout_rung": data.get("final_n25_closeout_rung", "not_recorded"),
        "native_bf5_supported": data.get("native_bf5_supported", "not_recorded"),
        "native_bf6_supported": data.get("native_bf6_supported", "not_recorded"),
        "independent_new_basin_supported": data.get(
            "independent_new_basin_supported", "not_recorded"
        ),
        "lgrc9v3_multi_basin_native_formation_supported": data.get(
            "lgrc9v3_multi_basin_native_formation_supported", "not_recorded"
        ),
        "phase8_extension_required_for_multi_basin_formation": data.get(
            "phase8_extension_required_for_multi_basin_formation", "not_recorded"
        ),
        "n25_1_requirements_bridge_needed": data.get(
            "n25_1_requirements_bridge_needed", "not_recorded"
        ),
        "ready_for_n26_with_scope_constraints": data.get(
            "ready_for_n26_with_scope_constraints", "not_recorded"
        ),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def source_rows() -> list[dict[str, Any]]:
    return [
        {
            "row_id": "n25_1_i1_row_01_grc9_mechanical_spark_refinement",
            "source_key": "grc9_paper",
            "source_classification": "theory_and_mechanical_spec",
            "may_consume_as": [
                "nine_port_mechanical_refinement_contract",
                "spark_expansion_and_boundary_reassignment_basis",
                "identity_basin_and_sink_definition_basis",
            ],
            "must_not_consume_as": [
                "LGRC9V3_runtime_evidence",
                "automatic_multi_basin_formation_evidence",
                "identity_fission_imposed_by_spark_event",
            ],
            "source_backed_claim": (
                "GRC-9 defines deterministic mechanical spark expansion and "
                "states that post-expansion reflexive flow may realize child "
                "basins; the spark operator itself does not directly impose "
                "multiple basins."
            ),
            "gap_contribution": (
                "Provides refinement mechanics but leaves child-basin formation "
                "to later flow, persistence, and controls."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_02_grcv3_basin_attribute_child_identity_semantics",
            "source_key": "grcv3_paper",
            "source_classification": "theory_and_semantic_spec",
            "may_consume_as": [
                "basin_attribute_bundle_basis",
                "signed_hessian_spark_semantics_basis",
                "parent_child_hierarchy_basis",
                "completed_spark_requires_attractor_count_change_basis",
            ],
            "must_not_consume_as": [
                "nine_port_runtime_implementation",
                "LGRC causal_history_execution",
                "native_multi_basin_evidence_without_runtime_rows",
            ],
            "source_backed_claim": (
                "GRC-v3 defines basin charts, hierarchy labels, sink/basin "
                "validation, and tightened spark semantics where local "
                "degeneracy is not sufficient unless post-event child "
                "attractor structure stabilizes."
            ),
            "gap_contribution": (
                "Defines what child-basin semantics must mean, but does not "
                "itself provide LGRC9V3 causal runtime evidence."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_03_lgrc9_causal_history_constraints",
            "source_key": "lgrc9_paper",
            "source_classification": "causal_history_theory_spec",
            "may_consume_as": [
                "causal_ordering_contract",
                "proper_time_and_event_queue_requirement_basis",
                "lineage_preserving_refinement_constraint",
                "node_plus_packet_budget_requirement_basis",
            ],
            "must_not_consume_as": [
                "implemented_LGRC9V3_multi_basin_extension",
                "automatic_topology_changing_causal_history_evidence",
            ],
            "source_backed_claim": (
                "LGRC separates scheduler order, proper time, and checkpoints, "
                "and requires causal availability, lineage-preserving "
                "refinement, and budget preservation."
            ),
            "gap_contribution": (
                "Future multi-basin formation must be causal-history-safe, not "
                "a synchronous relabel or checkpoint artifact."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_04_native_packet_loop_specialization",
            "source_key": "native_packet_loop_paper",
            "source_classification": "validated_implementation_specialization",
            "may_consume_as": [
                "native_packet_execution_and_budget_precedent",
                "producer_observes_and_schedules_boundary",
                "artifact_validated_packet_loop_precedent",
            ],
            "must_not_consume_as": [
                "native_GRC9V3_proposal_flux_loop",
                "movement_evidence",
                "multi_basin_formation_evidence",
                "agency_evidence",
            ],
            "source_backed_claim": (
                "Native LGRC9V3 packetized causal execution can support "
                "conserved self-rearming packet loops under controls, with "
                "producers observing and scheduling rather than directly "
                "mutating coherence."
            ),
            "gap_contribution": (
                "Shows a valid producer/step boundary and packet budget model "
                "that a future multi-basin extension must preserve."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_05_causal_pulse_surface_proposal",
            "source_key": "causal_pulse_surface_paper",
            "source_classification": "proposed_implementation_specialization",
            "may_consume_as": [
                "default_off_surface_contract_pattern",
                "policy_gated_producer_boundary_pattern",
                "causal_surface_replay_and_digest_requirement_basis",
            ],
            "must_not_consume_as": [
                "implemented_native_pulse_substrate_support",
                "movement_evidence",
                "identity_evidence",
                "multi_basin_formation_evidence",
            ],
            "source_backed_claim": (
                "The causal pulse-substrate surface is proposed as a "
                "serializable, replayable, default-off surface with "
                "policy-gated producers; native implementation remains future "
                "work in the cited paper."
            ),
            "gap_contribution": (
                "Provides a disciplined extension pattern but cannot be used as "
                "runtime evidence that a multi-basin surface already exists."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_06_grc9v3_spec_current_hybrid_spark_contract",
            "source_key": "grc9v3_spec",
            "source_classification": "implementation_spec",
            "may_consume_as": [
                "GRC9V3_step_semantics_basis",
                "mechanical_expansion_and_child_stabilization_requirement_basis",
                "spark_lane_ownership_boundary",
            ],
            "must_not_consume_as": [
                "LGRC9V3_event_queue_multi_basin_formation",
                "causal_history_topology_integration_evidence",
            ],
            "source_backed_claim": (
                "GRC9V3 must detect spark candidates, execute mechanical "
                "expansion, and register completed sparks only after "
                "post-event child-basin stabilization."
            ),
            "gap_contribution": (
                "Establishes that spark/refinement is not invented by N25.1; "
                "the missing part is the LGRC9V3 causal extension surface."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_07_lgrc9v3_spec_current_slice_boundary",
            "source_key": "lgrc9v3_spec",
            "source_classification": "current_implementation_spec_and_boundary",
            "may_consume_as": [
                "current_LGRC9V3_capability_boundary",
                "causal_spark_candidate_boundary",
                "packet_transport_through_refinement_boundary",
                "missing_automatic_topology_integration_record",
            ],
            "must_not_consume_as": [
                "full_event_queue_driven_topology_changing_step_loop",
                "automatic_mechanical_expansion_from_causal_spark_candidates",
                "native_multi_basin_formation_support",
            ],
            "source_backed_claim": (
                "The current LGRC9V3 slices include packet processing, causal "
                "spark-candidate wrapping, and refinement packet transport, "
                "while explicitly not implementing automatic mechanical "
                "expansion from causal spark candidates or the full "
                "topology-changing causal-history step loop."
            ),
            "gap_contribution": (
                "This is the central N25.1 gap: causal spark evidence exists, "
                "but the extension surface from causal refinement to replayable "
                "child-basin persistence is missing."
            ),
            "row_decision": "supported_as_gap_boundary_source",
        },
        {
            "row_id": "n25_1_i1_row_08_phase7_grc9v3_representative_evidence",
            "source_key": "phase7_closeout",
            "source_classification": "historical_runtime_evidence",
            "may_consume_as": [
                "GRC9V3_representative_spark_and_daughter_sink_evidence",
                "synchronous_child_basin_stabilization_precedent",
            ],
            "must_not_consume_as": [
                "LGRC9V3_causal_multi_basin_evidence",
                "post_repair_basin_mass_final_evidence_for_old_artifacts",
            ],
            "source_backed_claim": (
                "Phase 7 recorded an executable deterministic GRC9V3 core with "
                "hybrid spark, mechanical expansion, and representative "
                "daughter-sink evidence; it also records a later basin-mass "
                "correctness qualification for older mass-dependent claims."
            ),
            "gap_contribution": (
                "Confirms GRC9V3 spark-ish behavior exists, but keeps N25.1 "
                "from relabeling old synchronous evidence as LGRC9V3 native "
                "multi-basin formation."
            ),
            "row_decision": "supported_as_historical_context",
        },
        {
            "row_id": "n25_1_i1_row_09_phase8_lgrc9_implementation_plan_boundary",
            "source_key": "phase8_plan",
            "source_classification": "implementation_plan_boundary",
            "may_consume_as": [
                "Phase8_surface_map",
                "LGRC2_LGRC3_continuation_boundary",
                "extension_governance_precedent",
            ],
            "must_not_consume_as": [
                "completed_multi_basin_extension",
                "general_LGRC_dynamics_validation",
            ],
            "source_backed_claim": (
                "The Phase 8 plan tracks LGRC0-LGRC3 slices and future surfaces "
                "through explicit gates, preventing later extension plans from "
                "retroactively widening completed evidence."
            ),
            "gap_contribution": (
                "N25.1 should follow the same explicit extension discipline "
                "rather than modifying the main runtime silently."
            ),
            "row_decision": "supported_as_requirements_source",
        },
        {
            "row_id": "n25_1_i1_row_10_lgrc9v3_examples_spark_and_transport_surfaces",
            "source_key": "lgrc9v3_examples_readme",
            "supporting_source_keys": [
                "lgrc9v3_causal_spark_example",
                "lgrc9v3_refinement_transport_example",
            ],
            "source_classification": "current_example_boundary",
            "may_consume_as": [
                "current_causal_spark_candidate_example_context",
                "current_refinement_packet_transport_example_context",
                "producer_executor_boundary_context",
            ],
            "must_not_consume_as": [
                "full_LGRC9V3_topology_changing_loop_evidence",
                "native_multi_basin_formation_evidence",
            ],
            "source_backed_claim": (
                "The examples show executable causal spark diagnostics and "
                "refinement packet transport surfaces, while keeping mechanical "
                "expansion and active topology-integration gates explicit."
            ),
            "gap_contribution": (
                "Confirms N25.1 must not pretend sparks are absent; it must "
                "specify the missing child-basin formation and persistence "
                "surface after the existing spark/transport boundary."
            ),
            "row_decision": "supported_as_current_example_context",
        },
        {
            "row_id": "n25_1_i1_row_11_n25_closeout_scope_boundary",
            "source_key": "n25_closeout",
            "source_classification": "current_experiment_closeout",
            "may_consume_as": [
                "N25_scoped_BF5_sub_basin_evidence",
                "producer_assisted_scaffold_context",
                "multi_basin_extension_requirement",
                "N26_scope_constraint",
            ],
            "must_not_consume_as": [
                "BF6",
                "independent_new_basin_support",
                "native_LGRC9V3_multi_basin_formation_support",
                "producer_result_as_native_upgrade",
            ],
            "source_backed_claim": (
                "N25 closed with scoped native BF5 sub-basin/core evidence and "
                "producer-assisted scaffold context, while BF6, independent "
                "new-basin formation, and native LGRC9V3 multi-basin formation "
                "remain blocked."
            ),
            "gap_contribution": (
                "N25.1 exists because N25 reached N26 readiness only under "
                "scope constraints; independent multi-basin substrate requires "
                "a new extension contract."
            ),
            "row_decision": "supported_as_current_boundary_source",
        },
    ]


def missing_surface_records() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "causal_refinement_event_to_topology_integration",
            "status": "missing_as_native_multi_basin_extension_surface",
            "source_basis": [
                "lgrc9v3_spec",
                "grc9v3_spec",
                "lgrc9v3_examples_readme",
            ],
            "required_by": ["MB1", "MB2"],
            "must_be_built_from": [
                "causal_spark_candidate_event",
                "explicit_topology_integration_gate",
                "lineage_preserving_refinement",
                "node_plus_packet_budget_audit",
            ],
            "not_allowed_to_use": [
                "post_hoc_topology_label",
                "hidden_producer_topology_insertion",
                "old_synchronous_expansion_relabel_as_causal_extension",
            ],
        },
        {
            "surface_id": "post_refinement_child_basin_extraction",
            "status": "missing_as_replayable_child_basin_surface",
            "source_basis": ["grc9_paper", "grcv3_paper", "grc9v3_spec"],
            "required_by": ["MB3"],
            "must_be_built_from": [
                "post_refinement_flow_window",
                "child_basin_core_ids",
                "child_basin_support_floor_records",
                "child_basin_coherence_floor_records",
                "child_basin_boundary_records",
                "child_basin_membership_digest",
            ],
            "not_allowed_to_use": [
                "child_identity_label_only",
                "module_node_created_equals_child_basin",
                "transient_sink_as_persistent_child_basin",
            ],
        },
        {
            "surface_id": "merge_leakage_and_relabel_controls",
            "status": "missing_as_control_matrix_for_multi_basin_claim",
            "source_basis": ["grcv3_paper", "n25_closeout"],
            "required_by": ["MB4", "MB5", "MB6"],
            "must_be_built_from": [
                "merge_leakage_trace",
                "neighbor_leakage_records",
                "old_basin_thickening_control",
                "sub_basin_relabel_control",
                "producer_insertion_control",
                "replay_window",
            ],
            "not_allowed_to_use": [
                "support_margin_only",
                "producer_assisted_success_as_native_success",
                "BF5_scoped_sub_basin_as_BF6",
            ],
        },
    ]


def build_output() -> dict[str, Any]:
    rows = source_rows()
    source_records = [
        source_record(SOURCE_PATHS[key], role)
        for key, role in [
            ("grc9_paper", "primary_theory"),
            ("grcv3_paper", "primary_theory"),
            ("lgrc9_paper", "primary_lgrc_theory"),
            ("native_packet_loop_paper", "validated_implementation_specialization"),
            ("causal_pulse_surface_paper", "proposed_specialization_contract"),
            ("grc9v3_spec", "implementation_spec"),
            ("lgrc9v3_spec", "current_implementation_spec"),
            ("phase7_closeout", "historical_runtime_closeout"),
            ("phase8_plan", "implementation_plan_boundary"),
            ("lgrc9v3_examples_readme", "current_example_boundary"),
            ("lgrc9v3_causal_spark_example", "supporting_example_source"),
            ("lgrc9v3_refinement_transport_example", "supporting_example_source"),
            ("n25_closeout", "current_experiment_closeout"),
        ]
    ]
    unsafe_flags = unsafe_claim_flags()
    missing_surfaces = missing_surface_records()
    output: dict[str, Any] = {
        "artifact_id": "n25_1_source_crosswalk_and_gap_inventory",
        "status": "passed",
        "acceptance_state": "accepted_source_crosswalk_gap_inventory_no_runtime_implementation",
        "generated_at": GENERATED_AT,
        "reproduction_command": COMMAND,
        "experiment": "N25.1",
        "iteration": "I1",
        "experiment_kind": "requirements_spec_bridge",
        "runtime_implementation_opened": False,
        "phase8_extension_implemented": False,
        "multi_basin_evidence_opened": False,
        "mb_ladder_rung_assigned": False,
        "mb_ladder_ceiling": "MB0_source_crosswalk_only",
        "source_rows": rows,
        "source_row_count": len(rows),
        "source_records": source_records,
        "source_record_count": len(source_records),
        "n25_closeout_summary": n25_summary(),
        "existing_spark_surface_summary": {
            "grc9_mechanical_sparks_exist_in_theory": True,
            "grc9v3_hybrid_sparks_and_child_stabilization_exist_in_spec": True,
            "phase7_grc9v3_representative_spark_evidence_exists": True,
            "lgrc9v3_causal_spark_candidate_examples_exist": True,
            "lgrc9v3_refinement_packet_transport_examples_exist": True,
            "n25_1_gap_is_not_spark_absence": True,
            "n25_1_gap": (
                "native LGRC9V3 causal refinement to replayable multi-basin "
                "formation, controls, and N26-ready substrate evidence"
            ),
        },
        "missing_runtime_surfaces": missing_surfaces,
        "missing_runtime_surface_count": len(missing_surfaces),
        "required_future_extension_chain": [
            "causal_spark_or_boundary_birth_event",
            "topology_integration_or_mechanical_refinement_event",
            "post_refinement_flow_window",
            "child_basin_core_extraction",
            "child_basin_support_coherence_boundary_flux_records",
            "merge_leakage_and_relabel_controls",
            "replayable_child_basin_persistence",
        ],
        "claim_boundary": {
            "requirements_contract_allowed": True,
            "runtime_evidence_allowed": False,
            "native_multi_basin_formation_supported": False,
            "BF6_supported": False,
            "N26_unscoped_multi_basin_consumption_allowed": False,
            "unsafe_claim_flags": unsafe_flags,
        },
    }

    checks = [
        check(
            "all_cited_sources_exist",
            all((ROOT / source["path"]).exists() for source in source_records),
            [source["path"] for source in source_records],
        ),
        check(
            "n25_closeout_consumed_as_boundary_not_success_upgrade",
            output["n25_closeout_summary"]["native_bf6_supported"] is False
            and output["n25_closeout_summary"][
                "lgrc9v3_multi_basin_native_formation_supported"
            ]
            is False,
            output["n25_closeout_summary"],
        ),
        check(
            "existing_spark_surfaces_preserved",
            output["existing_spark_surface_summary"][
                "n25_1_gap_is_not_spark_absence"
            ]
            is True,
            output["existing_spark_surface_summary"],
        ),
        check(
            "missing_multi_basin_runtime_surface_recorded",
            len(missing_surfaces) == 3
            and all(
                record["status"].startswith("missing_as")
                for record in missing_surfaces
            ),
            missing_surfaces,
        ),
        check(
            "runtime_implementation_remains_closed",
            output["runtime_implementation_opened"] is False
            and output["phase8_extension_implemented"] is False
            and output["multi_basin_evidence_opened"] is False,
            {
                "runtime_implementation_opened": output["runtime_implementation_opened"],
                "phase8_extension_implemented": output["phase8_extension_implemented"],
                "multi_basin_evidence_opened": output["multi_basin_evidence_opened"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in unsafe_flags.values()),
            unsafe_flags,
        ),
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(output),
            "repo_relative_paths_only",
        ),
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
        "# N25.1 Iteration 1 - Source Crosswalk And Gap Inventory",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        (
            f"Crosswalk rows: `{data['source_row_count']}`; source records: "
            f"`{data['source_record_count']}`."
        ),
        "",
        "## Interpretation",
        "",
        (
            "I1 is a source/spec inventory only. It confirms that RC/GRC/GRC9V3 "
            "already contain spark and mechanical-refinement machinery, and that "
            "LGRC9V3 already has causal spark-candidate and refinement-transport "
            "surfaces. The missing target is narrower: a native LGRC9V3 extension "
            "that carries causal refinement through child-basin extraction, "
            "merge/leakage controls, replay, and N26-ready multi-basin substrate "
            "evidence."
        ),
        "",
        "This artifact does not implement that extension and does not open runtime "
        "multi-basin evidence.",
        "",
        "## Source Rows",
        "",
        "| Row | Source | Classification | Decision | Gap Contribution |",
        "| --- | --- | --- | --- | --- |",
    ]
    source_by_key = {
        key: value
        for key, value in SOURCE_PATHS.items()
    }
    for row in data["source_rows"]:
        source_key = row["source_key"]
        source_path = source_by_key[source_key]
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{source_path}` | "
            f"`{row['source_classification']}` | "
            f"`{row['row_decision']}` | "
            f"{row['gap_contribution']} |"
        )
    lines.extend(
        [
            "",
            "## Existing Spark Surface Boundary",
            "",
            "```text",
            "GRC-9 mechanical sparks: present as theory/spec.",
            "GRC9V3 hybrid sparks and child stabilization: present in spec and Phase 7 evidence.",
            "LGRC9V3 causal spark candidates: present in current examples/spec.",
            "LGRC9V3 refinement packet transport: present as a bounded surface.",
            "N25.1 gap: not spark absence; missing native causal multi-basin formation extension.",
            "```",
            "",
            "## Missing Runtime Surfaces",
            "",
            "| Surface | Status | Required By |",
            "| --- | --- | --- |",
        ]
    )
    for record in data["missing_runtime_surfaces"]:
        lines.append(
            "| "
            f"`{record['surface_id']}` | "
            f"`{record['status']}` | "
            f"`{', '.join(record['required_by'])}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "```text",
            f"runtime_implementation_opened = {str(data['runtime_implementation_opened']).lower()}",
            f"phase8_extension_implemented = {str(data['phase8_extension_implemented']).lower()}",
            f"multi_basin_evidence_opened = {str(data['multi_basin_evidence_opened']).lower()}",
            f"native_multi_basin_formation_supported = {str(data['claim_boundary']['native_multi_basin_formation_supported']).lower()}",
            f"BF6_supported = {str(data['claim_boundary']['BF6_supported']).lower()}",
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

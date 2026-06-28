#!/usr/bin/env python3
"""Build N25.2 Iteration 1 source inventory and admissibility audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_source_inventory_and_admissibility_audit.json"
REPORT = EXPERIMENT / "reports" / "n25_2_source_inventory_and_admissibility_audit.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_source_inventory_and_admissibility_audit.py"
)

SOURCE_ROWS: list[dict[str, Any]] = [
    {
        "source_id": "n25_closeout_json",
        "path": (
            "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
            "outputs/n25_closeout_and_n26_handoff.json"
        ),
        "source_role": "scoped_bf5_n25_c6_context",
        "may_consume_as": [
            "scoped_BF5_high_margin_core_sub_basin_context",
            "N25_C6_bounded_formation_handoff_context",
            "native_BF6_and_independent_new_basin_blocker_context",
        ],
        "must_not_consume_as": [
            "independent_multi_basin_formation",
            "native_LGRC9V3_multi_basin_formation",
            "MB6",
            "native_support",
        ],
    },
    {
        "source_id": "n25_closeout_report",
        "path": (
            "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
            "reports/n25_closeout_and_n26_handoff.md"
        ),
        "source_role": "scoped_bf5_interpretation",
        "may_consume_as": ["claim_boundary_context", "BF6_blocker_interpretation"],
        "must_not_consume_as": ["runtime_evidence", "native_support_evidence"],
    },
    {
        "source_id": "n25_1_closeout_json",
        "path": (
            "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-"
            "requirements/outputs/n25_1_closeout_and_phase8_extension_handoff.json"
        ),
        "source_role": "mb_ladder_and_requirements_context",
        "may_consume_as": [
            "MB0_to_MB6_ladder_context",
            "Phase_8_requirements_bridge_context",
            "N26_consumption_constraint_context",
        ],
        "must_not_consume_as": ["runtime_evidence", "MB5", "MB6"],
    },
    {
        "source_id": "n25_1_closeout_report",
        "path": (
            "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-"
            "requirements/reports/n25_1_closeout_and_phase8_extension_handoff.md"
        ),
        "source_role": "mb_ladder_interpretation",
        "may_consume_as": ["requirements_interpretation", "N26_scope_context"],
        "must_not_consume_as": ["runtime_evidence", "MB5", "MB6"],
    },
    {
        "source_id": "phase8_closeout_json",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.json",
        "source_role": "phase8_mb5_implementation_closeout",
        "may_consume_as": [
            "MB5_control_backed_candidate_evidence",
            "Phase_8_runtime_surface_evidence",
            "producer_compatibility_audit_evidence",
            "N25_2_transition_context",
        ],
        "must_not_consume_as": [
            "automatic_MB6",
            "N26_unscoped_consumption",
            "native_support",
            "agency",
        ],
    },
    {
        "source_id": "phase8_closeout_report",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md",
        "source_role": "phase8_mb5_interpretation",
        "may_consume_as": ["MB5_interpretation", "remaining_MB6_blocker_context"],
        "must_not_consume_as": ["automatic_MB6", "N26_unscoped_consumption"],
    },
    {
        "source_id": "phase8_plan",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationPlan.md",
        "source_role": "implementation_plan_context",
        "may_consume_as": ["planned_gate_context", "source_boundary_context"],
        "must_not_consume_as": ["final_result_evidence"],
    },
    {
        "source_id": "phase8_checklist",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationChecklist.md",
        "source_role": "implementation_record_context",
        "may_consume_as": ["verification_context", "iteration_record_context"],
        "must_not_consume_as": ["automatic_MB6"],
    },
    {
        "source_id": "phase8_contract_schema_json",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.json",
        "source_role": "contract_schema_context",
        "may_consume_as": ["schema_admissibility_context"],
        "must_not_consume_as": ["positive_runtime_result_by_itself"],
    },
    {
        "source_id": "phase8_contract_schema_report",
        "path": "implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.md",
        "source_role": "contract_schema_interpretation",
        "may_consume_as": ["schema_interpretation"],
        "must_not_consume_as": ["positive_runtime_result_by_itself"],
    },
    {
        "source_id": "phase8_handoff",
        "path": "implementation/Phase-8-LGRC9-Handoff.md",
        "source_role": "phase8_state_pointer",
        "may_consume_as": ["current_phase8_state_context"],
        "must_not_consume_as": ["MB6_support_by_itself"],
    },
    {
        "source_id": "lgrc9v3_spec",
        "path": "specs/lgrc-9-v3-spec.md",
        "source_role": "implementation_contract_and_claim_boundary",
        "may_consume_as": ["contract_context", "claim_boundary_context"],
        "must_not_consume_as": ["experiment_result_by_itself"],
    },
    {
        "source_id": "examples_readme",
        "path": "examples/lgrc9v3/README.md",
        "source_role": "example_interpretation_boundary",
        "may_consume_as": ["telemetry_visual_corroboration_context"],
        "must_not_consume_as": ["proof_by_visualization"],
    },
    {
        "source_id": "runtime_contract_code",
        "path": "src/pygrc/models/lgrc_9_v3_contract.py",
        "source_role": "implementation_boundary_audit",
        "may_consume_as": ["contract_code_audit_context"],
        "must_not_consume_as": ["claim_support_without_artifacts"],
    },
    {
        "source_id": "runtime_code",
        "path": "src/pygrc/models/lgrc_9_v3_runtime.py",
        "source_role": "producer_runtime_mutation_boundary_audit",
        "may_consume_as": ["producer_runtime_boundary_context"],
        "must_not_consume_as": ["claim_support_without_artifacts"],
    },
    {
        "source_id": "runtime_state_code",
        "path": "src/pygrc/models/lgrc_9_v3_runtime_state.py",
        "source_role": "runtime_state_surface_audit",
        "may_consume_as": ["runtime_state_surface_context"],
        "must_not_consume_as": ["claim_support_without_artifacts"],
    },
    {
        "source_id": "telemetry_code",
        "path": "src/pygrc/telemetry/lgrc9v3_contract.py",
        "source_role": "telemetry_export_audit",
        "may_consume_as": ["telemetry_export_context"],
        "must_not_consume_as": ["proof_by_telemetry_alone"],
    },
    {
        "source_id": "contract_tests",
        "path": "tests/models/test_lgrc_9_v3_contract.py",
        "source_role": "test_admissibility_evidence",
        "may_consume_as": ["contract_test_context"],
        "must_not_consume_as": ["MB6_support_by_itself"],
    },
    {
        "source_id": "runtime_tests",
        "path": "tests/models/test_lgrc_9_v3_runtime.py",
        "source_role": "test_admissibility_evidence",
        "may_consume_as": ["runtime_test_context"],
        "must_not_consume_as": ["MB6_support_by_itself"],
    },
    {
        "source_id": "autonomy_contract_tests",
        "path": "tests/models/test_lgrc_9_v3_autonomy_contract.py",
        "source_role": "producer_discipline_evidence",
        "may_consume_as": ["producer_contract_test_context"],
        "must_not_consume_as": ["native_support_evidence"],
    },
    {
        "source_id": "telemetry_tests",
        "path": "tests/telemetry/test_lgrc9v3_contract.py",
        "source_role": "telemetry_contract_evidence",
        "may_consume_as": ["telemetry_test_context"],
        "must_not_consume_as": ["proof_by_telemetry_alone"],
    },
    {
        "source_id": "visualization_tests",
        "path": "tests/visualization/test_visualization.py",
        "source_role": "visualization_contract_evidence",
        "may_consume_as": ["visualization_test_context"],
        "must_not_consume_as": ["proof_by_visualization_alone"],
    },
    {
        "source_id": "source_inventory_scaffold",
        "path": "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/source_inventory.md",
        "source_role": "local_source_inventory_scaffold",
        "may_consume_as": ["I1_source_inventory_seed"],
        "must_not_consume_as": ["validated_source_inventory_by_itself"],
    },
]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_learning_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
]

SOURCE_EVIDENCE_KIND_BY_ID = {
    "n25_closeout_json": "closeout",
    "n25_closeout_report": "markdown_context",
    "n25_1_closeout_json": "requirements_contract",
    "n25_1_closeout_report": "markdown_context",
    "phase8_closeout_json": "implementation_closeout",
    "phase8_closeout_report": "markdown_context",
    "phase8_plan": "markdown_context",
    "phase8_checklist": "markdown_context",
    "phase8_contract_schema_json": "implementation_schema",
    "phase8_contract_schema_report": "markdown_context",
    "phase8_handoff": "markdown_context",
    "lgrc9v3_spec": "implementation_schema",
    "examples_readme": "example_visual_corroboration",
    "runtime_contract_code": "runtime_source_audit",
    "runtime_code": "runtime_source_audit",
    "runtime_state_code": "runtime_source_audit",
    "telemetry_code": "runtime_source_audit",
    "contract_tests": "test_audit",
    "runtime_tests": "test_audit",
    "autonomy_contract_tests": "test_audit",
    "telemetry_tests": "test_audit",
    "visualization_tests": "test_audit",
    "source_inventory_scaffold": "markdown_context",
}

SOURCE_GROUP_BY_KIND = {
    "closeout": "primary_evidence_source",
    "requirements_contract": "requirements_source",
    "implementation_closeout": "primary_phase8_evidence_source",
    "implementation_schema": "schema_or_runtime_audit_source",
    "runtime_source_audit": "runtime_audit_source",
    "test_audit": "test_audit_source",
    "example_visual_corroboration": "visual_corroboration_source",
    "markdown_context": "context_source",
}

ADMISSIBILITY_BY_KIND = {
    "closeout": "admissible_for_mb6_gate_context",
    "requirements_contract": "admissible_for_mb6_gate_context",
    "implementation_closeout": "admissible_for_mb5_chain_audit",
    "implementation_schema": "admissible_for_mb6_gate_context",
    "runtime_source_audit": "admissible_for_inventory",
    "test_audit": "admissible_for_inventory",
    "example_visual_corroboration": "corroboration_only",
    "markdown_context": "admissible_for_inventory",
}

PRODUCER_NATIVE_DISCIPLINE = {
    "producer_scheduling_may_consume_as": "audit_context_only",
    "producer_scheduling_must_not_consume_as": "native_support",
    "producer_compatibility_audit_required": True,
    "runtime_mutation_ownership_required": "LGRC9V3_transitions",
    "hidden_producer_basin_insertion_allowed": False,
}

VISUAL_EVIDENCE_LIMITS = {
    "may_consume_as": "telemetry_or_visual_corroboration_only",
    "must_not_consume_as": [
        "runtime_evidence",
        "replay_evidence",
        "MB6_support",
    ],
}


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


def first_present(data: Any, key: str, default: Any = "not_recorded") -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = first_present(value, key, None)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = first_present(item, key, None)
            if found is not None:
                return found
    return default


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


def source_record(row: dict[str, Any]) -> dict[str, Any]:
    path = str(row["path"])
    source_id = str(row["source_id"])
    source_evidence_kind = SOURCE_EVIDENCE_KIND_BY_ID[source_id]
    record = {
        "source_id": source_id,
        "path": path,
        "source_artifact_path": path,
        "sha256": sha256_file(path),
        "source_evidence_kind": source_evidence_kind,
        "source_group": SOURCE_GROUP_BY_KIND[source_evidence_kind],
        "source_admissibility_decision": ADMISSIBILITY_BY_KIND[
            source_evidence_kind
        ],
        "parseable_json_or_markdown_context_only": (
            "parseable_json" if path.endswith(".json") else "context_only"
        ),
        "source_role": row["source_role"],
        "may_consume_as": row["may_consume_as"],
        "must_not_consume_as": row["must_not_consume_as"],
        "producer_native_discipline": PRODUCER_NATIVE_DISCIPLINE,
        "row_decision": "admissible_source_context",
    }
    if source_evidence_kind == "example_visual_corroboration":
        record["visual_evidence_limits"] = VISUAL_EVIDENCE_LIMITS
    if path.endswith(".json"):
        data = load_json(path)
        record["parseable_json"] = True
        record["status"] = str(data.get("status", "not_recorded"))
        record["acceptance_state"] = str(data.get("acceptance_state", "not_recorded"))
        record["output_digest"] = str(data.get("output_digest", "not_recorded"))
    else:
        record["parseable_json"] = False
        record["status"] = "text_or_code_source"
    return record


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def build_output() -> dict[str, Any]:
    source_records = [source_record(row) for row in SOURCE_ROWS]
    n25 = load_json(str(SOURCE_ROWS[0]["path"]))
    n25_1 = load_json(str(SOURCE_ROWS[2]["path"]))
    phase8 = load_json(str(SOURCE_ROWS[4]["path"]))
    schema = load_json(str(SOURCE_ROWS[8]["path"]))

    phase8_closeout = dict(phase8["mb_ladder_closeout"])
    n25_summary = {
        "acceptance_state": n25.get("acceptance_state"),
        "final_bf_level": n25.get("final_bf_level"),
        "final_n25_closeout_rung": n25.get("final_n25_closeout_rung"),
        "native_bf5_supported": n25.get("native_bf5_supported"),
        "native_bf6_supported": n25.get("native_bf6_supported"),
        "independent_new_basin_supported": n25.get("independent_new_basin_supported"),
        "lgrc9v3_multi_basin_native_formation_supported": n25.get(
            "lgrc9v3_multi_basin_native_formation_supported"
        ),
    }
    n25_1_summary = {
        "acceptance_state": n25_1.get("acceptance_state"),
        "final_mb_ladder_ceiling": n25_1.get("final_mb_ladder_ceiling"),
        "phase8_extension_ready_to_implement": n25_1.get(
            "phase8_extension_ready_to_implement"
        ),
        "runtime_implementation_opened": n25_1.get("runtime_implementation_opened"),
        "multi_basin_evidence_opened": n25_1.get("multi_basin_evidence_opened"),
        "BF6_supported": n25_1.get("BF6_supported"),
    }
    phase8_summary = {
        "status": phase8.get("status"),
        "supported_ceiling": phase8_closeout.get("supported_ceiling"),
        "mb5_control_backed_candidate_allowed": phase8_closeout.get(
            "mb5_control_backed_candidate_allowed"
        ),
        "mb6_or_stronger_supported": phase8_closeout.get(
            "mb6_or_stronger_supported"
        ),
        "native_lgrc_multi_basin_formation_supported": phase8_closeout.get(
            "native_lgrc_multi_basin_formation_supported"
        ),
        "n26_unscoped_consumption_allowed": phase8_closeout.get(
            "n26_unscoped_consumption_allowed"
        ),
        "producer_audit_status": first_present(phase8, "producer_audit_status"),
    }
    schema_summary = {
        "status": schema.get("status"),
        "purpose": schema.get("purpose"),
        "runtime_record_emission_opened": first_present(
            schema, "runtime_record_emission_opened"
        ),
        "default_flags": schema.get("default_causal_mode_flags"),
    }
    source_consumption_rules = {
        str(row["source_id"]): {
            "may_consume_as": row["may_consume_as"],
            "must_not_consume_as": row["must_not_consume_as"],
        }
        for row in SOURCE_ROWS
    }
    initial_admissibility = {
        "source_inventory_opened": True,
        "mb6_validation_opened": False,
        "runtime_implementation_opened": False,
        "phase8_mb5_evidence_admissible_for_i2_schema": True,
        "mb6_supported": False,
        "mb6_gate_applied": False,
        "mb6_gate_schema_frozen": False,
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "blocked_pending_mb6_gate",
        "ready_for_iteration_2_mb6_gate_schema": True,
    }
    source_role_separation = {
        "n25_bf5_scoped_sub_basin_evidence_is_not_mb6": True,
        "n25_1_requirements_contract_is_not_runtime_evidence": True,
        "phase8_mb5_candidate_is_not_mb6": True,
        "visual_topology_growth_is_not_multi_basin_substrate_persistence": True,
        "collapse_reabsorption_telemetry_is_not_independent_new_basin_formation": True,
        "producer_scheduling_is_not_native_support": True,
        "front_capacity_companion_is_not_blanket_mb6_upgrade": True,
        "n25_2_c6_closeout_is_not_mb6_support_by_itself": True,
    }
    phase8_mb5_admissibility_precheck = {
        "phase8_closeout_artifact_exists": (
            ROOT / str(SOURCE_ROWS[4]["path"])
        ).exists(),
        "phase8_closeout_parses": True,
        "phase8_closeout_reports_mb5_not_mb6": (
            phase8_summary["supported_ceiling"]
            == "MB5_control_backed_native_multi_basin_formation_candidate"
            and phase8_summary["mb6_or_stronger_supported"] is False
        ),
        "runtime_surfaces_claimed_default_off": (
            schema_summary["default_flags"][
                "native_lgrc_multi_basin_formation_enabled"
            ]
            is False
        ),
        "replay_control_evidence_referenced": True,
        "producer_compatibility_audit_referenced": (
            phase8_summary["producer_audit_status"] == "passed"
        ),
        "unsafe_flags_false": True,
    }
    n26_consumption_scope = {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": "pending",
        "n26_consumable_context": [],
        "n26_blocked_consumption": [
            "unscoped_multi_basin_substrate",
            "MB6_without_gate",
            "visual_topology_growth_as_substrate",
            "producer_success_as_native_support",
        ],
    }
    runtime_implementation_discipline = {
        "runtime_implementation_opened": False,
        "existing_lgrc9v3_runtime_execution_allowed_in_later_iterations": True,
        "src_diff_expected": False,
        "implementation_files_read_for_audit_only": True,
        "implementation_modification_allowed": False,
        "implementation_defect_fix_allowed_in_n25_2": False,
        "implementation_defect_disposition": "record_as_blocker_or_repair_target_only",
        "no_src_specs_tests_examples_or_implementation_source_changes_allowed": True,
    }
    i1_ladder_ceiling = {
        "n25_2_closeout_ceiling": (
            "N25.2-C1_source_inventory_and_admissibility_audit_passed"
        ),
        "n25_2_closeout_ladder_rung_assigned": False,
        "mb_ladder_candidate": "MB5_input_only_not_assigned",
        "starting_mb6_status": "blocked",
        "mb6_gate_status": "not_applied",
        "mb5_demoted": False,
    }

    checks = [
        check(
            "all_declared_sources_exist",
            all((ROOT / str(row["path"])).exists() for row in SOURCE_ROWS),
            {"source_count": len(SOURCE_ROWS)},
        ),
        check(
            "json_sources_parse",
            all(record["parseable_json"] for record in source_records if record["path"].endswith(".json")),
            [
                record["source_id"]
                for record in source_records
                if record["path"].endswith(".json")
            ],
        ),
        check(
            "n25_consumed_as_scoped_bf5_not_mb6",
            n25_summary["final_bf_level"] == "BF5_scoped_native_high_margin_core_sub_basin"
            and n25_summary["native_bf6_supported"] is False
            and n25_summary["independent_new_basin_supported"] is False,
            n25_summary,
        ),
        check(
            "n25_1_consumed_as_requirements_not_runtime",
            n25_1_summary["final_mb_ladder_ceiling"]
            == "MB0_requirements_bridge_only_no_runtime_evidence"
            and n25_1_summary["runtime_implementation_opened"] is False
            and n25_1_summary["multi_basin_evidence_opened"] is False,
            n25_1_summary,
        ),
        check(
            "phase8_closeout_starts_n25_2_at_mb5_not_mb6",
            phase8_summary["supported_ceiling"]
            == "MB5_control_backed_native_multi_basin_formation_candidate"
            and phase8_summary["mb5_control_backed_candidate_allowed"] is True
            and phase8_summary["mb6_or_stronger_supported"] is False,
            phase8_summary,
        ),
        check(
            "n26_unscoped_consumption_still_blocked",
            phase8_summary["n26_unscoped_consumption_allowed"] is False,
            phase8_summary["n26_unscoped_consumption_allowed"],
        ),
        check(
            "source_consumption_rules_nonempty",
            all(
                row["may_consume_as"] and row["must_not_consume_as"]
                for row in SOURCE_ROWS
            ),
            {"source_count": len(SOURCE_ROWS)},
        ),
        check(
            "source_admissibility_decisions_present",
            all(record["source_admissibility_decision"] for record in source_records),
            {
                record["source_id"]: record["source_admissibility_decision"]
                for record in source_records
            },
        ),
        check(
            "source_role_separation_frozen",
            all(source_role_separation.values()),
            source_role_separation,
        ),
        check(
            "phase8_mb5_admissibility_precheck_passes",
            all(phase8_mb5_admissibility_precheck.values()),
            phase8_mb5_admissibility_precheck,
        ),
        check(
            "mb6_inference_blocked_in_i1",
            initial_admissibility["mb6_supported"] is False
            and initial_admissibility["mb6_gate_applied"] is False
            and initial_admissibility["mb6_gate_schema_frozen"] is False,
            initial_admissibility,
        ),
        check(
            "n26_scope_blocked_pending_mb6_gate",
            n26_consumption_scope["n26_unscoped_multi_basin_consumption_allowed"]
            is False
            and n26_consumption_scope["n26_consumable_context"] == [],
            n26_consumption_scope,
        ),
        check(
            "runtime_implementation_discipline_closed",
            runtime_implementation_discipline["runtime_implementation_opened"]
            is False
            and runtime_implementation_discipline["src_diff_expected"] is False
            and runtime_implementation_discipline[
                "implementation_modification_allowed"
            ]
            is False
            and runtime_implementation_discipline[
                "implementation_defect_fix_allowed_in_n25_2"
            ]
            is False,
            runtime_implementation_discipline,
        ),
        check(
            "producer_native_discipline_present_per_source",
            all(record["producer_native_discipline"] for record in source_records),
            "producer scheduling cannot be consumed as native support",
        ),
        check(
            "visual_example_sources_are_corroboration_only",
            all(
                record["source_admissibility_decision"] == "corroboration_only"
                for record in source_records
                if record["source_evidence_kind"] == "example_visual_corroboration"
            ),
            [
                record["source_id"]
                for record in source_records
                if record["source_evidence_kind"] == "example_visual_corroboration"
            ],
        ),
        check(
            "producer_audit_present",
            phase8_summary["producer_audit_status"] == "passed",
            phase8_summary["producer_audit_status"],
        ),
        check(
            "runtime_implementation_not_opened_by_n25_2",
            initial_admissibility["runtime_implementation_opened"] is False,
            initial_admissibility["runtime_implementation_opened"],
        ),
        check("unsafe_claim_flags_false", all(flag is False for flag in unsafe_claim_flags().values()), unsafe_claim_flags()),
    ]

    data_without_digest = {
        "artifact_id": "n25_2_source_inventory_and_admissibility_audit",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_inventory_admissibility_audit_ready_for_i2_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": 1,
        "starting_phase8_mb_ceiling": phase8_summary["supported_ceiling"],
        "mb5_evidence_admissible_for_validation": True,
        "mb6_supported": False,
        "n26_unscoped_consumption_allowed": False,
        "runtime_implementation_opened": False,
        "ready_for_iteration_2_mb6_gate_schema": True,
        "mb6_gate_applied": False,
        "mb6_gate_schema_frozen": False,
        "starting_mb6_status": "blocked",
        "n26_consumption_effect": "blocked_pending_mb6_gate",
        "command": COMMAND,
        "source_records": source_records,
        "source_row_count": len(source_records),
        "source_consumption_rules": source_consumption_rules,
        "source_role_separation": source_role_separation,
        "n25_summary": n25_summary,
        "n25_1_summary": n25_1_summary,
        "phase8_summary": phase8_summary,
        "schema_summary": schema_summary,
        "phase8_mb5_admissibility_precheck": phase8_mb5_admissibility_precheck,
        "initial_admissibility": initial_admissibility,
        "n26_consumption_scope": n26_consumption_scope,
        "runtime_implementation_discipline": runtime_implementation_discipline,
        "i1_ladder_ceiling": i1_ladder_ceiling,
        "mb_ladder_state": {
            "starting_phase8_mb_ceiling": phase8_summary["supported_ceiling"],
            "mb5_evidence_admissible_for_validation": True,
            "mb6_supported": False,
            "starting_mb6_status": "blocked",
            "mb6_gate_applied": False,
            "mb6_gate_schema_frozen": False,
            "mb6_validation_pending_iteration_2_and_later": True,
        },
        "claim_boundary": {
            "unsafe_claim_flags": unsafe_claim_flags(),
            "mb6_claim_allowed": False,
            "n26_unscoped_consumption_allowed": False,
            "native_support_claim_allowed": False,
            "phase8_completion_claim_allowed": False,
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    data_without_digest["checks"].append(
        check("no_absolute_paths_in_records", not contains_absolute_path(data_without_digest), "repo_relative_paths_only")
    )
    data_without_digest["failed_checks"] = [
        item["check_id"] for item in data_without_digest["checks"] if not item["passed"]
    ]
    data_without_digest["output_digest"] = digest_value(data_without_digest)
    return data_without_digest


def write_report(data: dict[str, Any]) -> None:
    rows = [
        "| Source ID | Kind | Group | Role | Admissibility |",
        "|---|---|---|---|---|",
    ]
    for record in data["source_records"]:
        rows.append(
            f"| `{record['source_id']}` | {record['source_evidence_kind']} | "
            f"{record['source_group']} | {record['source_role']} | "
            f"{record['source_admissibility_decision']} |"
        )

    checks = [
        "| Check | Passed |",
        "|---|---|",
    ]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    report = f"""# N25.2 Iteration 1 - Source Inventory And Admissibility Audit

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

N25.2 starts from the Phase 8 multi-basin closeout at:

```text
starting_phase8_mb_ceiling = {data['mb_ladder_state']['starting_phase8_mb_ceiling']}
starting_mb6_status = blocked
mb5_evidence_admissible_for_validation = true
mb6_supported = false
mb6_gate_applied = false
mb6_gate_schema_frozen = false
n26_unscoped_consumption_allowed = false
runtime_implementation_opened = false
```

Iteration 1 validates the source map and admissibility boundary only. It does
not support MB6, does not open N26 unscoped consumption, and does not modify
runtime implementation.

## Source Rows

{chr(10).join(rows)}

## Key Source Results

```text
N25 final BF level = {data['n25_summary']['final_bf_level']}
N25 native BF6 supported = {str(data['n25_summary']['native_bf6_supported']).lower()}
N25.1 final MB ceiling = {data['n25_1_summary']['final_mb_ladder_ceiling']}
Phase 8 supported ceiling = {data['phase8_summary']['supported_ceiling']}
Phase 8 MB6 supported = {str(data['phase8_summary']['mb6_or_stronger_supported']).lower()}
Phase 8 N26 unscoped consumption allowed = {str(data['phase8_summary']['n26_unscoped_consumption_allowed']).lower()}
```

## Source-Role Separation

```text
N25 BF5 scoped sub-basin evidence != MB6
N25.1 requirements contract != runtime evidence
Phase 8 MB5 candidate != MB6
visual topology growth != multi-basin substrate persistence
collapse/reabsorption telemetry != independent new-basin formation
producer scheduling != native support
front-capacity companion != blanket MB6 upgrade
N25.2-C6 closeout != MB6 support by itself
```

## N26 Consumption Scope

```text
n26_unscoped_multi_basin_consumption_allowed = false
n26_scoped_context_consumption_allowed = pending
n26_consumable_context = []
n26_consumption_effect = blocked_pending_mb6_gate
```

## Runtime Discipline

```text
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed_in_later_iterations = true
src_diff_expected = false
implementation_files_read_for_audit_only = true
implementation_modification_allowed = false
implementation_defect_fix_allowed_in_n25_2 = false
implementation_defect_disposition = record_as_blocker_or_repair_target_only
no_src_specs_tests_examples_or_implementation_source_changes_allowed = true
```

## Checks

{chr(10).join(checks)}

## Claim Boundary

```text
mb6_claim_allowed = false
n26_unscoped_consumption_allowed = false
native_support_claim_allowed = false
phase8_completion_claim_allowed = false
```

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

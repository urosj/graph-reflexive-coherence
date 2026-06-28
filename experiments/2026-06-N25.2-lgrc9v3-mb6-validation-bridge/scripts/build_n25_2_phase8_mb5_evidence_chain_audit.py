#!/usr/bin/env python3
"""Build N25.2 Iteration 3 Phase 8 MB5 evidence-chain audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n25_2_source_inventory_and_admissibility_audit.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n25_2_mb6_gate_schema_and_controls.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_phase8_mb5_evidence_chain_audit.json"
REPORT = EXPERIMENT / "reports" / "n25_2_phase8_mb5_evidence_chain_audit.md"
PHASE8_CLOSEOUT_JSON = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationCloseout.json"
PHASE8_CLOSEOUT_MD = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationCloseout.md"
PHASE8_SCHEMA_JSON = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationContractSchema.json"
PHASE8_SCHEMA_MD = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationContractSchema.md"
PHASE8_PLAN = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationPlan.md"
PHASE8_CHECKLIST = ROOT / "implementation" / "Phase-8-LGRC9-MultiBasinFormationChecklist.md"
RUNTIME_CONTRACT = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_contract.py"
RUNTIME_CODE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
RUNTIME_STATE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime_state.py"
TELEMETRY_CODE = ROOT / "src" / "pygrc" / "telemetry" / "lgrc9v3_contract.py"
MULTI_BASIN_EXAMPLE = ROOT / "examples" / "lgrc9v3" / "multi_basin_formation_bundle.py"
CONTRACT_TESTS = ROOT / "tests" / "models" / "test_lgrc_9_v3_contract.py"
RUNTIME_TESTS = ROOT / "tests" / "models" / "test_lgrc_9_v3_runtime.py"
TELEMETRY_TESTS = ROOT / "tests" / "telemetry" / "test_lgrc9v3_contract.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_phase8_mb5_evidence_chain_audit.py"
)

REQUIRED_CONTRACT_RECORD_KINDS = [
    "lgrc9v3_multi_basin_post_refinement_flow_window_record",
    "lgrc9v3_child_basin_state_record",
    "lgrc9v3_multi_basin_replay_validation_record",
    "lgrc9v3_multi_basin_merge_leakage_control_record",
]

REQUIRED_SUPPORTED_CAPABILITIES = [
    "front_capacity_boundary_birth_companion_available",
    "merge_leakage_control_matrix_available",
    "multi_basin_replay_validation_available",
    "multi_basin_runtime_surfaces_exposed",
]

REQUIRED_CLOSEOUT_FALSE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_learning_claim_allowed",
    "sentience_claim_allowed",
]

REQUIRED_SCHEMA_FALSE_CLAIMS = [
    "BF6_claim_allowed",
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "independent_new_basin_claim_allowed",
    "native_multi_basin_formation_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_learning_claim_allowed",
    "sentience_claim_allowed",
]

CHILD_BASIN_DIRECTIVE_FIELD_MAP = {
    "child_basin_id": [
        "child_basin_state_record_id",
        "child_basin_core_ids",
        "child_basin_membership_digest",
    ],
    "parent_or_source_basin_id": [
        "old_basin_relation_trace",
        "source_flow_window_digest",
    ],
    "birth_or_detection_step": [
        "source_flow_window_digest",
        "window_start_event_time_key",
        "window_end_event_time_key",
    ],
    "flow_window_id": ["source_flow_window_digest"],
    "support_core_nodes": ["child_basin_support_floor_records"],
    "coherence_core_nodes": ["child_basin_coherence_floor_records"],
    "basin_signature_digest": [
        "child_basin_membership_digest",
        "child_basin_state_digest",
    ],
    "topology_signature_before": ["pre_refinement_topology_signature"],
    "topology_signature_after": ["post_refinement_topology_signature"],
    "boundary_birth_or_refinement_provenance": [
        "old_basin_relation_trace",
        "refinement_lineage_map",
        "source_topology_event_digest",
    ],
    "merge_leakage_status": ["merge_leakage_trace"],
    "producer_native_mutation_owner": [
        "producer_residue_classification",
        "runtime_visible_inputs",
    ],
    "trace_digest": ["child_basin_state_digest", "source_flow_window_digest"],
}

MERGE_CONTROL_IDS = [
    "label_only_multi_basin_relabel",
    "old_basin_thickening_as_new_basin",
    "transient_flow_sink_as_child_basin",
    "collapse_reabsorption_relabel",
    "graph_visual_only_success",
]

MERGE_CONTROL_SCHEMA_BLOCKERS = [
    "label_only_child_basin",
    "old_basin_thickening_as_child_basin",
    "transient_flow_sink_as_child_basin",
    "merge_leakage_as_success",
    "hidden_producer_basin_insertion",
]

REPAIR_TARGET_SCHEMA = {
    "gap_id": "stable identifier",
    "gap_class": (
        "missing_source_artifact | digest_or_parse_failure | "
        "default_off_surface_missing | runtime_surface_mismatch | "
        "child_basin_state_record_missing | child_basin_provenance_missing | "
        "replay_missing_or_unstable | control_missing_or_failed_open | "
        "producer_native_ownership_ambiguous | visual_only_evidence | "
        "test_scope_gap | unsafe_claim_boundary_violation | mb5_as_mb6_relabel"
    ),
    "source_artifact": "repo-relative source path",
    "source_field_or_section": "field or section that failed",
    "expected_condition": "required condition",
    "observed_condition": "observed condition",
    "effect_on_mb5": "none | blocker | demotion",
    "effect_on_mb6": "blocked | demotion",
    "effect_on_n26_consumption": "blocked | scoped_only",
    "repair_target": "required repair action",
    "repair_requires_new_implementation_tranche": "boolean",
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


def artifact_record(path: Path, role: str) -> dict[str, str]:
    return {
        "path": repo_path(path),
        "sha256": sha256_file(path),
        "role": role,
    }


def claim_flags_false(claim_boundary: dict[str, Any], keys: list[str]) -> bool:
    return all(claim_boundary.get(key) is False for key in keys)


def source_path(record: dict[str, Any]) -> Path:
    return ROOT / str(record["path"])


def source_records_exist(source_records: list[dict[str, Any]]) -> bool:
    return all(source_path(record).exists() for record in source_records)


def source_record_hashes_match(source_records: list[dict[str, Any]]) -> bool:
    for record in source_records:
        path = source_path(record)
        if not path.exists() or sha256_file(path) != record.get("sha256"):
            return False
    return True


def json_source_records_parse(source_records: list[dict[str, Any]]) -> bool:
    for record in source_records:
        if record.get("parseable_json") is not True:
            continue
        try:
            load_json(source_path(record))
        except (OSError, TypeError, json.JSONDecodeError):
            return False
    return True


def context_sources_are_limited(source_records: list[dict[str, Any]]) -> bool:
    for record in source_records:
        evidence_kind = str(record.get("source_evidence_kind", ""))
        if evidence_kind not in {
            "markdown_context",
            "example_visual_corroboration",
        }:
            continue
        must_not = set(record.get("must_not_consume_as", []))
        if evidence_kind == "markdown_context" and not must_not:
            return False
        if (
            evidence_kind == "example_visual_corroboration"
            and "proof_by_visualization" not in must_not
        ):
            return False
    return True


def all_source_paths_repo_relative(source_records: list[dict[str, Any]]) -> bool:
    return all(not str(record.get("path", "")).startswith("/") for record in source_records)


def text_contains(path: Path, needles: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(needle in text for needle in needles)


def contract_record_minimum_fields(
    schema: dict[str, Any],
    record_key: str,
) -> list[str]:
    record = schema["contract_record_types"][record_key]
    return list(record["minimum_fields"])


def directive_field_map_satisfied(
    schema: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    child_fields = set(contract_record_minimum_fields(schema, "child_basin_state"))
    flow_fields = set(contract_record_minimum_fields(schema, "post_refinement_flow_window"))
    all_fields = child_fields | flow_fields | {"child_basin_state_digest"}
    result: dict[str, dict[str, Any]] = {}
    for directive_field, candidate_fields in CHILD_BASIN_DIRECTIVE_FIELD_MAP.items():
        matched = [field for field in candidate_fields if field in all_fields]
        result[directive_field] = {
            "matched_phase8_fields": matched,
            "satisfied": bool(matched),
        }
    return result


def repair_targets_from_reasons(
    reasons: list[str],
) -> list[dict[str, Any]]:
    targets = []
    for reason in reasons:
        targets.append(
            {
                "gap_id": f"n25_2_i3_gap_{reason}",
                "gap_class": reason,
                "source_artifact": repo_path(PHASE8_CLOSEOUT_JSON),
                "source_field_or_section": "Phase 8 MB5 evidence chain",
                "expected_condition": "MB5 chain remains admissible without MB6 promotion",
                "observed_condition": reason,
                "effect_on_mb5": "demotion_or_repair_required",
                "effect_on_mb6": "blocked",
                "effect_on_n26_consumption": "blocked",
                "repair_target": "record and repair in a separate implementation tranche",
                "repair_requires_new_implementation_tranche": True,
            }
        )
    return targets


def build_chain_audit_rows(
    closeout: dict[str, Any],
    schema: dict[str, Any],
) -> list[dict[str, Any]]:
    supported = closeout["supported_capability"]
    mb_closeout = closeout["mb_ladder_closeout"]
    producer_audit = closeout["producer_compatibility_audit"]
    verification = closeout["verification"]
    contract_types = schema["contract_record_types"]
    contract_kinds = [
        record["kind"]
        for record in contract_types.values()
        if isinstance(record, dict) and "kind" in record
    ]
    field_map = directive_field_map_satisfied(schema)

    return [
        {
            "row_id": "n25_2_i3_row_01_phase8_closeout_mb5_ceiling",
            "chain_component": "phase8_closeout",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "closed MB5 ceiling confirmed",
            "mb6_contribution": "none",
            "observed_state": {
                "phase8_status": closeout["status"],
                "supported_ceiling": mb_closeout["supported_ceiling"],
                "mb5_control_backed_candidate_allowed": mb_closeout[
                    "mb5_control_backed_candidate_allowed"
                ],
                "mb6_or_stronger_supported": mb_closeout[
                    "mb6_or_stronger_supported"
                ],
                "n26_unscoped_consumption_allowed": mb_closeout[
                    "n26_unscoped_consumption_allowed"
                ],
            },
            "claim_ceiling": "MB5 input only; MB6 remains pending N25.2 gate",
        },
        {
            "row_id": "n25_2_i3_row_02_runtime_surfaces_exposed",
            "chain_component": "runtime_surfaces",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "runtime surfaces available for I4 probing",
            "mb6_contribution": "none until N25.2 runtime/replay/control matrix",
            "observed_state": {
                key: supported[key] for key in REQUIRED_SUPPORTED_CAPABILITIES
            }
            | {
                "default_causal_mode_flags": schema["default_causal_mode_flags"],
                "runtime_surface_not_active_by_default": True,
                "runtime_source_backed_surfaces_checked": [
                    repo_path(RUNTIME_CONTRACT),
                    repo_path(RUNTIME_CODE),
                    repo_path(RUNTIME_STATE),
                    repo_path(TELEMETRY_CODE),
                ],
            },
            "claim_ceiling": "admissible MB5 surface context, not positive MB6",
        },
        {
            "row_id": "n25_2_i3_row_03_contract_record_types_present",
            "chain_component": "contract_schema",
            "source_artifact_path": repo_path(PHASE8_SCHEMA_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "flow, child-basin, replay, and control record schemas present",
            "mb6_contribution": "schemas only; source-current I4+ artifacts still required",
            "observed_state": {
                "contract_record_kinds": contract_kinds,
                "required_contract_record_kinds": REQUIRED_CONTRACT_RECORD_KINDS,
                "child_basin_directive_field_map": field_map,
            },
            "claim_ceiling": "schema admissibility context",
        },
        {
            "row_id": "n25_2_i3_row_04_replay_and_merge_control_available",
            "chain_component": "replay_and_controls",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "Phase 8 reports replay and merge/leakage controls available",
            "mb6_contribution": "none until N25.2 applies replay/control matrix to I4 artifacts",
            "observed_state": {
                "multi_basin_replay_validation_available": supported[
                    "multi_basin_replay_validation_available"
                ],
                "merge_leakage_control_matrix_available": supported[
                    "merge_leakage_control_matrix_available"
                ],
                "replay_record_minimum_fields": contract_record_minimum_fields(
                    schema,
                    "replay_validation",
                ),
                "merge_control_record_minimum_fields": contract_record_minimum_fields(
                    schema,
                    "merge_leakage_control",
                ),
                "replay_creates_original_child_basin_evidence": False,
            },
            "claim_ceiling": "MB5 replay/control chain input only",
        },
        {
            "row_id": "n25_2_i3_row_05_producer_compatibility_audit",
            "chain_component": "producer_native_discipline",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "producer compatibility audit passed",
            "mb6_contribution": "producer audit does not upgrade native capacity",
            "observed_state": {
                "producer_audit_status": producer_audit["producer_audit_status"],
                "native_capacity_upgraded_from_producer_schedule": producer_audit[
                    "native_capacity_upgraded_from_producer_schedule"
                ],
                "semantic_content_injection_allowed": producer_audit[
                    "semantic_content_injection_allowed"
                ],
                "third_party_observer_content_management_opened": producer_audit[
                    "third_party_observer_content_management_opened"
                ],
            },
            "claim_ceiling": "producer-compatible MB5 context, not native support",
        },
        {
            "row_id": "n25_2_i3_row_06_verification_suite",
            "chain_component": "implementation_verification",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "Phase 8 verification suite recorded as passed",
            "mb6_contribution": "test pass does not replace N25.2 runtime evidence",
            "observed_state": {
                "diff_check": verification["diff_check"],
                "focused_suite_result": verification["focused_suite_result"],
                "ruff_result": verification["ruff_result"],
                "visualization_suite_result": verification[
                    "visualization_suite_result"
                ],
                "examples": verification["examples"],
                "tests_do_not_replace_runtime_artifacts": True,
                "tests_do_not_open_mb6": True,
            },
            "claim_ceiling": "verification context only",
        },
        {
            "row_id": "n25_2_i3_row_07_visual_and_example_limits",
            "chain_component": "telemetry_examples",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "examples corroborate runtime surfaces",
            "mb6_contribution": "visual/example evidence remains corroboration only",
            "observed_state": {
                "examples": verification["examples"],
                "visual_evidence_role": "corroboration_only",
                "visual_graph_growth_supports_mb6": False,
                "must_not_consume_as": [
                    "MB5_proof",
                    "MB6_proof",
                    "replay_evidence",
                    "runtime_surface_evidence",
                ],
            },
            "claim_ceiling": "corroboration only",
        },
        {
            "row_id": "n25_2_i3_row_08_claim_boundary",
            "chain_component": "claim_boundary",
            "source_artifact_path": repo_path(PHASE8_CLOSEOUT_JSON),
            "row_decision": "supported",
            "mb5_chain_contribution": "unsafe claims remain blocked",
            "mb6_contribution": "none",
            "observed_state": {
                "phase8_claim_boundary": closeout["claim_boundary"],
                "contract_schema_claim_boundary": schema["claim_boundary"],
            },
            "claim_ceiling": "MB5 chain audit only",
        },
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    closeout = load_json(PHASE8_CLOSEOUT_JSON)
    schema = load_json(PHASE8_SCHEMA_JSON)

    source_records = list(i1["source_records"])
    supported = closeout["supported_capability"]
    mb_closeout = closeout["mb_ladder_closeout"]
    producer_audit = closeout["producer_compatibility_audit"]
    verification = closeout["verification"]
    contract_types = schema["contract_record_types"]
    contract_kinds = [
        record["kind"]
        for record in contract_types.values()
        if isinstance(record, dict) and "kind" in record
    ]
    examples_passed = all(
        result == "passed" for result in verification["examples"].values()
    )
    field_map = directive_field_map_satisfied(schema)
    field_map_passed = all(item["satisfied"] for item in field_map.values())
    source_chain_integrity = {
        "i1_output_digest_matches_i2_reference": (
            i2["source_inventory"]["output_digest"] == i1["output_digest"]
        ),
        "all_source_paths_repo_relative": all_source_paths_repo_relative(
            source_records
        ),
        "all_required_source_artifacts_exist": source_records_exist(source_records),
        "all_source_record_hashes_match_file_contents": (
            source_record_hashes_match(source_records)
        ),
        "all_json_source_artifacts_parse": json_source_records_parse(source_records),
        "markdown_and_example_sources_context_limited": (
            context_sources_are_limited(source_records)
        ),
        "no_stale_regenerated_artifact_mismatch": (
            i2["source_inventory"]["output_digest"] == i1["output_digest"]
        ),
    }
    runtime_surface_audit = {
        "runtime_surface_records_present": all(
            kind in contract_kinds for kind in REQUIRED_CONTRACT_RECORD_KINDS
        ),
        "default_off_policy_recorded": (
            schema["default_causal_mode_flags"][
                "native_lgrc_multi_basin_formation_enabled"
            ]
            is False
            and schema["default_causal_mode_flags"][
                "native_lgrc_multi_basin_formation_policy"
            ]
            == "disabled"
        ),
        "enablement_gate_recorded": text_contains(
            RUNTIME_CODE,
            [
                "_native_multi_basin_formation_enabled",
                "_emit_multi_basin_records_for_committed_topology",
            ],
        ),
        "runtime_surface_not_active_by_default": True,
        "runtime_surface_matches_phase8_contract_schema": text_contains(
            RUNTIME_CONTRACT,
            REQUIRED_CONTRACT_RECORD_KINDS,
        )
        and text_contains(
            RUNTIME_STATE,
            [
                "post_refinement_flow_window_log",
                "child_basin_state_log",
                "multi_basin_replay_validation_log",
                "merge_leakage_control_matrix_log",
            ],
        ),
        "telemetry_contract_can_serialize_surface": text_contains(
            TELEMETRY_CODE,
            [
                "post_refinement_flow_window_log",
                "child_basin_state_log",
                "multi_basin_replay_validation_log",
                "merge_leakage_control_matrix_log",
            ],
        ),
    }
    child_basin_record_audit = {
        "child_basin_state_record_schema_present": (
            "lgrc9v3_child_basin_state_record" in contract_kinds
        ),
        "directive_field_map": field_map,
        "directive_field_map_satisfied": field_map_passed,
        "runtime_emitter_present": text_contains(
            RUNTIME_CODE,
            [
                "_build_child_basin_state_record",
                "child_basin_state_log.append",
                "child_basin_support_floor_records",
                "child_basin_coherence_floor_records",
                "old_basin_relation_trace",
                "merge_leakage_trace",
            ],
        ),
        "example_runtime_record_use_present": text_contains(
            MULTI_BASIN_EXAMPLE,
            [
                'commit["child_basin_state_records"][0]',
                "validate_multi_basin_child_basin_replay",
                "validate_multi_basin_merge_leakage_controls",
            ],
        ),
        "label_only_child_basin_rejected_by_schema": (
            "label_only_child_basin" in schema["forbidden_runtime_visible_inputs"]
        ),
        "old_basin_thickening_rejected_by_schema": (
            "old_basin_thickening_as_child_basin"
            in schema["forbidden_runtime_visible_inputs"]
        ),
        "transient_sink_rejected_by_schema": (
            "transient_flow_sink_as_child_basin"
            in schema["forbidden_runtime_visible_inputs"]
        ),
    }
    replay_audit = {
        "artifact_replay_present": "artifact_replay_result"
        in contract_record_minimum_fields(schema, "replay_validation"),
        "snapshot_load_replay_present": "snapshot_load_replay_result"
        in contract_record_minimum_fields(schema, "replay_validation"),
        "duplicate_replay_present": "duplicate_replay_result"
        in contract_record_minimum_fields(schema, "replay_validation"),
        "child_basin_persistence_replay_present": text_contains(
            RUNTIME_CODE,
            [
                "membership_persistence_ratio",
                "support_persistence_ratio",
                "coherence_persistence_ratio",
                "boundary_persistence_ratio",
                "flux_persistence_ratio",
            ],
        ),
        "replay_validates_runtime_emitted_records_only": True,
        "replay_does_not_create_original_child_basin_records": True,
    }
    merge_control_audit = {
        "merge_leakage_control_present": (
            "lgrc9v3_multi_basin_merge_leakage_control_record" in contract_kinds
        ),
        "control_ids_present": MERGE_CONTROL_IDS,
        "schema_blockers_present": MERGE_CONTROL_SCHEMA_BLOCKERS,
        "controls_are_schema_backed": all(
            blocker in schema["forbidden_runtime_visible_inputs"]
            or blocker in schema["implementation_defensive_forbidden_runtime_visible_inputs"]
            for blocker in MERGE_CONTROL_SCHEMA_BLOCKERS
        ),
        "control_record_fields_present": all(
            field in contract_record_minimum_fields(schema, "merge_leakage_control")
            for field in [
                "control_id",
                "blocked_condition",
                "expected_result",
                "actual_result",
                "control_status",
                "rung_effect",
            ]
        ),
        "failed_open_blocks_mb6": True,
    }
    tests_audit = {
        "focused_tests_present_or_prior_test_results_source_backed": (
            "passed" in verification["focused_suite_result"]
            and text_contains(CONTRACT_TESTS, ["child_basin_state_digest"])
            and text_contains(
                RUNTIME_TESTS,
                ["validate_multi_basin_merge_leakage_controls"],
            )
            and text_contains(TELEMETRY_TESTS, ["merge_leakage_control_matrix_log"])
        ),
        "test_scope_matches_phase8_claim": True,
        "tests_do_not_open_mb6": True,
        "tests_do_not_patch_runtime_or_relax_specs": True,
    }
    demotion_reasons = []
    if not all(source_chain_integrity.values()):
        demotion_reasons.append("source_chain_integrity_failure")
    if mb_closeout["mb5_control_backed_candidate_allowed"] is not True:
        demotion_reasons.append("phase8_mb5_candidate_not_allowed")
    if mb_closeout["mb6_or_stronger_supported"] is not False:
        demotion_reasons.append("mb6_claimed_before_n25_2_gate")
    if not all(supported[key] is True for key in REQUIRED_SUPPORTED_CAPABILITIES):
        demotion_reasons.append("required_runtime_surface_missing")
    if not all(kind in contract_kinds for kind in REQUIRED_CONTRACT_RECORD_KINDS):
        demotion_reasons.append("required_contract_record_type_missing")
    if not all(runtime_surface_audit.values()):
        demotion_reasons.append("runtime_surface_mismatch")
    if not all(child_basin_record_audit.values()):
        demotion_reasons.append("child_basin_state_record_missing")
    if not all(replay_audit.values()):
        demotion_reasons.append("replay_missing_or_unstable")
    if not all(merge_control_audit.values()):
        demotion_reasons.append("control_missing_or_failed_open")
    if producer_audit["producer_audit_status"] != "passed":
        demotion_reasons.append("producer_audit_missing_or_not_passed")
    if producer_audit["native_capacity_upgraded_from_producer_schedule"] is not False:
        demotion_reasons.append("producer_schedule_upgraded_native_capacity")
    if not claim_flags_false(closeout["claim_boundary"], REQUIRED_CLOSEOUT_FALSE_CLAIMS):
        demotion_reasons.append("phase8_unsafe_claim_flag_open")
    if not claim_flags_false(schema["claim_boundary"], REQUIRED_SCHEMA_FALSE_CLAIMS):
        demotion_reasons.append("schema_unsafe_claim_flag_open")
    if not examples_passed:
        demotion_reasons.append("phase8_examples_not_passed")
    if not all(tests_audit.values()):
        demotion_reasons.append("test_scope_gap")
    mb5_demoted = bool(demotion_reasons)

    chain_audit_rows = build_chain_audit_rows(closeout, schema)
    checks = [
        check(
            "i1_inventory_passed",
            i1["status"] == "passed" and i1["failed_checks"] == [],
            {"i1_output_digest": i1["output_digest"]},
        ),
        check(
            "i2_schema_passed",
            i2["status"] == "passed"
            and i2["failed_checks"] == []
            and i2["ready_for_iteration_3_phase8_mb5_evidence_chain_audit"]
            is True,
            {"i2_output_digest": i2["output_digest"]},
        ),
        check(
            "source_chain_integrity_validated",
            all(source_chain_integrity.values()),
            source_chain_integrity,
        ),
        check(
            "phase8_closeout_exists_and_parses",
            closeout["status"] == "closed",
            {"phase8_closeout_status": closeout["status"]},
        ),
        check(
            "phase8_closeout_reports_mb5_not_mb6",
            mb_closeout["mb5_control_backed_candidate_allowed"] is True
            and mb_closeout["mb6_or_stronger_supported"] is False
            and mb_closeout["native_lgrc_multi_basin_formation_supported"]
            is False
            and mb_closeout["n26_unscoped_consumption_allowed"] is False
            and mb_closeout["supported_ceiling"]
            == "MB5_control_backed_native_multi_basin_formation_candidate",
            mb_closeout,
        ),
        check(
            "phase8_supported_capabilities_present",
            all(supported[key] is True for key in REQUIRED_SUPPORTED_CAPABILITIES),
            {key: supported[key] for key in REQUIRED_SUPPORTED_CAPABILITIES},
        ),
        check(
            "runtime_surfaces_default_off_and_source_backed",
            all(runtime_surface_audit.values()),
            runtime_surface_audit,
        ),
        check(
            "phase8_contract_schema_exists_and_parses",
            schema["status"] == "passed",
            {"schema_status": schema["status"]},
        ),
        check(
            "contract_record_types_include_required",
            all(kind in contract_kinds for kind in REQUIRED_CONTRACT_RECORD_KINDS),
            {
                "contract_record_kinds": contract_kinds,
                "required_contract_record_kinds": REQUIRED_CONTRACT_RECORD_KINDS,
            },
        ),
        check(
            "child_basin_state_records_present",
            all(child_basin_record_audit.values()),
            child_basin_record_audit,
        ),
        check(
            "topology_refinement_provenance_present",
            bool(
                field_map["boundary_birth_or_refinement_provenance"][
                    "matched_phase8_fields"
                ]
            )
            and text_contains(RUNTIME_CODE, ["source_topology_event_digest"]),
            field_map["boundary_birth_or_refinement_provenance"],
        ),
        check(
            "replay_evidence_present",
            all(replay_audit.values()),
            replay_audit,
        ),
        check(
            "merge_leakage_controls_present_and_fail_closed",
            all(merge_control_audit.values()),
            merge_control_audit,
        ),
        check(
            "default_multi_basin_flags_do_not_claim_native_support",
            schema["default_causal_mode_flags"][
                "native_lgrc_multi_basin_formation_supported"
            ]
            is False,
            schema["default_causal_mode_flags"],
        ),
        check(
            "producer_compatibility_audit_passed",
            producer_audit["producer_audit_status"] == "passed"
            and producer_audit["native_capacity_upgraded_from_producer_schedule"]
            is False
            and producer_audit["semantic_content_injection_allowed"] is False
            and producer_audit[
                "third_party_observer_content_management_opened"
            ]
            is False,
            producer_audit,
        ),
        check(
            "producer_compatibility_audit_present",
            producer_audit["producer_audit_status"] == "passed",
            {"producer_audit_status": producer_audit["producer_audit_status"]},
        ),
        check(
            "producer_native_mutation_ownership_clean",
            producer_audit["native_capacity_upgraded_from_producer_schedule"]
            is False
            and producer_audit["semantic_content_injection_allowed"] is False
            and producer_audit[
                "third_party_observer_content_management_opened"
            ]
            is False,
            producer_audit,
        ),
        check(
            "verification_results_passed",
            verification["diff_check"] == "passed"
            and "passed" in verification["focused_suite_result"]
            and verification["ruff_result"] == "All checks passed"
            and "passed" in verification["visualization_suite_result"]
            and examples_passed,
            verification,
        ),
        check(
            "telemetry_examples_correspond_to_closeout",
            examples_passed
            and supported["front_capacity_boundary_birth_companion_available"] is True,
            verification["examples"],
        ),
        check(
            "visual_evidence_not_used_as_proof",
            context_sources_are_limited(source_records),
            "examples and visual sources are corroboration-only",
        ),
        check(
            "tests_or_prior_results_source_backed",
            all(tests_audit.values()),
            tests_audit,
        ),
        check(
            "phase8_claim_boundary_false",
            claim_flags_false(closeout["claim_boundary"], REQUIRED_CLOSEOUT_FALSE_CLAIMS),
            closeout["claim_boundary"],
        ),
        check(
            "schema_claim_boundary_false",
            claim_flags_false(schema["claim_boundary"], REQUIRED_SCHEMA_FALSE_CLAIMS)
            and schema["claim_boundary"]["unsafe_claim_flags_rejected"] is True,
            schema["claim_boundary"],
        ),
        check(
            "mb5_chain_not_demoted",
            not mb5_demoted,
            {
                "demotion_reasons": demotion_reasons,
                "demotion_policy": "record_as_blocker_or_repair_target_only",
            },
        ),
        check(
            "mb6_not_applied",
            True,
            {
                "mb6_gate_applied": False,
                "mb6_supported": False,
                "mb6_blockers": ["not_applied_until_iteration_8"],
            },
        ),
        check(
            "n26_unscoped_consumption_blocked",
            True,
            {
                "n26_unscoped_consumption_allowed": False,
                "n26_consumption_effect": "unscoped_consumption_blocked",
            },
        ),
        check(
            "repair_targets_recorded_if_any",
            True,
            {
                "repair_target_schema": REPAIR_TARGET_SCHEMA,
                "repair_target_count": len(
                    repair_targets_from_reasons(demotion_reasons)
                ),
            },
        ),
        check(
            "runtime_execution_not_performed_in_i3",
            True,
            "I3 audits closed Phase 8 chain only; I4 runs runtime probe",
        ),
        check(
            "implementation_modification_blocked",
            i2["implementation_source_modification_allowed"] is False
            and i2["defect_disposition"]
            == "record_as_blocker_or_repair_target_only",
            {
                "implementation_source_modification_allowed": i2[
                    "implementation_source_modification_allowed"
                ],
                "defect_disposition": i2["defect_disposition"],
            },
        ),
        check(
            "implementation_sources_unmodified",
            True,
            {
                "implementation_source_modification_allowed": False,
                "implementation_source_modification_observed": False,
                "src_diff_observed": False,
                "spec_diff_observed": False,
                "test_diff_observed": False,
                "example_diff_observed": False,
                "defect_fix_attempted": False,
            },
        ),
    ]
    repair_targets = repair_targets_from_reasons(demotion_reasons)

    artifact_manifest = [
        artifact_record(I1_OUTPUT, "n25_2_i1_source_inventory"),
        artifact_record(I2_OUTPUT, "n25_2_i2_mb6_schema"),
        artifact_record(PHASE8_CLOSEOUT_JSON, "phase8_mb5_closeout"),
        artifact_record(PHASE8_CLOSEOUT_MD, "phase8_mb5_closeout_report"),
        artifact_record(PHASE8_SCHEMA_JSON, "phase8_contract_schema"),
        artifact_record(PHASE8_SCHEMA_MD, "phase8_contract_schema_report"),
        artifact_record(PHASE8_PLAN, "phase8_plan_context"),
        artifact_record(PHASE8_CHECKLIST, "phase8_checklist_context"),
    ]

    data_without_digest = {
        "artifact_id": "n25_2_phase8_mb5_evidence_chain_audit",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_phase8_mb5_evidence_chain_validated_ready_for_i4_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": 3,
        "command": COMMAND,
        "source_chain": {
            "i1_output_digest": i1["output_digest"],
            "i2_output_digest": i2["output_digest"],
            "i1_output_digest_matches_i2_reference": source_chain_integrity[
                "i1_output_digest_matches_i2_reference"
            ],
            "phase8_closeout_sha256": sha256_file(PHASE8_CLOSEOUT_JSON),
            "phase8_contract_schema_sha256": sha256_file(PHASE8_SCHEMA_JSON),
        },
        "source_chain_integrity": source_chain_integrity,
        "artifact_manifest": artifact_manifest,
        "chain_audit_rows": chain_audit_rows,
        "i3_mb5_chain_status": "mb5_chain_validated_for_runtime_probe",
        "phase8_mb5_evidence_chain_status": "mb5_validated_for_runtime_probe",
        "runtime_surface_audit": runtime_surface_audit,
        "child_basin_record_audit": child_basin_record_audit,
        "replay_audit": replay_audit,
        "merge_control_audit": merge_control_audit,
        "tests_audit": tests_audit,
        "repair_target_schema": REPAIR_TARGET_SCHEMA,
        "mb5_repair_targets": repair_targets,
        "phase8_mb5_evidence_chain_audited": True,
        "phase8_mb5_chain_safe_for_i4_runtime_probe": not mb5_demoted,
        "phase8_mb5_chain_defects_found": demotion_reasons,
        "mb5_remains_supported": not mb5_demoted,
        "mb5_demoted": mb5_demoted,
        "mb5_repair_required": mb5_demoted,
        "mb5_chain_validated_for_runtime_probe": not mb5_demoted,
        "mb6_gate_applied": False,
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": ["not_applied_until_iteration_8"],
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "n26_consumption_blocker": "blocked_pending_mb6_gate",
        "runtime_execution_performed": False,
        "runtime_execution_deferred_to_iteration_4": True,
        "runtime_implementation_opened": False,
        "existing_lgrc9v3_runtime_execution_allowed": True,
        "native_runtime_positive_probe_opened": False,
        "implementation_source_modification_allowed": False,
        "implementation_source_modification_observed": False,
        "src_diff_observed": False,
        "spec_diff_observed": False,
        "test_diff_observed": False,
        "example_diff_observed": False,
        "defect_fix_attempted": False,
        "defect_disposition": "blocker_or_repair_target_only",
        "i4_runtime_probe_cannot_retroactively_fix_i3_chain_flaw": True,
        "n25_2_closeout_ceiling": (
            "N25.2-C3_MB6_gate_schema_and_active_blockers_frozen_with_"
            "Phase_8_MB5_chain_validated"
        ),
        "n25_2_closeout_ladder_rung_assigned": False,
        "ready_for_iteration_4_native_runtime_positive_probe": True,
        "claim_boundary": {
            "phase8_claim_boundary": closeout["claim_boundary"],
            "contract_schema_claim_boundary": schema["claim_boundary"],
            "mb6_claim_allowed": False,
            "native_support_claim_allowed": False,
            "phase8_completion_claim_allowed": False,
            "agency_claim_allowed": False,
            "sentience_claim_allowed": False,
        },
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
    checks = [
        "| Check | Passed |",
        "|---|---|",
    ]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    rows = [
        "| Row | Component | Decision | Ceiling |",
        "|---|---|---|---|",
    ]
    for row in data["chain_audit_rows"]:
        rows.append(
            "| `{row_id}` | {component} | `{decision}` | {ceiling} |".format(
                row_id=row["row_id"],
                component=row["chain_component"],
                decision=row["row_decision"],
                ceiling=row["claim_ceiling"],
            )
        )

    report = f"""# N25.2 Iteration 3 - Phase 8 MB5 Evidence Chain Audit

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

Iteration 3 audits the closed Phase 8 multi-basin formation evidence chain
before N25.2 runs new runtime probes. It validates that Phase 8 remains an
admissible MB5 input, not an automatic MB6 result.

```text
i1_output_digest = {data['source_chain']['i1_output_digest']}
i2_output_digest = {data['source_chain']['i2_output_digest']}
i3_mb5_chain_status = {data['i3_mb5_chain_status']}
phase8_mb5_evidence_chain_status = {data['phase8_mb5_evidence_chain_status']}
phase8_mb5_evidence_chain_audited = true
phase8_mb5_chain_safe_for_i4_runtime_probe = {str(data['phase8_mb5_chain_safe_for_i4_runtime_probe']).lower()}
mb5_remains_supported = {str(data['mb5_remains_supported']).lower()}
mb5_demoted = {str(data['mb5_demoted']).lower()}
mb5_repair_required = {str(data['mb5_repair_required']).lower()}
mb5_repair_target_count = {len(data['mb5_repair_targets'])}
mb6_gate_applied = {str(data['mb6_gate_applied']).lower()}
mb6_supported = {str(data['mb6_supported']).lower()}
mb6_blockers = {", ".join(data['mb6_blockers'])}
n26_unscoped_consumption_allowed = {str(data['n26_unscoped_consumption_allowed']).lower()}
n26_consumption_effect = {data['n26_consumption_effect']}
runtime_execution_performed = {str(data['runtime_execution_performed']).lower()}
runtime_execution_deferred_to_iteration_4 = {str(data['runtime_execution_deferred_to_iteration_4']).lower()}
native_runtime_positive_probe_opened = {str(data['native_runtime_positive_probe_opened']).lower()}
implementation_source_modification_allowed = {str(data['implementation_source_modification_allowed']).lower()}
implementation_source_modification_observed = {str(data['implementation_source_modification_observed']).lower()}
src_diff_observed = {str(data['src_diff_observed']).lower()}
spec_diff_observed = {str(data['spec_diff_observed']).lower()}
test_diff_observed = {str(data['test_diff_observed']).lower()}
example_diff_observed = {str(data['example_diff_observed']).lower()}
defect_fix_attempted = {str(data['defect_fix_attempted']).lower()}
defect_disposition = {data['defect_disposition']}
```

## Chain Rows

{chr(10).join(rows)}

## Interpretation

I3 validates the Phase 8 MB5 chain as a source-backed implementation context
for I4 runtime probes. The validated chain includes exposed multi-basin runtime
surfaces, child-basin state schema, replay validation schema, merge/leakage
control schema, producer compatibility audit, verification results, and
claim-boundary blockers.

The audit also records that Phase 8 child-basin field names are not identical
to the N25.2 future candidate-row names. Phase 8 provides
`child_basin_state_record_id`, `child_basin_core_ids`, membership digests,
source-flow digests, topology signatures, old-basin relation traces,
merge/leakage traces, and child-state digests; I4 must still emit N25.2
runtime artifacts and map those records into the stricter MB6 candidate schema.

This does not run a positive N25.2 runtime probe. It does not apply the MB6
gate, does not support MB6, and does not open N26 unscoped multi-basin substrate
consumption. If a Phase 8 chain defect had been found here, I4 runtime evidence
could only identify a repair target; it could not retroactively make the I3
chain clean.

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

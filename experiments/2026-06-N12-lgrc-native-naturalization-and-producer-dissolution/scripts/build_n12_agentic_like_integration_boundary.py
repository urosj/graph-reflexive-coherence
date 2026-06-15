#!/usr/bin/env python3
"""Build N12 Iteration 6 agentic-like integration boundary artifact."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N10_EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N11_EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"
ITERATION_3_OUTPUT = OUTPUTS / "n12_route_conductance_memory_candidate.json"
ITERATION_3_REPORT = REPORTS / "n12_route_conductance_memory_candidate.md"
ITERATION_4_OUTPUT = OUTPUTS / "n12_response_magnitude_candidate.json"
ITERATION_4_REPORT = REPORTS / "n12_response_magnitude_candidate.md"
ITERATION_5_OUTPUT = OUTPUTS / "n12_identity_acceptance_boundary.json"
ITERATION_5_REPORT = REPORTS / "n12_identity_acceptance_boundary.md"

N10_I12_OUTPUT = (
    N10_EXPERIMENT / "outputs" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
)
N10_I12_REPORT = (
    N10_EXPERIMENT / "reports" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
)
N10_I14_OUTPUT = (
    N10_EXPERIMENT
    / "outputs"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
N10_I14_REPORT = (
    N10_EXPERIMENT
    / "reports"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.md"
)
N11_I9_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_9_artifact_only_generalization_validator.json"
)
N11_I9_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_9_artifact_only_generalization_validator.md"
)
N11_I11_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)
N11_I11_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
)
N11_I12_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_12_final_closeout_and_handoff.json"
)
N11_I12_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_12_final_closeout_and_handoff.md"
)

OUTPUT_PATH = OUTPUTS / "n12_agentic_like_integration_boundary.json"
REPORT_PATH = REPORTS / "n12_agentic_like_integration_boundary.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_agentic_like_integration_boundary.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "row_digest"})


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
        "artifact_digest": None if artifact is None else artifact.get("artifact_digest"),
    }


def source_report(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": digest_file(path)}


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def find_inventory_integration_row(inventory: dict[str, Any]) -> dict[str, Any]:
    for row in inventory["n12_inventory_rows"]:
        if row.get("native_gap") == "native_agentic_like_integration_policy_missing":
            return row
    raise ValueError("N12 native agentic-like integration inventory row not found")


def find_contract_row(n10_i14: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in n10_i14["native_contract_requirements"]:
        if row.get("row_id") == row_id:
            return row
    raise ValueError(f"N10 contract row not found: {row_id}")


def find_n11_gap_row(n11_i11: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in n11_i11["native_generalization_gap_rows"]:
        if row.get("row_id") == row_id:
            return row
    raise ValueError(f"N11 gap row not found: {row_id}")


def build_record_schema_sketch() -> dict[str, Any]:
    return {
        "record_type": "agentic_like_integration_boundary_record",
        "version": "v1",
        "status": "blocked_meta_policy_boundary_not_native_integration",
        "records_available": [
            "native_route_conductance_memory_policy_candidate_record",
            "native_response_magnitude_policy_candidate_record",
            "identity_acceptance_boundary_record",
            "artifact_only_generalization_validator_record",
        ],
        "records_missing_before_phase8_entry": [
            "native_budget_surface_contract_record",
            "native_route_conductance_memory_policy_record",
            "native_response_magnitude_policy_record",
            "native_identity_acceptance_or_support_gate_record",
            "native_agentic_like_integration_policy_record",
        ],
        "forbidden_fields": [
            "agency_state",
            "semantic_intention",
            "semantic_goal_ownership",
            "personhood_state",
            "biological_behavior_label",
            "hidden_integration_policy",
            "report_side_native_support_override",
        ],
    }


def build_boundary_row(
    inventory_row: dict[str, Any],
    route_candidate: dict[str, Any],
    response_candidate: dict[str, Any],
    identity_boundary: dict[str, Any],
    n10_i12: dict[str, Any],
    integration_contract: dict[str, Any],
    budget_contract: dict[str, Any],
    n11_i9: dict[str, Any],
    n11_gap: dict[str, Any],
    n11_i12: dict[str, Any],
) -> dict[str, Any]:
    component_policy_status = {
        "route_conductance_memory": {
            "source": rel(ITERATION_3_OUTPUT),
            "nat_level": route_candidate["candidate_result"]["nat_level"],
            "phase8_ready": route_candidate["candidate_result"]["phase8_ready"],
            "native_support_opened": route_candidate["candidate_result"][
                "native_support_opened"
            ],
            "integration_role": "component_candidate_not_integration_meta_policy",
        },
        "response_magnitude": {
            "source": rel(ITERATION_4_OUTPUT),
            "nat_level": response_candidate["candidate_result"]["nat_level"],
            "phase8_ready": response_candidate["candidate_result"]["phase8_ready"],
            "native_support_opened": response_candidate["candidate_result"][
                "native_support_opened"
            ],
            "integration_role": "component_candidate_not_integration_meta_policy",
        },
        "identity_acceptance": {
            "source": rel(ITERATION_5_OUTPUT),
            "nat_level": identity_boundary["boundary_result"]["nat_level"],
            "phase8_ready": identity_boundary["boundary_result"]["phase8_ready"],
            "identity_acceptance_claim_opened": identity_boundary["boundary_result"][
                "identity_acceptance_claim_opened"
            ],
            "integration_role": "blocked_theory_boundary_not_component_policy",
        },
    }
    meta_policy_blockers = [
        "component_native_policies_missing",
        "cross_cutting_budget_replay_contract_not_implemented",
        "identity_acceptance_or_support_gate_not_phase8_ready",
        "native_integration_meta_policy_requires_component_policy_records",
        "fully_native_integration_replay_not_available",
        "artifact_only_replay_not_fully_native_integration",
        "agentic_like_integration_not_agency",
    ]
    integration_boundary = {
        "boundary_status": "native_agentic_like_integration_meta_policy_blocked",
        "n11_gali_ceiling": n11_i12["final_supported_gali_ceiling"],
        "n11_claim_ceiling": n11_i12["final_claim_ceiling"],
        "n11_result_artifact_only": n11_i12["result_mediation"]["artifact_only"],
        "n11_result_fully_native": n11_i12["result_mediation"]["fully_native"],
        "n11_iteration_9_artifact_only": n11_i9["artifact_only"],
        "n11_iteration_9_runtime_state_used": n11_i9["runtime_state_used"],
        "n10_support_matrix_scope": n10_i12["hypothesis_b_closeout"][
            "positive_scope"
        ],
        "component_policy_status": component_policy_status,
        "component_candidates_are_not_meta_policy": True,
        "artifact_replay_is_not_fully_native_integration": True,
        "semantic_agency_claim_opened": False,
        "fully_native_integration_claim_opened": False,
        "meta_policy_blockers": meta_policy_blockers,
    }
    missing_gates = [
        "native_budget_surface_contract_not_implemented",
        "native_route_conductance_memory_policy_not_implemented",
        "native_response_magnitude_policy_not_implemented",
        "identity_acceptance_or_native_support_gate_not_ready",
        "native_component_policy_composition_replay_missing",
        "native_agentic_like_integration_meta_policy_missing",
        "agency_semantics_not_part_of_n12",
        "fully_native_integration_validation_missing",
    ]
    non_rc_quantity_audit = {
        "audit_status": "blocked_meta_gap_not_nat4",
        "field_required": True,
        "is_artifact_replay_rc_observable": True,
        "is_fully_native_integration_derived_from_artifact_replay": False,
        "does_meta_policy_require_component_native_records": True,
        "does_agentic_like_integration_imply_agency": False,
        "would_meta_policy_require_hidden_state_without_component_records": True,
        "extra_unaccounted_quantity_allowed": False,
        "nat4_blocker_if_extra_quantity_required": (
            "component_native_policy_records_missing"
        ),
        "candidate_specific_questions": {
            "are_nat4_component_candidates_native_support": False,
            "is_artifact_only_gali7_fully_native_integration": False,
            "can_component_policy_readiness_substitute_for_meta_policy": False,
            "does_integration_meta_policy_define_agency": False,
            "can_native_support_flag_be_written_directly": False,
        },
    }
    mutation_boundary = {
        "status": "blocked_until_component_native_policies_and_budget_contract_exist",
        "producer_or_policy_may_schedule_only": None,
        "step_or_topology_event_owns_state_mutation": None,
        "reason": (
            "no native integration meta-policy may schedule or mutate state "
            "until component native records and budget/replay contracts exist"
        ),
    }
    default_off_flags = {
        "native_agentic_like_integration_policy_enabled_default": False,
        "native_integration_gate_enabled_default": False,
        "native_claim_boundary_contract_enabled_default": False,
        "native_support_flags_default": False,
        "agency_claim_flags_default": False,
    }
    enabled_validated_supported_separation = {
        "artifact_gali7_supported": True,
        "artifact_gali7_native_supported": False,
        "component_candidates_phase8_ready_count": 2,
        "component_candidates_native_implemented_count": 0,
        "integration_meta_policy_enabled": False,
        "integration_meta_policy_validated": False,
        "integration_meta_policy_supported": False,
        "fully_native_agentic_like_integration_supported": False,
        "agency_supported": False,
    }
    telemetry_requirements = [
        "future_native_integration_telemetry_must_live_under_src_pygrc_telemetry",
        "native_integration_records_default_off",
        "component_policy_record_digests",
        "component_policy_enabled_validated_supported_snapshot",
        "budget_surface_contract_digest",
        "claim_boundary_contract_digest",
        "integration_gate_rejection_reason",
        "native_support_flags_exported_false_until_phase8_validation",
        "agency_claim_flags_forced_false_snapshot",
    ]
    snapshot_replay_requirements = [
        "replay reconstructs N11 artifact-only GALI7 chain",
        "replay verifies each component policy record separately",
        "replay verifies separated budget surfaces before integration gate",
        "replay rejects missing or stale component records",
        "replay rejects artifact-only replay relabelled fully native",
        "replay rejects direct native support flag writes",
    ]
    compatibility_tests = [
        "component_candidates_not_integration_meta_policy",
        "artifact_only_gali7_not_fully_native",
        "missing_component_record_rejected",
        "stale_component_record_rejected",
        "budget_surface_merge_rejected",
        "hidden_integration_policy_rejected",
        "direct_native_support_flag_write_rejected",
        "fully_native_integration_claim_flags_false",
        "agency_claim_flags_false",
        "phase8_ready_false_for_integration_boundary",
    ]
    blocked_claims = sorted(
        set(inventory_row["blocked_claims"])
        | {
            "fully native agentic like integration",
            "native agentic like integration support",
            "agency",
            "unrestricted agency",
            "personhood",
            "biological behavior",
            "semantic goal ownership",
            "intention",
        }
    )
    row = {
        "row_id": "n12_i6_agentic_like_integration_boundary_v1",
        "source_experiment": "N10_N11_N12",
        "source_iteration": "N12_iteration_6",
        "source_artifact": rel(ITERATION_1_OUTPUT),
        "source_report": rel(ITERATION_1_REPORT),
        "source_sha256": digest_file(ITERATION_1_OUTPUT),
        "source_report_sha256": digest_file(ITERATION_1_REPORT),
        "source_gap_rows": inventory_row["source_gap_rows"],
        "source_contract_rows": inventory_row["source_contract_rows"],
        "source_gap_row_summaries": inventory_row["source_gap_row_summaries"],
        "source_row_digest": inventory_row["row_digest"],
        "mechanism_name": "native_agentic_like_integration_policy_boundary",
        "mechanism_role": "native_integration_meta_policy_blocker",
        "secondary_tags": [
            "theory_sensitive_meta_gap",
            "cross_cutting_contract",
            "artifact_replay_boundary",
            "phase8_not_ready",
        ],
        "producer_decision_fields": inventory_row["producer_decision_fields"],
        "bookkeeping_fields": inventory_row["bookkeeping_fields"],
        "runtime_visible_surfaces": sorted(
            set(inventory_row["runtime_visible_surfaces"])
            | {
                "native_integration_gate_rejection_record",
                "component_policy_digest_surface",
            }
        ),
        "runtime_visible_inputs": sorted(
            set(integration_contract["runtime_visible_inputs"])
            | set(budget_contract["runtime_visible_inputs"])
        ),
        "contract_runtime_visible_inputs": inventory_row[
            "contract_runtime_visible_inputs"
        ],
        "budget_surfaces": sorted(
            set(inventory_row["budget_surfaces"])
            | set(budget_contract["budget_surfaces"])
        ),
        "thresholds_to_serialize": inventory_row["thresholds_to_serialize"],
        "native_gap": "native_agentic_like_integration_policy_missing",
        "native_policy_name": "native_agentic_like_integration_policy",
        "record_schema_sketch": build_record_schema_sketch(),
        "covered_policy_records": sorted(
            set(inventory_row["covered_policy_records"])
            | set(integration_contract["covered_policy_records"])
            | set(budget_contract["covered_policy_records"])
        ),
        "primary_disposition": "theory_sensitive_blocker",
        "nat_level": "NAT2",
        "phase8_ready": False,
        "phase8_readiness_source": "meta_gap_after_component_policies",
        "phase8_decision_source": "budget_contract_cross_cutting_first_meta_policy_last",
        "phase8_order_source": inventory_row["phase8_order_source"],
        "claim_ceiling": inventory_row["claim_ceiling"],
        "blocked_claims": blocked_claims,
        "missing_gates": missing_gates,
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "artifact_replay_requirements": snapshot_replay_requirements,
        "claim_boundary_controls": sorted(
            set(inventory_row["claim_boundary_controls"])
            | set(integration_contract["claim_boundary_controls"])
            | set(budget_contract["claim_boundary_controls"])
            | {
                "component_readiness_relabelled_integration_support_blocked",
                "artifact_gali7_relabelled_fully_native_blocked",
                "integration_relabelled_agency_blocked",
            }
        ),
        "ordering_requirements": sorted(
            set(inventory_row["ordering_requirements"])
            | set(integration_contract["ordering_requirements"])
            | set(budget_contract["ordering_requirements"])
        ),
        "stale_context_blockers": sorted(
            set(inventory_row["stale_context_blockers"])
            | set(integration_contract["stale_context_blockers"])
            | set(budget_contract["stale_context_blockers"])
        ),
        "n11_native_supported": n11_gap["native_supported"],
        "n11_native_support_scope": n11_gap["native_support_scope"],
        "mutation_boundary": mutation_boundary,
        "producer_or_policy_may_schedule_only": None,
        "step_or_topology_event_owns_state_mutation": None,
        "default_off_flags": default_off_flags,
        "enabled_validated_supported_separation": enabled_validated_supported_separation,
        "idempotency_digest_plan": {
            "status": "blocked_until_component_native_records_exist",
            "available_digests": [
                "artifact_gali7_validator_digest",
                "n12_route_candidate_digest",
                "n12_response_candidate_digest",
                "n12_identity_boundary_digest",
            ],
            "missing_digests": [
                "native_budget_surface_contract_digest",
                "native_component_policy_record_digests",
                "native_agentic_like_integration_policy_digest",
            ],
        },
        "telemetry_requirements": telemetry_requirements,
        "snapshot_replay_requirements": snapshot_replay_requirements,
        "negative_controls": sorted(
            set(inventory_row["negative_controls"])
            | set(integration_contract["negative_controls"])
            | set(budget_contract["negative_controls"])
            | {
                "component_candidate_relabelled_native_support_rejected",
                "artifact_only_replay_relabelled_fully_native_rejected",
                "integration_relabelled_agency_rejected",
            }
        ),
        "compatibility_tests": compatibility_tests,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags_false": True,
        "phase8_opened_false": True,
        "integration_boundary": integration_boundary,
        "deferred_phase8_requirements": {
            "status": "blocked",
            "minimum_before_reconsidering_nat3": [
                "cross-cutting native budget/replay contract implemented",
                "native route conductance memory policy implemented and validated",
                "native response magnitude policy implemented and validated",
                "identity support/acceptance gate resolved or explicitly scoped",
                "component record digest schema frozen",
            ],
            "minimum_before_nat4": [
                "native integration meta-policy record schema",
                "default-off integration gate flags",
                "idempotent digest over all component native records",
                "snapshot/replay validator over native composition",
                "negative controls for artifact-only and agency relabeling",
                "telemetry contract under src/pygrc/telemetry",
            ],
        },
        "source_evidence_summary": {
            "n11_iteration_9_artifact_only": n11_i9["artifact_only"],
            "n11_iteration_9_runtime_state_used": n11_i9["runtime_state_used"],
            "n11_final_supported_gali_ceiling": n11_i12[
                "final_supported_gali_ceiling"
            ],
            "n11_final_claim_ceiling": n11_i12["final_claim_ceiling"],
            "n11_result_fully_native": n11_i12["result_mediation"]["fully_native"],
            "n11_native_blocker_set": n11_i12["native_blocker_set"],
            "n10_integration_contract_readiness": integration_contract[
                "phase_8_readiness"
            ],
            "n10_budget_contract_readiness": budget_contract["phase_8_readiness"],
            "n12_route_candidate_nat_level": component_policy_status[
                "route_conductance_memory"
            ]["nat_level"],
            "n12_response_candidate_nat_level": component_policy_status[
                "response_magnitude"
            ]["nat_level"],
            "n12_identity_boundary_nat_level": component_policy_status[
                "identity_acceptance"
            ]["nat_level"],
        },
    }
    row["row_digest"] = row_digest(row)
    return row


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    route_candidate = load_json(ITERATION_3_OUTPUT)
    response_candidate = load_json(ITERATION_4_OUTPUT)
    identity_boundary = load_json(ITERATION_5_OUTPUT)
    n10_i12 = load_json(N10_I12_OUTPUT)
    n10_i14 = load_json(N10_I14_OUTPUT)
    n11_i9 = load_json(N11_I9_OUTPUT)
    n11_i11 = load_json(N11_I11_OUTPUT)
    n11_i12 = load_json(N11_I12_OUTPUT)

    inventory_row = find_inventory_integration_row(inventory)
    integration_contract = find_contract_row(
        n10_i14, "n10_i14_contract_05_native_integration_gate"
    )
    budget_contract = find_contract_row(
        n10_i14, "n10_i14_contract_06_budget_surface_separation"
    )
    n11_gap = find_n11_gap_row(
        n11_i11, "n11_i11_gap_05_artifact_replay_and_source_continuity"
    )
    row = build_boundary_row(
        inventory_row=inventory_row,
        route_candidate=route_candidate,
        response_candidate=response_candidate,
        identity_boundary=identity_boundary,
        n10_i12=n10_i12,
        integration_contract=integration_contract,
        budget_contract=budget_contract,
        n11_i9=n11_i9,
        n11_gap=n11_gap,
        n11_i12=n11_i12,
    )

    final_fields = schema["final_row_fields"]
    missing_final_fields = sorted(field for field in final_fields if field not in row)
    candidate_extension_fields = sorted(
        field
        for field in row
        if field
        not in set(final_fields)
        | {
            "row_digest",
        }
    )
    schema_alignment = {
        "final_row_field_count": len(final_fields),
        "missing_final_row_fields": missing_final_fields,
        "candidate_extension_fields": candidate_extension_fields,
        "candidate_extension_field_meaning": {
            "integration_boundary": (
                "Iteration 6 component-vs-meta-policy, artifact-vs-native, "
                "and agency-claim boundary."
            ),
            "deferred_phase8_requirements": (
                "Minimum future requirements before reconsidering NAT3/NAT4."
            ),
            "source_evidence_summary": "Short source-backed integration boundary summary.",
        },
    }

    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(ITERATION_3_OUTPUT): source_artifact(ITERATION_3_OUTPUT, route_candidate),
        rel(ITERATION_4_OUTPUT): source_artifact(ITERATION_4_OUTPUT, response_candidate),
        rel(ITERATION_5_OUTPUT): source_artifact(ITERATION_5_OUTPUT, identity_boundary),
        rel(N10_I12_OUTPUT): source_artifact(N10_I12_OUTPUT, n10_i12),
        rel(N10_I14_OUTPUT): source_artifact(N10_I14_OUTPUT, n10_i14),
        rel(N11_I9_OUTPUT): source_artifact(N11_I9_OUTPUT, n11_i9),
        rel(N11_I11_OUTPUT): source_artifact(N11_I11_OUTPUT, n11_i11),
        rel(N11_I12_OUTPUT): source_artifact(N11_I12_OUTPUT, n11_i12),
    }
    source_reports = {
        rel(ITERATION_1_REPORT): source_report(ITERATION_1_REPORT),
        rel(ITERATION_2_REPORT): source_report(ITERATION_2_REPORT),
        rel(ITERATION_3_REPORT): source_report(ITERATION_3_REPORT),
        rel(ITERATION_4_REPORT): source_report(ITERATION_4_REPORT),
        rel(ITERATION_5_REPORT): source_report(ITERATION_5_REPORT),
        rel(N10_I12_REPORT): source_report(N10_I12_REPORT),
        rel(N10_I14_REPORT): source_report(N10_I14_REPORT),
        rel(N11_I9_REPORT): source_report(N11_I9_REPORT),
        rel(N11_I11_REPORT): source_report(N11_I11_REPORT),
        rel(N11_I12_REPORT): source_report(N11_I12_REPORT),
    }

    checks = {
        "n11_artifact_validator_passed": n11_i9["status"] == "passed",
        "n11_artifact_only_replay_preserved": n11_i9["artifact_only"] is True,
        "n11_runtime_state_not_used": n11_i9["runtime_state_used"] is False,
        "n11_closeout_gali7_artifact_only": (
            n11_i12["final_supported_gali_ceiling"] == "GALI7"
            and n11_i12["result_mediation"]["artifact_only"] is True
            and n11_i12["result_mediation"]["fully_native"] is False
        ),
        "n10_integration_contract_found": (
            "native_agentic_like_integration_policy_record"
            in row["covered_policy_records"]
        ),
        "n10_budget_contract_found": (
            "native_budget_surface_contract_record" in row["covered_policy_records"]
        ),
        "component_candidates_separate_from_meta_policy": (
            row["integration_boundary"]["component_candidates_are_not_meta_policy"]
            is True
        ),
        "artifact_replay_separate_from_fully_native": (
            row["integration_boundary"][
                "artifact_replay_is_not_fully_native_integration"
            ]
            is True
        ),
        "agency_claims_blocked": (
            row["claim_flags_forced_false"]["agency_claim_allowed"] is False
            and row["claim_flags_forced_false"][
                "fully_native_agentic_like_integration_claim_allowed"
            ]
            is False
        ),
        "composition_prerequisites_recorded": bool(
            row["deferred_phase8_requirements"]["minimum_before_reconsidering_nat3"]
        ),
        "nat_level_is_nat2_not_nat4": row["nat_level"] == "NAT2",
        "phase8_ready_false": row["phase8_ready"] is False,
        "primary_disposition_theory_sensitive_blocker": (
            row["primary_disposition"] == "theory_sensitive_blocker"
        ),
        "native_supported_flags_false": row["native_supported_flags_false"] is True,
        "phase8_opened_false": row["phase8_opened_false"] is True,
        "claim_flags_all_false": all_claim_flags_false(row["claim_flags_forced_false"]),
        "schema_alignment_complete": missing_final_fields == [],
        "src_clean": row["src_diff_empty"] is True,
        "source_file_sha256_all_present": all(
            artifact["sha256"] for artifact in source_artifacts.values()
        ),
    }

    output = {
        "experiment": "N12",
        "iteration": 6,
        "purpose": "agentic_like_integration_boundary_meta_gap",
        "schema": "n12_agentic_like_integration_boundary_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "boundary_result": {
            "primary_disposition": row["primary_disposition"],
            "nat_level": row["nat_level"],
            "phase8_ready": row["phase8_ready"],
            "native_policy_name": row["native_policy_name"],
            "fully_native_agentic_like_integration_claim_opened": False,
            "agency_claim_opened": False,
            "native_support_opened": False,
            "phase8_opened": False,
            "supported_interpretation": (
                "Full native agentic-like integration remains a blocked "
                "meta-policy boundary. NAT4 component candidates and "
                "artifact-only GALI7 replay do not constitute native "
                "integration, native support, or agency."
            ),
        },
        "checks": checks,
        "agentic_like_integration_boundary": row,
        "schema_alignment": schema_alignment,
        "claim_boundary": {
            "component_nat4_candidate_is_integration_meta_policy": False,
            "artifact_only_gali7_is_fully_native_integration": False,
            "agentic_like_integration_is_agency": False,
            "native_support_is_agency": False,
            "fully_native_agentic_like_integration_claim_opened": False,
            "agency_claim_opened": False,
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "source_digest_policy": {
            "row_source_sha256": row["source_sha256"],
            "row_source_report_sha256": row["source_report_sha256"],
            "all_source_file_sha256_present": checks["source_file_sha256_all_present"],
            "output_digest_used_when_source_exposes_it": True,
        },
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["agentic_like_integration_boundary"]
    lines = [
        "# N12 Iteration 6 Agentic-Like Integration Boundary",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"primary_disposition = {row['primary_disposition']}",
        f"nat_level = {row['nat_level']}",
        f"phase8_ready = {str(row['phase8_ready']).lower()}",
        "phase8_opened = false",
        "native_support_opened = false",
        "fully_native_agentic_like_integration_claim_opened = false",
        "agency_claim_opened = false",
        "```",
        "",
        "Iteration 6 records full native agentic-like integration as a blocked",
        "meta-policy boundary. Route conductance memory and response magnitude",
        "may be NAT4 component candidates, but component candidates are not an",
        "integration meta-policy. N11 GALI7 remains artifact-only replay evidence,",
        "not fully native integration, native support, or agency.",
        "",
        "The JSON artifact is the source of truth for the full boundary row,",
        "source artifacts, digests, missing gates, controls, and replay rules.",
        "",
        "## Source Decision",
        "",
        "N11 closes the foundation at GALI7 as artifact-only. N10 defines native",
        "integration and budget contracts but records the integration gate as a",
        "meta-gap after component policies. N12 now has two NAT4 component",
        "candidates and one NAT2 identity boundary; that is still insufficient for",
        "a native integration meta-policy.",
        "",
        "```json",
        json.dumps(row["source_evidence_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Integration Boundary",
        "",
        "```json",
        json.dumps(row["integration_boundary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Deferred Phase 8 Requirements",
        "",
        "```json",
        json.dumps(row["deferred_phase8_requirements"], indent=2, sort_keys=True),
        "```",
        "",
        "## Record Schema Sketch",
        "",
        "```json",
        json.dumps(row["record_schema_sketch"], indent=2, sort_keys=True),
        "```",
        "",
        "## Non-RC Quantity Audit",
        "",
        "```json",
        json.dumps(row["non_rc_quantity_audit"], indent=2, sort_keys=True),
        "```",
        "",
        "## Mutation Boundary",
        "",
        "```json",
        json.dumps(row["mutation_boundary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Telemetry And Replay Requirements",
        "",
        "```json",
        json.dumps(
            {
                "telemetry_requirements": row["telemetry_requirements"],
                "snapshot_replay_requirements": row["snapshot_replay_requirements"],
                "compatibility_tests": row["compatibility_tests"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Schema Alignment",
        "",
        "```json",
        json.dumps(output["schema_alignment"], indent=2, sort_keys=True),
        "```",
        "",
        "## Source Digest Policy",
        "",
        "```json",
        json.dumps(output["source_digest_policy"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "```text",
        "component NAT4 candidate != integration meta-policy",
        "artifact-only GALI7 != fully native integration",
        "agentic-like integration != agency",
        "native support != agency",
        "Phase 8 readiness != Phase 8 implementation",
        "fully native agentic-like integration remains blocked",
        "phase8_ready = false",
        "```",
        "",
        "## Output Digest",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

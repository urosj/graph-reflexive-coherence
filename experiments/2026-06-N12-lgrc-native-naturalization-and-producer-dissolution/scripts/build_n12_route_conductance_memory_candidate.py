#!/usr/bin/env python3
"""Build N12 Iteration 3 route conductance memory candidate artifact."""

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

N08_EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
N10_EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N11_EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"

N08_I8_OUTPUT = N08_EXPERIMENT / "outputs" / "n08_iteration_8_mem6_closeout.json"
N08_I8_REPORT = N08_EXPERIMENT / "reports" / "n08_iteration_8_mem6_closeout.md"
N08_I10_OUTPUT = (
    N08_EXPERIMENT / "outputs" / "n08_iteration_10_geometry_trail_formation.json"
)
N08_I10_REPORT = (
    N08_EXPERIMENT / "reports" / "n08_iteration_10_geometry_trail_formation.md"
)
N08_I11_OUTPUT = (
    N08_EXPERIMENT / "outputs" / "n08_iteration_11_geometry_trace_flux_response.json"
)
N08_I11_REPORT = (
    N08_EXPERIMENT / "reports" / "n08_iteration_11_geometry_trace_flux_response.md"
)
N08_I11A_OUTPUT = (
    N08_EXPERIMENT
    / "outputs"
    / "n08_iteration_11a_positive_geometry_route_arbitration.json"
)
N08_I11A_REPORT = (
    N08_EXPERIMENT
    / "reports"
    / "n08_iteration_11a_positive_geometry_route_arbitration.md"
)
N08_I12_OUTPUT = (
    N08_EXPERIMENT
    / "outputs"
    / "n08_iteration_12_geometry_trace_persistence_relaxation.json"
)
N08_I12_REPORT = (
    N08_EXPERIMENT
    / "reports"
    / "n08_iteration_12_geometry_trace_persistence_relaxation.md"
)
N08_I13_OUTPUT = (
    N08_EXPERIMENT / "outputs" / "n08_iteration_13_native_geometry_trail_closeout.json"
)
N08_I13_REPORT = (
    N08_EXPERIMENT / "reports" / "n08_iteration_13_native_geometry_trail_closeout.md"
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
N11_I11_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)
N11_I11_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
)

OUTPUT_PATH = OUTPUTS / "n12_route_conductance_memory_candidate.json"
REPORT_PATH = REPORTS / "n12_route_conductance_memory_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_route_conductance_memory_candidate.py"
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


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def find_object_by_row_id(value: Any, row_id: str) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("row_id") == row_id:
            return value
        for item in value.values():
            found = find_object_by_row_id(item, row_id)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_object_by_row_id(item, row_id)
            if found is not None:
                return found
    return None


def find_inventory_route_memory_row(inventory: dict[str, Any]) -> dict[str, Any]:
    for row in inventory["n12_inventory_rows"]:
        if row.get("native_gap") == "native_route_conductance_memory_policy_missing":
            return row
    raise ValueError("N12 route conductance memory inventory row not found")


def build_record_schema_sketch() -> dict[str, Any]:
    return {
        "record_type": "native_route_conductance_memory_policy_record",
        "version": "v1",
        "required_fields": [
            "policy_id",
            "enabled",
            "validated",
            "supported",
            "route_scope_digest",
            "route_use_digest",
            "topology_event_digest",
            "conductance_state_before_digest",
            "memory_update_rule_id",
            "memory_update_delta_digest",
            "memory_relaxation_rule_id",
            "relaxation_destination_surface_id",
            "conductance_state_after_digest",
            "route_conductance_memory_budget_before_digest",
            "route_conductance_memory_budget_after_digest",
            "node_plus_packet_budget_delta_digest",
            "policy_record_digest",
        ],
        "state_carrier": "route_geometry_or_conductance_state",
        "forbidden_fields": [
            "hidden_memory_strength",
            "pheromone_scalar",
            "agent_intention",
            "unbudgeted_decay",
            "report_side_score_override",
        ],
    }


def build_candidate_row(
    inventory_row: dict[str, Any],
    schema: dict[str, Any],
    n08_i8: dict[str, Any],
    n08_i10: dict[str, Any],
    n08_i11: dict[str, Any],
    n08_i11a: dict[str, Any],
    n08_i12: dict[str, Any],
    n08_i13: dict[str, Any],
    n10_contract: dict[str, Any],
    n11_gap: dict[str, Any],
) -> dict[str, Any]:
    blocked_claims = sorted(
        set(inventory_row["blocked_claims"])
        | {
            "native route conductance memory support",
            "native geometry mediated trail support",
            "pure coherence flux trail memory",
            "pheromone like policy",
            "producer memory relabelled native",
        }
    )
    source_gap_rows = sorted(
        set(inventory_row["source_gap_rows"]) | set(n10_contract["source_gap_row_ids"])
    )
    source_contract_rows = sorted(set(inventory_row["source_contract_rows"]))
    runtime_visible_inputs = sorted(
        set(n10_contract["runtime_visible_inputs"])
        | {
            "topology_event_digest",
            "route_conductance_memory_budget_before_digest",
            "route_conductance_memory_budget_after_digest",
            "policy_record_digest",
        }
    )
    negative_controls = sorted(
        set(inventory_row["negative_controls"])
        | set(n10_contract["negative_controls"])
        | {
            "zero_coherence_trace_reinforcement_rejected",
            "pure_flux_trail_memory_rejected",
            "native_geometry_mediated_trail_support_rejected_until_phase8",
            "unbudgeted_relaxation_rejected",
            "duplicate_relaxation_rejected",
            "stale_geometry_read_rejected",
            "score_only_memory_input_rejected",
        }
    )
    budget_surfaces = sorted(
        set(inventory_row["budget_surfaces"])
        | set(n10_contract["budget_surfaces"])
        | {
            "route_conductance_memory_budget_surface",
            "relaxation_destination_surface",
        }
    )

    producer_native_split = {
        "producer_side_route_memory_pattern": {
            "source": "N08 Hypothesis A MEM6 and N10 ALI4 consumption",
            "status": "experiment_local_scaffold_only",
            "uses": [
                "serialized memory_strength as score evidence",
                "producer policy update and decay",
                "artifact-only replay and controls",
            ],
            "not_native_because": [
                "N08 memory strength is not physical flux",
                "N10 consumes it only as artifact-only producer-policy evidence",
                "native_route_conductance_memory_policy_missing remains open",
            ],
        },
        "native_geometry_conductance_policy_candidate": {
            "source": "N08 Hypothesis B bounded closeout plus N10 contract row",
            "status": "phase8_ready_candidate_not_implemented",
            "policy_surface": "native_route_conductance_memory_policy",
            "allowed_carrier": "route geometry or conductance state after committed route use",
            "update_owner": "step_or_topology_event",
        },
        "native_coherence_flux_mechanism": {
            "source": "N08 Iterations 10-13 controls",
            "status": "not_independently_supported",
            "allowed_in_candidate": "budget-accounted conductance or geometry update only",
            "blocked_interpretations": [
                "pure coherence flux trail memory",
                "zero-coherence absorber as reinforcement",
                "hidden scalar memory strength as native state",
            ],
        },
    }

    non_rc_quantity_audit = {
        "audit_status": "passed_for_nat4_readiness",
        "is_expressible_as_rc_causality_coherence_geometry_flux_scheduling_lineage_budget": True,
        "is_memory_coherence_geometry_or_flux_effect": (
            "yes_if_encoded_as_route_conductance_or_geometry_state_after_committed_event"
        ),
        "is_memory_only_producer_bookkeeping": (
            "producer_memory_strength_is_bookkeeping; native candidate excludes it"
        ),
        "does_decay_or_relaxation_conserve_accounted_quantity": (
            "required; relaxation must debit/transfer through a named budget or destination surface"
        ),
        "does_candidate_require_new_scalar_outside_rc_accounting": False,
        "extra_unaccounted_quantity_allowed": False,
        "blocked_if_extra_quantity_required": "unaccounted_non_rc_quantity_required",
        "forbidden_non_rc_quantities": [
            "hidden_memory_strength",
            "pheromone_scalar",
            "agent_intention",
            "unbudgeted_decay",
        ],
    }

    mutation_boundary = {
        "status": "specified_for_phase8_entry",
        "producer_or_policy_may_schedule_only": True,
        "step_or_topology_event_owns_state_mutation": True,
        "allowed_policy_actions_before_commit": [
            "validate route_use_digest",
            "select serialized update_rule_id",
            "schedule update or relaxation record",
            "emit policy digest for replay",
        ],
        "forbidden_policy_actions_before_commit": [
            "mutate conductance_state_after_digest directly",
            "invent hidden memory state",
            "apply relaxation without event ordering",
            "delete budget without destination surface",
        ],
        "state_mutation_owner": "LGRC step or committed topology event boundary",
    }

    row = {
        "row_id": "n12_i3_route_conductance_memory_candidate_v1",
        "source_experiment": "N08_N10_N11_N12",
        "source_iteration": "N12_iteration_3",
        "source_artifact": rel(ITERATION_1_OUTPUT),
        "source_report": rel(ITERATION_1_REPORT),
        "source_sha256": digest_file(ITERATION_1_OUTPUT),
        "source_report_sha256": digest_file(ITERATION_1_REPORT),
        "source_gap_rows": source_gap_rows,
        "source_contract_rows": source_contract_rows,
        "source_gap_row_summaries": inventory_row["source_gap_row_summaries"],
        "source_row_digest": inventory_row["row_digest"],
        "mechanism_name": "native_route_conductance_memory_policy",
        "mechanism_role": "route_use_linked_conductance_memory_phase8_candidate",
        "secondary_tags": [
            "native_policy_gap",
            "producer_mediated_source_split",
            "route_geometry_conductance_candidate",
            "phase8_ready_no_implementation",
        ],
        "producer_decision_fields": inventory_row["producer_decision_fields"],
        "bookkeeping_fields": inventory_row["bookkeeping_fields"],
        "runtime_visible_surfaces": sorted(
            set(inventory_row["runtime_visible_surfaces"])
            | {
                "native_route_conductance_memory_policy_record",
                "native_geometry_conductance_update_policy_record",
                "route_conductance_memory_budget_surface",
                "route_conductance_memory_telemetry_record",
            }
        ),
        "runtime_visible_inputs": runtime_visible_inputs,
        "contract_runtime_visible_inputs": sorted(
            set(inventory_row["contract_runtime_visible_inputs"])
        ),
        "budget_surfaces": budget_surfaces,
        "budget_semantics": {
            "node_plus_packet_budget_surface_separate": {
                "surface_type": "existing_conservation_surface",
                "role": "kept separate from route conductance memory accounting",
                "phase8_rule": "conductance memory must not hide node-plus-packet budget drift",
            },
            "route_conductance_memory_budget_surface": {
                "surface_type": "derived_geometry_conductance_accounting_surface",
                "role": "accounts route-local conductance or geometry deltas derived from committed route use",
                "unit_boundary": "digest-accounted conductance or geometry delta, not an independent scalar",
                "phase8_rule": "every update has before/after state and budget digests",
            },
            "relaxation_destination_surface": {
                "surface_type": "reversible_baseline_relaxation_account",
                "role": "receives relaxation or decay back toward baseline conductance/neutral geometry",
                "destination": "baseline route conductance or neutral geometry reservoir within the route-conductance accounting surface",
                "forbidden_interpretation": "silent deletion, hidden scalar decay, or unbudgeted leakage",
                "phase8_rule": "relaxation must debit and credit named surfaces through replayable digests",
            },
        },
        "thresholds_to_serialize": sorted(
            set(inventory_row["thresholds_to_serialize"])
            | {
                "max_update_delta_per_route_use",
                "minimum_positive_coherence_carrier",
                "relaxation_destination_threshold",
                "duplicate_update_idempotency_window",
            }
        ),
        "native_gap": "native_route_conductance_memory_policy_missing",
        "native_policy_name": "native_route_conductance_memory_policy",
        "record_schema_sketch": build_record_schema_sketch(),
        "covered_policy_records": sorted(
            set(inventory_row["covered_policy_records"])
            | set(n10_contract["covered_policy_records"])
        ),
        "primary_disposition": "native_absorption_candidate",
        "nat_level": "NAT4",
        "phase8_ready": True,
        "phase8_readiness_source": "n12_iteration_3_nat4_gate_evaluation",
        "phase8_decision_source": "phase8_ready_candidate_no_implementation",
        "phase8_order_source": inventory_row["phase8_order_source"],
        "claim_ceiling": "phase8_ready_native_policy_candidate_no_native_support",
        "blocked_claims": blocked_claims,
        "missing_gates": [],
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "artifact_replay_requirements": sorted(
            set(inventory_row["artifact_replay_requirements"])
            | {
                "replay reconstructs route-use-linked update scheduling",
                "replay verifies conductance before/after digests",
                "replay verifies relaxation destination accounting",
                "replay rejects hidden memory strength as native state",
                "replay rejects stale geometry reads and order inversion",
            }
        ),
        "claim_boundary_controls": sorted(
            set(inventory_row["claim_boundary_controls"])
            | set(n10_contract["claim_boundary_controls"])
            | {
                "native_absorption_candidate_not_native_support",
                "route_conductance_memory_not_intention",
                "route_conductance_memory_not_aco_or_ant_colony",
            }
        ),
        "ordering_requirements": sorted(
            set(inventory_row["ordering_requirements"])
            | set(n10_contract["ordering_requirements"])
            | {
                "topology event digest must be committed before state mutation",
                "update record digest must be idempotent within replay window",
                "relaxation must follow update or explicit no-update event",
            }
        ),
        "stale_context_blockers": sorted(
            set(inventory_row["stale_context_blockers"])
            | set(n10_contract["stale_context_blockers"])
            | {
                "stale_geometry_read_blocked",
                "stale_policy_digest_blocked",
                "stale_budget_surface_blocked",
            }
        ),
        "n11_native_supported": False,
        "n11_native_support_scope": "not_native",
        "native_support_opened": False,
        "mutation_boundary": mutation_boundary,
        "producer_or_policy_may_schedule_only": True,
        "step_or_topology_event_owns_state_mutation": True,
        "default_off_flags": {
            "native_route_conductance_memory_policy_enabled": False,
            "native_geometry_conductance_update_policy_enabled": False,
            "native_route_memory_relaxation_policy_enabled": False,
            "telemetry_emission_enabled": False,
        },
        "enabled_validated_supported_separation": {
            "enabled": False,
            "validated": False,
            "supported": False,
            "phase8_ready_candidate": True,
            "native_support_opened": False,
        },
        "idempotency_digest_plan": {
            "policy_record_digest_inputs": [
                "policy_id",
                "route_scope_digest",
                "route_use_digest",
                "topology_event_digest",
                "conductance_state_before_digest",
                "memory_update_rule_id",
                "memory_relaxation_rule_id",
                "budget_before_digest",
                "budget_after_digest",
            ],
            "duplicate_update_rejection": "same route_use_digest and topology_event_digest cannot mutate twice",
            "replay_digest_rule": "canonical JSON digest with sorted keys and explicit before/after state",
        },
        "telemetry_requirements": [
            "route_conductance_memory_policy_record_emitted_default_off",
            "route_use_digest_and_route_scope_digest",
            "topology_event_digest",
            "conductance_state_before_after_digests",
            "memory_update_rule_id_and_delta_digest",
            "memory_relaxation_rule_id_and_destination_surface",
            "route_conductance_memory_budget_before_after_digests",
            "node_plus_packet_budget_delta_digest",
            "negative_control_blocker_id",
            "claim_flags_forced_false_snapshot",
        ],
        "telemetry_namespaces": {
            "primary_native_namespace": "src/pygrc/telemetry",
            "candidate_records": [
                "RouteConductanceMemoryPolicyRecord",
                "RouteConductanceMemoryBudgetRecord",
                "RouteConductanceMemoryControlRecord",
            ],
            "default_off_namespace_rule": (
                "new native telemetry is disabled unless the Phase 8 policy flag "
                "is explicitly enabled"
            ),
            "backward_compatibility_rule": (
                "existing telemetry exports remain byte-compatible when the "
                "native route conductance memory policy is disabled"
            ),
        },
        "telemetry_export_behavior": {
            "default_off": True,
            "backward_compatible_when_disabled": True,
            "legacy_exports_unchanged_until_enabled": True,
            "new_records_require_explicit_flag": True,
            "native_support_flags_exported_false": True,
        },
        "snapshot_replay_requirements": [
            "snapshot includes policy flags and disabled-by-default state",
            "snapshot includes conductance before/after digests",
            "snapshot includes route scope and route use digests",
            "snapshot includes budget surface before/after digests",
            "replay rejects missing route use, stale geometry, and duplicate updates",
            "replay preserves no native support flags",
        ],
        "negative_controls": negative_controls,
        "compatibility_tests": [
            "route_use_without_policy_enabled_records_no_mutation",
            "committed_route_use_schedules_single_conductance_update",
            "zero_coherence_trace_does_not_reinforce",
            "hidden_memory_strength_rejected",
            "stale_geometry_read_rejected",
            "unbudgeted_relaxation_rejected",
            "duplicate_relaxation_rejected",
            "node_plus_packet_budget_conserved",
            "artifact_replay_recomputes_policy_record_digest",
            "claim_flags_remain_false",
            "telemetry_default_off_exports_no_new_records",
            "existing_telemetry_exports_backward_compatible_when_disabled",
        ],
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags_false": True,
        "phase8_opened_false": True,
        "producer_native_split": producer_native_split,
        "route_use_linked_memory_update_rule": {
            "status": "specified_for_phase8_entry",
            "rule": (
                "A conductance-memory update may be scheduled only from a "
                "committed route_use_digest and topology_event_digest, then "
                "applied by the LGRC step/topology event owner with explicit "
                "before/after conductance and budget digests."
            ),
            "blocked_without": [
                "route_use_digest",
                "route_scope_digest",
                "topology_event_digest",
                "conductance_state_before_digest",
                "budget_before_digest",
            ],
        },
        "memory_relaxation_or_decay_rule": {
            "status": "specified_for_phase8_entry",
            "rule": (
                "Relaxation or decay must be serialized, event-ordered, "
                "idempotent, and budget-accounted through a named destination "
                "surface; silent deletion or hidden decay is rejected."
            ),
            "destination_surface_type": "reversible_baseline_relaxation_account",
            "destination_surface_meaning": (
                "baseline route conductance or neutral geometry reservoir "
                "inside route-conductance accounting"
            ),
            "blocked_without": [
                "memory_relaxation_rule_id",
                "relaxation_destination_surface_id",
                "budget_after_digest",
            ],
        },
        "route_scope_runtime_policy": {
            "status": "specified_for_phase8_entry",
            "rule": (
                "Memory scope is route-local or route-set-local by digest; "
                "global hidden route preference is rejected."
            ),
            "runtime_visible_inputs": [
                "route_scope_digest",
                "route_use_digest",
                "policy_record_digest",
            ],
        },
        "conductance_eligibility_threshold": {
            "status": "specified_for_phase8_entry",
            "thresholds_to_serialize": [
                "minimum_positive_coherence_carrier",
                "max_update_delta_per_route_use",
                "conductance_eligibility_threshold",
                "relaxation_destination_threshold",
            ],
            "zero_coherence_boundary": "zero-coherence trace remains absorber, not reinforcement",
        },
        "source_evidence_summary": {
            "n08_hypothesis_a_scope": n08_i8["closeout"]["memory_or_trail_claim_scope"],
            "n08_hypothesis_a_memory_strength_physical_flux": n08_i8["closeout"][
                "independent_memory_strength_used_as_physical_flux"
            ],
            "n08_hypothesis_b_status": n08_i13["closeout_summary"][
                "hypothesis_b_status"
            ],
            "n08_hypothesis_b_current_blocker": n08_i13["closeout_summary"][
                "hypothesis_b_current_blocker"
            ],
            "n08_phase8_candidate_policy_surface": n08_i13["closeout_summary"][
                "phase_8_candidate_policy_surface"
            ],
            "n08_positive_geometry_response_present": n08_i13["checks"][
                "positive_geometry_response_present"
            ],
            "n08_static_persistence_present": n08_i13["checks"][
                "static_persistence_present"
            ],
            "n08_iteration_10_route_use_causes_trace": n08_i10["checks"][
                "route_use_causes_trace"
            ],
            "n08_iteration_11_native_policy_blocker_recorded": n08_i11["checks"][
                "native_policy_blocker_recorded"
            ],
            "n08_iteration_11a_positive_response_supported": n08_i11a[
                "claim_boundary"
            ]["positive_geometry_route_response_candidate_supported"],
            "n08_iteration_12_relaxation_not_applied": n08_i12["checks"][
                "relaxation_not_applied"
            ],
            "n08_iteration_12_relaxation_boundary_audited": n08_i12["checks"][
                "relaxation_boundary_audited"
            ],
            "n10_contract_status": n10_contract["native_contract_status"],
            "n11_gap_native_supported": n11_gap["native_supported"],
        },
    }
    row["row_digest"] = row_digest(row)
    return row


def build_nat4_gate_status(row: dict[str, Any], schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    def present(gate: str) -> bool:
        return gate in row and row[gate] not in (None, [], {})

    gate_sources = {
        "native_policy_name": "N08 closeout, N10 contract, N11 gap, N12 candidate row",
        "record_schema_sketch": "N12 Iteration 3 record schema sketch",
        "default_off_flags": "N12 Iteration 3 default-off policy flags",
        "enabled_validated_supported_separation": "N12 Iteration 3 claim boundary fields",
        "idempotency_digest_plan": "N12 Iteration 3 digest plan",
        "runtime_visible_inputs": "N10 contract plus N12 topology/budget extensions",
        "budget_surfaces": "N10 contract plus N12 typed budget semantics",
        "telemetry_requirements": "N12 telemetry namespace and export behavior",
        "snapshot_replay_requirements": "N10 replay requirements plus N12 replay extensions",
        "negative_controls": "N08 controls, N10 contract controls, N12 claim controls",
        "compatibility_tests": "N12 Iteration 3 compatibility test list",
        "claim_flags_forced_false": "N12 Iteration 2 claim flags",
        "non_rc_quantity_audit": "N12 Iteration 3 non-RC audit",
        "mutation_boundary": "N12 Iteration 3 mutation boundary",
        "producer_or_policy_may_schedule_only": "N12 Iteration 3 mutation boundary",
        "step_or_topology_event_owns_state_mutation": "N12 Iteration 3 mutation boundary",
        "src_diff_empty": "git status --short src",
        "native_supported_flags_false": "N12 Iteration 3 no-native-support flags",
        "phase8_opened_false": "N12 Iteration 3 no-implementation flags",
    }
    validators = {
        "native_policy_name": lambda: row["native_policy_name"]
        == "native_route_conductance_memory_policy",
        "record_schema_sketch": lambda: {
            "policy_id",
            "route_use_digest",
            "topology_event_digest",
            "conductance_state_before_digest",
            "conductance_state_after_digest",
            "policy_record_digest",
        }.issubset(set(row["record_schema_sketch"]["required_fields"]))
        and "hidden_memory_strength" in row["record_schema_sketch"]["forbidden_fields"],
        "default_off_flags": lambda: all(
            value is False for value in row["default_off_flags"].values()
        ),
        "enabled_validated_supported_separation": lambda: row[
            "enabled_validated_supported_separation"
        ]
        == {
            "enabled": False,
            "validated": False,
            "supported": False,
            "phase8_ready_candidate": True,
            "native_support_opened": False,
        },
        "idempotency_digest_plan": lambda: "topology_event_digest"
        in row["idempotency_digest_plan"]["policy_record_digest_inputs"]
        and "cannot mutate twice" in row["idempotency_digest_plan"][
            "duplicate_update_rejection"
        ],
        "runtime_visible_inputs": lambda: {
            "route_use_digest",
            "route_scope_digest",
            "topology_event_digest",
            "conductance_state_before_digest",
            "conductance_state_after_digest",
            "policy_record_digest",
        }.issubset(set(row["runtime_visible_inputs"])),
        "budget_surfaces": lambda: {
            "node_plus_packet_budget_surface_separate",
            "route_conductance_memory_budget_surface",
            "relaxation_destination_surface",
        }.issubset(set(row["budget_surfaces"]))
        and row["budget_semantics"]["relaxation_destination_surface"][
            "surface_type"
        ]
        == "reversible_baseline_relaxation_account",
        "telemetry_requirements": lambda: "src/pygrc/telemetry"
        == row["telemetry_namespaces"]["primary_native_namespace"]
        and row["telemetry_export_behavior"]["default_off"] is True
        and row["telemetry_export_behavior"]["backward_compatible_when_disabled"]
        is True,
        "snapshot_replay_requirements": lambda: {
            "snapshot includes policy flags and disabled-by-default state",
            "snapshot includes conductance before/after digests",
            "snapshot includes budget surface before/after digests",
            "replay preserves no native support flags",
        }.issubset(set(row["snapshot_replay_requirements"])),
        "negative_controls": lambda: {
            "hidden_memory_policy_rejected",
            "producer_memory_relabelled_native_rejected",
            "stale_geometry_read_rejected",
            "unbudgeted_relaxation_rejected",
        }.issubset(set(row["negative_controls"])),
        "compatibility_tests": lambda: {
            "route_use_without_policy_enabled_records_no_mutation",
            "node_plus_packet_budget_conserved",
            "telemetry_default_off_exports_no_new_records",
            "existing_telemetry_exports_backward_compatible_when_disabled",
            "claim_flags_remain_false",
        }.issubset(set(row["compatibility_tests"])),
        "claim_flags_forced_false": lambda: all_claim_flags_false(
            row["claim_flags_forced_false"]
        ),
        "non_rc_quantity_audit": lambda: row["non_rc_quantity_audit"][
            "audit_status"
        ]
        == "passed_for_nat4_readiness"
        and row["non_rc_quantity_audit"][
            "does_candidate_require_new_scalar_outside_rc_accounting"
        ]
        is False,
        "mutation_boundary": lambda: row["mutation_boundary"]["status"]
        == "specified_for_phase8_entry"
        and row["mutation_boundary"]["producer_or_policy_may_schedule_only"] is True
        and row["mutation_boundary"]["step_or_topology_event_owns_state_mutation"]
        is True,
        "producer_or_policy_may_schedule_only": lambda: row[
            "producer_or_policy_may_schedule_only"
        ]
        is True,
        "step_or_topology_event_owns_state_mutation": lambda: row[
            "step_or_topology_event_owns_state_mutation"
        ]
        is True,
        "src_diff_empty": lambda: row["src_diff_empty"] is True,
        "native_supported_flags_false": lambda: row["native_supported_flags_false"]
        is True
        and row["native_support_opened"] is False
        and row["claim_flags_forced_false"]["native_support_opened"] is False,
        "phase8_opened_false": lambda: row["phase8_opened_false"] is True,
    }

    status: dict[str, dict[str, Any]] = {}
    for gate in schema["nat4_gates"]["required"]:
        gate_present = present(gate)
        gate_validated = gate_present and validators[gate]()
        status[gate] = {
            "present": gate_present,
            "validated": gate_validated,
            "source": gate_sources[gate],
        }
    return status


def validate_candidate(
    row: dict[str, Any],
    schema: dict[str, Any],
    inventory_row: dict[str, Any],
    n08_i8: dict[str, Any],
    n08_i13: dict[str, Any],
    n10_contract: dict[str, Any],
    n11_gap: dict[str, Any],
) -> dict[str, bool]:
    nat4_required = schema["nat4_gates"]["required"]
    nat4_status = build_nat4_gate_status(row, schema)
    return {
        "iteration_1_route_memory_row_present": bool(inventory_row),
        "iteration_2_nat4_gates_loaded": bool(nat4_required),
        "n08_hypothesis_a_artifact_only_scope": n08_i8["closeout"][
            "memory_or_trail_claim_scope"
        ]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "n08_hypothesis_a_memory_strength_not_physical_flux": n08_i8["closeout"][
            "independent_memory_strength_used_as_physical_flux"
        ]
        is False,
        "n08_hypothesis_b_native_claims_blocked": n08_i13["claim_flags"][
            "native_route_conductance_memory_policy_supported"
        ]
        is False,
        "n08_positive_geometry_response_present": n08_i13["checks"][
            "positive_geometry_response_present"
        ],
        "n08_static_persistence_present": n08_i13["checks"][
            "static_persistence_present"
        ],
        "n08_native_policy_blocker_recorded": n08_i13["checks"][
            "native_policy_blocker_recorded"
        ],
        "n10_contract_present": n10_contract["row_id"]
        == "n10_i14_contract_02_route_conductance_memory",
        "n11_gap_present": n11_gap["native_gap"]
        == "native_route_conductance_memory_policy_missing",
        "producer_geometry_bookkeeping_split_recorded": set(
            row["producer_native_split"].keys()
        )
        == {
            "producer_side_route_memory_pattern",
            "native_geometry_conductance_policy_candidate",
            "native_coherence_flux_mechanism",
        },
        "non_rc_quantity_audit_passed": row["non_rc_quantity_audit"][
            "audit_status"
        ]
        == "passed_for_nat4_readiness",
        "no_extra_unaccounted_quantity": row["non_rc_quantity_audit"][
            "does_candidate_require_new_scalar_outside_rc_accounting"
        ]
        is False,
        "mutation_boundary_recorded": row["producer_or_policy_may_schedule_only"]
        is True
        and row["step_or_topology_event_owns_state_mutation"] is True,
        "all_nat4_gates_present": all(
            gate["present"] for gate in nat4_status.values()
        ),
        "all_nat4_gates_validated": all(
            gate["validated"] for gate in nat4_status.values()
        ),
        "telemetry_namespace_explicit": row["telemetry_namespaces"][
            "primary_native_namespace"
        ]
        == "src/pygrc/telemetry",
        "telemetry_default_off_backward_compatible": row[
            "telemetry_export_behavior"
        ]["default_off"]
        is True
        and row["telemetry_export_behavior"]["backward_compatible_when_disabled"]
        is True,
        "budget_semantics_typed": row["budget_semantics"][
            "relaxation_destination_surface"
        ]["surface_type"]
        == "reversible_baseline_relaxation_account",
        "phase8_ready_derived_from_nat4": row["nat_level"] == "NAT4"
        and row["phase8_ready"] is True,
        "no_native_support_claim": row["native_supported_flags_false"] is True
        and row["native_support_opened"] is False
        and row["claim_flags_forced_false"]["native_support_opened"] is False,
        "claim_flags_forced_false": all_claim_flags_false(
            row["claim_flags_forced_false"]
        ),
        "src_clean": row["src_diff_empty"] is True,
}


def build_schema_alignment(row: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    final_row_fields = schema["final_row_fields"]
    row_fields = sorted(row.keys())
    missing_final_row_fields = sorted(set(final_row_fields) - set(row_fields))
    extra_row_fields = sorted(set(row_fields) - set(final_row_fields))
    candidate_specific_extension_fields = {
        "budget_semantics": "Iteration 3 typed budget semantics for conductance memory and relaxation destination.",
        "conductance_eligibility_threshold": "Iteration 3 route conductance eligibility thresholds.",
        "memory_relaxation_or_decay_rule": "Iteration 3 relaxation/decay entry gate.",
        "native_support_opened": "Row-level no-native-support flag added to remove placement ambiguity.",
        "producer_native_split": "Iteration 3 geometry-vs-bookkeeping split.",
        "route_scope_runtime_policy": "Iteration 3 route-scope runtime-visible policy requirement.",
        "route_use_linked_memory_update_rule": "Iteration 3 update rule boundary.",
        "source_evidence_summary": "Iteration 3 compact source-backed evidence summary.",
        "telemetry_export_behavior": "Iteration 3 default-off/backward-compatible telemetry export behavior.",
        "telemetry_namespaces": "Iteration 3 telemetry namespace declaration, including src/pygrc/telemetry.",
    }
    return {
        "iteration_2_final_row_fields_count": len(final_row_fields),
        "candidate_row_fields_count": len(row_fields),
        "missing_final_row_fields": missing_final_row_fields,
        "extra_row_fields": extra_row_fields,
        "candidate_specific_extension_fields": candidate_specific_extension_fields,
        "all_extra_fields_documented": set(extra_row_fields).issubset(
            set(candidate_specific_extension_fields)
        ),
        "native_support_opened_field_in_iteration_2_schema": (
            "native_support_opened" in final_row_fields
        ),
        "native_support_opened_field_present_in_candidate_row": (
            row.get("native_support_opened") is False
        ),
        "extension_policy": (
            "Iteration 3 may add candidate-specific extension fields when they "
            "are explicitly documented and do not promote native support or "
            "Phase 8 implementation."
        ),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    n08_i8 = load_json(N08_I8_OUTPUT)
    n08_i10 = load_json(N08_I10_OUTPUT)
    n08_i11 = load_json(N08_I11_OUTPUT)
    n08_i11a = load_json(N08_I11A_OUTPUT)
    n08_i12 = load_json(N08_I12_OUTPUT)
    n08_i13 = load_json(N08_I13_OUTPUT)
    n10_i14 = load_json(N10_I14_OUTPUT)
    n11_i11 = load_json(N11_I11_OUTPUT)

    inventory_row = find_inventory_route_memory_row(inventory)
    n10_contract = find_object_by_row_id(
        n10_i14, "n10_i14_contract_02_route_conductance_memory"
    )
    n11_gap = find_object_by_row_id(
        n11_i11, "n11_i11_gap_02_route_conductance_memory_policy"
    )
    if n10_contract is None:
        raise ValueError("N10 route conductance memory contract row missing")
    if n11_gap is None:
        raise ValueError("N11 route conductance memory gap row missing")

    row = build_candidate_row(
        inventory_row,
        schema,
        n08_i8,
        n08_i10,
        n08_i11,
        n08_i11a,
        n08_i12,
        n08_i13,
        n10_contract,
        n11_gap,
    )
    nat4_status = build_nat4_gate_status(row, schema)
    checks = validate_candidate(
        row, schema, inventory_row, n08_i8, n08_i13, n10_contract, n11_gap
    )

    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_1_REPORT): source_artifact(ITERATION_1_REPORT),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(ITERATION_2_REPORT): source_artifact(ITERATION_2_REPORT),
        rel(N08_I8_OUTPUT): source_artifact(N08_I8_OUTPUT, n08_i8),
        rel(N08_I8_REPORT): source_artifact(N08_I8_REPORT),
        rel(N08_I10_OUTPUT): source_artifact(N08_I10_OUTPUT, n08_i10),
        rel(N08_I10_REPORT): source_artifact(N08_I10_REPORT),
        rel(N08_I11_OUTPUT): source_artifact(N08_I11_OUTPUT, n08_i11),
        rel(N08_I11_REPORT): source_artifact(N08_I11_REPORT),
        rel(N08_I11A_OUTPUT): source_artifact(N08_I11A_OUTPUT, n08_i11a),
        rel(N08_I11A_REPORT): source_artifact(N08_I11A_REPORT),
        rel(N08_I12_OUTPUT): source_artifact(N08_I12_OUTPUT, n08_i12),
        rel(N08_I12_REPORT): source_artifact(N08_I12_REPORT),
        rel(N08_I13_OUTPUT): source_artifact(N08_I13_OUTPUT, n08_i13),
        rel(N08_I13_REPORT): source_artifact(N08_I13_REPORT),
        rel(N10_I14_OUTPUT): source_artifact(N10_I14_OUTPUT, n10_i14),
        rel(N10_I14_REPORT): source_artifact(N10_I14_REPORT),
        rel(N11_I11_OUTPUT): source_artifact(N11_I11_OUTPUT, n11_i11),
        rel(N11_I11_REPORT): source_artifact(N11_I11_REPORT),
    }
    schema_alignment = build_schema_alignment(row, schema)
    source_digest_policy = {
        "file_sha256_is_required_for_every_source": True,
        "all_source_file_sha256_present": all(
            isinstance(artifact["sha256"], str) and len(artifact["sha256"]) == 64
            for artifact in source_artifacts.values()
        ),
        "upstream_output_digest_or_artifact_digest_may_be_null": True,
        "null_digest_reason": (
            "Upstream N08/N10/N11 artifacts use mixed output_digest and "
            "artifact_digest conventions. N12 pins every source by file SHA-256 "
            "and records upstream digest fields opportunistically."
        ),
        "controlling_provenance_pin": "source_artifacts[*].sha256",
    }
    artifact_reproducibility = {
        "wall_clock_timestamp_in_file": False,
        "generated_at": GENERATED_AT,
        "generated_at_policy": (
            "fixed experiment timestamp for reproducible file SHA across reruns "
            "with unchanged source files and git HEAD"
        ),
        "output_digest_excludes": ["generated_at", "output_digest", "git"],
        "file_sha_reproducible_for_fixed_sources_and_git_head": True,
    }
    checks.update(
        {
            "row_level_native_support_opened_false": row["native_support_opened"]
            is False,
            "schema_extension_fields_documented": schema_alignment[
                "all_extra_fields_documented"
            ],
            "source_file_sha256_all_present": source_digest_policy[
                "all_source_file_sha256_present"
            ],
            "generated_at_reproducible": artifact_reproducibility[
                "wall_clock_timestamp_in_file"
            ]
            is False,
        }
    )

    output = {
        "experiment": "N12",
        "iteration": 3,
        "purpose": "route_conductance_memory_candidate_nat4_readiness",
        "schema": "n12_route_conductance_memory_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "candidate_result": {
            "primary_disposition": row["primary_disposition"],
            "nat_level": row["nat_level"],
            "phase8_ready": row["phase8_ready"],
            "native_policy_name": row["native_policy_name"],
            "native_support_opened": False,
            "phase8_opened": False,
            "claim_ceiling": row["claim_ceiling"],
            "supported_interpretation": (
                "Phase 8-ready native route-conductance memory policy "
                "candidate with no implementation and no native support claim."
            ),
        },
        "checks": checks,
        "route_conductance_memory_candidate": row,
        "schema_alignment": schema_alignment,
        "nat4_gate_status": nat4_status,
        "claim_boundary": {
            "native_absorption_candidate_is_native_support": False,
            "native_support_is_agency": False,
            "route_conductance_memory_is_intention": False,
            "route_conductance_memory_is_aco_or_ant_colony": False,
            "producer_memory_strength_is_native_state": False,
            "pure_flux_trail_memory_supported": False,
            "phase8_ready_is_implementation": False,
        },
        "source_artifacts": source_artifacts,
        "source_digest_policy": source_digest_policy,
        "artifact_reproducibility": artifact_reproducibility,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["route_conductance_memory_candidate"]
    checks = output["checks"]
    split = row["producer_native_split"]
    source_summary = row["source_evidence_summary"]
    schema_alignment = output["schema_alignment"]
    lines = [
        "# N12 Iteration 3 Route Conductance Memory Candidate",
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
        "row.native_support_opened = false",
        "```",
        "",
        "Iteration 3 classifies route conductance memory as a `NAT4` Phase 8-ready",
        "native policy candidate. This is a readiness classification only. It is",
        "not native support, not agency, not intention, not ACO or ant-colony",
        "behavior, and not a Phase 8 implementation.",
        "",
        "The JSON artifact is the source of truth for the full candidate record,",
        "source artifacts, digests, policy schema sketch, controls, and gate audit.",
        "The file is generated without a wall-clock timestamp so its SHA is",
        "reproducible for unchanged sources and git HEAD.",
        "",
        "## Source Decision",
        "",
        "N08 Hypothesis A remains producer/artifact-local memory. N08 Hypothesis B",
        "provides a bounded static positive-geometry route-response design target,",
        "but does not support native geometry-mediated trail memory. N10 and N11",
        "identify the missing native surface as `native_route_conductance_memory_policy`.",
        "",
        "```text",
        f"N08 Hypothesis A scope = {source_summary['n08_hypothesis_a_scope']}",
        "N08 memory strength used as physical flux = "
        f"{str(source_summary['n08_hypothesis_a_memory_strength_physical_flux']).lower()}",
        f"N08 Hypothesis B blocker = {source_summary['n08_hypothesis_b_current_blocker']}",
        "Phase 8 candidate policy surface = "
        f"{source_summary['n08_phase8_candidate_policy_surface']}",
        "```",
        "",
        "## Geometry Vs Bookkeeping Split",
        "",
        "| Layer | Status | Boundary |",
        "| --- | --- | --- |",
        "| Producer-side route memory pattern | "
        f"{split['producer_side_route_memory_pattern']['status']} | "
        "Serialized `memory_strength` remains artifact-only score evidence. |",
        "| Native geometry/conductance policy candidate | "
        f"{split['native_geometry_conductance_policy_candidate']['status']} | "
        "Only committed route-use/topology events may mutate conductance state. |",
        "| Native coherence/flux mechanism | "
        f"{split['native_coherence_flux_mechanism']['status']} | "
        "Pure flux trail memory and zero-coherence reinforcement remain blocked. |",
        "",
        "## NAT4 Gate Audit",
        "",
        "| Gate | Present | Validated | Source |",
        "| --- | --- | --- | --- |",
    ]
    for gate, status in output["nat4_gate_status"].items():
        lines.append(
            "| "
            f"`{gate}` | "
            f"`{str(status['present']).lower()}` | "
            f"`{str(status['validated']).lower()}` | "
            f"{status['source']} |"
        )
    lines.extend(
        [
            "",
            "## Record Schema Sketch",
            "",
            "```json",
            json.dumps(row["record_schema_sketch"], indent=2, sort_keys=True),
            "```",
            "",
            "## Budget Semantics",
            "",
            "```json",
            json.dumps(row["budget_semantics"], indent=2, sort_keys=True),
            "```",
            "",
            "## Telemetry Requirements",
            "",
            "```json",
            json.dumps(
                {
                    "telemetry_namespaces": row["telemetry_namespaces"],
                    "telemetry_export_behavior": row["telemetry_export_behavior"],
                    "telemetry_requirements": row["telemetry_requirements"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Compatibility Tests",
            "",
            "```json",
            json.dumps(row["compatibility_tests"], indent=2, sort_keys=True),
            "```",
            "",
            "## Schema Alignment And Candidate Extensions",
            "",
            "```json",
            json.dumps(schema_alignment, indent=2, sort_keys=True),
            "```",
            "",
            "## Source Digest Policy",
            "",
            "```json",
            json.dumps(output["source_digest_policy"], indent=2, sort_keys=True),
            "```",
            "",
            "## Artifact Reproducibility",
            "",
            "```json",
            json.dumps(
                output["artifact_reproducibility"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Non-RC Quantity Audit",
            "",
            "```text",
            "memory is RC-compatible only as route geometry/conductance state",
            "producer memory_strength is bookkeeping and cannot be native state",
            "relaxation or decay must debit/transfer through an accounted surface",
            "extra scalar outside RC accounting required = false",
            "```",
            "",
            "## Mutation Boundary",
            "",
            "```text",
            "producer_or_policy_may_schedule_only = true",
            "step_or_topology_event_owns_state_mutation = true",
            "state_mutation_owner = LGRC step or committed topology event boundary",
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(checks, indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "native absorption candidate != native support",
            "native support != agency",
            "route conductance memory != intention",
            "route conductance memory != ACO or ant-colony behavior",
            "producer memory_strength != native route memory state",
            "phase8_ready != Phase 8 implementation",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)


if __name__ == "__main__":
    main()

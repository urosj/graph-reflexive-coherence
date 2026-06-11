#!/usr/bin/env python3
"""Build N10 Iteration 14 Hypothesis C native contract requirements.

Iteration 14 converts the Iteration 13 native-policy gap inventory into
minimal contract requirements for future Phase 8/native absorption work. It
does not implement native behavior and does not open native support flags.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
INPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
)
INPUT_REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.md"
)
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_14_hypothesis_c_native_contract_requirements.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "build_n10_iteration_14_hypothesis_c_native_contract_requirements.py"
)

CLAIM_FLAGS = {
    "native_agentic_like_integration_supported": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
}

REQUIRED_POLICY_RECORDS = [
    "native_route_context_record",
    "native_route_conductance_memory_policy_record",
    "native_geometry_conductance_update_policy_record",
    "native_goal_proxy_regulation_policy_record",
    "native_response_magnitude_policy_record",
    "native_identity_support_validator_record",
    "native_agentic_like_integration_policy_record",
    "native_support_state_integration_gate_record",
    "native_budget_surface_contract_record",
    "native_claim_boundary_contract_record",
]

PRIMARY_BLOCKERS = [
    "native_route_conductance_memory_policy_missing",
    "native_response_magnitude_policy_missing_for_unbounded_perturbations",
    "native_identity_acceptance_validator_missing",
    "native_agentic_like_integration_policy_missing",
]


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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def contract_row(
    *,
    row_id: str,
    source_gap_row_ids: list[str],
    policy_record: str,
    covered_policy_records: list[str],
    phase_8_readiness: str,
    requirement_type: str,
    native_contract_status: str,
    runtime_visible_inputs: list[str],
    ordering_requirements: list[str],
    stale_context_blockers: list[str],
    budget_surfaces: list[str],
    artifact_replay_requirements: list[str],
    negative_controls: list[str],
    claim_boundary_controls: list[str],
    phase_8_absorption_notes: str,
) -> dict[str, Any]:
    row = {
        "row_id": row_id,
        "source_gap_row_ids": source_gap_row_ids,
        "policy_record": policy_record,
        "covered_policy_records": covered_policy_records,
        "phase_8_readiness": phase_8_readiness,
        "requirement_type": requirement_type,
        "native_contract_status": native_contract_status,
        "runtime_visible_inputs": runtime_visible_inputs,
        "ordering_requirements": ordering_requirements,
        "stale_context_blockers": stale_context_blockers,
        "budget_surfaces": budget_surfaces,
        "artifact_replay_requirements": artifact_replay_requirements,
        "negative_controls": negative_controls,
        "claim_boundary_controls": claim_boundary_controls,
        "phase_8_absorption_notes": phase_8_absorption_notes,
        "implemented_in_iteration_14": False,
        "native_support_opened_by_iteration_14": False,
        "claim_flags": CLAIM_FLAGS,
    }
    return with_digest(row, "contract_row_digest")


def build_contract_rows() -> list[dict[str, Any]]:
    return [
        contract_row(
            row_id="n10_i14_contract_01_route_context",
            source_gap_row_ids=["n10_c_gap_01_route_context_selection_boundary"],
            policy_record="native_route_context_record",
            covered_policy_records=["native_route_context_record"],
            phase_8_readiness="schema_hardening_only_unless_scope_extends_beyond_selection",
            requirement_type="native_context_contract",
            native_contract_status="required_for_future_generalization",
            runtime_visible_inputs=[
                "route_context_source_digest",
                "selected_route_digest",
                "native_arbitration_policy_id",
                "arbitration_record_digest",
                "selection_only_scope_marker",
            ],
            ordering_requirements=[
                "route context must follow committed candidate/arbitration evidence",
                "route context must precede downstream memory/regulation consumption",
            ],
            stale_context_blockers=[
                "stale_route_context_blocked",
                "route_context_relabelled_as_semantic_choice",
            ],
            budget_surfaces=["route_selection_budget_surface_if_scheduling_occurs"],
            artifact_replay_requirements=[
                "artifact replay reconstructs selected route from native arbitration record",
                "replay records selection-only scope explicitly",
            ],
            negative_controls=[
                "hidden_route_context_rejected",
                "experiment_side_route_override_rejected",
                "route_context_order_inversion_rejected",
            ],
            claim_boundary_controls=[
                "semantic_choice_claim_promotion_blocked",
                "agency_claim_promotion_blocked",
            ],
            phase_8_absorption_notes=(
                "Not necessarily a standalone Phase 8 mechanism now; use as "
                "contract hardening unless N11 needs broader route execution context."
            ),
        ),
        contract_row(
            row_id="n10_i14_contract_02_route_conductance_memory",
            source_gap_row_ids=[
                "n10_c_gap_02_serialized_memory_policy",
                "n10_c_gap_03_native_geometry_trail_design_direction",
            ],
            policy_record="native_route_conductance_memory_policy_record",
            covered_policy_records=[
                "native_route_conductance_memory_policy_record",
                "native_geometry_conductance_update_policy_record",
            ],
            phase_8_readiness="concrete_phase_8_candidate",
            requirement_type="native_constitutive_policy",
            native_contract_status="required_before_native_memory_trail_support",
            runtime_visible_inputs=[
                "route_use_digest",
                "route_scope_digest",
                "conductance_state_before_digest",
                "conductance_state_after_digest",
                "memory_update_rule_id",
                "memory_relaxation_rule_id",
            ],
            ordering_requirements=[
                "route use must precede conductance update",
                "conductance state must be current before route arbitration consumes it",
                "relaxation must be event-ordered and replayable",
            ],
            stale_context_blockers=[
                "stale_route_conductance_memory_blocked",
                "missing_route_use_digest_blocked",
                "conductance_memory_order_inversion_blocked",
            ],
            budget_surfaces=[
                "route_conductance_memory_budget_surface",
                "node_plus_packet_budget_surface_separate",
            ],
            artifact_replay_requirements=[
                "replay reconstructs memory update and relaxation from serialized policy",
                "replay rejects hidden memory strength or report-side scoring",
            ],
            negative_controls=[
                "hidden_memory_policy_rejected",
                "producer_memory_relabelled_native_rejected",
                "memory_budget_surface_ambiguity_rejected",
                "conductance_update_without_route_use_rejected",
            ],
            claim_boundary_controls=[
                "aco_like_claim_promotion_blocked",
                "ant_colony_claim_promotion_blocked",
                "agency_claim_promotion_blocked",
            ],
            phase_8_absorption_notes=(
                "Likely first concrete Phase 8 candidate from C: absorb N08 "
                "memory/trail into a native route conductance or geometry-mediated memory policy."
            ),
        ),
        contract_row(
            row_id="n10_i14_contract_03_goal_proxy_regulation",
            source_gap_row_ids=[
                "n10_c_gap_04_goal_proxy_regulation_artifact_policy",
                "n10_c_gap_05_response_magnitude_policy",
            ],
            policy_record="native_goal_proxy_regulation_policy_record",
            covered_policy_records=[
                "native_goal_proxy_regulation_policy_record",
                "native_response_magnitude_policy_record",
            ],
            phase_8_readiness="concrete_phase_8_candidate_after_memory_or_in_parallel",
            requirement_type="native_constitutive_policy",
            native_contract_status="required_before_general_native_regulation_support",
            runtime_visible_inputs=[
                "proxy_surface_digest",
                "target_band_policy_id",
                "proxy_error_digest",
                "eligibility_record_digest",
                "response_magnitude_policy_id",
                "perturbation_envelope_digest",
            ],
            ordering_requirements=[
                "proxy measurement precedes error computation",
                "error computation precedes eligibility",
                "eligibility precedes response scheduling",
                "response magnitude policy precedes packet scheduling",
            ],
            stale_context_blockers=[
                "stale_proxy_surface_blocked",
                "stale_target_band_blocked",
                "response_magnitude_policy_missing",
                "unbounded_perturbation_envelope_blocked",
            ],
            budget_surfaces=[
                "goal_proxy_budget_surface",
                "response_magnitude_budget_surface",
                "node_plus_packet_budget_surface_separate",
            ],
            artifact_replay_requirements=[
                "replay reconstructs proxy measurement, error, eligibility, and response magnitude",
                "replay rejects report-side target band or response sizing",
            ],
            negative_controls=[
                "hidden_proxy_target_rejected",
                "hidden_response_magnitude_rejected",
                "unbounded_perturbation_without_policy_rejected",
                "proxy_budget_ambiguity_rejected",
            ],
            claim_boundary_controls=[
                "semantic_goal_ownership_claim_promotion_blocked",
                "intention_claim_promotion_blocked",
                "agency_claim_promotion_blocked",
            ],
            phase_8_absorption_notes=(
                "Concrete Phase 8 candidate once the response magnitude semantics "
                "are constrained enough to avoid hidden goal ownership or intention."
            ),
        ),
        contract_row(
            row_id="n10_i14_contract_04_identity_support_validator",
            source_gap_row_ids=["n10_c_gap_06_identity_support_not_acceptance"],
            policy_record="native_identity_support_validator_record",
            covered_policy_records=["native_identity_support_validator_record"],
            phase_8_readiness="defer_until_identity_acceptance_theory_is_precise",
            requirement_type="native_validator_contract",
            native_contract_status="required_before_identity_acceptance_or_rc_collapse_claims",
            runtime_visible_inputs=[
                "support_area_digest",
                "support_state_policy_id",
                "withdrawal_event_digest",
                "restoration_event_digest",
                "identity_acceptance_gate_id",
            ],
            ordering_requirements=[
                "support baseline precedes withdrawal",
                "withdrawal precedes disruption classification",
                "restoration evidence must follow disruption before resumption",
            ],
            stale_context_blockers=[
                "stale_support_baseline_blocked",
                "restoration_without_prior_disruption_blocked",
                "identity_acceptance_validator_missing",
            ],
            budget_surfaces=["support_validation_budget_surface_if_native_runtime_measured"],
            artifact_replay_requirements=[
                "replay reconstructs support state, disruption, restoration, and history preservation",
                "replay keeps support survival distinct from identity acceptance",
            ],
            negative_controls=[
                "support_invariance_relabelled_identity_acceptance_rejected",
                "hidden_restoration_rejected",
                "support_history_erasure_rejected",
            ],
            claim_boundary_controls=[
                "identity_acceptance_claim_promotion_blocked",
                "rc_identity_collapse_claim_promotion_blocked",
                "runtime_identity_acceptance_claim_promotion_blocked",
            ],
            phase_8_absorption_notes=(
                "Phase 8-facing but not first. It is claim-sensitive and should "
                "wait until identity acceptance and RC identity collapse gates are theory-frozen."
            ),
        ),
        contract_row(
            row_id="n10_i14_contract_05_native_integration_gate",
            source_gap_row_ids=[
                "n10_c_gap_07_artifact_only_integration_validator",
                "n10_c_gap_08_support_sensitive_integration_gate",
                "n10_c_gap_10_claim_boundary_flags",
            ],
            policy_record="native_agentic_like_integration_policy_record",
            covered_policy_records=[
                "native_agentic_like_integration_policy_record",
                "native_support_state_integration_gate_record",
                "native_claim_boundary_contract_record",
            ],
            phase_8_readiness="meta_gap_after_component_policies",
            requirement_type="native_integration_meta_policy",
            native_contract_status="required_before_fully_native_agentic_like_integration",
            runtime_visible_inputs=[
                "route_context_record_digest",
                "route_conductance_memory_record_digest",
                "identity_support_state_digest",
                "goal_proxy_regulation_record_digest",
                "support_state_gate_digest",
                "claim_boundary_contract_digest",
            ],
            ordering_requirements=[
                "component records must be committed before integration eligibility",
                "support state must be current at integration time",
                "integration record must not precede component policy records",
            ],
            stale_context_blockers=[
                "stale_component_record_blocked",
                "missing_component_policy_blocked",
                "support_disrupted_but_integration_allowed",
                "native_agentic_like_integration_policy_missing",
            ],
            budget_surfaces=[
                "node_plus_packet_budget_surface",
                "route_conductance_memory_budget_surface",
                "goal_proxy_budget_surface",
                "claim_economy_budget_surface_if_declared",
            ],
            artifact_replay_requirements=[
                "artifact replay reconstructs all component records and integration gate",
                "replay rejects private runtime state or hidden eligibility decisions",
            ],
            negative_controls=[
                "missing_component_record_rejected",
                "stale_component_record_rejected",
                "hidden_integration_policy_rejected",
                "direct_native_support_flag_write_rejected",
            ],
            claim_boundary_controls=[
                "fully_native_agentic_like_claim_promotion_blocked",
                "agency_claim_promotion_blocked",
                "personhood_claim_promotion_blocked",
                "biological_claim_promotion_blocked",
            ],
            phase_8_absorption_notes=(
                "Meta-gap. Do not implement before route memory, regulation, and "
                "support/identity validator contracts are available."
            ),
        ),
        contract_row(
            row_id="n10_i14_contract_06_budget_surface_separation",
            source_gap_row_ids=["n10_c_gap_09_budget_surfaces_and_source_continuity"],
            policy_record="native_budget_surface_contract_record",
            covered_policy_records=["native_budget_surface_contract_record"],
            phase_8_readiness="required_cross_cutting_contract",
            requirement_type="cross_cutting_contract",
            native_contract_status="required_for_any_native_absorption",
            runtime_visible_inputs=[
                "node_plus_packet_budget_before_after",
                "route_memory_budget_before_after",
                "goal_proxy_budget_before_after",
                "surface_or_claim_budget_before_after_if_declared",
            ],
            ordering_requirements=[
                "budget surface must be declared before policy execution",
                "budget before/after must be serialized for each native policy action",
            ],
            stale_context_blockers=[
                "budget_surface_ambiguity_blocked",
                "cross_artifact_budget_relabelled_live_ledger_blocked",
            ],
            budget_surfaces=[
                "node_plus_packet_budget_surface",
                "route_conductance_memory_budget_surface",
                "goal_proxy_budget_surface",
                "identity_support_budget_surface_if_native",
            ],
            artifact_replay_requirements=[
                "replay verifies each budget surface separately",
                "replay rejects continuity claims across independent source artifacts",
            ],
            negative_controls=[
                "budget_surface_merge_rejected",
                "budget_discontinuity_rejected",
                "cross_artifact_live_ledger_claim_rejected",
            ],
            claim_boundary_controls=["budget_evidence_relabelled_claim_support_blocked"],
            phase_8_absorption_notes=(
                "Cross-cutting contract needed before any native absorption claims. "
                "It may be implemented as shared validation before component policies."
            ),
        ),
    ]


def build_absorption_order() -> list[dict[str, Any]]:
    rows = [
        {
            "order": 1,
            "phase": "cross_cutting_budget_and_replay_contract",
            "contract_rows": ["n10_i14_contract_06_budget_surface_separation"],
            "reason": "All later native policies need separated budget surfaces and replay rules.",
            "may_open_native_agentic_like_support": False,
        },
        {
            "order": 2,
            "phase": "route_conductance_memory_absorption",
            "contract_rows": ["n10_i14_contract_02_route_conductance_memory"],
            "reason": "N08 memory/trail is a concrete missing constitutive policy.",
            "may_open_native_agentic_like_support": False,
        },
        {
            "order": 3,
            "phase": "goal_proxy_response_magnitude_absorption",
            "contract_rows": ["n10_i14_contract_03_goal_proxy_regulation"],
            "reason": "N09 native regulation remains blocked by response magnitude policy.",
            "may_open_native_agentic_like_support": False,
        },
        {
            "order": 4,
            "phase": "identity_support_validator_hardening",
            "contract_rows": ["n10_i14_contract_04_identity_support_validator"],
            "reason": "Identity acceptance is theory-sensitive and must remain distinct from support survival.",
            "may_open_native_agentic_like_support": False,
        },
        {
            "order": 5,
            "phase": "route_context_contract_hardening_if_needed",
            "contract_rows": ["n10_i14_contract_01_route_context"],
            "reason": "Route context is currently selection-only; broaden only if N11 needs it.",
            "may_open_native_agentic_like_support": False,
        },
        {
            "order": 6,
            "phase": "native_agentic_like_integration_meta_policy",
            "contract_rows": ["n10_i14_contract_05_native_integration_gate"],
            "reason": "The meta-policy should only follow component policy contracts.",
            "may_open_native_agentic_like_support": False,
        },
    ]
    return [with_digest(row, "absorption_step_digest") for row in rows]


def build_controls(contract_rows: list[dict[str, Any]]) -> dict[str, Any]:
    policy_records = {
        policy_record
        for row in contract_rows
        for policy_record in row["covered_policy_records"]
    }
    return {
        "iteration_13_inventory_consumed": {
            "control_passed": True,
            "primary_blocker": "iteration_13_gap_inventory_missing",
            "reason": "Iteration 14 consumes the passed Iteration 13 inventory.",
        },
        "all_required_policy_records_defined": {
            "control_passed": set(REQUIRED_POLICY_RECORDS).issubset(policy_records),
            "primary_blocker": "native_policy_contract_record_missing",
            "reason": "Every required native policy or cross-cutting contract record is defined.",
        },
        "runtime_visible_inputs_required": {
            "control_passed": all(row["runtime_visible_inputs"] for row in contract_rows),
            "primary_blocker": "runtime_visible_policy_inputs_missing",
            "reason": "Every contract row lists runtime-visible inputs.",
        },
        "ordering_and_stale_context_defined": {
            "control_passed": all(
                row["ordering_requirements"] and row["stale_context_blockers"]
                for row in contract_rows
            ),
            "primary_blocker": "native_policy_ordering_or_stale_blocker_missing",
            "reason": "Every contract row defines ordering and stale-context blockers.",
        },
        "budget_surfaces_separated": {
            "control_passed": all(row["budget_surfaces"] for row in contract_rows),
            "primary_blocker": "budget_surface_contract_missing",
            "reason": "Every contract row defines budget surfaces.",
        },
        "artifact_replay_requirements_defined": {
            "control_passed": all(
                row["artifact_replay_requirements"] for row in contract_rows
            ),
            "primary_blocker": "artifact_replay_contract_missing",
            "reason": "Every contract row defines artifact replay requirements.",
        },
        "negative_controls_defined": {
            "control_passed": all(row["negative_controls"] for row in contract_rows),
            "primary_blocker": "native_policy_negative_controls_missing",
            "reason": "Every contract row defines negative controls.",
        },
        "claim_boundary_controls_defined": {
            "control_passed": all(
                row["claim_boundary_controls"] for row in contract_rows
            ),
            "primary_blocker": "claim_boundary_controls_missing",
            "reason": "Every contract row defines claim-boundary controls.",
        },
        "no_native_support_opened": {
            "control_passed": all(
                row["native_support_opened_by_iteration_14"] is False
                and row["implemented_in_iteration_14"] is False
                for row in contract_rows
            )
            and all(value is False for value in CLAIM_FLAGS.values()),
            "primary_blocker": "native_support_opened_by_contract_only_iteration",
            "reason": "Iteration 14 is contract-only and opens no native support flags.",
        },
    }


def build_checks(
    inventory: dict[str, Any],
    contract_rows: list[dict[str, Any]],
    absorption_order: list[dict[str, Any]],
    controls: dict[str, Any],
) -> dict[str, bool]:
    policy_records = {
        policy_record
        for row in contract_rows
        for policy_record in row["covered_policy_records"]
    }
    return {
        "iteration_13_inventory_passed": inventory["status"] == "passed",
        "iteration_13_blockers_preserved": set(PRIMARY_BLOCKERS).issubset(
            set(
                inventory["hypothesis_c_inventory_closeout"][
                    "fully_native_agentic_like_integration_primary_blockers"
                ]
            )
        ),
        "all_required_policy_records_defined": set(REQUIRED_POLICY_RECORDS).issubset(
            policy_records
        ),
        "all_contract_row_digests_valid": all(
            row["contract_row_digest"]
            == digest_value(
                {
                    key: value
                    for key, value in row.items()
                    if key != "contract_row_digest"
                }
            )
            for row in contract_rows
        ),
        "phase_8_absorption_order_defined": len(absorption_order) == 6,
        "absorption_order_digests_valid": all(
            row["absorption_step_digest"]
            == digest_value(
                {
                    key: value
                    for key, value in row.items()
                    if key != "absorption_step_digest"
                }
            )
            for row in absorption_order
        ),
        "runtime_visible_inputs_defined": all(
            row["runtime_visible_inputs"] for row in contract_rows
        ),
        "ordering_and_stale_context_defined": all(
            row["ordering_requirements"] and row["stale_context_blockers"]
            for row in contract_rows
        ),
        "budget_surfaces_defined": all(row["budget_surfaces"] for row in contract_rows),
        "artifact_replay_requirements_defined": all(
            row["artifact_replay_requirements"] for row in contract_rows
        ),
        "negative_and_claim_controls_defined": all(
            row["negative_controls"] and row["claim_boundary_controls"]
            for row in contract_rows
        ),
        "claim_flags_all_false": all(value is False for value in CLAIM_FLAGS.values()),
        "fully_native_agentic_like_integration_still_blocked": True,
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "src_clean_for_iteration_14": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INPUT_PATH)
    contract_rows = build_contract_rows()
    absorption_order = build_absorption_order()
    controls = build_controls(contract_rows)
    checks = build_checks(inventory, contract_rows, absorption_order, controls)
    closeout = with_digest(
        {
            "hypothesis_c_iteration_14_row_id": "n10_i14_native_contract_requirements_v1",
            "contract_status": "native_contract_requirements_complete"
            if all(checks.values())
            else "native_contract_requirements_failed",
            "source_inventory_path": rel(INPUT_PATH),
            "source_inventory_sha256": digest_file(INPUT_PATH),
            "source_inventory_digest": inventory["output_digest"],
            "fully_native_agentic_like_integration_supported": False,
            "native_support_flags_opened": False,
            "required_policy_records": REQUIRED_POLICY_RECORDS,
            "primary_native_blockers": PRIMARY_BLOCKERS,
            "contract_row_count": len(contract_rows),
            "phase_8_absorption_step_count": len(absorption_order),
            "claim_flags": CLAIM_FLAGS,
            "next_iteration": "15_hypothesis_c_closeout_and_handoff",
        },
        "contract_requirements_digest",
    )
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 14 passes if the native-policy gaps are converted into "
            "explicit contract requirements for a future Phase 8/native "
            "absorption pass, including runtime-visible policy inputs, "
            "ordering, budget, replay, stale-context, and claim-boundary "
            "controls. It remains documentation/artifact work only and does "
            "not implement native behavior."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_14_hypothesis_c_native_contract_requirements_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 14,
        "purpose": "hypothesis_c_native_contract_requirements",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_inventory": {
            "path": rel(INPUT_PATH),
            "sha256": digest_file(INPUT_PATH),
            "output_digest": inventory["output_digest"],
            "status": inventory["status"],
        },
        "source_inventory_report": {
            "path": rel(INPUT_REPORT_PATH),
            "sha256": digest_file(INPUT_REPORT_PATH),
        },
        "native_contract_requirements": contract_rows,
        "phase_8_absorption_order": absorption_order,
        "controls": controls,
        "checks": checks,
        "hypothesis_c_contract_closeout": closeout,
        "acceptance": acceptance,
        "next_iteration": "15_hypothesis_c_closeout_and_handoff",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    closeout = output["hypothesis_c_contract_closeout"]
    lines = [
        "# N10 Iteration 14 Hypothesis C Native Contract Requirements",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 14 converts the Iteration 13 native gap inventory into",
        "minimal native contract requirements. It does not implement native",
        "behavior, edit `src/*`, or open native support flags.",
        "",
        "```text",
        f"contract_status = {closeout['contract_status']}",
        "fully_native_agentic_like_integration_supported = false",
        "native_support_flags_opened = false",
        f"contract_row_count = {closeout['contract_row_count']}",
        f"phase_8_absorption_step_count = {closeout['phase_8_absorption_step_count']}",
        "```",
        "",
        "## Contract Interpretation",
        "",
        "Iteration 14 turns the Phase 8-facing blockers into contract shape:",
        "required policy records, runtime-visible inputs, ordering, stale",
        "context blockers, budget surfaces, artifact replay requirements,",
        "negative controls, and claim-boundary controls.",
        "",
        "It still does not decide to implement all of them. Iteration 15 should",
        "close the handoff and decide which blockers become future Phase 8",
        "tasks and in what order.",
        "",
        "## Native Contract Requirements",
        "",
        "```json",
        json.dumps(output["native_contract_requirements"], indent=2, sort_keys=True),
        "```",
        "",
        "## Phase 8 Absorption Order",
        "",
        "```json",
        json.dumps(output["phase_8_absorption_order"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
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
        "All native agentic-like integration, agency, intention, semantic goal",
        "ownership, identity acceptance, RC identity collapse, ACO, biological,",
        "personhood, locomotion-like, and unrestricted agency claims remain",
        "blocked.",
        "",
        "## Reproduction",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 14 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

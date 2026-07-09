#!/usr/bin/env python3
"""Build N30 Iteration 2 participant / medium schema freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
I1_OUTPUT = EXPERIMENT / "outputs" / "n30_source_inventory_i1.json"
OUTPUT = EXPERIMENT / "outputs" / "n30_schema_control_freeze_i2.json"
REPORT = EXPERIMENT / "reports" / "n30_schema_control_freeze_i2.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_schema_control_freeze_i2.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"


PARTICIPANT_LADDER = {
    "P0": {
        "label": "medium_only_perturbation_no_attributable_participant",
        "meaning": "A medium perturbation exists but no contributor/respondent carrier is attributable.",
        "n30_positive_support_allowed": False,
    },
    "P1": {
        "label": "attributable_contributor_or_respondent_within_one_event_chain",
        "meaning": "A participant carrier is attributable within a bounded event chain.",
        "n30_positive_support_allowed": "minimal_input_only",
    },
    "P2": {
        "label": "same_carrier_recognizable_across_bounded_replay_window",
        "meaning": "The participant carrier remains recognizable under bounded replay.",
        "n30_positive_support_allowed": True,
    },
    "P3": {
        "label": "boundary_or_interface_participant",
        "meaning": "The participant is expressed through a boundary/interface surface.",
        "n30_positive_support_allowed": "secondary_observation_only",
    },
    "P4": {
        "label": "support_sensitive_participant",
        "meaning": "The carrier has support-sensitive persistence but not N30-native agency.",
        "n30_positive_support_allowed": "secondary_observation_only",
    },
    "P5": {
        "label": "withdrawal_resistant_participant_out_of_N30_primary_scope",
        "meaning": "Withdrawal-resistant participant evidence belongs to earlier/later dedicated probes.",
        "n30_positive_support_allowed": False,
    },
    "P6": {
        "label": "generative_participant_out_of_N30_primary_scope",
        "meaning": "Generative participant evidence is out of N30 primary scope.",
        "n30_positive_support_allowed": False,
    },
    "P7": {
        "label": "agentic_participant_blocked",
        "meaning": "Agentic participant, selfhood, intention, and semantic agency remain blocked.",
        "n30_positive_support_allowed": False,
    },
}


MEDIUM_RELATION_LADDER = {
    "M0": {
        "label": "direct_message_passing",
        "meaning": "Sender-receiver scripting or direct message transfer, not shared-medium evidence.",
        "n30_positive_support_allowed": False,
    },
    "M1": {
        "label": "boundary_perturbation",
        "meaning": "Participant perturbs a declared non-private medium surface.",
        "n30_positive_support_allowed": True,
    },
    "M2": {
        "label": "trace_mediated_eligibility_or_influence",
        "meaning": "Medium trace/surface change conditions later eligibility, cost, routing, support, susceptibility, or capacity.",
        "n30_positive_support_allowed": True,
    },
    "M3": {
        "label": "shared_field_co_response_optional_secondary_candidate",
        "meaning": "Multiple participants co-respond through a shared field; optional and not required for N30.",
        "n30_positive_support_allowed": "secondary_candidate_only",
    },
    "M4": {
        "label": "parent_basin_modulation_blocked_future",
        "meaning": "Parent-basin modulation is future work and blocked for N30 positive claims.",
        "n30_positive_support_allowed": False,
    },
    "M5": {
        "label": "resonant_alignment_blocked_future",
        "meaning": "Resonant alignment is future work and blocked for N30 positive claims.",
        "n30_positive_support_allowed": False,
    },
    "M6": {
        "label": "native_shared_medium_organization_blocked_future",
        "meaning": "Native shared-medium organization is not an N30 claim.",
        "n30_positive_support_allowed": False,
    },
}


N30_CLOSEOUT_LADDER = {
    "N30-C0": "initialized_only",
    "N30-C1": "source_method_inventory_passed",
    "N30-C2": "schema_and_active_null_controls_frozen",
    "N30-C3": "participant_admissibility_candidate",
    "N30-C4": "medium_perturbation_trace_candidate",
    "N30-C5": (
        "replay_control_backed_minimal_shared_medium_participation_candidate"
    ),
    "N30-C6": "N31_ready_minimal_shared_medium_participation_closeout",
}


REQUIRED_CANDIDATE_FIELDS = [
    "row_id",
    "source_iteration",
    "primary_layer",
    "participant_ladder_rung",
    "medium_relation_ladder_rung",
    "relation_chain_id",
    "participant_event_id",
    "participant_carrier_id",
    "participant_carrier",
    "participant_persistence_window",
    "participant_attribution_trace",
    "medium_surface_id",
    "medium_surface_carrier",
    "medium_surface_scope",
    "participant_medium_distinct",
    "participant_medium_separation_argument",
    "perturbation_trace",
    "perturbation_event_id",
    "trace_or_surface_change_id",
    "trace_persistence_or_decay",
    "susceptibility_or_eligibility_trace",
    "later_response_event_id",
    "later_response_conditioned_by_medium",
    "later_response_metric",
    "expected_direction",
    "response_window",
    "baseline_window",
    "acceptance_threshold",
    "normalization_denominator",
    "effect_size",
    "counterfactual_row_id",
    "causal_order_verified",
    "trace_dependency_control_ids",
    "medium_ablation_control_result",
    "row_chain_decision",
    "direct_message_present",
    "direct_message_status",
    "medium_debt_record",
    "producer_residue_record",
    "source_current_inputs",
    "artifact_manifest",
    "replay_statuses",
    "control_results",
    "claim_ceiling",
    "blocked_relabels",
    "row_decision",
]


CONTROL_IDS = [
    "direct_message_only_relabel",
    "medium_surface_label_only",
    "hidden_global_controller",
    "hidden_producer_routing",
    "post_hoc_trace_construction",
    "no_perturbation_control",
    "trace_ablation_control",
    "wrong_surface_control",
    "time_reversed_trace_control",
    "medium_freeze_control",
    "trace_shuffle_control",
    "false_trace_injection_control",
    "decay_manipulation_control",
    "susceptibility_inversion_control",
    "participant_label_drift_control",
    "generic_redistribution_relabel",
    "semantic_communication_relabel",
    "semantic_coordination_relabel",
    "cooperation_agency_relabel",
    "native_shared_medium_organization_relabel",
]


BLOCKED_CLAIMS = [
    "shared_medium_coordination",
    "native_shared_medium_organization",
    "parent_basin_modulation",
    "resonant_alignment",
    "semantic_communication",
    "semantic_coordination",
    "cooperation",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_completion",
    "unrestricted_autonomy",
]

HYPOTHESIS_MANIFEST = [
    {
        "hypothesis_id": "Hypothesis A",
        "path": "hypotheses/hypothesis_a_shared_medium_source_basis.md",
        "role": "source_basis_and_method_admission",
    },
    {
        "hypothesis_id": "Hypothesis B",
        "path": "hypotheses/hypothesis_b_minimal_participant_continuity.md",
        "role": "participant_continuity_gate",
    },
    {
        "hypothesis_id": "Hypothesis C",
        "path": "hypotheses/hypothesis_c_medium_trace_eligibility.md",
        "role": "medium_trace_and_later_eligibility_gate",
    },
    {
        "hypothesis_id": "Hypothesis D",
        "path": "hypotheses/hypothesis_d_medium_debt_and_claim_boundary.md",
        "role": "debt_controls_and_claim_boundary_gate",
    },
    {
        "hypothesis_id": "Hypothesis E",
        "path": "hypotheses/hypothesis_e_coupled_shared_medium_relation_chain.md",
        "role": "coupled_relation_chain_gate",
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def build_payload() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    source_inventory = {
        "source_output": "outputs/n30_source_inventory_i1.json",
        "source_output_sha256": sha256_file(I1_OUTPUT),
        "source_output_digest": i1["output_digest"],
        "source_acceptance_state": i1["acceptance_state"],
        "source_ready_for_i2": i1["ready_for_iteration_2_schema_freeze"],
    }
    control_results_schema = {
        "required_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        ],
        "allowed_statuses": [
            "passed",
            "failed_closed",
            "failed_open",
            "not_run",
            "not_applicable",
        ],
        "failed_open_effect": "blocks_row_and_blocks_N30-C5_or_stronger",
        "not_run_effect": "blocks_dependent_rung",
    }
    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "2_participant_medium_schema_freeze",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_participant_medium_schema_controls_frozen_no_positive_evidence",
        "source_inventory": source_inventory,
        "primary_layer": "primitive",
        "positive_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "candidate_rows_classified": False,
        "participant_ladder_rung_assigned": False,
        "medium_relation_ladder_rung_assigned": False,
        "final_n30_closeout_rung": "not_assigned",
        "n30_closeout_ceiling": "N30-C2_schema_and_active_null_controls_frozen",
        "ready_for_iteration_3_active_nulls": True,
        "candidate_required_field_count": len(REQUIRED_CANDIDATE_FIELDS),
        "required_control_count": len(CONTROL_IDS),
        "hypothesis_manifest": HYPOTHESIS_MANIFEST,
        "participant_ladder": PARTICIPANT_LADDER,
        "medium_relation_ladder": MEDIUM_RELATION_LADDER,
        "n30_closeout_ladder": N30_CLOSEOUT_LADDER,
        "candidate_evidence_row_schema": {
            "required_fields": REQUIRED_CANDIDATE_FIELDS,
            "row_decision_allowed_values": [
                "supported",
                "partial",
                "blocked",
                "rejected",
                "not_applicable",
            ],
            "positive_row_requires_derived_report_only_false": True,
            "source_current_inputs_required_for_positive_rows": True,
            "artifact_manifest_required_for_positive_rows": True,
            "all_artifact_sha256_match_file_contents_required": True,
        },
        "coupled_relation_chain_schema": {
            "required_order": [
                "participant_continuity",
                "medium_surface_perturbation",
                "trace_or_surface_change",
                "later_eligibility_or_susceptibility_change",
            ],
            "must_share_relation_chain_id": True,
            "separate_components_without_chain_support": "partial_or_rejected",
            "dependency_requirement": (
                "later response must depend on declared medium surface change"
            ),
            "blocked_explanations": [
                "direct_message",
                "global_controller",
                "hidden_producer",
                "scheduler_drift",
                "post_hoc_trace_construction",
            ],
        },
        "closeout_minimum_rung_policy": {
            "N30-C3": {
                "minimum_participant_rung": "P1",
                "minimum_medium_relation_rung": "not_required",
                "meaning": "participant admissibility candidate only",
            },
            "N30-C4": {
                "minimum_participant_rung": "P1",
                "minimum_medium_relation_rung": "M1",
                "meaning": "medium perturbation / trace candidate only",
            },
            "N30-C5": {
                "minimum_participant_rung": "P2",
                "minimum_medium_relation_rung": "M2",
                "meaning": "replay/control-backed minimal shared-medium participation candidate",
            },
            "N30-C6": {
                "minimum_participant_rung": "P2",
                "minimum_medium_relation_rung": "M2",
                "meaning": "N31-ready minimal shared-medium participation closeout",
            },
        },
        "sharedness_gate": {
            "medium_surface_scope_allowed_values": [
                "private_internal",
                "boundary_accessible",
                "shared_local",
                "shared_global",
                "route_conductance_susceptibility_surface",
                "packet_event_history_surface",
                "parent_surface_candidate",
            ],
            "minimum_scope_for_N30_C5_or_C6": [
                "boundary_accessible",
                "shared_local",
                "shared_global",
                "route_conductance_susceptibility_surface",
                "packet_event_history_surface",
            ],
            "private_internal_effect": (
                "classify_as_medium_mediated_self_aftereffect_candidate_unless_special_case_controls_pass"
            ),
            "parent_surface_candidate_effect": "blocked_for_N30_positive_claims_unless_explicitly_scoped",
            "telemetry_only_surface_policy": {
                "runtime_conditioning_required": True,
                "report_or_log_only_effect": (
                    "classify_as_post_hoc_trace_construction_or_label_only_surface"
                ),
                "packet_event_history_surface_requirement": (
                    "must condition runtime later response, not merely appear in logs"
                ),
            },
        },
        "participant_medium_separation_audit": {
            "participant_medium_distinct_required_for_N30_C5_or_C6": True,
            "same_identifier_blocks_N30_C5_or_C6": True,
            "same_identifier_effect": [
                "internal_aftereffect",
                "medium_only_perturbation",
                "medium_mediated_self_aftereffect_candidate",
                "partial_not_C5_or_C6",
            ],
            "separation_argument_required_if_same_identifier": (
                "allowed_for_explanation_but_not_for_C5_or_C6_closure"
            ),
            "controls_required_to_record_partial_same_identifier_row": [
                "participant_label_drift_control",
                "medium_surface_label_only",
                "trace_ablation_control",
                "wrong_surface_control",
            ],
        },
        "later_response_metric_schema": {
            "predeclared_before_row_classification_required": True,
            "required_fields": [
                "later_response_metric",
                "expected_direction",
                "response_window",
                "baseline_window",
                "acceptance_threshold",
                "normalization_denominator",
                "effect_size",
                "counterfactual_row_id",
            ],
            "post_hoc_difference_effect": (
                "exploratory_only_blocks_N30-C5_and_N30-C6"
            ),
        },
        "medium_debt_schema": {
            "status_allowed_values": [
                "none",
                "medium_surface_producer_mediated",
                "trace_decay_producer_mediated",
                "susceptibility_metric_producer_mediated",
                "naturalization_debt",
                "blocked_relabel",
            ],
            "producer_mediated_effect": (
                "may_support_artifact_level_candidate_but_records_debt_and_cannot_claim_native_shared_medium"
            ),
        },
        "producer_residue_schema": {
            "status_allowed_values": [
                "none",
                "declared_scaffold",
                "direct_message_scaffold",
                "hidden_routing_detected",
                "global_controller_detected",
                "post_hoc_trace_detected",
            ],
            "hidden_residue_effect": "blocks_positive_row",
            "declared_scaffold_effect": "records_debt_without_native_upgrade",
        },
        "controls": {
            "required_control_ids": CONTROL_IDS,
            "control_results_schema": control_results_schema,
            "direct_message_and_hidden_producer_policy": {
                "direct_message_only_relabel": "failed_closed_required_before_positive_support",
                "hidden_global_controller": "failed_closed_required_before_positive_support",
                "hidden_producer_routing": "failed_closed_required_before_positive_support",
                "producer_success_cannot_upgrade_native_shared_medium": True,
            },
        },
        "replay_requirements": {
            "N30_C3_requires": [
                "participant_attribution_replay_or_declared_bounded_window",
            ],
            "N30_C4_requires": [
                "source_current_medium_surface_trace",
                "trace_or_surface_change_reconstruction",
            ],
            "N30_C5_requires": [
                "artifact_only_replay",
                "duplicate_replay",
                "snapshot_load_replay",
                "trace_dependency_controls_failed_closed",
                "later_response_metric_recomputed",
            ],
            "N30_C6_requires": [
                "N30_C5",
                "handoff_grade_contract",
                "declared_transfer_status",
                "declared_medium_and_producer_debt",
                "N31_candidate_interface",
            ],
        },
        "active_null_schema": {
            "required_fields": [
                "null_row_id",
                "null_type",
                "expected_fail_reason",
                "observed_fail_reason",
                "fail_closed",
                "blocked_gate",
                "blocked_rung",
                "dependent_hypothesis",
                "control_equivalent_id",
            ],
            "required_null_ids": CONTROL_IDS,
            "active_null_positive_evidence_allowed": False,
        },
        "n27_n28_guardrail_sufficiency_policy": {
            "inherits_i1_policy": True,
            "source_inventory_policy_key": "guardrail_sufficiency_policy",
            "N27_closeout_guardrail_role": "participant_recognizability_and_transfer_discipline",
            "N28_closeout_guardrail_role": "environment_effect_and_generic_redistribution_boundary",
            "positive_row_rule": (
                "closeout summaries are enough only if they expose the required "
                "guardrail fields; otherwise consume underlying N27/N28 result artifacts"
            ),
            "closeout_summary_alone_can_support_positive_N30_row": False,
        },
        "digest_semantics": {
            "output_digest": "canonical_payload_digest_excluding_output_digest_field",
            "file_sha256": "exact_artifact_file_content_digest",
            "source_output_sha256_scope": "exact_I1_JSON_file_content",
            "source_output_digest_scope": "I1_canonical_payload_digest",
        },
        "claim_boundary": {
            "claim_ceiling": "schema_and_control_freeze_only_no_N30_evidence",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {
                f"{claim}_opened": False for claim in BLOCKED_CLAIMS
            },
        },
    }
    checks = [
        {
            "check_id": "i1_source_inventory_passed",
            "passed": source_inventory["source_acceptance_state"]
            == "accepted_source_inventory_method_admission_no_positive_evidence"
            and source_inventory["source_ready_for_i2"] is True,
        },
        {
            "check_id": "participant_ladder_frozen",
            "passed": list(PARTICIPANT_LADDER) == [f"P{i}" for i in range(8)],
        },
        {
            "check_id": "medium_relation_ladder_frozen",
            "passed": list(MEDIUM_RELATION_LADDER) == [f"M{i}" for i in range(7)],
        },
        {
            "check_id": "n30_closeout_ladder_frozen",
            "passed": list(N30_CLOSEOUT_LADDER)
            == [f"N30-C{i}" for i in range(7)],
        },
        {
            "check_id": "candidate_required_fields_present",
            "passed": len(REQUIRED_CANDIDATE_FIELDS) == 46,
        },
        {
            "check_id": "coupled_relation_chain_requirement_frozen",
            "passed": payload["coupled_relation_chain_schema"]["must_share_relation_chain_id"]
            is True
            and len(payload["coupled_relation_chain_schema"]["required_order"]) == 4,
        },
        {
            "check_id": "sharedness_gate_blocks_private_internal",
            "passed": "private_internal"
            in payload["sharedness_gate"]["medium_surface_scope_allowed_values"]
            and "self_aftereffect"
            in payload["sharedness_gate"]["private_internal_effect"],
        },
        {
            "check_id": "participant_medium_separation_audit_frozen",
            "passed": payload["participant_medium_separation_audit"][
                "participant_medium_distinct_required_for_N30_C5_or_C6"
            ]
            is True
            and payload["participant_medium_separation_audit"][
                "same_identifier_blocks_N30_C5_or_C6"
            ]
            is True,
        },
        {
            "check_id": "C5_C6_minimum_rung_policy_frozen",
            "passed": payload["closeout_minimum_rung_policy"]["N30-C5"][
                "minimum_participant_rung"
            ]
            == "P2"
            and payload["closeout_minimum_rung_policy"]["N30-C5"][
                "minimum_medium_relation_rung"
            ]
            == "M2"
            and payload["closeout_minimum_rung_policy"]["N30-C6"][
                "minimum_participant_rung"
            ]
            == "P2"
            and payload["closeout_minimum_rung_policy"]["N30-C6"][
                "minimum_medium_relation_rung"
            ]
            == "M2",
        },
        {
            "check_id": "telemetry_only_medium_surfaces_blocked",
            "passed": payload["sharedness_gate"]["telemetry_only_surface_policy"][
                "runtime_conditioning_required"
            ]
            is True,
        },
        {
            "check_id": "later_response_metrics_predeclared",
            "passed": payload["later_response_metric_schema"][
                "predeclared_before_row_classification_required"
            ]
            is True,
        },
        {
            "check_id": "controls_cover_plan_required_ids",
            "passed": set(CONTROL_IDS)
            == set(payload["active_null_schema"]["required_null_ids"]),
        },
        {
            "check_id": "active_null_gate_mapping_fields_required",
            "passed": all(
                field in payload["active_null_schema"]["required_fields"]
                for field in [
                    "blocked_gate",
                    "blocked_rung",
                    "dependent_hypothesis",
                    "control_equivalent_id",
                ]
            ),
        },
        {
            "check_id": "replay_requirements_block_C5_until_replay_controls",
            "passed": "trace_dependency_controls_failed_closed"
            in payload["replay_requirements"]["N30_C5_requires"],
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
        },
        {
            "check_id": "no_positive_evidence_opened",
            "passed": payload["positive_evidence_opened"] is False
            and payload["candidate_rows_classified"] is False,
        },
    ]
    payload["checks"] = checks
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        }
    )
    payload["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    def report_value(value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    participant_rows = "\n".join(
        f"| {rung} | {entry['label']} | {report_value(entry['n30_positive_support_allowed'])} |"
        for rung, entry in payload["participant_ladder"].items()
    )
    medium_rows = "\n".join(
        f"| {rung} | {entry['label']} | {report_value(entry['n30_positive_support_allowed'])} |"
        for rung, entry in payload["medium_relation_ladder"].items()
    )
    control_rows = "\n".join(
        f"- `{control_id}`" for control_id in payload["controls"]["required_control_ids"]
    )
    hypothesis_rows = "\n".join(
        f"- {entry['hypothesis_id']}: `{entry['role']}`"
        for entry in payload["hypothesis_manifest"]
    )
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    text = f"""# N30 Iteration 2 - Participant / Medium Schema Freeze

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 2 freezes the contract that later positive rows must obey. It assigns
no participant rung, no medium-relation rung, and no final closeout rung.

## Participant Ladder

| Rung | Label | N30 Positive Support |
|---|---|---|
{participant_rows}

## Shared-Medium Relation Ladder

| Rung | Label | N30 Positive Support |
|---|---|---|
{medium_rows}

## Coupled Relation Chain

A later row cannot close at N30-C5 or N30-C6 unless one causal lineage links:

```text
participant continuity
medium surface perturbation
trace or surface change
later eligibility / susceptibility / cost / routing / support / capacity change
```

Separate components without ordered dependency are partial or rejected.

## Minimum Rung Policy

```text
N30-C3 may close with P1.
N30-C4 may close with P1 + M1.
N30-C5 and N30-C6 require P2 + M2.
```

This keeps boundary perturbation from being promoted into trace-mediated
shared-medium participation. M1 is necessary for N30-C4, but it is not
sufficient for C5/C6 without later eligibility or susceptibility dependence.

## Separation And Telemetry Policies

```text
same participant_carrier_id == medium_surface_id blocks N30-C5/C6
```

Same-identifier rows may be recorded as internal aftereffect,
medium-mediated self-aftereffect, or partial rows, but not as minimal
shared-medium participation closeout evidence.

Telemetry-only surfaces are also blocked. A packet/event history surface must
condition runtime later response; if it exists only as a report or log artifact,
it is classified as post-hoc trace construction or label-only surface.

## Controls Frozen

{control_rows}

## Hypothesis Linkage

I3 active nulls and later positive rows should reference these hypothesis IDs
through `dependent_hypothesis`:

{hypothesis_rows}

## Checks

{check_rows}

## Claim Boundary

`minimal_shared_medium_participation_claim_allowed = false`

`shared_medium_coordination_claim_allowed = false`

`native_shared_medium_organization_claim_allowed = false`
"""
    REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N30 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
I2_OUTPUT = EXPERIMENT / "outputs" / "n30_schema_control_freeze_i2.json"
OUTPUT = EXPERIMENT / "outputs" / "n30_active_nulls_i3.json"
REPORT = EXPERIMENT / "reports" / "n30_active_nulls_i3.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_active_nulls_i3.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"


NULL_SPECS: list[dict[str, Any]] = [
    {
        "control_id": "direct_message_only_relabel",
        "false_positive_path": "direct sender-receiver packet relabeled as shared medium",
        "blocked_gate": "medium_surface_non_private_trace_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "direct message path lacks declared medium-surface conditioning",
        "observed_fail_reason": "direct_message_present=true and direct_message_status=direct_only_blocks_M2",
        "unsafe_if_accepted": "message passing would be promoted into shared-medium participation",
    },
    {
        "control_id": "medium_surface_label_only",
        "false_positive_path": "surface name exists but no source-current medium surface change exists",
        "blocked_gate": "declared_medium_surface_trace_gate",
        "blocked_rung": "N30-C4",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "label-only surface cannot satisfy perturbation or trace gate",
        "observed_fail_reason": "medium_surface_id is label-only and trace_or_surface_change_id is missing",
        "unsafe_if_accepted": "surface vocabulary would replace source-current medium evidence",
    },
    {
        "control_id": "hidden_global_controller",
        "false_positive_path": "global controller changes later eligibility outside the medium surface",
        "blocked_gate": "later_response_depends_on_medium_trace",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis E",
        "expected_fail_reason": "later response is controller-carried instead of trace-carried",
        "observed_fail_reason": "hidden_global_controller_detected=true and relation_chain_dependency=false",
        "unsafe_if_accepted": "central orchestration would be mistaken for shared-medium causality",
    },
    {
        "control_id": "hidden_producer_routing",
        "false_positive_path": "producer routes later response without visible medium dependency",
        "blocked_gate": "producer_residue_and_trace_dependency_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "hidden producer routing blocks artifact-level relation-chain support",
        "observed_fail_reason": "producer_residue_status=hidden_routing_detected",
        "unsafe_if_accepted": "producer routing would be counted as substrate medium influence",
    },
    {
        "control_id": "post_hoc_trace_construction",
        "false_positive_path": "trace is assembled from report/log after outcome inspection",
        "blocked_gate": "source_current_trace_gate",
        "blocked_rung": "N30-C4",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "post-hoc trace cannot count as medium surface state",
        "observed_fail_reason": "trace_declared_after_later_response=true",
        "unsafe_if_accepted": "telemetry-only or report-only trace would pass as runtime medium",
    },
    {
        "control_id": "no_perturbation_control",
        "false_positive_path": "later difference appears with no participant-caused perturbation",
        "blocked_gate": "participant_to_medium_perturbation_gate",
        "blocked_rung": "N30-C4",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "medium trace requires a perturbation event",
        "observed_fail_reason": "perturbation_event_id=missing and participant_attribution_trace=absent",
        "unsafe_if_accepted": "ambient change would be promoted into participation",
    },
    {
        "control_id": "trace_ablation_control",
        "false_positive_path": "later eligibility still claimed after declared trace removal",
        "blocked_gate": "later_response_depends_on_medium_trace",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis E",
        "expected_fail_reason": "trace must be necessary for the later response dependency",
        "observed_fail_reason": "trace_ablation_breaks_dependency=true",
        "unsafe_if_accepted": "unnecessary trace would be treated as causal medium evidence",
    },
    {
        "control_id": "wrong_surface_control",
        "false_positive_path": "dependency is attributed to an unrelated medium surface",
        "blocked_gate": "declared_surface_specificity_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "later response must depend on the declared changed surface",
        "observed_fail_reason": "wrong_surface_substitution_fails_dependency=true",
        "unsafe_if_accepted": "generic field change would replace surface-specific evidence",
    },
    {
        "control_id": "time_reversed_trace_control",
        "false_positive_path": "later response is used to explain an earlier trace",
        "blocked_gate": "causal_order_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis E",
        "expected_fail_reason": "ordered lineage must be participant -> perturbation -> trace -> later response",
        "observed_fail_reason": "causal_order_verified=false_under_time_reversal",
        "unsafe_if_accepted": "post-outcome ordering would masquerade as trace dependency",
    },
    {
        "control_id": "medium_freeze_control",
        "false_positive_path": "medium surface is frozen yet later response is still claimed",
        "blocked_gate": "medium_surface_change_gate",
        "blocked_rung": "N30-C4",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "surface state must change or leave a trace",
        "observed_fail_reason": "medium_surface_frozen=true and trace_or_surface_change_id=missing",
        "unsafe_if_accepted": "unchanged medium would count as changed shared surface",
    },
    {
        "control_id": "trace_shuffle_control",
        "false_positive_path": "trace is shuffled across unrelated chains while retaining the label",
        "blocked_gate": "relation_chain_identity_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis E",
        "expected_fail_reason": "trace must stay in the same relation_chain_id",
        "observed_fail_reason": "trace_shuffle_breaks_relation_chain=true",
        "unsafe_if_accepted": "unordered trace association would replace coupled lineage",
    },
    {
        "control_id": "false_trace_injection_control",
        "false_positive_path": "injected trace is used as evidence without participant perturbation",
        "blocked_gate": "trace_provenance_gate",
        "blocked_rung": "N30-C4",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "trace provenance must point to the participant perturbation",
        "observed_fail_reason": "false_trace_injected=true and perturbation_trace_link=false",
        "unsafe_if_accepted": "injected trace would be counted as source-current medium change",
    },
    {
        "control_id": "decay_manipulation_control",
        "false_positive_path": "trace persistence is created by manipulating decay after the outcome",
        "blocked_gate": "trace_persistence_or_decay_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "trace persistence/decay must be declared before classification",
        "observed_fail_reason": "decay_schedule_post_hoc_or_manipulated=true",
        "unsafe_if_accepted": "post-hoc decay tuning would create fake medium memory",
    },
    {
        "control_id": "susceptibility_inversion_control",
        "false_positive_path": "later response changes opposite to the predeclared direction",
        "blocked_gate": "predeclared_later_response_metric_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis C",
        "expected_fail_reason": "later-response metric must match predeclared direction and threshold",
        "observed_fail_reason": "expected_direction_violated=true",
        "unsafe_if_accepted": "any downstream difference would be treated as eligibility dependency",
    },
    {
        "control_id": "participant_label_drift_control",
        "false_positive_path": "participant carrier changes identity while retaining participant label",
        "blocked_gate": "participant_carrier_continuity_gate",
        "blocked_rung": "N30-C3",
        "dependent_hypothesis": "Hypothesis B",
        "expected_fail_reason": "participant carrier must remain recognizable for P2",
        "observed_fail_reason": "participant_label_persisted_but_carrier_digest_changed=true",
        "unsafe_if_accepted": "label persistence would replace participant continuity",
    },
    {
        "control_id": "generic_redistribution_relabel",
        "false_positive_path": "generic redistribution is relabeled as shared-medium eligibility",
        "blocked_gate": "N28_environment_effect_distinction_gate",
        "blocked_rung": "N30-C5",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "environment change must be specific trace-mediated eligibility, not generic redistribution",
        "observed_fail_reason": "redistribution_specific_trace_dependency=false",
        "unsafe_if_accepted": "N28-style environment reshaping would be overpromoted into shared medium",
    },
    {
        "control_id": "semantic_communication_relabel",
        "false_positive_path": "trace influence is relabeled as semantic communication",
        "blocked_gate": "claim_boundary_gate",
        "blocked_rung": "N30-C6",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "N30 blocks semantic communication claims",
        "observed_fail_reason": "semantic_content_evidence=absent",
        "unsafe_if_accepted": "minimal trace relation would become communication",
    },
    {
        "control_id": "semantic_coordination_relabel",
        "false_positive_path": "co-response vocabulary is relabeled as semantic coordination",
        "blocked_gate": "claim_boundary_gate",
        "blocked_rung": "N30-C6",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "N30 blocks shared-medium coordination claims",
        "observed_fail_reason": "coordination_protocol_evidence=absent",
        "unsafe_if_accepted": "minimal shared-medium participation would become coordination",
    },
    {
        "control_id": "cooperation_agency_relabel",
        "false_positive_path": "participant relation is relabeled as cooperation or agency",
        "blocked_gate": "claim_boundary_gate",
        "blocked_rung": "N30-C6",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "N30 blocks cooperation, agency, selfhood, and identity claims",
        "observed_fail_reason": "agency_intention_goal_evidence=absent",
        "unsafe_if_accepted": "minimal participant relation would become agency-like behavior",
    },
    {
        "control_id": "native_shared_medium_organization_relabel",
        "false_positive_path": "artifact-level medium trace is relabeled as native shared-medium organization",
        "blocked_gate": "native_shared_medium_claim_boundary_gate",
        "blocked_rung": "N30-C6",
        "dependent_hypothesis": "Hypothesis D",
        "expected_fail_reason": "N30 explicitly blocks native shared-medium organization",
        "observed_fail_reason": "native_organization_evidence=absent_and_medium_debt_not_closed",
        "unsafe_if_accepted": "artifact-level primitive would become native shared-medium organization",
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


def build_null_row(index: int, spec: dict[str, Any]) -> dict[str, Any]:
    control_id = spec["control_id"]
    return {
        "null_row_id": f"n30_i3_null_{index:02d}_{control_id}",
        "null_type": control_id,
        "control_equivalent_id": control_id,
        "false_positive_path": spec["false_positive_path"],
        "expected_fail_reason": spec["expected_fail_reason"],
        "observed_fail_reason": spec["observed_fail_reason"],
        "observation_source": "pre_positive_synthetic_active_null_fixture",
        "observed_fail_reason_semantics": (
            "declared_expected_fail_condition_not_runtime_measurement"
        ),
        "fail_closed": True,
        "failed_open": False,
        "blocked_gate": spec["blocked_gate"],
        "blocked_rung": spec["blocked_rung"],
        "dependent_hypothesis": spec["dependent_hypothesis"],
        "unsafe_if_accepted": spec["unsafe_if_accepted"],
        "schema_instantiation_only": True,
        "active_null_fixture_only": True,
        "derived_report_only": True,
        "positive_evidence_admissible": False,
        "source_current_inputs": [],
        "artifact_manifest": [],
        "participant_ladder_rung_assigned": False,
        "medium_relation_ladder_rung_assigned": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "row_decision": "rejected_failed_closed_active_null",
    }


def build_payload() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    required_null_ids = i2["active_null_schema"]["required_null_ids"]
    null_rows = [build_null_row(index, spec) for index, spec in enumerate(NULL_SPECS, 1)]
    observed_null_ids = [row["null_type"] for row in null_rows]
    required_null_fields = i2["active_null_schema"]["required_fields"]
    null_fixture_config = {
        "source_i2_output_digest": i2["output_digest"],
        "required_null_ids": required_null_ids,
        "required_null_fields": required_null_fields,
    }
    null_generation_policy = {
        "null_specs": NULL_SPECS,
        "row_builder": "build_null_row",
        "positive_evidence_admissible": False,
        "artifact_manifest_policy": "empty_for_active_null_fixture_only",
    }
    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "3_active_nulls_and_failure_baselines",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_evidence",
        "source_schema": {
            "source_output": "outputs/n30_schema_control_freeze_i2.json",
            "source_output_sha256": sha256_file(I2_OUTPUT),
            "source_output_digest": i2["output_digest"],
            "source_acceptance_state": i2["acceptance_state"],
            "required_null_id_count": len(required_null_ids),
            "required_null_fields": required_null_fields,
        },
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
        "active_null_count": len(null_rows),
        "failed_closed_count": sum(1 for row in null_rows if row["fail_closed"]),
        "failed_open_rows": [
            row["null_row_id"] for row in null_rows if row["failed_open"]
        ],
        "positive_evidence_admissible": False,
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "observed_fail_reason_policy": {
            "field_name_preserved_from_i2_schema": "observed_fail_reason",
            "observation_source": "pre_positive_synthetic_active_null_fixture",
            "meaning": (
                "I3 observed_fail_reason values are declared fail-closed fixture "
                "conditions, not measurements from runtime controls"
            ),
            "i7_runtime_controls_required_for_positive_candidates": True,
        },
        "ready_for_iteration_4_participant_admissibility_probe": True,
        "null_fixture_reproducibility": {
            "null_fixture_id": "n30_i3_pre_positive_active_null_fixture",
            "null_fixture_config_digest": digest_value(null_fixture_config),
            "null_generation_policy_digest": digest_value(null_generation_policy),
            "artifact_manifest_policy": "empty_manifest_allowed_only_because_positive_evidence_admissible_false",
            "runtime_artifacts_required_for_positive_rows": True,
        },
        "i3_to_i7_control_policy": {
            "i3_nulls_define_false_positive_paths": True,
            "i3_nulls_substitute_for_i7_runtime_controls": False,
            "i7_must_rerun_or_reinstantiate_equivalent_controls_against_positive_candidates": True,
            "covered_by_i3_alone_blocks_positive_candidate_validation": True,
        },
        "i4_participant_only_ceiling_guard": {
            "i4_maximum_closeout_ceiling": "N30-C3_participant_admissibility_candidate",
            "i4_medium_relation_rung_assignment_allowed": False,
            "i4_medium_perturbation_claim_allowed": False,
            "i4_trace_mediated_eligibility_claim_allowed": False,
            "i4_minimal_shared_medium_participation_claim_allowed": False,
            "exploratory_medium_observation_effect": "record_only_not_C4_or_C5_support",
            "required_i4_fields": [
                "participant_carrier_id",
                "participant_carrier_type",
                "participant_persistence_window",
                "participant_start_state_digest",
                "participant_end_state_digest",
                "participant_attribution_trace",
                "recognizability_metric",
                "recognizability_threshold",
                "replay_status",
                "label_drift_control_result",
                "claim_ceiling",
                "blocked_relabels",
            ],
            "same_label_is_not_same_carrier": True,
            "carrier_digest_or_trace_continuity_required": True,
        },
        "active_null_rows": null_rows,
        "gate_mapping_summary": {
            "blocked_gates": sorted({row["blocked_gate"] for row in null_rows}),
            "blocked_rungs": sorted({row["blocked_rung"] for row in null_rows}),
            "dependent_hypotheses": sorted({row["dependent_hypothesis"] for row in null_rows}),
        },
        "i3_consumption_rule": {
            "may_consume_as": [
                "pre_positive_false_positive_blocker_matrix",
                "I4_I6_admission_gate_context",
                "claim_boundary_control_context",
            ],
            "must_not_consume_as": [
                "participant_admissibility_evidence",
                "medium_surface_trace_evidence",
                "later_eligibility_dependency_evidence",
                "N30-C5_or_C6_support",
            ],
        },
        "claim_boundary": {
            "claim_ceiling": "active_nulls_fail_closed_no_positive_N30_evidence",
            "blocked_claims": i2["claim_boundary"]["blocked_claims"],
            "unsafe_claim_flags": i2["claim_boundary"]["unsafe_claim_flags"],
        },
    }
    checks = [
        {
            "check_id": "i2_schema_freeze_passed",
            "passed": i2["acceptance_state"]
            == "accepted_participant_medium_schema_controls_frozen_no_positive_evidence",
        },
        {
            "check_id": "all_required_null_ids_present_once",
            "passed": sorted(observed_null_ids) == sorted(required_null_ids)
            and len(observed_null_ids) == len(set(observed_null_ids)),
        },
        {
            "check_id": "all_required_null_fields_present",
            "passed": all(
                all(field in row for field in required_null_fields)
                for row in null_rows
            ),
        },
        {
            "check_id": "all_nulls_fail_closed",
            "passed": all(row["fail_closed"] is True for row in null_rows),
        },
        {
            "check_id": "no_failed_open_rows",
            "passed": payload["failed_open_rows"] == [],
        },
        {
            "check_id": "nulls_map_to_specific_gates_and_rungs",
            "passed": all(
                row["blocked_gate"] and row["blocked_rung"] for row in null_rows
            ),
        },
        {
            "check_id": "nulls_reference_hypotheses",
            "passed": all(
                row["dependent_hypothesis"]
                in {"Hypothesis B", "Hypothesis C", "Hypothesis D", "Hypothesis E"}
                for row in null_rows
            ),
        },
        {
            "check_id": "no_positive_evidence_opened",
            "passed": payload["positive_evidence_opened"] is False
            and payload["candidate_rows_classified"] is False,
        },
        {
            "check_id": "active_nulls_not_runtime_artifacts",
            "passed": all(
                row["derived_report_only"] is True
                and row["source_current_inputs"] == []
                and row["artifact_manifest"] == []
                for row in null_rows
            ),
        },
        {
            "check_id": "observed_fail_reasons_marked_synthetic",
            "passed": all(
                row["observation_source"]
                == "pre_positive_synthetic_active_null_fixture"
                and row["observed_fail_reason_semantics"]
                == "declared_expected_fail_condition_not_runtime_measurement"
                for row in null_rows
            ),
        },
        {
            "check_id": "null_fixture_reproducibility_digests_present",
            "passed": bool(
                payload["null_fixture_reproducibility"]["null_fixture_config_digest"]
            )
            and bool(
                payload["null_fixture_reproducibility"][
                    "null_generation_policy_digest"
                ]
            ),
        },
        {
            "check_id": "i3_nulls_do_not_substitute_for_i7_runtime_controls",
            "passed": payload["i3_to_i7_control_policy"][
                "i3_nulls_substitute_for_i7_runtime_controls"
            ]
            is False
            and payload["i3_to_i7_control_policy"][
                "i7_must_rerun_or_reinstantiate_equivalent_controls_against_positive_candidates"
            ]
            is True,
        },
        {
            "check_id": "i4_ceiling_guard_blocks_medium_evidence",
            "passed": payload["i4_participant_only_ceiling_guard"][
                "i4_medium_relation_rung_assignment_allowed"
            ]
            is False
            and payload["i4_participant_only_ceiling_guard"][
                "i4_trace_mediated_eligibility_claim_allowed"
            ]
            is False,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
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
    row_table = "\n".join(
        "| {null_type} | {blocked_gate} | {blocked_rung} | {hypothesis} | {fail_closed} |".format(
            null_type=row["null_type"],
            blocked_gate=row["blocked_gate"],
            blocked_rung=row["blocked_rung"],
            hypothesis=row["dependent_hypothesis"],
            fail_closed=str(row["fail_closed"]).lower(),
        )
        for row in payload["active_null_rows"]
    )
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    text = f"""# N30 Iteration 3 - Active Nulls And Failure Baselines

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 3 instantiates the false-positive boundary from the I2 schema. These
rows can block unsafe paths, but they cannot support participant admissibility,
medium trace evidence, later eligibility dependency, or N30-C5/C6.

`failed_closed` means the blocker triggered and the claim was rejected.
`failed_open` would mean the blocker triggered but the row still passed.

## Null Rows

| Null | Blocked Gate | Blocked Rung | Hypothesis | Failed Closed |
|---|---|---|---|---:|
{row_table}

## Interpretation

The nulls make the relation-chain boundary explicit. A later positive row
cannot pass by combining participant labels, trace labels, or later differences
after the fact. Direct messages, hidden producers, global controllers,
post-hoc traces, wrong surfaces, time reversal, trace shuffling, false trace
injection, decay manipulation, participant label drift, generic redistribution,
and semantic relabels all fail closed before any positive N30 probe runs.

## Fixture And Control Policy

```text
null_fixture_id = {payload['null_fixture_reproducibility']['null_fixture_id']}
null_fixture_config_digest = {payload['null_fixture_reproducibility']['null_fixture_config_digest']}
null_generation_policy_digest = {payload['null_fixture_reproducibility']['null_generation_policy_digest']}
```

I3 nulls are pre-positive false-positive blockers. They do not substitute for
I7 runtime controls. I7 must rerun or reinstantiate equivalent controls against
the actual I4-I6 positive candidate fixture; `covered_by_i3` alone blocks
positive candidate validation.

The `observed_fail_reason` field is preserved because I2 requires it, but in
I3 its observation source is `pre_positive_synthetic_active_null_fixture`. These
values are declared fail-closed fixture conditions, not runtime measurements.

## I4 Ceiling Guard

I4 may test only participant admissibility. Its maximum ceiling is
`N30-C3_participant_admissibility_candidate`. I4 cannot assign a medium-relation
rung, medium perturbation claim, trace-mediated eligibility claim, or minimal
shared-medium participation claim. Any medium observation in I4 is exploratory
only and cannot support N30-C4 or N30-C5.

I4 must distinguish same label from same carrier by recording carrier digest or
trace continuity, recognizability metric, recognizability threshold, replay
status, and label-drift control result.

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

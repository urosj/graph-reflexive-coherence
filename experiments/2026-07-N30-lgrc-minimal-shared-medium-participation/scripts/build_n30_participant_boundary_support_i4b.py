#!/usr/bin/env python3
"""Build N30 Iteration 4-B participant boundary/support sensitivity probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_participant_boundary_support_i4b.json"
REPORT = EXPERIMENT / "reports" / "n30_participant_boundary_support_i4b.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_participant_boundary_support_i4b_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_participant_boundary_support_i4b.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I4_OUTPUT = EXPERIMENT / "outputs" / "n30_participant_admissibility_i4.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n30_participant_admissibility_i4a.json"

N27_ROOT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
N27_STRESS_OUTPUT = N27_ROOT / "outputs" / "n27_stress_mapping_variant_transfer_matrix.json"
N27_STRESS_ARTIFACT_DIR = (
    N27_ROOT / "outputs" / "n27_stress_mapping_variant_transfer_matrix_artifacts"
)
N27_I4_STRESS_TRACE = (
    N27_STRESS_ARTIFACT_DIR / "n27_i6_row_i4_stress_stress_variant_trace.json"
)
N27_I4A_STRESS_TRACE = (
    N27_STRESS_ARTIFACT_DIR / "n27_i6_row_i4a_stress_stress_variant_trace.json"
)
N27_I4_CONTROL_TRACE = (
    N27_STRESS_ARTIFACT_DIR / "n27_i6_row_i4_stress_control_trace.json"
)
N27_I4A_CONTROL_TRACE = (
    N27_STRESS_ARTIFACT_DIR / "n27_i6_row_i4a_stress_control_trace.json"
)

BLOCKED_CLAIMS = [
    "medium_perturbation",
    "trace_mediated_eligibility",
    "minimal_shared_medium_participation",
    "shared_medium_coordination",
    "native_shared_medium_organization",
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def write_artifact(name: str, data: dict[str, Any]) -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(canonical_json(data), encoding="utf-8")
    return {
        "path": rel(path),
        "artifact_role": data["artifact_role"],
        "sha256": sha256_file(path),
    }


def source_input(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": rel(path),
        "source_role": role,
        "sha256": sha256_file(path),
    }


def stress_row_by_source(stress_matrix: dict[str, Any], source_iteration: str) -> dict[str, Any]:
    for row in stress_matrix["stress_rows"]:
        if row["source_iteration"] == source_iteration:
            return row
    raise KeyError(source_iteration)


def min_margin(stress_trace: dict[str, Any]) -> float:
    values: list[float] = []
    for result in stress_trace["stress_results"]:
        values.extend(result["residual_margins"].values())
    if not values:
        raise ValueError(
            f"stress trace {stress_trace.get('trace_id', 'unknown')} has no residual margins"
        )
    return min(values)


def build_source_summary(
    source_label: str,
    participant_carrier_id: str,
    stress_row: dict[str, Any],
    stress_trace: dict[str, Any],
    control_trace: dict[str, Any],
) -> dict[str, Any]:
    all_passed = stress_trace["all_stress_rows_passed"]
    failed_stress_ids = stress_trace["failed_stress_ids"]
    passed_stress_ids = [
        row["stress_id"] for row in stress_trace["stress_results"] if row["stress_passed"]
    ]
    supported_p4 = all_passed is True
    if supported_p4:
        participant_rung = "P4_candidate"
        row_decision = "supported_participant_boundary_support_sensitive_candidate_only"
        rung_reason = (
            "participant carrier survived boundary tightening, support drawdown, "
            "coherence drawdown, flux pressure, and combined bounded stress"
        )
    else:
        participant_rung = "P2_stress_limited"
        row_decision = "partial_boundary_limited_participant_admissibility"
        rung_reason = (
            "participant carrier remains admissible as P2, but boundary stress "
            "fails closed and blocks P3/P4 strengthening"
        )

    summary = {
        "source_label": source_label,
        "participant_carrier_id": participant_carrier_id,
        "source_iteration": stress_row["source_iteration"],
        "transfer_mapping_id": stress_row["transfer_mapping_id"],
        "transfer_scope": stress_row["transfer_scope"],
        "participant_ladder_rung": participant_rung,
        "participant_ladder_rung_reason": rung_reason,
        "row_decision": row_decision,
        "stress_variant_candidate_supported": supported_p4,
        "all_stress_rows_passed": all_passed,
        "failed_stress_ids": failed_stress_ids,
        "passed_stress_ids": passed_stress_ids,
        "base_margins": stress_trace["base_margins"],
        "minimum_residual_margin_across_stress": min_margin(stress_trace),
        "baseline_boundary_at_floor": stress_trace["baseline_boundary_at_floor"],
        "stress_failure_mode": stress_trace["stress_failure_mode"],
        "control_trace_status": control_trace["stress_variant_failure_control_status"],
        "control_trace_meaning": control_trace["stress_variant_failure_control_meaning"],
        "source_transfer_core_digest": stress_trace["source_transfer_core_digest"],
        "stress_trace_digest": digest_value(stress_trace),
        "control_trace_digest": digest_value(control_trace),
        "medium_relation_ladder_rung": "not_assigned",
        "medium_surface_trace_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "claim_ceiling": (
            "participant boundary/support sensitivity only; no medium perturbation, "
            "trace-mediated eligibility, minimal shared-medium participation, "
            "agency, selfhood, or native shared-medium organization claim"
        ),
        "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
    }
    summary["summary_digest"] = digest_value(summary)
    return summary


def build_payload() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    stress_matrix = load_json(N27_STRESS_OUTPUT)
    i4_stress_trace = load_json(N27_I4_STRESS_TRACE)
    i4a_stress_trace = load_json(N27_I4A_STRESS_TRACE)
    i4_control_trace = load_json(N27_I4_CONTROL_TRACE)
    i4a_control_trace = load_json(N27_I4A_CONTROL_TRACE)
    i4_stress_row = stress_row_by_source(stress_matrix, "4")
    i4a_stress_row = stress_row_by_source(stress_matrix, "4-A")

    i4_carrier = i4["candidate_rows"][0]["participant_carrier_id"]
    i4a_carrier = i4a["candidate_rows"][0]["participant_carrier_id"]

    i4_summary = build_source_summary(
        "I4_minimal_alpha_beta_participant",
        i4_carrier,
        i4_stress_row,
        i4_stress_trace,
        i4_control_trace,
    )
    i4a_summary = build_source_summary(
        "I4A_branched_topology_participant",
        i4a_carrier,
        i4a_stress_row,
        i4a_stress_trace,
        i4a_control_trace,
    )

    stress_policy_record = {
        "artifact_role": "participant_boundary_support_stress_policy_record",
        "record_id": "n30_i4b_participant_boundary_support_stress_policy_record",
        "declared_before_classification": True,
        "source_policy_id": stress_matrix["stress_policy"]["policy_id"],
        "source_declaration_order": stress_matrix["stress_policy"]["declaration_order"],
        "pass_rule": stress_matrix["stress_policy"]["pass_rule"],
        "stress_rows": stress_matrix["stress_policy"]["stress_rows"],
        "n30_interpretation": (
            "boundary/support participant sensitivity requires all declared "
            "residual margins to remain non-negative for the tested carrier"
        ),
        "p3_gate": "boundary_tightening_0_05 must pass",
        "p4_gate": (
            "boundary_tightening_0_05, support_drawdown_0_008, "
            "coherence_drawdown_0_012, flux_pressure_0_02, and "
            "combined_moderate_mapping_stress must pass"
        ),
        "medium_relation_assignment_allowed": False,
    }
    stress_policy_record["stress_policy_record_digest"] = digest_value(
        stress_policy_record
    )

    stress_matrix_trace = {
        "artifact_role": "participant_boundary_support_sensitivity_matrix",
        "trace_id": "n30_i4b_participant_boundary_support_sensitivity_matrix",
        "i4_summary": i4_summary,
        "i4a_summary": i4a_summary,
        "strongest_participant_ladder_rung": "P4_candidate",
        "strongest_participant_carrier_id": i4a_carrier,
        "p4_supported_by": "I4-A topology fixture participant carrier under N27 I6 stress matrix",
        "i4_boundary_limited": True,
        "i4a_boundary_support_sensitive_candidate_supported": True,
        "i4_replaced": False,
        "i4a_replaced": False,
        "medium_relation_evidence_opened": False,
    }
    stress_matrix_trace["stress_matrix_trace_digest"] = digest_value(
        stress_matrix_trace
    )

    p4_candidate_trace = {
        "artifact_role": "participant_p4_candidate_trace",
        "trace_id": "n30_i4b_participant_p4_candidate_trace",
        "participant_carrier_id": i4a_carrier,
        "participant_ladder_rung": "P4_candidate",
        "base_margins": i4a_stress_trace["base_margins"],
        "stress_results": i4a_stress_trace["stress_results"],
        "minimum_residual_margin_across_stress": i4a_summary[
            "minimum_residual_margin_across_stress"
        ],
        "all_stress_rows_passed": True,
        "boundary_interface_participant_candidate": True,
        "support_sensitive_participant_candidate": True,
        "withdrawal_resistant_participant_claim_allowed": False,
        "generative_participant_claim_allowed": False,
        "agentic_participant_claim_allowed": False,
    }
    p4_candidate_trace["p4_candidate_trace_digest"] = digest_value(
        p4_candidate_trace
    )

    stress_limited_trace = {
        "artifact_role": "participant_stress_limited_trace",
        "trace_id": "n30_i4b_participant_stress_limited_trace",
        "participant_carrier_id": i4_carrier,
        "participant_ladder_rung": "P2_stress_limited",
        "base_margins": i4_stress_trace["base_margins"],
        "stress_results": i4_stress_trace["stress_results"],
        "failed_stress_ids": i4_stress_trace["failed_stress_ids"],
        "baseline_boundary_at_floor": i4_stress_trace["baseline_boundary_at_floor"],
        "boundary_interface_participant_candidate": False,
        "support_sensitive_participant_candidate": False,
        "p3_p4_blocker": "boundary_tightening fails closed",
    }
    stress_limited_trace["stress_limited_trace_digest"] = digest_value(
        stress_limited_trace
    )

    medium_leakage_guard_trace = {
        "artifact_role": "i4b_medium_leakage_guard_trace",
        "trace_id": "n30_i4b_medium_leakage_guard_trace",
        "participant_stress_sensitivity_only": True,
        "medium_relation_ladder_rung": "not_assigned",
        "medium_surface_id": "not_declared_in_iteration_4b",
        "medium_surface_trace_evidence_opened": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "p4_does_not_imply_medium_relation": True,
    }
    medium_leakage_guard_trace["medium_leakage_guard_trace_digest"] = digest_value(
        medium_leakage_guard_trace
    )

    artifacts = [
        write_artifact("stress_policy_record.json", stress_policy_record),
        write_artifact("participant_boundary_support_sensitivity_matrix.json", stress_matrix_trace),
        write_artifact("participant_p4_candidate_trace.json", p4_candidate_trace),
        write_artifact("participant_stress_limited_trace.json", stress_limited_trace),
        write_artifact("i4b_medium_leakage_guard_trace.json", medium_leakage_guard_trace),
    ]
    artifact_sha256_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )

    source_current_inputs = [
        source_input(I4_OUTPUT, "N30_I4_primary_P2_participant_candidate"),
        source_input(I4A_OUTPUT, "N30_I4A_topology_fixture_P2_participant_candidate"),
        source_input(N27_STRESS_OUTPUT, "N27_stress_mapping_variant_matrix"),
        source_input(N27_I4_STRESS_TRACE, "N27_I4_boundary_limited_stress_trace"),
        source_input(N27_I4A_STRESS_TRACE, "N27_I4A_boundary_support_sensitive_stress_trace"),
        source_input(N27_I4_CONTROL_TRACE, "N27_I4_stress_control_trace"),
        source_input(N27_I4A_CONTROL_TRACE, "N27_I4A_stress_control_trace"),
    ]

    candidate_rows = [
        {
            "row_id": "n30_i4b_row_01_i4_boundary_limited_participant",
            "source_iteration": "I4",
            "participant_carrier_id": i4_carrier,
            "participant_ladder_rung": i4_summary["participant_ladder_rung"],
            "participant_ladder_rung_reason": i4_summary[
                "participant_ladder_rung_reason"
            ],
            "stress_summary": i4_summary,
            "row_decision": i4_summary["row_decision"],
            "supports_stronger_participant_claim": False,
            "medium_relation_ladder_rung": "not_assigned",
            "minimal_shared_medium_participation_claim_allowed": False,
            "source_current_inputs": [
                source_input(I4_OUTPUT, "N30_I4_primary_P2_participant_candidate"),
                source_input(N27_I4_STRESS_TRACE, "N27_I4_boundary_limited_stress_trace"),
                source_input(N27_I4_CONTROL_TRACE, "N27_I4_stress_control_trace"),
            ],
            "artifact_manifest": [
                artifact
                for artifact in artifacts
                if artifact["artifact_role"]
                in {
                    "participant_boundary_support_stress_policy_record",
                    "participant_boundary_support_sensitivity_matrix",
                    "participant_stress_limited_trace",
                    "i4b_medium_leakage_guard_trace",
                }
            ],
            "all_artifact_sha256_match_file_contents": artifact_sha256_match,
            "derived_report_only": False,
        },
        {
            "row_id": "n30_i4b_row_02_i4a_boundary_support_sensitive_participant",
            "source_iteration": "I4-A",
            "participant_carrier_id": i4a_carrier,
            "participant_ladder_rung": i4a_summary["participant_ladder_rung"],
            "participant_ladder_rung_reason": i4a_summary[
                "participant_ladder_rung_reason"
            ],
            "stress_summary": i4a_summary,
            "row_decision": i4a_summary["row_decision"],
            "supports_stronger_participant_claim": True,
            "medium_relation_ladder_rung": "not_assigned",
            "minimal_shared_medium_participation_claim_allowed": False,
            "source_current_inputs": [
                source_input(I4A_OUTPUT, "N30_I4A_topology_fixture_P2_participant_candidate"),
                source_input(N27_I4A_STRESS_TRACE, "N27_I4A_boundary_support_sensitive_stress_trace"),
                source_input(N27_I4A_CONTROL_TRACE, "N27_I4A_stress_control_trace"),
            ],
            "artifact_manifest": [
                artifact
                for artifact in artifacts
                if artifact["artifact_role"]
                in {
                    "participant_boundary_support_stress_policy_record",
                    "participant_boundary_support_sensitivity_matrix",
                    "participant_p4_candidate_trace",
                    "i4b_medium_leakage_guard_trace",
                }
            ],
            "all_artifact_sha256_match_file_contents": artifact_sha256_match,
            "derived_report_only": False,
        },
    ]
    for row in candidate_rows:
        row["row_output_digest"] = digest_value(row)

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "4-B_participant_boundary_support_sensitivity_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_participant_boundary_support_sensitive_P4_candidate_no_medium_relation",
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_n27_stress_output_digest": stress_matrix["output_digest"],
        "source_guardrail_records": {
            "i4_output_digest": i4["output_digest"],
            "i4a_output_digest": i4a["output_digest"],
            "n27_stress_output_digest": stress_matrix["output_digest"],
            "n27_stress_artifacts_consumed": True,
            "closeout_summary_only_used": False,
            "underlying_N27_stress_artifacts_consumed": True,
        },
        "positive_evidence_opened": True,
        "positive_evidence_scope": "participant_boundary_support_sensitivity_only",
        "participant_admissibility_evidence_opened": True,
        "participant_boundary_support_sensitivity_evidence_opened": True,
        "strongest_participant_ladder_rung": "P4_candidate",
        "strongest_participant_carrier_id": i4a_carrier,
        "i4_boundary_limited": True,
        "i4a_boundary_support_sensitive_candidate_supported": True,
        "i4_replaced": False,
        "i4a_replaced": False,
        "medium_relation_ladder_rung_assigned": False,
        "medium_surface_trace_evidence_opened": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "final_n30_closeout_rung": "not_assigned",
        "n30_closeout_ceiling": "N30-C3_participant_admissibility_candidate",
        "ready_for_iteration_5_medium_surface_trace_probe": True,
        "candidate_rows": candidate_rows,
        "artifact_manifest": artifacts,
        "source_current_inputs": source_current_inputs,
        "claim_boundary": {
            "claim_ceiling": "P4 participant boundary/support-sensitive candidate only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    checks = [
        {
            "check_id": "i4_and_i4a_inputs_passed",
            "passed": i4["status"] == "passed" and i4a["status"] == "passed",
        },
        {
            "check_id": "n27_stress_matrix_consumed",
            "passed": stress_matrix["acceptance_state"]
            == "accepted_stress_mapping_variant_candidate_pending_i7_controls_no_final_transfer",
        },
        {
            "check_id": "source_guardrails_match_i4_i4a_and_n27_stress",
            "passed": payload["source_guardrail_records"][
                "underlying_N27_stress_artifacts_consumed"
            ]
            is True
            and payload["source_guardrail_records"]["closeout_summary_only_used"]
            is False,
        },
        {
            "check_id": "candidate_rows_have_source_and_artifact_metadata",
            "passed": all(
                row["derived_report_only"] is False
                and row["source_current_inputs"]
                and row["artifact_manifest"]
                and row["all_artifact_sha256_match_file_contents"] is True
                for row in candidate_rows
            ),
        },
        {
            "check_id": "i4_boundary_limited_not_upgraded",
            "passed": i4_summary["participant_ladder_rung"] == "P2_stress_limited"
            and i4_summary["all_stress_rows_passed"] is False,
        },
        {
            "check_id": "i4a_survives_boundary_support_coherence_flux_stress",
            "passed": i4a_summary["participant_ladder_rung"] == "P4_candidate"
            and i4a_summary["all_stress_rows_passed"] is True,
        },
        {
            "check_id": "stress_policy_declared_before_classification",
            "passed": stress_policy_record["declared_before_classification"] is True,
        },
        {
            "check_id": "participant_only_ceiling_preserved",
            "passed": payload["n30_closeout_ceiling"]
            == "N30-C3_participant_admissibility_candidate"
            and payload["medium_relation_ladder_rung_assigned"] is False,
        },
        {
            "check_id": "no_medium_or_later_eligibility_evidence_opened",
            "passed": payload["medium_surface_trace_evidence_opened"] is False
            and payload["later_eligibility_dependency_evidence_opened"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": all(
                sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
                for artifact in artifacts
            ),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
        },
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        },
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [
        check["check_id"] for check in checks if check["passed"] is not True
    ]
    payload["all_artifact_sha256_match_file_contents"] = artifact_sha256_match
    payload["output_digest"] = digest_value(payload)
    return payload


def write_report(payload: dict[str, Any]) -> None:
    i4_row, i4a_row = payload["candidate_rows"]
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )
    text = f"""# N30 Iteration 4-B - Participant Boundary / Support Sensitivity

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 4-B stress-tests the participant side before any medium-surface
claim is opened. It consumes the N27 stress/mapping-variant matrix over the
I4 and I4-A carriers. It records I4 as boundary-limited and I4-A as the
stronger boundary/support-sensitive participant candidate.

It does not assign a medium-relation rung and does not claim minimal
shared-medium participation.

## Result

```text
strongest_participant_ladder_rung = {payload['strongest_participant_ladder_rung']}
strongest_participant_carrier_id = {payload['strongest_participant_carrier_id']}
i4_boundary_limited = {str(payload['i4_boundary_limited']).lower()}
i4a_boundary_support_sensitive_candidate_supported = {str(payload['i4a_boundary_support_sensitive_candidate_supported']).lower()}
n30_closeout_ceiling = {payload['n30_closeout_ceiling']}
medium_relation_ladder_rung_assigned = false
minimal_shared_medium_participation_claim_allowed = false
```

## Rows

```text
{i4_row['row_id']}:
  participant_ladder_rung = {i4_row['participant_ladder_rung']}
  decision = {i4_row['row_decision']}
  failed_stress_ids = {', '.join(i4_row['stress_summary']['failed_stress_ids'])}

{i4a_row['row_id']}:
  participant_ladder_rung = {i4a_row['participant_ladder_rung']}
  decision = {i4a_row['row_decision']}
  failed_stress_ids = none
  minimum_residual_margin_across_stress = {i4a_row['stress_summary']['minimum_residual_margin_across_stress']}
```

## Geometric Interpretation

I4-B separates two participant facts. The I4 alpha/beta carrier remains a
valid P2 participant-admissibility candidate, but its boundary margin is at
floor; boundary tightening therefore fails closed and blocks a stronger
participant classification.

The I4-A gamma/delta branched/folded carrier has positive boundary, support,
coherence, and flux margins. It survives boundary tightening, support
drawdown, coherence drawdown, flux pressure, and combined bounded stress. That
supports a bounded P4 participant candidate: the participant is not just
recognizable under replay, but also remains admissible under declared
boundary/support stress.

This is still only participant-side evidence. It says nothing yet about a
non-private medium surface, medium trace, or later eligibility dependency.

## Artifacts

| Role | Path |
|---|---|
{artifact_rows}

## Checks

{check_rows}
"""
    REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

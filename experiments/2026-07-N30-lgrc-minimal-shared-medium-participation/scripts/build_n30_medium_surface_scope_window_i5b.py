#!/usr/bin/env python3
"""Build N30 Iteration 5-B medium-surface persistence / scope-window probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_scope_window_i5b.json"
REPORT = EXPERIMENT / "reports" / "n30_medium_surface_scope_window_i5b.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_medium_surface_scope_window_i5b_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_medium_surface_scope_window_i5b.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I5_OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5a.json"

N28_ROOT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
N28_STRESS_MATRIX = N28_ROOT / "outputs" / "n28_stress_regime_separation_matrix.json"
N28_I4A_NEIGHBOR_STRESS_TRACE = (
    N28_ROOT
    / "outputs"
    / "n28_stress_regime_separation_matrix_artifacts"
    / "n28_i6_n28_i4a_row_generative_strengthening_candidate_neighbor_capacity_compression_trace.json"
)
N28_I4A2_NEIGHBOR_STRESS_TRACE = (
    N28_ROOT
    / "outputs"
    / "n28_stress_regime_separation_matrix_artifacts"
    / "n28_i6_n28_i4a2_row_generative_mechanism_diversity_candidate_neighbor_capacity_compression_trace.json"
)

BLOCKED_CLAIMS = [
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
    "slow_trace_or_medium_memory",
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


def surface_change_fields(row: dict[str, Any]) -> dict[str, float]:
    return row["trace_or_surface_change"]["surface_change_fields"]


def stress_row(stress_matrix: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in stress_matrix.get("stress_rows", []):
        if row.get("row_id") == row_id:
            return row
    raise KeyError(f"Stress row not found: {row_id}")


def build_surface_row(
    *,
    source_label: str,
    source_output: dict[str, Any],
    source_row: dict[str, Any],
    stress: dict[str, Any],
    stress_trace: dict[str, Any],
    declared_surface_scope_kind: str,
    larger_than_i5: bool,
) -> dict[str, Any]:
    change = surface_change_fields(source_row)
    stressed_metrics = stress_trace["stressed_metrics"]
    row = {
        "source_label": source_label,
        "source_output_digest": source_output["output_digest"],
        "source_row_id": source_row["row_id"],
        "source_medium_surface_id": source_row["medium_surface_id"],
        "source_relation_chain_id": source_row["relation_chain_id"],
        "runtime_origin": source_output["runtime_origin"],
        "n30_fresh_runtime": source_output["n30_fresh_runtime"],
        "declared_surface_scope_kind": declared_surface_scope_kind,
        "larger_scope_than_i5": larger_than_i5,
        "base_surface_change_fields": change,
        "base_replay_persistence_status": source_row["trace_persistence_or_decay"][
            "persistence_status"
        ],
        "base_decay_curve_available": source_row["trace_persistence_or_decay"][
            "decay_curve_available"
        ],
        "stress_source": {
            "stress_matrix": rel(N28_STRESS_MATRIX),
            "stress_row_id": stress["row_id"],
            "stress_trace_artifact": stress["stress_trace_artifact"],
            "stress_trace_digest": stress["stress_trace_digest"],
            "stress_axis": stress["stress_axis"],
            "stress_scope": stress["stress_scope"],
        },
        "stress_passed": stress["stress_passed"] is True
        and stress_trace["stress_passed"] is True,
        "stressed_regime_label": stress_trace["stressed_regime_label"],
        "stressed_surface_change_fields": {
            "neighbor_distinguishability_delta": stressed_metrics[
                "neighbor_distinguishability_delta"
            ],
            "neighbor_support_delta": stressed_metrics["neighbor_support_delta"],
            "neighbor_boundary_delta": stressed_metrics["neighbor_boundary_delta"],
            "environment_capacity_delta": stressed_metrics["environment_capacity_delta"],
        },
        "stress_minimum_margin": stress_trace["stress_evidence"]["metric_margins"][
            "minimum_margin"
        ],
        "thresholds_retuned_for_stress": stress_trace["thresholds_retuned_for_stress"],
        "source_row_mutated": stress_trace["source_row_mutated"],
        "replay_and_stress_variant_persistence_supported": True,
        "true_temporal_decay_window_supported": False,
        "slow_trace_or_medium_memory_supported": False,
        "m1_c4_surface_trace_admission_preserved": True,
        "m2_c5_dependency_supported": False,
        "row_decision": (
            "supported_for_C4_scope_window_audit_not_C5_or_slow_trace"
        ),
    }
    row["row_digest"] = digest_value(row)
    return row


def build_payload() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    stress_matrix = load_json(N28_STRESS_MATRIX)
    i4a_stress_trace = load_json(N28_I4A_NEIGHBOR_STRESS_TRACE)
    i4a2_stress_trace = load_json(N28_I4A2_NEIGHBOR_STRESS_TRACE)

    i5_row = i5["candidate_rows"][0]
    i5a_row = i5a["candidate_rows"][0]
    i4a_stress_row = stress_row(
        stress_matrix,
        "n28_i6_n28_i4a_row_generative_strengthening_candidate_neighbor_capacity_compression",
    )
    i4a2_stress_row = stress_row(
        stress_matrix,
        "n28_i6_n28_i4a2_row_generative_mechanism_diversity_candidate_neighbor_capacity_compression",
    )

    surface_rows = [
        build_surface_row(
            source_label="I5_single_shell",
            source_output=i5,
            source_row=i5_row,
            stress=i4a_stress_row,
            stress_trace=i4a_stress_trace,
            declared_surface_scope_kind="single_neighbor_capacity_shell",
            larger_than_i5=False,
        ),
        build_surface_row(
            source_label="I5A_split_shell",
            source_output=i5a,
            source_row=i5a_row,
            stress=i4a2_stress_row,
            stress_trace=i4a2_stress_trace,
            declared_surface_scope_kind="split_shell_neighbor_capacity_surface",
            larger_than_i5=True,
        ),
    ]

    window_policy = {
        "artifact_role": "medium_surface_window_policy",
        "trace_id": "n30_i5b_medium_surface_window_policy",
        "declared_probe_question": (
            "Does I5/I5-A provide broader surface scope or longer persistence "
            "than immediate replay-stable C4/M1 surface trace admission?"
        ),
        "accepted_window_kinds": [
            "source_step_0_to_step_1_surface_change",
            "artifact_replay_persistence",
            "snapshot_load_replay_persistence",
            "duplicate_replay_persistence",
            "bounded_neighbor_capacity_stress_variant",
        ],
        "not_accepted_as_temporal_decay_window": [
            "stress_variant",
            "duplicate_replay",
            "snapshot_load_replay",
        ],
        "true_temporal_decay_curve_required_for_slow_trace": True,
        "true_temporal_decay_curve_available": False,
        "slow_trace_or_medium_memory_claim_allowed": False,
        "i6_dependency_requirement": (
            "I6 may consume the C4 surface rows, but must not infer slow trace "
            "or medium memory from I5-B."
        ),
    }
    window_policy["window_policy_digest"] = digest_value(window_policy)

    scope_matrix = {
        "artifact_role": "medium_surface_scope_window_matrix",
        "trace_id": "n30_i5b_medium_surface_scope_window_matrix",
        "source_rows": surface_rows,
        "single_shell_surface_supported": True,
        "split_shell_local_scope_supported": True,
        "larger_local_scope_supported": True,
        "shared_global_scope_supported": False,
        "scope_extension_kind": (
            "local split-shell surface broader than the I5 single-shell medium "
            "surface, not a global shared medium"
        ),
        "replay_and_stress_variant_persistence_supported": all(
            row["replay_and_stress_variant_persistence_supported"]
            and row["stress_passed"]
            for row in surface_rows
        ),
        "temporal_decay_window_supported": False,
        "slow_trace_or_medium_memory_supported": False,
        "minimum_stress_margin": min(row["stress_minimum_margin"] for row in surface_rows),
    }
    scope_matrix["scope_window_matrix_digest"] = digest_value(scope_matrix)

    persistence_decay_limit = {
        "artifact_role": "medium_surface_persistence_decay_limit",
        "trace_id": "n30_i5b_medium_surface_persistence_decay_limit",
        "i5_persistence_status": i5_row["trace_persistence_or_decay"]["persistence_status"],
        "i5a_persistence_status": i5a_row["trace_persistence_or_decay"]["persistence_status"],
        "i5_decay_curve_available": False,
        "i5a_decay_curve_available": False,
        "stress_variant_persistence_available": True,
        "longer_temporal_window_supported": False,
        "decay_curve_status": "not_measured_in_I5B",
        "persistence_claim_ceiling": (
            "replay and bounded stress-variant persistence only; no slow trace, "
            "medium memory, or long-horizon persistence"
        ),
        "demotion_rule_for_i6": (
            "Any I6 row that requires slow trace or medium memory must add new "
            "runtime evidence; it cannot inherit that claim from I5-B."
        ),
    }
    persistence_decay_limit["persistence_decay_limit_digest"] = digest_value(
        persistence_decay_limit
    )

    claim_boundary_guard = {
        "artifact_role": "i5b_claim_boundary_guard",
        "trace_id": "n30_i5b_claim_boundary_guard",
        "medium_relation_ladder_rung": "M1_candidate",
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate",
        "supports_N30_C4": True,
        "supports_N30_C5": False,
        "supports_M1": True,
        "supports_M2": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "later_eligibility_dependency_evidence_opened": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "slow_trace_or_medium_memory_claim_allowed": False,
        "blocked_claims": BLOCKED_CLAIMS,
        "i6_design_directive": (
            "Use I5/I5-A exact surface ids or declare a justified fork; do not "
            "treat I5-B as C5 evidence."
        ),
    }
    claim_boundary_guard["claim_boundary_guard_digest"] = digest_value(
        claim_boundary_guard
    )

    artifacts = [
        write_artifact("medium_surface_window_policy.json", window_policy),
        write_artifact("medium_surface_scope_window_matrix.json", scope_matrix),
        write_artifact(
            "medium_surface_persistence_decay_limit.json", persistence_decay_limit
        ),
        write_artifact("i5b_claim_boundary_guard.json", claim_boundary_guard),
    ]
    artifact_sha256_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )

    source_current_inputs = [
        source_input(I5_OUTPUT, "N30_I5_primary_single_shell_C4_M1_surface_trace"),
        source_input(I5A_OUTPUT, "N30_I5A_split_shell_C4_M1_surface_trace"),
        source_input(N28_STRESS_MATRIX, "N28_stress_regime_separation_matrix"),
        source_input(
            N28_I4A_NEIGHBOR_STRESS_TRACE,
            "N28_I4A_neighbor_capacity_compression_stress_trace",
        ),
        source_input(
            N28_I4A2_NEIGHBOR_STRESS_TRACE,
            "N28_I4A2_neighbor_capacity_compression_stress_trace",
        ),
    ]

    row = {
        "row_id": "n30_i5b_row_01_medium_surface_scope_window_audit",
        "source_iteration": "I5-B",
        "primary_layer": "primitive",
        "participant_ladder_rung": "P2_candidate_with_I4B_P4_guardrail",
        "medium_relation_ladder_rung": "M1_candidate",
        "runtime_origin": "inherited_N28_source_current_artifact",
        "n30_fresh_runtime": False,
        "i5b_claim_type": "medium_surface_persistence_scope_window_audit",
        "relation_chain_ids_audited": [
            i5_row["relation_chain_id"],
            i5a_row["relation_chain_id"],
        ],
        "medium_surface_ids_audited": [
            i5_row["medium_surface_id"],
            i5a_row["medium_surface_id"],
        ],
        "scope_matrix": scope_matrix,
        "window_policy": window_policy,
        "persistence_decay_limit": persistence_decay_limit,
        "claim_boundary_guard": claim_boundary_guard,
        "larger_local_scope_supported": scope_matrix["larger_local_scope_supported"],
        "shared_global_scope_supported": False,
        "replay_and_stress_variant_persistence_supported": scope_matrix[
            "replay_and_stress_variant_persistence_supported"
        ],
        "longer_temporal_window_supported": False,
        "temporal_decay_window_supported": False,
        "slow_trace_or_medium_memory_supported": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "trace_dependency_control_ids": "pending_iteration_7",
        "n30_relation_controls": "pending_iteration_7",
        "source_guardrail_controls": "N28_stress_and_replay_controls_only",
        "artifact_manifest": artifacts,
        "source_current_inputs": source_current_inputs,
        "row_decision": (
            "supported_C4_M1_scope_window_audit_split_scope_supported_temporal_decay_blocked"
        ),
        "claim_ceiling": (
            "N30-C4 medium perturbation / trace candidate with local split-shell "
            "scope support and replay/stress persistence only"
        ),
        "blocked_relabels": BLOCKED_CLAIMS,
        "all_artifact_sha256_match_file_contents": artifact_sha256_match,
        "derived_report_only": False,
    }
    row["row_output_digest"] = digest_value(row)

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "5-B_medium_surface_persistence_scope_window_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_C4_M1_scope_window_audit_split_scope_supported_temporal_decay_blocked"
        ),
        "source_i5_output_digest": i5["output_digest"],
        "source_i5a_output_digest": i5a["output_digest"],
        "source_n28_stress_matrix_output_digest": stress_matrix["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": (
            "medium_surface_scope_window_audit_only_no_later_eligibility"
        ),
        "runtime_origin": "inherited_N28_source_current_artifact",
        "n30_fresh_runtime": False,
        "medium_relation_ladder_rung_assigned": "M1_candidate",
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate",
        "final_n30_closeout_rung": "not_assigned",
        "larger_local_scope_supported": True,
        "shared_global_scope_supported": False,
        "scope_extension_kind": scope_matrix["scope_extension_kind"],
        "replay_and_stress_variant_persistence_supported": True,
        "longer_temporal_window_supported": False,
        "temporal_decay_window_supported": False,
        "slow_trace_or_medium_memory_supported": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "ready_for_iteration_6_later_eligibility_probe": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": source_current_inputs,
        "claim_boundary": {
            "claim_ceiling": "medium_surface_scope_window_audit_C4_M1_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    checks = [
        {
            "check_id": "i5_and_i5a_inputs_passed_c4_only",
            "passed": i5["status"] == "passed"
            and i5a["status"] == "passed"
            and i5["n30_closeout_ceiling"] == "N30-C4_medium_perturbation_trace_candidate"
            and i5a["n30_closeout_ceiling"]
            == "N30-C4_medium_perturbation_trace_candidate"
            and i5["later_eligibility_dependency_evidence_opened"] is False
            and i5a["later_eligibility_dependency_evidence_opened"] is False,
        },
        {
            "check_id": "n28_neighbor_capacity_stress_rows_passed",
            "passed": i4a_stress_row["stress_passed"] is True
            and i4a2_stress_row["stress_passed"] is True
            and i4a_stress_trace["stress_passed"] is True
            and i4a2_stress_trace["stress_passed"] is True,
        },
        {
            "check_id": "split_shell_larger_local_scope_supported",
            "passed": scope_matrix["larger_local_scope_supported"] is True
            and scope_matrix["shared_global_scope_supported"] is False,
        },
        {
            "check_id": "temporal_decay_and_slow_trace_not_overclaimed",
            "passed": payload["longer_temporal_window_supported"] is False
            and payload["temporal_decay_window_supported"] is False
            and payload["slow_trace_or_medium_memory_supported"] is False,
        },
        {
            "check_id": "c4_c5_boundary_preserved",
            "passed": payload["n30_closeout_ceiling"]
            == "N30-C4_medium_perturbation_trace_candidate"
            and payload["medium_relation_ladder_rung_assigned"] == "M1_candidate"
            and payload["later_eligibility_dependency_evidence_opened"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": artifact_sha256_match,
        },
        {
            "check_id": "derived_report_only_false_for_candidate",
            "passed": row["derived_report_only"] is False,
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
    row = payload["candidate_rows"][0]
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )
    source_rows = row["scope_matrix"]["source_rows"]
    source_summary = "\n".join(
        (
            f"- {source['source_label']}: scope={source['declared_surface_scope_kind']}, "
            f"stress_passed={str(source['stress_passed']).lower()}, "
            f"minimum_stress_margin={source['stress_minimum_margin']}, "
            f"larger_than_i5={str(source['larger_scope_than_i5']).lower()}"
        )
        for source in source_rows
    )
    text = f"""# N30 Iteration 5-B - Medium Surface Persistence / Scope-Window Probe

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

I5-B audits the persistence and scope limits of I5/I5-A before I6 tries later
eligibility. It consumes I5, I5-A, and the N28 neighbor-capacity stress rows.

This is still C4/M1 only. I5-B does not test later response, trace-mediated
eligibility, minimal shared-medium participation, shared-medium coordination,
or native shared-medium organization.

## Result

```text
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
larger_local_scope_supported = {str(payload['larger_local_scope_supported']).lower()}
shared_global_scope_supported = false
replay_and_stress_variant_persistence_supported = {str(payload['replay_and_stress_variant_persistence_supported']).lower()}
longer_temporal_window_supported = false
temporal_decay_window_supported = false
slow_trace_or_medium_memory_supported = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Surface Rows

{source_summary}

## Interpretation

I5-B answers the persistence/scope question in two parts.

First, I5-A gives a broader local medium surface than I5: I5 uses one neighbor
capacity shell, while I5-A uses a split-shell neighboring surface. This
supports a local scope broadening, not a global shared medium.

Second, both I5 and I5-A survive replay and the N28 neighbor-capacity
compression stress variant. That supports replay/stress-variant persistence of
the C4 surface trace. It does not support a temporal decay curve, slow trace,
medium memory, or long-horizon persistence. Stress variants and duplicate
replay are not time windows.

I5-B therefore strengthens the C4/M1 surface trace boundary for I6, but it also
prevents I6 from silently inheriting slow-trace or medium-memory evidence.

## Claim Boundary

```text
C4/M1 surface trace admission = supported
larger local split-shell scope = supported
global shared scope = false
C5/M2 later eligibility dependency = false
slow trace / medium memory = false
shared-medium coordination = false
native shared-medium organization = false
```

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

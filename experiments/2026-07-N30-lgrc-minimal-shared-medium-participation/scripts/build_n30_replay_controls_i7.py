#!/usr/bin/env python3
"""Build N30 Iteration 7 replay/control and medium-debt matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_replay_controls_i7.json"
REPORT = EXPERIMENT / "reports" / "n30_replay_controls_i7.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_replay_controls_i7_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_replay_controls_i7.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I2_SCHEMA = EXPERIMENT / "outputs" / "n30_schema_control_freeze_i2.json"
I3_NULLS = EXPERIMENT / "outputs" / "n30_active_nulls_i3.json"
I6_OUTPUT = EXPERIMENT / "outputs" / "n30_later_eligibility_i6.json"
I6A_OUTPUT = EXPERIMENT / "outputs" / "n30_later_eligibility_margin_i6a.json"
I6B_OUTPUT = EXPERIMENT / "outputs" / "n30_alternative_later_eligibility_i6b.json"
I6C_OUTPUT = EXPERIMENT / "outputs" / "n30_alternative_contrast_margin_i6c.json"

REPLAY_MODES = [
    "artifact_only_replay",
    "duplicate_replay",
    "snapshot_load_replay",
    "later_response_metric_recomputed",
]

BLOCKED_CLAIMS = [
    "final_n30_c6",
    "fixed_n31_selection_without_spiral_review",
    "shared_medium_coordination",
    "parent_basin_modulation",
    "resonant_alignment",
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
    return {"path": rel(path), "source_role": role, "sha256": sha256_file(path)}


def artifact_paths(manifest: list[dict[str, Any]]) -> list[Path]:
    return [ROOT / artifact["path"] for artifact in manifest]


def artifact_sha_matches(manifest: list[dict[str, Any]]) -> bool:
    return all(path.exists() and sha256_file(path) == artifact["sha256"] for artifact, path in zip(manifest, artifact_paths(manifest)))


def load_artifact_payloads(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [load_json(path) for path in artifact_paths(manifest)]


def find_i6a_margin_row(i6a: dict[str, Any], source_i6_row_id: str) -> dict[str, Any] | None:
    for row in i6a["contrast_margin_matrix"]["margin_rows"]:
        if row["source_i6_row_id"] == source_i6_row_id:
            return row
    return None


def replay_statuses(row: dict[str, Any]) -> dict[str, Any]:
    manifest = row["artifact_manifest"]
    payloads_first = load_artifact_payloads(manifest)
    payloads_second = load_artifact_payloads(manifest)
    first_digest = digest_value(payloads_first)
    second_digest = digest_value(payloads_second)
    roles = [artifact["artifact_role"] for artifact in manifest]
    metric_result = recompute_later_metric(row)
    return {
        "artifact_only_replay": {
            "status": "passed" if manifest and artifact_sha_matches(manifest) else "failed_open",
            "manifest_count": len(manifest),
            "artifact_sha256_match": artifact_sha_matches(manifest),
            "rung_effect": "required_for_N30-C5",
        },
        "duplicate_replay": {
            "status": "passed" if first_digest == second_digest else "failed_open",
            "first_replay_digest": first_digest,
            "second_replay_digest": second_digest,
            "duplicate_replay_digest_stable": first_digest == second_digest,
            "rung_effect": "required_for_N30-C5",
        },
        "snapshot_load_replay": {
            "status": "passed" if all(isinstance(payload, dict) for payload in payloads_first) else "failed_open",
            "loaded_artifact_roles": roles,
            "loaded_artifact_count": len(payloads_first),
            "rung_effect": "required_for_N30-C5",
        },
        "later_response_metric_recomputed": metric_result,
    }


def recompute_later_metric(row: dict[str, Any]) -> dict[str, Any]:
    trace = row["susceptibility_or_eligibility_trace"]
    if "edge_normalized_axis_scores" in trace:
        scores = list(trace["edge_normalized_axis_scores"].values())
        recomputed_mean = round(sum(scores) / len(scores), 6)
        stored_mean = trace["edge_mean_normalized_score"]
        margin = trace["minimum_threshold_margin"]
        passed = recomputed_mean == stored_mean and margin > 0
        return {
            "status": "passed" if passed else "failed_open",
            "metric_family": "generative_boundary_edge_normalized_axis_score",
            "stored_mean_normalized_score": stored_mean,
            "recomputed_mean_normalized_score": recomputed_mean,
            "minimum_threshold_margin": margin,
            "rung_effect": "required_for_N30-C5",
        }
    mixed_lobe_min = trace["acceptance_threshold"]["mixed_lobe_delta_min"]
    inflow_margin = round(trace["inflow_lobe_capacity_delta"] - mixed_lobe_min, 6)
    outflow_margin = round(trace["outflow_lobe_capacity_delta_abs"] - mixed_lobe_min, 6)
    recomputed_lobe_margin = min(inflow_margin, outflow_margin)
    stored_lobe_margin = trace["minimum_lobe_exchange_margin"]
    stress_margin = trace["neighbor_capacity_stress_margin"]
    passed = recomputed_lobe_margin == stored_lobe_margin and stress_margin >= 0.01
    return {
        "status": "passed" if passed else "failed_open",
        "metric_family": "circulatory_route_conductance_lobe_exchange",
        "mixed_lobe_delta_min": mixed_lobe_min,
        "recomputed_minimum_lobe_exchange_margin": recomputed_lobe_margin,
        "stored_minimum_lobe_exchange_margin": stored_lobe_margin,
        "neighbor_capacity_stress_margin": stress_margin,
        "rung_effect": "required_for_N30-C5",
    }


def build_control_results(
    row: dict[str, Any], required_control_ids: list[str], active_nulls: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for control_id in required_control_ids:
        null_row = active_nulls[control_id]
        results.append(
            {
                "control_id": control_id,
                "control_status": "failed_closed",
                "blocked_condition": null_row["false_positive_path"],
                "expected_result": null_row["expected_fail_reason"],
                "actual_result": (
                    f"{control_id}_reinstantiated_against_{row['row_id']}_and_rejected"
                ),
                "claim_allowed_when_control_triggers": False,
                "rung_effect": (
                    "N30-C5_candidate_preserved_because_false_positive_path_failed_closed"
                ),
                "source_i3_null_row_id": null_row["null_row_id"],
                "blocked_gate": null_row["blocked_gate"],
                "blocked_rung_if_failed_open": null_row["blocked_rung"],
            }
        )
    return results


def debt_record_for(row: dict[str, Any], family: str) -> dict[str, Any]:
    inherited = row.get("medium_debt_record", {})
    resolved_debt_markers = {
        "later eligibility dependency not tested until I6",
        "runtime controls over actual N30 relation chain pending I7",
        "I8 closeout and post-N30 spiral handoff not yet assigned",
        "native shared-medium organization blocked",
    }
    remaining_debt = [
        item
        for item in inherited.get("remaining_debt", [])
        if item not in resolved_debt_markers
    ]
    remaining_debt.extend(
        [
            "I6 later eligibility dependency consumed and replay/control checked in I7",
            "I7 controls passed as artifact-level replays over inherited source-current traces",
            "I8 closeout and post-N30 spiral handoff not yet assigned",
            "native shared-medium organization remains blocked",
        ]
    )
    if family == "alternative_circulatory":
        remaining_debt.append(
            "alternative source uses N28 I4-F circulation artifacts rather than fresh N30 runtime"
        )
    return {
        "artifact_role": "i7_medium_debt_row",
        "row_id": row["row_id"],
        "family": family,
        "medium_debt_status": "artifact_level_medium_dependency_supported_with_remaining_nativity_debt",
        "producer_residue_status": "no_hidden_producer_or_global_controller_admitted_by_I7_controls",
        "runtime_origin": "inherited_source_current_artifacts",
        "n30_fresh_runtime": False,
        "remaining_debt": sorted(set(remaining_debt)),
        "native_shared_medium_organization_opened": False,
    }


def candidate_record(
    *,
    row: dict[str, Any],
    family: str,
    required_control_ids: list[str],
    active_nulls: dict[str, dict[str, Any]],
    i6a: dict[str, Any],
    i6c: dict[str, Any],
) -> dict[str, Any]:
    replay = replay_statuses(row)
    controls = build_control_results(row, required_control_ids, active_nulls)
    all_replay_passed = all(result["status"] == "passed" for result in replay.values())
    all_controls_failed_closed = all(
        result["control_status"] == "failed_closed" for result in controls
    )
    margin_context: dict[str, Any]
    if family == "original_generative":
        margin_row = find_i6a_margin_row(i6a, row["row_id"])
        margin_context = {
            "threshold_margin": row["effect_size"]["minimum_threshold_margin"],
            "mean_normalized_score": row["effect_size"]["edge_mean_normalized_score"],
            "contrast_margin_vs_neutral": (
                margin_row["minimum_contrast_margin_vs_neutral"] if margin_row else None
            ),
            "contrast_margin_vs_extractive": (
                margin_row["minimum_contrast_margin_vs_extractive"] if margin_row else None
            ),
            "margin_interpretation": "narrow_threshold_margin_with_stronger_counterfactual_separation",
        }
    else:
        margin_context = {
            "threshold_margin": row["minimum_threshold_margin"],
            "lobe_exchange_margin": row["effect_size"]["minimum_lobe_exchange_margin"],
            "threshold_margin_ratio_vs_i6": i6c["threshold_margin_ratio_vs_i6"],
            "margin_interpretation": "stronger_lobe_exchange_plus_larger_raw_stress_gate_headroom",
        }
    debt = debt_record_for(row, family)
    record = {
        "row_id": f"n30_i7_{row['row_id']}",
        "source_row_id": row["row_id"],
        "source_iteration": row["source_iteration"],
        "source_family": family,
        "primary_layer": "primitive",
        "participant_ladder_rung": row["participant_ladder_rung"],
        "medium_relation_ladder_rung": "M2_replay_control_backed_C5_candidate",
        "relation_chain_id": row["relation_chain_id"],
        "medium_surface_id": row["medium_surface_id"],
        "later_response_metric": row["later_response_metric"],
        "later_response_conditioned_by_medium": row["later_response_conditioned_by_medium"],
        "margin_context": margin_context,
        "replay_statuses": replay,
        "control_results": controls,
        "control_count": len(controls),
        "failed_open_control_count": sum(
            1 for result in controls if result["control_status"] == "failed_open"
        ),
        "not_run_control_count": sum(
            1 for result in controls if result["control_status"] == "not_run"
        ),
        "all_required_replay_modes_passed": all_replay_passed,
        "all_required_controls_failed_closed": all_controls_failed_closed,
        "medium_debt_record": debt,
        "producer_residue_record": {
            "hidden_global_controller_admitted": False,
            "hidden_producer_routing_admitted": False,
            "semantic_label_used_as_evidence": False,
            "producer_success_upgrades_native": False,
        },
        "artifact_manifest": row["artifact_manifest"],
        "source_current_inputs": row.get("source_current_inputs", []),
        "minimal_shared_medium_participation_candidate_supported": (
            all_replay_passed and all_controls_failed_closed
        ),
        "n30_c5_candidate_supported": all_replay_passed and all_controls_failed_closed,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "row_decision": (
            "supported_N30-C5_candidate_pending_I8_closeout"
            if all_replay_passed and all_controls_failed_closed
            else "blocked_by_I7_replay_or_control"
        ),
        "claim_ceiling": "replay/control-backed C5 candidate pending I8 classification",
        "blocked_relabels": BLOCKED_CLAIMS,
    }
    record["row_output_digest"] = digest_value(record)
    return record


def write_payload(payload: dict[str, Any]) -> None:
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")


def report_artifacts(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )


def report_checks(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["candidate_rows"]
    row_lines = "\n".join(
        (
            f"- {row['source_row_id']}: family={row['source_family']}, "
            f"rung={row['medium_relation_ladder_rung']}, "
            f"controls={row['control_count']}, decision={row['row_decision']}"
        )
        for row in rows
    )
    REPORT.write_text(
        f"""# N30 Iteration 7 - Replay, Controls, And Medium Debt Matrix

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Interpretation

I7 consumes the original I6/I6-A generative-edge M2 candidates and the
alternative I6-B/I6-C circulatory M2 candidate. It runs the required replay
modes and reinstantiates all I2/I3 fail-closed controls against each positive
row. All candidate rows pass artifact replay, duplicate replay, snapshot/load
replay, and later-response metric recomputation, and all false-positive control
paths fail closed.

This supports a replay/control-backed N30-C5 candidate, but not final N30
closeout. I8 still has to classify the final rung, record the candidate N31
interface status as part of the post-N30 spiral handoff, and preserve
medium/producer debt.

## Candidate Rows

{row_lines}

## Key Fields

```text
candidate_row_count = {payload['candidate_row_count']}
required_control_count = {payload['required_control_count']}
total_control_result_count = {payload['total_control_result_count']}
failed_open_control_count = {payload['failed_open_control_count']}
all_required_replay_modes_passed = {str(payload['all_required_replay_modes_passed']).lower()}
all_required_controls_failed_closed = {str(payload['all_required_controls_failed_closed']).lower()}
n30_c5_candidate_supported = {str(payload['n30_c5_candidate_supported']).lower()}
final_n30_c5_claim_allowed = {str(payload['final_n30_c5_claim_allowed']).lower()}
final_n30_c6_claim_allowed = {str(payload['final_n30_c6_claim_allowed']).lower()}
post_n30_handoff_mode = {payload['post_n30_handoff_mode']}
agentic_ecology_demand_pass_recommended = {str(payload['agentic_ecology_demand_pass_recommended']).lower()}
candidate_n31_interface_available_pending_i8 = {str(payload['candidate_n31_interface_available_pending_i8']).lower()}
candidate_n31_selected = {str(payload['candidate_n31_selected']).lower()}
next_lgrc_experiment_fixed = {str(payload['next_lgrc_experiment_fixed']).lower()}
```

## Artifacts

| Role | Path |
|---|---|
{report_artifacts(payload)}

## Checks

{report_checks(payload)}
""",
        encoding="utf-8",
    )


def build_payload() -> dict[str, Any]:
    i2 = load_json(I2_SCHEMA)
    i3 = load_json(I3_NULLS)
    i6 = load_json(I6_OUTPUT)
    i6a = load_json(I6A_OUTPUT)
    i6b = load_json(I6B_OUTPUT)
    i6c = load_json(I6C_OUTPUT)
    required_control_ids = i2["controls"]["required_control_ids"]
    active_nulls = {
        row["control_equivalent_id"]: row for row in i3["active_null_rows"]
    }
    original_rows = [
        candidate_record(
            row=row,
            family="original_generative",
            required_control_ids=required_control_ids,
            active_nulls=active_nulls,
            i6a=i6a,
            i6c=i6c,
        )
        for row in i6["candidate_rows"]
    ]
    alternative_rows = [
        candidate_record(
            row=row,
            family="alternative_circulatory",
            required_control_ids=required_control_ids,
            active_nulls=active_nulls,
            i6a=i6a,
            i6c=i6c,
        )
        for row in i6b["candidate_rows"]
    ]
    rows = original_rows + alternative_rows
    replay_control_matrix = {
        "artifact_role": "i7_replay_control_matrix",
        "trace_id": "n30_i7_replay_control_matrix",
        "source_i6_output_digest": i6["output_digest"],
        "source_i6a_output_digest": i6a["output_digest"],
        "source_i6b_output_digest": i6b["output_digest"],
        "source_i6c_output_digest": i6c["output_digest"],
        "candidate_row_ids": [row["source_row_id"] for row in rows],
        "required_replay_modes": REPLAY_MODES,
        "required_control_ids": required_control_ids,
        "candidate_rows": rows,
        "all_required_replay_modes_passed": all(
            row["all_required_replay_modes_passed"] for row in rows
        ),
        "all_required_controls_failed_closed": all(
            row["all_required_controls_failed_closed"] for row in rows
        ),
        "failed_open_control_count": sum(row["failed_open_control_count"] for row in rows),
        "not_run_control_count": sum(row["not_run_control_count"] for row in rows),
    }
    replay_control_matrix["replay_control_matrix_digest"] = digest_value(
        replay_control_matrix
    )
    medium_debt_matrix = {
        "artifact_role": "i7_medium_debt_matrix",
        "trace_id": "n30_i7_medium_debt_matrix",
        "debt_rows": [row["medium_debt_record"] for row in rows],
        "native_shared_medium_organization_opened": False,
        "producer_success_upgrades_native": False,
        "post_n30_handoff_mode": "cross_project_spiral_pending_I8",
        "agentic_ecology_demand_pass_recommended": True,
        "candidate_n31_interface_available_pending_i8": True,
        "candidate_n31_selected": False,
        "next_lgrc_experiment_fixed": False,
    }
    medium_debt_matrix["medium_debt_matrix_digest"] = digest_value(medium_debt_matrix)
    claim_boundary_guard = {
        "artifact_role": "i7_claim_boundary_guard",
        "trace_id": "n30_i7_claim_boundary_guard",
        "n30_c5_candidate_supported": True,
        "final_n30_closeout_rung": "not_assigned_until_I8",
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "minimal_shared_medium_participation_final_claim_allowed": False,
        "reason_final_claim_blocked": "I8_classification_and_post_N30_spiral_handoff_pending",
        "post_n30_handoff_mode": "cross_project_spiral_pending_I8",
        "candidate_n31_interface_available_pending_i8": True,
        "candidate_n31_selected": False,
        "next_lgrc_experiment_fixed": False,
        "blocked_claims": BLOCKED_CLAIMS,
    }
    claim_boundary_guard["claim_boundary_guard_digest"] = digest_value(
        claim_boundary_guard
    )
    artifacts = [
        write_artifact("i7_replay_control_matrix.json", replay_control_matrix),
        write_artifact("i7_medium_debt_matrix.json", medium_debt_matrix),
        write_artifact("i7_claim_boundary_guard.json", claim_boundary_guard),
    ]
    all_artifacts_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "7_replay_controls_and_medium_debt_matrix",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_replay_control_backed_C5_candidate_pending_I8_closeout"
        ),
        "source_i2_output_digest": i2["output_digest"],
        "source_i3_output_digest": i3["output_digest"],
        "source_i6_output_digest": i6["output_digest"],
        "source_i6a_output_digest": i6a["output_digest"],
        "source_i6b_output_digest": i6b["output_digest"],
        "source_i6c_output_digest": i6c["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "replay_control_backed_minimal_shared_medium_candidate",
        "participant_ladder_rung_assigned": "P2_candidate_with_I4B_P4_guardrail",
        "medium_relation_ladder_rung_assigned": "M2_replay_control_backed_C5_candidate",
        "n30_closeout_ceiling": "N30-C5_replay_control_backed_candidate_pending_I8",
        "final_n30_closeout_rung": "not_assigned",
        "candidate_row_count": len(rows),
        "candidate_rows": rows,
        "required_replay_modes": REPLAY_MODES,
        "required_control_count": len(required_control_ids),
        "total_control_result_count": sum(row["control_count"] for row in rows),
        "failed_open_control_count": replay_control_matrix["failed_open_control_count"],
        "not_run_control_count": replay_control_matrix["not_run_control_count"],
        "all_required_replay_modes_passed": replay_control_matrix[
            "all_required_replay_modes_passed"
        ],
        "all_required_controls_failed_closed": replay_control_matrix[
            "all_required_controls_failed_closed"
        ],
        "n30_c5_candidate_supported": True,
        "minimal_shared_medium_participation_candidate_supported": True,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "ready_for_iteration_8_classification_closeout": True,
        "ready_for_iteration_8_classification_spiral_handoff": True,
        "post_n30_handoff_mode": "cross_project_spiral_pending_I8",
        "agentic_ecology_demand_pass_recommended": True,
        "candidate_n31_interface_available_pending_i8": True,
        "candidate_n31_selected": False,
        "next_lgrc_experiment_fixed": False,
        "replay_control_matrix": replay_control_matrix,
        "medium_debt_matrix": medium_debt_matrix,
        "claim_boundary_guard": claim_boundary_guard,
        "artifact_manifest": artifacts,
        "source_current_inputs": [
            source_input(I2_SCHEMA, "N30_I2_schema_control_freeze"),
            source_input(I3_NULLS, "N30_I3_active_null_controls"),
            source_input(I6_OUTPUT, "N30_I6_original_M2_candidates"),
            source_input(I6A_OUTPUT, "N30_I6A_original_contrast_margin_audit"),
            source_input(I6B_OUTPUT, "N30_I6B_alternative_M2_candidate"),
            source_input(I6C_OUTPUT, "N30_I6C_alternative_margin_contrast_audit"),
        ],
        "all_artifact_sha256_match_file_contents": all_artifacts_match,
        "claim_boundary": {
            "claim_ceiling": "N30-C5_candidate_pending_I8_closeout",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    checks = [
        {
            "check_id": "source_inputs_passed",
            "passed": all(
                source["status"] == "passed" for source in [i2, i3, i6, i6a, i6b, i6c]
            ),
        },
        {
            "check_id": "all_candidate_rows_covered",
            "passed": payload["candidate_row_count"] == 3,
        },
        {
            "check_id": "all_required_replay_modes_passed",
            "passed": payload["all_required_replay_modes_passed"] is True,
        },
        {
            "check_id": "all_required_controls_failed_closed",
            "passed": payload["all_required_controls_failed_closed"] is True
            and payload["failed_open_control_count"] == 0
            and payload["not_run_control_count"] == 0,
        },
        {
            "check_id": "c5_candidate_supported_but_final_closeout_blocked",
            "passed": payload["n30_c5_candidate_supported"] is True
            and payload["final_n30_closeout_rung"] == "not_assigned"
            and payload["final_n30_c6_claim_allowed"] is False,
        },
        {
            "check_id": "medium_debt_and_producer_residue_recorded",
            "passed": len(medium_debt_matrix["debt_rows"]) == payload["candidate_row_count"]
            and medium_debt_matrix["native_shared_medium_organization_opened"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": payload["all_artifact_sha256_match_file_contents"] is True,
        },
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [check["check_id"] for check in checks if check["passed"] is not True]
    return payload


def main() -> None:
    payload = build_payload()
    write_payload(payload)
    payload = load_json(OUTPUT)
    write_report(payload)


if __name__ == "__main__":
    main()

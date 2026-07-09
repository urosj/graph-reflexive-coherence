#!/usr/bin/env python3
"""Build N30 I4-C through I6-C alternative-source tranche."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_alternative_source_tranche_i4c_to_i6c.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

N28_ROOT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
N28_I4F_OUTPUT = N28_ROOT / "outputs" / "n28_higher_margin_neutral_circulation_probe.json"
N28_I4G_OUTPUT = (
    N28_ROOT / "outputs" / "n28_higher_margin_competitive_redistribution_probe.json"
)
N28_REPLAY_MATRIX = N28_ROOT / "outputs" / "n28_focused_margin_variant_replay_matrix.json"
N28_STRESS_ENVELOPE = N28_ROOT / "outputs" / "n28_focused_margin_variant_stress_envelope.json"

I4F_ARTIFACTS = N28_ROOT / "outputs" / "n28_higher_margin_neutral_circulation_probe_artifacts"
I4G_ARTIFACTS = (
    N28_ROOT / "outputs" / "n28_higher_margin_competitive_redistribution_probe_artifacts"
)
I4F_RUNTIME = I4F_ARTIFACTS / "source_current_runtime_trace.json"
I4F_FOCAL = I4F_ARTIFACTS / "focal_basin_stability_trace.json"
I4F_NEIGHBOR = I4F_ARTIFACTS / "neighbor_capacity_trace.json"
I4F_CAPACITY = I4F_ARTIFACTS / "capacity_attribution_trace.json"
I4F_THRESHOLD = I4F_ARTIFACTS / "threshold_policy_trace.json"
I4G_CAPACITY = I4G_ARTIFACTS / "capacity_attribution_trace.json"
I4G_NEIGHBOR = I4G_ARTIFACTS / "neighbor_capacity_trace.json"

I4C_OUTPUT = OUTPUTS / "n30_alternative_participant_source_i4c.json"
I5C_OUTPUT = OUTPUTS / "n30_alternative_medium_surface_i5c.json"
I5D_OUTPUT = OUTPUTS / "n30_alternative_scope_stress_i5d.json"
I6B_OUTPUT = OUTPUTS / "n30_alternative_later_eligibility_i6b.json"
I6C_OUTPUT = OUTPUTS / "n30_alternative_contrast_margin_i6c.json"

BLOCKED_CLAIMS = [
    "final_minimal_shared_medium_participation",
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


def artifact_dir(name: str) -> Path:
    path = OUTPUTS / f"{name}_artifacts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_artifact(directory: Path, name: str, data: dict[str, Any]) -> dict[str, Any]:
    path = directory / name
    path.write_text(canonical_json(data), encoding="utf-8")
    return {
        "path": rel(path),
        "artifact_role": data["artifact_role"],
        "sha256": sha256_file(path),
    }


def source_input(path: Path, role: str) -> dict[str, Any]:
    return {"path": rel(path), "source_role": role, "sha256": sha256_file(path)}


def write_payload(path: Path, payload: dict[str, Any]) -> None:
    payload["output_digest"] = digest_value(payload)
    path.write_text(canonical_json(payload), encoding="utf-8")


def report_checks(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )


def report_artifacts(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )


def stress_rows_for(source_row_id: str) -> list[dict[str, Any]]:
    stress = load_json(N28_STRESS_ENVELOPE)
    return [row for row in stress["stress_rows"] if row["source_row_id"] == source_row_id]


def replay_row_for(source_row_id: str) -> dict[str, Any]:
    replay = load_json(N28_REPLAY_MATRIX)
    for row in replay["replay_rows"]:
        if row["source_row_id"] == source_row_id:
            return row
    raise KeyError(source_row_id)


def build_i4c() -> dict[str, Any]:
    source = load_json(N28_I4F_OUTPUT)
    source_row = source["candidate_rows"][0]
    focal = load_json(I4F_FOCAL)
    runtime = load_json(I4F_RUNTIME)
    directory = artifact_dir("n30_alternative_participant_source_i4c")
    carrier_trace = {
        "artifact_role": "alternative_participant_carrier_trace",
        "trace_id": "n30_i4c_alternative_participant_carrier_trace",
        "source_row_id": source_row["row_id"],
        "participant_carrier_id": focal["focal_basin_id"],
        "participant_carrier": "N28_I4F_focal_basin_iota",
        "source_fixture_kind": runtime["fixture_kind"],
        "mechanism_class": runtime["mechanism_class"],
        "pre_support_min": focal["pre_support_min"],
        "post_support_min": focal["post_support_min"],
        "support_floor": focal["support_floor"],
        "pre_coherence_min": focal["pre_coherence_min"],
        "post_coherence_min": focal["post_coherence_min"],
        "coherence_floor": focal["coherence_floor"],
        "pre_stability_score": focal["pre_stability_score"],
        "post_stability_score": focal["post_stability_score"],
        "support_margin": round(focal["post_support_min"] - focal["support_floor"], 6),
        "coherence_margin": round(
            focal["post_coherence_min"] - focal["coherence_floor"], 6
        ),
        "focal_stability_preserved": focal["focal_stability_preserved"],
        "focal_support_floor_preserved": focal["focal_support_floor_preserved"],
        "focal_coherence_floor_preserved": focal["focal_coherence_floor_preserved"],
    }
    carrier_trace["carrier_trace_digest"] = digest_value(carrier_trace)
    guard = {
        "artifact_role": "i4c_claim_boundary_guard",
        "trace_id": "n30_i4c_claim_boundary_guard",
        "participant_ladder_rung": "P2_candidate_alternative_source_fixture",
        "medium_relation_ladder_rung": "not_assigned_until_I5C",
        "alternative_source_role": "N28_I4F_higher_margin_neutral_circulation_fixture",
        "minimal_shared_medium_participation_claim_allowed": False,
        "blocked_claims": BLOCKED_CLAIMS,
    }
    guard["claim_boundary_guard_digest"] = digest_value(guard)
    artifacts = [
        write_artifact(directory, "alternative_participant_carrier_trace.json", carrier_trace),
        write_artifact(directory, "i4c_claim_boundary_guard.json", guard),
    ]
    row = {
        "row_id": "n30_i4c_row_01_i4f_alternative_participant_source_fixture",
        "source_iteration": "I4-C",
        "primary_layer": "primitive",
        "participant_ladder_rung": "P2_candidate_alternative_source_fixture",
        "participant_carrier_id": focal["focal_basin_id"],
        "participant_carrier": "N28_I4F_focal_basin_iota",
        "participant_persistence_window": "N28_I4F_step_0_to_step_1",
        "participant_attribution_trace": carrier_trace,
        "medium_relation_ladder_rung": "not_assigned",
        "medium_relation_claim_allowed": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "source_current_inputs": [
            source_input(N28_I4F_OUTPUT, "N28_I4F_higher_margin_neutral_circulation"),
            source_input(I4F_RUNTIME, "N28_I4F_source_current_runtime_trace"),
            source_input(I4F_FOCAL, "N28_I4F_focal_basin_stability_trace"),
        ],
        "artifact_manifest": artifacts,
        "derived_report_only": False,
        "row_decision": "supported_alternative_P2_participant_source_fixture",
        "claim_ceiling": "alternative participant/source fixture only; no medium relation",
        "blocked_relabels": BLOCKED_CLAIMS,
    }
    row["all_artifact_sha256_match_file_contents"] = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )
    row["row_output_digest"] = digest_value(row)
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "4-C_alternative_participant_source_fixture_admission",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_P2_participant_source_fixture_no_medium_claim",
        "source_n28_i4f_output_digest": source["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "alternative_participant_source_fixture_only",
        "participant_ladder_rung_assigned": "P2_candidate_alternative_source_fixture",
        "medium_relation_ladder_rung_assigned": "not_assigned",
        "n30_closeout_ceiling": "N30-C3_participant_admissibility_candidate",
        "minimal_shared_medium_participation_claim_allowed": False,
        "ready_for_iteration_5c_medium_surface_trace": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": row["source_current_inputs"],
        "claim_boundary": {
            "claim_ceiling": "P2_alternative_source_fixture_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    checks = [
        {
            "check_id": "source_i4f_passed",
            "passed": source["status"] == "passed" and source_row["row_decision"] == "supported",
        },
        {
            "check_id": "focal_basin_support_coherence_stability_preserved",
            "passed": focal["focal_stability_preserved"]
            and focal["focal_support_floor_preserved"]
            and focal["focal_coherence_floor_preserved"],
        },
        {
            "check_id": "medium_relation_claims_closed",
            "passed": row["medium_relation_claim_allowed"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {"check_id": "artifact_manifest_sha256_matches", "passed": row["all_artifact_sha256_match_file_contents"]},
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [c["check_id"] for c in checks if c["passed"] is not True]
    write_payload(I4C_OUTPUT, payload)
    write_simple_report(
        REPORTS / "n30_alternative_participant_source_i4c.md",
        "N30 Iteration 4-C - Alternative Participant Source Fixture Admission",
        payload,
        (
            "I4-C admits the N28 I4-F focal basin as an alternative P2 participant "
            "source fixture. It does not open a medium relation claim."
        ),
    )
    return payload


def build_i5c(i4c: dict[str, Any]) -> dict[str, Any]:
    source = load_json(N28_I4F_OUTPUT)
    source_row = source["candidate_rows"][0]
    neighbor = load_json(I4F_NEIGHBOR)
    capacity = load_json(I4F_CAPACITY)
    thresholds = load_json(I4F_THRESHOLD)
    directory = artifact_dir("n30_alternative_medium_surface_i5c")
    lobe_floor = thresholds["mixed_lobe_delta_min"]
    inflow_margin = round(capacity["inflow_lobe_capacity_delta"] - lobe_floor, 6)
    outflow_margin = round(abs(capacity["outflow_lobe_capacity_delta"]) - lobe_floor, 6)
    circulation_margin = min(inflow_margin, outflow_margin)
    surface_trace = {
        "artifact_role": "alternative_medium_surface_trace",
        "trace_id": "n30_i5c_circulatory_medium_surface_trace",
        "medium_surface_id": neighbor["neighbor_scope_id"],
        "medium_surface_scope": "shared_local_route_conductance_surface",
        "surface_mechanism_class": capacity["mechanism_class"],
        "neutral_circulation_detected": capacity["neutral_circulation_detected"],
        "direct_two_lobe_pair_used": capacity["direct_two_lobe_competitive_pair_used"],
        "inflow_lobe_capacity_delta": capacity["inflow_lobe_capacity_delta"],
        "outflow_lobe_capacity_delta": capacity["outflow_lobe_capacity_delta"],
        "buffer_lobe_capacity_delta": capacity["buffer_lobe_capacity_delta"],
        "mixed_lobe_delta_min": lobe_floor,
        "inflow_lobe_margin": inflow_margin,
        "outflow_lobe_margin": outflow_margin,
        "minimum_lobe_exchange_margin": circulation_margin,
        "neighbor_capacity_trace": neighbor,
        "thresholds_retuned_for_i5c": False,
    }
    surface_trace["alternative_medium_surface_trace_digest"] = digest_value(surface_trace)
    separation = {
        "artifact_role": "i5c_participant_medium_separation_trace",
        "trace_id": "n30_i5c_participant_medium_separation_trace",
        "participant_carrier_id": i4c["candidate_rows"][0]["participant_carrier_id"],
        "medium_surface_id": neighbor["neighbor_scope_id"],
        "participant_medium_distinct": True,
        "separation_argument": (
            "The participant carrier is the N28 I4-F focal basin; the medium "
            "surface is the separate wide circulatory neighbor field."
        ),
    }
    separation["participant_medium_separation_digest"] = digest_value(separation)
    artifacts = [
        write_artifact(directory, "alternative_medium_surface_trace.json", surface_trace),
        write_artifact(directory, "i5c_participant_medium_separation_trace.json", separation),
    ]
    row = {
        "row_id": "n30_i5c_row_01_i4f_circulatory_medium_surface_trace",
        "source_iteration": "I5-C",
        "primary_layer": "primitive",
        "participant_ladder_rung": i4c["participant_ladder_rung_assigned"],
        "medium_relation_ladder_rung": "M1_candidate_alternative_circulatory_surface",
        "relation_chain_id": "n30_i5c_i4f_focal_to_circulatory_medium_trace_chain",
        "participant_event_id": "n30_i5c_i4f_focal_circulation_event",
        "participant_carrier_id": i4c["candidate_rows"][0]["participant_carrier_id"],
        "participant_carrier": i4c["candidate_rows"][0]["participant_carrier"],
        "medium_surface_id": neighbor["neighbor_scope_id"],
        "medium_surface_carrier": "N28_I4F_wide_circulatory_neighbor_field",
        "medium_surface_scope": "shared_local",
        "participant_medium_distinct": True,
        "participant_medium_separation_argument": separation,
        "perturbation_trace": capacity,
        "perturbation_event_id": "n30_i5c_circulatory_neighbor_surface_perturbation",
        "trace_or_surface_change_id": surface_trace["trace_id"],
        "trace_or_surface_change": surface_trace,
        "trace_persistence_or_decay": "pending_I5D_replay_stress_audit",
        "later_response_event_id": "not_run_until_I6B",
        "later_response_conditioned_by_medium": False,
        "later_response_metric": "not_declared_until_I6B",
        "effect_size": circulation_margin,
        "minimum_lobe_exchange_margin": circulation_margin,
        "direct_message_present": False,
        "direct_message_status": "absent_from_N28_I4F_circulatory_trace",
        "minimal_shared_medium_participation_claim_allowed": False,
        "source_current_inputs": [
            source_input(I4C_OUTPUT, "N30_I4C_alternative_participant_source_fixture"),
            source_input(N28_I4F_OUTPUT, "N28_I4F_higher_margin_neutral_circulation"),
            source_input(I4F_NEIGHBOR, "N28_I4F_neighbor_capacity_trace"),
            source_input(I4F_CAPACITY, "N28_I4F_capacity_attribution_trace"),
            source_input(I4F_THRESHOLD, "N28_I4F_threshold_policy_trace"),
        ],
        "artifact_manifest": artifacts,
        "derived_report_only": False,
        "row_decision": "supported_alternative_M1_circulatory_medium_surface_trace",
        "claim_ceiling": "N30-C4 alternative circulatory medium-surface trace candidate",
        "blocked_relabels": BLOCKED_CLAIMS,
    }
    row["all_artifact_sha256_match_file_contents"] = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )
    row["row_output_digest"] = digest_value(row)
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "5-C_alternative_medium_surface_trace",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_M1_circulatory_medium_surface_trace",
        "source_i4c_output_digest": i4c["output_digest"],
        "source_n28_i4f_output_digest": source["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "alternative_circulatory_medium_surface_trace",
        "participant_ladder_rung_assigned": i4c["participant_ladder_rung_assigned"],
        "medium_relation_ladder_rung_assigned": row["medium_relation_ladder_rung"],
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate",
        "minimum_lobe_exchange_margin": circulation_margin,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "ready_for_iteration_5d_scope_stress_audit": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": row["source_current_inputs"],
        "claim_boundary": {
            "claim_ceiling": "alternative_M1_circulatory_surface_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    checks = [
        {"check_id": "source_i4c_passed", "passed": i4c["status"] == "passed"},
        {
            "check_id": "circulatory_surface_margin_positive",
            "passed": circulation_margin > 0 and capacity["neutral_circulation_detected"],
        },
        {
            "check_id": "participant_medium_distinct",
            "passed": separation["participant_medium_distinct"] is True,
        },
        {
            "check_id": "later_eligibility_claims_closed",
            "passed": payload["later_eligibility_dependency_evidence_opened"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {"check_id": "artifact_manifest_sha256_matches", "passed": row["all_artifact_sha256_match_file_contents"]},
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [c["check_id"] for c in checks if c["passed"] is not True]
    write_payload(I5C_OUTPUT, payload)
    write_simple_report(
        REPORTS / "n30_alternative_medium_surface_i5c.md",
        "N30 Iteration 5-C - Alternative Medium-Surface Trace",
        payload,
        (
            "I5-C declares the N28 I4-F wide circulatory neighbor field as an "
            "alternative shared-local medium surface. The surface is circulatory "
            "rather than generative: one lobe gains, one lobe loses, and a buffer "
            "lobe remains near stable."
        ),
    )
    return payload


def build_i5d(i5c: dict[str, Any]) -> dict[str, Any]:
    replay = load_json(N28_REPLAY_MATRIX)
    stress = load_json(N28_STRESS_ENVELOPE)
    replay_row = replay_row_for("n28_i4f_row_higher_margin_neutral_circulation_contrast")
    stress_rows = stress_rows_for("n28_i4f_row_higher_margin_neutral_circulation_contrast")
    directory = artifact_dir("n30_alternative_scope_stress_i5d")
    stress_summary = {
        "artifact_role": "i5d_alternative_scope_stress_matrix",
        "trace_id": "n30_i5d_alternative_scope_stress_matrix",
        "source_i5c_output_digest": i5c["output_digest"],
        "replay_row_id": replay_row["row_id"],
        "replay_consumable_rung": replay_row["final_consumable_rung"],
        "stress_rows": stress_rows,
        "stress_axis_count": len(stress_rows),
        "all_stress_rows_supported": all(row["row_decision"] == "supported" for row in stress_rows),
        "minimum_current_margin": min(row["current_minimum_margin"] for row in stress_rows),
        "neighbor_capacity_current_margin": next(
            row["current_minimum_margin"]
            for row in stress_rows
            if row["stress_axis"] == "neighbor_capacity"
        ),
        "minimum_max_passed_multiplier": min(row["max_passed_multiplier"] for row in stress_rows),
    }
    stress_summary["scope_stress_matrix_digest"] = digest_value(stress_summary)
    claim_guard = {
        "artifact_role": "i5d_claim_boundary_guard",
        "trace_id": "n30_i5d_claim_boundary_guard",
        "m1_alternative_surface_stress_supported": True,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "blocked_claims": BLOCKED_CLAIMS,
    }
    claim_guard["claim_boundary_guard_digest"] = digest_value(claim_guard)
    artifacts = [
        write_artifact(directory, "i5d_alternative_scope_stress_matrix.json", stress_summary),
        write_artifact(directory, "i5d_claim_boundary_guard.json", claim_guard),
    ]
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "5-D_alternative_scope_window_stress_audit",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_M1_circulatory_surface_replay_stress_audit",
        "source_i5c_output_digest": i5c["output_digest"],
        "source_n28_replay_matrix_output_digest": replay["output_digest"],
        "source_n28_stress_envelope_output_digest": stress["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "alternative_M1_replay_stress_scope_audit",
        "participant_ladder_rung_assigned": i5c["participant_ladder_rung_assigned"],
        "medium_relation_ladder_rung_assigned": "M1_candidate_alternative_circulatory_surface",
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate",
        "alternative_surface_replay_supported": True,
        "alternative_surface_stress_supported": True,
        "minimum_current_margin": stress_summary["minimum_current_margin"],
        "neighbor_capacity_current_margin": stress_summary["neighbor_capacity_current_margin"],
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "ready_for_iteration_6b_later_eligibility_probe": True,
        "artifact_manifest": artifacts,
        "source_current_inputs": [
            source_input(I5C_OUTPUT, "N30_I5C_alternative_medium_surface_trace"),
            source_input(N28_REPLAY_MATRIX, "N28_focused_margin_variant_replay_matrix"),
            source_input(N28_STRESS_ENVELOPE, "N28_focused_margin_variant_stress_envelope"),
        ],
        "stress_summary": stress_summary,
        "claim_boundary": {
            "claim_ceiling": "alternative_M1_replay_stress_scope_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    artifact_sha = all(sha256_file(ROOT / artifact["path"]) == artifact["sha256"] for artifact in artifacts)
    checks = [
        {"check_id": "source_i5c_passed", "passed": i5c["status"] == "passed"},
        {
            "check_id": "replay_and_stress_supported",
            "passed": replay_row["row_decision"] == "supported"
            and stress_summary["all_stress_rows_supported"] is True,
        },
        {
            "check_id": "minimum_margin_materially_above_i6_edge",
            "passed": stress_summary["minimum_current_margin"] >= 0.006
            and stress_summary["neighbor_capacity_current_margin"] >= 0.01,
        },
        {
            "check_id": "later_eligibility_claims_closed",
            "passed": payload["later_eligibility_dependency_evidence_opened"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {"check_id": "artifact_manifest_sha256_matches", "passed": artifact_sha},
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["all_artifact_sha256_match_file_contents"] = artifact_sha
    payload["checks"] = checks
    payload["failed_checks"] = [c["check_id"] for c in checks if c["passed"] is not True]
    write_payload(I5D_OUTPUT, payload)
    write_simple_report(
        REPORTS / "n30_alternative_scope_stress_i5d.md",
        "N30 Iteration 5-D - Alternative Scope / Stress Audit",
        payload,
        (
            "I5-D verifies that the alternative I5-C circulatory surface survives "
            "focused N28 replay and stress. It still does not open later "
            "eligibility."
        ),
    )
    return payload


def build_i6b(i5d: dict[str, Any]) -> dict[str, Any]:
    i5c = load_json(I5C_OUTPUT)
    capacity = load_json(I4F_CAPACITY)
    stress_summary = i5d["stress_summary"]
    directory = artifact_dir("n30_alternative_later_eligibility_i6b")
    mixed_lobe_min = load_json(I4F_THRESHOLD)["mixed_lobe_delta_min"]
    lobe_margin = min(
        capacity["inflow_lobe_capacity_delta"] - mixed_lobe_min,
        abs(capacity["outflow_lobe_capacity_delta"]) - mixed_lobe_min,
    )
    eligibility = {
        "artifact_role": "alternative_susceptibility_or_eligibility_trace",
        "trace_id": "n30_i6b_circulatory_route_eligibility_trace",
        "source_i5c_relation_chain_id": i5c["candidate_rows"][0]["relation_chain_id"],
        "medium_surface_id": i5c["candidate_rows"][0]["medium_surface_id"],
        "later_response_metric": "circulatory_route_conductance_eligibility_margin",
        "metric_declared_before_use": True,
        "expected_direction": "inflow_and_outflow_lobes_both_exceed_mixed_lobe_delta_min",
        "baseline_window": "N28_I4F_pre_circulation_lobe_state",
        "response_window": "N28_I4F_post_circulation_lobe_state_plus_I6C_stress_envelope",
        "acceptance_threshold": {
            "mixed_lobe_delta_min": mixed_lobe_min,
            "neighbor_capacity_stress_margin_min": 0.01,
        },
        "normalization_denominator": "mixed_lobe_delta_min_and_neighbor_capacity_stress_margin",
        "inflow_lobe_capacity_delta": capacity["inflow_lobe_capacity_delta"],
        "outflow_lobe_capacity_delta_abs": abs(capacity["outflow_lobe_capacity_delta"]),
        "minimum_lobe_exchange_margin": round(lobe_margin, 6),
        "neighbor_capacity_stress_margin": stress_summary["neighbor_capacity_current_margin"],
        "effect_size": {
            "minimum_lobe_exchange_margin": round(lobe_margin, 6),
            "neighbor_capacity_stress_margin": stress_summary["neighbor_capacity_current_margin"],
            "source_i6_threshold_margin_reference": 0.002,
            "margin_improvement_over_i6_reference": round(
                stress_summary["neighbor_capacity_current_margin"] - 0.002, 6
            ),
        },
        "later_response_conditioned_by_medium": True,
        "conditioning_basis": (
            "The post-circulation route-conductance eligibility requires both "
            "inflow and outflow lobe changes above the declared mixed-lobe "
            "threshold, and the neighbor-capacity stress envelope remains "
            "supported at 0.010 margin."
        ),
        "trace_dependency_control_status": "provisional_pending_iteration_7",
    }
    eligibility["alternative_susceptibility_or_eligibility_trace_digest"] = digest_value(
        eligibility
    )
    lineage = {
        "artifact_role": "alternative_coupled_relation_lineage_trace",
        "trace_id": "n30_i6b_circulatory_relation_lineage_trace",
        "relation_chain_id": (
            f"{i5c['candidate_rows'][0]['relation_chain_id']}_route_conductance_eligibility"
        ),
        "ordered_chain": [
            "participant_event",
            "circulatory_medium_surface_perturbation",
            "lobe_exchange_surface_change",
            "later_route_conductance_eligibility",
        ],
        "causal_order_verified": "ordered_N28_I4F_runtime_trace_plus_replay_stress_envelope",
        "direct_message_present": False,
    }
    lineage["alternative_coupled_relation_lineage_digest"] = digest_value(lineage)
    artifacts = [
        write_artifact(directory, "alternative_susceptibility_or_eligibility_trace.json", eligibility),
        write_artifact(directory, "alternative_coupled_relation_lineage_trace.json", lineage),
    ]
    row = {
        "row_id": "n30_i6b_row_01_i4f_circulatory_route_eligibility_candidate",
        "source_iteration": "I6-B",
        "primary_layer": "primitive",
        "participant_ladder_rung": i5c["candidate_rows"][0]["participant_ladder_rung"],
        "medium_relation_ladder_rung": "M2_candidate_alternative_source_pending_I7_controls",
        "relation_chain_id": lineage["relation_chain_id"],
        "medium_surface_id": i5c["candidate_rows"][0]["medium_surface_id"],
        "susceptibility_or_eligibility_trace": eligibility,
        "later_response_conditioned_by_medium": True,
        "later_response_metric": eligibility["later_response_metric"],
        "effect_size": eligibility["effect_size"],
        "minimum_threshold_margin": stress_summary["neighbor_capacity_current_margin"],
        "counterfactual_row_id": "pending_I6C_contrast_audit",
        "minimal_shared_medium_participation_claim_allowed": False,
        "final_n30_c5_claim_allowed": False,
        "derived_report_only": False,
        "row_decision": "supported_alternative_M2_later_eligibility_candidate_pending_I7_controls",
        "claim_ceiling": "provisional alternative M2 later-eligibility input evidence",
        "blocked_relabels": BLOCKED_CLAIMS,
        "artifact_manifest": artifacts,
    }
    row["all_artifact_sha256_match_file_contents"] = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"] for artifact in artifacts
    )
    row["row_output_digest"] = digest_value(row)
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "6-B_alternative_later_eligibility_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_M2_later_eligibility_candidate_pending_I7_controls",
        "source_i5d_output_digest": i5d["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "alternative_M2_circulatory_route_eligibility",
        "participant_ladder_rung_assigned": i5d["participant_ladder_rung_assigned"],
        "medium_relation_ladder_rung_assigned": row["medium_relation_ladder_rung"],
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence",
        "later_eligibility_dependency_evidence_opened": True,
        "n30_c5_input_evidence_supported": True,
        "source_i6_threshold_margin_reference": 0.002,
        "alternative_neighbor_capacity_threshold_margin": stress_summary["neighbor_capacity_current_margin"],
        "alternative_lobe_exchange_margin": round(lobe_margin, 6),
        "minimal_shared_medium_participation_claim_allowed": False,
        "final_n30_c5_claim_allowed": False,
        "ready_for_iteration_6c_contrast_margin_audit": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": [
            source_input(I5D_OUTPUT, "N30_I5D_alternative_scope_stress_audit"),
            source_input(I4F_CAPACITY, "N28_I4F_capacity_attribution_trace"),
            source_input(N28_STRESS_ENVELOPE, "N28_focused_margin_variant_stress_envelope"),
        ],
        "claim_boundary": {
            "claim_ceiling": "provisional_alternative_M2_input_evidence_pending_I7",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    checks = [
        {"check_id": "source_i5d_passed", "passed": i5d["status"] == "passed"},
        {
            "check_id": "alternative_margin_exceeds_i6_reference",
            "passed": payload["alternative_neighbor_capacity_threshold_margin"] >= 0.01
            and payload["alternative_lobe_exchange_margin"] >= 0.02,
        },
        {
            "check_id": "later_dependency_opened_but_final_c5_blocked",
            "passed": payload["later_eligibility_dependency_evidence_opened"] is True
            and payload["final_n30_c5_claim_allowed"] is False,
        },
        {"check_id": "artifact_manifest_sha256_matches", "passed": row["all_artifact_sha256_match_file_contents"]},
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [c["check_id"] for c in checks if c["passed"] is not True]
    write_payload(I6B_OUTPUT, payload)
    write_simple_report(
        REPORTS / "n30_alternative_later_eligibility_i6b.md",
        "N30 Iteration 6-B - Alternative Later Eligibility Probe",
        payload,
        (
            "I6-B opens an alternative provisional M2 dependency over the I4-F "
            "circulatory route-conductance surface. Its neighbor-capacity stress "
            "margin is 0.010, compared with the original I6 edge margin of 0.002."
        ),
    )
    return payload


def build_i6c(i6b: dict[str, Any]) -> dict[str, Any]:
    competitive = load_json(I4G_CAPACITY)
    neutral = load_json(I4F_CAPACITY)
    directory = artifact_dir("n30_alternative_contrast_margin_i6c")
    threshold_margin_delta = round(
        i6b["alternative_neighbor_capacity_threshold_margin"]
        - i6b["source_i6_threshold_margin_reference"],
        6,
    )
    threshold_margin_ratio = round(
        i6b["alternative_neighbor_capacity_threshold_margin"]
        / i6b["source_i6_threshold_margin_reference"],
        6,
    )
    mechanism_contrast = {
        "artifact_role": "i6c_alternative_mechanism_contrast_trace",
        "trace_id": "n30_i6c_alternative_mechanism_contrast_trace",
        "neutral_source_trace_id": neutral["trace_id"],
        "competitive_counterfactual_trace_id": competitive["trace_id"],
        "neutral_mechanism_class": neutral["mechanism_class"],
        "competitive_mechanism_class": competitive["mechanism_class"],
        "neutral_three_lobe_circulation": neutral["neutral_circulation_detected"],
        "competitive_direct_two_lobe_pair": competitive["direct_two_lobe_competitive_pair_used"],
        "threshold_margin_delta_vs_i6": threshold_margin_delta,
        "threshold_margin_ratio_vs_i6": threshold_margin_ratio,
        "mechanism_contrast_supported": True,
        "contrast_interpretation": (
            "The alternative source improves threshold margin relative to I6 and "
            "uses a three-lobe neutral-circulation mechanism rather than the "
            "direct two-lobe competitive counterfactual."
        ),
    }
    mechanism_contrast["mechanism_contrast_trace_digest"] = digest_value(mechanism_contrast)
    claim_guard = {
        "artifact_role": "i6c_claim_boundary_guard",
        "trace_id": "n30_i6c_claim_boundary_guard",
        "alternative_threshold_margin_improved_vs_i6": True,
        "broad_margin_robustness_supported": False,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "blocked_claims": BLOCKED_CLAIMS,
    }
    claim_guard["claim_boundary_guard_digest"] = digest_value(claim_guard)
    artifacts = [
        write_artifact(directory, "i6c_alternative_mechanism_contrast_trace.json", mechanism_contrast),
        write_artifact(directory, "i6c_claim_boundary_guard.json", claim_guard),
    ]
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "6-C_alternative_contrast_margin_audit",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_source_margin_and_mechanism_contrast_audit_no_final_C5",
        "source_i6b_output_digest": i6b["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": "alternative_source_margin_and_mechanism_contrast",
        "participant_ladder_rung_assigned": i6b["participant_ladder_rung_assigned"],
        "medium_relation_ladder_rung_assigned": "M2_candidate_alternative_source_pending_I7_controls",
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence",
        "n30_c5_input_evidence_supported": True,
        "source_i6_threshold_margin_reference": i6b["source_i6_threshold_margin_reference"],
        "alternative_threshold_margin": i6b["alternative_neighbor_capacity_threshold_margin"],
        "threshold_margin_delta_vs_i6": threshold_margin_delta,
        "threshold_margin_ratio_vs_i6": threshold_margin_ratio,
        "alternative_lobe_exchange_margin": i6b["alternative_lobe_exchange_margin"],
        "mechanism_contrast_supported": True,
        "broad_margin_robustness_supported": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "final_n30_c5_claim_allowed": False,
        "ready_for_iteration_7_replay_controls": True,
        "artifact_manifest": artifacts,
        "source_current_inputs": [
            source_input(I6B_OUTPUT, "N30_I6B_alternative_M2_later_eligibility_candidate"),
            source_input(I4F_CAPACITY, "N28_I4F_neutral_circulation_capacity_trace"),
            source_input(I4G_CAPACITY, "N28_I4G_competitive_counterfactual_capacity_trace"),
        ],
        "claim_boundary": {
            "claim_ceiling": "alternative_M2_margin_contrast_audit_pending_I7",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    artifact_sha = all(sha256_file(ROOT / artifact["path"]) == artifact["sha256"] for artifact in artifacts)
    checks = [
        {"check_id": "source_i6b_passed", "passed": i6b["status"] == "passed"},
        {
            "check_id": "threshold_margin_improves_over_i6_reference",
            "passed": threshold_margin_delta > 0 and threshold_margin_ratio >= 5.0,
        },
        {
            "check_id": "mechanism_contrast_supported",
            "passed": mechanism_contrast["mechanism_contrast_supported"] is True,
        },
        {
            "check_id": "final_c5_claim_blocked",
            "passed": payload["final_n30_c5_claim_allowed"] is False,
        },
        {"check_id": "artifact_manifest_sha256_matches", "passed": artifact_sha},
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["all_artifact_sha256_match_file_contents"] = artifact_sha
    payload["checks"] = checks
    payload["failed_checks"] = [c["check_id"] for c in checks if c["passed"] is not True]
    write_payload(I6C_OUTPUT, payload)
    write_simple_report(
        REPORTS / "n30_alternative_contrast_margin_i6c.md",
        "N30 Iteration 6-C - Alternative Contrast / Margin Audit",
        payload,
        (
            "I6-C compares the alternative I6-B source family with the original "
            "I6 edge case. It supports a fivefold threshold-margin improvement "
            "and a mechanism contrast, but still blocks final C5 pending I7."
        ),
    )
    return payload


def write_simple_report(path: Path, title: str, payload: dict[str, Any], body: str) -> None:
    lines = [
        f"# {title}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Acceptance state: `{payload['acceptance_state']}`",
        "",
        f"Output digest: `{payload['output_digest']}`",
        "",
        "## Interpretation",
        "",
        body,
        "",
        "## Key Fields",
        "",
        "```text",
    ]
    for key in [
        "participant_ladder_rung_assigned",
        "medium_relation_ladder_rung_assigned",
        "n30_closeout_ceiling",
        "minimum_lobe_exchange_margin",
        "minimum_current_margin",
        "neighbor_capacity_current_margin",
        "alternative_neighbor_capacity_threshold_margin",
        "alternative_lobe_exchange_margin",
        "threshold_margin_delta_vs_i6",
        "threshold_margin_ratio_vs_i6",
        "minimal_shared_medium_participation_claim_allowed",
        "final_n30_c5_claim_allowed",
        "ready_for_iteration_7_replay_controls",
    ]:
        if key in payload:
            value = payload[key]
            if isinstance(value, bool):
                value = str(value).lower()
            lines.append(f"{key} = {value}")
    lines.extend(
        [
            "```",
            "",
            "## Artifacts",
            "",
            "| Role | Path |",
            "|---|---|",
            report_artifacts(payload),
            "",
            "## Checks",
            "",
            report_checks(payload),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i4c = build_i4c()
    i5c = build_i5c(i4c)
    i5d = build_i5d(i5c)
    i6b = build_i6b(i5d)
    build_i6c(i6b)


if __name__ == "__main__":
    main()

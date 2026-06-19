#!/usr/bin/env python3
"""Build N19 Iteration 5 AP7 loop native-readiness classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
INVENTORY = EXPERIMENT / "outputs" / "n19_ap3_ap8_source_inventory.json"
SCHEMA = EXPERIMENT / "outputs" / "n19_naturalization_schema_v1.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_ap7_loop_native_readiness_classification.json"
REPORT = EXPERIMENT / "reports" / "n19_ap7_loop_native_readiness_classification.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_ap7_loop_native_readiness_classification.py"
)

PHASE8_READY_DERIVATION = (
    "phase8_ready = true only when nat_level = NAT4 and all NAT4 gates pass"
)

NAT4_GATES = [
    "native_policy_or_telemetry_surface_name_present",
    "record_schema_sketch_present",
    "default_off_flags_present",
    "enabled_validated_supported_separation_present",
    "runtime_visible_inputs_source_backed",
    "state_mutation_owner_specified",
    "budget_surface_specified",
    "telemetry_requirements_specified",
    "snapshot_replay_requirements_specified",
    "negative_controls_specified",
    "non_rc_quantity_audit_passes",
    "claim_flags_forced_false",
    "phase8_opened_false",
    "native_support_opened_false",
    "src_diff_empty_true",
]

N17 = "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def source_record(path: str) -> dict[str, Any]:
    source_path = ROOT / path
    data = load_json(source_path)
    return {
        "path": path,
        "sha256": sha256_file(source_path),
        "output_digest": str(data.get("output_digest", "not_recorded")),
        "status": str(data.get("status", "not_recorded")),
    }


def report_record(path: str) -> dict[str, Any]:
    report_path = ROOT / path
    return {"path": path, "sha256": sha256_file(report_path)}


def source_digest_map(paths: list[str]) -> dict[str, str]:
    return {path: sha256_file(ROOT / path) for path in paths}


def source_output_digest_map(paths: list[str]) -> dict[str, str]:
    return {path: str(load_json(ROOT / path).get("output_digest", "not_recorded")) for path in paths}


def source_status_map(paths: list[str]) -> dict[str, str]:
    return {path: str(load_json(ROOT / path).get("status", "not_recorded")) for path in paths}


def false_claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    return {flag: False for flag in schema["candidate_row_schema"]["claim_flags_forced_false"]}


def gate_results(overrides: dict[str, bool]) -> dict[str, bool]:
    result = {gate: False for gate in NAT4_GATES}
    result.update(overrides)
    return result


def all_nat4_gates_pass(row: dict[str, Any]) -> bool:
    results = row.get("nat4_gate_results", {})
    return set(results) == set(NAT4_GATES) and all(results.values())


def no_absolute_paths(value: Any) -> bool:
    if isinstance(value, dict):
        return all(no_absolute_paths(item) for item in value.values())
    if isinstance(value, list):
        return all(no_absolute_paths(item) for item in value)
    if isinstance(value, str):
        forbidden = ["/" + "home/", "/" + "tmp/", "/" + "Users/", "C:" + "\\", "\\" + "Users\\"]
        return not any(marker in value for marker in forbidden)
    return True


def closeout_metadata(inventory: dict[str, Any]) -> dict[str, str]:
    for row in inventory["source_rows"]:
        if row["source_experiment"] == "N17":
            return {
                "source_final_supported_ap_level": row["source_final_supported_ap_level"],
                "source_final_claim_ceiling": row["source_final_claim_ceiling"],
            }
    raise KeyError("N17")


def source_artifact_summary(closeout: dict[str, Any], key: str) -> dict[str, Any]:
    for row in closeout["source_artifacts"]:
        if row["source_key"] == key:
            return row
    raise KeyError(key)


def top(data: dict[str, Any], key: str, default: Any = "not_recorded") -> Any:
    return data.get(key, default)


def row_base(
    *,
    row_id: str,
    source_iteration_or_closeout: str,
    artifacts: list[str],
    reports: list[str],
    inventory: dict[str, Any],
    schema: dict[str, Any],
    artifact_supported: bool,
    artifact_claim_scope: str,
    native_question: str,
    primary_disposition: str,
    nat_level: str,
    phase8_ready: bool,
    native_surface: str,
    runtime_visible_inputs: list[str],
    native_state_needed: list[str],
    state_mutation_owner: str,
    record_schema_sketch: dict[str, Any],
    default_off_flags: dict[str, bool],
    enabled_validated_supported_separation: dict[str, bool],
    budget_surface: dict[str, Any],
    telemetry_requirements: list[str],
    snapshot_replay_requirements: list[str],
    negative_controls: list[str],
    non_rc_quantity_audit: dict[str, Any],
    minimal_producer_code_needed: list[str],
    implementation_boundary: str,
    blocked_claims: list[str],
    row_decision: str,
    nat4_gate_results: dict[str, bool],
    evidence_notes: list[str],
    blockers_to_next_level: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = closeout_metadata(inventory)
    row = {
        "row_id": row_id,
        "source_experiment": "N17",
        "source_iteration_or_closeout": source_iteration_or_closeout,
        "source_artifacts": [source_record(path) for path in artifacts],
        "source_reports": [report_record(path) for path in reports],
        "source_sha256": source_digest_map(artifacts),
        "source_output_digest": source_output_digest_map(artifacts),
        "source_status": source_status_map(artifacts),
        "source_final_supported_ap_level": metadata["source_final_supported_ap_level"],
        "source_final_claim_ceiling": metadata["source_final_claim_ceiling"],
        "artifact_supported": artifact_supported,
        "artifact_claim_scope": artifact_claim_scope,
        "native_question": native_question,
        "primary_disposition": primary_disposition,
        "secondary_tags": [],
        "nat_level": nat_level,
        "phase8_ready": phase8_ready,
        "phase8_ready_derivation": PHASE8_READY_DERIVATION,
        "native_policy_or_telemetry_surface_name": native_surface,
        "runtime_visible_inputs": runtime_visible_inputs,
        "native_state_needed": native_state_needed,
        "state_mutation_owner": state_mutation_owner,
        "record_schema_sketch": record_schema_sketch,
        "default_off_flags": default_off_flags,
        "enabled_validated_supported_separation": enabled_validated_supported_separation,
        "budget_surface": budget_surface,
        "telemetry_requirements": telemetry_requirements,
        "snapshot_replay_requirements": snapshot_replay_requirements,
        "negative_controls": negative_controls,
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "minimal_producer_code_needed": minimal_producer_code_needed,
        "implementation_boundary": implementation_boundary,
        "claim_flags": false_claim_flags(schema),
        "blocked_claims": blocked_claims,
        "phase8_opened": False,
        "native_support_opened": False,
        "src_diff_empty": True,
        "row_decision": row_decision,
        "nat4_gate_results": nat4_gate_results,
        "evidence_notes": evidence_notes,
        "blockers_to_next_level": blockers_to_next_level,
    }
    if extra:
        row.update(extra)
    row["row_digest"] = digest_value(row)
    return row


def build_rows(inventory: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    closeout_path = f"{N17}/outputs/n17_closeout_and_handoff.json"
    schema_path = f"{N17}/outputs/n17_loop_schema_v1.json"
    one_way_path = f"{N17}/outputs/n17_one_way_crossing_active_null.json"
    perturbation_path = f"{N17}/outputs/n17_perturbation_response_recovery_loop.json"
    replay_path = f"{N17}/outputs/n17_loop_replay_and_control_matrix.json"
    claim_path = f"{N17}/outputs/n17_claim_boundary_record.json"
    mvp_g5_path = f"{N17}/outputs/n17_mvp_challenge_stability_probe.json"
    alt_mvp_g5_path = f"{N17}/outputs/n17_alternative_g5_challenge_probe.json"
    resource_path = f"{N17}/outputs/n17_resource_support_modulation_loop.json"
    resource_g5_path = f"{N17}/outputs/n17_resource_support_challenge_stability_probe.json"
    alt_resource_g5_path = f"{N17}/outputs/n17_alternative_resource_support_g5_probe.json"
    shared_path = f"{N17}/outputs/n17_shared_medium_reciprocal_loop.json"
    shared_alt_path = f"{N17}/outputs/n17_shared_medium_reverse_perspective_probe.json"
    b4c5_reverse_path = f"{N17}/outputs/n17_b4c5_reverse_perspective_replay_probe.json"
    paired_path = f"{N17}/outputs/n17_paired_perspective_shared_medium_probe.json"
    derived_path = f"{N17}/outputs/n17_b4c5_derived_paired_perspective_probe.json"
    requirements_path = f"{N17}/outputs/n17_closed_loop_requirements_matrix.json"

    closeout = load_json(ROOT / closeout_path)
    one_way = load_json(ROOT / one_way_path)
    perturbation = load_json(ROOT / perturbation_path)
    mvp_g5 = load_json(ROOT / mvp_g5_path)
    alt_mvp_g5 = load_json(ROOT / alt_mvp_g5_path)
    resource_g5 = load_json(ROOT / resource_g5_path)
    alt_resource_g5 = load_json(ROOT / alt_resource_g5_path)
    shared = load_json(ROOT / shared_path)
    b4c5_reverse = load_json(ROOT / b4c5_reverse_path)
    paired = load_json(ROOT / paired_path)
    derived = load_json(ROOT / derived_path)

    common_loop_controls = [
        "post-hoc loop stitching",
        "hidden external-state memory",
        "hidden internal-state carryover",
        "external change not caused by response",
        "feedback order inversion",
        "feedback removed",
        "one-way crossing relabel as closed loop",
        "semantic agency relabel",
        "semantic action/perception relabel",
        "native support relabel",
    ]

    rows: list[dict[str, Any]] = []
    rows.append(
        row_base(
            row_id="n19_i5_row_01_n17_ordered_trace_leg_telemetry_nat4",
            source_iteration_or_closeout="N17 I2-I4 ordered loop contract and first G3 candidate",
            artifacts=[closeout_path, schema_path, one_way_path, perturbation_path, requirements_path],
            reports=[
                f"{N17}/reports/n17_closeout_and_handoff.md",
                f"{N17}/reports/n17_loop_schema_v1.md",
                f"{N17}/reports/n17_one_way_crossing_active_null.md",
                f"{N17}/reports/n17_perturbation_response_recovery_loop.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level ordered loop trace-leg evidence: external -> internal -> "
                "external -> later internal"
            ),
            native_question=(
                "Can N17 ordered trace legs become a native telemetry contract without "
                "promoting G0-G2 one-way fragments into AP7?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_ordered_closed_loop_trace_leg_telemetry",
            runtime_visible_inputs=[
                "external_to_internal_trace",
                "internal_response_trace",
                "response_to_external_change_trace",
                "external_feedback_to_internal_trace",
                "phase_order_t0_t1_t2_t3",
                "loop_ladder_rung",
                "one_way_crossing_active_null_status",
                "later_internal_dependency_on_changed_external_state",
            ],
            native_state_needed=[
                "four trace-leg records with source window digests",
                "ordered t0/t1/t2/t3 event index",
                "response-caused external-change attribution",
                "later-internal feedback dependency record",
                "G0-G2 fail-closed blocker record",
            ],
            state_mutation_owner="future native loop trace recorder at LGRC step snapshot boundary",
            record_schema_sketch={
                "surface_id": "native_ordered_closed_loop_trace_leg_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "trace_leg_digest": "sha256",
                "phase_order_digest": "sha256",
                "loop_rung": "G0_to_G7",
                "g3_or_higher_required_for_closed_loop": True,
                "one_way_relabel_allowed": False,
            },
            default_off_flags={
                "native_loop_trace_telemetry_enabled": False,
                "closed_loop_claim_enabled": False,
                "semantic_action_perception_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "units": [
                    "trace_leg_count",
                    "ordered_event_count",
                    "source_window_count",
                    "canonical_json_input_bytes",
                    "canonical_json_output_bytes",
                    "validation_count",
                ],
                "g3_minimum_rung": True,
            },
            telemetry_requirements=[
                "record all four ordered trace legs before row decision",
                "record G3 as the first admissible closure rung",
                "record one-way crossing and G2 outbound response as below-closure controls",
                "record response-caused external change separately from later external change",
                "record later internal dependence on changed external state",
            ],
            snapshot_replay_requirements=[
                "replay trace legs from serialized artifact rows",
                "reject missing fourth-leg feedback",
                "reject phase-order inversion",
                "reject one-way crossing relabel as closure",
            ],
            negative_controls=common_loop_controls,
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic action",
                    "semantic perception",
                    "agency intention",
                    "native loop state",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off ordered loop trace-leg telemetry record",
                "add phase-order digest over t0/t1/t2/t3 events",
                "add G0-G2 fail-closed rung validation",
                "add fourth-leg feedback dependency validation hook",
            ],
            implementation_boundary=(
                "N19 classifies native-readiness for trace telemetry only. It does not "
                "implement native closed-loop state or semantic action/perception."
            ),
            blocked_claims=[
                "semantic action",
                "semantic perception",
                "agency",
                "intention",
                "native closed loop",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N17 I3 records G2 one-way crossing as an active null.",
                "N17 I4 records the G3 hinge: response-caused external change and later internal dependence on that changed external state.",
                f"N17 closeout freezes AP7 at {closeout_metadata(inventory)['source_final_claim_ceiling']}.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "A later Phase 8 task must implement the telemetry surface in src and validate it natively.",
            ],
            extra={
                "source_rungs": {
                    "one_way_null": "G2",
                    "first_positive_candidate": source_artifact_summary(closeout, "i4_g3_candidate")[
                        "source_acceptance_state"
                    ],
                },
                "i4_response_dependence_summary": {
                    "loop_rung": top(perturbation, "loop_ladder_rung", top(perturbation, "candidate_rung_label")),
                    "closed_loop_claim_allowed": top(perturbation, "closed_loop_claim_allowed"),
                    "final_ap7_supported": top(perturbation, "final_ap7_supported"),
                },
                "i3_active_null_summary": {
                    "acceptance_state": top(one_way, "acceptance_state"),
                    "final_ap7_supported": top(one_way, "final_ap7_supported"),
                },
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_02_n17_loop_replay_order_control_telemetry_nat4",
            source_iteration_or_closeout="N17 I5-I6 replay/order/control matrix and claim boundary",
            artifacts=[closeout_path, replay_path, claim_path, requirements_path],
            reports=[
                f"{N17}/reports/n17_closeout_and_handoff.md",
                f"{N17}/reports/n17_loop_replay_and_control_matrix.md",
                f"{N17}/reports/n17_claim_boundary_record.md",
                f"{N17}/reports/n17_closed_loop_requirements_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP7 replay, order, hidden-state, and loop-overclaim controls"
            ),
            native_question=(
                "Can AP7 replay and controls become native admissibility telemetry for "
                "future loop rows?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_closed_loop_replay_order_control_telemetry",
            runtime_visible_inputs=[
                "artifact_only_replay_status",
                "snapshot_load_replay_status",
                "duplicate_replay_status",
                "order_inversion_control_status",
                "post_hoc_stitching_control_status",
                "hidden_external_state_memory_control_status",
                "hidden_internal_state_carryover_control_status",
                "external_change_not_caused_by_response_control_status",
                "claim_boundary_flags",
            ],
            native_state_needed=[
                "stable replay matrix",
                "fail-closed loop-specific negative control matrix",
                "claim boundary record",
                "duplicate replay run-level note",
                "source digest set for loop artifacts",
            ],
            state_mutation_owner="future native loop replay/control validator",
            record_schema_sketch={
                "surface_id": "native_closed_loop_replay_order_control_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "replay_matrix_digest": "sha256",
                "control_matrix_digest": "sha256",
                "claim_boundary_digest": "sha256",
                "negative_controls_fail_closed": True,
            },
            default_off_flags={
                "native_loop_replay_control_telemetry_enabled": False,
                "native_loop_claim_admission_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "units": [
                    "replay_count",
                    "negative_control_count",
                    "claim_boundary_check_count",
                    "canonical_digest_count",
                    "validation_count",
                ],
                "duplicate_replay_is_run_level_control": True,
            },
            telemetry_requirements=[
                "record replay stability before loop claim admission",
                "record fail-closed negative controls with blocker ids",
                "record duplicate replay separately from schema-backed row controls",
                "record unsafe claim flags false beside every loop row",
            ],
            snapshot_replay_requirements=[
                "artifact-only replay stable",
                "snapshot/load replay stable",
                "duplicate replay stable",
                "order-inversion control fails closed as expected",
                "post-hoc stitching control fails closed as expected",
            ],
            negative_controls=common_loop_controls
            + [
                "outbound response relabel",
                "semantic action/perception loop relabel",
                "native closed-loop relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden runtime state",
                    "hidden external memory",
                    "hidden internal carryover",
                    "semantic agency",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off loop replay/control telemetry surface",
                "add canonical replay digest over trace legs, budget, row decision, and claim flags",
                "add negative-control blocker records for loop failure modes",
                "add run-level duplicate replay note distinct from schema-backed row controls",
            ],
            implementation_boundary=(
                "N19 classifies replay/control readiness only. It does not make AP7 native "
                "and does not admit semantic agency, action, or perception claims."
            ),
            blocked_claims=[
                "agency",
                "intention",
                "semantic action",
                "semantic perception",
                "semantic action-perception loop",
                "native closed loop",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N17 I5 records artifact-only, snapshot/load, duplicate, and order-inversion replay outcomes.",
                "N17 I6 preserves claim-clean loop interpretation before extension rows.",
                "N17 closeout confirms unsafe claim flags and native supported flags remain false.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "Native replay/control admission requires future Phase 8 implementation.",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_03_n17_perturbation_response_recovery_loop_telemetry_nat4",
            source_iteration_or_closeout="N17 I4, I6-A, and I6-B perturbation-response-recovery loop probes",
            artifacts=[
                closeout_path,
                perturbation_path,
                replay_path,
                claim_path,
                mvp_g5_path,
                alt_mvp_g5_path,
                requirements_path,
            ],
            reports=[
                f"{N17}/reports/n17_perturbation_response_recovery_loop.md",
                f"{N17}/reports/n17_mvp_challenge_stability_probe.md",
                f"{N17}/reports/n17_alternative_g5_challenge_probe.md",
                f"{N17}/reports/n17_closeout_and_handoff.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="artifact-level perturbation-response-recovery G3/G5 loop family evidence",
            native_question=(
                "Can perturbation-response-recovery loop telemetry become a Phase-8-ready "
                "native policy surface without becoming semantic action/perception?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_perturbation_response_recovery_loop_telemetry",
            runtime_visible_inputs=[
                "external_perturbation_crossing",
                "internal_support_shift",
                "bounded_response_or_reclosure",
                "response_caused_external_perturbation_field_change",
                "later_internal_support_conditioned_by_changed_external_state",
                "challenge_stability_envelope",
                "target_band_gated_alternative_envelope",
                "support_floor",
                "budget_surface",
            ],
            native_state_needed=[
                "perturbation field trace",
                "internal support before/after response",
                "bounded reclosure response edge",
                "challenge-stability envelope rows",
                "alternative target-band gated challenge rows",
            ],
            state_mutation_owner="future native perturbation-response loop telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_perturbation_response_recovery_loop_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "perturbation_trace_digest": "sha256",
                "response_trace_digest": "sha256",
                "feedback_dependency_digest": "sha256",
                "challenge_envelope_digest": "sha256",
                "semantic_action_claim_allowed": False,
            },
            default_off_flags={
                "native_perturbation_loop_telemetry_enabled": False,
                "native_semantic_action_enabled": False,
                "native_semantic_perception_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "g3_source": source_artifact_summary(closeout, "i4_g3_candidate")[
                    "source_acceptance_state"
                ],
                "g5_source": source_artifact_summary(closeout, "i6a_mvp_g5")[
                    "source_acceptance_state"
                ],
                "alternative_g5_source": source_artifact_summary(closeout, "i6b_alternative_mvp_g5")[
                    "source_acceptance_state"
                ],
            },
            telemetry_requirements=[
                "record perturbation field before crossing",
                "record support shift after crossing",
                "record bounded response/reclosure and its budget cost",
                "record response-caused perturbation-field change",
                "record later internal support dependence on the changed field",
                "record G5 challenge-stability envelope and failed controls",
            ],
            snapshot_replay_requirements=[
                "replay the G3 candidate through I5 controls",
                "replay I6-A fixed challenge-stability envelope",
                "replay I6-B alternative target-band-gated envelope",
                "reject feedback-removed and external-change-not-caused-by-response controls",
            ],
            negative_controls=common_loop_controls
            + [
                "one-step recovery as closed loop",
                "response label as semantic action",
                "later stability without changed-field dependence",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic action",
                    "semantic perception",
                    "agency intention",
                    "native repair",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off perturbation-response loop telemetry surface",
                "add response-causation attribution record",
                "add later-internal dependency-on-changed-external-state record",
                "add challenge-stability envelope digest and fail-closed controls",
            ],
            implementation_boundary=(
                "The row is Phase 8-ready as telemetry only. It does not implement "
                "native closed-loop control, semantic action, perception, or autonomous repair."
            ),
            blocked_claims=[
                "semantic action",
                "semantic perception",
                "agency",
                "intention",
                "autonomous repair",
                "native support",
                "native closed loop",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "I4 supplies the first G3 closure candidate.",
                f"I6-A current evidence rung is {top(mvp_g5, 'current_evidence_rung')}.",
                f"I6-B current evidence rung is {top(alt_mvp_g5, 'current_evidence_rung')}.",
                "The loop family remains perturbation-response-recovery, not semantic agency.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "Native loop execution would require a Phase 8 producer implementation and source-current validation.",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_04_n17_resource_support_loop_telemetry_nat4",
            source_iteration_or_closeout="N17 I7, I7-A, and I7-B resource/support loop probes",
            artifacts=[
                closeout_path,
                resource_path,
                resource_g5_path,
                alt_resource_g5_path,
                requirements_path,
            ],
            reports=[
                f"{N17}/reports/n17_resource_support_modulation_loop.md",
                f"{N17}/reports/n17_resource_support_challenge_stability_probe.md",
                f"{N17}/reports/n17_alternative_resource_support_g5_probe.md",
                f"{N17}/reports/n17_closeout_and_handoff.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="artifact-level local resource/support modulation loop evidence",
            native_question=(
                "Can resource/support modulation loop telemetry become Phase-8-ready "
                "without becoming resource seeking, goal pursuit, or native support?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_resource_support_modulation_loop_telemetry",
            runtime_visible_inputs=[
                "route_b_resource_support_access_modulation",
                "support_floor",
                "support_margin_above_floor",
                "target_band",
                "resource_support_attenuation",
                "access_delay_window",
                "route_b_support_reduction",
                "compound_support_cost",
                "resource_goal_pursuit_relabel_control",
            ],
            native_state_needed=[
                "fixed route_b resource/support loop row",
                "I7-A fixed-row local G5 envelope",
                "I7-B alternative low-margin local G5 envelope",
                "support floor and target-band gate records",
                "goal-pursuit and native-support relabel controls",
            ],
            state_mutation_owner="future native resource/support loop telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_resource_support_modulation_loop_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "route_id": "string",
                "resource_support_access_digest": "sha256",
                "support_floor_digest": "sha256",
                "target_band_digest": "sha256",
                "challenge_envelope_digest": "sha256",
                "semantic_goal_pursuit_claim_allowed": False,
            },
            default_off_flags={
                "native_resource_support_loop_telemetry_enabled": False,
                "native_resource_seeking_enabled": False,
                "native_support_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "i7a_fixed_route_b_support_margin_above_floor": 0.074495897432,
                "i7b_low_margin_support_margin_above_floor": 0.02583821862,
                "i7b_low_margin_min_supported": 0.00583821862,
                "i7b_does_not_expand_i7a_envelope": True,
            },
            telemetry_requirements=[
                "record selected route identity and resource/support access trace",
                "record support floor and target-band membership before row decision",
                "record fixed-row I7-A envelope separately from I7-B alternative setup",
                "record floor crossing, target-band crossing, missing feedback, and goal-pursuit relabel controls",
            ],
            snapshot_replay_requirements=[
                "replay fixed route_b row without retuning",
                "replay I7-A fixed-row G5 envelope",
                "replay I7-B alternative low-margin envelope as separate evidence",
                "reject support-floor crossing, target-band crossing, and missing-feedback controls",
            ],
            negative_controls=common_loop_controls
            + [
                "resource label-only relabel",
                "resource depletion as goal pursuit",
                "route_a burden switching as route_b stability",
                "native support relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic goal",
                    "resource seeking intention",
                    "native support",
                    "hidden route switch",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off resource/support loop telemetry surface",
                "add route-fixed resource access digest",
                "add support-floor and target-band gate records",
                "add local challenge-envelope records for fixed and alternative setups",
                "add resource/goal/native-support relabel rejection hooks",
            ],
            implementation_boundary=(
                "The row is a local resource/support telemetry readiness candidate. "
                "It does not implement native support, resource seeking, or semantic goal pursuit."
            ),
            blocked_claims=[
                "semantic goal ownership",
                "resource seeking",
                "intention",
                "semantic action",
                "semantic perception",
                "native support",
                "agency",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                f"I7-A current evidence rung is {top(resource_g5, 'current_evidence_rung')}.",
                f"I7-B current evidence rung is {top(alt_resource_g5, 'current_evidence_rung')}.",
                "I7-B strengthens setup variation but does not widen the I7-A fixed route_b envelope.",
                "Resource/support modulation remains artifact-level loop telemetry, not goal pursuit or native support.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "Native support/resource-seeking remains blocked without a separate Phase 8 implementation.",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_05_n17_scoped_shared_medium_loop_telemetry_nat4",
            source_iteration_or_closeout="N17 I8 through I8-D scoped shared-medium loop probes",
            artifacts=[
                closeout_path,
                shared_path,
                shared_alt_path,
                paired_path,
                derived_path,
                b4c5_reverse_path,
                requirements_path,
            ],
            reports=[
                f"{N17}/reports/n17_shared_medium_reciprocal_loop.md",
                f"{N17}/reports/n17_shared_medium_reverse_perspective_probe.md",
                f"{N17}/reports/n17_paired_perspective_shared_medium_probe.md",
                f"{N17}/reports/n17_b4c5_derived_paired_perspective_probe.md",
                f"{N17}/reports/n17_b4c5_reverse_perspective_replay_probe.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level scoped shared-medium loop telemetry: local one-sided, "
                "alternate-source, local paired, and B4_C5-derived two-cycle candidates"
            ),
            native_question=(
                "Can scoped shared-medium loop telemetry become Phase-8-ready while preserving "
                "the original B4_C5 reverse replay blocker and rejecting general symmetric/native claims?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_scoped_shared_medium_loop_telemetry",
            runtime_visible_inputs=[
                "shared_medium_boundary_exchange",
                "coupling_channel_attribution",
                "shared_medium_leakage",
                "neighbor_leakage",
                "merge_confusion_pressure",
                "local_paired_perspective_trace",
                "b4c5_derived_two_cycle_reverse_side_state",
                "original_b4c5_reverse_replay_blocker",
            ],
            native_state_needed=[
                "local one-sided shared-medium G6 row",
                "alternate-source shared-medium G6 row",
                "local paired-perspective shared-medium G6 row",
                "B4_C5-derived two-cycle paired-perspective G6 row",
                "original B4_C5 reverse-perspective blocker",
                "merge/leakage attribution controls",
            ],
            state_mutation_owner="future native scoped shared-medium loop telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_scoped_shared_medium_loop_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "shared_medium_exchange_digest": "sha256",
                "paired_perspective_digest": "sha256",
                "derived_two_cycle_digest": "sha256",
                "original_b4c5_reverse_replay_allowed": False,
                "general_shared_medium_g6_allowed": False,
            },
            default_off_flags={
                "native_shared_medium_loop_telemetry_enabled": False,
                "native_general_shared_medium_g6_enabled": False,
                "native_multi_basin_selfhood_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "local_one_sided_candidate_supported": top(
                    shared, "shared_medium_g6_candidate_supported"
                ),
                "local_paired_candidate_supported": top(
                    paired, "paired_perspective_shared_medium_g6_candidate_supported"
                ),
                "b4c5_derived_two_cycle_candidate_supported": top(
                    derived, "b4c5_derived_paired_perspective_g6_candidate_supported"
                ),
                "original_b4c5_reverse_replay_supported": top(
                    b4c5_reverse, "b4c5_reverse_perspective_replay_supported"
                ),
            },
            telemetry_requirements=[
                "record shared-medium exchange and coupling-channel attribution",
                "record leakage, neighbor leakage, and merge pressure separately",
                "record local paired perspective rows separately from original B4_C5 replay",
                "record B4_C5-derived two-cycle protocol as derived evidence only",
                "record general/symmetric/native shared-medium relabel blockers",
            ],
            snapshot_replay_requirements=[
                "replay local one-sided shared-medium row with one-sided scope",
                "replay local paired-perspective row without importing it into original B4_C5",
                "replay B4_C5-derived two-cycle row as derived protocol only",
                "reject original B4_C5 reverse replay and label-swap controls",
                "reject merge/leakage as reciprocity",
            ],
            negative_controls=common_loop_controls
            + [
                "neighbor leakage as retention",
                "merge/leakage as reciprocity",
                "label swap as reverse perspective",
                "8-C evidence imported as original B4_C5 reverse replay",
                "general shared-medium G6 relabel",
                "symmetric native multi-basin replay relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden reverse perspective",
                    "hidden shared-medium routing",
                    "native multi-basin selfhood",
                    "general symmetric shared-medium loop",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off scoped shared-medium loop telemetry surface",
                "add paired-perspective and derived two-cycle provenance digests",
                "add original-B4_C5 reverse replay blocker field",
                "add merge/leakage attribution controls",
                "add general/symmetric/native shared-medium relabel rejection hooks",
            ],
            implementation_boundary=(
                "The row is scoped shared-medium telemetry readiness only. It does not "
                "support general shared-medium G6, symmetric native replay, or native multi-basin selfhood."
            ),
            blocked_claims=[
                "general shared-medium G6",
                "B4_C5 original reverse-perspective replay",
                "symmetric native multi-basin replay",
                "native multi-basin selfhood",
                "semantic action",
                "semantic perception",
                "agency",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "I8 source supports a local one-sided shared-medium G6 candidate.",
                f"I8-C local paired-perspective evidence rung is {top(paired, 'current_evidence_rung')}.",
                f"I8-D derived two-cycle evidence rung is {top(derived, 'current_evidence_rung')}.",
                "I8-B keeps original B4_C5 reverse replay blocked, so the NAT4 surface is scoped and provenance-sensitive.",
            ],
            blockers_to_next_level=[
                "general shared-medium G6 remains blocked",
                "original B4_C5 reverse replay remains blocked",
                "native symmetric multi-basin replay remains blocked",
                "NAT5/NAT6 are out of scope for N19",
            ],
            extra={
                "shared_medium_scope": {
                    "local_one_sided_supported": top(
                        shared, "shared_medium_g6_candidate_supported"
                    ),
                    "b4c5_reverse_replay_supported": top(
                        b4c5_reverse, "b4c5_reverse_perspective_replay_supported"
                    ),
                    "general_shared_medium_g6_supported": top(
                        b4c5_reverse, "general_shared_medium_g6_supported"
                    ),
                    "b4c5_reverse_replay_blocker": top(
                        b4c5_reverse, "b4c5_reverse_replay_blocker"
                    ),
                }
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_06_n17_original_b4c5_general_shared_medium_blocker",
            source_iteration_or_closeout="N17 I8-B blocker and I8/I8-D provenance distinction",
            artifacts=[closeout_path, shared_path, b4c5_reverse_path, derived_path, requirements_path],
            reports=[
                f"{N17}/reports/n17_b4c5_reverse_perspective_replay_probe.md",
                f"{N17}/reports/n17_shared_medium_reciprocal_loop.md",
                f"{N17}/reports/n17_b4c5_derived_paired_perspective_probe.md",
                f"{N17}/reports/n17_closeout_and_handoff.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope=(
                "blocked upgrade of original B4_C5 into reverse-perspective, general "
                "shared-medium G6, or symmetric native multi-basin replay evidence"
            ),
            native_question=(
                "Can original B4_C5 or later derived shared-medium evidence be relabeled as "
                "general/native symmetric shared-medium loop evidence?"
            ),
            primary_disposition="implementation_gap_blocker",
            nat_level="NAT2",
            phase8_ready=False,
            native_surface="native_general_shared_medium_reverse_perspective_evidence_required",
            runtime_visible_inputs=[
                "original_b4c5_forward_perspective",
                "missing_reverse_internal_side_state",
                "missing_reverse_support_metric",
                "missing_reverse_coherence_metric",
                "missing_reverse_boundary_edge",
                "missing_reverse_feedback_trace",
                "derived_two_cycle_protocol_distinct_from_original_source",
            ],
            native_state_needed=[
                "source-backed reverse internal nodes for original source",
                "reverse support/coherence metrics for original source",
                "reverse boundary edge for original source",
                "reverse changed-medium feedback trace for original source",
                "control preventing derived-pair evidence from backfilling original B4_C5",
            ],
            state_mutation_owner="future general shared-medium reverse-perspective producer",
            record_schema_sketch={
                "blocked_upgrade_id": "original_b4c5_general_shared_medium_blocker",
                "original_forward_digest": "sha256",
                "reverse_perspective_digest": "required_missing",
                "derived_evidence_backfill_allowed": False,
                "general_shared_medium_g6_allowed": False,
            },
            default_off_flags={
                "native_general_shared_medium_g6_enabled": False,
                "native_symmetric_multi_basin_replay_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "status": "blocked_until_original_reverse_source_rows_exist",
                "derived_two_cycle_rows_do_not_rewrite_original_source": True,
            },
            telemetry_requirements=[
                "record original B4_C5 as one-sided in provenance",
                "record reverse support/coherence/boundary/feedback evidence as missing",
                "record derived two-cycle evidence as separate protocol",
                "record general and symmetric relabel attempts as blocked",
            ],
            snapshot_replay_requirements=[
                "replay original B4_C5 without perspective swap",
                "reject reverse replay when reverse source rows are missing",
                "reject 8-C or 8-D evidence imported into original B4_C5 provenance",
            ],
            negative_controls=[
                "label swap as reverse perspective",
                "derived paired evidence as original B4_C5 reverse replay",
                "merge/leakage as reciprocity",
                "general shared-medium G6 relabel",
                "symmetric native multi-basin replay relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden reverse-side state",
                    "hidden reverse support/coherence",
                    "hidden reverse boundary edge",
                    "native multi-basin selfhood",
                ],
            },
            minimal_producer_code_needed=[
                "generate original-source reverse-side rows rather than relabeling",
                "record reverse support/coherence/boundary/feedback traces",
                "preserve derived two-cycle provenance as separate evidence",
            ],
            implementation_boundary=(
                "This blocker preserves source provenance. It prevents scoped shared-medium "
                "telemetry from becoming general/native symmetric shared-medium evidence."
            ),
            blocked_claims=[
                "general shared-medium G6",
                "B4_C5 original reverse-perspective replay",
                "symmetric native multi-basin replay",
                "native multi-basin selfhood",
                "agency",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="blocked",
            nat4_gate_results=gate_results(
                {
                    "native_policy_or_telemetry_surface_name_present": True,
                    "record_schema_sketch_present": True,
                    "default_off_flags_present": True,
                    "enabled_validated_supported_separation_present": True,
                    "state_mutation_owner_specified": True,
                    "budget_surface_specified": True,
                    "telemetry_requirements_specified": True,
                    "snapshot_replay_requirements_specified": True,
                    "negative_controls_specified": True,
                    "non_rc_quantity_audit_passes": True,
                    "claim_flags_forced_false": True,
                    "phase8_opened_false": True,
                    "native_support_opened_false": True,
                    "src_diff_empty_true": True,
                }
            ),
            evidence_notes=[
                "NAT2 describes replayable blocker evidence only; row_decision remains blocked and phase8_ready remains false.",
                "I8-B confirms original B4_C5 is multi-basin but not reverse-perspective paired.",
                "I8-D can generate a B4_C5-derived two-cycle protocol, but it does not rewrite original B4_C5.",
                f"Original reverse blocker: {top(b4c5_reverse, 'b4c5_reverse_replay_blocker')}.",
            ],
            blockers_to_next_level=[
                "reverse internal side not source-backed in original B4_C5",
                "reverse support/coherence metrics missing",
                "reverse boundary edge missing",
                "reverse feedback trace missing",
                "derived evidence cannot backfill original source provenance",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i5_row_07_n17_loop_agency_action_perception_relabels_rejected",
            source_iteration_or_closeout="N17 closeout, claim boundary, and replay/control records",
            artifacts=[closeout_path, claim_path, replay_path, requirements_path],
            reports=[
                f"{N17}/reports/n17_closeout_and_handoff.md",
                f"{N17}/reports/n17_claim_boundary_record.md",
                f"{N17}/reports/n17_loop_replay_and_control_matrix.md",
                f"{N17}/reports/n17_closed_loop_requirements_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="unsafe relabel controls over AP7 loop evidence",
            native_question=(
                "Can AP7 loop evidence be relabeled as agency, intention, semantic action, "
                "semantic perception, native support, or fully native integration?"
            ),
            primary_disposition="unsafe_relabel_rejected",
            nat_level="NAT0",
            phase8_ready=False,
            native_surface="not_applicable_relabel_rejected",
            runtime_visible_inputs=[],
            native_state_needed=[],
            state_mutation_owner="not_applicable",
            record_schema_sketch={"relabel_claim": "string", "claim_allowed": False},
            default_off_flags={"unsafe_loop_relabel_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={"required": False, "reason": "claim-control row"},
            telemetry_requirements=["record rejected relabel and source claim boundary"],
            snapshot_replay_requirements=["replay unsafe claim flags as false"],
            negative_controls=[
                "loop as agency",
                "response as semantic action",
                "feedback as semantic perception",
                "resource/support loop as semantic goal ownership",
                "shared-medium loop as native multi-basin selfhood",
                "AP7 as native support",
                "AP7 as Phase 8 implementation",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "agency",
                    "intention",
                    "semantic action",
                    "semantic perception",
                    "native support",
                ],
            },
            minimal_producer_code_needed=[
                "none for this rejected relabel; preserve controls in any future loop surface"
            ],
            implementation_boundary="Rejected relabel row; no implementation path.",
            blocked_claims=[
                "agency",
                "intention",
                "choice",
                "semantic action",
                "semantic perception",
                "semantic goal ownership",
                "selfhood",
                "identity acceptance",
                "native support",
                "organism/life behavior",
                "fully native agentic-like integration",
                "unrestricted agency",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="rejected",
            nat4_gate_results=gate_results({}),
            evidence_notes=[
                "N17 closeout supports artifact-level AP7 only.",
                "The final claim boundary blocks agency, intention, semantic action, semantic perception, native support, and fully native integration.",
                "One-way crossing relabel remains rejected; G0-G2 fragments cannot become closed-loop evidence.",
                "one_way_crossing_trace != closed_boundary_engagement_loop",
            ],
            blockers_to_next_level=["unsafe relabel has no native-readiness promotion path"],
        )
    )
    return rows


def validate_rows(rows: list[dict[str, Any]], schema: dict[str, Any]) -> list[dict[str, Any]]:
    required_fields = set(schema["candidate_row_schema"]["required_fields"])
    primary_dispositions = set(schema["enums"]["primary_disposition"])
    nat_levels = set(schema["enums"]["nat_level"])
    row_decisions = set(schema["enums"]["row_decision"])
    claim_flags = set(schema["candidate_row_schema"]["claim_flags_forced_false"])
    row_ids = {row["row_id"] for row in rows}
    expected_ids = {
        "n19_i5_row_01_n17_ordered_trace_leg_telemetry_nat4",
        "n19_i5_row_02_n17_loop_replay_order_control_telemetry_nat4",
        "n19_i5_row_03_n17_perturbation_response_recovery_loop_telemetry_nat4",
        "n19_i5_row_04_n17_resource_support_loop_telemetry_nat4",
        "n19_i5_row_05_n17_scoped_shared_medium_loop_telemetry_nat4",
        "n19_i5_row_06_n17_original_b4c5_general_shared_medium_blocker",
        "n19_i5_row_07_n17_loop_agency_action_perception_relabels_rejected",
    }
    checks = [
        {
            "check_id": "required_ap7_rows_present",
            "passed": row_ids == expected_ids,
            "detail": sorted(row_ids),
        },
        {
            "check_id": "all_required_schema_fields_present",
            "passed": all(required_fields.issubset(row) for row in rows),
            "detail": {
                row["row_id"]: sorted(required_fields - set(row))
                for row in rows
                if not required_fields.issubset(row)
            },
        },
        {
            "check_id": "primary_dispositions_valid",
            "passed": all(row["primary_disposition"] in primary_dispositions for row in rows),
            "detail": {row["row_id"]: row["primary_disposition"] for row in rows},
        },
        {
            "check_id": "nat_levels_valid",
            "passed": all(row["nat_level"] in nat_levels for row in rows),
            "detail": {row["row_id"]: row["nat_level"] for row in rows},
        },
        {
            "check_id": "row_decisions_valid",
            "passed": all(row["row_decision"] in row_decisions for row in rows),
            "detail": {row["row_id"]: row["row_decision"] for row in rows},
        },
        {
            "check_id": "phase8_ready_derivation_enforced",
            "passed": all(
                row["phase8_ready"] == (row["nat_level"] == "NAT4" and all_nat4_gates_pass(row))
                for row in rows
            ),
            "detail": {
                row["row_id"]: {
                    "nat_level": row["nat_level"],
                    "phase8_ready": row["phase8_ready"],
                    "all_nat4_gates_pass": all_nat4_gates_pass(row),
                }
                for row in rows
            },
        },
        {
            "check_id": "nat4_rows_have_all_gates_passed",
            "passed": all(all_nat4_gates_pass(row) for row in rows if row["nat_level"] == "NAT4"),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
        },
        {
            "check_id": "nat2_blocker_has_nat4_gap",
            "passed": any(
                row["row_id"] == "n19_i5_row_06_n17_original_b4c5_general_shared_medium_blocker"
                and row["nat_level"] == "NAT2"
                and not all_nat4_gates_pass(row)
                for row in rows
            ),
            "detail": "original B4_C5/general shared-medium blocker remains below NAT4",
        },
        {
            "check_id": "claim_flags_forced_false_all_rows",
            "passed": all(
                set(row["claim_flags"]) == claim_flags
                and all(value is False for value in row["claim_flags"].values())
                for row in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "phase8_and_native_support_not_opened",
            "passed": all(not row["phase8_opened"] and not row["native_support_opened"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "source_digests_present",
            "passed": all(row["source_sha256"] and row["source_output_digest"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "ordered_trace_leg_candidates_classified",
            "passed": "n19_i5_row_01_n17_ordered_trace_leg_telemetry_nat4" in row_ids,
            "detail": "external -> internal -> external -> later internal telemetry row present",
        },
        {
            "check_id": "loop_replay_control_telemetry_classified",
            "passed": "n19_i5_row_02_n17_loop_replay_order_control_telemetry_nat4" in row_ids,
            "detail": "replay/order/control telemetry row present",
        },
        {
            "check_id": "perturbation_response_recovery_classified",
            "passed": "n19_i5_row_03_n17_perturbation_response_recovery_loop_telemetry_nat4" in row_ids,
            "detail": "G3/G5 perturbation-response-recovery row present",
        },
        {
            "check_id": "resource_support_loop_classified",
            "passed": "n19_i5_row_04_n17_resource_support_loop_telemetry_nat4" in row_ids,
            "detail": "I7/I7-A/I7-B resource/support row present",
        },
        {
            "check_id": "shared_medium_loop_classified_with_scope",
            "passed": any(
                row["row_id"] == "n19_i5_row_05_n17_scoped_shared_medium_loop_telemetry_nat4"
                and "general shared-medium G6" in row["blocked_claims"]
                and "B4_C5 original reverse-perspective replay" in row["blocked_claims"]
                for row in rows
            ),
            "detail": "shared-medium NAT4 row is scoped and keeps original B4_C5 blocker",
        },
        {
            "check_id": "one_way_crossing_relabel_remains_rejected",
            "passed": any(
                row["row_id"] == "n19_i5_row_07_n17_loop_agency_action_perception_relabels_rejected"
                and any("One-way crossing relabel remains rejected" in note for note in row["evidence_notes"])
                for row in rows
            ),
            "detail": "G0-G2 fragments cannot become AP7",
        },
        {
            "check_id": "agency_action_perception_relabels_rejected",
            "passed": any(
                row["row_id"] == "n19_i5_row_07_n17_loop_agency_action_perception_relabels_rejected"
                and row["row_decision"] == "rejected"
                and {"agency", "semantic action", "semantic perception", "native support"}.issubset(
                    set(row["blocked_claims"])
                )
                for row in rows
            ),
            "detail": "unsafe AP7 relabel row rejected",
        },
        {
            "check_id": "native_loop_telemetry_requirements_recorded",
            "passed": all(
                row["telemetry_requirements"]
                and row["minimal_producer_code_needed"]
                for row in rows
                if row["nat_level"] == "NAT4"
            ),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(rows),
            "detail": "all row paths are relative",
        },
        {
            "check_id": "src_diff_empty_recorded_true",
            "passed": all(row["src_diff_empty"] is True for row in rows),
            "detail": len(rows),
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 5 - AP7 Loop Native-Readiness Classification",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"row_count = {artifact['row_count']}",
        f"phase8_ready_row_count = {artifact['classification_summary']['phase8_ready_row_count']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Classification rows:",
        "",
        "| Row | Disposition | NAT | Decision | Phase 8 Ready | Surface |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["candidate_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["primary_disposition"],
                    row["nat_level"],
                    row["row_decision"],
                    str(row["phase8_ready"]).lower(),
                    row["native_policy_or_telemetry_surface_name"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Main interpretation:",
            "",
            "```text",
            artifact["interpretation"]["main_read"],
            "```",
            "",
            "Scope boundary:",
            "",
            "```text",
            artifact["interpretation"]["scope_boundary"],
            "```",
            "",
            "Classification summary:",
            "",
            "```json",
            json.dumps(artifact["classification_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = load_json(INVENTORY)
    schema = load_json(SCHEMA)
    rows = build_rows(inventory, schema)
    checks = [
        {
            "check_id": "source_inventory_passed",
            "passed": inventory.get("status") == "passed",
            "detail": rel(INVENTORY),
        },
        {
            "check_id": "schema_freeze_passed",
            "passed": schema.get("status") == "passed"
            and schema.get("candidate_rows_classified") is False,
            "detail": rel(SCHEMA),
        },
    ] + validate_rows(rows, schema)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_ap7_loop_native_readiness_classification",
        "schema_version": "n19_ap7_loop_native_readiness_classification_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 5,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Classify N17 AP7 ordered loop, replay/control, perturbation-response, "
            "resource/support, and scoped shared-medium loop evidence as native-readiness "
            "surfaces without opening Phase 8, native support, agency, action, or perception."
        ),
        "source_inventory": {
            "path": rel(INVENTORY),
            "sha256": sha256_file(INVENTORY),
            "output_digest": inventory["output_digest"],
        },
        "schema_source": {
            "path": rel(SCHEMA),
            "sha256": sha256_file(SCHEMA),
            "output_digest": schema["output_digest"],
        },
        "candidate_rows": rows,
        "row_count": len(rows),
        "classification_summary": {
            "classified_sources": ["N17"],
            "nat4_rows": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
            "nat2_rows": [row["row_id"] for row in rows if row["nat_level"] == "NAT2"],
            "rejected_rows": [row["row_id"] for row in rows if row["row_decision"] == "rejected"],
            "blocked_rows": [row["row_id"] for row in rows if row["row_decision"] == "blocked"],
            "phase8_ready_row_count": sum(1 for row in rows if row["phase8_ready"]),
            "ap7_phase8_ready_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["phase8_ready"]
            ],
            "ordered_trace_legs_classification": "NAT4 phase8-ready telemetry candidate",
            "replay_control_classification": "NAT4 phase8-ready telemetry candidate",
            "perturbation_response_recovery_classification": "NAT4 phase8-ready telemetry candidate",
            "resource_support_classification": "NAT4 scoped local telemetry candidate",
            "shared_medium_classification": (
                "NAT4 scoped local/derived telemetry candidate with original B4_C5 "
                "and general symmetric shared-medium blockers preserved"
            ),
            "one_way_crossing_relabel_status": "rejected",
            "semantic_agency_action_perception_relabel_status": "rejected",
            "native_support_relabel_status": "rejected",
        },
        "interpretation": {
            "main_read": (
                "Iteration 5 classifies N17 AP7 evidence as a set of Phase-8-ready "
                "native telemetry candidates: ordered trace legs, replay/order controls, "
                "perturbation-response-recovery, local resource/support modulation, and "
                "scoped shared-medium loop telemetry. The classification is not a native "
                "loop implementation and does not promote response into semantic action, "
                "feedback into semantic perception, or loop closure into agency."
            ),
            "scope_boundary": (
                "The original B4_C5 reverse-perspective replay and general symmetric "
                "shared-medium G6 remain blocked. Local paired and B4_C5-derived two-cycle "
                "evidence can support scoped shared-medium telemetry readiness, but cannot "
                "rewrite the original B4_C5 source or open native multi-basin selfhood."
            ),
            "not_supported": [
                "agency",
                "intention",
                "semantic action",
                "semantic perception",
                "semantic goal ownership",
                "selfhood",
                "identity acceptance",
                "native support",
                "native closed loop",
                "general shared-medium G6",
                "symmetric native multi-basin replay",
                "organism/life behavior",
                "fully native agentic-like integration",
                "Phase 8 implementation",
                "AP9",
            ],
        },
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
        "src_diff_empty": True,
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

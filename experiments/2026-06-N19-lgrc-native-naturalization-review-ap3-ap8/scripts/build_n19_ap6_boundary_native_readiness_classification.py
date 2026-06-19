#!/usr/bin/env python3
"""Build N19 Iteration 4 AP6 boundary native-readiness classification."""

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
OUTPUT = EXPERIMENT / "outputs" / "n19_ap6_boundary_native_readiness_classification.json"
REPORT = EXPERIMENT / "reports" / "n19_ap6_boundary_native_readiness_classification.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_ap6_boundary_native_readiness_classification.py"
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

N16 = "experiments/2026-06-N16-lgrc-self-environment-boundary"


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
    return {
        flag: False
        for flag in schema["candidate_row_schema"]["claim_flags_forced_false"]
    }


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
        if row["source_experiment"] == "N16":
            return {
                "source_final_supported_ap_level": row["source_final_supported_ap_level"],
                "source_final_claim_ceiling": row["source_final_claim_ceiling"],
            }
    raise KeyError("N16")


def selected_row(selected: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for row in selected["rows"]:
        if row["cell_id"] == cell_id:
            return row
    raise KeyError(cell_id)


def metric(row: dict[str, Any], key: str) -> Any:
    if key in row:
        return row[key]
    replay = row.get("replay_digest_inputs", {})
    metrics = replay.get("metrics", {}) if isinstance(replay, dict) else {}
    return metrics.get(key, "not_recorded")


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
        "source_experiment": "N16",
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
    closeout_path = f"{N16}/outputs/n16_closeout_and_handoff.json"
    schema_path = f"{N16}/outputs/n16_boundary_schema_v1.json"
    requirements_path = f"{N16}/outputs/n16_basin_boundary_requirements_matrix.json"
    selected_path = f"{N16}/outputs/n16_selected_interaction_probe_matrix.json"
    sweep_path = f"{N16}/outputs/n16_boundary_state_sweep_matrix.json"
    challenge_path = f"{N16}/outputs/n16_challenge_sweep_matrix.json"
    claim_path = f"{N16}/outputs/n16_claim_boundary_record.json"
    quiet_path = f"{N16}/outputs/n16_quiet_boundary_calibration.json"

    requirements = load_json(ROOT / requirements_path)
    selected = load_json(ROOT / selected_path)
    claim = load_json(ROOT / claim_path)
    b0_c3 = selected_row(selected, "B0_C3")
    b2_c1 = selected_row(selected, "B2_C1")
    b3_c4 = selected_row(selected, "B3_C4")
    b4_c5 = selected_row(selected, "B4_C5")
    supported_envelope = requirements["aggregate_metric_summary"]["supported_boundary_candidate_rows"]
    ap6_gates = claim["ap6_gate_summary"]

    common_negative_controls = [
        "externally supplied boundary labels",
        "post-hoc boundary labels",
        "hidden external-state injection",
        "missing boundary side state",
        "stale internal state",
        "stale external state",
        "boundary drift outside frozen policy",
        "untracked boundary crossing",
        "native support relabel",
        "selfhood/personhood relabel",
        "identity acceptance relabel",
    ]

    rows: list[dict[str, Any]] = []
    rows.append(
        row_base(
            row_id="n19_i4_row_01_n16_boundary_side_state_edge_telemetry_nat4",
            source_iteration_or_closeout="N16 AP6 closeout, schema, selected probes, and requirements matrix",
            artifacts=[closeout_path, schema_path, requirements_path, selected_path, claim_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_boundary_schema_v1.md",
                f"{N16}/reports/n16_basin_boundary_requirements_matrix.md",
                f"{N16}/reports/n16_selected_interaction_probe_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP6 side-state, boundary-edge, challenge-role, and "
                "internal/external separability telemetry"
            ),
            native_question=(
                "Can N16 boundary side assignments, boundary edges, challenge roles, and "
                "internal/external state descriptors become a native boundary telemetry surface?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_boundary_side_state_and_edge_telemetry",
            runtime_visible_inputs=[
                "boundary_state",
                "challenge_class",
                "external_state_role",
                "boundary_side_assignments",
                "boundary_edges",
                "internal_state_descriptor",
                "external_region_nodes",
                "self_region_nodes",
                "challenge_profile",
                "dependency_trace",
                "replay_digest_inputs",
            ],
            native_state_needed=[
                "derived internal/external side assignment map",
                "boundary edge list with left/right side attribution",
                "internal support-relevant state descriptor",
                "external resource/perturbation/structured/shared-medium role descriptor",
                "source window and replay digest boundary",
            ],
            state_mutation_owner="future native boundary telemetry recorder at LGRC step snapshot boundary",
            record_schema_sketch={
                "surface_id": "native_boundary_side_state_and_edge_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "boundary_state": "B0_to_B4",
                "challenge_class": "C0_to_C5",
                "external_state_role": "enum",
                "side_assignment_digest": "sha256",
                "boundary_edge_digest": "sha256",
                "source_window_digest": "sha256",
                "claim_flags_digest": "sha256",
            },
            default_off_flags={
                "native_boundary_side_state_telemetry_enabled": False,
                "native_boundary_edge_telemetry_enabled": False,
                "native_selfhood_interpretation_enabled": False,
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
                    "source_row_count",
                    "matrix_cell_count",
                    "transform_count",
                    "canonical_json_input_bytes",
                    "canonical_json_output_bytes",
                    "replay_count",
                    "validation_count",
                    "wall_clock_seconds",
                ],
                "budget_validity_required": True,
            },
            telemetry_requirements=[
                "record boundary side assignments before row decision",
                "record boundary edges incident to derived sides",
                "record external_state_role from frozen enum",
                "record source-current challenge profile and window",
                "record claim flags false beside every side-state row",
            ],
            snapshot_replay_requirements=[
                "artifact-only replay over serialized side assignments and edge list",
                "snapshot/load replay of boundary side state",
                "order-inversion replay over canonical row order",
                "reject externally supplied labels and hidden external state",
            ],
            negative_controls=common_negative_controls,
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "selfhood",
                    "identity acceptance",
                    "native support",
                    "semantic goal ownership",
                    "agency environment model",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off boundary side-state telemetry record",
                "add boundary-edge attribution digest at LGRC step snapshot boundary",
                "add replay digest over side assignments, edge list, challenge role, and claim flags",
            ],
            implementation_boundary=(
                "N19 classifies telemetry readiness only. It does not implement native "
                "boundary state, selfhood, native support, or Phase 8."
            ),
            blocked_claims=[
                "selfhood",
                "identity acceptance",
                "semantic goal ownership",
                "agency",
                "agency environment model",
                "native support",
                "fully native agentic-like integration",
                "organism/life behavior",
                "closed action-perception loop",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                f"N16 validates {ap6_gates['validated_gate_count']} / {ap6_gates['gate_count']} AP6 gates.",
                "Selected-probe rows carry derived side assignments and edge lists without externally supplied boundary labels.",
                "B0_C3 demonstrates active-null rejection: structured external coherence remains external structured state.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "A later Phase 8 task must implement the default-off telemetry surface in src.",
            ],
            extra={
                "source_examples": {
                    "B0_C3": {
                        "external_state_role": b0_c3["external_state_role"],
                        "self_region_nodes": b0_c3["self_region_nodes"],
                        "external_region_nodes": b0_c3["external_region_nodes"],
                    },
                    "B2_C1": {
                        "boundary_edges": b2_c1["boundary_edges"],
                        "side_assignments": b2_c1["boundary_side_assignments"],
                    },
                }
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i4_row_02_n16_leakage_separability_requirement_telemetry_nat4",
            source_iteration_or_closeout="N16 controlled basin-boundary requirements matrix",
            artifacts=[closeout_path, requirements_path, selected_path, sweep_path, challenge_path, claim_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_basin_boundary_requirements_matrix.md",
                f"{N16}/reports/n16_boundary_state_sweep_matrix.md",
                f"{N16}/reports/n16_challenge_sweep_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP6 controlled boundary requirements: leakage, support, "
                "coherence margin, flux balance, repair/reclosure, structured external rejection, "
                "and inter-basin separation"
            ),
            native_question=(
                "Can leakage, support, coherence margin, flux balance, and separability "
                "requirements become native boundary validation telemetry?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_boundary_leakage_separability_requirements_telemetry",
            runtime_visible_inputs=[
                "minimum_internal_support",
                "minimum_coherence_margin",
                "maximum_leakage_ratio",
                "inbound_flux",
                "outbound_flux",
                "retained_flux",
                "repair_score",
                "reclosure_score",
                "basin_separation_score",
                "boundary_exclusivity_score",
                "merge_confusion_pressure",
                "row_decision",
                "negative_control_matrix",
                "replay_matrix",
            ],
            native_state_needed=[
                "supported-candidate operating envelope",
                "all-row stress envelope",
                "boundary requirement table",
                "fail-closed control outcomes",
                "stable replay digests",
            ],
            state_mutation_owner="future native boundary validation telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_boundary_leakage_separability_requirements_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "minimum_internal_support": "float",
                "minimum_coherence_margin": "float",
                "maximum_leakage_ratio": "float",
                "requirement_status_digest": "sha256",
                "control_matrix_digest": "sha256",
                "replay_matrix_digest": "sha256",
            },
            default_off_flags={
                "native_boundary_requirement_telemetry_enabled": False,
                "native_boundary_validation_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "budget_policy": "consume serialized I3-I7 source rows and controls only",
                "duplicate_replay_stable": True,
                "order_inversion_replay_stable": True,
                "snapshot_load_replay_stable": True,
            },
            telemetry_requirements=[
                "record supported-candidate operating envelope separately from all-row stress envelope",
                "record which rows support and limit each requirement",
                "record negative-control blocker for each dangerous relabel",
                "record stable replay digests",
            ],
            snapshot_replay_requirements=[
                "artifact-only replay stable",
                "duplicate replay stable",
                "order-inversion replay stable after canonical ordering",
                "snapshot/load replay stable",
                "reject stale internal/external state and boundary drift outside policy",
            ],
            negative_controls=common_negative_controls
            + [
                "multi-basin merge/leakage as retention",
                "structured external coherence as self region",
                "resource relabel as self",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden self boundary",
                    "hidden native support",
                    "unrecorded external state",
                    "unrecorded boundary side",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off boundary requirement telemetry surface",
                "add operating-envelope digest for supported boundary candidates",
                "add fail-closed negative-control replay hooks",
                "add stale-state and boundary-drift rejection records",
            ],
            implementation_boundary=(
                "N19 classifies a native validation telemetry candidate. It does not "
                "make AP6 native, general, or selfhood-supporting."
            ),
            blocked_claims=[
                "native support",
                "selfhood",
                "identity acceptance",
                "agency",
                "semantic goal ownership",
                "closed action-perception loop",
                "fully native agentic-like integration",
                "organism/life behavior",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "Supported boundary-candidate envelope preserves maximum leakage ratio 0.118.",
                "Supported boundary-candidate envelope preserves minimum coherence margin 0.524.",
                "Supported boundary-candidate envelope preserves minimum internal support 0.85.",
                "Global all-row metrics include null, partial, and rejected controls and are not the operating envelope.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "A later Phase 8 task must implement native recording and validation, not just consume artifacts.",
            ],
            extra={
                "supported_candidate_operating_envelope": {
                    "maximum_leakage_ratio": supported_envelope["maximum_leakage_ratio"],
                    "minimum_coherence_margin": supported_envelope["minimum_coherence_margin"],
                    "minimum_internal_support": supported_envelope["minimum_internal_support"],
                    "row_scope": supported_envelope["row_scope"],
                },
                "requirements_observed": sorted(requirements["native_boundary_requirements_observed"]),
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i4_row_03_n16_breach_reclosure_boundary_telemetry_nat4",
            source_iteration_or_closeout="N16 selected B3_C4 breach/reclosure probe and requirements matrix",
            artifacts=[closeout_path, requirements_path, selected_path, claim_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_basin_boundary_requirements_matrix.md",
                f"{N16}/reports/n16_selected_interaction_probe_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="artifact-level B3_C4 breach/reclosure boundary telemetry candidate",
            native_question=(
                "Can B3_C4 breach pressure, reclosure score, and boundary repair/reabsorption "
                "metrics become native telemetry without claiming autonomous repair?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_breach_reclosure_boundary_telemetry",
            runtime_visible_inputs=[
                "breach_pressure",
                "reclosure_score",
                "repair_score",
                "leakage_ratio",
                "minimum_internal_support",
                "coherence_margin",
                "boundary_edges",
                "boundary_side_assignments",
                "B2_C4 baseline comparison",
                "B3_C2 anchor comparison",
            ],
            native_state_needed=[
                "transient breach edge",
                "bounded reclosure response edge",
                "B2 baseline comparison row",
                "B3 flux repair anchor metrics",
                "claim ceiling that blocks autonomous repair",
            ],
            state_mutation_owner="future native breach/reclosure telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_breach_reclosure_boundary_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "breach_edge_digest": "sha256",
                "reclosure_edge_digest": "sha256",
                "repair_score": "float",
                "reclosure_score": "float",
                "baseline_comparison_digest": "sha256",
                "autonomous_repair_claim_allowed": False,
            },
            default_off_flags={
                "native_breach_reclosure_telemetry_enabled": False,
                "native_autonomous_repair_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "budget_validity_required": True,
                "reclosure_window": "selected_probe_window",
                "autonomous_repair_budget_supported": False,
            },
            telemetry_requirements=[
                "record breach pressure and reclosure edge separately",
                "record reclosure score and repair score as telemetry only",
                "record B2_C4 baseline and B3_C2 anchor comparison",
                "record autonomous repair and native reabsorption claim flags false",
            ],
            snapshot_replay_requirements=[
                "replay B3_C4 boundary edges and metrics from serialized selected probe",
                "reject B2 persistence as repair",
                "reject autonomous repair, native reabsorption, and native support relabels",
            ],
            negative_controls=common_negative_controls
            + [
                "B2 persistence as repair",
                "breach/reclosure telemetry as autonomous repair",
                "reclosure response as native reabsorption",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "autonomous repair intention",
                    "native reabsorption",
                    "organism repair",
                    "native support",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off breach/reclosure telemetry surface",
                "add baseline-comparison digest for B2_C4 and B3_C2 references",
                "add autonomous-repair relabel rejection hook",
            ],
            implementation_boundary=(
                "The row is Phase 8-ready only as telemetry. It does not implement or "
                "support autonomous repair, native reabsorption, or native support."
            ),
            blocked_claims=[
                "autonomous repair",
                "native reabsorption",
                "native support",
                "selfhood",
                "organism/life behavior",
                "agency",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                f"B3_C4 records reclosure score {metric(b3_c4, 'reclosure_score')} and repair score {metric(b3_c4, 'repair_score')}.",
                f"B3_C4 keeps leakage ratio {metric(b3_c4, 'leakage_ratio')} and coherence margin {metric(b3_c4, 'coherence_margin')} within the supported candidate envelope.",
                "The source explicitly blocks autonomous repair and native reabsorption interpretations.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "Native repair/reabsorption would require a separate Phase 8 implementation and stronger controls.",
            ],
            extra={
                "b3_c4_source_metrics": {
                    "reclosure_score": metric(b3_c4, "reclosure_score"),
                    "repair_score": metric(b3_c4, "repair_score"),
                    "leakage_ratio": metric(b3_c4, "leakage_ratio"),
                    "coherence_margin": metric(b3_c4, "coherence_margin"),
                    "minimum_internal_support": metric(b3_c4, "minimum_internal_support"),
                    "boundary_edges": b3_c4["boundary_edges"],
                }
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i4_row_04_n16_b4_c5_shared_medium_one_sided_contract_nat3",
            source_iteration_or_closeout="N16 selected B4_C5 shared-medium separability probe",
            artifacts=[closeout_path, requirements_path, selected_path, claim_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_basin_boundary_requirements_matrix.md",
                f"{N16}/reports/n16_selected_interaction_probe_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level B4_C5 shared-medium separability candidate from basin-A "
                "internal perspective only"
            ),
            native_question=(
                "Can original N16 B4_C5 become native shared-medium multi-basin separability "
                "telemetry?"
            ),
            primary_disposition="native_contract_candidate",
            nat_level="NAT3",
            phase8_ready=False,
            native_surface="native_shared_medium_paired_separability_telemetry_contract_gap",
            runtime_visible_inputs=[
                "basin_A_internal_side_assignments",
                "neighbor_basin_external_side_assignments",
                "shared_medium_external_side",
                "basin_separation_score",
                "boundary_exclusivity_score",
                "shared_medium_leakage",
                "merge_confusion_pressure",
                "leakage_into_neighbor_basin",
                "redirected_flux_through_coupling_channel",
                "reverse_basin_perspective_inputs_missing",
            ],
            native_state_needed=[
                "forward basin-A side assignment and edge list",
                "reverse basin-B internal-side assignment and edge list",
                "paired support/coherence metrics for both perspectives",
                "merge/leakage attribution in both directions",
            ],
            state_mutation_owner="future shared-medium paired-separability telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_shared_medium_paired_separability_telemetry_contract_gap",
                "enabled": False,
                "validated": False,
                "supported": False,
                "forward_perspective_digest": "sha256",
                "reverse_perspective_digest": "sha256_required_before_nat4",
                "paired_medium_digest": "sha256_required_before_nat4",
                "merge_pressure_digest": "sha256",
                "native_multi_basin_selfhood_claim_allowed": False,
            },
            default_off_flags={
                "native_shared_medium_paired_separability_enabled": False,
                "native_multi_basin_selfhood_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "forward_perspective_budget_valid": True,
                "reverse_perspective_budget_valid": False,
                "paired_perspective_budget_required_before_nat4": True,
            },
            telemetry_requirements=[
                "record B4_C5 basin-A internal perspective exactly",
                "record neighbor basin and shared medium as external in original N16",
                "record reverse perspective as missing rather than inferred",
                "record shared-medium leakage, neighbor leakage, coupling flux, and merge pressure separately",
            ],
            snapshot_replay_requirements=[
                "replay original B4_C5 one-sided perspective",
                "reject label swap as reverse perspective",
                "reject later derived evidence as original N16 reverse replay",
                "require source-backed reverse side state before NAT4",
            ],
            negative_controls=common_negative_controls
            + [
                "label swap as reverse perspective",
                "neighbor leakage as retention",
                "merge pressure as separability success",
                "later paired evidence backfilled into original B4_C5",
                "shared-medium separability as native multi-basin selfhood",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "reverse internal nodes",
                    "reverse support/coherence metrics",
                    "native multi-basin selfhood",
                    "hidden shared-medium route",
                ],
            },
            minimal_producer_code_needed=[
                "add paired-perspective side-state recorder",
                "add reverse basin support/coherence metric records",
                "add reverse boundary edge and medium-attribution digests",
                "add reverse later-feedback trace record",
                "validate separability, leakage, and merge controls from both perspectives",
                "add controls rejecting label swap, merge-as-success, and later-evidence backfill",
            ],
            implementation_boundary=(
                "The original N16 B4_C5 source is preserved as one-sided basin-A "
                "shared-medium evidence. It is not Phase 8-ready for paired/native "
                "multi-basin separability."
            ),
            blocked_claims=[
                "native multi-basin separability",
                "native multi-basin selfhood",
                "selfhood",
                "identity acceptance",
                "native support",
                "resource assimilation",
                "organism/life behavior",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results(
                {
                    "native_policy_or_telemetry_surface_name_present": True,
                    "record_schema_sketch_present": True,
                    "default_off_flags_present": True,
                    "enabled_validated_supported_separation_present": True,
                    "state_mutation_owner_specified": True,
                    "budget_surface_specified": True,
                    "telemetry_requirements_specified": True,
                    "negative_controls_specified": True,
                    "non_rc_quantity_audit_passes": True,
                    "claim_flags_forced_false": True,
                    "phase8_opened_false": True,
                    "native_support_opened_false": True,
                    "src_diff_empty_true": True,
                }
            ),
            evidence_notes=[
                "Original B4_C5 treats basin A as internal and the neighbor basin/shared medium as external.",
                "B4_C5 records basin separation 0.74, boundary exclusivity 0.73, shared-medium leakage 0.108, and merge pressure 0.14.",
                "The source explicitly records reverse basin perspective replay as deferred before final AP6.",
                "N19 preserves that limitation and does not backfill it from later derived experiments.",
                "The native surface name denotes a future paired-separability contract gap, not existing paired source evidence.",
            ],
            blockers_to_next_level=[
                "reverse basin perspective side-state is not source-backed in original N16",
                "paired support/coherence metrics are missing from original N16",
                "reverse boundary edge and medium feedback trace are missing from original N16",
            ],
            extra={
                "b4_c5_source_metrics": {
                    "basin_separation_score": metric(b4_c5, "basin_separation_score"),
                    "boundary_exclusivity_score": b4_c5["replay_digest_inputs"]["probe_decomposition"]["boundary_exclusivity_score"],
                    "shared_medium_leakage": metric(b4_c5, "shared_medium_leakage"),
                    "merge_confusion_pressure": metric(b4_c5, "merge_confusion_pressure"),
                    "leakage_into_neighbor_basin": metric(b4_c5, "leakage_into_neighbor_basin"),
                    "redirected_flux_through_coupling_channel": metric(b4_c5, "redirected_flux_through_coupling_channel"),
                    "coherence_margin": metric(b4_c5, "coherence_margin"),
                    "minimum_internal_support": metric(b4_c5, "minimum_internal_support"),
                },
                "source_one_sidedness_record": {
                    "basin_a_as_internal_side": True,
                    "neighbor_basin_treated_as_external_side": True,
                    "reverse_basin_perspective_replay_deferred": True,
                },
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i4_row_05_n16_original_b4c5_reverse_backfill_blocker",
            source_iteration_or_closeout="N16 B4_C5 one-sided limitation and claim boundary",
            artifacts=[closeout_path, selected_path, claim_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_selected_interaction_probe_matrix.md",
                f"{N16}/reports/n16_claim_boundary_record.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="blocked upgrade of original N16 B4_C5 into reverse/paired perspective evidence",
            native_question=(
                "Can original N16 B4_C5 be treated as source-backed reverse-perspective "
                "or paired shared-medium evidence?"
            ),
            primary_disposition="implementation_gap_blocker",
            nat_level="NAT2",
            phase8_ready=False,
            native_surface="native_shared_medium_reverse_perspective_evidence_required",
            runtime_visible_inputs=[
                "reverse_internal_side_assignments_required",
                "reverse_support_metrics_required",
                "reverse_coherence_metrics_required",
                "reverse_boundary_edge_required",
                "reverse_medium_attribution_required",
            ],
            native_state_needed=[
                "reverse-side internal nodes",
                "reverse support/coherence floor metrics",
                "reverse boundary edge across the medium",
                "paired leakage and merge attribution",
            ],
            state_mutation_owner="future paired-perspective probe producer",
            record_schema_sketch={
                "blocked_upgrade_id": "original_b4c5_reverse_backfill_blocker",
                "original_forward_digest": "sha256",
                "reverse_digest": "required_missing",
                "label_swap_allowed": False,
                "later_evidence_backfill_allowed": False,
            },
            default_off_flags={"reverse_perspective_backfill_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "status": "blocked_until_reverse_source_rows_exist",
            },
            telemetry_requirements=[
                "record original B4_C5 as one-sided",
                "record reverse perspective as missing",
                "record label-swap and later-evidence backfill as blocked",
            ],
            snapshot_replay_requirements=[
                "replay original B4_C5 without changing perspective",
                "reject reverse perspective if reverse source rows are absent",
            ],
            negative_controls=[
                "label swap as reverse perspective",
                "later paired evidence imported into original B4_C5",
                "merge/leakage as reciprocity",
                "native multi-basin selfhood relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden reverse state",
                    "hidden reverse support metric",
                    "hidden reverse boundary edge",
                ],
            },
            minimal_producer_code_needed=[
                "generate source-backed reverse-side state in a new probe",
                "record reverse support/coherence metrics",
                "record reverse boundary edge and medium attribution",
                "record reverse later-feedback trace",
                "validate separability, leakage, and merge controls under reverse perspective",
                "keep original B4_C5 one-sided in provenance",
            ],
            implementation_boundary=(
                "This is a blocker row. It names future evidence needed and rejects "
                "retroactive reinterpretation of original N16 B4_C5."
            ),
            blocked_claims=[
                "original B4_C5 paired perspective",
                "original B4_C5 native multi-basin separability",
                "native multi-basin selfhood",
                "selfhood",
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
                "The source B4_C5 replay digest has basin A as internal and neighbor basin as external.",
                "No reverse internal-side node set or reverse support/coherence metric exists in original N16.",
                "Later derived paired evidence, if any, cannot rewrite original N16 provenance.",
            ],
            blockers_to_next_level=[
                "reverse perspective source rows absent",
                "reverse support/coherence metrics absent",
                "reverse boundary edge absent",
                "label-swap and later-evidence backfill controls must fail closed",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i4_row_06_n16_boundary_selfhood_native_support_relabels_rejected",
            source_iteration_or_closeout="N16 closeout and claim-boundary record",
            artifacts=[closeout_path, claim_path, requirements_path],
            reports=[
                f"{N16}/reports/n16_closeout_and_handoff.md",
                f"{N16}/reports/n16_claim_boundary_record.md",
                f"{N16}/reports/n16_basin_boundary_requirements_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="unsafe relabel controls over AP6 boundary evidence",
            native_question=(
                "Can AP6 boundary evidence be relabeled as selfhood, identity acceptance, "
                "native support, agency, or organism/life behavior?"
            ),
            primary_disposition="unsafe_relabel_rejected",
            nat_level="NAT0",
            phase8_ready=False,
            native_surface="not_applicable_relabel_rejected",
            runtime_visible_inputs=[],
            native_state_needed=[],
            state_mutation_owner="not_applicable",
            record_schema_sketch={"relabel_claim": "string", "claim_allowed": False},
            default_off_flags={"unsafe_boundary_relabel_enabled": False},
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
                "boundary as selfhood",
                "boundary side assignment as identity acceptance",
                "structured external coherence as self-region",
                "shared-medium separability as native multi-basin selfhood",
                "boundary evidence as native support",
                "resource state as selective uptake or assimilation",
                "AP6 boundary as closed action-perception loop",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "selfhood",
                    "identity acceptance",
                    "native support",
                    "agency",
                    "organism/life",
                ],
            },
            minimal_producer_code_needed=[
                "none for this rejected relabel; preserve controls in any future native boundary surface"
            ],
            implementation_boundary="Rejected relabel row; no implementation path.",
            blocked_claims=[
                "selfhood",
                "identity acceptance",
                "semantic goal ownership",
                "agency",
                "closed action-perception loop",
                "native support",
                "native multi-basin selfhood",
                "selective uptake/resource assimilation",
                "organism/life behavior",
                "fully native agentic-like integration",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="rejected",
            nat4_gate_results=gate_results({}),
            evidence_notes=[
                "N16 final claim boundary keeps selfhood, identity acceptance, agency, native support, and life claims false.",
                "Supported null/control rows remain null/control rows, not boundary selfhood evidence.",
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
    checks = [
        {
            "check_id": "required_ap6_rows_present",
            "passed": row_ids
            == {
                "n19_i4_row_01_n16_boundary_side_state_edge_telemetry_nat4",
                "n19_i4_row_02_n16_leakage_separability_requirement_telemetry_nat4",
                "n19_i4_row_03_n16_breach_reclosure_boundary_telemetry_nat4",
                "n19_i4_row_04_n16_b4_c5_shared_medium_one_sided_contract_nat3",
                "n19_i4_row_05_n16_original_b4c5_reverse_backfill_blocker",
                "n19_i4_row_06_n16_boundary_selfhood_native_support_relabels_rejected",
            },
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
            "check_id": "nat3_and_blocked_rows_have_explicit_nat4_gate_blocker",
            "passed": all(
                not all_nat4_gates_pass(row)
                for row in rows
                if row["nat_level"] in {"NAT2", "NAT3"}
            ),
            "detail": {
                row["row_id"]: [
                    gate for gate, passed in row["nat4_gate_results"].items() if not passed
                ]
                for row in rows
                if row["nat_level"] in {"NAT2", "NAT3"}
            },
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
            "check_id": "boundary_side_state_candidate_classified",
            "passed": "n19_i4_row_01_n16_boundary_side_state_edge_telemetry_nat4" in row_ids,
            "detail": "side-state and edge telemetry row present",
        },
        {
            "check_id": "leakage_separability_candidate_classified",
            "passed": "n19_i4_row_02_n16_leakage_separability_requirement_telemetry_nat4" in row_ids,
            "detail": "requirements telemetry row present",
        },
        {
            "check_id": "b4_c5_one_sidedness_preserved",
            "passed": any(
                row["row_id"] == "n19_i4_row_04_n16_b4_c5_shared_medium_one_sided_contract_nat3"
                and row["nat_level"] == "NAT3"
                and "reverse basin perspective side-state is not source-backed in original N16"
                in row["blockers_to_next_level"]
                for row in rows
            ),
            "detail": "original B4_C5 remains one-sided and below NAT4",
        },
        {
            "check_id": "original_b4c5_reverse_backfill_blocked",
            "passed": any(
                row["row_id"] == "n19_i4_row_05_n16_original_b4c5_reverse_backfill_blocker"
                and row["row_decision"] == "blocked"
                for row in rows
            ),
            "detail": "reverse/pairing backfill row blocked",
        },
        {
            "check_id": "boundary_selfhood_native_support_relabels_rejected",
            "passed": any(
                row["row_id"] == "n19_i4_row_06_n16_boundary_selfhood_native_support_relabels_rejected"
                and row["row_decision"] == "rejected"
                and "selfhood" in row["blocked_claims"]
                and "native support" in row["blocked_claims"]
                for row in rows
            ),
            "detail": "unsafe boundary relabel row rejected",
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
        "# N19 Iteration 4 - AP6 Boundary Native-Readiness Classification",
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
            "Boundary result:",
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
    lines.extend([""])
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
        "artifact_id": "n19_ap6_boundary_native_readiness_classification",
        "schema_version": "n19_ap6_boundary_native_readiness_classification_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 4,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Classify N16 AP6 boundary side-state, leakage/separability, breach/reclosure, "
            "and shared-medium geometry native-readiness without opening Phase 8 or native support."
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
            "classified_sources": ["N16"],
            "nat4_rows": [
                row["row_id"] for row in rows if row["nat_level"] == "NAT4"
            ],
            "nat3_rows": [
                row["row_id"] for row in rows if row["nat_level"] == "NAT3"
            ],
            "blocked_rows": [
                row["row_id"] for row in rows if row["row_decision"] == "blocked"
            ],
            "rejected_rows": [
                row["row_id"] for row in rows if row["row_decision"] == "rejected"
            ],
            "phase8_ready_row_count": sum(1 for row in rows if row["phase8_ready"]),
            "ap6_phase8_ready_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["phase8_ready"]
            ],
            "native_contract_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["primary_disposition"] == "native_contract_candidate"
            ],
            "n16_boundary_side_state_classification": "NAT4 phase8-ready telemetry candidate",
            "n16_leakage_separability_classification": "NAT4 phase8-ready telemetry candidate",
            "n16_breach_reclosure_classification": "NAT4 phase8-ready telemetry candidate, not autonomous repair",
            "n16_b4_c5_classification": "NAT3 one-sided shared-medium contract; paired/native multi-basin separability blocked",
        },
        "interpretation": {
            "main_read": (
                "Iteration 4 finds strong AP6 native-readiness for boundary telemetry: "
                "N16 side-state/edge telemetry, leakage/separability requirements telemetry, "
                "and breach/reclosure telemetry are NAT4 Phase 8-ready candidates. The "
                "original B4_C5 shared-medium row remains a NAT3 one-sided contract because "
                "N16 records basin A as internal and defers reverse basin perspective replay. "
                "N19 therefore preserves B4_C5 as useful source-backed geometry without "
                "promoting it to paired/native multi-basin separability or selfhood."
            ),
            "not_supported": [
                "native support",
                "selfhood",
                "identity acceptance",
                "agency",
                "semantic goal ownership",
                "native multi-basin selfhood",
                "selective uptake/resource assimilation",
                "organism/life behavior",
                "closed action-perception loop",
                "Phase 8 implementation",
                "AP9",
            ],
            "claim_boundary": (
                "phase8_ready rows are telemetry readiness only. N19 does not implement "
                "native boundary state, native support, selfhood, or Phase 8."
            ),
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

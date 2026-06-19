#!/usr/bin/env python3
"""Build N19 Iteration 3 AP3-AP5 lower-stack candidate classification."""

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
OUTPUT = EXPERIMENT / "outputs" / "n19_lower_stack_candidate_classification.json"
REPORT = EXPERIMENT / "reports" / "n19_lower_stack_candidate_classification.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_lower_stack_candidate_classification.py"
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

N13 = "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
N14 = "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection"
N15 = "experiments/2026-06-N15-lgrc-endogenous-proxy-formation"
N12 = "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"


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


def first_present(data: dict[str, Any], paths: list[tuple[str, ...]], default: Any) -> Any:
    for path in paths:
        current: Any = data
        found = True
        for part in path:
            if not isinstance(current, dict) or part not in current:
                found = False
                break
            current = current[part]
        if found and current is not None:
            return current
    return default


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
    return {
        "path": path,
        "sha256": sha256_file(report_path),
    }


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


def closeout_metadata(source_experiment: str, inventory: dict[str, Any]) -> dict[str, str]:
    for row in inventory["source_rows"]:
        if row["source_experiment"] == source_experiment:
            return {
                "source_final_supported_ap_level": row["source_final_supported_ap_level"],
                "source_final_claim_ceiling": row["source_final_claim_ceiling"],
            }
    raise KeyError(source_experiment)


def row_base(
    *,
    row_id: str,
    source_experiment: str,
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
    metadata = closeout_metadata(source_experiment, inventory)
    row = {
        "row_id": row_id,
        "source_experiment": source_experiment,
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
    n13_closeout = f"{N13}/outputs/n13_closeout_and_handoff.json"
    n13_support = f"{N13}/outputs/n13_support_seeking_regulation_candidate.json"
    n13_schema = f"{N13}/outputs/n13_support_schema_v1.json"
    n13_target = f"{N13}/outputs/n13_support_derived_target_candidate.json"
    n13_controls = f"{N13}/outputs/n13_external_proxy_control_matrix.json"
    n12_phase8 = f"{N12}/outputs/n12_phase8_readiness_matrix.json"
    n13_reports = [
        f"{N13}/reports/n13_closeout_and_handoff.md",
        f"{N13}/reports/n13_support_seeking_regulation_candidate.md",
    ]

    n14_closeout = f"{N14}/outputs/n14_closeout_and_handoff.json"
    n14_selection = f"{N14}/outputs/n14_consequence_sensitive_selection_candidate.json"
    n14_records = f"{N14}/outputs/n14_route_consequence_records.json"
    n14_conditioned_blocker = f"{N14}/outputs/n14_route_conditioned_support_regulation_probe.json"
    n14_followout = f"{N14}/outputs/n14_route_conditioned_followout_probe.json"
    n14_control = f"{N14}/outputs/n14_consequence_control_matrix.json"
    n14_reports = [
        f"{N14}/reports/n14_closeout_and_handoff.md",
        f"{N14}/reports/n14_consequence_sensitive_selection_candidate.md",
    ]

    n15_closeout = f"{N15}/outputs/n15_closeout_and_handoff.json"
    n15_target = f"{N15}/outputs/n15_runtime_derived_target_candidate.json"
    n15_schema = f"{N15}/outputs/n15_proxy_formation_schema_v1.json"
    n15_control = f"{N15}/outputs/n15_proxy_control_matrix.json"
    n15_drift = f"{N15}/outputs/n15_bounded_drift_replay_matrix.json"
    n15_claims = f"{N15}/outputs/n15_claim_boundary_record.json"
    n15_reports = [
        f"{N15}/reports/n15_closeout_and_handoff.md",
        f"{N15}/reports/n15_runtime_derived_target_candidate.md",
    ]

    rows: list[dict[str, Any]] = []
    rows.append(
        row_base(
            row_id="n19_i3_row_01_n13_support_margin_response_policy_nat4",
            source_experiment="N13",
            source_iteration_or_closeout=(
                "N13 closeout + support-seeking regulation candidate + N12 readiness input"
            ),
            artifacts=[n13_closeout, n13_support, n13_schema, n13_target, n13_controls, n12_phase8],
            reports=n13_reports,
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP3 support-seeking regulation, support-margin, "
                "and bounded response-magnitude candidate"
            ),
            native_question=(
                "Can support-margin measurement and bounded response magnitude become a "
                "native regulation policy surface without claiming native support?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_support_margin_and_response_magnitude_policy",
            runtime_visible_inputs=[
                "final_A_support_retention",
                "support_survival_threshold",
                "support_margin",
                "support_error_signal",
                "lane_digest",
                "support_area_digest",
                "scheduled_response_amounts",
                "scheduled_response_total",
                "bounded_window_count",
                "budget_debit_surface",
            ],
            native_state_needed=[
                "source-current support retention per support area",
                "support survival threshold digest",
                "support margin / threshold deficit",
                "bounded response packet schedule",
                "budget debit before commit",
            ],
            state_mutation_owner="LGRC step or committed response-packet scheduling event boundary",
            record_schema_sketch={
                "policy_id": "native_support_margin_and_response_magnitude_policy",
                "enabled": False,
                "validated": False,
                "supported": False,
                "source_current_support_digest": "sha256",
                "threshold_digest": "sha256",
                "support_error_digest": "sha256",
                "response_magnitude_policy_id": "native_response_magnitude_policy",
                "max_correction_per_window": "float",
                "scheduled_response_digest": "sha256",
                "budget_before_digest": "sha256",
                "budget_after_digest": "sha256",
                "claim_flags_digest": "sha256",
            },
            default_off_flags={
                "native_support_margin_response_policy_enabled": False,
                "native_support_margin_response_telemetry_enabled": False,
                "native_support_mutation_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "surfaces": [
                    "support_response_packet_budget_debit",
                    "response_packet_budget_surface",
                    "node_plus_packet_budget_error",
                    "final_budget_error",
                ],
                "max_correction_per_window": 0.07,
                "total_bounded_correction_capacity": 0.28,
                "producer_direct_mutation_allowed": False,
            },
            telemetry_requirements=[
                "record source-current support margin before response scheduling",
                "record threshold deficit expression and source digests",
                "record bounded response schedule and budget debit",
                "record out-of-envelope blocker for unbounded perturbation",
                "record unsafe claim flags false at the same boundary",
            ],
            snapshot_replay_requirements=[
                "replay support retention and threshold digests",
                "recompute support error from source-current support only",
                "recompute bounded response schedule and budget debit",
                "reject duplicate schedule, stale support, external proxy, hidden target, and out-of-envelope variants",
            ],
            negative_controls=[
                "external proxy fields reused as support error",
                "hidden target injected as support condition",
                "post-hoc support label written after response",
                "unbounded perturbation envelope",
                "native support relabel",
                "support-seeking relabel as semantic goal ownership",
                "self-maintenance relabel as selfhood",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic goal",
                    "intention",
                    "selfhood state",
                    "native support flag",
                    "external proxy-as-support",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off native support-margin telemetry record",
                "add default-off response-magnitude policy schedule record",
                "add budget-debit validation hook before response packet commit",
                "add replay digest over support, threshold, response schedule, budget, and claim flags",
            ],
            implementation_boundary=(
                "N19 classifies readiness only; producer may schedule response packets, "
                "but no native support mutation or Phase 8 implementation is opened."
            ),
            blocked_claims=[
                "native support",
                "semantic goal ownership",
                "intention",
                "agency",
                "selfhood",
                "identity acceptance",
                "organism/life behavior",
                "fully native agentic-like integration",
                "Phase 8 opened",
                "Phase 8 implementation",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N13 records support error as max(0, threshold - source-current support retention).",
                "The disrupted lane schedules a bounded response total of 0.120134817816 within a four-window capacity of 0.28.",
                "N12 response magnitude readiness is consumed only as readiness input, not as native support.",
                "The mutation boundary is explicit: schedule only; step/topology owns state mutation.",
            ],
            blockers_to_next_level=[
                "NAT5/NAT6 are out of scope for N19.",
                "A later Phase 8 implementation would need to add the default-off policy surface and validate it in src.",
            ],
            extra={
                "phase8_readiness_basis": (
                    "direct lower-stack readiness: source-current support margin, bounded response "
                    "schedule, budget debit, default-off policy separation, and claim-clean controls"
                ),
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i3_row_02_n13_support_goal_selfhood_relabels_rejected",
            source_experiment="N13",
            source_iteration_or_closeout="N13 claim boundary and external proxy controls",
            artifacts=[n13_closeout, n13_controls],
            reports=[f"{N13}/reports/n13_closeout_and_handoff.md", f"{N13}/reports/n13_external_proxy_control_matrix.md"],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="unsafe relabel controls over N13 AP3 support-seeking regulation",
            native_question=(
                "Can support-seeking regulation be relabeled as semantic goal ownership, "
                "agency, selfhood, or native support?"
            ),
            primary_disposition="unsafe_relabel_rejected",
            nat_level="NAT0",
            phase8_ready=False,
            native_surface="not_applicable_relabel_rejected",
            runtime_visible_inputs=[],
            native_state_needed=[],
            state_mutation_owner="not_applicable",
            record_schema_sketch={"relabel_claim": "string", "claim_allowed": False},
            default_off_flags={"unsafe_relabel_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={"required": False, "reason": "claim-control row"},
            telemetry_requirements=["record rejected relabel and source claim boundary"],
            snapshot_replay_requirements=["replay claim flags as false"],
            negative_controls=[
                "support target as semantic goal",
                "bounded response as intention",
                "support regulation as agency",
                "self-maintenance as selfhood",
                "artifact AP3 as native support",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": ["goal ownership", "selfhood", "native support"],
            },
            minimal_producer_code_needed=[
                "none for this rejected relabel; preserve controls in any future producer surface"
            ],
            implementation_boundary="Rejected relabel row; no implementation path.",
            blocked_claims=[
                "semantic goal ownership",
                "intention",
                "agency",
                "selfhood",
                "identity acceptance",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="rejected",
            nat4_gate_results=gate_results({}),
            evidence_notes=[
                "N13 closeout forces unsafe claim flags false.",
                "External proxy and hidden target controls prevent support error from becoming semantic goal ownership.",
            ],
            blockers_to_next_level=["unsafe relabel has no native-readiness promotion path"],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i3_row_03_n14_route_consequence_selection_contract_nat3",
            source_experiment="N14",
            source_iteration_or_closeout="N14 AP4 closeout and consequence-sensitive selection candidate",
            artifacts=[n14_closeout, n14_selection, n14_records, n14_control],
            reports=n14_reports,
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP4 consequence-sensitive route selection with memory-dominant "
                "route consequence evidence"
            ),
            native_question=(
                "Can route consequence records and deterministic route-conditioned selection "
                "context become a native selection telemetry or policy surface?"
            ),
            primary_disposition="native_contract_candidate",
            nat_level="NAT3",
            phase8_ready=False,
            native_surface="native_route_consequence_selection_telemetry",
            runtime_visible_inputs=[
                "complete_candidate_route_set",
                "pre_selection_consequence_records",
                "serialized_consequence_score_components",
                "derived_consequence_rank",
                "budget_validity",
                "tie_policy",
                "selected_route",
            ],
            native_state_needed=[
                "route candidate set digest",
                "pre-selection consequence record per route",
                "route consequence score components",
                "deterministic rank and tie policy",
                "budget-validity surface",
            ],
            state_mutation_owner="future route-selection policy event boundary, default-off",
            record_schema_sketch={
                "policy_id": "native_route_consequence_selection_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "candidate_set_digest": "sha256",
                "route_records_digest": "sha256",
                "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
                "selected_route": "route_id",
                "budget_validity_digest": "sha256",
            },
            default_off_flags={
                "native_route_consequence_selection_enabled": False,
                "native_route_consequence_telemetry_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "surfaces": [
                    "n06_budget_conservation",
                    "n08_memory_budget",
                    "n09_node_plus_packet_budget_error",
                    "n13_support_response_budget_debit",
                ],
                "route_specific_support_regulation_budget_supported": False,
            },
            telemetry_requirements=[
                "record route candidate set before selection",
                "record per-route consequence components and ranks before selection",
                "record budget validity and tie policy",
                "record selected route and rejected route records",
                "record source window for memory, regulation, and support context",
            ],
            snapshot_replay_requirements=[
                "replay candidate set and consequence rank deterministically",
                "reject missing consequence records",
                "reject stale records, hidden outcome tables, post-hoc scoring, and invalid budgets",
            ],
            negative_controls=[
                "hidden outcome table",
                "post-hoc selected-route scoring",
                "route label swap",
                "missing consequence record",
                "stale consequence record",
                "semantic choice relabel",
                "intention relabel",
                "native support relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic choice",
                    "intention",
                    "hidden outcome table",
                    "native support",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off route consequence telemetry record",
                "add deterministic route rank replay digest",
                "add budget-validity and stale-record rejection hooks",
                "add source-current route-conditioned support/regulation fields before NAT4 promotion",
            ],
            implementation_boundary=(
                "N19 classifies a native contract candidate only. Current N14 route "
                "selection is memory-dominant and artifact-level."
            ),
            blocked_claims=[
                "semantic choice",
                "intention",
                "semantic goal ownership",
                "agency",
                "identity acceptance",
                "native support",
                "fully native agentic-like integration",
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
                "N14 selects route_b by derived consequence rank even though immediate affordance favors route_a.",
                "The AP4 closeout preserves a memory-dominant scope with constructed route-conditioned followout.",
                "The source itself records that upstream observed route-conditioned support/regulation remains unsupported.",
            ],
            blockers_to_next_level=[
                "route-conditioned support/regulation rows are absent upstream",
                "constructed followout cannot be treated as observed native support",
                "native route-selection mutation and telemetry surface are not implemented",
            ],
            extra={
                "nat3_reason": (
                    "The contract surface is clear and source-backed, but the route-conditioned "
                    "support/regulation gap blocks Phase 8-ready NAT4 classification."
                ),
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i3_row_04_n14_constructed_followout_native_support_blocker",
            source_experiment="N14",
            source_iteration_or_closeout="N14 route-conditioned support/regulation blocker probe",
            artifacts=[n14_closeout, n14_conditioned_blocker, n14_followout],
            reports=[
                f"{N14}/reports/n14_closeout_and_handoff.md",
                f"{N14}/reports/n14_route_conditioned_support_regulation_probe.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope=(
                "route-conditioned support/regulation followout blocker; constructed followout "
                "must not become observed native support"
            ),
            native_question=(
                "Can constructed route-conditioned followout be promoted to observed route-specific "
                "support/regulation or native support?"
            ),
            primary_disposition="implementation_gap_blocker",
            nat_level="NAT2",
            phase8_ready=False,
            native_surface="native_route_conditioned_support_regulation_observation_required",
            runtime_visible_inputs=[
                "route_candidate_id",
                "route_conditioned_support_observation",
                "route_conditioned_regulation_observation",
                "same_budget_accounting",
                "same_horizon_requirement",
            ],
            native_state_needed=[
                "route-bound support consequence row",
                "route-bound regulation consequence row",
                "same-horizon and same-budget evidence for peer routes",
            ],
            state_mutation_owner="future route-conditioned consequence observation producer",
            record_schema_sketch={
                "route_candidate_id": "route_id",
                "axis": "support_or_regulation",
                "route_conditioned": True,
                "observed_source_row_digest": "sha256",
                "same_horizon_digest": "sha256",
                "same_budget_digest": "sha256",
                "generic_source_reuse_allowed": False,
            },
            default_off_flags={"native_route_conditioned_support_regulation_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "status": "not_validated_without_route_conditioned_rows",
                "generic_support_regulation_budget_reuse_allowed": False,
            },
            telemetry_requirements=[
                "record route_candidate_id on support/regulation rows",
                "record same-horizon and same-budget status per route",
                "record generic source reuse as blocked when route-conditioned rows are absent",
            ],
            snapshot_replay_requirements=[
                "replay route label swap control",
                "replay generic source reuse control",
                "replay missing/stale route observation controls",
            ],
            negative_controls=[
                "generic support source reuse",
                "generic regulation source reuse",
                "post-hoc route conditioning",
                "route label swap",
                "constructed followout as observed support",
                "constructed followout as native support",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden route-specific support row",
                    "hidden route-specific regulation row",
                    "native support flag",
                ],
            },
            minimal_producer_code_needed=[
                "add route_candidate_id to support/regulation consequence rows",
                "add peer-route same-horizon comparison record",
                "add peer-route same-budget comparison record",
                "add rejection record for generic support/regulation reuse",
            ],
            implementation_boundary=(
                "This blocker names producer work needed before any route-conditioned "
                "support/regulation NAT4 promotion."
            ),
            blocked_claims=[
                "observed route-conditioned support consequence support",
                "observed route-conditioned regulation consequence support",
                "constructed followout as native support",
                "semantic choice",
                "intention",
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
                "N14 route-conditioned support/regulation probe records route_a and route_b support/regulation observations as unsupported.",
                "Generic N09/N13 support and regulation sources are available but generic reuse is blocked.",
                "Constructed followout is valid as artifact context, not as observed upstream route-conditioned support/regulation.",
            ],
            blockers_to_next_level=[
                "runtime-visible route-conditioned support/regulation inputs are missing",
                "generic source reuse is blocked",
                "constructed followout cannot satisfy the observed-source gate",
            ],
        )
    )
    rows.append(
        row_base(
            row_id="n19_i3_row_05_n15_proxy_derivation_contract_nat3",
            source_experiment="N15",
            source_iteration_or_closeout="N15 AP5 closeout and runtime-derived target candidate",
            artifacts=[n15_closeout, n15_target, n15_schema, n15_control, n15_drift, n15_claims],
            reports=n15_reports,
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope=(
                "artifact-level AP5 endogenous proxy formation from source-current support, "
                "memory, regulation, AP4 context, and readiness-only context"
            ),
            native_question=(
                "Can source-current target/proxy derivation become a native proxy policy "
                "surface without semantic goal ownership?"
            ),
            primary_disposition="native_contract_candidate",
            nat_level="NAT3",
            phase8_ready=False,
            native_surface="native_proxy_derivation_policy",
            runtime_visible_inputs=[
                "support_margin",
                "support_threshold",
                "current_support_retention",
                "regulation_recovery_score",
                "memory_context_score",
                "ap4_consequence_context_score",
                "readiness_context_flag",
                "weighted_sum",
                "target_center",
                "target_tolerance",
                "target_band",
                "bridge_probe_candidate_ranking",
            ],
            native_state_needed=[
                "source-current lower-stack vector",
                "frozen proxy derivation policy",
                "target-condition digest before use",
                "budget-valid candidate response ranking",
                "bounded drift/replay state",
            ],
            state_mutation_owner="future proxy-derivation policy boundary, default-off",
            record_schema_sketch={
                "policy_id": "native_proxy_derivation_policy",
                "enabled": False,
                "validated": False,
                "supported": False,
                "input_vector_digest": "sha256",
                "derivation_policy_digest": "sha256",
                "target_condition_digest": "sha256",
                "target_band": ["float", "float"],
                "bridge_rank_digest": "sha256",
                "budget_surface_digest": "sha256",
                "claim_flags_digest": "sha256",
            },
            default_off_flags={
                "native_proxy_derivation_enabled": False,
                "native_proxy_telemetry_enabled": False,
                "semantic_goal_interpretation_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "surfaces": [
                    "target_derivation_transform_budget",
                    "bridge_probe_response_budget_validity",
                    "bounded_drift_replay_budget",
                ],
                "lower_native_surface_dependency": True,
            },
            telemetry_requirements=[
                "record source-current vector and source digests",
                "record frozen derivation policy and target digest before bridge use",
                "record target-band membership for each candidate response",
                "record external proxy, hidden target, stale source, and drift controls",
            ],
            snapshot_replay_requirements=[
                "replay target derivation from serialized source-current vector",
                "replay bridge ranking against target band",
                "reject external target, post-hoc proxy, hidden target, stale source, and unbounded drift variants",
            ],
            negative_controls=[
                "externally injected target",
                "hidden target derivation",
                "post-hoc proxy formation",
                "fixture-label proxy",
                "stale source state",
                "missing source state",
                "unbounded target drift",
                "semantic goal ownership relabel",
                "native support relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic goal",
                    "intention",
                    "choice",
                    "native support",
                    "hidden target",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off proxy derivation policy record",
                "add native lower-stack input vector capture after AP3/AP4 native surfaces exist",
                "add target condition digest before use",
                "add replay digest over target derivation, bridge ranking, budget, and claim flags",
            ],
            implementation_boundary=(
                "N15 remains a native contract candidate because its target derivation "
                "depends on artifact lower-stack inputs rather than implemented native lower-stack surfaces."
            ),
            blocked_claims=[
                "semantic goal ownership",
                "intention",
                "semantic choice",
                "agency",
                "identity acceptance",
                "native support",
                "fully native agentic-like integration",
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
                "N15 generates target_center 0.887594607287 and target_band [0.817594607287, 0.957594607287] before bridge use.",
                "The generated target ranks the bounded N13 response inside band and rejects the no-response baseline outside band.",
                "N12 readiness has weight 0.0 in the derivation, so it remains context and does not change the target value.",
                "The runtime vector explicitly records the N14 constructed-followout caveat.",
            ],
            blockers_to_next_level=[
                "lower AP3/AP4 native policy surfaces are not implemented",
                "N14 route-conditioned support/regulation remains constructed or absent upstream",
                "native proxy derivation policy and replay hooks do not exist in src",
            ],
            extra={
                "nat3_reason": (
                    "The proxy contract is source-backed and replay/control clean at artifact level, "
                    "but it is not Phase 8-ready until its lower-stack inputs are native surfaces."
                ),
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i3_row_06_n15_proxy_goal_choice_relabels_rejected",
            source_experiment="N15",
            source_iteration_or_closeout="N15 claim boundary and proxy controls",
            artifacts=[n15_closeout, n15_control, n15_claims],
            reports=[
                f"{N15}/reports/n15_closeout_and_handoff.md",
                f"{N15}/reports/n15_proxy_control_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="unsafe relabel controls over N15 proxy/target formation",
            native_question=(
                "Can a generated target/proxy be relabeled as semantic goal ownership, "
                "choice, intention, agency, identity, or native support?"
            ),
            primary_disposition="unsafe_relabel_rejected",
            nat_level="NAT0",
            phase8_ready=False,
            native_surface="not_applicable_relabel_rejected",
            runtime_visible_inputs=[],
            native_state_needed=[],
            state_mutation_owner="not_applicable",
            record_schema_sketch={"relabel_claim": "string", "claim_allowed": False},
            default_off_flags={"unsafe_relabel_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={"required": False, "reason": "claim-control row"},
            telemetry_requirements=["record rejected relabel and source claim boundary"],
            snapshot_replay_requirements=["replay claim flags as false"],
            negative_controls=[
                "generated target as semantic goal",
                "target consumption as semantic choice",
                "runtime target as intention",
                "support-derived target as agency",
                "artifact AP5 as native support",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "semantic goal",
                    "semantic choice",
                    "intention",
                    "identity",
                    "native support",
                ],
            },
            minimal_producer_code_needed=[
                "none for this rejected relabel; preserve controls in any future producer surface"
            ],
            implementation_boundary="Rejected relabel row; no implementation path.",
            blocked_claims=[
                "semantic goal ownership",
                "semantic choice",
                "intention",
                "agency",
                "identity acceptance",
                "selfhood",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="rejected",
            nat4_gate_results=gate_results({}),
            evidence_notes=[
                "N15 closeout forces unsafe proxy/target promotion flags false.",
                "Proxy controls reject external, hidden, stale, post-hoc, and semantic relabel variants.",
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
    checks = [
        {
            "check_id": "required_lower_stack_rows_present",
            "passed": {row["source_experiment"] for row in rows} == {"N13", "N14", "N15"}
            and len(rows) == 6,
            "detail": [row["row_id"] for row in rows],
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
            "check_id": "primary_dispositions_valid_and_singular",
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
            "detail": [
                row["row_id"]
                for row in rows
                if row["nat_level"] == "NAT4" and all_nat4_gates_pass(row)
            ],
        },
        {
            "check_id": "nat3_rows_keep_phase8_ready_false",
            "passed": all(not row["phase8_ready"] for row in rows if row["nat_level"] == "NAT3"),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT3"],
        },
        {
            "check_id": "nat3_rows_have_explicit_nat4_gate_blocker",
            "passed": all(
                not all_nat4_gates_pass(row) for row in rows if row["nat_level"] == "NAT3"
            ),
            "detail": {
                row["row_id"]: [
                    gate
                    for gate, passed in row["nat4_gate_results"].items()
                    if not passed
                ]
                for row in rows
                if row["nat_level"] == "NAT3"
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
            "check_id": "constructed_followout_not_promoted_to_observed_native_support",
            "passed": any(
                row["row_id"] == "n19_i3_row_04_n14_constructed_followout_native_support_blocker"
                and row["row_decision"] == "blocked"
                and "constructed followout as native support" in row["blocked_claims"]
                for row in rows
            ),
            "detail": "N14 constructed followout remains blocker context, not native support.",
        },
        {
            "check_id": "n12_readiness_only_context_not_relabelled_as_native_support",
            "passed": any(
                row["row_id"] == "n19_i3_row_01_n13_support_margin_response_policy_nat4"
                and "N12 response magnitude readiness is consumed only as readiness input, not as native support."
                in row["evidence_notes"]
                for row in rows
            )
            and any(
                row["row_id"] == "n19_i3_row_05_n15_proxy_derivation_contract_nat3"
                and "N12 readiness has weight 0.0 in the derivation, so it remains context and does not change the target value."
                in row["evidence_notes"]
                for row in rows
            ),
            "detail": "N12 readiness remains readiness-only in N13 and N15 rows.",
        },
        {
            "check_id": "unsafe_goal_choice_selfhood_agency_promotions_rejected",
            "passed": all(
                blocked in {
                    claim
                    for row in rows
                    for claim in row["blocked_claims"]
                }
                for blocked in ["semantic goal ownership", "agency", "selfhood", "native support"]
            ),
            "detail": "Unsafe promotions remain in blocked_claims.",
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
        "# N19 Iteration 3 - Lower-Stack Candidate Classification",
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
        "| Row | Source | Disposition | NAT | Decision | Phase 8 Ready | Surface |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["candidate_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["source_experiment"],
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
            "Lower-stack result:",
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
        "artifact_id": "n19_lower_stack_candidate_classification",
        "schema_version": "n19_lower_stack_candidate_classification_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 3,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Classify AP3-AP5 lower-stack native-readiness candidates and blockers "
            "under the N19 schema without opening Phase 8 or native support."
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
            "classified_sources": ["N13", "N14", "N15"],
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
            "lower_stack_phase8_ready_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["phase8_ready"]
            ],
            "native_contract_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["primary_disposition"] == "native_contract_candidate"
            ],
            "n13_classification": "NAT4 phase8-ready native policy candidate",
            "n14_classification": "NAT3 native contract candidate plus route-conditioned support/regulation blocker",
            "n15_classification": "NAT3 native contract candidate plus unsafe proxy/goal relabel rejection",
        },
        "interpretation": {
            "main_read": (
                "Iteration 3 finds one lower-stack Phase 8-ready native policy candidate: "
                "N13 support-margin/response-magnitude telemetry. N14 and N15 are stronger "
                "than scaffolds because their native contracts are clear and source-backed, "
                "but they remain NAT3: N14 is limited by the constructed-followout versus "
                "observed route-conditioned support/regulation gap, and N15 depends on "
                "artifact lower-stack inputs that are not yet native surfaces."
            ),
            "not_supported": [
                "native support",
                "semantic goal ownership",
                "semantic choice",
                "intention",
                "agency",
                "selfhood",
                "identity acceptance",
                "Phase 8 implementation",
                "AP9",
            ],
            "claim_boundary": (
                "phase8_ready in the N13 row is readiness classification only. It does not "
                "open Phase 8, implement native producer code, or support native support."
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

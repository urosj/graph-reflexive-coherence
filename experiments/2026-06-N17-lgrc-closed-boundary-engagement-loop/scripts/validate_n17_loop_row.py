#!/usr/bin/env python3
"""Validate N17 loop rows against the Iteration 2 AP7 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
DEFAULT_SCHEMA = EXPERIMENT / "outputs" / "n17_loop_schema_v1.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "geometric-" + "reflexive-coherence",
    "arc-" + "of-becoming",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in ABSOLUTE_PATH_MARKERS)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def as_bool(value: Any) -> bool:
    return value is True


def trace_present(row: dict[str, Any], trace_id: str) -> bool:
    trace = row.get(trace_id)
    return isinstance(trace, dict) and trace.get("present") is True


def trace_source_backed(row: dict[str, Any], trace_id: str) -> bool:
    trace = row.get(trace_id)
    return isinstance(trace, dict) and trace.get("source_backed") is True


def trace_phase(row: dict[str, Any], trace_id: str) -> str | None:
    trace = row.get(trace_id)
    return trace.get("phase") if isinstance(trace, dict) else None


def control_status(row: dict[str, Any], control_id: str) -> str | None:
    controls = row.get("controls")
    if not isinstance(controls, dict):
        return None
    value = controls.get(control_id)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        status = value.get("status")
        return status if isinstance(status, str) else None
    return None


def control_allowed_for_row(row: dict[str, Any], control: dict[str, Any]) -> set[str]:
    expected = control.get("expected_for_supported_loop")
    if expected == "not_applicable_for_mvp_or_passed_for_resource_extension":
        if row.get("loop_family") == "resource_support_modulation_loop":
            return {"passed"}
        return {"not_applicable", "passed"}
    if expected == "not_applicable_for_mvp_or_passed_for_shared_medium_extension":
        if row.get("loop_family") == "shared_medium_reciprocal_loop":
            return {"passed"}
        return {"not_applicable", "passed"}
    return {"passed"}


def dependency_edges(row: dict[str, Any]) -> set[str]:
    trace = row.get("dependency_trace")
    edges: set[str] = set()
    if isinstance(trace, dict):
        raw_edges = trace.get("edges", [])
    else:
        raw_edges = trace if isinstance(trace, list) else []
    for edge in raw_edges:
        if isinstance(edge, str):
            edges.add(edge)
        elif isinstance(edge, dict) and isinstance(edge.get("edge_id"), str):
            edges.add(edge["edge_id"])
    return edges


def budget_valid(row: dict[str, Any]) -> bool:
    value = row.get("budget_validity")
    if value is True:
        return True
    if not isinstance(value, dict):
        return False
    return value.get("valid") is True and value.get("within_limits") is True


def replay_stable(row: dict[str, Any]) -> bool:
    return all(
        row.get(field) == "stable"
        for field in (
            "artifact_only_replay_status",
            "snapshot_load_status",
            "duplicate_replay_status",
            "order_inversion_replay_status",
        )
    )


def phase_order_valid(row: dict[str, Any], schema: dict[str, Any]) -> bool:
    expected = schema["phase_order_policy"]["ordered_phases"]
    phases = [
        trace_phase(row, "external_to_internal_trace"),
        trace_phase(row, "internal_response_trace"),
        trace_phase(row, "response_to_external_change_trace"),
        trace_phase(row, "external_feedback_to_internal_trace"),
    ]
    if phases != expected:
        return False
    timing = row.get("phase_timing")
    if not isinstance(timing, dict):
        return False
    indices = [timing.get(phase) for phase in expected]
    if not all(isinstance(index, int) for index in indices):
        return False
    return indices == sorted(indices) and len(set(indices)) == len(indices)


def validate_row(row: dict[str, Any], schema: dict[str, Any], index: int = 0) -> list[str]:
    errors: list[str] = []
    contract = schema.get("row_schema_contract")
    if not isinstance(contract, dict):
        return [f"row_{index}:schema_row_schema_contract_missing_or_malformed"]

    row_schema_fields = contract.get("row_schema_fields")
    if not isinstance(row_schema_fields, list):
        return [f"row_{index}:schema_row_schema_fields_missing_or_malformed"]

    required_fields = set(row_schema_fields)
    missing_fields = sorted(required_fields - set(row))
    if missing_fields:
        errors.append(f"row_{index}:required_fields_missing={missing_fields}")

    rung_index = schema["loop_rung_index"]
    rung = row.get("loop_rung")
    if rung not in rung_index:
        errors.append(f"row_{index}:invalid_loop_rung={rung}")
        numeric_rung = -1
    else:
        numeric_rung = rung_index[rung]
        if row.get("loop_rung_index") != numeric_rung:
            errors.append(
                f"row_{index}:loop_rung_index_mismatch={row.get('loop_rung_index')}"
            )

    row_decision_values = set(schema["row_decision_policy"].get("values", []))
    if not row_decision_values:
        row_decision_values = {"supported", "blocked", "partial", "rejected", "not_applicable"}
    if row.get("row_decision") not in row_decision_values:
        errors.append(f"row_{index}:invalid_row_decision={row.get('row_decision')}")

    row_type_values = contract.get("row_type_values")
    if not isinstance(row_type_values, list):
        errors.append(f"row_{index}:schema_row_type_values_missing_or_malformed")
        row_type_values = []
    if row_type_values and row.get("row_type") not in set(row_type_values):
        errors.append(f"row_{index}:invalid_row_type={row.get('row_type')}")

    loop_family_values = contract.get("loop_families")
    if not isinstance(loop_family_values, list):
        errors.append(f"row_{index}:schema_loop_families_missing_or_malformed")
        loop_family_values = []
    loop_families = set(loop_family_values)
    if row.get("loop_family") not in loop_families:
        errors.append(f"row_{index}:invalid_loop_family={row.get('loop_family')}")

    closed_allowed = row.get("closed_loop_claim_allowed") is True
    final_ap7 = row.get("final_ap7_supported") is True
    if final_ap7:
        errors.append(f"row_{index}:row_level_final_ap7_supported_forbidden")

    if row.get("row_decision") in {"blocked", "partial", "rejected", "not_applicable"} and closed_allowed:
        errors.append(f"row_{index}:non_supported_row_decision_forces_closed_loop_false")

    if numeric_rung < 3 and closed_allowed:
        errors.append(f"row_{index}:g0_g1_g2_cannot_allow_closed_loop_claim")

    gates = row.get("ap7_gates")
    if not isinstance(gates, dict):
        gates = {}
        if closed_allowed:
            errors.append(f"row_{index}:ap7_gates_missing")

    required_gates = schema["ap7_required_gates"]
    missing_gate_keys = [gate for gate in required_gates if gate not in gates]
    if closed_allowed and missing_gate_keys:
        errors.append(f"row_{index}:ap7_gate_keys_missing={missing_gate_keys}")

    false_gates = [gate for gate in required_gates if gates.get(gate) is not True]
    if closed_allowed and false_gates:
        errors.append(f"row_{index}:closed_loop_claim_with_false_gates={false_gates}")

    trace_legs = schema["trace_leg_policy"]["trace_legs"]
    present_legs = [leg for leg in trace_legs if trace_present(row, leg)]
    backed_legs = [leg for leg in trace_legs if trace_source_backed(row, leg)]
    if closed_allowed and len(present_legs) != len(trace_legs):
        errors.append(f"row_{index}:closed_loop_requires_all_trace_legs")
    if closed_allowed and len(backed_legs) != len(trace_legs):
        errors.append(f"row_{index}:closed_loop_requires_source_backed_trace_legs")

    if numeric_rung == 2 and set(present_legs) >= set(trace_legs[:3]):
        if closed_allowed or gates.get("g3_or_higher") is True:
            errors.append(f"row_{index}:g2_outbound_change_cannot_pass_without_fourth_leg")

    if closed_allowed and not phase_order_valid(row, schema):
        errors.append(f"row_{index}:monotonic_phase_order_invalid")

    if closed_allowed:
        if row.get("response_caused_external_change") is not True:
            errors.append(f"row_{index}:response_caused_external_change_required")
        if row.get("external_change_would_occur_without_response") is not False:
            errors.append(f"row_{index}:external_change_counterfactual_required")
        if row.get("later_internal_depends_on_changed_external_state") is not True:
            errors.append(f"row_{index}:later_internal_feedback_dependence_required")
        if row.get("feedback_removed_control_changes_result") is not True:
            errors.append(f"row_{index}:feedback_removed_control_must_change_result")

    required_edges = set(schema["dependency_trace_format"]["required_edges"])
    if closed_allowed and not required_edges <= dependency_edges(row):
        errors.append(f"row_{index}:dependency_trace_missing_required_edges")

    control_requirements = schema.get("control_requirements")
    if not isinstance(control_requirements, list):
        control_requirements = []
        if closed_allowed:
            errors.append(f"row_{index}:schema_control_requirements_missing_or_malformed")
    if closed_allowed:
        missing_controls = [
            control["control_id"]
            for control in control_requirements
            if control_status(row, control["control_id"]) not in control_allowed_for_row(row, control)
        ]
        if missing_controls:
            errors.append(f"row_{index}:required_controls_not_passed={missing_controls}")
        if not replay_stable(row):
            errors.append(f"row_{index}:replay_status_not_stable")
        if not budget_valid(row):
            errors.append(f"row_{index}:budget_validity_required")

    replay_inputs = row.get("replay_digest_inputs")
    required_replay_inputs = set(schema["replay_digest_policy"]["include_fields"])
    if closed_allowed:
        if not isinstance(replay_inputs, list):
            errors.append(f"row_{index}:replay_digest_inputs_missing")
        elif not required_replay_inputs <= set(replay_inputs):
            errors.append(f"row_{index}:replay_digest_inputs_incomplete")

    claim_flags = row.get("claim_flags")
    if not isinstance(claim_flags, dict):
        if closed_allowed:
            errors.append(f"row_{index}:claim_flags_missing")
    else:
        unsafe_true = [
            flag
            for flag in schema["claim_boundary_policy"]["required_false_flags"]
            if claim_flags.get(flag) is True
        ]
        if unsafe_true:
            errors.append(f"row_{index}:unsafe_claim_flags_true={unsafe_true}")

    if contains_absolute_path(row):
        errors.append(f"row_{index}:absolute_path_detected")

    return errors


def rows_from_artifact(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    if "rows" in artifact and isinstance(artifact["rows"], list):
        return [row for row in artifact["rows"] if isinstance(row, dict)]
    return [artifact]


def validate_artifact(artifact: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contains_absolute_path(artifact):
        errors.append("artifact:absolute_path_detected")
    output_digest = artifact.get("output_digest")
    if output_digest is not None and not (isinstance(output_digest, str) and HEX64.match(output_digest)):
        errors.append("artifact:output_digest_not_sha256")
    for index, row in enumerate(rows_from_artifact(artifact)):
        errors.extend(validate_row(row, schema, index))
    return errors


def complete_row() -> dict[str, Any]:
    controls = {
        control_id: "passed"
        for control_id in [
            "artifact_only_replay_control",
            "snapshot_load_replay_control",
            "duplicate_replay_control",
            "order_inversion_replay_control",
            "post_hoc_loop_stitching_control",
            "hidden_external_state_memory_control",
            "hidden_internal_state_carryover_control",
            "outbound_response_relabel_control",
            "external_change_not_caused_by_response_control",
            "feedback_order_inversion_control",
            "feedback_removed_control",
            "one_way_crossing_relabel_control",
            "semantic_agency_relabel_control",
            "semantic_intention_relabel_control",
            "semantic_action_perception_relabel_control",
            "native_support_relabel_control",
            "selfhood_identity_relabel_control",
            "organism_life_relabel_control",
        ]
    }
    controls["resource_depletion_goal_pursuit_relabel_control"] = "not_applicable"
    controls["shared_medium_merge_relabel_as_reciprocal_loop_control"] = "not_applicable"
    gates = {
        gate: True
        for gate in [
            "g3_or_higher",
            "four_trace_legs_present",
            "four_trace_legs_source_backed",
            "monotonic_phase_order_valid",
            "response_caused_external_change",
            "external_change_counterfactual_blocks_spontaneous_change",
            "later_internal_depends_on_changed_external_state",
            "feedback_removed_control_passed",
            "one_way_crossing_null_blocked",
            "dependency_trace_complete",
            "replay_digest_valid",
            "budget_validity_passed",
            "controls_passed",
            "claim_boundary_clean",
            "source_registry_backed",
            "no_absolute_paths",
        ]
    }
    claim_flags = {
        flag: False
        for flag in [
            "agency_claim_opened",
            "intention_claim_opened",
            "semantic_action_opened",
            "semantic_perception_opened",
            "semantic_goal_ownership_opened",
            "selfhood_claim_opened",
            "identity_acceptance_opened",
            "native_support_opened",
            "organism_life_opened",
            "fully_native_integration_opened",
            "unrestricted_agency_opened",
            "phase8_opened",
        ]
    }
    return {
        "row_id": "validator_self_test_complete_g3",
        "row_type": "validator_self_test_not_evidence",
        "loop_family": "perturbation_response_recovery_loop",
        "loop_rung": "G3",
        "loop_rung_index": 3,
        "source_row_ids": ["n17_i1_row_03_n16_b3_c4_breach_reclosure"],
        "source_artifacts": [],
        "row_decision": "supported",
        "boundary_assignments": {"internal": "source_backed", "external": "source_backed"},
        "external_to_internal_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t0_external_pressure_or_crossing",
            "state_before": "external_pressure_absent",
            "state_after": "external_pressure_crossed",
            "dependency_note": "self-test",
        },
        "internal_response_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t1_internal_support_update",
            "state_before": "support_pre",
            "state_after": "support_shift",
            "dependency_note": "self-test",
        },
        "response_to_external_change_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t2_response_caused_external_change",
            "state_before": "external_pressure_crossed",
            "state_after": "external_pressure_changed_by_response",
            "dependency_note": "self-test",
        },
        "external_feedback_to_internal_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t3_later_internal_support_conditioned_by_changed_external_state",
            "state_before": "external_pressure_changed_by_response",
            "state_after": "later_support_conditioned",
            "dependency_note": "self-test",
        },
        "phase_timing": {
            "t0_external_pressure_or_crossing": 0,
            "t1_internal_support_update": 1,
            "t2_response_caused_external_change": 2,
            "t3_later_internal_support_conditioned_by_changed_external_state": 3,
        },
        "monotonic_phase_order": True,
        "response_caused_external_change": True,
        "external_change_would_occur_without_response": False,
        "later_internal_depends_on_changed_external_state": True,
        "feedback_removed_control_changes_result": True,
        "loop_closure_evidence": {
            "ordered_closure_present": True,
            "closure_not_posthoc": True,
        },
        "dependency_trace": {
            "edges": [
                {"edge_id": "external_to_internal"},
                {"edge_id": "internal_response_to_external_change"},
                {"edge_id": "changed_external_to_later_internal"},
            ]
        },
        "budget_cost_surface": {"hidden_state_allowance": 0},
        "budget_units": "normalized_cost",
        "budget_validity": {"valid": True, "within_limits": True},
        "replay_digest_inputs": [
            "schema_version",
            "source_row_ids",
            "source_artifacts",
            "loop_policy_digest",
            "boundary_assignments",
            "row_decision",
            "external_to_internal_trace",
            "internal_response_trace",
            "response_to_external_change_trace",
            "external_feedback_to_internal_trace",
            "phase_timing",
            "monotonic_phase_order",
            "response_caused_external_change",
            "later_internal_depends_on_changed_external_state",
            "loop_closure_evidence",
            "dependency_trace",
            "budget_cost_surface",
            "budget_validity",
            "controls",
            "ap7_gates",
            "claim_flags",
            "closed_loop_claim_allowed",
        ],
        "replay_digest_algorithm": "sha256_canonical_json",
        "artifact_only_replay_status": "stable",
        "snapshot_load_status": "stable",
        "duplicate_replay_status": "stable",
        "order_inversion_replay_status": "stable",
        "controls": controls,
        "ap7_gates": gates,
        "closed_loop_claim_allowed": True,
        "provisional_ap_level": "AP7_candidate",
        "provisional_claim_ceiling": "artifact_level_closed_boundary_engagement_loop_candidate",
        "claim_flags": claim_flags,
        "blocked_claims": [],
        "missing_gates": [],
        "final_ap7_supported": False,
    }


def run_self_tests(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    complete = complete_row()
    if validate_row(complete, schema):
        errors.append("self_test:complete_g3_should_pass_validator")

    g2_bad = json.loads(json.dumps(complete))
    g2_bad["row_id"] = "validator_self_test_g2_bad"
    g2_bad["loop_rung"] = "G2"
    g2_bad["loop_rung_index"] = 2
    g2_bad["external_feedback_to_internal_trace"]["present"] = False
    g2_bad["ap7_gates"]["g3_or_higher"] = True
    if not validate_row(g2_bad, schema):
        errors.append("self_test:g2_outbound_without_feedback_should_fail")

    no_feedback_control = json.loads(json.dumps(complete))
    no_feedback_control["row_id"] = "validator_self_test_no_feedback_control"
    no_feedback_control["feedback_removed_control_changes_result"] = False
    no_feedback_control["controls"]["feedback_removed_control"] = "blocked"
    if not validate_row(no_feedback_control, schema):
        errors.append("self_test:missing_feedback_removed_control_should_fail")

    after_not_caused = json.loads(json.dumps(complete))
    after_not_caused["row_id"] = "validator_self_test_after_not_caused"
    after_not_caused["response_caused_external_change"] = False
    after_not_caused["external_change_would_occur_without_response"] = True
    if not validate_row(after_not_caused, schema):
        errors.append("self_test:external_change_after_not_caused_should_fail")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", help="row or row-bearing artifact to validate")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="schema artifact path")
    parser.add_argument("--self-test", action="store_true", help="run validator self-tests")
    args = parser.parse_args()

    schema = load_json(Path(args.schema))
    errors: list[str] = []
    if args.self_test:
        errors.extend(run_self_tests(schema))
    if args.artifact:
        errors.extend(validate_artifact(load_json(Path(args.artifact)), schema))

    result = {
        "status": "passed" if not errors else "failed",
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

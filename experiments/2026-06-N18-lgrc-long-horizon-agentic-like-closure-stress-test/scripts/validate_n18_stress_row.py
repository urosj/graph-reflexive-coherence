#!/usr/bin/env python3
"""Validate N18 stress rows against the Iteration 2 AP8 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
DEFAULT_SCHEMA = EXPERIMENT / "outputs" / "n18_long_horizon_schema_v1.json"
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


def trace_present(row: dict[str, Any], trace_id: str) -> bool:
    trace = row.get(trace_id)
    return isinstance(trace, dict) and trace.get("present") is True


def trace_source_backed(row: dict[str, Any], trace_id: str) -> bool:
    trace = row.get(trace_id)
    return isinstance(trace, dict) and trace.get("source_backed") is True


def replay_status_passed(row: dict[str, Any], status_field: str, expected: str) -> bool:
    return row.get(status_field) == expected


def unsafe_flags_false(row: dict[str, Any]) -> bool:
    flags = row.get("unsafe_claim_flags")
    return isinstance(flags, dict) and all(value is False for value in flags.values())


def linked_trace_continuity_valid(row: dict[str, Any], schema: dict[str, Any]) -> bool:
    policy = schema.get("linked_trace_policy", {})
    required_links = policy.get("required_links", [])
    links = row.get("linked_trace_continuity")
    if not isinstance(links, dict):
        return False
    for link in required_links:
        value = links.get(link)
        if value is True:
            continue
        if isinstance(value, dict) and value.get("present") is True and value.get("source_current") is True:
            continue
        return False
    return True


def cross_axis_continuity_valid(row: dict[str, Any]) -> bool:
    evidence = row.get("cross_axis_continuity_evidence")
    if evidence is True:
        return True
    if not isinstance(evidence, dict):
        return False
    if evidence.get("present") is not True:
        return False
    if evidence.get("source_current") is not True:
        return False
    linked_edges = evidence.get("linked_edges")
    if linked_edges is None:
        return True
    return isinstance(linked_edges, list) and len(linked_edges) > 0


def single_axis_stale_controls_valid(row: dict[str, Any], schema: dict[str, Any]) -> bool:
    controls = row.get("single_axis_stale_controls")
    if not isinstance(controls, dict):
        return False
    required_controls = [
        item["control_id"]
        for item in schema.get("control_requirements", [])
        if item.get("failure_blocks_gate") == "single_axis_stale_controls_passed"
    ]
    return all(controls.get(control_id) == "failed_expected" for control_id in required_controls)


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


def budget_valid(row: dict[str, Any]) -> bool:
    if row.get("budget_valid") is True:
        return True
    budget = row.get("budget_surface")
    return isinstance(budget, dict) and budget.get("valid") is True


def source_digests_valid(row: dict[str, Any]) -> bool:
    digests = row.get("source_digests")
    if not isinstance(digests, list) or not digests:
        return False
    for item in digests:
        if isinstance(item, str):
            if HEX64.match(item) is None:
                return False
        elif isinstance(item, dict):
            values = [
                value
                for key, value in item.items()
                if key in {"sha256", "source_sha256", "output_digest", "source_output_digest"}
            ]
            if not values or any(not isinstance(value, str) or HEX64.match(value) is None for value in values):
                return False
        else:
            return False
    return True


def source_claim_ceilings_valid(row: dict[str, Any]) -> bool:
    ceilings = row.get("source_claim_ceilings")
    return isinstance(ceilings, list) and len(ceilings) > 0 and all(
        isinstance(item, str) and item for item in ceilings
    )


def claim_ceiling_allowed(row: dict[str, Any], schema: dict[str, Any]) -> bool:
    claim = row.get("claim_ceiling")
    if not isinstance(claim, str):
        return False
    allowed = set(schema.get("claim_ceiling_policy", {}).get("allowed_ap8_claim_ceilings", []))
    return claim in allowed


def validate_row(row: dict[str, Any], schema: dict[str, Any], index: int = 0) -> list[str]:
    errors: list[str] = []
    contract = schema.get("row_schema_contract")
    if not isinstance(contract, dict):
        return [f"row_{index}:schema_row_schema_contract_missing"]

    required_fields = set(contract.get("row_schema_fields", []))
    missing_fields = sorted(required_fields - set(row))
    if missing_fields:
        errors.append(f"row_{index}:required_fields_missing={missing_fields}")

    ladder_index = schema.get("stress_ladder_index", {})
    rung = row.get("stress_ladder_rung")
    if rung not in ladder_index:
        errors.append(f"row_{index}:invalid_stress_ladder_rung={rung}")
        numeric_rung = -1
    else:
        numeric_rung = ladder_index[rung]
        if row.get("stress_ladder_index") != numeric_rung:
            errors.append(
                f"row_{index}:stress_ladder_index_mismatch={row.get('stress_ladder_index')}"
            )

    if row.get("row_type") not in set(contract.get("row_type_values", [])):
        errors.append(f"row_{index}:invalid_row_type={row.get('row_type')}")

    if row.get("row_decision") not in set(contract.get("row_decision_values", [])):
        errors.append(f"row_{index}:invalid_row_decision={row.get('row_decision')}")

    if row.get("stress_dimension") not in set(schema.get("stress_dimensions", [])):
        errors.append(f"row_{index}:invalid_stress_dimension={row.get('stress_dimension')}")

    dimension_policy = schema.get("stress_ladder_dimension_policy", {})
    if row.get("stress_dimension") in dimension_policy:
        allowed_rungs = set(dimension_policy[row["stress_dimension"]])
        if row.get("stress_ladder_rung") not in allowed_rungs:
            errors.append(
                f"row_{index}:stress_dimension_rung_mismatch="
                f"{row.get('stress_dimension')}:{row.get('stress_ladder_rung')}"
            )

    ap8_allowed = row.get("ap8_candidate_allowed") is True
    if row.get("final_ap8_supported") is True:
        errors.append(f"row_{index}:row_level_final_ap8_supported_forbidden")

    if row.get("row_decision") in {"partial", "blocked", "rejected", "not_applicable"} and ap8_allowed:
        errors.append(f"row_{index}:non_supported_row_decision_forces_ap8_false")

    if row.get("stress_dimension") == "baseline_ap7_replay" and ap8_allowed:
        errors.append(f"row_{index}:baseline_ap7_replay_cannot_allow_ap8")

    if ap8_allowed and row.get("evidence_branch") != "artifact_only":
        errors.append(f"row_{index}:evidence_branch_must_be_artifact_only")
    if ap8_allowed and row.get("native_branch_opened") is not False:
        errors.append(f"row_{index}:native_branch_opened_must_be_false")
    if ap8_allowed and row.get("phase8_branch_opened") is not False:
        errors.append(f"row_{index}:phase8_branch_opened_must_be_false")
    if ap8_allowed and row.get("horizon_extrapolation_allowed") is not False:
        errors.append(f"row_{index}:horizon_extrapolation_must_be_false")
    if ap8_allowed and not row.get("max_supported_horizon"):
        errors.append(f"row_{index}:max_supported_horizon_required")
    if ap8_allowed and not isinstance(row.get("source_backed_horizon_envelope"), dict):
        errors.append(f"row_{index}:source_backed_horizon_envelope_required")
    if ap8_allowed and not isinstance(row.get("source_rows"), list):
        errors.append(f"row_{index}:source_rows_must_be_list")
    if ap8_allowed and isinstance(row.get("source_rows"), list) and not row["source_rows"]:
        errors.append(f"row_{index}:source_rows_required_for_ap8")
    if ap8_allowed and not source_digests_valid(row):
        errors.append(f"row_{index}:source_digests_must_be_sha256")
    if ap8_allowed and not source_claim_ceilings_valid(row):
        errors.append(f"row_{index}:source_claim_ceilings_required")
    if ap8_allowed and not claim_ceiling_allowed(row, schema):
        errors.append(f"row_{index}:claim_ceiling_not_allowed_for_ap8")

    gates = row.get("ap8_gates")
    if not isinstance(gates, dict):
        gates = {}
        if ap8_allowed:
            errors.append(f"row_{index}:ap8_gates_missing")

    required_gates = schema.get("ap8_required_gates", [])
    false_gates = [gate for gate in required_gates if gates.get(gate) is not True]
    if ap8_allowed and false_gates:
        errors.append(f"row_{index}:ap8_candidate_with_false_gates={false_gates}")

    trace_fields = contract.get("trace_fields", [])
    missing_traces = [trace for trace in trace_fields if not trace_present(row, trace)]
    unbacked_traces = [
        trace for trace in trace_fields if not trace_source_backed(row, trace)
    ]
    if ap8_allowed and missing_traces:
        errors.append(f"row_{index}:ap8_requires_all_trace_axes={missing_traces}")
    if ap8_allowed and unbacked_traces:
        errors.append(f"row_{index}:ap8_requires_source_backed_trace_axes={unbacked_traces}")

    if ap8_allowed and not linked_trace_continuity_valid(row, schema):
        errors.append(f"row_{index}:linked_trace_continuity_required")

    if ap8_allowed and not cross_axis_continuity_valid(row):
        errors.append(f"row_{index}:cross_axis_continuity_evidence_required")

    if ap8_allowed and not row.get("long_horizon_continuity_evidence"):
        errors.append(f"row_{index}:long_horizon_continuity_evidence_required")

    if ap8_allowed and not budget_valid(row):
        errors.append(f"row_{index}:budget_valid_required")

    if ap8_allowed and not single_axis_stale_controls_valid(row, schema):
        errors.append(f"row_{index}:single_axis_stale_controls_required")

    replay_expectations = schema["replay_digest_policy"][
        "required_replay_statuses_for_ap8"
    ]
    for field, expected in replay_expectations.items():
        if ap8_allowed and not replay_status_passed(row, field, expected):
            errors.append(f"row_{index}:replay_status_{field}_expected_{expected}")

    if ap8_allowed and not unsafe_flags_false(row):
        errors.append(f"row_{index}:unsafe_claim_flags_must_be_false")

    if row.get("phase8_opened") is True and ap8_allowed:
        errors.append(f"row_{index}:phase8_opened_blocks_artifact_only_ap8")
    if row.get("native_support_opened") is True and ap8_allowed:
        errors.append(f"row_{index}:native_support_opened_blocks_artifact_only_ap8")

    if ap8_allowed:
        for control in schema.get("control_requirements", []):
            expected = control.get("expected_status_for_ap8")
            if expected is None:
                continue
            observed = control_status(row, control["control_id"])
            if observed != expected:
                errors.append(
                    f"row_{index}:control_{control['control_id']}_expected_{expected}"
                )

    digest = row.get("artifact_only_replay_digest")
    if ap8_allowed and not (isinstance(digest, str) and HEX64.match(digest)):
        errors.append(f"row_{index}:artifact_only_replay_digest_must_be_sha256")

    if contains_absolute_path(row):
        errors.append(f"row_{index}:absolute_path_detected")

    return errors


def rows_from_document(document: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(document.get("rows"), list):
        return [row for row in document["rows"] if isinstance(row, dict)]
    if isinstance(document.get("stress_rows"), list):
        return [row for row in document["stress_rows"] if isinstance(row, dict)]
    if isinstance(document.get("row"), dict):
        return [document["row"]]
    return [document]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path, nargs="?", help="JSON artifact or row to validate")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    schema = load_json(args.schema)
    if args.self_test:
        probe = {
            "row_id": "validator_self_test_gated_row",
            "row_type": "validator_self_test_not_evidence",
            "stress_id": "self_test",
            "stress_dimension": "baseline_ap7_replay",
            "stress_ladder_rung": "L1",
            "stress_ladder_index": 1,
            "horizon_window": {"window_id": "baseline"},
            "max_supported_horizon": "baseline_only",
            "source_backed_horizon_envelope": {},
            "horizon_extrapolation_allowed": False,
            "evidence_branch": "artifact_only",
            "native_branch_opened": False,
            "phase8_branch_opened": False,
            "source_rows": [],
            "source_claim_ceilings": [],
            "source_digests": [],
            "budget_surface": {"valid": False},
            "budget_valid": False,
            "support_state_trace": {"present": False, "source_backed": False},
            "memory_context_trace": {"present": False, "source_backed": False},
            "regulation_trace": {"present": False, "source_backed": False},
            "selection_context_trace": {"present": False, "source_backed": False},
            "proxy_target_trace": {"present": False, "source_backed": False},
            "boundary_separation_trace": {"present": False, "source_backed": False},
            "closed_loop_feedback_trace": {"present": False, "source_backed": False},
            "linked_trace_continuity": {},
            "cross_axis_continuity_evidence": False,
            "long_horizon_continuity_evidence": False,
            "artifact_only_replay_digest": digest_value({"self_test": True}),
            "artifact_only_reconstruction_status": "not_run",
            "duplicate_replay_status": "not_run",
            "snapshot_load_replay_status": "not_run",
            "stale_state_control_status": "not_run",
            "order_inversion_status": "not_run",
            "post_hoc_stitching_control_status": "not_run",
            "single_axis_stale_controls": {},
            "controls": {},
            "ap8_gates": {},
            "row_decision": "blocked",
            "claim_ceiling": "validator_self_test_not_evidence",
            "ap8_candidate_allowed": True,
            "final_ap8_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "unsafe_claim_flags": {"agency_claim_opened": False},
            "missing_gates": schema.get("ap8_required_gates", []),
            "ap8_outcome_classification": "AP8_blocked",
        }
        errors = validate_row(probe, schema)
        if not errors:
            raise SystemExit("self-test failed: invalid AP8 row passed")
        print("self-test passed")
        return

    if args.artifact is None:
        parser.error("artifact is required unless --self-test is used")

    document = load_json(args.artifact)
    errors: list[str] = []
    for index, row in enumerate(rows_from_document(document)):
        errors.extend(validate_row(row, schema, index))

    result = {
        "artifact": args.artifact.as_posix(),
        "schema": args.schema.as_posix(),
        "row_count": len(rows_from_document(document)),
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

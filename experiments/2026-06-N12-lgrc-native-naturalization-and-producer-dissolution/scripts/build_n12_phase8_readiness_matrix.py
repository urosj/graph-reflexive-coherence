#!/usr/bin/env python3
"""Build N12 Iteration 7 Phase 8 readiness matrix."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"
ITERATION_3_OUTPUT = OUTPUTS / "n12_route_conductance_memory_candidate.json"
ITERATION_3_REPORT = REPORTS / "n12_route_conductance_memory_candidate.md"
ITERATION_4_OUTPUT = OUTPUTS / "n12_response_magnitude_candidate.json"
ITERATION_4_REPORT = REPORTS / "n12_response_magnitude_candidate.md"
ITERATION_5_OUTPUT = OUTPUTS / "n12_identity_acceptance_boundary.json"
ITERATION_5_REPORT = REPORTS / "n12_identity_acceptance_boundary.md"
ITERATION_6_OUTPUT = OUTPUTS / "n12_agentic_like_integration_boundary.json"
ITERATION_6_REPORT = REPORTS / "n12_agentic_like_integration_boundary.md"

OUTPUT_PATH = OUTPUTS / "n12_phase8_readiness_matrix.json"
REPORT_PATH = REPORTS / "n12_phase8_readiness_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_phase8_readiness_matrix.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": digest_file(path)}


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def build_ready_contract(
    *,
    order: int,
    source_path: Path,
    artifact: dict[str, Any],
    row_key: str,
    contract_label: str,
) -> dict[str, Any]:
    row = artifact[row_key]
    result = artifact["candidate_result"]
    return {
        "row_id": f"n12_i7_phase8_ready_{order:02d}_{row['native_policy_name']}",
        "source_artifact": rel(source_path),
        "source_output_digest": artifact["output_digest"],
        "source_row_digest": row["row_digest"],
        "contract_label": contract_label,
        "contract_type": "phase8_ready_native_policy_candidate_contract",
        "native_policy_name": row["native_policy_name"],
        "primary_disposition": row["primary_disposition"],
        "nat_level": row["nat_level"],
        "phase8_ready": row["phase8_ready"],
        "phase8_opened": False,
        "phase8_implementation_allowed_in_n12": False,
        "native_support_opened": result["native_support_opened"],
        "claim_ceiling": row["claim_ceiling"],
        "record_schema_sketch": row["record_schema_sketch"],
        "default_off_flags": row["default_off_flags"],
        "enabled_validated_supported_separation": row[
            "enabled_validated_supported_separation"
        ],
        "idempotency_digest_plan": row["idempotency_digest_plan"],
        "runtime_visible_inputs": row["runtime_visible_inputs"],
        "budget_surfaces": row["budget_surfaces"],
        "budget_semantics": row.get("budget_semantics", {}),
        "telemetry_namespace": row.get("telemetry_namespaces", {}).get(
            "primary_native_namespace"
        ),
        "telemetry_requirements": row["telemetry_requirements"],
        "snapshot_replay_requirements": row["snapshot_replay_requirements"],
        "negative_controls": row["negative_controls"],
        "compatibility_tests": row["compatibility_tests"],
        "mutation_boundary": row["mutation_boundary"],
        "non_rc_quantity_audit": row["non_rc_quantity_audit"],
        "claim_flags_forced_false": row["claim_flags_forced_false"],
        "blocked_claims": row["blocked_claims"],
        "acceptance_gates": {
            "src_diff_empty": row["src_diff_empty"],
            "native_supported_flags_false": row["native_supported_flags_false"],
            "phase8_opened_false": row["phase8_opened_false"],
            "claim_flags_all_false": all_claim_flags_false(
                row["claim_flags_forced_false"]
            ),
            "default_off_flags_present": bool(row["default_off_flags"]),
            "telemetry_requirements_present": bool(row["telemetry_requirements"]),
            "compatibility_tests_present": bool(row["compatibility_tests"]),
            "negative_controls_present": bool(row["negative_controls"]),
            "mutation_boundary_specified": (
                row["mutation_boundary"].get("producer_or_policy_may_schedule_only")
                is True
                and row["mutation_boundary"].get(
                    "step_or_topology_event_owns_state_mutation"
                )
                is True
            ),
        },
    }


def build_deferred_blocker(
    *,
    order: int,
    source_path: Path,
    artifact: dict[str, Any],
    row_key: str,
    blocker_label: str,
) -> dict[str, Any]:
    row = artifact[row_key]
    result = artifact["boundary_result"]
    missing_records = row["record_schema_sketch"].get(
        "records_missing_before_phase8_entry", []
    )
    current_scope_records = row.get("covered_policy_records", [])
    return {
        "row_id": f"n12_i7_deferred_{order:02d}_{row['native_policy_name']}",
        "source_artifact": rel(source_path),
        "source_output_digest": artifact["output_digest"],
        "source_row_digest": row["row_digest"],
        "blocker_label": blocker_label,
        "disposition": row["primary_disposition"],
        "native_policy_name": row["native_policy_name"],
        "nat_level": row["nat_level"],
        "phase8_ready": row["phase8_ready"],
        "phase8_opened": False,
        "native_support_opened": result["native_support_opened"],
        "claim_ceiling": row["claim_ceiling"],
        "current_scope_records": current_scope_records,
        "required_future_policy_records": missing_records,
        "required_future_policy_records_note": (
            "Records listed here are required before future Phase 8 entry; "
            "they are not native support records opened by N12."
        ),
        "missing_gates": row["missing_gates"],
        "deferred_phase8_requirements": row["deferred_phase8_requirements"],
        "telemetry_requirements": row["telemetry_requirements"],
        "snapshot_replay_requirements": row["snapshot_replay_requirements"],
        "negative_controls": row["negative_controls"],
        "compatibility_tests": row["compatibility_tests"],
        "mutation_boundary": row["mutation_boundary"],
        "non_rc_quantity_audit": row["non_rc_quantity_audit"],
        "claim_flags_forced_false": row["claim_flags_forced_false"],
        "blocked_claims": row["blocked_claims"],
        "blocker_gates": {
            "src_diff_empty": row["src_diff_empty"],
            "native_supported_flags_false": row["native_supported_flags_false"],
            "phase8_opened_false": row["phase8_opened_false"],
            "claim_flags_all_false": all_claim_flags_false(
                row["claim_flags_forced_false"]
            ),
            "phase8_ready_false": row["phase8_ready"] is False,
            "missing_gates_present": bool(row["missing_gates"]),
            "deferred_requirements_present": bool(row["deferred_phase8_requirements"]),
        },
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    route = load_json(ITERATION_3_OUTPUT)
    response = load_json(ITERATION_4_OUTPUT)
    identity = load_json(ITERATION_5_OUTPUT)
    integration = load_json(ITERATION_6_OUTPUT)

    ready_contracts = [
        build_ready_contract(
            order=1,
            source_path=ITERATION_3_OUTPUT,
            artifact=route,
            row_key="route_conductance_memory_candidate",
            contract_label="route_conductance_memory",
        ),
        build_ready_contract(
            order=2,
            source_path=ITERATION_4_OUTPUT,
            artifact=response,
            row_key="response_magnitude_candidate",
            contract_label="bounded_envelope_gated_response_magnitude",
        ),
    ]
    deferred_blockers = [
        build_deferred_blocker(
            order=1,
            source_path=ITERATION_5_OUTPUT,
            artifact=identity,
            row_key="identity_acceptance_boundary",
            blocker_label="identity_acceptance_theory_boundary",
        ),
        build_deferred_blocker(
            order=2,
            source_path=ITERATION_6_OUTPUT,
            artifact=integration,
            row_key="agentic_like_integration_boundary",
            blocker_label="native_agentic_like_integration_meta_gap",
        ),
    ]
    phase8_ready_contract_names = [
        contract["native_policy_name"] for contract in ready_contracts
    ]
    deferred_policy_names = [
        blocker["native_policy_name"] for blocker in deferred_blockers
    ]
    no_implementation_checks = {
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags_false": all(
            contract["native_support_opened"] is False for contract in ready_contracts
        )
        and all(blocker["native_support_opened"] is False for blocker in deferred_blockers),
        "phase8_opened": False,
        "phase8_opened_false": all(
            contract["phase8_opened"] is False for contract in ready_contracts
        )
        and all(blocker["phase8_opened"] is False for blocker in deferred_blockers),
        "phase8_implementation_files_changed": False,
    }
    controls_summary = {
        "fail_closed_controls": sorted(
            {
                control
                for item in ready_contracts + deferred_blockers
                for control in item["negative_controls"]
            }
        ),
        "claim_boundary_controls": {
            "native_absorption_candidate_is_native_support": False,
            "phase8_ready_is_phase8_implementation": False,
            "route_conductance_memory_is_intention": False,
            "response_magnitude_policy_is_goal_ownership": False,
            "identity_validator_candidate_is_identity_acceptance": False,
            "component_nat4_candidate_is_integration_meta_policy": False,
            "agentic_like_integration_is_agency": False,
        },
    }
    telemetry_summary = {
        "primary_native_namespace_required_if_phase8_opens": "src/pygrc/telemetry",
        "default_off_required": True,
        "ready_contract_telemetry_requirements": {
            contract["native_policy_name"]: contract["telemetry_requirements"]
            for contract in ready_contracts
        },
        "deferred_blocker_telemetry_requirements": {
            blocker["native_policy_name"]: blocker["telemetry_requirements"]
            for blocker in deferred_blockers
        },
    }
    test_gate_summary = {
        "ready_contract_test_gates": {
            contract["native_policy_name"]: contract["compatibility_tests"]
            for contract in ready_contracts
        },
        "deferred_blocker_test_gates": {
            blocker["native_policy_name"]: blocker["compatibility_tests"]
            for blocker in deferred_blockers
        },
    }
    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(ITERATION_3_OUTPUT): source_artifact(ITERATION_3_OUTPUT, route),
        rel(ITERATION_4_OUTPUT): source_artifact(ITERATION_4_OUTPUT, response),
        rel(ITERATION_5_OUTPUT): source_artifact(ITERATION_5_OUTPUT, identity),
        rel(ITERATION_6_OUTPUT): source_artifact(ITERATION_6_OUTPUT, integration),
    }
    source_reports = {
        rel(ITERATION_1_REPORT): source_report(ITERATION_1_REPORT),
        rel(ITERATION_2_REPORT): source_report(ITERATION_2_REPORT),
        rel(ITERATION_3_REPORT): source_report(ITERATION_3_REPORT),
        rel(ITERATION_4_REPORT): source_report(ITERATION_4_REPORT),
        rel(ITERATION_5_REPORT): source_report(ITERATION_5_REPORT),
        rel(ITERATION_6_REPORT): source_report(ITERATION_6_REPORT),
    }
    checks = {
        "exactly_two_phase8_ready_contracts": len(ready_contracts) == 2,
        "ready_contracts_are_route_and_response": phase8_ready_contract_names
        == [
            "native_route_conductance_memory_policy",
            "native_response_magnitude_policy",
        ],
        "all_ready_contracts_nat4": all(
            contract["nat_level"] == "NAT4" for contract in ready_contracts
        ),
        "all_ready_contracts_phase8_ready": all(
            contract["phase8_ready"] is True for contract in ready_contracts
        ),
        "all_ready_contracts_have_controls_telemetry_tests": all(
            contract["negative_controls"]
            and contract["telemetry_requirements"]
            and contract["compatibility_tests"]
            for contract in ready_contracts
        ),
        "identity_and_integration_deferred": deferred_policy_names
        == [
            "native_identity_acceptance_validator",
            "native_agentic_like_integration_policy",
        ],
        "all_deferred_rows_nat2": all(
            blocker["nat_level"] == "NAT2" for blocker in deferred_blockers
        ),
        "all_deferred_rows_phase8_ready_false": all(
            blocker["phase8_ready"] is False for blocker in deferred_blockers
        ),
        "all_deferred_rows_have_blockers_and_rationale": all(
            blocker["missing_gates"] and blocker["deferred_phase8_requirements"]
            for blocker in deferred_blockers
        ),
        "integration_required_future_records_explicit": bool(
            deferred_blockers[1]["required_future_policy_records"]
        ),
        "src_diff_empty": no_implementation_checks["src_diff_empty"],
        "native_supported_flags_false": no_implementation_checks[
            "native_supported_flags_false"
        ],
        "phase8_opened_false": no_implementation_checks["phase8_opened_false"],
        "claim_boundary_controls_present": bool(
            controls_summary["claim_boundary_controls"]
        ),
        "source_file_sha256_all_present": all(
            artifact["sha256"] for artifact in source_artifacts.values()
        ),
    }
    output = {
        "experiment": "N12",
        "iteration": 7,
        "purpose": "phase8_readiness_package_no_implementation",
        "schema": "n12_phase8_readiness_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "matrix_result": {
            "phase8_ready_contract_count": len(ready_contracts),
            "phase8_ready_contracts": phase8_ready_contract_names,
            "deferred_blocker_count": len(deferred_blockers),
            "deferred_blockers": deferred_policy_names,
            "src_diff_empty": no_implementation_checks["src_diff_empty"],
            "native_supported_flags": False,
            "phase8_opened": False,
            "phase8_implementation_opened": False,
            "supported_interpretation": (
                "Only route conductance memory and bounded/envelope-gated "
                "response magnitude are Phase 8-ready contracts. Identity "
                "acceptance and native agentic-like integration remain blocked."
            ),
        },
        "phase8_ready_contracts": ready_contracts,
        "deferred_blockers": deferred_blockers,
        "controls_summary": controls_summary,
        "telemetry_summary": telemetry_summary,
        "test_gate_summary": test_gate_summary,
        "no_implementation_checks": no_implementation_checks,
        "checks": checks,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N12 Iteration 7 Phase 8 Readiness Matrix",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        "phase8_ready_contract_count = "
        f"{output['matrix_result']['phase8_ready_contract_count']}",
        "deferred_blocker_count = "
        f"{output['matrix_result']['deferred_blocker_count']}",
        f"src_diff_empty = {str(output['matrix_result']['src_diff_empty']).lower()}",
        "native_supported_flags = false",
        "phase8_opened = false",
        "phase8_implementation_opened = false",
        "```",
        "",
        "Iteration 7 produces the Phase 8 readiness package without opening Phase",
        "8. Only route conductance memory and bounded/envelope-gated response",
        "magnitude are Phase 8-ready contracts. Identity acceptance and native",
        "agentic-like integration remain blocked/deferred rows.",
        "",
        "The JSON artifact is the source of truth for the full readiness matrix,",
        "source artifacts, digests, controls, telemetry requirements, and test",
        "gates.",
        "",
        "## Phase 8-Ready Contracts",
        "",
        "| Native policy | NAT | Source | Controls | Telemetry | Tests |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for contract in output["phase8_ready_contracts"]:
        lines.append(
            "| "
            f"`{contract['native_policy_name']}` | "
            f"`{contract['nat_level']}` | "
            f"`{contract['source_artifact']}` | "
            f"{len(contract['negative_controls'])} | "
            f"{len(contract['telemetry_requirements'])} | "
            f"{len(contract['compatibility_tests'])} |"
        )
    lines.extend(
        [
            "",
            "## Deferred Blockers",
            "",
            "| Native policy | NAT | Reason | Missing gates | Future records |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for blocker in output["deferred_blockers"]:
        lines.append(
            "| "
            f"`{blocker['native_policy_name']}` | "
            f"`{blocker['nat_level']}` | "
            f"{blocker['blocker_label']} | "
            f"{len(blocker['missing_gates'])} | "
            f"{len(blocker['required_future_policy_records'])} |"
        )
    lines.extend(
        [
            "",
            "Future policy records listed for deferred rows are required before future",
            "Phase 8 entry. They are not native support records opened by N12.",
            "",
            "## No-Implementation Checks",
            "",
            "```json",
            json.dumps(output["no_implementation_checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Controls Summary",
            "",
            "```json",
            json.dumps(output["controls_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Telemetry Summary",
            "",
            "```json",
            json.dumps(output["telemetry_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Test Gate Summary",
            "",
            "```json",
            json.dumps(output["test_gate_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "Phase 8 readiness != Phase 8 implementation",
            "native absorption candidate != native support",
            "route conductance memory != intention",
            "response magnitude policy != goal ownership",
            "identity validator candidate != identity acceptance",
            "component NAT4 candidate != integration meta-policy",
            "agentic-like integration != agency",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

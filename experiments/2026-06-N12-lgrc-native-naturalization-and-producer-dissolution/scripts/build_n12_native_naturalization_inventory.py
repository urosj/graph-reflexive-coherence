#!/usr/bin/env python3
"""Build N12 Iteration 1 native naturalization inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
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

N11_EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
N10_EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"

N11_I11_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)
N11_I11_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
)
N11_I12_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_12_final_closeout_and_handoff.json"
)
N11_I12_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_12_final_closeout_and_handoff.md"
)
N11_FINAL_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_final_interpretation_and_roadmap_significance.md"
)
N10_I13_OUTPUT = (
    N10_EXPERIMENT / "outputs" / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
)
N10_I14_OUTPUT = (
    N10_EXPERIMENT / "outputs" / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
N10_I15_OUTPUT = (
    N10_EXPERIMENT / "outputs" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
)

N12_HANDOFF = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesHandoff.md"
N12_ROADMAP = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesRoadmap.md"
N05_N11_ROADMAP = ROOT / "experiments" / "N05-N11-LGRC-AgenticLikeFoundationRoadmap.md"

OUTPUT_PATH = OUTPUTS / "n12_native_naturalization_inventory.json"
REPORT_PATH = REPORTS / "n12_native_naturalization_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_native_naturalization_inventory.py"
)

PROVISIONAL_ROW_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "mechanism_name",
    "mechanism_role",
    "producer_decision_fields",
    "bookkeeping_fields",
    "runtime_visible_surfaces",
    "budget_surfaces",
    "native_gap",
    "provisional_primary_disposition",
    "provisional_nat_level",
    "provisional_phase8_ready",
    "claim_ceiling",
    "blocked_claims",
    "missing_gates",
    "non_rc_quantity_audit",
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}


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


def index_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "row_digest"})


def unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def canonical_claim(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def unique_sorted_claims(values: list[str]) -> list[str]:
    return sorted({canonical_claim(value) for value in values})


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def contract_bundle(
    gap_row: dict[str, Any], contract_rows: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    contracts = [
        contract_rows[row_id]
        for row_id in gap_row.get("source_contract_rows", [])
        if row_id in contract_rows
    ]
    return {
        "source_contract_rows": [row["row_id"] for row in contracts],
        "covered_policy_records": [
            record
            for row in contracts
            for record in row.get("covered_policy_records", [])
        ],
        "runtime_visible_inputs": unique_sorted(
            [
                item
                for row in contracts
                for item in row.get("runtime_visible_inputs", [])
            ]
        ),
        "budget_surfaces": unique_sorted(
            [item for row in contracts for item in row.get("budget_surfaces", [])]
        ),
        "negative_controls": unique_sorted(
            [item for row in contracts for item in row.get("negative_controls", [])]
        ),
        "artifact_replay_requirements": unique_sorted(
            [
                item
                for row in contracts
                for item in row.get("artifact_replay_requirements", [])
            ]
        ),
        "claim_boundary_controls": unique_sorted(
            [
                item
                for row in contracts
                for item in row.get("claim_boundary_controls", [])
            ]
        ),
        "ordering_requirements": unique_sorted(
            [item for row in contracts for item in row.get("ordering_requirements", [])]
        ),
        "stale_context_blockers": unique_sorted(
            [
                item
                for row in contracts
                for item in row.get("stale_context_blockers", [])
            ]
        ),
        "phase_8_readiness": unique_sorted(
            [
                row.get("phase_8_readiness")
                for row in contracts
                if row.get("phase_8_readiness")
            ]
        ),
    }


def disposition_for(row_id: str) -> tuple[str, str, bool, list[str], list[str]]:
    if row_id == "n11_i11_gap_01_route_context_contract_hardening":
        return (
            "scaffold",
            "NAT2",
            False,
            ["native_supported_selection_only", "schema_hardening_if_scope_extends"],
            [
                "future_scope_beyond_selection_only_not_opened",
                "route_execution_context_not_requested",
            ],
        )
    if row_id == "n11_i11_gap_02_route_conductance_memory_policy":
        return (
            "native_absorption_candidate",
            "NAT3",
            False,
            ["producer_mediated", "native_policy_gap"],
            [
                "route_memory_geometry_vs_bookkeeping_split_missing",
                "route_memory_non_rc_quantity_audit_pending",
                "route_memory_mutation_boundary_missing",
                "route_memory_telemetry_requirements_missing",
                "route_memory_compatibility_tests_missing",
            ],
        )
    if row_id == "n11_i11_gap_03_response_magnitude_policy":
        return (
            "native_absorption_candidate",
            "NAT3",
            False,
            ["producer_mediated", "native_policy_gap"],
            [
                "response_magnitude_non_rc_quantity_audit_pending",
                "response_trend_stability_fields_missing",
                "response_magnitude_mutation_boundary_missing",
                "response_magnitude_telemetry_requirements_missing",
                "response_magnitude_compatibility_tests_missing",
            ],
        )
    if row_id == "n11_i11_gap_04_identity_support_validator":
        return (
            "theory_sensitive_blocker",
            "NAT2",
            False,
            ["validator_local", "native_policy_gap"],
            [
                "identity_acceptance_semantics_not_formalized",
                "support_survival_not_identity_acceptance",
                "runtime_acceptance_validator_missing",
            ],
        )
    if row_id == "n11_i11_gap_05_artifact_replay_and_source_continuity":
        return (
            "scaffold",
            "NAT2",
            False,
            ["validator_local", "cross_cutting_contract", "theory_sensitive_meta_gap"],
            [
                "component_native_policies_missing",
                "native_integration_meta_policy_not_one_small_mechanism",
                "fully_native_integration_replay_not_available",
            ],
        )
    raise KeyError(f"Unmapped N11 gap row {row_id}")


def non_rc_audit_for(row_id: str) -> dict[str, Any]:
    common = {
        "field_required": True,
        "extra_unaccounted_quantity_allowed": False,
        "nat4_blocker_if_extra_quantity_required": (
            "unaccounted_non_rc_quantity_required"
        ),
    }
    if row_id == "n11_i11_gap_02_route_conductance_memory_policy":
        return {
            **common,
            "audit_status": "pending_iteration_3_candidate_audit",
            "candidate_specific_questions": {
                "is_memory_coherence_geometry_or_flux_effect": "unresolved",
                "is_memory_only_producer_bookkeeping": "source_indicates_artifact_producer_policy_so_far",
                "does_decay_or_relaxation_conserve_accounted_quantity": "unresolved",
                "does_candidate_require_new_scalar_outside_rc_accounting": "unresolved",
            },
        }
    if row_id == "n11_i11_gap_03_response_magnitude_policy":
        return {
            **common,
            "audit_status": "pending_iteration_4_candidate_audit",
            "candidate_specific_questions": {
                "is_proxy_measurement_derived_observable_or_new_state": "unresolved",
                "is_target_band_exogenous_or_runtime_visible_policy": "unresolved",
                "is_response_gain_serialized_and_replayable": "unresolved",
                "does_correction_debit_node_plus_packet_budget": "unresolved",
                "does_response_sizing_require_hidden_optimization_or_external_controller_state": "unresolved",
            },
        }
    return {
        **common,
        "audit_status": "not_phase8_candidate_in_iteration_1",
        "candidate_specific_questions": {},
    }


def mechanism_role(row: dict[str, Any]) -> str:
    return str(row.get("n11_role") or row.get("classification") or "source_gap_row")


def build_inventory_rows(
    n11_i11: dict[str, Any],
    n11_i12: dict[str, Any],
    n10_i13: dict[str, Any],
    n10_i14: dict[str, Any],
) -> list[dict[str, Any]]:
    gap_rows = n11_i11["native_generalization_gap_rows"]
    n10_gap_rows = index_by(n10_i13["native_policy_gap_inventory"], "row_id")
    contract_rows = index_by(n10_i14["native_contract_requirements"], "row_id")
    rows: list[dict[str, Any]] = []

    for index, gap_row in enumerate(gap_rows, start=1):
        disposition, nat_level, phase8_ready, secondary_tags, missing_gates = (
            disposition_for(gap_row["row_id"])
        )
        bundle = contract_bundle(gap_row, contract_rows)
        source_gap_rows = [
            n10_gap_rows[row_id]
            for row_id in gap_row.get("source_gap_rows", [])
            if row_id in n10_gap_rows
        ]
        blocked_claims = unique_sorted_claims(
            list(gap_row.get("claims_invalid_until_dissolved", []))
            + list(n11_i12["final_blocked_claims"])
        )
        row = {
            "row_id": f"n12_i1_inventory_{index:02d}_{gap_row['row_id']}",
            "source_experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
            "source_iteration": 11,
            "source_artifact": rel(N11_I11_OUTPUT),
            "source_report": rel(N11_I11_REPORT),
            "source_sha256": digest_file(N11_I11_OUTPUT),
            "source_report_sha256": digest_file(N11_I11_REPORT),
            "mechanism_name": gap_row["component"],
            "mechanism_role": mechanism_role(gap_row),
            "producer_decision_fields": gap_row.get("producer_decisions_essential", []),
            "bookkeeping_fields": gap_row.get("bookkeeping_fields", []),
            "runtime_visible_surfaces": gap_row.get(
                "runtime_visible_surfaces_needed", []
            ),
            "budget_surfaces": bundle["budget_surfaces"],
            "native_gap": gap_row.get("native_gap"),
            "provisional_primary_disposition": disposition,
            "provisional_nat_level": nat_level,
            "provisional_phase8_ready": phase8_ready,
            "claim_ceiling": n11_i12["final_claim_ceiling"],
            "blocked_claims": blocked_claims,
            "missing_gates": missing_gates,
            "non_rc_quantity_audit": non_rc_audit_for(gap_row["row_id"]),
            "secondary_tags": secondary_tags,
            "source_gap_rows": gap_row.get("source_gap_rows", []),
            "source_gap_row_summaries": [
                {
                    "row_id": row["row_id"],
                    "component": row["component"],
                    "native_policy_gap": row.get("native_policy_gap"),
                    "classification": row["classification"],
                    "overread_blocker": row.get("overread_blocker"),
                }
                for row in source_gap_rows
            ],
            "source_contract_rows": bundle["source_contract_rows"],
            "covered_policy_records": bundle["covered_policy_records"],
            "contract_runtime_visible_inputs": bundle["runtime_visible_inputs"],
            "negative_controls": bundle["negative_controls"],
            "artifact_replay_requirements": bundle["artifact_replay_requirements"],
            "claim_boundary_controls": bundle["claim_boundary_controls"],
            "ordering_requirements": bundle["ordering_requirements"],
            "stale_context_blockers": bundle["stale_context_blockers"],
            "thresholds_to_serialize": gap_row.get("thresholds_to_serialize", []),
            "source_row_digest": gap_row.get("row_digest"),
            "n11_native_supported": gap_row.get("native_supported"),
            "n11_native_support_scope": gap_row.get("native_support_scope"),
            "phase8_readiness_source": gap_row.get("phase8_readiness"),
            "phase8_decision_source": gap_row.get("phase8_decision"),
            "phase8_order_source": gap_row.get("phase8_order"),
            "claim_flags_forced_false": {
                key: gap_row["claim_flags"][key]
                for key in CLAIM_FLAGS_FORCED_FALSE
                if key in gap_row["claim_flags"]
            },
            "mutation_boundary": {
                "required_for_nat4": True,
                "status": "not_evaluated_in_iteration_1",
                "producer_or_policy_may_schedule_only": None,
                "step_or_topology_event_owns_state_mutation": None,
            },
        }
        row["row_digest"] = row_digest(row)
        rows.append(row)

    return rows


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        "all_rows_have_provisional_shape": all(
            all(field in row for field in PROVISIONAL_ROW_FIELDS) for row in rows
        ),
        "all_rows_have_non_rc_quantity_audit": all(
            isinstance(row["non_rc_quantity_audit"], dict) for row in rows
        ),
        "all_rows_have_single_primary_disposition": all(
            row["provisional_primary_disposition"]
            in {
                "scaffold",
                "native_absorption_candidate",
                "theory_sensitive_blocker",
                "blocked_missing_source_or_gate",
            }
            for row in rows
        ),
        "phase8_ready_derived_from_nat4": all(
            row["provisional_phase8_ready"] == (row["provisional_nat_level"] == "NAT4")
            for row in rows
        ),
        "no_iteration_1_nat4_claims": all(
            row["provisional_nat_level"] != "NAT4" for row in rows
        ),
        "claim_flags_forced_false": all(
            all_claim_flags_false(row["claim_flags_forced_false"]) for row in rows
        ),
        "n12_native_support_not_opened": all(
            row["claim_flags_forced_false"].get("native_support_opened") is False
            for row in rows
        ),
        "src_clean": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    n11_i11 = load_json(N11_I11_OUTPUT)
    n11_i12 = load_json(N11_I12_OUTPUT)
    n10_i13 = load_json(N10_I13_OUTPUT)
    n10_i14 = load_json(N10_I14_OUTPUT)
    n10_i15 = load_json(N10_I15_OUTPUT)

    source_artifacts = {
        "n12_handoff": source_artifact(N12_HANDOFF),
        "n12_roadmap": source_artifact(N12_ROADMAP),
        "n05_n11_roadmap": source_artifact(N05_N11_ROADMAP),
        "n11_iteration_11_native_gap_output": source_artifact(
            N11_I11_OUTPUT, n11_i11
        ),
        "n11_iteration_11_native_gap_report": source_artifact(N11_I11_REPORT),
        "n11_iteration_12_closeout_output": source_artifact(
            N11_I12_OUTPUT, n11_i12
        ),
        "n11_iteration_12_closeout_report": source_artifact(N11_I12_REPORT),
        "n11_final_interpretation_report": source_artifact(N11_FINAL_REPORT),
        "n10_iteration_13_gap_inventory": source_artifact(N10_I13_OUTPUT, n10_i13),
        "n10_iteration_14_contract_requirements": source_artifact(
            N10_I14_OUTPUT, n10_i14
        ),
        "n10_iteration_15_closeout": source_artifact(N10_I15_OUTPUT, n10_i15),
    }
    rows = build_inventory_rows(n11_i11, n11_i12, n10_i13, n10_i14)
    checks = {
        "n11_iteration_11_passed": n11_i11["status"] == "passed",
        "n11_iteration_12_passed": n11_i12["status"] == "passed",
        "n10_iteration_13_passed": n10_i13["status"] == "passed",
        "n10_iteration_14_passed": n10_i14["status"] == "passed",
        "n10_iteration_15_passed": n10_i15["status"] == "passed",
        "n11_gali7_artifact_only_preserved": n11_i12["final_supported_gali_ceiling"]
        == "GALI7",
        "n11_fully_native_false": n11_i12["result_mediation"]["fully_native"]
        is False,
        "expected_seed_row_count": len(rows) == 5,
        **validate_rows(rows),
    }
    output: dict[str, Any] = {
        "schema": "n12_native_naturalization_inventory_v1",
        "experiment": "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution",
        "iteration": 1,
        "purpose": "baseline_and_mechanism_inventory",
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": source_artifacts,
        "source_state": {
            "n11_final_supported_gali_ceiling": n11_i12[
                "final_supported_gali_ceiling"
            ],
            "n11_final_claim_ceiling": n11_i12["final_claim_ceiling"],
            "artifact_only": n11_i12["result_mediation"]["artifact_only"],
            "fully_native": n11_i12["result_mediation"]["fully_native"],
            "native_blocker_set": n11_i12["native_blocker_set"],
            "inherited_native_route_arbitration_scope": (
                "selection_only_route_arbitration_context"
            ),
            "n12_native_support_opened": False,
        },
        "provisional_row_shape": PROVISIONAL_ROW_FIELDS,
        "primary_disposition_values": [
            "scaffold",
            "native_absorption_candidate",
            "theory_sensitive_blocker",
            "blocked_missing_source_or_gate",
        ],
        "n12_inventory_rows": rows,
        "classification_summary": {
            "row_count": len(rows),
            "by_primary_disposition": {
                disposition: sum(
                    1
                    for row in rows
                    if row["provisional_primary_disposition"] == disposition
                )
                for disposition in [
                    "scaffold",
                    "native_absorption_candidate",
                    "theory_sensitive_blocker",
                    "blocked_missing_source_or_gate",
                ]
            },
            "by_provisional_nat_level": {
                nat_level: sum(
                    1 for row in rows if row["provisional_nat_level"] == nat_level
                )
                for nat_level in ["NAT0", "NAT1", "NAT2", "NAT3", "NAT4", "NAT5", "NAT6"]
            },
            "phase8_ready_rows": [
                row["row_id"] for row in rows if row["provisional_phase8_ready"]
            ],
            "nat3_native_absorption_candidates": [
                row["row_id"]
                for row in rows
                if row["provisional_primary_disposition"]
                == "native_absorption_candidate"
            ],
        },
        "claim_boundary": {
            "native_absorption_candidate_is_native_support": False,
            "native_support_is_agency": False,
            "route_conductance_memory_is_intention": False,
            "response_magnitude_policy_is_goal_ownership": False,
            "identity_validator_candidate_is_identity_acceptance": False,
            "agentic_like_integration_is_agency": False,
            "inherited_route_arbitration_support_scope": (
                "selection_only_route_arbitration_context"
            ),
            "n12_opened_new_native_support": False,
        },
        "checks": checks,
        "acceptance": {
            "status": "passed" if all(checks.values()) else "failed",
            "achieved": all(checks.values()),
            "acceptance_statement": (
                "Iteration 1 passes if every mechanism row is source-backed "
                "and N12 records the inherited native gaps using the "
                "provisional row shape, with non-RC audits and without "
                "promoting them into native support."
            ),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_json(output: dict[str, Any]) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# N12 Native Naturalization Inventory",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        "Iteration 1 builds the source-backed mechanism inventory for N12.",
        "It consumes N11's native gap and closeout artifacts and preserves the",
        "artifact-only GALI7 boundary without opening Phase 8.",
        "",
        "```text",
        f"final_supported_gali_ceiling = {output['source_state']['n11_final_supported_gali_ceiling']}",
        f"final_claim_ceiling = {output['source_state']['n11_final_claim_ceiling']}",
        f"artifact_only = {output['source_state']['artifact_only']}",
        f"fully_native = {output['source_state']['fully_native']}",
        f"phase8_ready_rows = {len(output['classification_summary']['phase8_ready_rows'])}",
        "```",
        "",
        "## Provisional Rows",
        "",
        "| Row | Mechanism | Provisional disposition | NAT | Native gap |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in output["n12_inventory_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"{row['mechanism_name']} | "
            f"`{row['provisional_primary_disposition']}` | "
            f"`{row['provisional_nat_level']}` | "
            f"`{row['native_gap']}` |"
        )
    lines.extend(
        [
            "",
            "## NAT Summary",
            "",
            "```json",
            json.dumps(output["classification_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Missing Gates",
            "",
        ]
    )
    for row in output["n12_inventory_rows"]:
        lines.extend(
            [
                f"### {row['row_id']}",
                "",
                "```json",
                json.dumps(row["missing_gates"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Non-RC Quantity Audit Status",
            "",
        ]
    )
    for row in output["n12_inventory_rows"]:
        lines.extend(
            [
                f"### {row['row_id']}",
                "",
                "```json",
                json.dumps(row["non_rc_quantity_audit"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(output)
    write_report(output)


if __name__ == "__main__":
    main()

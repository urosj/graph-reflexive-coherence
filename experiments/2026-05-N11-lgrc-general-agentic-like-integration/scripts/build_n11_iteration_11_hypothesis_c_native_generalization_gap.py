#!/usr/bin/env python3
"""Build N11 Iteration 11 native generalization gap inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N11_I10_PATH = OUTPUTS / "n11_iteration_10_hypothesis_ab_closeout.json"
N10_I13_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "outputs"
    / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
)
N10_I14_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "outputs"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
N10_I15_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "outputs"
    / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
)

OUTPUT_PATH = OUTPUTS / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
REPORT_PATH = REPORTS / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "build_n11_iteration_11_hypothesis_c_native_generalization_gap.py"
)

CLAIM_FLAGS_FALSE = {
    "agency_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "intention_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
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


def source_artifact(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": artifact.get("status"),
        "output_digest": artifact.get("output_digest"),
    }


def index_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def gap_row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "row_digest"})


def build_gap_rows(
    n10_i13: dict[str, Any],
    n10_i14: dict[str, Any],
    n10_i15: dict[str, Any],
) -> list[dict[str, Any]]:
    gap_rows = index_by(n10_i13["native_policy_gap_inventory"], "row_id")
    contract_rows = index_by(n10_i14["native_contract_requirements"], "row_id")
    absorption_order = n10_i15["phase8_native_absorption_handoff"][
        "native_absorption_order"
    ]

    def phase_for(contract_row_id: str) -> dict[str, Any]:
        for item in absorption_order:
            if contract_row_id in item["contract_rows"]:
                return item
        return {
            "order": None,
            "phase": "not_ordered",
            "reason": "No explicit N10 absorption order row.",
        }

    rows = [
        {
            "row_id": "n11_i11_gap_01_route_context_contract_hardening",
            "component": "route_context_and_native_route_arbitration_boundary",
            "n11_role": "GALI2_context_transfer_input",
            "classification": "native_supported_selection_only_with_schema_hardening_gap",
            "artifact_local": False,
            "producer_mediated": False,
            "validator_local": False,
            "native_supported": True,
            "native_support_scope": "selection_only_route_arbitration_context",
            "native_gap": "native_route_context_contract_hardening_if_scope_extends",
            "source_gap_rows": ["n10_c_gap_01_route_context_selection_boundary"],
            "source_contract_rows": ["n10_i14_contract_01_route_context"],
            "phase8_readiness": contract_rows[
                "n10_i14_contract_01_route_context"
            ]["phase_8_readiness"],
            "phase8_order": phase_for("n10_i14_contract_01_route_context"),
            "producer_decisions_essential": [],
            "bookkeeping_fields": [
                "route_context_source_digest",
                "selected_route_digest",
                "selection_only_scope_marker",
            ],
            "thresholds_to_serialize": [],
            "runtime_visible_surfaces_needed": [
                "native_route_context_record",
                "arbitration_record_digest",
                "stale_route_context_blocker",
            ],
            "claims_invalid_until_dissolved": [
                "semantic_choice",
                "agency",
                "semantic_goal_ownership",
            ],
            "phase8_decision": "schema_hardening_only_unless_future_scope_exceeds_selection",
        },
        {
            "row_id": "n11_i11_gap_02_route_conductance_memory_policy",
            "component": "N08_memory_trail_affordance_consumed_by_N10_N11",
            "n11_role": "memory_shaped_route_affordance_under_GALI7",
            "classification": "producer_mediated_artifact_local_concrete_native_gap",
            "artifact_local": True,
            "producer_mediated": True,
            "validator_local": False,
            "native_supported": False,
            "native_support_scope": "not_native",
            "native_gap": "native_route_conductance_memory_policy_missing",
            "source_gap_rows": [
                "n10_c_gap_02_serialized_memory_policy",
                "n10_c_gap_03_native_geometry_trail_design_direction",
            ],
            "source_contract_rows": ["n10_i14_contract_02_route_conductance_memory"],
            "phase8_readiness": contract_rows[
                "n10_i14_contract_02_route_conductance_memory"
            ]["phase_8_readiness"],
            "phase8_order": phase_for("n10_i14_contract_02_route_conductance_memory"),
            "producer_decisions_essential": [
                "route-use-linked memory update",
                "memory relaxation/decay rule",
                "route-scope digest selection",
            ],
            "bookkeeping_fields": [
                "memory_budget_surface",
                "memory_policy_id",
                "route_scope_digest",
            ],
            "thresholds_to_serialize": [
                "memory update magnitude",
                "relaxation schedule",
                "conductance eligibility threshold",
            ],
            "runtime_visible_surfaces_needed": [
                "native_route_conductance_memory_policy_record",
                "native_geometry_conductance_update_policy_record",
                "route_conductance_memory_budget_surface",
            ],
            "claims_invalid_until_dissolved": [
                "ACO-like behavior",
                "ant-colony behavior",
                "native memory trail support",
                "agency",
            ],
            "phase8_decision": "concrete_phase8_candidate_after_cross_cutting_budget_contract",
        },
        {
            "row_id": "n11_i11_gap_03_response_magnitude_policy",
            "component": "N09_goal_proxy_regulation_and_response_sizing",
            "n11_role": "GALI3_proxy_transfer_and_GALI7_regulation_subchain",
            "classification": "producer_mediated_artifact_local_concrete_native_gap",
            "artifact_local": True,
            "producer_mediated": True,
            "validator_local": False,
            "native_supported": False,
            "native_support_scope": "not_native",
            "native_gap": "native_response_magnitude_policy_missing_for_unbounded_perturbations",
            "source_gap_rows": [
                "n10_c_gap_04_goal_proxy_regulation_artifact_policy",
                "n10_c_gap_05_response_magnitude_policy",
            ],
            "source_contract_rows": ["n10_i14_contract_03_goal_proxy_regulation"],
            "phase8_readiness": contract_rows[
                "n10_i14_contract_03_goal_proxy_regulation"
            ]["phase_8_readiness"],
            "phase8_order": phase_for("n10_i14_contract_03_goal_proxy_regulation"),
            "producer_decisions_essential": [
                "proxy error measurement",
                "bounded correction magnitude selection",
                "response packet scheduling",
            ],
            "bookkeeping_fields": [
                "proxy_budget_surface",
                "target_band_digest",
                "response_window_id",
            ],
            "thresholds_to_serialize": [
                "target band",
                "response gain",
                "max correction per window",
                "out-of-envelope blocker threshold",
            ],
            "runtime_visible_surfaces_needed": [
                "native_goal_proxy_regulation_policy_record",
                "native_response_magnitude_policy_record",
                "proxy measurement surface digest",
            ],
            "claims_invalid_until_dissolved": [
                "semantic goal ownership",
                "semantic goal understanding",
                "intention",
                "agency",
            ],
            "phase8_decision": "concrete_phase8_candidate_after_memory_or_in_parallel",
        },
        {
            "row_id": "n11_i11_gap_04_identity_support_validator",
            "component": "N07_support_invariance_and_identity_acceptance_boundary",
            "n11_role": "GALI4_support_transfer_and_GALI7_support_gate",
            "classification": "support_evidence_theory_sensitive_native_gap",
            "artifact_local": True,
            "producer_mediated": False,
            "validator_local": True,
            "native_supported": False,
            "native_support_scope": "support_survival_only_not_identity_acceptance",
            "native_gap": "native_identity_acceptance_validator_missing",
            "source_gap_rows": ["n10_c_gap_06_identity_support_not_acceptance"],
            "source_contract_rows": ["n10_i14_contract_04_identity_support_validator"],
            "phase8_readiness": contract_rows[
                "n10_i14_contract_04_identity_support_validator"
            ]["phase_8_readiness"],
            "phase8_order": phase_for("n10_i14_contract_04_identity_support_validator"),
            "producer_decisions_essential": [],
            "bookkeeping_fields": [
                "support_state_digest",
                "restoration_history_digest",
                "support_survival_threshold",
            ],
            "thresholds_to_serialize": [
                "support survival threshold",
                "withdrawal disruption threshold",
                "restoration eligibility threshold",
            ],
            "runtime_visible_surfaces_needed": [
                "native_identity_support_validator_record",
                "lineage-current support state surface",
                "disruption/restoration history surface",
            ],
            "claims_invalid_until_dissolved": [
                "identity acceptance",
                "runtime identity acceptance",
                "RC identity collapse",
                "agency",
            ],
            "phase8_decision": "defer_until_identity_acceptance_theory_is_precise",
        },
        {
            "row_id": "n11_i11_gap_05_artifact_replay_and_source_continuity",
            "component": "artifact_only_generalization_validator",
            "n11_role": "Iteration_9_replay_validation_and_GALI7_closeout_gate",
            "classification": "validator_local_replay_contract",
            "artifact_local": True,
            "producer_mediated": False,
            "validator_local": True,
            "native_supported": False,
            "native_support_scope": "artifact_replay_only",
            "native_gap": "native_agentic_like_integration_policy_missing",
            "source_gap_rows": [
                "n10_c_gap_07_artifact_only_integration_validator",
                "n10_c_gap_08_support_sensitive_integration_gate",
                "n10_c_gap_09_budget_surfaces_and_source_continuity",
            ],
            "source_contract_rows": [
                "n10_i14_contract_05_native_integration_gate",
                "n10_i14_contract_06_budget_surface_separation",
            ],
            "phase8_readiness": "cross_cutting_contract_then_meta_gap",
            "phase8_order": {
                "budget_contract": phase_for("n10_i14_contract_06_budget_surface_separation"),
                "native_integration_gate": phase_for("n10_i14_contract_05_native_integration_gate"),
            },
            "producer_decisions_essential": [],
            "bookkeeping_fields": [
                "source_artifact_digest",
                "row_digest",
                "event_window_order",
                "budget_surface_id",
            ],
            "thresholds_to_serialize": [
                "source-current validity window",
                "budget continuity epsilon",
                "claim-promotion rejection policy",
            ],
            "runtime_visible_surfaces_needed": [
                "native_budget_surface_contract_record",
                "native_claim_boundary_contract_record",
                "native_agentic_like_integration_policy_record",
            ],
            "claims_invalid_until_dissolved": [
                "fully native agentic-like integration",
                "unrestricted agency",
                "personhood",
            ],
            "phase8_decision": "budget_contract_cross_cutting_first_meta_policy_last",
        },
    ]
    for row in rows:
        row["source_gap_digests"] = {
            row_id: gap_rows[row_id]["gap_row_digest"]
            for row_id in row["source_gap_rows"]
            if row_id in gap_rows
        }
        row["source_contract_digests"] = {
            row_id: contract_rows[row_id]["contract_row_digest"]
            for row_id in row["source_contract_rows"]
            if row_id in contract_rows
        }
        row["claim_flags"] = CLAIM_FLAGS_FALSE
        row["native_support_opened_by_iteration_11"] = False
        row["row_digest"] = gap_row_digest(row)
    return rows


def build_output() -> dict[str, Any]:
    n11_i10 = load_json(N11_I10_PATH)
    n10_i13 = load_json(N10_I13_PATH)
    n10_i14 = load_json(N10_I14_PATH)
    n10_i15 = load_json(N10_I15_PATH)
    gap_rows = build_gap_rows(n10_i13, n10_i14, n10_i15)
    phase8_ready_rows = [
        row["row_id"]
        for row in gap_rows
        if "concrete_phase8_candidate" in row["phase8_readiness"]
        or row["phase8_decision"].startswith("concrete_phase8_candidate")
    ]
    answered_questions = {
        "which_producer_decisions_were_essential": {
            row["row_id"]: row["producer_decisions_essential"]
            for row in gap_rows
            if row["producer_decisions_essential"]
        },
        "which_producer_fields_were_only_bookkeeping": {
            row["row_id"]: row["bookkeeping_fields"] for row in gap_rows
        },
        "which_thresholds_should_become_serialized_substrate_policies": {
            row["row_id"]: row["thresholds_to_serialize"] for row in gap_rows
        },
        "which_runtime_visible_surfaces_must_be_added_to_lgrc": {
            row["row_id"]: row["runtime_visible_surfaces_needed"]
            for row in gap_rows
        },
        "which_claims_remain_invalid_until_producer_logic_is_dissolved": {
            row["row_id"]: row["claims_invalid_until_dissolved"] for row in gap_rows
        },
    }
    checks = {
        "iteration_10_closeout_consumed": n11_i10["status"] == "passed",
        "n10_gap_inventory_consumed": n10_i13["status"] == "passed",
        "n10_contract_requirements_consumed": n10_i14["status"] == "passed",
        "n10_phase8_handoff_consumed": n10_i15["status"] == "passed",
        "gali7_artifact_only_ceiling_preserved": (
            n11_i10["strongest_supported_gali_level"] == "GALI7"
            and n11_i10["gali7_evidence_classification_supported"] is True
        ),
        "all_components_classified": len(gap_rows) == 5,
        "phase8_ready_candidates_identified": set(phase8_ready_rows)
        == {
            "n11_i11_gap_02_route_conductance_memory_policy",
            "n11_i11_gap_03_response_magnitude_policy",
        },
        "identity_acceptance_deferred": any(
            row["phase8_decision"] == "defer_until_identity_acceptance_theory_is_precise"
            for row in gap_rows
        ),
        "meta_policy_last": any(
            row["phase8_decision"] == "budget_contract_cross_cutting_first_meta_policy_last"
            for row in gap_rows
        ),
        "no_phase8_implementation_performed": True,
        "all_native_support_flags_false": all(
            row["native_support_opened_by_iteration_11"] is False for row in gap_rows
        ),
        "all_claim_flags_false": all(
            all(value is False for value in row["claim_flags"].values())
            for row in gap_rows
        ),
        "src_clean_for_iteration_11": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 11 passes if N11's native generalization gaps are named, "
            "scoped, and ordered without implementing them or relabeling "
            "artifact-only evidence as native support. Fully native "
            "broader/general agentic-like integration remains blocked unless a "
            "separate native implementation exists."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_11_hypothesis_c_native_generalization_gap_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 11,
        "purpose": "hypothesis_c_native_generalization_gap_inventory",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": {
            "n11_iteration_10_closeout": source_artifact(N11_I10_PATH, n11_i10),
            "n10_iteration_13_gap_inventory": source_artifact(N10_I13_PATH, n10_i13),
            "n10_iteration_14_contract_requirements": source_artifact(N10_I14_PATH, n10_i14),
            "n10_iteration_15_closeout_handoff": source_artifact(N10_I15_PATH, n10_i15),
        },
        "gali7_artifact_only_result_preserved": True,
        "native_generalization_gap_rows": gap_rows,
        "phase8_ready_candidate_rows": phase8_ready_rows,
        "phase8_not_ready_or_deferred_rows": [
            row["row_id"] for row in gap_rows if row["row_id"] not in phase8_ready_rows
        ],
        "answered_questions": answered_questions,
        "native_support_flags": {
            "fully_native_agentic_like_integration_supported": False,
            "native_agentic_like_integration_policy_supported": False,
            "native_route_conductance_memory_policy_supported": False,
            "native_response_magnitude_policy_supported": False,
            "native_identity_acceptance_validator_supported": False,
        },
        "claim_flags": CLAIM_FLAGS_FALSE,
        "interpretation": {
            "summary": (
                "N11's GALI7 result is artifact-only and source-backed. "
                "Hypothesis C identifies which parts remain producer-mediated, "
                "validator-local, or native-policy gaps before the result can be "
                "naturalized into LGRC."
            ),
            "phase8_sequence": (
                "Cross-cutting budget/replay contract first, then route "
                "conductance memory, response magnitude regulation, identity "
                "support validator hardening, optional route-context hardening, "
                "and only then the native agentic-like integration meta-policy."
            ),
        },
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "12_final_closeout_and_handoff",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 11 Hypothesis C Native Generalization Gap",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        output["interpretation"]["summary"],
        "",
        "```text",
        "gali7_artifact_only_result_preserved = true",
        "fully_native_agentic_like_integration_supported = false",
        "native_support_opened_by_iteration_11 = false",
        "```",
        "",
        "## Gap Rows",
        "",
        "```json",
        json.dumps(output["native_generalization_gap_rows"], indent=2, sort_keys=True),
        "```",
        "",
        "## Phase 8 Readiness",
        "",
        "```json",
        json.dumps(
            {
                "phase8_ready_candidate_rows": output["phase8_ready_candidate_rows"],
                "phase8_not_ready_or_deferred_rows": output[
                    "phase8_not_ready_or_deferred_rows"
                ],
                "phase8_sequence": output["interpretation"]["phase8_sequence"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Questions Answered",
        "",
        "```json",
        json.dumps(output["answered_questions"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "```json",
        json.dumps(
            {
                "claim_flags": output["claim_flags"],
                "native_support_flags": output["native_support_flags"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

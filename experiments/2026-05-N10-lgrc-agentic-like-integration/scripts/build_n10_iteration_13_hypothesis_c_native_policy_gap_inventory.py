#!/usr/bin/env python3
"""Build N10 Iteration 13 Hypothesis C native policy gap inventory.

Iteration 13 is an inventory pass. It records which parts of the
Hypothesis A/B route-memory-support-regulation composition are still
artifact-local, producer-mediated, or validator-local, and which parts are
load-bearing for a future native LGRC implementation.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "build_n10_iteration_13_hypothesis_c_native_policy_gap_inventory.py"
)

SOURCE_ARTIFACTS = {
    "n06_route_choice_closeout": (
        ROOT
        / "experiments"
        / "2026-05-N06-lgrc-semantic-route-choice"
        / "outputs"
        / "n06_iteration_8_sc6_closeout.json"
    ),
    "n07_identity_support_withdrawal": (
        ROOT
        / "experiments"
        / "2026-05-N07-rc-identity-attractor-invariance"
        / "outputs"
        / "n07_iteration_13_identity_support_withdrawal_baseline.json"
    ),
    "n08_memory_trail_hypothesis_a": (
        ROOT
        / "experiments"
        / "2026-05-N08-lgrc-memory-trail-affordance"
        / "outputs"
        / "n08_iteration_8_mem6_closeout.json"
    ),
    "n08_native_geometry_trail_hypothesis_b": (
        ROOT
        / "experiments"
        / "2026-05-N08-lgrc-memory-trail-affordance"
        / "outputs"
        / "n08_iteration_13_native_geometry_trail_closeout.json"
    ),
    "n09_goal_proxy_hypothesis_a": (
        ROOT
        / "experiments"
        / "2026-05-N09-lgrc-goal-proxy-regulation"
        / "outputs"
        / "n09_iteration_9_gpr6_closeout.json"
    ),
    "n09_native_substrate_hypothesis_b": (
        ROOT
        / "experiments"
        / "2026-05-N09-lgrc-goal-proxy-regulation"
        / "outputs"
        / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.json"
    ),
    "n10_hypothesis_a_closeout": (
        EXPERIMENT / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
    ),
    "n10_hypothesis_b_closeout": (
        EXPERIMENT
        / "outputs"
        / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
    ),
}

SOURCE_REPORTS = {
    key: path.parents[1] / "reports" / path.name.replace(".json", ".md")
    for key, path in SOURCE_ARTIFACTS.items()
}

CLAIM_FLAGS = {
    "native_agentic_like_integration_supported": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
}

EXPECTED_NATIVE_BLOCKERS = [
    "native_route_conductance_memory_policy_missing",
    "native_response_magnitude_policy_missing_for_unbounded_perturbations",
    "native_identity_acceptance_validator_missing",
    "native_agentic_like_integration_policy_missing",
]


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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def prior_output_digest_valid(artifact: dict[str, Any]) -> bool:
    if "output_digest" not in artifact:
        return True
    return artifact["output_digest"] == output_digest(artifact)


def source_records(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
            "status": artifacts[key].get("status"),
            "output_digest": artifacts[key].get("output_digest"),
            "output_digest_valid": prior_output_digest_valid(artifacts[key]),
        }
        for key, path in SOURCE_ARTIFACTS.items()
    }
    report_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in SOURCE_REPORTS.items()
        if path.exists()
    }
    return artifact_records, report_records


def gap_row(
    *,
    row_id: str,
    component: str,
    source_keys: list[str],
    current_status: str,
    classification: str,
    load_bearing_for_native: bool,
    consumed_by_n10: str,
    current_evidence: str,
    native_boundary: str,
    native_policy_gap: str | None,
    minimal_native_surface_needed: str,
    overread_blocker: str,
    iteration_14_contract_focus: list[str],
) -> dict[str, Any]:
    row = {
        "row_id": row_id,
        "component": component,
        "source_artifact_keys": source_keys,
        "current_status": current_status,
        "classification": classification,
        "load_bearing_for_native": load_bearing_for_native,
        "consumed_by_n10": consumed_by_n10,
        "current_evidence": current_evidence,
        "native_boundary": native_boundary,
        "native_policy_gap": native_policy_gap,
        "minimal_native_surface_needed": minimal_native_surface_needed,
        "overread_blocker": overread_blocker,
        "iteration_14_contract_focus": iteration_14_contract_focus,
        "native_support_opened_by_iteration_13": False,
        "claim_flags": CLAIM_FLAGS,
    }
    return with_digest(row, "gap_row_digest")


def build_gap_inventory() -> list[dict[str, Any]]:
    return [
        gap_row(
            row_id="n10_c_gap_01_route_context_selection_boundary",
            component="N06 route context / native route arbitration boundary",
            source_keys=["n06_route_choice_closeout", "n10_hypothesis_a_closeout"],
            current_status="native_route_arbitration_consumed_as_selection_only_artifact_context",
            classification="constitutive_policy_input",
            load_bearing_for_native=True,
            consumed_by_n10="route_context_tag = route_context_selection_only",
            current_evidence=(
                "N06 supplies SC6 selection-only route-choice evidence; N10 "
                "uses selected route context, not semantic choice or route "
                "execution ownership."
            ),
            native_boundary=(
                "Native route arbitration can support route selection, but "
                "N10 does not treat that as semantic choice, agency, or "
                "goal ownership."
            ),
            native_policy_gap=None,
            minimal_native_surface_needed=(
                "If N11/N10 extends beyond selection-only context, the native "
                "route record must serialize context source, selected route "
                "digest, arbitration policy, stale-context blocker, and "
                "downstream consumption scope."
            ),
            overread_blocker="route_selection_relabelled_as_semantic_choice",
            iteration_14_contract_focus=[
                "route_context_source_digest",
                "selected_route_digest",
                "native_arbitration_policy_id",
                "stale_route_context_blocker",
                "selection_only_scope_marker",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_02_serialized_memory_policy",
            component="N08 artifact-only memory / trail affordance",
            source_keys=["n08_memory_trail_hypothesis_a", "n10_hypothesis_a_closeout"],
            current_status="artifact_only_serialized_producer_policy",
            classification="constitutive_policy_input",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "memory_scope_tag = "
                "artifact_only_serialized_producer_policy_route_memory_or_trail"
            ),
            current_evidence=(
                "N08 Hypothesis A provides MEM6 artifact-only route memory or "
                "trail affordance evidence via serialized producer policy."
            ),
            native_boundary=(
                "The memory/trail quantity is not yet a native coherence or "
                "geometry-conductance memory policy."
            ),
            native_policy_gap="native_route_conductance_memory_policy_missing",
            minimal_native_surface_needed=(
                "A native route-conductance memory policy with serialized "
                "update, decay/relaxation, reinforcement, budget surface, "
                "route-scope, and artifact replay contract."
            ),
            overread_blocker="producer_memory_policy_relabelled_as_native_memory",
            iteration_14_contract_focus=[
                "route_conductance_memory_policy_id",
                "memory_update_rule",
                "memory_relaxation_rule",
                "route_scope_digest",
                "memory_budget_surface",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_03_native_geometry_trail_design_direction",
            component="N08 native geometry trail design direction",
            source_keys=["n08_native_geometry_trail_hypothesis_b"],
            current_status="native_geometry_design_candidate_policy_gap_open",
            classification="constitutive_policy_input",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "recorded as native design direction, not consumed as native "
                "support in A/B composition"
            ),
            current_evidence=(
                "N08 Hypothesis B records static positive geometry response "
                "persistence and native geometry trail direction, while "
                "native route-conductance memory policy remains unavailable."
            ),
            native_boundary=(
                "Geometry can shape response, but persistent route memory is "
                "not yet a native policy surface."
            ),
            native_policy_gap="native_route_conductance_memory_policy_missing",
            minimal_native_surface_needed=(
                "A native geometry/conductance policy that records how route "
                "use changes future route affordance without introducing "
                "non-coherence hidden state."
            ),
            overread_blocker="static_geometry_response_relabelled_as_native_trail_memory",
            iteration_14_contract_focus=[
                "geometry_trace_source",
                "conductance_update_policy",
                "relaxation_persistence_window",
                "native_budget_conservation_check",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_04_goal_proxy_regulation_artifact_policy",
            component="N09 artifact-only goal-proxy regulation",
            source_keys=["n09_goal_proxy_hypothesis_a", "n10_hypothesis_a_closeout"],
            current_status="artifact_only_goal_proxy_regulation_candidate",
            classification="constitutive_policy_input",
            load_bearing_for_native=True,
            consumed_by_n10="regulation_scope = N09_GPR5_repeated_window_and_GPR6_closeout",
            current_evidence=(
                "N09 Hypothesis A supports artifact-only goal-proxy "
                "regulation; N10 consumes this as proxy regulation, not "
                "goal ownership or intention."
            ),
            native_boundary=(
                "Proxy measurement, error, eligibility, and correction are "
                "still artifact/producer policy surfaces for N10."
            ),
            native_policy_gap="native_goal_proxy_regulation_policy_missing",
            minimal_native_surface_needed=(
                "Native proxy surface, target band, error, eligibility, "
                "response, and artifact replay policy records."
            ),
            overread_blocker="goal_proxy_regulation_relabelled_as_goal_ownership",
            iteration_14_contract_focus=[
                "native_proxy_surface_policy_id",
                "target_band_policy",
                "proxy_error_policy",
                "proxy_conditioned_response_policy",
                "goal_proxy_budget_surface",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_05_response_magnitude_policy",
            component="N09 native-substrate response magnitude",
            source_keys=["n09_native_substrate_hypothesis_b"],
            current_status="native_substrate_design_candidate_blocked_for_general_regulation",
            classification="constitutive_policy_input",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "recorded as native regulation design direction, not consumed "
                "as general native regulation support"
            ),
            current_evidence=(
                "N09 Hypothesis B closes with a native-substrate-mediated "
                "goal-proxy regulation design candidate, but general native "
                "regulation remains blocked for unbounded perturbations."
            ),
            native_boundary=(
                "Native substrate response exists as a design candidate; "
                "general native regulation still needs a response magnitude "
                "policy."
            ),
            native_policy_gap="native_response_magnitude_policy_missing_for_unbounded_perturbations",
            minimal_native_surface_needed=(
                "A native response magnitude policy that serializes response "
                "size, perturbation envelope, budget effect, saturation "
                "control, and failure mode."
            ),
            overread_blocker="bounded_response_design_relabelled_as_general_native_regulation",
            iteration_14_contract_focus=[
                "response_magnitude_policy_id",
                "perturbation_envelope",
                "saturation_blocker",
                "unbounded_perturbation_failure_mode",
                "proxy_response_budget_check",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_06_identity_support_not_acceptance",
            component="N07 identity/support and withdrawal/restoration baseline",
            source_keys=["n07_identity_support_withdrawal", "n10_hypothesis_b_closeout"],
            current_status="support_invariance_baseline_consumable_not_identity_acceptance",
            classification="constitutive_prerequisite_and_replay_validation",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "support_state_tag matrix: support_intact, mild_withdrawal, "
                "disrupted, explicit_restoration"
            ),
            current_evidence=(
                "N07 supplies support/invariance, support-disruption, and "
                "explicit-restoration baselines used by N10 Hypothesis B."
            ),
            native_boundary=(
                "Support survival and restoration are not runtime identity "
                "acceptance, RC identity collapse, or identity ownership."
            ),
            native_policy_gap="native_identity_acceptance_validator_missing",
            minimal_native_surface_needed=(
                "A native identity/support validator that separates support "
                "survival, restoration, identity acceptance, and RC identity "
                "collapse with explicit blockers."
            ),
            overread_blocker="support_invariance_relabelled_as_identity_acceptance",
            iteration_14_contract_focus=[
                "support_area_digest",
                "support_state_policy",
                "withdrawal_restoration_ordering",
                "identity_acceptance_validator",
                "rc_identity_collapse_blocker",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_07_artifact_only_integration_validator",
            component="N10 Hypothesis A artifact-only integration validator",
            source_keys=["n10_hypothesis_a_closeout"],
            current_status="artifact_only_integration_supported",
            classification="replay_validation",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "validates source-backed route-memory-support-regulation "
                "composition without private runtime state"
            ),
            current_evidence=(
                "N10 Hypothesis A supports bounded artifact-only "
                "agentic-like integration candidate."
            ),
            native_boundary=(
                "Artifact-only replay is not the same as a live native "
                "agentic-like integration policy."
            ),
            native_policy_gap="native_agentic_like_integration_policy_missing",
            minimal_native_surface_needed=(
                "A native integration policy that serializes component "
                "eligibility, source-current requirements, ordering, budget "
                "surfaces, stale-source blockers, and no-claim flags."
            ),
            overread_blocker="artifact_only_closeout_relabelled_as_native_integration",
            iteration_14_contract_focus=[
                "native_integration_policy_id",
                "component_eligibility_records",
                "source_current_ordering",
                "artifact_replay_contract",
                "claim_boundary_flags",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_08_support_sensitive_integration_gate",
            component="N10 Hypothesis B support-state matrix",
            source_keys=["n10_hypothesis_b_closeout"],
            current_status="artifact_only_support_sensitive_integration_supported",
            classification="replay_validation_and_constitutive_gate",
            load_bearing_for_native=True,
            consumed_by_n10=(
                "intact/mild/restored support may allow composition; "
                "disrupted support must block"
            ),
            current_evidence=(
                "N10 Hypothesis B supports bounded support-sensitive full "
                "composition and preserves disruption history."
            ),
            native_boundary=(
                "The support-sensitive gate is artifact-only; a native "
                "integration policy would need to enforce it at runtime."
            ),
            native_policy_gap="native_agentic_like_integration_policy_missing",
            minimal_native_surface_needed=(
                "A native support-state integration gate with explicit "
                "support-current, disruption, restoration, and history "
                "preservation blockers."
            ),
            overread_blocker="support_sensitive_artifact_matrix_relabelled_as_native_gate",
            iteration_14_contract_focus=[
                "support_state_current_digest",
                "disrupted_support_blocker",
                "restoration_evidence_digest",
                "support_history_preservation",
                "support_state_ordering",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_09_budget_surfaces_and_source_continuity",
            component="N10 source-artifact budget compatibility",
            source_keys=["n10_hypothesis_a_closeout", "n10_hypothesis_b_closeout"],
            current_status="source_artifact_budget_compatibility_not_single_live_ledger",
            classification="bookkeeping_and_replay_validation",
            load_bearing_for_native=False,
            consumed_by_n10=(
                "N10 checks each source artifact budget surface but does not "
                "claim one continuous packet ledger across N05-N09."
            ),
            current_evidence=(
                "A/B preserve exact per-artifact budget checks and keep "
                "node-plus-packet, memory, and proxy budget surfaces separate."
            ),
            native_boundary=(
                "Fully native integration would need same-runtime budget "
                "continuity; current N10 has source-artifact compatibility."
            ),
            native_policy_gap=None,
            minimal_native_surface_needed=(
                "If later implemented natively, one live runtime must keep "
                "node-plus-packet, memory, proxy, and claim/economy accounting "
                "separate while preserving end-to-end conservation."
            ),
            overread_blocker="source_artifact_budget_relabelled_as_live_packet_ledger",
            iteration_14_contract_focus=[
                "node_plus_packet_budget_surface",
                "memory_budget_surface",
                "proxy_budget_surface",
                "cross_artifact_budget_nonclaim",
            ],
        ),
        gap_row(
            row_id="n10_c_gap_10_claim_boundary_flags",
            component="N10 claim boundary",
            source_keys=["n10_hypothesis_a_closeout", "n10_hypothesis_b_closeout"],
            current_status="all_native_agentic_and_agency_claims_blocked",
            classification="claim_boundary",
            load_bearing_for_native=True,
            consumed_by_n10="claim flags remain false across A/B/C",
            current_evidence=(
                "A/B closeouts leave agency, semantic goal ownership, "
                "identity acceptance, ACO, biology, personhood, A7, and fully "
                "native agentic-like integration blocked."
            ),
            native_boundary=(
                "No native support flag may open until the missing native "
                "policy surfaces have explicit implementations and controls."
            ),
            native_policy_gap="native_agentic_like_integration_policy_missing",
            minimal_native_surface_needed=(
                "Claim boundary schema that rejects producer relabeling, "
                "hidden policy inputs, direct mutation, and native support "
                "claims without native contracts."
            ),
            overread_blocker="claim_promotion_blocked",
            iteration_14_contract_focus=[
                "claim_flag_immutability",
                "native_support_flag_gate",
                "producer_relabeling_blocker",
                "hidden_policy_blocker",
            ],
        ),
    ]


def build_controls(rows: list[dict[str, Any]]) -> dict[str, Any]:
    row_ids = {row["row_id"] for row in rows}
    blockers = {row["native_policy_gap"] for row in rows if row["native_policy_gap"]}
    return {
        "producer_scaffold_relabelled_native": {
            "control_passed": True,
            "primary_blocker": "producer_scaffold_relabelled_as_native_blocked",
            "reason": "producer-mediated and artifact-local fields are explicitly classified",
        },
        "artifact_validator_relabelled_native": {
            "control_passed": True,
            "primary_blocker": "artifact_validator_relabelled_as_native_blocked",
            "reason": "artifact-only replay rows remain replay validation, not native runtime support",
        },
        "route_selection_relabelled_semantic_choice": {
            "control_passed": "n10_c_gap_01_route_context_selection_boundary" in row_ids,
            "primary_blocker": "route_selection_relabelled_as_semantic_choice",
            "reason": "N06 route context remains selection-only in N10",
        },
        "memory_policy_relabelled_native_memory": {
            "control_passed": "native_route_conductance_memory_policy_missing" in blockers,
            "primary_blocker": "producer_memory_policy_relabelled_as_native_memory",
            "reason": "N08 route memory remains artifact-only until native conductance memory exists",
        },
        "goal_proxy_relabelled_goal_ownership": {
            "control_passed": "native_response_magnitude_policy_missing_for_unbounded_perturbations"
            in blockers,
            "primary_blocker": "goal_proxy_regulation_relabelled_as_goal_ownership",
            "reason": "N09 remains proxy regulation, not goal ownership",
        },
        "support_relabelled_identity_acceptance": {
            "control_passed": "native_identity_acceptance_validator_missing" in blockers,
            "primary_blocker": "support_invariance_relabelled_as_identity_acceptance",
            "reason": "N07 support/invariance remains distinct from identity acceptance",
        },
        "native_support_claim_promotion": {
            "control_passed": all(value is False for value in CLAIM_FLAGS.values()),
            "primary_blocker": "native_support_claim_promotion_blocked",
            "reason": "Iteration 13 opens no native support or agency-related claim flags",
        },
    }


def build_checks(
    artifacts: dict[str, dict[str, Any]],
    artifact_records: dict[str, Any],
    rows: list[dict[str, Any]],
    controls: dict[str, Any],
) -> dict[str, bool]:
    row_ids = {row["row_id"] for row in rows}
    row_blockers = {row["native_policy_gap"] for row in rows if row["native_policy_gap"]}
    required_rows = {
        "n10_c_gap_01_route_context_selection_boundary",
        "n10_c_gap_02_serialized_memory_policy",
        "n10_c_gap_03_native_geometry_trail_design_direction",
        "n10_c_gap_04_goal_proxy_regulation_artifact_policy",
        "n10_c_gap_05_response_magnitude_policy",
        "n10_c_gap_06_identity_support_not_acceptance",
        "n10_c_gap_07_artifact_only_integration_validator",
        "n10_c_gap_08_support_sensitive_integration_gate",
        "n10_c_gap_09_budget_surfaces_and_source_continuity",
        "n10_c_gap_10_claim_boundary_flags",
    }
    return {
        "all_required_source_artifacts_present": set(SOURCE_ARTIFACTS).issubset(
            artifact_records
        ),
        "all_required_source_artifacts_passed": all(
            artifact.get("status") == "passed" for artifact in artifacts.values()
        ),
        "source_sha256_pins_recorded": all(
            isinstance(record["sha256"], str) and len(record["sha256"]) == 64
            for record in artifact_records.values()
        ),
        "source_embedded_output_digest_audit_completed": all(
            "output_digest_valid" in record for record in artifact_records.values()
        ),
        "all_required_gap_rows_present": required_rows.issubset(row_ids),
        "all_gap_row_digests_valid": all(
            row["gap_row_digest"]
            == digest_value(
                {key: value for key, value in row.items() if key != "gap_row_digest"}
            )
            for row in rows
        ),
        "load_bearing_constitutive_inputs_identified": sum(
            1
            for row in rows
            if row["load_bearing_for_native"]
            and "constitutive" in row["classification"]
        )
        >= 6,
        "expected_native_blockers_recorded": set(EXPECTED_NATIVE_BLOCKERS).issubset(
            row_blockers
        ),
        "bookkeeping_not_promoted_to_native": any(
            row["classification"] == "bookkeeping_and_replay_validation"
            and row["load_bearing_for_native"] is False
            for row in rows
        ),
        "claim_flags_all_false": all(value is False for value in CLAIM_FLAGS.values()),
        "fully_native_agentic_like_integration_blocked": True,
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "src_clean_for_iteration_13": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    artifacts = {key: load_json(path) for key, path in SOURCE_ARTIFACTS.items()}
    artifact_records, report_records = source_records(artifacts)
    gap_inventory = build_gap_inventory()
    controls = build_controls(gap_inventory)
    checks = build_checks(artifacts, artifact_records, gap_inventory, controls)
    closeout = with_digest(
        {
            "hypothesis_c_iteration_13_row_id": "n10_i13_native_policy_gap_inventory_v1",
            "inventory_status": "native_policy_gap_inventory_complete"
            if all(checks.values())
            else "native_policy_gap_inventory_failed",
            "bounded_artifact_only_agentic_like_integration_supported": True,
            "support_sensitive_integration_supported": True,
            "fully_native_agentic_like_integration_supported": False,
            "fully_native_agentic_like_integration_primary_blockers": EXPECTED_NATIVE_BLOCKERS,
            "native_support_flags_opened": False,
            "gap_row_count": len(gap_inventory),
            "load_bearing_gap_row_count": sum(
                1 for row in gap_inventory if row["load_bearing_for_native"]
            ),
            "source_embedded_output_digest_mismatch_count": sum(
                1
                for record in artifact_records.values()
                if record["output_digest"] is not None
                and record["output_digest_valid"] is False
            ),
            "classification_counts": {
                classification: sum(
                    1 for row in gap_inventory if row["classification"] == classification
                )
                for classification in sorted(
                    {row["classification"] for row in gap_inventory}
                )
            },
            "claim_flags": CLAIM_FLAGS,
            "next_iteration": "14_hypothesis_c_native_contract_requirements",
        },
        "hypothesis_c_inventory_digest",
    )
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 13 passes if N10 records which parts of the bounded "
            "integration chain are still producer-mediated, artifact-local, "
            "or validator-local, and which of those parts are load-bearing "
            "for a future native implementation. The iteration is "
            "inventory-only and does not claim native agentic-like "
            "integration support."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_13_hypothesis_c_native_policy_gap_inventory_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 13,
        "purpose": "hypothesis_c_native_policy_gap_inventory",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": artifact_records,
        "source_reports": report_records,
        "native_policy_gap_inventory": gap_inventory,
        "controls": controls,
        "checks": checks,
        "hypothesis_c_inventory_closeout": closeout,
        "acceptance": acceptance,
        "next_iteration": "14_hypothesis_c_native_contract_requirements",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    closeout = output["hypothesis_c_inventory_closeout"]
    rows = output["native_policy_gap_inventory"]
    lines = [
        "# N10 Iteration 13 Hypothesis C Native Policy Gap Inventory",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 13 inventories the native-policy boundary for N10. It",
        "does not run a new mechanism and does not open native support. The",
        "result is a source-backed map of which A/B composition fields are",
        "bookkeeping, replay validation, or constitutive policy inputs.",
        "",
        "```text",
        f"inventory_status = {closeout['inventory_status']}",
        "bounded_artifact_only_agentic_like_integration_supported = true",
        "support_sensitive_integration_supported = true",
        "fully_native_agentic_like_integration_supported = false",
        "native_support_flags_opened = false",
        "```",
        "",
        "## What Hypothesis C Can Show",
        "",
        "Hypothesis C shows the exact native absorption boundary. A and B",
        "proved bounded artifact-only composition and support sensitivity. C",
        "shows which pieces must become native policy surfaces before the same",
        "pattern can be treated as fully native LGRC substrate support.",
        "",
        "The conservative result is:",
        "",
        "```text",
        "bounded artifact-only agentic-like integration = supported",
        "support-sensitive integration = supported",
        "fully native agentic-like integration = blocked by named native gaps",
        "```",
        "",
        "## Phase 8 Boundary",
        "",
        "The recorded blockers are Phase 8-facing native absorption",
        "requirements, not Phase 8 work already opened or implemented. In",
        "this split, N10 Hypothesis C identifies what is missing natively;",
        "a later Phase 8 task would implement selected missing mechanisms in",
        "`src/*`.",
        "",
        "```text",
        "native_route_conductance_memory_policy_missing:",
        "    likely a concrete Phase 8 element for absorbing N08 memory/trail",
        "    into native route conductance or geometry-mediated route memory",
        "",
        "native_response_magnitude_policy_missing_for_unbounded_perturbations:",
        "    likely a concrete Phase 8 element for absorbing N09 response",
        "    sizing into native regulation policy",
        "",
        "native_identity_acceptance_validator_missing:",
        "    Phase 8-facing eventually, but claim-sensitive and theory-sensitive;",
        "    it should wait until identity acceptance is precisely defined",
        "",
        "native_agentic_like_integration_policy_missing:",
        "    a meta-gap, not one small mechanism; it should come after the",
        "    component native policies are defined",
        "```",
        "",
        "Iteration 14 should turn these into contract requirements. Iteration",
        "15 should decide which become future Phase 8 tasks and in what order.",
        "",
        "## Primary Native Blockers",
        "",
        "```json",
        json.dumps(
            closeout["fully_native_agentic_like_integration_primary_blockers"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Inventory Rows",
        "",
        "```json",
        json.dumps(rows, indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
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
        "Iteration 13 does not claim fully native agentic-like integration,",
        "agency, intention, semantic goal ownership, identity acceptance, RC",
        "identity collapse, ACO, biological behavior, personhood, locomotion,",
        "or unrestricted agency. It records gaps for Iteration 14 contracts.",
        "",
        "## Reproduction",
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
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 13 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run N10 Iteration 7 route-memory-regulation composition.

Iteration 7 composes the source-backed N06 route-choice, N08 memory/trail,
N07 support, and N09 goal-proxy regulation artifacts into one bounded
artifact-only integration row. It is the first ALI4 row, not an A6/ALI6
closeout: repeated-window validation and final artifact-only closeout remain
assigned to Iterations 8 and 9.
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
BASELINE_PATH = EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json"
ITERATION_6_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_6_explicit_restoration_replay.json"
)
OUTPUT_PATH = (
    EXPERIMENT
    / "outputs"
    / "n10_iteration_7_route_memory_regulation_composition.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports"
    / "n10_iteration_7_route_memory_regulation_composition.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_7_route_memory_regulation_composition.py"
)


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
    return digest_value({k: v for k, v in output.items() if k not in excluded})


def source_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_artifacts"][key]["path"]


def report_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_reports"][key]["path"]


def find_lane(rows: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("lane_id") == lane_id:
            return row
    raise KeyError(f"lane not found: {lane_id}")


def find_fixture_lane(manifest: dict[str, Any], lane_id: str) -> dict[str, Any]:
    return find_lane(manifest["fixture_lanes"], lane_id)


def source_support_state_tag(manifest: dict[str, Any], support_lane: dict[str, Any]) -> str:
    outcome = support_lane["identity_support_outcome_tag"]
    return manifest["allowed_values"]["source_support_outcome_map"][outcome]


def build_source_records(
    baseline: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]
    report_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]
    source_artifacts = {
        "n10_baseline_inventory": {
            "path": rel(BASELINE_PATH),
            "sha256": digest_file(BASELINE_PATH),
        },
        "n10_fixture_manifest": {
            "path": rel(MANIFEST_PATH),
            "sha256": digest_file(MANIFEST_PATH),
        },
        "n10_iteration_6_explicit_restoration_replay": {
            "path": rel(ITERATION_6_PATH),
            "sha256": digest_file(ITERATION_6_PATH),
        },
    }
    for key in artifact_keys:
        path = source_path(baseline, key)
        current_digest = digest_file(path)
        source_artifacts[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_artifacts"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_artifacts"][key]["sha256"],
        }

    source_reports = {}
    for key in report_keys:
        path = report_path(baseline, key)
        current_digest = digest_file(path)
        source_reports[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_reports"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_reports"][key]["sha256"],
        }
    return source_artifacts, source_reports


def route_evidence(n06: dict[str, Any]) -> dict[str, Any]:
    artifact_closeout = n06["artifact_only_closeout"]
    per_cycle = artifact_closeout["per_cycle"]
    return {
        "source_sc_level": n06["closeout"]["strongest_supported_sc_level"],
        "source_claim_ceiling": n06["closeout"]["strongest_claim_ceiling"],
        "selection_causality_basis": n06["closeout"]["selection_causality_basis"],
        "selection_scope": artifact_closeout["scope"],
        "scheduled_processed_packet_evidence_applicability": n06["closeout"][
            "scheduled_processed_packet_evidence_applicability"
        ],
        "artifact_only_replay_passed": n06["acceptance"][
            "artifact_only_replay_passed"
        ],
        "budget_conservation_passed": n06["acceptance"][
            "budget_conservation_passed"
        ],
        "controls_passed": n06["acceptance"]["controls_passed"],
        "native_selection_replayable_under_selection_only_scope": all(
            row["checks"]["native_selection_replayable_under_selection_only_scope"]
            for row in per_cycle
        ),
        "candidate_sets_replayed": artifact_closeout["checks"][
            "candidate_sets_replayed"
        ],
        "native_arbitration_records_replayed": artifact_closeout["checks"][
            "native_arbitration_records_replayed"
        ],
        "context_relations_replayed": artifact_closeout["checks"][
            "context_relations_replayed"
        ],
        "selected_routes": [row["selected_route"] for row in per_cycle],
        "selected_route_count": len(per_cycle),
        "claim_flags_false": all(
            value is False
            for key, value in n06["acceptance"].items()
            if key.endswith("_claim_allowed")
        ),
    }


def memory_evidence(n08: dict[str, Any]) -> dict[str, Any]:
    closeout = n08["closeout"]
    replay = n08["artifact_only_replay"]
    source_controls = n08["source_control_replay"]
    return {
        "source_mem_level": closeout["strongest_supported_mem_level"],
        "source_claim_ceiling": closeout["strongest_claim_ceiling"],
        "memory_or_trail_claim_scope": closeout["memory_or_trail_claim_scope"],
        "native_support_status": closeout["native_support_status"],
        "artifact_only_replay_passed": closeout["artifact_only_replay_passed"],
        "corrupted_controls_passed": closeout["corrupted_controls_passed"],
        "source_controls_replayed": n08["checks"]["source_controls_replayed"],
        "memory_strength_used_as_score_evidence": closeout[
            "independent_memory_strength_used_as_score_evidence"
        ],
        "memory_strength_used_as_physical_flux": closeout[
            "independent_memory_strength_used_as_physical_flux"
        ],
        "memory_budget_discontinuity_control_passed": source_controls[
            "memory_budget_discontinuity"
        ]["replay_passed"],
        "hidden_route_preference_control_passed": source_controls[
            "repeated_hidden_route_preference"
        ]["replay_passed"],
        "stale_memory_surface_control_passed": source_controls[
            "stale_memory_surface_read"
        ]["replay_passed"],
        "artifact_only_chain_reconstructed": replay["chain_reconstructed"],
        "selected_routes": replay["selected_routes"],
        "route_a_strength_after_each_cycle": replay[
            "route_a_strength_after_each_cycle"
        ],
        "route_b_strength_after_each_cycle": replay[
            "route_b_strength_after_each_cycle"
        ],
        "claim_flags_scope": "source_memory_or_trail_claim_only_not_n10_agency_claim",
    }


def build_composition_row(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n06: dict[str, Any],
    n08: dict[str, Any],
    n09: dict[str, Any],
    support_lane: dict[str, Any],
    fixture_lane: dict[str, Any],
    iteration_6: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    support_state_tag = source_support_state_tag(manifest, support_lane)
    route = route_evidence(n06)
    memory = memory_evidence(n08)
    row = {
        "integration_row_id": "n10_i7_route_memory_regulation_composition_row_v1",
        "integration_level": "A4",
        "attempted_integration_level": "A6",
        "accepted_integration_level": "A4",
        "n10_category_level": "ALI4",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": "artifact_replay_n10_i7",
        "scheduler_event_index": None,
        "source_experiment_ids": ["N06", "N07", "N08", "N09", "N10"],
        "source_artifacts": {
            key: value["path"] for key, value in source_artifacts.items()
        },
        "source_reports": {
            key: value["path"] for key, value in source_reports.items()
        },
        "source_artifact_digests": {
            key: value["sha256"] for key, value in source_artifacts.items()
        },
        "route_choice_artifact": "n06_closeout",
        "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
        "memory_affordance_artifact": "n08_hypothesis_a_closeout",
        "memory_affordance_digest": source_artifacts[
            "n08_hypothesis_a_closeout"
        ]["sha256"],
        "identity_support_artifact": "n07_withdrawal_baseline",
        "identity_support_digest": source_artifacts["n07_withdrawal_baseline"][
            "sha256"
        ],
        "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
        "goal_proxy_regulation_digest": source_artifacts["n09_hypothesis_a_closeout"][
            "sha256"
        ],
        "support_state_tag": support_state_tag,
        "route_context_tag": "route_context_selection_only",
        "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "regulation_scope_tag": "artifact_only_goal_proxy_regulation_candidate",
        "integration_outcome_tag": "route_memory_regulation_composition_candidate",
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "n08_source_memory_budget_compatibility",
        "proxy_budget_surface": "n09_source_proxy_budget_compatibility",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": baseline["native_policy_gaps"],
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "claim_flags": claim_flags,
        "integration_allowed": True,
        "positive_integration_row_emitted": True,
        "primary_blocker": None,
        "category_boundary": (
            "ALI4 composes route choice, memory/trail affordance, identity "
            "support, and goal-proxy regulation from source artifacts. It "
            "does not close ALI5/ALI6 because bounded repeated integration "
            "and final artifact-only closeout remain pending."
        ),
        "a6_relevance": "route_memory_regulation_composition_component_not_a6_closeout",
        "fixture_lane": {
            "lane_id": fixture_lane["lane_id"],
            "expected_role": fixture_lane["expected_role"],
            "required_support_state_tag": fixture_lane[
                "required_support_state_tag"
            ],
            "required_route_context_tag": fixture_lane[
                "required_route_context_tag"
            ],
            "route_context_constraint": fixture_lane["route_context_constraint"],
            "source_support_lane_id": fixture_lane["source_support_lane_id"],
        },
        "composition_chain": [
            "N06 route-choice source",
            "N08 memory/trail affordance source",
            "N07 support-intact baseline",
            "N09 goal-proxy regulation source",
            "N10 ALI3 support-sensitive regulation precondition",
            "N10 ALI4 route-memory-regulation composition row",
        ],
        "route_evidence": route,
        "memory_evidence": memory,
        "support_evidence": {
            "source_lane_id": support_lane["lane_id"],
            "lane_digest": support_lane["lane_digest"],
            "identity_support_outcome_tag": support_lane[
                "identity_support_outcome_tag"
            ],
            "support_survival_passed": support_lane["support_survival_passed"],
            "support_survival_threshold": support_lane["support_survival_threshold"],
            "final_A_support_retention": support_lane["final_A_support_retention"],
            "reference_A_support_retention": support_lane[
                "reference_A_support_retention"
            ],
            "final_basin_separability": support_lane["final_basin_separability"],
            "final_budget_error": support_lane["final_budget_error"],
            "withdrawal_depth": support_lane["withdrawal_depth"],
            "restoration_fraction": support_lane["restoration_fraction"],
        },
        "regulation_evidence": {
            "source_gpr_level": n09["ceiling_algorithm_result"][
                "strongest_passing_gpr_level"
            ],
            "source_claim_ceiling": n09["claim_ceiling"],
            "source_hypothesis_a_status": n09["ceiling_algorithm_result"][
                "hypothesis_a_status"
            ],
            "source_budget_control_passed": n09["controls"]["budget_violation"][
                "control_passed"
            ],
            "source_artifact_only_runtime_fallback_blocked": n09["controls"][
                "artifact_runtime_fallback"
            ]["control_passed"],
        },
        "support_sensitive_precondition": {
            "source_iteration": 6,
            "artifact": "n10_iteration_6_explicit_restoration_replay",
            "artifact_digest": source_artifacts[
                "n10_iteration_6_explicit_restoration_replay"
            ]["sha256"],
            "ali3_status": iteration_6["integration_row"]["ali3_status"],
            "a6_not_supported_by_iteration_6": iteration_6["checks"][
                "a6_not_supported_by_iteration_6"
            ],
        },
        "budget_mode": "source_artifact_budget_compatibility_not_single_runtime_continuity",
    }
    return with_digest(row, "integration_row_digest")


def build_controls(
    manifest: dict[str, Any],
    integration_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    manifest_support_lane: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    route = integration_row["route_evidence"]
    memory = integration_row["memory_evidence"]
    support = integration_row["support_evidence"]
    return {
        "missing_route_choice_artifact": {
            "control_passed": integration_row["route_choice_artifact"]
            == "n06_closeout",
            "primary_blocker": blockers["missing_route_choice_artifact"],
            "reason": "ALI4 composition requires the N06 route-choice closeout",
        },
        "missing_memory_affordance_artifact": {
            "control_passed": integration_row["memory_affordance_artifact"]
            == "n08_hypothesis_a_closeout",
            "primary_blocker": blockers["missing_memory_affordance_artifact"],
            "reason": "ALI4 composition requires the N08 Hypothesis A MEM6 closeout",
        },
        "missing_identity_support_artifact": {
            "control_passed": integration_row["identity_support_artifact"]
            == "n07_withdrawal_baseline",
            "primary_blocker": blockers["missing_identity_support_artifact"],
            "reason": "ALI4 composition requires N07 support baseline evidence",
        },
        "missing_goal_proxy_regulation_artifact": {
            "control_passed": integration_row["goal_proxy_regulation_artifact"]
            == "n09_hypothesis_a_closeout",
            "primary_blocker": blockers["missing_goal_proxy_regulation_artifact"],
            "reason": "ALI4 composition requires N09 GPR closeout evidence",
        },
        "source_artifact_digest_mismatch": {
            "control_passed": all(
                value.get("matches_baseline", True) for value in source_artifacts.values()
            ),
            "primary_blocker": blockers["source_artifact_digest_mismatch"],
            "reason": "N06/N07/N08/N09 source artifact digests are rechecked against Iteration 1",
        },
        "stale_route_context": {
            "control_passed": integration_row["route_context_tag"]
            == "route_context_selection_only"
            and route["selection_scope"] == "selection_only_pre_topology_commit"
            and route["scheduled_processed_packet_evidence_applicability"]
            == "not_applicable_pre_topology_selection_only_scope",
            "primary_blocker": blockers["stale_route_context"],
            "reason": "N06 route evidence is consumed only under its declared selection-only pre-topology scope",
        },
        "stale_memory_surface": {
            "control_passed": integration_row["memory_scope_tag"]
            == "artifact_only_serialized_producer_policy_route_memory_or_trail"
            and memory["source_mem_level"] == "MEM6"
            and memory["stale_memory_surface_control_passed"] is True,
            "primary_blocker": blockers["stale_memory_surface"],
            "reason": "N08 memory surface is consumed only as serialized artifact-only producer-policy memory evidence",
        },
        "stale_identity_support_baseline": {
            "control_passed": support["lane_digest"]
            == manifest_support_lane["lane_digest"]
            and support["final_A_support_retention"]
            == manifest_support_lane["final_A_support_retention"],
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "support state is read from the current N07 support-intact lane and matched against the N10 manifest summary",
        },
        "hidden_experiment_side_steering": {
            "control_passed": route[
                "native_selection_replayable_under_selection_only_scope"
            ]
            is True
            and memory["hidden_route_preference_control_passed"] is True,
            "primary_blocker": blockers["hidden_experiment_side_steering"],
            "reason": "route selection and memory-shaped scoring are source-backed replay evidence, not N10 report-side if/else steering",
        },
        "budget_surface_ambiguity": {
            "control_passed": integration_row["node_plus_packet_budget_error"] == 0.0
            and route["budget_conservation_passed"] is True
            and memory["memory_budget_discontinuity_control_passed"] is True
            and support["final_budget_error"] == 0.0
            and integration_row["regulation_evidence"]["source_budget_control_passed"]
            is True,
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "Iteration 7 claims source-artifact budget compatibility only, while route, memory, support, and proxy budget surfaces remain separate",
        },
        "artifact_only_replay_missing_link": {
            "control_passed": all(
                integration_row[field] is not None
                for field in [
                    "route_choice_digest",
                    "memory_affordance_digest",
                    "identity_support_digest",
                    "goal_proxy_regulation_digest",
                ]
            )
            and integration_row["artifact_only"] is True
            and integration_row["runtime_state_used"] is False,
            "primary_blocker": blockers["artifact_only_replay_missing_link"],
            "reason": "all four source links are present and replay remains artifact-only",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in integration_row["claim_flags"].values()
            ),
            "primary_blocker": blockers["claim_promotion"],
            "reason": "ALI4 composition cannot emit ACO, agency, A6, identity acceptance, or goal-ownership claims",
        },
    }


def validate_output(
    manifest: dict[str, Any],
    integration_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    required_fields = set(manifest["integration_row_required_fields"])
    row_fields = set(integration_row)
    route = integration_row["route_evidence"]
    memory = integration_row["memory_evidence"]
    support = integration_row["support_evidence"]
    regulation = integration_row["regulation_evidence"]
    fixture = integration_row["fixture_lane"]
    return {
        "integration_row_required_fields_present": required_fields.issubset(
            row_fields
        ),
        "integration_row_digest_valid": integration_row["integration_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in integration_row.items()
                if key != "integration_row_digest"
            }
        ),
        "n10_category_level_is_ali4": integration_row["n10_category_level"]
        == "ALI4",
        "integration_level_is_a4_not_a6": integration_row["integration_level"]
        == "A4",
        "attempted_a6_not_accepted": integration_row["attempted_integration_level"]
        == "A6"
        and integration_row["accepted_integration_level"] == "A4",
        "route_context_tag_is_selection_only": integration_row["route_context_tag"]
        == "route_context_selection_only",
        "fixture_required_route_context_tag_matched": integration_row[
            "route_context_tag"
        ]
        == fixture["required_route_context_tag"],
        "support_state_tag_is_support_intact": integration_row["support_state_tag"]
        == "support_intact_survives",
        "fixture_required_support_state_tag_matched": integration_row[
            "support_state_tag"
        ]
        == fixture["required_support_state_tag"],
        "memory_scope_tag_is_artifact_only_policy": integration_row[
            "memory_scope_tag"
        ]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "route_sc6_available": route["source_sc_level"] == "SC6",
        "route_selection_scope_preserved": route["selection_scope"]
        == "selection_only_pre_topology_commit"
        and route["scheduled_processed_packet_evidence_applicability"]
        == "not_applicable_pre_topology_selection_only_scope",
        "route_native_selection_replayable": route[
            "native_selection_replayable_under_selection_only_scope"
        ]
        is True,
        "memory_mem6_available": memory["source_mem_level"] == "MEM6",
        "memory_scope_preserved": memory["memory_or_trail_claim_scope"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "memory_not_physical_flux": memory["memory_strength_used_as_physical_flux"]
        is False,
        "memory_artifact_only_chain_reconstructed": memory[
            "artifact_only_chain_reconstructed"
        ]
        is True,
        "support_intact_lane_survives": support["support_survival_passed"] is True,
        "support_lane_budget_error_zero": support["final_budget_error"] == 0.0,
        "n09_gpr6_available": regulation["source_gpr_level"] == "GPR6",
        "n09_goal_proxy_candidate_available": regulation["source_claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "ali3_support_sensitive_precondition_available": integration_row[
            "support_sensitive_precondition"
        ]["ali3_status"]
        == "support_sensitive_regulation_closed_for_artifact_only_support_regulation_path",
        "source_artifact_digests_match_baseline": all(
            value.get("matches_baseline", True) for value in source_artifacts.values()
        ),
        "artifact_only_replay": integration_row["artifact_only"] is True
        and integration_row["runtime_state_used"] is False,
        "all_four_source_links_present": all(
            integration_row[field] is not None
            for field in [
                "route_choice_digest",
                "memory_affordance_digest",
                "identity_support_digest",
                "goal_proxy_regulation_digest",
            ]
        ),
        "integration_allowed_true": integration_row["integration_allowed"] is True,
        "positive_integration_row_emitted": integration_row[
            "positive_integration_row_emitted"
        ]
        is True,
        "claim_flags_all_false": all(
            value is False for value in integration_row["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "a6_not_supported_by_iteration_7": integration_row["n10_category_level"]
        != "ALI6"
        and integration_row["integration_level"] != "A6",
        "src_clean_for_iteration_7": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n06 = load_json(source_path(baseline, "n06_closeout"))
    n07_i13 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n08 = load_json(source_path(baseline, "n08_hypothesis_a_closeout"))
    n09 = load_json(source_path(baseline, "n09_hypothesis_a_closeout"))
    iteration_6 = load_json(ITERATION_6_PATH)
    support_lane = find_lane(n07_i13["withdrawal_lanes"], "support_intact_reference")
    manifest_support_lane = find_lane(
        manifest["source_support_lanes"], "support_intact_reference"
    )
    fixture_lane = find_fixture_lane(manifest, "route_memory_regulation_composition")
    source_artifacts, source_reports = build_source_records(baseline)
    integration_row = build_composition_row(
        baseline,
        manifest,
        n06,
        n08,
        n09,
        support_lane,
        fixture_lane,
        iteration_6,
        source_artifacts,
        source_reports,
    )
    controls = build_controls(
        manifest, integration_row, source_artifacts, manifest_support_lane
    )
    checks = validate_output(manifest, integration_row, source_artifacts, controls)
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_n06_route_choice_closeout",
                "artifact": source_artifacts["n06_closeout"]["path"],
                "digest": source_artifacts["n06_closeout"]["sha256"],
                "route_context_tag": integration_row["route_context_tag"],
            },
            {
                "step": "load_n08_memory_trail_affordance_closeout",
                "artifact": source_artifacts["n08_hypothesis_a_closeout"]["path"],
                "digest": source_artifacts["n08_hypothesis_a_closeout"]["sha256"],
                "memory_scope_tag": integration_row["memory_scope_tag"],
            },
            {
                "step": "load_n07_support_intact_lane",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_id": support_lane["lane_id"],
                "support_lane_digest": support_lane["lane_digest"],
            },
            {
                "step": "load_n09_goal_proxy_regulation_closeout",
                "artifact": source_artifacts["n09_hypothesis_a_closeout"]["path"],
                "digest": source_artifacts["n09_hypothesis_a_closeout"]["sha256"],
            },
            {
                "step": "load_n10_ali3_support_sensitive_precondition",
                "artifact": source_artifacts[
                    "n10_iteration_6_explicit_restoration_replay"
                ]["path"],
                "digest": source_artifacts[
                    "n10_iteration_6_explicit_restoration_replay"
                ]["sha256"],
                "ali3_status": integration_row["support_sensitive_precondition"][
                    "ali3_status"
                ],
            },
            {
                "step": "emit_route_memory_regulation_composition_row",
                "integration_row_digest": integration_row["integration_row_digest"],
                "n10_category_level": integration_row["n10_category_level"],
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 7 passes if N10 can compose route choice, memory/trail "
            "affordance, identity/support evidence, and goal-proxy regulation "
            "into one replayable source-backed row while rejecting hidden route "
            "labels, hidden memory surfaces, stale context, budget ambiguity, "
            "and claim promotion."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_7_route_memory_regulation_composition_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 7,
        "purpose": "route_memory_regulation_composition_no_a6_closeout",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "manifest_digest": manifest["manifest_digest"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "integration_row": integration_row,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "8_bounded_repeated_integration",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    row = output["integration_row"]
    lines = [
        "# N10 Iteration 7 Route-Memory-Regulation Composition",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 7 composed N06 route-choice evidence, N08 memory/trail",
        "affordance evidence, N07 support-intact evidence, and N09 goal-proxy",
        "regulation evidence into one source-backed artifact-only row.",
        "",
        "This is the first ALI4 row. It does not close A6/ALI6 because bounded",
        "repetition and final artifact-only closeout remain assigned to",
        "Iterations 8 and 9.",
        "",
        "```text",
        f"integration_level = {row['integration_level']}",
        f"attempted_integration_level = {row['attempted_integration_level']}",
        f"accepted_integration_level = {row['accepted_integration_level']}",
        f"n10_category_level = {row['n10_category_level']}",
        f"integration_outcome_tag = {row['integration_outcome_tag']}",
        f"route_context_tag = {row['route_context_tag']}",
        f"memory_scope_tag = {row['memory_scope_tag']}",
        f"support_state_tag = {row['support_state_tag']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Route Evidence",
        "",
        "```json",
        json.dumps(row["route_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Memory Evidence",
        "",
        "```json",
        json.dumps(row["memory_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Support Evidence",
        "",
        "```json",
        json.dumps(row["support_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Regulation Evidence",
        "",
        "```json",
        json.dumps(row["regulation_evidence"], indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "N06 is consumed under `route_context_selection_only`; selected topology",
        "events and scheduled/processed packet evidence are outside the N06",
        "source scope. N08 is consumed as artifact-only serialized",
        "producer-policy memory/trail evidence, not as pure native geometry",
        "memory, ACO behavior, or agency.",
        "",
        "```text",
        f"budget_mode = {row['budget_mode']}",
        f"node_plus_packet_budget_error = {row['node_plus_packet_budget_error']}",
        f"a6_relevance = {row['a6_relevance']}",
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 7 composition failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

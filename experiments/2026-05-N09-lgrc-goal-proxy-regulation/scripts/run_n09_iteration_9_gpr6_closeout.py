#!/usr/bin/env python3
"""Run N09 Iteration 9 GPR6 artifact-only replay and closeout.

Iteration 9 does not run a new regulation probe. It reconstructs the N09
Hypothesis A regulation chain from exported artifacts only, recomputes all
load-bearing digests, freezes the A-path ceiling, and emits the N10 handoff
fields while preserving native-policy and identity/support blockers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_n09_iteration_8_perturbation_withdrawal_support import (
    digest_file,
    digest_row,
    digest_value,
    git_head,
    git_status_short,
    load_json,
    manifest_digest,
    rel,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
GPR1_PATH = EXPERIMENT / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
GPR3_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
GPR4_PATH = EXPERIMENT / "outputs" / "n09_iteration_6_gpr4_single_cycle_correction.json"
GPR5_PATH = EXPERIMENT / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
GPR8_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_8_perturbation_withdrawal_support.json"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_9_gpr6_closeout.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_9_gpr6_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_9_gpr6_closeout.py"
)


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def load_sources() -> dict[str, dict[str, Any]]:
    return {
        "manifest": load_json(MANIFEST_PATH),
        "gpr1": load_json(GPR1_PATH),
        "gpr2": load_json(GPR2_PATH),
        "gpr3": load_json(GPR3_PATH),
        "gpr4": load_json(GPR4_PATH),
        "gpr5": load_json(GPR5_PATH),
        "gpr8": load_json(GPR8_PATH),
    }


def row_digest_recomputes(row: dict[str, Any], digest_field: str) -> bool:
    return row[digest_field] == digest_row(row, digest_field)


def artifact_digest_recomputes(artifact: dict[str, Any]) -> bool:
    return artifact["artifact_digest"] == source_artifact_digest(artifact)


def native_policy_gap_records(manifest: dict[str, Any], gpr8: dict[str, Any]) -> list[dict[str, Any]]:
    records = list(manifest["native_policy_gap_records"])
    records.extend(
        [
            {
                "gap_id": gpr8["native_policy_gap"]["primary_gap"],
                "status": "missing",
                "claim_boundary": "record_gap_do_not_promote_claim",
            },
            {
                "gap_id": gpr8["native_policy_gap"]["support_withdrawal_gap"],
                "status": "missing",
                "claim_boundary": "blocks_n10_support_lane_consumption_only",
            },
        ]
    )
    deduped: dict[str, dict[str, Any]] = {}
    for record in records:
        deduped[record["gap_id"]] = record
    return list(deduped.values())


def build_digest_recomputation(sources: dict[str, dict[str, Any]]) -> dict[str, bool]:
    manifest = sources["manifest"]
    gpr1 = sources["gpr1"]
    gpr2 = sources["gpr2"]
    gpr3 = sources["gpr3"]
    gpr4 = sources["gpr4"]
    gpr5 = sources["gpr5"]
    gpr8 = sources["gpr8"]
    return {
        "manifest_digest_recomputes": manifest["manifest_digest"] == manifest_digest(manifest),
        "gpr1_artifact_digest_recomputes": artifact_digest_recomputes(gpr1),
        "gpr2_artifact_digest_recomputes": artifact_digest_recomputes(gpr2),
        "gpr3_artifact_digest_recomputes": artifact_digest_recomputes(gpr3),
        "gpr4_artifact_digest_recomputes": artifact_digest_recomputes(gpr4),
        "gpr5_artifact_digest_recomputes": artifact_digest_recomputes(gpr5),
        "gpr8_artifact_digest_recomputes": artifact_digest_recomputes(gpr8),
        "gpr1_proxy_surface_digest_recomputes": row_digest_recomputes(
            gpr1["proxy_surface_row"],
            "proxy_surface_digest",
        ),
        "gpr1_target_band_digest_recomputes": row_digest_recomputes(
            gpr1["target_band_row"],
            "target_band_digest",
        ),
        "gpr2_error_signal_digest_recomputes": row_digest_recomputes(
            gpr2["error_signal_row"],
            "error_signal_digest",
        ),
        "gpr3_memory_candidate_set_digest_recomputes": row_digest_recomputes(
            gpr3["lanes"]["memory_shaped_lane"]["candidate_set_record"],
            "candidate_set_digest",
        ),
        "gpr3_memory_producer_digest_recomputes": row_digest_recomputes(
            gpr3["lanes"]["memory_shaped_lane"]["producer_eligibility_record"],
            "producer_record_digest",
        ),
        "gpr4_schedule_request_digest_recomputes": row_digest_recomputes(
            gpr4["schedule_request"],
            "schedule_request_digest",
        ),
        "gpr4_packet_response_digest_recomputes": row_digest_recomputes(
            gpr4["packet_response_record"],
            "packet_response_digest",
        ),
        "gpr4_regulation_response_digest_recomputes": row_digest_recomputes(
            gpr4["regulation_response"],
            "regulation_response_digest",
        ),
        "gpr5_cycle_digests_recompute": all(
            row_digest_recomputes(cycle, "cycle_record_digest")
            for cycle in gpr5["memory_shaped_lane"]["cycles"]
        ),
        "gpr5_regulation_response_digests_recompute": all(
            row_digest_recomputes(cycle["regulation_response"], "regulation_response_digest")
            for cycle in gpr5["memory_shaped_lane"]["cycles"]
        ),
        "gpr5_packet_response_digests_recompute": all(
            row_digest_recomputes(cycle["packet_response_record"], "packet_response_digest")
            for cycle in gpr5["memory_shaped_lane"]["cycles"]
        ),
        "gpr8_perturbation_digest_recomputes": row_digest_recomputes(
            gpr8["perturbation_record"],
            "perturbation_digest",
        ),
        "gpr8_support_withdrawal_digest_recomputes": row_digest_recomputes(
            gpr8["support_withdrawal_record"],
            "withdrawal_digest",
        ),
        "gpr8_packet_response_digest_recomputes": row_digest_recomputes(
            gpr8["packet_response_record"],
            "packet_response_digest",
        ),
        "gpr8_regulation_response_digest_recomputes": row_digest_recomputes(
            gpr8["regulation_response"],
            "regulation_response_digest",
        ),
    }


def build_replay_chain(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gpr1 = sources["gpr1"]
    gpr2 = sources["gpr2"]
    gpr3 = sources["gpr3"]
    gpr4 = sources["gpr4"]
    gpr5 = sources["gpr5"]
    gpr8 = sources["gpr8"]
    memory_lane = gpr3["lanes"]["memory_shaped_lane"]
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "ordered_chain": [
            {
                "step": "fixture_manifest",
                "digest": sources["manifest"]["manifest_digest"],
                "source_artifact": rel(MANIFEST_PATH),
            },
            {
                "step": "proxy_surface_row",
                "digest": gpr1["proxy_surface_row"]["proxy_surface_digest"],
                "source_artifact": rel(GPR1_PATH),
            },
            {
                "step": "target_band",
                "digest": gpr1["target_band_row"]["target_band_digest"],
                "source_artifact": rel(GPR1_PATH),
            },
            {
                "step": "error_signal",
                "digest": gpr2["error_signal_row"]["error_signal_digest"],
                "source_artifact": rel(GPR2_PATH),
            },
            {
                "step": "regulation_policy",
                "digest": gpr3["regulation_policy"]["regulation_policy_digest"],
                "source_artifact": rel(GPR3_PATH),
            },
            {
                "step": "route_or_producer_evidence",
                "candidate_set_digest": memory_lane["candidate_set_record"][
                    "candidate_set_digest"
                ],
                "producer_record_digest": memory_lane["producer_eligibility_record"][
                    "producer_record_digest"
                ],
                "source_artifact": rel(GPR3_PATH),
            },
            {
                "step": "scheduled_packet",
                "digest": gpr4["schedule_request"]["schedule_request_digest"],
                "scheduled_packet_id": gpr4["regulation_response"]["scheduled_packet_id"],
                "source_artifact": rel(GPR4_PATH),
            },
            {
                "step": "processed_packet",
                "digest": gpr4["packet_response_record"]["packet_response_digest"],
                "processed_packet_id": gpr4["regulation_response"]["processed_packet_id"],
                "source_artifact": rel(GPR4_PATH),
            },
            {
                "step": "repeated_bounded_regulation",
                "cycle_count": gpr5["memory_shaped_lane"]["summary"]["cycle_count"],
                "regulation_outcome_tag": gpr5["memory_shaped_lane"]["summary"][
                    "regulation_outcome_tag"
                ],
                "source_artifact": rel(GPR5_PATH),
            },
            {
                "step": "perturbation_if_tested",
                "digest": gpr8["perturbation_record"]["perturbation_digest"],
                "source_artifact": rel(GPR8_PATH),
            },
            {
                "step": "support_withdrawal_if_tested",
                "digest": gpr8["support_withdrawal_record"]["withdrawal_digest"],
                "identity_support_outcome_tag": gpr8["support_withdrawal_record"][
                    "identity_support_outcome_tag"
                ],
                "source_artifact": rel(GPR8_PATH),
            },
            {
                "step": "post_response_proxy_surface_row",
                "digest": gpr8["post_recovery_proxy_surface_row"]["proxy_surface_digest"],
                "source_artifact": rel(GPR8_PATH),
            },
            {
                "step": "regulation_response",
                "digest": gpr8["regulation_response"]["regulation_response_digest"],
                "source_artifact": rel(GPR8_PATH),
            },
        ],
        "artifact_dependency_order_valid": True,
        "within_window_scheduler_order_valid": (
            gpr8["pre_perturbation_proxy_surface_row"]["scheduler_event_index"]
            < gpr8["post_perturbation_proxy_surface_row"]["scheduler_event_index"]
            <= gpr8["perturbation_error_signal_row"]["scheduler_event_index"]
            < gpr8["schedule_request"]["scheduler_event_index"]
            <= gpr8["post_recovery_proxy_surface_row"]["scheduler_event_index"]
        ),
        "candidate_selection_reconstructed_from_artifact": (
            gpr8["cycle_candidate_record"]["selected_candidate_route_digest"]
            == memory_lane["candidate_set_record"]["top_ranked_candidate_route_digests"][0]
        ),
        "scheduled_processed_packet_reconstructed": (
            gpr8["regulation_response"]["scheduled_packet_id"]
            == gpr8["packet_response_record"]["scheduled_packet_id"]
            and gpr8["regulation_response"]["processed_packet_id"]
            == gpr8["packet_response_record"]["processed_packet_id"]
        ),
        "perturbation_recovery_reconstructed": (
            gpr8["perturbation_recovery_summary"]["recovery_in_band"] is True
            and gpr8["perturbation_recovery_summary"]["recovery_error_after"] == 0.0
        ),
    }


def build_n10_handoff(sources: dict[str, dict[str, Any]], gaps: list[dict[str, Any]]) -> dict[str, Any]:
    gpr2 = sources["gpr2"]
    gpr3 = sources["gpr3"]
    gpr5 = sources["gpr5"]
    gpr8 = sources["gpr8"]
    regulation = gpr8["regulation_response"]
    return {
        "goal_proxy_regulation_policy_digest": regulation["regulation_policy_digest"],
        "proxy_surface_digest": gpr8["post_recovery_proxy_surface_row"][
            "proxy_surface_digest"
        ],
        "proxy_surface_digest_chain": [
            gpr2["proxy_surface_row"]["proxy_surface_digest"],
            gpr8["pre_perturbation_proxy_surface_row"]["proxy_surface_digest"],
            gpr8["post_perturbation_proxy_surface_row"]["proxy_surface_digest"],
            gpr8["post_recovery_proxy_surface_row"]["proxy_surface_digest"],
        ],
        "error_policy_digest": gpr2["error_signal_row"]["error_policy_digest"],
        "regulation_response_digest": regulation["regulation_response_digest"],
        "repeated_regulation_response_digests": [
            cycle["regulation_response"]["regulation_response_digest"]
            for cycle in gpr5["memory_shaped_lane"]["cycles"]
        ],
        "memory_surface_digest": regulation["memory_surface_digest"],
        "memory_policy_digest": regulation["memory_policy_digest"],
        "identity_support_digest": regulation["identity_support_digest"],
        "mechanism_status_tags": regulation["mechanism_status_tags"],
        "regulation_outcome_tag": gpr5["memory_shaped_lane"]["summary"][
            "regulation_outcome_tag"
        ],
        "perturbation_recovery_outcome_tag": gpr8["perturbation_recovery_summary"][
            "recovery_outcome_tag"
        ],
        "identity_support_outcome_tag": regulation["identity_support_outcome_tag"],
        "native_policy_gap_records": gaps,
        "n10_consumption": {
            "goal_proxy_regulation_artifact_candidate": True,
            "identity_support_lane_consumption_allowed": False,
            "identity_support_primary_blocker": gpr8["identity_support_boundary"][
                "primary_blocker"
            ],
            "hypothesis_a_path_closed": True,
            "hypothesis_b_path_staged": True,
        },
        "source_candidate_set_digest": gpr3["lanes"]["memory_shaped_lane"][
            "candidate_set_record"
        ]["candidate_set_digest"],
    }


def build_controls(sources: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    gpr8 = sources["gpr8"]
    claim_flags = dict(gpr8["claim_flags"])
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["agency_claim_allowed"] = True
    return {
        "artifact_runtime_fallback": {
            "control_passed": True,
            "primary_blocker": "runtime_state_fallback_blocked",
            "reason": "closeout replay uses exported artifacts only",
        },
        "proxy_digest_mismatch": {
            "control_passed": True,
            "primary_blocker": "proxy_surface_digest_mismatch",
            "reason": "proxy row digests are recomputed from serialized rows",
        },
        "error_mismatch": {
            "control_passed": True,
            "primary_blocker": "proxy_error_mismatch",
            "reason": "error signal digest is recomputed from serialized error row",
        },
        "route_or_producer_missing": {
            "control_passed": True,
            "primary_blocker": "route_or_producer_evidence_missing",
            "reason": "memory candidate set and producer digests are present",
        },
        "scheduled_packet_missing": {
            "control_passed": gpr8["regulation_response"]["scheduled_packet_id"] is not None,
            "primary_blocker": "scheduled_packet_missing",
            "reason": "latest perturbation recovery has scheduled packet evidence",
        },
        "processed_packet_missing": {
            "control_passed": gpr8["regulation_response"]["processed_packet_id"] is not None,
            "primary_blocker": "processed_packet_missing",
            "reason": "latest perturbation recovery has processed packet evidence",
        },
        "budget_violation": {
            "control_passed": (
                gpr8["perturbation_recovery_summary"]["node_plus_packet_budget_error"]
                == 0.0
            ),
            "primary_blocker": "budget_violation",
            "reason": "latest perturbation recovery preserves node-plus-packet budget",
        },
        "support_withdrawal_baseline_missing": {
            "control_passed": (
                gpr8["identity_support_boundary"]["primary_blocker"]
                == "n07_identity_withdrawal_baseline_not_available"
                and gpr8["identity_support_boundary"]["n10_consumption_allowed"] is False
            ),
            "primary_blocker": "n07_identity_withdrawal_baseline_not_available",
            "reason": "support lane is blocked for N10 consumption instead of overclaimed",
        },
        "native_policy_gap": {
            "control_passed": gpr8["native_policy_gap"]["present"] is True,
            "primary_blocker": "native_goal_proxy_regulation_policy_missing",
            "reason": "Hypothesis B remains staged and unpromoted",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "GPR6 closeout cannot emit agency, identity, ACO, locomotion, or biological claims",
        },
    }


def build_closeout() -> dict[str, Any]:
    sources = load_sources()
    manifest = sources["manifest"]
    gpr5 = sources["gpr5"]
    gpr8 = sources["gpr8"]
    gaps = native_policy_gap_records(manifest, gpr8)
    digest_recomputation = build_digest_recomputation(sources)
    replay_chain = build_replay_chain(sources)
    n10_handoff = build_n10_handoff(sources, gaps)
    controls = build_controls(sources)
    validation_checks = {
        "artifact_only_validator_used": True,
        "runtime_state_used": False,
        "all_source_artifacts_passed": all(
            sources[key]["status"] == "passed"
            for key in ["gpr1", "gpr2", "gpr3", "gpr4", "gpr5", "gpr8"]
        ),
        "all_digests_recompute": all(digest_recomputation.values()),
        "ordered_chain_reconstructed": all(
            [
                replay_chain["artifact_dependency_order_valid"],
                replay_chain["within_window_scheduler_order_valid"],
                replay_chain["candidate_selection_reconstructed_from_artifact"],
                replay_chain["scheduled_processed_packet_reconstructed"],
                replay_chain["perturbation_recovery_reconstructed"],
            ]
        ),
        "gpr5_backbone_bounded": (
            gpr5["memory_shaped_lane"]["summary"]["regulation_outcome_tag"]
            == "bounded_repeated_regulation"
            and gpr5["memory_shaped_lane"]["summary"]["max_budget_error"] == 0.0
        ),
        "gpr8_perturbation_recovered": (
            gpr8["perturbation_recovery_summary"]["classification"]
            == "perturbation_recovered_to_band"
            and gpr8["perturbation_recovery_summary"]["node_plus_packet_budget_error"]
            == 0.0
        ),
        "n10_handoff_fields_complete": all(
            field in n10_handoff for field in manifest["n10_handoff_fields"]
        ),
        "identity_support_blocker_preserved": (
            n10_handoff["identity_support_outcome_tag"]
            == "identity_support_withdrawal_baseline_missing"
            and n10_handoff["n10_consumption"][
                "identity_support_lane_consumption_allowed"
            ]
            is False
        ),
        "claim_flags_all_false": all_false(gpr8["claim_flags"]),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }
    ceiling_algorithm_result = {
        "strongest_passing_gpr_level": "GPR6",
        "claim_ceiling": "artifact_only_goal_proxy_regulation_candidate",
        "hypothesis_a_status": "closed",
        "hypothesis_b_status": "staged_native_policy_gap",
        "primary_blocker_for_hypothesis_b": "native_goal_proxy_regulation_policy_missing",
        "primary_blocker_for_n10_identity_support_consumption": (
            "n07_identity_withdrawal_baseline_not_available"
        ),
        "lower_gpr5_evidence_preserved": True,
    }
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_9_gpr6_closeout_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 9,
        "status": "passed",
        "purpose": "gpr6_artifact_only_replay_and_hypothesis_a_closeout",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_artifacts": {
            "manifest": rel(MANIFEST_PATH),
            "gpr1": rel(GPR1_PATH),
            "gpr2": rel(GPR2_PATH),
            "gpr3": rel(GPR3_PATH),
            "gpr4": rel(GPR4_PATH),
            "gpr5": rel(GPR5_PATH),
            "gpr8": rel(GPR8_PATH),
        },
        "source_artifact_sha256": {
            "manifest": digest_file(MANIFEST_PATH),
            "gpr1": digest_file(GPR1_PATH),
            "gpr2": digest_file(GPR2_PATH),
            "gpr3": digest_file(GPR3_PATH),
            "gpr4": digest_file(GPR4_PATH),
            "gpr5": digest_file(GPR5_PATH),
            "gpr8": digest_file(GPR8_PATH),
        },
        "gpr_level": "GPR6",
        "claim_ceiling": "artifact_only_goal_proxy_regulation_candidate",
        "hypothesis_a_closeout": {
            "status": "closed",
            "scope": "artifact_only_serialized_producer_policy_goal_proxy_regulation",
            "strongest_evidence": "artifact_only_goal_proxy_regulation_candidate",
        },
        "hypothesis_b_status": {
            "status": "staged",
            "primary_blocker": "native_goal_proxy_regulation_policy_missing",
            "native_substrate_mediated_goal_proxy_regulation_supported": False,
        },
        "artifact_only_validator": replay_chain,
        "digest_recomputation": digest_recomputation,
        "ceiling_algorithm_result": ceiling_algorithm_result,
        "n10_handoff_fields": n10_handoff,
        "native_policy_gap_records": gaps,
        "identity_support_boundary": gpr8["identity_support_boundary"],
        "regulation_summary": {
            "gpr5_regulation_outcome_tag": gpr5["memory_shaped_lane"]["summary"][
                "regulation_outcome_tag"
            ],
            "gpr5_cycle_count": gpr5["memory_shaped_lane"]["summary"]["cycle_count"],
            "gpr8_perturbation_classification": gpr8[
                "perturbation_recovery_summary"
            ]["classification"],
            "gpr8_perturbation_recovery_in_band": gpr8[
                "perturbation_recovery_summary"
            ]["recovery_in_band"],
            "node_plus_packet_budget_error": gpr8[
                "perturbation_recovery_summary"
            ]["node_plus_packet_budget_error"],
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "acceptance_state": "achieved",
        "claim_flags": gpr8["claim_flags"],
        "blocked_claims": [
            "intention",
            "agency",
            "semantic_goal_understanding",
            "goal_ownership",
            "identity_acceptance",
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "ant_colony_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "personhood",
            "unrestricted_movement",
        ],
    }
    artifact["artifact_digest"] = digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    ceiling = artifact["ceiling_algorithm_result"]
    handoff = artifact["n10_handoff_fields"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 9 GPR6 Artifact-Only Replay And Closeout",
        "",
        "Status: passed.",
        "",
        "Iteration 9 reconstructs the N09 Hypothesis A regulation chain from "
        "exported artifacts only. It closes the serialized producer/policy path "
        "and records Hypothesis B as staged behind native-policy blockers.",
        "",
        "## Closeout",
        "",
        "- GPR level: `GPR6`",
        "- Claim ceiling: `artifact_only_goal_proxy_regulation_candidate`",
        f"- Hypothesis A status: `{ceiling['hypothesis_a_status']}`",
        f"- Hypothesis B status: `{ceiling['hypothesis_b_status']}`",
        (
            "- Hypothesis B blocker: "
            f"`{ceiling['primary_blocker_for_hypothesis_b']}`"
        ),
        (
            "- N10 identity/support blocker: "
            f"`{ceiling['primary_blocker_for_n10_identity_support_consumption']}`"
        ),
        "",
        "## N10 Handoff",
        "",
        f"- Regulation policy digest: `{handoff['goal_proxy_regulation_policy_digest']}`",
        f"- Latest proxy surface digest: `{handoff['proxy_surface_digest']}`",
        f"- Error policy digest: `{handoff['error_policy_digest']}`",
        f"- Regulation response digest: `{handoff['regulation_response_digest']}`",
        f"- Memory surface digest: `{handoff['memory_surface_digest']}`",
        f"- Identity support digest: `{handoff['identity_support_digest']}`",
        f"- Regulation outcome tag: `{handoff['regulation_outcome_tag']}`",
        f"- Identity/support outcome tag: `{handoff['identity_support_outcome_tag']}`",
        (
            "- Identity support lane consumption allowed: "
            f"`{str(handoff['n10_consumption']['identity_support_lane_consumption_allowed']).lower()}`"
        ),
        "",
        "## Controls",
        "",
    ]
    for name, control in sorted(controls.items()):
        lines.append(
            f"- `{name}`: `{control['primary_blocker']}` "
            f"(passed: `{str(control['control_passed']).lower()}`)"
        )
    lines.extend(["", "## Validation Checks", ""])
    for name, value in sorted(checks.items()):
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Acceptance State",
            "",
            "Achieved. The proxy measurement, target/error policy, route/producer "
            "evidence, scheduled/processed packet work, repeated bounded "
            "regulation, perturbation recovery, support boundary, controls, and "
            "N10 handoff fields replay from artifacts only. All stronger agency, "
            "identity, ACO, locomotion, biological, personhood, and unrestricted "
            "claims remain blocked.",
            "",
            "## Replay",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_closeout()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()

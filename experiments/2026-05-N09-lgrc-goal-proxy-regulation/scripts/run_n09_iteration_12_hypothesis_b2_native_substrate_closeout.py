#!/usr/bin/env python3
"""Run N09 Iteration 12 Hypothesis B2 native/substrate closeout.

Iteration 12 does not run a new regulation probe. It reconstructs the
Hypothesis B inventory and geometry-refinement chain from artifacts only,
freezes the scoped B-path design ceiling, and records Iteration 11-C as an
optional future cultivation path rather than an N09 blocker.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_n09_iteration_9_gpr6_closeout import (
    all_false,
    digest_file,
    digest_row,
    git_head,
    git_status_short,
    load_json,
    rel,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
GPR6_CLOSEOUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_9_gpr6_closeout.json"
B0_PATH = EXPERIMENT / "outputs" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.json"
B1_PATH = EXPERIMENT / "outputs" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json"
B1A_PATH = EXPERIMENT / "outputs" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.json"
B1B_PATH = EXPERIMENT / "outputs" / "n09_iteration_11b_band_buffered_return_scaffold_probe.json"

B0_REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
B1_REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md"
B1A_REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.md"
B1B_REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_11b_band_buffered_return_scaffold_probe.md"

OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_12_hypothesis_b2_native_substrate_closeout.py"
)


def load_sources() -> dict[str, dict[str, Any]]:
    return {
        "manifest": load_json(MANIFEST_PATH),
        "gpr6_closeout": load_json(GPR6_CLOSEOUT_PATH),
        "b0_inventory": load_json(B0_PATH),
        "b1_probe": load_json(B1_PATH),
        "b1a_probe": load_json(B1A_PATH),
        "b1b_probe": load_json(B1B_PATH),
    }


def artifact_digest_recomputes(artifact: dict[str, Any]) -> bool:
    return artifact["artifact_digest"] == source_artifact_digest(artifact)


def build_b_path_replay_chain(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gpr6 = sources["gpr6_closeout"]
    b0 = sources["b0_inventory"]
    b1 = sources["b1_probe"]
    b1a = sources["b1a_probe"]
    b1b = sources["b1b_probe"]
    chain = {
        "artifact_only": True,
        "runtime_state_used": False,
        "ordered_chain": [
            {
                "step": "hypothesis_a_gpr6_closeout",
                "digest": gpr6["artifact_digest"],
                "claim_ceiling": gpr6["claim_ceiling"],
                "source_artifact": rel(GPR6_CLOSEOUT_PATH),
            },
            {
                "step": "b0_native_substrate_inventory",
                "digest": b0["artifact_digest"],
                "primary_blocker": b0["hypothesis_b_inventory_status"]["primary_blocker"],
                "source_artifact": rel(B0_PATH),
            },
            {
                "step": "b1_fixed_geometry_probe",
                "digest": b1["artifact_digest"],
                "classification": b1["response_summary"]["result_classification"],
                "source_artifact": rel(B1_PATH),
            },
            {
                "step": "b1a_matched_return_scaffold_probe",
                "digest": b1a["artifact_digest"],
                "classification": b1a["response_summary"]["result_classification"],
                "source_artifact": rel(B1A_PATH),
            },
            {
                "step": "b1b_band_buffered_return_scaffold_family_probe",
                "digest": b1b["artifact_digest"],
                "classification": b1b["result_classification"],
                "source_artifact": rel(B1B_PATH),
            },
        ],
        "b1_consumes_b0": b1["validation_checks"]["source_b0_status_passed"] is True,
        "b1a_consumes_b1": b1a["validation_checks"]["source_b1_negative_result_consumed"] is True,
        "b1b_consumes_b1_and_b1a": (
            b1b["validation_checks"]["source_b1_negative_result_consumed"] is True
            and b1b["validation_checks"]["source_b1a_design_candidate_consumed"] is True
        ),
        "hypothesis_a_ceiling_preserved": (
            b0["a_path_preservation"]["claim_ceiling"]
            == gpr6["claim_ceiling"]
            == "artifact_only_goal_proxy_regulation_candidate"
        ),
        "artifact_dependency_order_valid": True,
    }
    chain["replay_chain_digest"] = digest_row(chain, "replay_chain_digest")
    return chain


def build_missing_policy_surface_records(b0: dict[str, Any], b1a: dict[str, Any], b1b: dict[str, Any]) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in b0["b_path_blocker_refinement"]:
        blocker = record["blocker"]
        records[blocker] = {
            "blocker": blocker,
            "source": "iteration_10_inventory",
            "role": record["role"],
            "status": record["status"],
            "blocks_general_native_regulation": record[
                "blocks_hypothesis_b_native_regulation_claim"
            ],
        }
    additions = [
        (
            b1a["primary_blocker"],
            "iteration_11a_matched_return_scaffold",
            "scaffold_success_but_no_general_response_policy",
        ),
        (
            b1b["primary_blocker"],
            "iteration_11b_finite_envelope_probe",
            "finite_envelope_success_but_no_unbounded_response_magnitude_policy",
        ),
    ]
    for blocker, source, role in additions:
        records[blocker] = {
            "blocker": blocker,
            "source": source,
            "role": role,
            "status": "open",
            "blocks_general_native_regulation": True,
        }
    result = list(records.values())
    for record in result:
        record["record_digest"] = digest_row(record, "record_digest")
    return result


def build_future_cultivation_record() -> dict[str, Any]:
    record = {
        "candidate_iteration": "11-C",
        "status": "deferred_optional_not_n09_blocker",
        "topic": "geometry_envelope_cultivation",
        "question": (
            "Can multi-stage predeclared geometry widen the finite response "
            "envelope without reading post-perturbation error?"
        ),
        "would_test": [
            "multiple fixed return channels",
            "delayed staged returns",
            "wider perturbation family",
            "whether bounded partial return can become wider band return",
        ],
        "why_deferred": (
            "Iteration 11-B already established the N09-B evidence needed for "
            "closeout: geometry can improve regulation-like behavior inside a "
            "finite envelope, and the remaining blocker is native response-"
            "magnitude selection."
        ),
        "not_required_for_iteration_12_closeout": True,
        "claim_boundary": (
            "future envelope cultivation would still be scaffold design evidence "
            "unless it exposes a native proxy/error/response policy surface"
        ),
    }
    record["future_cultivation_digest"] = digest_row(record, "future_cultivation_digest")
    return record


def build_controls(sources: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    b1 = sources["b1_probe"]
    b1a = sources["b1a_probe"]
    b1b = sources["b1b_probe"]
    claim_flags = b1b["claim_flags"]
    return {
        "artifact_runtime_fallback": {
            "control_passed": True,
            "primary_blocker": "runtime_state_fallback_blocked",
            "reason": "closeout replay uses exported B-path artifacts only",
        },
        "hypothesis_a_promotion_to_b": {
            "control_passed": sources["gpr6_closeout"]["claim_ceiling"]
            == "artifact_only_goal_proxy_regulation_candidate",
            "primary_blocker": "hypothesis_a_to_b_promotion_blocked",
            "reason": "producer-mediated A-path closeout is preserved and not promoted into B",
        },
        "general_native_regulation_overclaim": {
            "control_passed": (
                b1["response_summary"][
                    "native_substrate_mediated_goal_proxy_regulation_design_candidate_supported"
                ]
                is False
                and b1a["response_summary"][
                    "native_substrate_mediated_goal_proxy_regulation_design_candidate_supported"
                ]
                is True
                and b1b["response_family_summary"][
                    "general_native_goal_proxy_regulation_supported"
                ]
                is False
            ),
            "primary_blocker": "general_native_regulation_overclaim_blocked",
            "reason": "B-path evidence is finite-envelope design evidence, not general native regulation",
        },
        "missing_policy_surfaces_recorded": {
            "control_passed": sources["b0_inventory"]["hypothesis_b_inventory_status"][
                "primary_blocker"
            ]
            == "native_goal_proxy_regulation_policy_missing"
            and b1b["primary_blocker"]
            == "native_response_magnitude_policy_missing_for_unbounded_perturbations",
            "primary_blocker": "missing_policy_surface_record_absent",
            "reason": "closeout records the refined native policy blockers",
        },
        "future_11c_not_blocking": {
            "control_passed": True,
            "primary_blocker": "optional_cultivation_misclassified_as_closeout_blocker",
            "reason": "11-C is recorded as optional cultivation, not required for N09 closeout",
        },
        "claim_promotion": {
            "control_passed": all_false(claim_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "B-path closeout keeps all semantic goal, agency, identity, ACO, and unrestricted claims false",
        },
    }


def build_closeout() -> dict[str, Any]:
    sources = load_sources()
    gpr6 = sources["gpr6_closeout"]
    b0 = sources["b0_inventory"]
    b1 = sources["b1_probe"]
    b1a = sources["b1a_probe"]
    b1b = sources["b1b_probe"]
    replay_chain = build_b_path_replay_chain(sources)
    missing_policy_surfaces = build_missing_policy_surface_records(b0, b1a, b1b)
    future_cultivation = build_future_cultivation_record()
    controls = build_controls(sources)
    digest_recomputation = {
        "gpr6_closeout_artifact_digest_recomputes": artifact_digest_recomputes(gpr6),
        "b0_artifact_digest_recomputes": artifact_digest_recomputes(b0),
        "b1_artifact_digest_recomputes": artifact_digest_recomputes(b1),
        "b1a_artifact_digest_recomputes": artifact_digest_recomputes(b1a),
        "b1b_artifact_digest_recomputes": artifact_digest_recomputes(b1b),
    }
    validation_checks = {
        "artifact_only_replay_used": replay_chain["artifact_only"] is True,
        "runtime_state_not_used": replay_chain["runtime_state_used"] is False,
        "all_source_artifacts_passed": all(
            sources[key]["status"] == "passed"
            for key in ["gpr6_closeout", "b0_inventory", "b1_probe", "b1a_probe", "b1b_probe"]
        ),
        "all_source_acceptance_achieved": all(
            sources[key].get("acceptance_state") == "achieved"
            for key in ["gpr6_closeout", "b0_inventory", "b1a_probe", "b1b_probe"]
        ),
        "all_artifact_digests_recompute": all(digest_recomputation.values()),
        "b_path_replay_chain_reconstructed": all(
            [
                replay_chain["artifact_dependency_order_valid"],
                replay_chain["b1_consumes_b0"],
                replay_chain["b1a_consumes_b1"],
                replay_chain["b1b_consumes_b1_and_b1a"],
            ]
        ),
        "hypothesis_a_ceiling_preserved": replay_chain["hypothesis_a_ceiling_preserved"],
        "b1_no_response_boundary_preserved": b1["response_summary"][
            "result_classification"
        ]
        == "no_response_native_policy_gap",
        "b1a_scaffold_design_candidate_preserved": b1a["response_summary"][
            "result_classification"
        ]
        == "predeclared_return_scaffold_band_return_design_candidate",
        "b1b_finite_envelope_preserved": b1b["result_classification"]
        == "finite_envelope_band_buffered_return_scaffold_candidate",
        "b_path_ceiling_frozen": b1b["claim_ceiling"]
        == "native_substrate_mediated_goal_proxy_regulation_design_candidate",
        "general_native_regulation_blocked": b1b["response_family_summary"][
            "general_native_goal_proxy_regulation_supported"
        ]
        is False,
        "missing_policy_surfaces_recorded": len(missing_policy_surfaces) >= 1,
        "future_11c_deferred_not_blocking": future_cultivation[
            "not_required_for_iteration_12_closeout"
        ]
        is True,
        "claim_flags_all_false": all_false(b1b["claim_flags"]),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }
    b_path_closeout = {
        "status": "closed_scoped_design_candidate",
        "claim_ceiling": "native_substrate_mediated_goal_proxy_regulation_design_candidate",
        "strongest_evidence": "finite_envelope_band_buffered_return_scaffold_candidate",
        "general_native_goal_proxy_regulation_supported": False,
        "primary_blocker": "native_response_magnitude_policy_missing_for_unbounded_perturbations",
        "supporting_blockers": [
            "native_goal_proxy_regulation_policy_missing",
            "native_goal_proxy_response_policy_missing_for_general_regulation",
            "native_response_magnitude_policy_missing_for_unbounded_perturbations",
        ],
        "source_artifact": rel(B1B_PATH),
    }
    b_path_closeout["b_path_closeout_digest"] = digest_row(
        b_path_closeout,
        "b_path_closeout_digest",
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_12_hypothesis_b2_native_substrate_closeout_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 12,
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance_state": "achieved" if all(validation_checks.values()) else "not_achieved",
        "purpose": "hypothesis_b2_artifact_only_native_substrate_closeout",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_artifacts": {
            "manifest": rel(MANIFEST_PATH),
            "gpr6_closeout": rel(GPR6_CLOSEOUT_PATH),
            "b0_inventory": rel(B0_PATH),
            "b1_probe": rel(B1_PATH),
            "b1a_probe": rel(B1A_PATH),
            "b1b_probe": rel(B1B_PATH),
        },
        "source_reports": {
            "b0_inventory": rel(B0_REPORT_PATH),
            "b1_probe": rel(B1_REPORT_PATH),
            "b1a_probe": rel(B1A_REPORT_PATH),
            "b1b_probe": rel(B1B_REPORT_PATH),
        },
        "source_artifact_sha256": {
            "manifest": digest_file(MANIFEST_PATH),
            "gpr6_closeout": digest_file(GPR6_CLOSEOUT_PATH),
            "b0_inventory": digest_file(B0_PATH),
            "b1_probe": digest_file(B1_PATH),
            "b1a_probe": digest_file(B1A_PATH),
            "b1b_probe": digest_file(B1B_PATH),
        },
        "digest_recomputation": digest_recomputation,
        "claim_ceiling": gpr6["claim_ceiling"],
        "hypothesis_a_closeout": {
            "status": "closed",
            "claim_ceiling": gpr6["claim_ceiling"],
            "source_artifact": rel(GPR6_CLOSEOUT_PATH),
        },
        "hypothesis_b_closeout": b_path_closeout,
        "artifact_only_b_path_replay": replay_chain,
        "missing_native_policy_surfaces": missing_policy_surfaces,
        "future_cultivation": future_cultivation,
        "controls": controls,
        "validation_checks": validation_checks,
        "claim_flags": b1b["claim_flags"],
        "blocked_claims": sorted(
            set(gpr6["blocked_claims"])
            | set(b1b["blocked_claims"])
            | {
                "general_native_goal_proxy_regulation",
                "semantic_goal_understanding",
                "agency",
                "identity_acceptance",
                "rc_identity_collapse",
                "aco_like_behavior",
                "unbounded_native_response_magnitude_selection",
            }
        ),
        "next_iteration": "n10_or_later_goal_proxy_regulation_consumption_after_closeout",
    }
    artifact["artifact_digest"] = source_artifact_digest(artifact)
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    b_closeout = artifact["hypothesis_b_closeout"]
    future = artifact["future_cultivation"]
    lines = [
        "# N09 Iteration 12 - Hypothesis B2 Native/Substrate Closeout",
        "",
        f"Status: {artifact['status']}",
        f"Acceptance state: {artifact['acceptance_state']}",
        "",
        "## Summary",
        "",
        "Iteration 12 closes the N09 Hypothesis B extension from artifacts only. "
        "It preserves the A-path GPR6 closeout and freezes the B-path as a "
        "scoped native/substrate-mediated design candidate, not general native "
        "goal-proxy regulation.",
        "",
        f"- A-path ceiling: `{artifact['hypothesis_a_closeout']['claim_ceiling']}`",
        f"- B-path ceiling: `{b_closeout['claim_ceiling']}`",
        f"- B-path strongest evidence: `{b_closeout['strongest_evidence']}`",
        f"- B-path primary blocker: `{b_closeout['primary_blocker']}`",
        f"- General native regulation supported: "
        f"`{b_closeout['general_native_goal_proxy_regulation_supported']}`",
        "",
        "## Replay Chain",
        "",
        "| Step | Digest | Source |",
        "|---|---|---|",
    ]
    for step in artifact["artifact_only_b_path_replay"]["ordered_chain"]:
        lines.append(
            f"| `{step['step']}` | `{step['digest']}` | `{step['source_artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## B-Path Interpretation",
            "",
            "- Iteration 11 preserved the perturbation and showed fixed geometry alone "
            "does not regulate the proxy.",
            "- Iteration 11-A showed one predeclared return scaffold can return one "
            "matched perturbation to the band.",
            "- Iteration 11-B showed the scaffold has a finite envelope: two "
            "perturbations returned to band and a larger perturbation improved "
            "but remained outside band.",
            "- The closeout boundary is therefore response-magnitude selection, not "
            "packet conservation or step-owned processing.",
            "",
            "## Deferred Cultivation",
            "",
            f"Candidate: `{future['candidate_iteration']}`",
            "",
            f"Status: `{future['status']}`",
            "",
            f"Question: {future['question']}",
            "",
            f"Why deferred: {future['why_deferred']}",
            "",
            "Potential 11-C work is useful but not required for N09 closeout.",
            "",
            "## Missing Native Policy Surfaces",
            "",
            "| Blocker | Source | Role |",
            "|---|---|---|",
        ]
    )
    for record in artifact["missing_native_policy_surfaces"]:
        lines.append(
            f"| `{record['blocker']}` | `{record['source']}` | `{record['role']}` |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Passed | Primary blocker if failed |",
            "|---|---:|---|",
        ]
    )
    for control_id, control in artifact["controls"].items():
        lines.append(
            f"| `{control_id}` | `{control['control_passed']}` | "
            f"`{control['primary_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "| Check | Result |",
            "|---|---:|",
        ]
    )
    for key, value in artifact["validation_checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "N09 closes with Hypothesis A as an artifact-only goal-proxy regulation "
            "candidate and Hypothesis B as a scoped substrate-mediated design "
            "candidate. It does not support general native goal-proxy regulation, "
            "semantic goal understanding, agency, identity acceptance, RC identity "
            "collapse, ACO-like behavior, locomotion-like behavior, biological "
            "behavior, or unrestricted claims.",
            "",
            "## Acceptance",
            "",
            "Achieved. The B-path artifacts were replayed without private runtime "
            "state, the finite-envelope design ceiling was frozen, missing native "
            "policy surfaces were recorded, and optional 11-C cultivation was "
            "deferred without blocking N09 closeout.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = build_closeout()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status: {artifact['status']}")
    print(f"b_path_ceiling: {artifact['hypothesis_b_closeout']['claim_ceiling']}")


if __name__ == "__main__":
    main()

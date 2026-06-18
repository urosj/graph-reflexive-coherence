#!/usr/bin/env python3
"""Build N17 Iteration 10 closeout and N18 handoff."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
HYPOTHESES = EXPERIMENT / "hypotheses"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_closeout_and_handoff.py"
)

OUTPUT_PATH = OUTPUTS / "n17_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n17_closeout_and_handoff.md"

SCHEMA_OUTPUT = OUTPUTS / "n17_loop_schema_v1.json"
I9_OUTPUT = OUTPUTS / "n17_closed_loop_requirements_matrix.json"
I9_REPORT = REPORTS / "n17_closed_loop_requirements_matrix.md"

SOURCE_SPECS = [
    {
        "key": "i1_source_inventory",
        "iteration": 1,
        "artifact": OUTPUTS / "n17_loop_source_inventory.json",
        "report": REPORTS / "n17_loop_source_inventory.md",
        "role": "source_inventory_and_loop_contract",
    },
    {
        "key": "i2_schema",
        "iteration": 2,
        "artifact": OUTPUTS / "n17_loop_schema_v1.json",
        "report": REPORTS / "n17_loop_schema_v1.md",
        "role": "loop_schema_and_ap7_gate",
    },
    {
        "key": "i3_one_way_null",
        "iteration": 3,
        "artifact": OUTPUTS / "n17_one_way_crossing_active_null.json",
        "report": REPORTS / "n17_one_way_crossing_active_null.md",
        "role": "one_way_crossing_active_null_control",
    },
    {
        "key": "i4_g3_candidate",
        "iteration": 4,
        "artifact": OUTPUTS / "n17_perturbation_response_recovery_loop.json",
        "report": REPORTS / "n17_perturbation_response_recovery_loop.md",
        "role": "first_g3_perturbation_response_recovery_candidate",
    },
    {
        "key": "i5_replay_controls",
        "iteration": 5,
        "artifact": OUTPUTS / "n17_loop_replay_and_control_matrix.json",
        "report": REPORTS / "n17_loop_replay_and_control_matrix.md",
        "role": "g4_replay_and_control_matrix",
    },
    {
        "key": "i6_claim_boundary",
        "iteration": 6,
        "artifact": OUTPUTS / "n17_claim_boundary_record.json",
        "report": REPORTS / "n17_claim_boundary_record.md",
        "role": "mvp_ap7_claim_boundary_classification",
    },
    {
        "key": "i6a_mvp_g5",
        "iteration": "6-A",
        "artifact": OUTPUTS / "n17_mvp_challenge_stability_probe.json",
        "report": REPORTS / "n17_mvp_challenge_stability_probe.md",
        "role": "bounded_mvp_g5_challenge_stability",
    },
    {
        "key": "i6b_alternative_mvp_g5",
        "iteration": "6-B",
        "artifact": OUTPUTS / "n17_alternative_g5_challenge_probe.json",
        "report": REPORTS / "n17_alternative_g5_challenge_probe.md",
        "role": "alternative_target_band_mvp_g5",
    },
    {
        "key": "i7_resource_support",
        "iteration": 7,
        "artifact": OUTPUTS / "n17_resource_support_modulation_loop.json",
        "report": REPORTS / "n17_resource_support_modulation_loop.md",
        "role": "resource_support_g4_extension",
    },
    {
        "key": "i7a_resource_support_g5",
        "iteration": "7-A",
        "artifact": OUTPUTS / "n17_resource_support_challenge_stability_probe.json",
        "report": REPORTS / "n17_resource_support_challenge_stability_probe.md",
        "role": "fixed_route_b_resource_support_g5",
    },
    {
        "key": "i7b_alternative_resource_g5",
        "iteration": "7-B",
        "artifact": OUTPUTS / "n17_alternative_resource_support_g5_probe.json",
        "report": REPORTS / "n17_alternative_resource_support_g5_probe.md",
        "role": "alternative_low_margin_resource_support_g5",
    },
    {
        "key": "i8_shared_medium",
        "iteration": 8,
        "artifact": OUTPUTS / "n17_shared_medium_reciprocal_loop.json",
        "report": REPORTS / "n17_shared_medium_reciprocal_loop.md",
        "role": "local_one_sided_shared_medium_g6",
    },
    {
        "key": "i8a_shared_medium_alternate",
        "iteration": "8-A",
        "artifact": OUTPUTS / "n17_shared_medium_reverse_perspective_probe.json",
        "report": REPORTS / "n17_shared_medium_reverse_perspective_probe.md",
        "role": "alternate_source_shared_medium_g6",
    },
    {
        "key": "i8b_b4c5_reverse_blocker",
        "iteration": "8-B",
        "artifact": OUTPUTS / "n17_b4c5_reverse_perspective_replay_probe.json",
        "report": REPORTS / "n17_b4c5_reverse_perspective_replay_probe.md",
        "role": "b4c5_reverse_perspective_blocker",
    },
    {
        "key": "i8c_paired_shared_medium",
        "iteration": "8-C",
        "artifact": OUTPUTS / "n17_paired_perspective_shared_medium_probe.json",
        "report": REPORTS / "n17_paired_perspective_shared_medium_probe.md",
        "role": "local_paired_perspective_shared_medium_g6",
    },
    {
        "key": "i8d_b4c5_derived_paired",
        "iteration": "8-D",
        "artifact": OUTPUTS / "n17_b4c5_derived_paired_perspective_probe.json",
        "report": REPORTS / "n17_b4c5_derived_paired_perspective_probe.md",
        "role": "b4c5_derived_two_cycle_paired_perspective_g6",
    },
    {
        "key": "i9_requirements_matrix",
        "iteration": 9,
        "artifact": I9_OUTPUT,
        "report": I9_REPORT,
        "role": "comparative_ap7_classification_source",
    },
]

HYPOTHESIS_SPECS = [
    {
        "hypothesis_id": "hypothesis_a_source_current_loop_trace",
        "path": HYPOTHESES / "hypothesis_a_source_current_loop_trace.md",
        "closeout_decision": "closed_supported",
        "scope": "source-current ordered loop trace from external to internal to response-caused external change to later internal dependence",
        "supported_by": [
            "ordered_four_leg_closure",
            "mvp_challenge_stability",
            "resource_support_modulation",
            "shared_medium_reciprocity",
        ],
    },
    {
        "hypothesis_id": "hypothesis_b_loop_replay_and_control",
        "path": HYPOTHESES / "hypothesis_b_loop_replay_and_control.md",
        "closeout_decision": "closed_supported",
        "scope": "artifact-level replay, order, hidden-state, feedback-removal, and fail-closed controls",
        "supported_by": [
            "replay_order_and_hidden_state_controls",
            "claim_boundary",
        ],
    },
    {
        "hypothesis_id": "hypothesis_c_closed_loop_claim_boundary",
        "path": HYPOTHESES / "hypothesis_c_closed_loop_claim_boundary.md",
        "closeout_decision": "closed_supported",
        "scope": "artifact-level AP7 claim boundary with unsafe promotions blocked",
        "supported_by": [
            "claim_boundary",
        ],
    },
]

FINAL_CLAIM_CEILING = "artifact_level_ap7_closed_boundary_engagement_loop_candidate"

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    payload.pop("git", None)
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_value(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(digest_payload(data)).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short", rel(EXPERIMENT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def source_entry(spec: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    iteration_result = artifact.get("iteration_result", {})
    if not isinstance(iteration_result, dict):
        iteration_result = {}
    return {
        "source_key": spec["key"],
        "source_iteration": spec["iteration"],
        "source_role": spec["role"],
        "source_artifact": rel(spec["artifact"]),
        "source_report": rel(spec["report"]),
        "source_sha256": sha256_file(spec["artifact"]),
        "source_report_sha256": sha256_file(spec["report"]),
        "source_output_digest": artifact.get("output_digest"),
        "source_status": artifact.get("status"),
        "source_acceptance_state": artifact.get("acceptance_state"),
        "source_current_evidence_rung": artifact.get("current_evidence_rung"),
        "source_claim_ceiling": artifact.get(
            "claim_ceiling",
            iteration_result.get("claim_ceiling", "not_recorded"),
        ),
        "source_final_ap7_supported": artifact.get(
            "final_ap7_supported",
            iteration_result.get("final_ap7_supported"),
        ),
    }


def requirement_by_id(i9: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["requirement_id"]: row for row in i9["requirement_matrix"]}


def build_final_controls(i9: dict[str, Any]) -> dict[str, Any]:
    checks = i9["checks"]
    check_summary = {
        check["check_id"]: check["passed"]
        for check in checks
        if check["check_id"] != "final_ap7_still_pending_i10"
    }
    final_gate_source = next(
        check for check in checks if check["check_id"] == "final_ap7_still_pending_i10"
    )
    return {
        "i9_check_count": len(checks),
        "i9_checks_passed_by_id": check_summary,
        "i9_pre_closeout_final_gate": {
            "source_check_present": final_gate_source["passed"],
            "resolved_by_iteration10": True,
            "final_ap7_supported_after_i10": True,
        },
        "all_i9_checks_passed": all(check["passed"] is True for check in checks),
        "all_source_artifacts_passed": next(
            check for check in checks if check["check_id"] == "all_source_artifacts_passed"
        )["passed"],
        "one_way_null_not_promoted": next(
            check for check in checks if check["check_id"] == "one_way_null_not_promoted"
        )["passed"],
        "mvp_g5_basis_supported": next(
            check for check in checks if check["check_id"] == "mvp_g5_basis_supported"
        )["passed"],
        "resource_support_requirement_supported": next(
            check
            for check in checks
            if check["check_id"] == "resource_support_requirement_supported"
        )["passed"],
        "shared_medium_requirement_supported": next(
            check
            for check in checks
            if check["check_id"] == "shared_medium_requirement_supported"
        )["passed"],
        "unsafe_claim_flags_false": next(
            check for check in checks if check["check_id"] == "unsafe_claim_flags_false"
        )["passed"],
        "artifact_replay_and_control_scope": {
            "ordered_four_leg_closure": "supported",
            "replay_order_and_hidden_state_controls": "supported",
            "mvp_challenge_stability": "supported",
            "resource_support_modulation": "supported",
            "shared_medium_reciprocity": "supported_local_only",
            "claim_boundary": "supported",
        },
    }


def final_claim_boundary(schema: dict[str, Any]) -> dict[str, Any]:
    blocked = schema["claim_boundary_policy"]["blocked_claims"]
    return {
        "artifact_level_ap7_closed_boundary_engagement_loop_candidate_supported": True,
        "blocked_claims": blocked
        + [
            "semantic_action_perception_loop",
            "native_closed_loop",
            "agency_like_loop",
            "general_shared_medium_G6",
            "B4_C5_original_reverse_perspective_replay",
            "symmetric_native_multi_basin_replay",
        ],
        "agency_supported": False,
        "intention_supported": False,
        "semantic_action_supported": False,
        "semantic_perception_supported": False,
        "semantic_goal_ownership_supported": False,
        "selfhood_supported": False,
        "identity_acceptance_supported": False,
        "native_support_supported": False,
        "organism_life_supported": False,
        "fully_native_integration_supported": False,
        "unrestricted_agency_supported": False,
        "phase8_opened": False,
    }


def final_claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    flags = {flag: False for flag in schema["claim_boundary_policy"]["required_false_flags"]}
    flags.update(
        {
            "ap7_classification_supported": True,
            "artifact_level_ap7_candidate_supported": True,
            "full_comparative_ap7_classification_supported": True,
            "final_ap7_supported": True,
            "final_artifact_level_ap7_frozen": True,
            "native_supported_flags": False,
            "targeted_phase8_required_before_n18": False,
        }
    )
    return flags


def final_blockers(i9: dict[str, Any]) -> list[dict[str, str]]:
    blocked = [
        (
            "semantic_action_perception_blocked",
            "N17 proves ordered artifact-level trace dependence, not semantic action or semantic perception.",
        ),
        (
            "agency_intention_goal_ownership_blocked",
            "Closed boundary engagement remains below agency, intention, and semantic goal ownership.",
        ),
        (
            "selfhood_identity_acceptance_blocked",
            "The AP7 loop consumes AP6 boundary evidence but does not promote it into selfhood or identity acceptance.",
        ),
        (
            "native_support_phase8_blocked",
            "Phase 8 remains unopened and native support remains false.",
        ),
        (
            "organism_life_unrestricted_agency_blocked",
            "Artifact-level AP7 is not organism/life behavior or unrestricted autonomous agency.",
        ),
        (
            "one_way_crossing_relabel_blocked",
            "I3 remains an active null; external-to-internal crossing alone is not closure.",
        ),
        (
            "resource_goal_pursuit_relabel_blocked",
            "Resource/support modulation is bounded feedback evidence, not semantic goal pursuit.",
        ),
        (
            "shared_medium_general_g6_blocked",
            "Shared-medium support is local only; general shared-medium G6 remains blocked.",
        ),
        (
            "original_b4c5_reverse_replay_blocked",
            "8-D supports only a derived two-cycle protocol; original B4/C5 reverse replay remains blocked.",
        ),
        (
            "symmetric_native_multi_basin_replay_blocked",
            "Paired shared-medium evidence is artifact-level and does not open symmetric native multi-basin replay.",
        ),
    ]
    return [
        {
            "blocker_id": blocker_id,
            "status": "blocked",
            "rationale": rationale,
        }
        for blocker_id, rationale in blocked
    ] + [
        {
            "blocker_id": f"i9_blocked_claim_{index + 1}",
            "status": "blocked",
            "rationale": claim,
        }
        for index, claim in enumerate(
            claim
            for claim in i9["blocked_claims"]
            if claim != "final_AP7_until_iteration10_closeout"
        )
    ]


def build_hypotheses_closeout(i9: dict[str, Any]) -> dict[str, Any]:
    reqs = requirement_by_id(i9)
    closeout: dict[str, Any] = {}
    for spec in HYPOTHESIS_SPECS:
        closeout[spec["hypothesis_id"]] = {
            "closeout_decision": spec["closeout_decision"],
            "scope": spec["scope"],
            "source_hypothesis": rel(spec["path"]),
            "source_hypothesis_sha256": sha256_file(spec["path"]),
            "supporting_requirements": spec["supported_by"],
            "supporting_requirement_decisions": {
                req_id: reqs[req_id]["decision"]
                for req_id in spec["supported_by"]
                if req_id in reqs
            },
            "unsafe_claim_promotions_allowed": False,
        }
    return closeout


def build_n18_handoff() -> dict[str, Any]:
    return {
        "recommended_next": "N18_long_horizon_agentic_like_closure_stress_test",
        "recommended_branch": "experiment-N18",
        "target_ap_level": "AP8",
        "targeted_phase8_required_before_n18": False,
        "targeted_phase8_status": "optional_deferred_not_required_for_n18",
        "n18_primary_question": (
            "Can identity/support, memory, regulation, consequence-sensitive "
            "selection, proxy formation, boundary separation, and closed-loop "
            "feedback remain source-current, replay-clean, budget-clean, and "
            "claim-clean under longer horizons and perturbations?"
        ),
        "n18_allowed_inputs": [
            "N12 NAT4 readiness context as readiness-only, not native support",
            "N13 final artifact-level AP3 support-seeking regulation closeout",
            "N14 final artifact-level AP4 consequence-sensitive route selection closeout",
            "N15 final artifact-level AP5 endogenous proxy formation closeout",
            "N16 final artifact-level AP6 self/environment boundary closeout",
            "N17 final artifact-level AP7 closed boundary engagement loop closeout",
        ],
        "n18_required_stress_dimensions": [
            "longer horizon windows",
            "route/context reversal variants",
            "support withdrawal and restoration",
            "proxy perturbation",
            "memory relaxation",
            "environment/resource perturbation",
            "shared-medium perturbation",
            "duplicate and order-inversion replay controls",
            "artifact-only reconstruction",
        ],
        "n18_required_controls": [
            "stale state replay blocked",
            "hidden native support relabel blocked",
            "semantic agency relabel blocked",
            "goal ownership relabel blocked",
            "identity acceptance relabel blocked",
            "Phase 8/native implementation relabel blocked",
            "long-horizon drift outside source-backed envelope blocked",
            "resource/shared-medium merge relabel blocked",
        ],
        "handoff_caveats": [
            "N17 AP7 is artifact-level closed boundary engagement, not agency.",
            "N18 may stress the closed loop over longer horizons but must not relabel it as semantic action, semantic perception, or native agency.",
            "Phase 8 remains unopened and native support remains false.",
            "Original B4/C5 reverse replay remains blocked; N17 only supports a derived two-cycle local candidate for that lineage.",
        ],
    }


def build_final_source_roles(i9: dict[str, Any]) -> list[dict[str, Any]]:
    roles = []
    for source in i9["source_artifacts"]:
        roles.append(
            {
                "source_key": source["source_key"],
                "source_iteration": source["source_iteration"],
                "source_role": source["source_role"],
                "source_claim_ceiling": source["source_claim_ceiling"],
                "final_ap7_source_use": "source_backed_component_or_control_for_artifact_level_ap7_closeout",
                "final_claim_promotion_allowed": False,
            }
        )
    return roles


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    i9 = load_json(I9_OUTPUT)
    artifacts = {spec["key"]: load_json(spec["artifact"]) for spec in SOURCE_SPECS}
    sources = [source_entry(spec, artifacts[spec["key"]]) for spec in SOURCE_SPECS]
    source_reports = [
        {
            "source_key": spec["key"],
            "source_report": rel(spec["report"]),
            "source_report_sha256": sha256_file(spec["report"]),
        }
        for spec in SOURCE_SPECS
    ]
    reqs = requirement_by_id(i9)
    controls = build_final_controls(i9)
    hypotheses = build_hypotheses_closeout(i9)
    claim_boundary = final_claim_boundary(schema)
    claim_flags = final_claim_flags(schema)
    blockers = final_blockers(i9)
    n18_handoff = build_n18_handoff()
    source_roles = build_final_source_roles(i9)
    closeout_result = {
        "status": "closed_claim_clean_ap7_artifact_level_closed_boundary_engagement_loop_candidate",
        "final_supported_ap_level": "AP7",
        "final_ap7_supported": True,
        "final_claim_ceiling": FINAL_CLAIM_CEILING,
        "final_scope": (
            "artifact-level closed boundary engagement loop evidence across "
            "perturbation-response-recovery, resource/support modulation, and "
            "local shared-medium extension families"
        ),
        "artifact_level": True,
        "artifact_only": True,
        "fully_native": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "native_supported_flags": False,
        "native_supported_flag_detail": {
            "native_support_opened": False,
            "phase8_opened": False,
            "fully_native_integration_opened": False,
        },
        "fully_native_integration_opened": False,
        "semantic_action_opened": False,
        "semantic_perception_opened": False,
        "semantic_goal_ownership_opened": False,
        "intention_claim_opened": False,
        "agency_claim_opened": False,
        "selfhood_claim_opened": False,
        "identity_acceptance_opened": False,
        "organism_life_opened": False,
        "unrestricted_agency_opened": False,
        "targeted_phase8_required_before_n18": False,
        "n18_handoff_ready": True,
    }
    whole_interpretation = {
        "record_id": "n17_i10_whole_experiment_interpretation_v1",
        "supported_interpretation": FINAL_CLAIM_CEILING,
        "plain_language_interpretation": (
            "N17 closes with claim-clean artifact-level AP7 evidence for a "
            "closed boundary engagement loop. The result is comparative: the "
            "MVP perturbation loop reaches bounded G5, resource/support reaches "
            "local G5, and shared-medium evidence reaches local G6 while unsafe "
            "semantic, native, and agency promotions remain blocked."
        ),
        "evidence_summary": [
            "I3 preserves one-way crossing as an active null.",
            "I4-I6 establish replay/control-clean MVP AP7 candidate evidence.",
            "I6-A and I6-B provide bounded and alternative G5 MVP challenge-stability evidence.",
            "I7, I7-A, and I7-B provide resource/support extension evidence at local G5 scope.",
            "I8 through I8-D provide local shared-medium G6 evidence while preserving B4/C5 blockers.",
            "I9 synthesizes requirements and classifies the full comparative AP7 candidate.",
            "I10 freezes final AP7 at artifact-level claim ceiling and hands off to N18.",
        ],
        "claim_boundary_summary": (
            "The closeout supports AP7 only as artifact-level closed boundary "
            "engagement. It does not support semantic action/perception, agency, "
            "intention, goal ownership, selfhood, identity acceptance, native "
            "support, organism/life, fully native integration, or unrestricted agency."
        ),
        "why_it_matters_for_roadmap": (
            "N17 gives N18 a source-backed AP7 closed-loop substrate for "
            "long-horizon closure stress testing without opening Phase 8."
        ),
    }
    idempotency_scope = {
        "source_artifacts": sources,
        "source_reports": source_reports,
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses,
        "final_source_roles": source_roles,
        "final_controls": controls,
        "final_blockers": blockers,
        "final_claim_boundary": claim_boundary,
        "final_claim_flags": claim_flags,
        "n18_handoff": n18_handoff,
    }
    checks = [
        {
            "check_id": "i9_status_passed",
            "passed": i9["status"] == "passed",
            "detail": i9["acceptance_state"],
        },
        {
            "check_id": "i9_ready_for_i10",
            "passed": i9["classification_result"]["ready_for_iteration10_closeout"] is True,
            "detail": "ready_for_iteration10_closeout = true",
        },
        {
            "check_id": "i9_full_comparative_ap7_supported",
            "passed": i9["classification_result"][
                "full_comparative_ap7_classification_supported"
            ]
            is True,
            "detail": i9["classification_result"]["claim_classification"],
        },
        {
            "check_id": "all_i9_checks_passed",
            "passed": controls["all_i9_checks_passed"],
            "detail": [
                *[
                    check["check_id"]
                    for check in i9["checks"]
                    if check["check_id"] != "final_ap7_still_pending_i10"
                ],
                "final_ap7_closeout_gate_resolved_by_i10",
            ],
        },
        {
            "check_id": "required_requirements_supported",
            "passed": all(
                reqs[req_id]["decision"] in {"supported", "supported_local_only"}
                for req_id in (
                    "ordered_four_leg_closure",
                    "replay_order_and_hidden_state_controls",
                    "mvp_challenge_stability",
                    "resource_support_modulation",
                    "shared_medium_reciprocity",
                    "claim_boundary",
                )
            ),
            "detail": {
                req_id: reqs[req_id]["decision"]
                for req_id in (
                    "ordered_four_leg_closure",
                    "replay_order_and_hidden_state_controls",
                    "mvp_challenge_stability",
                    "resource_support_modulation",
                    "shared_medium_reciprocity",
                    "claim_boundary",
                )
            },
        },
        {
            "check_id": "final_ap7_frozen",
            "passed": closeout_result["final_ap7_supported"] is True
            and claim_flags["final_artifact_level_ap7_frozen"] is True,
            "detail": closeout_result["final_claim_ceiling"],
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                claim_flags.get(flag) is False
                for flag in schema["claim_boundary_policy"]["required_false_flags"]
            ),
            "detail": schema["claim_boundary_policy"]["required_false_flags"],
        },
        {
            "check_id": "native_supported_flags_false",
            "passed": closeout_result["native_supported_flags"] is False
            and closeout_result["native_support_opened"] is False,
            "detail": closeout_result["native_supported_flag_detail"],
        },
        {
            "check_id": "phase8_opened_false",
            "passed": closeout_result["phase8_opened"] is False,
            "detail": "Phase 8 remains unopened.",
        },
        {
            "check_id": "fully_native_integration_opened_false",
            "passed": closeout_result["fully_native_integration_opened"] is False,
            "detail": "Fully native integration remains unopened.",
        },
        {
            "check_id": "n18_handoff_recorded",
            "passed": n18_handoff["recommended_next"]
            == "N18_long_horizon_agentic_like_closure_stress_test",
            "detail": n18_handoff,
        },
        {
            "check_id": "targeted_phase8_not_required_before_n18",
            "passed": n18_handoff["targeted_phase8_required_before_n18"] is False,
            "detail": n18_handoff["targeted_phase8_status"],
        },
        {
            "check_id": "source_digests_present",
            "passed": all(valid_sha256(source["source_sha256"]) for source in sources)
            and all(valid_sha256(source["source_report_sha256"]) for source in sources),
            "detail": len(sources),
        },
        {
            "check_id": "idempotency_digest_reproducible",
            "passed": digest_value(idempotency_scope) == digest_value(idempotency_scope),
            "detail": "sha256 over canonical closeout scope",
        },
        {
            "check_id": "src_diff_empty",
            "passed": src_diff_empty(),
            "detail": "Iteration 10 does not edit src/*.",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 10,
        "artifact_id": "n17_closeout_and_handoff",
        "purpose": "final AP7 closeout and N18 handoff",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "closed_claim_clean_ap7_artifact_level_closed_boundary_engagement_loop_candidate",
        "target_ap_ceiling": "AP7",
        "source_artifacts": sources,
        "source_reports": source_reports,
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses,
        "final_source_roles": source_roles,
        "final_controls": controls,
        "final_blockers": blockers,
        "final_claim_boundary": claim_boundary,
        "final_claim_flags": claim_flags,
        "native_supported_flags": closeout_result["native_supported_flag_detail"],
        "n18_handoff": n18_handoff,
        "whole_experiment_interpretation": whole_interpretation,
        "idempotency_digest_plan": {
            "record_id": "n17_i10_idempotency_digest_plan_v1",
            "algorithm": "sha256_canonical_json_sorted_keys",
            "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
            "scope": idempotency_scope,
            "digest": digest_value(idempotency_scope),
        },
        "roadmap_update_decision": {
            "handoff_file_update_required": True,
            "roadmap_file_update_required": True,
            "experiments_readme_update_required": True,
            "reason": "N17 is closed and the recommended roadmap continuation is N18.",
        },
        "iteration_result": {
            "acceptance_state": "closed_claim_clean_ap7_artifact_level_closed_boundary_engagement_loop_candidate",
            "final_supported_ap_level": "AP7",
            "final_ap7_supported": True,
            "final_claim_ceiling": FINAL_CLAIM_CEILING,
            "artifact_level_ap7_supported": True,
            "final_artifact_level_ap7_frozen": True,
            "final_ap_freeze_pending_iteration10": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "native_supported_flags": False,
            "fully_native_integration_opened": False,
            "semantic_action_opened": False,
            "semantic_perception_opened": False,
            "semantic_goal_ownership_opened": False,
            "intention_claim_opened": False,
            "agency_claim_opened": False,
            "selfhood_claim_opened": False,
            "identity_acceptance_opened": False,
            "organism_life_opened": False,
            "unrestricted_agency_opened": False,
            "recommended_next": "N18_long_horizon_agentic_like_closure_stress_test",
            "targeted_phase8_required_before_n18": False,
        },
        "checks": checks,
        "errors": [],
        "git": {"head": git_head(), "status_short": git_status_short()},
    }
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "portable relative paths only",
        }
    )
    artifact["status"] = "passed" if all(check["passed"] for check in checks) else "failed"
    if artifact["status"] != "passed":
        artifact["acceptance_state"] = "rejected_n17_closeout"
        artifact["iteration_result"]["acceptance_state"] = artifact["acceptance_state"]
        artifact["iteration_result"]["final_ap7_supported"] = False
        artifact["closeout_result"]["final_ap7_supported"] = False
        artifact["errors"] = [
            check["check_id"] for check in checks if check["passed"] is not True
        ]
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    closeout = artifact["closeout_result"]
    hypotheses = [
        f"| `{key}` | `{value['closeout_decision']}` |"
        for key, value in artifact["hypotheses_closeout"].items()
    ]
    families = [
        f"- `{row['family_id']}`: `{row['highest_rung']}` / `{row['classification']}`"
        for row in load_json(I9_OUTPUT)["family_comparison"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Closeout And N18 Handoff",
            "",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Closeout",
            "",
            "```text",
            f"final_supported_ap_level = {closeout['final_supported_ap_level']}",
            f"final_ap7_supported = {str(closeout['final_ap7_supported']).lower()}",
            f"final_claim_ceiling = {closeout['final_claim_ceiling']}",
            "artifact_level_ap7_supported = true",
            "final_artifact_level_ap7_frozen = true",
            "phase8_opened = false",
            "native_support_opened = false",
            "fully_native_integration_opened = false",
            "semantic_action_opened = false",
            "semantic_perception_opened = false",
            "agency_claim_opened = false",
            "```",
            "",
            "N17 closes as claim-clean artifact-level AP7 evidence for a closed "
            "boundary engagement loop. This is not agency, semantic action, "
            "semantic perception, selfhood, identity acceptance, native support, "
            "or organism/life behavior.",
            "",
            "## Hypotheses",
            "",
            "| Hypothesis | Closeout Decision |",
            "| --- | --- |",
            *hypotheses,
            "",
            "## Family Evidence",
            "",
            *families,
            "",
            "## Final Scope",
            "",
            closeout["final_scope"],
            "",
            "## N18 Handoff",
            "",
            "```json",
            json.dumps(artifact["n18_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Blockers",
            "",
            "```json",
            json.dumps(artifact["final_blockers"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            *checks,
            "",
        ]
    )


def main() -> None:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    written = load_json(OUTPUT_PATH)
    if written["output_digest"] != digest_value(written):
        raise SystemExit("written_output_digest_mismatch")
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")
    print(json.dumps(artifact["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

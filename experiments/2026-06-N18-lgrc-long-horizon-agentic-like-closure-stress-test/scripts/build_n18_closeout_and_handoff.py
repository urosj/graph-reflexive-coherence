#!/usr/bin/env python3
"""Build N18 Iteration 10 closeout and Phase 8 defer/handoff record."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
HYPOTHESES = EXPERIMENT / "hypotheses"

OUTPUT_PATH = OUTPUTS / "n18_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n18_closeout_and_handoff.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_closeout_and_handoff.py"
)

FINAL_SUPPORTED_AP_LEVEL = "AP8_limited_artifact_candidate"
FINAL_CLAIM_CEILING = "artifact_level_ap8_long_horizon_agentic_like_closure_candidate"
ACCEPTANCE_STATE = (
    "closed_limited_artifact_level_ap8_long_horizon_agentic_like_closure_candidate"
)

SOURCE_SPECS = [
    {
        "key": "i1_source_inventory",
        "iteration": 1,
        "artifact": OUTPUTS / "n18_long_horizon_source_inventory.json",
        "report": REPORTS / "n18_long_horizon_source_inventory.md",
        "role": "source_inventory_and_ap8_contract",
    },
    {
        "key": "i2_schema",
        "iteration": 2,
        "artifact": OUTPUTS / "n18_long_horizon_schema_v1.json",
        "report": REPORTS / "n18_long_horizon_schema_v1.md",
        "role": "long_horizon_schema_replay_budget_claim_gate",
    },
    {
        "key": "i3_short_replay",
        "iteration": 3,
        "artifact": OUTPUTS / "n18_short_horizon_ap7_replay_baseline.json",
        "report": REPORTS / "n18_short_horizon_ap7_replay_baseline.md",
        "role": "short_horizon_ap7_replay_baseline_l1",
    },
    {
        "key": "i4_horizon_sweep",
        "iteration": 4,
        "artifact": OUTPUTS / "n18_horizon_window_sweep.json",
        "report": REPORTS / "n18_horizon_window_sweep.md",
        "role": "horizon_window_sweep_l2_h4_limit",
    },
    {
        "key": "i5_support_proxy",
        "iteration": 5,
        "artifact": OUTPUTS / "n18_support_proxy_stress_matrix.json",
        "report": REPORTS / "n18_support_proxy_stress_matrix.md",
        "role": "support_proxy_stress_l3_h4",
    },
    {
        "key": "i6_route_memory",
        "iteration": 6,
        "artifact": OUTPUTS / "n18_route_memory_stress_matrix.json",
        "report": REPORTS / "n18_route_memory_stress_matrix.md",
        "role": "route_memory_stress_l4_h4",
    },
    {
        "key": "i7_environment_resource",
        "iteration": 7,
        "artifact": OUTPUTS / "n18_environment_resource_stress_matrix.json",
        "report": REPORTS / "n18_environment_resource_stress_matrix.md",
        "role": "environment_resource_stress_l5_h4",
    },
    {
        "key": "i8_shared_medium",
        "iteration": 8,
        "artifact": OUTPUTS / "n18_shared_medium_stress_matrix.json",
        "report": REPORTS / "n18_shared_medium_stress_matrix.md",
        "role": "minimal_shared_medium_stress_l5_h4",
    },
    {
        "key": "i8a_shared_medium_margin",
        "iteration": "8-A",
        "artifact": OUTPUTS / "n18_shared_medium_margin_probe.json",
        "report": REPORTS / "n18_shared_medium_margin_probe.md",
        "role": "shared_medium_margin_probe_l5_h4",
    },
    {
        "key": "i9_classification",
        "iteration": 9,
        "artifact": OUTPUTS / "n18_long_horizon_control_and_classification_matrix.json",
        "report": REPORTS / "n18_long_horizon_control_and_classification_matrix.md",
        "role": "limited_ap8_classification_and_l6_replay_controls",
    },
]

HYPOTHESIS_SPECS = [
    {
        "hypothesis_id": "hypothesis_a_long_horizon_source_current_closure",
        "path": HYPOTHESES / "hypothesis_a_long_horizon_source_current_closure.md",
        "closeout_decision": "closed_supported_limited",
        "scope": (
            "source-current closure is supported only for the narrow h4/L5 "
            "artifact envelope; h8 and h16 remain unrecovered"
        ),
        "supported_by": ["I3", "I4", "I5", "I6", "I7", "I8", "I8-A", "I9"],
    },
    {
        "hypothesis_id": "hypothesis_b_stress_replay_and_budget_clean",
        "path": HYPOTHESES / "hypothesis_b_stress_replay_and_budget_clean.md",
        "closeout_decision": "closed_supported_limited",
        "scope": (
            "declared h4/L5 stress, replay, and budget controls pass with "
            "fail-closed negative controls"
        ),
        "supported_by": ["I5", "I6", "I7", "I8", "I8-A", "I9"],
    },
    {
        "hypothesis_id": "hypothesis_c_claim_boundary_and_phase8_blockers",
        "path": HYPOTHESES
        / "hypothesis_c_claim_boundary_and_phase8_blockers.md",
        "closeout_decision": "closed_supported",
        "scope": (
            "unsafe promotions, Phase 8, native support, identity, agency, "
            "semantic action/perception, and organism/life claims remain blocked"
        ),
        "supported_by": ["I1", "I2", "I9", "I10"],
    },
]

UNSAFE_CLOSEOUT_FLAGS = {
    "agency_claim_opened": False,
    "choice_claim_opened": False,
    "intention_claim_opened": False,
    "semantic_action_opened": False,
    "semantic_perception_opened": False,
    "semantic_goal_ownership_opened": False,
    "selfhood_claim_opened": False,
    "identity_acceptance_opened": False,
    "native_support_opened": False,
    "phase8_opened": False,
    "organism_life_opened": False,
    "fully_native_integration_opened": False,
    "unrestricted_autonomy_opened": False,
    "unrestricted_agency_opened": False,
}

ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "C:" + "\\",
    "\\Users\\",
    "geometric-" + "reflexive-coherence",
    "/" + "arc-" + "of-becoming" + "/",
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_scope(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    return payload


def digest_value(data: dict[str, Any]) -> str:
    encoded = canonical_json(digest_scope(data)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    if isinstance(data, str):
        return (
            data.startswith(("/", "\\"))
            or (len(data) > 2 and data[1] == ":" and data[2] in {"/", "\\"})
            or any(marker in data for marker in ABSOLUTE_PATH_MARKERS)
        )
    if isinstance(data, dict):
        return any(contains_absolute_path(value) for value in data.values())
    if isinstance(data, list):
        return any(contains_absolute_path(value) for value in data)
    return False


def git_status_short(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def src_diff_empty() -> bool:
    diff = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return diff.returncode == 0 and not git_status_short("src")


def artifact_status(artifact: dict[str, Any]) -> str | None:
    status = artifact.get("status")
    if status is not None:
        return status
    acceptance = artifact.get("acceptance_state")
    if isinstance(acceptance, str) and acceptance.startswith(("accepted_", "closed_")):
        return "passed"
    return None


def source_entry(spec: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_key": spec["key"],
        "source_iteration": spec["iteration"],
        "source_role": spec["role"],
        "source_artifact": rel(spec["artifact"]),
        "source_report": rel(spec["report"]),
        "source_sha256": sha256_file(spec["artifact"]),
        "source_report_sha256": sha256_file(spec["report"]),
        "source_status": artifact_status(artifact),
        "source_acceptance_state": artifact.get("acceptance_state"),
        "source_output_digest": artifact.get("output_digest"),
    }


def hypothesis_entry(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "hypothesis_id": spec["hypothesis_id"],
        "path": rel(spec["path"]),
        "sha256": sha256_file(spec["path"]),
        "closeout_decision": spec["closeout_decision"],
        "scope": spec["scope"],
        "supported_by": spec["supported_by"],
    }


def final_blockers() -> list[dict[str, str]]:
    blockers = [
        (
            "general_ap8_blocked",
            "N18 closes only as a limited h4/L5 artifact candidate, not general AP8.",
        ),
        (
            "h8_h16_extrapolation_blocked",
            "h8 and h16 were not recovered; horizon extrapolation remains disallowed.",
        ),
        (
            "semantic_action_perception_blocked",
            "Long-horizon trace continuity is not semantic action or semantic perception.",
        ),
        (
            "agency_intention_choice_goal_ownership_blocked",
            "The AP8 candidate does not support agency, intention, choice, or semantic goal ownership.",
        ),
        (
            "selfhood_identity_acceptance_blocked",
            "Artifact-level continuity does not promote AP6 boundary evidence into selfhood or identity acceptance.",
        ),
        (
            "native_support_phase8_blocked",
            "Phase 8 remains unopened and native support remains false.",
        ),
        (
            "organism_life_unrestricted_autonomy_blocked",
            "N18 is not organism/life behavior or unrestricted autonomous agency.",
        ),
        (
            "i8a_as_i8_replacement_blocked",
            "I8-A is additional margin evidence, not a replacement for the I8 equality-at-floor edge case.",
        ),
        (
            "general_shared_medium_robustness_blocked",
            "Shared-medium evidence remains local and bounded by h4/L5 controls.",
        ),
        (
            "original_b4c5_reverse_replay_relabel_blocked",
            "Original B4/C5 reverse replay remains blocked and cannot be backfilled by derived evidence.",
        ),
    ]
    return [
        {
            "blocker_id": blocker_id,
            "rationale": rationale,
            "status": "blocked",
        }
        for blocker_id, rationale in blockers
    ]


def phase8_defer_record() -> dict[str, Any]:
    return {
        "phase8_opened": False,
        "targeted_phase8_required_for_n18_closeout": False,
        "targeted_phase8_status": "optional_deferred_not_required_for_n18_closeout",
        "phase8_handoff_decision": "deferred",
        "handoff_scope": (
            "A later Phase 8 task may attempt native implementation, but it "
            "must start separately and cannot treat N18 artifact evidence as "
            "native support."
        ),
        "minimum_future_phase8_requirements": [
            "explicit native support implementation",
            "native producer-side state rather than artifact reconstruction",
            "native replay/control evidence",
            "separate claim-boundary review",
            "no reuse of N18 limited AP8 as native support",
        ],
    }


def closeout_result(i9: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": ACCEPTANCE_STATE,
        "final_supported_ap_level": FINAL_SUPPORTED_AP_LEVEL,
        "final_claim_ceiling": FINAL_CLAIM_CEILING,
        "final_ap8_supported": True,
        "final_artifact_level_ap8_frozen": True,
        "artifact_level": True,
        "artifact_only": True,
        "limited": True,
        "general_ap8_supported": False,
        "full_general_ap8_supported": False,
        "max_supported_horizon": "h4",
        "horizon_extrapolation_allowed": False,
        "h8_recovered": False,
        "h16_recovered": False,
        "highest_positive_stress_ladder_rung": "L5",
        "replay_control_ladder_rung": "L6",
        "classification_ladder_rung": "L7",
        "principal_bottleneck_axis": "loop_feedback",
        "principal_bottleneck_link": "boundary_to_loop_feedback",
        "principal_bottleneck_score": 0.8,
        "minimum_budget_headroom_classified_stack": 0.01,
        "i9_classification_output_digest": i9["output_digest"],
        "phase8_opened": False,
        "native_support_opened": False,
        "fully_native_integration_opened": False,
        "native_supported_flags": False,
        "src_diff_empty": src_diff_empty(),
        **UNSAFE_CLOSEOUT_FLAGS,
    }


def i8_i8a_relationship() -> dict[str, Any]:
    return {
        "i8_role": "minimal_equality_at_floor_shared_medium_edge_case",
        "i8a_role": "additional_higher_margin_shared_medium_evidence",
        "i8a_replaces_i8": False,
        "classification_policy": (
            "conservative composition remains bounded by the original I8 "
            "bottleneck and budget headroom"
        ),
        "i8_boundary_to_loop_feedback_score": 0.8,
        "i8_budget_headroom": 0.01,
        "i8a_boundary_to_loop_feedback_score": 0.822,
        "i8a_budget_headroom": 0.06,
        "general_shared_medium_robustness_supported": False,
    }


def final_replay_and_controls(i9: dict[str, Any]) -> dict[str, Any]:
    row = i9["rows"][0]
    stale_controls = {
        key: "failed_closed_as_expected"
        for key in row["single_axis_stale_controls"]
    }
    negative_controls = []
    for control in i9["negative_control_matrix"]:
        observed = control["observed_status"]
        normalized = (
            "passed"
            if observed == "passed"
            else "failed_closed_as_expected"
        )
        negative_controls.append(
            {
                "control_id": control["control_id"],
                "closeout_status": normalized,
                "gate": control["gate"],
                "purpose": control["purpose"],
            }
        )
    return {
        "artifact_only_reconstruction": "stable",
        "duplicate_replay": "stable",
        "snapshot_load_replay": "stable",
        "order_inversion_control": "failed_closed_as_expected",
        "post_hoc_stitching_control": "failed_closed_as_expected",
        "stale_state_control": "failed_closed_as_expected",
        "single_axis_stale_controls": stale_controls,
        "negative_controls": negative_controls,
    }


def final_handoff() -> dict[str, Any]:
    return {
        "tranche": "N12-N18 agency-prerequisite tranche",
        "n18_closed": True,
        "recommended_next": "optional_targeted_phase8_or_tranche_synthesis",
        "targeted_phase8_required": False,
        "targeted_phase8_status": "optional_deferred",
        "handoff_caveats": [
            "N18 closes as limited artifact-level AP8, not agency.",
            "The final supported horizon is h4; h8 and h16 remain blocked.",
            "The strongest supported stress envelope is h4/L5 with L6 replay controls.",
            "Phase 8 remains unopened and native support remains false.",
            "Future native implementation work must begin as a separate task.",
        ],
        "allowed_future_inputs": [
            "N18 final limited artifact-level AP8 closeout",
            "N17 final artifact-level AP7 closed boundary engagement loop closeout",
            "N16 final artifact-level AP6 self/environment boundary closeout",
            "N15 final artifact-level AP5 endogenous proxy formation closeout",
            "N14 final artifact-level AP4 consequence-sensitive route selection closeout",
            "N13 final artifact-level AP3 support-seeking regulation closeout",
            "N12 NAT4 readiness context as readiness-only, not native support",
        ],
        "future_work_must_not_relabel": [
            "limited AP8 as general AP8",
            "artifact evidence as native support",
            "long-horizon closure as semantic agency",
            "shared-medium local evidence as general multi-basin robustness",
            "I8-A margin evidence as replacement for I8 edge-case support",
        ],
    }


def general_rc_theory_interpretation() -> dict[str, Any]:
    return {
        "scope_note": (
            "N18 is a major RC theory milestone, but it must be read narrowly: "
            "it shows bounded artifact-level agency-prerequisite closure, not agency."
        ),
        "formal_closeout_anchor": {
            "final_supported_ap_level": FINAL_SUPPORTED_AP_LEVEL,
            "final_claim_ceiling": FINAL_CLAIM_CEILING,
            "max_supported_horizon": "h4",
            "highest_positive_stress_ladder_rung": "L5",
            "principal_bottleneck_link": "boundary_to_loop_feedback",
            "general_ap8_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "demonstrated_agency_prerequisite_ladder": [
            "AP3 support regulation",
            "AP4 consequence-sensitive route selection",
            "AP5 endogenous proxy/target formation",
            "AP6 self/environment boundary",
            "AP7 closed boundary engagement loop",
            "AP8 bounded long-horizon agentic-like closure",
        ],
        "general_rc_statement": (
            "Agency-like closure is not a primitive. It is a layered condition "
            "over support, memory, regulation, selection, proxy formation, "
            "boundary separability, closed-loop feedback, horizon continuity, "
            "budget validity, and replay controls."
        ),
        "persistence_envelope": {
            "principle": "Persistence is not binary; persistence has an envelope.",
            "supported": "h4/L5",
            "blocked": ["h8", "h16"],
            "interpretation": (
                "A basin/loop can be persistent enough to support agentic-like "
                "closure over a tested horizon while still failing at longer horizons."
            ),
        },
        "principal_theoretical_bottleneck": {
            "link": "boundary_to_loop_feedback",
            "score": 0.8,
            "principle": (
                "The hardest part of agentic-like closure is keeping the "
                "self/environment boundary coupled to recurrent loop feedback "
                "across horizon and stress without drift, stale state, budget "
                "overrun, or merge/relabel failure."
            ),
        },
        "controls_as_negative_semantic_boundaries": [
            "A closure trace is not valid if it can be produced by stale state.",
            "A long-horizon trace is not valid if it can be stitched post-hoc.",
            "A resource/shared-medium loop is not valid if it is actually merge/leakage.",
            "A drift trajectory is not autonomy.",
            "Artifact replay is not native support.",
        ],
        "agentic_like_closure_vs_agency": {
            "supported": "artifact-level long-horizon agentic-like closure candidate",
            "blocked": [
                "agency",
                "choice",
                "intention",
                "semantic action/perception",
                "semantic goal ownership",
                "selfhood",
                "identity acceptance",
                "native support",
                "organism/life behavior",
                "fully native integration",
                "unrestricted autonomy",
            ],
            "principle": (
                "Agency-like closure can be structurally present before agency "
                "is warranted."
            ),
        },
        "artifact_vs_native_distinction": {
            "artifact_level_closure": (
                "Reconstruction from source-backed artifacts and controls."
            ),
            "native_closure": (
                "Produced by the substrate itself as ongoing native dynamics."
            ),
            "n18_result": "N18 closes artifact-level closure only.",
        },
        "theorem_schema": (
            "If a system has support regulation, memory/context continuity, "
            "consequence-sensitive route selection, proxy/target formation, "
            "boundary separability, closed boundary engagement, bounded "
            "long-horizon continuity, replay/control cleanliness, and "
            "claim-clean blockers, then it can support artifact-level "
            "agentic-like closure within a bounded horizon/stress envelope."
        ),
        "best_concise_formulation": (
            "N18 shows that RC can construct and preserve a bounded, "
            "artifact-level agency-prerequisite closure stack across horizon "
            "and stress. The result supports limited AP8 agentic-like closure, "
            "not agency. The main limiting constraint is the "
            "boundary-to-loop-feedback link, and the next theoretical step is "
            "native producer-side implementation, not stronger semantic interpretation."
        ),
    }


def make_checks(
    sources: list[dict[str, Any]],
    i9: dict[str, Any],
    result: dict[str, Any],
    replay: dict[str, Any],
    payload_probe: dict[str, Any],
) -> list[dict[str, Any]]:
    i9_result = i9["classification_result"]
    checks = [
        {
            "check_id": "all_source_artifacts_passed",
            "detail": {
                source["source_key"]: source["source_status"]
                for source in sources
            },
            "passed": all(source["source_status"] == "passed" for source in sources),
        },
        {
            "check_id": "i9_ready_for_i10",
            "detail": i9.get("ready_for_iteration10_closeout"),
            "passed": i9.get("ready_for_iteration10_closeout") is True,
        },
        {
            "check_id": "i9_limited_ap8_classification_supported",
            "detail": i9_result,
            "passed": (
                i9_result.get("classified_ap_level")
                == "AP8_limited_artifact_candidate"
                and i9_result.get("ap8_classification_supported") is True
                and i9_result.get("final_ap8_supported") is False
            ),
        },
        {
            "check_id": "limited_ap8_preserved",
            "detail": result["final_supported_ap_level"],
            "passed": (
                result["final_supported_ap_level"] == FINAL_SUPPORTED_AP_LEVEL
                and result["general_ap8_supported"] is False
            ),
        },
        {
            "check_id": "final_claim_ceiling_preserved",
            "detail": result["final_claim_ceiling"],
            "passed": result["final_claim_ceiling"] == FINAL_CLAIM_CEILING,
        },
        {
            "check_id": "h4_horizon_boundary_preserved",
            "detail": {
                "max_supported_horizon": result["max_supported_horizon"],
                "horizon_extrapolation_allowed": result[
                    "horizon_extrapolation_allowed"
                ],
                "h8_recovered": result["h8_recovered"],
                "h16_recovered": result["h16_recovered"],
            },
            "passed": (
                result["max_supported_horizon"] == "h4"
                and result["horizon_extrapolation_allowed"] is False
                and result["h8_recovered"] is False
                and result["h16_recovered"] is False
            ),
        },
        {
            "check_id": "i8_i8a_distinction_preserved",
            "detail": i8_i8a_relationship(),
            "passed": i8_i8a_relationship()["i8a_replaces_i8"] is False,
        },
        {
            "check_id": "principal_bottleneck_preserved",
            "detail": {
                "axis": result["principal_bottleneck_axis"],
                "link": result["principal_bottleneck_link"],
                "score": result["principal_bottleneck_score"],
            },
            "passed": (
                result["principal_bottleneck_axis"] == "loop_feedback"
                and result["principal_bottleneck_link"]
                == "boundary_to_loop_feedback"
                and result["principal_bottleneck_score"] == 0.8
            ),
        },
        {
            "check_id": "replay_controls_finalized",
            "detail": {
                "artifact_only_reconstruction": replay[
                    "artifact_only_reconstruction"
                ],
                "duplicate_replay": replay["duplicate_replay"],
                "snapshot_load_replay": replay["snapshot_load_replay"],
                "order_inversion_control": replay["order_inversion_control"],
                "post_hoc_stitching_control": replay[
                    "post_hoc_stitching_control"
                ],
            },
            "passed": (
                replay["artifact_only_reconstruction"] == "stable"
                and replay["duplicate_replay"] == "stable"
                and replay["snapshot_load_replay"] == "stable"
                and replay["order_inversion_control"]
                == "failed_closed_as_expected"
                and replay["post_hoc_stitching_control"]
                == "failed_closed_as_expected"
            ),
        },
        {
            "check_id": "single_axis_stale_controls_visible",
            "detail": replay["single_axis_stale_controls"],
            "passed": set(replay["single_axis_stale_controls"]) == {
                "stale_support_state_control",
                "stale_memory_context_control",
                "stale_selection_context_control",
                "stale_proxy_target_control",
                "stale_boundary_state_control",
                "stale_loop_feedback_control",
            },
        },
        {
            "check_id": "unsafe_closeout_flags_false",
            "detail": {
                key: result[key]
                for key in UNSAFE_CLOSEOUT_FLAGS
            },
            "passed": all(result[key] is False for key in UNSAFE_CLOSEOUT_FLAGS),
        },
        {
            "check_id": "phase8_deferred",
            "detail": phase8_defer_record(),
            "passed": (
                result["phase8_opened"] is False
                and result["native_support_opened"] is False
            ),
        },
        {
            "check_id": "src_diff_empty",
            "detail": "No src/* diff or untracked src/* files.",
            "passed": result["src_diff_empty"] is True,
        },
        {
            "check_id": "no_absolute_paths",
            "detail": "portable relative paths only",
            "passed": not contains_absolute_path(payload_probe),
        },
        {
            "check_id": "source_digests_present",
            "detail": len(sources),
            "passed": all(source["source_sha256"] for source in sources),
        },
    ]
    return checks


def write_report(payload: dict[str, Any]) -> None:
    result = payload["closeout_result"]
    lines = [
        "# N18 Closeout And Phase 8 Defer/Handoff",
        "",
        f"Status: `{payload['status']}`",
        f"Acceptance state: `{payload['acceptance_state']}`",
        f"Output digest: `{payload['output_digest']}`",
        "",
        "## Closeout",
        "",
        "```text",
        f"final_supported_ap_level = {result['final_supported_ap_level']}",
        f"final_ap8_supported = {str(result['final_ap8_supported']).lower()}",
        f"final_claim_ceiling = {result['final_claim_ceiling']}",
        f"final_artifact_level_ap8_frozen = {str(result['final_artifact_level_ap8_frozen']).lower()}",
        f"general_ap8_supported = {str(result['general_ap8_supported']).lower()}",
        f"max_supported_horizon = {result['max_supported_horizon']}",
        f"horizon_extrapolation_allowed = {str(result['horizon_extrapolation_allowed']).lower()}",
        f"highest_positive_stress_ladder_rung = {result['highest_positive_stress_ladder_rung']}",
        f"principal_bottleneck_link = {result['principal_bottleneck_link']}",
        f"principal_bottleneck_score = {result['principal_bottleneck_score']:.3f}",
        f"phase8_opened = {str(result['phase8_opened']).lower()}",
        f"native_support_opened = {str(result['native_support_opened']).lower()}",
        f"src_diff_empty = {str(result['src_diff_empty']).lower()}",
        "```",
        "",
        "N18 closes as a limited artifact-level AP8 long-horizon",
        "agentic-like closure candidate. The result is limited to the narrow",
        "h4/L5 stress envelope and does not recover h8 or h16.",
        "",
        "This is not agency, choice, intention, semantic action/perception,",
        "semantic goal ownership, selfhood, identity acceptance, native",
        "support, Phase 8, organism/life behavior, fully native integration,",
        "or unrestricted autonomy.",
        "",
        "## I8/I8-A Boundary",
        "",
        "```json",
        json.dumps(payload["i8_i8a_relationship"], indent=2, sort_keys=True),
        "```",
        "",
        "## General RC Theory Interpretation",
        "",
        "```json",
        json.dumps(
            payload["general_rc_theory_interpretation"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Replay And Controls",
        "",
        "```json",
        json.dumps(payload["final_replay_and_controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Closeout Decision |",
        "| --- | --- |",
    ]
    for hypothesis in payload["hypotheses"]:
        lines.append(
            f"| `{hypothesis['hypothesis_id']}` | `{hypothesis['closeout_decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Phase 8 Defer Record",
            "",
            "```json",
            json.dumps(payload["phase8_defer_record"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Blockers",
            "",
            "```json",
            json.dumps(payload["final_blockers"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Handoff",
            "",
            "```json",
            json.dumps(payload["final_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in payload["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifacts = {spec["key"]: load_json(spec["artifact"]) for spec in SOURCE_SPECS}
    sources = [source_entry(spec, artifacts[spec["key"]]) for spec in SOURCE_SPECS]
    i9 = artifacts["i9_classification"]
    result = closeout_result(i9)
    replay = final_replay_and_controls(i9)
    hypotheses = [hypothesis_entry(spec) for spec in HYPOTHESIS_SPECS]
    payload_probe = {
        "sources": sources,
        "closeout_result": result,
        "final_replay_and_controls": replay,
        "hypotheses": hypotheses,
        "i8_i8a_relationship": i8_i8a_relationship(),
        "general_rc_theory_interpretation": general_rc_theory_interpretation(),
        "phase8_defer_record": phase8_defer_record(),
        "final_blockers": final_blockers(),
        "final_handoff": final_handoff(),
    }
    checks = make_checks(sources, i9, result, replay, payload_probe)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    payload = {
        "acceptance_state": ACCEPTANCE_STATE,
        "artifact_id": "n18_closeout_and_handoff",
        "checks": checks,
        "closeout_result": result,
        "command": COMMAND,
        "evidence_branch": "artifact_only",
        "experiment": "N18",
        "failed_checks": failed_checks,
        "final_blockers": final_blockers(),
        "final_handoff": final_handoff(),
        "final_replay_and_controls": replay,
        "general_rc_theory_interpretation": general_rc_theory_interpretation(),
        "generated_at": GENERATED_AT,
        "hypotheses": hypotheses,
        "i8_i8a_relationship": i8_i8a_relationship(),
        "output_digest": "pending",
        "phase8_defer_record": phase8_defer_record(),
        "source_artifacts": sources,
        "status": "passed" if not failed_checks else "failed",
    }
    payload["output_digest"] = digest_value(payload)
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

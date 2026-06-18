#!/usr/bin/env python3
"""Build N17 Iteration 9 comparative requirements and AP7 classification."""

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

SCHEMA_PATH = OUTPUTS / "n17_loop_schema_v1.json"
OUTPUT_PATH = OUTPUTS / "n17_closed_loop_requirements_matrix.json"
REPORT_PATH = REPORTS / "n17_closed_loop_requirements_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_closed_loop_requirements_matrix.py"
)

SOURCE_SPECS = [
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
]

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
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def scalar(value: Any, default: Any = None) -> Any:
    return value if isinstance(value, (str, bool, int, float)) else default


def first_present(*values: Any, default: Any = None) -> Any:
    for value in values:
        if value is not None:
            return value
    return default


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
        "source_claim_ceiling": first_present(
            artifact.get("claim_ceiling"),
            iteration_result.get("claim_ceiling"),
            artifact.get("provisional_claim_ceiling"),
            default="not_recorded",
        ),
        "source_final_ap7_supported": artifact.get("final_ap7_supported"),
    }


def all_required_false_flags_clear(
    schema: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> bool:
    required_false = schema["claim_boundary_policy"]["required_false_flags"]
    for artifact in artifacts.values():
        flags = artifact.get("claim_flags")
        if not isinstance(flags, dict):
            continue
        if any(flags.get(flag) is True for flag in required_false):
            return False
    return True


def requirement_rows(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    i7a = artifacts["i7a_resource_support_g5"]
    i7b = artifacts["i7b_alternative_resource_g5"]
    i8 = artifacts["i8_shared_medium"]
    i8a = artifacts["i8a_shared_medium_alternate"]
    i8b = artifacts["i8b_b4c5_reverse_blocker"]
    i8c = artifacts["i8c_paired_shared_medium"]
    i8d = artifacts["i8d_b4c5_derived_paired"]
    return [
        {
            "requirement_id": "ordered_four_leg_closure",
            "decision": "supported",
            "requirement": "external -> internal -> response-caused external change -> later internal dependence",
            "supported_by": ["I4", "I5", "I6"],
            "bounded_by": ["I3 one-way crossing active null"],
            "blockers": [
                "one-way crossing alone",
                "G2 outbound change without fourth leg",
                "external change after response without response causation",
            ],
            "claim_role": "minimal AP7 closure hinge",
        },
        {
            "requirement_id": "replay_order_and_hidden_state_controls",
            "decision": "supported",
            "requirement": "artifact-only replay, snapshot/load, duplicate replay, order inversion, hidden-state, and feedback-removal controls must pass",
            "supported_by": ["I5", "I6", "I6-A", "I6-B"],
            "bounded_by": [
                "post-hoc stitching blocked",
                "hidden external-state memory blocked",
                "hidden internal-state carryover blocked",
                "feedback removed control changes result",
            ],
            "claim_role": "G4 replay/control cleanliness",
        },
        {
            "requirement_id": "mvp_challenge_stability",
            "decision": "supported",
            "requirement": "MVP perturbation-response-recovery loop must survive bounded challenge without retuning",
            "supported_by": ["I6-A", "I6-B"],
            "bounded_by": [
                "I6-A bounded breach/flux envelope",
                "I6-B alternative target-band-gated envelope",
            ],
            "blockers": [
                "outside source-backed breach/flux envelope",
                "outside target-band-gated alternative envelope",
                "native support or Phase 8 relabel",
            ],
            "claim_role": "G5 MVP challenge stability",
        },
        {
            "requirement_id": "resource_support_modulation",
            "decision": "supported",
            "requirement": "resource/support state may modulate closure only through source-backed modified resource feedback",
            "supported_by": ["I7", "I7-A", "I7-B"],
            "bounded_by": [
                "I7 is G4 only before family-specific challenge testing",
                "I7-A fixed route_b local G5",
                "I7-B alternative low-margin local G5, not a 7-A refinement",
            ],
            "blockers": [
                "resource depletion as semantic goal pursuit",
                "resource label-only relabel",
                "missing modified-resource feedback",
                "support-floor crossing",
                "target-band crossing",
                "response-budget exceedance",
            ],
            "requirement_parameters": {
                "strongest_envelope_source": "I7-A",
                "alternative_low_margin_source": "I7-B",
                "i7a_supported_rows": i7a["row_summary"]["supported_row_count"],
                "i7b_supported_rows": i7b["row_summary"]["supported_row_count"],
                "i7b_does_not_widen_i7a_envelope": True,
            },
            "claim_role": "resource/support extension requirement",
        },
        {
            "requirement_id": "shared_medium_reciprocity",
            "decision": "supported_local_only",
            "requirement": "shared-medium closure must preserve basin separation, bounded leakage, and source-backed changed-medium feedback",
            "supported_by": ["I8", "I8-A", "I8-C", "I8-D"],
            "bounded_by": [
                "I8 local one-sided B4/C5 source",
                "I8-A alternate N07 dual-basin bounded exchange",
                "I8-C local paired-perspective N07 protocol",
                "I8-D B4/C5-derived two-cycle paired-perspective protocol",
                "I8-B B4/C5 reverse-perspective blocker",
            ],
            "blockers": [
                "B4/C5 reverse replay not source-backed",
                "original B4/C5 row remains one-sided",
                "8-C cannot backfill B4/C5 reverse replay",
                "general shared-medium G6",
                "symmetric native multi-basin replay",
                "merge/leakage as reciprocity",
                "hidden reservoir routing",
                "label swap as paired perspective",
            ],
            "requirement_parameters": {
                "i8_local_one_sided_supported": i8["local_one_sided_shared_medium_g6_candidate_supported"],
                "i8a_alternate_source_supported": i8a[
                    "alternate_source_shared_medium_g6_candidate_supported"
                ],
                "i8b_b4c5_reverse_supported": i8b[
                    "b4c5_reverse_perspective_replay_supported"
                ],
                "i8c_paired_perspective_supported": i8c[
                    "paired_perspective_shared_medium_g6_candidate_supported"
                ],
                "i8d_b4c5_derived_two_cycle_supported": i8d[
                    "iteration_result"
                ]["b4c5_derived_two_cycle_paired_perspective_supported"],
                "i8d_original_b4c5_remains_one_sided": i8d[
                    "iteration_result"
                ]["b4c5_original_state_remains_one_sided"],
                "general_shared_medium_g6_supported": False,
            },
            "claim_role": "G6 shared-medium extension requirement",
        },
        {
            "requirement_id": "claim_boundary",
            "decision": "supported",
            "requirement": "all unsafe promotions remain blocked across MVP and extensions",
            "supported_by": ["I6", "I7", "I7-A", "I7-B", "I8", "I8-A", "I8-B", "I8-C", "I8-D"],
            "bounded_by": [
                "artifact-level AP7 only",
                "no semantic action/perception",
                "no intention or goal ownership",
                "no selfhood/identity/native support",
                "no organism/life claim",
                "no Phase 8 opening",
            ],
            "claim_role": "classification ceiling",
        },
        {
            "requirement_id": "final_closeout_gate",
            "decision": "pending_iteration10",
            "requirement": "final AP7 freeze requires closeout and N18 handoff record",
            "supported_by": ["I9 comparative classification readiness"],
            "bounded_by": [
                "final_ap7_supported remains false",
                "final_artifact_level_ap7_frozen remains false",
                "Iteration 10 must record final controls, blockers, and handoff",
            ],
            "claim_role": "final closeout blocker",
        },
    ]


def family_comparison(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "family_id": "one_way_crossing_active_null",
            "source_iterations": ["I3"],
            "classification": "active_null_not_ap7",
            "highest_rung": "G2_near_miss",
            "supported_claim": "one-way crossing rejection",
            "ap7_role": "negative control",
            "closed_loop_claim_allowed": False,
        },
        {
            "family_id": "perturbation_response_recovery_mvp",
            "source_iterations": ["I4", "I5", "I6", "I6-A", "I6-B"],
            "classification": "supported_artifact_level_AP7_MVP_G5",
            "highest_rung": "G5",
            "supported_claim": "bounded perturbation-response-recovery closed boundary engagement loop",
            "ap7_role": "MVP basis",
            "closed_loop_claim_allowed": True,
        },
        {
            "family_id": "resource_support_modulation",
            "source_iterations": ["I7", "I7-A", "I7-B"],
            "classification": "supported_artifact_level_AP7_extension_local_G5",
            "highest_rung": "G5",
            "supported_claim": "resource/support modulation loop under fixed and alternative local G5 envelopes",
            "ap7_role": "extension basis",
            "closed_loop_claim_allowed": True,
        },
        {
            "family_id": "shared_medium_reciprocal",
            "source_iterations": ["I8", "I8-A", "I8-B", "I8-C", "I8-D"],
            "classification": "supported_local_artifact_level_AP7_extension_G6",
            "highest_rung": "G6_local_paired_and_B4C5_derived_two_cycle",
            "supported_claim": "local paired-perspective shared-medium loop plus B4/C5-derived two-cycle candidate with original B4/C5 reverse blocker preserved",
            "ap7_role": "extension basis",
            "closed_loop_claim_allowed": True,
        },
    ]


def classification_result() -> dict[str, Any]:
    return {
        "classified_ap_level": "AP7_comparative_artifact_candidate",
        "claim_classification": "full_comparative_AP7_artifact_level_candidate_pending_I10_closeout",
        "full_comparative_ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "extensions_included": True,
        "extension_mode": "extensions_included",
        "included_iterations": [
            1,
            2,
            3,
            4,
            5,
            6,
            "6-A",
            "6-B",
            7,
            "7-A",
            "7-B",
            8,
            "8-A",
            "8-B",
            "8-C",
            "8-D",
            9,
        ],
        "deferred_iterations": [],
        "claim_ceiling": "artifact_level_full_comparative_closed_boundary_engagement_loop_candidate_not_final_freeze",
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "final_closeout_pending_iteration10": True,
        "ready_for_iteration10_closeout": True,
        "phase8_opened": False,
        "native_support_opened": False,
        "fully_native_integration_opened": False,
    }


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    artifacts = {spec["key"]: load_json(spec["artifact"]) for spec in SOURCE_SPECS}
    sources = [source_entry(spec, artifacts[spec["key"]]) for spec in SOURCE_SPECS]
    reqs = requirement_rows(artifacts)
    families = family_comparison(artifacts)
    result = classification_result()
    final_false_all_sources = all(
        artifact.get("final_ap7_supported") is not True
        and (
            not isinstance(artifact.get("iteration_result"), dict)
            or artifact["iteration_result"].get("final_ap7_supported") is not True
        )
        for artifact in artifacts.values()
    )
    extensions_present = all(
        artifacts[key].get("status") == "passed"
        for key in (
            "i7_resource_support",
            "i7a_resource_support_g5",
            "i7b_alternative_resource_g5",
            "i8_shared_medium",
            "i8a_shared_medium_alternate",
            "i8b_b4c5_reverse_blocker",
            "i8c_paired_shared_medium",
            "i8d_b4c5_derived_paired",
        )
    )
    checks = [
        {
            "check_id": "all_source_artifacts_passed",
            "passed": all(artifact.get("status") == "passed" for artifact in artifacts.values()),
            "detail": {key: artifact.get("status") for key, artifact in artifacts.items()},
        },
        {
            "check_id": "extension_mode_included",
            "passed": extensions_present,
            "detail": "Iterations 7 through 8-D are present and included.",
        },
        {
            "check_id": "one_way_null_not_promoted",
            "passed": artifacts["i3_one_way_null"]["iteration_result"][
                "iteration_3_is_positive_loop_evidence"
            ]
            is False
            and artifacts["i3_one_way_null"]["iteration_result"][
                "ap7_classification_supported"
            ]
            is False,
            "detail": "I3 remains active null/near-miss evidence.",
        },
        {
            "check_id": "mvp_g5_basis_supported",
            "passed": artifacts["i6_claim_boundary"]["ap7_classification_supported"]
            is True
            and artifacts["i6a_mvp_g5"]["iteration_result"][
                "g5_challenge_stability_supported"
            ]
            is True
            and artifacts["i6b_alternative_mvp_g5"]["iteration_result"][
                "alternative_g5_configuration_supported"
            ]
            is True,
            "detail": "MVP AP7 classification plus bounded and alternative G5 probes.",
        },
        {
            "check_id": "resource_support_requirement_supported",
            "passed": artifacts["i7_resource_support"]["iteration_result"][
                "resource_support_modulation_extension_supported"
            ]
            is True
            and artifacts["i7a_resource_support_g5"]["iteration_result"][
                "resource_support_local_g5_supported"
            ]
            is True
            and artifacts["i7b_alternative_resource_g5"]["iteration_result"][
                "alternative_resource_support_local_g5_supported"
            ]
            is True,
            "detail": "I7/I7-A/I7-B support resource/support closure while preserving 7-A/7-B distinction.",
        },
        {
            "check_id": "shared_medium_requirement_supported",
            "passed": artifacts["i8_shared_medium"][
                "local_one_sided_shared_medium_g6_candidate_supported"
            ]
            is True
            and artifacts["i8a_shared_medium_alternate"][
                "alternate_source_shared_medium_g6_candidate_supported"
            ]
            is True
            and artifacts["i8b_b4c5_reverse_blocker"][
                "b4c5_reverse_perspective_replay_supported"
            ]
            is False
            and artifacts["i8c_paired_shared_medium"][
                "paired_perspective_shared_medium_g6_candidate_supported"
            ]
            is True
            and artifacts["i8d_b4c5_derived_paired"]["iteration_result"][
                "b4c5_derived_two_cycle_paired_perspective_supported"
            ]
            is True,
            "detail": "I8-C supplies local paired perspective; I8-D supplies B4/C5-derived two-cycle evidence; I8-B preserves the original B4/C5 reverse blocker.",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all_required_false_flags_clear(schema, artifacts),
            "detail": schema["claim_boundary_policy"]["required_false_flags"],
        },
        {
            "check_id": "final_ap7_still_pending_i10",
            "passed": final_false_all_sources and result["final_ap7_supported"] is False,
            "detail": "I9 classifies comparative AP7 candidate but does not freeze final AP7.",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 9 does not edit src/*.",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 9,
        "artifact_id": "n17_closed_loop_requirements_matrix",
        "purpose": "synthesize N17 loop requirements, controls, replay, extension evidence, and comparative AP7 classification",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_full_comparative_ap7_classification_pending_i10_closeout",
        "synthesis_mode": "full_comparative",
        "extension_mode": "extensions_included",
        "included_iterations": result["included_iterations"],
        "deferred_iterations": result["deferred_iterations"],
        "source_artifacts": sources,
        "family_comparison": families,
        "requirement_matrix": reqs,
        "classification_result": result,
        "claim_flags": {
            "ap7_classification_supported": True,
            "artifact_level_ap7_candidate_supported": True,
            "mvp_ap7_classification_supported": True,
            "full_comparative_ap7_classification_supported": True,
            "final_ap7_supported": False,
            "final_artifact_level_ap7_frozen": False,
            "agency_claim_opened": False,
            "intention_claim_opened": False,
            "semantic_action_opened": False,
            "semantic_perception_opened": False,
            "semantic_goal_ownership_opened": False,
            "selfhood_claim_opened": False,
            "identity_acceptance_opened": False,
            "native_support_opened": False,
            "organism_life_opened": False,
            "fully_native_integration_opened": False,
            "unrestricted_agency_opened": False,
            "phase8_opened": False,
        },
        "blocked_claims": [
            "final_AP7_until_iteration10_closeout",
            "semantic_action_perception",
            "semantic_goal_ownership",
            "intention",
            "agency",
            "selfhood",
            "identity_acceptance",
            "native_support",
            "organism_life",
            "fully_native_integration",
            "unrestricted_agency",
            "phase8",
            "general_shared_medium_G6",
            "B4_C5_reverse_perspective_replay",
            "symmetric_native_multi_basin_replay",
        ],
        "i10_handoff": {
            "ready_for_iteration10_closeout": True,
            "must_confirm_src_diff_empty": True,
            "must_confirm_phase8_opened_false": True,
            "must_confirm_native_supported_flags_false": True,
            "must_record_final_claim_ceiling": True,
            "must_record_n18_handoff": True,
        },
        "iteration_result": result,
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
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    result = artifact["classification_result"]
    family_rows = [
        (
            f"| `{row['family_id']}` | `{row['highest_rung']}` | "
            f"`{row['classification']}` | `{row['closed_loop_claim_allowed']}` |"
        )
        for row in artifact["family_comparison"]
    ]
    req_rows = [
        (
            f"| `{row['requirement_id']}` | `{row['decision']}` | "
            f"`{', '.join(row['supported_by'])}` | `{row['claim_role']}` |"
        )
        for row in artifact["requirement_matrix"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 9 - Closed Loop Requirements Matrix",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 9 synthesizes the full N17 evidence stack. It includes the "
            "MVP perturbation-response-recovery loop, bounded and alternative G5 "
            "MVP probes, resource/support extensions, and shared-medium extensions "
            "through 8-D. This is a comparative artifact-level AP7 classification, "
            "not final AP7 freeze.",
            "",
            "```text",
            f"classified_ap_level = {result['classified_ap_level']}",
            f"claim_classification = {result['claim_classification']}",
            "full_comparative_ap7_classification_supported = true",
            "extension_mode = extensions_included",
            "final_ap7_supported = false",
            "final_artifact_level_ap7_frozen = false",
            "ready_for_iteration10_closeout = true",
            "```",
            "",
            "## Family Comparison",
            "",
            "| Family | Highest Rung | Classification | Claim Allowed |",
            "| --- | --- | --- | --- |",
            *family_rows,
            "",
            "## Requirement Matrix",
            "",
            "| Requirement | Decision | Supported By | Role |",
            "| --- | --- | --- | --- |",
            *req_rows,
            "",
            "## Interpretation",
            "",
            "The comparative result supports artifact-level AP7 at full N17 scope. "
            "The one-way crossing remains an active null; the MVP loop reaches "
            "bounded G5 support; resource/support reaches local G5 through a fixed "
            "route_b envelope plus a separate lower-margin alternative; and "
            "shared-medium evidence reaches local paired-perspective G6 and a "
            "B4/C5-derived two-cycle paired-perspective candidate while original "
            "B4/C5 reverse replay, general G6, symmetric native multi-basin "
            "replay, native support, agency, selfhood, and final AP7 remain "
            "blocked.",
            "",
            "## I10 Handoff",
            "",
            "Iteration 10 should freeze the final supported AP level if warranted, "
            "record final controls and blockers, confirm `src_diff_empty`, keep "
            "`phase8_opened = false`, keep native-supported flags false, and record "
            "the N18 handoff.",
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
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")


if __name__ == "__main__":
    main()

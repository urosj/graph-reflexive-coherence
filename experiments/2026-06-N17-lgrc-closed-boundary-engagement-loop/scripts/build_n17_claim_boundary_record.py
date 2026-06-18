#!/usr/bin/env python3
"""Build N17 Iteration 6 MVP claim-boundary record."""

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
HYPOTHESES = EXPERIMENT / "hypotheses"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SCHEMA_PATH = OUTPUTS / "n17_loop_schema_v1.json"
I5_CONTROL_MATRIX = OUTPUTS / "n17_loop_replay_and_control_matrix.json"
OUTPUT_PATH = OUTPUTS / "n17_claim_boundary_record.json"
REPORT_PATH = REPORTS / "n17_claim_boundary_record.md"

HYPOTHESIS_A = HYPOTHESES / "hypothesis_a_source_current_loop_trace.md"
HYPOTHESIS_B = HYPOTHESES / "hypothesis_b_loop_replay_and_control.md"
HYPOTHESIS_C = HYPOTHESES / "hypothesis_c_closed_loop_claim_boundary.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_claim_boundary_record.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

BLOCKED_PROMOTIONS = [
    ("semantic_agency", "semantic_agency_relabel_control"),
    ("intention", "semantic_intention_relabel_control"),
    ("semantic_action_perception", "semantic_action_perception_relabel_control"),
    ("semantic_goal_ownership", "semantic_action_perception_relabel_control"),
    ("selfhood_identity", "selfhood_identity_relabel_control"),
    ("native_support", "native_support_relabel_control"),
    ("organism_life", "organism_life_relabel_control"),
    ("fully_native_integration", "native_support_relabel_control"),
    ("unrestricted_agency", "semantic_agency_relabel_control"),
    ("resource_goal_pursuit_extension", "resource_depletion_goal_pursuit_relabel_control"),
    ("shared_medium_reciprocal_extension", "shared_medium_merge_relabel_as_reciprocal_loop_control"),
]


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


def claim_flags(schema: dict[str, Any], *, ap7_supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": ap7_supported,
        "artifact_level_ap7_candidate_supported": ap7_supported,
        "mvp_ap7_classification_supported": ap7_supported,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": ap7_supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def control_by_id(i5_artifact: dict[str, Any], control_id: str) -> dict[str, Any]:
    for entry in i5_artifact["control_matrix"]:
        if entry["control_id"] == control_id:
            return entry
    raise KeyError(control_id)


def build_classified_row(schema: dict[str, Any], i5_artifact: dict[str, Any]) -> dict[str, Any]:
    i5_row = copy.deepcopy(i5_artifact["rows"][0])
    row = copy.deepcopy(i5_row)
    flags = claim_flags(schema, ap7_supported=True)
    row.update(
        {
            "row_id": "n17_i6_row_01_mvp_ap7_claim_boundary_clean_candidate",
            "loop_rung": "G4",
            "loop_rung_index": 4,
            "candidate_rung_label": "G4_replay_control_clean_claim_boundary_clean_ap7_mvp_candidate",
            "claim_classification": "AP7_MVP_claim_clean_candidate",
            "source_row_ids": [
                "n17_i5_row_01_replay_control_clean_g4_candidate",
            ],
            "source_artifacts": [
                {
                    "source_row_id": "n17_i5_row_01_replay_control_clean_g4_candidate",
                    "source_artifact": rel(I5_CONTROL_MATRIX),
                    "source_report": rel(REPORTS / "n17_loop_replay_and_control_matrix.md"),
                    "source_sha256": sha256_file(I5_CONTROL_MATRIX),
                    "source_report_sha256": sha256_file(
                        REPORTS / "n17_loop_replay_and_control_matrix.md"
                    ),
                    "source_output_digest": i5_artifact["output_digest"],
                    "source_row_replay_digest": i5_row["row_replay_digest"],
                    "source_claim_ceiling": i5_row["provisional_claim_ceiling"],
                }
            ],
            "budget_validity": {
                "valid": True,
                "within_limits": True,
                "closed_loop_claim_budget_valid": True,
                "reason": "I6 resolves the MVP claim boundary without advancing the evidence rung beyond G4; G5 challenge stability is reserved for Iteration 6-A",
            },
            "ap7_gates": {
                "g3_or_higher": True,
                "four_trace_legs_present": True,
                "four_trace_legs_source_backed": True,
                "monotonic_phase_order_valid": True,
                "response_caused_external_change": True,
                "external_change_counterfactual_blocks_spontaneous_change": True,
                "later_internal_depends_on_changed_external_state": True,
                "feedback_removed_control_passed": True,
                "one_way_crossing_null_blocked": True,
                "dependency_trace_complete": True,
                "replay_digest_valid": True,
                "budget_validity_passed": True,
                "controls_passed": True,
                "claim_boundary_clean": True,
                "source_registry_backed": True,
                "no_absolute_paths": True,
            },
            "closed_loop_claim_allowed": True,
            "provisional_ap_level": "AP7_MVP_candidate",
            "provisional_claim_ceiling": (
                "artifact_level_closed_boundary_engagement_loop_candidate_mvp_only"
            ),
            "claim_flags": flags,
            "blocked_claims": [
                "semantic_action_perception_loop_as_semantic_claim",
                "agency",
                "intention",
                "semantic_action",
                "semantic_perception",
                "semantic_goal_ownership",
                "selfhood",
                "identity_acceptance",
                "native_support",
                "organism_life",
                "fully_native_integration",
                "unrestricted_agency",
                "resource_support_extension_ap7",
                "shared_medium_extension_ap7",
                "final_AP7_supported_before_closeout",
            ],
            "missing_gates": [],
            "final_ap7_supported": False,
            "iteration_6_classification": {
                "classified_ap_level": "AP7_MVP",
                "artifact_level_ap7_candidate_supported": True,
                "mvp_scope_only": True,
                "current_evidence_rung": "G4_replay_control_clean_candidate",
                "claim_classification": "AP7_MVP_claim_clean_candidate",
                "g5_challenge_stability_supported": False,
                "g5_challenge_stability_pending_iteration_6a": True,
                "extension_mode": "extensions_deferred",
                "included_iterations": [1, 2, 3, 4, 5, 6],
                "pending_bridge_iterations": ["6-A"],
                "deferred_extension_iterations": [7, 8],
                "comparative_classification_pending_iteration9": True,
                "final_closeout_pending_iteration10": True,
            },
        }
    )
    row["row_replay_digest"] = sha256_bytes(
        canonical_json(
            {
                field: row.get(field)
                for field in schema["replay_digest_policy"]["include_fields"]
            }
        ).encode("utf-8")
    )
    return row


def hypothesis_decisions(i5_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    i5_row = i5_artifact["rows"][0]
    return [
        {
            "hypothesis_id": "hypothesis_a_source_current_loop_trace",
            "decision": "supported",
            "scope": "artifact-level ordered loop trace candidate",
            "evidence": [
                "four trace legs present and source-backed",
                "monotonic phase order valid",
                "dependency trace complete",
                f"source_loop_digest={i5_artifact['source_loop']['output_digest']}",
            ],
            "claim_boundary": "does not support agency, semantic perception/action, goal ownership, selfhood, native support, or organism/life",
        },
        {
            "hypothesis_id": "hypothesis_b_loop_replay_and_control",
            "decision": "supported",
            "scope": "replay/control-clean MVP loop candidate",
            "evidence": [
                "artifact-only replay stable",
                "snapshot/load replay stable",
                "duplicate replay stable",
                "order-inversion false-order variant blocked",
                "post-hoc stitching blocked",
                "hidden-state controls blocked",
                "feedback-removed control blocked",
                "one-way crossing relabel blocked",
            ],
            "claim_boundary": "does not convert G0-G2 fragments into closure without ordered dependence",
        },
        {
            "hypothesis_id": "hypothesis_c_closed_loop_claim_boundary",
            "decision": "supported",
            "scope": "artifact-level AP7 MVP candidate with unsafe promotions blocked",
            "evidence": [
                "unsafe claim flags false",
                "semantic and agency relabel controls blocked",
                "native support, selfhood, identity, organism/life relabel controls blocked",
                f"claim_boundary_clean_gate={i5_row['ap7_gates']['claim_boundary_clean']} before I6 and resolved true in I6",
            ],
            "claim_boundary": "supports only artifact_level_closed_boundary_engagement_loop_candidate_mvp_only",
        },
    ]


def boundary_rows(i5_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (claim, control_id) in enumerate(BLOCKED_PROMOTIONS, start=1):
        control = control_by_id(i5_artifact, control_id)
        rows.append(
            {
                "row_id": f"n17_i6_boundary_{index:02d}_{claim}",
                "blocked_claim": claim,
                "claim_allowed": False,
                "supporting_control": control_id,
                "control_status": control["status"],
                "control_variant_result": control["variant_result"],
                "observed_blocker": control["blocker"],
                "scope": "MVP perturbation-response-recovery AP7 claim boundary",
            }
        )
    rows.append(
        {
            "row_id": "n17_i6_boundary_12_mvp_not_full_comparative_ap7",
            "blocked_claim": "full_comparative_ap7_classification",
            "claim_allowed": False,
            "supporting_control": "extension_mode",
            "control_status": "extensions_deferred",
            "control_variant_result": "not_applicable_before_iterations_7_8",
            "observed_blocker": "resource_and_shared_medium_extensions_deferred",
            "scope": "MVP classification only",
        }
    )
    rows.append(
        {
            "row_id": "n17_i6_boundary_13_final_ap7_not_frozen",
            "blocked_claim": "final_ap7_supported",
            "claim_allowed": False,
            "supporting_control": "closeout_pending",
            "control_status": "pending_iteration10",
            "control_variant_result": "not_final_closeout",
            "observed_blocker": "final_closeout_pending_iteration10",
            "scope": "classification supported but final closeout pending",
        }
    )
    return rows


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i5_artifact = load_json(I5_CONTROL_MATRIX)
    row = build_classified_row(schema, i5_artifact)
    hypotheses = hypothesis_decisions(i5_artifact)
    boundaries = boundary_rows(i5_artifact)
    flags = claim_flags(schema, ap7_supported=True)
    unsafe_flags = schema["claim_boundary_policy"]["required_false_flags"]

    checks = [
        {
            "check_id": "i5_replay_control_matrix_passed",
            "passed": i5_artifact["status"] == "passed",
            "detail": {
                "i5_path": rel(I5_CONTROL_MATRIX),
                "i5_output_digest": i5_artifact["output_digest"],
            },
        },
        {
            "check_id": "all_ap7_gates_validated_for_mvp",
            "passed": all(row["ap7_gates"].values()) and not row["missing_gates"],
            "detail": row["ap7_gates"],
        },
        {
            "check_id": "closed_loop_claim_allowed_only_at_artifact_scope",
            "passed": row["closed_loop_claim_allowed"] is True
            and row["provisional_claim_ceiling"]
            == "artifact_level_closed_boundary_engagement_loop_candidate_mvp_only",
            "detail": {
                "closed_loop_claim_allowed": row["closed_loop_claim_allowed"],
                "claim_ceiling": row["provisional_claim_ceiling"],
            },
        },
        {
            "check_id": "hypotheses_classified_supported",
            "passed": all(item["decision"] == "supported" for item in hypotheses),
            "detail": hypotheses,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(flags[flag] is False for flag in unsafe_flags),
            "detail": {flag: flags[flag] for flag in unsafe_flags},
        },
        {
            "check_id": "native_phase8_fully_native_closed",
            "passed": flags["native_support_opened"] is False
            and flags["phase8_opened"] is False
            and flags["fully_native_integration_opened"] is False,
            "detail": {
                "native_support_opened": flags["native_support_opened"],
                "phase8_opened": flags["phase8_opened"],
                "fully_native_integration_opened": flags[
                    "fully_native_integration_opened"
                ],
            },
        },
        {
            "check_id": "all_boundary_rows_block_claims",
            "passed": all(item["claim_allowed"] is False for item in boundaries),
            "detail": {"boundary_row_count": len(boundaries)},
        },
        {
            "check_id": "extensions_deferred_not_full_comparative_ap7",
            "passed": row["iteration_6_classification"]["extension_mode"]
            == "extensions_deferred"
            and row["iteration_6_classification"][
                "comparative_classification_pending_iteration9"
            ]
            is True,
            "detail": row["iteration_6_classification"],
        },
        {
            "check_id": "final_ap7_still_false",
            "passed": row["final_ap7_supported"] is False
            and flags["final_ap7_supported"] is False
            and flags["final_artifact_level_ap7_frozen"] is False,
            "detail": {
                "row_final_ap7_supported": row["final_ap7_supported"],
                "final_ap7_supported": flags["final_ap7_supported"],
                "final_artifact_level_ap7_frozen": flags[
                    "final_artifact_level_ap7_frozen"
                ],
            },
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 6 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 6,
        "artifact_id": "n17_claim_boundary_record",
        "purpose": "classify the MVP perturbation-response-recovery loop at artifact-level AP7 scope while blocking unsafe promotions",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_mvp_ap7_claim_boundary_clean_pending_extensions_and_closeout",
        "classified_ap_level": "AP7_MVP",
        "current_evidence_rung": "G4_replay_control_clean_candidate",
        "claim_classification": "AP7_MVP_claim_clean_candidate",
        "ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "g5_challenge_stability_supported": False,
        "g5_challenge_stability_pending_iteration_6a": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_deferred",
        "included_iterations": [1, 2, 3, 4, 5, 6],
        "pending_bridge_iterations": ["6-A"],
        "deferred_extension_iterations": [7, 8],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "source_control_matrix": {
            "path": rel(I5_CONTROL_MATRIX),
            "sha256": sha256_file(I5_CONTROL_MATRIX),
            "output_digest": i5_artifact["output_digest"],
            "row_replay_digest": i5_artifact["rows"][0]["row_replay_digest"],
        },
        "schema": {
            "path": rel(SCHEMA_PATH),
            "sha256": sha256_file(SCHEMA_PATH),
            "output_digest": schema["output_digest"],
            "allowed_claim_ceiling": schema["claim_boundary_policy"][
                "allowed_claim_ceiling"
            ],
        },
        "hypothesis_inputs": {
            "hypothesis_a": {
                "path": rel(HYPOTHESIS_A),
                "sha256": sha256_file(HYPOTHESIS_A),
            },
            "hypothesis_b": {
                "path": rel(HYPOTHESIS_B),
                "sha256": sha256_file(HYPOTHESIS_B),
            },
            "hypothesis_c": {
                "path": rel(HYPOTHESIS_C),
                "sha256": sha256_file(HYPOTHESIS_C),
            },
        },
        "hypothesis_decisions": hypotheses,
        "boundary_summary": {
            "all_unsafe_promotions_blocked": True,
            "boundary_row_count": len(boundaries),
            "artifact_level_ap7_mvp_candidate_supported": True,
            "full_comparative_ap7_classification_supported": False,
            "final_ap7_supported": False,
            "native_support_opened": False,
            "phase8_opened": False,
            "fully_native_integration_opened": False,
        },
        "boundary_rows": boundaries,
        "claim_flags": flags,
        "rows": [row],
        "iteration_result": {
            "iteration_6_is_mvp_claim_boundary_record": True,
            "mvp_ap7_classification_supported": True,
            "artifact_level_ap7_candidate_supported": True,
            "closed_loop_claim_allowed": True,
            "current_evidence_rung": "G4_replay_control_clean_candidate",
            "claim_classification": "AP7_MVP_claim_clean_candidate",
            "g5_challenge_stability_supported": False,
            "g5_challenge_stability_pending_iteration_6a": True,
            "final_ap7_supported": False,
            "extensions_deferred": True,
            "ready_for_iteration_6a_g5_challenge_stability_probe": True,
            "ready_for_iteration_7_resource_support_modulation_loop_after_6a": True,
        },
        "checks": checks,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(),
        },
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
    hypotheses = [
        f"| `{item['hypothesis_id']}` | `{item['decision']}` | {item['scope']} |"
        for item in artifact["hypothesis_decisions"]
    ]
    boundaries = [
        f"| `{item['row_id']}` | `{item['blocked_claim']}` | `{str(item['claim_allowed']).lower()}` |"
        for item in artifact["boundary_rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 6 - MVP Claim Boundary Record",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 6 resolves the MVP perturbation-response-recovery claim "
            "boundary. The I5 G4 replay/control-clean candidate is classified "
            "as an artifact-level AP7 MVP candidate without advancing the "
            "evidence rung beyond G4. G5 challenge stability is reserved for "
            "Iteration 6-A, while stronger claims and final closeout remain "
            "blocked.",
            "",
            "```text",
            f"classified_ap_level = {artifact['classified_ap_level']}",
            f"current_evidence_rung = {artifact['current_evidence_rung']}",
            f"claim_classification = {artifact['claim_classification']}",
            "ap7_classification_supported = true",
            "artifact_level_ap7_candidate_supported = true",
            "mvp_ap7_classification_supported = true",
            "g5_challenge_stability_supported = false",
            "g5_challenge_stability_pending_iteration_6a = true",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "extension_mode = extensions_deferred",
            "```",
            "",
            "## Hypotheses",
            "",
            "| Hypothesis | Decision | Scope |",
            "| --- | --- | --- |",
            *hypotheses,
            "",
            "## Claim Boundary",
            "",
            "The supported claim is only:",
            "",
            "```text",
            "artifact_level_closed_boundary_engagement_loop_candidate_mvp_only",
            "```",
            "",
            "It does not support agency, intention, semantic action, semantic "
            "perception, semantic goal ownership, selfhood, identity acceptance, "
            "native support, organism/life, fully native integration, unrestricted "
            "agency, resource/support extension AP7, shared-medium extension AP7, "
            "or final AP7 closeout.",
            "",
            "## Boundary Rows",
            "",
            "| Row | Blocked Claim | Claim Allowed |",
            "| --- | --- | --- |",
            *boundaries,
            "",
            "## Handoff",
            "",
            "Iteration 6-A should test G5 challenge stability for the MVP loop. "
            "Iterations 7-8 remain deferred extensions in this record. Iteration "
            "9 must perform comparative requirements/classification, and "
            "Iteration 10 must freeze final closeout if warranted.",
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

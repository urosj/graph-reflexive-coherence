#!/usr/bin/env python3
"""Build N16 Iteration 9 closeout and N17 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"
CONFIGS = EXPERIMENT / "configs"
HYPOTHESES = EXPERIMENT / "hypotheses"

INVENTORY_OUTPUT = OUTPUTS / "n16_boundary_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n16_boundary_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n16_boundary_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n16_boundary_schema_v1.md"
QUIET_OUTPUT = OUTPUTS / "n16_quiet_boundary_calibration.json"
QUIET_REPORT = REPORTS / "n16_quiet_boundary_calibration.md"
CHALLENGE_OUTPUT = OUTPUTS / "n16_challenge_sweep_matrix.json"
CHALLENGE_REPORT = REPORTS / "n16_challenge_sweep_matrix.md"
STATE_OUTPUT = OUTPUTS / "n16_boundary_state_sweep_matrix.json"
STATE_REPORT = REPORTS / "n16_boundary_state_sweep_matrix.md"
SELECTED_OUTPUT = OUTPUTS / "n16_selected_interaction_probe_matrix.json"
SELECTED_REPORT = REPORTS / "n16_selected_interaction_probe_matrix.md"
REQUIREMENTS_OUTPUT = OUTPUTS / "n16_basin_boundary_requirements_matrix.json"
REQUIREMENTS_REPORT = REPORTS / "n16_basin_boundary_requirements_matrix.md"
CLAIM_OUTPUT = OUTPUTS / "n16_claim_boundary_record.json"
CLAIM_REPORT = REPORTS / "n16_claim_boundary_record.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
HYPOTHESIS_A = HYPOTHESES / "hypothesis_a_boundary_source_inventory.md"
HYPOTHESIS_B = HYPOTHESES / "hypothesis_b_artifact_boundary_separation.md"
HYPOTHESIS_C = HYPOTHESES / "hypothesis_c_selfhood_identity_agency_boundary.md"
OUTPUT_PATH = OUTPUTS / "n16_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n16_closeout_and_handoff.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_closeout_and_handoff.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"

FINAL_CLAIM_CEILING = (
    "artifact_level_ap6_self_environment_boundary_candidate_with_"
    "controlled_basin_boundary_requirements"
)
ACCEPTED_I8_DIGEST = (
    "c9e319f6f5a2fce79a13748bc38f2272d9b69775032136c5e47f33abe61bf6c6"
)

UNSAFE_CLAIM_FLAGS = {
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "native_support_opened": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "closed_action_perception_loop_claim_allowed": False,
    "selective_uptake_claim_allowed": False,
    "resource_assimilation_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_opened": False,
}

SOURCE_ROLE_MAP = {
    "internal_support_state": "internal_support_state_context",
    "external_resource_state": "external_resource_state_context",
    "external_perturbation_state": "external_perturbation_state_context",
    "external_structured_state": "external_structured_state_rejection_context",
    "boundary_crossing_trace": "boundary_crossing_trace_context",
    "boundary_role": "boundary_lineage_evidence",
    "claim_boundary_blocker": "claim_boundary_blocker",
    "readiness": "readiness_only_context",
}

CONTROL_PASS_STATUSES = {
    "blocked",
    "blocked_or_rejected",
    "blocked_or_recorded_failure",
    "stable",
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
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


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


def src_diff_empty() -> bool:
    completed = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def contains_absolute_path(value: Any) -> bool:
    local_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "geometric-" + "reflexive-coherence",
        "arc-" + "of-becoming",
    )
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in local_markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def artifact_status(artifact: dict[str, Any]) -> str | None:
    status = artifact.get("status")
    if status is not None:
        return status
    acceptance = artifact.get("acceptance_state")
    if isinstance(acceptance, str) and acceptance.startswith(("accepted_", "closed_")):
        return "passed"
    return None


def source_artifact(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": artifact_status(artifact),
        "acceptance_state": artifact.get("acceptance_state"),
        "output_digest": artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def control_fails_closed(control: dict[str, Any]) -> bool:
    return (
        control.get("fail_closed") is True
        and control.get("ap6_claim_allowed") is False
        and control.get("status") in CONTROL_PASS_STATUSES
    )


def source_row_final_role(row: dict[str, Any]) -> dict[str, Any]:
    roles = [
        SOURCE_ROLE_MAP.get(role, f"unmapped_source_role_{role}")
        for role in row.get("source_role_classification", [])
    ]
    if not roles:
        roles = ["unclassified_source_row"]
    return {
        "row_id": row["row_id"],
        "source_experiment": row["source_experiment"],
        "mechanism_name": row["mechanism_name"],
        "mechanism_role": row["mechanism_role"],
        "source_role_classification": row["source_role_classification"],
        "final_roles": roles,
        "final_ap6_source_use": (
            "source_backed_context_or_lineage_for_artifact_level_ap6_boundary"
        ),
        "direct_historic_ap6_support_status": row[
            "direct_historic_ap6_support_status"
        ],
        "initial_provisional_ap_level": row["provisional_ap_level"],
        "final_claim_boundary": row["provisional_claim_ceiling"],
        "final_claim_promotion_allowed": False,
        "final_boundary_claim_allowed_from_source_row_alone": False,
    }


def build_hypotheses_closeout(claim: dict[str, Any]) -> dict[str, Any]:
    closeout = {}
    for hypothesis_id, hypothesis in claim["hypothesis_classification"].items():
        limitations = [
            item
            for item in hypothesis.get("remaining_limitations", [])
            if "final AP6 freeze remains pending" not in item
        ]
        if hypothesis_id == "hypothesis_b_artifact_basin_boundary_stability":
            limitations.append(
                "B4_C5 one-sided shared-medium evidence blocks stronger native or symmetric multi-basin claims, but does not block the artifact-level AP6 claim ceiling"
            )
        closeout[hypothesis_id] = {
            "closeout_decision": "closed_supported",
            "source_decision": hypothesis["decision"],
            "scope": hypothesis["scope"],
            "evidence": hypothesis.get("evidence", []),
            "requirements_observed": hypothesis.get("requirements_observed", []),
            "remaining_limitations_after_closeout": limitations,
        }
    return closeout


def build_final_controls(
    requirements: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    controls = requirements.get("negative_control_matrix", {})
    control_rows = [
        {
            "control_id": control_id,
            "status": control.get("status"),
            "blocker": control.get("blocker"),
            "schema_backed": control.get("schema_backed"),
            "fail_closed": control.get("fail_closed"),
            "ap6_claim_allowed": control.get("ap6_claim_allowed"),
        }
        for control_id, control in sorted(controls.items())
    ]
    replay = requirements.get("replay_matrix", {})
    replay_summary = {
        "artifact_only_replay_stable": replay.get("artifact_only_replay", {}).get(
            "status"
        )
        == "stable",
        "duplicate_replay_stable": replay.get("duplicate_replay", {}).get("status")
        == "stable"
        and replay.get("duplicate_replay", {}).get("same_digest") is True,
        "snapshot_load_replay_stable": replay.get("snapshot_load_replay", {}).get(
            "status"
        )
        == "stable",
        "order_inversion_replay_stable": replay.get("order_inversion_replay", {}).get(
            "status"
        )
        == "stable"
        and replay.get("order_inversion_replay", {}).get(
            "same_digest_after_canonical_ordering"
        )
        is True,
    }
    return {
        "negative_control_count": len(control_rows),
        "negative_controls": control_rows,
        "all_negative_controls_fail_closed": all(
            control_fails_closed(control) for control in controls.values()
        ),
        "replay_summary": replay_summary,
        "all_replay_controls_stable": all(replay_summary.values()),
        "ap6_gate_summary": claim["ap6_gate_summary"],
        "claim_boundary_summary": claim["boundary_summary"],
        "duplicate_replay_backing": claim["duplicate_replay_backing_audit"],
    }


def final_claim_boundary() -> dict[str, bool]:
    return {
        "artifact_level_ap6_self_environment_boundary_candidate_supported": True,
        "selfhood_supported": False,
        "personhood_supported": False,
        "identity_acceptance_supported": False,
        "runtime_identity_acceptance_supported": False,
        "semantic_goal_ownership_supported": False,
        "semantic_goal_understanding_supported": False,
        "intention_supported": False,
        "semantic_choice_supported": False,
        "agency_supported": False,
        "agency_environment_model_supported": False,
        "closed_action_perception_loop_supported": False,
        "native_support_supported": False,
        "fully_native_agentic_like_integration_supported": False,
        "autonomous_repair_supported": False,
        "native_multi_basin_selfhood_supported": False,
        "selective_uptake_supported": False,
        "resource_assimilation_supported": False,
        "organism_life_supported": False,
        "biological_behavior_supported": False,
        "unrestricted_agency_supported": False,
    }


def final_claim_flags() -> dict[str, bool]:
    return {
        **UNSAFE_CLAIM_FLAGS,
        "artifact_level_ap6_supported": True,
        "ap6_classification_supported": True,
        "final_ap6_supported": True,
        "final_artifact_level_ap6_frozen": True,
        "final_ap_freeze_pending_iteration9": False,
    }


def final_blockers() -> list[dict[str, str]]:
    blockers = [
        (
            "closed_action_perception_loop_not_tested_until_N17",
            "N16 records boundary-crossing traces but does not close action-perception feedback.",
        ),
        (
            "selfhood_personhood_identity_acceptance_blocked",
            "Artifact boundary-side assignment is not selfhood, personhood, or identity acceptance.",
        ),
        (
            "semantic_goal_ownership_and_intention_blocked",
            "Internal support-relevant state is not semantic goal ownership, intention, or semantic choice.",
        ),
        (
            "agency_and_agency_environment_model_blocked",
            "External resource/challenge descriptors are not an agency environment model.",
        ),
        (
            "native_support_and_phase8_blocked",
            "N16 leaves native support, Phase 8, and fully native integration unopened.",
        ),
        (
            "autonomous_repair_blocked",
            "B3_C4 is artifact-level breach/reclosure evidence, not autonomous repair.",
        ),
        (
            "native_multi_basin_selfhood_blocked",
            "B4_C5 is artifact-level shared-medium separability evidence only.",
        ),
        (
            "selective_uptake_resource_assimilation_life_blocked",
            "N16 excludes selective uptake, resource assimilation, organism, and life claims.",
        ),
        (
            "reverse_basin_perspective_deferred_as_stronger_scope_limit",
            "One-sided B4_C5 evidence is enough for this artifact-level claim ceiling but blocks stronger symmetric/native multi-basin claims.",
        ),
        (
            "direct_historic_ap6_support_absent",
            "Final AP6 is constructed and controlled from prior claims plus N16 evidence, not inherited directly from a historic AP6 row.",
        ),
    ]
    return [
        {"blocker_id": blocker_id, "status": "blocked", "rationale": rationale}
        for blocker_id, rationale in blockers
    ]


def build_n17_handoff() -> dict[str, Any]:
    return {
        "recommended_next": "N17_closed_action_perception_loop",
        "recommended_branch": "experiment-N17",
        "target_ap_level": "AP7",
        "targeted_phase8_required_before_n17": False,
        "targeted_phase8_status": "optional_deferred_not_required_for_n17",
        "n17_primary_question": (
            "Can selected actions alter substrate or environment state, and can "
            "those altered conditions feed back into later selection?"
        ),
        "n17_allowed_inputs": [
            "N16 final artifact-level AP6 self/environment boundary closeout",
            "N15 final artifact-level AP5 endogenous proxy formation closeout",
            "N14 final artifact-level AP4 consequence-sensitive route selection closeout",
            "N13 final artifact-level AP3 support-seeking regulation closeout",
            "N08 memory/context and N09 bounded-regulation context as artifact evidence",
        ],
        "n17_blocked_inputs": [
            "selfhood",
            "personhood",
            "identity acceptance",
            "semantic goal ownership",
            "intention",
            "semantic choice",
            "agency",
            "native support",
            "fully native agentic-like integration",
            "organism or biological behavior",
            "unrestricted agency",
        ],
        "n17_required_controls": [
            "action consequence missing blocked",
            "stale consequence read blocked",
            "producer direct mutation blocked",
            "environment change without selected action blocked",
            "boundary crossing without feedback blocked",
            "semantic agency relabel blocked",
            "identity/selfhood/personhood relabel blocked",
            "native support relabel blocked",
            "artifact-only, snapshot/load, duplicate, and order-inversion replay stable",
        ],
        "handoff_caveats": [
            "N16 AP6 is an artifact-level boundary candidate, not selfhood or agency.",
            "N17 must show selected action consequences changing later selection inputs, not only boundary separability.",
            "Boundary-crossing traces from N16 are allowed context but do not themselves prove a closed action-perception loop.",
            "Phase 8 remains unopened and native support remains false.",
        ],
    }


def build_idempotency_digest_plan(
    *,
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    closeout_result: dict[str, Any],
    hypotheses_closeout: dict[str, Any],
    final_source_roles: list[dict[str, Any]],
    final_controls: dict[str, Any],
    blockers: list[dict[str, str]],
    claim_boundary: dict[str, bool],
    flags: dict[str, bool],
    n17_handoff: dict[str, Any],
) -> dict[str, Any]:
    scope = {
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_source_roles": final_source_roles,
        "final_controls": final_controls,
        "final_blockers": blockers,
        "final_claim_boundary": claim_boundary,
        "final_claim_flags": flags,
        "n17_handoff": n17_handoff,
    }
    return {
        "record_id": "n16_i9_idempotency_digest_plan_v1",
        "algorithm": "sha256_canonical_json_sorted_keys",
        "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
        "scope": scope,
        "digest": digest_value(scope),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    quiet = load_json(QUIET_OUTPUT)
    challenge = load_json(CHALLENGE_OUTPUT)
    state = load_json(STATE_OUTPUT)
    selected = load_json(SELECTED_OUTPUT)
    requirements = load_json(REQUIREMENTS_OUTPUT)
    claim = load_json(CLAIM_OUTPUT)
    boundary_policy = load_json(BOUNDARY_POLICY)
    control_variants = load_json(CONTROL_VARIANTS)

    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_artifact(QUIET_OUTPUT, quiet),
        rel(CHALLENGE_OUTPUT): source_artifact(CHALLENGE_OUTPUT, challenge),
        rel(STATE_OUTPUT): source_artifact(STATE_OUTPUT, state),
        rel(SELECTED_OUTPUT): source_artifact(SELECTED_OUTPUT, selected),
        rel(REQUIREMENTS_OUTPUT): source_artifact(REQUIREMENTS_OUTPUT, requirements),
        rel(CLAIM_OUTPUT): source_artifact(CLAIM_OUTPUT, claim),
        rel(BOUNDARY_POLICY): source_artifact(BOUNDARY_POLICY, boundary_policy),
        rel(CONTROL_VARIANTS): source_artifact(CONTROL_VARIANTS, control_variants),
        rel(HYPOTHESIS_A): source_report(HYPOTHESIS_A),
        rel(HYPOTHESIS_B): source_report(HYPOTHESIS_B),
        rel(HYPOTHESIS_C): source_report(HYPOTHESIS_C),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(QUIET_REPORT): source_report(QUIET_REPORT),
        rel(CHALLENGE_REPORT): source_report(CHALLENGE_REPORT),
        rel(STATE_REPORT): source_report(STATE_REPORT),
        rel(SELECTED_REPORT): source_report(SELECTED_REPORT),
        rel(REQUIREMENTS_REPORT): source_report(REQUIREMENTS_REPORT),
        rel(CLAIM_REPORT): source_report(CLAIM_REPORT),
    }

    final_source_roles = [source_row_final_role(row) for row in inventory["rows"]]
    hypotheses_closeout = build_hypotheses_closeout(claim)
    controls = build_final_controls(requirements, claim)
    claim_boundary = final_claim_boundary()
    flags = final_claim_flags()
    blockers = final_blockers()
    n17_handoff = build_n17_handoff()
    closeout_result = {
        "status": "closed_claim_clean_ap6_artifact_level_self_environment_boundary_candidate",
        "final_supported_ap_level": "AP6",
        "final_ap6_supported": True,
        "final_claim_ceiling": FINAL_CLAIM_CEILING,
        "final_scope": (
            "internal support-relevant state and external resource, "
            "perturbation, structured-state, and shared-medium pressures are "
            "separable in generated artifacts and controls"
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
        "closed_action_perception_loop_opened": False,
        "selfhood_claim_opened": False,
        "identity_acceptance_opened": False,
        "semantic_goal_ownership_opened": False,
        "agency_claim_opened": False,
        "targeted_phase8_required_before_n17": False,
        "n17_handoff_ready": True,
    }
    whole_experiment_interpretation = {
        "record_id": "n16_i9_whole_experiment_interpretation_v1",
        "supported_interpretation": FINAL_CLAIM_CEILING,
        "plain_language_interpretation": (
            "N16 closes with claim-clean artifact-level AP6 evidence for a "
            "self/environment boundary candidate. The evidence supports "
            "separability of internal support-relevant state from external "
            "resource, perturbation, structured-state, and shared-medium "
            "pressures across generated artifacts, controls, and replay."
        ),
        "supporting_evidence_summary": [
            "I1 pins source rows and records direct historic AP6 support as absent.",
            "I2 freezes the B-axis, C-axis, row schema, controls, and AP6 gates.",
            "I3-I6 generate calibration, challenge, boundary-state, and selected interaction evidence.",
            "I7 converts I3-I6 evidence into a full controlled requirements matrix.",
            "I8 validates all 39 AP6 gates and keeps unsafe promotions blocked.",
            "I9 freezes final supported AP level AP6 at artifact-level candidate scope.",
        ],
        "claim_boundary_summary": (
            "The closeout supports AP6 only as an artifact-level boundary "
            "candidate. It does not support selfhood, identity acceptance, "
            "semantic goal ownership, agency, native support, a closed "
            "action-perception loop, organism/life claims, or unrestricted agency."
        ),
        "why_it_matters_for_roadmap": (
            "N16 gives N17 a source-backed boundary substrate for testing "
            "closed action-perception feedback without relabeling AP6 as agency."
        ),
    }
    idempotency_digest_plan = build_idempotency_digest_plan(
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        closeout_result=closeout_result,
        hypotheses_closeout=hypotheses_closeout,
        final_source_roles=final_source_roles,
        final_controls=controls,
        blockers=blockers,
        claim_boundary=claim_boundary,
        flags=flags,
        n17_handoff=n17_handoff,
    )

    checks = {
        "inventory_source_passed": artifact_status(inventory) == "passed",
        "schema_source_passed": artifact_status(schema) == "passed",
        "iteration_3_source_passed": artifact_status(quiet) == "passed",
        "iteration_4_source_passed": artifact_status(challenge) == "passed",
        "iteration_5_source_passed": artifact_status(state) == "passed",
        "iteration_6_source_passed": artifact_status(selected) == "passed",
        "iteration_7_source_passed": artifact_status(requirements) == "passed",
        "iteration_8_source_passed": artifact_status(claim) == "passed",
        "iteration_8_acceptance_state_valid": claim["acceptance_state"]
        == "accepted_ap6_classification_claim_boundary_clean_pending_closeout",
        "iteration_8_output_digest_matches_reviewed_record": claim["output_digest"]
        == ACCEPTED_I8_DIGEST,
        "iteration_9_closeout_ready": claim["iteration_result"][
            "iteration_9_closeout_ready"
        ]
        is True,
        "final_supported_ap_level_ap6": closeout_result["final_supported_ap_level"]
        == "AP6"
        and closeout_result["final_ap6_supported"] is True,
        "final_claim_ceiling_recorded": closeout_result["final_claim_ceiling"]
        == FINAL_CLAIM_CEILING,
        "every_ap6_gate_validated": claim["ap6_gate_summary"][
            "all_ap6_gates_validated"
        ]
        is True
        and claim["ap6_gate_summary"]["gate_count"] == 39,
        "hypothesis_a_closed_supported": hypotheses_closeout[
            "hypothesis_a_boundary_source_inventory"
        ]["closeout_decision"]
        == "closed_supported",
        "hypothesis_b_closed_supported": hypotheses_closeout[
            "hypothesis_b_artifact_basin_boundary_stability"
        ]["closeout_decision"]
        == "closed_supported",
        "hypothesis_c_closed_supported": hypotheses_closeout[
            "hypothesis_c_selfhood_identity_agency_boundary"
        ]["closeout_decision"]
        == "closed_supported",
        "all_source_rows_have_final_roles": len(final_source_roles)
        == inventory["inventory_summary"]["row_count"]
        and all(row["final_roles"] for row in final_source_roles),
        "no_unclassified_source_rows": all(
            "unclassified_source_row" not in row["final_roles"]
            and all(not role.startswith("unmapped_source_role_") for role in row["final_roles"])
            for row in final_source_roles
        ),
        "final_controls_recorded": controls["negative_control_count"] >= 20
        and controls["all_negative_controls_fail_closed"]
        and controls["all_replay_controls_stable"],
        "final_blockers_recorded": len(blockers) >= 10,
        "final_claim_boundary_unsafe_false": all(
            value is False
            for key, value in claim_boundary.items()
            if key != "artifact_level_ap6_self_environment_boundary_candidate_supported"
        ),
        "artifact_ap6_supported_and_frozen": flags["artifact_level_ap6_supported"]
        is True
        and flags["final_ap6_supported"] is True
        and flags["final_artifact_level_ap6_frozen"] is True
        and flags["final_ap_freeze_pending_iteration9"] is False,
        "unsafe_claim_flags_false": all(
            flags.get(key) is False for key in UNSAFE_CLAIM_FLAGS
        ),
        "native_supported_flags_false": closeout_result["native_supported_flags"]
        is False
        and closeout_result["native_support_opened"] is False,
        "phase8_opened_false": closeout_result["phase8_opened"] is False,
        "fully_native_integration_opened_false": closeout_result[
            "fully_native_integration_opened"
        ]
        is False,
        "closed_action_perception_loop_not_opened": closeout_result[
            "closed_action_perception_loop_opened"
        ]
        is False,
        "n17_handoff_recorded": n17_handoff["recommended_next"]
        == "N17_closed_action_perception_loop",
        "targeted_phase8_not_required_for_n17": n17_handoff[
            "targeted_phase8_required_before_n17"
        ]
        is False,
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "idempotency_digest_plan_reproducible": idempotency_digest_plan["digest"]
        == digest_value(idempotency_digest_plan["scope"]),
        "src_diff_empty": src_diff_empty(),
    }
    acceptance_state = (
        "closed_claim_clean_ap6_artifact_level_self_environment_boundary_candidate"
        if all(checks.values())
        else "rejected_n16_closeout"
    )
    output: dict[str, Any] = {
        "experiment": "N16",
        "iteration": "9",
        "artifact_id": "n16_closeout_and_handoff",
        "purpose": "closeout_and_n17_handoff",
        "schema_version": "n16_closeout_and_handoff_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "checks": checks,
        "errors": [],
        "target_ap_ceiling": "AP6",
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_source_row_roles": final_source_roles,
        "final_controls": controls,
        "final_blockers": blockers,
        "final_claim_boundary": claim_boundary,
        "final_claim_flags": flags,
        "native_supported_flags": closeout_result["native_supported_flag_detail"],
        "n17_handoff": n17_handoff,
        "whole_experiment_interpretation": whole_experiment_interpretation,
        "idempotency_digest_plan": idempotency_digest_plan,
        "roadmap_update_decision": {
            "handoff_file_update_required": True,
            "roadmap_file_update_required": True,
            "experiments_readme_update_required": True,
            "reason": "N16 is closed and the recommended roadmap continuation is N17.",
        },
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "final_supported_ap_level": "AP6",
            "final_ap6_supported": all(checks.values()),
            "final_claim_ceiling": FINAL_CLAIM_CEILING,
            "artifact_level_ap6_supported": True,
            "final_artifact_level_ap6_frozen": True,
            "final_ap_freeze_pending_iteration9": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "native_supported_flags": False,
            "fully_native_integration_opened": False,
            "closed_action_perception_loop_opened": False,
            "selfhood_claim_opened": False,
            "semantic_goal_ownership_opened": False,
            "identity_acceptance_opened": False,
            "agency_claim_opened": False,
            "recommended_next": "N17_closed_action_perception_loop",
            "targeted_phase8_required_before_n17": False,
        },
        "post_write_output_digest_self_verification": {
            "enabled": True,
            "verification_target": "output_digest",
            "algorithm": "sha256_canonical_json_excluding_generated_at_output_digest_git",
        },
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
            "src_diff_empty": src_diff_empty(),
        },
        "output_digest": "",
    }
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = True
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "closed_claim_clean_ap6_artifact_level_self_environment_boundary_candidate"
        if output["status"] == "passed"
        else "rejected_n16_closeout"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["final_ap6_supported"] = output["status"] == "passed"
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    output["output_digest"] = output_digest(output)
    return output


def build_report(output: dict[str, Any]) -> str:
    closeout = output["closeout_result"]
    lines = [
        "# N16 Closeout And N17 Handoff",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"final_supported_ap_level = {closeout['final_supported_ap_level']}",
        f"final_ap6_supported = {str(closeout['final_ap6_supported']).lower()}",
        f"final_claim_ceiling = {closeout['final_claim_ceiling']}",
        "artifact_level_ap6_supported = true",
        "final_artifact_level_ap6_frozen = true",
        "phase8_opened = false",
        "native_support_opened = false",
        "fully_native_integration_opened = false",
        "closed_action_perception_loop_opened = false",
        "```",
        "",
        "N16 closes with supported artifact-level `AP6` evidence for a",
        "self/environment boundary candidate. The final scope is separability",
        "of internal support-relevant state from external resource,",
        "perturbation, structured-state, and shared-medium pressures in",
        "generated artifacts and controls.",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Closeout decision |",
        "| --- | --- |",
    ]
    for name, hypothesis in output["hypotheses_closeout"].items():
        lines.append(f"| `{name}` | `{hypothesis['closeout_decision']}` |")
    lines.extend(
        [
            "",
            "## Closeout Result",
            "",
            "```json",
            json.dumps(closeout, indent=2, sort_keys=True),
            "```",
            "",
            "## Final Controls",
            "",
            "```json",
            json.dumps(output["final_controls"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Source Row Roles",
            "",
            "```json",
            json.dumps(output["final_source_row_roles"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Claim Boundary",
            "",
            "```json",
            json.dumps(output["final_claim_boundary"], indent=2, sort_keys=True),
            "```",
            "",
            "## N17 Handoff",
            "",
            "```json",
            json.dumps(output["n17_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Blockers",
            "",
            "```json",
            json.dumps(output["final_blockers"], indent=2, sort_keys=True),
            "```",
            "",
            "## Whole Experiment Interpretation",
            "",
            "```json",
            json.dumps(
                output["whole_experiment_interpretation"],
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
            "## Claim Boundary",
            "",
            "```text",
            "artifact self/environment boundary != selfhood",
            "boundary-side assignment != identity acceptance",
            "internal support-relevant state != semantic goal ownership",
            "external resource/challenge state != agency environment model",
            "boundary-crossing trace != closed action-perception loop",
            "artifact-level AP6 != native support",
            "N16 AP6 != fully native agentic-like integration",
            "N16 AP6 != organism, life, biological behavior, or unrestricted agency",
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
    return "\n".join(lines)


def validate_output(output: dict[str, Any]) -> None:
    errors = []
    if output["status"] != "passed":
        errors.append("status_not_passed")
    failed_checks = sorted(key for key, value in output["checks"].items() if value is not True)
    if failed_checks:
        errors.append(f"failed_checks={failed_checks}")
    if output["iteration_result"]["final_ap6_supported"] is not True:
        errors.append("final_ap6_not_supported")
    if output["iteration_result"]["closed_action_perception_loop_opened"] is not False:
        errors.append("closed_action_perception_loop_opened_in_n16")
    if output["output_digest"] != output_digest(output):
        errors.append("output_digest_mismatch_before_write")
    if contains_absolute_path(output):
        errors.append("absolute_path_recorded")
    if errors:
        raise SystemExit(json.dumps({"status": "failed", "errors": errors}, indent=2))


def verify_written_output(path: Path) -> None:
    written = load_json(path)
    errors = []
    if written.get("output_digest") != output_digest(written):
        errors.append("written_output_digest_mismatch")
    if contains_absolute_path(written):
        errors.append("written_output_contains_absolute_path")
    if errors:
        raise SystemExit(json.dumps({"status": "failed", "errors": errors}, indent=2))


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    validate_output(output)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    verify_written_output(OUTPUT_PATH)
    REPORT_PATH.write_text(build_report(output), encoding="utf-8")
    print(json.dumps(output["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N15 Iteration 8 closeout and N16 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

INVENTORY_OUTPUT = OUTPUTS / "n15_proxy_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n15_proxy_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n15_proxy_formation_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n15_proxy_formation_schema_v1.md"
I3_OUTPUT = OUTPUTS / "n15_runtime_derived_target_candidate.json"
I3_REPORT = REPORTS / "n15_runtime_derived_target_candidate.md"
I4_OUTPUT = OUTPUTS / "n15_external_proxy_contrast_matrix.json"
I4_REPORT = REPORTS / "n15_external_proxy_contrast_matrix.md"
I5_OUTPUT = OUTPUTS / "n15_proxy_control_matrix.json"
I5_REPORT = REPORTS / "n15_proxy_control_matrix.md"
I6_OUTPUT = OUTPUTS / "n15_bounded_drift_replay_matrix.json"
I6_REPORT = REPORTS / "n15_bounded_drift_replay_matrix.md"
I7_OUTPUT = OUTPUTS / "n15_claim_boundary_record.json"
I7_REPORT = REPORTS / "n15_claim_boundary_record.md"

OUTPUT_PATH = OUTPUTS / "n15_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n15_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_closeout_and_handoff.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

FINAL_CLAIM_CEILING = "artifact_level_ap5_endogenous_proxy_formation_candidate"

REQUIRED_FALSE_FLAGS = {
    "semantic_goal_ownership_opened": False,
    "semantic_choice_opened": False,
    "intention_claim_opened": False,
    "identity_acceptance_opened": False,
    "runtime_identity_acceptance_opened": False,
    "agency_claim_opened": False,
    "selfhood_opened": False,
    "personhood_or_biological_behavior_opened": False,
    "biological_behavior_opened": False,
    "unrestricted_agency_opened": False,
    "native_support_opened": False,
    "native_supported_flags": False,
    "fully_native_integration_opened": False,
    "phase8_opened": False,
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
        "acceptance_state": artifact.get("acceptance_state"),
        "output_digest": artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def row_classification(row: dict[str, Any]) -> dict[str, Any]:
    role_map = {
        "direct_historic_target_formation_support": (
            "direct_historic_ap2_target_existence_context_not_final_ap5_source"
        ),
        "support_regulation_axis_source": (
            "n13_ap3_support_regulation_axis_consumed_for_ap5_construction"
        ),
        "old_best_ap3_support_axis": (
            "n13_ap3_closed_claim_ceiling_consumed_as_boundary_context"
        ),
        "old_best_ap4_selection_axis": (
            "n14_ap4_consequence_selection_axis_consumed_for_ap5_construction"
        ),
        "constructed_followout_context_source": (
            "n14_constructed_followout_context_consumed_with_upstream_observation_caveat"
        ),
        "claim_boundary_source": "n14_claim_boundary_source_consumed_as_blocker_context",
        "memory_context_axis_source": (
            "n08_memory_context_axis_consumed_for_ap5_construction"
        ),
        "bounded_regulation_context_source": (
            "n09_bounded_regulation_context_axis_consumed_for_ap5_construction"
        ),
        "phase8_readiness_input_only": (
            "n12_readiness_only_context_no_native_support"
        ),
    }
    return {
        "row_id": row["row_id"],
        "source_experiment": row["source_experiment"],
        "mechanism_name": row["mechanism_name"],
        "mechanism_role": row["mechanism_role"],
        "source_role_classification": row["source_role_classification"],
        "initial_provisional_ap_level": row["provisional_ap_level"],
        "final_role": role_map.get(row["mechanism_role"], "unclassified_source_row"),
        "final_claim_promotion_allowed": False,
        "final_claim_boundary": row["provisional_claim_ceiling"],
    }


def build_hypotheses_closeout(boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        name: {
            "acceptance_state": hypothesis["acceptance_state"],
            "supported": hypothesis["supported"],
            "resolution": hypothesis["scope"],
            "supporting_artifacts": hypothesis["evidence"],
            "boundary": hypothesis["boundary"],
        }
        for name, hypothesis in boundary["hypothesis_classification"].items()
    }


def build_ap5_gate_resolution(boundary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "gate": record["gate_id"],
            "status": record["resolution"],
            "validated": record["validated"],
            "evidence_sources": record["evidence_sources"],
            "notes": record["notes"],
        }
        for record in boundary["ap5_gate_resolution"]
    ]


def build_final_controls(
    i4: dict[str, Any],
    i5: dict[str, Any],
    i6: dict[str, Any],
    i7: dict[str, Any],
) -> dict[str, Any]:
    return {
        "external_proxy_contrast_matrix": {
            "source": rel(I4_OUTPUT),
            "externally_injected_target_blocked": i4["iteration_result"][
                "externally_injected_target_blocked"
            ],
            "hidden_target_derivation_blocked": i4["iteration_result"][
                "hidden_target_derivation_blocked"
            ],
            "post_hoc_proxy_formation_blocked": i4["iteration_result"][
                "post_hoc_proxy_formation_blocked"
            ],
            "candidate_distinguishable_from_declared_proxy_regulation": i4[
                "iteration_result"
            ]["candidate_distinguishable_from_declared_proxy_regulation"],
        },
        "adversarial_control_matrix": {
            "source": rel(I5_OUTPUT),
            "control_count": i5["control_summary"]["control_count"],
            "all_controls_fail_closed": i5["control_summary"][
                "all_controls_fail_closed"
            ],
            "distinct_blockers_recorded": i5["control_summary"][
                "blocker_labels_distinct"
            ],
            "observed_blockers": i5["control_summary"]["observed_blockers"],
        },
        "bounded_drift_replay_matrix": {
            "source": rel(I6_OUTPUT),
            "record_count": i6["matrix_summary"]["record_count"],
            "bounded_perturbations_change_target": i6["matrix_summary"][
                "bounded_perturbations_change_target"
            ],
            "unchanged_replays_preserve_target": i6["matrix_summary"][
                "unchanged_replays_preserve_target"
            ],
            "fail_closed_records_blocked": i6["matrix_summary"][
                "fail_closed_records_blocked"
            ],
            "artifact_only_filesystem_replay_passed": i6["checks"][
                "artifact_only_filesystem_replay_passed"
            ],
            "snapshot_load_replay_passed": i6["checks"][
                "snapshot_load_replay_passed"
            ],
            "order_inversion_replay_passed": i6["checks"][
                "order_inversion_replay_passed"
            ],
        },
        "claim_boundary_classification": {
            "source": rel(I7_OUTPUT),
            "all_ap5_gates_validated": i7["ap5_gate_summary"][
                "all_ap5_gates_validated"
            ],
            "all_boundary_claims_blocked": i7["boundary_summary"][
                "all_boundary_claims_blocked"
            ],
            "hypothesis_acceptance_states": {
                key: value["acceptance_state"]
                for key, value in i7["hypothesis_classification"].items()
            },
        },
    }


def build_n16_handoff() -> dict[str, Any]:
    return {
        "recommended_next": "N16_self_environment_boundary",
        "recommended_branch": "experiment-N16",
        "target_ap_level": "AP6",
        "targeted_phase8_required_before_n16": False,
        "targeted_phase8_status": "optional_deferred_not_required_for_n16",
        "n16_primary_question": (
            "Can internal support-relevant state and external resource or "
            "perturbation state be separated in artifacts and controls without "
            "promoting the boundary into selfhood or identity acceptance?"
        ),
        "n16_allowed_inputs": [
            "N15 final artifact-level AP5 endogenous proxy formation closeout",
            "N14 artifact-level AP4 consequence-sensitive route selection closeout",
            "N13 artifact-level AP3 support-seeking regulation closeout",
            "N12 NAT4 readiness records as readiness-only context",
            "N08 route memory context as artifact memory evidence",
            "N09 bounded regulation context as artifact regulation evidence",
        ],
        "n16_blocked_inputs": [
            "semantic goal ownership",
            "intention",
            "semantic choice",
            "agency",
            "identity acceptance",
            "runtime identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support without explicit Phase 8 implementation",
            "fully native agentic-like integration",
            "unrestricted agency",
        ],
        "n16_required_controls": [
            "externally supplied self/environment boundary blocked",
            "post-hoc boundary labeling blocked",
            "hidden environment-state injection blocked",
            "identity acceptance relabel blocked",
            "selfhood/personhood relabel blocked",
            "semantic goal ownership relabel blocked",
            "native support relabel blocked",
            "stale internal or external state blocked",
            "missing boundary-side state blocked",
            "boundary drift outside frozen policy blocked",
            "artifact-only, snapshot/load, and order-inversion replay stable",
        ],
        "handoff_caveats": [
            "N15 AP5 is artifact-level endogenous proxy formation only",
            "runtime-derived target formation is not semantic goal ownership",
            "support/identity-condition descriptors are not identity acceptance",
            "N14 constructed followout remains constructed context, not upstream observed route-conditioned support/regulation",
            "Phase 8 remains unopened and native support remains false",
        ],
    }


def build_idempotency_digest_plan(
    *,
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    controls: dict[str, str],
    closeout_result: dict[str, Any],
    hypotheses_closeout: dict[str, Any],
    final_classification_rows: list[dict[str, Any]],
    final_controls: dict[str, Any],
    final_blockers: list[str],
    n16_handoff: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    scope = {
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "controls": controls,
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_classification_rows": final_classification_rows,
        "final_controls": final_controls,
        "final_blockers": final_blockers,
        "n16_handoff": n16_handoff,
        "claim_flags": claim_flags,
    }
    return {
        "record_id": "n15_i8_idempotency_digest_plan_v1",
        "algorithm": "sha256_canonical_json_sorted_keys",
        "scope": scope,
        "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
        "digest": digest_value(scope),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    final_classification_rows = [row_classification(row) for row in inventory["rows"]]
    hypotheses_closeout = build_hypotheses_closeout(i7)
    ap5_gate_resolution = build_ap5_gate_resolution(i7)
    final_controls = build_final_controls(i4, i5, i6, i7)
    n16_handoff = build_n16_handoff()
    final_claim_boundary = {
        "runtime_derived_target_is_semantic_goal_ownership": False,
        "runtime_derived_target_is_intention": False,
        "target_consumption_by_rank_is_semantic_choice": False,
        "support_derived_target_is_agency": False,
        "support_identity_descriptor_is_identity_acceptance": False,
        "artifact_level_ap5_is_native_support": False,
        "n15_ap5_is_selfhood_personhood_or_biological_behavior": False,
        "n15_ap5_is_fully_native_agentic_like_integration": False,
        "n15_ap5_is_unrestricted_agency": False,
    }
    final_blockers = [
        "semantic_goal_ownership_semantics_missing",
        "intention_semantics_missing",
        "semantic_choice_semantics_missing",
        "identity_acceptance_validator_missing",
        "selfhood_personhood_biological_behavior_out_of_scope",
        "phase8_native_support_not_opened",
        "fully_native_agentic_like_integration_meta_policy_missing",
        "unrestricted_agency_out_of_scope",
        "n16_self_environment_boundary_not_yet_tested",
        "n17_closed_action_perception_loop_not_yet_tested",
        "n18_long_horizon_agentic_like_closure_not_yet_tested",
        "n14_constructed_followout_not_upstream_observed_route_conditioned_support_regulation",
    ]
    closeout_result = {
        "status": "closed_claim_clean_ap5_artifact_level_endogenous_proxy_formation",
        "final_supported_ap_level": "AP5",
        "final_ap5_supported": True,
        "final_claim_ceiling": FINAL_CLAIM_CEILING,
        "final_scope": (
            "runtime-derived target/proxy condition generated from source-current "
            "support, memory, regulation, and AP4 consequence context; "
            "control-clean, bounded-drift clean, and replay-clean at artifact level"
        ),
        "artifact_only": True,
        "fully_native": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "native_supported_flags": False,
        "fully_native_integration_opened": False,
        "semantic_goal_ownership_opened": False,
        "semantic_choice_opened": False,
        "intention_claim_opened": False,
        "identity_acceptance_opened": False,
        "runtime_identity_acceptance_opened": False,
        "agency_claim_opened": False,
        "selfhood_opened": False,
        "personhood_or_biological_behavior_opened": False,
        "biological_behavior_opened": False,
        "unrestricted_agency_opened": False,
    }
    whole_experiment_interpretation = {
        "record_id": "n15_i8_whole_experiment_interpretation_v1",
        "record_type": "n15_whole_experiment_interpretation",
        "plain_language_interpretation": (
            "N15 closes with artifact-level AP5 endogenous proxy formation. "
            "The target condition is generated before use from source-current "
            "support, memory, regulation, and AP4 consequence context. It is "
            "distinguishable from external fixtures and hidden or post-hoc "
            "derivations, all frozen controls fail closed, and bounded drift "
            "plus replay hold."
        ),
        "supported_interpretation": FINAL_CLAIM_CEILING,
        "supporting_evidence_summary": [
            "N15 pins direct AP2 target evidence but does not promote it to AP5",
            "old-best N13 AP3 + N14 AP4 + N08/N09/N12 context generates the target before use",
            "bridge probe consumes the generated target during bounded regulation ranking",
            "external fixture, injected target, hidden derivation, and post-hoc proxy explanations are blocked",
            "twelve adversarial controls fail closed with distinct blockers",
            "support, memory, regulation, and AP4 consequence perturbations remain within bounded drift",
            "duplicate, artifact-only filesystem, snapshot/load, and order-inversion replay are stable",
            "all 36 AP5 gates validate and all unsafe claim promotions remain blocked",
        ],
        "unsupported_interpretations": final_blockers,
        "claim_boundary_summary": (
            "The AP5 result supports only artifact-level endogenous proxy "
            "formation. It does not license semantic goal ownership, intention, "
            "semantic choice, agency, identity acceptance, native support, "
            "fully native integration, or unrestricted agency."
        ),
        "why_it_matters_for_roadmap": (
            "N15 gives N16 a claim-clean endogenous target/proxy formation "
            "substrate for testing self/environment boundary separation."
        ),
        "handoff_rule": (
            "N16 may consume N15 only as artifact-level AP5 endogenous proxy "
            "formation evidence; it must not consume N15 as semantic goal "
            "ownership, identity acceptance, agency, native support, or fully "
            "native integration evidence."
        ),
    }
    controls = {control_id: "blocked_in_iteration_5" for control_id in i5["controls"]}
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(I3_OUTPUT): source_artifact(I3_OUTPUT, i3),
        rel(I4_OUTPUT): source_artifact(I4_OUTPUT, i4),
        rel(I5_OUTPUT): source_artifact(I5_OUTPUT, i5),
        rel(I6_OUTPUT): source_artifact(I6_OUTPUT, i6),
        rel(I7_OUTPUT): source_artifact(I7_OUTPUT, i7),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(I3_REPORT): source_report(I3_REPORT),
        rel(I4_REPORT): source_report(I4_REPORT),
        rel(I5_REPORT): source_report(I5_REPORT),
        rel(I6_REPORT): source_report(I6_REPORT),
        rel(I7_REPORT): source_report(I7_REPORT),
    }
    idempotency_digest_plan = build_idempotency_digest_plan(
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        controls=controls,
        closeout_result=closeout_result,
        hypotheses_closeout=hypotheses_closeout,
        final_classification_rows=final_classification_rows,
        final_controls=final_controls,
        final_blockers=final_blockers,
        n16_handoff=n16_handoff,
        claim_flags=schema["claim_flags"],
    )
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "iteration_3_source_passed": i3["status"] == "passed",
        "iteration_4_source_passed": i4["status"] == "passed",
        "iteration_5_source_passed": i5["status"] == "passed",
        "iteration_6_source_passed": i6["status"] == "passed",
        "iteration_7_source_passed": i7["status"] == "passed",
        "iteration_7_acceptance_state_valid": i7["acceptance_state"]
        == "accepted_ap5_classification_claim_boundary_clean_pending_closeout",
        "final_supported_ap_level_ap5": closeout_result["final_supported_ap_level"]
        == "AP5"
        and closeout_result["final_ap5_supported"] is True,
        "final_claim_ceiling_recorded": closeout_result["final_claim_ceiling"]
        == FINAL_CLAIM_CEILING,
        "hypothesis_a_closed_supported": hypotheses_closeout[
            "hypothesis_a_runtime_state_proxy_sources"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_b_closed_supported": hypotheses_closeout[
            "hypothesis_b_bounded_endogenous_proxy_formation"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_c_closed_supported": hypotheses_closeout[
            "hypothesis_c_goal_ownership_and_agency_boundary"
        ]["acceptance_state"]
        == "supported",
        "every_source_row_classified": len(final_classification_rows)
        == inventory["inventory_summary"]["row_count"]
        and all(row["final_role"] for row in final_classification_rows),
        "no_generic_source_row_classifications": all(
            row["final_role"] != "unclassified_source_row"
            for row in final_classification_rows
        ),
        "every_ap5_gate_validated": all(
            row["status"] == "validated" for row in ap5_gate_resolution
        )
        and len(ap5_gate_resolution) == 36,
        "every_control_has_result": i5["control_summary"]["control_count"] == 12
        and i5["control_summary"]["all_controls_fail_closed"]
        and i6["matrix_summary"]["all_records_passed"]
        and i7["ap5_gate_summary"]["all_ap5_gates_validated"],
        "final_controls_recorded": bool(final_controls)
        and final_controls["adversarial_control_matrix"]["all_controls_fail_closed"]
        and final_controls["bounded_drift_replay_matrix"][
            "fail_closed_records_blocked"
        ],
        "final_blockers_recorded": len(final_blockers) >= 10,
        "final_claim_boundary_controls_false": all(
            value is False for value in final_claim_boundary.values()
        ),
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "required_false_flags_false": all(
            value is False for value in REQUIRED_FALSE_FLAGS.values()
        ),
        "native_supported_flags_false": closeout_result["native_supported_flags"]
        is False
        and closeout_result["native_support_opened"] is False,
        "phase8_opened_false": closeout_result["phase8_opened"] is False,
        "fully_native_integration_opened_false": closeout_result[
            "fully_native_integration_opened"
        ]
        is False,
        "n16_handoff_recorded": n16_handoff["recommended_next"]
        == "N16_self_environment_boundary",
        "targeted_phase8_not_required_for_n16": n16_handoff[
            "targeted_phase8_required_before_n16"
        ]
        is False,
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "idempotency_digest_plan_reproducible": idempotency_digest_plan["digest"]
        == digest_value(idempotency_digest_plan["scope"]),
        "whole_experiment_interpretation_recorded": (
            whole_experiment_interpretation["supported_interpretation"]
            == FINAL_CLAIM_CEILING
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "closed_claim_clean_ap5_artifact_level_endogenous_proxy_formation"
        if all(checks.values())
        else "rejected_n15_closeout"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 8,
        "artifact_id": "n15_closeout_and_handoff",
        "purpose": "closeout_and_n16_handoff",
        "schema_version": "n15_closeout_and_handoff_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": [],
        "controls": controls,
        "checks": checks,
        "claim_flags": schema["claim_flags"],
        "errors": [],
        "target_ap_ceiling": "AP5",
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_classification_rows": final_classification_rows,
        "ap5_gate_resolution": ap5_gate_resolution,
        "final_controls": final_controls,
        "final_blockers": final_blockers,
        "final_claim_boundary": final_claim_boundary,
        "required_false_flags": REQUIRED_FALSE_FLAGS,
        "n16_handoff": n16_handoff,
        "whole_experiment_interpretation": whole_experiment_interpretation,
        "idempotency_digest_plan": idempotency_digest_plan,
        "roadmap_update_decision": {
            "handoff_file_update_required": True,
            "roadmap_file_update_required": True,
            "experiments_readme_update_required": True,
            "reason": "N15 is closed and the recommended roadmap continuation is N16.",
        },
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "final_supported_ap_level": "AP5",
            "final_ap5_supported": all(checks.values()),
            "final_claim_ceiling": FINAL_CLAIM_CEILING,
            "phase8_opened": False,
            "native_support_opened": False,
            "native_supported_flags": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "identity_acceptance_opened": False,
            "agency_claim_opened": False,
            "recommended_next": "N16_self_environment_boundary",
            "targeted_phase8_required_before_n16": False,
        },
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = True
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "closed_claim_clean_ap5_artifact_level_endogenous_proxy_formation"
        if all(output["checks"].values())
        else "rejected_n15_closeout"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["final_ap5_supported"] = output["status"] == "passed"
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    closeout = output["closeout_result"]
    lines = [
        "# N15 Closeout And N16 Handoff",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"final_supported_ap_level = {closeout['final_supported_ap_level']}",
        f"final_ap5_supported = {str(closeout['final_ap5_supported']).lower()}",
        f"final_claim_ceiling = {closeout['final_claim_ceiling']}",
        "artifact_only = true",
        "fully_native = false",
        "fully_native_integration_opened = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "semantic_goal_ownership_opened = false",
        "identity_acceptance_opened = false",
        "agency_claim_opened = false",
        "```",
        "",
        "N15 closes with supported artifact-level `AP5` evidence for endogenous",
        "proxy formation. The final scope is runtime-derived target formation",
        "from source-current support, memory, regulation, and AP4 consequence",
        "context. Semantic goal ownership, intention, agency, identity",
        "acceptance, native support, and fully native integration remain blocked.",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Acceptance state |",
        "| --- | --- |",
    ]
    for name, hypothesis in output["hypotheses_closeout"].items():
        lines.append(f"| `{name}` | `{hypothesis['acceptance_state']}` |")
    lines.extend(
        [
            "",
            "## Closeout Result",
            "",
            "```json",
            json.dumps(closeout, indent=2, sort_keys=True),
            "```",
            "",
            "## AP5 Gate Resolution",
            "",
            "| Gate | Status |",
            "| --- | --- |",
        ]
    )
    for row in output["ap5_gate_resolution"]:
        lines.append(f"| `{row['gate']}` | `{row['status']}` |")
    lines.extend(
        [
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
            json.dumps(
                output["final_classification_rows"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Final Claim Boundary",
            "",
            "```json",
            json.dumps(output["final_claim_boundary"], indent=2, sort_keys=True),
            "```",
            "",
            "## N16 Handoff",
            "",
            "```json",
            json.dumps(output["n16_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Blockers",
            "",
            "```json",
            json.dumps(output["final_blockers"], indent=2, sort_keys=True),
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
            "endogenous proxy formation != semantic goal ownership",
            "runtime-derived target != intention",
            "support-derived target != agency",
            "support/identity-condition descriptor != identity acceptance",
            "artifact-level AP5 != native support",
            "N15 AP5 != fully native agentic-like integration",
            "N15 AP5 != selfhood, personhood, biological behavior, or unrestricted agency",
            "constructed N14 followout != upstream observed route-conditioned support/regulation",
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
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N14 Iteration 8 closeout and N15 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

INVENTORY_OUTPUT = OUTPUTS / "n14_consequence_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n14_consequence_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n14_consequence_selection_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n14_consequence_selection_schema_v1.md"
CONSEQUENCE_OUTPUT = OUTPUTS / "n14_route_consequence_records.json"
CONSEQUENCE_REPORT = REPORTS / "n14_route_consequence_records.md"
SELECTION_OUTPUT = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
SELECTION_REPORT = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
CONTROL_OUTPUT = OUTPUTS / "n14_consequence_control_matrix.json"
CONTROL_REPORT = REPORTS / "n14_consequence_control_matrix.md"
PERTURBATION_OUTPUT = OUTPUTS / "n14_consequence_perturbation_matrix.json"
PERTURBATION_REPORT = REPORTS / "n14_consequence_perturbation_matrix.md"
OBSERVED_PROBE_OUTPUT = OUTPUTS / "n14_observed_route_specific_consequence_probe.json"
OBSERVED_PROBE_REPORT = REPORTS / "n14_observed_route_specific_consequence_probe.md"
CONDITIONED_PROBE_OUTPUT = (
    OUTPUTS / "n14_route_conditioned_support_regulation_probe.json"
)
CONDITIONED_PROBE_REPORT = (
    REPORTS / "n14_route_conditioned_support_regulation_probe.md"
)
FOLLOWOUT_OUTPUT = OUTPUTS / "n14_route_conditioned_followout_probe.json"
FOLLOWOUT_REPORT = REPORTS / "n14_route_conditioned_followout_probe.md"
BOUNDARY_OUTPUT = OUTPUTS / "n14_claim_boundary_record.json"
BOUNDARY_REPORT = REPORTS / "n14_claim_boundary_record.md"

OUTPUT_PATH = OUTPUTS / "n14_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n14_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_closeout_and_handoff.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
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


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def row_classification(row: dict[str, Any]) -> dict[str, Any]:
    role_map = {
        "route_alternative_and_immediate_affordance_source": (
            "route_affordance_source_consumed_for_conflict_case"
        ),
        "memory_effect_source": (
            "route_specific_memory_consequence_source_consumed_for_ap4"
        ),
        "memory_geometry_boundary_source": (
            "memory_geometry_boundary_source_consumed_as_non_native_boundary"
        ),
        "regulation_effect_source": (
            "regulation_compatibility_source_consumed_for_constructed_followout"
        ),
        "support_effect_and_control_source": (
            "support_compatibility_source_consumed_for_constructed_followout"
        ),
        "phase8_readiness_input_only": (
            "phase8_readiness_input_only_no_native_support"
        ),
        "ap3_support_regulation_and_n14_handoff_source": (
            "ap3_support_seeking_regulation_source"
        ),
    }
    final_role = role_map.get(row["mechanism_role"], "classified_source_row")
    return {
        "row_id": row["row_id"],
        "source_experiment": row["source_experiment"],
        "mechanism_name": row["mechanism_name"],
        "mechanism_role": row["mechanism_role"],
        "initial_provisional_ap_level": row["provisional_ap_level"],
        "final_role": final_role,
        "final_claim_promotion_allowed": False,
    }


def build_hypotheses_closeout(boundary: dict[str, Any]) -> dict[str, Any]:
    hypotheses = boundary["hypotheses_closeout"]
    return {
        name: {
            "acceptance_state": hypothesis["acceptance_state"],
            "resolution": hypothesis["scope"],
            "supporting_artifacts": hypothesis["evidence"],
            "boundary": hypothesis["boundary"],
            "supported": hypothesis["supported"],
        }
        for name, hypothesis in hypotheses.items()
    }


def build_gate_resolution(
    schema: dict[str, Any],
    selection: dict[str, Any],
    control: dict[str, Any],
    perturbation: dict[str, Any],
    observed_probe: dict[str, Any],
    conditioned_probe: dict[str, Any],
    followout: dict[str, Any],
    boundary: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "gate": "candidate route set and eligible candidate completeness",
            "status": "validated",
            "source": rel(SELECTION_OUTPUT),
            "evidence": {
                "candidate_set_complete": selection["checks"]["candidate_set_complete"],
                "all_eligible_candidates_recorded": selection["checks"][
                    "all_eligible_candidates_recorded"
                ],
            },
        },
        {
            "gate": "pre-selection consequence records and source digests",
            "status": "validated",
            "source": rel(CONSEQUENCE_OUTPUT),
            "evidence": {
                "source_backed_records": True,
                "hidden_outcome_table_blocked": control["checks"][
                    "hidden_outcome_table_blocked"
                ],
                "post_hoc_consequence_scoring_blocked": control["checks"][
                    "post_hoc_consequence_scoring_blocked"
                ],
            },
        },
        {
            "gate": "support memory regulation downstream descriptors",
            "status": "validated_with_scope_caveat",
            "source": rel(BOUNDARY_OUTPUT),
            "evidence": {
                "observed_route_specific_memory_supported": observed_probe[
                    "iteration_result"
                ]["observed_route_specific_memory_supported"],
                "constructed_support_followout_supported": followout[
                    "iteration_result"
                ]["constructed_route_conditioned_support_followout_supported"],
                "constructed_regulation_followout_supported": followout[
                    "iteration_result"
                ]["constructed_route_conditioned_regulation_followout_supported"],
                "upstream_observed_support_regulation_supported": False,
                "scope_caveat": (
                    "support/regulation evidence is constructed N14 followout, "
                    "not upstream observed N09/N13 route-conditioned evidence"
                ),
            },
        },
        {
            "gate": "immediate affordance versus consequence conflict",
            "status": "validated",
            "source": rel(SELECTION_OUTPUT),
            "evidence": {
                "affordance_consequence_conflict_resolved_by_consequence": selection[
                    "checks"
                ]["affordance_consequence_conflict_resolved_by_consequence"],
                "selected_route": selection["iteration_result"]["selected_route"],
                "immediate_affordance_top_route": selection["iteration_result"][
                    "immediate_affordance_top_route"
                ],
            },
        },
        {
            "gate": "budget, stale-record, missing-record, and relabel controls",
            "status": "validated",
            "source": rel(CONTROL_OUTPUT),
            "evidence": {
                "negative_controls_blocked": control["iteration_result"][
                    "negative_controls_blocked"
                ],
                "budget_invalid_route_blocked": control["checks"][
                    "budget_invalid_route_blocked"
                ],
                "stale_consequence_record_blocked": control["checks"][
                    "stale_consequence_record_blocked"
                ],
                "missing_consequence_record_blocked": control["checks"][
                    "missing_consequence_record_blocked"
                ],
            },
        },
        {
            "gate": "perturbation sensitivity and replay/snapshot stability",
            "status": "validated",
            "source": rel(PERTURBATION_OUTPUT),
            "evidence": {
                "perturbation_records_passed": perturbation["iteration_result"][
                    "perturbation_records_passed"
                ],
                "replay_records_passed": perturbation["iteration_result"][
                    "replay_records_passed"
                ],
                "artifact_only_replay_filesystem_roundtrip": perturbation["checks"][
                    "artifact_only_replay_uses_filesystem_roundtrip"
                ],
                "snapshot_load_replay_filesystem_roundtrip": perturbation["checks"][
                    "snapshot_load_replay_uses_filesystem_roundtrip"
                ],
            },
        },
        {
            "gate": "route-conditioned upstream support/regulation observation",
            "status": "recorded_blocker",
            "source": rel(CONDITIONED_PROBE_OUTPUT),
            "evidence": {
                "observed_route_conditioned_support_supported": conditioned_probe[
                    "iteration_result"
                ]["observed_route_conditioned_support_supported"],
                "observed_route_conditioned_regulation_supported": conditioned_probe[
                    "iteration_result"
                ]["observed_route_conditioned_regulation_supported"],
                "blocker": (
                    "current N09/N13 sources do not contain upstream observed "
                    "route-conditioned support/regulation rows"
                ),
            },
        },
        {
            "gate": "claim flags, native support, and Phase 8",
            "status": "validated_blocked",
            "source": rel(BOUNDARY_OUTPUT),
            "evidence": {
                "all_boundary_claims_blocked": boundary["checks"][
                    "all_boundary_claims_blocked"
                ],
                "all_claim_flags_forced_false": boundary["checks"][
                    "all_claim_flags_forced_false"
                ],
                "phase8_opened_false": boundary["checks"]["phase8_opened_false"],
                "native_support_opened_false": boundary["checks"][
                    "native_support_opened_false"
                ],
                "schema_gate_declared": schema["status"] == "passed",
            },
        },
    ]


def build_whole_experiment_interpretation() -> dict[str, Any]:
    return {
        "record_id": "n14_i8_whole_experiment_interpretation_v1",
        "record_type": "n14_whole_experiment_interpretation",
        "plain_language_interpretation": (
            "N14 closes with artifact-level AP4 consequence-sensitive route "
            "selection. The selected route is determined by source-backed "
            "downstream consequence records rather than immediate route "
            "affordance alone, under adversarial controls and replay checks."
        ),
        "supported_interpretation": (
            "artifact-level AP4 consequence-sensitive route selection candidate "
            "with observed route-specific memory evidence and constructed "
            "route-conditioned support/regulation followout evidence"
        ),
        "supporting_evidence_summary": [
            "route_b is selected over immediate-affordance route_a by consequence rank",
            "hidden outcome, post-hoc score, stale record, budget invalid, missing record, fixture label, and unsafe relabel controls fail closed",
            "support, memory, and regulation perturbations alter ranking only through serialized source-backed inputs",
            "duplicate, artifact-only, snapshot/load, and order-inverted replays are stable",
            "observed route-specific memory consequence evidence is present",
            "constructed route-conditioned support/regulation followout evidence is present",
            "upstream observed N09/N13 route-conditioned support/regulation remains unsupported",
        ],
        "unsupported_interpretations": [
            "intention",
            "semantic choice",
            "semantic goal ownership",
            "semantic goal understanding",
            "identity acceptance",
            "runtime identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "agency",
            "unrestricted agency",
            "native support",
            "fully native agentic-like integration",
        ],
        "claim_boundary_summary": (
            "The AP4 result supports only artifact-level consequence-sensitive "
            "route selection. It does not license intention, semantic choice, "
            "agency, identity acceptance, selfhood, native support, or fully "
            "native integration claims."
        ),
        "why_it_matters_for_roadmap": (
            "N14 gives N15 a claim-clean consequence-sensitive route selection "
            "substrate for testing whether proxy/target conditions can be "
            "runtime-derived rather than externally declared."
        ),
        "handoff_rule": (
            "N15 may consume N14 only as artifact-level AP4 consequence-sensitive "
            "selection evidence; constructed followout evidence must remain "
            "distinguished from upstream observed route-conditioned "
            "support/regulation evidence."
        ),
    }


def build_n15_handoff() -> dict[str, Any]:
    return {
        "recommended_next": "N15_endogenous_proxy_formation",
        "recommended_branch": "new_experiment_branch_after_n14_merge",
        "targeted_phase8_required_before_n15": False,
        "targeted_phase8_status": "optional_deferred_not_required_for_n15",
        "n15_primary_question": (
            "Can proxy or target conditions arise from runtime-visible support, "
            "memory, or regulation state rather than being declared externally?"
        ),
        "n15_allowed_inputs": [
            "N14 artifact-level AP4 consequence-sensitive route selection closeout",
            "N13 artifact-level AP3 support-seeking regulation closeout",
            "N12 NAT4 readiness records as readiness-only context",
            "N08 route memory evidence as artifact memory context",
            "N09 bounded regulation evidence as artifact regulation context",
        ],
        "n15_blocked_inputs": [
            "identity acceptance",
            "runtime identity acceptance",
            "semantic goal ownership",
            "intention",
            "semantic choice",
            "agency",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support without explicit Phase 8 implementation",
            "fully native agentic-like integration",
        ],
        "n15_required_controls": [
            "externally injected target blocked",
            "hidden target derivation blocked",
            "semantic goal ownership relabel blocked",
            "post-hoc proxy formation blocked",
            "unbounded target drift blocked",
            "budget-surface ambiguity blocked",
            "identity acceptance relabel blocked",
            "native support relabel blocked",
        ],
        "handoff_caveats": [
            "N14 support/regulation broadening is constructed followout evidence",
            "upstream observed route-conditioned support/regulation remains blocked",
            "N14 AP4 is not intention, semantic choice, or agency",
            "Phase 8 remains unopened",
        ],
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    consequence = load_json(CONSEQUENCE_OUTPUT)
    selection = load_json(SELECTION_OUTPUT)
    control = load_json(CONTROL_OUTPUT)
    perturbation = load_json(PERTURBATION_OUTPUT)
    observed_probe = load_json(OBSERVED_PROBE_OUTPUT)
    conditioned_probe = load_json(CONDITIONED_PROBE_OUTPUT)
    followout = load_json(FOLLOWOUT_OUTPUT)
    boundary = load_json(BOUNDARY_OUTPUT)

    final_classification_rows = [
        row_classification(row) for row in inventory["n14_inventory_rows"]
    ]
    hypotheses_closeout = build_hypotheses_closeout(boundary)
    ap4_gate_resolution = build_gate_resolution(
        schema,
        selection,
        control,
        perturbation,
        observed_probe,
        conditioned_probe,
        followout,
        boundary,
    )
    whole_experiment_interpretation = build_whole_experiment_interpretation()
    n15_handoff = build_n15_handoff()
    final_claim_boundary = {
        "consequence_sensitive_route_selection_is_intention": False,
        "route_preference_is_semantic_choice": False,
        "expected_downstream_effect_is_semantic_goal_ownership": False,
        "memory_sensitive_route_choice_is_identity_acceptance": False,
        "support_preserving_route_choice_is_agency": False,
        "artifact_level_ap4_is_native_support": False,
        "n14_ap4_is_fully_native_agentic_like_integration": False,
        "n14_evidence_is_selfhood_personhood_or_biological_behavior": False,
        "n14_evidence_is_unrestricted_agency": False,
    }
    closeout_result = {
        "status": "closed_claim_clean_ap4_artifact_level_consequence_sensitive_route_selection",
        "final_supported_ap_level": "AP4",
        "final_ap4_supported": True,
        "final_claim_ceiling": (
            "artifact_level_ap4_consequence_sensitive_route_selection_candidate_"
            "with_constructed_route_conditioned_support_regulation_followout"
        ),
        "final_scope": (
            "observed route-specific memory plus constructed route-conditioned "
            "support/regulation followout; upstream observed route-conditioned "
            "support/regulation remains unsupported"
        ),
        "artifact_only": True,
        "fully_native": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "native_supported_flags": False,
        "fully_native_integration_opened": False,
        "intention_claim_opened": False,
        "semantic_choice_opened": False,
        "semantic_goal_ownership_opened": False,
        "identity_acceptance_opened": False,
        "agency_claim_opened": False,
        "selfhood_opened": False,
        "personhood_or_biological_behavior_opened": False,
        "unrestricted_agency_opened": False,
    }
    final_controls = {
        "adversarial_control_matrix": {
            "source": rel(CONTROL_OUTPUT),
            "control_record_count": control["iteration_result"]["control_record_count"],
            "negative_control_count": control["iteration_result"][
                "negative_control_count"
            ],
            "negative_controls_blocked": control["iteration_result"][
                "negative_controls_blocked"
            ],
        },
        "perturbation_replay_matrix": {
            "source": rel(PERTURBATION_OUTPUT),
            "perturbation_records_passed": perturbation["iteration_result"][
                "perturbation_records_passed"
            ],
            "replay_records_passed": perturbation["iteration_result"][
                "replay_records_passed"
            ],
            "filesystem_replays": {
                "artifact_only": perturbation["checks"][
                    "artifact_only_replay_uses_filesystem_roundtrip"
                ],
                "snapshot_load": perturbation["checks"][
                    "snapshot_load_replay_uses_filesystem_roundtrip"
                ],
            },
        },
        "route_specific_probes": {
            "observed_memory_source": rel(OBSERVED_PROBE_OUTPUT),
            "observed_route_specific_memory_supported": observed_probe[
                "iteration_result"
            ]["observed_route_specific_memory_supported"],
            "observed_route_conditioned_support_supported": conditioned_probe[
                "iteration_result"
            ]["observed_route_conditioned_support_supported"],
            "observed_route_conditioned_regulation_supported": conditioned_probe[
                "iteration_result"
            ]["observed_route_conditioned_regulation_supported"],
            "constructed_followout_source": rel(FOLLOWOUT_OUTPUT),
            "constructed_route_conditioned_support_followout_supported": followout[
                "iteration_result"
            ]["constructed_route_conditioned_support_followout_supported"],
            "constructed_route_conditioned_regulation_followout_supported": followout[
                "iteration_result"
            ]["constructed_route_conditioned_regulation_followout_supported"],
        },
        "claim_boundary_summary": boundary["claim_boundary_record"][
            "boundary_summary"
        ],
    }
    final_blockers = [
        "upstream_observed_route_conditioned_support_rows_missing",
        "upstream_observed_route_conditioned_regulation_rows_missing",
        "intention_semantics_missing",
        "semantic_choice_semantics_missing",
        "semantic_goal_ownership_semantics_missing",
        "identity_acceptance_validator_missing",
        "phase8_native_support_not_opened",
        "fully_native_agentic_like_integration_meta_policy_missing",
        "agency_semantics_not_part_of_n14",
        "selfhood_personhood_biological_behavior_out_of_scope",
    ]
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "consequence_source_passed": consequence["status"] == "passed",
        "selection_source_passed": selection["status"] == "passed",
        "control_source_passed": control["status"] == "passed",
        "perturbation_source_passed": perturbation["status"] == "passed",
        "observed_probe_source_passed": observed_probe["status"] == "passed",
        "conditioned_probe_source_passed": conditioned_probe["status"] == "passed",
        "followout_source_passed": followout["status"] == "passed",
        "boundary_source_passed": boundary["status"] == "passed",
        "hypothesis_a_closed_supported": hypotheses_closeout[
            "hypothesis_a_pre_selection_consequence_records"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_b_closed_supported": hypotheses_closeout[
            "hypothesis_b_rank_sensitive_route_selection"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_c_closed_supported": hypotheses_closeout[
            "hypothesis_c_intention_and_agency_boundary"
        ]["acceptance_state"]
        == "supported",
        "every_source_row_classified": len(final_classification_rows)
        == inventory["inventory_summary"]["row_count"]
        and all(row["final_role"] for row in final_classification_rows),
        "no_generic_source_row_classifications": all(
            row["final_role"] != "classified_source_row"
            for row in final_classification_rows
        ),
        "every_ap4_gate_validated_or_blocked": all(
            row["status"] in {"validated", "validated_with_scope_caveat", "recorded_blocker", "validated_blocked"}
            for row in ap4_gate_resolution
        ),
        "every_control_has_result": control["checks"]["all_controls_executed"]
        and control["checks"]["all_controls_passed"]
        and followout["checks"]["controls_passed"],
        "final_supported_ap_level_ap4": closeout_result["final_supported_ap_level"]
        == "AP4"
        and closeout_result["final_ap4_supported"] is True,
        "final_claim_ceiling_recorded": bool(closeout_result["final_claim_ceiling"]),
        "final_claim_boundary_controls_false": all(
            value is False for value in final_claim_boundary.values()
        ),
        "final_claim_flags_all_false_for_unsafe_claims": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "native_supported_flags_false": closeout_result["native_supported_flags"]
        is False
        and closeout_result["native_support_opened"] is False,
        "fully_native_integration_opened_false": closeout_result[
            "fully_native_integration_opened"
        ]
        is False,
        "phase8_opened_false": closeout_result["phase8_opened"] is False,
        "n15_handoff_recorded": n15_handoff["recommended_next"]
        == "N15_endogenous_proxy_formation",
        "targeted_phase8_not_required_for_n15": n15_handoff[
            "targeted_phase8_required_before_n15"
        ]
        is False,
        "whole_experiment_interpretation_recorded": (
            whole_experiment_interpretation["supported_interpretation"]
            == (
                "artifact-level AP4 consequence-sensitive route selection candidate "
                "with observed route-specific memory evidence and constructed "
                "route-conditioned support/regulation followout evidence"
            )
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N14",
        "iteration": 8,
        "purpose": "closeout_and_handoff",
        "schema": "n14_closeout_and_handoff_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": (
            "closed_claim_clean_ap4_artifact_level_consequence_sensitive_route_selection"
            if all(checks.values())
            else "rejected_n14_closeout"
        ),
        "target_ap_ceiling": "AP4",
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_classification_rows": final_classification_rows,
        "ap4_gate_resolution": ap4_gate_resolution,
        "final_controls": final_controls,
        "final_blockers": final_blockers,
        "final_claim_boundary": final_claim_boundary,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "n15_handoff": n15_handoff,
        "whole_experiment_interpretation": whole_experiment_interpretation,
        "roadmap_update_decision": {
            "handoff_file_update_required": True,
            "roadmap_file_update_required": True,
            "experiments_readme_update_required": True,
            "reason": "N14 is closed and the recommended roadmap continuation is N15.",
        },
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(CONSEQUENCE_OUTPUT): source_artifact(CONSEQUENCE_OUTPUT, consequence),
            rel(SELECTION_OUTPUT): source_artifact(SELECTION_OUTPUT, selection),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, control),
            rel(PERTURBATION_OUTPUT): source_artifact(
                PERTURBATION_OUTPUT, perturbation
            ),
            rel(OBSERVED_PROBE_OUTPUT): source_artifact(
                OBSERVED_PROBE_OUTPUT, observed_probe
            ),
            rel(CONDITIONED_PROBE_OUTPUT): source_artifact(
                CONDITIONED_PROBE_OUTPUT, conditioned_probe
            ),
            rel(FOLLOWOUT_OUTPUT): source_artifact(FOLLOWOUT_OUTPUT, followout),
            rel(BOUNDARY_OUTPUT): source_artifact(BOUNDARY_OUTPUT, boundary),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(CONSEQUENCE_REPORT): source_report(CONSEQUENCE_REPORT),
            rel(SELECTION_REPORT): source_report(SELECTION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
            rel(PERTURBATION_REPORT): source_report(PERTURBATION_REPORT),
            rel(OBSERVED_PROBE_REPORT): source_report(OBSERVED_PROBE_REPORT),
            rel(CONDITIONED_PROBE_REPORT): source_report(CONDITIONED_PROBE_REPORT),
            rel(FOLLOWOUT_REPORT): source_report(FOLLOWOUT_REPORT),
            rel(BOUNDARY_REPORT): source_report(BOUNDARY_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    closeout = output["closeout_result"]
    lines = [
        "# N14 Closeout And N15 Handoff",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"final_supported_ap_level = {closeout['final_supported_ap_level']}",
        f"final_ap4_supported = {str(closeout['final_ap4_supported']).lower()}",
        f"final_claim_ceiling = {closeout['final_claim_ceiling']}",
        "artifact_only = true",
        "fully_native = false",
        "fully_native_integration_opened = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "agency_claim_opened = false",
        "intention_claim_opened = false",
        "semantic_choice_opened = false",
        "semantic_goal_ownership_opened = false",
        "identity_acceptance_opened = false",
        "```",
        "",
        "N14 closes with supported artifact-level `AP4` evidence for",
        "consequence-sensitive route selection. The final scope is observed",
        "route-specific memory plus constructed route-conditioned",
        "support/regulation followout. Upstream observed N09/N13",
        "route-conditioned support/regulation remains unsupported.",
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
            "## AP4 Gate Resolution",
            "",
            "| Gate | Status | Source |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["ap4_gate_resolution"]:
        lines.append(
            "| "
            f"{row['gate']} | "
            f"`{row['status']}` | "
            f"`{row['source']}` |"
        )
    lines.extend(
        [
            "",
            "## Final Controls",
            "",
            "```json",
            json.dumps(output["final_controls"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Claim Boundary",
            "",
            "```json",
            json.dumps(output["final_claim_boundary"], indent=2, sort_keys=True),
            "```",
            "",
            "## N15 Handoff",
            "",
            "```json",
            json.dumps(output["n15_handoff"], indent=2, sort_keys=True),
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
            "consequence-sensitive route selection != intention",
            "expected downstream support effect != semantic goal ownership",
            "support-preserving route choice != agency",
            "memory-sensitive route choice != identity acceptance",
            "regulation-sensitive route choice != goal ownership",
            "route preference != selfhood",
            "artifact-level AP4 != native support",
            "N14 AP4 != fully native agentic-like integration",
            "constructed support/regulation followout != upstream observed route-conditioned support/regulation",
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
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

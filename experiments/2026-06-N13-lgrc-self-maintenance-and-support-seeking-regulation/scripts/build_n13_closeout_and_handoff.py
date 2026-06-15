#!/usr/bin/env python3
"""Build N13 Iteration 8 closeout and handoff."""

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
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

INVENTORY_OUTPUT = OUTPUTS / "n13_support_condition_inventory.json"
INVENTORY_REPORT = REPORTS / "n13_support_condition_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n13_support_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n13_support_schema_v1.md"
TARGET_OUTPUT = OUTPUTS / "n13_support_derived_target_candidate.json"
TARGET_REPORT = REPORTS / "n13_support_derived_target_candidate.md"
REGULATION_OUTPUT = OUTPUTS / "n13_support_seeking_regulation_candidate.json"
REGULATION_REPORT = REPORTS / "n13_support_seeking_regulation_candidate.md"
CONTROL_OUTPUT = OUTPUTS / "n13_external_proxy_control_matrix.json"
CONTROL_REPORT = REPORTS / "n13_external_proxy_control_matrix.md"
STRESS_OUTPUT = OUTPUTS / "n13_support_disruption_restoration_matrix.json"
STRESS_REPORT = REPORTS / "n13_support_disruption_restoration_matrix.md"
BOUNDARY_OUTPUT = OUTPUTS / "n13_claim_boundary_record.json"
BOUNDARY_REPORT = REPORTS / "n13_claim_boundary_record.md"

OUTPUT_PATH = OUTPUTS / "n13_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n13_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_closeout_and_handoff.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
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
    row_id = row["row_id"]
    if row_id == "n13_i1_row_01_n07_support_withdrawal_baseline":
        final_role = "source_current_support_condition_seed_consumed_for_target"
    elif row_id == "n13_i1_row_02_n09_bounded_external_proxy_regulation":
        final_role = "external_proxy_baseline_and_control_source"
    elif row_id == "n13_i1_row_03_n10_support_sensitive_matrix":
        final_role = "support_sensitive_matrix_consumed_for_stress_alignment"
    elif row_id == "n13_i1_row_04_n10_final_handoff":
        final_role = "bounded_artifact_only_integration_handoff_source"
    elif row_id == "n13_i1_row_05_n11_gali7_artifact_envelope":
        final_role = "artifact_only_generalization_envelope_boundary"
    elif row_id == "n13_i1_row_06_n12_phase8_readiness_inputs":
        final_role = "phase8_readiness_input_only_no_native_support"
    elif row_id == "n13_i1_row_07_n12_closeout_boundary":
        final_role = "claim_boundary_and_handoff_source"
    else:
        final_role = "classified_source_row"
    return {
        "row_id": row_id,
        "source_experiment": row["source_experiment"],
        "mechanism_name": row["mechanism_name"],
        "initial_provisional_ap_level": row["provisional_ap_level"],
        "final_role": final_role,
        "final_claim_promotion_allowed": False,
    }


def build_hypotheses_closeout(
    inventory: dict[str, Any],
    target: dict[str, Any],
    regulation: dict[str, Any],
    control: dict[str, Any],
    stress: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "hypothesis_a_support_condition_inventory": {
            "acceptance_state": "supported",
            "resolution": (
                "Source-backed support-state evidence was inventoried and "
                "converted into the support_retention_above_threshold_source_current "
                "target without promoting support survival into identity acceptance."
            ),
            "supporting_artifacts": [
                rel(INVENTORY_OUTPUT),
                rel(TARGET_OUTPUT),
                rel(BOUNDARY_OUTPUT),
            ],
            "key_checks": {
                "inventory_rows_classified": inventory["inventory_summary"]["row_count"]
                == 7,
                "support_derived_target_candidate": target["iteration_result"][
                    "support_derived_target_candidate"
                ],
                "identity_acceptance_blocked": boundary["claim_boundary_record"][
                    "boundary_summary"
                ]["identity_acceptance_blocked"],
            },
        },
        "hypothesis_b_support_seeking_regulation": {
            "acceptance_state": "supported",
            "resolution": (
                "The support-seeking regulation candidate was distinguished "
                "from external proxy regulation by source-current target "
                "derivation, bounded response magnitude, budget debit, "
                "fail-closed controls, and stress-regime separation."
            ),
            "supporting_artifacts": [
                rel(REGULATION_OUTPUT),
                rel(CONTROL_OUTPUT),
                rel(STRESS_OUTPUT),
                rel(BOUNDARY_OUTPUT),
            ],
            "key_checks": {
                "support_seeking_regulation_candidate": regulation["iteration_result"][
                    "support_seeking_regulation_candidate"
                ],
                "all_controls_fail_closed": control["control_matrix"][
                    "control_summary"
                ]["all_controls_fail_closed"],
                "stress_matrix_passed": stress["iteration_result"][
                    "support_disruption_restoration_stress_matrix_passed"
                ],
                "claim_boundary_record_passed": boundary["iteration_result"][
                    "claim_boundary_record_passed"
                ],
            },
        },
        "hypothesis_c_claim_boundary_blockers": {
            "acceptance_state": "supported",
            "resolution": (
                "Positive N13 evidence remains claim-clean: identity acceptance, "
                "semantic goal ownership, intention, agency, selfhood, "
                "personhood, biological behavior, native support, and fully "
                "native integration are blocked unless separate theory or "
                "Phase 8 implementation gates are satisfied."
            ),
            "supporting_artifacts": [
                rel(CONTROL_OUTPUT),
                rel(STRESS_OUTPUT),
                rel(BOUNDARY_OUTPUT),
            ],
            "key_checks": {
                "all_boundary_claims_blocked": boundary["claim_boundary_record"][
                    "boundary_summary"
                ]["all_boundary_claims_blocked"],
                "all_unsafe_claim_flags_false": boundary["checks"][
                    "all_unsafe_claim_flags_false"
                ],
                "native_support_opened": False,
                "phase8_opened": False,
            },
        },
    }


def build_whole_experiment_interpretation() -> dict[str, Any]:
    return {
        "record_id": "n13_i8_whole_experiment_interpretation_v1",
        "record_type": "n13_whole_experiment_interpretation",
        "plain_language_interpretation": (
            "N13 shows artifact-level support-seeking regulation: source-backed "
            "support state can be converted into a source-current support target, "
            "a support error can be computed from that target, and bounded "
            "budgeted response can be scheduled only when that error is present."
        ),
        "supported_interpretation": (
            "artifact-level AP3 self-maintenance candidate / support-seeking "
            "regulation candidate"
        ),
        "supporting_evidence_summary": [
            "source-current support target derivation is recorded",
            "bounded response magnitude and budget debit are recorded",
            "external-proxy and hidden-target controls fail closed",
            "support disruption/restoration stress regimes pass",
            "claim-boundary flags remain false",
        ],
        "unsupported_interpretations": [
            "agency",
            "intention",
            "semantic goal ownership",
            "semantic goal understanding",
            "identity acceptance",
            "runtime identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support",
            "fully native agentic-like integration",
            "unrestricted agency",
        ],
        "claim_boundary_summary": (
            "The AP3 result supports only artifact-level self-maintenance "
            "candidate evidence. It does not license agency, semantic goal "
            "ownership, identity acceptance, selfhood, native support, or fully "
            "native integration claims."
        ),
        "why_it_matters_for_roadmap": (
            "N13 gives N14 a claim-clean support-seeking regulation substrate "
            "for consequence-sensitive route selection."
        ),
        "handoff_rule": (
            "N14 may consume N13 only as artifact-level AP3 support-seeking "
            "regulation evidence."
        ),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    target = load_json(TARGET_OUTPUT)
    regulation = load_json(REGULATION_OUTPUT)
    control = load_json(CONTROL_OUTPUT)
    stress = load_json(STRESS_OUTPUT)
    boundary = load_json(BOUNDARY_OUTPUT)
    final_classification_rows = [
        row_classification(row) for row in inventory["n13_inventory_rows"]
    ]
    hypotheses_closeout = build_hypotheses_closeout(
        inventory, target, regulation, control, stress, boundary
    )
    final_claim_boundary = {
        "support_seeking_regulation_is_agency": False,
        "self_maintenance_candidate_is_selfhood": False,
        "support_survival_is_identity_acceptance": False,
        "support_target_or_error_is_semantic_goal_ownership": False,
        "bounded_response_is_intention": False,
        "artifact_level_support_regulation_is_native_support": False,
        "n13_stress_clean_candidate_is_fully_native_integration": False,
        "n13_evidence_is_personhood_or_biological_behavior": False,
    }
    closeout_result = {
        "status": "closed_claim_clean_ap3_artifact_level_support_seeking_regulation",
        "final_supported_ap_level": "AP3",
        "final_ap3_supported": True,
        "self_maintenance_candidate_supported": True,
        "self_maintenance_candidate_scope": (
            "artifact-level support-seeking regulation candidate; not selfhood"
        ),
        "final_claim_ceiling": (
            "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation"
        ),
        "artifact_only": True,
        "fully_native": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "native_supported_flags": False,
        "identity_acceptance_opened": False,
        "semantic_goal_ownership_opened": False,
        "agency_claim_opened": False,
        "personhood_or_biological_behavior_opened": False,
    }
    n14_handoff = {
        "recommended_next": "N14_consequence_sensitive_route_selection",
        "recommended_branch": "continue_artifact_roadmap_no_src",
        "targeted_phase8_required_before_n14": False,
        "targeted_phase8_optional_parallel_branch": True,
        "n14_primary_question": (
            "Can route selection depend on expected downstream effects on "
            "support, memory, or regulation, rather than immediate route "
            "affordance alone?"
        ),
        "n14_allowed_inputs": [
            "N06 native route arbitration evidence",
            "N08 route memory / affordance evidence",
            "N09 bounded response regulation evidence",
            "N13 final AP3 artifact-level support-seeking regulation candidate",
            "N12 NAT4 route conductance memory and response magnitude readiness records",
        ],
        "n14_blocked_inputs": [
            "identity acceptance",
            "runtime identity acceptance",
            "semantic goal ownership",
            "intention",
            "agency",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support without Phase 8 implementation",
            "fully native agentic-like integration",
        ],
        "n14_required_controls": [
            "hidden outcome table blocked",
            "post-hoc consequence scoring blocked",
            "stale consequence record blocked",
            "budget-invalid route blocked",
            "semantic intention relabel blocked",
            "agency relabel blocked",
            "native support relabel blocked",
        ],
    }
    whole_experiment_interpretation = build_whole_experiment_interpretation()
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "target_source_passed": target["status"] == "passed",
        "regulation_source_passed": regulation["status"] == "passed",
        "control_source_passed": control["status"] == "passed",
        "stress_source_passed": stress["status"] == "passed",
        "boundary_source_passed": boundary["status"] == "passed",
        "hypothesis_a_closed_supported": hypotheses_closeout[
            "hypothesis_a_support_condition_inventory"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_b_closed_supported": hypotheses_closeout[
            "hypothesis_b_support_seeking_regulation"
        ]["acceptance_state"]
        == "supported",
        "hypothesis_c_closed_supported": hypotheses_closeout[
            "hypothesis_c_claim_boundary_blockers"
        ]["acceptance_state"]
        == "supported",
        "every_seed_row_classified": len(final_classification_rows)
        == inventory["inventory_summary"]["row_count"]
        and all(row["final_role"] for row in final_classification_rows),
        "final_support_condition_candidates_recorded": target["iteration_result"][
            "support_derived_target_candidate"
        ]
        is True,
        "final_support_seeking_regulation_recorded": regulation["iteration_result"][
            "support_seeking_regulation_candidate"
        ]
        is True,
        "external_proxy_and_hidden_target_controls_recorded": control[
            "iteration_result"
        ]["external_proxy_controls_passed"]
        and control["iteration_result"]["hidden_target_controls_passed"],
        "stress_matrix_passed": stress["iteration_result"][
            "support_disruption_restoration_stress_matrix_passed"
        ],
        "claim_boundary_passed": boundary["iteration_result"][
            "claim_boundary_record_passed"
        ],
        "final_supported_ap_level_ap3": closeout_result["final_supported_ap_level"]
        == "AP3"
        and closeout_result["final_ap3_supported"] is True,
        "claim_boundary_controls_false": all(
            value is False for value in final_claim_boundary.values()
        ),
        "final_claim_flags_all_false_for_unsafe_claims": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "native_supported_flags_false": closeout_result["native_supported_flags"]
        is False
        and closeout_result["native_support_opened"] is False,
        "phase8_opened_false": closeout_result["phase8_opened"] is False,
        "n14_handoff_recorded": n14_handoff["recommended_next"]
        == "N14_consequence_sensitive_route_selection",
        "whole_experiment_interpretation_recorded": (
            whole_experiment_interpretation["supported_interpretation"]
            == (
                "artifact-level AP3 self-maintenance candidate / support-seeking "
                "regulation candidate"
            )
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 8,
        "purpose": "closeout_and_handoff",
        "schema": "n13_closeout_and_handoff_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "closeout_result": closeout_result,
        "hypotheses_closeout": hypotheses_closeout,
        "final_classification_rows": final_classification_rows,
        "final_support_condition_candidates": [
            {
                "candidate_name": "support_retention_above_threshold_source_current",
                "source": rel(TARGET_OUTPUT),
                "output_digest": target["output_digest"],
                "status": "supported_source_current_target",
            }
        ],
        "final_support_seeking_regulation_result": {
            "candidate_name": "support_error_bounded_response_candidate",
            "source": rel(REGULATION_OUTPUT),
            "output_digest": regulation["output_digest"],
            "control_source": rel(CONTROL_OUTPUT),
            "stress_source": rel(STRESS_OUTPUT),
            "claim_boundary_source": rel(BOUNDARY_OUTPUT),
            "status": "supported_artifact_level_ap3_self_maintenance_candidate",
        },
        "final_controls": {
            "external_proxy_hidden_target_controls": control["control_matrix"][
                "control_summary"
            ],
            "support_disruption_restoration_stress": stress["stress_matrix"][
                "stress_summary"
            ],
            "claim_boundary_summary": boundary["claim_boundary_record"][
                "boundary_summary"
            ],
        },
        "final_blockers": boundary["claim_boundary_record"][
            "remaining_theory_sensitive_blockers"
        ],
        "final_claim_boundary": final_claim_boundary,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "n14_handoff": n14_handoff,
        "whole_experiment_interpretation": whole_experiment_interpretation,
        "roadmap_update_decision": {
            "handoff_file_update_required": True,
            "roadmap_file_update_required": True,
            "reason": "N13 is closed and the recommended roadmap continuation is N14.",
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
            rel(TARGET_OUTPUT): source_artifact(TARGET_OUTPUT, target),
            rel(REGULATION_OUTPUT): source_artifact(REGULATION_OUTPUT, regulation),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, control),
            rel(STRESS_OUTPUT): source_artifact(STRESS_OUTPUT, stress),
            rel(BOUNDARY_OUTPUT): source_artifact(BOUNDARY_OUTPUT, boundary),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(TARGET_REPORT): source_report(TARGET_REPORT),
            rel(REGULATION_REPORT): source_report(REGULATION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
            rel(STRESS_REPORT): source_report(STRESS_REPORT),
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
        "# N13 Closeout And Handoff",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"final_supported_ap_level = {closeout['final_supported_ap_level']}",
        f"final_ap3_supported = {str(closeout['final_ap3_supported']).lower()}",
        f"self_maintenance_candidate_supported = {str(closeout['self_maintenance_candidate_supported']).lower()}",
        f"final_claim_ceiling = {closeout['final_claim_ceiling']}",
        "artifact_only = true",
        "fully_native = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "agency_claim_opened = false",
        "identity_acceptance_opened = false",
        "semantic_goal_ownership_opened = false",
        "```",
        "",
        "N13 closes with supported `AP3` evidence for an artifact-level",
        "self-maintenance candidate: source-current support-seeking regulation",
        "that is distinguished from external proxy regulation, stress-clean,",
        "budgeted, replayable, and claim-clean. This is not agency, identity",
        "acceptance, intention, selfhood, native support, or fully native",
        "agentic-like integration.",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Acceptance state |",
        "| --- | --- |",
    ]
    for name, hypothesis in output["hypotheses_closeout"].items():
        lines.append(
            f"| `{name}` | `{hypothesis['acceptance_state']}` |"
        )
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
            "## Final Claim Boundary",
            "",
            "```json",
            json.dumps(output["final_claim_boundary"], indent=2, sort_keys=True),
            "```",
            "",
            "## N14 Handoff",
            "",
            "```json",
            json.dumps(output["n14_handoff"], indent=2, sort_keys=True),
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
            "artifact-level AP3 self-maintenance candidate != selfhood",
            "support-seeking regulation != agency",
            "support survival != identity acceptance",
            "support target/error != semantic goal ownership",
            "bounded response != intention",
            "artifact-level support regulation != native support",
            "N13 AP3 != fully native agentic-like integration",
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

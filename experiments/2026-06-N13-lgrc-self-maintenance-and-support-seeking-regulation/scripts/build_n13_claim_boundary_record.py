#!/usr/bin/env python3
"""Build N13 Iteration 7 identity, goal-ownership, and agency boundary record."""

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

N12_CLOSEOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "outputs"
    / "n12_closeout_and_handoff.json"
)
N12_CLOSEOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "reports"
    / "n12_closeout_and_handoff.md"
)

OUTPUT_PATH = OUTPUTS / "n13_claim_boundary_record.json"
REPORT_PATH = REPORTS / "n13_claim_boundary_record.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_claim_boundary_record.py"
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


def boundary_row(
    *,
    row_id: str,
    blocked_claim: str,
    positive_evidence: list[str],
    boundary_reason: str,
    required_future_gate: list[str],
    control_sources: list[str],
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "blocked_claim": blocked_claim,
        "boundary_status": "blocked",
        "claim_allowed": False,
        "positive_evidence_retained": positive_evidence,
        "boundary_reason": boundary_reason,
        "required_future_gate": required_future_gate,
        "control_sources": control_sources,
    }


def build_boundary_rows(
    control: dict[str, Any],
    stress: dict[str, Any],
    n12_closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        boundary_row(
            row_id="n13_i7_boundary_01_support_survival_not_identity_acceptance",
            blocked_claim="identity_acceptance",
            positive_evidence=[
                "N07 support survival/disruption/restoration lanes",
                "N13 source-current support target",
                "N13 stress-clean support-seeking regulation candidate",
            ],
            boundary_reason=(
                "Support survival and restoration are source-current support "
                "state observations; they do not define a runtime acceptance "
                "event or identity acceptance validator."
            ),
            required_future_gate=[
                "formal_identity_acceptance_semantics",
                "runtime_acceptance_event_schema",
                "native_identity_acceptance_validator",
            ],
            control_sources=[
                control["interpretation_record"]["record_id"],
                stress["interpretation_record"]["record_id"],
                "n12_native_identity_acceptance_validator_nat2_blocker",
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_02_support_target_not_semantic_goal_ownership",
            blocked_claim="semantic_goal_ownership",
            positive_evidence=[
                "support_retention_above_threshold_source_current target",
                "support_retention_threshold_deficit error signal",
            ],
            boundary_reason=(
                "The support target is a threshold condition over recorded "
                "support state, not a semantic goal owned or understood by an "
                "agent."
            ),
            required_future_gate=[
                "formal_semantic_goal_ownership_semantics",
                "runtime_goal_ownership_event_schema",
                "negative_controls_for_goal_ownership_relabeling",
            ],
            control_sources=[
                "semantic_goal_ownership_relabel_control",
                control["interpretation_record"]["record_id"],
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_03_bounded_response_not_intention",
            blocked_claim="intention",
            positive_evidence=[
                "bounded response magnitude surface",
                "budgeted response packet schedule for support deficit",
            ],
            boundary_reason=(
                "Bounded response is serialized packet scheduling against a "
                "source-current error; it is not intention, choice semantics, "
                "or goal ownership."
            ),
            required_future_gate=[
                "formal_intention_semantics",
                "choice_or_intention_event_schema",
                "negative_controls_for_intention_relabeling",
            ],
            control_sources=[
                "agency_relabel_control",
                stress["interpretation_record"]["record_id"],
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_04_self_maintenance_candidate_not_selfhood",
            blocked_claim="selfhood",
            positive_evidence=[
                "artifact-level AP3 stress-clean support-seeking regulation candidate",
                "support-disruption/restoration stress matrix passed",
            ],
            boundary_reason=(
                "A self-maintenance candidate is an agency-prerequisite support "
                "regulation pattern; it does not establish selfhood, self-model, "
                "personhood, or biological behavior."
            ),
            required_future_gate=[
                "selfhood_theory_not_in_n13_scope",
                "personhood_and_biological_behavior_out_of_scope",
            ],
            control_sources=[stress["interpretation_record"]["record_id"]],
        ),
        boundary_row(
            row_id="n13_i7_boundary_05_n13_not_agency",
            blocked_claim="agency",
            positive_evidence=[
                "control-clean support-seeking regulation candidate",
                "stress-clean source-current support response",
            ],
            boundary_reason=(
                "N13 is an agency-prerequisite experiment. It does not include "
                "consequence-sensitive route selection, endogenous proxy "
                "formation, self/environment boundary, closed action-perception "
                "loop, long-horizon closure, or agency semantics."
            ),
            required_future_gate=[
                "N14_consequence_sensitive_route_selection",
                "N15_endogenous_proxy_formation",
                "N16_self_environment_boundary",
                "N17_closed_action_perception_loop",
                "N18_long_horizon_agentic_like_closure",
            ],
            control_sources=[
                "agency_relabel_control",
                control["interpretation_record"]["record_id"],
                stress["interpretation_record"]["record_id"],
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_06_artifact_candidate_not_native_support",
            blocked_claim="native_support_without_phase8",
            positive_evidence=[
                "N12 NAT4 response magnitude readiness input",
                "artifact-level bounded support response schedule",
            ],
            boundary_reason=(
                "N13 consumes N12 readiness records and artifact-level "
                "response scheduling. It does not implement Phase 8 and does "
                "not add native support in src/."
            ),
            required_future_gate=[
                "Phase_8_native_implementation_explicitly_opened",
                "native_response_magnitude_policy_implemented_and_validated",
                "telemetry_under_src_pygrc_telemetry_when_phase8_opens",
            ],
            control_sources=[
                "native_support_without_phase8_control",
                "n12_phase8_ready_but_not_implemented_boundary",
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_07_not_fully_native_integration",
            blocked_claim="fully_native_agentic_like_integration",
            positive_evidence=[
                "N11 artifact-only GALI7 handoff",
                "N12 native agentic-like integration policy remains NAT2",
                "N13 artifact-level support-seeking regulation candidate",
            ],
            boundary_reason=(
                "Fully native agentic-like integration requires a native "
                "integration meta-policy and component native policy records. "
                "N13 remains artifact-level."
            ),
            required_future_gate=[
                "native_route_conductance_memory_policy_implemented",
                "native_response_magnitude_policy_implemented",
                "native_agentic_like_integration_meta_policy_formalized",
                "component_native_policy_composition_replay",
            ],
            control_sources=[
                "n12_native_agentic_like_integration_policy_nat2_blocker",
                (
                    "n12_final_nat_level_native_agentic_like_integration_policy="
                    + n12_closeout["final_nat_levels"][
                        "native_agentic_like_integration_policy"
                    ]
                ),
            ],
        ),
        boundary_row(
            row_id="n13_i7_boundary_08_not_personhood_or_biological_behavior",
            blocked_claim="personhood_or_biological_behavior",
            positive_evidence=[
                "artifact-level support-seeking regulation candidate",
            ],
            boundary_reason=(
                "No N13 artifact concerns personhood, subjective status, or "
                "biological behavior. Those claims are outside the experiment."
            ),
            required_future_gate=[
                "not_part_of_lgrc_experiment_scope",
            ],
            control_sources=[stress["interpretation_record"]["record_id"]],
        ),
    ]


def build_interpretation_record(
    boundary_rows: list[dict[str, Any]],
    stress: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": "n13_i7_interpretation_claim_boundary_v1",
        "record_type": "n13_iteration_7_claim_boundary_interpretation",
        "plain_language_meaning": (
            "Iteration 7 makes the N13 stress-clean AP3 candidate claim-clean: "
            "the positive result may be interpreted as artifact-level "
            "support-seeking regulation, but not as identity acceptance, "
            "semantic goal ownership, intention, agency, selfhood, native "
            "support, or fully native integration."
        ),
        "supported_interpretation": (
            "Artifact-level AP3 boundary-clean support-seeking regulation "
            "candidate, pending Iteration 8 closeout and supported AP freeze."
        ),
        "unsupported_interpretations": [
            row["blocked_claim"] for row in boundary_rows
        ],
        "ap_state_after_claim_boundary": {
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_boundary_clean_pending_closeout",
            "claim_boundary_record_passed": True,
            "stress_matrix_passed": stress["iteration_result"][
                "support_disruption_restoration_stress_matrix_passed"
            ],
            "final_ap3_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "remaining_required_work": [
            "n13_closeout_handoff_iteration_8",
        ],
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    target = load_json(TARGET_OUTPUT)
    regulation = load_json(REGULATION_OUTPUT)
    control = load_json(CONTROL_OUTPUT)
    stress = load_json(STRESS_OUTPUT)
    n12_closeout = load_json(N12_CLOSEOUT_OUTPUT)
    boundary_rows = build_boundary_rows(control, stress, n12_closeout)
    interpretation_record = build_interpretation_record(boundary_rows, stress)
    claim_boundary_record = {
        "record_name": "n13_identity_goal_ownership_agency_boundary_record",
        "candidate_source": rel(STRESS_OUTPUT),
        "candidate_output_digest": stress["output_digest"],
        "boundary_rows": boundary_rows,
        "boundary_summary": {
            "boundary_row_count": len(boundary_rows),
            "all_boundary_claims_blocked": all(
                row["claim_allowed"] is False for row in boundary_rows
            ),
            "identity_acceptance_blocked": True,
            "semantic_goal_ownership_blocked": True,
            "intention_blocked": True,
            "agency_blocked": True,
            "selfhood_blocked": True,
            "native_support_without_phase8_blocked": True,
            "fully_native_integration_blocked": True,
            "personhood_and_biological_behavior_blocked": True,
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "ap_state_after_claim_boundary": interpretation_record[
            "ap_state_after_claim_boundary"
        ],
        "remaining_theory_sensitive_blockers": [
            "formal_identity_acceptance_semantics_missing",
            "semantic_goal_ownership_semantics_missing",
            "intention_semantics_missing",
            "agency_semantics_not_part_of_n13",
            "selfhood_personhood_biological_behavior_out_of_scope",
            "native_support_requires_explicit_phase8_implementation",
            "fully_native_agentic_like_integration_requires_native_meta_policy",
        ],
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "target_source_passed": target["status"] == "passed",
        "regulation_source_passed": regulation["status"] == "passed",
        "control_source_passed": control["status"] == "passed",
        "stress_source_passed": stress["status"] == "passed",
        "n12_closeout_source_passed": n12_closeout["status"] == "passed",
        "support_survival_not_identity_acceptance_recorded": any(
            row["blocked_claim"] == "identity_acceptance" for row in boundary_rows
        ),
        "support_target_not_semantic_goal_ownership_recorded": any(
            row["blocked_claim"] == "semantic_goal_ownership" for row in boundary_rows
        ),
        "bounded_response_not_intention_recorded": any(
            row["blocked_claim"] == "intention" for row in boundary_rows
        ),
        "self_maintenance_candidate_not_selfhood_recorded": any(
            row["blocked_claim"] == "selfhood" for row in boundary_rows
        ),
        "n13_not_agency_recorded": any(
            row["blocked_claim"] == "agency" for row in boundary_rows
        ),
        "native_support_without_phase8_blocked": any(
            row["blocked_claim"] == "native_support_without_phase8"
            for row in boundary_rows
        ),
        "fully_native_integration_blocked": any(
            row["blocked_claim"] == "fully_native_agentic_like_integration"
            for row in boundary_rows
        ),
        "all_boundary_claims_blocked": claim_boundary_record["boundary_summary"][
            "all_boundary_claims_blocked"
        ],
        "all_unsafe_claim_flags_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "interpretation_record_present": interpretation_record["record_type"]
        == "n13_iteration_7_claim_boundary_interpretation",
        "stress_clean_candidate_carried_forward": stress["iteration_result"][
            "support_seeking_regulation_survives_controls"
        ]
        is True,
        "final_ap3_not_frozen_until_iteration8": interpretation_record[
            "ap_state_after_claim_boundary"
        ]["final_ap3_supported"]
        is False
        and interpretation_record["ap_state_after_claim_boundary"][
            "final_ap_freeze_pending_iteration8"
        ]
        is True,
        "self_maintenance_not_supported_yet": interpretation_record[
            "ap_state_after_claim_boundary"
        ]["self_maintenance_candidate_supported"]
        is False,
        "native_support_not_opened": interpretation_record[
            "ap_state_after_claim_boundary"
        ]["native_support_opened"]
        is False,
        "phase8_not_opened": interpretation_record["ap_state_after_claim_boundary"][
            "phase8_opened"
        ]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 7,
        "purpose": "claim_boundary_record",
        "schema": "n13_claim_boundary_record_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_result": {
            "claim_boundary_record_passed": True,
            "candidate_ap_level": "AP3",
            "provisional_ap_level": "AP3_candidate_boundary_clean_pending_closeout",
            "final_ap3_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "self_maintenance_candidate_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "claim_boundary_record": claim_boundary_record,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(TARGET_OUTPUT): source_artifact(TARGET_OUTPUT, target),
            rel(REGULATION_OUTPUT): source_artifact(REGULATION_OUTPUT, regulation),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, control),
            rel(STRESS_OUTPUT): source_artifact(STRESS_OUTPUT, stress),
            rel(N12_CLOSEOUT_OUTPUT): source_artifact(N12_CLOSEOUT_OUTPUT, n12_closeout),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(TARGET_REPORT): source_report(TARGET_REPORT),
            rel(REGULATION_REPORT): source_report(REGULATION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
            rel(STRESS_REPORT): source_report(STRESS_REPORT),
            rel(N12_CLOSEOUT_REPORT): source_report(N12_CLOSEOUT_REPORT),
        },
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    record = output["claim_boundary_record"]
    interpretation = output["interpretation_record"]
    result = output["iteration_result"]
    lines = [
        "# N13 Claim Boundary Record",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"claim_boundary_record_passed = {str(result['claim_boundary_record_passed']).lower()}",
        f"candidate_ap_level = {result['candidate_ap_level']}",
        f"provisional_ap_level = {result['provisional_ap_level']}",
        "final_ap3_supported = false",
        "final_ap_freeze_pending_iteration8 = true",
        "self_maintenance_candidate_supported = false",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 7 records why the N13 stress-clean AP3 candidate remains",
        "claim-bounded. The positive result is an artifact-level",
        "support-seeking regulation candidate, not identity acceptance,",
        "semantic goal ownership, intention, agency, selfhood, personhood,",
        "biological behavior, native support, or fully native integration.",
        "",
        "## Boundary Summary",
        "",
        "```json",
        json.dumps(record["boundary_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary Rows",
        "",
        "| Row | Blocked claim | Claim allowed |",
        "| --- | --- | --- |",
    ]
    for row in record["boundary_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['blocked_claim']}` | "
            f"`{str(row['claim_allowed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Record",
            "",
            "```json",
            json.dumps(interpretation, indent=2, sort_keys=True),
            "```",
            "",
            "## Remaining Blockers",
            "",
            "```json",
            json.dumps(
                record["remaining_theory_sensitive_blockers"],
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
            "support-seeking regulation candidate != agency",
            "support survival != identity acceptance",
            "support target/error != semantic goal ownership",
            "bounded response != intention",
            "self-maintenance candidate != selfhood",
            "artifact-level candidate != native support",
            "N13 stress-clean candidate != fully native integration",
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

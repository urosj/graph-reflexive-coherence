#!/usr/bin/env python3
"""Run N10 Iteration 12 Hypothesis B support-state matrix closeout.

Iteration 12 closes Hypothesis B by validating the full-composition support
matrix:

* support intact and mild withdrawal may preserve the bounded composition;
* disrupted support must block the full A6/ALI6 composition;
* explicit restoration may resume it without erasing the disruption history.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_12_hypothesis_b_support_state_matrix_closeout.py"
)

ARTIFACT_PATHS = {
    "n10_iteration_8_bounded_repeated_integration": (
        EXPERIMENT / "outputs" / "n10_iteration_8_bounded_repeated_integration.json"
    ),
    "n10_iteration_9_hypothesis_a_closeout": (
        EXPERIMENT / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
    ),
    "n10_iteration_10_disrupted_support_control": (
        EXPERIMENT / "outputs" / "n10_iteration_10_full_composition_disrupted_support_control.json"
    ),
    "n10_iteration_11_explicit_restoration_replay": (
        EXPERIMENT / "outputs" / "n10_iteration_11_full_composition_explicit_restoration_replay.json"
    ),
}
REPORT_PATHS = {
    "n10_iteration_8_bounded_repeated_integration": (
        EXPERIMENT / "reports" / "n10_iteration_8_bounded_repeated_integration.md"
    ),
    "n10_iteration_9_hypothesis_a_closeout": (
        EXPERIMENT / "reports" / "n10_iteration_9_artifact_only_closeout.md"
    ),
    "n10_iteration_10_disrupted_support_control": (
        EXPERIMENT / "reports" / "n10_iteration_10_full_composition_disrupted_support_control.md"
    ),
    "n10_iteration_11_explicit_restoration_replay": (
        EXPERIMENT / "reports" / "n10_iteration_11_full_composition_explicit_restoration_replay.md"
    ),
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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def row_digest_valid(row: dict[str, Any], digest_field: str = "integration_row_digest") -> bool:
    return row[digest_field] == digest_value(
        {key: value for key, value in row.items() if key != digest_field}
    )


def all_claim_flags_false(row: dict[str, Any]) -> bool:
    return all(value is False for value in row["claim_flags"].values())


def prior_output_digest_valid(artifact: dict[str, Any]) -> bool:
    if "output_digest" not in artifact:
        return True
    return artifact["output_digest"] == output_digest(artifact)


def build_artifact_records(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
            "status": artifacts[key].get("status"),
            "output_digest": artifacts[key].get("output_digest"),
            "output_digest_valid": prior_output_digest_valid(artifacts[key]),
        }
        for key, path in ARTIFACT_PATHS.items()
    }
    report_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in REPORT_PATHS.items()
        if path.exists()
    }
    return artifact_records, report_records


def build_matrix_rows(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    i8 = artifacts["n10_iteration_8_bounded_repeated_integration"]
    i10 = artifacts["n10_iteration_10_disrupted_support_control"]
    i11 = artifacts["n10_iteration_11_explicit_restoration_replay"]
    intact = i8["main_integration_row"]
    mild = i8["mild_withdrawal_companion_row"]
    disrupted = i10["blocked_full_composition_record"]
    restored = i11["restored_full_composition_row"]

    rows = [
        {
            "matrix_state": "support_intact_survives",
            "expected_outcome": "composition_preserved",
            "source_iteration": 8,
            "source_row_digest": intact["integration_row_digest"],
            "support_state_tag": intact["support_state_tag"],
            "integration_allowed": intact["integration_allowed"],
            "accepted_integration_level": intact["accepted_integration_level"],
            "accepted_n10_category_level": intact["n10_category_level"],
            "integration_outcome_tag": intact["integration_outcome_tag"],
            "artifact_only": intact["artifact_only"],
            "runtime_state_used": intact["runtime_state_used"],
            "row_digest_valid": row_digest_valid(intact),
            "claim_flags_false": all_claim_flags_false(intact),
            "budget_error_zero": intact["node_plus_packet_budget_error"] == 0.0
            and intact["bounded_window"]["all_cycle_budgets_exact"] is True,
            "outcome_matches_expectation": intact["integration_allowed"] is True
            and intact["support_state_tag"] == "support_intact_survives",
        },
        {
            "matrix_state": "mild_withdrawal_survives",
            "expected_outcome": "composition_preserved_under_bounded_companion_scope",
            "source_iteration": 8,
            "source_row_digest": mild["integration_row_digest"],
            "support_state_tag": mild["support_state_tag"],
            "integration_allowed": mild["integration_allowed"],
            "accepted_integration_level": mild["accepted_integration_level"],
            "accepted_n10_category_level": mild["n10_category_level"],
            "integration_outcome_tag": mild["integration_outcome_tag"],
            "artifact_only": mild["artifact_only"],
            "runtime_state_used": mild["runtime_state_used"],
            "row_digest_valid": row_digest_valid(mild),
            "claim_flags_false": all_claim_flags_false(mild),
            "budget_error_zero": mild["node_plus_packet_budget_error"] == 0.0
            and mild["bounded_window"]["all_cycle_budgets_exact"] is True,
            "outcome_matches_expectation": mild["integration_allowed"] is True
            and mild["support_state_tag"] == "mild_withdrawal_survives",
        },
        {
            "matrix_state": "n09_matched_withdrawal_disrupts_support",
            "expected_outcome": "composition_blocked_or_downgraded",
            "source_iteration": 10,
            "source_row_digest": disrupted["integration_row_digest"],
            "support_state_tag": disrupted["support_state_tag"],
            "integration_allowed": disrupted["integration_allowed"],
            "attempted_integration_level": disrupted["attempted_integration_level"],
            "accepted_integration_level": disrupted["accepted_integration_level"],
            "attempted_n10_category_level": disrupted["attempted_n10_category_level"],
            "accepted_n10_category_level": disrupted["accepted_n10_category_level"],
            "primary_blocker": disrupted["primary_blocker"],
            "artifact_only": disrupted["artifact_only"],
            "runtime_state_used": disrupted["runtime_state_used"],
            "row_digest_valid": row_digest_valid(disrupted),
            "claim_flags_false": all_claim_flags_false(disrupted),
            "budget_error_zero": disrupted["node_plus_packet_budget_error"] == 0.0
            and disrupted["support_evidence"]["final_budget_error"] == 0.0,
            "outcome_matches_expectation": disrupted["integration_allowed"] is False
            and disrupted["accepted_integration_level"] is None
            and disrupted["primary_blocker"] == "support_disrupted_but_integration_allowed"
            and disrupted["support_state_tag"] == "n09_matched_withdrawal_disrupts_support",
        },
        {
            "matrix_state": "explicit_restoration_recovers_support",
            "expected_outcome": "composition_restoration_gated_resume",
            "source_iteration": 11,
            "source_row_digest": restored["integration_row_digest"],
            "support_state_tag": restored["support_state_tag"],
            "integration_allowed": restored["integration_allowed"],
            "accepted_integration_level": restored["accepted_integration_level"],
            "accepted_n10_category_level": restored["accepted_n10_category_level"],
            "integration_outcome_tag": restored["integration_outcome_tag"],
            "artifact_only": restored["artifact_only"],
            "runtime_state_used": restored["runtime_state_used"],
            "row_digest_valid": row_digest_valid(restored),
            "claim_flags_false": all_claim_flags_false(restored),
            "budget_error_zero": restored["node_plus_packet_budget_error"] == 0.0
            and restored["support_evidence"]["final_budget_error"] == 0.0,
            "prior_disruption_history_preserved": restored["prior_disruption_evidence"][
                "history_preserved"
            ],
            "outcome_matches_expectation": restored["integration_allowed"] is True
            and restored["support_state_tag"] == "explicit_restoration_recovers_support"
            and restored["integration_outcome_tag"] == "restoration_gated_integration_candidate"
            and restored["prior_disruption_evidence"]["history_preserved"] is True,
        },
    ]
    return [with_digest(row, "matrix_row_digest") for row in rows]


def build_closeout_record(
    artifacts: dict[str, dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    i9 = artifacts["n10_iteration_9_hypothesis_a_closeout"]
    i10 = artifacts["n10_iteration_10_disrupted_support_control"]
    i11 = artifacts["n10_iteration_11_explicit_restoration_replay"]
    claim_flags = dict(i9["closeout"]["claim_flags"])
    matrix_passed = all(
        row["outcome_matches_expectation"]
        and row["artifact_only"]
        and not row["runtime_state_used"]
        and row["row_digest_valid"]
        and row["claim_flags_false"]
        and row["budget_error_zero"]
        for row in matrix_rows
    )
    record = {
        "hypothesis_b_closeout_row_id": "n10_i12_hypothesis_b_support_state_matrix_closeout_v1",
        "hypothesis_b_status": "supported_bounded_support_sensitive_full_composition"
        if matrix_passed
        else "blocked_support_state_matrix_validation_failed",
        "hypothesis_b_supported": matrix_passed,
        "matrix_states": [row["matrix_state"] for row in matrix_rows],
        "matrix_row_digests": [row["matrix_row_digest"] for row in matrix_rows],
        "support_sensitive_rule": (
            "intact, mild-withdrawal, and explicit-restoration support states "
            "may preserve or resume bounded composition; disrupted support "
            "must block or downgrade the full composition unless explicit "
            "restoration is present"
        ),
        "positive_scope": "bounded_artifact_only_support_sensitive_full_composition",
        "artifact_only": True,
        "runtime_state_used": False,
        "hypothesis_a_ceiling_preserved": i9["closeout"]["final_n10_ceiling"],
        "disrupted_support_blocker": i10["blocked_full_composition_record"][
            "primary_blocker"
        ],
        "restoration_gated_row_digest": i11["restored_full_composition_row"][
            "integration_row_digest"
        ],
        "restoration_preserves_disruption_history": i11["restored_full_composition_row"][
            "prior_disruption_evidence"
        ]["history_preserved"],
        "claim_flags": claim_flags,
        "blocked_claims": i9["closeout"]["blocked_claims"],
        "non_claims": [
            "agency",
            "intention",
            "semantic_goal_ownership",
            "identity_acceptance",
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "ant_colony_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "personhood",
            "unrestricted_agency",
            "A7_generalization",
            "fully_native_agentic_like_integration",
        ],
        "next_hypothesis": "C_native_policy_gap",
    }
    return with_digest(record, "hypothesis_b_closeout_digest")


def build_controls(
    matrix_rows: list[dict[str, Any]],
    closeout: dict[str, Any],
) -> dict[str, Any]:
    by_state = {row["matrix_state"]: row for row in matrix_rows}
    return {
        "support_intact_positive": {
            "control_passed": by_state["support_intact_survives"][
                "outcome_matches_expectation"
            ],
            "primary_blocker": "support_intact_full_composition_missing",
            "reason": "support-intact full composition remains available from Iteration 8",
        },
        "mild_withdrawal_positive": {
            "control_passed": by_state["mild_withdrawal_survives"][
                "outcome_matches_expectation"
            ],
            "primary_blocker": "mild_withdrawal_full_composition_missing",
            "reason": "mild-withdrawal companion remains valid under bounded scope",
        },
        "disrupted_support_blocks": {
            "control_passed": by_state["n09_matched_withdrawal_disrupts_support"][
                "outcome_matches_expectation"
            ],
            "primary_blocker": "support_disrupted_but_integration_allowed",
            "reason": "disrupted support blocks the attempted A6/ALI6 full composition",
        },
        "explicit_restoration_resumes": {
            "control_passed": by_state["explicit_restoration_recovers_support"][
                "outcome_matches_expectation"
            ],
            "primary_blocker": "restoration_required_but_missing",
            "reason": "explicit restoration resumes the full composition and preserves disruption history",
        },
        "artifact_only_replay": {
            "control_passed": all(row["artifact_only"] and not row["runtime_state_used"] for row in matrix_rows)
            and closeout["artifact_only"]
            and not closeout["runtime_state_used"],
            "primary_blocker": "artifact_only_replay_missing_link",
            "reason": "support-state matrix is reconstructed from exported artifacts only",
        },
        "budget_surfaces": {
            "control_passed": all(row["budget_error_zero"] for row in matrix_rows),
            "primary_blocker": "budget_surface_ambiguity",
            "reason": "source-artifact budget compatibility remains exact in every matrix state",
        },
        "claim_promotion": {
            "control_passed": all(row["claim_flags_false"] for row in matrix_rows)
            and all(value is False for value in closeout["claim_flags"].values()),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "Hypothesis B closeout does not emit agency, identity acceptance, A7, or fully native claims",
        },
    }


def build_checks(
    artifacts: dict[str, dict[str, Any]],
    artifact_records: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
    closeout: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    by_state = {row["matrix_state"]: row for row in matrix_rows}
    return {
        "all_required_artifacts_present": set(ARTIFACT_PATHS).issubset(
            artifact_records
        ),
        "all_required_artifacts_passed": all(
            artifact.get("status") == "passed" for artifact in artifacts.values()
        ),
        "prior_output_digests_valid": all(
            record["output_digest_valid"] for record in artifact_records.values()
        ),
        "all_matrix_row_digests_valid": all(
            row["matrix_row_digest"]
            == digest_value(
                {
                    key: value
                    for key, value in row.items()
                    if key != "matrix_row_digest"
                }
            )
            for row in matrix_rows
        ),
        "support_intact_preserves_composition": by_state["support_intact_survives"][
            "outcome_matches_expectation"
        ],
        "mild_withdrawal_preserves_bounded_companion": by_state[
            "mild_withdrawal_survives"
        ]["outcome_matches_expectation"],
        "disrupted_support_blocks_full_composition": by_state[
            "n09_matched_withdrawal_disrupts_support"
        ]["outcome_matches_expectation"],
        "explicit_restoration_resumes_full_composition": by_state[
            "explicit_restoration_recovers_support"
        ]["outcome_matches_expectation"],
        "restoration_preserves_disruption_history": closeout[
            "restoration_preserves_disruption_history"
        ],
        "hypothesis_b_supported": closeout["hypothesis_b_supported"] is True,
        "closeout_digest_valid": closeout["hypothesis_b_closeout_digest"]
        == digest_value(
            {
                key: value
                for key, value in closeout.items()
                if key != "hypothesis_b_closeout_digest"
            }
        ),
        "artifact_only_replay": closeout["artifact_only"] is True
        and closeout["runtime_state_used"] is False,
        "claim_flags_all_false": all(
            value is False for value in closeout["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "src_clean_for_iteration_12": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    artifacts = {key: load_json(path) for key, path in ARTIFACT_PATHS.items()}
    artifact_records, report_records = build_artifact_records(artifacts)
    matrix_rows = build_matrix_rows(artifacts)
    closeout = build_closeout_record(artifacts, matrix_rows)
    controls = build_controls(matrix_rows, closeout)
    checks = build_checks(artifacts, artifact_records, matrix_rows, closeout, controls)
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_support_intact_and_mild_withdrawal_rows",
                "artifact": artifact_records[
                    "n10_iteration_8_bounded_repeated_integration"
                ]["path"],
            },
            {
                "step": "load_hypothesis_a_closeout",
                "artifact": artifact_records["n10_iteration_9_hypothesis_a_closeout"][
                    "path"
                ],
            },
            {
                "step": "load_disrupted_support_block",
                "artifact": artifact_records[
                    "n10_iteration_10_disrupted_support_control"
                ]["path"],
            },
            {
                "step": "load_explicit_restoration_resumption",
                "artifact": artifact_records[
                    "n10_iteration_11_explicit_restoration_replay"
                ]["path"],
            },
            {
                "step": "emit_hypothesis_b_support_state_matrix_closeout",
                "hypothesis_b_closeout_digest": closeout[
                    "hypothesis_b_closeout_digest"
                ],
                "hypothesis_b_supported": closeout["hypothesis_b_supported"],
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 12 passes if the bounded N10 full composition is "
            "validated as support-sensitive: intact and mild-withdrawal "
            "support may preserve the composition, disrupted support blocks or "
            "downgrades it, and explicit restoration can resume it without "
            "erasing disruption history. The closeout is artifact-only, "
            "source-backed, budget-clean, and claim-clean."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_12_hypothesis_b_support_state_matrix_closeout_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 12,
        "purpose": "close_hypothesis_b_support_sensitive_full_composition_matrix",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "artifact_records": artifact_records,
        "report_records": report_records,
        "support_state_matrix": matrix_rows,
        "hypothesis_b_closeout": closeout,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "13_hypothesis_c_native_policy_gap_inventory",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    closeout = output["hypothesis_b_closeout"]
    lines = [
        "# N10 Iteration 12 Hypothesis B Support-State Matrix Closeout",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 12 closes Hypothesis B for the bounded N10 scope. The",
        "result is support-sensitive full composition: intact and mild",
        "support states preserve the composition, disrupted support blocks it,",
        "and explicit restoration resumes it without erasing the disruption",
        "history.",
        "",
        "```text",
        f"hypothesis_b_status = {closeout['hypothesis_b_status']}",
        f"hypothesis_b_supported = {closeout['hypothesis_b_supported']}",
        f"positive_scope = {closeout['positive_scope']}",
        f"disrupted_support_blocker = {closeout['disrupted_support_blocker']}",
        f"restoration_preserves_disruption_history = {closeout['restoration_preserves_disruption_history']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Support-State Matrix",
        "",
        "```json",
        json.dumps(output["support_state_matrix"], indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "Hypothesis B is not a claim that all support states are acceptable.",
        "It is the stronger boundary result: the full composition is accepted",
        "only in support-valid states, blocked when support is disrupted, and",
        "resumed only when explicit restoration evidence exists.",
        "",
        "Hypothesis B was needed because the Hypothesis A positive row could",
        "otherwise be overread as an unconditional route-memory-support-",
        "regulation composition. The support-state matrix tests whether the",
        "composition remains tied to the identity/support prerequisite instead",
        "of becoming a free-standing regulation or agency claim.",
        "",
        "What it proves in the bounded N10 scope:",
        "",
        "```text",
        "support_intact_survives:",
        "    intact support preserves the bounded composition",
        "",
        "mild_withdrawal_survives:",
        "    mild withdrawal preserves the bounded companion scope",
        "",
        "n09_matched_withdrawal_disrupts_support:",
        "    disrupted support blocks attempted A6/ALI6 with",
        "    support_disrupted_but_integration_allowed",
        "",
        "explicit_restoration_recovers_support:",
        "    explicit restoration resumes A6/ALI6 as",
        "    restoration_gated_integration_candidate",
        "```",
        "",
        "The result proves support sensitivity, not agency. The composition",
        "can proceed only when support remains valid, or when explicit",
        "restoration revalidates it. The disrupted-support block is therefore",
        "part of the positive evidence: it shows the validator refuses to",
        "compose regulation over a failed support identity baseline.",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(output["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "All claim flags remain false. Iteration 12 does not emit agency,",
        "semantic goal ownership, identity acceptance, ACO, biological,",
        "personhood, unrestricted agency, A7 generalization, or fully native",
        "agentic-like integration claims.",
        "",
        "## Reproduction",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 12 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

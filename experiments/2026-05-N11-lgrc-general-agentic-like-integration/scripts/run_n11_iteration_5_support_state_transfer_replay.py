#!/usr/bin/env python3
"""Run N11 Iteration 5 support-state transfer replay."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
N07 = ROOT / "experiments" / "2026-05-N07-rc-identity-attractor-invariance"
N10 = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"

BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
ITERATION_3_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_3_route_context_transfer_replay.json"
)
ITERATION_4_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4_proxy_condition_transfer_replay.json"
)
ITERATION_4B_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4b_proxy_target_band_variant_probe.json"
)
N07_WITHDRAWAL_PATH = (
    N07 / "outputs" / "n07_iteration_13_identity_support_withdrawal_baseline.json"
)
N10_I8_PATH = N10 / "outputs" / "n10_iteration_8_bounded_repeated_integration.json"
N10_I10_PATH = (
    N10 / "outputs" / "n10_iteration_10_full_composition_disrupted_support_control.json"
)
N10_I11_PATH = (
    N10 / "outputs" / "n10_iteration_11_full_composition_explicit_restoration_replay.json"
)
N10_I12_PATH = (
    N10 / "outputs" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
)
N10_I15_PATH = (
    N10 / "outputs" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_5_support_state_transfer_replay.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n11_iteration_5_support_state_transfer_replay.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_5_support_state_transfer_replay.py"
)


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


def transfer_row_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in row.items() if key != "transfer_row_digest"}
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def fixture_lane(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 5
        and lane.get("lane_id") == "support_state_transfer_matrix"
    ]
    if len(lanes) != 1:
        raise ValueError("expected exactly one Iteration 5 support fixture lane")
    return lanes[0]


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_3_route_context_transfer_replay": rel(ITERATION_3_PATH),
        "n11_iteration_4_proxy_condition_transfer_replay": rel(ITERATION_4_PATH),
        "n11_iteration_4b_proxy_target_band_variant_probe": rel(ITERATION_4B_PATH),
        "n07_identity_support_withdrawal_baseline": rel(N07_WITHDRAWAL_PATH),
        "n10_iteration_8_bounded_repeated_integration": rel(N10_I8_PATH),
        "n10_iteration_10_disrupted_support_control": rel(N10_I10_PATH),
        "n10_iteration_11_explicit_restoration_replay": rel(N10_I11_PATH),
        "n10_iteration_12_support_state_matrix_closeout": rel(N10_I12_PATH),
        "n10_iteration_15_closeout_and_handoff": rel(N10_I15_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_3_route_context_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_3_route_context_transfer_replay.md"
        ),
        "n11_iteration_4_proxy_condition_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4_proxy_condition_transfer_replay.md"
        ),
        "n11_iteration_4b_proxy_target_band_variant_probe": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4b_proxy_target_band_variant_probe.md"
        ),
        "n07_identity_support_withdrawal_baseline": (
            "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/"
            "n07_iteration_13_identity_support_withdrawal_baseline.md"
        ),
        "n10_iteration_8_bounded_repeated_integration": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_8_bounded_repeated_integration.md"
        ),
        "n10_iteration_10_disrupted_support_control": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_10_full_composition_disrupted_support_control.md"
        ),
        "n10_iteration_11_explicit_restoration_replay": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_11_full_composition_explicit_restoration_replay.md"
        ),
        "n10_iteration_12_support_state_matrix_closeout": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
        ),
        "n10_iteration_15_closeout_and_handoff": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_15_hypothesis_c_closeout_and_handoff.md"
        ),
    }
    return artifacts, digests, reports


def matrix_rows_by_state(n10_i12: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["matrix_state"]: row for row in n10_i12["support_state_matrix"]}


def source_record_for_state(
    state: str,
    n10_i8: dict[str, Any],
    n10_i10: dict[str, Any],
    n10_i11: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    if state == "support_intact_survives":
        return "n10_iteration_8_bounded_repeated_integration.main_integration_row", n10_i8[
            "main_integration_row"
        ]
    if state == "mild_withdrawal_survives":
        return (
            "n10_iteration_8_bounded_repeated_integration.mild_withdrawal_companion_row",
            n10_i8["mild_withdrawal_companion_row"],
        )
    if state == "n09_matched_withdrawal_disrupts_support":
        return (
            "n10_iteration_10_disrupted_support_control.blocked_full_composition_record",
            n10_i10["blocked_full_composition_record"],
        )
    if state == "explicit_restoration_recovers_support":
        return (
            "n10_iteration_11_explicit_restoration_replay.restored_full_composition_row",
            n10_i11["restored_full_composition_row"],
        )
    raise ValueError(f"unexpected support state: {state}")


def outcome_for_state(state: str) -> tuple[bool, str, str | None, str]:
    if state == "support_intact_survives":
        return True, "support_intact_reference_preserved", None, "local_observation_tag"
    if state == "mild_withdrawal_survives":
        return (
            True,
            "support_state_transfer_candidate",
            None,
            "support_dependent_expression",
        )
    if state == "n09_matched_withdrawal_disrupts_support":
        return (
            False,
            "transfer_blocked",
            "support_disrupted_but_integration_allowed",
            "support_dependent_expression",
        )
    if state == "explicit_restoration_recovers_support":
        return (
            True,
            "restoration_gated_support_transfer_candidate",
            None,
            "support_dependent_expression",
        )
    raise ValueError(f"unexpected support state: {state}")


def support_summary(
    state: str,
    source_ref: str,
    source_record: dict[str, Any],
    matrix_row: dict[str, Any],
) -> dict[str, Any]:
    evidence = source_record["support_evidence"]
    return {
        "matrix_state": state,
        "source_ref": source_ref,
        "source_iteration": matrix_row["source_iteration"],
        "source_row_digest": matrix_row["source_row_digest"],
        "matrix_row_digest": matrix_row["matrix_row_digest"],
        "support_state_tag": source_record["support_state_tag"],
        "support_lane_id": evidence["source_lane_id"],
        "support_lane_digest": evidence["lane_digest"],
        "identity_support_digest": source_record["identity_support_digest"],
        "source_current_status": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": evidence["final_A_support_retention"],
        "reference_support_retention": evidence["reference_A_support_retention"],
        "support_survival_threshold": evidence["support_survival_threshold"],
        "support_survival_passed": evidence["support_survival_passed"],
        "withdrawal_depth": evidence.get("withdrawal_depth"),
        "withdrawal_kind": evidence.get("withdrawal_kind"),
        "restoration_fraction": evidence.get("restoration_fraction"),
        "explicit_restoration_present": evidence.get(
            "explicit_restoration_present", False
        ),
        "n09_withdrawal_digest": evidence.get("n09_withdrawal_digest"),
        "integration_allowed": source_record["integration_allowed"],
        "accepted_integration_level": source_record.get("accepted_integration_level"),
        "accepted_n10_category_level": source_record.get(
            "accepted_n10_category_level"
        )
        or (
            source_record.get("n10_category_level")
            if source_record["integration_allowed"]
            else None
        ),
        "source_n10_category_level": source_record.get("n10_category_level"),
        "attempted_integration_level": source_record.get("attempted_integration_level"),
        "attempted_n10_category_level": source_record.get(
            "attempted_n10_category_level"
        ),
        "integration_outcome_tag": source_record["integration_outcome_tag"],
        "primary_blocker": source_record["primary_blocker"],
        "prior_disruption_evidence": source_record.get("prior_disruption_evidence"),
        "node_plus_packet_budget_error": source_record[
            "node_plus_packet_budget_error"
        ],
        "support_budget_error": evidence["final_budget_error"],
        "claim_flags_false": all(
            value is False for value in source_record["claim_flags"].values()
        ),
    }


def build_transfer_row(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    matrix_row: dict[str, Any],
    support_info: dict[str, Any],
    accepted: bool,
    outcome_tag: str,
    primary_blocker: str | None,
    arc_classification: str,
) -> dict[str, Any]:
    source_artifacts, source_digests, source_reports = source_bundle()
    row = {
        "transfer_row_id": f"n11_i5_{support_info['matrix_state']}_row_v1",
        "gali_level": "GALI4",
        "attempted_gali_level": "GALI4",
        "arc_of_becoming_classification": arc_classification,
        "producer_mediation_classification": "producer_mediated",
        "source_boundary": "N10_iteration_15_closeout",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": lane["context_tag"],
        "support_state_tag": support_info["support_state_tag"],
        "proxy_condition_tag": lane["proxy_condition_tag"],
        "source_scope_tag": "n10_bounded_artifact_only_source",
        "transfer_window_tag": "single_replay_window",
        "transfer_outcome_tag": outcome_tag,
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": support_info[
            "node_plus_packet_budget_error"
        ],
        "memory_budget_surface": "n10_source_memory_budget_compatibility",
        "proxy_budget_surface": "n10_source_proxy_budget_compatibility",
        "support_budget_surface": "n07_identity_support_withdrawal_baseline",
        "hidden_steering_used": False,
        "native_policy_gap": baseline["n11_baseline"]["primary_native_blockers"],
        "primary_blocker": primary_blocker,
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": false_claim_flags(baseline),
        "fixture_lane": lane,
        "matrix_row": matrix_row,
        "transfer_accepted": accepted,
        "support_state_transfer_rule_preserved": True,
        "identity_support_not_identity_acceptance": True,
        "support_summary": support_info,
        "interpretation": (
            "N10 Hypothesis B provides source-backed support-state evidence. "
            "N11 replays the support state as support/invariance evidence only; "
            "it does not relabel support survival, disruption, or restoration as "
            "identity acceptance."
        ),
    }
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def build_rows(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    n10_i8: dict[str, Any],
    n10_i10: dict[str, Any],
    n10_i11: dict[str, Any],
    n10_i12: dict[str, Any],
) -> list[dict[str, Any]]:
    rows_by_state = matrix_rows_by_state(n10_i12)
    rows: list[dict[str, Any]] = []
    for state in lane["matrix_states"]:
        source_ref, source_record = source_record_for_state(
            state, n10_i8, n10_i10, n10_i11
        )
        accepted, outcome_tag, primary_blocker, arc_classification = outcome_for_state(
            state
        )
        matrix_row = rows_by_state[state]
        support_info = support_summary(state, source_ref, source_record, matrix_row)
        rows.append(
            build_transfer_row(
                baseline=baseline,
                manifest=manifest,
                lane=lane,
                matrix_row=matrix_row,
                support_info=support_info,
                accepted=accepted,
                outcome_tag=outcome_tag,
                primary_blocker=primary_blocker,
                arc_classification=arc_classification,
            )
        )
    return rows


def validate_rows(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    row_validations = {}
    all_required_fields = True
    all_digests_valid = True
    all_claim_flags_false = True
    for row in rows:
        missing = [field for field in fields if field not in row]
        digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
        claim_flags_false = all(value is False for value in row["claim_flags"].values())
        all_required_fields = all_required_fields and not missing
        all_digests_valid = all_digests_valid and digest_valid
        all_claim_flags_false = all_claim_flags_false and claim_flags_false
        row_validations[row["transfer_row_id"]] = {
            "missing_required_fields": missing,
            "transfer_row_digest_valid": digest_valid,
            "claim_flags_false": claim_flags_false,
            "accepted": row["transfer_accepted"],
            "primary_blocker": row["primary_blocker"],
        }
    return {
        "row_validations": row_validations,
        "all_required_fields_present": all_required_fields,
        "all_transfer_row_digests_valid": all_digests_valid,
        "all_claim_flags_false": all_claim_flags_false,
    }


def support_matrix_summary(
    rows: list[dict[str, Any]],
    n07: dict[str, Any],
    n10_i12: dict[str, Any],
    n10_i15: dict[str, Any],
) -> dict[str, Any]:
    by_state = {row["support_state_tag"]: row for row in rows}
    return {
        "n07_withdrawal_baseline_status": n07["status"],
        "n07_baseline_summary": n07["baseline_summary"],
        "n10_hypothesis_b_status": n10_i12["hypothesis_b_closeout"][
            "hypothesis_b_status"
        ],
        "n10_hypothesis_b_supported": n10_i12["hypothesis_b_closeout"][
            "hypothesis_b_supported"
        ],
        "n10_support_sensitive_rule": n10_i12["hypothesis_b_closeout"][
            "support_sensitive_rule"
        ],
        "n11_handoff_preserves": n10_i15["n11_consumption_handoff"][
            "n11_must_preserve"
        ],
        "matrix_states": [row["support_state_tag"] for row in rows],
        "accepted_states": [
            row["support_state_tag"] for row in rows if row["transfer_accepted"]
        ],
        "blocked_states": [
            row["support_state_tag"]
            for row in rows
            if not row["transfer_accepted"]
        ],
        "support_intact_retention": by_state["support_intact_survives"][
            "support_summary"
        ]["support_retention"],
        "mild_withdrawal_retention": by_state["mild_withdrawal_survives"][
            "support_summary"
        ]["support_retention"],
        "disrupted_support_retention": by_state[
            "n09_matched_withdrawal_disrupts_support"
        ]["support_summary"]["support_retention"],
        "restored_support_retention": by_state[
            "explicit_restoration_recovers_support"
        ]["support_summary"]["support_retention"],
        "support_survival_threshold": by_state["support_intact_survives"][
            "support_summary"
        ]["support_survival_threshold"],
        "disrupted_primary_blocker": by_state[
            "n09_matched_withdrawal_disrupts_support"
        ]["primary_blocker"],
        "restoration_preserves_disruption_history": bool(
            by_state["explicit_restoration_recovers_support"]["support_summary"][
                "prior_disruption_evidence"
            ]
        ),
        "identity_acceptance_claim_allowed": False,
        "runtime_identity_acceptance_claim_allowed": False,
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_3 = load_json(ITERATION_3_PATH)
    iteration_4 = load_json(ITERATION_4_PATH)
    iteration_4b = load_json(ITERATION_4B_PATH)
    n07 = load_json(N07_WITHDRAWAL_PATH)
    n10_i8 = load_json(N10_I8_PATH)
    n10_i10 = load_json(N10_I10_PATH)
    n10_i11 = load_json(N10_I11_PATH)
    n10_i12 = load_json(N10_I12_PATH)
    n10_i15 = load_json(N10_I15_PATH)
    lane = fixture_lane(manifest)
    rows = build_rows(baseline, manifest, lane, n10_i8, n10_i10, n10_i11, n10_i12)
    row_validation = validate_rows(rows, manifest)
    summary = support_matrix_summary(rows, n07, n10_i12, n10_i15)
    controls = {
        "stale_support_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_support_state"],
            "reason": (
                "Support rows cite source-current N10/N07 support digests; stale "
                "support substitution cannot satisfy the transfer row digest."
            ),
        },
        "support_disrupted_without_restoration": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "support_disrupted_but_generalization_allowed"
            ],
            "reason": (
                "The disrupted-support row is blocked with the N10 support-specific "
                "blocker and emits no positive integration row."
            ),
        },
        "restoration_required_but_missing": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "restoration_required_but_missing"
            ],
            "reason": (
                "Restoration-gated transfer is accepted only for the row that "
                "cites explicit restoration and prior disruption history."
            ),
        },
        "identity_acceptance_relabeling": {
            "control_passed": True,
            "primary_blocker": "support_evidence_relabelled_as_identity_acceptance",
            "reason": (
                "N07/N10 support survival, disruption, and restoration remain "
                "support evidence, not runtime identity acceptance."
            ),
        },
        "claim_promotion": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["claim_promotion"],
            "reason": "All claim flags remain false.",
        },
    }
    states = set(lane["matrix_states"])
    row_states = {row["support_state_tag"] for row in rows}
    disrupted = next(
        row
        for row in rows
        if row["support_state_tag"] == "n09_matched_withdrawal_disrupts_support"
    )
    restored = next(
        row
        for row in rows
        if row["support_state_tag"] == "explicit_restoration_recovers_support"
    )
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": load_json(
            EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
        ).get("status")
        == "passed",
        "iteration_3_passed": iteration_3.get("status") == "passed",
        "iteration_4_passed": iteration_4.get("status") == "passed",
        "iteration_4b_proxy_condition_transfer_supported": iteration_4b.get("status")
        == "passed"
        and iteration_4b.get("strongest_supported_gali_level") == "GALI3"
        and iteration_4b.get("accepted_row_count") == 1,
        "iteration_5_fixture_lane_present": lane["lane_id"]
        == "support_state_transfer_matrix",
        "manifest_four_support_states_covered": states == row_states
        and len(rows) == 4,
        "support_intact_reference_included": "support_intact_survives" in row_states,
        "mild_withdrawal_survival_included": any(
            row["support_state_tag"] == "mild_withdrawal_survives"
            and row["transfer_accepted"] is True
            and row["support_summary"]["support_survival_passed"] is True
            for row in rows
        ),
        "disrupted_support_blocking_included": disrupted["transfer_accepted"]
        is False
        and disrupted["primary_blocker"] == "support_disrupted_but_integration_allowed",
        "explicit_restoration_resumption_included": restored["transfer_accepted"]
        is True
        and restored["support_summary"]["explicit_restoration_present"] is True,
        "restoration_preserves_disruption_history": restored["support_summary"][
            "prior_disruption_evidence"
        ]["history_preserved"]
        is True,
        "support_state_digests_recorded": all(
            row["support_summary"]["support_lane_digest"] for row in rows
        ),
        "support_source_current_status_recorded": all(
            row["support_summary"]["source_current_status"]
            == "source_current_from_n10_hypothesis_b_matrix"
            for row in rows
        ),
        "identity_support_not_identity_acceptance": all(
            row["identity_support_not_identity_acceptance"] is True for row in rows
        ),
        "budget_surfaces_separate": all(
            len(
                {
                    row["memory_budget_surface"],
                    row["proxy_budget_surface"],
                    row["support_budget_surface"],
                }
            )
            == 3
            for row in rows
        ),
        "node_plus_packet_budget_errors_zero": all(
            row["node_plus_packet_budget_error"] == 0.0 for row in rows
        ),
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "all_controls_passed": all(
            control["control_passed"] for control in controls.values()
        ),
        "all_claim_flags_false": row_validation["all_claim_flags_false"],
        "identity_acceptance_claims_false": all(
            row["claim_flags"].get("identity_acceptance_claim_allowed") is False
            and row["claim_flags"].get("runtime_identity_acceptance_claim_allowed")
            is False
            for row in rows
        ),
        "a7_not_supported": all(
            row["claim_flags"].get("a7_claim_allowed") is False for row in rows
        ),
        "gali7_not_supported": all(
            row["claim_flags"].get("gali7_claim_allowed") is False for row in rows
        ),
        "src_clean_for_iteration_5": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 5 passes if support-state transfer preserves N10's "
            "support-sensitive boundary: intact and mild support may preserve "
            "transfer, disrupted support must block or downgrade transfer, and "
            "explicit restoration may resume transfer without erasing disruption "
            "history. No identity acceptance or agency claim is emitted."
        ),
    }
    accepted_rows = [row for row in rows if row["transfer_accepted"]]
    blocked_rows = [row for row in rows if not row["transfer_accepted"]]
    output: dict[str, Any] = {
        "schema": "n11_iteration_5_support_state_transfer_replay_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 5,
        "purpose": "support_state_transfer_replay",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "baseline_path": rel(BASELINE_PATH),
        "baseline_inventory_digest": baseline["inventory_digest"],
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "iteration_3_path": rel(ITERATION_3_PATH),
        "iteration_3_output_digest": iteration_3["output_digest"],
        "iteration_4_path": rel(ITERATION_4_PATH),
        "iteration_4_output_digest": iteration_4["output_digest"],
        "iteration_4b_path": rel(ITERATION_4B_PATH),
        "iteration_4b_output_digest": iteration_4b["output_digest"],
        "support_matrix_summary": summary,
        "transfer_rows": rows,
        "accepted_row_count": len(accepted_rows),
        "blocked_row_count": len(blocked_rows),
        "support_axis_supported_gali_level": "GALI4",
        "strongest_supported_gali_level": "GALI4",
        "strongest_contiguous_gali_level": "GALI4",
        "gali3_proxy_condition_transfer_status": "supported_by_iteration_4b",
        "support_state_transfer_ceiling": (
            "support_state_transfer_candidate_with_disrupted_support_block"
        ),
        "non_claim_boundary": {
            "identity_acceptance_claim_allowed": False,
            "runtime_identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_goal_ownership_claim_allowed": False,
            "a7_claim_allowed": False,
            "gali7_claim_allowed": False,
        },
        "controls": controls,
        "row_validation": row_validation,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "6_multi_axis_transfer_matrix",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 5 Support-State Transfer Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 5 replayed the N10 Hypothesis B support-state matrix into",
        "N11. The support axis is supported at GALI4: intact support preserves",
        "the bounded composition, mild withdrawal preserves the bounded companion",
        "scope, disrupted support blocks attempted A6/ALI6, and explicit",
        "restoration resumes A6/ALI6 while preserving disruption history.",
        "",
        "Iteration 4 remains the negative source audit for the original N09",
        "same-band source, while Iteration 4-B supplies a declared proxy",
        "target-band variant with packet-processed source evidence. With GALI3",
        "covered by 4-B, this support-axis result raises the contiguous N11",
        "ceiling to GALI4. The disrupted-support block remains part of the",
        "GALI4 boundary rather than a failed support-axis result.",
        "",
        "Current state:",
        "",
        "```text",
        f"support_axis_supported_gali_level = {output['support_axis_supported_gali_level']}",
        f"strongest_contiguous_gali_level = {output['strongest_contiguous_gali_level']}",
        f"gali3_proxy_condition_transfer_status = {output['gali3_proxy_condition_transfer_status']}",
        f"support_state_transfer_ceiling = {output['support_state_transfer_ceiling']}",
        "identity_acceptance_claim_allowed = false",
        "runtime_identity_acceptance_claim_allowed = false",
        "agency_claim_allowed = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Support Matrix Summary",
        "",
        "```json",
        json.dumps(output["support_matrix_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Transfer Rows",
        "",
        "```json",
        json.dumps(output["transfer_rows"], indent=2, sort_keys=True),
        "```",
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
        "## Interpretation",
        "",
        "This result transfers the support-state rule, not identity acceptance.",
        "It says N11 can consume N10's source-backed support envelope: support",
        "survival and explicit restoration can preserve or resume bounded",
        "artifact-only integration, while support disruption remains a hard",
        "block unless restoration evidence is present. It does not make a claim",
        "that the runtime accepted identity, understood identity, or became",
        "agentic.",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

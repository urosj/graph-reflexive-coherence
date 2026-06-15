#!/usr/bin/env python3
"""Build N12 Iteration 5 identity acceptance boundary artifact."""

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
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N07_EXPERIMENT = ROOT / "experiments" / "2026-05-N07-rc-identity-attractor-invariance"
N10_EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N11_EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"

N07_I13_OUTPUT = (
    N07_EXPERIMENT / "outputs" / "n07_iteration_13_identity_support_withdrawal_baseline.json"
)
N07_I13_REPORT = (
    N07_EXPERIMENT / "reports" / "n07_iteration_13_identity_support_withdrawal_baseline.md"
)
N10_I12_OUTPUT = (
    N10_EXPERIMENT / "outputs" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
)
N10_I12_REPORT = (
    N10_EXPERIMENT / "reports" / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
)
N10_I14_OUTPUT = (
    N10_EXPERIMENT
    / "outputs"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
N10_I14_REPORT = (
    N10_EXPERIMENT
    / "reports"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.md"
)
N11_I11_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)
N11_I11_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
)
N11_I12_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_12_final_closeout_and_handoff.json"
)
N11_I12_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_12_final_closeout_and_handoff.md"
)

OUTPUT_PATH = OUTPUTS / "n12_identity_acceptance_boundary.json"
REPORT_PATH = REPORTS / "n12_identity_acceptance_boundary.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_identity_acceptance_boundary.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
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


def row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "row_digest"})


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
        "artifact_digest": None if artifact is None else artifact.get("artifact_digest"),
    }


def source_report(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": digest_file(path)}


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def find_inventory_identity_row(inventory: dict[str, Any]) -> dict[str, Any]:
    for row in inventory["n12_inventory_rows"]:
        if row.get("native_gap") == "native_identity_acceptance_validator_missing":
            return row
    raise ValueError("N12 identity acceptance inventory row not found")


def find_contract_row(n10_i14: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in n10_i14["native_contract_requirements"]:
        if row.get("row_id") == row_id:
            return row
    raise ValueError(f"N10 contract row not found: {row_id}")


def find_n11_gap_row(n11_i11: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in n11_i11["native_generalization_gap_rows"]:
        if row.get("row_id") == row_id:
            return row
    raise ValueError(f"N11 gap row not found: {row_id}")


def build_record_schema_sketch() -> dict[str, Any]:
    return {
        "record_type": "identity_acceptance_boundary_record",
        "version": "v1",
        "status": "blocked_theory_boundary_not_native_policy",
        "records_available": [
            "native_identity_support_validator_record",
            "support_state_history_record",
            "withdrawal_restoration_history_record",
        ],
        "records_missing_before_phase8_entry": [
            "identity_acceptance_event_record",
            "runtime_acceptance_validator_record",
            "rc_identity_collapse_validator_record",
        ],
        "forbidden_fields": [
            "semantic_identity_acceptance",
            "runtime_self_acceptance",
            "rc_identity_collapse_flag",
            "identity_personhood_state",
            "hidden_restoration_state",
            "report_side_acceptance_override",
        ],
    }


def build_boundary_row(
    inventory_row: dict[str, Any],
    n07_i13: dict[str, Any],
    n10_i12: dict[str, Any],
    n10_contract: dict[str, Any],
    n11_gap: dict[str, Any],
) -> dict[str, Any]:
    missing_gates = [
        "formal_identity_acceptance_semantics_missing",
        "runtime_acceptance_validator_missing",
        "identity_acceptance_event_schema_missing",
        "identity_continuity_vs_acceptance_theory_gate_missing",
        "rc_identity_collapse_theory_not_formalized",
        "support_survival_not_identity_acceptance",
        "native_acceptance_mutation_boundary_not_formalized",
        "native_acceptance_telemetry_contract_missing",
    ]
    theory_entry_gates = [
        {
            "gate_id": "identity_acceptance_semantics_formalized",
            "required_before": "NAT3_or_NAT4_for_identity_acceptance",
            "status": "missing",
        },
        {
            "gate_id": "runtime_acceptance_event_schema",
            "required_before": "native_identity_acceptance_validator_design",
            "status": "missing",
        },
        {
            "gate_id": "identity_continuity_acceptance_split",
            "required_before": "support_evidence_can_feed_acceptance_validator",
            "status": "missing",
        },
        {
            "gate_id": "rc_identity_collapse_claim_boundary",
            "required_before": "any_rc_identity_collapse_validator",
            "status": "missing",
        },
    ]
    support_lanes = [
        {
            "lane_id": lane["lane_id"],
            "identity_support_outcome_tag": lane["identity_support_outcome_tag"],
            "support_survival_passed": lane["support_survival_passed"],
            "support_survival_threshold": lane["support_survival_threshold"],
            "withdrawal_depth": lane["withdrawal_depth"],
            "restoration_fraction": lane["restoration_fraction"],
            "claim_boundary": lane["claim_boundary"],
        }
        for lane in n07_i13["withdrawal_lanes"]
    ]
    support_acceptance_boundary = {
        "boundary_status": "identity_acceptance_blocked",
        "support_survival_evidence_available": True,
        "support_survival_evidence_source": rel(N07_I13_OUTPUT),
        "support_survival_threshold": n07_i13["reference_metrics"][
            "support_survival_threshold"
        ],
        "support_lanes": support_lanes,
        "n10_support_matrix_states": n10_i12["hypothesis_b_closeout"][
            "matrix_states"
        ],
        "support_survival_meaning": (
            "support retention/disruption/restoration classification under "
            "serialized withdrawal lanes"
        ),
        "identity_continuity_meaning": (
            "lineage-current support history can be replayed but does not imply "
            "runtime acceptance"
        ),
        "identity_acceptance_meaning": "not formalized in N05-N11 or N12",
        "runtime_acceptance_meaning": "blocked until acceptance event semantics exist",
        "rc_identity_collapse_meaning": "blocked theory claim, not a validator result",
    }
    non_rc_quantity_audit = {
        "audit_status": "blocked_theory_sensitive_not_nat4",
        "field_required": True,
        "is_support_survival_rc_observable": True,
        "is_identity_acceptance_derived_observable": False,
        "does_identity_acceptance_require_semantics_not_yet_formalized": True,
        "would_acceptance_require_new_unaccounted_quantity_without_theory": True,
        "extra_unaccounted_quantity_allowed": False,
        "nat4_blocker_if_extra_quantity_required": (
            "identity_acceptance_semantics_not_formalized"
        ),
        "candidate_specific_questions": {
            "is_support_survival_identity_acceptance": False,
            "is_identity_continuity_runtime_acceptance": False,
            "is_restoration_history_identity_acceptance": False,
            "does_rc_identity_collapse_have_formal_validator": False,
            "can_acceptance_be_added_as_report_side_label": False,
        },
    }
    mutation_boundary = {
        "status": "blocked_until_identity_acceptance_theory_is_formalized",
        "producer_or_policy_may_schedule_only": None,
        "step_or_topology_event_owns_state_mutation": None,
        "reason": (
            "support history replay can be recorded, but no native acceptance "
            "state mutation or validator semantics are defined"
        ),
    }
    default_off_flags = {
        "identity_acceptance_validator_enabled_default": False,
        "runtime_acceptance_validator_enabled_default": False,
        "rc_identity_collapse_validator_enabled_default": False,
        "native_support_flags_default": False,
    }
    enabled_validated_supported_separation = {
        "support_survival_evidence_available": True,
        "support_survival_evidence_native_supported": False,
        "identity_acceptance_enabled": False,
        "identity_acceptance_validated": False,
        "identity_acceptance_supported": False,
        "runtime_acceptance_supported": False,
        "rc_identity_collapse_supported": False,
    }
    telemetry_requirements = [
        "future_identity_support_telemetry_must_remain_separate_from_acceptance",
        "identity_acceptance_flags_exported_false_until_theory_gate_passes",
        "support_state_digest_and_restoration_history_digest",
        "withdrawal_event_digest_and_restoration_event_digest",
        "claim_flags_forced_false_snapshot",
        "default_off_native_identity_acceptance_records",
        "src_pygrc_telemetry_namespace_required_if_phase8_later_opens",
    ]
    snapshot_replay_requirements = [
        "replay reconstructs support lanes and support survival outcomes",
        "replay preserves disruption and explicit restoration history",
        "replay keeps support survival distinct from identity acceptance",
        "replay rejects hidden restoration",
        "replay rejects report-side identity acceptance labels",
    ]
    compatibility_tests = [
        "support_survival_not_identity_acceptance",
        "identity_continuity_not_runtime_acceptance",
        "restoration_history_not_acceptance",
        "rc_identity_collapse_claim_blocked",
        "identity_acceptance_claim_flags_false",
        "phase8_ready_false_for_identity_boundary",
        "native_supported_flags_false",
        "hidden_restoration_rejected",
        "support_history_erasure_rejected",
    ]
    blocked_claims = sorted(
        set(inventory_row["blocked_claims"])
        | {
            "identity acceptance",
            "runtime identity acceptance",
            "rc identity collapse",
            "native identity acceptance support",
            "unrestricted identity",
            "personhood",
            "agency",
        }
    )
    row = {
        "row_id": "n12_i5_identity_acceptance_boundary_v1",
        "source_experiment": "N07_N10_N11_N12",
        "source_iteration": "N12_iteration_5",
        "source_artifact": rel(ITERATION_1_OUTPUT),
        "source_report": rel(ITERATION_1_REPORT),
        "source_sha256": digest_file(ITERATION_1_OUTPUT),
        "source_report_sha256": digest_file(ITERATION_1_REPORT),
        "source_gap_rows": inventory_row["source_gap_rows"],
        "source_contract_rows": inventory_row["source_contract_rows"],
        "source_gap_row_summaries": inventory_row["source_gap_row_summaries"],
        "source_row_digest": inventory_row["row_digest"],
        "mechanism_name": "native_identity_acceptance_validator_boundary",
        "mechanism_role": "theory_sensitive_identity_acceptance_blocker",
        "secondary_tags": [
            "theory_sensitive_blocker",
            "identity_support_boundary",
            "support_survival_not_identity_acceptance",
            "phase8_not_ready",
        ],
        "producer_decision_fields": inventory_row["producer_decision_fields"],
        "bookkeeping_fields": sorted(
            set(inventory_row["bookkeeping_fields"])
            | {
                "support_lane_digest",
                "withdrawal_event_digest",
                "explicit_restoration_digest",
            }
        ),
        "runtime_visible_surfaces": sorted(
            set(inventory_row["runtime_visible_surfaces"])
            | {
                "support_state_history_surface",
                "withdrawal_restoration_history_surface",
            }
        ),
        "runtime_visible_inputs": n10_contract["runtime_visible_inputs"],
        "contract_runtime_visible_inputs": inventory_row[
            "contract_runtime_visible_inputs"
        ],
        "budget_surfaces": inventory_row["budget_surfaces"],
        "thresholds_to_serialize": inventory_row["thresholds_to_serialize"],
        "native_gap": "native_identity_acceptance_validator_missing",
        "native_policy_name": "native_identity_acceptance_validator",
        "record_schema_sketch": build_record_schema_sketch(),
        "covered_policy_records": inventory_row["covered_policy_records"],
        "primary_disposition": "theory_sensitive_blocker",
        "nat_level": "NAT2",
        "phase8_ready": False,
        "phase8_readiness_source": "defer_until_identity_acceptance_theory_is_precise",
        "phase8_decision_source": "defer_until_identity_acceptance_theory_is_precise",
        "phase8_order_source": inventory_row["phase8_order_source"],
        "claim_ceiling": inventory_row["claim_ceiling"],
        "blocked_claims": blocked_claims,
        "missing_gates": missing_gates,
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "artifact_replay_requirements": snapshot_replay_requirements,
        "claim_boundary_controls": sorted(
            set(inventory_row["claim_boundary_controls"])
            | {
                "support_survival_relabelled_identity_acceptance_blocked",
                "identity_continuity_relabelled_runtime_acceptance_blocked",
                "restoration_relabelled_acceptance_blocked",
            }
        ),
        "ordering_requirements": n10_contract["ordering_requirements"],
        "stale_context_blockers": n10_contract["stale_context_blockers"],
        "n11_native_supported": n11_gap["native_supported"],
        "n11_native_support_scope": n11_gap["native_support_scope"],
        "mutation_boundary": mutation_boundary,
        "producer_or_policy_may_schedule_only": None,
        "step_or_topology_event_owns_state_mutation": None,
        "default_off_flags": default_off_flags,
        "enabled_validated_supported_separation": enabled_validated_supported_separation,
        "idempotency_digest_plan": {
            "status": "support_history_digest_only_acceptance_digest_blocked",
            "available_digests": [
                "support_state_digest",
                "restoration_history_digest",
                "withdrawal_event_digest",
            ],
            "missing_digest": "identity_acceptance_event_digest",
        },
        "telemetry_requirements": telemetry_requirements,
        "snapshot_replay_requirements": snapshot_replay_requirements,
        "negative_controls": sorted(
            set(inventory_row["negative_controls"])
            | set(n10_contract["negative_controls"])
            | {
                "identity_acceptance_without_semantics_rejected",
                "runtime_acceptance_without_event_schema_rejected",
                "rc_identity_collapse_relabel_rejected",
            }
        ),
        "compatibility_tests": compatibility_tests,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags_false": True,
        "phase8_opened_false": True,
        "support_acceptance_boundary": support_acceptance_boundary,
        "theory_entry_gates": theory_entry_gates,
        "deferred_phase8_requirements": {
            "status": "blocked",
            "minimum_before_reconsidering_nat3": [
                "formal semantics for identity acceptance",
                "runtime-visible acceptance event schema",
                "acceptance-vs-continuity separation rule",
                "negative controls for acceptance relabeling",
                "default-off telemetry contract under src/pygrc/telemetry",
            ],
            "minimum_before_nat4": [
                "native policy name with accepted semantics",
                "record schema for acceptance event and validator result",
                "idempotent digest over support, continuity, event, and budget",
                "snapshot/replay validator that rejects report-side acceptance",
                "compatibility tests preserving forced-false agency claims",
            ],
        },
        "source_evidence_summary": {
            "n07_status": n07_i13["status"],
            "n07_general_identity_acceptance_supported": n07_i13[
                "baseline_summary"
            ]["general_identity_acceptance_supported"],
            "n07_claim_boundary_identity_acceptance_allowed": n07_i13[
                "claim_boundary"
            ]["identity_acceptance_claim_allowed"],
            "n10_hypothesis_b_positive_scope": n10_i12["hypothesis_b_closeout"][
                "positive_scope"
            ],
            "n10_hypothesis_b_runtime_state_used": n10_i12["hypothesis_b_closeout"][
                "runtime_state_used"
            ],
            "n10_contract_phase8_readiness": n10_contract["phase_8_readiness"],
            "n11_gap_phase8_readiness": n11_gap["phase8_readiness"],
            "n11_gap_native_support_scope": n11_gap["native_support_scope"],
        },
    }
    row["row_digest"] = row_digest(row)
    return row


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    n07_i13 = load_json(N07_I13_OUTPUT)
    n10_i12 = load_json(N10_I12_OUTPUT)
    n10_i14 = load_json(N10_I14_OUTPUT)
    n11_i11 = load_json(N11_I11_OUTPUT)
    n11_i12 = load_json(N11_I12_OUTPUT)

    inventory_row = find_inventory_identity_row(inventory)
    n10_contract = find_contract_row(
        n10_i14, "n10_i14_contract_04_identity_support_validator"
    )
    n11_gap = find_n11_gap_row(n11_i11, "n11_i11_gap_04_identity_support_validator")
    row = build_boundary_row(
        inventory_row=inventory_row,
        n07_i13=n07_i13,
        n10_i12=n10_i12,
        n10_contract=n10_contract,
        n11_gap=n11_gap,
    )

    final_fields = schema["final_row_fields"]
    missing_final_fields = sorted(field for field in final_fields if field not in row)
    candidate_extension_fields = sorted(
        field
        for field in row
        if field
        not in set(final_fields)
        | {
            "row_digest",
        }
    )
    schema_alignment = {
        "final_row_field_count": len(final_fields),
        "missing_final_row_fields": missing_final_fields,
        "candidate_extension_fields": candidate_extension_fields,
        "candidate_extension_field_meaning": {
            "support_acceptance_boundary": (
                "Iteration 5 support survival, identity continuity, runtime "
                "acceptance, and RC identity collapse separation."
            ),
            "theory_entry_gates": (
                "Theory gates required before identity acceptance can move "
                "beyond a blocked boundary."
            ),
            "deferred_phase8_requirements": (
                "Minimum future requirements before reconsidering NAT3/NAT4."
            ),
            "source_evidence_summary": "Short source-backed boundary summary.",
        },
    }

    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(N07_I13_OUTPUT): source_artifact(N07_I13_OUTPUT, n07_i13),
        rel(N10_I12_OUTPUT): source_artifact(N10_I12_OUTPUT, n10_i12),
        rel(N10_I14_OUTPUT): source_artifact(N10_I14_OUTPUT, n10_i14),
        rel(N11_I11_OUTPUT): source_artifact(N11_I11_OUTPUT, n11_i11),
        rel(N11_I12_OUTPUT): source_artifact(N11_I12_OUTPUT, n11_i12),
    }
    source_reports = {
        rel(ITERATION_1_REPORT): source_report(ITERATION_1_REPORT),
        rel(ITERATION_2_REPORT): source_report(ITERATION_2_REPORT),
        rel(N07_I13_REPORT): source_report(N07_I13_REPORT),
        rel(N10_I12_REPORT): source_report(N10_I12_REPORT),
        rel(N10_I14_REPORT): source_report(N10_I14_REPORT),
        rel(N11_I11_REPORT): source_report(N11_I11_REPORT),
        rel(N11_I12_REPORT): source_report(N11_I12_REPORT),
    }

    checks = {
        "n07_support_baseline_passed": n07_i13["status"] == "passed",
        "n10_support_matrix_passed": n10_i12["status"] == "passed",
        "n10_contract_identity_support_validator_found": (
            n10_contract["row_id"] == "n10_i14_contract_04_identity_support_validator"
        ),
        "n11_identity_gap_found": (
            n11_gap["native_gap"] == "native_identity_acceptance_validator_missing"
        ),
        "support_survival_separated_from_identity_acceptance": (
            row["support_acceptance_boundary"]["identity_acceptance_meaning"]
            == "not formalized in N05-N11 or N12"
            and row["support_acceptance_boundary"]["support_survival_evidence_available"]
        ),
        "identity_continuity_separated_from_runtime_acceptance": (
            row["support_acceptance_boundary"]["runtime_acceptance_meaning"]
            == "blocked until acceptance event semantics exist"
        ),
        "rc_identity_collapse_claims_blocked": (
            CLAIM_FLAGS_FORCED_FALSE["rc_identity_collapse_claim_allowed"] is False
            and "rc_identity_collapse_theory_not_formalized" in row["missing_gates"]
        ),
        "validator_local_support_fields_identified": bool(
            set(row["runtime_visible_inputs"])
            & {
                "support_area_digest",
                "support_state_policy_id",
                "withdrawal_event_digest",
                "restoration_event_digest",
            }
        ),
        "missing_formal_acceptance_semantics_recorded": (
            "formal_identity_acceptance_semantics_missing" in row["missing_gates"]
        ),
        "no_identity_acceptance_claim_opens": (
            row["claim_flags_forced_false"]["identity_acceptance_claim_allowed"]
            is False
            and row["claim_flags_forced_false"][
                "runtime_identity_acceptance_claim_allowed"
            ]
            is False
        ),
        "nat_level_is_nat2_not_nat4": row["nat_level"] == "NAT2",
        "phase8_ready_false": row["phase8_ready"] is False,
        "primary_disposition_theory_sensitive_blocker": (
            row["primary_disposition"] == "theory_sensitive_blocker"
        ),
        "native_supported_flags_false": row["native_supported_flags_false"] is True,
        "phase8_opened_false": row["phase8_opened_false"] is True,
        "claim_flags_all_false": all_claim_flags_false(row["claim_flags_forced_false"]),
        "schema_alignment_complete": missing_final_fields == [],
        "src_clean": row["src_diff_empty"] is True,
        "source_file_sha256_all_present": all(
            artifact["sha256"] for artifact in source_artifacts.values()
        ),
    }

    output = {
        "experiment": "N12",
        "iteration": 5,
        "purpose": "identity_acceptance_boundary_theory_sensitive_blocker",
        "schema": "n12_identity_acceptance_boundary_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "boundary_result": {
            "primary_disposition": row["primary_disposition"],
            "nat_level": row["nat_level"],
            "phase8_ready": row["phase8_ready"],
            "native_policy_name": row["native_policy_name"],
            "identity_acceptance_claim_opened": False,
            "native_support_opened": False,
            "phase8_opened": False,
            "supported_interpretation": (
                "Identity acceptance remains a theory-sensitive blocked "
                "boundary. Support survival evidence is source-backed but does "
                "not become identity acceptance or native support."
            ),
        },
        "checks": checks,
        "identity_acceptance_boundary": row,
        "schema_alignment": schema_alignment,
        "claim_boundary": {
            "support_survival_is_identity_acceptance": False,
            "identity_continuity_is_runtime_acceptance": False,
            "restoration_history_is_identity_acceptance": False,
            "identity_validator_candidate_is_identity_acceptance": False,
            "identity_acceptance_is_native_support": False,
            "native_support_is_agency": False,
            "rc_identity_collapse_claim_opened": False,
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "source_digest_policy": {
            "row_source_sha256": row["source_sha256"],
            "row_source_report_sha256": row["source_report_sha256"],
            "all_source_file_sha256_present": checks["source_file_sha256_all_present"],
            "output_digest_used_when_source_exposes_it": True,
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
    row = output["identity_acceptance_boundary"]
    lines = [
        "# N12 Iteration 5 Identity Acceptance Boundary",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"primary_disposition = {row['primary_disposition']}",
        f"nat_level = {row['nat_level']}",
        f"phase8_ready = {str(row['phase8_ready']).lower()}",
        "phase8_opened = false",
        "native_support_opened = false",
        "identity_acceptance_claim_opened = false",
        "```",
        "",
        "Iteration 5 records identity acceptance as a theory-sensitive blocked",
        "boundary. It preserves N07/N10/N11 support-survival evidence, but does",
        "not promote support survival, continuity, or explicit restoration into",
        "identity acceptance, runtime acceptance, RC identity collapse, native",
        "support, or agency.",
        "",
        "The JSON artifact is the source of truth for the full boundary row,",
        "source artifacts, digests, missing gates, controls, and replay rules.",
        "",
        "## Source Decision",
        "",
        "N07 supplies source-backed support withdrawal/restoration lanes. N10",
        "shows bounded support-sensitive composition and defines a future",
        "identity-support validator contract. N11 keeps the identity acceptance",
        "validator blocked until theory is precise.",
        "",
        "```json",
        json.dumps(row["source_evidence_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Support Vs Acceptance Boundary",
        "",
        "```json",
        json.dumps(row["support_acceptance_boundary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Theory Entry Gates",
        "",
        "```json",
        json.dumps(row["theory_entry_gates"], indent=2, sort_keys=True),
        "```",
        "",
        "## Deferred Phase 8 Requirements",
        "",
        "```json",
        json.dumps(row["deferred_phase8_requirements"], indent=2, sort_keys=True),
        "```",
        "",
        "## Record Schema Sketch",
        "",
        "```json",
        json.dumps(row["record_schema_sketch"], indent=2, sort_keys=True),
        "```",
        "",
        "## Non-RC Quantity Audit",
        "",
        "```json",
        json.dumps(row["non_rc_quantity_audit"], indent=2, sort_keys=True),
        "```",
        "",
        "## Mutation Boundary",
        "",
        "```json",
        json.dumps(row["mutation_boundary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Telemetry And Replay Requirements",
        "",
        "```json",
        json.dumps(
            {
                "telemetry_requirements": row["telemetry_requirements"],
                "snapshot_replay_requirements": row["snapshot_replay_requirements"],
                "compatibility_tests": row["compatibility_tests"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Schema Alignment",
        "",
        "```json",
        json.dumps(output["schema_alignment"], indent=2, sort_keys=True),
        "```",
        "",
        "## Source Digest Policy",
        "",
        "```json",
        json.dumps(output["source_digest_policy"], indent=2, sort_keys=True),
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
        "support survival != identity acceptance",
        "identity continuity != runtime acceptance",
        "restoration history != identity acceptance",
        "identity validator candidate != identity acceptance",
        "identity acceptance != native support",
        "native support != agency",
        "RC identity collapse remains blocked",
        "phase8_ready = false",
        "```",
        "",
        "## Output Digest",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
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

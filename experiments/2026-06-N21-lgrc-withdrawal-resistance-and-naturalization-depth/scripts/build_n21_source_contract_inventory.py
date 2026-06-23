#!/usr/bin/env python3
"""Build N21 Iteration 1 source contract inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_source_contract_inventory.json"
REPORT = EXPERIMENT / "reports" / "n21_source_contract_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_source_contract_inventory.py"
)

N20_CLOSEOUT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_closeout_and_n21_handoff.json"
)
N20_I5_CONTRACT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

REQUIRED_ROWS = {
    "withdrawal_resistance": "n20_i5_row_01_withdrawal_resistance",
    "naturalization_depth": "n20_i5_row_02_naturalization_depth",
}

EXPECTED_READINESS_GATE = {
    "must_consume_i5_contract": True,
    "may_redefine_n20_contract_to_pass": False,
    "must_declare_row_specific_thresholds_before_use": True,
    "must_produce_source_backed_pass_fail_evidence": True,
    "must_fail_closed_on_hidden_support": True,
    "must_fail_closed_on_proxy_only_success": True,
    "must_keep_primitive_evidence_separate_from_contract": True,
    "must_keep_agency_native_phase8_sentience_claims_blocked": True,
}

BLOCKED_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def local_source(path: str, role: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["parseable_json"] = True
        record["status"] = str(data.get("status", "not_recorded"))
        record["acceptance_state"] = str(data.get("acceptance_state", "not_recorded"))
        record["output_digest"] = str(data.get("output_digest", "not_recorded"))
    return record


def all_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def global_unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in BLOCKED_CLAIMS}


def control_ids(controls: dict[str, Any]) -> list[str]:
    shared = [
        str(control["control_id"])
        for control in controls.get("shared_controls", [])
        if isinstance(control, dict)
    ]
    primitive_specific = [
        str(control["control_id"])
        for control in controls.get("primitive_specific_controls", [])
        if isinstance(control, dict)
    ]
    return shared + primitive_specific


def row_digest(row_data: dict[str, Any]) -> str:
    return digest_value(row_data)


def contract_inventory_row(row_data: dict[str, Any]) -> dict[str, Any]:
    primitive_id = str(row_data["primitive_id"])
    handoff_inputs = row_data["n21_handoff_inputs"]
    minimum_controls = row_data["minimum_controls"]
    same_basin_rule = row_data["same_basin_continuation_rule"]
    support_scaffold = row_data["support_scaffold_declaration"]
    source_unsafe_claim_flags = dict(row_data["unsafe_claim_flags"])
    global_flags = global_unsafe_claim_flags()
    source_current_fields = list(row_data["LGRC_visible_fields"])
    producer_mediated_fields = list(row_data["producer_mediated_fields"])
    naturalization_debt_fields = list(row_data["naturalization_debt_fields"])
    blocked_relabel_fields = list(row_data["blocked_relabel_fields"])

    return {
        "row_id": f"n21_i1_row_{1 if primitive_id == 'withdrawal_resistance' else 2:02d}_{primitive_id}",
        "primitive_id": primitive_id,
        "primitive_name": str(row_data["primitive_name"]),
        "source_contract_row": str(row_data["row_id"]),
        "source_contract_row_digest": row_digest(row_data),
        "source_artifact": N20_I5_CONTRACT_PATH,
        "source_contract_status": str(row_data["contract_status"]),
        "n20_source_downstream_consumption_status": str(
            row_data["downstream_consumption_status"]
        ),
        "n20_source_status_note": (
            "Inherited from the N20 source artifact; this is not an N21 "
            "iteration status."
        ),
        "source_primitive_evidence_opened": bool(row_data["primitive_evidence_opened"]),
        "source_primitive_supported": bool(row_data["primitive_supported"]),
        "contract_consumed_without_redefinition": True,
        "n21_inventory_role": "source_contract_input_only",
        "n21_primitive_evidence_opened": False,
        "n21_primitive_supported": False,
        "n21_ladder_rung_assigned": False,
        "wr_ladder_rung": (
            "not_assigned_contract_inventory_only"
            if primitive_id == "withdrawal_resistance"
            else "not_applicable"
        ),
        "nd_ladder_rung": (
            "not_assigned_contract_inventory_only"
            if primitive_id == "naturalization_depth"
            else "not_applicable"
        ),
        "allowed_next_assignment_source": "source_backed_N21_evidence_rows_only",
        "source_current_fields": source_current_fields,
        "producer_mediated_fields": producer_mediated_fields,
        "naturalization_debt_fields": naturalization_debt_fields,
        "row_specific_blocked_relabels": blocked_relabel_fields,
        "blocked_relabel_fields": blocked_relabel_fields,
        "handoff_inputs": handoff_inputs,
        "same_basin_rule": {
            "rule_id": same_basin_rule["rule_id"],
            "basin_signature_fields": same_basin_rule["basin_signature_fields"],
            "required_support_floor": same_basin_rule["required_support_floor"],
            "required_coherence_floor": same_basin_rule["required_coherence_floor"],
            "boundary_integrity_floor": same_basin_rule["boundary_integrity_floor"],
            "flux_balance_bounds": same_basin_rule["flux_balance_bounds"],
            "replay_requirement": same_basin_rule["replay_requirement"],
            "failure_modes": same_basin_rule["failure_modes"],
            "proxy_only_success_allowed": same_basin_rule[
                "proxy_only_success_allowed"
            ],
            "hidden_producer_support_allowed": same_basin_rule[
                "hidden_producer_support_allowed"
            ],
            "label_only_continuation_allowed": same_basin_rule[
                "label_only_continuation_allowed"
            ],
        },
        "support_scaffold": {
            "support_id": support_scaffold["support_id"],
            "declared_supports": support_scaffold["declared_supports"],
            "required_supports": support_scaffold["required_supports"],
            "withdrawable_supports": support_scaffold["withdrawable_supports"],
            "hidden_support_allowed": support_scaffold["hidden_support_allowed"],
            "hidden_support_blocker": support_scaffold["hidden_support_blocker"],
            "producer_supplied_scaffolds": support_scaffold[
                "producer_supplied_scaffolds"
            ],
            "producer_role": support_scaffold["producer_role"],
        },
        "required_control_ids": control_ids(minimum_controls),
        "controls_declared_fail_closed_in_contract": bool(
            minimum_controls["all_controls_fail_closed"]
        ),
        "control_execution_status": "not_run",
        "global_unsafe_claim_flags": global_flags,
        "source_unsafe_claim_flags": source_unsafe_claim_flags,
        "unsafe_claim_flags": global_flags,
        "global_unsafe_claim_flags_all_false": all_false(global_flags),
        "source_unsafe_claim_flags_all_false": all_false(source_unsafe_claim_flags),
        "unsafe_claim_flag_scope": {
            "global_unsafe_claim_flags": (
                "N21-wide unsafe claim family; every listed claim is forced false."
            ),
            "row_specific_blocked_relabels": (
                "Primitive-specific blocked relabel fields inherited from N20; "
                "they are not required to appear as global unsafe flag keys."
            ),
        },
        "blocked_claims_carried_forward": BLOCKED_CLAIMS,
        "claim_ceiling": (
            "source contract input only; no N21 primitive evidence, agency, "
            "native support, Phase 8, sentience, or ant-ecology implementation"
        ),
        "inventory_decision": "supported_as_contract_input_only",
        "row_decision": "not_applicable",
    }


def source_contract_rows(contract_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = contract_data["contract_rows"]
    by_id = {row["row_id"]: row for row in rows}
    missing = [row_id for row_id in REQUIRED_ROWS.values() if row_id not in by_id]
    if missing:
        raise KeyError(f"Missing required N20 I5 rows: {missing}")
    return [contract_inventory_row(by_id[row_id]) for row_id in REQUIRED_ROWS.values()]


def evidence_admissibility_contract() -> dict[str, Any]:
    return {
        "iteration_1_role": "inventory_only",
        "source_current_definition": (
            "emitted by the LGRC runtime or replay from declared run artifacts, "
            "not invented by a report builder, label, post-hoc parser, or "
            "producer-only policy"
        ),
        "positive_evidence_requires_future_run_artifacts": True,
        "required_future_run_artifact_fields": [
            "run_artifact_id",
            "source_commit_or_source_digest",
            "runtime_config_digest",
            "source_contract_row_digest",
            "baseline_artifact_path",
            "withdrawn_or_probe_absent_artifact_path",
            "event_log_or_trace_path",
            "snapshot_or_replay_artifact_path",
            "artifact_digest",
            "derived_report_only",
        ],
        "derived_report_only_true_blocks_positive_support": True,
        "n20_contract_completeness_assigns_ladder_rungs": False,
        "ladder_rungs_require_source_backed_n21_evidence": True,
    }


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def build_checks(
    closeout: dict[str, Any], contract_data: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    handoff = closeout["n21_handoff"]
    readiness_gate = handoff["readiness_gate"]
    artifact_invariants = closeout["artifact_invariants"]
    row_by_primitive = {row["primitive_id"]: row for row in rows}

    expected_controls = {
        "withdrawal_resistance": {
            "label_only_success_control",
            "proxy_only_success_control",
            "hidden_producer_support_control",
            "post_hoc_trace_construction_control",
            "semantic_relabel_control",
            "native_support_relabel_control",
            "phase8_relabel_control",
            "withdrawal_schedule_removed_control",
            "hidden_support_margin_control",
            "support_floor_crossing_control",
        },
        "naturalization_depth": {
            "label_only_success_control",
            "proxy_only_success_control",
            "hidden_producer_support_control",
            "post_hoc_trace_construction_control",
            "semantic_relabel_control",
            "native_support_relabel_control",
            "phase8_relabel_control",
            "probe_present_only_control",
            "probe_residue_control",
            "support_source_annotation_relabel_control",
        },
    }

    return [
        check(
            "n20_closeout_passed_and_ready_for_n21",
            closeout.get("status") == "passed"
            and closeout.get("acceptance_state")
            == "closed_n20_contract_and_n21_handoff_no_primitive_evidence"
            and bool(handoff.get("ready_for_n21")) is True,
            {
                "status": closeout.get("status"),
                "acceptance_state": closeout.get("acceptance_state"),
                "ready_for_n21": handoff.get("ready_for_n21"),
            },
        ),
        check(
            "n21_handoff_scope_matches_required_primitives",
            sorted(handoff.get("handoff_scope", [])) == sorted(REQUIRED_ROWS.keys()),
            handoff.get("handoff_scope", []),
        ),
        check(
            "readiness_gate_matches_expected",
            readiness_gate == EXPECTED_READINESS_GATE,
            readiness_gate,
        ),
        check(
            "n20_i5_contract_artifact_passed",
            contract_data.get("status") == "passed"
            and contract_data.get("acceptance_state")
            == "accepted_same_basin_control_contract_complete_no_primitive_evidence",
            {
                "status": contract_data.get("status"),
                "acceptance_state": contract_data.get("acceptance_state"),
            },
        ),
        check(
            "required_i5_contract_rows_present",
            set(row_by_primitive.keys()) == set(REQUIRED_ROWS.keys()),
            sorted(row_by_primitive.keys()),
        ),
        check(
            "required_i5_rows_contract_complete",
            all(row["source_contract_status"] == "complete" for row in rows),
            {row["primitive_id"]: row["source_contract_status"] for row in rows},
        ),
        check(
            "contract_rows_consumed_without_redefinition",
            all(row["contract_consumed_without_redefinition"] for row in rows),
            {
                row["primitive_id"]: row["contract_consumed_without_redefinition"]
                for row in rows
            },
        ),
        check(
            "primitive_evidence_not_opened",
            all(not row["n21_primitive_evidence_opened"] for row in rows)
            and not closeout["primitive_evidence_opened"]
            and not contract_data["artifact_invariants"]["primitive_evidence_opened"],
            {
                "n21_rows": {
                    row["primitive_id"]: row["n21_primitive_evidence_opened"]
                    for row in rows
                },
                "n20_closeout": closeout["primitive_evidence_opened"],
                "n20_i5": contract_data["artifact_invariants"][
                    "primitive_evidence_opened"
                ],
            },
        ),
        check(
            "primitive_support_not_claimed",
            all(not row["n21_primitive_supported"] for row in rows),
            {row["primitive_id"]: row["n21_primitive_supported"] for row in rows},
        ),
        check(
            "ladder_rungs_not_assigned_by_contract_inventory",
            all(not row["n21_ladder_rung_assigned"] for row in rows),
            {
                row["primitive_id"]: {
                    "wr_ladder_rung": row["wr_ladder_rung"],
                    "nd_ladder_rung": row["nd_ladder_rung"],
                }
                for row in rows
            },
        ),
        check(
            "source_current_fields_recorded",
            all(row["source_current_fields"] for row in rows),
            {row["primitive_id"]: row["source_current_fields"] for row in rows},
        ),
        check(
            "producer_and_debt_fields_recorded",
            all(row["producer_mediated_fields"] for row in rows)
            and all(row["naturalization_debt_fields"] for row in rows),
            {
                row["primitive_id"]: {
                    "producer_mediated_fields": row["producer_mediated_fields"],
                    "naturalization_debt_fields": row["naturalization_debt_fields"],
                }
                for row in rows
            },
        ),
        check(
            "blocked_relabel_fields_recorded",
            all(row["blocked_relabel_fields"] for row in rows),
            {row["primitive_id"]: len(row["blocked_relabel_fields"]) for row in rows},
        ),
        check(
            "required_controls_recorded",
            all(
                expected_controls[row["primitive_id"]].issubset(
                    set(row["required_control_ids"])
                )
                for row in rows
            ),
            {row["primitive_id"]: row["required_control_ids"] for row in rows},
        ),
        check(
            "global_unsafe_claim_flags_cover_blocked_claims",
            all(set(row["global_unsafe_claim_flags"].keys()) == set(BLOCKED_CLAIMS) for row in rows),
            {row["primitive_id"]: sorted(row["global_unsafe_claim_flags"].keys()) for row in rows},
        ),
        check(
            "global_and_source_unsafe_claim_flags_false_per_row",
            all(row["global_unsafe_claim_flags_all_false"] for row in rows)
            and all(row["source_unsafe_claim_flags_all_false"] for row in rows),
            {
                row["primitive_id"]: {
                    "global_unsafe_claim_flags": row["global_unsafe_claim_flags"],
                    "source_unsafe_claim_flags": row["source_unsafe_claim_flags"],
                    "row_specific_blocked_relabel_count": len(
                        row["row_specific_blocked_relabels"]
                    ),
                }
                for row in rows
            },
        ),
        check(
            "row_specific_blocked_relabels_separated_from_global_flags",
            all(row["row_specific_blocked_relabels"] for row in rows),
            {
                row["primitive_id"]: row["unsafe_claim_flag_scope"]
                for row in rows
            },
        ),
        check(
            "inventory_decision_uses_standard_row_decision",
            all(row["row_decision"] == "not_applicable" for row in rows)
            and all(
                row["inventory_decision"] == "supported_as_contract_input_only"
                for row in rows
            ),
            {
                row["primitive_id"]: {
                    "row_decision": row["row_decision"],
                    "inventory_decision": row["inventory_decision"],
                }
                for row in rows
            },
        ),
        check(
            "controls_declared_not_executed_in_inventory",
            all(row["controls_declared_fail_closed_in_contract"] for row in rows)
            and all(row["control_execution_status"] == "not_run" for row in rows),
            {
                row["primitive_id"]: {
                    "controls_declared_fail_closed_in_contract": row[
                        "controls_declared_fail_closed_in_contract"
                    ],
                    "control_execution_status": row["control_execution_status"],
                }
                for row in rows
            },
        ),
        check(
            "agency_native_phase8_sentience_ant_ecology_unopened",
            not closeout["agency_claim_opened"]
            and not closeout["phase8_opened"]
            and not closeout["native_support_opened"]
            and not closeout["sentience_opened"]
            and not closeout["ant_ecology_spec_opened"]
            and not artifact_invariants["agency_claim_opened"]
            and not artifact_invariants["phase8_opened"]
            and not artifact_invariants["native_support_opened"]
            and not artifact_invariants["sentience_opened"]
            and not artifact_invariants["ant_ecology_spec_opened"],
            {
                "agency_claim_opened": closeout["agency_claim_opened"],
                "phase8_opened": closeout["phase8_opened"],
                "native_support_opened": closeout["native_support_opened"],
                "sentience_opened": closeout["sentience_opened"],
                "ant_ecology_spec_opened": closeout["ant_ecology_spec_opened"],
            },
        ),
    ]


def contains_local_absolute_path(text: str) -> bool:
    needles = [
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "file" + "://",
        "vscode" + "://",
    ]
    return any(needle in text for needle in needles)


def build_payload() -> dict[str, Any]:
    closeout = load_json(N20_CLOSEOUT_PATH)
    contract_data = load_json(N20_I5_CONTRACT_PATH)
    rows = source_contract_rows(contract_data)
    source_artifacts = [
        local_source(N20_CLOSEOUT_PATH, "n20_closeout_and_n21_handoff"),
        local_source(N20_I5_CONTRACT_PATH, "n20_i5_same_basin_contract"),
        local_source(N20_HANDOFF_PATH, "n20_n29_handoff"),
        local_source(N20_ROADMAP_PATH, "n20_n29_roadmap"),
    ]

    checks = build_checks(closeout, contract_data, rows)

    payload: dict[str, Any] = {
        "artifact_id": "n21_source_contract_inventory",
        "schema_version": "n21_source_contract_inventory_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": 1,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_source_contract_inventory_no_primitive_evidence",
        "purpose": (
            "Inventory N20 closeout and I5 contract rows for N21 without opening "
            "withdrawal-resistance or naturalization-depth primitive evidence."
        ),
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "source_context_boundary": {
            "markdown_sources_context_only": [
                N20_HANDOFF_PATH,
                N20_ROADMAP_PATH,
            ],
            "markdown_sources_may_consume_as": [
                "context",
                "boundary",
                "roadmap",
            ],
            "markdown_sources_must_not_consume_as": [
                "source_current_run_artifact",
                "positive_primitive_evidence",
                "WR_or_ND_ladder_rung_assignment_source",
            ],
        },
        "source_closeout_summary": {
            "n20_status": closeout["status"],
            "n20_acceptance_state": closeout["acceptance_state"],
            "n20_output_digest": closeout["output_digest"],
            "ready_for_n21": closeout["n21_handoff"]["ready_for_n21"],
            "handoff_scope": closeout["n21_handoff"]["handoff_scope"],
            "readiness_gate": closeout["n21_handoff"]["readiness_gate"],
            "blockers": closeout["n21_handoff"]["blockers"],
        },
        "source_contract_rows": rows,
        "evidence_admissibility_contract": evidence_admissibility_contract(),
        "iteration1_boundary": {
            "primitive_evidence_opened": False,
            "withdrawal_resistance_supported": False,
            "naturalization_depth_supported": False,
            "wr_ladder_rung_assigned": False,
            "nd_ladder_rung_assigned": False,
            "n21_closeout_ladder_rung_assigned": False,
            "positive_run_artifacts_consumed": False,
            "source_contract_inventory_only": True,
            "ready_for_iteration_2_schema_freeze": True,
        },
        "blocked_claims": BLOCKED_CLAIMS,
        "checks": checks,
    }

    serialized_without_no_path_check = canonical_json(payload)
    no_absolute_paths = not contains_local_absolute_path(serialized_without_no_path_check)
    payload["checks"].append(
        check(
            "no_local_absolute_paths",
            no_absolute_paths,
            "payload uses repository-relative paths and source IDs only",
        )
    )
    payload["failed_checks"] = [
        item["check_id"] for item in payload["checks"] if not item["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_source_contract_inventory_checks_failed"

    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    lines: list[str] = [
        "# N21 Iteration 1 - Source Contract Inventory",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 1 is inventory-only. It consumes N20 closeout and I5 contract",
        "rows, records readiness gates, and does not assign WR, ND, or N21-C",
        "ladder rungs.",
        "",
        "## Source Artifacts",
        "",
        "| Role | Path | Status | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]

    for source in data["source_artifacts"]:
        lines.append(
            "| {role} | `{path}` | `{status}` | `{sha}` |".format(
                role=source["source_role"],
                path=source["path"],
                status=source.get("status", "not_json"),
                sha=source["sha256"],
            )
        )

    lines.extend(
        [
            "",
            "## Contract Rows",
            "",
            "| Primitive | Source row | Contract | Source fields | Controls | Evidence opened |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in data["source_contract_rows"]:
        lines.append(
            "| `{primitive}` | `{source_row}` | `{status}` | {field_count} | {control_count} | `{opened}` |".format(
                primitive=row["primitive_id"],
                source_row=row["source_contract_row"],
                status=row["source_contract_status"],
                field_count=len(row["source_current_fields"]),
                control_count=len(row["required_control_ids"]),
                opened=str(row["n21_primitive_evidence_opened"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Readiness Gate",
            "",
            "```json",
            json.dumps(
                data["source_closeout_summary"]["readiness_gate"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Evidence Boundary",
            "",
            "```text",
            "primitive_evidence_opened = false",
            "withdrawal_resistance_supported = false",
            "naturalization_depth_supported = false",
            "wr_ladder_rung_assigned = false",
            "nd_ladder_rung_assigned = false",
            "positive_run_artifacts_consumed = false",
            "```",
            "",
            "N20 contract completeness defines N21 eligibility only. WR, ND, and",
            "N21-C rungs require later source-backed N21 evidence rows.",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 1 passes as a source contract inventory. It confirms that the",
            "two required N20 I5 rows are complete contract inputs for N21 and that",
            "the N20 handoff marks N21 ready. It does not support withdrawal",
            "resistance, naturalization depth, agency, native support, sentience,",
            "Phase 8, or ant-ecology implementation.",
            "",
        ]
    )

    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()

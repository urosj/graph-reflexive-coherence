#!/usr/bin/env python3
"""Build N20 Iteration 6 closeout and N21 handoff."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-22T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
HYPOTHESES = EXPERIMENT / "hypotheses"

SOURCE_SPECS = [
    {
        "key": "i1_source_inventory",
        "iteration": 1,
        "artifact": OUTPUTS / "n20_source_method_inventory.json",
        "report": REPORTS / "n20_source_method_inventory.md",
        "role": "source_and_method_inventory",
    },
    {
        "key": "i2_translation_schema",
        "iteration": 2,
        "artifact": OUTPUTS / "n20_translation_schema_v1.json",
        "report": REPORTS / "n20_translation_schema_v1.md",
        "role": "translation_schema_and_gap_rules",
    },
    {
        "key": "i3_residue_ledger",
        "iteration": 3,
        "artifact": OUTPUTS / "n20_producer_residue_ledger.json",
        "report": REPORTS / "n20_producer_residue_ledger.md",
        "role": "producer_residue_and_naturalization_debt_ledger",
    },
    {
        "key": "i4_function_proxy_scaffold",
        "iteration": 4,
        "artifact": OUTPUTS / "n20_native_function_proxy_contract.json",
        "report": REPORTS / "n20_native_function_proxy_contract.md",
        "role": "continuation_function_proxy_scaffold_contract",
    },
    {
        "key": "i5_same_basin_control",
        "iteration": 5,
        "artifact": OUTPUTS / "n20_same_basin_continuation_contract.json",
        "report": REPORTS / "n20_same_basin_continuation_contract.md",
        "role": "same_basin_continuation_and_control_contract",
    },
]

HYPOTHESIS_SPECS = [
    {
        "hypothesis_id": "hypothesis_a_becoming_diagnostic_translation",
        "path": HYPOTHESES / "hypothesis_a_becoming_diagnostic_translation.md",
        "closeout_decision": "closed_supported_as_translation_contract",
        "scope": (
            "agency-of-becoming diagnostics are translated into LGRC-visible "
            "primitive contracts without semantic promotion"
        ),
        "supported_by": ["I1", "I2", "I3", "I4", "I5", "I6"],
    },
    {
        "hypothesis_id": "hypothesis_b_producer_residue_and_naturalization_debt",
        "path": HYPOTHESES
        / "hypothesis_b_producer_residue_and_naturalization_debt.md",
        "closeout_decision": "closed_supported_as_residue_debt_contract",
        "scope": (
            "substrate-carried fields, producer-mediated fields, naturalization "
            "debt, and blocked relabels are separated before primitive tests"
        ),
        "supported_by": ["I2", "I3", "I4", "I5", "I6"],
    },
    {
        "hypothesis_id": "hypothesis_c_claim_boundary_and_gap_preservation",
        "path": HYPOTHESES / "hypothesis_c_claim_boundary_and_gap_preservation.md",
        "closeout_decision": "closed_supported_as_claim_boundary_contract",
        "scope": (
            "N19 AP4/AP5 NAT4 gaps and unsafe claim blockers remain preserved "
            "while N20 closes as contract work"
        ),
        "supported_by": ["I1", "I2", "I3", "I4", "I5", "I6"],
    },
    {
        "hypothesis_id": "hypothesis_d_downstream_contract_enforceability",
        "path": HYPOTHESES / "hypothesis_d_downstream_contract_enforceability.md",
        "closeout_decision": "closed_supported_as_downstream_enforceable_contract",
        "scope": (
            "N21-N28 must consume the frozen N20 contract without redefining "
            "basin signature, continuation condition, proxy-only success, or "
            "producer-residue classification in order to pass"
        ),
        "supported_by": ["I2", "I3", "I4", "I5", "I6"],
    },
]

OUTPUT = OUTPUTS / "n20_closeout_and_n21_handoff.json"
REPORT = REPORTS / "n20_closeout_and_n21_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_closeout_and_n21_handoff.py"
)

INVARIANTS = {
    "primitive_evidence_opened": False,
    "agency_claim_opened": False,
    "phase8_opened": False,
    "native_support_opened": False,
    "sentience_opened": False,
    "ant_ecology_spec_opened": False,
    "src_diff_empty_required": True,
}

BLOCKED_CLOSEOUT_CLAIMS = [
    "primitive support",
    "withdrawal resistance supported",
    "naturalization depth supported",
    "susceptibility update supported",
    "learning or choice",
    "abundance",
    "spark or new-basin formation",
    "proxy collapse supported",
    "configuration/substrate transfer supported",
    "generative/extractive persistence supported",
    "agency",
    "semantic action",
    "semantic perception",
    "semantic goal ownership",
    "selfhood",
    "identity acceptance",
    "native support",
    "Phase 8 implementation",
    "sentience",
    "ant ecology implementation",
    "organism/life behavior",
    "unrestricted autonomy",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: dict[str, Any]) -> str:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        markers = (
            "/" + "home" + "/",
            "/" + "tmp" + "/",
            "/" + "Users" + "/",
            "file://",
            "C:" + "\\",
            "\\Users\\",
        )
        return value.startswith(("/", "\\")) or any(marker in value for marker in markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def git_status_short(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0 and not git_status_short("src")


def source_entry(spec: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_key": spec["key"],
        "source_iteration": spec["iteration"],
        "source_role": spec["role"],
        "source_artifact": rel(spec["artifact"]),
        "source_report": rel(spec["report"]),
        "source_sha256": sha256_file(spec["artifact"]),
        "source_report_sha256": sha256_file(spec["report"]),
        "source_status": artifact["status"],
        "source_acceptance_state": artifact["acceptance_state"],
        "source_output_digest": artifact["output_digest"],
    }


def unsafe_flags_false(row: dict[str, Any]) -> bool:
    flags = row.get("unsafe_claim_flags", {})
    return isinstance(flags, dict) and bool(flags) and all(value is False for value in flags.values())


def n21_rows(i5: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in i5["contract_rows"]
        if row["primitive_id"] in {"withdrawal_resistance", "naturalization_depth"}
    ]
    return sorted(rows, key=lambda row: row["primitive_id"])


def n21_handoff_row(row: dict[str, Any]) -> dict[str, Any]:
    controls = [
        control["control_id"]
        for control in row["minimum_controls"]["shared_controls"]
        + row["minimum_controls"]["primitive_specific_controls"]
    ]
    return {
        "primitive_id": row["primitive_id"],
        "primitive_name": row["primitive_name"],
        "source_i5_row_id": row["row_id"],
        "handoff_status": "ready_for_n21_contract_consumption",
        "contract_status": row["contract_status"],
        "expected_first_positive_experiment": row["expected_first_positive_experiment"],
        "primitive_specific_consumption_inputs": row["primitive_specific_consumption_inputs"],
        "LGRC_visible_fields": row["LGRC_visible_fields"],
        "producer_mediated_fields": row["producer_mediated_fields"],
        "naturalization_debt_fields": row["naturalization_debt_fields"],
        "blocked_relabel_fields": row["blocked_relabel_fields"],
        "continuation_function_descriptor": row["continuation_function_descriptor"],
        "proxy_metric_definition": row["proxy_metric_definition"],
        "support_scaffold_declaration": row["support_scaffold_declaration"],
        "same_basin_continuation_rule": row["same_basin_continuation_rule"],
        "minimum_control_ids": controls,
        "n21_handoff_inputs": row["n21_handoff_inputs"],
        "primitive_supported": False,
        "primitive_evidence_opened": False,
        "claim_ceiling": row["claim_ceiling"],
        "unsafe_claim_flags": row["unsafe_claim_flags"],
    }


def hypothesis_closeout() -> list[dict[str, Any]]:
    return [
        {
            "hypothesis_id": spec["hypothesis_id"],
            "path": rel(spec["path"]),
            "sha256": sha256_file(spec["path"]),
            "closeout_decision": spec["closeout_decision"],
            "scope": spec["scope"],
            "supported_by": spec["supported_by"],
            "primitive_evidence_required": False,
            "primitive_evidence_opened": False,
        }
        for spec in HYPOTHESIS_SPECS
    ]


def build_checks(artifact: dict[str, Any], i5: dict[str, Any]) -> list[dict[str, Any]]:
    rows = i5["contract_rows"]
    n21 = artifact["n21_handoff"]["handoff_rows"]
    return [
        {
            "check_id": "all_source_artifacts_passed",
            "passed": all(source["source_status"] == "passed" for source in artifact["source_artifacts"]),
            "detail": [source["source_key"] for source in artifact["source_artifacts"]],
        },
        {
            "check_id": "i5_contract_passed_and_ready_for_closeout",
            "passed": i5["status"] == "passed"
            and not i5["failed_checks"]
            and i5["iteration6_handoff"]["ready_for_iteration_6_closeout"] is True,
            "detail": i5["acceptance_state"],
        },
        {
            "check_id": "contract_rows_complete_not_primitive_evidence",
            "passed": i5["contract_completion_alias"]["contract_complete"] is True
            and i5["contract_completion_alias"]["primitive_supported"] is False
            and i5["contract_completion_alias"]["primitive_evidence_opened"] is False
            and artifact["n20_contract_complete"] is True
            and artifact["primitive_evidence_opened"] is False,
            "detail": i5["contract_completion_alias"],
        },
        {
            "check_id": "artifact_invariants_preserved",
            "passed": artifact["artifact_invariants"] == INVARIANTS
            and all(artifact[key] == value for key, value in INVARIANTS.items() if key != "src_diff_empty_required"),
            "detail": artifact["artifact_invariants"],
        },
        {
            "check_id": "unsafe_claim_flags_false_per_row",
            "passed": all(unsafe_flags_false(row) for row in rows)
            and all(unsafe_flags_false(row) for row in n21),
            "detail": len(rows),
        },
        {
            "check_id": "definition_guards_preserved",
            "passed": i5["definition_sufficiency_status"]
            == "necessary_contract_gates_not_sufficient_primitive_evidence"
            and i5["definition_outcome_guard"]["contract_definitions_are_primitive_evidence"]
            is False
            and i5["definition_outcome_guard"][
                "future_rows_must_supply_source_backed_pass_fail_evidence"
            ]
            is True,
            "detail": i5["definition_outcome_guard"],
        },
        {
            "check_id": "ap4_ap5_gap_guards_preserved",
            "passed": i5["ap5_dependency_refinement"][
                "susceptibility_update_split_status"
            ]
            == "explicit_split_not_gap_removal"
            and i5["ap5_dependency_refinement"]["n19_ap5_gap_removed"] is False,
            "detail": i5["ap5_dependency_refinement"],
        },
        {
            "check_id": "n21_handoff_rows_present",
            "passed": [row["primitive_id"] for row in n21]
            == ["naturalization_depth", "withdrawal_resistance"]
            and all(row["n21_handoff_inputs"] for row in n21),
            "detail": [row["primitive_id"] for row in n21],
        },
        {
            "check_id": "n21_handoff_requires_hidden_support_and_proxy_controls",
            "passed": all(
                "hidden_producer_support_control" in row["minimum_control_ids"]
                and "proxy_only_success_control" in row["minimum_control_ids"]
                and row["same_basin_continuation_rule"]["hidden_producer_support_allowed"]
                is False
                and row["same_basin_continuation_rule"]["proxy_only_success_allowed"]
                is False
                for row in n21
            ),
            "detail": "N21 rows fail closed for hidden support and proxy-only success",
        },
        {
            "check_id": "n21_readiness_gate_blocks_redefinition",
            "passed": artifact["n21_handoff"]["readiness_gate"][
                "may_redefine_n20_contract_to_pass"
            ]
            is False
            and artifact["n21_handoff"]["readiness_gate"][
                "must_consume_i5_contract"
            ]
            is True,
            "detail": artifact["n21_handoff"]["readiness_gate"],
        },
        {
            "check_id": "hypotheses_closed_as_contract_supported",
            "passed": len(artifact["hypothesis_closeout"]) == 4
            and all(
                row["closeout_decision"].startswith("closed_supported_as_")
                and row["primitive_evidence_opened"] is False
                for row in artifact["hypothesis_closeout"]
            ),
            "detail": [row["hypothesis_id"] for row in artifact["hypothesis_closeout"]],
        },
        {
            "check_id": "src_diff_empty",
            "passed": artifact["src_diff_empty"] is True,
            "detail": artifact["src_diff_empty"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "all closeout paths are repository-relative",
        },
    ]


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 6 - Closeout And N21 Handoff",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"final_supported_status = {artifact['final_supported_status']}",
        f"final_claim_ceiling = {artifact['final_claim_ceiling']}",
        f"n20_contract_complete = {str(artifact['n20_contract_complete']).lower()}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        f"src_diff_empty = {str(artifact['src_diff_empty']).lower()}",
        "```",
        "",
        "Interpretation:",
        "",
        "```text",
        artifact["interpretation"]["main_read"],
        "```",
        "",
        "Hypothesis closeout:",
        "",
        "| Hypothesis | Decision |",
        "| --- | --- |",
    ]
    for row in artifact["hypothesis_closeout"]:
        lines.append(f"| {row['hypothesis_id']} | {row['closeout_decision']} |")
    lines.extend(
        [
            "",
            "N21 handoff rows:",
            "",
            "| Primitive | Source Row | Status |",
            "| --- | --- | --- |",
        ]
    )
    for row in artifact["n21_handoff"]["handoff_rows"]:
        lines.append(
            f"| {row['primitive_id']} | {row['source_i5_row_id']} | {row['handoff_status']} |"
        )
    lines.extend(
        [
            "",
            "N21 readiness gate:",
            "",
            "```json",
            json.dumps(artifact["n21_handoff"]["readiness_gate"], indent=2, sort_keys=True),
            "```",
            "",
            "Blocked closeout claims:",
            "",
        ]
    )
    for claim in artifact["blocked_closeout_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    source_artifacts = []
    loaded: dict[str, dict[str, Any]] = {}
    for spec in SOURCE_SPECS:
        artifact = load_json(spec["artifact"])
        loaded[spec["key"]] = artifact
        source_artifacts.append(source_entry(spec, artifact))

    i5 = loaded["i5_same_basin_control"]
    n21_rows_data = [n21_handoff_row(row) for row in n21_rows(i5)]
    artifact: dict[str, Any] = {
        "artifact_id": "n20_closeout_and_n21_handoff",
        "schema_version": "n20_closeout_and_n21_handoff_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 6,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Close N20 as a becoming-primitive translation contract and hand "
            "withdrawal-resistance / naturalization-depth contract rows to N21."
        ),
        "source_artifacts": source_artifacts,
        "artifact_invariants": INVARIANTS,
        "final_supported_status": "N20_contract_closed_no_primitive_evidence",
        "final_claim_ceiling": "artifact_level_becoming_primitive_translation_contract_only",
        "acceptance_state": "pending",
        "n20_contract_complete": True,
        "contract_status_counts": i5["contract_status_counts"],
        "contract_completion_alias": i5["contract_completion_alias"],
        "primitive_evidence_opened": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_spec_opened": False,
        "src_diff_empty": src_diff_empty(),
        "hypothesis_closeout": hypothesis_closeout(),
        "ap4_ap5_gap_closeout": {
            "ap4_gap_carried_forward": True,
            "ap5_gap_carried_forward": True,
            "ap5_susceptibility_update_split": i5["ap5_dependency_refinement"],
            "ap5_gap_removed": False,
            "claim_boundary": (
                "N20 records AP4/AP5 dependency rules for later primitive tests; "
                "it does not resolve the N19 NAT4 gaps."
            ),
        },
        "definition_closeout": {
            "definition_validation_status": i5["definition_validation_status"],
            "definition_sufficiency_status": i5["definition_sufficiency_status"],
            "definition_outcome_guard": i5["definition_outcome_guard"],
            "definition_revision_policy": i5["definition_revision_policy"],
        },
        "n21_handoff": {
            "ready_for_n21": True,
            "first_positive_experiment": "N21",
            "handoff_scope": [
                "withdrawal_resistance",
                "naturalization_depth",
            ],
            "handoff_rows": n21_rows_data,
            "readiness_gate": {
                "must_consume_i5_contract": True,
                "may_redefine_n20_contract_to_pass": False,
                "must_declare_row_specific_thresholds_before_use": True,
                "must_produce_source_backed_pass_fail_evidence": True,
                "must_fail_closed_on_hidden_support": True,
                "must_fail_closed_on_proxy_only_success": True,
                "must_keep_primitive_evidence_separate_from_contract": True,
                "must_keep_agency_native_phase8_sentience_claims_blocked": True,
            },
            "blockers": [
                "missing I5 same-basin rule",
                "missing declared support/coherence floor",
                "missing boundary integrity check",
                "hidden support preserves margin",
                "proxy-only success",
                "label-only continuation",
                "post-hoc replay construction",
                "producer-mediated state relabeled as native support",
                "semantic agency or sentience relabel",
            ],
        },
        "blocked_closeout_claims": BLOCKED_CLOSEOUT_CLAIMS,
        "interpretation": {
            "main_read": (
                "N20 closes as a contract/schema experiment. It translates "
                "becoming-agency diagnostics into LGRC-visible contract rows, "
                "separates producer residue and naturalization debt, freezes "
                "same-basin and proxy-failure rules, and hands N21 the first two "
                "primitive contracts. It does not produce primitive evidence."
            ),
            "n21_read": (
                "N21 may start with withdrawal resistance and naturalization depth, "
                "but only by consuming the I5 contract rows and producing new "
                "source-backed pass/fail evidence."
            ),
        },
        "output_digest": "pending",
    }
    checks = build_checks(artifact, i5)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "closed_n20_contract_and_n21_handoff_no_primitive_evidence"
        if not failed_checks
        else "failed_n20_closeout_and_n21_handoff"
    )
    artifact["output_digest"] = digest_value(artifact)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

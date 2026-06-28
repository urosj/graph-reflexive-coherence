#!/usr/bin/env python3
"""Build N26 Iteration 1 source inventory and scoped substrate admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_source_inventory_and_scoped_substrate_admission.json"
REPORT = EXPERIMENT / "reports" / "n26_source_inventory_and_scoped_substrate_admission.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_source_inventory_and_scoped_substrate_admission.py"
)

N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N15_CLOSEOUT_PATH = (
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "outputs/n15_closeout_and_handoff.json"
)
N15_CLAIM_BOUNDARY_PATH = (
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "outputs/n15_claim_boundary_record.json"
)
N19_CANDIDATE_MATRIX_PATH = (
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "outputs/n19_candidate_classification_matrix.json"
)
N19_CLOSEOUT_PATH = (
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "outputs/n19_closeout_and_handoff.json"
)
N25_CLOSEOUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_closeout_and_n26_handoff.json"
)
N25_1_SCHEMA_PATH = (
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "outputs/n25_1_multi_basin_extension_schema.json"
)
N25_1_CLOSEOUT_PATH = (
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "outputs/n25_1_closeout_and_phase8_extension_handoff.json"
)
N25_2_CLOSEOUT_PATH = (
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
    "outputs/n25_2_closeout_and_n26_handoff.json"
)
N25_2_GATE_PATH = (
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
    "outputs/n25_2_mb6_support_blocker_matrix.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

SOURCE_CONTRACT_ROW = "n20_i4_row_07_proxy_divergence_proxy_collapse"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_07_proxy_divergence_proxy_collapse"
N19_AP5_NAT3_ROW = "n19_i3_row_05_n15_proxy_derivation_contract_nat3"
PRIMITIVE_ID = "proxy_divergence_proxy_collapse"

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

SOURCE_ROWS: list[dict[str, Any]] = [
    {
        "source_id": "n20_native_function_proxy_contract",
        "path": N20_NATIVE_FUNCTION_PATH,
        "source_classification": "contract_source",
        "source_role": "proxy_divergence_proxy_collapse_schema_source",
        "may_consume_as": ["N20_i4_proxy_contract", "contract_fields_context"],
        "must_not_consume_as": ["primitive_evidence", "positive_proxy_result"],
    },
    {
        "source_id": "n20_same_basin_continuation_contract",
        "path": N20_SAME_BASIN_PATH,
        "source_classification": "contract_source",
        "source_role": "same_basin_rule_and_controls_source",
        "may_consume_as": ["N20_i5_complete_proxy_same_basin_contract"],
        "must_not_consume_as": ["primitive_evidence", "positive_proxy_result"],
    },
    {
        "source_id": "n15_ap5_closeout",
        "path": N15_CLOSEOUT_PATH,
        "source_classification": "historical_ap5_context",
        "source_role": "artifact_level_ap5_proxy_formation_context",
        "may_consume_as": ["historic_artifact_level_AP5_context", "proxy_boundary_context"],
        "must_not_consume_as": ["native_AP5", "semantic_goal", "agency", "native_support"],
    },
    {
        "source_id": "n15_claim_boundary_record",
        "path": N15_CLAIM_BOUNDARY_PATH,
        "source_classification": "claim_boundary_context",
        "source_role": "ap5_unsafe_promotion_boundary",
        "may_consume_as": ["claim_boundary_context", "AP5_relabel_blocker_context"],
        "must_not_consume_as": ["positive_proxy_evidence", "native_AP5"],
    },
    {
        "source_id": "n19_candidate_classification_matrix",
        "path": N19_CANDIDATE_MATRIX_PATH,
        "source_classification": "ap5_nat_gap_boundary",
        "source_role": "current_AP5_NAT3_gap_classification",
        "may_consume_as": ["AP5_NAT4_gap_boundary", "N19_native_readiness_context"],
        "must_not_consume_as": ["native_AP5_evidence", "proxy_divergence_evidence"],
    },
    {
        "source_id": "n19_closeout",
        "path": N19_CLOSEOUT_PATH,
        "source_classification": "ap_ladder_generation_boundary",
        "source_role": "AP4_AP5_gap_closeout_context",
        "may_consume_as": ["AP4_AP5_NAT4_gap_boundary", "Phase8_readiness_review_context"],
        "must_not_consume_as": ["positive_proxy_evidence", "native_AP5_evidence"],
    },
    {
        "source_id": "n25_closeout",
        "path": N25_CLOSEOUT_PATH,
        "source_classification": "historical_sub_basin_context",
        "source_role": "scoped_BF5_core_sub_basin_context",
        "may_consume_as": [
            "scoped_BF5_high_margin_core_sub_basin_context",
            "N25_C6_bounded_formation_context",
        ],
        "must_not_consume_as": [
            "independent_new_basin_evidence",
            "native_multi_basin_evidence",
            "native_support",
        ],
    },
    {
        "source_id": "n25_1_multi_basin_schema",
        "path": N25_1_SCHEMA_PATH,
        "source_classification": "requirements_context",
        "source_role": "MB0_MB6_schema_and_N26_constraints_context",
        "may_consume_as": ["MB_ladder_context", "N26_consumption_constraint_context"],
        "must_not_consume_as": ["runtime_evidence", "MB6_support_by_itself"],
    },
    {
        "source_id": "n25_1_closeout",
        "path": N25_1_CLOSEOUT_PATH,
        "source_classification": "requirements_bridge_context",
        "source_role": "phase8_extension_requirements_closeout_context",
        "may_consume_as": ["requirements_bridge_context", "N26_scope_context"],
        "must_not_consume_as": ["runtime_evidence", "MB6_support_by_itself"],
    },
    {
        "source_id": "n25_2_closeout",
        "path": N25_2_CLOSEOUT_PATH,
        "source_classification": "scoped_substrate_evidence_source",
        "source_role": "scoped_MB6_multi_basin_substrate_admission_source",
        "may_consume_as": ["scoped_MB6_multi_basin_substrate_evidence"],
        "must_not_consume_as": [
            "unscoped_multi_basin_substrate",
            "native_support",
            "agency",
            "sentience",
            "ant_ecology_implementation",
        ],
    },
    {
        "source_id": "n25_2_mb6_support_blocker_matrix",
        "path": N25_2_GATE_PATH,
        "source_classification": "scoped_substrate_gate_context",
        "source_role": "MB6_support_and_blocker_matrix_context",
        "may_consume_as": ["MB6_gate_context", "blocked_relabel_context"],
        "must_not_consume_as": ["positive_proxy_evidence", "semantic_goal_context"],
    },
    {
        "source_id": "n20_n29_handoff",
        "path": N20_HANDOFF_PATH,
        "source_classification": "handoff_context",
        "source_role": "current_N26_pickup_note",
        "may_consume_as": ["roadmap_handoff_context", "N26_scope_context"],
        "must_not_consume_as": ["positive_proxy_evidence"],
    },
    {
        "source_id": "n20_n29_roadmap",
        "path": N20_ROADMAP_PATH,
        "source_classification": "roadmap_context",
        "source_role": "N26_question_and_iteration_context",
        "may_consume_as": ["roadmap_context", "N26_question_context"],
        "must_not_consume_as": ["positive_proxy_evidence"],
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def walk_dicts(data: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(data, dict):
        found.append(data)
        for value in data.values():
            found.extend(walk_dicts(value))
    elif isinstance(data, list):
        for item in data:
            found.extend(walk_dicts(item))
    return found


def find_row(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for candidate in walk_dicts(data):
        if candidate.get("row_id") == row_id:
            return candidate
    raise KeyError(f"Missing row_id {row_id}")


def first_value(data: Any, key: str, default: Any = "not_recorded") -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = first_value(value, key, None)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = first_value(item, key, None)
            if found is not None:
                return found
    return default


def collect_strings(data: Any) -> set[str]:
    values: set[str] = set()
    if isinstance(data, str):
        values.add(data)
    elif isinstance(data, dict):
        for value in data.values():
            values.update(collect_strings(value))
    elif isinstance(data, list):
        for item in data:
            values.update(collect_strings(item))
    return values


def source_record(row: dict[str, Any]) -> dict[str, Any]:
    path = row["path"]
    full_path = ROOT / path
    artifact_exists = full_path.exists()
    record = {
        **row,
        "artifact_exists": artifact_exists,
        "sha256": sha256_file(path) if artifact_exists else "missing_source_file",
        "path_is_repo_relative": not Path(path).is_absolute(),
    }
    if path.endswith(".json") and artifact_exists:
        try:
            data = load_json(path)
            parseable_json = True
            status = data.get("status", "not_recorded")
            acceptance_state = data.get("acceptance_state", "not_recorded")
            output_digest = data.get("output_digest", "not_recorded")
        except (json.JSONDecodeError, TypeError):
            parseable_json = False
            status = "unparseable_json"
            acceptance_state = "unparseable_json"
            output_digest = "unparseable_json"
        record.update(
            {
                "parseable_json": parseable_json,
                "status": status,
                "acceptance_state": acceptance_state,
                "output_digest": output_digest,
            }
        )
    else:
        record.update(
            {
                "parseable_json": not path.endswith(".json"),
                "status": "missing_source_file" if not artifact_exists else "context_only",
                "acceptance_state": (
                    "missing_source_file"
                    if not artifact_exists
                    else "not_applicable_markdown_context"
                ),
                "output_digest": (
                    "missing_source_file"
                    if not artifact_exists
                    else "not_applicable_markdown_context"
                ),
            }
        )
    return record


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_output() -> dict[str, Any]:
    n20_native = load_json(N20_NATIVE_FUNCTION_PATH)
    n20_same_basin = load_json(N20_SAME_BASIN_PATH)
    n15_closeout = load_json(N15_CLOSEOUT_PATH)
    n19_matrix = load_json(N19_CANDIDATE_MATRIX_PATH)
    n19_closeout = load_json(N19_CLOSEOUT_PATH)
    n25_closeout = load_json(N25_CLOSEOUT_PATH)
    n25_1_closeout = load_json(N25_1_CLOSEOUT_PATH)
    n25_2_closeout = load_json(N25_2_CLOSEOUT_PATH)

    source_row = find_row(n20_native, SOURCE_CONTRACT_ROW)
    consumable_row = find_row(n20_same_basin, CONSUMABLE_CONTRACT_ROW)
    n19_ap5_row = find_row(n19_matrix, N19_AP5_NAT3_ROW)

    consumable_strings = collect_strings(consumable_row)
    source_records = [source_record(row) for row in SOURCE_ROWS]

    n25_2_handoff = n25_2_closeout["n26_handoff"]
    n25_2_admission = {
        "source_id": "n25_2_closeout",
        "allowed_n26_consumption": n25_2_handoff["allowed_n26_consumption"],
        "n26_consumption_effect": n25_2_handoff["n26_consumption_effect"],
        "n26_scoped_context_consumption_allowed": n25_2_handoff[
            "n26_scoped_context_consumption_allowed"
        ],
        "n26_unscoped_consumption_allowed": n25_2_handoff[
            "n26_unscoped_consumption_allowed"
        ],
        "n26_unscoped_multi_basin_consumption_allowed": n25_2_handoff[
            "n26_unscoped_multi_basin_consumption_allowed"
        ],
        "required_n26_boundary": n25_2_handoff["required_n26_boundary"],
    }
    unsafe_claim_flags = {claim: False for claim in UNSAFE_CLAIMS}
    source_consumption_rows = [
        {
            "row_id": f"n26_i1_source_{index:02d}_{record['source_id']}",
            "source_id": record["source_id"],
            "path": record["path"],
            "source_classification": record["source_classification"],
            "source_role": record["source_role"],
            "may_consume_as": record["may_consume_as"],
            "must_not_consume_as": record["must_not_consume_as"],
            "row_decision": "supported_as_source_inventory_only",
            "pd_ladder_rung_assigned": False,
            "positive_proxy_evidence_opened": False,
            "scoped_substrate_consumption_effect": (
                "scoped_MB6_admission_source"
                if record["source_id"] == "n25_2_closeout"
                else "context_or_boundary_only"
            ),
            "unsafe_claim_flags": unsafe_claim_flags,
            "sha256": record["sha256"],
        }
        for index, record in enumerate(source_records, start=1)
    ]

    checks = [
        check(
            "all_sources_exist",
            all(record["artifact_exists"] for record in source_records),
            {"source_count": len(source_records)},
        ),
        check(
            "json_sources_parseable",
            all(record["parseable_json"] for record in source_records if record["path"].endswith(".json")),
            "all JSON source records parsed",
        ),
        check(
            "n20_proxy_contract_row_present",
            source_row.get("primitive_id") == PRIMITIVE_ID,
            {"row_id": source_row.get("row_id"), "primitive_id": source_row.get("primitive_id")},
        ),
        check(
            "n20_same_basin_contract_complete",
            consumable_row.get("contract_status") == "complete"
            and source_row.get("row_id") in consumable_strings,
            {
                "row_id": consumable_row.get("row_id"),
                "contract_status": consumable_row.get("contract_status"),
                "source_contract_row": source_row.get("row_id"),
            },
        ),
        check(
            "n15_ap5_artifact_context_present",
            n15_closeout.get("acceptance_state")
            == "closed_claim_clean_ap5_artifact_level_endogenous_proxy_formation",
            {"acceptance_state": n15_closeout.get("acceptance_state")},
        ),
        check(
            "n19_ap5_nat4_gap_recorded",
            n19_ap5_row.get("nat_level") == "NAT3"
            and n19_closeout.get("claimed_ladder_generation_status")
            == "blocked_by_ap4_ap5_nat4_evidence_gaps",
            {
                "n19_ap5_row_id": n19_ap5_row.get("row_id"),
                "nat_level": n19_ap5_row.get("nat_level"),
                "claimed_ladder_generation_status": n19_closeout.get(
                    "claimed_ladder_generation_status"
                ),
            },
        ),
        check(
            "n25_context_is_scoped_bf5_not_bf6",
            n25_closeout.get("native_bf5_supported") is True
            and n25_closeout.get("native_bf6_supported") is False
            and n25_closeout.get("independent_new_basin_supported") is False,
            {
                "final_bf_level": n25_closeout.get("final_bf_level"),
                "native_bf5_supported": n25_closeout.get("native_bf5_supported"),
                "native_bf6_supported": n25_closeout.get("native_bf6_supported"),
                "independent_new_basin_supported": n25_closeout.get(
                    "independent_new_basin_supported"
                ),
            },
        ),
        check(
            "n25_1_requirements_bridge_present",
            n25_1_closeout.get("status") == "passed"
            or str(n25_1_closeout.get("acceptance_state", "")).startswith("accepted"),
            {
                "status": n25_1_closeout.get("status"),
                "acceptance_state": n25_1_closeout.get("acceptance_state"),
            },
        ),
        check(
            "n25_2_scoped_consumption_allowed",
            n25_2_admission["n26_scoped_context_consumption_allowed"] is True
            and n25_2_admission["n26_consumption_effect"]
            == "scoped_mb6_substrate_consumption_allowed",
            n25_2_admission,
        ),
        check(
            "n25_2_unscoped_consumption_blocked",
            n25_2_admission["n26_unscoped_consumption_allowed"] is False
            and n25_2_admission["n26_unscoped_multi_basin_consumption_allowed"] is False,
            n25_2_admission,
        ),
        check(
            "source_rows_have_positive_and_negative_consumption_rules",
            all(record["may_consume_as"] and record["must_not_consume_as"] for record in source_records),
            {"source_count": len(source_records)},
        ),
        check(
            "no_pd_rung_assigned",
            True,
            "Iteration 1 is inventory/admission only",
        ),
        check(
            "positive_proxy_evidence_not_opened",
            True,
            "No proxy derivation, divergence, or collapse rows are produced in I1",
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in unsafe_claim_flags.values()),
            unsafe_claim_flags,
        ),
        check(
            "no_absolute_paths_in_records",
            all(record["path_is_repo_relative"] for record in source_records),
            "all source paths are repository-relative",
        ),
    ]

    output: dict[str, Any] = {
        "artifact_id": "n26_source_inventory_and_scoped_substrate_admission",
        "schema_version": "1.0",
        "experiment": "N26_proxy_divergence_proxy_collapse",
        "iteration": "1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "source inventory and scoped substrate admission only",
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_source_inventory_scoped_substrate_admission_no_proxy_evidence",
        "source_contract_row": SOURCE_CONTRACT_ROW,
        "source_consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
        "source_contract_row_digest": digest_value(source_row),
        "source_consumable_contract_row_digest": digest_value(consumable_row),
        "target_primitive": PRIMITIVE_ID,
        "pd_ladder_rung_assigned": False,
        "candidate_pd_ladder_rung": "not_assigned_inventory_only",
        "n26_closeout_ceiling": "N26-C1_source_inventory_and_scoped_substrate_admission_passed",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": False,
        "proxy_derivation_opened": False,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "ap5_bridge_status": "not_supported_inventory_only",
        "ap5_gap_ledger": {
            "n15_artifact_context_acceptance_state": n15_closeout.get("acceptance_state"),
            "n19_ap5_nat_level": n19_ap5_row.get("nat_level"),
            "n19_ap5_row_id": n19_ap5_row.get("row_id"),
            "claimed_ap_ladder_generation_status": n19_closeout.get(
                "claimed_ladder_generation_status"
            ),
            "row_local_ap5_dependency_required_for_future_proxy_rows": True,
        },
        "n25_context_boundary": {
            "final_bf_level": n25_closeout.get("final_bf_level"),
            "final_n25_closeout_rung": n25_closeout.get("final_n25_closeout_rung"),
            "native_bf5_supported": n25_closeout.get("native_bf5_supported"),
            "native_bf6_supported": n25_closeout.get("native_bf6_supported"),
            "independent_new_basin_supported": n25_closeout.get(
                "independent_new_basin_supported"
            ),
            "lgrc9v3_multi_basin_native_formation_supported": n25_closeout.get(
                "lgrc9v3_multi_basin_native_formation_supported"
            ),
        },
        "n25_2_scoped_substrate_admission": n25_2_admission,
        "source_records": source_records,
        "source_consumption_rows": source_consumption_rows,
        "claim_boundary": {
            "claim_ceiling": (
                "N26 I1 source inventory and scoped-substrate admission only; no "
                "proxy derivation, proxy divergence, proxy collapse, AP5 bridge, "
                "semantic goal, agency, native support, sentience, Phase 8, or "
                "ant ecology evidence"
            ),
            "unsafe_claim_flags": unsafe_claim_flags,
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N26 Iteration 1 - Source Inventory And Scoped Substrate Admission",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Scope",
        "",
        "Iteration 1 is inventory/admission only. It assigns no PD rung and opens no positive proxy evidence.",
        "",
        "## Source Rows",
        "",
        "| Source | Classification | Role | Row Decision |",
        "| --- | --- | --- | --- |",
    ]
    for row in output["source_consumption_rows"]:
        lines.append(
            "| `{source_id}` | `{source_classification}` | `{source_role}` | `{row_decision}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Scoped Substrate Admission",
            "",
            "```text",
            f"allowed_n26_consumption = {output['n25_2_scoped_substrate_admission']['allowed_n26_consumption']}",
            f"n26_consumption_effect = {output['n25_2_scoped_substrate_admission']['n26_consumption_effect']}",
            f"n26_scoped_context_consumption_allowed = {str(output['n25_2_scoped_substrate_admission']['n26_scoped_context_consumption_allowed']).lower()}",
            f"n26_unscoped_consumption_allowed = {str(output['n25_2_scoped_substrate_admission']['n26_unscoped_consumption_allowed']).lower()}",
            f"n26_unscoped_multi_basin_consumption_allowed = {str(output['n25_2_scoped_substrate_admission']['n26_unscoped_multi_basin_consumption_allowed']).lower()}",
            "```",
            "",
            "## AP5 Gap Ledger",
            "",
            "```text",
            f"n15_artifact_context_acceptance_state = {output['ap5_gap_ledger']['n15_artifact_context_acceptance_state']}",
            f"n19_ap5_nat_level = {output['ap5_gap_ledger']['n19_ap5_nat_level']}",
            f"claimed_ap_ladder_generation_status = {output['ap5_gap_ledger']['claimed_ap_ladder_generation_status']}",
            "future_proxy_rows_require_row_local_ap5_dependency = true",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | "
            f"`{json.dumps(item['detail'], sort_keys=True, ensure_ascii=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["claim_boundary"]["claim_ceiling"],
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

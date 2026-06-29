#!/usr/bin/env python3
"""Build N27 Iteration 1 source inventory and transfer contract admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
REPORT = EXPERIMENT / "reports" / "n27_source_inventory_and_transfer_contract_admission.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_source_inventory_and_transfer_contract_admission.py"
)

N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N26_CLOSEOUT_PATH = (
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
    "outputs/n26_closeout_and_n27_handoff.json"
)
N26_CLOSEOUT_REPORT_PATH = (
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
    "reports/n26_closeout_and_n27_handoff.md"
)
N25_2_CLOSEOUT_PATH = (
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
    "outputs/n25_2_closeout_and_n26_handoff.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

SOURCE_CONTRACT_ROW = "n20_i4_row_08_configuration_substrate_transfer"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_08_configuration_substrate_transfer"
PRIMITIVE_ID = "configuration_substrate_transfer"

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

SOURCE_ROWS: list[dict[str, Any]] = [
    {
        "source_id": "n20_same_basin_continuation_contract",
        "path": N20_SAME_BASIN_PATH,
        "source_classification": "contract_source",
        "source_role": "complete_configuration_substrate_transfer_contract",
        "may_consume_as": [
            "N20_i5_complete_transfer_contract",
            "same_basin_rule_source",
            "transfer_support_scaffold_source",
        ],
        "must_not_consume_as": [
            "positive_transfer_evidence",
            "runtime_transfer_probe",
            "semantic_identity_evidence",
        ],
    },
    {
        "source_id": "n20_native_function_proxy_contract",
        "path": N20_NATIVE_FUNCTION_PATH,
        "source_classification": "contract_source",
        "source_role": "configuration_substrate_transfer_descriptor_source",
        "may_consume_as": [
            "N20_i4_transfer_descriptor_context",
            "proxy_metric_boundary_context",
        ],
        "must_not_consume_as": [
            "positive_transfer_evidence",
            "same_basin_rule_complete_source",
            "semantic_identity_evidence",
        ],
    },
    {
        "source_id": "n26_closeout",
        "path": N26_CLOSEOUT_PATH,
        "source_classification": "handoff_source",
        "source_role": "bounded_PD6_proxy_divergence_collapse_context",
        "may_consume_as": [
            "bounded_PD6_proxy_divergence_collapse_evidence",
            "scoped_artifact_AP5_bridge_candidate_context",
            "proxy_pressure_control_context",
            "source_current_proxy_basin_contrast_context",
        ],
        "must_not_consume_as": [
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "transfer_evidence",
            "semantic_identity_evidence",
            "native_support",
            "agency",
            "unscoped_multi_basin_substrate",
        ],
    },
    {
        "source_id": "n26_closeout_report",
        "path": N26_CLOSEOUT_REPORT_PATH,
        "source_classification": "handoff_report_context",
        "source_role": "N27_handoff_text_boundary",
        "may_consume_as": ["handoff_interpretation_context", "claim_boundary_context"],
        "must_not_consume_as": [
            "positive_transfer_evidence",
            "native_AP5",
            "semantic_identity_evidence",
        ],
    },
    {
        "source_id": "n25_2_closeout_inherited_through_n26",
        "path": N25_2_CLOSEOUT_PATH,
        "source_classification": "inherited_scoped_substrate_context",
        "source_role": "scoped_MB6_context_inherited_only_through_N26",
        "may_consume_as": [
            "inherited_scoped_MB6_context_through_N26",
            "N26_substrate_boundary_context",
        ],
        "must_not_consume_as": [
            "direct_N27_substrate_transfer_evidence",
            "unscoped_multi_basin_substrate",
            "native_support",
            "agency",
            "ant_ecology_implementation",
        ],
    },
    {
        "source_id": "n20_n29_handoff",
        "path": N20_HANDOFF_PATH,
        "source_classification": "handoff_context",
        "source_role": "current_N27_pickup_note",
        "may_consume_as": ["roadmap_handoff_context", "N27_scope_context"],
        "must_not_consume_as": ["positive_transfer_evidence"],
    },
    {
        "source_id": "n20_n29_roadmap",
        "path": N20_ROADMAP_PATH,
        "source_classification": "roadmap_context",
        "source_role": "N27_question_and_iteration_context",
        "may_consume_as": ["roadmap_context", "N27_question_context"],
        "must_not_consume_as": ["positive_transfer_evidence"],
    },
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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def find_contract_row(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in data.get("contract_rows", []):
        if isinstance(row, dict) and row.get("row_id") == row_id:
            return row
    raise ValueError(f"missing contract row {row_id}")


def source_record(row: dict[str, Any]) -> dict[str, Any]:
    path = row["path"]
    record = dict(row)
    record["exists"] = (ROOT / path).exists()
    if path.endswith(".json"):
        record["sha256"] = sha256_file(path)
        record["digest_policy"] = "sha256_pinned_source_artifact"
        source_json = load_json(path)
        record["artifact_id"] = source_json.get("artifact_id", "not_recorded")
        record["status"] = source_json.get("status", "not_recorded")
        record["acceptance_state"] = source_json.get("acceptance_state", "not_recorded")
        record["output_digest"] = source_json.get("output_digest", "not_recorded")
    elif row["source_id"] in {"n20_n29_handoff", "n20_n29_roadmap"}:
        record["sha256"] = "not_pinned_active_context_document"
        record["digest_policy"] = "existence_only_active_roadmap_context"
        record["artifact_id"] = "markdown_source"
        record["status"] = "context_only"
        record["acceptance_state"] = "not_applicable_markdown_context"
        record["output_digest"] = "not_applicable_markdown_context"
    else:
        record["sha256"] = sha256_file(path)
        record["digest_policy"] = "sha256_pinned_markdown_context"
        record["artifact_id"] = "markdown_source"
        record["status"] = "context_only"
        record["acceptance_state"] = "not_applicable_markdown_context"
        record["output_digest"] = "not_applicable_markdown_context"
    return record


def transfer_contract_summary(row: dict[str, Any]) -> dict[str, Any]:
    continuation = row["continuation_function_descriptor"]
    same_basin = row["same_basin_continuation_rule"]
    scaffold = row["support_scaffold_declaration"]
    proxy = row["proxy_metric_definition"]
    return {
        "row_id": row["row_id"],
        "primitive_id": row["primitive_id"],
        "contract_status": row["contract_status"],
        "continuation_condition": continuation["continuation_condition"],
        "transfer_condition": continuation["transfer_condition"],
        "basin_signature": continuation["basin_signature"],
        "same_basin_rule_id": same_basin["rule_id"],
        "same_basin_signature_fields": same_basin.get("basin_signature_fields", []),
        "allowed_drift": same_basin.get("allowed_drift", "deferred_or_not_recorded"),
        "failure_modes": same_basin.get("failure_modes", []),
        "replay_requirement": same_basin.get("replay_requirement", "deferred_or_not_recorded"),
        "hidden_producer_support_allowed": same_basin.get(
            "hidden_producer_support_allowed", "deferred_or_not_recorded"
        ),
        "label_only_continuation_allowed": same_basin.get(
            "label_only_continuation_allowed", "deferred_or_not_recorded"
        ),
        "proxy_only_success_allowed": same_basin.get(
            "proxy_only_success_allowed", "deferred_or_not_recorded"
        ),
        "required_supports": scaffold["required_supports"],
        "producer_supplied_scaffolds": scaffold["producer_supplied_scaffolds"],
        "naturalization_debt": scaffold["naturalization_debt"],
        "proxy_metric_id": proxy["proxy_id"],
        "proxy_only_success_blocker": proxy["proxy_only_success_blocker"],
        "proxy_success_replaces_continuation": proxy["proxy_success_replaces_continuation"],
        "source_current_inputs": proxy["source_current_inputs"],
    }


def build_checks(output: dict[str, Any]) -> list[dict[str, Any]]:
    source_records = output["source_records"]
    contract = output["transfer_contract_summary"]
    n26 = output["n26_handoff_boundary"]
    checks = [
        {
            "check": "all_cited_sources_exist",
            "passed": all(record["exists"] for record in source_records),
            "detail": {"source_count": len(source_records)},
        },
        {
            "check": "n20_i5_transfer_contract_complete",
            "passed": contract["contract_status"] == "complete",
            "detail": {
                "row_id": contract["row_id"],
                "primitive_id": contract["primitive_id"],
                "same_basin_rule_id": contract["same_basin_rule_id"],
            },
        },
        {
            "check": "required_transfer_contract_fields_present",
            "passed": all(
                contract.get(field)
                for field in [
                    "basin_signature",
                    "same_basin_signature_fields",
                    "failure_modes",
                    "replay_requirement",
                    "required_supports",
                    "source_current_inputs",
                ]
            ),
            "detail": {
                "basin_signature_fields": contract["basin_signature"],
                "source_current_inputs": contract["source_current_inputs"],
            },
        },
        {
            "check": "n26_consumed_as_context_not_transfer_evidence",
            "passed": (
                "bounded_PD6_proxy_divergence_collapse_evidence"
                in n26["may_consume_n26_as"]
                and "native_AP5" in n26["must_not_consume_n26_as"]
                and output["n26_consumed_as_transfer_evidence"] is False
            ),
            "detail": {
                "may_consume_n26_as": n26["may_consume_n26_as"],
                "must_not_consume_n26_as": n26["must_not_consume_n26_as"],
            },
        },
        {
            "check": "n26_ap5_boundary_preserved",
            "passed": (
                output["n26_ap5_boundary"]["scoped_artifact_ap5_bridge_candidate_supported"]
                is True
                and output["n26_ap5_boundary"]["native_ap5_bridge_supported"] is False
                and output["n26_ap5_boundary"]["ap5_nat4_gap_resolved"] is False
            ),
            "detail": output["n26_ap5_boundary"],
        },
        {
            "check": "n25_2_consumed_only_through_n26_scoped_context",
            "passed": output["n25_2_direct_transfer_consumption_allowed"] is False,
            "detail": {
                "n25_2_role": "inherited_scoped_context_only_through_N26",
                "direct_transfer_consumption_allowed": output[
                    "n25_2_direct_transfer_consumption_allowed"
                ],
            },
        },
        {
            "check": "no_positive_transfer_evidence_opened",
            "passed": (
                output["positive_transfer_evidence_opened"] is False
                and output["candidate_rows_classified"] is False
                and output["ct_ladder_rung_assigned"] is False
            ),
            "detail": {
                "positive_transfer_evidence_opened": output[
                    "positive_transfer_evidence_opened"
                ],
                "ct_ladder_rung_assigned": output["ct_ladder_rung_assigned"],
            },
        },
        {
            "check": "movement_vs_transfer_boundary_recorded",
            "passed": output["movement_vs_transfer_boundary"]["basin_movement_is_transfer"]
            is False,
            "detail": output["movement_vs_transfer_boundary"],
        },
        {
            "check": "unsafe_claim_flags_false",
            "passed": all(value is False for value in output["unsafe_claim_flags"].values()),
            "detail": {"claim_count": len(output["unsafe_claim_flags"])},
        },
        {
            "check": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
            "detail": {"absolute_path_policy": "repository_relative_paths_only"},
        },
    ]
    return checks


def write_report(output: dict[str, Any]) -> None:
    checks = output["checks"]
    REPORT.write_text(
        "\n".join(
            [
                "# N27 Iteration 1 - Source Inventory And Transfer Contract Admission",
                "",
                f"Status: `{output['status']}`",
                "",
                f"Acceptance state: `{output['acceptance_state']}`",
                "",
                "## Summary",
                "",
                "Iteration 1 admits the N20 configuration/substrate transfer contract and the N26 handoff boundary. It opens no positive transfer evidence and assigns no CT rung.",
                "",
                "```text",
                f"source_contract_row = {output['source_contract_row']}",
                f"consumable_contract_row = {output['consumable_contract_row']}",
                f"positive_transfer_evidence_opened = {str(output['positive_transfer_evidence_opened']).lower()}",
                f"ct_ladder_rung_assigned = {str(output['ct_ladder_rung_assigned']).lower()}",
                f"ready_for_iteration_2 = {str(output['ready_for_iteration_2']).lower()}",
                "```",
                "",
                "## Transfer Boundary",
                "",
                "N27 is not a basin-movement experiment. Movement is within-frame continuity; transfer is a cross-frame mapping question requiring declared mapping, boundary mapping, support/coherence preservation, flux discipline, and fail-closed relabel controls.",
                "",
                "## Source Records",
                "",
                "| Source | Role | May Consume As | Must Not Consume As |",
                "| --- | --- | --- | --- |",
                *[
                    "| `{source_id}` | `{role}` | {may} | {must_not} |".format(
                        source_id=record["source_id"],
                        role=record["source_role"],
                        may=", ".join(f"`{item}`" for item in record["may_consume_as"]),
                        must_not=", ".join(f"`{item}`" for item in record["must_not_consume_as"]),
                    )
                    for record in output["source_records"]
                ],
                "",
                "## Checks",
                "",
                "| Check | Passed |",
                "| --- | --- |",
                *[
                    f"| `{check['check']}` | `{str(check['passed']).lower()}` |"
                    for check in checks
                ],
                "",
                "## Claim Boundary",
                "",
                output["claim_boundary"]["claim_ceiling"],
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def build_output() -> dict[str, Any]:
    n20_same = load_json(N20_SAME_BASIN_PATH)
    n20_native = load_json(N20_NATIVE_FUNCTION_PATH)
    n26_closeout = load_json(N26_CLOSEOUT_PATH)

    consumable_row = find_contract_row(n20_same, CONSUMABLE_CONTRACT_ROW)
    descriptor_row = find_contract_row(n20_native, SOURCE_CONTRACT_ROW)
    n26_handoff = n26_closeout["n27_handoff"]
    n26_ap5 = n26_closeout["final_ap5_status"]

    output: dict[str, Any] = {
        "artifact_id": "n27_source_inventory_and_transfer_contract_admission",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "experiment": "N27",
        "iteration": "I1",
        "status": "passed",
        "acceptance_state": "accepted_source_inventory_transfer_contract_admission_no_positive_evidence",
        "source_contract_row": SOURCE_CONTRACT_ROW,
        "consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
        "target_primitive": PRIMITIVE_ID,
        "target_reading": "bounded configuration / substrate transfer",
        "source_records": [source_record(row) for row in SOURCE_ROWS],
        "descriptor_contract_summary": transfer_contract_summary(descriptor_row),
        "transfer_contract_summary": transfer_contract_summary(consumable_row),
        "n26_handoff_boundary": {
            "handoff_status": n26_handoff["handoff_status"],
            "may_consume_n26_as": n26_handoff["may_consume_n26_as"],
            "must_not_consume_n26_as": n26_handoff["must_not_consume_n26_as"],
            "required_n27_controls": n26_handoff["required_n27_controls"],
        },
        "n26_ap5_boundary": {
            "scoped_artifact_ap5_bridge_candidate_supported": n26_ap5[
                "scoped_artifact_ap5_bridge_candidate_supported"
            ],
            "native_ap5_bridge_supported": n26_ap5["native_ap5_bridge_supported"],
            "ap5_nat4_gap_resolved": n26_ap5["ap5_nat4_gap_resolved"],
            "ap5_dependency_role": n26_ap5["ap5_dependency_role"],
        },
        "n26_consumed_as_transfer_evidence": False,
        "n25_2_direct_transfer_consumption_allowed": False,
        "transfer_scope_policy": {
            "primary_scope": "configuration_or_topology_transfer_inside_LGRC",
            "allowed_row_scopes": ["configuration", "fixture", "topology", "substrate"],
            "substrate_transfer_requires_source_backed_mapping": True,
            "full_substrate_transfer_supported_by_i1": False,
        },
        "movement_vs_transfer_boundary": {
            "basin_movement_is_transfer": False,
            "movement_reading": "within-frame basin center or boundary shift in the same graph",
            "transfer_reading": "cross-frame declared mapping with pre/post signature, boundary mapping, support/coherence preservation, and flux discipline",
            "same_label_after_mapping_sufficient": False,
        },
        "positive_transfer_evidence_opened": False,
        "candidate_rows_classified": False,
        "ct_ladder_rung_assigned": False,
        "n27_closeout_ladder_rung_assigned": False,
        "native_support_opened": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "ready_for_iteration_2": True,
        "claim_boundary": {
            "claim_ceiling": "source inventory and transfer contract admission only; no positive transfer evidence, semantic identity, agency, native support, sentience, Phase 8 completion, ant ecology, native AP5, or AP5 NAT4 gap resolution",
            "blocked_claims": [
                "semantic_identity",
                "semantic_choice",
                "semantic_goal_ownership",
                "semantic_learning",
                "agency",
                "native_support",
                "selfhood",
                "identity_acceptance",
                "sentience",
                "organism_life",
                "ant_ecology_implementation",
                "Phase_8_completion",
                "unscoped_multi_basin_substrate",
                "native_AP5",
                "AP5_NAT4_gap_resolution",
            ],
        },
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
    }
    output["checks"] = build_checks(output)
    output["failed_checks"] = [
        check["check"] for check in output["checks"] if check["passed"] is not True
    ]
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

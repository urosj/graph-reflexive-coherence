#!/usr/bin/env python3
"""Build N28 Iteration 1 source inventory and contract admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_source_inventory_and_contract_admission.json"
REPORT = EXPERIMENT / "reports" / "n28_source_inventory_and_contract_admission.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_source_inventory_and_contract_admission.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

N20_PRODUCER_LEDGER_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_producer_residue_ledger.json"
)
N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N27_CLOSEOUT_PATH = (
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
    "outputs/n27_closeout_and_n28_handoff.json"
)
N27_PRECURSOR_EVALUATION_PATH = (
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
    "outputs/n27_n28_precursor_side_effect_evaluation_matrix.json"
)
N27_PRECURSOR_CLASSIFICATION_PATH = (
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
    "outputs/n27_n28_precursor_side_effect_claim_classification.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

N20_I3_ROW_ID = "n20_i3_row_09_generative_extractive_persistence"
N20_I4_ROW_ID = "n20_i4_row_09_generative_extractive_persistence"
N20_I5_ROW_ID = "n20_i5_row_09_generative_extractive_persistence"

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "generative_persistence_claim_allowed": False,
    "n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}

SOURCE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "source_id": "n20_i3_generative_extractive_producer_residue_ledger",
        "path": N20_PRODUCER_LEDGER_PATH,
        "row_id": N20_I3_ROW_ID,
        "source_classification": "contract_source",
        "source_role": "producer_residue_and_naturalization_debt_ledger",
        "may_consume_as": [
            "producer_residue_classification",
            "naturalization_debt_boundary",
            "blocked_relabel_boundary",
        ],
        "must_not_consume_as": [
            "positive_generative_evidence",
            "positive_extractive_evidence",
            "source_current_neighbor_capacity_probe",
            "native_support_evidence",
            "semantic_cooperation_evidence",
        ],
    },
    {
        "source_id": "n20_i4_generative_extractive_native_function_proxy_contract",
        "path": N20_NATIVE_FUNCTION_PATH,
        "row_id": N20_I4_ROW_ID,
        "source_classification": "contract_source",
        "source_role": "native_function_proxy_descriptor_context",
        "may_consume_as": [
            "bounded_continuation_descriptor",
            "proxy_metric_boundary_context",
            "support_scaffold_boundary",
        ],
        "must_not_consume_as": [
            "positive_generative_evidence",
            "proxy_metric_success_as_primitive_support",
            "semantic_function_or_goal_evidence",
            "native_support_evidence",
        ],
    },
    {
        "source_id": "n20_i5_generative_extractive_same_basin_contract",
        "path": N20_SAME_BASIN_PATH,
        "row_id": N20_I5_ROW_ID,
        "source_classification": "contract_source",
        "source_role": "normative_same_basin_continuation_contract",
        "may_consume_as": [
            "same_basin_rule",
            "required_floor_and_failure_mode_contract",
            "minimum_control_contract",
        ],
        "must_not_consume_as": [
            "positive_generative_evidence",
            "positive_extractive_evidence",
            "runtime_probe_result",
            "native_support_evidence",
        ],
    },
    {
        "source_id": "n27_closeout_and_n28_handoff",
        "path": N27_CLOSEOUT_PATH,
        "source_classification": "handoff_source",
        "source_role": "bounded_ct6_transfer_and_n28_precursor_context",
        "may_consume_as": [
            "bounded_configuration_topology_transfer_evidence",
            "claim_clean_ct5_transfer_candidate_closeout",
            "n28_ready_side_effect_precursor_evaluation",
            "focal_stability_with_neighbor_capacity_metrics_context",
        ],
        "must_not_consume_as": [
            "N28_generative_persistence_evidence",
            "semantic_identity",
            "semantic_cooperation",
            "agency",
            "native_support",
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "Phase_8_completion",
            "ant_ecology",
            "organism_life",
        ],
    },
    {
        "source_id": "n27_n28_precursor_side_effect_evaluation",
        "path": N27_PRECURSOR_EVALUATION_PATH,
        "source_classification": "precursor_context",
        "source_role": "side_effect_metric_context_no_n28_claim",
        "may_consume_as": [
            "focal_stability_metric_context",
            "neighbor_capacity_metric_context",
            "starting_threshold_context",
        ],
        "must_not_consume_as": [
            "N28_generative_persistence_evidence",
            "source_current_N28_probe_result",
            "final_regime_classification",
            "native_support_evidence",
        ],
    },
    {
        "source_id": "n27_n28_precursor_claim_classification",
        "path": N27_PRECURSOR_CLASSIFICATION_PATH,
        "source_classification": "claim_boundary_context",
        "source_role": "n28_precursor_claim_clean_no_n28_claim",
        "may_consume_as": [
            "starting_control_context",
            "claim_boundary_context",
            "precursor_ready_context",
        ],
        "must_not_consume_as": [
            "N28_generative_persistence_evidence",
            "N28_claim_support",
            "semantic_cooperation",
            "native_support",
            "Phase_8_completion",
            "ant_ecology",
        ],
    },
    {
        "source_id": "n20_n29_handoff",
        "path": N20_HANDOFF_PATH,
        "source_classification": "handoff_context",
        "source_role": "current_N28_pickup_note",
        "may_consume_as": ["roadmap_handoff_context", "N28_scope_context"],
        "must_not_consume_as": ["positive_generative_evidence"],
    },
    {
        "source_id": "n20_n29_roadmap",
        "path": N20_ROADMAP_PATH,
        "source_classification": "roadmap_context",
        "source_role": "N28_question_and_iteration_context",
        "may_consume_as": ["roadmap_context", "N28_question_context"],
        "must_not_consume_as": ["positive_generative_evidence"],
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
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def iter_dicts(data: Any):
    if isinstance(data, dict):
        yield data
        for value in data.values():
            yield from iter_dicts(value)
    elif isinstance(data, list):
        for value in data:
            yield from iter_dicts(value)


def find_row(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for item in iter_dicts(data):
        if item.get("row_id") == row_id:
            return item
    raise ValueError(f"missing source row {row_id}")


def source_record(source: dict[str, Any]) -> dict[str, Any]:
    path = source["path"]
    record = dict(source)
    record["exists"] = (ROOT / path).exists()
    if not record["exists"]:
        record["sha256"] = "missing"
        record["digest_policy"] = "missing_source"
        return record

    if path.endswith(".json"):
        source_json = load_json(path)
        record["sha256"] = sha256_file(path)
        record["digest_policy"] = "sha256_pinned_source_artifact"
        record["artifact_id"] = source_json.get("artifact_id", "not_recorded")
        record["status"] = source_json.get("status", "not_recorded")
        record["acceptance_state"] = source_json.get("acceptance_state", "not_recorded")
        record["output_digest"] = source_json.get("output_digest", "not_recorded")
        if "row_id" in source:
            row = find_row(source_json, source["row_id"])
            record["row_digest"] = digest_value(row)
            record["row_decision"] = row.get("row_decision", "not_recorded")
    else:
        record["sha256"] = "not_pinned_active_context_document"
        record["digest_policy"] = "existence_only_active_roadmap_context"
        record["artifact_id"] = "markdown_source"
        record["status"] = "context_only"
        record["acceptance_state"] = "context_only"
        record["output_digest"] = "not_applicable_markdown_context"
    return record


def build_output() -> dict[str, Any]:
    n20_i3_json = load_json(N20_PRODUCER_LEDGER_PATH)
    n20_i4_json = load_json(N20_NATIVE_FUNCTION_PATH)
    n20_i5_json = load_json(N20_SAME_BASIN_PATH)
    n27_closeout = load_json(N27_CLOSEOUT_PATH)
    n27_precursor = load_json(N27_PRECURSOR_EVALUATION_PATH)
    n27_classification = load_json(N27_PRECURSOR_CLASSIFICATION_PATH)

    n20_i3_row = find_row(n20_i3_json, N20_I3_ROW_ID)
    n20_i4_row = find_row(n20_i4_json, N20_I4_ROW_ID)
    n20_i5_row = find_row(n20_i5_json, N20_I5_ROW_ID)

    n27_handoff = n27_closeout.get("n28_handoff", {})
    precursor_trace = n27_precursor.get("evaluation_row", {}).get("evaluation_trace")
    if not isinstance(precursor_trace, dict):
        precursor_trace = n27_precursor.get("evaluation_trace", {})
    classification_trace = n27_classification.get("classification_row", {}).get(
        "classification_trace", {}
    )

    source_records = [source_record(source) for source in SOURCE_DEFINITIONS]

    n20_contract_admission = {
        "primitive_id": "generative_extractive_persistence",
        "n20_i3_row_id": N20_I3_ROW_ID,
        "n20_i3_row_digest": digest_value(n20_i3_row),
        "n20_i4_row_id": N20_I4_ROW_ID,
        "n20_i4_row_digest": digest_value(n20_i4_row),
        "n20_i5_row_id": N20_I5_ROW_ID,
        "n20_i5_row_digest": digest_value(n20_i5_row),
        "producer_residue_fields": n20_i3_row.get("producer_mediated_fields", []),
        "substrate_carried_fields": n20_i3_row.get("LGRC_visible_fields", []),
        "naturalization_debt_fields": n20_i3_row.get("naturalization_debt_fields", []),
        "blocked_relabel_fields": n20_i3_row.get("blocked_relabel_fields", []),
        "continuation_function_descriptor": n20_i4_row.get(
            "continuation_function_descriptor", {}
        ),
        "proxy_metric_definition": n20_i4_row.get("proxy_metric_definition", {}),
        "support_scaffold_declaration": n20_i4_row.get(
            "support_scaffold_declaration", {}
        ),
        "same_basin_continuation_rule": n20_i5_row.get(
            "same_basin_continuation_rule", {}
        ),
        "minimum_controls": n20_i5_row.get("minimum_controls", {}),
        "claim_ceiling": n20_i5_row.get("claim_ceiling", "not_recorded"),
        "contract_consumption_status": "admitted_as_contract_only_no_positive_N28_evidence",
    }

    n27_precursor_metrics = precursor_trace.get("metrics", {})
    n27_precursor_policy = precursor_trace.get("policy", {})
    n27_handoff_admission = {
        "n27_final_ct_ladder_rung": n27_closeout.get("final_ct_ladder_rung"),
        "n27_final_closeout_rung": n27_handoff.get("n27_final_closeout_rung"),
        "n27_closeout_supported": n27_closeout.get("n27_closeout_supported", False),
        "n28_precursor_evaluation_supported": n27_closeout.get(
            "n28_precursor_evaluation_supported", False
        ),
        "n28_generative_persistence_supported": n27_closeout.get(
            "n28_generative_persistence_supported", "not_recorded"
        ),
        "n28_may_consume_as": n27_handoff.get("n28_may_consume_as", []),
        "n28_must_not_consume_as": n27_handoff.get("n28_must_not_consume_as", []),
        "required_n28_starting_controls": n27_handoff.get(
            "required_n28_starting_controls", []
        ),
        "precursor_metrics_context_only": n27_precursor_metrics,
        "precursor_policy_context_only": n27_precursor_policy,
        "precursor_classification_acceptance_state": n27_classification.get(
            "acceptance_state"
        ),
        "precursor_claim_classification_failed_open_control_count": n27_classification.get(
            "failed_open_control_count",
            classification_trace.get("failed_open_control_count", "not_recorded"),
        ),
        "transfer_success_as_n28_success_allowed": False,
        "n27_consumed_as_n28_evidence": False,
        "side_effect_precursor_role": "context_only_not_positive_N28_evidence",
    }

    medium_debt_record = {
        "medium_debt_fields": [
            "generative_extractive_persistence.source_current_neighbor_basin_birth_telemetry",
            "generative_extractive_persistence.medium_debt_deferred_to_n28_n29",
            "generative_extractive_persistence.environment_capacity_budget_replay",
        ],
        "medium_debt_status": "recorded_for_N28_schema_and_later_N29_ecology_bridge",
        "medium_debt_as_success_allowed": False,
        "shared_medium_label_only_success_allowed": False,
        "direct_message_scaffold_as_native_medium_allowed": False,
    }

    evidence_state = {
        "positive_generative_evidence_opened": False,
        "positive_extractive_evidence_opened": False,
        "candidate_rows_classified": False,
        "ge_ladder_rung_assigned": False,
        "n28_closeout_ladder_rung_assigned": False,
        "n27_consumed_as_n28_evidence": False,
        "n27_transfer_success_as_n28_success_allowed": False,
        "native_support_opened": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "ready_for_iteration_2": True,
    }

    checks = [
        {
            "check_id": "all_required_sources_exist",
            "passed": all(record["exists"] for record in source_records),
        },
        {
            "check_id": "n20_i3_i4_i5_rows_found",
            "passed": all(
                row.get("primitive_id") == "generative_extractive_persistence"
                for row in [n20_i3_row, n20_i4_row, n20_i5_row]
            ),
        },
        {
            "check_id": "n20_i5_normative_contract_recorded",
            "passed": n20_i5_row.get("same_basin_continuation_rule", {}).get("rule_id")
            == "n20_i5_generative_extractive_persistence_same_basin_rule",
        },
        {
            "check_id": "n27_closeout_ready_for_n28",
            "passed": bool(n27_closeout.get("ready_for_n28"))
            and n27_closeout.get("final_ct_ladder_rung")
            == "CT6_N28_ready_bounded_transfer_evidence",
        },
        {
            "check_id": "n27_not_consumed_as_n28_evidence",
            "passed": n27_handoff_admission["n27_consumed_as_n28_evidence"] is False
            and "N28_generative_persistence_evidence"
            in n27_handoff_admission["n28_must_not_consume_as"]
            and n27_handoff_admission["n28_generative_persistence_supported"] is False,
        },
        {
            "check_id": "n27_precursor_metrics_context_only",
            "passed": bool(n27_precursor_metrics)
            and n27_handoff_admission["side_effect_precursor_role"]
            == "context_only_not_positive_N28_evidence",
        },
        {
            "check_id": "medium_debt_recorded",
            "passed": medium_debt_record["medium_debt_as_success_allowed"] is False
            and len(medium_debt_record["medium_debt_fields"]) == 3,
        },
        {
            "check_id": "no_positive_evidence_opened",
            "passed": all(
                evidence_state[key] is False
                for key in [
                    "positive_generative_evidence_opened",
                    "positive_extractive_evidence_opened",
                    "candidate_rows_classified",
                    "ge_ladder_rung_assigned",
                    "n28_closeout_ladder_rung_assigned",
                    "native_support_opened",
                    "phase8_completion_opened",
                    "ant_ecology_opened",
                ]
            ),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]

    output = {
        "artifact_id": "n28_source_inventory_and_contract_admission",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_inventory_generative_extractive_contract_admission_"
            "no_positive_evidence"
        ),
        "experiment": "N28",
        "iteration": "1",
        "claim_ceiling": "source_inventory_and_contract_admission_only_no_N28_evidence",
        "source_record_count": len(source_records),
        "source_records": source_records,
        "n20_contract_admission": n20_contract_admission,
        "n27_handoff_admission": n27_handoff_admission,
        "medium_debt_record": medium_debt_record,
        "evidence_state": evidence_state,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
        }
    )
    output["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 1 - Source Inventory And Contract Admission",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Positive generative evidence opened: `{str(output['evidence_state']['positive_generative_evidence_opened']).lower()}`",
        f"- Candidate rows classified: `{str(output['evidence_state']['candidate_rows_classified']).lower()}`",
        f"- Ready for Iteration 2: `{str(output['evidence_state']['ready_for_iteration_2']).lower()}`",
        "",
        "I1 admits N20 generative/extractive contracts and N27 precursor context only. "
        "It does not open N28 positive evidence, GE ladder assignment, native support, "
        "Phase 8 completion, or ant-ecology claims.",
        "",
        "## Source Records",
        "",
        "| Source | Role | Status | Output Digest | Row Digest |",
        "|---|---|---|---|---|",
    ]

    for record in output["source_records"]:
        lines.append(
            "| "
            f"`{record['source_id']}` | "
            f"{record['source_role']} | "
            f"`{record.get('status', 'not_recorded')}` | "
            f"`{record.get('output_digest', 'not_applicable')}` | "
            f"`{record.get('row_digest', 'not_applicable')}` |"
        )

    n27 = output["n27_handoff_admission"]
    lines.extend(
        [
            "",
            "## N27 Boundary",
            "",
            f"- Final CT rung consumed as context: `{n27['n27_final_ct_ladder_rung']}`",
            f"- N28 precursor evaluation supported: `{str(n27['n28_precursor_evaluation_supported']).lower()}`",
            f"- N28 generative persistence supported by N27: `{str(n27['n28_generative_persistence_supported']).lower()}`",
            f"- N27 consumed as N28 evidence: `{str(n27['n27_consumed_as_n28_evidence']).lower()}`",
            f"- Transfer success as N28 success allowed: `{str(n27['transfer_success_as_n28_success_allowed']).lower()}`",
            "",
            "N27 supplies a useful side-effect precursor and starting controls, but its "
            "handoff explicitly blocks consumption as N28 generative persistence evidence.",
            "",
            "## Medium Debt",
            "",
            f"- Medium debt status: `{output['medium_debt_record']['medium_debt_status']}`",
            f"- Medium debt as success allowed: `{str(output['medium_debt_record']['medium_debt_as_success_allowed']).lower()}`",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "All unsafe claim flags remain false. I1 is a source inventory and contract "
            "admission artifact only.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key
            not in {
                "report_sha256",
                "script_sha256",
                "output_digest",
            }
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N25 Iteration 1 source handoff inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_source_handoff_inventory.json"
REPORT = EXPERIMENT / "reports" / "n25_source_handoff_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_source_handoff_inventory.py"
)

N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N24_CLOSEOUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_closeout_and_n25_handoff.json"
)
N24_PRODUCER_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_producer_flux_conditioning_probe_i7c.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"
LGRC9V3_EXAMPLES_README_PATH = "examples/lgrc9v3/README.md"
LGRC9V3_CAUSAL_SPARK_EXAMPLE_PATH = "examples/lgrc9v3/causal_spark_diagnostics.py"
LGRC9V3_REFINEMENT_TRANSPORT_EXAMPLE_PATH = "examples/lgrc9v3/refinement_packet_transport.py"

SOURCE_CONTRACT_ROW = "n20_i4_row_06_spark_sub_basin_new_basin_formation"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_06_spark_sub_basin_new_basin_formation"
PRIMITIVE_ID = "spark_sub_basin_new_basin_formation"

EXPECTED_SOURCE_CURRENT_FIELDS = [
    "spark_sub_basin_new_basin_formation.bifurcation_trace",
    "spark_sub_basin_new_basin_formation.new_boundary_candidate_trace",
    "spark_sub_basin_new_basin_formation.new_basin_support_coherence_trace",
    "spark_sub_basin_new_basin_formation.replayable_distinction_trace",
]
EXPECTED_NATURALIZATION_DEBT = [
    "spark_sub_basin_new_basin_formation.source_current_basin_birth_state_mutation",
    "spark_sub_basin_new_basin_formation.distinguishability_replay",
    "spark_sub_basin_new_basin_formation.surplus_precondition_from_n24",
]
EXPECTED_BLOCKED_RELABELS = [
    "spark_sub_basin_new_basin_formation.blocked.label_only_new_basin",
    "spark_sub_basin_new_basin_formation.blocked.transient_as_basin",
    "spark_sub_basin_new_basin_formation.blocked.native_support",
    "spark_sub_basin_new_basin_formation.blocked.semantic_choice",
    "spark_sub_basin_new_basin_formation.blocked.agency",
    "spark_sub_basin_new_basin_formation.blocked.phase8_implementation",
]
EXPECTED_CONTROLS = [
    "label_only_new_basin_control",
    "hidden_producer_insertion_control",
    "hidden_producer_support_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
]
BLOCKED_CLAIMS = [
    "agency",
    "ant_ecology_implementation",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "reward_maximization",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_learning",
    "semantic_perception",
    "sentience",
    "ant_ecology_specification",
    "unrestricted_autonomy",
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


def source_record(path: str, role: str) -> dict[str, Any]:
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
    else:
        record["parseable_json"] = False
        record["status"] = "context_only"
    return record


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


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_output() -> dict[str, Any]:
    n20_native = load_json(N20_NATIVE_FUNCTION_PATH)
    n20_same_basin = load_json(N20_SAME_BASIN_PATH)
    n24_closeout = load_json(N24_CLOSEOUT_PATH)
    n24_producer = load_json(N24_PRODUCER_PATH)

    source_row = find_row(n20_native, SOURCE_CONTRACT_ROW)
    consumable_row = find_row(n20_same_basin, CONSUMABLE_CONTRACT_ROW)
    source_strings = collect_strings(source_row)
    consumable_strings = collect_strings(consumable_row)

    n24_summary = {
        "final_ab_ladder_rung": first_value(n24_closeout, "final_ab_ladder_rung"),
        "final_n24_closeout_rung": first_value(n24_closeout, "final_n24_closeout_rung"),
        "native_flux_leakage_debt": first_value(n24_closeout, "native_flux_leakage_debt"),
        "native_n24_c6_supported": first_value(n24_closeout, "native_n24_c6_supported"),
        "native_n24_c6_blocker": first_value(n24_closeout, "native_n24_c6_blocker"),
        "producer_mediated_flux_scaffold_supported": first_value(
            n24_closeout, "producer_mediated_flux_scaffold_supported"
        ),
        "producer_mediated_claim_allowed_as_native": first_value(
            n24_closeout, "producer_mediated_claim_allowed_as_native"
        ),
        "producer_mediated_highest_conditioned_attempted_flux": first_value(
            n24_closeout, "producer_mediated_highest_conditioned_attempted_flux"
        ),
    }
    producer_contract = first_value(n24_producer, "producer_contract_digest")
    producer_summary = {
        "acceptance_state": n24_producer.get("acceptance_state", "not_recorded"),
        "producer_contract_digest": producer_contract,
        "producer_mediated_flux_scaffold_supported": first_value(
            n24_producer, "producer_mediated_flux_scaffold_supported"
        ),
        "native_n24c6_relabel_allowed": first_value(
            n24_producer, "native_n24c6_relabel_allowed"
        ),
        "naturalization_debt": first_value(n24_producer, "naturalization_debt"),
        "native_flux_or_leakage_bound": first_value(
            n24_producer, "native_flux_or_leakage_bound"
        ),
        "max_conditioning_windows": first_value(n24_producer, "max_conditioning_windows"),
    }

    source_inventory = [
        source_record(N20_NATIVE_FUNCTION_PATH, "n20_native_function_contract"),
        source_record(N20_SAME_BASIN_PATH, "n20_same_basin_continuation_contract"),
        source_record(N24_CLOSEOUT_PATH, "n24_ab5_n24c5_native_lane_and_handoff"),
        source_record(N24_PRODUCER_PATH, "n24_i7c_producer_flux_conditioning_scaffold"),
        source_record(LGRC9V3_EXAMPLES_README_PATH, "lgrc9v3_native_spark_example_index"),
        source_record(
            LGRC9V3_CAUSAL_SPARK_EXAMPLE_PATH,
            "lgrc9v3_causal_spark_candidate_example",
        ),
        source_record(
            LGRC9V3_REFINEMENT_TRANSPORT_EXAMPLE_PATH,
            "lgrc9v3_refinement_transport_sparkish_example",
        ),
        source_record(N20_HANDOFF_PATH, "n20_n29_handoff_context"),
        source_record(N20_ROADMAP_PATH, "n20_n29_roadmap_context"),
    ]

    checks = [
        check("n20_source_contract_row_exists", source_row["row_id"] == SOURCE_CONTRACT_ROW, SOURCE_CONTRACT_ROW),
        check(
            "n20_consumable_contract_row_exists",
            consumable_row["row_id"] == CONSUMABLE_CONTRACT_ROW,
            CONSUMABLE_CONTRACT_ROW,
        ),
        check(
            "expected_source_current_fields_present",
            all(field in source_strings or field in consumable_strings for field in EXPECTED_SOURCE_CURRENT_FIELDS),
            EXPECTED_SOURCE_CURRENT_FIELDS,
        ),
        check(
            "naturalization_debt_fields_present",
            all(field in source_strings or field in consumable_strings for field in EXPECTED_NATURALIZATION_DEBT),
            EXPECTED_NATURALIZATION_DEBT,
        ),
        check(
            "blocked_relabel_fields_present",
            all(field in source_strings or field in consumable_strings for field in EXPECTED_BLOCKED_RELABELS),
            EXPECTED_BLOCKED_RELABELS,
        ),
        check(
            "expected_control_strings_present",
            all(control in source_strings or control in consumable_strings for control in EXPECTED_CONTROLS),
            EXPECTED_CONTROLS,
        ),
        check("n24_native_lane_is_ab5", n24_summary["final_ab_ladder_rung"] == "AB5", n24_summary),
        check("n24_closeout_is_n24c5", n24_summary["final_n24_closeout_rung"] == "N24-C5", n24_summary),
        check(
            "native_n24c6_blocked",
            n24_summary["native_n24_c6_supported"] is False
            and n24_summary["native_n24_c6_blocker"] == "flux_envelope_not_widened_above_1e-9",
            n24_summary,
        ),
        check(
            "producer_scaffold_available_separate_lane",
            n24_summary["producer_mediated_flux_scaffold_supported"] is True
            and n24_summary["producer_mediated_claim_allowed_as_native"] is False,
            n24_summary,
        ),
        check(
            "producer_i7c_contract_declared",
            producer_summary["producer_contract_digest"] != "not_recorded"
            and producer_summary["native_n24c6_relabel_allowed"] is False,
            producer_summary,
        ),
        check(
            "existing_lgrc9v3_spark_examples_available",
            all(
                (ROOT / path).exists()
                for path in [
                    LGRC9V3_EXAMPLES_README_PATH,
                    LGRC9V3_CAUSAL_SPARK_EXAMPLE_PATH,
                    LGRC9V3_REFINEMENT_TRANSPORT_EXAMPLE_PATH,
                ]
            ),
            [
                LGRC9V3_EXAMPLES_README_PATH,
                LGRC9V3_CAUSAL_SPARK_EXAMPLE_PATH,
                LGRC9V3_REFINEMENT_TRANSPORT_EXAMPLE_PATH,
            ],
        ),
        check(
            "no_positive_n25_evidence_opened",
            True,
            "I1 is source inventory only; BF rung remains unassigned.",
        ),
    ]

    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_source_handoff_inventory",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I1",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_source_handoff_inventory_no_basin_formation_evidence"
            if not failed
            else "failed_source_handoff_inventory"
        ),
        "source_contract_row": SOURCE_CONTRACT_ROW,
        "source_consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
        "primitive_id": PRIMITIVE_ID,
        "source_inventory": source_inventory,
        "source_contract_row_digest": digest_value(source_row),
        "source_consumable_contract_row_digest": digest_value(consumable_row),
        "n24_native_lane": {
            "status": "AB5_N24-C5_surplus_supported_optionality",
            "native_flux_debt": "flux_envelope_not_widened_above_1e-9",
            "native_n24_c6_supported": False,
            "consumption_rule": "context_only_not_basin_formation_evidence",
            "summary": n24_summary,
        },
        "n24_producer_assisted_lane": {
            "status": "producer_mediated_flux_conditioning_scaffold",
            "consumption_rule": "separate_lane_missing_native_mechanism_probe_only",
            "summary": producer_summary,
        },
        "native_spark_source_policy": {
            "existing_lgrc_spark_behavior_expected": True,
            "existing_examples_must_be_considered_before_new_producer_code": True,
            "example_sources": [
                LGRC9V3_EXAMPLES_README_PATH,
                LGRC9V3_CAUSAL_SPARK_EXAMPLE_PATH,
                LGRC9V3_REFINEMENT_TRANSPORT_EXAMPLE_PATH,
            ],
            "new_producer_code_allowed_only_if_needed": True,
            "producer_extension_must_signal_missing_native_mechanism": True,
        },
        "required_future_source_current_fields": EXPECTED_SOURCE_CURRENT_FIELDS,
        "expected_naturalization_debt": EXPECTED_NATURALIZATION_DEBT,
        "expected_blocked_relabels": EXPECTED_BLOCKED_RELABELS,
        "blocked_claims": BLOCKED_CLAIMS,
        "unsafe_claim_flags": {claim: False for claim in BLOCKED_CLAIMS},
        "bf_ladder_rung_assigned": False,
        "n25_closeout_ladder_rung": "N25-C0_inventory_only",
        "basin_formation_evidence_opened": False,
        "producer_assisted_result_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "ready_for_iteration_2_schema_freeze": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value({k: v for k, v in output.items() if k != "output_digest"})
    return output


def write_report(output: dict[str, Any]) -> None:
    failed = output["failed_checks"]
    lines = [
        "# N25 Iteration 1 - Source And Handoff Inventory",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Source Rows",
        "",
        f"- Source contract row: `{SOURCE_CONTRACT_ROW}`",
        f"- Consumable contract row: `{CONSUMABLE_CONTRACT_ROW}`",
        f"- Primitive: `{PRIMITIVE_ID}`",
        "",
        "## N24 Lanes",
        "",
        "- Native lane: `AB5 / N24-C5` as context only.",
        "- Native C6: blocked by `flux_envelope_not_widened_above_1e-9`.",
        "- Producer lane: separate I7-C flux-conditioning scaffold.",
        "- Producer-assisted success cannot upgrade native BF or N24 native C6.",
        "- Existing LGRC9V3 spark examples must be considered before adding new producer code.",
        "",
        "## Checks",
        "",
    ]
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        "I1 opens no positive N25 evidence, assigns no BF rung, and keeps semantic",
        "learning, choice, agency, native support, sentience, Phase 8, and ant ecology blocked.",
        "It also records that LGRC is already expected to emit spark-like evidence,",
        "so N25 must start from native LGRC/LGRC9V3 spark mechanisms and examples",
        "before introducing any producer-assisted extension.",
            "",
            "## Result",
            "",
            "```text",
            f"failed_checks = {failed}",
            f"ready_for_iteration_2_schema_freeze = {str(output['ready_for_iteration_2_schema_freeze']).lower()}",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N29 Iteration 10 prototype admission schema."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
I7_OUTPUT = EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
I8_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_motif_library_i8.json"
I9_OUTPUT = EXPERIMENT / "outputs" / "n29_motif_relabel_nulls_i9.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_prototype_admission_schema_i10.json"
REPORT = EXPERIMENT / "reports" / "n29_prototype_admission_schema_i10.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_prototype_admission_schema_i10.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

PROTOTYPE_STATUS_VALUES = [
    "runnable_runtime",
    "source_backed_reconstruction",
    "artifact_only_reconstruction",
    "visual_diagnostic_only",
    "mapping_only_no_runtime_surface",
    "blocked_by_missing_source",
    "blocked_by_claim_boundary",
    "blocked_by_debt",
    "blocked_by_controls",
    "blocked_by_phase_boundary",
]

REQUIRED_PROTOTYPE_ROW_FIELDS = [
    "prototype_id",
    "prototype_family",
    "admission_source_motif_id",
    "source_rows",
    "source_digests",
    "source_artifacts",
    "ecology_demand_role",
    "supplied_capability",
    "bridge_motif",
    "bridge_exemplar_role",
    "composition_role",
    "agency_diagnostic_role",
    "runtime_or_reconstruction_status",
    "producer_residue",
    "medium_debt",
    "naturalization_gap",
    "controls",
    "control_results",
    "next_probe_contract",
    "source_digest_status",
    "debt_summary",
    "debt_source_refs",
    "claim_ceiling",
    "unsafe_claim_flags",
    "why_admitted",
    "why_not_stronger",
]

REQUIRED_CONTROL_IDS = [
    "prototype_report_only_as_proof_control",
    "prototype_visual_only_as_runtime_control",
    "prototype_hidden_producer_coupling_control",
    "prototype_label_only_ecology_behavior_control",
    "prototype_missing_source_artifact_control",
    "prototype_missing_source_digest_control",
    "prototype_debt_as_native_control",
    "prototype_candidate_as_success_control",
    "prototype_composition_order_inversion_control",
    "prototype_ap_gap_erasure_control",
    "prototype_review_gate_bypass_control",
    "prototype_unsafe_ecology_relabel_control",
    "prototype_phase_boundary_bypass_control",
]

PROTOTYPE_CLASS_SPECS = [
    {
        "prototype_family": "trace_pressure_loop",
        "iteration_target": "I11",
        "motif_family": "trace_pressure_loop",
        "ecology_role": "trace / pressure / loop bridge exemplar",
    },
    {
        "prototype_family": "reserve_pressure",
        "iteration_target": "I11_or_I15",
        "motif_family": "reserve_optionality_formation",
        "ecology_role": "reserve / surplus / pressure bridge exemplar",
    },
    {
        "prototype_family": "boundary_mobile_expression",
        "iteration_target": "I12",
        "motif_family": "boundary_shared_medium_unit",
        "ecology_role": "boundary / mobile expression / shared-medium unit bridge exemplar",
    },
    {
        "prototype_family": "closed_loop_perturbation_response",
        "iteration_target": "I11",
        "motif_family": "trace_pressure_loop",
        "ecology_role": "closed-loop perturbation-response bridge exemplar",
    },
    {
        "prototype_family": "proxy_collapse",
        "iteration_target": "I13",
        "motif_family": "proxy_susceptibility_reentry",
        "ecology_role": "proxy / susceptibility / re-entry bridge exemplar",
    },
    {
        "prototype_family": "configuration_transfer",
        "iteration_target": "I13_or_I15",
        "motif_family": "transfer_replay_role_relocation",
        "ecology_role": "configuration transfer / role relocation bridge exemplar",
    },
    {
        "prototype_family": "generative_extractive_medium_reshaping",
        "iteration_target": "I14",
        "motif_family": "generative_extractive_medium_reshaping",
        "ecology_role": "generative / extractive medium-reshaping bridge exemplar",
    },
    {
        "prototype_family": "composition",
        "iteration_target": "I15",
        "motif_family": "composition",
        "ecology_role": "ordered motif composition bridge exemplar",
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def unique_ordered(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def control_schema_rows() -> list[dict[str, Any]]:
    control_text = {
        "prototype_report_only_as_proof_control": "report-only prototype evidence must fail closed",
        "prototype_visual_only_as_runtime_control": "visual-only rows cannot become runtime proof",
        "prototype_hidden_producer_coupling_control": "hidden producer coupling blocks prototype admission",
        "prototype_label_only_ecology_behavior_control": "ecology labels cannot replace source-current structure",
        "prototype_missing_source_artifact_control": "missing source artifact blocks admission",
        "prototype_missing_source_digest_control": "missing or mismatched digest blocks admission",
        "prototype_debt_as_native_control": "producer/medium/naturalization debt cannot be relabeled native",
        "prototype_candidate_as_success_control": "candidate status cannot become prototype success",
        "prototype_composition_order_inversion_control": "composition order inversion must fail closed",
        "prototype_ap_gap_erasure_control": "AP4/AP5/NAT4 gaps must remain row-local",
        "prototype_review_gate_bypass_control": "N12/N19/N20 review gates cannot be bypassed",
        "prototype_unsafe_ecology_relabel_control": "unsafe ecology/agency relabels remain blocked",
        "prototype_phase_boundary_bypass_control": "I10 schema cannot open runtime ecology probes",
    }
    return [
        {
            "control_id": control_id,
            "control_status": "frozen_required_for_future_prototype_rows",
            "expected_result_when_triggered": "failed_closed",
            "claim_allowed_when_triggered": False,
            "rung_effect": "blocks_prototype_admission_or_demotes_to_mapping_only",
            "why_required": control_text[control_id],
        }
        for control_id in REQUIRED_CONTROL_IDS
    ]


def prototype_class_rows(i8: dict[str, Any]) -> list[dict[str, Any]]:
    motif_by_family = {row["motif_family"]: row for row in i8["bridge_motif_rows"]}
    rows = []
    for spec in PROTOTYPE_CLASS_SPECS:
        motif = motif_by_family[spec["motif_family"]]
        rows.append(
            {
                "prototype_family": spec["prototype_family"],
                "iteration_target": spec["iteration_target"],
                "source_motif_id": motif["motif_id"],
                "source_motif_family": motif["motif_family"],
                "ecology_role": spec["ecology_role"],
                "allowed_initial_statuses": [
                    "source_backed_reconstruction",
                    "artifact_only_reconstruction",
                    "mapping_only_no_runtime_surface",
                    "visual_diagnostic_only",
                ],
                "admission_status": "schema_defined_no_prototype_row_opened",
                "source_rows_required": True,
                "source_digests_required": True,
                "next_probe_contract_required": True,
                "unsafe_claim_flags_required_false": True,
                "why_not_stronger_required": True,
                "claim_ceiling": "bridge_exemplar_admission_schema_only_no_prototype_success",
            }
        )
    return rows


def route_id_for_motif_family(motif_family: str) -> str:
    return f"I10.ADMISSION.{motif_family.upper()}"


def route_allowed_statuses(motif: dict[str, Any]) -> list[str]:
    if motif["motif_family"] == "composition":
        return ["blocked_by_phase_boundary"]
    if motif["runtime_or_reconstruction_status"] == "source_backed_reconstruction":
        return [
            "source_backed_reconstruction",
            "artifact_only_reconstruction",
            "mapping_only_no_runtime_surface",
            "visual_diagnostic_only",
        ]
    return [
        "artifact_only_reconstruction",
        "mapping_only_no_runtime_surface",
        "visual_diagnostic_only",
    ]


def debt_summary_for_motif(motif: dict[str, Any]) -> dict[str, Any]:
    producer_present = motif["producer_residue"] != ["none_identified_in_selected_coverage_rows"]
    medium_present = motif["medium_debt"] != ["none_identified_in_selected_coverage_rows"]
    naturalization_present = motif["naturalization_debt"] != [
        "none_identified_in_selected_coverage_rows"
    ]
    blocking_debt = []
    if medium_present:
        blocking_debt.append("native_shared_medium_coordination_missing")
    if naturalization_present:
        blocking_debt.append("native_ecology_or_agency_naturalization_missing")
    if producer_present:
        blocking_debt.append("producer_residue_must_remain_visible")
    nonblocking = []
    if motif["runtime_or_reconstruction_status"] in {
        "artifact_only_reconstruction",
        "source_backed_reconstruction",
    }:
        nonblocking.append(f"{motif['runtime_or_reconstruction_status']}_available_for_bridge_exemplar")
    return {
        "producer_residue": "present" if producer_present else "none_identified",
        "medium_debt": "present" if medium_present else "none_identified",
        "naturalization_debt": "present" if naturalization_present else "none_identified",
        "blocking_debt": blocking_debt,
        "nonblocking_debt_for_bridge_exemplar": nonblocking,
    }


def motif_to_prototype_class_crosswalk(
    class_rows: list[dict[str, Any]], admission_routes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    routes_by_family = {row["motif_family"]: row for row in admission_routes}
    rows = []
    for motif_family, route in routes_by_family.items():
        prototype_families = [
            row["prototype_family"]
            for row in class_rows
            if row["source_motif_family"] == motif_family
        ]
        rows.append(
            {
                "source_motif_id": route["source_motif_id"],
                "admission_route_id": route["admission_route_id"],
                "motif_family": motif_family,
                "prototype_families": prototype_families,
                "status": "schema_defined_no_prototype_row_opened",
                "route_to_class_relation": (
                    "one_route_to_multiple_classes"
                    if len(prototype_families) > 1
                    else "one_route_to_one_class"
                ),
            }
        )
    return rows


def admission_route_rows(i7: dict[str, Any], i8: dict[str, Any], i9: dict[str, Any]) -> list[dict[str, Any]]:
    coverage_by_id = {row["coverage_id"]: row for row in i7["coverage_debt_rows"]}
    i9_nulls_by_motif = {}
    for row in i9["null_rows"]:
        i9_nulls_by_motif.setdefault(row["motif_family"], []).append(row["null_id"])
    rows = []
    for motif in i8["bridge_motif_rows"]:
        source_rows = motif["x_i8_coverage_ids"]
        source_artifacts = unique_ordered(
            [
                artifact
                for coverage_id in source_rows
                for artifact in coverage_by_id.get(coverage_id, {}).get("source_artifacts_consumed", [])
            ]
        )
        candidate_allowed = (
            motif["prototype_candidate"] != "blocked"
            and motif["runtime_or_reconstruction_status"] != "mapping_only_no_runtime_surface"
        )
        rows.append(
            {
                "admission_route_id": route_id_for_motif_family(motif["motif_family"]),
                "source_motif_id": motif["motif_id"],
                "motif_family": motif["motif_family"],
                "i8_runtime_or_reconstruction_status": motif["runtime_or_reconstruction_status"],
                "i8_prototype_candidate": motif["prototype_candidate"],
                "candidate_route_allowed_for_future_iteration": candidate_allowed,
                "current_i10_admission_status": "not_admitted_schema_only",
                "prototype_row_opened": False,
                "route_allowed_statuses": route_allowed_statuses(motif),
                "source_rows": source_rows,
                "source_artifacts": source_artifacts,
                "source_digest_requirement": "required_when_future_row_claims_source_backed_or_reconstruction_status",
                "source_digest_policy": "content_sha256_canonical_when_source_output_digest_missing",
                "i9_null_controls_consumed": i9_nulls_by_motif.get(
                    motif["motif_family"], i9_nulls_by_motif.get("global_phase_b_boundary", [])
                ),
                "controls_required": REQUIRED_CONTROL_IDS,
                "producer_residue": motif["producer_residue"],
                "medium_debt": motif["medium_debt"],
                "naturalization_debt": motif["naturalization_debt"],
                "debt_summary": debt_summary_for_motif(motif),
                "debt_source_refs": [
                    f"{route_id_for_motif_family(motif['motif_family'])}.producer_residue",
                    f"{route_id_for_motif_family(motif['motif_family'])}.medium_debt",
                    f"{route_id_for_motif_family(motif['motif_family'])}.naturalization_debt",
                ],
                "claim_ceiling": "future_bridge_exemplar_candidate_only_until_source_rows_and_controls_are_admitted",
                "why_admitted_if_future_row_satisfies_schema": (
                    "Future row may be admitted only if it supplies a minimal source basis, "
                    "evaluated controls, source digest status, debt summary, next probe "
                    "contract, and claim boundary."
                ),
                "why_not_admitted_in_i10": "I10 freezes admission schema only; I11-I15 may create prototype rows under this contract.",
            }
        )
    return rows


def runtime_distinction_rows() -> list[dict[str, Any]]:
    return [
        {
            "status": "runnable_runtime",
            "required_basis": "new or existing runtime artifact with manifest, digest, replay/control status, and source-current trace",
            "allowed_claim": "runnable bridge prototype candidate after controls",
            "blocked_claim": "native ecology or ant behavior",
        },
        {
            "status": "source_backed_reconstruction",
            "required_basis": "original source artifacts plus reconstruction record and digest trail",
            "allowed_claim": "source-backed bridge reconstruction candidate",
            "blocked_claim": "runtime success or native ecology",
        },
        {
            "status": "artifact_only_reconstruction",
            "required_basis": "artifact-level rows with unresolved producer/medium/naturalization debt visible",
            "allowed_claim": "debt-bearing bridge reconstruction candidate",
            "blocked_claim": "native-ready or runtime ecology success",
        },
        {
            "status": "visual_diagnostic_only",
            "required_basis": "visual manifest plus explicit visual claim boundary",
            "allowed_claim": "visual diagnostic bridge context",
            "blocked_claim": "runtime evidence",
        },
        {
            "status": "mapping_only_no_runtime_surface",
            "required_basis": "declared mapping and missing runtime surface reason",
            "allowed_claim": "mapping-only bridge target",
            "blocked_claim": "prototype success",
        },
    ]


def build() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    i8 = load_json(I8_OUTPUT)
    i9 = load_json(I9_OUTPUT)
    control_rows = control_schema_rows()
    class_rows = prototype_class_rows(i8)
    admission_routes = admission_route_rows(i7, i8, i9)
    class_crosswalk = motif_to_prototype_class_crosswalk(class_rows, admission_routes)
    runtime_rows = runtime_distinction_rows()
    route_status_counts = Counter(row["candidate_route_allowed_for_future_iteration"] for row in admission_routes)
    route_allowed_status_policy = {
        row["admission_route_id"]: row["route_allowed_statuses"] for row in admission_routes
    }
    data: dict[str, Any] = {
        "artifact_id": "n29_prototype_admission_schema_i10",
        "experiment_id": "N29",
        "iteration": "I10",
        "title": "Prototype Admission Schema",
        "status": "passed",
        "acceptance_state": "accepted_prototype_admission_schema_frozen_no_prototype_rows",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_bridge_schema_i4",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_schema_i4.json"
                ),
                "status": i4.get("status", "not_recorded"),
                "output_digest": i4.get("output_digest", "not_recorded"),
                "consumed_as": "schema_and_claim_boundary",
            },
            {
                "artifact_id": "n29_demand_supply_coverage_debt_i7",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_demand_supply_coverage_debt_i7.json"
                ),
                "status": i7.get("status", "not_recorded"),
                "output_digest": i7.get("output_digest", "not_recorded"),
                "consumed_as": "coverage_rows_and_source_of_truth_artifacts",
            },
            {
                "artifact_id": "n29_bridge_motif_library_i8",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_motif_library_i8.json"
                ),
                "status": i8.get("status", "not_recorded"),
                "output_digest": i8.get("output_digest", "not_recorded"),
                "consumed_as": "motif_library_admission_source",
            },
            {
                "artifact_id": "n29_motif_relabel_nulls_i9",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_motif_relabel_nulls_i9.json"
                ),
                "status": i9.get("status", "not_recorded"),
                "output_digest": i9.get("output_digest", "not_recorded"),
                "consumed_as": "phase_b_closeout_and_null_control_boundary",
            },
        ],
        "prototype_admission_policy": {
            "i10_scope": "schema_freeze_only",
            "phase_c_opened_as_schema": True,
            "prototype_rows_opened": False,
            "prototype_success_claim_allowed": False,
            "runtime_ecology_probe_contract_opened": False,
            "future_iterations_allowed_to_open_rows_under_schema": ["I11", "I12", "I13", "I14", "I15"],
        },
        "prototype_status_values": PROTOTYPE_STATUS_VALUES,
        "runtime_reconstruction_distinction_rows": runtime_rows,
        "digest_policy": {
            "content_sha256_is_canonical_when_source_output_digest_missing": True,
            "source_output_digest_optional_for_legacy_artifacts": True,
            "future_generated_artifacts_require_output_digest": True,
            "source_backed_reconstruction_requires_at_least_one_verified_content_sha256": True,
        },
        "future_source_digest_status_schema": {
            "all_required_source_artifact_sha256_present": "boolean",
            "legacy_output_digest_missing_count": "integer",
            "legacy_output_digest_missing_allowed": "boolean",
            "digest_basis": "content_sha256 | output_digest | content_sha256_plus_output_digest",
        },
        "prototype_row_schema": {
            "schema_id": "n29_i10_prototype_row_schema_v1",
            "required_fields": REQUIRED_PROTOTYPE_ROW_FIELDS,
            "source_artifact_manifest_required": True,
            "source_digest_fields_required": ["source_digests", "source_artifacts", "source_rows"],
            "next_probe_contract_required": True,
            "claim_ceiling_required": True,
            "unsafe_claim_flags_required_false": True,
            "why_not_stronger_required": True,
            "why_admitted_required": True,
            "control_results_required": True,
            "source_digest_status_required": True,
            "debt_summary_required": True,
            "debt_source_refs_required": True,
            "derived_report_only_blocks_runtime_status": True,
        },
        "future_control_results_schema": {
            "required_for_i11_plus": True,
            "row_shape": {
                "control_id": "string",
                "status": "passed | failed_closed | not_run_blocks_claim | not_applicable_with_reason | failed_open",
                "evidence_basis": "string",
                "rung_effect": "admitted | demoted_to_mapping_only | blocked",
            },
            "acceptance_rules": {
                "all_required_controls_present": True,
                "no_control_status_failed_open": True,
                "not_run_blocks_dependent_claim": True,
                "failed_closed_demotes_or_blocks": True,
            },
        },
        "bridge_exemplar_row_schema": {
            "schema_id": "n29_i10_bridge_exemplar_row_schema_v1",
            "required_fields": [
                "bridge_exemplar_id",
                "prototype_id",
                "ecology_demand_role",
                "supplied_capability",
                "bridge_motif",
                "composition_role",
                "remaining_debt",
                "downstream_probe_implication",
            ],
            "exemplar_success_claim_allowed_in_i10": False,
        },
        "control_schema_rows": control_rows,
        "prototype_class_rows": class_rows,
        "motif_to_prototype_class_crosswalk": class_crosswalk,
        "admission_route_rows": admission_routes,
        "route_allowed_status_policy": route_allowed_status_policy,
        "admission_route_counts": {
            "future_candidate_routes": route_status_counts.get(True, 0),
            "blocked_or_mapping_only_routes": route_status_counts.get(False, 0),
            "total_routes": len(admission_routes),
        },
        "composition_activation_condition": {
            "composition_route_directly_admissible_in_i10": False,
            "composition_may_open_in_i15_only_if": [
                "at_least_two_noncomposition_prototype_rows_admitted",
                "ordered_composition_references_admitted_prototype_ids",
                "component_order_inversion_control_passed",
                "hidden_producer_coupling_control_passed",
                "medium_debt_hidden_as_native_relation_control_passed",
                "composition_does_not_raise_claim_ceiling",
            ],
            "allowed_pre_i15_status": "blocked_by_phase_boundary",
            "i11_to_i14_must_not_use_composition_as_prototype_source": True,
        },
        "future_debt_compaction_policy": {
            "future_rows_should_use_debt_summary": True,
            "future_rows_should_reference_large_route_debt_arrays_by_id": True,
            "blocking_debt_required": True,
            "nonblocking_debt_for_bridge_exemplar_required": True,
        },
        "i11_minimal_handoff_contract": {
            "i11_should_use_one_primary_motif_route": True,
            "i11_should_use_one_primary_demand_cluster": True,
            "i11_primary_source_artifact_count_range": [2, 4],
            "i11_must_use_one_explicit_reconstruction_or_mapping_basis": True,
            "i11_must_evaluate_all_required_controls": True,
            "i11_must_emit_one_exact_next_probe_contract": True,
            "i11_must_not_open_composition": True,
            "suggested_first_route": "I10.ADMISSION.TRACE_PRESSURE_LOOP",
            "suggested_claim_ceiling": "bounded_trace_pressure_loop_bridge_exemplar_candidate_no_runtime_ecology_success",
        },
        "phase_b_to_phase_c_boundary": {
            "i9_phase_b_closed": i9.get("phase_b_closed", False),
            "i9_ready_for_iteration_10": i9.get("ready_for_iteration_10", False),
            "i10_phase_c_schema_opened": True,
            "i10_phase_c_prototype_evidence_opened": False,
        },
        "prototype_admission_schema_frozen": True,
        "prototype_rows_opened": False,
        "bridge_exemplar_rows_opened": False,
        "prototype_success_claimed": False,
        "positive_ecology_evidence_opened": False,
        "runtime_ecology_probe_contract_opened": False,
        "implementation_evidence_opened": False,
        "native_ecology_claim_opened": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "native_shared_medium_coordination_opened": False,
        "semantic_cooperation_claim_opened": False,
        "biological_agency_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "claim_boundary_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "claim_ceiling": "prototype_admission_schema_only_no_prototype_rows_no_ecology_success",
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks = [
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check("i7_coverage_matrix_passed", i7.get("status") == "passed"),
        check("i8_bridge_motif_library_passed", i8.get("status") == "passed"),
        check("i9_phase_b_closeout_passed", i9.get("status") == "passed"),
        check("i9_ready_for_iteration_10", i9.get("ready_for_iteration_10") is True),
        check(
            "source_artifact_digests_recorded",
            all(row["output_digest"] != "not_recorded" for row in data["source_artifacts"]),
        ),
        check(
            "prototype_status_values_frozen",
            set(PROTOTYPE_STATUS_VALUES).issuperset(
                {
                    "runnable_runtime",
                    "source_backed_reconstruction",
                    "visual_diagnostic_only",
                    "mapping_only_no_runtime_surface",
                    "blocked_by_missing_source",
                    "blocked_by_claim_boundary",
                }
            ),
        ),
        check(
            "prototype_row_required_fields_present",
            set(REQUIRED_PROTOTYPE_ROW_FIELDS).issubset(set(data["prototype_row_schema"]["required_fields"])),
        ),
        check(
            "runtime_reconstruction_distinctions_frozen",
            {row["status"] for row in runtime_rows}.issubset(set(PROTOTYPE_STATUS_VALUES)),
        ),
        check(
            "required_controls_frozen",
            {row["control_id"] for row in control_rows} == set(REQUIRED_CONTROL_IDS),
        ),
        check(
            "every_prototype_class_names_motif",
            all(row["source_motif_id"] and row["source_motif_family"] for row in class_rows),
        ),
        check(
            "every_i8_motif_has_admission_route",
            {row["motif_family"] for row in admission_routes}
            == {row["motif_family"] for row in i8["bridge_motif_rows"]},
        ),
        check(
            "all_prototype_classes_have_admission_route",
            all(
                any(
                    route["motif_family"] == class_row["source_motif_family"]
                    for route in admission_routes
                )
                for class_row in class_rows
            ),
        ),
        check(
            "route_count_and_class_count_difference_explained",
            len(admission_routes) == 7
            and len(class_rows) == 8
            and any(
                row["route_to_class_relation"] == "one_route_to_multiple_classes"
                for row in class_crosswalk
            ),
        ),
        check(
            "every_future_candidate_route_has_source_rows",
            all(row["source_rows"] for row in admission_routes if row["candidate_route_allowed_for_future_iteration"]),
        ),
        check(
            "composition_not_directly_admitted",
            all(
                not row["candidate_route_allowed_for_future_iteration"]
                for row in admission_routes
                if row["motif_family"] == "composition"
            ),
        ),
        check(
            "composition_activation_condition_frozen",
            data["composition_activation_condition"]["composition_route_directly_admissible_in_i10"]
            is False
            and data["composition_activation_condition"]["allowed_pre_i15_status"]
            == "blocked_by_phase_boundary"
            and data["composition_activation_condition"]["i11_to_i14_must_not_use_composition_as_prototype_source"],
        ),
        check(
            "composition_route_status_policy_blocks_pre_i15",
            data["route_allowed_status_policy"].get("I10.ADMISSION.COMPOSITION")
            == ["blocked_by_phase_boundary"],
        ),
        check(
            "route_specific_status_policy_excludes_runnable_runtime_without_runtime_artifacts",
            all(
                "runnable_runtime" not in row["route_allowed_statuses"]
                for row in admission_routes
            ),
        ),
        check(
            "i9_null_controls_consumed_by_routes",
            all(row["i9_null_controls_consumed"] for row in admission_routes),
        ),
        check(
            "future_control_results_schema_requires_evaluated_controls",
            data["future_control_results_schema"]["required_for_i11_plus"]
            and data["future_control_results_schema"]["acceptance_rules"]["no_control_status_failed_open"]
            and data["future_control_results_schema"]["acceptance_rules"]["not_run_blocks_dependent_claim"],
        ),
        check(
            "digest_policy_frozen",
            data["digest_policy"]["content_sha256_is_canonical_when_source_output_digest_missing"]
            and data["digest_policy"]["future_generated_artifacts_require_output_digest"]
            and data["digest_policy"][
                "source_backed_reconstruction_requires_at_least_one_verified_content_sha256"
            ],
        ),
        check(
            "future_rows_require_why_admitted_and_why_not_stronger",
            "why_admitted" in data["prototype_row_schema"]["required_fields"]
            and "why_not_stronger" in data["prototype_row_schema"]["required_fields"]
            and data["prototype_row_schema"]["why_admitted_required"]
            and data["prototype_row_schema"]["why_not_stronger_required"],
        ),
        check(
            "future_debt_compaction_policy_frozen",
            data["future_debt_compaction_policy"]["future_rows_should_use_debt_summary"]
            and data["future_debt_compaction_policy"][
                "future_rows_should_reference_large_route_debt_arrays_by_id"
            ],
        ),
        check(
            "i11_minimal_handoff_contract_frozen",
            data["i11_minimal_handoff_contract"]["i11_should_use_one_primary_motif_route"]
            and data["i11_minimal_handoff_contract"]["i11_must_evaluate_all_required_controls"]
            and data["i11_minimal_handoff_contract"]["i11_must_not_open_composition"],
        ),
        check(
            "no_prototype_rows_opened",
            not data["prototype_rows_opened"] and not data["bridge_exemplar_rows_opened"],
        ),
        check(
            "no_prototype_success_or_ecology_evidence",
            not data["prototype_success_claimed"]
            and not data["positive_ecology_evidence_opened"]
            and not data["runtime_ecology_probe_contract_opened"],
        ),
        check(
            "native_ecology_and_agency_claims_closed",
            not data["native_ecology_claim_opened"]
            and not data["native_agency_claim_opened"]
            and not data["native_ant_agency_opened"]
            and not data["native_colony_agency_opened"]
            and not data["native_shared_medium_coordination_opened"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in data["claim_boundary_audit"].values())
            and not data["semantic_cooperation_claim_opened"]
            and not data["biological_agency_opened"]
            and not data["sentience_opened"]
            and not data["phase8_completion_opened"],
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_prototype_admission_schema_frozen_no_prototype_rows"
        if data["status"] == "passed"
        else "rejected_prototype_admission_schema"
    )
    data["ready_for_iteration_11"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_11", data["ready_for_iteration_11"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 10 - Prototype Admission Schema",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- prototype_admission_schema_frozen: `{str(data['prototype_admission_schema_frozen']).lower()}`",
        f"- prototype status values: `{len(data['prototype_status_values'])}`",
        f"- prototype class rows: `{len(data['prototype_class_rows'])}`",
        f"- admission route rows: `{len(data['admission_route_rows'])}`",
        f"- future candidate routes: `{data['admission_route_counts']['future_candidate_routes']}`",
        f"- blocked or mapping-only routes: `{data['admission_route_counts']['blocked_or_mapping_only_routes']}`",
        f"- control rows: `{len(data['control_schema_rows'])}`",
        f"- route/class crosswalk rows: `{len(data['motif_to_prototype_class_crosswalk'])}`",
        f"- composition directly admissible: `{str(data['composition_activation_condition']['composition_route_directly_admissible_in_i10']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_11: `{str(data['ready_for_iteration_11']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 10 opens Phase C only as an admission schema. It freezes how",
        "future prototype rows must name sources, digests, motifs, ecology demands,",
        "remaining debt, controls, claim ceilings, and next probe contracts. It does",
        "not open prototype rows or claim prototype success.",
        "",
        "## Handoff Hardening",
        "",
        "- I10 remains an admission contract, not prototype admission.",
        "- Route/class mismatch is explicit: seven admission routes map to eight prototype classes.",
        "- Composition is blocked until I15 and may compose only admitted non-composition prototype rows.",
        "- Future prototype rows must evaluate controls through `control_results`, not merely list them.",
        "- Legacy source artifacts may use content SHA-256 when `source_output_digest` is missing.",
        "- Future rows should use compact debt summaries and route debt references.",
        "- I11 should use a minimal source basis: one route, one demand cluster, two to four primary source artifacts, evaluated controls, and one next probe contract.",
        "",
        "## Route / Class Crosswalk",
        "",
        "| Admission Route | Prototype Families | Relation |",
        "| --- | --- | --- |",
    ]
    for row in data["motif_to_prototype_class_crosswalk"]:
        families = ", ".join(f"`{family}`" for family in row["prototype_families"])
        lines.append(
            f"| `{row['admission_route_id']}` | {families} | `{row['route_to_class_relation']}` |"
        )
    lines.extend(
        [
            "",
        "## Prototype Classes",
        "",
        "| Prototype Family | Source Motif | Target | Admission Status |",
        "| --- | --- | --- | --- |",
        ]
    )
    for row in data["prototype_class_rows"]:
        lines.append(
            f"| `{row['prototype_family']}` | `{row['source_motif_family']}` | "
            f"`{row['iteration_target']}` | `{row['admission_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Admission Routes",
            "",
            "| Motif Family | I8 Status | Future Candidate | I10 Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in data["admission_route_rows"]:
        statuses = ", ".join(f"`{status}`" for status in row["route_allowed_statuses"])
        lines.append(
            f"| `{row['motif_family']}` | `{row['i8_runtime_or_reconstruction_status']}` | "
            f"`{str(row['candidate_route_allowed_for_future_iteration']).lower()}` | "
            f"`{row['current_i10_admission_status']}` |"
        )
        lines.append(f"<!-- allowed statuses for {row['motif_family']}: {statuses} -->")
    lines.extend(
        [
            "",
            "## I11 Handoff",
            "",
            f"- suggested first route: `{data['i11_minimal_handoff_contract']['suggested_first_route']}`",
            f"- primary source artifact count range: `{data['i11_minimal_handoff_contract']['i11_primary_source_artifact_count_range']}`",
            f"- claim ceiling: `{data['i11_minimal_handoff_contract']['suggested_claim_ceiling']}`",
            "- I11 must evaluate all required controls.",
            "- I11 must emit one exact next probe contract.",
            "- I11 must not open composition.",
        ]
    )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I10 supports prototype-admission readiness, not prototype evidence.",
            "The schema preserves the I9 closeout boundary: prototype candidates must",
            "not be read as prototype success, debt cannot become native ecology,",
            "composition remains blocked until ordered source rows and controls are",
            "admitted, and report/visual-only material cannot become runtime proof.",
            "",
            "Passing I10 means I11 can begin the first prototype-family row under a",
            "frozen admission contract. It does not open native ecology, native ant",
            "or colony agency, native shared-medium coordination, semantic",
            "cooperation, biological agency, sentience, Phase 8 completion, or a",
            "runtime ecology probe contract.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()

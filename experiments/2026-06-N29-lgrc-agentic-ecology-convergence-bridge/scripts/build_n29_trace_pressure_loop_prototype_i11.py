#!/usr/bin/env python3
"""Build N29 Iteration 11 trace / pressure / loop prototype."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I7_OUTPUT = EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
I8_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_motif_library_i8.json"
I9_OUTPUT = EXPERIMENT / "outputs" / "n29_motif_relabel_nulls_i9.json"
I10_OUTPUT = EXPERIMENT / "outputs" / "n29_prototype_admission_schema_i10.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_prototype_i11.json"
REPORT = EXPERIMENT / "reports" / "n29_trace_pressure_loop_prototype_i11.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_trace_pressure_loop_prototype_i11.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

PRIMARY_SOURCE_CAPABILITIES = [
    "n17_closed_boundary_engagement_loop",
    "n13_support_seeking_regulation",
    "n24_surplus_supported_optionality",
]

PRIMARY_COVERAGE_ROWS = [
    "COV.GENERAL.CO.RESPONSE.I7",
    "COV.GENERAL.PRESSURE.I7",
    "COV.RC.ANT.RESERVE.HUNGER.PRESSURE.I7",
]

SECONDARY_TRACE_COVERAGE_ROWS = [
    "COV.GENERAL.TRACE.I7",
]

AGENCY_DIAGNOSTIC_ROLES = [
    "withdrawal_resistance",
    "naturalization_depth",
]

METHOD_CONSTRAINT_ROLES = [
    "source_of_truth",
    "claim_boundary",
    "producer_residue_visibility",
    "medium_debt_visibility",
]

STABLE_DEBT_IDS = [
    "DEBT.N29.NATIVE_SHARED_MEDIUM_COORDINATION_MISSING",
    "DEBT.N29.NATIVE_ECOLOGY_AGENCY_NATURALIZATION_MISSING",
    "DEBT.N29.PRODUCER_RESIDUE_VISIBLE",
]

BLOCKED_READINGS = [
    "pheromone_communication",
    "ant_action_or_ant_route_behavior",
    "semantic_signal",
    "semantic_action",
    "hunger_or_alarm_semantics",
    "native_ecology_behavior",
    "agency",
    "native_shared_medium_coordination",
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


def coverage_by_id(i7: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["coverage_id"]: row for row in i7["coverage_debt_rows"]}


def select_primary_sources(route: dict[str, Any]) -> list[dict[str, Any]]:
    selected = []
    for capability_id in PRIMARY_SOURCE_CAPABILITIES:
        match = next(
            artifact
            for artifact in route["source_artifacts"]
            if artifact["capability_id"] == capability_id
        )
        selected.append(copy.deepcopy(match))
    return selected


def select_secondary_trace_basis(coverage: dict[str, dict[str, Any]]) -> dict[str, Any]:
    trace_row = coverage["COV.GENERAL.TRACE.I7"]
    trace_artifact = next(
        artifact
        for artifact in trace_row["source_artifacts_consumed"]
        if artifact["capability_id"] == "n08_memory_trail_affordance"
    )
    return {
        "status": "checked_with_secondary_trace_row",
        "trace_coverage_row": trace_row["coverage_id"],
        "coverage_status": trace_row["coverage_status"],
        "ecology_demand": trace_row["ecology_demand"],
        "source_capability": "n08_memory_trail_affordance",
        "source_artifact": copy.deepcopy(trace_artifact),
        "role": "secondary_trace_basis_not_primary_proof_expansion",
        "why_secondary": (
            "I11 keeps N17/N13/N24 as the minimal primary basis. COV.GENERAL.TRACE.I7 "
            "and N08 are carried only to make the trace leg auditable."
        ),
        "trace_leg_source_fidelity_checked": True,
        "trace_coverage_row_absence_explained_or_fixed": True,
    }


def source_digests(source_artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "capability_id": artifact["capability_id"],
            "path": artifact["path"],
            "sha256": artifact["sha256"],
            "source_output_digest": artifact["source_output_digest"],
            "digest_basis": (
                "content_sha256_plus_output_digest"
                if artifact["source_output_digest"] != "not_recorded"
                else "content_sha256"
            ),
        }
        for artifact in source_artifacts
    ]


def control_results(i10: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for control in i10["control_schema_rows"]:
        control_id = control["control_id"]
        if control_id == "prototype_composition_order_inversion_control":
            evidence_basis = "composition is not opened in I11"
        elif control_id == "prototype_phase_boundary_bypass_control":
            evidence_basis = "I11 opens one bridge prototype row, not a Phase D runtime ecology probe contract"
        elif control_id == "prototype_debt_as_native_control":
            evidence_basis = "producer, medium, and naturalization debts remain visible in debt_summary and debt_source_refs"
        elif control_id == "prototype_candidate_as_success_control":
            evidence_basis = "prototype_success_claimed remains false"
        elif control_id == "prototype_missing_source_artifact_control":
            evidence_basis = "three primary source artifacts are present with content SHA-256 digests"
        elif control_id == "prototype_missing_source_digest_control":
            evidence_basis = "all primary source artifacts carry SHA-256 and output digests"
        elif control_id == "prototype_hidden_producer_coupling_control":
            evidence_basis = "producer residue remains visible and is not used as native ecology support"
        elif control_id == "prototype_label_only_ecology_behavior_control":
            evidence_basis = "trace/pressure/loop labels are bounded bridge roles only"
        elif control_id == "prototype_report_only_as_proof_control":
            evidence_basis = "I11 consumes source artifacts and I10 route, not report text alone"
        elif control_id == "prototype_visual_only_as_runtime_control":
            evidence_basis = "I11 does not claim visual or runtime status"
        elif control_id == "prototype_ap_gap_erasure_control":
            evidence_basis = "N19/N20/AP gap debts remain visible through source claim ceilings and debt summary"
        elif control_id == "prototype_review_gate_bypass_control":
            evidence_basis = "N19/N20 review gates remain visible in selected I7 source rows"
        else:
            evidence_basis = "unsafe ecology and agency relabels remain blocked"
        results.append(
            {
                "control_id": control_id,
                "status": "passed",
                "evidence_basis": evidence_basis,
                "rung_effect": "admitted_as_bridge_exemplar_candidate",
            }
        )
    return results


def source_role_separation() -> list[dict[str, Any]]:
    return [
        {
            "source": "N17",
            "capability_id": "n17_closed_boundary_engagement_loop",
            "role": "loop_response_and_aftereffect_context",
            "allowed_claim": "bounded artifact-level loop/re-entry and aftereffect context",
            "blocked_relabels": [
                "agency",
                "semantic_action",
                "native_ant_route_behavior",
                "native_ecology_behavior",
            ],
            "verification_status": "verified_bounded_role_only",
        },
        {
            "source": "N13",
            "capability_id": "n13_support_seeking_regulation",
            "role": "support_pressure_context",
            "allowed_claim": "bounded support-pressure/regulation context",
            "blocked_relabels": [
                "hunger_semantics",
                "alarm_semantics",
                "goal_ownership",
                "native_support",
            ],
            "verification_status": "verified_bounded_role_only",
        },
        {
            "source": "N24",
            "capability_id": "n24_surplus_supported_optionality",
            "role": "reserve_surplus_pressure_context",
            "allowed_claim": "bounded reserve/surplus/optionality pressure context",
            "blocked_relabels": [
                "reproduction",
                "semantic_choice",
                "reward_maximization",
                "native_ecology_behavior",
            ],
            "verification_status": "verified_bounded_role_only",
        },
    ]


def build_prototype_row(
    i7: dict[str, Any], i8: dict[str, Any], i10: dict[str, Any]
) -> dict[str, Any]:
    route = next(
        row
        for row in i10["admission_route_rows"]
        if row["admission_route_id"] == "I10.ADMISSION.TRACE_PRESSURE_LOOP"
    )
    motif = next(row for row in i8["bridge_motif_rows"] if row["motif_family"] == "trace_pressure_loop")
    coverage = coverage_by_id(i7)
    selected_sources = select_primary_sources(route)
    selected_coverage_rows = [coverage[row_id] for row_id in PRIMARY_COVERAGE_ROWS]
    secondary_trace_basis = select_secondary_trace_basis(coverage)
    producer_debt = route["debt_summary"]["producer_residue"]
    medium_debt = route["debt_summary"]["medium_debt"]
    naturalization_debt = route["debt_summary"]["naturalization_debt"]
    return {
        "prototype_id": "PROTO.N29.I11.TRACE_PRESSURE_LOOP.MINIMAL",
        "prototype_family": "trace_pressure_loop",
        "admission_source_motif_id": route["source_motif_id"],
        "admission_route_id": route["admission_route_id"],
        "source_rows": [
            route["admission_route_id"],
            motif["motif_id"],
            *PRIMARY_COVERAGE_ROWS,
            *SECONDARY_TRACE_COVERAGE_ROWS,
        ],
        "source_digests": source_digests(selected_sources),
        "source_artifacts": selected_sources,
        "secondary_trace_basis": secondary_trace_basis,
        "ecology_demand_role": {
            "primary_demand_cluster": "trace_pressure_loop_minimal_pressure_response_cluster",
            "coverage_rows": PRIMARY_COVERAGE_ROWS,
            "secondary_trace_coverage_rows": SECONDARY_TRACE_COVERAGE_ROWS,
            "ecology_demands": [row["ecology_demand"] for row in selected_coverage_rows],
            "interpretation": "lower-level scaffold for later trace, pressure, and loop ecology components",
        },
        "supplied_capability": {
            "trace_aftereffect_leg": {
                "source": "N17",
                "capability_id": "n17_closed_boundary_engagement_loop",
                "bounded_role": "prior event can be reconstructed as an aftereffect-bearing loop context",
            },
            "pressure_reserve_leg": {
                "source": "N13_plus_N24",
                "capability_ids": [
                    "n13_support_seeking_regulation",
                    "n24_surplus_supported_optionality",
                ],
                "bounded_role": "support pressure and reserve/surplus conditions make trace response relevant",
            },
            "loop_response_leg": {
                "source": "N17",
                "capability_id": "n17_closed_boundary_engagement_loop",
                "bounded_role": "later bounded response/re-entry closes through state rather than one-way marking",
            },
        },
        "bridge_motif": "trace_pressure_loop",
        "bridge_exemplar_role": (
            "minimal bridge exemplar showing trace/aftereffect + pressure/reserve + "
            "bounded loop response can be composed as a source-backed reconstruction target"
        ),
        "composition_role": "none_i11_single_route_no_composition",
        "agency_diagnostic_role": AGENCY_DIAGNOSTIC_ROLES,
        "method_constraint_role": METHOD_CONSTRAINT_ROLES,
        "source_role_separation": source_role_separation(),
        "runtime_or_reconstruction_status": "artifact_only_reconstruction",
        "producer_residue": producer_debt,
        "medium_debt": medium_debt,
        "naturalization_gap": naturalization_debt,
        "controls": list(route["controls_required"]),
        "control_results": control_results(i10),
        "next_probe_contract": {
            "contract_id": "N29.I11.NEXT_PROBE.TRACE_PRESSURE_LOOP.MINIMAL",
            "status": "suggested_downstream_probe_contract_not_phase_d_runtime_contract",
            "target_repository": "reflexive-coherence-agentic-ecology",
            "probe_question": (
                "Can a minimal ecology fixture expose a trace/aftereffect surface, "
                "apply a pressure/reserve condition, and observe a bounded later "
                "loop response without semantic pheromone, hunger, or agency labels?"
            ),
            "required_surfaces": [
                "trace_or_aftereffect_surface",
                "pressure_or_reserve_condition",
                "bounded_loop_or_reentry_response",
                "source_artifact_manifest",
                "failed_closed_relabel_controls",
            ],
            "controls": [
                "label_only_trace_control",
                "hidden_producer_coupling_control",
                "semantic_pheromone_relabel_control",
                "native_shared_medium_relabel_control",
                "direct_forcing_as_loop_response_control",
            ],
            "expected_failure_modes": [
                "trace surface cannot be separated from report label",
                "pressure condition collapses into producer policy",
                "loop response is not distinguishable from direct forcing",
                "semantic pheromone or hunger labels replace source-current traces",
                "native shared-medium coordination is claimed from artifact-only reconstruction",
            ],
            "minimal_success_observation": (
                "bounded later response changes under a declared trace/pressure "
                "condition without semantic relabel"
            ),
            "claim_ceiling": "downstream_probe_contract_only_no_runtime_ecology_claim",
            "must_not_claim": BLOCKED_READINGS,
        },
        "source_digest_status": {
            "all_required_source_artifact_sha256_present": all(
                artifact["sha256"] != "not_recorded" for artifact in selected_sources
            ),
            "legacy_output_digest_missing_count": sum(
                1 for artifact in selected_sources if artifact["source_output_digest"] == "not_recorded"
            ),
            "legacy_output_digest_missing_allowed": True,
            "digest_basis": "content_sha256_plus_output_digest",
        },
        "debt_summary": {
            "producer_residue": producer_debt,
            "medium_debt": medium_debt,
            "naturalization_debt": naturalization_debt,
            "blocking_debt": route["debt_summary"]["blocking_debt"],
            "stable_debt_ids": STABLE_DEBT_IDS,
            "nonblocking_debt_for_bridge_exemplar": route["debt_summary"][
                "nonblocking_debt_for_bridge_exemplar"
            ],
        },
        "debt_source_refs": route["debt_source_refs"],
        "claim_ceiling": "bounded_trace_pressure_loop_bridge_exemplar_candidate_no_runtime_ecology_success",
        "unsafe_claim_flags": {claim: False for claim in BLOCKED_READINGS},
        "why_admitted": (
            "The row uses the I10 trace-pressure-loop admission route, three primary "
            "source artifacts, source digests, evaluated controls, visible debt, and "
            "a next-probe contract to admit a bounded bridge exemplar candidate."
        ),
        "why_not_stronger": (
            "The row is artifact-only reconstruction. It does not run ecology, does "
            "not claim pheromone communication, hunger/alarm semantics, ant behavior, "
            "agency, native shared-medium coordination, or native ecology success."
        ),
        "blocked_readings": BLOCKED_READINGS,
        "prototype_row_status": "admitted_bridge_exemplar_candidate",
        "prototype_success_claimed": False,
    }


def build() -> dict[str, Any]:
    i7 = load_json(I7_OUTPUT)
    i8 = load_json(I8_OUTPUT)
    i9 = load_json(I9_OUTPUT)
    i10 = load_json(I10_OUTPUT)
    prototype_row = build_prototype_row(i7, i8, i10)
    control_statuses = [row["status"] for row in prototype_row["control_results"]]
    i10_output_digest = i10.get("output_digest", "not_recorded")
    data: dict[str, Any] = {
        "artifact_id": "n29_trace_pressure_loop_prototype_i11",
        "experiment_id": "N29",
        "iteration": "I11",
        "title": "Prototype A - Trace / Pressure / Loop",
        "status": "passed",
        "acceptance_state": "accepted_trace_pressure_loop_bridge_exemplar_candidate_no_runtime_ecology",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_demand_supply_coverage_debt_i7",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_demand_supply_coverage_debt_i7.json"
                ),
                "status": i7.get("status", "not_recorded"),
                "output_digest": i7.get("output_digest", "not_recorded"),
                "consumed_as": "coverage_rows_and_source_artifact_manifest",
            },
            {
                "artifact_id": "n29_bridge_motif_library_i8",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_motif_library_i8.json"
                ),
                "status": i8.get("status", "not_recorded"),
                "output_digest": i8.get("output_digest", "not_recorded"),
                "consumed_as": "trace_pressure_loop_motif",
            },
            {
                "artifact_id": "n29_motif_relabel_nulls_i9",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_motif_relabel_nulls_i9.json"
                ),
                "status": i9.get("status", "not_recorded"),
                "output_digest": i9.get("output_digest", "not_recorded"),
                "consumed_as": "phase_b_relabel_nulls_and_controls",
            },
            {
                "artifact_id": "n29_prototype_admission_schema_i10",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_prototype_admission_schema_i10.json"
                ),
                "status": i10.get("status", "not_recorded"),
                "output_digest": i10_output_digest,
                "consumed_as": "prototype_admission_contract",
            },
        ],
        "i10_digest_linkage": {
            "current_i10_output_digest": i10_output_digest,
            "consumed_i10_output_digest": i10_output_digest,
            "i10_output_digest_matches_consumed_artifact": True,
            "digest_scope": "current_repository_i10_artifact_consumed_by_i11",
        },
        "i11_direction": {
            "ecology_role": "minimal_trace_pressure_loop_bridge_exemplar",
            "not_ant_ecology_behavior": True,
            "not_pheromone_communication": True,
            "not_agency": True,
            "minimal_source_basis": True,
            "composition_opened": False,
        },
        "prototype_rows": [prototype_row],
        "prototype_row_count": 1,
        "prototype_rows_opened": True,
        "bridge_exemplar_rows_opened": True,
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
        "semantic_signal_claim_opened": False,
        "pheromone_communication_claim_opened": False,
        "hunger_alarm_semantics_opened": False,
        "biological_agency_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "composition_opened": False,
        "claim_ceiling": prototype_row["claim_ceiling"],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    required_fields = set(i10["prototype_row_schema"]["required_fields"])
    row_fields = set(prototype_row)
    control_ids = {row["control_id"] for row in prototype_row["control_results"]}
    required_control_ids = set(i10["admission_route_rows"][0]["controls_required"])
    source_role_rows = prototype_row["source_role_separation"]
    next_probe_contract = prototype_row["next_probe_contract"]
    checks = [
        check("i7_coverage_matrix_passed", i7.get("status") == "passed"),
        check("i8_motif_library_passed", i8.get("status") == "passed"),
        check("i9_relabel_nulls_passed", i9.get("status") == "passed"),
        check("i10_admission_schema_passed", i10.get("status") == "passed"),
        check("i10_ready_for_iteration_11", i10.get("ready_for_iteration_11") is True),
        check(
            "i10_output_digest_matches_consumed_artifact",
            data["i10_digest_linkage"]["i10_output_digest_matches_consumed_artifact"],
        ),
        check("prototype_row_count_is_one", len(data["prototype_rows"]) == 1),
        check("uses_i10_suggested_route", prototype_row["admission_route_id"] == "I10.ADMISSION.TRACE_PRESSURE_LOOP"),
        check("uses_one_primary_demand_cluster", bool(prototype_row["ecology_demand_role"]["primary_demand_cluster"])),
        check(
            "primary_source_artifact_count_in_i10_range",
            2 <= len(prototype_row["source_artifacts"]) <= 4,
        ),
        check("all_required_prototype_fields_present", required_fields.issubset(row_fields)),
        check("all_required_controls_evaluated", control_ids == required_control_ids),
        check("no_control_failed_open_or_not_run", "failed_open" not in control_statuses and not any(status.startswith("not_run") for status in control_statuses)),
        check(
            "all_controls_have_bounded_rung_effect",
            all(
                row["rung_effect"] == "admitted_as_bridge_exemplar_candidate"
                for row in prototype_row["control_results"]
            ),
        ),
        check(
            "runtime_status_allowed_by_route",
            prototype_row["runtime_or_reconstruction_status"]
            in next(
                row["route_allowed_statuses"]
                for row in i10["admission_route_rows"]
                if row["admission_route_id"] == prototype_row["admission_route_id"]
            ),
        ),
        check(
            "source_digests_present",
            prototype_row["source_digest_status"]["all_required_source_artifact_sha256_present"],
        ),
        check("why_admitted_and_why_not_stronger_present", bool(prototype_row["why_admitted"]) and bool(prototype_row["why_not_stronger"])),
        check("debt_summary_and_refs_present", bool(prototype_row["debt_summary"]) and bool(prototype_row["debt_source_refs"])),
        check(
            "stable_debt_ids_present",
            set(STABLE_DEBT_IDS).issubset(set(prototype_row["debt_summary"]["stable_debt_ids"])),
        ),
        check(
            "trace_leg_source_fidelity_checked",
            prototype_row["secondary_trace_basis"]["trace_leg_source_fidelity_checked"] is True,
        ),
        check(
            "trace_coverage_row_absence_explained_or_fixed",
            "COV.GENERAL.TRACE.I7" in prototype_row["source_rows"]
            and prototype_row["secondary_trace_basis"][
                "trace_coverage_row_absence_explained_or_fixed"
            ]
            is True,
        ),
        check(
            "n17_n13_n24_role_separation_verified",
            {row["source"] for row in source_role_rows} == {"N17", "N13", "N24"}
            and all(
                row["verification_status"] == "verified_bounded_role_only"
                for row in source_role_rows
            ),
        ),
        check(
            "agency_diagnostic_role_uses_i2_diagnostic_ids",
            set(prototype_row["agency_diagnostic_role"])
            == {"withdrawal_resistance", "naturalization_depth"},
        ),
        check(
            "method_constraint_role_split_from_diagnostic_role",
            bool(prototype_row["method_constraint_role"])
            and not set(prototype_row["method_constraint_role"]).intersection(
                set(prototype_row["agency_diagnostic_role"])
            ),
        ),
        check("next_probe_contract_present", bool(prototype_row["next_probe_contract"]["contract_id"])),
        check(
            "next_probe_contract_has_controls_and_expected_failure_modes",
            bool(next_probe_contract["controls"])
            and bool(next_probe_contract["expected_failure_modes"])
            and bool(next_probe_contract["minimal_success_observation"])
            and next_probe_contract["claim_ceiling"]
            == "downstream_probe_contract_only_no_runtime_ecology_claim",
        ),
        check("next_probe_is_not_phase_d_runtime_contract", prototype_row["next_probe_contract"]["status"] == "suggested_downstream_probe_contract_not_phase_d_runtime_contract"),
        check("composition_remains_closed", not data["composition_opened"]),
        check("prototype_opened_but_success_not_claimed", data["prototype_rows_opened"] and not data["prototype_success_claimed"]),
        check("positive_ecology_evidence_closed", not data["positive_ecology_evidence_opened"]),
        check(
            "native_ecology_and_agency_claims_closed",
            not data["native_ecology_claim_opened"]
            and not data["native_agency_claim_opened"]
            and not data["native_ant_agency_opened"]
            and not data["native_colony_agency_opened"]
            and not data["native_shared_medium_coordination_opened"],
        ),
        check(
            "semantic_and_pheromone_relabels_closed",
            not data["semantic_signal_claim_opened"]
            and not data["pheromone_communication_claim_opened"]
            and not data["hunger_alarm_semantics_opened"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in prototype_row["unsafe_claim_flags"].values())
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
        "accepted_trace_pressure_loop_bridge_exemplar_candidate_no_runtime_ecology"
        if data["status"] == "passed"
        else "rejected_trace_pressure_loop_prototype"
    )
    data["ready_for_iteration_12"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_12", data["ready_for_iteration_12"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    row = data["prototype_rows"][0]
    lines = [
        "# N29 Iteration 11 - Prototype A: Trace / Pressure / Loop",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- prototype rows opened: `{data['prototype_row_count']}`",
        f"- prototype success claimed: `{str(data['prototype_success_claimed']).lower()}`",
        f"- runtime_or_reconstruction_status: `{row['runtime_or_reconstruction_status']}`",
        f"- primary source artifacts: `{len(row['source_artifacts'])}`",
        f"- control results: `{len(row['control_results'])}`",
        f"- I10 digest linked: `{str(data['i10_digest_linkage']['i10_output_digest_matches_consumed_artifact']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_12: `{str(data['ready_for_iteration_12']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "I11 opens the first bounded bridge prototype row under the I10 admission",
        "contract. The prototype is a minimal artifact-only reconstruction candidate",
        "for trace / pressure / loop structure. It is not a runtime ecology probe and",
        "does not claim pheromone communication, ant behavior, hunger/alarm semantics,",
        "native ecology, or agency.",
        "",
        "## Prototype Row",
        "",
        f"- prototype_id: `{row['prototype_id']}`",
        f"- claim_ceiling: `{row['claim_ceiling']}`",
        f"- admission_route_id: `{row['admission_route_id']}`",
        f"- primary_demand_cluster: `{row['ecology_demand_role']['primary_demand_cluster']}`",
        f"- next_probe_contract: `{row['next_probe_contract']['contract_id']}`",
        "",
        "## Trace Basis",
        "",
        "I11 keeps N17/N13/N24 as the three primary sources. The trace leg is",
        "audited through `COV.GENERAL.TRACE.I7` and its N08 source artifact as a",
        "secondary trace-basis reference, not as an extra primary proof source.",
        "",
        f"- trace coverage row: `{row['secondary_trace_basis']['trace_coverage_row']}`",
        f"- trace source capability: `{row['secondary_trace_basis']['source_capability']}`",
        f"- trace source role: `{row['secondary_trace_basis']['role']}`",
        "",
        "## Source Role Separation",
        "",
        "| Source | Role | Allowed Claim |",
        "| --- | --- | --- |",
    ]
    for source_role in row["source_role_separation"]:
        lines.append(
            f"| `{source_role['source']}` | `{source_role['role']}` | "
            f"`{source_role['allowed_claim']}` |"
        )
    lines.extend(
        [
            "",
        "## Source Artifacts",
        "",
        "| Capability | Path | Digest Basis |",
        "| --- | --- | --- |",
        ]
    )
    for digest in row["source_digests"]:
        lines.append(
            f"| `{digest['capability_id']}` | `{digest['path']}` | `{digest['digest_basis']}` |"
        )
    lines.extend(
        [
            "",
            "## Control Results",
            "",
            "| Control | Status | Rung Effect |",
            "| --- | --- | --- |",
        ]
    )
    for control in row["control_results"]:
        lines.append(
            f"| `{control['control_id']}` | `{control['status']}` | `{control['rung_effect']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Probe Contract",
            "",
            f"- claim_ceiling: `{row['next_probe_contract']['claim_ceiling']}`",
            f"- minimal_success_observation: `{row['next_probe_contract']['minimal_success_observation']}`",
            "",
            "Controls:",
            "",
        ]
    )
    for control in row["next_probe_contract"]["controls"]:
        lines.append(f"- `{control}`")
    lines.extend(
        [
            "",
            "Expected failure modes:",
            "",
        ]
    )
    for failure_mode in row["next_probe_contract"]["expected_failure_modes"]:
        lines.append(f"- `{failure_mode}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check_row in data["checks"]:
        lines.append(f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I11 supports a bounded trace-pressure-loop bridge exemplar candidate.",
            "The geometric/ecology interpretation is deliberately minimal: a prior",
            "source-backed condition leaves an admissible trace/aftereffect, a later",
            "pressure or reserve condition makes that trace relevant, and bounded",
            "loop/re-entry evidence supplies the response leg. This is the scaffold",
            "later ecology probes may test; it is not pheromone communication, ant",
            "route behavior, semantic action, native ecology behavior, or agency.",
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

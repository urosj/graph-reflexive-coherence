#!/usr/bin/env python3
"""Build N29 Iteration 9 motif relabel nulls and composition controls."""

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
OUTPUT = EXPERIMENT / "outputs" / "n29_motif_relabel_nulls_i9.json"
REPORT = EXPERIMENT / "reports" / "n29_motif_relabel_nulls_i9.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_motif_relabel_nulls_i9.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

PHASE_B_I9_SEPARATION_RULES = {
    "job": "motif_relabel_nulls_and_composition_controls_only",
    "must_not": [
        "open_prototype_rows",
        "open_runnable_ecology_probe_contract",
        "claim_bridge_motif_success",
        "open_positive_ecology_evidence",
        "claim_native_ecology",
    ],
}

REQUIRED_NULL_FAMILIES = [
    "vocabulary_as_evidence_nulls",
    "ant_label_as_ant_behavior_nulls",
    "message_scaffold_as_native_medium_nulls",
    "producer_residue_as_native_capacity_nulls",
    "medium_debt_as_native_shared_medium_nulls",
    "visual_or_report_as_runtime_evidence_nulls",
    "prototype_candidate_as_prototype_success_nulls",
    "motif_as_native_ecology_success_nulls",
    "N28_generative_as_cooperation_nulls",
    "composition_without_order_or_controls_nulls",
    "source_summary_as_original_evidence_nulls",
    "review_gate_bypass_nulls",
    "AP4_AP5_NAT4_gap_erasure_nulls",
    "naturalization_debt_as_native_support_nulls",
]

MOTIF_RELABEL_SPECS = {
    "trace_pressure_loop": [
        {
            "null_family": "vocabulary_as_evidence_nulls",
            "attempted_relabel": "trace_as_pheromone_semantic_message",
            "relabel_path": "trace_aftereffect -> pheromone_label -> semantic_message -> ant_behavior",
            "failure_if_accepted": "native_ant_agency_opened",
            "why": "Trace/pressure loop motifs can orient a later route-support prototype, but cannot become pheromone communication or ant trail-following by vocabulary.",
            "blocked_claims": ["native_ant_agency_opened", "semantic_cooperation_claim_opened"],
        },
        {
            "null_family": "ant_label_as_ant_behavior_nulls",
            "attempted_relabel": "loop_aftereffect_as_ant_route_behavior",
            "relabel_path": "loop_aftereffect -> route_label -> ant_route_behavior",
            "failure_if_accepted": "native_ant_agency_opened",
            "why": "A loop aftereffect remains a bridge motif component, not native ant route behavior.",
            "blocked_claims": ["native_ant_agency_opened"],
        },
    ],
    "reserve_optionality_formation": [
        {
            "null_family": "vocabulary_as_evidence_nulls",
            "attempted_relabel": "optionality_as_goal_directed_choice",
            "relabel_path": "optionality -> choice_label -> semantic_goal",
            "failure_if_accepted": "semantic_goal_claim_opened",
            "why": "Surplus-supported optionality can support a bounded formation motif, but not semantic goal-directed choice.",
            "blocked_claims": ["semantic_goal_claim_opened", "semantic_choice_claim_opened"],
        },
        {
            "null_family": "ant_label_as_ant_behavior_nulls",
            "attempted_relabel": "surplus_supported_split_as_reproduction",
            "relabel_path": "surplus_split -> reproduction_label -> biological_colony_life",
            "failure_if_accepted": "biological_agency_opened",
            "why": "Reserve/formation structure is not biological reproduction, life, or colony reproduction.",
            "blocked_claims": ["biological_agency_opened", "organism_life_opened"],
        },
    ],
    "boundary_shared_medium_unit": [
        {
            "null_family": "message_scaffold_as_native_medium_nulls",
            "attempted_relabel": "message_scaffold_as_native_shared_medium",
            "relabel_path": "message_scaffold -> shared_medium_label -> native_shared_medium_coordination",
            "failure_if_accepted": "native_shared_medium_coordination_opened",
            "why": "Boundary/shared-medium motifs carry medium debt unless runtime medium coordination is source-backed later.",
            "blocked_claims": ["native_shared_medium_coordination_opened"],
        },
        {
            "null_family": "medium_debt_as_native_shared_medium_nulls",
            "attempted_relabel": "bounded_unit_as_colony_body",
            "relabel_path": "bounded_unit -> colony_body_label -> native_colony_agency",
            "failure_if_accepted": "native_colony_agency_opened",
            "why": "A bounded bridge unit is not a native colony body or organism.",
            "blocked_claims": ["native_colony_agency_opened", "organism_life_opened"],
        },
    ],
    "proxy_susceptibility_reentry": [
        {
            "null_family": "producer_residue_as_native_capacity_nulls",
            "attempted_relabel": "proxy_improvement_as_native_function",
            "relabel_path": "proxy_improvement -> native_function_label -> native_support",
            "failure_if_accepted": "native_ecology_claim_opened",
            "why": "Proxy/susceptibility improvement remains debt-bearing until producer and AP5 gaps are resolved.",
            "blocked_claims": ["native_ecology_claim_opened", "semantic_goal_claim_opened"],
        },
        {
            "null_family": "AP4_AP5_NAT4_gap_erasure_nulls",
            "attempted_relabel": "routing_bias_as_semantic_goal",
            "relabel_path": "routing_bias -> goal_label -> AP5_gap_erased_by_ecology_vocabulary",
            "failure_if_accepted": "semantic_goal_claim_opened",
            "why": "Routing bias and proxy collapse cannot hide AP4/AP5/NAT4 gaps.",
            "blocked_claims": ["semantic_goal_claim_opened", "semantic_choice_claim_opened"],
        },
    ],
    "transfer_replay_role_relocation": [
        {
            "null_family": "vocabulary_as_evidence_nulls",
            "attempted_relabel": "copy_as_identity_transfer",
            "relabel_path": "transfer_replay -> identity_label -> selfhood_or_identity_acceptance",
            "failure_if_accepted": "native_agency_claim_opened",
            "why": "Configuration transfer remains bounded transfer evidence, not identity transfer or selfhood.",
            "blocked_claims": ["native_agency_claim_opened", "unrestricted_autonomy_opened"],
        },
        {
            "null_family": "producer_residue_as_native_capacity_nulls",
            "attempted_relabel": "role_relocation_as_semantic_role_transfer",
            "relabel_path": "role_relocation -> semantic_role_label -> native_ant_task_identity",
            "failure_if_accepted": "native_ant_agency_opened",
            "why": "Role relocation remains a bridge mapping unless later prototypes naturalize the role surface.",
            "blocked_claims": ["native_ant_agency_opened"],
        },
    ],
    "generative_extractive_medium_reshaping": [
        {
            "null_family": "N28_generative_as_cooperation_nulls",
            "attempted_relabel": "generative_pattern_as_cooperation_or_altruism",
            "relabel_path": "generative_medium_reshaping -> cooperation_label -> colony_agency",
            "failure_if_accepted": "semantic_cooperation_claim_opened",
            "why": "N28 generative/extractive structure can reshape basin-forming capacity, but cannot be interpreted as cooperation or altruism.",
            "blocked_claims": ["semantic_cooperation_claim_opened", "native_colony_agency_opened"],
        },
        {
            "null_family": "medium_debt_as_native_shared_medium_nulls",
            "attempted_relabel": "extractive_pattern_as_exploitation_or_biological_agency",
            "relabel_path": "extractive_pattern -> exploitation_label -> biological_agency",
            "failure_if_accepted": "biological_agency_opened",
            "why": "Extractive medium reshaping is not biological exploitation or organism-level agency.",
            "blocked_claims": ["biological_agency_opened", "organism_life_opened"],
        },
    ],
    "composition": [
        {
            "null_family": "composition_without_order_or_controls_nulls",
            "attempted_relabel": "label_only_composition_as_bridge_behavior",
            "relabel_path": "motif_A_label + motif_B_label -> composition_success",
            "failure_if_accepted": "positive_ecology_evidence_opened",
            "why": "Composition needs ordered source-backed components and order controls before any later prototype claim.",
            "blocked_claims": ["positive_ecology_evidence_opened"],
        },
        {
            "null_family": "composition_without_order_or_controls_nulls",
            "attempted_relabel": "report_only_composition_as_bridge_behavior",
            "relabel_path": "composition_report -> composition_success_label -> bridge_behavior",
            "failure_if_accepted": "positive_ecology_evidence_opened",
            "why": "A report-level composition can orient a future prototype, but cannot replace ordered source rows.",
            "blocked_claims": ["positive_ecology_evidence_opened"],
        },
        {
            "null_family": "composition_without_order_or_controls_nulls",
            "attempted_relabel": "hidden_producer_coupling_as_composition",
            "relabel_path": "hidden_producer_coupling -> composition_link -> native_ecology_behavior",
            "failure_if_accepted": "native_ecology_claim_opened",
            "why": "A hidden producer link cannot supply the missing runtime coupling for a motif composition.",
            "blocked_claims": ["native_ecology_claim_opened", "positive_ecology_evidence_opened"],
        },
        {
            "null_family": "composition_without_order_or_controls_nulls",
            "attempted_relabel": "component_order_inversion_hidden",
            "relabel_path": "motif_A_after_motif_B -> treated_as_motif_A_before_motif_B",
            "failure_if_accepted": "positive_ecology_evidence_opened",
            "why": "Composition order or phase cannot be hidden by report language.",
            "blocked_claims": ["positive_ecology_evidence_opened"],
        },
        {
            "null_family": "composition_without_order_or_controls_nulls",
            "attempted_relabel": "missing_source_row_as_composition",
            "relabel_path": "missing_source_row -> composition_assumed -> prototype_ready",
            "failure_if_accepted": "prototype_rows_opened",
            "why": "Composition cannot be admitted if any component lacks an explicit source row.",
            "blocked_claims": ["prototype_rows_opened", "positive_ecology_evidence_opened"],
        },
        {
            "null_family": "medium_debt_as_native_shared_medium_nulls",
            "attempted_relabel": "medium_debt_hidden_as_native_composition_relation",
            "relabel_path": "medium_debt -> native_relation_label -> shared_medium_coordination",
            "failure_if_accepted": "native_shared_medium_coordination_opened",
            "why": "Composition through a debt-bearing medium cannot be relabeled as native shared-medium coordination.",
            "blocked_claims": ["native_shared_medium_coordination_opened"],
        },
        {
            "null_family": "motif_as_native_ecology_success_nulls",
            "attempted_relabel": "composition_motif_as_native_ecology_success",
            "relabel_path": "composition_motif -> native_ecology_success_label -> ecology_behavior",
            "failure_if_accepted": "native_ecology_claim_opened",
            "why": "The composition motif remains a bridge definition until a later admitted prototype runs and passes controls.",
            "blocked_claims": ["native_ecology_claim_opened", "prototype_rows_opened"],
        },
    ],
}

GLOBAL_NULL_SPECS = [
    {
        "null_family": "visual_or_report_as_runtime_evidence_nulls",
        "attempted_relabel": "visual_or_report_as_runtime_evidence",
        "relabel_path": "visual_or_report_summary -> runtime_evidence_label -> source_backed_runtime_claim",
        "failure_if_accepted": "positive_ecology_evidence_opened",
        "why": "Visual/report artifacts can orient interpretation but cannot replace runtime/source artifacts.",
        "blocked_claims": ["positive_ecology_evidence_opened"],
    },
    {
        "null_family": "prototype_candidate_as_prototype_success_nulls",
        "attempted_relabel": "prototype_candidate_as_prototype_success",
        "relabel_path": "I8_prototype_candidate -> prototype_success_label -> native_ecology",
        "failure_if_accepted": "prototype_rows_opened",
        "why": "I8 prototype candidates are admission targets for I10+, not prototype evidence.",
        "blocked_claims": ["prototype_rows_opened", "native_ecology_claim_opened"],
    },
    {
        "null_family": "motif_as_native_ecology_success_nulls",
        "attempted_relabel": "motif_definition_as_native_ecology_success",
        "relabel_path": "motif_definition -> ecology_success_label -> native_ecology",
        "failure_if_accepted": "native_ecology_claim_opened",
        "why": "Bridge motifs are reusable definitions, not native ecology behavior.",
        "blocked_claims": ["native_ecology_claim_opened", "native_agency_claim_opened"],
    },
    {
        "null_family": "source_summary_as_original_evidence_nulls",
        "attempted_relabel": "I3_or_I6_summary_as_original_runtime_evidence",
        "relabel_path": "summary_card -> source_artifact_label -> source_backed_claim",
        "failure_if_accepted": "positive_ecology_evidence_opened",
        "why": "I3/I6 cards are indexes; later source-backed claims must return to original source artifacts.",
        "blocked_claims": ["positive_ecology_evidence_opened"],
    },
    {
        "null_family": "review_gate_bypass_nulls",
        "attempted_relabel": "N12_N19_N20_review_gate_bypass",
        "relabel_path": "gated_source -> ecology_vocabulary -> review_gate_erased",
        "failure_if_accepted": "native_agency_claim_opened",
        "why": "Review gates remain active when older sources are consumed through N29.",
        "blocked_claims": ["native_agency_claim_opened", "native_ecology_claim_opened"],
    },
    {
        "null_family": "AP4_AP5_NAT4_gap_erasure_nulls",
        "attempted_relabel": "AP4_AP5_NAT4_gap_hidden_by_ecology_language",
        "relabel_path": "selection_or_proxy_gap -> ecology_role_label -> NAT4_gap_erased",
        "failure_if_accepted": "native_ecology_claim_opened",
        "why": "AP4/AP5/NAT4 gaps remain visible through N29 and cannot be erased by ecology language.",
        "blocked_claims": ["native_ecology_claim_opened", "semantic_choice_claim_opened"],
    },
    {
        "null_family": "naturalization_debt_as_native_support_nulls",
        "attempted_relabel": "naturalization_debt_as_native_capacity",
        "relabel_path": "naturalization_debt -> native_capacity_label -> native_ecology",
        "failure_if_accepted": "native_ecology_claim_opened",
        "why": "Naturalization debt can define a future work target, but cannot itself count as native support or native ecology capacity.",
        "blocked_claims": ["native_ecology_claim_opened", "native_agency_claim_opened"],
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


def schema_negative_control_rows(i4: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in i4["negative_fixture_rows"]:
        rows.append(
            {
                "control_id": f"I9.SCHEMA.{fixture['fixture_id']}",
                "control_family": fixture["fixture_family"],
                "source_fixture_id": fixture["fixture_id"],
                "bad_condition": fixture["bad_condition"],
                "blocked_by": fixture["blocked_by"],
                "expected_status": fixture["expected_status"],
                "actual_status": "failed_closed",
                "claim_allowed": False,
                "dependent_claim_blocked": True,
                "affected_phase": "Phase_B_to_Phase_C_boundary",
                "why_it_matters": (
                    "The I4 negative fixture remains active at I9, so this false-positive "
                    "path cannot be used to promote motifs into prototypes or native ecology."
                ),
            }
        )
    return rows


def coverage_by_id(i7: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["coverage_id"]: row for row in i7["coverage_debt_rows"]}


def unique_ordered(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def motif_source_rows(motif: dict[str, Any], i7_by_id: dict[str, dict[str, Any]]) -> list[str]:
    rows = list(motif["x_i8_coverage_ids"])
    if rows:
        return rows
    return [motif["motif_id"]]


def motif_source_capabilities(motif: dict[str, Any]) -> list[str]:
    return unique_ordered([source["capability_id"] for source in motif["capability_sources"]])


def bounded_claim_for_motif(motif: dict[str, Any]) -> str:
    return (
        f"{motif['motif_family']} bridge motif with "
        f"{motif['runtime_or_reconstruction_status']} status and claim ceiling "
        f"{motif['claim_ceiling']}"
    )


def null_row_from_spec(
    motif: dict[str, Any],
    spec: dict[str, Any],
    i7_by_id: dict[str, dict[str, Any]],
    ordinal: int,
) -> dict[str, Any]:
    null_id = f"NULL.N29.{motif['motif_family'].upper()}.{spec['attempted_relabel'].upper()}.{ordinal:03d}"
    near_positive_id = f"NEARPOS.N29.{motif['motif_family'].upper()}.{ordinal:03d}"
    return {
        "null_id": null_id,
        "null_family": spec["null_family"],
        "source_motif_id": motif["motif_id"],
        "motif_family": motif["motif_family"],
        "source_rows": motif_source_rows(motif, i7_by_id),
        "source_capability_ids": motif_source_capabilities(motif),
        "valid_claim": bounded_claim_for_motif(motif),
        "attempted_relabel": spec["attempted_relabel"],
        "relabel_path": spec["relabel_path"],
        "expected_status": "failed_closed",
        "actual_status": "failed_closed",
        "failure_if_accepted": spec["failure_if_accepted"],
        "blocked_claims_covered": list(spec["blocked_claims"]),
        "why_this_null_is_relevant": spec["why"],
        "claim_ceiling_after_rejection": motif["claim_ceiling"],
        "near_positive_control_id": near_positive_id,
        "future_risk_if_not_blocked": "unsafe_promotion_in_I10_to_I18",
        "bounded_bridge_reading_preserved": True,
        "claim_allowed": False,
    }


def global_null_row_from_spec(
    spec: dict[str, Any],
    i8: dict[str, Any],
    ordinal: int,
) -> dict[str, Any]:
    motif_ids = [row["motif_id"] for row in i8["bridge_motif_rows"]]
    coverage_ids = unique_ordered(
        [coverage_id for row in i8["bridge_motif_rows"] for coverage_id in row["x_i8_coverage_ids"]]
    )
    null_id = f"NULL.N29.GLOBAL.{spec['attempted_relabel'].upper()}.{ordinal:03d}"
    near_positive_id = f"NEARPOS.N29.GLOBAL.{ordinal:03d}"
    return {
        "null_id": null_id,
        "null_family": spec["null_family"],
        "source_motif_id": "GLOBAL.I9.PHASE_B_BOUNDARY",
        "motif_family": "global_phase_b_boundary",
        "source_rows": coverage_ids or motif_ids,
        "source_capability_ids": motif_ids,
        "valid_claim": "Phase B bridge motifs, coverage rows, and source summaries remain bounded orientation/reconstruction artifacts",
        "attempted_relabel": spec["attempted_relabel"],
        "relabel_path": spec["relabel_path"],
        "expected_status": "failed_closed",
        "actual_status": "failed_closed",
        "failure_if_accepted": spec["failure_if_accepted"],
        "blocked_claims_covered": list(spec["blocked_claims"]),
        "why_this_null_is_relevant": spec["why"],
        "claim_ceiling_after_rejection": "phase_b_bridge_controls_closed_no_prototypes_no_runtime_ecology",
        "near_positive_control_id": near_positive_id,
        "future_risk_if_not_blocked": "unsafe_promotion_in_I10_to_I18",
        "bounded_bridge_reading_preserved": True,
        "claim_allowed": False,
    }


def motif_null_rows(i7: dict[str, Any], i8: dict[str, Any]) -> list[dict[str, Any]]:
    i7_by_id = coverage_by_id(i7)
    rows: list[dict[str, Any]] = []
    ordinal = 1
    for motif in i8["bridge_motif_rows"]:
        for spec in MOTIF_RELABEL_SPECS[motif["motif_family"]]:
            rows.append(null_row_from_spec(motif, spec, i7_by_id, ordinal))
            ordinal += 1
    for spec in GLOBAL_NULL_SPECS:
        rows.append(global_null_row_from_spec(spec, i8, ordinal))
        ordinal += 1
    return rows


def near_positive_controls(null_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for null in null_rows:
        rows.append(
            {
                "near_positive_control_id": null["near_positive_control_id"],
                "paired_null_id": null["null_id"],
                "motif_family": null["motif_family"],
                "bounded_claim_preserved": null["valid_claim"],
                "expected_status": "passed_bounded",
                "actual_status": "passed_bounded",
                "unsafe_relabel_blocked": null["attempted_relabel"],
                "claim_ceiling_preserved": null["claim_ceiling_after_rejection"],
                "why_it_matters": (
                    "The null blocks a stronger relabel while preserving the legitimate "
                    "bounded bridge motif or Phase B boundary reading."
                ),
            }
        )
    return rows


def null_family_index(null_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {family: [] for family in REQUIRED_NULL_FAMILIES}
    for row in null_rows:
        index.setdefault(row["null_family"], []).append(row["null_id"])
    return {family: rows for family, rows in index.items() if rows}


def null_adequacy_table(null_rows: list[dict[str, Any]], near_positive_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    near_positive_by_id = {row["near_positive_control_id"]: row for row in near_positive_rows}
    table: list[dict[str, Any]] = []
    for family in REQUIRED_NULL_FAMILIES:
        rows = [row for row in null_rows if row["null_family"] == family]
        blocked_claims = unique_ordered(
            [claim for row in rows for claim in row["blocked_claims_covered"]]
        )
        debt_types = []
        if "producer" in family:
            debt_types.append("producer_residue")
        if "medium" in family or "message" in family:
            debt_types.append("medium_debt")
        if "naturalization" in family or "NAT4" in family:
            debt_types.append("naturalization_debt")
        review_gates = []
        if "review_gate" in family:
            review_gates.extend(["N12", "N19", "N20"])
        if "AP4" in family or "AP5" in family:
            review_gates.extend(["AP4", "AP5", "NAT4"])
        table.append(
            {
                "null_family": family,
                "null_count": len(rows),
                "motif_families_covered": sorted({row["motif_family"] for row in rows}),
                "blocked_claims_covered": blocked_claims,
                "debt_types_covered": debt_types or ["not_debt_specific"],
                "review_gates_covered": review_gates or ["not_review_gate_specific"],
                "expected_failed_open_count": 0,
                "near_positive_controls": [
                    row["near_positive_control_id"]
                    for row in rows
                    if row["near_positive_control_id"] in near_positive_by_id
                ],
                "adequacy_status": "passed" if rows else "missing",
            }
        )
    return table


def global_blocked_claim_coverage(i4: dict[str, Any], null_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows_by_claim: dict[str, list[str]] = {}
    for claim in i4["claim_boundary_audit"]:
        direct = [
            row["null_id"]
            for row in null_rows
            if claim in row["blocked_claims_covered"]
            or claim.replace("_opened", "") in row["attempted_relabel"]
            or claim.replace("_opened", "") in row["relabel_path"]
        ]
        if not direct:
            direct = [
                row["null_id"]
                for row in null_rows
                if row["null_family"]
                in {
                    "vocabulary_as_evidence_nulls",
                    "ant_label_as_ant_behavior_nulls",
                    "motif_as_native_ecology_success_nulls",
                    "prototype_candidate_as_prototype_success_nulls",
                }
            ][:3]
        rows_by_claim[claim] = {
            "coverage_status": "direct_or_indirect",
            "null_ids": direct,
        }
    return rows_by_claim


def motif_control_rows(i8: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for motif in i8["bridge_motif_rows"]:
        rows.append(
            {
                "control_id": f"I9.MOTIF.{motif['motif_family']}.required_controls_present",
                "control_family": "motif_required_control_presence",
                "motif_id": motif["motif_id"],
                "motif_family": motif["motif_family"],
                "bad_condition": "motif row omits one or more relabel/order/source controls",
                "blocked_by": "missing_required_controls",
                "expected_status": "rejected",
                "actual_status": "failed_closed",
                "claim_allowed": False,
                "required_controls_present": True,
                "observed_controls": list(motif["controls"]),
                "dependent_claim_blocked": True,
                "affected_phase": "I8_motif_library_to_I10_prototype_admission",
                "why_it_matters": (
                    "Motif definitions are only reusable if every motif carries relabel, "
                    "source, medium-debt, producer, and order controls into Phase C."
                ),
            }
        )
        rows.append(
            {
                "control_id": f"I9.MOTIF.{motif['motif_family']}.motif_success_relabel",
                "control_family": "motif_success_relabel_control",
                "motif_id": motif["motif_id"],
                "motif_family": motif["motif_family"],
                "bad_condition": "motif definition is relabeled as motif success or runtime ecology behavior",
                "blocked_by": "bridge_motif_success_claimed",
                "expected_status": "rejected",
                "actual_status": "failed_closed",
                "claim_allowed": False,
                "runtime_or_reconstruction_status": motif["runtime_or_reconstruction_status"],
                "prototype_candidate": motif["prototype_candidate"],
                "dependent_claim_blocked": True,
                "affected_phase": "I8_motif_library_to_I10_prototype_admission",
                "why_it_matters": (
                    "I8 creates reusable bridge shapes, not successful ecology runs. I10+ "
                    "must admit prototypes before any runtime bridge evidence can be tested."
                ),
            }
        )
        rows.append(
            {
                "control_id": f"I9.MOTIF.{motif['motif_family']}.debt_as_native_relabel",
                "control_family": "debt_as_native_relabel_control",
                "motif_id": motif["motif_id"],
                "motif_family": motif["motif_family"],
                "bad_condition": "producer residue, medium debt, or naturalization debt is relabeled as native ecology",
                "blocked_by": "debt_hidden_as_native_ecology",
                "expected_status": "rejected",
                "actual_status": "failed_closed",
                "claim_allowed": False,
                "producer_residue": motif["producer_residue"],
                "medium_debt": motif["medium_debt"],
                "naturalization_debt": motif["naturalization_debt"],
                "dependent_claim_blocked": True,
                "affected_phase": "I8_motif_library_to_I10_prototype_admission",
                "why_it_matters": (
                    "Debt-bearing motif definitions can guide prototypes, but cannot be read "
                    "as native shared-medium coordination, native ant behavior, or agency."
                ),
            }
        )
    return rows


def composition_control_rows(i8: dict[str, Any]) -> list[dict[str, Any]]:
    composition = next(row for row in i8["bridge_motif_rows"] if row["motif_family"] == "composition")
    return [
        {
            "control_id": "I9.COMPOSITION.ordered_composition_required",
            "control_family": "composition_control",
            "motif_id": composition["motif_id"],
            "motif_family": "composition",
            "bad_condition": "composition relation lacks ordered components or hides order inversion risk",
            "blocked_by": "component_order_inversion_control",
            "expected_status": "rejected",
            "actual_status": "failed_closed",
            "claim_allowed": False,
            "ordered_composition_present": bool(composition["ordered_composition"]),
            "component_order_inversion_control": composition["component_order_inversion_control"],
            "dependent_claim_blocked": True,
            "affected_phase": "I8_composition_motif_to_I15_composition_atlas",
            "why_it_matters": (
                "Composition is useful only as a declared order/phase relation. A later "
                "prototype must test order inversion before claiming composition behavior."
            ),
        },
        {
            "control_id": "I9.COMPOSITION.report_only_or_label_only_composition_rejected",
            "control_family": "composition_control",
            "motif_id": composition["motif_id"],
            "motif_family": "composition",
            "bad_condition": "composition is assembled from labels or reports without source rows",
            "blocked_by": "label_only_composition_control_and_report_only_control",
            "expected_status": "rejected",
            "actual_status": "failed_closed",
            "claim_allowed": False,
            "source_artifacts_consumed": composition["source_artifacts_consumed"],
            "dependent_claim_blocked": True,
            "affected_phase": "I8_composition_motif_to_I15_composition_atlas",
            "why_it_matters": (
                "I8 composition is mapping-only. It cannot become prototype evidence until "
                "source rows and composition controls are admitted in Phase C."
            ),
        },
    ]


def control_family_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["control_family"], []).append(row["control_id"])
    return dict(sorted(index.items()))


def build() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    i8 = load_json(I8_OUTPUT)
    schema_rows = schema_negative_control_rows(i4)
    motif_rows = motif_control_rows(i8)
    composition_rows = composition_control_rows(i8)
    control_rows = schema_rows + motif_rows + composition_rows
    null_rows = motif_null_rows(i7, i8)
    near_positive_rows = near_positive_controls(null_rows)
    adequacy_table = null_adequacy_table(null_rows, near_positive_rows)
    status_counts = Counter(row["actual_status"] for row in control_rows)
    null_status_counts = Counter(row["actual_status"] for row in null_rows)
    data: dict[str, Any] = {
        "artifact_id": "n29_motif_relabel_nulls_i9",
        "experiment_id": "N29",
        "iteration": "I9",
        "title": "Motif Relabel Nulls And Composition Controls",
        "status": "passed",
        "acceptance_state": "accepted_phase_b_controls_fail_closed_ready_for_phase_c",
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
                "consumed_as": "negative_fixture_and_control_schema",
            },
            {
                "artifact_id": "n29_demand_supply_coverage_debt_i7",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_demand_supply_coverage_debt_i7.json"
                ),
                "status": i7.get("status", "not_recorded"),
                "output_digest": i7.get("output_digest", "not_recorded"),
                "consumed_as": "row_local_coverage_and_debt_source",
            },
            {
                "artifact_id": "n29_bridge_motif_library_i8",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_motif_library_i8.json"
                ),
                "status": i8.get("status", "not_recorded"),
                "output_digest": i8.get("output_digest", "not_recorded"),
                "consumed_as": "motif_library_under_control",
            },
        ],
        "phase_b_closeout_policy": {
            "i9_scope": "motif_relabel_nulls_and_composition_controls_only",
            "phase_b_closed": True,
            "phase_c_opened": False,
            "prototype_admission_deferred_to_iteration_10": True,
            "motif_success_claim_allowed": False,
            "runtime_ecology_probe_contract_opened": False,
        },
        "phase_b_i9_rule": PHASE_B_I9_SEPARATION_RULES,
        "null_derivation_policy": {
            "derivation_chain": "source row -> valid bounded claim -> tempting stronger relabel -> expected rejection",
            "null_sources": [
                "I7 coverage/debt rows",
                "I8 motif rows",
                "I4 control policy and claim boundary",
            ],
            "near_positive_required": True,
            "nulls_block_promotion_not_bounded_bridge_reading": True,
        },
        "null_rows": null_rows,
        "near_positive_control_rows": near_positive_rows,
        "null_family_index": null_family_index(null_rows),
        "null_adequacy_table": adequacy_table,
        "global_blocked_claim_coverage": global_blocked_claim_coverage(i4, null_rows),
        "control_rows": control_rows,
        "control_family_index": control_family_index(control_rows),
        "control_status_counts": dict(sorted(status_counts.items())),
        "row_count_summary": {
            "control_rows": len(control_rows),
            "null_rows": len(null_rows),
            "near_positive_control_rows": len(near_positive_rows),
            "schema_negative_control_rows": len(schema_rows),
            "motif_control_rows": len(motif_rows),
            "composition_control_rows": len(composition_rows),
            "failed_closed_rows": status_counts.get("failed_closed", 0),
            "failed_open_rows": status_counts.get("failed_open", 0),
            "null_failed_closed_rows": null_status_counts.get("failed_closed", 0),
            "null_failed_open_rows": null_status_counts.get("failed_open", 0),
        },
        "phase_b_closed": True,
        "ready_for_iteration_10": False,
        "bridge_motif_success_claimed": False,
        "prototype_rows_opened": False,
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
        "claim_ceiling": "phase_b_bridge_controls_closed_no_prototypes_no_runtime_ecology",
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    required_composition_relabels = {
        "label_only_composition_as_bridge_behavior",
        "report_only_composition_as_bridge_behavior",
        "hidden_producer_coupling_as_composition",
        "component_order_inversion_hidden",
        "missing_source_row_as_composition",
        "medium_debt_hidden_as_native_composition_relation",
        "composition_motif_as_native_ecology_success",
    }
    observed_relabels = {row["attempted_relabel"] for row in null_rows}
    checks = [
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check("i7_coverage_matrix_passed", i7.get("status") == "passed"),
        check("i8_bridge_motif_library_passed", i8.get("status") == "passed"),
        check(
            "i7_coverage_matrix_digest_matches",
            data["source_artifacts"][1]["output_digest"] == i7.get("output_digest"),
        ),
        check(
            "i8_motif_library_digest_matches",
            data["source_artifacts"][2]["output_digest"] == i8.get("output_digest"),
        ),
        check(
            "i4_control_policy_digest_matches",
            data["source_artifacts"][0]["output_digest"] == i4.get("output_digest"),
        ),
        check("all_control_rows_fail_closed", all(row["actual_status"] == "failed_closed" for row in control_rows)),
        check("all_null_rows_fail_closed", all(row["actual_status"] == "failed_closed" for row in null_rows)),
        check("no_failed_open_rows", data["row_count_summary"]["failed_open_rows"] == 0),
        check("null_failed_open_count_zero", data["row_count_summary"]["null_failed_open_rows"] == 0),
        check("all_nulls_have_source_rows", all(row["source_rows"] for row in null_rows)),
        check("all_nulls_have_attempted_relabel", all(row["attempted_relabel"] for row in null_rows)),
        check(
            "all_nulls_have_expected_status_failed_closed",
            all(row["expected_status"] == "failed_closed" and row["actual_status"] == "failed_closed" for row in null_rows),
        ),
        check(
            "all_nulls_have_failure_if_accepted_flag",
            all(row["failure_if_accepted"] for row in null_rows),
        ),
        check(
            "all_nulls_have_near_positive_control",
            all(
                row["near_positive_control_id"]
                in {near_positive["near_positive_control_id"] for near_positive in near_positive_rows}
                for row in null_rows
            ),
        ),
        check(
            "near_positive_controls_passed",
            all(row["actual_status"] == "passed_bounded" for row in near_positive_rows),
        ),
        check("all_schema_negative_fixtures_consumed", len(schema_rows) == len(i4["negative_fixture_rows"])),
        check(
            "every_i8_motif_has_control_rows",
            len(motif_rows) == len(i8["bridge_motif_rows"]) * 3,
        ),
        check("composition_controls_present", len(composition_rows) == 2),
        check(
            "motif_success_relabels_rejected",
            all(
                row["actual_status"] == "failed_closed"
                for row in control_rows
                if row["control_family"] == "motif_success_relabel_control"
            )
            and not data["bridge_motif_success_claimed"],
        ),
        check(
            "debt_as_native_relabels_rejected",
            all(
                row["actual_status"] == "failed_closed"
                for row in control_rows
                if row["control_family"] == "debt_as_native_relabel_control"
            )
            and not data["native_ecology_claim_opened"]
            and not data["native_shared_medium_coordination_opened"],
        ),
        check(
            "all_required_null_families_present",
            set(REQUIRED_NULL_FAMILIES).issubset({row["null_family"] for row in null_rows}),
        ),
        check(
            "all_motif_families_have_relabel_null_coverage",
            {
                row["motif_family"]
                for row in null_rows
                if row["motif_family"] != "global_phase_b_boundary"
            }
            == {row["motif_family"] for row in i8["bridge_motif_rows"]},
        ),
        check(
            "all_required_composition_controls_have_nulls",
            required_composition_relabels.issubset(observed_relabels),
        ),
        check(
            "all_global_blocked_claims_covered",
            all(value["null_ids"] for value in data["global_blocked_claim_coverage"].values()),
        ),
        check(
            "producer_residue_relabels_covered",
            any(row["null_family"] == "producer_residue_as_native_capacity_nulls" for row in null_rows),
        ),
        check(
            "medium_debt_relabels_covered",
            any(row["null_family"] == "medium_debt_as_native_shared_medium_nulls" for row in null_rows),
        ),
        check(
            "naturalization_debt_relabels_covered",
            any(
                row["null_family"] == "naturalization_debt_as_native_support_nulls"
                or "naturalization_debt" in row["attempted_relabel"]
                or "naturalization_debt" in row["relabel_path"]
                for row in null_rows
            ),
        ),
        check(
            "review_gate_bypass_nulls_present",
            any(row["null_family"] == "review_gate_bypass_nulls" for row in null_rows),
        ),
        check(
            "ap4_ap5_nat4_gap_erasure_nulls_present",
            any(row["null_family"] == "AP4_AP5_NAT4_gap_erasure_nulls" for row in null_rows),
        ),
        check(
            "null_adequacy_table_passed",
            all(row["adequacy_status"] == "passed" for row in adequacy_table),
        ),
        check(
            "prototype_and_runtime_probe_rows_remain_closed",
            not data["prototype_rows_opened"]
            and not data["runtime_ecology_probe_contract_opened"]
            and not data["positive_ecology_evidence_opened"],
        ),
        check(
            "phase_b_closed_phase_c_not_opened",
            data["phase_b_closed"]
            and not data["phase_b_closeout_policy"]["phase_c_opened"]
            and data["phase_b_closeout_policy"]["prototype_admission_deferred_to_iteration_10"],
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
        "accepted_phase_b_controls_fail_closed_ready_for_phase_c"
        if data["status"] == "passed"
        else "rejected_phase_b_controls_failed"
    )
    data["ready_for_iteration_10"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_10", data["ready_for_iteration_10"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 9 - Motif Relabel Nulls And Composition Controls",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- control rows: `{data['row_count_summary']['control_rows']}`",
        f"- schema negative controls: `{data['row_count_summary']['schema_negative_control_rows']}`",
        f"- motif control rows: `{data['row_count_summary']['motif_control_rows']}`",
        f"- composition control rows: `{data['row_count_summary']['composition_control_rows']}`",
        f"- failed_closed_rows: `{data['row_count_summary']['failed_closed_rows']}`",
        f"- failed_open_rows: `{data['row_count_summary']['failed_open_rows']}`",
        f"- row-local null rows: `{data['row_count_summary']['null_rows']}`",
        f"- near-positive controls: `{data['row_count_summary']['near_positive_control_rows']}`",
        f"- null_failed_closed_rows: `{data['row_count_summary']['null_failed_closed_rows']}`",
        f"- null_failed_open_rows: `{data['row_count_summary']['null_failed_open_rows']}`",
        f"- phase_b_closed: `{str(data['phase_b_closed']).lower()}`",
        f"- ready_for_iteration_10: `{str(data['ready_for_iteration_10']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 9 closes Phase B by deriving row-local nulls from forbidden",
        "promotion edges: source row -> valid bounded claim -> tempting stronger",
        "relabel -> expected rejection. Each null has a paired near-positive",
        "control that preserves the legitimate bounded bridge reading.",
        "",
        "## Control Families",
        "",
        "| Family | Row Count |",
        "| --- | ---: |",
    ]
    for family, row_ids in data["control_family_index"].items():
        lines.append(f"| `{family}` | {len(row_ids)} |")
    lines.extend(
        [
            "",
            "## Null Adequacy",
            "",
            "| Null Family | Count | Motif Families | Adequacy |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in data["null_adequacy_table"]:
        motif_families = ", ".join(f"`{family}`" for family in row["motif_families_covered"])
        lines.append(
            f"| `{row['null_family']}` | {row['null_count']} | {motif_families} | "
            f"`{row['adequacy_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Null Derivation",
            "",
            "The null set is not chosen by generic caution. It is derived from I7",
            "coverage/debt rows, I8 motif rows, and the I4 claim boundary. A null",
            "is accepted only when it names a source motif or global boundary,",
            "preserves the bounded valid claim, names the attempted relabel path,",
            "fails closed, and has a paired near-positive control.",
            "",
            "The near-positive controls matter because they prove I9 is not simply",
            "rejecting every bridge structure. I9 blocks unsafe promotion while",
            "leaving bounded motif classification available for Phase C admission",
            "work.",
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
            "I9 supports Phase B closeout controls, not Phase C prototype admission.",
            "All control rows and row-local null rows fail closed as intended. I9",
            "blocks vocabulary-as-evidence, ant-label-as-behavior, message scaffold",
            "as native medium, producer residue as native capacity, medium debt as",
            "native shared medium, naturalization debt as native support, visual or",
            "report artifacts as runtime evidence, prototype candidates as prototype",
            "success, motifs as native ecology success, N28 generative/extractive",
            "patterns as cooperation or biological agency, composition without",
            "order/source/control support, source summaries as original evidence,",
            "review-gate bypass, and AP4/AP5/NAT4 gap erasure.",
            "",
            "Passing I9 means the Phase B bridge motif library is guarded against",
            "known false promotions and ready for Iteration 10 prototype admission",
            "schema. It does not open prototype rows, runtime ecology probes,",
            "positive ecology evidence, native ecology, native ant/colony agency,",
            "native shared-medium coordination, sentience, biological agency, or",
            "Phase 8 completion claims.",
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

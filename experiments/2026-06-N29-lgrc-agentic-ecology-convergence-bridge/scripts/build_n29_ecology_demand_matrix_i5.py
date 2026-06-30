#!/usr/bin/env python3
"""Build N29 Iteration 5 ecology demand matrix."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_extraction_i1.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n29_agency_diagnostic_method_constraints_i2.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_matrix_i5.json"
REPORT = EXPERIMENT / "reports" / "n29_ecology_demand_matrix_i5.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_ecology_demand_matrix_i5.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

MATRIX_GROUPS = {
    "parent_basin_and_subbasin": {
        "description": "parent/colony/nest context, modulation, and contained sub-basin surfaces",
        "demand_components": {
            "parent_basin",
            "colony_parent_basin",
            "nest_home_basin",
        },
    },
    "shared_medium_and_medium_surface": {
        "description": "shared medium, medium surface, message scaffold, and medium debt target surfaces",
        "demand_components": {
            "shared_medium",
            "medium_surface",
            "message_scaffold",
            "medium_debt",
        },
    },
    "trace_pressure_and_affordance": {
        "description": "trace, pressure, route support, affordance, reserve, and alarm surfaces",
        "demand_components": {
            "trace",
            "pressure",
            "route_support_trace",
            "foodward_affordance_surface",
            "homeward_affordance_surface",
            "reserve_hunger_pressure",
            "alarm_threat_pressure",
        },
    },
    "susceptibility_and_resonance": {
        "description": "susceptibility, cargo-shaped response, resonance, and role-capture surfaces",
        "demand_components": {
            "susceptibility",
            "cargo_shaped_susceptibility",
            "role_susceptibility_division_of_labor",
            "resonance",
        },
    },
    "perturbation_co_response_loop": {
        "description": "perturbation, co-response, and parent-modulation loop target surfaces",
        "demand_components": {
            "perturbation",
            "co_response",
            "parent_basin_modulation",
        },
    },
    "role_labor_and_task_differentiation": {
        "description": "role, labor, isolation, construction, congestion, and mobile-boundary target surfaces",
        "demand_components": {
            "mobile_boundary_expression",
            "nursery_demand",
            "waste_isolation",
            "construction_tension",
            "crowding_congestion_cost",
            "role_susceptibility_division_of_labor",
        },
    },
    "reserve_surplus_and_reproduction_split": {
        "description": "resource, reserve, surplus, and split/reproduction target surfaces",
        "demand_components": {
            "food_resource_coupling",
            "reserve_hunger_pressure",
            "surplus_supported_split_reproduction",
        },
    },
    "debt_and_naturalization_conditions": {
        "description": "producer residue, medium debt, scaffold, and naturalization-condition demand rows",
        "demand_components": {
            "producer_residue",
            "medium_debt",
            "message_scaffold",
            "naturalization_condition",
        },
    },
}

PHASE_B_I5_SEPARATION_RULES = {
    "job": "ecology_demand_matrix_only",
    "must_not": [
        "import_N05_N28_evidence",
        "match_demand_to_supply",
        "create_bridge_motifs",
        "open_prototype_rows",
    ],
}


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


def demand_rows_from_i1(i1: dict[str, Any]) -> list[dict[str, Any]]:
    return list(i1.get("ecology_demand_rows", [])) + list(
        i1.get("rc_ant_component_demand_rows", [])
    )


def groups_for_component(component: str) -> list[str]:
    groups = [
        group_id
        for group_id, group in MATRIX_GROUPS.items()
        if component in group["demand_components"]
    ]
    if groups:
        return groups
    return ["shared_medium_and_medium_surface"]


def demand_matrix_row(row: dict[str, Any]) -> dict[str, Any]:
    group_ids = groups_for_component(row["ecology_component"])
    controls = list(row["required_controls"])
    return {
        "demand_id": row["demand_id"],
        "ecology_component": row["ecology_component"],
        "source_spec_reference": row["source_spec_reference"],
        "source_role": row["source_role"],
        "required_dynamics": row["required_dynamics"],
        "required_state_surfaces": row["required_state_surfaces"],
        "required_trace_surfaces": row["required_trace_surfaces"],
        "required_controls": controls,
        "blocked_relabels": row["blocked_relabels"],
        "first_probe_relevance": row["first_probe_relevance"],
        "producer_residue_risk": row["producer_residue_risk"],
        "medium_debt_risk": row["medium_debt_risk"],
        "claim_ceiling": "target_requirement_only",
        "x_i5_demand_family": group_ids[0],
        "x_i5_demand_subfamily": row["ecology_component"],
        "x_i5_source_demand_family": row["demand_family"],
        "x_i5_matrix_group_ids": group_ids,
        "x_i5_current_lgrc_surface_expectation": "unknown_until_I7",
        "x_i5_unresolved_without_capability_match": True,
        "x_unknown_field_review_status": "accepted_no_claim_effect",
        "x_i5_required_runtime_surfaces": {
            "state_surfaces": row["required_state_surfaces"],
            "trace_surfaces": row["required_trace_surfaces"],
            "control_surfaces": controls,
        },
        "x_i5_required_state_surface_count": len(row["required_state_surfaces"]),
        "x_i5_required_trace_surface_count": len(row["required_trace_surfaces"]),
        "x_i5_required_control_count": len(controls),
        "x_i5_unresolved_demand_status": "pending_i6_supply_atlas_and_i7_coverage_match",
        "x_i5_unresolved_as_of_i5": True,
        "x_i5_unresolved_reason": (
            "I5 is demand-only and cannot import N05-N28 capability evidence or "
            "perform demand/supply matching."
        ),
        "x_i5_candidate_capability_sources_imported": False,
        "x_i5_demand_supply_match_opened": False,
        "x_i5_bridge_motif_created": False,
        "x_i5_prototype_row_opened": False,
        "x_i5_positive_ecology_evidence_opened": False,
        "x_i5_implementation_evidence_opened": False,
        "x_i5_why_not_stronger": (
            "Current LGRC/GRC coverage is deliberately not evaluated until I6/I7; "
            "this row only states what the ecology demand requires."
        ),
    }


def group_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters: dict[str, int] = {group_id: 0 for group_id in MATRIX_GROUPS}
    for row in rows:
        for group_id in row["x_i5_matrix_group_ids"]:
            counters[group_id] += 1
    return [
        {
            "group_id": group_id,
            "description": MATRIX_GROUPS[group_id]["description"],
            "demand_count": counters[group_id],
        }
        for group_id in MATRIX_GROUPS
    ]


def surface_inventory(rows: list[dict[str, Any]]) -> dict[str, Any]:
    state_counter: Counter[str] = Counter()
    trace_counter: Counter[str] = Counter()
    control_counter: Counter[str] = Counter()
    relabel_counter: Counter[str] = Counter()
    for row in rows:
        state_counter.update(row["x_i5_required_runtime_surfaces"]["state_surfaces"])
        trace_counter.update(row["x_i5_required_runtime_surfaces"]["trace_surfaces"])
        control_counter.update(row["required_controls"])
        relabel_counter.update(row["blocked_relabels"])
    return {
        "unique_state_surface_count": len(state_counter),
        "unique_trace_surface_count": len(trace_counter),
        "unique_control_count": len(control_counter),
        "unique_blocked_relabel_count": len(relabel_counter),
        "top_state_surfaces": state_counter.most_common(10),
        "top_trace_surfaces": trace_counter.most_common(10),
        "top_controls": control_counter.most_common(10),
        "top_blocked_relabels": relabel_counter.most_common(10),
    }


def source_key(source_reference: str) -> str:
    if "README.md" in source_reference:
        return "README"
    if "FromStateToBecoming" in source_reference:
        return "FromStateToBecoming"
    if "RC-AgenticEcology" in source_reference:
        return "RCAgenticEcology"
    if "TheSharedMedium" in source_reference:
        return "TheSharedMedium"
    if "SharedMediumCoordination-EngineeringSpec" in source_reference:
        return "SharedMediumCoordinationSpec"
    return "other_source"


def demand_family_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {group_id: [] for group_id in MATRIX_GROUPS}
    for row in rows:
        for group_id in row["x_i5_matrix_group_ids"]:
            index[group_id].append(row["demand_id"])
    return index


def source_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, set[str]] = {
        "README": set(),
        "FromStateToBecoming": set(),
        "RCAgenticEcology": set(),
        "TheSharedMedium": set(),
        "SharedMediumCoordinationSpec": set(),
    }
    for row in rows:
        for ref in row["source_spec_reference"]:
            index.setdefault(source_key(ref), set()).add(row["demand_id"])
    return {key: sorted(value) for key, value in sorted(index.items())}


def control_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, set[str]] = {}
    for row in rows:
        for control in row["required_controls"]:
            index.setdefault(control, set()).add(row["demand_id"])
    return {key: sorted(value) for key, value in sorted(index.items())}


def demand_surface_taxonomy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    taxonomy: dict[str, Any] = {}
    for group_id, group in MATRIX_GROUPS.items():
        group_rows = [row for row in rows if group_id in row["x_i5_matrix_group_ids"]]
        state_surfaces = sorted(
            {
                surface
                for row in group_rows
                for surface in row["required_state_surfaces"]
            }
        )
        trace_surfaces = sorted(
            {
                surface
                for row in group_rows
                for surface in row["required_trace_surfaces"]
            }
        )
        taxonomy[group_id] = {
            "description": group["description"],
            "demand_ids": [row["demand_id"] for row in group_rows],
            "state_surfaces": state_surfaces,
            "trace_surfaces": trace_surfaces,
        }
    return taxonomy


def control_taxonomy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = control_index(rows)
    return {
        "control_count": len(controls),
        "control_index": controls,
        "control_policy": (
            "controls are target requirements only in I5; execution and fail-closed "
            "evaluation remain later-phase work"
        ),
    }


def unresolved_demand_ledger(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    for row in rows:
        future_surface = " + ".join(
            row["required_state_surfaces"][:2] + row["required_trace_surfaces"][:2]
        )
        ledger.append(
            {
                "demand_id": row["demand_id"],
                "unresolved_reason": row["x_i5_unresolved_reason"],
                "required_future_surface": future_surface,
                "blocked_relabels": row["blocked_relabels"],
                "first_probe_relevance": row["first_probe_relevance"],
            }
        )
    return ledger


def build() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    source_rows = demand_rows_from_i1(i1)
    rows = [demand_matrix_row(row) for row in source_rows]
    ecology_schema = i4["schema_bundle"]["ecology_demand_row_schema"]
    i5_rule = i4["phase_b_separation_rules"]["I5"]
    data: dict[str, Any] = {
        "artifact_id": "n29_ecology_demand_matrix_i5",
        "experiment_id": "N29",
        "iteration": "I5",
        "title": "Ecology Demand Matrix",
        "status": "passed",
        "acceptance_state": "accepted_ecology_demand_matrix",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_ecology_demand_extraction_i1",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_ecology_demand_extraction_i1.json"
                ),
                "status": i1.get("status", "not_recorded"),
                "output_digest": i1.get("output_digest", "not_recorded"),
                "consumed_as": "demand_source",
            },
            {
                "artifact_id": "n29_agency_diagnostic_method_constraints_i2",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_agency_diagnostic_method_constraints_i2.json"
                ),
                "status": i2.get("status", "not_recorded"),
                "output_digest": i2.get("output_digest", "not_recorded"),
                "consumed_as": "blocked_claim_language_only_not_demand_or_supply_source",
            },
            {
                "artifact_id": "n29_bridge_schema_i4",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_schema_i4.json"
                ),
                "status": i4.get("status", "not_recorded"),
                "output_digest": i4.get("output_digest", "not_recorded"),
                "consumed_as": "schema_and_phase_b_boundary",
            },
        ],
        "matrix_policy": {
            "canonical_row_semantics": "one row = one ecology demand requirement",
            "facets_stay_in_arrays": [
                "required_dynamics",
                "required_state_surfaces",
                "required_trace_surfaces",
                "required_controls",
                "blocked_relabels",
            ],
            "cartesian_expansion_allowed": False,
            "coverage_status_assignment_allowed": False,
            "current_lgrc_surface_claim_allowed": False,
            "source_capability_matching_allowed": False,
            "prototype_rows_allowed": False,
        },
        "phase_b_separation_rule_consumed": copy.deepcopy(i5_rule),
        "phase_b_i5_job": "ecology_demand_matrix_only",
        "ecology_demand_matrix_supported": True,
        "ecology_demand_rows": rows,
        "demand_family_index": demand_family_index(rows),
        "source_index": source_index(rows),
        "control_index": control_index(rows),
        "demand_surface_taxonomy": demand_surface_taxonomy(rows),
        "control_taxonomy": control_taxonomy(rows),
        "demand_group_summary": group_summary(rows),
        "runtime_surface_inventory": surface_inventory(rows),
        "unresolved_demand_ledger": unresolved_demand_ledger(rows),
        "source_coverage_summary": {
            "source_count": len(source_index(rows)),
            "demand_source": "n29_ecology_demand_extraction_i1",
            "blocked_claim_language_source": "n29_agency_diagnostic_method_constraints_i2",
            "schema_boundary_source": "n29_bridge_schema_i4",
            "coverage_claimed": False,
            "coverage_deferred_to": "I7",
        },
        "row_count_summary": {
            "ecology_demand_rows": len(rows),
            "demand_family_index_count": len(MATRIX_GROUPS),
            "source_index_count": len(source_index(rows)),
            "control_index_count": len(control_index(rows)),
            "unresolved_demand_ledger_rows": len(rows),
        },
        "current_lgrc_grc_surface_evaluation_status": "deferred_to_iteration_6_and_7",
        "n05_n28_evidence_imported": False,
        "i3_capability_matching_attempted": False,
        "candidate_capability_sources_imported": False,
        "demand_supply_matching_opened": False,
        "coverage_status_assigned": False,
        "coverage_debt_rows_opened": False,
        "bridge_motif_success_claimed": False,
        "bridge_motifs_created": False,
        "prototype_rows_opened": False,
        "positive_ecology_evidence_opened": False,
        "implementation_evidence_opened": False,
        "claim_boundary_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "claim_ceiling": "ecology_demand_matrix_only_no_supply_match_no_prototypes",
        "ready_for_iteration_6": False,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    required_schema_fields = set(ecology_schema["required_fields"])
    expected_groups = {
        "parent_basin_and_subbasin",
        "shared_medium_and_medium_surface",
        "trace_pressure_and_affordance",
        "susceptibility_and_resonance",
        "perturbation_co_response_loop",
        "role_labor_and_task_differentiation",
        "reserve_surplus_and_reproduction_split",
        "debt_and_naturalization_conditions",
    }
    seen_groups = {group for row in rows for group in row["x_i5_matrix_group_ids"]}
    demand_ids = {row["demand_id"] for row in rows}
    unresolved_ids = {row["demand_id"] for row in data["unresolved_demand_ledger"]}
    allowed_i4_fields = (
        set(ecology_schema["required_fields"])
        | set(ecology_schema["optional_fields"])
        | {"source_role"}
    )
    checks = [
        check("i1_ecology_demand_model_passed", i1.get("status") == "passed"),
        check("i2_agency_method_constraints_passed", i2.get("status") == "passed"),
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check(
            "i1_source_digest_matches",
            data["source_artifacts"][0]["output_digest"] == i1.get("output_digest"),
        ),
        check(
            "uses_i1_as_only_demand_source",
            [
                row["artifact_id"]
                for row in data["source_artifacts"]
                if row["consumed_as"] == "demand_source"
            ]
            == ["n29_ecology_demand_extraction_i1"],
        ),
        check(
            "i2_used_only_for_blocked_claim_language",
            any(
                row["artifact_id"] == "n29_agency_diagnostic_method_constraints_i2"
                and row["consumed_as"] == "blocked_claim_language_only_not_demand_or_supply_source"
                for row in data["source_artifacts"]
            ),
        ),
        check(
            "i5_phase_b_separation_rule_consumed",
            i5_rule == PHASE_B_I5_SEPARATION_RULES,
        ),
        check(
            "only_i1_i2_i4_sources_consumed",
            {row["artifact_id"] for row in data["source_artifacts"]}
            == {
                "n29_ecology_demand_extraction_i1",
                "n29_agency_diagnostic_method_constraints_i2",
                "n29_bridge_schema_i4",
            },
        ),
        check(
            "demand_row_count_matches_i1",
            len(rows)
            == i1.get("total_demand_row_count")
            == len(source_rows)
            == 30,
        ),
        check(
            "all_i4_ecology_demand_schema_fields_present",
            all(required_schema_fields.issubset(row.keys()) for row in rows),
        ),
        check(
            "all_i5_row_extensions_are_namespaced",
            all(
                all(key in allowed_i4_fields or key.startswith("x_") for key in row)
                for row in rows
            ),
        ),
        check(
            "required_group_families_present",
            seen_groups == expected_groups,
            f"seen_groups={sorted(seen_groups)}",
        ),
        check(
            "every_demand_has_runtime_surfaces_and_controls",
            all(
                row["required_state_surfaces"]
                and row["required_trace_surfaces"]
                and row["required_controls"]
                for row in rows
            ),
        ),
        check(
            "all_rows_have_claim_ceiling_target_requirement_only",
            all(row["claim_ceiling"] == "target_requirement_only" for row in rows),
        ),
        check(
            "all_rows_have_blocked_relabels",
            all(row["blocked_relabels"] for row in rows),
        ),
        check(
            "current_surfaces_marked_unresolved_pending_i6_i7",
            all(
                row["x_i5_unresolved_without_capability_match"]
                and row["x_i5_current_lgrc_surface_expectation"] == "unknown_until_I7"
                for row in rows
            ),
        ),
        check("all_rows_with_missing_surfaces_enter_unresolved_ledger", demand_ids == unresolved_ids),
        check(
            "source_roles_are_target_requirement_not_evidence",
            all(row["source_role"] == "target_requirement_not_evidence" for row in rows),
        ),
        check(
            "coverage_status_assigned_false",
            not data["coverage_status_assigned"]
            and all("coverage_status" not in row for row in rows),
        ),
        check(
            "i3_capability_matching_attempted_false",
            not data["i3_capability_matching_attempted"],
        ),
        check(
            "no_n05_n28_evidence_imported",
            not data["n05_n28_evidence_imported"]
            and not data["candidate_capability_sources_imported"],
        ),
        check(
            "no_demand_supply_matching_or_coverage_rows_opened",
            not data["demand_supply_matching_opened"]
            and not data["coverage_debt_rows_opened"]
            and all(not row["x_i5_demand_supply_match_opened"] for row in rows),
        ),
        check(
            "no_bridge_motifs_or_prototype_rows_opened",
            not data["bridge_motif_success_claimed"]
            and not data["bridge_motifs_created"]
            and not data["prototype_rows_opened"]
            and all(
                not row["x_i5_bridge_motif_created"]
                and not row["x_i5_prototype_row_opened"]
                for row in rows
            ),
        ),
        check(
            "positive_ecology_and_implementation_evidence_closed",
            not data["positive_ecology_evidence_opened"]
            and not data["implementation_evidence_opened"]
            and all(
                not row["x_i5_positive_ecology_evidence_opened"]
                and not row["x_i5_implementation_evidence_opened"]
                for row in rows
            ),
        ),
        check(
            "native_shared_medium_coordination_opened_false",
            data["claim_boundary_audit"].get("native_shared_medium_coordination_opened") is False,
        ),
        check(
            "native_ant_and_colony_agency_opened_false",
            data["claim_boundary_audit"].get("native_ant_agency_opened") is False
            and data["claim_boundary_audit"].get("native_colony_agency_opened") is False,
        ),
        check(
            "phase8_completion_opened_false",
            data["claim_boundary_audit"].get("phase8_completion_opened") is False,
        ),
        check(
            "claim_boundary_flags_false",
            all(value is False for value in data["claim_boundary_audit"].values()),
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_ecology_demand_matrix"
        if data["status"] == "passed"
        else "rejected_ecology_demand_matrix_failed_checks"
    )
    data["ready_for_iteration_6"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_6", data["ready_for_iteration_6"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 5 - Ecology Demand Matrix",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- demand rows: `{len(data['ecology_demand_rows'])}`",
        f"- current_lgrc_grc_surface_evaluation_status: `{data['current_lgrc_grc_surface_evaluation_status']}`",
        f"- n05_n28_evidence_imported: `{str(data['n05_n28_evidence_imported']).lower()}`",
        f"- coverage_status_assigned: `{str(data['coverage_status_assigned']).lower()}`",
        f"- demand_supply_matching_opened: `{str(data['demand_supply_matching_opened']).lower()}`",
        f"- bridge_motifs_created: `{str(data['bridge_motifs_created']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- ready_for_iteration_6: `{str(data['ready_for_iteration_6']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 5 is demand-only. It turns I1 ecology target demands into a",
        "grouped matrix of required dynamics, state surfaces, trace surfaces, and",
        "controls. It does not import N05-N28 capability evidence, perform supply",
        "matching, create motifs, or open prototype rows.",
        "",
        "## Demand Groups",
        "",
        "| Group | Demand Count | Description |",
        "| --- | ---: | --- |",
    ]
    for group in data["demand_group_summary"]:
        lines.append(
            f"| `{group['group_id']}` | {group['demand_count']} | {group['description']} |"
        )
    lines.extend(
        [
            "",
            "## Surface Inventory",
            "",
            f"- unique state surfaces: `{data['runtime_surface_inventory']['unique_state_surface_count']}`",
            f"- unique trace surfaces: `{data['runtime_surface_inventory']['unique_trace_surface_count']}`",
            f"- unique controls: `{data['runtime_surface_inventory']['unique_control_count']}`",
            f"- unique blocked relabels: `{data['runtime_surface_inventory']['unique_blocked_relabel_count']}`",
            "",
            "## Source Index",
            "",
            "| Source | Demand Count |",
            "| --- | ---: |",
        ]
    )
    for source, demand_ids in data["source_index"].items():
        lines.append(f"| `{source}` | {len(demand_ids)} |")
    lines.extend(
        [
            "",
            "## Recurring Runtime Surfaces",
            "",
            "| Kind | Top Entries |",
            "| --- | --- |",
            "| State | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["runtime_surface_inventory"]["top_state_surfaces"][:5]
            )
            + " |",
            "| Trace | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["runtime_surface_inventory"]["top_trace_surfaces"][:5]
            )
            + " |",
            "| Control | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["runtime_surface_inventory"]["top_controls"][:5]
            )
            + " |",
            "| Blocked relabel | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["runtime_surface_inventory"]["top_blocked_relabels"][:5]
            )
            + " |",
            "",
            "## Unresolved Demand Ledger",
            "",
            "All I5 demand rows remain unresolved until I6/I7 by design. The JSON",
            "contains the full ledger; this report lists the first probe clusters",
            "through the family index rather than a flat Cartesian table.",
            "",
            "| Family | Demand IDs |",
            "| --- | --- |",
        ]
    )
    for family, demand_ids in data["demand_family_index"].items():
        lines.append(f"| `{family}` | `{', '.join(demand_ids)}` |")
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
            "I5 supports the ecology demand matrix as a target-requirement artifact.",
            "All rows remain unresolved as of I5 because the phase boundary forbids",
            "current LGRC/GRC coverage evaluation until I6/I7. This is intentional:",
            "I5 defines what the ecology side asks for; it does not answer what the",
            "N05-N28 stack can supply.",
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

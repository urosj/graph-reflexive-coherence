#!/usr/bin/env python3
"""Build N29 Iteration 7 demand/supply coverage and debt matrix."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_matrix_i5.json"
I6_OUTPUT = EXPERIMENT / "outputs" / "n29_capability_supply_atlas_i6.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
REPORT = EXPERIMENT / "reports" / "n29_demand_supply_coverage_debt_i7.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_demand_supply_coverage_debt_i7.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

PHASE_B_I7_SEPARATION_RULES = {
    "job": "demand_supply_coverage_debt_matching_only",
    "must_not": [
        "create_bridge_motifs",
        "open_prototype_rows",
        "claim_native_ecology",
    ],
}

SOURCE_BACKED_FAMILIES = {
    "trace_pressure_and_affordance",
    "susceptibility_and_resonance",
    "perturbation_co_response_loop",
    "reserve_surplus_and_reproduction_split",
    "role_labor_and_task_differentiation",
}

MEDIUM_DEBT_COMPONENTS = {
    "shared_medium",
    "medium_surface",
    "message_scaffold",
    "medium_debt",
    "colony_parent_basin",
    "parent_basin",
    "parent_basin_modulation",
}

PRODUCER_MEDIATED_COMPONENTS = {
    "producer_residue",
    "message_scaffold",
    "construction_tension",
}

NATURALIZATION_COMPONENTS = {
    "naturalization_condition",
    "role_susceptibility_division_of_labor",
}

MOTIF_HINTS = {
    "trace_pressure_loop",
    "reserve_optionality_formation",
    "boundary_shared_medium_unit",
    "proxy_susceptibility_reentry",
    "transfer_replay_role_relocation",
    "generative_extractive_medium_reshaping",
    "composition",
    "none",
}

DEMAND_ANCHOR_CAPABILITIES = {
    "general_parent_basin": [
        "n25_2_mb6_validation_bridge",
        "n16_self_environment_boundary",
        "n24_surplus_supported_optionality",
    ],
    "general_shared_medium": [
        "n25_2_mb6_validation_bridge",
        "n28_generative_extractive_persistence",
        "n18_limited_long_horizon_closure",
    ],
    "general_medium_surface": [
        "n28_generative_extractive_persistence",
        "n24_surplus_supported_optionality",
        "n25_2_mb6_validation_bridge",
    ],
    "general_perturbation": [
        "n17_closed_boundary_engagement_loop",
        "n09_goal_proxy_regulation",
        "n16_self_environment_boundary",
    ],
    "general_trace": [
        "n08_memory_trail_affordance",
        "n17_closed_boundary_engagement_loop",
        "n28_generative_extractive_persistence",
    ],
    "general_pressure": [
        "n13_support_seeking_regulation",
        "n24_surplus_supported_optionality",
        "n09_goal_proxy_regulation",
    ],
    "general_susceptibility": [
        "n22_susceptibility_update",
        "n26_proxy_divergence_collapse",
        "n15_endogenous_proxy_formation",
    ],
    "general_co_response": [
        "n17_closed_boundary_engagement_loop",
        "n28_generative_extractive_persistence",
        "n18_limited_long_horizon_closure",
    ],
    "general_resonance": [
        "n05_coherence_waves_oscillators",
        "n17_closed_boundary_engagement_loop",
    ],
    "general_parent_basin_modulation": [
        "n25_2_mb6_validation_bridge",
        "n24_surplus_supported_optionality",
        "n28_generative_extractive_persistence",
    ],
    "general_message_scaffold": [
        "n20_becoming_primitive_contract",
        "n25_1_multi_basin_requirements_bridge",
    ],
    "general_medium_debt": [
        "n25_1_multi_basin_requirements_bridge",
        "n28_generative_extractive_persistence",
        "n25_2_mb6_validation_bridge",
    ],
    "general_producer_residue": [
        "n20_becoming_primitive_contract",
        "n25_1_multi_basin_requirements_bridge",
        "n22_susceptibility_update",
    ],
    "general_naturalization_condition": [
        "n21_withdrawal_naturalization",
        "n20_becoming_primitive_contract",
    ],
    "rc_ant_colony_parent_basin": [
        "n25_2_mb6_validation_bridge",
        "n16_self_environment_boundary",
        "n24_surplus_supported_optionality",
    ],
    "rc_ant_mobile_boundary_expression": [
        "n27_configuration_substrate_transfer",
        "n16_self_environment_boundary",
        "n25_2_mb6_validation_bridge",
    ],
    "rc_ant_nest_home_basin": [
        "n25_2_mb6_validation_bridge",
        "n24_surplus_supported_optionality",
        "n16_self_environment_boundary",
    ],
    "rc_ant_food_resource_coupling": [
        "n28_generative_extractive_persistence",
        "n24_surplus_supported_optionality",
        "n26_proxy_divergence_collapse",
    ],
    "rc_ant_route_support_trace": [
        "n08_memory_trail_affordance",
        "n06_runtime_visible_route_selection",
        "n17_closed_boundary_engagement_loop",
    ],
    "rc_ant_foodward_affordance_surface": [
        "n06_runtime_visible_route_selection",
        "n14_consequence_sensitive_route_selection",
        "n22_susceptibility_update",
    ],
    "rc_ant_homeward_affordance_surface": [
        "n06_runtime_visible_route_selection",
        "n14_consequence_sensitive_route_selection",
        "n27_configuration_substrate_transfer",
    ],
    "rc_ant_cargo_shaped_susceptibility": [
        "n22_susceptibility_update",
        "n26_proxy_divergence_collapse",
        "n27_configuration_substrate_transfer",
    ],
    "rc_ant_reserve_hunger_pressure": [
        "n24_surplus_supported_optionality",
        "n13_support_seeking_regulation",
        "n09_goal_proxy_regulation",
    ],
    "rc_ant_alarm_threat_pressure": [
        "n09_goal_proxy_regulation",
        "n13_support_seeking_regulation",
        "n17_closed_boundary_engagement_loop",
    ],
    "rc_ant_nursery_demand": [
        "n22_susceptibility_update",
        "n24_surplus_supported_optionality",
        "n25_2_mb6_validation_bridge",
    ],
    "rc_ant_waste_isolation": [
        "n28_generative_extractive_persistence",
        "n24_surplus_supported_optionality",
    ],
    "rc_ant_construction_tension": [
        "n28_generative_extractive_persistence",
        "n24_surplus_supported_optionality",
        "n25_2_mb6_validation_bridge",
    ],
    "rc_ant_crowding_congestion_cost": [
        "n14_consequence_sensitive_route_selection",
        "n28_generative_extractive_persistence",
        "n06_runtime_visible_route_selection",
    ],
    "rc_ant_role_susceptibility_division_of_labor": [
        "n22_susceptibility_update",
        "n27_configuration_substrate_transfer",
        "n23_live_continuation_collapse",
    ],
    "rc_ant_surplus_supported_split_reproduction": [
        "n24_surplus_supported_optionality",
        "n25_2_mb6_validation_bridge",
        "n25_scoped_basin_formation",
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


def tokens_from_value(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        parts = re.split(r"[^a-zA-Z0-9]+", value.lower())
        return {part for part in parts if len(part) >= 3}
    if isinstance(value, list):
        tokens: set[str] = set()
        for item in value:
            tokens.update(tokens_from_value(item))
        return tokens
    if isinstance(value, dict):
        tokens: set[str] = set()
        for item in value.values():
            tokens.update(tokens_from_value(item))
        return tokens
    return set()


def demand_tokens(row: dict[str, Any]) -> set[str]:
    tokens = tokens_from_value(
        [
            row["demand_id"],
            row["ecology_component"],
            row["required_state_surfaces"],
            row["required_trace_surfaces"],
            row["required_dynamics"],
            row["x_i5_matrix_group_ids"],
        ]
    )
    for prefix in ("general", "ant"):
        tokens.discard(prefix)
    return tokens


def supply_tokens(row: dict[str, Any]) -> set[str]:
    return tokens_from_value(
        [
            row["capability_id"],
            row["source_experiment"],
            row["possible_ecology_demands"],
            row["supplied_geometry_or_dynamic"],
            row["x_i6_supply_group_ids"],
            row["x_i6_possible_bridge_motif_tags"],
        ]
    )


def direct_demand_names(row: dict[str, Any]) -> set[str]:
    names = {
        row["demand_id"],
        row["ecology_component"],
        row["demand_id"].removeprefix("general_"),
        row["demand_id"].removeprefix("rc_ant_"),
    }
    return {name for name in names if name}


def score_candidate(demand: dict[str, Any], supply: dict[str, Any]) -> dict[str, Any]:
    direct_names = direct_demand_names(demand)
    possible = set(supply["possible_ecology_demands"])
    exact_matches = sorted(direct_names & possible)
    d_tokens = demand_tokens(demand)
    s_tokens = supply_tokens(supply)
    overlap = sorted(d_tokens & s_tokens)
    group_bonus = 0
    demand_groups = set(demand["x_i5_matrix_group_ids"])
    supply_groups = set(supply["x_i6_supply_group_ids"])
    if "trace_pressure_and_affordance" in demand_groups and {
        "trace_aftereffect",
        "pressure_reserve_support",
        "route_choice_arbitration",
    } & supply_groups:
        group_bonus += 4
    if "susceptibility_and_resonance" in demand_groups and {
        "proxy_divergence_collapse",
        "trace_aftereffect",
    } & supply_groups:
        group_bonus += 4
    if "perturbation_co_response_loop" in demand_groups and {
        "closed_loop_perturbation_response",
        "pressure_reserve_support",
        "medium_reshaping_generative_extractive",
    } & supply_groups:
        group_bonus += 4
    if "parent_basin_and_subbasin" in demand_groups and {
        "boundary_multi_basin_unit",
        "formation_child_basin",
    } & supply_groups:
        group_bonus += 4
    if "shared_medium_and_medium_surface" in demand_groups and {
        "medium_reshaping_generative_extractive",
        "boundary_multi_basin_unit",
    } & supply_groups:
        group_bonus += 4
    if "role_labor_and_task_differentiation" in demand_groups and {
        "proxy_divergence_collapse",
        "transfer_replay_relocation",
        "medium_reshaping_generative_extractive",
    } & supply_groups:
        group_bonus += 4
    if "reserve_surplus_and_reproduction_split" in demand_groups and {
        "formation_child_basin",
        "pressure_reserve_support",
        "medium_reshaping_generative_extractive",
    } & supply_groups:
        group_bonus += 4
    if "debt_and_naturalization_conditions" in demand_groups and {
        "control_only_or_negative",
        "pressure_reserve_support",
    } & supply_groups:
        group_bonus += 3
    anchor_rank = None
    anchor_bonus = 0
    anchors = DEMAND_ANCHOR_CAPABILITIES.get(demand["demand_id"], [])
    if supply["capability_id"] in anchors:
        anchor_rank = anchors.index(supply["capability_id"]) + 1
        anchor_bonus = max(6 - anchor_rank, 1)
    score = 10 * len(exact_matches) + min(len(overlap), 8) + group_bonus + anchor_bonus
    return {
        "capability_id": supply["capability_id"],
        "source_experiment": supply["source_experiment"],
        "score": score,
        "anchor_rank": anchor_rank,
        "exact_matches": exact_matches,
        "token_overlap": overlap[:12],
        "supply_family": supply["x_i6_supply_family"],
        "prototype_potential_status": supply["x_i6_prototype_potential_status"],
        "normalized_native_readiness_status": supply[
            "x_i6_normalized_native_readiness_status"
        ],
    }


def ranked_candidates(
    demand: dict[str, Any], supply_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    scored = [score_candidate(demand, row) for row in supply_rows]
    viable = [row for row in scored if row["score"] >= 4 or row["exact_matches"]]
    viable.sort(key=lambda row: (-row["score"], row["source_experiment"], row["capability_id"]))
    return viable[:6]


def row_source_artifacts(candidate_ids: list[str], supply_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for capability_id in candidate_ids:
        for artifact in supply_by_id[capability_id]["x_i6_source_artifact_manifest"]:
            artifacts.append(
                {
                    "capability_id": capability_id,
                    "path": artifact["path"],
                    "artifact_role": artifact["artifact_role"],
                    "exists": artifact["exists"],
                    "sha256": artifact["sha256"],
                    "source_status": artifact["source_status"],
                    "source_output_digest": artifact["source_output_digest"],
                }
            )
    return artifacts


def coverage_id_for(demand: dict[str, Any]) -> str:
    slug = re.sub(r"[^A-Z0-9]+", ".", demand["demand_id"].upper()).strip(".")
    return f"COV.{slug}.I7"


def combined_debt(
    candidates: list[dict[str, Any]], supply_by_id: dict[str, dict[str, Any]], debt_type: str
) -> list[str]:
    values = []
    for candidate in candidates:
        value = supply_by_id[candidate["capability_id"]][debt_type]
        if value and value != "none" and value not in values:
            values.append(value)
    return values


def debt_status(values: list[str]) -> str:
    return "present" if values else "absent"


def combined_relabels(
    demand: dict[str, Any],
    candidates: list[dict[str, Any]],
    supply_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    relabels = list(demand["blocked_relabels"])
    for candidate in candidates:
        for relabel in supply_by_id[candidate["capability_id"]]["blocked_ecology_relabels"]:
            if relabel not in relabels:
                relabels.append(relabel)
    return relabels


def coverage_status_for(
    demand: dict[str, Any], candidates: list[dict[str, Any]], supply_by_id: dict[str, dict[str, Any]]
) -> str:
    if not candidates:
        return "missing_runtime_surface"
    component = demand["ecology_component"]
    if component in PRODUCER_MEDIATED_COMPONENTS:
        return "producer_mediated"
    if component in NATURALIZATION_COMPONENTS:
        return "naturalization_debt"
    if component in MEDIUM_DEBT_COMPONENTS:
        return "medium_debt"
    if all(
        supply_by_id[row["capability_id"]]["x_i6_normalized_native_readiness_status"]
        in {"control_only", "blocked_by_review_gate"}
        for row in candidates[:3]
    ):
        return "control_only"
    if any(row["prototype_potential_status"] == "blocked_by_claim_boundary" for row in candidates[:3]):
        return "prototype_candidate"
    if demand["x_i5_demand_family"] in SOURCE_BACKED_FAMILIES and any(
        row["exact_matches"] for row in candidates[:3]
    ):
        return "source_backed"
    if any(
        supply_by_id[row["capability_id"]]["x_i6_normalized_native_readiness_status"] == "medium_debt"
        for row in candidates[:3]
    ):
        return "medium_debt"
    return "prototype_candidate"


def bridge_motif_hint(
    demand: dict[str, Any], candidates: list[dict[str, Any]], supply_by_id: dict[str, dict[str, Any]]
) -> str:
    motif_counts: Counter[str] = Counter()
    for candidate in candidates[:4]:
        motif_counts.update(supply_by_id[candidate["capability_id"]]["x_i6_possible_bridge_motif_tags"])
    if not motif_counts:
        return "none"
    motif = motif_counts.most_common(1)[0][0]
    if motif in MOTIF_HINTS:
        return motif
    return "composition"


def agency_diagnostic_roles(status: str, demand: dict[str, Any]) -> list[str]:
    roles = ["claim_boundary", "source_of_truth"]
    if status in {"naturalization_debt", "producer_mediated"}:
        roles.extend(["naturalization_depth", "withdrawal_resistance"])
    if status in {"medium_debt", "prototype_candidate", "source_backed"}:
        roles.append("medium_debt_visibility")
    if "susceptibility" in demand["ecology_component"] or "role" in demand["ecology_component"]:
        roles.append("susceptibility_update")
    if "trace" in demand["ecology_component"] or "pressure" in demand["ecology_component"]:
        roles.append("trace_pressure")
    return sorted(set(roles))


def coverage_reason(
    status: str, candidates: list[dict[str, Any]], demand: dict[str, Any]
) -> str:
    if status == "missing_runtime_surface":
        return "No I6 supply row reached the minimum deterministic match threshold for this demand."
    top = candidates[0]
    exact = ", ".join(top["exact_matches"]) if top["exact_matches"] else "no exact tag"
    if status == "source_backed":
        return (
            f"Top candidate {top['capability_id']} has original source artifacts and exact "
            f"demand tag match ({exact}); debt remains row-local and claim-bounded."
        )
    if status == "prototype_candidate":
        return (
            f"Top candidate {top['capability_id']} supplies related geometry but I7 only "
            "classifies the mapping; prototype construction waits for later iterations."
        )
    if status == "producer_mediated":
        return (
            f"Demand {demand['demand_id']} depends on explicit producer/scaffold handling; "
            "coverage is producer-mediated and cannot upgrade native ecology."
        )
    if status == "medium_debt":
        return (
            f"Demand {demand['demand_id']} touches shared-medium or parent-medium semantics; "
            "I7 records a candidate surface but preserves medium debt."
        )
    if status == "naturalization_debt":
        return (
            f"Demand {demand['demand_id']} requires scaffold withdrawal or substrate carriage; "
            "I7 records naturalization debt rather than native support."
        )
    if status == "control_only":
        return "Only review/schema/control supply rows match strongly enough; no runtime coverage is claimed."
    if status == "blocked_relabel":
        return "The demand would require an unsafe relabel under the current claim boundary."
    return "Coverage is not applicable under the current demand/supply scope."


def native_gap(status: str, candidates: list[dict[str, Any]]) -> str:
    if status == "source_backed":
        return "source-backed bridge coverage is still not native ecology or native agency"
    if status == "prototype_candidate":
        return "requires motif/prototype construction and controls before runtime bridge claim"
    if status == "producer_mediated":
        return "producer residue must remain explicit or be naturalized by later N30+ work"
    if status == "medium_debt":
        return "shared-medium relation is not yet native coordination"
    if status == "naturalization_debt":
        return "requires scaffold withdrawal or substrate-carried continuation evidence"
    if status == "control_only":
        return "review/schema gate only; no current runtime surface"
    if status == "missing_runtime_surface":
        return "no current N05-N28 supply surface identified"
    return "not_applicable"


def first_probe_implication(
    demand: dict[str, Any], status: str, candidates: list[dict[str, Any]]
) -> str:
    if status == "missing_runtime_surface":
        return (
            "Define a minimal runtime/reconstruction probe for the missing state and trace "
            f"surfaces: {', '.join(demand['required_state_surfaces'][:2])}."
        )
    if status == "source_backed":
        return (
            "Build an I10+ admission record that returns to the named original artifacts and "
            "tests the demand-specific controls without opening native ecology."
        )
    if status == "prototype_candidate":
        return (
            "Use I8 to define the bridge motif, then I10+ to decide whether this mapping can "
            "become a runnable or source-backed reconstruction prototype."
        )
    if status == "producer_mediated":
        return "Prototype must expose producer ledger and include producer-as-native relabel controls."
    if status == "medium_debt":
        return "Prototype must expose medium debt and test medium-as-native-coordination controls."
    if status == "naturalization_debt":
        return "Prototype must include withdrawal/substrate-carriage checks before native wording."
    return "Keep as control/context row unless later source evidence changes the scope."


def coverage_row(
    demand: dict[str, Any], supply_rows: list[dict[str, Any]], supply_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    candidates = ranked_candidates(demand, supply_rows)
    candidate_ids = [row["capability_id"] for row in candidates]
    status = coverage_status_for(demand, candidates, supply_by_id)
    source_artifacts = row_source_artifacts(candidate_ids[:4], supply_by_id)
    source_ok = bool(source_artifacts) and all(artifact["exists"] and artifact["sha256"] for artifact in source_artifacts)
    producer_debt = combined_debt(candidates[:4], supply_by_id, "producer_residue")
    medium_debt = combined_debt(candidates[:4], supply_by_id, "medium_debt")
    naturalization_debt = combined_debt(candidates[:4], supply_by_id, "naturalization_debt")
    motif_hint = bridge_motif_hint(demand, candidates, supply_by_id)
    row = {
        "coverage_id": coverage_id_for(demand),
        "source_experiment_or_spec": demand["source_spec_reference"],
        "ecology_demand": demand["demand_id"],
        "candidate_capability_sources": [
            {
                "capability_id": candidate["capability_id"],
                "source_experiment": candidate["source_experiment"],
                "source_claim_ceiling": supply_by_id[candidate["capability_id"]][
                    "source_claim_ceiling"
                ],
                "review_gate_status": supply_by_id[candidate["capability_id"]][
                    "review_gate_status"
                ],
                "score": candidate["score"],
                "anchor_rank": candidate["anchor_rank"],
                "exact_matches": candidate["exact_matches"],
                "token_overlap": candidate["token_overlap"],
                "supply_family": candidate["supply_family"],
                "prototype_potential_status": candidate["prototype_potential_status"],
                "normalized_native_readiness_status": candidate[
                    "normalized_native_readiness_status"
                ],
            }
            for candidate in candidates
        ],
        "bridge_motif": motif_hint,
        "agency_diagnostic_role": agency_diagnostic_roles(status, demand),
        "coverage_status": status,
        "coverage_reason": coverage_reason(status, candidates, demand),
        "producer_residue": producer_debt or ["none_identified_in_top_candidates"],
        "medium_debt": medium_debt or ["none_identified_in_top_candidates"],
        "naturalization_debt": naturalization_debt or ["none_identified_in_top_candidates"],
        "native_readiness_status": "no_native_ready_surface_opened_by_I7",
        "native_readiness_gap": native_gap(status, candidates),
        "blocked_relabels": combined_relabels(demand, candidates[:4], supply_by_id),
        "first_probe_implication": first_probe_implication(demand, status, candidates),
        "claim_ceiling": "demand_supply_coverage_mapping_only_no_motif_no_prototype_no_native_ecology",
        "why_not_stronger": (
            "I7 matches demand to supply and records debt. Bridge motif definitions start in I8; "
            "prototype admission starts in I10; positive ecology evidence remains closed."
        ),
        "source_artifacts_consumed": source_artifacts,
        "source_of_truth_check": (
            "original_artifact_or_runtime_record_verified"
            if source_ok
            else "missing_or_unverified_source_blocks_source_backed_claim"
        ),
        "motif_status": "hint_for_I8_not_motif_evidence",
        "x_i7_producer_residue_status": debt_status(producer_debt),
        "x_i7_medium_debt_status": debt_status(medium_debt),
        "x_i7_naturalization_debt_status": debt_status(naturalization_debt),
        "x_i7_demand_family": demand["x_i5_demand_family"],
        "x_i7_demand_component": demand["ecology_component"],
        "x_i7_candidate_count": len(candidates),
        "x_i7_top_match_score": candidates[0]["score"] if candidates else 0,
        "x_i7_source_backed_claim_allowed": status == "source_backed" and source_ok,
        "x_i7_bridge_motif_row_created": False,
        "x_i7_bridge_motif_success_claimed": False,
        "x_i7_prototype_row_opened": False,
        "x_i7_positive_ecology_evidence_opened": False,
        "x_i7_native_ecology_claim_opened": False,
        "x_unknown_field_review_status": "accepted_no_claim_effect",
    }
    return row


def candidate_link_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for row in rows:
        for rank, candidate in enumerate(row["candidate_capability_sources"], start=1):
            links.append(
                {
                    "coverage_id": row["coverage_id"],
                    "ecology_demand": row["ecology_demand"],
                    "capability_id": candidate["capability_id"],
                    "source_experiment": candidate["source_experiment"],
                    "rank": rank,
                    "score": candidate["score"],
                    "relation_kind": (
                        "exact_demand_tag"
                        if candidate["exact_matches"]
                        else "surface_family_or_token_overlap"
                    ),
                    "supply_family": candidate["supply_family"],
                    "coverage_status": row["coverage_status"],
                    "source_of_truth_check": row["source_of_truth_check"],
                    "debt_summary": {
                        "producer_residue": row["x_i7_producer_residue_status"],
                        "medium_debt": row["x_i7_medium_debt_status"],
                        "naturalization_debt": row["x_i7_naturalization_debt_status"],
                    },
                    "claim_ceiling": row["claim_ceiling"],
                }
            )
    return links


def coverage_status_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["coverage_status"], []).append(row["ecology_demand"])
    return dict(sorted(index.items()))


def demand_family_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["x_i7_demand_family"], []).append(row["ecology_demand"])
    return dict(sorted(index.items()))


def capability_match_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        for candidate in row["candidate_capability_sources"]:
            index.setdefault(candidate["capability_id"], []).append(row["ecology_demand"])
    return dict(sorted(index.items()))


def supply_family_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        for candidate in row["candidate_capability_sources"]:
            index.setdefault(candidate["supply_family"], []).append(row["ecology_demand"])
    return {key: sorted(set(values)) for key, values in sorted(index.items())}


def debt_type_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index = {
        "producer_residue": [],
        "medium_debt": [],
        "naturalization_debt": [],
    }
    for row in rows:
        if row["x_i7_producer_residue_status"] == "present":
            index["producer_residue"].append(row["ecology_demand"])
        if row["x_i7_medium_debt_status"] == "present":
            index["medium_debt"].append(row["ecology_demand"])
        if row["x_i7_naturalization_debt_status"] == "present":
            index["naturalization_debt"].append(row["ecology_demand"])
    return index


def first_probe_cluster(row: dict[str, Any]) -> str:
    status = row["coverage_status"]
    if status == "source_backed":
        return "source_artifact_admission"
    if status == "prototype_candidate":
        return "prototype_admission_pending"
    if status == "producer_mediated":
        return "producer_residue_isolation"
    if status == "medium_debt":
        return "medium_debt_resolution"
    if status == "naturalization_debt":
        return "withdrawal_or_substrate_carriage"
    if status == "missing_runtime_surface":
        return "missing_surface_definition"
    if status == "control_only":
        return "control_or_review_gate"
    return "not_applicable_or_blocked"


def first_probe_cluster_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(first_probe_cluster(row), []).append(row["ecology_demand"])
    return dict(sorted(index.items()))


def debt_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows_with_producer_residue": sum(
            row["producer_residue"] != ["none_identified_in_top_candidates"] for row in rows
        ),
        "rows_with_medium_debt": sum(
            row["medium_debt"] != ["none_identified_in_top_candidates"] for row in rows
        ),
        "rows_with_naturalization_debt": sum(
            row["naturalization_debt"] != ["none_identified_in_top_candidates"] for row in rows
        ),
    }


def build() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    demand_rows = i5["ecology_demand_rows"]
    supply_rows = i6["capability_supply_rows"]
    supply_by_id = {row["capability_id"]: row for row in supply_rows}
    rows = [coverage_row(demand, supply_rows, supply_by_id) for demand in demand_rows]
    schema = i4["schema_bundle"]["coverage_debt_row_schema"]
    coverage_enum = set(i4["coverage_status_enum"])
    i7_rule = i4["phase_b_separation_rules"]["I7"]
    required_schema_fields = set(schema["required_fields"])
    allowed_fields = (
        set(schema["required_fields"])
        | set(schema["optional_fields"])
        | {
            "coverage_id",
            "motif_status",
            "source_artifacts_consumed",
            "source_of_truth_check",
        }
    )
    links = candidate_link_rows(rows)
    data: dict[str, Any] = {
        "artifact_id": "n29_demand_supply_coverage_debt_i7",
        "experiment_id": "N29",
        "iteration": "I7",
        "title": "Demand / Supply Coverage And Debt Matrix",
        "status": "passed",
        "acceptance_state": "accepted_demand_supply_coverage_and_debt_matrix",
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
                "consumed_as": "coverage_schema_and_phase_b_boundary",
            },
            {
                "artifact_id": "n29_ecology_demand_matrix_i5",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_ecology_demand_matrix_i5.json"
                ),
                "status": i5.get("status", "not_recorded"),
                "output_digest": i5.get("output_digest", "not_recorded"),
                "consumed_as": "demand_side_matrix",
            },
            {
                "artifact_id": "n29_capability_supply_atlas_i6",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_capability_supply_atlas_i6.json"
                ),
                "status": i6.get("status", "not_recorded"),
                "output_digest": i6.get("output_digest", "not_recorded"),
                "consumed_as": "supply_side_atlas",
            },
        ],
        "coverage_policy": {
            "canonical_row_semantics": "one row = one I5 ecology demand matched against I6 supply",
            "i7_matching_is_not_bridge_motif_success": True,
            "i7_matching_is_not_prototype_evidence": True,
            "i7_matching_is_not_positive_ecology_evidence": True,
            "source_backed_status_meaning": (
                "a demand has a directly relevant source-backed capability surface; "
                "it remains a coverage mapping, not a runtime ecology proof"
            ),
            "source_of_truth_rule": (
                "I6 supply rows may orient matching, but source-backed statuses must carry "
                "original artifact manifests from the matched capability rows."
            ),
        },
        "phase_b_separation_rule_consumed": copy.deepcopy(i7_rule),
        "phase_b_i7_job": "demand_supply_coverage_debt_matching_only",
        "coverage_matrix_supported": True,
        "coverage_debt_rows": rows,
        "candidate_link_rows": links,
        "coverage_status_index": coverage_status_index(rows),
        "demand_family_index": demand_family_index(rows),
        "supply_family_index": supply_family_index(rows),
        "capability_match_index": capability_match_index(rows),
        "debt_type_index": debt_type_index(rows),
        "first_probe_cluster_index": first_probe_cluster_index(rows),
        "debt_summary": debt_summary(rows),
        "row_count_summary": {
            "coverage_debt_rows": len(rows),
            "candidate_link_rows": len(links),
            "demand_rows_consumed": len(demand_rows),
            "supply_rows_available": len(supply_rows),
            "demands_with_any_candidate_source": sum(
                1 for row in rows if row["candidate_capability_sources"]
            ),
            "demands_without_candidate_source": sum(
                1 for row in rows if not row["candidate_capability_sources"]
            ),
        },
        "bridge_motifs_created": False,
        "bridge_motif_library_opened": False,
        "bridge_motif_success_claimed": False,
        "prototype_rows_opened": False,
        "positive_ecology_evidence_opened": False,
        "implementation_evidence_opened": False,
        "native_ecology_claim_opened": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "native_shared_medium_coordination_opened": False,
        "claim_boundary_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "claim_ceiling": "demand_supply_coverage_and_debt_matrix_only_no_motifs_no_prototypes",
        "ready_for_iteration_8": False,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks = [
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check("i5_demand_matrix_passed", i5.get("status") == "passed"),
        check("i6_supply_atlas_passed", i6.get("status") == "passed"),
        check(
            "i7_phase_b_separation_rule_consumed",
            i7_rule == PHASE_B_I7_SEPARATION_RULES,
        ),
        check(
            "only_i4_i5_i6_sources_consumed",
            {row["artifact_id"] for row in data["source_artifacts"]}
            == {
                "n29_bridge_schema_i4",
                "n29_ecology_demand_matrix_i5",
                "n29_capability_supply_atlas_i6",
            },
        ),
        check(
            "coverage_row_count_matches_i5",
            len(rows) == len(demand_rows) == data["row_count_summary"]["demand_rows_consumed"],
        ),
        check(
            "candidate_link_rows_sparse_not_cartesian",
            0 < len(links) < len(demand_rows) * len(supply_rows),
            f"candidate_link_rows={len(links)} cartesian={len(demand_rows) * len(supply_rows)}",
        ),
        check(
            "all_coverage_rows_follow_i4_schema",
            all(required_schema_fields.issubset(row.keys()) for row in rows),
        ),
        check(
            "all_rows_have_coverage_id_and_motif_hint_status",
            all(row["coverage_id"] and row["motif_status"] == "hint_for_I8_not_motif_evidence" for row in rows),
        ),
        check(
            "all_i7_row_extensions_are_namespaced",
            all(
                all(key in allowed_fields or key.startswith("x_") for key in row)
                for row in rows
            ),
        ),
        check(
            "coverage_status_values_valid",
            all(row["coverage_status"] in coverage_enum for row in rows),
        ),
        check(
            "all_rows_have_coverage_reason",
            all(row["coverage_reason"] for row in rows),
        ),
        check(
            "all_rows_have_blocked_relabels",
            all(row["blocked_relabels"] for row in rows),
        ),
        check(
            "all_rows_have_native_readiness_status_and_gap",
            all(row["native_readiness_status"] and row["native_readiness_gap"] for row in rows),
        ),
        check(
            "all_rows_have_debt_status_fields",
            all(
                row["x_i7_producer_residue_status"] in {"present", "absent"}
                and row["x_i7_medium_debt_status"] in {"present", "absent"}
                and row["x_i7_naturalization_debt_status"] in {"present", "absent"}
                for row in rows
            ),
        ),
        check(
            "source_backed_rows_have_original_artifacts",
            all(
                row["coverage_status"] != "source_backed"
                or (
                    row["source_artifacts_consumed"]
                    and row["source_of_truth_check"] == "original_artifact_or_runtime_record_verified"
                )
                for row in rows
            ),
        ),
        check(
            "prototype_candidate_rows_do_not_open_prototypes",
            any(row["coverage_status"] == "prototype_candidate" for row in rows)
            and not data["prototype_rows_opened"]
            and all(not row["x_i7_prototype_row_opened"] for row in rows),
        ),
        check(
            "native_ready_surface_rows_have_review_gate_basis",
            all(
                row["coverage_status"] != "native_ready_surface"
                or any(
                    "native_ready_surface" in candidate["normalized_native_readiness_status"]
                    for candidate in row["candidate_capability_sources"]
                )
                for row in rows
            ),
        ),
        check(
            "debt_rows_remain_claim_bounded",
            all(
                row["native_readiness_status"] == "no_native_ready_surface_opened_by_I7"
                and row["claim_ceiling"]
                == "demand_supply_coverage_mapping_only_no_motif_no_prototype_no_native_ecology"
                for row in rows
            ),
        ),
        check(
            "all_rows_have_first_probe_implication",
            all(row["first_probe_implication"] for row in rows),
        ),
        check(
            "all_rows_have_candidate_or_missing_status",
            all(
                row["candidate_capability_sources"]
                or row["coverage_status"] == "missing_runtime_surface"
                for row in rows
            ),
        ),
        check(
            "bridge_motifs_not_created_or_claimed",
            not data["bridge_motifs_created"]
            and not data["bridge_motif_library_opened"]
            and not data["bridge_motif_success_claimed"]
            and all(not row["x_i7_bridge_motif_row_created"] for row in rows)
            and all(not row["x_i7_bridge_motif_success_claimed"] for row in rows),
        ),
        check(
            "motif_family_hints_do_not_open_motif_library",
            all(row["bridge_motif"] in MOTIF_HINTS for row in rows)
            and all(row["motif_status"] == "hint_for_I8_not_motif_evidence" for row in rows)
            and not data["bridge_motif_library_opened"],
        ),
        check(
            "positive_ecology_and_implementation_evidence_closed",
            not data["positive_ecology_evidence_opened"]
            and not data["implementation_evidence_opened"]
            and all(not row["x_i7_positive_ecology_evidence_opened"] for row in rows),
        ),
        check(
            "native_ecology_and_agency_claims_closed",
            not data["native_ecology_claim_opened"]
            and not data["native_agency_claim_opened"]
            and not data["native_ant_agency_opened"]
            and not data["native_colony_agency_opened"]
            and not data["native_shared_medium_coordination_opened"]
            and all(not row["x_i7_native_ecology_claim_opened"] for row in rows),
        ),
        check(
            "producer_residue_not_relabelled_native",
            all(
                row["coverage_status"] != "producer_mediated"
                or "native" in row["native_readiness_gap"]
                or "producer" in row["native_readiness_gap"]
                for row in rows
            )
            and not data["native_ecology_claim_opened"],
        ),
        check(
            "medium_debt_not_relabelled_native_shared_medium",
            all(
                row["coverage_status"] != "medium_debt"
                or "native coordination" in row["native_readiness_gap"]
                or "shared-medium" in row["native_readiness_gap"]
                for row in rows
            )
            and not data["native_shared_medium_coordination_opened"],
        ),
        check(
            "n12_n19_n20_gates_preserved",
            all(
                candidate["review_gate_status"]
                for row in rows
                for candidate in row["candidate_capability_sources"]
                if candidate["source_experiment"] in {"N12", "N19", "N20"}
            ),
        ),
        check(
            "ap4_ap5_nat4_gaps_not_hidden",
            all(
                row["coverage_status"] != "native_ready_surface"
                for row in rows
                if any(
                    candidate["source_experiment"] in {"N14", "N15", "N23", "N26"}
                    for candidate in row["candidate_capability_sources"]
                )
            ),
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
        "accepted_demand_supply_coverage_and_debt_matrix"
        if data["status"] == "passed"
        else "rejected_demand_supply_coverage_and_debt_matrix_failed_checks"
    )
    data["ready_for_iteration_8"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_8", data["ready_for_iteration_8"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 7 - Demand / Supply Coverage And Debt Matrix",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- coverage debt rows: `{data['row_count_summary']['coverage_debt_rows']}`",
        f"- candidate link rows: `{data['row_count_summary']['candidate_link_rows']}`",
        f"- demands with candidates: `{data['row_count_summary']['demands_with_any_candidate_source']}`",
        f"- demands without candidates: `{data['row_count_summary']['demands_without_candidate_source']}`",
        f"- bridge_motifs_created: `{str(data['bridge_motifs_created']).lower()}`",
        f"- bridge_motif_library_opened: `{str(data['bridge_motif_library_opened']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_8: `{str(data['ready_for_iteration_8']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 7 is the first demand/supply matching pass. It classifies",
        "coverage and debt, but it does not create bridge motifs, open prototype",
        "rows, or claim positive ecology evidence.",
        "",
        "## Coverage Status",
        "",
        "| Status | Row Count |",
        "| --- | ---: |",
    ]
    for status, row_ids in data["coverage_status_index"].items():
        lines.append(f"| `{status}` | {len(row_ids)} |")
    lines.extend(
        [
            "",
            "## Demand Families",
            "",
            "| Family | Row Count |",
            "| --- | ---: |",
        ]
    )
    for family, row_ids in data["demand_family_index"].items():
        lines.append(f"| `{family}` | {len(row_ids)} |")
    lines.extend(
        [
            "",
            "## Motif Hints",
            "",
            "| Motif Hint | Row Count |",
            "| --- | ---: |",
        ]
    )
    motif_counts = Counter(row["bridge_motif"] for row in data["coverage_debt_rows"])
    for motif, count in sorted(motif_counts.items()):
        lines.append(f"| `{motif}` | {count} |")
    lines.extend(
        [
            "",
            "## First Probe Clusters",
            "",
            "| Cluster | Row Count |",
            "| --- | ---: |",
        ]
    )
    for cluster, row_ids in data["first_probe_cluster_index"].items():
        lines.append(f"| `{cluster}` | {len(row_ids)} |")
    lines.extend(
        [
            "",
            "## Debt Summary",
            "",
            f"- rows_with_producer_residue: `{data['debt_summary']['rows_with_producer_residue']}`",
            f"- rows_with_medium_debt: `{data['debt_summary']['rows_with_medium_debt']}`",
            f"- rows_with_naturalization_debt: `{data['debt_summary']['rows_with_naturalization_debt']}`",
            "",
            "## Coverage Rows",
            "",
            "| Demand | Status | Top Candidate | Probe Implication |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in data["coverage_debt_rows"]:
        top = (
            row["candidate_capability_sources"][0]["capability_id"]
            if row["candidate_capability_sources"]
            else "none"
        )
        implication = row["first_probe_implication"].replace("|", "/")
        lines.append(
            f"| `{row['ecology_demand']}` | `{row['coverage_status']}` | "
            f"`{top}` | {implication} |"
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
            "I7 supports a coverage/debt matrix, not bridge motif success. It shows",
            "which ecology demands have source-backed, prototype-candidate,",
            "producer-mediated, medium-debt, naturalization-debt, control-only,",
            "or missing-surface coverage under the current N05-N28 supply stack.",
            "Candidate link rows are sparse audit edges, not a Cartesian matrix.",
            "Bridge motif labels are hints for I8 and carry",
            "`motif_status = hint_for_I8_not_motif_evidence` in every row.",
            "All coverage remains below native ecology, native agency, ant agency,",
            "colony agency, and native shared-medium coordination.",
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

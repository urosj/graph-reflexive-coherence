#!/usr/bin/env python3
"""Build N29 Iteration 6 capability supply atlas."""

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
I3_OUTPUT = EXPERIMENT / "outputs" / "n29_capability_atlas_i3.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_capability_supply_atlas_i6.json"
REPORT = EXPERIMENT / "reports" / "n29_capability_supply_atlas_i6.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_capability_supply_atlas_i6.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SUPPLY_FAMILIES = {
    "trace_aftereffect": {
        "description": "memory, trail, aftereffect, replay, and trace surfaces",
        "tokens": {"trace", "trail", "memory", "aftereffect", "history", "replay"},
    },
    "pressure_reserve_support": {
        "description": "support, reserve, perturbation, proxy, target, and regulation pressure surfaces",
        "tokens": {"pressure", "support", "reserve", "perturb", "proxy", "target", "regulation", "goal"},
    },
    "boundary_multi_basin_unit": {
        "description": "identity, self/environment, basin boundary, mobile boundary, and child-basin surfaces",
        "tokens": {"boundary", "identity", "basin", "mobile", "child", "self_environment", "environment"},
    },
    "closed_loop_perturbation_response": {
        "description": "closed-loop, feedback, recovery, response, and long-horizon closure surfaces",
        "tokens": {"loop", "feedback", "response", "closure", "closed", "recovery", "long_horizon", "cycle"},
    },
    "proxy_divergence_collapse": {
        "description": "proxy, target, route-selection, branch-collapse, and susceptibility surfaces",
        "tokens": {"proxy", "target", "selection", "route", "collapse", "susceptibility", "choice"},
    },
    "transfer_replay_relocation": {
        "description": "configuration transfer, substrate transfer, role relocation, and re-entry surfaces",
        "tokens": {"transfer", "substrate", "relocation", "reentry", "re-entry", "configuration"},
    },
    "formation_child_basin": {
        "description": "surplus, optionality, basin formation, split, and multi-basin formation surfaces",
        "tokens": {"formation", "surplus", "optionality", "split", "multi_basin", "basin"},
    },
    "medium_reshaping_generative_extractive": {
        "description": "shared-medium, construction, waste/isolation, generative, extractive, and medium-reshaping surfaces",
        "tokens": {
            "medium",
            "shared",
            "construction",
            "waste",
            "generative",
            "extractive",
            "reshaping",
            "resource",
        },
    },
    "route_choice_arbitration": {
        "description": "route choice, route arbitration, and affordance-selection surfaces",
        "tokens": {"route", "selection", "arbitration", "affordance", "choice"},
    },
    "regulation_homeostasis": {
        "description": "support regulation, perturbation recovery, floor preservation, and budget surfaces",
        "tokens": {"regulation", "support", "recovery", "floor", "budget", "retention", "homeostasis"},
    },
    "visual_or_report_only": {
        "description": "visual, report, and diagnostic surfaces that cannot substitute for runtime evidence",
        "tokens": {"visual", "report", "diagnostic", "image", "manifest"},
    },
    "control_only_or_negative": {
        "description": "review, contract, schema, readiness, control, and negative context; not direct supply evidence",
        "tokens": {"review", "contract", "readiness", "requirements", "schema", "control", "negative", "gate"},
    },
}

PHASE_B_I6_SEPARATION_RULES = {
    "job": "capability_supply_atlas_only",
    "must_not": [
        "create_coverage_debt_matches",
        "create_bridge_motifs",
        "open_prototype_rows",
    ],
}

PROTOTYPE_POTENTIAL_ENUM = {
    "none",
    "mapping_only_candidate",
    "visual_diagnostic_candidate",
    "source_backed_reconstruction_candidate",
    "runnable_runtime_candidate",
    "blocked_by_missing_source",
    "blocked_by_claim_boundary",
}

NORMALIZED_NATIVE_READINESS_ENUM = {
    "native_ready_surface",
    "producer_mediated",
    "artifact_level_only",
    "bounded_runtime_surface",
    "visual_diagnostic_only",
    "control_only",
    "naturalization_debt",
    "medium_debt",
    "blocked_by_review_gate",
    "blocked_by_missing_source",
}

NON_DIRECT_PROTOTYPE_CLASSES = {
    "review_gate_only",
    "schema_gate_only",
    "requirements_context_only",
    "historical_integration_context_only",
    "same_basin_signature_context",
    "long_horizon_constraint_context",
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


def card_text(card: dict[str, Any]) -> str:
    parts: list[str] = [
        card["capability_id"],
        card["source_experiment"],
        card["prototype_potential"],
    ]
    parts.extend(card["supplied_geometry_or_dynamic"])
    parts.extend(card["possible_ecology_demands"])
    return " ".join(parts).lower().replace("-", "_")


def groups_for_card(card: dict[str, Any]) -> list[str]:
    text = card_text(card)
    groups = [
        group_id
        for group_id, group in SUPPLY_FAMILIES.items()
        if any(token in text for token in group["tokens"])
    ]
    if card["prototype_potential"] in NON_DIRECT_PROTOTYPE_CLASSES:
        if "control_only_or_negative" not in groups:
            groups.append("control_only_or_negative")
    return groups or ["control_only_or_negative"]


def prototype_candidate_class(card: dict[str, Any]) -> str:
    potential = card["prototype_potential"]
    if potential in {"review_gate_only", "schema_gate_only", "requirements_context_only"}:
        return "gate_or_requirements_context_only"
    if potential in {
        "historical_integration_context_only",
        "same_basin_signature_context",
        "long_horizon_constraint_context",
    }:
        return "supporting_context_only"
    if "with_debt" in potential or "with_AP" in potential or "with_extension_dependency" in potential:
        return "direct_component_candidate_with_debt"
    if "component" in potential or "mapping" in potential:
        return "direct_component_candidate"
    return "supporting_context_only"


def normalized_prototype_potential(card: dict[str, Any]) -> str:
    potential = card["prototype_potential"]
    if potential in {"review_gate_only", "schema_gate_only", "requirements_context_only"}:
        return "none"
    if potential in {
        "historical_integration_context_only",
        "same_basin_signature_context",
        "long_horizon_constraint_context",
    }:
        return "mapping_only_candidate"
    if any(not artifact.get("exists") for artifact in card["source_artifacts"]):
        return "blocked_by_missing_source"
    if "AP4_gap" in potential or "AP5_gap" in potential:
        return "blocked_by_claim_boundary"
    if "component" in potential or "mapping" in potential:
        return "source_backed_reconstruction_candidate"
    return "mapping_only_candidate"


def normalized_native_readiness(card: dict[str, Any]) -> tuple[str, str]:
    status = card["native_readiness_status"].lower()
    source_experiment = card["source_experiment"]
    prototype_potential = card["prototype_potential"]
    if source_experiment in {"N12", "N19"}:
        return "blocked_by_review_gate", f"{source_experiment}_review_gate"
    if prototype_potential in {"schema_gate_only", "requirements_context_only", "review_gate_only"}:
        return "control_only", "N20_contract_or_requirements_gate"
    if any(not artifact.get("exists") for artifact in card["source_artifacts"]):
        return "blocked_by_missing_source", "missing"
    if card["medium_debt"] and card["medium_debt"] != "none":
        if "scoped native" in status or "mostly native" in status:
            return "bounded_runtime_surface", "source_closeout_with_medium_debt_visible"
        return "medium_debt", "source_closeout_with_medium_debt_visible"
    if card["producer_residue"] and card["producer_residue"] != "none":
        if "producer-mediated" in status or "producer mediated" in status:
            return "producer_mediated", "source_closeout_with_producer_residue_visible"
    if "artifact" in status or "historical" in status or "reviewed" in status:
        return "artifact_level_only", "source_closeout_or_review_gate"
    if "bounded" in status or "scoped native" in status or "mostly native" in status:
        return "bounded_runtime_surface", "source_closeout"
    if "visual" in status:
        return "visual_diagnostic_only", "visual_manifest_only"
    return "artifact_level_only", "source_closeout"


def possible_bridge_motif_tags(row: dict[str, Any]) -> list[str]:
    groups = set(row["x_i6_supply_group_ids"])
    tags: list[str] = []
    if {"trace_aftereffect", "pressure_reserve_support", "closed_loop_perturbation_response"} & groups:
        tags.append("trace_pressure_loop")
    if {"pressure_reserve_support", "formation_child_basin"} <= groups:
        tags.append("reserve_optionality_formation")
    if {"boundary_multi_basin_unit", "medium_reshaping_generative_extractive"} & groups:
        tags.append("boundary_shared_medium_unit")
    if {"proxy_divergence_collapse", "trace_aftereffect"} & groups:
        tags.append("proxy_susceptibility_reentry")
    if "transfer_replay_relocation" in groups:
        tags.append("transfer_replay_role_relocation")
    if "medium_reshaping_generative_extractive" in groups:
        tags.append("generative_extractive_medium_reshaping")
    return sorted(set(tags))


def supply_row(card: dict[str, Any]) -> dict[str, Any]:
    groups = groups_for_card(card)
    candidate_class = prototype_candidate_class(card)
    normalized_prototype = normalized_prototype_potential(card)
    normalized_readiness, readiness_basis = normalized_native_readiness(card)
    original_artifacts = [
        {
            "path": artifact["path"],
            "artifact_role": artifact["artifact_role"],
            "exists": artifact["exists"],
            "sha256": artifact["sha256"],
            "source_status": artifact["source_status"],
            "source_output_digest": artifact["source_output_digest"],
        }
        for artifact in card["source_artifacts"]
    ]
    row = copy.deepcopy(card)
    row.update(
        {
            "x_i6_supply_group_ids": groups,
            "x_i6_supply_family": groups[0],
            "x_i6_secondary_supply_families": groups[1:],
            "x_i6_direct_prototype_candidate_class": candidate_class,
            "x_i6_direct_prototype_candidate": candidate_class.startswith("direct_component_candidate"),
            "x_i6_prototype_potential_status": normalized_prototype,
            "x_i6_prototype_potential_is_not_prototype_evidence": True,
            "x_i6_normalized_native_readiness_status": normalized_readiness,
            "x_i6_native_readiness_basis": readiness_basis,
            "x_i6_original_artifacts_required_for_i7_claims": True,
            "x_i6_source_card_role": "supply_orientation_card_not_full_data_source",
            "x_i6_source_of_truth_rule": (
                "I3 capability card is an index; original artifacts, closeouts, runtime "
                "records, source reports, or visual manifests are required for I7+ claims."
            ),
            "x_i6_possible_bridge_motif_tags": [],
            "x_i6_coverage_match_opened": False,
            "x_i6_bridge_motif_created": False,
            "x_i6_prototype_row_opened": False,
            "x_i6_positive_ecology_evidence_opened": False,
            "x_i6_native_ecology_claim_opened": False,
            "x_i6_source_artifact_manifest": original_artifacts,
            "x_i6_why_not_stronger": (
                "I6 indexes supplied capability surfaces from I3 cards only. I7+ "
                "must return to original source artifacts before any coverage, "
                "motif, or prototype evidence claim."
            ),
            "x_unknown_field_review_status": "accepted_no_claim_effect",
        }
    )
    row["x_i6_possible_bridge_motif_tags"] = possible_bridge_motif_tags(row)
    return row


def supply_group_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {group_id: [] for group_id in SUPPLY_FAMILIES}
    for row in rows:
        for group_id in row["x_i6_supply_group_ids"]:
            index[group_id].append(row["capability_id"])
    return index


def source_experiment_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["source_experiment"], []).append(row["capability_id"])
    return dict(sorted(index.items()))


def prototype_candidate_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["x_i6_direct_prototype_candidate_class"], []).append(row["capability_id"])
    return dict(sorted(index.items()))


def debt_index(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    return {
        "producer_residue": [
            {"capability_id": row["capability_id"], "producer_residue": row["producer_residue"]}
            for row in rows
            if row["producer_residue"] and row["producer_residue"] != "none"
        ],
        "naturalization_debt": [
            {"capability_id": row["capability_id"], "naturalization_debt": row["naturalization_debt"]}
            for row in rows
            if row["naturalization_debt"] and row["naturalization_debt"] != "none"
        ],
        "medium_debt": [
            {"capability_id": row["capability_id"], "medium_debt": row["medium_debt"]}
            for row in rows
            if row["medium_debt"] and row["medium_debt"] != "none"
        ],
    }


def debt_ledgers(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    ledgers: dict[str, list[dict[str, Any]]] = {
        "producer_residue_ledger": [],
        "medium_debt_ledger": [],
        "naturalization_debt_ledger": [],
    }
    ledger_map = {
        "producer_residue": "producer_residue_ledger",
        "medium_debt": "medium_debt_ledger",
        "naturalization_debt": "naturalization_debt_ledger",
    }
    for row in rows:
        for debt_type, ledger_id in ledger_map.items():
            value = row[debt_type]
            if not value or value == "none":
                continue
            ledgers[ledger_id].append(
                {
                    "debt_id": f"DEBT.{row['source_experiment']}.{row['capability_id']}.{debt_type}".upper(),
                    "capability_id": row["capability_id"],
                    "debt_type": debt_type,
                    "source_basis": row["source_claim_ceiling"],
                    "debt_description": value,
                    "why_it_matters_for_ecology": (
                        "The ecology bridge may use this capability as orientation, but must not "
                        "relabel unresolved producer, medium, or naturalization debt as native "
                        "ecology behavior."
                    ),
                    "blocked_relabels": list(row["blocked_ecology_relabels"]),
                    "handoff_relevance": "candidate_N30_plus_naturalization_or_medium_target",
                }
            )
    return ledgers


def readiness_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {key: [] for key in sorted(NORMALIZED_NATIVE_READINESS_ENUM)}
    for row in rows:
        buckets[row["x_i6_normalized_native_readiness_status"]].append(row["capability_id"])
    return buckets


def review_gate_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["review_gate_status"], []).append(row["capability_id"])
    return dict(sorted(index.items()))


def source_coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_group_counts = Counter(row["source_group"] for row in rows)
    artifact_status_counts = Counter(
        artifact["source_status"]
        for row in rows
        for artifact in row["x_i6_source_artifact_manifest"]
    )
    missing_artifacts = [
        {
            "capability_id": row["capability_id"],
            "path": artifact["path"],
        }
        for row in rows
        for artifact in row["x_i6_source_artifact_manifest"]
        if not artifact["exists"]
    ]
    return {
        "meaning": "source inventory coverage only; not ecology demand coverage",
        "source_group_counts": dict(sorted(source_group_counts.items())),
        "artifact_status_counts": dict(sorted(artifact_status_counts.items())),
        "missing_source_artifacts": missing_artifacts,
    }


def serializable_supply_taxonomy() -> dict[str, dict[str, Any]]:
    return {
        family_id: {
            "description": family["description"],
            "tokens": sorted(family["tokens"]),
        }
        for family_id, family in SUPPLY_FAMILIES.items()
    }


def supply_surface_inventory(rows: list[dict[str, Any]]) -> dict[str, Any]:
    geometry_counter: Counter[str] = Counter()
    demand_counter: Counter[str] = Counter()
    relabel_counter: Counter[str] = Counter()
    for row in rows:
        geometry_counter.update(row["supplied_geometry_or_dynamic"])
        demand_counter.update(row["possible_ecology_demands"])
        relabel_counter.update(row["blocked_ecology_relabels"])
    return {
        "unique_supplied_geometry_count": len(geometry_counter),
        "unique_possible_ecology_demand_count": len(demand_counter),
        "unique_blocked_relabel_count": len(relabel_counter),
        "top_supplied_geometry": geometry_counter.most_common(12),
        "top_possible_ecology_demands": demand_counter.most_common(12),
        "top_blocked_ecology_relabels": relabel_counter.most_common(12),
    }


def build() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    cards = list(i3["capability_cards"])
    rows = [supply_row(card) for card in cards]
    capability_schema = i4["schema_bundle"]["capability_card_schema"]
    i6_rule = i4["phase_b_separation_rules"]["I6"]
    data: dict[str, Any] = {
        "artifact_id": "n29_capability_supply_atlas_i6",
        "experiment_id": "N29",
        "iteration": "I6",
        "title": "N05-N28 Capability Supply Atlas",
        "status": "passed",
        "acceptance_state": "accepted_capability_supply_atlas",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_capability_atlas_i3",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_capability_atlas_i3.json"
                ),
                "status": i3.get("status", "not_recorded"),
                "output_digest": i3.get("output_digest", "not_recorded"),
                "consumed_as": "capability_card_supply_source",
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
        "supply_policy": {
            "canonical_row_semantics": "one row = one imported capability card",
            "source_of_truth_rule": (
                "I3 card = index; original artifact / closeout / runtime record = evidence source"
            ),
            "capability_cards_are_full_data_source": False,
            "source_artifacts_required_for_i7_coverage_claim": True,
            "demand_matching_allowed": False,
            "coverage_debt_rows_allowed": False,
            "bridge_motifs_allowed": False,
            "prototype_rows_allowed": False,
            "direct_prototype_candidate_means": (
                "supply-side potential only; not a prototype row and not ecology evidence"
            ),
        },
        "source_of_truth_policy": {
            "i3_capability_cards_consumed_as": "orientation_index_and_claim_boundary_summary",
            "i3_capability_cards_must_not_be_consumed_as": "runtime_or_closeout_evidence",
            "source_backed_claims_require": [
                "original_artifact",
                "source_closeout",
                "runtime_record",
                "source_report",
                "visual_manifest_where_visual_claim_is_explicit",
            ],
            "missing_original_source_effect": "blocked_by_missing_source_or_orientation_only",
        },
        "phase_b_separation_rule_consumed": copy.deepcopy(i6_rule),
        "phase_b_i6_job": "capability_supply_atlas_only",
        "capability_supply_atlas_supported": True,
        "capability_supply_rows": rows,
        "supply_group_index": supply_group_index(rows),
        "supply_family_index": supply_group_index(rows),
        "capability_surface_taxonomy": serializable_supply_taxonomy(),
        "source_experiment_index": source_experiment_index(rows),
        "prototype_candidate_index": prototype_candidate_index(rows),
        "prototype_potential_enum": sorted(PROTOTYPE_POTENTIAL_ENUM),
        "debt_index": debt_index(rows),
        "debt_ledgers": debt_ledgers(rows),
        "review_gate_index": review_gate_index(rows),
        "native_readiness_index": readiness_index(rows),
        "native_readiness_enum": sorted(NORMALIZED_NATIVE_READINESS_ENUM),
        "supply_surface_inventory": supply_surface_inventory(rows),
        "source_coverage_summary": source_coverage_summary(rows),
        "row_count_summary": {
            "capability_supply_rows": len(rows),
            "supply_group_count": len(SUPPLY_FAMILIES),
            "source_experiment_count": len(source_experiment_index(rows)),
            "direct_prototype_candidate_count": sum(
                1 for row in rows if row["x_i6_direct_prototype_candidate"]
            ),
            "context_only_or_gate_count": sum(
                1 for row in rows if not row["x_i6_direct_prototype_candidate"]
            ),
        },
        "demand_supply_matching_opened": False,
        "coverage_debt_rows_opened": False,
        "bridge_motifs_created": False,
        "bridge_motif_success_claimed": False,
        "prototype_rows_opened": False,
        "positive_ecology_evidence_opened": False,
        "implementation_evidence_opened": False,
        "native_ecology_claim_opened": False,
        "claim_boundary_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "blocked_claim_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "claim_ceiling": "capability_supply_atlas_only_no_coverage_no_motifs_no_prototypes",
        "ready_for_iteration_7": False,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    required_schema_fields = set(capability_schema["required_fields"])
    allowed_fields = (
        set(capability_schema["required_fields"])
        | set(capability_schema["optional_fields"])
        | {"native_agency_claim_opened", "native_ecology_claim_opened", "positive_ecology_evidence_opened", "prototype_row_opened", "prior_experiment_revalidated"}
    )
    expected_supply_groups = {
        "trace_aftereffect",
        "pressure_reserve_support",
        "boundary_multi_basin_unit",
        "closed_loop_perturbation_response",
        "proxy_divergence_collapse",
        "transfer_replay_relocation",
        "formation_child_basin",
        "medium_reshaping_generative_extractive",
    }
    seen_supply_groups = {group for row in rows for group in row["x_i6_supply_group_ids"]}
    checks = [
        check("i3_capability_atlas_passed", i3.get("status") == "passed"),
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check(
            "i3_source_digest_matches",
            data["source_artifacts"][0]["output_digest"] == i3.get("output_digest"),
        ),
        check(
            "i6_phase_b_separation_rule_consumed",
            i6_rule == PHASE_B_I6_SEPARATION_RULES,
        ),
        check(
            "only_i3_and_i4_sources_consumed",
            {row["artifact_id"] for row in data["source_artifacts"]}
            == {"n29_capability_atlas_i3", "n29_bridge_schema_i4"},
        ),
        check(
            "uses_i3_as_index_not_full_evidence",
            data["source_of_truth_policy"]["i3_capability_cards_consumed_as"]
            == "orientation_index_and_claim_boundary_summary"
            and all(
                row["x_i6_source_card_role"] == "supply_orientation_card_not_full_data_source"
                for row in rows
            ),
        ),
        check(
            "capability_row_count_matches_i3",
            len(rows) == i3.get("capability_card_count") == 26,
        ),
        check(
            "all_i4_capability_card_schema_fields_present",
            all(required_schema_fields.issubset(row.keys()) for row in rows),
        ),
        check(
            "all_i6_row_extensions_are_namespaced",
            all(
                all(key in allowed_fields or key.startswith("x_") for key in row)
                for row in rows
            ),
        ),
        check(
            "required_supply_groups_present",
            expected_supply_groups.issubset(seen_supply_groups),
            f"seen_supply_groups={sorted(seen_supply_groups)}",
        ),
        check(
            "native_readiness_and_debt_preserved_row_locally",
            all(
                row["native_readiness_status"]
                and "producer_residue" in row
                and "naturalization_debt" in row
                and "medium_debt" in row
                for row in rows
            ),
        ),
        check(
            "native_readiness_normalized_without_claim_upgrade",
            all(
                row["x_i6_normalized_native_readiness_status"] in NORMALIZED_NATIVE_READINESS_ENUM
                and row["x_i6_native_readiness_basis"]
                for row in rows
            )
            and len(data["native_readiness_index"]["native_ready_surface"]) == 0,
        ),
        check(
            "debt_ledgers_emitted",
            set(data["debt_ledgers"])
            == {"producer_residue_ledger", "medium_debt_ledger", "naturalization_debt_ledger"}
            and sum(len(value) for value in data["debt_ledgers"].values()) > 0,
        ),
        check(
            "direct_prototype_candidates_identified_without_opening_rows",
            data["row_count_summary"]["direct_prototype_candidate_count"] > 0
            and not data["prototype_rows_opened"]
            and all(not row["x_i6_prototype_row_opened"] for row in rows),
        ),
        check(
            "prototype_potential_is_not_prototype_evidence",
            all(
                row["x_i6_prototype_potential_status"] in PROTOTYPE_POTENTIAL_ENUM
                and row["x_i6_prototype_potential_is_not_prototype_evidence"]
                for row in rows
            )
            and not data["prototype_rows_opened"]
            and not data["positive_ecology_evidence_opened"],
        ),
        check(
            "source_artifacts_required_for_future_coverage_claims",
            all(row["x_i6_original_artifacts_required_for_i7_claims"] for row in rows),
        ),
        check(
            "original_source_artifacts_available_for_reconstruction_candidates",
            all(
                row["x_i6_prototype_potential_status"] != "source_backed_reconstruction_candidate"
                or (
                    row["x_i6_source_artifact_manifest"]
                    and all(artifact["exists"] and artifact["sha256"] for artifact in row["x_i6_source_artifact_manifest"])
                )
                for row in rows
            ),
        ),
        check(
            "no_demand_supply_matching_or_coverage_rows_opened",
            not data["demand_supply_matching_opened"]
            and not data["coverage_debt_rows_opened"]
            and all(not row["x_i6_coverage_match_opened"] for row in rows),
        ),
        check(
            "coverage_status_assigned_false",
            all("coverage_status" not in row for row in rows),
        ),
        check(
            "no_bridge_motifs_created_or_claimed",
            not data["bridge_motifs_created"]
            and not data["bridge_motif_success_claimed"]
            and all(not row["x_i6_bridge_motif_created"] for row in rows),
        ),
        check(
            "positive_ecology_and_implementation_evidence_closed",
            not data["positive_ecology_evidence_opened"]
            and not data["implementation_evidence_opened"]
            and all(
                not row["x_i6_positive_ecology_evidence_opened"]
                and not row["x_i6_native_ecology_claim_opened"]
                for row in rows
            ),
        ),
        check(
            "claim_boundary_flags_false",
            all(value is False for value in data["claim_boundary_audit"].values())
            and data["claim_boundary_audit"] == data["blocked_claim_audit"],
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_capability_supply_atlas"
        if data["status"] == "passed"
        else "rejected_capability_supply_atlas_failed_checks"
    )
    data["ready_for_iteration_7"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_7", data["ready_for_iteration_7"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 6 - Capability Supply Atlas",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- capability supply rows: `{data['row_count_summary']['capability_supply_rows']}`",
        f"- direct prototype candidates: `{data['row_count_summary']['direct_prototype_candidate_count']}`",
        f"- coverage_debt_rows_opened: `{str(data['coverage_debt_rows_opened']).lower()}`",
        f"- demand_supply_matching_opened: `{str(data['demand_supply_matching_opened']).lower()}`",
        f"- bridge_motifs_created: `{str(data['bridge_motifs_created']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- ready_for_iteration_7: `{str(data['ready_for_iteration_7']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 6 is supply-only. It indexes I3 capability cards by supplied",
        "surface family and preserves native-readiness, producer residue,",
        "naturalization debt, medium debt, source claim ceilings, and blocked",
        "relabels. Direct prototype candidates are supply-side potential only;",
        "no prototype rows or coverage matches are opened.",
        "",
        "Source-of-truth rule: I3 cards are orientation indexes. Any I7+ coverage,",
        "motif, prototype, or runtime claim must return to the original source",
        "artifacts, closeouts, runtime records, source reports, or visual manifests",
        "listed in the row manifest.",
        "",
        "## Supply Families",
        "",
        "| Family | Capability Count |",
        "| --- | ---: |",
    ]
    for group_id, capability_ids in data["supply_family_index"].items():
        lines.append(f"| `{group_id}` | {len(capability_ids)} |")
    lines.extend(
        [
            "",
            "## Prototype Potential",
            "",
            "| Status | Capability Count |",
            "| --- | ---: |",
        ]
    )
    prototype_status_counts = Counter(
        row["x_i6_prototype_potential_status"] for row in data["capability_supply_rows"]
    )
    for status, count in sorted(prototype_status_counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Readiness And Debt",
            "",
            "| Normalized readiness status | Capability Count |",
            "| --- | ---: |",
        ]
    )
    for bucket, capability_ids in data["native_readiness_index"].items():
        lines.append(f"| `{bucket}` | {len(capability_ids)} |")
    lines.extend(
        [
            "",
            "## Debt Ledgers",
            "",
            "| Ledger | Row Count |",
            "| --- | ---: |",
        ]
    )
    for ledger_id, ledger_rows in data["debt_ledgers"].items():
        lines.append(f"| `{ledger_id}` | {len(ledger_rows)} |")
    lines.extend(
        [
            "",
            "## Recurring Supply Surfaces",
            "",
            "| Kind | Top Entries |",
            "| --- | --- |",
            "| Geometry/dynamic | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["supply_surface_inventory"]["top_supplied_geometry"][:6]
            )
            + " |",
            "| Possible ecology demand | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["supply_surface_inventory"]["top_possible_ecology_demands"][:6]
            )
            + " |",
            "| Blocked relabel | "
            + ", ".join(
                f"`{name}` ({count})"
                for name, count in data["supply_surface_inventory"]["top_blocked_ecology_relabels"][:6]
            )
            + " |",
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
            "I6 supports a capability supply atlas, not coverage. It makes the N05-N28",
            "supply side navigable for I7 by grouping supplied surfaces and preserving",
            "row-local debt and claim ceilings. Any later source-backed coverage, motif,",
            "or prototype claim must return to the original experiment artifacts named",
            "inside each card.",
            "",
            "Normalized readiness statuses are intentionally conservative. A row may",
            "be a bounded runtime surface or source-backed reconstruction candidate",
            "without becoming native ecology, native agency, or demand coverage.",
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

#!/usr/bin/env python3
"""Build N29 I12 boundary / shared-medium unit admission artifact."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
OUTPUT = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_i12.json"
REPORT = EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_i12.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_boundary_shared_medium_unit_i12.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_SPECS = [
    {
        "source_id": "n16_closeout_ap6_boundary",
        "path": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
        "n16_closeout_and_handoff.json",
        "consume_as": "boundary_discipline_source",
        "may_supply": [
            "AP6 artifact-level boundary separability",
            "claim boundary for internal/external separability",
        ],
        "must_not_supply": [
            "native selfhood",
            "native shared-medium coordination",
            "agent body",
            "multi-agent interaction",
        ],
    },
    {
        "source_id": "n16_boundary_requirements",
        "path": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
        "n16_basin_boundary_requirements_matrix.json",
        "consume_as": "boundary_requirement_and_control_source",
        "may_supply": [
            "leakage, support, coherence, and shared-medium separability requirements",
            "negative-control vocabulary for boundary relabels",
        ],
        "must_not_supply": [
            "native environment model",
            "semantic self/environment boundary",
            "agency",
        ],
    },
    {
        "source_id": "n25_closeout_bf_scope",
        "path": "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
        "outputs/n25_closeout_and_n26_handoff.json",
        "consume_as": "sub_basin_and_gap_history_context",
        "may_supply": [
            "BF5 scoped formation context",
            "record of the pre-Phase-8 native multi-basin gap",
        ],
        "must_not_supply": [
            "MB6 evidence",
            "native multi-basin runtime success",
            "agentic ecology component success",
        ],
    },
    {
        "source_id": "n25_1_phase8_bridge",
        "path": "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
        "outputs/n25_1_closeout_and_phase8_extension_handoff.json",
        "consume_as": "phase8_multi_basin_extension_bridge",
        "may_supply": [
            "requirements bridge for dedicated multi-basin runtime surfaces",
            "implementation boundary before N25.2 validation",
        ],
        "must_not_supply": [
            "runtime multi-basin evidence",
            "MB6 validation",
            "native shared-medium coordination",
        ],
    },
    {
        "source_id": "n25_2_closeout_mb6",
        "path": "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
        "n25_2_closeout_and_n26_handoff.json",
        "consume_as": "primary_scoped_multi_basin_runtime_source",
        "may_supply": [
            "MB6 N26-ready scoped multi-basin substrate evidence",
            "source-current runtime, replay, control, and stress discipline",
        ],
        "must_not_supply": [
            "native support",
            "agency",
            "sentience",
            "ant ecology implementation",
            "unscoped multi-basin substrate consumption",
        ],
    },
    {
        "source_id": "n25_2_runtime_positive",
        "path": "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
        "n25_2_native_runtime_positive_probe.json",
        "consume_as": "runtime_candidate_source",
        "may_supply": [
            "native runtime child-basin / multi-basin candidate trace",
        ],
        "must_not_supply": [
            "long-horizon ecology persistence",
            "semantic colony-local interaction",
        ],
    },
    {
        "source_id": "n25_2_multi_window_replay",
        "path": "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
        "n25_2_multi_window_persistence_replay.json",
        "consume_as": "multi_window_child_basin_replay_source",
        "may_supply": [
            "multi-window child-basin persistence replay evidence",
        ],
        "must_not_supply": [
            "general long-horizon ecology",
            "semantic memory or ownership",
        ],
    },
    {
        "source_id": "n25_2_control_matrix",
        "path": "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
        "n25_2_fail_closed_control_matrix.json",
        "consume_as": "multi_basin_control_source",
        "may_supply": [
            "label-only, visual-only, merge/leakage, and producer-as-native controls",
        ],
        "must_not_supply": [
            "positive runtime evidence by itself",
        ],
    },
    {
        "source_id": "n24_closeout_medium_capacity",
        "path": "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
        "outputs/n24_closeout_and_n25_handoff.json",
        "consume_as": "medium_capacity_context_only",
        "may_supply": [
            "bounded surplus / optionality context for medium-capacity interpretation",
        ],
        "must_not_supply": [
            "boundary/shared-medium unit success",
            "resource ownership",
            "choice",
        ],
    },
    {
        "source_id": "n28_closeout_medium_reshaping",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
        "outputs/n28_closeout_and_n29_handoff.json",
        "consume_as": "medium_reshaping_context_only",
        "may_supply": [
            "generative/extractive medium-reshaping context",
            "conservation caveat for visual interpretation",
        ],
        "must_not_supply": [
            "boundary/shared-medium unit success",
            "cooperation",
            "biological agency",
        ],
    },
    {
        "source_id": "n29_i10_prototype_admission_schema",
        "path": "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
        "outputs/n29_prototype_admission_schema_i10.json",
        "consume_as": "prototype_admission_schema_source",
        "may_supply": [
            "Prototype B route definition",
            "allowed initial bridge status policy",
        ],
        "must_not_supply": [
            "prototype success",
            "runtime ecology evidence",
        ],
    },
    {
        "source_id": "n29_i111c_prototype_a_context",
        "path": "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
        "outputs/n29_trace_pressure_loop_stronger_replay_stress_i111c.json",
        "consume_as": "prior_prototype_context_only",
        "may_supply": [
            "contrast with Prototype A evidence pattern",
        ],
        "must_not_supply": [
            "Prototype B boundary/shared-medium evidence",
            "shared-medium unit success",
        ],
    },
]

UNSAFE_CLAIM_FLAGS = {
    "agent_body_claim_allowed": False,
    "organism_environment_boundary_claim_allowed": False,
    "native_colony_boundary_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "semantic_trail_or_pheromone_substrate_claim_allowed": False,
    "resource_ownership_claim_allowed": False,
    "multi_agent_interaction_claim_allowed": False,
    "agency_claim_allowed": False,
    "life_claim_allowed": False,
    "sentience_claim_allowed": False,
    "native_support_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
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
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def nested_get(data: dict[str, Any], path: tuple[str, ...], default: Any = None) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def source_record(spec: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / spec["path"]
    parsed = load_json(path)
    return {
        "source_id": spec["source_id"],
        "path": spec["path"],
        "exists": path.exists(),
        "parseable_json": True,
        "file_sha256": sha256_file(path),
        "output_digest": parsed.get("output_digest", "not_recorded"),
        "artifact_id": parsed.get("artifact_id", "not_recorded"),
        "status": parsed.get("status", "not_recorded"),
        "acceptance_state": parsed.get("acceptance_state", "not_recorded"),
        "consume_as": spec["consume_as"],
        "may_supply": spec["may_supply"],
        "must_not_supply": spec["must_not_supply"],
    }


def build_source_artifacts() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows = [source_record(spec) for spec in SOURCE_SPECS]
    loaded = {row["source_id"]: load_json(ROOT / row["path"]) for row in rows}
    return rows, loaded


def build_unit_row(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    n16 = loaded["n16_closeout_ap6_boundary"]
    n25_2 = loaded["n25_2_closeout_mb6"]
    mb6_status = n25_2.get("final_mb_status", {})
    return {
        "prototype_unit_id": "N29.I12.PROTOTYPE_B.BOUNDARY_SHARED_MEDIUM_UNIT.PRIMARY",
        "prototype_family": "boundary_shared_medium_unit",
        "prototype_class": "boundary_mobile_expression",
        "prototype_subclass": "boundary_shared_medium_unit_not_mobile_body",
        "row_decision": "admitted_for_runtime_tranche",
        "prototype_success_claimed": False,
        "runtime_instantiation_claimed": False,
        "bridge_exemplar_claim_allowed": False,
        "mobile_boundary_claim_opened": False,
        "admission_status": "source_backed_runtime_tranche_admission_pending_i12abc",
        "claim_ceiling": "bounded_boundary_shared_medium_bridge_exemplar_candidate_pending_i12abc",
        "primary_runtime_source": {
            "source_id": "n25_2_closeout_mb6",
            "final_mb_ladder_rung": mb6_status.get("final_mb_ladder_rung", "not_recorded"),
            "mb6_supported": mb6_status.get("mb6_supported", False),
            "consumption_scope": nested_get(
                n25_2,
                ("n26_handoff", "allowed_n26_consumption"),
                "scoped multi-basin substrate evidence only",
            ),
        },
        "boundary_discipline_source": {
            "source_id": "n16_closeout_ap6_boundary",
            "final_supported_ap_level": nested_get(
                n16, ("closeout_result", "final_supported_ap_level"), "not_recorded"
            ),
            "final_scope": nested_get(n16, ("closeout_result", "final_scope"), "not_recorded"),
            "fully_native": nested_get(n16, ("closeout_result", "fully_native"), False),
        },
        "structural_parts": [
            {
                "part": "basin_side_state",
                "source_basis": "N25.2 scoped MB6 multi-basin substrate evidence plus N16 AP6 internal-side discipline",
                "required_i12abc_measurement": [
                    "source-current basin-side support/coherence",
                    "boundary-side assignment",
                    "basin-side persistence under replay",
                ],
            },
            {
                "part": "shared_or_adjacent_medium",
                "source_basis": "N16 shared-medium separability controls, N25.2 child-basin / multi-basin interface, N24/N28 context only if capacity or reshaping is needed",
                "required_i12abc_measurement": [
                    "coupling or leakage channel",
                    "shared-medium / adjacent-region attribution",
                    "merge pressure and leakage bounds",
                ],
            },
            {
                "part": "counterpart_region",
                "source_basis": "N25.2 multi-basin counterpart-side records; N16 negative controls prevent label-only neighbor claims",
                "required_i12abc_measurement": [
                    "counterpart support/coherence or child-basin record",
                    "separability from basin-side state",
                    "counterpart not reduced to relabeled old basin thickening",
                ],
            },
        ],
        "geometric_interpretation": (
            "Prototype B treats the ecology bridge unit as a three-part geometric "
            "surface: one basin-side region, one shared or adjacent medium channel, "
            "and one counterpart region. The important dynamic is not motion, choice, "
            "or colony behavior. It is whether the sides remain distinguishable while "
            "coupling/leakage through the medium is measurable and fail-closed controls "
            "reject merge, label-only, and visual-only success."
        ),
        "debt_distinctions": [
            {
                "debt_id": "DEBT.I12.MULTI_BASIN_EXACT_ROW_EXTRACTION_REQUIRED",
                "debt_kind": "multi_basin_debt",
                "description": "Runtime source is available from N25.2, but I12-A must extract one exact bridge-unit row rather than inherit MB6 wholesale.",
            },
            {
                "debt_id": "DEBT.I12.CHILD_BASIN_REPLAY_CONTROL_LINEAGE_REQUIRED",
                "debt_kind": "child_basin_debt",
                "description": "Child-basin records may be consumed only with replay/control lineage intact.",
            },
            {
                "debt_id": "DEBT.I12.MOBILE_BODY_READING_BLOCKED",
                "debt_kind": "mobile_boundary_debt",
                "description": "Mobile/body-like readings remain blocked; no mobile boundary or agent-body claim is opened.",
            },
            {
                "debt_id": "DEBT.I12.N16_N25_2_JOIN_REQUIRED",
                "debt_kind": "shared_medium_debt",
                "description": "N16 artifact-level shared-medium discipline and N25.2 runtime substrate must be joined before claiming a bridge exemplar.",
            },
            {
                "debt_id": "DEBT.I12.SEMANTIC_MEDIUM_LABELS_BLOCKED",
                "debt_kind": "semantic_medium_debt",
                "description": "Trail, pheromone, resource, and colony-local medium language remain blocked labels.",
            },
        ],
        "ecology_demand_served": [
            "scoped body/environment precursor without body claim",
            "shared-medium substrate precursor without pheromone/trail semantics",
            "neighbor/counterpart precursor without multi-agent interaction claim",
            "local interaction surface precursor without colony agency claim",
        ],
        "downstream_probe_suggestion": {
            "i12a": "extract or instantiate one source-current boundary/shared-medium unit row from N25.2-style runtime artifacts",
            "i12b": "run controls against label-only boundary, visual-only boundary, merge/leakage-as-success, producer-as-native, and native shared-medium coordination relabels",
            "i12c": "run replay/stress for basin-side, medium-side, and counterpart-region separability under bounded coupling",
        },
    }


def build_handoff() -> dict[str, Any]:
    return {
        "i12a_runtime_instantiation_required": True,
        "i12a_required_outputs": [
            "source-current bridge-unit runtime artifact",
            "basin-side trace",
            "shared/adjacent-medium trace",
            "counterpart-region trace",
            "artifact manifest with SHA-256 digests",
        ],
        "i12a_required_candidate_fields": [
            "runtime_family",
            "source_runtime_artifact_id",
            "source_runtime_artifact_digest",
            "unit_extraction_rule",
            "unit_id",
            "basin_side_region_id",
            "basin_side_support_or_coherence_trace",
            "basin_side_boundary_assignment",
            "medium_region_or_channel_id",
            "medium_coupling_or_leakage_trace",
            "medium_merge_pressure_metric",
            "counterpart_region_id",
            "counterpart_support_or_coherence_trace",
            "counterpart_separability_from_basin_side",
            "coupling_or_leakage_measure",
            "separability_measure",
            "merge_pressure_measure",
            "producer_residue",
            "claim_ceiling",
            "why_admitted",
            "why_not_stronger",
        ],
        "i12a_validation_fields": {
            "all_three_parts_present": True,
            "all_three_parts_have_source_current_runtime_trace": True,
            "medium_part_is_not_merely_label": True,
            "counterpart_region_is_not_old_basin_thickening": True,
            "n25_2_mb6_not_inherited_wholesale": True,
        },
        "i12b_controls_required": [
            "label_only_boundary_control",
            "visual_only_boundary_control",
            "merge_leakage_as_success_control",
            "old_basin_thickening_as_counterpart_control",
            "producer_as_native_control",
            "n16_artifact_boundary_as_native_runtime_relabel_control",
            "n25_2_mb6_as_ant_ecology_relabel_control",
            "native_shared_medium_coordination_relabel_control",
            "semantic_trail_or_pheromone_relabel_control",
            "agent_body_relabel_control",
        ],
        "i12b_expected_control_results": [
            {
                "control_id": "label_only_boundary_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_boundary_shared_medium_claim",
            },
            {
                "control_id": "visual_only_boundary_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_visual_backfill",
            },
            {
                "control_id": "merge_leakage_as_success_control",
                "expected_result": "failed_closed_or_demote",
                "rung_effect": "blocks_or_demotes_if_coupling_collapses_separability",
            },
            {
                "control_id": "old_basin_thickening_as_counterpart_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_counterpart_claim",
            },
            {
                "control_id": "producer_as_native_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_native_runtime_upgrade",
            },
            {
                "control_id": "n16_artifact_boundary_as_native_runtime_relabel_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_N16_artifact_to_native_runtime_relabel",
            },
            {
                "control_id": "n25_2_mb6_as_ant_ecology_relabel_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_MB6_to_ant_ecology_relabel",
            },
            {
                "control_id": "native_shared_medium_coordination_relabel_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_native_shared_medium_coordination_claim",
            },
            {
                "control_id": "semantic_trail_or_pheromone_relabel_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_semantic_medium_claim",
            },
            {
                "control_id": "agent_body_relabel_control",
                "expected_result": "failed_closed",
                "rung_effect": "blocks_agent_body_claim",
            },
        ],
        "i12c_replay_stress_required": [
            "artifact_only_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "medium_coupling_stress",
            "merge_pressure_stress",
            "counterpart_separability_stress",
        ],
        "i12c_pass_or_demote_conditions": {
            "artifact_only_replay": "same unit row reconstructs from artifact manifest",
            "snapshot_load_replay": "basin, medium, and counterpart assignments survive snapshot load",
            "duplicate_replay": "duplicate run preserves classification within tolerance",
            "medium_coupling_stress": "coupling changes medium trace without collapsing separability",
            "merge_pressure_stress": "increased merge pressure remains bounded or demotes claim",
            "counterpart_separability_stress": "counterpart remains distinguishable from basin-side state or row is demoted",
        },
        "hard_gates_before_iteration_13": {
            "i12a_runtime_artifact_present": True,
            "i12a_basin_side_trace_present": True,
            "i12a_medium_trace_present": True,
            "i12a_counterpart_trace_present": True,
            "i12a_manifest_sha256_present": True,
            "i12b_all_controls_run": True,
            "i12b_failed_open_count": 0,
            "i12b_merge_leakage_as_success_rejected": True,
            "i12b_old_basin_thickening_as_counterpart_rejected": True,
            "i12b_native_shared_medium_relabel_rejected": True,
            "i12b_agent_body_relabel_rejected": True,
            "i12c_replay_stress_complete": True,
            "i12c_counterpart_separability_survives_or_demotes": True,
            "i12c_merge_pressure_survives_or_demotes": True,
            "prototype_success_claimed": False,
            "native_shared_medium_coordination_opened": False,
            "agent_body_claim_opened": False,
            "multi_agent_interaction_opened": False,
            "semantic_trail_or_pheromone_substrate_opened": False,
        },
        "potential_failure_conditions": [
            "unit inherited from MB6 wholesale instead of extracted as one row",
            "medium trace is only a label, not a measured channel or region",
            "counterpart region is old basin thickening",
            "merge or leakage is treated as success rather than stress",
            "N16 artifact boundary is relabeled as native runtime boundary",
            "N25.2 MB6 is relabeled as ant ecology",
            "body/environment or agent-body language appears as a claim",
            "ready_for_iteration_13 becomes true before I12-A/B/C pass",
        ],
        "promotion_blockers": [
            "agent body",
            "organism/environment boundary",
            "native colony boundary",
            "native shared-medium coordination",
            "semantic trail or pheromone substrate",
            "resource ownership",
            "multi-agent interaction",
            "agency",
            "life",
        ],
    }


def build_output() -> dict[str, Any]:
    source_artifacts, loaded = build_source_artifacts()
    unit_row = build_unit_row(loaded)
    handoff = build_handoff()
    n25_2 = loaded["n25_2_closeout_mb6"]
    n16 = loaded["n16_closeout_ap6_boundary"]
    i10 = loaded["n29_i10_prototype_admission_schema"]

    checks = [
        check(
            "all_required_sources_exist_and_parse",
            all(row["exists"] and row["parseable_json"] for row in source_artifacts),
        ),
        check(
            "n16_consumed_as_boundary_discipline_not_native_shared_medium",
            nested_get(n16, ("closeout_result", "final_supported_ap_level")) == "AP6"
            and nested_get(n16, ("closeout_result", "fully_native")) is False
            and nested_get(
                n16,
                ("final_claim_boundary", "native_multi_basin_selfhood_supported"),
                False,
            )
            is False,
        ),
        check(
            "n25_2_consumed_as_scoped_mb6_runtime_source",
            nested_get(n25_2, ("final_mb_status", "mb6_supported")) is True
            and nested_get(n25_2, ("n26_handoff", "n26_unscoped_consumption_allowed"))
            is False,
        ),
        check(
            "n25_and_n25_1_not_promoted_to_runtime_mb6",
            loaded["n25_1_phase8_bridge"].get("acceptance_state", "").endswith(
                "no_runtime_evidence"
            )
            and "scoped_bf5" in loaded["n25_closeout_bf_scope"].get("acceptance_state", ""),
        ),
        check(
            "n24_n28_consumed_as_context_only",
            all(
                row["consume_as"].endswith("context_only")
                for row in source_artifacts
                if row["source_id"] in {"n24_closeout_medium_capacity", "n28_closeout_medium_reshaping"}
            ),
        ),
        check(
            "prototype_b_route_present_in_i10",
            any(
                row.get("source_motif_id") == "MOTIF.N29.BOUNDARY_SHARED_MEDIUM_UNIT"
                and row.get("iteration_target") == "I12"
                for row in i10.get("prototype_class_rows", [])
            ),
        ),
        check(
            "unit_has_basin_medium_counterpart_parts",
            {part["part"] for part in unit_row["structural_parts"]}
            == {"basin_side_state", "shared_or_adjacent_medium", "counterpart_region"},
        ),
        check(
            "i12abc_handoff_defined",
            all(bool(handoff[key]) for key in ("i12a_required_outputs", "i12b_controls_required", "i12c_replay_stress_required")),
        ),
        check(
            "i12a_exact_row_extraction_required",
            handoff["i12a_validation_fields"]["n25_2_mb6_not_inherited_wholesale"] is True
            and "unit_extraction_rule" in handoff["i12a_required_candidate_fields"],
        ),
        check(
            "i12b_expected_control_results_defined",
            len(handoff["i12b_expected_control_results"]) == len(handoff["i12b_controls_required"])
            and all(
                row["expected_result"] in {"failed_closed", "failed_closed_or_demote"}
                for row in handoff["i12b_expected_control_results"]
            ),
        ),
        check(
            "i13_hard_gates_keep_next_family_closed",
            handoff["hard_gates_before_iteration_13"]["i12b_failed_open_count"] == 0
            and handoff["hard_gates_before_iteration_13"]["prototype_success_claimed"] is False,
        ),
        check(
            "mobile_body_subclass_boundary_recorded",
            unit_row["prototype_subclass"] == "boundary_shared_medium_unit_not_mobile_body"
            and unit_row["mobile_boundary_claim_opened"] is False,
        ),
        check(
            "stable_debt_ids_present",
            {
                debt["debt_id"]
                for debt in unit_row["debt_distinctions"]
            }
            == {
                "DEBT.I12.CHILD_BASIN_REPLAY_CONTROL_LINEAGE_REQUIRED",
                "DEBT.I12.MOBILE_BODY_READING_BLOCKED",
                "DEBT.I12.MULTI_BASIN_EXACT_ROW_EXTRACTION_REQUIRED",
                "DEBT.I12.N16_N25_2_JOIN_REQUIRED",
                "DEBT.I12.SEMANTIC_MEDIUM_LABELS_BLOCKED",
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        ),
    ]

    output: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_i12",
        "experiment_id": "N29",
        "title": "Prototype B - Boundary / Shared-Medium Unit Admission",
        "iteration": "I12",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_boundary_shared_medium_unit_runtime_tranche_admission_pending_i12abc",
        "prototype_family": "boundary_shared_medium_unit",
        "prototype_class": "boundary_mobile_expression",
        "prototype_subclass": "boundary_shared_medium_unit_not_mobile_body",
        "source_artifacts": source_artifacts,
        "source_hierarchy": {
            "primary_runtime_source": "n25_2_closeout_mb6",
            "boundary_discipline_source": "n16_closeout_ap6_boundary",
            "control_sources": [
                "n16_boundary_requirements",
                "n25_2_control_matrix",
            ],
            "replay_source": "n25_2_multi_window_replay",
            "gap_and_requirements_history": [
                "n25_closeout_bf_scope",
                "n25_1_phase8_bridge",
            ],
            "context_only_sources": [
                "n24_closeout_medium_capacity",
                "n28_closeout_medium_reshaping",
                "n29_i111c_prototype_a_context",
            ],
        },
        "prototype_b_unit_row": unit_row,
        "prototype_b_claim_boundary": {
            "allowed_claim": "admitted bounded boundary/shared-medium bridge unit pending I12-A/B/C runtime, controls, and replay/stress",
            "claim_ceiling": "bounded_boundary_shared_medium_bridge_exemplar_candidate_pending_i12abc",
            "prototype_success_claimed": False,
            "runtime_ecology_success_claimed": False,
            "native_shared_medium_coordination_opened": False,
            "ant_ecology_implementation_opened": False,
            "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        },
        "i12abc_handoff_contract": handoff,
        "ready_for_i12a_i12b_i12c": True,
        "ready_for_iteration_13": False,
        "why_not_iteration_13_yet": "Prototype B still needs I12-A/B/C runtime extraction, controls, and replay/stress before the next prototype family.",
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    output["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["failed_checks"] = [row["check_id"] for row in output["checks"] if not row["passed"]]
    if output["failed_checks"]:
        output["status"] = "failed"
        output["acceptance_state"] = "failed_boundary_shared_medium_unit_admission"
        output["ready_for_i12a_i12b_i12c"] = False
    return finalize(output)


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def write_report(path: Path, data: dict[str, Any]) -> None:
    unit = data["prototype_b_unit_row"]
    lines = [
        "# N29 Iteration 12 - Boundary / Shared-Medium Unit",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Main Read",
        "",
        "I12 admits Prototype B as a boundary/shared-medium unit design. It does not "
        "claim prototype success yet. The source hierarchy is now explicit: N25.2 "
        "is the primary scoped MB6 runtime source, N16 supplies AP6 boundary "
        "discipline, N25/N25.1 explain the gap-to-implementation chain, and "
        "N24/N28 are context-only sources for medium capacity or reshaping.",
        "",
        "The bridge unit has three required geometric parts:",
        "",
    ]
    for part in unit["structural_parts"]:
        lines.append(f"- `{part['part']}`: {part['source_basis']}")
    lines.extend(
        [
            "",
            "Geometric interpretation:",
            "",
            unit["geometric_interpretation"],
            "",
            "## Source Hierarchy",
            "",
            "| Source | Consumed As | Status | Output Digest |",
            "|---|---|---|---|",
        ]
    )
    for row in data["source_artifacts"]:
        lines.append(
            f"| `{row['source_id']}` | `{row['consume_as']}` | "
            f"`{row['status']}` | `{row['output_digest']}` |"
        )
    lines.extend(
        [
            "",
            "## Debt Records",
            "",
            "| Debt ID | Meaning |",
            "|---|---|",
        ]
    )
    for debt in unit["debt_distinctions"]:
        lines.append(f"| `{debt['debt_id']}` | {debt['description']} |")
    lines.extend(
        [
            "",
            "## I12-A/B/C Handoff",
            "",
            "I12-A must extract or instantiate the source-current unit row. I12-B must "
            "run the fail-closed control matrix. I12-C must replay and stress the "
            "basin-side, shared/adjacent-medium, and counterpart-region separability.",
            "",
            "Required controls:",
            "",
        ]
    )
    for control in data["i12abc_handoff_contract"]["i12b_controls_required"]:
        lines.append(f"- `{control}`")
    lines.extend(
        [
            "",
            "I12-A required candidate fields include:",
            "",
        ]
    )
    for field in data["i12abc_handoff_contract"]["i12a_required_candidate_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(
        [
            "",
            "Hard gates before I13:",
            "",
        ]
    )
    for gate, expected in data["i12abc_handoff_contract"][
        "hard_gates_before_iteration_13"
    ].items():
        lines.append(f"- `{gate}` = `{expected}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: admitted bounded boundary/shared-medium bridge unit pending "
            "I12-A/B/C runtime, controls, and replay/stress.",
            "",
            "Blocked: agent body, organism/environment boundary, native colony "
            "boundary, native shared-medium coordination, semantic trail or "
            "pheromone substrate, resource ownership, multi-agent interaction, "
            "agency, life, sentience, native support, and Phase 8 completion.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUTPUT, data)
    write_report(REPORT, data)


if __name__ == "__main__":
    main()

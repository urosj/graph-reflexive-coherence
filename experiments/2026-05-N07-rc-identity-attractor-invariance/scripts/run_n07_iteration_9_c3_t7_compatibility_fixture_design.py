"""Run N07 Iteration 9 C3/T7 compatibility fixture design.

This is a design/freeze iteration only. It declares the competing-basin C3/T7
fixture, metric contract, support digest inputs, source-control replay
requirements, and artifact-replay requirements before any compatibility probe
is run.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
CONFIGS = N07 / "configs"
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"
MANIFEST_PATH = CONFIGS / "n07_fixture_manifest_v1.json"
ITERATION_8_OUTPUT_PATH = OUTPUTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.json"
ITERATION_8_REPORT_PATH = REPORTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.md"
ITERATION_7B_OUTPUT_PATH = OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json"
ITERATION_7B_REPORT_PATH = REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md"
FIXTURE_PATH = CONFIGS / "n07_c3_t7_compatibility_fixture_v1.json"
OUTPUT_PATH = OUTPUTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.json"
REPORT_PATH = REPORTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_9_c3_t7_compatibility_fixture_design.py"
)

GATE_VECTOR_FIELDS = [
    "support",
    "stability",
    "attractivity",
    "invariance",
    "lineage_current",
    "reflexive_closure",
    "compatibility",
    "artifact_replay",
]

COMPATIBILITY_CONTROL_CEILINGS = {
    "destructive_interference": "ID5",
    "ambiguous_overlap": "ID5",
    "wrong_basin": "ID5",
    "hidden_support_field": "ID5",
    "budget_discontinuity": "ID5",
    "support_drift_beyond_threshold": "ID5",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _claim_flags(manifest: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(manifest["claim_boundary"]["claim_flags"])}


def _source_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        {
            "name": "n07_iteration_8_c1_t6_artifact_replay_closeout",
            "path": _rel(ITERATION_8_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_8_OUTPUT_PATH),
        },
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure",
            "path": _rel(ITERATION_7B_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_7B_OUTPUT_PATH),
        },
    ]


def _source_reports() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_8_c1_t6_artifact_replay_closeout_report",
            "path": _rel(ITERATION_8_REPORT_PATH),
            "sha256": _file_sha256(ITERATION_8_REPORT_PATH),
        },
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure_report",
            "path": _rel(ITERATION_7B_REPORT_PATH),
            "sha256": _file_sha256(ITERATION_7B_REPORT_PATH),
        }
    ]


def _support_surface_descriptor(
    *,
    support_area_id: str,
    basin_id: str,
    support_node_ids: list[int],
    support_edge_ids: list[int],
    support_port_ids: list[str],
    role: str,
    source_digest: str | None,
) -> dict[str, Any]:
    return {
        "descriptor_kind": "n07_c3_t7_design_support_surface_descriptor",
        "support_area_id": support_area_id,
        "basin_id": basin_id,
        "support_node_ids": support_node_ids,
        "support_edge_ids": support_edge_ids,
        "support_port_ids": support_port_ids,
        "role": role,
        "source_digest": source_digest,
        "design_only": True,
    }


def _support_area_digest_input(
    *,
    support_area_id: str,
    support_node_ids: list[int],
    support_edge_ids: list[int],
    support_port_ids: list[str],
    support_surface_digest: str,
) -> dict[str, Any]:
    return {
        "support_area_id": support_area_id,
        "candidate_identity_carrier_type": "coherence_basin",
        "support_node_ids": support_node_ids,
        "support_edge_ids": support_edge_ids,
        "support_port_ids": support_port_ids,
        "lineage_status": "fixed_c3_t7_fixture_design",
        "lineage_map_digest": None,
        "support_surface_digest": support_surface_digest,
        "event_time_key": "n07_i9_c3_t7_fixture_design_no_probe",
        "scheduler_event_index": None,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
    }


def _support_area_row(
    *,
    support_area_id: str,
    basin_id: str,
    support_node_ids: list[int],
    support_edge_ids: list[int],
    support_port_ids: list[str],
    role: str,
    source_digest: str | None,
) -> dict[str, Any]:
    descriptor = _support_surface_descriptor(
        support_area_id=support_area_id,
        basin_id=basin_id,
        support_node_ids=support_node_ids,
        support_edge_ids=support_edge_ids,
        support_port_ids=support_port_ids,
        role=role,
        source_digest=source_digest,
    )
    support_surface_digest = _digest(descriptor)
    digest_input = _support_area_digest_input(
        support_area_id=support_area_id,
        support_node_ids=support_node_ids,
        support_edge_ids=support_edge_ids,
        support_port_ids=support_port_ids,
        support_surface_digest=support_surface_digest,
    )
    support_area_digest = _digest(digest_input)
    return {
        **digest_input,
        "basin_id": basin_id,
        "role": role,
        "support_area_digest": support_area_digest,
        "support_area_digest_input": digest_input,
        "support_surface_descriptor": descriptor,
        "support_digest_replay_required": True,
        "visual_is_evidence_source": False,
    }


def _metric_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    base_metric = manifest["metric_definitions"]["coherence_compatibility"]
    metrics = [
        {
            "metric_name": "a_support_retention_near_b",
            "metric_kind": "support_retention",
            "target_basin": "A",
            "source_support_area_id": "n07_support_area_A_v1",
            "threshold": 0.85,
            "comparison": "greater_than_or_equal",
            "runtime_visible_inputs_required": [
                "A_support_area_digest",
                "A_support_mass_before",
                "A_support_mass_after_near_B",
                "node_plus_packet_budget_surface",
            ],
        },
        {
            "metric_name": "b_support_retention_near_a",
            "metric_kind": "support_retention",
            "target_basin": "B",
            "source_support_area_id": "n07_support_area_B_v1",
            "threshold": 0.85,
            "comparison": "greater_than_or_equal",
            "runtime_visible_inputs_required": [
                "B_support_area_digest",
                "B_support_mass_before",
                "B_support_mass_after_near_A",
                "node_plus_packet_budget_surface",
            ],
        },
        {
            "metric_name": "destructive_interference_score",
            "metric_kind": "interference",
            "threshold": 0.15,
            "comparison": "less_than_or_equal",
            "primary_blocker": "destructive_interference",
            "runtime_visible_inputs_required": [
                "A_support_loss",
                "B_support_loss",
                "shared_U_flux_balance",
                "node_plus_packet_budget_surface",
            ],
        },
        {
            "metric_name": "ambiguous_overlap_score",
            "metric_kind": "support_overlap",
            "threshold": 0.2,
            "comparison": "less_than_or_equal",
            "primary_blocker": "ambiguous_overlap",
            "runtime_visible_inputs_required": [
                "A_support_node_ids",
                "B_support_node_ids",
                "lineage_status",
                "shared_U_node_ids",
            ],
        },
        {
            "metric_name": "wrong_basin_leakage_score",
            "metric_kind": "wrong_basin_leakage",
            "threshold": 0.1,
            "comparison": "less_than_or_equal",
            "primary_blocker": "wrong_basin",
            "runtime_visible_inputs_required": [
                "A_flux_into_B_support",
                "B_flux_into_A_support",
                "shared_U_route_context",
            ],
        },
        {
            "metric_name": "hidden_support_rejection_rule",
            "metric_kind": "schema_guard",
            "threshold": 0,
            "comparison": "must_equal",
            "metric_formula": "hidden_support_field_count == 0",
            "metric_semantics": (
                "Count support-affecting fields not present in the declared "
                "support_area_digest_input or source support rows. The metric "
                "passes only when no hidden support fields are consumed."
            ),
            "primary_blocker": "hidden_support_field",
            "runtime_visible_inputs_required": [
                "support_area_digest_input",
                "source_artifact_digest",
                "declared_support_rows",
            ],
        },
    ]
    return {
        "metric_id": base_metric["metric_id"],
        "source_metric_conditions": base_metric["conditions"],
        "frozen_before_probe": True,
        "compatibility_gate_mapping": {
            "all_metrics_pass": "compatibility=pass",
            "any_metric_fails": "compatibility=blocked",
            "probe_not_run": "compatibility=not_measured",
        },
        "metrics": metrics,
        "metric_names": [metric["metric_name"] for metric in metrics],
        "thresholds_are_frozen": True,
        "hidden_report_side_metric_allowed": False,
    }


def _control_requirements(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    blockers = {
        control["control_id"]: control["primary_blocker"]
        for control in manifest["controls"]
    }
    rows: list[dict[str, Any]] = []
    for control_id, ceiling in COMPATIBILITY_CONTROL_CEILINGS.items():
        rows.append(
            {
                "control_id": control_id,
                "primary_blocker": blockers[control_id],
                "declared_before_probe": True,
                "must_emit_source_control_row_in_iteration_9b": True,
                "must_replay_from_source_artifact_in_iteration_9c": True,
                "control_gate": "compatibility",
                "gate_specific_derived_id_ceiling": ceiling,
                "claim_flags_must_remain_false": True,
            }
        )
    return rows


def _gate_vector_from_iteration_8(iteration_8: Mapping[str, Any]) -> dict[str, str]:
    source = dict(iteration_8["c1_t6_closeout_row"]["gate_vector"])
    source["compatibility"] = "not_measured"
    source["artifact_replay"] = "not_measured"
    return {field: source[field] for field in GATE_VECTOR_FIELDS}


def _fixture(
    *,
    manifest: Mapping[str, Any],
    iteration_8: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    closeout = iteration_8["c1_t6_closeout_row"]
    direct_iteration_7b = _load_json(ITERATION_7B_OUTPUT_PATH)
    source_t6_state = iteration_8["source_outputs"]["iteration_7b"][
        "source_backed_t6_chain"
    ]["later_cycle_state_row"]
    source_t6_support_digest = closeout["support_area_digest"]
    a_support = _support_area_row(
        support_area_id="n07_support_area_A_v1",
        basin_id="n07_basin_A_candidate_v1",
        support_node_ids=source_t6_state["support_node_ids"],
        support_edge_ids=[300, 301, 302, 306],
        support_port_ids=[
            "A_support_front",
            "A_support_rear",
            "A_support_shared_U",
            "A_support_reentry",
        ],
        role="candidate_A_source_backed_c1_t6_basin_reexpressed_for_c3_design",
        source_digest=source_t6_support_digest,
    )
    b_support = _support_area_row(
        support_area_id="n07_support_area_B_v1",
        basin_id="n07_basin_B_competitor_v1",
        support_node_ids=[40, 41, 42],
        support_edge_ids=[303, 304, 305, 307],
        support_port_ids=[
            "B_support_front",
            "B_support_rear",
            "B_support_shared_U",
            "B_support_reentry",
        ],
        role="candidate_B_declared_competing_basin_design_only",
        source_digest=None,
    )
    shared_u = {
        "neighborhood_id": "n07_U_shared_A_B_competing_basin_v1",
        "node_ids": [33, 34, 35],
        "edge_ids": [308, 309, 310, 311],
        "ports": [
            "U_to_A_front",
            "U_to_A_rear",
            "U_to_B_front",
            "U_to_B_rear",
        ],
        "connects_support_area_ids": [
            a_support["support_area_id"],
            b_support["support_area_id"],
        ],
        "wrong_basin_leakage_measured": True,
        "route_choice_claim_allowed": False,
    }
    t7_family = {
        "topology_family_id": "n07_T7_compatibility",
        "declaration_source": "n07_c3_t7_compatibility_fixture_v1",
        "manifest_extension_status": "post_iteration_8_fixture_extension",
        "frozen_manifest_topology_family_present": False,
        "frozen_manifest_not_mutated": True,
        "target_id_level": "ID6",
        "expected_maximum_id_ceiling": "ID6_only_after_9b_compatibility_and_9c_artifact_replay",
        "gate_under_test": "compatibility",
        "primary_positive_metric": "n07_coherence_compatibility_v1",
        "paired_negative_control_topologies": sorted(
            COMPATIBILITY_CONTROL_CEILINGS
        ),
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_ids": [
            a_support["support_area_id"],
            b_support["support_area_id"],
        ],
        "shared_neighborhood_U": shared_u["neighborhood_id"],
        "budget_surface": "node_plus_packet",
        "probe_run": False,
        "compatibility_evidence_emitted": False,
        "claim_flags": dict(claim_flags),
    }
    c3_composite = {
        "composite_topology_id": "n07_C3_competing_basin_compatibility_candidate",
        "source_manifest_composite_topology": next(
            row
            for row in manifest["composite_topologies"]
            if row["composite_topology_id"]
            == "n07_C3_competing_basin_compatibility_candidate"
        ),
        "primitive_blocks_combined": [
            "n07_T1_support_area_minimal",
            "n07_T2_stable_well_basin",
            "n07_T3_attractor_neighborhood",
            "n07_T5_lineage_current_invariance",
            "n07_T6_reflexive_closure",
            "n07_T7_compatibility",
        ],
        "manifest_primitive_blocks_combined": next(
            row
            for row in manifest["composite_topologies"]
            if row["composite_topology_id"]
            == "n07_C3_competing_basin_compatibility_candidate"
        )["primitive_blocks_combined"],
        "primitive_extension_policy": (
            "The frozen Iteration 2 C3 manifest declares a minimal T2/T3 "
            "compatibility sketch. Iteration 9 extends C3 after the Iteration 8 "
            "C1/T6 closeout by composing the closed ID5 chain with T7 "
            "compatibility. The frozen manifest is not rewritten; 9-B/9-C use "
            "this fixture as the authoritative C3/T7 extension contract."
        ),
        "primitive_extension_requires_fixture_validation": True,
        "source_context_closeout_row_id": closeout["row_id"],
        "source_context_closeout_row_digest": closeout["closeout_row_digest"],
        "source_context_derived_id_ceiling": "ID5",
        "design_iteration_derived_id_ceiling": "ID5",
        "id6_requires": [
            "iteration_9b_compatibility_pass",
            "iteration_9c_artifact_replay_pass",
            "all_claim_flags_false",
        ],
        "claim_flags": dict(claim_flags),
    }
    row_schema = iteration_8["source_outputs"]["iteration_1"]["id_ladder_schema"]
    return {
        "schema": "n07_c3_t7_compatibility_fixture_v1",
        "fixture_id": "n07_c3_t7_competing_basin_compatibility_fixture_v1",
        "purpose": "design_only_no_probe_no_id_promotion",
        "manifest_extension_policy": {
            "frozen_manifest_path": _rel(MANIFEST_PATH),
            "frozen_manifest_sha256": _file_sha256(MANIFEST_PATH),
            "manifest_remains_frozen": True,
            "topology_family_extension_id": "n07_T7_compatibility",
            "extension_declared_in_fixture": True,
            "iteration_9b_9c_validation_source": _rel(FIXTURE_PATH),
            "rationale": (
                "Changing n07_fixture_manifest_v1 after Iteration 2 would "
                "invalidate pinned prior artifacts. Iteration 9 therefore "
                "declares T7 as a post-closeout fixture extension and records "
                "that downstream C3/T7 iterations validate against this fixture."
            ),
        },
        "source_iteration_8_closeout_row_digest": closeout["closeout_row_digest"],
        "source_iteration_7b_direct_artifact": {
            "path": _rel(ITERATION_7B_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_7B_OUTPUT_PATH),
            "object_digest": _digest(direct_iteration_7b),
            "matches_iteration_8_embedded_7b": _digest(direct_iteration_7b)
            == _digest(iteration_8["source_outputs"]["iteration_7b"]),
            "later_cycle_state_digest": direct_iteration_7b["source_backed_t6_chain"][
                "later_cycle_state_row"
            ]["state_digest"],
        },
        "topology_family": t7_family,
        "composite_topology": c3_composite,
        "basins": {
            "A": {
                "basin_id": "n07_basin_A_candidate_v1",
                "source_status": "source_backed_c1_t6_nodes_structurally_reexpressed_for_c3",
                "source_backing_scope": {
                    "support_node_ids": "source_backed_from_iteration_7b_later_cycle_state_row",
                    "support_area_digest": "source_backed_from_iteration_8_closeout",
                    "support_edge_ids": "c3_design_extension",
                    "support_port_ids": "c3_design_extension",
                },
                "structural_reexpression_note": (
                    "Basin A imports the source-backed C1/T6 support nodes and "
                    "support digest, then declares new C3-specific edge/port ids "
                    "for the competing-basin fixture. The new edges and ports are "
                    "design extensions, not prior runtime evidence."
                ),
                "source_support_area_digest": source_t6_support_digest,
                "support_area_row": a_support,
            },
            "B": {
                "basin_id": "n07_basin_B_competitor_v1",
                "source_status": "declared_design_fixture_until_iteration_9b",
                "source_backing_required_in_iteration_9b": True,
                "source_backing_requirement": (
                    "Iteration 9-B must emit source-backed B support/probe rows "
                    "before B can be used as compatibility evidence. This design "
                    "row alone is not evidence for B-basin identity."
                ),
                "support_area_row": b_support,
            },
        },
        "shared_neighborhood_U": shared_u,
        "competition_semantics": {
            "definition": (
                "Competing basins are structurally coupled alternatives on the "
                "same coherence/flux field. They share or border a local "
                "neighborhood U such that coherence, flux, support evidence, "
                "or basin legibility can be captured by, leaked into, or "
                "disturbed by either basin."
            ),
            "not_meant_as": [
                "semantic_choice",
                "agency",
                "goal_directed_competition",
                "biological_competition",
                "identity_acceptance",
            ],
            "competition_axes": [
                "shared_neighborhood_U",
                "flux_ambiguity",
                "support_overlap_risk",
                "attractor_interference",
                "wrong_basin_leakage",
                "artifact_replay_identity_ambiguity",
            ],
            "iteration_9b_question": (
                "Does Basin A remain distinct, coherent, and replayable as A "
                "when Basin B is source-backed and present in the shared-U "
                "compatibility fixture?"
            ),
            "claim_boundary": (
                "A positive result would support compatibility of an ID5 basin "
                "near another basin; it would not prove semantic choice, agency, "
                "identity acceptance, RC identity collapse, or biological identity."
            ),
        },
        "compatibility_metric_contract": _metric_contract(manifest),
        "control_requirements": _control_requirements(manifest),
        "source_control_replay_requirements": {
            "iteration_9b": "emit probe/control rows from the frozen fixture",
            "iteration_9c": "replay 9-B source probe/control rows from artifacts only",
            "synthetic_closeout_controls_allowed": False,
            "gate_specific_ceilings_required": True,
            "b_basin_source_backing_required_in_iteration_9b": True,
        },
        "artifact_replay_requirements": {
            "artifact_only": True,
            "private_runtime_state_allowed": False,
            "required_chain": [
                "A_support_area_row",
                "B_support_area_row",
                "shared_neighborhood_U",
                "compatibility_metric_records",
                "source_control_rows",
                "budget_records",
                "closeout_row",
            ],
            "support_area_digest_replay_required_for": ["A", "B"],
            "support_digest_replay_chain": [
                "support_surface_descriptor_digest",
                "support_area_digest_input_digest",
            ],
            "support_surface_descriptor_kind": (
                "n07_c3_t7_design_support_surface_descriptor"
            ),
            "support_surface_descriptor_kind_declared_here": True,
            "semantic_consistency_required": True,
        },
        "row_schema_requirements": {
            "required_fields": row_schema["row_required_fields"],
            "runtime_family_allowed_values": row_schema[
                "runtime_family_allowed_values"
            ],
            "implementation_surface_allowed_values": row_schema[
                "implementation_surface_allowed_values"
            ],
            "becoming_enum_values": manifest["becoming_method_fields"][
                "enum_values"
            ],
        },
        "gate_vector_mapping": {
            "source_c1_t6_gate_vector": closeout["gate_vector"],
            "iteration_9_design_gate_vector": _gate_vector_from_iteration_8(
                iteration_8
            ),
            "compatibility_probe_status": "not_run",
            "artifact_replay_status": "not_run",
        },
        "t7_becoming_method_guidance": {
            "boundary_rung_for_design_only_fixture": "eligible_state",
            "boundary_rung_for_positive_9b_probe_candidate": (
                "source_specific_expression"
            ),
            "boundary_rung_for_9c_artifact_closeout_if_compatibility_passes": (
                "recurrence_or_continuation"
            ),
            "identity_acceptance_claim_allowed": False,
            "note": (
                "T7 compatibility can strengthen an artifact-only ID candidate, "
                "but does not by itself authorize identity acceptance, RC "
                "identity collapse, agency, or semantic choice."
            ),
        },
        "non_actions": {
            "compatibility_probe_run": False,
            "compatibility_passed": False,
            "artifact_replay_passed": False,
            "id6_claimed": False,
            "identity_acceptance_event_emitted": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
        },
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
    }


def _fixture_checks(
    *,
    fixture: Mapping[str, Any],
    manifest: Mapping[str, Any],
    iteration_8: Mapping[str, Any],
) -> dict[str, bool]:
    controls = fixture["control_requirements"]
    metric_names = set(fixture["compatibility_metric_contract"]["metric_names"])
    required_metric_names = {
        "a_support_retention_near_b",
        "b_support_retention_near_a",
        "destructive_interference_score",
        "ambiguous_overlap_score",
        "wrong_basin_leakage_score",
        "hidden_support_rejection_rule",
    }
    support_rows = [
        fixture["basins"]["A"]["support_area_row"],
        fixture["basins"]["B"]["support_area_row"],
    ]
    a_nodes = set(fixture["basins"]["A"]["support_area_row"]["support_node_ids"])
    b_nodes = set(fixture["basins"]["B"]["support_area_row"]["support_node_ids"])
    u_nodes = set(fixture["shared_neighborhood_U"]["node_ids"])
    a_edges = set(fixture["basins"]["A"]["support_area_row"]["support_edge_ids"])
    b_edges = set(fixture["basins"]["B"]["support_area_row"]["support_edge_ids"])
    u_edges = set(fixture["shared_neighborhood_U"]["edge_ids"])
    blockers = [row["primary_blocker"] for row in controls]
    manifest_blockers = {
        row["control_id"]: row["primary_blocker"] for row in manifest["controls"]
    }
    manifest_c3 = next(
        row
        for row in manifest["composite_topologies"]
        if row["composite_topology_id"]
        == "n07_C3_competing_basin_compatibility_candidate"
    )
    return {
        "schema_matches": fixture["schema"] == "n07_c3_t7_compatibility_fixture_v1",
        "iteration_8_source_passed": iteration_8["status"] == "passed"
        and iteration_8["acceptance"]["derived_id_ceiling"] == "ID5"
        and iteration_8["acceptance"]["id6_claimed"] is False
        and iteration_8["acceptance"]["next_iteration"]
        == "9_c3_t7_competing_basin_compatibility_fixture_design",
        "t7_family_declared": fixture["topology_family"]["topology_family_id"]
        == "n07_T7_compatibility",
        "t7_manifest_extension_policy_declared": fixture["manifest_extension_policy"][
            "manifest_remains_frozen"
        ]
        is True
        and fixture["manifest_extension_policy"]["extension_declared_in_fixture"]
        is True
        and fixture["topology_family"]["manifest_extension_status"]
        == "post_iteration_8_fixture_extension"
        and "n07_T7_compatibility"
        not in {row["topology_family_id"] for row in manifest["topology_families"]},
        "c3_composite_declared": fixture["composite_topology"]["composite_topology_id"]
        == "n07_C3_competing_basin_compatibility_candidate",
        "c3_primitive_extension_policy_declared": fixture["composite_topology"][
            "manifest_primitive_blocks_combined"
        ]
        == manifest_c3["primitive_blocks_combined"]
        and fixture["composite_topology"][
            "primitive_extension_requires_fixture_validation"
        ]
        is True
        and "n07_T7_compatibility"
        in fixture["composite_topology"]["primitive_blocks_combined"],
        "a_b_support_areas_declared": set(fixture["basins"].keys()) == {"A", "B"}
        and all(row["support_area_id"] for row in support_rows),
        "direct_iteration_7b_provenance_verified": fixture[
            "source_iteration_7b_direct_artifact"
        ]["matches_iteration_8_embedded_7b"]
        is True,
        "basin_a_reexpression_scope_recorded": fixture["basins"]["A"][
            "source_status"
        ]
        == "source_backed_c1_t6_nodes_structurally_reexpressed_for_c3"
        and fixture["basins"]["A"]["source_backing_scope"]["support_edge_ids"]
        == "c3_design_extension"
        and fixture["basins"]["A"]["source_backing_scope"]["support_node_ids"]
        == "source_backed_from_iteration_7b_later_cycle_state_row",
        "basin_b_source_backing_required_for_9b": fixture["basins"]["B"][
            "source_backing_required_in_iteration_9b"
        ]
        is True
        and fixture["source_control_replay_requirements"][
            "b_basin_source_backing_required_in_iteration_9b"
        ]
        is True,
        "shared_u_declared": fixture["shared_neighborhood_U"]["neighborhood_id"]
        == "n07_U_shared_A_B_competing_basin_v1"
        and set(fixture["shared_neighborhood_U"]["connects_support_area_ids"])
        == {"n07_support_area_A_v1", "n07_support_area_B_v1"},
        "competition_semantics_declared": "shared_neighborhood_U"
        in fixture["competition_semantics"]["competition_axes"]
        and "agency" in fixture["competition_semantics"]["not_meant_as"]
        and "semantic_choice" in fixture["competition_semantics"]["not_meant_as"]
        and "Does Basin A remain distinct"
        in fixture["competition_semantics"]["iteration_9b_question"],
        "support_digest_inputs_recompute": all(
            row["support_area_digest"] == _digest(row["support_area_digest_input"])
            for row in support_rows
        ),
        "support_digest_chain_declared": fixture["artifact_replay_requirements"][
            "support_digest_replay_chain"
        ]
        == ["support_surface_descriptor_digest", "support_area_digest_input_digest"]
        and fixture["artifact_replay_requirements"][
            "support_surface_descriptor_kind_declared_here"
        ]
        is True,
        "a_b_u_node_edge_ids_disjoint": not (a_nodes & b_nodes)
        and not (a_nodes & u_nodes)
        and not (b_nodes & u_nodes)
        and not (a_edges & b_edges)
        and not (a_edges & u_edges)
        and not (b_edges & u_edges),
        "support_visuals_non_authoritative": fixture["visual_is_evidence_source"]
        is False
        and all(row["visual_is_evidence_source"] is False for row in support_rows),
        "metric_contract_frozen": fixture["compatibility_metric_contract"][
            "frozen_before_probe"
        ]
        is True
        and fixture["compatibility_metric_contract"]["thresholds_are_frozen"] is True,
        "all_required_metrics_declared": required_metric_names <= metric_names,
        "hidden_support_metric_semantics_declared": any(
            metric["metric_name"] == "hidden_support_rejection_rule"
            and metric.get("metric_formula") == "hidden_support_field_count == 0"
            and metric.get("metric_semantics")
            for metric in fixture["compatibility_metric_contract"]["metrics"]
        ),
        "hidden_metric_inputs_blocked": fixture["compatibility_metric_contract"][
            "hidden_report_side_metric_allowed"
        ]
        is False,
        "control_requirements_complete": set(COMPATIBILITY_CONTROL_CEILINGS)
        == {row["control_id"] for row in controls},
        "control_blockers_match_manifest": all(
            row["primary_blocker"] == manifest_blockers[row["control_id"]]
            for row in controls
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "control_ceilings_gate_specific": all(
            row["gate_specific_derived_id_ceiling"]
            == COMPATIBILITY_CONTROL_CEILINGS[row["control_id"]]
            for row in controls
        ),
        "source_control_replay_required": fixture[
            "source_control_replay_requirements"
        ]["synthetic_closeout_controls_allowed"]
        is False
        and fixture["source_control_replay_requirements"][
            "gate_specific_ceilings_required"
        ]
        is True,
        "artifact_replay_requirements_declared": fixture[
            "artifact_replay_requirements"
        ]["artifact_only"]
        is True
        and fixture["artifact_replay_requirements"]["private_runtime_state_allowed"]
        is False
        and set(fixture["artifact_replay_requirements"][
            "support_area_digest_replay_required_for"
        ])
        == {"A", "B"},
        "frozen_id_row_fields_declared": set(
            iteration_8["source_outputs"]["iteration_1"]["id_ladder_schema"][
                "row_required_fields"
            ]
        )
        == set(fixture["row_schema_requirements"]["required_fields"]),
        "gate_vector_no_compatibility_promotion": fixture["gate_vector_mapping"][
            "iteration_9_design_gate_vector"
        ]["compatibility"]
        == "not_measured"
        and fixture["gate_vector_mapping"]["iteration_9_design_gate_vector"][
            "artifact_replay"
        ]
        == "not_measured",
        "non_actions_preserved": all(
            value is False for value in fixture["non_actions"].values()
        ),
        "t7_becoming_guidance_declared": fixture["t7_becoming_method_guidance"][
            "boundary_rung_for_design_only_fixture"
        ]
        in manifest["becoming_method_fields"]["enum_values"]["boundary_rung"]
        and fixture["t7_becoming_method_guidance"][
            "boundary_rung_for_9c_artifact_closeout_if_compatibility_passes"
        ]
        in manifest["becoming_method_fields"]["enum_values"]["boundary_rung"]
        and fixture["t7_becoming_method_guidance"][
            "identity_acceptance_claim_allowed"
        ]
        is False,
        "claim_flags_all_false": all(value is False for value in fixture["claim_flags"].values()),
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "fixture_digest": _digest(result["fixture"]),
        "fixture_checks_digest": _digest(result["fixture_checks"]),
        "checks_digest": _digest(result["checks"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "acceptance_digest": _digest(result["acceptance"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    fixture = result["fixture"]
    fixture_checks = result["fixture_checks"]
    acceptance = result["acceptance"]
    return {
        "status_passed": result["status"] == "passed",
        "fixture_checks_passed": all(fixture_checks.values()),
        "fixture_file_written": FIXTURE_PATH.exists(),
        "fixture_file_reloads": _load_json(FIXTURE_PATH)["schema"]
        == "n07_c3_t7_compatibility_fixture_v1",
        "fixture_file_digest_matches": _digest(_load_json(FIXTURE_PATH))
        == _digest(fixture),
        "design_only": fixture["purpose"] == "design_only_no_probe_no_id_promotion",
        "compatibility_not_run": acceptance["compatibility_probe_run"] is False
        and acceptance["compatibility_passed"] is False,
        "artifact_replay_not_run": acceptance["artifact_replay_passed"] is False,
        "id6_not_claimed": acceptance["id6_claimed"] is False
        and acceptance["derived_id_ceiling"] == "ID5",
        "claim_flags_false": all(value is False for value in result["claim_flags"].values()),
        "next_iteration_is_9b": acceptance["next_iteration"]
        == "9B_c3_compatibility_interference_probe",
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _write_report(result: Mapping[str, Any]) -> None:
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    fixture_checks = "\n".join(
        f"| `{key}` | `{value}` |"
        for key, value in sorted(result["fixture_checks"].items())
    )
    controls = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            row["control_id"],
            row["primary_blocker"],
            row["control_gate"],
            row["gate_specific_derived_id_ceiling"],
        )
        for row in result["fixture"]["control_requirements"]
    )
    metrics = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            row["metric_name"],
            row["metric_kind"],
            row["comparison"],
            row["threshold"],
        )
        for row in result["fixture"]["compatibility_metric_contract"]["metrics"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 9: C3/T7 Compatibility Fixture Design

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 9 is a design/freeze iteration. It declares the C3/T7
competing-basin compatibility fixture, frozen compatibility metrics,
support-area digest replay inputs, source-control replay requirements, and
artifact-only replay requirements. It does not run the compatibility probe and
does not claim ID6.

## Compatibility Metrics

| Metric | Kind | Comparison | Threshold |
|---|---|---|---:|
{metrics}

## Control Requirements

| Control | Primary blocker | Gate | Blocked ceiling |
|---|---|---|---|
{controls}

## Fixture Checks

| Check | Passed |
|---|---:|
{fixture_checks}

## Checks

| Check | Passed |
|---|---:|
{checks}

## Fixture

```json
{json.dumps(result['fixture'], indent=2, sort_keys=True)}
```

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 9 passes because the C3/T7 compatibility fixture is frozen before
probes run. A and B support areas, shared neighborhood U, metric thresholds,
control replay requirements, artifact replay requirements, and frozen ID row
fields are declared. Compatibility remains not measured, artifact replay is not
run, ID6 is not claimed, and all identity acceptance, RC identity collapse,
agency, semantic choice, biological identity, personhood, and unrestricted
identity claims remain blocked.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    iteration_8 = _load_json(ITERATION_8_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    fixture = _fixture(
        manifest=manifest,
        iteration_8=iteration_8,
        claim_flags=claim_flags,
    )
    CONFIGS.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fixture_checks = _fixture_checks(
        fixture=fixture,
        manifest=manifest,
        iteration_8=iteration_8,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_9_c3_t7_compatibility_fixture_design_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 9,
        "status": "passed",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_artifacts": _source_artifacts(),
        "source_reports": _source_reports(),
        "source_manifest": manifest,
        "source_iteration_8": iteration_8,
        "fixture_path": _rel(FIXTURE_PATH),
        "fixture": fixture,
        "fixture_checks": fixture_checks,
        "claim_flags": claim_flags,
        "acceptance": {
            "fixture_declared": True,
            "compatibility_probe_run": False,
            "compatibility_passed": False,
            "artifact_replay_passed": False,
            "derived_id_ceiling": "ID5",
            "id6_claimed": False,
            "id6_blocker": "compatibility_probe_and_artifact_replay_not_run",
            "identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "next_iteration": "9B_c3_compatibility_interference_probe",
        },
        "git": {
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["artifact_digests"] = _artifact_digests(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    result = build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(FIXTURE_PATH)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()

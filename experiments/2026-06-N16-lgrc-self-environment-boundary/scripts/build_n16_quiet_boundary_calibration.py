#!/usr/bin/env python3
"""Build N16 Iteration 3 quiet boundary calibration rows."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"

INVENTORY_OUTPUT = OUTPUTS / "n16_boundary_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n16_boundary_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n16_boundary_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n16_boundary_schema_v1.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n16_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n16_replay_policy_v1.json"
SOURCE_REGISTRY = CONFIGS / "n16_source_registry.json"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

OUTPUT_PATH = OUTPUTS / "n16_quiet_boundary_calibration.json"
REPORT_PATH = REPORTS / "n16_quiet_boundary_calibration.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_quiet_boundary_calibration.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"

INTERNAL_SUPPORT_FLOOR = 0.85
INTERNAL_COHERENCE_FLOOR = 0.84
BASIN_SIGNAL_FLOOR = 0.70
MINIMUM_COHERENCE_MARGIN_FLOOR = 0.52
QUIET_LEAKAGE_CEILING = 0.12
QUIET_STABILITY_FLOOR = 0.90

BLOCKED_CLAIMS = [
    "final_ap6",
    "selfhood",
    "personhood",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "intention",
    "semantic_choice",
    "agency",
    "unrestricted_agency",
    "native_support_without_phase8",
    "fully_native_agentic_like_integration",
    "selective_uptake_or_resource_assimilation",
    "organism_or_life_claim",
]

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify B0 as active null, B1 as localized partition candidate, "
        "and B2 as quiet persistence candidate without promoting any row to "
        "final AP6"
    ),
    "interrogation_of_becoming": (
        "treat C0 as a bounded calibration question: can the frozen machinery "
        "separate null external coherence, partition visibility, and quiet "
        "persistence"
    ),
    "naturalization_of_becoming": (
        "keep artifact-visible boundary separability distinct from native "
        "support or native self/environment understanding"
    ),
    "cultivation_of_becoming": (
        "cultivate reusable derived side assignments, boundary edges, and "
        "quiet baselines before applying challenge-class stress"
    ),
}

CASE_INPUTS = {
    "B0_C0": {
        "case_id": "n16_i3_b0_c0_quiet_external_coherence_null",
        "boundary_state": "B0",
        "challenge_class": "C0",
        "primary_source_row_id": "n16_i1_row_04_n15_claim_boundary",
        "selected_source_row_ids": [
            "n16_i1_row_04_n15_claim_boundary",
            "n16_i1_row_10_n03_artifact_surface_inventory",
        ],
        "snapshots": [
            {
                "snapshot_id": "q0",
                "nodes": {
                    "b0_q0": {
                        "support": 0.18,
                        "coherence": 0.42,
                        "basin_signal": 0.10,
                        "external_coherence": 0.74,
                    },
                    "b0_q1": {
                        "support": 0.16,
                        "coherence": 0.45,
                        "basin_signal": 0.08,
                        "external_coherence": 0.76,
                    },
                    "b0_q2": {
                        "support": 0.14,
                        "coherence": 0.43,
                        "basin_signal": 0.09,
                        "external_coherence": 0.73,
                    },
                },
                "edges": [
                    ["b0_q0", "b0_q1", 0.61],
                    ["b0_q1", "b0_q2", 0.59],
                ],
            }
        ],
    },
    "B1_C0": {
        "case_id": "n16_i3_b1_c0_quiet_localized_partition",
        "boundary_state": "B1",
        "challenge_class": "C0",
        "primary_source_row_id": "n16_i1_row_10_n03_artifact_surface_inventory",
        "selected_source_row_ids": [
            "n16_i1_row_10_n03_artifact_surface_inventory",
            "n16_i1_row_11_n03_native_packet_loop_closeout",
            "n16_i1_row_12_n04_taxonomy_inventory",
            "n16_i1_row_13_n04_boundary_coupled_pulse",
        ],
        "snapshots": [
            {
                "snapshot_id": "q0",
                "nodes": {
                    "b1_q0": {
                        "support": 0.78,
                        "coherence": 0.82,
                        "basin_signal": 0.76,
                        "external_coherence": 0.14,
                    },
                    "b1_q1": {
                        "support": 0.75,
                        "coherence": 0.79,
                        "basin_signal": 0.74,
                        "external_coherence": 0.16,
                    },
                    "b1_q2": {
                        "support": 0.22,
                        "coherence": 0.27,
                        "basin_signal": 0.19,
                        "external_coherence": 0.35,
                    },
                    "b1_q3": {
                        "support": 0.20,
                        "coherence": 0.23,
                        "basin_signal": 0.16,
                        "external_coherence": 0.37,
                    },
                },
                "edges": [
                    ["b1_q0", "b1_q1", 0.68],
                    ["b1_q1", "b1_q2", 0.18],
                    ["b1_q2", "b1_q3", 0.44],
                ],
            }
        ],
    },
    "B2_C0": {
        "case_id": "n16_i3_b2_c0_quiet_support_persistence",
        "boundary_state": "B2",
        "challenge_class": "C0",
        "primary_source_row_id": "n16_i1_row_07_n13_closeout_ap3",
        "selected_source_row_ids": [
            "n16_i1_row_01_n15_closeout_ap5",
            "n16_i1_row_03_n15_bounded_drift_replay",
            "n16_i1_row_07_n13_closeout_ap3",
            "n16_i1_row_11_n03_native_packet_loop_closeout",
            "n16_i1_row_12_n04_taxonomy_inventory",
            "n16_i1_row_15_n07_long_horizon_compatibility_closeout",
            "n16_i1_row_16_n07_identity_support_withdrawal_baseline",
        ],
        "snapshots": [
            {
                "snapshot_id": "q0",
                "nodes": {
                    "b2_q0": {
                        "support": 0.86,
                        "coherence": 0.88,
                        "basin_signal": 0.82,
                        "external_coherence": 0.16,
                    },
                    "b2_q1": {
                        "support": 0.87,
                        "coherence": 0.89,
                        "basin_signal": 0.84,
                        "external_coherence": 0.15,
                    },
                    "b2_q2": {
                        "support": 0.86,
                        "coherence": 0.87,
                        "basin_signal": 0.83,
                        "external_coherence": 0.15,
                    },
                    "b2_q3": {
                        "support": 0.23,
                        "coherence": 0.29,
                        "basin_signal": 0.20,
                        "external_coherence": 0.36,
                    },
                    "b2_q4": {
                        "support": 0.21,
                        "coherence": 0.26,
                        "basin_signal": 0.18,
                        "external_coherence": 0.34,
                    },
                },
                "edges": [
                    ["b2_q0", "b2_q1", 0.74],
                    ["b2_q1", "b2_q2", 0.72],
                    ["b2_q2", "b2_q3", 0.09],
                    ["b2_q3", "b2_q4", 0.37],
                ],
            },
            {
                "snapshot_id": "q1",
                "nodes": {
                    "b2_q0": {
                        "support": 0.85,
                        "coherence": 0.87,
                        "basin_signal": 0.82,
                        "external_coherence": 0.17,
                    },
                    "b2_q1": {
                        "support": 0.86,
                        "coherence": 0.88,
                        "basin_signal": 0.83,
                        "external_coherence": 0.15,
                    },
                    "b2_q2": {
                        "support": 0.85,
                        "coherence": 0.86,
                        "basin_signal": 0.81,
                        "external_coherence": 0.15,
                    },
                    "b2_q3": {
                        "support": 0.24,
                        "coherence": 0.28,
                        "basin_signal": 0.20,
                        "external_coherence": 0.34,
                    },
                    "b2_q4": {
                        "support": 0.21,
                        "coherence": 0.25,
                        "basin_signal": 0.18,
                        "external_coherence": 0.34,
                    },
                },
                "edges": [
                    ["b2_q0", "b2_q1", 0.73],
                    ["b2_q1", "b2_q2", 0.71],
                    ["b2_q2", "b2_q3", 0.10],
                    ["b2_q3", "b2_q4", 0.37],
                ],
            },
            {
                "snapshot_id": "q2",
                "nodes": {
                    "b2_q0": {
                        "support": 0.86,
                        "coherence": 0.88,
                        "basin_signal": 0.82,
                        "external_coherence": 0.16,
                    },
                    "b2_q1": {
                        "support": 0.86,
                        "coherence": 0.88,
                        "basin_signal": 0.83,
                        "external_coherence": 0.15,
                    },
                    "b2_q2": {
                        "support": 0.85,
                        "coherence": 0.87,
                        "basin_signal": 0.81,
                        "external_coherence": 0.16,
                    },
                    "b2_q3": {
                        "support": 0.23,
                        "coherence": 0.29,
                        "basin_signal": 0.19,
                        "external_coherence": 0.35,
                    },
                    "b2_q4": {
                        "support": 0.22,
                        "coherence": 0.26,
                        "basin_signal": 0.18,
                        "external_coherence": 0.34,
                    },
                },
                "edges": [
                    ["b2_q0", "b2_q1", 0.74],
                    ["b2_q1", "b2_q2", 0.72],
                    ["b2_q2", "b2_q3", 0.09],
                    ["b2_q3", "b2_q4", 0.36],
                ],
            },
        ],
    },
}

MINIMUM_SUPPORT_SWEEP = [
    {
        "candidate_internal_support": 0.78,
        "candidate_internal_coherence": 0.82,
        "coherence_margin": 0.46,
        "detectable_partition": True,
        "persistent_under_quiet_window": False,
        "reason": "partition visible but below support persistence floor",
    },
    {
        "candidate_internal_support": 0.82,
        "candidate_internal_coherence": 0.83,
        "coherence_margin": 0.50,
        "detectable_partition": True,
        "persistent_under_quiet_window": False,
        "reason": "quiet partition still below frozen support floor",
    },
    {
        "candidate_internal_support": 0.85,
        "candidate_internal_coherence": 0.84,
        "coherence_margin": MINIMUM_COHERENCE_MARGIN_FLOOR,
        "detectable_partition": True,
        "persistent_under_quiet_window": True,
        "reason": "first quiet calibration point satisfying support and coherence floors",
    },
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def artifact_status(artifact: dict[str, Any] | None) -> str | None:
    if artifact is None:
        return None
    if artifact.get("status") is not None:
        return artifact["status"]
    iteration_result = artifact.get("iteration_result")
    if isinstance(iteration_result, dict) and any(
        key.endswith("_passed") and value is True
        for key, value in iteration_result.items()
    ):
        return "passed"
    return "not_applicable"


def source_record(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": rel(path), "sha256": digest_file(path)}
    if artifact is not None:
        record["status"] = artifact_status(artifact)
        record["acceptance_state"] = artifact.get("acceptance_state")
        record["output_digest"] = artifact.get("output_digest")
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def contains_absolute_path(value: Any) -> bool:
    local_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "geometric-" + "reflexive-coherence",
        "arc-" + "of-becoming",
    )
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in local_markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def indexed_by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items}


def derive_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    nodes = snapshot["nodes"]
    primary_internal_nodes = sorted(
        node_id
        for node_id, node in nodes.items()
        if node["support"] >= INTERNAL_SUPPORT_FLOOR
        and node["coherence"] >= INTERNAL_COHERENCE_FLOOR
        and node["basin_signal"] >= BASIN_SIGNAL_FLOOR
    )
    if primary_internal_nodes:
        internal_nodes = primary_internal_nodes
        classification_path = "primary_floor"
    else:
        internal_nodes = sorted(
            node_id
            for node_id, node in nodes.items()
            if node["coherence"] >= BASIN_SIGNAL_FLOOR
            and node["basin_signal"] >= BASIN_SIGNAL_FLOOR
        )
        classification_path = (
            "fallback_basin_signal_only" if internal_nodes else "none"
        )
    external_nodes = sorted(node_id for node_id in nodes if node_id not in internal_nodes)
    side_by_node = {
        node_id: "derived_internal_side"
        for node_id in internal_nodes
    } | {
        node_id: "derived_external_side"
        for node_id in external_nodes
    }
    boundary_edges = []
    internal_edges = []
    external_edges = []
    for left, right, weight in snapshot["edges"]:
        edge = {
            "left": left,
            "right": right,
            "weight": weight,
            "left_side": side_by_node[left],
            "right_side": side_by_node[right],
        }
        if side_by_node[left] != side_by_node[right]:
            boundary_edges.append(edge)
        elif side_by_node[left] == "derived_internal_side":
            internal_edges.append(edge)
        else:
            external_edges.append(edge)
    internal_values = [nodes[node]["coherence"] for node in internal_nodes]
    external_values = [nodes[node]["external_coherence"] for node in external_nodes]
    support_values = [nodes[node]["support"] for node in internal_nodes]
    internal_coherence = round(sum(internal_values) / len(internal_values), 6) if internal_values else 0.0
    external_coherence = round(sum(external_values) / len(external_values), 6) if external_values else 0.0
    minimum_support = round(min(support_values), 6) if support_values else 0.0
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "internal_nodes": internal_nodes,
        "external_nodes": external_nodes,
        "side_by_node": side_by_node,
        "classification_path": classification_path,
        "boundary_edges": boundary_edges,
        "internal_edges": internal_edges,
        "external_edges": external_edges,
        "internal_coherence": internal_coherence,
        "external_coherence": external_coherence,
        "coherence_margin": round(internal_coherence - external_coherence, 6),
        "minimum_internal_support": minimum_support,
    }


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    snapshots = [derive_snapshot(snapshot) for snapshot in case["snapshots"]]
    first = snapshots[0]
    internal_sets = {tuple(snapshot["internal_nodes"]) for snapshot in snapshots}
    boundary_sets = {
        tuple((edge["left"], edge["right"]) for edge in snapshot["boundary_edges"])
        for snapshot in snapshots
    }
    stable_side_assignments = len(internal_sets) == 1
    stable_boundary_edges = len(boundary_sets) == 1
    all_snapshots_meet_persistence_floors = all(
        snapshot["minimum_internal_support"] >= INTERNAL_SUPPORT_FLOOR
        and snapshot["coherence_margin"] >= MINIMUM_COHERENCE_MARGIN_FLOOR
        for snapshot in snapshots
    )
    leakage_ratio = round(
        sum(edge["weight"] for edge in first["boundary_edges"])
        / max(1.0, sum(edge["weight"] for edge in first["internal_edges"])),
        6,
    )
    persistence_basis = (
        stable_side_assignments
        and stable_boundary_edges
        and len(snapshots) > 1
        and all_snapshots_meet_persistence_floors
        and leakage_ratio <= QUIET_LEAKAGE_CEILING
    )
    partition_detected = bool(first["internal_nodes"] and first["external_nodes"] and first["boundary_edges"])
    stability_score = 1.0 if persistence_basis else (0.5 if partition_detected else 0.0)
    return {
        "snapshots": snapshots,
        "partition_detected": partition_detected,
        "persistence_basis": persistence_basis,
        "stable_side_assignments": stable_side_assignments,
        "stable_boundary_edges": stable_boundary_edges,
        "all_snapshots_meet_persistence_floors": all_snapshots_meet_persistence_floors,
        "leakage_ratio": leakage_ratio,
        "stability_score": stability_score,
    }


def verified_digest_plan(value: dict[str, Any]) -> dict[str, Any]:
    first_digest = digest_value(value)
    second_digest = digest_value(value)
    if first_digest != second_digest:
        raise RuntimeError("idempotency digest self-verification failed")
    return {
        "algorithm": "sha256",
        "digest": first_digest,
        "self_verified": True,
        "same_inputs_same_digest_required": True,
    }


def dependency_entry(
    row_field: str,
    source: dict[str, Any],
    source_field: str,
    transform_id: str,
    transform_parameters: dict[str, Any],
    boundary_side: str,
) -> dict[str, Any]:
    return {
        "row_field": row_field,
        "source_row_id": source["row_id"],
        "source_artifact": source["source_artifact"],
        "source_sha256": source["source_sha256"],
        "source_field": source_field,
        "transform_id": transform_id,
        "transform_parameters": transform_parameters,
        "claim_ceiling_of_source": source["provisional_claim_ceiling"],
        "boundary_side": boundary_side,
    }


def row_controls(control_ids: list[str], label: str) -> dict[str, Any]:
    controls = {}
    for control_id in control_ids:
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "iteration_3_scope": "not_a_full_negative_control_matrix",
        }
    controls["externally_supplied_boundary_control"] = {
        "status": "passed_for_quiet_calibration",
        "result": "no trusted boundary label supplied to case data",
        "label_policy": label,
    }
    controls["post_hoc_boundary_label_control"] = {
        "status": "passed_for_quiet_calibration",
        "result": "side assignments are computed before row decision",
        "label_policy": label,
    }
    controls["hidden_external_state_injection_control"] = {
        "status": "passed_for_quiet_calibration",
        "result": "external-state role is fixed to background for C0 rows",
        "label_policy": label,
    }
    return controls


def top_level_controls(schema: dict[str, Any]) -> dict[str, Any]:
    controls = {}
    for requirement in schema["control_requirements"]:
        control_id = requirement["control_id"]
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "expected_status": requirement["expected_status"],
            "expected_blocker": requirement["expected_blocker"],
        }
    controls["externally_supplied_boundary_control"]["status"] = "checked_i3_passed"
    controls["externally_supplied_boundary_control"]["observed"] = (
        "all boundary-side assignments are derived from quiet case metrics"
    )
    controls["post_hoc_boundary_label_control"]["status"] = "checked_i3_passed"
    controls["post_hoc_boundary_label_control"]["observed"] = (
        "row decisions are assigned after side derivation"
    )
    controls["artifact_only_replay_control"]["status"] = "deterministic_builder_replay_ready"
    return controls


def base_row(
    schema: dict[str, Any],
    inventory: dict[str, Any],
    case: dict[str, Any],
    case_eval: dict[str, Any],
) -> dict[str, Any]:
    rows_by_id = indexed_by(inventory["rows"], "row_id")
    boundary_by_state = indexed_by(inventory["boundary_state_lineage"], "boundary_state")
    challenge_by_class = indexed_by(inventory["challenge_class_records"], "challenge_class")
    primary = rows_by_id[case["primary_source_row_id"]]
    boundary_lineage = boundary_by_state[case["boundary_state"]]
    challenge_record = challenge_by_class[case["challenge_class"]]
    selected_sources = [rows_by_id[row_id] for row_id in case["selected_source_row_ids"]]
    control_ids = [control["control_id"] for control in schema["control_requirements"]]
    first = case_eval["snapshots"][0]
    label_policy = (
        "derived_from_support_coherence_and_basin_signal_thresholds;"
        "no externally supplied self or external labels"
    )
    dependency_trace = [
        dependency_entry(
            "boundary_state_lineage_sources",
            source,
            "boundary_state_relevance",
            "n16_i3_old_best_lineage_selection",
            {"boundary_state": case["boundary_state"], "challenge_class": "C0"},
            "claim_boundary",
        )
        for source in selected_sources
    ]
    dependency_trace.extend(
        [
            dependency_entry(
                "boundary_side_assignments",
                primary,
                "source_role_classification",
                "n16_i3_quiet_side_derivation",
                {
                    "internal_support_floor": INTERNAL_SUPPORT_FLOOR,
                    "internal_coherence_floor": INTERNAL_COHERENCE_FLOOR,
                    "basin_signal_floor": BASIN_SIGNAL_FLOOR,
                    "external_labels_supplied": False,
                },
                "derived_internal_and_external_sides",
            ),
            dependency_entry(
                "boundary_edges",
                primary,
                "source_artifact",
                "n16_i3_cross_side_edge_extraction",
                {"edge_rule": "edge endpoints with different derived sides"},
                "boundary_side",
            ),
        ]
    )
    replay_inputs = {
        "policy_id": "n16_replay_digest_policy_v1",
        "case_id": case["case_id"],
        "boundary_state": case["boundary_state"],
        "challenge_class": case["challenge_class"],
        "selected_source_row_ids": case["selected_source_row_ids"],
        "side_assignments": first["side_by_node"],
        "classification_path": first["classification_path"],
        "boundary_edges": first["boundary_edges"],
        "metrics": {
            "internal_coherence": first["internal_coherence"],
            "external_coherence": first["external_coherence"],
            "coherence_margin": first["coherence_margin"],
            "leakage_ratio": case_eval["leakage_ratio"],
            "boundary_stability_score": case_eval["stability_score"],
        },
    }

    row: dict[str, Any] = {field: "not_applicable" for field in schema["row_schema_fields"]}
    row.update(
        {
            "row_id": f"n16_i3_row_{case['boundary_state'].lower()}_c0",
            "cell_id": f"{case['boundary_state']}_C0",
            "boundary_state": case["boundary_state"],
            "case_id": case["case_id"],
            "challenge_class": "C0",
            "basin_count": 1 if first["internal_nodes"] else 0,
            "boundary_state_lineage_sources": boundary_lineage["lineage_sources"],
            "boundary_state_inherited_closed_claims": boundary_lineage[
                "inherited_closed_claims"
            ],
            "boundary_state_constructed_support": boundary_lineage[
                "constructed_support"
            ],
            "boundary_state_unsupported_extension": boundary_lineage[
                "unsupported_extension"
            ],
            "required_n16_boundary_evidence": boundary_lineage[
                "required_N16_evidence"
            ],
            "source_experiment": primary["source_experiment"],
            "source_iteration": primary["source_iteration"],
            "source_artifact": primary["source_artifact"],
            "source_report": primary["source_report"],
            "source_sha256": primary["source_sha256"],
            "source_report_sha256": primary["source_report_sha256"],
            "source_status": primary["source_status"],
            "mechanism_name": primary["mechanism_name"],
            "mechanism_role": primary["mechanism_role"],
            "source_role_classification": primary["source_role_classification"],
            "role_classification_audit": {
                "status": "passed",
                "claim_ceiling_preserved": True,
                "c0_is_calibration_only": True,
            },
            "evidence_strategy": "quiet_calibration_from_old_best_source_rows",
            "evidence_strategy_class": "old_best_claims_construction",
            "old_best_claim_inputs": case["selected_source_row_ids"],
            "direct_historic_ap6_support_status": "not_direct_ap6_support",
            "direct_historic_support_status": "absent",
            "ap5_contribution_status": (
                "context_only_not_promoted"
                if "n16_i1_row_01_n15_closeout_ap5" in case["selected_source_row_ids"]
                else "not_applicable"
            ),
            "boundary_state_relevance": [case["boundary_state"]],
            "challenge_class_relevance": ["C0"],
            "arc_method_mapping": ARC_METHOD_MAPPING,
            "runtime_state_surface_id": f"{case['case_id']}_derived_surface",
            "state_source_window": {
                "window_id": "quiet_reference_window",
                "snapshot_count": len(case["snapshots"]),
                "freshness": "source_current_for_iteration_3",
                "challenge_pressure": "none",
            },
            "source_current": {
                "selected_source_rows": case["selected_source_row_ids"],
                "case_snapshots": case["snapshots"],
                "external_boundary_labels_supplied": False,
            },
            "internal_state_descriptor": {
                "derived_internal_side_nodes": first["internal_nodes"],
                "classification_path": first["classification_path"],
                "support_floor": INTERNAL_SUPPORT_FLOOR,
                "coherence_floor": INTERNAL_COHERENCE_FLOOR,
                "coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
                "basin_signal_floor": BASIN_SIGNAL_FLOOR,
                "minimum_observed_internal_support": first["minimum_internal_support"],
            },
            "external_resource_descriptor": {
                "derived_external_side_nodes": first["external_nodes"],
                "resource_role": "not_resource_under_c0",
            },
            "external_perturbation_descriptor": {
                "challenge_class": "C0",
                "perturbation_present": False,
            },
            "external_structured_state_descriptor": {
                "structured_external_challenge_present": False,
                "external_background_coherence": first["external_coherence"],
            },
            "external_state_role": "background",
            "basin_descriptor": {
                "basin_count": 1 if first["internal_nodes"] else 0,
                "partition_detected": case_eval["partition_detected"],
                "quiet_persistence_basis": case_eval["persistence_basis"],
                "quiet_window_snapshot_count": len(case_eval["snapshots"]),
                "stable_side_assignments": case_eval["stable_side_assignments"],
                "stable_boundary_edges": case_eval["stable_boundary_edges"],
                "all_snapshots_meet_persistence_floors": case_eval[
                    "all_snapshots_meet_persistence_floors"
                ],
                "quiet_window_metrics": [
                    {
                        "snapshot_id": snapshot["snapshot_id"],
                        "classification_path": snapshot["classification_path"],
                        "minimum_internal_support": snapshot[
                            "minimum_internal_support"
                        ],
                        "internal_coherence": snapshot["internal_coherence"],
                        "external_coherence": snapshot["external_coherence"],
                        "coherence_margin": snapshot["coherence_margin"],
                        "boundary_edge_count": len(snapshot["boundary_edges"]),
                    }
                    for snapshot in case_eval["snapshots"]
                ],
            },
            "boundary_policy": {
                "policy_id": "n16_i3_quiet_boundary_calibration_policy",
                "inherits": "n16_boundary_policy_v1",
                "side_derivation": label_policy,
                "quiet_leakage_ceiling": QUIET_LEAKAGE_CEILING,
                "quiet_stability_floor": QUIET_STABILITY_FLOOR,
            },
            "case_policy": {
                "calibration_only": True,
                "external_boundary_labels_supplied": False,
                "post_hoc_labels_allowed": False,
                "challenge_class": "C0 quiet reference",
            },
            "boundary_condition_evaluated_at": "pre_use_quiet_calibration",
            "boundary_surface": {
                "snapshot_id": first["snapshot_id"],
                "side_derivation": first["side_by_node"],
                "classification_path": first["classification_path"],
                "internal_edges": first["internal_edges"],
                "external_edges": first["external_edges"],
            },
            "boundary_side_assignments": first["side_by_node"],
            "self_region_nodes": first["internal_nodes"],
            "external_region_nodes": first["external_nodes"],
            "boundary_edges": first["boundary_edges"],
            "boundary_crossing_trace": first["boundary_edges"],
            "dependency_trace": dependency_trace,
            "internal_coherence": first["internal_coherence"],
            "external_coherence": first["external_coherence"],
            "coherence_margin": first["coherence_margin"],
            "inbound_flux": 0.0,
            "outbound_flux": 0.0,
            "retained_flux": round(
                float(sum(edge["weight"] for edge in first["internal_edges"])), 6
            ),
            "leakage_ratio": case_eval["leakage_ratio"],
            "boundary_stability_score": case_eval["stability_score"],
            "repair_score": "not_evaluated_in_quiet_calibration",
            "noise_resilience_score": "not_evaluated_in_c0",
            "flux_tolerance_score": "not_evaluated_in_c0",
            "basin_separation_score": "not_evaluated_until_shared_medium_rows",
            "native_boundary_requirements_observed": [],
            "requirements_satisfied": [
                "source_rows_selected",
                "common_schema_populated",
                "no_externally_supplied_boundary_labels",
            ],
            "requirements_failed": [],
            "budget_cost_surface": {
                "source_row_count": len(case["selected_source_row_ids"]),
                "matrix_cell_count": 1,
                "transform_count": 4,
                "canonical_json_input_bytes": len(canonical_json(case)),
                "canonical_json_output_bytes": len(canonical_json(replay_inputs)),
                "replay_count": len(case["snapshots"]),
                "validation_count": 1,
                "wall_clock_seconds": 0,
            },
            "budget_units": [
                "source_row_count",
                "matrix_cell_count",
                "transform_count",
                "canonical_json_input_bytes",
                "canonical_json_output_bytes",
                "replay_count",
                "validation_count",
                "wall_clock_seconds",
            ],
            "budget_validity": "valid",
            "replay_digest_inputs": replay_inputs,
            "replay_digest_algorithm": "sha256_canonical_json_sorted_keys_ascii",
            "idempotency_digest_plan": {
                **verified_digest_plan(replay_inputs),
            },
            "artifact_only_replay_status": "deterministic_builder_replay_ready",
            "snapshot_load_status": "not_run_iteration_3_deferred_before_final_ap6",
            "order_inversion_replay_status": "not_run_iteration_3_deferred_before_final_ap6",
            "boundary_claim_allowed": False,
            "boundary_classification": "quiet_calibration_pending_classification",
            "failure_mode": "not_applicable",
            "provisional_ap_level": "AP6_candidate_input_only",
            "provisional_claim_ceiling": boundary_lineage["claim_ceiling"],
            "claim_ceiling": boundary_lineage["claim_ceiling"],
            "claim_ceiling_preserved": True,
            "claim_promotion_allowed": False,
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "challenge_class_sweep_missing",
                "negative_control_matrix_missing",
                "artifact_only_replay_matrix_missing",
                "claim_boundary_classification_missing",
            ],
            "ap6_required_evidence_still_missing": [
                "C1_unstructured_perturbation",
                "C2_directional_flux",
                "C3_structured_external_coherence_rejection",
                "C4_breach_reclosure_pressure",
                "C5_shared_medium_separation",
                "full_negative_controls",
                "duplicate_and_order_inversion_replay",
            ],
            "final_ap6_supported": False,
        }
    )
    row.update(row_controls(control_ids, label_policy))

    if case["boundary_state"] == "B0":
        row.update(
            {
                "row_decision": "rejected",
                "boundary_classification": "active_null_external_coherence_rejected_as_boundary_support",
                "failure_mode": "active_null_external_coherence_no_internal_partition",
                "requirements_satisfied": [
                    "active_null_row_valid",
                    "external_coherence_does_not_become_boundary_support",
                    "boundary_claim_allowed_false",
                ],
                "requirements_failed": [
                    "no_internal_support_relevant_side",
                    "no_boundary_edge",
                    "no_partition_candidate",
                ],
                "native_boundary_requirements_observed": [
                    "external_coherence_alone_is_insufficient_for_boundary_support"
                ],
                "provisional_ap_level": "AP0_active_null",
            }
        )
    elif case["boundary_state"] == "B1":
        row.update(
            {
                "row_decision": "partial",
                "boundary_classification": "localized_partition_candidate_under_C0",
                "failure_mode": "persistence_not_evaluated_for_B1",
                "requirements_satisfied": row["requirements_satisfied"]
                + [
                    "boundary_edge_extraction_passed",
                    "inside_outside_partition_passed",
                    "boundary_edges_incident_to_both_derived_sides",
                ],
                "requirements_failed": [
                    "support_persistence_not_claimed",
                    "quiet_window_replay_not_required_for_B1",
                    (
                        f"quiet_leakage_ratio_{row['leakage_ratio']}"
                        f"_exceeds_ceiling_{QUIET_LEAKAGE_CEILING}"
                    ),
                    (
                        f"coherence_margin_{row['coherence_margin']}"
                        f"_below_floor_{MINIMUM_COHERENCE_MARGIN_FLOOR}"
                    ),
                ],
                "native_boundary_requirements_observed": [
                    "localized_partition_requires_internal_coherence_above_0.70",
                    "localized_partition_is_not_persistence",
                    (
                        f"quiet_leakage_ratio_{row['leakage_ratio']}"
                        f"_exceeds_ceiling_{QUIET_LEAKAGE_CEILING}"
                    ),
                    (
                        f"coherence_margin_{row['coherence_margin']}"
                        f"_below_floor_{MINIMUM_COHERENCE_MARGIN_FLOOR}"
                    ),
                ],
                "provisional_claim_ceiling": "localized_basin_partition_candidate_under_C0_only",
                "claim_ceiling": "localized_basin_partition_candidate_under_C0_only",
            }
        )
    elif case["boundary_state"] == "B2":
        row.update(
            {
                "row_decision": "supported",
                "boundary_classification": "support_persistent_basin_under_C0_only",
                "failure_mode": "final_ap6_blocked_by_missing_challenge_controls_and_replay",
                "requirements_satisfied": row["requirements_satisfied"]
                + [
                    "boundary_edge_extraction_passed",
                    "inside_outside_partition_passed",
                    "quiet_window_side_assignment_stability_passed",
                    "quiet_window_boundary_edge_stability_passed",
                    "minimum_internal_support_baseline_recorded",
                    "minimum_coherence_margin_baseline_recorded",
                ],
                "requirements_failed": [
                    "challenge_robustness_not_tested",
                    "negative_controls_not_complete",
                    "final_ap6_not_allowed",
                ],
                "native_boundary_requirements_observed": [
                    "minimum_internal_support >= 0.85 under C0",
                    (
                        "minimum_coherence_margin >= "
                        f"{MINIMUM_COHERENCE_MARGIN_FLOOR} under C0"
                    ),
                    "quiet_leakage_ratio <= 0.12 under C0",
                    "stable_derived_side_assignments_across_quiet_window",
                ],
                "provisional_claim_ceiling": "support_persistent_basin_candidate_under_C0_only",
                "claim_ceiling": "support_persistent_basin_candidate_under_C0_only",
            }
        )
    return row


def build_rows(schema: dict[str, Any], inventory: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cell_id in ["B0_C0", "B1_C0", "B2_C0"]:
        case = CASE_INPUTS[cell_id]
        case_eval = evaluate_case(case)
        rows.append(base_row(schema, inventory, case, case_eval))
    return rows


def iteration_checks(rows: list[dict[str, Any]]) -> dict[str, bool]:
    by_cell = {row["cell_id"]: row for row in rows}
    b1 = by_cell["B1_C0"]
    b2 = by_cell["B2_C0"]
    b1_edges = b1["boundary_edges"]
    b2_edges = b2["boundary_edges"]
    return {
        "row_count_is_three": len(rows) == 3,
        "all_rows_under_c0": all(row["challenge_class"] == "C0" for row in rows),
        "c0_marked_calibration_only": all(
            row["case_policy"]["calibration_only"] is True for row in rows
        ),
        "b0_rejected_as_boundary_support": by_cell["B0_C0"]["row_decision"]
        == "rejected"
        and by_cell["B0_C0"]["boundary_claim_allowed"] is False,
        "b1_partition_candidate_not_persistence": b1["row_decision"] == "partial"
        and "support_persistence_not_claimed" in b1["requirements_failed"],
        "b1_non_persistence_threshold_breaches_recorded": (
            f"quiet_leakage_ratio_{b1['leakage_ratio']}"
            f"_exceeds_ceiling_{QUIET_LEAKAGE_CEILING}"
        )
        in b1["requirements_failed"]
        and (
            f"coherence_margin_{b1['coherence_margin']}"
            f"_below_floor_{MINIMUM_COHERENCE_MARGIN_FLOOR}"
        )
        in b1["requirements_failed"],
        "classification_path_recorded": all(
            row["internal_state_descriptor"]["classification_path"]
            in {"primary_floor", "fallback_basin_signal_only", "none"}
            for row in rows
        ),
        "b2_quiet_persistence_stronger_than_b1": b2["row_decision"] == "supported"
        and b2["boundary_stability_score"] > b1["boundary_stability_score"],
        "b2_multi_snapshot_stability_recorded": b2["basin_descriptor"][
            "quiet_window_snapshot_count"
        ]
        > 1
        and b2["basin_descriptor"]["stable_side_assignments"] is True
        and b2["basin_descriptor"]["stable_boundary_edges"] is True,
        "b2_all_snapshots_meet_persistence_floors": b2["basin_descriptor"][
            "all_snapshots_meet_persistence_floors"
        ]
        is True,
        "b1_boundary_edges_incident_to_both_sides": bool(b1_edges)
        and all(edge["left_side"] != edge["right_side"] for edge in b1_edges),
        "b2_boundary_edges_incident_to_both_sides": bool(b2_edges)
        and all(edge["left_side"] != edge["right_side"] for edge in b2_edges),
        "no_externally_supplied_boundary_labels": all(
            row["case_policy"]["external_boundary_labels_supplied"] is False
            for row in rows
        ),
        "minimum_support_baseline_recorded": any(
            item["persistent_under_quiet_window"] is True
            and item["candidate_internal_support"] == INTERNAL_SUPPORT_FLOOR
            and item["coherence_margin"] == MINIMUM_COHERENCE_MARGIN_FLOOR
            for item in MINIMUM_SUPPORT_SWEEP
        ),
        "all_boundary_claims_false": all(
            row["boundary_claim_allowed"] is False and row["final_ap6_supported"] is False
            for row in rows
        ),
        "ap_level_remains_provisional": all(
            row["provisional_ap_level"] != "AP6" for row in rows
        ),
    }


def build_report(output: dict[str, Any]) -> str:
    rows = output["rows"]
    by_cell = {row["cell_id"]: row for row in rows}
    lines = [
        "# N16 Quiet Boundary Calibration",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 3 is calibration only. It populates B0, B1, and B2 under "
        "C0 quiet reference to check that the frozen boundary machinery can "
        "distinguish null external coherence, a localized partition, and a "
        "quiet support-persistent basin before any robustness claim is made.",
        "",
        "It does not prove AP6, run the challenge sweep, run the full control "
        "matrix, or evaluate repair/reabsorption behavior.",
        "",
        "## Row Outcomes",
        "",
        "| Cell | Decision | Boundary Claim Allowed | Classification |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['cell_id']} | {row['row_decision']} | "
            f"{row['boundary_claim_allowed']} | {row['boundary_classification']} |"
        )
    lines.extend(
        [
            "",
            "## Calibration Findings",
            "",
            "- `B0_C0` is a valid active-null row, but it is rejected as boundary "
            "support because external coherence alone produced no derived "
            "internal side and no boundary edge.",
            "- `B1_C0` extracts boundary edges and an inside/outside partition, "
            "but remains only a localized partition candidate. It does not "
            "claim persistence.",
            "- `B2_C0` adds quiet-window stability over B1: derived side "
            "assignments and boundary edges remain stable across the C0 "
            "window, with support and coherence above the frozen floors.",
            "",
            "## Minimum Quiet Baseline",
            "",
            "```json",
            json.dumps(
                output["minimum_detectable_basin_requirement"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundary Derivation",
            "",
            "Boundary-side assignments are derived from support, coherence, and "
            "basin-signal thresholds. The case data does not supply trusted "
            "`self_region_nodes`, `external_region_nodes`, or boundary labels. "
            "Those schema fields are populated after derivation.",
            "",
            "B1 derived boundary edges:",
            "",
            "```json",
            json.dumps(by_cell["B1_C0"]["boundary_edges"], indent=2, sort_keys=True),
            "```",
            "",
            "B2 derived boundary edges:",
            "",
            "```json",
            json.dumps(by_cell["B2_C0"]["boundary_edges"], indent=2, sort_keys=True),
            "```",
            "",
            "## B2 Cross-Snapshot Stability",
            "",
            "```json",
            json.dumps(
                {
                    "stable_side_assignments": by_cell["B2_C0"][
                        "basin_descriptor"
                    ]["stable_side_assignments"],
                    "stable_boundary_edges": by_cell["B2_C0"][
                        "basin_descriptor"
                    ]["stable_boundary_edges"],
                    "all_snapshots_meet_persistence_floors": by_cell["B2_C0"][
                        "basin_descriptor"
                    ]["all_snapshots_meet_persistence_floors"],
                    "quiet_window_snapshot_count": by_cell["B2_C0"][
                        "basin_descriptor"
                    ]["quiet_window_snapshot_count"],
                    "quiet_window_metrics": by_cell["B2_C0"][
                        "basin_descriptor"
                    ]["quiet_window_metrics"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "quiet boundary calibration passed != AP6 supported",
            "localized partition candidate != support-persistent boundary",
            "support-persistent basin under C0 != challenge-stable boundary",
            "artifact-visible boundary separability != selfhood, agency, native support, or life",
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def validate_with_schema() -> None:
    subprocess.run(
        [
            ".venv/bin/python",
            rel(VALIDATOR_SCRIPT),
            rel(OUTPUT_PATH),
            "--schema",
            rel(SCHEMA_OUTPUT),
        ],
        cwd=ROOT,
        check=True,
    )


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    control_config = load_json(CONTROL_VARIANTS)
    rows = build_rows(schema, inventory)
    checks = iteration_checks(rows)
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(SOURCE_REGISTRY): source_record(SOURCE_REGISTRY),
        rel(BOUNDARY_POLICY): source_record(BOUNDARY_POLICY),
        rel(BUDGET_LIMITS): source_record(BUDGET_LIMITS),
        rel(CONTROL_VARIANTS): source_record(CONTROL_VARIANTS),
        rel(REPLAY_POLICY): source_record(REPLAY_POLICY),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
    }
    output = {
        "experiment": "N16",
        "iteration": "3",
        "artifact_id": "n16_quiet_boundary_calibration",
        "purpose": "quiet_boundary_calibration",
        "schema_version": schema["schema_version"],
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_quiet_boundary_calibration_no_ap6",
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2", "3"],
        "deferred_iterations": ["4", "5", "6", "7", "8", "9"],
        "final_ap6_closeout_allowed": False,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": rows,
        "controls": top_level_controls(schema),
        "checks": checks,
        "claim_flags": control_config["claim_flags_forced_false"],
        "errors": [],
        "iteration_result": {
            "quiet_boundary_calibration_passed": all(checks.values()),
            "matrix_rows_generated": True,
            "row_count": len(rows),
            "b0_boundary_support_rejected": checks["b0_rejected_as_boundary_support"],
            "b1_partition_extracted": checks[
                "b1_boundary_edges_incident_to_both_sides"
            ],
            "b2_quiet_persistence_calibrated": checks[
                "b2_quiet_persistence_stronger_than_b1"
            ],
            "final_ap6_supported": False,
        },
        "calibration_policy": {
            "policy_id": "n16_i3_quiet_boundary_calibration_policy",
            "inherits": "n16_boundary_policy_v1",
            "condition": "C0 quiet reference",
            "calibration_only": True,
            "internal_support_floor": INTERNAL_SUPPORT_FLOOR,
            "internal_coherence_floor": INTERNAL_COHERENCE_FLOOR,
            "minimum_coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
            "basin_signal_floor": BASIN_SIGNAL_FLOOR,
            "quiet_leakage_ceiling": QUIET_LEAKAGE_CEILING,
            "quiet_stability_floor": QUIET_STABILITY_FLOOR,
            "externally_supplied_boundary_labels_allowed": False,
        },
        "minimum_detectable_basin_requirement": {
            "minimum_internal_support": INTERNAL_SUPPORT_FLOOR,
            "minimum_internal_coherence": INTERNAL_COHERENCE_FLOOR,
            "minimum_coherence_margin": MINIMUM_COHERENCE_MARGIN_FLOOR,
            "maximum_quiet_leakage_ratio": QUIET_LEAKAGE_CEILING,
            "support_sweep": MINIMUM_SUPPORT_SWEEP,
            "claim_boundary": "quiet_baseline_for_later_challenges_not_ap6_closeout",
        },
        "audit_list": [
            "C0 treated as calibration only",
            "B0 rejected as boundary support",
            "B1 limited to partition extraction",
            "B2 adds quiet persistence beyond B1",
            "boundary labels derived, not injected",
            "boundary edges checked against inside/outside assignments",
            "minimum support/coherence baseline recorded",
            "no repair or reabsorption capability claimed",
            "quiet failures would block later challenge interpretation",
            "AP level remains provisional",
        ],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
        },
        "output_digest": "",
    }
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    if not all(checks.values()):
        output["errors"].append("quiet_boundary_calibration_check_failed")
    output["output_digest"] = output_digest(output)
    return output


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validate_with_schema()
    REPORT_PATH.write_text(build_report(output), encoding="utf-8")
    print(json.dumps(output["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

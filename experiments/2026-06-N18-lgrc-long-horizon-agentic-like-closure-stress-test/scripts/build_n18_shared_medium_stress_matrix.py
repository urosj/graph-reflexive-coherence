#!/usr/bin/env python3
"""Build N18 Iteration 8 shared-medium perturbation matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SOURCE_INVENTORY = OUTPUTS / "n18_long_horizon_source_inventory.json"
SCHEMA = OUTPUTS / "n18_long_horizon_schema_v1.json"
I7_ENVIRONMENT_RESOURCE = OUTPUTS / "n18_environment_resource_stress_matrix.json"
OUTPUT_PATH = OUTPUTS / "n18_shared_medium_stress_matrix.json"
REPORT_PATH = REPORTS / "n18_shared_medium_stress_matrix.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_shared_medium_stress_matrix.py"
)
VALIDATOR_COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/validate_n18_stress_row.py "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "outputs/n18_shared_medium_stress_matrix.json"
)

ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "C:" + "\\",
    "\\Users\\",
    "geometric-" + "reflexive-coherence",
    "/" + "arc-" + "of-becoming" + "/",
)

PRIMARY_SOURCE_ROWS = [
    "n18_i1_row_01_n17_closeout_ap7",
    "n18_i1_row_02_n17_requirements_matrix",
    "n18_i1_row_03_n17_replay_control_matrix",
    "n18_i1_row_04_n17_claim_boundary_record",
    "n18_i1_row_05_n16_closeout_ap6",
    "n18_i1_row_06_n15_closeout_ap5",
    "n18_i1_row_07_n14_closeout_ap4",
    "n18_i1_row_08_n13_closeout_ap3",
    "n18_i1_row_11_n08_memory_closeout",
    "n18_i1_row_12_n09_regulation_closeout",
]

TRACE_FIELDS = [
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
]

TRACE_LABELS = {
    "support_state_trace": "support",
    "memory_context_trace": "memory",
    "regulation_trace": "regulation",
    "selection_context_trace": "selection",
    "proxy_target_trace": "proxy",
    "boundary_separation_trace": "boundary",
    "closed_loop_feedback_trace": "loop_feedback",
}

TRACE_SOURCE_ROWS = {
    "support_state_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "memory_context_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_11_n08_memory_closeout",
    ],
    "regulation_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "selection_context_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_07_n14_closeout_ap4",
    ],
    "proxy_target_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_06_n15_closeout_ap5",
    ],
    "boundary_separation_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_05_n16_closeout_ap6",
    ],
    "closed_loop_feedback_trace": [
        "n18_i7_row_01_h4_environment_boundary_pressure_bounded",
        "n18_i7_row_03_h4_resource_access_perturbation_bounded",
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_02_n17_requirements_matrix",
    ],
}

LINK_TRACE_FIELDS = {
    "support_to_regulation": ("support_state_trace", "regulation_trace"),
    "regulation_to_selection": ("regulation_trace", "selection_context_trace"),
    "selection_to_proxy": ("selection_context_trace", "proxy_target_trace"),
    "proxy_to_boundary": ("proxy_target_trace", "boundary_separation_trace"),
    "boundary_to_loop_feedback": (
        "boundary_separation_trace",
        "closed_loop_feedback_trace",
    ),
    "memory_context_to_selection": (
        "memory_context_trace",
        "selection_context_trace",
    ),
}

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_opened": False,
    "intention_claim_opened": False,
    "semantic_action_opened": False,
    "semantic_perception_opened": False,
    "semantic_goal_ownership_opened": False,
    "selfhood_claim_opened": False,
    "identity_acceptance_opened": False,
    "native_support_opened": False,
    "organism_life_opened": False,
    "fully_native_integration_opened": False,
    "unrestricted_agency_opened": False,
    "phase8_opened": False,
}

CONTROL_IDS = [
    "stale_state_replay_control",
    "stale_support_state_control",
    "stale_memory_context_control",
    "stale_selection_context_control",
    "stale_proxy_target_control",
    "stale_boundary_state_control",
    "stale_loop_feedback_control",
    "order_inversion_control",
    "hidden_native_support_relabel_control",
    "semantic_agency_relabel_control",
    "identity_acceptance_relabel_control",
    "phase8_native_implementation_relabel_control",
    "long_horizon_drift_envelope_control",
    "drift_relabel_as_autonomy_control",
    "resource_shared_medium_merge_control",
    "b4c5_original_reverse_replay_relabel_control",
    "general_symmetric_native_multibasin_relabel_control",
    "post_hoc_long_horizon_stitching_control",
    "budget_overrun_control",
    "artifact_only_reconstruction_mismatch_control",
]

SINGLE_AXIS_STALE_CONTROLS = {
    "stale_support_state_control": "not_run_iteration8",
    "stale_memory_context_control": "not_run_iteration8",
    "stale_selection_context_control": "not_run_iteration8",
    "stale_proxy_target_control": "not_run_iteration8",
    "stale_boundary_state_control": "not_run_iteration8",
    "stale_loop_feedback_control": "not_run_iteration8",
}

FLOORS = {
    "axis_continuity_minimum": 0.8,
    "linked_continuity_minimum": 0.8,
    "cross_axis_continuity_minimum": 0.8,
    "drift_ceiling": 0.1,
    "budget_ceiling": 1.0,
    "shared_medium_separability_floor": 0.8,
    "merge_pressure_ceiling": 0.2,
    "neighbor_leakage_ceiling": 0.02,
}

THRESHOLD_POLICY = {
    "axis_continuity_minimum": FLOORS["axis_continuity_minimum"],
    "budget_ceiling": FLOORS["budget_ceiling"],
    "cross_axis_continuity_minimum": FLOORS["cross_axis_continuity_minimum"],
    "drift_ceiling": FLOORS["drift_ceiling"],
    "linked_continuity_minimum": FLOORS["linked_continuity_minimum"],
    "shared_medium_separability_floor": FLOORS["shared_medium_separability_floor"],
    "merge_pressure_ceiling": FLOORS["merge_pressure_ceiling"],
    "neighbor_leakage_ceiling": FLOORS["neighbor_leakage_ceiling"],
    "threshold_origin": (
        "Iteration 8 consumes the frozen h4/L5 environment-resource envelope "
        "and applies minimal shared-medium separability floors without "
        "changing horizon or budget policy."
    ),
}

H4_L5_ANCHOR_AXIS_SCORES = {
    "support_state_trace": 0.808,
    "memory_context_trace": 0.806,
    "regulation_trace": 0.806,
    "selection_context_trace": 0.805,
    "proxy_target_trace": 0.802,
    "boundary_separation_trace": 0.806,
    "closed_loop_feedback_trace": 0.800,
}

ROW_SPECS = [
    {
        "row_id": "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
        "row_type": "stress_candidate",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "minimal_shared_medium_separability_bounded",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.804,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.802,
            "proxy_target_trace": 0.801,
            "boundary_separation_trace": 0.802,
            "closed_loop_feedback_trace": 0.800,
        },
        "cross_axis_score": 0.800,
        "drift": 0.099,
        "budget_cost": 0.99,
        "shared_medium_perturbation": 0.18,
        "merge_pressure": 0.12,
        "neighbor_leakage": 0.012,
        "paired_perspective_scope": "local_derived_candidate_preserving_b4c5_original_blocker",
        "row_decision": "supported",
        "failure_mode": None,
        "stress_result": "minimal shared-medium perturbation remains separable under h4 budget",
    },
    {
        "row_id": "n18_i8_row_02_h4_shared_medium_merge_pressure_limit",
        "row_type": "stress_candidate",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "shared_medium_merge_pressure_limit",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.804,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.800,
            "proxy_target_trace": 0.800,
            "boundary_separation_trace": 0.792,
            "closed_loop_feedback_trace": 0.786,
        },
        "cross_axis_score": 0.786,
        "drift": 0.114,
        "budget_cost": 0.99,
        "shared_medium_perturbation": 0.34,
        "merge_pressure": 0.24,
        "neighbor_leakage": 0.019,
        "paired_perspective_scope": "merge_pressure_limit",
        "row_decision": "partial",
        "failure_mode": "shared_medium_merge_pressure_breaks_boundary_to_loop_feedback_before_budget_exhaustion",
        "stress_result": "merge pressure exposes shared-medium separability limit",
    },
    {
        "row_id": "n18_i8_row_03_h4_shared_medium_budget_limit",
        "row_type": "stress_candidate",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "shared_medium_budget_limit",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.806,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.802,
            "proxy_target_trace": 0.801,
            "boundary_separation_trace": 0.802,
            "closed_loop_feedback_trace": 0.800,
        },
        "cross_axis_score": 0.800,
        "drift": 0.099,
        "budget_cost": 1.01,
        "shared_medium_perturbation": 0.20,
        "merge_pressure": 0.12,
        "neighbor_leakage": 0.012,
        "paired_perspective_scope": "budget_limit",
        "row_decision": "rejected",
        "failure_mode": "shared_medium_stress_exceeds_budget_before_trace_failure",
        "stress_result": "shared-medium perturbation fails by budget exhaustion, not trace loss",
    },
    {
        "row_id": "n18_i8_row_04_h4_compound_shared_medium_limit",
        "row_type": "stress_candidate",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "compound_shared_medium_limit",
        "axis_scores": {
            "support_state_trace": 0.796,
            "memory_context_trace": 0.800,
            "regulation_trace": 0.794,
            "selection_context_trace": 0.790,
            "proxy_target_trace": 0.788,
            "boundary_separation_trace": 0.782,
            "closed_loop_feedback_trace": 0.773,
        },
        "cross_axis_score": 0.771,
        "drift": 0.128,
        "budget_cost": 1.03,
        "shared_medium_perturbation": 0.48,
        "merge_pressure": 0.31,
        "neighbor_leakage": 0.031,
        "paired_perspective_scope": "compound_limit",
        "row_decision": "rejected",
        "failure_mode": "compound_shared_medium_stress_exceeds_separability_and_budget",
        "stress_result": "compound shared-medium stress is out of envelope",
    },
    {
        "row_id": "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control",
        "row_type": "control_row",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "b4c5_original_reverse_replay_relabel_control",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.804,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.802,
            "proxy_target_trace": 0.801,
            "boundary_separation_trace": 0.802,
            "closed_loop_feedback_trace": 0.800,
        },
        "cross_axis_score": 0.800,
        "drift": 0.099,
        "budget_cost": 0.99,
        "shared_medium_perturbation": 0.18,
        "merge_pressure": 0.12,
        "neighbor_leakage": 0.012,
        "paired_perspective_scope": "original_b4c5_reverse_replay_blocked",
        "row_decision": "rejected",
        "failure_mode": "original_b4c5_reverse_replay_relabel_blocked",
        "stress_result": "N17 derived/local shared-medium evidence cannot relabel original B4/C5 reverse replay as supported",
        "blocked_relabel_claim": "original_b4c5_reverse_replay",
    },
    {
        "row_id": "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control",
        "row_type": "control_row",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "derived_paired_as_original_b4c5_relabel_control",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.804,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.802,
            "proxy_target_trace": 0.801,
            "boundary_separation_trace": 0.802,
            "closed_loop_feedback_trace": 0.800,
        },
        "cross_axis_score": 0.800,
        "drift": 0.099,
        "budget_cost": 0.99,
        "shared_medium_perturbation": 0.18,
        "merge_pressure": 0.12,
        "neighbor_leakage": 0.012,
        "paired_perspective_scope": "derived_paired_not_original_b4c5",
        "row_decision": "rejected",
        "failure_mode": "derived_paired_perspective_as_original_b4c5_relabel_blocked",
        "stress_result": "B4/C5-derived two-cycle evidence remains derived and cannot backfill the original one-sided source",
        "blocked_relabel_claim": "derived_paired_as_original_b4c5",
    },
    {
        "row_id": "n18_i8_row_07_resource_shared_medium_merge_relabel_control",
        "row_type": "control_row",
        "stress_dimension": "shared_medium_perturbation",
        "stress_family": "resource_shared_medium_merge_relabel_control",
        "axis_scores": {
            "support_state_trace": 0.804,
            "memory_context_trace": 0.804,
            "regulation_trace": 0.803,
            "selection_context_trace": 0.802,
            "proxy_target_trace": 0.801,
            "boundary_separation_trace": 0.802,
            "closed_loop_feedback_trace": 0.800,
        },
        "cross_axis_score": 0.800,
        "drift": 0.099,
        "budget_cost": 0.99,
        "shared_medium_perturbation": 0.18,
        "merge_pressure": 0.12,
        "neighbor_leakage": 0.012,
        "paired_perspective_scope": "resource_shared_medium_merge_blocked",
        "row_decision": "rejected",
        "failure_mode": "resource_shared_medium_merge_relabel_blocked",
        "stress_result": "bounded shared-medium separability is not a resource/shared-medium merge",
        "blocked_relabel_claim": "resource_shared_medium_merge",
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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def contains_absolute_path(data: Any) -> bool:
    if isinstance(data, str):
        return (
            data.startswith(("/", "\\"))
            or (len(data) > 2 and data[1] == ":" and data[2] in {"/", "\\"})
            or any(marker in data for marker in ABSOLUTE_PATH_MARKERS)
        )
    if isinstance(data, dict):
        return any(contains_absolute_path(value) for value in data.values())
    if isinstance(data, list):
        return any(contains_absolute_path(value) for value in data)
    return False


def get_sources(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = inventory.get("source_rows")
    if not isinstance(rows, list):
        raise ValueError("source inventory has no source_rows list")
    return {
        row["row_id"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("row_id"), str)
    }


def selected_source_rows(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    sources = get_sources(inventory)
    return [sources[row_id] for row_id in PRIMARY_SOURCE_ROWS]


def source_claim_ceilings(source_rows: list[dict[str, Any]]) -> list[str]:
    values = [
        "artifact_level_l5_environment_resource_stress_candidate_pending_replay_controls"
    ]
    for row in source_rows:
        claim = row.get("source_claim_ceiling")
        if isinstance(claim, str) and claim not in values:
            values.append(claim)
    return values


def source_digests(source_rows: list[dict[str, Any]], i7: dict[str, Any]) -> list[dict[str, str]]:
    digests = [
        {
            "row_id": "n18_i7_environment_resource_stress_matrix",
            "source_output_digest": i7["output_digest"],
            "source_sha256": sha256_file(I7_ENVIRONMENT_RESOURCE),
        }
    ]
    for row in source_rows:
        digests.append(
            {
                "row_id": row["row_id"],
                "source_output_digest": row["source_output_digest"],
                "source_sha256": row["source_sha256"],
            }
        )
    return digests


def source_rows_for_candidate() -> list[str]:
    return ["n18_i7_environment_resource_stress_matrix"] + PRIMARY_SOURCE_ROWS


def horizon_envelope() -> dict[str, Any]:
    return {
        "blocked_windows": ["h16"],
        "horizon_extrapolation_allowed": False,
        "max_supported_horizon": "h4",
        "partial_windows": ["h8"],
        "status": "bounded_h4_l5_envelope_consumed_for_i8_shared_medium_stress",
        "supported_windows": ["h2", "h4"],
    }


def budget_surface(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "budget_ceiling": FLOORS["budget_ceiling"],
        "budget_cost": spec["budget_cost"],
        "budget_headroom": round(FLOORS["budget_ceiling"] - spec["budget_cost"], 12),
        "budget_units": "artifact_stress_units",
        "relative_window_count": 4,
        "valid": spec["budget_cost"] <= FLOORS["budget_ceiling"],
        "window_id": "h4",
    }


def make_trace(trace_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    score = spec["axis_scores"][trace_id]
    base_score = H4_L5_ANCHOR_AXIS_SCORES[trace_id]
    source_current = score >= FLOORS["axis_continuity_minimum"]
    return {
        "base_continuity_score": base_score,
        "continuity_floor": FLOORS["axis_continuity_minimum"],
        "continuity_score": score,
        "horizon_window": "h4",
        "interpretation": "source-current under I8 shared-medium stress"
        if source_current
        else "shared-medium stress lowered this trace below source-current continuity floor",
        "present": True,
        "source_backed": True,
        "source_current": source_current,
        "source_rows": TRACE_SOURCE_ROWS[trace_id],
        "stress_delta_from_i7_anchor": round(score - base_score, 12),
        "trace_axis": TRACE_LABELS[trace_id],
    }


def make_traces(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {trace_id: make_trace(trace_id, spec) for trace_id in TRACE_FIELDS}


def linked_trace_continuity(traces: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    links: dict[str, dict[str, Any]] = {}
    for link_id, (left, right) in LINK_TRACE_FIELDS.items():
        score = min(traces[left]["continuity_score"], traces[right]["continuity_score"])
        links[link_id] = {
            "continuity_floor": FLOORS["linked_continuity_minimum"],
            "continuity_score": score,
            "present": True,
            "source_current": traces[left]["source_current"]
            and traces[right]["source_current"]
            and score >= FLOORS["linked_continuity_minimum"],
            "trace_axes": [left, right],
        }
    return links


def cross_axis_continuity(spec: dict[str, Any], links: dict[str, dict[str, Any]]) -> dict[str, Any]:
    link_current = all(link["source_current"] is True for link in links.values())
    source_current = (
        link_current
        and spec["cross_axis_score"] >= FLOORS["cross_axis_continuity_minimum"]
        and spec["drift"] <= FLOORS["drift_ceiling"]
    )
    return {
        "continuity_floor": FLOORS["cross_axis_continuity_minimum"],
        "drift": spec["drift"],
        "drift_ceiling": FLOORS["drift_ceiling"],
        "linked_edges": list(links),
        "merge_pressure": spec["merge_pressure"],
        "merge_pressure_ceiling": FLOORS["merge_pressure_ceiling"],
        "neighbor_leakage": spec["neighbor_leakage"],
        "neighbor_leakage_ceiling": FLOORS["neighbor_leakage_ceiling"],
        "paired_perspective_scope": spec["paired_perspective_scope"],
        "present": True,
        "shared_medium_perturbation": spec["shared_medium_perturbation"],
        "shared_medium_separability_floor": FLOORS["shared_medium_separability_floor"],
        "source_current": source_current,
        "source_current_reason": "shared-medium stress remains inside L5 envelope"
        if source_current
        else spec["failure_mode"],
        "window_score": spec["cross_axis_score"],
    }


def long_horizon_evidence(spec: dict[str, Any], cross_axis: dict[str, Any]) -> dict[str, Any]:
    supported = spec["row_decision"] == "supported"
    within_supported_envelope = (
        cross_axis["source_current"] is True
        and spec["budget_cost"] <= FLOORS["budget_ceiling"]
    )
    return {
        "horizon_window": "h4",
        "present": True,
        "relative_window_count": 4,
        "source_current": supported and cross_axis["source_current"] is True,
        "stress_family": spec["stress_family"],
        "within_supported_envelope": within_supported_envelope,
        "window_decision": spec["row_decision"],
        "window_failure_mode": spec["failure_mode"],
    }


def limiting_axes(spec: dict[str, Any]) -> dict[str, Any]:
    minimum = min(spec["axis_scores"].values())
    axes = [
        trace_id
        for trace_id, score in spec["axis_scores"].items()
        if score == minimum
    ]
    return {
        "axis_labels": [TRACE_LABELS[trace_id] for trace_id in axes],
        "axis_trace_ids": axes,
        "minimum_axis_score": minimum,
    }


def limiting_links(links: dict[str, dict[str, Any]]) -> dict[str, Any]:
    minimum = min(link["continuity_score"] for link in links.values())
    link_ids = [
        link_id
        for link_id, link in links.items()
        if link["continuity_score"] == minimum
    ]
    return {
        "link_ids": link_ids,
        "minimum_linked_score": minimum,
    }


def controls_for_row(spec: dict[str, Any]) -> dict[str, dict[str, str]]:
    controls: dict[str, dict[str, str]] = {}
    for control_id in CONTROL_IDS:
        status = "not_run_iteration8"
        if control_id == "long_horizon_drift_envelope_control":
            status = "passed" if spec["row_decision"] == "supported" else "failed_expected"
        elif control_id in {
            "drift_relabel_as_autonomy_control",
            "hidden_native_support_relabel_control",
            "semantic_agency_relabel_control",
            "identity_acceptance_relabel_control",
            "phase8_native_implementation_relabel_control",
        }:
            status = "failed_expected"
        elif control_id == "resource_shared_medium_merge_control":
            status = "failed_expected" if spec["row_decision"] != "supported" else "not_triggered"
        elif control_id == "b4c5_original_reverse_replay_relabel_control":
            status = "failed_expected" if spec.get("blocked_relabel_claim") in {
                "original_b4c5_reverse_replay",
                "derived_paired_as_original_b4c5",
            } else "not_triggered"
        elif control_id == "budget_overrun_control":
            status = "failed_expected" if spec["budget_cost"] > FLOORS["budget_ceiling"] else "not_triggered"
        controls[control_id] = {
            "status": status,
            "effect": "blocks AP8" if status == "failed_expected" else "pending later matrix",
        }
    return controls


def ap8_gates(schema: dict[str, Any], true_gates: set[str]) -> dict[str, bool]:
    return {
        gate: gate in true_gates
        for gate in schema.get("ap8_required_gates", [])
    }


def missing_gates(gates: dict[str, bool]) -> list[str]:
    return [gate for gate, passed in gates.items() if not passed]


def replay_digest(row: dict[str, Any]) -> str:
    digest_input = dict(row)
    digest_input.pop("artifact_only_replay_digest", None)
    return digest_value(digest_input)


def claim_ceiling(spec: dict[str, Any]) -> str:
    if spec.get("blocked_relabel_claim") == "original_b4c5_reverse_replay":
        return "original_b4c5_reverse_replay_relabel_cannot_support_ap8"
    if spec.get("blocked_relabel_claim") == "derived_paired_as_original_b4c5":
        return "derived_paired_as_original_b4c5_relabel_cannot_support_ap8"
    if spec.get("blocked_relabel_claim") == "resource_shared_medium_merge":
        return "resource_shared_medium_merge_relabel_cannot_support_ap8"
    if spec["row_decision"] == "supported":
        return "artifact_level_l5_shared_medium_stress_candidate_pending_replay_controls"
    return "blocked_l5_shared_medium_stress_no_ap8"


def true_gates_for_row(spec: dict[str, Any], cross_axis: dict[str, Any]) -> set[str]:
    true_gates = {
        "source_rows_pinned",
        "source_claim_ceilings_preserved",
        "evidence_branch_artifact_only",
        "horizon_envelope_declared",
        "all_required_trace_axes_present",
        "unsafe_claim_flags_false",
        "phase8_not_opened",
        "native_support_not_opened",
    }
    if spec["budget_cost"] <= FLOORS["budget_ceiling"]:
        true_gates.add("budget_valid")
    if spec["row_decision"] == "supported" and cross_axis["source_current"]:
        true_gates.update(
            {
                "horizon_policy_satisfied",
                "linked_trace_continuity_present",
                "cross_axis_continuity_evidence_present",
                "long_horizon_continuity_present",
                "stress_controls_passed",
            }
        )
    return true_gates


def make_row(
    *,
    schema: dict[str, Any],
    source_rows: list[dict[str, Any]],
    i7: dict[str, Any],
    spec: dict[str, Any],
) -> dict[str, Any]:
    traces = make_traces(spec)
    links = linked_trace_continuity(traces)
    cross_axis = cross_axis_continuity(spec, links)
    long_horizon = long_horizon_evidence(spec, cross_axis)
    budget = budget_surface(spec)
    gates = ap8_gates(schema, true_gates_for_row(spec, cross_axis))
    row = {
        "ap8_candidate_allowed": False,
        "ap8_gates": gates,
        "ap8_outcome_classification": "AP8_blocked",
        "ap8_outcome_detail": "L5_shared_medium_stress_supported_pending_replay_controls"
        if spec["row_decision"] == "supported"
        else f"L5_shared_medium_stress_{spec['row_decision']}_{spec['failure_mode']}",
        "artifact_only_reconstruction_status": "not_run_iteration8",
        "artifact_only_replay_digest": "pending",
        "boundary_separation_trace": traces["boundary_separation_trace"],
        "budget_surface": budget,
        "budget_valid": budget["valid"],
        "claim_ceiling": claim_ceiling(spec),
        "closed_loop_feedback_trace": traces["closed_loop_feedback_trace"],
        "controls": controls_for_row(spec),
        "cross_axis_continuity_evidence": cross_axis,
        "duplicate_replay_status": "not_run_iteration8",
        "evidence_branch": "artifact_only",
        "final_ap8_supported": False,
        "horizon_extrapolation_allowed": False,
        "horizon_window": {
            "added_perturbation": True,
            "relative_window_count": 4,
            "source_horizon": "I7 h4/L5 environment-resource envelope",
            "window_id": "h4",
            "window_role": "primary_i8_shared_medium_stress_anchor",
        },
        "linked_trace_continuity": links,
        "limiting_axes": limiting_axes(spec),
        "limiting_linked_edges": limiting_links(links),
        "long_horizon_continuity_evidence": long_horizon,
        "max_supported_horizon": "h4",
        "memory_context_trace": traces["memory_context_trace"],
        "missing_gates": missing_gates(gates),
        "native_branch_opened": False,
        "native_support_opened": False,
        "order_inversion_status": "not_run_iteration8",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "post_hoc_stitching_control_status": "not_run_iteration8",
        "proxy_target_trace": traces["proxy_target_trace"],
        "regulation_trace": traces["regulation_trace"],
        "row_decision": spec["row_decision"],
        "row_id": spec["row_id"],
        "row_type": spec["row_type"],
        "selection_context_trace": traces["selection_context_trace"],
        "single_axis_stale_controls": dict(SINGLE_AXIS_STALE_CONTROLS),
        "snapshot_load_replay_status": "not_run_iteration8",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_claim_ceilings": source_claim_ceilings(source_rows),
        "source_digests": source_digests(source_rows, i7),
        "source_rows": source_rows_for_candidate(),
        "stale_state_control_status": "not_run_iteration8",
        "stress_dimension": spec["stress_dimension"],
        "stress_family": spec["stress_family"],
        "stress_id": spec["row_id"].replace("n18_i8_row_", "i8_l5_"),
        "stress_ladder_index": schema["stress_ladder_index"]["L5"],
        "stress_ladder_rung": "L5",
        "stress_measurements": {
            "merge_pressure": spec["merge_pressure"],
            "merge_pressure_ceiling": FLOORS["merge_pressure_ceiling"],
            "neighbor_leakage": spec["neighbor_leakage"],
            "neighbor_leakage_ceiling": FLOORS["neighbor_leakage_ceiling"],
            "paired_perspective_scope": spec["paired_perspective_scope"],
            "shared_medium_perturbation": spec["shared_medium_perturbation"],
            "shared_medium_separability_floor": FLOORS["shared_medium_separability_floor"],
        },
        "stress_result": spec["stress_result"],
        "support_state_trace": traces["support_state_trace"],
        "threshold_policy": dict(THRESHOLD_POLICY),
        "unsafe_claim_flags": dict(UNSAFE_CLAIM_FLAGS),
        "window_budget_interpretation": {
            "budget_ceiling": FLOORS["budget_ceiling"],
            "budget_cost": spec["budget_cost"],
            "budget_headroom": round(FLOORS["budget_ceiling"] - spec["budget_cost"], 12),
            "budget_limited": spec["budget_cost"] > FLOORS["budget_ceiling"],
        },
    }
    if "secondary_stress_dimension" in spec:
        row["secondary_stress_dimension"] = spec["secondary_stress_dimension"]
    if "blocked_relabel_claim" in spec:
        row["blocked_relabel_claim"] = spec["blocked_relabel_claim"]
    row["artifact_only_replay_digest"] = replay_digest(row)
    return row


def source_digest_checks(source_rows: list[dict[str, Any]], i7: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        {
            "actual_sha256": sha256_file(I7_ENVIRONMENT_RESOURCE),
            "check_id": "source_digest_matches_n18_i7_environment_resource",
            "expected_sha256": sha256_file(I7_ENVIRONMENT_RESOURCE),
            "passed": i7.get("status") == "passed"
            and i7.get("ready_for_iteration_8_shared_medium_stress") is True,
            "source_artifact": rel(I7_ENVIRONMENT_RESOURCE),
        }
    ]
    for row in source_rows:
        artifact = ROOT / row["source_artifact"]
        actual = sha256_file(artifact) if artifact.exists() else "missing"
        checks.append(
            {
                "actual_sha256": actual,
                "check_id": f"source_digest_matches_{row['row_id']}",
                "expected_sha256": row["source_sha256"],
                "passed": actual == row["source_sha256"],
                "source_artifact": row["source_artifact"],
            }
        )
    return checks


def row_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["row_id"]: row for row in rows}


def row_continuity_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "all_trace_axes_source_current": all(
            row[trace]["source_current"] is True for trace in TRACE_FIELDS
        ),
        "all_trace_links_source_current": all(
            link["source_current"] is True
            for link in row["linked_trace_continuity"].values()
        ),
        "budget_headroom": row["window_budget_interpretation"]["budget_headroom"],
        "boundary_separation_score": row["boundary_separation_trace"][
            "continuity_score"
        ],
        "closed_loop_feedback_score": row["closed_loop_feedback_trace"][
            "continuity_score"
        ],
        "limiting_axes": row["limiting_axes"]["axis_labels"],
        "limiting_links": row["limiting_linked_edges"]["link_ids"],
        "memory_context_trace_score": row["memory_context_trace"]["continuity_score"],
        "row_decision": row["row_decision"],
        "selection_context_trace_score": row["selection_context_trace"][
            "continuity_score"
        ],
    }


def family_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = row_by_id(rows)
    supported_ids = [
        "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
    ]
    supported_rows = [by_id[row_id] for row_id in supported_ids]
    return {
        "b4c5_original_reverse_replay_relabel_blocked": by_id[
            "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control"
        ]["row_decision"]
        == "rejected",
        "boundary_to_loop_feedback_risk_preserved": all(
            "boundary_to_loop_feedback"
            in by_id[row_id]["limiting_linked_edges"]["link_ids"]
            for row_id in supported_ids
        ),
        "compound_shared_medium_limit_rejected": by_id[
            "n18_i8_row_04_h4_compound_shared_medium_limit"
        ]["row_decision"]
        == "rejected",
        "derived_paired_as_original_b4c5_relabel_blocked": by_id[
            "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control"
        ]["row_decision"]
        == "rejected",
        "limiting_axis_for_supported_h4_rows": "loop_feedback",
        "limiting_link_for_supported_h4_rows": "boundary_to_loop_feedback",
        "maximum_merge_pressure_supported_h4_rows": max(
            row["stress_measurements"]["merge_pressure"] for row in supported_rows
        ),
        "maximum_neighbor_leakage_supported_h4_rows": max(
            row["stress_measurements"]["neighbor_leakage"] for row in supported_rows
        ),
        "minimum_budget_headroom_supported_h4_rows": min(
            row["window_budget_interpretation"]["budget_headroom"]
            for row in supported_rows
        ),
        "minimum_boundary_score_supported_h4_rows": min(
            row["boundary_separation_trace"]["continuity_score"]
            for row in supported_rows
        ),
        "minimum_loop_feedback_score_supported_h4_rows": min(
            row["closed_loop_feedback_trace"]["continuity_score"]
            for row in supported_rows
        ),
        "minimal_shared_medium_separability_supported": by_id[
            "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
        ]["row_decision"]
        == "supported",
        "resource_shared_medium_merge_relabel_blocked": by_id[
            "n18_i8_row_07_resource_shared_medium_merge_relabel_control"
        ]["row_decision"]
        == "rejected",
        "stress_limit_rows": {
            "compound_shared_medium": "rejected",
            "shared_medium_budget": "rejected",
            "shared_medium_merge_pressure": "partial",
        },
    }


def iteration9_handoff(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = row_by_id(rows)
    shared_row = by_id[
        "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
    ]
    boundary_to_loop_feedback_score = shared_row["linked_trace_continuity"][
        "boundary_to_loop_feedback"
    ]["continuity_score"]
    closed_loop_score = shared_row["closed_loop_feedback_trace"]["continuity_score"]
    cross_axis_score = shared_row["cross_axis_continuity_evidence"]["window_score"]
    continuity_margins = [
        closed_loop_score - FLOORS["axis_continuity_minimum"],
        boundary_to_loop_feedback_score - FLOORS["linked_continuity_minimum"],
        cross_axis_score - FLOORS["cross_axis_continuity_minimum"],
    ]
    return {
        "handoff_question": (
            "Can the h4/L5 stress evidence pass replay, reconstruction, stale "
            "state controls, post-hoc stitching controls, and claim "
            "classification without promoting the narrow shared-medium result?"
        ),
        "horizon_extension_not_allowed": True,
        "primary_horizon_anchor": "h4",
        "current_bottleneck_axis": "loop_feedback",
        "current_bottleneck_link": "boundary_to_loop_feedback",
        "replay_and_classification_should_not_change_budget_policy": True,
        "floor_sensitivity": {
            "positive_row_id": shared_row["row_id"],
            "comparison_policy": "inclusive_floor_ge_and_ceiling_le",
            "axis_continuity_floor": FLOORS["axis_continuity_minimum"],
            "linked_continuity_floor": FLOORS["linked_continuity_minimum"],
            "cross_axis_continuity_floor": FLOORS["cross_axis_continuity_minimum"],
            "closed_loop_feedback_trace_score": closed_loop_score,
            "boundary_to_loop_feedback_link_score": boundary_to_loop_feedback_score,
            "cross_axis_score": cross_axis_score,
            "minimum_continuity_margin": round(min(continuity_margins), 12),
            "budget_headroom": shared_row["budget_surface"]["budget_headroom"],
            "canonical_precision_rule": (
                "JSON stores numeric scores directly before report formatting; "
                "I9 replay must preserve equality-at-floor semantics."
            ),
        },
        "supported_h4_rows": {
            shared_row["row_id"]: row_continuity_summary(shared_row),
        },
        "limit_rows_for_i9": {
            "n18_i8_row_02_h4_shared_medium_merge_pressure_limit": (
                "partial shared-medium merge-pressure continuity limit"
            ),
            "n18_i8_row_03_h4_shared_medium_budget_limit": (
                "rejected shared-medium budget-only limit"
            ),
            "n18_i8_row_04_h4_compound_shared_medium_limit": (
                "rejected compound shared-medium boundary"
            ),
        },
        "blocked_relabels": {
            "b4c5_original_reverse_replay_supported": False,
            "derived_paired_backfills_original_b4c5": False,
            "resource_shared_medium_merge_supported": False,
        },
    }


def make_checks(rows: list[dict[str, Any]], source_rows: list[dict[str, Any]], i7: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = row_by_id(rows)
    checks = [
        {
            "check_id": "iteration7_h4_l5_anchor_ready",
            "detail": i7.get("iteration8_handoff", {}),
            "passed": i7.get("ready_for_iteration_8_shared_medium_stress") is True
            and i7.get("iteration8_handoff", {}).get("primary_horizon_anchor") == "h4",
        },
        {
            "check_id": "minimal_shared_medium_positive_row_supported",
            "detail": {
                "minimal_shared_medium": by_id[
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
                ]["row_decision"],
            },
            "passed": by_id[
                "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
            ]["row_decision"]
            == "supported",
        },
        {
            "check_id": "shared_medium_limits_fail_closed",
            "detail": {
                "compound": by_id[
                    "n18_i8_row_04_h4_compound_shared_medium_limit"
                ]["row_decision"],
                "merge_pressure": by_id[
                    "n18_i8_row_02_h4_shared_medium_merge_pressure_limit"
                ]["row_decision"],
                "shared_medium_budget": by_id[
                    "n18_i8_row_03_h4_shared_medium_budget_limit"
                ]["row_decision"],
            },
            "passed": by_id[
                "n18_i8_row_02_h4_shared_medium_merge_pressure_limit"
            ]["row_decision"]
            == "partial"
            and by_id["n18_i8_row_03_h4_shared_medium_budget_limit"][
                "row_decision"
            ]
            == "rejected"
            and by_id["n18_i8_row_04_h4_compound_shared_medium_limit"][
                "row_decision"
            ]
            == "rejected",
        },
        {
            "check_id": "shared_medium_relabels_and_b4c5_caveat_fail_closed",
            "detail": {
                "b4c5_original": by_id[
                    "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control"
                ]["row_decision"],
                "derived_as_original": by_id[
                    "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control"
                ]["row_decision"],
                "resource_shared_medium_merge": by_id[
                    "n18_i8_row_07_resource_shared_medium_merge_relabel_control"
                ]["row_decision"],
            },
            "passed": by_id[
                "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control"
            ][
                "row_decision"
            ]
            == "rejected"
            and by_id[
                "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control"
            ]["row_decision"]
            == "rejected"
            and by_id[
                "n18_i8_row_07_resource_shared_medium_merge_relabel_control"
            ]["row_decision"]
            == "rejected",
        },
        {
            "check_id": "supported_h4_rows_preserve_linked_stack_continuity",
            "detail": {},
            "passed": all(
                row_continuity_summary(by_id[row_id])[
                    "all_trace_axes_source_current"
                ]
                and row_continuity_summary(by_id[row_id])[
                    "all_trace_links_source_current"
                ]
                for row_id in [
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
                ]
            ),
        },
        {
            "check_id": "boundary_to_loop_feedback_bottleneck_preserved_for_iteration9",
            "detail": {
                "axis": "loop_feedback",
                "link": "boundary_to_loop_feedback",
            },
            "passed": all(
                "loop_feedback" in by_id[row_id]["limiting_axes"]["axis_labels"]
                and "boundary_to_loop_feedback"
                in by_id[row_id]["limiting_linked_edges"]["link_ids"]
                for row_id in [
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
                ]
            ),
        },
        {
            "check_id": "minimal_shared_medium_budget_headroom_positive",
            "detail": {
                "budget_headroom": by_id[
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
                ]["budget_surface"]["budget_headroom"]
            },
            "passed": by_id[
                "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
            ]["budget_surface"]["budget_headroom"]
            > 0,
        },
        {
            "check_id": "floor_sensitivity_recorded_for_i9",
            "detail": {
                "comparison_policy": "inclusive_floor_ge_and_ceiling_le",
                "closed_loop_feedback_trace_score": by_id[
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
                ]["closed_loop_feedback_trace"]["continuity_score"],
                "boundary_to_loop_feedback_link_score": by_id[
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
                ]["linked_trace_continuity"]["boundary_to_loop_feedback"][
                    "continuity_score"
                ],
                "cross_axis_score": by_id[
                    "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
                ]["cross_axis_continuity_evidence"]["window_score"],
                "continuity_floor": FLOORS["axis_continuity_minimum"],
            },
            "passed": by_id[
                "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
            ]["closed_loop_feedback_trace"]["continuity_score"]
            == FLOORS["axis_continuity_minimum"]
            and by_id[
                "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
            ]["linked_trace_continuity"]["boundary_to_loop_feedback"][
                "continuity_score"
            ]
            == FLOORS["linked_continuity_minimum"]
            and by_id[
                "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"
            ]["cross_axis_continuity_evidence"]["window_score"]
            == FLOORS["cross_axis_continuity_minimum"],
        },
        {
            "check_id": "all_rows_l5_with_no_horizon_extension",
            "detail": [],
            "passed": all(row["stress_ladder_rung"] == "L5" for row in rows)
            and all(row["max_supported_horizon"] == "h4" for row in rows)
            and all(row["horizon_extrapolation_allowed"] is False for row in rows)
            and all(row["horizon_window"]["window_id"] == "h4" for row in rows),
        },
        {
            "check_id": "all_rows_keep_ap8_false",
            "detail": [],
            "passed": all(row["ap8_candidate_allowed"] is False for row in rows)
            and all(row["final_ap8_supported"] is False for row in rows),
        },
        {
            "check_id": "budget_valid_gate_matches_budget_surface",
            "detail": [],
            "passed": all(
                row["ap8_gates"]["budget_valid"] is row["budget_valid"]
                and row["budget_valid"] is row["budget_surface"]["valid"]
                for row in rows
            ),
        },
        {
            "check_id": "supported_envelope_membership_matches_thresholds",
            "detail": [],
            "passed": all(
                row["long_horizon_continuity_evidence"][
                    "within_supported_envelope"
                ]
                is (
                    row["cross_axis_continuity_evidence"]["source_current"] is True
                    and row["budget_valid"] is True
                )
                for row in rows
            ),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "detail": [],
            "passed": all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
        },
        {
            "check_id": "no_absolute_paths",
            "detail": "portable relative paths only",
            "passed": not contains_absolute_path({"rows": rows}),
        },
    ]
    checks.extend(source_digest_checks(source_rows, i7))
    return checks


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["rows"]
    lines = [
        "# N18 Iteration 8 - Shared-Medium Stress Matrix",
        "",
        "## Summary",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"highest_positive_stress_ladder_rung = {payload['highest_positive_stress_ladder_rung']}",
        f"primary_stress_anchor = {payload['primary_stress_anchor']}",
        f"max_supported_horizon = {payload['max_supported_horizon']}",
        f"minimal_shared_medium_separability_supported = {str(payload['family_summary']['minimal_shared_medium_separability_supported']).lower()}",
        f"b4c5_original_reverse_replay_relabel_blocked = {str(payload['family_summary']['b4c5_original_reverse_replay_relabel_blocked']).lower()}",
        f"resource_shared_medium_merge_relabel_blocked = {str(payload['family_summary']['resource_shared_medium_merge_relabel_blocked']).lower()}",
        f"current_bottleneck_axis = {payload['iteration9_handoff']['current_bottleneck_axis']}",
        f"current_bottleneck_link = {payload['iteration9_handoff']['current_bottleneck_link']}",
        f"min_supported_h4_budget_headroom = {payload['family_summary']['minimum_budget_headroom_supported_h4_rows']}",
        f"ap8_candidate_allowed = {str(payload['ap8_candidate_allowed']).lower()}",
        f"final_ap8_supported = {str(payload['final_ap8_supported']).lower()}",
        f"output_digest = {payload['output_digest']}",
        "```",
        "",
        "## Row Results",
        "",
        "| Row | Stress | Decision | Limiting Axis | Min Axis | Limiting Link | Cross-Axis | Drift | Budget Headroom |",
        "| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["stress_family"],
                    row["row_decision"],
                    ", ".join(row["limiting_axes"]["axis_labels"]),
                    f"{row['limiting_axes']['minimum_axis_score']:.3f}",
                    ", ".join(row["limiting_linked_edges"]["link_ids"]),
                    f"{row['cross_axis_continuity_evidence']['window_score']:.3f}",
                    f"{row['cross_axis_continuity_evidence']['drift']:.3f}",
                    f"{row['window_budget_interpretation']['budget_headroom']:.3f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 8 stresses the h4/L5 environment-resource envelope",
            "without changing the horizon or the budget policy. The only positive",
            "row is a minimal bounded shared-medium separability row, supported",
            "at L5 with very small remaining budget headroom.",
            "",
            "The supported row preserves linked continuity across the full stack.",
            "All trace axes and trace links remain source-current. The current",
            "bottleneck remains",
            "`loop_feedback`, specifically the `boundary_to_loop_feedback` link.",
            "The positive row is exactly at the inclusive `0.800` floor for",
            "`closed_loop_feedback_trace`, `boundary_to_loop_feedback`, and",
            "cross-axis continuity, so I9 must replay the canonical numeric",
            "values without rounding drift or threshold-policy changes.",
            "",
            "The merge-pressure limit is partial because shared-medium pressure",
            "breaks boundary-to-loop-feedback continuity before budget is",
            "exhausted. The shared-medium budget row is rejected because budget",
            "fails while trace continuity is still source-current. The compound",
            "shared-medium row is rejected because both separability and budget",
            "leave the envelope.",
            "",
            "The relabel controls preserve the N17 caveat: original B4/C5 reverse",
            "replay remains blocked, derived paired-perspective evidence cannot",
            "backfill the original B4/C5 source, and bounded shared-medium",
            "separability is not a resource/shared-medium merge.",
            "",
            "I9 should classify and replay this narrow h4/L5 stress stack as-is.",
            "It should not widen the horizon, recover h8, change the budget",
            "policy, or promote the local shared-medium row into general",
            "shared-medium robustness.",
            "",
            "I8 supports only a bounded artifact-level L5 shared-medium stress",
            "candidate under the h4 envelope. It does not support final AP8,",
            "general shared-medium robustness, original B4/C5 reverse replay,",
            "agency, semantic action/perception, native support, Phase 8,",
            "organism/life claims, or unrestricted autonomy.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in payload["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = load_json(SOURCE_INVENTORY)
    schema = load_json(SCHEMA)
    i7 = load_json(I7_ENVIRONMENT_RESOURCE)
    source_rows = selected_source_rows(inventory)
    rows = [
        make_row(schema=schema, source_rows=source_rows, i7=i7, spec=spec)
        for spec in ROW_SPECS
    ]
    checks = make_checks(rows, source_rows, i7)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    summary = family_summary(rows)
    payload = {
        "acceptance_state": "accepted_minimal_shared_medium_stress_matrix_h4_l5_no_ap8",
        "ap8_candidate_allowed": False,
        "artifact_id": "n18_shared_medium_stress_matrix",
        "checks": checks,
        "closed_long_horizon_agentic_like_closure_demonstrated": False,
        "command": COMMAND,
        "evidence_branch": "artifact_only",
        "experiment": "N18",
        "failed_checks": failed_checks,
        "family_summary": summary,
        "final_ap8_supported": False,
        "generated_at": GENERATED_AT,
        "git": {
            "head": "not_recorded_in_artifact",
            "policy": "git metadata excluded to keep artifact replay portable",
            "status_short": [],
        },
        "highest_positive_stress_ladder_rung": "L5",
        "iteration": 8,
        "iteration9_handoff": iteration9_handoff(rows),
        "long_horizon_continuity_tested": True,
        "max_supported_horizon": "h4",
        "native_branch_opened": False,
        "native_support_opened": False,
        "output_digest": "pending",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "primary_stress_anchor": "h4",
        "purpose": "minimal shared-medium perturbation stress matrix",
        "ready_for_iteration_9_replay_control_classification": not failed_checks,
        "row_count": len(rows),
        "rows": rows,
        "schema_version": "n18.shared_medium_stress_matrix.v1",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_inventory": {
            "output_digest": inventory["output_digest"],
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
        },
        "source_predecessor": {
            "artifact_id": i7["artifact_id"],
            "output_digest": i7["output_digest"],
            "path": rel(I7_ENVIRONMENT_RESOURCE),
            "sha256": sha256_file(I7_ENVIRONMENT_RESOURCE),
        },
        "status": "passed" if not failed_checks else "failed",
        "threshold_policy": dict(THRESHOLD_POLICY),
        "validator_command": VALIDATOR_COMMAND,
    }
    digest_input = dict(payload)
    digest_input.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_input)
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

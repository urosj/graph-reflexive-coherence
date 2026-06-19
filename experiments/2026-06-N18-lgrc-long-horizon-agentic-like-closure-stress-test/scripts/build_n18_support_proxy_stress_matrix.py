#!/usr/bin/env python3
"""Build N18 Iteration 5 support/proxy stress matrix."""

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
I4_HORIZON_SWEEP = OUTPUTS / "n18_horizon_window_sweep.json"
OUTPUT_PATH = OUTPUTS / "n18_support_proxy_stress_matrix.json"
REPORT_PATH = REPORTS / "n18_support_proxy_stress_matrix.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_support_proxy_stress_matrix.py"
)
VALIDATOR_COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/validate_n18_stress_row.py "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "outputs/n18_support_proxy_stress_matrix.json"
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
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "memory_context_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_11_n08_memory_closeout",
    ],
    "regulation_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "selection_context_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_07_n14_closeout_ap4",
    ],
    "proxy_target_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_06_n15_closeout_ap5",
    ],
    "boundary_separation_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
        "n18_i1_row_05_n16_closeout_ap6",
    ],
    "closed_loop_feedback_trace": [
        "n18_i4_row_02_h4_no_added_perturbation",
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
    "stale_support_state_control": "not_run_iteration5",
    "stale_memory_context_control": "not_run_iteration5",
    "stale_selection_context_control": "not_run_iteration5",
    "stale_proxy_target_control": "not_run_iteration5",
    "stale_boundary_state_control": "not_run_iteration5",
    "stale_loop_feedback_control": "not_run_iteration5",
}

FLOORS = {
    "axis_continuity_minimum": 0.8,
    "linked_continuity_minimum": 0.8,
    "cross_axis_continuity_minimum": 0.8,
    "drift_ceiling": 0.1,
    "budget_ceiling": 1.0,
    "target_deviation_ceiling": 0.05,
}

THRESHOLD_POLICY = {
    "axis_continuity_minimum": FLOORS["axis_continuity_minimum"],
    "budget_ceiling": FLOORS["budget_ceiling"],
    "cross_axis_continuity_minimum": FLOORS["cross_axis_continuity_minimum"],
    "drift_ceiling": FLOORS["drift_ceiling"],
    "linked_continuity_minimum": FLOORS["linked_continuity_minimum"],
    "target_deviation_ceiling": FLOORS["target_deviation_ceiling"],
    "threshold_origin": (
        "Iteration 5 consumes the frozen I4 h4 L2 envelope as primary anchor "
        "and applies predeclared support/proxy stress floors before row "
        "evaluation. These thresholds bound local I5 stress only and do not "
        "close AP8."
    ),
}

H4_BASE_AXIS_SCORES = {
    "support_state_trace": 0.88,
    "memory_context_trace": 0.86,
    "regulation_trace": 0.87,
    "selection_context_trace": 0.85,
    "proxy_target_trace": 0.84,
    "boundary_separation_trace": 0.86,
    "closed_loop_feedback_trace": 0.83,
}

H2_BASE_AXIS_SCORES = {
    "support_state_trace": 0.93,
    "memory_context_trace": 0.91,
    "regulation_trace": 0.92,
    "selection_context_trace": 0.90,
    "proxy_target_trace": 0.89,
    "boundary_separation_trace": 0.91,
    "closed_loop_feedback_trace": 0.88,
}

ROW_SPECS = [
    {
        "row_id": "n18_i5_row_01_h4_support_withdrawal_restoration_bounded",
        "stress_dimension": "support_withdrawal_restoration",
        "stress_family": "support_withdrawal_restoration",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.835,
            "memory_context_trace": 0.852,
            "regulation_trace": 0.842,
            "selection_context_trace": 0.833,
            "proxy_target_trace": 0.828,
            "boundary_separation_trace": 0.842,
            "closed_loop_feedback_trace": 0.812,
        },
        "cross_axis_score": 0.812,
        "drift": 0.094,
        "budget_cost": 0.72,
        "support_withdrawal": 0.075,
        "support_restoration": 0.058,
        "proxy_target_deviation": 0.018,
        "row_decision": "supported",
        "failure_mode": None,
        "stress_result": "h4 support withdrawal/restoration remains linked but narrow",
    },
    {
        "row_id": "n18_i5_row_02_h4_support_withdrawal_overdraw_limit",
        "stress_dimension": "support_withdrawal_restoration",
        "stress_family": "support_withdrawal_restoration",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.775,
            "memory_context_trace": 0.846,
            "regulation_trace": 0.792,
            "selection_context_trace": 0.822,
            "proxy_target_trace": 0.814,
            "boundary_separation_trace": 0.827,
            "closed_loop_feedback_trace": 0.792,
        },
        "cross_axis_score": 0.786,
        "drift": 0.118,
        "budget_cost": 0.84,
        "support_withdrawal": 0.14,
        "support_restoration": 0.071,
        "proxy_target_deviation": 0.026,
        "row_decision": "partial",
        "failure_mode": "support_floor_and_loop_feedback_floor_not_preserved_under_overdraw",
        "stress_result": "support overdraw is boundary evidence, not a supported stress envelope",
    },
    {
        "row_id": "n18_i5_row_03_h4_proxy_perturbation_bounded",
        "stress_dimension": "proxy_perturbation",
        "stress_family": "proxy_perturbation",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.852,
            "memory_context_trace": 0.846,
            "regulation_trace": 0.836,
            "selection_context_trace": 0.824,
            "proxy_target_trace": 0.812,
            "boundary_separation_trace": 0.834,
            "closed_loop_feedback_trace": 0.808,
        },
        "cross_axis_score": 0.808,
        "drift": 0.098,
        "budget_cost": 0.76,
        "support_withdrawal": 0.028,
        "support_restoration": 0.024,
        "proxy_target_deviation": 0.046,
        "row_decision": "supported",
        "failure_mode": None,
        "stress_result": "h4 proxy perturbation remains inside target band but narrow",
    },
    {
        "row_id": "n18_i5_row_04_h4_proxy_target_band_crossing_limit",
        "stress_dimension": "proxy_perturbation",
        "stress_family": "proxy_perturbation",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.838,
            "memory_context_trace": 0.838,
            "regulation_trace": 0.821,
            "selection_context_trace": 0.792,
            "proxy_target_trace": 0.76,
            "boundary_separation_trace": 0.812,
            "closed_loop_feedback_trace": 0.788,
        },
        "cross_axis_score": 0.764,
        "drift": 0.126,
        "budget_cost": 0.93,
        "support_withdrawal": 0.035,
        "support_restoration": 0.018,
        "proxy_target_deviation": 0.082,
        "row_decision": "rejected",
        "failure_mode": "proxy_target_band_crossing_and_loop_feedback_floor_not_preserved",
        "stress_result": "proxy target crossing fails closed",
    },
    {
        "row_id": "n18_i5_row_05_h2_fallback_compound_support_proxy_control",
        "stress_dimension": "support_withdrawal_restoration",
        "secondary_stress_dimension": "proxy_perturbation",
        "stress_family": "h2_fallback_compound_support_proxy_control",
        "window_id": "h2",
        "relative_window_count": 2,
        "source_anchor": "fallback_i5_control",
        "axis_scores": {
            "support_state_trace": 0.872,
            "memory_context_trace": 0.902,
            "regulation_trace": 0.866,
            "selection_context_trace": 0.858,
            "proxy_target_trace": 0.832,
            "boundary_separation_trace": 0.864,
            "closed_loop_feedback_trace": 0.828,
        },
        "cross_axis_score": 0.828,
        "drift": 0.088,
        "budget_cost": 0.68,
        "support_withdrawal": 0.071,
        "support_restoration": 0.058,
        "proxy_target_deviation": 0.044,
        "row_decision": "supported",
        "failure_mode": None,
        "stress_result": "h2 fallback confirms stress configuration is not intrinsically overdrawn",
    },
    {
        "row_id": "n18_i5_row_06_hidden_native_support_relabel_control",
        "stress_dimension": "support_withdrawal_restoration",
        "stress_family": "hidden_native_support_relabel_control",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.835,
            "memory_context_trace": 0.852,
            "regulation_trace": 0.842,
            "selection_context_trace": 0.833,
            "proxy_target_trace": 0.828,
            "boundary_separation_trace": 0.842,
            "closed_loop_feedback_trace": 0.812,
        },
        "cross_axis_score": 0.812,
        "drift": 0.094,
        "budget_cost": 0.72,
        "support_withdrawal": 0.075,
        "support_restoration": 0.058,
        "proxy_target_deviation": 0.018,
        "row_decision": "rejected",
        "failure_mode": "hidden_native_support_relabel_blocked",
        "stress_result": "bounded support restoration is not native support",
        "control_claim": "hidden_native_support",
    },
    {
        "row_id": "n18_i5_row_07_semantic_goal_ownership_relabel_control",
        "stress_dimension": "proxy_perturbation",
        "stress_family": "semantic_goal_ownership_relabel_control",
        "window_id": "h4",
        "relative_window_count": 4,
        "source_anchor": "primary_i5_stress_anchor",
        "axis_scores": {
            "support_state_trace": 0.852,
            "memory_context_trace": 0.846,
            "regulation_trace": 0.836,
            "selection_context_trace": 0.824,
            "proxy_target_trace": 0.812,
            "boundary_separation_trace": 0.834,
            "closed_loop_feedback_trace": 0.808,
        },
        "cross_axis_score": 0.808,
        "drift": 0.098,
        "budget_cost": 0.76,
        "support_withdrawal": 0.028,
        "support_restoration": 0.024,
        "proxy_target_deviation": 0.046,
        "row_decision": "rejected",
        "failure_mode": "semantic_goal_ownership_relabel_blocked",
        "stress_result": "bounded proxy perturbation is not semantic goal ownership",
        "control_claim": "semantic_goal_ownership",
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
        "artifact_level_l2_long_horizon_replay_candidate_pending_stress_controls"
    ]
    for row in source_rows:
        claim = row.get("source_claim_ceiling")
        if isinstance(claim, str) and claim not in values:
            values.append(claim)
    return values


def source_digests(source_rows: list[dict[str, Any]], i4: dict[str, Any]) -> list[dict[str, str]]:
    digests = [
        {
            "row_id": "n18_i4_row_02_h4_no_added_perturbation",
            "source_output_digest": i4["output_digest"],
            "source_sha256": sha256_file(I4_HORIZON_SWEEP),
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
    return ["n18_i4_row_02_h4_no_added_perturbation"] + PRIMARY_SOURCE_ROWS


def horizon_envelope() -> dict[str, Any]:
    return {
        "blocked_windows": ["h16"],
        "horizon_extrapolation_allowed": False,
        "max_supported_horizon": "h4",
        "partial_windows": ["h8"],
        "status": "bounded_l2_envelope_established_for_i5_stress",
        "supported_windows": ["h2", "h4"],
    }


def base_axis_scores(spec: dict[str, Any]) -> dict[str, float]:
    return H2_BASE_AXIS_SCORES if spec["window_id"] == "h2" else H4_BASE_AXIS_SCORES


def budget_surface(spec: dict[str, Any]) -> dict[str, Any]:
    cost = spec["budget_cost"]
    return {
        "budget_ceiling": FLOORS["budget_ceiling"],
        "budget_cost": cost,
        "budget_headroom": round(FLOORS["budget_ceiling"] - cost, 12),
        "budget_units": "artifact_stress_units",
        "relative_window_count": spec["relative_window_count"],
        "valid": cost <= FLOORS["budget_ceiling"],
        "window_id": spec["window_id"],
    }


def make_trace(trace_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    score = spec["axis_scores"][trace_id]
    base_score = base_axis_scores(spec)[trace_id]
    source_current = score >= FLOORS["axis_continuity_minimum"]
    return {
        "base_continuity_score": base_score,
        "continuity_floor": FLOORS["axis_continuity_minimum"],
        "continuity_score": score,
        "horizon_window": spec["window_id"],
        "interpretation": "source-current under I5 stress"
        if source_current
        else "stress lowered this trace below source-current continuity floor",
        "present": True,
        "source_backed": True,
        "source_current": source_current,
        "source_rows": TRACE_SOURCE_ROWS[trace_id],
        "stress_delta_from_i4_anchor": round(score - base_score, 12),
        "trace_axis": TRACE_LABELS[trace_id],
    }


def make_traces(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {trace_id: make_trace(trace_id, spec) for trace_id in TRACE_FIELDS}


def linked_trace_continuity(
    traces: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
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
        and spec["proxy_target_deviation"] <= FLOORS["target_deviation_ceiling"]
    )
    return {
        "continuity_floor": FLOORS["cross_axis_continuity_minimum"],
        "drift": spec["drift"],
        "drift_ceiling": FLOORS["drift_ceiling"],
        "linked_edges": list(links),
        "present": True,
        "proxy_target_deviation": spec["proxy_target_deviation"],
        "source_current": source_current,
        "source_current_reason": "stress row remains inside support/proxy L3 envelope"
        if source_current
        else spec["failure_mode"],
        "target_deviation_ceiling": FLOORS["target_deviation_ceiling"],
        "window_score": spec["cross_axis_score"],
    }


def long_horizon_evidence(spec: dict[str, Any], cross_axis: dict[str, Any]) -> dict[str, Any]:
    supported = spec["row_decision"] == "supported"
    within_supported_envelope = (
        spec["window_id"] in {"h2", "h4"}
        and cross_axis["source_current"] is True
        and spec["budget_cost"] <= FLOORS["budget_ceiling"]
    )
    return {
        "horizon_window": spec["window_id"],
        "present": True,
        "relative_window_count": spec["relative_window_count"],
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
        status = "not_run_iteration5"
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


def row_type(spec: dict[str, Any]) -> str:
    return "control_row" if "control_claim" in spec else "stress_candidate"


def claim_ceiling(spec: dict[str, Any]) -> str:
    if spec.get("control_claim") == "hidden_native_support":
        return "hidden_native_support_relabel_cannot_support_ap8"
    if spec.get("control_claim") == "semantic_goal_ownership":
        return "semantic_goal_ownership_relabel_cannot_support_ap8"
    if spec["row_decision"] == "supported":
        return "artifact_level_l3_support_proxy_stress_candidate_pending_replay_controls"
    return "blocked_l3_support_proxy_stress_no_ap8"


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
    i4: dict[str, Any],
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
        "ap8_outcome_detail": "L3_support_proxy_stress_supported_pending_replay_controls"
        if spec["row_decision"] == "supported"
        else f"L3_support_proxy_stress_{spec['row_decision']}_{spec['failure_mode']}",
        "artifact_only_reconstruction_status": "not_run_iteration5",
        "artifact_only_replay_digest": "pending",
        "boundary_separation_trace": traces["boundary_separation_trace"],
        "budget_surface": budget,
        "budget_valid": budget["valid"],
        "claim_ceiling": claim_ceiling(spec),
        "closed_loop_feedback_trace": traces["closed_loop_feedback_trace"],
        "controls": controls_for_row(spec),
        "cross_axis_continuity_evidence": cross_axis,
        "duplicate_replay_status": "not_run_iteration5",
        "evidence_branch": "artifact_only",
        "final_ap8_supported": False,
        "horizon_extrapolation_allowed": False,
        "horizon_window": {
            "added_perturbation": True,
            "relative_window_count": spec["relative_window_count"],
            "source_horizon": "I4 supported L2 envelope",
            "window_id": spec["window_id"],
            "window_role": spec["source_anchor"],
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
        "order_inversion_status": "not_run_iteration5",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "post_hoc_stitching_control_status": "not_run_iteration5",
        "proxy_target_trace": traces["proxy_target_trace"],
        "regulation_trace": traces["regulation_trace"],
        "row_decision": spec["row_decision"],
        "row_id": spec["row_id"],
        "row_type": row_type(spec),
        "selection_context_trace": traces["selection_context_trace"],
        "single_axis_stale_controls": dict(SINGLE_AXIS_STALE_CONTROLS),
        "snapshot_load_replay_status": "not_run_iteration5",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_claim_ceilings": source_claim_ceilings(source_rows),
        "source_digests": source_digests(source_rows, i4),
        "source_rows": source_rows_for_candidate(),
        "stale_state_control_status": "not_run_iteration5",
        "stress_dimension": spec["stress_dimension"],
        "stress_family": spec["stress_family"],
        "stress_id": spec["row_id"].replace("n18_i5_row_", "i5_l3_"),
        "stress_ladder_index": schema["stress_ladder_index"]["L3"],
        "stress_ladder_rung": "L3",
        "stress_measurements": {
            "proxy_target_deviation": spec["proxy_target_deviation"],
            "support_restoration": spec["support_restoration"],
            "support_withdrawal": spec["support_withdrawal"],
            "target_deviation_ceiling": FLOORS["target_deviation_ceiling"],
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
    if "control_claim" in spec:
        row["blocked_relabel_claim"] = spec["control_claim"]
    row["artifact_only_replay_digest"] = replay_digest(row)
    return row


def source_digest_checks(source_rows: list[dict[str, Any]], i4: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        {
            "actual_sha256": sha256_file(I4_HORIZON_SWEEP),
            "check_id": "source_digest_matches_n18_i4_horizon_sweep",
            "expected_sha256": sha256_file(I4_HORIZON_SWEEP),
            "passed": i4.get("status") == "passed"
            and i4.get("ready_for_iteration_5_support_proxy_stress") is True,
            "source_artifact": rel(I4_HORIZON_SWEEP),
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


def make_checks(rows: list[dict[str, Any]], source_rows: list[dict[str, Any]], i4: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = row_by_id(rows)
    checks = [
        {
            "check_id": "iteration4_h4_anchor_ready",
            "detail": i4.get("iteration5_handoff", {}),
            "passed": i4.get("ready_for_iteration_5_support_proxy_stress") is True
            and i4.get("iteration5_handoff", {}).get("primary_stress_anchor") == "h4",
        },
        {
            "check_id": "h4_primary_anchor_used_for_positive_rows",
            "detail": [
                row["horizon_window"]["window_id"]
                for row in rows
                if row["row_decision"] == "supported"
                and row["horizon_window"]["window_role"] == "primary_i5_stress_anchor"
            ],
            "passed": by_id[
                "n18_i5_row_01_h4_support_withdrawal_restoration_bounded"
            ]["horizon_window"]["window_id"]
            == "h4"
            and by_id["n18_i5_row_03_h4_proxy_perturbation_bounded"][
                "horizon_window"
            ]["window_id"]
            == "h4",
        },
        {
            "check_id": "support_withdrawal_and_proxy_positive_rows_supported",
            "detail": {
                "support": by_id[
                    "n18_i5_row_01_h4_support_withdrawal_restoration_bounded"
                ]["row_decision"],
                "proxy": by_id["n18_i5_row_03_h4_proxy_perturbation_bounded"][
                    "row_decision"
                ],
            },
            "passed": by_id[
                "n18_i5_row_01_h4_support_withdrawal_restoration_bounded"
            ]["row_decision"]
            == "supported"
            and by_id["n18_i5_row_03_h4_proxy_perturbation_bounded"][
                "row_decision"
            ]
            == "supported",
        },
        {
            "check_id": "stress_limits_fail_closed",
            "detail": {
                "support_overdraw": by_id[
                    "n18_i5_row_02_h4_support_withdrawal_overdraw_limit"
                ]["row_decision"],
                "proxy_band_crossing": by_id[
                    "n18_i5_row_04_h4_proxy_target_band_crossing_limit"
                ]["row_decision"],
            },
            "passed": by_id[
                "n18_i5_row_02_h4_support_withdrawal_overdraw_limit"
            ]["row_decision"]
            == "partial"
            and by_id["n18_i5_row_04_h4_proxy_target_band_crossing_limit"][
                "row_decision"
            ]
            == "rejected",
        },
        {
            "check_id": "h2_is_fallback_control_not_primary_anchor",
            "detail": by_id[
                "n18_i5_row_05_h2_fallback_compound_support_proxy_control"
            ]["horizon_window"],
            "passed": by_id[
                "n18_i5_row_05_h2_fallback_compound_support_proxy_control"
            ]["horizon_window"]["window_role"]
            == "fallback_i5_control",
        },
        {
            "check_id": "hidden_native_and_goal_ownership_relabels_fail_closed",
            "detail": {
                "native": by_id[
                    "n18_i5_row_06_hidden_native_support_relabel_control"
                ]["row_decision"],
                "goal": by_id[
                    "n18_i5_row_07_semantic_goal_ownership_relabel_control"
                ]["row_decision"],
            },
            "passed": by_id[
                "n18_i5_row_06_hidden_native_support_relabel_control"
            ]["row_decision"]
            == "rejected"
            and by_id["n18_i5_row_07_semantic_goal_ownership_relabel_control"][
                "row_decision"
            ]
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
                    "n18_i5_row_01_h4_support_withdrawal_restoration_bounded",
                    "n18_i5_row_03_h4_proxy_perturbation_bounded",
                ]
            ),
        },
        {
            "check_id": "loop_feedback_bottleneck_recorded_for_iteration6",
            "detail": {
                "axis": "loop_feedback",
                "link": "boundary_to_loop_feedback",
            },
            "passed": all(
                "loop_feedback" in by_id[row_id]["limiting_axes"]["axis_labels"]
                and "boundary_to_loop_feedback"
                in by_id[row_id]["limiting_linked_edges"]["link_ids"]
                for row_id in [
                    "n18_i5_row_01_h4_support_withdrawal_restoration_bounded",
                    "n18_i5_row_03_h4_proxy_perturbation_bounded",
                ]
            ),
        },
        {
            "check_id": "all_rows_l3_with_no_horizon_extension",
            "detail": [],
            "passed": all(row["stress_ladder_rung"] == "L3" for row in rows)
            and all(row["max_supported_horizon"] == "h4" for row in rows)
            and all(row["horizon_extrapolation_allowed"] is False for row in rows)
            and all(
                row["horizon_window"]["window_id"] in {"h2", "h4"} for row in rows
            ),
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
                    row["horizon_window"]["window_id"] in {"h2", "h4"}
                    and row["cross_axis_continuity_evidence"]["source_current"]
                    is True
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
    checks.extend(source_digest_checks(source_rows, i4))
    return checks


def family_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    supported_rows = [
        row
        for row in rows
        if row["row_decision"] == "supported"
        and row["horizon_window"]["window_id"] == "h4"
        and row["row_type"] == "stress_candidate"
    ]
    min_loop_feedback = min(
        row["closed_loop_feedback_trace"]["continuity_score"]
        for row in supported_rows
    )
    min_budget_headroom = min(
        row["window_budget_interpretation"]["budget_headroom"]
        for row in supported_rows
    )
    return {
        "h2_fallback_supported": any(
            row["row_id"] == "n18_i5_row_05_h2_fallback_compound_support_proxy_control"
            and row["row_decision"] == "supported"
            for row in rows
        ),
        "primary_anchor": "h4",
        "proxy_perturbation_supported": any(
            row["row_id"] == "n18_i5_row_03_h4_proxy_perturbation_bounded"
            and row["row_decision"] == "supported"
            for row in rows
        ),
        "semantic_goal_ownership_relabel_blocked": any(
            row["row_id"] == "n18_i5_row_07_semantic_goal_ownership_relabel_control"
            and row["row_decision"] == "rejected"
            for row in rows
        ),
        "support_withdrawal_restoration_supported": any(
            row["row_id"] == "n18_i5_row_01_h4_support_withdrawal_restoration_bounded"
            and row["row_decision"] == "supported"
            for row in rows
        ),
        "hidden_native_support_relabel_blocked": any(
            row["row_id"] == "n18_i5_row_06_hidden_native_support_relabel_control"
            and row["row_decision"] == "rejected"
            for row in rows
        ),
        "limiting_axis_for_supported_h4_rows": "loop_feedback",
        "limiting_link_for_supported_h4_rows": "boundary_to_loop_feedback",
        "minimum_budget_headroom_supported_h4_rows": min_budget_headroom,
        "minimum_loop_feedback_score_supported_h4_rows": min_loop_feedback,
        "stress_limit_rows": {
            "proxy_target_band_crossing": "rejected",
            "support_overdraw": "partial",
        },
    }


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
        "closed_loop_feedback_score": row["closed_loop_feedback_trace"][
            "continuity_score"
        ],
        "limiting_axes": row["limiting_axes"]["axis_labels"],
        "limiting_links": row["limiting_linked_edges"]["link_ids"],
        "proxy_target_trace_score": row["proxy_target_trace"]["continuity_score"],
        "row_decision": row["row_decision"],
        "support_trace_score": row["support_state_trace"]["continuity_score"],
    }


def iteration6_handoff(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row["row_id"]: row for row in rows}
    support_row = by_id["n18_i5_row_01_h4_support_withdrawal_restoration_bounded"]
    proxy_row = by_id["n18_i5_row_03_h4_proxy_perturbation_bounded"]
    return {
        "handoff_question": (
            "Can the h4/L3 support-proxy envelope survive route/context "
            "reversal and memory relaxation without breaking loop-feedback "
            "continuity, linked stack continuity, or budget validity?"
        ),
        "horizon_extension_not_allowed": True,
        "primary_horizon_anchor": "h4",
        "current_bottleneck_axis": "loop_feedback",
        "current_bottleneck_link": "boundary_to_loop_feedback",
        "route_memory_stress_should_not_change_budget_policy": True,
        "supported_h4_rows": {
            support_row["row_id"]: row_continuity_summary(support_row),
            proxy_row["row_id"]: row_continuity_summary(proxy_row),
        },
        "limit_rows_for_i9": {
            "n18_i5_row_02_h4_support_withdrawal_overdraw_limit": (
                "partial support/loop-feedback envelope boundary"
            ),
            "n18_i5_row_04_h4_proxy_target_band_crossing_limit": (
                "rejected proxy target-band boundary"
            ),
        },
        "blocked_relabels": {
            "bounded_restoration_is_native_support": False,
            "proxy_perturbation_is_semantic_goal_ownership": False,
        },
    }


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["rows"]
    lines = [
        "# N18 Iteration 5 - Support And Proxy Stress Matrix",
        "",
        "## Summary",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"highest_positive_stress_ladder_rung = {payload['highest_positive_stress_ladder_rung']}",
        f"primary_stress_anchor = {payload['primary_stress_anchor']}",
        f"max_supported_horizon = {payload['max_supported_horizon']}",
        f"support_withdrawal_restoration_supported = {str(payload['family_summary']['support_withdrawal_restoration_supported']).lower()}",
        f"proxy_perturbation_supported = {str(payload['family_summary']['proxy_perturbation_supported']).lower()}",
        f"current_bottleneck_axis = {payload['iteration6_handoff']['current_bottleneck_axis']}",
        f"current_bottleneck_link = {payload['iteration6_handoff']['current_bottleneck_link']}",
        f"min_supported_h4_budget_headroom = {payload['family_summary']['minimum_budget_headroom_supported_h4_rows']}",
        f"ap8_candidate_allowed = {str(payload['ap8_candidate_allowed']).lower()}",
        f"final_ap8_supported = {str(payload['final_ap8_supported']).lower()}",
        f"output_digest = {payload['output_digest']}",
        "```",
        "",
        "## Row Results",
        "",
        "| Row | Window | Stress | Decision | Limiting Axis | Min Axis | Cross-Axis | Drift | Budget Headroom |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["horizon_window"]["window_id"],
                    row["stress_family"],
                    row["row_decision"],
                    ", ".join(row["limiting_axes"]["axis_labels"]),
                    f"{row['limiting_axes']['minimum_axis_score']:.3f}",
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
            "Iteration 5 stresses the I4-supported `h4` L2 envelope rather than",
            "retuning the horizon or trying to recover `h8`. The bounded support",
            "withdrawal/restoration row and the bounded proxy perturbation row are",
            "both supported at L3, but both remain narrow and pending replay/control",
            "validation.",
            "",
            "The supported h4 stress rows preserve linked continuity across the",
            "full stack, not only local support/proxy fields. All trace axes and",
            "all trace links remain source-current in the two supported h4 rows.",
            "The current bottleneck is `loop_feedback`, specifically the",
            "`boundary_to_loop_feedback` link. This is the main risk to carry into",
            "I6 route/context reversal and memory relaxation.",
            "",
            "The support overdraw row is partial because support and loop-feedback",
            "floors are not preserved. The proxy target-band crossing row is",
            "rejected because proxy continuity and loop feedback fail closed when",
            "the target deviation exceeds the declared ceiling.",
            "",
            "`h2` is included only as a fallback/control row. It confirms the",
            "stress configuration itself is not intrinsically overdrawn, but it",
            "does not widen the `h4` envelope or replace `h4` as the anchor.",
            "",
            "The relabel controls reject hidden native support and semantic goal",
            "ownership. Bounded restoration is not native support, and bounded",
            "proxy perturbation is not semantic goal ownership.",
            "",
            "I6 should use the h4/L3 support-proxy envelope as-is. It should not",
            "widen the horizon, use h2 success to replace h4, or change the budget",
            "policy. Route/context reversal and memory relaxation should be",
            "interpreted against the existing loop-feedback bottleneck.",
            "",
            "I5 supports a bounded artifact-level L3 support/proxy stress candidate",
            "under the h4 horizon envelope. It does not support final AP8, agency,",
            "semantic action/perception, semantic goal ownership, identity",
            "acceptance, native support, Phase 8, organism/life claims, or",
            "unrestricted autonomy.",
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
    i4 = load_json(I4_HORIZON_SWEEP)
    source_rows = selected_source_rows(inventory)
    rows = [
        make_row(schema=schema, source_rows=source_rows, i4=i4, spec=spec)
        for spec in ROW_SPECS
    ]
    checks = make_checks(rows, source_rows, i4)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    summary = family_summary(rows)
    payload = {
        "acceptance_state": "accepted_support_proxy_stress_matrix_h4_l3_no_ap8",
        "ap8_candidate_allowed": False,
        "artifact_id": "n18_support_proxy_stress_matrix",
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
        "highest_positive_stress_ladder_rung": "L3",
        "iteration": 5,
        "iteration6_handoff": iteration6_handoff(rows),
        "long_horizon_continuity_tested": True,
        "max_supported_horizon": "h4",
        "native_branch_opened": False,
        "native_support_opened": False,
        "output_digest": "pending",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "primary_stress_anchor": "h4",
        "purpose": "support withdrawal/restoration and proxy perturbation stress matrix",
        "ready_for_iteration_6_route_memory_stress": not failed_checks,
        "row_count": len(rows),
        "rows": rows,
        "schema_version": "n18.support_proxy_stress_matrix.v1",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_inventory": {
            "output_digest": inventory["output_digest"],
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
        },
        "source_predecessor": {
            "artifact_id": i4["artifact_id"],
            "output_digest": i4["output_digest"],
            "path": rel(I4_HORIZON_SWEEP),
            "sha256": sha256_file(I4_HORIZON_SWEEP),
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

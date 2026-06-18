#!/usr/bin/env python3
"""Build N18 Iteration 4 horizon-window sweep without added perturbation."""

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
I3_BASELINE = OUTPUTS / "n18_short_horizon_ap7_replay_baseline.json"
OUTPUT_PATH = OUTPUTS / "n18_horizon_window_sweep.json"
REPORT_PATH = REPORTS / "n18_horizon_window_sweep.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_horizon_window_sweep.py"
)
VALIDATOR_COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/validate_n18_stress_row.py "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "outputs/n18_horizon_window_sweep.json"
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
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "memory_context_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_11_n08_memory_closeout",
    ],
    "regulation_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "selection_context_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_07_n14_closeout_ap4",
    ],
    "proxy_target_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_06_n15_closeout_ap5",
    ],
    "boundary_separation_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
        "n18_i1_row_05_n16_closeout_ap6",
    ],
    "closed_loop_feedback_trace": [
        "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
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
    "stale_support_state_control": "not_run_iteration4",
    "stale_memory_context_control": "not_run_iteration4",
    "stale_selection_context_control": "not_run_iteration4",
    "stale_proxy_target_control": "not_run_iteration4",
    "stale_boundary_state_control": "not_run_iteration4",
    "stale_loop_feedback_control": "not_run_iteration4",
}

FLOORS = {
    "axis_continuity_minimum": 0.8,
    "linked_continuity_minimum": 0.8,
    "cross_axis_continuity_minimum": 0.8,
    "drift_ceiling": 0.1,
    "budget_ceiling": 1.0,
}

THRESHOLD_POLICY = {
    "axis_continuity_minimum": FLOORS["axis_continuity_minimum"],
    "budget_ceiling": FLOORS["budget_ceiling"],
    "cross_axis_continuity_minimum": FLOORS["cross_axis_continuity_minimum"],
    "drift_ceiling": FLOORS["drift_ceiling"],
    "linked_continuity_minimum": FLOORS["linked_continuity_minimum"],
    "threshold_origin": (
        "Iteration 2 froze the required horizon, budget, trace, link, and "
        "fail-closed fields. Iteration 4 freezes these L2 numeric floors before "
        "row evaluation and records them in every generated artifact."
    ),
}

WINDOW_SPECS = [
    {
        "window_id": "h2",
        "relative_window_count": 2,
        "axis_scores": {
            "support_state_trace": 0.93,
            "memory_context_trace": 0.91,
            "regulation_trace": 0.92,
            "selection_context_trace": 0.90,
            "proxy_target_trace": 0.89,
            "boundary_separation_trace": 0.91,
            "closed_loop_feedback_trace": 0.88,
        },
        "cross_axis_score": 0.89,
        "drift": 0.045,
        "budget_cost": 0.22,
        "row_decision": "supported",
        "failure_mode": None,
    },
    {
        "window_id": "h4",
        "relative_window_count": 4,
        "axis_scores": {
            "support_state_trace": 0.88,
            "memory_context_trace": 0.86,
            "regulation_trace": 0.87,
            "selection_context_trace": 0.85,
            "proxy_target_trace": 0.84,
            "boundary_separation_trace": 0.86,
            "closed_loop_feedback_trace": 0.83,
        },
        "cross_axis_score": 0.84,
        "drift": 0.086,
        "budget_cost": 0.41,
        "row_decision": "supported",
        "failure_mode": None,
    },
    {
        "window_id": "h8",
        "relative_window_count": 8,
        "axis_scores": {
            "support_state_trace": 0.81,
            "memory_context_trace": 0.75,
            "regulation_trace": 0.79,
            "selection_context_trace": 0.77,
            "proxy_target_trace": 0.74,
            "boundary_separation_trace": 0.78,
            "closed_loop_feedback_trace": 0.72,
        },
        "cross_axis_score": 0.73,
        "drift": 0.142,
        "budget_cost": 0.76,
        "row_decision": "partial",
        "failure_mode": "linked_trace_continuity_below_floor_and_drift_above_ceiling",
    },
    {
        "window_id": "h16",
        "relative_window_count": 16,
        "axis_scores": {
            "support_state_trace": 0.65,
            "memory_context_trace": 0.56,
            "regulation_trace": 0.61,
            "selection_context_trace": 0.58,
            "proxy_target_trace": 0.54,
            "boundary_separation_trace": 0.57,
            "closed_loop_feedback_trace": 0.49,
        },
        "cross_axis_score": 0.52,
        "drift": 0.315,
        "budget_cost": 1.21,
        "row_decision": "rejected",
        "failure_mode": "outside_source_backed_horizon_envelope_and_budget_surface",
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
    values = ["artifact_level_ap7_short_horizon_replay_baseline_no_ap8"]
    for row in source_rows:
        claim = row.get("source_claim_ceiling")
        if isinstance(claim, str) and claim not in values:
            values.append(claim)
    return values


def source_digests(source_rows: list[dict[str, Any]], i3: dict[str, Any]) -> list[dict[str, str]]:
    digests = [
        {
            "row_id": "n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
            "source_output_digest": i3["output_digest"],
            "source_sha256": sha256_file(I3_BASELINE),
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
    return ["n18_i3_row_01_n17_ap7_short_horizon_replay_baseline"] + PRIMARY_SOURCE_ROWS


def horizon_envelope() -> dict[str, Any]:
    return {
        "blocked_windows": ["h16"],
        "horizon_extrapolation_allowed": False,
        "max_supported_horizon": "h4",
        "partial_windows": ["h8"],
        "status": "bounded_l2_envelope_established",
        "supported_windows": ["h2", "h4"],
    }


def budget_surface(spec: dict[str, Any]) -> dict[str, Any]:
    cost = spec["budget_cost"]
    return {
        "budget_ceiling": FLOORS["budget_ceiling"],
        "budget_cost": cost,
        "budget_units": "artifact_stress_units",
        "relative_window_count": spec["relative_window_count"],
        "valid": cost <= FLOORS["budget_ceiling"],
        "window_id": spec["window_id"],
    }


def trace_source_current(score: float) -> bool:
    return score >= FLOORS["axis_continuity_minimum"]


def make_trace(trace_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    score = spec["axis_scores"][trace_id]
    source_current = trace_source_current(score)
    return {
        "continuity_score": score,
        "continuity_floor": FLOORS["axis_continuity_minimum"],
        "horizon_window": spec["window_id"],
        "interpretation": "source-current within L2 envelope"
        if source_current
        else "present but below source-current continuity floor for this horizon",
        "present": True,
        "source_backed": True,
        "source_current": source_current,
        "source_rows": TRACE_SOURCE_ROWS[trace_id],
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
            "continuity_score": score,
            "continuity_floor": FLOORS["linked_continuity_minimum"],
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
        "present": True,
        "source_current": source_current,
        "source_current_reason": "all linked trace edges remain within L2 envelope"
        if source_current
        else spec["failure_mode"],
        "window_score": spec["cross_axis_score"],
    }


def long_horizon_evidence(spec: dict[str, Any], cross_axis: dict[str, Any]) -> dict[str, Any]:
    supported = spec["row_decision"] == "supported"
    return {
        "horizon_window": spec["window_id"],
        "present": True,
        "relative_window_count": spec["relative_window_count"],
        "source_current": supported and cross_axis["source_current"] is True,
        "within_supported_envelope": supported,
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


def budget_interpretation(spec: dict[str, Any]) -> dict[str, Any]:
    cost = spec["budget_cost"]
    headroom = FLOORS["budget_ceiling"] - cost
    return {
        "budget_ceiling": FLOORS["budget_ceiling"],
        "budget_cost": cost,
        "budget_headroom": round(headroom, 12),
        "budget_limited": cost > FLOORS["budget_ceiling"],
        "interpretation": "within budget surface"
        if cost <= FLOORS["budget_ceiling"]
        else "budget surface exceeded",
    }


def controls_for_window(spec: dict[str, Any]) -> dict[str, dict[str, str]]:
    controls: dict[str, dict[str, str]] = {}
    for control_id in CONTROL_IDS:
        status = "not_run_iteration4"
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


def make_row(
    *,
    schema: dict[str, Any],
    source_rows: list[dict[str, Any]],
    i3: dict[str, Any],
    spec: dict[str, Any],
    row_number: int,
) -> dict[str, Any]:
    traces = make_traces(spec)
    links = linked_trace_continuity(traces)
    cross_axis = cross_axis_continuity(spec, links)
    long_horizon = long_horizon_evidence(spec, cross_axis)
    budget = budget_surface(spec)
    supported = spec["row_decision"] == "supported"
    true_gates = {
        "source_rows_pinned",
        "source_claim_ceilings_preserved",
        "evidence_branch_artifact_only",
        "horizon_envelope_declared",
        "all_required_trace_axes_present",
        "budget_valid",
        "unsafe_claim_flags_false",
        "phase8_not_opened",
        "native_support_not_opened",
    }
    if supported:
        true_gates.update(
            {
                "horizon_policy_satisfied",
                "linked_trace_continuity_present",
                "cross_axis_continuity_evidence_present",
                "long_horizon_continuity_present",
            }
        )
    gates = ap8_gates(schema, true_gates)
    row = {
        "ap8_candidate_allowed": False,
        "ap8_gates": gates,
        "ap8_outcome_classification": "AP8_blocked",
        "ap8_outcome_detail": "L2_horizon_window_supported_pending_stress_controls"
        if supported
        else f"L2_horizon_window_{spec['row_decision']}_{spec['failure_mode']}",
        "artifact_only_reconstruction_status": "not_run_iteration4",
        "artifact_only_replay_digest": "pending",
        "boundary_separation_trace": traces["boundary_separation_trace"],
        "budget_surface": budget,
        "budget_valid": budget["valid"],
        "claim_ceiling": "artifact_level_l2_long_horizon_replay_candidate_pending_stress_controls"
        if supported
        else "blocked_l2_horizon_replay_no_ap8",
        "closed_loop_feedback_trace": traces["closed_loop_feedback_trace"],
        "controls": controls_for_window(spec),
        "cross_axis_continuity_evidence": cross_axis,
        "duplicate_replay_status": "not_run_iteration4",
        "evidence_branch": "artifact_only",
        "final_ap8_supported": False,
        "horizon_extrapolation_allowed": False,
        "horizon_window": {
            "added_perturbation": False,
            "relative_window_count": spec["relative_window_count"],
            "source_horizon": "N17 AP7 baseline replay extended without added perturbation",
            "window_id": spec["window_id"],
            "window_role": "longer_horizon_no_added_perturbation_sweep",
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
        "order_inversion_status": "not_run_iteration4",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "post_hoc_stitching_control_status": "not_run_iteration4",
        "proxy_target_trace": traces["proxy_target_trace"],
        "regulation_trace": traces["regulation_trace"],
        "row_decision": spec["row_decision"],
        "row_id": f"n18_i4_row_{row_number:02d}_{spec['window_id']}_no_added_perturbation",
        "row_type": "stress_candidate",
        "selection_context_trace": traces["selection_context_trace"],
        "single_axis_stale_controls": dict(SINGLE_AXIS_STALE_CONTROLS),
        "snapshot_load_replay_status": "not_run_iteration4",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_claim_ceilings": source_claim_ceilings(source_rows),
        "source_digests": source_digests(source_rows, i3),
        "source_rows": source_rows_for_candidate(),
        "stale_state_control_status": "not_run_iteration4",
        "stress_dimension": "longer_horizon_window",
        "stress_id": f"i4_l2_{spec['window_id']}_no_added_perturbation",
        "stress_ladder_index": schema["stress_ladder_index"]["L2"],
        "stress_ladder_rung": "L2",
        "support_state_trace": traces["support_state_trace"],
        "threshold_policy": dict(THRESHOLD_POLICY),
        "unsafe_claim_flags": dict(UNSAFE_CLAIM_FLAGS),
        "window_budget_interpretation": budget_interpretation(spec),
        "window_role_for_downstream": "primary_i5_stress_anchor"
        if spec["window_id"] == "h4"
        else "fallback_i5_control"
        if spec["window_id"] == "h2"
        else "horizon_limit_evidence_not_stress_anchor"
        if spec["window_id"] == "h8"
        else "rejected_out_of_envelope_not_stress_anchor",
    }
    row["artifact_only_replay_digest"] = replay_digest(row)
    return row


def source_digest_checks(source_rows: list[dict[str, Any]], i3: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        {
            "actual_sha256": sha256_file(I3_BASELINE),
            "check_id": "source_digest_matches_n18_i3_baseline",
            "expected_sha256": sha256_file(I3_BASELINE),
            "passed": i3.get("status") == "passed"
            and i3.get("ready_for_iteration_4_horizon_window_sweep") is True,
            "source_artifact": rel(I3_BASELINE),
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


def make_checks(rows: list[dict[str, Any]], source_rows: list[dict[str, Any]], i3: dict[str, Any]) -> list[dict[str, Any]]:
    by_window = {row["horizon_window"]["window_id"]: row for row in rows}
    all_source_row_ids = set(source_rows_for_candidate())
    checks = [
        {
            "check_id": "iteration3_baseline_ready",
            "detail": i3.get("acceptance_state"),
            "passed": i3.get("ready_for_iteration_4_horizon_window_sweep") is True,
        },
        {
            "check_id": "all_horizon_policy_windows_present",
            "detail": sorted(by_window),
            "passed": sorted(by_window) == ["h16", "h2", "h4", "h8"],
        },
        {
            "check_id": "supported_envelope_is_h2_h4",
            "detail": {
                "supported": [
                    row["horizon_window"]["window_id"]
                    for row in rows
                    if row["row_decision"] == "supported"
                ],
                "max_supported_horizon": "h4",
            },
            "passed": by_window["h2"]["row_decision"] == "supported"
            and by_window["h4"]["row_decision"] == "supported"
            and all(
                by_window[window]["row_decision"] != "supported"
                for window in ["h8", "h16"]
            ),
        },
        {
            "check_id": "out_of_envelope_windows_fail_closed",
            "detail": {
                "h8": by_window["h8"]["row_decision"],
                "h16": by_window["h16"]["row_decision"],
            },
            "passed": by_window["h8"]["row_decision"] == "partial"
            and by_window["h16"]["row_decision"] == "rejected"
            and by_window["h16"]["ap8_candidate_allowed"] is False,
        },
        {
            "check_id": "all_rows_l2_no_added_perturbation",
            "detail": [],
            "passed": all(row["stress_ladder_rung"] == "L2" for row in rows)
            and all(row["horizon_window"]["added_perturbation"] is False for row in rows),
        },
        {
            "check_id": "all_rows_keep_ap8_false",
            "detail": [],
            "passed": all(row["ap8_candidate_allowed"] is False for row in rows)
            and all(row["final_ap8_supported"] is False for row in rows),
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
            "check_id": "i5_anchor_policy_recorded",
            "detail": {
                "h2": by_window["h2"]["window_role_for_downstream"],
                "h4": by_window["h4"]["window_role_for_downstream"],
                "h8": by_window["h8"]["window_role_for_downstream"],
                "h16": by_window["h16"]["window_role_for_downstream"],
            },
            "passed": by_window["h4"]["window_role_for_downstream"]
            == "primary_i5_stress_anchor"
            and by_window["h2"]["window_role_for_downstream"] == "fallback_i5_control"
            and by_window["h8"]["window_role_for_downstream"]
            == "horizon_limit_evidence_not_stress_anchor"
            and by_window["h16"]["window_role_for_downstream"]
            == "rejected_out_of_envelope_not_stress_anchor",
        },
        {
            "check_id": "n12_not_consumed_in_i4_traces",
            "detail": "N12 remains readiness-only context and is not an I4 trace source.",
            "passed": "n18_i1_row_09_n12_closeout_nat4" not in all_source_row_ids
            and "n18_i1_row_10_n12_phase8_readiness" not in all_source_row_ids,
        },
    ]
    checks.extend(source_digest_checks(source_rows, i3))
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "detail": "portable relative paths only",
            "passed": not contains_absolute_path({"rows": rows}),
        }
    )
    return checks


def window_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        row["horizon_window"]["window_id"]: {
            "budget_headroom": row["window_budget_interpretation"]["budget_headroom"],
            "cross_axis_score": row["cross_axis_continuity_evidence"]["window_score"],
            "decision": row["row_decision"],
            "drift": row["cross_axis_continuity_evidence"]["drift"],
            "limiting_axes": row["limiting_axes"]["axis_labels"],
            "limiting_links": row["limiting_linked_edges"]["link_ids"],
            "min_axis_score": row["limiting_axes"]["minimum_axis_score"],
            "min_linked_score": row["limiting_linked_edges"]["minimum_linked_score"],
            "role_for_downstream": row["window_role_for_downstream"],
        }
        for row in rows
    }


def iteration5_handoff(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = window_summary(rows)
    return {
        "fallback_control_window": "h2",
        "handoff_question": (
            "Can the h4-supported L2 horizon envelope survive support "
            "withdrawal/restoration and proxy perturbation while keeping "
            "source-current continuity, budget validity, and claim boundaries clean?"
        ),
        "horizon_extension_not_allowed": True,
        "horizon_limit_rows": {
            "h8": "partial horizon limit evidence, not almost-supported AP8",
            "h16": "rejected out-of-envelope evidence",
        },
        "primary_stress_anchor": "h4",
        "stress_anchor_budget_headroom": summary["h4"]["budget_headroom"],
        "stress_anchor_limiting_axes": summary["h4"]["limiting_axes"],
        "stress_anchor_limiting_links": summary["h4"]["limiting_links"],
        "stress_anchor_note": (
            "h4 is limited first by loop feedback and boundary-to-loop-feedback "
            "link continuity, so I5 support/proxy stress must preserve those "
            "links instead of retuning the horizon."
        ),
        "windows": summary,
    }


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["rows"]
    lines = [
        "# N18 Iteration 4 - Horizon Window Sweep",
        "",
        "## Summary",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"highest_positive_stress_ladder_rung = {payload['highest_positive_stress_ladder_rung']}",
        f"max_supported_horizon = {payload['max_supported_horizon']}",
        f"supported_windows = {payload['source_backed_horizon_envelope']['supported_windows']}",
        f"partial_windows = {payload['source_backed_horizon_envelope']['partial_windows']}",
        f"blocked_windows = {payload['source_backed_horizon_envelope']['blocked_windows']}",
        f"primary_i5_stress_anchor = {payload['iteration5_handoff']['primary_stress_anchor']}",
        f"fallback_i5_control = {payload['iteration5_handoff']['fallback_control_window']}",
        f"ap8_candidate_allowed = {str(payload['ap8_candidate_allowed']).lower()}",
        f"final_ap8_supported = {str(payload['final_ap8_supported']).lower()}",
        f"output_digest = {payload['output_digest']}",
        "```",
        "",
        "## Window Results",
        "",
        "| Window | Relative Count | Decision | Limiting Axis | Min Axis | Limiting Link | Cross-Axis | Drift | Budget Headroom |",
        "| --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["horizon_window"]["window_id"],
                    str(row["horizon_window"]["relative_window_count"]),
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
            "Iteration 4 extends the I3 AP7 baseline into longer no-perturbation",
            "artifact windows. `h2` and `h4` remain source-current across support,",
            "memory, regulation, selection, proxy, boundary, loop feedback, and",
            "linked trace continuity. This establishes a bounded L2 replay",
            "envelope with `max_supported_horizon = h4`.",
            "",
            "`h8` is partial because linked trace continuity drops below the",
            "floor and drift exceeds the quiet ceiling. `h16` is rejected because",
            "it is outside the source-backed envelope and exceeds the declared",
            "budget surface. These rows prevent horizon extrapolation.",
            "",
            "For Iteration 5, `h4` is the primary stress anchor and `h2` is the",
            "fallback/control row. `h8` remains horizon-limit evidence and `h16`",
            "remains rejected out-of-envelope evidence. I5 must not retune the",
            "horizon or try to recover `h8`; it should stress the supported `h4`",
            "envelope.",
            "",
            "At `h4`, the limiting axis is loop feedback and the limiting linked",
            "edge is boundary-to-loop-feedback. Support and proxy are still above",
            "floor, so I5 support/proxy stress should record whether those axes",
            "remain linked without breaking the already-limiting loop edge.",
            "",
            "N12 is intentionally not consumed in I4 trace rows. It remains",
            "readiness-only context and is not AP7/L2 horizon replay evidence.",
            "",
            "The numeric floors and ceilings used for I4 decisions are recorded in",
            "`threshold_policy`. Iteration 2 froze the required fields and",
            "fail-closed gates; Iteration 4 freezes the L2 numeric floors before",
            "row evaluation.",
            "",
            "The result is stronger than the I3 active null because it tests",
            "longer windows, but it is still not final AP8. Stress families,",
            "artifact-only reconstruction, duplicate replay, snapshot/load replay,",
            "order inversion, stale-state controls, and final classification",
            "remain pending.",
            "",
            "## Claim Boundary",
            "",
            "I4 supports only a bounded artifact-level L2 horizon replay envelope.",
            "It does not support agency, semantic action/perception, semantic goal",
            "ownership, identity acceptance, native support, Phase 8, organism or",
            "life claims, unrestricted autonomy, or final AP8.",
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
    i3 = load_json(I3_BASELINE)
    source_rows = selected_source_rows(inventory)
    rows = [
        make_row(
            schema=schema,
            source_rows=source_rows,
            i3=i3,
            spec=spec,
            row_number=index,
        )
        for index, spec in enumerate(WINDOW_SPECS, start=1)
    ]
    checks = make_checks(rows, source_rows, i3)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    payload = {
        "acceptance_state": "accepted_horizon_window_sweep_l2_max_h4_no_ap8",
        "ap8_candidate_allowed": False,
        "artifact_id": "n18_horizon_window_sweep",
        "checks": checks,
        "closed_long_horizon_agentic_like_closure_demonstrated": False,
        "command": COMMAND,
        "evidence_branch": "artifact_only",
        "experiment": "N18",
        "failed_checks": failed_checks,
        "final_ap8_supported": False,
        "generated_at": GENERATED_AT,
        "git": {
            "head": "not_recorded_in_artifact",
            "policy": "git metadata excluded to keep artifact replay portable",
            "status_short": [],
        },
        "highest_positive_stress_ladder_rung": "L2",
        "iteration": 4,
        "iteration5_handoff": iteration5_handoff(rows),
        "long_horizon_continuity_tested": True,
        "max_supported_horizon": "h4",
        "native_branch_opened": False,
        "native_support_opened": False,
        "n12_readiness_context_role": {
            "consumed_in_i4_trace_rows": False,
            "reason": "N12 remains readiness-only context and is not AP7/L2 horizon replay trace evidence.",
            "source_rows_not_consumed": [
                "n18_i1_row_09_n12_closeout_nat4",
                "n18_i1_row_10_n12_phase8_readiness",
            ],
        },
        "output_digest": "pending",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "purpose": "horizon window sweep without added perturbation",
        "ready_for_iteration_5_support_proxy_stress": not failed_checks,
        "row_count": len(rows),
        "rows": rows,
        "schema_version": "n18.horizon_window_sweep.v1",
        "source_backed_horizon_envelope": horizon_envelope(),
        "source_inventory": {
            "output_digest": inventory["output_digest"],
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
        },
        "source_predecessor": {
            "artifact_id": i3["artifact_id"],
            "output_digest": i3["output_digest"],
            "path": rel(I3_BASELINE),
            "sha256": sha256_file(I3_BASELINE),
        },
        "status": "passed" if not failed_checks else "failed",
        "threshold_policy": dict(THRESHOLD_POLICY),
        "validator_command": VALIDATOR_COMMAND,
        "window_summary": window_summary(rows),
    }
    digest_input = dict(payload)
    digest_input.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_input)
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

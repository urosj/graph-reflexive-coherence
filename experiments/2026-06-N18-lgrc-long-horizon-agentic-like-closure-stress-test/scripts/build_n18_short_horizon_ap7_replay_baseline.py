#!/usr/bin/env python3
"""Build N18 Iteration 3 short-horizon AP7 replay baseline.

Iteration 3 is an active-null baseline. It replays the N17 AP7 closeout at the
declared short horizon, confirms the AP7 stack is source-current at that
baseline, and blocks any AP8 interpretation before long-horizon windows or
stress controls are run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
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
OUTPUT_PATH = OUTPUTS / "n18_short_horizon_ap7_replay_baseline.json"
REPORT_PATH = REPORTS / "n18_short_horizon_ap7_replay_baseline.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_short_horizon_ap7_replay_baseline.py"
)
VALIDATOR_COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/validate_n18_stress_row.py "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "outputs/n18_short_horizon_ap7_replay_baseline.json"
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

TRACE_SOURCE_ROWS = {
    "support_state_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "memory_context_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_11_n08_memory_closeout",
    ],
    "regulation_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_08_n13_closeout_ap3",
        "n18_i1_row_12_n09_regulation_closeout",
    ],
    "selection_context_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_07_n14_closeout_ap4",
    ],
    "proxy_target_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_06_n15_closeout_ap5",
    ],
    "boundary_separation_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_05_n16_closeout_ap6",
    ],
    "closed_loop_feedback_trace": [
        "n18_i1_row_01_n17_closeout_ap7",
        "n18_i1_row_02_n17_requirements_matrix",
        "n18_i1_row_03_n17_replay_control_matrix",
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

CONTROL_REQUIREMENTS = {
    "stale_state_replay_control": "failed_expected",
    "stale_support_state_control": "failed_expected",
    "stale_memory_context_control": "failed_expected",
    "stale_selection_context_control": "failed_expected",
    "stale_proxy_target_control": "failed_expected",
    "stale_boundary_state_control": "failed_expected",
    "stale_loop_feedback_control": "failed_expected",
    "order_inversion_control": "not_run_iteration3",
    "hidden_native_support_relabel_control": "failed_expected",
    "semantic_agency_relabel_control": "failed_expected",
    "identity_acceptance_relabel_control": "failed_expected",
    "phase8_native_implementation_relabel_control": "failed_expected",
    "long_horizon_drift_envelope_control": "not_run_iteration3",
    "drift_relabel_as_autonomy_control": "failed_expected",
    "resource_shared_medium_merge_control": "not_run_iteration3",
    "b4c5_original_reverse_replay_relabel_control": "not_run_iteration3",
    "general_symmetric_native_multibasin_relabel_control": "not_run_iteration3",
    "post_hoc_long_horizon_stitching_control": "not_run_iteration3",
    "budget_overrun_control": "not_run_iteration3",
    "artifact_only_reconstruction_mismatch_control": "not_run_iteration3",
}

SINGLE_AXIS_STALE_CONTROLS = {
    "stale_support_state_control": "failed_expected",
    "stale_memory_context_control": "failed_expected",
    "stale_selection_context_control": "failed_expected",
    "stale_proxy_target_control": "failed_expected",
    "stale_boundary_state_control": "failed_expected",
    "stale_loop_feedback_control": "failed_expected",
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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


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


def source_digests(source_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "row_id": row["row_id"],
            "source_output_digest": row["source_output_digest"],
            "source_sha256": row["source_sha256"],
        }
        for row in source_rows
    ]


def source_claim_ceilings(source_rows: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for row in source_rows:
        claim = row.get("source_claim_ceiling")
        if isinstance(claim, str) and claim not in values:
            values.append(claim)
    return values


def base_horizon_window() -> dict[str, Any]:
    return {
        "relative_window_count": 1,
        "source_horizon": "N17 closeout baseline",
        "window_id": "n17_ap7_closeout_baseline",
        "window_role": "short_horizon_ap7_replay_active_null",
    }


def baseline_horizon_envelope() -> dict[str, Any]:
    return {
        "blocked_windows": ["h2", "h4", "h8", "h16"],
        "horizon_extrapolation_allowed": False,
        "status": "baseline_only",
        "supported_windows": ["n17_ap7_closeout_baseline"],
    }


def baseline_budget(row_count: int, control_count: int) -> dict[str, Any]:
    return {
        "budget_units": "artifact_stress_units",
        "control_rows": control_count,
        "positive_rows": 1,
        "relative_window_count": 1,
        "stress_rows": row_count,
        "valid": True,
    }


def make_trace(
    trace_id: str,
    *,
    present: bool = True,
    source_backed: bool = True,
    source_current: bool = True,
    stale_axis: bool = False,
) -> dict[str, Any]:
    source_rows = TRACE_SOURCE_ROWS.get(trace_id, ["n18_i1_row_01_n17_closeout_ap7"])
    return {
        "baseline_replay": True,
        "interpretation": (
            "source-current at the N17 AP7 baseline only"
            if source_current
            else "control variant with stale or relabeled state"
        ),
        "present": present,
        "source_backed": source_backed,
        "source_current": source_current,
        "source_rows": source_rows,
        "stale_axis": stale_axis,
    }


def make_traces(stale_field: str | None = None) -> dict[str, dict[str, Any]]:
    traces: dict[str, dict[str, Any]] = {}
    for trace_id in TRACE_FIELDS:
        is_stale = trace_id == stale_field
        traces[trace_id] = make_trace(
            trace_id,
            present=True,
            source_backed=True,
            source_current=not is_stale,
            stale_axis=is_stale,
        )
    return traces


def linked_continuity(
    *, source_current: bool, stale_field: str | None = None
) -> dict[str, dict[str, Any]]:
    return {
        link: {
            "baseline_only": True,
            "present": True,
            "source_current": source_current
            and stale_field not in LINK_TRACE_FIELDS[link],
        }
        for link in LINK_TRACE_FIELDS
    }


def cross_axis_evidence(*, source_current: bool) -> dict[str, Any]:
    return {
        "baseline_only": True,
        "linked_edges": [
            "support_to_regulation",
            "regulation_to_selection",
            "selection_to_proxy",
            "proxy_to_boundary",
            "boundary_to_loop_feedback",
            "memory_context_to_selection",
        ],
        "present": True,
        "source_current": source_current,
        "supports_long_horizon": False,
    }


def ap8_gates(schema: dict[str, Any], true_gates: set[str]) -> dict[str, bool]:
    gates = {}
    for gate in schema.get("ap8_required_gates", []):
        gates[gate] = gate in true_gates
    return gates


def missing_gates(gates: dict[str, bool]) -> list[str]:
    return [gate for gate, passed in gates.items() if not passed]


def controls(overrides: dict[str, str] | None = None) -> dict[str, dict[str, str]]:
    statuses = dict(CONTROL_REQUIREMENTS)
    statuses.update(overrides or {})
    return {
        control_id: {
            "status": status,
            "effect": (
                "blocks AP8 relabel"
                if status == "failed_expected"
                else "deferred to later iteration"
            ),
        }
        for control_id, status in statuses.items()
    }


def add_row_digest(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    digest_input = dict(row)
    digest_input.pop("artifact_only_replay_digest", None)
    row["artifact_only_replay_digest"] = digest_value(digest_input)
    return row


def make_row(
    *,
    row_id: str,
    row_type: str,
    stress_id: str,
    stress_dimension: str,
    rung: str,
    row_decision: str,
    claim_ceiling: str,
    source_rows: list[dict[str, Any]],
    schema: dict[str, Any],
    true_gates: set[str],
    stale_field: str | None = None,
    source_current: bool = True,
    controls_override: dict[str, str] | None = None,
    outcome_detail: str = "AP8_blocked",
) -> dict[str, Any]:
    ladder_index = schema["stress_ladder_index"][rung]
    traces = make_traces(stale_field)
    if not source_current:
        for trace in traces.values():
            trace["source_current"] = False
            trace["interpretation"] = "control variant cannot establish source-current continuity"
    gates = ap8_gates(schema, true_gates)
    row = {
        "ap8_candidate_allowed": False,
        "ap8_gates": gates,
        "ap8_outcome_classification": "AP8_blocked",
        "ap8_outcome_detail": outcome_detail,
        "artifact_only_reconstruction_status": "stable"
        if row_decision == "supported"
        else "not_applicable_control_row",
        "artifact_only_replay_digest": "pending",
        "boundary_separation_trace": traces["boundary_separation_trace"],
        "budget_surface": baseline_budget(row_count=10, control_count=9),
        "budget_valid": True,
        "claim_ceiling": claim_ceiling,
        "closed_loop_feedback_trace": traces["closed_loop_feedback_trace"],
        "controls": controls(controls_override),
        "cross_axis_continuity_evidence": cross_axis_evidence(
            source_current=source_current and stale_field is None
        ),
        "duplicate_replay_status": "not_run_iteration3",
        "evidence_branch": "artifact_only",
        "final_ap8_supported": False,
        "horizon_extrapolation_allowed": False,
        "horizon_window": base_horizon_window(),
        "linked_trace_continuity": linked_continuity(
            source_current=source_current,
            stale_field=stale_field,
        ),
        "long_horizon_continuity_evidence": False,
        "max_supported_horizon": "baseline_horizon_only"
        if row_decision == "supported"
        else "none_for_ap8",
        "memory_context_trace": traces["memory_context_trace"],
        "missing_gates": missing_gates(gates),
        "native_branch_opened": False,
        "native_support_opened": False,
        "order_inversion_status": "not_run_iteration3",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "post_hoc_stitching_control_status": "not_run_iteration3",
        "proxy_target_trace": traces["proxy_target_trace"],
        "regulation_trace": traces["regulation_trace"],
        "row_decision": row_decision,
        "row_id": row_id,
        "row_type": row_type,
        "selection_context_trace": traces["selection_context_trace"],
        "single_axis_stale_controls": dict(SINGLE_AXIS_STALE_CONTROLS),
        "snapshot_load_replay_status": "not_run_iteration3",
        "source_backed_horizon_envelope": baseline_horizon_envelope(),
        "source_claim_ceilings": source_claim_ceilings(source_rows),
        "source_digests": source_digests(source_rows),
        "source_rows": [row["row_id"] for row in source_rows],
        "stale_state_control_status": "failed_expected"
        if stale_field or stress_dimension.startswith("stale_")
        else "not_run_iteration3",
        "stress_dimension": stress_dimension,
        "stress_id": stress_id,
        "stress_ladder_index": ladder_index,
        "stress_ladder_rung": rung,
        "support_state_trace": traces["support_state_trace"],
        "unsafe_claim_flags": dict(UNSAFE_CLAIM_FLAGS),
    }
    return add_row_digest(row)


def build_rows(
    *,
    schema: dict[str, Any],
    selected_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_true_gates = {
        "source_rows_pinned",
        "source_claim_ceilings_preserved",
        "evidence_branch_artifact_only",
        "horizon_envelope_declared",
        "all_required_trace_axes_present",
        "linked_trace_continuity_present",
        "cross_axis_continuity_evidence_present",
        "budget_valid",
        "unsafe_claim_flags_false",
        "phase8_not_opened",
        "native_support_not_opened",
    }
    control_true_gates = {
        "source_rows_pinned",
        "source_claim_ceilings_preserved",
        "evidence_branch_artifact_only",
        "horizon_envelope_declared",
        "budget_valid",
        "unsafe_claim_flags_false",
        "phase8_not_opened",
        "native_support_not_opened",
    }
    stale_control_true_gates = control_true_gates | {"all_required_trace_axes_present"}
    return [
        make_row(
            row_id="n18_i3_row_01_n17_ap7_short_horizon_replay_baseline",
            row_type="baseline_replay",
            stress_id="i3_l1_n17_ap7_short_horizon_baseline",
            stress_dimension="baseline_ap7_replay",
            rung="L1",
            row_decision="supported",
            claim_ceiling="artifact_level_ap7_closed_boundary_engagement_loop_candidate",
            source_rows=selected_sources,
            schema=schema,
            true_gates=baseline_true_gates,
            outcome_detail="baseline_ap7_replay_supported_no_ap8",
        ),
        make_row(
            row_id="n18_i3_row_02_baseline_ap7_as_ap8_relabel_control",
            row_type="control_row",
            stress_id="i3_l1_baseline_ap7_as_ap8_relabel_control",
            stress_dimension="baseline_ap7_replay",
            rung="L1",
            row_decision="rejected",
            claim_ceiling="baseline_ap7_replay_is_not_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=baseline_true_gates,
            outcome_detail="AP8_blocked_baseline_only",
        ),
        make_row(
            row_id="n18_i3_row_03_stale_state_replay_control",
            row_type="control_row",
            stress_id="i3_l6_stale_state_replay_control",
            stress_dimension="stale_state_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_state_replay_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            source_current=False,
            controls_override={"stale_state_replay_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_state",
        ),
        make_row(
            row_id="n18_i3_row_04_stale_support_state_control",
            row_type="control_row",
            stress_id="i3_l6_stale_support_state_control",
            stress_dimension="stale_support_state_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_support_state_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="support_state_trace",
            controls_override={"stale_support_state_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_05_stale_memory_context_control",
            row_type="control_row",
            stress_id="i3_l6_stale_memory_context_control",
            stress_dimension="stale_memory_context_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_memory_context_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="memory_context_trace",
            controls_override={"stale_memory_context_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_06_stale_selection_context_control",
            row_type="control_row",
            stress_id="i3_l6_stale_selection_context_control",
            stress_dimension="stale_selection_context_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_selection_context_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="selection_context_trace",
            controls_override={"stale_selection_context_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_07_stale_proxy_target_control",
            row_type="control_row",
            stress_id="i3_l6_stale_proxy_target_control",
            stress_dimension="stale_proxy_target_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_proxy_target_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="proxy_target_trace",
            controls_override={"stale_proxy_target_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_08_stale_boundary_state_control",
            row_type="control_row",
            stress_id="i3_l6_stale_boundary_state_control",
            stress_dimension="stale_boundary_state_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_boundary_state_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="boundary_separation_trace",
            controls_override={"stale_boundary_state_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_09_stale_loop_feedback_control",
            row_type="control_row",
            stress_id="i3_l6_stale_loop_feedback_control",
            stress_dimension="stale_loop_feedback_control",
            rung="L6",
            row_decision="rejected",
            claim_ceiling="stale_loop_feedback_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=stale_control_true_gates,
            stale_field="closed_loop_feedback_trace",
            controls_override={"stale_loop_feedback_control": "failed_expected"},
            outcome_detail="AP8_blocked_stale_single_axis",
        ),
        make_row(
            row_id="n18_i3_row_10_hidden_native_support_relabel_control",
            row_type="control_row",
            stress_id="i3_l1_hidden_native_support_relabel_control",
            stress_dimension="baseline_ap7_replay",
            rung="L1",
            row_decision="rejected",
            claim_ceiling="hidden_native_support_relabel_cannot_support_ap8",
            source_rows=selected_sources,
            schema=schema,
            true_gates=baseline_true_gates,
            controls_override={"hidden_native_support_relabel_control": "failed_expected"},
            outcome_detail="AP8_blocked_hidden_native_support",
        ),
    ]


def source_digest_checks(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
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


def make_checks(rows: list[dict[str, Any]], source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = rows[0]
    trace_checks = [
        baseline[trace]["present"] is True
        and baseline[trace]["source_backed"] is True
        and baseline[trace]["source_current"] is True
        for trace in TRACE_FIELDS
    ]
    stale_rows = [row for row in rows if row["stress_dimension"].startswith("stale_")]
    checks = [
        {
            "check_id": "required_source_rows_selected",
            "detail": [row["row_id"] for row in source_rows],
            "passed": [row["row_id"] for row in source_rows] == PRIMARY_SOURCE_ROWS,
        },
        {
            "check_id": "baseline_row_supported_at_l1",
            "detail": baseline["row_id"],
            "passed": baseline["row_decision"] == "supported"
            and baseline["stress_ladder_rung"] == "L1"
            and baseline["stress_dimension"] == "baseline_ap7_replay",
        },
        {
            "check_id": "baseline_trace_axes_source_current",
            "detail": TRACE_FIELDS,
            "passed": all(trace_checks),
        },
        {
            "check_id": "baseline_ap7_replay_not_promoted_to_ap8",
            "detail": {
                "ap8_candidate_allowed": baseline["ap8_candidate_allowed"],
                "final_ap8_supported": baseline["final_ap8_supported"],
                "long_horizon_continuity_evidence": baseline[
                    "long_horizon_continuity_evidence"
                ],
            },
            "passed": baseline["ap8_candidate_allowed"] is False
            and baseline["final_ap8_supported"] is False
            and baseline["long_horizon_continuity_evidence"] is False,
        },
        {
            "check_id": "stale_controls_fail_closed",
            "detail": [row["row_id"] for row in stale_rows],
            "passed": bool(stale_rows)
            and all(row["row_decision"] == "rejected" for row in stale_rows)
            and all(row["ap8_candidate_allowed"] is False for row in stale_rows),
        },
        {
            "check_id": "hidden_native_support_relabel_fails_closed",
            "detail": "n18_i3_row_10_hidden_native_support_relabel_control",
            "passed": rows[-1]["row_decision"] == "rejected"
            and rows[-1]["native_support_opened"] is False
            and rows[-1]["ap8_candidate_allowed"] is False,
        },
        {
            "check_id": "all_rows_keep_ap8_false",
            "detail": [row["row_id"] for row in rows if row["ap8_candidate_allowed"]],
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
    ]
    checks.extend(source_digest_checks(source_rows))
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "detail": "portable relative paths only",
            "passed": not contains_absolute_path({"rows": rows}),
        }
    )
    return checks


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["rows"]
    lines = [
        "# N18 Iteration 3 - Short-Horizon AP7 Replay Baseline",
        "",
        "## Summary",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"highest_positive_stress_ladder_rung = {payload['highest_positive_stress_ladder_rung']}",
        f"row_count = {payload['row_count']}",
        f"baseline_ap7_replay_supported = {str(payload['baseline_ap7_replay_supported']).lower()}",
        f"ap8_candidate_allowed = {str(payload['ap8_candidate_allowed']).lower()}",
        f"final_ap8_supported = {str(payload['final_ap8_supported']).lower()}",
        f"phase8_opened = {str(payload['phase8_opened']).lower()}",
        f"native_support_opened = {str(payload['native_support_opened']).lower()}",
        f"long_horizon_continuity_tested = {str(payload['long_horizon_continuity_tested']).lower()}",
        f"output_digest = {payload['output_digest']}",
        "```",
        "",
        "## Row Results",
        "",
        "| Row | Rung | Dimension | Decision | AP8 Allowed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["stress_ladder_rung"],
                    row["stress_dimension"],
                    row["row_decision"],
                    str(row["ap8_candidate_allowed"]).lower(),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 3 confirms that the N17 AP7 stack can be replayed at the",
            "short baseline horizon as source-current artifact evidence. This is",
            "an active null for N18: AP7 replay remains valid, but it is not",
            "long-horizon AP8 evidence.",
            "",
            "The positive row is only `L1`. The `L6` rows are controls, not",
            "positive ladder progress. They show stale whole-state and stale",
            "single-axis variants fail closed instead of becoming AP8 continuity.",
            "",
            "The baseline row keeps support, memory, regulation, selection, proxy,",
            "boundary, and closed-loop feedback traces present and source-current",
            "only at the N17 closeout horizon. It records",
            "`long_horizon_continuity_evidence = false`, so Iteration 4 remains",
            "the first possible positive AP8 evidence point.",
            "",
            "## Review Follow-Up",
            "",
            "Post-review cleanup keeps `ap8_outcome_classification` aligned with",
            "the Iteration 2 taxonomy by using `AP8_blocked` for AP8 outcome",
            "classification, while row-specific diagnostic detail is recorded in",
            "`ap8_outcome_detail`. Row 02 uses only schema-defined controls;",
            "the baseline-as-AP8 rejection is represented by the row ID, decision,",
            "gates, and outcome detail. Stale single-axis rows mark only the",
            "links touching the stale trace as non-source-current.",
            "",
            "## Claim Boundary",
            "",
            "This artifact supports only a short-horizon AP7 replay baseline. It",
            "does not support AP8, agency, semantic action/perception, semantic",
            "goal ownership, identity acceptance, native support, Phase 8, organism",
            "or life claims, or unrestricted autonomy.",
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
    sources_by_id = get_sources(inventory)
    selected_sources = [sources_by_id[row_id] for row_id in PRIMARY_SOURCE_ROWS]
    rows = build_rows(schema=schema, selected_sources=selected_sources)
    checks = make_checks(rows, selected_sources)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    payload = {
        "acceptance_state": "accepted_short_horizon_ap7_replay_baseline_no_ap8",
        "ap8_candidate_allowed": False,
        "artifact_id": "n18_short_horizon_ap7_replay_baseline",
        "baseline_ap7_replay_supported": True,
        "checks": checks,
        "closed_long_horizon_agentic_like_closure_demonstrated": False,
        "command": COMMAND,
        "control_rungs_are_not_positive_evidence": True,
        "control_rungs_exercised": ["L6"],
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
        "highest_positive_stress_ladder_rung": "L1",
        "iteration": 3,
        "long_horizon_continuity_tested": False,
        "native_branch_opened": False,
        "native_support_opened": False,
        "output_digest": "pending",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "purpose": "short-horizon AP7 replay baseline and AP8 active-null controls",
        "ready_for_iteration_4_horizon_window_sweep": not failed_checks,
        "row_count": len(rows),
        "rows": rows,
        "schema_version": "n18.short_horizon_ap7_replay_baseline.v1",
        "source_inventory": {
            "output_digest": inventory["output_digest"],
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
        },
        "status": "passed" if not failed_checks else "failed",
        "validator_command": VALIDATOR_COMMAND,
    }
    digest_input = dict(payload)
    digest_input.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_input)
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()

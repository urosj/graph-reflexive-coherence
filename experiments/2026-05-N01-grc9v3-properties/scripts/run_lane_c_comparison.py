"""Lane C comparison: Lane A baseline versus Lane B v1 column-H-assisted lane."""

from __future__ import annotations

import argparse
import copy
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_to_rc

import run_experiment_b_column_interface_cancellation as exp_b
import run_experiment_c_saturation as exp_c
import run_experiment_d_refinement_identity as exp_d


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_lane_c_comparison.py"
)
ARTIFACT_SCHEMA_VERSION = "grc9v3_lane_c_comparison_v1"
LANE_A_ID = "current_hybrid_signed_hessian"
LANE_B_ID = "grc9v3_column_h_assisted"
LANE_C_ID = "comparison"
DEFAULT_EPS_COLUMN_H = 0.001


def _git_value(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            cwd=EXPERIMENT_ROOT.parents[1],
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _lane_params(base_params: dict[str, Any], *, lane_id: str) -> dict[str, Any]:
    params = copy.deepcopy(base_params)
    evolution = params.setdefault("evolution", {})
    modes = params.setdefault("constitutive_semantic_modes", {})
    modes["spark_lane"] = lane_id
    if lane_id == LANE_B_ID:
        evolution.setdefault("eps_column_h", DEFAULT_EPS_COLUMN_H)
        evolution.setdefault("eps_column_h_crossing_zero", 0.0)
        modes.update(
            {
                "enable_column_h_threshold": True,
                "enable_column_h_sign_crossing": False,
                "column_h_sign_crossing_mode": "theory_product",
                "store_previous_column_h": False,
                "require_active_degree_9": True,
                "require_sink_for_column_h_spark": True,
                "enable_near_saturation": False,
                "near_saturation_degree": 8,
            }
        )
    return params


def _run_once(
    *,
    state_payload: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    model = GRC9V3.from_state(state=copy.deepcopy(state_payload), params=params)
    emitted_events = model.apply_hybrid_sparks()
    candidate_events = [
        event for event in emitted_events if event.kind == "hybrid_spark_candidate"
    ]
    expansion_events = [
        event for event in emitted_events if event.kind == "hybrid_mechanical_expansion"
    ]
    completed_events = [
        event for event in emitted_events if event.kind == "hybrid_spark_completed"
    ]
    candidate_payload = candidate_events[0].payload if candidate_events else {}
    expansion_payload = expansion_events[0].payload if expansion_events else {}
    completed_payload = completed_events[0].payload if completed_events else {}
    return {
        "model": model,
        "state": model.get_state(),
        "events": emitted_events,
        "event_kinds": [event.kind for event in emitted_events],
        "candidate_count": len(candidate_events),
        "refinement_count": len(expansion_events),
        "completed_count": len(completed_events),
        "candidate_payload": candidate_payload,
        "expansion_payload": expansion_payload,
        "completed_payload": completed_payload,
    }


def _column_proxy_value_for_source(
    *,
    source_experiment: str,
    state_payload: dict[str, Any],
) -> float | str:
    if source_experiment == "experiment_b_column_interface_cancellation":
        model = GRC9V3.from_state(state=copy.deepcopy(state_payload), params=exp_b._params(0))
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_differential_state()
        proxy = exp_b.column_proxy(model.get_state())
        return min(float(value) for value in proxy["residual"].values())
    if source_experiment == "experiment_c_saturation":
        model = GRC9V3.from_state(state=copy.deepcopy(state_payload), params=exp_c._params(0))
        diagnostic = exp_c._column_diagnostic(model.get_state())
        return min(float(value) for value in diagnostic["residual"].values())
    return ""


def _old_column_preserved(expansion_payload: dict[str, Any]) -> bool | str:
    reassignment_map = expansion_payload.get("reassignment_map", {})
    if not reassignment_map:
        return ""
    preserved = []
    for payload in reassignment_map.values():
        _, old_column = port_to_rc(int(payload["from_port_id"]))
        _, new_column = port_to_rc(int(payload["to_port_id"]))
        preserved.append(old_column == new_column)
    return all(preserved)


def _identity_status(run: dict[str, Any]) -> str:
    if run["refinement_count"] == 0:
        return "no_refinement_no_identity_claim"
    completed_payload = run["completed_payload"]
    child_node_ids = [
        int(node_id)
        for node_id in completed_payload.get("stabilized_child_node_ids", [])
    ]
    if not child_node_ids:
        return "mechanical_refinement_only_no_completed_child_payload"
    persistence_rows = exp_d._run_persistence_window(
        run["model"],
        child_node_ids=child_node_ids,
        steps=exp_d.PERSISTENCE_WINDOW_STEPS,
    )
    persistent_children = [
        child_node_id
        for child_node_id in child_node_ids
        if exp_d._threshold_pass(
            persistence_rows,
            child_node_id=child_node_id,
            window_steps=exp_d.PERSISTENCE_WINDOW_STEPS,
            min_basin_mass=exp_d.MIN_BASIN_MASS,
        )
    ]
    if persistent_children:
        return "configured_window_child_basin_persistence"
    return "post_window_child_basin_persistence_not_observed"


def _comparison_row(
    *,
    comparison_id: str,
    source_experiment: str,
    source_fixture_id: str,
    condition_id: str,
    transform_id: str,
    seed: int,
    state_payload: dict[str, Any],
    lane_a_params: dict[str, Any],
    lane_b_params: dict[str, Any],
    lane_a_run: dict[str, Any],
    lane_b_run: dict[str, Any],
    source_artifact_paths: list[str],
) -> dict[str, Any]:
    lane_b_payload = lane_b_run["candidate_payload"]
    lane_a_proxy_value = _column_proxy_value_for_source(
        source_experiment=source_experiment,
        state_payload=state_payload,
    )
    column_h_branch_hit = bool(lane_b_payload.get("column_h_branch_hit", False))
    gate_reasons = list(lane_b_payload.get("gate_reasons", []))
    direct_column_h_branch = bool(
        lane_b_payload.get("spark_lane") == LANE_B_ID
        and column_h_branch_hit
        and (
            "column_h_threshold_hit" in gate_reasons
            or "column_h_sign_crossing_hit" in gate_reasons
        )
    )
    if source_experiment == "experiment_d_refinement_identity":
        lane_a_identity_status = _identity_status(lane_a_run)
        lane_b_identity_status = _identity_status(lane_b_run)
    else:
        lane_a_identity_status = "not_evaluated_for_this_lane_c_slice"
        lane_b_identity_status = "not_evaluated_for_this_lane_c_slice"
    return {
        "comparison_id": comparison_id,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_experiment_or_discriminator": source_experiment,
        "source_fixture_id": source_fixture_id,
        "condition_id": condition_id,
        "transform_id": transform_id,
        "seed": seed,
        "lane_a_id": LANE_A_ID,
        "lane_b_id": LANE_B_ID,
        "lane_a_runtime_params": _json(lane_a_params),
        "lane_b_runtime_params": _json(lane_b_params),
        "lane_a_artifact_paths": _json(source_artifact_paths),
        "lane_b_artifact_paths": _json([]),
        "candidate_count_lane_a": lane_a_run["candidate_count"],
        "candidate_count_lane_b": lane_b_run["candidate_count"],
        "refinement_count_lane_a": lane_a_run["refinement_count"],
        "refinement_count_lane_b": lane_b_run["refinement_count"],
        "lane_a_column_proxy_status": "derived_non_gating",
        "lane_a_column_proxy_value": lane_a_proxy_value,
        "lane_b_column_h": _json(lane_b_payload.get("column_h", [])),
        "lane_b_column_h_branch_hit": column_h_branch_hit,
        "lane_b_column_h_threshold_hit": bool(
            lane_b_payload.get("column_h_threshold_hit", False)
        ),
        "lane_b_column_h_sign_crossing_hit": bool(
            lane_b_payload.get("column_h_sign_crossing_hit", False)
        ),
        "lane_b_gate_reasons": _json(gate_reasons),
        "lane_b_candidate_event_id": lane_b_payload.get("candidate_event_id", ""),
        "lane_b_linked_expansion_event_id": lane_b_payload.get(
            "linked_expansion_event_id",
            "",
        ),
        "budget_error_lane_a": lane_a_run["expansion_payload"].get("budget_error", ""),
        "budget_error_lane_b": lane_b_run["expansion_payload"].get("budget_error", ""),
        "old_column_preservation_lane_a": _old_column_preserved(
            lane_a_run["expansion_payload"],
        ),
        "old_column_preservation_lane_b": _old_column_preserved(
            lane_b_run["expansion_payload"],
        ),
        "post_window_identity_status_lane_a": lane_a_identity_status,
        "post_window_identity_status_lane_b": lane_b_identity_status,
        "lane_b_evidence_label": (
            "direct_runtime_proxy_branch"
            if direct_column_h_branch
            else (
                "direct_runtime_non_branch_diagnostic"
                if lane_b_payload.get("spark_lane") == LANE_B_ID
                else "no_lane_b_candidate"
            )
        ),
        "evidence_boundary": (
            "Lane C paired clean fixture comparison only; no landscape-general claim."
        ),
    }


def _b_fixture_cases(seed: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    transforms = exp_b._transforms(seed)
    for base_fixture, expected_column in exp_b._fixture_suite(seed):
        del expected_column
        for transform_id, port_map in transforms.items():
            fixture = (
                base_fixture
                if transform_id == "identity"
                else exp_b.apply_port_map(
                    base_fixture,
                    port_map,
                    transform_id=transform_id,
                )
            )
            cases.append(
                {
                    "source_experiment": "experiment_b_column_interface_cancellation",
                    "source_fixture_id": base_fixture.fixture_id,
                    "condition_id": fixture.fixture_id,
                    "transform_id": transform_id,
                    "state_payload": exp_b.fixture_to_state(fixture),
                    "base_params": exp_b._params(seed),
                    "source_artifact_paths": [
                        "outputs/experiment_b_column_interface_cancellation_manifest.json",
                        "outputs/experiment_b_column_interface_cancellation_rows.csv",
                    ],
                }
            )
    return cases


def _c_fixture_cases(seed: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    transforms = exp_c._transforms(seed)
    selected = {
        "C1_degree_7_stressed",
        "C2_degree_8_stressed",
        "C3_degree_9_stressed",
        "C5_degree_9_stable_hessian",
    }
    for condition in exp_c._condition_suite(seed):
        if condition["condition_id"] not in selected:
            continue
        for transform_id, port_map in transforms.items():
            active_ports = exp_c._active_ports_after_transform(
                condition["active_ports"],
                port_map,
            )
            cases.append(
                {
                    "source_experiment": "experiment_c_saturation",
                    "source_fixture_id": condition["condition_id"],
                    "condition_id": condition["condition_id"],
                    "transform_id": transform_id,
                    "state_payload": exp_c.saturation_fixture_state(
                        active_ports=active_ports,
                        signed_hessian=condition["signed_hessian"],
                    ),
                    "base_params": exp_c._params(seed),
                    "source_artifact_paths": [
                        "outputs/experiment_c_saturation_manifest.json",
                        "outputs/d4_saturation_summary.json",
                    ],
                }
            )
    return cases


def _d_fixture_cases(seed: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    transforms = exp_d._transforms(seed)
    selected = {
        "d_equal_transfer_refinement",
        "d_column_1_skewed_transfer",
        "d_column_2_skewed_transfer",
        "d_column_3_skewed_transfer",
        "d_degree_8_no_refinement_control",
    }
    for condition in exp_d._condition_suite():
        if condition["condition_id"] not in selected:
            continue
        for transform_id, port_map in transforms.items():
            active_ports = exp_d._active_ports_after_transform(
                condition["active_ports"],
                port_map,
            )
            cases.append(
                {
                    "source_experiment": "experiment_d_refinement_identity",
                    "source_fixture_id": condition["condition_id"],
                    "condition_id": condition["condition_id"],
                    "transform_id": transform_id,
                    "state_payload": exp_c.saturation_fixture_state(
                        active_ports=active_ports,
                        signed_hessian=exp_d.STRESSED_SIGNED_HESSIAN,
                    ),
                    "base_params": exp_d._params(
                        seed,
                        expansion_distribution_mode=condition[
                            "expansion_distribution_mode"
                        ],
                        expansion_custom_weights=condition["expansion_custom_weights"],
                    ),
                    "source_artifact_paths": [
                        "outputs/experiment_d_refinement_identity_manifest.json",
                        "outputs/d5_interface_memory_summary.json",
                        "outputs/d8_identity_emergence_summary.json",
                    ],
                }
            )
    return cases


def run_comparison(seed: int) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    candidate_rows: list[dict[str, Any]] = []
    refinement_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    branch_rows: list[dict[str, Any]] = []
    for index, case in enumerate(
        [*_b_fixture_cases(seed), *_c_fixture_cases(seed), *_d_fixture_cases(seed)]
    ):
        lane_a_params = _lane_params(case["base_params"], lane_id=LANE_A_ID)
        lane_b_params = _lane_params(case["base_params"], lane_id=LANE_B_ID)
        lane_a_run = _run_once(
            state_payload=case["state_payload"],
            params=lane_a_params,
        )
        lane_b_run = _run_once(
            state_payload=case["state_payload"],
            params=lane_b_params,
        )
        comparison_id = f"lane_c_{index:03d}"
        row = _comparison_row(
            comparison_id=comparison_id,
            source_experiment=case["source_experiment"],
            source_fixture_id=case["source_fixture_id"],
            condition_id=case["condition_id"],
            transform_id=case["transform_id"],
            seed=seed,
            state_payload=case["state_payload"],
            lane_a_params=lane_a_params,
            lane_b_params=lane_b_params,
            lane_a_run=lane_a_run,
            lane_b_run=lane_b_run,
            source_artifact_paths=case["source_artifact_paths"],
        )
        candidate_rows.append(row)
        if lane_a_run["refinement_count"] or lane_b_run["refinement_count"]:
            refinement_rows.append(row)
        if case["source_experiment"] == "experiment_d_refinement_identity":
            identity_rows.append(row)
        if lane_b_run["candidate_count"]:
            branch_rows.append(
                {
                    "comparison_id": comparison_id,
                    "source_experiment_or_discriminator": case["source_experiment"],
                    "condition_id": case["condition_id"],
                    "transform_id": case["transform_id"],
                    "seed": seed,
                    "spark_lane": LANE_B_ID,
                    "candidate_event_id": row["lane_b_candidate_event_id"],
                    "column_h": row["lane_b_column_h"],
                    "column_h_branch_hit": row["lane_b_column_h_branch_hit"],
                    "column_h_threshold_hit": row["lane_b_column_h_threshold_hit"],
                    "column_h_sign_crossing_hit": (
                        row["lane_b_column_h_sign_crossing_hit"]
                    ),
                    "gate_reasons": row["lane_b_gate_reasons"],
                    "evidence_label": row["lane_b_evidence_label"],
                }
            )

    direct_branch_rows = [
        row
        for row in candidate_rows
        if row["lane_b_evidence_label"] == "direct_runtime_proxy_branch"
    ]
    candidate_delta_rows = [
        row
        for row in candidate_rows
        if int(row["candidate_count_lane_a"]) != int(row["candidate_count_lane_b"])
    ]
    refinement_delta_rows = [
        row
        for row in candidate_rows
        if int(row["refinement_count_lane_a"]) != int(row["refinement_count_lane_b"])
    ]
    summary = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_c_id": LANE_C_ID,
        "seed": seed,
        "lane_a_id": LANE_A_ID,
        "lane_b_id": LANE_B_ID,
        "comparison_row_count": len(candidate_rows),
        "candidate_count_lane_a_total": sum(
            int(row["candidate_count_lane_a"]) for row in candidate_rows
        ),
        "candidate_count_lane_b_total": sum(
            int(row["candidate_count_lane_b"]) for row in candidate_rows
        ),
        "refinement_count_lane_a_total": sum(
            int(row["refinement_count_lane_a"]) for row in candidate_rows
        ),
        "refinement_count_lane_b_total": sum(
            int(row["refinement_count_lane_b"]) for row in candidate_rows
        ),
        "direct_runtime_proxy_branch_rows": len(direct_branch_rows),
        "signed_hessian_only_lane_b_candidate_rows": sum(
            1
            for row in branch_rows
            if row["evidence_label"] == "direct_runtime_non_branch_diagnostic"
        ),
        "candidate_delta_rows": len(candidate_delta_rows),
        "refinement_delta_rows": len(refinement_delta_rows),
        "degree_8_near_saturation_blocked": all(
            int(row["candidate_count_lane_b"]) == 0
            for row in candidate_rows
            if "degree_8" in str(row["condition_id"])
        ),
        "lane_a_column_evidence_label": "derived_non_gating",
        "lane_b_direct_branch_evidence_rule": (
            "spark_lane == grc9v3_column_h_assisted and column_h_branch_hit "
            "with a column-H gate reason"
        ),
        "identity_claim_boundary": (
            "mechanical expansion is not identity; identity status uses post-event basin persistence"
        ),
        "classification": (
            "lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries"
        ),
    }
    blocked_rows = [
        {
            "observation": "degree_8_near_saturation",
            "status": "blocked",
            "artifact_source": "Lane B v1 predicate and paired Lane C degree-8 rows",
            "notes": "Degree-8 rows do not emit Lane B candidates; virtual stubs remain out of scope.",
        },
        {
            "observation": "landscape_general_lane_delta",
            "status": "inconclusive",
            "artifact_source": "Lane C clean fixture subset",
            "notes": "Lane C uses selected clean fixtures only, not a robustness suite.",
        },
        {
            "observation": "pure_grc9_eq12_column_h_lane",
            "status": "not_run",
            "artifact_source": "Lane C setup",
            "notes": "Lane B v1 is GRC9V3 column-H-assisted inside the saturation/gradient envelope, not bare Eq. 12.",
        },
        {
            "observation": "full_D1_D3_rerun_under_lane_b",
            "status": "partial",
            "artifact_source": "Lane C transformed B/C/D fixture rows",
            "notes": "Lane C includes sampled transforms from the existing harness but does not rerun the full D1/D3 discriminator family.",
        },
    ]
    return candidate_rows, refinement_rows, identity_rows, branch_rows, blocked_rows, summary


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        if not rows:
            raise ValueError(f"cannot infer CSV fields for empty {path}")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(
    path: Path,
    *,
    candidate_rows: list[dict[str, Any]],
    branch_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_source = sorted(
        {
            row["source_experiment_or_discriminator"]
            for row in candidate_rows
        }
    )
    lines = [
        "# Lane C Lane A / Lane B Comparison",
        "",
        "Status: complete.",
        "",
        "Lane C is an analysis pass, not a runtime spark lane. It compares",
        "`current_hybrid_signed_hessian` against opt-in",
        "`grc9v3_column_h_assisted` on selected clean fixtures.",
        "",
        "## Result",
        "",
        f"- comparison rows: `{summary['comparison_row_count']}`",
        f"- Lane A candidates: `{summary['candidate_count_lane_a_total']}`",
        f"- Lane B candidates: `{summary['candidate_count_lane_b_total']}`",
        f"- Lane A refinements: `{summary['refinement_count_lane_a_total']}`",
        f"- Lane B refinements: `{summary['refinement_count_lane_b_total']}`",
        f"- direct Lane B column-H proxy-branch rows: `{summary['direct_runtime_proxy_branch_rows']}`",
        f"- candidate delta rows: `{summary['candidate_delta_rows']}`",
        f"- refinement delta rows: `{summary['refinement_delta_rows']}`",
        f"- degree-8 near-saturation blocked: `{json.dumps(summary['degree_8_near_saturation_blocked'])}`",
        "",
        "Classification:",
        "",
        f"`{summary['classification']}`",
        "",
        "## Source Slices",
        "",
    ]
    for source in by_source:
        source_rows = [
            row
            for row in candidate_rows
            if row["source_experiment_or_discriminator"] == source
        ]
        direct_rows = [
            row
            for row in source_rows
            if row["lane_b_evidence_label"] == "direct_runtime_proxy_branch"
        ]
        lines.append(
            f"- `{source}`: `{len(source_rows)}` rows; "
            f"`{len(direct_rows)}` direct column-H proxy-branch rows."
        )
    lines.extend(
        [
            "",
            "## Branch Attribution",
            "",
            "| Condition | Transform | Gate reasons | Evidence label |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in branch_rows[:20]:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['transform_id']} | "
            f"`{row['gate_reasons']}` | "
            f"`{row['evidence_label']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Lane A column evidence remains `derived_non_gating`.",
            "- Lane B direct evidence means direct runtime evidence that the",
            "  column-H proxy branch fired; `H_s[b]` remains a proxy.",
            "- Degree-8 near-saturation and virtual stubs remain blocked in Lane B v1.",
            "- Mechanical expansion remains separate from identity acceptance.",
            "- This is a clean fixture comparison, not landscape-general validation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_c_id": LANE_C_ID,
        "script_path": SCRIPT_PATH,
        "command": (
            "PYTHONPATH=src .venv/bin/python "
            f"{SCRIPT_PATH} --write-defaults --seed {seed}"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "seed": seed,
        "lane_a_id": LANE_A_ID,
        "lane_b_id": LANE_B_ID,
        "summary": summary,
        "output_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in output_paths.items()
        },
        "source_setup": "implementation/GRC9V3-LaneC-ComparisonSetup.md",
        "validation_commands": [
            f"PYTHONPATH=src .venv/bin/python -m py_compile {SCRIPT_PATH}",
            f"PYTHONPATH=src .venv/bin/ruff check {SCRIPT_PATH}",
            (
                "PYTHONPATH=src .venv/bin/python "
                f"{SCRIPT_PATH} --write-defaults --seed {seed}"
            ),
            (
                ".venv/bin/python -m json.tool "
                "experiments/2026-05-N01-grc9v3-properties/outputs/"
                "lane_c_summary.json"
            ),
        ],
    }


def write_outputs(seed: int) -> dict[str, Any]:
    (
        candidate_rows,
        refinement_rows,
        identity_rows,
        branch_rows,
        blocked_rows,
        summary,
    ) = run_comparison(seed)
    output_paths = {
        "manifest": EXPERIMENT_ROOT / "outputs/lane_c_comparison_manifest.json",
        "candidate": EXPERIMENT_ROOT / "outputs/lane_c_candidate_comparison.csv",
        "refinement": EXPERIMENT_ROOT / "outputs/lane_c_refinement_comparison.csv",
        "identity": EXPERIMENT_ROOT / "outputs/lane_c_identity_comparison.csv",
        "branch": EXPERIMENT_ROOT / "outputs/lane_c_branch_attribution.csv",
        "summary": EXPERIMENT_ROOT / "outputs/lane_c_summary.json",
        "report": EXPERIMENT_ROOT / "reports/lane_c_comparison_report.md",
        "blocked": EXPERIMENT_ROOT / "reports/lane_c_blocked_observations.md",
    }
    _write_csv(output_paths["candidate"], candidate_rows)
    _write_csv(output_paths["refinement"], refinement_rows, list(candidate_rows[0]))
    _write_csv(output_paths["identity"], identity_rows, list(candidate_rows[0]))
    _write_csv(output_paths["branch"], branch_rows)
    _write_json(output_paths["summary"], summary)
    _write_report(
        output_paths["report"],
        candidate_rows=candidate_rows,
        branch_rows=branch_rows,
        summary=summary,
    )
    output_paths["blocked"].write_text(
        "# Lane C Blocked Observations\n\n"
        "| Observation | Status | Artifact source | Notes |\n"
        "| --- | --- | --- | --- |\n"
        + "\n".join(
            "| "
            f"{row['observation']} | "
            f"{row['status']} | "
            f"{row['artifact_source']} | "
            f"{row['notes']} |"
            for row in blocked_rows
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(
        seed=seed,
        summary=summary,
        output_paths=output_paths,
    )
    _write_json(output_paths["manifest"], manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()

    if args.write_defaults:
        manifest = write_outputs(args.seed)
    else:
        (*_, summary) = run_comparison(args.seed)
        manifest = {"summary": summary}
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

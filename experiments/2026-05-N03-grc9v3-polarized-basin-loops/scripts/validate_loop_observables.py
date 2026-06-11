#!/usr/bin/env python3
"""Smoke-test experiment-local loop observables.

The script builds synthetic null, structured, kick-like, and budget-drift
traces.  It validates observable orientation, schema shape, cycle detection,
and fail-closed budget reporting without importing or modifying `src/pygrc`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from loop_observables import (
    REQUIRED_REPORT_KEYS,
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = ROOT / "outputs" / "loop_observables_smoke_report.json"
REPORT_PATH = ROOT / "reports" / "loop_observables_smoke_report.md"
TIMESERIES_DIR = ROOT / "outputs" / "loop_observables_timeseries"


def _uniform_c(node_count: int, budget: float = 1.0) -> dict[str, float]:
    value = budget / node_count
    return {str(node_id): value for node_id in range(node_count)}


def _apply_delta(c_values: Mapping[str, float], deltas: Mapping[int, float]) -> dict[str, float]:
    updated = {str(node_id): float(value) for node_id, value in c_values.items()}
    for node_id, delta in deltas.items():
        updated[str(node_id)] = updated.get(str(node_id), 0.0) + float(delta)
    return updated


def _flux(edge_values: Mapping[int, float]) -> dict[str, float]:
    return {str(edge_id): float(value) for edge_id, value in edge_values.items()}


def _budget(c_pre: Mapping[str, float], c_post: Mapping[str, float]) -> dict[str, Any]:
    before = sum(float(value) for value in c_pre.values())
    after = sum(float(value) for value in c_post.values())
    return {
        "before_continuity": before,
        "after_continuity": after,
        "after_correction": after,
        "correction_method": "none",
        "correction_magnitude": 0.0,
        "simplex_projection_applied": False,
        "uniform_shift_applied": False,
    }


def _record(
    *,
    step_index: int,
    c_pre: Mapping[str, float],
    deltas: Mapping[int, float] | None = None,
    flux_values: Mapping[int, float] | None = None,
    budget_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    c_post = _apply_delta(c_pre, deltas or {})
    return {
        "step_index": step_index,
        "C_pre": dict(c_pre),
        "C_post_continuity": c_post,
        "C_post_budget": dict(c_post),
        "flux_uv": _flux(flux_values or {}),
        "budget": dict(budget_override) if budget_override is not None else _budget(c_pre, c_post),
    }


def _null_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    c = _uniform_c(node_count)
    return [_record(step_index=step, c_pre=c) for step in range(total_steps)]


def _positive_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    """Build three ordered source/forward/sink/return/refill cascades."""

    c = _uniform_c(node_count)
    records: list[dict[str, Any]] = []
    cycle_starts = {15, 45, 75}
    for step in range(total_steps):
        offset = next((step - start for start in cycle_starts if 0 <= step - start <= 4), None)
        deltas: dict[int, float] = {}
        flux_values: dict[int, float] = {}
        if offset == 0:
            # Source drop/export: edge 1 leaves source region.
            deltas = {0: -0.002, 1: -0.002, 2: 0.002, 3: 0.002}
            flux_values = {1: 0.03}
        elif offset == 1:
            # Forward channel pulse source -> sink.
            flux_values = {edge_id: 0.03 for edge_id in range(1, 6)}
        elif offset == 2:
            # Sink rise/import: edge 5 enters sink region.
            deltas = {6: 0.002, 7: 0.002, 4: -0.002, 5: -0.002}
            flux_values = {5: 0.04}
        elif offset == 3:
            # Return channel pulse sink side -> source side.
            flux_values = {edge_id: 0.01 for edge_id in range(7, 12)}
        elif offset == 4:
            # Source refill: edge 11 enters source region.
            deltas = {0: 0.002, 1: 0.002, 10: -0.002, 11: -0.002}
            flux_values = {11: 0.015}
        records.append(
            _record(
                step_index=step,
                c_pre=c,
                deltas=deltas,
                flux_values=flux_values,
            )
        )
    return records


def _partial_cascade_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    """Build repeated source/forward/sink events without return/refill closure."""

    c = _uniform_c(node_count)
    records: list[dict[str, Any]] = []
    cycle_starts = {15, 45, 75}
    for step in range(total_steps):
        offset = next((step - start for start in cycle_starts if 0 <= step - start <= 2), None)
        deltas: dict[int, float] = {}
        flux_values: dict[int, float] = {}
        if offset == 0:
            deltas = {0: -0.002, 1: -0.002, 2: 0.002, 3: 0.002}
            flux_values = {1: 0.03}
        elif offset == 1:
            flux_values = {edge_id: 0.03 for edge_id in range(1, 6)}
        elif offset == 2:
            deltas = {6: 0.002, 7: 0.002, 4: -0.002, 5: -0.002}
            flux_values = {5: 0.04}
        records.append(
            _record(
                step_index=step,
                c_pre=c,
                deltas=deltas,
                flux_values=flux_values,
            )
        )
    return records


def _phase_scrambled_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    """Use matching amplitudes but a wrong event order."""

    c = _uniform_c(node_count)
    records: list[dict[str, Any]] = []
    cycle_starts = {15, 45, 75}
    for step in range(total_steps):
        offset = next((step - start for start in cycle_starts if 0 <= step - start <= 4), None)
        deltas: dict[int, float] = {}
        flux_values: dict[int, float] = {}
        if offset == 0:
            # Source drop/export is present.
            deltas = {0: -0.002, 1: -0.002, 2: 0.002, 3: 0.002}
            flux_values = {1: 0.03}
        elif offset == 1:
            # Return flux appears before sink rise and forward channel pulse.
            flux_values = {edge_id: 0.01 for edge_id in range(7, 12)}
        elif offset == 2:
            deltas = {6: 0.002, 7: 0.002, 4: -0.002, 5: -0.002}
            flux_values = {5: 0.04}
        elif offset == 3:
            flux_values = {edge_id: 0.03 for edge_id in range(1, 6)}
        elif offset == 4:
            deltas = {0: 0.002, 1: 0.002, 10: -0.002, 11: -0.002}
            flux_values = {11: 0.015}
        records.append(
            _record(
                step_index=step,
                c_pre=c,
                deltas=deltas,
                flux_values=flux_values,
            )
        )
    return records


def _perfect_cascade_with_budget_drift_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    """Positive cascade trace with an uncorrected budget drift injected."""

    records = _positive_trace(total_steps, node_count)
    record = dict(records[16])
    c_post = dict(record["C_post_budget"])
    c_post["0"] = float(c_post["0"]) + 0.01
    record["C_post_continuity"] = c_post
    record["C_post_budget"] = c_post
    record["budget"] = {
        "before_continuity": 1.0,
        "after_continuity": 1.01,
        "after_correction": 1.01,
        "correction_method": "none",
        "correction_magnitude": 0.0,
        "simplex_projection_applied": False,
        "uniform_shift_applied": False,
    }
    records[16] = record
    return records


def _budget_drift_trace(total_steps: int, node_count: int) -> list[dict[str, Any]]:
    c = _uniform_c(node_count)
    records = [_record(step_index=step, c_pre=c) for step in range(total_steps)]
    drift_post = _apply_delta(c, {0: 0.01})
    records[20] = {
        "step_index": 20,
        "C_pre": dict(c),
        "C_post_continuity": drift_post,
        "C_post_budget": drift_post,
        "flux_uv": {},
        "budget": {
            "before_continuity": 1.0,
            "after_continuity": 1.01,
            "after_correction": 1.01,
            "correction_method": "none",
            "correction_magnitude": 0.0,
            "simplex_projection_applied": False,
            "uniform_shift_applied": False,
        },
    }
    return records


def _run_trace(
    *,
    manifest: Mapping[str, Any],
    lane_id: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = compute_observable_rows(
        manifest=manifest,
        records=records,
        fixture_id="grc9v3_ported_ring_v1",
    )
    timeseries_path = TIMESERIES_DIR / f"{lane_id.lower()}_synthetic_timeseries.jsonl"
    write_jsonl(timeseries_path, rows)
    return summarize_observables(
        manifest=manifest,
        rows=rows,
        lane_id=lane_id,
        fixture_id="grc9v3_ported_ring_v1",
        timeseries_path=timeseries_path,
        runtime_provenance_override={
            "model_family": "synthetic_trace",
            "runner_mode": "synthetic_trace_validator",
            "called_methods": [
                "synthetic_trace_generation",
                "experiment_local_loop_observables",
            ],
            "source_manifest_model_family": manifest["scope"]["model_family"],
            "source_manifest_runner_mode": manifest["scope"]["runner_mode"],
        },
    )


def _validate_reports(reports: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for lane_id, report in reports.items():
        missing = sorted(REQUIRED_REPORT_KEYS - set(report))
        if missing:
            errors.append(f"{lane_id}: missing required report keys {missing}")
        if report.get("schema") != "grc9v3_polarized_basin_loop_report_v1":
            errors.append(f"{lane_id}: unexpected report schema {report.get('schema')!r}")

    null_report = reports["U0_synthetic"]
    if null_report["roles"]["source_like_measured"]:
        errors.append("U0_synthetic unexpectedly measured source-like role")
    if null_report["roles"]["sink_like_measured"]:
        errors.append("U0_synthetic unexpectedly measured sink-like role")
    if null_report["cycles"]["cycle_count"] != 0:
        errors.append("U0_synthetic unexpectedly detected cycles")
    if not null_report["budget"]["passed"]:
        errors.append("U0_synthetic budget audit should pass")

    positive_report = reports["K_synthetic"]
    if not positive_report["roles"]["source_like_measured"]:
        errors.append("K_synthetic did not measure source-like role")
    if not positive_report["roles"]["sink_like_measured"]:
        errors.append("K_synthetic did not measure sink-like role")
    if not positive_report["phase_cascade"]["passed"]:
        errors.append("K_synthetic did not pass phase-cascade gate")
    if not positive_report["cycles"]["l4_cycle_requirement_met"]:
        errors.append("K_synthetic did not satisfy n_cycles_min")
    if not positive_report["budget"]["passed"]:
        errors.append("K_synthetic budget audit should pass")
    if positive_report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
        errors.append("K_synthetic should not promote a runtime candidate claim")
    if positive_report["runtime_provenance"]["runner_mode"] != "synthetic_trace_validator":
        errors.append("synthetic smoke report should not look like a live GRC9V3 runtime run")
    if positive_report["timeseries"]["artifact_sha256"] is None:
        errors.append("K_synthetic is missing a time-series digest")

    drift_report = reports["budget_drift_synthetic"]
    if drift_report["budget"]["passed"]:
        errors.append("budget_drift_synthetic budget audit should fail")
    if drift_report["budget"]["max_abs_error_post_correction"] <= 0.0:
        errors.append("budget_drift_synthetic did not expose post-correction error")

    partial_report = reports["partial_cascade_synthetic"]
    if partial_report["phase_cascade"]["n_detected_cascades"] != 0:
        errors.append("partial_cascade_synthetic should not count full cascades")
    if partial_report["cycles"]["l4_cycle_requirement_met"]:
        errors.append("partial_cascade_synthetic should not satisfy L4 cycle gate")

    scrambled_report = reports["phase_scrambled_synthetic"]
    if scrambled_report["phase_cascade"]["n_detected_cascades"] != 0:
        errors.append("phase_scrambled_synthetic should not count ordered cascades")
    if scrambled_report["cycles"]["l4_cycle_requirement_met"]:
        errors.append("phase_scrambled_synthetic should not satisfy L4 cycle gate")

    drift_cascade_report = reports["budget_drift_with_cascade_synthetic"]
    if drift_cascade_report["budget"]["passed"]:
        errors.append("budget_drift_with_cascade_synthetic budget audit should fail")
    if not drift_cascade_report["cycles"]["l4_cycle_requirement_met"]:
        errors.append("budget_drift_with_cascade_synthetic should still expose cascade shape")
    if drift_cascade_report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
        errors.append("budget_drift_with_cascade_synthetic should block positive claims")
    if "budget_gate_failed" not in drift_cascade_report["claim_gate"]["blocked_reasons"]:
        errors.append("budget_drift_with_cascade_synthetic should list budget_gate_failed")
    if drift_cascade_report["claim_gate"]["primary_scientific_blocker"] != "budget_gate_failed":
        errors.append("budget_drift_with_cascade_synthetic should expose budget as primary blocker")
    return errors


def _write_markdown_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    reports = result["reports"]
    lines = [
        "# Iteration 3 Loop Observable Smoke Report",
        "",
        "Command:",
        "",
        "```bash",
        "python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "This smoke run uses synthetic traces only. It validates the experiment-local",
        "observable library and does not import or modify `src/pygrc`.",
        "",
        "## Trace Summary",
        "",
        "| Trace | Budget | Source | Sink | Cascades | L4 Cycle Gate | Claim Allowed | Runner |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for lane_id, report in reports.items():
        lines.append(
            "| {lane} | {budget} | {source} | {sink} | {cascades} | {l4} | {claim} | {runner} |".format(
                lane=lane_id,
                budget=report["budget"]["passed"],
                source=report["roles"]["source_like_measured"],
                sink=report["roles"]["sink_like_measured"],
                cascades=report["phase_cascade"]["n_detected_cascades"],
                l4=report["cycles"]["l4_cycle_requirement_met"],
                claim=report["claim_gate"]["positive_candidate_loop_claim_allowed"],
                runner=report["runtime_provenance"]["runner_mode"],
            )
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- JSON report: `{OUTPUT_PATH.relative_to(ROOT)}`",
            "- Time-series artifacts: `outputs/loop_observables_timeseries/*.jsonl`",
            "",
            "## Errors",
            "",
        ]
    )
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    total_steps = int(manifest["runner_config"]["total_steps"])
    node_count = int(manifest["fixtures"]["grc9v3_ported_ring_v1"]["node_count"])
    reports = {
        "U0_synthetic": _run_trace(
            manifest=manifest,
            lane_id="U0_synthetic",
            records=_null_trace(total_steps, node_count),
        ),
        "S_synthetic": _run_trace(
            manifest=manifest,
            lane_id="S_synthetic",
            records=_positive_trace(total_steps, node_count),
        ),
        "K_synthetic": _run_trace(
            manifest=manifest,
            lane_id="K_synthetic",
            records=_positive_trace(total_steps, node_count),
        ),
        "partial_cascade_synthetic": _run_trace(
            manifest=manifest,
            lane_id="partial_cascade_synthetic",
            records=_partial_cascade_trace(total_steps, node_count),
        ),
        "phase_scrambled_synthetic": _run_trace(
            manifest=manifest,
            lane_id="phase_scrambled_synthetic",
            records=_phase_scrambled_trace(total_steps, node_count),
        ),
        "budget_drift_synthetic": _run_trace(
            manifest=manifest,
            lane_id="budget_drift_synthetic",
            records=_budget_drift_trace(total_steps, node_count),
        ),
        "budget_drift_with_cascade_synthetic": _run_trace(
            manifest=manifest,
            lane_id="budget_drift_with_cascade_synthetic",
            records=_perfect_cascade_with_budget_drift_trace(total_steps, node_count),
        ),
    }
    errors = _validate_reports(reports)
    result = {
        "schema": "grc9v3_polarized_basin_loop_observable_smoke_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": (
            "python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
            "scripts/validate_loop_observables.py"
        ),
        "src_imports_or_changes_required": False,
        "errors": errors,
        "reports": reports,
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown_report(result)
    print(json.dumps({"status": result["status"], "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

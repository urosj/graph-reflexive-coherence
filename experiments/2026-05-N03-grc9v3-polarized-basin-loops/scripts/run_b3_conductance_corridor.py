#!/usr/bin/env python3
"""Run Branch B3 conductance-corridor diagnostics.

B3 tests whether fixed-topology channel structure helps source export survive
as directed flux.  It modifies only in-memory fixture conductance values and
keeps the experiment diagnostic-only.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)
from run_b1_diagnostic_sweeps import _run_fixed_topology_trace  # noqa: E402
from run_b2_channel_attenuation import _attenuation_metrics  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "b3_conductance_corridor_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "b3_conductance_corridor_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "b3_conductance_corridor_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "b3_conductance_corridor_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_b3_conductance_corridor.py"
)


def _boost_edges(
    fixture: dict[str, Any],
    *,
    edge_ids: Sequence[int],
    multiplier: float,
) -> None:
    selected = {int(edge_id) for edge_id in edge_ids}
    for edge in fixture["edges"]:
        if int(edge["edge_id"]) in selected:
            edge["base_conductance"] = float(edge.get("base_conductance", 1.0)) * multiplier


def _variant_manifest(
    base_manifest: Mapping[str, Any],
    *,
    variant_id: str,
    forward_multiplier: float = 1.0,
    return_multiplier: float = 1.0,
    source_exit_multiplier: float = 1.0,
    sink_entry_multiplier: float = 1.0,
) -> dict[str, Any]:
    manifest = copy.deepcopy(dict(base_manifest))
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    return_edges = [int(edge_id) for edge_id in masks["return_channel_edges"]]

    _boost_edges(fixture, edge_ids=forward_edges, multiplier=forward_multiplier)
    _boost_edges(fixture, edge_ids=return_edges, multiplier=return_multiplier)
    if forward_edges:
        _boost_edges(
            fixture,
            edge_ids=[forward_edges[0]],
            multiplier=source_exit_multiplier,
        )
        _boost_edges(
            fixture,
            edge_ids=[forward_edges[-1]],
            multiplier=sink_entry_multiplier,
        )

    fixture["variant_parameters"] = {
        "variant_id": variant_id,
        "forward_multiplier": forward_multiplier,
        "return_multiplier": return_multiplier,
        "source_exit_multiplier": source_exit_multiplier,
        "sink_entry_multiplier": sink_entry_multiplier,
    }
    manifest["diagnostic_branch"] = {
        "branch": "B3",
        "claim_ceiling": "conductance_corridor_diagnostic_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
        "variant_is_in_memory_only": True,
    }
    return manifest


def _apply_diagnostic_ceiling(report: dict[str, Any]) -> None:
    would_candidate = bool(report["claim_gate"]["positive_candidate_loop_claim_allowed"])
    blocked_reasons = list(report["claim_gate"].get("blocked_reasons", []))
    if "diagnostic_branch_claim_ceiling" not in blocked_reasons:
        blocked_reasons.append("diagnostic_branch_claim_ceiling")
    report["claim_gate"]["would_candidate_loop_claim_without_diagnostic_ceiling"] = would_candidate
    report["claim_gate"]["positive_candidate_loop_claim_allowed"] = False
    report["claim_gate"]["positive_full_loop_claim_allowed"] = False
    report["claim_gate"]["diagnostic_branch_claim_ceiling_applied"] = True
    report["claim_gate"]["blocked_reasons"] = blocked_reasons
    report["blocked_claims"] = blocked_reasons
    report["diagnostic_branch"] = {
        "branch": "B3",
        "claim_ceiling": "conductance_corridor_diagnostic_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
    }


def _budget_summary(
    *,
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    target = float(manifest["budget"]["total_budget"])
    errors = [
        abs(float(record["budget"]["after_correction"]) - target)
        for record in records
    ]
    corrections = [
        abs(float(record["budget"]["correction_magnitude"]))
        for record in records
    ]
    return {
        "target_budget": target,
        "max_abs_error_post_correction": max(errors, default=0.0),
        "max_correction_magnitude": max(corrections, default=0.0),
        "passed": max(errors, default=0.0) <= 1e-9,
    }


def _run_row(
    *,
    base_manifest: Mapping[str, Any],
    row_id: str,
    lane_id: str,
    variant_id: str,
    forward_multiplier: float = 1.0,
    return_multiplier: float = 1.0,
    source_exit_multiplier: float = 1.0,
    sink_entry_multiplier: float = 1.0,
) -> dict[str, Any]:
    manifest = _variant_manifest(
        base_manifest,
        variant_id=variant_id,
        forward_multiplier=forward_multiplier,
        return_multiplier=return_multiplier,
        source_exit_multiplier=source_exit_multiplier,
        sink_entry_multiplier=sink_entry_multiplier,
    )
    model, raw_records = _run_fixed_topology_trace(manifest=manifest, lane_id=lane_id)
    raw_path = RAW_RECORD_DIR / f"{row_id}_raw_records.jsonl"
    write_jsonl(raw_path, raw_records)
    rows = compute_observable_rows(
        manifest=manifest,
        records=raw_records,
        fixture_id="grc9v3_ported_ring_v1",
    )
    timeseries_path = TIMESERIES_DIR / f"{row_id}_timeseries.jsonl"
    write_jsonl(timeseries_path, rows)
    report = summarize_observables(
        manifest=manifest,
        rows=rows,
        lane_id=lane_id,
        fixture_id="grc9v3_ported_ring_v1",
        timeseries_path=timeseries_path,
        controls_status={
            "topology_disabled": "configured_and_audited_no_events",
            "zero_flux_reset": "not_applicable_fresh_transport_rebuild",
            "randomized_labels_posthoc": "not_run_b3",
            "shuffled_conductance": "not_run_b3_corridor_is_structured_runtime_variant",
            "budget_projection_disabled_dry_run": "not_run_b3",
        },
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    report["topology"]["final_node_count"] = final_node_count
    report["topology"]["final_edge_count"] = final_edge_count
    report["topology"]["changed"] = (
        int(report["topology"]["initial_node_count"]) != final_node_count
        or int(report["topology"]["initial_edge_count"]) != final_edge_count
    )
    report["topology"]["passed_fixed_topology_gate"] = not report["topology"]["changed"]
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["diagnostic_row"] = {
        "row_id": row_id,
        "lane_id": lane_id,
        "variant_id": variant_id,
        "forward_multiplier": forward_multiplier,
        "return_multiplier": return_multiplier,
        "source_exit_multiplier": source_exit_multiplier,
        "sink_entry_multiplier": sink_entry_multiplier,
    }
    report["attenuation"] = _attenuation_metrics(
        manifest=manifest,
        records=raw_records,
        observable_rows=rows,
    )
    report["budget"] = {
        **report["budget"],
        "diagnostic_budget_summary": _budget_summary(
            manifest=manifest,
            records=raw_records,
        ),
    }
    _apply_diagnostic_ceiling(report)
    return report


def _run_rows(base_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for multiplier in (1.5, 2.0, 4.0):
        variants.extend(
            [
                {
                    "variant_id": f"forward_x{multiplier:g}",
                    "forward_multiplier": multiplier,
                },
                {
                    "variant_id": f"return_x{multiplier:g}",
                    "return_multiplier": multiplier,
                },
                {
                    "variant_id": f"balanced_x{multiplier:g}",
                    "forward_multiplier": multiplier,
                    "return_multiplier": multiplier,
                },
            ]
        )
    variants.extend(
        [
            {
                "variant_id": "forward4_return1p5",
                "forward_multiplier": 4.0,
                "return_multiplier": 1.5,
            },
            {
                "variant_id": "forward1p5_return4",
                "forward_multiplier": 1.5,
                "return_multiplier": 4.0,
            },
            {
                "variant_id": "source_exit_sink_entry_x4",
                "source_exit_multiplier": 4.0,
                "sink_entry_multiplier": 4.0,
            },
        ]
    )

    rows: list[dict[str, Any]] = []
    for variant in variants:
        for lane_id in ("S", "K"):
            rows.append(
                _run_row(
                    base_manifest=base_manifest,
                    row_id=f"b3_{lane_id.lower()}_{variant['variant_id']}".replace(".", "p"),
                    lane_id=lane_id,
                    **variant,
                )
            )
    return rows


def _summarize(reports: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows = []
    promising = []
    for report in reports:
        row = report["diagnostic_row"]
        eval_window = report["attenuation"]["eval_window"]
        compact = {
            "row_id": row["row_id"],
            "lane_id": row["lane_id"],
            "variant_id": row["variant_id"],
            "source_like": report["roles"]["source_like_measured"],
            "sink_like": report["roles"]["sink_like_measured"],
            "raw_cycles": report["cycles"]["raw_cycle_count"],
            "role_gated_cycles": report["cycles"]["role_gated_cycle_count"],
            "would_candidate_loop_claim_without_diagnostic_ceiling": report["claim_gate"][
                "would_candidate_loop_claim_without_diagnostic_ceiling"
            ],
            "eval_last_over_first": eval_window["mean_abs_attenuation_last_over_first"],
            "eval_sink_import_over_source_export": eval_window[
                "sink_import_abs_over_source_export_abs"
            ],
            "max_correction_magnitude": report["budget"]["max_correction_magnitude"],
        }
        compact_rows.append(compact)
        if compact["role_gated_cycles"] or compact[
            "would_candidate_loop_claim_without_diagnostic_ceiling"
        ]:
            promising.append(compact)
    return {
        "row_count": len(reports),
        "promising_row_count": len(promising),
        "promising_rows": promising,
        "compact_rows": compact_rows,
        "positive_loop_claim_allowed": False,
        "interpretation": (
            "corridor_conditions_require_new_named_tranche"
            if promising
            else "conductance_corridor_did_not_create_role_gated_loop_evidence"
        ),
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for report in result["reports"]:
        row_id = report["diagnostic_row"]["row_id"]
        if report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a candidate claim")
        if report["claim_gate"]["positive_full_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a full loop claim")
        if report["topology"]["changed"]:
            errors.append(f"{row_id} changed topology")
        if not report["budget"]["passed"]:
            errors.append(f"{row_id} failed report budget audit")
        if not report["budget"]["diagnostic_budget_summary"]["passed"]:
            errors.append(f"{row_id} failed diagnostic budget audit")
    return errors


def _format_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6g}"


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch B3 Conductance Corridor Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "B3 is diagnostic-only. It tests fixed-topology in-memory conductance",
        "corridors and cannot promote a positive loop claim.",
        "",
        f"Rows: `{result['summary']['row_count']}`",
        f"Promising diagnostic rows: `{result['summary']['promising_row_count']}`",
        f"Interpretation: `{result['summary']['interpretation']}`",
        "",
        "## Compact Summary",
        "",
        "| Row | Lane | Variant | Source | Sink | Raw | Role-Gated | Would Claim | Eval Last/First | Eval Sink/Source | Max Correction |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {row_id} | {lane} | {variant} | {source} | {sink} | {raw} | {gated} | {would} | {lf} | {ss} | {corr} |".format(
                row_id=row["row_id"],
                lane=row["lane_id"],
                variant=row["variant_id"],
                source=row["source_like"],
                sink=row["sink_like"],
                raw=row["raw_cycles"],
                gated=row["role_gated_cycles"],
                would=row["would_candidate_loop_claim_without_diagnostic_ceiling"],
                lf=_format_float(row["eval_last_over_first"]),
                ss=_format_float(row["eval_sink_import_over_source_export"]),
                corr=_format_float(row["max_correction_magnitude"]),
            )
        )
    lines.extend(["", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    reports = _run_rows(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_b3_conductance_corridor_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "branch": "B3",
        "claim_ceiling": "conductance_corridor_diagnostic_not_positive_loop_claim",
        "reports": reports,
        "summary": _summarize(reports),
        "errors": [],
    }
    errors = _validate(result)
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "rows": result["summary"]["row_count"],
                "promising_rows": result["summary"]["promising_row_count"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

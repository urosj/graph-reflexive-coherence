#!/usr/bin/env python3
"""Run Branch B2 channel attenuation diagnostics.

This diagnostic asks whether source-region export survives across the
intermediate channel nodes as directed flux toward the sink.  It is
diagnostic-only and cannot promote a loop claim.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    write_json,
    write_jsonl,
)
from run_b1_diagnostic_sweeps import (  # noqa: E402
    _arc_edges,
    _run_fixed_topology_trace,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "b2_channel_attenuation_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "b2_channel_attenuation_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "b2_channel_attenuation_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "b2_channel_attenuation_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_b2_channel_attenuation.py"
)


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if abs(denominator) <= 1e-15:
        return None
    return numerator / denominator


def _ring_fixture_with_forward_gap(
    *,
    base_fixture: Mapping[str, Any],
    node_count: int,
    mask_width: int,
    forward_gap_nodes: int,
) -> dict[str, Any]:
    """Build a ring fixture where the source-to-sink gap is explicit."""

    sink_start = mask_width + forward_gap_nodes
    if sink_start + mask_width > node_count:
        raise ValueError("sink mask does not fit before ring wrap")
    source_nodes = list(range(mask_width))
    sink_nodes = list(range(sink_start, sink_start + mask_width))
    edges = [
        {
            "edge_id": edge_id,
            "node_u": edge_id,
            "port_u": 6,
            "node_v": (edge_id + 1) % node_count,
            "port_v": 4,
            "orientation": "clockwise",
            "base_conductance": 1.0,
            "geometric_length": 1.0,
            "flux_uv_initial": 0.0,
        }
        for edge_id in range(node_count)
    ]
    source_internal = list(range(max(0, mask_width - 1)))
    sink_internal = list(range(sink_start, sink_start + max(0, mask_width - 1)))
    forward_edges = _arc_edges(
        start_edge=source_nodes[-1],
        stop_node=sink_nodes[0],
        node_count=node_count,
    )
    return_edges = _arc_edges(
        start_edge=sink_nodes[-1],
        stop_node=source_nodes[0],
        node_count=node_count,
    )
    masks = dict(base_fixture["masks"])
    masks.update(
        {
            "source_aspect_nodes": source_nodes,
            "sink_aspect_nodes": sink_nodes,
            "forward_channel_edges": forward_edges,
            "return_channel_edges": return_edges,
            "source_internal_edges": source_internal,
            "sink_internal_edges": sink_internal,
            "parent_basin_nodes": list(range(node_count)),
            "same_parent_basin_mode": "configured_parent_region_only",
        }
    )
    fixture = dict(base_fixture)
    fixture.update(
        {
            "fixture_id": "grc9v3_ported_ring_v1",
            "node_count": node_count,
            "edge_count": node_count,
            "nodes": list(range(node_count)),
            "edges": edges,
            "masks": masks,
            "reversed_masks": {
                "source_aspect_nodes": sink_nodes,
                "sink_aspect_nodes": source_nodes,
                "forward_channel_edges": return_edges,
                "return_channel_edges": forward_edges,
                "source_internal_edges": sink_internal,
                "sink_internal_edges": source_internal,
            },
            "variant_parameters": {
                "node_count": node_count,
                "mask_width": mask_width,
                "forward_gap_nodes": forward_gap_nodes,
                "forward_edge_count": len(forward_edges),
                "return_edge_count": len(return_edges),
            },
        }
    )
    return fixture


def _variant_manifest(
    base_manifest: Mapping[str, Any],
    *,
    node_count: int,
    mask_width: int,
    forward_gap_nodes: int,
) -> dict[str, Any]:
    manifest = copy.deepcopy(dict(base_manifest))
    manifest["fixtures"]["grc9v3_ported_ring_v1"] = _ring_fixture_with_forward_gap(
        base_fixture=base_manifest["fixtures"]["grc9v3_ported_ring_v1"],
        node_count=node_count,
        mask_width=mask_width,
        forward_gap_nodes=forward_gap_nodes,
    )
    manifest["diagnostic_branch"] = {
        "branch": "B2",
        "claim_ceiling": "channel_attenuation_diagnostic_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
        "variant_is_in_memory_only": True,
    }
    return manifest


def _edge_series(
    records: Sequence[Mapping[str, Any]],
    *,
    edge_id: int,
    start_step: int,
    end_step: int,
) -> list[float]:
    return [
        float(record["flux_uv"].get(str(edge_id), 0.0))
        for record in records
        if start_step <= int(record["step_index"]) <= end_step
    ]


def _region_mass_series(
    records: Sequence[Mapping[str, Any]],
    *,
    nodes: Sequence[int],
    start_step: int,
    end_step: int,
) -> list[float]:
    node_ids = [str(node_id) for node_id in nodes]
    return [
        sum(float(record["C_post_budget"].get(node_id, 0.0)) for node_id in node_ids)
        for record in records
        if start_step <= int(record["step_index"]) <= end_step
    ]


def _attenuation_metrics(
    *,
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    observable_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    config = manifest["metric_config_defaults"]
    full_start = 0
    full_end = len(records) - 1
    early_start = 0
    early_end = min(29, full_end)
    eval_start = int(config["washout_steps"])
    eval_end = min(eval_start + int(config["min_eval_steps"]) - 1, full_end)

    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    source_nodes = [int(node_id) for node_id in masks["source_aspect_nodes"]]
    sink_nodes = [int(node_id) for node_id in masks["sink_aspect_nodes"]]
    channel_nodes = [
        node_id
        for node_id in range(int(fixture["node_count"]))
        if node_id not in set(source_nodes) and node_id not in set(sink_nodes)
    ]

    def _window_metrics(start_step: int, end_step: int) -> dict[str, Any]:
        edge_metrics: list[dict[str, Any]] = []
        for edge_id in forward_edges:
            series = _edge_series(
                records,
                edge_id=edge_id,
                start_step=start_step,
                end_step=end_step,
            )
            abs_series = [abs(value) for value in series]
            peak_index = max(range(len(abs_series)), key=abs_series.__getitem__) if abs_series else 0
            edge_metrics.append(
                {
                    "edge_id": edge_id,
                    "mean_flux": _mean(series),
                    "mean_abs_flux": _mean(abs_series),
                    "max_abs_flux": max(abs_series, default=0.0),
                    "peak_step": start_step + peak_index if series else None,
                }
            )
        first = edge_metrics[0] if edge_metrics else {"mean_abs_flux": 0.0, "max_abs_flux": 0.0}
        last = edge_metrics[-1] if edge_metrics else {"mean_abs_flux": 0.0, "max_abs_flux": 0.0}
        window_rows = [
            row
            for row in observable_rows
            if start_step <= int(row["step_index"]) <= end_step
        ]
        source_export_abs = _mean([abs(float(row["source_export"])) for row in window_rows])
        sink_import_abs = _mean([abs(float(row["sink_import"])) for row in window_rows])
        channel_mass = _region_mass_series(
            records,
            nodes=channel_nodes,
            start_step=start_step,
            end_step=end_step,
        )
        channel_initial = channel_mass[0] if channel_mass else 0.0
        return {
            "start_step": start_step,
            "end_step": end_step,
            "forward_edge_metrics": edge_metrics,
            "first_forward_edge_mean_abs_flux": first["mean_abs_flux"],
            "last_forward_edge_mean_abs_flux": last["mean_abs_flux"],
            "first_forward_edge_max_abs_flux": first["max_abs_flux"],
            "last_forward_edge_max_abs_flux": last["max_abs_flux"],
            "mean_abs_attenuation_last_over_first": _safe_ratio(
                float(last["mean_abs_flux"]),
                float(first["mean_abs_flux"]),
            ),
            "peak_abs_attenuation_last_over_first": _safe_ratio(
                float(last["max_abs_flux"]),
                float(first["max_abs_flux"]),
            ),
            "sink_import_abs_over_source_export_abs": _safe_ratio(
                sink_import_abs,
                source_export_abs,
            ),
            "source_export_abs_mean": source_export_abs,
            "sink_import_abs_mean": sink_import_abs,
            "channel_mass_initial": channel_initial,
            "channel_mass_final": channel_mass[-1] if channel_mass else 0.0,
            "channel_mass_max_abs_deviation": max(
                (abs(value - channel_initial) for value in channel_mass),
                default=0.0,
            ),
        }

    return {
        "full_window": _window_metrics(full_start, full_end),
        "early_window": _window_metrics(early_start, early_end),
        "eval_window": _window_metrics(eval_start, eval_end),
    }


def _run_row(
    *,
    base_manifest: Mapping[str, Any],
    row_id: str,
    lane_id: str,
    node_count: int,
    mask_width: int,
    forward_gap_nodes: int,
) -> dict[str, Any]:
    manifest = _variant_manifest(
        base_manifest,
        node_count=node_count,
        mask_width=mask_width,
        forward_gap_nodes=forward_gap_nodes,
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
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    budget_target = float(manifest["budget"]["total_budget"])
    post_budget_errors = [
        abs(float(record["budget"]["after_correction"]) - budget_target)
        for record in raw_records
    ]
    correction_magnitudes = [
        abs(float(record["budget"]["correction_magnitude"]))
        for record in raw_records
    ]
    return {
        "row_id": row_id,
        "lane_id": lane_id,
        "node_count": node_count,
        "mask_width": mask_width,
        "forward_gap_nodes": forward_gap_nodes,
        "forward_edge_count": len(
            manifest["fixtures"]["grc9v3_ported_ring_v1"]["masks"]["forward_channel_edges"]
        ),
        "return_edge_count": len(
            manifest["fixtures"]["grc9v3_ported_ring_v1"]["masks"]["return_channel_edges"]
        ),
        "raw_records": {"artifact_path": str(raw_path)},
        "timeseries": {"artifact_path": str(timeseries_path)},
        "topology": {
            "initial_node_count": node_count,
            "final_node_count": final_node_count,
            "initial_edge_count": node_count,
            "final_edge_count": final_edge_count,
            "changed": node_count != final_node_count or node_count != final_edge_count,
        },
        "budget": {
            "target_budget": budget_target,
            "max_abs_error_post_correction": max(post_budget_errors, default=0.0),
            "max_correction_magnitude": max(correction_magnitudes, default=0.0),
            "passed": max(post_budget_errors, default=0.0) <= 1e-9,
        },
        "attenuation": _attenuation_metrics(
            manifest=manifest,
            records=raw_records,
            observable_rows=rows,
        ),
        "claim_ceiling": "channel_attenuation_diagnostic_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
    }


def _run_rows(base_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    node_count = 16
    mask_width = 2
    for gap in (0, 1, 2, 4, 6):
        for lane_id in ("S", "K"):
            rows.append(
                _run_row(
                    base_manifest=base_manifest,
                    row_id=f"b2_{lane_id.lower()}_n{node_count}_gap{gap}",
                    lane_id=lane_id,
                    node_count=node_count,
                    mask_width=mask_width,
                    forward_gap_nodes=gap,
                )
            )
    return rows


def _summarize(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows = []
    for row in rows:
        early = row["attenuation"]["early_window"]
        eval_window = row["attenuation"]["eval_window"]
        compact_rows.append(
            {
                "row_id": row["row_id"],
                "lane_id": row["lane_id"],
                "forward_gap_nodes": row["forward_gap_nodes"],
                "forward_edge_count": row["forward_edge_count"],
                "early_last_over_first": early["mean_abs_attenuation_last_over_first"],
                "early_sink_import_over_source_export": early[
                    "sink_import_abs_over_source_export_abs"
                ],
                "eval_last_over_first": eval_window[
                    "mean_abs_attenuation_last_over_first"
                ],
                "eval_sink_import_over_source_export": eval_window[
                    "sink_import_abs_over_source_export_abs"
                ],
                "eval_channel_mass_max_abs_deviation": eval_window[
                    "channel_mass_max_abs_deviation"
                ],
            }
        )
    return {
        "row_count": len(rows),
        "node_count": 16,
        "interpretation": (
            "channel_attenuation_diagnostic_only; compare last/first forward "
            "edge flux and sink/source boundary ratios across gap lengths"
        ),
        "compact_rows": compact_rows,
        "positive_loop_claim_allowed": False,
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for row in result["rows"]:
        if row["positive_loop_claim_allowed"]:
            errors.append(f"{row['row_id']} promoted a positive claim")
        if row["topology"]["changed"]:
            errors.append(f"{row['row_id']} changed topology")
        if not row["budget"]["passed"]:
            errors.append(f"{row['row_id']} failed budget audit")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch B2 Channel Attenuation Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "This diagnostic asks whether source export survives across intermediate",
        "nodes as directed channel flux. It is not a positive loop-claim surface.",
        "",
        "## Compact Summary",
        "",
        "| Row | Lane | Gap Nodes | Forward Edges | Early Last/First | Early Sink/Source | Eval Last/First | Eval Sink/Source | Eval Channel Mass Dev |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {row_id} | {lane} | {gap} | {edges} | {early_lf} | {early_ss} | {eval_lf} | {eval_ss} | {mass} |".format(
                row_id=row["row_id"],
                lane=row["lane_id"],
                gap=row["forward_gap_nodes"],
                edges=row["forward_edge_count"],
                early_lf=_format_float(row["early_last_over_first"]),
                early_ss=_format_float(row["early_sink_import_over_source_export"]),
                eval_lf=_format_float(row["eval_last_over_first"]),
                eval_ss=_format_float(row["eval_sink_import_over_source_export"]),
                mass=_format_float(row["eval_channel_mass_max_abs_deviation"]),
            )
        )
    lines.extend(["", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6g}"


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    rows = _run_rows(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_b2_channel_attenuation_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "branch": "B2",
        "claim_ceiling": "channel_attenuation_diagnostic_not_positive_loop_claim",
        "rows": rows,
        "summary": _summarize(rows),
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
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

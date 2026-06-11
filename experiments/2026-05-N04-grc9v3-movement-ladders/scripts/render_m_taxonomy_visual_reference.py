#!/usr/bin/env python3
"""Render N04 M0-M6 visual reference artifacts.

The visuals are supporting references only. Movement claims come from the
existing N04 reports and validators, not from these rendered figures.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
VISUAL_ROOT = N04 / "outputs/m_taxonomy_visual_reference"
OUTPUT_PATH = N04 / "outputs/m_taxonomy_visual_reference.json"
REPORT_PATH = N04 / "reports/m_taxonomy_visual_reference.md"
NATIVE_TELEMETRY_ROOT = N04 / "outputs/m_taxonomy_native_lgrc_runs"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/render_m_taxonomy_visual_reference.py"
)

SCRIPTS = N04 / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_native_m6_same_fixture_validator as native_m6  # noqa: E402
from pygrc.telemetry import (  # noqa: E402
    EventTelemetryRow,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
    TelemetryArtifactPack,
    TelemetryExperimentReport,
    build_telemetry_artifact_layout,
    load_telemetry_artifact_pack,
    save_telemetry_artifact_pack,
)
from pygrc.visualization import DEFAULT_LGRC9V3_RUN_OBSERVABLES, render_run_visual_bundle  # noqa: E402
from pygrc.visualization.layout import build_run_visualization_layout  # noqa: E402


CLAIM_BOUNDARY = (
    "visual_reference_only_claims_come_from_n04_reports_not_from_visuals"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _coherence_matrix(rows: list[dict[str, Any]]) -> tuple[list[list[float]], list[float]]:
    matrix: list[list[float]] = []
    centroids: list[float] = []
    for row in rows:
        values = row.get("coherence_by_node")
        if not isinstance(values, dict):
            raise ValueError("timeseries row does not contain coherence_by_node")
        ordered = [float(values[str(index)]) for index in range(len(values))]
        matrix.append(ordered)
        centroids.append(float(row.get("centroid", 0.0)))
    return matrix, centroids


def _metric_series(rows: list[dict[str, Any]], keys: list[str]) -> dict[str, list[float]]:
    series: dict[str, list[float]] = {key: [] for key in keys}
    for row in rows:
        for key in keys:
            series[key].append(float(row.get(key, 0.0)))
    return series


def _color(value: float, minimum: float, maximum: float) -> str:
    if maximum <= minimum:
        fraction = 0.5
    else:
        fraction = max(0.0, min(1.0, (value - minimum) / (maximum - minimum)))
    # Blue -> white -> red, kept simple for SVG portability.
    if fraction < 0.5:
        local = fraction * 2.0
        red = int(245 * local)
        green = int(247 * local)
        blue = int(160 + 80 * local)
    else:
        local = (fraction - 0.5) * 2.0
        red = int(245 + 10 * local)
        green = int(247 * (1.0 - local) + 95 * local)
        blue = int(240 * (1.0 - local) + 95 * local)
    return f"#{red:02x}{green:02x}{blue:02x}"


def _polyline(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def _render_heatmap_svg(
    *,
    title: str,
    subtitle: str,
    matrix: list[list[float]],
    centroids: list[float],
    path: Path,
) -> None:
    width = 980
    height = 540
    left = 70
    top = 88
    heat_w = 820
    heat_h = 280
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 1
    values = [value for row in matrix for value in row]
    minimum = min(values) if values else 0.0
    maximum = max(values) if values else 1.0
    cell_w = heat_w / max(1, cols)
    cell_h = heat_h / max(1, rows)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="40" y="42" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="40" y="68" font-family="Arial, sans-serif" font-size="14" fill="#52606d">{html.escape(subtitle)}</text>',
        f'<rect x="{left}" y="{top}" width="{heat_w}" height="{heat_h}" fill="#ffffff" stroke="#cbd2d9"/>',
    ]
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            x = left + col_index * cell_w
            y = top + row_index * cell_h
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell_w + 0.1:.2f}" height="{cell_h + 0.1:.2f}" fill="{_color(value, minimum, maximum)}"/>'
            )
    parts.extend(
        [
            f'<text x="{left}" y="{top + heat_h + 24}" font-family="Arial, sans-serif" font-size="12" fill="#52606d">node index -></text>',
            f'<text x="20" y="{top + heat_h / 2:.2f}" font-family="Arial, sans-serif" font-size="12" fill="#52606d" transform="rotate(-90 20,{top + heat_h / 2:.2f})">time / step</text>',
        ]
    )
    plot_top = 410
    plot_h = 82
    plot_w = heat_w
    if centroids:
        c_min = min(centroids)
        c_max = max(centroids)
        if math.isclose(c_min, c_max):
            c_min -= 0.5
            c_max += 0.5
        points = []
        for index, centroid in enumerate(centroids):
            x = left + (plot_w * index / max(1, len(centroids) - 1))
            y = plot_top + plot_h - ((centroid - c_min) / (c_max - c_min) * plot_h)
            points.append((x, y))
        parts.extend(
            [
                f'<rect x="{left}" y="{plot_top}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#cbd2d9"/>',
                f'<polyline points="{_polyline(points)}" fill="none" stroke="#1f7a8c" stroke-width="3"/>',
                f'<text x="{left}" y="{plot_top - 10}" font-family="Arial, sans-serif" font-size="13" fill="#1f2933">centroid trace ({c_min:.4f} to {c_max:.4f})</text>',
            ]
        )
    parts.append("</svg>")
    _write_text(path, "\n".join(parts) + "\n")


def _render_metric_svg(
    *,
    title: str,
    subtitle: str,
    series: dict[str, list[float]],
    path: Path,
) -> None:
    width = 980
    height = 540
    left = 80
    top = 100
    plot_w = 800
    plot_h = 330
    colors = ["#1f7a8c", "#d1495b", "#edae49", "#2f7d32", "#5b5f97", "#7f5539"]
    all_values = [value for values in series.values() for value in values]
    minimum = min(all_values) if all_values else 0.0
    maximum = max(all_values) if all_values else 1.0
    if math.isclose(minimum, maximum):
        minimum -= 0.5
        maximum += 0.5
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="40" y="42" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="40" y="68" font-family="Arial, sans-serif" font-size="14" fill="#52606d">{html.escape(subtitle)}</text>',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#cbd2d9"/>',
    ]
    legend_y = top + plot_h + 38
    for series_index, (key, values) in enumerate(series.items()):
        if not values:
            continue
        points = []
        for index, value in enumerate(values):
            x = left + plot_w * index / max(1, len(values) - 1)
            y = top + plot_h - ((value - minimum) / (maximum - minimum) * plot_h)
            points.append((x, y))
        color = colors[series_index % len(colors)]
        parts.append(
            f'<polyline points="{_polyline(points)}" fill="none" stroke="{color}" stroke-width="3"/>'
        )
        parts.append(
            f'<rect x="{left + series_index * 150}" y="{legend_y - 12}" width="14" height="14" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{left + 20 + series_index * 150}" y="{legend_y}" font-family="Arial, sans-serif" font-size="12" fill="#1f2933">{html.escape(key)}</text>'
        )
    parts.append("</svg>")
    _write_text(path, "\n".join(parts) + "\n")


def _render_card_svg(*, title: str, lines: list[str], path: Path) -> None:
    width = 980
    height = 540
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="40" y="50" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
    ]
    y = 98
    for line in lines:
        parts.append(
            f'<text x="54" y="{y}" font-family="Arial, sans-serif" font-size="18" fill="#1f2933">{html.escape(line)}</text>'
        )
        y += 34
    parts.append("</svg>")
    _write_text(path, "\n".join(parts) + "\n")


def _native_m6_replay(direction: str) -> tuple[list[list[float]], list[float]]:
    if direction == "forward":
        source = native_m6.FORWARD_SOURCE
        target = native_m6.FORWARD_TARGET
        expected_polarity = "positive"
    elif direction == "reversed":
        source = native_m6.REVERSED_SOURCE
        target = native_m6.REVERSED_TARGET
        expected_polarity = "negative"
    else:
        raise ValueError(f"unknown direction {direction!r}")

    state, edges = native_m6._s0_chain_state()
    model = native_m6.LGRC9V3.from_state(state, native_m6._params())
    edge_id = edges[(source, target)]
    matrix = [native_m6._node_vector(model)]
    centroids = [native_m6._centroid(matrix[-1])]

    model.schedule_packet_departure(
        source_node_id=source,
        target_node_id=target,
        edge_id=edge_id,
        amount=native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    native_m6._process_queue(model)
    matrix.append(native_m6._node_vector(model))
    centroids.append(native_m6._centroid(matrix[-1]))

    for _cycle_index in range(native_m6.SELF_RENEWED_CYCLE_MIN):
        feedback_row = model.emit_feedback_eligibility_surface_row(
            front_node_ids=native_m6.FRONT_MASK,
            rear_node_ids=native_m6.REAR_MASK,
            reference_delta=0.0,
            feedback_threshold=native_m6.FEEDBACK_THRESHOLD,
            expected_next_route_id=f"s0-native-m6-{direction}",
            expected_next_channel_id=f"edge:{edge_id}",
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=source,
            target_node_id=target,
            edge_id=edge_id,
            threshold=native_m6.FEEDBACK_THRESHOLD,
            packet_amount=native_m6.FEEDBACK_PACKET_AMOUNT,
            expected_polarity=expected_polarity,
            expected_source_surface_digest=feedback_row.surface_values_after[
                "source_surface_digest"
            ],
            expected_next_route_id=f"s0-native-m6-{direction}",
            expected_next_channel_id=f"edge:{edge_id}",
        )
        model.produce_events(
            policy=(
                native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
        native_m6._process_queue(model)
        matrix.append(native_m6._node_vector(model))
        centroids.append(native_m6._centroid(matrix[-1]))
    return matrix, centroids


def _identity(run_id: str, seed_name: str, requested_steps: int) -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="LGRC9V3",
        params_identity="n04_m_taxonomy_visual_reference_v1",
        seed_name=seed_name,
        seed_source_reference="N04 Iteration 11 visual reference",
        seed_path=None,
        param_family="native_causal_pulse_substrate_surface",
        rng_seed=0,
        requested_steps=requested_steps,
    )


def _event_row(
    identity: RunTelemetryIdentity,
    *,
    step_index: int,
    event_index: int,
    event_kind: str,
    payload: dict[str, Any],
) -> EventTelemetryRow:
    return EventTelemetryRow(
        identity=identity,
        step_index=step_index,
        event_index=event_index,
        event_kind=event_kind,
        source_family="LGRC9V3",
        payload=payload,
        family_extensions={"lgrc9v3": payload},
    )


def _step_row(
    identity: RunTelemetryIdentity,
    *,
    step_index: int,
    time: float,
    event_count: int,
    event_counts_by_kind: dict[str, int],
    observables: dict[str, Any],
    extensions: dict[str, Any],
) -> StepTelemetryRow:
    return StepTelemetryRow(
        identity=identity,
        step_index=step_index,
        time=time,
        event_count=event_count,
        event_counts_by_kind=event_counts_by_kind,
        observables=observables,
        family_extensions={"lgrc9v3": extensions},
    )


def _summary(
    identity: RunTelemetryIdentity,
    step_rows: list[StepTelemetryRow],
    event_rows: list[EventTelemetryRow],
    *,
    raw_params: dict[str, Any],
    extensions: dict[str, Any],
) -> RunTelemetrySummary:
    event_counts: dict[str, int] = {}
    for row in event_rows:
        event_counts[row.event_kind] = event_counts.get(row.event_kind, 0) + 1
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=len(step_rows),
        final_step_index=step_rows[-1].step_index,
        initial_time=step_rows[0].time,
        final_time=step_rows[-1].time,
        total_event_count=len(event_rows),
        event_counts_by_kind=event_counts,
        initial_observables=dict(step_rows[0].observables),
        final_observables=dict(step_rows[-1].observables),
        resolved_params=raw_params,
        raw_params=raw_params,
        parameter_overrides={},
        family_extensions={"lgrc9v3": extensions},
    )


def _report(
    identity: RunTelemetryIdentity,
    summary: RunTelemetrySummary,
    *,
    changed_observables: list[str],
    extra_common: dict[str, Any],
    extensions: dict[str, Any],
) -> TelemetryExperimentReport:
    return TelemetryExperimentReport(
        family="LGRC9V3",
        common={
            "run_id": identity.run_id,
            "seed_name": identity.seed_name,
            "param_family": identity.param_family,
            "completed_steps": summary.completed_steps,
            "total_event_count": summary.total_event_count,
            "changed_observables": changed_observables,
            "params_identity": identity.params_identity,
            "resolved_params": dict(summary.resolved_params),
            "event_counts_by_kind": dict(summary.event_counts_by_kind),
            "checkpoint_overview": {},
            **extra_common,
        },
        extensions={"lgrc9v3": extensions},
    )


def _save_and_render_native_pack(
    *,
    run_id: str,
    step_rows: list[StepTelemetryRow],
    event_rows: list[EventTelemetryRow],
    run_summary: RunTelemetrySummary,
    report: TelemetryExperimentReport,
) -> dict[str, str]:
    layout = build_telemetry_artifact_layout(run_id, root_dir=NATIVE_TELEMETRY_ROOT)
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
    )
    pack = TelemetryArtifactPack(
        layout=layout,
        step_rows=tuple(step_rows),
        event_rows=tuple(event_rows),
        run_summary=run_summary,
        experiment_report=report,
    )
    visualization_layout = build_run_visualization_layout(
        layout,
        visualization_root=VISUAL_ROOT / "native_lgrc_visualizations",
    )
    render_run_visual_bundle(
        pack,
        report=report,
        layout=visualization_layout,
        observables=(
            "conserved_budget_total",
            "in_flight_packet_total",
            "event_queue_length",
            "packet_count",
            "event_time_key",
            "family_extensions.lgrc9v3.centroid",
            "family_extensions.lgrc9v3.boundary_coupling_score",
            "family_extensions.lgrc9v3.feedback_cycle_index",
        ),
    )
    loaded = load_telemetry_artifact_pack(layout)
    if len(loaded.step_rows) != len(step_rows) or len(loaded.event_rows) != len(event_rows):
        raise RuntimeError("native telemetry pack did not round-trip expected rows")
    return {
        "telemetry_run_dir": _rel(layout.run_dir),
        "telemetry_step_rows": _rel(layout.step_rows_path),
        "telemetry_event_rows": _rel(layout.event_rows_path),
        "telemetry_run_summary": _rel(layout.run_summary_path),
        "trajectory_figure": _rel(visualization_layout.trajectory_figure_path),
        "event_timeline": _rel(visualization_layout.event_timeline_path),
        "report_panel": _rel(visualization_layout.report_panel_path),
    }


def _build_native_m5_pack() -> dict[str, str]:
    rows = _read_jsonl(
        N04
        / "outputs/reversed_e3_pulse_boundary_timeseries/P3_true_reversed_e3_pulse_boundary_coupling.jsonl"
    )
    identity = _identity("n04_m5_true_reversed_e3_boundary_response", "M5 true reversed E3", len(rows))
    step_rows: list[StepTelemetryRow] = []
    event_rows: list[EventTelemetryRow] = []
    for index, row in enumerate(rows):
        event_count = 1 if float(row.get("pulse_signal", 0.0)) > 0.0 else 0
        event_counts = {"native_e3_boundary_contact": event_count} if event_count else {}
        step_rows.append(
            _step_row(
                identity,
                step_index=index,
                time=float(row.get("time", index)),
                event_count=event_count,
                event_counts_by_kind=event_counts,
                observables={
                    "conserved_budget_total": float(row.get("total_budget", 0.0)),
                    "in_flight_packet_total": float(row.get("pulse_signal", 0.0)),
                    "event_queue_length": 0,
                    "packet_count": event_count,
                    "event_time_key": float(row.get("event_time_key", row.get("time", index))),
                    "budget_error": 0.0,
                },
                extensions={
                    "centroid": float(row.get("centroid", 0.0)),
                    "boundary_coupling_score": float(row.get("coupling_amount", 0.0)),
                    "front_mass": float(row.get("front_mass", 0.0)),
                    "rear_mass": float(row.get("rear_mass", 0.0)),
                    "pulse_signal": float(row.get("pulse_signal", 0.0)),
                    "feedback_cycle_index": -1,
                },
            )
        )
        if event_count:
            event_rows.append(
                _event_row(
                    identity,
                    step_index=index,
                    event_index=len(event_rows),
                    event_kind="native_e3_boundary_contact",
                    payload={
                        "source_e3_direction": row.get("source_e3_direction"),
                        "source_e3_label": row.get("source_e3_label"),
                        "coupling_amount": row.get("coupling_amount"),
                    },
                )
            )
    summary = _summary(
        identity,
        step_rows,
        event_rows,
        raw_params={"runtime_family": "LGRC9V3", "source": "true_reversed_e3_boundary_timeseries"},
        extensions={"claim_ceiling": "m5_direction_parity_supported_boundary_response"},
    )
    report = _report(
        identity,
        summary,
        changed_observables=["centroid", "boundary_coupling_score"],
        extra_common={"fixture_name": "S0_chain_v1"},
        extensions={"claim_boundary": CLAIM_BOUNDARY, "native_m6": False},
    )
    return _save_and_render_native_pack(
        run_id=identity.run_id,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        report=report,
    )


def _build_native_m6_pack() -> dict[str, str]:
    identity = _identity("n04_m6_native_same_fixture_self_renewal", "M6 native same-fixture", 4)
    matrix, centroids = _native_m6_replay("forward")
    step_rows: list[StepTelemetryRow] = []
    event_rows: list[EventTelemetryRow] = []
    for index, values in enumerate(matrix):
        event_count = 1 if index > 0 else 0
        event_kind = (
            "seeded_packet_contact"
            if index == 1
            else "feedback_authorized_regenerated_packet"
            if index > 1
            else "initial_state"
        )
        event_counts = {event_kind: event_count} if event_count else {}
        step_rows.append(
            _step_row(
                identity,
                step_index=index,
                time=float(index),
                event_count=event_count,
                event_counts_by_kind=event_counts,
                observables={
                    "conserved_budget_total": sum(values),
                    "in_flight_packet_total": 0.0,
                    "event_queue_length": 0,
                    "packet_count": event_count,
                    "event_time_key": float(index),
                    "budget_error": 0.0,
                },
                extensions={
                    "centroid": centroids[index],
                    "boundary_coupling_score": 0.0 if index == 0 else native_m6.FEEDBACK_PACKET_AMOUNT,
                    "feedback_cycle_index": index - 1,
                    "node_coherence_min": min(values),
                    "node_coherence_max": max(values),
                },
            )
        )
        if event_count:
            event_rows.append(
                _event_row(
                    identity,
                    step_index=index,
                    event_index=len(event_rows),
                    event_kind=event_kind,
                    payload={
                        "regenerated_pulse_source": (
                            "seeded_first_contact" if index == 1 else "feedback_eligibility"
                        ),
                        "copied_from_original_schedule": False if index > 1 else None,
                    },
                )
            )
    summary = _summary(
        identity,
        step_rows,
        event_rows,
        raw_params={
            "runtime_family": "LGRC9V3",
            "execution_surface": "native_causal_pulse_substrate_surface",
        },
        extensions={"claim_ceiling": "native_m6_same_fixture_self_renewal_candidate"},
    )
    report = _report(
        identity,
        summary,
        changed_observables=["centroid", "feedback_cycle_index"],
        extra_common={"fixture_name": "S0_chain_v1"},
        extensions={"claim_boundary": CLAIM_BOUNDARY, "native_m6_candidate": True},
    )
    return _save_and_render_native_pack(
        run_id=identity.run_id,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        report=report,
    )


def _build_visuals() -> list[dict[str, Any]]:
    VISUAL_ROOT.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    def add_record(**record: Any) -> None:
        path = Path(record["visual_path"])
        record["visual_sha256"] = _sha256_file(path)
        for visual_key in ("native_trajectory_figure", "native_event_timeline", "native_report_panel"):
            if visual_key in record:
                record[f"{visual_key}_sha256"] = _sha256_file(Path(record[visual_key]))
        record["claim_boundary"] = CLAIM_BOUNDARY
        records.append(record)

    m0_rows = _read_jsonl(N04 / "outputs/fixed_substrate_tranche_a_timeseries/S0_chain_v1_B1.jsonl")
    matrix, centroids = _coherence_matrix(m0_rows)
    m0_path = VISUAL_ROOT / "M0_fixed_substrate_subthreshold_bias.svg"
    _render_heatmap_svg(
        title="M0: fixed-substrate subthreshold directional bias",
        subtitle="S0 B1 remains below threshold; direction signal is diagnostic only.",
        matrix=matrix,
        centroids=centroids,
        path=m0_path,
    )
    add_record(
        rung="M0",
        label="fixed_substrate_subthreshold_bias",
        evidence_status="real_timeseries_existing_n04",
        implementation_surface="experiment_local_fixed_substrate",
        visual_path=_rel(m0_path),
        source_artifacts=[
            "outputs/fixed_substrate_tranche_a_timeseries/S0_chain_v1_B1.jsonl",
            "outputs/fixed_substrate_tranche_a_report.json",
        ],
        claim_ceiling="no_movement_response_candidates",
    )

    m1_rows = _read_jsonl(N04 / "outputs/movement_observables_timeseries/S0_chain_v1_basin_replacement.jsonl")
    matrix, centroids = _coherence_matrix(m1_rows)
    m1_path = VISUAL_ROOT / "M1_apparent_centroid_identity_blocked.svg"
    _render_heatmap_svg(
        title="M1: apparent centroid displacement",
        subtitle="Basin replacement moves the centroid but fails identity continuity.",
        matrix=matrix,
        centroids=centroids,
        path=m1_path,
    )
    add_record(
        rung="M1",
        label="apparent_centroid_displacement_identity_blocked",
        evidence_status="real_timeseries_existing_n04",
        implementation_surface="experiment_local_observable_fixture",
        visual_path=_rel(m1_path),
        source_artifacts=[
            "outputs/movement_observables_timeseries/S0_chain_v1_basin_replacement.jsonl",
            "outputs/movement_classifier_m0_m3_validation.json",
        ],
        claim_ceiling="M1_apparent_centroid_displacement_evidence_only",
    )

    m2 = _read_json(N04 / "outputs/m2_runtime_shape_blocked_fixture.json")
    m2_rows = _read_jsonl(
        N04 / "outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl"
    )
    matrix, centroids = _coherence_matrix(m2_rows)
    m2_path = VISUAL_ROOT / "M2_boundary_reassignment_shape_blocked.svg"
    _render_heatmap_svg(
        title="M2: boundary reassignment, shape blocked",
        subtitle=(
            "Runtime fixture: displacement, identity, and boundary pass; "
            "profile gate blocks M3."
        ),
        matrix=matrix,
        centroids=centroids,
        path=m2_path,
    )
    add_record(
        rung="M2",
        label="boundary_reassignment_shape_blocked",
        evidence_status="runtime_timeseries_existing_n04",
        implementation_surface="iteration_11b_runtime_shape_blocked_fixture",
        visual_path=_rel(m2_path),
        source_artifacts=[
            "outputs/m2_runtime_shape_blocked_fixture.json",
            "outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl",
            "outputs/movement_classifier_m0_m3_validation.json",
        ],
        claim_ceiling="M2_identity_preserving_displacement_evidence_only",
    )

    m3_rows = _read_jsonl(N04 / "outputs/movement_observables_timeseries/S0_chain_v1_shape_preserving_shift.jsonl")
    matrix, centroids = _coherence_matrix(m3_rows)
    m3_path = VISUAL_ROOT / "M3_shape_preserving_identity_displacement.svg"
    _render_heatmap_svg(
        title="M3: shape-preserving identity displacement",
        subtitle="Classifier fixture passes identity and shape/profile gates.",
        matrix=matrix,
        centroids=centroids,
        path=m3_path,
    )
    add_record(
        rung="M3",
        label="shape_preserving_identity_displacement",
        evidence_status="real_timeseries_existing_n04",
        implementation_surface="experiment_local_observable_fixture",
        visual_path=_rel(m3_path),
        source_artifacts=[
            "outputs/movement_observables_timeseries/S0_chain_v1_shape_preserving_shift.jsonl",
            "outputs/movement_classifier_m0_m3_validation.json",
        ],
        claim_ceiling="M3_shape_preserving_identity_displacement_evidence_only",
    )

    m4_rows = _read_jsonl(N04 / "outputs/boundary_coupled_pulse_timeseries/P2_asymmetric_boundary_coupling_forward.jsonl")
    m4_path = VISUAL_ROOT / "M4_boundary_coupled_response.svg"
    _render_metric_svg(
        title="M4: coordinated boundary response",
        subtitle="State-mediated boundary coupling; movement claims remain blocked.",
        series=_metric_series(
            m4_rows,
            ["centroid", "front_mass", "rear_mass", "coupling_amount", "pulse_signal"],
        ),
        path=m4_path,
    )
    add_record(
        rung="M4",
        label="coordinated_front_rear_boundary_response",
        evidence_status="real_timeseries_existing_n04",
        implementation_surface="boundary_coupled_pulse_fixture",
        visual_path=_rel(m4_path),
        source_artifacts=[
            "outputs/boundary_coupled_pulse_timeseries/P2_asymmetric_boundary_coupling_forward.jsonl",
            "outputs/boundary_coupled_pulse_report.json",
        ],
        claim_ceiling="boundary_coupled_pulse_fixture_validation",
    )

    native_m5 = _build_native_m5_pack()
    m5_forward = _read_jsonl(N04 / "outputs/boundary_coupled_pulse_timeseries/P2_asymmetric_boundary_coupling_forward.jsonl")
    m5_reverse = _read_jsonl(N04 / "outputs/reversed_e3_pulse_boundary_timeseries/P3_true_reversed_e3_pulse_boundary_coupling.jsonl")
    m5_path = VISUAL_ROOT / "M5_direction_parity_boundary_response.svg"
    _render_metric_svg(
        title="M5: direction-parity repeated boundary response",
        subtitle="Forward and true reversed E3 lanes have opposite signed centroid response.",
        series={
            "forward_centroid": [float(row.get("centroid", 0.0)) for row in m5_forward],
            "reversed_centroid": [float(row.get("centroid", 0.0)) for row in m5_reverse],
            "forward_coupling": [float(row.get("coupling_amount", 0.0)) for row in m5_forward],
            "reversed_coupling": [float(row.get("coupling_amount", 0.0)) for row in m5_reverse],
        },
        path=m5_path,
    )
    add_record(
        rung="M5",
        label="direction_parity_supported_boundary_response",
        evidence_status="native_lgrc9v3_telemetry_pack_plus_reference_svg",
        implementation_surface="native_lgrc9v3_true_reversed_e3_boundary_response",
        visual_path=_rel(m5_path),
        native_telemetry_run_dir=native_m5["telemetry_run_dir"],
        native_trajectory_figure=native_m5["trajectory_figure"],
        native_event_timeline=native_m5["event_timeline"],
        native_report_panel=native_m5["report_panel"],
        source_artifacts=[
            native_m5["telemetry_step_rows"],
            native_m5["telemetry_event_rows"],
            native_m5["telemetry_run_summary"],
            "outputs/reversed_e3_pulse_m4_m5_classification.json",
            "outputs/reversed_e3_pulse_boundary_timeseries/P3_true_reversed_e3_pulse_boundary_coupling.jsonl",
        ],
        claim_ceiling="m5_direction_parity_supported_boundary_response",
    )

    native_m6_pack = _build_native_m6_pack()
    m6_matrix, m6_centroids = _native_m6_replay("forward")
    m6_path = VISUAL_ROOT / "M6_native_same_fixture_self_renewal.svg"
    _render_heatmap_svg(
        title="M6: native same-fixture self-renewal candidate",
        subtitle="Native LGRC9V3 replay: seed contact followed by feedback-renewed packet work.",
        matrix=m6_matrix,
        centroids=m6_centroids,
        path=m6_path,
    )
    add_record(
        rung="M6",
        label="native_same_fixture_self_renewal_candidate",
        evidence_status="native_lgrc9v3_telemetry_pack_plus_reference_svg",
        implementation_surface="native_causal_pulse_substrate_surface",
        visual_path=_rel(m6_path),
        native_telemetry_run_dir=native_m6_pack["telemetry_run_dir"],
        native_trajectory_figure=native_m6_pack["trajectory_figure"],
        native_event_timeline=native_m6_pack["event_timeline"],
        native_report_panel=native_m6_pack["report_panel"],
        source_artifacts=[
            native_m6_pack["telemetry_step_rows"],
            native_m6_pack["telemetry_event_rows"],
            native_m6_pack["telemetry_run_summary"],
            "outputs/native_m6_same_fixture_validator.json",
            "outputs/native_m6_validation_checklist_audit.json",
        ],
        claim_ceiling="native_m6_same_fixture_self_renewal_candidate",
    )

    return records


def _write_index(records: list[dict[str, Any]]) -> Path:
    index_path = VISUAL_ROOT / "index.html"
    cards = []
    for record in records:
        native_bits = ""
        if "native_trajectory_figure" in record:
            native_bits = (
                f"<p><strong>Native LGRC figures:</strong> "
                f"<code>{html.escape(record['native_trajectory_figure'])}</code>, "
                f"<code>{html.escape(record['native_event_timeline'])}</code></p>"
            )
        cards.append(
            "\n".join(
                [
                    '<section class="card">',
                    f"<h2>{html.escape(record['rung'])}: {html.escape(record['label'])}</h2>",
                    f"<p><strong>Surface:</strong> {html.escape(record['implementation_surface'])}</p>",
                    f"<p><strong>Status:</strong> {html.escape(record['evidence_status'])}</p>",
                    f"<img src=\"{html.escape(Path(record['visual_path']).name)}\" alt=\"{html.escape(record['rung'])} visual\"/>",
                    native_bits,
                    f"<p><strong>Claim ceiling:</strong> <code>{html.escape(record['claim_ceiling'])}</code></p>",
                    "</section>",
                ]
            )
        )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>N04 M0-M6 Visual Reference</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; background: #f7f7f4; color: #1f2933; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 18px; }}
.card {{ background: white; border: 1px solid #d9e2ec; padding: 16px; }}
img {{ width: 100%; height: auto; border: 1px solid #d9e2ec; }}
code {{ background: #f0f4f8; padding: 2px 4px; }}
</style>
</head>
<body>
<h1>N04 M0-M6 Visual Reference</h1>
<p>Visuals are supporting references only. Claims come from the N04 reports and validators.</p>
<div class="grid">
{''.join(cards)}
</div>
</body>
</html>
"""
    _write_text(index_path, html_text)
    return index_path


def _build_report(records: list[dict[str, Any]], index_path: Path) -> dict[str, Any]:
    return {
        "schema": "movement_ladder_visual_reference_v1",
        "report_kind": "n04_m_taxonomy_visual_reference_v1",
        "status": "passed",
        "claim_boundary": CLAIM_BOUNDARY,
        "visual_root": _rel(VISUAL_ROOT),
        "index_html": _rel(index_path),
        "records": records,
        "gaps": [
            {
                "rung": "M0-M4",
                "gap": (
                    "M0-M4 reference panels use N04 JSONL/reference SVGs; "
                    "only M5 and M6 currently have generated native LGRC telemetry "
                    "packs rendered through the standard pygrc visualization stack."
                ),
                "recommended_next": (
                    "Add native/standard telemetry-pack adapters for M0-M4 if the "
                    "sharing pack needs uniform LGRC visualization provenance."
                ),
            }
        ],
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "rev_parse_head": _run_git(["rev-parse", "HEAD"]),
            "diff_check": _run_git(["diff", "--check"]),
            "status_short": _run_git(["status", "--short"]),
        },
    }


def _write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# N04 M0-M6 Visual Reference",
        "",
        f"Status: `{payload['status']}`",
        "",
        "These visuals are supporting references only. They do not promote claims.",
        "",
        f"Index: `{payload['index_html']}`",
        "",
        "## Records",
        "",
        "| Rung | Label | Surface | Status | Visual | Native LGRC figure |",
        "|---|---|---|---|---|---|",
    ]
    for record in payload["records"]:
        native_figure = record.get("native_trajectory_figure", "")
        lines.append(
            "| "
            f"`{record['rung']}` | `{record['label']}` | "
            f"`{record['implementation_surface']}` | "
            f"`{record['evidence_status']}` | `{record['visual_path']}` | "
            f"`{native_figure}` |"
        )
    lines.extend(["", "## Gaps", ""])
    for gap in payload["gaps"]:
        lines.append(f"- `{gap['rung']}`: {gap['gap']} {gap['recommended_next']}")
    _write_text(REPORT_PATH, "\n".join(lines) + "\n")


def main() -> None:
    records = _build_visuals()
    index_path = _write_index(records)
    payload = _build_report(records, index_path)
    _write_json(OUTPUT_PATH, payload)
    _write_json(VISUAL_ROOT / "manifest.json", payload)
    _write_markdown(payload)


if __name__ == "__main__":
    main()

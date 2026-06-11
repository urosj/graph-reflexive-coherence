"""Experiment-local loop observables for polarized basin loops.

This module intentionally does not import `src/pygrc`.  It consumes the
experiment fixture manifest and per-step records, then emits auditable loop
evidence.  The goal is to keep the first polarity-loop measurement surface
separate from core GRC9V3 runtime semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence


REQUIRED_REPORT_KEYS = {
    "schema",
    "experiment_id",
    "fixture_id",
    "lane_id",
    "metric_config",
    "runtime_provenance",
    "evaluation_window",
    "topology",
    "budget",
    "roles",
    "flux",
    "closure",
    "phase_lock",
    "phase_cascade",
    "cycles",
    "timeseries",
    "controls_status",
    "claim_gate",
    "claim_ceiling",
    "ladder",
    "blocked_claims",
}

PHASE_LOCK_FORMULA = (
    "best Pearson correlation over nonnegative lags between "
    "-Delta C_source and Delta C_sink, and between -Delta C_sink and "
    "Delta C_source; score is the maximum positive pairwise value"
)

PHASE_CASCADE_FORMULA = (
    "count ordered windows satisfying source_drop -> forward_flux -> "
    "sink_rise -> return_flux -> source_refill using configured theta_mass, "
    "theta_export, theta_import, phase_cascade_score_min, and n_cycles_min"
)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from `path`."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    """Write deterministic JSON to `path`."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    """Write deterministic JSON Lines to `path`."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_fixture(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the canonical GRC9V3 ported-ring fixture."""

    return manifest["fixtures"]["grc9v3_ported_ring_v1"]


def fixture_edges(fixture: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    """Return canonical fixture edges keyed by integer edge id."""

    return {int(edge["edge_id"]): edge for edge in fixture["edges"]}


def metric_config(manifest: Mapping[str, Any]) -> dict[str, float | int]:
    """Return a copy of metric defaults used by the observable library."""

    return dict(manifest["metric_config_defaults"])


def _int_key_value(mapping: Mapping[Any, Any], key: int, default: float = 0.0) -> float:
    if key in mapping:
        return float(mapping[key])
    text_key = str(key)
    if text_key in mapping:
        return float(mapping[text_key])
    return default


def _series_mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _safe_ratio(value: float, scale: float) -> float:
    if scale <= 0.0:
        return 0.0
    return value / scale


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


def region_mass(coherence: Mapping[Any, Any], nodes: Iterable[int]) -> float:
    """Sum coherence over a node region."""

    return sum(_int_key_value(coherence, int(node_id)) for node_id in nodes)


def oriented_flux_from_region_node(edge: Mapping[str, Any], local_node: int, flux_uv: float) -> float:
    """Return edge flux oriented out of `local_node`.

    The manifest convention is `flux_uv > 0` from `node_u` to `node_v`.
    For a boundary node on the `node_v` side, export is therefore `-flux_uv`.
    """

    node_u = int(edge["node_u"])
    node_v = int(edge["node_v"])
    if local_node == node_u:
        return flux_uv
    if local_node == node_v:
        return -flux_uv
    raise ValueError(f"node {local_node} is not incident to edge {edge}")


def region_export(
    *,
    edges: Mapping[int, Mapping[str, Any]],
    flux_uv: Mapping[Any, Any],
    region_nodes: Iterable[int],
) -> float:
    """Compute net boundary export from a region from edge-level flux."""

    region = {int(node_id) for node_id in region_nodes}
    total = 0.0
    for edge_id, edge in edges.items():
        node_u = int(edge["node_u"])
        node_v = int(edge["node_v"])
        u_inside = node_u in region
        v_inside = node_v in region
        if u_inside == v_inside:
            continue
        local_node = node_u if u_inside else node_v
        total += oriented_flux_from_region_node(
            edge,
            local_node,
            _int_key_value(flux_uv, int(edge_id)),
        )
    return total


def channel_flux(edge_ids: Iterable[int], flux_uv: Mapping[Any, Any]) -> float:
    """Sum manifest-oriented channel flux values."""

    return sum(_int_key_value(flux_uv, int(edge_id)) for edge_id in edge_ids)


def compute_observable_rows(
    *,
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    fixture_id: str = "grc9v3_ported_ring_v1",
) -> list[dict[str, Any]]:
    """Compute per-step loop observables from raw per-step records."""

    fixture = manifest["fixtures"][fixture_id]
    edges = fixture_edges(fixture)
    masks = fixture["masks"]
    source_nodes = [int(node_id) for node_id in masks["source_aspect_nodes"]]
    sink_nodes = [int(node_id) for node_id in masks["sink_aspect_nodes"]]
    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    return_edges = [int(edge_id) for edge_id in masks["return_channel_edges"]]
    budget_total = float(manifest["budget"]["total_budget"])

    rows: list[dict[str, Any]] = []
    for record in records:
        step_index = int(record["step_index"])
        c_pre = record["C_pre"]
        c_post_continuity = record["C_post_continuity"]
        c_post_budget = record["C_post_budget"]
        flux_uv = record["flux_uv"]
        budget_record = record.get("budget", {})

        source_pre = region_mass(c_pre, source_nodes)
        sink_pre = region_mass(c_pre, sink_nodes)
        source_post_continuity = region_mass(c_post_continuity, source_nodes)
        sink_post_continuity = region_mass(c_post_continuity, sink_nodes)
        source_post_budget = region_mass(c_post_budget, source_nodes)
        sink_post_budget = region_mass(c_post_budget, sink_nodes)
        source_export = region_export(edges=edges, flux_uv=flux_uv, region_nodes=source_nodes)
        sink_export = region_export(edges=edges, flux_uv=flux_uv, region_nodes=sink_nodes)

        budget_before = float(
            budget_record.get("before_continuity", sum(float(value) for value in c_pre.values()))
        )
        budget_after_continuity = float(
            budget_record.get(
                "after_continuity",
                sum(float(value) for value in c_post_continuity.values()),
            )
        )
        budget_after_correction = float(
            budget_record.get(
                "after_correction",
                sum(float(value) for value in c_post_budget.values()),
            )
        )

        rows.append(
            {
                "step_index": step_index,
                "C_source": source_post_budget,
                "C_sink": sink_post_budget,
                "C_source_pre": source_pre,
                "C_sink_pre": sink_pre,
                "C_source_post_continuity": source_post_continuity,
                "C_sink_post_continuity": sink_post_continuity,
                "Delta_C_source_pre_budget": source_post_continuity - source_pre,
                "Delta_C_sink_pre_budget": sink_post_continuity - sink_pre,
                "Delta_C_source_post_budget": source_post_budget - source_pre,
                "Delta_C_sink_post_budget": sink_post_budget - sink_pre,
                "source_export": source_export,
                "sink_import": -sink_export,
                "J_forward": channel_flux(forward_edges, flux_uv),
                "J_return": channel_flux(return_edges, flux_uv),
                "budget_before_continuity": budget_before,
                "budget_after_continuity": budget_after_continuity,
                "budget_error_pre_correction": budget_after_continuity - budget_total,
                "budget_after_correction": budget_after_correction,
                "budget_error_post_correction": budget_after_correction - budget_total,
                "budget_correction_method": str(budget_record.get("correction_method", "none")),
                "budget_correction_magnitude": float(
                    budget_record.get("correction_magnitude", 0.0)
                ),
                "simplex_projection_applied": bool(
                    budget_record.get("simplex_projection_applied", False)
                ),
                "uniform_shift_applied": bool(
                    budget_record.get("uniform_shift_applied", False)
                ),
            }
        )
    return rows


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mean_x = fmean(xs)
    mean_y = fmean(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denom_x = math.sqrt(sum(value * value for value in dx))
    denom_y = math.sqrt(sum(value * value for value in dy))
    if denom_x == 0.0 or denom_y == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(dx, dy)) / (denom_x * denom_y)


def _best_lagged_correlation(
    xs: Sequence[float],
    ys: Sequence[float],
    *,
    max_lag: int,
) -> tuple[float, int]:
    best_corr = 0.0
    best_lag = 0
    if not xs or not ys:
        return best_corr, best_lag
    limit = min(max_lag, len(xs) - 2, len(ys) - 2)
    for lag in range(max(0, limit) + 1):
        corr = _pearson(xs[: len(xs) - lag], ys[lag:]) if lag else _pearson(xs, ys)
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
    return best_corr, best_lag


def compute_phase_lock(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_lag: int = 20,
) -> dict[str, Any]:
    """Compute the first pairwise phase-lock metric."""

    source_drop = [-float(row["Delta_C_source_pre_budget"]) for row in rows]
    sink_rise = [float(row["Delta_C_sink_pre_budget"]) for row in rows]
    sink_drop = [-float(row["Delta_C_sink_pre_budget"]) for row in rows]
    source_rise = [float(row["Delta_C_source_pre_budget"]) for row in rows]
    source_to_sink, source_to_sink_lag = _best_lagged_correlation(
        source_drop,
        sink_rise,
        max_lag=max_lag,
    )
    sink_to_source, sink_to_source_lag = _best_lagged_correlation(
        sink_drop,
        source_rise,
        max_lag=max_lag,
    )
    score = max(0.0, source_to_sink, sink_to_source)
    return {
        "formula": PHASE_LOCK_FORMULA,
        "max_lag": max_lag,
        "smoothing": "none",
        "sign_convention": "-Delta_C_source leads Delta_C_sink; -Delta_C_sink leads Delta_C_source",
        "score": score,
        "source_drop_to_sink_rise_correlation": source_to_sink,
        "source_drop_to_sink_rise_lag": source_to_sink_lag,
        "sink_drop_to_source_rise_correlation": sink_to_source,
        "sink_drop_to_source_rise_lag": sink_to_source_lag,
    }


def compute_phase_cascade(
    rows: Sequence[Mapping[str, Any]],
    *,
    theta_mass: float,
    theta_export: float,
    theta_import: float,
    n_cycles_min: int,
    max_stage_lag: int = 20,
) -> dict[str, Any]:
    """Count ordered source/forward/sink/return/refill cascades."""

    steps = [int(row["step_index"]) for row in rows]

    def _indices(predicate: Any) -> list[int]:
        return [index for index, row in enumerate(rows) if predicate(row)]

    source_drop = _indices(lambda row: float(row["Delta_C_source_pre_budget"]) < -theta_mass)
    forward = _indices(lambda row: float(row["J_forward"]) > theta_export)
    sink_rise = _indices(lambda row: float(row["Delta_C_sink_pre_budget"]) > theta_mass)
    return_flux = _indices(lambda row: float(row["J_return"]) > theta_import)
    source_refill = _indices(lambda row: float(row["Delta_C_source_pre_budget"]) > theta_mass)

    consumed_refills: set[int] = set()
    cascades: list[dict[str, Any]] = []
    lag_records: list[tuple[int, int, int, int]] = []
    for first in source_drop:
        stages: list[int] = [first]
        cursor = first
        for candidates in (forward, sink_rise, return_flux, source_refill):
            next_index = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate > cursor
                    and candidate - cursor <= max_stage_lag
                    and (candidates is not source_refill or candidate not in consumed_refills)
                ),
                None,
            )
            if next_index is None:
                stages = []
                break
            stages.append(next_index)
            cursor = next_index
        if len(stages) != 5:
            continue
        consumed_refills.add(stages[-1])
        lags = (
            stages[1] - stages[0],
            stages[2] - stages[1],
            stages[3] - stages[2],
            stages[4] - stages[3],
        )
        lag_records.append(lags)
        cascades.append(
            {
                "source_drop_step": steps[stages[0]],
                "forward_flux_step": steps[stages[1]],
                "sink_rise_step": steps[stages[2]],
                "return_flux_step": steps[stages[3]],
                "source_refill_step": steps[stages[4]],
            }
        )

    def _mean_lag(position: int) -> float:
        return _series_mean([float(lags[position]) for lags in lag_records])

    count = len(cascades)
    return {
        "formula": PHASE_CASCADE_FORMULA,
        "max_stage_lag": max_stage_lag,
        "event_detection_rule": {
            "source_drop": "Delta_C_source_pre_budget < -theta_mass",
            "forward_flux": "J_forward > theta_export",
            "sink_rise": "Delta_C_sink_pre_budget > theta_mass",
            "return_flux": "J_return > theta_import",
            "source_refill": "Delta_C_source_pre_budget > theta_mass",
        },
        "smoothing": "none",
        "sign_convention": "return flux is manifest-clockwise positive channel flux",
        "n_detected_cascades": count,
        "score": _clip01(_safe_ratio(float(count), float(n_cycles_min))),
        "n_cycles_min": n_cycles_min,
        "passed_cycle_requirement": count >= n_cycles_min,
        "mean_lag_source_drop_to_forward_flux": _mean_lag(0),
        "mean_lag_forward_flux_to_sink_rise": _mean_lag(1),
        "mean_lag_sink_rise_to_return_flux": _mean_lag(2),
        "mean_lag_return_flux_to_source_refill": _mean_lag(3),
        "cascades": cascades,
    }


def path_closure_evidence(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Check static path closure properties from the fixture masks."""

    masks = fixture["masks"]
    all_edges = {int(edge["edge_id"]) for edge in fixture["edges"]}
    forward_edges = {int(edge_id) for edge_id in masks["forward_channel_edges"]}
    return_edges = {int(edge_id) for edge_id in masks["return_channel_edges"]}
    source_internal = {int(edge_id) for edge_id in masks.get("source_internal_edges", [])}
    sink_internal = {int(edge_id) for edge_id in masks.get("sink_internal_edges", [])}
    source_nodes = {int(node_id) for node_id in masks["source_aspect_nodes"]}
    sink_nodes = {int(node_id) for node_id in masks["sink_aspect_nodes"]}
    closed_edge_cover = forward_edges | return_edges | source_internal | sink_internal
    passed = (
        bool(forward_edges)
        and bool(return_edges)
        and not (forward_edges & return_edges)
        and not (source_nodes & sink_nodes)
        and closed_edge_cover == all_edges
    )
    return {
        "passed": passed,
        "forward_return_edge_sets_disjoint": not bool(forward_edges & return_edges),
        "source_sink_masks_disjoint": not bool(source_nodes & sink_nodes),
        "closed_route_edge_cover_complete": closed_edge_cover == all_edges,
        "evidence_source": "fixture_manifest_masks",
    }


def summarize_observables(
    *,
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    lane_id: str,
    fixture_id: str,
    timeseries_path: Path,
    controls_status: Mapping[str, Any] | None = None,
    runtime_provenance_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the schema-compatible run report object for one trace."""

    fixture = manifest["fixtures"][fixture_id]
    config = metric_config(manifest)
    washout_steps = int(config["washout_steps"])
    min_eval_steps = int(config["min_eval_steps"])
    theta_export = float(config["theta_export"])
    theta_import = float(config["theta_import"])
    theta_mass = float(config["theta_mass"])
    phase_lock_min = float(config["phase_lock_min"])
    phase_cascade_score_min = float(config["phase_cascade_score_min"])
    phase_lock_max_lag = int(config["phase_lock_max_lag"])
    phase_cascade_max_stage_lag = int(config["phase_cascade_max_stage_lag"])
    n_cycles_min = int(config["n_cycles_min"])

    eval_rows = [row for row in rows if int(row["step_index"]) >= washout_steps]
    eval_rows = eval_rows[:min_eval_steps] if len(eval_rows) >= min_eval_steps else eval_rows
    eval_window_start = int(eval_rows[0]["step_index"]) if eval_rows else None
    eval_window_end = int(eval_rows[-1]["step_index"]) if eval_rows else None

    source_export_values = [float(row["source_export"]) for row in eval_rows]
    sink_import_values = [float(row["sink_import"]) for row in eval_rows]
    forward_values = [float(row["J_forward"]) for row in eval_rows]
    return_values = [float(row["J_return"]) for row in eval_rows]

    source_exporting_deltas = [
        float(row["Delta_C_source_pre_budget"])
        for row in eval_rows
        if float(row["source_export"]) > theta_export
    ]
    sink_importing_deltas = [
        float(row["Delta_C_sink_pre_budget"])
        for row in eval_rows
        if float(row["sink_import"]) > theta_import
    ]
    source_delta_when_exporting = _series_mean(source_exporting_deltas)
    sink_delta_when_importing = _series_mean(sink_importing_deltas)

    mean_source_export = _series_mean(source_export_values)
    mean_sink_import = _series_mean(sink_import_values)
    mean_forward_flux = _series_mean(forward_values)
    mean_return_flux = _series_mean(return_values)
    source_like = (
        mean_source_export > theta_export
        and source_delta_when_exporting < -theta_mass
    )
    sink_like = (
        mean_sink_import > theta_import
        and sink_delta_when_importing > theta_mass
    )

    path_closure = path_closure_evidence(fixture)
    flux_closure_passed = mean_return_flux > theta_import
    phase_lock = compute_phase_lock(eval_rows, max_lag=phase_lock_max_lag)
    phase_lock["passed"] = phase_lock["score"] >= phase_lock_min
    phase_cascade = compute_phase_cascade(
        eval_rows,
        theta_mass=theta_mass,
        theta_export=theta_export,
        theta_import=theta_import,
        n_cycles_min=n_cycles_min,
        max_stage_lag=phase_cascade_max_stage_lag,
    )
    phase_cascade["passed"] = (
        phase_cascade["score"] >= phase_cascade_score_min
        and phase_cascade["passed_cycle_requirement"]
    )
    role_gated_cascade_count = (
        int(phase_cascade["n_detected_cascades"]) if source_like and sink_like else 0
    )
    role_gated_cascade_passed = role_gated_cascade_count >= n_cycles_min

    budget_errors_pre = [abs(float(row["budget_error_pre_correction"])) for row in rows]
    budget_errors_post = [abs(float(row["budget_error_post_correction"])) for row in rows]
    correction_magnitudes = [abs(float(row["budget_correction_magnitude"])) for row in rows]
    simplex_projection_count = sum(1 for row in rows if bool(row["simplex_projection_applied"]))
    uniform_shift_count = sum(1 for row in rows if bool(row["uniform_shift_applied"]))
    budget_passed = max(budget_errors_post, default=0.0) <= 1e-9

    node_count = int(fixture["node_count"])
    edge_count = int(fixture["edge_count"])
    topology_events_enabled = bool(manifest["scope"]["topology_events_enabled"])
    runtime_provenance = {
        "model_family": manifest["scope"]["model_family"],
        "runner_mode": manifest["scope"]["runner_mode"],
        "called_methods": list(manifest["runner_config"]["runner_sequence"]),
        "topology_events_enabled": topology_events_enabled,
        "spark_enabled": bool(manifest["controls"]["topology_disabled"]["spark_enabled"]),
        "growth_enabled": bool(manifest["controls"]["topology_disabled"]["growth_enabled"]),
        "boundary_behavior_enabled": bool(
            manifest["controls"]["topology_disabled"]["boundary_behavior_enabled"]
        ),
        "birth_enabled": bool(manifest["controls"]["topology_disabled"]["birth_enabled"]),
        "pruning_enabled": bool(manifest["controls"]["topology_disabled"]["pruning_enabled"]),
        "runtime_semantics_changed": False,
        "src_changes_required": False,
    }
    if runtime_provenance_override is not None:
        runtime_provenance.update(dict(runtime_provenance_override))
    runtime_evidence_gate_passed = runtime_provenance["runner_mode"] != "synthetic_trace_validator"
    full_l_positive_allowed = fixture["masks"]["same_parent_basin_mode"] == "flux_successor_basin"
    candidate_claim_allowed = (
        budget_passed
        and source_like
        and sink_like
        and bool(path_closure["passed"])
        and bool(phase_cascade["passed"])
        and runtime_evidence_gate_passed
    )
    gate_status = {
        "budget_gate": budget_passed,
        "topology_gate": True,
        "role_gate": source_like and sink_like,
        "path_closure_gate": bool(path_closure["passed"]),
        "flux_closure_gate": flux_closure_passed,
        "phase_cascade_gate": bool(phase_cascade["passed"]),
        "cycle_gate": bool(phase_cascade["passed_cycle_requirement"]),
        "runtime_evidence_gate": runtime_evidence_gate_passed,
        "same_parent_basin_gate": full_l_positive_allowed,
    }
    blocked_reasons: list[str] = []
    if not budget_passed:
        blocked_reasons.append("budget_gate_failed")
    if not gate_status["topology_gate"]:
        blocked_reasons.append("topology_gate_failed")
    if not gate_status["role_gate"]:
        blocked_reasons.append("role_gate_failed")
    if not gate_status["path_closure_gate"]:
        blocked_reasons.append("path_closure_gate_failed")
    if not gate_status["flux_closure_gate"]:
        blocked_reasons.append("flux_closure_gate_failed")
    if not gate_status["phase_cascade_gate"]:
        blocked_reasons.append("phase_cascade_gate_failed")
    if not gate_status["cycle_gate"]:
        blocked_reasons.append("cycle_gate_failed")
    if not runtime_evidence_gate_passed:
        blocked_reasons.append("synthetic_trace_not_runtime_evidence")
    if not full_l_positive_allowed:
        blocked_reasons.append("same_parent_basin_evidence_configured_only")

    ladder_level = "L0"
    gates_passed: list[str] = []
    gates_failed: list[str] = []
    for gate_name, passed in gate_status.items():
        (gates_passed if passed else gates_failed).append(gate_name)
    if budget_passed and gate_status["path_closure_gate"]:
        ladder_level = "L1"
    if budget_passed and gate_status["role_gate"]:
        ladder_level = "L2"
    if budget_passed and gate_status["role_gate"] and gate_status["flux_closure_gate"]:
        ladder_level = "L3"
    if (
        budget_passed
        and gate_status["role_gate"]
        and gate_status["path_closure_gate"]
        and gate_status["phase_cascade_gate"]
        and gate_status["cycle_gate"]
    ):
        ladder_level = "L4"

    primary_scientific_blocker = next(
        (
            reason
            for reason in blocked_reasons
            if reason
            not in {
                "synthetic_trace_not_runtime_evidence",
                "same_parent_basin_evidence_configured_only",
            }
        ),
        None,
    )
    controls = controls_status or {
        "topology_disabled": "configured",
        "shuffled_conductance": "not_run_iteration_3",
        "zero_flux_reset": "not_run_iteration_3",
        "budget_projection_disabled_dry_run": "not_run_iteration_3",
        "randomized_labels_posthoc": "not_run_iteration_3",
    }

    report = {
        "schema": "grc9v3_polarized_basin_loop_report_v1",
        "experiment_id": manifest["experiment_id"],
        "fixture_id": fixture_id,
        "lane_id": lane_id,
        "metric_config": config,
        "runtime_provenance": runtime_provenance,
        "evaluation_window": {
            "start_step": eval_window_start,
            "end_step": eval_window_end,
            "washout_steps": washout_steps,
            "min_eval_steps": min_eval_steps,
            "actual_eval_steps": len(eval_rows),
            "rule": "step_index >= washout_steps, then first min_eval_steps rows",
        },
        "topology": {
            "initial_node_count": node_count,
            "final_node_count": node_count,
            "initial_edge_count": edge_count,
            "final_edge_count": edge_count,
            "changed": False,
            "passed_fixed_topology_gate": True,
            "topology_event_count": 0,
            "blocked_topology_event_kinds": [],
        },
        "budget": {
            "target_budget": float(manifest["budget"]["total_budget"]),
            "max_abs_error_pre_correction": max(budget_errors_pre, default=0.0),
            "max_abs_error_post_correction": max(budget_errors_post, default=0.0),
            "max_correction_magnitude": max(correction_magnitudes, default=0.0),
            "mean_correction_magnitude": _series_mean(correction_magnitudes),
            "simplex_projection_count": simplex_projection_count,
            "uniform_shift_count": uniform_shift_count,
            "passed": budget_passed,
            "correction_method": "per_step_recorded",
        },
        "roles": {
            "source_export_mean": mean_source_export,
            "sink_import_mean": mean_sink_import,
            "source_delta_c_pre_budget_when_exporting_mean": source_delta_when_exporting,
            "sink_delta_c_pre_budget_when_importing_mean": sink_delta_when_importing,
            "source_delta_c_post_budget_mean": _series_mean(
                [float(row["Delta_C_source_post_budget"]) for row in eval_rows]
            ),
            "sink_delta_c_post_budget_mean": _series_mean(
                [float(row["Delta_C_sink_post_budget"]) for row in eval_rows]
            ),
            "source_like_measured": source_like,
            "sink_like_measured": sink_like,
            "source_sink_role_measurement_source": "edge_level_flux_uv_and_pre_budget_mass_change",
            "reversal_outcome": "not_run_iteration_3",
        },
        "flux": {
            "J_forward_mean": mean_forward_flux,
            "J_return_mean": mean_return_flux,
            "J_forward_max": max(forward_values, default=0.0),
            "J_return_max": max(return_values, default=0.0),
            "source_export_series_mean": mean_source_export,
            "sink_import_series_mean": mean_sink_import,
            "orientation": "manifest_clockwise_flux_uv_positive",
            "forward_return_balance": mean_forward_flux - mean_return_flux,
        },
        "closure": {
            "path_closure": path_closure,
            "flux_closure": {
                "passed": flux_closure_passed,
                "mean_return_flux": mean_return_flux,
                "theta_import": theta_import,
            },
            "polarity_score": _clip01(
                min(
                    _safe_ratio(mean_source_export, theta_export),
                    _safe_ratio(mean_sink_import, theta_import),
                    1.0,
                )
            ),
            "closure_score": _clip01(
                min(
                    _safe_ratio(mean_forward_flux, theta_export),
                    _safe_ratio(mean_return_flux, theta_import),
                    1.0,
                )
            ),
        },
        "phase_lock": phase_lock,
        "phase_cascade": phase_cascade,
        "cycles": {
            "cycle_count": int(phase_cascade["n_detected_cascades"]),
            "raw_cycle_count": int(phase_cascade["n_detected_cascades"]),
            "role_gated_cycle_count": role_gated_cascade_count,
            "n_cycles_min": n_cycles_min,
            "l4_cycle_requirement_met": bool(phase_cascade["passed_cycle_requirement"]),
            "role_gated_cycle_requirement_met": role_gated_cascade_passed,
        },
        "timeseries": {
            "artifact_path": str(timeseries_path),
            "artifact_sha256": sha256_file(timeseries_path) if timeseries_path.exists() else None,
            "fields": [
                "C_source",
                "C_sink",
                "J_forward",
                "J_return",
                "source_export",
                "sink_import",
                "Delta_C_source_pre_budget",
                "Delta_C_sink_pre_budget",
                "Delta_C_source_post_budget",
                "Delta_C_sink_post_budget",
                "budget_error_pre_correction",
                "budget_error_post_correction",
            ],
        },
        "controls_status": dict(controls),
        "claim_gate": {
            "budget_gate_passed": budget_passed,
            "topology_gate_passed": True,
            "role_gate_passed": source_like and sink_like,
            "path_closure_gate_passed": bool(path_closure["passed"]),
            "flux_closure_gate_passed": flux_closure_passed,
            "phase_cascade_gate_passed": bool(phase_cascade["passed"]),
            "cycle_gate_passed": bool(phase_cascade["passed_cycle_requirement"]),
            "role_gated_cycle_gate_passed": role_gated_cascade_passed,
            "runtime_evidence_gate_passed": runtime_evidence_gate_passed,
            "positive_candidate_loop_claim_allowed": candidate_claim_allowed,
            "positive_full_loop_claim_allowed": candidate_claim_allowed and full_l_positive_allowed,
            "blocked_reasons": blocked_reasons,
            "primary_scientific_blocker": primary_scientific_blocker,
            "blocked_reason": (
                "synthetic_trace_not_runtime_evidence"
                if not runtime_evidence_gate_passed
                else "budget_gate_failed"
                if not budget_passed
                else "same_parent_basin_evidence_configured_only"
                if candidate_claim_allowed and not full_l_positive_allowed
                else None
            ),
        },
        "claim_ceiling": {
            "same_parent_basin_mode": fixture["masks"]["same_parent_basin_mode"],
            "full_l_positive_allowed": full_l_positive_allowed,
            "fixture_allows_candidate_claims": True,
            "candidate_loop_claim_allowed": True,
            "naming_note": "candidate_loop_claim_allowed is a fixture ceiling, not an actual positive claim; use claim_gate.positive_candidate_loop_claim_allowed for the actual result",
        },
        "ladder": {
            "level": ladder_level,
            "gates_passed": gates_passed,
            "gates_failed": gates_failed,
            "schema_status": "pre_iteration_6_shape_classifier",
        },
        "blocked_claims": blocked_reasons,
    }
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        raise ValueError(f"report object is missing required fields: {missing}")
    return report

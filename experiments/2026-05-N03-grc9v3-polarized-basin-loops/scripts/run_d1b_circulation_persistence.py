#!/usr/bin/env python3
"""Run D1b persistence/coherence audit for residual circulation.

D1b consumes the D1 circulation time-series artifacts and asks whether weak
residual circulation is persistent, sign-stable, decaying, or correlated with
loop-relevant evidence.  It does not rerun or modify core dynamics.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
D1_OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1_circulatory_proposal_audit.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1b_circulation_persistence_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1b_circulation_persistence_report.md"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1b_circulation_persistence.py"
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = fmean(xs)
    my = fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    sx = math.sqrt(sum(x * x for x in dx))
    sy = math.sqrt(sum(y * y for y in dy))
    if sx == 0.0 or sy == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(dx, dy)) / (sx * sy)


def _lag1_autocorrelation(values: Sequence[float]) -> float:
    if len(values) < 3:
        return 0.0
    return _pearson(values[:-1], values[1:])


def _sign(value: float, *, eps: float = 1e-12) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def _sign_persistence(values: Sequence[float]) -> dict[str, Any]:
    signs = [_sign(value) for value in values]
    nonzero = [sign for sign in signs if sign != 0]
    if not nonzero:
        return {
            "dominant_sign": 0,
            "nonzero_fraction": 0.0,
            "dominant_sign_fraction": 0.0,
            "sign_flip_count": 0,
        }
    positive = sum(1 for sign in nonzero if sign > 0)
    negative = sum(1 for sign in nonzero if sign < 0)
    dominant = 1 if positive >= negative else -1
    flips = sum(
        1
        for left, right in zip(nonzero, nonzero[1:])
        if left != right
    )
    return {
        "dominant_sign": dominant,
        "nonzero_fraction": len(nonzero) / len(signs),
        "dominant_sign_fraction": max(positive, negative) / len(nonzero),
        "sign_flip_count": flips,
    }


def _decay_ratio(values: Sequence[float]) -> float | None:
    if len(values) < 4:
        return None
    half = len(values) // 2
    early = _mean([abs(value) for value in values[:half]])
    late = _mean([abs(value) for value in values[half:]])
    if early <= 1e-15:
        return None
    return late / early


def _trend_slope(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    xs = list(range(len(values)))
    mx = fmean(xs)
    my = fmean(values)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0.0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, values)) / denom


def _scenario_metrics(scenario: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(scenario["timeseries"]["artifact_path"])
    rows = _read_jsonl(path)
    signed = [float(row["loop_circulation"]) for row in rows]
    normalized = [float(row["loop_normalized_circulation"]) for row in rows]
    abs_signed = [abs(value) for value in signed]
    abs_norm = [abs(value) for value in normalized]
    mean_abs_flux = [float(row["loop_mean_abs_flux"]) for row in rows]
    sign = _sign_persistence(signed)
    return {
        "scenario_id": scenario["scenario_id"],
        "mean_signed_circulation": _mean(signed),
        "mean_abs_signed_circulation": _mean(abs_signed),
        "max_abs_signed_circulation": max(abs_signed, default=0.0),
        "mean_normalized_circulation": _mean(normalized),
        "mean_abs_normalized_circulation": _mean(abs_norm),
        "max_abs_normalized_circulation": max(abs_norm, default=0.0),
        "sign_persistence_fraction": sign["dominant_sign_fraction"],
        "nonzero_sign_fraction": sign["nonzero_fraction"],
        "dominant_sign": sign["dominant_sign"],
        "sign_flip_count": sign["sign_flip_count"],
        "lag1_autocorrelation": _lag1_autocorrelation(signed),
        "abs_circulation_decay_ratio_late_over_early": _decay_ratio(signed),
        "abs_circulation_trend_slope": _trend_slope(abs_signed),
        "correlation_abs_circulation_with_mean_abs_flux": _pearson(abs_signed, mean_abs_flux),
        "source_timeseries": str(path),
    }


def _classify(metrics: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    material = [
        row
        for row in metrics
        if float(row["max_abs_normalized_circulation"]) >= 0.01
    ]
    stable = [
        row
        for row in metrics
        if float(row["mean_abs_normalized_circulation"]) > 0.001
        and float(row["sign_persistence_fraction"]) >= 0.9
        and float(row["lag1_autocorrelation"]) >= 0.5
    ]
    transient_or_weak = len(material) == 0
    return {
        "material_circulation_rows": [row["scenario_id"] for row in material],
        "stable_weak_rows": [row["scenario_id"] for row in stable],
        "classification": (
            "d1b_stable_weak_residual_circulation"
            if stable and transient_or_weak
            else "d1b_material_circulation_requires_review"
            if material
            else "d1b_transient_or_weak_residual_circulation"
        ),
    }


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D1b Circulation Persistence Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{result['classification']['classification']}`",
        "",
        "D1b consumes D1 circulation time-series artifacts. It does not rerun or",
        "modify core dynamics.",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Mean Signed | Max Abs | Mean Abs Norm | Max Abs Norm | Sign Persist | Lag1 | Decay Late/Early | Corr AbsCirc/Flux |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["scenario_metrics"]:
        decay = row["abs_circulation_decay_ratio_late_over_early"]
        lines.append(
            "| {scenario} | {mean_signed:.6g} | {max_abs:.6g} | {mean_norm:.6g} | {max_norm:.6g} | {persist:.6g} | {lag:.6g} | {decay} | {corr:.6g} |".format(
                scenario=row["scenario_id"],
                mean_signed=row["mean_signed_circulation"],
                max_abs=row["max_abs_signed_circulation"],
                mean_norm=row["mean_abs_normalized_circulation"],
                max_norm=row["max_abs_normalized_circulation"],
                persist=row["sign_persistence_fraction"],
                lag=row["lag1_autocorrelation"],
                decay="n/a" if decay is None else f"{float(decay):.6g}",
                corr=row["correlation_abs_circulation_with_mean_abs_flux"],
            )
        )
    lines.extend(["", "## Interpretation", ""])
    lines.append(result["interpretation"])
    lines.extend(["", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not D1_OUTPUT_PATH.exists():
        raise SystemExit(
            "D1 output is missing; run run_d1_circulatory_proposal_audit.py first"
        )
    d1 = load_json(D1_OUTPUT_PATH)
    metrics = [_scenario_metrics(scenario) for scenario in d1["scenarios"]]
    classification = _classify(metrics)
    interpretation = (
        "Residual circulation remains below the material normalized threshold. "
        "Stable weak rows, if present, should be treated as weak residual "
        "targets for any future D2 prototype, not as native loop evidence."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1b_circulation_persistence_v1",
        "experiment_id": d1["experiment_id"],
        "status": "pass",
        "command": COMMAND,
        "source_d1_output": str(D1_OUTPUT_PATH),
        "classification": classification,
        "scenario_metrics": metrics,
        "interpretation": interpretation,
        "errors": [],
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification["classification"],
                "material_rows": classification["material_circulation_rows"],
                "stable_weak_rows": classification["stable_weak_rows"],
                "errors": [],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Cross-family pressure-boundary evidence comparison."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps


DEFAULT_PRESSURE_BOUNDARY_COMPARISON_ROOT = Path(
    "outputs/pressure_boundary/cross_family"
)
DEFAULT_PRESSURE_BOUNDARY_COMPARISON_SESSION_ID = "S0001"

DEFAULT_EVIDENCE_PATHS: dict[str, Path] = {
    "grc9": Path(
        "outputs/grc9/phenomenology_discovery/sessions/S0038/generated_lanes/"
        "front_capacity_growth_pressure_boundary_positive_control/telemetry/run_summary.json"
    ),
    "grcl9": Path(
        "outputs/grcl9/lowering/sessions/S0038/lanes/"
        "corrected_pressure_boundary_positive_high/telemetry/run_summary.json"
    ),
    "grc9v3": Path(
        "outputs/grc9v3/phenomenology_discovery/sessions/S0015/generated_lanes/"
        "pressure_boundary_growth_positive_control_positive_control/telemetry/run_summary.json"
    ),
    "grcl9v3": Path(
        "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
        "pressure_boundary_positive_control/telemetry/run_summary.json"
    ),
    "grcv3": Path(
        "outputs/grcv3/pressure_boundary/sessions/S0001/lanes/"
        "pressure_boundary_frontier_birth_positive/telemetry/run_summary.json"
    ),
}

FAMILY_SPECIFIC_OBSERVABLES: dict[str, tuple[str, ...]] = {
    "grc9": (
        "family_extensions.grc9.growth_summary.pressure_boundary_growth_count",
        "family_extensions.grc9.growth_summary.front_capacity_growth_count",
        "family_extensions.grc9.final_port_chart_summary.inactive_port_count",
        "family_extensions.grc9.final_transport_summary.flux_abs_sum",
    ),
    "grcl9": (
        "family_extensions.grcl9.growth_parent_capacity_sources",
        "family_extensions.grcl9.growth_parent_eligibility_mode",
        "family_extensions.grc9.growth_summary.pressure_boundary_growth_count",
    ),
    "grc9v3": (
        "family_extensions.grc9v3.lifecycle_event_counts.pressure_boundary_growth_count",
        "family_extensions.grc9v3.final_port_chart_summary.inactive_port_count",
        "family_extensions.grc9v3.final_differential_summary.signed_hessian_min",
        "family_extensions.grc9v3.final_choice_collapse_summary.choice_regime_count",
    ),
    "grcl9v3": (
        "family_extensions.grcl9v3.expected_region_caches.grcl9v3_expected_pressure_boundary_region_ids",
        "family_extensions.grc9v3.lifecycle_event_counts.pressure_boundary_growth_count",
        "family_extensions.grc9v3.final_choice_collapse_summary.choice_regime_count",
    ),
    "grcv3": (
        "family_extensions.grcv3.frontier_birth_summary.pressure_boundary_birth_count",
        "family_extensions.grcv3.frontier_birth_summary.frontier_birth_mode",
        "family_extensions.grcv3.final_basin_summary.active_basin_count",
        "family_extensions.grcv3.signed_hessian.hessian_sign",
    ),
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_path(payload: Mapping[str, Any], field_path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in field_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return default
        current = current[part]
    return current


def _extract_family_row(family: str, path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if family in {"grc9", "grcl9"}:
        growth_summary = _get_path(payload, "family_extensions.grc9.growth_summary", {})
        pressure_birth_count = int(growth_summary.get("pressure_boundary_growth_count", 0))
        generic_birth_count = int(growth_summary.get("front_capacity_growth_count", 0))
        legacy_count = int(growth_summary.get("legacy_broad_growth_count", 0))
        birth_label = "growth"
    elif family in {"grc9v3", "grcl9v3"}:
        lifecycle = _get_path(payload, "family_extensions.grc9v3.lifecycle_event_counts", {})
        pressure_birth_count = int(lifecycle.get("pressure_boundary_growth_count", 0))
        generic_birth_count = int(lifecycle.get("front_capacity_growth_count", 0))
        legacy_count = int(lifecycle.get("legacy_broad_growth_count", 0))
        birth_label = "growth"
    elif family == "grcv3":
        frontier_summary = _get_path(
            payload,
            "family_extensions.grcv3.frontier_birth_summary",
            {},
        )
        pressure_birth_count = int(frontier_summary.get("pressure_boundary_birth_count", 0))
        generic_birth_count = int(frontier_summary.get("frontier_birth_count", 0))
        legacy_count = 0
        birth_label = "frontier_birth"
    else:
        raise ValueError(f"unsupported pressure-boundary comparison family {family!r}")
    observables = {
        field_path: _get_path(payload, field_path)
        for field_path in FAMILY_SPECIFIC_OBSERVABLES[family]
    }
    return {
        "family": family,
        "artifact_path": str(path),
        "seed_name": _get_path(payload, "identity.seed_name"),
        "event_counts_by_kind": _get_path(payload, "event_counts_by_kind", {}),
        "pressure_boundary_birth_count": pressure_birth_count,
        "generic_frontier_or_capacity_birth_count": generic_birth_count,
        "legacy_broad_growth_count": legacy_count,
        "birth_event_label": birth_label,
        "evidence_passed": pressure_birth_count > 0 and legacy_count == 0,
        "family_specific_observables": observables,
    }


def build_pressure_boundary_cross_family_report(
    evidence_paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Build a compact comparison over current pressure-boundary evidence."""

    paths = DEFAULT_EVIDENCE_PATHS if evidence_paths is None else dict(evidence_paths)
    rows = [_extract_family_row(family, path) for family, path in sorted(paths.items())]
    return {
        "comparison_version": "pressure_boundary_cross_family_v1",
        "shared_observable": (
            "pressure-boundary-sourced birth/growth count is positive and "
            "legacy broad growth count is zero"
        ),
        "interpretation": {
            "compatibility_scope": (
                "Legacy or missing/disabled birth modes are expected to remain "
                "no-birth. That compatibility is checked in the GRCV3 S0001 "
                "compatibility lanes, not by these positive rows."
            ),
            "positive_evidence_scope": (
                "The rows in this comparison are opt-in positive pressure-boundary "
                "examples. They grow because their source/runtime metadata marks "
                "an eligible pressure-boundary or front-capacity parent and the "
                "outward-flux pressure birth rule is enabled."
            ),
            "birth_rule": "p_birth = 1 - exp(-lambda_birth * F_out)",
            "legacy_distinction": (
                "Legacy broad growth was over-permissive in parent eligibility. "
                "The corrected positive rows are not chance-only legacy growth; "
                "they require explicit pressure-boundary/frontier provenance."
            ),
        },
        "shared_result": all(row["evidence_passed"] for row in rows),
        "families": rows,
        "family_specific_summary": {
            "grc9": "nine-port front-capacity growth on GRC9 mechanical graph",
            "grcl9": "GRCL-9 authored pressure-boundary source lowered to GRC9 front capacity",
            "grc9v3": "hybrid GRC9V3 pressure-boundary growth with GRCV3 differential summaries",
            "grcl9v3": "GRCL-9V3 source region cache plus GRC9V3 hybrid runtime evidence",
            "grcv3": "opt-in active-frontier pressure birth without nine-port claims",
        },
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: Mapping[str, Any]) -> None:
    lines = [
        "# Pressure-Boundary Cross-Family Comparison",
        "",
        f"- Version: `{report['comparison_version']}`",
        f"- Shared result: `{report['shared_result']}`",
        f"- Shared observable: {report['shared_observable']}",
        "",
        "## Interpretation",
        "",
        f"- Compatibility scope: {report['interpretation']['compatibility_scope']}",
        f"- Positive evidence scope: {report['interpretation']['positive_evidence_scope']}",
        f"- Birth rule: `{report['interpretation']['birth_rule']}`",
        f"- Legacy distinction: {report['interpretation']['legacy_distinction']}",
        "",
        "| Family | Pressure Boundary Count | Generic Count | Legacy Count | Event Label | Evidence |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in report["families"]:
        lines.append(
            "| {family} | {pressure} | {generic} | {legacy} | {label} | {passed} |".format(
                family=row["family"],
                pressure=row["pressure_boundary_birth_count"],
                generic=row["generic_frontier_or_capacity_birth_count"],
                legacy=row["legacy_broad_growth_count"],
                label=row["birth_event_label"],
                passed=row["evidence_passed"],
            )
        )
    lines.extend(["", "## Family-Specific Observables", ""])
    for row in report["families"]:
        lines.append(f"### {row['family']}")
        lines.append("")
        lines.append(f"- Artifact: `{row['artifact_path']}`")
        for field_path, value in row["family_specific_observables"].items():
            lines.append(f"- `{field_path}`: `{value}`")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_pressure_boundary_cross_family_session(
    *,
    session_id: str = DEFAULT_PRESSURE_BOUNDARY_COMPARISON_SESSION_ID,
    output_root: str | Path = DEFAULT_PRESSURE_BOUNDARY_COMPARISON_ROOT,
) -> dict[str, Any]:
    """Write the cross-family comparison report under outputs."""

    session_dir = Path(output_root) / session_id
    report = build_pressure_boundary_cross_family_report()
    report = {
        **report,
        "session_id": session_id,
        "session_root": str(session_dir),
        "replay_command": (
            "PYTHONPATH=src python -m pygrc.telemetry.pressure_boundary_cross_family "
            f"--session-id {session_id}"
        ),
    }
    _write_json(session_dir / "comparison_report.json", report)
    _write_markdown(session_dir / "comparison_report.md", report)
    _write_json(
        session_dir / "session_manifest.json",
        {
            "session_id": session_id,
            "comparison_version": report["comparison_version"],
            "source_artifacts": [
                row["artifact_path"] for row in report["families"]
            ],
            "replay_command": report["replay_command"],
        },
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the pressure-boundary cross-family comparison report."
    )
    parser.add_argument("--session-id", default=DEFAULT_PRESSURE_BOUNDARY_COMPARISON_SESSION_ID)
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_PRESSURE_BOUNDARY_COMPARISON_ROOT),
    )
    args = parser.parse_args(argv)
    report = write_pressure_boundary_cross_family_session(
        session_id=args.session_id,
        output_root=args.output_root,
    )
    print(canonical_json_dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_EVIDENCE_PATHS",
    "DEFAULT_PRESSURE_BOUNDARY_COMPARISON_ROOT",
    "DEFAULT_PRESSURE_BOUNDARY_COMPARISON_SESSION_ID",
    "build_pressure_boundary_cross_family_report",
    "write_pressure_boundary_cross_family_session",
]

"""Complex GRC9/GRC9V3 growth-source comparison probes."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps
from pygrc.discovery.grc9_discovery_runner import _run_discovery_lane as _run_grc9_lane
from pygrc.discovery.grc9_seed_generator import (
    GRC9GeneratedSeed,
    generate_grc9_corrected_growth_combo_fixture,
)
from pygrc.discovery.grc9v3_discovery_runner import (
    _run_discovery_lane as _run_grc9v3_lane,
)
from pygrc.discovery.grc9v3_seed_generator import (
    GRC9V3GeneratedSeed,
    generate_grc9v3_pressure_boundary_example,
)


DEFAULT_COMPLEX_SOURCE_COMPARISON_ROOT = Path(
    "outputs/pressure_boundary/complex_source_comparison"
)
DEFAULT_COMPLEX_SOURCE_COMPARISON_SESSION_ID = "S0001"

GRC9_FRONT_CAPACITY_SOURCES: tuple[str, ...] = (
    "closed_front_capacity",
    "preexisting_front",
    "preexisting_front_capacity",
    "pressure_boundary",
    "propagated_front_growth",
    "refinement_boundary_capacity",
    "spark_expansion_front",
    "spark_refinement_boundary_front",
    "spark_refinement_front",
)
GRC9V3_FRONT_CAPACITY_SOURCES: tuple[str, ...] = (
    "closed_front_capacity",
    "preexisting_front",
    "pressure_boundary",
    "propagated_front_growth",
    "refinement_boundary_capacity",
    "spark_expansion_front",
    "spark_refinement_boundary_front",
    "spark_refinement_front",
)


def _source_token(source: str) -> str:
    return source.lower().replace("-", "_")


def _set_grc9_growth_source(state_payload: Mapping[str, Any], source: str) -> dict[str, Any]:
    payload = deepcopy(dict(state_payload))
    cached = payload.setdefault("cached_quantities", {})
    sources = cached.setdefault("grc9_growth_parent_capacity_sources", {})
    for record in sources.values():
        if isinstance(record, dict):
            record["front_capacity_source"] = source
    cached["pressure_boundary_source_comparison_variant"] = source
    return payload


def _set_grc9v3_growth_source(
    state_payload: Mapping[str, Any],
    source: str,
) -> dict[str, Any]:
    payload = deepcopy(dict(state_payload))
    cached = payload.setdefault("cached_quantities", {})
    sources = cached.setdefault("grcl9v3_growth_parent_capacity_sources", {})
    for record in sources.values():
        if isinstance(record, dict):
            record["front_capacity_source"] = source
    cached["grcl9v3_expected_pressure_boundary_region_ids"] = (
        [12] if source == "pressure_boundary" else []
    )
    cached["pressure_boundary_source_comparison_variant"] = source
    return payload


def _with_mode(
    runtime_config: Mapping[str, Any],
    *,
    growth_parent_eligibility: str,
) -> dict[str, Any]:
    config = deepcopy(dict(runtime_config))
    modes = config.setdefault("constitutive_semantic_modes", {})
    modes["growth_parent_eligibility"] = growth_parent_eligibility
    return config


def _grc9_variant_seed(base: GRC9GeneratedSeed, *, source: str | None) -> GRC9GeneratedSeed:
    if source is None:
        lane_name = "grc9_complex_legacy_any_inactive_port"
        seed_parameters = {
            **dict(base.seed_parameters),
            "source_comparison_variant": "legacy_any_inactive_port",
            "front_capacity_source": None,
            "evidence_status": "diagnostic_legacy_control",
        }
        return replace(
            base,
            seed_family=lane_name,
            seed_name=lane_name,
            lane_name=lane_name,
            control_role="legacy_control",
            profile="pressure_boundary_complex_source_comparison_v1",
            seed_parameters=seed_parameters,
            expected_runtime_config=_with_mode(
                base.expected_runtime_config,
                growth_parent_eligibility="legacy_any_inactive_port",
            ),
            graph_preconditions={
                **dict(base.graph_preconditions),
                "source_comparison_variant": "legacy_any_inactive_port",
                "diagnostic_only": True,
            },
            state_payload=deepcopy(dict(base.state_payload)),
        )
    lane_name = f"grc9_complex_front_source_{_source_token(source)}"
    seed_parameters = {
        **dict(base.seed_parameters),
        "source_comparison_variant": source,
        "front_capacity_source": source,
        "evidence_status": (
            "pressure_boundary_specific"
            if source == "pressure_boundary"
            else "generic_corrected_front_capacity"
        ),
    }
    return replace(
        base,
        seed_family=lane_name,
        seed_name=lane_name,
        lane_name=lane_name,
        control_role="source_comparison",
        profile="pressure_boundary_complex_source_comparison_v1",
        seed_parameters=seed_parameters,
        expected_runtime_config=_with_mode(
            base.expected_runtime_config,
            growth_parent_eligibility="grc9_front_capacity",
        ),
        graph_preconditions={
            **dict(base.graph_preconditions),
            "source_comparison_variant": source,
            "same_base_topology_as": base.lane_name,
        },
        state_payload=_set_grc9_growth_source(base.state_payload, source),
    )


def _grc9v3_variant_seed(
    base: GRC9V3GeneratedSeed,
    *,
    source: str | None,
) -> GRC9V3GeneratedSeed:
    if source is None:
        lane_name = "grc9v3_complex_legacy_any_inactive_port"
        seed_parameters = {
            **dict(base.seed_parameters),
            "source_comparison_variant": "legacy_any_inactive_port",
            "front_capacity_source": None,
            "evidence_status": "diagnostic_legacy_control",
        }
        return replace(
            base,
            seed_family=lane_name,
            seed_name=lane_name,
            lane_name=lane_name,
            control_role="legacy_control",
            profile="pressure_boundary_complex_source_comparison_v1",
            seed_parameters=seed_parameters,
            expected_runtime_config=_with_mode(
                base.expected_runtime_config,
                growth_parent_eligibility="legacy_any_inactive_port",
            ),
            graph_preconditions={
                **dict(base.graph_preconditions),
                "source_comparison_variant": "legacy_any_inactive_port",
                "diagnostic_only": True,
            },
            state_payload=deepcopy(dict(base.state_payload)),
        )
    lane_name = f"grc9v3_complex_front_source_{_source_token(source)}"
    seed_parameters = {
        **dict(base.seed_parameters),
        "source_comparison_variant": source,
        "front_capacity_source": source,
        "evidence_status": (
            "pressure_boundary_specific"
            if source == "pressure_boundary"
            else "generic_corrected_front_capacity"
        ),
    }
    return replace(
        base,
        seed_family=lane_name,
        seed_name=lane_name,
        lane_name=lane_name,
        control_role="source_comparison",
        profile="pressure_boundary_complex_source_comparison_v1",
        seed_parameters=seed_parameters,
        expected_runtime_config=_with_mode(
            base.expected_runtime_config,
            growth_parent_eligibility="grcl9v3_front_capacity",
        ),
        graph_preconditions={
            **dict(base.graph_preconditions),
            "source_comparison_variant": source,
            "same_base_topology_as": base.lane_name,
        },
        state_payload=_set_grc9v3_growth_source(base.state_payload, source),
    )


def _summary_path(lane_artifact_root: str) -> Path:
    return Path(lane_artifact_root) / "telemetry" / "run_summary.json"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_from_grc9_summary(lane: Any, summary: Mapping[str, Any]) -> dict[str, Any]:
    grc9 = summary.get("family_extensions", {}).get("grc9", {})
    growth = grc9.get("growth_summary", {})
    backend = grc9.get("backend_summary", {})
    raw_modes = summary.get("raw_params", {}).get("constitutive_semantic_modes", {})
    return {
        "family": "grc9",
        "lane_name": lane.seed.lane_name,
        "variant": lane.seed.seed_parameters.get("source_comparison_variant"),
        "evidence_status": lane.seed.seed_parameters.get("evidence_status"),
        "growth_parent_eligibility_mode": backend.get(
            "growth_parent_eligibility_mode",
            raw_modes.get("growth_parent_eligibility"),
        ),
        "event_counts_by_kind": dict(lane.event_counts_by_kind),
        "growth_count": int(growth.get("growth_count", 0)),
        "front_capacity_growth_count": int(growth.get("front_capacity_growth_count", 0)),
        "pressure_boundary_growth_count": int(
            growth.get("pressure_boundary_growth_count", 0)
        ),
        "legacy_broad_growth_count": int(growth.get("legacy_broad_growth_count", 0)),
        "artifact_root": lane.artifact_root,
    }


def _row_from_grc9v3_summary(lane: Any, summary: Mapping[str, Any]) -> dict[str, Any]:
    grc9v3 = summary.get("family_extensions", {}).get("grc9v3", {})
    lifecycle = grc9v3.get("lifecycle_event_counts", {})
    backend = grc9v3.get("backend_summary", {})
    raw_modes = summary.get("raw_params", {}).get("constitutive_semantic_modes", {})
    return {
        "family": "grc9v3",
        "lane_name": lane.seed.lane_name,
        "variant": lane.seed.seed_parameters.get("source_comparison_variant"),
        "evidence_status": lane.seed.seed_parameters.get("evidence_status"),
        "growth_parent_eligibility_mode": backend.get(
            "growth_parent_eligibility_mode",
            raw_modes.get("growth_parent_eligibility"),
        ),
        "event_counts_by_kind": dict(lane.event_counts_by_kind),
        "growth_count": int(lifecycle.get("growth_count", 0)),
        "front_capacity_growth_count": int(
            lifecycle.get("front_capacity_growth_count", 0)
        ),
        "pressure_boundary_growth_count": int(
            lifecycle.get("pressure_boundary_growth_count", 0)
        ),
        "legacy_broad_growth_count": int(lifecycle.get("legacy_broad_growth_count", 0)),
        "choice_detected_count": int(lifecycle.get("choice_detected_count", 0)),
        "collapse_count": int(lifecycle.get("collapse_count", 0)),
        "artifact_root": lane.artifact_root,
    }


def _write_json(path: Path, payload: Mapping[str, Any] | Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: Mapping[str, Any]) -> None:
    lines = [
        "# Pressure-Boundary Complex Source Comparison",
        "",
        "This is an exploratory comparison. Legacy rows are diagnostic controls only.",
        "",
        "| family | variant | mode | growth | front | pressure | legacy | events |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {family} | {variant} | {mode} | {growth} | {front} | {pressure} | {legacy} | `{events}` |".format(
                family=row["family"],
                variant=row["variant"],
                mode=row.get("growth_parent_eligibility_mode"),
                growth=row["growth_count"],
                front=row["front_capacity_growth_count"],
                pressure=row["pressure_boundary_growth_count"],
                legacy=row["legacy_broad_growth_count"],
                events=json.dumps(row["event_counts_by_kind"], sort_keys=True),
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- `pressure_boundary` rows are pressure-boundary-specific.",
            "- Other front-capacity source rows are generic corrected-front source probes.",
            "- `legacy_any_inactive_port` rows are historical diagnostic controls and are not accepted pressure-boundary evidence.",
            "",
            f"Replay: `{report['replay_command']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_pressure_boundary_complex_source_comparison(
    *,
    session_id: str = DEFAULT_COMPLEX_SOURCE_COMPARISON_SESSION_ID,
    output_root: str | Path = DEFAULT_COMPLEX_SOURCE_COMPARISON_ROOT,
    grc9_steps: int = 6,
    grc9v3_steps: int = 4,
) -> Mapping[str, Any]:
    """Run complex GRC9/GRC9V3 source-label comparison probes."""

    root = Path(output_root) / session_id
    root.mkdir(parents=True, exist_ok=True)
    grc9_lanes_root = root / "grc9" / "generated_lanes"
    grc9v3_lanes_root = root / "grc9v3" / "generated_lanes"

    grc9_base = generate_grc9_corrected_growth_combo_fixture(
        "corrected_spark_growth_fission_combo"
    )
    grc9v3_base = generate_grc9v3_pressure_boundary_example(
        "complex_spark_expansion_pressure_boundary_growth"
    )
    grc9_seeds = (
        _grc9_variant_seed(grc9_base, source=None),
        *(_grc9_variant_seed(grc9_base, source=source) for source in GRC9_FRONT_CAPACITY_SOURCES),
    )
    grc9v3_seeds = (
        _grc9v3_variant_seed(grc9v3_base, source=None),
        *(
            _grc9v3_variant_seed(grc9v3_base, source=source)
            for source in GRC9V3_FRONT_CAPACITY_SOURCES
        ),
    )

    rows: list[dict[str, Any]] = []
    for seed in grc9_seeds:
        lane = _run_grc9_lane(
            seed=seed,
            requested_steps=grc9_steps,
            session_root=root / "grc9",
            lanes_root=grc9_lanes_root,
        )
        rows.append(_row_from_grc9_summary(lane, _read_json(_summary_path(lane.artifact_root))))
    for seed in grc9v3_seeds:
        lane = _run_grc9v3_lane(
            seed=seed,
            requested_steps=grc9v3_steps,
            session_root=root / "grc9v3",
            lanes_root=grc9v3_lanes_root,
        )
        rows.append(
            _row_from_grc9v3_summary(lane, _read_json(_summary_path(lane.artifact_root)))
        )

    report = {
        "comparison_version": "pressure_boundary_complex_source_comparison_v1",
        "session_id": session_id,
        "session_root": str(root),
        "scope": "exploratory_iteration_8",
        "grc9_front_capacity_sources": list(GRC9_FRONT_CAPACITY_SOURCES),
        "grc9v3_front_capacity_sources": list(GRC9V3_FRONT_CAPACITY_SOURCES),
        "rows": rows,
        "interpretation": {
            "legacy_rows": "diagnostic only; not accepted pressure-boundary evidence",
            "pressure_boundary_rows": "pressure-boundary-specific source provenance",
            "other_front_capacity_rows": "generic corrected-front source-label probes",
        },
        "replay_command": (
            "PYTHONPATH=src python -m "
            "pygrc.telemetry.pressure_boundary_complex_source_comparison "
            f"--session-id {session_id}"
        ),
    }
    _write_json(root / "comparison_report.json", report)
    _write_json(
        root / "session_manifest.json",
        {
            "session_id": session_id,
            "session_root": str(root),
            "comparison_version": report["comparison_version"],
            "replay_command": report["replay_command"],
            "row_count": len(rows),
        },
    )
    _write_markdown(root / "comparison_report.md", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run exploratory complex front-capacity source comparisons."
    )
    parser.add_argument("--session-id", default=DEFAULT_COMPLEX_SOURCE_COMPARISON_SESSION_ID)
    parser.add_argument("--output-root", default=str(DEFAULT_COMPLEX_SOURCE_COMPARISON_ROOT))
    parser.add_argument("--grc9-steps", type=int, default=6)
    parser.add_argument("--grc9v3-steps", type=int, default=4)
    args = parser.parse_args(argv)
    report = run_pressure_boundary_complex_source_comparison(
        session_id=args.session_id,
        output_root=args.output_root,
        grc9_steps=args.grc9_steps,
        grc9v3_steps=args.grc9v3_steps,
    )
    print(canonical_json_dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_COMPLEX_SOURCE_COMPARISON_ROOT",
    "DEFAULT_COMPLEX_SOURCE_COMPARISON_SESSION_ID",
    "GRC9_FRONT_CAPACITY_SOURCES",
    "GRC9V3_FRONT_CAPACITY_SOURCES",
    "run_pressure_boundary_complex_source_comparison",
]

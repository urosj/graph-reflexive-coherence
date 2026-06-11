"""Replayable GRCV3 pressure-boundary frontier-birth evidence sessions."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import (
    GRCParams,
    StepResult,
    WeightedGraphBackend,
    canonical_json_dumps,
    digest_snapshot,
)
from pygrc.models import GRCV3
from pygrc.models.grc_v3_checkpoints import export_grcv3_graph_checkpoint

from ._grcv3_extensions import (
    _build_grcv3_run_summary_extension,
    _build_grcv3_step_extension,
)
from .grcv3_contract import (
    classify_grcv3_event_extension,
    grcv3_event_family_extensions,
    grcv3_run_summary_family_extensions,
    grcv3_step_family_extensions,
)
from .grcv3_pressure_boundary_selectors import (
    validate_grcv3_pressure_boundary_frontier_birth,
)
from .io import TelemetryArtifactLayout
from .recorder import TelemetryCaptureConfig, capture_run_telemetry
from .schema import RunTelemetryIdentity, build_run_id


DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ROOT = Path(
    "outputs/grcv3/pressure_boundary/sessions"
)
DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ID = "S0001"
GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE = (
    "implementation/PressureBoundary-GRCV3-FrontierAudit.md"
)


@dataclass(frozen=True)
class GRCV3PressureBoundaryLaneResult:
    """One lane emitted by the pressure-boundary evidence runner."""

    lane_name: str
    run_id: str
    telemetry_dir: Path
    event_counts_by_kind: Mapping[str, int]
    frontier_birth_count: int
    pressure_boundary_birth_count: int
    selector_passed: bool | None
    final_snapshot_digest: str


def _node_attributes(*, coherence: float, basin_id: int) -> dict[str, Any]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def _build_pressure_boundary_model(
    *,
    frontier_birth_mode: str | None,
    frontier_birth_strict: str | None = None,
) -> GRCV3:
    graph = WeightedGraphBackend()
    parent = graph.add_node({"role": "pressure_boundary_parent"})
    neighbor = graph.add_node({"role": "interior_support"})
    edge_id = graph.add_edge(parent, neighbor, {"role": "pressure_boundary_outflow"})
    modes: dict[str, Any] = {}
    if frontier_birth_mode is not None:
        modes["frontier_birth_mode"] = frontier_birth_mode
    if frontier_birth_strict is not None:
        modes["frontier_birth_strict"] = frontier_birth_strict
    model = GRCV3.from_state(
        state={
            "nodes": {
                str(parent): _node_attributes(coherence=10.0, basin_id=parent),
                str(neighbor): _node_attributes(coherence=1.0, basin_id=neighbor),
            },
            "base_conductance": {str(edge_id): 1.0},
            "cached_quantities": {
                "hessian_sign": 1,
                "grcv3_frontier_birth_candidates": {
                    str(parent): {
                        "frontier_source": "pressure_boundary",
                        "frontier_role": "system_boundary",
                        "source_construct_id": "pressure_boundary_frontier",
                    }
                },
                "grcv3_active_frontier_node_ids": [parent],
                "grcv3_pressure_boundary_frontier_node_ids": [parent],
            },
            "budget_target": 11.0,
        },
        params={
            "dt": 0.1,
            "evolution": {
                "lambda_birth": 100.0,
                "alpha_seed": 0.2,
                "rng_seed": 0,
            },
            "constitutive_semantic_modes": modes,
        },
    )
    state = model.get_state()
    state.topology = graph
    state.flux = {
        (edge_id, parent): 2.0,
        (edge_id, neighbor): -2.0,
    }
    return model


def _source_fixture_payload() -> dict[str, Any]:
    return {
        "schema_version": "grclv3.pressure_boundary_frontier.v1",
        "fixture_name": "grcv3_pressure_boundary_frontier_birth_positive",
        "source_reference": GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE,
        "constructs": [
            {
                "construct_id": "pressure_boundary_frontier",
                "construct_kind": "system_boundary_frontier",
                "boundary_role": "pressure_boundary",
                "growth_semantics": "active_frontier_pressure",
                "frontier_birth_mode": "active_frontier_pressure",
                "eligible_parent_rule": "explicit_pressure_boundary_frontier_node",
            }
        ],
        "lowering_contract": {
            "runtime_family": "grcv3",
            "frontier_candidate_cache": "grcv3_frontier_birth_candidates",
            "frontier_source": "pressure_boundary",
            "mode_required": "active_frontier_pressure",
        },
        "non_claims": [
            "no_default_birth_for_grcv3",
            "no_broad_internal_growth",
            "no_grc9_front_capacity_claim",
        ],
    }


def _capture_lane(
    *,
    lane_name: str,
    model: GRCV3,
    session_dir: Path,
    operation: str,
) -> GRCV3PressureBoundaryLaneResult:
    lane_dir = session_dir / "lanes" / lane_name
    lane_dir.mkdir(parents=True, exist_ok=True)
    initial_snapshot = model.snapshot()
    initial_observables = dict(model.compute_observables())
    if operation == "step":
        step_result = model.step()
    elif operation == "frontier_birth_apply":
        events = model.apply_frontier_birth()
        step_result = StepResult(
            step_index=model.get_state().step_index,
            time=model.get_state().time,
            events=events,
            observables=dict(model.compute_observables()),
            bookkeeping={"step_order": ("apply_frontier_birth",)},
        )
    else:
        raise ValueError(f"unsupported pressure-boundary lane operation {operation!r}")

    step_family_extensions = [
        dict(grcv3_step_family_extensions(_build_grcv3_step_extension(model)))
    ]
    event_family_extensions_by_step = [
        [
            dict(
                grcv3_event_family_extensions(
                    classify_grcv3_event_extension(event.kind, event.payload)
                )
            )
            for event in step_result.events
        ]
    ]
    summary_family_extensions = dict(
        grcv3_run_summary_family_extensions(
            _build_grcv3_run_summary_extension(model, (step_result,))
        )
    )
    params: GRCParams = model.get_params()
    run_id = build_run_id(
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=lane_name,
        seed_source_reference=GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE,
        seed_path=f"outputs/grcv3/pressure_boundary/{lane_name}",
        param_family="pressure_boundary_frontier_birth",
        rng_seed=0,
        requested_steps=1,
        overrides=None,
    )
    identity = RunTelemetryIdentity(
        run_id=run_id,
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=lane_name,
        seed_source_reference=GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE,
        seed_path=f"outputs/grcv3/pressure_boundary/{lane_name}",
        param_family="pressure_boundary_frontier_birth",
        rng_seed=0,
        requested_steps=1,
    )
    final_observables = dict(model.compute_observables())
    event_counts_by_kind: dict[str, int] = {}
    for event in step_result.events:
        event_counts_by_kind[event.kind] = event_counts_by_kind.get(event.kind, 0) + 1
    checkpoints = (
        export_grcv3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="step-00000001",
            checkpoint_label="final",
            checkpoint_reason="final",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=len(step_result.events),
            event_counts_by_kind_window=event_counts_by_kind,
            include_flow_overlays=False,
        ),
    )
    layout = TelemetryArtifactLayout(
        root_dir=lane_dir,
        run_id=run_id,
        run_dir=lane_dir,
        telemetry_dir=lane_dir / "telemetry",
        step_rows_path=lane_dir / "telemetry" / "steps.jsonl",
        event_rows_path=lane_dir / "telemetry" / "events.jsonl",
        run_summary_path=lane_dir / "telemetry" / "run_summary.json",
        comparison_report_path=lane_dir / "telemetry" / "comparison_report.json",
        experiment_report_path=lane_dir / "telemetry" / "experiment_report.json",
        graph_checkpoints_dir=lane_dir / "telemetry" / "graph_checkpoints",
        graph_checkpoint_index_path=lane_dir
        / "telemetry"
        / "graph_checkpoints"
        / "index.json",
    )
    capture = capture_run_telemetry(
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=lane_name,
        seed_source_reference=GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE,
        seed_path=f"outputs/grcv3/pressure_boundary/{lane_name}",
        param_family="pressure_boundary_frontier_birth",
        rng_seed=0,
        requested_steps=1,
        initial_observables=initial_observables,
        step_results=(step_result,),
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        step_family_extensions=step_family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=checkpoints,
        artifact_layout=layout,
        config=TelemetryCaptureConfig(write_artifacts=True),
    )
    snapshots_dir = lane_dir / "snapshots"
    _write_json(snapshots_dir / "initial_snapshot.json", initial_snapshot)
    _write_json(snapshots_dir / "final_snapshot.json", model.snapshot())
    summary_payload = {
        "family_extensions": dict(capture.run_summary.family_extensions),
    }
    selector_result = validate_grcv3_pressure_boundary_frontier_birth(summary_payload)
    frontier_summary = summary_family_extensions["grcv3"]["frontier_birth_summary"]
    _write_json(
        lane_dir / "lane_report.json",
        {
            "lane_name": lane_name,
            "operation": operation,
            "run_id": run_id,
            "event_counts_by_kind": dict(capture.run_summary.event_counts_by_kind),
            "frontier_birth_summary": frontier_summary,
            "selector": selector_result.to_mapping(),
            "final_snapshot_digest": digest_snapshot(model.snapshot()),
        },
    )
    return GRCV3PressureBoundaryLaneResult(
        lane_name=lane_name,
        run_id=run_id,
        telemetry_dir=layout.telemetry_dir,
        event_counts_by_kind=dict(capture.run_summary.event_counts_by_kind),
        frontier_birth_count=int(frontier_summary["frontier_birth_count"]),
        pressure_boundary_birth_count=int(
            frontier_summary["pressure_boundary_birth_count"]
        ),
        selector_passed=selector_result.passed,
        final_snapshot_digest=digest_snapshot(model.snapshot()),
    )


def _write_json(path: Path, payload: Mapping[str, Any] | Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _read_legacy_reference() -> dict[str, Any]:
    root = Path("outputs/grcv3-rich-fulltest-choice-smoke")
    candidates = sorted(root.glob("**/telemetry/run_summary.json"))
    if not candidates:
        return {
            "status": "not_available",
            "reference_path": None,
            "frontier_birth_count": None,
        }
    path = candidates[0]
    payload = json.loads(path.read_text(encoding="utf-8"))
    event_counts = payload.get("event_counts_by_kind", {})
    frontier_summary = (
        payload.get("family_extensions", {})
        .get("grcv3", {})
        .get("frontier_birth_summary", {})
    )
    return {
        "status": "loaded",
        "reference_path": str(path),
        "event_counts_by_kind": event_counts,
        "frontier_birth_count": int(event_counts.get("frontier_birth", 0)),
        "frontier_birth_summary_present": bool(frontier_summary),
    }


def run_grcv3_pressure_boundary_evidence_session(
    *,
    session_id: str = DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ID,
    output_root: str | Path = DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ROOT,
) -> dict[str, Any]:
    """Write a replayable pressure-boundary GRCV3 evidence session."""

    session_dir = Path(output_root) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    _write_json(session_dir / "source_fixtures" / "pressure_boundary_frontier.json", _source_fixture_payload())
    lanes = (
        _capture_lane(
            lane_name="compat_missing_frontier_birth_mode",
            model=_build_pressure_boundary_model(
                frontier_birth_mode=None,
                frontier_birth_strict="allow",
            ),
            session_dir=session_dir,
            operation="step",
        ),
        _capture_lane(
            lane_name="compat_disabled_frontier_birth_mode",
            model=_build_pressure_boundary_model(
                frontier_birth_mode="disabled",
                frontier_birth_strict="allow",
            ),
            session_dir=session_dir,
            operation="step",
        ),
        _capture_lane(
            lane_name="pressure_boundary_frontier_birth_positive",
            model=_build_pressure_boundary_model(
                frontier_birth_mode="active_frontier_pressure",
                frontier_birth_strict="error",
            ),
            session_dir=session_dir,
            operation="frontier_birth_apply",
        ),
    )
    legacy_reference = _read_legacy_reference()
    report = {
        "session_id": session_id,
        "session_root": str(session_dir),
        "source_reference": GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE,
        "lanes": [
            {
                "lane_name": lane.lane_name,
                "run_id": lane.run_id,
                "telemetry_dir": str(lane.telemetry_dir),
                "event_counts_by_kind": dict(lane.event_counts_by_kind),
                "frontier_birth_count": lane.frontier_birth_count,
                "pressure_boundary_birth_count": lane.pressure_boundary_birth_count,
                "selector_passed": lane.selector_passed,
                "final_snapshot_digest": lane.final_snapshot_digest,
            }
            for lane in lanes
        ],
        "compatibility": {
            "legacy_reference": legacy_reference,
            "missing_mode_no_birth": lanes[0].frontier_birth_count == 0,
            "disabled_mode_no_birth": lanes[1].frontier_birth_count == 0,
            "old_reference_no_birth": legacy_reference.get("frontier_birth_count") == 0,
        },
        "replay_command": (
            f"PYTHONPATH=src python -m pygrc.telemetry.grcv3_pressure_boundary_evidence "
            f"--session-id {session_id}"
        ),
        "compatibility_landscape_replay_command": (
            "PYTHONPATH=src python -c \"from pygrc.telemetry.experiments import "
            "run_grcv3_landscape_experiment; "
            "run_grcv3_landscape_experiment("
            f"telemetry_experiment_path='grcv3/pressure_boundary/sessions/{session_id}/compatibility_replay', "
            "profile_name='seed_baseline', num_steps=3, "
            "cell1_seed_path='configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml', "
            "cell4_seed_path='configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml', "
            "record_graph_checkpoints=False)\""
        ),
    }
    _write_json(session_dir / "run_report.json", report)
    _write_json(
        session_dir / "session_manifest.json",
        {
            "session_id": session_id,
            "family": "grcv3",
            "purpose": "pressure_boundary_frontier_birth_evidence",
            "source_fixture": "source_fixtures/pressure_boundary_frontier.json",
            "lane_names": [lane.lane_name for lane in lanes],
            "replay_command": report["replay_command"],
            "compatibility_landscape_replay_command": report[
                "compatibility_landscape_replay_command"
            ],
        },
    )
    _write_text(
        session_dir / "README.md",
        "\n".join(
            [
                "# GRCV3 Pressure-Boundary Evidence",
                "",
                "This session records the opt-in GRCV3 pressure-boundary frontier-birth lane and two compatibility no-birth lanes.",
                "",
                f"Replay: `{report['replay_command']}`",
                "",
                "Compatibility replay:",
                f"`{report['compatibility_landscape_replay_command']}`",
                "",
                "Legacy broad growth is not used. Missing `frontier_birth_mode` and explicit `disabled` remain no-birth.",
                "",
            ]
        ),
    )
    _write_text(
        session_dir / "replay.sh",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"PYTHONPATH=src python -m pygrc.telemetry.grcv3_pressure_boundary_evidence --session-id {session_id}\n",
    )
    _append_experimental_log(Path(output_root).parent / "ExperimentalLog.md", report)
    return report


def _append_experimental_log(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = [
        f"## {report['session_id']}",
        "",
        "- Track: GRCV3 pressure-boundary frontier birth",
        f"- Session root: `{report['session_root']}`",
        f"- Replay: `{report['replay_command']}`",
        "- Compatibility: missing/disabled frontier birth modes remain no-birth",
        "",
    ]
    existing = path.read_text(encoding="utf-8") if path.exists() else "# GRCV3 Pressure-Boundary Experimental Log\n\n"
    marker = f"## {report['session_id']}\n"
    if marker in existing:
        before, rest = existing.split(marker, 1)
        next_entry_index = rest.find("\n## ")
        after = "" if next_entry_index < 0 else rest[next_entry_index + 1 :]
        path.write_text(
            before.rstrip() + "\n\n" + "\n".join(entry) + "\n" + after,
            encoding="utf-8",
        )
        return
    path.write_text(existing.rstrip() + "\n\n" + "\n".join(entry) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the GRCV3 pressure-boundary frontier-birth evidence session."
    )
    parser.add_argument("--session-id", default=DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ID)
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ROOT),
    )
    args = parser.parse_args(argv)
    report = run_grcv3_pressure_boundary_evidence_session(
        session_id=args.session_id,
        output_root=args.output_root,
    )
    print(canonical_json_dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ID",
    "DEFAULT_GRCV3_PRESSURE_BOUNDARY_SESSION_ROOT",
    "GRCV3_PRESSURE_BOUNDARY_SOURCE_REFERENCE",
    "GRCV3PressureBoundaryLaneResult",
    "run_grcv3_pressure_boundary_evidence_session",
]

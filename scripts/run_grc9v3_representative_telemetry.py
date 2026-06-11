"""Run the representative telemetry-backed GRC9V3 lane and write artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult, digest_snapshot
from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_to_rc
from pygrc.telemetry._grc9v3_extensions import (
    _build_grc9v3_event_extensions,
    _build_grc9v3_run_summary_extension,
    _build_grc9v3_step_extension,
)
from scripts.run_grc9v3_representative_runtime import (
    DEFAULT_FIXTURE_NAME,
    build_representative_hybrid_model,
)


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_PATH = Path("phase-t-grc9v3") / "representative" / DEFAULT_FIXTURE_NAME
DEFAULT_STEPS = 3


def run_grc9v3_representative_telemetry(
    *,
    outputs_root: Path,
    experiment_path: Path = DEFAULT_EXPERIMENT_PATH,
    steps: int = DEFAULT_STEPS,
    include_checkpoint_overlays: bool = True,
) -> dict[str, Any]:
    """Run the Appendix E representative lane and write Phase T-GRC9V3 artifacts."""

    if steps <= 0:
        raise ValueError("steps must be > 0")

    primary_model = build_representative_hybrid_model()
    identity = telemetry.RunTelemetryIdentity(
        run_id=telemetry.build_run_id(
            model_family="grc9v3",
            params_identity=primary_model.get_params().params_hash,
            seed_name=DEFAULT_FIXTURE_NAME,
            seed_source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            seed_path="scripts/run_grc9v3_representative_runtime.py",
            param_family="phase7_appendix_e",
            rng_seed=0,
            requested_steps=steps,
            overrides={"phase_t_contract": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION},
        ),
        model_family="grc9v3",
        params_identity=primary_model.get_params().params_hash,
        seed_name=DEFAULT_FIXTURE_NAME,
        seed_source_reference="implementation/Phase-7-RepresentativeRuntime.md",
        seed_path="scripts/run_grc9v3_representative_runtime.py",
        param_family="phase7_appendix_e",
        rng_seed=0,
        requested_steps=steps,
    )
    layout = telemetry.build_telemetry_artifact_layout(
        identity.run_id,
        root_dir=outputs_root,
        experiment_path=experiment_path,
    )
    lane_context = telemetry.GRC9V3LaneContext(
        source_reference="implementation/Phase-T-GRC9V3-TelemetryContract.md",
        fixture_name=DEFAULT_FIXTURE_NAME,
        run_role="representative_primary",
        experiment_id="phase_t_grc9v3_representative",
        representative_lane_name="appendix_e_cell_division",
        source_runtime_artifact="implementation/Phase-7-RepresentativeRuntime.md",
    )

    initial_observables = primary_model.compute_observables()
    snapshot_dir = layout.run_dir / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    initial_snapshot_path = snapshot_dir / "initial_snapshot.json"
    final_snapshot_path = snapshot_dir / "final_snapshot.json"
    primary_model.save(str(initial_snapshot_path))

    primary_run = _run_rows_and_checkpoints(
        primary_model,
        identity=identity,
        lane_context=lane_context,
        steps=steps,
        include_checkpoint_overlays=include_checkpoint_overlays,
    )
    primary_model.save(str(final_snapshot_path))
    final_digest = digest_snapshot(primary_model.snapshot())

    replay_model = GRC9V3.load(str(initial_snapshot_path))
    replay_run = _run_rows_and_checkpoints(
        replay_model,
        identity=identity,
        lane_context=lane_context,
        steps=steps,
        build_checkpoints=False,
    )
    replay_digest = digest_snapshot(replay_model.snapshot())
    replay_step_rows_match = replay_run["step_rows"] == primary_run["step_rows"]
    replay_event_rows_match = replay_run["event_rows"] == primary_run["event_rows"]
    replay_digest_match = replay_digest == final_digest

    run_extension = _build_grc9v3_run_summary_extension(
        primary_model,
        primary_run["step_results"],
        lane_context=lane_context,
        replay_digest_match=(
            replay_step_rows_match and replay_event_rows_match and replay_digest_match
        ),
    )
    run_summary = telemetry.run_summary_from_step_results(
        primary_run["step_results"],
        identity=identity,
        initial_observables=initial_observables,
        final_observables=primary_model.compute_observables(),
        resolved_params=primary_model.get_params().resolved_config,
        raw_params=primary_model.get_params().raw_config,
        family_extensions=telemetry.grc9v3_run_summary_family_extensions(run_extension),
    )
    checkpoint_index = _build_checkpoint_index(
        identity,
        primary_run["checkpoints"],
        steps=steps,
    )

    telemetry.save_telemetry_artifact_pack(
        layout,
        step_rows=primary_run["step_rows"],
        event_rows=primary_run["event_rows"],
        run_summary=run_summary,
        graph_checkpoint_index=checkpoint_index,
        graph_checkpoints=primary_run["checkpoints"],
    )
    experiment_report = telemetry.TelemetryExperimentReport(
        family="grc9v3",
        common={
            "run_id": identity.run_id,
            "model_family": identity.model_family,
            "fixture_name": DEFAULT_FIXTURE_NAME,
            "steps": steps,
            "artifact_dir": layout.run_dir.as_posix(),
            "telemetry_dir": layout.telemetry_dir.as_posix(),
            "initial_snapshot_path": initial_snapshot_path.as_posix(),
            "final_snapshot_path": final_snapshot_path.as_posix(),
            "final_snapshot_digest": final_digest,
            "replay_final_snapshot_digest": replay_digest,
            "replay_step_rows_match": replay_step_rows_match,
            "replay_event_rows_match": replay_event_rows_match,
            "replay_digest_match": replay_digest_match,
            "checkpoint_count": len(primary_run["checkpoints"]),
        },
        extensions={
            "grc9v3": {
                "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "representative_fixture": DEFAULT_FIXTURE_NAME,
                "phase7_runtime_source": "scripts/run_grc9v3_representative_runtime.py",
            }
        },
    )
    telemetry.save_experiment_report(layout.experiment_report_path, experiment_report)
    return {
        "run_id": identity.run_id,
        "fixture_name": DEFAULT_FIXTURE_NAME,
        "steps": steps,
        "artifact_dir": layout.run_dir.as_posix(),
        "telemetry_dir": layout.telemetry_dir.as_posix(),
        "step_rows_path": layout.step_rows_path.as_posix(),
        "event_rows_path": layout.event_rows_path.as_posix(),
        "run_summary_path": layout.run_summary_path.as_posix(),
        "experiment_report_path": layout.experiment_report_path.as_posix(),
        "graph_checkpoint_index_path": layout.graph_checkpoint_index_path.as_posix(),
        "initial_snapshot_path": initial_snapshot_path.as_posix(),
        "final_snapshot_path": final_snapshot_path.as_posix(),
        "final_snapshot_digest": final_digest,
        "replay_final_snapshot_digest": replay_digest,
        "replay_step_rows_match": replay_step_rows_match,
        "replay_event_rows_match": replay_event_rows_match,
        "replay_digest_match": replay_digest_match,
        "checkpoint_count": len(primary_run["checkpoints"]),
        "checkpoint_overlays_enabled": include_checkpoint_overlays,
    }


def _run_rows_and_checkpoints(
    model: GRC9V3,
    *,
    identity: telemetry.RunTelemetryIdentity,
    lane_context: telemetry.GRC9V3LaneContext,
    steps: int,
    build_checkpoints: bool = True,
    include_checkpoint_overlays: bool = True,
) -> dict[str, Any]:
    step_results: list[StepResult] = []
    step_rows: list[telemetry.StepTelemetryRow] = []
    events: list[GRCEvent] = []
    checkpoints: list[telemetry.GraphCheckpointArtifact] = []
    if build_checkpoints:
        checkpoints.append(
            _export_basic_checkpoint(
                model,
                identity=identity,
                checkpoint_id="step-00000000",
                checkpoint_label="initial",
                checkpoint_reason="initial",
                events=(),
                include_overlays=include_checkpoint_overlays,
            )
        )

    for _ in range(steps):
        result = model.step()
        step_results.append(result)
        events.extend(result.events)
        step_rows.append(
            telemetry.step_row_from_step_result(
                result,
                identity=identity,
                family_extensions=telemetry.grc9v3_step_family_extensions(
                    _build_grc9v3_step_extension(model, lane_context=lane_context)
                ),
            )
        )
        if build_checkpoints:
            label = "final" if result.step_index == steps else "post_step"
            checkpoints.append(
                _export_basic_checkpoint(
                    model,
                    identity=identity,
                    checkpoint_id=f"step-{result.step_index:08d}",
                    checkpoint_label=label,
                    checkpoint_reason="representative_every_step",
                    events=result.events,
                    include_overlays=include_checkpoint_overlays,
                )
            )

    event_extensions = _build_grc9v3_event_extensions(
        model,
        events,
        lane_context=lane_context,
    )
    event_rows = telemetry.event_rows_from_events(
        events,
        identity=identity,
        family_extensions_by_event=tuple(
            telemetry.grc9v3_event_family_extensions(extension)
            for extension in event_extensions
        ),
    )
    return {
        "step_results": tuple(step_results),
        "step_rows": tuple(step_rows),
        "event_rows": tuple(event_rows),
        "checkpoints": tuple(checkpoints),
    }


def _export_basic_checkpoint(
    model: GRC9V3,
    *,
    identity: telemetry.RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    events: tuple[GRCEvent, ...],
    include_overlays: bool = True,
) -> telemetry.GraphCheckpointArtifact:
    state = model.get_state()
    event_counts = Counter(event.kind for event in events)
    return telemetry.GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=state.step_index,
        time=state.time,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        graph_kind="port_graph",
        node_count=len(tuple(state.topology.iter_live_node_ids())),
        edge_count=len(tuple(state.topology.iter_live_edge_ids())),
        node_records=_node_records(model),
        edge_records=_edge_records(model),
        event_step_range={
            "start_step_inclusive": state.step_index,
            "end_step_inclusive": state.step_index,
        },
        event_count_window=len(events),
        event_counts_by_kind_window=dict(sorted(event_counts.items())),
        flow_representation="signed_port_flux",
        flow_cadence="checkpoint_only",
        label_computation_modes=dict(state.edge_label_computation_mode),
        topology_extensions={
            "next_node_id": state.topology.next_node_id,
            "next_edge_id": state.topology.next_edge_id,
        },
        family_extensions=_checkpoint_family_extensions(
            model,
            include_overlays=include_overlays,
        ),
    )


def _checkpoint_family_extensions(
    model: GRC9V3,
    *,
    include_overlays: bool,
) -> dict[str, dict[str, Any]]:
    payload: dict[str, Any] = {
        "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
        "checkpoint_surface": "phase_t_grc9v3_iter6_overlays",
        "overlay_status": "enabled" if include_overlays else "disabled",
    }
    if include_overlays:
        payload.update(
            {
                "node_overlay": _checkpoint_node_overlay(model),
                "port_overlay": _checkpoint_port_overlay(model),
                "edge_overlay": _checkpoint_edge_overlay(model),
                "module_overlay": _checkpoint_module_overlay(model),
                "choice_overlay": _checkpoint_choice_overlay(model),
            }
        )
    return {"grc9v3": payload}


def _checkpoint_node_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    geometric_identity = state.cached_quantities.get("geometric_identity", {})
    seed_nodes: set[int] = set()
    if isinstance(geometric_identity, dict):
        seed_nodes = {int(node_id) for node_id in geometric_identity.get("seed_nodes", [])}
    module_node_ids = _module_node_ids(model)
    return {
        str(node_id): {
            "coherence": None if node is None else float(node.coherence),
            "gradient_norm": None
            if node is None
            else float(sum(value * value for value in node.gradient_row_basis) ** 0.5),
            "min_signed_hessian": None
            if node is None or not node.signed_hessian_row_basis
            else float(min(node.signed_hessian_row_basis)),
            "basin_mass": None if node is None else float(node.basin_mass),
            "basin_id": None if node is None else str(node.basin_id),
            "parent_id": None
            if node is None or node.parent_id is None
            else str(node.parent_id),
            "depth": None if node is None else int(node.depth),
            "is_sink": node_id in state.sink_set,
            "is_geometric_seed": node_id in seed_nodes,
            "is_module_node": node_id in module_node_ids,
        }
        for node_id, node in (
            (node_id, state.nodes.get(node_id))
            for node_id in sorted(state.topology.iter_live_node_ids())
        )
    }


def _checkpoint_port_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    row_totals = [0, 0, 0]
    column_totals = [0, 0, 0]
    by_node: dict[str, Any] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        occupied_ports: list[int] = []
        free_ports: list[int] = []
        for port_id in range(1, 10):
            if state.topology.port_is_occupied(node_id, port_id - 1):
                occupied_ports.append(port_id)
                row, column = port_to_rc(port_id)
                row_totals[row - 1] += 1
                column_totals[column - 1] += 1
            else:
                free_ports.append(port_id)
        by_node[str(node_id)] = {
            "occupied_ports": occupied_ports,
            "free_ports": free_ports,
            "active_degree": len(occupied_ports),
            "saturated": len(occupied_ports) == 9,
        }
    return {
        "by_node": by_node,
        "row_totals": tuple(row_totals),
        "column_totals": tuple(column_totals),
        "saturated_node_ids": tuple(
            int(node_id)
            for node_id, payload in by_node.items()
            if bool(payload["saturated"])
        ),
    }


def _checkpoint_edge_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        str(edge_id): {
            "base_conductance": float(
                state.base_conductance.get(edge_id, state.port_edges[edge_id].conductance)
            ),
            "flux_uv": float(state.port_edges[edge_id].flux_uv),
            "geometric_length": (
                None
                if edge_id not in state.geometric_length
                else float(state.geometric_length[edge_id])
            ),
            "temporal_delay": (
                None
                if edge_id not in state.temporal_delay
                else float(state.temporal_delay[edge_id])
            ),
            "flux_coupling": (
                None
                if edge_id not in state.flux_coupling
                else float(state.flux_coupling[edge_id])
            ),
        }
        for edge_id in sorted(state.topology.iter_live_edge_ids())
    }


def _checkpoint_module_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    stabilization = state.cached_quantities.get("last_child_basin_stabilization", {})
    if not isinstance(stabilization, dict):
        stabilization = {}
    return {
        "expansions": {
            str(expansion_id): {
                "parent_sink_id": int(record.parent_sink_id),
                "module_node_ids": tuple(int(node_id) for node_id in record.module_node_ids),
                "expansion_step": int(record.expansion_step),
                "distribution_weights": tuple(float(value) for value in record.distribution_weights),
            }
            for expansion_id, record in sorted(state.expansion_registry.items())
        },
        "latest": {
            "module_sink_ids": tuple(
                int(node_id) for node_id in stabilization.get("module_sink_nodes", [])
            ),
            "stabilized_child_node_ids": tuple(
                int(node_id)
                for node_id in stabilization.get("stabilized_child_node_ids", [])
            ),
            "stable_child_basin_count": int(
                stabilization.get("stable_child_basin_count", 0)
            ),
        },
    }


def _checkpoint_choice_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    learning_state = state.cached_quantities.get("choice_learning_state", {})
    if not isinstance(learning_state, dict):
        learning_state = {}
    return {
        "choice_regime_nodes": tuple(
            int(value["node_id"])
            for _, value in sorted(state.choice_registry.items())
            if isinstance(value, dict) and "node_id" in value
        ),
        "choice_registry": _plain_json_mapping(state.choice_registry),
        "collapse_registry": _plain_json_mapping(state.collapse_registry),
        "learned_basin_ids": {
            str(node_id): str(payload.get("learned_basin_id"))
            for node_id, payload in sorted(learning_state.items(), key=lambda item: str(item[0]))
            if isinstance(payload, dict) and "learned_basin_id" in payload
        },
    }


def _plain_json_mapping(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True))


def _module_node_ids(model: GRC9V3) -> set[int]:
    module_node_ids: set[int] = set()
    for record in model.get_state().expansion_registry.values():
        module_node_ids.update(int(node_id) for node_id in record.module_node_ids)
    return module_node_ids


def _node_records(model: GRC9V3) -> tuple[dict[str, Any], ...]:
    state = model.get_state()
    records: list[dict[str, Any]] = []
    for node_id in sorted(state.topology.iter_live_node_ids()):
        node = state.nodes.get(node_id)
        payload = state.topology.node_payload(node_id)
        records.append(
            {
                "node_id": node_id,
                "role": payload.get("role"),
                "coherence": None if node is None else float(node.coherence),
                "basin_mass": None if node is None else float(node.basin_mass),
                "basin_id": None if node is None else str(node.basin_id),
                "parent_id": None if node is None else None if node.parent_id is None else str(node.parent_id),
                "depth": None if node is None else int(node.depth),
                "is_sink": node_id in state.sink_set,
                "active_degree": len(tuple(state.topology.incident_edge_ids(node_id))),
            }
        )
    return tuple(records)


def _edge_records(model: GRC9V3) -> tuple[dict[str, Any], ...]:
    state = model.get_state()
    records: list[dict[str, Any]] = []
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        port_edge = state.port_edges[edge_id]
        payload = state.topology.edge_payload(edge_id)
        records.append(
            {
                "edge_id": edge_id,
                "source_node_id": endpoint_a[0],
                "source_port_id": endpoint_a[1] + 1,
                "target_node_id": endpoint_b[0],
                "target_port_id": endpoint_b[1] + 1,
                "conductance": float(port_edge.conductance),
                "base_conductance": float(state.base_conductance.get(edge_id, port_edge.conductance)),
                "signed_flux_source_to_target": float(port_edge.flux_uv),
                "geometric_length_available": edge_id in state.geometric_length,
                "temporal_delay_available": edge_id in state.temporal_delay,
                "flux_coupling_available": edge_id in state.flux_coupling,
                "role": payload.get("role") or payload.get("kind"),
            }
        )
    return tuple(records)


def _build_checkpoint_index(
    identity: telemetry.RunTelemetryIdentity,
    checkpoints: tuple[telemetry.GraphCheckpointArtifact, ...],
    *,
    steps: int,
) -> telemetry.GraphCheckpointIndex:
    return telemetry.GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+every_step",
        selection_params={
            "include_initial": True,
            "every_step": True,
            "requested_steps": steps,
            "surface": "phase_t_grc9v3_iter6_overlays",
        },
        checkpoints=tuple(
            telemetry.GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                checkpoint_reason=checkpoint.checkpoint_reason,
                path=f"{checkpoint.checkpoint_id}.json",
                event_step_range=checkpoint.event_step_range,
                event_count_window=checkpoint.event_count_window,
                event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
            )
            for checkpoint in checkpoints
        ),
        family_extensions={
            "grc9v3": {
                "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "checkpoint_surface": "phase_t_grc9v3_iter6_overlays",
            }
        },
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the representative telemetry-backed GRC9V3 lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_EXPERIMENT_PATH),
        help="Relative path written under the outputs root.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of deterministic GRC9V3 steps to run.",
    )
    parser.add_argument(
        "--disable-checkpoint-overlays",
        action="store_true",
        help="Write basic graph checkpoints without GRC9V3 overlay payloads.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    report = run_grc9v3_representative_telemetry(
        outputs_root=Path(args.outputs_root),
        experiment_path=Path(args.experiment_path),
        steps=args.steps,
        include_checkpoint_overlays=not args.disable_checkpoint_overlays,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    MotionWindowLoadResult,
    load_motion_window,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout, save_telemetry_artifact_pack
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
)


def _identity(family: str) -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="motion_seed",
        requested_steps=6,
    )


def _summary(identity: RunTelemetryIdentity, family: str) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=6,
        final_step_index=5,
        initial_time=0.0,
        final_time=0.5,
        total_event_count=1,
        event_counts_by_kind={"growth": 1},
        initial_observables={},
        final_observables={},
        resolved_params={"evolution": {"dt": 0.1}},
        raw_params={},
        parameter_overrides={},
        status="completed",
        family_extensions={family: {"contract_version": "test"}},
    )


def _steps(identity: RunTelemetryIdentity, family: str) -> tuple[StepTelemetryRow, ...]:
    return tuple(
        StepTelemetryRow(
            identity=identity,
            step_index=index,
            time=float(index) * 0.1,
            event_count=1 if index == 2 else 0,
            event_counts_by_kind={"growth": 1} if index == 2 else {},
            observables={},
            family_extensions={family: {"step_marker": index}},
        )
        for index in range(6)
    )


def _events(identity: RunTelemetryIdentity, family: str) -> tuple[EventTelemetryRow, ...]:
    return (
        EventTelemetryRow(
            identity=identity,
            step_index=2,
            event_index=0,
            event_kind="growth",
            source_family=family,
            payload={"parent_node_id": 1, "child_node_id": 3},
            family_extensions={family: {"event_marker": True}},
        ),
    )


def _checkpoint(
    identity: RunTelemetryIdentity,
    family: str,
    *,
    checkpoint_id: str,
    step_index: int,
    time: float,
    nodes: tuple[dict[str, object], ...],
    edges: tuple[dict[str, object], ...],
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=time,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="motion_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={family: {"checkpoint_marker": True}},
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="motion_test",
        selection_params={"explicit": True},
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                path=f"{checkpoint.checkpoint_id}.json",
            )
            for checkpoint in checkpoints
        ),
    )


def _write_pack(
    root: Path,
    family: str,
    *,
    checkpoint_steps: tuple[int, ...] = (0, 2, 5),
    checkpoints: bool = True,
) -> Path:
    identity = _identity(family)
    layout = build_telemetry_artifact_layout(identity.run_id, root_dir=root)
    graph_checkpoints: tuple[GraphCheckpointArtifact, ...] = ()
    if checkpoints:
        graph_checkpoints = tuple(
            _checkpoint_for_step(identity, family, step)
            for step in checkpoint_steps
        )
    save_telemetry_artifact_pack(
        layout,
        step_rows=_steps(identity, family),
        event_rows=_events(identity, family),
        run_summary=_summary(identity, family),
        graph_checkpoint_index=_checkpoint_index(identity, graph_checkpoints)
        if checkpoints
        else None,
        graph_checkpoints=graph_checkpoints,
    )
    return layout.run_dir


def _checkpoint_for_step(
    identity: RunTelemetryIdentity,
    family: str,
    step: int,
) -> GraphCheckpointArtifact:
    if step == 0:
        nodes = (
            {
                "node_id": 1,
                "coherence": 3.0,
                "basin_id": "basin_a",
                "is_sink": True,
                "payload": {
                    "coordinates": [0.0, 0.0],
                    "source_construct_id": "source_a",
                    "continuity_delta": -0.2,
                },
            },
            {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a", "payload": {}},
        )
        edges = (
            {
                "edge_id": 10,
                "source_node_id": 1,
                "target_node_id": 2,
                "conductance": 1.0,
                "signed_flux": 0.5,
                "payload": {"source_construct_id": "edge_a"},
            },
        )
    elif step == 2:
        nodes = (
            {
                "node_id": 1,
                "coherence": 2.0,
                "basin_id": "basin_a",
                "is_sink": False,
                "payload": {"coordinates": [0.5, 0.0], "continuity_delta": -0.1},
            },
            {
                "node_id": 2,
                "coherence": 2.5,
                "basin_id": "basin_a",
                "is_sink": True,
                "payload": {"coordinates": [1.0, 0.0]},
            },
            {"node_id": 3, "coherence": 0.5, "basin_id": "basin_a", "payload": {}},
        )
        edges = (
            {
                "edge_id": 10,
                "source_node_id": 1,
                "target_node_id": 2,
                "conductance": 1.0,
                "signed_flux": 0.75,
                "payload": {},
            },
            {
                "edge_id": 11,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": 0.5,
                "signed_flux": 0.25,
                "payload": {},
            },
        )
    else:
        nodes = (
            {"node_id": 2, "coherence": 3.0, "basin_id": "basin_a", "is_sink": True, "payload": {}},
            {"node_id": 3, "coherence": 1.0, "basin_id": "basin_a", "payload": {}},
        )
        edges = (
            {
                "edge_id": 11,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": 0.5,
                "signed_flux": 0.2,
                "payload": {},
            },
        )
    return _checkpoint(
        identity,
        family,
        checkpoint_id=f"checkpoint_{step:04d}",
        step_index=step,
        time=float(step) * 0.1,
        nodes=nodes,
        edges=edges,
    )


class MotionWindowLoaderTest(unittest.TestCase):
    def test_loader_builds_motion_window_from_checkpoint_series(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = _write_pack(Path(tmp), "grc9v3")
            result = load_motion_window(run_dir, allow_short_persistence_window=True)

        self.assertIsInstance(result, MotionWindowLoadResult)
        self.assertEqual("grc9v3", result.landscape_load_result.source_runtime_family)
        self.assertEqual((0, 5), (result.motion_window.start_step, result.motion_window.end_step))
        self.assertEqual(
            ("checkpoint_0000", "checkpoint_0002", "checkpoint_0005"),
            result.motion_window.checkpoint_ids,
        )
        self.assertEqual("irregular", result.motion_window.checkpoint_spacing.spacing_mode)
        self.assertEqual((2, 3), result.motion_window.checkpoint_spacing.step_deltas)
        self.assertEqual("unit_measure_assumed", result.quadrature_mode)
        self.assertTrue(result.availability.checkpoint_series_available)
        self.assertEqual("available", result.availability.local_motion_claim_status)
        self.assertFalse(result.availability.diagnostic_only)

        first = result.checkpoint_evidence[0]
        self.assertEqual((1,), first.representative_node_ids)
        self.assertTrue(first.centroid_candidate_available)
        self.assertTrue(first.graph_medoid_proxy_available)
        self.assertEqual((0.0, 0.0), first.nodes[1].coordinates)
        self.assertTrue(first.nodes[1].provenance_available)
        self.assertEqual(-0.2, first.nodes[1].continuity_delta)
        self.assertEqual(0.5, first.edges[10].signed_flux)
        self.assertTrue(first.edges[10].provenance_available)

    def test_loader_records_topology_births_and_removals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_motion_window(
                _write_pack(Path(tmp), "grc9v3"),
                allow_short_persistence_window=True,
            )

        self.assertEqual(2, len(result.topology_deltas))
        first_delta = result.topology_deltas[0]
        self.assertEqual((3,), first_delta.born_node_ids)
        self.assertEqual((11,), first_delta.born_edge_ids)
        second_delta = result.topology_deltas[1]
        self.assertEqual((1,), second_delta.removed_node_ids)
        self.assertEqual((10,), second_delta.removed_edge_ids)

    def test_loader_marks_two_checkpoint_windows_as_diagnostic_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_motion_window(
                _write_pack(Path(tmp), "grc9", checkpoint_steps=(0, 2)),
            )

        self.assertEqual(2, result.availability.checkpoint_count)
        self.assertTrue(result.availability.checkpoint_series_available)
        self.assertEqual("diagnostic_only", result.availability.local_motion_claim_status)
        self.assertTrue(result.availability.diagnostic_only)

    def test_loader_marks_missing_checkpoint_series_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_motion_window(_write_pack(Path(tmp), "grcv3", checkpoints=False))

        self.assertEqual(0, result.availability.checkpoint_count)
        self.assertFalse(result.availability.checkpoint_series_available)
        self.assertEqual("unavailable", result.availability.local_motion_claim_status)
        self.assertIn("checkpoint_series", result.availability.missing_surfaces)
        self.assertEqual((), result.checkpoint_evidence)

    def test_loader_exposes_checkpoint_weight_quadrature_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            identity = _identity("grc9v3")
            checkpoint = _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                time=0.0,
                nodes=(
                    {"node_id": 1, "coherence": 2.0, "quadrature_weight": 2.0},
                    {"node_id": 2, "coherence": 1.0},
                ),
                edges=(),
            )
            layout = build_telemetry_artifact_layout(identity.run_id, root_dir=Path(tmp))
            save_telemetry_artifact_pack(
                layout,
                step_rows=_steps(identity, "grc9v3"),
                event_rows=_events(identity, "grc9v3"),
                run_summary=_summary(identity, "grc9v3"),
                graph_checkpoint_index=_checkpoint_index(identity, (checkpoint,)),
                graph_checkpoints=(checkpoint,),
            )

            result = load_motion_window(layout.run_dir)

        self.assertEqual("checkpoint_weight", result.quadrature_mode)

    def test_loader_supports_explicit_window_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_motion_window(
                _write_pack(Path(tmp), "grc9v3"),
                window_policy="explicit",
                start_step=1,
                end_step=3,
                allow_short_persistence_window=True,
            )

        self.assertEqual((1, 3), (result.motion_window.start_step, result.motion_window.end_step))
        self.assertEqual(("checkpoint_0002",), result.motion_window.checkpoint_ids)
        self.assertEqual("unknown", result.motion_window.checkpoint_spacing.spacing_mode)
        self.assertEqual("single_checkpoint_unavailable_for_motion", result.availability.local_motion_claim_status)

    def test_loader_summary_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = _write_pack(Path(tmp), "grc9v3")
            first = load_motion_window(run_dir).to_summary_mapping()
            second = load_motion_window(run_dir).to_summary_mapping()

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
